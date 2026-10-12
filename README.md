# wordorb

**Python SDK for the [Word Orb](https://wordorb.ai) language enrichment API.**

162,000+ words across 47 languages. Daily lessons, quizzes, knowledge graphs, and multilingual enrichment — all from one API.

[![PyPI version](https://img.shields.io/pypi/v/wordorb)](https://pypi.org/project/wordorb/)
[![Python](https://img.shields.io/pypi/pyversions/wordorb)](https://pypi.org/project/wordorb/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
pip install wordorb
```

## Quickstart

```python
from wordorb import WordOrb

orb = WordOrb()  # $0 tier: 500 requests a day, no API key needed

# Look up a word
word = orb.enrich("courage")
print(word.definition)   # "Courage is the ability to face fear..."
print(word.ipa)          # "/ˈkɜːrɪdʒ/"
print(word.etymology)    # "From Old French 'corage'..."
print(word.translations) # {"es": "coraje", "fr": "courage", "de": "Mut", ...}

# Age-appropriate tones
print(word.tones["child"])  # Simple explanation for kids
print(word.tones["adult"])  # Full philosophical definition

# Ethics analysis
ethics = orb.ethics("mankind")
print(ethics.tones)         # Child, teen, adult perspectives
print(ethics.translations)  # How it translates across cultures

# Daily lesson (day 1-365)
lesson = orb.lesson(74)
print(lesson.title)               # Lesson title
print(lesson.phases.hook)         # Opening hook
print(lesson.phases.wisdom)       # Closing wisdom

# Quiz / Assessment
quiz = orb.quiz(74)
for q in quiz.interactions[:3]:
    print(q.prompt, "→", q.answer)

# Knowledge graph
graph = orb.graph("courage")
print(f"Appears in {graph.appears_in} lessons")
print(graph.related_words)  # ["intention", "integrity", ...]

# Platform stats
stats = orb.stats()
print(f"{stats.word_orb.words:,} words")  # "162,253 words"
```

## Async Support

```python
import asyncio
from wordorb import AsyncWordOrb

async def main():
    async with AsyncWordOrb() as orb:
        word = await orb.enrich("serendipity")
        print(word.definition)

        # Parallel lookups
        import asyncio
        words = await asyncio.gather(
            orb.enrich("courage"),
            orb.enrich("wisdom"),
            orb.enrich("resilience"),
        )
        for w in words:
            print(f"{w.word}: {w.definition}")

asyncio.run(main())
```

## Authentication

```python
# $0 tier: 500 requests a day, no key needed
orb = WordOrb()

# With API key: higher limits
orb = WordOrb(api_key="wo_your_key_here")

# Get a key: POST https://wordorb.ai/api/signup
```

## CLI

```bash
# Look up a word
python -m wordorb courage

# Ethics analysis
python -m wordorb mankind --ethics

# Knowledge graph
python -m wordorb courage --graph

# Daily lesson
python -m wordorb --lesson 74

# Quiz
python -m wordorb --quiz 74

# Platform stats
python -m wordorb --stats

# JSON output
python -m wordorb courage --json
```

## Error Handling

```python
from wordorb import WordOrb, RateLimitError, AuthError, NotFoundError

orb = WordOrb()

try:
    word = orb.enrich("xyznotaword")
except NotFoundError:
    print("Word not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except AuthError:
    print("Invalid API key")
```

Rate-limit retries happen automatically with exponential backoff (up to 3 retries).

## Data Types

| Method | Returns | Description |
|--------|---------|-------------|
| `enrich(word)` | `WordEnrichment` | Definition, IPA, etymology, translations, tones |
| `ethics(word)` | `EthicsAnalysis` | Tones and translations for inclusive language |
| `lesson(day)` | `Lesson` | Five-phase daily lesson with theme and archetype |
| `quiz(day)` | `Quiz` | Assessment interactions for a calendar day |
| `graph(word)` | `GraphResult` | Lesson appearances and related words |
| `stats()` | `PlatformStats` | Platform-wide counts and trending words |

All return types are frozen dataclasses with full type annotations.

## Requirements

- Python 3.10+
- [httpx](https://www.python-httpx.org/) (installed automatically)

## Links

- **API Docs:** [wordorb.ai/docs](https://wordorb.ai/docs)
- **Playground:** [wordorb.ai/playground](https://wordorb.ai/playground)
- **Pricing:** [wordorb.ai/pricing](https://wordorb.ai/pricing)
- **Source:** [github.com/nicoletterankin/wordorb-python](https://github.com/nicoletterankin/wordorb-python)

## License

MIT — [Lesson of the Day PBC](https://lotdpbc.com)
