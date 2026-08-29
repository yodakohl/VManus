# GDT615 report — the joint binding clears Stage 0 but cannot form W0

Date: 2026-08-29

## Decision

`MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE`

The complete registered same-role card-permutation space has one canonical
optimum under the prospective train-only hierarchy. It places 55/64 directed
merge renders directly inside the 28,101 frozen train substrings. The nine
remaining merges have an exact inclusive-DAG cover minimum of four, below the
registered maximum of eight. That Stage-0 result opened Stage 1, but the fixed
mapping cannot satisfy Stage 1's paid-child counterpart gate. No complete W0
train world exists under the registered contract.

The immutable Stage-0 mapping commit is
`edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262`.
Every Stage-1 process consumed that exact hash. No next-best mapping is
available inside GDT615 after the downstream gate failed.

## Terminal Stage-1 bound

The failure is the two-case contradiction at merge rank 14, `Ey`:

- the fixed primitive mapping gives `E→ho` and `y→i`, so its unoverridden
  direct child composition is `hoi`;
- `hoi` is absent from the complete 28,101-entry train-substring table;
- `Ey` is raw-unsupported and its inclusive recursive merge subtree is the
  singleton `{14}`, so coverage forces rank 14 to be an actual paid location;
- a paid location must directly expose its unoverridden child composition,
  so the missing `hoi` span forbids rank 14 from being paid.

The primary Boolean/Z3 model reports UNSAT with the subset-minimal core
`E14_paid_requires_train_child_span` plus
`U14_raw_unsupported_requires_paid_subtree`. Dropping either clause is SAT.
A separately implemented combinatorial proof reaches the same contradiction
even after admitting every other node and omitting paid-card roles, outputs,
licenses, grammar, and tiling. A third contract-only two-case audit confirms
that both the default and paid readings fail and that the only readings which
avoid the result change a registered gate.

This necessary bound is more permissive than the full Stage-1 solver. Its
UNSAT result therefore terminates GDT615 without selecting actual paid
locations or constructing W0, W1, or W2. Held, LM-confirm, oracle, recovery,
Voynich target data, f84, and f84r were not opened.

## Exact optimum

The fixed objective order was:

1. maximize raw train-substring support over all 64 named merges;
2. minimize the exact inclusive merge-subtree cover;
3. minimize the 34-card ID sequence in registered primitive order;
4. minimize the ascending cover-rank tuple.

The optimum is 55 raw-supported merges and cover minimum four. Support 56 is
UNSAT; at support 55, cover three is UNSAT. With both values fixed, every
lexicographically earlier mapping is UNSAT. With the mapping fixed, every
earlier four-rank cover tuple is UNSAT.

The canonical relaxed cover is:

| rank | merge |
|---:|:---|
| 2 | `ok` |
| 3 | `ol` |
| 14 | `Ey` |
| 23 | `ai` |

This tuple is a necessary-bound certificate only. It is not a choice of actual
paid locations or cards.

## Frozen mapping

These strings are synthetic Latin-carrier output cards. They are not Voynich
sounds, words, stems, or meanings.

| primitive | role | card | output |
|:---|:---|:---|:---|
| `C` | null layout | N01 | empty |
| `E` | syllabic carrier | Y03 | `ho` |
| `F` | connector | K01 | `um` |
| `I` | suffix operator | S03 | `tur` |
| `K` | literal carrier | L02 | `b` |
| `N` | syllabic carrier | Y01 | `q` |
| `P` | literal carrier | L03 | `c` |
| `S` | prefix operator | P01 | `h` |
| `T` | connector | K02 | `in` |
| `a` | literal carrier | L01 | `a` |
| `b` | literal carrier | L05 | `f` |
| `c` | syllabic carrier | Y02 | `hi` |
| `d` | literal carrier | L09 | `m` |
| `e` | literal carrier | L16 | `u` |
| `f` | literal carrier | L06 | `g` |
| `g` | prefix operator | P02 | `pr` |
| `h` | literal carrier | L08 | `l` |
| `i` | context abbreviation | C01 | `nt` |
| `j` | literal carrier | L10 | `n` |
| `k` | literal carrier | L13 | `r` |
| `l` | context abbreviation | C02 | `re` |
| `m` | suffix operator | S01 | `d` |
| `n` | macro core | M01 | `ibus` |
| `o` | literal carrier | L04 | `e` |
| `p` | literal carrier | L11 | `o` |
| `q` | literal carrier | L12 | `p` |
| `r` | syllabic carrier | Y04 | `que` |
| `s` | literal carrier | L15 | `t` |
| `t` | literal carrier | L14 | `s` |
| `u` | suffix operator | S02 | `us` |
| `v` | literal carrier | L17 | `v` |
| `x` | prefix operator | P03 | `pro` |
| `y` | literal carrier | L07 | `i` |
| `z` | literal carrier | L18 | `x` |

## The nine unsupported raw renders

| rank | merge | raw render | covered by canonical relaxed node |
|---:|:---|:---|:---|
| 14 | `Ey` | `hoi` | `Ey` |
| 38 | `air` | `antque` | `ai` |
| 45 | `Sol` | `here` | `ol` |
| 46 | `qokaN` | `peraq` | `ok` |
| 47 | `qokEdy` | `perhomi` | `ok`, `Ey` |
| 49 | `qokedy` | `perumi` | `ok` |
| 53 | `CEy` | `hoi` | `Ey` |
| 59 | `qokEy` | `perhoi` | `ok`, `Ey` |
| 60 | `okaN` | `eraq` | `ok` |

## Independent evidence

The primary Python/Z3 model used 3,690 base assertions and a reduced
3,493-node/14,120-arc MDD. Its 193-query boundary proof was repeated with
byte-identical deterministic outputs.

A separately written C++20 implementation did not import the primary model.
It exhaustively completed all 1,728 nonliteral-role tasks, searched the eleven
objective-relevant literal slots, directly replayed its winner, and returned
the same full mapping, supported-rank set, 55/4 objective, and cover tuple
`[2,3,14,23]`. Its independent exhaustive miniature-DAG cover test also
passes. The old positional GDT614 binding replays in both implementations at
25/64 support and exact minimum 15, matching the registered negative control.

The earlier 1,490,756-evaluation scout also found 55/4 repeatedly, but it did
not prove optimality and did not select the lexicographically canonical key.
It is published only as auxiliary search history.

## Scope and consequence

No held, LM-confirm, Voynich target, f84, or f84r data entered Stage 0. No
Voynich unit, language, word, plaintext, object, operation, or meaning is
assigned here.

GDT615 ends here. It cannot try a second Stage-0 binding. A successor may use a
new experiment ID to choose the primitive mapping jointly with the newly
identified paid-child eligibility condition; that would be a genuinely
stronger search, not a reinterpretation of this result.

## Reproduction

Install `z3-solver==4.15.3.0` and a C++20 compiler, then run:

```bash
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/run.py \
  --output-root gdt615-stage0-reproduction
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/stage1/primary_bound.py \
  --output experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/stage1/PRIMARY_RESULT.json
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/stage1/independent_bound.py
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/stage1/contract_audit.py \
  --output experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/stage1/CONTRACT_AUDIT.json
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/validate.py
```

The stable public bundle is listed in `artifacts/stage0/STAGE0_BUNDLE.json`;
the terminal evidence bundle is `artifacts/stage1/STAGE1_BUNDLE.json`.
Transient timing diagnostics, PIDs, compiler binaries, and duplicate work
directories are deliberately excluded.
