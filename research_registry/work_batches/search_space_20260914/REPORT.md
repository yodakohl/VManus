# Wortzahlen und bedingte Versuchszahlen

Nutzerfrage: Wie viele Wörter, wie viele Permutationen, welche Einschränkungen und welche Versuchszahl folgen daraus? Das ist eine deskriptive Bestandsrechnung, kein neuer Decoder oder Bedeutungsversuch. Die frühere pauschale Antwort „keine seriöse Zahl“ war zu undifferenziert: endliche Kandidatenräume und bedingte Erwartungswerte sind berechenbar; die tatsächliche Zahl bis zu einer erkennbar richtigen Übersetzung ist damit nicht kalibriert.

## Tatsächliche Zählung im freigegebenen Bestand

Alle sechs gehashten GDT915-Schnappschüsse aus GDT947;179 erlaubte Selektoren. Keine neuen Inhalte, Reserven oder Bilder. Rohgruppen unverändert, Leser getrennt.

| Quelle | Rohgruppen/Vorkommen | Verschiedene Rohformen | Nur a-z: Vorkommen | Nur a-z: Formen | Formen für50% der a-z-Vorkommen | Top100-Abdeckung |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 32363 | 7231 | 31309 | 6254 | 134 | 45.37% |
| IT2a | 31875 | 6793 | 31820 | 6750 | 151 | 43.43% |
| RF1b | 31946 | 7963 | 28167 | 6081 | 139 | 44.68% |

Die Rohformen enthalten Unsicherheits-/Sonderzeichen. Der a-z-Filter entfernt solche Gruppen ohne sie zu korrigieren. Er beweist keine zuverlässige Lesung oder sichere Wortgrenze. Das strengere, zusätzlich beidseitig sicher begrenzte Teilinventar steht in COUNTS.json. Rohformen, Grundwörter, Morpheme und Bedeutungen sind verschiedene Größen; ihre Gleichsetzung wäre ein zusätzliches Modell.

Für den ganzen Manuskriptbestand nennt René Zandbergens [eigene Zählung](https://voynich.nu/extra/sp_analysis.html) als grobe Größenordnung37000–39000 Vorkommen und9000–10000 Formen. Seine konkrete Tabelle reicht je nach Transkription und Abstandszählung von8412 bis10553 Formen. Diese öffentlichen Aggregatwerte wurden als Metadaten nachgeschlagen; keine ausgeschlossenen Absatzinhalte wurden dazu geöffnet. Sie sind nicht mit unserem kleineren freigegebenen Bestand gleichzusetzen.

## Permutationsraum nur bei festgelegtem Modell

Angenommen, n verschiedene Schriftformen entsprechen genau n bereits bekannten verschiedenen Bedeutungen, jede genau einmal. Dann sind n! Zuordnungen möglich. Die Folge der Manuskriptwörter selbst wird dabei nicht umsortiert.

| n | n! ungefähr |
|---|---:|
| 10 | 3.63 ×10^6 |
| 20 | 2.43 ×10^18 |
| 50 | 3.04 ×10^64 |
| 100 | 9.33 ×10^157 |
| 9000 | 8.10 ×10^31681 |

Das ist ein absichtlich vereinfachtes Wörterbuchmodell, keine obere oder untere Schranke für alle Voynich-Lesungen. Wortaufbau, mehrere Bedeutungen, Schreibvarianten, unbekannte Ausgangssprache und unbekanntes Bedeutungsinventar ändern den Modellraum. Für n feste Formen mit jeweils v möglichen Werten und erlaubter Mehrfachzuordnung gilt dagegen v^n, vor weiteren Konsistenzbedingungen.

## Was vorhandenes Wissen tatsächlich einschränkt

GDT608 belegt gerichtete formale Komposition, zugleich paarspezifische Restinformation. Die primär geprüfte [Strukturbilanz](../../proposals/differential_reading_20260914/STRUCTURAL_BASELINE.md) bündelt wiederverwendbare Teile, Wort-/Zeilenposition, Kontext und die nur begrenzte Übertragbarkeit bekannter r/l-Familien. Diese Befunde sind Anforderungen an Erklärungen; sie liefern keine gemessene Zahl semantischer Restkandidaten. Die98 gelernten Einheiten sind insbesondere kein nachgewiesenes98-Wörter-Lexikon.

- Wiederholungen unter einer stabilen Abbildungsannahme gemeinsam behandeln, statt jedes Vorkommen separat zu raten. Homographie/Polysemie als explizite Modellmöglichkeiten, nicht beliebige Ausnahmen.
- Wiederverwendete Formen mit gemeinsamen Regeln erklären; Eigenheiten ganzer Formen und Kontext erhalten. Die tatsächliche Anzahl semantischer Freiheitsgrade ist unbekannt.
- Positions-/Kombinationsprofile und bekannte Grenzen verwenden. Sie dürfen nicht ungeprüft als Verb/Nomen/Kasus oder englische Bedeutung gelten.
- Den häufigen Kern priorisieren:134–151 reine a-z-Formen decken bereits die Hälfte der so gefilterten Vorkommen ab. Das schafft viele mögliche Gegenstellen, noch keine50% Übersetzung.

Wie groß ein **wirklich begründeter** Filter wirken kann: Bei20 Wörtern und20 bekannten Bedeutungen, beiderseits korrekt in vier Klassen à5 eingeordnet, bleiben (5!)^4 =207360000 statt20! Zuordnungen. Ein Rückgang um den Faktor11732745024. Eine solche vollständige semantische Klasseneinteilung besitzen wir derzeit nicht. Die Rechnung zeigt den Wert einer Einschränkung, nicht eine schon erreichte Reduktion.

## Eine konkrete bedingte Versuchsschätzung

Für einen lokalen gemeinsamen Bedeutungsentwurf mit k unbekannten Werten, jeweils3 vorab festgelegten Kandidaten, und4 binären Regelentscheidungen umfasst das kartesische Modell vor Filterung N=3^k ×2^4 Kombinationen:

| k | vollständige Modellkombinationen | Erwartete Position der einzigen richtigen Kombination bei zufälliger Reihenfolge ohne Wiederholung |
|---|---:|---:|
| 6 | 11664 | 5832.5 |
| 8 | 104976 | 52488.5 |
| 10 | 944784 | 472392.5 |

Die Erwartung (N+1)/2 setzt voraus, dass die richtige Kombination enthalten ist, nur eine richtig ist, die Reihenfolge zufällig ist und wir Richtigkeit erkennen können. Diese Voraussetzungen sind für Voynich nicht belegt. Bei r>1 richtigen Kandidaten ist die erwartete erste Position (N+1)/(r+1), unter denselben Zufalls-/Erkennbarkeitsannahmen. Ohne enthaltene richtige Lösung bringt vollständige Enumeration keine Übersetzung. Die3 Werte und4 Regeln sind Szenarioparameter, keine gemessenen Restfreiheiten unseres Projekts.

Eine automatische Modellkombination ist kein arbeitsintensiver GDT-Versuch: Ein gemeinsamer Lauf kann viele Kombinationen behandeln. Wie viele unterschiedliche Beobachtungsprüfungen gebraucht werden, hängt von deren Trennkraft ab. Ideale zuverlässige binäre Fragen benötigen mindestens ceil(log2 N) Antworten zur Identifikation unter N gleichberechtigten Kandidaten; für20! sind das62. Es ist weder bekannt, dass solche Fragen im Manuskript verfügbar sind, noch dass die bisherigen Versuche unabhängige Bits geliefert haben.

Praktische Aussage: Ein explizit begrenzter lokaler Kandidatenraum im Bereich10^4–10^6 lässt sich als solcher planen und vollständig bilanzieren. Das ist keine Prognose „nach einer Million Versuchen ist ein Wort übersetzt“. Zuerst müssten die Kandidaten und ihre gemeinsamen Regeln begründet festgelegt werden. Alte Fehlschläge oder50 probeweise gesetzte Glossen machen aus dem offenen Problem keine schon bekannte endliche Restliste.

## Reproduktion

`python research_registry/work_batches/search_space_20260914/count.py` schreibt [COUNTS.json](COUNTS.json), verifiziert zuerst die gebundenen Quell- und Modellhashes, prüft179Selektoren, eindeutige Quellgruppen und die Summe96184. Alle Größen stammen aus getrennten ZL/IT/RF-Zählungen. Die Fakultäten werden logarithmisch mit lgamma gerechnet; kleine Szenarien und die Klasseneinteilung exakt als Ganzzahlen. Keine neue Signifikanz oder Bedeutung behauptet.
