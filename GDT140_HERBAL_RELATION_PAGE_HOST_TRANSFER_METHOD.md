# GDT140 — Herbal relation PAGE_HOST transfer

## Question

Do independently archived visual relations between Herbal drawings pair pages
whose formal inventories are unusually similar?  The primary panel is the
pre-existing `CLEAN_HA_HAND1_5X5` set in
`manual_herbal_internal_relations.tsv`.  It contains five disjoint source
pages and five disjoint target pages, all Herbal Currier A/hand 1.  The
relations include whole-plant similarity and component similarities involving
leaves, a flower, and bulbs.  They are human comparison statements, not
botanical truth.

## Frozen exact test

The five relation IDs and page pairs are frozen before relation-conditioned
formal similarity is computed.  For each page build four complete page bags:
exact HPR2 PAGE_HOST, PAGE_HOST character trigrams, raw source-group character
trigrams, and compiler signatures.  Score a pair by weighted Jaccard
similarity.  Enumerate all `5! = 120` one-to-one assignments of the fixed five
source pages to the fixed five target pages.  Report the true assignment's
inclusive rank for every representation and a maximum-over-four statistic.

Also report each true target's rank among its five candidates, leave-one-pair
effects, and exact-host witnesses.  The source-display HPR2 inventory is one
derived view; it does not provide three independent transcription samples.
The earlier root/label repeated-plant failures remain unchanged: this is a
different whole-page distribution test, not a rerun of an ordered-root or
pharmaceutical-label query.

## Ceiling

A high true-pair rank would support anonymous formal content preservation
between visually related Herbal pages.  It cannot establish that the relation
is botanically correct or identify a plant, component, word, morpheme, POS,
sound, language, plaintext, meaning, or translation.  All f84 rows are
rejected before retention and no new f84 access is authorized.
