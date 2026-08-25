# Pass 1022 — Aus Wurzeln werden Klammern

## Was sich verbessert hat

Wir hatten nach Pass 1021 ein kleines Wörterbuch, aber noch kein zuverlässiges
Verfahren für Folgen wie:

```text
WERT — ANTEIL — EINHEIT — GRAD — ZIELORT
```

Jetzt hat jede der 3.888 laufenden Karten einen Besitzer-, Paket- und
Handlungsrahmen. Der ausführbare Durchgang umfasst 10.252 Komponenten in 627
Aussagen. Kein Bestandteil bleibt ungebunden; die 19 Kernwerte, acht
Steuerwerte und vier örtlichen Kanäle bleiben unverändert.

Das ist ein echter Fortschritt gegenüber den alten Satzglossen. `ody` muss zum
Beispiel nicht mehr als das geratene Wort *kühlen* gespeichert werden:

```text
O + DY = aktive örtliche Handlung AUSFÜHREN + Gang SCHLIESSEN
```

Was diese örtliche Handlung konkret ist, liefert der Besitzer oder das
Meisterexemplar.

## Die ausgewählte Werkstattmechanik

```text
BESITZER
  └─ GANG
      └─ ÄUSSERES KARTENPAKET
          └─ INNERER HANDLUNGSKOPF
              ├─ POSTEN / WERT / ANTEIL / EINHEIT
              ├─ AUSGANG / VERBINDUNG / LAUF / ZIELORT
              └─ GRAD / STUFE
```

Eine Mehrkopfkarte ist nicht flach. `CH+K+Y` wird
`NEHMEN[GEBEN[AKTIVER POSTEN]]`; nach Kartenende bleibt `NEHMEN` als äußerer
Kopf offen. `Q` eröffnet ein Paket, `OT` wechselt zum Geschwisterpaket, `OL`
führt fort, `VORBEZUG` stellt einen älteren Besitzerrahmen wieder her, und nur
ein lizenziertes `DY` oder eine wirkliche Besitzer-/Proseblockgrenze schließt.

Ein Zeilenende, ein radialer Zeilenknick oder Text, der um ein vorher
gezeichnetes Bild fließt, schließt nichts von selbst.

## Vollständige Anwendung

Der Compiler schreibt für jede Karte aus:

- ihre Handlungsköpfe;
- den beim Eintritt offenen Kopf;
- die gebundenen Argumente, Beziehungen und Grade;
- den Besitzerkanal;
- den Kopf, der nach der Karte offen bleibt;
- Beginn, Schluss und die Pass-1021-Doppelregel.

Ergebnis:

| Kartenklasse | Karten |
|---|---:|
| vollständig in der eigenen Karte gebunden | 2.322 |
| benutzt einen laufenden, vorgebundenen oder Meisterkopf | 1.566 |
| **gesamt** | **3.888** |

Die 627 Aussagen erhalten alle eine vollständige Scope-Zeile. 27 beginnen mit
einer ausdrücklich geerbten Handlung. 183 Aussagen benutzen wenigstens eine
begrenzte Vorwärtsbindung, weil Wert, Steuerung oder Beziehung vor dem ersten
sichtbaren Kopf stehen. 21 Aussagen brauchen für einzelne kopflose Zusätze
den im Meisterexemplar gespeicherten Handlungskopf.

## Vollinventar der besonders wichtigen Zusätze

Der unabhängige Fokusdurchgang zählt 4.345 Vorkommen von
`Y/AIIN/AIN/OR/E/EE/EEE/AL/AR/AIR/L`:

| Anschluss | Vorkommen |
|---|---:|
| Handlung links in derselben Karte | 2.828 |
| Handlung rechts in derselben Karte | 272 |
| Handlung der unmittelbar vorigen Karte | 643 |
| ältere offene Handlung derselben Aussage | 353 |
| zunächst nur sichtbarer Besitzer | 249 |

Die ausführbare Ausgabe darf in einem Besitzersegment kurz vorausgreifen und
bindet deshalb auch die 249 kopflosen Anfangsstellen. Sie versteckt aber die
Alternative nicht: 328 Fokusstellen behalten eine zweite mögliche Klammerung.

- 120 liegen gleich weit zwischen zwei Köpfen;
- 146 können zunächst am Besitzer oder am Kopf der nächsten Karte hängen;
- 63 hängen davon ab, ob `R` örtlich Kopf oder Schwanz ist;
- eine Stelle gehört zu zwei dieser Gruppen, daher 329 Alternativzeilen.

Das sind **keine fehlenden Wortbedeutungen**. Es sind lokale Fragen darüber,
welche Handlung den bereits gelesenen Kern regiert.

## Der harte Bildcheck

Zwölf schwierige Aussagen wurden einzeln auf f75r, f67r2 und f88r gegen die
Originalbilder gelesen, insgesamt 306 Karten.

Nur f88r S591 kommt mit einer flachen Defaultregel aus. Elf Aussagen verlangen
mindestens eine der nun eingebauten Ergänzungen: kurzer Vorgriff, sichtbarer
Besitzerrahmen oder verschachteltes Kartenpaket. Keine verlangt ein neues
Wort.

Besonders wichtig:

- f75r ist Text um einen vorgezeichneten Stationsblock; die Textlücken sind
  keine Ganggrenzen.
- f67r2 besitzt getrennte Räder; Rad-/Sektor- und Legendenbesitzer dürfen
  nicht vermischt werden, radiale Zeilen sind aber nicht automatisch Ende.
- f88r hat getrennte Drogen-/Gefäß- und Proseblöcke. Diese Bildreihen setzen
  den Besitzer wirklich zurück; ein `DY` kann sogar mitten in einer
  physischen Zeile schließen.

## Was wir jetzt auf einer neuen Seite vorhersagen würden

Ohne eine Bedeutung umzudeuten, muss eine neue Seite so lesbar sein:

1. Besitzer aus Bild oder lokalem Textblock setzen.
2. Karten mit der bestehenden 19+8+4-Tafel öffnen.
3. Mehrkopfkarte verschachteln; äußersten Kopf nach der Karte offenhalten.
4. Argumente und Grade zuerst in der Karte, dann am offenen Kopf, zuletzt kurz
   vorwärts im selben Besitzersegment binden.
5. `Q/OT/OL/VORBEZUG/DY` als Paketoperationen ausführen.
6. Nur örtliche Namen und sichtbare Referenten dürfen aus dem Exemplar kommen.

Wenn dafür auf einer späteren Seite `AIIN`, `AIN`, `OR`, `E/EE/EEE` oder eine
Beziehung einen neuen tragbaren Sinn braucht, ist die aktuelle Fassung falsch.
Lokale Bildfüllung ist erlaubt; Wurzelverschiebung nicht.

## Dateien

- `PASS1022_CURRENT_SCOPE_SHEET.md` — die kompakte Lehrlingsseite
- `PASS1022_EIGHT_SCOPE_RULES.tsv` — acht ausführbare Regeln
- `PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv` — jede laufende Karte
- `PASS1022_627_STATEMENT_SCOPE_EDITION.tsv` — jede Aussage
- `SCOPE_STACK_ATTACHMENTS.tsv` — 4.345 Fokusanschlüsse
- `SCOPE_STACK_AMBIGUITIES.tsv` — 329 offene Alternativzeilen
- `MANUAL_SCOPE_12_STATEMENT_AUDIT.tsv` — zwölf harte Bildlesungen
- `HISTORICAL_SCOPE_WORKSHOP_RULES.md` — zeitnahe Werkstattanalogie
- `build_pass1022.py`, `validate_pass1022.py` — Neubau und Prüfung

## Nächster Engpass

Die Wortwerte sind diesmal nicht das Problem. Der nächste sinnvolle Pass muss
die 328 offenen Anschlüsse auf den vorhandenen Seiten in drei kleinen Gruppen
angreifen: Gleichabstand, Besitzer-gegen-Nächstkopf und `R` als Kopf oder
Schwanz. Erst danach bringt eine neue Seite maximalen Erkenntnisgewinn.
