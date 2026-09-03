# GDT770 artifacts

Status: `PASS`. The runner writes seventeen deterministic artifacts; the
independent validator adds `VALIDATION.json` after 34,744 assertions and a
17/17 byte-identical temporary replay.

## Cohort and target graph

- `MASKED_COHORT_15_LINE_ATLAS.tsv` — all 131 tokens with four target
  spellings replaced by opaque mask IDs.
- `TARGET_17_OCCURRENCE_INVENTORY.tsv` — direct exact neighbours and scorer
  context for the seventeen target occurrences.
- `NULL_ORPHAN_EDGE_ATLAS.tsv` — the thirty amount, value, patient, result, and
  two-sided field edges left open by target-matched NULL.

## Candidate scoring

- `CANDIDATE_OCCURRENCE_SCOREBOARD.tsv` — seventy-five candidate-occurrence
  penalties, bound role edges, and orphan disposition.
- `ATTACHMENT_EDGE_ATLAS.tsv` — every ordered required or optional binding
  claim, including visible double claims.
- `ORPHAN_DEBT_ATLAS.tsv` — candidate-by-NULL-orphan resolution state.
- `PENALTY_EVENT_ATLAS.tsv` — one row per concrete penalty event.
- `TARGET_POLICY_SCOREBOARD.tsv` — aggregate scores, NULL deltas, rival
  margins, removed orphans, and winner eligibility.
- `LEAVE_ONE_PAGE_OUT.tsv` — all page holdouts without refitting a policy.
- `BRANCH_COVERAGE.tsv` — observed versus required pages for every fixed
  branch.
- `WINNER_GATE_AUDIT.tsv` — all eight ordered gate decisions per candidate.
- `TARGET_DECISIONS.tsv` — raw lead and formal target decision for each opaque
  target mask.

## Working meanings and complete reader

- `GDT770_4_WORKING_DICTIONARY.tsv` — four concrete replaceable defaults,
  formal and exploratory confidence, evidence, and counterevidence.
- `FIFTEEN_COMPLETE_LINE_READER.tsv` — full written-order working readers for
  all fifteen lines.
- `READER_UNIT_CONSUMPTION.tsv` — 127 disjoint reader units whose source
  memberships cover all 131 token ordinals exactly once.
- `GDT770_CONCRETE_READER.md` — human-readable lines; every tied local minimum
  is retained, C-support and ties are bracketed, and editorial German receives
  zero score credit.
- `RESULT.json` — compact counts, score contract, scope guards, decisions, and
  claim ceiling.
- `VALIDATION.json` — independent schema, source, scorer, reader, guard, and
  byte-replay validation.

Lower penalty is better. The reader is post-score exploratory output, not a
target-wide winner or recovered plaintext. `Fertigprodukt/Colatura` is rendered
conservatively as `fertige Zubereitung`; no specific colature identity has
been established. Structural tags remain distinct from German word choices.
