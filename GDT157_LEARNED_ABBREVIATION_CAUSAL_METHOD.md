# GDT157 — learned medieval abbreviation causal control

Status: **FROZEN BEFORE GENERATED-DIPLOMATIC SCORING**.

Date: 2026-08-15

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question

Can a channel learned from genuine expansion↔diplomatic parallels generate
Voynich-like formal architecture without receiving a Voynich alphabet,
wrapper, suffix, grammar, or target statistic?

This is a causal positive control for abbreviation. It is not a language,
plaintext, morphology, or translation test. No Voynich string is decoded.

## Source and seal

The sole learned channel source is the public Nuremberg Letterbooks parallel
export frozen and unblinded by GDT155. Books 2–5 are four outer folds. For each
held book, only aligned expanded/diplomatic group pairs from the other three
books may determine a channel parameter. The held diplomatic groups remain
targets until generation is complete.

The causal views are:

1. `EXPANDED_PLAINTEXT`: held expanded groups, unchanged;
2. `GENERATED_DIPLOMATIC_MAP`: deterministic posterior-modal channel output;
3. `GENERATED_DIPLOMATIC_SAMPLED`: deterministic hash-sampling from the same
   training-only channel distributions;
4. `REAL_DIPLOMATIC`: held diplomatic targets, opened only for evaluation.

The same line, record, book and group positions are used in every view.
Forty-five group-count-unaligned lines are excluded symmetrically. Ste1 is not
used to fit or score the channel because it is not one of the four held books.

No Voynich transcription, parser, image, or row is an input. The only Voynich
comparisons are already-published aggregates listed in
`gdt157_voynich_reference_manifest.tsv`. The numerical GDT003 reference was
constructed with f84r routed out before surface retention. No f84r artifact is
opened by GDT157.

## Learned transducer

Every aligned training pair contributes both identity and abbreviated
examples. The channel has two nested training-only levels.

1. An exact expansion-type distribution records all observed diplomatic
   outputs. MAP uses the count/lexical modal output. Sampling draws from the
   empirical distribution with additive one-half identity smoothing.
2. For expansion types absent from training, a character-alignment backoff is
   learned. Deterministic minimum-edit alignments attach each target insertion
   to the preceding source character. Emission distributions are estimated
   for successively backed-off contexts: two-character neighbors plus
   position/length bins; one-character neighbors plus position; character plus
   position/length; character plus edge class; character alone. A separate
   learned abbreviation propensity indexed by suffix/prefix and length decides
   whether the productive channel fires. MAP uses posterior modes; sampling
   uses fixed SHA-derived uniforms. Identity is the final fallback.

The transducer may delete, retain, substitute, or emit characters only where
those actions occur in training alignments. It has no literal `q`, `d`, `s`,
`o`, `ot`, `dy`, `dal`, `dar`, HPR2 layer, Voynich length bin, or record-rule
injection. Generated empty groups are rejected to identity. All tie breaks and
hash seeds are lexical and fixed.

## Channel checks

For each held book report group exact accuracy, character error rate,
abbreviation precision/recall, generated and real retention ratios, exact
lexicon coverage, productive-backoff coverage, and identity fallback. These
measure whether a negative architecture result is merely a failed transducer.

## Frozen structural diagnostics

`gdt157_feature_contract.tsv` is exhaustive. The principal blocks are:

- the exact GDT003 nested edit-algebra fingerprint on a common deterministic
  12×1,000 group sample per view: operations, left/right support, replacement
  fraction, rectangle completion, compatibility, hidden-fourth-cell precision
  and AP against KT2/KT4, frequency and edit-distance baselines;
- the GDT155 blind HPR2-like deletion parser, re-learned in held-book folds,
  yielding left/right families, complete left×right host rectangles and
  PAGE_HOST recurrence;
- line/record start and end distribution divergence and reset contrasts;
- cross-space edge mutual information above within-line cyclic rotations;
- group/character entropy and conditional-character entropy;
- record-level known-content retrieval with raw character trigrams,
  PAGE_HOST trigrams and compiler-only features.

All parsers and diagnostic selectors are trained without the held book. The
12,000-token fingerprint positions are selected once from expanded metadata
and reused across all four views. ZL3b/IT2a/RF1b never enter this experiment.

## Causal attribution

For each scalar feature, abbreviation movement is

`GENERATED - EXPANDED`.

Channel fidelity is judged by the generated-to-real residual. A feature is
`ABBREVIATION_SUFFICIENT` only if generated moves in the real-diplomatic
direction and closes at least half of the expanded→real gap in both MAP and
sampled views. It is `PARTIAL_ABBREVIATION_EFFECT` for a same-direction move
below one half, `NOT_GENERATED_BY_ABBREVIATION` for no material movement or a
wrong direction, and `UNRESOLVED_CHANNEL_FAILURE` if the held channel does not
beat identity on abbreviation-site recovery.

Voynich comparison is direct only for the identically defined GDT003
fingerprint. Other published Voynich record effects are contextual reference
rows, never folded into a synthetic distance or confirmation score. A feature
where real diplomatic and generated diplomatic are both weak but the frozen
Voynich aggregate is strong is a candidate for an additional layout/record
compiler; it is not proof of one.

## Controls and decision

- exact un-abbreviated plaintext is the paired negative control;
- real diplomatic text is the positive calibration, not training data;
- character KT2/KT4, whole-form frequency, and nearest-edit baselines remain
  inside the GDT003 diagnostic;
- all four book-held folds and per-book effects are reported;
- MAP and sampled channels are a two-view robustness family, not independent
  samples;
- genre and record layout are held fixed within each paired line but differ
  fundamentally from the Voynich manuscript.

Final status vocabulary:

- `LEARNED_ABBREVIATION_GENERATES_MOST_TESTED_ARCHITECTURE`
- `LEARNED_ABBREVIATION_GENERATES_PARTIAL_ARCHITECTURE`
- `LEARNED_ABBREVIATION_DOES_NOT_GENERATE_VOYNICH_LIKE_ARCHITECTURE`
- `INSUFFICIENT_TRANSDUCER_FIDELITY`

## Claim ceiling

At most: a held-book learned medieval abbreviation channel does or does not
generate specified surface/record statistics resembling frozen Voynich
aggregates. No Voynich word, morpheme, sound, language, plaintext, semantic
role, meaning, geographic origin, scribal tradition, or translation follows.
