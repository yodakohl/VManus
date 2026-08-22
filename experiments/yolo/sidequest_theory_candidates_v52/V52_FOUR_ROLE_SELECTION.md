# V52 — Feldgrammatik: Struktur ja, Satzkomposition nein

## Auswahl

Alle vier Rollen kommen zum selben Haupturteil:

> Die V50/V51-Werte ergeben eine lehrbare **parataktische Karten- und
> Feldnotation**, aber keine rekonstruierte Satz- oder Rezeptgrammatik.

Der einzige feldweite harte Bau ist:

```text
FIELD := NONCLOSE* TERMINAL?
```

Alle 90 `CLOSE`/`CLOSE_B3`-Ereignisse stehen genau einmal auf der letzten
Karte eines Feldes. Die übrigen 45 Felder sind offen. Diese Regel erfasst alle
135 Felder und 381 Ereignisse ohne Ausnahme.

## Bedeutungsdeckung

- 145/381 Ereignisse tragen einen ausgewählten formalen Namen oder ein
  schwaches Merkwort;
- 236/381 bleiben opak;
- 83/135 Felder enthalten mindestens einen ausgewählten Anker;
- nur 17/135 sind vollständig benannt;
- 52/135 besitzen gar keinen benannten Anker;
- nur 24/135 enthalten sowohl Host-/Operator- als auch Ganzkartenwerte und
  testen überhaupt deren Zusammenspiel.

Die fünf erschöpfenden Feldtypen stehen in
`V52_SELECTED_FIELD_GRAMMAR.tsv`. Sie unterscheiden offene/terminale opake
Felder, Host-/Rahmenfelder, Ganzkartenfelder und gemischte parataktische
Folgen.

## Entscheidende Reparatur

V49 hatte die vollständigen kreativen Kartenwerte wie moderne Prosa
aneinandergereiht. V52 stellt klar:

```text
WARM? | VERWENDEN? | LINK | CLOSE(UNKNOWN)
```

ist eine geordnete, teilweise annotierte Kartenfolge. Daraus folgt nicht von
selbst:

```text
„Temperiere die Flüssigkeit, verwende sie mit dem vorigen Ansatz
 und lasse sie bis zur Bereitschaft stehen.“
```

Der lange Satz bleibt als kreative Gesamtdeutung erlaubt, ist aber keine
kompositionell entzifferte Klausel.

Ebenso wird `CLOSE` nicht mehr als gesprochenes „beende den Schritt“ behandelt,
und eine RIGHT-Klasse wie `<ARG_AIIN>` erbt niemals das Merkwort der exakten
Ganzkarte `AIIN=MASS?`.

## Gewinn

Die Werkstatttheorie wird einfacher und lehrbarer:

1. kopiere die exakten Karten in der gegebenen Feldreihenfolge;
2. bewahre jeden bekannten Formelbaum;
3. lies nur ausgewählte Atome als Merkhilfen;
4. lasse unbekannte Karten unbekannt;
5. markiere einen vorhandenen Schluss nur formal;
6. expandiere erst anschließend das ganze Feld aus Bild, Register und
   praktischer Routine.

Damit können V53 und V54 vollständige Herbal- beziehungsweise Bio-Texte
weiterhin kreativ rekonstruieren, ohne so zu tun, als seien alle deutschen
Wörter bereits auf einzelne Karten verteilt. Keine Sprache oder Semantik ist
bewiesen; `f84` und `f84r` blieben versiegelt.
