# Voynich active state — structural reset baseline

Updated: 2026-08-06. Read this file first, then
`experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv`.

## Outcome

- The manuscript is **not translated**. There are zero confirmed English
  lexemes, zero plaintext clauses, and no established language, phonetic
  alphabet, cipher, part-of-speech system, or S/V/O order.
- Every attempted transferable meaning assignment failed, stopped for lack of
  authorial support, was invalidated, or remained source-only and unscored.
- The accumulated semantic investigation is frozen under
  `archive_pre_reset_2026-08-06/`; do not load it by default.
- The active investigation has no word guess or source-family hypothesis.

## Confirmed structural baseline

1. Visible spaces are real hierarchical boundaries, although they need not be
   European-style word boundaries.
2. Multi-unit forms are productively compositional; the inventory is not well
   described as unrelated opaque codebook items.
3. Physical lines behave as record/utterance-like units. A validated writing-
   order/content coordinate rises within a line and resets at the next line.
4. Directional formal-state grammar exists. Position-controlled exact local
   transitions include several D-to-q and E-to-q edges; detached REL_I,
   FREE_L, and FREE_R completions also occur across ordinary spaces.
5. Bare d/s/t line-entry carriers form a qualified state system. Bare t is
   paragraph-opening-associated; bare d/s are continuation-associated. These
   are not START or CONTINUE words.
6. Strict `AII+N` tends to precede strict `AI+N` within a physical line,
   especially in Currier B. This is not counting or a number system.
7. Roots show a weak but held left-to-right rise toward content/identifier-like
   usage. It is distributed rather than a fixed sentence field.
8. Exact `che+VALUE` is a highly productive carrier construction. Its relative
   low-content-to-high-content direction is qualified across source ecologies;
   neither `che` nor its values have English meanings.

ZL3b, IT2a, and RF1b are alternate readings of one manuscript, never three
independent samples. Structural tags must remain distinct from translations.

## What is deliberately inactive

Botanical identification, bathing imagery, zodiac/astronomical dictionaries,
number systems, image proximity, OCR/CV semantics, CLIP prompts, historical
source matching, known-language alignment, cipher/codebook work, and all named
word guesses are archive-only. Consult `CLOSED_ROUTE_FAMILIES.tsv` before
proposing any related test.

## Fresh research question

Before assigning another meaning, determine which broad system class best
predicts the confirmed text-internal grammar: ordinary language, structured
notation, mnemonic/record system, or a generative/synthetic process. No class
is currently preferred. A future experiment must state a discriminating held
prediction; fitting another descriptive model is insufficient.

## Admission rule for new work

A new semantic route needs genuinely independent authorial evidence or a new
invariant capable of falsifying competing meanings. A new model, crop,
threshold, spelling resemblance, subset, historical analogy, or GPU search is
not new evidence. Record every material pass or failure in the active ledger.

## Runtime and sources

- Interpreter: `/home/anon/VManus/vpy`; up to 32 CPU workers and the RTX 3090
  are available when they reduce total iteration time.
- Main text: manual ZL/IT/RF transcription only. Custom f68 OCR is rejected.
- Cached images and embeddings in the archive are inactive and must not be
  imported into a fresh test without an explicit registered reason.

## Recovery

- Primary grammar evidence index:
  `experiments/semantic_assumptions/grammar/PRIMARY_EVIDENCE.tsv`
- Complete negative-route memory:
  `experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv`
- Full pre-reset files and reports: `archive_pre_reset_2026-08-06/`
- Archive integrity: `archive_pre_reset_2026-08-06/ARCHIVE_MANIFEST.tsv`
  (SHA-256 `dade5b48caa64acf557020f96d52675bf6f37ad03f304a879eb6bc5e4c990271`).
