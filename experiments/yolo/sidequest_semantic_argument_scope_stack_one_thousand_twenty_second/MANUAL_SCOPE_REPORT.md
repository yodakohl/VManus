# Pass 1022 — manueller harter Scope-Check

## Frage

Zwölf lange oder mehrfach referierende Aussagen wurden auf den bereits
freigegebenen Seiten f75r, f67r2 und f88r von Hand gegen diese einfache Regel
gelesen:

1. innerhalb einer Karte nach rechts binden;
2. über Karten hinweg den letzten aktiven Handlungskopf erben;
3. an einer sichtbaren Grenze zurücksetzen.

Es wurden keine neuen Seiten und keine neuen Wörter benutzt. Die Bildprüfung
verwendete die bereits gespeicherten Originale:

- f75r, 2852×3759, SHA256
  `6fd33917722a97ef0c93f905885963332645c1a1c81f60f03a165b12007a7fc3`;
- f67r2, 1600×1203, SHA256
  `099ded767a3f8a3472e675dcaa2b609ab2d6842d62813a94159fc1dc20f023f3`;
- f88r, 2714×3735, SHA256
  `a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013`.

## Kurzer Befund

Die Regel ist ein guter **Default**, aber kein vollständiger Scope-Mechanismus.
Sie funktioniert bei einfachen Karten wie `OK+AIN`, `S+AIIN`, `SH+E+Y` und
bei einem unmittelbar nachfolgenden nackten `WERT`, `ANTEIL` oder `EINHEIT`.
Sie scheitert an vier klar sichtbaren Situationen:

- Ein Statement oder lokaler Abschnitt beginnt mit Steuerung oder Argumenten,
  bevor ein Handlungskopf erscheint. Dann ist kurze Vorwärtsbindung nötig.
- `CARRIER_Q`, `OT` und `VORBEZUG` dürfen nicht als gewöhnliche Argumente des
  letzten Kopfes gelesen werden. Sie öffnen, wechseln oder restaurieren einen
  lokalen Rahmen.
- Mehrköpfige Karten wie `CH+K+Y`, `SH+EE+K+Y` oder `OR+CH+OR` brauchen
  Paketverschachtelung; ein einziges globales „letzter Kopf“-Register verliert
  den äußeren Kopf.
- Der Bildbesitzer begrenzt den Rahmen. Ein bloßer Zeilenbruch oder eine durch
  das vorher gezeichnete Bild erzwungene Textlücke ist dagegen **kein** Reset.

Von den zwölf Aussagen ist nur f88r S591 unmittelbar mit der einfachen Regel
lesbar, sofern „rechts binden“ ausdrücklich als verschachteltes Paket und
nicht als flache Kette verstanden wird. Elf Aussagen benötigen mindestens
eine begrenzte Ergänzung durch nächste passende Bindung, Besitzerrahmen oder
Paketstapel. Keine benötigt einen neuen Kernwert.

## Was auf den drei Bildern als Grenze zählt

### f75r

Der Text läuft in schmalen Fragmenten um die große grüne Figuren- und
Stationszeichnung. Diese Lücken entstanden aus der Bildbelegung und trennen
nicht automatisch einen Arbeitsgang. S075, S100, S109 und S120 dürfen deshalb
über gewöhnliche physische Zeilen weiterlaufen. `DY` schließt sie wirklich.
Der äußere Besitzer ist der aktuelle Text-/Stationsblock; einzelne Figuren
oder grüne Inseln dürfen ohne Zeiger nicht als neue Besitzer erzwungen werden.

### f67r2

Die Seite zeigt zwei voneinander getrennte Räder ohne sichtbaren Verbinder.
Innerhalb eines Rades bilden Sektor, Ring und lokale Textgruppe den
Besitzerrahmen. Ein radialer Zeilenwechsel ist nicht automatisch ein Reset.
Der Wechsel von den Sektortexten zur unteren gemeinsamen Legendenzeile vor
S041 ist dagegen ein wirklicher Besitzerwechsel. Keine Scope-Regel darf daraus
Richtung oder Rotation ergänzen.

### f88r

Mehrere deutlich getrennte Drogen-/Wurzelreihen, drei Gefäßgruppen und die
dazwischenliegenden Proseblöcke bilden lokale Besitzerpakete. S590 gehört zum
oberen Proseblock, S591/S592 zum mittleren und S594 zum unteren. Die Bildreihe
zwischen den Blöcken setzt den Rahmen zurück. Innerhalb der Prosezeilen gilt
kein Zeilenreset; S591 zeigt sogar einen `DY`-Schluss mitten in f88r.18, bevor
S592 auf derselben physischen Zeile neu beginnt.

## Die zwölf harten Stellen

Die vollständigen Kartenstellen und Reparaturen stehen in
`MANUAL_SCOPE_12_STATEMENT_AUDIT.tsv`. Die wichtigsten Eingriffe sind:

### f75r

- **S075:** Karten 7, 11 und 13 sind verschachtelte Pakete. In
  `SH+EE+K+Y` bindet Grad II zunächst an `SH`; `K+Y` bleibt der innere Gang.
  In `DA+CH+K+Y` umfasst die zweite Stufe `CH[K[Y]]`. Die nackten
  Zeilenwechsel .2→.3→.4 resetten nicht; Karte 20 `OK+EE+DY` tut es.
- **S100:** Karte 4 `OT+AR` darf nicht rückwärts an das `OK` von Karte 3
  geklebt werden. Sie wechselt in einen neuen lokalen Beziehungsrahmen, zu dem
  Karte 5 `AL+Y` gehört. Karte 8 ist ein verschachtelter
  `OL[K[Grad II, OL[Y]]]`-Gang.
- **S109:** Karte 1 `OL` hat innerhalb der Aussage noch keinen Handlungskopf;
  sie setzt den äußeren Stationsgang fort. Karten 10–14 bilden eine
  Einheit-/Verbindungsgruppe und dürfen nicht sämtlich das `SH` von Karte 9
  erben. Die Pakete 19, 21, 40, 45 und 49 müssen gepusht und nach Kartenende
  wieder geschlossen werden. Die sieben um das Bild gebrochenen Zeilen sind
  kein siebenfacher Reset; Karte 50 mit `DY` ist der Schluss.
- **S120:** Nach Karte 1 folgt `OT+KLASSE | O | ANTEIL`. Das nackte `ANTEIL`
  an Karte 4 darf nicht unbeschränkt zum alten `CHD` zurückspringen; es bleibt
  im neuen Klassenrahmen und bindet an den nächsten passenden lokalen Gang.
  Karten 5 und 8 sind `CH[K[Grad, Y]]`-Pakete.

### f67r2

- **S032:** Karte 1 besteht nur aus Ausführung, zweiter Stufe, Grad I und
  Stufe. Nach dem `DY`-Schluss von S031 existiert kein letzter Kopf, den sie
  erben könnte; diese Steuerung muss kurz vorwärts an Karten 2–3 gebunden
  werden. Karten 11 und 15 sind mehrköpfige lokale Pakete. Die sechs radialen
  Textloci bleiben innerhalb desselben Radbesitzers.
- **S038:** Die zwei `WERT`-Karten 14–15 können am unmittelbar vorangehenden
  Paket hängen. Karte 16 `VORBEZUG` ist aber kein drittes Argument: Sie
  restauriert den Besitzerrahmen. Karte 17 `BEGINNMARKER+WÄHLEN+VARIANTE`
  pusht danach einen neuen Unterrahmen. Karten 9–13 benötigen ebenfalls
  Paketverschachtelung.
- **S040:** Karte 4 `VORBEZUG` restauriert einen Rahmen und erbt nicht einfach
  `EINSTELLEN` von Karte 1. Karte 9 besitzt nach dem physischen Zeilenwechsel
  keinen eigenen Handlungskopf; ob sie an `S+AL` von Karte 8 hängt, bestimmt
  der gemeinsame Sektor-/Eintragsbesitzer, nicht das Zeilenende allein.
- **S041:** Die Kopfkarten 1–3 nennen Ausgang, Zielwert und aktiven Wert,
  bevor mit Karte 4 der erste `BEGINNMARKER` und Handlungskopf erscheint.
  Rückwärtsvererbung ist hier unmöglich. Die `BEGINNMARKER` in Karten 4, 6,
  16 und 28 eröffnen lokale Pakete; die Schlussgruppe 34–36
  `AUSGANG | LAUF | HIER+Y` bleibt eine offene Beziehungs-/Besitzertail und
  wird nicht pauschal zum letzten `OK` geschlagen.

### f88r

- **S590:** Nackte Werte nach Karten 14 und 17 binden gut an das jeweils
  nächste `OK` beziehungsweise `S`. Dagegen braucht Karte 8
  `CH+CH+T+OL` die äußere/innere Paketregel. `OT+HIER` an Karte 24 wechselt
  den lokalen Postenrahmen; `Q` an Karte 43 eröffnet einen neuen. Die vielen
  `HIER`-Karten werden durch den jeweiligen Drogen-/Gefäßbesitzer, nicht durch
  einen seitenweit letzten Handlungskopf konkret.
- **S591:** Dies ist der klare Positivfall. Jede der sechs Karten enthält einen
  eigenen Kopf oder Fortsetzungsoperator. `OR+CH+OR` an Karte 3 wird als
  äußere `EINHEIT` mit innerem `CH[OR]` gelesen. Karte 6 schließt mit `DY`;
  erst danach beginnt S592 auf derselben physischen Zeile.
- **S592:** Die drei `CARRIER_Q`-Karten 5–7 sind drei lokale Beginnrahmen,
  nicht eine fortlaufende Vererbung des ersten `K`. Karte 1 verlangt
  paarweise nächste Bindung von zwei `S+AL`-Gruppen. Karte 28 `Y+Y` ist die
  bereits festgelegte freie Mehrzahl zweier Posten und darf nicht als ein
  einziges doppeltes Argument des `SH` von Karte 27 kollabieren.
- **S594:** Die Fortsetzungsserie 1–5 und `OR | AIIN` nach `SH+EE+Y` sind mit
  der Defaultregel gut lesbar. Die doppelten Ausgänge 17–18 sowie die lokalen
  Ziel-/Ausgangskarten 35–36 gehören jedoch zum unteren Gefäß-/Drogenrahmen.
  Karte 40 `CARRIER_Q+...` pusht einen neuen Unterrahmen. Weil S594 am
  Seitenende offen bleibt, darf dort kein künstlicher Schlussreset entstehen.

## Kleinste tragfähige Reparatur

Die drei Defaultregeln bleiben erhalten, bekommen aber einen kleinen Stapel:

1. **Besitzerrahmen setzen.** Klare Rad-, Sektor-, Drogenreihen-, Gefäß- oder
   Textblockgrenzen setzen zurück. Bildbedingte Zeilenlücken tun es nicht.
2. **Nächsten passenden Kopf nehmen.** Innerhalb einer Karte und eines lokalen
   Segments binden Grad, Wert, Anteil, Einheit, Ort und Posten an den nächsten
   kompatiblen Handlungskopf. Fehlt links ein Kopf, ist kurze Vorwärtsbindung
   bis zum nächsten Kopf erlaubt.
3. **Paket pushen.** Mehrköpfige Karten behalten äußeren und inneren Kopf.
   Das innere Paket endet mit der Karte; der äußere Rahmen bleibt verfügbar.
4. **Steuerung behandeln.** `CARRIER_Q` pusht einen Beginnrahmen, `OT` wechselt
   in den nächsten Geschwistergang, `VORBEZUG` restauriert den vorherigen
   Besitzerrahmen und `OL` setzt den obersten offenen Gang fort.
5. **Wirklich schließen.** `DY` schließt den aktuellen Gang. Eine eindeutige
   Besitzer-/Proseblockgrenze leert den lokalen Stapel; ein offenes Seitenende
   wie S041 oder S594 tut das nicht automatisch.

Das Ergebnis ist keine neue Grammatik und kein neues Wörterbuch. Es ist nur
die kleinste Scope-Ergänzung, die die zwölf manuellen Gegenbeispiele lesbar
hält: **nearest attachment innerhalb des Besitzerrahmens, ein kleiner
Paketstapel und echte statt bloß typographische Grenzen.**
