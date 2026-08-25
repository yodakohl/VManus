# Pass1023 — OWNER_OR_NEXT_CARD_ACTION

## Ergebnis

Alle **146/146** offenen Pass1022-Fälle sind einzeln gebunden:

- **127 BOUNDED_FORWARD**
- **19 OWNER_ONLY**
- **0 UNRESOLVED**

Die Auflösung benutzt ausschließlich die drei Pass1022-Primärtabellen: Ambiguitäten, Fokus-Anhänge und Event-Scope-Bindungen. Es wurde keine neue Seite und kein neuer Wortwert eingeführt. Die bereits dokumentierte Besitzer-/Locus-Geometrie ersetzt hier eine erneute Bildauslegung.

## Was die Geometrie tatsächlich entscheidet

Alle 146 Alternativen zeigen auf den **unmittelbar nächsten Karteneintrag**. Der erste dortige Handlungskopf steht 115-mal an Atom 1, 30-mal an Atom 2 und einmal an Atom 3. Kein Fall überspringt eine weitere Karte.

Zwischen Ausgang und Ziel gibt es in diesen 146 Fällen:

- 0 Wechsel des dokumentierten Besitzers;
- 0 Wechsel des Pass1022-Proseblocks bzw. Statements;
- 22 Locus-/Zeilenwechsel, aber jeweils innerhalb desselben dokumentierten Besitzers;
- 0 aktuelles `DY` und 0 aktuelles `OS`, die den Weg sperren würden.

Damit ist ein Locuswechsel allein kein Reset. Zugleich enthält diese besondere Ambiguitätsklasse kein positives Beispiel für einen echten Besitzergrenz-Reset: solche Kandidaten wurden bereits durch die Pass1022-Statementgrenzen ausgeschlossen.

## Entscheidungsregeln

Die 127 Vorwärtsbindungen zerfallen ohne Nachjustierung in:

- 45 Fokusfälle unter `OT`: unmittelbarer Geschwisterkopf;
- 4 Fokusfälle unter `Q`: Kopf des geöffneten lokalen Pakets;
- 23 Fokusfälle unter einem `L`-/`AIR`-Rechtsrahmen;
- 1 freier Gradfall zum nächsten kompatiblen Kopf;
- 52 kopflose Anfangsargumente zum unmittelbar nächsten Kopf;
- 2 kopflose Anfangsargumente zum unmittelbar nächsten `Q`-Paket.

Auf Kartenebene entsprechen die ersten beiden Gruppen 31 `OT`-Karten und 3 `Q`-Karten. Auf der Zielkarte stehen dreimal `Q`, einmal `OT` und 22-mal `DY`. In allen 22 `DY`-Fällen steht der Zielkopf vor dem Abschluss: erst wird gebunden, dann schließt `DY` das Paket.

Die 19 Besitzerbindungen sind genau die `AR`-/`AL`-Fälle ohne lokalen oder geerbten Kopf und ohne `Q`, `OT`, `L` oder `AIR` als Rechtslizenz. Das folgt der Pass1022-Regel „AR/AL links bevorzugt; ohne Kopf Besitzer“:

`SAA0010, SAA0072, SAA0099, SAA0109, SAA0117, SAA0118, SAA0129, SAA0140, SAA0173, SAA0184, SAA0221, SAA0224, SAA0231, SAA0245, SAA0255, SAA0279, SAA0313, SAA0314, SAA0317`.

## Harte Gegenbeispiele gegen zu einfache Bindung

1. **Nicht die ganze Karte nach rechts ziehen.** In `P1009-S019` / `darod` bleibt `AR` (`SAA0010`) beim Pflanzenbesitzer, während `OR` derselben Karte (`SAA0011`) an den nächsten `K`-Kopf bindet. Dasselbe Muster wiederholt `P1009-S061` / `aloy`: `AL` bleibt beim Besitzer (`SAA0072`), `Y` geht zum nächsten `OK` (`SAA0073`). Package-Nesting ist daher besser als Whole-card-Attachment.

2. **Unmittelbare Nachbarschaft allein genügt nicht.** `dar` in `P1009-S155` (`SAA0117`) und `dal` in `P1009-S157` (`SAA0118`) bleiben trotz direkt folgender Handlung beim Besitzer. Ohne Rechtslizenz gewinnt die AR/AL-Seitenregel.

3. **Ein expliziter Rahmen kann dieselben Kerne umschalten.** `qotar` in `P1009-S128` bindet `AR` wegen `OT` an das folgende `SH` (`SAA0107`). `lar` in `P1009-S475` bindet `AR` wegen `L` an das folgende `OK` (`SAA0248`). Das widerspricht einer pauschalen Regel „AR immer Besitzer“.

4. **Der längste zulässige Fall bleibt lokal.** In `P1009-S525` führt `L` aus `lo` über genau eine Karte zum `CH` an Atom 3 der nächsten Karte (`SAA0275`); ein dortiges `Q` bleibt Teil desselben lokalen Pakets. Mehr als eine Karte wird nirgends übersprungen.

5. **Zeilen-/Locusknick ist keine Grenze.** `SAA0119` läuft auf f75r von Locus `.41` nach `.42`; `SAA0306/0307` laufen auf f88v von `.15` nach `.16`. Der dokumentierte Besitzer bleibt jeweils identisch, daher bleibt die Vorwärtsbindung offen.

## Konsequenz für die Arbeitsgrammatik

Die einfache Regel wird präzisiert zu:

> Innerhalb eines kopflosen Pakets darf bis zum ersten Kopf der unmittelbar nächsten Karte rechts gebunden werden, solange Besitzer und Proseblock gleich bleiben und kein aktuelles `DY`/`OS` schließt. `Q`, `OT`, `L` und `AIR` lizenzieren den rechten Scope ausdrücklich. `AR`/`AL` bleiben ohne eine solche Lizenz beim Besitzer. Ein `DY` nach dem Zielkopf schließt erst nach dessen Argumentaufnahme.

Das ist keine neue Übersetzung, sondern nur eine Besitzer-/Argumentbindung der vorhandenen Pass1022-Karten. Die vollständige Fallliste mit Anlass, Abstand, Ziel und Begründung steht in `OWNER_NEXT_146_RESOLUTIONS.tsv`; die mechanischen Vollständigkeitschecks stehen in `OWNER_NEXT_VALIDATION.json`.
