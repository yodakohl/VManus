# GDT059 — HPR2 external-information localization

## Purpose

Localize exploratory external content signal among HPR2 layers without
assigning a meaning to any Voynich form. Archived visual/semantic annotations
are used only as hypothesis-generation outcomes, never confirmation.

## Panels

1. `EXACT_LOCAL_ALL`: one row per existing exact human-annotated locus,
   aggregated across its physical source groups.
2. `EXACT_LOCAL_UNHEDGED`: the unhedged sensitivity subset.
3. `PAGE_CATALOGUE`: confirmed-prose groups aggregated by page and joined to
   pre-existing human catalogue source tags.

All evaluation holds out the complete physical folio. ZL3b/IT2a/RF1b are not
replicates. f84r is filtered before annotations or formal fields are retained.

## HPR2 decomposition

For each group, remove in order: terminal B3/display-M class, a frozen
AIIN/AIR/AIN/AR/AL right-family member, carrier-conditioned inner D, and a
licensed O/OT frame. O/OT stripping is licensed only for the three discovery
hosts AR/AL/OL or a host with bare, O-, and OT- forms in the complete GDT016
inventory. The remainder is `PAGE_HOST`. This is an exploratory parser, not a
linguistic segmentation.

## Predictors and nuisance controls

The fixed predictor set is:

- raw exact group bag and raw character-trigram bag;
- residual-root exact bag and character-trigram bag;
- PAGE_HOST exact bag and character-trigram bag;
- PAGE_HOST plus compiler signature;
- compiler-only signature;
- RIGHT_FAMILY only;
- B3 only.

For every human outcome code, use five-nearest-neighbour prediction under
weighted-Jaccard distance. Training excludes the target physical folio.
Candidate pools match section and Currier, backing off to section only when
necessary. A shared nuisance distance then fixes hand, layout/kind, physical
group and line counts, groups per line, and the catalogue P/L/C/R profile.
The baseline uses the five nearest nuisance neighbours. Every representation
uses nuisance distance plus its own distance and shrinks toward that exact
baseline with fixed weight four. Report held log-loss improvement over the
nuisance baseline, per-folio gains, and all tried variants.

## Renderer-preservation diagnostics

Separately predict held annotated groups from training groups with the same
PAGE_HOST but a different wrapper or right-family member. The O-versus-OT
version requires the exact same PAGE_HOST under opposite O/OT frames on a
different physical folio and in the same section. If absent, report zero
capacity; do not broaden the test.

No positive threshold is preregistered. This is permissive discovery. The
strongest weird correlation and all confounds are reported; no English gloss,
semantic role, word, morpheme, POS, sound, language, plaintext, or translation
is assigned.
