# GDT831 — independently annotated ink/paper point control

2026-09-05. Register and publish before any classifier score on manuscript
pixels, including calibration. All visual coordinates receive a hash lock
before that first score. Label acquisition is independent of classifier
output, not independent of visual darkness. Selected-point bias is explicit.

## New question and predecessor

Can one fixed local-contrast primitive distinguish newly visually annotated,
clear writing-core center pixels from nearby visibly blank paper on four
admitted photographs? GDT830's maximum-envelope observation failed its real
paper diagnostic. Its parameters, continuation experiment and outcome remain
closed. This is a new observation endpoint with new visual labels; no old
retrieval score or disputed production path is evaluated or rescued.

The internal route-check returns GDT830 as the direct predecessor. GDT360 and
the GDT002 existing-annotation synthesis concern formal/semantic grounding of
previous object/relation annotations; neither supplies ink/paper center labels.
The closed shape-atlas family does not establish this pixel distinction or
authorize glyph identification. No public approach search is used.

## Images, geometry and labels

Use only bound native Yale JPEGs f76r, f77r, f81r, f83r. f84 and f84r remain
sealed. SOURCES.json carries hashes, dimensions and official endpoints.
Six 192×192 native-pixel tiles per page are fixed in TILES.json. Their centers
use GDT830 source ordinals 2,7,12 and one-third/two-thirds of each registered
strip width. Geometry is inherited, not selected from new detector scores.
There is no new page admission or transcription access.

Visual A annotates f76r/f77r; visual B separately annotates f81r/f83r. Each
views original RGB crops at exact nearest-neighbour ×4 with coordinate ticks
outside the image. Select four clear dense writing-core center pixels and
four visibly blank nearby paper center pixels per tile: 192 labels total.
Use spatial spread and more than one glyph; include nearby paper texture.
These are centerpixel judgments, not 3×3 patch masks. Uncertain edges, possible
faint strokes, bleed-through and illustration marks are not force-labeled;
record uncertainty notes. If four clear points of either class are unavailable
in a tile, stop acquisition rather than replacing the tile. The annotations
are model-assisted visual judgments, not independent physical ink certification.

Each annotator reviews coordinate overlays; a second visual reviewer checks
overlays before scores. Obvious coordinate mistakes may be corrected at this
stage with a recorded reason. All final coordinates and review notes are
frozen before scoring; no prediction-based exclusions or replacements.

f76r/f77r calibrate one scalar threshold. f81r/f83r are held from this new
labeled calibration only: their images were already exposed in GDT830 and
visual work. The two split-specific annotators can introduce reader differences;
this is not an inter-reader agreement study or historically unseen data.

## Fixed observation and calibration

For each tile retain a real 16-pixel halo from its source image. Round the
float32 mean RGB to uint8 grayscale. Apply median3, then median31 to that
smoothed grayscale. Let S be the first image and B the second. The score is
float32(B−S)/max(B,1). Retain the inner 192×192 region. No maximum filter,
OCR, learned classifier, contrast enhancement or synthetic manuscript image.
These operational scales are not historical nib measurements. Raw RGB is
not replaced for any future physical photometry.

Ink prediction is score >= threshold. Threshold candidates are exactly
0.02,0.03,...,0.30. Select the smallest candidate achieving paper specificity
at least 0.95 on EACH calibration page. No candidate means CALIBRATION_STOP.
After selection require ink recall >=0.90 and paper specificity >=0.95 on each
calibration page, plus both >=0.75 on every calibration tile. Failure stops
before held feature extraction. Do not choose another threshold to repair it.
Persist calibration scores and selected threshold before separately invoking
held evaluation. Held values cannot change threshold or annotations.

On each held page require ink recall >=0.90 and paper specificity >=0.95, plus
both >=0.75 in every held tile. Four ink and four paper points per tile mean
at least 3/4 correct per class; 24 points per class/page mean at least 22/24 ink
and 23/24 paper correct. Passing all requirements is
RESTRICTED_POINT_CONTROL_PASS; any held failure is HELD_POINT_CONTROL_FAIL.
All-ink and all-paper constants must fail the joint requirements.

## Controls and ceiling

Before real scores run deterministic synthetic textured/sloping paper and
planted-stroke controls, changed light-field control, halo equivalence and
an explicit dense-dark-area limitation fixture. These verify software and
challenge the prior failure mode; they cannot certify manuscript ink.
An independently written validator reconstructs threshold/counts/gates and
checks source/annotation/geometry hashes. Pixel replay, if performed, uses
an independent implementation of the prescribed arithmetic and is described
separately from visual validity.

Report integer page/tile counts and every scored label. Do not compute a
pixel-independent significance or population accuracy interval from manually
selected, spatially dependent points. Even a pass applies only to clear
selected cores versus nearby selected paper in these photos. It establishes
neither a complete ink mask, faint/edge recovery, pen state, ink chemistry,
dating, writing order, intended reading order, glyph values nor translation.
No semantic relation packet is produced. No automatic return to GDT830.
