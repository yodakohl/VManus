# Independent design review

2026-09-05. Review of the proposal, `SPEC.json` and `../PREREGISTRATION.md`
before manuscript candidate extraction. No manuscript rows, candidate counts,
terminal outcomes or images were inspected by this reviewer. This is a
methodological review, not independent evidence for an experimental result.

## Contract assessment

The specification and preregistration agree on the principal safeguards:

- Match the complete target-group body with its final literal l/m masked,
  plus twelve literal transcription atoms on either side. Separators remain
  in the signature without contributing to the atom count. Partial outer
  groups make these extended local contexts, not guaranteed whole passages.
- Keep extended entities and bracketed constructs opaque. Normalize only an
  admissible physical line join and a definite group gap to the comparison
  GAP; retain uncertainty and split at paragraph, locus, panel and drawing
  barriers. This normalization is an analytical convention, not a finding
  that manuscript line breaks are word spaces.
- Freeze every recurrent-context occurrence before revealing layout. Select
  crossed-layout pairs with target values still hidden, including unchanged
  and reverse outcomes by construction. Do not require both endings to occur.
- Primary pairs require known equal source hand labels. Collapse repetition
  families linked through physical leaves, including their sides and panels,
  and retain one deterministic pair per component. Never replace tied pairs.
- Stop this unit at inventory and upper-bound capacity. Alternative readings
  are separate sensitivity channels; they cannot multiply manuscript evidence.

No substantive mismatch was found between the two reviewed documents.
`primary_certainty` denotes the stated transcription-syntax filter, not known
glyph identity or phonetic certainty for opaque entities. Equal hand labels
are inherited annotations; their equality is not a new palaeographic result.
Conservative component construction limits obvious pseudoreplication without
establishing probabilistic independence of manuscript observations.

## Independently calculated power

For informative, non-tied contrast count n, let k be the least upper-tail
critical value satisfying `2 * P(Binomial(n, .5) >= k) <= .01`. The exact
two-sided rejection regions are `X >= k` and `X <= n-k`. Power at directional
success probability .8 is the sum of these two tail probabilities under
`Binomial(n, .8)`. Direct finite binomial summation gives:

| Informative n | Upper critical k | Actual two-sided size | Power at .8 |
|---:|---:|---:|---:|
| 29 | 22 | .008130058646202 | .790272919484 |
| 30 | 23 | .005222879350185 | .760790618738 |
| 31 | 24 | .003326892852784 | .730026478914 |
| 32 | 24 | .007000366691500 | .825395312300 |
| 33 | 25 | .004551384132355 | .799963623379 |
| 34 | 25 | .009041185490787 | .874563244161 |

Enumeration from n=1 establishes n=32 as the first sample size reaching
power .8. Discrete critical values make power nonmonotonic: n=33 is slightly
below .8. A future test must calculate power for its actual informative n,
not use rounded percentages or an unconditional `n >= 32` shortcut.

Before revealing target values, U primary crossed-layout components supply
only an upper bound on informative n. If U<32, this fixed design cannot meet
its power requirement even if every selected pair changes. U>=32 establishes
potential feasibility only; ties can still remove the necessary information.

The prospective sign test concerns directional asymmetry among changed
pairs. Unchanged pairs remain ties. Their abundance by itself establishes
neither a text-fixed mechanism nor a rejection of probabilistic layout
influence. No direction test or semantic conclusion is authorized by this
capacity-only review.
