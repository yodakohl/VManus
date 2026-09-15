# GDT960 — kein beobachteter Pflanzenname aus der vollständigen Stern-Pflanzen-Verteilung

Keine der88 vollständig geprüften Kombinationen besitzt eine Wortzuordnung, die
alle erforderlichen Pflanzenvorkommen tatsächlich lesbar abdeckt. **60 Fälle
widersprechen der Hypothese;28 bleiben ausschließlich durch Ergänzungen unbekannter
Gruppen möglich.** Alle28 stammen aus ZL3b. Kein Pflanzennamenkandidat wird übernommen.
GDT888/913 und alle früheren Schlüssel bleiben unverändert.

|Edition|ganze15-Absatz-Folgen|Fälle mit beiden Quellenmodellen/Richtungen|beobachtete Gesamtzuordnung|widersprochen|nur unbekannte Ergänzungen|
|---|---:|---:|---:|---:|---:|
|ZL3b|10|40|0|12|28|
|IT2a|12|48|0|48|0|
|RF1b|0|0|keine Kapazität|nicht geprüft|nicht geprüft|

Die88 Fälle enthalten alle22 Folgen, zwei feste Reihenfolgen und zwei vorab
festgelegte Arten, Pflanzenteile zu behandeln. Es wurden keine passenden Absätze
herausgegriffen. [Kandidaten-/Ergebnistabelle](artifacts/CANDIDATE_TABLE.tsv),
[2904 konkrete Pflanzenvorhersagen](artifacts/PLANT_PREDICTION_TABLE.tsv),
[sämtliche Kandidatendaten](artifacts/ALL_CASES.json.gz) und
[alle ganzen Textfolgen](artifacts/ALL_WINDOWS.json.gz) sind veröffentlicht.

## Die konkrete Inhaltskonsequenz

Agrippas *De occulta philosophia* I.32 zählt15 Sterne mit zugehörigen Pflanzen auf.
Die hier kollationierte1651-Überlieferung ist über [EEBO](https://quod.lib.umich.edu/e/eebo/A26565.0001.001/1%3A16.32?rgn=div2%3Bview=fulltext)
und [Wikisource](https://en.wikisource.org/wiki/Three_Books_of_Occult_Philosophy/Book_1/Chapter_32)
nachvollziehbar. Eine15er-Zahl allein wäre keine Wortbedeutung. Der neue Test
verlangt deshalb das gesamte Netz ihrer mehrfach geteilten Pflanzennamen:

|Quellenname als Pflanzenidentität|Einträge mit geforderter Nennung|
|---|---|
|Mugwort|1,4,5,7,8,10,15|
|Mandrake|4,10,15|
|Succory|8,14|
|Perwinkle|8,10|
|Trifoile|10,12|

Auch alle nur einmal genannten Pflanzen müssen gleichzeitig eine eigene Form
bekommen. Insgesamt sind es43 Pflanzenzuordnungen:32 Pflanzenidentitäten oder34
getrennte Materialien, wenn Mandragorawurzel und Immergrünblüten eigene Namen
tragen. Die vollständigen Quellenzeilen und alle expliziten Aliasentscheidungen
stehen in [SOURCE.json](src/SOURCE.json). Historische Namen wie Diacedon oder
Quadraginus bleiben Quellenbezeichnungen; eine moderne Artidentifikation wurde
nicht behauptet. Bur und Quadraginus wurden nicht nachträglich zusammengelegt.

Die Hypothese fordert je Pflanze/Material dieselbe vollständige rohe Voynichgruppe
in allen zugehörigen Absätzen und keine bekannte Nennung in den übrigen Einträgen.
Das ist eine konkrete Darstellungsannahme, keine bereits bewiesene Schreibweise.
Alle anderen Wörter, Sternnamen, Steine, Tiere und Metalle bleiben unübersetzt.
Die Quelle ist ein später Zeuge; das genaue15-Zeilen-Verzeichnis wurde nicht als
unveränderte Vorlage von1420 zertifiziert.

## Was die möglichen Ergänzungen wirklich tragen

Schon der gemeinsame Quellenname Mugwort besitzt in **keinem** der88 Fälle einen
Träger mit allen sieben erforderlichen bekannten Absatzvorkommen. In sämtlichen
60 widersprochenen Fällen bleibt sogar seine obere Formmenge leer: Auch unter
den registrierten Ergänzungsmöglichkeiten kann keine einzige konsistente Form
sein vollständiges Vorkommensmuster erfüllen. Die übrigen Namen wurden dennoch
vollständig und gemeinsam geprüft.

Die28 rechnerisch möglichen Fälle enthalten jeweils64–102 unbekannte Gruppen.
Für Mugwort deckt selbst die bestgestützte mögliche Form höchstens vier der
sieben notwendigen Absätze lesbar ab. Mindestens drei notwendige Nennungen
müssten dort erst aus unbekannten Gruppen entstehen. Die
[vollständige Stützentabelle](artifacts/REPEATED_PLANT_OBSERVED_SUPPORT.tsv) trennt
für alle mehrfach genannten Pflanzen lesbare Vorkommen von solchen Ergänzungen.

Ein besonders instruktiver scheinbar eindeutiger Fall ist ZL3b/f103r in umgekehrter
Quellenreihenfolge: Eine15-Absatz-Folge erlaubt für Mugwort nur `sheckhy`, die
nächste nur `qokey`. Beide Formen sind aber jeweils nur in **zwei von sieben**
notwendigen Absätzen bekannt; fünf weitere Vorkommen werden ausschließlich in
Lücken angenommen. Beide Quellenmodelle teilen diese Fälle. Das ist keine
Übersetzung von `sheckhy` oder `qokey` als Beifuß. Die benachbarten Folgen sind
überlappend und widersprechen einer Auswahl allein nach lokaler Eindeutigkeit.
Die vollständigeren IT2a-Fälle widersprechen dem Gesamtmodell durchgehend.

Eine hypothetische Ergänzung ist ein gemeinsames Modell für alle Pflanzen:
verschiedene Namen dürfen weder dieselbe Form noch denselben unbekannten Platz
verwenden. Die veröffentlichten Zeugen und vollständigen möglichen Formmengen
berücksichtigen diese Bedingungen; getrennte passende Einzelwörter wurden nicht
als Gesamtlexikon gezählt. Die Zahl der oberen Gesamtlexika ist ausdrücklich
nicht gezählt. Ein einzelner Solver-Zeuge begründet keine Eindeutigkeit.

Mehrere nur einmal erwähnte Namen derselben Quellenzeile bleiben auch bei einem
Fit gegeneinander austauschbar. Alle solchen unvermeidbaren Gruppen sind in
[SOURCE_EQUIVALENCE_CLASSES.json](artifacts/SOURCE_EQUIVALENCE_CLASSES.json)
aufgeführt. Die [beobachteten Wortverteilungen](artifacts/ALL_WINDOW_WORD_MASKS.tsv)
und eingefrorenen Sollmasken machen auch jeden ausgeschlossenen Formkandidaten
nachvollziehbar: Eine zusätzliche bekannte Zeile oder eine erforderliche Zeile
ohne unbekannten Platz schließt ihn aus.

## Abgrenzung, Prüfung und Entscheidung

Die öffentliche Registrierung **4ec67acb0** lag vor der Wortinzidenz-Auswertung.
Die frühen Metadatenzählungen und sämtliche vorherige Projektexposition sind im
[Protokoll](PREREGISTRATION.md) offengelegt. Verwendet wurden eigene vollständige
Absätze aus GDT928 und unveränderte rohe Gruppen/Grenzen aus GDT915, innerhalb der
179 Textselektoren. Die22 Folgen liegen auf fünf exponierten physischen Blättern:
f103,f106,f107,f108,f113. Jeder Kandidat nutzt ein Blatt und hat **null unabhängige
Bestätigungsblätter**. Überlappende Folgen und alternate Transkriptionen sind keine
unabhängigen Wiederholungen. RF1b hat keine eigenen Absatzgrenzen und deshalb
keine Prüfkapazität. Es wurden keine neuen Bilder, Reserven, f84/f84r oder f116v
geöffnet. Die besondere Bildgrenze für f106v blieb bestehen.

Der separat implementierte Validator (**PASS**) in [VALIDATION.json](artifacts/VALIDATION.json) prüft die
Quelleninzidenzen, Rohgruppen, vollständige Folgenmenge, exakten unteren Anzahlen,
gemeinsamen oberen Bedingungen und möglichen Formmengen. Das prüft Daten und
Rechnung, keine Manuskriptbedeutung. Ein anfänglicher Fehler des Prüfprogramms
und ein späteres Zeitlimit sind im [Korrekturbeleg](src/VALIDATOR_NOTES.md)
festgehalten. Root stellte die separate Implementierung fertig; alle17116
Formmöglichkeiten wurden über exakt geprüfte Vertauschungsklassen nachgerechnet. Ausgaben wurden um explizite Gründe für
unbekannte Gruppen sowie die Stützentabelle ergänzt; die wissenschaftlichen
Prädikate und Resultate änderten sich dadurch nicht.

**Entscheidung:** Die feste Darstellung als geordnete15-Absatz-Folge mit einem
unveränderten ganzen Wort pro Pflanze liefert keinen beobachteten Bedeutungsgewinn.
Die28 Ergänzungsfälle werden nicht zu Pflanzenlesungen aufgewertet. Keine weitere
Präfix-, Endungs-, Reihenfolge- oder Absatzreparatur aus diesem Ergebnis. Das ist
keine allgemeine Widerlegung astraler Pflanzenmedizin oder dieser historischen
Quellenfamilie. Ohne Gegenkontrolle der gesamten Suche keine Signifikanzbehauptung;
ohne unabhängige Bedeutungsprüfung keine bestätigten Pflanzennamen.
