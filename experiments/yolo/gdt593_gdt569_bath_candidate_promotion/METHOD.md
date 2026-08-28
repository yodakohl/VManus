# GDT593 — Methode

## Frage

Können die zwölf neutralen GDT592-Badhandlungen mit einer spezifisch
getragenen AIN- oder OR-Spur einen konkreteren Default erhalten, ohne Y
pauschal mitzudeuten und ohne eine neue Seite, Wurzel, Segmentierung oder
Wortzerlegung zu öffnen?

## Population und Quellen

Ausgangspunkt sind exakt die 61 GDT592-Zeilen mit
`COLD_BATH_OBJECT_DEFAULT` und
`GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT`. GDT593 nimmt daraus nur die
8 AIN- und 4 OR-Vorkommen. Die 49 Y-Vorkommen bleiben unangetastet, weil ihre
Arbeitsbedeutung bereits aktionsabhängig zwischen Körper, Stationsansatz und
Strom wechselt.

GDT569 liefert das getragene Argument, aber keine Quellereignis-ID. Deshalb
wird die kanonische Herkunft aus den GDT581-`OBJECT_ALIAS`-Karten gelesen:

- sechs Ziele besitzen eine `SAME_STATEMENT_EVENT`-Schriftquelle;
- sechs Ziele besitzen `OWNER_DEFAULT`; dort ist die letzte geschriebene
  AIN/OR-Stelle nur Kontextzeuge, ausdrücklich kein nachträglich erfundener
  lokaler Donor.

GDT416 rekonstruiert diesen letzten geschriebenen Kontextzeugen. GDT581,
GDT582 und GDT590 geben seinen exakten Slot und seine bisherige Arbeitsphrase;
GDT515 und ZL3b geben Reihenfolge, Ort und physischen Absatz. Alle gemischten
TSVs werden vor dem Materialisieren auf f75r, f77r, f81r, f81v, f82r und f83r
beschränkt; f84/f84r bleiben gesperrt.

## Zwei occurrence-level Regelkarten

Die Promotion gilt ausschließlich für die zwölf aufgelisteten Aktionsslots:

1. `GDT569_AIN_PORTION_PROMOTION`:
   AIN → `PORTION` → `Anwendungsportion`;
2. `GDT569_OR_UNIT_PROMOTION`:
   OR → `BATH_UNIT` → lokal `Stationseinheit`, nach Reset `Badeinheit`.

OR behält zusätzlich `die Badeinheit` als gleichklassige Zielhost-Alternative.
AIN behält die ältere GDT569-Phrase `denselben Stationsanteil` in der
Herkunftsspur. In beiden Klassen bleibt die vollständige GDT592-Klausel mit
`das zu badende Gut` als allgemeiner Rivale erhalten.

Die sechs gleichsatzinternen Quellen zerfallen in fünf sichtbare Quellen ohne
Readerreset und E3314, wo zwischen AIN und Ziel ein `OT/PARAGRAPH_AFTER` liegt.
Nur die fünf Quellen im selben Objektsegment werden anaphorisch mit `dieselbe`
formuliert. E3314 und die sechs Besitzer-Defaults erhalten den bestimmten Typ
`die Anwendungsportion` bzw. `die Badeinheit`, ohne Identität über einen
Reset zu behaupten. Die sechs Besitzer-Defaults liegen trotz
Satzgrenze im selben physischen Absatz wie ihr nächster geschriebener
Kontextzeuge; der Besitzerkontext, nicht lokale Objektidentität, lizenziert
hier den explorativen Typdefault.

## Leserpatch

Nur die genaue GDT592-Zielklausel wird verändert:

```text
Halte das zu badende Gut im Bad ...
→ Halte dieselbe/die Anwendungsportion im Bad ...
→ Halte dieselbe Stationseinheit/die Badeinheit im Bad ...
```

Grad, Relationen, Füllung und Schluss bleiben unverändert. Die Zuordnung läuft
über Aktionsslot, Hostordinal und die n-te konkrete Klausel im vollständigen
793-Aussagen-Leser. Zwölf Aussagen ändern sich; 781 bleiben bytegleich.

## Behauptungsgrenze

GDT593 ist eine absichtlich konkrete Arbeitsübersetzung. AIN/OR werden an
diesen zwölf Vorkommen als stabile Typvorschläge verwendet; daraus folgt noch
kein bestätigtes Voynich-Wort, kein globales Wörterbuch und keine bewiesene
Objektidentität über Satz- oder Readergrenzen. Die alternative strenge Lesung
bleibt in jeder Zeile als `Badegut` erhalten. Bestätigt werden weder Klartext,
Sprache, Patient, Körperteil, Stoff, Krankheit, Heilung, historisches Codebuch
noch eine ungesehene Seite.
