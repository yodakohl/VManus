# IDEA000414: bounded f83r.25–30 composition audit and expanded draft

Status: exploratory source/content construction; root review below records
SURFACE_COMPLETE_SEMANTIC_CONSTRUCTOR_MISSING. RAW 414 and both drafts are
retained; the proposal is unselected for a fixed manuscript test. This file is a new elaboration and does not revise the raw
card. No new target rows, image, mixed TSV, reserve, decoder or experiment was
used.

## Boundaries and source corrections

The exact six report-owned lines are in
`research_registry/proposals/translation_programs_20260912/work/P12/READING_L1.md`.
The raw card's P28 path is retained unchanged, but P12 is the existing file
that actually contains these f83r.25–30 records. The six displayed lines have
33 groups and no additional reader stream in this bounded Markdown excerpt.

The complete source checkpoint was read first:
`research_registry/work_batches/ten_hours_20260915/BALNEIS_COMPLETE_CONTENT_20260920.md`.
It covers all 48 physical lines (VII 74–85, XI 123–134, XIX 219–230 and
XXXIII 393–404). XI distinguishes fresh water at its own spring, heat
tolerance, removal from the spring, cooling, and renewal. It also distinguishes
renewal of bodily powers at 126 from renewal of water at 134. The checkpoint
retains the removed/cooled overlap, the VII supply/object uncertainties, XIX
scope and witness variants, and XXXIII's unresolved consumption syntax and
distinct renewal/witness content. The draft below therefore uses those as
typed content values; it does not silently turn the source into a conserved
four-step trajectory.

The raw card's recorded source digest is visibly malformed: its `sha256` value
has 63 characters and differs from the 64-character cache digest. This audit
does not repair the card. The cache's actual `sha256sum` is
`397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd`.

The raw card also records `qokeedy` and `qokedy` at f83r.26, while the bounded
P12 text has `qokeedy` at .25/.27/.30 and `qokedy` at .25/.28. This is a
provenance/locus mismatch in the retained RAW metadata, not a silent correction
to that card; the expanded draft follows the displayed P12 text and records
the mismatch as a cost.

## 414's original six-part contract

The original proposal remains the starting point:

```text
qokeedy = qok + e + edy
qokeey  = qok + e + ey
qokedy  = qok + edy
qoky    = qok + y
chedy   = che + dy
cheey   = che + ey
```

`qok` is the state/update stem, `che` the effect/result stem, `e` an explicit
source/state carrier, and `edy`, `ey`, `y`, `dy` are globally reused frame
suffixes. Crucially, `cheey` is `che+ey`; it contains no separate `e` and this
segmentation does **not** provide an explicit-recipient argument. Recipient
identity must therefore be supplied by the expanded clause grammar below.

Under the original six-part contract alone, only 12 of 33 positions have a
declared function. That is a development gap, not proof of incompatibility.

## V1 retained, with mechanical defects

The following section is retained as V1 for provenance. It is **not** a valid
complete writer. Its displayed concatenations are wrong for `qolchey`,
`otchey`, and `saiin`; its two `shckhedy` occurrences have no written list
argument supplier; and `oldy` changes function without a rule. The V2 section
below is the corrected development.

## V1 new global development: finite component writer

The following is one complete, explicitly costed working hypothesis. It adds
global components; it does not add a different meaning at a later occurrence.
The additions are:

| Component | Fixed function |
|---|---|
| `qol` | source-to-effect relation |
| `ot` | condition/scope operator |
| `al` | endpoint/goal argument |
| `t` | location/temporal frame |
| `ol` | source/location value |
| `sh` | recipient/property frame |
| `ckh` | paired-list item frame |
| `da` | ordered temporal operator |
| `in` | prospective condition frame |
| `sa` | relief/renewal discourse root |
| `aiin` | seeking-recipient argument |
| `ii` | return/closure argument |
| `l` | scope binder |
| `ddy` | guarded completion frame |
| `qo` | state reference root |
| `kes` | negation/no-utility root |
| `d` | negative-polarity suffix |
| `o` + `ke` | renewal-of-water compound |
| `ky` | low-degree outcome suffix |

These are a finite inventory, not 21 singleton whole-word glosses. Their cost
is real: several are observed only once in these six lines, so their functions
remain freely hypothesized until another complete exposed passage or a source
binding constrains them. No local exception is allowed.

The fixed surface rule is `ROOT + FRAME`, with the following globally stable
decompositions:

```text
qokeedy  qok+e+edy       qolchey   qol+che+ey       qokeey   qok+e+ey
qokedy   qok+edy         chedy     che+dy           otal     ot+al
otchey   ot+che+ey       qoky      qok+y            tol      t+ol
shedy    sh+edy          qokylddy  qok+y+l+ddy      dain     da+in
shckhedy sh+ckh+edy      saiin     sa+aiin          cheeky   che+e+ky
sheey    sh+e+ey         oldy      ol+dy            salchedy sa+l+che+dy
cheey    che+ey          qody      qo+dy            kesd     kes+d
s        s               okeedy    o+ke+edy         saii     sa+ii
```

`cheey` remains `che+ey`, with no hidden `e`. `shckhedy` is repeatable as a
list-item constructor, so its two adjacent occurrences take two ordered typed
arguments without changing its meaning. Repetition is not a quantity claim.

## Complete 33-group working composition

The following assigns every group a fixed clause function. Surface functions
are global; the parenthesized values are the one shared Balneis content
inventory, not target gloss claims.

| Locus | Group | Fixed function in this draft |
|---|---|---|
| .25 | `qokeedy` | `STATE(WATER,FRESH_AT_SOURCE)` |
| .25 | `qolchey` | `RELATE(SOURCE,EFFECT_FRAME)` |
| .25 | `qokeey` | `STATE(WATER,REMOVED_FROM_SOURCE)` |
| .25 | `qokedy` | `STATE(WATER,COOLED)` |
| .25 | `chedy` | `EFFECT(RECIPIENT,REMOVE_SYMPTOMS)` |
| .25 | `otal` | `CONDITION(ENDURE_HEAT)` |
| .26 | `otchey` | `SCOPE(CONDITION,EFFECT_FRAME)` |
| .26 | `qokeey` | `STATE(WATER,REMOVED_FROM_SOURCE)` |
| .26 | `qoky` | `CONTINUE_STATE(WATER,RENEWED)` |
| .26 | `tol` | `LOCATE(WATER,AT_SOURCE)` |
| .26 | `shedy` | `RECIPIENT(SICK_PERSON)` |
| .26 | `qokylddy` | `GUARDED_STATE(STATE_CHAIN,RENEWAL_COMPLETE)` |
| .27 | `dain` | `TEMPORAL(AFTER)` |
| .27 | `chedy` | `EFFECT(RECIPIENT,REMOVE_SYMPTOMS)` |
| .27 | `qokeedy` | `STATE(WATER,FRESH_AT_SOURCE)` |
| .27 | `shckhedy` | `LIST_ITEM(RENEWAL_TARGET,BODILY_POWERS)` |
| .27 | `shckhedy` | `LIST_ITEM(RENEWAL_TARGET,WATER)` |
| .28 | `saiin` | `SEEK(RECIPIENT,RELIEF)` |
| .28 | `cheeky` | `EFFECT(RECIPIENT,LITTLE_BENEFIT)` |
| .28 | `sheey` | `CONDITION(RECIPIENT,ENDURE_HEAT)` |
| .28 | `qokedy` | `STATE(WATER,COOLED)` |
| .28 | `shedy` | `RECIPIENT(SICK_PERSON)` |
| .28 | `oldy` | `ATTRIBUTE(EFFECT,LOW_DEGREE)` |
| .29 | `salchedy` | `RENEW(WATER)` |
| .29 | `cheey` | `EFFECT(RECIPIENT,HELP)` |
| .29 | `qody` | `REFERENCE(SAME_WATER)` |
| .29 | `kesd` | `EFFECT(RECIPIENT,NO_UTILITY)` |
| .29 | `oldy` | `ATTRIBUTE(EFFECT,LOW_DEGREE)` |
| .30 | `s` | `TOPIC(WATER_CASE)` |
| .30 | `okeedy` | `RENEW(WATER)` |
| .30 | `qokeedy` | `STATE(WATER,FRESH_AT_SOURCE)` |
| .30 | `qoky` | `CONTINUE_STATE(WATER,RENEWED)` |
| .30 | `saii` | `CLOSE_OR_RETURN(RELIEF_CASE)` |

The resulting source-side whole account is: introduce one water and its source;
state fresh-at-source, require recipient heat tolerance, and state removal;
retain a sick recipient; then represent cooling, low benefit, no utility and
renewal of water as separately typed effects. The paired `shckhedy` items keep
the two source renewal objects separate. `cheey` carries help through `che+ey`
as an effect frame; it does not carry recipient identity by itself. Recipient
identity comes from the globally shared `shedy` frame and its scope.

V1 claimed this as a complete composition, but that claim is withdrawn. It is
not a valid string generator or complete source writer. It remains in this file
only as the prior version being corrected.

## V2 corrected writer: exact surface generation and argument consumption

V2 changes only the new elaboration, not RAW 414. It uses exact surface
components whose concatenations were checked mechanically. In particular:

```text
qolchey = qol + chey       otchey = ot + chey       saiin = sa + iin
shckhedy = sh + ckh + edy  oldy = ol + dy          cheey = che + ey
```

Here `chey`, `iin`, `ckh`, and `dy` are distinct globally fixed surface
components. V2 does not derive `qolchey` or `otchey` by silently deleting an
`e`, and does not derive `saiin` from the nonexistent concatenation `sa+aiin`.
The corrected surface inventory is:

| Surface component | Typed function |
|---|---|
| `qok` | state/transition operator |
| `e` | explicit state/source frame |
| `edy` | state declaration frame |
| `ey` | outcome frame |
| `y` | continuation frame |
| `dy` | completion/closure frame |
| `che` | effect operator |
| `chey` | source-effect relation frame |
| `iin` | attribution frame |
| `qol` | benefit/source relation |
| `ot` | condition/scope operator |
| `al` | endpoint argument |
| `t` | location frame |
| `ol` | same-water/source reference |
| `sh` | recipient/list-item frame |
| `ckh` | ordered list-item selector |
| `da` + `in` | ordered list introduction |
| `sa` + `l` | renewal/relief scope |
| `ii` | seek/closure frame |
| `ky` | low-benefit degree |
| `l` + `ddy` | guarded completion scope |
| `qo` | state reference |
| `kes` + `d` | no-utility polarity |
| `o` + `ke` | water-renewal compound |

The exact generator table is:

| Form | Exact assembly | Typed output and consumed arguments |
|---|---|---|
| `qokeedy` | `qok+e+edy` | `REFRESH_FRESH(WATER,LIMBS_INGRATUS,FRESH_AT_SOURCE)`; consumes `WATER` |
| `qolchey` | `qol+chey` | `BENEFIT(BATH,HUMAN_USE,MANY)`; consumes `BATH,HUMAN_USE` |
| `qokeey` | `qok+e+ey` | `STATE(WATER,REMOVED_FROM_SOURCE)`; consumes `WATER` |
| `qokedy` | `qok+edy` | `STATE(WATER,COOLED)`; consumes `WATER` |
| `chedy` | `che+dy` | `EFFECT(RECIPIENT,REMOVE_SYMPTOMS)`; consumes `RECIPIENT` |
| `otal` | `ot+al` | `CONDITION(RECIPIENT,ENDURE_HEAT)`; consumes `RECIPIENT` |
| `otchey` | `ot+chey` | `EVALUATED_DIG(PERSON,SAND,REMARKABLE)`; consumes `PERSON,SAND` |
| `qoky` | `qok+y` | `CONTINUE_STATE(WATER,RENEWED)`; consumes `WATER` |
| `tol` | `t+ol` | `LOCATE(WATER,AT_OWN_SOURCE)`; consumes `WATER,SOURCE` |
| `shedy` | `sh+edy` | `RECIPIENT(SICK_PERSON)`; consumes `SICK_PERSON` |
| `qokylddy` | `qok+y+l+ddy` | `FLOW(WATER_HOT,MIDDLE(HOLE))`; consumes `WATER,HOT,HOLE` |
| `dain` | `da+in` | `OPEN_LIST([BODY_POWERS,WATER])`; creates ordered list `R` |
| `shckhedy` | `sh+ckh+edy` | `RENEW_LIST_ITEM(R,next)`; consumes exactly the next item of `R` |
| `saiin` | `sa+iin` | `ATTRIBUTE(PEOPLE,BATH,ANASTASIA)`; consumes `PEOPLE,BATH,ANASTASIA` |
| `cheeky` | `che+e+ky` | `EFFECT(RECIPIENT,LITTLE_BENEFIT)`; consumes `RECIPIENT` |
| `sheey` | `sh+e+ey` | `CONDITION(RECIPIENT,ENDURE_HEAT)`; consumes `RECIPIENT,WATER_HEAT` |
| `oldy` | `ol+dy` | `REFERENCE(WATER,SOURCE_CONTEXT)`; consumes `WATER,SOURCE` |
| `salchedy` | `sa+l+che+dy` | `RENEW(WATER)`; consumes `WATER` |
| `cheey` | `che+ey` | `EFFECT(RECIPIENT,HELP)`; consumes `RECIPIENT` |
| `qody` | `qo+dy` | `REFERENCE(SAME_WATER)`; consumes current `WATER` |
| `kesd` | `kes+d` | `EFFECT(RECIPIENT,NO_UTILITY)`; consumes `RECIPIENT` |
| `s` | `s` | `OPEN_CASE(BATH,WATER,SOURCE)`; consumes the paragraph case |
| `okeedy` | `o+ke+edy` | `RENEW(WATER)`; consumes `WATER` |
| `saii` | `sa+ii` | `SEEK(RECIPIENT,RELIEF)`; consumes `RECIPIENT,ILLNESS` |

No form has two functions. `oldy` is now always a same-water/source reference;
it no longer means low degree. Low degree is carried only by the fixed `ky`
component in `cheeky`. `shckhedy` has one function at both occurrences: `dain`
creates the ordered list `R=[BODY_POWERS,WATER]`, and occurrence one consumes
`R[1]` while occurrence two consumes `R[2]`. The concrete object difference is
therefore supplied by a written list constructor, not by a local reinterpretation.

The complete XI source constructor represented by these typed outputs is:

```text
INTRODUCE(BATH,WATER,SOURCE)
ATTRIBUTE(PEOPLE,BATH,ANASTASIA)
BENEFIT(BATH,HUMAN_USE,MANY)
REFRESH(WATER,LIMBS(INGRATUS))
RENEW(BODY_POWERS)
EVALUATE(DIG(PERSON,SAND),REMARKABLE)
FLOW(WATER_HOT,MIDDLE(HOLE))
STATE(WATER,FRESH_AT_SOURCE)
EFFECT(SICK_PERSON,REMOVE_SYMPTOMS)
CONDITION(ENDURE(SICK_PERSON,WATER_HEAT))
STATE(WATER,REMOVED_FROM_SOURCE)
EFFECT(SICK_PERSON,NO_UTILITY)
STATE(WATER,COOLED)
EFFECT(SICK_PERSON,LITTLE_BENEFIT)
SEEK(SICK_PERSON,RELIEF(ILLNESS))
RENEW(WATER)
EFFECT(SICK_PERSON,HELP)
```

`OPEN_CASE` supplies `INTRODUCE`, `EVALUATED_DIG` supplies both the digging
event and its remarkable status, and `RENEW_LIST_ITEM` supplies the two
distinct renewal objects. These are fixed compound constructors rather than
unstated filler. The source's uncertainty remains: this constructor preserves
the clauses without asserting that they describe one executed water portion.

### V2 string and arity check

The six exact line outputs are generated by joining the following component
sequences; the resulting strings are the report-owned lines, with no deletion
or insertion rule:

```text
.25 [qok,e,edy] [qol,chey] [qok,e,ey] [qok,edy] [che,dy] [ot,al]
    -> qokeedy qolchey qokeey qokedy chedy otal
.26 [ot,chey] [qok,e,ey] [qok,y] [t,ol] [sh,edy] [qok,y,l,ddy]
    -> otchey qokeey qoky tol shedy qokylddy
.27 [da,in] [che,dy] [qok,e,edy] [sh,ckh,edy] [sh,ckh,edy]
    -> dain chedy qokeedy shckhedy shckhedy
.28 [sa,iin] [che,e,ky] [sh,e,ey] [qok,edy] [sh,edy] [ol,dy]
    -> saiin cheeky sheey qokedy shedy oldy
.29 [sa,l,che,dy] [che,ey] [qo,dy] [kes,d] [ol,dy]
    -> salchedy cheey qody kesd oldy
.30 [s] [o,ke,edy] [qok,e,edy] [qok,y] [sa,ii]
    -> s okeedy qokeedy qoky saii
```

The V2 hypothesis is therefore mechanically complete as a surface writer and
has explicit argument consumption. Its remaining debt is scientific: the
component functions and source dictionary are not independently bound to the
target, and the paragraph order is a hypothesis. That is a development cost,
not an incompatibility claim.

## Two explicit rivals and changed consequences

**Expanded persistent-state writer (H3).** Every `qokeey` denotes the same
removed-from-source state, every `qokedy` the same cooled state, and every
`cheey` the same help effect. The two adjacent `shckhedy` groups are two
ordered list items, not two meanings. H3 predicts that changing `qokeey` to
`qokedy` changes state while retaining source and recipient bindings, and that
`kesd` can express no utility without changing the state token.

**Guarded local-state rival (H4).** Keep the same finite components but let
`qokeey` carry an unfilled state argument supplied by `otchey`/`tol`; it may
therefore denote removed or cooled according to explicit condition scope. H4
predicts that replacing `tol` with `shedy` changes the bound source/recipient
while leaving the qok stem unchanged. It preserves global composition but
rejects H3's fixed value assignment to each qok surface form.

H3 and H4 differ on whether the two `qokeey` occurrences must have one state
value and on whether the `.30` `qokeedy qoky` sequence reintroduces fresh water
or continues a caller-supplied state. Neither is selected: no independent
target evidence currently binds these source values.

## Development debt, separated from incompatibility

The expanded draft removes the earlier overstatement that 21 unassigned
positions prove impossibility. The remaining debt is evidential and
engineering-related: 18 added component functions are not independently
established on the target; P12 versus the raw card's P28 path and the raw locus
table disagree; the source itself has overlap and scope alternatives; and the
source does not establish a single executed water trajectory. These are costs
and review gates, not logical contradictions. A genuine incompatibility would
require a repeated form to receive two different fixed functions under the
same global rule; this draft does not do that.

No target meaning, language, or source-to-target historical channel is claimed.


## Root review, 2026-09-20 16:21 UTC

Decision: **SURFACE_COMPLETE_SEMANTIC_CONSTRUCTOR_MISSING**. This is a
review of the changed V2 draft, not another unchanged missing-input audit,
a manuscript contradiction, or an impossibility claim. All 24 distinct
written forms now concatenate exactly. Their 33 displayed occurrences are
covered. This useful surface correction is retained.

The plus-separated inventory actually contains **29 atomic parts**, including
the standalone `s`: the seven original parts plus **22 additions**, rather
than the claimed 18. Treating `da+in`, `sa+l`, `l+ddy`, `kes+d` and `o+ke`
as compound meanings would be a different inventory; the draft must say
which units are semantic atoms. Neither counting choice creates a derivation.
The exact atomic inventory is:

```
al che chey ckh d da ddy dy e edy ey ii iin in ke kes ky l o ol
 ot qo qok qol s sa sh t y
```

The V2 claims of explicit argument consumption and a complete constructor
are **not established** by the table. It names whole-form outputs and their
arguments, but supplies neither semantic functions for all separate parts
nor reduction and binding rules that compute those outputs. For example:

| Written construction | Available component descriptions | Missing derivation |
|---|---|---|
| `ot+chey` | condition/scope + source-effect relation | DIG, SAND and REMARKABLE do not follow from these functions |
| `qok+y+l+ddy` | state + continuation + guarded completion | HOT, FLOW, MIDDLE and HOLE have no declared part-level introduction |
| `da+in`, then repeated `sh+ckh+edy` | explicitly proposed two-item list | The list is a new constant hypothesis; the different agents of bodily-power renewal and water renewal still need a rule |
| `che+ey` | effect + outcome | HELP is stipulated for the whole; it is not computed from a declared composition law |
| `sh+e+ey` | recipient/list + state/source + outcome | ENDURE_HEAT and its conditional scope remain stipulated |

The source-order list printed after the table is not the result of parsing
the written order. Source XI requires antecedent/consequent attachment for
freshness plus heat tolerance, removal, cooling and renewal. A list of state
and effect labels does not determine these attachments. The repeated
REFRESH_FRESH macros additionally combine unconditional refreshment with a
freshness guard; their scope and duplicate handling remain unspecified.
The last-line `s` could in principle introduce a declarative forward binding;
its late position is therefore not by itself a contradiction. Such a binding
rule simply has not been supplied. The ordered renewal list is similarly
permitted as an explicit hypothesis, without treating it as evidence.

H3 and H4 are sketches rather than two executable complete rivals. H4 calls
on `otchey` as a state supplier, while V2 assigns that same form a digging
macro. The consequences cannot yet be compared under one fully stated rule
set. We do not repair either rival after looking for a favorable consequence.

Source uncertainties, raw-card provenance errors, V1 errors and all revisions
remain above. All six target lines were already exposed in P12. Root also
reinspected the already admitted full f83r image at 15:53:11 UTC in this work
block; it provided no independently identified heat, digging or flow-direction
anchor. No new page, reserve, f84/f84r or f116v was opened. Independent meaning
confirmation capacity is zero; confirmed words remain zero.

Next decision: do not launch a decoder or fixed manuscript test for this
version. Reconsider a genuinely complete constructor that derives all part
outputs, reference and conditional scope, and the whole source account in
written order. More surface coverage, renamed whole-form macros or an
unimplemented claim that a recipient is shared are insufficient. This stop
concerns the available constructor, not the possibility of compositional
Voynich writing or balneological content.
