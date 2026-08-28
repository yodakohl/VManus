# GDT613 prospective execution contract

Date: 2026-08-28

This contract precedes the new observation-complete truth worlds and recovery
runs. The seven-key GDT612 rescore is explicitly a post-run bridge diagnostic
and cannot count as prospective recovery.

## Inputs and exclusions

- bind GDT608's 98-unit directed merge tree and GDT609's `model_v1.json`;
- bind a hash-pinned normalized Latin reference and partition it before keys;
- no Voynich target train or held sequence in the fitter;
- no f84/f84r selector or material;
- no word candidates, exact-word bonus, aligned plaintext, truth mapping or
  target glossary in optimization.

The Latin reference is split into contiguous blocks for LM fit, LM confirmation,
synthetic train plaintext and synthetic held plaintext. The manifest records
each block and rejects repeated long token windows across partitions.

## Truth worlds and observability

Generate three deterministic independent FST34 truth worlds. Nonempty output
strings are unique unless a declared behavioral equivalence makes identity
unavoidable. Before a world is accepted, its certificate must show:

- every one of 34 primitive cards directly used in train and held;
- every one of eight paid merge cards directly used in train and held;
- every paid merge's unoverridden child composition also represented;
- prefix, suffix, connector, context, wholeform and null each exercised in
  every legal transition implemented;
- null train mass between 0.5% and 2.5%, below the model's 3% ceiling;
- each scored parameter in at least eight train word types and sixteen held
  events;
- every non-card merge unit used compositionally at least once in train.

World generation rejects a seed rather than weakening these thresholds.

## Fixed output-length cards

```text
literal       18 × 1
syllabic       1,2,2,3
prefix         1,2,3
suffix         1,2,3
connector      1,2
context        1,2
wholeform      4
null           0
override-short 2,2,3,3
override-whole 3,4,5,6
```

If this multiset cannot produce three certified natural-Latin worlds, GDT613
reports infeasibility; it does not silently retune lengths inside a scored run.

## Oracle gate

Before blind recovery, score truth against all legal single-character output
mutations, all legal complete role-card swaps, delete/move/type/output mutations
of every paid card, at least 100,000 deterministic legal near/far decoys and
the six old GDT612 keys where capacity is comparable.

Truth must rank first on the fit objective and independent confirmation block.
Every truth parameter needs a positive confirmation gap, and each declared
single mutation must lose in at least six of eight synthetic-train blocks. A
failed oracle gate stops recovery and forbids target use.

## Recovery gate

For each of three accepted worlds, run eight independent starts:

- at least 7/8 starts recover the exact behavioral truth class;
- modal recovery is 34/34 primitive role+output cards and 8/8 merge cards;
- every exact recovered key decodes 100% of synthetic held chunks;
- no paired destroyed-reference fit recovers the truth class;
- the result repeats in all three worlds.

Oracle pass plus recovery failure licenses optimizer work only. Full recovery
licenses a later separately registered target experiment, not a meaning claim.
