# Independent replay review B

I rebuilt the checks from the hash-bound GDT1045 473-row projection, the
unchanged parent S/E dictionaries, and the GDT1046 frozen SPEC. I did not read
or import `src/run.py`. The independent validator verifies every registered
input hash before comparing any result tables.

The replay matches all 81 E groups: 27 per reader, with 8/7/7 occurrences
covered by the inherited 24 S plus 6 E values, leaving 19/20/20 E groups
unassigned. The author's full E inventory matches the literal source rows and
retains unparsed groups. This is not a complete E reading; the coverage counts
do not add meanings or turn opaque groups into omissions from the source.

All 16 exact standalone `ar` cases match the projection with their same-line
neighbors and separators (4/6/6 by reader). The two adjacent pairs are exactly
IT2a and RF1b at `.24`; the ZL pair set is empty. Under the fixed
`ProcessFrame → FacultySpec` nominalization, granting an immediately preceding
ProcessFrame conditionally licenses the first `ar`, whose result is a
FacultySpec. The immediately following `ar` requires a ProcessFrame, so that
second application has a domain mismatch. RF retains an uncertain-small-space
boundary after the second `ar`; IT's corresponding boundary is definite. This
rejects the adjacent sequence under these exact two reductions, not under all
possible grammars. The unresolved line-initial cases do not establish a frame
across a line boundary.

The `.24` native packet preserves 44 exact group records and 13 alignment
units; every literal source group is referenced exactly once, including
multi-group alignment units. Both observer records are hash-bound and retain
uncertainty. They share the same previously admitted pixels and knew the
comparison, so their agreement is not independent visual or semantic
confirmation. No unique `aram` versus `ar`/`am` grouping is established.

The validator reproduces `RESULT.json`. Its ceiling is literal source
completeness, unchanged parent membership, and conditional type application.
It does not establish any target meaning, a complete E parse, or proof that
ZL's whole-E account is impossible. Confirmed meanings remain zero.
