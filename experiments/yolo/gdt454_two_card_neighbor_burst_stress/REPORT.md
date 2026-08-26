# GDT454 — Auch zwei gleichzeitige Kartenänderungen bleiben beherrschbar

## Ergebnis

Aus 5.283 festen Nachbarvarianten und 3.861 wirklichen Quellkartenpaaren
entstehen 34.205 Zweierbursts:

| Karte 1 | Karte 2 | Bursts |
|---|---|---:|
| lesbar | lesbar | 25.754 |
| lesbar | Stopp | 3.719 |
| Stopp | lesbar | 4.095 |
| Stopp | Stopp | 637 |

Jeder Stopp in beiden Positionen bewahrt Handlung und Argument. Eine gestoppte
erste Karte vergiftet die zweite also nicht; eine lesbare erste Karte liefert
ihren wirklichen neuen Zustand an die zweite.

## Die echte dritte Karte

5.962 Paare enden mit Karte zwei und haben keine dritte Karte derselben
Aussage. In den übrigen 28.243 Fällen:

- 28.190 dritte Karten lesen grün;
- 50 lesen gelb;
- drei stoppen.

Die drei Stopps sind wieder kein Parserverlust, sondern drei Varianten eines
einzigen f72r-Paares. Beide gewählten Zielkarten sind lesbar, aber beide haben
den Quellkopf `P` entfernt. Die echte dritte Karte ist `EEE+DY` und darf ohne
Kopf nicht schließen:

```text
EE+OT+Y | AR+AR | EEE+DY  -> drittes Feld STOP
EE+Y    | AR+AR | EEE+DY  -> drittes Feld STOP
OL+EE+Y | AR+AR | EEE+DY  -> drittes Feld STOP
```

Alle drei lesen am nächsten Aussagenanfang `CH+E` wieder grün.

## Bedeutung für den Seitendurchsatz

Der Intake ist nicht nur gegen einen einzelnen fremden Baustein robust. Er
trägt zwei veränderte Karten sequenziell, unterscheidet vier mögliche
Lesen/Stopp-Verläufe und synchronisiert nach dem einzigen abhängigen
Kopfverlust wieder. Damit kann eine spätere Seite mehrere unbekannte
Kompositionen nebeneinander enthalten, ohne dass ein früher Stopp still den
Rest der Aussage autorisiert oder zerstört.

Der Test erzeugt keine dieser Formen und bestätigt weiterhin kein Wort.
