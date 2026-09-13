# W47 — sheey: keine direkte Ausgangszustandsprüfung

**Die zusätzliche Kontextprüfung bestätigt sheey≈benetzen nicht.** Sie findet keinen Fall des vorregistrierten unmittelbaren Material–Handlung–Zustandsmusters. Das ist fehlende Testkapazität für diesen engen Vertrag, kein Widerspruch gegen Benetzung und keine allgemeine Ausschöpfung aller sheey-Kontexte. Die bedingte W46-Arbeitsglosse ysheol≈feucht bleibt von der frei gesetzten Benetzungsannahme abhängig.

## Herkunft der Bedeutungsannahme

W02/LEXICON.tsv führt sheey als „benetze“, ACTION, „W02 common extension authored“, f102v2.30:7, UNCONFIRMED_ASSUMPTION. W02/MODEL.md erklärt die frei entwickelten Wortwerte und die Exposition aller 900 Positionen bei ihrer Ausarbeitung. W09/SPEC.json übernimmt moisture=wet; seine Zustandsrechnung bindet diese Bedeutung nicht unabhängig. W11 hält für die ursprüngliche sheey-Stelle ausdrücklich den fehlenden Patienten fest. Das neue ysheol auf f21r darf nicht als unabhängige Bestätigung seiner eigenen angenommenen Vorgeschichte dienen.

## Tatsächlich geprüfter Umfang

Alle 96.184 Rohgruppen aus den sechs bereits exponierten GDT915-Dateien, unveränderte 179-Selektoren-Zulassung. Kein neues Manuskriptmaterial.

| Lesung | Gruppen durchsucht | exaktes sheey |
|---|---:|---:|
| ZL3b | 32.363 | 126 |
| IT2a | 31.875 | 128 |
| RF1b | 31.946 | 111 |

Zusammen 365 lesungsabhängige Vorkommen auf 133 verschiedenen Quellzeilen und 46 physischen Blättern. Das sind keine 365 unabhängigen Schriftstellen. Unterschiedliche Gruppenindizes wurden nicht als nativ ausgerichtete Positionen behandelt. Die beiden ursprünglichen Motivationsblätter f21/f102 sind in OCCURRENCES.tsv von allen anderen bereits exponierten Blättern getrennt. Auch die anderen Blätter sind nicht blind gehaltene Bestätigung.

Geprüft wurden ausschließlich sichere unmittelbare Dreierfolgen `MATERIAL sheey STATE` und `sheey MATERIAL STATE`, getrennt für W38 C_A/C_Q. Materialrollen stammen unverändert aus W05, Wortrollen aus W38, selbständige Zustandswerte aus W03. shol ist nur in Q eine Zustandsangabe; chol bleibt Handlung. ysheol, konstitutionelles chkaiin, offene Formen und nominale Eigenschaftswerte erzeugen keinen Ausgangszustand. Keine Wörter übersprungen, kein Fenster vergrößert und keine nachträgliche Ausnahme.

**Null passende Dreierfolgen, schon vor der Prüfung sicherer Wortgrenzen.** Daher gibt es keinen Kandidatentest an einem geschriebenen Ausgangszustand. PATTERNS.tsv und PREDICTIONS.tsv sind entsprechend leer und behalten ihre Spaltenschemata.

## Vollständige Kandidatenentscheidung

| sheey-Wirkungskandidat | Vorhersage unter Ausgangslesung O | geeignete Fälle f21/f102 | geeignete Fälle andere Blätter | Entscheidung |
|---|---|---:|---:|---|
| benetzen | danach physisch feucht | 0 | 0 | ungeprüft |
| trocknen | danach physisch trocken | 0 | 0 | ungeprüft |
| abkühlen | danach physisch kalt | 0 | 0 | ungeprüft |
| erwärmen | danach physisch warm | 0 | 0 | ungeprüft |
| erhitzen | danach physisch heiß | 0 | 0 | ungeprüft |

Die ebenfalls vorregistrierte Eingangslesung I hätte aus einer vorher geltenden Qualität keinen Operationsausgang abgeleitet. Auch für sie fehlt ein passendes Muster. Kein Rivale gewinnt, kein Rivale wird widersprochen. Unabhängige Bedeutungsbestätigungskapazität: **0 für jeden Kandidaten**. Die Zustandswörter selbst bleiben zudem angenommene Übersetzungen.

## Entscheidung und nächste Grenze

Den unmittelbaren Dreierfolgen-Test hier abschließen; nicht durch längere Fenster oder passende Einzelstellen retten. „Feucht“ darf weiterhin als bedingter Entwurf verwendet werden, erhält durch W47 aber keine zusätzliche Begründung. W44–46 bleiben bytegleich. Eine weitere Arbeit muss eine tatsächlich andere geschriebene Konsequenz prüfen, beispielsweise eine anderweitig gebundene Materialveränderung; diese ist hier weder gefunden noch als nächster Test ausgewählt. Kein neuer Decoder und keine zusätzliche Glosse wurden erzeugt.

OCCURRENCES.tsv bewahrt jedes exakte Zielwort mit ganzer Quellzeile. CONTEXTS.json/.md enthalten alle 200 verfügbaren vollständigen GDT928-Absätze der Zielzeilen, sonst die ganze Zeile mit fehlender Absatzkapazität. Die übrigen Absatzwörter wurden nicht vollständig semantisch ausgewertet. Das Material war bereits projektbekannt; keine neue Seite, Bilder, Reserve, Kontakte, Signifikanz oder Pflanzennamenbehauptung. f84/f84r bleiben geschlossen.

## Reproduktion

```sh
python research_registry/proposals/translation_programs_20260912/work/W47/build.py
python research_registry/proposals/translation_programs_20260912/work/W47/validate.py
```

SPEC.json und DECISION.md vor dem Zensus geschrieben. Der separate Validator rekonstruiert alle Zielvorkommen direkt aus den Quellarrays, prüft vollständige Absatzabdeckung und enumeriert unabhängig alle Dreierfenster: PASS. Quellenbindung/Berechnung, keine Bedeutungsvalidierung. Eine anfängliche interne Ergebnisbezeichnung „physical_loci“ für lesungsübergreifende Indexpaare wurde vor Veröffentlichung korrigiert: ohne native Ausrichtung ist diese Zählung kein physischer Vorkommenszensus. Quelldaten und Testvertrag unverändert.

Die globale Repository-Prüfung bleibt bei acht bekannten Altlasten rot: sieben ungebundene GDT600-Dateien und veralteter Experimentindex. Diese Dateien wurden nicht verändert.
