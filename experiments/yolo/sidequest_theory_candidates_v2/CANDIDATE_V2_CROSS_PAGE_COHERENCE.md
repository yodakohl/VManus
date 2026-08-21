# V2 candidate — formula-card medical register with silent visual address

Date: 2026-08-21

Status: **independent sidequest theory, deliberately abductive, not a GDT
result and not a translation**.

Scope is fixed to `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r`, `f83r`,
`f67r2`, `f68r1`, and `f69v`. No `f84` or `f84r` material was accessed. The
seven prose pages were inspected only through the guarded f84-free GDT327 and
native-event slices. The three circle pages have no GDT327 events and are kept
at topology/layout level.

## Result in one sentence

The best next evolution is a **formula-card medical register**, not a general
purpose codebook: a pictured subject is normally silent; a small set of common
cards supplies instruction heads, links, parameters and qualifiers; Currier A
renders these in long open dossier clauses while Currier B renders much the
same practical material in short committed cells; rare content remains in
page/register-local cards. The astronomical pages are most safely a separate
lookup annex made by the same workshop, not the demonstrated `WHEN` half of a
single WHAT/HOW/WHEN database.

In compact form:

```text
shown plant / shown apparatus / shown diagram
       ↓ supplies subject and local namespace silently
ordinary practical source wording
       ↓ formulaic abbreviation and argument omission
HEAD? + ARGUMENT/LINK/QUALIFIER/PARAMETER cards
       ↓ one of two learned documentary modes
A: continuous open dossier clause
B: short cell sequence + local commitment marks
       ↓ hand-specific wrapper and physical reflow
visible Voynich groups
```

This retains the exemplar-led workshop architecture but makes it less
codebook-heavy and more specific. A trainee needs a small common formula deck,
two layout modes and a local glossary; the trainee need not memorize all 1,676
joint tuples or execute a modern cipher.

## What changed from the incoming theory

1. `qokaiin` is upgraded from a vague carried parameter to the best candidate
   **instruction/entry head**. A source expansion in the class TAKE / USE /
   ENTER is plausible, although no particular English word is assigned.
2. L/O is upgraded from a vague relation/class card to a likely **link or
   co-member relation**. Its repeated interleaving inside fields is stronger
   than its spelling.
3. `AIIN` remains a parameter/value/reference candidate, but its numerical
   interpretation is downgraded. Its placement is too broad for a bare number.
4. `Y–AIIN–Y` is retained as a **paired-slot parameter construction**, but
   “equal quantity” is only one low-confidence expansion. The Herbal occurrence
   has an extra preceding Y, so a simple binary equality formula is not forced.
5. Attached DY remains a local commitment boundary. The identities of the
   close-bearing cards do **not** look like clean semantic close types: the
   major identities span very different field lengths and predecessors.
6. WHAT/HOW/WHEN is demoted from integrated theory to optional codex-level
   organization. The circle pages fit a practical miscellany, but no cross-page
   pointer joins them to the seven prose pages.

## Fixed observational census

The seven prose pages contain 381 guarded GDT327 events.

| page | lines | records | events | fields | closed fields | line shapes |
|---|---:|---:|---:|---:|---:|---|
| f10r | 5 | 2 | 38 | 5 | 0 | `10O; 4O; 9O; 8O; 7O` |
| f11r | 3 | 1 | 17 | 4 | 1 | `7C+1O; 5O; 4O` |
| f55v | 2 | 1 | 18 | 4 | 3 | `5C+3C; 4C+6O` |
| f56r | 7 | 1 | 27 | 7 | 1 | `4O; 5O; 4C; 4O; 3O; 4O; 3O` |
| f81v | 7 | 1 | 66 | 24 | 17 | mixed short cells, ending open on every line |
| f82r | 8 | 1 | 62 | 26 | 19 | mixed short cells, including one all-closed row |
| f83r | 25 | 4 | 153 | 65 | 49 | dense closed R1/R2, looser R3, open R4 |

`O` means no attached close in the formal field; `C` means a DY/B3-bearing
terminal. These are structural descriptions, not open/closed grammatical
clauses.

The cleanest register contrast is therefore not simply Herbal versus Bio. It
is:

```text
Herbal A       mostly long, open abbreviation
Herbal B f55v  short, mostly committed cells
Bio B          short, mostly committed cells, plus open continuations
```

f55v is an actual bridge: it behaves like B while retaining a plant page.
That is more economical than treating Biological layout alone as a special
semantic language.

## Cross-register card behavior

### AIIN exact card — `2f1c5e56...`

Twenty events occur on all seven prose pages.

| subset | n | field placement | immediately before a close |
|---|---:|---|---:|
| Herbal | 9 | first 2, middle 4, last 3 | 0 |
| Biological | 11 | first 4, middle 5, last 2 | 0 |

This is remarkably stable in the weak sense: it is neither a pure entry head
nor a close. It fits a portable argument/parameter/reference card. It does not
behave narrowly enough to establish NUMBER or AMOUNT. A quantity/index reading
remains useful only because it occurs in the repeated `Y–AIIN–Y` construction
and often occupies compact formula environments.

Best provisional class:

```text
AIIN_CARD ≈ entered parameter / amount / degree / index / reference
```

Working confidence: `.28` for a parameter class, `.15` for specifically a
quantity.

### Y exact card — `b921a237...`

Eighteen events occur on six pages, split 9 Herbal and 9 Biological. It is
mostly field-internal in both registers. It repeats within four fields, more
often than most high-frequency cards, and appears as free `y`, `dy`, `chy`,
`shy`, `sy`, and `chey`-like renderings.

That behavior is compatible with a generic item/unit/reference placeholder,
but it is also compatible with a common relation-like card. “Type tag” is not
demonstrated.

Best provisional class:

```text
Y_CARD ≈ generic item / unit / reference slot
```

Working confidence: `.21`.

### L/O exact card — `dcda95c8...`

Nineteen events occur on f10r, f81v and f83r. Fourteen are field-internal.
Three separate fields repeat the card. Particularly suggestive strings are:

```text
f10r.8   ... CHOL ... CHOLOR CHOL ...
f81v.2   ... OL ... OL ...
f81v.18  CHEY OL CHEKY OL SHEDY-CLOSE
```

The third example has the abstract shape:

```text
X  LINK  Y  LINK  CLOSE
```

This is the best cross-register candidate for a functional relation. It might
expand upstream as AND, WITH, OF, IN, or a list/class connective; the data do
not distinguish those readings. It should not be identified with water.

Best provisional class:

```text
L/O_CARD ≈ LINK / CO-MEMBER / GENERAL RELATION
```

Working confidence: `.39` for a relational class, below `.15` for any one
English preposition or coordinator.

### CTHY exact card — `e0b630cb...`

Seven events occur on f10r, f11r and f83r. Six are field-middle and one is the
last card of an open Herbal field. It never carries closure itself. Every
occurrence has a different immediate left and right environment. Herbal uses
the unwrapped rendering while f83r uses `sh`/`che` wrappers.

That is consistent with a portable qualifier/state card under register
rendering. It is not evidence for DRY or any other material quality.

Best provisional class:

```text
CTHY_CARD ≈ QUALIFIED / PREPARED / PROPERTY STATE
```

Working confidence: `.25` for a qualifier, below `.10` for any specific state.

### qokaiin exact card — `b5fcea1e...`

Nine events occur on f55v, f81v, f82r and f83r. Seven are field-first. The two
exceptions are the f82r boundary pair and one position inside a long open
field. Its nine right neighbours are all different, while its left context is
limited to field entry or two local predecessors. This is the strongest
function-word-like bottleneck in the fixed panel:

```text
restricted left/entry ecology + highly diverse continuation
```

The exact card is visible once as unwrapped `okaiin`, so the entry behavior is
not reducible to the visible `q` wrapper.

Best provisional class:

```text
QOKAIIN_CARD ≈ INSTRUCTION / ENTRY HEAD
possible upstream expansion class: TAKE / USE / ENTER / APPLY
```

Working confidence: `.46` for entry-head behavior and `.27` for a practical
instruction-head expansion. This is the strongest concrete word/function guess
in this candidate.

## The `Y–AIIN–Y` construction

The sole three-card exact formula crossing two fixed prose pages is:

```text
f10r.6  CHY  TAIIN  SHY
f83r.3  CHEY DAIIN  CHEY
```

The same latent cards occur despite different wrappers. The two environments
are informative in different ways.

### f83r.3

```text
OLKEEDY-CLOSE
|
QOTAL  CHKEEDY-CLOSE
|
CHEY  DAIIN  CHEY  LCHEDY-CLOSE
|
QOKAIIN  QOTAL  DAR
```

A parsimonious schematic parse is:

```text
[closed local state]
[QOTAL-associated closed cell]
[Y — AIIN — Y parameter cell, committed]
[ENTRY_HEAD + QOTAL + continuation]
```

`QOTAL` occurs on both sides of the parameter cell. The strongest story is
therefore not a three-word clause but a small parameter frame embedded between
two states of the same local item/card.

### f10r.6

```text
YCHEOR CTHY CHOR CTHAIIN QOCTHOLY DY  CHY TAIIN SHY
```

The repeated triple is at the tail of one long open Herbal field, but another
exact Y card immediately precedes it. The local tail is therefore:

```text
Y  Y — AIIN — Y
```

This is awkward for a clean `ITEM — EQUAL AMOUNT — ITEM` translation. It is
still compatible with a typed or paired parameter formula, with the first Y
belonging to the preceding construction. There is no formal boundary proving
that segmentation.

Revised interpretation:

```text
Y–AIIN–Y ≈ PAIRED/TYPED PARAMETER FRAME
equal/shared amount = one possible expansion, not the default conclusion
```

Working confidence: `.34` for a reusable parameter construction, `.12` for
specifically “equal amounts/of each”.

## Closure is real; semantic closer types are not yet real

The major close-bearing exact cards do not each select a narrow field shape:

| close-bearing card | occurrences | observed field lengths | pages |
|---|---:|---|---|
| `bc4f1f5c...` (`shedy` family) | 12 | 1–6 | f81v, f82r, f83r |
| `7d25241b...` (`qokeedy`) | 10 | 1–4 | f82r, f83r |
| `7db18b2f...` (`qokedy`) | 8 | 1–4 | f81v, f83r |
| `de7321bf...` (`lchedy`) | 8 | 1–4 | f82r, f83r |
| `259b2b3b...` (`chedy` family) | 4 | 1 and 8 | f81v, f82r, f83r |

The common `bc4f...` close follows L/O four times but also occurs as a singleton
three times and after many unrelated cards. `qokeedy` is a singleton in five
of ten fields. This does not support a neat table such as:

```text
SHEDY = RESULT CLOSE
QOKEEDY = ACTION CLOSE
LCHEDY = ARGUMENT CLOSE
```

The better model is:

```text
close-bearing exact card = local payload/card identity fused with COMMIT
```

The DY/B3 coordinate can still be a commitment/termination feature, while the
whole close-bearing card retains lexical or form content. This respects the
failure of PAGE_HOST/coordinate free recombination and prevents punctuation
from swallowing the payload.

## The f82r carry and line reflow

The exact transition is:

```text
f82r.3  QOKALY SOLKAIIN CHCKHY QOKAIIN
f82r.4  QOKAIIN OCTHEOL CHKEEY LDY-CLOSE | ...
```

Under the literal surface parse, `qokaiin` ends one open field and immediately
begins the next line. Under the proposed logical parse, the first copy is an
anticipatory/carry copy of the next field head:

```text
f82r.3 logical end: QOKALY SOLKAIIN CHCKHY
carry display:       QOKAIIN
f82r.4 logical field: QOKAIIN OCTHEOL CHKEEY LDY-CLOSE
```

This turns the sole field-final occurrence of qokaiin into another entry head
and gives the next line a conventional `HEAD + arguments + close` form. It is
the most coherent parse, but only one transition exhibits it. Accidental
dittography and ordinary lexical repetition remain viable.

Crucially, the logical statement is not equated with the physical line. A line
can terminate during a statement, after the first visible group of the next
cell, or because the pre-drawn image has exhausted the available width.

## Explicit page and record parses

These parses use anonymous classes. `H` = possible entry head, `R` = possible
link, `P` = parameter, `U` = unit/reference, `Q` = qualifier, `C` = attached
commit, and `x` = unknown exact card. Square brackets are formal fields, not
sentences.

### f10r — two open dossier modules

```text
R1
  .2 [x x x x x x x x P x]
  .5 [x x R Q]

R2
  .6 [x Q x x x U  U P U]
  .8 [x x x R x R P x]
  .9 [x x x U x U x]
```

All five lines are open. Repeated R, Q, P and U cards make the page look like
a compact dossier written in continuous mode. `.6` supplies the cross-register
paired parameter frame. A plant picture can silently provide the principal
subject throughout R1/R2.

Water is allowed here in three distinct ways without assigning a WATER card:

1. the pictured plant may imply a wet habitat;
2. an unknown `x` card may name water as preparation medium;
3. a link card may connect the silent plant to an unknown liquid card.

The page does not license `AROL`, `OL`, L/O or CTHY as WATER.

### f11r — mostly open dossier with one early commitment

```text
R1
  .1 [x x x x x x x-C] [x]
  .4 [x U x U P]
  .7 [x x Q U]
```

The single early commitment does not change the rest of the page into Bio-like
cell notation. The shared U/P/Q deck is sufficient to relate it formally to
f10r and later Bio material.

### f55v — the Herbal/B bridge

```text
R1
  .5 [H P x x x-C] [P x x-C]
  .11 [x x x x-C] [P x x x U x]
```

Three of four fields close. An entry-head candidate begins the record, and the
portable parameter card begins the second field. This is the strongest single
page for a medical-form interpretation: it is still picture-addressed Herbal,
but it uses the B commitment mode later dominant in Biological pages.

### f56r — open Herbal dossier

```text
R1
  .5  [x x x P]
  .7  [x x x x x]
  .8  [x x x x-C]
  .12 [x x x x]
  .13 [x x x]
  .18 [x x x x]
  .19 [x x P]
```

This is the cleanest counterexample to “Currier B morphology always means
closed technical cells”: only one of seven fields commits. It argues for a
layout/register template on top of content, not for one closure per statement.

### f81v — closed configuration record plus open tails

```text
.2  [x-C] [H x x x R x x x R x x]
.7  [x R x P x P x-C] [R]
.17 [x-C] [U R x-C] [x-C] [x x x x]
.18 [x-C] [U R x R x-C] [x-C] [x-C] [x x]
.21 [x x x-C] [x-C] [x x x R x]
.24 [x x-C] [x x R x-C] [x x x-C] [x]
.27 [x x x-C] [x-C] [x x-C] [x]
```

The long `.2` field begins with the unwrapped exact qokaiin head after a
singleton closed cell. `.18` contains the clearest `X R Y R CLOSE` frame. Every
physical line ends with an open tail or singleton after a series of committed
cells, suggesting a line stencil of checked entries followed by continuation,
not independent sentences.

### f82r — dense record with one carried head

```text
.2  [x-C] [x-C] [x U x-C] [x x x]
.3  [x x-C] [x x x H]
.4  [H x x x-C] [x x x x]
.7  [x-C] [x x x-C] [x-C] [x x x x]
.19 [x x x x-C] [x]
.23 [x x x x P U x-C] [x-C] [x]
.26 [x x-C] [x x x P x H x]
.27 [x-C] [x x-C] [x-C] [x-C] [x-C] [x-C] [x-C]
```

The `.3/.4` boundary is the carry candidate. `.27` is a pure seven-cell row,
showing that the system can reduce to a checklist/catalogue line when the
local diagram or record demands it.

### f83r — structured main records followed by open notes

Record-level commitment rates are:

```text
R1 31/38 fields closed
R2 16/20 fields closed
R3  2/5  fields closed
R4  0/2  fields closed
```

R1 contains every qokaiin occurrence on the page and all four CTHY occurrences.
It also contains the closed `Y–AIIN–Y` cell. R2 remains strongly committed but
loses the entry head. R3/R4 become short open sequences.

A coherent nonsemantic parse is:

```text
R1  principal checked configuration/procedure
R2  continuation or second checked configuration
R3  mixed short appendix
R4  open gloss/summary
```

This warns against treating “Biological” as one uniform record syntax. The page
itself alternates closed form and open note modes.

## The circle pages

### f67r2

```text
PAGE := nested circular selector
        seven-member local set
        twelve-member moon-associated local set
        central/local elements
```

The safest use is a lookup/classification wheel. It can belong in a practical
medical-astrological miscellany, but the seven and twelve inventories are local
namespaces, not decoded planets or zodiac labels.

### f68r1

```text
PAGE := one central labelled star + 28 noncentral labelled stars
```

This is a spatial catalogue. No authorial 28-member cyclic order is established.
Its function can be celestial naming, mnemonic indexing or lookup without being
the same table as f69v.

### f69v

```text
PAGE := 28 ordered radial entries
        strict LONG / SHORT / LONG / SHORT ... alternation
```

This is the strongest actual schedule/table topology among the three. The
alternation is visual and has no reliable text marker. It may encode alternating
entry ownership, alternating table states or simply a legibility layout.

### Can Astro join the medical theory?

Yes at codex and workshop level:

- late-medieval medical miscellanies commonly admit astrology/prognostics;
- circle arrays are compatible with practical lookup;
- the same workshop can apply one graphic repertoire to independent registers.

No at card or referential level:

- these pages lack GDT327 joint tuples;
- no cross-register pointer joins a plant, Bio configuration and circle slot;
- 7/12/28/29 cardinalities are not culturally or semantically unique;
- f68r1 and f69v do not supply one proven common order.

Therefore the leading synthesis is:

```text
medical-practical Herbal/Bio ecology
+ independently useful astronomical/astrological annex
+ shared workshop notation habits
```

not:

```text
each plant/treatment record points to one decoded astronomical schedule
```

## Historical fit

The theory requires no unprecedented mixture of subjects. The British Library
catalogue describes Harley MS 2558 as a composite of botanical, surgical,
medical, magical, astrological and prognostic texts, assembled with additions
by a fifteenth-century physician:

- <https://searcharchives.bl.uk/catalog/040-002032705>

Harley MS 2375 combines fifteenth-century medical recipes, explicit `Recipe`
and `ana` prescription formulas, and an *Astrologia medicorum*:

- <https://searcharchives.bl.uk/catalog/040-002048206>

A corpus study of Latin and Middle English plague tracts found that recurrent
abbreviations with at least three occurrences were dominated by recipe-formula
items such as drachm, *ana*, *recipe*, half and ounce. That supports the modest
claim that a small recurrent formula deck can dominate abbreviated practical
writing without making every surface group a word:

- <https://academic.oup.com/dsh/article/37/3/765/6401180>

These parallels support genre and mechanism only. They do not identify the
Voynich language, region, donor text or expansion of any card.

## A learnable 1420 workshop protocol

The mature system need only teach four things:

1. **Common formula strip** — perhaps a few dozen high-frequency cards such as
   the entry head, link, parameter, generic unit and state qualifier.
2. **Two documentary modes** — open dossier mode and committed cell mode.
3. **Register sheets** — plant descriptors, bath/apparatus terms and local
   circle labels copied as whole cards from exemplars.
4. **Hand habits** — wrapper variants, joining, line-entry `s`, post-close `q`
   and reflow around an already drawn image.

The large rare inventory is not all memorized. Rare cards are copied from a
master, a glossary or a prior leaf. Frequent formula cards become abbreviated
and graphically regular through use. This naturally yields:

- common cards across hands;
- many rare register-local cards;
- wrapper allography;
- fossilized or opaque internal pieces;
- exact recurring formulas but few long repeated sequences;
- scribes who can reproduce the notation with only partial source-language
  expansion knowledge.

## Best current tentative expansion table

| exact form/construction | tentative source-function class | confidence |
|---|---|---:|
| qokaiin card | instruction/entry head; possibly TAKE/USE/ENTER/APPLY | .46 formal / .27 lexical class |
| L/O card | link, co-member or broad relation | .39 formal |
| AIIN card | parameter/amount/degree/index/reference | .28 |
| CTHY card | qualifier/prepared/property state | .25 |
| Y card | generic item/unit/reference slot | .21 |
| Y–AIIN–Y | paired or typed parameter frame | .34 constructional |
| Y–AIIN–Y | equal amount / “of each” specifically | .12 |
| attached DY/B3 | local commit/termination behavior | .78 formal only |
| repeated qokaiin at f82r.3/.4 | one carried logical entry head | .52 local parse |

No sound value is proposed. None of the uppercase paraphrases is a translation.

## Representative speculative expansions

### f55v.5

Surface:

```text
QOKAIIN CHAIIN YKAIN YKAN ODY-CLOSE | DAIIN CHEDY TALAM-CLOSE
```

Schematic:

```text
[INSTRUCTION_HEAD PARAMETER x x x-COMMIT]
[PARAMETER x x-COMMIT]
```

Free paraphrase, deliberately nonlexical:

> For the pictured simple, enter/use the following parameterized item and
> commit it; enter the associated value/preparation and commit that cell.

### f81v.18 field 2

Surface:

```text
CHEY OL CHEKY OL SHEDY-CLOSE
```

Schematic:

```text
[ITEM LINK ITEM LINK x-COMMIT]
```

Free paraphrase:

> Combine or relate two local items/states under the same closed configuration.

### f83r.3

Schematic:

```text
[state-C] [QOTAL state-C] [U P U state-C] [HEAD QOTAL x]
```

Free paraphrase:

> A local item QOTAL is assigned a paired/typed parameter, then re-enters the
> next instruction/configuration under the record head.

These paraphrases are coherence tests. They should be discarded if new fixed
page evidence makes the card placements incompatible.

## Awkward observations

1. The exact card vocabulary is large; a pure learned nomenclator would burden
   trainees. The common-formula-plus-copied-local-glossary solution is plausible
   but unproved.
2. The same field shape often accepts almost entirely different cards. That is
   expected for a form, but it leaves content identities ungrounded.
3. Major close-bearing cards accept very different field lengths, weakening a
   neat typed-closure dictionary.
4. AIIN is too positionally flexible to be confidently numerical.
5. Y repeats heavily and can be adjacent to itself. A simple “unit” expansion
   may be wrong.
6. The f82r carry is unique among 46 same-record line transitions. It could be
   dittography rather than a taught rule.
7. f83r changes from dense closed records to open records on the same page.
   The change may be spatial/page-layout reflow rather than a semantic change.
8. No fixed-page evidence links a particular plant feature, water, vessel,
   conduit, figure or star to one exact card.
9. Astro integration remains a genre story rather than a formal bridge.

## Leading adversarial alternative

If the practical medical reading breaks, the strongest alternative is an
**image-indexed concordance or teaching pattern register**:

- plant, apparatus and circle pictures provide categories or mnemonic prompts;
- exact cards are exemplar identifiers rather than abbreviated source words;
- long A fields and short B cells are two exercise/index templates;
- qokaiin is a section-entry control rather than an action head;
- L/O and Y are generic construction fillers;
- Astro is not an annex but the clearest expression of the lookup method.

This alternative explains the formal apparatus and the absence of long phrase
reuse. It loses on historical/content economy: a lavish illustrated codex with
plant simples, bath-like configurations and astronomical arrays is more easily
understood as a practical miscellany than as a pure formal exercise book.

## Novel predictions inside the already fixed pages

These were not used to select the theory and can be checked without adding
folios.

1. **Head prediction:** after treating the f82r boundary duplication as one
   state, qokaiin realizations should overwhelmingly introduce a new logical
   field or subfield and should have higher right-context diversity than
   matched cards of the same frequency.
2. **Link prediction:** L/O occurrences should sit between structurally more
   similar left/right local constituents than frequency-matched interior cards;
   `f81v.18` is the clearest positive, not the training definition.
3. **Parameter prediction:** occurrences of AIIN in committed Bio cells should
   be more often surrounded by generic unit/reference cards than matched
   interior cards, while remaining free of direct closure.
4. **Paired-frame prediction:** the two `Y–AIIN–Y` occurrences should belong to
   parameter-bearing local modules, but their pictured owners need not match.
   Failure would close the equal/shared-value gloss while preserving exact
   formula reuse.
5. **Closure prediction:** factoring out DY/B3 should not produce clean semantic
   closer classes; exact close-bearing card identity should still retain local
   payload dependence.
6. **Mode prediction:** within f83r, the disappearance of qokaiin and CTHY after
   R1 should track the closed-form-to-open-note transition better than physical
   line length alone.
7. **Water prediction:** no common portable card should be required on every
   visually water-relevant Herbal/Bio item. Water can be a rare content card or
   silent medium; the hypothesis specifically rejects a universal OL/AROL
   water token.
8. **Astro prediction:** the three circle pages may share visual organization
   principles but should not yield a forced one-to-one surface label dictionary
   across 7/12/28/29 inventories.

## Verdict

The exemplar-coded register survives, but its best coherent specialization is
now:

```text
FORMULA-CARD PRACTICAL MEDICAL REGISTER
WITH SILENT PICTURE ADDRESS,
OPEN A DOSSIER MODE,
COMMITTED B CELL MODE,
AND A SEPARATE LOOKUP ANNEX
```

The highest-value concrete lead is not `AIIN = number`. It is the joint system:

```text
qokaiin-like entry head
+ L/O-like relational link
+ AIIN/Y parameter frame
+ payload-bearing committed close
```

That small grammar explains f55v as the Herbal/B bridge, the closed Bio
stencils, the f82r carry, the f83r parameter cell, free/bound renderer variants,
line reflow, and multi-scribe learnability without pretending that a physical
line is a sentence. Astro fits the codex ecology but is not yet part of the same
demonstrated card grammar.
