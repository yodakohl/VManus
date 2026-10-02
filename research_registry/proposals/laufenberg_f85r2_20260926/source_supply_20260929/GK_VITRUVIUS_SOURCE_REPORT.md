# GK — A concrete shadow–axis–wind–street comparison sequence

2026-10-02. **SOURCE_TEMPLATE_ACQUIRED; no Voynich reading tested or selected.** IDEA748 now has directly inspected historical source images rather than only a modern translation. The positive result is a layered construction with written role ownership. It does not establish that any Voynich circle depicts this construction.

## What was actually acquired and read

1. **British Library, Harley2767, ff.16v–17r.** The [holding-library catalogue](https://searcharchives.bl.uk/catalog/040-002048598) dates the codex to0800–0824 and identifies its wind diagram on16v. The [official digitization manifest](https://bl.digirati.io/iiif/ark:/81055/vdc_100056038850.0x000001) binds the downloaded canvases to those exact leaves. Root inspected both whole page images at1560pixels width. Original-resolution delivery failed with a broken response; the smaller successful delivery is reported as such, not as the full6010pixel native. The text and broad diagram are readable; small peripheral glyphs are not fully collated.
2. **Vitruvius edited by Fra Giocondo, Venice1511, MPIWG XS9KA6WS, scan pages29–33**, printed leaves10r–12r. The [institutional viewer](https://echo-old.mpiwg-berlin.mpg.de/ECHOdocuView?pn=29&tocMode=figures&url=%2Fpermanent%2Flibrary%2FXS9KA6WS%2Findex.meta&viewMode=image) identifies the edition. Root inspected all five original printed page images, not the1914 redrawing/reproduction found in web results. This1511 source is later than the assumed Voynich production period; it demonstrates a documented representation, not a proven1420 exemplar.

The prior cached modern Vitruvius text supplied I.6.6–8 and the separately declared I.6.12–13 continuation. It was already project-exposed. The new acquisition supplies two historical witness layers; they transmit the same ancient work and are not independent evidence for a Voynich interpretation. No Voynich target, reserve, or new transcript was opened. f84/f84r and the unadmitted Voynich f116v remain closed; similarly numbered leaves of other books are not those targets.

## Observed features, without merging text and figure

| Witness / exact unit | Directly inspected observation | Limit retained |
|---|---|---|
| Harley16v prose | The written explanation names centreA, morning shadowB, returning afternoon shadowC of matching length, construction intersectionD, and the meridian/northern axis with terminal lettersE/F. It proceeds to one-sixteenth division. | This is prose role ownership. It does not prove every letter is drawn or independently legible in the marginal diagram. |
| Harley16v marginal figure | An octagonal wind diagram with central radiating strokes, wind inscriptions, and outer letter/number marks. East is at the top, west below; north is left and south right in the page orientation. | A dedicated, explicitly captioned pair of shadow rays and a separate street grid are not established in this figure at supplied scale. No street figure is visible on the acquired17r. No claim about the rest of the codex. |
| Harley17r continuation | The written construction divides eight wind spaces and places lettered boundaries between named winds before mentioning street/alley divisions. | Peripheral letters and the numeral following the street-division phrase are not fully collated here. Do not silently substitute a modern or1511 numeral. |
| 1511scan29 /10r | Circle, two rays keyeda/b to morning/afternoon shadows, c keyedGnomon; north/south line and decussation mark separately labelled. | Equality belongs to the written construction; no pixel-length test was made. A gnomon stroke is not a third shadow or third wind. |
| 1511scan30 /10v | Wind-name ring, cardinal labels and multiple named subdivisions; west at page top and north at page right. | This is not the orientation of the adjacent north-up construction pages. Neither fixed book orientation nor a12-name system may be imported. |
| 1511scan31 /11r | Centre/lettered perimeter, two shadow rays keyedp/q and gnomon keyedr in the legend; named wind regions and meridian coexist. Text above supplies the construction's A–O references. | Figure legendp/q/r differs from the earliera/b/c legend and text's shadow-pointB/C. Preserve the roles and separate local keys; do not flatten them into one global alphabet. |
| 1511scan32 /11v | Eight named wind regions, intervening boundary letters and north/east/south/west orientation labels. Inner spokes and outer boundaries occupy different angular positions. | A region's name does not name each boundary ray; a blank centre is not an unnamed ninth wind. |
| 1511scan33 /12r | Rectangular building-block grid with repeated Insula, Platea and Angiportus inscriptions; the wind octagon is rotated relative to the street grid. Side legend associates corner classesa–d with pairs of winds broken there. | This is an explicit town/street diagram, not evidence that all concentric wind diagrams contain roads or buildings. |

The separate observer's [record](GK_INDEPENDENT_SOURCE_OBSERVATION.md) covers the acquired images available to that observer; it is another visual reading of the same scans, not independent historical attestation. Root alone added17r to complete the textual continuation.

## What this changes for748

The source's chain has distinct kinds of referents: a measured endpoint, a constructed axis, a wind region, a region boundary and a street direction. These cannot all be translated as wind names. A hypothetical reading preserving this chain must keep their dependencies: the two shadow observations determine the axis; the partition depends on that axis; the street choice is constrained relative to wind regions. Exchanging a region centre and boundary changes the instruction even if the circle retains the same number of strokes. A static wind list does not supply the measurement-to-axis relation.

The original source-acquisition requirement is **partly met**: an early medieval witness directly preserves the construction in prose with a wind diagram; the later1511 edition explicitly illustrates the full stages and streets. A pre1420 picture sequence showing all these roles has not been obtained. No direct exemplar relationship between the witnesses or to Voynich is asserted.

The next comparison must first establish, in a specifically admitted whole diagram, two genuinely distinct observation marks and their derived axis, or a separately owned boundary/region/street relation. An attractive circle, equal sector counts or a fitted rotation is insufficient. Do not assign a word to morning, evening, north, or street before that relation is owned. Existing1067/1081 symmetry decisions and1085/1086 ownership corrections remain unchanged; this source result does not reopen them by itself. A scored relation packet would still require the existing capacity/provenance/held-folio/mobile-null gates.

## Reproduction and limits

[GK_SOURCE_RECEIPT.json](GK_SOURCE_RECEIPT.json) records exact public image URLs, byte hashes, image dimensions and successful timestamps. `GK_FETCH_SOURCES.py --directory CACHE` reacquires just those seven external pages and verifies the received hashes; it never queries Voynich. Images themselves are not added to the repository. A hash match validates delivery, not Latin reading, date or interpretation. Provider failures and the reduced Harley sampling remain disclosed. Source observation is positive; confirmed Voynich words remain0.


## Bounded comparison with existing target observations

Root and a separate reviewer inspected the existing [GDT871 report](../../../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/REPORT.md), [f57v description](../../../../experiments/semantic_assumptions/results/f57v_ai_visual_description_pilot.md), and [f57v ownership comparison](../../../../experiments/semantic_assumptions/results/bnf_lat15171_f203_f57v_native_visual_ownership_report.md). These document radial/annular text, figures, pointed fields or angularly offset inscription registers. None documents the timed-shadow/derived-axis/street dependencies required by748. A register offset is not an observed street/wind offset. This limits what can be inferred from those existing reports; it is not a fresh visual absence test or a claim that every possible target lacks such relations.

Decision: retain the newly acquired source template; do not launch a lexical or rotation test on f67r1/f57v from these records. A later target inspection needs its own explicit scoped question and existing gates; no target opening occurred here. The distinct source-only757 remedy-timing alternative remains unselected and was not merged with this geometric chain.

Timing: source acquisition decision about14:55UTC; seven successful image deliveries14:58:58–15:01:51UTC; root/independent observations and target-primary comparison complete by15:06:46UTC. Publication preparation follows inside the30-minute checkpoint. No background continuation is claimed.
