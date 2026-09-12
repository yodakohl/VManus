# P16 — Bedingungen, Ausnahmen und Verneinung

Der Durchgang ergibt vier vollständig gebundene Regelkandidaten und einen konkreten Unterschied im zweiten Absatz: Die bedingte Fassung lässt den Zustand von Stoff B offen, während die Aufzählung ihn als warm behauptet. Die übrigen Aussagen desselben Absatzes fordern in beiden Fassungen „A ist warm; A nicht erhitzen“. Diese Werte sind Hypothesen, keine Übersetzung. Die neue Grammatik löst die Zustandswidersprüche im ersten und dritten Absatz nicht.

Alle 341 Gruppen der sieben f83r-Records wurden in C (bedingt) und U (unbedingt) ausgeführt. Neun angenommene ganze Wortwerte betreffen 73 Positionen; 268 bleiben offen. Alle 15 Verknüpfungsstellen, 38 Prädikatsstellen und 126 Fallzeilen sind dokumentiert. Keine Stellen wurden nach ihrer Passung ausgewählt oder weggelassen.

## Vier konkrete Regeln und ihre Bereiche

| Verknüpfung | Linke und rechte Prädikatsstelle | C: konkrete Folgerung | U: unbedingte Gegenlesung |
|---|---|---|---|
| qokal .6:3 | kalt(B) .5:9; erhitze(A) .6:6 | Außer wenn B kalt ist, erhitze A | B ist kalt; erhitze A |
| qokal .12:9 | warm(A) .12:8; warm(B) .13:7 | Außer wenn A warm ist, ist B warm | A ist warm; B ist warm |
| sol .20:5 | warm(B) .20:4; warm(B) .20:7 | Wenn B warm ist, ist B warm | B ist warm; B ist warm |
| sol .21:4 | warm(B) .21:2; erhitze(B) .21:5 | Wenn B warm ist, erhitze B | B ist warm; erhitze B |

[Exakte Regelbereiche](RULES.tsv), [sämtliche Operatoren einschließlich Fehlern](OPERATORS.tsv), [sämtliche Prädikate mit Material- und Negationsbezügen](PROPOSITIONS.tsv). Die Materialzuweisung folgt stets der letzten gewählten Materialnennung im selben Record. Andere Wörter in diesen Bereichen bleiben offen. Die dritte Regel ist eine Tautologie; sie liefert keine neue Sachinformation. „Warm → erhitzen“ wird nicht als naturwissenschaftlich unmöglich bezeichnet, bleibt aber ohne Temperaturziel oder Zweck inhaltlich schwach.

## Falltabelle in Alltagssprache

| Regel | Auslösender Fall in C | Anderer Fall in C | Zusätzliche Behauptung von U |
|---|---|---|---|
| Ausnahme .6:3 | B warm oder weder warm noch kalt: A erhitzen | B kalt: diese Regel sagt nichts über Erhitzen von A | B kalt, A unbedingt erhitzen |
| Ausnahme .12:9 | A kalt oder weder warm noch kalt: B warm | A warm: diese Regel sagt nichts über B | A und B unbedingt warm |
| Bedingung .20:5 | B warm: B warm | B nicht warm: keine Behauptung aus dieser Regel | B unbedingt warm |
| Bedingung .21:4 | B warm: B erhitzen | B nicht warm: diese Regel gibt keine Anweisung | B warm und unbedingt erhitzen |

Nichtauslösung bedeutet weder das Gegenteil des Ergebnisses noch ein Handlungsverbot. Die Voraussetzungen sind in C keine allein durch die Regel behaupteten Tatsachen. [ALL_CASES.tsv](ALL_CASES.tsv) enthält für jeden ganzen Record alle neun Kombinationen A/B je warm, kalt oder neutral, in beiden Fassungen, mit allen aktiven Aussagen, erforderlichen/verbotenen Handlungen, verletzten Zustandsbehauptungen und ungebundenen Teilnehmern.

## Ganze Absätze statt passender Einzelregeln

P1, 72 Gruppen: Der konkrete Ausnahmesatz verbindet B als Bedingung mit einer Handlung an A. Das könnte einen Zusammenhang zwischen zwei Stoffen beschreiben; dessen Zweck ist nicht gelesen. Gleichzeitig wird A auf .2:7 kalt und auf .4:3 warm genannt. Unter dem vorab festgelegten gemeinsamen Zustandszeitpunkt ist keine der neun Fallkombinationen möglich, in C ebenso wenig wie in U. Der ungebundene erste sol-Anschluss bleibt offen. Die beiden chey auf .3:4 und .3:6 beziehen sich nach derselben Regel auf .4:2: doppelte Negation, kein einzelnes bequemes Verbot.

P2, 84 Gruppen: Die mögliche Lesung lautet in ihrem gebundenen Kern: „A ist warm. Außer wenn A warm ist, ist B warm. A nicht erhitzen.“ Die erste Warmbehauptung auf .11:6 gilt unabhängig von der späteren Ausnahme. Daher löst diese Ausnahme in jedem konsistenten Fall nicht aus; B bleibt frei. C lässt drei Zustandskombinationen zu, U nur A warm/B warm. Das ist eine konkrete unterschiedliche Aussage, aber noch kein beobachteter Entscheidungsgrund zugunsten von C. Der anfängliche qokedy auf .9:3 hat keinen Materialbezug; „kühle B“ auf .14:2 bleibt in beiden Fassungen eine zusätzliche Anweisung. Die vollständigen Wortlesungen stehen in [P1 C](F83_P1_C.md), [P1 U](F83_P1_U.md), [P2 C](F83_P2_C.md), [P2 U](F83_P2_U.md).

P3, 63 Gruppen: Zwei gebundene Wenn-Regeln, darunter die Tautologie. Die unbedingten Aussagen kalt(B) .20:2 und warm(B) .21:8 widersprechen einander weiterhin im gemeinsamen Zustand. Null konsistente Kombinationen in C und U. qokal .23:3 folgt nach unserer Regel einer Handlung statt einer Zustandsaussage und bleibt ungebunden; keine Sonderausnahme wird ergänzt.

P4, 33 Gruppen: Keine gewählte Verknüpfung. Drei konsistente Zustandskombinationen in beiden Fassungen; ein früher Zustand und Handlungen haben ungebundene Teilnehmer. P5, 62 Gruppen: Keine vollständige Regel; seine sol-/chey-Bereiche bleiben ungebunden. Neun formal konsistente Kombinationen bedeuten hier geringe Aussagebindung, nicht gute Übersetzung. Q1, 11 Gruppen: sol und die Erhitzungsanweisung besitzen keinen Stoffbezug; ebenfalls neun formal konsistente Fälle. Q2, 16 Gruppen: Nur sol/chey sind mit Hypothesen versehen, beide ungebunden; neun Fälle ohne gebundene Sachinformation.

Alle übrigen vollständigen Leser heißen entsprechend F83_P3_C.md bis F83_Q2_U.md. [C-Ausrichtung](ALIGNMENT_C.tsv), [U-Ausrichtung](ALIGNMENT_U.tsv), [Abdeckung und Fallzahlen](COVERAGE.tsv). Acht der 15 Operatorstellen bleiben ungebunden. Von fünf chey sind drei an Prädikate gebunden: zwei bilden die doppelte Negation in P1, eines verbietet Erhitzen in P2; zwei bleiben ungebunden. Keine Fallzeile fordert und verbietet dieselbe Handlung zugleich. Die tatsächlichen Widersprüche betreffen hier Zustandsbehauptungen, nicht automatisch die Abfolge von Erhitzen und Kühlen.

## Entscheidung und Abgrenzung

Die beiden Fassungen als konkrete partielle Gegenlesungen aufbewahren; keine auswählen. Die Ausnahme in P2 zeigt einen echten Unterschied der angesetzten Aussagen. Größere logische Freiheit in C bestätigt aber keinen Ausnahmeoperator: sie entsteht definitionsgemäß durch den Wegfall unbedingter Behauptungen. Die aktuelle gemeinsame Zustandslesung bleibt für P1 und P3 widersprüchlich. Eine zeitliche Gliederung könnte andere Folgen haben, wäre eine neue ausgewiesene Fassung und wurde nicht stillschweigend benutzt. Kein allgemeiner Ausschluss bedingter oder zeitlicher Prosa.

GDT269 liefert keine Wenn-Bedeutung für q; GDT752 keine unabhängig bestätigte q-Qualitätsregel. IDEA000031s ungeklärte Gegenkontrolle wird nicht übernommen. GDT899/908 betreffen einen festen Astrolabium-Vertrag, dessen ursprüngliche Befunde unverändert bleiben. Alle jetzigen Werte einschließlich warm/kalt, Nachstellung, Negationsbereich und Teilnehmeridentität sind neue freie Annahmen auf exponiertem Material. Frühere P12/P15/P07/P26-Lesungen wurden gesehen; keine unabhängige Bestätigungskapazität, keine Signifikanzbehauptung.

Keine neuen Seiten, Bilder, Kontakte oder Reservetests. f84/f84r geschlossen; HERB4 nicht ausgeführt. Keine nahezu vollständige Lesung bei 268 offenen Gruppen. Nächster Kandidat zur Primärprüfung: P21, Flexionsformen ganzer Aussagen.

Reproduktion: aus Repositorywurzel `python3 research_registry/proposals/translation_programs_20260912/work/P16/build.py`, dann entsprechend `validate.py`. SOURCE.json bindet die bereits begrenzte Projektion und die vor dem Lauf geschriebene DECISION.md per SHA256. Der Validator rekonstruiert alle 126 Fallzeilen als Mengen von Behauptungen und Befehlen und prüft Quellabdeckung, nächste Bereichsenden und Negationsparität. Das prüft Modellkonsequenzen, nicht Bedeutungswahrheit.
