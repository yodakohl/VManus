# GDT1061 method

The [preregistration](PREREGISTRATION.md) fixed six publicly quoted `Raw EVA`
strings and the matching criteria before opening f56r/f77r content. f88r had
already been inspected exploratorily. Public source: ZFD `CASE_STUDIES.md`,
commit `3f030a9293b8db15dc2c7b0d0e7c703e71711f62`, SHA-256 recorded in
the preregistration. `src/claims.tsv` is the complete fixed six-string input.

`src/run.py` invokes `./vmanus-exp query-tsv` twice with explicit page selector
allow-values f56r/f77r/f88r and explicit output columns. The cross-reader line
source supplies ZL3b, IT2a and RF1b; the ZL3b metadata source identifies P
prose loci. The guarded reader excludes f84* before it materializes other row
fields. The report counts all P loci of each page, and the secondary all-kind
diagnostic checks labels as well. Dots in the six source strings become group
spaces; no characters or boundaries in Voynich source strings change. Exact
whole-line, within-line contiguous span and span crossing one *numerically*
adjacent P-line boundary are recorded. Every source claim is evaluated in all
three alternate readings of one manuscript. `kostain` is checked as a whole
group on the two pages on which the public examples place it.

`src/validate.py` independently pins the public Markdown bytes by SHA-256,
checks the six quote strings occur in those bytes, and checks the result
matrix and summary counts. Reproduce from repository root with the run and
validate commands in `experiment.json`. No manuscript image was opened, and
no held leaf or reserve was used. This is a source-input audit, not a
translation test or an independent confirmation experiment.
