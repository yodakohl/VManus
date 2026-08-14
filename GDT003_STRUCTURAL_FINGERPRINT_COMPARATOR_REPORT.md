# GDT003 structural fingerprint comparator report

Status: **LANGUAGE_AGNOSTIC_STRUCTURAL_NEIGHBORS_ONLY**

## Outcome

The closest capacity-matched corpus in this frozen tournament is
**Old Italian** (`OLD_ITALIAN_UD_CONTROL`), with descriptive distance
0.291089. This is not a language
identification. It is a rank among a small, postulated corpus panel whose
scripts, genres, orthographic systems, tokenization, and source dates differ.

Voynich's matched nested algebra made 58,336 candidate
fourth-cell predictions, with 569 exact held-fold hits,
precision 0.009753840, and AP gain over the best
same-candidate string baseline -0.001466772.
The literal `q` plus `dy/dal/dar` subgroup's AP gain was
-0.107569866
(19/857 exact).
No literal Voynich operation was mapped into another script.

The matched Voynich fingerprint has 406.833
retained operations per fold, left/right log-support ratio
-0.261292, rectangle completion
0.507323, and compatible-pair density
0.045291. These are surface-system
statistics, not linguistic categories.

## Overall matched rank

| rank | corpus | family | tier | distance | AP gain | precision |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | Old Italian | Romance | HISTORICAL_UD | 0.291089 | -0.050137 | 0.010309 |
| 2 | Old Church Slavonic | Slavic | HISTORICAL_UD | 0.347233 | -0.072696 | 0.023810 |
| 3 | Adyghe | Northwest_Caucasian | MODERN_MATCHED_SENSITIVITY | 0.351919 | +0.002511 | 0.010738 |
| 4 | Latin | Italic | HISTORICAL_UD | 0.405138 | -0.856794 | 0.072727 |
| 5 | Kazakh | Turkic_Kipchak | MODERN_MATCHED_SENSITIVITY | 0.428610 | +0.000000 | 0.000000 |
| 6 | Latin | Italic | MODERN_MATCHED_SENSITIVITY | 0.445260 | +0.000000 | 0.000000 |
| 7 | Italian | Romance | MODERN_MATCHED_SENSITIVITY | 0.447560 | +0.000000 | 0.000000 |
| 8 | Lezgian | Northeast_Caucasian | MODERN_MATCHED_SENSITIVITY | 0.448205 | +0.000000 | 0.000000 |
| 9 | Arabic | Semitic | MODERN_MATCHED_SENSITIVITY | 0.454166 | -0.078957 | 0.017707 |
| 10 | Maltese | Semitic | MODERN_MATCHED_SENSITIVITY | 0.456916 | +0.000000 | 0.000000 |
| 11 | Basque | Basque | MODERN_MATCHED_SENSITIVITY | 0.463358 | -0.480000 | 0.055556 |
| 12 | Hungarian | Uralic | MODERN_MATCHED_SENSITIVITY | 0.499249 | +0.000000 | 0.000000 |
| 13 | German | Germanic | MODERN_MATCHED_SENSITIVITY | 0.521193 | +0.000000 | 0.000000 |
| 14 | Abkhaz | Northwest_Caucasian | MODERN_MATCHED_SENSITIVITY | 0.531206 | -0.366841 | 0.022989 |
| 15 | Avar | Northeast_Caucasian | MODERN_MATCHED_SENSITIVITY | 0.533140 | -0.644511 | 0.142857 |
| 16 | Georgian | Kartvelian | MODERN_MATCHED_SENSITIVITY | 0.540314 | +0.000000 | 0.000000 |
| 17 | Ancient Greek | Greek | HISTORICAL_UD | 0.540561 | +0.000000 | 0.000000 |
| 18 | Armenian | Armenian | MODERN_MATCHED_SENSITIVITY | 0.548540 | +0.000000 | 0.000000 |
| 19 | Greek | Greek | MODERN_MATCHED_SENSITIVITY | 0.596184 | +0.000000 | 0.000000 |


The rank combines Jensen-Shannon distance between the predeclared edit spectra
with an equally weighted, range-normalized scalar fingerprint. It is sensitive
to the admitted panel and is not a posterior probability.

## Components behind the nearest ranks

| corpus | mean operations | right/left log2 support | replace fraction | rectangle completion | compatible-pair density | AP gain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Old Italian | 361.667 | +0.270481 | 0.618894 | 0.391566 | 0.000373 | -0.050137 |
| Old Church Slavonic | 241.583 | +0.322904 | 0.597102 | 0.522727 | 0.000244 | -0.072696 |
| Adyghe | 238.667 | +1.283948 | 0.560754 | 0.227593 | 0.000551 | +0.002511 |
| Latin | 261.917 | +1.682224 | 0.727649 | 0.901554 | 0.000471 | -0.856794 |
| Kazakh | 223.583 | +2.082781 | 0.584793 | 0.000000 | 0.000000 | +0.000000 |
| Latin | 185.167 | +2.586076 | 0.637264 | 0.000000 | 0.000000 | +0.000000 |
| Italian | 173.000 | +1.498998 | 0.625241 | 0.507937 | 0.000118 | +0.000000 |
| Lezgian | 153.583 | +3.098969 | 0.562670 | 0.333333 | 0.000064 | +0.000000 |
| Arabic | 171.583 | -1.285646 | 0.631374 | 0.375188 | 0.001605 | -0.078957 |
| Maltese | 114.000 | +0.432424 | 0.605263 | 0.596154 | 0.000155 | +0.000000 |


Voynich itself has by far the denser compatible-pair inventory in this table;
the nearest neighbors match only a mixture of components. Old Italian is an
ordinary control and ranks first, which directly blocks a geographically
specific reading of the rank. Modern Adyghe is the closest modern sensitivity,
but its positive AP gain is only +0.002511
from 8/745
exact predictions.

## Voynich same-candidate prediction baselines

| model | AP | paradigm minus model |
| --- | ---: | ---: |
| CHARACTER_ORDER2_KT | 0.025604568 | -0.001466772 |
| CHARACTER_ORDER4_KT | 0.020964122 | +0.003173673 |
| NEAREST_EDIT_DISTANCE | 0.013892907 | +0.010244888 |
| NESTED_PARADIGM | 0.024137796 | +0.000000000 |
| VISIBLE_WHOLE_GROUP_FREQUENCY | 0.013976543 | +0.010161252 |


On this matched resample, the broad algebra does not beat KT2. This does not
rewrite the larger 102-folio GDT003 result; it shows that its small positive
full-corpus advantage is not stable under this capacity/genre-matched sampling
design. The predeclared literal Voynich q/right subsystem is substantially
worse than its strongest string baseline here as well.

## Historical tier and missing varieties

| historical rank | corpus | distance | AP gain |
| ---: | --- | ---: | ---: |
| 1 | Old Italian | 0.291089 | -0.050137 |
| 2 | Old Church Slavonic | 0.347233 | -0.072696 |
| 3 | Latin | 0.405138 | -0.856794 |
| 4 | Ancient Greek | 0.540561 | +0.000000 |


Old Georgian is retained at 6,093 tokens as a low-capacity descriptive
sensitivity and receives no primary rank. Middle Armenian has only 788 eligible
tokens in two source documents and is not fitted. No historical Cuman or Early
Maltese/Siculo-Arabic corpus was admitted; modern Kazakh and Maltese are visibly
labeled proxies/sensitivities.

## Reading the spectra

The artifacts report the left/right support ratio, add/replace balance,
rectangle completion, compatible-pair density, held-out precision, and gain
over KT/string baselines separately. A close aggregate distance can therefore
coexist with failure on the decisive predictive dimension. `gdt003_structural_fingerprint_baselines.tsv`
contains the identical-candidate baseline comparison for every corpus.

The generic cross-language subsystem is “one-character left add plus any
right-edge operation.” It tests positional combinability without asserting
that any two literal characters correspond. The Voynich-specific `q` plus
`dy/dal/dar` result is reported only for Voynich.

## Family aggregation

| family rank | family | members | mean distance | closest member distance |
| ---: | --- | ---: | ---: | ---: |
| 1 | Slavic | 1 | 0.347233 | 0.347233 |
| 2 | Romance | 2 | 0.369325 | 0.291089 |
| 3 | Italic | 2 | 0.425199 | 0.405138 |
| 4 | Turkic_Kipchak | 1 | 0.428610 | 0.428610 |
| 5 | Northwest_Caucasian | 2 | 0.441562 | 0.351919 |
| 6 | Semitic | 2 | 0.455541 | 0.454166 |
| 7 | Basque | 1 | 0.463358 | 0.463358 |
| 8 | Northeast_Caucasian | 2 | 0.490672 | 0.448205 |
| 9 | Uralic | 1 | 0.499249 | 0.499249 |
| 10 | Germanic | 1 | 0.521193 | 0.521193 |
| 11 | Kartvelian | 1 | 0.540314 | 0.540314 |
| 12 | Armenian | 1 | 0.548540 | 0.548540 |
| 13 | Greek | 2 | 0.568372 | 0.540561 |


Family labels are descriptive metadata. Several families have one corpus;
their “family rank” is therefore just that corpus's rank, not a replicated
family-level estimate.

## Falsifiers and limitations

- Historical exact-variety capacity is incomplete, especially for Middle
  Armenian, Old Georgian, Cuman, and Early Maltese.
- Wikipedia is a modern random-page sensitivity corpus, not a historical or
  genre-matched manuscript corpus.
- Native orthographies are intentionally preserved. Distance can reflect
  script conventions and editorial tokenization.
- Exact held-fold hits are computationally hidden public forms, not new text.
- f84r remained sealed.
- No phoneme, sound, meaning, morpheme, POS, plaintext, or translation is
  assigned.

## Conclusion

This experiment ranks surface-system fingerprints, not languages. The useful
question is whether the nearest corpus shares Voynich's balance of edge edits,
rectangle completion, compatibility, and held-out gain. The rank is therefore
reported alongside every dirty confound and predictive counterexample, and it
does not revise GDT003's `LIMITED/LOCAL COMPOSITION ONLY` conclusion.
