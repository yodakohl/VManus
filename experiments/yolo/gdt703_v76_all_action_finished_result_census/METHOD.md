# GDT703 method

## Question

Does the first semantic item after every one of the 83 current action clauses
contain a small, complete set of already written finished-result states, and do
any of those cases support an occurrence-bound practical result relation?

## Inputs

- GDT695's 175-clause realization and its 83 action clauses.
- GDT687's independent occurrence dispatch for bound-`dy` result states.
- GDT700's exact state-only checkpoint classification at `f26r.2#5`.
- GDT702's cumulative C001–C012 graph, position atlas, token overlay, line
  overlay, span freeze, and result summary.
- `src/V76_7_FINISHED_RESULT_CASE_SPECS.tsv`, which fixes the seven candidate
  readings, their strongest rivals, and their local/nonportable status.

## Method

1. Traverse every GDT695 `ACTION_CLAUSE` in source order.  Complete the whole
   clause before selecting anything to its right.
2. Select only the first ordinal of the immediately following clause in the
   same locus.  If no clause follows, record `END_OF_LINE`.  Do not skip a
   nominal or action entry to reach a more attractive later result word.
3. Join that exact first ordinal to GDT687.  Retain as candidates only
   `HIGH / NOMINAL_FINISHED_RESULT_STATE` occurrences.  This yields seven
   cases, not a surface or suffix search.
4. Compare each candidate's written operation and local material/output line.
   Keep C012; add the two explicitly local working relations C013 and C014;
   preserve the four weaker juxtapositions as `HOLD_OPEN` readings rather than
   deleting them.
5. Recompose the cumulative occurrence graph.  C013 adds `f26r.2#4→#5` beside
   the existing C011 `#4→#6`; it must not manufacture `#5→#6`.  C014 creates
   M010 on `f115r.23#3→#4` and stops before action #5.
6. Carry the relation metadata over the unchanged 479 token glosses, 51 line
   translations, and 3 bound spans.  Submit both new edges to the executable
   GDT388 intake gate and retain its exact not-score-ready result.

## Decision rule and claim ceiling

An admitted edge must use the complete left action and the first immediate
right semantic item, whose finished-state reading already exists independently
in GDT687.  Its local operation/material reading must be coherent enough to
serve as a practical working hypothesis.  The edge remains occurrence-bound;
no adjacency, action-surface, result-surface, or morphology default follows.

V76 is an exploratory workshop relation edition.  It introduces no Voynich
word meaning, plaintext claim, language identification, historical codebook,
page, or sealed-material access.  Its two new relations can be replaced by a
better practical account without changing the underlying word reader.
