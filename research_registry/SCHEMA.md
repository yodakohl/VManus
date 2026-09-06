# Registry contract, version 1

Canonical data is UTF-8 JSONL, one object per line, with deterministic imports.
The generated SQLite FTS5 index requires Python's standard `sqlite3` extension;
there is no embedding service, LLM API, network query or additional dependency.

| Entity/field | Meaning |
|---|---|
| `id`, `aliases` | Stable identity and exact lookup names. Alias collisions require disambiguation. |
| `kind` | `idea`, `family`, `attempt`, `history`, `anchor`; never automatically interchangeable. |
| `scope` | `semantic`, `structural`, `method`, `acquisition`, `workflow`, `unknown`. |
| `source_status`, `events` | Original reported claims and append-only source history, including limitations. |
| `review_status` | `imported_unreviewed`, `inherited_summary`, `curated`, `stale_review`. |
| `assessment_basis` | `primary_reports`, `registry_summary_only`, `proposal_only`; source level is visible. |
| `verdict` | `unreviewed`, `untested`, `supported_limited`, `nonconfirming`, `refuted_specific_model`, `inconclusive`, `not_tested`, `stopped_by_user`. |
| `blockers` | List of `{code, detail, evidence:[path]}`. Multiple reasons may coexist. |
| `reopen` | `{policy, all_of:[condition], not_sufficient:[text]}`. Conditions are source-bound obligations, not auto-evaluated truth. |
| `condition` | `{id, change, detail, evidence}`; optional scoped numerical `fact:{key,op,value}`. |
| `relations` | Evidence-backed `tests`, `duplicate_of`, `related_to`, `corrects`, `supersedes`; imported `same_experiment_reference` is navigation only. |
| `design` | Mechanism, unit, contrast, prediction and scope, used for declared-design duplicate candidates. |
| `sources` | Actual imported metadata path, line locator and hash; linked reports are separate pointers. |
| `signals` | Explicit lexical history hints; never scientific adjudications. |

Common blocker codes distinguish `insufficient_independent_data`,
`missing_matched_contrast`, `confounded_data`, `missing_binding`,
`missing_readable_values`, `test_not_validated`, `model_counterexample`,
`nonconfirmation`, `user_stop`, `primary_report_unavailable`, `unmotivated_model`
and `not_reviewed`. An empty blocker list on an unreviewed import means unknown,
not ready or successful.

Reopening policies: `unreviewed`, `conditional`, `do_not_repeat_same_model`,
`user_stopped`. Revision history uses `previous_sha256`; review basis uses
`basis_sha256` plus individual `evidence_sha256`. New events or changed primary
reports invalidate the review. An unrelated append elsewhere in the ledger does
not alter the record's scientific basis, although the metadata snapshot must be
refreshed. Identical wording does not establish duplicate identity.

Migration completeness means preservation of the source records and retrieval
paths. It does not mean all historical hypotheses are reconciled, all old
reports survive, or all imported claims are true. Unreviewed work remains
explicitly filterable and searchable; assess it when a candidate makes it relevant.
