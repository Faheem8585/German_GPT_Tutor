"""Routes each user message through the right agent — tutor, grammar, planner, or motivation."""

from __future__ import annotations

import json
from enum import Enum
from typing import Annotated, Any, TypedDict

import structlog
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from app.agents.grammar_agent import GrammarAgent
from app.agents.motivation_agent import MotivationAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.tutor_agent import TutorAgent
from app.core.security import detect_prompt_injection, sanitize_user_input
from app.memory.user_memory import UserMemoryService
from app.models.user import CEFRLevel, InterfaceLanguage
from app.services.llm_service import LLMMessage, LLMResponse, llm_service

logger = structlog.get_logger(__name__)


class AgentIntent(str, Enum):
    TUTOR = "tutor"
    GRAMMAR_CHECK = "grammar_check"
    PLAN = "plan"
    MOTIVATE = "motivate"
    GAME = "game"
    UNKNOWN = "unknown"


class TutorState(TypedDict):
    messages: Annotated[list[dict], add_messages]
    user_id: str
    cefr_level: str
    interface_language: str
    intent: str
    grammar_errors: list[dict]
    rag_context: str
    agent_response: str
    xp_earned: int
    metadata: dict[str, Any]


class TutorOrchestrator:

    def __init__(self) -> None:
        self.tutor = TutorAgent()
        self.grammar = GrammarAgent()
        self.planner = PlannerAgent()
        self.motivator = MotivationAgent()
        self.memory_service = UserMemoryService()
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        workflow = StateGraph(TutorState)

        # Register nodes
        workflow.add_node("safety_check", self._safety_check)
        workflow.add_node("rag_retrieval", self._rag_retrieval)
        workflow.add_node("intent_router", self._intent_router)
        workflow.add_node("tutor_agent", self._tutor_node)
        workflow.add_node("grammar_agent", self._grammar_node)
        workflow.add_node("planner_agent", self._planner_node)
        workflow.add_node("motivation_agent", self._motivation_node)
        workflow.add_node("response_synthesizer", self._synthesizer)
        workflow.add_node("memory_update", self._memory_update)

        # Entry
        workflow.set_entry_point("safety_check")

        # Edges
        workflow.add_edge("safety_check", "rag_retrieval")
        workflow.add_edge("rag_retrieval", "intent_router")
        workflow.add_conditional_edges(
            "intent_router",
            self._route_to_agent,
            {
                AgentIntent.TUTOR: "tutor_agent",
                AgentIntent.GRAMMAR_CHECK: "grammar_agent",
                AgentIntent.PLAN: "planner_agent",
                AgentIntent.MOTIVATE: "motivation_agent",
                AgentIntent.UNKNOWN: "tutor_agent",
                AgentIntent.GAME: "tutor_agent",
            },
        )
        workflow.add_edge("tutor_agent", "grammar_agent")
        workflow.add_edge("grammar_agent", "response_synthesizer")
        workflow.add_edge("planner_agent", "response_synthesizer")
        workflow.add_edge("motivation_agent", "response_synthesizer")
        workflow.add_edge("response_synthesizer", "memory_update")
        workflow.add_edge("memory_update", END)

        return workflow.compile()

    async def run(
        self,
        user_message: str,
        user_id: str,
        cefr_level: CEFRLevel = CEFRLevel.A1,
        interface_language: InterfaceLanguage = InterfaceLanguage.EN,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        initial_state: TutorState = {
            "messages": conversation_history or [],
            "user_id": user_id,
            "cefr_level": cefr_level.value,
            "interface_language": interface_language.value,
            "intent": AgentIntent.UNKNOWN.value,
            "grammar_errors": [],
            "rag_context": "",
            "agent_response": "",
            "xp_earned": 0,
            "metadata": {"user_message": user_message},
        }

        # Add the new user message
        initial_state["messages"].append({"role": "user", "content": user_message})

        final_state = await self._graph.ainvoke(initial_state)
        return {
            "response": final_state["agent_response"],
            "grammar_errors": final_state["grammar_errors"],
            "xp_earned": final_state["xp_earned"],
            "intent": final_state["intent"],
            "metadata": final_state["metadata"],
        }

    async def _safety_check(self, state: TutorState) -> TutorState:
        """Detect prompt injection and sanitize input."""
        user_message = state["metadata"].get("user_message", "")
        clean_message = sanitize_user_input(user_message)

        if detect_prompt_injection(clean_message):
            logger.warning("prompt_injection_detected", user_id=state["user_id"])
            state["agent_response"] = (
                "Ich verstehe das nicht ganz. Lass uns weiter Deutsch lernen! "
                "Was möchtest du heute üben? (I'm not sure I understand. Let's continue learning German! "
                "What would you like to practice today?)"
            )
        state["metadata"]["sanitized_message"] = clean_message
        return state

    async def _rag_retrieval(self, state: TutorState) -> TutorState:
        """Retrieve relevant context from the German knowledge base."""
        if not state["agent_response"]:  # Skip if already handled by safety
            try:
                from app.rag.pipeline import rag_pipeline

                query = state["metadata"].get("sanitized_message", "")
                context = await rag_pipeline.retrieve(
                    query=query,
                    cefr_level=state["cefr_level"],
                    top_k=3,
                )
                state["rag_context"] = context
            except Exception as e:
                logger.warning("rag_retrieval_failed", error=str(e))
                state["rag_context"] = ""
        return state

    async def _intent_router(self, state: TutorState) -> TutorState:
        """Classify user intent to route to the right agent."""
        if state["agent_response"]:
            return state

        message = state["metadata"].get("sanitized_message", "").lower()

        # Fast pattern-based routing
        grammar_triggers = ["correct", "grammar", "mistake", "check my", "is this correct", "grammatik"]
        plan_triggers = ["plan", "schedule", "roadmap", "what should i learn", "curriculum", "lernplan"]
        motivate_triggers = ["frustrated", "giving up", "too hard", "can't", "unmotiviert", "motivation"]

        if any(t in message for t in grammar_triggers):
            state["intent"] = AgentIntent.GRAMMAR_CHECK.value
        elif any(t in message for t in plan_triggers):
            state["intent"] = AgentIntent.PLAN.value
        elif any(t in message for t in motivate_triggers):
            state["intent"] = AgentIntent.MOTIVATE.value
        else:
            state["intent"] = AgentIntent.TUTOR.value

        return state

    def _route_to_agent(self, state: TutorState) -> str:
        if state["agent_response"]:
            return AgentIntent.UNKNOWN.value  # Will short-circuit in tutor node
        return state["intent"]

    async def _tutor_node(self, state: TutorState) -> TutorState:
        if state["agent_response"]:
            return state
        response = await self.tutor.respond(
            messages=state["messages"],
            cefr_level=CEFRLevel(state["cefr_level"]),
            interface_language=InterfaceLanguage(state["interface_language"]),
            rag_context=state["rag_context"],
        )
        state["agent_response"] = response.content
        state["metadata"]["llm_meta"] = {
            "model": response.model,
            "provider": response.provider,
            "tokens": response.total_tokens(),
            "cost_usd": response.cost_usd,
            "latency_ms": response.latency_ms,
        }
        state["xp_earned"] += 10
        return state

    async def _grammar_node(self, state: TutorState) -> TutorState:
        """Run grammar check on user input — appends corrections to response."""
        user_text = state["metadata"].get("sanitized_message", "")
        if len(user_text) < 5:
            return state

        errors = await self.grammar.analyze(
            text=user_text,
            cefr_level=CEFRLevel(state["cefr_level"]),
        )
        state["grammar_errors"] = errors
        if errors:
            state["xp_earned"] = max(0, state["xp_earned"] - 2)
        return state

    async def _planner_node(self, state: TutorState) -> TutorState:
        response = await self.planner.create_plan(
            user_id=state["user_id"],
            cefr_level=CEFRLevel(state["cefr_level"]),
            messages=state["messages"],
        )
        state["agent_response"] = response.content
        state["xp_earned"] += 5
        return state

    async def _motivation_node(self, state: TutorState) -> TutorState:
        response = await self.motivator.encourage(
            user_id=state["user_id"],
            messages=state["messages"],
        )
        state["agent_response"] = response.content
        state["xp_earned"] += 15
        return state

    async def _synthesizer(self, state: TutorState) -> TutorState:
        """Final response assembly — add grammar feedback if present."""
        if state["grammar_errors"] and state["intent"] != AgentIntent.GRAMMAR_CHECK.value:
            # Append grammar corrections as a helpful note
            error_count = len(state["grammar_errors"])
            note = f"\n\n---\n📝 **Grammar note**: I noticed {error_count} area{'s' if error_count > 1 else ''} to work on in your message. Keep practicing!"
            state["agent_response"] += note

        state["messages"].append({
            "role": "assistant",
            "content": state["agent_response"],
        })
        return state

    async def _memory_update(self, state: TutorState) -> TutorState:
        """Async memory persistence — runs after response is ready."""
        try:
            if state["grammar_errors"]:
                await self.memory_service.record_mistakes(
                    user_id=state["user_id"],
                    mistakes=state["grammar_errors"],
                )
        except Exception as e:
            logger.warning("memory_update_failed", error=str(e))
        return state


# Singleton
orchestrator = TutorOrchestrator()
