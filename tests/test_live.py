"""Live integration tests against the real Word Orb API.

Run with: pytest tests/test_live.py -v --live
These are skipped by default to avoid consuming API quota.
"""

from __future__ import annotations

import os

import pytest

from wordorb import AsyncWordOrb, WordOrb

# Skip unless --live flag or WORDORB_LIVE_TESTS env var
pytestmark = pytest.mark.skipif(
    not os.environ.get("WORDORB_LIVE_TESTS"),
    reason="Set WORDORB_LIVE_TESTS=1 to run live API tests",
)


API_KEY = os.environ.get("WORDORB_API_KEY", "")


class TestLiveSync:
    def test_enrich(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            word = orb.enrich("courage")
            assert word.word == "courage"
            assert word.ipa
            assert word.definition
            assert len(word.translations) > 0

    def test_ethics(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            ethics = orb.ethics("mankind")
            assert ethics.word == "mankind"
            assert ethics.definition

    def test_lesson(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            lesson = orb.lesson(81)
            assert lesson.day == 81
            assert lesson.title
            assert lesson.phases.hook

    def test_quiz(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            quiz = orb.quiz(81)
            assert quiz.day == 81
            assert quiz.count > 0

    def test_graph(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            graph = orb.graph("courage")
            assert graph.word == "courage"
            assert graph.appears_in > 0

    def test_stats(self) -> None:
        with WordOrb(api_key=API_KEY or None) as orb:
            stats = orb.stats()
            assert stats.word_orb.words > 100000
            assert stats.version


class TestLiveAsync:
    @pytest.mark.asyncio
    async def test_enrich(self) -> None:
        async with AsyncWordOrb(api_key=API_KEY or None) as orb:
            word = await orb.enrich("serendipity")
            assert word.word == "serendipity"
            assert word.definition
