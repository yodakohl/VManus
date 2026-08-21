# V10 historical Herbal practice: a compressed illustrated materia-medica entry

Date: 2026-08-21

Status: independent speculative sidequest report, not a GDT result and not a
translation.

## Selection in one sentence

The best historical source architecture for the opaque material on `f10r` and
`f56r` is **an illustrated simple-medicine dossier in abbreviated prose**:

```text
PICTURED SIMPLE / PAGE OWNER
  + optional name or alias packet
  + nature/quality/classification packet
  + virtue, application and/or preparation clauses
  + recurrent relation/reference cards
  + page-local lexical cards
  + physical reflow around an already allocated illustration
```

This is a mixture, but it has a learnable rule. It is not a free mixture of all
possible readings. The picture owns one simple; stock cards render the repeated
grammar of a materia-medica notice; rare and page-local cards carry names,
properties, parts, ailments, preparations or other content. A card may
abbreviate a source word or a short formula. Nothing in the fixed pages supports
a separate tabular value for every group.

`f84` and `f84r` were not accessed. The prose census used only guarded GDT327
rows selected for `f10r`, `f11r`, `f55v`, and `f56r`. Images were inspected only
for these four authorized pages. No other V10 candidate report was read.

## Why this is historically ordinary around 1420

The closest dated source mechanism is Tadhg O Cuinn's Irish book of simple
medicines, explicitly completed in **1415**. Its editor describes the usual
entry order as a Latin chapter heading, the Irish drug name, hot/cold/dry/wet
qualities, general virtues, and specific uses. The work follows *Circa instans*,
was compiled for practical local use, and survives through a production milieu
that included several named amanuenses. This is almost exactly the kind of
teachable source template a small workshop could compress without turning it
into a modern table ([UCC CELT edition, lines 480-505](https://celt.ucc.ie/document/G600005/)).

Three manuscript comparators reinforce different parts of the mechanism:

- British Library Egerton MS 747 combines the illustrated *Tractatus de
  herbis* with an antidotary, dosage material, ingredient substitutions,
  weights and measures, and a long synonym list. Its large plant images are set
  into the text area and its entries run from *Aloen* to *Zuchara*. This is a
  secure example of identification, synonyms, properties, recipe practice and
  quantitative apparatus living in one codex rather than separate genres
  ([British Library catalogue](https://searcharchives.bl.uk/catalog/032-001983805)).
- Penn Oversize LJS 419 is a fifteenth-century north-Italian Herbal with
  conventional and fantastic images. About a quarter of its illustrations
  carry Italian, Latin or mixed notes on medicinal properties and preparations,
  written around and sometimes over the images. It is especially relevant to a
  page where text had to fit an illustration rather than an abstract sentence
  grid ([OPenn catalogue](https://openn.library.upenn.edu/Data/0001/html/ljs419.html)).
- Ibn al-Tilmidh's older but structurally explicit simple-drug book divides 287
  entries into synonyms, description, faculties, benefits and use in compounds.
  It shows that the same multi-slot source architecture was not confined to one
  European language or one scribal school
  ([Cambridge, *Drugs in the Medieval Mediterranean*](https://www.cambridge.org/core/books/abs/drugs-in-the-medieval-mediterranean/ibn-altilmidhs-book-on-simple-drugs/AE2990B32C3F44DE02302AFA495CFCAF)).

Late-medieval medical manuscripts also possessed a dense abbreviation system,
including ordinary suspensions and contractions plus signs for *recipe*,
*ana*, handful, drachm, ounce, pound, scruple and fractional quantities. That
makes a learned whole-card layer historically plausible without making every
card a number or measure
([de la Cruz-Cabanillas and Diego-Rodriguez, manuscript survey](https://reunido.uniovi.es/index.php/SELIM/article/download/13301/12036/28090)).

These are mechanism comparators, not donors. None identifies a Voynich plant,
language, card or source text.

## Fixed-page image audit

The pictures can silently supply an owner, but they do not safely supply a
species name.

| page | source-bound visible description | permissible silent argument | unsupported leap |
|---|---|---|---|
| `f10r` | one tall plant; paired broad serrated/banded leaves; two flower-head-like forms; horizontal basal structure ending in two red swollen forms | one pictured simple; conspicuous leaf, flower and basal/root structures | a named species; red fruit versus tuber; WATER |
| `f56r` | one tall plant; narrow/spiny structures; two dark heads; one very large radial/spiral head | one pictured simple; conspicuous heads and spiny structures | a named thistle; SUN; a specific drug; WATER |
| `f11r` control | dense rounded flowering mass, several stems, jagged basal structures | one pictured simple/configuration | species identity |
| `f55v` control | one huge broad leaf, terminal clustered head and branched root, with text in separated page areas | one pictured simple; leaf/head/root | universal Herbal-A record order |

There is no authorial pool, stream, wavy ground, vessel or other secure water
owner on either primary page. A phrase such as “grows in wet places,” “wash,”
“decoct in water,” or “use the juice” is historically possible, but would be
textual content rather than a read-off picture label. The blue-green offset or
wash behind portions of the pages is not treated as depicted water.

Individual species guesses are deliberately withheld. The Voynich plants are
famously resistant to stable identification; even medieval herbal pictures can
combine conventionalized or corrupted traits. The page drawings can support
part-level prompts without licensing a botanical name.

## Exact field and record census

GDT327 supplies 38 exact-card events on `f10r` and 27 on `f56r`.

- `f10r` has two paragraph records. Record 1 is `f10r.2 + f10r.5` (14 cards);
  record 2 is `f10r.6 + f10r.8 + f10r.9` (24 cards).
- `f56r` has one paragraph record spread over seven physical lines (27 cards).
- Every physical line is one field in this slice.
- All five `f10r` fields are open.
- Six of seven `f56r` fields are open; only `f56r.8` has attached DY closure.

This is crucial. The opaque Herbal target is not behaving like the Biological
12/10/8/8 committed-value deck. It is mostly continuous open material reflowed
around pictures.

### Anonymous exact-card labels

The following labels are merely compact references:

| label | exact tuple | all occurrences on the four fixed Herbal pages |
|---|---|---|
| `A` | `2f1c5e56e8f0ff459065` | 9: f10r 3, f11r 1, f55v 3, f56r 2 |
| `Y` | `b921a237be883a820352` | 9: f10r 5, f11r 3, f55v 1 |
| `R` | `7a4bb8136330ee4e6e56` | 5: f10r 4, f55v 1 |
| `O56` | `2cc054357a929df85f64` | 4: all on f56r |
| `K1` | `276a7c2d74d1143446f4` | 3: f10r 1, f56r 2 |
| `K2` | `9ad66e67803a12e745de` | 3: f10r 1, f56r 2 |
| `L` | `dcda95c81a5460feb191` | 3: all on f10r |
| `S` | `e0b630cb1b5df5e7105b` | 3: f10r 2, f11r 1 |
| `K3` | `10488b911aae52b3b334` | 2: f10r 1, f56r 1 |

All other primary-page exact identities occur once, except exact
`4d4559019a961b834aa1`, which occurs twice on `f10r`. `A`, `Y`, `L`, and `S`
retain only the loose formal roles already in the compact basis; the neutral
labels above do not assert meanings.

### Complete primary sequences

`Uxxxx` means a singleton exact identity, shown by its hash prefix. Square
brackets mark the one attached close.

```text
f10r record 1
  .2  U65f Uded U4d4 U80e Udf1 U12e U62f K1 A Ua69
  .5  K2 Ue8a L S

f10r record 2
  .6  U724 S R Uf3c Uaf8 Y Y A Y
  .8  K3 R U497 L Udec L A U4d4
  .9  U27d R R Y U409 Y U834

f56r record 1
  .5  Ub9d O56 U0ec A
  .7  O56 U893 K3 K1 Udd0
  .8  Ud66 Uc10 K1 [U959]
  .12 Uad3 O56 Ub74 U132
  .13 K2 U087 U75a
  .18 O56 K2 Uc71 U61a
  .19 Ufaf U9bb A
```

This sequence accounts for every primary event. It also exposes the essential
split:

- recurrent cross-page cards (`A`, `K1`, `K2`, `K3`) are better candidates for
  stock grammar, common class, common preparation or common value than for the
  identity of either pictured plant;
- `R`, `L`, `S`, and `Y` organize repeated internal relations on `f10r` and its
  controls;
- `O56` is the strongest page-local repeated-content candidate: four copies in
  four different local frames, twice at line entry and twice medially;
- the singleton tail is where names, aliases, parts, ailments, preparations and
  virtues most plausibly reside, but the fixed data do not separate those
  subclasses.

## Mechanism comparison

### Plant name or synonym list only

A name/alias packet is plausible near an entry head. It cannot explain the
whole target: `f10r` has 38 cards in two continuing paragraph records, and the
same `R`, `Y`, `L` and `A` cards recur deep inside them. A pure multilingual
name list would also predict a more compact, parallel enumeration than the
observed open prose ecology.

### Habitat, moisture or WATER catalogue

Habitat is a legitimate Herbal slot. Some herbal traditions include where a
plant grows, and moist/dry are also ordinary humoral qualities. But no primary
picture owns water, no exact card is independently linked to wet ground, and
the recurrent cross-page cards occur in too many structural roles to be called
WATER. Retain `HABITAT/MOISTURE` as one possible rare payload, not the page's
organizing architecture.

### Qualities or classification only

Hot/cold/dry/wet and degree are historically expected near the front of a
simple entry. They could explain several short stock cards and the retained
AIIN reference/standard role. They do not explain two long f10r records,
page-local repetition, or the lack of a visible fourfold value stencil. A
quality packet is likely upstream content, not the whole system.

### Recipe or preparation only

Preparations and uses are strongly plausible, especially in the later part of
an entry. A pure sequence of imperative recipe steps is weaker: there is no
stable TAKE/action card, almost no attached closure, and the first f10r record
looks as substantial as the second. The safer source is a materia-medica notice
that can contain recipe clauses.

### Fixed table, index or exemplar code

The large rare exact-card tail is compatible with copied exemplar forms, and
the workshop may indeed have used a codebook. But the page supplies no columns,
row headings, cell boundaries, numerical axis, or repeated fixed stencil.
Table-driven semantics explains Biological better than these open Herbal-A
paragraphs. An exemplar can explain how cards were learned; it does not best
explain what this Herbal source said.

### Abbreviated ordinary prose

Ordinary source syntax best explains continuation across physical lines and
long open records. Completely ordinary diplomatic words, however, understate
the exact-card/workshop architecture already established elsewhere. The winner
is therefore abbreviated prose **compiled into the learned card register**, not
a letter-for-letter cipher and not unstructured language.

## Selected source architecture

The minimum historically plausible schema is:

```text
HERBAL_ENTRY := OWNER
                + (NAME / ALIAS / PROVENANCE)?
                + NATURE_OR_QUALITY*
                + (PART / FORM / HABITAT)?
                + VIRTUE_OR_USE_CLAUSE+
                + PREPARATION_OR_APPLICATION_CLAUSE*

CLAUSE := inherited OWNER
          + reusable RELATION/REFERENCE cards
          + one or more rare CONTENT cards
          + optional local closure
```

The schema is not claimed to be the actual authorial field order. Its value is
that it explains the observed asymmetry: common cards recur as grammatical or
technical scaffolding while most content identities remain rare, the page image
supplies the simple without constant renaming, and lines can stop wherever the
pre-drawn plant leaves space.

### What could `O56` be?

`O56` is the best new candidate, but it has two live interpretations:

1. **CURRENT_SIMPLE / ITS / OF-THIS**: an owner-resumption card repeated when a
   new virtue or preparation clause resumes the pictured plant;
2. **one page-specific recurrent operation or part**: for example a repeatedly
   mentioned head, juice, root, powder or preparation.

The first is preferred because `O56` occupies four changing constructions and
alternates between line entry and middle. But it is not assigned a gloss. A
plant name repeated four times is possible, especially in a compressed
technical register.

## Controlled pseudo-translation

The following is source-class expansion, not plaintext. Parentheses mark the
boldest content guesses.

### First complete Herbal record: f10r record 1

> **For the pictured simple:** enter its identity or accepted alias and its
> nature/class. Record a conspicuous part, form or place-of-growth qualifier
> and the currently stated setting. Continue with a second stock descriptor;
> associate the entry with a property/state.

A deliberately bolder 1420-style reconstruction is:

> **This simple, also called [alias], is of [quality and degree]. It is found
> in (possibly moist) ground and is recognized by [leaf/root/flower feature].
> Use or prepare [the relevant part] with [medium] in the stated manner.**

The words *moist*, *root*, *use* and *medium* are alternatives inside known
Herbal slots. None has an identified card.

### f10r record 2

> Give its first virtue or use under the carried state. Relate the marked item
> to the current reference. Continue with a second use containing two explicit
> associations. Add a third short use or qualification and leave the dossier
> open.

The high density of `R`, `Y` and `L` makes this record more likely to contain
several related claims than a long name string.

### f56r complete record

> **For the pictured spiny simple:** state its name/class and one recurrent
> owner or process item; attach a rare content value to the current standard.
> Resume that item in further clauses, giving a property or preparation, a
> second common descriptor and several page-local details. Commit one local
> subclause, then continue with three more open clauses and close the paragraph
> under the carried reference.

A bolder historical paraphrase is:

> **This [spiny simple] has [quality]. Use the [head/leaf/root] in
> [preparation]; for [condition], apply or take it in the stated manner. The
> same simple or preparation is used again for [two further conditions].**

Again, this is a plausible source shape, not a decoded plant or remedy.

## Adversarial alternatives

The strongest rival is **an exemplar-coded descriptive catalogue with little
or no medicinal procedure**. Rare cards could be copied index identities;
`O56` could be a local classification; repeated cards could be cross-reference
operators. It explains the codebook better than the prose reading but explains
the historical Herbal comparators and f10r's two-paragraph organization less
well.

The second rival is **fully ordinary abbreviated prose**. It explains open
continuation very well but does not independently explain why exact normalized
cards and renderer variants behave as a learned workshop deck.

The third rival is **a plant-description-only Herbal**. It remains possible
that the records discuss shape, parts, flowering and habitat without remedies.
The fixed pictures cannot distinguish descriptive from medicinal content.

## Fixed-page predictions and loss conditions

The selected architecture predicts, within the already fixed pages:

1. recurrent cross-page cards should remain mobile and combine with changing
   rare content, as `A`, `K1`, `K2`, and `K3` already do;
2. page-local repetition should be strongest for an owner-resumption,
   conspicuous part or recurring local preparation, making `O56` the decisive
   candidate rather than a universal first-position heading;
3. paragraph changes may correspond to source-stage changes, but physical line
   changes need not;
4. the only attached close on `f56r.8` should close a local clause, not the
   complete page entry;
5. a true WATER/HABITAT reading needs an independent contrast; neither f10r nor
   f56r provides one by itself;
6. exact first cards on f10r/f56r may be names or entry heads, but `f55v`
   beginning with the already mobile qokaiin card prevents a universal
   `FIRST_CARD = PLANT_NAME` rule.

The leading reading loses if any of the following becomes established:

- the opaque sequences align to fixed columns or numerical cells rather than
  continuing clauses;
- `O56` is shown to be a generic high-frequency renderer/construction state
  outside its apparent page-local ecology;
- the rare tail proves fully predictable from position and copying mechanics,
  leaving no payload-bearing identities;
- a readable parallel shows that these pages are captions, name lists or
  nonmedical catalogue entries rather than mixed simple-medicine notices;
- a repeated visual referent fixes a different card architecture.

## Bottom line

The historical evidence does not license a plant identification or a WATER
word. It does make one source architecture substantially more economical than
the alternatives:

> A workshop around 1420 could learn a compact card register by copying a
> familiar illustrated materia-medica template: the plant is the page owner;
> names and rare content vary; qualities, references and relations reuse stock
> cards; virtues and preparations continue across physical lines; and the
> scribe fits the compiled notice into the space left by the drawing.

The strongest new semantic target is not a species name but the page-local
`O56` recurrence on f56r. It may be an anonymous owner-resumption or repeated
part/process card. That is the maximum claim supported by this four-page pass.
