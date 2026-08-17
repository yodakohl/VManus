# GDT222 — fixed-module local alignment is coverage-unstable

Status: **FIXED_MODULE_LOCAL_ASSEMBLY_LEAD_COVERAGE_UNSTABLE_NO_TRANSFER_TARGET**.

The eight pre-existing candidate modules align the human top/bottom assemblies
on both f75v and f83r, unlike the complete-string representations in GDT221.
The all-row assignment leads are **1.119048** on f75v and **0.233333** on
f83r, for an aggregate **1.352381**.  The exact two-page swap tail is the
minimum available **1/4**, so this is not confirmation.

The lead is **not coverage-stable**. Restricting prose to physical lines with
complete HPR2 group coverage reduces f75v to +0.083333 and reverses f83r to
-0.133333 (aggregate -0.050000; only 1/2 pages positive). The all-row `ar`
match on f83r is supplied by `qotar` on incomplete line f83r.53; among complete
bottom-block rows, no `ar` substring remains. This is a precise dependency,
not a nuisance to hide.

The useful exploratory detail is narrower: in the all-row view, `ar` is the
only frozen module whose binary
presence distinguishes the same label/prose assembly on both pages.  On f75v
it is present in the top label and prose bags and absent from the bottom bags;
on f83r the orientation reverses, with `ar` present in the bottom label and
prose bags and absent from the top.  This rules out a simple universal
upper/lower reading while making `ar` a candidate **page-local assembly/content
address component**.  The max-eight module tail is also 1/4.  Removing `ar`
reverses the f83r lead (-0.116667); all other leave-one-module-out f83r leads
remain positive. Under complete-line coverage, however, `ar` supports neither
page: the f75 top-block `ar` rows and the f83 bottom-block `qotar` row are all
outside complete-line coverage. The result is therefore concentrated in one
module and incomplete prose rows on both pages.

The f83r label evidence is conservative: the unavailable reading-unstable
f83r.50 label is not imputed, even though its displayed forms contain `ar/ol/dal`.
The scored f83r bottom label is only f83r.51 (`darolsy`).  Its neighboring
bottom prose contains `ar` in `raly` and `qotar`, not the exact label or exact
PAGE_HOST; this is component reuse, not a recovered dictionary entry.

This nominates, but does not establish, a useful generator refinement: compact
modules may behave as local content-address material even when whole forms and
family strings fail to align. Two exposed pages, four null worlds, one
coverage-sensitive module, and missing labels are nowhere near a decoded
lexicon. The next valid test is to freeze a third independently human-defined
multi-assembly page before opening its module presence. Do not reinterpret
`ar`, `ol`, `dal`, `dar`, `sy`,
`te/tee`, or `dy` as a word, morpheme, process, object, direction, sound,
language, plaintext, or translation.  No f84 row or artifact was used.
