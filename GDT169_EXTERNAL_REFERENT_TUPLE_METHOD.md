# GDT169 — external-referent host versus record-tuple calibration

## Question

When an existing human/layout source independently links two manuscript
objects or homologous records without using Voynich strings, is the linked
text more invariant as an exact `PAGE_HOST` inventory or as the complete
HPR2 record tuple

`(position slot, wrapper, PAGE_HOST, right family, closure)`?

This is an exposed exploratory atlas.  It does not assign a meaning to any
host or tuple and it does not treat a human resemblance judgment as botanical
ground truth.

## Source-only candidate freeze

Candidates are selected before formal scoring from three already cached human
sources:

1. the complete Voynich.nu Herbal-to-pharmaceutical relation census already
   exported by GDT151;
2. the complete internal-Herbal relation census in
   `manual_herbal_internal_relations.tsv`, collapsing the three alternate
   readings to one physical relation;
3. the later Stolfi 2025 plant-pair table, used only to mark a pair as
   cross-source corroborated.  It is not counted as another manuscript sample
   and its independence from the catalogue is unknown.

The five previously published locally owned/provisionally owned pharmaceutical
labels in GDT152 are attached to their external plant pair as a stronger
ownership tier.  Their Voynich strings did not select the relation.

Derived copies of the same human assertion are not counted twice.  Every
`f84*` row is rejected before any descriptive or formal field is retained.
No image is opened and no new visual observation is made.

## Fixed formal comparison

The scorer streams the existing f84-free selection through the one published
GDT062 HPR2 display view.  For each page it constructs:

- an exact multiset of `PAGE_HOST` values;
- an exact multiset of
  `position_quartile|wrapper|PAGE_HOST|right_family|closure`, where closure is
  `DY`, `B3`, or `OPEN`.

For every page pair it reports weighted-Jaccard similarity, shared exact item
mass, the fraction of shared host mass retaining the complete tuple, and the
rank of the asserted partner among pages matched to the target's
section/Currier/hand.  The meaningful layer comparison is standardized
partner excess within that same candidate pool, not raw tuple similarity:
the tuple is a refinement of the host and therefore cannot have greater raw
overlap.

For each locally owned label, the scorer separately asks whether its exact
host and exact complete tuple occur anywhere on the paired Herbal page.  These
five queries are kept separate from whole-page bags.

Candidate priority is frozen from provenance only: local ownership,
cross-source corroboration, same-object versus resemblance wording, physical
folio separation, and the number of distinct relation pairs in the same
evidence class.  Formal scores do not change that priority order.

## Interpretation

- `HOST_MORE_INVARIANT`: exact host standardized excess exceeds tuple excess.
- `TUPLE_MORE_INVARIANT`: the complete tuple standardized excess exceeds host
  excess.
- `BOTH_LOCAL_ONLY`: both are above their matched medians but neither has a
  strong rank.
- `NO_FORMAL_INVARIANCE`: neither representation is above its matched median.
- `INSUFFICIENT_FORMAL_CAPACITY`: one page lacks the HPR2 view or the matched
  pool is too small.

These are exploratory labels, not confirmation decisions.

## Claim ceiling

At most this experiment identifies externally nominated object/layout pairs
whose anonymous formal inventory is unusually similar.  It establishes no
plant identity, component name, semantic role, word, code value, morpheme,
part of speech, sound, language, plaintext, meaning, or translation.

No host-neighbor endpoint is run.  f84r is not accessed.
