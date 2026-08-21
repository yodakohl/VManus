# Candidate evolution: abbreviated natural language under a workshop renderer

Updated: 2026-08-21

Status: **independent speculative sidequest candidate, not a GDT result and not
a translation**. This branch was developed blind from only
`VOYNICH_CURRENT_ROUTE.md` and `SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`, plus
external historical literature. It did not inspect the long sidequest archive,
the translation draft, candidate files, the active ledger, or another agent's
work.

## Constraints held fixed

- Fixed pages only: Herbal `f10r`, `f11r`, `f55v`, `f56r`; Biological `f81v`,
  `f82r`, `f83r`; circle/astronomical `f67r2`, `f68r1`, `f69v`.
- `f84` and `f84r` remain sealed and were not accessed.
- ZL3b, IT2a and RF1b are alternate readings of one manuscript.
- Exact card identities remain opaque. They are not assumed to be words,
  lexemes, morphemes, sounds or meanings.
- GDT003's failure to beat strong character/string baselines prevents treating
  regular transformations as demonstrated linguistic morphology.
- No GDT327 tuple or event is imported into the three circle pages.
- Confirmed English lexemes: **0**. Confirmed plaintext clauses: **0**.
- A route duplicate screen returned the already rejected direct abbreviation
  decoder (GDT207), the exploratory abbreviation-heavy residual lead (GDT276),
  and failed control transport (GDT347). Therefore this is not a Cappelli lookup
  or direct abbreviation decoder. It is a generative architecture with
  falsifiable role hypotheses.

## Executive claim

The best evolution is a **three-layer abbreviated natural-language system**:

1. a practitioner first reduces ordinary multilingual or vernacular technical
   prose to an elliptical record, omitting what the picture, page register and
   routine already supply;
2. recurrent content words, relation words, quantities and technical states are
   copied as learned or locally invented abbreviations, some of them radically
   homographic;
3. a workshop renderer adds entry/link wrappers, joins or spaces packets, and
   marks resolved fields according to hand and register.

This is a hybrid notation, but its payload need not be a codebook detached from
language. The proposed payload is **compressed language with typed shorthand
slots**. An exact card is the safest observable unit of the shorthand ledger,
while a visible Voynich group is its context-shaped rendering. Neither need
equal one source word: a card may abbreviate a word, a recurrent phrase, a
measure-plus-number bundle, or a conventional relation.

The important shift is from:

```text
ordinary prose -> encrypted words
```

to:

```text
ordinary technical utterance
    -> pragmatic ellipsis (picture and register supply arguments)
    -> abbreviated lexical/quantitative packets
    -> exact workshop cards
    -> hand/register wrapper + joining + close
    -> visible groups fitted around the drawing
```

This model explains why natural-language meaning could survive while lexical
stems are difficult to recover: abbreviation, omitted arguments, phrase-level
cards and renderer variation all intervene before the surface string.

## Historical mechanism, not historical identification

The architecture uses ordinary medieval practices in an unusually dense local
combination.

- Medieval abbreviation included suspension, contraction, superscript letters
  and special signs. Its rules were flexible across scribes and texts, and
  context was often needed to supply omitted letters. The Library of Congress
  overview also notes that study texts tended to be more heavily abbreviated
  than texts intended for oral delivery. This supports context-dependent
  expansion, not any Voynich glyph equation.
- Medical recipes could mix full words, abbreviations and special symbols for
  measures. A single measure could have many graphic forms, while one form
  could be ambiguous between measures. This is a close historical mechanism
  for typed but homographic packets.
- Recipe ingredients could be laid out one per line, and an opaque abbreviation
  could remain ambiguous even to a modern editor without its measurement
  context. Layout therefore can carry grammatical information that running
  prose normally makes explicit.
- Fifteenth-century practical miscellanies combined medicine, craft knowledge,
  agriculture and prognostication; they were repositories assembled for use,
  and some were written in informal hands by household compilers. A mixed
  workshop book is historically normal even if its exact notation is not.
- Practical pharmacological books included simple-drug entries, recipe lists,
  synonym glossaries, substitutions, weights and measures, and daily-use
  manuals associated with practitioners, apothecaries or institutions.
  Multilingual synonym transmission and transliteration make a shallow
  one-language decipherment especially unsafe.
- A fifteenth-century practitioner's surgical book could combine limited Latin,
  vernacular writing, learned surgery and experiential knowledge. The relevant
  social unit is therefore not necessarily a university-trained cryptographer;
  it can be a mixed-literacy practitioner workshop.
- Late-medieval astronomical compilations combined treatises, tables, diagrams
  and paper instruments, sometimes with local calculations added for particular
  cities. This supports diagram-specific compact namespaces, not transfer of a
  prose dictionary into Astro.

No cited comparator contains the Voynich system. The claim is only that every
operation in the proposed production chain was available around the fifteenth
century.

## Concrete generative system

### Stage 1: source utterance

The source can be ordinary technical language, possibly with conventional
Latin recipe vocabulary embedded in a vernacular or multilingual environment.
A full source utterance might schematically contain:

```text
[shown subject] + [take/use/consider] + ENTITY + RELATION + VALUE/AMOUNT
                + STATE/OPERATION + TARGET/TIME + completion
```

### Stage 2: register ellipsis

The compiler deletes predictable material:

- Herbal: plant subject is supplied by the picture; repeated “this plant” and
  perhaps “is/has/use” can vanish.
- Biological: pictured figure, vessel, conduit or bath supplies the site and
  apparatus; repeated imperatives and body/application context can vanish.
- Astro: ring, radial position and sequence supply coordinate type and order;
  labels need only distinguish values within a local array.

The remainder is not a sentence. It is a sequence of content-bearing and
relation-bearing slots.

### Stage 3: abbreviation ledger

The workshop maps recurrent remnants to cards. Four types are plausible:

```text
LEX       abbreviated lexical head or phrase
REL       common relation, conjunction or construction frame
VAL       number, degree, amount, index or other parameter
STATE     prepared/qualified/conditioned state
```

Cards are exact learned exemplars. Their internal characters may preserve a
source stem, but that is not assumed. Some could be logographic abbreviations;
some could preserve only initial/final material; some could package multiple
source tokens. Thus exact-card identity and natural language are compatible
without exact-card-equals-word.

### Stage 4: renderer

```text
SURFACE_GROUP := ENTRY/LINK_WRAPPER + CARD_REALIZATION + optional JOIN
FIELD_END     := licensed attached close, or open continuation
```

Wrappers such as the surfaces represented by `d`, `s`, `q`, `ch`, `sh` are
treated primarily as entry/link/pen-state behavior. They can resemble letters
without being pronounced prefixes. This directly accommodates exact collapse
of `AIIN / DAIIN / SAIIN / CHAIIN / TAIIN`, the free Y family, `CHOL / OL`,
and CTHY variants.

The system is learned by copying exemplars, not by applying a general cipher:

```text
common abbreviation ledger
  + register template
  + hand-specific wrapper/close habits
  + page-local rare expansions
```

That predicts both shared exact cards and the strong B/biological closure skew.

## Confidence-ranked candidate meanings and parses

These are bold search hypotheses. Probabilities are judgments, not measured
posteriors, and alternatives within a row compete.

### 1. AIIN is a value/amount/index packet — 0.31

**Preferred parse:** AIIN is a compact scalar complement: amount, ratio,
degree, count or indexed value. It is not necessarily a numeral itself; it may
stand for a measure-plus-value phrase such as “one portion”, “of the stated
degree”, or a locally numbered class.

Why it fits: it occurs on all seven prose pages, mostly internally, can appear
first or last, and avoids an immediate attached close in all 15 observed
opportunities. A value packet naturally combines with surrounding type and
relation packets and need not close the field by itself. The repeated minims
may be a deliberately number-like realization, but this is only suggestive.

**Alternative:** an extremely common abbreviated complement such as a medium
or preparation basis. Reject any single noun unless it predicts contexts beyond
frequency.

### 2. Y is a frame/deictic card — 0.25

**Preferred parse:** Y means something in the family “the stated/same/this
type”, or is a typed slot marker selecting how its neighbour is to be read. It
may be grammatical shorthand rather than a content word.

Why it fits: it is portable, mostly medial, and participates twice in the only
cross-page longer exact path. Its many surface wrappers are better explained by
entry/link state than by six related lexical forms.

**Alternative:** a very common relation such as “of/for”. This is possible but
weaker because no agreement or stable surface prefix pattern has been shown.

### 3. `Y -> AIIN -> Y` is a bounded parameter frame — 0.22

**Preferred schematic expansion:**

```text
[PARAMETER/TYPE] [VALUE OR DEGREE] [QUALIFIER/RETURN-TO-FRAME]
```

Natural-language paraphrase: **“as to X: value V, of the stated kind”**. On the
Herbal occurrence it is a field tail; on the Biological occurrence it is a
field head followed by a close. That mobility fits a reusable abbreviated
attribute, not a complete proposition.

**Alternative A:** “of [amount] of”, a relation–quantity–relation phrase.

**Alternative B:** an anaphoric template, “the same [value] likewise”.

No option licenses translating any of the three cards individually.

### 4. L/O is a relation or ingredient-link packet — 0.19

**Preferred parse:** a broad connective such as WITH / IN / OF / FROM, or a
technical “medium/base” relation. Its 19 events on only three pages suggest a
common local construction rather than a universal noun.

Why it fits: medial placement dominates and a close follows in 5/17
opportunities. Herbal `CHOL` and Biological `OL` collapsing to one exact card
fits a wrapper plus a stable relational kernel.

**Alternative:** a high-frequency material class (liquid, oil, base). This must
remain below the relation hypothesis because earlier WATER/HOT readings were
withdrawn and no independent pictured owner is available.

### 5. CTHY is a prepared-state or quality packet — 0.17

**Preferred parse:** “prepared/conditioned in manner X”, or a generic quality
slot whose exact expansion depends on register. Its overwhelmingly medial
placement and Herbal/Biological portability suit a modifier.

**Alternatives:** temperature class, consistency, potency, maturity, or
application state. **DRY is not revived**; there is no basis for choosing one
quality.

### 6. Attached closures mark resolution of a shorthand cell — 0.38

**Preferred parse:** the close says “this abbreviated entry is complete or
resolved here”, comparable in function to punctuation, a terminal abbreviation
sign, or a checked form cell. It is metadata on a field, not a spoken word.

The B renderer's high closure rate and Biological short-cell layout then arise
from a form-filling convention. An open Herbal field can continue as a long
attribute list; a Bio cell is usually explicitly committed. Free DY remains
ordinary wrapper-plus-Y and is not the close.

**Alternative:** closure packages an omitted repeated verb (“take/apply/mix”).
This is linguistically attractive but less likely because closer identity is
strongly local and f55v transfers the B habit more readily than exact closers.

### 7. `qokaiin` is a carried lexical/parameter head — 0.29

**Preferred parse:** the same ingredient, apparatus parameter, operation head
or local topic is repeated at the line boundary because the record reflows. The
first occurrence announces or ends with the item; the next reactivates it before
additional specification.

This is analogous to repeating a headword or ditto-bearing parameter, but the
surface word itself does **not** mean RESUME. The `q` at the new position may be
the licensed post-close/link renderer state rather than semantic “next”.

**Alternative:** scribal catch/repetition caused by copying or planning. With
only one exact boundary repeat among 46 transitions, accidental or emphatic
repetition remains a serious rival.

### 8. Repeated Bio stencils are elliptical recipes or settings — 0.27

**Preferred parse of `1C | 3C | 1C | 4O`:** four typed microentries, roughly

```text
[SITE/ITEM + setting]C | [ingredients/values]C |
[state/result]C | [continuing qualification]O
```

Eight of nine cards changing while the three-card field retains the same exact
`shedy` closer is exactly what a copied form with variable abbreviated values
predicts. It is weaker evidence for a repeated prose sentence, because lexical
identity largely varies.

**Alternative:** an inspection/checklist record rather than a recipe. The
architecture cannot yet distinguish instruction, observation and inventory.

### 9. Herbal rows are abbreviated dossier attributes — 0.24

**Preferred parse:** the picture silently supplies the simple; each long open
field lists one or more of name/synonym, classification, quality/degree,
habitat, preparation medium and use. A schematic line is:

```text
[silent THIS SIMPLE] [attribute frame] [relation] [value/state] ...
```

The recurring 4O and 5O patterns are comparable to fixed-width dossier entries
whose lexical fillings differ. They do not require rigid
description-then-recipe order.

**Alternative:** recipe clauses with repeatedly omitted “take/use”. This is
possible, especially for f55v, but line openness and long fields favor attribute
bundles over a chain of independently closed operations.

### 10. Astro consists of local abbreviated table labels — 0.20

**Preferred parse:** the circle pages use natural-language abbreviations,
proper-name contractions, numerals and/or technical symbols as labels in three
separate local namespaces. Geometry supplies the relation: ring membership,
radial address, or ordered schedule position. Thus a short label can carry less
language than a prose card while still belonging to the same workshop.

- `f67r2`: selector/class labels for layers or compartments;
- `f68r1`: catalogue labels attached to one centre and 28 noncentral stars;
- `f69v`: value/state labels in an ordered alternating 28-entry schedule.

No shared prose identity is asserted. No authorial cyclic order is invented for
f68r1, and the failed direct A-65 transfer stays closed.

## Integrated page reading

The safest commonality is a **shared compression practice**, not necessarily a
single WHAT/HOW/WHEN doctrine.

| Register | Silent information | Written residue under this model |
|---|---|---|
| Herbal | pictured plant/simple | abbreviated attributes, relations, values, preparation/use hints |
| Biological | figure, vessel, conduit, bath/site | short configured cells: item/site, setting, state, qualification |
| Astro | ring, radial position, sequence | local labels, indices, classes or values |

The WHAT/HOW/WHEN integration remains possible: Herbal identifies materia,
Biological configures application, Astro selects time or celestial condition.
But the abbreviation model does not require it. A heterogeneous practical
miscellany held together by one workshop notation is historically safer.

## Why this can hide lexical stems

Four losses can accumulate:

1. **Ellipsis:** pictured subjects, repeated verbs and coordinate types vanish.
2. **Brachygraphy:** a word or phrase retains only selected letters or a special
   sign; the same abbreviation can require context to expand.
3. **Packetization:** a measure-plus-value or relation phrase becomes one copied
   card, while one source word could be split across cards.
4. **Rendering:** entry/link wrappers and joining alter the visible group.

Therefore a failed search for ordinary word forms does not decide against
natural language. Conversely, historical abbreviation does not rescue an
arbitrary plaintext: expansions multiply rapidly, and without external
constraints almost any short card can be made to fit many words.

## Awkward facts and failure modes

1. Voynich groups are often not visibly shorter than plausible source words.
   The model must earn “compression” from omitted clauses and phrase-level
   packets, not merely character count.
2. Exact cards may simply be formal code states. Nothing yet proves that any
   card preserves letters from a source language.
3. The exact collapse of many prefixed surfaces is more radical than ordinary
   scribal abbreviation. It requires a renderer layer; Cappelli-style expansion
   alone is inadequate.
4. Medieval abbreviation marks were normally interpretable by an initiated
   reader. A wholly local, exceptionally dense system needs a workshop or
   training explanation, not the claim that all manuscripts worked this way.
5. AIIN as quantity is tempting because of its minims, but its five first/last
   placements and absence of independent numerical anchors can refute a narrow
   numeral reading.
6. `Y -> AIIN -> Y` occurs only twice. It is a valuable formula but too sparse
   to establish a grammatical construction or shared referent.
7. Closures may reflect hand B's punctuation aesthetics rather than semantic
   cell resolution. The f55v bridge supports renderer ecology but does not
   prove the proposed function.
8. The unique `qokaiin` carry may be accident, emphasis or copy planning.
9. Biological imagery does not independently distinguish baths, applications,
   anatomy, apparatus or allegory. The cell grammar is stronger than the genre
   gloss.
10. Astro has no GDT327 coverage. Any apparent surface resemblance to prose can
    be paleographic coincidence, and no prose card mapping may cross the gate.
11. Multiple hands can explain renderer variation but also create false
    “grammar” through scribal habit. Hand, register and content are partially
    confounded.
12. GDT003 warns that transformation regularity can be captured by ordinary
    string statistics. A linguistic abbreviation hypothesis must predict
    external expansions or held structural behavior beyond those baselines.

## Discriminating predictions on the fixed pages

These predictions can sharpen or kill the model without opening another page.

1. **Typed-context prediction:** if AIIN is VAL-like, its neighboring exact
   cards should occupy narrower structural classes than frequency-matched
   portable cards, while the surface wrapper should add little after line/close
   context is known.
2. **Frame prediction:** in the two `Y-AIIN-Y` instances, surrounding fields
   should be compatible with the same slot type even though page genre and
   field position differ. A purely lexical phrase would instead predict more
   neighboring identity.
3. **Ellipsis prediction:** repeated Herbal 4O/5O stencils should preserve slot
   classes or closure expectations while exchanging content cards; exact word
   order need not repeat.
4. **Form prediction:** repeated Bio stencils should show lower variation in
   close identity and slot count than in interior card identity, as already
   suggested by the strongest pair.
5. **Carry prediction:** `qokaiin` should retain the same field role across the
   boundary, while its surface entry wrapper may change only when licensed by
   line/close state. If it instead changes structural role, catch/repetition is
   favored.
6. **Hand/register prediction:** f55v should pattern with Bio-B in wrapper and
   closure probability but with Herbal in long-field template. This interaction
   is more diagnostic than shared vocabulary alone.
7. **Homography prediction:** candidate expansions should be register-sensitive
   but type-consistent—for example, AIIN may realize different measures or
   degrees, but should not alternate freely among entity, action and value.
8. **Astro independence prediction:** within each circle page, label length or
   repeated surface class should correlate with local geometric role; the same
   mapping need not hold across the three pages. This must be tested only from
   frozen surface/topology.
9. **Compression prediction:** a reconstructed template should require fewer
   omitted source roles per record than a pure word-for-word decipherment, yet
   should not improve merely because it has more free semantic labels.
10. **External falsifier:** a blinded contemporary abbreviated technical corpus
    passed through the proposed ellipse/card/renderer interface should reproduce
    the key combination—portable packets, stencil stability, register-specific
    closure and boundary carry—better than matched ordinary diplomatic text and
    a nonlinguistic card generator. This must clear the existing GDT207/GDT347
    objections rather than relabel them.

## Ranked conclusions

1. **Most likely (0.42): abbreviated-language payload inside a typed workshop
   form system.** Natural language enters upstream, but the surviving observable
   units are elliptical abbreviation packets plus renderer states. This best
   reconciles portable exact cards, register forms, multiple hands and lost
   lexical stems.
2. **Second (0.31): primarily nonlinguistic technical codebook with only local
   language labels.** The current structural evidence cannot exclude this and
   may favor it if typed semantic predictions fail.
3. **Third (0.17): heavily abbreviated running natural language.** This is less
   likely because line/field templates, wrapper collapse and closure ecology
   require more than ordinary prose abbreviation.
4. **Residual (0.10): heterogeneous mechanisms by section or copying artifact.**
   Herbal, Bio and Astro may share production but not a single payload system.

Within the leading model, the most useful provisional assignments are:

```text
AIIN       VAL/amount/index complement          low-moderate confidence
Y          frame/deictic/type marker            low confidence
L/O        relation or medium-link              low confidence
CTHY       prepared-state/quality slot          low confidence
ATTACHED   field resolved/committed             moderate confidence
CLOSE
qokaiin    carried lexical/parameter head       low-moderate confidence
```

These are structural-semantic types, not translations. The next decisive gain
would be an independently constrained expansion class—especially measure,
degree, or repeated headword—not a guessed English noun.

## Sources

- Library of Congress, [Deciphering scribal abbreviations](https://guides.loc.gov/manuscript-facsimiles/deciphering-scribal-abbreviations): common abbreviation mechanisms, flexibility across scribes/texts, and contextual expansion.
- Adriano Cappelli via Universität Zürich, [Cappelli Online](https://www.adfontes.uzh.ch/en/ressourcen/abkuerzungen/cappelli-online): searchable historical reference corpus. It is cited as a mechanism inventory, not a Voynich key.
- Claire Burridge, [Note on Weights, Measures, and Their Symbols](https://www.ncbi.nlm.nih.gov/books/NBK608570/): full words, abbreviations, symbols, multiple realizations and ambiguity in medical recipes.
- Claire Burridge, [Recipe Transcriptions](https://www.ncbi.nlm.nih.gov/books/NBK608569/): line-listed ingredients and an unresolved abbreviation whose interpretation depends on measurement context.
- Melissa Reynolds, [“Here Is a Good Boke to Lerne”](https://doi.org/10.1017/jbr.2018.182): survey of 88 fifteenth-century practical manuscripts and the miscellany/repository model.
- Melissa Reynolds, [The *Sururgia* of Nicholas Neesbett](https://doi.org/10.1093/shm/hkaa099): a fifteenth-century practitioner combining vernacular, limited Latin, learned surgery and experiential exchange.
- Petros Bouras-Vallianatos, [Medieval Mediterranean Pharmacology](https://www.ncbi.nlm.nih.gov/books/NBK606146/pdf/Bookshelf_NBK606146.pdf): recipe collections, practical manuals, synonym glossaries, substitution lists, multilingual transliteration and weights/measures.
- Daniel Wakelin, [The Idea of the Remedy Collection](https://academic.oup.com/book/41401/chapter/352708437): one fifteenth-century manuscript combining arithmetic, recipes, astronomy, herbal, plague and surgery.
- University of Pennsylvania, [MS Codex 1881](https://bibliophilly.library.upenn.edu/viewer.php?id=Oversize+Ms.+Codex+1881): a late-fifteenth-century astronomical compilation with treatises, tables, diagrams, volvelles and local city calculations.
- Seb Falk, [Learning Medieval Astronomy through Tables](https://doi.org/10.1111/1600-0498.12114): tables as practical learning and computation in a late-medieval compilation.
