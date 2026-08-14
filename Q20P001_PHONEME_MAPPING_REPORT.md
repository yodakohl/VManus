# Q20P001 Q20 phoneme-mapping report

Status: **KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS**

This frozen experiment fitted explicit many-to-one mappings from 36 source-native
STA member codes on eleven Q20 folios and evaluated each mapping on the twelfth.
It used 4,671 groups from twelve physical folios. ZL3b, IT2a, and RF1b supplied
one strict consensus sequence, never three samples. f84r remained sealed.

## Held-folio result

| rank | external profile | panel | aggregate held bits/member | folds beating random-map median |
|---:|---|---|---:|---:|
| 1 | BASQUE | UNRELATED_CONTROL | 4.228221 | 12/12 |
| 2 | FINNISH | UNRELATED_CONTROL | 4.242279 | 12/12 |
| 3 | ARABIC_QURANIC | UNRELATED_CONTROL | 4.483276 | 12/12 |
| 4 | TURKISH | UNRELATED_CONTROL | 4.629676 | 12/12 |
| 5 | GREEK | UNRELATED_CONTROL | 4.694917 | 12/12 |
| 6 | CHECHEN | UNRELATED_CONTROL | 4.835610 | 12/12 |
| 7 | MINGRELIAN | KARTVELIAN_TARGET | 5.003208 | 12/12 |
| 8 | ARMENIAN | UNRELATED_CONTROL | 5.004680 | 12/12 |
| 9 | GEORGIAN | KARTVELIAN_TARGET | 5.057186 | 12/12 |
| 10 | LAZ | KARTVELIAN_TARGET | 5.234051 | 12/12 |
| 11 | SVAN | KARTVELIAN_TARGET | 5.243113 | 12/12 |
| 12 | AVAR | UNRELATED_CONTROL | 5.313821 | 12/12 |

The frozen Kartvelian mean is **5.134389** bits/member and the control
mean is **4.679060**, for Kartvelian-minus-control
**+0.455329**. The exact 4-of-12 panel diagnostic is
**p=0.977778** over 495 subsets. This diagnostic does not make the twelve
languages an exchangeable population sample.

The best target profile is **MINGRELIAN** (5.003208);
the best unrelated control is **BASQUE** (4.228221).
The source-native order-2 KT baseline scores **2.747658** and the
whole-group KT/escape baseline **3.427610** bits/member.
Because the phoneme map is many-to-one and has no reverse-ambiguity channel,
these reversible source-code lengths are reference baselines rather than a
direct MDL likelihood ratio against the external mapping.
Relative to each profile's own random-map median, the four target profiles gain
**1.157959** bits/member versus
**1.266316** for controls. Thus
the result is not rescued by normalizing the different phoneme-inventory sizes.

## Stability and registered operations

The best target's frequent-code cross-fold direct phoneme agreement is
**0.325455**,
with **12** distinct
mapping hashes in twelve folds. Exactly **0/6**
registered `q-`, `d-`, `s-`, `-dy`, `-dal`, `-dar` source sequences retain the
same mapped phoneme sequence in at least 9/12 folds. This is direct named-label
agreement; no phoneme relabeling was allowed.

## Interpretation

The mapping family is flexible and the external profiles contain only 39--40
modern basic-vocabulary forms. A low score would show compatibility with that
small phonotactic model, not a decoded language. The decision follows every
frozen family-specificity, random-map, mapping-stability, and module-stability
gate. Exact fold scores, mappings, controls, and counterexamples are published
in the TSV artifacts.

No output was optimized for recognizable words. Nothing here assigns a sound,
word, morpheme, POS, plaintext, meaning, translation, authorship, or origin.
