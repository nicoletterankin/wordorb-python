"""Word Orb SDK — synchronous and asynchronous HTTP clients."""

from __future__ import annotations

import time
from typing import Any

import httpx

from wordorb.errors import AuthError, NotFoundError, RateLimitError, WordOrbError
from wordorb.types import (
    EthicsAnalysis,
    GraphResult,
    Lesson,
    PlatformStats,
    Quiz,
    WordEnrichment,
)

__all__ = ["WordOrb", "AsyncWordOrb"]

_DEFAULT_BASE_URL = "https://wordorb.ai"
_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_INITIAL_BACKOFF = 1.0


def _build_headers(api_key: str | None) -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "wordorb-python/0.1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _raise_for_status(response: httpx.Response) -> None:
    """Inspect *response* and raise a typed SDK error when appropriate."""
    if response.is_success:
        return

    try:
        body: dict[str, Any] = response.json()
    except Exception:
        body = {}

    message = body.get("error", response.reason_phrase or "Unknown error")
    trace_id = body.get("trace_id")
    status = response.status_code

    if status == 429:
        retry_after_raw = response.headers.get("Retry-After")
        retry_after = float(retry_after_raw) if retry_after_raw else None
        raise RateLimitError(
            message, status_code=status, trace_id=trace_id, retry_after=retry_after
        )
    if status in (401, 403):
        raise AuthError(message, status_code=status, trace_id=trace_id)
    if status == 404:
        raise NotFoundError(message, status_code=status, trace_id=trace_id)

    raise WordOrbError(message, status_code=status, trace_id=trace_id)


# ---------------------------------------------------------------------------
# Synchronous client
# ---------------------------------------------------------------------------


class WordOrb:
    """Synchronous Word Orb API client.

    Args:
        api_key: Optional API key. Without one, most read endpoints allow 200 calls/day per IP; a key gives 10,000 calls/day.
        base_url: Override the API base URL (default ``https://wordorb.ai``).
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on rate-limit (429) responses.

    Example::

        from wordorb import WordOrb

        orb = WordOrb()                         # no key: 200 calls/day per IP
        word = orb.enrich("courage")
        print(word.definition, word.ipa)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    # -- internal helpers --------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        backoff = _INITIAL_BACKOFF
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._client.get(path, params=params)
                _raise_for_status(resp)
                return resp.json()
            except RateLimitError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    raise
                wait = exc.retry_after if exc.retry_after else backoff
                time.sleep(wait)
                backoff *= 2
        raise last_exc  # type: ignore[misc]  # pragma: no cover

    # -- public API --------------------------------------------------------

    def enrich(self, word: str, *, lang: str | None = None) -> WordEnrichment:
        """Look up a word and return its full enrichment data.

        Args:
            word: The word to look up (e.g. ``"courage"``).
            lang: Optional ISO 639-1 language code for multilingual data.

        Returns:
            A :class:`WordEnrichment` dataclass.
        """
        params: dict[str, Any] = {}
        if lang:
            params["lang"] = lang
        data = self._get(f"/api/word/{word}", params=params or None)
        return WordEnrichment.from_api(data)

    def ethics(self, word: str) -> EthicsAnalysis:
        """Return ethics-relevant analysis for a word.

        Includes age-appropriate tone definitions and translations that
        help evaluate inclusive language choices.

        Args:
            word: The word to analyse (e.g. ``"mankind"``).

        Returns:
            An :class:`EthicsAnalysis` dataclass.
        """
        data = self._get(f"/api/word/{word}")
        return EthicsAnalysis.from_api(data)

    def lesson(self, day: int, *, track: str = "learn") -> Lesson:
        """Retrieve a lesson by calendar day.

        Args:
            day: Calendar day (1--365).
            track: Lesson track (``"learn"``, ``"teach"``, ``"grow"``,
                   ``"trivia"``). Defaults to ``"learn"``.

        Returns:
            A :class:`Lesson` dataclass.
        """
        data = self._get("/api/lesson", params={"day": day, "track": track})
        return Lesson.from_api(data)

    def quiz(self, day: int, *, track: str = "learn") -> Quiz:
        """Retrieve a quiz/assessment by calendar day.

        Args:
            day: Calendar day (1--365).
            track: Lesson track. Defaults to ``"learn"``.

        Returns:
            A :class:`Quiz` dataclass.
        """
        data = self._get("/api/quiz", params={"day": day, "track": track})
        return Quiz.from_api(data)

    def graph(self, word: str) -> GraphResult:
        """Get knowledge-graph connections for a word.

        Args:
            word: The word to look up.

        Returns:
            A :class:`GraphResult` dataclass containing lessons and related words.
        """
        data = self._get("/api/graph/word", params={"word": word})
        return GraphResult.from_api(data)

    def stats(self) -> PlatformStats:
        """Retrieve platform-wide statistics.

        Returns:
            A :class:`PlatformStats` dataclass.
        """
        data = self._get("/api/stats")
        return PlatformStats.from_api(data)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> WordOrb:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Asynchronous client
# ---------------------------------------------------------------------------


class AsyncWordOrb:
    """Asynchronous Word Orb API client.

    Args:
        api_key: Optional API key. Without one, most read endpoints allow 200 calls/day per IP; a key gives 10,000 calls/day.
        base_url: Override the API base URL (default ``https://wordorb.ai``).
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on rate-limit (429) responses.

    Example::

        import asyncio
        from wordorb import AsyncWordOrb

        async def main():
            async with AsyncWordOrb() as orb:
                word = await orb.enrich("serendipity")
                print(word.definition)

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    # -- internal helpers --------------------------------------------------

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        import asyncio

        backoff = _INITIAL_BACKOFF
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = await self._client.get(path, params=params)
                _raise_for_status(resp)
                return resp.json()
            except RateLimitError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    raise
                wait = exc.retry_after if exc.retry_after else backoff
                await asyncio.sleep(wait)
                backoff *= 2
        raise last_exc  # type: ignore[misc]  # pragma: no cover

    # -- public API --------------------------------------------------------

    async def enrich(self, word: str, *, lang: str | None = None) -> WordEnrichment:
        """Look up a word and return its full enrichment data.

        Args:
            word: The word to look up.
            lang: Optional ISO 639-1 language code.

        Returns:
            A :class:`WordEnrichment` dataclass.
        """
        params: dict[str, Any] = {}
        if lang:
            params["lang"] = lang
        data = await self._get(f"/api/word/{word}", params=params or None)
        return WordEnrichment.from_api(data)

    async def ethics(self, word: str) -> EthicsAnalysis:
        """Return ethics-relevant analysis for a word.

        Args:
            word: The word to analyse.

        Returns:
            An :class:`EthicsAnalysis` dataclass.
        """
        data = await self._get(f"/api/word/{word}")
        return EthicsAnalysis.from_api(data)

    async def lesson(self, day: int, *, track: str = "learn") -> Lesson:
        """Retrieve a lesson by calendar day.

        Args:
            day: Calendar day (1--365).
            track: Lesson track. Defaults to ``"learn"``.

        Returns:
            A :class:`Lesson` dataclass.
        """
        data = await self._get("/api/lesson", params={"day": day, "track": track})
        return Lesson.from_api(data)

    async def quiz(self, day: int, *, track: str = "learn") -> Quiz:
        """Retrieve a quiz/assessment by calendar day.

        Args:
            day: Calendar day (1--365).
            track: Lesson track. Defaults to ``"learn"``.

        Returns:
            A :class:`Quiz` dataclass.
        """
        data = await self._get("/api/quiz", params={"day": day, "track": track})
        return Quiz.from_api(data)

    async def graph(self, word: str) -> GraphResult:
        """Get knowledge-graph connections for a word.

        Args:
            word: The word to look up.

        Returns:
            A :class:`GraphResult` dataclass.
        """
        data = await self._get("/api/graph/word", params={"word": word})
        return GraphResult.from_api(data)

    async def stats(self) -> PlatformStats:
        """Retrieve platform-wide statistics.

        Returns:
            A :class:`PlatformStats` dataclass.
        """
        data = await self._get("/api/stats")
        return PlatformStats.from_api(data)

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncWordOrb:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
