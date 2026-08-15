# GDT142 — relation assignment geometry

## Scope

This is an exposed, post-hoc robustness audit of the frozen GDT140 five-by-five
Herbal relation panel.  It uses only the published, f84-free GDT140 relation
inventory, pair-similarity matrix, and 120 exact assignment worlds.  It does
not reopen a transcription source, inspect an image, add a visual relation, or
alter the human pairings.

The question is narrower than GDT140: does the PAGE_HOST result depend on the
absolute scale of weighted-Jaccard similarity, or is the true assignment also
favoured when each pair is judged by its rank from the source page, its rank
into the target page, or both?

## Fixed audit family

For each of the four published GDT140 representations, evaluate six fixed
normalizations of the same 5×5 matrix:

1. `RAW_SIMILARITY` — the published weighted Jaccard;
2. `SOURCE_RANK` — descending within-source rank converted to `(6-rank)/5`;
3. `TARGET_RANK` — descending within-target rank converted identically;
4. `MUTUAL_RANK_MEAN` — mean source and target rank scores;
5. `RECIPROCAL_RANK_MEAN` — mean reciprocal source and target ranks;
6. `MUTUAL_TOP2` — one only when both ranks are at most two.

Ties receive the same competition rank.  For every variant, enumerate all
`5! = 120` one-to-one assignments and report the true mapping's inclusive
rank and inclusive exact tail.  The shared search diagnostic standardizes all
24 variant score vectors and takes their maximum in every assignment world.
This is an exact finite-orbit correction for this declared audit family, but
it cannot correct the earlier choice to perform this audit after seeing
GDT140.

Report reciprocal ranks for every true pair, the closest false assignments,
and a unit-temperature standardized-score posterior only as a descriptive
concentration measure.  No posterior is a semantic probability.

## Decision and ceiling

Use `RELATION_ASSIGNMENT_GEOMETRY_ROBUST_WITHIN_EXPOSED_5X5` only if all six
PAGE_HOST-character-trigram normalizations rank the true assignment at most
6/120 and the shared 24-variant tail is at most .05.  Otherwise use
`RELATION_ASSIGNMENT_GEOMETRY_SENSITIVE`.

Even a robust result supports only assignment-scale robustness inside the
already exposed five-pair panel.  It is not an independent relation panel,
botanical truth, a plant or component identity, a semantic role, a gloss, a
word, a morpheme, a part of speech, a sound, a language, plaintext, meaning,
or translation.

The sealed folio is absent from every input to this audit.  No f84 source,
image, transcription, or derived formal row is opened.
