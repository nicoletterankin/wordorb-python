"""CLI entry point: ``python -m wordorb <word>``."""

from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import asdict
from typing import Any

from wordorb.client import WordOrb
from wordorb.errors import WordOrbError

# Ensure stdout can handle Unicode on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )


def _serialize(obj: Any) -> Any:
    """Convert dataclass dicts for JSON output."""
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)  # type: ignore[arg-type]
    return obj


def main(argv: list[str] | None = None) -> int:
    """Run the Word Orb CLI."""
    parser = argparse.ArgumentParser(
        prog="wordorb",
        description="Word Orb CLI — look up words from the terminal",
    )
    parser.add_argument("word", nargs="?", help="Word to look up")
    parser.add_argument(
        "--lang",
        default=None,
        help="ISO 639-1 language code (e.g. es, fr, zh)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Word Orb API key (optional; without one, 200 calls/day per IP)",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Show knowledge-graph connections instead of word data",
    )
    parser.add_argument(
        "--ethics",
        action="store_true",
        help="Show ethics analysis (tones and translations)",
    )
    parser.add_argument(
        "--lesson",
        type=int,
        default=None,
        metavar="DAY",
        help="Fetch lesson for calendar day (1-365)",
    )
    parser.add_argument(
        "--quiz",
        type=int,
        default=None,
        metavar="DAY",
        help="Fetch quiz for calendar day (1-365)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show platform statistics",
    )
    parser.add_argument(
        "--track",
        default="learn",
        help="Lesson/quiz track (learn, teach, grow, trivia). Default: learn",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON",
    )

    args = parser.parse_args(argv)

    orb = WordOrb(api_key=args.api_key)

    try:
        if args.stats:
            result = orb.stats()
            if args.json_output:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"Word Orb Platform v{result.version}")
                print(f"  Words:       {result.word_orb.words:,}")
                print(f"  Lessons:     {result.lesson_orb.base_lessons:,}")
                print(f"  Quizzes:     {result.quiz_orb.interactions:,}")
                print(f"  Graph links: {result.knowledge_graph.word_lesson_links:,}")
                print(f"  Active keys: {result.active_keys}")
                print(f"  Calls today: {result.calls_today}")
            return 0

        if args.lesson is not None:
            result = orb.lesson(args.lesson, track=args.track)
            if args.json_output:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"Day {result.day} — {result.title}")
                print(f"Track: {result.track} | Theme: {result.theme} | Archetype: {result.archetype}")
                print()
                for phase_name in ("hook", "story", "wonder", "action", "wisdom"):
                    text = getattr(result.phases, phase_name)
                    if text:
                        print(f"[{phase_name.upper()}]")
                        print(text)
                        print()
            return 0

        if args.quiz is not None:
            result = orb.quiz(args.quiz, track=args.track)
            if args.json_output:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"Day {result.day} — {result.count} questions")
                for i, q in enumerate(result.interactions[:5], 1):
                    print(f"\n  Q{i} [{q.type}] {q.prompt}")
                    if q.choices:
                        for c in q.choices:
                            print(f"      - {c}")
                    print(f"      Answer: {q.answer}")
                if result.count > 5:
                    print(f"\n  ... and {result.count - 5} more (use --json for all)")
            return 0

        if not args.word:
            parser.print_help()
            return 1

        if args.graph:
            result = orb.graph(args.word)
            if args.json_output:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"'{result.word}' appears in {result.appears_in} lessons")
                if result.related_words:
                    print(f"Related: {', '.join(result.related_words[:10])}")
                for le in result.lessons[:5]:
                    print(f"  Day {le.day} ({le.track}/{le.phase})")
            return 0

        if args.ethics:
            result = orb.ethics(args.word)
            if args.json_output:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"Ethics analysis: {result.word}")
                print(f"Definition: {result.definition}")
                if result.tones:
                    print("\nTones:")
                    for tone, text in result.tones.items():
                        print(f"  [{tone}] {text[:120]}...")
                if result.translations:
                    print(f"\nTranslations: {len(result.translations)} languages")
            return 0

        # Default: word enrichment
        result = orb.enrich(args.word, lang=args.lang)
        if args.json_output:
            print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
        else:
            print(f"{result.word}  {result.ipa}  ({result.pos})")
            print(f"  {result.definition}")
            if result.etymology:
                print(f"\n  Etymology: {result.etymology}")
            if result.tones:
                print("\n  Tones:")
                for tone, text in result.tones.items():
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"    [{tone}] {preview}")
            if result.translations:
                top = list(result.translations.items())[:8]
                trans_str = ", ".join(f"{k}: {v}" for k, v in top)
                remaining = len(result.translations) - 8
                if remaining > 0:
                    trans_str += f" (+{remaining} more)"
                print(f"\n  Translations: {trans_str}")

        return 0

    except WordOrbError as exc:
        print(f"Error: {exc.message}", file=sys.stderr)
        if exc.trace_id:
            print(f"Trace ID: {exc.trace_id}", file=sys.stderr)
        return 1
    finally:
        orb.close()


if __name__ == "__main__":
    sys.exit(main())
