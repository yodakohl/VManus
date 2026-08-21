# V11 adversarial audit — topic carrier versus local Herbal recurrence

Date: 2026-08-21

Status: independent speculative sidequest candidate. This is neither a GDT
result nor a translation.

## Forced decision

`TOPIC_CARRIER_NOT_DISTINGUISHABLE_FROM_LOCAL_PROSE_RECURRENCE`

The strongest pro-topic observation is real: all four `O56` occurrences fall
in the first two positions of their physical lines, and its line-first copies
use `sh` while its medial copies use `ch`. That is good evidence for a stable
opaque card with a position-sensitive realization in an early construction.
It is not evidence that the card denotes or resumes the pictured plant.

`OWNER-10` supplies even less discourse evidence. It occurs once in each f10r
paragraph, but once is ordinary medial material and once is the final card of
a later physical line. The page-local `dcda95c8...` control also crosses the
two f10r paragraphs. Deleting either target leaves ordinary open Herbal lines;
no observable dependency, repeated frame, dangling operand or broken closure
remains. The parsimonious provisional account is **ordinary recurrent
page-local prose/content**, while a topic-resumption function remains a live
but unearned expansion.

## Data and seal

The audit used the guarded f84-free GDT327/current formal rows selected only
for `f10r`, `f11r`, `f55v`, and `f56r`. The target panel contains 100 scored
events. Exact tuple IDs were treated as atomic cards. Source readings below
are only display labels; no spelling, substring or phonetic relation enters
the comparison. `f84` and `f84r` were not selected, opened or inspected.

## All six target occurrences in complete scored contexts

The slash marks a physical line, not a statement boundary. Brackets mark the
target and nothing else.

### f10r, paragraph/record 1

```text
f10r.2  dchey cthoor [char/OWNER-10] chty os chair otytchol oky daiin etyd
f10r.5  qokchy qotchol chol cthy
```

The target is group 3/10, surrounded by ordinary definite spaces. It does not
open the paragraph or line and has distinct opaque neighbors on both sides.

### f10r, paragraph/record 2

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.8  qotchor chor otol chol cholor chol daiin [dar/OWNER-10]
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
```

The target is group 8/8 at a physical line end. It is not repeated at the
start of f10r.9 and does not close an attached DY/B3 field. Calling this
`RESUME` requires an anticipatory or trailing realization different from its
first occurrence.

### f56r, its one scored paragraph/record

```text
f56r.5   chochor [cho/O56] chodaly daiin
f56r.7   [sho/O56] kchol otchor choky dal
f56r.8   schol choy choky cheeckhody
f56r.12  sh [cho/O56] kchey qokokchy
f56r.13  okchy chokcheo kchal
f56r.18  [sho/O56] chokchy kchoar sotodan
f56r.19  otchey keol daiin
```

The four occurrences occupy positions 2, 1, 2 and 1. Every immediate
non-boundary predecessor and every successor is different. Both line-first
copies are rendered `sho`; both group-2 copies are rendered `cho`. All
adjacent internal boundaries are ordinary definite spaces. O56 is absent from
three of the seven lines, including the only scored line with attached DY
closure. It therefore marks neither every line continuation nor every local
closure.

## Exhaustive matched recurrent-card control

This table contains every exact tuple recurring at least twice in the 100-event
four-page panel. `early` means physical-line group 1 or 2. The candidates are
not unique in recurrence, page locality, paragraph transfer or early-line
placement.

| exact card | N | pages | records | FIRST / MIDDLE / LAST | early | diagnostic |
|---|---:|---:|---:|---:|---:|---|
| `2f1c5e56...` | 9 | 4 | 5 | 2 / 4 / 3 | 1 | portable and position-flexible |
| `b921a237...` | 9 | 3 | 3 | 0 / 7 / 2 | 1 | repeated within records |
| `7a4bb813...` | 5 | 2 | 2 | 0 / 5 / 0 | 2 | stable medial control |
| **O56 `2cc05435...`** | **4** | **1** | **1** | **2 / 2 / 0** | **4** | page-local, all early |
| `276a7c2d...` | 3 | 2 | 2 | 0 / 3 / 0 | 0 | cross-page medial control |
| `9ad66e67...` | 3 | 2 | 2 | 2 / 1 / 0 | 3 | exact early-position rival |
| `dcda95c8...` | 3 | 1 | 2 | 0 / 3 / 0 | 0 | page-local and crosses both f10r paragraphs |
| `e0b630cb...` | 3 | 2 | 3 | 0 / 2 / 1 | 1 | record-transfer control |
| `10488b91...` | 2 | 2 | 2 | 1 / 1 / 0 | 1 | mixed first/medial control |
| **OWNER-10 `4d455901...`** | **2** | **1** | **2** | **0 / 1 / 1** | **0** | page-local and crosses paragraphs |
| `d665560c...` | 2 | 2 | 2 | 2 / 0 / 0 | 2 | exact line-entry control |

Seventeen of 100 scored events are line-first. A naive frequency-preserving
hypergeometric comparison gives `P(X >= 2) = .133` for two or more line-first
occurrences among four draws. More relevantly, the recurrent-card panel itself
contains a 3/3 early rival (`9ad66e67...`) and a 2/2 line-first rival
(`d665560c...`). O56's 4/4 first-two-position pattern is worth retaining as a
construction lead, but it was selected after recurrent cards were inspected
and cannot carry a topic interpretation by itself.

## Removal and continuity audit

### OWNER-10

Removing `OWNER-10` turns f10r.2 from ten to nine cards and f10r.8 from eight
to seven. Both remain ordinary one-field open Herbal lines. The later line now
ends in the recurrent `2f1c5e56...` card; no target-seeking continuation occurs
on f10r.9. The page still has the same two paragraph records. Consequently the
card is not an observable structural owner required to bind them.

### O56

Removing O56 leaves lines of lengths 3, 4, 4, 3, 3, 3 and 3. No line becomes
empty, no close loses its host, and all remaining neighboring pairs are legal
observed prose adjacencies. Because O56's three overt left contexts and four
right outcomes do not repeat, deletion reveals no common frame such as
`X O56 Y` whose operands remain systematically homologous.

This does not prove that deletion would preserve an unknown plaintext clause.
It establishes the narrower point: the frozen formal grammar supplies no
observable coherence test that distinguishes topic resumption from deleting a
frequent word or abbreviation.

## Strongest possible pro-topic reconstruction

The pro-topic case combines four observations:

1. each page depicts one prominent simple, providing a silent dossier owner;
2. OWNER-10 is the only two-copy f10r card specifically nominated because it
   recurs once in each paragraph under different wrappers;
3. O56 is page-private, spread through a long article and always early in its
   line;
4. O56's `sho` at line entry versus `cho` medially looks like a teachable
   renderer adaptation of one underlying resumption card.

A scribe could therefore have used different page-local abbreviations for
something like `CURRENT ARTICLE`, `OF THIS SIMPLE`, or an abbreviated plant
name. Illustrated Herbal traditions make this historically possible. The
*Circa instans* organizes hundreds of simples as separate entries, and
Pseudo-Apuleius chapters repeatedly deploy the current herb in multiple
remedies. The Wellcome catalogue even transcribes chapter openings such as
`Nomen herbe plantago` and later anaphoric `huius` material. Picture-first
production and text reflow are also well documented for illustrated herbals.

These comparators establish a plausible source practice, not an alignment:

- Jean A. Givens, “Production and design of early illustrated herbals,”
  *Word & Image* 38 (2022), DOI
  `10.1080/02666286.2021.1951518`;
- [Wellcome Collection, Pseudo-Apuleius Herbarium manuscript
  catalogue](https://wellcomecollection.org/works/cjz7ymnk);
- [CELT, *An Irish Materia Medica* introduction](https://celt.ucc.ie/document/G600005/);
- [Paris et al., medieval *Cucumis* iconography and the *Circa instans*
  tradition](https://pmc.ncbi.nlm.nih.gov/articles/PMC3158695/).

The same history also supplies the strongest anti-topic reading. A Herbal
entry naturally repeats ordinary lexical material: *herba*, the plant name,
parts, preparations, ailments, relational expressions, and imperatives. A
page-private recurrent item can therefore be content precisely because each
page concerns a different simple. Internal recurrence cannot choose among a
name, a part, a preparation, an anaphoric expression, or a common local
construction.

## Competing architectures

| architecture | fit | decisive problem |
|---|---:|---|
| ordinary frequent prose / repeated local content | **88/100** | explains recurrence parsimoniously but cannot name the content |
| TOPIC_RESUME | 79/100 | O56 fits; OWNER-10's line-final occurrence does not |
| LOCAL_RELATION | 73/100 | position flexibility is plausible, but no operand relation repeats |
| PAGE_OWNER | 67/100 | page locality fits; neither candidate consistently opens or labels its page |
| renderer/position effect alone | 58/100 | explains `sho/cho`, not why this exact tuple recurs |

The numerical rubric favors ordinary local prose, but that is not a positive
lexical identification. The evidence does not cross the stronger distinction
required by the protocol, hence the formal forced decision remains
`TOPIC_CARRIER_NOT_DISTINGUISHABLE_FROM_LOCAL_PROSE_RECURRENCE`.

## Controlled continuous readings

### Topic-carrier version

> **f10r:** Regarding the pictured simple: [opaque identification],
> **CURRENT ARTICLE**, [opaque description and relation material]. [The
> article continues.] In the second paragraph [opaque property/relation
> material]; [further material], **CURRENT ARTICLE**. [Continuation.]

> **f56r:** For the pictured simple: [opaque head], **OF THE CURRENT SIMPLE**,
> [opaque material]. **OF THE CURRENT SIMPLE**, [new opaque material]. [A
> separate closed local clause.] [Opaque head], **OF THE CURRENT SIMPLE**,
> [new material]. [Further clause.] **OF THE CURRENT SIMPLE**, [new material].
> [Final continuation.]

### Equally compatible local-content version

> **f10r:** Regarding the pictured simple: [opaque identification], **R10**,
> [opaque description]. [Continuation.] In the second paragraph [opaque
> material]; [further material], **R10**. [Continuation.]

> **f56r:** [Opaque head], **R56**, [opaque material]. **R56**, [new material].
> [Other clause.] [Opaque head], **R56**, [new material]. [Further clause.]
> **R56**, [new material]. [Final continuation.]

The second reading loses no observed fact. Replacing `R10/R56` with a plant
part, preparation, property, common construction or anaphoric resumption is
not decidable from these six events.

## Hard falsifiers and fixed-page predictions

A future topic-carrier promotion would require evidence not used to nominate
the cards, for example:

1. a fixed-page visual/layout annotation showing that every target occurrence
   resumes the same independently identifiable object after an interruption;
2. a repeated construction in which target deletion uniquely destroys a
   relation while matched recurrent cards do not;
3. a source-independent parallel article where the corresponding slot is
   known to repeat the article owner;
4. O56 outperforming the `9ad66e67...`, `10488b91...` and `d665560c...`
   early-position controls on a consequence other than the position used to
   select it;
5. OWNER-10 acquiring one stable discourse placement rather than needing both
   medial introduction and line-final anticipation.

Within the fixed four Herbal pages, the strongest counterexamples are already
present: `dcda95c8...` duplicates OWNER-10's cross-paragraph recurrence without
being the nominated owner, and `9ad66e67...` duplicates O56's all-early
ecology. If those controls can be ordinary relation/content cards, so can the
targets.

## What the O56 early-line pattern actually licenses

It licenses exactly this much:

```text
O56 = page-local opaque card with a strong early-construction preference
      and a line-entry-sensitive sh/ch surface realization
```

It does **not** license:

```text
O56 = plant | this plant | its | water | leaf | preparation | resume
```

Thus V11 should retain O56 as an anonymous early constructional card, withdraw
`OWNER-10` as a privileged page-owner label, and avoid using either card as a
semantic anchor in later sidequest translations.
