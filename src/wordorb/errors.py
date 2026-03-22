"""Word Orb SDK error classes."""

from __future__ import annotations


class WordOrbError(Exception):
    """Base exception for all Word Orb SDK errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code from the API, if applicable.
        trace_id: Server-side trace ID for debugging, if returned.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.trace_id = trace_id

    def __repr__(self) -> str:
        parts = [f"WordOrbError({self.message!r}"]
        if self.status_code is not None:
            parts.append(f", status_code={self.status_code}")
        if self.trace_id is not None:
            parts.append(f", trace_id={self.trace_id!r}")
        parts.append(")")
        return "".join(parts)


class RateLimitError(WordOrbError):
    """Raised when the API rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying, if provided by the server.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        status_code: int = 429,
        trace_id: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, trace_id=trace_id)
        self.retry_after = retry_after


class AuthError(WordOrbError):
    """Raised on authentication or authorization failures (HTTP 401/403)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        *,
        status_code: int = 401,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, trace_id=trace_id)


class NotFoundError(WordOrbError):
    """Raised when a requested resource is not found (HTTP 404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        status_code: int = 404,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, trace_id=trace_id)
