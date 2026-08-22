# V62 R4 — Korrektoraudit der stillen Register

Status: unabhängiger kreativer Sidequest-Pass, keine Referenzauflösung und
keine Übersetzung. Keine V62-Geschwister, weiteren Seiten oder
`f84`/`f84r`-Daten wurden gelesen.

## Vier getrennte Merktafeln

```text
O = PICTURE_OWNER
A = ACTIVE_ITEM_OR_PREPARATION
T = TARGET_OR_STATION
P = PREVIOUS_ITEM
```

Die Werte sind ausschließlich anonyme Record-IDs wie `OWNER_H2` oder
`ITEM_B3_04`. Sie heißen nicht Pflanze, Wasser, Bad, Körperteil oder Gefäß.

## Ausführbare Regel

1. Am Recordbeginn O aus Bild/Layout setzen und A als ersten anonymen Posten
   eröffnen.
2. `CONTINUE_SAME_CLAUSE` trägt O, A und gegebenenfalls T weiter.
3. `RESUME_ACTIVE_ITEM` beginnt eine neue Klausel, behält aber A.
4. `NEXT_PARALLEL_CELL`, `START_NEW_CLAUSE` und die ungelöste Grenze speichern
   A nach P, eröffnen ein neues A und löschen T.
5. Nur ein exaktes `ZIEL?` eröffnet einen neuen anonymen T-Slot.
6. Nur ein exaktes `VORIGES?` wählt P aus; was P in der Welt bezeichnet,
   bleibt unbekannt.

Die Regel erzeugt für alle 116 Aussagen einen eindeutigen Vor- und
Nachzustand. Sie macht keine der stillen IDs zu einer Voynich-Kartenbedeutung.

## Was damit tatsächlich erklärt wird

- Derselbe Bildbesitzer kann über den gesamten Record unausgesprochen bleiben.
- Eine neue Klausel kann denselben aktiven Posten übernehmen, ohne ihn erneut
  zu benennen.
- `ZIEL?` signalisiert höchstens, dass ein Zielslot gefüllt werden soll; das
  Ziel selbst kommt aus Bild oder Exemplar.
- `VORIGES?` signalisiert höchstens Rückgriff; der Antezedent kommt aus der
  anonymen Arbeitshistorie.
- f82r.3→.4 trägt denselben A-Zustand über den Zeilenreset. Die doppelte
  Randkarte bleibt eine Schreiberwiederaufnahme, keine fünfte Merktafel.

## Korrektorische Grenze

O und A sind nötig, um die vollständige kreative Edition überhaupt kohärent
zu lesen. T und P sind dagegen nur schwach sichtbar: T wird durch zehn
`ZIEL?`-Ereignisse geöffnet, P durch zwei `VORIGES?`-Ereignisse ausgewählt.
Die konkreten Referenten sind nie intern geankert. Ein einfacheres
Zwei-Register-System O+A kann daher dieselbe **Form** reproduzieren, verliert
aber die Unterscheidung zwischen Zielsetzung und Rückgriff in der
Quellenlesung.

Das Nullmodell bleibt ein reines Exemplarformular: Der Schreiber kopiert jede
Klausel vollständig aus der Vorlage und benötigt keine semantischen Register.
Es ist formal genauso möglich, aber als circa-1420 Lehrpraxis weniger
wirtschaftlich, weil Besitzer und Arbeitsgegenstand bei jedem der 116 Schritte
neu nachgeschlagen werden müssten.

## Ergebnis

Die vier Register sind ein brauchbares **Lesegedächtnis**, keine dechiffrierte
Pronomen- oder Kasusgrammatik. Die vollständige Trace, 105 Carry-Kanten und
44 Record×Register-Inventarzeilen sind maschinell validiert. Keine neue
Kartenbedeutung wurde eingesetzt.
