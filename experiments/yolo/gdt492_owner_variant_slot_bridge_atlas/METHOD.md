# GDT492 — Methode

## Question

Lassen sich die vier GDT491-Owner-Varianten vollständig aus bereits
beobachteten registergebundenen Realisierungen ihrer einzelnen Komponenten
erklären? Welche anderen Handlungsköpfe tragen dieselben exakten Rahmen?

## Inputs

- GDT413: 46-Komponenten-Wörterbuch, insbesondere `E=GRAD I`;
- GDT415: 95 beobachtete Wurzel×Register-Realisierungen;
- GDT416: 4.576 beobachtete owner-lokale Imperativklauseln;
- GDT491: die vier unveränderten `OWNER-VARIANTE`-Kontrastkarten.

## Method

1. Die vier Rahmen werden in ihre sichtbaren Komponentenplätze zerlegt.
   `@ACTION` wird auf der T-Seite als T, auf der R-Seite als R geführt; alle
   übrigen Wurzeln bleiben identisch.
2. Das Register jeder ausgewählten T- und R-Klausel wird aus ihren exakten
   GDT416-Trägern bestimmt. Für T, R, AL, Y, CH und OR wird anschließend die
   alte GDT415-Registerrealisierung eingesetzt. `E` kommt aus GDT413; seine
   tatsächlichen GDT416-Träger werden in jedem Register gezählt.
3. Ein nicht-aktionaler Slot heißt `REGISTER_STABLE_REALIZATION`, wenn beide
   Register denselben Wortlaut besitzen. Andernfalls heißt er
   `OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE`. Der T/R-Platz bleibt der
   beabsichtigte Aktionskontrast.
4. Für jeden Rahmen werden alle neun bekannten Handlungsköpfe eingesetzt und
   nur exakt in GDT416 vorkommende Rezepte behalten. Jede Klausel bleibt
   wortwörtlich erhalten.
5. Ein Rahmen×Handlungs-Rezept in mehreren Registern bildet eine direkte
   Registerbrücke. Verschiedene Handlungen im gleichen Rahmen bilden weitere
   beobachtete Aktionszellen, aber keine synthetischen Sätze.

## Decision rule and claim ceiling

Eine Slotzelle zählt nur, wenn sie alte Ereignisträger besitzt. Eine
Rahmenfamilie zählt nur über exakte Komponentenrezepte. Keine aus einzelnen
Slots zusammengesetzte Phrase wird als beobachtete Klausel ausgegeben.

Das Ergebnis ist ein Owner-Slot-Modell der kreativen Arbeitsübersetzung. Es
bestätigt keine historische Sprache oder Lexeme und ändert keine Bedeutung,
Formulierung, Modellfolge, Grenze, Oberfläche, Rezeptfolge, Event- oder
Seitenzuordnung.
