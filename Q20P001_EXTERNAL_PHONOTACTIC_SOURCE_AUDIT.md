# Q20P001 external phonotactic source audit

Status: `FROZEN_BEFORE_Q20_TARGET_SCORING`

Date: 2026-08-14

## Source

The external comparator is the CLDF conversion of **ASJP Database v21** at
commit `012795349540ba0dabfdcf2be16f2e77622f62d6`:

- repository: https://github.com/lexibank/asjp
- release tag: `v21`
- editors: Soren Wichmann, Eric W. Holman, Cecil H. Brown, Matthew S. Dryer,
  and Qibin Ran (eds.), 2025
- license: CC BY 4.0
- database documentation: https://asjp.clld.org/help

ASJP aims to supply the same stable 40-item basic-vocabulary list across
languages in a standardized phonetic code. The Lexibank CLDF conversion
provides tokenized `Segments` normalized through CLTS. This makes it suitable
for a small, uniform phonotactic comparison. It does not make the forms
historical, dialect-complete, error-free, or representative of running prose.

## Frozen language panel

The target panel was named by the user: `GEORGIAN`, `MINGRELIAN`, `LAZ`, and
`SVAN`. The controls were selected before any Q20 score:

- regional unrelated controls: `ARMENIAN`, `CHECHEN`, and `AVAR`;
- typological/geographical controls: `BASQUE`, `TURKISH`, `GREEK`,
  `ARABIC_QURANIC`, and `FINNISH`.

Every language comes from the same ASJP release and transcription pipeline.
For each of the 40 starred core concepts, the lowest stable ASJP FormTable ID
is selected. The ASJP `+` internal boundary marker is removed rather than
treated as a phoneme. Loans are retained and never used to select a record.
The resulting lists contain 39 or 40 forms each and inventories of 18--35
phoneme tokens.

Exact language metadata, inventories, coverage, upstream table hashes, and
derived-output hashes are frozen in `q20p001_language_manifest.tsv`,
`q20p001_asjp_v21_core40.tsv`, and `q20p001_source_provenance.json`.

## Capacity and limitations

This is deliberately a low-capacity phonotactic reference, not a lexicon for
word matching. Forty isolated basic forms are too small to characterize the
full phonotactics of any language, especially morphologically complex running
text. Modern Georgian and the modern low-resource Kartvelian lists are not
medieval language witnesses. `ARABIC_QURANIC` is a historically relevant
control name in ASJP, not an age-matched corpus for every comparator.

No concept gloss, cognacy field, source word identity, or recognizable word is
available to mapping optimization or evaluation. The experiment may compare
only sequence probabilities of phoneme tokens.

## Claim ceiling

Even a positive result would establish only compatibility with a small ASJP
phonotactic profile under a highly flexible many-to-one mapping. It cannot
establish a language, historical stage, sound value, word, morpheme, meaning,
plaintext, translation, authorship, or origin.
