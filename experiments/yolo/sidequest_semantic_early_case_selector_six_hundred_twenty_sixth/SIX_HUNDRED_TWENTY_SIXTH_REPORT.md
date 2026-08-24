# Sechshundertsechsundzwanzigste Runde: den Fall in fuenf Karten erkennen

## Ergebnis

Ein Lehrling kann auf den festen Seiten jeden der fuenf Hauptfaelle nach
hoechstens fuenf Karten positiv erkennen:

```text
C5  Karte 1: HO=ZUTAT
C3  Karte 3: CFH=AUSWRINGEN
C4  Karte 4: AN=NACHPORTION
C1  Karte 5: OS=ARBEITSFACH
C2  Karte 5: drei CTH=BEREIT-Kerne innerhalb der Eroeffnung
```

C2 ist damit kein blosses Auffangbecken fuer alles, was die anderen Regeln
nicht erkennen. Seine ersten fuenf Karten enthalten dreimal den
BEREIT-Kern, waehrend C1 dort nur einen und C3-C5 keinen tragen.

## Die fuenf Eroeffnungen

- **C1:** `dchey cthoor char chty os` — Abnehmen, Bereit/Arbeitsgang/Ansatz,
  Vorrat, Eintragen/Posten, Arbeitsfach.
- **C2:** `ycheor cthy chor cthaiin qoctholy` — Posten/Abnehmen/Ansatz,
  Bereit/Posten, Ansatz, Bereit/Sollmass, Arbeitsgang/Bereit/Fortsetzen/Posten.
- **C3:** `tshol schoal cfhy shfydaiin cphy` — Eintragen/Halten/Fortsetzen,
  Halten/Arbeitsgang/Zielstelle, Auswringen/Posten, Halten/Posten/Sollmass,
  Einfuellen/Posten.
- **C4:** `qokaiin chaiin ykain ykan ody` — Ansetzen/Sollmass, Sollmass,
  Posten/Zudosieren/Portion, Posten/Zudosieren/Nachportion,
  Arbeitsgang/Schluss.
- **C5:** `chochor cho chodaly daiin sho` — Zutat/Abnehmen/Ansatz, Zutat,
  Zutat/Zielstelle/Posten, Sollmass, Zutat.

## Spaetere Rueckbestaetigung

Die neun Einzelfallmarker wurden durch alle 372 Ereignisse der fuenf
Hauptfaelle verfolgt. Kein fremder Marker erscheint und kein Record wechselt
den Zweig.

- C1 bestaetigt sich spaeter noch dreimal mit `LSH=WASCHEN`.
- C2 liefert sein exklusives `S=TEILEN` erst im 74. C2-Ereignis.
- C3 braucht nach dem fruehen `CFH=AUSWRINGEN` keinen zweiten exklusiven Kern.
- C4 bestaetigt `NACHPORTION` spaeter durch `TALAM=VERWAHREN` und
  `LD=BEFESTIGEN`.
- C5 wiederholt `HO=ZUTAT` achtmal und setzt fast am Ende zusaetzlich
  `DA=ZWEITMARKER`.

## Werkstattdeutung

Das sieht nach einer kurzen Formularerkennung aus: Der Bildbesitzer bestimmt
den Gegenstand, die ersten Karten rufen den Fallzweig auf, und die folgenden
Karten fuehren die gemeinsame Sechs-Modul-Maschine aus. Spaetere seltene
Marker sind keine neue Grammatik, sondern erinnern den Schreiber daran, ob er
waschen, teilen, auswringen, nachdosieren/befestigen oder Zutaten nachfuehren
soll.

## Vollstaendigkeit

Die Ausgabe bindet die fuenf Eroeffnungsstreifen, alle 372 Ereignisse und alle
spaeteren Einzelfallmarker. Es wurde kein Wort ergaenzt oder umgedeutet; C6 und
die drei Astro-Seiten bleiben ausserhalb dieses Prosa-Selektors.

## Naechster Schritt

Als naechstes wird die Auswahlregel in die andere Richtung benutzt: Aus jedem
Fallzweig wird eine kurze normale Werkstattanweisung formuliert und dann Karte
fuer Karte zurueckgeschrieben. Wo die Rueckschreibung mehr als eine der 173
Karten erlaubt, soll die in Pass 614 gefundene Schreiberpalette die sichtbare
Form waehlen. Damit entsteht erstmals ein vollstaendiger praktischer
Schreibdurchlauf fuer C1-C5 statt nur eine Lesefassung.
