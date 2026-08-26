# GDT492 — die vier Abweichungen sind Besitzerwortschatz, keine neuen Wörter

Status: `FOUR_OWNER_VARIANTS_DECOMPOSED__THIRTY_FIVE_SLOT_CELLS_OBSERVED__NINE_ALTERNATE_ACTION_CELLS`

## Ergebnis

Die vier nicht restgleichen GDT491-Karten zerfallen vollständig in zwölf
sichtbare Slots. Sie verwenden nur sieben bereits feststehende Werte: T, R,
AL, Y, CH, E und OR. Jeder dieser Werte besitzt alte Träger in jedem der fünf
Register. Der resultierende Atlas hat **35/35 beobachtete Registerzellen** und
keinen undefinierten Slot.

Die acht nicht-aktionalen Slotvorkommen teilen sich sauber:

- sieben behalten denselben portablen Wert, wechseln aber das alte
  Besitzerwort;
- einer bleibt sogar wörtlich gleich: `E=GRAD I` in Source-Text und
  Biological;
- die vier Aktionsplätze sind der beabsichtigte Kontrast
  `T=EINSTELLEN ↔ R=MARKIEREN`, nicht eine Owner-Reparatur.

## Was die vier Karten konkret sagen

`@ACTION+AL+Y` unterscheidet Zielposition/Positionsposten von
Zielstation/Stationsposten. Der portable Rest bleibt `ZIELORT · POSTEN`.

`@ACTION+CH+E+Y` unterscheidet den laufenden Eintrag vom Stationsposten und
`ENTNEHMEN` von `POSTEN ENTNEHMEN`; `GRAD I` bleibt unverändert. Der portable
Rest bleibt `NEHMEN · GRAD I · POSTEN`.

`@ACTION+OR+Y` unterscheidet Arbeitseinheit/Pflanzenposten von
Stationseinheit/Stationsposten. Der portable Rest bleibt `EINHEIT · POSTEN`.

`CH+@ACTION` unterscheidet „Pflanzenteil nehmen“ von „Posten entnehmen“, bevor
T oder R folgt. Der portable erste Slot bleibt `NEHMEN`.

## Die Rahmen leben auch außerhalb T und R

Die vier exakten Rahmenfamilien enthalten 23 alte Ereignisse auf elf Seiten
und in allen fünf Registern. Daraus entstehen 17 Rahmen×Handlungs-Zellen und
19 beobachtete deutsche Satzformen. Neun Zellen verwenden weder T noch R:

- `@ACTION+AL+Y` trägt zusätzlich OK und CH;
- `@ACTION+CH+E+Y` zusätzlich OK, K und S;
- `@ACTION+OR+Y` zusätzlich SH und S;
- `CH+@ACTION` zusätzlich K und S.

Zwei besonders starke Brücken halten sogar Handlung und gesamten formalen
Rahmen gleich und wechseln nur das Register:

- `OK+AL+Y`: Positionsposten/Zielposition celestial gegen
  Stationsposten/Zielstation biological;
- `CH+AL+Y`: Stationsposten/Zielstation biological gegen
  Drogenposten/Zielgefäß pharmazeutisch.

Damit ist die beste Arbeitslesung nicht „vier Ausnahmen“, sondern eine kleine
produktive Kürzelgrammatik mit registergebundenem Fachwortschatz. Die Wurzeln
bestimmen Slot und portablen Wert; der Besitzer bestimmt, ob derselbe POSTEN
als Eintrag, Pflanzen-, Stations-, Positions- oder Drogenposten ausgesprochen
wird.

Der deterministische Validator besteht 105 von 105 Prüfungen. Keine Phrase,
Bedeutung, Formulierung, Modellfolge, Grenze, Oberfläche, Rezeptfolge, Event-
oder Seitenzuordnung wurde hinzugefügt oder geändert.

## Nächster sinnvoller Schritt

Aus den 35 beobachteten Registerzellen kann nun ein kleiner Owner-abhängiger
Satzgenerator für alle elf T/R-Rahmen gebaut werden. Er muss zwei Ausgabetypen
streng sichtbar trennen: wortwörtlich beobachtete Klausel und slotweise
zusammengesetzte Arbeitslesung. So lassen sich die vier Varianten in allen
Registern vorhersagen, ohne eine erzeugte Phrase als Manuskriptbeleg
auszugeben.
