# GDT1065 — no opening-H1 to internal-H4 same-body pair

The fixed 13 complete f77r/f82r/f83r records contain **four** ordered H1→H4
pairs with an identical GDT735 rest body, but **zero** meet the predeclared
condition that H1 opens the physical record. No candidate reaches the
meaning test; no word is translated.

The guarded GDT791 occurrence spine contributes 940 running-prose tokens in
13 records. Eighty-eight are exact members of the fixed 96-form, 24-body
GDT735 grid. The complete ordered-pair result is:

| Record | H1+body | H4+same body | Position result |
|---|---|---|---|
| f77r P2 | `pchedy` at .36 token 2 | `lchedy` at .37 token 7 | H1 is record token 79, not opener; one pair. |
| f82r P3 | `pchedy` at .27 token 1 | `lchedy` at .29 tokens 3 and 5, .31 token 4 | H1 is record token 67, not opener; three pairs. |

The actual record openers are `otedy` at f77r.25 and `posalshy` at f82r.20.
All four H4 tokens are line-internal. The complete intervening surface lists,
including uncertain-looking but unaltered forms, and the nine records with
zero ordered pairs are in [RESULT.json](artifacts/RESULT.json). A line-start
H1 inside P3 is not retrospectively promoted to a new record opener.

The [fixed decision note](../../../research_registry/decisions/idea643_same_record_capacity_20260928.md)
preceded the first join; the experiment package followed an initial diagnostic,
as [the chronology](PREREGISTRATION.md) states. The packaged run checks both
input hashes and every record, and the independent validator reconstructs
all four pairs from GDT790's separately structured 123-line artifact. It
passes. No mixed raw TSV, new page, image, source or decoder was opened.

Decision: **ZERO_STRICT_CAPACITY_NO_MEANING_TEST** for IDEA643 on these 13
deep-page records. The four relaxed pairs show literal recurrence, not item
identity or a later property. The old [GDT737](../gdt737_held_body_record_role_transfer/REPORT.md)
counterexample still defeats a general H1/H4 body-affinity rule. The remaining
admitted pages were not silently searched or treated as an independent
holdout. An independently mapped new physical record and a separately bound
property would be necessary before a different fixed test. Zero confirmed
Voynich words.
