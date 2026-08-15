# GDT133 — raw-surface transfer decomposition

Status: **RAW_CONTROL_POSTHOC_RESIDUAL_SURFACE_LEAD_ONLY**

This is a post-hoc decomposition of the exposed corrected GDT132 panel, not a replication. All tried variants are logged.

| representation | gain bits | positive folios | top-1 | top-3 | local p | max-6 p |
|---|---:|---:|---:|---:|---:|---:|
| `RAW_CHAR3` | +1.293 | 12/24 | 24/31 | 28/31 | 0.0273 | 0.0273 |
| `COMPILER12` | +0.752 | 10/24 | 24/31 | 28/31 | 0.1855 | 0.1867 |
| `EDGE29` | -0.465 | 9/24 | 24/31 | 27/31 | 0.3673 | 1.0000 |
| `FACTORED_PLUS_RAW` | -2.861 | 10/24 | 23/31 | 27/31 | 0.0564 | 1.0000 |
| `HOST_CHAR3` | -4.153 | 11/24 | 23/31 | 27/31 | 0.4772 | 1.0000 |
| `FACTORED` | -4.245 | 8/24 | 23/31 | 27/31 | 0.3490 | 1.0000 |

The largest fixed decomposition remains raw token trigrams at +1.293 bits (max-six p=0.0273), but top-1 is unchanged and only 12/24 folios are positive. COMPILER12 is +0.752 bits with no corrected lead; FACTORED minus HOST is -0.092; adding RAW after FACTORED is +1.384, yet FACTORED_PLUS_RAW remains negative overall. The exposed trace therefore localizes only to uninterpreted residual source-string texture, not to an HPR2 compiler or PAGE_HOST edge layer. Its p-value is coarse, post-hoc, and not opportunity-length matched.

No heading, recipe, transferable record semantics, content-bearing layer, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. Limited f84 audit exposure remains disclosed; all final GDT133 inputs are f84-free and no further f84 access occurred.
