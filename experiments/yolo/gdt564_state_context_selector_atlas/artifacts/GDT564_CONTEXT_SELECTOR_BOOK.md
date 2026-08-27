# GDT564 – kompakter Kontextwähler für alle 402 Zustandsrezepte

## Ergebnis

301 Rezepte haben in den aktuellen Ereignissen eine feste Mikrophrase. Die101 variablen Rezepte
werden durch415 beobachtete Kontextzellen vollständig getrennt. `Rezept + aktive Handlung + aktives
Argument` hat null mehrdeutige Zellen; Besitzer, Seite und Register sind nicht nötig.

```text
geschriebene Handlung vorhanden  → nur aktives Argument auswählen
nur geschriebenes Argument da    → nur aktive Handlung auswählen
beide Slots ausgelassen           → Handlung + Argument auswählen
```

## Vier portable Routen

| Route | Rezepte | Ereignisse | Kontextzellen |
|---|---:|---:|---:|
| `FIXED_RECIPE` | 301 | 379 | 301 |
| `WRITTEN_ACTION__SELECT_ARGUMENT` | 54 | 638 | 144 |
| `WRITTEN_ARGUMENT__SELECT_ACTION` | 15 | 206 | 76 |
| `OPEN_FRAME__SELECT_ACTION_ARGUMENT` | 32 | 433 | 195 |

Die301 festen Rezepte plus415 variable Zellen ergeben716 vollständige Rezept-Kontext-Lesungen.
Der sichtbare Dreiwegschalter ist absichtlich etwas vorsichtiger als ein pro Rezept gelernter
Minimaltrick: Er verlässt sich nicht auf zufällige Gleichläufe von Handlung und Argument.

## Empirisch kleinste Schlüssel

| Minimalrelation | Rezepte | Ereignisse | Mikrophrasen |
|---|---:|---:|---:|
| `ARGUMENT_ONLY` | 49 | 620 | 134 |
| `ACTION_ONLY` | 26 | 240 | 108 |
| `ACTION_ARGUMENT_REQUIRED` | 15 | 385 | 149 |
| `EITHER_ACTION_OR_ARGUMENT` | 6 | 14 | 14 |
| `ARGUMENT_OR_RESOLUTION_MODE` | 5 | 18 | 10 |

Für einen festen ausführbaren Standard wird bei Gleichstand das Argument bevorzugt. Damit nutzen60
variable Rezepte nur das Argument,26 nur die Handlung und15 beide Werte. Die portable sichtbare
Regel bleibt jedoch54/15/32, weil sie auch bei einer später neu auftretenden Kombination weiß, welcher
Slot wirklich offen ist.

## Warum die Zustände zählen

Wählt man je Rezept immer nur seine häufigste Phrase, trifft man 566/1277 Ereignisse.
Nur die Handlung erreicht 932/1277, nur das Argument 872/1277.
Handlung plus Argument erreicht 1277/1277 und lässt 0 mehrdeutige Zellen.

## Wiederverwendete Zellen

183/415 Zellen treten mehrfach auf und tragen 1045/1277 Ereignisse.
172 Zellen stehen auf mehreren Seiten,123 in mehreren Registern und
47 in beiden Seitenkohorten. Die größte Einzelzelle hat 64 Ereignisse.

| Rezept | Selektor | Ereignisse | Mikrophrase |
|---|---|---:|---|
| `SH+E+DY` | `ARGUMENT=Y` | 64 | Halte den Posten; auf Grad I; abschließen. |
| `OK+E+DY` | `ARGUMENT=Y` | 56 | Setze den Posten; auf Grad I; abschließen. |
| `OK+EE+DY` | `ARGUMENT=Y` | 56 | Setze den Posten; auf Grad II; abschließen. |
| `L+CHD+DY` | `ARGUMENT=Y` | 32 | Bearbeite den Posten; über die Verbindung; abschließen. |
| `OL` | `ACTION=OK | ARGUMENT=Y` | 26 | Weiter: setze den Posten. |
| `OL` | `ACTION=SH | ARGUMENT=Y` | 24 | Weiter: halte den Posten. |
| `SH+E+DY` | `ARGUMENT=AIIN` | 22 | Halte den Wert; auf Grad I; abschließen. |
| `OK+OL` | `ARGUMENT=Y` | 19 | Weiter: setze den Posten. |
| `SH+E+DY` | `ARGUMENT=AIN` | 18 | Halte den Anteil; auf Grad I; abschließen. |
| `OL` | `ACTION=CHD | ARGUMENT=Y` | 17 | Weiter: bearbeite den Posten. |
| `OL` | `ACTION=K | ARGUMENT=Y` | 15 | Weiter: gib den Posten. |
| `OK+E+OL` | `ARGUMENT=Y` | 14 | Weiter: setze den Posten; auf Grad I. |

## Arbeitsregel

Das Rezept liefert die sichtbaren Kürzel und ihre Reihenfolge. Der Selektor füllt nur die tatsächlich
offenen Handlungs- und Argumentslots. Er darf weder den Besitzer in einen Wortstamm zurückschreiben
noch eine neue Ganzwortbedeutung lernen. Diese Ausgabe benutzt keine neue Seite und ändert keinen Root.
