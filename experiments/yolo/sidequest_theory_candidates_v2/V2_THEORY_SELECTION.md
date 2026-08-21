# Sidequest V2 theory selection

Date: 2026-08-21

Status: speculative abductive selection, not a GDT result or translation. Four
independent candidates were written from the compact ten-page basis without
reading one another. The rubric in `V2_SELECTION_PROTOCOL.md` was frozen before
their outcomes were read.

## Scores

| candidate | grammar /20 | parses /20 | exact /15 | semantics /15 | coherence /10 | history /10 | tests /10 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| executable exemplar-card parser | 20 | 20 | 14 | 13 | 9 | 8 | 10 | **94** |
| cross-page coherence model | 18 | 19 | 15 | 13 | 10 | 8 | 10 | **93** |
| evolved organic codebook | 18 | 17 | 14 | 13 | 9 | 9 | 10 | **90** |
| historical workshop formularium | 16 | 15 | 13 | 14 | 8 | 10 | 8 | **84** |

Scores are comparative judgments, not probabilities.

## Selected architecture

The executable parser wins because it explains the largest number of actual
fixed-page lines with one teachable procedure and exposes a concrete common
deck rather than stopping at generic roles. The selected basis is:

```text
FORMULA-CARD PRACTICAL MEDICAL REGISTER
  + silent picture/page address
  + roughly twenty frequently taught whole cards
  + register/page-local copied tail
  + open Currier-A dossier mode
  + committed Currier-B cell mode
  + payload-bearing terminal cards with COMMIT realization
  + line reflow and rare copied-forward head
  + a separate Astro lookup namespace
```

The upstream source remains a hybrid: abbreviated natural-language material
is compiled into technical cards and forms. Whole-card identity dominates;
productive composition is limited to renderer, closure and a few entrenched
frames.

## Mandatory correction imported from the runner-up

The runner-up found two places where the executable parser overinterpreted:

1. Major close-bearing cards accept field lengths 1–6 and diverse payloads.
   Their exact identities remain real, but no stable dictionary such as
   `SHEDY=RESULT`, `QOKEEDY=ACTION`, `LCHEDY=LOCATION` is established.
2. AIIN occurs at all field positions and never immediately closes. Its best
   class is `PARAMETER/AMOUNT/DEGREE/INDEX/REFERENCE`; specifically numerical
   or quantitative content is only a subordinate guess.

Therefore the selected formula is:

```text
TERMINAL_CARD = unknown local payload identity + COMMITTED realization
```

not typed English result names and not meaningless punctuation.

## Best retained provisional readings

| card/construction | selected role | confidence |
|---|---|---:|
| attached DY/B3 behavior | local field commitment/termination | .78 formal |
| exact `qokaiin` | entry/instruction head | .46 formal |
| exact `qokaiin` | TAKE/USE/ENTER/APPLY-like source class | .27 |
| L/O exact card | link/co-member/general relation | .39 formal |
| AIIN exact card | parameter/amount/degree/index/reference | .28 |
| AIIN specifically quantity | subordinate hypothesis | .15 |
| CTHY exact card | qualifier/prepared/property state | .25 |
| Y exact card | item/unit/reference slot | .21 |
| `Y–AIIN–Y` | paired or typed parameter frame | .34 constructional |
| `Y–AIIN–Y` specifically equal amount | subordinate hypothesis | .12 |
| f82r repeated `qokaiin` | one copied-forward logical head | .52 local parse only |

No entry is a confirmed word, sound, POS or translation.

## Strongest concrete source-like parse

The current miniature grammar is:

```text
HEAD? + ARGUMENT/ITEM* + LINK/STATE/PARAMETER* + TERMINAL_CARD(COMMIT)
```

with inherited owner and omitted unchanged values. Its least-bad free
paraphrase is:

> For the pictured owner, take/set the current item; relate it to the stated
> parameter or prepared condition; commit the local cell; carry an unfinished
> head across reflow when necessary.

This is a source-class reconstruction, not plaintext.

## Mandatory decisions

1. **Remembered unit:** mixed, strongly weighted toward exact whole cards.
2. **Upstream content:** hybrid abbreviated natural language plus technical
   notation.
3. **Closures:** local commitment fused to an unknown payload card; no typed
   semantic closer dictionary yet.
4. **`Y–AIIN–Y`:** paired/typed parameter frame retained; equal-amount reading
   downgraded.
5. **Repeated `qokaiin`:** copied-forward logical head is the best local parse,
   but it remains one witness and may be dittography or ordinary repetition.
6. **Cards:** `qokaiin` entry-head and L/O relation are the best new leads;
   AIIN/Y/CTHY remain broader parameter/tag/state classes.
7. **Astro:** same workshop pedagogy, separate local namespace; no demonstrated
   WHAT/HOW/WHEN pointer.
8. **Loss condition:** the theory loses if geometry/stroke continuation explains
   portable-card placement as well as record roles, or if the proposed head,
   link and parameter behaviors do not survive fixed-page matched controls.

## Candidate hashes

- `CANDIDATE_V2_EXECUTABLE_PARSER.md`:
  `02fd06f20d33d4fe9f10af21d2fa90c00f7897180a6d776cfd14c5ef4612ac53`
- `CANDIDATE_V2_CROSS_PAGE_COHERENCE.md`:
  `5836bee102dd8d659167e589b6a65c0186971f213a3cc61e08fe3cdbdc221d6e`
- `CANDIDATE_V2_EVOLVED_CODEBOOK.md`:
  `a2457215470fc094b662efdc5200a990248c655471197cbf681f7bf899f6a4e3`
- `CANDIDATE_V2_HISTORICAL_WORKSHOP.md`:
  `8332cd1670f8c62bf0ec4575e2b863b85bd210991abe282b9767d68d8183ad05`

The compact current theory is the only default continuation context. These
candidate files are recovery material.
