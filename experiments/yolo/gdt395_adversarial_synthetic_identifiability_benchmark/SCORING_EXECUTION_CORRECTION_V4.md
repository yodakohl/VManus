# GDT395 scoring execution correction V4

Status: `POST_ORACLE_SCHEMA_CORRECTION_FROZEN_BEFORE_SCORING_V4`

V3 authenticated and ingested all 50 permitted held synthetic oracle files
(422,697 rows), then stopped while scoring the first W03 partition. No aggregate
score file was written. This is therefore a post-oracle correction.

The frozen oracle schema permits canonical pipe-delimited truth sets. In W03,
19,547 of 42,268 held events use such sets in several anonymous partition
fields; all other worlds are scalar on the triggering lexical field. The
original scorer and validator incorrectly required one atom for every
partition truth.

V4 keeps every event and treats each canonical sorted set as one opaque
composite partition label. It does not split a multi-ID event, select one atom,
discard the event, expose names, or introduce a multi-label similarity metric.
`A|B` equals only the same canonical `A|B`; this is still exact anonymous
partition recovery. Literal `NONE` remains absent truth.

The matching independent-validator wrapper changes only its oracle partition
gate from “exactly one atom” to “one canonical opaque atom-set.” Existing pipe
canonicalization and all other oracle, claim, metric, threshold, capacity,
decision, and output checks remain unchanged.

No per-world recovery result was available or inspected when this rule was
chosen. No Voynich source or f84 data was accessed.

