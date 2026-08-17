# GDT276 — residual channel and five-world comparison

Status: **RESIDUAL_CHANNEL_QUANTIFIED_ABBREVIATION_HEAVY_LANGUAGE_MDL_LEAD_EXPLORATORY**.

## Held-folio world comparison

| rank | world | bits | bits/group | bits/symbol | folio wins vs abbreviation | matched savings | matched p |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ABBREVIATION_HEAVY_LANGUAGE | 67620.0 | 8.0043 | 1.9824 | 0/91 | +3080.5 | 0.0154 |
| 2 | COMPRESSED_NATURAL_LANGUAGE | 70519.7 | 8.3475 | 2.0674 | 11/91 | +427.2 | 0.0154 |
| 3 | TECHNICAL_NOTATION | 75568.5 | 8.9451 | 2.2154 | 2/91 | +2297.1 | 0.0154 |
| 4 | LOCAL_CODEBOOK | 76616.8 | 9.0692 | 2.2461 | 2/91 | +0.0 | 1.0000 |
| 5 | HYBRID | 77845.2 | 9.2146 | 2.2821 | 1/91 | +666.3 | 0.0154 |

All worlds encode the same opaque PAGE_HOST target.  The selector charge is equal, so the ranking is unchanged by `log2(5)` bits.  Context models have the same 256-bucket ceiling; the page-local dictionary is prequential and begins empty on every held page.

## Residual localization

Compiler-conditioned host character form costs **67620.0 bits**.  Switching to exact compiler-conditioned PAGE_HOST identities changes this by **-7948.5 bits**.  Adding the previous exact host changes it by a further **-2276.7 bits**.  The page-local codebook costs **76616.8 bits**.

The full HPR2 tuple reconstructs raw source groups deterministically on this panel (2368 tuple types, zero ambiguous), so raw-given-host-plus-renderer residual entropy is zero by parser construction—not an empirical semantic result.

## Interpretation

The leading operational world is **ABBREVIATION_HEAVY_LANGUAGE**.  This ranks residual coding architectures; it does not identify what PAGE_HOSTs denote.  Matched-control savings show whether the particular context alignment matters beyond bucket frequency and structural opportunity.

No meaning, semantic role, language, plaintext, or translation is assigned.  All f84* source rows were rejected from raw page/locus fields before formal-column parsing; none was retained, joined, tuned on, or scored.
