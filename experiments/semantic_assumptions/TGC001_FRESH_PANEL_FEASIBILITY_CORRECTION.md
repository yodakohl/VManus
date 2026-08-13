# TGC001 fresh-panel feasibility correction

Status: **FROZEN SOURCE-ONLY CORRECTION**.

## Error being corrected

The initial TGC001 capacity artifact published the exact 30-row geometry so
that its arithmetic could be audited, then correctly declared every published
row permanently ineligible for later image review. It nevertheless authorized
target-free calibration for a future fresh 30-row panel drawn from the same
five cells. Those two statements are incompatible unless at least six further
distinct-folio rows remain in every cell.

This correction checks that necessary condition using only the same frozen
manual-transcription sources. It opens no image, crop, trace, or manuscript
score.

## Exact reconstruction

Reconstruct the 676 all-pattern-nonduplicate disagreement groups exactly as in
TGC001. Restrict them to the five published controlled cells. For each cell,
delete every `consensus_group_id` already present in
`tgc001_whole_group_trace_capacity_panel.tsv` and count the remaining rows and
physical folios.

Also compute the stricter whole-folio-fresh count by deleting every row whose
physical folio occurs anywhere in the published panel.

The downstream image experiment is feasible only if every one of the five
cells retains at least six distinct physical folios after the applicable
exclusion. Otherwise stop before synthetic calibration: a synthetic pass could
not authorize an image panel that does not exist.

## Interpretation ceiling

This correction can only stop the proposed same-five-cell TGC001 experiment.
It says nothing about the physical ink, preferred transcription, glyph
identity, sound, alphabet, word, language, cipher, plaintext, meaning, or
translation.
