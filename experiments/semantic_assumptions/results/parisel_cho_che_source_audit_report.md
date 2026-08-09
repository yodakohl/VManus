# Parisel `cho/che` source and implementation audit

Status: **CONFIRM_FOLIO_REGIME_REJECT_EXACT_PUBLISHED_IMPLEMENTATION_CLAIMS**

The folio-level effect is real and unusually strong. With all manual separator
classes kept as source separators, the fitted high/low rates are
**0.675/0.155** in ZL,
**0.673/0.157** in IT,
and **0.683/0.160** in RF.
All three EM state labels agree on
**196/200** folios; the literal
threshold labels agree on
**197/200**. These are
alternate readings of the same manuscript, so this is transcription robustness,
not three independent replications.

The exact published implementation claims do not survive audit:

- every reading has **200**, not 197, eligible folios under the linked parser;
- the printed threshold and the implemented EM state differ on **13/200** RF
  folios (also 13/200 in ZL and IT);
- the published 31-template inventory is reproduced only when `<->` drawing
  interruptions are deleted and their neighboring groups are concatenated;
- the repository's aligned-drawing repair yields
  **34** RF templates, but still
  deletes comma and `<~>` separators;
- preserving every manual separator yields **35**
  RF templates, while ZL/IT yield
  **32** and
  **31**;
- the published table itself has two reverse-rate rows (`shXo`, `otchXy`), so
  the literal zero-reversal and `2^-31` claim is false.

The safe retained result is therefore a page-level formal regime that modulates
some `ch/sh + o/e` contexts. The exact 31-item template table and its monotonicity
argument are retired. Nothing here identifies sounds, vowels, consonants, words,
a natural language, a cipher operation, meaning, plaintext, or translation.
