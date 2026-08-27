# GDT561 – vollständiger typisierter Zustandskartenleser

## Ergebnis in einem Satz

Alle 1.656 bekannten Karten mit `OT`, `OL` oder `DY` besitzen nun eine links-nach-rechts erhaltene Standardlesung: 4.684/4.684 Atome sind über sieben Rollen und 36 kurze Arbeitswerte abgedeckt; kein Rezept benötigt einen neu gelernten Ganzkartenwert.

Das ist eine Arbeitskomposition, keine Entzifferung. Besonders `HIER`, `VARIANTE` und `KLASSE` bleiben Strukturmarken und werden nicht zu deutschen Wörtern im Manuskript erklärt.

## Umfang

- Karten: **1656**
- verschiedene exakte Rezepte: **402**
- Atomnennungen: **4684**
- verschiedene verwendete Atome: **36**
- geordnete Rollenmuster: **213**
- spezialisierte Grad-/Argument-/Relationslinks: **939** auf **787** Karten
- ungeordnete Atommengen mit mehreren Reihenfolgen: **18** (37 Rezepte, 102 Karten)

## Sieben Rollen

| Rolle | Atome | Nennungen | Karten |
|---|---:|---:|---:|
| HANDLUNG | 9 | 1158 | 950 |
| GRAD | 3 | 742 | 729 |
| ARGUMENT | 4 | 390 | 382 |
| RELATION | 4 | 216 | 212 |
| ZUSTANDSSTEUERUNG | 3 | 1870 | 1656 |
| FORMSTEUERUNG | 4 | 175 | 152 |
| LOKAL-/KLASSENZEICHEN | 9 | 133 | 124 |

## Häufigste geordnete Muster

| Rollenmuster | Karten | Rezepte | Beispiel |
|---|---:|---:|---|
| `ACTION_HEAD+GRADE+STATE_CONTROL` | 370 | 14 | `K+E+DY` |
| `STATE_CONTROL` | 191 | 2 | `OL` |
| `STATE_CONTROL+ARGUMENT` | 147 | 8 | `OL+AIIN` |
| `ACTION_HEAD+STATE_CONTROL` | 84 | 9 | `CHD+DY` |
| `STATE_CONTROL+GRADE+STATE_CONTROL` | 73 | 5 | `OT+E+DY` |
| `STATE_CONTROL+GRADE+ARGUMENT` | 49 | 6 | `OL+E+OR` |
| `STATE_CONTROL+RELATION` | 45 | 4 | `OL+AL` |
| `ACTION_HEAD+ACTION_HEAD+STATE_CONTROL` | 42 | 10 | `CH+K+OL` |
| `RELATION+ACTION_HEAD+STATE_CONTROL` | 40 | 2 | `AL+CHD+DY` |
| `STATE_CONTROL+ACTION_HEAD+STATE_CONTROL` | 33 | 4 | `OL+CHD+DY` |
| `STATE_CONTROL+ACTION_HEAD+GRADE+STATE_CONTROL` | 31 | 8 | `OL+CH+EE+DY` |
| `STATE_CONTROL+STATE_CONTROL` | 31 | 3 | `OL+DY` |

## Häufigste exakte Rezepte

| Rezept | Karten | vollständiger Default |
|---|---:|---|
| `OL` | 189 | weiter |
| `SH+E+DY` | 119 | halten; auf Grad I; abschließen |
| `OK+EE+DY` | 83 | setzen; auf Grad II; abschließen |
| `OK+E+DY` | 79 | setzen; auf Grad I; abschließen |
| `OT+Y` | 40 | danach; den Posten |
| `OT+E+DY` | 37 | danach; auf Grad I; abschließen |
| `L+CHD+DY` | 35 | über die Verbindung; bearbeiten; abschließen |
| `OL+Y` | 33 | weiter; den Posten |
| `OK+OL` | 28 | setzen; weiter |
| `OT+EE+DY` | 28 | danach; auf Grad II; abschließen |
| `SH+OL` | 27 | halten; weiter |
| `OT+AR` | 24 | danach; vom Ausgang |

## Warum die Reihenfolge stehenbleibt

Es gibt 18 Atommengen, die in mehr als einer geschriebenen Reihenfolge vorkommen. Zusammen betreffen sie 37 Rezepte und 102 Karten. `OL+Y` und `Y+OL` erhalten deshalb nicht denselben Schlüssel: der erste Default lautet „weiter; den Posten“, der zweite „den Posten; weiter“. Das Wörterbuch liefert die Bestandteile; das Rezept liefert ihre Anordnung.

## Leseregel

1. Jedes Atom behält seinen kurzen Wert und seine strukturelle Rolle.
2. Die Atome werden exakt in geschriebener Reihenfolge wiedergegeben.
3. Grad, Argument und Relation übernehmen zusätzlich die engere Trägerlesung aus GDT558–GDT560, wo eine solche vorliegt.
4. Die kontextuelle Satzzeile aus GDT416/GDT539 bleibt daneben sichtbar; sie darf die atomare Spur nicht überschreiben.
5. Ein Rezeptdefault gilt nur für das bereits beobachtete exakte Rezept. Er erzeugt keine neue Voynichform.

## Was jetzt wirklich noch offen ist

Die Abdeckung ist nicht mehr das Problem: jede Karte ist lesbar. Offen ist die Qualität der Komposition. Besonders Karten ohne sichtbare Handlung, reine Steuerkarten und seltene Form-/Lokalzeichen müssen nun danach sortiert werden, ob ihre vollständige Defaultphrase wie eine Initialisierung, Fortsetzung, Referenz oder Abschlusszeile klingt. Dafür ist kein neuer Grundwortwert nötig; der nächste Pass kann auf den 1.656 fertigen Zeilen arbeiten.
