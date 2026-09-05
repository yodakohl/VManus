# Native image and row geometry review

Date: 2026-09-05. Reviewer: PEN_NATIVE_SOURCES.

Scope is the four already visually admitted control pages f76r, f77r, f81r
and f83r. Admission was checked in GDT791's `PAGE_SELECTOR_SPECS.tsv`.
No disputed split-block target page was opened by this reviewer, no new page
was admitted, and no sealed f84/f84r image or transcription was accessed.
No public approach search was made.

## Source acquisition and direct views

`SOURCES.json` binds each original JPEG by its SHA-256, native dimensions,
byte count, official Yale IIIF request, and canvas identity. The existing
native f81r cache was reused. The other three native files were obtained from
their official full-size IIIF endpoints. No resampling, color correction,
image synthesis or format conversion was applied to the bound files.

The reviewer opened each full native file using the image viewer before
selecting its row geometry: f81r first, then f76r and f77r, then f83r.
These were direct full-image views, with no inferred temporal order, pen
state ranking or continuation candidate comparison. No local cache path is
part of the public provenance contract; the official requests and hashes
identify the source bytes.

## Frozen control strips

The 86 rectangles in `ROWS.tsv` are interior spans of visible text rows,
selected to avoid foreground illustrations and isolated labels. They are
not an exhaustive page transcription, complete textual rows, exact baseline
traces, or examples with independently known continuous pen contact.

| Page | Native dimensions | Selected rows | Fixed horizontal range | Overall vertical range |
|---|---|---:|---|---|
| f76r | 2793 by 3769 | 27 | 559 to 2095 | 350 to 1820 |
| f77r | 2793 by 3752 | 14 | 670 to 1955 | 638 to 1439 |
| f81r | 2776 by 3737 | 27 | 611 to 1360 | 856 to 2565 |
| f83r | 2753 by 3745 | 18 | 743 to 2092 | 357 to 1819 |

Coordinates are integers in the native full image. Rectangle limits use the
usual half-open convention. `source_ordinal` and the `R` suffix enumerate
the selected rows from top to bottom on each page; neither is a manuscript
transcription line number. `row_core_y` denotes an approximate row-body
center, **not** a measured typographic baseline or a time marker.

After the direct visual review, a geometry-only horizontal occupancy
projection located dark row bodies within fixed central spans: f76r
0.20–0.75 of image width, f77r 0.24–0.70, f81r 0.22–0.49, and f83r
0.27–0.76. This used the fraction of green-channel pixels below 130 and a
nine-pixel moving average. Initial local maxima above 0.025 with 1% image
height separation included ascender/ornament peaks; a geometry draft used
maxima above 0.13 with 1.1% separation, followed by selection of visible
interior row ranges. This step was exploratory geometry acquisition,
before any continuation features or outcome comparisons.

The draft intended to avoid large paragraph openings and short final rows.
Its paragraph labels were approximate: some ordinary rows may be omitted
and an ornate opening may remain, especially on f81r. It must not be
described as a complete inventory of ordinary paragraph-interior lines.
The final instruction froze all 86 drafted row centers without further
selection or ink-based exclusion. This limitation is preferable to a
post-score geometry revision.

For each selected row, vertical half-height is the smaller of 0.007 times
native image height, rounded to an integer, and half the nearest selected
row-center separation, rounded down, minus two pixels. Bounds are clipped
to the previously selected text block. This keeps selected rectangles from
overlapping; it does not establish perfect separation of slanted strokes
or tall ascenders. Horizontal skew, bleed-through, parchment texture,
letter shape and variable foreground coverage remain possible nuisances.

The review did not inspect glyph identities, text meanings, pen-state
feature values, source/foil distances, retrieval accuracy, or any disputed
production path. Geometric continuity inside a selected row supplies only
the artificial-cut control relation. The future result must not upgrade
that relation to observed historical writing time.
