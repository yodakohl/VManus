# GDT1366 — Joint terminal capacity after alphabet saturation

## Decision note and scope

GDT1365 already excludes FULL for both fixed source tables. Its GE2 restricted18
mixed-direction count passes only a necessary diversity test. This new test asks
whether the joint per-word terminal constraint also fails there. It does not
reopen FULL, replace its result, or select a replacement source or spelling.
Selection follows exposed1365 results; no holdout or confirmatory claim.
Budget25minutes including preparation, implementation, independent validation
and publication. Smallest adequate test: a proof plus census of occurrences of
the forced terminal-only character set. Failure closes the GE2 mixed-direction
capacity survivor; no violations would leave only necessary capacity, not fit.
No decoder or broader corpus work follows automatically.

## Proof and frozen test

Inherit1365restricted18source classes, exactly3 terminal-only and15other classes,
one fixed RAW_CHAR per class, arbitrary whole-source-word reversal, preserved
source boundaries and optional additional splits. A native group is a substring
of one encoded source word, never a concatenation across source boundaries.
No erasure of emitted classes, aliases, variable-width rendering or inserted
controls. Distinct source classes may merge in the model, but if the observed
panel uses18distinct characters, its18-class function is necessarily bijective.
If exactly15characters appear in strict word interiors, the other3 must be
images of the3terminal-only classes. Every source word has at mostONE total
occurrence of those classes, regardless of direction. Splitting cannot increase
that count within a group. Thus every native group must contain at mostONE
occurrence from the forced3character set, counting repeats as well as distinct
members. A single violating group falsifies this conjunction.

Use each reader's unchanged1233cache/631allowlist and1365GE2selection: exact raw
whole forms on >=2 physical leaves, no pooling readers. Recompute alphabet and
strict-middle set, assert18/15; derive terminal candidates by set difference,
not hard-coded native letters. If cardinality premises fail, stop UNAPPLICABLE;
do not seek a convenient substitute set. Enumerate every GE2group with >=2total
candidate occurrences. Save complete cached source row, raw offsets, totalcount;
summarize groups/types/physical leaves, violation occurrence rate, counts by
terminal-character string, and top10violating forms ordered (-frequency,form).
These summaries are descriptive, not p-values or independent confirmations.

FULL failure is retained without a new FULL score. Extended20software classes
are outside the bijection proof because20classes can map to18observed signs.
No native letter receives a source value or meaning; forced set is hypothetical
under this model only. ASCII characters are not an identified physical alphabet.
No rawTSV, images, f84/f84r, f116v, f1rbody or reserve admission. No new sources.

## Dependencies and validation

Read1365primary/source-contract and1343/1359primary boundary contracts; those
older terminal doubling/run tests are different laws, not evidence for this one.
Existing800/801semantic/line-boundary terminal studies do not select source
phonemes and are not reused as such. Original failures stand.
Freeze this protocol, primary and independently authored validator, proof review,
cache, allowlist and1365source/method/results before new joint census. Known
q-initial/n-final word forms already make failure plausible; no blind surprise.
Validator must independently rebuild GE2, derive the set and every witness,
including repeated candidate occurrences, singleton and split/reversal controls.
No claim of minimal repair or historical Arabic identification follows.

Registry reconsider(IDEA001045,new_design) reports SAME_MODEL_NOT_REOPENED:
its FULL failure requires new_binding to reopen. We do not reopen that failure.
This followup strengthens a previously untested necessary condition on the
explicit GE2 mixed-direction capacity-only survivor. No failed score is rerun
or repaired, and no reopening approval is claimed.
