# V14 R2 — iatromedizinisches Arbeitsbuch mit Bild-, Anwendungs- und Wahlregister

Date: 2026-08-21

Role: **R2 — medical/Herbal scribe around 1420**. This is an independent,
abductive sidequest report. It is not a GDT result, decipherment or plaintext
translation.

## Decision

The strongest single purpose is a **practical iatromedical concordance** made
for consultation in a small medical workshop:

```text
HERBAL     WHAT may be used: pictured simples and their open dossiers
BIOLOGICAL HOW/WHERE it is used: bath/application configurations
ASTRO      WHEN/UNDER WHAT INFLUENCE: compact election/prognostic selectors
```

This is not one modern database whose columns recur unchanged. It is a
late-medieval composite working book whose three source genres were reduced to
one workshop's learned abbreviation cards. The formula-card system is its
production format; medical consultation is its likeliest purpose.

Working confidence:

- practical medical/materia-medica purpose: **.68**;
- the narrower WHAT/HOW/WHEN integration: **.57**;
- formula-card/register production architecture: **.86**;
- a single doctrine or a cross-register pointer dictionary: **.24**.

The strongest rival is a **generic indexed pattern/form book**. I retain it at
**.43**. It explains stencils, exact copied cards, multiple hands and image-led
layout, but it explains less well why expensive, content-rich pictures fall
into three historically cohabiting medical source classes and why each class
has the textual density appropriate to its practical use.

## One rule that explains the three registers

The amount of text is inverse to the amount of the entry already supplied by
the picture:

```text
Herbal drawing supplies TOPIC only
  -> long open article is still required.

Bio drawing supplies TOPIC + stations/relations + a repeated form
  -> short slot values and local commitments suffice.

Astro diagram supplies TOPIC + slots + order/topology
  -> labels and local lookup entries suffice.
```

This is a historically ordinary difference among a herbal article, an
application memorandum and a rota/table. It requires no Currier-language split
and no universal semantic meaning for a physical field.

## All ten pages as one consultation apparatus

| page | visible layout | best source-class function |
|---|---|---|
| f10r | one pictured simple; two open text records reflowed around the plant | a fuller simple monograph: name/class, description and one or more property, habitat, preparation or use clauses |
| f11r | one pictured simple with open lines fitted to the drawing | a second monograph copied in the same Herbal-A article practice, not the same lexical entry |
| f55v | pictured simple, but B-register writing and three closes in four fields | bridge sheet: simple dossier passing into a prepared/dispensatory entry with locally checked specifications |
| f56r | pictured simple, highly local vocabulary and almost entirely open writing | a short page-local article whose rare tail most plausibly contains identity, morphology, habitat, virtue or use |
| f81v | a large lower pool containing figures and an inlet/outlet arrangement | bath/application unit whose pictured stations silently supply operands for short records |
| f82r | the most crowded fixed Bio page: figures, pools/vessels and conduits at several stations | multi-station treatment/configuration sheet; repeated committed values can be reused at nonadjacent stations |
| f83r | figures and connected container/conduit forms with text inserted in the remaining spaces | another application sheet using the same B value deck but different local operands |
| f67r2 | concentric selector with distinct 7, 12 and central inventories | master influence selector: seven governors and twelve zodiacal divisions around a central condition/rule |
| f68r1 | one central object plus 28 noncentral labelled star-like objects | identification catalogue for 28 celestial stations, plausibly lunar mansions; spatial arrangement is not yet an authorial cycle |
| f69v | 28 loci in an ordered alternation of LONG and SHORT entries | operational 28-step schedule, plausibly mansion-by-mansion election or prognostic use |

The 7/12/28 fit is not a decipherment. Seven planets, twelve signs and
twenty-eight lunar mansions are nevertheless a historically coherent inventory,
and it gives the three Astro pages a concrete job. My preferred relation is:

```text
f67r2 = choose governing layer
f68r1 = identify the 28 named stations
f69v  = consult the 28 station-specific working outcomes/rules
```

This does not require direct label identity between f68r1 and f69v. A diagram
legend and a copied working canon can use distinct abbreviation namespaces.
The f69v LONG/SHORT alternation may be `condition -> result`, `name -> rule`, or
two opposed prognostic classes; it is not evidence for good/bad by itself.

## Image-first production and physical reflow

The pictures were laid out before the text. A workshop could copy the plant,
bath/apparatus scheme or rota from one exemplar, then have a text scribe fit an
abbreviated source around it. Consequently:

1. the picture owns the dossier topic, but a stem interrupting a line does not
   own the adjacent card;
2. a physical line is a fitting strip, not necessarily a sentence;
3. Herbal statements may continue across several strips;
4. Bio fields can be genuinely local because the drawing and stencil already
   identify their station/question;
5. Astro labels are addressed primarily by geometry, not by prose order.

This also explains mixed hands without requiring every copyist to know the
full expansion of every rare card. A master prepares a common deck and
register exemplars; a scribe selects the register, copies the local source
entry, applies exact cards, and renders wrappers according to hand and line
position.

```text
medical sources and exemplars
  -> picture/register ellipsis
  -> exact abbreviation cards and inherited slots
  -> register grammar
  -> hand-specific wrappers, spacing and physical reflow
```

## Exact register grammar

```text
CODEX        := HERBAL_DOSSIER+ APPLICATION_SHEET+ ASTRO_INSTRUMENT+

HERBAL       := DRAWN_SIMPLE + OPEN_ARTICLE+
OPEN_ARTICLE := CLAUSE_PACKET+
CLAUSE_PACKET:= ITEM? + CARD* + RELATION/REFERENCE* + rare LOCAL_CONTENT+

BIO          := DRAWN_CONFIGURATION + RECORD+
RECORD       := COMMITTED_CELL* + OPEN_CONTINUATION?
COMMITTED_CELL
              := inherited VISUAL_SLOT
                 + ITEM?
                 + CARD/QUALIFIER*
                 + EXACT_VALUE_CARD
                 + ATTACHED_COMMIT

ASTRO        := DRAWN_TOPOLOGY + GEOMETRY_ADDRESSED_LABEL/ENTRY+
```

`FIELD` remains a formal slice. On Herbal A it usually contains open article
material; on Bio B it can instantiate a complete inherited question. Attached
DY/B3 behavior commits the local cell, while free rendered DY can still be the
ordinary Y card with a wrapper. A statement need not end at the line break.

The known-card rules fit this grammar:

```text
qokaiin
  -> ITEM / NEXT / activate the next inherited entry

A -- L/O -- B
  -> place B with A / under the active medical relation

L/O at field start or alone
  -> likewise under the inherited heading

L/O at line end
  -> hold that relation open for the next strip

Y -- AIIN -- Y
  -> FORMULA_F3: two marked items under one stated/current reference

[qualifier ...] EXACT_VALUE + COMMIT
  -> fill the pictured/inherited application slot and validate it locally
```

`qokaiin` is field-first in 7/9 cases, has nine different right neighbors, and
its exceptional final copy at f82r.3 repeats at the start of f82r.4. `ITEM`,
`NEXT` or rubric-like reactivation is therefore more plausible than WATER.

L/O has one rule over all 19 occurrences: 14 medial, three initial, one alone
and one final, with five immediately before a close. Its medical expansion is
approximately *cum*, *item cum*, *similiter* or *sub eodem capite*, but no one
Latin word is being assigned.

`FORMULA_F3 = Y-AIIN-Y` remains a genuine learned formula shared by f10r and
f83r. In a medical source it can naturally stand for “both marked matters under
the stated standard” or *ut supra* reuse. The extra preceding Y on f10r and the
following committed value on f83r prevent a literal `ana/equal dose` reading.

The Bio 12/10/8/8 deck is best read as recurrent **categorical application
values**, not four columns or a numerical scale. The values may answer such
questions as medium, application station, preparation state, flow/temperature
class, duration class or expected result. Only the structural claim—exact value
plus local commit—is strong.

## Why exact cards outrank naive EVA words

The visible spellings mix a stable learned card with renderer behavior.
AIIN/DAIIN/SAIIN/CHAIIN/TAIIN collapse to one exact card; Y/DY/CHY/SHY/SY/CHEY
can collapse to another; Herbal CHOL and Biological OL can realize the same
L/O card. Conversely, attached closure and free `DY` are not the same event.

Thus the useful unit is neither an EVA token nor a plaintext word. It is an
exact workshop card whose source expansion could be a word, abbreviation,
phrase, reference or form instruction. Exact identity explains cross-hand
formula copying and the repeated Bio value deck; naive surface words split the
same instruction into wrapper variants and sometimes merge unlike functions.

## Continuous pseudo-readings

These are source-class reconstructions. Bracketed content is deliberately
unknown, but every formal event is assigned a job rather than erased.

### Herbal — complete f10r second paragraph

> Concerning the pictured simple, continue its article with [local identifying
> or descriptive matter]. Put the two marked matters under the same stated
> standard. Add the next [property, part or habitat] and its qualification.
> With the current matter enter [local determination], and likewise continue
> the associated clause. Record [virtue or application] and its condition;
> then [preparation or medium] with the remaining local qualification. The last
> physical strip completes the copied paragraph, not a Bio-style checked cell.

This covers the complete seven-line paragraph as one open article, including
the f10r `Y-Y-AIIN-Y` tail. The alternatives in brackets are a ranked source
menu, not covert plaintext. My first concrete guess is that at least one of the
later clauses is a **virtue/use** clause (.48), ahead of habitat (.35) and
preparation (.33); no exact card selects among them.

### Biological — complete f82r.27 record

The record has seven committed cells with lengths `1 | 2 | 1 | 1 | 1 | 1 | 1`
and anonymous values `A | (B,b) | C | D | E | C | F`.

> For the pictured bath/application unit: enter setting A and commit it; enter
> B with modifier b and commit it; enter C for the next inherited station;
> enter D; enter E; reuse the same setting C at the second corresponding
> station; enter final setting F. The configuration is locally complete.

The concrete medical expansion I favor is a **treatment-configuration record**:
A–F choose medium/state/station/degree/result categories supplied by the
picture and stencil. This reading explains the nonadjacent recurrence of C
without pretending that C means water, heat or dose.

### Astro — whole-diagram readings

> **f67r2:** Select the governing sevenfold influence; locate the relevant one
> of twelve zodiacal divisions; apply the central qualification or rule.

> **f68r1:** Under the central lunar/celestial owner, identify the twenty-eight
> named stations. Use the drawing as a spatial catalogue; do not infer a cycle
> merely from modern reading order.

> **f69v:** Traverse the twenty-eight stations in the drawn order. For each,
> consult the alternating short/long entry as a station heading plus its
> election/prognostic rule, or as two recurrent rule classes.

My concrete guess is a **lunar-mansion election annex** (.63 for the
twenty-eight-station source class; .41 for specifically medical timing). It can
serve medical use without being lexically joined to every Herbal or Bio entry.

## Meaning guesses forced across the fixed pages

| guess | confidence | fixed-page check | survival decision |
|---|---:|---|---|
| qokaiin = ITEM/NEXT/reactivate entry | .69 | fits 7/9 field-initial cases, nine different successors, one medial use and the f82r line-end/start carry; not tested on Astro because no prose tuple layer exists there | retain as best source function; reject literal WATER |
| L/O = WITH CURRENT ITEM / LIKEWISE UNDER SAME HEADING | .61 source, .76 formal | one inherited-relation rule covers all 19 occurrences including first, only and final positions on the fixed prose pages | retain; exact preposition remains open |
| AIIN = STATED/CURRENT STANDARD | .46 | broad mobility across all seven prose pages and no immediate attached close fit reference reuse better than a fixed dose slot; f10r/f83r preserve FORMULA_F3 | retain narrowly; equal amount only .18 |
| Bio terminal deck = treatment-configuration categories | .49 content, .84 structure | 90/90 attached terminals fit value+commit; the 12/10/8/8 families cross all three Bio pages and move among field ordinals/lengths | leading medical expansion; result/checklist/cadence remain rivals |
| Herbal rare tail carries plant-specific name/property/use material | .66 | f10r/f56r are singleton-rich, share only four exact types, and remain open; f55v bridges toward B production | retain at source-class level; no plant or part identification |
| 7/12/28 Astro set = planets/signs/lunar mansions | .72 for 7/12, .63 for 28 | explains all three topologies, but no direct f68r1↔f69v label transfer and no prose-card bridge exist | retain as leading Astro source family, not a decoded list |

The guesses are mutually supportive but not made artificially universal. The
prose cards are not imported into the circle pages, and Astro vocabulary is not
required to recur in Herbal or Bio.

## Historical comparison around 1420

The combination is unusual but not anachronistic.

- British Library [Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783),
  made c. 1420–30, combines Arderne's illustrated recipes and surgery, a Zodiac
  Man, 68 medicinal-plant drawings, a *Circa instans* simple-medicine text,
  regimen and added cures. It is the closest control for the coexistence of
  simples, application/surgery and medical astrology in one professionally
  illustrated codex. It does not attest Voynich notation.
- [Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567) (main
  copying dated 1446) combines recipes, urinary instruments/surgery and the
  pseudo-Hippocratic *Astrologia medicorum*. This supports a practitioner's
  miscellany whose source genres have different local formats.
- The fifteenth-century [Add MS 34111](https://searcharchives.bl.uk/?q=032-002025081&sort=hierarchy)
  is catalogued as a medical miscellany including zodiacal influences on the
  body. It is further evidence that medical and astrological consultation were
  not separate modern subjects.
- Wellcome [MS.9280](https://wellcomecollection.org/works/b5k4wa4d) is later
  (1489) but preserves an older compilation ecology: monthly dietetic rules,
  a twelve-sign zodiac text, lunar-day prognostics, recipes and herbal texts.
  It is an analogy for WHAT/WHEN consultation, not a donor.
- The medical core of the York barbers' and surgeons' guild book includes a
  bloodletting man, Zodiac Man, volvelle, astrological tracts and a bloodletting
  poem; see the [Cambridge study of Egerton MS 2572](https://doi.org/10.1017/9781800102729.001).
  It is later (1486) but shows practical professional ownership of the same
  visual-astrological apparatus.
- The Warburg edition of the Latin
  [*Picatrix* tradition](https://resources.warburg.sas.ac.uk/pdf/fbh295b2205454.pdf)
  documents a real 28-mansion technical inventory and mansion-by-mansion
  operations, including material framed against bodily infirmities. This makes
  a 28-entry source class historically available; it does not make f68r1 or
  f69v *Picatrix*.

The strongest pattern-book control is the
[Vienna Model Book](https://www.khm.at/en/artworks/so-called-vienna-model-book-with-leather-case-selection-91010),
dated c. 1410/20. It proves that portable workshop collections of exact motifs
were real. Yet its function is a repertory of reusable heads and skulls. The
[Morgan model book](https://www.themorgan.org/collection/model-book) likewise
preserves more than seventy motif drawings for study and reuse. These genuine
model books strengthen the copying-workshop rival but also sharpen its cost:
one must explain why the ten fixed Voynich pages add dense, register-specific
writing, short committed value cells and operational 7/12/28 layouts instead
of mainly presenting motifs to copy.

## Competition, contradictions and discriminating observations

Frozen-rubric self-score:

| criterion | score |
|---|---:|
| ten-page coverage and awkward facts | 23/25 |
| one learnable multi-scribe workflow | 19/20 |
| register differentiation | 15/15 |
| concrete source-class readings | 13/15 |
| historical plausibility | 14/15 |
| rival, contradictions and predictions | 9/10 |
| **total** | **93/100** |

The model's main liabilities are real:

1. no exact card has an externally owned medical meaning;
2. Bio cells could be generic answers or a scribal cadence rather than
   treatment values;
3. naked figures, conduits and pools need not denote baths or anatomy;
4. 7/12/28 are common astronomical cardinalities and may be a separate
   natural-philosophical annex;
5. f68r1 has no established cyclic order and no proven identity mapping to
   f69v;
6. a pattern/training book predicts exact copying and multiple hands at least
   as naturally as the medical theory does.

The fixed-page observations that would most change the ranking are:

- **Medical rises:** on f81v/f82r/f83r, the same exact Bio value recurs at the
  same independently visible station or relation more often than at unmatched
  stations, while remaining movable across field ordinal. That would connect
  the value deck to application content rather than generic cadence.
- **WHAT/HOW/WHEN rises:** a geometry-only correspondence pairs at least a
  substantial subset of f68r1's 28 positions with f69v's 28 ordered entries
  without selecting by their text.
- **Pattern/form rival rises:** Bio values follow line length, available space
  or graphic symmetry better than visible stations, and f69v LONG/SHORT
  alternation is explained entirely by line filling.
- **Medical falls sharply:** the four Herbal pictures prove to be copied motif
  variants with text blocks mechanically interchangeable among pages, or Bio
  committed values remain unchanged under visibly different station roles.

## Final selection

Keep the generic form/pattern theory as the adversary, but select the
**iatromedical practical concordance** as V14 R2's overall purpose. Its economy
is that the same ellipsis rule explains the long Herbal articles, compact Bio
cells and label-like Astro registers. Its historical claim is modest: a
practical medical miscellany around 1420 could unite simples, applications and
astrological election. Its semantic claim is exploratory: the ten pages most
coherently read as WHAT/HOW/WHEN, while every exact lexical expansion remains
revisable.

## Scope and seals

Only f10r, f11r, f55v, f56r, f81v, f82r, f83r, f67r2, f68r1 and f69v were used.
No Voynich phonetics, language identification or new substring mining was
attempted. ZL3b/IT2a/RF1b remain alternate readings of one manuscript. No f84
or f84r image, transcription, formal value, metadata or inference was opened
or used.
