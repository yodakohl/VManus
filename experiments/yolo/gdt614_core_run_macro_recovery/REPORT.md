# GDT614 report — the fixed V2 world needs at least 18 paid subtrees

Date: 2026-08-29

## Decision

`TRUTH_GENERATOR_INFEASIBLE`

The registered design world cannot expose all 64 named merges in both frozen
Latin partitions with eight paid cards. The exact necessary minimum is 18.
This stops GDT614 before joint parsing, three-world generation, oracle scoring,
blind recovery, and every Voynich target operation.

## Exact pre-world bound

A directly emitted source unit occupies a contiguous interval in its decoded
word. Therefore its render must at least occur as a substring in that word.
This remains necessary even before applying grammar, macro-side, collision,
transition, or unique-parse constraints.

Under the prospectively fixed primitive assignment:

- 19/64 raw merge renders occur in at least one train type and one held event;
- 45/64 miss one or both partitions;
- a failing node's raw render can change only if that node or a recursive merge
  descendant receives a paid card;
- covering all 45 failing nodes by such paid subtrees is an exact hitting-set
  problem over the registered 64-node directed tree.

The solver proves the covering formula UNSAT with at most 17 paid nodes and
SAT with exactly 18. A deterministic minimum witness is:

```text
dy ok ol aN Ce ot ar al or Se aI Ey ai ey yk yt Ty Sy
```

The registered capacity is eight, ten below the necessary minimum. In
particular, the exact eight-card formula is UNSAT.

## Why this is a strong stop

The bound deliberately grants the model more freedom than GDT614:

- it ignores the complete grammar and all 21 transition requirements;
- it ignores macro side licenses and the qok-macro prohibition;
- it ignores output collisions and short-versus-macro card types;
- it ignores all paid-child counterpart requirements;
- it asks only for substring presence, not a legal ordered parse or a
  nonoverlapping 98-unit tiling.

Every omitted condition can only remove solutions. Thus a later parser or
optimizer cannot rescue the registered fixed mapping.

## What the near-repair result did and did not establish

The earlier post-hoc candidate correctly showed 41 collision-free nonempty
card outputs and simultaneous 8/16 card-level potential exposure. Its selected
parse artifact was a card bit-mask: it discarded order, multiplicity, spans,
unit identity, and real NULL placement. Its separate 64/64 witness certified
role-sequence legality only. GDT614 is the first pass to join the fixed outputs
to the named merge tree, and that join fails before ambiguity matters.

## Consequence and next route

Do not raise the paid-card budget from eight to eighteen merely to preserve an
arbitrary primitive/output binding. The next version must choose the
within-role primitive/output permutation jointly with the 64-merge carrier
bound, while retaining the fixed deck, role counts, eight paid cards, direct
merge exposure, historical macro licenses, and later oracle/recovery gates.
Only a prospectively frozen mapping whose exact minimum hitting number is at
most eight may enter the expensive ordered-trace solver.

This result assigns no Voynich unit, word, sound, language, plaintext, object,
operation, or meaning and uses no f84/f84r material.

## Reproduction

```bash
python3 experiments/yolo/gdt614_core_run_macro_recovery/src/run.py
python3 experiments/yolo/gdt614_core_run_macro_recovery/src/validate.py
```

The generator repeats byte-identically. The independent validator rederives
all raw renders and supports, proves `<=17` UNSAT and the published 18-node
witness SAT, and passes 398/398 checks.
