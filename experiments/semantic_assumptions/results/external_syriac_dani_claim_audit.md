# External Syriac DANI claim audit

Status: **HOLD_AS_LANGUAGE_OR_TRANSLATION_EVIDENCE_UNREPRODUCIBLE_NONHELD_AND_VISUAL_COMPONENT_EXCLUDED**.

This is more testable than a prose-only translation claim: the latest Zenodo version publishes an EVA-to-consonant table, a 1,389-key JSON lexicon, and a coverage pipeline. The original one-PDF record was superseded the next day and is not used for this conclusion.

The deposit still omits its exact `lsi_all.txt` input. The released Python only implements parsing, skeleton conversion, affix stripping, and coverage; it does not implement or preserve the 500 permutations, comparison lexicons, plant tests, language comparisons, scores, or random seeds. The current metadata still reports z=3.83 and a 14.9-point gap while its PDF reports z=4.86 and a 42.2-point gap.

The reported 86.9% result is not held out. The mapping, domain lexicon, token filter, vowel deletion, gallows handling, prefix/suffix stripping, and downstream word choices are evaluated on the same manuscript. Its null permutes only ten core consonant assignments; it does not reproduce the larger search over those other choices. The headline is frequency-weighted token coverage, while no type-level or token-concentration robustness and no exact finite-permutation p-value formula are supplied.

The deposited lexicon itself has 1,441 entries under 1,389 keys, but 1,334 entries lack a source field and 570 keys contain consonants the released mapping cannot emit. Its domain tags also do not reproduce the PDF's 1,375-key no-function comparison: removing every function-tagged key leaves 1,243, while retaining mixed-sense keys leaves 1,251.

The claimed plant support comes from AI visual identification of 111 drawings, which is excluded by the active no-neural-vision policy. The paper itself says that no paragraph has been read as coherent connected Syriac prose by a specialist and estimates only 10--15% word-level accuracy.

Therefore no Syriac mapping, medical gloss, phrase, or plaintext is imported. Reopen when the exact corpus, complete statistical code and scores, selection history, and held evaluation are public and independently reconstructable. This hold does not establish that a Syriac or pharmaceutical hypothesis is false.
