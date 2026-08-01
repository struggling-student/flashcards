# Safe updates and Anki identity

## Why prompt stability matters

With `markdown-anki-decks`/`genanki`, note identity is derived from stable deck/model inputs and the question field. Changing an existing question heading can therefore create a new note when the user imports the rebuilt APKG. The old note is not automatically deleted, so the user may see both the obsolete and replacement cards and may lose the old card's scheduling history.

Importing a new APKG is an update mechanism, not a synchronization or deletion mechanism.

## Before editing an imported deck

Capture all current level-two question headings and retain their exact text. The validator can create a machine-readable baseline:

```bash
python3 "$SKILL_DIR/scripts/validate_anki_project.py" COURSE_DIR \
  --write-baseline COURSE_DIR/question-baseline.json
```

Also preserve:

- the deck prefix and subdeck names;
- Markdown filenames when they influence deck names;
- the note model and field ordering;
- stable media basenames;
- the build tool and relevant dependency versions.

Commit or otherwise snapshot the source before a large review pass when version control is available.

## Editing policy

Safely improve an existing card by editing its answer body while leaving the `##` heading unchanged. Add a new card with a new heading. Move an existing heading between files only after confirming that the resulting deck identity stays the same.

Rename or replace an old heading only when one of these is true:

- the deck has not yet been imported;
- the user explicitly accepts a new note and will delete or suspend the old one;
- a controlled migration preserves the note GUID and scheduling data.

If a prompt is imperfect but understandable, keep it stable and clarify the scope in the answer. Do not silently “polish” hundreds of headings during an enrichment pass.

## Validate stability

After editing, run:

```bash
python3 "$SKILL_DIR/scripts/validate_anki_project.py" COURSE_DIR \
  --baseline-questions COURSE_DIR/question-baseline.json \
  --require-apkg
```

Missing baseline prompts are errors. New prompts are expected when cards were added. Exact retention is more important than retaining only a normalized equivalent.

Compare Markdown card count, parser note count, APKG note count, and APKG card count. Confirm packaged media hashes match the source files. For high-risk migrations, import into a clean Anki profile before touching the student's working collection.

## Communicate the result

Tell the user whether existing prompt identities were preserved, how many cards were added, and whether importing the APKG will leave any intentionally replaced cards behind. Never imply that importing removes cards absent from the new package.
