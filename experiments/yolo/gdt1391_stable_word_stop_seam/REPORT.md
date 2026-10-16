# GDT1391 — an existing boundary pair excludes stable immediate stopping

**STABLE_STOP_CONTRACT_EXCLUDED.** The existing same-line pair `saino ol`
contradicts any causal deterministic grouping rule with all three properties:
a mandatory immediate word stop, a stop condition that remains true for the
same next sign, and no state change at the written gap. This is a new
conditional deduction from an old source, not a newly discovered reading.

The proof needs no key or bound on the number of states. The concrete
MOVE* followed by WAIT/ROTATE writer, IDEA1065, satisfies these premises and
is therefore excluded under its fixed output-unit/group assumptions. Original
IDEA1054, which accepts externally supplied phases, remains outside the claim.

## The manual witness

| Reading | First complete group | Immediately following complete group |
|---|---|---|
| IT2a | f75v.48 G006: `saino` | f75v.48 G007: `ol` |
| ZL3b | f75v.48 G006: `saino` | f75v.48 G007: `ol` |
| RF1b | f75v.48 G006: `saino` | f75v.48 G007: `ol` |

All exterior separators are definite spaces. Original indices are consecutive
on the same physical prose line; its own paragraph-start and paragraph-end
flags are zero in each reading. The unique working-unit parses are
`[s,a,i,n,o]` and `[o,l]`. These are three readings of one physical occurrence,
not three independent manuscript confirmations. No new image was inspected.

If the last o in `saino` triggers an obligatory immediate stop, and consuming
that o leaves another o terminal, then the next group must be the singleton
`o`. It cannot be `ol`. Both the written l and the complete group are retained;
no sign, gap or action is silently removed.

Formally, let T(s,x) indicate a stop while consuming x from state s, and let
F(s,x) be the resulting state. The tested stability is

    T(s,x) => T(F(s,x),x).

After the first terminal x, continuity leaves state F(s,x). A next x therefore
ends immediately. This argument permits arbitrary state size, noninvertible
updates and unrelated internal content. It does not assume a common endpoint
or a first-sign entry-state table.

## Application to the complete proposed writer

The new IDEA1065 contract uses five named containers with total stock five.
It preserves every source action. A word contains zero or more legal unit
transfers, followed by one WAIT or ROTATE; the first such action ends the word.
The running inventory continues across words. The writer/reader construction
is internally coherent, but internal coherence is not native compatibility.

With k occupied containers there are 4k legal transfers, then WAIT and ROTATE
at ranks 4k and 4k+1. Either completion preserves k. The same written rank is
therefore terminal again, independently of its unknown global glyph binding.
All 252 completion cases across the 126 inventory states have this property.
The elapsed waiting counter does not affect rank or stopping, so its unbounded
size cannot change the conclusion.

A separate inherited-capacity contradiction reaches the same concrete writer:
its ten possible final ranks are `4,5,8,9,12,13,16,17,20,21`. GDT1319 already
retains 18/19/19 distinct active final working units for ZL/IT/RF. These exceed
ten under the stipulated bijection. No new endpoint census was performed.
The seam proof does not depend on that larger inventory or its rare endpoints.

## Verification and limits

The full proposed grammar was written before reviewers retrieved the inherited
endpoint contradiction. Its registry retention followed that counterevidence,
with the chronology disclosed. Root selected the old `saino ol` pair manually
before executable verification. The plan is expressly post-observation; there
is no held-out result, statistical discovery claim or selected favorable p-value.

The primary program builds the ordered legal-action menu. A separate validator
uses arithmetic ranks over occupied source containers. All 2,772 state/rank
cases agree: 1,652 legal and 1,120 illegal. Source-free two-state fixtures and
17,856 independent greedy-stream checks supplement the general proof. The
source witness, unique parses, original flags, old endpoint counts and both
saved escaping countermodels independently verify. Validation PASS concerns
source fidelity and the conditional deduction, not manuscript meaning.

The proof leaves open rules whose stop changes its own condition, genuine
state changes at boundaries, lookahead, and externally chosen boundaries that
replace the mandatory stop rule. Explicit countermodels show two of these
escapes. They are scope checks, not repaired Voynich readings. Contextual
choice of actions alone cannot rescue a writer that retains all excluded
premises. Different glyph identities or grouping would also change the input
contract and require evidence rather than an invented exception.

GDT1326's identical-reset prefix obstruction is a different theorem. GDT1319's
entry/exit equality-table result is also different; only its old final-unit
inventory is reused here. Original1054 is not closed, and there is no claim
that all stateful, phonetic, numerical or semantic systems are impossible.

**Decision:** retain this exclusion for future writer design. A construction
that generates boundaries must explicitly account for `saino ol`; it cannot
retain a self-stable obligatory stop across that gap. Do not run a larger
state solver for IDEA1065 or add a reset to save it after observing the failure.
No word meaning, letter value or complete passage translation is obtained.
