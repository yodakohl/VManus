# GDT666 historical codebook analogue memo

## Clerk's conclusion

The best historical analogue is **not** a one-letter substitution cipher and
not a prose dictionary. It is a compact workshop breviary: a small productive
inventory of command heads, process and material abbreviations, quantity or
grade tails, plus memorized preparation names and closing formulae. That is a
good architectural match for the current 47-role model and its 151 new cards.
It does not identify a single Voynich value.

The accompanying `CARD_SPECS_HISTORICAL_CANDIDATE.tsv` keeps every surface and
composition exactly as supplied. It has 151 cards in the same order: 129 are
compositions of existing roles and 22 are learned wholes. I changed only the
German working reading, rival, or family where the historical comparison made
the result more economical or prevented one role from doing two jobs at once.

## Ranked analogues

### 1. Command sign followed by compressed payload — strongest analogue

Real recipe manuscripts repeatedly begin an entry with *Recipe* or *Accipe*
and then append ingredients, quantities, and operations. In the mid-fifteenth-
century North Italian Wellcome MS.683, examples include *Recipe ... infunde in
aceto*, *Recipe ... ana grani ii*, and a closing *fiat pessarium*. The same
manuscript mixes named dosage forms—ointment, plaster, oil, powder, pills, and
pessary—with short procedural clauses. This is very close in **format** to
`QO_COMMAND + payload`, and to learned command blocks such as `QOL_ADD`; it is
not evidence that the Voynich shape `qo` literally expands to Latin *Recipe*.

Source: [Wellcome MS.683, North-East Italy, mid fifteenth century](https://wellcomecollection.org/works/w6ne7k4t).

Cappelli's abbreviation repertory makes the economy explicit: it lists `R`
and `Rec` for *Recipe*, `aa` for *ana*, `M ft` for *Mistura fiat*, `p` for both
*pulvis* and *pulverisare*, and `pp` for *praeparare*. A short command head may
therefore govern a compound payload, while one compact learned formula may do
the work of several ordinary words.

Source: [Ad fontes, searchable Cappelli repertory](https://www.adfontes.uzh.ch/en/ressourcen/abkuerzungen/cappelli-online), especially its [medical-abbreviation results](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/category/up/139).

### 2. Operations, materials, measures, and formulae in one register — very strong

The early-fifteenth-century Italian Wellcome MS.140 moves freely between Latin
and Italian recipe language. Its catalogue records commands to put material in
a furnace, convert it to water, take ingredients in ounces, calcine for twelve
hours, and distil as before. The same codex contains learned experiment names,
recipes for salts and waters, and a later ink recipe. A compact manuscript need
not choose between an operational codebook and memorized wholes: the historical
workshop register actually mixes both.

Source: [Wellcome MS.140, early fifteenth century](https://wellcomecollection.org/works/actgjagb).

Harley MS 2390 likewise mixes Latin and Middle English, medical and craft
recipes, ingredient names, weights, and end formulae. Its catalogue preserves
examples with *bulliat*, *libra*, an ounce/dram notation, and *fiat ... pulvis*.
That is a close analogue for a page on which process cards, material cards,
units, and a learned result-name all coexist.

Source: [British Library, Harley MS 2390](https://searcharchives.bl.uk/catalog/040-002048221).

### 3. Short signs are context-bound and polyfunctional — strong architectural analogue

Cappelli records single or very short medical signs whose reading depends on
register and position: `A` may stand for *alumen*, *atramentum*, or *amalgama*;
`D` can mean *digerere, siccare*; `p` can be the noun *pulvis* or the operation
*pulverisare*. Its `G/g` entries include medical *gutta*, Italian *grano
(peso)*, and Latin *gradus*. This strongly favors the **principle** behind the
current positional splits (`d-` versus `-d`, `s-` versus `-s`) and the decision
to retain rivals. It does not prove any one of the present Voynich assignments.

The practical consequence for GDT666 is important: do not force every repeated
shape into one modern dictionary head. A workshop clerk could read the same
short sign as a substance, process, quantity, or closure only inside a licensed
formula.

Sources: [Ad fontes medical category](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/category/4/9) and [Cappelli's `G/g` page](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/page_id/9/99).

### 4. Exact and rough measures coexist — strong analogue, weak exact mapping

MS.683 has *ana grani ii* and a recipe with drams. Harley MS 2390 combines
libra, ounce/dram notation, and vernacular fractions. A study of late-medieval
practical books notes that one physician's Ashmole miscellany uses apothecary
symbols for scruples and drachms, while other recipe books use rough measures
such as a handful or spoonful. This supports a single register containing
`AM_UNIT_I`, `MANIPULUS_SIGLUM`, `G_GRAIN_SIGLUM`, fraction roles, and repeated
number tails. It does **not** independently establish `ain=II` or `aiin=III`.

Source: [Jones, “Here Is a Good Boke to Lerne,” Journal of British Studies](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12/share/a024150fe1501e59df5b45628147fdd3df550196).

Cappelli also explicitly lists `man`/`MJ` for *manipulus* and conventional
signs for *dragma* and *uncia*. `g=ein Gran` is therefore a reasonable working
default. Its strongest rival should be `ein Tropfen`, however, because medical
`G=gutta` is equally real; the historical source itself warns against pretending
that the bare sign has one universal value.

Sources: [Cappelli `manipulus` entries](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/4/4/69), [conventional *dragma* sign](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/language/2/23), and [conventional *uncia* sign](https://www.adfontes.uzh.ch/ressourcen/abkuerzungen/cappelli-online/characters/down/8).

### 5. Material-part vocabulary and learned preparation names — good analogue

Fifteenth-century medical books combine botanical glossaries with recipe
collections. Harley MS 2374 contains a botanical glossary, an antidotary, and
Latin/Middle English recipes; Wellcome MS.5262, from the first quarter of the
fifteenth century, has a contents list for 129 recipes and practical directions
using named herbs. MS.683's learned dosage forms coexist with oils, wax, marrow,
and other named materials. This is compatible with broad cards for root, wood,
herb/leaf, seed, flower, powder, and compound preparation, surrounded by
memorized names. It does not tell us which Voynich stem names which plant part.

Sources: [British Library, Harley MS 2374](https://searcharchives.bl.uk/catalog/040-002048205) and [Wellcome MS.5262](https://wellcomecollection.org/works/nuckbt25).

## Concrete changes made to the 151-card candidate

1. **No doubled terminal `d`.** `ld` now defaults to “Holzdroge abschließen”
   with “Holzdroge abziehen” as its rival; `cthd` receives the same treatment.
   One `D_TERM_CLOSE` no longer performs both “abziehen” and “abschließen” in
   the same reading.
2. **`g` remains a grain, but gains the right historical rival.** Cappelli has
   both weight-*grano* and medical `G=gutta`; the candidate now records “ein
   Tropfen” rather than the uninformative “kleines Apothekengewicht.”
3. **A learned closer is phrased as a closer.** `eey` becomes “schließe den
   vorstehenden Rezeptposten ab,” analogous in register to a compact *fiat* or
   *mistura fiat* formula, without claiming a Latin expansion.
4. **Repeated grades become repeated passes.** `checthey` and `ycheckhey` now
   say “zweimal/mals mäßig trocknen,” not the unnatural “in zwei
   Mittelstufen.” Both visible `E_MIDDLE` atoms remain represented.
5. **Direction was repaired where the old prose outran the atom order.**
   `qopchaiin` is “drei Teile des getrockneten Pulveransatzes”; `qochol` takes
   dry drug material **as** an Ansatz rather than extracting it “from” one.
6. **Telegraphic cards stay telegraphic.** Several long readings now use
   “mäßig,” commas, and explicit second passes. They preserve each atom but no
   longer invent an elaborate causal sentence merely because the surface is
   long.

## What this does and does not buy us

The historical comparison makes the following model more plausible:

`COMMAND + [PREPARATION/MATERIAL] + PROCESS + GRADE + QUANTITY/CLOSE`

with occasional replacement of the whole string by a learned preparation,
measure, or closing formula. It also makes a roughly 85:15 split between
productive compounds and learned wholes entirely unsurprising for a practical
working book.

It does **not** license a direct Cappelli lookup of Voynich transliteration.
The manuscript's glyphs are not Latin letters merely because EVA/ZL3b prints
them as `q`, `p`, `d`, or `g`. The strongest historical payoff is therefore an
architecture and a style of concrete reading:

- short imperative, not “execute work step”;
- named material class, not “working substance”;
- explicit measure/grade, not an invented quantity hidden in prose;
- one atom, one contribution, unless the card is openly learned as a whole;
- a rival retained wherever real workshop sigla were polyfunctional.

## Recommended synthesis choice

Use `CARD_SPECS_HISTORICAL_CANDIDATE.tsv` as a conservative editorial layer on
top of the stem candidate. Its most consequential choices are `ld`, `cthd`,
`g`, `eey`, `checthey`, and `ycheckhey`; the remaining changes primarily make
the German output sound like a compact recipe register. If another independent
reader supplies better line-local values, retain this memo's architecture but
prefer the reader's concrete object or operation.
