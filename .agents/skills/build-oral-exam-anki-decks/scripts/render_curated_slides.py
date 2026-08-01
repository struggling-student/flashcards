#!/usr/bin/env python3
"""Render selected one-based PDF slide numbers into same-folder JPEG media."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pymupdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_dir", type=Path, help="Course project directory")
    parser.add_argument("--manifest", required=True, type=Path, help="Rendering JSON file")
    parser.add_argument("--lectures-dir", default="lectures")
    parser.add_argument("--output-dir", default="flashcards")
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete matching generated JPEGs omitted from the manifest",
    )
    return parser.parse_args()


def safe_prefix(value: str) -> str:
    prefix = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not prefix:
        raise ValueError("Manifest prefix must contain at least one letter or digit")
    return prefix


def lecture_id(pdf_name: str, ordinal: int) -> str:
    match = re.match(r"(\d{1,4})", Path(pdf_name).name)
    return f"{int(match.group(1)):03d}" if match else f"{ordinal:03d}"


def render(pdf_path: Path, slide_number: int, output: Path, width: int, quality: int) -> None:
    with pymupdf.open(pdf_path) as document:
        if not 1 <= slide_number <= document.page_count:
            raise ValueError(
                f"Slide {slide_number} is outside {pdf_path.name}'s 1-{document.page_count} range"
            )
        page = document[slide_number - 1]
        zoom = width / page.rect.width
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        pixmap.save(output, jpg_quality=quality)


def main() -> None:
    args = parse_args()
    course_dir = args.course_dir.expanduser().resolve()
    manifest_path = args.manifest.expanduser()
    if not manifest_path.is_absolute():
        manifest_path = course_dir / manifest_path
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    prefix = safe_prefix(data.get("prefix", course_dir.name))
    width = int(data.get("image_width", 1500))
    quality = int(data.get("jpeg_quality", 84))
    slides = data.get("slides")
    if not isinstance(slides, dict) or not slides:
        raise ValueError("Manifest must contain a non-empty 'slides' object")
    if width < 400:
        raise ValueError("image_width must be at least 400 pixels")
    if not 1 <= quality <= 100:
        raise ValueError("jpeg_quality must be between 1 and 100")

    lectures_dir = course_dir / args.lectures_dir
    output_dir = course_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    used_ids: dict[str, str] = {}

    for ordinal, (pdf_name, raw_numbers) in enumerate(slides.items(), start=1):
        pdf_path = lectures_dir / pdf_name
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)
        identifier = lecture_id(pdf_name, ordinal)
        if identifier in used_ids and used_ids[identifier] != pdf_name:
            raise ValueError(
                f"Lecture identifier {identifier} is shared by {used_ids[identifier]!r} and {pdf_name!r}"
            )
        used_ids[identifier] = pdf_name
        if not isinstance(raw_numbers, list) or not raw_numbers:
            raise ValueError(f"{pdf_name!r} must map to a non-empty slide-number list")

        numbers = sorted({int(number) for number in raw_numbers})
        for slide_number in numbers:
            output = output_dir / f"{prefix}-{identifier}-s{slide_number:02d}.jpg"
            render(pdf_path, slide_number, output, width, quality)
            expected.add(output.resolve())

    removed = 0
    if args.prune:
        pattern = re.compile(rf"^{re.escape(prefix)}-\d{{3,4}}-s\d+\.jpg$", re.IGNORECASE)
        for candidate in output_dir.glob("*.jpg"):
            if pattern.match(candidate.name) and candidate.resolve() not in expected:
                candidate.unlink()
                removed += 1

    print(f"Rendered {len(expected)} curated visuals into {output_dir}; removed {removed} stale files")


if __name__ == "__main__":
    main()
