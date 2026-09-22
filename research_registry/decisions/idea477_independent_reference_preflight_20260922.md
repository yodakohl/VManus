# IDEA477: independent reference preflight

2026-09-22; bounded manual review started 16:28 UTC. No new experiment, parser,
target opening or arithmetic execution. Frozen RAW and GDT1015 remain unchanged.

**Decision:** the seven declared FETCH sites can form a narrow, coherent
reference layer, but they are not all the old account's backward dependencies.
All remaining global and local bindings must be declared explicitly. The RAW
does not itself provide a complete referent-creation/eligibility ledger.
Separately, combining eager result publication with nonconsuming selection
does remove BOTH A/B comparisons; each change alone leaves one. That exact
dependency is a substantive conditional consequence suitable for a small
frozen-model audit, not confirmation of a manuscript grammar.

## Entire-constructor audit

The table distinguishes what the old MODEL actually declares from bookkeeping
that a new reference evaluator must freeze. D denotes the abstract DAY schema,
U the generic hour unit, H the cyclic order/successor, and alpha the common
initial phase. They are not identified physical days, individual hours or
named planets. MA/MB are calculation records; RA/RB are their result records.

| Constructor | Existing binding and consequence for the new layer |
|---|---|
| C01, 1–8 | Explicit `day_register=DAY`. D can be created here. DAYLIGHT and BOUNDARY are properties/parts in the definition; whether they also create mention records must be fixed, not decided by which untyped rival should fail. |
| C02, 9–16 | Explicit `cycle_register=H`, length from word 10. H is a persistent global order. MEMBER, LAST_MEMBER and RETURN_START operate inside that order; distinguish bound members/operations from separately published discourse individuals. |
| C03, 17–24 | General hour transition and common successor; HOUR at 19 is not a newly observed individual hour. This is an early occurrence of the generic U. Whether it creates/touches an eligible U record must be stated. H/successor is a global function dependency, not one of the seven calls. |
| C04, 25–29 | Call 1: subject FETCH(DAY) obtains D. `name_reference=ruler at initial hour` is a function of common alpha/H, not an additional last-result selection. Since C05 has not chosen alpha yet, C04 is a symbolic naming rule; it cannot pretend to fetch a previously completed numerical ruler result. |
| C05, 30–33 | Choose alpha freely among seven and bind START to the initial hour of D. No prior-method choice. The selected initial ruler, a generic RULER mention and a computation's RULER_RESULT are different semantic roles; give them explicit types/identity policy. |
| C06, 34–39 | NIGHT is part of D; DAY36 rementions D, HOUR37 is the general member/unit U, RULER39 is assigned by H. Repetition must touch old D/U, not create fresh individuals. The RAW's intended C07 untyped countercase requires an eligible last RULER mention at 39; that eligibility is a declared modeling decision. |
| C07, 40–43 | Calls 2–3: FETCH(DAY)→D, FETCH(HOUR_UNIT)→U. These are different types, so local consumption is not what separates them. At closure, publish the day-count result N=24 associated with D, needed by C09. The old model calls the required type HOUR; HOUR_UNIT is the new layer's explicit generic-type refinement. |
| C08, 44–47 | Local bound source hour h restricted to NIGHT and following hour h+1, using the same successor as C03. These are not two fresh generic U identities nor two FETCH calls. Generic unit mentions versus local variables require a fixed publication policy. |
| C09, 48–55 | Call 4: FETCH(DAY_COUNT)→N from C07. But `cycle=C02` is also an explicit old backward dependency. It can remain direct access to global H only if declared as such; silently looking up desired clause ID C02 while advertising universal FETCH would be false. REMAINDER=3 is a numeric output, not a RULER_RESULT. Its publication/mention status must be explicit even if no typed call uses it. |
| C10, 56–63 | Use shared D, U, H and alpha; endpoint is hour 24. At structural closure create/publish MA and its provenance-distinct RA. DAYLIGHT/DAY/HOUR occurrences still need consistent mention treatment. No equality-based choice of which result to publish. |
| C11, 64–75 | Open MB, compute local RB from common alpha/H and two separately counted unit operands. `start=same initial ruler as METHOD_A` is direct common-alpha access, not secretly a METHOD lookup by the desired ID. CYCLE73 likewise uses H. Call 5 at SAME75 chooses a result. Primary delayed visibility yields RA; eager visibility can yield RB. Closure publishes MB/RB under the frozen policy. |
| C12, 76–80 | Calls 6–7: FETCH(METHOD) then FETCH(METHOD). With local consumption obtain MB, MA; without it obtain MB twice. HOUR79 is expressly generic and RULERSHIP80 is the projection applied to the selected methods. Those projections must use their function arguments, not another hidden result lookup. |

Thus seven is defensible only as the number of declared **dynamic selections**
after exposing the old global/function/local bindings. It is not an exhaustive
count of anaphoric-looking words, prior-clause links or all reference behavior.
C09.cycle, C08.successor, C11.start and C04.name_reference are concrete boundaries
to this claim. No additional obligatory dynamic choice was established once
those dependencies are openly treated as the unchanged globals/functions.
The classification is a supplied design, not recovered syntax or uniquely
minimal grammar. Choosing it just to obtain the seven desired outputs would
not be independent evidence.

## Manual selection trace and combined rival

At each of the twelve constructor entries reset local used set U_used to empty;
it must not be confused with the generic hour-unit record U. Under the proposed
primary availability discipline the seven outputs in order are:

`D; D, U; N; RA; MB, MA`.

In C11 the locally computed RB is an argument to the comparison, not another
FETCH. At that moment the completed-result candidates contain RA, while RB
is still private. C12 starts after both calculations have structurally closed.
The new algorithm need only know required type, visibility, recency and the
used set; it must not receive the desired ID, clause number, expected value or
equality result as a selection key.

Let a=value(RA), b=value(RB). The whole two-comparison consequence is:

| Publication / selection | C11 comparison | C12 comparison | Truth pair if a≠b | Joint obligation |
|---|---|---|---|---|
| Delayed / consuming | RB versus RA | MB versus MA, projected | false, false | a=b |
| Delayed / nonconsuming | RB versus RA | MB versus MB, projected | false, true | a=b |
| Eager / consuming | RB versus RB | MB versus MA, projected | true, false | a=b |
| Eager / nonconsuming | RB versus RB | MB versus MB, projected | true, true | tautology |

For a=b all four rows give true,true. Consequently testing each rule change
alone can conceal the combined loss of every A/B equality requirement. The
combined rival is not selected merely because it avoids contradiction: it is
a weaker interpretation that no longer asserts agreement of the two methods.
Other constraints and lexical/scope differences remain; this table alone must
not be called complete coherence of every altered reading.

The root's announced pre-execution clarification is appropriate: completion
and publication are structural, even after a false equality. The false claim
stays false in the constraint ledger; it does not control reference visibility.
This prevents a truth-dependent registry from selecting favorable referents or
silently stopping before a later comparison. It is a new explicit clarification
of RAW's ambiguous “checks equality, and only then registers”, not an already
executed GDT1015 reference rule.

## Remaining freeze requirements and diagnostic limits

- **Result identity:** RA and RB are provenance-distinct result records even
  when they denote the same ruler value. MA/MB are separate method records;
  fetching RA does not automatically consume MA. Interning results by their
  equal numeric/planet value would erase the self-versus-cross distinction.
- **Eligibility:** specify every creation, mention, local variable, output and
  publication in the table. Old MODEL stores patterns/binding descriptions;
  it does not supply this complete event ledger. Publish order within a closure,
  recency updates after FETCH and whether touching a result touches its owner
  must not be silently chosen in code.
- **Eager visibility:** RB must actually become eligible before SAME. Appending
  it with `completed=false` while FETCH still filters completed records would
  leave the primary result unchanged. Freeze whether the eager event publishes
  both MB/RB or only the computed RB; the seven typed outputs alone cannot
  distinguish those implementations.
- **Global consumption:** if D is one identity as RAW requires, C04 consumes
  it and C06 only rementions it. With no reset, C07's first fetch already has
  an empty DAY domain. There is no need to invent a later A-exhaustion failure;
  that later claim additionally depends on method/result identity conventions.
- **Untyped recency:** the first conflict may already occur at C04 if C03's
  HOUR or a MEMBER/function record is eligible, or H is the latest record.
  Do not force the first failure to the attractive RULER39 example at C07.
  A full eligibility ledger determines it before execution.
- **Old rival bindings:** importing the 357 old numeric settings does not mean
  preserving every old reference rule. In particular SAME_METHOD_REFERENCE
  originally fixes C12=B/B. Replacing the seven sites by the new policy must
  be labelled explicitly; retain each old lexical and nonreference scope change.

## Prior execution and manuscript ceiling

The original `src/run.py` computes C11 directly as `a==b`, and C12 as either
`True` for old B/B or `a==b` (line 42). It contains no general discourse FETCH
implementation. The old arithmetic validation therefore does not validate the
new eligibility ledger or its alleged exhaustiveness. GDT933's typed recency
and GDT947's failed exact-written-antecedent contract remain distinct predecessors;
no prefix interpretation or previously closed reference census is reopened.

SCOPE_CORRECTION remains binding: these are all 80 positions of the normalized
working copy, not full diplomatic manuscript coverage. The disputed normalized
HOUR at position 37 is actually `qok[ee:ch]dy` in the cache; normalized DAY_COUNT
`ra` at position 54 omits the braced material in `ra{cty}`. They directly touch
the proposed hour and day-count references. Only three of nine original lines
are anchor-eligible. No literal alternate-reader result follows from this audit.

All 60 opaque word guesses, twelve authored constructor patterns and their
earlier exposure remain. Only C12 supplies two candidates of the same METHOD
type for consumption to distinguish; most other typed fetches have just one
eligible referent under the supplied registry. A successful replay would be a
conditional refactoring plus the combined-rival dependency above, not learned
word composition, astronomy, an independently selected reading or a translated
word. Reflexive comparisons remain legitimate rivals outside this new rule.

## Frozen input hashes checked

| Input | SHA-256 |
|---|---|
| RAW477 | `ae6d21f1355c02d01bfa7380524695960e1097d24b5a3e4c5dd706d5240e6169` |
| GDT1015 READING_v01 | `9d96ef4198c8623183e25724331559c9bc2bad3b159fcdabcaee07ebb26f7840` |
| GDT1015 MODEL_v01 | `07fdeb0b6f53fad8d9f2a253c585699c8c5d248c9206d4599d43e3ceaf5171c7` |
| GDT1015 REPORT | `f067ae4313f4e3b155bcdf524e6ae578fceab0e28d8227a80a8e0da7e1810f34` |
| GDT1015 SCOPE_CORRECTION | `0308a1a0d592c759c7b8ffd4c3d425f44371b33f0b9e932eb3cb0da1461f9001` |
| GDT1015 legacy run.py, read only | `5acfe03f8f51935ce6a1f806c337e1a6ab9eedeba48518f54bd3309ebf48fdee` |

No old input, code, registry or shared status file was changed.
