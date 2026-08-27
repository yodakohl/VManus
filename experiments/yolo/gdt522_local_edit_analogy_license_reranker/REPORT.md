# GDT522 — Alte Nachbarformen sagen lokale Rezeptänderungen voraus

## Ergebnis

Die nächste brauchbare Schicht ist keine weitere Ganzwortliste. Sie ist eine
Sammlung lokaler Analogien: Wenn eine alte sichtbare Form durch einen kleinen
Einschub aus einer anderen alten Form entsteht, fragt GDT522, welcher kleine
Einschub gleichzeitig im Komponentenrezept erscheint.

Das bringt zwei aktuelle Restfälle ohne Verlust eines bisherigen Treffers:

- `dcheol`: `D_ADDR+CH+E+OL` → **`D_ADDR+CH+E+O+L`**;
- `dyky`: `Y+K+Y` → **`D_ADDR+Y+K+Y`**.

Alle 140 bisherigen aktuellen Top-1-Treffer bleiben erhalten. Damit steigt
der aktuelle Stand auf 142 von 159.

## Gesamtwirkung

| Deck | Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---|---:|---:|---:|---:|---:|---:|
| vier rotierende Altgruppen | GDT521 | 1.090 | 1.325 | 1.387 | 1.418 | 2.118 | 22 |
| vier rotierende Altgruppen | GDT522 | **1.096** | **1.327** | 1.386 | 1.418 | **2.113** | 22 |
| aktuelle 159 Formen | GDT521 | 140 | 154 | 158 | 158 | 189 | 9 |
| aktuelle 159 Formen | GDT522 | **142** | 154 | 158 | 158 | **187** | 9 |

Im alten Vierfachlauf werden 14 frühere Fehler korrigiert und acht frühere
Treffer verloren: netto sechs zusätzliche Rang-1-Treffer. Der einzelne
Top-3-Rückgang bleibt sichtbar; die Rangsumme verbessert sich um fünf.

## Warum die Analogie konkret funktioniert

Für `dcheol` findet das Modell den alten direkten Nachbarn `dcheo`. Der
rechte Einschub ist eindeutig:

```text
dcheo + l  ->  altes Rezept + L
12 von 12 beobachteten rechten l-Analogien
```

Damit wird das atomare Ende `O+L` gegenüber dem Ganzrenderer `OL` bevorzugt.

Für `dyky` ist der nächste alte Nachbar `yky`:

```text
yky + linkes d  ->  D_ADDR + altes Rezept
32 von 47 linken d-Relationen; geglättete Wahrscheinlichkeit 0,657
```

Das liefert genau den bisher fehlenden Anfang `D_ADDR`, ohne `dyky` als
Sonderwort zu speichern.

## Der wichtige negative Fund: sichtbare Nullstücke

GDT522 erlaubt ausdrücklich, dass eine sichtbare Einfügung kein zusätzliches
Rezeptatom trägt. Das ist kein Randphänomen. Im alten Vollmodell stehen unter
anderem:

- linkes `q → NULL`: 75 von 84 Relationen;
- linkes `ch → NULL`: 29 von 88;
- inneres `ch → NULL`: 22 von 67;
- inneres `e → NULL`: 19 von 117;
- inneres `d → NULL`: 16 von 56;
- linkes `d → NULL`: 12 von 47.

Damit ist jetzt als Arbeitsregel ausdrücklich modelliert, dass sichtbare
Zeichenfolgen teils rendererische Erweiterungen sein können und nicht für
jedes Zeichen ein eigenes Bedeutungsatom erfunden werden muss.

Das erklärt aber `qef` noch nicht automatisch: `qef` besitzt keinen alten
bekannten Löschungsnachbarn innerhalb von drei Zeichen, über den sein
`q → NULL` aktiviert werden könnte. Die globale Nullregel ist vorhanden, die
lokale Brücke zur unbekannten Restform `ef` fehlt.

## Warum das erste Rohmodell verworfen wurde

Eine bloße Häufigkeitsbelohnung bevorzugte bei `psheody` den häufigen inneren
Einschub `o → O` über den selteneren linken Einschub `p → P` und zerstörte so
einen bereits gewonnenen Treffer. Das ausgewählte Modell bewertet deshalb die
bedingte Eindeutigkeit: `p` links bildet in 15 von 15 alten Relationen auf `P`
ab, während inneres `o` mehrere Rezeptmöglichkeiten besitzt. `psheody` bleibt
dadurch korrekt.

## Offene 17 Formen und nächster Griff

Die verbleibenden Top-1-Fehler sind:

`aiicthy`, `chady`, `chap`, `chekchy`, `cthom`, `dairykodas`,
`dalcheeeky`, `dsholdaiir`, `kchody`, `kechody`, `keeol`, `keody`, `ld`,
`okedals`, `qef`, `qocthedy`, `saiis`.

Der nächste sinnvolle Ausbau ist zweigeteilt:

1. Null- und lokale Editlizenzen direkt auf die Renderer-Ausrichtung anwenden,
   auch wenn die nach Löschung verbleibende Oberfläche noch kein bekanntes
   altes Ganzformular ist. Das zielt besonders auf `qef`.
2. Für die bekannten Nachbarfälle mehrere kompatible lokale Änderungen
   zusammensetzen, statt nur genau einen Einschub zu bewerten. Das zielt auf
   `kchody`, `kechody`, `keeol`, `ld` und `okedals`, ohne sie als Vollformen
   einzutragen.

Bekannte Ereignis- und Oberflächenkarten behalten Vorrang. Die 1.081
Signaturen sind ein Arbeitsmodell der Schreib-/Kompositionsmechanik, noch kein
Beweis für Wörter, Sprache oder Klartext.
