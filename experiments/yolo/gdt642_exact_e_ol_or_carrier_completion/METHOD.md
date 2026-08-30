# GDT642 method

## Question

Do the exact surfaces `cheol`, `cheor` and `tcheol` admit practical material
and part readings predicted by the already observed E/NONE × OL/OR carrier
grid, and do those readings remain usable over all 219 allowed occurrences?

## Inputs and scope

- Frozen V18 dictionary, exact glossary, full line coverage, complete lines and
  one-hole frontier from GDT641.
- The CH/TCH quality arms from GDT624–625, OL/OR carrier contrast and part versus
  portion rivals from GDT628–630, and the E binding-stage model from GDT633.
- The inherited 179-page guarded transcription panel. `f1r` remains excluded;
  `f84` and `f84r` remain forbidden. No new page or image is used.

## Method

1. Freeze three complete-surface candidates and their rivals before rendering
   the target circuits.
2. Materialize the inherited token and alternate-reader projections only
   through the guarded explicit-page selector.
3. Count eleven independently observed prefix rows in the E/NONE × OL/OR
   design. Every row must occupy all four cells; the focal CH and TCH rows must
   remain complete.
4. Audit every ZL3b target token against the fixed V18 context, so an earlier
   promotion cannot make a later candidate appear artificially more concrete.
   A token is concrete-compatible when it is reader-exact and at least two
   other positions in its line already have scoped V18 readings. An otherwise
   exact sparse line is opaque; a non-exact alternate-reader token is a reader
   warning. Opposite-quality neighbours in list-like lines are tagged but are
   not treated as same-slot contradictions.
5. Promote one exact-whole surface at a time, rebuilding all 4,128 line states
   and recording dictionary hashes, coverage changes and newly exposed
   one-hole lines after every round.
6. Replay the builder byte-for-byte and independently reconstruct target
   occurrence, page and reader-exact counts in the validator.

## Working semantics and decision rule

The visible fields are realized rather than erased:

| Surface | Bound parse | Running German realization |
|---|---|---|
| `cheol` | `ch+e+ol` | dry + attributive E + material → trockener Drogenstoff |
| `cheor` | `ch+e+or` | dry + attributive E + part → trockener Drogenteil |
| `tcheol` | `tch+e+ol` | cold-dry + attributive E + material → kalt-trockener Drogenstoff |

A target is accepted when its four-cell family is fully occupied, it has a
non-zero independent reader-exact circuit, all occurrences are rendered, and
no concrete context forces a same-slot opposite or different carrier type.
Opaque contexts are neutral, not confirming evidence. Reader warnings remain
attached to the relevant occurrences.

No free `ch`, `tch`, `e`, `ol` or `or`, substring, wrapper, absent cell or
arbitrary compound is promoted. `Drogenstoff` and `Drogenteil` are compact
pharmaceutical smoothings of material and part carriers; the broader
material/state and part/portion readings remain explicit rivals.
