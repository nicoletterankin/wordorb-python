"""Tests for wordorb.client — sync and async clients against mock responses."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from wordorb.client import AsyncWordOrb, WordOrb
from wordorb.errors import AuthError, NotFoundError, RateLimitError, WordOrbError
from wordorb.types import (
    EthicsAnalysis,
    GraphResult,
    Lesson,
    PlatformStats,
    Quiz,
    WordEnrichment,
)

# ---------------------------------------------------------------------------
# Fixtures — mock transport that returns canned API responses
# ---------------------------------------------------------------------------

WORD_RESPONSE: dict[str, Any] = {
    "word": "courage",
    "ipa": "/k/",
    "pos": "noun",
    "def": "Bravery",
    "etym": "French",
    "langs": {"es": "coraje"},
    "tones": {"child": "Being brave"},
    "image_url": None,
    "audio_url": None,
    "_source": "d1",
    "_tier": "free",
}

LESSON_RESPONSE: dict[str, Any] = {
    "day": 1,
    "track": "learn",
    "title": "Test Lesson",
    "theme": "test",
    "age_group": "adult",
    "language": "en",
    "archetype": "explorer",
    "phases": {"hook": "H", "story": "S", "wonder": "W", "action": "A", "wisdom": "Wi"},
    "archetypes_available": ["explorer"],
    "languages_available": ["en"],
    "_product": "lesson_orb",
    "_tier": "free",
}

QUIZ_RESPONSE: dict[str, Any] = {
    "day": 1,
    "track": "learn",
    "count": 1,
    "interactions": [
        {
            "type": "open",
            "phase": "hook",
            "age_group": "adult",
            "language": "en",
            "prompt": "What?",
            "choices": None,
            "answer": "this",
            "explanation": "Because",
        }
    ],
}

GRAPH_RESPONSE: dict[str, Any] = {
    "word": "courage",
    "appears_in": 5,
    "lessons": [],
    "related_words": ["bravery"],
    "word_url": "/api/word/courage",
    "_product": "knowledge_graph",
    "_tier": "free",
}

STATS_RESPONSE: dict[str, Any] = {
    "products": {
        "word_orb": {"words": 100},
        "lesson_orb": {"base_lessons": 50},
        "quiz_orb": {"interactions": 25},
        "knowledge_graph": {"word_lesson_links": 10},
    },
    "active_keys": 5,
    "calls_today": 10,
    "top_words_today": [],
    "tiers": {},
    "version": "1.0.0",
    "ts": "2026-01-01T00:00:00Z",
}


class MockTransport(httpx.BaseTransport):
    """Return canned responses based on URL path."""

    def __init__(self, status: int = 200, body: Any = None) -> None:
        self._status = status
        self._body = body

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if self._status != 200:
            body = self._body or {"code": "error", "error": "test error", "trace_id": "t1"}
            return httpx.Response(
                self._status,
                json=body,
                request=request,
            )

        if "/api/word/" in path:
            return httpx.Response(200, json=WORD_RESPONSE, request=request)
        if "/api/lesson" in path:
            return httpx.Response(200, json=LESSON_RESPONSE, request=request)
        if "/api/quiz" in path:
            return httpx.Response(200, json=QUIZ_RESPONSE, request=request)
        if "/api/graph" in path:
            return httpx.Response(200, json=GRAPH_RESPONSE, request=request)
        if "/api/stats" in path:
            return httpx.Response(200, json=STATS_RESPONSE, request=request)

        return httpx.Response(404, json={"error": "not found"}, request=request)


class AsyncMockTransport(httpx.AsyncBaseTransport):
    """Async version of MockTransport."""

    def __init__(self, status: int = 200, body: Any = None) -> None:
        self._sync = MockTransport(status=status, body=body)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return self._sync.handle_request(request)


def _make_sync_client(status: int = 200, body: Any = None) -> WordOrb:
    client = WordOrb(api_key="test_key")
    client._client = httpx.Client(
        base_url="https://wordorb.ai",
        transport=MockTransport(status=status, body=body),
    )
    return client


def _make_async_client(status: int = 200, body: Any = None) -> AsyncWordOrb:
    client = AsyncWordOrb(api_key="test_key")
    client._client = httpx.AsyncClient(
        base_url="https://wordorb.ai",
        transport=AsyncMockTransport(status=status, body=body),
    )
    return client


# ---------------------------------------------------------------------------
# Sync client tests
# ---------------------------------------------------------------------------


class TestWordOrbSync:
    def test_enrich(self) -> None:
        orb = _make_sync_client()
        result = orb.enrich("courage")
        assert isinstance(result, WordEnrichment)
        assert result.word == "courage"
        orb.close()

    def test_ethics(self) -> None:
        orb = _make_sync_client()
        result = orb.ethics("courage")
        assert isinstance(result, EthicsAnalysis)
        assert result.word == "courage"
        orb.close()

    def test_lesson(self) -> None:
        orb = _make_sync_client()
        result = orb.lesson(1)
        assert isinstance(result, Lesson)
        assert result.day == 1
        orb.close()

    def test_quiz(self) -> None:
        orb = _make_sync_client()
        result = orb.quiz(1)
        assert isinstance(result, Quiz)
        assert result.count == 1
        orb.close()

    def test_graph(self) -> None:
        orb = _make_sync_client()
        result = orb.graph("courage")
        assert isinstance(result, GraphResult)
        assert result.word == "courage"
        orb.close()

    def test_stats(self) -> None:
        orb = _make_sync_client()
        result = orb.stats()
        assert isinstance(result, PlatformStats)
        assert result.word_orb.words == 100
        orb.close()

    def test_context_manager(self) -> None:
        with _make_sync_client() as orb:
            result = orb.enrich("courage")
            assert result.word == "courage"

    def test_auth_error(self) -> None:
        orb = _make_sync_client(status=401)
        with pytest.raises(AuthError):
            orb.enrich("test")
        orb.close()

    def test_not_found_error(self) -> None:
        orb = _make_sync_client(status=404)
        with pytest.raises(NotFoundError):
            orb.enrich("test")
        orb.close()

    def test_rate_limit_error(self) -> None:
        orb = _make_sync_client(status=429)
        orb._max_retries = 0  # no retries for test speed
        with pytest.raises(RateLimitError):
            orb.enrich("test")
        orb.close()

    def test_generic_error(self) -> None:
        orb = _make_sync_client(status=500)
        with pytest.raises(WordOrbError):
            orb.enrich("test")
        orb.close()


# ---------------------------------------------------------------------------
# Async client tests
# ---------------------------------------------------------------------------


class TestAsyncWordOrb:
    @pytest.mark.asyncio
    async def test_enrich(self) -> None:
        orb = _make_async_client()
        result = await orb.enrich("courage")
        assert isinstance(result, WordEnrichment)
        assert result.word == "courage"
        await orb.close()

    @pytest.mark.asyncio
    async def test_ethics(self) -> None:
        orb = _make_async_client()
        result = await orb.ethics("courage")
        assert isinstance(result, EthicsAnalysis)
        await orb.close()

    @pytest.mark.asyncio
    async def test_lesson(self) -> None:
        orb = _make_async_client()
        result = await orb.lesson(1)
        assert isinstance(result, Lesson)
        await orb.close()

    @pytest.mark.asyncio
    async def test_quiz(self) -> None:
        orb = _make_async_client()
        result = await orb.quiz(1)
        assert isinstance(result, Quiz)
        await orb.close()

    @pytest.mark.asyncio
    async def test_graph(self) -> None:
        orb = _make_async_client()
        result = await orb.graph("courage")
        assert isinstance(result, GraphResult)
        await orb.close()

    @pytest.mark.asyncio
    async def test_stats(self) -> None:
        orb = _make_async_client()
        result = await orb.stats()
        assert isinstance(result, PlatformStats)
        await orb.close()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        async with _make_async_client() as orb:
            result = await orb.enrich("courage")
            assert result.word == "courage"

    @pytest.mark.asyncio
    async def test_auth_error(self) -> None:
        orb = _make_async_client(status=401)
        with pytest.raises(AuthError):
            await orb.enrich("test")
        await orb.close()

    @pytest.mark.asyncio
    async def test_rate_limit_error(self) -> None:
        orb = _make_async_client(status=429)
        orb._max_retries = 0
        with pytest.raises(RateLimitError):
            await orb.enrich("test")
        await orb.close()
