# GDT147 — relation-backbone stability

## Scope

This is an explicitly post-hoc decomposition of the exposed GDT140 five-source
by five-target Herbal relation matrix.  It asks which individual human-paired
edges are retained by the best assignment under the six PAGE_HOST-character-
trigram normalizations already published by GDT142.  It adds no visual
annotation, transcription, target page, or representation.

Only the published f84-free GDT140 relation inventory, pair similarities, and
exact 120-world assignment orbit are used.  No transcription source or image
is opened.  f84r remains sealed.

## Fixed calculations

For `PAGE_HOST_CHAR3`, reconstruct the six GDT142 normalizations:

1. raw weighted-Jaccard similarity;
2. source-rank score;
3. target-rank score;
4. mean source/target-rank score;
5. mean reciprocal source/target rank;
6. mutual-top-two indicator.

Enumerate all 5! assignments for each normalization.  Ties within `1e-12` are
retained rather than broken.  For every true human-paired edge report:

- **best-assignment inclusion mass**: for each normalization, the fraction of
  tied best assignments containing the edge, averaged over six normalizations;
- **top-five inclusion mass**: the fraction of the five deterministically
  ordered highest-scoring assignments containing the edge, averaged over six;
- the number of normalizations in which the edge appears in at least one best
  assignment and in every best assignment.

For concise descriptive localization, call an edge a `STABLE_BACKBONE_EDGE`
when best-assignment inclusion mass is at least 0.75 and top-five inclusion
mass is at least 0.60.  These thresholds are post-hoc summaries, not a test or
confirmation criterion.

The exact two-target swap between the true assignment `A000` and the assignment
that exchanges only the MHI004 and MHI007 targets is reported separately for
all six normalizations.  No p-value is attached to an edge: the panel and the
normalization family are exposed, and the purpose is mechanism localization.

## Claim ceiling

GDT147 can show only that part of the anonymous PAGE_HOST-character-trigram
assignment lead is stable inside the exposed five-target pool.  It cannot
establish that a human visual relation is true, that a source or target page
depicts the same plant or component, or that any Voynich form has a semantic
role, gloss, word, morpheme, part of speech, sound, language, plaintext,
meaning, or translation.
