# GDT688 — V61 exact verb provenance

## Ergebnis

V61 schließt den Aktionsfehler des praktischen Readers vollständig: Alle 113
ausgegebenen deutschen Verbvorkommen besitzen einen exakten Zeichenspan in
genau einer geschriebenen Aktionskarte. Der Span projiziert auf ein
`action_ordinal`, dessen Surface und Literalgloss bytegenau im Reader stehen.
Es bleiben null freie, null mehrdeutige und null bloß aus Satzfluss ergänzte
Verben.

Die 85 Aktionspositionen verteilen sich nicht eins zu eins auf Verben:

| Verben in einer Aktionskarte | Aktionspositionen | Verbvorkommen |
|---:|---:|---:|
| 1 | 65 | 65 |
| 2 | 12 | 24 |
| 3 | 8 | 24 |
| **gesamt** | **85** | **113** |

Damit bleibt etwa `sheky = einweichen, erhitzen und abschließen` als eine
geschriebene dreigliedrige Aktionskarte erhalten, ohne drei hypothetische
Voynichwörter zu erfinden.

## Wichtige Scope-Korrektur

Der GDT687-Bericht und die damalige Route nannten 66 zusätzliche
Verb×Zeile-Paare als Ausgangspunkt des nächsten Passes. Das war der
reproduzierbare V59-Wert, nicht der bereits erzeugte V60-Wert. GDT687 hatte
vierzig Zeilen mit einem strengen Tokenrenderer neu ausgegeben und dabei schon
62 dieser 66 Paare beseitigt.

Der ausführbare Verlauf lautet:

| Reader | Aktionspositionen | zusätzliche alte Lemma×Zeile-Paare | Zeilen |
|---|---:|---:|---:|
| V57 / GDT684 | 86 | 74 | 29 |
| V59 / GDT686 | 86 | 66 | 28 |
| V60 / GDT687 | 85 | 4 | 2 |
| V61 / GDT688 | 85 | 0 | 0 |

Die Korrektur ändert den GDT687-Rollenbefund nicht; sie zeigt, dass dessen
Rendererwirkung stärker war als im Ausblick angegeben.

## Die vier letzten freien Verben

### f114v.36

V60 verband nominale Zustände zu einer Handlung und schloss den Block, obwohl
keine geschriebene Karte `verbinden` oder `abschließen` lizenzierte. Außerdem
verschmolzen zwei getrennte Nehmen-Karten zu einem einzigen Verb.

V61 liest quellgeordnet:

> Kalt und feucht in der Mitte des Grades; abgemessene Rohstoffmenge I im
> Ansatz, Grundform; Pulveransatz; erhitzter Feuchtansatz; kalt-trockener Ansatz
> in der Mitte des Grades; nimm getrockneten Pulverstoff; drei Teile
> Pulveransatz nehmen; kalte Drogenfraktion I; Rohstoffklasse I;
> Rohstoffklasse I, heiß am Gradanfang; Wurzel/Wurzeldroge: Maß-/Einheitsform I.

Beide geschriebenen Nehmen-Handlungen bleiben getrennt; die zwei freien
Verben verschwinden.

### f75r.3

V60 machte aus `trocken am Gradanfang` den Befehl *leicht trocknen* und aus
`heiß, Grad II` den Befehl *auf Heizstufe II bringen*. Beide Zustandskarten
waren nominal.

V61 liest:

> Heiß, Grad II; Rohstoffklasse I, trocken am Gradanfang; eine Portion bis zur
> Mittelstufe getrocknete Droge; die vorstehende Mittelstufenportion
> anschließend nehmen; heiß, Grad II; vollständig einweichen, erhitzen und
> abschließen; Holzdroge, kalt auf Stufe II; erste erhitzte Drogenfraktion im
> Ansatz; Holzbindung offen; Drogenportion.

Nur `nehmen` sowie die geschriebene Dreierkarte `einweichen, erhitzen,
abschließen` bleiben Verben.

## Warum Zeichenspans nötig sind

V60 enthielt 116 erkannte praktische Verbvorkommen. Die vierzig von GDT687
bereits neu gerenderten Zeilen lieferten 95 exakte Spanrückbindungen. Auf den
übrigen Zeilen hatten sieben Vorkommen nur einen lexikalischen Kandidaten,
zehn mehrere und vier keinen. Besonders f80r.17 wiederholt dieselbe
dreigliedrige `sheky`-Karte an drei Ordinalen; ein bloßer Lemmaabgleich kann
nicht sagen, welches *einweichen* zu welchem geschriebenen Surface gehört.

V61 speichert die Tokenbeiträge als Zeichenintervalle. Dadurch zeigen alle
neun Verben der drei `sheky`-Karten auf ihre jeweils eigene Position. Auch die
alte Regexkollision `kühle … ab = abkühlen + kühlen` verschwindet: Der
separable Span zählt einmal als `abkühlen`.

## Drei Reader-Modi

V61 ändert keine Grammatik. Es macht die vorhandenen Zeilentypen nur im
Arbeitsreader sichtbar:

- 16 `ARBEITSGANG`-Zeilen aus `ACTION_SEQUENCE`;
- 23 `HYBRID_ARBEIT_UND_ZUSTAND` aus `MIXED_RECORD`;
- 6 `ZUSTANDSLISTE` aus `NOMINAL_REGISTER`;
- 6 `MENGEN_UND_ZUSTANDSLISTE` aus `QUANTITY_LABEL`.

Die Modusnamen sind eine Anzeigehilfe und kein übersetztes Manuskriptwort.
Jede praktische Zeile bleibt in geschriebener Tokenreihenfolge.

## Was V61 nicht repariert

V61 ändert null semantische Karten. Darum bleiben die GDT687-Schuldenstände
unverändert: 106 strikte Positionen, 152 in der mechanischen Union und 330 in
der Vier-Schichten-Union. Ausdrücke wie `Holzbindung offen`, Slash-Alternativen
oder schwache Stoffidentitäten sind nun sauber vom Verbproblem getrennt, aber
noch nicht beseitigt.

Der nächste Bedeutungshebel ist die `-dy/-y`-Schwesterfamilie. Von den 60
gebundenen V60-`dy`-Oberflächen besitzen 39 eine echte nicht-`dy`-Schwester.
Der nächste Pass muss jede dieser Paarungen genau einer Arbeitsklasse
zuordnen: bloßes Feldende, nominales Resultatpartizip oder Telizität einer
bereits lizenzierten Aktion. `dchey/dchedy` ist wegen verschiedener Parser
ausdrücklich kein Minimalpaar. Danach folgt die Trennung von sauberem
Haupttext und Unsicherheitsapparat. Keine neue Seite ist nötig.

## Grenze

Die 113 deutschen Verben sind jetzt vollständig rückprojizierbar. Das beweist
nicht, dass ihre deutschen Werte historisch richtig sind. V61 ist ein sauberer
Compiler für die aktuelle Arbeitstheorie, keine Entzifferung.
