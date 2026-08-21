# Candidate V17 R2 — the recurrent medicinal-operation deck

Date: 2026-08-21

Status: **independent, maximally abductive sidequest candidate**. This is a
concrete reconstruction of a possible source text, not a decipherment claim.

## Result

All 30 recurrent exact cards and all 217 of their fixed-page occurrences have
been rewritten. The strongest R2 reading is a compact medicinal-operation
deck shared by open Herbal articles and short Biological treatment cells:

```text
TAKE → MEASURE/TIME → ADD → MIX/WARM → STRAIN
     → BATHE/APPLY → DRAIN → repeat or close
```

The Herbal register fills the same deck with plant parts, wine, honey, juice
and storage. The Biological register fills it with compounded liquor, basins,
conduits, immersion and local rinsing. This is exactly the kind of economy a
small medical workshop can learn: ordinary recipe imperatives upstream, about
twenty portable brevigraph cards downstream, plus page-owned names and parts.

## Main semantic revisions

### Retained

- `DAIIN`: in the stated measure or for the stated time.
- `L/O`: with the foregoing preparation; likewise.
- `Y`: this present portion, locally the treated member.
- `qokaiin`: take up the next entry or portion.
- `CTHY`: when the preparation is ready.
- `CHEDY`: mix until the preparation is even.
- `DAL`: at the indicated affected place.
- `OR`: the prepared liquor, specifically expressed juice in Herbal clauses.
- `CKHY`: pass the liquor through the joined conduits.
- `SHEY`: until the liquor runs clear.
- `OLKEEDY`: let the liquor settle.
- `OTAIIN`: keep it for the stated time.
- `QOTAL`: toward the lower outlet.
- `KAIN`: one measured portion.
- `CHEKY`: at a gentle heat.

### Improved

- `SHEDY`: **give the ordinary lukewarm bath and set it ready**, not merely a
  contentless close.
- `QOKEEDY`: **bathe with the tempered herbal liquor**.
- `QOKAIN`: **add the measured ingredient**, narrower than “put it in.”
- `QOKAL`: **mix the two portions with warm water**.
- `QOLCHEDY`: **keep the combined mixture covered**.
- `QOKCHDY`: **warm it gently once**.
- `QOKCHY`: **use the freshly pounded preparation**.
- `SHCKHEDY`: **strain thoroughly through cloth**; immediate repetition means
  strain a second time.

### Reversed

- `OKY/QOKY`: V16's “lesser portion” loses to **apply or use it at the affected
  place**. It works in f10r, f56r and every Bio occurrence; “lesser” repeatedly
  needs an unexpressed application verb.
- `OKEEY/QOKEEY`: V16's “keep gently warmed” loses narrowly to **mix the
  preparation thoroughly**. It sits naturally between filling, bath choice,
  rinsing and application. A directly heat-flanked occurrence retains the
  conditioned reading “keep gently warmed.”
- `LCHEDY`: “ordinary base setting” loses to **let the liquor drain at the
  lower outlet**. The card repeatedly precedes an explicit basin, outlet or
  next-entry sequence.
- `CHAR/DAR/SAR`: “of the same” is too noun-bound. The portable instruction is
  **repeat the foregoing preparation**; directly before a noun-like card it
  may still read “of the same.”
- `SCHEDY`: generic “finish application” loses to **strain the application and
  set it aside**.
- page-local f56r `CHO/SHO`: “thereafter” loses to **the flowering tops**.

## Why the heat/mix decision falls this way

`QOKEEY` has seven occurrences. “Keep warm” remains locally good, but “mix
thoroughly” makes the complete sequences more economical:

- after ordinary bath and before application (`f82r.7`);
- after filling the vessel and before pouring/rinsing (`f83r.25`);
- between a marked share and its use (`f83r.26`);
- between bind/settle and rinse (`f83r.20`).

Conversely, `QOKCHDY` and `CHEKY` already supply an explicit warm-once/gentle-
heat pair. The deck is simpler if `QOKEEY` owns mixing rather than duplicating
both heat cards. The leading alternative remains close and is recorded in the
decision table; it is not erased.

## Historical fit

The selected operations are ordinary late-medieval recipe language rather than
a modern hydraulic fantasy:

- [British Library Harley MS 2381](https://searcharchives.bl.uk/catalog/040-002048212)
  contains roughly 600 mid-fifteenth-century medical recipes; its catalogue
  quotes a normal `Take ... and pare away` opening and records embedded
  astrological tables, waters, plasters and distillation.
- [British Library Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567)
  preserves a 1446 medical miscellany whose recipe incipit has `take ... and
  seethe it till`, alongside medical astrology.
- [British Library Harley MS 2375](https://searcharchives.bl.uk/catalog/040-002048206)
  combines a Macer herbal, hot and humid baths, clysters, oils, recipes and
  medical astrology in one fifteenth-century volume.
- [British Library Harley MS 2558](https://searcharchives.bl.uk/catalog/040-002032705)
  is a fifteenth-century physician's composite of botanical synonym lists, a
  herbal, case notes, medical and surgical commonplace books and uroscopy.

These witnesses justify the *kind* of source order—take, seethe, measure,
apply, bath, repeat—and the mixed manuscript ecology. They do not identify a
single Voynich card.

## Coverage and cost

| measure | result |
|---|---:|
| recurrent exact cards | 30/30 |
| recurrent-card occurrences | 217/217 |
| concrete rivals per card | exactly 3 |
| cards retaining V16 broadly | 8 |
| cards improved/narrowed | 16 |
| cards reversed | 6 |
| complete rewritten pages | f10r, f56r, f82r |

The price is two conditioned senses (`Y`, `OR`) and two constructional
conditionings (`QOKEEY`, `CHAR/DAR/SAR`), all explicitly listed. No card ends
as UNKNOWN, OPAQUE, CONTENT, PAYLOAD, ITEM, VALUE or STATE.

## Files

- `V17_R2_RECURRENT_CARD_DECISIONS.tsv`: three preregistered concrete rivals,
  component scores, selection, confidence and revision status for all cards.
- `V17_R2_ALL_OCCURRENCE_READINGS.tsv`: every occurrence with two-sided
  context, record/field/line placement and its complete rewritten local line.
- `V17_R2_REWRITTEN_PASSAGES.md`: complete literal and fluent f10r, f56r and
  f82r readings.

## Selection recommendation

Adopt the R2 deck as the medical source layer if the other perspectives also
converge on `OKY = APPLY`, `QOKAIN = ADD`, `CHEDY = MIX`, and a distinct
`QOKCHDY/CHEKY = HEAT` pair. Preserve `QOKEEY = KEEP WARM` as the strongest
rival unless the complete cross-agent rewrite clearly favors mixing.

Seal: only the ten authorized sidequest pages were used. f84 and f84r were not
opened.
