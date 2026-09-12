# P30 — aus D0 erzeugte Konfigurationen

Jeder Kasten zeigt ausschließlich die hypothetische A/B-Kante nach allen zugehörigen Records. Keine rekonstruierte Gesamtzeichnung.
A/B bleiben ungebundene Funktionsstellen. Eine gestrichelte Verbindung in diesen Diagrammen bezeichnet fehlende Kante, keine unsichere beobachtete Bildkante.
Alle nicht durch D0 erzeugten Bilddetails sind in VISION.md erhalten, nicht als passend vorausgesetzt.

## Gemeinsames Grundschema

```mermaid
graph LR
 A["A: ungebundene Stelle"] -.- B["B: ungebundene Stelle"]
```

Anfang: e(A,B)=0; Herstellen setzt1, Lösen setzt0. Beide Knoten bleiben erhalten.

## Tafel f83r

```mermaid
graph TB
 subgraph P0["F83_UPPER_SPRAY · e=0"]
 A0["A"] -.- B0["B"]
 end
 subgraph P1["F83_MIDDLE_LOOP · e=1"]
 A1["A"] --- B1["B"]
 end
 subgraph P2["F83_LOWER_DRIP · e=0"]
 A2["A"] -.- B2["B"]
 end
 subgraph P3["F83_LOWER_COUPLED · e=1"]
 A3["A"] --- B3["B"]
 end
```

## Tafel f77r

```mermaid
graph TB
 subgraph P0["F77_TOP_ARCH · e=1"]
 A0["A"] --- B0["B"]
 end
 subgraph P1["F77_MIDDLE_BODY · e=1"]
 A1["A"] --- B1["B"]
 end
 subgraph P2["F77_LOWER_VESSEL · e=1"]
 A2["A"] --- B2["B"]
 end
```

## Tafel f82r

```mermaid
graph TB
 subgraph P0["F82_TOP_COUPLED · e=0"]
 A0["A"] -.- B0["B"]
 end
 subgraph P1["F82_MIDDLE_TRANSFER · e=1"]
 A1["A"] --- B1["B"]
 end
 subgraph P2["F82_BOTTOM_COMMUNAL · e=1"]
 A2["A"] --- B2["B"]
 end
```
