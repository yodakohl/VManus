# Pass 1020 — f13r mit dem Einseitenblatt gelesen

## Das erlaubte Blatt

Der Rundlauf benutzt ausschließlich dieses Inventar.

```text
19 KERNE
OK SETZEN      CH NEHMEN       SH HALTEN       K GEBEN
S  WÄHLEN      T  EINSTELLEN   CHD UMSETZEN    P EINSETZEN
AIIN WERT      AIN ANTEIL      OR EINHEIT      R MARKIEREN
Y AKTIVER POSTEN  OL FORTSETZEN  OT DANACH
AL ZIELORT        AR AUSGANG      L VERBINDUNG   AIR LAUF

8 KONTROLLEN
E / EE / EEE = GRAD I / II / III
DY = SCHLUSS   O = AUSFÜHRUNG   Q = BEGINNMARKER
IIN = STUFE    DA = ZWEITE STUFE

4 LOKALE KANÄLE
HIER | VARIANTE | KLASSE | VORBEZUG

10 ERLAUBTE RESEGMENTIERUNGEN
CTH=CH+T   CKH=CH+K   CHEO=CH+E+O   CHK=CH+K   CPH=CH+P
SHED=SH+E  SOLK=OL+K  LSH=L+SH      CFH=CH+HIER  LD=L+HIER
```

Die beiden eingeschobenen Formen, die f13r tatsächlich braucht, sind
`CKH=NEHMEN+GEBEN` und `CFH=NEHMEN+HIER`. Sie erhalten keine zusätzliche
portable Bedeutung.

## Seiteneinsatz

f13r umfasst im laufenden Text `P1009-S005` bis `P1009-S009`, zehn physische
Loci und 77 sichtbare Karten. Alle 77 Karten lassen sich durch das Blatt
routen. Auf dieser Seite werden tatsächlich gebraucht:

- 14 Kerne: `OK CH SH K S T P AIIN OR Y OL OT AL AR`;
- fünf Kontrollen: `E EEE DY O IIN`;
- drei lokale Kanäle: `HIER`, `VARIANTE`, `KLASSE`;
- zwei Resegmentierungen: `CKH`, `CFH`.

`CHD`, `AIN`, `R`, `L`, `AIR`, `EE`, `Q`, `DA`, `VORBEZUG` und die übrigen
acht Resegmentierungen werden auf f13r nicht benötigt. Ein sichtbares `q` am
Kartenanfang zählt hier nicht automatisch als `Q`: Wo die vorhandene
Komponentenfolge keinen `BEGINNMARKER` enthält, bleibt es Teil der bereits
gelernten Oberflächenform.

## Vollständige Werkstattlektüre

Die eckigen Bildzusätze kommen aus der Zeichnung und sind keine geheimen
Kernwörter.

### P1009-S005 — f13r.1 bis f13r.5

> Bei der **[BILDLOKAL: großen Wurzelkrone mit Blatt und Blütenstand]** eine
> Einheit einstellen und halten. Den bezeichneten **[BILDLOKAL:
> Pflanzenteil]** einsetzen und fortsetzen, nach dem eingetragenen Wert wählen
> und halten, an den Zielort geben und die örtlich markierte Variante in Grad
> III ausführen. Danach aus der Einheit nehmen, am bezeichneten Platz einsetzen
> und fortsetzen; am Nebenplatz schließen.

Offen bleibt, welcher Bildteil jeweils durch `HIER` und `VARIANTE` gewählt wird
und welche konkrete Handlung `AUSFÜHRUNG` bezeichnet.

### P1009-S006 — f13r.6 bis f13r.7

> Die bezeichnete **[BILDLOKAL: Pflanzeneinheit]** nach dem eingetragenen Wert
> einstellen. Danach einen Teil nehmen und fortsetzen, den aktiven Posten sowie
> eine neue Einheit setzen, auf der Stufe ausführen, nehmen und geben, am
> bezeichneten Platz fortsetzen; schließen.

Offen bleiben der Inhalt von `WERT` und `STUFE` sowie die Grenze zwischen
ganzer Artikel- und Pflanzenteileinheit.

### P1009-S007 — f13r.7 bis f13r.9

> Eine Einheit nehmen und setzen; am bezeichneten Platz den Wert ausführen.
> Einen Posten der **[BILDLOKAL: sichtbaren Organ- oder Stoffklasse]** setzen,
> die Einheit einstellen, geben und wählen; den Posten nach dem Wert setzen und
> schließen.

`KLASSE` ist lesbar, nennt aber weder Wurzel, Blatt noch Blüte. Diese Auswahl
müsste aus Exemplarwissen oder einem nicht sichtbaren Zeiger kommen.

### P1009-S008 — f13r.9

> Den **[BILDLOKAL: gewählten Pflanzenteil]** in Grad I halten und fortsetzen.
> Am bezeichneten Platz die Stufe ausführen, den Posten geben und fortsetzen,
> am Zielort setzen und nehmen; den Zielgang schließen.

Das Blatt liefert keinen konkreten Zielort und keine konkrete Stufe im Bild.

### P1009-S009 — f13r.10

> Danach den nächsten **[BILDLOKAL: sichtbaren Pflanzenteil]** wählen, geben
> und in die laufende Einheit innerhalb des Artikelrahmens setzen; offen
> weiterführen.

Die zwei aufeinanderfolgenden `OR` sind als `EINHEIT+EINHEIT` lesbar. Ob das
wirklich Teil-in-Artikel, Wiederaufnahme oder zwei Arbeitsblöcke bedeutet,
entscheidet das Blatt noch nicht.

## Was der Rundlauf zeigt

Das Einseitenblatt deckt die sichtbare Kartenfolge vollständig ab, aber es ist
noch keine selbstgenügsame Gebrauchsanweisung. Es erklärt zuverlässig:

> Posten wählen/nehmen/setzen/halten/geben → Wert oder Grad anwenden → lokalen
> Platz, Variante oder Klasse übernehmen → fortsetzen oder schließen.

Es erklärt noch nicht:

- welcher konkrete Pflanzenteil der aktive Posten ist;
- welcher Wert eingetragen oder erinnert wird;
- was Grad I und III praktisch verändern;
- welcher Bildplatz Ziel, Ausgang oder lokales `HIER` ist;
- welche konkrete Werkstatthandlung `O=AUSFÜHRUNG` auslöst;
- warum `OR+OR` am offenen Ende doppelt steht.

Die beste Gesamtlektüre von f13r ist daher eine kompakte, wiederholte
Teileverwaltung für einen einzigen Pflanzenartikel. Die Karte ist lernbar;
die konkreten Referenten und Handgriffe bleiben exemplar- oder
werkstattgebunden.
