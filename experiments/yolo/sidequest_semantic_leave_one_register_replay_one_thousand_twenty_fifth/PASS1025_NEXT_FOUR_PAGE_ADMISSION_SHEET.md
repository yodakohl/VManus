# Aktuelles Eintrittsblatt für die nächsten vier Seiten

Dieses Blatt ersetzt das Pass-1024-Blatt. Während der gemeinsamen Erstlesung
der vier neuen Seiten wird es nicht umgeschrieben.

## Nullregel: Sichtbares bleibt sichtbar

```text
EINE IDENTISCHE LAUFTEXT-OBERFLÄCHE → EINE IDENTISCHE KOMPONENTENFOLGE
```

Ein ähnliches Wort darf eine Schreiberverwandtschaft zeigen. Es darf kein
fehlendes Atom und keine fehlende Bedeutung importieren.
Eine lokale Bild-/Ringadresse bleibt dagegen eine unzerlegte Adresse in ihrem
eigenen Namensraum.

```text
cheo   = CH + E + O
okeor  = OK + E + OR
```

## 19 Kerne

```text
Y     AKTIVER POSTEN       OK    SETZEN           OL    FORTSETZEN
OT    DANACH               AL    ZIELORT          CH    NEHMEN
SH    HALTEN               AR    AUSGANG          K     GEBEN
AIIN  WERT                 S     WÄHLEN            CHD   UMSETZEN
OR    EINHEIT              L     VERBINDUNG        T     EINSTELLEN
AIN   ANTEIL               R     MARKIEREN         P     EINSETZEN
AIR   LAUF
```

## Steuerung und lokale Kanäle

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

## Lesen

1. Lauftext von Bild-/Ringadresse trennen. Eine Adresse eröffnet keinen Satz.
2. Besitzer und echte Besitzer-/Proseblockgrenzen eintragen. Zeile oder
   Bildumbruch allein schließt nicht.
3. Exakte alte Oberfläche zuerst; sonst sichtbare Atome ohne unsichtbare
   Ergänzung zerlegen.
4. Längstes Paket und unmittelbare Doppelung öffnen. Paket-X+X steigt eine
   Ebene ab; freies X+X bedeutet mehrere X oder X nochmals.
5. Mehrere Handlungsköpfe verschachteln; der äußere Kopf bleibt offen.
6. Argument/Grad nimmt den nächsten Kopf; bei Gleichstand links.
7. `AL/AR`: links → laufend → einziger gleichkarten-rechter Kopf → Besitzer.
8. `L/AIR`: rechts → links/laufend → höchstens eine folgende Karte.
9. Kopflose Anfangspakete dürfen höchstens eine Karte im selben Besitzer
   vorausgreifen.
10. `Q` pusht, `OT` wechselt, `OL` führt fort, `VORBEZUG` restauriert,
    lizenziertes `DY` schließt.
11. `R` mit Rechtsglied ist Kopf, nach äußerer Handlung Schwanz, dazwischen
    innerer Kopf.

## Wertung

```text
GRÜN
  alte Oberfläche oder neue sichtbare Komposition aus bekannten Atomen;
  bekannte Scope-Regel; sichtbarer Besitzer

GELB
  lokaler Name, Adresse oder isolierte NEW_LOCAL_CARD;
  keine Wörterbuchrettung daraus

ROT
  gleiche Lauftextoberfläche mit anderer Komponentenfolge
  fehlendes Atom aus nur ähnlicher Karte importiert
  bekannter Kern braucht neue Bedeutung
  neue grobe Scope-Regel
  Vorgriff über mehr als eine Karte
  Sprung über echte Besitzergrenze
  Adressregister muss zu Prosa werden
```

## Vier unverhandelte Vorhersagen

```text
chain   CH + AIN     EINEN ANTEIL NEHMEN
pain    P  + AIN     EINEN ANTEIL EINSETZEN
paiin   P  + AIIN    EINEN WERT EINSETZEN
lair    L  + AIR     VERBINDUNG IM LAUF
```

## Vierseitige Ausgabe

Erst nachdem alle vier Seiten erfasst sind, werden gemeinsam bilanziert:

- exakte registerfremde Oberflächen;
- registerfremde Komponentenfolgen;
- neue Folgen aus bekannten Atomen;
- lokale Namen und `NEW_LOCAL_CARD`;
- identische Oberflächen mit abweichender Zerlegung;
- grüne, gelbe und rote Aussagen;
- jede verlangte Änderung an einem Kern oder Scope-Griff.
