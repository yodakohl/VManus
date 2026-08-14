# Q20P001 Q20 phoneme-mapping method

Status: `FROZEN_BEFORE_Q20_TARGET_SCORING`

Date: 2026-08-14

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question

Does a training-folio-learned mapping from source-native Voynich STA member
codes to phoneme tokens predict held Q20 folios better under the ASJP profiles
of Georgian, Mingrelian, Laz, or Svan than under eight unrelated controls?

This is a phonotactic compatibility test. It never optimizes word identity,
glosses, translations, cognates, morphemes, POS, or recognizable strings.

## Voynich corpus and folds

Q20 is frozen to physical folios `f103`--`f108` and `f111`--`f116`. A source
group is eligible only when ZL3b, IT2a, and RF1b have byte-identical
`primary_sta_codes` and the same source-group topology. The three readings are
alternate observations of one manuscript and contribute one sequence. Source
groups reset the external word model; manual separators are retained as the
group boundaries but are not declared linguistic words.

There are twelve leave-one-physical-folio-out folds. The held folio is removed
before mapping initialization, search, tie-breaking, and all Voynich-fitted
baselines. f84r is rejected by routing key before any formal field can enter
the experiment and remains sealed.

## External phonotactic models

The twelve ASJP v21 core-40 lists and inventories are frozen in the external
source audit. Each language receives one order-2 phoneme KT model with two BOS
states, an EOS event, and symmetric alpha `0.5` over the language inventory
plus EOS. No ASJP gloss or source word is loaded by the runner.

## Mapping family and search

Every observed STA member code maps to exactly one phoneme token from the
candidate language inventory. Multiple source codes may map to the same
phoneme; deletion, insertion, multigraph emission, spaces, exceptions, and
context-dependent keys are forbidden. The mapping is therefore explicit but
not reversible, and no decipherment or plaintext reconstruction is claimed.

For each language and outer fold, optimize the training phonotactic bits plus
the full mapping-key charge `G*log2(M)`, where `G` is the fixed source-code
inventory and `M` the candidate phoneme inventory. The key charge is constant
within a language but is reported for cross-language MDL transparency.

Search uses exactly three SHA-seeded starts and at most ten exact coordinate
descent sweeps. Each coordinate proposal tests every phoneme using sufficient
source trigram counts. Retain the lowest training total, then the
lexicographically smallest complete mapping. `cpu_exact` means exact rescoring
of a retained local optimum, not globally exact optimization.

The primary predictive score is held phonotactic bits per source member,
without charging the training-derived key again. Also report a conservative
per-fold adjusted score that adds the full key to the held payload.

## Baselines and controls

For every fold report:

- source-native STA order-2 KT fitted on training folios;
- a whole-group KT dictionary with an escape whose unseen forms are encoded by
  the source STA order-2 KT;
- 128 deterministic random many-to-one mappings for each external language;
- all eight unrelated language profiles fitted with exactly the same mapping
  family and search budget.

Primary family specificity compares the aggregate held bits/member of the four
Kartvelian profiles with the eight controls. An exact `C(12,4)=495` label-set
test reports how often an arbitrary four-language subset has an equal or lower
mean than the frozen Kartvelian subset. This is a diagnostic across a
nonexchangeable language sample, not a population-level p-value.

## Stability and named operations

Report direct phoneme-label agreement among the twelve held-folio mappings,
both across all source members and across members occurring at least 20 times
in Q20. Report within-fold agreement among the three restarts and exact mapping
hash recurrence. No post-hoc phoneme relabeling is allowed.

The source-native realizations of the previously discussed display operations
are frozen as:

- `q-`: `D1`;
- `d-`: `B1`;
- `s-`: `C2`;
- `-dy`: `B1 A2`;
- `-dal`: `B1 A3 B2`;
- `-dar`: `B1 A3 C1`.

These equivalences are descriptive all-reading alignment facts, not sounds.
For every candidate language report whether their mapped phoneme sequences are
identical across folds. No semantic or linguistic function is assigned.

## Decision

`KARTVELIAN_PHONOTACTIC_ADVANTAGE_SUPPORTED` requires all of:

- Kartvelian mean held bits/member lower than control mean;
- exact 495-subset diagnostic `p<=0.05`;
- at least three of four Kartvelian profiles rank above the median control;
- frequent-code cross-fold exact mapping agreement at least `0.75`;
- retained mapping beats its random-map median in every fold for at least
  three Kartvelian languages;
- at least four of the six named module realizations are identical in at least
  9/12 folds for the best Kartvelian profile.

`KARTVELIAN_PHONOTACTIC_FIT_WEAK_OR_UNSTABLE` applies when the target family
has a nominal held advantage but misses any stability/specificity gate.

`KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS` applies when its aggregate held
fit is not better than the controls or the best control beats every target.

`INSUFFICIENT_PHONOTACTIC_CAPACITY` applies if fewer than ten Q20 folios or
fewer than three target profiles retain at least 35 external forms.

The result cannot establish Georgian, Mingrelian, Laz, or Svan language; any
sound value; a word or morpheme; plaintext; meaning; translation; authorship;
or geographic origin.
