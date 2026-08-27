# GDT556 — `DY` ist tatsächlich der Abschlussmarker

Status: `PASS_DY_702_OF_705_STATEMENT_FINAL__THREE_LOCAL_STEP_CLOSURES`

## Ergebnis

Der vollständige Lauf über 5.122 Ereignisse und 793 Aussagen auf den 30 bereits
zugelassenen Seiten ergibt ein ungewöhnlich klares Bild:

- `DY` erscheint 705-mal in 703 Aussagen;
- 215 Vorkommen bilden eine Ein-Karten-Aussage;
- 487 stehen als letzte Karte einer längeren Aussage;
- nur drei stehen im Inneren einer weiterlaufenden Aussage;
- damit liegen 702/705 beziehungsweise 99,574468 Prozent am Aussageende;
- unter den 4.417 Nicht-`DY`-Ereignissen enden nur 2,060222 Prozent eine
  Aussage.

Auch die getrennten Kohorten stimmen überein. Im alten 26-Seiten-Präfix stehen
636/639 `DY` am Aussageende; die drei internen Fälle liegen alle dort. Auf den
vier aktuellen Seiten stehen 66/66 am Aussageende. Das ist die bisher stärkste
direkte Positionsstützung eines unserer portablen Bedeutungswerte.

## Abschluss von Schritt oder Aussage

Der bessere Default lautet jetzt präzise:

```text
DY = den aktuellen Schritt abschließen
am Aussageende: zugleich die Aussage abschließen
im Aussageinneren: lokaler Schrittabschluss, danach weiter
```

Die drei internen Rezepte sind jeweils einmalig:

- `Y+DY+D_LABEL` auf f1r schließt einen Postenschritt vor einer lokalen
  Kennung; danach folgen noch 26 Karten;
- `D_ADDR+O+DY+D_LABEL` auf f55v schließt einen Ausführungsschritt vor einer
  lokalen Kennung; drei Karten später endet die Aussage mit einem zweiten
  `DY`;
- `OK+EE+DY+OL` auf f75r sagt sichtbar „setzen, Grad II, abschließen,
  fortsetzen“; drei Karten später folgt wiederum der Aussageabschluss.

Gerade `DY+OL` ist semantisch nützlich: „abschließen“ und „fortsetzen“ sind
nicht widersprüchlich, wenn das erste den lokalen Schritt und das zweite den
laufenden Satz betrifft.

## Position innerhalb der Karte

`DY` steht in 700/705 Rezepten als letztes Atom. Die fünf Nachträge sind eng
begrenzt:

- zweimal `D_LABEL`;
- zweimal `L`;
- einmal `OL`.

Die beiden `D_LABEL`- und das `OL`-Vorkommen sind genau die drei internen
Schlüsse. Die zwei `L`-Nachträge stehen trotzdem am Aussageende. `DY` ist damit
kein ausnahmslos letztes Schriftatom, aber ein nahezu terminaler funktionaler
Slot, hinter dem nur eine lokale Kennung, Verbindung oder Fortsetzung hängt.

## Vergleich mit anderen Markern

Kein anderer geprüfter Kontrollwert zeigt annähernd dieselbe
Aussageendbindung:

| Marker | Vorkommen | am Aussageende |
|---|---:|---:|
| `DY` | 705 | 99,574468 % |
| `E` | 1.106 | 31,283906 % |
| `EE` | 538 | 30,855019 % |
| `EEE` | 30 | 23,333333 % |
| `OT` | 404 | 22,524752 % |
| `OL` | 747 | 11,914324 % |
| `O` | 791 | 9,987358 % |
| `DA` | 42 | 9,523810 % |

Die 151 exakten `DY`-Rezepte wechseln nie zwischen internem Lokalabschluss und
Aussageabschluss. Die drei internen Rezepte sind jeweils eigene einmalige
Erweiterungen. 41 häufigere Rezepte variieren nur zwischen einer alleinstehenden
Abschlusskarte und der letzten Karte einer längeren Aussage — beides bleibt
Aussageabschluss.

Alle 29 Prüfungen bestehen. Die alten gemischten TSV-Quellen wurden nur durch
die explizite 26-Seiten-Allow-Liste gelesen; kein verbotener Selektor wurde
materialisiert. Keine Aussagegrenze, Rezeptfolge, Stamm­bedeutung oder deutsche
Lesung wurde geändert.

## Nächster Griff

`DY` braucht vorerst keine neue Bedeutung. Als Nächstes lohnt sich die
komplementäre Positionsprüfung von `OL=FORTSETZEN` und `OT=DANACH`: Der erste
steht überwiegend im Aussageinneren und oft am Kartenende, der zweite fast nie
am Kartenende. Zusammen könnten sie mit `DY` ein kleines, vorhersagbares
Start-/Weiter-/Schluss-System bilden.
