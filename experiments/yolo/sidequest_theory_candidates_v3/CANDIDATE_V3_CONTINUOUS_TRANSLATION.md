# V3 candidate — continuous formula-card translation

Date: 2026-08-21

Status: **YOLO source-layer reconstruction; not a decipherment result.**

Scope is restricted to the fixed Herbal pages `f10r`, `f11r`, `f55v`,
`f56r` and Biological pages `f81v`, `f82r`, `f83r`. The three circle pages
remain a separate topology-only namespace and are not used to infer prose-card
meanings. Neither `f84` nor `f84r` was accessed.

This candidate deliberately asks how far one can translate *continuously*
after freezing a tiny formula-card vocabulary. It uses exact GDT327 joint-card
identity rather than visible spelling. All readings below are provisional
source classes. None is an identified English word, sound, POS or plaintext.

## Data slice

The 381 permitted prose events were selected from the already published
GDT276 surface inventory and GDT327 interlinear with guarded page allow-lists
and `--forbid-prefix f84`. The tables were joined only on permitted
`page+locus+group_index`. No candidate archive was consulted.

## Frozen V3 lexicon before continuous reading

I froze the following inventory before composing the paraphrases. The point is
to prevent a card from changing meaning whenever the surrounding line changes.

| exact card | surface examples | literal V3 tag | fixed expansion class |
|---|---|---|---|
| `b5fcea1eaed06b2f2291` | `qokaiin`, `okaiin` | `HEAD` | take, enter, use or specify the following entry |
| `dcda95c81a5460feb191` | `ol`, `chol`, `qol`, `sol`, `tol` | `REL` | with, of, in, together with; a broad relation |
| `2f1c5e56e8f0ff459065` | `aiin`, `daiin`, `saiin`, `taiin`, `chaiin` | `PAR` | a parameter, share, amount, degree or indexed value |
| `b921a237be883a820352` | `y`, `dy`, `chey`, `chy`, `shy`, `sy` | `ITEM` | generic item, portion, unit or typed reference |
| `e0b630cb1b5df5e7105b` | `cthy`, `shcthy`, `checthy` | `STATE` | qualified/prepared state or property |
| `308e8ea2d5d190c498e8` | `okal`, `qokal` | `SET` | set/select the local relation or setting |
| `276a7c2d74d1143446f4` | `oky`, `choky`, `qoky` | `SLOT` | generic local slot/value card |
| `1645e612504fcef59ced` | `okain`, `qokain` | `ENTRY` | introduce a local item/value entry |
| `2cc8bb3c2af19607888f` | `chckhy`, `shckhy` | `PROC` | local process/configuration card |
| `6f7ff8287eddf4da9fdb` | `chedy`, `chdy` | `STEP` | ordinary internal step/prepared item; **not** a close |
| `bc4f1f5c006c74a4d26d` | `shedy`, `cheedy`, `tedy` | `TERM-A!` | payload-bearing terminal card A, commit field |
| `7d25241b0e56c836372a` | `qokeedy` | `TERM-B!` | payload-bearing terminal card B, commit field |
| `7db18b2f0fb7ed0fcfd3` | `qokedy` | `TERM-C!` | payload-bearing terminal card C, commit field |
| `de7321bface5628e35d6` | `lchedy` | `TERM-D!` | payload-bearing terminal card D, commit field |
| `259b2b3b0bf859882e2c` | `dchedy`, `schedy`, `tchedy` | `TERM-E!` | payload-bearing terminal card E, commit field |
| other attached-close cards | varied | `TERM-x!` | preserve exact local payload, commit field |

`!` means an attached DY/B3-bearing commitment, not punctuation. In the fluent
rendering below I use the same deliberately broad expansions throughout:

```text
HEAD       take/specify
REL        with/of
PAR        measured share / setting
ITEM       portion/item
STATE      prepared/qualified
SET        set according to
SLOT       local setting
ENTRY      enter item
PROC       work/process
STEP       prepare/work
TERM-A!    apply and close
TERM-B!    complete the preparation
TERM-C!    set and close
TERM-D!    leave/finish this cell
TERM-E!    close the entry
TERM-x!    [local result/action], close
```

The English verbs are not card glosses. They are a stable, readable expansion
of anonymous register operations.

## Source grammar held fixed

```text
DOSSIER := silent picture/page address + ENTRY*
ENTRY   := HEAD? + LOCAL_CARD* + (REL|SET|PAR|ITEM|STATE|PROC|STEP)*
           + TERM-x!?
FIELD   := one committed ENTRY, or an open continuation slice
LINE    := one or more FIELD slices fitted around the pre-drawn image
```

The fluent translation therefore reads like reconstructed notes, not like a
word-for-word cipher solution. Bracketed capitals are unresolved exact cards;
they retain one identity wherever repeated.

## Continuous Herbal reading

### f10r, lines 5–9

These five physical lines are read as one picture-owned plant dossier. The
line break is not forced to be a sentence boundary.

#### Literal anonymous parse

```text
f10r.5  [9ad66e67] [e8a6105b] REL STATE
f10r.6  [7249edc4] STATE [7a4bb813] [f3c23f42]
         [af816c04] ITEM ITEM PAR ITEM
f10r.8  [10488b91] [7a4bb813] [497cbd9c] REL
         [dec40177] REL PAR [4d455901]
f10r.9  [27d97af8] [7a4bb813] [7a4bb813] ITEM
         [409de023] ITEM [834825c6]
```

#### Source-class expansion

```text
plant-entry / plant-entry / RELATION / QUALIFIED-STATE;
local-property / QUALIFIED-STATE / repeated-class / local-parameter,
local-relation / ITEM / ITEM / PARAMETER / ITEM;
local-setting / repeated-class / local-class / RELATION,
related-class / RELATION / PARAMETER / repeated-card;
local-property / repeated-class / repeated-class / ITEM,
indexed-value / ITEM / local-compound.
```

#### Fluent pseudo-translation

> For the plant shown: record its principal kind and its prepared condition.
> The second quality is of the same general class; for the paired items enter
> the stated measure. Record the associated kind with its measured relation,
> then add the repeated quality and its indexed portion.

This is intentionally less specific than “boil the root in water.” The plant
picture can silently supply the object, and water may be an unexpanded local
card, but nothing in these lines fixes WATER.

### f55v, lines 5 and 11

f55v is rendered in the B ecology but remains a pictured Herbal dossier. Its
short committed fields are a useful bridge to the Biological forms.

#### Literal anonymous parse

```text
f55v.5  HEAD PAR [403c1592] [d929a14e] [TERM-97cc!]
         | PAR STEP [e026af58!]
f55v.11 [f7dc90b2] [807591ef] [2c1a5fd9] [TERM-1b1f!]
         | PAR SET [204b0483] [7a4bb813] ITEM [6afeb5c9]
```

#### Fluent pseudo-translation

> Take the measured share; enter the two local specifications and commit that
> preparation. For the following share, prepare it and close under the stated
> local result. In the second entry, register the named preparation and its
> committed condition; then enter the measure, set the associated relation,
> and retain the indicated item/reference.

The repeated `PAR` is rendered “share/measure” here, but it could instead be a
degree, index or recipe-table reference. The continuous grammar survives that
replacement unchanged.

## Continuous Biological reading

The Biological pages are treated as picture-addressed application or
apparatus records. Figures, containers, tubes and pools provide silent
arguments. The fields below are read as compact checked cells rather than
ordinary clauses.

### f81v, lines 17–24

#### Literal anonymous parse

```text
f81v.17 TERM-54e3! |
         STEP REL TERM-A! |
         TERM-28ff! |
         ENTRY PROC [0f18de17] [4da0f0f7]

f81v.18 TERM-8741! |
         ITEM REL [d904bf7b] REL TERM-A! |
         TERM-C! | TERM-C! |
         PROC SLOT

f81v.21 [be0974b3] [08bd5ca0] TERM-2e7e! |
         TERM-2e7e! |
         STEP [c205570c] [43371329] REL [b6b65472]

f81v.24 [a7af89ab] TERM-0791! |
         SET [0275fbf1] REL TERM-A! |
         [dd0ecaf5] [a06244ef] TERM-d225! |
         [b38d70da]
```

#### Source-class expansion

```text
close local entry;
prepare + REL + terminal-A;
terminal local relation;
enter item + process + two local specifications.

close configuration;
ITEM + REL + local state + REL + terminal-A;
terminal-C; terminal-C;
process + local setting.

local head + local state + close;
repeat same close;
prepare + local relation + local result + REL + local parameter.

local item + close;
SET + local state + REL + terminal-A;
local relation + local value + close;
open continuation card.
```

#### Fluent pseudo-translation

> Close the first setting. Prepare the related component and apply it; close
> the linked setting. Enter the process with its two local specifications.
> Close that configuration. Couple the indicated item to the prepared state,
> relate it to the application, and close. Set and close the next two cells;
> continue with the working setting. Repeat the specified closing operation,
> then prepare the linked result under its parameter. Finally set the next
> relation, apply and close it, and leave the last card open for continuation.

This reads coherently as a worksheet because identical terminal cards produce
identical closure expansions. It does **not** tell us whether the operation is
bathing, pouring, heating, draining, applying to a body, or recording a
diagram configuration.

### f82r, lines 2–7

This is the strongest continuous test because it includes the unique repeated
`qokaiin` across a physical line boundary.

#### Literal anonymous parse

```text
f82r.2  TERM-E! | TERM-28ff! |
         ENTRY ITEM TERM-B! |
         SET [f329f205] [ba814268]

f82r.3  [0275fbf1] TERM-c1db! |
         [4a7a6326] [2d2e37cc] PROC HEAD

f82r.4  HEAD [a8f891de] [f0db6d30] TERM-04a3! |
         [5d5e0b28] SET [c1913ec4] SLOT

f82r.7  TERM-cbb4! |
         [54d0e228] [3ae9a121] TERM-A! |
         TERM-daa1! |
         [0275fbf1] SLOT [5eff216b] [b5df9126]
```

#### Source-class expansion

```text
close entry; close related entry;
introduce ITEM and complete-preparation;
SET + local process + local value.

local state + close;
local relation + local parameter + PROC + HEAD(carry).

HEAD(resumed) + local operation + local state + close;
local state + SET + local process + SLOT.

close local entry;
local parameter + local relation + terminal-A;
close local relation;
local state + SLOT + local relation + local item.
```

#### Fluent pseudo-translation

> Close the opening entry and its linked entry. Enter the item, complete its
> preparation, and set the following process and value. Close that local
> state. Begin the next instruction with its relation and working
> configuration—take/specify: [physical line break] take/specify the carried
> operation, its prepared state, and commit it. Record the following setting.
> Close the next entry; apply and close its related parameter; close the linked
> cell, then retain the final setting and item as an open continuation.

The double translation “take/specify … take/specify” is deliberately awkward.
If the first `HEAD` is an anticipatory catchword, the logical reading becomes:

> Begin the next instruction with its relation and working configuration—
> [catchword] Take/specify the carried operation, its prepared state, and
> commit it.

That is the cleanest reading, but it is a local scribal hypothesis rather than
a universal RESUME operator.

### f83r, lines 3–16

This provides the longest continuous paragraph-sized expansion attempted in
V3.

#### Literal anonymous parse

```text
f83r.3  TERM-3b70! |
         [90bcf0a9] TERM-a84f! |
         ITEM PAR ITEM TERM-D! |
         HEAD [90bcf0a9] [4d455901]

f83r.6  TERM-E! |
         [5e844139] SET TERM-28ff! |
         HEAD STEP TERM-B! |
         TERM-D! |
         SLOT

f83r.8  [ba540da9] TERM-c45e! |
         [348e81ba] SLOT STEP [0bdc8b6d]

f83r.11 [7a4bb813] TERM-A! |
         HEAD [9da1b6ac] [6b89d6dd] TERM-C! |
         [7d2404c8] [03626ca9!] |
         TERM-D! | [2b7fa918]

f83r.14 [07913ef9!] | TERM-B! | TERM-A! | [db167f8e!] |
         [dd0ecaf5] TERM-D! |
         HEAD STATE [dd0ecaf5] ITEM

f83r.15 PAR [abb23e5e] [cb57b696] ITEM [dd0ecaf5]
         [cb57b696] [2bc2ed26!] |
         [4de12cf3!] | TERM-D!

f83r.16 TERM-E! | [87411f84!] |
         [342c3f07] [d72f71ba] STEP ENTRY STATE [d788d8d7]
```

#### Fluent pseudo-translation

> Complete the first preparation. Record the local setting and close it. For
> the two items enter their measured relation and finish the cell; then take
> the next local setting and specification. Close the new entry. Set its
> relation and commit it. Take the prepared step and complete the preparation;
> finish that cell and retain the following setting. Enter the next local
> relation and close it, then keep the prepared setting open.
>
> Record the associated class and apply it. Take the indexed item under its
> parameter and set it closed. Commit the next local preparation, finish the
> cell, and retain its continuation marker. Close four short settings in
> sequence. For the following relation, finish the cell; then take the
> qualified relation and its item. Enter its measure, related state, item and
> second relation; commit the resulting configuration. Close the next two
> cells. Close the new entry and its configuration, then prepare the entered
> item in the qualified state under the final local specification.

This sounds formulaic because the source hypothesis *is* formulaic. The
advantage is that it accounts for the extreme number of short close-bearing
fields without pretending each is a full spoken sentence.

## The `Y–AIIN–Y` construction under the frozen lexicon

```text
f10r.6  CHY TAIIN SHY
f83r.3  CHEY DAIIN CHEY LCHEDY!
```

Literal:

```text
ITEM — PARAMETER — ITEM
ITEM — PARAMETER — ITEM — TERM-D!
```

Stable V3 expansion:

> item—shared or typed parameter—item [then finish the cell]

The strongest daring source analogy remains “of each / equal share,” but this
is **not** adopted as the primary translation. The Herbal instance has an
additional adjacent ITEM and neither image independently proves paired equal
operands. V3 therefore freezes only a two-item parameter frame.

## Consistency ledger

The ledger counts all occurrences on the seven fixed prose pages, not merely
the excerpts translated above.

| candidate | occurrences | consistent with frozen broad class | direct tensions | simple consistency | principal contradiction |
|---|---:|---:|---:|---:|---|
| `HEAD/qokaiin` | 9 | 7 field-first + 1 resumed line-first | 1 field-final catchword, 1 medial | 7/9 = 77.8% strict | pure spoken imperative should not be field-final |
| `REL/L-O` | 19 | 14 field-medial | 3 field-first, 1 only, 1 last | 14/19 = 73.7% strict | too mobile for a narrow binary conjunction |
| `PAR/AIIN` | 20 | all permit a broad parameter/reference reading | 6 first and 5 last oppose a narrow infix quantity marker | 20/20 broad; 9/20 strict-medial | AMOUNT alone is too narrow |
| `ITEM/Y` | 18 | repeated frame/item behavior is possible | 2 first, 3 last; forms also occur freely as `dy` | 13/18 strict-medial | may be a generic formal card rather than an entity |
| `STATE/CTHY` | 7 | 6 medial, 1 final | no independent prepared-state owner | 7/7 distributionally possible | semantics wholly ungrounded |
| terminal cards collectively | 90 close-bearing events | all commit their field by construction | exact payloads remain heterogeneous | 90/90 formal only | no evidence that A/B/C/D mean apply/complete/set/leave |
| `TERM-A` | 12 | 9 last, 3 only | none formally | 12/12 close | fluent “apply” is unsupported |
| `TERM-B` | 10 | 5 last, 5 only | none formally | 10/10 close | fluent “complete preparation” is unsupported |
| `TERM-C` | 8 | 5 last, 3 only | none formally | 8/8 close | fluent “set” is unsupported |
| `TERM-D` | 8 | 3 last, 5 only | none formally | 8/8 close | fluent “finish” is unsupported |

The broad formal/source-class grammar achieves high internal consistency only
because it is deliberately low-resolution. The fluent English layer is much
less constrained. Its main gain is not lexeme recovery but the demonstration
that many consecutive fields can be read as a teachable practical register
without changing the six central assignments ad hoc.

## Contradictions and awkward facts

1. `HEAD` is not exclusively field-initial. The f82r final/initial repetition
   is elegant as a catchword, but that interpretation is post-hoc and unique.
2. `REL` is too positionally mobile to be simply AND, WITH or OF. Its best V3
   meaning is a family-level relational instruction, not one preposition.
3. `PAR` at field edges makes “amount” insufficient. Table address, degree,
   named value or compact formula are live alternatives.
4. `ITEM` can repeat directly and appears through many wrappers. It might be a
   generic typed slot rather than a noun-like item.
5. The close-bearing cards carry substantial exact identity. Translating all
   of them as punctuation is wrong; translating each as a known action is also
   unjustified.
6. Biological fluent prose can be made coherent as treatment, bath procedure,
   apparatus configuration or bookkeeping. The text alone does not choose.
7. Herbal lines are much more open and longer than Biological cells. The same
   compiler can explain this through dossier versus checked-form register, but
   an ordinary language/Register-A versus notation/Register-B split remains
   possible.
8. No prose card bridges the circle pages under GDT327. WHAT/HOW/WHEN remains
   an editorial story, not a decoded pointer system.

## V3 verdict

The most productive translation-like reconstruction is:

> **A pictured practical register whose writer silently supplies the shown
> object, selects a learned entry card, records relations, parameters and
> prepared/configurational states, and commits short local cells with
> payload-bearing terminal cards.**

A concise sample translation is:

> Take the shown item under the stated measure; set its related prepared
> condition and commit the cell. Continue with the linked item, retain its
> parameter, and close the local result.

This is a coherent *source-layer idiom*, not recovered plaintext. The strongest
new result of the exercise is negative but useful: continuous reading does not
require each physical line to be a sentence, nor each group to be a word. It
does require a stable distinction among entry head, broad relation, parameter,
typed item, prepared state, internal step and exact payload-bearing terminal
cards.

The next iteration should challenge the bold English layer by forcing the same
lexicon through every occurrence of each exact card, especially the awkward
field-edge `PAR`, noninitial `HEAD`, and the four high-frequency terminal
families. It should not expand the page set or import Astro meanings until a
bridge is independently found.
