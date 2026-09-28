# GDT1073 method

The fixed question, cohort, capacity threshold, and decision rule are in
[PREREGISTRATION.md](PREREGISTRATION.md). This is one guarded query on the
already admitted GDT631 179-selector corpus. The raw page selector is checked
against 179 explicit allow values and `f84` is forbidden before content
materialization. The output columns are only edition, page, locus, source kind,
group position, paragraph-start metadata, and raw group. The runner enumerates
all exact lowercase ASCII `pX`/`yX` pairs with shared suffix length ≥3 among
line-initial running-prose groups and writes every pair/reader result to
`artifacts/PAIRS.tsv`. A physical folio is the number part of `fNNr/v`;
different panels or sides of the same leaf are not independent folios.

The validator recalculates support and direction for all 141 pair-reader rows,
and independently queries paragraph-start metadata for **every** admitted
running line. This exposed a source-channel asymmetry: RF1b has 3,768 running
line starts but zero positive paragraph-start marks, whereas ZL3b and IT2a
have 665 and 697. A zero in RF1b is thus missing metadata for this decision,
not a legitimate zero-start observation or a scientific counterexample. The
first runner's literal `DIRECTION_NOT_UNIVERSAL` is retained in `RESULT.json`
as the raw mechanical output; the review decision is **unscorable under the
registered all-reader gate**. ZL3b and IT2a values are descriptive diagnostics
from alternate transcriptions of one manuscript, not an independent holdout.

The runner uses raw source groups, not GDT756's selected 13-line cache. A
subsequent bounded source query showed ZL3b f44r.4 is an additional exact,
definitely separated line-initial `ychor` (14 total in the full 179 selectors),
also not paragraph-initial. This changes the full-corpus denominator, not the
old GDT756 cache result. No prefix meaning or word translation is exported.
