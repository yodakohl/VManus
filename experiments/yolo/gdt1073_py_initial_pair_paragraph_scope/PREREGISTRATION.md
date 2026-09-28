# GDT1073 preregistration — `p…`/`y…` paragraph scope

Registered before enumerating the target pairs in the complete admitted
corpus. GDT756/757: exact `pchor` and `ychor` are both conspicuous line-initial
but contrast in paragraph starts (6/7 vs 0/13). GDT914's local repeated
single-edit test was negative; it did **not** ask whether the initial-letter
contrast transfers as a paragraph-scope tendency across complete forms.
The known counterexample is that p/y can be merely whole-form identity or a
layout-conditioned spelling difference. This audit tests **structure**, not
whether a letter literally means Recipe or Item.

Use exactly GDT631's 179 admitted text selectors, all three alternative
readings, raw groups and source-bound `kind=P`, `source_group_index=1`, and
`paragraph_start`. Only complete lowercase ASCII groups of the pattern
`pX`/`yX` with identical `X` of length at least three are paired. No edit
distance beyond the first position, no `q` or inserted letter, no segmentation
repair. Include every eligible pair and every line-initial occurrence, including
zero paragraph starts. Define a supported base in a reader as at least three
line-initial occurrences of **each** form on at least two distinct physical
folios for each form. ZL3b is the primary counting reader; IT2a and RF1b
are boundary-sensitivity audits, not replications.

The primary consequence is whether at least **three supported bases** in
ZL3b have a higher paragraph-start fraction for pX than yX, with the same
direction for those bases wherever supported in IT2a/RF1b. If there are fewer
than three, stop for missing generalization capacity. If three exist but any
contradicts, reject a universal p/y paragraph-opening tendency. A positive
trend changes only the structural interpretation of `pchor`/`ychor`: their
contrast may instantiate a wider positional renderer, weakening a direct
Recipe/Item **whole-word** identification. A negative or capacity failure
leaves the two whole-form working glosses independent and unconfirmed.

Report raw counts and physical-folio coverage for every pair and reader,
including low-support pairs; no selected examples, p-value, significance,
prefix-meaning export or confirmed translation. Preexisting exposed data only;
f84/f84r, f116v and reserves stay closed. Smallest adequate implementation:
one selector-guarded group query, exact pair enumeration and an independent
recount. Budget 45 minutes from the first complete query, including build,
validation, decision and publication. No downstream decoder work.
