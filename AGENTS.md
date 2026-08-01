# Flashcards repository instructions

## Repository purpose

Maintain explanation-heavy Anki decks for university oral exams. Course directories contain original material, Markdown card sources, media, reproducible build helpers, and generated APKG packages.

## Reusable flashcard skill

- For any task that creates, reviews, enriches, rebuilds, or validates course decks, use the repository skill at `.agents/skills/build-oral-exam-anki-decks/SKILL.md`.
- Read the skill completely before acting, then read the reference files it marks as required or relevant.
- Agents that support the open Agent Skills standard should discover the skill automatically. Codex can invoke it as `$build-oral-exam-anki-decks`; Claude Code can invoke it as `/build-oral-exam-anki-decks` through `.claude/skills/`.
- Agents without automatic skill discovery must open the canonical `SKILL.md` directly and follow it as the task workflow.
- Treat `.agents/skills/build-oral-exam-anki-decks/` as the canonical repository copy. The `.claude/skills/build-oral-exam-anki-decks` entry is only a compatibility symlink; do not maintain a second copy there.

## Working rules

- Inspect every supplied lecture, slide deck, note, and existing card file before changing deck content.
- Group material by examinable argument and maintain source traceability. Do not generate one card mechanically per slide.
- Write answers that a prepared student could speak and defend: thesis, mechanism, rationale, example, and tradeoff or limitation when relevant.
- Use curated images, compact code, and tables only when they improve understanding or recall. Keep Anki media beside the Markdown files, reference basenames only, and make basenames globally unique.
- Preserve existing `##` question headings, deck prefixes, subdeck names, and media basenames when updating an imported deck. APKG import does not delete obsolete Anki notes.
- Preserve user changes and unrelated course directories. Never overwrite original lecture material.
- Keep generated APKGs outside the Markdown source directory.

## Reusable commands

Set the skill path from the repository root:

```bash
SKILL_DIR=.agents/skills/build-oral-exam-anki-decks
```

Build a combined package and individual topic packages:

```bash
.venv/bin/python "$SKILL_DIR/scripts/build_anki_decks.py" COURSE_DIR --individual
```

Validate Markdown and the compiled combined package:

```bash
.venv/bin/python "$SKILL_DIR/scripts/validate_anki_project.py" COURSE_DIR --require-apkg
```

Render curated PDF slides after creating the course's `visuals.json` manifest:

```bash
.venv/bin/python "$SKILL_DIR/scripts/render_curated_slides.py" \
  COURSE_DIR --manifest COURSE_DIR/visuals.json
```

Use the course's pinned requirements when they exist. For a new course, begin with the templates in the skill's `assets/` directory.

If the repository environment is absent, create it without committing it and install the course requirements:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r COURSE_DIR/requirements-anki.txt
```

## Completion criteria

- Reconcile the final deck against a complete source coverage pass.
- Run the repository validator after the final build and resolve all errors.
- Report card, subdeck, image, code-block, and table counts, the exact APKG paths, source caveats, and whether existing prompt identities were preserved.
