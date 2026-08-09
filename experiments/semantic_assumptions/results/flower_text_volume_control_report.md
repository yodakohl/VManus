# FLOWERVOL001 text-volume control report

## Status

**Anonymous controls pass; target unrun.**

The experiment reuses FLOWER001's 21-distinct-folio, seven-triplet source
panel but opens a genuinely different root-free channel. It freezes only
confirmed physical-line count, stored manual-transcription word count, and
tokens per line. No glyph, root, word identity, paragraph reconstruction,
OCR, image recognition, or plant name is used.

The first control invocation stopped before output because normalized
hierarchical `surface` spacing is not identical to the interlinear's original
stored `word_count` on every locus. The design already specified the stored
count, so the invalid cross-field equality assertion was removed without
changing a page, measure, statistic, or gate. No target statistic was
extracted.

All `3^7 = 2,187` synchronized within-triplet assignments are exact. The
unique synthetic assignment has tail 1/2,187; alternate-reading disagreement
and block-constant signals both collapse to zero. The three-measure family
maximum has 95th percentile 2.167718794875. The artifact records
`target_assignment_extracted: false`, and no target artifact exists.

A nonimporting implementation independently reconstructs the source panel,
843 prose loci, exact three-measure matrix hash, full orbit, family null, and
all controls in 15 checks. Both artifacts reproduce byte for byte on rerun.

One frozen target invocation is authorized. Even a pass is only a whole-page
text-volume association, not a flower line, word meaning, plant name,
language, plaintext, or translation.

## Reproduction

```text
./vpy experiments/semantic_assumptions/flower_text_volume/run_flower_text_volume.py --mode controls --output experiments/semantic_assumptions/flower_text_volume/CONTROL_RESULT.json
./vpy experiments/semantic_assumptions/flower_text_volume/validate_flower_text_volume_controls.py --output experiments/semantic_assumptions/flower_text_volume/CONTROL_VALIDATION.json
```
