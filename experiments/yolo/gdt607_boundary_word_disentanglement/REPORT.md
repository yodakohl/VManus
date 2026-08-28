# GDT607 — boundary/word-bucket disentanglement

## Decision

**`W_BUCKET_CONFUND_CORRECTED__FIVE_DISTINCT_OUTPUT_BEARING_FORMAL_ROLES`**

GDT606's `W` category is not an observed whole-word class. It is primarily a
frequency- and mobility-weighted output-capacity bucket. The five recurring
targets are mutually distinguishable formal carriers, and a dedicated
outputless boundary class does not absorb them. The stable information is
their orientation and scope, not any generated plaintext value.

## Why the original `W` reading fails

Across all 98 units, all-real `W` membership correlates with log frequency at
Spearman 0.73065 and effective-neighbour count at 0.61081, but negatively with
literal standalone hard-chunk rate at -0.13513. Non-target `ar`, `s`, `or`,
and `k` enter `W` in 31--34 of 36 real runs. Conversely, five `qok`-family
units are complete one-unit hard chunks in 97.2--98.9% of pooled occurrences
but enter `W` in 0/36 real runs.

The five target identities are recoverable from held context with balanced
accuracy 0.6456 versus a conditional permutation mean of 0.3221
(`p=0.004975`). Local neighbours alone reach 0.6493, metadata alone 0.2224,
and all ten pairwise held AUCs are 0.8502--0.9875. One exchangeable semantic
or functional class is therefore untenable.

## Explicit boundary grid

Ninety complete keys exchange the eleven original `W` slots for an outputless
`B` category: `B0/W11`, `B3/W8`, `B6/W5`, `B8/W3`, and `B11/W0`, with six
starts in each of three reference languages.

Across the 72 runs that contain `B` slots, category counts for the targets are:

| unit | `B` assignments | `W` assignments at `B8/W3` (18 runs) | result |
|---|---:|---:|---|
| `o` | 0 | 7 | output-bearing flexible connector |
| `y` | 0 | 16 | output-bearing closure carrier |
| `ol` | 0 | 13 | output-bearing boundary/standalone carrier |
| `C` | 4 | 5 | predominantly output-bearing local opener |
| `d` | 4 | 5 | predominantly output-bearing chunk/line head |

With `W=0`, all five predominantly enter the multi-character `S` category;
they do not become empty delimiters. Pure `B` assignments themselves are
restart-unstable: at `B3/W8` no unit is `B` in all six starts for any language.
The language-model margin also falls sharply as output capacity is replaced by
empty boundaries, showing that the original optimizer used `W` mainly as a
high-capacity output macro class.

## Retained formal defaults

| unit | formal default | held anchors |
|---|---|---|
| `C` | strict local hard-chunk opener | initial 0.6934; final 0.0056 |
| `d` | hard-chunk and physical-line head carrier | chunk-initial 0.4992; line-initial 0.1759 |
| `y` | chunk/line and weak paragraph closure carrier | chunk-final 0.6390; line-final 0.2347 |
| `ol` | boundary and occasional standalone carrier | chunk-final 0.5463; standalone 0.1433 |
| `o` | flexible bidirectional connector | initial 0.3120; final 0.2989; middle 0.4154 |

Train and held directions agree. Every target occurs on every held folio;
section, hand, and Currier association is weak compared with local position.
Thus these are manuscript-wide formal defaults, not folio labels.

## Consequence for decoding

The 98 BPE units must not be treated as 98 unrelated code signs. Several
frequent units are explicit compositions in the frozen merge tree: `ol=o+l`,
`or=o+r`, `ok=o+k`, `ot=o+t`, `dy=d+y`, and `aN=a+N`. The next decoder must
fit shared component roles—opener, closer, connector, internal macro,
whole-form, and null—then charge output length and codebook complexity. Only
carrier-stable values that survive synthetic recovery and held transfer can be
promoted to candidate meanings.

The detailed 153-check role audit, all 10,277 target events, matched controls,
classifier tables, and exact selector list are retained under
`artifacts/role_attack/`. The boundary arm retains all 8,820 unit assignments
from the 90 complete keys.
