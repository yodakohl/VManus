# GDT442 method

## Question

Welche elementaren Faktorregeln stecken hinter GDT441s 269 neutralen Stopps,
und bleibt der Leserzustand bei jeder möglichen Grundregel intakt?

## Inputs

- GDT441s vollständige 4.938-Kandidaten-Faktortabelle;
- der ausführbare GDT441-Faktorleser;
- dessen unveränderte Action-, Focus- und Close-Inventare.

## Method

Zuerst werden alle 269 Kandidaten mit `STOP__UNLICENSED_FACTOR` in einzelne
Blockgründe zerlegt. Danach wird der vollständige endliche Raum ausgeschrieben:

- 9×9 = 81 geordnete direkte Handlungspaare;
- 10 Köpfe einschließlich Besitzer × 11 Fokuskerne = 110 Kopf–Fokus-Kanten;
- neun sichtbare Schlussträger plus der Fall ohne aktiven Kopf = 10.

Jede der 201 Zellen wird grün, gelb oder Stop. Die 47 Stop-Zellen bilden das
Deck. Für jede wird eine minimale unlistete Probe gebaut. Handlungspaar- und
Fokusproben laufen nach `OK+Y`, die Schlussprobe startet in einem leeren
Besitzerbank. Nach dem erwarteten Stopp folgt eine gültige Karte. Damit werden
Stoppgrund, unveränderter Zustand und Wiederaufnahme separat geprüft.

## Decision rule and claim ceiling

Ein Stop darf weder den aktiven Handlungskopf noch das aktive Argument ändern.
Es gibt keine automatische Reparatur. Eine künftig sichtbare Wiederholung kann
einen Stop nur durch neue reale Evidenz zu Gelb/Grün machen; GDT442 selbst
promoviert nichts.

Die sechs derzeit beobachteten neutralen Stop-Kandidaten sind ausschließlich
Schlusskarten, die in ihrem realen linken Kontext einen Kopf erben. Sie sind
kein Widerspruch: Der neutrale Kandidatenraum hatte diesen Kontext absichtlich
nicht.
