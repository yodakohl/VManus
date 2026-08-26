# GDT427 — Die Klassen lernen endlich „nein“ zu sagen

## Die notwendige Korrektur

GDT426 war als Kompression nützlich, aber als Vorhersagemodell zu großzügig:
seine vier Klassen belegten **16/16** mögliche Übergänge. Damit wurde jedes
noch nie gesehene Aktionspaar automatisch gelb. Das war keine echte
Vorhersagegrenze.

Unter sieben kleinen Reparaturen funktioniert die Trennung der bisherigen
CONTROL-Familie am besten:

- **SELECT:** `CH=NEHMEN`, `S=WÄHLEN`;
- **MOVE_SET:** `K=GEBEN`, `OK=SETZEN`, `P=EINSETZEN`;
- **HOLD_PROCESS:** `SH=HALTEN`, `CHD=BEARBEITEN`;
- **SET_CONTROL:** `T=EINSTELLEN`;
- **MARK_CONTROL:** `R=MARKIEREN`.

Jetzt sind nur noch **22/25** Klassenübergänge belegt. Leer bleiben
MOVE_SET→T, R→MOVE_SET und R→R. Das Gate kann also erstmals bestimmte Formen
vor ihrem Auftauchen rot markieren.

## Positiv- und Negativprobe

Von den fünfzehn exakten Aktionspaaren, die nur auf einer Seite vorkommen,
werden beim Verbergen dieser Seite **12** über einen anderswo belegten
Klassenübergang erwartet; drei bleiben lokal: `R>T`, `SH>R` und `T>T`.

Von siebzehn exakten Paaren, die im ganzen Bestand nie vorkommen, blockiert das
Gate **7** korrekt und lässt noch **10** fälschlich zu. Die balancierte
Trefferquote steigt damit von **0,500000** beim alten Vierklassenmodell auf
**0,605882**. Das ist keine Entzifferung, aber ein echter Unterschied zwischen
„erlaubt“ und „nicht erlaubt“.

## Die neun lokalen Karten nach der Reparatur

Sieben bleiben gelb:

- `CH>OK`, `CHD>S`, `K>OK` über alte Klassenübergänge;
- `OK>S` und `SH>T` sogar als exakte Paare auf anderen Seiten;
- `R<-AIR` und `S<-EEE` als vollständige Kopf×Fokus-Rechtecke.

Zwei bleiben rot-lokal:

- `R>T` auf f83r: kein anderes Blatt trägt R→T;
- `R<-EE` auf f82r: EE steht an vielen Köpfen, aber R nimmt außerhalb dieses
  Blattes weder EE noch einen anderen Gradwert.

Das ist der wichtigste Gewinn dieser Runde: Wir retten nicht mehr jede
Ausnahme durch eine immer gröbere Kategorie.

## Was diese Runde über Bedeutungen sagt

Die Trennung `T=EINSTELLEN` versus `R=MARKIEREN` ist strukturell nützlicher als
ihre frühere Zusammenlegung. Die übrigen drei Sammelklassen bleiben vorläufig
sinnvoll, aber ihre Mitglieder dürfen semantisch nicht verschmolzen werden:
NEHMEN ist nicht WÄHLEN, GEBEN nicht SETZEN, HALTEN nicht BEARBEITEN. Der
nächste Pass muss genau diese inneren Kontraste anhand ihrer Argumente,
Nachbarn und Besitzer prüfen.

## Grenze

Das Modell ist auf denselben bereits freigegebenen Seiten aufgebaut. Es führt
keine neue Wurzel, keine Wörterbuchrevision und keine neue Seite ein. Die
Klassen sind Werkstatt-Hilfen für Vorhersagen, keine bestätigten Wortarten oder
Klartextbedeutungen.
