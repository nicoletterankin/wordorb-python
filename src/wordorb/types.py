"""Word Orb SDK data types — dataclasses for all API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Word Orb
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WordEnrichment:
    """Full enrichment payload for a single word.

    Returned by :meth:`WordOrb.enrich` and :meth:`AsyncWordOrb.enrich`.
    """

    word: str
    ipa: str
    pos: str
    definition: str
    etymology: str
    translations: dict[str, str] = field(default_factory=dict)
    tones: dict[str, str] = field(default_factory=dict)
    image_url: str | None = None
    audio_url: str | None = None
    source: str | None = None
    tier: str | None = None

    @staticmethod
    def from_api(data: dict[str, Any]) -> WordEnrichment:
        """Construct from raw API JSON."""
        return WordEnrichment(
            word=data.get("word", ""),
            ipa=data.get("ipa", ""),
            pos=data.get("pos", ""),
            definition=data.get("def", ""),
            etymology=data.get("etym", ""),
            translations=data.get("langs", {}),
            tones=data.get("tones", {}),
            image_url=data.get("image_url"),
            audio_url=data.get("audio_url"),
            source=data.get("_source"),
            tier=data.get("_tier"),
        )


@dataclass(frozen=True)
class EthicsAnalysis:
    """Ethics-relevant data for a word.

    Contains the word's tones (child / teen / adult perspectives) and any
    translation or sensitivity information useful for inclusive language work.
    """

    word: str
    definition: str
    tones: dict[str, str] = field(default_factory=dict)
    translations: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def from_api(data: dict[str, Any]) -> EthicsAnalysis:
        """Construct from raw word API JSON."""
        return EthicsAnalysis(
            word=data.get("word", ""),
            definition=data.get("def", ""),
            tones=data.get("tones", {}),
            translations=data.get("langs", {}),
        )


# ---------------------------------------------------------------------------
# Lesson Orb
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LessonPhases:
    """The five phases of a Word Orb lesson."""

    hook: str = ""
    story: str = ""
    wonder: str = ""
    action: str = ""
    wisdom: str = ""

    @staticmethod
    def from_api(data: dict[str, Any]) -> LessonPhases:
        """Construct from the ``phases`` sub-object."""
        return LessonPhases(
            hook=data.get("hook", ""),
            story=data.get("story", ""),
            wonder=data.get("wonder", ""),
            action=data.get("action", ""),
            wisdom=data.get("wisdom", ""),
        )


@dataclass(frozen=True)
class Lesson:
    """A single daily lesson.

    Returned by :meth:`WordOrb.lesson` and :meth:`AsyncWordOrb.lesson`.
    """

    day: int
    track: str
    title: str
    theme: str
    age_group: str
    language: str
    archetype: str
    phases: LessonPhases
    archetypes_available: list[str] = field(default_factory=list)
    languages_available: list[str] = field(default_factory=list)
    product: str | None = None
    tier: str | None = None

    @staticmethod
    def from_api(data: dict[str, Any]) -> Lesson:
        """Construct from raw API JSON."""
        phases_raw = data.get("phases", {})
        return Lesson(
            day=data.get("day", 0),
            track=data.get("track", ""),
            title=data.get("title", ""),
            theme=data.get("theme", ""),
            age_group=data.get("age_group", ""),
            language=data.get("language", ""),
            archetype=data.get("archetype", ""),
            phases=LessonPhases.from_api(phases_raw),
            archetypes_available=data.get("archetypes_available", []),
            languages_available=data.get("languages_available", []),
            product=data.get("_product"),
            tier=data.get("_tier"),
        )


# ---------------------------------------------------------------------------
# Quiz Orb
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuizInteraction:
    """A single quiz question/interaction."""

    type: str
    phase: str
    age_group: str
    language: str
    prompt: str
    choices: list[str] | None = None
    answer: str = ""
    explanation: str = ""

    @staticmethod
    def from_api(data: dict[str, Any]) -> QuizInteraction:
        """Construct from a single interaction dict."""
        return QuizInteraction(
            type=data.get("type", ""),
            phase=data.get("phase", ""),
            age_group=data.get("age_group", ""),
            language=data.get("language", ""),
            prompt=data.get("prompt", ""),
            choices=data.get("choices"),
            answer=data.get("answer", ""),
            explanation=data.get("explanation", ""),
        )


@dataclass(frozen=True)
class Quiz:
    """Assessment data for a calendar day.

    Returned by :meth:`WordOrb.quiz` and :meth:`AsyncWordOrb.quiz`.
    """

    day: int
    track: str
    count: int
    interactions: list[QuizInteraction] = field(default_factory=list)

    @staticmethod
    def from_api(data: dict[str, Any]) -> Quiz:
        """Construct from raw API JSON."""
        interactions = [
            QuizInteraction.from_api(i) for i in data.get("interactions", [])
        ]
        return Quiz(
            day=data.get("day", 0),
            track=data.get("track", ""),
            count=data.get("count", 0),
            interactions=interactions,
        )


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphLesson:
    """A lesson appearance in the knowledge graph."""

    day: int
    track: str
    phase: str
    context: str | None = None
    importance: int = 0
    lesson_url: str = ""

    @staticmethod
    def from_api(data: dict[str, Any]) -> GraphLesson:
        """Construct from a single lesson dict."""
        return GraphLesson(
            day=data.get("day", 0),
            track=data.get("track", ""),
            phase=data.get("phase", ""),
            context=data.get("context"),
            importance=data.get("importance", 0),
            lesson_url=data.get("lesson_url", ""),
        )


@dataclass(frozen=True)
class GraphResult:
    """Knowledge graph connections for a word.

    Returned by :meth:`WordOrb.graph` and :meth:`AsyncWordOrb.graph`.
    """

    word: str
    appears_in: int
    lessons: list[GraphLesson] = field(default_factory=list)
    related_words: list[str] = field(default_factory=list)
    word_url: str = ""
    product: str | None = None
    tier: str | None = None

    @staticmethod
    def from_api(data: dict[str, Any]) -> GraphResult:
        """Construct from raw API JSON."""
        lessons = [GraphLesson.from_api(le) for le in data.get("lessons", [])]
        return GraphResult(
            word=data.get("word", ""),
            appears_in=data.get("appears_in", 0),
            lessons=lessons,
            related_words=data.get("related_words", []),
            word_url=data.get("word_url", ""),
            product=data.get("_product"),
            tier=data.get("_tier"),
        )


# ---------------------------------------------------------------------------
# Platform Stats
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProductStats:
    """Stats for a single product within Word Orb."""

    words: int = 0
    kv_cached: int = 0
    feedback: int = 0
    base_lessons: int = 0
    archetype_variants: int = 0
    total_blocks: int = 0
    interactions: int = 0
    word_lesson_links: int = 0


@dataclass(frozen=True)
class TierInfo:
    """Pricing tier information."""

    daily_limit: int | str
    price: str


@dataclass(frozen=True)
class TopWord:
    """A trending word from today's lookups."""

    word: str
    lookups: int


@dataclass(frozen=True)
class PlatformStats:
    """Platform-wide statistics.

    Returned by :meth:`WordOrb.stats` and :meth:`AsyncWordOrb.stats`.
    """

    word_orb: ProductStats
    lesson_orb: ProductStats
    quiz_orb: ProductStats
    knowledge_graph: ProductStats
    active_keys: int = 0
    calls_today: int = 0
    top_words_today: list[TopWord] = field(default_factory=list)
    tiers: dict[str, TierInfo] = field(default_factory=dict)
    version: str = ""
    timestamp: str = ""

    @staticmethod
    def from_api(data: dict[str, Any]) -> PlatformStats:
        """Construct from raw API JSON."""
        products = data.get("products", {})

        def _product_stats(key: str) -> ProductStats:
            p = products.get(key, {})
            return ProductStats(
                words=p.get("words", 0),
                kv_cached=p.get("kv_cached", 0),
                feedback=p.get("feedback", 0),
                base_lessons=p.get("base_lessons", 0),
                archetype_variants=p.get("archetype_variants", 0),
                total_blocks=p.get("total_blocks", 0),
                interactions=p.get("interactions", 0),
                word_lesson_links=p.get("word_lesson_links", 0),
            )

        top_words = [
            TopWord(word=w.get("word", ""), lookups=w.get("lookups", 0))
            for w in data.get("top_words_today", [])
        ]

        tiers: dict[str, TierInfo] = {}
        for name, info in data.get("tiers", {}).items():
            tiers[name] = TierInfo(
                daily_limit=info.get("daily_limit", 0),
                price=info.get("price", ""),
            )

        return PlatformStats(
            word_orb=_product_stats("word_orb"),
            lesson_orb=_product_stats("lesson_orb"),
            quiz_orb=_product_stats("quiz_orb"),
            knowledge_graph=_product_stats("knowledge_graph"),
            active_keys=data.get("active_keys", 0),
            calls_today=data.get("calls_today", 0),
            top_words_today=top_words,
            tiers=tiers,
            version=data.get("version", ""),
            timestamp=data.get("ts", ""),
        )
