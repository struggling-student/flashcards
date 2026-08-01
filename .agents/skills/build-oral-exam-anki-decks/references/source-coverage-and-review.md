# Source coverage and review

## Inventory before authoring

List every source file and capture its order, title, source type, and page or slide count. Read the complete corpus before choosing the deck structure. Course concepts often start in one lecture, gain an implementation in another, and receive limitations later.

For PDFs and slides, combine text extraction with visual rendering. Extraction finds terms and repeated claims; rendered pages reveal arrows, nesting, annotations, packet layouts, and staged examples that extraction loses. For notes, inspect headings, code, footnotes, and linked materials.

Group sources by conceptual material. A sensible grouping might follow modules, protocols, design layers, or problem families rather than filenames alone.

## Maintain a coverage map

Use a Markdown table or structured notes with these fields:

| Source range | Argument or skill | Status | Card | Action or caveat |
|---|---|---|---|---|
| Lecture 3, slides 12–16 | Configuration datastore workflow | covered | “How does…” | Enrich with edit/commit trace |

Use these statuses consistently:

- `new`: an examinable argument has no card;
- `covered`: an existing card tests it adequately;
- `enrich`: the card exists but misses reasoning, an example, or a limitation;
- `merge`: duplicated source material belongs in another card;
- `administrative`: agenda, title, bibliography, or non-examinable logistics;
- `caveat`: unclear, inconsistent, or apparently incorrect source material.

The map is an audit aid, not a quota. One card may cover several slides that form one argument, and one dense diagram may warrant several distinct questions.

## Coverage dimensions

Check each topic for more than definitions:

- motivation and problem statement;
- assumptions and system model;
- components, roles, and interfaces;
- sequence or lifecycle;
- state and information flow;
- algorithms, formulas, and complexity;
- worked examples and boundary cases;
- comparisons and design tradeoffs;
- operational commands, formats, and artifacts;
- failure modes, security implications, and limitations;
- cross-topic relationships.

If the instructor repeatedly develops an example across slides, preserve the progression. A final-state screenshot alone may not test the reasoning the exam expects.

## Second-pass method

After drafting, review every source page again without trusting the first outline. For each page, point to the card that covers its examinable argument or record why no card is appropriate. Then review the deck independently from the source:

- identify near-duplicate questions;
- find answers that rely on an unseen slide;
- turn important diagrams or code into interpretation questions;
- add follow-ups that connect lectures;
- check that examples use internally consistent values and terminology;
- challenge claims that are stronger than the source supports.

Finally simulate an oral exam. Ask the heading, answer aloud from memory, then probe “why?”, “what changes if?”, “show me an example,” and “what is the tradeoff?” Strengthen the card when the written answer cannot support those probes.

## Handling external verification

Use external sources only when they materially improve correctness or resolve ambiguity. For standards, protocols, APIs, laws, or current software, verify against primary and current documentation. Keep the lecture citation and clearly label any corrective note so the student knows the difference between course framing and verified behavior.
