# GDT676 method

## Question

When GDT675's 51 external exact-spelling transfers are placed back into their
complete lines, do they still produce useful, scope-consistent readings, or do
they collapse into generic prose, action/result conflicts, or hidden unknowns?

## Fixed material

No new manuscript page is opened. The build consumes three published GDT675
artifacts:

- `../gdt675_f81r_card_occurrence_conflict_scan/artifacts/TOUCHED_LINE_OVERLAY.tsv`:
  the 51 complete ZL3b lines before and after the one-position GDT675 overlay;
- `../gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv`:
  the exact transferred surface, reader support, render mode and applied
  meaning at each position;
- `../gdt675_f81r_card_occurrence_conflict_scan/artifacts/RESULT.json`: the
  upstream status and counts.

The GDT676 source tables supply explicit, author-written renderer decisions
and contextual paraphrases. They are semantic inputs to the build, not values
algorithmically inferred by `run.py`:

- `src/LINE_MODE_SPECS.tsv`: licensed action ordinals and the inherited
  action/scope audit;
- `src/LINE_READER_SPECS.tsv`: one manually composed, token-preserving German
  working reading per line, with every residual form written as
  `⟦surface:?⟧`;
- `src/VALUE_ATTACHMENT_SPECS.tsv`: 17 local head/value decisions;
- `src/SYNTAX_TEMPLATES.tsv`: eight reusable scope rules;
- `src/PASSAGE_SELECTIONS.tsv`: four diagnostic passages selected for the
  report.

Both f84 and f84r are forbidden throughout. ZL3b is the source surface;
alternate-reader support is inherited from GDT675 and is not counted as an
independent manuscript occurrence.

## Construction

For each of the 51 lines, `src/run.py`:

1. preserves the complete source-token sequence and checks equal token-vector
   lengths before and after GDT675;
2. verifies that exactly one formerly unknown position changed and that it is
   the exact GDT675 occurrence for that locus and ordinal;
3. verifies every licensed action against its visible ordinal and surface;
4. requires the multiset of `⟦surface:?⟧` markers in the working line to equal
   the residual-unknown multiset exactly;
5. assigns each of the 479 positions, in priority order, to `NEW_V50`,
   `RESIDUAL_UNKNOWN`, `INHERITED_NARROW_CARRIER` or
   `INHERITED_OTHER_ASSIGNED`;
6. rejects hard generic filler such as *Arbeitsgut*, *Arbeitsgang*, *work
   item* or *work cycle*;
7. checks and materializes the author-written line readings as line, page,
   register/hand, passage, value-attachment and syntax audits plus the complete
   readable edition.

The resulting partition is 51 new V50 positions, 136 residual unknowns, 77
inherited narrow carriers and 215 other inherited assignments, totaling 479.
The narrow carrier screen finds 105 positions/106 matches in the literal token
overlay and 113 positions/114 matches in the fluent working reader. The wider
class sensitivity screen additionally matches 311/343 assigned literal values
(`0.906706`) as substance, grade, measure, state or other class-level readings.
These are rendered slots, not established concrete meanings.

The line renderer distinguishes four practical modes: 11 action sequences, 18
mixed records, 14 nominal registers and eight quantity labels. It licenses 48
action positions on 29 lines. Values bind only to a visible compatible local
head: ten bindings are accepted (including the nominal f26r.2 correction),
three remain provisional, and four proposed jumps are rejected.

## Decision rule

The experiment passes only if all of the following reconstruct exactly:

- 51 loci, 479 tokens and one GDT675-applied position per line;
- information counts `51/136/77/215`, with 343/479 positions assigned after
  V50 and 136 gaps still visible;
- literal-overlay narrow counts `105/106`, working-reader narrow counts
  `113/114`, 311/343 assigned literal values matched by the extended class
  sensitivity screen, and zero hard-generic matches in either layer;
- two complete and 49 incomplete lines, including the residual distribution
  `0:2, 1:9, 2:17, 3:8, 4:8, 5:6, 7:1`;
- 50 GDT675 applications holding at line scale and exactly one named override,
  f26r.2;
- all action, value, mode, passage and file-hash audits, followed by a
  byte-identical rebuild. Replay proves that the declared edition is
  reproducible; it does not validate the historical truth of its German
  paraphrases.

Run:

```bash
python3 experiments/yolo/gdt676_v50_external_line_renderer/src/run.py
python3 experiments/yolo/gdt676_v50_external_line_renderer/src/validate.py
```

## Claim ceiling

This is a context-aware practical renderer over 51 already touched lines. It
is not plaintext or a historical codebook, and it does not establish a
language, phonetic value, manuscript-wide lexeme, named substance, plant,
disease, patient, cure or procedure. Assigned working meanings remain
exploratory; every residual gap and broad carrier stays visible rather than
being converted into fluency.
