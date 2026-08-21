# Candidate theory: an iatromathematical workshop concordance

Status: independent sidequest proposal, 2026-08-21. This is a deliberately
abductive reconstruction, not a GDT result or a translation. It was developed
from `VOYNICH_CURRENT_ROUTE.md`, `SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`, and
external historical sources only. The long sidequest archive, translation
draft, active ledger, other candidate theories, and f84/f84r were not read.

## Leading theory

The ten pages belong to a **compact medical-astrological concordance produced
by a small practical workshop**. It is not ordinary prose encoded word for
word. It is a hybrid of abbreviated natural language, a shared technical card
inventory, diagrams that silently supply arguments, and register-specific
lookup forms.

Its best tentative organizing question is:

```text
WHAT can be used?       Herbal illustrated simple dossiers
HOW is it prepared or applied?  Biological bath/application forms
WHEN is it permitted or preferred?  Astronomical/calendrical selectors
```

This does not require a Herbal page, a Biological page, and an Astro page to
form one explicit cross-referenced prescription. A practitioner could consult
each register independently, just as a late-medieval medical miscellany could
put remedies, bloodletting rules, lunar tables, and a Zodiac Man into separate
tracts. The integration exists at the level of practice and book architecture,
not necessarily through repeated lexical pointers.

The safest genre name is therefore **iatromathematical workshop concordance**:
a book used to reconcile materia medica, procedure, and celestial timing. A
looser heterogeneous practical miscellany remains the principal alternative.

## Why this is historically plausible

The proposed architecture is not inferred from a single analogue.

- Wellcome MS.8004, compiled around 1425, is described as a practical manual
  of computistical science and astrological medicine. It combines calendar
  material, a tract on administering medicine by zodiacal sign, eclipse
  tables, and later medical recipes. This is almost exactly the kind of
  practical bridge required between a WHEN register and recipe material:
  [Wellcome MS.8004](https://wellcomecollection.org/works/w9nkm98w).
- A Latin folding almanac of 1415–20 supplied tables and diagrams for checking
  planetary hours and the Moon's zodiacal position before a medical procedure.
  Folding almanacs were practical lookup objects rather than continuous books
  to be read from beginning to end:
  [Wellcome, medieval folding almanac](https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac).
- Wellcome MS.40 contains a calendar, planetary table, lunar table, eclipse
  material, Vein Man, Zodiac Man, and calendar canon in only seven folded
  leaves. It demonstrates extreme compression and the coexistence of several
  local visual/table namespaces:
  [Wellcome MS.40](https://wellcomecollection.org/works/sq4rjv47).
- Harley MS 3843 combines calendar and astrological tables, bloodletting,
  complexions, zodiacal regimen, and monthly health regimen in one fifteenth-
  century computistical miscellany:
  [British Library catalogue, Harley MS 3843](https://searcharchives.bl.uk/?f%5Blanguage_ssim%5D%5B%5D=Latin&f%5Bproject_collections_ssim%5D%5B%5D=Harley+Collection&f%5Burl_stub_si%5D%5B%5D=www.bl.uk+%28unavailable%29&page=37&per_page=20).
- Durham Cosin MS V.iv.1 places an astrological plague tract, a monthly health
  regimen, and English and French bath recipes in the same manuscript. The
  surviving bath instructions explicitly use herbs in a bath:
  [Durham Cosin MS V.iv.1 catalogue](https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s19s1616306.xml).
- British Library Add MS 41623 is a northern Italian herbal with an index of
  plants and appended magical/astrological medical tracts, including one on
  herbs under zodiacal and planetary influence:
  [British Library Add MS 41623](https://searcharchives.bl.uk/catalog/032-002085314).
- A fifteenth-century medical prescription tradition used stable genre-specific
  abbreviations for measures and formulae, including `ana` ('of each'),
  `recipe`, drachm, half, and ounce. This supports the possibility of a compact
  technical register without implying that any Voynich form spells Latin:
  [Rodríguez Ledesma, "Abbreviations in Medieval Medical Manuscripts"](https://reunido.uniovi.es/index.php/SELIM/article/download/13301/12036/28090),
  and the aligned-corpus study in
  [Digital Scholarship in the Humanities](https://academic.oup.com/dsh/article/37/3/765/6401180).
- A later but especially explicit example records a table of the Moon's zodiacal
  position together with favorable times for bloodletting, purging, and
  bathing. It confirms the functional linkage, not a direct donor:
  [Morgan MS M.1117, fol. 19v](https://ica.themorgan.org/manuscript/page/8/184768).

These analogues establish a **document ecology**, not provenance, language,
authorship, or direct copying. Seven planets, twelve zodiac signs, and lunar
cycles are widespread medieval structures and have low cultural specificity.

## Generative workshop workflow

The system can be learned by several scribes without a cryptographic school.

```text
1. A master or illustrator lays out the pictures and circles first.
2. The page register selects a local form book:
      SIMPLE DOSSIER | PROCEDURE CELL FORM | CELESTIAL LOOKUP
3. The picture or geometric locus silently supplies the main subject/address.
4. The scribe copies a sequence of abstract cards from a shared ledger.
5. Register-local cards supply plant, procedure, vessel, state, or table values.
6. Attached DY/B3-like states commit a local cell; an open field may continue.
7. Wrapper and JOIN/SPACE choices render the licensed card in the current hand.
8. Physical lines are fitted around prior drawings and need not end statements.
```

The workshop's minimal teaching kit would contain:

```text
COMMON CARD SHEET       relation, value, qualification, framing cards
HERBAL ADDENDUM         plant-dossier and preparation values
PROCEDURE ADDENDUM      medium, vessel, operation, state, application values
CELESTIAL TABLE KEY     locally ordered labels and outcome classes
HAND EXEMPLARS          wrapper and line-entry variants
```

This explains why several hands can share an exact-card grammar without making
the script a simple substitution alphabet. It also explains why the B writing
ecology transfers between f55v and Biological pages while most technical card
identities remain register-local.

## Proposed latent record grammar

```text
HERBAL_DOSSIER := PICTURE_ADDRESS + CLASS/RELATION*
                  + QUALITY_OR_PART* + PREPARATION_OR_USE*
                  + optional VALUE_FRAME

PROCEDURE_RECORD := PICTURED_APPARATUS_OR_BODY_ADDRESS
                    + CLOSED_CELL*
                    + OPEN_CONTINUATION?

CLOSED_CELL := ROLE/OBJECT + VALUE_OR_STATE* + COMMITTED_CLOSE

ASTRO_LOOKUP := GEOMETRIC_ADDRESS + LOCAL_LABEL_OR_VALUE
                + optional BINARY_LAYOUT_STATE
```

The grammar is intentionally not `subject + verb + object`. In the prose
registers, a record can be equivalent to a form such as:

```text
[silent pictured subject]
  class/relation: value
  component/process: value: committed state
  application/result: open continuation
```

The short Biological cells are consequently not miniature sentences. They are
entries in a diagram-owned procedure or configuration record.

## Tentative card functions and readings

The following guesses are functional analogies. They are not phonetic readings
and do not make the exact cards into source-language words.

| exact card/family | strongest tentative function | bold workshop paraphrase | confidence |
|---|---|---|---|
| AIIN `2f1c5e56...` | value/reference placeholder | "the entered amount/index/value" | medium-low |
| Y `b921a237...` | value/type framing card | "value of this kind" / value delimiter | low |
| L/O `dcda95c8...` | relation or class link | "of / for / under / belonging to" | low |
| CTHY `e0b630cb...` | qualitative condition | "in the specified condition/grade" | low |
| attached DY/B3 state | local commitment | "cell resolved/entered" | medium structurally, none semantically |
| Bio OKE/OK/LCHE/CHE families | procedure-state deck | operation, medium, result, or modality classes | very low |

Two deliberately bold readings deserve separate treatment.

### `Y → AIIN → Y`: equal-measure or paired-value frame

This exact path occurs as Herbal `CHY TAIIN SHY` and Biological
`CHEY DAIIN CHEY`. Because it crosses unrelated pictured subjects, the center
is unlikely to name a plant, water, tube, or person.

The best concrete guess is:

```text
Y     AIIN              Y
VALUE [entered amount]  SAME/VALUE

≈ "matching value", "of equal measure", or "paired quantity frame"
```

The historical analogue is the prescription formula `ana`, 'of each/equal
amount', but **AIIN is not being read as ana**. No sound or letter mapping is
claimed. The analogy is purely functional: an abbreviated pharmacy system
needs a reusable instruction that binds several silent or nearby operands to a
shared quantity. Its occurrence at a Herbal field tail and at a Biological
field head is consistent with a portable value frame.

An equally viable non-quantitative reading is `same class/reference on both
sides`. If future instances do not accompany paired operands or a stable scalar
slot, the equal-measure guess should be withdrawn while retaining the abstract
frame.

### `OR → Y`: relation opening a typed value

The path recurs on f10r, f55v, and f83r under different surfaces. A useful
provisional paraphrase is:

```text
RELATION → TYPE/VALUE

≈ "for the class/value ..." or "under condition ..."
```

This is more likely to be technical syntax than one repeated substance. The
different wrappers are rendering choices, not ordinary agreement morphology.

### The f82r `qokaiin` line carry

The exact card repeats from the end of one physical line to the beginning of
the next inside the same paragraph. In this theory it is a **carried parameter
or copied entry**, functionally comparable to a ditto/re-entry device:

```text
... [PARAMETER X] | physical reflow | [PARAMETER X] ...
```

The `q` itself is not translated as NEXT or REPEAT. The whole exact card can
carry the value while `q` remains the known post-close/entry renderer.

## Page-family interpretation

### Herbal: WHAT / materia-medica dossiers

The four plant pictures are silent headwords. Each page records a dossier
about the shown simple rather than repeatedly spelling its name. Long open
fields suit a heterogeneous entry with classification, usable part, quality,
preparation, habitat/medium, and indications. Water can plausibly occur as:

- habitat or growth condition;
- washing/steeping/decoction medium;
- administration medium;
- a quality such as moistness;
- part of a bath preparation.

No current card is assigned WATER. In particular, L/O is only a relational
candidate, and CTHY is only a condition candidate.

The f55v bridge is expected under this theory: it is Herbal in content but is
written with a B-compatible form shelf, hence Bio-like closure density and
shared common cards without becoming a Biological page.

### Biological: HOW / therapeutic procedure forms

The images are best treated as schematic therapeutic scenes: baths, washes,
infusions, irrigations, heating/cooling circuits, vessels, outlets, body-contact
sites, or combinations of these. The exact choice remains open. The many short
closed cells encode local components or states attached to pictured nodes.

A reusable line stencil such as:

```text
1C | 3C | 1C | 4O
```

is interpreted as a procedure template with three committed subentries and one
open tail, not as a repeated sentence. The fact that eight of nine cards can
vary while the form persists is exactly what a check-form requires.

The family-specific closers may distinguish **kinds of committed result**—for
example prepared medium, completed manipulation, selected outlet/application,
or accepted state—rather than being synonyms for END. This is a more useful
guess than assigning OKE, CKHY, or LCHE to concrete ingredients.

The female figures could identify body sites, patient classes, or a women's-
health subregister, but the apparatus/application reading does not require a
gynaecological doctrine. Their strongest role in the theory is as silent
participants in the procedure graph.

### f67r2: celestial selector

The leading speculative assignment is:

```text
upper 7     seven planetary/luminary rulers or weekday regents
lower 12    zodiacal signs or twelve sign-conditioned classes
central 8   local phase/condition/quality selectors, presently unidentified
```

The 7 and 12 assignments are historically natural but not specific. The
central eight must not be forced into elements, directions, winds, houses, or
humours. Its role may be an intermediate selector that tells the user which
local table branch to follow.

Crucially, the layers use distinct local namespaces. The page can function as
a selector because geometry, not repeated vocabulary, defines ownership.

### f68r1: lunar-position or stellar-station catalogue

The one central and 28 noncentral labelled stars are best guessed to form a
**spatial roster of lunar stations or another 28-member celestial index**.
This is a catalogue, not yet a cycle: no authorial order has been established.
The central star supplies a reference point, pole, authority, or diagram title;
the surrounding labels identify spatial entries.

Calling the 28 entries lunar mansions is a low-confidence historical reading,
not a recovered label set. The page could instead be a list of stars,
directions, or 28 lunar positions. Its expected function in the handbook is to
identify the celestial position to be used in an election or prognosis.

### f69v: ordered 28-step election schedule

Unlike f68r1, f69v has an authorial 28-entry order. Its strict LONG/SHORT
alternation is best treated as a binary **layout channel** superimposed on a
lunar-day or lunar-position schedule.

The strongest concrete guess is:

```text
entry n := local lunar-day/station condition
LONG/SHORT := alternating table lane or query class
label(s) := outcome/instruction code for that entry
```

A deliberately bolder medical interpretation is a schedule of permissible
versus constrained acts—bleeding, purging, bathing, administering medicine,
or prognosis. But LONG must not be equated with favorable, odd, red, waxing,
or any other named state, nor SHORT with its opposite. Existing nonconfirmation
of a textual LONG/SHORT marker makes the binary class more likely to be a
layout/reading convention than a lexically repeated good/bad word.

### How the three Astro pages can work together

The most coherent workflow is not a shared 28-name list:

```text
f67r2: choose ruler/sign/local condition
f68r1: identify spatial station or celestial address
f69v: retrieve the ordered day/position outcome
```

This architecture explicitly preserves the failure of direct f68↔f69 label
identity and direct A-65 transfer. Separate labels are expected because one
page names addresses and another records outcomes. What is shared is the user's
mental lookup operation, not necessarily a surface token.

## Representative schematic parses

These are not plaintext translations.

```text
f10r.6  ... Y AIIN Y
         [pictured simple] ... MATCHED-VALUE-FRAME
         bold reading: "use/record the same entered measure"

f10r.9  ... OR Y ...
         [pictured simple] ... RELATION → TYPED-VALUE ...
         bold reading: "for/under the specified class or condition"

f55v.11 ... OR Y ... + B-style commitments
         Herbal subject expressed through a B workshop form shelf

f81v.17 [1C] [3C ending SHEDY-close] [1C] [4O]
         one committed setting; a three-card resolved operation/state;
         one committed setting; an unresolved continuation

f82r.7  [1C] [3C ending same SHEDY-close] [1C] [4O]
         same procedure form, different local entries

f83r.3  Y AIIN Y + LCHE-close
         MATCHED-VALUE-FRAME committed as one local procedure cell

f82r.3→4 ... QOKAIIN | QOKAIIN ...
         parameter repeated across physical reflow, not sentence restart
```

At the most adventurous but still coherent level, these amount to forms like:

> For the pictured simple, record its class and condition; where multiple
> components share a measure, enter that common value. For the pictured bath or
> application, fill each operation/state cell and commit it. Before use,
> consult the planetary/sign selector and the relevant lunar schedule.

This is a translation of the **hypothesized workflow**, not of Voynich words.

## What this theory explains economically

1. **Free/bound reuse.** A card can be rendered independently or inside a
   wrapper because the ledger identity and its written realization are
   separate.
2. **Split/join variation.** JOIN/SPACE is part of technical rendering and
   spatial fitting, not necessarily linguistic word division.
3. **Right-edge DY.** Attached closure commits a local form cell; free DY is a
   rendered Y card and therefore need not behave like closure.
4. **Productive `q+X`.** `q` marks a licensed post-close/entry realization; it
   need not have the lexical meaning NEXT.
5. **Line reset.** Lines are copy packets fitted around pre-drawn images;
   `s`-entry rendering helps restart a packet without beginning a new statement.
6. **Repeated exact labels/cards.** Repetition can mean repeated ledger state,
   equal slot value, or deliberate carry, not a duplicated sentence.
7. **Currier effects.** Hands/register shelves favor different closure and
   wrapper habits while sharing the common ledger.
8. **Extreme formal compatibility without GDT003 gain.** Frequent registered
   formulae and renderer alternatives can mimic morphology while remaining a
   finite card-and-form system.
9. **Failure of simple language/cipher mappings.** Surface groups entangle
   abstract card, wrapper, placement, register, and layout; they are not plain
   phonographic words.
10. **Seven/twelve/twenty-eight circle structures.** They are appropriate
    lookup cardinalities in a generic medieval astro-medical ecology without
    identifying a Georgian/A-65 donor.

## Awkward facts and potential falsifiers

1. There is no observed cross-section pointer linking a plant, procedure, and
   celestial entry. The integrated `WHAT/HOW/WHEN` workflow may be merely a
   modern story imposed on a miscellaneous codex.
2. GDT327 has no events for f67r2, f68r1, or f69v. The prose card grammar cannot
   currently be demonstrated in Astro.
3. The f68r1 noncentral 28 has no authorial cycle. Calling it lunar mansions is
   underdetermined.
4. The f69v binary alternation lacks a reliable textual marker. It might be
   purely decorative or a copying aid.
5. Seven planets, twelve signs, and 28-day or 28-station systems are common
   across medieval traditions. They support genre compatibility, not origin.
6. `Y→AIIN→Y` occurs only twice. The equal-measure reading is especially
   vulnerable to coincidence and could instead be a purely grammatical frame.
7. The Biological pictures need not be baths or therapeutic apparatus. They
   may be cosmological, allegorical, anatomical, or another technical domain.
8. No exact card currently correlates with an independently repeated visible
   substance, action, body site, vessel, or celestial value.
9. Register-local closers could be scribal punctuation rather than result-state
   classes.
10. A practical concordance normally benefits from overt cross-references,
    headings, or numerals. Their absence may mean those functions are encoded
    in currently unrecognized geometry, or that the integrated model is wrong.

## Five novel predictions

These predictions are consequences of the theory and were not used to select
its central `WHAT/HOW/WHEN` story.

1. **Procedure-template prediction.** On independently annotated fixed-page
   Biological loci, repetitions of the same closed/open field stencil should
   align more often with homologous operation geometry (vessel → conduit →
   contact/outlet) than with the identity or posture of the depicted figure.
   Failure would weaken the HOW register interpretation.
2. **Closer-class prediction.** Different recurrent Biological closer cards
   should associate with different endpoint topologies—such as termination in
   a vessel, conduit, body-contact site, or open continuation—across at least
   two pages. If all closer families are interchangeable after hand and
   placement, they are probably renderer/punctuation rather than committed
   result classes.
3. **Paired-value prediction.** Any later independently admitted occurrence of
   exact `Y→AIIN→Y` should occur where two operands, components, or states can
   share a value. It should not consistently identify one visible object. A
   counterexample with a unique stable object owner rejects the equal-measure
   fork but not the abstract frame.
4. **Astro role-separation prediction.** If f68r1 is an address catalogue and
   f69v an outcome schedule, f68r1 should have high label individuality while
   f69v should reuse a smaller set of outcome/form classes. Correspondence,
   where found, should be ordinal/topological rather than exact surface-label
   identity. A one-to-one shared name list would instead favor direct table
   duplication.
5. **Selection-chain prediction.** If f67r2, f68r1, and f69v are parts of one
   lookup system, at least one independently recognizable geometric convention
   should specify a path from a 7/12 selector to a 28-entry lookup without
   requiring a universal textual label. If no such routing convention exists,
   the three diagrams should be demoted to unrelated astronomical miscellany.

## Confidence ranking

### HIGH within the sidequest

- Pre-drawn images and geometry silently own substantial arguments.
- Physical line is a reflow/copy unit, not a sentence boundary.
- The prose pages use a shared exact-card ledger plus register-local tails.
- B writing favors explicit cell closure; Biological pages favor many short
  fields.
- Astro uses local topology/surface namespaces and cannot inherit GDT327 prose
  cards.

### MEDIUM

- The ten pages belong to a practical medical or natural-philosophical workshop
  miscellany.
- Biological records are diagram-owned procedural/configuration forms rather
  than continuous narrative.
- The circle pages are lookup instruments rather than discursive exposition.

### PROVISIONAL LEADING CONTENT THEORY

- `WHAT / HOW / WHEN` forms a shared iatromathematical practice architecture.
- f67r2 is a 7/12/local selector; f68r1 is a 28-address celestial roster; f69v
  is an ordered 28-step electional schedule.

### LOW

- Biological imagery specifically encodes therapeutic baths, washes,
  irrigations, or applications.
- AIIN is a scalar/reference entry; Y frames a typed value; L/O supplies a
  relation; CTHY supplies a qualitative state.
- Bio closer families encode different committed result or modality classes.

### VERY LOW, retained because it is generative and testable

- `Y→AIIN→Y` is the workshop equivalent of "same/equal measure".
- f68r1 specifically catalogues lunar mansions.
- f69v specifically governs medical elections such as bathing, purging,
  bleeding, or administering medicine.

## Final candidate judgment

The best single story is not "a herbal plus unrelated strange diagrams." It is
a workshop's **iatromathematical concordance** in which pictures identify the
thing being discussed, compact card forms record qualities and procedure
states, and separate celestial tables constrain the occasion of use. This
explains more of the ten-page architecture than compressed natural-language
prose alone, while requiring less artificial regularity than a pure semantic
code.

The main uncertainty is not whether medieval medicine could combine these
domains—it demonstrably did—but whether these particular three Voynich page
families are linked by anything stronger than codex-level coexistence. Until a
fixed-page geometric or referential bridge is found, `WHAT/HOW/WHEN` should be
the leading **working theory**, not a claim.

Confirmed Voynich meanings under this candidate: **zero**.
