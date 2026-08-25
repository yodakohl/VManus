# Eintrittsblatt für die nächsten vier Seiten

Dieses Blatt wird vor der neuen Seite benutzt. Seine kurzen Werte werden
während der Erstlesung nicht umbenannt.

## 19 Kerne

```text
Y     AKTIVER POSTEN       OK    SETZEN           OL    FORTSETZEN
OT    DANACH               AL    ZIELORT          CH    NEHMEN
SH    HALTEN               AR    AUSGANG          K     GEBEN
AIIN  WERT                 S     WÄHLEN           CHD   UMSETZEN
OR    EINHEIT              L     VERBINDUNG        T     EINSTELLEN
AIN   ANTEIL               R     MARKIEREN         P     EINSETZEN
AIR   LAUF
```

## Acht Steuerungen und vier lokale Kanäle

```text
E / EE / EEE   GRAD I / II / III
IIN / DA       STUFE / ZWEITE STUFE
O              AUSFÜHRUNG
Q              BEGINNMARKER; Paket pushen
DY             nur in lizenzierter Endkarte: SCHLUSS

HIER           örtlicher Besitzerzeiger
VARIANTE       örtliche Variante
KLASSE         örtliche Klasse
VORBEZUG       älteren Besitzerrahmen restaurieren
```

## Öffnungsfolge

1. Zuerst entscheiden: Lauftext oder lokale Bild-/Ringadresse. Eine Adresse
   wird kopiert und eröffnet keinen Satz, auch wenn sie bekannte Kerne enthält.
2. Sichtbaren Besitzer und echte Besitzer-/Proseblockgrenzen eintragen.
   Zeilenende, radialer Knick und Bildumbruch allein resetten nicht.
3. Längste gelernte Karte, eingebettetes Paket und unmittelbare Doppelung
   öffnen. Paketgebundenes `X+X` steigt eine Ebene ab; freies `X+X` bedeutet
   mehrere X beziehungsweise X nochmals.
4. Mehrere Handlungsköpfe verschachteln. Der äußere Kopf bleibt nach der Karte
   offen, bis ein lizenzierter Schluss oder eine echte Besitzergrenze kommt.
5. Argument oder Grad nimmt den nächsten Handlungskopf; bei gleicher
   Entfernung links.
6. `AL/AR` bindet in dieser Reihenfolge: links → laufender Kopf → einziger
   Kopf derselben Karte rechts → sichtbarer Besitzer.
7. `L/AIR` nimmt den nächsten rechten Kopf; fehlt er, folgt der linke/laufende
   Kopf oder genau eine unmittelbar folgende Karte im selben Besitzersegment.
8. Ein kopfloses Anfangspaket darf höchstens eine Karte bis zum ersten
   kompatiblen Kopf desselben Besitzersegments vorausgreifen.
9. `Q` pusht; `OT` wechselt zum Geschwistergang; `OL` führt fort;
   `VORBEZUG` restauriert; lizenziertes `DY` schließt.
10. `R` mit eigenem Rechtsglied ist Kopf; nach äußerer Handlung ohne eigenes
    Rechtsglied ist es Schwanz; zwischen äußerem Kopf und Rechtsglied ist es
    innerer Kopf.

## Was auf der neuen Seite erlaubt ist

- eine neue sichtbare Kartenoberfläche aus bekannten Atomen;
- eine neue Reihenfolge bekannter Atome, sofern obige Klammerregeln reichen;
- ein neuer Bildbesitzer, lokaler Name, Stern-/Stationswert oder Adresszeichen;
- eine neue gelernte Ganzkarte, wenn sie als `NEW_LOCAL_CARD` isoliert bleibt
  und keinen bekannten Kern umdeutet;
- eine lokale flüssige Erweiterung wie Pflanzenteil, Becken, Sektor oder
  Zubereitung, wenn sie sichtbar vom Besitzer stammt und nicht ins Wörterbuch
  zurückgeschrieben wird.

## Grün, gelb, rot

```text
GRÜN
  bekannte Atome + bekannte Klammerregel + sichtbarer Besitzer

GELB
  neue lokale Adresse oder isolierte NEW_LOCAL_CARD;
  Seite bleibt teilweise lesbar, aber diese Karte zählt nicht als Kernbeleg

ROT
  bekannter Kern braucht eine andere Bedeutung
  oder eine neue grobe Scope-Regel
  oder Vorgriff über mehr als eine Karte
  oder Sprung über echte Besitzergrenze
  oder Adressring muss als Prosa gelesen werden
```

Eine rote Stelle wird nicht durch eine schönere deutsche Übersetzung gerettet.
Sie bleibt sichtbar und entscheidet gegen die aktuelle Werkstattfassung.

## Vier feste Zukunftsformen

Falls sie auftreten, lautet die erste Lesung ohne Nachverhandlung:

```text
chain   CH + AIN     EINEN ANTEIL NEHMEN
pain    P  + AIN     EINEN ANTEIL EINSETZEN
paiin   P  + AIIN    EINEN WERT EINSETZEN
lair    L  + AIR     VERBINDUNG IM LAUF
```

## Ausgabe pro neuer Seite

Für jede der vier Seiten werden getrennt gezählt:

- exakte alte Oberflächen;
- neue Oberflächen mit alter Komponentenfolge;
- neue Komponentenfolgen aus bekannten Atomen;
- lokale Adressen;
- `NEW_LOCAL_CARD`-Fälle;
- grüne, gelbe und rote Aussagen;
- jede Änderung, die man am Wörterbuch oder an den zehn Regeln vornehmen
  müsste.

Bis alle vier Seiten gelesen sind, wird nichts am Blatt geändert.
