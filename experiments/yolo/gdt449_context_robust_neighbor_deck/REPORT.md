# GDT449 — Nur zehn Nachbarkarten sind wirklich kontextabhängig

## Ergebnis

Die 61.878 Einzelproben aus GDT448 fallen auf 25.576 gerichtete
Quell→Nachbar-Kanten:

| Robustheit über alle beobachteten Quellkontexte | Kanten |
|---|---:|
| immer grün | 21.970 |
| immer lesbar, teils gelb | 694 |
| lesbar oder Stopp, je nach Kontext | 10 |
| immer Stopp | 2.902 |

Damit bleiben 22.664 Kanten in allen bisher tatsächlich belegten Kontexten
lesbar. Das ist aber kein Auftretens- oder Identitätsbeleg: Es heißt nur, dass
der vorhandene Faktorenleser an diesen Stellen keinen Widerspruch erzeugt.

Die Änderungstypen unterscheiden sich deutlich:

- Atomlöschung: 4.527/4.612 überall lesbar, drei Mischfälle;
- Nachbartausch: 3.183/3.344 überall lesbar, kein Mischfall;
- Gleichklassen-Austausch: 14.954/17.620 überall lesbar, sieben Mischfälle.

Ein Austausch innerhalb derselben groben Klasse ist also keineswegs
automatisch sicher. Die roten Direktpaare bleiben der Hauptgrund für die 2.902
stabilen Stopps.

## Die zehn echten Warnkarten

Nur diese zehn gerichteten Kanten wechseln zwischen Lesen und Stopp:

```text
D_ADDR+EE+Y  -> D_ADDR+EEE+Y
OK+E+DY      -> E+DY
OK+EEE+Y     -> EEE+Y
OT+E+AIIN    -> OT+EEE+AIIN
OT+E+DY      -> OT+EEE+DY
OT+E+O       -> OT+EEE+O
OT+E+OR      -> OT+EEE+OR
OT+EE+DY     -> OT+EEE+DY
OT+EE+Y      -> OT+EEE+Y
SH+EE+DY     -> EE+DY
```

Sie führen nichts Neues ein. Acht Familien berühren die bekannten
Grad-III-Lücken `CHD←EEE` oder `R←EEE`; zwei verlieren durch Löschung ihren
sichtbaren Handlungskopf und funktionieren nur dort, wo ein Kopf geerbt wird.

## Zielrezept statt Lieblingsquelle

Mehrere Quellkarten können dasselbe Ziel erreichen. Deshalb wurde zusätzlich
über 18.381 verschiedene Zielrezepte aggregiert:

| Zielstatus | Zielrezepte |
|---|---:|
| immer grün | 15.467 |
| immer lesbar, teils gelb | 532 |
| kontextabhängig | 10 |
| immer Stopp | 2.372 |

Die zehn Ziel-Warnkarten sind:

```text
D_ADDR+EEE+Y, E+DY, EE+DY, EEE+Y, OT+EEE+AIIN,
OT+EEE+DY, OT+EEE+O, OT+EEE+OR, OT+EEE+Y, OT+O+DY
```

Diese Zielliste ist die bessere Lehrlingswarnung als eine einzelne
Quellkante. Besonders `E+DY`, `EE+DY` und `OT+O+DY` zeigen, warum eine
Schlussform niemals ohne den aktuellen Kopf gelesen werden darf.

## Praktische Regel

```text
Immer grün/lesbar = gute Vorprüfung, aber aktuellen Kontext erneut testen.
Mischfall = ohne Handlungskopf und Scope niemals lesen.
Immer Stopp = Zustand bewahren; keine Reparatur erfinden.
Exakte Identität = weiterhin ausschließlich vollständiger Zielschlüssel.
```

Selbst drei exakte Katalogziele stoppen in allen untersuchten Kontexten. Das
bestätigt nochmals: Bekanntheit einer Karte und Ausführbarkeit an einer Stelle
sind zwei verschiedene Fragen.

## Grenze

„Alle Kontexte“ meint alle 4.275 im aktuellen 26-Seiten-Strom beobachteten
Signaturen, nicht alle theoretisch denkbaren Zustände. Das Deck ist deshalb
ein schneller Sicherheitsfilter vor dem Echtzeitzertifikat, kein Ersatz dafür
und kein Generator für neue Schriftformen.
