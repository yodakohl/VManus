# GDT159 diplomatic surface-algebra source audit

Status: `FROZEN_BEFORE_GDT003_FINGERPRINT_SCORING`

Date: 2026-08-15

## Admission rule

This pass admits public, machine-readable manuscript transcriptions only when
their source policy preserves visible abbreviation signs or graphematic
surface forms.  Corpus admission used date, language, genre, transcription
policy, and machine-readable capacity.  No GDT003 fingerprint was computed
before this manifest was frozen.

The search prioritized Latin technical and medical material.  It did **not**
find a capacity-matched corpus that is simultaneously early-fifteenth-century,
Latin, technical/medical, and abbreviation-preserving.  That four-way gap is
kept visible rather than filled with expanded text or a later normalized
edition.

## Admitted corpora

### Latin medical graphematic panel

CREMMA Medii Aevi is public CC-BY 4.0 ALTO ground truth.  Its transcription is
graphematic: abbreviations and abbreviation signs are preserved, ligatures are
reduced to component letters, and manuscript spacing is retained.  The five
frozen medical manuscripts are Egerton 821, Montpellier H318, Clm 13027, BnF
Latin 16195, and Philadelphia College of Physicians 10a 135.  They contain
medical treatises, recipes, charms, *De urinis*, *Liber minor de coitu*,
*De crisibus*, *Questiones de coitu*, and *Tractatus de sterilitate*.  Their
dates span 1100--1399, so this is a genre-priority period sensitivity, not an
exact-period control.

Sources:

- CREMMA Medii Aevi repository and transcription policy:
  https://github.com/HTR-United/CREMMA-Medieval-LAT
- Data paper: https://doi.org/10.5334/johd.97
- Frozen repository commit: `292525969ad98380b398e6606a9c2a36d51913ae`

### Fifteenth-century Latin graphematic panel

The exact-century panel combines non-overlapping fifteenth-century Latin
manuscript samples from CREMMA Medii Aevi and HTRomance.  Both use
graphematic manuscript transcription and preserve abbreviation signs.  The
panel is deliberately mixed genre (scholastic, grammatical, literary, and
ecclesiastical), because no technical/medical exact-period subset reaches the
frozen 12,000-group capacity.

Sources:

- CREMMA source above.
- HTRomance Medieval Latin:
  https://github.com/HTRomance-Project/medieval-latin
- Frozen HTRomance commit: `fe25eb9ffaa37a32333fe0e3f4093ff4dd8186db`

### Latin scholastic graphematic panel

Three nonmedical scholastic manuscripts from CREMMA (WettF 15, BIS 193, and
Mazarine 915) form a separate 1270--1399 abbreviation-practice sensitivity.
It is below matched capacity and is not promoted by padding.

### iForal 1395--1411 charter panel

iForal provides PAGE XML transcriptions of medieval Latin/Portuguese
*forais*.  The source describes specialist transcription but warns that
line-image alignment was carried out mainly by a nonspecialist.  The frozen
scope is mechanical: all documents whose directory date is 1390--1450,
yielding charters dated 1395 and 1411.  Visible abbreviation signs remain in
the surface.  The panel has 6,104 eligible groups and is a low-capacity
different-morphology sensitivity.

Sources:

- Repository: https://github.com/arhelio/iForal-Dataset
- Project: https://iforal.hypotheses.org/
- Frozen commit: `9bdc5b006f634bc2e12abe043ca6e5578dfcdd83`

### Late-fifteenth-century apothecary sensitivity

TranscriboQuest 2024 supplies seven expert-corrected pages from Biblioteka
Baworowskich Rps 12533 II, a Latin/German apothecary recipe manuscript from
the second half of the fifteenth century.  Abbreviations were not expanded;
MUFI abbreviation and apothecary measure signs were transcribed.  At 1,554
eligible groups it is descriptive only.  Its late date and very low capacity
are explicit counterweights to its high genre relevance.

Sources:

- Dataset record: https://doi.org/10.5281/zenodo.13757440
- Frozen archive SHA-256:
  `fd3b6cc4661027ec3e1311b21f3eba8fe083f26f79f20b1347888ce21f3ab71b`

## Rejected or separated sources

- Nuremberg and Ste1 remain published anchors from GDT155--158; they are not
  counted as new corpora.
- ANR e-NDP and AMSMB have excellent period/administrative coverage but their
  published transcription policies resolve abbreviations.  They cannot answer
  whether authentic visible abbreviation creates the residual.
- Modern editions, OCR text, critical expansions, and texts without
  manuscript-surface abbreviation provenance are excluded.
- The later apothecary sample is not relabeled early fifteenth century.
- The earlier medical panel is not relabeled contemporaneous.

## Frozen normalization and capacity

The experiment reuses the exact GDT003 surface normalizer: NFC case-folded
Unicode letter/combining-mark runs, Latin-script only, length 2--30.  Whole
PAGE/ALTO files are source units.  Capacity-matched corpora use the unchanged
12 folds x 1,000 groups; lower-capacity corpora use the unchanged GDT003
low-capacity retention path without padding.

Abbreviation signs that Unicode classifies as letters or combining marks
remain.  Punctuation-like signs can become boundaries under the frozen
normalizer.  This is an orthographic/tokenization confound, not an inferred
linguistic segmentation.

## Seal

Stage A reads no Voynich source row or image.  The later comparator may use
only the already-published, f84r-free GDT003 aggregate as its Voynich target.
No f84r source artifact may be opened, queried, retained, joined, or scored.
