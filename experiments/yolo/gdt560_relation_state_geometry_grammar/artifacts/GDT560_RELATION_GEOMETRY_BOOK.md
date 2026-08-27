# GDT560 — Relations-Geometriebuch

Die vier Wurzeln bleiben kurz: `AL=ZIELORT`, `AR=AUSGANG`, `L=VERBINDUNG`, `AIR=BAHN`. Anders als die vier Argumente bilden sie im Zustandsstrom kein einheitliches Viererfach. Alle216 Stellen erhalten dennoch eine der8 geschriebenen Kontrollhüllen und eine kurze Defaultlesung.

## Vier verschiedene Geometrien

| Wurzel | Wert | Stellen | links vom Block | rechts vom Block | Handlung rechts | OT/OL links | DY/OL rechts |
|---|---|---:|---:|---:|---:|---:|---:|
| `AL` | ZIELORT | 60 | 45 | 39 | 10 | 37 | 25 |
| `AR` | AUSGANG | 58 | 35 | 50 | 2 | 47 | 13 |
| `L` | VERBINDUNG | 92 | 86 | 33 | 58 | 5 | 85 |
| `AIR` | BAHN | 6 | 2 | 3 | 0 | 3 | 3 |

AR ist der deutlichste rechte Ausgang:50/58 Stellen beenden ihren lokalen Inhalt und47 liegen nach OT/OL. L ist das Gegenbild:86/92 eröffnen den lokalen Inhalt,58 zeigen rechts eine Handlung und85 laufen in DY/OL. AL besetzt beide Seiten und verbindet die Ausgangs- mit der Verbindungsgeometrie. AIR bleibt mit6 Stellen und0 Zustands-Austauschfamilien ein eigener seltener Bahntyp.

## Acht vollständige Kontrollhüllen

| Hülle | Stellen | AL | AR | L | AIR | Default |
|---|---:|---:|---:|---:|---:|---|
| `START>R<DY` | 91 | 19 | 5 | 64 | 3 | REL · ABSCHLIESSEN |
| `OT>R<END` | 62 | 26 | 34 | 1 | 1 | DANACH · REL |
| `START>R<OL` | 31 | 4 | 6 | 21 | 0 | REL · FORTSETZEN |
| `OL>R<END` | 26 | 9 | 11 | 4 | 2 | FORTSETZEN · REL |
| `DY>R<END` | 2 | 0 | 0 | 2 | 0 | ABSCHLIESSEN · REL |
| `OT>R<DY` | 2 | 1 | 1 | 0 | 0 | DANACH · REL · ABSCHLIESSEN |
| `OL>R<DY` | 1 | 1 | 0 | 0 | 0 | FORTSETZEN · REL · ABSCHLIESSEN |
| `OL>R<OL` | 1 | 0 | 1 | 0 | 0 | FORTSETZEN · REL · FORTSETZEN |

## Zwölf Austauschfamilien, aber kein Viererfach

| Familie | Rezept | Varianten | Karten | final |
|---|---|---|---:|---:|
| G560-F01 | `REL+OL` | AL|AR|L | 18 | 0 |
| G560-F02 | `OT+REL` | AL|AR | 41 | 0 |
| G560-F03 | `REL+CHD+DY` | AL|L | 40 | 40 |
| G560-F04 | `REL+DY` | AL|L | 12 | 12 |
| G560-F05 | `REL+SH+E+DY` | AL|L | 11 | 11 |
| G560-F06 | `OL+K+REL` | AL|AR | 4 | 0 |
| G560-F07 | `OL+REL` | AL|AR | 4 | 0 |
| G560-F08 | `OT+REL+Y` | AL|AR | 4 | 0 |
| G560-F09 | `REL+OL+Y` | AR|L | 4 | 0 |
| G560-F10 | `OK+REL+DY` | AL|AR | 2 | 2 |
| G560-F11 | `OT+E+REL` | AL|AR | 2 | 0 |
| G560-F12 | `OT+REL+DY` | AL|AR | 2 | 2 |

AL↔AR teilen8 Zustandsfamilien, AL↔L vier und AR↔L zwei. AL ist damit das Gelenk. Kein AIR-Paar besitzt in diesem Zustandsausschnitt eine exakte Austauschfamilie. Die67 Familienkarten mit DY schließen67/67 Aussagen; die77 ohne DY schließen0/77. Der Relationswechsel ändert also den Kontrollschluss nicht.

## Zwei sichtbare Nachschluss-Verbindungen

`OT+E+DY+L` und `OK+CHD+DY+L` schreiben den ungewöhnlichen Ablauf `ABSCHLIESSEN · VERBINDUNG`. Beide sind aussagefinal. L wird hier nicht über DY zurückgebunden, sondern bleibt als sichtbarer Verbindungsschwanz nach dem geschlossenen Schritt stehen.

## Alle28 Relations-Steuerfolgen

| Folge | Karten | final | Default |
|---|---:|---:|---|
| `L+DY` | 64 | 64 | VERBINDUNG · ABSCHLIESSEN |
| `OT+AR` | 33 | 0 | DANACH · AUSGANG |
| `OT+AL` | 25 | 0 | DANACH · ZIELORT |
| `L+OL` | 18 | 0 | VERBINDUNG · FORTSETZEN |
| `AL+DY` | 17 | 17 | ZIELORT · ABSCHLIESSEN |
| `OL+AR` | 10 | 0 | FORTSETZEN · AUSGANG |
| `OL+AL` | 8 | 1 | FORTSETZEN · ZIELORT |
| `AR+OL` | 6 | 0 | AUSGANG · FORTSETZEN |
| `AL+OL` | 4 | 0 | ZIELORT · FORTSETZEN |
| `AIR+DY` | 3 | 3 | BAHN · ABSCHLIESSEN |
| `AR+DY` | 3 | 3 | AUSGANG · ABSCHLIESSEN |
| `OL+L` | 3 | 0 | FORTSETZEN · VERBINDUNG |
| `L+OL+OL` | 2 | 0 | VERBINDUNG · FORTSETZEN · FORTSETZEN |
| `OL+AIR` | 2 | 0 | FORTSETZEN · BAHN |
| `AL+AL+DY` | 1 | 1 | ZIELORT · ZIELORT · ABSCHLIESSEN |
| `AR+AR+DY` | 1 | 1 | AUSGANG · AUSGANG · ABSCHLIESSEN |
| `DY+L` | 1 | 1 | ABSCHLIESSEN · VERBINDUNG |
| `L+OL+DY` | 1 | 1 | VERBINDUNG · FORTSETZEN · ABSCHLIESSEN |
| `OL+AL+DY` | 1 | 1 | FORTSETZEN · ZIELORT · ABSCHLIESSEN |
| `OL+AR+L` | 1 | 0 | FORTSETZEN · AUSGANG · VERBINDUNG |
| `OL+AR+OL` | 1 | 0 | FORTSETZEN · AUSGANG · FORTSETZEN |
| `OT+AIR` | 1 | 0 | DANACH · BAHN |
| `OT+AL+AR` | 1 | 0 | DANACH · ZIELORT · AUSGANG |
| `OT+AL+DY` | 1 | 1 | DANACH · ZIELORT · ABSCHLIESSEN |
| `OT+AR+DY` | 1 | 1 | DANACH · AUSGANG · ABSCHLIESSEN |
| `OT+DY+L` | 1 | 1 | DANACH · ABSCHLIESSEN · VERBINDUNG |
| `OT+L` | 1 | 0 | DANACH · VERBINDUNG |
| `OT+OL+AL` | 1 | 0 | DANACH · FORTSETZEN · ZIELORT |

Die zusätzliche44-Zeilen-Tabelle hält jede geschriebene Relation-Argument-Steuerfolge fest. Nur16/216 Relationsstellen berühren überhaupt ein explizites Argument in derselben Kontrollhülle; die Relation ist daher meist ein Kontextlink und keine ausgeschriebene binäre Klammer zwischen zwei Nomen.

## Arbeitsgrenze und nächster Schritt

Dies ist eine vollständige Arbeitsbelegung vorhandener Wurzeln. Sie ändert keine Bedeutung oder Seite. Als nächstes können Handlung, Grad, Relation, Argument und Kontrolle zu einer einzigen typisierten Zustandskarte zusammengesetzt werden; dafür wird weiterhin keine neue Seite geöffnet.
