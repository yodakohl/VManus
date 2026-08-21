# V19 R1 — complete four-article workshop reading

Date: 2026-08-21

Status: **maximally abductive sidequest reconstruction**, not deciphered
plaintext.  Every card receives a concrete English workshop default because
that is the rule of this round.

## Result

I would teach an apprentice that these four pages are illustrated entries for
medicinal simples.  The picture silently owns the article's plant; the visible
cards tell the apprentice which part, time, liquid, preparation, dose,
application, indication or storage step to recover.  A physical line is only a
place where the pen turned back.  It need not end a statement.

This produces complete coverage:

- 4/4 Herbal pages;
- 100/100 visible events;
- 66/66 exact indivisible card types;
- 55/55 singleton cards, each compared with two other concrete meanings;
- 11 broad source classes rather than 55 invented diseases or exotic drugs;
- zero blank meanings.

The selected compact article inventory is:

```text
NAME/SYNONYM
PLANT PART OR PRODUCT
HABITAT/GATHERING
QUALITY OR PROCESS CONDITION
PREPARATION
MEDIUM/ADJUVANT
MEASURE/DOSE
APPLICATION
INDICATION
REFERENCE/CONTINUATION
STORAGE/CLOSE
```

All 100 events inherit a silent contextual argument, but only from five
teachable buckets: pictured plant/part (19), current material/preparation (39),
current preparation plus patient/place (14), current preparation plus vessel
(6), or an antecedent batch/part/instruction (22).  Thus the reconstruction
does not need a different invisible entity for every rare card.

## Freeze before text

I inspected the color scans and wrote
`V19_R1_VISIBLE_PLANT_FREEZE.tsv` **before** assigning V19 meanings.  The frozen
visual observations are deliberately coarse:

- **f10r:** paired broad serrate leaves, unequal blue composite heads, creeping
  base and two red storage bodies; best concrete guess `twin-root waterwort`,
  fallback `broad-leaved damp-bank simple`;
- **f11r:** dense cushion of crenate leaves with many small blue flowers and
  three toothed roots; guess `spring-bank saxifrage/brooklime-like simple`;
- **f55v:** enormous lanceolate leaf cup, tall red stalk, lattice head and
  creeping fibrous root; guess `large-leaved marsh rhizome`;
- **f56r:** pale scale-bearing stalk and several contrasting blue head stages;
  guess `tall spiny thistle/teasel-like simple`.

Water is not painted explicitly.  It enters f10r and f55v as an allowed habitat
or recipe-medium guess because creeping rhizomes/storage bodies and the
large-leaved marsh habit support it.  It is not used as a universal key.

The inspected images were the color folios made available from Yale scans via
the [Voynich folio gallery](https://www.voynich.com/folios/).  No unlicensed
folio was used.

## Why this is an ordinary 1420 workshop genre

This page architecture needs no modern database.  The British Library
catalogue describes Egerton MS 747 as containing the *Tractatus de herbis*, an
*Antidotarium*, substitutions, weights/measures and plant-name synonyms in one
medical volume
([catalogue record](https://searcharchives.bl.uk/catalog/032-001983805)).
That makes names, synonyms, doses and preparations an ordinary shared scribal
inventory.  A survey of medieval Mediterranean pharmacology gives the common
recipe bundle explicitly: drug name, indication, ingredients with quantity,
preparation, administration and dosage
([NCBI Bookshelf](https://www.ncbi.nlm.nih.gov/books/NBK606146/)).  These sources
license the **shape** of my reconstruction; they do not identify any Voynich
card.

## The four selected articles

The fluent full readings are in `V19_R1_COMPLETE_HERBAL_ARTICLES.md`.  In
short:

1. **f10r:** a twin-root damp-bank simple.  Store roots, pound root and leaf,
   use a warm measured stomach remedy; a second recipe uses water decoction,
   expressed leaf juice and oil preservation.
2. **f11r:** gather a spring-bank cushion herb before its blue flowers open;
   strain twice to clarity, cool it in an open jar, and bind the warm leaves on
   swelling.
3. **f55v:** boil marsh-rhizome portions in white wine, steep/decant and wash;
   a second warm preparation mixes equal portions and is kept covered for
   fresh use.
4. **f56r:** a part-by-part thistle dossier: root, flower-head, whole herb,
   seed-head, dried scale-leaf, honey preparation and a measured pale opened
   head.

The awkward repetitions of CURRENT-PORTION and SAME-PREPARATION are retained
rather than paraphrased away.  They are exactly the kind of formula a workshop
can copy reliably.

## Exact-card decisions

The V18 recurrent deck remains fixed except where the four-page evidence makes
its old expansion concretely contradictory.  One recurrent correction is
required:

```text
d665560c...  f11r dchol / f56r schol
old: the pictured simple is called one identical local name
new: take the whole pictured simple
```

The two drawings are plainly different; the old literal-name reading would
give them the same name solely because the formal card recurs.  A reusable
whole-simple instruction keeps exact-card identity and makes both articles
readable.

Two singleton apparatus-flavored V18 defaults also become Herbal instructions:

```text
f11r tchody       leave jar mouth uncovered until cool
f56r cheeckhody   bind poultice overnight, then remove
```

They were never members of the stable V18 recurrent bridge.  Forcing an
`outlet` into f56r's dry plant-part dossier costs more silent machinery than a
normal poultice close.

## Apprentice production rule

1. Draw or select the pictured simple first.
2. Open an article or subrecipe with NAME, GATHER or NEXT-PART.
3. Keep the pictured simple active until another page or explicit continuation
   changes it.
4. Keep the latest named plant part, liquid and batch active across physical
   line ends.
5. Use the recurrent cards unchanged: CURRENT PORTION, USUAL MEASURE,
   FOREGOING PREPARATION, READY, SAME BATCH, NEXT PART.
6. Close only when a storage/application card actually closes a subrecipe.
7. For a rare whole card, memorize its phrase from the exemplar; do not derive
   it from its visible letters.

To read back, expand each whole card, restore only the currently active plant,
part, liquid, place or vessel, then smooth the result into continuous prose.

## Errors a real apprentice would make

- treating every physical line as a new sentence;
- forgetting which portion `this present portion` points to;
- copying the f11r second straining step only once;
- taking f56r NEXT-PART as a plant name and thereby creating four false plants;
- carrying `white wine` from one subrecipe into the next after a close;
- expanding the same whole-simple instruction as the same botanical name on
  two different illustrated pages;
- mistaking a close card for a picture label because the drawing forced the
  text around available space.

## Remaining pressure points

The weakest stretches are f10r's four consecutive measure/portion cards and
f56r's many independent part recipes.  The first may conceal a real enumerated
ratio; the second may be a list of names or synonyms instead of preparations.
Those rivals remain alive.  Nevertheless, this candidate wins as a workshop
model because one short deck yields four readable articles without leaving a
single card empty.

No source spelling, tuple coordinate, PAGE_HOST decomposition or glyph
resemblance was used.  f84 and f84r remained sealed.
