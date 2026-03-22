"""Tests for wordorb.types — dataclass construction from API payloads."""

from __future__ import annotations

from wordorb.types import (
    EthicsAnalysis,
    GraphResult,
    Lesson,
    PlatformStats,
    Quiz,
    WordEnrichment,
)


def test_word_enrichment_from_api() -> None:
    raw = {
        "word": "courage",
        "ipa": "/ˈkɜːrɪdʒ/",
        "pos": "noun",
        "def": "The ability to face fear.",
        "etym": "From Old French 'corage'",
        "langs": {"es": "coraje", "fr": "courage"},
        "tones": {"child": "Being brave.", "adult": "Confronting fear."},
        "image_url": "/media/images/words/courage.png",
        "audio_url": "/audio/pronunciation/en/courage.mp3",
        "_source": "d1",
        "_tier": "free",
    }
    w = WordEnrichment.from_api(raw)
    assert w.word == "courage"
    assert w.ipa == "/ˈkɜːrɪdʒ/"
    assert w.pos == "noun"
    assert w.definition == "The ability to face fear."
    assert w.etymology == "From Old French 'corage'"
    assert w.translations == {"es": "coraje", "fr": "courage"}
    assert w.tones["child"] == "Being brave."
    assert w.image_url == "/media/images/words/courage.png"
    assert w.source == "d1"
    assert w.tier == "free"


def test_word_enrichment_minimal() -> None:
    w = WordEnrichment.from_api({"word": "test"})
    assert w.word == "test"
    assert w.ipa == ""
    assert w.translations == {}
    assert w.image_url is None


def test_ethics_from_api() -> None:
    raw = {
        "word": "mankind",
        "def": "human beings collectively",
        "tones": {"child": "All people.", "teen": "Everyone."},
        "langs": {"es": "humanidad"},
    }
    e = EthicsAnalysis.from_api(raw)
    assert e.word == "mankind"
    assert e.definition == "human beings collectively"
    assert "child" in e.tones
    assert e.translations["es"] == "humanidad"


def test_lesson_from_api() -> None:
    raw = {
        "day": 81,
        "track": "learn",
        "title": "The Language of Soil",
        "theme": "ecology",
        "age_group": "adult",
        "language": "en",
        "archetype": "explorer",
        "phases": {
            "hook": "Beneath your feet...",
            "story": "Suzanne Simard...",
            "wonder": "The mycorrhizal network...",
            "action": "Today, go outside...",
            "wisdom": "The forest teaches...",
        },
        "archetypes_available": ["explorer", "scientist"],
        "languages_available": ["en", "es"],
        "_product": "lesson_orb",
        "_tier": "free",
    }
    le = Lesson.from_api(raw)
    assert le.day == 81
    assert le.title == "The Language of Soil"
    assert le.phases.hook.startswith("Beneath")
    assert le.phases.wisdom.startswith("The forest")
    assert "explorer" in le.archetypes_available
    assert le.product == "lesson_orb"


def test_quiz_from_api() -> None:
    raw = {
        "day": 81,
        "track": "learn",
        "count": 2,
        "interactions": [
            {
                "type": "open",
                "phase": "action",
                "age_group": "adult",
                "language": "en",
                "prompt": "What should you look for?",
                "choices": None,
                "answer": "mycelium",
                "explanation": "The lesson says...",
            },
            {
                "type": "multiple_choice",
                "phase": "story",
                "age_group": "adult",
                "language": "en",
                "prompt": "Who researched this?",
                "choices": ["Simard", "Darwin", "Newton"],
                "answer": "Simard",
                "explanation": "Suzanne Simard...",
            },
        ],
    }
    q = Quiz.from_api(raw)
    assert q.day == 81
    assert q.count == 2
    assert len(q.interactions) == 2
    assert q.interactions[0].type == "open"
    assert q.interactions[1].choices is not None
    assert "Simard" in q.interactions[1].choices


def test_graph_result_from_api() -> None:
    raw = {
        "word": "courage",
        "appears_in": 17,
        "lessons": [
            {
                "day": 30,
                "track": "teach",
                "phase": "story",
                "context": "some context",
                "importance": 2,
                "lesson_url": "/api/lesson?day=30&track=teach",
            }
        ],
        "related_words": ["intention", "integrity"],
        "word_url": "/api/word/courage",
        "_product": "knowledge_graph",
        "_tier": "free",
    }
    g = GraphResult.from_api(raw)
    assert g.word == "courage"
    assert g.appears_in == 17
    assert len(g.lessons) == 1
    assert g.lessons[0].day == 30
    assert g.related_words == ["intention", "integrity"]


def test_platform_stats_from_api() -> None:
    raw = {
        "products": {
            "word_orb": {"words": 162253, "kv_cached": 32, "feedback": 1},
            "lesson_orb": {
                "base_lessons": 278036,
                "archetype_variants": 164250,
                "total_blocks": 442286,
            },
            "quiz_orb": {"interactions": 64494},
            "knowledge_graph": {"word_lesson_links": 30526},
        },
        "active_keys": 27,
        "calls_today": 33,
        "top_words_today": [{"word": "courage", "lookups": 3}],
        "tiers": {
            "free": {"daily_limit": 500, "price": "free"},
            "starter": {"daily_limit": 5000, "price": "$29/mo"},
        },
        "version": "6.2.0",
        "ts": "2026-03-22T03:55:56.824Z",
    }
    s = PlatformStats.from_api(raw)
    assert s.word_orb.words == 162253
    assert s.lesson_orb.base_lessons == 278036
    assert s.quiz_orb.interactions == 64494
    assert s.knowledge_graph.word_lesson_links == 30526
    assert s.active_keys == 27
    assert len(s.top_words_today) == 1
    assert s.top_words_today[0].word == "courage"
    assert s.tiers["free"].daily_limit == 500
    assert s.version == "6.2.0"
