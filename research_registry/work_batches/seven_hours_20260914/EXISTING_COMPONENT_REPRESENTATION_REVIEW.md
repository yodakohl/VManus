# Existing component representation review

Bounded source/registry audit, 2026-09-15. No GDT960 cases, target text,
images, keys, reserves, or new selectors were opened. The question was whether
an already fixed component representation can replace whole-plant incidence
without choosing new substrings.

## What is actually fixed

**GDT608** is the only direct candidate. Its method freezes the 64 ordered
GDT605 BPE merges and the 98-unit inventory, with `L+R=M` as the only allowed
component rule (`experiments/yolo/gdt608_compositional_stem_orientation/METHOD.md`,
lines 7-29). DIRECT composition predicts left-side and right-side formal edge
profiles from the two registered children; it does not invent decompositions.
The result is explicitly partial: ATOMIC remains better on all 23 held folios
and 51/64 merges, and the report says the residual merge identity remains
essential. The same report states that this is not linguistic morphology and
supplies no meaning (`REPORT.md`, lines 5-23, 339-347). Thus it is a reusable
formal tree, but not a source-compatible plant/part representation.

GDT282's complete wrapper identity transfers across registers, GDT286's host
association is position-conditioned, and GDT318's line-start/preceding-DY
model is an opaque renderer state machine. Their claim ceilings explicitly
exclude morphology and meaning. They cannot replace a plant-content relation.

GDT915 retains only known terminal-r/l phrase co-variation and explicitly does
not establish productive morphology on unseen stems. GDT916 fails the new-pair
concordance endpoint. GDT928 finds zero paragraph pairs with two disjoint exact
word sequences, so it supplies no larger repeated-content scaffold.

## Conclusion and distinct falsifier

No unchanged corpus-wide component rule currently replaces whole-plant
incidence. The closest available representation is the frozen GDT608 merge
tree, but its empirical boundary is formal edge backoff plus pair-specific
residual identity. A future distinct falsifier would have to freeze an
independently sourced base/part relation first, then predict a qualified target
component pattern from registered `L+R=M` edges on held records. The required
source-to-target part binding is absent here; inventing it would be new
substring mining or a decoder change. Therefore no additional raw proposal was
registered in this audit.

## Root correction

The absence of an established semantic morpheme in GDT608 does not prohibit
using its fixed merge parser as an exploratory formal hypothesis. An allowed
exploratory reading may test the registered `L+R=M` representation against a
source-derived question without first claiming a source-to-target plant
binding. That binding is a prerequisite for semantic confirmation, not a ban on
the exploratory parser test. This correction does not turn GDT608 into a
confirmed morpheme system. The part-qualified Behenian card was not selected as
a GDT960 rescue because the seven Mugwort occurrences remain unchanged.
