# YOLO sidequest: ten-page scribe-workshop microtheory

Status: **deliberately speculative, post-hoc, and non-confirmatory**.

This is not a GDT result and does not modify any canonical claim. It asks what
a small workshop might plausibly have been doing if one deliberately tries to
make the current VManus grammar intelligible. The sample is fixed to four
Herbal pages (`f10r`, `f11r`, `f55v`, `f56r`), three Biological pages (`f81v`,
`f82r`, `f83r`) and three circle/astronomical pages (`f67r2`, `f68r1`, `f69v`).
No further page is admitted until this set is exhausted. ZL3b is used for the
displayed surface; reading uncertainty is retained where it matters. The
initial six-page pass did not access `f84` or `f84r`. During Iteration 4, a
direct scan of a mixed result table
unintentionally displayed one `f84v` row; it was excluded from the inference
and is disclosed in the ledger. No `f84r` row was accessed.

## Current synthesis after Iteration 79

The leading reconstruction is a **hybrid abbreviated language + technical
codebook** used for an illustrated medico-astrological workshop handbook.

```text
DOCUMENT
  four two-module plant entries
  three variable bath/site/apparatus records with local hydraulic labels
  three astronomical lookup modes: selection wheel, spatial catalogue, schedule

ENCODING
  picture/geometry supplies silent subject, owner, ordinal and some state
  paragraph supplies the main discourse module
  registered cards supply remaining content, setting, state and relation
  s/d/q and joining render licensed cards in local structural contexts
  DY checkpoints a local cell but does not end the statement
```

The strongest current content guess is not a translated word but a local
system: Biological `OL` behaves like a carrier/medium/channel class, and
`D/S + AR + OL + right state` differentiates related hydraulic constructions.
`OTAIN OLKAL` is a tub/apparatus caption candidate; `OKAL` is an anonymous card
reused between a figure label and two prose blocks; SOL is a flexible
Biological construction head. In Herbal A, `CHOL CTHY` is a repeated
quality/qualification construction, with a paired medical-quality reading now
leading over the earlier water-preparation guess. On the circle pages the
written label is residual data added to visible ring/star/radial coordinates.

Explicitly withdrawn readings include `AROL = WATER`, `OL = WATER`, SOL as a
confirmed verb, a fixed DESCRIPTION→RECIPE order for the two Herbal packets,
line equals sentence, a universal diagram-label dictionary, and a direct
f68↔f69 28-name list. No exact card has a confirmed English meaning.

The main unresolved fork is whether the long blocks are abbreviated natural
language, nominal technical specifications, or a mixture. The mixed world is
currently best because it explains prose texture, sparse label↔prose keys,
strong card recurrence and register-local rendering with one teachable system.

The sections below preserve the rapid historical iterations, including ideas
later narrowed or withdrawn. The current synthesis and the final iterations
take precedence over the early `v0.3` dictionary.

### Current sentence/record hierarchy

```text
PAGE        illustrated entry or lookup table
PARAGRAPH   record/module under the page subject
LINE        physical writing packet and renderer reset, not a sentence
FIELD       local clause/cell, often checkpointed by DY or line end
GROUP       rendered card or compact construction
JOIN/SPACE  local attachment choice, not automatically a word boundary
```

An “utterance” may span several physical lines, and a paragraph may contain
several clause-like fields. No current evidence establishes SVO order, POS or
sentence-final punctuation.

## Rapid iterations

### Version 0 — ordinary prose with encrypted words

Assume every visible group is a word and repeated groups are repeated lexical
items. This gives easy-looking sentences but explains the evidence badly:

- the same small pieces occur free, joined, and inside many surface groups;
- Currier B has many more compiled fields than comparable Herbal A pages;
- `s` is selected at physical-line entry and `q` after DY;
- exact-tuple/PAGE_HOST identities do not behave like a stable global lexicon;
- free predictive clustering of the 1,676 joint tuples produced no stable
  equivalence classes in GDT398.

Verdict: reject as the workshop's primary writing rule.

### Version 1 — a clean agglutinative language

Read `q-`, `d-`, `s-`, `-dy`, `-dal`, `-dar`, and `-sy` as morphemes around a
root. This explains `otedy/qotedy`, split/join forms such as `dar | ol/darol`,
and dense labels. It fails as a complete model: GDT003 does not beat strong
string baselines, segmentations overlap, the visual roles do not transfer, and
`AROL` occurs in plant/pharma labels as well as flow-like diagrams.

Verdict: retain productive-looking *formal construction*, reject a clean
global morpheme dictionary.

### Version 2 — pure nomenclator/codebook

Assume every exact joint tuple is an indivisible code. This explains opaque
repetition but not the regular line reset, wrapper licensing, DY fields,
split/join economy, or the shared grammar across registers.

Verdict: a codebook is present, but it is embedded in a compiler.

### Version 3 — leading workshop reconstruction

The best small-sample story is a **hybrid technical register: local address
codebook plus a shared record compiler**.

```text
PAGE_PROFILE := local inventory + diagram/specimen/process template

RECORD := ENTRY? FIELD (DY FIELD)* B3?
FIELD  := (WRAPPER FRAME? ADDRESS RIGHT_VALUE?)+

render(FIELD):
  choose joined/detached realization
  select s-form at a new physical-line entry where licensed
  select q-form after a DY closure where licensed
  abbreviate frequent address/value combinations
```

The content-bearing object is probably not one substring. It is the complete
page-conditioned address/construction. A visible group is therefore closer to
a filled form cell than to an ordinary word.

## Workshop dictionary v0.3

The right column is an intentionally aggressive guess, not a translation.

| Form coordinate | Best structural reading | Deliberate workshop guess |
|---|---|---|
| `PAGE_HOST` / exact address | page-conditioned opaque value | local item, state, material, or diagram-node code |
| `s-` | licensed physical-line-entry renderer | **NEW ENTRY / resume at margin** |
| `q-` | licensed post-DY renderer; productive `q+X` | **NEXT / linked continuation** |
| `d-` | recurrent binding wrapper | **OF / AT / WITH** relation |
| `ch-` | broad construction wrapper | ordinary **DESCRIPTOR** |
| `che-` | related extended wrapper | elaborated/derived descriptor |
| `sh-` | contrasting construction wrapper | state/result descriptor |
| `O` | local frame | default/current frame |
| `OT` | marked frame | alternate, referenced, or derived frame |
| right `aiin/ain` | recurrent right-side value family | count, index, or measure class |
| right `al/ar` | recurrent paired value families | two opposed variant classes, not left/right directions |
| `DY` | field closure | semicolon / **FIELD COMPLETE** |
| `B3` | harder record closure | full stop / **RECORD COMPLETE** |
| joined label | compressed record address | catalogue key with omitted field separators |

The least bad content guesses are deliberately abstract:

- `AROL`: initially **referenced unit/branch/item**; Iteration 4 below sharpens
  this to a possible course/carrier category. It may also be merely a frequent
  local address family whose value is rebound by page profile.
- `AIIN`: an **index/quantity-bearing value**, because it occurs both as a host
  and a right family. No number is assigned.
- `OK/OKEE/OKCH`: a broad family of **standard local entries/states**. The
  individual values remain page-local.
- `DAL/DAR/SY`: compact **variant/relation/status values** used especially in
  labels; they are not established suffixes or meanings.
- `OL`: a common **link/unit class**, compatible with free and joined use.

## Six-page micro-edition

### Herbal A — f10r

The page behaves like a relatively unsegmented specimen description. In the
GDT278-covered material, DY and B3 closures are absent. A representative line
is:

```text
f10r.2
dchey | cthoor | char | chty | os | chair | otytchol | oky | daiin | etyd

D:CHEY  CTHOOR  CH:AR  CH:TY  OS  CH:AIR  OTYTCHOL  OKY  D:AIIN  ETYD
```

Workshop paraphrase:

> Open the specimen entry under CHEY; list its CTHOOR, AR, TY, OS and AIR
> descriptors; add the OTYTCHOL/OKY classification and AIIN index; close the
> line.

This is not word-for-word plaintext. It treats the line as one long form whose
slots carry several local observations. The many `ch-` realizations are more
naturally repeated descriptor constructions than repeated content words.

### Herbal B — f55v

The matched page has the same broad illustration profile but uses a denser
record style. A covered line divides cleanly at `oldy`:

```text
f55v.11
ykaiin | cheoar | cheeky | oldy  //  aiin | okal | oltchy | or | y | orain

YK+AIIN  CHE:O+AR  CHE:EKY  O:L+DY
// AIIN  OK+AL  OLTCHY  OR  Y  OR+AIN
```

Workshop paraphrase:

> Specimen/index YK-AIIN: elaborated O-AR and EKY descriptors; field complete.
> Then record the AIIN value, OK-AL class, OLTCHY item, and OR/Y/OR-AIN detail.

The important contrast is architectural: B compresses a page entry into more
explicit fields. It need not be a different language. A small workshop could
have an older/descriptive A register and a later/tabular B register, with hand
and Currier differences inseparable.

### Biological — f82r

Here the same compiler is used as a dense apparatus/process ledger. `f82r.2`
contains four fields, the first two being single closed cells:

```text
dchedy // qolchedy // qokain | dy | qokeedy // qokal | lcheckhy | lched

D:CHE+DY
// Q:OLCHE+DY
// Q:OK+AIN  D:Y  Q:OKEE+DY
// Q:OK+AL  LCHECKHY  LCHED
```

Workshop paraphrase:

> Register component/state CHE; next linked OLCHE; continue with indexed OK,
> Y, and OKEE; then open the linked OK-AL detail and its two descriptors.

The diagram labels `darol` and the reading-unstable `darary` are then compact
addresses attached to two independently described flow-like structures:

```text
darol  ≈ D(relation) + AROL(local unit)
darary ≈ D(relation) + AR... (reading unstable)
```

The theory does **not** say AROL means flow. It says the page profile can bind a
generic/local address to an apparatus node.

### Biological — f83r

The page supplies a particularly form-like three-cell line:

```text
f83r.47
otchdy // qokchdy // shedal

OT:CH+DY // Q:OKCH+DY // SH:ED+AL
```

Workshop paraphrase:

> Mark the CH item in the alternate frame; continue with linked OKCH; finish
> with the ED state of variant AL.

The nearby labels can be made coherent without making them water words:

```text
darolsy   ≈ D(relation) + AROL(unit/address) + SY(variant)
saroldal  ≈ S(entry)    + AROL(unit/address) + DAL(variant)
```

The second form is transcription-uncertain (`sasoldal` in ZL3b versus
`saroldal` in IT2a/RF1b). The attractive reading is therefore only that two
parallel structures receive two related *catalogue addresses*. Their shared
part identifies a local class; the edges distinguish relation/entry and
variant. Only the rigid equation `AROL = WATER` is excluded; a water-, sap-,
or conduit-related construction can occur beside plants as well as apparatus.

### Astronomical/circle — f67r2

This page is best read as several circular legends, not prose. Human inventory
defines a seven-member circular label set and a twelve-member moon-associated
set. Representative constructions include:

```text
ydchos | ain | ar | amy
sor | chedaiin | dy
todaiin | dain | dy
qotoear
ytodal
```

Workshop reading:

> A page-local table names or addresses members of several closed systems. A
> multi-group legend can carry an address, index/value and closure; compact
> one-group labels are precompiled catalogue keys.

The seven and twelve positions suggest celestial/system inventories, but no
group is assigned to a planet, sign, direction, or number. The same formal
compiler can render a legend item more compactly than a prose field.

### Astronomical/circle — f69v

The external geometry is unusually strong: 28 radial text loci and a strict
14 LONG / 14 SHORT alternation. The text does not reliably distinguish the two
visual classes. Several labels nevertheless look like closed catalogue cells:

```text
ytody  okody  otody  ykeydy  ykeody  sarydy  okeody
```

Workshop reading:

> This is a 28-entry cyclic schedule or observational register. Each spoke
> receives a local address and sometimes an explicit closure. LONG/SHORT is a
> layout/parity convention—possibly two alternating table states—not a decoded
> odd/even word contrast. DY closes an entry; it does not mean “day”.

A lunar/calendar-like practical purpose is the best genre guess, but direct
table transfer is weakened by the poor lag-14 textual symmetry and by generic
medieval prevalence of 28-member lunar systems.

## How the workshop could produce the manuscript

1. A master prepares a page template and a small local list of content
   addresses.
2. A compiler convention specifies entry, continuation, frame, value and
   closure states.
3. The scribe fills records from a source notebook, memory, diagram, or spoken
   instruction.
4. Frequent combinations fuse; rare combinations remain separated. Spaces are
   therefore construction boundaries, not necessarily linguistic word spaces.
5. A label suppresses most record scaffolding and joins an address with one or
   two discriminating values.
6. Scribes share the compiler but differ in abbreviatory habits and local
   codebooks. Currier A/B can therefore differ sharply while remaining one
   workshop technology.
7. Fossilized pieces survive after their original compositional motivation is
   lost. This produces apparent morphology that is real historically but not
   synchronically recoverable as clean slots.

## What this model explains unusually well

- free/bound and split/join reuse without requiring every piece to be a live
  morpheme;
- productive-looking `q+X` and right-edge DY without beating generic string
  models as a natural-language paradigm;
- `s` at line entry and `q` after field closure;
- Currier-B field density and its different renderer regime;
- labels being more compositionally dense than running text;
- repeated identical labels such as `daldy` as repeated filled form cells;
- local label/prose reuse without a global label dictionary;
- strong page/register effects and weak manuscript-global host semantics;
- failures of phoneme mapping, simple cipher mappings, universal semantic
  roots, and free latent-tuple clustering.

## Awkward facts

- The model can explain almost any local code by rebinding it, so it risks
  becoming unfalsifiably flexible.
- No page-local codebook has been recovered independently.
- Exact joint tuples are sparse and do not compress into stable free
  equivalence classes.
- Some long lines may still contain natural-language syntax that this form
  interpretation washes out.
- There is no anchored value for even one address, wrapper, or right family.
- The f69v LONG/SHORT alternation remains visual only.

## Sidequest conclusion

If I had to act as one of the scribes, I would not think “write an encrypted
sentence.” I would think:

> choose the page's item code; place it into the current record slot; mark
> whether this is a new entry, a linked continuation, a framed variant, or a
> value-bearing form; close the field; abbreviate the result according to the
> hand's house style.

The best explicit meaning guess is therefore not a vocabulary but a writing
procedure. The manuscript is most plausibly rendered as a **technical
catalogue/process notebook with page-local addresses and a shared scribal
compiler**, possibly carrying compressed natural-language residue inside some
addresses. On these six pages, that theory makes more coherent sense than a
word cipher, a clean agglutinative language, or a pure nomenclator.

## Iteration 4 — allow water in plant records

The original wording made the plant-label counterexamples do too much work. A
plant illustration can perfectly well be accompanied by a note about water,
sap, juice, soaking, irrigation, root uptake, or a conduit-like stalk. The
counterexamples exclude only the rigid equation `AROL = WATER`.

Three competing readings were compared informally:

1. **AROL = a water/fluid noun.** This fits `darol` beside the f82r waterfall,
   the f75v pond context, and `orarol` in front of Rosettes tubes. It becomes
   strained in circular contexts and does not explain why the form changes at
   its edges.
2. **AROL = a plant stem/branch.** This fits `sarol` near a stalk on f102v2,
   `darolaly` near a stem on f99v, and longer AROL labels below leaves. It fails
   to generalize naturally to waterfalls, tubes, and circular diagrams.
3. **AROL = a course/carrier/connection.** This can be realized physically as
   a stem or sap path in a plant, a pipe/watercourse in an apparatus, and a
   connection/orbit in a circle. It explains the cross-domain distribution
   with one abstract workshop category.

Version 3 is the new leading guess. The microlexicon becomes:

```text
AR       ≈ transmitted/circulating content or active connection class
OL       ≈ carrier/path/axis construction
AROL     ≈ connected carrier, course, conduit, stalk-path, branch-path
d+AROL   ≈ active/outgoing/delivery course
s+AROL   ≈ source/incoming/standing course
AROL+SY  ≈ course with endpoint/status variant SY
AROL+DAL ≈ course with endpoint/status variant DAL
```

This is deliberately bolder than the evidence. In particular, no controlled
visual test has established the proposed `d/s` polarity, and `AR + OL` need
not be the true synchronous segmentation. But it gives a useful workshop
reading of the f82r/f83r labels:

```text
f82r  darol       "delivery/outgoing conduit"
f83r  darolsy     "delivery conduit, endpoint/status SY"
f83r  saroldal    "source/return conduit, endpoint/status DAL"
```

The last surface is reading-sensitive. The paraphrases are therefore not
translations; they are the most economical explicit design values for a
scribe trying to make related apparatus labels while retaining the plant
occurrences.

Under this revision, the plant pages need not contain only botanical names.
Their records may mix specimen identity with functional observations such as
root uptake, sap-bearing stalks, expressed juice, soaking, or preparation.
This strengthens the overall **technical notebook** interpretation: the same
formal course/carrier category can be reused across living plants, vessels,
channels, and astronomical paths without requiring the same concrete object.

## Iteration 5 — one practical workflow across the six pages

The most coherent manuscript-level guess is no longer merely “technical
catalogue.” It is a **medical/pharmacological and balneological workshop book
with an astronomical scheduling layer**:

```text
HERBAL A     raw material/specimen identification and properties
HERBAL B     preparation, quantity, carrier and derived-state records
BIOLOGICAL   apparatus, flow, bathing/application and process diagrams
ASTRO/CIRCLE timing, cycle, condition and lookup tables
```

This does not require every section to be prose or every drawing to illustrate
the adjacent record exactly. The workshop can reuse one compiler while loading
a different local address table for plants, preparations, apparatus and
cycles.

### More aggressive functional lexicon

| Form | Iteration-5 guess | Intended breadth |
|---|---|---|
| `s-` | start/resume a record | entry control, not content |
| `q-` | then/next/linked step | continuation control |
| `d-` | take from/apply to/through | generic directed relation |
| `ch-` | describe or qualify | ordinary property construction |
| `che-` | prepare/transform/qualified state | process-like construction |
| `sh-` | resulting or standing state | state/result construction |
| `t-` | marked action/instruction | rare action-head candidate |
| `Y` | local pointer/index carrier | “this/entry n” without a number value |
| `AIIN/AIN` | amount, count, dose, or table index | value slot |
| `OL` | carrier/base/path | liquid, stalk, tube, or formal carrier |
| `AROL` | conducting course/carrier | sap path, tube, watercourse, orbit |
| `OK/OKEE` | standard operation/state family | perhaps continue, circulate, prepare |
| `AL/AR` | paired input/output or state variants | no direction assigned |
| `SY/DAL/DAR` | endpoint/condition variants | compact label discrimination |
| `DY` | complete the current field | punctuation-like compiler state |
| `B3` | complete the record | stronger terminal state |

The most useful new guess is `Q+OKEE+DY ≈ THEN CONTINUE/PROCESS;`. It is a
very common, highly reusable closed cell and repeats several times in dense
Biological records. This need not mean one ordinary word. It can be a compiled
instruction cell.

### Reverse-generating f55v.11

Start from an invented workshop record:

```text
ITEM YK, VALUE AIIN
PREPARE/QUALIFY O with variant AR
PREPARE/QUALIFY EKY
CARRIER L; CLOSE FIELD
VALUE AIIN, STANDARD-STATE AL, CARRIER OLTCHY, VALUES OR/Y/OR-AIN
```

Apply the guessed compiler:

```text
YK+AIIN | CHE+O+AR | CHE+EKY | O+L+DY
// AIIN | OK+AL | OLTCHY | OR | Y | OR+AIN
```

This yields the observed line:

```text
ykaiin | cheoar | cheeky | oldy // aiin | okal | oltchy | or | y | orain
```

The result reads naturally as a plant-linked preparation record even though
the page carries a plant illustration. The picture can identify the raw
material while the text specifies extraction, carrier, amount, or use.

### Reverse-generating f82r.27

Treat the seven closed fields as a process path rather than seven words:

```text
pchedy
// rsheal | daldy
// qokeedy
// rshedy
// qoteedy
// qokeedy
// lochedy
```

Provisional workshop paraphrase:

> Establish the PCHE state. Pass RSHE through variant AL and close. Then
> continue/circulate. Set the RSHE state. Then use the marked EE treatment.
> Continue/circulate again. End in the LOCHE receiver/state.

This is the first speculative reading that makes repeated `qokeedy` useful:
it acts like a recurrent process instruction or continuation checkpoint. The
large number of one-cell DY fields becomes expected in a diagram-associated
procedure.

### Reinterpreting the circle pages

Under the unified workflow, f67r2 and f69v need not contain names of planets
or lunar days. They can be lookup keys used by the preparation/application
records:

- the seven-member set selects one of seven celestial/time conditions;
- the twelve-member set selects a larger cycle class;
- the 28-spoke f69v wheel supplies daily/nightly or phase-indexed conditions;
- strict LONG/SHORT alternation is an alternating table channel, perhaps two
  classes of entry, not a decoded word feature.

The bolder semantic paraphrase is:

> choose material → prepare it through a carrier/process → apply or circulate
> it under a selected cyclical condition → close the record.

That is not yet a translation, but it is a concrete end-to-end purpose that
lets the same formal grammar do useful work in all six sampled pages.

### Current leading reconstruction

```text
VISIBLE GROUP
  = render(
      local item/process code,
      record operation,
      carrier/frame,
      value or condition,
      closure state,
      register and hand convention
    )

VISIBLE LINE
  = ITEM/HEAD + PROPERTY* + PROCESS* + CONDITION* + CLOSE
```

The system is therefore plausibly **compressed technical language plus
notation**, not purely one or the other. Some local codes may abbreviate real
spoken words; the surrounding construction behaves like a form language.

## Iteration 6 — the visible ending is not the grammatical unit

A quick internal consistency check on the covered f82r/f83r lines improves the
model. The visible string ending `-dy` cannot always be read as the same suffix.

```text
qokeedy = q + OKEE + licensed DY closure
qokedy  = q + OKE  + licensed DY closure
qoteedy = q + OT-frame + EE + licensed DY closure
daldy   = d + AL + licensed DY closure
oldy    = O-frame + L + licensed DY closure

chedy   = often CHE wrapper + Y host, with NO licensed DY closure
```

In the covered f82r/f83r events, all ten `qokeedy` occurrences are either the
only or the last group of their field and all ten carry the formal DY closure.
The inspected `qokedy` and `qoteedy` cases behave the same way. By contrast,
the covered `chedy` cases are mostly field-internal and carry no formal DY
closure despite their surface spelling.

This changes the invented lexicon in an important way:

- `DY` is not an alphabetic suffix meaning “finished.” It is a **licensed
  construction cell** whose surface can overlap ordinary host material.
- `qokeedy` is not simply a word for “continue.” Its best full reading is
  **NEXT/PROCESS(OKEE) + CLOSE FIELD**.
- `chedy` may instead be an inline **DESCRIPTOR(Y)** construction.
- a reader in the workshop recognizes the construction from slot, spacing,
  line state and expected record schema, not from the final glyphs alone.

The wrapper ecology on these two pages fits that interpretation. `s` is
concentrated at record/line entry; `che` is overwhelmingly nonclosing and
internal; `q` frequently realizes compact closed cells; `sh` often carries a
closing/result state. These are tendencies, not a one-form/one-function code.

### Revised record syntax

```text
RECORD := ENTRY_FIELD CONTINUATION_FIELD* TERMINAL_FIELD?

ENTRY_FIELD := S_ENTRY? HEAD DESCRIPTOR*
CONTINUATION_FIELD := Q_LINK? ARGUMENT* CHECKPOINT
CHECKPOINT := STATE_OR_PROCESS + LICENSED_DY
TERMINAL_FIELD := RESULT_OR_VALUE + (DY | B3 | LINE_END)
```

Working semantic roles:

```text
s-construction      "start/resume this record"
ch/che-construction "describe the current item"
d-construction      "bind a source, recipient, carrier, or relation"
q-construction      "continue with a linked field/step"
sh-construction     "record a standing/result state"
DY-cell             "commit the current field"
B3-cell             "commit the complete record"
```

This is closer to a medieval shorthand or tabular notarial system than to
ordinary alphabetic morphology. The same visible glyph sequence can be parsed
differently because construction position is part of the code.

### Consequence for translation attempts

A future line reading should first recover the record actions and only then
guess content:

```text
surface: qokeedy
bad first move: identify a word stem OKEE and suffix DY
better move:   identify a complete linked checkpoint cell
               [Q_LINK, local value OKEE, FIELD_CLOSE]
```

Thus the current best “translation” is two-layered:

```text
formal reading: NEXT(OKEE); CLOSE
content guess:  then continue/process/circulate; checkpoint
```

The formal reading is considerably more plausible than the content guess.

## Iteration 7 — a provisional procedural automaton

The construction tendencies can be turned into a concrete scribal state
machine:

```text
START/SELECT
  -> ITEM_OR_AMOUNT
  -> DESCRIPTION*
  -> (NEXT_PROCESS -> ARGUMENT_OR_VALUE* -> CHECKPOINT)*
  -> RESULT_STATE?
  -> RECORD_CLOSE
```

The most aggressive cell-level guesses are now:

```text
daiin      ASSIGN/TAKE an AIIN amount or index
qokaiin    NEXT: standard entry with AIIN amount/index
qokal      NEXT: standard entry, variant AL
qokeedy    NEXT: perform/continue OKEE; close field
qokedy     NEXT: perform/continue OKE; close field
shedy      RESULT/standing state E; close field
chedy      describe/qualify Y (usually not a close cell)
oldy       carrier/base L; close field
daldy      assign/route variant AL; close field
```

`AIIN` is allowed to be either a numerical-looking index or a conventional
quantity class; no number is guessed. `OK/OKE/OKEE` may be a family of closely
related standard processes, degrees, or states. Their difference could be
lexical, scalar, or merely historical allography.

### A fuller f82r.2 reading

```text
dchedy
// qolchedy
// qokain | dy | qokeedy
// qokal | lcheckhy | lched
```

Two-layer paraphrase:

```text
FORMAL
SELECT(CHE); CLOSE
NEXT(OLCHE); CLOSE
NEXT(OK, value AIN), ASSIGN(Y), NEXT_PROCESS(OKEE); CLOSE
NEXT(OK, variant AL), DESCRIBE(LCHECKHY, LCHED); LINE CLOSE

SPECULATIVE CONTENT
Take/establish the CHE material or state.
Pass to the OLCHE carrier/state.
Use indexed OK with Y, then continue the OKEE treatment.
Finally use OK-AL with the two listed descriptors.
```

### A short unclosed line: f83r.52

```text
solkeey | qekey | raly | ol

S:OLKEEY | Q:EKEY | RALY | O:L
```

Provisional reading:

> Start/resume the OLKEEY item; link EKEY; add RALY; place or understand it in
> carrier/frame L. The physical line end commits the field without an explicit
> DY cell.

This explains why some records are saturated with `DY` while others have none:
line end is itself a licensed closure, and B-style pages more often spell out
intermediate checkpoints.

### Updated manuscript purpose

The most specific coherent story is now:

> a workshop reference manual for identifying natural materials, assigning
> quantities or indices, preparing/extracting them through carrier states or
> vessels, recording intermediate/result states, and selecting cyclical
> conditions for the operation.

The script is partly abbreviatory language and partly an executable notation.
Its “sentences” are closer to recipes, register entries, or process cards than
to narrative clauses.

## Iteration 8 — three layers of vocabulary

Trying to give every recurring host one global concrete meaning makes the
theory unstable. A workshop would more plausibly maintain three vocabularies:

### Layer A: shared control language

```text
S_ENTRY       start/resume
Q_LINK        next/continue in the same construction
D_BIND        take/assign/connect/apply
CHE_DESCRIBE  supply an inline property or prepared form
SH_STATE      supply a standing/result state
DY_CLOSE      commit field
B3_CLOSE      commit record
```

These are grammatical or notational actions shared by the scribes.

### Layer B: broad technical value families

```text
AIIN  portion, unit, count, dose, or ordinal value
DAIIN take/assign one AIIN-class value
DAIN  related shorter value form
DAIR  contrasting value/measure realization

OL    carrier, base, path, vessel relation
AROL  conducting carrier/course: sap path, tube, channel, orbit

OK/OKE/OKEE
      standard state/process family; OKEE tentatively means repeat,
      continue, cycle, circulate, or maintain the treatment

AL/AR two paired state, route, or endpoint classes
```

Layer B is allowed to become more concrete inside a register. For Biological
records, `OKEE` might be “circulate/rinse”; in Herbal preparation, “soak or
repeat treatment”; in a circle table, “advance/continuing phase.” The shared
meaning would be ITERATE/CONTINUE, not one substance.

### Layer C: page-local address values

Forms such as `CHEY`, `CTHOOR`, `EKY`, `RSHE`, `LCHECKHY`, and `OLTCHY` are
currently treated as page- or register-local material, state, apparatus, or
property codes. Their visible similarity may reflect historical ancestry or
scribal abbreviation, but their value is loaded from the current page profile.

This separation prevents the theory from demanding that every repeated shape
be either meaningless or a universal dictionary word.

### First explicit quantity guess

`AIIN` is the best candidate for a value-bearing technical unit because it is
common in Herbal, Biological, and circle material, occurs independently, and
also fills a right-side value family. The deliberately literal guess is:

```text
AIIN   "one registered portion/unit" or "unit-value slot"
DAIIN  "take/assign a portion"
QOKAIIN "then use the standard AIIN value"
```

No numerical value is implied. The “one” reading means one conventional unit
entry, not the integer 1.

### Microtranslations

```text
f10r.12
odaiin | daiin | qotchy | qotor
```

> In the current O-frame, record a portion; take/assign a portion; then use
> TCHY; then use OR.

```text
f55v.6
ykaiin | daiin | ykair | cheky | daiiny
```

> YK with its unit value; assign a portion; YK with the contrasting measure;
> prepare/describe KY; finish with the Y-marked portion state.

```text
f82r.16
qokeedy | lchedy | qokeedy | cheey | r | or | ol | s | aiin | chey | ... | dam
```

> Continue/circulate and close; commit the LCHE state; continue/circulate
> again; describe Y with the listed R/OR/OL material; resume with an AIIN unit;
> add CHEY; terminate with DAM.

The last paraphrase is useful because repeated `qokeedy` now means an iterative
action bracketing another state, not a repeated object name.

### Current confidence ordering inside the sidequest

```text
highest:  DY/B3 closure; s-entry; q-linked continuation
medium:   che-description; sh-state/result; AIIN value/portion class
low:      OKEE iterate/circulate; OL carrier; AROL course/conduit
very low: concrete water, dose, source/return, or action glosses
```

This is still deliberate invention, but it now distinguishes what the scribe
probably did structurally from what the workshop may have meant technically.

## Iteration 9 — section-specific record syntax

The same compiler appears to be used with different higher-level templates.
In the covered six-page material, the useful qualitative contrast is:

```text
HERBAL A
  one long descriptive field, usually committed by physical line end

HERBAL B
  one preparation/property field // one value/result field

BIOLOGICAL
  CHECKPOINT // CHECKPOINT // CHECKPOINT ... // descriptive tail

CIRCLE LABEL
  one compact precompiled address/value cell
```

This suggests that “sentence structure” is section-dependent even if the cell
grammar is shared.

### Biological command-cell hypothesis

Singleton closed fields are tentatively read by wrapper class:

```text
Q+VALUE+DY   linked process/next-step checkpoint
SH+VALUE+DY  standing/result-state checkpoint
D+VALUE+DY   assign, transfer, take-from, or apply-to checkpoint
S+VALUE+DY   reset, resume, or new-subroutine checkpoint
VALUE+DY     bare state/material checkpoint
```

A multi-group final field then supplies arguments, values, exceptions, or a
description and is committed by line end. The wrappers do not have to be
spoken words; they may function like rubric symbols in an executable recipe.

### Re-reading f82r.2 as a small program

```text
D(CHE); CLOSE
Q(OLCHE); CLOSE
Q(OK-AIN), D(Y), Q(OKEE); CLOSE
Q(OK-AL), LCHECKHY, LCHED; LINE CLOSE
```

Possible operational paraphrase:

> Establish or take CHE. Transfer to the linked OLCHE stage. At the indexed OK
> stage assign Y and continue the OKEE treatment. Finish with OK variant AL and
> its two qualifying values.

### Re-reading f83r.47 as state progression

```text
OT(CH); CLOSE
Q(OKCH); CLOSE
SH(ED-AL); LINE CLOSE
```

> Enter the marked CH state. Continue through OKCH. Record the resulting ED-AL
> state.

This is substantially more coherent than treating `otchdy`, `qokchdy`, and
`shedal` as three unrelated nouns.

### Why Currier B looks different

The difference may be documentary rather than linguistic:

- Currier A spells out descriptive chains and lets line end close them.
- Currier B compiles intermediate stages into explicit closed cells.
- Biological B pushes this convention furthest because a depicted process or
  apparatus benefits from checkpoint-like notation.
- A small workshop can teach both as register templates while retaining shared
  signs and local content codes.

The resulting leading syntax is:

```text
LINE := DESCRIPTION_RECORD
      | PREPARATION_FIELD // VALUE_OR_RESULT_FIELD
      | CHECKPOINT+ // ARGUMENT_OR_RESULT_TAIL
      | COMPACT_LABEL
```

This gives the manuscript a plausible sentence structure without forcing it
to copy the syntax of an ordinary spoken language.

## Iteration 10 — the picture is a grammatical argument

The circle pages reveal a more powerful design principle: the visible text is
only one channel of the record. Geometry and illustration can supply values
that the scribe deliberately omits from the glyph sequence.

```text
COMPLETE RECORD MEANING
  = PAGE/IMAGE REFERENT
  + OWNED OBJECT OR SLOT
  + GEOMETRIC STATE
  + TEXTUAL CONSTRUCTION CELLS
```

### Herbal consequence

The plant drawing can function as a zero-marked record head:

```text
[THIS DEPICTED PLANT]
  property ...
  portion AIIN ...
  carrier/water/sap treatment ...
  resulting state ...
```

The prose therefore need not contain a plant name. A note about water, root
uptake, expressed juice, soaking, or storage beside a plant is exactly what a
working herbal/preparation manual would need. This resolves the false dilemma
between “plant label” and “water word.”

### Biological consequence

The diagram supplies vessels, bodies, pipes, or process nodes. Text can then
encode only operations and state changes:

```text
[THE DEPICTED NODE/CHANNEL]
  D_BIND(AROL-course)
  Q_NEXT(process)
  SH_RESULT(state)
```

Under this model `AROL` is best treated as an **edge/path relation class**—a
conducting or connecting course—rather than the name of water or of the object
itself. A plant stalk, apparatus pipe, waterfall path, and diagram connection
can instantiate the same formal relation.

### f69v consequence

Every radial entry already carries at least three channels:

```text
ordinal/cyclic position i
LONG or SHORT radial state
local textual label tuple
```

The full entry is therefore:

```text
F69_ENTRY(i) := POSITION(i) + PARITY_STATE(i) + LABEL_CODE(i)
```

The strict alternation can be a table-reading convention analogous to
alternating ink or background treatment in other 28-member medieval systems.
It need not encode a property repeated inside the label. This predicts exactly
why F69LS001 found no reliable textual LONG/SHORT marker.

The 28 labels can be member-specific keys while geometry provides their order
and alternating class. A lunar-night, mansion, treatment-day, or prognostic
schedule remains a plausible genre guess, but direct values and a start
direction remain unknown.

### f67r2 consequence

The seven- and twelve-member rings similarly supply class membership and order
visually. Compact labels need encode only the local member key or associated
value. They do not need to spell out “planet,” “sign,” or a number.

### Revised notion of a Voynich “sentence”

```text
TEXT-ONLY VIEW:
  Q(OKEE); SH(E); AIIN ...

SCRIBE'S VIEW:
  for the object shown here,
  at this diagram position,
  continue the registered process,
  record the resulting state and unit value.
```

This is the first reconstruction that explains why extensive internal grammar
can coexist with almost no recoverable standalone semantics: crucial arguments
are supplied by page context, object ownership, and geometry rather than by a
globally readable word sequence.

### Updated leading architecture

```text
ILLUSTRATED REFERENT OR TABLE SLOT
    -> supplies entity/class/index silently
LOCAL ADDRESS CODE
    -> identifies a material, state, member, edge, or operation within page
SHARED COMPILER
    -> start/link/describe/assign/state/close
SCRIBE RENDERER
    -> joins, spaces, abbreviates, and selects hand/register variants
```

The manuscript may consequently be less like encrypted prose and more like an
illustrated database whose rows contain compressed procedural annotations.

## Iteration 11 — write like the scribe

To make the theory genuinely generative, start with an invented workshop
instruction rather than an observed line.

### Plant preparation card

Underlying instruction:

> For the plant drawn on this page, take one registered portion; prepare it in
> the carrier/base; repeat or circulate the treatment; record result variant
> AL.

Compiler input:

```text
IMAGE_HEAD(plant)
D_ASSIGN(AIIN)
CHE_PREPARE(OL)
Q_NEXT(OKEE) + DY_CLOSE
SH_RESULT(ED, AL)
```

Generated surface:

```text
daiin | cheol | qokeedy | shedal
```

Every construction is ordinary-looking under the small-page inventory. The
plant name is absent because the drawing supplies it.

### Apparatus/process card

Underlying instruction:

> Use the outgoing carrier-course with endpoint SY; continue through the OKCH
> stage; record result ED-AL.

Compiler input and surface:

```text
D_BIND(AROL, SY) | Q_NEXT(OKCH)+DY | SH_RESULT(ED, AL)

darolsy | qokchdy | shedal
```

This deliberately combines the f83r label construction with the observed
checkpoint/result forms. It looks like the same workshop language rather than
a new cipher alphabet.

### Circle-table keys

For a radial member whose ordinal and binary class are supplied geometrically:

```text
Y_INDEX(TO) + DY_CLOSE  -> ytody
STATE(OKO) + DY_CLOSE   -> okody
OT_FRAME(O) + DY_CLOSE -> otody
```

These three actual-looking f69v labels can be generated as alternative local
member keys without encoding their radial length in the text.

### What this exercise changes

The system can now generate plausible Voynich forms from one compact design:

```text
silent illustrated/table argument
+ local value code
+ control construction
+ optional frame/value
+ licensed close
```

The most important remaining ambiguity is whether `AIIN`, `OKEE`, `OL`, and
`AROL` have broad technical meanings or are merely local values repeatedly
loaded into the same compiler slots. The writing system works in either case;
only the translation changes.

## Iteration 12 — repeated strokes as scalar payload

The common near-pairs are easier to understand if repeated `e/i`-like units are
technical tallies or grades rather than vowels:

```text
qokedy   / qokeedy   / qokeeedy
qokain   / qokaiin   / qokaiiin
oteedy   / oteeedy
```

These forms coexist in similar lines and sometimes in the same record. A
workshop can use repeated strokes to mark relative amount, duration, degree,
iteration, or a small ordinal while retaining the same surrounding operation.

Provisional mechanism:

```text
E^n in an OK/OKE construction
    = process/state grade or duration n

I^n in an AIN/AIIN construction
    = amount/index grade n

Y
    = value terminator or compact state ending in some constructions
```

No absolute number is assigned. Only the relative principle “more repeated
units may represent a different grade” is being invented.

### Example paradigm

```text
Q + OK + E  + DY  -> qokedy
Q + OK + EE + DY  -> qokeedy
Q + OK + EEE+ DY  -> qokeeedy
```

Possible reading:

```text
qokedy    continue the standard process at grade/duration 1; close
qokeedy   continue the standard process at grade/duration 2; close
qokeeedy  continue the standard process at grade/duration 3; close
```

Likewise:

```text
qokain    next standard value, short amount/index grade
qokaiin   next standard value, longer amount/index grade
```

This is more attractive than treating every member as an unrelated word, but
it need not be numerical morphology in a spoken language. It can be a scribal
value code embedded inside the composite cell.

### Why this helps the manuscript-wide theory

- Herbal records need quantities, proportions, durations, and preparation
  grades.
- Biological/process records need repeated operations and state levels.
- Astronomical tables need ordinal or cyclical values.
- repeated strokes are economical for a workshop and naturally generate dense
  near-neighbour families;
- a phoneme mapping will fail if some graphemes function as tallies rather than
  sounds;
- exact whole forms remain sparse because control, local address, scalar value,
  closure, and renderer are fused.

### Updated generated instruction

Underlying note:

> Take an AIIN-grade portion of the depicted plant; process it in carrier OL
> for OKEE-grade duration; record state AL.

```text
daiin | cheol | qokeedy | shedal
```

The same surface generated in Iteration 11 now receives a more specific
internal interpretation: `AIIN` and `EE` are value-bearing grades rather than
ordinary lexical syllables.

The risk is obvious: repeated glyphs can arise from ordinary orthography,
abbreviation, copying habits, or the transcription system. The scalar reading
is retained only because it makes the invented technical notation simpler.

## Iteration 13 — how a small workshop could evolve the system

The final surface should not expose a clean designed grammar. Assume several
scribal habits descended from an earlier practical notation.

### Stage 1: loose source notes

```text
ITEM   AMOUNT   PROCESS   RESULT
```

Content abbreviations are relatively independent. A picture or marginal label
supplies the item.

### Stage 2: recurrent control marks

Scribes introduce free or detached marks for:

```text
new entry | next step | relation | field done | record done
```

These become the ancestors of `s`, `q`, `d`, DY and B3 constructions.

### Stage 3: fusion and positional allomorphy

High-frequency sequences fuse:

```text
q | okee | DY -> qokeedy
d | ar | ol   -> darol
ar | ol       -> arol
```

The same pieces remain detached in slower writing or when scope must be clear.
Line-entry and post-closure position begin selecting `s` and `q` renderers.

### Stage 4: tabular standardization

Currier-B hands increasingly write explicit intermediate cells:

```text
STEP; STEP; STATE; STEP; RESULT
```

Currier A retains longer descriptive lines and lets physical line end perform
more closure work. This is a register/history contrast, not necessarily a
language split.

### Stage 5: scalar and geometric compression

Repeated strokes encode value grades; diagrams encode entity, order, binary
state, and ownership. Text carries only the residual instruction or local key.

### Stage 6: fossilization and local rebinding

Later scribes copy forms whose original pieces are no longer fully productive.
A historically meaningful component can become:

- obligatory renderer material;
- a page-local address fragment;
- an opaque fixed cell;
- a construction used with a new technical value;
- a homograph of a still-live closure or scalar mark.

This yields strong formal reuse but weak clean paradigms. It also explains why
free clustering of complete joint tuples finds no stable lexicon: historical
ancestry, present function, and local value need not define the same partition.

### Proposed workshop stations

```text
HAND 1 / descriptive station
  longer Herbal-A fields, inline CH constructions, fewer explicit stops

HANDS 2/3/5 / tabular-process station
  denser Herbal-B and Biological fields, checkpoint cells and Q links

CIRCLE specialist
  compact labels; order, parity and class delegated to diagram geometry
```

These are functional stations in the imagined workshop, not identified people.

### Translation consequence

There may be no valid operation “strip affixes and read the root.” A decoder
would instead need:

```text
historical form family
+ current construction role
+ page-local value binding
+ scalar/closure interpretation
+ visual/geometric arguments
+ hand/register renderer
```

Only after those layers are resolved would an ordinary-language paraphrase be
possible.

## Iteration 14 — fixed translation draft

To prevent the sidequest from changing its glosses on every line, the current
working decoder is frozen in
`SIDEQUEST_SCRIBE_WORKSHOP_TRANSLATION_DRAFT.tsv`. It contains twelve real
micro-parses spanning the six selected pages.

The provisional dictionary for subsequent rapid iterations is:

```text
AIIN       registered unit/portion/index
DAIIN      take, assign, or record one AIIN-class value
S          begin/resume
Q          next/continue/link
D          select/assign/apply/connect
CH/CHE     describe, qualify, or prepare
SH         standing/result state
OKEE       repeat, maintain, circulate, or continue a standard process
OL         carrier/base/path/frame
AROL       conducting or connecting course
AL/AR      paired value/state classes
DY         licensed field commit when the formal parse supports it
B3         record commit
```

Unknown capitalized values remain untranslated local codes. The draft uses
German procedural paraphrases rather than pretending to recover original
spoken syntax.

This fixed draft creates a useful discipline even in YOLO mode: a later line
must either read coherently under this dictionary or force an explicit revision
with a named contradiction.

## Iteration 15 — Q is a construction state, not necessarily “then”

Two new lines were read without changing the Iteration-14 draft first. f10r.8
works reasonably as a continued descriptive record, but f83r.25 contains three
`q` constructions inside one field:

```text
qokeedy
// qolchey | qokeey | qokedy
// chedy | otal
```

If every `q` meant the spoken word “then,” the middle field would be an
unnaturally repetitive conjunction chain. The better analysis is:

```text
Q_LINKED_FORM(value)
```

`q` marks a value as belonging to the active/linked procedural construction.
Actual sequence comes from physical order and field boundaries. Post-DY
position strongly licenses this form but does not exhaust its use.

Revised dictionary entry:

```text
old: Q = "then/next"
new: Q = LINKED/ACTIVE construction state
     possible paraphrases: next, continue, associated, in the current process
```

The f83r.25 parse becomes:

```text
Q(OKEE); CLOSE
Q(OLCHEY), Q(OKEEY), Q(OKE); CLOSE
CHE(Y), MARKED_STATE(AL); LINE CLOSE
```

> Commit the linked OKEE process. In the linked field register OLCHEY, OKEEY
> and OKE, then close it. Describe Y and end in marked state AL.

This remains process-like but no longer mistakes a renderer/construction state
for an ordinary conjunction.

The f10r.8 line similarly begins with `Q(OT-CHOR)` and then lists several
CH-marked descriptors before `D(AIIN)` and `D(AR)`. It can be read as a
continuation of the preceding plant record even though no DY occurs on the
line itself.

### Updated control vocabulary

```text
S  line-entry/new-record realization
Q  active or linked-construction realization
D  binding/assignment realization
CH/CHE descriptive realization
SH standing/result realization
```

English sequencing words are now paraphrases of the complete construction,
not direct glosses of the wrapper glyphs.

## Iteration 16 — OKE is a graded state family

The f83r.25 sequence suggests a better analysis than lexical `OKEE = repeat`:

```text
Q(OKEE); CLOSE
Q(OLCHEY), Q(OKEEY), Q(OKE); CLOSE
CHE(Y), OT+AL
```

The same broad OKE family appears at different apparent lengths and closure
states inside one short record. Treat it as a graded technical state:

```text
OKE      state/process family at grade 1
OKEE     state/process family at grade 2
OKEEE    state/process family at grade 3
OKEEY    an open or value-terminated realization of the grade-2 family
```

`q` places the state in the active/linked construction and formal DY commits
the checkpoint. Thus:

```text
qokedy   ACTIVE(OKE, grade 1); COMMIT
qokeedy  ACTIVE(OKE, grade 2); COMMIT
```

The underlying dimension could be duration, concentration, heat, moisture,
iteration count, processing degree, or an ordinal class. The sidequest does
not choose among them yet.

### Process reading of f83r.25

> Begin from committed OKE grade 2. Introduce or associate OLCHEY and the open
> grade-2 value. Move to committed OKE grade 1. Record descriptor Y and final
> marked state AL.

This resembles a controlled state transition—possibly cooling, diluting,
reducing, settling, or changing treatment duration—rather than a list of
unrelated nouns.

### Revised technical lexicon

```text
Q      active/linked construction
OK     standard technical state/process family
E^n    relative grade within that family
DY     checkpoint commit
```

The earlier paraphrase “continue/circulate” is retained only as a possible
whole-cell effect of `Q(OKE-grade)`, not as the lexical meaning of OKEE.

This is a substantial simplification: one state family plus a scalar channel
generates many high-frequency forms while allowing lines to describe genuine
technical transitions.

## Iteration 17 — typed value vectors on the right

f82r.14 contains both `qokain` and `qokaiin` in the same physical line, and the
contrast survives ZL3b, IT2a, and RF1b. The intervening `deeedy` and `qokeey`
are also stable across the three readings. This makes an accidental spelling
variant less attractive inside the sidequest.

```text
r | olchy | qokal | chey | qokain | deeedy | qokeey | qokaiin | olchedy
```

Treat the right side as a compact typed value vector:

```text
A + I^n + N   quantity/index channel at grade n
A + L         categorical endpoint/state L
A + R         categorical endpoint/state R
E^n           process/duration/intensity channel at grade n
Y             compact terminator or local state channel
```

The full cell template becomes:

```text
CONTROL + LOCAL_HOST + VALUE_TYPE + VALUE_GRADE + COMMIT
```

Examples:

```text
qokain   Q_ACTIVE + OK + N_VALUE(grade 1)
qokaiin  Q_ACTIVE + OK + N_VALUE(grade 2)
qokal    Q_ACTIVE + OK + L_STATE
qokar    Q_ACTIVE + OK + R_STATE
shedal   SH_RESULT + ED + L_STATE
daldy    D_BIND + L_STATE + COMMIT
```

This is almost exactly what a compact technical notation needs: the same
operation or object code can be combined with a typed amount, route, endpoint,
or process grade without spelling a new ordinary word.

### Provisional f82r.14 reading

```text
R/OLCHY record head
Q(OK, state L)
CHE(Y descriptor)
Q(OK, amount/index grade 1)
D(process grade 3); commit candidate
Q(OK, process grade 2, Y realization)
Q(OK, amount/index grade 2)
OLCHE terminal state
```

Loose paraphrase:

> For R/OLCHY, use OK state L and descriptor Y; assign quantity/index grade 1;
> apply process grade 3 and then grade 2; set quantity/index grade 2; finish in
> the OLCHE state.

The line may encode a ratio, schedule, calibration, or sequence of treatment
levels. The crucial hypothesis is not a particular operation but that `AIN`
and `AIIN` are two values of one typed channel.

### Revised scalar architecture

```text
I-count channel  -> amount, count, dose, or ordinal
E-count channel  -> duration, intensity, concentration, or process degree
L/R channel      -> paired categorical alternatives
```

This provides a reason for multiple recurrent right families and for the
extreme near-neighbour structure without requiring phonological inflection.

## Iteration 18 — a complete semantic record schema

The current guesses can be assembled into one practical data model:

```text
ENTITY/REFERENT       supplied by plant, figure, vessel, or circle position
LOCAL_PART_OR_ITEM    page-local address code
QUANTITY_OR_INDEX     I-count channel
OPERATION/RELATION    Q/D/CH/CHE construction
PROCESS_GRADE         E-count channel
CARRIER_OR_PATH       OL/AROL family
RESULT_STATE          SH construction plus L/R/Y value
TIME_OR_CYCLE         circle slot and geometric state
COMMIT                DY/B3/line/record boundary
```

This is the first nearly complete answer to what a record could mean without
requiring recovered nouns.

### Section projections of the same schema

```text
HERBAL A
  IMAGE_ENTITY + PART/PROPERTY + CLASSIFICATION + UNIT

HERBAL B
  IMAGE_ENTITY + UNIT + PREPARATION + CARRIER + RESULT

BIOLOGICAL
  DEPICTED_NODE/PATH + TRANSFER + PROCESS_GRADE + RESULT_STATE

ASTRO/CIRCLE
  CYCLE_POSITION + BINARY/GEOMETRIC_STATE + LOCAL CONDITION KEY
```

The sections may be complementary reference tables in one technical system:
what material is used, how it is prepared or circulated, what state should
result, and under which cyclical condition the action is indexed.

### Canonical hypothetical workshop record

Invented underlying entry:

> For the plant shown here, take a grade-2 unit of the selected part. Prepare
> it in carrier OL at process grade 2. Transfer it through the AROL course to
> endpoint SY. Record result state ED-L. Use the cycle condition represented by
> the selected f69v slot.

Possible compiled text:

```text
daiin | cheol | qokeedy | darolsy | shedal
```

Additional timing is supplied by pointing to or copying the appropriate circle
key rather than spelling its ordinal in the prose.

Expanded procedural paraphrase:

```text
TAKE/ASSIGN UNIT(I-grade 2)
PREPARE IN CARRIER(OL)
ACTIVE PROCESS(OK, E-grade 2); COMMIT
TRANSFER THROUGH COURSE(AROL) TO STATE(SY)
RECORD RESULT(ED, L)
UNDER CYCLE CONDITION(slot geometry + local key)
```

### What “translation” now means in this sidequest

The likely recoverable first translation is not:

```text
Voynich word -> German word
```

It is:

```text
Voynich construction
  -> technical record operation and typed value
  -> page-local referent
  -> eventual natural-language paraphrase
```

Thus a useful partial translation might read “assign a grade-2 quantity,
process at grade 2, transfer through the depicted course, record result L” even
while the material and operation names remain unknown.

## Iteration 19 — AIIN is a parameter, not necessarily a dose

Across the selected pages, standalone `aiin` is mostly field-internal and
appears after several different constructions. `daiin` can occur at line entry
or internally. This weakens the concrete noun “portion” and strengthens the
abstract reading **registered value/parameter**.

The decisive workshop clue is f10r.7. All three readings preserve the adjacent
pair:

```text
dain | dair
```

They also preserve an earlier `daiin` in the same line. The line therefore
contains:

```text
D + A + II + N
D + A + I  + N
D + A + I  + R
```

This looks like a tiny typed parameter table:

```text
D           assign/bind/set
A           value introducer
I-count     relative grade
N/R         value type or channel
```

### Revised AIIN family

```text
AIIN  N-type registered value at grade 2
AIN   N-type registered value at grade 1
AIR   R-type registered value at grade 1
DAIIN set/bind N-type grade 2
DAIN  set/bind N-type grade 1
DAIR  set/bind R-type grade 1
```

In a recipe, an N-value may be paraphrased as an amount or dose. In a circle
table it may be an ordinal/index. In an apparatus record it may be a setting.
The abstract parameter role is shared; the concrete unit is supplied by the
page/register.

### Provisional f10r.7 reading

```text
dchy | qokchol | y/kchaiin | yty | daiin | cth | dain | dair | am
```

> Bind CHY and activate/associate OKCHOL. Register the Y/KCH grade-2 value and
> YTY. Set N-channel grade 2; for CTH set both N-channel grade 1 and R-channel
> grade 1; finish with AM.

This sounds more like a compact specification or comparison table than a
sentence. The plant image silently identifies what is being specified.

### Updated value model

```text
N-channel  scalar quantity/index/setting
R-channel  paired route/quality/category setting
L-channel  another categorical endpoint/state
E-channel  process intensity/duration grade
```

The channel names are anonymous transcription labels, not sounds or initials.

The best concrete gloss for `daiin` is now **SET VALUE N2**, with “take a
portion” retained only as a context-specific Herbal paraphrase.

## Iteration 20 — AM as a terminal result family (superseded)

**Superseded by Iteration 21.** This iteration incorrectly treated physical
line end as if it normally ended the complete statement/record. The observed
line-final pattern remains real in the tiny sample, but the semantic inference
"terminal result" does not survive paragraph-aware reading.

Within the selected f10r/f55v/f82r/f83r/f69v ZL sample, the exact forms
`am`, `dam`, `kam`, `sam`, `otam`, and `talam` occur seven times in total. All
seven are the last physical group of their line:

```text
f10r.7   ... dain | dair | am
f55v.3   ... aiin | ol | kar | am
f55v.5   ... daiin | chedy | talam
f55v.12  ... aiin | daiin | otam
f82r.11  ... qotal | chedy | kam
f82r.16  ... aiin | chey | racty | dam
f83r.10  ... aiin | chky | lal | sam
```

The best workshop interpretation is not another punctuation mark. Physical
line end already commits the record. `AM` instead carries a **terminal content
value**:

```text
AM      result, end product, final condition, or terminal value
D-AM    assigned/applied result
K-AM    K-class result
S-AM    resumed/new-state result
OT-AM   marked-frame result
T-AL-AM action/variant-L result
```

The prefixes remain speculative, but the shared line-final function is useful.

### Consequence for record syntax

```text
... PROCESS ... STATE ... AM_RESULT | LINE_COMMIT
```

This separates semantic result from grammatical closure:

```text
DY/B3/line end  = commit mechanics
AM family       = terminal value carried by the committed record
```

### Revised f10r.7 ending

```text
... D_SET(N-grade 2) | CTH | D_SET(N-grade 1) | D_SET(R-grade 1) | AM_RESULT
```

> Set the N2 parameter; for CTH set N1 and R1; record the final product or
> condition AM.

### Revised f82r.16 ending

```text
... S_RESUME | AIIN_VALUE | CHE(Y) | RACTY | D-AM_RESULT
```

> Resume with the registered N-value, describe Y and RACTY, and finish with
> the assigned/applied result state AM.

This is the first content-function guess in the microtheory supported by a
perfect positional pattern inside the tiny chosen sample. It may still be a
line-final formula or renderer class rather than “result” in semantics, but it
deserves priority over isolated object glosses.

### Current content hierarchy

```text
AM family    strongest candidate for terminal result/value
AIIN family  typed parameter/value
OKE family   graded process/state
OL/AROL      carrier/path relation
local hosts  unresolved materials, parts, operations, or states
```

## Iteration 21 — statements span lines; AM is a local checkpoint at most

The source-native paragraph flags overturn the preceding interpretation. For
the seven selected AM-family lines:

```text
locus      paragraph start  paragraph end
f10r.7          no              no
f55v.3          no              no
f55v.5          no              no
f55v.12         no              yes
f82r.11         yes             no
f82r.16         no              no
f83r.10         no              no
```

Only one of seven ends its paragraph. Five are internal lines and one begins a
paragraph. Therefore:

```text
physical line != complete statement
line-final AM  != demonstrated final result
```

The surviving workshop hypothesis is narrower:

```text
AM family = local carried state / checkpoint / line packet value
```

It could tell the next line which local state is current, close a subrecord
that is embedded in a longer paragraph, or simply belong to a line-final
renderer formula. `D-AM`, `K-AM`, `S-AM`, `OT-AM`, and `T-AL-AM` remain useful
formal variants, but their prefixes cannot yet be read as result modifiers.

This also changes f10r.7. It is not a self-contained instruction ending in
`AM`; it is one packet inside the paragraph running from f10r.6 through
f10r.12. Likewise f55v.3 and f55v.5 are two internal packets of the same
f55v.1--6 paragraph, while f82r.11 opens a paragraph and f82r.16 continues it.

## Iteration 22 — the likely unit is a multi-line procedural block

The revised invented compiler now has three nested levels:

```text
GROUP       local value, operator, item, or state
LINE        bounded packet / scribal row / partial clause
PARAGRAPH   complete practical record or multi-step statement
```

A plausible paragraph generator is:

```text
PARAGRAPH_START:
    establish depicted/local subject and initial state

CONTINUATION_LINE*:
    inherit subject/state
    add item, parameter, operation, path, or comparison
    optionally emit DY/AM-like local checkpoint

PARAGRAPH_END:
    commit the accumulated record
```

This makes the frequent absence of an explicit repeated subject economical:
the plant, vessel, body, or circle region supplies the referent once; following
lines inherit it. A line-initial `s`, `q`, `d`, or `o/ot` form can therefore be
a continuation-mode selector rather than a sentence-initial word.

### Revised sample reading: f10r.6--12

Instead of seven independent sentences, read the block schematically as:

```text
f10r.6   establish preparation/state for the depicted plant
f10r.7   bind CHY; register N2, N1, and R1 parameters; checkpoint AM
f10r.8   continue with a linked CHOR/CHOL carrier/path specification
f10r.9   add a second operation and commit a local DY field
f10r.10  continue in an O/OT-framed mode with an N2 value
f10r.11  specify another framed operation/path variant
f10r.12  close the block with ODAIIN/DAIIN and linked Q forms
```

This is not plaintext. It is a forward-coherent workshop reconstruction. Its
advantage is that it explains why subject words need not recur on every line,
why line entry has strong formal effects, and why a supposedly terminal `AM`
can occur long before paragraph closure.

### Current ranking after the correction

```text
MULTI-LINE INHERITED RECORD STATE       strongest architectural guess
AIIN / DAIIN typed parameter channel    useful provisional content channel
OKE repeated-E process/grade channel    useful provisional content channel
OL / AROL carrier/path family           useful but weak content hypothesis
AM terminal result                      rejected
AM local checkpoint/carried state       provisional
```

## Iteration 23 — paragraph-internal families behave like a shared workspace

Once the paragraph rather than the line is treated as the likely statement,
the selected Herbal blocks become more coherent.

In f55v.1--6, successive lines repeatedly reuse the same broad families:

```text
OKE / OKEE / OKEEE      process or state grades
AIIN / AIN              parameter values
DAIIN                   parameter assignment
CHEDY / CHEODY / OCHEDY descriptor-state variants
ODY / DY                local commits or carried states
```

That resembles six rows updating one shared preparation workspace, not six
sentences that independently name their subjects. In f10r.6--12 the recurrent
CHOR/CHOL, QOTOR and AIIN/DAIIN families similarly cross physical line breaks.

The workshop model can now be made more explicit:

```text
paragraph environment E = {
    silent pictured referent,
    current material/object,
    parameter vector,
    current process grade,
    carrier/path state,
    last checkpoint
}

each line:
    read inherited E
    emit a bounded sequence of updates
    write back modified E
```

Under this model, a short form at line end need not be punctuation or a final
object. It can be the value intentionally left "on top of the stack" for the
next line. This gives provisional functions to the architecture without
requiring every visible group to be a natural-language word.

### Stronger purpose guess

For the two Herbal pages, the text is best imagined as a compact technical
description plus preparation/use record attached to the pictured plant. Water
may be one locally supplied material or process medium, but the drawing alone
does not tell which group denotes it. For the Biological pages, the same
compiler records successive states/flows through a pictured apparatus. For the
circle pages, geometry supplies most identity and the text supplies compact
slot values.

The leading world therefore remains a **hybrid workshop register**:

```text
abbreviated local vocabulary
+ typed parameters
+ persistent paragraph state
+ image-supplied referents
+ layout-sensitive rendering
```

This is more coherent than either ordinary prose or a pure codebook, while
still leaving almost all concrete nouns and operations unresolved.

## Iteration 24 — f55v as two preparations for one depicted plant

f55v contains twelve lines divided source-natively into two six-line
paragraphs. Reading the paragraph as the record produces a more natural
workshop document than reading twelve separate sentences.

### Paragraph 1: f55v.1--6

The first line introduces several dense CHE/CKHY and DAIIN-like constructions.
The middle repeatedly cycles through OKE/OKEE grades, CHEDY variants, ODY/DY,
and AIIN values. The final line is unusually parameter-heavy:

```text
ykaiin | daiin | ykair | cheky | daiiny
```

Provisional record shape:

```text
line 1     identify plant part/preparation base and initial condition
line 2     begin graded treatment and introduce a measured value
line 3     continue at another grade; introduce carrier/state OL; checkpoint AM
line 4     repeat treatment of the same local part/state
line 5     set paired values and a prepared-state variant; checkpoint TALAM
line 6     summarize N/R-type parameters and close the paragraph
```

Fast natural-language paraphrase:

> Take the relevant part of the depicted plant in the stated initial
> condition. Treat it through the indicated grades in a carrier medium, adding
> the registered quantity. Repeat or continue the treatment, set the paired
> parameters, and leave the preparation in the indicated final local state.

This is invented, but it respects the actual multi-line recurrence better than
twelve unrelated glosses.

### Is `OL` water?

The most useful cross-section abstraction remains:

```text
OL    carrier / medium / channel
AROL  extended carrier-course / path
```

On a plant-preparation page, `OL` could concretely be **water**, oil, juice,
decoction liquid, or vessel contents. On a Biological apparatus page, the same
abstract role could be a conduit or flow path. The present sidequest therefore
permits the paraphrase "in water/the liquid medium" but does not bind `OL`
specifically to water.

### Paragraph 2: f55v.7--12

The second paragraph reuses AIIN/DAIIN, OK-, OTAR, AR, AL, OL, and CHE-like
families but changes their ordering. This is exactly what we would expect from
a second preparation, application, storage condition, or alternative method
for the same pictured plant.

Provisional shape:

```text
line 7      introduce alternate local state/part
lines 8--9  specify treatment and AR/AL relations
lines 10--11 accumulate carrier and parameter values
line 12     bind the last values in AR/OL context; close at OTAM
```

Fast paraphrase:

> Alternatively prepare or apply the same plant under the second condition.
> Use the specified carrier/path relation, add the indexed quantities in the
> stated order, and retain the final marked medium/state.

### Currier A versus B in the workshop theory

This yields a concrete explanation for the established architectural
difference without requiring two languages:

```text
Herbal Currier A  descriptive catalogue / identification register
Herbal Currier B  preparation, application, or dispensary record register
```

Both may describe plants, but B compiles more of the practical procedure into
short closed fields and repeated parameter updates. This is presently the best
sidequest-level interpretation of why the same broad formal vocabulary appears
in Herbal B and Recipe/Stars records.

## Iteration 25 — Biological paragraphs as reusable process programs

The complete f82r.11--19 paragraph repeatedly uses the same compact families
across nine physical lines:

```text
QOKEDY / QOKEEDY / QOKEEY / QOKEEEY
LCHEDY / OLCHEDY
CHEDY / SHEDY
QOKAIIN / OKAIN / AIIN
OL / OR / R
```

f83r.25--30 independently reuses QOKEEDY, QOKEEY, QOKEDY, CHEDY, SHEDY and
OLDY in another six-line paragraph. In the workshop story these are not names
of fifteen objects. They form a reusable process language applied to different
local diagrams.

### A bolder contextual vocabulary

```text
OKE                 standard transform/process
Q + OKE             execute or activate that process
E-count             process grade, duration, or intensity
DY                   commit the local process state
CHE                 prepare/qualify the current item or channel
SH                  treated/resulting realization of a comparable state
L / OL              carrier, vessel, medium, or channel
R / AR               route/relation/course selector
AIIN                 measured setting, amount, time, or ordinal
```

In the Biological register the most natural concrete paraphrases are:

```text
QOKEEDY   flush/bathe/circulate at grade 2, then checkpoint
QOKEDY    flush/bathe/circulate at grade 1, then checkpoint
LCHEDY    hold/settle in the channel or vessel, then checkpoint
SHEDY     resulting treated state, checkpoint
QOKAIIN   execute process with registered setting N2
```

"Water" is highly plausible as one physical medium on bathing/apparatus pages,
but these are contextual glosses. The abstract operation could also cover heat,
mixture, flow, immersion, or timed residence.

### f82r.11--19 as an invented nine-stage program

```text
11  initialize channel/device; execute standard process; retain KAM checkpoint
12  enter marked process; set conduit/path and local prepared state
13  transfer through OLCHE; repeat standard process; retain AROL course
14  load R/OL channel state; set grade and quantity parameters
15  cycle through K/LCHE/OKE states with several local commits
16  repeat standard process twice; bind R/OR/OL carrier; retain DAM checkpoint
17  execute several grades; leave RALCHEY local state
18  load carrier, resulting state, DAL relation and measured parameter
19  write final OKAIN/QOKEEDY/LCHY packet and close the paragraph
```

Fast paraphrase:

> Set up the indicated vessel or channel. Run the standard bath/flow operation
> through the listed grades, holding the material at the marked intermediate
> states. Set the recorded amount or duration, repeat the cycle where shown,
> transfer through the indicated course, and leave the system in its final
> local channel state.

### f83r.25--30 as a shorter related program

```text
25  execute several OKE grades; qualify state Y; set marked AL state
26  prepare marked channel; repeat OKE; enter resulting state and commit
27  set N1 parameter; prepare; process; record the same treated state twice
28  introduce N2 parameter; qualify; process; retain resulting OLDY state
29  carry forward SALCHE/OLDY state with a local exceptional value
30  reset/continue; execute OKE grades; close the paragraph
```

This repeated process inventory is the strongest reason to imagine a small
workshop with standardized procedural notation. The page image supplies which
vessel, body, pool, tube, or route is current; the text records what is done to
it and with which local settings.

### Cross-register contextual translation

The same abstract cell can receive a register-specific paraphrase without
changing its compiler role:

```text
Herbal       QOKEEDY = soak/extract/process at grade 2
Biological   QOKEEDY = bathe/flush/circulate at grade 2
Recipe       QOKEEDY = perform the standard operation at grade 2
Circle       QOKEEDY = execute/record the slot's grade-2 state
```

This is exactly the hybrid hypothesis: a small shared technical algebra plus
page-local vocabulary and image-supplied referents, not one universal English
word per Voynich group.

## Iteration 26 — what an apprentice scribe could actually learn in 1420

The theory must be learnable without statistics. A workshop scribe does not
know HPR2 coordinates or 1,676 abstract joint tuples. The useful empirical clue
is that 53 recurrent tuple types occur in all five powered registers and cover
about 45.4% of their events. The workshop can therefore have a small common
phrasebook plus register-specific additions.

### The imagined teaching sequence

An apprentice could learn the system in five stages:

```text
1. Learn the small pen-stroke/glyph inventory.
2. Memorize roughly fifty common complete forms as indivisible shorthand.
3. Learn four or five paragraph templates by copying model pages.
4. Learn a limited set of licensed variants around those complete forms.
5. Add the local plant, recipe, apparatus, or astronomical lookup list.
```

The system is **analogical but not freely generative**. This is important.
GDT003 found much formal compatibility but no advantage over strong string
statistics on unseen folios, and later work retained exact joint tuples rather
than freely recombining their apparent coordinates. In the workshop story the
scribe writes from remembered exemplars:

```text
known complete form
    + one familiar positional/rendering alteration
    + page-local value
```

He does not mechanically combine every possible prefix, host, and suffix.
That produces the observed mixture of obvious families, forbidden-looking
combinations, fossilized irregularities, and large register-local tails.

### The pocket grammar

The whole practical grammar could fit on one teaching leaf:

```text
A. The image or paragraph opening establishes the subject.
B. Do not repeat that subject unless it changes.
C. Each physical line adds one bounded packet to the current record.
D. Carry the current state across line breaks until paragraph closure.
E. Use an entry form to show whether a packet starts, resumes, or activates.
F. Use a known process/value form; modify it only by licensed analogy.
G. End a local field with its conventional checkpoint form.
H. End the complete instruction at the paragraph boundary.
```

The provisional signs in the sidequest phrasebook become workshop actions,
not dictionary words:

```text
s-form at line entry     open/reset a packet
q-form after checkpoint  reactivate/continue a licensed construction
d-form                   bind/set the following local value
ch/che-form              qualify or prepare a local item/state
o/ot-frame               select a carrier/process frame
I/E repetitions          choose a grade in a small value series
DY                       close or commit a local field
AM family                retain a line-edge/local checkpoint state
paragraph end            close the complete record
```

Only the first two renderer tendencies have solid formal backing in the main
project. The remaining functions are the invented scribe model.

### How several scribes remain mutually intelligible

The workshop needs shared conventions but permits personal hands:

```text
shared:
    paragraph templates
    common complete-form phrasebook
    order of process/value/carrier/checkpoint fields
    diagram ownership conventions

scribe-specific:
    stroke shape and ligature
    preferred abbreviation length
    which optional checkpoint is written
    local spelling/rendering variants
    density of explicit versus inherited information
```

A new scribe copies several approved model records before contributing pages.
He can read another hand because the construction order and common formulae
are stable even when the surface rendering differs.

### Currier A and B as learnable workshop registers

The simplest workshop explanation is not two unrelated languages:

```text
COMMON CORE       shared shorthand and record mechanics
REGISTER A        slower descriptive/catalogue expansion
REGISTER B        denser procedural/checkpoint expansion
SPECIAL CIRCLES   compact slot-table expansion
```

A scribe may specialize in one register, explaining hand/register
concentration, while still recognizing the common core. Recipe/Stars and
Herbal B look related because both favor the denser practical expansion.

### What this predicts inside the sidequest

If the theory is coherent, then:

1. Common forms should concentrate at structurally important packet positions.
2. Rare local forms should be surrounded by familiar common scaffolding.
3. A paragraph should remain readable after replacing rare forms with blanks:
   its process/parameter/checkpoint skeleton should survive.
4. Different scribes should vary more in surface realization than in paragraph
   architecture.
5. Apparent morphology should be productive only near frequent exemplars, not
   across the full theoretical grid.

These predictions fit the existing broad results much better than a perfectly
regular cipher or a freely productive agglutinative language.

### Leading historical picture

The current best imaginative reconstruction is a small technical workshop
around 1420 using a private or school-specific shorthand. Masters maintain
model leaves and local lookup lists; scribes encode illustrated plant,
preparation, apparatus, and calendar records using a shared packet grammar.
The system may abbreviate natural-language source notes, but its final page is
closer to a technical register than ordinary prose. It is learnable because
most grammar is construction order and recurrence, while difficult local
content is copied from exemplars rather than generated from first principles.

## Iteration 27 — the first apprentice phrasebook from the six pages

The six-page sample contains a compact exact-form core. This is preferable to
inventing a meaning for every rare family:

```text
form    occurrences  pages  line start / middle / end
AIIN        19          6          0 / 16 / 3
DAIIN       23          5          5 / 17 / 1
OR           9          5          1 /  7 / 1
DAR          5          5          1 /  2 / 2
CHEY        17          4          0 / 15 / 2
DY          16          4          0 /  8 / 8
AR          14          4          0 / 12 / 2
DAL         12          4          1 /  8 / 3
OL          11          4          0 /  8 / 3
S           11          4          3 /  8 / 0
SAR          7          4          2 /  2 / 3
```

This supports a learnable positional phrasebook. The scribe need not know a
modern grammatical label; he learns where a form belongs in a record.

### Pocket-card version

```text
AIIN   registered measure/setting/value; normally follows something
DAIIN  enter, assign, or add the registered value
CHEY   qualify/prepare the current local item or state
OL     carrier/medium/channel; Herbal concretization may be water/liquid
AR     route/source/course relation
OR     second relation or target channel
DAR    bind/apply/transfer through the AR relation
DAL    retain/settle/bind at the L-side state
S      open or resume a packet; never used as the final item here
SAR    resumed/marked AR-course state
DY     local checkpoint; often but not always at line end
```

The semantic words are invented. The positional distinctions are the reason
these guesses cohere:

```text
entry/control        S
local qualification  CHEY
value                AIIN
value assignment     DAIIN
carrier/relation     OL / AR / OR
applied relation     DAR / DAL / SAR
checkpoint           DY
```

### A 1420 teaching instruction

An imagined master might teach the apprentice:

> First copy the form that opens the row. Then copy the sign for the thing or
> process from the page list. If a quantity is needed, write AIIN after it; if
> the quantity is to be entered or added, use DAIIN. Write OL for the carrier
> line and AR or OR for its course. Use only the DAR/DAL variant shown in the
> exemplar. Put DY where the local operation is fixed, then continue on the
> next line until the paragraph is complete.

That instruction is simple enough to transmit orally and by model leaves.

### More concrete f55v.12 attempt

```text
daiin | ar | cheky | olkeechy | sl | ar | aiin | daiin | otam
```

Workshop parse:

```text
SET/ADD MEASURE
THROUGH COURSE AR
PREPARE LOCAL KY ITEM
IN OL-CARRIER WITH KEE/CHY STATE
RETAIN SL STATE
THROUGH COURSE AR
MEASURE
SET/ADD MEASURE
MARKED AM CHECKPOINT; PARAGRAPH END
```

Bold paraphrase:

> Add the measured amount. Prepare the KY material and carry it through the
> liquid medium—possibly water—under the indicated condition. Retain that
> state, apply the second measured amount, and leave it in the marked final
> condition.

This line genuinely ends its paragraph, so `OTAM` can be translated here as a
final retained condition even though the broader AM family is not a universal
statement closer.

## Iteration 28 — AR, OR and OL as a tiny relational case system

The immediate contexts of the short cross-page forms suggest that they are
more useful as relational particles or technical case tags than as names of
materials. They mostly occur between longer constructions; AR appears 12/14
times internally, OR 7/9, and OL 8/11.

The simplest learnable three-way system is:

```text
AR   course/source/instrument relation: through, from, by means of
OR   target/association relation: for, to, concerning
OL   containment/carrier relation: in, within, using the medium
```

These English alternatives are contextual paraphrases, not separate recovered
words. A scribe learns three relation signs:

```text
AR  path or means
OR  target or associated item
OL  containing medium or channel
```

### Productive-looking licensed compounds

```text
D + AR       apply/send/bind through the indicated course
D + AL       place, retain, or settle at the L-state
S + AR       resume along the current course
AR + OL      course through a carrier/channel
D + AR + OL  send/apply through the carrier course
```

This does not require all combinations to exist. The apprentice copies only
the compounds present on the model leaf.

### Re-reading `darolsy`

```text
darolsy
= D + AR + OL + S/Y
= APPLY + COURSE + CARRIER + TERMINAL LOCAL STATE
```

Bold paraphrase:

> Lead or apply it through the carrier/channel to the marked Y-state.

This fits its placement beside a FLOW-like structure on f83r without requiring
`AROL` itself to mean water. Water may flow in that channel; AROL is the
route-through-carrier construction.

The uncertain opposing reading around `sasoldal`/approximately `saroldal` can
then be understood cautiously as:

```text
S + (AR) + OL + D + AL
RESUME + COURSE + CARRIER + SETTLE/PLACE AT L
```

> Continue through the carrier and leave it at the L-state.

The uncertain transcription prevents treating the pair as a clean opposition,
but the workshop grammar can generate both constructions with a small number
of learned cells.

### f55v.10 under the relation system

```text
oaiin | ol | s | aiin | okaiin | oky | ytaiin | otar | y | kal | ykar | ol
```

Workshop parse:

```text
framed value N2
in carrier/medium OL
resume packet
value N2
OK process with indexed value
local OK/Y value series
marked AR course
local K/AL and Y/K/AR values
finish line in carrier OL
```

Bold paraphrase:

> In the current liquid or carrier enter the first measured value. Resume with
> the second indexed amount, perform the standard operation on the Y/K item,
> use the marked course, and leave the line's preparation in the carrier.

Because f55v.10 is paragraph-internal, the final OL is a carried medium state,
not the end of the complete instruction.

### Revised minimal grammar

```text
ENTRY        s / selected line-entry form
ACTION       q+licensed process, d+licensed assignment
ITEM/STATE   page-local complete form
VALUE        AIIN-family
RELATION     AR | OR | OL and licensed compounds
CHECKPOINT   DY or local AM-family realization
```

That is small enough for several scribes to share, yet expressive enough to
describe plant treatment, apparatus flow and circular slot records.

## Iteration 29 — the first complete apprentice formula: f83r.27

f83r.27 is unusually clean. ZL3b, IT2a and RF1b all give exactly:

```text
dain | chedy | qokeedy | shckhedy | shckhedy
```

All five are distinct source groups separated by definite spaces. The last
complete form is repeated exactly. This makes the line suitable as a model-leaf
exercise.

### Mechanical workshop parse

```text
DAIN          set/register N-type value at grade 1
CHE-DY        prepare or qualify the current item; checkpoint
Q-OKE-E-DY    execute the standard process at grade 2; checkpoint
SH-CKHE-DY    retain/record resulting CKHE state; checkpoint
SH-CKHE-DY    repeat the same resulting state or assign it to a second item
```

Abstractly:

```text
VALUE | PREPARATION-CLOSE | PROCESS-CLOSE | RESULT-CLOSE | RESULT-CLOSE
```

The exact content can vary while this formula remains teachable.

### Bold plaintext-style paraphrases

Process repetition reading:

> Set one unit. Prepare it. Apply the standard grade-two treatment. Hold the
> resulting CKHE condition twice.

Parallel-output reading:

> Set one unit and prepare it. Apply the grade-two process, then record the same
> treated condition for each of the two corresponding outputs.

The second reading is particularly attractive if the image supplies two
parallel figures, vessels, streams, or targets. The text need not name either
referent; repeating the same closed state assigns one code to both.

### Repetition as a scribal operator

A medieval workshop does not need a separate numeral or word for every small
multiplicity. It can use literal repetition:

```text
X-DY              set state X once
X-DY | X-DY       set the same state twice / for two parallel slots
```

This would explain otherwise odd adjacent identical labels and forms such as
repeated `daldy`: the code is repeated because the same instruction or state
belongs to more than one pictured object/slot. It is safer than assigning a
number value to any glyph.

### Distinguishing CHE and SH in the workshop grammar

The f83r.25--30 paragraph supports a useful asymmetric teaching distinction:

```text
CHE-family   pending/prepared/qualified current item or state
QOKE-family  active standard transformation
SH-family    resulting/treated realization
```

Thus the broad construction is:

```text
CHE(X)  ->  QOKE(grade)  ->  SH(X')
```

DY can close any of the three local cells. An open SH form may remain available
for another operation; SH...DY fixes it as a checkpoint.

This is still an invented semantics, but it explains several observations at
once: wrapper families, repeated identical forms, DY chaining, compact
Biological lines, and easy transmission between scribes.

### How the master teaches it

> The CHE form tells which prepared thing is active. Copy the QOKE form for the
> operation and choose its E-grade from the model. After the operation copy the
> corresponding SH form. Add DY whenever that entry is fixed. If two equal
> figures receive the same state, copy the closed SH form twice.

This is simpler than teaching sounds, declensions, or a one-to-one cipher.

## Iteration 30 — correction: learn whole state cells, not `SH = result`

The immediately following f83r.28 provides a useful adversarial test:

```text
ZL3b  saiin | cheeky | sheey | qokedy | shedy | oldy
IT2a  saiin | cheeky | sheey | qokedy | shedy | oldy
RF1b  saiin | cheeky | sheey | qokedy | edy   | oldy
```

The six source groups are definite-space separated in ZL, but the fifth group
has a real alternate-reading disagreement. Therefore the attractive rule
`SH = resulting state` is too strong.

### Revised principle

```text
wrongly simple:
    SH + HOST + DY = RESULT(HOST)

better workshop model:
    learn recurrent complete state cells such as
    CHEDY, SHCKHEDY, EDY/SHEDY, OLDY
    and place them in known construction slots
```

Some cells may be historically related or analogically patterned, but the
apprentice does not need to decompose them productively. This matches the main
project's failure to support free allomorph/coordinate recombination.

### f83r.28 as a state-transition packet

```text
SAIIN      resume/open with registered N2 setting
CHEEKY     current prepared KY item/state
SHEEY      initial local state cell
QOKEDY     execute standard grade-1 process; checkpoint
(SH)EDY    resulting/current EDY state; reading uncertain
OLDY       put/hold in OL carrier state; line checkpoint
```

Bold paraphrase:

> Continue with the registered setting and the prepared KY item in its initial
> state. Apply the standard first-grade treatment, record the resulting EDY
> condition, and carry it forward in the OL medium or channel.

Because the paragraph continues, `OLDY` is a line-carried state rather than a
complete-instruction ending.

### What remains of the f83r.27 formula

The sequence remains an excellent complete construction:

```text
DAIN | CHEDY | QOKEEDY | SHCKHEDY | SHCKHEDY
```

But the safe workshop lesson is now:

```text
VALUE-CELL | PREPARATION-CELL | PROCESS-CELL | STATE-CELL | STATE-CELL
```

not a universal morpheme equation. `SHCKHEDY` can be learned as one conventional
closed state form, exactly as a medieval abbreviation student memorizes a
whole suspension or ligature even when parts resemble other abbreviations.

### The learnability payoff

This yields a two-tier grammar:

```text
productive tier:
    paragraph/line/field order, state inheritance, a few renderer choices

lexicalized tier:
    complete process, value, carrier and state cells copied from exemplars
```

Several scribes can learn this easily. They share the productive construction
order and a central phrasebook, while rare or irregular complete cells remain
register- or master-specific.

## Iteration 31 — f83r.28--30 exposes the renderer as a scribal rule

The end of the f83r.25--30 paragraph gives the cleanest bridge between the
confirmed renderer and the invented workshop semantics.

```text
f83r.28  ... oldy
f83r.29  ... oldy
f83r.30  s | okeedy | qokeedy | qoky | saii
```

`OLDY` is stable at the end of both f83r.28 and f83r.29 in all three readings.
The final line then has a source-boundary disagreement:

```text
ZL3b  s | okeedy    (uncertain small space)
IT2a  sokeedy
RF1b  sokeedy
```

The joined/detached choice does not need a semantic difference. It is exactly
what a workshop renderer produces.

### The same base cell in two constructional positions

```text
line-entry position:       S + OKEEDY
after a DY-closed cell:    Q + OKEEDY
```

In f83r.30 they occur consecutively:

```text
S-OKEEDY | Q-OKEEDY
```

The master can teach this without translating either wrapper:

> At the beginning of a new physical row use the S realization of the licensed
> OKEEDY cell. When the next licensed cell follows a DY checkpoint, use its Q
> realization. Join or lightly detach the entry mark according to the house
> hand.

This fits the established renderer results much better than treating `s` and
`q` as ordinary words.

### Cross-line state inheritance

The repeated line-final `OLDY` now receives a simple record-level function:

```text
f83r.28  write OL carrier state to line boundary
f83r.29  preserve/write the same OL carrier state again
f83r.30  resume the process in a new physical row
```

Bold paraphrase of the three-line tail:

> Leave the prepared item in the OL medium. While it remains in that medium,
> perform the CHEY, QODY and KESD substeps and retain the same carrier state.
> On the next row resume the standard treatment, repeat the linked process,
> enter the QOKY value and close the paragraph with SAII.

The content names remain unknown, but the carried-state syntax is now much
clearer.

### Why multiple hands are expected

Different scribes can render the same abstract packet as:

```text
s | okeedy
sokeedy
```

without disagreeing about the record. This naturally produces varying spaces,
ligatures and transcription boundaries while preserving the construction.
The manuscript's notorious boundary ambiguity is therefore not necessarily
corruption; it may be an intended property of a shorthand in which entry marks
can be written free or bound.

### Updated minimal compiler

```text
INPUT STATE       complete learned cell, inherited from earlier line
LINE ENTRY        choose licensed S realization
LOCAL PROCESS     copy complete process/value/state cells
POST-CHECKPOINT   choose licensed Q realization after DY
LINE CARRY        repeat current carrier/state cell at row edge if needed
PARAGRAPH CLOSE   terminate the inherited workspace
```

This is the most historically learnable version so far: a phrasebook plus two
positional rendering habits and paragraph-level state inheritance.

## Iteration 32 — f55v must be read around the plant, not across it (superseded)

**Superseded by Iteration 33.** The visual observation of four text blocks and
drawing interruptions is valid. The inference that those blocks carry fixed
plant-part or column meanings is not justified.

Direct inspection of the official Yale f55v canvas corrects the earlier
paragraph reading. The page has four visible text blocks:

```text
upper left    | flowering crown | upper right

              large plant image

lower left    | stem/root zone  | lower right
```

Official canvas: `1006183`. The inspected 2200-pixel IIIF derivative has
SHA-256 `6d10a10138c833a8ed63dd8031bed97c1ae6b22ceac1243043dd71c3fdcf3182`.

The source-native `DRAWING_INTERRUPTION` occurs on f55v.1--5 and f55v.7--12.
It is literally the plant occupying the middle of the physical row. Therefore
the concatenated transcription order:

```text
LEFT SEGMENT <DRAWING> RIGHT SEGMENT
```

does not establish a sentence that runs left-to-right through the plant.

### Corrected reading order

The most plausible workshop order is column-local:

```text
upper-left column downward
upper-right column downward

lower-left column downward
lower-right column downward
```

Another possibility is paired row-by-row entries, but in either case the
drawing boundary is structural. The plant is the shared silent argument between
the two columns.

### Upper zone: likely two notes for the flowering part

The first six physical rows divide into:

```text
UPPER LEFT
f55v.1  kcheedchdy oedain chckhy
f55v.2  oeeed yteey okeedy qoaiin
f55v.3  qokeeey os ain qool al chedy
f55v.4  okar chckhdy cheody keeyfar al
f55v.5  qokaiin chaiin ykain ykan ody
f55v.6  ykaiin daiin ykair cheky daiiny

UPPER RIGHT
f55v.1  otoldaiin dodyd
f55v.2  okeody ykeesan
f55v.3  sar aiin ol kar am
f55v.4  ochedy qokain ody
f55v.5  daiin chedy talam
```

The longer left column looks like description plus preparation parameters; the
shorter right column looks like a compact parallel use, state, or dosage list.
Both are attached visually to the flowering/upper plant zone.

### Lower zone: likely two notes for leaf, stem, or root use

The last six rows likewise form two streams. The crucial tail is:

```text
LOWER LEFT
f55v.10  oaiin ol s aiin okaiin oky
f55v.11  ykaiin cheoar cheeky oldy
f55v.12  daiin ar cheky olkeechy sl

LOWER RIGHT
f55v.10  ytaiin otar y kal ykar ol
f55v.11  aiin okal oltchy or y orain
f55v.12  ar aiin daiin otam
```

The left column contains the clearest sequence compatible with putting a plant
part into a medium, preparing it, and retaining an OL-state. The right column
contains another parameter/relation sequence that may encode use, dose,
application, storage, or an alternative preparation.

### Corrected bold paraphrase

Lower-left stream:

> Enter the measured plant material into the liquid carrier—possibly water.
> Continue with the indexed amount, prepare the KY material, let or keep it in
> the carrier condition, then add the final measure along the indicated course.

Lower-right stream:

> For the corresponding application or second preparation, use the marked
> relation and Y/K values in the carrier. Add the registered quantity and leave
> it in the final marked condition.

This is still invented, but it respects the manuscript layout.

### Stronger workshop document model

The page is not simply:

```text
plant picture + prose underneath
```

It is:

```text
plant image as shared subject and spatial index
+ multiple local text streams attached to plant zones
+ paragraph/column templates
+ compressed process and value cells
```

A scribe learns to place the appropriate note beside the relevant plant zone.
Another scribe can understand it because vertical zone and column position are
part of the notation. This also explains why mechanically stitching physical
row fragments can create sentences the author never intended.

### Correction to Iteration 24

The earlier `f55v.1--6 = one preparation` and `f55v.7--12 = second preparation`
reading was too linear. Retain only:

```text
upper paragraph/zone = notes associated with upper/flowering plant region
lower paragraph/zone = notes associated with lower plant/root region
each zone contains at least two layout-separated streams
```

Preparation, use, dosage and water remain candidate contextual interpretations,
not established column labels.

## Iteration 33 — pre-drawn image, space-filling text

The simpler circa-1420 production model is:

```text
1. illustrator draws and colours the plant;
2. text scribe receives the already occupied page;
3. scribe fits the entry into the remaining parchment spaces;
4. lines stop at the drawing and may resume on its other side;
5. paragraph structure continues independently of the irregular line widths.
```

This chronology is an explicit sidequest assumption, not a codicological result
established here. It explains the page without assigning semantics to proximity.

### What the image licenses

```text
plausible:
    the page broadly concerns the depicted plant
    the drawing constrains available writing space
    the same paragraph may occupy several irregular blocks

not licensed:
    upper text = flower meaning
    lower text = root meaning
    left = preparation
    right = application/dosage
    drawing boundary = grammatical operator
    nearby group names the nearby plant part
```

The `DRAWING_INTERRUPTION` therefore becomes a **layout obstacle marker** in the
working theory. It may coincide with a logical break, but it does not create one.

### Reading-order consequence

For f55v and f10r we retain multiple possible orders:

```text
row-wise continuation around the drawing
column-wise continuation within a free text block
mixed order chosen by paragraph geometry
```

No semantic paraphrase may depend on choosing one of these without stronger
evidence. The earlier horizontal and column-wise translations remain examples
of possible readings only, not the preferred decoder.

### Revised workshop model

The image may still save the scribe from repeatedly naming the plant at page
level. But the text grammar itself is reconstructed from recurrence, paragraph
boundaries, source groups, line entry and DY behavior—not from which leaf,
flower, stem, or root happens to be closest.

This makes the production process simpler:

```text
shared page topic: depicted plant
text placement: available-space optimization
record grammar: learned phrasebook and paragraph templates
local visual ownership: unknown
```

For multiple scribes this is natural. The illustrator fixes the occupied
regions; each text hand wraps or blocks the record according to available
space and house convention. Variation in line length and drawing interruption
then needs no semantic explanation.

## Iteration 34 — a shared workshop card, not a single uniform vocabulary

The six-page ZL3b micro-sample contains three hands and three broad registers:

```text
hand 1: f10r                     Herbal A
hand 2: f55v, f82r, f83r        Herbal B / Biological
hand 4: f67r2, f69v              astronomical / circle material
```

An exact-form census gives the following forms in **all three hands**:

| form | total | hand 1 | hand 2 | hand 4 |
|---|---:|---:|---:|---:|
| `daiin` | 23 | 5 | 14 | 4 |
| `aiin` | 19 | 1 | 12 | 6 |
| `dy` | 16 | 4 | 3 | 9 |
| `or` | 9 | 2 | 6 | 1 |
| `dar` | 5 | 1 | 2 | 2 |

Several shorter forms also span all three hands, but their low complexity makes
them poor teaching-card evidence. Conversely, `chey`, `ar`, `dal`, `ol`, `s`
and `sar` occur in hands 2 and 4 in this sample but not in the one selected
hand-1 page.

This suggests a deliberately modest workshop model:

```text
MASTER CARD
    a small stock of highly reusable complete forms
    shared boundary and placement habits
    a few licensed positional renderings

REGISTER CARD
    additional complete cells useful for a particular document type
    copied paradigms and local formulae

SCRIBE HABIT
    ductus, joining, optional separation and abbreviation density
```

The apprentice therefore does not learn a huge dictionary or a clean
prefix-root-suffix grammar. The apprentice first learns perhaps a few dozen
frequent complete cells and how to place them in records. Less frequent cells
are copied from exemplars; recurring constructions allow analogical extension.
That is simple enough for several scribes while still producing strong local
register differences.

### What this changes in the invented reading

`AIIN/DAIIN` and `DY` remain good candidates for the **shared procedural
infrastructure**, because they cross the selected hands and registers. `OR` and
`DAR` may belong to the same shared card, although their support is much lower.
The richer `CHEY/AR/DAL/OL/SAR` system should no longer be treated as mandatory
universal grammar; in this sample it is a register-card possibility.

This is more economical than assigning every visible piece an invariant
meaning:

```text
same manuscript-wide infrastructure
+ register-specific stock formulae
+ hand-specific rendering habits
```

It also predicts that a new scribe can produce acceptable entries by copying
complete cells in the correct constructional order, without knowing how every
glyph sequence decomposes.

### Confound and ceiling

Hand and register are heavily confounded in this tiny selection: hand 1 has
only one chosen Herbal-A page; hand 2 supplies the selected Herbal-B and
Biological prose; hand 4 supplies both circle pages. The census therefore does
not separate scribal dialect from document register and does not establish the
invented value, checkpoint, relation or procedural readings. It only makes the
small-workshop learning model more concrete.

## Iteration 35 — the first teachable contrast: `AIIN` versus `D-AIIN`

The narrowest useful master-card contrast is the exact pair:

```text
AIIN      19 occurrences; 0 line-initial, 3 line-final
DAIIN     23 occurrences; 4 line-initial, 1 line-final
```

Both occur in all three selected hands. `AIIN` repeatedly follows short forms
such as `s`, `or`, `ar` and `sar`; `DAIIN` can itself open a line and often
precedes another constructional cell. The contrast is not absolute, but it is
simple enough to teach:

```text
AIIN       bare parameter/reference cell
D-AIIN     entered, activated or instruction-ready form of that cell
```

In the invented practical reading, the least committal paraphrase is:

```text
AIIN       “the registered item/value”
DAIIN      “enter/take/set the registered item/value”
```

“Value” may mean quantity, grade, duration, catalogue index or something else;
the sidequest does not choose among them. The important hypothesis is
constructional rather than lexical: `D` licenses the same familiar cell in a
more active or entry-like slot.

This would be easy for an apprentice because it is learned as one paired card,
not as a universal rule over every possible host. Other `D+X` forms can arise
by analogy, but they need not all have the same interpretation. The adjacent
`daiin aiin` on f67r2.43 and `aiin daiin` on f55v.12 also warn that the two
forms are not freely interchangeable spellings.

This remains an invented workshop convention. The positional skew is small,
the six-page selection is not an independent test, and GDT003 already prevents
promotion of a productive linguistic morphology from such formal pairs.

## Iteration 36 — `DY` closes a local unit, not necessarily an utterance

The exact standalone form `dy` occurs 16 times in the six-page ZL3b sample:

```text
line-final       8
line-internal    8
```

The eight internal successors are diverse:

```text
dy, chy, chodaiin, qokeedy, daiin, choaiin, ykey, chol
```

Only one begins with `q`. This makes two simple readings untenable:

```text
DY = sentence-final full stop             too strong
DY mechanically requires following q      false in this sample
```

The useful workshop rule is instead:

```text
DY = finish or checkpoint the current local cell;
     the record may stop, continue on the same line,
     or continue on a later physical line.
```

In the invented practical paraphrase, `DY` is closest to a tiny **done/next
notch** rather than a spoken word. It could be read operationally as “this
entry is complete” while leaving the containing procedure open. The doubled
`dy dy` at f10r.3 is then compatible with two adjacent closed slots, although
that particular explanation is especially weak.

This also sharpens the renderer model. `q` may be favoured in some post-DY
constructional states, as the main project found, but it is a stochastic or
licensed realization rather than the literal successor of every written
`DY`. An apprentice learns where a completed cell permits the next registered
form, not the deterministic string rewrite `DY -> Q`.

Thus the working hierarchy becomes:

```text
physical line       available writing packet
DY                   local cell checkpoint
paragraph/record     larger continuing instruction or entry
```

The invented gloss “done/next” remains shorthand for this structural behavior,
not a recovered English meaning or proof that `DY` is punctuation.

## Iteration 37 — `OR` is a link-like cell; `DAR` is not simply `D+OR`

The shared master-card candidates `or` and `dar` do not behave like the clean
`aiin/daiin` pair:

```text
OR       9 occurrences: 1 start, 7 middle, 1 end
DAR      5 occurrences: 1 start, 2 middle, 2 end
```

`OR` is strongly internal in this tiny sample. It precedes `aiin` twice and
appears literally doubled in f55v.9:

```text
... chey | or | or | aiin ...
```

That makes a link, relation slot or small connective card a useful sidequest
interpretation. It does **not** determine whether the relation would be read as
with, of, to, from, at, another column label, or no spoken word at all.

`DAR`, by contrast, is more boundary-skewed and is not visibly `D+OR`: the
surface forms differ in their middle element. The apprentice model should
therefore store it as a complete card:

```text
OR       small link/relation cell
DAR      registered whole relation or operation cell
```

The earlier temptation to derive every `DAR/DAL/SAR` form from a universal
`D/S + AR/OR` grammar is accordingly weakened. Analogy may help a scribe
remember the family, but historical resemblance, current formal segmentation
and current function need not coincide. This is exactly the kind of
lexicalized irregularity expected in a small workshop shorthand.

The repeated `OR OR` can be imagined as two relation slots, a repeated link, or
two separately copied codes. It is not enough to call `OR` “and”, and the
sidequest leaves that choice open.

## Iteration 38 — page-template pickup keys

The first visible family of a locus differs sharply by page. The most useful
comparison holds hand 2 constant:

| page | loci | Q | S | D | O | Y | other |
|---|---:|---:|---:|---:|---:|---:|---:|
| f55v | 12 | 2 | 0 | 1 | 4 | 3 | 2 |
| f82r | 45 | 9 | 6 | 9 | 10 | 0 | 11 |
| f83r | 55 | 5 | 28 | 7 | 6 | 0 | 9 |

The same hand therefore produces no S-initial locus on f55v but an S-initial
majority on f83r. This is better modeled as a page/construction template than
as a personal scribal dialect or one ordinary content word.

There is also a local architectural contrast on f82r. Its ten O-initial loci
average only 2.1 groups, whereas its other powered initial families average
roughly 5.2--9.1 groups. O-initial material there is strongly associated with
compact entries. This need not generalize to every page.

The invented apprentice card now contains five **pickup modes**:

```text
O    open or neutral compact entry
S    resume the locally active construction at a new locus/line
D    enter or assert the first registered cell
Q    attach the new packet to a licensed preceding/checkpoint state
Y    select an indexed or register-local entry type
```

These are deliberately operational descriptions, not word meanings. A scribe
chooses the pickup mode demanded by the page template and then copies the
appropriate complete cells. The same content cell may consequently surface
under different pickup modes without requiring five different lexical senses.

This yields a learnable production routine:

```text
1. identify the page/record template;
2. choose its licensed pickup mode;
3. copy or adapt the next complete cell sequence;
4. mark local cell completion with DY where required;
5. continue across physical lines until the larger record closes.
```

The circle pages are not treated as ordinary prose lines in this comparison:
their f67r2/f69v loci are array or radial inscription slots. Their strong O/Y
opening profiles may use the same pickup inventory, but that is only an analogy
until slot and prose behavior are compared on equal structural units.

The concrete labels open, resume, enter, attach and select remain invented.
The observed result is only that opening-family choice is strongly local to
page/construction type even within one hand.

## Iteration 39 — f83r.25–30 as one six-packet instruction

The pickup-key model permits a coherent non-line-bound reading of the six-line
f83r paragraph:

```text
25  QOKEEDY QOLCHEY QOKEEY QOKEDY CHEDY OTAL
26  OTCHEY QOKEEY QOKY TOL SHEDY QOKYLDDY
27  DAIN CHEDY QOKEEDY SHCKHEDY SHCKHEDY
28  SAIIN CHEEKY SHEEY QOKEDY SHEDY OLDY
29  SALCHEDY CHEEY QODY KESD OLDY
30  S|OKEEDY QOKEEDY QOKY SAII
```

The invented workshop parse is:

```text
packet 25   open a Q-rich registered operation sequence;
packet 26   continue it in an OT-framed variant;
packet 27   enter a DAIN parameter, close CHEDY and QOKEEDY cells,
            then write the same SHCKHEDY cell into two slots;
packet 28   pick up a registered SAIIN/CHEEKY state,
            execute the QOKEDY cell and carry OLDY forward;
packet 29   resume with the CHEEY/QODY/KESD cells and retain OLDY;
packet 30   resume OKEEDY in line-entry S rendering,
            continue with QOKEEDY, enter QOKY, and close at SAII.
```

As a deliberately speculative practical paraphrase:

> Open the standard sequence and pass through the listed CHEY/OKE stages. In
> the alternate OT setting repeat the registered stages. Enter the indicated
> parameter, complete the preparation and operation cells, and record the same
> resulting condition for two slots. With the next registered setting and
> item, perform the operation and retain it in the OLDY condition or medium.
> Continue the CHEEY, QODY and KESD steps while preserving OLDY. Resume the OKE
> operation, register QOKY, and close the complete entry.

If the page concerns a liquid-working process, `OLDY` could be a carried liquid
or water-compatible medium. It could equally be a non-liquid state, container,
channel, table column or purely formal carry cell. The paragraph structure does
not decide this.

The main gain is not the invented prose but the compact production grammar:

```text
OPEN PACKET → CONTINUE PACKET → PARAMETER/CHECKPOINT PACKET
            → STATE-CARRY PACKET → STATE-CARRY PACKET → CLOSE PACKET
```

This is learnable by copying a model paragraph. Its variable complete cells can
change while the six-packet scaffold remains familiar. No physical line has to
be a complete statement, and the pre-drawn illustration need only constrain
where the packets fit.

## Iteration 40 — literal duplication as a workshop instruction

The six-page sample contains nine immediate exact `X X` pairs:

```text
f10r.3     dy dy
f55v.9     or or
f82r.18    shedy shedy
f82r.29    qoty qoty
f83r.7     qoteedy qoteedy
f83r.27    shckhedy shckhedy
f67r2.73   ykchey ykchey
f69v.1     okar okar
f69v.3     oteey oteey
```

All nine duplicate pairs remain exact in ZL3b, IT2a and RF1b. They occur on
all six selected pages and in all three selected hands; five are the final two
groups of their locus. The convention is therefore broader than the particular
SHCKHEDY example.

The simplest apprentice rule is:

```text
X X = copy the same registered cell into the next adjacent opportunity
```

Depending on the record, a practitioner might understand this operationally
as “again”, “for the second parallel slot”, “repeat once”, or “the same value
for both”. The written system need not contain a separate word meaning twice.
Literal recopying is easy to teach, robust across scribes, and compatible with
both prose-like records and circular lists.

This revises the f83r.27 paraphrase. `SHCKHEDY SHCKHEDY` need not encode a
special plural ending or a semantic result morpheme. The whole registered cell
is simply deployed twice. Likewise `OR OR` may occupy two relation positions
without making `OR` equivalent to spoken “and”.

The rule remains formal and underspecified:

```text
supported sidequest function:     DUPLICATE_OR_REPEAT_CURRENT_CELL
not established:                  TWO, PLURAL, BOTH, AGAIN, EMPHASIS
```

Exact repetition also fits an organically learned workshop notation better
than a perfectly economical engineered code. A hurried scribe can repeat a
known cell rather than invoke an abstract iteration sign, and every colleague
can read the local instruction from the copied form.

## Iteration 41 — analytic packets and space-saving compact cards

The secure paragraph beginning at f83r.47 has a striking shape:

```text
47  otchdy | qokchdy | shedal
48  dal | cheol | lol | chdal | aiin
49  sol | daiiin | chedy
50  sasoldal
51  darolsy
```

The first three loci are analytic multi-cell packets; the last two contain one
long complete group each. Nearby surface material repeatedly exposes pieces
resembling `dal`, `ol`, `sol`, `chedy` and relation-family cards in separated
or differently joined realizations.

The simplest circa-1420 workshop explanation is **layout-sensitive
compilation**:

```text
broad writing space    write several registered cells separately
narrow/local space     join a licensed sequence into one compact card
```

The two compact forms need not be lexical words. They may be abbreviated
renderings of a construction that apprentices already know from the analytic
packets. Conversely, the separated forms need not be spoken words either;
spacing simply exposes the copied cells more clearly.

An invented operational parse is:

```text
47  initialize or qualify the local construction
48  list its DAL/OL/value cells explicitly
49  enter the SOL/value/CHEDY continuation
50  write the first compact construction card: SASOLDAL
51  write the second compact construction card: DAROLSY
```

If forced into speculative practical prose:

> Establish the local CH/DY construction. Enter the DAL and OL-associated
> cells with the registered value, then continue with SOL and CHEDY. In the
> remaining compact positions write the corresponding SASOLDAL and DAROLSY
> formulae.

This intentionally avoids deciding whether the final cards are products,
operations, states, labels, references or merely continuations fitted around
the pre-existing diagram. The image-first production assumption gives a direct
nonsemantic reason for joining: parchment width is locally unavailable.

The workshop grammar therefore gains a renderer rule:

```text
CELL₁ SPACE CELL₂ SPACE CELL₃
    may have a licensed compact realization
CELL₁+CELL₂+CELL₃
```

The license must still be learned from exemplars; arbitrary concatenation is
not allowed. This explains free/bound reuse without requiring ordinary lexical
word boundaries or fully productive linguistic morphology.

## Iteration 42 — `SOL` as a register-local construction head

The next secure paragraph, f83r.52--55, begins with a near-isomorphic pair:

```text
52  solkeey  | qekey | raly  | ol
53  solchkal | cheol | qotar | ol
54  daiin    | ol    | dain  | chey | ldalor
55  sol      | rtain | cthal
```

The two four-cell packets have the same outer template:

```text
SOL+VARIABLE | VARIABLE | VARIABLE | OL
SOL+VARIABLE | VARIABLE | VARIABLE | OL
```

This frame is stable across the three readings; only the internal f83r.53
`cheol/cheal` reading varies. In the same paragraph `sol` appears free on the
last line.

Across the entire six-page ZL3b sample there are 20 groups containing the exact
surface sequence `sol`. Eight are the complete free group `sol`, and 14 of the
20 SOL-bearing groups occupy locus-initial position. All are on f82r/f83r.
This concentration makes `SOL` a plausible **register-local construction
head**, rather than a universal manuscript-wide content root.

The provisional workshop card is:

```text
SOL [CELL...]       free head in ample space
SOL+CELL [...]      compact attached realization

operational role:   initiate a registered action on the following cell(s)
bold gloss:          take / prepare / process
```

The final `OL` shared by the two parallel packets may be a common carrier,
medium, destination, state, or simply a fixed fourth column. A liquid or water
medium is compatible with the invented practical reading but is not required.

A deliberately bold paraphrase of the paired packets is:

> Process or take the KEEY item with its QEKEY/RALY specifications in the OL
> medium. Process or take the CHKAL item with its CHEOL/QOTAR specifications in
> the same OL medium. Enter the shared OL and DAIN/CHEY settings, then issue the
> final SOL instruction for RTAIN/CTHAL.

This is not a translation of the unknown cells. Its useful claim is the
construction:

```text
ACTION_HEAD + variable arguments + invariant final slot
```

The same head can be detached or attached according to the licensed exemplar
and available space. An apprentice can learn that behavior without knowing a
phonetic value or decomposing every SOL compound productively.

## Iteration 43 — `SOL` has a constructional attachment gradient

The simple claim “SOL joins only to save space” does not survive its wider
sample distribution. Free-SOL lines average 6.88 groups; bound-SOL lines average
6.42. There is no useful global line-length separation.

Instead, f83r.20 and f83r.21 each contain both attachment states within the
same physical locus:

```text
20  solkeedy ... sol | cheeety ...
21  solkeedy ... sol | chedy ...       ZL3b/IT2a
21  solkeedy ... solchedy ...          RF1b
```

The initial `solkeedy` is consistently bound. `sol cheeety` is consistently
separate. The `sol/chedy` boundary is read both ways. This supplies a direct
attachment gradient:

```text
SOL | CHEEETY              detached
SOL | CHEDY ~ SOLCHEDY     variably perceived/joined
SOLKEEDY                   conventional bound card
```

The repaired workshop rule is therefore:

```text
SOL is a detachable construction head.
Its following host and construction slot license free, variable or fused form.
Available space may influence a marginal join, but does not determine the rule.
```

This is exactly the kind of system several scribes can learn. Common
head+operand combinations become memorized compact cards; less familiar or
wider-scope applications keep the head separate. Analogy can create intermediate
forms, and a physical boundary can be genuinely ambiguous to modern readers.

The bold operational reading remains:

```text
SOL = initiate the registered treatment/preparation of the next cell or span
```

Under that guess, f83r.20--21 contain a primary bound SOLKEEDY operation and a
later secondary SOL CHE... operation inside each packet. A loose paraphrase is:

> Perform the standard KEEDY treatment through the listed Q-stages; then apply
> the same treatment head to the CHEEETY/CHEDY component and continue with the
> remaining registered cells.

“Treatment” and “preparation” are still guesses. The defensible sidequest gain
is the free/variable/fused constructional behavior, not a recovered verb.

### Correction to Iterations 41--42

Space-sensitive joining remains a plausible local renderer, especially on
pages written around prior illustrations, but it cannot be the sole explanation
for SOL attachment. Host-specific lexicalization and constructional scope must
be part of the invented grammar.

## Iteration 44 — `OL` as a dependent carrier/object slot

The 11 exact free `ol` occurrences in the six-page ZL3b sample have the opposite
placement profile from SOL:

```text
locus-initial     0
locus-internal    8
locus-final       3
```

Its immediate left environments include:

```text
AIIN, OAIIN, OR, CHEOL, SAIN, SOL, RALY, QOTAR, DAIIN, YKAR
```

Thus `OL` is not a plausible general pickup key or action head. It behaves more
like a dependent registered object, carrier, medium, state, or destination that
different heads and relation cells can select.

The invented local constructions now read:

```text
SOL | OL ...          operate on / prepare the OL carrier or object
DAIIN | OL ...        enter or set the OL carrier or object
OR | OL ...           place OL in the current relation slot
... RALY | OL         close a parallel packet with OL as its fourth value
... QOTAR | OL        same fourth slot under a different internal specification
```

This gives the f83r.52--53 parallelism a simple head/argument shape:

```text
SOL+item | method/state | relation | OL
SOL+item | method/state | relation | OL
```

The bold practical gloss is **carrier or working medium**. On a plant or
biological page, that could readily be water, another liquid, oil, sap, a bath,
a vessel content, or a prepared substrate. The f69v circle occurrence of free
`ol` warns that the same formal cell may instead be a generic channel/ring field,
a register-rebound code, or a homograph. Therefore:

```text
useful invented class:     CARRIER_OR_OBJECT_SLOT
premature lexical gloss:   WATER
```

This is compatible with the small-workshop model. Apprentices need learn only
that OL occupies an argument/carrier position under several construction heads;
the actual referent may be supplied by the page register, illustration, or an
exemplar table rather than encoded by OL alone.

## Iteration 45 — `DAIIN | CHEY` as a reusable entry frame

Exact free `chey` occurs 17 times in the six-page ZL3b sample:

```text
locus-initial     0
locus-internal   15
locus-final       2
```

Like OL, CHEY therefore behaves as a dependent cell rather than a pickup head.
Its strongest local construction is the exact bigram `daiin | chey`, repeated
on two independent selected folios:

```text
f82r.21   daiin | chey | qol ...
f82r.23   daiin | chey | qokeeedy ...
f83r.3    daiin | chey | lchedy ...
```

All three occurrences preserve `daiin | chey` in ZL3b, IT2a and RF1b, while
the following cell changes. That is the expected shape of a reusable entry
frame followed by a variable continuation.

The invented workshop parse is:

```text
DAIIN        activate/enter the registered item or parameter
CHEY         current dependent item, material, class or setting
NEXT CELL    chosen operation/state/continuation
```

The bold practical paraphrase is:

> Enter or take the current CHEY item/setting; then perform the following
> registered operation.

This makes `DAIIN CHEY` more like a small “head + operand” construction than a
complete sentence. It can be embedded halfway through a longer packet and can
feed several different continuations.

CHEY itself should not yet receive one concrete gloss. Its circle occurrences
and diverse neighbors allow at least:

```text
current item/material
selected category
quality or preparation state
parameter value
generic entry cell rebound by register
```

For the workshop learner, this ambiguity is not fatal. The phrasebook can
teach `DAIIN CHEY` as a frequent construction while exemplar context supplies
the page-specific object. The formal construction can be stable even if CHEY
does not denote the same external thing in every register.

## Iteration 46 — `Q-OKE-E-DY` as a complete linked operation card

The selected ZL3b sample contains:

```text
qokeedy      21
okeedy        3
solkeedy      2
```

The 21 exact `qokeedy` occurrences are concentrated on f82r/f83r. Only three
are locus-initial and only one immediately follows a free standalone `dy`.
Consequently, the Q of QOKEEDY is not explained as the deterministic visible
successor of every preceding DY checkpoint.

The strongest small construction is f83r.30:

```text
s | okeedy | qokeedy | qoky | saii        ZL3b
sokeedy | qokeedy | qoky | saii           joined reading tendency
```

The invented compiler parse is:

```text
S       physical-line pickup/resume realization
OKEE    registered operation or process family
DY      complete/checkpoint that local cell
Q       link the following homologous cell into the active chain
QOKY    associated value/state card
SAII    larger local record closure
```

This yields:

```text
S | OKEE-DY       resume and execute one complete OKEE cell
Q-OKEE-DY         execute the linked/next homologous OKEE cell
```

A bold practical paraphrase is:

> Resume the standard OKEE treatment, then carry out the linked next instance
> of the same treatment; enter QOKY and close the local entry.

This is exactly the kind of formula an apprentice can memorize as a model line.
The placement prefixes and DY checkpoint are partly productive, while
`OKEEDY/QOKEEDY` remain common complete cards rather than proof of unrestricted
morpheme concatenation.

`solkeedy` is deliberately not forced into the same decomposition. It may be
SOL+KEEDY, S+OL+KEEDY, or a lexicalized whole card; the visible string alone
does not choose. The SOL attachment result from Iteration 43 applies only where
free/bound evidence actually licenses that boundary.

The useful sidequest class is therefore:

```text
LINKED_CHECKPOINTED_OPERATION_CELL
```

The words operation, treatment, same and next remain invented. GDT003 still
prevents treating this attractive local algebra as confirmed linguistic
morphology or as predictive evidence beyond ordinary Voynich string structure.

## Iteration 47 — `SAII` is not a closure; the AIIN operator card expands

The f83r.30 ending initially tempted the parse:

```text
qoky | saii = value/state + record close
```

The sample does not support that claim. Exact `saii` occurs only once. Exact
`qoky` occurs nine times and is locus-final only three times. Neither form is a
general closure marker on this evidence.

A more coherent local comparison is:

```text
f83r.20   ... qoky | saiin     locus-final
f83r.30   ... qoky | saii      locus-final
```

Exact `saiin` occurs five times: three locus-initial and two locus-final. This
two-edge distribution fits a carried/reference state better than a dedicated
ending. Together with the earlier AIIN/DAIIN contrast it yields a simple,
explicitly speculative apprentice paradigm:

```text
AIIN       bare registered reference/parameter cell
D-AIIN     enter, assert or activate that cell
S-AIIN     resume, preserve or carry that cell at a packet boundary
S-AII      possible locally shortened/rendered S-AIIN realization
```

This would give the S family a concrete constructional function without making
it a universal lexical prefix. It agrees with the independently useful
line-entry tendency: S can mark that an already active record state is being
picked up on a fresh physical packet.

The repaired f83r.30 paraphrase is therefore:

> Resume the OKEE cell, perform its linked Q-framed counterpart, and leave the
> QOKY setting under the carried S-AI(N) reference state.

It does **not** say that the paragraph or sentence ends there. The physical
locus ends; the larger statement may or may not.

The paradigm remains weak in ordinary evidential terms: SAIIN has only five
examples, SAII one, and GDT003 found no transformation algebra outperforming
strong string statistics. Its sidequest value is explanatory economy: the
same two pickup operations D and S now act on the widely shared AIIN card in
ways compatible with their observed boundary profiles.

### Correction to Iterations 39 and 46

Withdraw `SAII = larger record closure`. Retain only a QOKY+SAI-family local
tail and the possibility that SAI(N) carries or resumes the current registered
state.

## Iteration 48 — a two-column `QOK` workshop card

The larger AIIN-ending inventory is dominated by three forms:

```text
DAIIN       23 occurrences, 5 selected folios
AIIN        19 occurrences, 6 selected folios
QOKAIIN     17 occurrences, 3 selected folios
```

`QOKAIIN` is therefore not a rare accidental extension in this sample. It can
be compared directly with the 21 `QOKEEDY` occurrences. Five loci on f82r/f83r
contain both exact cards:

```text
f82r.15   QOKEEDY ... QOKAIIN
f82r.26   QOKEEDY ... QOKAIIN
f82r.28   QOKEEDY ... QOKAIIN
f83r.6    QOKAIIN ... QOKEEDY
f83r.14   QOKEEDY ... QOKAIIN
```

Four of the five put the EEDY card first. The sidequest can therefore give an
apprentice a small two-column paradigm without claiming ordinary morphology:

```text
registered family       checkpoint/process column    reference/value column
QOK                     QOK-EEDY                      QOK-AIIN
```

The operational reading is:

```text
QOKEEDY     perform or record the completed QOK-family operation/state
QOKAIIN     enter or retain its associated QOK-family parameter/reference
```

This makes the right-side material a **cell-type selector** in the invented
notation. `EEDY` packages a DY-closed process/state realization; `AIIN` packages
a registered reference/value realization. QOK identifies the shared local
family or row of the workshop table.

A bold paraphrase of the common order is:

> Carry out the QOK operation and then record its corresponding QOK setting.

The reverse f83r.6 order prevents a universal temporal rule. It may mean that
some templates state the parameter first, or that the two columns are not
temporal at all. The safer claim is paired availability inside the same packet.

This is learnable as a lookup grid:

```text
choose family row → choose process or reference column → add licensed pickup
```

The grid need not extend to every visible form, and the cells may be
lexicalized. GDT002's semantic-slot stop and GDT003's string-baseline result
still block promotion to a demonstrated linguistic paradigm. The sidequest
uses it only as a compact generative theory for a scribal notation.

## Iteration 49 — the sparse AIIN/EDY/EEDY workshop matrix

The QOK row is not isolated. Mechanical suffix matching in the six-page ZL3b
sample finds seven visible rows with an AIIN card and at least one EDY/EEDY
counterpart:

| row | AIIN | EDY | EEDY |
|---|---:|---:|---:|
| QOK | `qokaiin` 17 | `qokedy` 18 | `qokeedy` 21 |
| QOT | `qotaiin` 3 | `qotedy` 3 | `qoteedy` 7 |
| CH | `chaiin` 2 | `chedy` 22 | `cheedy` 1 |
| OK | `okaiin` 2 | `okedy` 2 | `okeedy` 3 |
| OT | `otaiin` 2 | `otedy` 4 | — |
| LK | `lkaiin` 1 | `lkedy` 3 | `lkeedy` 1 |
| SOLK | `solkaiin` 1 | — | `solkeedy` 2 |

This is a sparse lookup table, not a complete factorial system. That is a
feature of the workshop theory: common cells are memorized and analogy is
limited by licensed exemplars.

EDY and EEDY cannot be dismissed as mere spelling alternatives in the QOK row.
They co-occur in three loci. Most strikingly, f82r.15 contains all three QOK
cards:

```text
kedy | lchedy | qokedy | qokeedy | lkeedy | qokaiin |
dy | daiin | chdy | dy
```

The invented matrix columns are now:

```text
AIIN       registered reference, parameter or input form
EDY        base completed process/state form
EEDY       extended, second-stage or marked completed process/state form
```

The EEDY description is deliberately vague. It may mark duration, grade,
iteration, a second state, a different renderer or a conventional whole-form
contrast. No number value is assigned.

The generative workshop rule becomes:

```text
CELL := [licensed pickup/head] + REGISTERED_ROW + REGISTERED_COLUMN

ROW     := QOK | QOT | CH | OK | OT | LK | SOLK | ...
COLUMN  := AIIN_REFERENCE | EDY_BASE_DONE | EEDY_MARKED_DONE
```

Not every Cartesian combination exists. An apprentice learns the frequent
rows as a table and creates a new combination only by close analogy or from an
exemplar.

A bold f82r.15 paraphrase is:

> Record the K and LCH completed cells; enter the base and marked QOK states,
> then the marked LK state and the QOK reference setting. Checkpoint the row,
> enter the general reference, record CH, and checkpoint again.

The literal meanings of K, LCH, QOK, LK and CH are entirely unknown. The value
of the paraphrase is that it reads the packet as a sequence of table cells,
not as ten unrelated word-like tokens.

This matrix is the strongest current sidequest account of apparent word
composition. It remains a generative notation hypothesis, not evidence that
the rows are lexemes or that the columns are linguistic morphemes.

## Iteration 50 — free `S | AIIN` confirms a detachable carry operator

The six-page ZL3b sample contains four exact detached `s | aiin` sequences on
three pages:

```text
f55v.10   ol    | s | aiin | okaiin
f82r.16   ol    | s | aiin | chey
f83r.10   cthal | s | aiin | chky
f83r.33   sy    | s | aiin | sheekchy
```

This is additional to five exact fused `saiin` groups. Alternate readings vary
precisely at the attachment boundary:

```text
f55v.10   S | AIIN in all three readings
f82r.16   SAIIN in IT; S | AIIN in ZL/RF
f83r.10   SAIIN or attachment to the preceding cell in IT/RF;
          S | AIIN in ZL
f83r.33   SAIIN in IT; S | AIIN in ZL/RF
```

Thus the S-AIIN relation is not inferred from substring resemblance alone.
The source boundary itself oscillates while the construction survives.

This strengthens the apprentice card:

```text
AIIN       the registered setting/reference
D-AIIN     enter or establish a new setting/reference
S-AIIN     retain, resume or reuse the same/current setting/reference
```

The boldest useful gloss for S is now **SAME/CURRENT-CARRY**, not a sound or an
ordinary translated word. It explains why S is favoured at physical line entry:
the new writing packet resumes a state already active in the larger record.

The repeated cross-page frame `ol | s | aiin` then receives a concrete
sidequest reading:

> For the OL carrier/object, retain the same currently registered setting.

This fits plant/biological technical prose especially well if OL is a liquid,
water, vessel content or substrate and AIIN a quantity/grade/duration. It also
remains compatible with non-liquid values.

The construction is still not proof that S always means same. S may have other
licensed functions, and the exact external content of AIIN and OL is unknown.
The advance is the detachable operator behavior plus a single economical
functional interpretation that links free/bound spelling, line reset and state
inheritance.

## Iteration 51 — one compiler, three image-bound technical registers

Direct review of the already repository-bound official Yale views sharpens the
sidequest at page level:

```text
f82r/f83r    containers, tubes, bathing figures, streams and transitions
f67r2/f69v   radial/cyclic arrays with repeated inscription opportunities
f10r/f55v    a depicted plant supplies the page-level physical subject
```

This licenses a hybrid workshop system:

```text
shared formal compiler
    pickup modes
    registered row × AIIN/EDY/EEDY cell type
    DY local checkpoints
    free/bound renderer choices
    literal X X duplication

register-local binding
    Herbal: depicted plant + preparation/carrier/setting record
    Biological: body/apparatus + liquid/process/state record
    Circle: cyclic slot + parameter/state record
```

### Herbal sidequest reading

The image supplies “this plant” without requiring a repeated plant name. The
text may concentrate on what the workshop needs to do with it:

```text
DAIIN/AIIN       enter or reuse quantity, grade or preparation setting
OL               carrier or medium, plausibly including water
DY               finish the current local preparation cell
row matrix       select registered preparation/state variants
```

Thus a broad page paraphrase can be:

> For the depicted plant, record the prescribed settings and carrier; perform
> the listed preparation cells, retaining or replacing values as marked.

### Biological/bathing sidequest reading

The visible containers, tubes, baths, emissions and linked bodies make a
procedural or balneological register plausible:

```text
SOL              apply, treat, wash, bathe, pour or process
OL               bath/liquid/carrier/channel content
AIIN              amount, grade, duration or registered setting
EDY/EEDY          base versus marked/extended process state
Q                 link a homologous next process cell
S                 retain the currently active setting across a packet boundary
```

A broad paraphrase is:

> Apply the registered treatment through the depicted vessel or bodily path,
> using the indicated medium and setting; preserve, replace or repeat local
> states according to the copied cells.

Water is visually plausible here, but OL still need not lexically mean water.
The illustration may supply the liquid/bath interpretation while OL specifies
only a formal carrier slot.

### Astronomical/circle sidequest reading

The same compiler can be reused without action semantics:

```text
array position    supplies cyclic order and object ownership
AIIN              slot reference or parameter value
EDY/EEDY          alternative slot states or marked columns
D/S               set a new value versus carry the current value
X X               repeat the same value in the adjacent opportunity
```

A broad paraphrase is:

> At each radial position, enter the registered parameter or carry the previous
> one; select the appropriate base or marked state and repeat a cell where two
> adjacent positions share it.

### Leading sidequest architecture

This is now more coherent than either ordinary prose or a pure codebook alone:

```text
HYBRID TECHNICAL SHORTHAND
= image-bound silent subject
+ sparse tabular codebook
+ construction heads and carry operators
+ layout-sensitive free/bound rendering
+ limited natural-language-like sequencing
```

The same visible form need not have one external referent in every register.
What transfers is the compiler role; the illustration, page template and local
row table supply the content binding. This explains why universal gloss mining
has repeatedly failed while formal construction order remains strong.

## Iteration 52 — six-page saturation and frozen four-page extension

The remaining exact cross-folio transitions in the original six pages are:

```text
QOKEEDY → LCHEDY
SHEDY   → QOKEEY
QOKEEY  → QOKY
OR      → AIIN
YKAR    → OL
AR      → AIR
```

They add no new construction class. The first three are already instances of
the sparse row/cell matrix; OR→AIIN is already a relation-to-reference frame;
YKAR→OL and AR→AIR are content-pair candidates without enough variable-host
support. `YKAR | OL` appearing on both f55v and f69v is also a useful
counterexample to universal `OL = water`.

An exact cross-folio n-gram census finds only one three-cell construction beyond
trivial short-locus types:

```text
OL | S | AIIN
```

That construction is already incorporated. A coarsened AIIN/EDY/DY/relation
packet-skeleton search produces only generic one- and two-group classes, not a
new specific cross-folio record template. Further lowering the resolution would
manufacture agreement from line length alone.

### Six-page saturation decision

The following reusable rules have been extracted:

```text
1. image/page template supplies silent subject and register
2. O/S/D/Q/Y choose local pickup/rendering modes
3. sparse registered row × AIIN/EDY/EEDY cell matrix
4. D-AIIN introduces; S-AIIN carries/resumes a reference
5. SOL is a detachable Biological-register construction head
6. OL is a dependent carrier/object slot, not universally water
7. DY checkpoints a local cell, not necessarily a statement
8. X X duplicates or repeats a complete cell
9. statements/records can span physical lines
10. attachment can be detached, variable or lexicalized by host
```

No remaining six-page exact recurrence supplies a genuinely new rule rather
than renaming one of these. The original micro-corpus is therefore declared
**SIDEQUEST_SIX_PAGE_FORMAL_SATURATION**.

### Mechanically frozen extension pages

Before inspecting their forms, four additions are selected by physical/register
adjacency rather than attractive text:

| page | reason |
|---|---|
| f11r | next new Herbal-A physical folio after f10r |
| f56r | next new Herbal-B physical folio after f55v |
| f81v | closest preceding new Biological physical folio before f82r |
| f68r1 | intervening new circle/Astro physical folio between f67 and f69 |

The frozen questions are:

```text
Does the AIIN/EDY/EEDY sparse matrix recur?
Does detached/fused S-AIIN recur?
Does SOL remain Biological-register concentrated and head-like?
Does OL remain dependent but receive register-local visual interpretation?
Do DY checkpoints and X X duplication transfer?
Does any genuinely new construction survive at least two of the four pages?
```

No page is selected because it contains a desired form or image detail. f84 and
f84r remain excluded.

## Iteration 53 — extension metadata correction and Herbal-A formula

The frozen page selection is retained exactly, but its prereveal description
contained one metadata error: f56r is Herbal **A**, Currier A, hand 1, not
Herbal B. It is not swapped after exposure. The four-page extension is therefore
f11r (Herbal A/1), f56r (Herbal A/1), f81v (Biological B/2), and f68r1
(circle/hand 4).

One exact construction transfers especially cleanly:

```text
f10r.5   QOKCHY QOTCHOL | CHOL CTHY
f11r.3   QOTY | CHOL CTHY | DOR ...
f56r.15  TCHO TCHOL | CHOL CTHY
```

`CHOL | CTHY` is identical in ZL3b, IT2a and RF1b on all three folios. It is
not fixed to physical-line closure: it is internal on f11r. The three depicted
plants are visibly different, so the pair is unlikely to be the proper name of
one plant. In this ten-page workshop sample, exact `CTHY` occurs only on f10r,
f11r and f56r, while `CHOL` also occurs in the circle pages. The economical
scribe's reading is therefore:

```text
CHOL        a reusable carrier/content card
CTHY        an Herbal-A/hand-1 instruction or qualification card
CHOL CTHY   a standard plant-record construction
```

For a deliberately concrete sidequest paraphrase, `CHOL CTHY` can be read as
“enter the standard preparation for the usable plant material.” A carrier such
as water may belong to that preparation, but neither member is identified as
WATER. Currier A, hand 1 and Herbal register are perfectly confounded in these
three occurrences, so the formula could be a school/scribe rendering rather
than herbal content.

The page images reinforce only the silent-subject architecture. f11r has a
dense crown of leaves and blue flowers with its two text packets above the
drawing. f56r has spiny blue-green structures and a spiral upper growth, with
the writing fitted around the already drawn plant. The irregular line lengths
are therefore licensed as page layout, not sentence boundaries or plant-part
ownership.

## Iteration 54 — carry, checkpoint and override on f81v

The strongest Biological extension is the exact opening sequence on f81v.3:

```text
SAIIN | DAIIN | OLKEEDY | OKEDY | DYKAIN | SHEK | CHDY | DALAL | OLDY
```

All three readings preserve `SAIIN DAIIN`. Under the existing apprentice card,
this is a compact **carry then replace/set** transition: resume the inherited
AIIN setting, then enter the setting for the new packet. It is especially
plausible on a page whose drawing consists of repeated figures occupying
parallel compartments of a shared green enclosure: successive slots can reuse
a treatment setting and then override it locally. The picture supplies only
the repeated-stage interpretation, not ownership of either token.

A more reproducible transition crosses three pages:

```text
f11r.4   ... KCHY | DY DAIIN
f81v.4   ... DAIN | DY DAIIN | CHCTHY
f82r.15  ... QOKAIIN | DY DAIIN | CHDY DY
```

`DY | DAIIN` survives all three readings at all three loci. This extends the
workshop state machine:

```text
DY       checkpoint/commit the current local cell
DAIIN    write or activate the next registered setting/value cell
S-AIIN   inherit the current setting/value into the new packet
```

The useful correction is that `DAIIN` is not necessarily a verb meaning
“begin”. On f11r and f56r it often closes a short Herbal-A physical line; on
f81v it occurs nine times and always inside a longer Biological line. It is
better treated as a portable **set/value card** whose placement is determined
by the register's record template.

Literal duplication also transfers, but with a reading-sensitivity warning.
`SHOR SHOR` on f11r.5 is exact in all three readings. f56r.4 preserves a copied
`CHOR` realization but IT2a joins the first copy to preceding `QOT`; the three
f81v ZL duplicates are broken in at least one alternate reading. Thus `X X =
copy/repeat the complete cell` remains useful, while only f11r adds a secure new
instance.

## Iteration 55 — f68r1 object-label namespace

f68r1 separates two writing modes unusually sharply. Thirty-two of its 37 loci
are one-group diagram labels, and all 32 label surfaces are distinct in ZL3b.
Their initial families are concentrated in a compact namespace:

```text
O  9     OT 9     OK 6     CH/C 3     Y 3     D 2
```

The page therefore looks less like 32 miniature words or clauses than a copied
inventory of celestial/object cards rendered through a small set of pickup
families. One card, `OTOR`, appears both as the isolated label f68r1.26 and
inside the longer legend/prose locus f68r1.1 in ZL3b and IT2a. RF1b splits the
prose occurrence as `OT | R` but retains the label `OTOR`. Exact `OTOR` also
occurs in the Herbal and Biological micro-corpus, so it cannot safely be a
unique star name.

The workshop interpretation is narrower and more useful:

```text
isolated circle label   = object/value identifier card
same card in prose      = reference to or use of that registered card
O/OT/OK                 = dominant label-rendering/pickup families
```

This is the first clear extension-page example of a candidate code value moving
between a diagram label and a longer construction. It supports the hybrid
codebook-plus-compiler model, but not any astronomical name, sound, number or
translation.

## Iteration 56 — a transferred Biological two-card formula

One further exact sequence survives the old/new-page comparison:

```text
f82r.2   DCHEDY | QOLCHEDY QOKAIN | DY | QOKEEDY ...
f81v.17  ... SHEDY | QOLCHEDY QOKAIN | CKHY ...
```

`QOLCHEDY | QOKAIN` is intact in ZL3b, IT2a and RF1b on both folios. It pairs a
checkpointed QOL-family card with a QOK-family AI(N) card and therefore fits the
same economical workshop ordering already proposed for QOK E(E)DY and AIIN:

> execute or record the QOL process/state card, then supply the associated QOK
> setting/reference card.

This is a useful Biological-register template, not a translation. QOL and QOK
could instead be two opaque values whose order is fixed by a form. The important
advance is that the proposed row-by-cell system now predicts a repeated
**two-card construction** rather than only individual surface families.

f81v also supplies 15 exact free `OL` groups: fourteen internal and one at locus
start. This strongly preserves OL as a recurrent Biological carrier/object
slot, while the one start occurrence rejects the strict claim that OL can only
be dependent. In the workshop grammar it can head an elliptical packet when
the operation or current setting is inherited from the preceding record. The
green shared enclosure makes liquid or bath medium plausible at page level;
it still does not make OL the word WATER.

## Iteration 57 — ten-page saturation

After adding the four frozen pages, the exact cross-folio construction census
has produced only four genuinely new reusable observations:

```text
CHOL CTHY            Herbal-A/hand-1 standard construction
DY DAIIN             checkpoint followed by set/value card
QOLCHEDY QOKAIN      Biological two-card process/reference frame
OTOR label ↔ prose   diagram identifier card reused in a construction
```

The other old/new exact pairs (`SHEDY QOKEDY`, `CHEDY QOKEDY`, `DAL LCHEDY`,
`QOL OTAR`, and `CHEY QOL CHEDY`) either reduce to the existing matrix and
relation grammar or lose an exact boundary/form in at least one alternate
reading. f81v's three apparent ZL duplicate pairs likewise fail all-reading
stability. Lowering the match resolution further would simply rediscover DY,
EDY, AIIN or short line geometry.

### Best apprentice-level writing system after ten pages

The system a small workshop around 1420 could plausibly teach is now:

```text
PAGE CARD
    drawing supplies silent subject and document register

RECORD CARD
    optional S-AIIN carry-in or D-AIIN explicit set/value
    one or more registered ROW × CELL cards
    relation/carrier slots such as OL
    DY checkpoint between local cells
    literal duplicate when the same complete card is needed twice

RENDERING
    cards may be joined, detached or shortened by hand/register and available
    space; physical lines package writing but do not bound statements

REGISTER TABLES
    Herbal A: CHOL CTHY and short value-ending packets
    Biological B: SOL and QOLCHEDY QOKAIN process packets, frequent OL carrier
    Circle: mostly isolated O/OT/OK object/value cards plus short legends
```

This is simple enough for several scribes: learn a common layout/compiler deck,
then learn the permitted row cards for the register being copied. It explains
why the manuscript has strong recurrence and positional grammar but defeats a
single word-for-word dictionary. The current best overall guess remains a
**hybrid technical shorthand**, not ordinary continuous prose and not a pure
substitution cipher.

The content ceiling remains low. The plant pages may discuss water, decoction,
washing, drying, roots, leaves, flowers, quantities or timing, and the bathing
pages may describe liquids or bodily treatments. The present ten pages do not
select among those. No further exact recurrence in this micro-corpus changes
the grammar or supplies a defensible new content word. The expanded sample is
therefore declared **SIDEQUEST_TEN_PAGE_FORMAL_SATURATION**.

## Iteration 58 — correction: exact-form saturation is not page saturation

The preceding declaration is narrowed to the exact recurring n-gram census.
It was premature as a stop on paragraph-, record-, layout-, image- and
historical-document inference. The same ten pages remain active; no additional
page is admitted.

f81v supplies a sharp paragraph-scale mode switch:

| f81v prose block | groups | AIIN-family | exact DAIIN | EDY-ending | Q-initial |
|---|---:|---:|---:|---:|---:|
| paragraph 1, loci 1–9 | 88 | 16 | 8 | 12 | 7 |
| paragraph 2, loci 10–27 | 165 | 2 | 1 | 50 | 36 |

The first prose packet is dominated by AIIN/DAIIN setting or value cards. The
second nearly abandons them and switches to checkpointed EDY-family and
Q-linked cards. The best workshop reading is a two-part technical record:

```text
PARAGRAPH 1    establish materials, quantities, settings or apparatus state
PARAGRAPH 2    list operations, stages, transitions or observations
```

In loose German: “Zuerst die Ausgangswerte und beteiligten Träger eintragen;
danach die Abfolge der auszuführenden oder beobachteten Zustände.” This gives
the AIIN-versus-EDY column guess a paragraph-level consequence. It also explains
why DAIIN can close short Herbal lines but occur inside a Biological record: it
belongs to a setup inventory, not necessarily to sentence syntax.

The two prose blocks occupy the open area above the previously drawn large
pool. The image can motivate a bath, liquid-treatment or apparatus reading for
the record as a whole, but the paragraph split need not map to the pool's upper
and lower rows.

## Iteration 59 — the f81v tub/pool caption

The public human catalogue identifies f81v.28 as the page's single two-word
label of type “tubs or tubes”, positioned left of the large tub at the bottom.
Its alternate readings are:

```text
ZL3b   OTAIN OLKAL
IT2a   OTOIN OLKOL
RF1b   TAIN  OLKAL
```

The exact graphemic details vary, but the two-card `O/zero-TAIN | OLK-L` frame
survives. Exact `OTAIN` also occurs inside f81v.5's setup paragraph and
f82r.18's running Biological text, and is absent from the other eight workshop
pages.

This permits the first comparatively concrete image-bound sidequest gloss:

```text
OTAIN OLKAL    caption for this tub/pool/apparatus or its contents
OTAIN          candidate general bath/pool/vessel/apparatus class
OLKAL          candidate subtype, contained medium, treatment class or local ID
```

If forced to write an apprentice translation today, the label would be “the
OLKAL bath” or “bath containing/using OLKAL”. The direction of modification is
unknown: OLKAL could instead be the head meaning tub while OTAIN is a condition
or treatment. The robust layer is only shared Biological recurrence plus
independent tub-label ownership.

## Iteration 60 — the four Herbal pages are two-part illustrated entries

The extension pages reveal a page-level regularity that the exact-form census
missed. All four Herbal pages contain two prose packets around one previously
drawn plant:

| page | Currier / hand | first packet | second packet | visible arrangement |
|---|---|---:|---:|---|
| f10r | A / 1 | 43 groups | 49 groups | two blocks above the plant |
| f11r | A / 1 | 32 groups | 27 groups | two short blocks above the plant |
| f55v | B / 2 | 43 groups | 62 groups | two blocks interrupted by the plant |
| f56r | A / 1 | 49 groups | 54 groups | two blocks fitted around the plant |

This transfers across Currier A/B and hands 1/2. The economical page grammar
is therefore not “one sentence per line” but:

```text
DRAWN PLANT = silent entry heading
HERBAL BLOCK A = identification, qualities or description card set
HERBAL BLOCK B = uses, preparation, administration or dose card set
```

The alternatives within each block cannot yet be ordered. In particular, a
simple feature count does not sharply separate the two packet types, and the
closed Herbal paragraph-ordinal route found no predictive universal formal
profile. The useful result is the **two-part document template**, not a proof
that the first packet is DESCRIPTION or the second is PREPARATION.

This is historically plausible without being diagnostic. The British
Library's catalogue for the illustrated *Tractatus de herbis* in Egerton 747
describes plant/substance entries accompanied by an antidotarium and material
on doses, substitutions, weights and synonyms
(<https://searcharchives.bl.uk/catalog/032-001983805>). Penn's ca. 1400
*Erbario* likewise places medicinal-property and preparation notes around or
over plant images (<https://colenda.library.upenn.edu/catalog/81431-p3n87308d>).
Those comparators make a silent image heading plus compact technical modules a
credible workshop format; they do not identify either Voynich packet.

`CHOL CTHY`, which recurs exactly on f10r, f11r and f56r, now has a slightly
more concrete but still reversible workshop reading. Since `OL` behaves
elsewhere like a carrier/medium slot, `CHOL CTHY` may be an Herbal-A formula of
the form “with/in the registered carrier, perform the CTHY preparation”. A
bold apprentice could paraphrase it as “prepare/heat in water”, but WATER and
HEAT are deliberately interchangeable guesses: the exact evidence licenses
only a repeated hand-1 Herbal construction.

## Iteration 61 — three different astronomical data modes

The three circle pages should not be translated as one homogeneous list.

1. **f68r1 is an object-card field.** Its human inventory contains 29
   explicitly attached star labels; the 29 ZL surfaces are all different. An
   attached card such as `OTOR` also occurs in the page's longer text. This is
   compatible with individual catalogue identifiers or attribute bundles.
2. **f69v is a repeated state/value schedule.** Among its 28 ordered radial
   entries, `OKEOD` repeats at positions 14 and 18 in all readings, and at 27
   in ZL3b/IT2a with an RF1b split. A repeated card is awkward for 28 unique
   names but natural in a schedule where the same state/value can recur.
3. **f67r2 is a nested almanac.** It combines distinct 7- and 12-member human
   label arrays plus surrounding rings and prose. Most labels are unique; the
   apparent ZL `OKODAR` echo across the 7 and 12 rings is not stable in the
   alternate readings and is retained only as a warning against easy ring
   alignment.

One post-hoc f68 clue is worth preserving without promotion. For its nine
plain-O star labels, eight attached stars have seven rays and one has six. For
the nine OT labels, only three have seven rays, while four have six and two
have eight. The local one-sided exact tail for the 1/9 versus 6/9 non-seven
contrast is about .025 before any search correction. Thus O may be an
unmarked seven-ray renderer and OT a marked/nonstandard renderer **on this
folio**. This cannot be generalized: the direct star-label route has only one
owned folio, the feature was noticed post hoc, and O/OT occur throughout other
registers. It is a plausible example of how a compact card encodes
object-class plus local ID, not evidence that T means “six/eight rays”.

The conservative astronomical paraphrase is therefore “object catalogue +
cyclic state table + nested calendrical/almanac table”. KART001 already showed
that the relevant 7/12/28/30 cardinalities fit broad medieval
astrology/computus and are not geographically specific; its failed f69 lag-14
prediction also argues against a direct copied 28-night value table. Medieval
computistical diagrams routinely combine multiple cyclic schedules rather
than prose sentences—for example Walters W.73 is a small cosmographical
diagram compendium (<https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html>).

## Iteration 62 — OL/AROL as a Biological carrier-and-conduit vocabulary

The strongest content-bearing sidequest clue now comes from the independently
catalogued Biological labels, not from line statistics:

| page/locus | reading nucleus | independent visible ownership | OL present |
|---|---|---|---|
| f81v.28 | `OTAIN OLKAL` | label left of bottom tub | yes |
| f82r.10 | `OROL DAIN` / joined variant | cross-shaped tube | yes |
| f82r.35 | `DAROL` | left waterfall/flow label | yes |
| f82r.38 | `DARARY` | right waterfall/flow label | no |
| f83r.45 | `CHTOROL` | possible left tube end | yes |
| f83r.46 | `OLSAIIN` | possible right tube end | yes |
| f83r.50 | approx. `SAROLDAL` | left lower structure | yes, reading-unstable |
| f83r.51 | `DAROLSY` | right lower structure / spray | yes |

Seven of these eight labels from tub/tube/flow/apparatus micro-scenes contain
an OL sequence. This concentration is a real reason to keep a
Biological-register gloss alive, but it is not a clean word-to-picture binding:
the two f83 tube-end assignments are hedged, f83r.50 is only a nearby structure
label, f82's waterfall labels are spatial labels rather than proved nouns, and
earlier all-folio transfer tests rejected OL as a universal left/right marker.

The best unifying decomposition is now:

```text
OL       carrier / medium / conduit-class slot
AR       path / axis / relation slot
AR-OL    conduit, axis, stem or route through a carrier
D-AR-OL  activated/directed conduit or outgoing flow state
S-AR-OL  carried/return/source counterpart
DAL/SY   local endpoint or state selector
```

This is better than `AROL = water`. An axis/conduit abstraction can recur in
plant-root/stalk labels and in tubes, channels and flows; a water noun cannot
explain the plant and astronomical counterexamples. On f83r the tempting pair
is therefore not two translated phrases but two ends/states of one registered
conduit construction:

```text
approximately S-AR-OL-DAL    conduit/path in state DAL
exact         D-AR-OL-SY      conduit/path in state SY
```

The left member is transcription-unstable (`SASOLDAL` in ZL, approximately
`SAROLDAL` in IT, split in RF), while `DAROLSY` is stable. `DARARY` is the
important same-scene counterexample: if OL were obligatory for water/flow,
that label should contain it. The current theory instead permits different
channel/material classes under a shared D-AR relation.

## Iteration 63 — leading document theory: a medico-astrological workshop manual

The ten pages now support one more specific overall theory than “hybrid
technical shorthand” alone:

> A small workshop compiled an illustrated practical medical handbook. Plant
> pages register simples and their properties/preparations; Biological pages
> register baths, liquids, channels or treatment apparatus plus independent
> procedural prose; astronomical pages supply timing, classification or
> calendrical lookup tables used by the same practical system.

The shared writing system remains deliberately simple enough for several
scribes around 1420:

```text
1. picture or diagram supplies the silent subject and local register
2. choose a register-local row/card from a memorized table or exemplar
3. AIIN-like cells enter a setting, quantity, grade or registered reference
4. EDY/EEDY-like cells record completed/marked states
5. S carries or resumes; D sets, activates or selects; Q links a licensed cell
6. OL supplies a carrier/medium/channel argument; AR supplies a path/relation
7. DY checkpoints a local cell but does not end the statement
8. JOIN/SPACE and shortened forms fit the cards around the earlier drawing
```

The historical comparison is architectural, not identificatory. The
*De balneis Puteolanis* tradition organized therapeutic waters and baths in a
repeated illustrated medical genre
(<https://www.cambridge.org/core/journals/traditio/article/peter-of-eboli-de-balneis-puteolanis-manuscripts-from-the-aragonese-scriptorium-in-naples/C804287BB668512B4D019696E0B114C8>),
while medieval medical astrology tied astronomical cycles to diagnosis and
treatment timing. These traditions make a plant + bath/apparatus + almanac
compendium historically intelligible, but many Latin, Greek, Arabic and
vernacular technical compilations could supply the same broad architecture.

The leading theory beats its rivals abductively as follows:

| world | what it explains | main failure |
|---|---|---|
| ordinary encrypted prose | broad paragraph flow | labels, repeated card algebra and sharp within-page mode switches |
| pure technical notation | compact cards and diagrams | long paragraph texture and scribal variation |
| ordinary abbreviated medical language | paragraphs and formulae | unusually strong formal compatibility and register-local card inventories |
| **hybrid abbreviated language + codebook/notation** | all three modes with one teachable workshop system | still lacks any securely decoded lexeme or clause |

This is now the best sidequest theory, not a manuscript claim. Its awkward
facts remain decisive: GDT003 composition does not beat string baselines;
f69's direct lunar lag-14 prediction failed; OL and AROL occur outside water
contexts; the Herbal two packets lack a stable universal formal contrast; the
f68 O/OT ray clue is single-folio and post-hoc; and no image has yet supplied a
word-level referent that transfers independently.

## Iteration 64 — page-local keys bridge labels and prose

The strongest evidence that the prose and diagrams participate in one system
is not a global label dictionary. It is a repeated **page-local key** pattern:

| page | diagram/ring card | occurrence in longer text | reading status |
|---|---|---|---|
| f68r1 | `OTOR` star label | f68r1.1 | exact ZL/IT; RF splits the prose card |
| f69v | `OKEOD`, `OKEEY`, `OKODY`, `SAR` radial cards | outer text loci 1/3 | several exact per reading; boundaries vary |
| f81v | OTAIN-family tub label | f81v.5 and f82r.18 | exact within ZL; label varies in IT/RF |
| f82r | `OKAL` lower-figure label | f82r.6 and f82r.12 | exact in all three readings at all three loci |

f82r is the cleanest case. `OKAL` labels a position between a nymph and the
left waterfall in the lower figure, then appears once in the first prose block
and once in the second. The location does not decide whether OKAL identifies a
figure, stream, material, state or apparatus component. Its repeat nevertheless
supports a practical scribal rule:

```text
write a compact card beside the depicted item or slot
reuse the same card inside one or more prose instructions on that page
```

f83r is the counterexample: none of its four selected apparatus/structure
labels reappears exactly in its prose. f67r2 has only the very short `AIR` and
`AY` overlap between ring labels and outer prose, too weak to interpret. The
result is therefore a sparse reference channel, not a mandatory page key.
This agrees with GDT258's corrected architecture: diagram legends and
paragraph records are independent channels with only a minority of complete
groups shared between them.

In the invented workshop manual, `OKAL` is best treated as a **local registered
referent**. A loose f82 paraphrase can say “for the OKAL item/state, carry out
the following entries” without claiming that OKAL means WATER, WOMAN, BATH or
any other object. The important semantic advance is referential function at
page scale, not lexical content.

## Iteration 65 — real manuscript types make the combined document ordinary

The unified medical-astrological theory does not require an exotic cultural
package. Several catalogued medieval manuscripts combine nearly the same broad
genres:

| comparator | relevant contents | consequence for the sidequest |
|---|---|---|
| BL Egerton 747, ca. 1280–1350 | *Tractatus de herbis*, lunar calendar, antidotarium, doses, substitutions, weights and synonyms | plant, remedy, measure and lunar material can inhabit one medical volume |
| BL Add MS 5297, late 15th c. | calendars, lunar-change table with instructions, 171 herb illustrations and 330 chapters of properties/descriptions | an illustrated herbal and astronomical lookup apparatus can be one compilation |
| BL Add MS 29301, ca. 1420–30 | surgical diagrams, Zodiac Man, 68 plant drawings, *Circa instans*, regimen and recipes | the exact period supports image-led surgery/medicine, zodiac and herbs together |
| BL Harley MS 1736, 1446 and later | medical/veterinary recipes, lucky/unlucky days, *Astrologia medicorum*, seven planets and zodiac tables | practical recipes and astrological timing coexist in a working miscellany |

Catalogue records:

- <https://searcharchives.bl.uk/catalog/032-001983805>
- <https://searcharchives.bl.uk/catalog/032-002029027>
- <https://searcharchives.bl.uk/catalog/032-002020783>
- <https://searcharchives.bl.uk/catalog/040-002047567>

This literature comparison strengthens only the **document architecture**. It
does not show that the Voynich text is Latin, English, Italian, Georgian or any
other language; it does not identify the drawings; and it makes astronomical
material less geographically diagnostic, not more. The simplest historical
world is now a workshop medical miscellany or deliberately unified handbook,
not six unrelated treatises accidentally bound together.

## Iteration 66 — best loose page-level reading of the ten-page set

At the current ceiling, the most useful “translation” is a document-level
paraphrase rather than invented word-for-word prose:

| page | best loose workshop reading | main uncertainty |
|---|---|---|
| f10r | “For the depicted flowering simple: enter two compact technical notes; one includes the standard CHOL–CTHY preparation and several AIIN settings.” | either note could instead be identity, quality, synonym, locality, dose or use |
| f11r | “For the clustered blue-flowered simple: enter two short notes; repeat one complete SHOR card, checkpoint, and reuse the CHOL–CTHY construction.” | the duplicate may be emphasis, two applications or pure scribal copying |
| f55v | “For the broad-leaved rooted simple: place two longer modules around the drawing, carrying AIIN values and OL/AR relations across the spatial interruption.” | Currier-B vocabulary and image-shaped line breaks dominate; no part ownership |
| f56r | “For the spiral/spiny simple: record two modules using the Herbal-A construction deck, ending the second with a DAIIN setting.” | the striking spiral cannot be assigned a textual description |
| f67r2 | “Consult the nested 12- and 7-member almanac rings and their local legends; use the surrounding text for the rule or interpretation.” | no authorial start, direction or value mapping |
| f68r1 | “Register 29 individual star/object cards; distinguish local marked variants and refer to at least OTOR in the accompanying legend.” | identifiers versus attribute bundles; O/OT ray clue is post-hoc |
| f69v | “Read a 28-position alternating radial schedule whose state cards may recur; the outer text explains or invokes several of those cards.” | LONG/SHORT has no textual marker and the schedule is not proved lunar |
| f81v | “Set up the material/apparatus/value inventory, then execute or record a much denser process/state sequence; the bottom tub bears the OTAIN–OLKAL key.” | setup/process is inferred from the sharp paragraph mode switch |
| f82r | “Describe three stages or aspects of a bath/apparatus system; label its lower figures/flows, and reuse OKAL as a local key in two prose blocks.” | paragraphs need not map one-to-one to upper/lower image regions |
| f83r | “Give five main procedure blocks plus two local apparatus blocks; identify paired conduit endpoints/states with the AROL construction.” | the local labels do not exactly recur in prose and one paired reading is unstable |

Nothing here requires a statement to end at a physical line. The scribe copies
cards and clauses through available pockets around a pre-existing drawing;
paragraph initials and paragraph ends are stronger discourse boundaries than
line ends, while DY remains a local cell checkpoint inside them.

## Iteration 67 — f83 separates procedural prose from apparatus-local text

The five large f83r prose paragraphs and the two small blocks written inside
the lower apparatus provide an internal mode comparison on one folio:

| f83 mode | groups | EDY-ending | contains OL |
|---|---:|---:|---:|
| five main prose blocks | 314 | 134 (42.7%) | 34 (10.8%) |
| two apparatus-local blocks | 27 | 3 (11.1%) | 10 (37.0%) |

This is a large descriptive reversal, though post-hoc and confined to one
page. It strengthens a division of labour:

```text
EDY-rich main prose       process, outcome or successive state recording
OL-rich apparatus prose  carriers, channels, media or local component relations
```

The final local block is particularly compact:

```text
f83r.52  SOLKEEY | QEKEY | RALY | OL
f83r.53  SOLCHKAL | CHEOL | QOTAR | OL
f83r.54  DAIIN | OL | DAIN | CHEY | LDALOR
f83r.55  SOL | RTAIN | CTHAL
```

The first two lines form a clear local parallel: `SOL + variable material`,
two variable relation/state cells, and final `OL`. Across the f82/f83 sample,
the only two lines ending in exact free `OL` are these two adjacent SOL-initial
lines; eleven other SOL-initial lines end differently. This licenses a local
construction, not a universal syntax.

Earlier iterations tentatively called SOL an ACTION head. The apparatus-local
concentration forces a broader and better guess: SOL is a **Biological
construction head** that can introduce an operation, component or treatment
entry. In a recipe-like reading the two lines say “process/use KEEY … in OL”
and “process/use CHKAL … in OL”; in an apparatus-list reading they say “SOL
component KEEY … OL” and “SOL component CHKAL … OL”. The data do not choose
between verbal instruction and nominal specification.

## Iteration 68 — geometry carries data that the writing need not repeat

The three circle pages make the compiler easier to teach because part of every
entry is already supplied by geometry:

```text
f67r2: ring membership supplies 7-system versus 12-system and local slot
f68r1: the depicted star supplies ray/core/location attributes and object slot
f69v: radial order supplies 1..28 position and LONG/SHORT supplies a binary bit
```

F69LS001 found no reliable text feature distinguishing LONG from SHORT. In the
workshop theory this is expected rather than embarrassing: the geometry is the
binary field, while the written card records some other attribute. The
complete f69 cell is therefore:

```text
radial ordinal + visible LONG/SHORT state + opaque written value card
```

Likewise, f68's ray count need not be fully spelled out, though the post-hoc
O/OT association suggests that the written card may redundantly mark an
exception class. f67's 7/12 membership need not be encoded in every label
because the ring supplies it. This **silent-coordinate principle** also
explains the Herbal and Biological pages: the plant, tub, figure or channel can
serve as a silent argument while the text supplies properties and operations.

It follows that a word-for-word decipherment is structurally the wrong first
target. A surface group can be only the written residue of a larger cell whose
other coordinates are image, ring, position, paragraph and current carried
state. The system still permits natural-language fragments in the long prose;
it merely predicts that isolated labels are intentionally incomplete.

## Iteration 69 — an apprentice's teachable grammar and current card lexicon

A master could teach the current ten-page system without teaching 1,676
independent “words”:

```text
PAGE RULE
  identify the picture/register and its silent subject

BLOCK RULE
  start a new paragraph card; do not restart at every physical line

ENTRY RULE
  [carry S / explicitly select D] + registered content card
  + zero or more relation/value cards + optional local checkpoint DY

LINK RULE
  after a licensed checkpoint, Q selects a linked/homologous card

LABEL RULE
  write only the local identifier/attribute bundle beside its visible owner

COPY RULE
  repeat X literally when the same complete cell is required twice

LAYOUT RULE
  join, detach or shorten licensed pieces to fit the earlier drawing
```

Within the ten-page ZL surface alone, the exact free cards are frequent enough
to memorize as a small practical deck: `DAIIN` 43, `CHEDY` 31, `SHEDY` 30,
`OL` 26, `DY` 22, `AIIN` 21, `QOKEEDY` 21, `QOKAIIN` 18, `CHOL` 12, `OKAL`
8, `SOL` 8, `CTHY` 7, and `OTAIN` 3. Compounds and alternate readings add
further realizations. Counts do not prove meanings, but they make a shared
exemplar/card system plausible for multiple scribes.

The current deliberately concrete vocabulary is ranked as follows:

| card/construction | best provisional function | status |
|---|---|---|
| `DY` | local checkpoint/cell closure, not sentence end | strongest structural guess |
| `S-` | carry/resume current licensed state at line entry | renderer-supported, meaning invented |
| `D-` | explicit select/set/activate counterpart | provisional |
| `Q-` | linked/homologous lookup after a checkpoint | renderer-supported placement, meaning invented |
| `AIIN` family | registered setting/value/quantity/reference cell | provisional but distributionally useful |
| `EDY/EEDY` family | process/result/state cell with grades or marked variants | provisional |
| `OL` | Biological carrier/medium/channel slot; broader carrier elsewhere | strongest content guess |
| `AR-OL` | axis/conduit/path over that carrier | abductive cross-domain guess |
| `SOL` | Biological construction head for operation/component/treatment entry | provisional, verb versus noun unresolved |
| `OTAIN OLKAL` | local tub/apparatus label | image-owned phrase, internal roles unresolved |
| `OKAL` on f82r | page-local registered referent | strongest anonymous reference function |
| `CHOL CTHY` | repeated Herbal-A preparation/qualification construction | exact form, content weak |
| `OKEOD` | repeatable f69 cyclic state/value card | schedule role plausible, value unknown |

This lexicon is intentionally functional rather than phonetic. A five-scribe
workshop can learn it as a shared grammar plus register-specific lookup sheets,
with individual hands choosing slightly different joins and surface variants.
That is simpler than requiring every scribe to encrypt ordinary prose letter by
letter while independently reproducing the same positional restrictions.

## Iteration 70 — a concrete hydraulic microdictionary

The f82/f83 labels permit one deliberately bold, internally coherent reading.
On f82r two independently catalogued left/right waterfall positions carry:

```text
left   DAROL
right  DARARY        (IT: DARYRY; RF: JARARY)
```

The repeated `D-AR` frame is more informative than either ending. The two
visible objects are the same broad class but differ in rendering: the left is
a broad/wavy fall and the right a narrow vertical fall. A workshop copying
hydraulic diagrams could therefore use:

```text
D-AR          active outflow / discharge-path construction
OL            channel or sheet-medium subtype
ARY           alternate outlet/stream subtype
```

f83r adds a second local opposition:

```text
approximately S-AR-OL-DAL    left/source/base construction
exact         D-AR-OL-SY      right/outflow/spray construction
```

Here the `S` versus `D` contrast fits the global renderer intuition unusually
well: S carries or resumes an incoming/current state; D explicitly activates
or selects an outgoing state. `DAL` can then be a basin/base/reservoir state,
while `SY` can be a spray/release/terminal state. The right-hand lower
structure visibly emits a dotted spray, making the following apprentice
translations maximally coherent:

| locus | bold workshop paraphrase |
|---|---|
| f82r.35 `DAROL` | “active outflow through the OL channel” |
| f82r.38 `DARARY` | “active outflow through the ARY outlet” |
| f83r.50 approx. `SAROLDAL` | “incoming/return OL conduit to the DAL reservoir” |
| f83r.51 `DAROLSY` | “discharge the OL conduit in the SY spray state” |

This is the best current content microtheory, but its weaknesses must remain
attached to it. The f82 labels are proximity-owned; the right reading varies;
the f83 left form is unstable; the states were inferred from the same pictures
being explained; and earlier transfer tests rejected a universal OL
left/right marker. The theory is therefore a **local hydraulic legend**, not a
dictionary for the manuscript. A safer statement is only that D/S plus AR/OL
and right-edge variants differentiate related visible flow constructions.

The f81v caption completes the local vocabulary without fixing direction:

```text
OTAIN OLKAL    the OTAIN-class vessel/bath with OLKAL contents or subtype
```

Together, the five bold label readings form a tiny apparatus legend that an
apprentice could copy from a model sheet. They are more useful than calling
OL “water”, because water is supplied by the drawing while the written cards
differentiate vessel, channel, outlet and state.

## Iteration 71 — Biological paragraphs as a variable bath/site record package

The three Biological pages do not have one paragraph per depicted figure:

| page | main prose blocks | local apparatus blocks | selected labels |
|---|---:|---:|---:|
| f81v | 2 | 0 | 1 two-card tub label |
| f82r | 3 | 0 | 13 figure/flow/tube labels |
| f83r | 5 | 2 | 4 selected tube/structure labels |

This matches the readable *De balneis* calibration better than a rigid recipe
template. GDT211's 32 bath records all had an identity and indication, while
location/access, hydraulic description, procedure/caution and outcome were
optional. GDT212 further found that pictures weakly expose setting/access and
hydraulic organization but do **not** reliably expose indication, procedure or
outcome. Applied as a sidequest model, the likely page package is:

```text
silent page subject: named spring, bath, apparatus or treatment complex
optional prose modules:
  identity/site or class
  access/setting
  hydraulic/physical properties
  medical indication or body condition
  preparation/procedure/caution
  result/testimony
local labels:
  depicted vessel/channel/flow/component cards
```

The paragraph count can vary because modules can be omitted or combined. This
also explains why the f81 two-block mode switch can be setup→process while f82
needs three long blocks and f83 five: they need not encode identical roles or
the same number of patients. The illustrations chiefly ground the hydraulic
layer; much of the actual medical payload may be invisible in the pictures.

The best loose page readings become:

```text
f81v  compact bath/apparatus entry: setup inventory, procedure sequence, vessel key
f82r  fuller bath/site entry: three prose modules plus a labelled hydraulic/figure tableau
f83r  extended bath/apparatus entry: five prose modules plus a locally specified flow circuit
```

This makes “Biological” a modern visual label rather than the document's
necessary genre. The pages can be balneological, therapeutic, hydraulic,
alchemical or a hybrid; the variable illustrated medical-record architecture
is the stronger inference.

## Iteration 72 — Herbal incipits are candidate entry addresses, not sentences

The first prose packet on each plant page begins with a different construction:

```text
f10r  PCHOCTHY ...
f11r  TSHOL ...
f55v  KCHEDCHDY ...
f56r  O | CHAL ...
```

Their line-entry surfaces are unique in the ten-page set and visibly share
pieces with common body families (`CTHY`, `SHOL/OL`, `CHEDY`, `CHAL`). A
scribe-like reading is that the incipit carries the plant entry's local address
or first descriptive class through an ornamental/positional renderer. It need
not be a spoken plant name, and the drawing already makes a written title
optional.

The second packets open differently again (`YCHEOR`, `OKCHD`, `TCHOL`,
`TCHOKY`). No exact opener or final card is common to all four pages. Their
paragraph ends are respectively CTHY/DAIIN/DAIINY/CHEECKHODY for the first
packets and QOTOR/DY/OTAM/DAIIN for the second. Thus the paragraph boundary is
encoded by layout and source separation rather than a universal END word.

The best Herbal syntax is consequently:

```text
[page-specific entry address or class] + multi-line technical module
[new module address or discourse reset] + multi-line technical module
```

Calling the first card a plant name remains attractive because readable
herbals normally begin an entry with a name or synonym, but the same rarity of
paragraph starts occurs in other registers. The safer term is
`HERBAL_ENTRY_ADDRESS_A`; no lexeme is promoted.

## Iteration 73 — plausible production workflow for a five-scribe workshop

The current model can be implemented with ordinary fifteenth-century workshop
practice and no implausibly perfect cipher training:

1. **Layout and drawing first.** A master or illustrator reserves text pockets,
   draws the plant, bath/apparatus or circle, and establishes visible slots.
2. **Source abstraction.** A compiler or senior scribe reduces a source entry
   to a page address, a few content cards, settings and ordered operations.
3. **Register table.** The writer consults a small Herbal, bath or almanac card
   list. Common content rows combine with AIIN/EDY/EEDY-like cell types.
4. **Stateful copying.** S carries the current state, D makes a selection
   explicit, Q links a licensed next/homologous cell, and DY checkpoints a
   local cell without ending the larger statement.
5. **Local references.** A compact card can be written beside a visible object
   and reused in prose (`OKAL`, `OTOR`, OTAIN-family, f69 ring cards).
6. **Renderer choice.** The hand joins or detaches pieces and shortens a form
   according to learned practice and available space. This creates alternate
   readings without requiring different underlying content.
7. **Paragraph commit.** A marked paragraph break closes the module; a physical
   line break normally does not.

This workflow naturally produces Currier/register effects. Hand 1's Herbal-A
deck licenses `CHOL CTHY`; hand 2's Biological/Herbal-B deck favours its own
surface inventory and longer record-like packets; hand 4 fills compact circle
slots. They share the compiler conventions but not every card or spelling.

The reason for using such a system could be compression, standardization of
heterogeneous source languages, rapid copying, workshop secrecy, or several at
once. Compression/standardization is the primary hypothesis because the
notation exploits images and slot geometry; deliberate concealment is not
required. This also explains why simple language/cipher mappings and phonotactic
fits fail while formal recurrence remains strong.

## Iteration 74 — deliberately bold Biological paraphrases

The sidequest now permits the following end-to-end German paraphrases. They are
not recovered plaintext; they show that one coherent codebook can make the
pages useful to a practitioner.

### f81v

> **OTAIN–OLKAL bath/apparatus.** First carry the existing setting, enter the
> local quantities or reference values, and specify the OL medium and apparatus
> state. Then work through the long sequence of linked and completed process
> cards, retaining the medium at checkpoints and repeating a card where the
> same treatment/state is required.

### f82r

> **OKAL bath/site or hydraulic system.** Record its identity/physical setting
> and the relevant values; record a second module for use, condition or
> procedure; then give the extended operating/therapeutic entry. In the lower
> scheme mark the left discharge as DAROL and the right discharge as DARARY;
> assign separate short cards to the figures and remaining components.

### f83r

> **Extended treatment and flow circuit.** The five main blocks give the
> successive descriptive, indication and procedure modules. In the lower local
> diagram carry the incoming OL path to the DAL basin, activate the outgoing OL
> path at the SY spray, and specify two parallel SOL constructions ending in
> OL, followed by the local DAIIN setting and a final short SOL construction.

The most literal invented rendering of f83r.52–55 is:

```text
SOL-KEEY; linked EKEY; RALY relation; in/through OL.
SOL-CHKAL; CHE-OL; QOT-AR relation; in/through OL.
Set one OL unit; enter DAIN/CHEY; hold at LDALOR.
SOL; RTAIN; CTHAL.
```

A practitioner could read that as two parallel operations in the same medium,
a setting/quantity line and a final operation. A diagram drafter could instead
read it as two component specifications, one configuration line and a final
component. The unresolved verb-versus-noun choice is now the largest local
ambiguity, not the overall record architecture.

## Current maximum-use theory after seventy-four iterations

The ten pages now yield a coherent hierarchy:

```text
DOCUMENT  illustrated medical/astrological workshop handbook
PAGE      silent subject and register supplied by drawing
MODULE    paragraph-scale entry; statements can cross physical lines
FIELD     one or more registered cards with local checkpointing
CARD      opaque content row plus setting/state/renderer choices
LABEL     incomplete card completed by visible owner and slot geometry
```

The best content assignments are, in descending order of usefulness:

1. Biological `OL` is a carrier/medium/channel class, often literally water or
   liquid at page level but not a universal word WATER.
2. `D/S + AR + OL + right state` is a local hydraulic conduit algebra; D is
   active/outgoing and S incoming/carried in the strongest scene.
3. `OTAIN OLKAL` is a vessel/bath/apparatus label and `OKAL` is a reusable
   anonymous page key.
4. EDY-rich prose records processes/results/states, while AIIN-rich packets
   record settings/values/references.
5. SOL is a Biological construction head, with action versus component status
   unresolved.
6. Herbal pages contain two technical modules under a silent plant heading;
   `CHOL CTHY` is a shared Herbal-A preparation/qualification formula.
7. Circle labels are residual value/object cards whose ordinal, system and some
   state information are carried by geometry.

This is substantially more than whole-word similarity alone, but it is still
a generative translation hypothesis. It has not produced one independently
confirmed plaintext word, and several attractive assignments were deliberately
chosen because they make these ten pages cohere.

## Iteration 75 — explicit counterexample ledger for the current theory

The ten-page theory becomes more useful when its attractive terms are tested
against their own awkward occurrences:

| proposed reading | strongest support | counterexample / correction | retained form |
|---|---|---|---|
| `AROL = water` | DAROL and DAROLSY in flow scenes | plant/pharma and astronomical contexts; zero free exact `AROL` in these ten pages | reject WATER; retain compound conduit/axis hypothesis |
| `OL = water` | OL-rich apparatus-local f83 text and OL-bearing labels | exact OL also occurs on f55v and f69v; DARARY is a flow-scene no-OL form | register-local carrier/medium/channel only |
| `OKAL = the f82 object` | exact label plus two prose hits in all readings | exact OKAL occurs eight times across f55v, f67r2, f81v and f82r | general registered category/card used as a local f82 key |
| `OTAIN = bath` | one tub label plus f81/f82 prose; all three exact ZL hits are Biological | label changes to OTOIN/TAIN in alternate readings; wider manuscript not tested here | bath/vessel/apparatus-class candidate in this register |
| `SOL = action verb` | Biological concentration, frequent line entry, parallel SOL…OL lines | SOL-rich local block may specify apparatus components; 11/13 SOL-initial lines do not end OL | anonymous Biological construction head |
| `first Herbal block = description; second = recipe` | four pages have exactly two prose packets | feature profiles and CHOL CTHY position do not preserve that order; prior ordinal test failed | two technical modules with unknown ordering |
| `O/OT encodes star rays` | f68 1/9 versus 6/9 non-seven-ray post-hoc contrast | one folio, no held array, widespread O/OT outside stars | local renderer clue only |
| `f69 is a 28-night table copied from one known source` | 28 radial entries and strict alternation | lag-14 prediction failed; LONG/SHORT lacks a text marker | generic 28-position state schedule |
| `line = sentence` | visually lineated prose | renderer reset and continuation evidence; text is fitted around drawings | line is a writing packet, paragraph is the stronger discourse unit |
| `all diagram labels are referenced in prose` | OTOR, OKEOD-family, OTAIN-family, OKAL bridges | f83 selected labels have zero exact prose reuse; f82 only 1/13 labels repeats exactly | sparse optional page-key channel |

Two numerical cautions are especially important. The f68 page has 29
human-owned star labels; the earlier “32 labels” count included three other
one-group diagram texts and must not be read as 32 stars. Also, the compound
AROL theory has only one exact `DAROL` and one exact `DAROLSY` free surface in
the fixed ten pages. Its apparent productivity comes from older split/join and
component evidence, not a large local paradigm.

## Iteration 76 — recipe grammar as an analogy, not a Latin decoding

Readable medieval recipes often compress a practical sequence into a small
set of recurrent functions: take/select material, give quantity, prepare,
combine with a vehicle, apply, wait/continue, and close. The present cards can
be aligned with that **event grammar** without claiming a word correspondence:

| practical function | current anonymous card candidate |
|---|---|
| select or explicitly enter an item/value | D + content; `DAIIN` |
| carry the current item/state into a new packet | S + content; `SAIIN` |
| refer to a linked licensed operation/value | Q + content |
| quantity, grade, setting or registered reference | AIIN family |
| processed/completed/marked state | EDY/EEDY family |
| carrier, vehicle, bath medium or channel | OL family |
| route, transfer or conduit relation | AR with OL/other tail |
| introduce a Biological operation/component specification | SOL construction |
| checkpoint one local operation | DY |
| repeat the same operation or assign it twice | literal `X X` |

This yields an end-to-end **technical event language** rather than a list of
translated words. For example, the invented construction

```text
SAIIN | DAIIN | ... OL ... | QOKEEDY | DAROLSY
```

can be read abstractly as:

```text
carry current setting → enter local value/item → specify carrier
→ invoke linked completed process → discharge/transfer to terminal state
```

It should not be converted into a Latin sentence such as *recipe aquam...*.
The analogy is useful precisely because the notation may summarize Latin,
vernacular or nonlinguistic source instructions with the same cards.

## Iteration 77 — strongest next discriminant inside the same ten pages

The main unresolved fork is now:

```text
WORLD L: the long paragraphs are heavily abbreviated natural-language clauses
WORLD N: the long paragraphs are sequences of nominal technical specifications
WORLD H: both occur, with prose-like connectors around codebook cells
```

The local SOL construction demonstrates why surface order alone cannot choose.
`SOLKEEY ... OL` can be “perform X in medium OL” under WORLD L, or “component X,
OL channel” under WORLD N. WORLD H remains the leader because it allows long
paragraph discourse while treating diagram labels and repeated matrix cards as
technical notation.

Within the fixed pages, the best discriminator is not another substring. It is
whether repeated construction heads systematically change their argument
inventory between main prose and diagram-local blocks. The current evidence is:

- SOL occurs only in the f82/f83 Biological sample and usually at line entry;
- exact free final OL occurs only in the two adjacent local SOL lines;
- the local f83 blocks reverse the main-prose EDY/OL balance;
- but most SOL lines have varied continuations and no fixed arity.

That favours a flexible construction head over a fixed noun label, while still
falling short of a verb. The working notation should therefore retain
`SOL_HEAD(ARGUMENTS...)` and postpone TAKE/APPLY/COMPONENT until an independent
relation becomes available.

## Iteration 78 — the three Astro pages form a multi-table system, not one copied list

The most attractive numerical bridge must survive a direct inventory check:

```text
f68r1  29 labelled stars = one documented central + 28 noncentral
f69v   28 ordered radial entries
```

If these were simply the same 28 named units rendered twice, shared cards or a
fixed order would be expected. In the fixed ZL readings, none of the 29 exact
f68 star-label groups is an exact group in the f69 radial entries. The f68
array also has no authorial start or direction. This rejects the simplest
“star map plus identical keyed list” reading.

A more realistic workshop system uses different dimensions:

```text
f67r2   rule/classification wheel: 12-member system under 7-member system
f68r1   spatial object or station catalogue around sun/moon references
f69v    ordered 28-position schedule with a visible parity/alternation channel
```

The three tables can belong to one astrological toolkit without sharing
surface identifiers. The 12/7 wheel may choose sign and celestial controller;
the star field may identify a spatial configuration; the 28 schedule may give
a daily/station prognosis, permitted action or state. These are semantic
possibilities, not decoded coordinates.

The historical analogy is strong but nonunique. An Oxford Museum of the
History of Science late-fifteenth-century medical-astrology instrument combines
fever prediction, a zodiac scale and a 1–28 scale for lunar mansions
(<https://www.mhs.ox.ac.uk/astrolabe/exhibition/medical_astrology.html>).
Late medieval folded almanacs were likewise designed in part for medical
practitioners
(<https://research-information.bris.ac.uk/en/publications/astrological-medicine-and-the-medieval-english-folded-alihanac/>).
This makes a 7/12/28 medical timing apparatus plausible, but it does not make
f69 a lunar-mansion list or connect any Voynich card to a mansion.

The strict f69 LONG/SHORT alternation is best read as a parity or two-column
scaffold, not GOOD/BAD. Alternating layout can help a copyist track odd/even
slots. The actual written card then supplies the variable result. Since the
text does not distinguish LONG from SHORT, the geometry already carries the
binary bit and no redundant marker is needed.

## Iteration 79 — bold Astro paraphrase and medical use

The strongest complete but explicitly speculative reading is:

### f67r2

> Choose the relevant one of twelve cyclic classes and the governing one of
> seven celestial classes. Read the associated short rule cards and consult the
> surrounding legend for how to combine them.

### f68r1

> Identify the individual star/station or observed configuration relative to
> the sun and moon. Record one compact identifier/attribute card beside each
> object; use the upper prose as the catalogue legend.

### f69v

> For each of twenty-eight ordered stations/days, follow the alternating slot
> scaffold and read the assigned state, prognosis or permitted-action card.
> Repeated `OKEOD` means that the same result recurs at several positions. The
> outer text explains how those value cards are used.

In the unified medical manual, these pages could answer “when, under which
celestial configuration, is the plant/bath procedure selected, avoided or
modified?” They might instead be ordinary astronomical, calendrical or magical
tables bound with medicine. The ten pages do not decide. The useful advance is
the division into **selection wheel, spatial catalogue and ordered schedule**,
which explains their different recurrence patterns without pretending all
labels are names.

The zero f68↔f69 exact-card overlap and failed f69 lag-14 test remain central
falsifiers. Any later attempt to claim a direct lunar table must explain both
rather than relying on the attractive number 28.

## Iteration 80 — statements live between line and paragraph scale

The fixed pages quantify why line-by-line translation repeatedly failed. The
two Herbal modules occupy:

| page | module A lines | module B lines |
|---|---:|---:|
| f10r | 5 | 7 |
| f11r | 5 | 2 |
| f55v | 6 | 6 |
| f56r | 9 | 10 |

The Biological prose modules are larger still:

```text
f81v  9 + 18 lines
f82r  9 + 9 + 14 lines
f83r  8 + 9 + 7 + 6 + 14 main lines, then 3 + 4 local lines
```

A paragraph therefore behaves like a **record or discourse module**, not one
ordinary sentence. It can contain a list of operations, properties or clauses.
The physical line is a copy packet constrained by available width; supported
S-at-line-entry and Q-after-DY rendering shows that line position changes a
surface form without necessarily changing content.

The smallest useful sentence-like unit is the field or short construction,
but DY cannot be translated as a full stop. f83r.52–55 illustrates the full
hierarchy particularly clearly:

```text
paragraph/local record
  line 52: one four-card SOL...OL clause/specification
  line 53: a parallel four-card SOL...OL clause/specification
  line 54: a five-card DAIIN configuration clause
  line 55: a short three-card SOL clause/specification
```

The four lines jointly describe one local apparatus record. A translation
should preserve their parallelism and shared scope rather than emit four
unrelated sentences.

The current punctuation analogy is consequently:

```text
SPACE/JOIN       internal attachment uncertainty
DY               comma/semicolon/check box inside a module
physical line    line wrap plus possible carried state
paragraph break  record/module boundary, closest available analogue to full stop
page/diagram     silent heading and discourse domain
```

B3 may be a stronger closure state in the formal parser, but it is not a
confirmed period and is not required at every visible paragraph end. The early
v0.3 `B3 = full stop` gloss is withdrawn.

## Iteration 81 — CHOL CTHY as a paired quality formula

The earlier “prepare in water” reading of `CHOL CTHY` used OL too literally.
The actual repeated lines suggest a different construction:

```text
f10r.5   QOKCHY | QOTCHOL | CHOL | CTHY
f11r.3   QOTY | CHOL | CTHY | DOR ...
f56r.15  TCHO | TCHOL | CHOL | CTHY
```

The stable tail describes three visibly different plants, occurs in different
packet positions, and is absent from the hand-2/Currier-B f55v page. This is
exactly the behaviour expected of either a hand-1 stock formula or a shared
classification, not a plant name.

Medieval materia medica supplies a particularly economical class of stock
formulae: paired qualities such as hot/cold and dry/moist, often qualified by a
degree. The British Library's Add MS 29301 catalogue even quotes the Middle
English *Circa instans* opening “Aloe is hot and dry”
(<https://searcharchives.bl.uk/catalog/032-002020783>). Astrological medicine
uses the same broad quality system for signs, planets, bodies and treatment
conditions. Exact `CHOL` also occurs in the f67r2/f69v circle text, so a quality
card can cross Herbal and Astro registers more naturally than a literal plant
preparation or water noun.

The new leading parse is therefore:

```text
T/QOT-CHOL     marked or linked quality/class card
CHOL CTHY      paired quality/constitution formula
AIIN/DAIIN     possible degree, setting or quantity value when supplied
```

A bold readable paraphrase is “[quality A] and [quality B], at the registered
degree.” It would be tempting to write “hot and dry”, but there is no basis for
choosing which quality, which order, or even whether the pair is humoral. Other
possibilities are part-used + preparation-method, season + habitat, or two
workshop classification codes.

The main counterevidence is strong: CTHY itself is confined to the three
Herbal-A/hand-1 pages in this sample, CHOL has many non-paired occurrences, no
explicit AND is identified, and the formula's paragraph ordinal varies. The
result is a better **functional gloss**—paired classification—not two English
adjectives.

## Iteration 82 — weak ordering of the two Herbal modules

The four Herbal pages each contain two prose modules, but the earlier rigid
`DESCRIPTION -> RECIPE` reading was too strong. A deliberately coarse exact-form
census nevertheless leaves a weaker ordering clue. Across ZL3b the four first
modules contain 167 groups and the four second modules 192 groups:

| module set | AR-family | OL-family | AIIN-family |
|---|---:|---:|---:|
| first | 6 (3.6%) | 18 (10.8%) | 27 (16.2%) |
| second | 16 (8.3%) | 24 (12.5%) | 34 (17.7%) |

AR-family density does not decrease from first to second on any of the four
pages, although most of the aggregate contrast is supplied by f55v. OL and
AIIN are only slightly denser in the second modules. Coupled with the repeated
`CHOL CTHY` quality formula, the least extravagant workshop ordering is:

```text
module 1    identity / class / intrinsic qualities
module 2    relational use / preparation / quantity / application
```

This is an ordering tendency, not two fixed fields and not two sentences.
Page-specific omissions, copied source differences, and available drawing
space can change the contents and length of either module. A previous powered
paragraph-ordinal route failed, so this ordering is retained only as a weak
scribe-level default. It becomes useful only if later parses independently
place a classification formula in module 1 and a relational or procedural
construction in module 2 on the same page.

## Iteration 83 — one workshop handbook, three lookup layers

The ten pages now support a more economical historical model than ten isolated
microgenres. The proposed object is an **illustrated practical handbook** whose
three surviving lookup layers answer different questions:

| layer | these pages | silent information | written residual |
|---|---|---|---|
| materia medica | f10r, f11r, f55v, f56r | pictured simple | class/quality, virtues, preparation/use |
| baths/apparatus | f81v, f82r, f83r | pictured site, vessel, conduit and participant | setting, local component, process/state, indication/result |
| astro-medical lookup | f67r2, f68r1, f69v | selected ring, star position, radial ordinal/parity | class, local state, prognosis or permitted action |

This package is historically ordinary at the level that matters. British
Library Egerton MS 747 joins an illustrated *Tractatus de herbis*, a lunar
calendar, an antidotary, doses, substitutions, weights/measures and ingredient
synonyms (<https://searcharchives.bl.uk/catalog/032-001983805>). Add MS 29301
(c. 1420–1430) joins surgical diagrams, a Zodiac Man, 68 plant drawings, a
Middle English *Circa instans*, a regimen and recipes
(<https://searcharchives.bl.uk/catalog/032-002020783>). Monica Green's and
Hilary Carey's work on late-medieval folded almanacs identifies them as compact
medical-practitioner instruments combining calendrical, astrological and
medical information (<https://research-information.bris.ac.uk/en/publications/astrological-medicine-and-the-medieval-english-folded-alihanac/>).
Peter of Eboli's illustrated *De balneis* tradition describes named baths,
their therapeutic waters and treatment effects; even the number and order of
bath entries vary among witnesses
(<https://www.cambridge.org/core/journals/traditio/article/peter-of-eboli-de-balneis-puteolanis-manuscripts-from-the-aragonese-scriptorium-in-naples/C804287BB668512B4D019696E0B114C8>).

The parallel is **information architecture**, not textual descent. No readable
comparator has the Voynich drawings, card strings, paragraph counts or exact
circle system. But it makes a single small workshop's task intelligible:

```text
1 draw or copy the subject and its slots
2 choose the register table: SIMPLE / BATH-APPARATUS / CIRCLE
3 write a page-specific address or let the image supply it silently
4 emit one or more records from shared abstract cards
5 render a card joined or detached according to hand, state and available space
6 carry state across line packets; close only the local field or paragraph
```

The resulting grammar need not be a substitution cipher. A new scribe learns
roughly a dozen construction states and three finite register tables, then
copies content from heterogeneous sources into that normalized format. This
explains why Currier/hand changes affect surface families, why exact cards can
recur without stable immediate neighbours, why image labels and prose only
occasionally bridge exactly, and why a character model predicts formal variants
well while whole-word translation attempts fail.

### Current compact card manual (v0.4)

| card/construction | best workshop instruction | confidence | strongest warning |
|---|---|---|---|
| pictured subject | take as silent record address | medium | ownership can be ambiguous |
| paragraph start | open a new module under that address | medium | not necessarily a new subject |
| `S-` line entry | carry/resume current setting | low | may be renderer only |
| `D-` construction | set/activate an explicit local item/state | low | no semantic transfer proof |
| `Q-` construction | link/look up a dependent registered card | low | GDT003 cannot beat strings |
| `AIIN/DAIIN` | supply value, degree, quantity or reference | very low | exact value/number unknown |
| `EDY/EEDY` | processed/result/state family | very low | extremely register-sensitive |
| `OL` in Biological | carrier/medium/channel class | low local | emphatically not universal WATER |
| `AR+OL` in local labels | conduit/path relation | very low local | tiny, partly unstable sample |
| `SOL ... OL` | construction head with an OL argument/terminal | very low | verb/noun unresolved |
| `CHOL CTHY` | paired quality/classification formula | low functional | qualities and degree unknown |
| `DY` | field checkpoint/transition | medium formal | not sentence-final punctuation |
| B3 | stronger local closure state | medium formal | not a confirmed period |
| drawing/ring position | silent owner, ordinal or state | medium | cannot assume one universal coordinate |

The best current end-to-end paraphrase is therefore not a plaintext but an
editorial instruction: **identify the pictured entry; register its qualities
and values; record relevant relations, process states or uses; consult the
appropriate astronomical state table when needed; carry and close the record
with a small shared compiler.** This is the first theory that covers all ten
pages without requiring one global word gloss.
