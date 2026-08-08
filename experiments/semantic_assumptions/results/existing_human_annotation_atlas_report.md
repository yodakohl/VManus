# Existing human-annotation atlas

Decision: **PASS_EXISTING_HUMAN_ANNOTATION_REUSE_SCOPED**.

Creating a new 47-page annotation set before using the public metadata was unnecessary. Existing human work supplies manuscript-wide editorial locus roles, a near-complete page catalogue, page-level text-layout descriptions, and useful but incomplete label/comment layers.

| human source layer | coverage | admissible use |
|---|---:|---|
| voynich.nu categorized folio prose | 226/227 exact active page IDs | page type, illustration description, and text-layout assertions |
| current IVTFF metadata | 5385 loci on 227 pages | complete editorial P/L/C/R locus role; ZL3b and RF1b codes match at every locus |
| Stolfi 25e1 exact comments | 1099 object-bearing plus 93 label-only regex-indexed loci on 78 pages | exact or unit-scoped source comments with hedging retained; absence is unknown |
| Stolfi 1998 best label/title index | 1018 legacy records on 79 source page IDs | described subset with human class/guess/attributes; not the current complete label inventory |

Text-layout prose is present for **226** catalogue records; the older local inventory had accidentally omitted this entire named source field.

Of **398** unhedged exact-local relation rows, **317** use proximity language and only **109** contain a stronger attachment, enclosure, contact, wrap, or grouping assertion; these tag counts overlap. They remain source assertions, not automatic ownership truth.

The current metadata has **1029** `L` loci. The older Stolfi file's **1018** records are a different labels-plus-proposed-titles inventory (including **43** title guesses), so the totals must not be subtracted or treated as one-to-one coverage. Legacy page IDs `f101v1, f101v2, f86r4` remain explicitly flagged.

Live verification: **not all sources were live-verified**.

The sole active page ID without a literal catalogue counterpart is `fRos`; the catalogue describes the compound 85/86 foldout through its component/wrapper entries, so that mapping must be explicit rather than silently duplicated.

This atlas replaces new labeling only as the immediate source-gathering action. It does not provide complete paragraph-to-object ownership; missing ownership remains unknown because the user has ruled out a new manual pass. Modern descriptions are not authorial meanings.

No manuscript image, OCR, automated vision, excluded old-scan coordinate, grammar feature, or semantic score was used.
