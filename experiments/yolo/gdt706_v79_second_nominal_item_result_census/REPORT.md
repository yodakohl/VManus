# GDT706 — delayed written-result census

Status: `PASS_V79_83_ACTION_DISPOSITIONS__161_DELAYED_PAIRS__28_BOUNDED_CELLS__1_NEW_C019_BUNDLE_10_HOLDS_17_STOPS__18_EDGES_12_COMPONENTS__ZERO_WORD_DELTA`

## Result

The search now has both a complete outer map and a completely read near zone.
Forty-two action windows that were still unbound at the start contain 161 later semantic items. The
nearest 28 rank-2/rank-3 cells divide into one admitted result bundle, ten
useful holds, and seventeen visible stops.

The new local reading is:

> **C019 / f86v6.25#2-7:** Aus dem Anteil I des heißen Holzansatzes einen
> heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe
> III erhitzen. Ergebnis: Die Drogenportion ist vollständig bis zur letzten
> Heizstufe geführt.

This is materially more concrete than a generic action sequence: it names the
source share, measured drug share, heat stage, written result material, and
written terminal heating state.

## Why #6 is not skipped

The new relation's source is `#5 ykaiin`, while its state endpoint is
`#7 okeeeey`. The intervening `#6 or` is not discarded. It supplies the missing
written patient, *Drogenportion*, and remains in the rendered result bundle
`#6-7`. In the cumulative graph it is a hull-only material carrier rather than
an endpoint, because C019 asserts one action-to-result relation, not two
independent relations.

The strongest alternative is that #6 and #7 begin two separate register
entries. That keeps C019 occurrence-bound. The next entry, `#8 ofchedy`
(*fertig getrocknete Blütenmasse*), changes both material and operation and
therefore ends this result path. The later `#9 qokaiin` cannot be selected by
skipping that break.

## Complete accounting

| layer | count | result |
|---|---:|---|
| all actions | 83 | 5 immediate results, 42 delayed windows, 13 one-item windows, 15 action boundaries, 8 line ends |
| initially unbound delayed windows | 42 | 41 remain without a delayed result after C019 |
| raw later positions | 163 | includes two period controls |
| semantic delayed pairs | 161 | complete outer search map |
| bounded cells read in full | 28 | 16 rank 2 plus 12 rank 3 |
| admitted | 1 | D026 / A077 / C019 |
| held | 10 | concrete but incomplete readings |
| stopped | 17 | material, operation, state, or earlier-result break |

The outer map matters: the bounded decision does not hide longer candidates.
In particular, A083's three-token sequence remains explicitly available for
the next pass.

## Strongest holds

| case | practical reading | what remains open |
|---|---|---|
| A029 | leicht erhitzter Ansatzstoff | `dar` supplies a share, but measurement is not licensed and *leicht* is not mirrored exactly |
| A070 | trockenes Maß bis zum heiß-trockenen Anfang erhitzen | heating matches; measure and exact destination degree remain unwritten |
| A017 | getrockneter Krautanteil I | the herb preparation is a plausible patient, but the middle stage is absent |
| A063 | Drogenstoff in einen heißen Empfänger geben | concrete argument chain, but no transformed output is written |
| A082 | trockenen Drogenstoff in heißen Ansatzstoff geben | useful patient/destination order candidate, not yet a result edge |

These remain available working readings rather than being erased.

## Cumulative graph and preservation

C019 extends existing component M007. The graph changes from 17 to 18 edges
while remaining at twelve components. It now contains 33 unique edge nodes, 39
edge incidences, 36 hull/render positions, six shared nodes, and three hull-only
positions. `f86v6.25#6 or` is the new hull-only position.

All 479 token glosses, 51 line translations, three bound spans, and 36 pages
remain unchanged. The independent validator performs 71,625 checks. The GDT388
packet correctly remains invalid/not score-ready because its single relation
has no sealed formal-access packet.

## Next

Use the now-published 161-pair map rather than rediscovering delayed positions.
The next focused bundle is A083 `f8r.15#1 → #2-4`: measured portion dried to the
middle stage, followed by written drug material, dry state, and middle-grade
state. Compare it with the longer A073, A002, and A012 alternatives. Open no
new page and change no word meaning.

## Claim ceiling

C019 is a replaceable occurrence-bound working relation inside the current
exploratory codebook. It is not recovered Voynich plaintext, a portable output
rule, or historical proof of the current German glosses.
