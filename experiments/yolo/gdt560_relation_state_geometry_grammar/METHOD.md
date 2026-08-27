# GDT560 method

## Question

Bilden `AL=ZIELORT`, `AR=AUSGANG`, `L=VERBINDUNG` und `AIR=BAHN` innerhalb
der sichtbaren `OT/OL/DY`-Steuerung ein einziges austauschbares Relationsfach,
oder zeigen ihre Positionen verschiedene Richtungsfunktionen? Kann jede
Vorkommensstelle kompositionell gelesen werden, einschließlich Relationen vor
Argumenten und der seltenen Reihenfolge `DY+L`?

## Inputs

- `GDT557` —1,870 Zustandsmarkerzeilen/1,656 eindeutige Zustandskarten aus30
  bereits zugelassenen Seiten;
- `GDT429` —dreizehn Nicht-Handlungs-Kontraste, darunter alle sechs Paare der
  vier Relationswerte.

## Method

1. Die GDT557-Zeilen werden auf eindeutige Karten reduziert und alle exakten
   Vorkommen von `AL/AR/L/AIR` ausgewählt.
2. Jede Relationsstelle erhält den nächsten `OT/OL/DY`-Rand links und rechts.
   Die8 beobachteten Hüllen werden in geschriebener Reihenfolge gelesen.
3. Innerhalb derselben Hülle wird festgehalten, ob die Relation am linken oder
   rechten Blockrand steht und ob links oder rechts ein sichtbares Argument
   oder eine Handlung liegt.
4. Jede Karte mit genau einer Relation wird nur an diesem Slot zu `REL`
   normalisiert. Mindestens zwei vorhandene Relationswerte im sonst exakten
   Rezept ergeben eine Austauschfamilie.
5. Alle sechs Relationspaare werden mit GDT429 gekreuzt. Eine fehlende
   state-spezifische AIR-Familie hebt die älteren Gesamtkorpus-Kontraste nicht
   auf; sie verhindert nur, AIR hier als freien Ersatz zu behandeln.
6. Zwei Projektionen werden ausgegeben:28 reine Relation-Steuerfolgen und44
   Folgen, die zusätzlich die vier Argumentwerte sichtbar halten.
7. Alle expliziten Relation-Argument-Kontakte und alle Relationen nach DY
   werden einzeln ausgegeben. Kein Atom wird über eine Kontrollgrenze
   zurücksortiert.
8. Der Validator rekonstruiert die Population, Geometrien, Familien und
   Schlussverteilungen und prüft einen bytegleichen Neubau.

## Decision rule and claim ceiling

Die Arbeitsgrammatik wird übernommen, wenn alle216 Stellen eine Hülle und
Defaultlesung erhalten, die exakten Familien die sichtbaren Root-Unterschiede
bewahren, DY den Schluss unabhängig vom Relationswert kontrolliert und AIR
nicht ohne beobachteten Rahmen in die anderen Slots gezwungen wird.

Das Ergebnis präzisiert nur die vier vorhandenen Arbeitswerte und ihre
Position in bereits bekannten Rezepten. Es ändert keine Wurzel, Oberfläche,
Segmentierung, Aussagegrenze oder Seite und bestätigt weder Klartext noch
historische Sprache, Syntax oder Codebuchidentität.
