# Candidate theory: the pictured dispensatory and treatment scheduler

Status: independent speculative sidequest candidate, 2026-08-21. This is not a
GDT result, a decipherment, or a claim about language or origin. It deliberately
uses abductive historical plausibility and permits ranked meaning guesses. The
scope is only `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r`, `f83r`, `f67r2`,
`f68r1`, and `f69v`. `f84` and `f84r` were not accessed.

## Leading theory

The ten pages are best explained as parts of a **picture-addressed practical
dispensatory with treatment and timing sheets**, copied by a small workshop
around 1420.

The three registers do not narrate the same topic in the same syntax. They are
three interfaces to one working practice:

1. **Herbal dossier — select WHAT:** the pictured plant is the silent headword;
   the rows record usable part, class/quality, preparation, carrier or use.
2. **Biological sheet — specify HOW:** the drawn figure, pool, conduit or vessel
   is a silent treatment location; short checked cells specify preparation,
   medium, route/stage and completion.
3. **Circle sheet — choose WHEN/UNDER WHICH CONFIGURATION:** labels address
   cyclic lookup positions. They can constrain treatment timing or prognosis,
   but may also be a separate astronomical tool kept in the same practical
   miscellany.

This is not primarily an alphabetic cipher. A visible group is the rendered
form of a workshop card. Some cards probably abbreviate source-language words;
others are technical values or form controls. The same abstract card can appear
as `AIIN/DAIIN/SAIIN/CHAIIN/TAIIN`, or as the free
`Y/DY/CHY/SHY/SY/CHEY` family, because the wrapper is partly a scribal
constructional rendering rather than part of the card's narrow content.

The theory is intentionally stronger than the safe miscellany theory: it says
the dominant organizing problem is **turning pictured materia medica into an
actionable treatment entry**. The astronomical leaves are the least secure
part of the integration.

## How a workshop could generate the pages

The writing system must be learnable by several scribes without requiring them
to memorize a modern cryptographic algorithm. A plausible production workflow
is:

1. An artist or compiler copies the plant, treatment scene or circular diagram
   first. The image establishes the page's implicit subject and many repeated
   arguments.
2. A compiler consults mixed sources: a herbal/simple entry, recipes or bath
   instructions, and perhaps a calendar/prognostic table.
3. The compiler reduces each source passage into a short sequence selected from
   a common card ledger plus a register-specific supplement.
4. The register chooses the form:
   - Herbal uses relatively long, mostly open rows;
   - Biological uses several short, explicitly committed cells;
   - Astro writes local labels into already owned geometric slots.
5. A scribe renders each card through the locally licensed wrapper and
   JOIN/SPACE habits. `s` at physical-line entry and `q` after an attached DY
   close belong mainly to this entry/rendering layer.
6. The scribe reflows a continuing record around the pre-drawn picture. A line
   break is therefore not a sentence boundary. A value can be copied at the
   end of one line and resumed at the start of the next, as the repeated exact
   `qokaiin` card on `f82r` suggests.
7. Attached DY/B3 commits a local cell. It need not mean “end”, “done”, or any
   spoken word; it acts more like a check, resolved value, or compact recipe
   punctuation. Free surface `DY` remains the ordinary Y card under wrapper
   `d` and is not this closure.

In workshop terms, a trainee learns a **small common card book**, the closure
habits of the B exemplar shelf, and one addendum for each technical register.
Irregular full cards can be copied from exemplars. This is simpler and more
historically plausible than deriving every group by a clean prefix-root-suffix
algorithm.

## Provisional content dictionary

These are guesses about functional payload, not lexical translations. The
ordering is confidence-ranked within this speculative exercise.

| rank | anonymous form/card | best tentative role | deliberately weaker alternatives | reason |
|---:|---|---|---|---|
| 1 | attached DY/B3 close | `CELL_COMMITTED / VALUE_RESOLVED` | result reached; instruction terminator | It is local and constructional; Biological B uses it heavily, while free DY is a separate Y card. |
| 2 | AIIN exact card | `VALUE_OR_AMOUNT_REFERENCE` | item index; dose class; repeated entity | It occurs in all seven prose pages, tolerates wrappers, occupies first/interior/final positions, and usually does not itself trigger attached closure. |
| 3 | free Y exact card | `VALUE_TYPE_OR_UNIT_FRAME` | quality class; generic specified item | It combines on either side of AIIN and near closures, but its multiple wrappers prevent a literal `Y/DY` reading. |
| 4 | `Y → AIIN → Y` | `BOUNDED_OR_TYPED_VALUE_FRAME` | ratio; two-place relation; amount plus unit | It is the sole recurring three-card cross-page path and crosses unrelated pictures, making a portable value frame more plausible than an object name. |
| 5 | L/O exact card (`CHOL` Herbal = `OL` Bio) | `MEDIUM_OR_RELATION_CLASS` | “with/in/of”; treatment class | Cross-register identity rules out simultaneous `CHOL=HOT` and `OL=WATER`, but an abstract relation can connect a plant property and a bath/application field. |
| 6 | CTHY exact card | `PREPARATION_OR_RESULTING_STATE` | property/quality; processed-state class | It is chiefly field-interior and crosses Herbal/Bio wrappers. A general state survives where `DRY` does not. |
| 7 | OR→Y path | `RELATION_PLUS_TYPED_VALUE` | carrier plus measure; class plus qualifier | The exact path repeats on three pages under dissimilar wrappers. It may be a short parameter phrase rather than two independent lexical words. |
| 8 | `qokaiin` exact carry on f82r | `ACTIVE_ENTRY_CARRIED_FORWARD` | current material; treatment subject; unresolved value | Exact repetition across a physical line inside one record resembles copying the active operand into the next row, but one occurrence pair is not enough to call it “same” or “continue”. |
| 9 | Biological OKE/OK/LCHE/CHE/CKHY deck | `LOCAL_PROCESS_OR_CONFIGURATION_VALUES` | media, routes, body zones, apparatus states | Their Biological concentration and closing behavior indicate technical payload, but no individual member is yet separable as “wash”, “heat”, “woman”, or “water”. |
| 10 | Astro labels | `LOCAL_SLOT_VALUES` | named objects; dates; prognostic states | The geometry owns the labels. No prose card identity may be imported because the circle pages lack GDT327 coverage. |

### Water hypothesis, kept narrow

Water is highly plausible at the **record level**, especially in the
Biological register and potentially as a preparation medium in Herbal. It is
not assigned to `OL`, `CHOL`, AROL, or any other one group. In this theory,
“water” is more likely to be:

- supplied silently by a depicted pool or conduit;
- one value among the Biological local deck;
- or expressed compositionally as `MEDIUM_RELATION + LOCAL_VALUE`.

That explains why no portable common card needs to translate literally as
WATER.

## Representative speculative parses

The brackets are working paraphrases at the card/function level. They are not
recoveries of source-language sentences.

### `f10r.6` Herbal

Observed portable tail:

```text
CHY  TAIIN  SHY
 Y     AIIN   Y
```

Provisional parse:

```text
[VALUE-TYPE : AMOUNT/REFERENCE : VALUE-TYPE]
```

Strongest guess: the row ends with a bounded specification such as a dose,
ratio, paired quality or two-part classification for the pictured simple. The
picture supplies `[THIS PLANT]`; the text need not repeat its name.

### `f83r.3` Biological

Observed field head and close:

```text
CHEY  DAIIN  CHEY  →  LCHE-CLOSE
  Y     AIIN    Y      attached close
```

Provisional parse:

```text
[VALUE-TYPE : AMOUNT/REFERENCE : VALUE-TYPE] [COMMIT LOCAL SETTING]
```

The same portable frame is inserted into a treatment/apparatus cell, then a
Biological-specific closure resolves it. This is the strongest miniature of
the whole theory: common value grammar plus local technical implementation.

### `f10r.9`, `f55v.11`, `f83r.38`

Exact recurrent path:

```text
OR → Y
```

Provisional parse:

```text
[RELATION/MEDIUM-CLASS] → [TYPED VALUE]
```

Loose practical readings include “in/with [specified class]”, “for [specified
condition]”, or “carrier of [typed value]”. The surface wrappers vary, so a
fixed two-word plaintext phrase is less likely than a reusable parameter slot.

### `f81v.17` and `f82r.7`

Shared form stencil:

```text
1C | 3C | 1C | 4O
```

Provisional parse:

```text
[select/commit] |
[configure three-card setting/commit] |
[select/commit] |
[open continuation or result note]
```

Eight of nine cards vary, while one exact `shedy` closer remains. This resembles
a reusable treatment form with variable entries more than a repeated sentence.
The final open field may carry a result, exception, or continuation that cannot
be reduced to the checked cells.

### `f82r.3 → f82r.4`

The exact `qokaiin` card ends one line and begins the next within the same
paragraph record.

Provisional parse:

```text
... [ACTIVE OPERAND/SETTING X]
[X RE-ENTERED] ...
```

This could be the manuscript analogue of a ditto/carry instruction, but the
identity may simply be ordinary lexical repetition. The theory predicts that
the downstream row continues the same local treatment object rather than
starting a new recipe.

### Herbal open row

The common four- or five-open-card Herbal stencil is provisionally:

```text
[PICTURED SIMPLE] : CLASS/QUALITY : USABLE PART OR STATE :
PREPARATION/RELATION : VALUE/USE
```

The exact order may vary, and not every entry has every slot. The image is the
silent address; the row is not required to begin with a plant name or command.

### Biological closed cell

A short Biological cell is provisionally:

```text
[SILENT DRAWN LOCATION] : LOCAL SETTING/PROCESS VALUE + [COMMIT]
```

Several cells can belong to one treatment record. Nude figures need not each be
patients or named persons; they can point to stages, locations or applications.

### `f67r2`, `f68r1`, `f69v`

At the only justified resolution:

```text
f67r2 = choose among layered 7/12/central local values
f68r1 = identify a central item and 28 surrounding catalogue entries
f69v  = step through an ordered 28-entry schedule with alternating layout state
```

The medical-workshop reading is “consult the appropriate timing/configuration
sheet before or alongside treatment.” No label is assigned a planet, sign,
lunar mansion, day, number or prognosis. The safer alternative is that these
are independent astronomical reference leaves in the same miscellany.

## Why the three registers can belong together

The integration does not require every card to be shared. A working medical
book naturally needs different local vocabularies:

- a simple can be indexed visually and then described by qualities,
  preparation and use;
- a bath/application diagram can omit the repeatedly pictured medium and body,
  leaving compact configuration cells;
- a timing wheel can omit prose and place values directly in cyclic slots.

The shared H/B cards then carry portable administrative or parametric content
(`RELATION`, `VALUE`, `TYPE`, `STATE`), whereas the Biological-private tail
carries specific process/configuration values. The f55v bridge follows B
rendering habits while remaining Herbal in subject, exactly what a shared
workshop with topic addenda predicts.

Medieval precedent supports the **cohabitation**, not the decoding. British
Library Harley MS 1736 combines surgery, medicinal recipes, an astrological
medical tract, seven planets and zodiac tables. Add MS 29301 combines an
illustrated surgical work, recipes, *Circa instans* simples and a health
treatise, with related workshop art including a Zodiac Man. Add MS 41623 is a
northern Italian herbal whose contents include a treatise on nineteen herbs
under zodiacal and planetary influence. Such combinations make WHAT/HOW/WHEN
historically ordinary enough to be plausible, though not specific enough to
identify the Voynich tradition.

## Awkward facts and possible failures

1. **No external bridge links the three registers.** WHAT/HOW/WHEN is an elegant
   editorial reconstruction, not a demonstrated cross-reference system.
2. **The sole `Y-AIIN-Y` formula has only two occurrences.** It may be a chance
   collision or generic orthographic grammar rather than a value frame.
3. **No common card has a confirmed practical meaning.** `AIIN=amount` and
   `L/O=relation` are useful guesses, not translations.
4. **The plant pictures are silent addresses only by hypothesis.** Herbal rows
   could still be descriptive prose, lore, habitat notes or something
   nonmedical.
5. **Biological drawings may not depict baths or treatments.** They may be
   cosmological, allegorical or mnemonic diagrams. Even if water is depicted,
   the text may encode topology rather than therapy.
6. **Astro has no exact-card bridge.** Surface similarity cannot legally import
   the prose ledger, and f68r1 lacks an authorial cyclic order.
7. **Checked cells may be graphical grammar, not completed parameters.** B's
   closure preference could be scribal habit alone.
8. **A card ledger is not directly attested by the historical comparators.** A
   heavily abbreviated phrasebook, nomenclator or constrained natural language
   could generate similar structure.
9. **Many page-opening forms are unique.** If the system were a highly
   standardized dispensatory, repeated entry headers might be expected. The
   image-address model explains their absence, but does not predict the unique
   openings positively.

## Five novel predictions

These predictions are consequences of this candidate and were not used to
choose its individual glosses.

1. **Portable-value prediction.** On untouched nonsealed Herbal/Bio pages,
   `Y-AIIN-Y` or shorter AIIN/Y frames should preferentially occupy variable
   slots inside otherwise recurrent field stencils, while local technical cards
   determine the page-specific surrounding content. Failure across a modest
   additional page set would demote the value-frame reading.
2. **Silent-medium prediction.** Biological records visibly owned by the same
   pool/conduit/vessel should share more of the local process/configuration deck
   than records linked only by page position. The portable L/O card need not be
   enriched; if one common card alone tracks every aqueous picture, this theory's
   compositional water account is wrong.
3. **Commitment prediction.** Attached closers should follow filled local
   settings and should be less likely before a same-record line carry or an
   unresolved repeated operand. A closer that behaves interchangeably with free
   Y would falsify the crucial free/attached distinction.
4. **Register-form prediction.** A further Herbal page written in a B hand
   should resemble f55v in closure frequency and wrapper ecology but retain a
   Herbal rather than Biological local-card inventory. Conversely a Bio page in
   a different hand should keep short-cell topology while changing renderer
   preferences.
5. **Timing-sheet prediction.** If the circle leaves serve practical timing,
   repeated surface labels within a single ordered array should act as repeated
   schedule states at geometrically nonrandom positions, not as a universal
   dictionary shared freely across f67/f68/f69. If later external evidence gives
   a fixed order, the pattern should align without choosing a phase from the
   text.

## Sources used for historical plausibility

- [British Library, Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567):
  a 1446 and later medical miscellany containing surgery, recipes,
  pseudo-Hippocratic medical astrology, seven planets and zodiacal tables.
- [British Library, Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783):
  c. 1420–30 illustrated surgery, recipes, *Circa instans* pharmaceutical
  simples and a health treatise; the catalogue also identifies associated
  workshop astronomical imagery.
- [British Library, Add MS 41623](https://searcharchives.bl.uk/catalog/032-002085314):
  northern Italian herbal material including a treatise on nineteen herbs
  according to zodiacal and planetary influence.
- [British Library, Harley MS 2390](https://searcharchives.bl.uk/catalog/040-002048221):
  fifteenth-century medical and cosmetic recipe book with herbal medicine,
  preparation/administration and zodiac material.
- [University of Edinburgh, MS 176](https://archives.collections.ed.ac.uk/repositories/2/archival_objects/160996):
  a fifteenth-century *De balneis Puteolanis* witness with little text and large
  half-page bath illustrations, demonstrating that bath knowledge could be
  organized around picture-led pages.
- [Morgan Library, MS G.74, *De balneis Puteolanis*](https://ica.themorgan.org/manuscript/page/20/77063):
  catalogue description of a multi-level bathhouse scene with nude bathers and
  bodily gestures.
- [Data Mining a Medieval Medical Text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7018648/):
  analysis of the fifteenth-century *Lylye of Medicynes*, documenting recipes
  with ingredients, quantities and operations such as boiling, powdering and
  infusing.
- [Medieval herbal iconography of *Cucumis*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3158695/):
  peer-reviewed account of illustrated herbals as accumulated simple-medicine
  knowledge and aids to plant identification.
- [Evidence for continued use of medieval medical prescriptions](https://pmc.ncbi.nlm.nih.gov/articles/PMC4847415/):
  a fifteenth-century practical remedy collection whose recipes include
  ingredients, acquisition, preparation, application and abbreviated efficacy
  endings.

These sources license only the proposed book ecology and workflow. They do not
license any Voynich card meaning, provenance, donor text or language.

## Confidence-ranked summary

### HIGH within the sidequest evidence

- The system is hierarchical: picture/page address, paragraph record, physical
  reflow line, field, exact card, renderer and local closure are distinct.
- Several surface spellings collapse to the same exact card; free DY is not the
  attached close.
- Herbal and Biological share a portable card core but use different form
  densities and local inventories.
- `f81v.17`/`f82r.7` show a reusable form stencil populated by different cards.

### MEDIUM as an abductive reconstruction

- The seven prose pages belong to one practical medicinal workflow.
- Herbal pictures serve as silent simple-drug addresses.
- Biological pages encode bath/application/apparatus settings in checked cells.
- Common cards carry generic parameter/relation/value functions, while local
  cards carry technical content.

### LOW but worth retaining

- `AIIN` is an amount/reference rather than merely a generic card.
- `Y-AIIN-Y` is a bounded value, ratio or typed-measure frame.
- L/O is a medium/relation class and CTHY a preparation/resulting state.
- The circle sheets provide the WHEN/configuration component of the same medical
  practice.

### VERY LOW / explicitly not claimed

- Any individual card equals WATER, BOIL, WASH, TAKE, PLANT, WOMAN, PLANET,
  DAY, or another English lexeme.
- The Biological pages are specifically gynecological.
- The language, region, phonology, author or donor manuscript is identified.

The best compact paraphrase is therefore:

> For the object supplied by the picture, fill a register-specific practical
> form with shared relation/value cards and local preparation or treatment
> settings; commit resolved cells, carry unresolved entries across the available
> writing space, and consult a separate cyclic sheet when timing or
> configuration matters.
