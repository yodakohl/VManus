# W21 – neue Portion: kein interner Vergleichsbestand für den nächsten Test

**Die feste Nimm-Lesung bietet derzeit keine Stelle mit sowohl vorherigem
schriftlichem Vergleichsbestand als auch späterer gebundener Verwendung.** Deshalb
wird kein Portions- oder Reset-Simulator gebaut. Das Ergebnis widerlegt weder
nimm noch eine neue Portion; es begrenzt die Vergleichskapazität des aktuellen
13-Absatz-Entwurfs. W19s lokaler Wiederholungskandidat bleibt unverändert.

## Vorab festgelegte Frage und vollständiger Test

[DECISION.md](DECISION.md), [SPEC.json](SPEC.json), IDEA000218. W08 fixierte
Nimm-Patienten; W13 ließ SAME/FRESH offen, W09 prüfte andere Ergebnisnamen.
Hier werden erstmals alle festen Nimm-Patienten mit ihren früheren Ganzform-
Nennungen und allen späteren gebundenen Verwendungen zusammengestellt, bevor
man weitere Zustandsmodelle dafür implementiert.

Alle 13 bereits exponierten W02-ZL-Absatzbereiche mit sämtlichen gespeicherten
IT/RF-Loci: 13/14/13 Nimm-Stellen, jeweils B/J/M. Insgesamt 120 abhängige
Patientenfälle. Originalwörter, Nimm-Vertrag und die nachfolgenden Verarbeitungs-
argumente bleiben unverändert. Kein Reset sämtlicher Materialien nach ychor.

## Konkrete konkurrierende Lesungen

| Fassung | Vorhersage bei einem früheren gleichnamigen Bestand | Welche Information zur Unterscheidung fehlt |
|---|---|---|
| S: vorhandene Portion nehmen | Frühere Behandlung kann die folgende Verarbeitung desselben Bestands betreffen | Ein vorheriger schriftlich gebundener Bestand fehlt an sämtlichen gebundenen primären Nimm-Stellen |
| F-abgeteilt: neue Portion aus altem Bestand | Neue individuelle Portion könnte Eigenschaften des Ausgangsbestands übernehmen | Keine gelesene Abteilung oder identifizierte Menge; nicht mit unvorbehandeltem Material gleichsetzen |
| F-extern: separate Portion von außerhalb | Frühere lokale Behandlung gehört nicht automatisch zu diesem Eingang | Keine externe Herkunft oder Anfangsgeschichte gelesen; Erstnennung beweist keine physische Neuheit |

Keine F-Fassung wird nur deshalb bevorzugt, weil das Materialwort neu erscheint.
Auch ein bekannter oder bereits vorbereiteter Stoff kann erstmals genannt werden.

## Ergebnisse über alle Lesungen

| Lesung | Kein früheres gleiches Materialwort | Kein Nimm-Patient | Früherer Bestand, aber keine folgende gebundene Verwendung | Früherer Bestand mit folgender Verwendung |
|---|---:|---:|---:|---:|
| ZL3b | 38 | 1 | 0 | 0 |
| IT2a | 38 | 1 | 3 | 0 |
| RF1b | 38 | 1 | 0 | 0 |

Die Zahlen sind Grammatikfälle: Ein fehlender B-Patient auf f106r steht zwei
gebundenen J/M-Fassungen gegenüber. Sie sind keine unabhängigen Manuskriptbelege.
„Folgende Verwendung“ bedeutet hier feste Verarbeitungsbindung oder eine bereits
gebundene primäre ZL-Qualität. **IT/RF-Qualitäten wurden nicht neu übertragen oder
geprüft.** Die Tabelle darf daher nicht als Vollständigkeitsbehauptung für alle
möglichen Aussagen der alternativen Texte verstanden werden.

[ TARGETS.tsv ](TARGETS.tsv) enthält jeden Kandidaten samt Vorgeschichte, Folge-
verwendungen und allen alten Bindungslücken. [PROCESSING_USES.tsv](PROCESSING_USES.tsv)
führt alle 96 gleichen Materialformen betreffenden Verarbeitungsfälle auf,
[QUALITY_USES.tsv](QUALITY_USES.tsv) die neun primären Qualitätsfälle. Eine
Wirkungskarte ist keine neu simulierte oder beobachtete Stoffbehandlung.

## Die eine abweichende IT-Stelle

Nur IT liest zusätzlich `ychor` auf f93r.10:1. Dessen fester Nimm-Patient ist
`ctho` auf .9:3, hypothetisch Krautmehl. Es gibt:

- eine frühere Nennung dieses Materials;
- keine frühere daran gebundene Verarbeitung im festen Modell;
- keine spätere daran gebundene Verarbeitung;
- eine weitere ctho-Nennung auf .29:3.

Die bloße Wiederholung auf .29 unterscheidet die alte von einer neu genommenen
Portion nicht. Es gibt dabei keine identifizierte Menge oder andere unabhängige
Portionskennung. Die Befehle der .10 verwenden einen anderen Materialpatienten;
das war schon in W08/W13 als Grenze des Nimm-Vertrags offengelegt. Der Rückbezug
auf .9 enthält weiterhin eine offene Gruppe und angenommene Fortführung.

Der fehlende Patient auf f106r.9 betrifft nur B. J/M teilen qokain mit dem
folgenden chol, aber ohne früheres qokain im Absatz. Keine fehlende frühere
Kühlung oder zusätzliche Portion wird eingesetzt.

## Entscheidung, Reproduktion und Grenzen

**Den festen Ansatz hier mangels interner Unterscheidungskapazität stoppen.**
Es wird keine neue Portion behauptet, keine alte Stoffgeschichte gelöscht und
keine bessere Lesung aus einer bloßen Erstnennung abgeleitet. Das allgemeine
Problem SAME/FRESH ist nicht gelöst oder ausgeschöpft; dieser konkrete
Nimm-Patientenvergleich rechtfertigt keinen weiteren Simulator.

Die vollständigen 900 primären Rohgruppen stehen unverändert in
[W16/ALIGNMENT.tsv](../W16/ALIGNMENT.tsv) und der gemeinsamen
[W16-Arbeitslesung](../W16/READING.md). 534 Positionen tragen hypothetische Wortwerte,
366 bleiben ungelesen. [CONTEXTS.tsv](CONTEXTS.tsv) erhält alle tatsächlichen
Nimm-Zeilen in jeder vorhandenen Transkription.

```sh
python research_registry/proposals/translation_programs_20260912/work/W21/build.py
python research_registry/proposals/translation_programs_20260912/work/W21/validate.py
```

[VALIDATION.json](VALIDATION.json): PASS für unabhängigen vollständigen Quellen-,
Zeit- und Verwendungszensus. 357 Dateien aus W02–W20 bleiben hashgeprüft bytegleich.
Keine neue Bedeutung, Signifikanz, Suchgegenkontrolle oder unabhängige Bestätigung;
Bestätigungskapazität je Kandidat 0. Keine neuen Seiten, Bilder, Quellen, Roh-TSV
oder Kontakte. f84/f84r und übrige Reserven geschlossen. Alte globale GDT600-/
Indexprobleme liegen außerhalb des lokalen Prüfers. Kein weiterer Test ausgewählt.
