# GDT721 method

## Question

Can the four active readings `pol`, `lor`, `l` and `r` be made consistently
compositional without treating naked one-character tokens as free material
words, and can every legacy bound span still referenced by V93 be made
executable again?

## Inputs

- V93 active lexical, exact-position, held-reading, complete-confidence, span,
  directive and f7r.2 artifacts from GDT720
- GDT635 four-head cells, remainder grids, neighbor swaps and initial-head scope
  profiles
- GDT636 explicit working-dictionary compositions
- GDT693 OR model and exact lor control
- GDT690 exact l noun/head selection
- GDT682 alternate-reader join for f7r.2
- GDT695 frozen B001–B003 boundaries and renderer values

All evidence is enumerated in `src/V94_30_PRIMARY_EVIDENCE_BINDINGS.tsv` and
replayed by the validator. f84 and f84r are forbidden.

## Method

1. Bind each target to its exact V93 lexical row, active position and repair
   queue row.
2. Test the scoped composition model against the complete GDT635 head/remainder
   grids and exact neighbor frames.
3. Keep `pol` and `lor` as whole defaults only if the same component values
   predict their attested sister forms.
4. Separate the productive initial L/R head priors from naked active tokens.
   If an active token is consumed by an admitted alternate-reader span, suppress
   its standalone output and retain the concrete value only at the appropriate
   layer.
5. Compare every V93 context span reference with the canonical V93 renderer.
   Restore a missing span only from the frozen GDT695 boundary and exact renderer
   value, without changing its wording.
6. Preserve all non-target lexical rows, contexts, one-shot directives and
   f7r.2 units; regenerate the complete confidence/evidence dictionary.

## Decision rule and claim ceiling

Pass requires four exact target repairs, zero new score credit, no component
global export, exact preservation of 320 non-target lexical rows and 475
non-target contexts, five executable two-position spans, byte-identical
B001–B003 renderer values, and a complete 1,586-reading dictionary with a
default, confidence, evidence and counterevidence on every row.

The result is an exploratory compositional renderer, not recovered plaintext or
a historical codebook identification. Period labels are functional analogies.
