# Visuals, code, and tables

## Select visuals for learning value

Use an image when it makes an important relationship easier to reconstruct than prose alone. Strong candidates include:

- architecture and ownership boundaries;
- sequence, lifecycle, or control flow;
- topology and path changes;
- packet/header layout;
- state before and after an operation;
- algorithm iterations;
- side-by-side design comparisons.

Skip title slides, decorative photos, dense screenshots that cannot be read on a phone, and diagrams already reproduced more clearly in text or a table.

Prefer a curated set rather than rendering every slide. A useful visual must be legible and directly relevant to the card. Preserve slide numbers in deterministic filenames so later audits can locate the source.

## Explain how to read the image

Introduce the image with its purpose and follow it with interpretation. Name the direction of flow, important boundaries, color or line semantics, state transitions, and the conclusion the student should draw. Do not assert relationships the image does not actually establish.

If the original slide is cluttered, crop it only when context is not lost. Otherwise render the full slide at a width that remains zoomable. Use JPEG for ordinary slides and PNG where line art or small text noticeably suffers.

## Make artifacts examinable

Code should test interpretation, not copying. Keep only the lines needed for the concept and ask what each field, clause, or stage contributes. Good artifact cards include:

- XML/YANG/YAML/JSON structures;
- CLI or protocol exchanges;
- P4-like parser, table, and control blocks;
- placement or routing pseudocode;
- packet traces and header stacks;
- equations with a small numerical example.

Explain inputs, outputs, state changes, and failure behavior. If a sample is intentionally simplified or not directly executable, say so.

Validate structured snippets when feasible. Parse XML, JSON, and YAML; syntax-check Python or shell fragments; verify calculations separately. For unsupported languages, inspect delimiters, identifiers, and consistency manually.

## Use tables deliberately

Tables work best for exact repeated fields:

- alternatives compared on the same criteria;
- protocol operation to effect mappings;
- algorithm iteration to state mappings;
- header field to meaning mappings;
- responsibility matrices.

Do not put long essays in table cells. Follow the table with the causal takeaway, especially when the exam asks why one alternative is chosen.

## Curated rendering manifest

The included renderer accepts JSON of this form:

```json
{
  "prefix": "pn",
  "image_width": 1500,
  "jpeg_quality": 84,
  "slides": {
    "001-Course Introduction.pdf": [9],
    "002-Networking Basics.pdf": [3, 7, 18]
  }
}
```

Slide numbers are one-based. Leading lecture numbers produce names such as `pn-002-s07.jpg`. Use `--prune` only when the manifest is authoritative; it deletes previously generated files matching the same prefix that are no longer selected.

After rendering, inspect representative images at full resolution and verify every Markdown reference resolves to a same-folder file.
