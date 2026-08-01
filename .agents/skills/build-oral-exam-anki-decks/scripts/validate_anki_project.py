#!/usr/bin/env python3
"""Validate oral-exam Markdown flashcards, media, prompt stability, and APKG output."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SOUND_RE = re.compile(r"\[sound:([^\]]+)\]")
SOURCE_RE = re.compile(r"(?im)^\s*_Source:\s*.+?_\s*$")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


@dataclass(frozen=True)
class Card:
    file: Path
    line: int
    question: str
    answer: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_dir", type=Path, help="Course project directory")
    parser.add_argument("--flashcards-dir", default="flashcards")
    parser.add_argument("--combined-apkg", type=Path)
    parser.add_argument("--expected-cards", type=int)
    parser.add_argument("--baseline-questions", type=Path)
    parser.add_argument("--write-baseline", type=Path)
    parser.add_argument("--allow-missing-source", action="store_true")
    parser.add_argument("--require-apkg", action="store_true")
    return parser.parse_args()


def normalize_question(question: str) -> str:
    plain = re.sub(r"[`*_]", "", question).casefold()
    return re.sub(r"\s+", " ", plain).strip()


def split_cards(path: Path, errors: list[str]) -> list[Card]:
    cards: list[Card] = []
    current_question: str | None = None
    current_line = 0
    answer_lines: list[str] = []
    fence_marker: str | None = None

    def finish() -> None:
        if current_question is not None:
            cards.append(Card(path, current_line, current_question, "\n".join(answer_lines).strip()))

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                fence_marker = None
        heading = HEADING_RE.match(line) if fence_marker is None else None
        if heading:
            finish()
            current_question = heading.group(1).strip()
            current_line = line_number
            answer_lines = []
        elif current_question is not None:
            answer_lines.append(line)

    finish()
    if fence_marker is not None:
        errors.append(f"{path}: unclosed fenced code block")
    return cards


def media_target(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    return value.split()[0].strip("\"'") if value else value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_source_features(paths: list[Path]) -> tuple[int, int]:
    code_blocks = 0
    tables = 0
    for path in paths:
        fence_marker: str | None = None
        previous_line = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            fence = FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)[0]
                if fence_marker is None:
                    fence_marker = marker
                    code_blocks += 1
                elif marker == fence_marker:
                    fence_marker = None
                previous_line = line
                continue
            if fence_marker is None and TABLE_SEPARATOR_RE.match(line) and "|" in previous_line:
                tables += 1
            previous_line = line
    return code_blocks, tables


def load_baseline(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [
            line.removeprefix("## ").strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("# ")
        ]
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list):
        raise ValueError("Question baseline must be a JSON list or object containing 'questions'")
    questions: list[str] = []
    for item in data:
        if isinstance(item, str):
            questions.append(item)
        elif isinstance(item, dict) and isinstance(item.get("question"), str):
            questions.append(item["question"])
        else:
            raise ValueError("Each baseline entry must be a question string or object")
    return questions


def find_apkg(course_dir: Path, requested: Path | None) -> Path | None:
    if requested is not None:
        return requested if requested.is_absolute() else course_dir / requested
    candidates = list((course_dir / "anki").glob("*.apkg"))
    return max(candidates, key=lambda item: item.stat().st_size) if candidates else None


def validate_apkg(
    apkg: Path,
    expected_notes: int,
    expected_decks: int,
    source_media: dict[str, Path],
    expected_code_blocks: int,
    expected_tables: int,
    errors: list[str],
    warnings: list[str],
) -> tuple[int, int, int, int]:
    if not apkg.is_file():
        errors.append(f"Combined APKG does not exist: {apkg}")
        return (0, 0, 0, 0)

    try:
        with zipfile.ZipFile(apkg) as archive:
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"{apkg}: corrupt ZIP member {bad_member}")
            names = set(archive.namelist())
            collection_name = next(
                (name for name in ("collection.anki2", "collection.anki21") if name in names),
                None,
            )
            if collection_name is None:
                errors.append(f"{apkg}: no Anki collection database")
                return (0, 0, 0, 0)
            if "media" not in names:
                errors.append(f"{apkg}: no media manifest")
                return (0, 0, 0, 0)

            manifest = json.loads(archive.read("media"))
            destinations = list(manifest.values())
            if len(destinations) != len({name.casefold() for name in destinations}):
                errors.append(f"{apkg}: media manifest contains duplicate destination names")
            for member, destination in manifest.items():
                if member not in names:
                    errors.append(f"{apkg}: manifest member {member!r} is missing")
                    continue
                source = source_media.get(destination.casefold())
                if source is None:
                    warnings.append(f"{apkg}: packaged media {destination!r} has no referenced source file")
                elif hashlib.sha256(archive.read(member)).hexdigest() != sha256(source):
                    errors.append(f"{apkg}: packaged media {destination!r} differs from {source}")

            with tempfile.TemporaryDirectory() as temporary:
                database = Path(temporary) / collection_name
                database.write_bytes(archive.read(collection_name))
                connection = sqlite3.connect(database)
                try:
                    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
                    if integrity != "ok":
                        errors.append(f"{apkg}: SQLite integrity check returned {integrity!r}")
                    note_count = connection.execute("SELECT count(*) FROM notes").fetchone()[0]
                    card_count = connection.execute("SELECT count(*) FROM cards").fetchone()[0]
                    decks = json.loads(connection.execute("SELECT decks FROM col").fetchone()[0])
                    models = json.loads(connection.execute("SELECT models FROM col").fetchone()[0])
                    deck_count = sum(
                        1 for deck in decks.values() if deck.get("name", "Default") != "Default"
                    )
                    fields = "\n".join(
                        row[0] for row in connection.execute("SELECT flds FROM notes").fetchall()
                    )
                finally:
                    connection.close()

            if note_count != expected_notes:
                errors.append(f"{apkg}: {note_count} notes, expected {expected_notes}")
            if card_count != expected_notes:
                errors.append(f"{apkg}: {card_count} cards, expected {expected_notes}")
            if deck_count != expected_decks:
                errors.append(f"{apkg}: {deck_count} non-default decks, expected {expected_decks}")

            rendered_code_blocks = len(re.findall(r"class=[\"']codehilite[\"']", fields))
            rendered_tables = len(re.findall(r"<table\b", fields, re.IGNORECASE))
            if rendered_code_blocks != expected_code_blocks:
                errors.append(
                    f"{apkg}: {rendered_code_blocks} rendered highlighted code blocks, "
                    f"expected {expected_code_blocks}"
                )
            if rendered_tables != expected_tables:
                errors.append(
                    f"{apkg}: {rendered_tables} rendered tables, expected {expected_tables}"
                )

            model_css = "\n".join(model.get("css", "") for model in models.values())
            if source_media and "img" not in model_css:
                errors.append(f"{apkg}: model CSS has no image styling")
            if expected_code_blocks and ("pre" not in model_css or "codehilite" not in model_css):
                errors.append(f"{apkg}: model CSS lacks code-block styling")
            if expected_tables and "table" not in model_css:
                errors.append(f"{apkg}: model CSS lacks table styling")
            if ".nightMode" not in model_css:
                warnings.append(f"{apkg}: model CSS has no explicit Anki night-mode rules")

            packaged = {name.casefold() for name in destinations}
            for reference in HTML_IMAGE_RE.findall(fields):
                name = Path(reference).name.casefold()
                if name not in packaged:
                    errors.append(f"{apkg}: rendered note references unpackaged image {reference!r}")
            return (note_count, card_count, deck_count, len(manifest))
    except (zipfile.BadZipFile, json.JSONDecodeError, sqlite3.DatabaseError) as exc:
        errors.append(f"{apkg}: cannot validate package: {exc}")
        return (0, 0, 0, 0)


def main() -> None:
    args = parse_args()
    course_dir = args.course_dir.expanduser().resolve()
    flashcards_dir = course_dir / args.flashcards_dir
    markdown_files = sorted(flashcards_dir.glob("*.md"))
    errors: list[str] = []
    warnings: list[str] = []
    if not markdown_files:
        raise SystemExit(f"No Markdown files found in {flashcards_dir}")

    cards: list[Card] = []
    source_code_blocks, source_tables = count_source_features(markdown_files)
    for markdown_file in markdown_files:
        parsed_cards = split_cards(markdown_file, errors)
        if not parsed_cards:
            errors.append(f"{markdown_file}: no level-two card headings")
        cards.extend(parsed_cards)

    by_normalized: dict[str, Card] = {}
    referenced_media: dict[str, Path] = {}
    image_references = 0
    sound_references = 0
    for card in cards:
        if not card.question:
            errors.append(f"{card.file}:{card.line}: empty question")
        normalized = normalize_question(card.question)
        previous = by_normalized.get(normalized)
        if previous:
            errors.append(
                f"Duplicate question: {previous.file}:{previous.line} and "
                f"{card.file}:{card.line}: {card.question!r}"
            )
        else:
            by_normalized[normalized] = card

        content_without_source = SOURCE_RE.sub("", card.answer).strip()
        if not content_without_source:
            errors.append(f"{card.file}:{card.line}: empty answer")
        if not args.allow_missing_source and not SOURCE_RE.search(card.answer):
            errors.append(f"{card.file}:{card.line}: missing _Source: ..._ line")

        raw_media = [(raw, "image") for raw in IMAGE_RE.findall(card.answer)]
        raw_media += [(raw, "sound") for raw in SOUND_RE.findall(card.answer)]
        for raw, kind in raw_media:
            target = media_target(raw)
            if kind == "image":
                image_references += 1
            else:
                sound_references += 1
            if re.match(r"^[a-z]+://", target, re.IGNORECASE):
                errors.append(f"{card.file}:{card.line}: external {kind} is not packaged: {target}")
                continue
            if not target or Path(target).name != target:
                errors.append(
                    f"{card.file}:{card.line}: {kind} must use a same-directory basename: {target!r}"
                )
                continue
            source = (card.file.parent / target).resolve()
            if not source.is_file():
                errors.append(f"{card.file}:{card.line}: missing {kind} file {source}")
                continue
            key = source.name.casefold()
            previous_source = referenced_media.get(key)
            if previous_source is not None and previous_source != source:
                errors.append(
                    f"Global media basename collision: {previous_source} and {source}"
                )
            else:
                referenced_media[key] = source

    if args.expected_cards is not None and len(cards) != args.expected_cards:
        errors.append(f"Markdown has {len(cards)} cards, expected {args.expected_cards}")

    parser_notes = 0
    try:
        from markdown_anki_decks.cli import parse_markdown

        for markdown_file in markdown_files:
            parsed = parse_markdown(markdown_file, "Validation::", False)
            parser_notes += len(parsed.deck.notes)
        if parser_notes != len(cards):
            errors.append(
                f"markdown-anki-decks parsed {parser_notes} notes but headings define {len(cards)} cards"
            )
    except ImportError:
        warnings.append("markdown-anki-decks is unavailable; renderer parsing was not checked")
    except Exception as exc:  # parser error should be reported without losing other findings
        errors.append(f"markdown-anki-decks parsing failed: {exc}")

    css_path = flashcards_dir / "anki.css"
    if css_path.is_file():
        css = css_path.read_text(encoding="utf-8")
        if referenced_media and "img" not in css:
            warnings.append(f"{css_path}: no image styling found")
        if source_code_blocks and ("pre" not in css or "codehilite" not in css):
            warnings.append(f"{css_path}: incomplete code-block styling")
        if source_tables and "table" not in css:
            warnings.append(f"{css_path}: no table styling found")
        if ".nightMode" not in css:
            warnings.append(f"{css_path}: no explicit Anki night-mode rules")
    else:
        warnings.append(f"No anki.css found in {flashcards_dir}")

    if args.baseline_questions:
        baseline_path = args.baseline_questions.expanduser()
        if not baseline_path.is_absolute():
            baseline_path = course_dir / baseline_path
        baseline = load_baseline(baseline_path)
        current_exact = {card.question for card in cards}
        missing = [question for question in baseline if question not in current_exact]
        if missing:
            preview = "; ".join(repr(question) for question in missing[:5])
            errors.append(
                f"{len(missing)} baseline question(s) were renamed or removed; first: {preview}"
            )

    apkg = find_apkg(course_dir, args.combined_apkg)
    apkg_counts = (0, 0, 0, 0)
    if apkg is None:
        message = f"No APKG found under {course_dir / 'anki'}"
        (errors if args.require_apkg else warnings).append(message)
    else:
        apkg_counts = validate_apkg(
            apkg,
            len(cards),
            len(markdown_files),
            referenced_media,
            source_code_blocks,
            source_tables,
            errors,
            warnings,
        )

    if args.write_baseline and not errors:
        baseline_path = args.write_baseline.expanduser()
        if not baseline_path.is_absolute():
            baseline_path = course_dir / baseline_path
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "questions": [
                {
                    "file": str(card.file.relative_to(course_dir)),
                    "question": card.question,
                }
                for card in cards
            ]
        }
        baseline_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote question baseline: {baseline_path}")

    print(
        f"Markdown: {len(markdown_files)} files, {len(cards)} cards, "
        f"{image_references} image references, {sound_references} sound references, "
        f"{len(referenced_media)} unique media files, {source_code_blocks} code blocks, "
        f"{source_tables} tables"
    )
    if apkg is not None:
        notes, package_cards, decks, media = apkg_counts
        print(
            f"APKG: {apkg} — {notes} notes, {package_cards} cards, "
            f"{decks} subdecks, {media} media files"
        )
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(f"Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s)")
    print(f"Validation passed with {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()
