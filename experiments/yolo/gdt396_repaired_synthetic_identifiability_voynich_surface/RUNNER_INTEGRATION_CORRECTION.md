# GDT396 runner-integration correction

Status: `PRE_QUALIFICATION_MECHANICAL_CORRECTION`.

The first invocation of the frozen multi-seed runner exposed one interface
assumption in independent decoders D396S01 and D396S02: each designer's local
smoke test fitted a subset of one development seed, whereas the registered
runner fits every available training seed for one world and surface together.
Both implementations therefore initially rejected the runner's input before
producing any claim.

Before qualification data were generated, the integration layer was corrected
without changing either decoder's method, thresholds, features, or outputs:

- `fit` now requires one world and one surface, but permits multiple seeds;
- seed-local physical container identifiers are namespaced by seed before
  recurrence/transition statistics are accumulated; and
- the model's administrative seed is the smallest training seed and is
  overwritten by the runner with the held seed in every emitted claim.

D396S01 namespaces page, paragraph, record, and line IDs. D396S02 uses only
record-level grouping in its fitted statistics and namespaces record IDs. Both
corrected decoders were then run through `run_blind_decoders.py` on W01,
development seed 3960000, `MULTI_RESOLUTION`, and both `FREE_SURFACE` and
`VOYNICH_SURFACE`; all runner schema, locality, rank, span, model-immutability,
and architecture checks passed.

No qualification or confirmation observation or oracle existed or was opened
when this correction was made. The final decoder-panel freeze binds the
corrected source bytes, the original designer attestations, and this disclosure.

A later all-representation development smoke exposed one additional interface
serialization mismatch in D396S05. It had put a hash of each visible candidate
list in `candidate_set_id`; the common interface reserves that field for the
frozen observation-only universe name. Its claim rows now carry the literal
`RECORD_EXCL_SELF` or `PRIOR_SEED_EVENTS`. Candidate generation, scores, ranks,
features, and thresholds are unchanged.

The same smoke showed that D396S02 repeated the source event in the start/end
columns of a negative scope claim. The common schema requires empty endpoints
when `scope_present=FALSE`; those two administrative cells are now empty. Its
scope decision, positive spans, and scoring logic are unchanged.

D396S04's type-to-representative lookup initially rescanned the complete held
event list for every visible type. It now builds the identical first-row lookup
in one pass. This removes a quadratic implementation cost on singleton-heavy
channels without changing a feature, role, score, claim, or threshold.

The runner now expands explicit `UNSUPPORTED` coverage only for endpoints
assigned to the current frozen representation view. The scorer still writes an
explicit `UNSUPPORTED` metric row for every other property/view cell. D396S04
was likewise gated so it does not construct relation, scope, component, or
architecture rows outside the view in which the retention plan can score them.
This preserves the complete scored matrix while avoiding repeated generation
of discarded claims. Every retained event endpoint still has complete
held-event coverage.

The logical-key re-audit added enforcement of each decoder's declared
morphology rank cap. D396S05 already emitted at most three component rows but
had omitted the administrative `MORPHOLOGY_ANALYSIS: 3` entry from its cap
dictionary. That declaration is now present; emitted components and their
order are unchanged.
