# Sidequest V13 — R2 medical/Herbal relation expansion

Date: 2026-08-21

Perspective: **R2, medical and Herbal scribe ca. 1420**.

Status: exploratory working theory, not a GDT result, plaintext translation,
lexeme identification, or language identification. English and Latin phrases
below name source-function classes only. The exact card is
`dcda95c81a5460feb191`; `L/O` is a neutral alias.

## Scope and evidence discipline

I used only the fixed prose pages `f10r`, `f11r`, `f55v`, `f56r`, `f81v`,
`f82r`, and `f83r`, selected from GDT276 and GDT327 through
`./vmanus-exp query-tsv` with repeated exact `--allow` values and
`--forbid-prefix f84`. The selected GDT327 slice has 381 events. The three
fixed circle pages have no GDT327 events and contribute no L/O occurrence.
`f84` and `f84r` were not accessed. No V13 sibling result was read.

Historical comparison is deliberately generic. Fifteenth-century medical
collections could mix herb lists, recipes, weights, calendars, and other
practical material, as in the catalogue description of
[Harley MS 2381](https://searcharchives.bl.uk/catalog/040-002048212), while a
mid-fifteenth-century collection could arrange many short recipes by bodily
region and freely include nonmedical items, as in the
[Huntington medical-recipe manuscript](https://hdl.huntington.org/digital/collection/p15150coll7/id/49488/).
Actual recipe incipits also show ordinary relational material such as *de*,
*ad*, *cum*, and partitive phrases; see the manuscript descriptions collected
by [Edinburgh University Library](https://archives.collections.ed.ac.uk/subjects/25913).
These comparators make the source classes ordinary for the period; they do not
identify any Voynich card.

## Decision

The best R2 expansion is:

```text
L/O ~= WITH THE CURRENT PREPARATION / COMBINE OR APPLY TOGETHER WITH
        and, when an operand is omitted, WITH IT LIKEWISE / AS ABOVE
```

Its invariant operation is narrower than generic association:

```text
COMITATIVE_BIND(active preparation-or-item, local or inherited participant)
```

Depending on the upstream phrase, this could have been realized by a broad
*cum/with*, by an additive recipe formula equivalent to “together with,” or in
application context by “apply with/to.” It is not three decoded senses. The
card tells the workshop scribe to bind another participant into the currently
active preparation or application frame; register and surrounding cards
supply the fluent preposition.

Working confidence:

- comitative/additive medical relation as the source class: **0.64**;
- the more specific phrase “with the current preparation”: **0.49**;
- literal *cum*, *with*, or any one historical word: **0.10 or less**.

The leading hypothesis is preserved because it covers all nineteen events
with one ellipsis rule and gives better continuous recipe readings than
`OF/FROM`, `IN A MEDIUM`, `PART`, or `ALSO` alone. It is not claimed proven.

## The single inherited-operand rule

```text
STATE = (active item/preparation A, active relation R, pending participant B?)

explicit X — L/O — Y : bind Y with/to X inside A; keep R active
field-initial L/O — Y : inherit X/A from the immediately active cell; bind Y
field-final X — L/O   : bind X and leave Y pending for the continuation
one-card L/O          : repeat R with the participants licensed by the
                        immediately preceding cell (“with it likewise”)

RESET: a new paragraph/record clears inherited participants.
KEEP: a field or physical-line boundary alone does not necessarily clear them.
```

This is learnable from one card: copy L/O between overt participants; if the
entry stencil already supplies one or both, omit them; if the card ends an
open line, complete its target in the next continuation. The bare `qol` at
`f81v.7` is therefore not an empty preposition. It is an elliptical recipe
instruction: **repeat the just-established comitative/application relation for
the current cell**.

## Complete nineteen-occurrence concordance

`C` marks an attached `DY/B3` commitment on the final exact card. `X` denotes
opaque payload; familiar aliases such as AIIN and Y remain anonymous exact
cards. “Record context” identifies the actual paragraph record, not a presumed
semantic recipe boundary.

| # | locus, record.field | complete field containing L/O | position and R2 reading |
|---:|---|---|---|
| 1 | f10r.5, 1.1 | `qokchy qotchol L/O CTHY` | medial, open: local substance/detail **with** a stated condition |
| 2 | f10r.8, 2.1 | `qotchor chor otol L/O cholor L/O AIIN dar` | first of two: bind the preceding specification **with** the next participant |
| 3 | f10r.8, 2.1 | same complete field | second of two: add that participant **with/as governed by** the following standard/value |
| 4 | f81v.2, 1.2 | `okaiin kair okal sar L/O kain olkain al L/O rol dl` | first of two, open Bio field: combine the first local participant with the next |
| 5 | f81v.2, 1.2 | same complete field | second of two: add/bind a further local participant; no commitment yet |
| 6 | f81v.7, 1.1 | `olor L/O sheckhal AIIN qokeedal AIIN chckhy schedy[C]` | medial: relation introduced before two parameter-like packets and a committed result |
| 7 | f81v.7, 1.2 | `L/O` | only card: repeat the relation and inherited participants of field 1, “with it likewise” |
| 8 | f81v.17, 1.2 | `chedy L/O shedy[C]` | medial, pre-close: bind local item to the selected committed preparation/state |
| 9 | f81v.18, 1.2 | `Y L/O cheky L/O shedy[C]` | first link in the repeated chain: bind explicit Y to local participant |
| 10 | f81v.18, 1.2 | same complete field | second link, pre-close: add the committed participant/result to the same frame |
| 11 | f81v.21, 1.3 | `chedy qolky lchedal L/O otar` | medial, open: combine the preceding local packet with the final participant |
| 12 | f81v.24, 1.2 | `qokal okeey L/O cheedy[C]` | medial, pre-close: associate/application-bind the local pair to the committed participant |
| 13 | f83r.20, 1.4 | `L/O cheeety qokedy[C]` | field-initial: inherit the active item from fields 1–3 and add the overt participant/result |
| 14 | f83r.26, 2.1 | `otchey qokeey qoky L/O shedy[C]` | pre-close: join the accumulated preparation to the terminal committed value |
| 15 | f83r.37, 2.1 | `L/O lkedy[C]` | field-initial plus close: with the inherited preparation, select this committed participant |
| 16 | f83r.48, 3.1 | `dal L/O lol chdal aiin` | medial, open: combine the initial participant with the following specification |
| 17 | f83r.49, 3.1 | `L/O daiiin chedy` | line/field-initial: inherit the active preparation from f83r.48 and continue its relation |
| 18 | f83r.52, 4.1 | `solkeey qekey raly L/O` | field-final, open: relation target is pending into the next line |
| 19 | f83r.54, 4.1 | `AIIN L/O dain Y ldalor` | medial: the line-initial AIIN is a good candidate completion of the pending target from f83r.52; a new binding then follows |

The census is exact: f10r 3, f81v 9, f83r 7; 14 MIDDLE, 3 FIRST, 1 ONLY,
and 1 LAST. Six occurrences form three repeated-L/O fields. Five have an
immediately following attached terminal card: the second L/O at f81v.18 plus
the four other constructions at f81v.17, f81v.24, f83r.26, and f83r.37.

## Required difficult constructions

### `X–L/O–Y–L/O–CLOSE`

The exact f81v.18 field is `Y–L/O–cheky–L/O–shedy[C]`. It is most naturally a
compact multi-participant preparation or application frame:

> For the marked item, combine/apply it with participant A and likewise with
> the selected committed participant B.

This is not an assertion that `cheky` or `shedy` names a drug, body part, or
result. The attached terminal identity carries the opaque selection; L/O only
adds it to the current frame.

### The four other pre-close constructions

- `f81v.17`: `X–L/O–X[C]` — select X **with** the committed participant.
- `f81v.24`: `X–X–L/O–X[C]` — the accumulated preparation is **with/applied
  to** the committed participant.
- `f83r.26`: `X–X–X–L/O–X[C]` — after several preparation details, bind the
  last committed value into that preparation.
- `f83r.37`: `L/O–X[C]` — inherit the preparation and relation, then enter its
  committed participant.

The last case shows why a bare spoken preposition is insufficient but does not
defeat a recipe abbreviation with an active frame.

## Herbal versus Biological transfer

On Herbal f10r, there are no local commitments in the two L/O-bearing records.
The best expansion is descriptive or compositional: a plant part, quality,
preparation, habitat, or use is stated **with/in relation to** another. The
picture owns the article topic, but it does not identify either operand.

On Biological f81v/f83r, 12 of 16 L/O events lie in fields that eventually
commit, and five directly precede a committed terminal card. Here the same
operation is naturally read as **combine with / apply with or to / enter under
the same preparation**. The register supplies the application flavour; the
card itself need not mean APPLY.

This is historically more plausible than forcing one modern database relation
name across an illustrated herbal article and short treatment/configuration
cells. A practical compiler can map several ordinary source phrases to one
learned comitative/additive card while retaining one workshop instruction.

## Consecutive record-level source-class readings

These are complete record skeletons. Every real line in each L/O-bearing
record is retained; non-L/O material remains opaque rather than being silently
translated.

### f10r, records 1–2

```text
R1  f10r.2  [opaque illustrated-simple description; AIIN occurs late]
    f10r.5  [take/describe X and X WITH its condition/state]

R2  f10r.6  [opaque continuation; Y–Y–AIIN–Y formula at line end]
    f10r.8  [opaque specification WITH X, likewise WITH standard/value X]
    f10r.9  [opaque continuation and close of the physical paragraph]
```

Fluent but bounded paraphrase:

> Of the pictured simple: an unidentified description; then an unidentified
> item with its condition. Next article/paragraph: an unidentified
> specification; combine it with one participant and likewise with its stated
> standard or value; continuation follows.

### f81v, record 1

```text
f81v.2   [C] [open long configuration: X X X X WITH X X X X WITH X X]
f81v.7   [X WITH X AIIN X AIIN X C] [WITH-IT-LIKEWISE]
f81v.17  [C] [X WITH X C] [C] [open X X X X]
f81v.18  [C] [Y WITH X WITH X C] [C] [C] [open X X]
f81v.21  [X X C] [C] [X X X WITH X]
f81v.24  [X C] [X X WITH X C] [X X C] [open X]
f81v.27  [X X C] [C] [X C] [open X]
```

Bounded reading:

> Enter a series of short preparation/application cells. In the open cells,
> combine the named local participants; in the checked cells, combine or apply
> the current item with the selected terminal participant. After the first
> f81v.7 cell, repeat the same relation for the inherited item. The remaining
> cells give opaque categorical selections and open continuations.

### f83r, records 1–4

```text
R1  .3 [C][X C][Y AIIN Y C][X X X]
    .6 [C][X X C][X X C][C][X]
    .8 [X C][X X X X]
    .11 [X C][X X X C][X C][C][X]
    .14 [C][C][C][C][X C][X X X X]
    .15 [X X X X X X C][C][C]
    .16 [C][C][X X X X X X]
    .20 [C][C][X C][WITH inherited-X, X C][X X]
    .22 [X C][C][X X X X C][C]
    .24 [X X X X X C]

R2  .25 [C][X X C][X X]
    .26 [X X X WITH X C][C]
    .27 [X X C][C][C]
    .28 [X X X C][C][C]
    .35 [X X X X X]
    .37 [WITH inherited-X, X C][C][X C]
    .38 [X X X C]
    .39 [X X X X]
    .41 [X C][X X]
    .44 [X C]

R3  .47 [C][C][X]
    .48 [X WITH X X X X]
    .49 [WITH inherited preparation, X X]

R4  .52 [X X X WITH ...]
    .54 [... AIIN; AIIN WITH X Y X]
```

Bounded reading:

> Record 1 is a dense run of committed selections with one inherited
> comitative/application entry at f83r.20. Record 2 twice binds a selected
> participant to an accumulated or inherited preparation. Record 3 continues
> one open preparation across two physical lines. Record 4 leaves a WITH-target
> pending at f83r.52; f83r.54 begins with AIIN and is the strongest fixed-page
> candidate for filling that target before opening another binding.

That last two-line sequence is the most discriminating positive witness for
the inherited/open-operand rule. It would be accidental under a model in which
field-final L/O is simply a completed word with no continuation effect.

## Forced comparison of source classes

| candidate | fit to 19 contexts | R2 judgment |
|---|---|---|
| WITH / combine or apply together with | strong medially; edge cases handled by one active-frame rule; works in Herbal description and Bio preparation | **selected** |
| OF / FROM / belonging to | plausible in Herbal and some Bio classification, but repeated `X–OF–Y–OF–C` and bare `OF` require less natural ellipsis | secondary, 0.31 |
| IN / in the medium of | plausible for bath/liquid imagery and a few Bio cells, but too narrow for Herbal transfer, repeated links, and open final position | 0.24 |
| APPLIED TO | excellent conditional Bio paraphrase, but too action-specific for open Herbal article prose and does not explain every repeated link | incorporated only as register rendering, 0.38 |
| AND / ALSO / ITEM | good at field entry and for the bare card; poor immediately before committed values and between explicit participants unless it becomes generic coordination | 0.34 |
| PART / SHARE / portion, including *ana*-like equality | recipe-plausible but no quantity, equal share, or symmetric ingredient set is independently present; bare and final cases remain costly | 0.20 |
| AS ABOVE / similarly | excellent for the one-card and initial cases, weak for all 14 medial cases as the card's sole sense | inherited-edge rendering only, 0.41 |
| ordinary high-frequency prose word | possible, especially on f10r, but one word would need unusually broad ellipsis and Bio pre-close behavior | 0.30 |
| pure argument/relation-frame notation | covers every position and makes no lexical demand; explains copied cells very well, but gives a less informative historical source expansion | **strongest rival, 0.55** |

## Strongest rival

The strongest rival is not a different preposition. It is a content-neutral
argument-frame card:

```text
L/O = OPEN_OR_REPEAT_RELATION_SLOT(A, B)
```

Under that model, no source word corresponds to L/O. A source phrase containing
*cum*, *de*, *ad*, *in*, coordination, or a rubric relation is normalized into
the same stencil operation. This rival explains FIRST/ONLY/LAST positions at
least as economically as the medical reading and is especially attractive in
the committed Biological cells.

The medical hypothesis remains the leader because one comitative/additive
relation produces usable continuous readings in both Herbal and Biological
records, while the rival stops one level earlier. The margin is modest:
**0.64 versus 0.55**. A future repeated slot pattern can reverse that ranking
without making the current medical expansion “disproved by lack of proof.”

## Forward copying instruction

> When the exemplar joins another ingredient, preparation, application target,
> or governed participant to the active item, copy exact L/O between the two
> cards. If the current cell already supplies the left participant, begin with
> L/O. If the exemplar says “with it likewise/as above,” copy L/O alone. If the
> target continues after the line, end with L/O and supply the target at the
> next continuation. Preserve the exact card identity and apply the ordinary
> positional renderer.

This instruction is executable without knowing whether the upstream scribe
wrote *cum*, *ad*, *de*, a vernacular “with,” or an abbreviation.

## Predictions and falsifiers on the fixed pages

1. **f83r.52→f83r.54 continuity.** The line-final L/O predicts that the
   line-initial AIIN on f83r.54 participates in the pending relation before the
   second L/O opens a new local binding. A demonstrably independent new-entry
   reset between these lines would weaken the selected rule sharply.
2. **Bare-field inheritance.** The one-card f81v.7 field predicts that the
   preceding committed field, not a remote paragraph topic, supplies its
   relation and participants. A securely established paragraph/record reset at
   that boundary would falsify this concrete inheritance rule.
3. **Initial-L/O locality.** f83r.20, f83r.37, and f83r.49 should attach to the
   immediately active preceding cell/line. If their best future parse instead
   opens independent headings, `ALSO/ITEM` becomes better than WITH.
4. **Pre-close semantics.** The five pre-close uses predict that terminal
   identities are participants or governed selections compatible with a
   preparation/application relation, not punctuation alone. If exact terminals
   prove to be only cadential closers, the medical expansion loses to the pure
   argument-frame rival.
5. **No equality prediction.** The model predicts no necessary equal amount or
   paired symmetry in f81v.18. Discovery of a consistently repeated equal-share
   stencil around L/O would instead favor PART/ANA.
6. **Register-conditioned wording, stable operation.** Herbal should continue
   to read descriptively (“with/belonging with”), Biological operationally
   (“combine/apply with”), but both should preserve the same bind/inherit/open
   behavior. If either register requires the reverse argument direction or a
   wholly different state transition, the one-card rule is insufficient.

## R2 conclusion

Keep the incumbent relation hypothesis, but make it medically concrete:

```text
L/O ~= COMITATIVE/ADDITIVE BIND
     ~= WITH THE CURRENT PREPARATION OR ITEM
     ~= WITH IT LIKEWISE / AS ABOVE when operands are inherited
```

This is the historically most useful source-class expansion across the fixed
pages. It survives all nineteen contexts, including the one-card field, the
repeated `X–L/O–Y–L/O–CLOSE` frame, the other four pre-close frames, and the
open f83r.52→f83r.54 continuation. The pure argument-frame card remains a close
and serious rival; neither model licenses a decoded word, plant, body part,
liquid, dose, or treatment.
