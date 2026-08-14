# GDT003 language-agnostic structural fingerprint comparator

Status: `SOURCE_POLICY_FROZEN_BEFORE_COMPARATOR_SCORING`

Date: 2026-08-14

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question and claim ceiling

This experiment asks whether the **surface-form transformation behavior**
measured by GDT003 is structurally closer to any requested comparison corpus
than to the others. It does not map Voynich signs to letters or phonemes, use
translations, search for recognizable words, or assign linguistic status to a
formal edit. A small structural distance is not language identification.

The prior GDT003 result remains unchanged: nested Voynich composition is
`LIMITED/LOCAL COMPOSITION ONLY`, and the named `q` plus right-edge subsystem
does not beat the string baselines.

## Frozen corpus strata

The comparator has two strata.

1. `MODERN_MATCHED_SENSITIVITY` is a frozen random main-namespace Wikipedia
   sample. Each admitted corpus has exactly 12 folds and 1,000 normalized
   surface tokens per fold. Kazakh is only a modern Kipchak sensitivity, never
   Cuman. Modern Maltese is not Early Maltese or Siculo-Arabic. Modern Adyghe,
   Abkhaz, Avar, and Lezgian are labeled modern-only.
2. `HISTORICAL_UD` uses only the CoNLL-U `FORM` column from Universal
   Dependencies release `r2.18`. Middle Armenian, Old Georgian, and Old Church
   Slavonic are the requested historical corpora. Latin, Old Italian, and
   Ancient Greek are historical controls. A corpus below matched capacity is
   retained as `INSUFFICIENT_CAPACITY`, not padded or promoted.

Voynich is downsampled to the same 12 x 1,000 design from strict source groups
on which ZL3b, IT2a, and RF1b agree. The editions are alternate readings, not
replications. Entire physical folios are assigned to folds. f84r is removed by
its routing field before surface retention and remains sealed.

## Surface normalization

Only native-script surface strings are used. Text is NFC-normalized and
case-folded; contiguous Unicode letter/combining-mark runs of length 2--30 are
retained only if every letter belongs to the corpus's declared script. No
lemma, POS, morphology, dependency, gloss, translation, transliteration, or
phonological representation enters the analysis.

Wikipedia page and UD document/block are indivisible source units. Units are
greedily balanced into 12 folds before deterministic within-fold sampling.
Every fitted transformation and baseline excludes the complete held fold.

## Nested transformation grammar

The grammar and training-only selector reproduce GDT003:

- add 1--3 characters at either edge;
- replace 1--2 left-edge characters;
- replace 2--3 right-edge characters;
- require at least five exact training type edges on at least three training
  folds;
- retain at most 32 rules per edit/length stratum;
- form commuting operation pairs only after discovery;
- require at least three training triplets and one complete training rectangle;
- predict only fourth-cell types absent from the training corpus.

The named Voynich `q`/`dy`/`dal`/`dar` strings are never projected into another
script. A language-agnostic `one-character-left-add + right-edge-operation`
subgroup is reported separately.

## Same-candidate baselines

Every candidate is ranked by the paradigm score, character KT order 2,
character KT order 4, visible-cell whole-group frequency, and nearest edit
distance. The character alphabet is learned inside each training fold, with a
single unknown-character cell. Report exact hits, precision, average precision,
AUC, and paradigm AP minus the strongest baseline AP. For an empty/no-positive
candidate set, AP is reported as 0.0. AUC is reported as the neutral 0.5 when
either class is absent; prediction and hit counts distinguish this reporting
convention from an evaluated mixed-class ranking.

## Fingerprint and distance

Each corpus fingerprint contains predeclared, language-agnostic quantities:

- normalized transformation spectrum by edit family and length stratum;
- left/right operation and support asymmetry;
- add/replace fraction;
- complete-rectangle density among eligible training triplets;
- compatible operation-pair density;
- held-out prediction density, precision, and AP gain over the best string
  baseline;
- the one-character-left plus right-edge subgroup's corresponding metrics.

The transformation-spectrum component uses Jensen-Shannon distance. Scalar
features are min-max scaled over Voynich plus all capacity-matched corpora;
their root-mean-square difference from Voynich is averaged with the spectrum
distance. Ties are resolved by corpus id. Historical low-capacity corpora are
reported but excluded from the primary rank.

The resulting rank is a descriptive distance among these frozen orthographies,
genres, and samples. Script, tokenization, corpus genre, editorial spelling,
and sample capacity remain explicit confounds.
