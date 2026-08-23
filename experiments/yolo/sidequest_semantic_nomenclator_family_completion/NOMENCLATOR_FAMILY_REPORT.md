# Der verbleibende Ganzwortsatz wird zu Fachwortfamilien

## Ergebnis

Die letzten 27 lokalen Einzelkarten sind nicht 27 unabhaengige Woerter. Nach
der neuen Zerlegung bleiben nur zehn lokale Ganzkarten uebrig, drei davon mit
dem gemeinsamen Kopfwort GEFAESS. Die 27 Karten teilen sich jetzt so:

```text
 7 voll kompositionell
10 teilweise kompositionell; ein lokaler Traeger bleibt
 3 gelernte Gefaesskarten mit demselben Kopfwort
 7 echte kurze Spezialkarten
```

Der groesste Gewinn sind zwei neue, einfach lehrbare Paradigmen:

```text
KCH = BEARBEITEN
  KCH + Y          diesen Posten bearbeiten
  KCH + E + Y      diesen Posten kurz bearbeiten
  KCH + AL         an der Zielstelle bearbeiten
  KCH + OL         weiter bearbeiten

TY = TEILPOSTEN / RESTANTEIL
  CH + TY          Teil abtrennen
  HO + Y + TY      Zutatenteil
  E + TY + D       kleiner Restteil
  EEE + TY         ganzer Teilposten
  OT + TY + OL     naechsten Teilposten weiterfuehren
```

KCH sagt weder ZERREIBEN noch ABSEIHEN noch TRANK. Diese drei alten
Einzellesungen waren miteinander unvereinbar. Der gemeinsame Wert BEARBEITEN
bleibt in allen vier Umgebungen gleich; Ziel, Dauer, Objekt und Fortsetzung
kommen aus den sichtbaren Nachbarteilen.

TY sagt nicht in jeder Karte REST oder RESERVE. Es bezeichnet die
abgetrennte Arbeitseinheit. Der Satzkontext entscheidet, ob sie gerade
abgetrennt, als Zutatenteil bereitgelegt, als kleiner Rest behalten, vollstaendig
genommen oder als naechster Teil weitergefuehrt wird.

## Das neue Gesamtinventar

Die vollstaendige Prosa hat jetzt folgende Architektur:

| Ebene | Kartentypen | Ereignisse |
|---|---:|---:|
| produktiv zusammengesetzt | 131 | 332 |
| teilweise zusammengesetzt | 20 | 21 |
| gelernte Ganzkarten | 22 | 28 |
| **gesamt** | **173** | **381** |

Nur fuer die 292 offenen, nicht abschliessenden Ereignisse lautet die Bilanz:

```text
256 voll kompositionell
 16 teilweise kompositionell
 20 gelernte Ganzkarten
```

Damit sind 272/292 offene Ereignisse aus sichtbaren Bauteilen zumindest
teilweise lesbar. Der grosse opake Exemplarrest der frueheren Theorie ist auf
einen kleinen realistischen Nomenklator geschrumpft.

## Weitere Reparaturen

Zehn Karten behalten einen lokalen Innenrest, aber ihre portable Komponente
ist jetzt klar:

- `ral`: `AL` liefert „zur Zielstelle“; Abkuehlung faellt weg.
- `sotodan`: `OT` liefert „danach“, der gelernte Rest ANWENDEN.
- `skar`: `AR` liefert „von dort“, der gelernte Rest AUSGIESSEN.
- `talam`: `AL` liefert das Ziel, der gelernte Rest VERWAHREN.
- `lo`: `L` liefert die Abfuehrrichtung; kein zweiter Bodenablauf noetig.
- `ls`: `L` liefert den Auslass; DUESE war zu eng.
- `qolky`: `OL` liefert WEITERFUEHREN; STATION war bildabhaengig.
- `tshey`: die bekannte `SHEY`-Karte liefert KLARLAUF; SPUELWASSER war zu eng.
- `tshol`: `HO + L` ergibt ZUTAT ENTNEHMEN; kein neues Pflanzenwort noetig.
- `chealror`: `AL + OR` liefert ANSATZ ZUR ZIELSTELLE; der innere
  Quelltraeger bleibt lokal.

Die drei alten Gefaesswoerter `os`, `ly` und `oykchor` werden nicht mehr als
GEFAESS, SCHALE und TOPF auswendig gelernt. Alle drei heissen im kleinen
Werkstattwoerterbuch schlicht GEFAESS. Bild und Arbeitsposition liefern die
jeweilige Form.

## Was als Ganzwort bleibt

Sieben lokale Spezialkarten bleiben absichtlich ungeteilt:

```text
CFHY    auswringen
CPHY    nachseihen
YTEY    fuellen
CHES    teilen
SH      Staengel
DCHEY   Wurzel
QEKEY   roh
```

CFHY und CPHY bilden ein gelerntes Trennpaar. SH und DCHEY sind
bildgebundene Pflanzenteile. YTEY, CHES und QEKEY sind kurze Befehls- oder
Zustandskarten. Hier waere eine weitere Buchstabenbedeutung teurer als das
Auswendiglernen der Karte.

## Drei verbesserte Ruecklesungen

### f10r, H1-S001

```text
Wurzel -> Ansatz bereit -> daraus -> Teil abtrennen -> Gefaess
-> Wasserzulauf -> naechsten Teilposten weiterfuehren
-> Posten ansetzen -> Sollmass -> kleiner Restteil
```

Lesung: Nimm die Wurzel, bereite den Ansatz, trenne daraus einen Teil ab,
gib ihn in das Gefaess, gib den Wasserzulauf zu, fuehre den naechsten
Teilposten weiter, setze ihn nach Sollmass an und behalte einen kleinen
Restteil.

### f56r, H5-S003 bis H5-S005

```text
Staengel -> Zutat -> diesen Posten kurz bearbeiten -> erneut ansetzen
Posten ansetzen -> Auszug zugeben -> an der Zielstelle bearbeiten
Zutat -> Posten ansetzen -> Auszug daraus -> danach anwenden
```

Die Folge braucht weder ein festes ZERREIBEN noch ein festes ABSEIHEN im
KCH-Stamm. Der Bearbeitungskern bleibt gleich; E, AL und OL steuern seine
Ausfuehrung.

### f83r, B3-S034

```text
Sollstufe -> bereit -> Teil abtrennen -> Folgemass
-> untere Zielstelle -> absetzen; Schluss
```

Lesung: Bringe auf Sollstufe, halte bereit, trenne einen Teil ab, stelle das
Folgemass ein, fuehre zur unteren Zielstelle, lass absetzen und schliesse.

## Neue Arbeitsbasis

`COMPACT_173_CARD_DICTIONARY.tsv` ist jetzt das konsolidierte Woerterbuch fuer
alle Prosakarten. `COMPACT_381_EVENT_INTERLINEAR.tsv`,
`COMPACT_116_PHRASES.tsv` und `COMPACT_11_RECORDS.md` tragen dieselben Werte
durch die komplette feste Prosa. `KCH_TY_PARADIGMS.tsv` ist die kleine
Lehrtafel, mit der ein Schreiber die beiden neuen Familien lernt.

Der naechste sinnvolle Angriff ist nicht noch ein weiterer Buchstabenstamm.
Jetzt sollte man die 22 uebrigen Ganzkarten als exaktes Mini-Codebuch
anordnen: vier wiederkehrende offene Sachkarten, acht terminale
Spezialprogramme und zehn lokale Fachkarten. Daraus kann ein wirklich
benutzbares einseitiges Werkstattwoerterbuch samt Schreibuebung entstehen.
