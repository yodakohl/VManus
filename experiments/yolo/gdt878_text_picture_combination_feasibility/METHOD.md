# GDT878 method

## Question

Do the fixed text anchors and admitted native drawings contain a new
object/relation configuration plus a second recurring text variation, or do
they provide only a structural feasibility lead? This is discovery work. It
does not test a translation, glyph value, or model meaning.

## Inputs

Root supplies `artifacts/SOURCES.json`, `ROOT_OBSERVATION.json`, and
`GEOMETRY_B_OBSERVATION.json`. Each packet has `schema_version`, `branch`
(or the frozen observer label), source binding fields, a scope, observations
(or the frozen geometry `medallions` list), and a decision. Root's
packet enumerates `f69v.14`, `.18`, `.27`, `f72r2.9`, `.10`, `.11`, and `.18`,
including unavailable or uncertain anchors. Geometry B records each inspected
f67r2 medallion with locator, bounded-contour state, coarse fraction when
distinguishable, nearby-writing attachment, and uncertainty, plus its capacity
decision. The two packets remain separate evidence branches.

## Method

`run.py` hashes the fixed protocol files, checks packet filenames and source
manifest, and packages the packets with the fixed anchor scope. It performs no
image processing and reads no TSV. `validate.py` independently recomputes
protocol hashes, checks packet/source binding and anchor coverage, preserves
negative/uncertain outcomes, and rejects semantic or statistical verdict
fields. It cannot validate whether a visual observation is true.

The root packet uses only the admitted f69v shared original and f72r2 regional
source. Geometry B uses only the admitted f67r2 original. No excluded parent
region, f72r1, f84, or f84r may enter. Image bytes remain local runtime input.

## Decision rule and claim ceiling

Each branch may report `PERMITS_FUTURE_TEST`, `CLOSES_CONCRETE_ENTRY`, or
`DEFERS_UNCERTAIN_VISIBILITY`. Geometry requires at least three clearly
distinct bounded fraction states and independently reusable writing or other
redundant encoding before it can permit a future test. No outcome supplies a
translation, semantic label, phonetic unit, instrument function, p-value,
directed inscription edge, or independent confirmation.
