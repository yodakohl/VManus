# Erratum to the frozen IDEA583 whole-audit plan

The original `DEFAULT_CONTEXT_WHOLE_AUDIT_PLAN_B.md` remains unchanged (SHA-256 `bb4c4a65322630e2d4b2fe7c43b50f25f3815ff437822c31cb61451dd4438886`). Its `or` InputRef bullet omitted the following `or` InputRef occurrences: ZL `.20 G001` and `.20 G004`, and IT/RF `.20 G004`. It also misstated `.24 G009` as IT/RF only. Exact frozen-lexicon/native-group replay gives the complete `or` list:

- ZL3b: `.2 G002, G003`; `.13 G001`; `.15 G004`; `.20 G001, G004`; `.22 G006`; `.24 G009`.
- IT2a: `.2 G002, G003`; `.13 G001`; `.15 G004`; `.20 G004`; `.22 G006`; `.24 G009`.
- RF1b: `.2 G002, G003`; `.13 G001`; `.15 G004`; `.20 G004`; `.22 G007`; `.24 G010`.

The complete machine-readable state/reference inventory, including these occurrences and every other exact fixed binder, reference, default control and list delimiter found in the frozen lexicon, is `DEFAULT_CONTEXT_STATE_REF_OCCURRENCES_B.tsv` (SHA-256 `5d2306141a4cf24ce87e9e34537eb9e50fb66b7de198bfdad2d1fc656f6039de`). It was built by exact literal matching over the contract's frozen lexicon and owned GDT1042 `native_groups.tsv`; no new target source or parser was used. This is a bookkeeping correction only and does not change the prior type/register qualifications or imply global UNSAT.
