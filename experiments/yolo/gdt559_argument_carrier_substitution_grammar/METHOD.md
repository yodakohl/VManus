# GDT559 method

## Question

Besetzen `Y=POSTEN`, `AIIN=WERT`, `AIN=ANTEIL` und `OR=EINHEIT` innerhalb der
sichtbaren `OT/OL/DY`-Steuerung denselben Argument-Trägerslot? Lassen sich alle
Vorkommen und alle geschriebenen Steuerfolgen lesen, ohne einem Ganzwort eine
neue Bedeutung zu geben? Ist insbesondere `Y` ein eigenständiges Argument und
nicht ein Teil des Schlussoperators `DY`?

## Inputs

- `GDT557` —1,870 Zustandsmarkerzeilen/1,656 eindeutige Zustandskarten aus30
  bereits zugelassenen Seiten;
- `GDT416` —4,576 alte Kontextkarten mit sichtbarem und geerbtem Argument;
- `GDT539` —546 Kontextkarten der bereits zugelassenen vier aktuellen Seiten;
- `GDT429` —dreizehn Nicht-Handlungs-Kontraste, darunter alle sechs Paare der
  vier Argumentwerte.

## Method

1. Zustandsmarkerzeilen werden auf die1,656 eindeutigen Karten reduziert.
2. Jede exakte Vorkommensstelle von `Y/AIIN/AIN/OR` erhält den nächsten
   `OT/OL/DY`-Kontrollrand links und rechts. Das ergibt eine sichtbare Hülle,
   keine neue Segmentierung.
3. Jede Hülle erhält eine kurze Atomlesung (`DANACH · ARG`,
   `FORTSETZEN · ARG`, `ARG · ABSCHLIESSEN` usw.). Auch Karten mit zwei
   Argumenten behalten die geschriebene Reihenfolge.
4. Bei Karten mit genau einem Argument wird nur dieser Slot zu `ARG`
   normalisiert. Ein Austauschrahmen zählt, wenn mindestens zwei der vier
   vorhandenen Werte im sonst bytegleichen Rezept vorkommen.
5. Die sechs Argumentpaare werden mit den älteren GDT429-Kontrasten
   gekreuzt. Die Werte bleiben verschieden, auch wenn sie denselben
   Steuerrahmen besetzen.
6. Für jede Karte, deren letztes Argument rechts von OT oder OL steht, wird die
   unmittelbar nächste Karte derselben Aussage gelesen: ein sichtbares neues
   Argument ersetzt den Träger; sonst muss der vorhandene Kontext genau den
   aktuellen Wert übernehmen.
7. `Y` und `DY` werden als exakte Atome gezählt. Gemeinsame Karten werden in
   ihrer geschriebenen Reihenfolge ausgegeben.
8. Der Runner publiziert alle390 Stellen, alle24 Steuerprojektionen und die
   vollständigen Familien- und Nachfolgertabellen. Der Validator baut alle
   Artefakte erneut und vergleicht ihre Hashes.

## Decision rule and claim ceiling

Der Pass gilt als brauchbare nächste Werkstattstufe, wenn alle Argumentstellen
eine der beobachteten Hüllen und eine Standardlesung erhalten, beide nackten
Rahmen `OT+ARG` und `OL+ARG` alle vier Werte tragen, alle impliziten
Nachfolger den aktuellen Wert übernehmen und gemeinsame `Y`/`DY`-Karten
kompositionell lesbar bleiben.

Das Ergebnis darf die vorhandenen vier kurzen Arbeitswerte innerhalb der
sichtbaren Zustandsgrammatik präzisieren. Es ändert keine Wurzel, Oberfläche,
Segmentierung, Rezeptfolge, Aussagegrenze oder Seite und bestätigt weder
Klartext noch historische Sprache oder Codebuchidentität.
