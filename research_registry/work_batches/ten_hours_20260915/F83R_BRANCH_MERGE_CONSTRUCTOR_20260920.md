# f83r.25–30: branch/merge constructor with executable reduction

Status: RAW_UNREVIEWED, exploratory and unselected. This is a new target-side
hypothesis over already exposed report-owned text. It does not revise IDEA414,
does not use the Balneis source, and does not claim an English or historical
translation. No new target data, image, reserve, sealed folio, decoder or
experiment was used.

## Fixed input and distinctness

The six complete lines and all 33 groups are copied from
`research_registry/proposals/translation_programs_20260912/work/P12/READING_L1.md`.
This is the complete 33-group ZL3b/P12-like display used by this proposal.
IT2a has a separate f83r.25–44 paragraph with 92 groups; it is not silently
treated as the same paragraph and remains a coverage debt for this hypothesis.
The exact input remains:

```text
f83r.25 qokeedy qolchey qokeey qokedy chedy otal
f83r.26 otchey qokeey qoky tol shedy qokylddy
f83r.27 dain chedy qokeedy shckhedy shckhedy
f83r.28 saiin cheeky sheey qokedy shedy oldy
f83r.29 salchedy cheey qody kesd oldy
f83r.30 s okeedy qokeedy qoky saii
```

The hypothesis is a finite branch/reference/guard process. Reusable parts
create and update opaque registers; they do not carry Balneis state values or
Llull rule species. Whole-form residuals are permitted only under the one
declared feature-signature rule in the executable file. P1 has no residual
groups, so its 33 outputs are all derived from shared parts.

## Reduction law

The executable specification is
`f83r_branch_merge_constructor.py`; generated traces are
`F83R_BRANCH_MERGE_P1_OUTPUT_20260920.json` and the prospective P2 trace is
`F83R_BRANCH_MERGE_P2_PREDICTION_20260920.json`.

The finite surface inventory is:

| Reusable part | Role |
|---|---|
| `qok` | UPDATE operator |
| `qol` | RELATE operator |
| `che`, `chey` | EFFECT and link frames |
| `ot` | GUARD operator |
| `sh`, `ckh` | participant and list-item frames |
| `da`, `sa`, `qo`, `kes`, `ol`, `o`, `ke`, `t`, `s` | order, reference, state-reference, negation, owner, renewal, material, location and topic roots |
| `e`, `l` | explicit-argument and scope parts |
| `edy`, `ey`, `y`, `dy`, `ddy`, `al`, `iin`, `in`, `ii`, `ky`, `d` | declaration, outcome, continuation, completion, guarded completion, target, attribution, order, closure, degree and negative frames |

The parser uses longest declared surface atoms, then the fixed residual rule
`R(first_character, token_length mod 2, vowel_count mod 3)` only if no complete
segmentation exists. A residual is an opaque typed argument shared by that
feature class; it is not assigned a word meaning. P1 requires zero residuals.

The context reducer maintains `last_register`, `last_event`, a scope depth, a
branch counter and participant registers. `qok` allocates a new register and
updates it; suffix frames choose UPDATE, CONTINUE_UPDATE or GUARDED_UPDATE.
`che` emits an EFFECT against the current register. `qol` links the current
register, `ot` guards the prior event, `sh` binds a participant, `da` opens an
ordered branch, `sa` references the current register, `qo` references its
state, `kes` negates the prior event, `ol` emits an owner reference, `o` emits
renewal, `t` locates, and `s` opens the topic. Every constructor has fixed
arity; context supplies register identity, never a fitted whole-form value.

## Complete P1 reduction

The generated operation sequence is:

| Locus | Derived operation sequence |
|---|---|
| .25 | `UPDATE → RELATE → UPDATE → UPDATE → EFFECT → GUARD` |
| .26 | `GUARD → UPDATE → CONTINUE_UPDATE → LOCATE → BIND → GUARDED_UPDATE` |
| .27 | `ORDER → EFFECT → UPDATE → BIND → BIND` |
| .28 | `REFERENCE → EFFECT → BIND → UPDATE → BIND → OWNER_REFERENCE` |
| .29 | `REFERENCE → EFFECT → STATE_REFERENCE → NEGATE → OWNER_REFERENCE` |
| .30 | `OPEN_TOPIC → RENEW → UPDATE → CONTINUE_UPDATE → REFERENCE` |

This gives one whole-passage working reading: a topic opens an opaque item;
updates create a directed chain; `qol` relates two successive states; effects
attach to the current state; guards scope prior events; `dain` starts an ordered
branch with two participant bindings; `sa`/`qo`/`ol` resume existing registers;
`kesd` negates the prior event; and `.30` closes by renewing, continuing and
referencing the chain. “Item”, “state”, “participant” and “branch” are typed
variables, not English glosses.

Repeated forms are evaluated by the same rule. `qokeedy` occurs three times and
always parses `qok+e+edy` as `UPDATE` with declaration frame, allocating a new
context register each time. `qokeey` occurs twice as `qok+e+ey`, `qokedy` twice
as `qok+edy`, `qoky` twice as `qok+y`, `chedy` twice as `che+dy`, `shedy` twice
as `sh+edy`, `shckhedy` twice as `sh+ckh+edy`, and `oldy` twice as `ol+dy`.
The same part roles are reused across different wholes: `qok` spans five
surface forms, `che` spans `chedy`, `cheeky`, `cheey` and `salchedy`, `edy`
spans state/participant/list frames, `dy` spans effect/reference/renewal/state
closures, and `e` spans qok, che and sh frames. The generated P1 component
counts are recorded in the JSON artifact rather than inferred from English.

P1 uses 33 groups, 28 distinct surface forms, 0 residuals, 10 state-register
allocations, 5 participant bindings and 1 ordered-branch marker. These are
properties of this declared reduction, not decipherment scores.

## Prospective prediction on another exposed complete paragraph

The same parser was run without changes on the already exposed f83r.9–17
records from `raw_f83r_diagnosis_fallback_aftercare.json`. It produces 84
groups, 11 state registers, 9 participant bindings and 3 branch markers. It
also produces 32 residual-argument events across 20 residual classes. That
sharp residual increase is the model's stated cost: the P1 composition is
compact, but the same reusable inventory does not fully analyze P2. No residual
is silently converted into a semantic operator, and no P2 value was fitted.

The observable prediction is therefore structural: if this constructor were a
real shared writer, another complete paragraph should preserve its qok/che/sh/ot
role signatures and keep residual classes stable across repeated tokens. P2's
32 residual events are an immediate prospective warning against selecting the
model on P1 alone. A rival that permits occurrence-specific whole outputs can
fit both, but loses the shared-part prediction.

## Costs and rivals

Free degrees of freedom are the names of opaque registers, the interpretation
of each finite role label, the choice of the residual feature signature, and
the initial `last_register` context. No target evidence fixes them. The model
also assumes the declared P12 line boundaries and that a new `qok` allocates a
register rather than mutating an old one.

The main rival is an occurrence-specific whole-form reader: it can assign any
operation to a repeated token and therefore avoid P2 residuals, but predicts no
stable component role or register allocation. A second rival treats `qok` as
an in-place update; it preserves the surface parse but changes the number and
identity of downstream registers. The P1 output artifact records the former
allocation, so these are distinct consequences.

No target meaning, source identity, language, or independent semantic success
is claimed. The card remains RAW_UNREVIEWED.


## Root execution review, 2026-09-20 16:49 UTC

Decision: **EXECUTABLE_TAGGER_NOT_COMPLETE_SEMANTIC_CONSTRUCTOR**. Preserve the
original script and RAW card. Its mechanical execution is a real improvement
over an unevaluated table; the result still does not execute the claimed
branch/merge or full component semantics. This is an engineering/design review,
not a Voynich contradiction or translation result.

Root imported the exact script, reran both passages, and separately evaluated
the following whole forms in fresh identical contexts. The main passage has
**33 groups, 24 distinct forms and 29 observed parts**; the dossier's 28-form
count is wrong. Its ten register allocations, five BIND events, one ORDER
counter increment and zero residual events reproduce. P2 has84groups/71forms,
32 residual events,11registers,9BIND events and3ORDER increments. These are
counts of the implementation's labels, not discovered manuscript entities.

| Exact input | Actual event output in a fresh context | Consequence |
|---|---|---|
| `qokeedy`, `qokedy` | both `UPDATE(input=ROOT,output=u0,frame=DECLARE_FRAME)` | the claimed EXPLICIT_ARG part makes no event-level difference |
| `shckhedy`, `shedy` | both `BIND(participant=p0,frame=DECLARE_FRAME)` | the written LIST_ITEM part is recorded but not executed |
| `salchedy` | `REFERENCE(target=u0,frame=COMPLETE_FRAME)` | SCOPE and EFFECT parts are recorded but not composed |
| `qolchey` | `RELATE(source=u0,frame=LINK_FRAME)` | no second endpoint or implemented binary relation is supplied |
| `saii` | `REFERENCE(target=u0,frame=CLOSE_FRAME)` | CLOSE_FRAME is a label; it does not close a guard or branch |

The full P1 execution ends at scope_depth2: guards are incremented, never
closed. The code contains no branch execution or merge. `last_event` stores
only an operation name, not a uniquely addressable event or value; later
references therefore do not implement the occurrence-specific chain described
in the prose. LOCATE has no location argument, GUARD has no evaluated condition,
and NEGATE has no proposition truth evaluation. A richer language could define
all of these, but this script has not done so. The last-line topic cannot be
said to open the beginning of the narrative under the implemented left-to-right
machine; a declarative binding rule would be a new explicit hypothesis.

The P2 trace is an **exploratory exposed application**. There was no prior
public prediction lock, withheld physical leaf, independently known semantic
output or comparison with manuscript meaning. Its residual increase measures
coverage, not a prospective verification or an observed contradiction of the
semantic roles. The feature-based residual classes are also freely selected.

The33group scope is a complete ZL3b paragraph in GDT928's owned cache. IT2a
instead owns f83r.25–44 as92groups; it does not independently confirm the short
scope. A later constructor must retain this source debt. Root's aware native
reinspection of already admitted f83r at approximately16:34UTC did not establish
flow direction, temperature, or participant identity for this model. Nothing
in the figure is used to score the five generated BIND labels.

Reopening requires an actual reduction for every semantic part and a typed
reference/scope/condition system that computes a complete stated content
rather than just operation labels. Exact segmentation, deterministic output,
register counts and a residual fallback are insufficient. No change to414,
GDT993/997, old workshop grammars, reserves or confirmed-word count follows.
