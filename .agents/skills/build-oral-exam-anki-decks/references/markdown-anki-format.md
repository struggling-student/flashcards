# Markdown and Anki format

## Recommended project layout

```text
CourseName/
├── lectures/                 # original PDFs or slides
├── flashcards/
│   ├── 001-first-topic.md
│   ├── 002-second-topic.md
│   ├── anki.css
│   └── course-001-s07.jpg    # all referenced media beside Markdown
├── anki/
│   ├── 001-first-topic.apkg
│   └── course-name.apkg
├── visuals.json
├── question-baseline.json    # important for later updates
└── requirements-anki.txt
```

Keep generated APKGs out of `flashcards/`. Preserve the original course material unchanged.

## Canonical card source

Use YAML front matter to select CSS, and use one level-two heading per card:

````markdown
---
css: anki.css
---

## How does a match-action pipeline process a packet, and why is it programmable?

A match-action pipeline parses selected header fields, applies a sequence of tables,
and executes the action associated with each match. Programmability comes from
controlling which fields form keys, how tables are populated, and what actions
change packet or metadata state.

![Pipeline stages](course-010-s18.jpg)

The diagram should be read from left to right: parsing creates structured fields;
each table consumes current state; an action may alter the state seen by later tables.

```c
table ipv4_lpm {
    key = { hdr.ipv4.dstAddr: lpm; }
    actions = { ipv4_forward; drop; }
}
```

The key selects the destination prefix, while the control plane chooses which action
and parameters a matching entry supplies. The program defines possible behavior;
runtime entries choose behavior for current policy.

_Source: Lecture 10, slides 18–21._
````

The heading text becomes the question and therefore participates in note identity. The body becomes the answer. Keep source lines specific enough to trace and review.

## Media constraints

`markdown-anki-decks` and Anki impose practical constraints:

- put an image or sound file in the same directory as the Markdown that references it;
- reference only the basename, for example `![Topology](course-004-s12.jpg)`;
- do not reference `./images/file.jpg`, `../file.jpg`, or an absolute path;
- make every media basename globally unique across the whole package;
- use stable deterministic names such as `course-004-s12.jpg`;
- keep source resolution high enough for mobile zoom, but compress images to control deck size;
- use useful alt text.

Repeated references to the same basename are fine. Two different files with the same basename are not.

## Code and tables

Use fenced blocks with a language tag supported by the installed Markdown/Pygments stack:

````markdown
```xml
<filter type="subtree">
  <interfaces xmlns="urn:example:interfaces"/>
</filter>
```
````

Choose the closest reliable lexer when a domain language has no dedicated lexer. For example, `c` may be more robust than an unsupported `p4` tag. Treat syntax highlighting as presentation; always explain semantics in prose.

Use Markdown tables for compact, repeated comparisons. Keep tables narrow enough for mobile screens and add responsive CSS so they can scroll horizontally.

## Dependencies

Pin a reproducible environment. A working baseline is:

```text
markdown-anki-decks==1.1.1
click<8.2
pymupdf==1.28.0
Pygments==2.19.2
```

`markdown-anki-decks` brings in `genanki` and Markdown-related dependencies. Confirm versions in the target environment rather than assuming these remain current forever.

## CSS expectations

Style prose for readable line length and spacing. Include responsive rules for images, `pre` blocks, and tables. Include `.nightMode` colors and Pygments token selectors when code highlighting is used. Verify the rendered HTML because source fences and source tables do not guarantee that Anki receives highlighted code and actual table elements.
