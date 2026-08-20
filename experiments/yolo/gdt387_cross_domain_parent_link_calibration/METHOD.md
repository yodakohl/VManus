# GDT387 method — cross-domain parent-link calibration

## Question

Does a domain-local temporal/gate-derived role, hidden behind the same
Voynichified composite representation used in GDT385, add held-file prediction
of an independently parsed syntactic governor target in PCEEC2?

This is comparator-only. No result or label transfers to Voynich.

## Frozen source

* PCEEC2 public commit `bf79d1c46e8ef983a7347b0664d0d80243f32831`;
* 84 parsed `.psd` files, bundle SHA-256
  `c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714`;
* GDT382's oracle-blind composite observation layer, filtered to PCEEC2; and
* GDT385 only as the preceding anonymous comparator calibration.

The scored observation contains no source word, POS, constituent label,
semantic role, or governor identity.

## Hidden role and independent relation

The hidden comparator role uses the frozen canonical source-form set:

`after, afore, before, ere, when, whan, whanne, whenne, until, untill, til,
till, while, whil, whiles, whilst`.

This yields 110 role pivots across 47 of 84 source files in the frozen first-12
record sampling frame. The vocabulary is comparator oracle material and is
never exposed to the model.

Every visible parse terminal receives a syntactic governor from a fixed,
hand-auditable constituency head rule:

* IP/VP/RRC: leftmost verbal child, else nested VP/IP, else leftmost child;
* NP/NX: rightmost nominal/pronominal/quantifier child, else rightmost child;
* PP: leftmost P/RP child, else leftmost child;
* CP: nested IP/VP head, else rightmost child;
* ADJP/ADVP: rightmost child;
* all other constituents: leftmost child.

Non-head child heads attach to the selected constituent head. Root heads are
unscored. The target is the exact governor element, represented to the model
only as a signed relative-distance class: L/R 1–13 or side-specific FAR. Exact
target probability divides class mass uniformly among same-class candidates in
the record. The target relation exists for ordinary and role pivots alike, so
role membership does not define whether an edge exists.

## Source-only representations

The role detector reuses the five frozen GDT385 resolutions:

1. opaque host identity;
2. complete rendered group;
3. wrapper/boundary/position construction;
4. composite joint state; and
5. short construction span.

A frequency/grammar channel uses only source-side frequency, field/within-field
position, boundary/positional state, preceding opaque host, and record length.
All realizations and counts are learned without the held source file. Domain
files are never samples from the same document fold.

The target baseline uses only source-side position, boundary, field-position,
record-length, and training frequency bins. The augmented model adds the held
role probability. It never sees a target constituent, POS, governor, target
distance, or target-derived feature.

## Fixed evaluation

Primary split: leave one of 84 PCEEC2 source files out.

Report hidden-role AUC/codelength, exact governor codelength gain, positive
held-file folds, exact governor top-1/MRR change, null mobility and explicit
counterexamples.

The null has 2,048 shared worlds. It permutes held role probabilities within
held file × positional state × boundary state × binned field index × binned
within-field index × record-length bin × training-frequency bin. It preserves
the complete source-side opportunity structure and changes only alignment of
the role signal with governor outcomes.

## Frozen gate

The independent-domain route passes only if all hold:

* at least 100 hidden-role pivots across at least 40 source files;
* held role AUC ≥ 0.65 and role codelength gain > 0;
* exact-governor codelength gain > 0;
* positive governor gain in at least 42/84 files;
* exact target MRR delta ≥ 0;
* at least 20% of scored rows mobile under the exact null; and
* inclusive permutation `p ≤ .05`.

No threshold is changed after scoring. Failure means the GDT385 anonymous lead
is CoReMA-local under this external relation instrument.

## Claim ceiling

At most GDT387 can show that a hidden comparator role contributes to an
external syntactic-governor relation across two readable domains after
Voynichification. It establishes no Voynich role, operator, syntax, POS,
meaning, language, plaintext, or translation. No Voynich row and no f84 source
is opened, parsed, retained, or scored.
