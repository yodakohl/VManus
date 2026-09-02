# GDT734 — V99R7 recurrent unknown-family dispatch

GDT734 führt zwei getrennte Arbeiten über dem unveränderten GDT733-Cache aus:

1. Es repariert einen reproduzierbaren Renderer-Projektionsfehler für 71 bereits
   exportlizenzierte aktive Ganzwörter an 305 Positionen.
2. Es setzt für 20 häufige bislang unbekannte Oberflächen an 226 Positionen
   explorative exakte Ganzwortdefaults ein. Diese sind einzeln als neun
   kompositionell gestützte, fünf rollenbeschränkte und sechs gelernte
   Ganzwörter klassifiziert.

Insgesamt ändern sich 531 Cache-Zellen auf 472 Zeilen. Die Zahl der
`[surface:?]`-Zellen fällt in diesem festen Cache von 7.989 auf 7.458; die Zahl
vollständiger Zeilen steigt von 1.413 auf 1.428. Das misst Rendererabdeckung,
nicht Übersetzungswahrheit.

Ein redaktioneller Präzedenz-Audit umfasst 28 aktive Ganzwortfassungen; 26
davon erhalten eine kürzere gesprochene Fassung, ohne Semantik oder Score zu
ändern.

Die 19-Formen-Kreuzmatrix behandelt `-ol`, `-or`, `-aiin/-ain` und `-ar` als
Arbeitsrollen, exportiert aber kein freies Morphem. `olk` bleibt gebunden und
`-dy` HOLD. Historische Mikroeinträge dienen ausschließlich als
Architekturvergleiche und erhalten null Relations- und Zeichenwertkredit.

## Reproduktion

```bash
python3 experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/src/run.py
python3 experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/src/validate.py
```

Details stehen in [METHOD.md](METHOD.md), das Ergebnis in [REPORT.md](REPORT.md)
und der Artefaktführer in [artifacts/README.md](artifacts/README.md).

Claim ceiling: explorativer Wörterbuch- und Cache-Renderer. GDT734 behauptet
keinen Klartext, keine Sprache oder Phonetik, keine Pflanzenart, Krankheit,
Heilung oder historische Maßeinheit und keinen freien Komponentenwert. Es
öffnet keine neue Seite und verwendet weder `f84` noch `f84r`.
