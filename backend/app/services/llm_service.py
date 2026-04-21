"""Wraps Gemini/Anthropic/OpenAI behind a single interface with retry and token tracking."""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import LLMProvider, settings
from app.core.exceptions import LLMError

logger = structlog.get_logger(__name__)

# Cost per 1M tokens (input/output) in USD
_COST_TABLE: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (0.25, 1.25),
    "claude-opus-4-7": (15.0, 75.0),
    "gpt-4o": (5.0, 15.0),
    "gpt-4o-mini": (0.15, 0.6),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (3.5, 10.5),
    "gemini-2.0-flash": (0.10, 0.40),
}


@dataclass
class LLMMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMService:

    def __init__(self) -> None:
        self._anthropic = None
        self._openai = None
        self._gemini = None

    def _get_anthropic(self):
        if self._anthropic is None:
            from anthropic import AsyncAnthropic
            self._anthropic = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic

    def _get_openai(self):
        if self._openai is None:
            from openai import AsyncOpenAI
            self._openai = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai

    def _get_gemini(self):
        if self._gemini is None:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            self._gemini = genai
        return self._gemini

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        if model not in _COST_TABLE:
            return 0.0
        in_cost, out_cost = _COST_TABLE[model]
        return (input_tokens * in_cost + output_tokens * out_cost) / 1_000_000

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def complete(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None = None,
        model: str | None = None,
        provider: LLMProvider | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        prov = provider or settings.default_llm_provider
        mdl = model or settings.default_chat_model
        temp = temperature if temperature is not None else settings.llm_temperature
        max_tok = max_tokens or settings.llm_max_tokens
        t0 = time.monotonic()

        try:
            if prov == LLMProvider.GEMINI:
                return await self._gemini_complete(messages, system_prompt, mdl, temp, max_tok, t0)
            elif prov == LLMProvider.ANTHROPIC:
                return await self._anthropic_complete(messages, system_prompt, mdl, temp, max_tok, t0)
            elif prov == LLMProvider.OPENAI:
                return await self._openai_complete(messages, system_prompt, mdl, temp, max_tok, t0)
            else:
                # Fallback to Gemini if provider not implemented
                return await self._gemini_complete(messages, system_prompt, "gemma-3-12b-it", temp, max_tok, t0)
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(str(e), str(prov)) from e

    async def _gemini_complete(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_tokens: int,
        t0: float,
    ) -> LLMResponse:
        import asyncio
        import google.generativeai as genai

        genai.configure(api_key=settings.google_api_key)

        # Gemma models don't support system_instruction — prepend to first user msg
        _is_gemma = model.startswith("gemma")
        sys_instr = system_prompt or "You are a helpful German language tutor."

        gen_model = genai.GenerativeModel(
            model_name=model,
            **({"system_instruction": sys_instr} if not _is_gemma else {}),
        )

        # Convert messages to Gemini format
        history = []
        last_user_message = ""
        _sys_prepended = False
        for msg in messages:
            if msg.role == "system":
                continue  # handled above
            elif msg.role == "user":
                content = msg.content
                # For Gemma: prepend system prompt to the first user message
                if _is_gemma and not _sys_prepended:
                    content = f"[System: {sys_instr}]\n\n{content}"
                    _sys_prepended = True
                last_user_message = content
                if history and history[-1]["role"] == "user":
                    history[-1]["parts"][0] += "\n" + content
                else:
                    history.append({"role": "user", "parts": [content]})
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})

        # Last message should be user — start chat with history minus last
        chat_history = history[:-1] if history else []
        user_msg = history[-1]["parts"][0] if history else last_user_message

        chat = gen_model.start_chat(history=chat_history)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # Run in executor since google SDK is sync
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message(user_msg, generation_config=generation_config),
        )

        latency = (time.monotonic() - t0) * 1000
        content = response.text or ""

        in_tok = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
        out_tok = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0

        return LLMResponse(
            content=content,
            model=model,
            provider="gemini",
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency,
            cost_usd=self._estimate_cost(model, in_tok, out_tok),
        )

    async def _anthropic_complete(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_tokens: int,
        t0: float,
    ) -> LLMResponse:
        client = self._get_anthropic()
        anthropic_messages = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)
        latency = (time.monotonic() - t0) * 1000
        in_tok = response.usage.input_tokens
        out_tok = response.usage.output_tokens
        return LLMResponse(
            content=response.content[0].text,
            model=model,
            provider="anthropic",
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency,
            cost_usd=self._estimate_cost(model, in_tok, out_tok),
        )

    async def _openai_complete(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_tokens: int,
        t0: float,
    ) -> LLMResponse:
        client = self._get_openai()
        openai_messages: list[dict] = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        openai_messages.extend({"role": m.role, "content": m.content} for m in messages)

        response = await client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = (time.monotonic() - t0) * 1000
        usage = response.usage
        in_tok = usage.prompt_tokens if usage else 0
        out_tok = usage.completion_tokens if usage else 0
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model,
            provider="openai",
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency,
            cost_usd=self._estimate_cost(model, in_tok, out_tok),
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None = None,
        model: str | None = None,
        provider: LLMProvider | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        prov = provider or settings.default_llm_provider
        mdl = model or settings.default_chat_model
        temp = temperature if temperature is not None else settings.llm_temperature
        max_tok = max_tokens or settings.llm_max_tokens

        if prov == LLMProvider.GEMINI:
            async for chunk in self._gemini_stream(messages, system_prompt, mdl, temp, max_tok):
                yield chunk
        elif prov == LLMProvider.ANTHROPIC:
            async for chunk in self._anthropic_stream(messages, system_prompt, mdl, temp, max_tok):
                yield chunk
        elif prov == LLMProvider.OPENAI:
            async for chunk in self._openai_stream(messages, system_prompt, mdl, temp, max_tok):
                yield chunk
        else:
            # Fallback — non-streaming via complete()
            resp = await self.complete(messages, system_prompt, mdl, prov, temp, max_tok)
            yield resp.content

    async def _gemini_stream(
        self, messages, system_prompt, model, temperature, max_tokens
    ) -> AsyncGenerator[str, None]:
        import asyncio
        import google.generativeai as genai

        genai.configure(api_key=settings.google_api_key)
        _is_gemma = model.startswith("gemma")
        sys_instr = system_prompt or "You are a helpful German language tutor."

        gen_model = genai.GenerativeModel(
            model_name=model,
            **({"system_instruction": sys_instr} if not _is_gemma else {}),
        )

        history = []
        _sys_prepended = False
        for msg in messages[:-1]:
            if msg.role == "user":
                content = msg.content
                if _is_gemma and not _sys_prepended:
                    content = f"[System: {sys_instr}]\n\n{content}"
                    _sys_prepended = True
                history.append({"role": "user", "parts": [content]})
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})

        last_msg = messages[-1].content if messages else ""
        if _is_gemma and not _sys_prepended:
            last_msg = f"[System: {sys_instr}]\n\n{last_msg}"
        chat = gen_model.start_chat(history=history)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message(last_msg, generation_config=generation_config, stream=True),
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def _anthropic_stream(
        self, messages, system_prompt, model, temperature, max_tokens
    ) -> AsyncGenerator[str, None]:
        client = self._get_anthropic()
        anthropic_messages = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def _openai_stream(
        self, messages, system_prompt, model, temperature, max_tokens
    ) -> AsyncGenerator[str, None]:
        client = self._get_openai()
        openai_messages: list[dict] = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        openai_messages.extend({"role": m.role, "content": m.content} for m in messages)

        stream = await client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings — uses Gemini if no OpenAI key."""
        if settings.openai_api_key and settings.openai_api_key not in ("", "sk-..."):
            client = self._get_openai()
            response = await client.embeddings.create(
                model=settings.default_embedding_model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        else:
            # Gemini embeddings
            import asyncio
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)

            loop = asyncio.get_event_loop()
            results = []
            for text in texts:
                # Try newer model first, fall back to embedding-001
                for emb_model in ("models/text-embedding-004", "models/embedding-001"):
                    try:
                        result = await loop.run_in_executor(
                            None,
                            lambda t=text, m=emb_model: genai.embed_content(
                                model=m,
                                content=t,
                            ),
                        )
                        results.append(result["embedding"])
                        break
                    except Exception as e:
                        if emb_model == "models/embedding-001":
                            raise RuntimeError(f"All embedding models failed: {e}") from e
                        continue
            return results


# Singleton
llm_service = LLMService()
