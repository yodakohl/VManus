# GDT454 — Methode

## Question

Bleiben Stopps, Scope und Besitzerzustand korrekt, wenn zwei benachbarte
Quellkarten gleichzeitig durch gebundene GDT447-Nachbarn ersetzt werden?

## Inputs

- alle 30.763 GDT447-Nachbarkanten;
- 3.861 wirkliche benachbarte Ereignispaare innerhalb einer Aussage;
- GDT448-Anfangskontexte;
- integrierter GDT451-Aufnahmebefehl.

## Method

Für jede Kombination aus Quellrezept, Mutationsfamilie und neutralem Ausgang
`READABLE`/`STOP` wird vor dem Burstlauf der lexikographisch erste Zielnachbar
gewählt. Das ergibt 5.283 Varianten für alle 1.563 Katalogquellen.

An jedem der 3.861 wirklichen Kartenpaare werden alle gewählten Varianten der
ersten Karte mit allen gewählten Varianten der zweiten Karte kombiniert:

1. erste Zielkarte im wirklichen Anfangszustand lesen;
2. ihren tatsächlichen Ausgabezustand und Aussage-Scope an Karte zwei geben;
3. Karte zwei lesen, auch wenn Karte eins gestoppt hat;
4. danach die wirkliche dritte Quellkarte als Recovery eingeben;
5. bei einer berechtigten Schlusskaskade den nächsten Aussagenanfang prüfen.

Stopps dürfen weder Handlung noch Argument verändern. Identität und historischer
Prior bleiben reine Anzeigen.

## Decision rule and claim ceiling

Jeder Stopp muss zustandserhaltend sein. Eine dritte Quellkarte darf nur dann
stoppen, wenn beide Mutationen ihren benötigten Kopf entfernt haben; dann muss
die nächste Aussage wieder synchronisieren.

Die Bursts sind Angriffe auf den Leser, keine Auftretensprognosen und keine
neuen Manuskriptformen.
