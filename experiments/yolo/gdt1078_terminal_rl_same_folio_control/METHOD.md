# GDT1078 method

The [preregistration](PREREGISTRATION.md) freezes GDT1077's complete
19,571-event written-adjacency file by SHA256. This control asks whether the
same-rest r/l next-initial contrast survives comparison *inside a physical
folio* rather than across pages in one section and hand. It makes no new
manuscript query or tokenization decision.

`src/run.py` groups every event by reader, full rest and physical folio. It
retains all groups, including one-sided cells. A cell is informative if both
endings occur at least twice. The fixed score is the next `{a,e,i,o}` rate
after r minus its rate after l. The primary ZL3b gate requires at least 20
informative cells on ten distinct folios, two-thirds strictly r-higher and
an equal-cell mean at least +0.05. Ties count against the sign gate. Readers
are alternative transcriptions of one manuscript.

The prespecified diagnostic splits the same events into source-group 1 and
later groups, then repeats GDT1077's rest/section/hand eligibility (≥3 of
each ending on ≥2 folios). It does not replace the folio gate. The runner
exports all folio and position cells, and `src/validate.py` independently
recalculates rosters, counts, rates and the failed registered decision.
The source data were previously exposed; no significance or meaning claim
follows from a positive descriptive mean.
