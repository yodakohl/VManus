# Candidate theory: exemplar-coded workshop register

Updated: 2026-08-21

Status: independent YOLO theory candidate. This is deliberately abductive and
may propose meanings. It is **not** a GDT result, decipherment, or translation.

Input discipline: developed only from `VOYNICH_CURRENT_ROUTE.md`,
`SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`, and the historical sources linked
below. The long sidequest archive, translation draft, active ledger, other
candidate theories, and all f84/f84r material were not consulted.

Fixed target pages:

- Herbal: `f10r`, `f11r`, `f55v`, `f56r`;
- Biological: `f81v`, `f82r`, `f83r`;
- circle/astronomical: `f67r2`, `f68r1`, `f69v`.

## Confidence-ranked conclusion

1. **Leading theory (0.62, architectural only):** the seven prose pages are
   written in an exemplar-coded practical register. A visible group is usually
   the rendered form of a learned formula card, not a letter-by-letter cipher
   word. Common cards express reusable record relations; pictures and local
   register cards carry much of the content. Different scribes share the card
   values and field stencils but render licensed cards with somewhat different
   entry wrappers and closure habits.
2. **Content model (0.40):** Herbal records identify or qualify the pictured
   simple; Biological records instantiate short apparatus/application/bath
   cells. The shared deck supplies relations, values, comparison and state;
   Bio adds a larger technical result/closure deck.
3. **Specific semantic lead (0.24):** `Y -> AIIN -> Y` may be an equal-value or
   same-measure frame, functionally comparable to recipe `ana` ("of each/the
   same amount"), not necessarily the word *ana* or even Latin.
4. **Integrated WHAT/HOW/WHEN manual (0.18):** the Herbal, Biological and
   circle pages may be complementary substance, procedure and timing tools.
   A looser practical miscellany remains more likely because no explicit
   cross-section pointer is established.

The novel step beyond the current base is to treat the system as a
**compressed exemplar register**: scribes copy formula-bearing cards from a
shared stock, while pictures and table geometry replace repeated nouns and
arguments. “Ledger” need not mean a lost physical table; it may have been a
memorized repertory plus model sheets.

## Why a workshop could learn it around 1420

The learner does not memorize 1,676 arbitrary meanings. The ten-page evidence
is compatible with a much smaller active curriculum:

1. learn the common card silhouettes and their permitted exact cells;
2. learn a few register stencils (open Herbal row; closed Bio cell sequence;
   local circle-label array);
3. copy rare technical cards from an exemplar rather than deriving them;
4. select a hand-appropriate entry allograph (`s`, `q`, or unwrapped) only
   after the card has been chosen;
5. close a Bio field with one licensed terminal card when its local entry is
   resolved;
6. repeat the boundary card when a record is physically reflowed and the next
   line needs a pickup cue.

This is simple enough for a small workshop: semantic choice is local and
template-driven; the difficult rare inventory stays in exemplars. The exact
joint card remains the authoritative unit. Wrapper pieces are scribal
realizations, not a freely generative alphabet.

## Executable writing procedure

The following procedure is concrete enough to generate the observed kind of
page without requiring a modern cipher machine.

### Encoder used by a scribe

```text
INPUT: drawing D, practical source note N, register R, hand H, available space

1. ADDRESS := the already drawn plant/object/ring position.
   Omit its full noun whenever ADDRESS makes it recoverable.

2. Select the register form:
      Herbal -> one mainly open descriptive/preparative field per line packet
      Bio    -> sequence of short resolved cells plus an optional open tail
      Astro  -> local label/value list owned by the diagram

3. Reduce N to cards from the shared exemplar stock:
      relation/class, item or unit, value/reference, property/state,
      register-local action/result/value.

4. Copy the cards in a licensed stencil. Do not derive an unknown card from
   its apparent letters.

5. If a cell is resolved, append its licensed DY/B3-bearing closer. The closer
   family may preserve the kind of resolution, not merely punctuation.

6. Render each already selected card with H's licensed wrapper/allograph:
      s is favored on physical-line entry;
      q is favored immediately after a closed cell;
      JOIN/SPACE follows the local exemplar and available space.

7. If the drawing forces a line break inside the record, optionally repeat the
   boundary card at the beginning of the next line as a pickup/re-entry cue.
```

### Decoder used by a workshop reader

```text
1. Identify the picture/table position and register before reading cards.
2. Normalize known wrapper realizations to their shared exact card.
3. Segment at source boundaries and licensed attached closers, not at every
   physical line ending.
4. Match the resulting card sequence to a familiar register stencil.
5. Fill the silent subject from the picture and repeated arguments from the
   current record/exemplar.
6. Expand only the cards whose values are known in that workshop; copy rare
   cards operationally if their spoken expansion is unnecessary.
```

This permits partial literacy: a copyist can reproduce a procedure correctly
without being able to expand every rare card into ordinary speech.

## Provisional card/function dictionary

These are deliberately risky hypotheses for iteration. `FORMAL` readings name
observable writing operations; `CONTENT` readings are possible expansions.

| item | proposed reading | type | confidence | reason / falsifier |
|---|---|---|---:|---|
| attached DY/B3-bearing terminal | `CELL RESOLVED / VALUE COMMITTED` | FORMAL | 0.78 | Bio has 85/115 closed fields, while free surface `DY` is an ordinary Y card. Multiple exact closers imply typed commitment rather than one period. Fails if the terminal families have no stable field ecology. |
| `s` wrapper | `physical-line pickup allograph` | FORMAL | 0.72 | Enriched at line entry; predicts no stable content difference after exact-card normalization. |
| `q` wrapper | `post-closure/new-cell entry allograph` | FORMAL | 0.72 | Enriched after attached closure; predicts constructional, not lexical, behavior. |
| AIIN card `2f1c5e56...` | `VALUE / AMOUNT / REFERENCE VALUE` | CONTENT | 0.37 | Portable across all seven prose pages and frequently interior. Fails if it clusters with subject/name rather than value opportunities. |
| Y card `b921a237...` | `ITEM-TYPE / UNIT / FRAME TAG` | CONTENT | 0.33 | Portable, accepts many wrappers, and flanks AIIN in the sole recurrent three-card formula. |
| `Y-AIIN-Y` | `EQUAL-PARTS / SAME-VALUE FRAME` | CONTENT/CONSTRUCTION | 0.24 | Formally symmetrical; medieval recipes use a stable `ana` abbreviation for equal amount. Only two occurrences, so a generic tagged-value frame is safer. |
| L/O card `dcda95c8...` | `OF / WITH / IN` relation, or broader class-link | CONTENT | 0.29 | Usually medial and participates in repeated `L/O -> Y`; exact Herbal CHOL and Bio OL identity rules out simple HOT/WATER readings. |
| CTHY card `e0b630cb...` | `PREPARED / QUALIFIED STATE` | CONTENT | 0.21 | Cross-register, almost always medial; “dry” is explicitly rejected. Could instead be an entirely abstract property class. |
| exact `qokaiin` card `b5fcea1e...` | `SAME DATUM / CARRY THIS VALUE` | CONTENT/EDITORIAL | 0.20 | Repeated at f82r.3 line end and f82r.4 line start inside one record. Fails if the duplication is ordinary dittography or if further pickups repeat arbitrary cards. |
| Bio-private OKE/OKEE/LCHE/E closer deck | `TECHNICAL RESULT/STATE CODES` | CONTENT CLASS | 0.18 | Many short Bio cells and position-pure terminal families. No individual action, body part or substance is assigned. |

The most useful risky equation is therefore:

```text
Y - AIIN - Y  ~=  ITEM/UNIT - SAME OR STATED VALUE - ITEM/UNIT
```

It is a *functional* expansion, not a phonetic reading. A plausible recipe
analogy is “of these, equal amount,” but the same formal frame in Bio could be
“two ports/settings share one value.” That portability is a virtue for a
technical card and a problem for a normal lexical phrase.

## Real ten-page parses under this theory

### f10r.6 Herbal

Observed field tail:

```text
CHY  TAIIN  SHY
 Y     AIIN   Y       (exact cards)
```

Best speculative expansion:

```text
[item/unit A] [same or stated amount] [item/unit B]
```

The wrappers `ch-t-sh` select written realizations; they are not translated.
The plant image silently supplies the dossier subject. An equally viable
weaker parse is `[tag] [value] [tag]`.

### f83r.3 Biological

Observed field head:

```text
CHEY  DAIIN  CHEY  -> LCHE-CLOSE
  Y     AIIN    Y       terminal state
```

Best speculative expansion:

```text
[two-place setting with shared value] -> [setting committed]
```

The same latent frame appears with `che-d-che` wrappers and a Bio closer. This
is more naturally one portable construction inserted into two register forms
than a phrase whose three visible prefixes each carry ordinary inflection.

### f10r.9, f55v.11 and f83r.38

```text
CHOR CHY | OR Y | OR CHEY
 L/O  Y    L/O Y   L/O Y       (exact paths)
```

Provisional expansion:

```text
[relation/class] [item/unit/type]
```

Possible ordinary paraphrases are “in/with [type]” or “of class [type].” The
cross-section recurrence is evidence for the construction, not for either
preposition.

### f81v.17 and f82r.7 Biological stencil

Both implement:

```text
1C | 3C | 1C | 4O
```

Eight of nine cards vary; the three-card cell retains the same exact `shedy`
closer. Workshop expansion:

```text
[resolved selector] |
[variable relation/value + typed resolved result] |
[resolved selector] |
[open explanatory or continuation tail]
```

This resembles filling two instances of the same form, not repeating a
sentence. The close tells the reader where an entry is complete even when the
physical line continues.

### f82r.3 -> f82r.4

```text
... qokaiin  /physical line/  qokaiin ...
```

Operational reading:

```text
... VALUE-X ; PICK UP VALUE-X ...
```

The reader collapses the duplicated boundary realization to one continuing
record value unless local syntax requires two. This is analogous in function
to a catchword or reprise, but it is not a quire catchword and must not be
called one historically.

## Why B closure and Bio stencils coexist

Two independent choices are needed:

```text
B hand/register habit  -> make local completion explicit
Bio document template  -> create many small fillable cells
```

This explains why f55v, a Herbal-B page, has 3/4 closed fields but does not
inherit the whole Bio closer vocabulary. The scribe learned the *practice* of
explicit closure from the B shelf; the Bio exemplar supplied the specific
technical closing cards. “Currier B = another language” is unnecessary.

Multiple terminal cards are predicted because the last card carries two jobs:

```text
LOCAL RESULT/STATE + THIS FIELD IS COMPLETE
```

If closure were only punctuation, one invariant terminator should dominate.
If it were only content, its extreme terminal placement would be accidental.
The fused two-job card explains both.

## Astro pages: why they can remain surface-only

The circle pages need not use the prose ledger at the same analytical level.
The workshop can have copied three local lookup sheets whose geometry provides
their slot identity:

- f67r2: separate 7-, 12-, and central selector vocabularies;
- f68r1: a central item plus 28 spatially owned star labels;
- f69v: 28 ordered entries with a strict LONG/SHORT visual alternation.

In this candidate theory an Astro group is a **local lookup entry**, perhaps a
name, day-state, prognostic code or table value. The prose joint-card parser is
not licensed there, so no prose meaning is projected onto these labels. The
fact that only surface `DY` is shared across the three displayed inventories
favors local code sheets over one universal astronomical dictionary.

Possible production sequence:

```text
copy/draw diagram -> allocate owned slots -> copy local label stock ->
alternate prescribed long/short realizations where the template requires it
```

The 28-fold f69v array may be a lunar schedule, but “lunar” is no more than a
genre-level guess; the weak lag-14 result and failed direct A-65 transfer argue
against importing a specific known table.

## Historical production analogues

These sources support mechanisms, not origin, language or plaintext.

1. Honkapohja et al., “Lexical and function words or language and text type?
   Abbreviation consistency in an aligned corpus of Latin and Middle English
   plague tracts,” *Digital Scholarship in the Humanities* 37.3 (2022),
   [article](https://academic.oup.com/dsh/article/37/3/765/6401180).
   Five scribes in six related manuscripts show that recipe abbreviations are
   substantially more consistent than abbreviations in running text. The
   stable items are formulaic recipe signs: `recipe`, dram, ounce, half, and
   especially `ana`, “the same amount.” The study also reports individual
   function-word abbreviation inventories and notes line justification, genre
   and chronology as conditioning factors. This is the closest real analogue
   for shared functional cards plus hand-specific rendering.

2. British Library, [Harley MS
   5228](https://searcharchives.bl.uk/catalog/040-002051072), catalogue record.
   This medical miscellany comprises eight independent units containing herbs
   and simples, antidotary excerpts, more than one recipe collection,
   uroscopy, a medical nomenclature, natural philosophy and a text on lucky and
   unlucky days. It demonstrates that heterogeneous medical and calendrical
   tools can be assembled as one working codex without one continuous text.

3. Melissa Reynolds, [“Here Is a Good Boke to Lerne”: Practical Books, the
   Coming of the Press, and the Search for Knowledge, ca.
   1400–1560](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12),
   *Journal of British Studies*. The article describes fifteenth-century
   practical miscellanies as products of repeated selection and recopying from
   an available corpus, combining medicine, agriculture, cookery, craft and
   other useful knowledge. This supports exemplar accumulation and repeated
   near-duplicates better than a single-author treatise.

4. CoReMA, [digital edition and corpus
   description](https://gams.uni-graz.at/o%3Akonde.p19) and [editorial
   declaration](https://gams.uni-graz.at/o%3Acorema.editorialdec). It documents
   more than eighty medieval manuscripts and about eight hundred recipes in
   several languages, preserves separate recipe collections within one
   manuscript, and records scribe-specific abbreviation, punctuation,
   terminators and layout. This supports distinguishing content tradition,
   collection structure and individual rendering.

5. Claire Burridge, [“Note on Weights, Measures, and Their
   Symbols”](https://www.ncbi.nlm.nih.gov/books/NBK608570/), in *Carolingian
   Medical Knowledge and Practice* (Brill, 2024). The documented measure terms
   can appear as full words, abbreviations, or diverse symbols, and even their
   exact physical quantities can be flexible. This is a useful warning that a
   stable technical card need not be phonetic and need not map to one modern
   numerical value.

None of these sources attests a Voynich alphabet or a literal card ledger.
They show that formula signs, exemplar persistence, scribe-specific expansion,
mixed practical collections and non-prose technical symbols were normal enough
to make the proposed workflow historically possible.

## What this theory explains at once

- **Free/bound reuse:** a card may be detached or joined according to the
  renderer; attached DY closure and free Y remain functionally distinct.
- **Exact-card wrapper collapse:** `DAIIN/SAIIN/CHAIIN/TAIIN` can be one card
  because the wrapper marks entry realization, not a new dictionary word.
- **Currier effects:** hands or exemplar shelves share a card deck while
  retaining different expansion/allograph habits.
- **Bio density:** many short, typed cells produce strong closure and a private
  technical tail.
- **Herbal openness:** the plant picture supplies the main address, allowing
  longer qualification/preparation strings without repeating a heading.
- **Line reset:** a physical line is a copy packet fitted around a prior image;
  `s` and occasional pickup repetition help re-enter the record.
- **q after close:** `q` is a conventional entry handshape after a completed
  cell, not necessarily “next.”
- **Repeated identical labels/cards:** repeated values are legitimate in a
  ledger and need not be accidental duplicate words.
- **Failure of simple ciphers and language mappings:** surface form includes
  whole-card abbreviation, wrapper allography, omitted pictured arguments and
  register-specific lookup entries.
- **Learnability:** the frequent formula deck is memorized; rare content is
  copied from exemplars; no scribe computes global transformations.

## Awkward observations and failures

1. There is no surviving ledger, bilingual expansion, correction key or
   external card-to-concept anchor.
2. Exact cards do not freely factor into the proposed HPR2 coordinates on
   unseen combinations. The theory must use registered whole cards, not claim
   productive prefix-stem-suffix morphology.
3. `Y-AIIN-Y` occurs only twice. Its “equal amount” reading is an attractive
   historical analogy and could be entirely wrong.
4. AIIN is portable enough to be a generic value/reference card, but that same
   portability makes a concrete quantity reading hard to distinguish from a
   grammatical frame.
5. Four frequent Bio closers remain different exact cards. Without additional
   matched stencils we cannot tell whether their differences encode result,
   state, unit, operation or merely inherited exemplar spelling.
6. The qokaiin boundary duplication has one occurrence. It may be dittography,
   emphasis or two genuine identical arguments rather than pickup.
7. The circle pages have no GDT327 coverage. Unifying them with the prose
   card-system would currently be an assertion, not a demonstrated parse.
8. A codebook that is usable by several scribes should leave teaching aids or
   especially stable core signs. The portable common deck is compatible with
   that prediction but does not uniquely demonstrate it.
9. A practical miscellany explains coexistence better than the integrated
   WHAT/HOW/WHEN theory; the integrated theory lacks explicit cross-references.
10. The proposal does not recover sounds, ordinary source-language syntax, or
    any confirmed full sentence.

## Fresh predictions on the fixed pages

These are prospective consequences for later checking, not results.

1. **Wrapper invariance:** after exact-card normalization, alternative wrappers
   of AIIN, Y, L/O and CTHY should preserve stencil position better than they
   preserve neighboring surface spelling.
2. **Equal-value construction:** if `Y-AIIN-Y` is an equal/same-value frame,
   both occurrences should sit between or adjacent to two independently
   comparable slots; its middle AIIN should not behave like a page heading.
3. **Typed closure:** each major Bio closer should prefer a reproducible
   pre-close stencil or field length even after hand and page are held fixed.
   Pure punctuation predicts much less differentiation.
4. **B ecology:** f55v should share the probability of explicit closure with
   Bio B but share more open-field content/stencil behavior with Herbal. It
   should not become globally Bio-like.
5. **Pickup deletion:** treating the duplicated f82r qokaiin boundary token as
   one carried state should yield a better-matched record stencil than treating
   both as independent values. No semantic gloss is needed for this test.
6. **Image-forced reflow:** other unusually repeated boundary cards, if any
   exist on the fixed pages, should concentrate where the drawing sharply
   changes available line width rather than at ordinary syntactic endpoints.
7. **Silent-address economy:** first cards of Herbal paragraphs should be
   diverse because the plant image already supplies the subject; a universal
   “take/name” heading is not expected.
8. **Local Bio addendum:** Bio-private OKE/OKEE/LCHE/E cards should recur within
   the same cell-stencil families more than the shared common cards do, even if
   their exact meanings remain opaque.
9. **Astro namespaces:** repeated surface labels should predict repeated roles
   within one diagram before predicting equality across f67/f68/f69. A single
   universal label dictionary is not expected.
10. **Copy competence without fluency:** rare cards should be copied with high
    internal graphic stability while common wrappers vary more by hand or line
    context—the reverse of an ordinary phonetic spelling-error pattern.

## Bottom line

The best working story is not “the scribes encrypted prose.” It is:

> A small workshop copied practical material into picture-addressed register
> forms. Recurrent instructions, relations, values and completion states were
> represented by learned whole cards. Scribes copied rare cards from model
> sheets, rendered common cards with local entry allographs, explicitly closed
> B/Bio cells, and reflowed continuing records around drawings already on the
> page.

The only concrete semantic advance worth retaining is the weak proposal that
`Y-AIIN-Y` is a same/equal-value construction and AIIN its value/reference
center. Everything else should remain a functional skeleton until a repeated
external referent is found on the fixed pages.
