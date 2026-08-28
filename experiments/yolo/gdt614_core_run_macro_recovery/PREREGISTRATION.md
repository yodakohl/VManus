# GDT614 prospective execution contract

Date: 2026-08-29

This contract is committed before the GDT614 generator, oracle, or recovery
code is implemented or run. The feasibility search that suggested the repair
was post-hoc to GDT613 and is labelled only as design evidence below.

## Bound inputs and exclusions

- bind GDT608's 98-unit directed tree and all 64 named merges;
- bind GDT609's eight-role historical model family;
- bind GDT613's exact Latin train/held blocks and failed V1 deck;
- bind the post-hoc 64/64 role assignment and candidate V2 deck now exposed in
  `artifacts/REGISTERED_MODEL.json`, without treating that search as a score;
- never read a Voynich target sequence, target key, target glossary, aligned
  plaintext, candidate meaning, f84, or f84r;
- do not change the frozen Latin partitions after seeing any GDT614 score.

The generator, oracle, and fitter may consume only manifest-listed inputs.
Every consumed path and hash is emitted again in the result bundle.

## Fixed model and deck

The exact grammar, role counts, card lengths, design-world outputs, role
assignment, seeds, and thresholds are sealed in
`artifacts/REGISTERED_MODEL.json`. The grammar is:

```text
WORD_EVENT := NULL{0,2} WORD NULL{0,2}
WORD := PREFIX{0,2} CORE_RUN (CONNECTOR CORE_RUN){0,3} SUFFIX{0,2}
CORE_RUN := TERM{1,12}
TERM := CORE | CONTEXT LITERAL | LITERAL CONTEXT
CORE := LITERAL | SYLLABIC | SHORT_CARD | MACRO_CORE
```

`TERM{1,12}` counts atoms; decoded plaintext words remain at most twelve Latin
characters, matching GDT613. All 41 nonempty card outputs must be globally
distinct. Paid output may differ from its child composition; a default merge
must equal its directed left-then-right child output. `qok` may not carry a
paid macro card. The V1 edge-connector, connector-only, standalone-WHOLE, and
boundary-compound branches are not part of V2; no unobserved branch can be
silently credited as covered.

`artifacts/REGISTERED_TRANSITIONS.tsv` is the complete 21-transition catalog.
NULL is a bounded edge layout event removed before plaintext scoring; it is
not a free cipher null. `MACRO_CORE` is an embeddable learned stem or syllable,
not an unrestricted whole-word nomenclator code. Each macro obeys its fixed
`LEFT_HOST`, `RIGHT_HOST`, or `STANDALONE_OR_LEFT_HOST` license in the model
JSON. A macro occurrence outside that license is illegal.

## Labelled design world and paid-card selection

World `W614_0` uses the registered primitive role/output table. Paid merge
locations are not chosen by hand after inspection. The program enumerates all
ordered choices of four short and four macro cards that satisfy grammar and
direct-exposure constraints, then chooses by this fixed objective:

1. maximize the minimum train-type exposure across the 42 scored cards;
2. maximize the minimum held-event exposure across them;
3. maximize the minimum direct train occurrence across the eight paid cards;
4. maximize total distinct labelled merge-node occurrences;
5. take the lexicographically smallest tuple of merge ranks and card IDs.

If exhaustive enumeration is impractical, an exact integer solver may replace
it only if the validator independently checks the witness and the solver
records optimality or a complete infeasibility certificate for objectives
1--3. Solver time may affect speed, never the accepted thresholds.

Every selected plaintext type has exactly one ordered labelled parse with card
multiplicity, character spans, occurrence indices, transition IDs, and a
nonoverlapping tiling by top-level source units. Labelling a
default merge span counts only when its two registered children occupy that
exact span; labelling the same leaf string as another node does not count.
Paid-child exposure must use the unoverridden child parse, not the paid atom.

## Observation-complete gate

Each accepted world must simultaneously certify:

- all 34 primitive cards directly present in train and held;
- all eight paid cards directly present in train and held;
- every paid card's unoverridden child composition present in both partitions;
- all 56 default merge nodes directly labelled in both partitions;
- every one of the 21 registered prefix, suffix, internal-connector, context,
  core-class, adjacency, and edge-null transitions represented in both
  partitions;
- every scored card in at least eight distinct train word types and sixteen
  held events;
- every named merge node in at least one train type and one held event;
- null in at least eight train types, train event mass from 0.5% through 2.5%,
  and at least sixteen held events;
- no output collision and no malformed or unparsed accepted event.
- every one of the 42 cards has at least one private/focal carrier in each
  partition where mutating that card changes acceptance or plaintext without
  being masked by another parse; the 42-column train focal-incidence matrix
  has rank 42.

Potential substring support, a card bit-mask, or a collection of mutually
incompatible parses does not pass. The compact bundle must expose the selected
word, event weight, ordered card/unit sequence, spans, transition labels, and
merge-node labels needed to recompute every count. The independent validator
rebuilds a separate recognizer and recursive 98-unit expansion rather than
importing the generator parser.

## Three-world rule

After `W614_0` passes, worlds `W614_1` and `W614_2` use seeds 61401 and 61402.
For each seed, the program deterministically permutes outputs only within
equal-role/equal-length classes and reruns the registered paid-location and
parse selection. It rejects failed permutations and advances the seed by two,
up to 10,000 attempts per world. The first passing world is fixed. No output
string, role, length, threshold, or plaintext partition may be added or edited.

All three worlds must differ in at least 24 of 34 primitive card outputs and
six of eight paid locations or outputs. Failure to construct three worlds is
`TRUTH_GENERATOR_INFEASIBLE` and stops before oracle fitting.

## Oracle gate

Two independent fourth-order character models are fit: `LM_A` on the frozen
`lm_fit` block and `LM_B` on `lm_confirm`. Each uses the published GDT613
reset-matched construction: alphabet `a..z` plus boundary, three BOS symbols,
one EOS symbol, add-one unigram probabilities, and recursive Dirichlet
backoff of strength `0.25 * 27` at orders two through four. Forward and
reversed-word models are fit separately. For a decoded word event `w`:

```text
J_X(w) = -0.5 * (log2 P_X_forward(BOS^3,w,EOS)
               + log2 P_X_reverse(BOS^3,reverse(w),EOS))
```

Scores sum event negative log probability; they are never normalized by
emitted length. Illegal parses are infinite. There is no lexicon reward,
destroyed-reference subtraction, injected word bonus, qok bonus, target term,
or hidden key prior.

The exact oracle is the twelve-panel product:

```text
LM      in {LM_A, LM_B}
DATA    in {TRAIN, HELD}
WEIGHT  in {EVENT, TYPE, FOCAL}
```

`EVENT` weights occurrences, `TYPE` gives each distinct source type equal
total weight, and `FOCAL` gives each of the 42 registered focal families equal
total weight. Forward-only and reverse-only results are mandatory sentinel
diagnostics. The primary blind-search objective is
`LM_A / TRAIN / EVENT`; no other panel is optimized.

Candidate mutation strings come only from `lm_fit`, ranked by substring
frequency and then lexical order, capped at 64 strings per role/length class.
The planted string and the named `que -> qua`, `q -> x`, and `in -> et`
sentinels are retained even at the cap. Carrier train or held words may not add
a candidate.

For each accepted world, score the planted truth and all of these alternatives
without optimization:

- every legal same-role/same-length one-value substitution of every nonempty
  output and every pair of disjoint one-value substitutions;
- every legal complete card swap within equal role and length;
- every legal role swap preserving the registered role histogram;
- delete, move, short/macro-type, output, and child/default mutations of every
  paid card;
- connector/context and short/macro confusions of compatible length;
- at least 100,000 deterministic legal multi-card near/far decoys;
- the six archived GDT612 pseudokeys where the V2 compiler can represent them.

Truth must be the unique rank one within `1e-9` total bit in every one of the
twelve panels. Every declared single-parameter mutation must lose with a
strictly positive margin in every panel; cross-panel averaging cannot rescue a
failure. Illegal mutations must have a named rejecting carrier.

The old exposed `que -> qua` improvement is a mandatory regression case. It
must lose by at least 0.05 bit per affected weighted word in every panel and
have positive forward-only and reverse-only margins under both LMs, or the
oracle gate fails. Ties, zero-exposure parameters, and truth-equivalent but
undeclared behavioral classes fail.

A matched `CORE_ORDER_NULL` hash-permutes resolved terms inside every
multi-core carrier while preserving modifiers, lengths, exposure, inventory,
and score orientation. It is a separate diagnostic, never subtracted from the
objective. Truth-order NLL must beat its null under both LMs in both train and
held; otherwise the model has no demonstrated compositional-order signal.

## Blind recovery gate

Only an oracle pass opens recovery. For each world run eight starts with seeds
`world_seed * 100 + 1..8`; initialization receives the grammar, tree,
candidate pools, `LM_A`, and observed train unit streams, but not the truth
mapping, labelled parse, train plaintext, held unit stream, or held plaintext.
Recovered keys are committed before held material is released; held decodes
are committed without refitting before truth is compared.

A world passes only when at least 7/8 starts recover the same exact behavioral
truth class, including 34/34 primitive role+output cards, 8/8 paid locations,
types and outputs, 64/64 merge behaviors, 100% of the labelled train and held
unit streams, and 100% of held plaintext chunks. Every exact recovery must
repeat under an independent validator. Matched destroyed-reference controls
must not recover the truth class.

All three worlds must pass. Any post-run repair requires a new experiment ID.

## Registered outcomes

- `TRUTH_GENERATOR_INFEASIBLE`
- `OBJECTIVE_NON_IDENTIFYING`
- `OPTIMIZER_INSUFFICIENT`
- `SYNTHETIC_RECOVERY_PASS`
- `IMPLEMENTATION_OR_VALIDATION_FAILURE`

Even `SYNTHETIC_RECOVERY_PASS` is only permission to preregister a target run;
it is not a Voynich decipherment or semantic claim.
