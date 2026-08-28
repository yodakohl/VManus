# GDT613 — observation-complete FST34 recovery

Date: 2026-08-28

Decision: **`MODEL_SCOPE_UNDERSPECIFIED_OR_INFEASIBLE`**

## Result

The registered natural-Latin recovery worlds cannot be constructed.  Two
independent necessary conditions fail before a truth output, language-model
score, optimizer start or Voynich target is allowed.

First, the literal flattened-piece reading of the published GDT609 EBNF is
structurally unsatisfiable together with the registered coverage gates.  The
exact solver assigns the fixed `18/4/3/3/2/2/1/1` role deck, exactly four short
cards as syllabic cores and four whole cards, recursively composes all 64
GDT608 merges and forbids exact `qok` as a whole card.  No assignment can make
every non-card direct composition and every paid card's unoverridden child
composition embeddable in a legal chunk.  The primary formula is `UNSAT`; the
stronger sensitivity that forbids every `qok*` whole card is also `UNSAT`.

Dropping only the paid-card child-counterpart gate makes the same formula
`SAT`.  Its fixed control witness has exact role/card counts and 56 legal
non-card compositions, but it hides five illegal child routes behind cards:

- `daN`: `SUFFIX CONNECTOR SYLLABIC`
- `dal`: `SUFFIX CONNECTOR CONTEXT`
- `dar`: `SUFFIX CONNECTOR LITERAL`
- `air`: `CONNECTOR LITERAL LITERAL`
- `daI`: `SUFFIX CONNECTOR SYLLABIC`

This localizes the contradiction to the combined exact grammar and coverage
contract.  It is not a search failure and cannot be repaired by more examples,
Latin strings or optimizer starts.

A stricter supplemental diagnostic expands every merge all the way to raw
primitive leaves, without collapsing paid descendants.  At most 60/64 raw
merge sequences can be embedded: `>=61` is unsatisfiable, while a fixed 60
witness exists.  In every 60-solution the four excluded sequences are
`daN/dal/dar/daI`; their shared optimum roles begin
`SUFFIX CONNECTOR ...`, which the exact grammar cannot continue with a core.
This bound is explanatory rather than the registered card-aware formula.

Second, the frozen output-length deck is already too small for collision-free
natural Latin.  It requires 23 distinct one-character outputs: eighteen
literals plus one syllabic, prefix, suffix, connector and context value.  The
frozen train/held Latin blocks contain only 22 different letters, and only 21
occur in at least eight train word types and sixteen held events.  At least two
functional length-one cards must move to length two before the registered
exposure threshold is even arithmetically possible.

The five scored whole parameters fail the same exposure contract for a
different reason.  Under the published `CONNECTOR? WHOLE CONNECTOR?` envelope,
an exhaustive generous search over every eligible one- and two-character
connector gives maximum train-word-type coverage of only 5/4/3/3 for whole
outputs of length 3/4/5/6.  The primitive length-four whole and all four paid
whole cards therefore miss the required eight train word types even before
held exposure or collisions are imposed.  Merely changing `CORE` to a run does
not fix this; a successor must either type whole cards as embeddable macro
cores or explicitly weaken the observation contract.

## Grammar-scope bridge

The old GDT612 planted world independently exposes the same scope mismatch.
Under exact flattened GDT609 grammar only 1,922/14,553 train events (13.21%)
and 505/3,639 held records (13.88%) are legal.  An explicitly unregistered
diagnostic that permits adjacent complete cores raises this to 14,461/14,553
(99.37%) and 3,562/3,639 (97.88%).  The remaining train failures all contain
an interior null; the held remainder contains seventeen interior-null cases
and sixty deliberately malformed context-exposure probes.

That discontinuity nominates a separately versioned core-run grammar.  It does
not retroactively change GDT609 or turn the old planted key into evidence.

## Objective bridge

A separate post-run audit removes GDT612's destroyed-language subtraction,
lexicon reward, grammar costs and key prior.  Pure real-Latin character
cross-entropy then ranks planted truth first against all six archived
pseudokeys in every legacy and reset-matched panel.  It still does not identify
the exact key: among 1,888 fixed-length one-primitive mutations, exposed
`P28 que→qua` beats truth in every primary panel, while 232 ties are exactly
the mutations of the four zero-train-exposure primitives `F/K/f/i`.

Thus the generative score is a major correction but not sufficient on the old
incomplete world.  `objective_bridge/` contains its preregistration, source,
validator, report and compact validated artifacts; the 15 MB exhaustive score
table is reproducibly generated but deliberately not committed.

## Consequence

GDT613 stops before its oracle and recovery gates.  It neither passes nor fails
a target decoder, and it does not test the larger GDT609 soft-count family.
The exact parser, directed tree checks, disjoint reference splits and language
model implementation remain reusable.

The next experiment must name a new grammar, use a length deck with enough
eligible natural-Latin values, reconstruct the observation-complete worlds and
then repeat oracle ranking and multi-start recovery.  No Voynich target may be
opened before those synthetic gates pass.

## Reproduction

Install the pinned solver and run:

```text
python3 -m pip install -r experiments/yolo/gdt613_observation_complete_fst34_recovery/requirements.txt
python3 experiments/yolo/gdt613_observation_complete_fst34_recovery/src/run.py
python3 experiments/yolo/gdt613_observation_complete_fst34_recovery/src/validate.py
```

The validator independently replays all three structural queries, checks the
fixed relaxed witness, exhaustively compares the parser with all 299,592 role
strings through length six, and checks the old-world scope bridge and Latin
length-deck capacity.

## Claim ceiling

This result rejects only the registered exact flattened-piece grammar plus its
simultaneous merge/card-child coverage gates and fixed natural-Latin length
deck.  It assigns no Voynich unit, output, sound, language, plaintext, word or
meaning and reads no f84/f84r material.
