# GDT013 latent-role propagation method

Status: **YOLO exploratory inference**

## Purpose

GDT012 tested one feature at a time.  GDT013 asks whether several weak formal
signals jointly predict independently human-annotated visual channels on an
unseen physical folio, and then uses the best formal model to nominate—not
confirm—roles for recurrent motifs in prose.

`f84r` is excluded before source-formal rows are retained.  ZL3b, IT2a, and
RF1b are alternate readings and only exact all-reading display agreements with
strict source-native family consensus are used.

## Discovery rows and targets

The 394 unhedged GDT012 rows are the primary labelled set.  Eight independent
binary channels are retained:

`PLANT`, `FIGURE`, `WATER_OR_APPARATUS`, `STAR_OR_SKY`,
`REL_EXPLICIT_ATTACHMENT`, `REL_ENCLOSURE`, `REL_PROXIMITY`, and
`REL_ARRAY_OR_GROUP`.

These are source annotations, not meanings assigned by this experiment.
Every fold holds out one complete physical folio.

## Models

All models are Laplace-smoothed Bernoulli naive Bayes with training-only
feature vocabularies (minimum training support two):

- `PRIOR`: training-fold target prevalence;
- `NUISANCE`: section, Currier, hand, layout kind, group-count and length bins;
- `WHOLE_TOKEN_STRING`: nuisance plus unstripped display-character 1--3 grams
  and whole-token identity;
- `RESIDUAL_HOST`: nuisance plus residual-host 1--3 grams/identity and the
  recovered prefix/closure state;
- `SOURCE_FAMILY`: nuisance plus source-native family 1--3 grams/identity;
- `FIELD_CONTENT_JOINT`: residual-host, source-family, layer, and nuisance
  features, without unstripped-token identity.

Models are compared by held-folio Brier score, log loss, and tie-aware average
precision.  Better prediction is useful evidence of transferable structure;
it does not turn a visual channel into a word meaning.

## Exploratory role propagation

The best-discriminating source-family model and the residual-host model are
refit to all labelled discovery rows.  Formal features with support on at
least two physical folios receive role log-odds.  The strongest positive
source-family and host motifs are then located in strict all-reading
`CONFIRMED_PROSE` groups outside f84r.  This propagation is explicitly
post-selected and is published so that a later theory can make line/record
predictions.  It is not decoded prose.

## Claim ceiling

Outputs may nominate anonymous functions such as attached index, bounded
reference, array member, or object-domain carrier.  They cannot establish a
word, morpheme, POS, sound, language, plaintext, or translation.  f84r remains
sealed.
