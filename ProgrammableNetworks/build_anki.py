"""Build one importable Anki package containing every lecture subdeck."""

from pathlib import Path

import genanki
from markdown_anki_decks.cli import parse_markdown


ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "flashcards"
OUTPUT_FILE = ROOT / "anki" / "programmable-networks.apkg"
DECK_PREFIX = "Programmable Networks::"


def main() -> None:
    decks = []
    media_files = []

    for markdown_file in sorted(INPUT_DIR.glob("*.md")):
        parsed = parse_markdown(markdown_file, DECK_PREFIX, False)
        decks.append(parsed.deck)
        media_files.extend(parsed.referenced_img_files)
        media_files.extend(parsed.referenced_sound_files)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(decks, media_files=list(dict.fromkeys(media_files)))
    package.write_to_file(OUTPUT_FILE)
    print(f"Created {OUTPUT_FILE} with {len(decks)} subdecks")


if __name__ == "__main__":
    main()
