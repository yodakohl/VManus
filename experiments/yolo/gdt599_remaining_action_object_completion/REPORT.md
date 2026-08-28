# GDT599 — jede Aktion hat jetzt einen konkreten Gegenstand

## Ergebnis

Der gesamte GDT598-Rest ist geschlossen:

```text
313 Aussagen / 2.272 Hosts
└── 1.443 Aktionshosts
    ├── 650 aus GDT598 bereits objektfertig
    └── 793 in GDT599 ergänzt
        ├── 736 Teilnehmer
        ├──  46 lokale AIIN-Maßargumente
        ├──  10 Bedingungsparameter
        └──   1 vorübergehender Maßpatient
```

Es bleiben null leere Aktionsslots. Alle 313 Aussagen sind damit erstmals als
durchgehende konkrete Werkstattfassung lesbar. Der Validator besteht 103
Populations-, Zustands-, Provenienz- und Reproduzierbarkeitsprüfungen.

## Woher die 793 neuen Gegenstände kommen

| Route | Fälle |
|---|---:|
| eigener geschriebener Teilnehmer | 297 |
| linker kompatibler Zustand | 207 |
| rechter geschriebener Teilnehmer desselben Ereignisses | 155 |
| kurzer Rootdefault | 54 |
| AIIN als eigenes Mengen-/Maßargument | 46 |
| rechter begrenzter Ergänzer | 21 |
| lokale Werkstattentscheidung | 11 |
| exakte CH→SH-Brücke | 2 |

Damit sind 454 Fälle direkt im eigenen oder gleichereignigen geschriebenen
Material verankert. 207 weitere setzen den zuletzt sichtbaren kompatiblen
Teilnehmer fort. Nur 54 von 793 Fällen — knapp sieben Prozent — brauchen den
reinen Rootdefault.

Die neu ergänzte Objektschicht enthält 573 Stationen, 96 Portionen, 47 Maße,
31 Körper, 22 Einheiten, 13 Flüsse, zehn Bedingungen und ein explizites
Körperteil. Diese Zahlen betreffen nur die 793 neuen Ergänzungen; die
vollständige 1.443er Edition enthält zusätzlich die 650 früheren Lesungen.

## Was sich konkret verbessert

Eine nackte Aktion wie `Führe zu` erhält beispielsweise aus dem rechten
geschriebenen Teilnehmer desselben Ereignisses `Führe den Stationsansatz zu`.
Nach einem bereits sichtbaren Stationsansatz wird ein offenes OK anaphorisch
zu `Beschicke oder bereite denselben Stationsansatz vor`. Ein AIIN-only-OK
wird nicht mehr abstrakt als „Stationsmaß“ behandelt, sondern als `Bereite
eine abgemessene Menge des Stationsansatzes vor` gesprochen.

Q-Klauseln sind nun als echte Zustandsübergänge lesbar. Der Eingang bleibt im
ersten Teilsatz und das Resultat folgt getrennt, etwa: `Wende die
Anwendungsportion auf Grad I an; übernimm das Ergebnis als neuen Bad- oder
Stationsansatz.` Neun verführerische rechte Stationsquellen wurden blockiert,
weil sie erst durch genau dasselbe Q-Ergebnis entstehen würden.

Die lokale Probenlesung zeigt, warum Einzelfälle wichtig bleiben:
`Entnimm die Probe am selben Körperteil …`; die nächste Aktion liest folgerichtig
`Bereite dieselbe Probe auf Grad II vor`. Ebenso wird ein Pfad-CH in sieben
Fällen konkret als `Lass den Strom … ab` statt als Entnahme eines abstrakten
Stationsansatzes gelesen.

## Sechs-Seiten-Realitätscheck

Ein manueller Lesepass wählte je Seite eine besonders aussagekräftige Kette.
Die verdichtete Fassung zeigt, was die jetzigen Objektzustände bereits tragen
und welche reine Oberflächenglättung als Nächstes möglich ist:

| Seite / Aussage | Verdichtete Werkstattlesung |
|---|---|
| f75r / G407-S109 | Leite die Teilmenge in das Zielbecken um. Bringe den Körper bei Grad I ins Bad und halte ihn dort. |
| f77r / G407-S377 | Behandle den Körperteil. Entnimm an der Arbeitsstelle über Kontakt oder Leitung eine Probe am selben Körperteil. Bereite diese Probe auf Grad II vor. |
| f81r / G407-S402 | Halte den Körper bei Grad I im Bad. Nimm ihn heraus. Bringe ihn bei Grad I wieder ein. |
| f81v / G407-S442 | Halte den Körper bei Grad I im Bad. Bringe ihn an der Arbeitsstelle aus dem Ausgangsbecken in das Zielbecken. Setze ihn dort ein und behandle ihn. |
| f82r / G407-S509 | Setze den Inhalt der Einheit in Anwendungsform ein und bereite daraus einen neuen Bad- oder Stationsansatz. |
| f83r / G407-S583 | Lass die Flüssigkeit in Anwendungsform über Kontakt oder Leitung ab und fange sie als neuen Bad- oder Stationsansatz auf. Führe diesen Ansatz zu und halte ihn bei Grad I im Bad. |

Diese Sätze sind keine zusätzliche Lexemzuweisung. Sie sind der manuelle
Nachweis, dass die Zustandsketten `Körper→Körper`,
`Körperteil→Probe→Probe`, `Fluss→neue Station` und
`Portion→neue Station` in zusammenhängender Sprache funktionieren.

## Historischer Formvergleich

Die AIIN-Lesung als Mengenhülle passt formal zu spätmittelalterlichen
Rezept- und Kochanweisungen, in denen ein Imperativ eine bestimmte Menge eines
Stoffs regiert. Als Vergleichsmaterial dienen:

- British Library, Harley MS 2378, um 1395: medizinisch-alchemistische
  Rezeptsammlung mit benannten Flüssigkeitsmengen;
- Durham, Cosin MS V.iv.8, frühes 15. Jahrhundert: Rezeptmengen unter anderem
  für Anis und Kümmel;
- die Harleian cookery books, etwa 1430/1450: wiederholte Mengen- und
  Portionskonstruktionen.

Quellen: [British Library catalogue](https://searcharchives.bl.uk/catalog/041-002041400),
[Durham catalogue and text](https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s1sn009x84b.xml),
[Middle English Compendium text](https://quod.lib.umich.edu/c/cme/CookBk/1%3A6.2?rgn=div2%3Bview%3Dfulltext).
Die Parallele stützt nur den Konstruktionstyp „Menge von X“; sie identifiziert
weder AIIN historisch noch die Sprache des Manuskripts.

## Was noch schwach ist

Vollständigkeit bedeutet hier nicht, dass jede Bedeutung gleich stark ist.
Die beweglichsten Stellen sind offen markiert:

- 54 reine Rootdefaults;
- 21 rechts ergänzte Fälle ohne linke Quelle;
- 46 AIIN-Hüllen, deren Substrat weiterhin aus lokalem Zustand oder Default
  stammt;
- 125 Einträge der Reviewqueue, vor allem ungewöhnliche Körper-, Fluss-,
  Einheiten- und lange Distanzfortsetzungen;
- 153 strukturelle Fragmente vom Typ „Verwende für den vorangehenden
  Arbeitsschritt“, die noch ein explizites Bezugswort brauchen;
- 168 CH-Klauseln mit dem Doppelverb „Entnimm oder lass“ und 234 OK-Klauseln
  mit „Beschicke oder bereite“, bei denen die Objektklasse künftig das genauere
  Einzelverb wählen kann;
- 168 Klauseln mit mindestens zwei flach gereihten Modifikatoren, davon 52 mit
  mindestens drei, sowie 105 CH/K/P-Klauseln, deren „auf Grad“-Valenz noch
  zwischen Vorgangstemperatur und echtem Einstellen unterscheiden sollte;
- 15 unmittelbar wiederholte Aktionssätze und 24 Q-Resultate, die mit
  `erneut` beziehungsweise input-spezifischen Ergebnisverben natürlicher
  werden können.

Das ist genau der gewünschte Zustand für die nächste Runde: kein Leerraum wird
mehr mit „unbekannt“ versteckt, aber jeder schwache Default bleibt auffindbar
und ersetzbar. Als nächstes sollte auf denselben sechs Seiten die Grammatik der
gemischten Mehrfachpakete und der 125 Reviewfälle verbessert werden, bevor
neue Seiten als Belastungsprobe dazukommen.
