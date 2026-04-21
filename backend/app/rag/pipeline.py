"""Hybrid retrieval pipeline — combines BM25 keyword search with Qdrant vector search."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, Filter, FieldCondition, MatchValue
from qdrant_client.models import PointStruct, VectorParams
from rank_bm25 import BM25Okapi

from app.config import settings
from app.services.llm_service import llm_service

logger = structlog.get_logger(__name__)


@dataclass
class RetrievedChunk:
    content: str
    source: str
    cefr_level: str
    topic: str
    score: float
    chunk_id: str


class RAGPipeline:

    def __init__(self) -> None:
        self._qdrant: AsyncQdrantClient | None = None
        self._bm25_corpus: list[str] = []
        self._bm25_metadata: list[dict] = []
        self._bm25: BM25Okapi | None = None
        self._initialized = False

    @property
    def qdrant(self) -> AsyncQdrantClient:
        if self._qdrant is None:
            self._qdrant = AsyncQdrantClient(url=settings.qdrant_url)
        return self._qdrant

    async def initialize(self) -> None:
        """Create Qdrant collection and seed knowledge base if empty."""
        if self._initialized:
            return

        try:
            collections = await self.qdrant.get_collections()
            existing = {c.name for c in collections.collections}

            if settings.qdrant_collection not in existing:
                await self.qdrant.create_collection(
                    collection_name=settings.qdrant_collection,
                    vectors_config=VectorParams(
                        size=settings.qdrant_vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("qdrant_collection_created", name=settings.qdrant_collection)
                await self._seed_knowledge_base()

            await self._load_bm25_corpus()
            self._initialized = True
            logger.info("rag_pipeline_initialized")
        except Exception as e:
            logger.error("rag_init_failed", error=str(e))

    async def _seed_knowledge_base(self) -> None:
        """Seed with core German grammar and vocabulary knowledge."""
        from app.rag.knowledge_base.german_grammar import GRAMMAR_CHUNKS
        from app.rag.knowledge_base.vocabulary import VOCABULARY_CHUNKS
        from app.rag.knowledge_base.exam_prep import EXAM_CHUNKS

        all_chunks = GRAMMAR_CHUNKS + VOCABULARY_CHUNKS + EXAM_CHUNKS
        await self.index_documents(all_chunks)
        logger.info("knowledge_base_seeded", chunks=len(all_chunks))

    async def index_documents(self, documents: list[dict]) -> None:
        """Index a list of documents into Qdrant."""
        if not documents:
            return

        texts = [doc["content"] for doc in documents]
        embeddings = await llm_service.embed(texts)

        points = []
        for doc, embedding in zip(documents, embeddings):
            chunk_id = hashlib.md5(doc["content"].encode()).hexdigest()
            points.append(
                PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload={
                        "content": doc["content"],
                        "source": doc.get("source", "unknown"),
                        "cefr_level": doc.get("cefr_level", "all"),
                        "topic": doc.get("topic", "general"),
                    },
                )
            )

        await self.qdrant.upsert(
            collection_name=settings.qdrant_collection,
            points=points,
        )
        self._initialized = False  # Force BM25 reload

    async def _load_bm25_corpus(self) -> None:
        """Load all documents from Qdrant into BM25 index."""
        try:
            results = await self.qdrant.scroll(
                collection_name=settings.qdrant_collection,
                limit=10000,
                with_payload=True,
                with_vectors=False,
            )
            self._bm25_corpus = [r.payload["content"] for r in results[0]]
            self._bm25_metadata = [r.payload for r in results[0]]
            tokenized = [doc.lower().split() for doc in self._bm25_corpus]
            self._bm25 = BM25Okapi(tokenized)
        except Exception as e:
            logger.warning("bm25_load_failed", error=str(e))
            self._bm25 = None

    async def retrieve(
        self,
        query: str,
        cefr_level: str | None = None,
        top_k: int = 3,
        rerank: bool = True,
    ) -> str:
        """Full hybrid retrieval pipeline."""
        if not self._initialized:
            return ""

        if not query.strip():
            return ""

        try:
            # 1. Query rewriting for better retrieval
            try:
                rewritten_query = await self._rewrite_query(query)
            except Exception:
                rewritten_query = query

            # 2. Vector search (optional — falls back to BM25-only if embeddings unavailable)
            try:
                vector_results = await self._vector_search(rewritten_query, cefr_level, top_k * 2)
            except Exception as e:
                logger.warning("rag_vector_search_failed", error=str(e))
                vector_results = []

            # 3. BM25 search
            bm25_results = self._bm25_search(rewritten_query, top_k * 2)

            # 4. Reciprocal Rank Fusion
            fused = self._rrf_merge(vector_results, bm25_results)[:top_k * 2]

            # 5. LLM reranking (skip if no results or only BM25)
            if rerank and fused and vector_results:
                try:
                    fused = await self._llm_rerank(query, fused, top_k)
                except Exception:
                    fused = fused[:top_k]
            else:
                fused = fused[:top_k]

            # 6. Format context
            return self._format_context(fused)

        except Exception as e:
            logger.warning("rag_retrieve_failed", error=str(e))
            return ""

    async def _rewrite_query(self, query: str) -> str:
        """Rewrite query to improve retrieval."""
        from app.services.llm_service import LLMMessage

        prompt = f"""Rewrite this German learning query to maximize retrieval from a German grammar/vocabulary database.
Query: "{query}"
Rewritten query (one line, include relevant German grammar terms):"""

        response = await llm_service.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.1,
            max_tokens=100,
        )
        return response.content.strip() or query

    async def _vector_search(
        self, query: str, cefr_level: str | None, top_k: int
    ) -> list[RetrievedChunk]:
        embeddings = await llm_service.embed([query])
        query_vector = embeddings[0]

        search_filter = None
        if cefr_level:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="cefr_level",
                        match=MatchValue(value=cefr_level),
                    )
                ]
            )

        results = await self.qdrant.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )

        return [
            RetrievedChunk(
                content=r.payload["content"],
                source=r.payload.get("source", ""),
                cefr_level=r.payload.get("cefr_level", "all"),
                topic=r.payload.get("topic", ""),
                score=r.score,
                chunk_id=str(r.id),
            )
            for r in results
        ]

    def _bm25_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if not self._bm25 or not self._bm25_corpus:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        return [
            RetrievedChunk(
                content=self._bm25_corpus[i],
                source=self._bm25_metadata[i].get("source", ""),
                cefr_level=self._bm25_metadata[i].get("cefr_level", "all"),
                topic=self._bm25_metadata[i].get("topic", ""),
                score=float(scores[i]),
                chunk_id=f"bm25_{i}",
            )
            for i in top_indices
            if scores[i] > 0
        ]

    def _rrf_merge(
        self,
        vector_results: list[RetrievedChunk],
        bm25_results: list[RetrievedChunk],
        k: int = 60,
    ) -> list[RetrievedChunk]:
        """Reciprocal Rank Fusion to combine vector and BM25 results."""
        scores: dict[str, float] = {}
        chunks: dict[str, RetrievedChunk] = {}

        for rank, chunk in enumerate(vector_results):
            key = chunk.content[:100]
            scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
            chunks[key] = chunk

        for rank, chunk in enumerate(bm25_results):
            key = chunk.content[:100]
            scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
            if key not in chunks:
                chunks[key] = chunk

        ranked_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [chunks[k] for k in ranked_keys]

    async def _llm_rerank(
        self, query: str, chunks: list[RetrievedChunk], top_k: int
    ) -> list[RetrievedChunk]:
        """Use LLM to select most relevant chunks."""
        from app.services.llm_service import LLMMessage

        chunk_text = "\n".join(
            f"[{i}] {c.content[:200]}" for i, c in enumerate(chunks)
        )
        prompt = f"""Given the query: "{query}"

Rate these knowledge base chunks by relevance (0-10). Return ONLY a comma-separated list of indices from most to least relevant.

Chunks:
{chunk_text}

Ordered indices (e.g., "2,0,4,1,3"):"""

        try:
            response = await llm_service.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=50,
            )
            indices = [int(i.strip()) for i in response.content.split(",") if i.strip().isdigit()]
            reranked = [chunks[i] for i in indices if i < len(chunks)]
            return reranked[:top_k]
        except Exception:
            return chunks[:top_k]

    def _format_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return ""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i}: {chunk.topic} | Level: {chunk.cefr_level}]\n{chunk.content}"
            )
        return "\n\n".join(parts)


# Singleton
rag_pipeline = RAGPipeline()
