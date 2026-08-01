# Oral-exam card-writing rubric

## The unit of learning

Make one card test one coherent argument: a claim together with the reasoning needed to defend it. Do not make a separate card for every bullet if the bullets form one mechanism. Split a card when its parts could be answered independently or when recalling one part gives away another.

A strong deck mixes several question forms:

- concept and purpose: what a mechanism is and why it exists;
- mechanism: how state or information moves through the system;
- comparison: dimensions, assumptions, benefits, and costs;
- causal reasoning: why one design choice produces an effect;
- worked example: trace, calculate, derive, place, or transform;
- artifact reading: explain a diagram, command, schema, code fragment, table, or packet;
- limitation and failure: when the method does not work or what it sacrifices;
- synthesis: connect concepts introduced in different lectures.

Avoid trivia unless the source or exam style clearly demands it.

## Question quality

Phrase the heading as a natural oral-exam prompt. Include the scope needed to distinguish it from nearby cards. Prefer:

> How does X achieve Y, and what tradeoff does that design introduce?

over:

> What is X?

Useful prompt verbs include explain, compare, trace, justify, derive, interpret, diagnose, and predict. A prompt may contain two clauses when the second forces the student to connect mechanism and rationale; do not create sprawling checklists.

## Answer architecture

Build the answer in this order when applicable:

1. **Thesis:** answer the question directly in one or two sentences.
2. **Mechanism:** identify actors, inputs, state, decisions, and outputs in causal order.
3. **Rationale:** explain why the mechanism achieves the goal.
4. **Example:** work through a concrete instance, not merely name one.
5. **Tradeoffs or limits:** state the cost, assumption, failure case, or alternative.
6. **Takeaway:** end with the distinction the examiner should hear.

Do not force labels into every answer. Clear connected prose is more important than a rigid template.

## Evidence of understanding

The answer should let the student handle likely follow-ups without returning to the slide. Define technical terms at first use, connect equations to their quantities, and distinguish control decisions from data-plane actions, logical abstractions from implementations, and an example trace from general behavior.

When a card uses an image, code block, or table, explicitly tell the learner what to read from it. An unexplained visual is decoration, not an answer.

When the source appears inaccurate, separate three things:

- what the lecture is trying to teach;
- what the displayed example actually does;
- what the authoritative specification or mathematics requires.

Use a concise caveat rather than silently teaching the error. Verify high-stakes corrections with primary sources.

## Length and clarity

Write enough to explain the reasoning, but remove sentences that do not improve recall or oral delivery. Prefer short paragraphs, ordered steps for sequences, and a small table for repeated comparisons. A typical answer can be spoken in roughly one to three minutes; a substantial worked example may be longer.

Do not answer with only a definition, a copied slide, or an unexplained list. Do not hide the core answer beneath historical context. Avoid vague claims such as “more efficient” unless the relevant resource, latency, state, or complexity is named.

## Final review questions

For every card, ask:

- Does the first paragraph directly answer the prompt?
- Is the causal chain explicit?
- Could the student explain why, not only what?
- Is there a concrete example when abstraction alone is hard to retain?
- Are comparisons made on consistent dimensions?
- Are caveats accurate and proportionate?
- Does the source line identify where the claim came from?
- Would this answer sound coherent when spoken aloud?
