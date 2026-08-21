# V11 candidate — OWNER-10/O56 context and continuity audit

Date: 2026-08-21

Status: independent speculative sidequest candidate. This is not a GDT result,
a plaintext reading, or a semantic identification.

## Decision

```text
TOPIC_CARRIER_NOT_DISTINGUISHABLE_FROM_LOCAL_PROSE_RECURRENCE
```

The winning architecture is an explicit mixture:

```text
UNKNOWN REPEATED HERBAL CONTENT/FUNCTION
  + ordinary physical-position renderer
```

`OWNER-10` and `O56` are real recurring exact cards, but the six occurrences
do not establish that they name or resume the pictured plant. In particular,
none of the six is paragraph-initial, none has a repeated right neighbour, and
the two cards have incompatible discourse ecologies: `OWNER-10` occurs once
in each of two f10r paragraphs, whereas all four `O56` copies occur inside one
f56r paragraph. Their wrapper variation is cleanly compatible with ordinary
position-sensitive rendering; it does not identify the payload.

The attractive topic-carrier reading remains a live expansion, especially for
`O56`, but it loses to `ORDINARY_FREQUENT_PROSE + RENDERER` under the frozen
controls. The exact card could still abbreviate a plant, plant part, working
substance, relation, property, or discourse expression. The fixed four Herbal
pages do not distinguish those possibilities.

## Source discipline

I read the current-route snapshot, the compact sidequest theory and the frozen
V11 protocol. I did not read another V11 candidate. The event slice was
materialized with the guarded command from `gdt327_joint_tuple_interlinear.tsv`
using an explicit allow-list for `f10r`, `f11r`, `f55v`, and `f56r`: 100
events. No substring, edit, phonetic, Biological, visual-semantic or external
page evidence entered the comparison. `f84` and `f84r` were neither selected
nor inspected.

The exact targets are:

| anonymous card | exact joint-tuple ID | fixed-page count |
|---|---|---:|
| `OWNER-10` | `4d4559019a961b834aa1` | 2, both f10r |
| `O56` | `2cc054357a929df85f64` | 4, all f56r |

## Exhaustive target contexts

The brackets mark only the exact target card. Every line of each containing
paragraph is retained. A slash is a physical-line change, not a claimed
sentence boundary.

### f10r paragraph 1: 14 events

```text
f10r.2  dchey cthoor [char] chty os chair otytchol oky daiin etyd
f10r.5  qokchy qotchol chol cthy
```

The first `OWNER-10` is record position 3/14, line position 3/10. Its immediate
predecessor is `dedc383b...`; its successor is `80ebbbbf...`. It is neither a
paragraph entry nor a physical-line entry. Its observed wrapper is `ch`.

### f10r paragraph 2: 24 events

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.8  qotchor chor otol chol cholor chol daiin [dar]
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
```

The second `OWNER-10` is record position 17/24 and the final card of f10r.8.
Its predecessor is exact `AIIN` (`2f1c5e56...`); because the paragraph
continues, its next record event is the first card of f10r.9
(`27d97af8...`). Its observed wrapper is `d`. Thus the recurrence is once per
paragraph, but at radically different internal positions: early-medial versus
late-line-final.

Conditional on placing two cards among the 38 f10r events, the elementary
probability that one falls in each 14/24-event paragraph is
`14*24 / C(38,2) = .478`. This is a descriptive anti-overreading check, not a
scientific p-value. “Once per paragraph” is not rare enough on two paragraphs
to carry the topic claim by itself.

### f56r paragraph 1: 27 events

```text
f56r.5   chochor [cho] chodaly daiin
f56r.7   [sho] kchol otchor choky dal
f56r.8   schol choy choky cheeckhody
f56r.12  sh [cho] kchey qokokchy
f56r.13  okchy chokcheo kchal
f56r.18  [sho] chokchy kchoar sotodan
f56r.19  otchey keol daiin
```

The four `O56` copies occupy record positions 2, 5, 15 and 21 of 27. Their
intervening-event gaps are 2, 9 and 5. The complete immediate contexts are:

| locus | line position | previous record event | next event | wrapper |
|---|---|---|---|---|
| f56r.5 | 2/4, middle | `b9d7b6d6...` | `0ec6a45e...` | `ch` |
| f56r.7 | 1/5, first | `AIIN` at end of f56r.5 | `893c570f...` | `sh` |
| f56r.12 | 2/4, middle | `ad3581d3...` | `b74e9e65...` | `ch` |
| f56r.18 | 1/4, first | `75a523fc...` at end of f56r.13 | `9ad66e67...` | `sh` |

There are six distinct successors across the six target occurrences. The only
shared predecessor is `AIIN`, once before each target family. No repeated
flank, local stencil, or fixed dependent identifies a common discourse
operation.

The perfect `O56` surface relation is worth preserving:

```text
middle → cho
line first → sho
```

But this is evidence about rendering of an already recurrent exact card. It
does not decide whether that card is topic, relation, or content. Two of four
copies being line-first is also not exceptional against seven line-entry
opportunities among 27 events: the conditional hypergeometric tail for at
least two line entries is `.269`.

## Matched exact-card controls

No other fixed-page card simultaneously matches exact frequency and strict
page locality, so the audit uses the complete nearest frequency/locality panel
rather than inventing a perfect control.

| exact card | count | page ecology | FIRST / MIDDLE / LAST | relevance |
|---|---:|---|---:|---|
| `OWNER-10` | 2 | f10r only | 0 / 1 / 1 | target |
| `10488b91...` | 2 | f10r + f56r | 1 / 1 / 0 | exact-frequency control |
| `d665560c...` | 2 | f11r + f56r | 2 / 0 / 0 | exact-frequency control |
| `O56` | 4 | f56r only | 2 / 2 / 0 | target |
| `dcda95c8...` | 3 | f10r only | 0 / 3 / 0 | page-locality control |
| `9ad66e67...` | 3 | f10r + f56r | 2 / 1 / 0 | placement/frequency control |
| `276a7c2d...` | 3 | f10r + f56r | 0 / 3 / 0 | frequency control |
| `e0b630cb...` | 3 | f10r + f11r | 0 / 2 / 1 | frequency control |
| `7a4bb813...` | 5 | f10r + f55v | 0 / 5 / 0 | frequency control |

Only three recurrent exact types are confined to a single one of the four
pages: `OWNER-10`, `O56`, and `dcda95c8...`. Page-local recurrence is therefore
real and uncommon. It still does not determine *why* a card recurs. The matched
panel shows that the target placements are not exceptional:

- a frequency-3 card is first in 2/3 occurrences, exceeding O56's 2/4;
- another frequency-2 card is first in 2/2 occurrences;
- page-local `dcda95c8...` is medial in 3/3 occurrences;
- multiple recurrent controls, like O56, are never line-final.

The wrapper/placement interaction is also not unique in kind. The exact
`9ad66e67...` card appears through different visible wrappers at first and
medial positions, and `10488b91...` likewise changes its visible rendering
with placement. O56's `sho/cho` alternation is a particularly clean example of
the already expected renderer, not evidence for a unique topic morpheme.

## Deletion and continuity test

Deleting the candidates does not reveal a repeated hidden template.

For `OWNER-10`, deletion creates two unrelated adjacencies:

```text
dedc383b... → 80ebbbbf...
AIIN        → 27d97af8... across the next physical line
```

It also makes `AIIN` line-final in f10r.8. Nothing else in the fixed material
shows that these are coherent source clauses, and the two deletion contexts
do not become homologous.

For `O56`, deletion creates four different joins or line entries:

```text
b9d7b6d6... → 0ec6a45e...
line entry becomes 893c570f...
ad3581d3... → b74e9e65...
line entry becomes 9ad66e67...
```

Again no repeated template emerges. Removal therefore behaves exactly like
deleting a frequent ordinary constituent: it leaves four different local
contexts. It does not demonstrate either a semantically empty resumptive or a
content word.

## Architecture competition

Scores use the frozen V11 rubric and are deliberately qualitative because six
events do not support a new inferential family.

| candidate | score / 100 | disposition |
|---|---:|---|
| ordinary recurrent content/function + position renderer | **88** | **selected** |
| TOPIC_RESUME | 78 | plausible expansion, not distinguished |
| LOCAL_RELATION | 73 | plausible, no stable operands or flanks |
| repeated part/process | 70 | possible content reading, no visual owner |
| PAGE_OWNER | 63 | once-per-f10-paragraph lead, but 0/6 paragraph-first |
| renderer alone | 57 | explains surface wrappers, not exact-card recurrence |

### Why PAGE_OWNER loses

`OWNER-10` does cross the f10r paragraph boundary exactly once. That is its
strongest fact. But both paragraphs are owned silently by the same picture,
neither occurrence introduces its paragraph, and the second arrives only at
position 17/24. O56 never crosses a paragraph boundary at all. A single common
`PAGE_OWNER` rule therefore requires more exceptions than it explains.

### Why TOPIC_RESUME remains live

O56 occurs at two line entries and twice after one local lead, with four
different continuations. This is compatible with restoring an inherited
topic after spatial interruption. Yet physical lines were fitted around a
pre-drawn image, and equally frequent controls show the same or stronger
line-entry concentration. The signal cannot be separated from ordinary
repetition plus reflow.

### Why a pure renderer loses

Renderer state explains why the same exact card appears as `cho/sho` or
`char/dar`. It cannot explain why this exact underlying card was selected four
times on f56r. Payload recurrence remains real even when its function is
unknown.

## Controlled continuous reading

This is the strongest reading licensed without supplying lexical glosses:

```text
f10r paragraph 1:
  Open the illustrated article with two local cards; use RECURRING-10 inside
  an otherwise local clause; continue through portable and copied cards; then
  add a second open clause with association/state machinery.

f10r paragraph 2:
  Continue the same pictured dossier through state/relation/item material;
  use RECURRING-10 late at a physical-line edge; continue the paragraph on the
  next line with other local and portable cards.

f56r paragraph:
  Introduce a local clause containing RECURRING-56; return to RECURRING-56 at
  two physical-line entries and twice medially; attach four different local
  continuations; close only the independent f56r.8 packet; finish with a local
  tail and a portable reference card.
```

Fluent but deliberately nonlexical paraphrase:

> “Concerning the pictured simple, the first article gives several local
> descriptions or instructions and reuses one article-specific expression in
> each paragraph. The second article repeatedly uses another page-specific
> expression in four different clauses, twice after a line reset. What those
> expressions denote is not recoverable from these recurrences.”

This preserves the useful Herbal model—open abbreviated article prose around
a pre-drawn picture—without making either repeated card a pronoun, name,
plant-part word, or WATER.

## Strongest counterexamples

1. **Against the selected conservative mixture:** `OWNER-10` occurs exactly
   once in each f10r paragraph, while O56 crosses the apparent spatial text
   blocks and always introduces a distinct continuation. Those are precisely
   the facts expected from a broad topic carrier.
2. **Against one shared topic role:** one card is sparse across two records and
   the other dense inside one record. Neither is paragraph-initial.
3. **Against ordinary content:** six different successors and wrapper mobility
   are unusually convenient for an inherited relation or topic expression.
4. **Against renderer-only:** exact underlying recurrence is not created by
   the wrapper; the renderer merely realizes it.
5. **Against a specific plant/part/process gloss:** there is no independently
   repeated visual referent, no cross-page contrast, and no homologous local
   stencil.

## Discriminating predictions

These are predictions for a future authorized expansion, not permission to
open more pages.

1. If O56-like cards are topic resumptives, their exact identities should
   recur after genuine paragraph or drawing-interruption resets more than
   frequency- and geometry-matched article cards, not merely at physical line
   starts.
2. If they are ordinary repeated content, their recurrence should track a
   narrower clause or subject matter and should sometimes remain medial across
   long uninterrupted text; no privileged return boundary is required.
3. If they are page owners, at least one realization should be concentrated
   near the opening of independently segmented articles. The present 0/6
   paragraph-opening count predicts failure unless silent opening ownership is
   separately motivated.
4. The rendering rule predicts that an exact recurrent card can change wrapper
   at line entry while preserving its non-position behavioural context. That
   must not be misread as two words or two topic functions.
5. A genuine shared topic role should produce comparable deletion consequences
   or dependent classes across independent articles. The current six deletions
   produce no such invariant.

## Bottom line

The audit strengthens one formal claim and withdraws one semantic temptation:

```text
SUPPORTED WORKING DESCRIPTION:
  page-local exact-card recurrence + position-conditioned surface rendering

NOT DISTINGUISHED:
  topic resumption vs local relation vs repeatedly mentioned content
```

The best V11 continuation should therefore leave `OWNER-10` and `O56` as
anonymous recurrent Herbal cards. They should not anchor the next translation
pass unless a new independent context supplies a real contrast.
