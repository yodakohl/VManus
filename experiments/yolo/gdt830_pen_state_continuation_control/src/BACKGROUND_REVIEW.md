# Independent review of the post-result background diagnostic

Date: 2026-09-05. Reviewer: PEN_NATIVE_SOURCES. This is a diagnostic review
after the registered capacity result, not a new preregistered target test.

I directly reopened the original, hash-bound native f76r image. Rectangle
`[698,3317,1955,3392]` is in the lower page margin, below the last text row:
approximately 25–70% of page width and 88–90% of page height. It contains
visually blank parchment rather than a text row or painted illustration.
Paper texture and faint marks remain visible; this is not a microscopic
certification that every pixel is free of historical ink.

I independently recalculated the unchanged registered mask and run-count
rule on this same rectangle, without importing `measure.patch_assay` or
`audit_background.py`. The original JPEG hash matched `SOURCES.json`.
Direct array arithmetic and a separate run-scanning loop reproduced:

- 94,275 rectangle pixels; 60,973 classified as foreground;
- foreground fraction **0.6467568284274728**;
- **4,233** accepted near-vertical core samples;
- median relative darkness against estimated paper **0.17124394184168018**,
  already above the registered 0.15 foreground threshold.

The max-filter background construction raises the paper estimate toward
local bright pixels. On this textured photograph, ordinary background
variation then crosses the foreground threshold over most of the rectangle.
The diagnostic demonstrates that the resulting mask and narrow-run selector
do not distinguish visible writing from background structure in this
control. The core count is therefore a count of qualifying digital patterns,
not verified pen strokes. This review does not separate parchment texture,
illumination, photographic grain, compression or faint surface marks as
the ultimate source of those patterns.

The uniform synthetic fixtures did not represent this background condition.
Their success cannot validate the real-image assay. Conversely, this failure
does **not** show that transient pen-state information is absent from the
manuscript or unrecoverable by every possible measurement. It shows that the
fixed GDT830 extraction lacks the required specificity for the intended
inference; its capacity stop must not be interpreted as a historical result.

No threshold, filter, geometry, score or source selection was changed. No
second manuscript extraction or disputed production-path test was performed.
Closing this fixed assay without a post-result rescue is warranted.
