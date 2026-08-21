# V17 R4 candidate — the recurrent deck as abbreviated working prose

Date: 2026-08-21

Status: maximally abductive ten-page sidequest candidate. These are concrete
default expansions, not deciphered plaintext.

## Verdict

The best R4 reading is **strongly abbreviated iatromedical working prose whose
most frequent phrases have become whole-card brevigraphs**. It is neither an
ordinary letter substitution nor a rigid modern table. A clerk can learn it by
copying thirty recurrent cards, a much larger exemplar-dependent tail, and a
small set of rules for inherited antecedents and instruction closure.

V16 was basically right about the document type, but several expansions were
too abstract. V17 makes the common deck more like language a fifteenth-century
recipe or register clerk could actually expand:

```text
picture/rubric silently names the treated plant, vessel, conduit or body place
→ take/resume the next portion or instruction
→ add, mix, warm, immerse, rinse, strain or leave standing
→ inherit batch, quantity, place or interval where abbreviated
→ a close-bearing whole card completes that local instruction
→ the statement may continue across the physical line
```

The 30-card deck covers 217/381 prose events. All 217 occurrences have a full
local rewrite in `V17_R4_ALL_OCCURRENCE_READINGS.tsv`; no occurrence receives a
neutral fallback.

## Selected common deck

| surfaces | concrete default expansion | status against V16 |
|---|---|---|
| `AIIN` family | in the quantity previously stated | improved |
| `L/O` family | with the foregoing preparation | improved |
| `Y` family | this same portion | improved |
| `CHEDY/SHEDY/TEDY` | let it stand until ready, then end this instruction | reversed |
| `CHDY/CHEDY` | stir until evenly mixed | improved |
| `OKY/QOKY` | apply the prescribed small portion | improved |
| `QOKEEDY` | bathe or immerse in the tempered warm liquid, then end the instruction | improved |
| `AL` family | at the place indicated by the drawing or rubric | improved |
| `OKAIIN/QOKAIIN` | take up the next portion or instruction | improved |
| `QOKEDY` | rinse the indicated place once, then end the instruction | improved |
| `LCHEDY` | leave it standing in the lower vessel, then end the instruction | improved |
| `OKEEY/QOKEEY` | keep it lukewarm | improved; warming beats mixing |
| `OKAIN/QOKAIN` | add one measured portion to the vessel | improved |
| `OR` family | the prepared decoction or working liquor | improved |
| `CTHY` family | when the preparation is ready | improved wording |
| `OKAL/QOKAL` | mix the two portions together | improved |
| `CHAR/DAR/SAR` | from the same batch | improved; reference beats sequence |
| `DCHEDY/SCHEDY/TCHEDY` | finish this treatment, then end the instruction | improved |
| `CHO/SHO` | thereafter take the following detail | improved |
| `CKHY` family | through the connected channels | retained |
| `CHEEY/SHEY` | until the liquor runs clear | improved |
| `OLCHEDY/QOLCHEDY` | reserve the mixed liquor, then end the instruction | improved |
| `OLKEEDY/SOLKEEDY` | let the liquor settle, then end the instruction | improved |
| `OTAIIN/SOTAIIN` | for the same interval as before | improved |
| `QOKCHDY` | heat it once, then end the instruction | improved |
| `OTAL/QOTAL` | toward the lower outlet | retained |
| `OKCHY/QOKCHY` | use the freshly prepared remedy | improved |
| `KAIN/CHKAIN` | one measured portion | improved |
| `SHCKHEDY` | strain it once through cloth, then end the instruction | improved |
| `CHEKY` | over a gentle heat | improved |

Exactly three rival expansions and their five-part scores are preserved for
every row in `V17_R4_RECURRENT_CARD_DECISIONS.tsv`. No losing rival was silently
deleted.

## Hard ambiguities

### `OKEEY/QOKEEY`: warming beats mixing

The card occurs beside cooling, combined portions, warm-medium cards, rinsing,
an immersed part and a small applied portion. `keep it lukewarm` lets those
neighbors retain different jobs. `mix thoroughly` duplicates the much better
placed `CHDY/CHEDY = stir until evenly mixed`. The selected expansion therefore
keeps heat and mixing distinct.

### `CHEDY/SHEDY`: two cards, not one vague action

The eleven open `CHDY/CHEDY` events are read as stirring or mixing. The twelve
close-bearing `CHEDY/SHEDY/TEDY` events are read as leaving the preparation to
stand until ready and then ending the local instruction. Their similar surface
appearance is thus a workshop hazard, not a reason to flatten their exact-card
identities.

### `OKY/QOKY`: application with a small portion

The Herbal occurrences resist an outlet-only reading, while the Biological
occurrences resist a plant-part reading. `apply the prescribed small portion`
works in both. In Herbal prose its one allowed conditioned expansion is `take
the prescribed small portion`; this is a voice/argument adjustment, not a new
object class.

### `OR`: liquor, not merely “from”

`OR` occurs twice consecutively in one Herbal line and elsewhere beside
expressed juice, a handful, storage, freshness and local application. A pure
source preposition would require too many invisible complements. The concrete
default is the prepared decoction or working liquor.

### `OKAIN/QOKAIN` and `OKAL/QOKAL`

These are separated as **ADD ONE MEASURED PORTION** and **MIX THE TWO PORTIONS**.
This makes `okain char okain` on f82r a deliberate instruction: add one
portion, take it from the same batch, and add one portion again. It also leaves
`KAIN` free to name one measured portion.

### Four close-bearing values

The four recurrent close cards now differ concretely:

- `QOKEEDY`: bathe/immerse in tempered warm liquid;
- `QOKEDY`: rinse the indicated place once;
- `LCHEDY`: leave standing in the lower vessel;
- `SHEDY`: let stand until ready.

Their common terminal behavior belongs to the complete card. It does not turn
their distinct middle content into a single generic `VALUE`.

### `CHAR/DAR/SAR`, `CHO/SHO`, and `O56`

`CHAR/DAR/SAR` is best expanded as `from the same batch`, a concrete
`idem/eadem`-like antecedent reference. `CHO/SHO` occurs only on f56r and leads
successive plant details, so `thereafter take the following detail` is better
than a plant part. This recurrent card is the exact V17 realization of the old
O56 question: it resumes the dossier sequence, while its following card names
root, wine, leaf or preparation. It is not itself any one of those objects.

### `CKHY`

All four recurrent copies fit `through the connected channels`; three appear
in strongly hydraulic Biological sequences and one follows `through a cloth`
and a second conduit. `immersion configuration` is possible but less exact.
The old fused-leaf/stalk interpretation survives only as the one licensed
conditioned expansion if this card should occur in a pictured-plant clause; it
is not needed in these four occurrences.

## Dittography and copying audit

Immediate repetition is not globally discarded as scribal noise.

- On f81v.18, `qokedy qokedy` consists of two separately closed one-card
  fields. The economical reading is **rinse once; rinse once again**, hence two
  rinses. Dittography remains possible but is not required.
- On f83r.27, `shckhedy shckhedy` likewise occupies two separately closed
  fields. The default is **strain once through cloth; strain once again**. A
  repeated filtration is ordinary enough that deletion as dittography would
  lose a usable instruction.
- On f82r.19, `okain char okain` is within one field and contains an intervening
  same-batch reference. That structure positively disfavors mechanical
  doubling: **add one portion—from the same batch—add one portion again**.
- f11r's adjacent but nonidentical cloth/straining cards can be amplification,
  two successive implements, or a copied echo. V17 leaves both concrete steps
  in the passage because no correction mark licenses deletion.

The correction rule is conservative in a specifically scribal sense: preserve
what can be read as a normal repeated operation; emend only when the reading
becomes impossible.

## Segmentation and abbreviation

1. A physical line end is not a sentence boundary. The continuous article may
   carry its subject, batch, place, measure or operation into the next line.
2. A source separator is a strength cue. Close-bearing exact cards end local
   instructions, but several such cells may belong to one larger treatment.
3. Surface wrapper variants of one exact tuple are alternative realizations of
   one learned card, not automatically separate prefixes or inflections.
4. The picture supplies recurring nouns that a working copy omits: the plant,
   vessel, connected path, outlet, or treated body place.
5. `with the foregoing preparation`, `from the same batch`, `in the quantity
   previously stated`, and `for the same interval as before` are ordinary
   abbreviation expansions. They function like `idem`, `eadem`, `ut supra` or
   a carried rubric without requiring those exact Latin words.
6. The learner does not spell the expansion from glyph components. The learner
   recognizes the whole exact card and writes a permitted surface realization.

This is teachable to several hands with four sheets: recurrent-card exemplar,
register-specific rare-card list, close-bearing operation list, and
antecedent/carry rules.

## Whole-page fluent reconstructions

These paraphrases compress the complete line-by-line expansions in
`V17_R4_REWRITTEN_PASSAGES.md`; they do not silently omit an encoded card.

### f10r

The pictured simple is named, kept covered, and taken from the same batch. Join
it evenly, pound it, and use its reddish stem for stomach pain: apply the small
portion in the quantity stated and retain the root. Use the freshly prepared
remedy warm with the foregoing preparation when ready. The plant is found in
the stated habitat; when ready, make the decoction and expressed juice, boil it
gently, and take the repeated portions in the quantity stated. Gather it before
flowering; use a handful of the decoction with the foregoing batch and the
stated quantity. Its flower, working liquor, bitter quality and same portions
are noted, and it is preserved in oil.

### f56r

Gather the pictured simple in spring. Thereafter take the lower root in the
quantity stated. Thereafter use white wine with material gathered before
flowering, applying the prescribed small portion at the indicated place. The
next plant note gives shaded woodland and the same small application before
closing the outlet. Thereafter take the dried leaf and dry it in shade. Use the
freshly prepared remedy for stomach pain and dry it in shade. Thereafter use the
fresh preparation with honey and use it fresh. The last short clause marks the
following pale flower share in the quantity stated.

### f82r

Finish the first treatment, reserve its mixed liquor, add a measured portion,
and bathe this same portion in tempered warm liquid; mix the two portions and
proceed through the second opening to the next basin. Keep the next liquid
lukewarm, strain it clear, continue at the second conduit and through the cloth
and connected channels, then take up the next instruction. Under the same
setting use the broad vessel, draw off the liquid, add prepared oil, mix both
portions and apply a small portion locally. Add clean water for the same
interval, let it stand ready, keep it warm, apply the prescribed small portion
through the first opening, and continue until the liquor runs clear. Add one
portion from the same batch and add one again; bathe it warm and draw off the
clear liquid. Keep the next immersed part lukewarm, in the previously stated
quantity, then immerse it fully and leave it in the lower vessel before closing
the outlet. Begin the next rinse with tempered warm liquid at the indicated
place; use cool water and prepared oil in equal stated portions, then take up
the next warm-water instruction. Finally draw off, pour in warmed water, repeat
at the second opening, bathe warm, take the stated drink, bind the place, bathe
again, and mix in equal shares.

## Retained, improved, reversed

- **Retained without semantic reversal:** connected channels and lower outlet.
- **Retained but made more concrete:** quantity reference, foregoing
  preparation, current portion, qokaiin, mixing, warming, readiness, settling,
  duration, fresh remedy, measured portion and gentle heat.
- **Substantively improved:** small-portion application, warm immersion, local
  rinse, lower-vessel standing, measured addition, working decoction,
  same-batch reference and all four close-bearing values.
- **Reversed:** only V16's generic `set ready` reading for the twelve-member
  `SHEDY` exact card. It is now `let stand until ready`; the old setting gloss
  remains a scored rival rather than vanishing.

## Strongest remaining difficulties

- f10r contains repeated `OR` and `Y` cards whose fluent expansion still sounds
  more tabular than ordinary prose. A short quantity/batch notation may be
  closer than fully vocalized language there.
- `AL = place indicated by drawing/rubric` fits the Biological diagrams better
  than its lone Herbal occurrence; the Herbal reading needs the picture to own
  the treatment locus.
- `LCHEDY = lower vessel` draws specificity from its Biological ecology. Its
  inherited fallback `leave standing in place` is required where no lower
  vessel has just been named.
- `QOKEEDY` may encode addition of warm liquid rather than immersion in it.
  Both generate coherent bath records; immersion currently saves one separate
  application step.
- No sequence selects Latin, a vernacular, or any phonetic expansion. The
  reconstruction is functional and scribal, not linguistic decipherment.

## Seal and independence

Only the seven authorized f84-free prose pages were used for this recurrent
deck stress test. The three Astro pages retain V16 meanings but supplied no
joint-tuple evidence. `f84` and `f84r` were never selected or opened. Candidate
construction used guarded loaders for mixed sources. R4 did not intentionally
use sibling V17 conclusions; an overbroad local text search accidentally
displayed fragments from existing sibling output after the principal R4 deck
had already been independently chosen, so selection should treat shared exact
wording with extra caution.
