# V11 candidate — opaque Herbal discourse carriers

Date: 2026-08-21

Status: **speculative sidequest analysis; not a GDT result and not a
translation**.

## Decision

```text
TOPIC_CARRIER_NOT_DISTINGUISHABLE_FROM_LOCAL_PROSE_RECURRENCE
```

`OWNER-10` and `O56` are useful recurrent whole-card landmarks, but the fixed
four-page Herbal panel does not distinguish a topic-resumption function from
ordinary repeated page content. The two cards also do not yet support one
common discourse rule:

- `OWNER-10` occurs twice on f10r, once in each paragraph, but its second copy
  is late in paragraph 2 and closes a physical line;
- `O56` occurs four times in the sole f56r paragraph, always in the first two
  positions of a physical line, but it cannot demonstrate paragraph
  reactivation because there is only one paragraph.

The strongest surviving lead is therefore narrower than the V10 mnemonic
names: `O56` is an anonymous **early-line recurrent content/construction card**.
`OWNER-10` is an anonymous **page-local paragraph-spanning card**. Neither is
promoted to page owner, topic, plant, pronoun, relation, process or part.

## Scope and method

The analysis used only the current route, compact sidequest state, the frozen
V11 protocol and a guarded GDT327 slice selected by the explicit page values
`f10r`, `f11r`, `f55v`, and `f56r`. The slice has 100 events. Candidate
identities were kept opaque; no PAGE_HOST, substring, spelling, phonetic,
Biological or semantic feature was used. `f84` and `f84r` were neither queried
nor accessed.

Eight-character displays below are merely shortened exact tuple hashes.
`U` means a type occurring once on its page, `R` a recurrent exact type, `X` a
type recurring elsewhere in the four-page panel, and `T10`/`T56` the two target
cards. These are source classes, not word classes.

## Complete paragraph parses

Line breaks are physical source lines, not asserted statement ends. A blank
line is the source paragraph boundary.

### f10r, paragraph 1

```text
f10r.2  U:65f320e7 U:dedc383b T10:4d455901 U:80ebbbbf U:df109883
         U:12efe866 U:62ff0597 X:276a7c2d X:2f1c5e56 U:a6939862
f10r.5  X:9ad66e67 U:e8a6105b R:dcda95c8 X:e0b630cb
```

`T10` is event 3 of 14 in paragraph 1, group 3/10 on its line. It is medial,
preceded by `dedc383b` and followed by `80ebbbbf`.

### f10r, paragraph 2

```text
f10r.6  U:7249edc4 X:e0b630cb R:7a4bb813 U:f3c23f42 U:af816c04
         R:b921a237 R:b921a237 X:2f1c5e56 R:b921a237
f10r.8  X:10488b91 R:7a4bb813 U:497cbd9c R:dcda95c8 U:dec40177
         R:dcda95c8 X:2f1c5e56 T10:4d455901
f10r.9  U:27d97af8 R:7a4bb813 R:7a4bb813 R:b921a237 U:409de023
         R:b921a237 U:834825c6
```

`T10` is event 17 of 24 in paragraph 2, group 8/8 on its line. It is preceded
by `2f1c5e56` and followed by a physical-line boundary. Thus “once in each
paragraph” is real, but “paragraph opener/reactivator” is not.

### f56r, its single paragraph

```text
f56r.5   U:b9d7b6d6 T56:2cc05435 U:0ec6a45e X:2f1c5e56
f56r.7   T56:2cc05435 U:893c570f X:10488b91 X:276a7c2d U:dd0ecaf5
f56r.8   U:d665560c U:c10aec6d X:276a7c2d U:95987d6f
f56r.12  U:ad3581d3 T56:2cc05435 U:b74e9e65 U:1322bc17
f56r.13  X:9ad66e67 U:087a47b5 U:75a523fc
f56r.18  T56:2cc05435 X:9ad66e67 U:c71c72da U:61a075bc
f56r.19  U:faf32194 U:9bb7122b X:2f1c5e56
```

The four `T56` events occur at page-event indices 2, 5, 15 and 21 (one-based),
with return gaps of 3, 10 and 6 events. Two are group 1 and two group 2. Their
successors are four different cards; the two overt predecessors are also
different, while the other two occurrences follow a line boundary.

## Exhaustive six-occurrence context table

| card | locus | paragraph | line position | previous | following |
|---|---|---:|---|---|---|
| `T10` | f10r.2#3 | 1 | 3/10, medial | `dedc383b` | `80ebbbbf` |
| `T10` | f10r.8#8 | 2 | 8/8, final | `2f1c5e56` | line boundary |
| `T56` | f56r.5#2 | 1 | 2/4, medial | `b9d7b6d6` | `0ec6a45e` |
| `T56` | f56r.7#1 | 1 | 1/5, initial | line boundary | `893c570f` |
| `T56` | f56r.12#2 | 1 | 2/4, medial | `ad3581d3` | `b74e9e65` |
| `T56` | f56r.18#1 | 1 | 1/4, initial | line boundary | `9ad66e67` |

No exact left or right neighbour repeats across either target's occurrences.
That is compatible with a discourse carrier accepting varied content, but it
is equally compatible with an ordinary recurrent item in a singleton-rich
lexicon.

## Matched-card controls

An exact frequency-and-page-locality match does not exist for either target in
the four-page panel. This is a capacity limitation, not positive evidence.

### f10r

Six exact types recur on the page. Four of those six span both paragraphs.
`T10` is therefore not unique in paragraph persistence. Two types are both
page-local and paragraph-spanning: `T10` (2 events) and `dcda95c8` (3 events).

The closest frequency/placement control is `e0b630cb`: it also occurs twice on
f10r, once final and once medial, and spans both paragraphs. It has a third
event on f11r, so it is not page-local. More importantly, its f10r occurrences
straddle the paragraph boundary much more directly—last card of f10r.5 and
second card of f10r.6—than `T10` does. A paragraph-spanning discourse reading
would therefore select at least one rival before seeing identity.

### f56r

`T56` is the only four-event type restricted to f56r. The nearest same-local-
frequency control is `7a4bb813` on f10r: four events on three lines, all medial,
with return gaps 8, 8 and 1. Its four successors are also all distinct. The
nearest position control is `9ad66e67` on f56r: two events, one initial and one
medial. Consequently neither high neighbour diversity nor changing return
distance distinguishes `T56`.

`T56` does have a genuine placement fact: all four copies are in the first two
line positions. Under a simple opportunity calculation, 14 of the 27 f56r
positions are in that zone; putting all four target copies there has an
uncorrected hypergeometric probability of approximately .057. This is a weak,
post-selected lead, not a topic-carrier result, and no exact four-event
page-local control exists.

## Deletion and substitution thought experiments

Removing `T10` creates two unrelated joins:

```text
dedc383b → 80ebbbbf
2f1c5e56 → LINE_END
```

It neither reveals a repeated residual frame nor makes the two paragraphs
formally more alike. Replacing it with the matched `e0b630cb` would preserve
the observed medial/final placement profile and paragraph coverage. The
visible structure alone cannot prefer the target.

Removing `T56` leaves four ordinary-looking lines of lengths 3, 4, 3 and 3.
It creates no repeated adjacency and destroys no observable branch, closure or
equality relation. A fourfold substitution by another recurrent type would
preserve the recurrence architecture; the only special cost would be losing
the early-line concentration. This supports a construction/content head
candidate, but not specifically a topic resumer.

## Historical plausibility

Medieval Herbal organization makes both sides of the ambiguity plausible.
The scholarly edition description of the *Lelamour Herbal* notes the ordinary
one-simple-per-chapter organization and more than two hundred plant entries.
Mäkinen's study of medieval English herbals further notes that a Latin plant
name can be supplied in a rubric and repeated in the entry, with vernacular
names and synonyms added; synonym lists could also compress plant description
into schematic form. Those practices make page/article identity recurrence
historically reasonable, but they also predict repeated ordinary names,
synonyms, parts and uses—the exact alternative the four-page statistics cannot
separate.

References:

- R. von Arx, *The Lelamour Herbal (MS Sloane 5, ff. 13r–57r)*, edition
  description: <https://www.peterlang.com/document/1056214>.
- M. Mäkinen, “Between Herbals et alia: Intertextuality in Medieval English
  Herbals,” especially the discussion of names, synonyms and schematic
  descriptions: <https://helda.helsinki.fi/server/api/core/bitstreams/9ab6008c-ab1b-44d6-b76e-30d680d7f233/content>.

The historical evidence raises the prior probability of repeated article
material. It supplies no ownership of either opaque card and therefore cannot
break the tie.

## Frozen-candidate comparison

| architecture | score / 100 | reason |
|---|---:|---|
| `PAGE_OWNER` | 62 | paragraph coverage helps T10, but late placement and f56r capacity hurt |
| `TOPIC_RESUME` | 68 | explains varied neighbours and T56 recurrence, but no observable resumption target exists |
| `LOCAL_RELATION` | 57 | can float in position, but has no overt two-argument or inherited-node test here |
| `REPEATED_PART_OR_PROCESS` | 73 | fits page locality and varied construction, but cannot be separated from other content |
| `ORDINARY_FREQUENT_PROSE` | 76 | needs no special invisible discourse mechanism and matches controls |
| `RENDERER_OR_POSITION_EFFECT` | 46 | T56 is early-biased, but exact identity is not licensed as a renderer effect |
| explicit mixture | 74 | T10 as paragraph landmark plus T56 as early content fits, but teaches two unsupported rules |

The numerical winner is ordinary recurrent prose, but the intended scientific
decision is the stronger tie statement: current evidence cannot tell whether
that repeated prose is an article owner, relation, part, process, property or
another local content item.

## Controlled continuous reading

No lexical gloss is needed to express everything established:

> **f10r paragraph 1:** open a pictured-Herbal article; introduce ten opaque
> cards, including page-local `T10`; continue with four cards, ending in a
> cross-page recurrent type.
>
> **f10r paragraph 2:** resume the article with nine cards and dense local
> recurrence; continue with eight cards, ending in the second `T10`; finish
> with seven cards and further recurrence.
>
> **f56r:** continue one pictured-Herbal article across seven physical lines;
> place `T56` near line entry on lines .5, .7, .12 and .18, interleaved with
> three lines lacking it; close each line through otherwise changing opaque
> content.

That reading is complete at the source-class level and makes no assertion that
a physical line is a statement.

## Strongest counterexample

`e0b630cb` is the decisive f10r counterexample. It has the same two-event
medial/final profile as `T10`, appears in both paragraphs, and directly links
the end of paragraph 1 to the beginning of paragraph 2. If such behavior is
enough to call `T10` a topic resumer, it is enough to nominate this other card
too. The fixed panel gives no independent criterion for choosing between them.

For `T56`, the strongest counterexample is capacity itself: a single paragraph
cannot demonstrate paragraph/topic resumption, and there is no same-frequency,
same-locality control. Four early-line occurrences establish a placement
profile, not a referent.

## Fixed-page predictions and stop condition

On the already fixed four pages, a genuine discourse carrier would have needed
at least one unused discriminator: a repeated residual frame after deletion,
an overt return to an earlier exact state, cleaner paragraph-entry placement,
or a matched-card advantage. None is present.

Therefore V11 should not assign a source gloss to either card. Future evidence
could reopen the question only with a newly authorized Herbal page that gives
independent paragraph recurrence or an externally owned repeated referent.
Within the present ten-page sidequest, the discourse-carrier route is
exhausted.
