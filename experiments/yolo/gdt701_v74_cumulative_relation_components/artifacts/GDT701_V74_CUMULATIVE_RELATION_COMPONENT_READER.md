# GDT701 — V74 cumulative relation components

Status: `PASS_V74_11_EDGES__9_CONNECTED_COMPONENTS__23_EDGE_NODES_2_HULL_ONLY_1_STRUCTURAL__ZERO_EDGE_WORD_DELTA`

## Nine complete practical components

| component | locus | edges | support | topology | practical microrecord |
|---|---|---|---|---|---|
| M001 | `f104v.2` | C009 | B_ONLY | SINGLE_EDGE | Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen. |
| M002 | `f105v.1` | C001 | A_ONLY | SINGLE_EDGE | Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. |
| M003 | `f113v.17` | C002 | A_ONLY | SINGLE_EDGE | Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen. |
| M004 | `f75r.3` | C003 | A_ONLY | SINGLE_EDGE | Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen. |
| M005 | `f77r.38` | C005 | A_ONLY | SINGLE_EDGE | Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben. |
| M006 | `f80v.35` | C004\|C008 | A_PLUS_B | ORDERED_REPEATED_COMMON_DESTINATION_FANOUT | Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben. |
| M007 | `f86v6.25` | C007\|C006 | A_MINUS_PLUS_B | SERIAL_ACTION_OUTPUT_CHAIN | Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. |
| M008 | `f86v5.24` | C010 | B_ONLY | SINGLE_EDGE_WITH_UNBOUND_QUANTITY_HULL | Anteil I des Ansatzes. [Ungebundene Mengenangabe #2: „Menge III“.] Den Ansatzanteil auf Stufe II erhitzen. |
| M009 | `f26r.2` | C011 | B_ONLY | SINGLE_EDGE_ACROSS_EXACT_STATE_CHECKPOINT | Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von ‚hiervon‘ offen]. [Zustandsvermerk ohne eigenen Materialträger: Mittlere Trockenstufe erreicht.] Die erhitzte Krautdroge bis zur Mittelstufe abkühlen und abschließen [C011-Arbeitshypothese]. |

## Graph accounting

- 11 inherited edges form exactly 9 connected components on exact locus+ordinal nodes.
- The components contain 23 unique edge nodes and 25 edge-node incidences; only f80v.35#3 and f86v6.25#4 are shared nodes.
- C010#2 and C011#5 lie inside their convex hulls but are not edge nodes. C011#7 is render-only structural closure outside hull 4–6.
- M007 remains the sole written serial intermediate. No component has a named final action result or an admitted outgoing final-result edge.
- M008 preserves AIIN as an unbound quantity register. M009 preserves the heated-Krautdroge identity as an explicit B-hypothesis, not a written output word.
- All 479 token glosses, 51 line translations and 3 bound spans are byte-identical; no edge, word meaning or page is added.
