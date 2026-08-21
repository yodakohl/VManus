# V4 candidate — record-level translation

Status: **independent speculative sidequest; not a GDT result and not a
translation**. Confirmed English lexemes: **0**. Confirmed plaintext clauses:
**0**.

## Scope and selection

This pass used only the current route, the compact ten-page theory, and guarded
event slices. It did not read earlier candidates or the archive. The source
selector was an explicit locus allow-list with `f84` forbidden before row
materialization.

The translation unit is the paragraph-owned **record**, not the physical line
or field. The selected powered material is:

- f82r record 1 (all GDT327-materialized lines);
- f83r records 1 and 2, the strongest consecutive record pair on that folio;
- f10r record 2 as the Herbal control.

Only materialized exact-card events are represented. Thus nonconsecutive locus
numbers do not mean that intervening manuscript lines were silently translated;
they mean that those lines are outside this exact-card panel. The reconstruction
is end-to-end over the selected powered record, not over unmaterialized text.

## Lexicon frozen before reconstruction

The five portable cards and one construction below were frozen from the compact
current theory before the records were interpreted. They are structural tags,
not words or parts of speech.

| short ID | exact card | frozen tag | permitted source expansion |
|---|---|---|---|
| `QH` | `b5fcea1e...` | `ENTRY_OR_REACTIVATED_ADDRESS_HEAD` | enter, take up, activate |
| `LO` | `dcda95c8...` | `RELATION_OR_CLASS` | with, under, associated class |
| `AI` | `2f1c5e56...` | `PARAMETER_OR_REFERENCE` | amount, degree, index, setting |
| `Y` | `b921a237...` | `ITEM_OR_REFERENCE_TAG` | item, station, marked member |
| `CT` | `e0b630cb...` | `PROPERTY_OR_STATE` | prepared/configured condition |
| `X†` | any exact card with attached close | `PAYLOAD_CARD_AND_COMMIT` | enter this value and close the cell |

`Y–AI–Y` was frozen as a paired or typed parameter frame. Equal quantity was
not permitted as the default. All other cards remain opaque exact identities.

Notation below: `{abcdef}` is the first six hexadecimal characters of the exact
card ID, `|` is a field boundary, `†` is attached commitment, and `¶` is the
record end. Surface spellings are included only as handles; wrapper variants do
not create extra meanings.

## Layer 1 — exact-card parse

### f82r, record 1

```text
f82r.2  dchedy{259b2b}† | qolchedy{28ffbc}† |
         qokain{1645e6} Y{b921a2} qokeedy{7d2524}† |
         qokal{308e8e} lcheckhy{f329f2} lched{ba8142}
f82r.3  qokeey{0275fb} lcheckhedy{c1db6b}† |
         qokaly{4a7a63} solkaiin{2d2e37} chckhy{2cc8bb} QH{b5fcea}
f82r.4  QH{b5fcea} octheol{a8f891} chkeey{f0db6d} ldy{04a387}† |
         oteey{5d5e0b} qokal{308e8e} sheckhy{c1913e} qoky{276a7c}
f82r.7  dshedy{cbb42a}† |
         sotaiin{54d0e2} qokar{3ae9a1} shedy{bc4f1f}† |
         solshedy{daa134}† |
         qokeey{0275fb} qoky{276a7c} ls{5eff21} cheey{b5df91}
f82r.19 okain{1645e6} char{4d4559} okain{1645e6} qokeedy{7d2524}† |
         lchy{0ab57b}
f82r.23 cheey{b5df91} qcthey{6b89d6} qokeey{0275fb} lcheey{5fca8f}
         AI{2f1c5e} Y{b921a2} qokeeedy{d25110}† |
         lchedy{de7321}† | lar{29e0eb}
f82r.26 tshey{d4a31d} qokeedy{7d2524}† |
         cheal{dd0eca} lchedar{0f15ef} ches{db729b} AI{2f1c5e}
         oteey{5d5e0b} QH{b5fcea} okey{08bd5c}
f82r.27 pchedy{65df3c}† | rsheal{98bdc4} daldy{78b3b3}† |
         qokeedy{7d2524}† | rshedy{7f68f6}† | qoteedy{ff1783}† |
         qokeedy{7d2524}† | lochedy{f2af63}† ¶
```

The f82r.3/4 boundary is exact `QH→QH`: the first occurrence is field-final
and uncommitted; the second is field-initial and leads to a committed cell. In
this record it is best parsed once logically: an anticipatory line-end copy plus
the operative head after reflow. Both written occurrences are preserved above.

### f83r, record 1

```text
f83r.3  olkeedy{3b7094}† | qotal{90bcf0} chkeedy{a84fbe}† |
         Y{b921a2} AI{2f1c5e} Y{b921a2} lchedy{de7321}† |
         QH{b5fcea} qotal{90bcf0} dar{4d4559}
f83r.6  schedy{259b2b}† | chedchy{5e8441} qokal{308e8e}
         olchedy{28ffbc}† |
         QH{b5fcea} chedy{6f7ff8} qokeedy{7d2524}† |
         lchedy{de7321}† | qoky{276a7c}
f83r.8  pchedal{ba540d} otedy{c45eba}† |
         shecthedchy{348e81} qoky{276a7c} chedy{6f7ff8} chary{0bdc8b}
f83r.11 sor{7a4bb8} shedy{bc4f1f}† |
         QH{b5fcea} chkain{9da1b6} shcthey{6b89d6} qokedy{7db18b}† |
         okair{7d2404} sheedy{03626c}† | lchedy{de7321}† | lo{2b7fa9}
f83r.14 qokchedy{07913e}† | qokeedy{7d2524}† | shedy{bc4f1f}† |
         qokshedy{db167f}† | dal{dd0eca} lchedy{de7321}† |
         QH{b5fcea} CT{e0b630} dal{dd0eca} Y{b921a2}
f83r.15 AI{2f1c5e} shedal{abb23e} shecthy{cb57b6} Y{b921a2}
         tal{dd0eca} CT{e0b630} dalchdy{2bc2ed}† |
         qotchedy{4de12c}† | lchedy{de7321}†
f83r.16 tchedy{259b2b}† | qokchdy{87411f}† |
         cheedar{342c3f} chldaiin{d72f71} chedy{6f7ff8}
         qokain{1645e6} CT{e0b630} chealror{d788d8}
f83r.20 solkeedy{3b7094}† | qoteedy{ff1783}† |
         qokeey{0275fb} qokedy{7db18b}† |
         LO{dcda95} cheeety{9247e3} qokedy{7db18b}† |
         qoky{276a7c} AI{2f1c5e}
f83r.22 schedair{b154ff} otchedy{4de12c}† | qokeedy{7d2524}† |
         chedain{d784b2} chedy{6f7ff8} qotedaiin{1779de}
         otaiin{54d0e2} otedy{c45eba}† | ldy{04a387}†
f83r.24 soiiin{2c8252} CT{e0b630} chety{80ebbb} otaiin{54d0e2}
         olsaly{7811a7} shedy{bc4f1f}† ¶
```

### f83r, consecutive record 2

```text
f83r.25 qokeedy{7d2524}† |
         qolchey{e2eb77} qokeey{0275fb} qokedy{7db18b}† |
         chedy{6f7ff8} otal{90bcf0}
f83r.26 otchey{faf321} qokeey{0275fb} qoky{276a7c} LO{dcda95}
         shedy{bc4f1f}† | qokylddy{eb2e4b}†
f83r.27 dain{53cd06} chedy{6f7ff8} qokeedy{7d2524}† |
         shckhedy{d68bc8}† | shckhedy{d68bc8}†
f83r.28 AI{2f1c5e} cheeky{2c1a5f} sheey{92e438} qokedy{7db18b}† |
         shedy{bc4f1f}† | oldy{1b1ffd}†
f83r.35 AI{2f1c5e} cheky{d904bf} okeeol{daf32e} okain{1645e6}
         chdy{6f7ff8}
f83r.37 LO{dcda95} lkedy{b958a5}† | lchedy{de7321}† |
         qokol{232195} shedy{bc4f1f}†
f83r.38 or{7a4bb8} Y{b921a2} qockhey{ecce30} dairydy{8aedd1}†
f83r.39 qokain{1645e6} shey{b5df91} kain{9da1b6} chckhal{21ed28}
f83r.41 solkey{42cdc1} lchedy{de7321}† | qolkain{94df48} dal{dd0eca}
f83r.44 skar{883a67} shedy{bc4f1f}† ¶
```

### Herbal control: f10r, record 2

```text
f10r.6 ycheor{7249ed} CT{e0b630} chor{7a4bb8} cthaiin{f3c23f}
        qoctholy{af816c} Y{b921a2} Y{b921a2} AI{2f1c5e} Y{b921a2}
f10r.8 qotchor{10488b} chor{7a4bb8} otol{497cbd} LO{dcda95}
        cholor{dec401} LO{dcda95} AI{2f1c5e} dar{4d4559}
f10r.9 oykchor{27d97a} shor{7a4bb8} chor{7a4bb8} Y{b921a2}
        kaiiin{409de0} Y{b921a2} chodaiin{834825} ¶
```

Herbal remains one open dossier field per powered line. Unlike the Biological
records, no selected Herbal field has an attached commitment. Its continuity
is therefore dossier continuity, not a chain of checked cells.

## Layer 2 — historically plausible source-register expansion

This layer expands only inherited picture/register arguments (`P`), frozen
formal roles (`F`), and explicitly speculative practical-register language
(`S`). Brackets mark ellipsis or state inheritance. No substance, body part,
dose, direction, or disease is supplied.

### f82r record 1

> [For the pictured station/apparatus (`P`)] enter and commit two local values
> (`F`). Enter a tagged member and commit its configuration; append the open
> local specification (`F/S`). Enter and commit the next specification. Begin
> another configuration and carry its address head to the following written
> line; there reactivate that head, add two opaque settings, and commit the
> cell (`F`). Continue with its second open specification. Commit a short value;
> commit a parameterized cell and one singleton cell; leave the next associated
> specification open (`F`). Reuse the current item around an opaque relation and
> commit it, then leave a reference open. Add a longer cell containing a
> parameter and tagged member, commit it, commit a dependent singleton, and
> leave its last reference open. Commit another value; enter a long setting
> containing a parameter and a reactivated head but leave it open. Finish the
> record with seven successive committed local values (`F/S`).

The source-like continuity is a changing **active cell state**, not a chain of
fully recoverable sentences. The final closure run is compatible with checking
off remaining stations or outputs; it does not identify what they are.

### f83r record 1

> [For the pictured configuration (`P`)] commit the first value and the next
> linked value. Set two marked members under one parameter and commit their
> cell; activate the following entry and leave its local setting open (`F/S`).
> Commit a singleton; commit a related value; activate and commit a further
> setting, commit its dependent value, and leave a reference open. Commit one
> two-part cell, then leave the next multi-part cell open. Commit a value;
> activate a parameterized setting and commit it; commit two dependent cells,
> then leave a local reference open. Commit four singletons and one pair;
> activate a state-qualified item and carry that unfinished state into the next
> line (`F`). There specify its parameter, members, and two occurrences of the
> state card, then commit it and two dependent values. Commit two new cells;
> leave a longer state-bearing specification open. Commit two values, commit a
> short pair, relate or class one further setting and commit it, then leave its
> parameter open. Commit the following values and a parameter-bearing cell;
> close the record with a state-qualified cell (`F/S`).

Here f83r.14→15 supplies the best record-scale state continuation: the
uncommitted `QH–CT–...–Y` tail is followed by `AI–...–Y–...–CT–...†`.
It is economical to inherit one active state frame across the physical break.
That does **not** prove that `CT` names a preparation rather than a formal
state code.

### f83r record 2

> Commit an initial value; fill and commit the next cell, leaving its dependent
> pair open. Complete a longer relation-bearing cell and commit its dependent
> value. Commit a three-card setting and repeat the same singleton commitment
> twice. Enter a parameterized setting and commit it, then commit two dependents.
> Open another parameterized specification; commit a relation-bearing value and
> two dependents. Commit a tagged setting, leave the next specification open,
> add one committed pair and one open pair, and close the record with a final
> commitment (`F/S`).

The immediate restart at f83r.25 does not inherit the previous record's active
state: the paragraph boundary resets the dossier and begins with a fresh closed
value. This is a stronger reset than any ordinary physical line boundary.

### f10r record 2

> [For the pictured plant/simple (`P`)] record its state or quality, followed by
> an opaque local description. Set three tagged members around a parameter
> (`F/S`). Continue the dossier with an opaque item, a relation, a second item,
> a second relation, and its parameter. Add a final open description containing
> two further tagged references, then end the dossier (`F`).

The Herbal record has continuity without cell commitments. The picture can
supply the silent subject throughout, while the three lines accumulate
properties or uses. This is historically compatible with a simple's dossier,
but the cards do not decide between properties, preparations, habitats, or
uses.

## Layer 3 — fluent pseudo-translation

These are deliberately marked pseudo-translations: they make the inferred
record logic readable while refusing lexical identification.

### f82r

> For the apparatus already shown, register the first two settings. Assign the
> tagged configuration and close it; add its remaining specification. Start the
> next setting, carrying its active head across the line, then complete and
> close it. Continue through the dependent entries, keeping unfinished
> specifications open. Enter the stated parameter where indicated, and finish
> by confirming the remaining seven local cells.

### f83r, record 1

> For this pictured configuration, confirm the initial values. Place the two
> marked members under their common parameter, close that cell, and open the
> next setting. Work through its dependent cells in order. Activate the stated
> condition, carry it into the following line, add its parameter and tagged
> members, and confirm the result. Continue with the related and parameterized
> settings, then close the record on the final conditioned entry.

### f83r, record 2

> Begin a fresh configuration. Confirm the first values, complete the linked
> setting, and repeat the paired confirmation where shown. Enter the next
> parameterized setting, then its related dependents. Leave the indicated
> specifications open until their continuations are supplied, and confirm the
> last cell to end the record.

### f10r

> For the simple shown here, note its condition and the first specification.
> Record the tagged members under their parameter. Continue with the related
> specifications and parameter, add the final references, and leave the dossier
> complete at the paragraph end.

## What record continuity contributes

### `qokaiin` / `QH`

Record context strengthens **entry or reactivated address head**. The f82r.3/4
repeat is the sole exact same-record boundary repeat in the current panel; its
field-final then field-initial placement repairs naturally as anticipatory
reflow. In f83r record 1, `QH` repeatedly begins a new field after earlier cells
are committed. A continuous-liquid reading can explain the f82r repetition,
but explains the repeated field-initial resets less economically and has no
independently owned liquid referent. Decision: retain `ENTRY/REACTIVATE`, with
no lexical TAKE/USE claim.

### `L/O` / `LO`

Record context gives only weak semantic leverage. In Herbal it lies inside the
parallel `X–LO–X–LO–AI` span; in f83r it appears both at a field edge and
internally before commitment. This favors a broad relation/class function over
one fixed conjunction, but a stencil divider fits equally well. Decision:
retain `RELATION_OR_CLASS`; do not narrow to WITH, IN, AND, or WATER.

### `AIIN` / `AI`

The f83r `Y–AI–Y` committed cell is the cleanest paired frame. Elsewhere `AI`
opens or ends long record segments and can be inherited into a continuing
state frame. That mobility rejects a narrow infix-dose rule and favors a broad
parameter/reference card. Herbal supplies no independently symmetric operands,
so equal amount remains unsupported. Decision: `PARAMETER_OR_REFERENCE`, with
quantity only one subordinate possibility.

### `Y`

`Y` repeats around `AI`, occurs in the f83r.14/15 state continuation, and
clusters three times in the Herbal dossier. Record continuity makes a generic
tag/member/reference more coherent than three independent lexical items. But
its wrapper mobility and broad placement also fit a purely formal slot marker.
Decision: `ITEM_OR_REFERENCE_TAG`; no entity name.

### `CTHY` / `CT`

`CT` is not isolated to Herbal: it participates in the f83r.14/15 unfinished
state frame and returns near record closure. This makes property/configuration
state the most coherent discourse role. Yet no pictured before/after state
owns it externally. Decision: retain `PROPERTY_OR_STATE`, explicitly not DRY,
PREPARED, HOT, or any other English quality.

## Ellipsis, inheritance, commitment, and transition model

```text
RECORD START
  inherit pictured subject + register template
  initialize active dossier/configuration
      ↓
OPEN FIELD
  inherit subject and any uncommitted head/state
  append opaque item/relation/parameter/state cards
      ↓
ATTACHED CLOSE
  commit exact payload-bearing cell; do not erase its identity
      ↓
PHYSICAL LINE BREAK
  reflow only; active state may continue or an anticipatory head may repeat
      ↓
PARAGRAPH BREAK
  reset active record; no inherited state crosses by default
```

The clearest possible ellipses are the pictured subject for an entire record,
the once-only logical `QH` across f82r.3/4, and the unfinished `QH–CT` frame
across f83r.14/15. These are record-level repairs, not universal rules.

## Semantic reconstruction versus nonsemantic form filling

Two accounts were compared against exactly the same parse.

| criterion | practical source-register expansion | nonsemantic form filling |
|---|---|---|
| attached closes and short B cells | explained as committing payload cells | explained directly as checking stencil cells |
| open Herbal lines | dossier accumulation | open exercise rows |
| f82r `QH` carry | anticipatory carry of active entry head | copied boundary cue or dittography |
| f83r.14/15 state continuity | inherited state/configuration | repeated slot family across rows |
| paragraph reset at f83r.24/25 | new practical record | new form block |
| picture as omitted subject | economical in a practical register | picture can simply cue a layout exercise |
| lexical risk | high: every fluent verb is speculative | low: no meanings needed |
| external semantic anchor | none | none required |

**Decision: the nonsemantic form-filling account is the better explanation of
the internal evidence alone, narrowly but clearly.** It accounts for every
closure, reset, reflow, and repeated card without positing unobserved actions or
substances. Record continuity improves the *coherence* of the practical
source-register expansion, especially for `QH` and `CT`, but does not identify
any meaning. The best combined theory is therefore asymmetric:

```text
established descriptive layer: paragraph-owned form filling with exact cards
best historical expansion conditional on semantics: practical medical register
plaintext/lexical claim: none
```

This result weakens any claim that V4 has moved closer to plaintext. It
strengthens only the record-aware compiler: picture/register inheritance,
payload-bearing committed cells, physical reflow, occasional ellipsis, and a
paragraph reset are jointly more adequate than line-by-line pseudo-sentences.

## Discriminating next prediction

On fresh authorized records, freeze `QH`, `AI`, `Y`, and `CT` before opening the
target. The semantic account should outperform a page/frequency-matched stencil
model in predicting which open state frame resumes after a line break and which
parameter/tag combination precedes a particular exact closer. If it does not,
retain form filling and withdraw discourse semantics beyond anonymous state
continuity.
