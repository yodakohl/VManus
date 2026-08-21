# V12 R1 — Lehrmeister einer Schreibwerkstatt um 1420

Date: 2026-08-21

Status: independent speculative sidequest candidate; not a GDT result and not
a translation.

## Forced decision

**Winner: `NOT_DISTINGUISHABLE_WITH_TWO_OCCURRENCES`.**

The teachable fact is narrower than the current shared-reference gloss. A
master can teach the exact whole-card formula

```text
Y -> AIIN -> Y
```

and can correct its copying across two registers. The ten-page evidence cannot
tell him whether its source function is shared reference, equality, a dyadic
relation, a checklist coordinate, or ordinary formulaic prose. The two outer
Y cards have the same opaque exact identity, but no independently identified
left and right operands. Their field placement and following closure also
differ. Therefore recurrence establishes a portable formula, not its expansion.

This decision withdraws no formal fact. It only declines to turn the exact
repetition into `SAME`, `EQUAL`, `PAIR`, or `INDEX`.

## Evidence and access boundary

I used only the frozen ten-page universe:

```text
Herbal:       f10r f11r f55v f56r
Biological:   f81v f82r f83r
Circle:       f67r2 f68r1 f69v
```

The source-native line census selected 320 ZL3b lines through guarded
`query-tsv`; the exact-card census selected 381 GDT327 events on the seven prose
pages. Every query had an explicit page allow-list and `--forbid-prefix f84`.
No f84/f84r row, image, transcription, formal value, or sibling V12 report was
read. ZL3b is used as one surface reading, not as independent confirmation from
IT2a or RF1b. The circle pages have no GDT327 event layer and contribute no
imported prose-card identity.

Card names below are formal aliases only:

```text
Y     = b921a237be883a820352
AIIN  = 2f1c5e56e8f0ff459065
```

No substring, sound, edit similarity, or semantic resemblance was used.

## Exact reconstruction of the two records

The following are the complete ZL3b `eva_clean` physical lines of the two
paragraph records containing the formula. A line is not assumed to be a
sentence.

### f10r record 2: lines 6–12

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.7  dchy qokchol y kchaiin yty daiin cth dain dair am
f10r.8  qotchor chor otol chol cholor chol daiin dar
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
f10r.10 oqotor otor cfhy cthor osain ytoiin
f10r.11 otchoshor qoty qotor cthyd otar
f10r.12 odaiin daiin qotchy qotor
```

The GDT327-covered target line contains one open field:

```text
f10r.6 FIELD 1 OPEN:
  ycheor cthy chor cthaiin qoctholy dy{Y} chy{Y} taiin{AIIN} shy{Y}
                                            [Y -> AIIN -> Y]
```

The recurring path is groups 7–9, not groups 6–8. This matters: it is preceded
immediately by another exact Y. The whole tail is therefore `Y Y AIIN Y`, and
a proposed left operand cannot be selected merely by choosing the most
convenient one of the adjacent equal cards. There is no attached close after
the formula; its final Y is field-final and line-final.

### f83r record 1: lines 1–8

```text
f83r.1 tchedy lpchedy opedy chepol pchedar shedy qopchedy
f83r.2 sol cheey qokaiin shol lchs shey qoteedy rches ar chedy dor
f83r.3 olkeedy qotal chkeedy chey daiin chey lchedy qokaiin qotal dar
f83r.4 qokshedy chedy qokedy chkedy daiin shetar shedy qekaiin chedy
f83r.5 deey qotaiin checkhy qoty cheg shedy qokeey rchedy qoteedy lo
f83r.6 schedy chedchy qokal olchedy qokaiin chedy qokeedy lchedy qoky
f83r.7 solshed lsheedy qeeedy qoky o qol rsheedy qokedy qoteedy qoteedy
f83r.8 pchedal otedy shecthedchy qoky chedy chary
```

The target line has four GDT327 fields:

```text
f83r.3:
  olkeedy{CLOSE}
  | qotal chkeedy{CLOSE}
  | chey{Y} daiin{AIIN} chey{Y} lchedy{CLOSE}
  | qokaiin qotal dar
    [Y -> AIIN -> Y]
```

Here the path is groups 4–6 and starts field 3. Its second Y is followed by an
opaque `lchedy` payload card carrying attached DY closure. Thus closure belongs
to the following card, not to Y, AIIN, or the three-card formula itself.

## All exact occurrences

There are 18 Y events on six pages and 20 AIIN events on all seven prose pages.
`FIRST/MIDDLE/LAST` is position inside the GDT327 field, not a grammatical POS.
`r/f` gives record and field ordinal. Surface forms are shown only to make the
wrapper realization auditable.

### Y: 18 events

| locus:g | r/f | position | surface | immediate field context |
|---|---:|---|---|---|
| f10r.6:6 | 2/1 | MIDDLE | dy | qoctholy _ chy |
| f10r.6:7 | 2/1 | MIDDLE | chy | dy _ taiin |
| f10r.6:9 | 2/1 | LAST | shy | taiin _ `|` |
| f10r.9:4 | 2/1 | MIDDLE | chy | chor _ kaiiin |
| f10r.9:6 | 2/1 | MIDDLE | dy | kaiiin _ chodaiin |
| f11r.4:2 | 1/1 | MIDDLE | chy | dchol _ kchy |
| f11r.4:4 | 1/1 | MIDDLE | dy | kchy _ daiin |
| f11r.7:4 | 1/1 | LAST | dy | cthy _ `|` |
| f55v.11:9 | 1/2 | MIDDLE | y | or _ orain |
| f81v.18:2 | 1/2 | FIRST | chey | `|` _ ol |
| f82r.2:4 | 1/3 | MIDDLE | dy | qokain _ qokeedy+CLOSE |
| f82r.23:6 | 1/1 | MIDDLE | chey | daiin _ qokeeedy+CLOSE |
| f83r.3:4 | 1/3 | FIRST | chey | `|` _ daiin |
| f83r.3:6 | 1/3 | MIDDLE | chey | daiin _ lchedy+CLOSE |
| f83r.14:10 | 1/6 | LAST | sy | dal _ `|` |
| f83r.15:4 | 1/1 | MIDDLE | chey | shecthy _ tal |
| f83r.38:2 | 2/1 | MIDDLE | chey | or _ qockhey |
| f83r.54:4 | 4/1 | MIDDLE | chey | dain _ ldalor |

Position census: 2 FIRST, 13 MIDDLE, 3 LAST. Three of the 15 Y events with an
available following card are followed by an attached close; the formula has
that consequence only on f83r.

### AIIN: 20 events

| locus:g | r/f | position | surface | immediate field context |
|---|---:|---|---|---|
| f10r.2:9 | 1/1 | MIDDLE | daiin | oky _ etyd |
| f10r.6:8 | 2/1 | MIDDLE | taiin | chy _ shy |
| f10r.8:7 | 2/1 | MIDDLE | daiin | chol _ dar |
| f11r.4:5 | 1/1 | LAST | daiin | dy _ `|` |
| f55v.5:2 | 1/1 | MIDDLE | chaiin | qokaiin _ ykain |
| f55v.5:6 | 1/2 | FIRST | daiin | `|` _ chedy |
| f55v.11:5 | 1/2 | FIRST | aiin | `|` _ okal |
| f56r.5:4 | 1/1 | LAST | daiin | chodaly _ `|` |
| f56r.19:3 | 1/1 | LAST | daiin | keol _ `|` |
| f81v.7:4 | 1/1 | MIDDLE | daiin | sheckhal _ qokeedal |
| f81v.7:6 | 1/1 | MIDDLE | daiin | qokeedal _ chckhy |
| f82r.23:5 | 1/1 | MIDDLE | daiin | lcheey _ chey |
| f82r.26:6 | 1/2 | MIDDLE | aiin | ches _ oteey |
| f83r.3:5 | 1/3 | MIDDLE | daiin | chey _ chey |
| f83r.15:1 | 1/1 | FIRST | saiin | `|` _ shedal |
| f83r.20:9 | 1/5 | LAST | saiin | qoky _ `|` |
| f83r.28:1 | 2/1 | FIRST | saiin | `|` _ cheeky |
| f83r.35:1 | 2/1 | FIRST | saiin | `|` _ cheky |
| f83r.48:5 | 3/1 | LAST | aiin | chdal _ `|` |
| f83r.54:1 | 4/1 | FIRST | daiin | `|` _ ol |

Position census: 6 FIRST, 9 MIDDLE, 5 LAST. In the 15 cases where AIIN has a
following card inside its field, that next card is never an attached close.
The card is too mobile to establish an obligatory infix, equality sign, or
fixed checklist column.

## Antecedents, operands, and consequences

### f10r

- The formula is in the first physical line of record 2, so no earlier line in
  that record supplies an overt active value.
- Its immediate left context is another exact Y. Before that stand five opaque
  cards, one of which is the portable CTHY card, but none has an independently
  established value or referent.
- Both candidate outer nodes are therefore formally identical and the left
  boundary is ambiguous: `... Y [Y AIIN Y]` is as exact as the unsegmented
  four-card tail.
- The final Y ends the open field. There is no local commit card and no overt
  downstream operation licensed by the exact structure.

### f83r

- The formula begins a new field after two already closed fields on the line.
  Its immediate predecessor is a different opaque card with attached close;
  that closure cuts rather than proves an inherited operand.
- The two Y cards have the same exact identity and the same `che` wrapper. No
  image annotation or neighboring exact card distinguishes a left object from
  a right object.
- A distinct LCHE-family card follows and commits the cell. That establishes a
  committed Bio cell, not that the formula itself expresses equality or
  reference.
- A fourth field then begins with qokaiin. It is downstream continuation, but
  no exact consequence ties its payload to either Y.

The only shared local fact is the ordered exact identity `Y AIIN Y`. The two
records do not share an independently known antecedent, symmetric pair, value,
closure behavior, field coordinate, or downstream consequence.

## Matched path and placement controls

Across the 135 fixed-page GDT327 fields there are 164 within-field three-card
windows and 163 distinct exact triples. `Y-AIIN-Y` is the only exact triple
that recurs on two pages. This makes it a real portable formula candidate.
It does not identify the formula's function.

The most relevant controls are:

- Eight windows have the abstract `A-B-A` shape. Repeated outer identity is
  therefore not unique to this formula.
- Four windows specifically have `Y-X-Y`: the two targets, `Y-409de023-Y` on
  f10r.9, and `Y-b2812c82-Y` on f11r.4. Y can frame more than AIIN.
- f81v.7 has the converse recurrence `AIIN-93f69c38-AIIN`. AIIN can itself be
  the repeated outer card rather than the binder in the middle.
- The frequency-matched portable L/O card has 19 events and is also mobile:
  3 FIRST, 14 MIDDLE, 1 LAST, 1 ONLY. Mobility is not special evidence that
  AIIN retrieves a value.
- The target placement changes from `MIDDLE-MIDDLE-LAST` at the Herbal field
  tail to `FIRST-MIDDLE-MIDDLE` at the Bio field head. It is not a fixed field
  coordinate.
- The surface wrapper sequence changes from `ch-t-sh` to `che-d-che`. Exact
  card identity survives while visible wrappers do not agree.
- The Herbal occurrence is open; the Bio occurrence is followed by a separate
  attached-DY close. A closure rule cannot be part of the triple.

Thus the duplicate is too exact to dismiss as random surface resemblance, but
its structural consequences are too variable to choose a semantic
architecture.

## Renderer and segmentation audit

`RENDERER_OR_SEGMENTATION_ARTIFACT` is strongly disfavored:

1. all six target events resolve to the same three exact joint-tuple identities
   in the same order;
2. the two occurrences use different visible wrapper sequences;
3. the path remains inside one field in each record;
4. the attached close on f83r belongs to the following LCHE card, while f10r
   has no corresponding close.

There is nevertheless a real segmentation warning on f10r: because an extra Y
precedes the path, no semantic argument boundary follows from the repeated
identity alone. The safe segmentation is observational—groups 7–9 are the
cross-page recurring window—not a claim that group 6 is outside its source
construction.

## Forced comparison of the frozen architectures

| architecture | what it explains | decisive problem | disposition |
|---|---|---|---|
| `SHARED_ACTIVE_REFERENCE` | a repeated middle card between two Y nodes | no independently identified active value or common antecedent | possible, not selected |
| `PAIRED_EQUAL_VALUE` | identical outer cards can look symmetric | no supported distinct operands; no amount/status evidence; contexts are asymmetric | rejected as default |
| `DYADIC_RELATION_FRAME` | exact `A-B-A` shape and Bio committed cell | outer endpoints are not distinguishable; seven other ABA windows exist | possible, not selected |
| `INDEXED_CHECKLIST_FRAME` | portable formula in a learned form system | head/tail placement and closure differ; no repeated ordinal is established | possible, not selected |
| `ORDINARY_FORMULAIC_PROSE` | rare exact phrase recurrence across Herbal and Bio | cannot be separated from a notational whole-card formula internally | live rival |
| `RENDERER_OR_SEGMENTATION_ARTIFACT` | would explain surface variation cheaply | exact tuple sequence survives divergent wrappers and field parsing | disfavored |
| `NOT_DISTINGUISHABLE_WITH_TWO_OCCURRENCES` | preserves the exact portable formula without inventing function | deliberately yields no source expansion | **selected** |

The winner is not a claim that all candidates are equally likely. Renderer
artifact and explicit equal allocation are substantially weaker. It is the
claim that the remaining reference/dyadic/index/prose fork is not identified
by these two witnesses.

## Lehrregel: forward production

A master can give the following executable instruction without knowing or
pretending to know the expansion:

```text
WHEN the exemplar calls for FORMULA F12:
  1. copy exact card Y;
  2. immediately copy exact card AIIN;
  3. immediately copy exact card Y again;
  4. keep all three cards in one field and in that order;
  5. apply the local hand/register wrappers to each card independently;
  6. take openness or commitment from the surrounding register exemplar,
     never from F12 itself.
```

For the two surviving exemplars this specializes to:

```text
Herbal-A exemplar: ... Y [Y AIIN Y] <open field/line end>
Biological-B:      | [Y AIIN Y] LCHE-COMMIT | continuation
```

This is a plausible workshop lesson because it uses a whole-card model, an
exact order, and a register-specific ending. It asks no apprentice to solve a
cipher or know whether AIIN means value, equality, reference, or nothing of
the kind.

## Controlled reverse reading

The corresponding reverse procedure is intentionally narrow:

```text
1. Normalize visible wrappers to exact cards.
2. If and only if three consecutive cards inside one field are Y, AIIN, Y,
   mark RECURRING_OPAQUE_FORMULA_F12.
3. Record its placement separately:
     f10r = open Herbal field tail;
     f83r = Bio field head before a distinct committed payload.
4. Do not expand F12 as SAME, EQUAL, BETWEEN, PAIR, AMOUNT, INDEX, or prose.
5. Do not attach the following Bio close to the formula.
```

Maximum responsible paraphrase:

> Repeat the learned three-card formula here; interpret its operands and
> source wording from an external exemplar that is presently absent.

That is an operational reading, not plaintext.

## Apprentice errors and corrections

These are concrete errors the rule predicts:

1. **Wrapper harmonization.** A novice copies `CHY-TAIIN-SHY` everywhere or
   makes all three wrappers alike. Correction: compare exact cards, then restore
   the local Herbal/Bio rendering habit.
2. **Loss of the middle card.** Seeing equal outer cards, the novice writes
   `Y-Y`. Correction: AIIN is obligatory in the frozen whole-card exemplar.
3. **Reversal.** The novice copies `AIIN-Y-Y` or `Y-Y-AIIN`. Correction: point
   to the invariant ordered triple, not to a guessed spoken phrase.
4. **Haplography at f10r.** The adjacent `Y Y` is collapsed to one Y.
   Correction: count four tail cards `Y-Y-AIIN-Y`; the recurring window starts
   at the second of the adjacent Ys.
5. **Dittography at f10r.** The novice treats the repeated Y as a cue to add
   another copy. Correction: copy the whole line exemplar and mark the
   three-card window only after exact normalization.
6. **Imported closure.** A novice appends the Bio LCHE-COMMIT to the Herbal
   formula, or omits it on f83r because it is absent on f10r. Correction:
   closure belongs to the register field, not F12.
7. **Fixed-slot relocation.** A novice moves every F12 to field head or tail.
   Correction: the two exemplars license both placements; placement is copied
   from the local stencil.
8. **Semantic overcorrection.** A corrector changes neighboring cards to make
   two imagined amounts or operands symmetric. Correction: no semantic
   symmetry has been established; preserve the diplomatic sequence.

Errors 1, 4, 5, and 6 are especially diagnostic. They follow from the actual
wrapper, adjacency, and closure differences rather than from a modern decoding
story.

## Fixed-page predictions and falsifiers

Within the already fixed pages, a future independent re-segmentation or hand
audit should test these predictions without mining new forms:

1. Exact-card normalization should retain both target triples despite wrapper
   disagreement. Failure would reopen renderer/segmentation artifact.
2. The f10r group-6/group-7 double Y should remain two source groups. A secure
   codicological merger would invalidate the present path boundary.
3. The f83r LCHE close should remain attached to group 7, not to the second Y.
   Reassignment would change the forward rule.
4. No common fixed field ordinal should emerge for the two formula events.
5. No independently owned picture or exact neighboring card should identify
   two symmetric operands or one shared value. If such an endpoint appears,
   rerank `SHARED_ACTIVE_REFERENCE`, `PAIRED_EQUAL_VALUE`, and
   `DYADIC_RELATION_FRAME` under the frozen protocol.
6. A workshop copy test should produce wrapper and closure errors more readily
   than exact-card reordering if F12 was memorized as a whole formula. This is
   a prospective production prediction, not evidence already observed.

## R1 conclusion

As a master, I would put `Y-AIIN-Y` in the common exemplar ledger as **F12, an
opaque three-card formula with register-specific realization**. I would not
teach `AIIN = same value`, because a pupil cannot verify that lesson from either
record. I would teach what can be checked: exact identity, order, field
containment, local wrapper choice, and the independence of the following Bio
close.

The repeated path is genuine and worth preserving. Its function is not yet
distinguishable with two occurrences.
