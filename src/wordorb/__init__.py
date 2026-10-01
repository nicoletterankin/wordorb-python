"""Word Orb — Python SDK for the Word Orb language enrichment API.

Quickstart::

    from wordorb import WordOrb

    orb = WordOrb()                     # no key: 200 calls/day per IP
    word = orb.enrich("courage")
    print(word.definition, word.ipa)

Async::

    from wordorb import AsyncWordOrb

    async with AsyncWordOrb() as orb:
        word = await orb.enrich("serendipity")
"""

from wordorb.client import AsyncWordOrb, WordOrb
from wordorb.errors import AuthError, NotFoundError, RateLimitError, WordOrbError
from wordorb.types import (
    EthicsAnalysis,
    GraphLesson,
    GraphResult,
    Lesson,
    LessonPhases,
    PlatformStats,
    ProductStats,
    Quiz,
    QuizInteraction,
    TierInfo,
    TopWord,
    WordEnrichment,
)

__all__ = [
    # Clients
    "WordOrb",
    "AsyncWordOrb",
    # Types
    "WordEnrichment",
    "EthicsAnalysis",
    "Lesson",
    "LessonPhases",
    "Quiz",
    "QuizInteraction",
    "GraphResult",
    "GraphLesson",
    "PlatformStats",
    "ProductStats",
    "TierInfo",
    "TopWord",
    # Errors
    "WordOrbError",
    "RateLimitError",
    "AuthError",
    "NotFoundError",
]

__version__ = "0.1.0"
