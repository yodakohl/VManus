# Independent first-contract review: frames, degree coverage, and `ain`

27 September 2026. This review covers only the released first contract
`PLANET_CHILD_AUTHOR_CONTRACT.md` (SHA256
`fc0092ad0792ea86aa26fdb24c3df3760a93425e8a17dda48cd63a5086f1e05f`). I
did not inspect any subsequent whole-form draft, target query, or new source.
The review tests the frozen contract against the earlier source-side
obligations; it does not prescribe a repair.

## Match to source-side requirements

The contract substantially preserves the required argument distinctions:

- `PowerFrame(p,e,U)` treats the planet `q` as power bearer and retains the
  same human `p` and one disjunctive birth/conception event `e`. Its domain
  is the seven-planet source collective. The strongest condition, rising
  east, and great-power guard are explicit rather than collapsed into one
  hidden lookup.
- `ReceiptFrame(p,H)` treats `p` as holder and the planet `q` as donor and
  provenance. Its domain is actual contributors to `p`'s named profile `H`,
  not automatically all seven planets or the power-support set.
- The contract expressly avoids asserting that `q` (power leader), the
  contributor set, and `r` (greatest received share/name source) are
  identical. It retains donor-nature and chosen donor-strength dependencies
  without adding a scale, linear rule, or power/share equality.
- It distinguishes rare sole power from mixed receipt, keeps the
  `some-two/some-three/some-all` statements non-exhaustive, and allows sole
  power. It also retains final naming on the same person, with an explicit
  birth `b` and the same name-source planet in the day-or-hour alternatives.
- `T_R` is defined as a global greatest relation, not merely locally
  undominated, and does not insert uniqueness or a tie-break. The Respect
  family is closed to exactly POWER and RECEIVED_PROPERTIES; `ain` is a
  reference to a prior evaluated Respect rather than a third value. The five
  compound cuts, no-free-`dain` policy, no aliasing, and no internal-register
  update are mechanically clear at contract level.

The `LAST_RESPECT` rule is determinate in the declared N,E,S,W discourse:
only a preceding standalone evaluated Respect expression updates the
register; an internal occurrence does not, and an anaphor repeats rather
than changes the resolved value. If no eligible antecedent exists, the result
is a gap. This avoids silently making `qodain` pick a respect based on the
line's later meaning. It remains an explicit discourse assumption rather
than a source-established rule, as the contract acknowledges.

## Frame coverage: a real underspecification, not an inconsistency

One formal gap remains in the closed-frame interface. A frame has a nonempty
index domain and a typed **relation** `Observe_F(q,v)`. The templates define
`G_R(F,q,v)` only when such a `v` is present. `T_R(F,q)` requires an observed
value for the candidate `q`, then compares it with every value that happens
to be observed for every index `r` in the domain. It does **not** require
every domain member to have a value, and it does not require one unique value
per member.

The emptiness case makes this concrete. Let the power domain be the source's
seven planets, let only `A` have an observation (`Observe_F(A,2)`), and let
there be no observation for `B` through `G`. Then `T_POWER(F,A)` is true:
the universal condition has no observed counterexample for any of the six
missing planets. Yet the frame has not established that `A` is greatest
among the seven. Similarly, a receipt frame with support `{A,B}` but only an
observed share for `A` can declare `A` greatest without comparing `B`.

This is not inconsistent with the template definition; it is a vacuous
case permitted by it. Frame prose (“the observation is q's degree …”) may
be intended to supply an observation for each q, and calling it a “complete
ComparisonFrame” points in that direction, but neither phrase is a stated
totality condition. The explicit `Observe_F` relation and guarded universal
quantifier leave the gap visible. For the contract's claimed comparison over
all seven / all contributors, the minimum obligation is that each member of
the declared domain have at least one `Observe_F(q,v)` value. That would
prevent an absent candidate from disappearing under the universal. The
frame can remain non-functional if its semantics are intentionally
relational, but then that choice needs interpretation: with multiple values
for `A`, `T` selects an observed value that dominates every observed value
(including `A`'s own others). It does not mean “A has one degree” unless
functionality or an equivalent single-degree interpretation is supplied.

I classify this as a contract-level **coverage/degree-arity
underspecification**, not a contradiction and not evidence that any concrete
planet lacks a value. It matters before claiming a source-faithful global
greatest; no draft is needed to see it.

## `LAST_RESPECT` and subtype closure

The exact two-value Respect domain and `ain : RespectRef → Respect` are
coherent. The rule handles both free `ain` and its occurrence inside
`qodain`, bans a third respect, and prevents internal `ar`/`aiin` pieces
inside derived compounds from changing the antecedent register. This is
particularly useful because otherwise `qodain` could resolve to the
wrongmost internal piece or to a reader-selected line-specific respect.
There is no contract-level subtype inconsistency in the stated
`Respect`, `RespectRef`, `GradedTemplate`, `TopTemplate`, or the two frame
schemas.

Potential boundary questions—how the whole discourse orders groups within
the declared N,E,S,W sequence, and whether a standalone anaphor itself
re-enters the register—do not create competing values under this rule: a
standalone `ain` can only repeat its already resolved Respect. They should
be checked against the frozen whole-form accounting later, but are not a
reason to revise the first contract now.

## Review conclusion

The frozen contract preserves the principal source-side role distinctions,
event OR, two comparison respects, provenance, and same-planet natal naming.
Its main contract-only limitation is precise: greatest is computed over
observed values, but frame membership is not explicitly covered by
observations, and the relation is not explicitly functional. An author can
therefore complete the typed composition under the written formulas while
still leaving a declared competitor unobserved. Any later result should
separate that formal success from a genuinely complete comparison frame.

No target form, literal assignment, semantic truth, source identity, or
historical planet comparison is established by this review.
