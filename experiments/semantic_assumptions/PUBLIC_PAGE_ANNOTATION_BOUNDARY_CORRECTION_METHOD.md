# Public page-annotation boundary correction

## Purpose

Reparse the 18 cached public `voynich.nu` quire catalogues while ending a page
record at either the next page header or the next folio header.  The former
parser ended records only at page headers, so folio-level prose could be
attached to the preceding verso page.

This is a public-source provenance and record-boundary correction.  It is not
a manuscript-text, grammar, image-recognition, or semantic experiment.

## Frozen rules

- A page starts only at an HTML `TH` whose ID matches `f[0-9]+[rv][0-9]*`.
- A folio header whose ID matches `f[0-9]+` clears the active page before any
  following prose is captured.
- The five public prose fields are retained verbatim after whitespace
  normalization; no tentative identification is silently corrected.
- The old table's page IDs, general descriptions, illustration descriptions,
  text descriptions, source tags, URLs, and role-evidence flags must remain
  exact.  Only falsely inherited `other_information` may change.
- Zodiac illustration identity, month name, and tentative identity are parsed
  only as a contradiction audit.  Tentative identifications remain excluded
  from role evidence.

## Claim ceiling

The result may correct public catalogue record ownership and identify internal
source contradictions.  It cannot establish a Voynich label owner, word,
lexeme, language, plaintext, or translation.
