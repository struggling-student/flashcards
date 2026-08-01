"""Render the curated lecture-slide visuals referenced by the flashcards."""

from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parent
LECTURES_DIR = ROOT / "lectures"
FLASHCARDS_DIR = ROOT / "flashcards"
IMAGE_WIDTH = 1500
JPEG_QUALITY = 84


# Slide numbers are one-based, matching the numbers used in the Markdown sources.
VISUAL_SLIDES = {
    "001-Course Introduction.pdf": [9],
    "002-basics.pdf": [3, 4, 7, 10, 13, 14, 15, 16, 18],
    "003-Netconf_YANG.pdf": [6, 10, 12, 14, 16, 18, 20, 25, 29, 33, 35, 54],
    "004-SDN and Openflow.pdf": [7, 12, 13, 14, 19, 23, 27, 33, 38, 40, 41],
    "005-NFV_ Use Cases.pdf": [6, 12, 13, 17, 21, 22, 23, 26, 28, 31],
    "006-Network Function Virtualization.pdf": [7, 10, 14, 18, 21, 24, 26, 32],
    "007-VNF Placement.pdf": [5, 7, 10, 11, 15, 16, 21],
    "008-Service Function Chaining.pdf": [6, 7, 11, 14, 17, 18, 22, 26, 31],
    "009-Segment Routing.pdf": [9, 14, 18, 19, 22, 24, 27, 30, 33, 36, 38, 44, 45, 49, 54, 57],
    "010-Programmable Data Plane.pdf": [7, 12, 18, 19, 21, 23, 25, 29],
    "011-P4 Ecosystem.pdf": [5, 7, 10, 12, 13, 18, 23, 27, 29],
}


def image_name(pdf_name: str, slide_number: int) -> str:
    lecture_number = pdf_name[:3]
    return f"pn-{lecture_number}-s{slide_number:02d}.jpg"


def render_slide(pdf_path: Path, slide_number: int, output_path: Path) -> None:
    with pymupdf.open(pdf_path) as document:
        if not 1 <= slide_number <= document.page_count:
            raise ValueError(
                f"Slide {slide_number} is outside {pdf_path.name}'s "
                f"1-{document.page_count} range"
            )
        page = document[slide_number - 1]
        zoom = IMAGE_WIDTH / page.rect.width
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        pixmap.save(output_path, jpg_quality=JPEG_QUALITY)


def main() -> None:
    FLASHCARDS_DIR.mkdir(parents=True, exist_ok=True)
    expected_files = set()

    for pdf_name, slide_numbers in VISUAL_SLIDES.items():
        pdf_path = LECTURES_DIR / pdf_name
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)

        for slide_number in slide_numbers:
            output_path = FLASHCARDS_DIR / image_name(pdf_name, slide_number)
            render_slide(pdf_path, slide_number, output_path)
            expected_files.add(output_path)

    for stale_file in FLASHCARDS_DIR.glob("pn-[0-9][0-9][0-9]-s[0-9][0-9].jpg"):
        if stale_file not in expected_files:
            stale_file.unlink()

    print(f"Rendered {len(expected_files)} curated slide visuals into {FLASHCARDS_DIR}")


if __name__ == "__main__":
    main()
