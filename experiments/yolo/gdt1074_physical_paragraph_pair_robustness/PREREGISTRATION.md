# GDT1074 preregistration — physical paragraph projection and strict boundaries

GDT1073's registered all-reader gate was unscorable: RF1b has zero positive
`paragraph_start` flags among 3,768 admitted running lines, unlike ZL3b and
IT2a. GDT1073 nonetheless found pX paragraph-start fractions above yX for
all 7 supported ZL3b and all 8 supported IT2a exact bases. This follow-up
addresses that **one source metadata defect**. It does not replace GDT1073's
original decision or claim a new independent manuscript.

Freeze the **47 base strings** in GDT1073 `artifacts/PAIRS.tsv` SHA256
`114719341ea3db9afe5d2a9fd93f038dbc93c0e0b350ef28949f31c72a18f841`.
Take all 179 GDT631 text selectors in ZL3b/IT2a/RF1b; exclude f84/f84r,
f116v and reserves. Consider only raw line-initial running-prose whole groups
exactly `pX` or `yX` for a frozen base X. Require source `left_separator` =
`LINE_START` and `right_separator` in {`DEFINITE_SPACE`, `LINE_END`}; uncertain
right boundaries are retained in a separate excluded-count table, never silently
repaired. For each physical line **locus**, take a paragraph-start value only
when both ZL3b and IT2a have a running first group and their flags agree.
Assign that shared physical-line value to all three editions' eligible first
groups at the same locus. Drop unpaired or disagreeing loci for **all** readers,
not just RF1b. Source group index and reader group spelling remain unchanged.

For each frozen base/reader, report exact pX and yX line counts, paragraph
starts, distinct physical folios, excluded uncertain-boundary counts, and any
missing-line/flag exclusions. A supported base requires ≥3 eligible lines of
each form, on ≥2 physical folios per form. **Primary robustness consequence:**
at least three bases supported in **all three** editions, and pX has a strictly
higher paragraph-start fraction than yX on each such base in each edition.
Otherwise report missing capacity or a literal contradiction; do not select
only the favorable bases. Also show all supported bases within each reader.

If it passes, a cross-base position-sensitive p/y *formal* tendency remains a
serious rival for the isolated `pchor`/`ychor` whole-word contrast. If it fails,
the strong GDT1073 ZL/IT diagnostics stay descriptive but do not generalize
under this stricter contract. Either outcome changes only that structural
decision; there is no p/y semantic export, Recipe/Item confirmation, p-value or
word translation. Prior exposure and same-manuscript alternate readers are
explicit. Budget 40 wall minutes from first query through publication; no
additional repair chain after a failure.
