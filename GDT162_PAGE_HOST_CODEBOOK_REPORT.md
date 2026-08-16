# GDT162 — short PAGE_HOST codebook report

Decision: **SHORT_HOST_INTERNAL_PRODUCTIVITY_INTERESTING**.

## Bottom line

The **pure opaque-codebook** version is not supported.  Exact PAGE_HOST
identity is much more predictive than a one-glyph-neighbor backoff, so host
identity plainly matters; however the same inventory has a denser Hamming-one
graph than its position-preserving null, and those neighbors transfer outer
context and substitution-direction effects.  The strongest descriptive model
is therefore an **identity-bearing but internally structured short-host
system**, not 241 arbitrary independent addresses.  The frozen strict codebook
label also fails because Voynich's 2–3-character concentration does not exceed
all primary historical graphematic controls.

## Short-host inventory

After rejecting 228 f84v rows before retention, the frozen HPR2
panel contains 15,364 non-f84 group occurrences on
93 physical folios.  PAGE_HOST length
2–3 accounts for 38.1% of occurrences and
12.9% of types.  Within that short-host
panel, 98.5% of occurrences use a
recurrent identity and 98.4%
use an identity observed on multiple physical folios.

The raw unstripped source-display comparison has
13.9% length-2/3
mass.  The closest frozen historical control by this single coordinate is
`LATIN_GERMAN_APOTHECARY_LATE15` at
35.4%.  Length concentration
is not treated as sufficient evidence by itself.

## Positional inventories and slot dependence

| length | weighting | position inventories | position entropies (bits) | position↔glyph MI | total correlation |
| ---: | --- | --- | --- | ---: | ---: |
| 2 | TYPE | `acdekloprsty|adefghiklmnoprsty` | 3.414336408366|3.822538680700 | 0.1210 | 1.1925 |
| 2 | TOKEN | `acdekloprsty|adefghiklmnoprsty` | 2.064985718630|2.960917829329 | 0.5937 | 1.1491 |
| 3 | TYPE | `acdefikloprsty|acdefghiklmopqrsty|adefghiklnorsty` | 3.307575173622|3.721613659406|3.600564284214 | 0.1946 | 3.1785 |
| 3 | TOKEN | `acdefikloprsty|acdefghiklmopqrsty|adefghiklnorsty` | 2.769765700304|3.079377333142|3.104633869709 | 0.5337 | 3.2681 |


The mean type-weighted total correlation across lengths 2 and 3 is
2.185511 bits, below the
position-preserving null mean 2.432377.  This is not a
compact-slot excess: after preserving positional inventories, randomized type
codes are more dependent because collisions remove distinct combinations.
The observed inventory is instead unusually injective and densely connected;
those properties must not be conflated with a small factorial code.

## Exact identity versus one-glyph neighbors

Across leave-one-physical-folio folds and all six outer compiler components,
exact PAGE_HOST identity changes the nuisance code by
+10636.305 bits.  Hamming-one neighbor
backoff changes it by +3037.383 bits;
exact identity therefore leads neighbor backoff by
+7598.923 bits.  The leave-one-section-out
sensitivity is exact +11529.813 and
neighbor +4345.302 bits.

This is the cleanest codebook-versus-productivity diagnostic in the pass.
Exact-identity gain cannot be read semantically: the HPR2 parser itself strips
licensed outer fields, so formal host/context coupling is partly architectural.

| held-folio component | exact-host gain (bits) | neighbor gain (bits) | positive exact folds | positive neighbor folds |
| --- | ---: | ---: | ---: | ---: |
| `wrapper` | +3677.734 | +1484.107 | 89/92 | 70/92 |
| `inner_d` | +25.307 | -79.708 | 25/92 | 17/92 |
| `local_frame` | +1453.544 | +356.199 | 90/92 | 65/92 |
| `right_family` | +3148.012 | +933.253 | 90/92 | 57/92 |
| `dy_closure` | +1961.913 | +226.348 | 66/92 | 45/92 |
| `b3` | +369.795 | +117.184 | 89/92 | 65/92 |


## Slot and neighbor geometry

The 2–3-character inventory contains 933 Hamming-one
type pairs, density 0.053713 versus the
position-preserving null mean 0.039437
(local/max-family p 0.000976/
0.000976).  Mean neighbor
outer-context cosine is
0.911518; mean repeated-substitution
context-delta coherence is
0.400454 over
1,701 within-class edge comparisons.
Against the position-preserving null, their local p-values are
0.000976 and
0.000976; max-family p-values are
0.000976 and
0.000976.

The largest recurrent neighbor pairs by combined occurrence are:

| pair | substitution | occurrences | folios | context cosine |
| --- | --- | ---: | ---: | ---: |
| `ok ~ or` | `L2:P2:k>r` | 1343 | 69/86 | 0.8596 |
| `ok ~ ot` | `L2:P2:k>t` | 1270 | 69/61 | 0.9831 |
| `or ~ ot` | `L2:P2:r>t` | 935 | 86/61 | 0.8767 |
| `ok ~ ol` | `L2:P2:k>l` | 910 | 69/42 | 0.6851 |
| `lk ~ ok` | `L2:P1:l>o` | 900 | 17/69 | 0.9293 |
| `ok ~ yk` | `L2:P1:o>y` | 894 | 69/32 | 0.9328 |
| `ok ~ os` | `L2:P2:k>s` | 886 | 69/33 | 0.8717 |
| `ok ~ op` | `L2:P2:k>p` | 863 | 69/18 | 0.9739 |
| `ar ~ or` | `L2:P1:a>o` | 854 | 69/86 | 0.9907 |
| `ek ~ ok` | `L2:P1:e>o` | 850 | 9/69 | 0.9254 |
| `of ~ ok` | `L2:P2:f>k` | 849 | 7/69 | 0.9615 |
| `ak ~ ok` | `L2:P1:a>o` | 842 | 3/69 | 0.9374 |


These are formal neighbors, not morpheme pairs.  High similarity is a
counterexample to wholly independent identities; low or incoherent
substitution deltas are counterexamples to a uniform productive operation.

## Historical controls

| representation | tokens | 2–3 mass | recurrent coverage | cross-fold coverage | neighbor density |
| --- | ---: | ---: | ---: | ---: | ---: |
| `VOYNICH_PAGE_HOST` | 15364 | 0.381 | 0.985 | 0.984 | 0.053713 |
| `VOYNICH_RAW_TOKEN` | 15364 | 0.139 | 0.969 | 0.968 | 0.067160 |
| `IFORAL_1395_1411_GRAPHEMATIC` | 6104 | 0.432 | 0.942 | 0.924 | 0.033535 |
| `LATIN_15C_GRAPHEMATIC` | 12000 | 0.288 | 0.909 | 0.882 | 0.023490 |
| `LATIN_GERMAN_APOTHECARY_LATE15` | 1554 | 0.354 | 0.824 | 0.776 | 0.030895 |
| `LATIN_MEDICAL_GRAPHEMATIC` | 12000 | 0.344 | 0.896 | 0.849 | 0.019419 |
| `LATIN_SCHOLASTIC_GRAPHEMATIC` | 11317 | 0.498 | 0.932 | 0.902 | 0.019785 |


The diplomatic controls calibrate ordinary abbreviated graphematic forms; they
do not share the Voynich HPR2 parser or outer compiler fields.  Script,
normalization, genre, and transcription practice remain confounds.

## Interpretation and counterevidence

The result is an exploratory architecture ranking.  GDT003's string-statistical
ceiling, GDT123's failed exact-host visual atlas, and GDT161's failed compact
operation classes remain binding counterevidence.  Outer LEFT/RIGHT material
was never folded into candidate host strings.  No host is assigned a word,
lexical value, number, morpheme, phoneme, language, semantic role, meaning,
plaintext, or translation.

No f84 row was retained or scored.  f84r is absent from the actual source
input and was not opened, queried, retained, joined, or scored.
