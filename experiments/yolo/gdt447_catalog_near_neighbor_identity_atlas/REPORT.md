# GDT447 — Nahe Form ist nicht dieselbe Karte

## Ergebnis

Der exakte Identitätskanal hält über 30.763 begrenzte Nachbaränderungen:

- 5.499 Atomlöschungen;
- 3.936 Tausche benachbarter ungleicher Atome;
- 21.328 Austausche innerhalb derselben portablen Kernklasse;
- 0 unscharfe Identitätstreffer;
- 0 mitgetragene Quellidentitäten;
- 0 verwendete Fuzzy-Regeln.

Ein Ziel erhält genau dann eine Katalogidentität, wenn seine vollständige
geordnete Komponentenfolge selbst unter den 1.563 Schlüsseln steht.

## Wie dicht liegt der Katalog wirklich?

Von den 30.763 gerichteten Nachbarn landen 6.372 wieder auf einem Katalogkey.
Sie erreichen 1.073 verschiedene exakte Zielschlüssel; 1.313 der 1.563
Quellschlüssel haben mindestens einen exakten Nachbarn.

Die drei Änderungstypen unterscheiden sich deutlich:

| Änderung | Nachbarn | exakte Ziele | neue Ziele |
|---|---:|---:|---:|
| Atom löschen | 5.499 | 2.278 | 3.221 |
| Nachbarn tauschen | 3.936 | 198 | 3.738 |
| gleiche Klasse einsetzen | 21.328 | 3.896 | 17.432 |

Das ist ein dichtes Paradigmenfeld, aber keine unscharfe Schriftidentität.
Gerade der Tausch ist nützlich: Nur 198 Tausche treffen einen anderen exakten
Schlüssel. Reihenfolge bleibt deshalb fast immer identitätsentscheidend.

## Identität und Lesbarkeit bleiben verschieden

24.391 Nachbarzeilen sind keine Katalogschlüssel. Trotzdem entscheidet der
unabhängige Faktorenkanal:

- 19.792 grün lesbar;
- 941 gelb lesbar;
- 3.658 Stopp.

Das ist kein Leck. Die Identität bleibt bei allen 24.391 `NEW_VISIBLE_RECIPE`;
nur ihre bereits sichtbaren alten Komponenten können nach Auftreten gelesen
werden. Genau dadurch wird erneut sichtbar, warum der Faktorenleser kein
Vorkommensgenerator sein darf.

Auch die 6.372 exakten Zielzeilen werden separat ausgeführt: 6.107 grün, 179
gelb und 86 im neutralen Kontext gestoppt. Ein Katalogtreffer überstimmt also
auch hier weder lokalen Rand noch fehlenden Kopf.

## Kollisionsatlas

Die 30.763 Kanten fallen auf 19.807 unterschiedliche Zielrezepte. 3.955 Ziele
werden aus mehr als einer Quellkarte erreicht; das dichteste Ziel hat 39
verschiedene Quellen. Dennoch erhält kein neues Ziel eine Identität durch
Mehrheitsnähe. Quellenzahl und Ähnlichkeit sind keine Schlüssel.

## Lehrregel

```text
Exakte Identität = vollständige geordnete Zielkarte im Katalog.
Nahe Quelle, gleicher Satzwert, viele Nachbarn oder gleiche Klasse zählen nicht.
Danach und davon getrennt entscheidet der Faktorenkanal über Ausführung.
```

Damit ist die zweite mögliche Aufnahmeleckstelle geschlossen. Der nächste
sinnvolle geschlossene Test setzt dieselben Nachbarn in die echten eingehenden
Zustände der 4.576 aktuellen Ereignisse. So lässt sich messen, welche
Kompositionen in realistischen Positionen grün, gelb oder rot wären, ohne eine
neue Seite zu öffnen.
