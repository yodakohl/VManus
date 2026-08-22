# V77 R2 — source-first historical codebook attestation audit

## Result

**No exact V77 card word is documentarily attested.** The frozen historical
inventory contains 48 exact source-language entry↔code rows from two real 1379
keys, but none supplies the category required by any of the eleven exposed
procedural mnemonics. All eleven are therefore withdrawn to
`EXEMPLAR_VALUE_UNKNOWN`. Three cards remain exclusively
`FORMAL_LABEL_NOT_WORD`; a fourth formal nonword channel is retained alongside
the withdrawn `MASS?` mnemonic. The ten frequency-selected noncontrols had no
prior word gloss and remain unknown.

This is a strict positive-attestation failure, not proof that such concepts did
not exist in fifteenth-century writing. The sampled keys are predominantly
diplomatic and political. Under the V77 rule, however, general period
plausibility and ordinary recipe prose cannot fill a missing key entry.

| quantity | result |
|---|---:|
| source objects/keys audited | 6 |
| exact historical entry↔code rows admitted | 48 |
| authoritative target cards | 24 |
| fixed Herbal/Biological occurrences inspected | 197 |
| old mnemonic handles withdrawn | 11 |
| formal-only cards | 3 |
| formal nonword channels retained (including the `MASS?` card's separate channel) | 4 |
| card words admitted | **0** |

Machine-readable endpoint: `NO_V77_R2_CARD_WORD_ATTESTED`.

## Source-first order and exposure disclosure

The source inventory was written and hashed before the V69 card dictionary was
queried. The source phase read no card-table column and performed no search for
a desired German/English word. The bounded target was then conformed exactly to
the central `V77_TARGET_FREEZE.tsv`: fourteen controls plus the top ten
recurrent noncontrols, 24 identities and 197 occurrences.

The role was nevertheless required to read the current route/theory before the
experiment, so routing-level legacy mnemonics were unavoidably already visible.
This is not claimed as perfect cognitive blinding. The protection actually
implemented is narrower and auditable: no desired-word query selected a source
or source entry, the documentary inventory was frozen first, and every later
match requires a literal source row with all mandatory fields.

Hashes and ordering evidence are in `V77_R2_SOURCE_FREEZE.json` and
`V77_R2_FREQUENCY_CANDIDATE_FREEZE.json`.

## Historical corpus

### Gabriel de Lavinde, 1379

Aloys Meister's documentary edition reproduces Gabriel de Lavinde's key
collection from **Archivio Apostolico Vaticano, Collect. 393, ff. 166–181**.
The collection heading dates it to 1379. Key 13 on printed p. 173 contains a
substitution alphabet and a nomenclator; key 26 on p. 175 contains altered
vowels and another nomenclator. The audit admitted only rows whose printed code
could be transcribed without guessing an ornate sign.

Examples of the exact admitted pairs are:

| source-language entry | opaque code | key/page |
|---|---|---|
| `cardinalis` | `3p` | key 13, p. 173 |
| `rex Anglie` | `gl` | key 13, p. 173 |
| `Dux Bavarie` | `ami` | key 13, p. 173 |
| `Regina` | `ba` | key 13, p. 173 |
| `Imperator` | `aa` | key 13, p. 173 |
| `Sicilia` | `fa` | key 13, p. 173 |
| `Papia` | `tp` | key 13, p. 173 |
| `Mediolanum` | `lo` | key 13, p. 173 |
| `Gentes armorum` | `gm` | key 13, p. 173 |
| `Matrimonium` | `ln` | key 13, p. 173 |
| `pax` | `pR` | key 13, p. 173 |
| `Massilia` | `mm` | key 26, p. 175 |
| `Napoli` | `mh` | key 26, p. 175 |
| `Lo cancelier` | `ph` | key 26, p. 175 |

The full 48-row transcription, including exact entry, code, key, shelfmark,
date, edition location, citation, stable locator and confidence, is in
`V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv`. Rows with visually ambiguous codes
were excluded rather than normalized speculatively.

Source: Aloys Meister, *Die Geheimschrift im Dienste der päpstlichen Kurie von
ihren Anfängen bis zum Ende des XVI. Jahrhunderts* (Paderborn, 1906), printed
pp. 171–175, especially [p. 173, key 13](https://archive.org/details/diegeheimschrift00meis/page/173/mode/1up)
and [p. 175, key 26](https://archive.org/details/diegeheimschrift00meis/page/175/mode/1up).

### Mantua, 1395–1404

Meister reproduces the Mantuan `Cum Paulo 1395` key from **Archivio di
Stato di Mantova, E. V. 3**, and a `Cum Simeone de Crema` key dated 1401.
They are genuine in-period cipher-key controls, but the displayed keys do not
supply an admissible word↔code list. Meister also reports that a 1404 Mantuan
nomenclator already used numbers 1–38; the cited narrative does not print the
38 plaintext mappings. Accordingly these three sources contribute **zero**
word entries rather than guessed ones.

Source: Aloys Meister, *Die Anfänge der modernen diplomatischen
Geheimschrift* (Paderborn, 1902), [pp. 38–41](https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA38).

### Pisa, 1442

The 7 November 1442 Pisan-archive example includes seven coded abbreviations.
The available text extraction preserves their plaintext descriptions but not
their graphic signs reliably enough for this exact-entry audit. The real key is
therefore recorded as a source object, with **zero admitted rows**. This is a
deliberate strict failure, not evidence that the abbreviations were absent.

Source: Meister 1902, [pp. 57–59](https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA58).

## What the frozen sources do and do not attest

The admitted vocabulary consists of people, rulers and offices; places and
political communities; followers/armed people; and a few political/social
relations such as `Matrimonium` and `pax`. It contains no exact entry for the
minimal categories proposed by `TEMPERIEREN?`, `ANWENDEN?`, `MASS?`,
`ANSATZ?`, `SPÜLEN?`, `KLAR?`, `ZIEL?`, `ABLASSEN?`, `VORIGES?`, `BEREIT?`
or `ANTEIL?`.

Nearness is not a match. A place name does not attest `ZIEL?`; `pax` does not
attest readiness or closure; a two-letter historical code resembling a display
form would not identify a Voynich card. No surface comparison was performed.

## Complete card and occurrence audit

`V77_R2_CARD_DECISIONS.tsv` covers all 24 frozen identities and
`V77_R2_OCCURRENCE_AUDIT.tsv` covers all 197 occurrences. The latter retains
page, locus, record, field, statement and the exposed V69 context so the
decision can be checked occurrence by occurrence.

The occurrence audit does not rescue a dictionary value because those
contexts were themselves authored under the exposed creative mnemonics. It can
still identify reasons to be stricter:

- `b5df…` changes from an Herbal “clear” condition to an unspecified
  Biological test state.
- `e0b6…` spans flower opening, general readiness and generic test states.
- `b921…`, the most frequent noncontrol, spans many incompatible exemplar
  actions and deictic-owner uses.
- `2cc0…` receives four different actions within H5 alone.
- Several other extras have recurrent formal context patterns, but a repeated
  pattern without a frozen word category or independent historical entry is
  not a dictionary word.

Conversely, the three explicit formal operations may remain useful editorial
bookkeeping. Their status is exactly `FORMAL_LABEL_NOT_WORD`; they are not
translations.

## Withdrawals and ceiling

`V77_R2_WITHDRAWALS.tsv` replaces all eleven mnemonic handles by
`EXEMPLAR_VALUE_UNKNOWN`. For `2f1…`, the nonword
`VORGABEPARAMETER?` channel may still be displayed separately as a formal
operation, but `MASS?` is withdrawn.

The header-only `V77_R2_ATTESTED_CARD_ROWS.tsv` is intentional: no row passed
all documentary fields. Even a future passing row could license only
historical dictionary granularity. It would not establish a Voynich word,
lexeme, sound, language, plaintext, translation or historical relationship to
the cited codebook.

No additional manuscript page was opened. `f84` and `f84r` remained sealed.
