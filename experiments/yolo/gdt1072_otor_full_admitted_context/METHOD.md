# GDT1072 method

The fixed decision and budget are in [PREREGISTRATION.md](PREREGISTRATION.md).
This is a descriptive, previously exposed-data census, not a new decoder.

The runner reads GDT631's frozen 179-selector allowlist (SHA256
`f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`)
and calls `vmanus-exp query-tsv` on the existing source separator table (SHA256
`4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`)
with raw `page` selector, each allow value, explicit output columns and
`--forbid-prefix f84`. A separate raw `locus` selector admits only f68r1.1 and
f68r1.26, already exposed in GDT791. The guarded tool discards forbidden rows
before materializing other fields. After admission, exact raw whole groups
equal to `otor` are retained; no normalization or substring matching occurs.
The complete 105-row result is `artifacts/EXACT_OCCURRENCES.tsv`.

The validator independently calls the preexisting `vmanus-work words profile`
for the 179-selector corpus and compares per-reader count, section, kind and
page count; it also verifies literal exactness, special-locus scope and absence
of f84. Its 40-locus count groups alternate readings by source locus, not by
group index (which may shift between editions). The three transcriptions are
alternatives of one manuscript, never three independent witnesses. Physical
line positions do not by themselves disclose referents or sentence boundaries.

The previously inspected 2026-08-21 workshop microtheory, GDT1071, and source
scope are dependencies. f68r1's one star attachment is grounded in the human
annotation quoted by GDT1071, while the same-page prose owner remains only the
page. The extra `otor` local loci on f88r, f89v1 and f99v have hedged or merely
proximity-based annotations, so they are not promoted to distinct pictured
object identities. No significance, star name, morphological rule or English
word is established.
