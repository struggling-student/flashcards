---
name: build-oral-exam-anki-decks
description: Create, review, enrich, rebuild, and validate explanation-heavy oral-exam flashcard decks from course PDFs, slides, and notes using Markdown and markdown-anki-decks. Use when turning a course corpus into Anki decks, checking whether an existing deck covers all examinable arguments, adding curated images/code/tables, preserving existing Anki note identities during updates, or producing importable per-topic and combined APKG files.
---

# Build Oral-Exam Anki Decks

## Purpose

Build flashcards that train a student to explain, reason, compare, and work through examples in an oral exam. Treat Markdown, media, generated APKG files, and a coverage audit as parts of one deliverable.

Use one coordinator to own source interpretation, card wording, integration, and final validation. Use optional read-only audit roles only when the user authorizes agent delegation and the environment supports it; see [references/optional-audit-roles.md](references/optional-audit-roles.md).

Resolve `SKILL_DIR` as the absolute directory containing this `SKILL.md` before running bundled scripts or copying assets. Use the skill path supplied by the host's discovery metadata; in Claude Code, `${CLAUDE_SKILL_DIR}` resolves to the same directory. Never assume the current working directory is the skill directory.

## Read the relevant knowledge

Always read:

- [references/card-writing-rubric.md](references/card-writing-rubric.md)
- [references/source-coverage-and-review.md](references/source-coverage-and-review.md)
- [references/markdown-anki-format.md](references/markdown-anki-format.md)

Also read:

- [references/visuals-code-and-tables.md](references/visuals-code-and-tables.md) when the sources contain diagrams, algorithms, commands, data models, packet formats, or code.
- [references/update-safety.md](references/update-safety.md) before changing an existing deck or recompiling a deck the user has already imported.
- [references/optional-audit-roles.md](references/optional-audit-roles.md) before delegating a large corpus.

## Workflow

### 1. Inventory the entire corpus

Inspect every source before writing cards. Record files, topics, ordering, page or slide counts, and source type. Group the material into coherent exam units rather than assuming one file equals one conceptual unit.

Use the PDF or presentation skill when its trigger applies. Extract text for search and render pages or slides for visual inspection; do not rely on extraction alone because diagrams and spatial relationships may carry the argument.

If updating an existing project, inspect its Markdown, build scripts, requirements, generated packages, media naming, deck prefix, and question headings before editing anything. Capture a question baseline as described in `update-safety.md`.

### 2. Build a coverage map

For every source range, classify its examinable content as one of:

- covered by an existing card;
- needs a new card;
- should enrich an existing answer;
- administrative, duplicated, or non-examinable;
- unclear, contradictory, or apparently inaccurate and requiring a caveat.

Track definitions, mechanisms, motivations, assumptions, tradeoffs, comparisons, workflows, architectures, algorithms, worked examples, and artifacts the student may be asked to interpret. Do not equate slide count with card count.

### 3. Design the oral-exam questions

Write questions a professor could naturally ask aloud. Make each card test one coherent argument while allowing necessary subparts. Prefer prompts that demand explanation—“why,” “how,” “compare,” “trace,” “derive,” or “what changes if”—over prompts that only invite a label.

Answer as a well-prepared student: state the thesis, explain the mechanism, justify it, walk through an example, and close with limits or tradeoffs where relevant. Apply the rubric in `card-writing-rubric.md`.

Preserve existing question headings and deck names during updates unless the user explicitly accepts Anki duplicates or obsolete notes.

### 4. Add learning-oriented visuals and technical artifacts

Select images because they clarify structure, sequence, topology, state, or contrast—not merely because the source contains them. Crop or render legibly and explain what the learner should notice. Store referenced images in the same directory as the Markdown file and give every media file a globally unique basename.

Use compact fenced code blocks for syntax, commands, packet transformations, schemas, pseudocode, and configurations. Use tables for exact mappings and comparisons. Explain every non-obvious field, line, transition, or row in prose.

For curated PDF slides, create a JSON manifest and run:

```bash
python3 "$SKILL_DIR/scripts/render_curated_slides.py" COURSE_DIR \
  --manifest COURSE_DIR/visuals.json
```

### 5. Author stable Markdown

Use one Markdown file per lecture or topic and one level-two heading per card. Include a precise source line in every answer. Follow the canonical structure in `markdown-anki-format.md`.

Keep media beside the Markdown files. Keep build outputs outside the source directory. Pin the Python dependencies needed to reproduce the build.

For a new project, copy `$SKILL_DIR/assets/anki.css` and `$SKILL_DIR/assets/requirements-anki.txt` as starting templates, then adapt them to the course rather than recreating basic responsive styles.

### 6. Build both useful package forms

Compile individual topic packages when they help selective study, and always compile a combined package with topic subdecks for normal importing:

```bash
python3 "$SKILL_DIR/scripts/build_anki_decks.py" COURSE_DIR --individual
```

Run the command with the Python environment containing `markdown-anki-decks` and `genanki`. Pass `--deck-prefix` when preserving an existing hierarchy or when the inferred course title is unsuitable.

### 7. Validate the source and compiled deck

Run validation after every meaningful edit and again after the final build:

```bash
python3 "$SKILL_DIR/scripts/validate_anki_project.py" COURSE_DIR --require-apkg
```

For an existing imported deck, also pass `--baseline-questions PATH`. Validation must cover card counts, empty answers, missing source lines, normalized duplicate prompts, Markdown parsing, media paths and uniqueness, APKG ZIP integrity, SQLite integrity, note/card counts, deck count, packaged media hashes, and media references inside rendered notes.

Resolve every error. Investigate warnings rather than automatically suppressing them. Import a clean test profile when the change is high risk or the renderer changed materially.

### 8. Perform a second-pass oral examination

Review the complete deck from two perspectives:

1. As the professor, look for missing follow-ups, weak distinctions, untested examples, and places where a diagram or artifact could become an exam question.
2. As the student, attempt each answer without the source and check whether it is understandable, defensible, and complete enough to say aloud.

Reconcile this pass with the coverage map, rebuild, and rerun validation. Do not declare completion while Markdown and APKG outputs disagree.

## Deliverables

Return:

- structured Markdown source files and their CSS;
- uniquely named, same-directory media;
- reproducible build and rendering configuration;
- individual APKGs when requested or useful;
- one combined APKG containing subdecks;
- a concise coverage summary, card/media counts, validation result, and any source caveats.

Link the final APKG and source directory using absolute paths. State whether prompt identities were preserved during an update.

## Included scripts

- `scripts/render_curated_slides.py`: render only selected PDF pages from a JSON manifest into safe same-folder JPEG media.
- `scripts/build_anki_decks.py`: build a combined package and optional individual packages from Markdown files.
- `scripts/validate_anki_project.py`: validate Markdown, media, prompt stability, and a compiled APKG down to its SQLite collection and media manifest.
- `assets/anki.css`: responsive Anki styling for prose, images, code, tables, and dark mode.
- `assets/requirements-anki.txt`: pinned baseline build dependencies.

Treat these scripts as reusable defaults. Inspect an existing course's local scripts first and preserve compatible behavior when updating it.
