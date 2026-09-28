# GDT1077 method

The [preregistration](PREREGISTRATION.md) fixes an externally nominated
next-initial contrast before the admitted source is queried. GDT915/916
compare terminal concordance in adjacent pairs; this experiment instead
holds the current group's full rest, section and hand fixed and tests the
graphic class of the **next group's initial**.

`src/run.py` uses the GDT631 179-page allowlist and `query-tsv`'s raw-selector
`f84*` guard. It retains every adjacent within-line running group pair with
literal lowercase raw forms, a definite intergroup space and a left form of
at least three letters ending in `r` or `l`. `rest` removes only this final
letter. Each event carries reader, physical line and folio, section, hand,
both full forms, next initial and fixed `{a,e,i,o}` indicator. Grouping by
reader/rest/section/hand retains sparse, tied and opposite cells. A cell is
informative with at least three of each ending on at least two physical
folios each. `r_aeio/r_n - l_aeio/l_n` is calculated without smoothing.

The registered ZL3b gate requires ten informative cells, two-thirds with
strictly positive difference and equal-cell mean difference at least 0.05.
IT2a and RF1b are alternate-reading sensitivity. `src/validate.py`
independently re-queries the guarded source, reconstructs all event keys,
stratum arithmetic, capacity and decision. No lexical spelling normalization,
phonetic value, language choice, p-value or translation is inferred.
