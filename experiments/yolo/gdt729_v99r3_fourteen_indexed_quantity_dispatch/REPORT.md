# GDT729 report — fourteen ambiguous quantity labels become usable defaults

## Outcome

GDT729 resolves the fourteen forms explicitly named by the current route. The
result is five cardinal amounts, one amount inside an indexed share, seven
open value levels and one quality grade. None remains a slash-separated
non-answer, and none is put on HOLD.

Status:
`PASS_V99R3_14_QUANTITY_READINGS__5_CARDINAL_1_INDEXED_SHARE_7_OPEN_VALUE_1_QUALITY_GRADE_0_MEASURE_0_HOLD__140_OCCURRENCES__NO_SLASH_AMBIGUITY_IN_TARGET_MEANINGS__324_ACTIVE_1248_OTHER_GLOBAL_BYTE_STABLE__SCORE_EVIDENCE_SCOPE_EXPORT_UNCHANGED__ZERO_COMPONENT_CREDIT__ALL_H0_NONE`.

| surface | occurrences | V99R2 | V99R3 default | class | confidence |
|---|---:|---|---|---|---|
| `arain` | 4 | erste Drogenfraktion in Menge II | zwei Teile des Drogenanteils I | indexed share amount | 66 / W3 |
| `chorain` | 2 | Blüten-/Pflanzenteil, Menge/Klasse II | Blütenteil, Wertstufe II | open value | 53 / W2 |
| `choraiin` | 3 | Blüten-/Pflanzenteil, Menge/Klasse III | Blütenteil, Wertstufe III | open value | 58 / W2 |
| `cthan` | 2 | Blatt-/Krautgut, Menge/Klasse I | Blattgut, Wertstufe I | open value | 53 / W2 |
| `cthain` | 4 | Blatt-/Krautgut, Menge/Klasse II | Blattgut, Wertstufe II | open value | 58 / W2 |
| `cthaiin` | 11 | Blatt-/Krautgut, Menge/Klasse III | Blattgut, Wertstufe III | open value | 59 / W2 |
| `dan` | 17 | Grad-/Maßwert I | Wertstufe I | open value | 55 / W2 |
| `daiiin` | 17 | Grad-/Maßwert IV | Wertstufe IV | open value | 55 / W2 |
| `olain` | 11 | Drogenstoff, Menge II | zwei Portionen Drogenstoff | cardinal amount | 76 / W3 |
| `olaiin` | 39 | Drogenstoff, Menge III | drei Portionen Drogenstoff | cardinal amount | 76 / W3 |
| `oraiin` | 26 | Portion III | drei Portionen | cardinal amount | 68 / W3 |
| `qoraiin` | 1 | nimm eine Drogenportion, Menge III | drei Drogenportionen nehmen | cardinal amount | 36 / W1 |
| `solaiin` | 1 | Salz, Menge III | drei Portionen Salz | cardinal amount | 28 / W1 |
| `tdain` | 2 | kalter Grad-/Maßwert II | Kältegrad II | quality grade | 16 / W0 |

The fourteen rows cover 140 exact ZL3b occurrences. The confidence column is
not newly awarded: GDT729 deliberately preserves every inherited score and
level.

## Why the plant-part series is not counted

One independent audit proposed `choraiin = three portions of flower material`
and `cthaiin = three portions of leaf material`. That sounds practical, but it
contradicts the primary head rule. GDT627 explicitly records that these
compounds may encode amount, strength, size, maturity or class and must not be
silently converted to literal organ counts. Their useful default is therefore
the concrete patient plus an honest level:

```text
choraiin  Blütenteil, Wertstufe III
cthaiin   Blattgut, Wertstufe III
```

This is more informative than `Menge/Klasse III`, while leaving the exact axis
available for later local context.

## Why the other quantities can be spoken

`olain/olaiin` already had practical source renderers with two or three parts
of the learned drug material. `oraiin` has a visible OR portion head, and the
GDT693 R/OR contrast requires OR to remain the divided portion rather than an
indexed share. `qoraiin` is a learned action whole, so its old duplicate
wording becomes the single instruction **three drug portions take**.
`solaiin` receives the same cardinal renderer but remains W1: `Saatgut, Charge
III` is retained as its strongest rival.

`arain` is different. It contains the indexed share and an amount inside that
share, so collapsing it to `two portions` would lose information. V99R3 keeps
both levels as **two parts of drug share I**.

Finally, GDT686 showed that the naked D series is a value ladder whose visible
outer head chooses the axis. `dan/daiiin` therefore become `Wertstufe I/IV`.
Exact `tdain` does have a visible cold-quality head, so `Kältegrad II` is the
best working default—still at its inherited W0 score because only two weak
occurrences support it.

## Preservation and limits

The canonical dictionary still has 1,586 rows and 1,582 surfaces. Exactly
fourteen global semantic rows change. All 324 active V99 rows, 1,248 other
global rows, the sixty GDT728 targets and the five active reader artifacts are
byte-stable. Scores, confidence, positive evidence, counterevidence, semantic
scope, export permissions and structural/action flags do not change.

The repeated pieces receive zero component credit. In particular, the result
does not say that `ain` freely means two, `aiin` freely means three, `ar`
freely means share or `d` freely means value/measure. Five historical quantity
comparators remain convention-only controls at `H0_NONE`; no specific period
unit is identified.

Canonical dictionary:
`artifacts/V99R3_COMPLETE_WORD_CONFIDENCE.tsv`.
