# GDT557 — Drei-Zustands-Grammatik über 30 Seiten

Die drei kurzen Komponenten bilden im Arbeitsmodell kein Synonymfeld, sondern einen kleinen Ablaufapparat: `OT` eröffnet oder verschiebt auf den nächsten Träger, `OL` hält den laufenden Träger aktiv, `DY` schließt den laufenden Schritt. Die Atomreihenfolge bleibt die Ausführungsreihenfolge.

## Gesamtprofil

| Komponente | Vorkommen | rechts ein Träger | links ein Träger | Karten am Satzende | Arbeitsoperation |
|---|---:|---:|---:|---:|---|
| OT | 404 | 402 (99.504950%) | 25 (6.188119%) | 91/404 (22.524752%) | nächsten Träger eröffnen |
| OL | 761 | 284 (37.319317%) | 373 (49.014455%) | 89/747 (11.914324%) | laufenden Träger fortsetzen |
| DY | 705 | 5 (0.709220%) | 705 (100.000000%) | 702/705 (99.574468%) | laufenden Schritt abschließen |

OT ist damit fast vollständig rechtsgerichtet, OL absichtlich beweglich und DY fast vollständig links- und schlussgerichtet. Das sind verschiedene Slots derselben kleinen Prozessgrammatik.

## Beobachtete Zustandsfolgen

| Folge | Karten | Arbeitslesung | Klasse |
|---|---:|---|---|
| `OL` | 619 | laufenden Träger fortsetzen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `DY` | 544 | laufenden Schritt abschließen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `OT` | 279 | nächsten Träger eröffnen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `OT+DY` | 86 | nächsten Träger eröffnen; dann laufenden Schritt abschließen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `OL+DY` | 74 | laufenden Träger fortsetzen; dann laufenden Schritt abschließen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `OT+OL` | 38 | nächsten Träger eröffnen; dann laufenden Träger fortsetzen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `OL+OL` | 14 | laufenden Träger fortsetzen; dann laufenden Träger fortsetzen | DOMINANT_START_CONTINUE_CLOSE_ORDER |
| `DY+OL` | 1 | laufenden Schritt abschließen; dann laufenden Träger fortsetzen | REVERSE_LOCAL_COMPOSITION |
| `OL+OT` | 1 | laufenden Träger fortsetzen; dann nächsten Träger eröffnen | REVERSE_LOCAL_COMPOSITION |

Die häufigen Doppeloperationen laufen fast vollständig in der Richtung Eröffnen → Fortsetzen → Schließen: OT→OL 38/39, OT→DY 86/86 und OL→DY 74/75. Es gibt keine Dreierkarte und kein DY→OT.

Noch deutlicher ist der Abschalteeffekt: Die 704 Folgen, deren letzter Zustandsoperator DY ist, stehen 702-mal am Aussageende (99,715909%). Von 951 operierten Karten ganz ohne DY stehen nur 20 am Aussageende (2,103049%). `OT+DY` endet 86/86-mal, `OL+DY` 74/74-mal, während `OT+OL` 0/38-mal endet. DY ist damit im Arbeitsleser der Schließschalter, nicht bloß ein häufiges Schlusswort.

## Die zwei umgekehrten Kompositionen

- `G407-E0034` / `roloty` / `R+OL+OT+Y`: laufenden Träger fortsetzen; dann nächsten Träger eröffnen.
- `G407-E1682` / `okeedyqol` / `OK+EE+DY+OL`: laufenden Schritt abschließen; dann laufenden Träger fortsetzen.

Diese zwei Karten widerlegen nicht die Komponenten. Sie zeigen, dass die Befehle wirklich komponieren: OL→OT heißt erst den laufenden Träger halten und danach einen neuen eröffnen; DY→OL heißt den lokalen Schritt schließen und anschließend weiterführen.

## Transfer

Alle 28 Seiten mit laufenden Karten enthalten OT, OL und DY. Die zwei zusätzlich zugelassenen alten Lokal-Seiten besitzen in dieser Edition keine laufenden Karten und werden als solche ausgewiesen. Gegenüber dem 69-Slot-Keim von GDT478 wächst der Test auf 1870 Operatorvorkommen in 1656 Karten; die Rollen bleiben erhalten, werden aber um DY und die zwei seltenen Umkehrfolgen ergänzt.

## Arbeitsleser

1. Lies die übrigen Komponenten der Karte in ihrer vorhandenen Reihenfolge.
2. Bei `OT` eröffne den rechts folgenden Träger; steht OT allein, kommt dieser Träger aus dem Satzkontext.
3. Bei `OL` halte den linken Träger, führe ihn in den rechten weiter oder nimm rechts einen fortzusetzenden Träger auf.
4. Bei `DY` schließe den linken Schritt. Nur wenn danach noch ein Atom steht, lies es als Nachtrag oder als ausdrückliche Fortsetzung.
5. Steht DY auf der letzten Karte, schließt der Schritt zugleich die Aussage; in drei internen Karten nur den lokalen Schritt.

## Grenze

Das ist eine vollständige Arbeitsgrammatik für die drei bereits gesetzten Komponenten in den vorhandenen Rezepten. Sie ändert keine Bedeutung, Segmentierung, Karte oder Aussagegrenze und behauptet weder historischen Klartext noch eine identifizierte Sprache oder ein identifiziertes Codebuch.
