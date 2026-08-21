# Candidate V2 — executable exemplar-card parser

Date: 2026-08-21

Status: **independent YOLO theory evolution; speculation, not a GDT result or
translation**.

This candidate was developed from `VOYNICH_CURRENT_ROUTE.md`,
`SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md`, and source-native slices for the fixed
ten pages only. I did not consult the previous candidate reports or the long
sidequest archive. `f84` and `f84r` were neither queried nor accessed.

## Executive result

The strongest executable reconstruction I can make is a **typed exemplar-card
register**. Its visible groups are not uniformly words. They are learned cards
which can abbreviate a word, short formula, relation, entered value, or
technical state. A small common deck is inserted into register-specific field
stencils. A final card can carry both content and a local `COMMIT` realization;
therefore it is neither merely punctuation nor necessarily a pronounced
suffix.

```text
PICTURE/PAGE ADDRESS
    supplies the silent dossier subject
        ↓
REGISTER STENCIL
    Herbal descriptor row | Bio operation/configuration cells | Astro array
        ↓
CARD SELECTION
    HEAD, ITEM, RELATION, VALUE, STATE, local technical card
        ↓
FIELD ASSEMBLY
    optional head + zero or more argument/state cards + typed terminal
        ↓
COMMIT / CARRY / REFLOW
    attached close commits a field; physical line only fits it around the image
        ↓
HAND RENDERER
    wrapper/allograph, JOIN/SPACE, line-entry and post-close habits
```

The upstream source can still have been ordinary abbreviated technical
language. The important claim is narrower: the manuscript page was generated
from **whole learned entries and templates**, not by enciphering every source
letter in running prose.

The best provisional content ecology is:

- Herbal: pictured simple plus qualities, habitat/medium, preparation or use;
- Biological: bath/application/apparatus records with short committed cells;
- Astro: local lookup arrays, perhaps timing/configuration aids, but not one
  universal dictionary shared with prose.

Water can occur as an ingredient, habitat, medium, bath, wash, conduit content,
or silent pictured default. Nothing in this parser requires `OL`, `AROL`, or
another common card to mean WATER.

## Evidence base

The guarded GDT276/GDT327 slice contains 381 events on the seven fixed prose
pages:

| page | events | exact cards | attached closes | physical lines |
|---|---:|---:|---:|---:|
| f10r | 38 | 25 | 0 | 5 |
| f11r | 17 | 15 | 1 | 3 |
| f55v | 18 | 16 | 2 | 2 |
| f56r | 27 | 21 | 1 | 7 |
| f81v | 66 | 43 | 17 | 7 |
| f82r | 62 | 46 | 19 | 8 |
| f83r | 153 | 79 | 49 | 25 |

There are 173 exact joint-tuple types, but their workload is strongly
concentrated:

| minimum occurrences | types | events carried |
|---:|---:|---:|
| 2 | 51 | 259 |
| 4 | 21 | 190 |
| 7 | 15 | 163 |
| 10 | 8 | 110 |

Thus a trainee could learn roughly twenty common cards and a dozen common
stencils, while copying the 122 one-off types from page/register exemplars.
This is much more plausible than requiring every writer to calculate a large
factorial morphology.

The circle pages are kept separate. f67r2 contains distinct labelled and prose
zones; f68r1 has one central and 28 noncentral labelled stars; f69v has 28
ordered radial text loci in strict LONG/SHORT layout alternation. They have no
GDT327 events, so their visually similar EVA pieces are not equated with prose
cards here.

## The compact workshop inventory

### Common content/grammar cards

The aliases below name parser functions, not established meanings. Hashes are
the first eight characters of exact opaque GDT327 IDs.

| alias | exact ID | observed surfaces | fixed-page evidence | boldest expansion |
|---|---|---|---|---|
| `VAL` | `2f1c5e56` | daiin/saiin/aiin/taiin/chaiin | 20 events, all 7 prose pages; freely first/middle/last | amount, degree, count, index or shared value |
| `TYPE` | `b921a237` | y/dy/chy/chey/shy/sy | 18 events, 6 pages; mostly interior | unit, object-type or argument-frame card |
| `LINK` | `dcda95c8` | ol/chol/qol/sol/tol/cheol | 19 events; often between items | broad of/with/in/for/list relation |
| `STATE` | `e0b630cb` | cthy/shcthy/checthy | 7 events; nearly always interior | quality or prepared/intermediate state |
| `HEAD` | `b5fcea1e` | qokaiin/okaiin | 9 events; field-first 7 times | take/set/enter the current operative item |
| `ITEM` | `1645e612` | qokain/okain | 7 events; first or interior | selected item/input/reference |
| `PROC` | `0275fbf1` | qokeey/okeey | 7 events; open, often before a close | perform/continue a preparation or setting |
| `STATUS` | `276a7c2d` | qoky/choky/oky | 10 events, 5 pages | status/default/continuation class |
| `REL-A` | `dd0ecaf5` | dal/al/sal/chal/cheal/tal | 10 events; all positions | destination, slot, part, or other relation |
| `REL-B` | `7a4bb813` | or/chor/shor/sor | 7 events | second broad relation or alternative argument link |
| `REF` | `4d455901` | ar/dar/char/sar | 5 events, 4 pages | local source/target/reference card |
| `ACTION` | `6f7ff828` | chedy/chedy/chdy | 11 events; explicitly not a GDT close | operation/state card awaiting another terminal |
| `CONFIG` | `2cc8bb3c` | chckhy/shckhy | 4 events | apparatus/body/material configuration card |
| `SET` | `308e8ea2` | qokal/okal | 6 events | set/class/measure-selection card |
| `QUAL` | `d904bf7b` | cheky | 3 events | local quality/state subtype |

`HEAD`, `ITEM`, and `PROC` are intentionally different exact cards despite
their similar surfaces. The parser does not derive them from spelling. Their
expansions are hypotheses about whole cards.

### Typed terminal cards

The principal biological terminal cards are:

| alias | exact ID | events | surface family | current formal reading | provisional content reading |
|---|---|---:|---|---|---|
| `CLOSE-A` | `bc4f1f5c` | 12 | shedy/cheedy/tedy | general typed commit | step/result completed |
| `CLOSE-B` | `7d25241b` | 10 | qokeedy | qokee-type commit | preparation/setting brought to required state |
| `CLOSE-C` | `7db18b2f` | 8 | qokedy | qoke-type commit | current operation/configuration confirmed |
| `CLOSE-D` | `de7321bf` | 8 | lchedy | lche-type commit | location/container/application slot resolved |
| `CLOSE-E` | `259b2b3b` | 4 | schedy/dchedy/tchedy | sche-type commit | record/phase boundary or higher-level result |
| `CLOSE-F` | `28ffbc88` | 3 | qolchedy/olchedy | qolche-type commit | linked/subordinate slot resolved |
| `CLOSE-G` | `3b709425` | 3 | olkeedy/solkeedy | olkee-type commit | source/input/medium slot resolved |
| `CLOSE-H` | `87411f84` | 3 | qokchdy | qokch-type commit | compact configuration committed |
| `CLOSE-I` | `d68bc8de` | 3 | shckhedy | shckhe-type commit | repeated local apparatus/state result |

The content column is deliberately aggressive. The formal claim is stronger:
these are **different cards with the same field-ending operation**, not one
punctuation mark. `CLOSE-A`, for example, occurs as a one-card field and after
1, 2, 3, 4, or 5 preceding cards. `CLOSE-B`, `CLOSE-C`, and `CLOSE-D` likewise
occur alone or with variable payloads.

This dual behavior motivates:

```text
TERMINAL_CARD := CONTENT_CLASS + COMMITTED_REALIZATION
```

rather than either extreme:

```text
DY = a translated word
DY = meaningless punctuation
```

## Executable grammar

### Page and record layer

```ebnf
PAGE        := VISUAL_ADDRESS RECORD+
RECORD      := LINE+
LINE        := FIELD (FIELD)*
FIELD       := OPEN_FIELD | COMMITTED_FIELD
OPEN_FIELD  := CARD+
COMMITTED_FIELD := PAYLOAD* TERMINAL_CARD
PAYLOAD     := HEAD | ITEM | TYPE | VALUE | RELATION | STATE | LOCAL_CARD
```

`LINE` is a physical packing unit. It does not close `RECORD`. A statement can
cross a line. `VISUAL_ADDRESS` supplies an omitted subject or object; it need
not supply every argument.

### Register programs

```ebnf
HERBAL_RECORD := OPEN_DESCRIPTOR_LINE+
OPEN_DESCRIPTOR_LINE := ENTRY? (CLASS | QUALITY | RELATION | VALUE | LOCAL_CARD)+

BIO_RECORD := BIO_LINE+
BIO_LINE := COMMITTED_FIELD+ OPEN_FIELD?
COMMITTED_FIELD := HEAD? ARGUMENT* TYPED_TERMINAL

ASTRO_ARRAY := LOCAL_PROSE? OWNED_LABEL_CELL+
OWNED_LABEL_CELL := one or more surface groups owned by one frozen diagram slot
```

### Inheritance and zero realization

Standalone terminal cards are common. The cheapest coherent rule is:

```text
if a field contains only TERMINAL_CARD:
    inherit the active page/record subject
    inherit any still-open argument class licensed by the preceding field
    write only the changed result/terminal state
```

This is not proven ellipsis. It is a necessary candidate rule because treating
each one-card close as a complete ordinary sentence makes the Bio pages less,
not more, intelligible.

### Reflow and carry

```text
if LINE space is exhausted inside RECORD:
    break the physical line
    optionally repeat the active HEAD at next line entry
    continue the same field/record program
```

The unique exact f82r carry (`qokaiin` line-final then identical `qokaiin`
line-initial) is the direct exemplar. The repeated card may be a catchword-like
copy aid, a rubric resumed after reflow, or semantically counted once.

### Renderer

```text
surface := render(EXACT_CARD, hand, register, line_entry, post_close)
```

Wrappers are selected only after the card is licensed. Known manuscript-wide
`s@LINE_START` and `q@POST_DY` effects belong here. The parser never expands
`q-`, `d-`, `s-`, `ch-`, or `sh-` as independent spoken morphemes.

## Actual line parses: Herbal

The right-hand paraphrases are deliberately schematic. `U` means a presently
unclassified exact local card, not noise.

### f10r

```text
f10r.2
dchey cthoor char chty os chair otytchol oky daiin etyd
U U REF U U U U STATUS VAL U
≈ [pictured plant]: local identity/class — status — entered value — local tail.

f10r.5
qokchy qotchol chol cthy
U U LINK STATE
≈ [pictured plant]: local class/material, linked to a quality/prepared state.

f10r.6
ycheor cthy chor cthaiin qoctholy dy chy taiin shy
U STATE REL-B U U TYPE TYPE VAL TYPE
≈ [plant dossier material] — state/relation — typed equal-or-shared value frame.

f10r.8
qotchor chor otol chol cholor chol daiin dar
U REL-B U LINK U LINK VAL REF
≈ class/relation chain — value — reference/source/destination.

f10r.9
oykchor shor chor chy kaiiin dy chodaiin
U REL-B REL-B TYPE U TYPE U
≈ local descriptor with two linked/type-marked arguments.
```

The long open lines are compatible with plant descriptions, qualities,
habitat/moisture, preparation, or indications. They do not resemble the short
committed Bio cells.

### f11r

```text
f11r.1
tshol schoal cfhy shfydaiin cphy shey tchody⟫ | shoyty
U U U U U U LOCAL-CLOSE | U
≈ long descriptor reaches one committed local result, then continues.

f11r.4
dchol chy kchy dy daiin
U TYPE U TYPE VAL
≈ two typed/classed items with an entered amount/index.

f11r.7
qotchy okchol cthy dy
U U STATE TYPE
≈ local item/class in a stated condition/type.
```

f11r proves that Herbal can use a committed cell, but its rarity prevents
equating closure with Biological subject matter.

### f55v — the renderer bridge

```text
f55v.5
qokaiin chaiin ykain ykan ody⟫ | daiin chedy talam
HEAD VAL U U LOCAL-CLOSE | VAL ACTION U
≈ TAKE/ENTER — amount/index — item details — commit;
  then amount + operation/state + local tail.

f55v.11
ykaiin cheoar cheeky oldy⟫ | aiin okal oltchy or y orain
U U U LOCAL-CLOSE | VAL SET U REL-B TYPE U
≈ selected item/configuration committed; then amount, setting, relation and type.
```

This is the cleanest Herbal support for a recipe-like `HEAD` reading. It is
also exactly what a shared B renderer plus a Herbal register addendum predicts.

### f56r

```text
f56r.5  chochor cho chodaly daiin
         U U U VAL
≈ local descriptor plus amount/index.

f56r.7  sho kchol otchor choky dal
         U U U STATUS REL-A
≈ class/status directed to a part/slot/relation.

f56r.8  schol choy choky cheeckhody⟫
         U U STATUS LOCAL-CLOSE
≈ a status-bearing plant field committed.

f56r.19 otchey keol daiin
          U U VAL
≈ local item or property plus entered value.
```

The other short f56r lines are mostly page-local cards. That is expected if the
image supplies the plant and the page records species-specific descriptors.

## Actual line parses: Biological

### f81v

```text
f81v.2
qokedy⟫ | okaiin kair okal sar ol kain olkain al ol rol dl
CLOSE-C | HEAD U SET REF LINK U U REL-A LINK U U
≈ inherit current subject/configuration and confirm it;
  then TAKE/SET an item with linked source/part/setting information.

f81v.17
sshkchdy⟫ | chedy ol shedy⟫ | qolchedy⟫ | qokain shckhy dl ral
U-CLOSE | ACTION LINK CLOSE-A | CLOSE-F | ITEM CONFIG U U
≈ commit local state; perform action through/with relation and complete;
  commit a linked slot; select item under an apparatus/configuration.

f81v.18
qokchdy⟫ | chey ol cheky ol shedy⟫ | qokedy⟫ | qokedy⟫ | chckhy qoky
CLOSE-H | TYPE LINK QUAL LINK CLOSE-A | CLOSE-C | CLOSE-C | CONFIG STATUS
≈ commit configuration; type/link/quality/link/result;
  two inherited confirmations; leave configuration in stated status.

f81v.21
lsho qokey lshedy⟫ | lshedy⟫ | chedy qolky lchedal qol otar
U U LOCAL-CLOSE | same CLOSE | ACTION U U LINK U
≈ explicit payload then identical inherited result; continue with action relation.

f81v.24
ytey okchedy⟫ | qokal okeey qol cheedy⟫ | sal teol dchdy⟫ | ly
U U-CLOSE | SET PROC LINK CLOSE-A | REL-A U U-CLOSE | U
≈ commit item; select and process through a link to result; commit destination;
  retain a local continuation card.

f81v.27
dsheol oiiin olkeedy⟫ | tedy⟫ | cheky shckhedy⟫ | chal
U U CLOSE-G | CLOSE-A | QUAL CLOSE-I | REL-A
≈ input/medium slot resolved; inherited result; qualified configuration resolved;
  next relation/part remains open.
```

### f82r

```text
f82r.2
dchedy⟫ | qolchedy⟫ | qokain dy qokeedy⟫ | qokal lcheckhy lched
CLOSE-E | CLOSE-F | ITEM TYPE CLOSE-B | SET U U
≈ close phase; close linked slot; select typed item and bring to state;
  open next setting/configuration.

f82r.3 → f82r.4
qokeey lcheckhedy⟫ | qokaly solkaiin chckhy qokaiin
PROC U-CLOSE | U U CONFIG HEAD
qokaiin octheol chkeey ldy⟫ | oteey qokal sheckhy qoky
HEAD U U CLOSE-D | U SET U STATUS
≈ process/commit; configure an item, writing HEAD at the line edge;
  repeat HEAD on the new line, then resolve a location/application slot;
  leave the next setting/configuration open.
```

Counting the two `qokaiin` surfaces as one active control state yields a more
coherent parse than translating both as independent content. This is the best
candidate instance of copy-forward/resume-by-repetition.

```text
f82r.7
dshedy⟫ | sotaiin qokar shedy⟫ | solshedy⟫ | qokeey qoky ls cheey
U-CLOSE | U U CLOSE-A | U-CLOSE | PROC STATUS U U
≈ phase result; variable payload completed; another local result;
  process remains open with status and local operands.

f82r.19
okain char okain qokeedy⟫ | lchy
ITEM REF ITEM CLOSE-B | U
≈ item — source/target relation — item — bring to required state;
  open local continuation.

f82r.23
cheey qcthey qokeey lcheey daiin chey qokeeedy⟫ | lchedy⟫ | lar
U U PROC U VAL TYPE U-CLOSE | CLOSE-D | U
≈ operation with value/type payload committed; inherited location/application
  slot committed; new relation/reference opened.

f82r.26
tshey qokeedy⟫ | cheal lchedar ches aiin oteey qokaiin okey
U CLOSE-B | REL-A U U VAL U HEAD U
≈ bring local item to required state; open next relation with value and HEAD.

f82r.27
pchedy⟫ | rsheal daldy⟫ | qokeedy⟫ | rshedy⟫ | qoteedy⟫ |
qokeedy⟫ | lochedy⟫
seven short committed cells
≈ a compact checklist/state vector, not seven ordinary one-word sentences.
```

### f83r

```text
f83r.3
olkeedy⟫ | qotal chkeedy⟫ | chey daiin chey lchedy⟫ | qokaiin qotal dar
CLOSE-G | U U-CLOSE | TYPE VAL TYPE CLOSE-D | HEAD U REF
≈ resolve input/medium; resolve local setting; assign the same/shared typed value
  to a location/application slot; begin next operation from/to a reference.

f83r.6
schedy⟫ | chedchy qokal olchedy⟫ | qokaiin chedy qokeedy⟫ |
lchedy⟫ | qoky
CLOSE-E | U SET CLOSE-F | HEAD ACTION CLOSE-B | CLOSE-D | STATUS
≈ phase close; linked setting resolved; take/perform until prepared;
  inherited location/application resolved; leave status open.

f83r.11
sor shedy⟫ | qokaiin chkain shcthey qokedy⟫ | okair sheedy⟫ |
lchedy⟫ | lo
REL-B CLOSE-A | HEAD U U CLOSE-C | U U-CLOSE | CLOSE-D | U
≈ relational result; take/set configuration and confirm; another state result;
  inherited application/location; open continuation.

f83r.14
qokchedy⟫ | qokeedy⟫ | shedy⟫ | qokshedy⟫ | dal lchedy⟫ |
qokaiin shcthy dal sy
five committed cells, then HEAD STATE REL-A TYPE
≈ compact state/configuration checklist followed by a new instruction:
  take/set [state] for/to [part or slot] [type].

f83r.16
tchedy⟫ | qokchdy⟫ | cheedar chldaiin chedy qokain checthy chealror
CLOSE-E | CLOSE-H | U U ACTION ITEM STATE U
≈ close phase/configuration; then action on selected item in a stated condition.

f83r.20
solkeedy⟫ | qoteedy⟫ | qokeey qokedy⟫ | sol cheeety qokedy⟫ |
qoky saiin
CLOSE-G | U-CLOSE | PROC CLOSE-C | LINK U CLOSE-C | STATUS VAL
≈ resolve input; resolve local state; process and confirm; linked item confirmed;
  retain status plus value/index.

f83r.25
qokeedy⟫ | qolchey qokeey qokedy⟫ | chedy otal
CLOSE-B | U PROC CLOSE-C | ACTION U
≈ inherited preparation state; process linked item and confirm;
  open next action/argument.

f83r.26
otchey qokeey qoky tol shedy⟫ | qokylddy⟫
U PROC STATUS LINK CLOSE-A | U-CLOSE
≈ process/status through a relation to completion, then commit local consequence.

f83r.27
dain chedy qokeedy⟫ | shckhedy⟫ | shckhedy⟫
U ACTION CLOSE-B | CLOSE-I | CLOSE-I
≈ operation brought to required state, followed by two identical inherited
  configuration/result cells.

f83r.28
saiin cheeky sheey qokedy⟫ | shedy⟫ | oldy⟫
VAL U U CLOSE-C | CLOSE-A | U-CLOSE
≈ entered value/quality confirmed; inherited result; final local state committed.

f83r.35
saiin cheky okeeol okain chdy
VAL QUAL U ITEM ACTION
≈ value + quality + selected item + still-open action.

f83r.37
sol lkedy⟫ | lchedy⟫ | qokol shedy⟫
LINK U-CLOSE | CLOSE-D | U CLOSE-A
≈ linked state; inherited application/location; local result completed.

f83r.38
or chey qockhey dairydy⟫
REL-B TYPE U U-CLOSE
≈ related typed item committed to a local result.

f83r.48
dal cheol lol chdal aiin
REL-A LINK U U VAL
≈ relation/part + link + local item + value; still open.

f83r.54
daiin ol dain chey ldalor
VAL LINK U TYPE U
≈ value linked to a typed local item/relationship.
```

## Recurrent constructions that drive the parser

These are exact-card recurrences, not substring analogies.

### 1. Typed value frame

```text
TYPE → VAL → TYPE
f10r.6  chy taiin shy
f83r.3  chey daiin chey
```

Boldest expansion:

```text
ITEM/UNIT — SAME OR STATED VALUE — ITEM/UNIT
```

The plausible late-medieval recipe analogy is *ana*, equal quantities of each,
but the construction could instead encode matching setting, paired degree,
same class, or a typed numerical range. It is not read phonetically as *ana*.

### 2. Linked result

```text
LINK → CLOSE-A
```

It occurs four times across f81v and f83r with surface variants such as
`ol shedy`, `qol cheedy`, and `tol shedy`. This is the strongest compact
argument/result construction:

```text
with/in/through X → complete or record the result
```

### 3. Procedure followed by confirmation

```text
PROC → CLOSE-C
f83r.20 qokeey qokedy
f83r.25 qokeey qokedy
```

This is compatible with `PROCESS → CONFIRM CURRENT STATE`, although it could be
a purely notational two-card setting.

### 4. Action followed by prepared-state terminal

```text
ACTION → CLOSE-B
f83r.6  chedy qokeedy
f83r.27 chedy qokeedy
```

Boldest paraphrase: `perform the operation until/so that the required state is
reached`. This is a constructional expansion, not a claim that either surface
group alone means DO or READY.

### 5. Terminal-to-next-head stencil

```text
CLOSE-F → ITEM
f81v.17 qolchedy | qokain
f82r.2  qolchedy | qokain

CLOSE-D → HEAD
f83r.3  lchedy | qokaiin
f83r.14 lchedy | qokaiin
```

These repeated field transitions suggest a form sequence, not random prose.
A relation/application slot closes, then a new item or instruction is opened.

### 6. Repeated inherited result

```text
f81v.18  CLOSE-C | CLOSE-C
f83r.27  CLOSE-I | CLOSE-I
```

Two adjacent identical committed cards are easiest to understand as two
parallel visible owners receiving the same state, or as a copied repeated
operation. They are awkward as natural-language accidental repetition.

## Astro as a separate local compiler

The Astro pages should not be forced through the prose card dictionary.

### f67r2

The page has multiple topology-owned namespaces: a 7-member circular set, a
12-member moon-associated set, other labels, and prose. The best parser is:

```text
LOCAL SELECTOR/CONCORDANCE
  layer owner → local label/value card
  prose block → operating note or legend
```

No surface fragment on f67r2 is imported as `VAL`, `LINK`, or a Biological
terminal without an exact joint-tuple bridge, which does not exist.

### f68r1

The one central plus 28 noncentral labelled stars form a spatial catalogue:

```text
CENTRAL OWNER  := one central label
STAR OWNER     := one local label per noncentral star
```

There is no authorial cyclic order for the 28 outer items. The model treats
them as an addressable roster, not a lunar sequence.

### f69v

The 28 radial entries and exact LONG/SHORT alternation are an ordered schedule:

```text
RING := CELL[1..28]
CELL := LOCAL_CARD + alternating layout class
```

`LONG` and `SHORT` are visual/rendering states only. They need not mean odd/even,
good/bad, day/night, or red/black. The earlier failed lag-14 and textual-marker
tests are consistent with the layout class being a copy/check aid rather than
semantic binary payload.

The three circle pages can still belong to a practical timing annex. They do
not yet provide a cross-reference from a particular plant or treatment record.

## Concrete source-language reconstruction

The easiest system for a workshop in c. 1420 to learn is not a wholly invented
language. It is an abbreviated source register with four layers:

1. **silent address** — the plant, apparatus, figure or star is already drawn;
2. **whole formula cards** — common recipe/technical phrases have conventional
   written cards;
3. **typed cells** — the terminal card both identifies the result/state class
   and commits the entry;
4. **copy variants** — wrappers and spacing vary by hand, position and register.

Plausible unencoded source expansions include:

```text
HEAD      take / set / enter / concerning the current item
ITEM      the selected simple, part, vessel, aperture, or listed object
VAL       an amount, degree, count, proportion, or table reference
TYPE      the unit/type tag controlling how VAL is read
LINK      of / with / in / through / for
STATE     prepared, heated, dried, moist, strained, ripe, suitable, etc.
REL-A/B   source, destination, part, alternative, or application relation
ACTION    prepare / wash / heat / pass / apply / set
COMMIT    write the resulting state into this cell and move on
```

This does **not** mean that one card has one English word. For example `HEAD`
could expand differently by register:

```text
Herbal B:  "take/for this simple ..."
Bio B:     "set/use the current channel or application ..."
Astro:     not licensed as the same card
```

Likewise `STATE` can denote a family of frequently abbreviated adjectival or
technical phrases rather than one adjective.

## Historical fit

This architecture combines historically ordinary mechanisms in an unusual
surface system:

- late-medieval medical manuscripts use dense abbreviation, including common
  recipe jargon such as *recipe* and *ana*;
- practical medical books can combine recipes, calendrical computation,
  astrology and treatment guidance;
- images and diagrams can serve as operational addresses rather than mere
  illustration;
- scribes can copy formulaic cards and layout patterns from exemplars without
  analytically decomposing every abbreviation.

Useful comparators include:

- the scholarly survey [Abbreviations in Medieval Medical Manuscripts](https://reunido.uniovi.es/index.php/SELIM/article/download/13301/12036/28090),
  which specifically discusses abbreviation of common medical-recipe jargon;
- the [Wellcome late-medieval computational/astrological medical manual](https://wellcomecollection.org/works/w9nkm98w),
  an early-fifteenth-century practical collection with calendar/astronomical
  material, zodiacal medicine and later medical recipes;
- scholarship on [physicians' folding almanacs](https://research-information.bris.ac.uk/en/publications/astrological-medicine-and-the-medieval-english-folded-alihanac/),
  showing practical medical use of compact astronomical/astrological reference
  structures.

These establish plausibility of the ecology and techniques only. They do not
identify the Voynich language, region, donor manuscript, or any card.

## Why this beats the nearest alternatives

### Versus compressed natural language alone

Natural language explains content diversity and hand-copying, but it handles
the following poorly without an added form compiler:

- 85 of 115 Bio fields have attached closure;
- major terminal cards can stand alone or take variable payloads;
- exact field-transition pairs recur while most lexical content changes;
- repeated identical committed cards occur adjacently;
- wrappers collapse very different-looking surfaces to exact cards;
- one physical line is plainly not one sentence.

### Versus pure semantic notation

Pure notation explains the form but struggles with:

- very large rare-card tail;
- plant-page descriptive diversity;
- line-like sequences rather than only tables;
- ordinary scribal variation and abbreviation behavior;
- the plausible need to encode names, qualities and instructions.

### Leading hybrid

```text
abbreviated technical language
  + picture-conditioned ellipsis
  + learned whole-card ledger
  + register-specific typed forms
  + positional renderer
```

This hybrid explains the most evidence with a mechanism a small workshop could
teach by exemplar.

## Contradictions and awkward observations

1. **No external card mapping.** All concrete expansions remain guesses.
2. **The inventory is not truly tiny.** There are 173 exact types in 381
   events; the model needs a small productive core plus a large copied tail.
3. **`VAL` is distributionally broad.** It occurs first, middle and last and
   never itself carries the formal close. It could be a pronoun/reference or a
   very common content card rather than quantity.
4. **`HEAD` is not obligatory.** Most fields lack it. This requires ellipsis,
   register-local heads, or several suppletive head cards.
5. **Terminal meanings are not separated.** Their distributions support typed
   closure, but not the proposed input/location/result distinctions.
6. **Herbal A remains underparsed.** Many cards are page-local and only broad
   descriptor roles are available.
7. **No WHAT/HOW/WHEN pointer.** The integrated medical-astrological story has
   no exact cross-page address.
8. **The Astro scripts can be independent.** Their inclusion may reflect a
   miscellany rather than one application system.
9. **Visible similarity is tempting but unsafe.** `qokeey`, `qokedy`, and
   `qokeedy` look related, but exact cards and formal states must remain primary.
10. **Zero/inherited fields are a powerful rescue rule.** It can overexplain
    short Bio cells unless it predicts independently identifiable parallel
    owners or repeated states.

## Discriminating predictions

These predictions were derived from the executable theory and should be tested
without changing the proposed card roles.

### P1 — typed terminal selection

Given only the nonterminal payload class and current register, the identity of
the terminal family should be predictable above a frequency/length baseline.
Specifically:

- `ACTION` should favor `CLOSE-B` more than generic terminals;
- `LINK` should favor `CLOSE-A` or the linked terminal families;
- `PROC` should favor `CLOSE-C`;
- apparatus/configuration payloads should favor `CLOSE-H/I`.

Failure would collapse the terminals toward punctuation.

### P2 — zero-field inheritance

A standalone terminal immediately after a filled field should repeat or
parallel the preceding field's visible owner more often than a length-matched
non-standalone terminal. The key fixed examples are consecutive `CLOSE-C` on
f81v.18 and `CLOSE-I` on f83r.27.

Failure would reject the inherited-argument rule.

### P3 — transition stencil

The two observed exact transitions should recur as construction families, not
merely exact phrases:

```text
linked/application terminal → ITEM or HEAD
procedure/action card → required-state terminal
```

The prediction concerns exact card classes and fields, not substrings.

### P4 — `TYPE–VAL–TYPE` operand symmetry

The two flanking `TYPE` occurrences should be owned by two comparable visible
objects, paths, compartments, or argument positions. If one occurrence clearly
belongs to only one object, reject equal/shared amount and retain only a typed
value frame.

### P5 — carried `HEAD`

On f82r.3→.4, counting the repeated exact `HEAD` once should align the record
with another known Bio stencil better than counting it twice. The repeated
surface should sit at a physical reflow boundary, not a semantic parallel.

### P6 — Herbal water without a water morpheme

If a fixed Herbal image is independently judged to show aquatic habitat,
washing, infusion, or a water-rich plant feature, the associated information
may be carried by a page-local card or omitted as pictured context. Common
`LINK`/`REF` cards should not uniquely track water across the four Herbal pages.

### P7 — twenty-card teaching deck

Across the fixed pages, the frequent exact cards should preserve broad parser
roles across hands/registers, while singleton cards substitute mainly within
the same stencil positions. If singletons destroy stencil regularity rather
than filling slots, the exemplar-ledger model weakens.

### P8 — Astro locality

Within each diagram, repeated surface families should recur at homologous local
roles more strongly than across f67r2/f68r1/f69v. A strong universal dictionary
across all three would falsify the separate-local-compiler choice.

### P9 — page image as silent address

Removing an explicit subject from the line parse should reduce redundancy:
page-internal lines should share more state/relation/value cards than exact
identity cards. If a recurrent exact noun-like card appears at a stable dossier
position on every line, the silent-address assumption is too strong.

### P10 — workshop learnability

Hand differences should concentrate in surface wrappers and entry rendering,
not in the order of the common exact parser cards. If card-transition order is
hand-private after register control, the shared workshop ledger becomes less
plausible.

## Current best pseudo-translation

At maximum YOLO resolution, a typical Biological record now reads:

> For the pictured installation/body/application, select or take the current
> item; enter its type and value; relate it to the indicated part, medium or
> setting; perform the local operation until the required state is reached;
> commit that state in the cell; carry unresolved material into the next cell
> or physical line.

A Herbal record reads:

> Concerning the pictured simple: enter its local class, qualities and
> habitat/medium or preparation relations; specify a value or proportion where
> required; commit only the fields that function as checklist entries.

An Astro array reads:

> For each diagram-owned position, copy the appropriate local lookup card;
> preserve the authored array order and layout class.

These are generative paraphrases, not plaintext translations.

## Bottom line

The next-evolution theory is not “Voynichese is a language with many affixes.”
It is:

> a workshop encoded ordinary technical source material into a mixed ledger of
> whole abbreviated cards, silent pictured arguments, typed committed fields,
> inherited/default values, and register-specific stencils; scribes then
> rendered those cards with positional wrapper variants and reflowed them
> around drawings made first.

The most useful concrete semantic gamble is the cluster:

```text
HEAD ≈ TAKE/SET/ENTER
VAL ≈ AMOUNT/DEGREE/INDEX
TYPE–VAL–TYPE ≈ SHARED OR MATCHED TYPED VALUE
ACTION→CLOSE-B ≈ PERFORM UNTIL/TO REQUIRED STATE
PROC→CLOSE-C ≈ PROCESS THEN CONFIRM CURRENT SETTING
LINK→CLOSE-A ≈ RELATED ITEM/MEDIUM THEN RESULT
```

It is coherent enough to generate the fixed pages and simple enough for
several scribes to learn. Its weakest point remains the absence of any external
card-to-source anchor.
