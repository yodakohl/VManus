# GDT614 historical model note

Date: 2026-08-29

This note constrains the synthetic V2 grammar; it does not identify the
Voynich language, script, genre, plaintext, or meaning.

## Two attested families, not one free hybrid

Late-medieval abbreviation and diplomatic nomenclators supply complementary
mechanisms, but no cited witness establishes every GDT614 role as one
homogeneous word grammar.

- Cappelli distinguishes truncation, contraction, fixed/context signs,
  superscripts, and conventional word/phrase signs. A 3-shaped `est` sign can
  stand alone and occur terminally in `prodest` and `interest`, directly
  supporting licensed embedded macros rather than unrestricted whole-word
  atoms: [Cappelli, *Elements of Abbreviation*](https://kuscholarworks.ku.edu/bitstream/handle/1808/1821/47cappelli.pdf),
  [Vatican Library guide](https://spotlight.vatlib.it/latin-paleography/feature/10-4-system-of-abbreviation-and-ligatures).
- The c.1400 Wycliffite Bible Dresden Mscr.Dresd.Od.83 conditions similar
  superscripts on host, lexeme, word edge, line edge, and graphic state:
  [SLUB catalogue](https://katalog.slub-dresden.de/id/0-1646789873),
  [Grzybowska study](https://czasopisma.kul.pl/index.php/LingBaW/article/view/5665).
  Its learned *nomina sacra* also show memorized stems with exposed endings:
  [study and manuscript evidence](https://repozytorium.kul.pl/server/api/core/bitstreams/3e0b8bb3-3fe8-4fd6-a2f2-f8eebf4e85d2/content).
- Italian keys from 1379--1448 combine alphabetic carriers, syllables, word
  signs, nomenclator entries, homophones, punctuation, and genuine nulls. The
  dated 1424, 1435, 1442, and 1448 inventories are especially close in time:
  [Somogyi 2016](https://ojs.ppke.hu/verbum/article/view/405).
- Reproduced Venetian 1411 and Urbino 1440 keys show literal fallback, nulls,
  nomenclator entries, and a `qua/que/qui/quo/quu` syllable family, but their
  nomenclator codes remain atomic:
  [Friedman/NSA summary](https://www.nsa.gov/Portals/75/documents/news-features/declassified-documents/friedman-documents/publications/ACC21609/41768429080752.pdf),
  [reproduced keys](https://www.govinfo.gov/content/pkg/GOVPUB-D-PURL-gpo58694/pdf/GOVPUB-D-PURL-gpo58694.pdf).
- Giovanni Fontana's Venetian 1420--1430 captions can switch between clear and
  cipher registers, a warning that visible mixture need not be token-internal
  morphology: [BSB Cod.icon. 242](https://www.digitale-sammlungen.de/de/details/bsb00013084).

## Frozen interpretation for V2

GDT614 tests only an `ABBREVIATION_PROFILE`:

- `CONTEXT` is hosted next to a literal and never floats;
- `MACRO_CORE` has a fixed side license;
- `NULL_LAYOUT` is a bounded word-edge layout event, not cipher epsilon;
- `CONNECTOR` remains an abstract internal formal role, not a proposed reading
  such as *et*;
- one hard role per primitive is a synthetic identifiability restriction, not
  a claim about medieval allography.

The five fixed macro licenses are:

| card | output | license |
|---|---|---|
| primitive macro | `ibus` | `LEFT_HOST` |
| macro:1 | `con` | `RIGHT_HOST` |
| macro:2 | `runt` | `LEFT_HOST` |
| macro:3 | `erunt` | `STANDALONE_OR_LEFT_HOST` |
| macro:4 | `reliqu` | `RIGHT_HOST` |

A nomenclator profile would instead require atomic macro words and genuine
cipher nulls. It is not silently folded into GDT614 and would need a separate
registered truth/recovery experiment.
