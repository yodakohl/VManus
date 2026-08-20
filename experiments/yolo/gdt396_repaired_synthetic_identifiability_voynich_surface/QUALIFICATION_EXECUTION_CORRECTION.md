# GDT396 qualification execution correction

Status: `POST_ORACLE_QUALIFIER_ELIGIBILITY_CORRECTION_FROZEN_BEFORE_REQUALIFICATION`.

The qualification scorer completed its full frozen pass and wrote 117,100
aggregate rows.  The first qualifier invocation then stopped without writing a
qualification result.  It requested an event-level W10 false-positive rate for
`D396S01 / ALTERNATIVE_RELATION / FULL_GROUP / FREE_SURFACE`, although that
property/representation cell is explicitly `UNSUPPORTED` under the frozen
claim-retention plan.

This exposed a mismatch between two prequalification safeguards:

* every *supported* semantic route must have five W10 rows and an event-level
  false-positive rate;
* omitted property/representation cells are serialized as five explicit
  `UNSUPPORTED` rows and are not candidate routes.

The correction is deliberately narrow.  A complete five-seed W10 route whose
five rows are all exactly `UNSUPPORTED` is exempt from the event-level W10-rate
requirement and remains ineligible.  Every supported, `NO_CAPACITY`, scored, or
otherwise non-`UNSUPPORTED` semantic route retains the fail-closed five-seed
and rate requirements.  Missing W10 routes still raise an error.

No score, threshold, representation, property, decoder, seed, world, surface,
or confirmation rule changes.  No decoder is repaired or rerun.  The already
frozen blind claims and completed metric table remain byte-identical.  This is
a post-oracle execution correction, and that chronology is part of the result.
It authorizes only re-running the deterministic qualifier over the existing
metric table.  It does not authorize confirmation generation, Voynich scoring,
semantic transfer, or access to `f84` or `f84r`.
