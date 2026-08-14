# GDT013 latent-role propagation report

Status: **WEAK ROLE RANKING WITH RELATIONAL MICROGRAMMAR LEADS**

## Held-physical-folio result

The experiment used 394 unhedged annotated groups on 18
physical folios.  `PRIOR` is the best calibrated model;
`SOURCE_FAMILY` gives the best mean held-folio ranking.  Mean
Brier / average precision across eight channels are:

- `PRIOR`: 0.166974 / 0.175985
- `NUISANCE`: 0.218475 / 0.463373
- `WHOLE_TOKEN_STRING`: 0.181205 / 0.454800
- `RESIDUAL_HOST`: 0.179948 / 0.459405
- `SOURCE_FAMILY`: 0.186836 / 0.463954
- `FIELD_CONTENT_JOINT`: 0.189141 / 0.435258

`FIELD_CONTENT_JOINT` changes mean Brier by -0.007936 relative to the
whole-token string model.  Source-native family structure changes mean AP by
+0.009154 relative to that string model.  The prior remains best
calibrated and nuisance/register structure nearly matches the best AP: there
is no general semantic decoder here.

## Concrete microgrammar leads

The best abductive contrast is now more specific than `AR` alone:

- `ARO` occurs in proximity-labelled contexts 9/9 times across 6 physical folios.  It is a plausible **adjacent/local-reference** sequence, but the within-folio p=0.520 shows that it largely follows register ecology.
- `TAR` occurs in enclosure contexts 3/4 times across 4 folios.  Its folio-conditioned effect is +0.900 (p=0.080), making **bounded/interior reference** the sharper risky prediction.
- `ED` is a weak apparatus/medium lead; `KAL` is a figure-associated index lead.  Both remain domain-confounded.

This suggests a provisional local-reference microgrammar in which material
around `AR`—especially `O` versus `T/OT` environments—modulates how a referent
is situated.  It is a generative hypothesis, not a lexical segmentation.

## What was extracted

The full-data exploratory fit ranks 4440 formal feature/role weights.
The top five source-family and residual-host motifs per channel were propagated into
2860 strict, all-reading confirmed-prose occurrences.  These are
concrete places where the label-derived theory makes a functional prediction;
they are not decoded prose.

GDT012's `AR` enclosure lead remains one member of a larger motif system rather
than a proposed standalone word.  GDT013 asks whether neighboring
source-family and residual-host features reinforce or replace it.  The anchor
and prose TSVs preserve every feature, score, locus, and renderer state so the
next pass can search record-level co-occurrence patterns instead of inventing
English sentences.

## Limits

The human labels are sparse and diagram-family clustered.  Naive Bayes assumes
conditional independence, and the selected model is post-selected on these
same eight channels.  A role predictor can exploit domain/register style even
under folio holdout.  Therefore every propagated role is speculative.

No word, morpheme, POS, sound, language, plaintext, or translation is claimed.
f84r remained unopened, unretained, unjoined, and unscored.
