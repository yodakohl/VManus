# GDT589 — der Vollhost-Leser hält; die alte Zählanzeige nicht

## Ergebnis

Der automatische Kern ist stabiler als der bisherige Stichprobentest zeigte.
Alle 910 automatisch routbaren Hosts mit 1.186 Carrier-Slots reproduzieren
ihre alte Regel, Rootfolge, Slotzahl, Kontextfamilie, Nomenformen und ihr
Packet exakt. 1.068 Slots kommen aus einer beobachteten Handlung×Root-Zelle,
118 aus einer bekannten Packetregel; kein alter automatischer Host benötigt
einen Registerfallback.

Der vollständige Bestand zerfällt damit sauber:

| Gate | Hosts | Slots | Ausgang |
|---|---:|---:|---|
| automatisch | 910 | 1.186 | vollständig exakt |
| bekannte manuelle GDT584-Regel | 41 | 53 | eigener sichtbarer Weg |
| alte source-ID-Regel | 2 | 4 | portabler Fallthrough sichtbar exakt |
| gesamt | 953 | 1.243 | vollständig geroutet |

## Manuell heißt vor allem: anderes Verb

Bei 39 der 41 manuellen Hosts ändert der Elternweg die konkrete Handlung,
etwa `Weiche ein → Halte`, `Zerkleinere → Zerreibe` oder
`Verreibe/mazeriere → Bearbeite`. Die Nomen sind wesentlich robuster:

- zwei Hosts ändern schon unter dem direkten Elternregelsinn je ein Nomen;
- zwei weitere ändern erst durch den bewusst konservativen breiten
  Runtime-Fallback ein sichtbares Nomen;
- vier andere ändern nur das Packet;
- insgesamt haben acht Hosts eine sichtbare Carrier-/Packetabweichung.

Der explizite alte manuelle Weg reproduziert alle 53 Slots. Er darf also nicht
heimlich automatisiert werden, muss aber auch nicht wie ein allgemeiner
Nomenfehler behandelt werden. Breite Defaults zeigen nun ihr beobachtetes
Alternativinventar, beispielsweise `Arzneiauszug/Dosismaß`.

Die zwei alten `SH_CH_BRIDGE_HOLD`-Hosts werden mit ihrer Quell-ID korrekt
abgewiesen. Mit neutraler Zukunfts-ID fallen beide auf `SH_REST_HOLD` zurück;
Verb, alle vier Nomen, Packet und Reihenfolge bleiben sichtbar gleich. Das ist
kein Lesestopp, sondern nur der Verlust alter Regelprovenienz.

## Der große Fund: 117 Repeat-Hosts, nicht 13

GDT588 hatte die 13 Wiederholungen innerhalb spezieller Packets gefunden.
Über alle 953 Hosts existieren jedoch:

- 117 Hosts mit wiederholten Roots;
- 295 Carrier-Slots darin;
- 132 zusätzliche Schriftpositionen über die bloße Root-Präsenz hinaus;
- 104 bisher unmarkierte Default-Kompositionen mit 258 Slots;
- 90 betroffene Reader-Einheiten: 83 Aussagen und sieben lokale Karten.

Die Ursache ist eindeutig: der alte flüssige Renderer dedupliziert Roots. Ein
Host wie `Y+Y+Y+Y` erscheint dadurch nur einmal als Pflanzenmaterial. Das
bedeutet aber nicht automatisch vier Pflanzenmengen. Lokale Formen wie
`Y–T–Y` zeigen, dass Wiederholung auch Rahmung oder Koreferenz sein kann.

GDT589 ersetzt deshalb die Ein-Kanal-Lösung durch eine bessere:

1. Die flüssige Bedeutungshypothese behält Relation und Grammatik.
2. Daneben steht die vollständige ordinale Spur, etwa
   `OR+Y+OR → Pflanzeneinheit | Pflanzenmaterial | Pflanzeneinheit`.
3. Ein Multiset fasst nur die Schriftstellen zusammen und sagt ausdrücklich,
   dass es keine Realobjekte zählt.

Damit sind alle 117 Wiederholungshosts sichtbar, ohne aus Orthographie eine
falsche Mengenlehre zu machen.

## Packet-Komposition ist mehr als die Summe der Slotnomen

Der Vollreplay trennt nun Slotspur, Packetkopf und fertigen Satz. Das deckt
zehn konkrete Anzeigeausnahmen auf:

- zwei Source-Part-Hosts haben Slot-Y=`Arbeitsgut`, aber in der
  Packetrelation sinnvoll `Arbeitsmaterial`;
- drei Seih-Hosts ohne geschriebenes AIIN erhalten `Auszug` aus der Handlung,
  nicht aus einem erfundenen Carrier;
- eine celestiale Kurzkarte unterschlägt den tatsächlich geschriebenen
  `Sektoranteil`;
- vier blockerfreie Y+AIIN-Badehosts erlauben eine echte
  Körper/Stationsansatz-Gabel.

Die vier Badstellen liegen bei G407-E2404, E2637, E2652 und E3182. Der bisherige
Code versprach in der Packetkarte `Stationsansatz/Körper`, konnte wegen seiner
`carrier_roots == {Y}`-Bedingung bei vorhandenem AIIN aber niemals Körper
liefern. Als nächste Arbeitshypothese steht dort jetzt `Körper im Bad bei der
angegebenen Füllung` zuerst; `Stationsansatz` bleibt als Alternative offen.

## Was jetzt als Basis gilt

Für neue, bereits segmentierte Hosts ist der technische Weg bereit:
vollständigen Host nehmen, Gate wählen, geordnete Slots erhalten, Packetkopf
separat komponieren und erst dann den flüssigen Satz anzeigen. Die 910
automatischen bekannten Hosts sind eine vollständige Regression dieser Kette.

Semantisch bleibt die stärkste prozedurale Schicht unverändert: Trocknen,
Zerkleinern, Mazerieren, Einweichen, Erwärmen, Halten, Absetzen, Sieben und
Abseihen sowie Material, Auszug, Portion und Ansatz. Neu ist nicht ein
Wörterbuchtausch, sondern eine ehrlichere und vollständigere Darstellung, in
der keine Schriftstelle verschwindet.

Validierung: 76/76 Prüfungen grün, einschließlich byte-identischem Rebuild.
