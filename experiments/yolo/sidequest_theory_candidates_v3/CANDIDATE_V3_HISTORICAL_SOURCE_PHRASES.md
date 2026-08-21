# V3 candidate — historically ordinary source phrases behind the card register

Date: 2026-08-21

Status: independent speculative sidequest theory. This is not a GDT result,
plaintext, language identification, or translation. English and Latin below
are deliberately explicit **source-class reconstructions** used to make the
current ten-page theory executable.

## Scope and evidence discipline

This pass used only:

- `VOYNICH_CURRENT_ROUTE.md`;
- `experiments/yolo/SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`;
- guarded slices of the current GDT276/GDT327 data for `f10r`, `f11r`,
  `f55v`, `f56r`, `f81v`, `f82r`, and `f83r`;
- frozen topology/layout and already quoted surface readings for `f67r2`,
  `f68r1`, and `f69v`;
- external historical recipe and palaeographical comparators.

The guarded prose slice contains 381 groups. The query admitted only those
seven named pages and explicitly rejected `f84*`. No candidate/archive folder
was read. No f84 or f84r material was accessed.

The task here is abductive: imagine a small workshop around 1420 and ask what
ordinary phrases it could have reduced to the observed cards. It is acceptable
to guess, but every guessed expansion remains below exact card identity.

## Historical constraints that actually matter

Late-medieval recipes do not require modern sentences or a fully explicit
argument structure. They commonly have a small succession of discourse parts:

```text
INDICATION/TITLE
TAKE + INGREDIENT/QUANTITY LIST
PREPARATION
APPLICATION
optional EFFICACY/ATTESTATION
```

A linguistic study of Middle English recipe structure similarly divides the
genre into heading/purpose, ingredient list and preparation, application, and
additional comment. A fifteenth-century remedy-book survey notes the common
consultation convention of an ailment title followed by a `Take ...` formula.

Concrete fifteenth-century English manuscript wording is highly repetitive:

```text
Take [plants] and stampe hem to gedir
and do thereto grese or buttir
and boyle hem
and clense hem thorow a clothe
and lete it stonde and kele
```

Manchester English MS 404 also has ingredient lists with `of eche liche
meche`, boiling in a measured amount of well water `till` it is reduced,
straining, cooling, placing in a vessel, stopping the vessel, waiting, and
giving the result to the sick person. These are ordinary operational chains,
not elaborate prose.

Latin formularies are even more card-like:

```text
Recipe X [amount], Y [amount], ana [amount].
Misce et fiat pulvis / emplastrum / cataplasma.
```

A catalogued medical manuscript entry gives `Recipe conserve violarum ... ana
uncias II`; another gives `Recipe nucis muscate ... ana dragmas II`. A
machine-readable Italian/Latin recipe collection preserves the compact close
`Misce et fiat pulvis`. These examples do not prove Latin behind Voynich, but
they show that `TAKE`, equal allocation, quantity, mixing and product-type can
be compressed into a very small formulary.

Ordinary medieval abbreviations included suspension, contraction, Tironian
notes and special signs. A diplomatic form therefore need not preserve a
one-to-one word expansion. Yet the current Voynich theory goes further than
ordinary abbreviation: it posits learned whole cards plus renderer variants.
Historical abbreviation makes that possible, not established. There is no
known comparator here in which the entire recipe is encoded exactly like the
proposed Voynich card deck.

Useful sources:

- [Manchester English MS 404, 15th-century medical recipes](https://luna.manchester.ac.uk/luna/servlet/detail/Man4MedievalVC~4~4~112916~103710%3AMedical-recipes)
- [Durham Cosin MS V.iv.8 catalogue, 15th-century `Take ...` recipe](https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s1sn009x84b.xml)
- [Cambridge Curious Cures project](https://www.lib.cam.ac.uk/curiouscures)
- [Middle English Medical Recipes and Literary Play, 1375–1500](https://academic.oup.com/book/41401)
- [Late Middle English remedy-book genre description](https://www.peterlang.com/view/9783035198713/Chapter01.html)
- [HAB 429 Helmstedt manuscript catalogue with Latin recipe incipits](https://diglib.hab.de/?catalog=Lesser&db=mss&id=429-helmst&lang=en&list=ms)
- [Ricettario Fermo MS 69, `Misce et fiat pulvis`](https://corpus.atliteg.org/testi/ricettario-fermo-ms-69/88)
- [CERL abbreviation typology](https://www.cerl.org/resources/links_to_other_resources/tools_decribing_mss_and_archival_materials)
- [Honkapohja, manuscript abbreviation history and typology](https://varieng.helsinki.fi/series/volumes/14/honkapohja/)

## Two candidate source orders

### Ordering A — Latin formulary / apothecary memorandum

```text
AD [condition] / [title]
R. [pictured simple, silently inherited]
   [item/state] [amount or grade]
   [item] [amount]
   ana / cum / et [relation]
M. F. [product or committed preparation]
Da / appone / unge [application]
```

Properties:

- `Recipe` naturally occupies an entry slot;
- substance names and amount marks can alternate without full syntax;
- `ana`, `cum`, and `et` supply compact internal relations;
- `Misce, fiat ...` naturally creates a payload-bearing terminal card rather
  than punctuation;
- the pictured plant, vessel or body can silently supply the first argument;
- a copied `R.` at a line boundary is plausible as a catch/head repetition.

### Ordering B — vernacular imperative chain

```text
For [condition, often heading or picture]
Take [pictured plant/part]
and [item]
and [item]
stamp/grind them together
put thereto [medium]
seethe until [state]
strain and let cool
give / lay / anoint [patient or place]
```

Properties:

- repeated conjunctions readily yield `X LINK Y LINK Z`;
- actions create longer discourse chains that need not end at line breaks;
- pronouns and inherited objects license radical ellipsis;
- result-state and application phrases can be short closed fields.

### Selection

**Ordering A is the better immediate compiler source.** It explains the
stronger facts with fewer invisible words: exact qokaiin at entry, parameter
cards, short Bio fields, and distinct payload-bearing close cards. Ordering B
is retained as the likely expanded reading of some operation sequences, or as
a vernacular upstream source that the workshop normalizes into Ordering A.

The selected historical path is therefore:

```text
Latin, vernacular, or mixed practical note
    ↓ normalize to formulary order
ADDRESS — R/ENTRY — ITEM/RELATION/PARAMETER — M.F./COMMIT — APPLICATION
    ↓ omit pictured/inherited arguments
formula cards
    ↓ hand/register rendering
visible Voynich groups
```

This selects a **register syntax**, not Latin as the language.

## Compact source-phrase inventory

The whole system can be learned from a small repertory of phrase classes. A
trainee need not know a substitution alphabet.

| source phrase class | historically ordinary realizations | proposed card behavior | silence/inheritance |
|---|---|---|---|
| `ADDRESS` | `ad ...`, `pro ...`, `for ...` | page title, picture ownership, rare opening card | plant/body/apparatus usually pictured |
| `ENTRY` | `Recipe`, `Take`, `Item` | field-initial head with diverse continuations | repeated head can be omitted or carried |
| `ITEM` | ingredient, plant part, medium, vessel | exact local card | page picture may replace principal item |
| `LINK` | `et`, `cum`, `de`, `in`, `ad`, `of`, `with`, `thereto` | internal high-diversity relation card | relation may be implied by field stencil |
| `EQUAL/SHARED` | `ana`; `of each alike much` | paired/list allocation construction | operands can be inherited from adjacent cards |
| `PARAMETER` | ounce, drachm, handful, spoonful, degree, duration, index | portable value/address card | actual unit or referent may be stencil-known |
| `PREPARE` | grind, pound, mix, boil, strain | action or whole instruction card | object inherited from preceding list/picture |
| `STATE` | powdered, warm, cold, fine, sufficient, until reduced | interior qualifier/state card | process itself may be formula-known |
| `COMMIT_PRODUCT` | `Misce et fiat pulvis/emplastrum`; let stand/cool | exact payload card in attached close realization | local closure marks completion, not sentence end |
| `APPLY` | give, drink, lay, anoint, put in vessel | final/open continuation card | patient/body/place often pictured or dossier-known |
| `CONTINUE` | `item`, `deinde`, `iterum`; and then | same head or transition into next field | previous object/state inherited |

This is deliberately no larger than what a workshop apprentice could learn:
about ten functional phrase classes plus the common exact-card deck and copied
local vocabulary.

## Concrete provisional card expansions

These are ranked guesses, not identifications.

### Exact `qokaiin`

Best expansion class:

```text
R. / Recipe / Take / Enter the following item
```

Reason: 7/9 field-initial occurrences and nine different right neighbors fit a
formula head unusually well. The f82r line-boundary doubling fits a repeated
or anticipatory recipe head. The card could abbreviate a whole instruction
frame, not the word `recipe`.

Working probabilities:

- entry/take/use formula: `.48`;
- generic record-start or reference head: `.27`;
- ordinary lexical content coincidentally entry-biased: `.25`.

Do **not** extend this to visibly similar `qokain`, `qokeey`, or `qokedy`:
they are distinct exact cards.

### Exact L/O card (`chol`/`ol` realizations)

Best expansion class:

```text
RELATE: et / cum / de / in / ad / of / with
```

The most concrete current guess is **WITH/AND**, because the Bio sequence
`Y – L/O – X – L/O – CLOSE` resembles a homogeneous list. But a compact
formulary relation can change its spoken expansion with its operands. Treat it
as a relation slot before treating it as one conjunction.

- general relation/link: `.44`;
- AND/WITH specifically: `.29`;
- ANA/equal allocation: `.10`;
- nonrelational class marker: `.17`.

### Exact AIIN card

Best expansion class:

```text
PARAMETER: amount / measure / grade / duration / table index / reference
```

Latin formularies strongly support the existence of such a slot, but the fixed
pages do not select quantity from the broader class. Its 20 occurrences span
first, middle and last position, and it does not demand immediate closure.

- general typed parameter/address: `.39`;
- quantity or equal amount: `.21`;
- item/concept identity: `.20`;
- other: `.20`.

### Exact Y card

Best expansion class:

```text
generic typed ITEM / UNIT / REFERENT slot
```

It may behave like an ideographic register marker more than a source word. Free
surface `dy` can be this Y card under a `d` wrapper and is not automatically a
closure.

### Exact CTHY card

Best expansion class:

```text
prepared/qualified STATE or PROPERTY
```

Possible ordinary expansions include `prepared`, `powdered`, `fine`, `warm`,
`cold`, or a named humoral/technical state. There is no basis to choose DRY.

### `Y – AIIN – Y`

Best source-like expansion:

```text
ITEM/TAG — SHARED OR TYPED PARAMETER — ITEM/TAG
```

Most aggressive historical paraphrase:

```text
of these two entries, use the same registered measure
```

This resembles the function of Latin `ana` or Middle English `of eche liche
meche`, but the visible order is not the normal full Latin sequence
`X, Y, ana [amount]`. The compiler would therefore have to encode a form slot,
not copy word order. Confidence: `.35` for a paired parameter frame, `.14` for
equal quantity.

### Attached DY/B3 close

Best source-like expansion:

```text
M. F. [named preparation/state]
```

or, in vernacular expansion:

```text
mix/prepare/put it thus; this cell is complete
```

The exact terminal card still carries unknown payload. The attached close is
the commitment realization of that card. It is not merely a period and need
not terminate a line, record, or sentence.

### Carried `qokaiin`

Best expansion:

```text
line n:     ... | R.〈anticipatory/catch head〉
line n+1:   R. [first actual entry] ...
```

Logical reading counts this as one instruction head repeated by layout. A
second possibility is deliberate lexical repetition, `take ...; take ...`.
The first is cleaner locally but must not become a universal resume rule.

## Pseudo-translation excerpts

Brackets mark unknown card payload. Small capitals are anonymous phrase
classes. None of these are proposed plaintext strings.

### Herbal f10r.5–6 — pictured simple with a property and parameter frame

Surface:

```text
f10r.5 qokchy qotchol chol cthy
f10r.6 ycheor cthy chor cthaiin qoctholy dy chy taiin shy
```

Card-aware pseudo-expansion:

```text
[For the simple pictured above:]
[entry/class A] [entry/class B], WITH/OF [prepared property].
[part/use C] [prepared property] [relation D] [parameter E]
[condition F]; ITEM ITEM — TYPED/SHARED PARAMETER — ITEM.
```

Readable workshop paraphrase:

> Of the pictured simple, use the registered part or preparation A with the
> stated prepared quality. Record the further parameter and its associated
> items under the same dossier.

This is less satisfying than the Bio parses because no exact qokaiin or close
occurs. It may be descriptive materia medica rather than a recipe. Water could
be an omitted medium or one of the unknown cards, but no card is read WATER.

### Herbal-B f55v.5 — strongest short formulary candidate

Surface and fields:

```text
qokaiin chaiin ykain ykan ody | daiin chedy talam
```

Pseudo-expansion:

```text
R. [of the pictured simple] PARAMETER [adjunct A] [adjunct B];
M.F. [preparation C].
PARAMETER [process/state D]; M.F. [product E].
```

Readable workshop paraphrase:

> Take or enter the pictured simple at the stated amount or grade, with the two
> listed adjuncts; prepare the first registered form. At the stated parameter,
> carry out the following process and complete the resulting preparation.

This is the best mini-translation in the fixed Herbal set because the exact
entry-head candidate starts the field and both fields end in attached commits.
It still identifies no ingredient, operation, amount, or product.

### Herbal-B f55v.11 — preparation then open application/detail

Surface:

```text
ykaiin cheoar cheeky oldy | aiin okal oltchy or y orain
```

Pseudo-expansion:

```text
[item/state A] [relation B] [process C]; M.F. [preparation D].
PARAMETER [item E] [state F] [relation G] ITEM [application/detail H].
```

Readable workshop paraphrase:

> Prepare the pictured material according to the first registered condition
> and commit that preparation. Then record its amount, accompanying item or
> state, and the still-open application detail.

The second field remains open; it need not be a sentence fragment caused by a
missing close. It may intentionally continue the dossier.

### Biological f81v.17–18 — compact checked-cell form

Surface:

```text
f81v.17 sshkchdy | chedy ol shedy | qolchedy |
         qokain shckhy dl ral
f81v.18 qokchdy | chey ol cheky ol shedy | qokedy |
         qokedy | chckhy qoky
```

Pseudo-expansion:

```text
[cell A, committed] |
[item/process B] WITH [product/state C, committed] |
[cell D, committed] |
[local head E] [configuration F] [site/value G] [qualifier H]

[cell I, committed] |
ITEM WITH [item J] WITH [product/state C, committed] |
[cell K, committed] | [cell K, committed] |
[configuration F] [setting L]
```

Readable workshop paraphrase:

> Complete the first setting. Combine or associate the next item with the
> stated prepared result and commit it. Complete the following setting, then
> leave the listed configuration details open. In the next record, commit the
> first setting; place one generic item with two related entries and commit the
> same terminal preparation. Repeat the next committed setting twice, then
> record the final configuration.

The repeated terminal `shedy` exact card across both list-like fields is better
read as the same **registered preparation/result card under commitment** than
as punctuation. The two L/O occurrences in f81v.18 give the best local support
for AND/WITH-like relation behavior.

### Biological f82r.2–4 — line carry and inherited head

Surface:

```text
f82r.2 dchedy | qolchedy | qokain dy qokeedy |
        qokal lcheckhy lched
f82r.3 qokeey lcheckhedy |
        qokaly solkaiin chckhy qokaiin
f82r.4 qokaiin octheol chkeey ldy |
        oteey qokal sheckhy qoky
```

Pseudo-expansion:

```text
[commit A] | [commit B] |
[local head C] ITEM [commit state D] |
[item E] [configuration F] [detail G]

[item/process H] [commit I] |
[setting J] [parameter/detail K] [configuration F] R.〈carry〉

R. [medium/operation L] [state M] [commit N] |
[continuation O] [item E] [configuration P] [setting Q]
```

Readable workshop paraphrase:

> Complete settings A and B. Enter the next item and its committed state; add
> its configuration details. Complete the following preparation. Under setting
> J, retain parameter K and configuration F. **Take/enter—** [line reflow]
> **take/enter** the next medium or operation, bring it to state M, and commit
> it; continue with item E and its final configuration.

This is the best explanation of the exact qokaiin duplication without making a
physical line a sentence boundary. The object of `take/enter` is supplied only
on the second physical line. The first occurrence can be a catch/reflow copy.

### Biological f83r.3 — paired parameter inside an otherwise closed form

Surface:

```text
olkeedy | qotal chkeedy | chey daiin chey lchedy |
qokaiin qotal dar
```

Pseudo-expansion:

```text
[commit A] |
[item B] [commit C] |
ITEM — TYPED/SHARED PARAMETER — ITEM [commit D] |
R. [item B] [qualifier/site E]
```

Readable workshop paraphrase:

> Complete the first preparation and the next item-specific setting. Assign or
> record the same typed parameter across the two generic item slots, then
> commit that cell. Take or enter item B with the listed qualifier or site.

More aggressive but weaker:

> ... of each of the two entries, use the same measure ...

The latter is the `ana` hypothesis. It is attractive historically but not yet
licensed by independently symmetric operands.

### Biological f83r.6 — repeated product card and entry head

Surface:

```text
schedy | chedchy qokal olchedy |
qokaiin chedy qokeedy | lchedy | qoky
```

Pseudo-expansion:

```text
[commit A] |
[component B] [item C] [commit D] |
R. [component/process E] [commit state F] |
[commit G] | [open setting H]
```

Readable workshop paraphrase:

> Complete A. Combine component B with item C and commit preparation D. Take
> or enter component E and complete its prepared state. Commit the following
> setting, leaving the final setting open for continuation or visual ownership.

Again, distinct terminal card identities carry distinct unknown payloads; the
English verbs are expansions of the record ecology, not decoded words.

## What the pictures and prior record make silent

The theory becomes much more economical if silence is systematic rather than
arbitrary.

### Herbal silence

The plant drawing can supply:

- the principal simple;
- its visible part or whole-plant identity;
- the page-level dossier address;
- sometimes an obvious medium/ecology, including water, without a WATER card.

Thus a field can begin with a property, quantity, preparation or application
instead of repeating the plant name.

### Biological silence

The figure/vessel/conduit geometry can supply:

- patient or apparatus;
- body/site or vessel destination;
- source and target of an application;
- which repeated cell the text belongs to.

Short closed fields can therefore encode `setting + state + commit`, not full
sentences. The diagram need not prove that the content is hydrotherapy; water
is only one historically and visually plausible medium.

### Within-record inheritance

A prior field can supply:

- current item mixture;
- current process;
- current destination;
- current quantity unit;
- current instruction head.

This makes `R.` repetition, zero subjects and short result cells ordinary.
It also explains why a statement can span physical lines and why the first
qokaiin at f82r.3 may be layout-induced.

## How a 1420 workshop learns it

The system does not require each scribe to memorize 1,676 meanings.

1. Learn a common deck of about twenty high-frequency cards.
2. Learn a handful of field stencils: open dossier, item list, parameter cell,
   process/result cell, committed close.
3. Learn the formulary order `ENTRY → ITEM/RELATION/PARAMETER → PRODUCT-CLOSE`.
4. Copy rare local cards from the page or register exemplar.
5. Apply hand-specific wrapper/joining habits.
6. Reflow around the already drawn image; repeat a head when needed.

This is comparable in cognitive difficulty to learning ordinary abbreviation
and a specialist formulary, even if the surface codebook is unusually opaque.

## Astro compatibility without forced integration

The selected phrase source does not translate f67r2, f68r1 or f69v. The
circle pages are better treated as separate local lookup tables using the same
workshop practices:

```text
diagram supplies system and slot
label/card supplies local entry
position supplies relation/order
renderer supplies surface form
```

The 7-, 12-, 28- and 29-member structures can therefore coexist with medical
formularies in a practical codex without every label sharing the prose deck.
If Astro supplies WHEN/configuration, it does so as a separate lookup annex,
not through a demonstrated pointer from these prose pages.

## Explanatory gains over the V2 basis

This candidate adds a concrete upstream grammar:

```text
ADDRESS — RECIPE/ENTRY — ITEM LIST — PARAMETER/RELATION — PREPARE — FIAT/CLOSE
```

It explains jointly:

- qokaiin's entry bias and continuation diversity;
- the usefulness but semantic breadth of L/O;
- AIIN as a parameter rather than automatically a quantity;
- Y as a typed slot rather than a noun;
- CTHY as a preparation/property state;
- attached close as `unknown product/state + fiat/commit`;
- distinct exact closer payloads;
- `Y–AIIN–Y` as a form-level shared/typed-parameter construction;
- physical-line carry without a sentence boundary;
- picture-supplied plant, apparatus and site arguments;
- multi-scribe learnability through formula order and exemplar copying.

## Awkward observations

1. Ordinary Latin and English abbreviations do not by themselves explain the
   extraordinary opacity and compatibility of Voynich forms.
2. Exact qokaiin has only nine occurrences in this fixed prose subset. One
   carry event heavily influences its narrative value.
3. L/O occurs on only three fixed pages; it is not yet a universal connector.
4. AIIN has no demonstrated numeric or visual quantity owner.
5. `Y–AIIN–Y` has only two occurrences and its surface order is not ordinary
   Latin `ana` syntax.
6. Herbal A is mostly open and difficult to segment into authentic recipe
   stages; it may contain description or indexing rather than instruction.
7. Bio images do not independently identify the operations, products, or
   anatomical sites used in the pseudo-translations.
8. The terminal payload cards remain mutually uninterpreted. Calling all of
   them `fiat` would incorrectly erase exact identity.
9. A visual pattern/form-filling book could generate similar record syntax
   without medical source phrases.

## Discriminating next predictions within the same ten pages

These predictions follow from the selected source ordering and were not needed
to write the individual pseudo-translations.

1. **ENTRY_HEAD:** exact qokaiin should precede a broader range of local item,
   parameter and state card classes than frequency-matched interior cards; its
   right continuation should not collapse to one exact phrase.
2. **RELATION_CHAIN:** L/O should be most useful between two similarly placed
   item/state cards, especially in variable-arity Bio lists. If it instead
   predicts one right card, demote AND/WITH.
3. **PARAMETER_ADJACENCY:** AIIN should neighbor generic item/type cards or
   local entries more often than terminal/product cards. Failure demotes the
   parameter reading.
4. **PRODUCT-CLOSE:** exact close-card identity should predict the preceding
   local construction better than a generic closure flag alone. Failure leaves
   only punctuation/commit behavior.
5. **CARRIED_HEAD:** when the f82r doubled qokaiin is counted once, the logical
   parse should become more stencil-regular, not less. If no improvement
   appears, prefer ordinary repetition or dittography.
6. **SILENT_ADDRESS:** Herbal lines should need fewer explicit entry heads than
   Bio cells because the single large plant image supplies the dossier subject.
7. **PAIR_FRAME:** the two Y–AIIN–Y cases should occupy a relation/parameter
   location, not a terminal result slot. If the surrounding items are not
   remotely parallel, withdraw the `ana` analogy.

## Best current translation excerpt

If forced to hand a workshop trainee one short expansion key, it would be:

```text
qokaiin     R. / take or enter the following registered item
L/O         relate it: with / and / of / in, as licensed by the stencil
AIIN        enter the registered parameter, amount, grade or reference
Y           generic item/unit/reference slot
CTHY        prepared or qualified state
...+CLOSE    make/commit the named local preparation or state
```

And the best consecutive paraphrase is f82r.3–4:

> Complete the preceding preparation. Under the current setting retain the
> stated parameter and configuration. **Take/enter—** [the scribe reaches the
> line boundary and repeats the head] **take/enter** the next medium or process,
> bring it to the registered state, commit it, and continue with the associated
> item and configuration.

This is useful because it is a coherent, historically ordinary instruction
shape and explains the visible carry. It is not a deciphered clause.

## Verdict

The strongest V3 evolution is not “Voynich is abbreviated Latin.” It is:

> A mixed-language workshop could normalize practical notes into a Latin-like
> formulary order, omit the subject and other arguments supplied by picture or
> prior field, and write the remaining ENTRY, ITEM, RELATION, PARAMETER, STATE
> and PRODUCT-COMMIT packets as learned exact cards.

Latin formulary order is the best current source model; vernacular imperative
chains remain the best expansion model. This makes the existing card theory
more concrete without pretending that any Voynich group has a confirmed Latin,
English, Georgian, Mingrelian, or other reading.
