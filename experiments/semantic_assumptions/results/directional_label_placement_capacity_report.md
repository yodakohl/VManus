# Directional label-placement source-capacity report

Date: 2026-08-09

## Result

The human exact-locus annotations support one new source-controlled experiment:
**horizontal label placement (east versus west of an illustrated object)**.
They do not support the analogous vertical experiment.

The admitted horizontal panel contains 57 fully ZL3b/IT2a/RF1b-covered loci
in 8 same-page, same-code, same-object-tag strata on 6 physical folios. There
are 39 EAST and 18 WEST rows across three code/object contexts. The largest
folio supplies 23/57 rows (40.35%), below the frozen 45% ceiling, and every
one-folio deletion retains five folios.

The vertical panel has only 18 matched loci on four physical folios and only
two code/object contexts. It fails the six-folio, deletion, and context gates
and is stopped before any text-feature experiment.

An independent nonimporting reconstruction passes all 18 source, coverage,
classification, matching, panel, gate, and claim-ceiling checks.

## Important correction

The exploratory classifier initially searched the unit description together
with the local comment. That incorrectly admitted phrases such as “nymphs at
bottom of page.” It also treated the descriptive phrase “roots bent
Eastwards” as label position. Before any Voynich feature was opened, the
classifier was replaced by a stricter rule:

- search `local_comment` only;
- require an explicit `east of`, `west of`, `above`, or `below/under` object
  clause;
- reject a row if both directions of an axis occur;
- require both classes on the same exact page/panel, exact normalized code,
  and exact object-tag set.

## Interpretation and limit

This panel is not an ownership annotation and does not imply that a label says
EAST or WEST. It only has enough independent, human-described positional
variation for a formal association test that controls page/register locally.
No OCR, automated vision, image measurement, plant identity, or Voynich string
feature was used in this audit.

The pass authorizes a separate target-blind prescore design. Even a later
positive association could at most establish recurrent morphology associated
with described label placement. It could also reflect layout or scribal
practice. It would not by itself establish a direction word, lexeme,
plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/directional_label_placement_capacity/audit_directional_label_placement_capacity.py
./vpy experiments/semantic_assumptions/directional_label_placement_capacity/validate_directional_label_placement_capacity.py
```
