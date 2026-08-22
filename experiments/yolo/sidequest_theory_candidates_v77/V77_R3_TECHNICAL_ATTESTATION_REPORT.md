# V77 R3 — maschinenpruefbarer Ganzkarten- und Codebuchaudit

Status: kreative Zehnseiten-Arbeitstheorie, keine Entzifferung. Dieser Audit
entscheidet nur, ob ein alter Mnemonic-Handle weiterhin als portables Wort
gedruckt werden darf.

## Entscheidung

```text
CODEBOOK_ATTESTED_CATEGORY                         0
EXEMPLAR_VALUE_UNKNOWN                           21 Karten
FORMAL_LABEL_NOT_WORD                             3 Karten
zusaetzlicher formaler Nichtwortkanal auf MASS?   1
```

Damit werden alle elf alten Mnemonic-Handles als portable Woerter
zurueckgezogen. Die vier formalen Prompts bleiben ausschliesslich
`FORMAL_LABEL_NOT_WORD`; einer davon liegt auf derselben exakten Karte wie
`MASS?`. Der Gesamtausgang lautet:

`ZERO_PORTABLE_WORDS__11_MNEMONICS_TO_UNKNOWN__4_FORMAL_CHANNELS_NONWORD`.

Das ist kein Nachweis, dass der betreffende Kartentyp keine Bedeutung hatte.
Es ist die engere Feststellung, dass V77 R3 keinen vollstaendigen zeitgenoessischen
Eintrag fand, der seine vorgeschlagene minimale Kategorie positiv attestiert.

## Operative Quellen-Firewall

Die historische Tabelle wurde vor dem Oeffnen anonymer Karten-IDs,
Haeufigkeiten oder Auftreten eingefroren. Die Pflichtdatei CURRENT hatte die
elf alten Mnemonic-Namen bereits verraten; deshalb kann diese Runde keine
vollstaendige psychologische Blindheit behaupten. Der maschinenpruefbare
Ersatz war:

1. keine Karten-ID, Haeufigkeit, V69-Woerterbuchzeile oder Auftretensbindung
   oeffnen;
2. echte historische Schluesseltabelle seitenweise lesen;
3. alle ohne erfundenen Glyphnamen transkribierbaren Eintraege aufnehmen;
4. TSV und Hash einfrieren;
5. erst danach das zentrale Kartenmanifest und die 381 Ereignisse binden.

Der exakte Vor-Oeffnungs-Hash ist in `V77_R3_SOURCE_FREEZE.json` erhalten. Nach
der Kartenoeffnung wurden nur zwei palaeographische Konfidenzen von HIGH auf
MEDIUM gesenkt und die IA-URL mechanisch kleingeschrieben; Eintraege, Codes,
Kategorien und Auswahl blieben unveraendert. Beide Hashstaende sind publiziert.

## Eingefrorenes historisches Inventar

Die Quelle ist Gabriel de Lavindes Schluessel Nr. 13 von 1379,
`Zifera [Anonym]`, im damaligen Vatikanischen Archiv, Collect. 393,
fol. 166–181. Verwendet wird Aloys Meisters dokumentarische Ausgabe,
Schluesselsammlung I Nr. 13, gedruckte Seite 173. Das Digitalisat ist
[direkt im Internet Archive](https://archive.org/download/diegeheimschrif00meisgoog/diegeheimschrif00meisgoog.pdf)
gebunden; sein SHA-256 steht in jeder Inventarzeile.

`V77_R3_FROZEN_SOURCE_INVENTORY.tsv` enthaelt 37 wirkliche
Nomenklatoreintraege mit Code, Schluessel, Datierung, Archivort,
Editionsseite, Zitat und Locator. Beispiele aus der eingefrorenen Reihenfolge:

| Quellenwortlaut | Code | Quellenseitige Klasse |
|---|---|---|
| `rex Anglie` | `gl` | Person/Amt |
| `Imperator` | `aa` | Person/Amt |
| `Gentes armorum` | `gm` | Kollektiv/Militaer |
| `Matrimonium` | `ln` | diplomatisches Thema |
| `pax` | `pR` | diplomatisches Thema |
| `guerra` | `pl` | diplomatisches Thema |
| `Mediolanum` | `10` | Ort |

Die `ln`- und `pl`-Minimen sind als MEDIUM transkribiert. Der Audit benoetigt
ihre Form nicht fuer eine Voynich-Zuordnung.

Das Inventar zeigt positiv, dass eine ganze opake Einheit um 1379 Personen,
Orte, Kollektive und abstrakte diplomatische Themen vertreten konnte. Es
enthaelt aber keinen Eintrag fuer Menge/Parameter, Anwenden, Bereitschaft,
Arbeitsansatz, Zielslot, Klarzustand, voriges Element, Anteil, Temperieren,
Spuelen, Ablassen oder eine abstrakte Registeroperation. Das beweist keine
historische Nichtexistenz solcher Kategorien. Unter der harten Zulassungsregel
fehlt lediglich die erforderliche positive Zeile.

## Gebundener Kartensatz

Das zentrale `V77_TARGET_FREEZE.tsv` bestimmt unveraendert:

- alle 14 V69-Kontrollidentitaeten mit 119 Auftreten;
- die Top 10 verbleibenden Ganzkarten nach absteigender Haeufigkeit und dann
  aufsteigender anonymer ID mit 78 Auftreten;
- zusammen 24 Identitaeten und 197/381 Prosaereignisse.

Keine Bedeutung, Oberflaechenaehnlichkeit oder Auftretensqualitaet ging in die
Top-10-Auswahl ein. `V77_R3_DECISION_TABLE.tsv` reproduziert diese Rangfolge
und `V77_R3_OCCURRENCE_AUDIT.tsv` gibt alle 197 Vorkommen vollstaendig aus.

## Die vierzehn Kontrollen

| alte Schicht | Auftreten H/B | Ergebnis | Hauptgrund |
|---|---:|---|---|
| `TEMPERIEREN?` | 0/7 | `EXEMPLAR_VALUE_UNKNOWN` | nur Biological; angenommene Waermestelle |
| `ANWENDEN?` | 3/7 | `EXEMPLAR_VALUE_UNKNOWN` | breit konsistent, aber aus demselben Handle expandiert |
| `MASS?` | 9/11 | `EXEMPLAR_VALUE_UNKNOWN` | Zahlen-Code `10` fuer Mailand ist kein Mengenwort; Renderer-Teilkanal |
| `LOKALEN_RELATIONSSLOT_SETZEN` | 1/5 | `FORMAL_LABEL_NOT_WORD` | editoriale Registeroperation |
| `ANSATZ?` | 5/2 | `EXEMPLAR_VALUE_UNKNOWN` | Neueroeffnung, Wiederholung und Fortsetzung kollabieren |
| `SPÜLEN?` | 0/8 | `EXEMPLAR_VALUE_UNKNOWN` | 8/8 terminal; Handlung nicht von CLOSE trennbar |
| `KLAR?` | 1/3 | `EXEMPLAR_VALUE_UNKNOWN` | Herbal-Klarheit gegen generischen Bio-Pruefzustand |
| `STANDARDSLOT_SETZEN` | 1/8 | `FORMAL_LABEL_NOT_WORD` | editoriale Registeroperation |
| `AKTIVEN_ARBEITSSTAND_VERKNÜPFEN` | 3/16 | `FORMAL_LABEL_NOT_WORD` | editoriale Registeroperation |
| `ZIEL?` | 1/9 | `EXEMPLAR_VALUE_UNKNOWN` | Ziel wurde vom Registermodell geliefert; Platzierungs-Shortcut |
| `ABLASSEN?` | 0/8 | `EXEMPLAR_VALUE_UNKNOWN` | 8/8 terminal; Handlung nicht von CLOSE trennbar |
| `VORIGES?` | 1/1 | `EXEMPLAR_VALUE_UNKNOWN` | nur zwei Auftreten; Vorgaenger-/Positionskonfundierung |
| `BEREIT?` | 3/4 | `EXEMPLAR_VALUE_UNKNOWN` | phenologisches Oeffnen und Prozessbereitschaft nicht atomar gleich |
| `ANTEIL?` | 1/1 | `EXEMPLAR_VALUE_UNKNOWN` | nur zwei Auftreten; Pflanzenfraktion und Bio-Charge |

Bei `MASS?` bleibt der oberflaechenspezifische
`VORGABEPARAMETER?`-Kanal getrennt als `FORMAL_LABEL_NOT_WORD`; er macht den
Kartentyp nicht zum Mengenwort.

## Cross-Herbal/Bio-Invarianz

Elf der 14 Kontrollkarten treten in beiden Prosasektionen auf. Das ist eine
gute formale Wiederverwendung, aber kein unabhaengiger Bedeutungsbeleg: Die
V69-Ausgaben hatten jedes Auftreten bereits mit dem jeweiligen Handle
formuliert. Eine anschliessend wiedergefundene Konsistenz waere kreisfoermig.

Trotzdem findet der occurrence-genaue Drucktest echte Schwachstellen:

- `BEREIT?` verbindet in H2 das Oeffnen von Pflanzenteilen mit spaeteren
  Arbeitszustandspruefungen;
- `KLAR?` ist nur in H3 spezifisch Klarheit, waehrend die drei Bio-Zeilen einen
  allgemeinen Pruefzustand tragen;
- `ANSATZ?` deckt Eroeffnen, Wiederholen und Fortsetzen ab;
- `VORIGES?` und `ANTEIL?` sind mit je zwei Auftreten nicht belastbar;
- `TEMPERIEREN?`, `SPÜLEN?` und `ABLASSEN?` besitzen gar keinen
  Herbal-Gegentest.

Somit ueberlebt keine atomare Wortbedeutung zugleich Dokumentations- und
Auftretensgate. Eine breite formale Funktion kann weiterhin existieren, wird
aber nicht als Wort gedruckt.

## CLOSE, Platzierung und falsche Freunde

`SPÜLEN?` und `ABLASSEN?` sind zusammen 16/16-mal terminal. Bei den zehn
Haeufigkeitskontrollen sind vier Typen mit zusammen 29/29 Auftreten terminal.
Insgesamt entfallen 45/197 auditierten Ereignissen auf solche terminalen
Karten. Hohe Wiederholung kann daher eine Schlussklasse statt eines
Handlungslexems anzeigen.

Auch Ziel-, Mengen-, Relations- und Aktivkarten stehen genau an den Positionen,
aus denen V69 ihre Registerfunktion abgeleitet hatte. Der Audit behandelt
diese Platzierung als Konfundierung, nicht als zweite unabhaengige Stuetze.

Die wichtigsten falschen Freunde sind:

- ein Zahlencode als **Codeform** (`Mediolanum -> 10`) attestiert nicht die
  Bedeutung „Menge“;
- `pax` und `guerra` sind konkrete diplomatische Themen, keine Lizenz fuer
  einen beliebigen Prozesszustand;
- Orts- und Personencodes attestieren externe Werte, keinen abstrakten
  Ziel-/Relationsslot;
- alphabetische Aehnlichkeit zwischen historischen Codes und sichtbaren
  Formen wird nie verglichen.

## Ganzkarten-Polyfunktionalitaet

Die exakte Karte bleibt der auditierte Atomtyp. Dennoch kann eine alte
Expansion mehrere Funktionen unter einem Handle verstecken. Der deutlichste
Fall ist `MASS?`: derselbe exakte Typ traegt einen Mengen-Mnemonic und nur bei
der `daiin`-Oberflaeche zusaetzlich den formalen Vorgabeparameterkanal.
`BEREIT?`, `KLAR?` und `ANSATZ?` kollabieren ebenfalls verschiedene lokale
Zustaende. Das ist mit Polyfunktionalitaet, Homographie oder bloss zu breiten
editorialen Handles vereinbar; keine dieser Moeglichkeiten erfuellt die
Attestationsregel.

Die Top-10-Nichtkontrollen erhalten absichtlich keinen nachtraeglichen Gloss.
Vier sind perfekte Schlusskarten; andere sind nur haeufig oder
sektionuebergreifend. Alle zehn bleiben `EXEMPLAR_VALUE_UNKNOWN`.

## Maschinenregel fuer V78

```text
if portable_dictionary_decision == CODEBOOK_ATTESTED_CATEGORY:
    print only the attested minimal category plus complete source row
elif portable_dictionary_decision == FORMAL_LABEL_NOT_WORD:
    print [FORMAL:...; KEIN WORT]
else:
    print [EXEMPLAR_VALUE_UNKNOWN]

occurrence-bound fluent prose may remain in brackets,
but must never be inherited as the exact card's dictionary value.
```

`V77_R3_WITHDRAWALS.tsv` enthaelt elf Wort-Rueckzuege und vier formale
Nichtwort-Festschreibungen. Kein Stamm, Laut, PAGE_HOST, Substring oder
Astro-Gruppenwert wurde verwendet. Keine weitere Seite wurde geoeffnet. f84 und f84r blieben versiegelt.
