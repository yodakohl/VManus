# GDT704 method

## Question

Among every immediate action-to-action transition already exposed by GDT703,
does an explicitly repeated material head distinguish a plausible continuation
of the preceding output from a repeated ingredient or a new batch?

## Inputs

- GDT695's 175 complete clause realizations.
- GDT703's complete 83-action right-context census and cumulative C001–C014
  graph.
- `src/V77_15_ACTION_CONTINUATION_SPECS.tsv`, which gives every one of the 15
  action-to-action transitions a practical material/process reading and rival.
- `src/V77_2_OBJECTLESS_POST_RESULT_SPECS.tsv`, which fixes the C011 replay and
  the weaker C016 comparison.

## Method

1. Select all and only GDT703 rows whose immediate right clause is another
   action.  Preserve each complete left and right clause, including structural
   closure tokens.
2. Classify the two actions' written material heads as exact repetition,
   deictic target, related explicit head, different explicit head, or no
   written head.
3. For exact repetitions, distinguish the preceding action's output from an
   ingredient merely repeated in parallel additions.  Do not equate identical
   nouns with identical batches automatically.
4. Admit C015 only at `f26r.2#6→#8`: C011 already carries the herb into the
   complete cooling clause #6–7, and #8 immediately writes `Krautdroge` again
   while applying the next operation.  Keep #7 as the structural closure and
   #9 `ls` (wood) as the right break.
5. Compare the only two objectless actions following a finished-result block.
   Replay C011 without inventing #5→#6.  Keep C016 (`f115r.23#4→#5`) open
   because #5 has neither deixis nor a written material head and #6
   `Samenposten` is a competing patient.
6. Recompose the cumulative graph and project relation metadata over the
   unchanged token, line, and bound-span readers.  Submit C015 to the executable
   GDT388 intake gate and retain its exact not-score-ready result.

## Decision and ceiling

C015 is an occurrence-bound B-tier working relation, not a rule that every
repeated material word continues the same batch.  C016 is neither erased nor
promoted: it stays available until another local reading fits better or adds a
written anchor.  The experiment adds no word meaning, plaintext claim,
historical codebook, page, or sealed-material access.
