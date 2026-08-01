# Optional audit roles

## Default: one coordinator

Use one coordinator skill invocation for ordinary courses. A single owner keeps question granularity, terminology, deck identity, media naming, and answer style consistent. Perform inventory, authoring, source review, oral simulation, and validation as separate passes even when one agent does all of them.

## When delegation helps

Use multiple agents only when the user authorizes delegation, the environment permits it, and the corpus is large enough for independent bounded audits. Delegation is most useful after the coordinator has inventoried the course and defined the card rubric.

Assign roles such as:

- **source-range auditor:** review a non-overlapping set of lectures and report missing or weak arguments;
- **artifact auditor:** inspect diagrams, code, tables, formulas, and worked examples for potential cards;
- **oral-exam critic:** challenge questions and answers with likely follow-ups;
- **final QA auditor:** independently compare the finished deck, source map, and build outputs.

## Safe coordination pattern

Give auditors read-only, bounded tasks and a shared report schema:

```text
Source range:
Existing card or NONE:
Finding:
Recommended action: add | enrich | merge | caveat | no card
Suggested question:
Answer points:
Useful visual/artifact:
Source location:
Confidence:
```

Do not let several agents concurrently edit the shared Markdown or media directory. The coordinator reconciles overlaps, decides card boundaries, applies edits, preserves old headings, and runs the build and validation. Treat auditor suggestions as evidence to evaluate, not automatically accepted changes.

If delegation is unavailable, execute the same roles serially. Do not reduce coverage or QA merely because only one agent is working.
