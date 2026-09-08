# GDT880 method

## Question

Do the admitted 163 selectors contain enough immediately adjacent three-group,
same-head written-tail windows to justify a later source-bound design review?
This producer records capacity only. It does not calculate an arithmetic
predicate, compare values, infer a numeral, or assign a meaning.

## Inputs and guard

`src/SPEC.json` fixes the 163-page allowlist, source columns, excluded GDT626
physical leaves, three readings, and sealed `f84`/`f84r` prefixes. `run.py`
reads the source only through `vmanus-exp query-tsv`, naming every selector and
projecting the SPEC columns. It retains all rows and uses source-group order;
invalid or empty rows therefore remain interstitial material for adjacency.

## Candidate construction

For each ZL3b locus, every sliding window of three adjacent raw rows is tested.
All three rows must be kind `P`, literal lowercase ASCII with
`raw == clean_ascii_fragments` and one clean fragment, match
`^([a-z]+)a(i{0,3})n$` with one common nonempty head, have consecutive raw
group indices, and have `DEFINITE_SPACE` on both sides of each internal gap.
All overlapping ZL windows are retained. IT2a and RF1b are joined only when
the exact three raw strings form a unique eligible window at the same locus.
No arithmetic equality or head selection by values is computed.

`SOURCE_ROWS.json` retains every projected row at candidate loci in all three
readings, including negative/interstitial rows. `CANDIDATES.json` records raw
groups, minim runs, heads, source indices, edition joins, and consensus status.

## Decision and claim ceiling

At least 20 consensus source lines on 5 physical leaves with 2 heads permits
`DESIGN_REVIEW_CAPACITY_ONLY`; otherwise the immediate-triple endpoint stops.
Either result is capacity triage only. It does not support arithmetic,
equality, ordinal/cardinal interpretation, translation, or an authorial claim.
