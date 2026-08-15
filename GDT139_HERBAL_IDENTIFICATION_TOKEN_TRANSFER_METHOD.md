# GDT139 — Herbal identification-token transfer

## Purpose

This exploratory test asks whether the HPR2 `PAGE_HOST` layer predicts a noisy
external content proxy: recurring head tokens in the published ELV and ThP
tentative plant identifications.  It is not a botanical identification test.
The catalogue guesses are hypotheses, can be wrong, and are not independent
ground truth.

## Frozen external endpoints

Only the already cached human page annotations and the complete f84-free
Herbal page census are used.  `ELVA` is normalized to `ELV` and `THP` to
`ThP`.  Within each explicitly marked source clause, comma/semicolon-separated
candidate strings are stripped of parenthetical citations.  The first
alphabetic token after the fixed stop list in the freezer is the endpoint.
No botanical synonym merging, spelling correction, taxonomy lookup, or
Voynich-form inspection is allowed.  ELV and ThP are separate panels, not
replications.  A scored token must occur on at least two pages and two physical
folios within its source panel.

Every page in a source panel has at least one mechanically extracted candidate,
including pages without a recurring scored token.  Therefore zero means “this
source proposed another extracted head token,” not “the depicted plant is
known not to belong to this taxon.”

## Fixed models

The nuisance-only neighbour model uses Currier, hand, illustration profile,
page layout/counts, and all twelve frozen GDT137 visible-feature indicators.
Four additions are scored separately: exact PAGE_HOST inventory, PAGE_HOST
character trigrams, raw source-group character trigrams, and the HPR2 compiler
signature.  Neighbours exclude the held physical folio.  `k=7`, shrinkage 8,
and binary codelength are inherited from GDT137.

The primary endpoint is aggregate held-folio codelength across all recurring
tokens within each source panel.  Report token, folio, Currier, and
leave-one-source-panel diagnostics.  A shared 10,000-world null permutes the
complete endpoint vector within source × Currier × hand × illustration-profile
strata.  Controls quantify interest; they do not erase descriptive leads.

## Interpretation ceiling

This is a post-hoc archive test of whether formal page texture tracks noisy
human identification vocabulary.  A positive result can nominate a PAGE_HOST
cluster for later prospective work.  It cannot identify a plant or establish
a word, morpheme, POS, sound, language, plaintext, meaning, or translation.
All f84 rows are rejected before retention and no new f84 access is authorized.
