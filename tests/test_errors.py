"""Tests for wordorb.errors — error class hierarchy."""

from __future__ import annotations

from wordorb.errors import AuthError, NotFoundError, RateLimitError, WordOrbError


def test_wordorb_error_basics() -> None:
    exc = WordOrbError("something broke", status_code=500, trace_id="abc123")
    assert str(exc) == "something broke"
    assert exc.message == "something broke"
    assert exc.status_code == 500
    assert exc.trace_id == "abc123"
    assert "abc123" in repr(exc)


def test_wordorb_error_is_exception() -> None:
    exc = WordOrbError("test")
    assert isinstance(exc, Exception)


def test_rate_limit_error() -> None:
    exc = RateLimitError(retry_after=30.0)
    assert isinstance(exc, WordOrbError)
    assert exc.status_code == 429
    assert exc.retry_after == 30.0
    assert exc.message == "Rate limit exceeded"


def test_auth_error() -> None:
    exc = AuthError("Invalid token", status_code=403)
    assert isinstance(exc, WordOrbError)
    assert exc.status_code == 403


def test_not_found_error() -> None:
    exc = NotFoundError("Word not found")
    assert isinstance(exc, WordOrbError)
    assert exc.status_code == 404
