# Warburg special-circle metadata prescreen

## Purpose

Screen public, human-authored catalogue metadata in the Warburg Institute
Iconographic Database before opening any image, manuscript, or paper.  The
three targets are the surviving acquisition gaps with the strongest
special-circle topology:

- f67: a complete twelve-wind or related circular homologue with a readable
  owned text sequence;
- f57v: a four-person wheel joining seasons/elements/qualities with explicit
  ownership of both four-item text registers;
- f68r2: a Moon-above/Sun-below diagram inside a ring of stars, with readable
  owned circular text and an interior star-associated label.

This is a metadata-worth screen, not image comparison and not a decoder-claim
review.  It cannot prove that an uncatalogued or undescribed image is absent.

## Public sources

Use only:

- `https://iconographic.warburg.sas.ac.uk/results`, queried through the public
  simple-search form;
- the public Warburg object records returned by those queries;
- `https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s28g84mm25j.xml`, the
  official Durham catalogue record for Hunter 100.

Require HTTP 200 at each exact URL with no terminal `Location` header.  Do not
request any Warburg asset, thumbnail, zoom image, IIIF manifest, Durham image,
PDF, or bibliography body.

## Fixed search strings

Post each literal query with `mi_adv_search=no` and
`mi_search_type=simple`:

1. `"four seasons"`
2. `"four elements"`
3. `four seasons elements`
4. `four seasons figures`
5. `four seasons elements figures`
6. `Sun Moon stars`
7. `Sun Moon stars circle`
8. `Sun Moon stars ring`
9. `Sun Moon stars medallions`
10. `twelve winds`
11. `twelve winds circle`
12. `winds faces circle`
13. `winds personifications circle`
14. `wind heads circle`

Project only the reported item count and each result card's stable object ID
and human title.  For the complete broad `twelve winds` and `Sun Moon stars`
results and the sole `four seasons elements` result, open only the HTML object
record and retain its human-written catalogue values.  Exclude forms, scripts,
media identifiers, asset links, image dimensions, tokens, contact text, and
rights boilerplate.

## Fixed target gates

The f67 candidate must have all of:

- twelve winds or another explicit twelve-part wind system;
- a ring/circle/wheel/rota/rose relation;
- human text stating a readable owned label, name, caption, inscription, or
  text sequence.

The f57 candidate must have all of:

- seasons and elements or qualities;
- four human figures, portraits, philosophers, heads, or faces;
- an explicit owned slot/register relation, not a generic correspondence
  diagram.

The f68 candidate must have all of:

- Sun, Moon, and stars;
- a ring/circle/annulus relation;
- human text stating label, caption, inscription, or text ownership;
- an upper/lower or above/below relation.

Classify the broad f67 records descriptively by the exact human paths
`Geography / Weather / Winds / The twelve winds` and the Homeric description
`twelve skins containing winds`.  Classify the broad f68 records descriptively
by the exact human phrases
`Spheres with Stars, Sun and Moon` and
`Creation of sun, moon and stars`; all others remain `OTHER`.

## Worth decision

Escalate only a record passing every target gate.  A generic twelve-winds
record, Homeric winds episode, broad element-season correspondence, ordinary
planetary spheres, Creation imagery, or an emblem does not justify image or
paper review.  Hunter 100 may be retained as a readable diagram-family
comparator only if Durham independently confirms the four-element/quality/
season description.

## Ceiling

This prescreen may close the current Warburg metadata lead and retain broad
comparanda.  It cannot assign a person, season, element, quality, direction,
astronomical object, label, word, sound, language, cipher operation, plaintext,
meaning, or translation to the Voynich manuscript.
