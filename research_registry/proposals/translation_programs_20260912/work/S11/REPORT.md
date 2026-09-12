# S11 — S10s Entscheidungen unterscheiden keine Behauptungs-/Beobachtungsrichtung

Der vollständige Vergleich liefert eine klare Grenze des Warenprüfungsentwurfs: **Alle drei Entscheidungen bleiben gleich, wenn statt der ersten die letzte Klassenstelle als behauptete Ware gilt.** In den beiden gebundenen Fällen wechseln damit die Rollen tatsächlich. S10s zwei Modellpassungen enthalten also keine Information darüber, welche Nennung Behauptung und welche Beobachtung wäre.

Das gilt nicht bloß zufällig für diese Beispiele. Die feste S10-Regel lässt sich auf Klassenhomogenität reduzieren: verschiedene Klassen → verwerfen; mindestens zwei gleiche Klassen plus letzte Qualität trocken → annehmen; sonst unbekannt. Die Wahl der behaupteten Klasse unter den genannten Klassen spielt für diese Regel keine Rolle. Mehr Beispiele allein mit genau dieser Regel würden die Richtung ebenfalls nicht identifizieren.

## Alle Entscheidungen in beiden Richtungen

| Entscheidung | FIRST: Behauptung / Beobachtung | LAST: Behauptung / Beobachtung | Erwartung in beiden |
|---|---|---|---|
| f17r.5:9 qody | chor .5:3 / shor .5:4 | shor .5:4 / chor .5:3 | verwerfen; gleiche S10-Modellpassung |
| f21r.9:4 chkaiin | keine Klasse vorhanden | keine Klasse vorhanden | unbekannt; weiterhin unbegründet |
| f21r.12:8 chkaiin | chor .12:2 / chor .12:5 | chor .12:5 / chor .12:2 | annehmen; gleiche S10-Modellpassung |

[DECISIONS.tsv](DECISIONS.tsv) enthält alle sechs Richtungs-/Entscheidungszeilen. LAST liest zuerst genannte Beobachtungen vor einer späteren Warenbezeichnung; es benutzt an jeder Entscheidung nur den bereits vorhandenen Recordpräfix. Keine spätere Nennung wird einer früheren Entscheidung zugeschoben. Es ist eine Rollenalternative, keine behauptete erkannte Satzstellung.

Die sechs S10-Wortwerte bleiben unverändert: chor=Blütenmaterial, shor=Samenmaterial, chol=trocken, shol=feucht, chkaiin=annehmen, qody=verwerfen. Kein neues Wort wurde zugewiesen. Alle145Gruppen stehen in beiden vollständigen Wortlesungen [FIRST](READING_FIRST.md) und [LAST](READING_LAST.md), mit19hypothetischen Werten und126offenen Positionen. Die Tabellen heißen ALIGNMENT_FIRST/LAST.tsv.

## Vollständige Begleitfolgen

Der attraktive f21r-Satz lautet vollständig:

`ykeey chor sheey ysheol chor chol daiin chkaiin`

Unter S10 bleibt das: `⟦ykeey⟧ Blütenmaterial ⟦sheey⟧ ⟦ysheol⟧ Blütenmaterial trocken ⟦daiin⟧ annehmen`. Die offenen Wörter erhalten keine heimliche Bedeutung wie „angeboten als“, „erkenne an“ oder „echt“.

| Entscheidungskontext | Zwischen den Klassen | Nach letzter Klasse bis Entscheidung |
|---|---|---|
| f17r.5:9 | keine Gruppe zwischen chor und shor | cphor cphaldy dair cthey |
| f21r.12:8 | sheey ysheol | chol daiin |
| f21r.9:4 | keine Klasse im Präfix | vollständiger klassenloser Präfix: fcho kshy otor sheol ocphal opsheas cthodaiin oty okaiin sho tshaiin |

[SPANS.tsv](SPANS.tsv) erhält alle fünf Bereiche einschließlich des leeren Zwischenraums; [COMPANIONS.tsv](COMPANIONS.tsv) alle19Positionen darin. [ALL_COMPANION_OCCURRENCES.tsv](ALL_COMPANION_OCCURRENCES.tsv) gibt zu jedem Begleitwort sämtliche exakten Vorkommen im gesamten145-Gruppen-Paket aus, nicht nur die attraktive Stelle. Die ganzen Reader enthalten zusätzlich alle Wörter vor der ersten Klasse und außerhalb der Entscheidungsbereiche.

sheey und ysheol kommen in diesem Paket jeweils nur einmal vor. Sie liefern daher hier keinen wiederkehrenden Rahmen, mit dem die angenommene Rollenrichtung verglichen werden könnte. Das ist keine Aussage über ihre Häufigkeit im ganzen Manuskript. Daiin wird nicht zerlegt: die genaue Form daiin wiederholt sich achtmal, bleibt aber in S10 ohne Wert. Ihre Rekurrenz allein beweist keine Prüfrelation. Chol ist als Qualität angesetzt; die übrigen Begleitwörter bleiben offen. Insbesondere sheey wird nicht mit shey normalisiert.

## Warum die Regel richtungsblind ist

Wähle irgendeine der vorhandenen Klassen als behauptete Ware. Wenn mindestens zwei verschiedene Klassen vorhanden sind, unterscheidet sich mindestens eine andere Nennung von der gewählten Klasse. Die Regel verwirft daher unabhängig von dieser Wahl. Wenn alle Nennungen gleich sind, gibt es bei mindestens zwei Nennungen immer eine passende Vergleichsnennung, wiederum unabhängig von der Wahl; dann entscheidet nur die unveränderte Trockenheitsbedingung. Bei keiner oder nur einer Nennung fehlt der erforderliche Vergleich.

[RULE_REDUCTION.json](RULE_REDUCTION.json) hält diese allgemeine Reduktion fest. Der Validator prüft zusätzlich alle zweiwertigen Folgen bis Länge6, alle gewählten Kopfpositionen und drei Qualitätszustände gegen dieselbe Reduktion. Das ist eine Rechenprüfung der logischen Aussage, kein statistischer Nulltest und kein Beleg für Warenprüfung. Eine rollenabhängige Entscheidungsregel wäre ein anderer Versuch.

## Entscheidung

**Die S10-Regel kann Behauptung und Beobachtung nicht identifizieren; diesen festen Auswahltest stoppen.** Die zwei ausgeschriebenen Warenprüfungsgeschichten bleiben mögliche Entwürfe. Ihre bisherigen Passungen rechtfertigen jedoch weder die behauptete Satzrichtung noch den Handelskontext. Auch die Zutaten-/Stofflistenfassung bleibt offen.

Der Begleitwortvergleich liefert keine bereits bedeutungsgebundene asymmetrische Relation. Die fehlende Bedeutung könnte theoretisch in offenen Gruppen liegen; sie wurde nicht gefunden. Neue Glossen genau an diesen Einzelstellen wären zusätzliche Konstruktion und werden hier nicht als Lösung eingeführt. S10 wird nicht rückwirkend umgeschrieben. Sein Resultat lautete bereits exponierte Modellpassung, keine unabhängige Bestätigung; S11 präzisiert nun die strukturelle Nicht-Identifizierbarkeit der Rollen.

Für eine Fortsetzung sollte eine andere dokumentierte Idee mit rollenabhängigen Konsequenzen ausgewählt werden. Keine weitere Serie von gleichheitsbasierten chor-Entscheidungen und keine neue Behauptungsmarkierung aus Einzelvorkommen. Ein konkreter nächster Kandidat ist noch nicht ausgewählt.

Vorgänger: S10 primär, GDT768 primär zu offener chor/shor-Richtung gelesen. Dessen ältere Bedeutungs-/Strukturdeutungen werden nicht als unabhängige Anker übernommen und sein größerer Korpus wurde nicht neu geöffnet. Alle145Gruppen waren exponiert; keine Reserveprüfung, kein neues Bild, keine Kontakte; f84/f84r geschlossen. Keine bestätigte Wortbedeutung, unabhängige Bedeutungsprüfung0, keine Signifikanzbehauptung.

Reproduktion: `python research_registry/proposals/translation_programs_20260912/work/S11/build.py`, anschließend `python research_registry/proposals/translation_programs_20260912/work/S11/validate.py`. Quellen-, Vollständigkeits-, Begleitwort- und Algebra-Prüfung PASS; keine historische Bedeutungsvalidierung. [DECISION.md](DECISION.md), [SOURCE.json](SOURCE.json), [RESULT.json](RESULT.json).

Repository-Prüfungen: S11-Validator, Registry und exakter Veröffentlichungsbaum auf private Inhalte/Diff-Fehler PASS. Globale Altbestandsprüfung unverändert acht bekannte Fehler: sieben ungebundene GDT600-Reproduktionsdateien und veralteter Experimentindex; nicht geändert. IDEA000192/193 sind separat ergänzte ungeprüfte Rohideen, keine S11-Befunde.
