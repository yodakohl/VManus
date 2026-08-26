# GDT442 — Die 47 roten Grundkarten

## Ergebnis

Die 269 roten GDT441-Kandidaten sehen groß aus, reduzieren sich aber auf ein
kleines, handhabbares Stop-Inventar:

- 44 bislang ungelernte direkt benachbarte Handlungspaare;
- 2 ungelernte Kopf–Grad-Kanten: `CHD<-EEE` und `R<-EEE`;
- 1 Kontextfehler: `DY` ohne sichtbaren oder geerbten Handlungskopf.

Das sind 47 Regeln. Jede wurde als minimale Karte durch den echten Leser
geschickt. Alle 47 stoppen am richtigen Grund, alle 47 lassen Handlung und
Argument unverändert, und nach allen 47 Stopps liest die Maschine die nächste
gültige Karte normal weiter.

## Die vollständige Karte

Der relevante Faktorraum hat nur 201 Zellen:

| Familie | Grün | Gelb | Stop | Gesamt |
|---|---:|---:|---:|---:|
| direkte Handlungspaare | 31 | 6 | 44 | 81 |
| Kopf–Fokus-Kanten | 104 | 4 | 2 | 110 |
| Schlusskopf/Kontext | 9 | 0 | 1 | 10 |
| **Gesamt** | **144** | **10** | **47** | **201** |

Damit kann man bei einer neuen sichtbaren Karte nicht nur „geht/geht nicht“
sagen, sondern den exakten fehlenden Baustein nennen.

## Was hinter den 269 Stopps steckt

Von den 269 neutral getesteten Kandidaten:

- 217 enthalten mindestens ein ungelerntes direktes Handlungspaar;
- 52 enthalten `DY`, aber im neutralen Test keinen aktiven Kopf;
- 6 der 217 Paarfälle enthalten zwei fehlende Paare;
- deshalb summieren sich die Blockregel-Vorkommen auf 275;
- nur 24 der 47 Stop-Regeln werden von diesem Kandidatenraum berührt: 23
  Paare und der fehlende Schlusskontext.

Die übrigen 23 Regeln—21 Paarlücken und die beiden Fokuslücken—stehen trotzdem
im Deck. Sie sind genau die Fälle, die auf einer späteren Seite sonst erstmals
überraschend auftauchen könnten.

## Wichtige Korrektur: 52 Stopps sind Kontextfragen

`CLOSE:NO_ACTIVE_ACTION` bedeutet nicht, dass die betreffende Karte verboten
ist. Sechs solcher Rezepte kommen in der aktuellen Ausgabe sogar vor:
`AL+DY`, `L+DY`, `OL+O+DY`, `OT+AL+DY`, `OT+AR+DY` und `OT+O+DY`.
Im Manuskript erben sie links einen Handlungskopf; in der neutralen
Kandidatenliste fehlte dieser Zustand.

Die richtige Lehrregel lautet daher:

```text
DY ohne Kopf -> STOP und Kontext verlangen
DY mit einem der neun alten Köpfe -> den laufenden Schritt schließen
```

Das nächste Experiment sollte die 52 neutralen Schlusskandidaten systematisch
gegen alle neun eingehenden Köpfe laufen lassen. Dann wissen wir im Voraus,
welcher Kontext jeden Kandidaten rettet und wo zusätzlich eine der zwei echten
Fokuslücken greift.

## Benutzung

```bash
python3 experiments/yolo/gdt442_forbidden_factor_stop_deck/src/explain_stop.py \
  --recipe A_ADDR+T+S+OR
```

liefert `PAIR:T>S`. Für eine grüne Karte liefert derselbe Befehl eine leere
Blockliste. Optional können `--incoming-action`, `--scope-incoming-action` und
`--next-recipe` gesetzt werden.

„Stop“ heißt weiterhin nur: **mit dem jetzigen Lehrdeck nicht lesen**. Es ist
keine Behauptung, dass der Schreiber diese Verbindung nie verwenden durfte.
