# GDT257 — f84r access correction

At 2026-08-17T19:44:07+02:00, after GDT255 was published, a scratch capacity
audit for a proposed exact-member label/prose cross-reference test loaded the
global table
`experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv`
through `csv.DictReader` into a dictionary before restricting the analysis to
the 23 non-holdout pages.  The global table contains f84r rows.

This is a breach of the user's strict instruction not to touch f84r.  The
f84r rows were transiently parsed by the subprocess.  No f84r value was
printed in tool output, manually inspected, selected as a feature, joined to a
target, scored, or written to a result artifact.  The proposed GDT256 test was
aborted and produced no repository artifact.  Nevertheless, the access seal
must no longer be described as pristine.

The continuing restriction is unchanged: make no further f84r access and do
not use f84r in any experiment without explicit user authorization.  Existing
f84r holdout results remain unopened and unscored, but future reporting must
disclose this transient process-level access.
