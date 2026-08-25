# Pass 1021 — der wiederholte Kern als Doppelrahmen

## Vollständiges Inventar

In den 3.888 laufenden Karten stehen **40** unmittelbar verdoppelte gleiche
tragbare Kerne. Jede Doppelung liegt innerhalb einer einzelnen Kartenzerlegung;
Karten über einen sichtbaren Trenner hinweg werden nicht zusammengezogen. Es
gibt 40 betroffene Karten in 38 Aussagen auf 16 Seiten,
28 sichtbare Kartentypen und 19 verschiedene
Komponentenrezepte. Keine Karte enthält zwei Doppelpaare oder eine Dreifachform.

Die Register verteilen sich auf Herbal 6, Biological
23, Celestial 6 und
Pharma 5.

| Kern | Wert | Vorkommen | Kurzform des Doppelrahmens |
|---|---|---:|---|
| `CH` | NEHMEN | 27 | äußere Einheit nehmen; darin die aktive Untereinheit nehmen |
| `OL` | FORTSETZEN | 5 | den äußeren Gang fortsetzen; darin den inneren Gang fortsetzen |
| `AR` | AUSGANG | 2 | den äußeren Ausgang wählen; darin den lokalen Ausgang wählen |
| `AL` | ZIELORT | 2 | den äußeren Zielort wählen; darin den lokalen Zielort wählen |
| `Y` | AKTIVER POSTEN | 2 | den Besitzerreferenten halten; darin den aktiven Unterreferenten halten |
| `OR` | EINHEIT | 1 | die äußere Einheit öffnen; darin die aktive Untereinheit öffnen |
| `OK` | SETZEN | 1 | die äußere Einheit setzen; darin den aktiven Unterposten setzen |


Die zwölf Kerne ohne unmittelbare Doppelung sind
`OT SH K AIIN S CHD L T AIN R P AIR`. Die Abwesenheit erzeugt keine Sonderregel; das Blatt
braucht sie für diese Konstruktion nur nicht.

## Vier mögliche Lesungen

### Bloße Wiederholung

Das passt teilweise zu `CH+CH`, `OK+OK` und `OL+OL`: eine Handlung wird noch
einmal ausgeführt. Es erklärt aber `AR+AR`, `AL+AL`, `OR+OR` und `Y+Y` schlecht,
weil dort nicht einfach eine Tätigkeit wiederholt wird.

### Plural

Zwei Ausgänge, Zielorte, Einheiten oder Posten wären möglich. Doch die
`CH+CH`-Karten stehen fast immer vor einem weiteren Kern wie `T`, `K`, `P` oder
`S`. Das sieht eher nach einem eingebetteten Arbeitsblock als nach einer
einfachen Zweizahl aus.

### Nachdruck

Nachdruck könnte eine einzelne Doppelkarte erklären, aber nicht, warum die
Doppelung bei Handlungen am Kartenanfang und bei Relationen häufig am Ende
eines Rahmens steht. Außerdem würde sie den sichtbaren Besitzerwechsel nicht
nutzen.

### Verschachtelung

Verschachtelung trägt alle sieben Kerne mit derselben Regel und erklärt die
Nachbarstruktur am sparsamsten. Bei `CH` folgen auf das Doppel stets
Handlungs- oder Einstellkerne; bei `AR`, `AL`, `OR` und `Y` werden dagegen zwei
Besitz- oder Adresslagen übereinandergelegt. `OL+OL` hält den äußeren und den
inneren Fortsetzungsgang zugleich offen.

## Die einheitliche Werkstattregel

Die beste Lehrregel heißt **DOPPELRAHMEN / EIN STUFENABSTIEG**:

> `X + X + Z` = `X_äußerer Besitzer ( X_aktive Untereinheit ( Z ) )`

Der erste Kern bindet den äußeren Bild-, Stations-, Ring- oder Gefäßbesitzer.
Der zweite gleiche Kern steigt genau eine Ebene zum aktiven Mitglied,
Teilposten oder Untergang hinab. Ein rechts folgender Kern `Z` füllt zuerst den
inneren Rahmen. Endet die Karte mit `X+X`, liefert der lokale Besitzer den
inneren Inhalt.

Dadurch darf die flüssige Sprache je nach Kern unterschiedlich klingen:

- bei Handlungen wie `CH` und `OK`: **am Besitzer und dann am Teilposten noch
  einmal ausführen**;
- bei `OL`: **äußeren und inneren Gang fortsetzen**;
- bei `AR` und `AL`: **Ausgang/Ziel innerhalb eines übergeordneten
  Ausgangs-/Zielrahmens**;
- bei `Y`: **Besitzerreferent und aktiver Unterreferent**;
- bei `OR`: **Einheit in Einheit**.

Wiederholung und Zweizahl können also als lokale deutsche Wirkung erscheinen,
sind aber nicht die Grundregel. Nachdruck ist für keine Karte erforderlich.

## f13r, P1009-S009

Die drei Karten lauten:

```text
sotchy            S + OT + Y
kchy              K + Y
okorory           OK + OR + OR + Y
```

Mit dem Doppelrahmen wird die letzte Karte rechtsgeschachtelt gelesen:

```text
SETZEN [äußere EINHEIT [innere EINHEIT [AKTIVER POSTEN]]]
```

Der Bildbesitzer zeigt eine ganze Pflanze mit deutlich getrennten Wurzel-,
Kronen-, Blatt- und Blütenposten. Die einfache lokale Expansion lautet:

> Danach den nächsten sichtbaren Pflanzenteil wählen und geben; ihn als
> Untereinheit in den laufenden Pflanzenartikel setzen. Offen weiterführen.

Damit bedeutet `OR+OR` weder zwei fertige Zubereitungen noch bloß
**sehr starke Einheit**. Die erste `OR` hält den Artikelrahmen, die zweite den
aktiven Teilrahmen. Das Blatt sagt weiterhin nicht, welcher Pflanzenteil gewählt
wird und ob der äußere Rahmen Artikel, Arbeitsgang oder Vorratsgruppe heißt;
genau diese Konkretisierung bleibt beim Besitzer.

## Was die Regel nicht erfindet

Der Doppelrahmen gibt keinem Kern einen zweiten Wörterbuchwert. Er benennt
keine Pflanzenart, Flüssigkeit, Körperstelle, Sternfigur oder Gefäßfüllung. Er
erklärt nur, warum derselbe bereits gelernte Kern unmittelbar zweimal stehen
kann: Der Schreiber führt dieselbe Funktion auf zwei benachbarten
Besitzerebenen aus.

Das vollständige Auftreten mit Karte, Aussage, Seite, Besitzer, inneren
Nachbaratomen sowie voriger und nächster Karte steht in
`REPEATED_CORE_OCCURRENCES.tsv`.
