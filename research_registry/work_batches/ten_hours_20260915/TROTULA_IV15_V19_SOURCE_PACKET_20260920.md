# Trotula IV15 and V19 source packet

Status: source-only packet, not a target reading, medical claim, experiment,
or translation. IDEA000421 and its dose-scope audit remain unchanged.

## Owned page and boundary

The official BSB scan's cached page8 image was inspected natively. Its SHA256 is
`5d9ce0a3a738fd8286b0fc270ae900983ec7013b3a6502e6ad29d85be316623e`, matching
the cached source receipt in `TROTULA_COMPLETE_CONTENT_20260920.json`.
The printed page is page 8 of the 1544 *Experimentarius medicinae*, digital
object `bsb10197839`.

This packet owns two complete source spans on that page:

1. IV15 begins with the alternative marker `Vel` after the preceding evening
   prescription and ends with the evening two-drachm administration.
2. V19 begins with the heading `Experimentum probatissimum ad Matricem
   egressam` and ends with the asserted return of the matrix to its own place.

The 1544 print is the owned witness. It does not establish pre-1420 wording or
order. The historical claims below report what this page writes; they are not
medical facts.

## Diplomatic transcription from page 8

Line-break hyphenation is expanded only where the page visibly breaks a word;
abbreviations, punctuation and the printed `i/j` numeral forms are retained in
the transcription. The final `apii` is normalized from the printed `apii`
letterform; it is not a target gloss.

```text
Vel Recipe castorei, piperis albi, costi, menthæ, apii,
ana drac. i. terantur, & distemperentur cum vino albo vel dulci,
& da sero drach. ij.

Experimentum probatissimum ad Matricem egressam.
Recipe pulveris de corde cervi, foliorum lauri, ana drach. i,
myrrhæ, scrup. i. distemperentur trita cum vino,
& dentur potanda; & sic Matrix revertetur in suum locum.
```

The page's lineation places the IV15 sentence in the preceding chapter's
continuous paragraph and the V19 experiment below the `Experimentum` side
label. The packet treats the printed words as one IV15 alternative and one
named V19 experiment; it does not infer a modern sentence boundary beyond
those visible source headings and punctuation.

### Reading uncertainties retained

* `apii` is the genitive ingredient form as read from the print; the final
  letter has the period's early-modern i/j appearance. No botanical identity
  is added.
* `drac. i.` and `drach. ij.` are printed abbreviations for the source's
  quantity expressions. This packet records the values as one drachm and two
  drachms while preserving the abbreviated surfaces.
* `ana` scopes the equal one-drachm amount over the five IV15 ingredients.
  In V19, `ana drach. i.` clearly follows the heart-powder and laurel-leaf
  pair; `myrrhæ, scrup. i.` is a separate one-scruple amount. The source does
  not state that myrrh shares the drachm amount.
* `trita` in V19 is grammatically and referentially awkward after the listed
  genitives. It is retained as printed, with the conservative typed reading
  “having been ground/pounded” left scope-uncertain. It is not silently
  rewritten as a separate ingredient or as a completed prior action.
* `distemperentur` can cover tempering, diluting or mixing. The packet uses
  `MIX_OR_TEMPER`, not a modern chemical operation.
* `cum vino albo vel dulci` explicitly gives white **or** sweet wine in IV15;
  no wine quantity is printed. V19 says only `cum vino`, with neither wine
  type nor quantity.
* `da sero drach. ij.` is an evening administration of two drachms. The
  source does not say whether this dose is measured before or after wine is
  added, and does not identify a dry-powder versus finished-mixture referent.
* `dentur potanda` gives V19 as something to drink, but supplies no dose or
  time. `revertetur in suum locum` is the source's asserted outcome, not an
  independently verified physiological result.
* `probatissimum` is a superlative claim in the heading (“most proven” or
  “best tested” experiment). It is retained as source rhetoric, not evidence
  that the outcome was independently measured.

## Complete typed content inventory

The corresponding machine-readable AST is
`TROTULA_IV15_V19_SOURCE_PACKET_20260920.json`. It separates named source
roles from interpretation:

```text
IV15 = ALTERNATIVE(
  prior=IV14,
  TAKE([castoreum, piper_albus, costus, mentha, apium],
       amount_each=D),
  GRIND_OR_POUND(all_five),
  MIX_OR_TEMPER(with=CHOICE(white_wine, sweet_wine), amount=UNKNOWN),
  ADMINISTER(amount=2D, route=UNKNOWN_DRINK_SCOPE, time=EVENING)
)

V19 = EXPERIMENT(
  claim=PROBATISSIMUM,
  condition=MATRIx_EGRESSAM,
  TAKE([
    (powder_from(deer_heart), D),
    (laurel_leaves, D),
    (myrrh, S)
  ]),
  GRIND_SCOPE=UNCERTAIN(trita),
  MIX_OR_TEMPER(with=wine, amount=UNKNOWN, type=UNKNOWN),
  ADMINISTER(route=DRINK, amount=UNKNOWN, time=UNKNOWN),
  ASSERTED_OUTCOME=matrix_returns_to_own_place
)
```

`D` and `S` are source unit roles, not converted numerical values. IV15's
quantified dry subtotal is `5D`; it is not the mass of the finished wine
mixture. V19's quantified dry base is `2D + 1S`, with no total dose. No
conversion `S/D`, no wine mass, and no `2/5` fraction is supplied by this
page.

## IV15 full scope

The preceding `Vel` marks this recipe as an alternative to the nearby evening
prescription. The alternative retains all of these operations and arguments:

| Source phrase | Typed role | Scope kept open |
|---|---|---|
| `Recipe castorei ... apii` | five named ingredients | no modern botanical normalization |
| `ana drac. i.` | one drachm each | dry ingredient subtotal `5D` only |
| `terantur` | grind/pound all listed ingredients | source does not state whether wine follows grinding immediately or is added during tempering |
| `distemperentur` | temper/mix | operation identity broader than modern “dissolve” |
| `cum vino albo vel dulci` | medium choice: white or sweet wine | wine amount and final mixture mass unknown |
| `da sero` | administration time: evening | no target time category is inferred |
| `drach. ij.` | administration amount: two drachms | dry versus finished-mixture dose scope unknown |

The source therefore supports `dry_subtotal = D+D+D+D+D = 5D` and a separate
`ADMINISTER(2D, EVENING)` node. It does not support `dose_fraction=2/5`.

## V19 complete experiment

V19 is not merely a three-ingredient list. Its named heading, condition,
processing, route and outcome are all retained:

1. The heading names a **most-proven experiment** for a matrix that has
   emerged (`Matricem egressam`). This is a source assertion about the
   experiment's status and its intended condition.
2. `pulveris de corde cervi` supplies powder from deer heart; the source does
   not say whether the heart was powdered immediately here or prepared before
   the instruction.
3. `foliorum lauri` supplies laurel leaves. `ana drach. i.` gives one drachm
   each to the heart powder and laurel leaves.
4. `myrrhæ, scrup. i.` adds myrrh at one scruple. It is not silently folded
   into the preceding drachm equality.
5. `distemperentur trita cum vino` orders a tempering/mixing with wine and
   contains the unresolved `trita` scope. Wine type and amount are absent.
6. `dentur potanda` orders oral/drink administration, without amount or time.
7. `& sic Matrix revertetur in suum locum` asserts that the matrix will return
   to its own place. This is the claimed endpoint of the experiment, not a
   verified observation in the source packet.

The V19 AST thus preserves a named experiment with a conditional initial
state, a typed three-ingredient amount vector, processing, medium, route and
claimed state transition. It does not turn the heading's superlative into a
success statistic or merge V19 with the preceding manual-restoration clause.

## Source-level contrasts and limits

The packet distinguishes several source operations that a complete writer must
keep apart:

* IV15's five equal dry amounts versus V19's two equal drachm amounts plus a
  one-scruple third ingredient;
* `terantur`/`trita` grinding language versus `distemperentur` mixing or
  tempering;
* IV15's white-or-sweet wine choice versus V19's untyped wine;
* IV15's evening two-drachm administration versus V19's undosed drink;
* IV15's alternative marker versus V19's named “most-proven experiment”;
* V19's asserted return-to-place outcome versus a source-independent observed
  outcome.

The exact IV15 dose-scope rivals remain: two drachms as a dry dose, two
drachms of the finished wine mixture, or two drachms per ingredient. The page
does not resolve them. The exact V19 arithmetic remains `2D+S`; assigning a
scruple-to-drachm conversion would add an external convention.

No target word, target participant, or target medical meaning is assigned.
Exploratory joint hypotheses may use this typed source packet without prior
independent target translations, but a fixed future writer must retain every
source node and expose its unknown scopes. No target or global files were
changed.

## Root correction before GDT1000 registration

The preceding claim that the page leaves all three dose readings unresolved
is too broad. The ordinary wording gives a two-drachm administration amount.
It does not repeat `ana` or say two drachms per ingredient at that point.
`PER_COMPONENT_DOSE` is an added rival hypothesis, not an equally supported
reading of the sentence. GDT1000 retains the administered amount and the
unstated material referent; it does not fit per-ingredient dosing or2/5.
This correction preserves the original packet prose and qualifies it explicitly.
