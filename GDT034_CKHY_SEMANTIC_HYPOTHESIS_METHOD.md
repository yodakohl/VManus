# GDT034 CKHY semantic-hypothesis transfer

GDT034 isolates the GDT033 semantic gloss from CKHY's formal status.  The
single hypothesis is:

> CKHY is associated with a visible parallel/fused leaf-or-stalk
> configuration.

This hypothesis is not part of the parser.  Failure rejects only this visual
gloss.  It does not reject CKHY as a reproducible residual host and does not
change any GDT016, GDT031, GDT032, or GDT033 formal result.

## Frozen target and observation

The only target is Herbal Currier-A page **f14r**, selected before querying its
CKHY status.  Source-bound direct inspection used Yale IIIF canvas 1006100 at
`https://collections.library.yale.edu/iiif/2/1006100/full/1600,/0/default.jpg`
(JPEG SHA-256 `8037a9f96a45d0650cd0c1c0b460249127a00b4d4c00a5d6aad445696039fc82`,
1600 x 2247).  The neutral direct observation is: two vertically separated
clusters contain multiple long narrow leaf-shaped forms; their bases converge
through multiple red branch/stem lines toward one central upright axis.  The
classification `COMPARABLE_PARALLEL_OR_FUSED_LEAF_STALK_GEOMETRY` is an
`AI_DIRECT_VISUAL_OBSERVATION`, not an existing human annotation and not a
botanical identification.

The existing human catalogue independently describes the leaves as arrow-like
and upward-pointing and says that all leaves connect to one point.  This is
supporting visual provenance, not a text-derived selection.

## Frozen prediction

The primary prediction is exact and binary: f14r contains at least one GDT016
row whose frozen `residual_host` is exactly `ckhy`.  The renderer forms admitted
by the parent hypothesis are exactly `ckhy`, `chckhy`, `checkhy`, and
`shckhy`; no new normalization or near-match is permitted.

- `PASS_SEMANTIC_GLOSS_PROVISIONAL_TRANSFER`: at least one exact CKHY host is
  present on f14r.
- `FAIL_SEMANTIC_GLOSS_REJECTED`: no exact CKHY host is present on f14r.

The test is page-level because no inscription is authorially owned by a
specific plant component.  A hit cannot identify which leaf, stalk, plant, or
text field the host describes.  After reveal, the runner may report the fixed
whole-Herbal-A CKHY page prevalence and alternate-reading stability only as
context.  It may not search for an alternative CKHY meaning, select a nearby
host, add pages, weaken the visual criterion, or reinterpret a miss.

This is prospective in query order but not a pristine observer-blind holdout:
the manuscript transcription and broad morphology inventories existed in the
repository, and unrelated f14r forms have appeared in earlier corpus-wide
outputs.  No f14r CKHY-presence query was made for this experiment before the
prediction artifact was frozen.  f84r remains sealed and is not opened,
retained, queried, joined, or scored.
