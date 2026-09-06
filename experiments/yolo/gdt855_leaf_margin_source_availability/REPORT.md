# GDT855 — three residual physical folios in the admitted metadata

**Six pages on f35,f36,f37 remain after excluding all60previously judged
LM001/LM001X/LM001Y physical folios.** These are metadata candidates for
possible new leaf-margin observations; no image was opened and no visual
state or page admission was produced. All six pages belong to ANN quire q05.

## Every remaining page

| Page | Physical folio | Currier | Section | Hand | ANN quire | ZL quire | Source tags |
|---|---|---|---|---|---|---|---|
| f35r | f35 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |
| f35v | f35 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |
| f36r | f36 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |
| f36v | f36 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |
| f37r | f37 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |
| f37v | f37 | A | H | 1 | q05 | E | SOURCE_HERBAL_PAGE;TEXT_PARAGRAPHS |

The registered join uses ANN quire q05 when present and retains ZL code E
separately; it does not infer an additional independently observed quire.
Both sides of one physical folio remain listed, not treated as separate
physical witnesses or automatically sampled down to one side.

## Complete exposure subtraction

- Historical batches: LM00132, LM001X19, LM001Y9, each unique and mutually disjoint.
- Total previously judged physical folios:60, including LM00116calibration folios.
- Current scope:179selectors; eligible herbal A/B pool118pages on61physical folios.
- Old exposure intersecting the current eligible pool:58physical folios.
- Old exposure outside that pool: f1 and f57. They remain excluded.
- Remainder:6pages on3physical folios; no ANN duplicate-page inconsistency.

This is61minus58within the current pool, not61minus60. Old selected pages
f31v,f90v1,f57r,f1v,f54r lie outside the current179selector list. The audit
nevertheless retained their physical-folio exposure. An opposite side or
panel cannot become fresh data by changing the selected page label.

LM002's44does not include the16LM001calibration folios. GDT363 reused
that same44panel without new image observations. Neither44count replaces
the full60-folio exclusion. No LM002 formal target or broad feature atlas
was inspected or scored.

## Why the remainder needs a careful interpretation

The historical LM001Y selector explicitly excluded q05. That source-code
boundary was already visible before this query. GDT855 measures its present
residual availability; it does not claim that q05 was previously unknown,
that these pages were never seen anywhere in the project, or that new visual
evidence has already been acquired. They are outside the three registered
LM exposure panels under the complete physical-folio subtraction.

Any later leaf-margin acquisition would need a separate protocol respecting
existing visual scope and the closed route requirements. No image selection,
leaf scoring, association test, formal-target access, calibration reuse or
automatic page admission follows from this metadata result. The experiment
ends with the complete concrete candidate list rather than reopening a fit.

## Guarded metadata provenance

| Projection | Selected rows | Forbidden-selector rows skipped | Other selectors skipped |
|---|---:|---:|---:|
| ANN | 179 | 2 | 47 |
| ZL | 4137 | 98 | 1150 |
| LM001 | 32 | 0 | 0 |
| LM001X | 19 | 0 | 0 |
| LM001Y | 9 | 0 | 0 |

ANN projected only page/source_tags/quire; ZL projected only
page/language/section/hand/quire. Historical selections projected only
page/physical_folio. Explicit selector allow-values and both sealed-prefix
exclusions preceded payload materialization. No text, glyph, leaf outcome
or image fields were requested. The protected LM002 state table was neither
opened nor hashed. Binding uses safe projection hashes, not restricted
whole-table contents.

Public registration fdb7e563 preceded all five queries. Independent validation
reconstructed the first-ZL-row metadata join, ANN uniqueness, every historical
exposure set and exact subtraction. Cached replay was byte-identical;
source/projection/result binding passed. The five queries plus validation
and replay completed in approximately0.3seconds. All outputs are metadata
only; zero new visual judgments or semantic claims.

## Post-count acquisition decision

A separate [post-count proof](POST_COUNT_FEASIBILITY.md), developed after this
metadata result, shows why this reserve cannot improve LM002 mobility while
retaining the old panel and rules. With t new TOOTHED folios, q05 contributes
(3+t)/(13+t), exceeding25% for every t>=1. With t=0, a new acquisition phase
has no TOOTHED state and hence no mixed conditional cell. All27hypothetical
leaf-state assignments were checked by src/post_count_feasibility.py; an
independent reviewer checked the algebra. No new image or formal-target access.
The registered metadata status is unchanged; the auxiliary result closes only
this prospective extension, not every research use of the three folios.
