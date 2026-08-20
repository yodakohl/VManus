# GDT396 qualification correction validator-provenance successor

Status: `VALIDATOR_PROVENANCE_CORRECTION_FROZEN_BEFORE_REQUALIFICATION`.

Independent review accepted the narrow post-oracle eligibility correction but
found that its V1 freeze did not bind the validator source and its PASS artifact
did not record the validator hash.  V1 remains immutable.  This V2 successor
binds the V1 freeze, V1 validation, V1 validator source, V2 freezer, and V2
validator; V2 validation records and checks its own source hash and recursively
checks every V1 binding.

This changes no decoder, claim, metric, route, property, threshold, world,
surface, seed, or eligibility rule.  The qualification result remains absent
while this provenance correction is frozen and validated.  It authorizes only
the already specified corrected qualifier over the byte-identical completed
metric table.  Confirmation, Voynich scoring, semantic transfer, `f84`, and
`f84r` access remain forbidden.
