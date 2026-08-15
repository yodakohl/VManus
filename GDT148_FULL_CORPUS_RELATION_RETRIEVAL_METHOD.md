# GDT148 — full-corpus Herbal relation retrieval

## Scope

GDT148 is an exposed YOLO follow-up to GDT140–GDT147.  It asks whether the six
pre-existing human Herbal-to-Herbal relation statements `MHI002`–`MHI007`
retrieve their stated target pages from the full comparable Herbal corpus.
Unlike GDT144, it uses complete page-frequency bags rather than the unique
O/OT-only set view.  No new relation, visual description, transcription, or
representation is selected.

The six statements are mechanically deduplicated across ZL3b/IT2a/RF1b from
the existing human-relation table.  They remain single human assertions, not
independent botanical ground truth.  Their already-recorded relation classes
define three fixed reporting scopes: all six, four component similarities, and
two whole-plant similarities.

The formal source is the published GDT062 HPR2 inventory.  It contains no f84r
row.  The scorer rejects every f84-prefixed page before retention; f84r is not
queried, selected, joined, or scored.

## Representations and candidates

The four GDT140 representations are reused exactly:

- exact PAGE_HOST frequency;
- PAGE_HOST padded character-trigram frequency;
- raw-token padded character-trigram frequency;
- HPR2 compiler signature frequency.

Similarity is weighted Jaccard.  For each source relation, the primary
candidate pool contains every non-source Herbal page with the target's Currier
and hand, excluding the source physical folio.  A target-illustration-profile
matched pool is reported only as a capacity-sensitive descriptive check.

For every source/model, similarities are standardized over its primary
candidate pool.  The true mean standardized score and number of true targets
ranked in the top six are computed for all/component/whole scopes.

## Null and interpretation

One hundred thousand deterministic worlds independently draw a target from
each primary pool, rejecting worlds with duplicate target pages.  The same
world is used for all four representations and three scopes.  Local tails and
maximum-over-12 standardized diagnostics are reported separately for mean
similarity and top-six count.

This is not prospective confirmation: the relations, GDT140 result, and the
decision to perform corpus-wide retrieval are exposed.  The component subset
is scientifically natural because it was recorded before scoring, but its
strong behavior was noticed during this follow-up.  Null tails therefore rank
how unusual the descriptive pattern is under the declared target randomizer;
they do not erase post-selection history.

Shared exact PAGE_HOST witnesses are exported with manuscript-wide page and
occurrence counts.  They are candidates for later tests only.  A shared host
does not name a plant, plant part, property, or operation.

## Claim ceiling

At most GDT148 may show that exact anonymous PAGE_HOST vocabularies retrieve
several human-related Herbal component pages better than raw strings or
compiler profiles.  It cannot establish botanical identity, component
identity, a semantic role, gloss, word, morpheme, part of speech, sound,
language, plaintext, meaning, or translation.
