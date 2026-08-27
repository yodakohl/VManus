# GDT523 — Nullkarten direkt im Rendererpfad

## Ergebnis

GDT522 konnte eine Nullbeziehung nur benutzen, wenn eine neue Form nach einer
kleinen Löschung auf eine bekannte alte Ganzform fiel. GDT523 entfernt diese
Abhängigkeit. Es liest stattdessen die konkrete Renderer-Spur. Zum Beispiel
enthält die Zielanalyse von `qef`:

```text
qe => e ~ E
```

Das sichtbare linke `q` ist hier genau eine Einfügung gegenüber dem alten
Alias `e`. Diese Einfügung kann nun direkt die alte Nullkarte ansprechen, auch
wenn `ef` selbst keine alte bekannte Ganzform ist.

## Ausgewählte leichte Wirkung

| Deck | Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---|---:|---:|---:|---:|---:|---:|
| vier rotierende Altgruppen | GDT522 | 1.096 | 1.327 | 1.386 | 1.418 | 2.113 | 22 |
| vier rotierende Altgruppen | GDT523 | 1.096 | 1.327 | **1.387** | 1.418 | **2.111** | 22 |
| aktuelle 159 Formen | GDT522 | 142 | 154 | 158 | 158 | 187 | 9 |
| aktuelle 159 Formen | GDT523 | 142 | 154 | 158 | 158 | 187 | 9 |

Im alten Vierfachlauf steigt `qopchy` von Rang 4 auf 3 und `qopchey` von Rang
9 auf 8. Kein alter oder aktueller Top-1-Treffer kippt unter der ausgewählten
Gewichtung. Auf den aktuellen 159 Formen bleibt die Rangordnung vollständig
gleich.

## Weshalb die Karte atomkonditioniert ist

Die globale alte Paarfamilie sagt zunächst: linkes `q→NULL` in 75 von 84
Relationen. Das reicht nicht, denn andere Fälle brauchen `CARRIER_Q`.
Konditioniert auf das erste Rezeptatom wird die Trennung deutlich:

- vor `OK`: 33 Nullrelationen, eine andere;
- vor `OL`: 11 zu 0;
- vor `OT`: 21 zu 1;
- vor `O`: 4 zu 7, also **keine** Nullfreigabe;
- vor `E`: 1 zu 0, aber nur ein alter Nachbarbeleg.

Die ausgewählte Regel fordert sowohl global als auch in diesem Atomkontext
eine Nullmehrheit. Sie belohnt dann nur ein Viertel der zuverlässig
zurückgewonnenen sichtbaren Editbreite; die Log-Odds selbst werden nicht in
den Live-Score aufgenommen.

## `qef`: erklärt, aber bewusst nicht erzwungen

Im alten-26-zu-neuen-4-Benchmark bleibt:

```text
GDT523 leicht:  CARRIER_Q+E+LOCAL_CHAR_F  (Rang 1)
Arbeitsziel:     E+LOCAL_CHAR_F            (Rang 2)
```

Eine kombinierte Pfadgewichtung von 0,85 würde `qef` tatsächlich auf Rang 1
heben und die aktuellen 159 von 142 auf 143 verbessern. Im alten Vierfachlauf
fällt sie jedoch von 1.096 auf 1.089 Rang-1-Treffer und verschlechtert die
Rangsumme von 2.113 auf 2.123. Der Grund ist kein Rätsel: In kleineren
Trainingsgruppen kippen dünn belegte `q`-Atomkontexte, und echte
`CARRIER_Q`-Formen werden als Nullrenderer gelesen.

Darum bleibt die starke Variante im `gdt523_q_path_tradeoff_atlas.tsv`, aber
nicht im Default. Die konkrete `qef`-Spur ist jetzt mechanisch erklärt; ihre
Stärke reicht allein noch nicht für eine übertragbare Auswahlregel.

## Was das für das Mischcodebuch bedeutet

Die Nullkarten sind realer Bestandteil des Arbeitsmodells: ein sichtbares
Zeichen kann innerhalb eines gelernten Renderers stehen, ohne ein zusätzliches
Komponentenatom auszulösen. Aber `q` ist kein universelles Nullzeichen. Seine
Rolle hängt mindestens vom folgenden Rezeptstamm ab. Das unterstützt gerade
die gesuchte Mischung aus produktiven Kürzeln und gelernten Renderern.

Siebzehn aktuelle Top-1-Fehler bleiben. Der nächste produktive Griff ist nun
nicht mehr ein stärkeres `q`-Gewicht, sondern die Komposition zweier bereits
belegter lokaler Änderungen. Kandidaten dafür sind `kchody`, `kechody`,
`keeol`, `ld` und `okedals`. Ziel bleibt eine wiederverwendbare Zwei-Schritt-
Karte, keine Vollformausnahme und keine neue Seite.
