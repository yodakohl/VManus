# GDT837 preregistration

The executable specification is src/SPEC.json; source/encoder gates are in
src/ENCODER_SPEC.json. METHOD.md explains the comparison and claim limits.
These files, the fitting/evaluation/validation code and frozen inputs are bound
by src/PREREG_LOCK.json before the first real initialization or score.

The fixed SCG Books I–II / III–IV source passes the inherited capacity gates:
9859 discovery / 13828 held source sentences, 129120 / 192991 words, all 22 active
literal, 4 suffix and 8 wholeword rules observed in discovery. Held novelty is
20871 composed form occurrences and 8254 unambiguous composed lemma occurrences.
There are no held-only rules, unsupported unit exclusions or exact twenty-word
reference overlaps. INITIAL_CAPACITY.json remains preserved. Source-only checking
may access source text and aggregate gold metadata, but no world truth map or
held recovery is inspected before the complete fit lock.

Registration occurs after implementation and invented-fixture tests, before any
real fit. Generation is already complete and its byte commitments are published;
confirmation payloads are withheld from this initial public tree until all 48
fits and six selections have been frozen. Publication of source material makes
blinding procedural, not cryptographic secrecy. The fitter has no truth interface.

Decision order: SOURCE_CAPACITY_STOP; INITIALIZATION_STOP; STRICT_RECOVERY_FAIL;
FRESH_RECOVERY_PASS_NO_DEMONSTRATED_CONSTRAINT_GAIN; or
FRESH_RECOVERY_PASS_WITH_CONSTRAINT_GAIN. No oracle selection or repair is allowed.
All thresholds, seeds, budgets and the common role-identifiability criterion are
fixed by SPEC.json. Oracle objective and proposal rejection counts are secondary.
