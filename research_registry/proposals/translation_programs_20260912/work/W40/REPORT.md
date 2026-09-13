# W40 — Mengenvergleich mit zusätzlicher Gleichung

**Auf f93r erzwingen die festen Absatzverträge von P14 nun B=C: dain und daiin müssten denselben positiven Wert tragen.** Das gilt im Mengenmodell M und im Verhältnismodell R. Es ist eine neue Konsequenz des erweiterten Arbeitskorpus, keine unabhängig gefundene Wortbedeutung. Insbesondere folgt weder „eins“ noch „Gleichteile“. Eine Lesung mit verschiedenen festen Zahlen für dain/daiin ist mit diesen vollständigen Absatzverträgen unvereinbar.

Die Voraussetzung ist stark: Dasselbe Materialwort bezeichnet im ganzen Absatz dieselbe zeitlich konstante Masse; der Bezug läuft über ungelesene Wörter weiter. Beim zeilenweisen Zurücksetzen verschwindet die Gleichung. Deshalb wird weder B=C als allgemeiner Wortwert übernommen noch der Absatzvertrag ausgewählt.

## Vollständige Kandidaten- und Vorhersagetabelle

Vorregistrierung: [DECISION.md](DECISION.md), [SPEC.json](SPEC.json). IDEA000088 wurde auf diesen konkreten Teilvergleich beschränkt. Unverändertes P14-Lexikon, Werte dair=A/dain=B/daiin=C, beide ursprünglichen Bereichsregeln. Keine W38-Bedeutungen importiert.

| Kandidat | Vorhersage jeder gebundenen Wertstelle | Beobachtete Modellfolgen an allen 40 Stellen | Widerspruch / fehlende Bezüge | Verbleibende Mehrdeutigkeit | Unabhängige Bestätigung |
|---|---|---|---|---|---|
| G / Absatz | Material besitzt die zuletzt geschriebene Qualität im Grad A/B/C. | 11 vollständige Felder. | 29 ohne erforderliche Material-/Qualitätsbezüge. | Achse und Skala nicht identifiziert; keine Zahlenelimination zulässig. | 0 |
| M / Absatz | Masse(Material)=A/B/C·U, gemeinsame offene Einheit je Absatz. | 27 Gleichungen; eine unabhängige Wertgleichung B=C. | 13 ohne Material. B≠C wäre ein Widerspruch zum Gesamtvertrag. | A und gemeinsamer Wert B=C bleiben frei; Einheit offen; Fernbezug und konstante Menge unbewiesen. | 0 |
| R / Absatz | Masse(Material)/Masse(vorheriges anderes Material)=A/B/C. | 20 Gleichungen; dieselbe unabhängige Wertgleichung B=C. | 20 ohne Zähler/Nenner. B≠C wäre ein Widerspruch zum Gesamtvertrag. | A und B=C frei; Nennerregel und Mengenidentität unbewiesen. | 0 |
| G / Zeile | Gleiche Gradforderung, Bezug an jeder Zeile zurückgesetzt. | 3 vollständige Felder. | 37 unvollständig. | Keine Gradskala oder Zahl identifiziert. | 0 |
| M / Zeile | Gleiche Massenforderung, syntaktisch nur innerhalb der Zeile. | 13 Gleichungen, keine Wertgleichung. | 27 ohne Material. | Jede positive Wahl A/B/C erfüllbar; Einheit offen. | 0 |
| R / Zeile | Gleiche Verhältnisforderung, syntaktisch nur innerhalb der Zeile. | 5 Gleichungen, keine Wertgleichung. | 35 unvollständig. | Jede positive Wahl A/B/C erfüllbar; Nennerregel offen. | 0 |

[Alle 80 Bereichs-/Wertfälle](FIELDS.tsv) enthalten konkrete Loci, Träger, Eigenschaften, Nenner und fehlende Rollen. Keine passende Einzelstelle wurde aus dem Korpus ausgewählt. Die Modelle M/R werden getrennt gerechnet; ihre Gleichungen dürfen nicht gemeinsam als Messungen benutzt werden. Weniger benötigte Rollen oder weniger Fehler beweisen keine Bedeutung. Beide M-/R-Systeme haben mindestens die positive Lösung A=B=C=1 mit passenden Massen, wählen diese aber nicht aus.

## Die neue Gleichung und ihr vollständiger Zwischenabschnitt

| Wertstelle | Eingetragener Wert | Fester Absatzträger | Fester Absatznenner |
|---|---|---|---|
| f93r.22:4 daiin | C | cthy, f93r.22:2 | cthol, f93r.20:2 |
| f93r.29:1 dain | B | dasselbe cthy, f93r.22:2 | dasselbe cthol, f93r.20:2 |

Unter M sagt die erste Stelle „Krautmenge C·U“, die zweite „dieselbe Krautmenge B·U“. Unter R lauten beide Angaben „Krautmasse bezogen auf dieselbe cthol-Masse“, einmal mit C, einmal B. Subtraktion in logarithmischen Größen ergibt log(B)−log(C)=0, also B=C. Der genaue algebraische Stellenzeuge steht für beide Modelle in [ALGEBRA.json](ALGEBRA.json). Es handelt sich um zwei Angaben zu derselben angesetzten Beziehung, nicht um eine neue mehrgliedrige Mischungsbilanz.

```text
f93r.20 ychockhy cthol osos
f93r.21 dol shol daiin shcthy
f93r.22 kchor cthy chakal daiin
f93r.23 oain okor shody teols
f93r.24 ychocthy chotey teey s
f93r.25 ysaiin chotar shody
f93r.26 ocheodaiin tchos sor
f93r.27 qokor cheo los ckheody
f93r.28 ychor odol chodaiin s
f93r.29 dain {ck}cho ctho ctho[s:e]g
```

Zwischen den beiden Wertstellen stehen **22 unter diesem alten Lexikon ungelesene Gruppen**. Sie werden weder gelöscht noch als bedeutungslos erklärt. Das Modell erkennt dort keinen neuen Materialnamen; das ist kein Beweis, dass der Schreiber keinen neuen Gegenstand, Bezug oder mengenverändernden Vorgang nennt. Die konstante Fernbindung war vorab als Modellannahme festgelegt. Ihre Schwäche wird nicht durch nachträgliche Umhängung repariert. Im Zeilenmodell hat das anfängliche dain auf .29 überhaupt keinen linken Träger.

Die ältere einfache Zahlenlesung B=2/C=3 würde diese Gleichung verletzen. Der Test entscheidet jedoch nicht zwischen gleichen Wortwerten, anderen Bezügen und einer zwischenzeitlich geänderten Menge. Er verbietet nur, unterschiedliche feste Zahlen **und zugleich** den hier geprüften konstanten Absatzbezug als widerspruchsfreie Gesamtlesung auszugeben.

## Abdeckung und Entscheidung

Alle **17 exponierten Absätze / 169 Zeilen / 1045 Gruppen** wurden verarbeitet. Das alte P14-Lexikon belegt hier nur 186 Positionen; 859 bleiben ungelesen. Dies ist ein bewusst getrennter Vergleich, keine Rücknahme oder Verbesserung der W38-Abdeckung. [Abdeckung je Absatz](COVERAGE.tsv), [vollständige sechs Lesungen mit Rohzeilen](READING.md), [maschinelle Ausrichtung](READINGS.tsv), [alle 28 Bereichs-/Handlungsfälle](ACTIONS.tsv).

Die ursprünglichen vier P14-Absätze sind mit sämtlichen 145 Rohgruppen und allen 20 Bereichs-/Wertbindungen unverändert enthalten. Dortige Ergebnisse bleiben bestehen. Neu hinzukommen 900 Gruppen und die oben ausgewiesene Wertgleichung; keine neue Seite wurde geöffnet. Die Gleichung schließt keine Dimension aus, da M und R dieselbe Wertbedingung liefern. G liefert mangels erkannter Qualität an den beiden Zeugen keine alternative Zahl.

**Entscheidung: keine Zahl übersetzen; den konstanten absatzweiten Mengenbezug nicht mit einer unterschiedlichen dain-/daiin-Zahlenleiter kombinieren.** B=C bleibt eine dokumentierte bedingte Lesung. Kein automatischer Eingriff in Lexikon, Nenner-, Zeit- oder Bezugsregeln. P14 und W36–W38 bleiben unverändert. Die Idee ist damit in diesem Vertrag geprüft, nicht als allgemeine Klassenhypothese vollständig ausgeschöpft.

Getrennter Prüfcode rekonstruiert alle 80 Wertbindungen aus linken Quellabschnitten. Ein Graphpotential-Verfahren prüft die Zahl und den Raum der Wertzwänge unabhängig von der vollständigen Matrixelimination; jeder ausgegebene Stellenzeuge hebt sämtliche Materialgrößen exakt auf. [VALIDATION.json](VALIDATION.json): PASS. Gleicher Bearbeiter, keine unabhängige Bedeutungsprüfung. Keine Signifikanz, bestätigte Pflanzen-/Wortnamen oder scorefähige Relationsevidenz. Die Arbeitsdaten und früheren Beispiele waren exponiert; f84/f84r und alle Reserveseiten blieben geschlossen.

Reproduktion aus Repositorywurzel:

```sh
python research_registry/proposals/translation_programs_20260912/work/W40/build.py
python research_registry/proposals/translation_programs_20260912/work/W40/validate.py
```

Publikationsprüfung: Der auf diese Dateien begrenzte Datenschutz-/Umfangsscan bestand. Die separate globale Prüfung bleibt wegen bestehender ungebundener GDT600-Reproduktionsdateien und eines veralteten Experimentindex negativ. Die dabei gemeldete Überschreitung der kompakten Route wurde durch Entfernen zweier Leerzeilen behoben; keine historischen Experimentdateien verändert.
