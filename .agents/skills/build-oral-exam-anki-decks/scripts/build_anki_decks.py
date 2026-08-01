#!/usr/bin/env python3
"""Build combined and optional per-topic APKGs from Markdown flashcards."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import genanki
from markdown_anki_decks.cli import parse_markdown


def humanize(name: str) -> str:
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    return re.sub(r"[-_]+", " ", separated).strip().title()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_dir", type=Path, help="Course project directory")
    parser.add_argument(
        "--flashcards-dir",
        default="flashcards",
        help="Markdown/media directory relative to the course directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Combined APKG path; defaults to anki/<course-slug>.apkg",
    )
    parser.add_argument(
        "--deck-prefix",
        help="Anki parent deck prefix; defaults to the humanized course directory name",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Also write one APKG per Markdown topic",
    )
    return parser.parse_args()


def unique_media(paths: list[Path]) -> list[Path]:
    by_name: dict[str, Path] = {}
    ordered: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).resolve()
        key = path.name.casefold()
        previous = by_name.get(key)
        if previous is not None and previous != path:
            raise ValueError(
                f"Anki media basename collision: {previous} and {path} both use {path.name!r}"
            )
        if previous is None:
            by_name[key] = path
            ordered.append(path)
    return ordered


def main() -> None:
    args = parse_args()
    course_dir = args.course_dir.expanduser().resolve()
    input_dir = course_dir / args.flashcards_dir
    markdown_files = sorted(input_dir.glob("*.md"))
    if not markdown_files:
        raise SystemExit(f"No Markdown files found in {input_dir}")

    course_title = humanize(course_dir.name)
    deck_prefix = args.deck_prefix or course_title
    deck_prefix = deck_prefix.rstrip(":") + "::"
    output = args.output or course_dir / "anki" / f"{slugify(course_title)}.apkg"
    if not output.is_absolute():
        output = course_dir / output
    output.parent.mkdir(parents=True, exist_ok=True)

    decks = []
    all_media: list[Path] = []
    parsed_topics = []
    for markdown_file in markdown_files:
        parsed = parse_markdown(markdown_file, deck_prefix, False)
        if not parsed.deck.notes:
            raise ValueError(f"No cards parsed from {markdown_file}")
        topic_media = unique_media(
            list(parsed.referenced_img_files) + list(parsed.referenced_sound_files)
        )
        parsed_topics.append((markdown_file, parsed.deck, topic_media))
        decks.append(parsed.deck)
        all_media.extend(topic_media)

    media = unique_media(all_media)
    genanki.Package(decks, media_files=media).write_to_file(output)
    print(
        f"Created {output} with {len(decks)} subdecks, "
        f"{sum(len(deck.notes) for deck in decks)} notes, and {len(media)} media files"
    )

    if args.individual:
        for markdown_file, deck, topic_media in parsed_topics:
            topic_output = output.parent / f"{markdown_file.stem}.apkg"
            genanki.Package([deck], media_files=topic_media).write_to_file(topic_output)
            print(
                f"Created {topic_output} with {len(deck.notes)} notes "
                f"and {len(topic_media)} media files"
            )


if __name__ == "__main__":
    main()
