# GDT879 method

## Question

Can the three fixed single-plant pages supply a reproducible intrinsic
attachment graph that could later serve as a source-bound endpoint for a
whole-page text prediction? This pass does not read text or infer a meaning.

## Inputs

`artifacts/SOURCES.json` binds the three admitted originals. Root and observer B
each provide one JSON packet with an observer identity and exactly the three
pages `f4r`, `f10r`, and `f13r`; the packet may encode those pages as a `pages`
list or as the frozen B `observations` mapping. Every page has an optional
`terminal_count` interval, a terminal-locator list of `{id,
center:[x,y]}`, boolean
`basal_hub_clear` and `hierarchy_clear`, `edges` of
`{parent, children:[...]}`, and `notes`. Count intervals and uncertainty are
preserved; no node IDs are matched across observers.

## Method

`run.py` verifies source bytes and dimensions and, when both native packets are
present, packages their exact JSON bytes with the frozen protocol hash.
`validate.py` independently verifies source bindings, exact page coverage,
terminal-locator shape, count-interval consistency where the count is exact,
nonempty local edge labels, and explicit result adjudication. It does not
match junction or terminal IDs across observers.
It does not adjudicate visual correspondence or reproduce native vision.

The only allowed pages are f4r/Yale1006082, f10r/Yale1006094, and
f13r/Yale1006098. The graph rubric excludes text, OCR, color, species, angle,
stroke width, and detailed margins. Approximate centers are locators only.

## Decision rule and claim ceiling

Only an explicit root-owned `RESULT.json` may decide `PROCEED_DESIGN_REVIEW`,
`STOP_UNSTABLE_ENDPOINT`, or `DEFER_UNCERTAIN_SOURCE`. A proceed decision must
explicitly name at least two pages with exact terminal-count agreement,
compatible rooted attachment relations, and a topology difference beyond global
size/position. The validator checks those declared predicates; it does not
compute observer correspondence or invent a decision. No outcome translates
text, establishes a semantic endpoint, or confirms text-picture alignment.
