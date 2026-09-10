# Independent exposed-source audit

Status: the proposed syllable-key collision is valid for this six-verse excerpt. This is not a blind recovery trial, a historical second reading, or evidence about Voynich plaintext. No primary runner was read or imported. Printed pages 57–58 of Choulant's 1832 Macer edition were visually checked against verses 716–721; the OCR's `TVertius` is printed `Tertius`.

## Scope and sentence edges

The source begins `Virtus est illi siccans et frigida valde`: its plant referent is inherited from the preceding Acidula section, not identified inside these six verses. Verses 716–717 form a grammatical statement: its power is drying and very cold; physicians assign the third degree in both respects. Hac apposita in 718 is an ablative absolute; sacer ignis and herpeta mordax are coordinated subjects of fugit. In 719 tumor is the subject of cedit; tritae is an elliptical reference to the crushed plant, attached to cataplasmate. Verse 720 gives finite treatment predicates with an understood plant subject. Verse 721 uses dicunt plus prodesse and dative calidae podagrae.

Crucial limitation: verse 721 ends with a comma and is immediately followed by `Si fuerit foliis illius operta virentis / Aut cataplasmetur mixta contrita polenta.` The six verses therefore cut off an explicit condition on the gout treatment. They are six complete verse lines, but not a self-contained complete historical prescription or sentence sequence. The opening also has an anaphoric referent. Do not present this as a complete-context semantic reconstruction.

## Scansion

One ordinary quantitative scansion, with feet separated by bars:

- 716: vir-tus | est-il | li-sic | cans-et | fri-gi-da | val-de
- 717: ter-ti-us | a-me-di | cis-da-tus | est-gra-dus | huic-in-u | tro-que
- 718: hac-fu-git | ap-po-si | ta-sa-cer | ig-nis-et | her-pe-ta | mor-dax
- 719: et-tu-mor | ex-o-cu | lis-tri | tae-ca-ta | plas-ma-te | ce-dit
- 720: ul-ce-ra | quae-ser | punt-co-hi | bet-com | bus-ta-que | cu-rat
- 721: et-mul | tum-ca-li | dae-di | cunt-pro | des-se-po | da-grae

The first five feet are dactyls or spondees, the fifth is a dactyl, and the sixth is long plus anceps. These scans require no elision or word removal. Syllabic spelling in this display is not a demand that all contextual consonant positions be orthographic codas. In particular the final da of podagrae is heavy before gr, using the ordinary available long treatment of mute plus liquid; do not assign a fictitious lexical long vowel to it. See [Allen and Greenough, general rules of quantity](https://dcc.dickinson.edu/es/grammar/latin/general-rules-quantity). The lexical quantities used here were assessed manually, not by an independently complete quantitative lexicon.

Replacing fri-gi-da by fer-vi-da preserves its dactyl: frīgĭda has a naturally long first syllable; fer in fervida is heavy by position, and vi is short. Compare [Lewis and Short, frigidus](https://atlas.perseus.tufts.edu/dictionaries/entry/urn%3Acite2%3Ascaife-viewer%3Adictionary-entries.atlas_v1%3Alat.ls.perseus-eng2-n18807/) and [fervidus](https://atlas.perseus.tufts.edu/dictionaries/entry/urn%3Acite2%3Ascaife-viewer%3Adictionary-entries.atlas_v1%3Alat.ls.perseus-eng2-n18014/). This substitution preserves agreement with virtus and changes cold to hot/burning. It does not preserve the historical author's assertion; B is constructed and could be rejected by a correctly identified historical plant/medical context. Grammatical and metrical admissibility alone does not establish medical or historical plausibility.

## Independently calculated equality collision

Orthographic word syllabification used independently:

```
vir-tus est il-li sic-cans et fri-gi-da val-de
ter-ti-us a me-di-cis da-tus est gra-dus huic in u-tro-que
hac fu-git ap-po-si-ta sa-cer ig-nis et her-pe-ta mor-dax
et tu-mor ex o-cu-lis tri-tae ca-ta-plas-ma-te ce-dit
ul-ce-ra quae ser-punt co-hi-bet com-bus-ta-que cu-rat
et mul-tum ca-li-dae di-cunt pro-des-se po-da-grae
```

A separate short Python calculation split these words on hyphens and assigned each distinct syllable its first-occurrence integer. It found 43 words, 92 syllable occurrences and 74 distinct syllables. The syllables fri and gi each occur exactly once; fer and vi occur nowhere. Replacing the former two by the latter two therefore leaves the entire word-preserving equality signature unchanged, without a collision with any other syllable. Both global keys are injective and below the 98-symbol maximum. Verse boundaries may be erased without changing this fact. Quantities were not encoded as symbol values.

This supplies an explicit local non-uniqueness witness for the selected broad channel plus grammar/metre conditions. It neither measures the frequency of such collisions nor proves that additional passages, historical context or other independently established constraints cannot identify a reading. It says nothing about whether this channel fits the manuscript.
