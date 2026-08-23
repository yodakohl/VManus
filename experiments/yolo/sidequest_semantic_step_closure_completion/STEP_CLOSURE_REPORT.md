# Werkstattklammer und Zellschluss

Diese Runde ordnet nicht neue Gegenstände in das Wörterbuch ein. Sie trennt
etwas, das in den bisherigen Übersetzungen zu oft unter demselben deutschen
Wort „schließen“ lief: eine Handlung am Gerät, das Bestätigen einer lokalen
Arbeitszelle und das Ende eines ganzen Records.

## Die einfache Schreiberregel

Ein Lehrling braucht nur vier Regeln:

1. **Endkarte:** Handlung ausführen und die lokale Arbeitszelle abhaken.
2. **Keine Endkarte:** Besitzer, Posten, Quelle, Ziel und Arbeitsgang bleiben
   für die nächste Zelle verfügbar.
3. **Record-Ende:** Alle laufenden Register werden zurückgesetzt, auch wenn
   keine Endkarte geschrieben wurde.
4. **Physisches Zeilenende:** Nur die Feder neu ansetzen; nichts zurücksetzen.

Damit entstehen drei wirkliche Ausgänge:

| Ausgang | Anzahl | Werkstattwirkung |
|---|---:|---|
| `COMMIT_CELL` | 89 | Arbeitsgang bestätigen; Besitzer/Posten bleiben verfügbar |
| `HANDOFF_OPEN` | 19 | laufenden Arbeitsgang an die nächste Zelle übergeben |
| `RELEASE_RECORD` | 8 | am Record-Ende alle Register entlassen |

## Die Endkarten sind Handlung plus Bestätigung

Es gibt 37 exakte Endkartentypen mit 89 Vorkommen. Bei allen 89 steht die
Endkarte am Ende der jeweiligen Arbeitsanweisung. Die meisten gehören zu
kleinen erlernbaren Reihen:

| Familie | Typen | Vorkommen | Beispiele |
|---|---:|---:|---|
| abgestuft ansetzen | 3 | 19 | kurz, länger, vollständig ansetzen |
| umsetzen/ein-/abführen | 8 | 21 | umsetzen, einführen, abführen |
| absetzen | 3 | 14 | absetzen, länger absetzen |
| seihen | 2 | 4 | seihen, abseihen |
| fortsetzen | 3 | 6 | fortsetzen, weiter absetzen |
| nächste Operation | 4 | 7 | kurze/lange Folge, Folgeumsetzung |

Das sind 23 Typen und 71 Vorkommen. Nur 14 Typen mit 18 Vorkommen bleiben
gelernte Spezialkarten, etwa **abkühlen**, **schwenken**, **waschen**,
**abziehen**, **auftragen**, **nachwaschen**, **befestigen** oder
**Wasserlauf schließen**. Ein kleiner Mehrschreiberbetrieb kann daher ein
produktives Grundmuster plus ein kurzes Spezialdeck lernen.

Die Übersetzung einer Endkarte wird nun gedanklich in zwei Teile zerlegt:

```text
QOKEEDY     LÄNGER ANSETZEN  +  ARBEITSZELLE BESTÄTIGEN
LCHEDY      ABFÜHREN         +  ARBEITSZELLE BESTÄTIGEN
SHEDY       ABSETZEN         +  ARBEITSZELLE BESTÄTIGEN
SHCKHEDY    SEIHEN           +  ARBEITSZELLE BESTÄTIGEN
```

Der zweite Teil ist keine zusätzliche lange Satzbedeutung. Er ist die
gelernte terminale Ausführung der ganzen Karte.

## Warum sichtbares `-dy` nicht genügt

Auf den sieben Prosaseiten enden 105 sichtbare Gruppen auf `dy`. Davon sind 89
Endkarten und 16 ausdrücklich offen:

- fünfmal ist sichtbares `dy` nur die exakte Karte **DIESER POSTEN**;
- elfmal ist `chdy|chedy` die offene Handlung **UMSETZEN**.

Der Schreiber lernt also nicht die Buchstabenregel „`dy` macht Schluss“.
Er lernt die 37 terminalen Ganzkarten beziehungsweise ihre kleinen Reihen.
Das erklärt, warum gleich aussehende Schriftenden nicht dieselbe Satzwirkung
haben müssen.

## Sachhandlung ist nicht Zellschluss

Der Unterschied wird in zwei benachbarten Biological-Beispielen besonders
klar:

- B2-S014: **„Schließe den Bodenablauf“** ist eine Handlung am Gerät. Es folgt
  keine Endkarte; die Arbeitsfolge wird weitergereicht.
- B4-S014: **„Schließe den Wasserlauf; Schluss“** enthält Sachhandlung und
  terminale Kartenausführung; die lokale Zelle ist bestätigt.

Ebenso kann ein Record ohne Endkarte enden. H1 schließt seine erste Anweisung
nicht, sondern reicht Wurzelansatz und Posten an H1-S002 weiter. Erst das
Record-Layout entlässt danach alle Register. B2 dagegen endet mit der Endkarte
„Rest abführen; Schluss“.

## Zeilenumbruch

18 Anweisungen laufen über mehr als einen physischen Locus. Fünfzehn enden
später mit einer Endkarte; drei bleiben auch nach dem Zeilenwechsel offen:

- H5-S001 reicht den Zutatenansatz an die nächste Zelle weiter;
- B5-S003 endet erst mit dem Record;
- B6-S001 läuft über zwei Zeilen und endet ebenfalls erst mit dem Record.

Damit kann eine Aussage über eine Zeilengrenze weiterlaufen, wie vom Benutzer
früh in dieser Sidequest vermutet. Der Umbruch folgt dem bereits gezeichneten
Bildraum; er ist kein eigener semantischer Befehl.

## Was sich an der Lesefassung ändert

Die 173 Kartenwerte und alle 381 Ereignislesungen bleiben konkret erhalten.
Neu ist die editorische Werkstattklammer:

- `[ZELLE ZU]` = lokale Arbeit bestätigt;
- `[WEITER]` = offene Übergabe an die nächste Zelle;
- `[RECORD ENDE]` = alle Register zurücksetzen.

Die vollständige Lesefassung zeigt diese Marken in allen elf Records. Sie
sind moderne Lesehilfen und werden nicht als zusätzliche Manuskriptzeichen
behauptet.

## Dateien

- `STEP_CLOSURE_DECK.tsv`: alle 37 Endkarten;
- `STATEMENT_ENDINGS.tsv`: alle 116 Anweisungen mit ihrem Ausgang;
- `LINE_CARRY.tsv`: die 18 zeilenübergreifenden Anweisungen;
- `OPEN_DY_COUNTERCARDS.tsv`: alle 16 offenen sichtbaren `-dy`-Fälle;
- `SELECTED_173_STEP_CLOSURE_DICTIONARY.tsv`;
- `SELECTED_381_STEP_CLOSURE_INTERLINEAR.tsv`;
- `SELECTED_116_STEP_CLOSURE_SENTENCES.tsv`;
- `SELECTED_11_STEP_CLOSURE_RECORDS.md`.

Die Kreis-/Astroseiten bleiben in ihrer getrennten lokalen Diagrammschicht.
Keine weitere Seite wurde einbezogen.
