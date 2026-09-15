# GDT973 source-only necessity review

2026-09-15. This review uses only the frozen S0 card
`research_registry/work_batches/ten_hours_20260915/ALLOY_FINITE_GRAMMAR.md`
and the source-only R1/R2 writing cards
`ALLOY_R1_WRITING_MODEL.md` and `ALLOY_R2_WRITING_MODEL.md`. No target cache,
result, image, reserve or new manuscript material was opened. R1 and R2 remain
raw competing writing hypotheses; this is a logical contract audit, not a
meaning result.

## Verdict

The proposed predicates are necessary under the stated models, with two scope
qualifications. The common `>=5` group count is a deliberately weak bound: the
written syntax appears to force four header groups, a separate `FIRST` group,
and at least one `YIELD` group, hence `>=6` when the first branch has only its
required yield. `>=5` is still a valid necessary condition, but it must not be
reported as the model's tight minimum. The R1 shared-initial and shared-final
tests apply only to R1; R2 explicitly removes those universal markers.

The header prefix test must compare each of the first four complete groups with
every other complete group, including the other three headers. Prefix equality
counts as a conflict for distinct positions. A first-failure label or a
survivor therefore cannot be inferred from an early comparison alone.

## Why the predicates follow

### Common and prefix conditions

Both models serialize a fixed four-group header: `GRADES`, `TARGET`, `TOTAL`,
then `FIRST` (or the corresponding branch marker). A branch has a terminal
`YIELD`; even the smallest first branch therefore supplies the separate marker
and yield groups. This proves the stronger six-group lower bound, and therefore
the registered five-group screen is safe but loose.

In R1 every group begins with `h(ENTRY[e])`, and the global component map is
injective and prefix-free. The four header heads `GRADES`, `TARGET`, `TOTAL`
and `FIRST` each occur as a unique constructor in an account. In R2 every group
begins with `H(C@e,m)`; the corresponding four allomorph heads are distinct,
and the allomorph/payload map is globally prefix-free. If a header string were
a prefix of another complete group, prefix-free decoding would force the same
first head component. The unique header heads make that impossible. This proves
the strict prefix-incomparability test for each header against all other
groups, including equality checks between distinct positions. A short first
branch ending immediately in `YIELD` does not change this argument: `YIELD` is
not one of the four header heads.

### R1-only surface consequences

R1 writes each group as an entry component, its core components, and one final
agreement component, with every codeword nonempty and at most eight letters.
Consequently:

| Predicate | Source derivation |
|---|---|
| Every group length at least 3 | `ENTRY + head + AGREE`; `YIELD` is included. |
| First group length 12–144 | `GRADES`, three type atoms, three `NUM` atoms, up to nine decimal digits, `ENTRY`, and `AGREE`: 12 to 18 codewords, each length 1–8. |
| Second and third lengths 5–56 | `TARGET`/`TOTAL`, one `NUM`, and one to three digits, plus `ENTRY` and `AGREE`: 5 to 7 codewords. |
| Fourth length 3–24 | `FIRST` (or its first-branch marker), `ENTRY`, and `AGREE`: 3 codewords. |
| At most two whole-account initial characters | The only group-initial components are `ENTRY0` and `ENTRY1`. Their codewords may share a first character, so the safe bound is two. |
| Header groups 2, 3 and 4 share their first character | Group 1 uses entry context 0; `TARGET`, `TOTAL`, and the following `FIRST` group use entry context 1, hence the same `h(ENTRY1)` codeword. |
| Header groups 1–4 share their last character | Each is an S-type, non-mixed core and ends in the same `AGREE_S0` codeword. |

The first R1 upper bound counts the maximum three digits for each grade; the
S0 strict positive ordering gives one-digit lower cases. The fourth group is a
separate `FIRST`/branch-marker group, not the first statement's `YIELD`.

### R2-only length consequences

R2 removes the universal `ENTRY` and `AGREE` components. Its first four groups
are therefore bounded by their allomorph head plus payload:

| Group | Component count at minimum/maximum | Length range |
|---|---:|---:|
| `GRADES(A,NUM(a),B,NUM(b),C,NUM(c))` | 10 / 16 | 10–128 |
| `TARGET(NUM(t))` | 3 / 5 | 3–40 |
| `TOTAL(NUM(m))` | 3 / 5 | 3–40 |
| `FIRST` or branch marker | 1 / 1 | 1–8 |

Each component code is nonempty and at most eight letters. The grade bounds
allow one to three canonical decimal digits; the same width calculation applies
to target and mass. R2 has no necessary common initial character, common final
character, or all-group minimum: its context is selected inside the operator
allomorph and no universal marker is emitted. Its unique header heads still
support the common first-four prefix-incomparability predicate above.

## Reporting limits

A surviving row would show only compatibility with these necessary surface
conditions for R1 or R2. It would not identify a code, operator, number,
language, alloy, source copy or Voynich meaning. A contradiction should be
reported against the selected fixed writing model and its applicable scope;
failure of R1's marker consequences does not reject R2 or S0. The five-group
screen should be described as a weak precondition rather than evidence of a
minimal complete account.
