# GDT701 — the complete current relation atlas

Status: `PASS_V74_11_EDGES__9_CONNECTED_COMPONENTS__23_EDGE_NODES_2_HULL_ONLY_1_STRUCTURAL__ZERO_EDGE_WORD_DELTA`

## Result

All eleven currently admitted occurrence relations can be rendered together
without falling back to “take material, perform work, continue.”  They form
exactly nine local components:

| component | locus | edges | practical reading |
|---|---|---|---|
| M001 | `f104v.2` | C009 | Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen. |
| M002 | `f105v.1` | C001 | Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. |
| M003 | `f113v.17` | C002 | Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen. |
| M004 | `f75r.3` | C003 | Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen. |
| M005 | `f77r.38` | C005 | Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben. |
| M006 | `f80v.35` | C004+C008 | Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben. |
| M007 | `f86v6.25` | C007→C006 | Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. |
| M008 | `f86v5.24` | C010 | Anteil I des Ansatzes. [Ungebundene Mengenangabe #2: „Menge III“.] Den Ansatzanteil auf Stufe II erhitzen. |
| M009 | `f26r.2` | C011 | Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von „hiervon“ offen]. [Zustandsvermerk ohne eigenen Materialträger: Mittlere Trockenstufe erreicht.] Die erhitzte Krautdroge bis zur Mittelstufe abkühlen und abschließen [C011-Arbeitshypothese]. |

The atlas now gives one exact home to every current edge.  Seven components
contain one edge, M006 is a two-action fan-out to one written destination, and
M007 is the sole serial chain with a written intermediate product.  The last
action in every component still lacks an admitted, separately named final
result.

## What is deliberately not smuggled into the reading

The graph has 23 unique edge nodes and 25 edge incidences.  Only
`f80v.35#3` and `f86v6.25#4` are genuine shared nodes.  Two visually intervening
positions are not nodes:

- `f86v5.24#2 aiin` is an unbound quantity register inside the C010 hull;
- `f26r.2#5 chedy` is an exact state checkpoint inside the C011 hull.

The free `dy` at `f26r.2#7` is retained only to close the rendered clause; it
lies outside C011's #4--#6 hull.  These distinctions prevent readable prose
from silently becoming extra relation evidence.

M009 is the only component whose material persistence is itself an inferred
B-tier action-output link.  The source action writes *Krautdroge* as its
patient, but it writes no separate word meaning “heated herb.”  M008 likewise
does not attach “Menge III” to the heating object.  These brackets expose the
remaining uncertainty instead of replacing it with generic filler.

## Scope and gain

- 11/11 inherited edges assigned exactly once to 9 components.
- 7 one-edge components, 1 repeated-destination fan-out, 1 serial chain.
- 23 edge nodes, 25 incidences, 25 minimal-hull positions, 2 hull-only
  positions and 1 render-only structural position.
- 17 held rivals and 27 reference decisions preserved unchanged.
- 479 token glosses, 51 line translations and 3 bound spans byte-identical.
- 0 new edges, participant identities, word meanings, pages or f84/f84r
  access.

The material gain is a single compact atlas that can be read, compared and
challenged as nine concrete local process fragments.  It is not a new
translation layer or a decipherment claim.

## Next useful move

Keep this nine-component atlas fixed.  The next finite question is whether an
explicitly written result label occurs in the exact immediate right context
of any of the eleven target actions.  Such a label may nominate an outgoing
result edge; mere adjacency, fluent recipe order or an assumed default output
may not.
