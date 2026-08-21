# V19 R4 — chancery correction of the complete Herbal articles

Date: 2026-08-21

Role: **R4, chancery scribe and corrector around 1420**.  This is an
independent maximally abductive sidequest reconstruction, not deciphered
plaintext.  I did not inspect sibling V19 candidates.  All English expansions
are reversible workshop defaults: a concrete rival may replace them later,
but no card is left semantically blank.

## Frozen evidence order

I first inspected the four color folios and wrote
`V19_R4_VISIBLE_PLANT_FREEZE.tsv`.  Only after that file existed did I assign
card meanings.  The freeze records organs and layout without using text:

- f10r: broad opposed leaves, one open and one closed head, a creeping base and
  two red swollen terminal rootstocks;
- f11r: a dense cushion of crenate leaves and blue flowers above three toothed
  strap-like underground bodies;
- f55v: an immense cup of lanceolate leaves, regular compound head, fibrous
  crown, divided rhizome and one unusual lateral swelling;
- f56r: a mostly leafless scaly stalk carrying five unlike head forms,
  including a spiral disk and two spiny burrs; its root is off-page.

No page depicts water.  Water is nevertheless permitted as a written habitat
or recipe medium.  That distinction matters on f10r and f11r.

## Historical source frame

The smallest source inventory is an illustrated book of simples with short
preparations and uses, not four botanical descriptions forced into a fixed
modern schema.  This is historically ordinary: the Herbaria manuscripta
catalogue describes medieval herbals as medical treatises on simple medicines
and records Latin and vernacular names; the Leiden description of BPL 3103
shows that a late-medieval Herbal could begin as pictures plus names and
receive fuller multilingual commentary later; the National Library of
Medicine notes that medieval/early printed herbals were compilations with
instructions for medical use.  These comparators license a mixed inventory of
name, habitat, gathering, part, medium, preparation, measure, use and storage.
They do not identify any Voynich card.

Sources consulted:

- https://herbaria.phil.muni.cz/en
- https://digmanclass.universiteitleiden.nl/manuscripts/bpl-3103/
- https://circulatingnow.nlm.nih.gov/2015/07/09/medieval-herbals-in-movable-type/

## Main correction to V18

The exact card `d665560c...` occurs at the head of f11r.4 and f56r.8.  V18
called it a local plant name.  Two different pictured owners make that reading
self-contradictory unless the pages duplicate one synonym by accident.  I
therefore revise it to the concrete shared rubric:

```text
dchol / schol  =  for painful swellings
```

It gives f11r a measured poultice and f56r a wine-ground overnight dressing.
This is the only recurrent-card contradiction strong enough to override V18.
The other V18 recurrent defaults are retained, with only local grammatical
inflection.

## Four complete article readings

The full continuous readings are in `V19_R4_COMPLETE_HERBAL_ARTICLES.md`.
Their compact content is:

| page | pictured owner | reconstructed article |
|---|---|---|
| f10r | broad-leaved creeping simple with paired swollen rootstocks | red-wine root paste for pain; fresh warm application; running-water habitat; decoction plus expressed juice; before-flowering collection; bitter stored portion |
| f11r | blue-flowered cushion simple | spring-bank gathering; leaf wash pressed through linen into a clear eye wash; swelling poultice; warm wine preparation of flowering tops |
| f55v | great broad-leaved rhizomatous simple | white-wine steep; strained measured mixture; second warm wine mixture for a slow-healing wound, jarred and used fresh |
| f56r | spiny simple displaying several head stages | root-and-wine application; swelling poultice; dried mature-head remedy; fresh honey poultice with pale flower centre |

Sentences explicitly cross f10r.2→.5, f10r.6→.8→.9,
f11r.1→.4, f56r.5→.7, f56r.12→.13 and f56r.18→.19.  The
physical line therefore controls placement and copying but does not supply
punctuation.

## Dictionary economy

The 66 exact types use 12 broad article classes:

```text
MATERIAL_OR_MEDIUM       PREPARATION_ACTION
HEAT_OR_STEEP            APPLICATION
STORAGE                  GATHERING
HABITAT                  MEASURE_OR_PORTION
INDICATION               RELATION_OR_CONTINUATION
PROCESS_CONDITION        PROCESS_ACTION_OR_CLOSE
```

Only four persistent silent picture-owner activations are charged, one per
page.  Pronouns and omitted imperative subjects inside an activated article
are ordinary continuation, not eighty-five independent repairs.  More
specific source-class labels in the dictionary describe the selected phrase;
they are subdivisions of these twelve reusable classes, not 66 invented
diseases or ingredients.

## Copying, abbreviation and segmentation audit

1. **f10r adjacent OR–OR.**  I read two reserved draughts because each later
   receives a current-portion pointer.  Dittography remains the strongest
   null; deleting one OR produces a shorter but still grammatical recipe.
2. **f10r CHOL–X–CHOL.**  This looks like a framed antecedent construction.
   A copied repeated abbreviation is viable, but the intervening batch card
   gives the frame useful work.
3. **f10r/f11r Y repetition.**  The short pointer may reflect line filling or
   resumption as much as quantity.  The selected reading uses first, second
   and repeated portions without claiming a numeral.
4. **f11r adjacent long straining forms.**  V18 made both “strained through
   cloth”.  I separate wash from linen pressing because exact cards differ and
   the following clarity gate gives a three-step sequence.  Scribal
   amplification or a bad source split remains plausible.
5. **f56r CHO/SHO.**  The repeated page-local card works as a dossier command
   whose object is the following card.  An exemplar heading copied before
   selected parts is the strongest nonlexical rival; both are learnable by a
   workshop.
6. **Text around drawings.**  The images preceded the writing.  Broken and
   displaced lines therefore support reflow, not semantic diagram ownership.
   No meaning is inferred merely because a word lies near a root or flower.
7. **Whole-card segmentation.**  Each default attaches to the frozen GDT327
   exact tuple.  A different historical JOIN/SPACE analysis could make one
   visible group part of a larger abbreviation.  Every singleton row records
   this null rather than pretending segmentation is solved.

## Why the resulting system is teachable

A corrector needs only this rule: activate the pictured simple once, copy an
exact whole-card for each source phrase, carry the current material across
line breaks, and use the common reference/action cards unchanged.  Rare cards
come from the page exemplar and need not be decomposed.  A second hand can
learn the common deck plus page-local exemplars without learning a modern
database or an elaborate cipher.

Expected errors are skipped rare cards, duplicated short reference cards,
wrong continuation wrappers at a new physical line, premature punctuation at
a picture-induced break, and accidental replacement of one copied local card
by a visually similar neighbor.  Those are ordinary workshop errors and form
the explicit null column in the interlinear.

## Deliverable and ceiling

- 100/100 events have a concrete default and contextual reading;
- 66/66 exact Herbal types have one selected phrase;
- 55/55 four-page singleton types have two additional concrete rivals;
- 12 broad semantic classes and four persistent picture-owner activations;
- no neutral placeholder and no phonetic, substring or PAGE_HOST inference;
- f84 and f84r were not accessed.

This candidate is intentionally bolder than the scientific GDT route.  It is
the strongest coherent chancery reconstruction of these four pages, not proof
that the source actually mentioned running water, wine, wounds, eyes or
swelling.
