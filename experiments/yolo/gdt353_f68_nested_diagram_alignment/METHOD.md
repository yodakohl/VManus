# GDT353 — f68 nested-diagram alignment

## Question

Do the eight clockwise radial titles of f68v1 and the eight clockwise radial
titles of f68v2 behave as two renderings of the same ordered formal cycle?

The source-only motivation is geometric. The human catalogue describes f68v1
as sixteen outer sectors alternating star-filled and text-filled sectors,
therefore eight radial text sectors. It describes f68v2 as eight sectors with
eight boundary titles and four interleaved star-label sectors. Stolfi's manual
comments order f68v1 E1 clockwise from its double radial stroke and f68v2 E1
clockwise from its first star point.

This is not a semantic or external-homologue test. The formal surfaces were
already displayed during the exploratory capacity audit, so the entire result
is `POST_EXPOSURE_EXPLORATORY`.

## Frozen arrays

- f68v1 E1: loci `f68v1.3` through `f68v1.10`, in manual clockwise order.
- f68v2 E1: `f68v2.18,.7,.9,.10,.12,.13,.15,.16`, the existing human atlas's
  clockwise order.

The f68v2 four star-label loci are excluded: they occupy a different
interleaved visual class. Circular texts and prose are excluded.

## Scores

For ZL3b, IT2a, and RF1b separately, preserve source-group boundaries inside
each title and score:

1. diplomatic-surface `SequenceMatcher` similarity;
2. diplomatic-surface boundary-marked trigram Jaccard;
3. primary STA-family `SequenceMatcher` similarity;
4. primary STA-family boundary-marked trigram Jaccard.

For each representation report the source-start alignment and the best of all
eight rotations times two directions. The exact null enumerates all 8! target
orders and repeats the same 16-way search. Alternate readings are sensitivities,
not independent samples.

A disclosed post-hoc length sensitivity uses the eight ZL3b title lengths,
maximizes Pearson correlation over the same dihedral search, and uses the same
8! null.

All global transcription inputs are raw-field guarded to the sixteen listed
loci. Rows beginning `f84` are rejected before parsing.

## Decision

Ordered formal support requires an inclusive exact tail at most .05 in all
three readings for at least one representation, with the same direction and
rotation. Failure closes only this eight-title formal-alignment hypothesis.

## Claim ceiling

No result identifies the diagrams, their sectors, a word, language, meaning,
plaintext, or translation. A negative result does not deny visual resemblance;
it says the two ordered title cycles do not show exceptional formal alignment
under the declared measures.
