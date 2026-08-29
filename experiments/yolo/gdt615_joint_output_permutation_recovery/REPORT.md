# GDT615 Stage-0 report — the joint binding clears the necessary bound

Date: 2026-08-29

## Decision

`STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN`

The complete registered same-role card-permutation space has one canonical
optimum under the prospective train-only hierarchy. It places 55/64 directed
merge renders directly inside the 28,101 frozen train substrings. The nine
remaining merges have an exact inclusive-DAG cover minimum of four, below the
registered maximum of eight. This opens Stage 1; it does not establish that a
complete grammar world exists.

The immutable Stage-0 mapping commit is
`edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262`.
Every Stage-1 process must consume that exact hash. No next-best mapping is
available inside GDT615 if a downstream gate fails.

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

## Scope and next step

No held, LM-confirm, Voynich target, f84, or f84r data entered Stage 0. No
Voynich unit, language, word, plaintext, object, operation, or meaning is
assigned here.

Stage 1 must now use train only to choose exactly eight legal paid locations,
assign the fixed four short and four macro cards, and construct all ordered
traces and top-level tilings for W0. Stage 2 must construct W1 and W2. The
complete three-world bundle and actual paid locations must be hash-committed
before held is opened once. A failure ends GDT615; it cannot trigger a second
Stage-0 binding.

## Reproduction

Install `z3-solver==4.15.3.0` and a C++20 compiler, then run:

```bash
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/run.py \
  --output-root gdt615-stage0-reproduction
python3 experiments/yolo/gdt615_joint_output_permutation_recovery/src/validate.py
```

The stable public bundle is listed in `artifacts/stage0/STAGE0_BUNDLE.json`;
transient timing diagnostics, PIDs, compiler binaries, and duplicate work
directories are deliberately excluded.
