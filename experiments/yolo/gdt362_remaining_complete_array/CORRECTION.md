# GDT362 foldout-canvas correction

This correction was frozen after the original source-only freeze and after
direct inspection of canvas `1006250`, but before canvas `1006251` was opened
for GDT362 and before any target formal family was queried.

The original freeze incorrectly treated Yale canvas `1006250` as the complete
f101v target. The cached human catalogue states that f101v is a single foldout
design photographed in two parts: canvas `1006250` is the left part, while the
leftmost part of canvas `1006251` contains the continuation formerly called
f101v1. Its row-2 catalogue numbering is `177,178,179,180,191,192,193,194,195`.
The exact-locus comments place `.13` over the fold. Therefore the corrected
image scope is:

- `.10`-`.12`: canvas `1006250`;
- `.13`: fold-boundary target, reviewed from both canvases and allowed to be
  `UNCERTAIN` if the split or damage prevents a secure call;
- `.14`-`.18`: the f101v continuation at the left of canvas `1006251`.

The unit, nine loci, visual rubric, AQ predicate, direction, uncertainty rule,
and exact within-array null are unchanged. Inspection of canvas `1006250`
included broad and target-region crops and produced preliminary visual
impressions for the left-side targets; no visual-state TSV had been written or
frozen. Metadata and the cached-file hash for `1006251` were checked without
displaying its pixels. No target formal value and no f84 material was accessed.

This is a provenance correction, not a result or a favorable reselection.
