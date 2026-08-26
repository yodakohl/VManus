# GDT494 — Methode

## Question

Welche der 73 GDT493-Arbeitskompositionen besitzen die stärkste alte
Rahmenfamilie im selben Register, und welche sind bisher nur durch
registerübergreifende Zielhandlungsbelege gestützt?

## Inputs

- GDT416: 4.576 exakte beobachtete Imperativklauseln;
- GDT493: 73 sichtbar markierte `COMPOSED_WORKING`-Zellen und deren kompakter
  Status.

## Method

1. Für jede Zielkarte werden die übrigen acht bekannten Handlungsköpfe in
   denselben formalen Rahmen eingesetzt. Nur exakte GDT416-Rezepte im selben
   Register zählen.
2. Nicht-T/R-Köpfe werden getrennt von der T/R-Gegenaktion gezählt. Events,
   Seiten und beobachtete Klauseln bleiben an jeder Stützzelle sichtbar.
3. Zusätzlich wird genau dieselbe Zielhandlung mit demselben Rahmen in den
   vier anderen Registern gesucht.
4. Die Stufen sind transparent:
   - A: mindestens zwei Nicht-T/R-Köpfe im Zielregister;
   - B: genau ein Nicht-T/R-Kopf;
   - C: nur die beobachtete T/R-Gegenaktion;
   - D: keine lokale Ganzrahmenstütze, aber dieselbe Zielhandlung in einem
     anderen Register.
5. Innerhalb einer Stufe folgen mehr Nicht-T/R-Köpfe, mehr Eventträger,
   vorhandene Gegenaktion, mehr Zielhandlungsregister und schließlich eine
   feste lexikalische Ordnung. Es gibt keinen vermischten Gesamtscore.

## Decision rule and claim ceiling

Alle 73 Karten behalten `COMPOSED_WORKING`, ihre alte Phrase,
Komponentenspur und Zustandswarnung. Das Ranking sagt weder Vorkommen noch
Voynich-Oberfläche voraus und fügt keine Bedeutung oder Formulierung hinzu.
