# Werkstattblatt nach Pass 1023

## 19 tragbare Kerne

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
Q              BEGINNMARKER / Paket pushen
DY             nur in lizenzierter Endkarte: SCHLUSS
HIER           örtlicher Besitzerzeiger
VARIANTE       örtliche Variante
KLASSE         örtliche Klasse
VORBEZUG       älteren Besitzerrahmen restaurieren
```

## Lesen

```text
BESITZER
  → GANG
    → PAKET
      → HANDLUNG
        → POSTEN / WERT / ANTEIL / EINHEIT
        → AUSGANG / VERBINDUNG / LAUF / ZIELORT
        → GRAD / STUFE
```

1. Längste gelernte Karte und Doppelpaket zuerst öffnen.
2. Mehrere Köpfe verschachteln; der äußere Kopf bleibt nach Kartenende offen.
3. Argument oder Grad nimmt den nächsten Kopf; bei gleicher Entfernung links.
4. `AL/AR` nimmt links, dann laufend, dann den einzigen Kopf derselben Karte
   rechts und erst danach den Besitzer. `L/AIR` nimmt rechts, sonst den
   linken/laufenden Kopf oder genau eine folgende Karte.
5. Fehlt am Paketanfang ein Kopf, höchstens bis zur unmittelbar nächsten Karte
   im selben Besitzersegment vorauslesen.
6. `Q` pusht; `OT` wechselt; `OL` führt fort; `VORBEZUG` restauriert; nur
   lizenziertes `DY` oder eine echte Besitzergrenze schließt.
7. `R` mit eigenem Rechtsglied ist Kopf; nach einer äußeren Handlung ohne
   Rechtsglied ist es Schwanz; dazwischen ist es innerer Kopf.
8. Zeilenende, radialer Knick und Text um ein vorher gezeichnetes Bild sind
   allein keine Grenze.

## Drei Muster

```text
CH + E + T + E + Y
= NEHMEN[GRAD I; EINSTELLEN[GRAD I; AKTIVER POSTEN]]

D_ADDR + AR + OR | Y + K + AR
= BESITZER[AUSGANG]; GEBEN[EINHEIT; AKTIVER POSTEN; AUSGANG]

P + HIER + R + AIR + DY
= EINSETZEN[MARKIEREN[LAUF]]; SCHLUSS
```

## Schreibprobe für eine neue Seite

Bekannte Kerne behalten genau diese kurzen Werte. Neu sein dürfen Bildbesitzer,
lokale Namen und gelernte Ganzkarten. Nicht erlaubt sind ein neuer Kernwert,
Vorgriff über mehr als eine Karte, Sprung über eine Besitzergrenze oder eine
vierte `R`-Funktion.
