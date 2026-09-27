# GDT1047: paragraph host capacity of daiin, aiin and the d/minim family

The universal paragraph-local overt-host rule fails for the whole formal
`dan / dain / daiin / daiiin` family in both paragraph-annotated readings.
Exact `aiin` retains left-host capacity in both, but violates the right-host
condition. Exact `daiin` is boundary-sensitive: ZL3b has no left contradiction;
IT2a has two. The first word agrees at both sites; the paragraph flags differ.
These are necessary-condition results, not identified hosts or translations.

## Fixed predictions and complete result

LEFT requires a noninventory written group to the left of every maximal
inventory run in the same source-marked paragraph. RIGHT requires one to its
right. Repeated inventory members cannot supply each other's hosts. Zero
available groups at an explicitly marked boundary contradicts the fixed rule;
an unmarked fragment edge is UNKNOWN. CAPACITY means only that a group exists,
not that it has the required semantic type. No candidate was selected by score.

C/X/U below mean CAPACITY / CONTRADICTION / UNKNOWN, counted by maximal run.

| Exact inventory | Reading | LEFT C/X/U | RIGHT C/X/U | Decision |
|---|---|---:|---:|---|
| FAMILY | ZL3b | 901 / 2 / 0 | 872 / 30 / 1 | Both fixed directions contradicted |
| FAMILY | IT2a | 913 / 4 / 0 | 885 / 31 / 1 | Both fixed directions contradicted |
| FAMILY | RF1b | 777 / 0 / 0 | 765 / 0 / 12 | No source-marked paragraph capacity |
| DAIIN | ZL3b | 705 / 0 / 0 | 680 / 25 / 0 | LEFT compatible only; RIGHT contradicted |
| DAIIN | IT2a | 719 / 2 / 0 | 695 / 26 / 0 | Both fixed directions contradicted |
| DAIIN | RF1b | 608 / 0 / 0 | 598 / 0 / 10 | No source-marked paragraph capacity |
| AIIN | ZL3b | 422 / 0 / 0 | 418 / 4 / 0 | LEFT compatible only; RIGHT contradicted |
| AIIN | IT2a | 389 / 0 / 0 | 386 / 3 / 0 | LEFT compatible only; RIGHT contradicted |
| AIIN | RF1b | 436 / 0 / 0 | 435 / 0 / 1 | No source-marked paragraph capacity |

RF1b has zero explicit paragraph starts and ends in this input. Its raw counts
are fragment diagnostics, not paragraph evidence; even its internal CAPACITY
entries do not establish the paid paragraph scope. It cannot be counted as a
third confirmation. ZL3b has703 reconstructed blocks,665 explicit starts/ends;
IT2a has734 blocks,697 explicit starts/ends; RF1b has240 unmarked fragments.

## Every left-boundary contradiction

| Reading | Inventory | Locus | Exact beginning | Source consequence |
|---|---|---|---|---|
| ZL3b and IT2a | FAMILY | f108r.45 | dain sheckhy okeey keey lchedy | dain has no overt left host in the marked paragraph45–47 |
| ZL3b and IT2a | FAMILY | f111r.6 | dain shedy qoky chedy qok shed | dain has no overt left host in the marked paragraph6–35 |
| IT2a | FAMILY and DAIIN | f28v.6 | daiin chkaiin | Complete two-group marked paragraph |
| IT2a | FAMILY and DAIIN | f58v.30 | daiin sheoikhy ykey sheky qokal | Marked paragraph30–33 starts with daiin |

The two additional IT2a sites have the same initial `daiin` spelling in ZL3b.
Only their start-marker contract changes the left verdict. No visual boundary
verification was performed; no reading was preferred after seeing the result.
Every right contradiction and every full paragraph containing any contradiction
is retained in BLOCKS.json; RUNS.json includes every tested occurrence run.
There are74 unique contradiction blocks and5878 total runs across the three
overlapping inventories and three readings, not5878 independent observations.

## Scope and changed inputs

The test uses179 current admitted selectors, without new admissions or images.
Guarded selection retained96184 source groups. P prose groups number31918 ZL,
31433 IT and31504 RF; other C/L kinds are counted separately in RESULT.json.
The guarded command, selected columns, rejection counts and projection hash
are recorded there. f84/f84r were rejected from raw selector fields before
materializing row contents; f116v and reserves were not admitted.

The earlier GDT81239-selector study is not a subset of this allowlist. A
metadata-only assertion detected this before the first raw extraction. The
separately locked pre-data addendum corrected the comparison to27 overlapping
selectors plus152 others, and lists the12 old selectors not opened here.
The original preregistration and lock are preserved. No old selector was
silently remapped. Raw representation also differs from the earlier cleaned
analysis, so this is not a pure sample-size comparison.

| Inventory | Reading | Stratum | Occurrences | Runs | LEFT X | RIGHT X |
|---|---|---|---:|---:|---:|---:|
| FAMILY | ZL3b | old_overlap27 | 146 | 143 | 0 | 6 |
| FAMILY | ZL3b | additional152 | 791 | 760 | 2 | 24 |
| FAMILY | IT2a | old_overlap27 | 152 | 149 | 0 | 6 |
| FAMILY | IT2a | additional152 | 801 | 768 | 4 | 25 |
| FAMILY | RF1b | old_overlap27 | 126 | 124 | 0 | 0 |
| FAMILY | RF1b | additional152 | 677 | 653 | 0 | 0 |
| DAIIN | ZL3b | old_overlap27 | 106 | 104 | 0 | 6 |
| DAIIN | ZL3b | additional152 | 609 | 601 | 0 | 19 |
| DAIIN | IT2a | old_overlap27 | 113 | 111 | 0 | 6 |
| DAIIN | IT2a | additional152 | 624 | 610 | 2 | 20 |
| DAIIN | RF1b | old_overlap27 | 93 | 92 | 0 | 0 |
| DAIIN | RF1b | additional152 | 522 | 516 | 0 | 0 |
| AIIN | ZL3b | old_overlap27 | 41 | 41 | 0 | 0 |
| AIIN | ZL3b | additional152 | 381 | 381 | 0 | 4 |
| AIIN | IT2a | old_overlap27 | 32 | 32 | 0 | 0 |
| AIIN | IT2a | additional152 | 357 | 357 | 0 | 3 |
| AIIN | RF1b | old_overlap27 | 47 | 47 | 0 | 0 |
| AIIN | RF1b | additional152 | 389 | 389 | 0 | 0 |

All left contradictions occur among the152 additional selectors. This changes
the necessary-condition evidence beyond the overlapping old scope, without
altering GDT812's original result. Prior project exposure applies throughout.
No selection/confirmation split or independent meaning capacity is claimed.

## What changes, and what remains ambiguous

Do not use the whole formal family as an exceptionless paragraph-local
postmodifier on the strength of the old limited absence at paragraph starts.
Both directions of that particular family rule are contradicted. For `daiin`
the same left rule is conditional on unresolved paragraph annotation. For
`aiin`, left-host capacity remains a permissible requirement for a future
explicit reading; capacity alone does not establish dependence or its meaning.

Numbers, qualities, nouns, references, linkers and writing conventions remain
unseparated by this test. No universal part-of-speech exclusion follows.
Implicit hosts, different scope or polysemy would be different models, not
excuses that rescue this registered one. The existing family/repetition facts,
GDT802's retired neighbour lead, GDT749's calibration limit and all older
semantic contradictions remain unchanged. Confirmed translated words:0.
No significance, chance probability or semantic confirmation is claimed.

## Reproduction and validation

Run `python3 experiments/yolo/gdt1047_bare_value_left_host/src/run.py --fetch`
to regenerate the selector-first projection and artifacts from the bound local
source; use `--check` to compare the retained artifacts. The runtime projection
is ignored, not published. The bound source and admission files already exist
in the repository. No OCR or external data acquisition is needed.

An independent validator, written without reading/importing the runner,
replayed the guard and independently reconstructed all1677 blocks,5878 runs,
18 stratum cells,18 directional decisions and74 full counterexample blocks.
It also passed12 synthetic/mutation checks, including missing/changed evidence
and paragraph flags. `src/validate.py --check` verifies its retained report.
This PASS verifies accounting and execution, not historical semantics.

Registration15:13:39UTC, corrected metadata lock15:19:27UTC, evaluation and
validation completed within the45-minute branch budget. The ten-hour parent
research block remains active; completing this test does not complete it.
