# GDT831 held-label visual review

2026-09-05. Annotator: `visual_B`. Status: visual annotation completed before
access to any GDT831 classifier values or calibration labels.

I personally inspected all twelve fixed f81r/f83r coordinate plates listed in
`TILES.json` with the image viewer. Each plate displays the unchanged native
192 by 192 source tile at four-times nearest-neighbour scale; coordinate ticks
are outside the source image. I selected four visually dense writing-core
center pixels and four visibly unmarked nearby paper center pixels per tile.
The result is 96 labels: 48 `ink` and 48 `paper`. Each tile includes points on
multiple visibly distinct glyphs, with horizontal and vertical spread.

Selection used visible stroke continuity, shape and local surroundings. No
brightness values, thresholds, detector output, OCR or numeric pixel features
were inspected or used. Paper points were chosen near writing and include the
visible uneven native paper texture. Visibly ambiguous stroke edges, possible
faint traces and possible bleed-through were avoided. Some paper points lie
within clearly open glyph spaces; they label the selected center only.

I then inspected all twelve ring-overlay review plates with the source centers
left unobscured. This visual coordinate check caught several initial coordinate
estimates on a loop interior or near an edge; I corrected them using the source
view and rechecked the resulting markers, still without model outputs. The
final TSV contains those visually checked coordinates. Red I1-I4 rings identify
ink labels; blue P1-P4 rings identify paper labels. Marker plates are temporary
review aids, not transformed evidence or model inputs. The table's tile-local
coordinates refer to single native pixels, not a claim about every pixel in a
3 by 3 neighbourhood.

These pages and source photos were already inspected in GDT830. Only the newly
collected held labels are withheld from GDT831 scalar calibration; the images
are not globally unseen manuscript evidence. Selection targets clear examples,
not random pixels or an exhaustive segmentation. Agreement on this set would
not establish accuracy on faint ink, stroke edges, bleed-through, every paper
texture, complete images or any historical writing sequence. Physical ink
chemistry and microscopic absence of traces are not certified by these RGB
observations. No new manuscript page, public decipherment method, external LLM
API, model value or calibration label was accessed during this annotation.

## Tile-specific visual limitations

These notes describe visible difficulties in the inspected tile, not measured
error rates or certification of every nearby pixel.

| Tile | Uncertainty handled during selection |
|---|---|
| f81r_B1L | Strong mottled paper texture and ragged curved-stroke edges; points were placed within dense strokes or clearly outside them. |
| f81r_B1R | Small loop interiors and faint diagonal continuations could be mistaken for a core or for paper; two ink coordinates were moved to clearer dense portions. |
| f81r_B2L | Tall stems and broad loops have uneven edges; the faint curved continuation at the right was avoided. |
| f81r_B2R | The lower-right loop lies near a separate upright stroke; the initial ink estimate fell in their gap, and a nearby paper estimate was too close to the loop edge. |
| f81r_B3L | The right tall stroke and a lower curved stroke had initially misestimated edges; both ink coordinates were moved inward. Faint connecting tails were avoided. |
| f81r_B3R | Open loop spaces and fine diagonal tails complicate local selection; two ink points were moved from an edge/interior estimate to visibly denser stroke portions. |
| f83r_B1L | Long fine descenders and a protruding upper arm make nearby paper boundaries uncertain; the paper point near that arm was moved farther outside it. |
| f83r_B1R | Broad loops vary in apparent density, while long curved continuations become faint; the central ink point was moved to the dense connecting neck. |
| f83r_B2L | Broad curved forms and uneven native texture surround the chosen points; the upper-right ink point was moved away from the outer loop edge. |
| f83r_B2R | Interlocking bars, open bowls and paired stems leave small paper spaces; a bowl-interior ink estimate and a near-arm paper estimate were corrected. |
| f83r_B3L | A fine descending continuation and the broad middle-row opening could confuse edges with cores; one ink point was moved into the adjacent dense curved stroke. |
| f83r_B3R | Two loops contain pale interiors surrounded by broad strokes; initial ink estimates in those interiors were moved to their connecting neck or outer stroke. |

## Exact visual coordinate corrections before model access

The initial TSV and review images were overwritten during this annotation
session rather than retained as separate frozen artifacts. The exact original
and final coordinates remain available in the annotator's tool-call history,
including the explicit replacement command. The following sixteen changes are
transcribed from that history. They all preceded access to classifier values;
no class changed. Other labels retained their initial coordinates. Coordinates
are native tile-local `(x,y)` center pixels.

| Label ID | Initial | Final |
|---|---:|---:|
| f81r_B1R_I1 | (57,13) | (63,14) |
| f81r_B1R_I3 | (105,60) | (100,60) |
| f81r_B2R_I4 | (178,160) | (172,160) |
| f81r_B2R_P4 | (157,166) | (157,174) |
| f81r_B3L_I2 | (135,35) | (128,35) |
| f81r_B3L_I3 | (103,105) | (94,105) |
| f81r_B3R_I3 | (104,112) | (108,115) |
| f81r_B3R_I4 | (64,167) | (58,168) |
| f83r_B1L_P3 | (48,91) | (53,88) |
| f83r_B1R_I3 | (91,99) | (94,95) |
| f83r_B2L_I2 | (166,32) | (171,33) |
| f83r_B2R_I2 | (35,91) | (29,92) |
| f83r_B2R_P3 | (93,88) | (98,91) |
| f83r_B3L_I3 | (24,93) | (27,94) |
| f83r_B3R_I3 | (66,92) | (64,99) |
| f83r_B3R_I4 | (154,104) | (160,105) |

This documentation addition does not change the final held-label TSV. The
coordinator subsequently reports personally viewing all twelve final held
review overlays and accepting those coordinates without further changes.
