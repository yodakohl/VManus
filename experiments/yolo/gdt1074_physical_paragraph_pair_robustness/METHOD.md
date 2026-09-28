# GDT1074 method

The [preregistration](PREREGISTRATION.md) freezes the 47 GDT1073 pair bases,
the source-bound paragraph projection, strict separators, capacity and gate.
The runner checks the frozen GDT1073 pair-table hash, reads the GDT631 179
allowed selectors through `vmanus-exp query-tsv` with `--forbid-prefix f84`,
and identifies every line-initial running-prose group matching a frozen pX/yX
whole. It constructs a paragraph-start flag per physical line locus only where
ZL3b and IT2a both have a running first group with equal flags. The flag is
then assigned to eligible exact groups in all three transcriptions; no group
is respelled, realigned by token ordinal, or merged. It requires literal
`LINE_START` at left and `DEFINITE_SPACE` or `LINE_END` at right, retaining all
excluded rows with reasons in `artifacts/EVENTS.tsv`.

`artifacts/PAIRS.tsv` contains every frozen pair and reader, including zeros
and low support. The validator independently recalculates every event count,
support and direction and reconstructs 3,715 physical-line consensus flags
from a fresh selector-guarded query. Its result is not a second witness: all
three readers transcribe the same manuscript, and projected paragraph flags
are borrowed from ZL3b/IT2a. The test repairs one metadata asymmetry only;
GDT1073's original unscorable all-reader gate remains unscorable as run.

No matched section/hand nuisance control, corpus-wide multiple-search null,
prefix semantics, English translation or source referent is claimed. The
positive decision concerns a narrowly defined formal direction under this
fixed source projection.
