# GDT624 — the 48-word quality grammar

Status: **COMPLETE_48_CELL_SURFACE_LATTICE__COMPOSITIONAL_QUALITY_CORE_WORKING_READER**.

## Result

The strongest current reader is no longer limited to four `qo-` words. One
compact grammar generates 48 complete, observed forms:

```text
P + {k,t} + {ch,sh} + [e?] + [d?] + y
P ∈ {bare,o,qo}
```

All 48 cells occur in the 179-page guarded panel, together 829 times on 157
pages and 679 physical lines. Every cell has at least one locus where ZL3b,
IT2a, and RF1b retain the same complete token. The conservative shared-token
minimum is 613 occurrences. This is therefore a real productive surface
family, not a list assembled from transcription accidents.

The live slot reader is:

| Slot | Working value |
|---|---|
| `k` | hot |
| `t` | cold |
| `ch` | dry |
| `sh` | moist |
| `e` | quality binds forward / attributive form |
| `d` | grammatical DY binding or state closure |
| `y` | completion of the form |
| bare / `o` / `qo` | three scope wrappers around the same quality core |

`k/t` is still the weaker orientation and `ch/sh` the stronger one inherited
from GDT623. `e` may additionally carry degree or strength, especially when
repeated. `d` receives no invented verb: the local evidence makes a bare
operation such as heat, cool, dry, or moisten distinctly worse than a binding
or state-form reading.

## Complete-word defaults

The reader constructs every gloss rather than memorizing 48 unrelated words.
Representative forms are:

| Form | Short default |
|---|---|
| `kchy` | hot-dry, unmarked/predicative |
| `kchey` | hot-dry, forward-bound/attributive |
| `kchdy` | hot-dry state/binding form |
| `kchedy` | hot-dry state/binding form, forward-bound |
| `kshy` | hot-moist, unmarked/predicative |
| `tchey` | cold-dry, forward-bound/attributive |
| `tshdy` | cold-moist state/binding form |
| `okchey` | in the `o` frame: hot-dry, bound to what follows |
| `qotshy` | in the `qo` quality frame: cold-moist |
| `qokchedy` | `qo` quality frame: hot-dry, bound DY form |

`PRODUCTIVE_READER.tsv` supplies the corresponding default for all 48 forms;
none is left with a generic “perform work” placeholder.

## The count lattice

Counts are shown as KCH/KSH/TCH/TSH:

| Wrapper | `y` | `ey` | `dy` | `edy` |
|---|---:|---:|---:|---:|
| bare | 31/6/27/3 | 18/6/18/8 | 17/4/12/5 | 22/5/33/10 |
| `o` | 22/10/40/4 | 29/9/26/7 | 16/1/24/3 | 23/4/34/7 |
| `qo` | 64/9/61/5 | 25/8/18/2 | 49/4/21/3 | 39/10/24/3 |

The complete occupancy alone could still be scribal templating. The local
edges make it more useful. Ten of 24 possible `k↔t` edge types occur on the
same line, nine with a three-reading-stable witness. `ch↔sh` has five local
edge types, `e` insertion two, `d` insertion four, bare↔`o` three, and
`o`↔`qo` four. In total there are 45 same-line edge witnesses, thirty stable.

There are also 22 core×page cases containing all three wrappers. For example,
f13r and f22r each contain `kchy`, `okchy`, and `qokchy`; four separate pages
contain `kchedy`, `okchedy`, and `qokchedy`. The wrappers therefore behave much
better as scopes around one value than as unrelated whole-word meanings.

## First practical Herbal phrases

Six adjacent contacts on the eleven already inspected Herbal images connect
the quality grammar directly to GDT623's part words:

```text
f23v.4  okchey dair
         hot-dry, forward-bound + root/radix
       → “hot, dry root”
```

```text
f31v.3  okchey sair
       → “hot-dry root part”
```

```text
f39v.6  okchey shor
       → “hot-dry flower/fruit stand”
```

```text
f29v.1  kooiin shor chetchy
       → “thick/creeping-root drug; the flower/fruit stand is cold and dry.”
```

```text
f45v.1  korary ... shor ykchy
       → “reproductive drug ... flower/fruit stand: hot and dry.”
```

```text
f23v.6  shor shkshy
       → “flower/fruit stand: hot and moist.”
```

The last reading matters because f23v.4 describes the root on the same page as
hot-dry while f23v.6 describes the reproductive head as hot-moist. This is more
coherent as part-specific quality information than as one page-wide plant
temperament. It also explains why distant page-level attachment was misleading.

## What `e` and `d` most likely do

Three of the four exact `okchey` occurrences stand immediately before `dair`,
`sair`, or `shor`. Bare-y quality cores also occur after part words. The best
current distributional rule is therefore:

```text
o + QUALITY + ey + PART  → forward-bound or attributive quality
PART + P + QUALITY + y   → postposed or predicative quality
P + QUALITY + dy         → grammatically bound state/closure form
```

The separate e-length census is genuinely productive. Among its clearest
series:

```text
chdy / chedy / cheedy = 133 / 470 / 56
shdy / shedy / sheedy =  40 / 390 / 77
okedy / okeedy / okeeedy = 87 / 94 / 7
otedy / oteedy / oteeedy = 131 / 88 / 2
```

f116r.10 contains `shdy`, `shedy`, and `sheedy` on one line, all three retained
by all readings. Repeated `e` is therefore an ordered expansion slot. Whether
the order is stronger binding, degree, or a related grammatical grade remains
open; the current reader says “extended e-binding” rather than inventing
degree I/II/III.

The historical comparison supports exactly this ranking. Early-fifteenth-
century Wellcome MS.542 f118r puts grammatically different hot/dry adjective
forms beside different drug head constructions. Pal.lat.1234 puts quality and
degree rubrics before the name lists they govern. Wellcome MS.541 and Clm667
show compact invariant quality codes followed by explicit degree material.
Pal.lat.1085 supplies an older tabular calibration with name, temperature,
moisture, and degree fields. Thus both attribution and degree are historically
real; the Voynich local position makes forward binding the better first
default for `e`.

## Concrete line excerpts

The reader also makes formal contrasts legible:

```text
f42v.2  ... tchey ... kchey ...
       → ... cold-dry [bound] ... hot-dry [bound] ...
```

```text
f85r1.5 tchedy kchedy ... okchy ...
       → cold-dry bound state; hot-dry bound state; ... hot-dry ...
```

```text
f107v.38 ... okchey qokchey ...
        → ... o-frame hot-dry [bound]; qo-frame hot-dry [bound] ...
```

Every unassigned surface remains visible in angle brackets in the artifact
edition. This prevents the old failure where fluent generic prose concealed
zero lexical information.

## Boundary and next move

GDT624 establishes one complete working family and six concrete part-quality
phrases. It does not yet turn state order into verbs. The next useful move is
to follow repeated local sequences such as cold-moist → cold-dry and ask
whether the relation between the two states means drying, while preserving
each individual quality word unchanged. In parallel, the same adjacency rule
can search already inspected heads for leaf, seed, whole-herb, liquid, and
vessel part words.
