# GDT1038: eine einheitliche Packungsregel trägt die ganze IT-Fortsetzung

**Begrenztes positives Ergebnis:** Alle 32 Rohgruppen von f108r.45–47 in IT2a
passen unter einer einheitlichen atomaren/zweiteiligen Wortregel genau einmal
zur bisherigen vollständigen 33-Terminal-Arbeitslesung. Kein Wortwert wurde
geändert. Die reine Ganzwortlesung scheitert dort, ebenso die Regel, jede
zerlegbare Form immer zu zerlegen. Der ursprüngliche f83r-Absatz bleibt in
beiden diplomatischen Fassungen ohne vollständige Lösung. Das ist ein
Fortschritt bei der Vereinbarkeit der Arbeitslesung mit Lesergrenzen, keine
bestätigte Übersetzung oder allgemeine Grammatik.

Öffentlich vor Berechnung registriert in Commit
`0680297a406cf84294bfd4467bc59c0c1a56c2e6`. Die vollständige Alternativtabelle
wurde anschließend separat eingefroren, bevor irgendein Fit ausgeführt wurde.
Alle 88 Bedeutungen, 13 verfassten Terminalmuster, fünf vollständigen Eingaben
und vier Modelle sind unverändert. Beide Motivationskonflikte saiin/qokeedy
waren vorher bekannt. Unabhängige Bestätigungskapazität: null Blätter.

## Vollständiger Kandidatenvergleich

Zahlen sind Anzahlen vollständiger lexikalischer Ableitungen unter den festen
Mustern, keine Wahrscheinlichkeiten. Null bedeutet kein vollständiger Fit
für die exakte jeweilige Eingabe. Die Quellunsicherheit bleibt separat.

| Ganze Eingabe | Rohgruppen | Nur Ganzwörter | Ganzwort oder Zweierteilung | Immer teilen, wenn möglich | Alte exakte Wortabstände | Ungebundene Gruppen |
|---|---:|---:|---:|---:|---:|---:|
| f83r P12-Arbeitsprojektion | 84 | 1 | 1 | 0 | 1 | 0 |
| f83r diplomatisch ZL3b | 84 | 0 | 0 | 0 | 0 | 3 |
| f83r diplomatisch IT2a | 83 | 0 | 0 | 0 | 0 | 9 |
| f108r ZL3b | 33 | 1 | 1 | 0 | 1 | 0 |
| f108r IT2a | 32 | 0 | 1 | 0 | 0 | 0 |

RF1b: kein vollständiger Absatz in der geerbten GDT928-Abdeckung, für beide
Einheiten NO_WHOLE_READER. Keine Rekonstruktion anhand fremder Lesergrenzen.
ZL f108r.46/.47 haben weiterhin anchor_eligible=false; ein Fit löst diese
Unsicherheit nicht. ZL f83r.9/.10/.12/.13/.15/.17 behalten ebenfalls ihre
negativen Quellflags. Die P12-Projektion ist eine eigene redaktionelle Fassung.

Die vollständigen 316 Rohgruppen sind in ALL_ALTERNATIVES.json enthalten.
CANDIDATE_PREDICTIONS.tsv bietet die ganze Vergleichstabelle, RESULT.json
bewahrt alle erfolgreichen Teilpfade und exakten Gesamtzahlen. Einzelne
passende Klauseln werden nicht als vollständiger Absatz gezählt.

## Was die Regel tatsächlich unterscheidet

Im ganzen IT-f108r-Absatz muss `qokeedy` auf .46/G002 als
`qokeed + y` mit den unveränderten Werten ENCLOSED_STATE + AND gelesen werden.
Dasselbe geschriebene `qokeedy` auf .47/G008 bleibt das atomare WING_TIP_OF.
Der vollständige feste Terminalstrom lässt genau diese Kombination zu.
Es gibt keinen neu gesetzten Orts- oder Kontextschalter. Die stark verfassten
Terminalmuster selbst liefern allerdings die Auswahl; ihre historische
Gültigkeit wird nicht bewiesen.

Alle anderen Formen wurden ebenso geprüft. Die vollständige Tabelle über
101 Formen (88 Lexikoneinträge plus alle weiteren Rohformen) steht in
SURFACE_ALTERNATIVES.tsv, mit jedem Vorkommens-ID. Genau sieben der vorkommenden
Formen haben mindestens eine binäre Analyse:

| Form | Atomare Annahme | Binäre Annahme |
|---|---|---|
| chedy | CLAIMS_PROTECTS | ched SELECTED_BIRD_KIND + y AND |
| lkeedy | CARRIER_REFERENCE | lkeed FAVOR_ESTEEM_AT_POWERFUL_ENCOUNTERS + y AND |
| qokeedy | WING_TIP_OF | qokeed ENCLOSED_STATE + y AND |
| saiin | ALTERNATIVELY | s ALSO + aiin OF |
| saltedy | kein atomarer Eintrag | s ALSO + altedy REQUIRE_POSITION |
| sy | THE_STONE | s ALSO + y AND |
| yched | THROUGHOUT | y AND + ched SELECTED_BIRD_KIND |

Die neue Regel kann auch das bekannte saiin und das zusätzliche saltedy in
IT-f83r lexikalisch zerlegen. Dennoch scheitern deren **ganze** Klauseln und
der ganze Absatz an den übrigen festen Eingaben. Dies ist keine zweite
vollständige Bestätigung. ALWAYS_DECOMPOSE zerstört bereits C06/C07/C08 der
alten Projektion und beide gesamten f108r-Varianten. Das bloße Finden eines
bekannten Teilworts rechtfertigt also keine obligatorische Zerlegung.

## Ganze hypothetische Fortsetzung

Die erfolgreiche IT-Ableitung behält vollständig die früher angebotenen vier
Aussagen. Sinngemäß, mit weiterhin geratenen Bedeutungen:

1. Das eingravierte Bild und der Traubenkern behalten ihre Identität.
2. Der behauptete Schutz wird an die Bedingung geknüpft, dass der Stein mit
   den ausgewählten Materialien eingeschlossen und vom selben Träger getragen wird.
3. Das unveränderte Bild soll während des Zusammenfügens auf dem Stein bleiben.
4. Die Spitze des Flügels bzw. der Feder des ausgewählten Vogels soll nach
   dem Zusammenfügen unter demselben Trägerstein bleiben.

Dies ist die alte analytische Kommentarhypothese zu Cyranides I.1.39, keine
neu identifizierte historische Fortsetzung. Die vollständige Zuordnung jedes
IT-Rohworts zu allen 33 alten Terminalwerten und unveränderten Bedeutungen
steht in EXTENSION_IT_COMPLETE_ALIGNMENT.tsv. Der heutige Test berechnet nur
die Vereinbarkeit der Zeichenfolgen mit den verfassten Tagmustern; er führt
die Bedeutungsreduktionen oder die physische Herstellung nicht nochmals aus.

## Widersprüche, Unsicherheiten und Entscheidung

Die drei ungebundenen ZL-f83r-Gruppen bleiben `{ck}al`, `q{cphh}edy` und
`dche[o:?]kedy`. In IT bleiben neun: `qofshdy`, `cheen`, `ram`, `cseckhdy`,
`ckol`, `solcheol`, `qpchedy`, `dcheo`, `kedy`. Sie wurden weder ersetzt noch
übersprungen; alle Quellpositionen stehen im Ergebnis. Ein Scheitern dieser
exakten Fassungen ist keine globale Widerlegung der geratenen Erzählung und
auch keine Erlaubnis, die Gruppen passend umzuschreiben.

**Entscheidung: LIMITED_WHOLE_EXTENSION_REPRESENTATION_FIT.** Die eine Regel
bleibt als bedingte Darstellungshypothese für die ganze f108r-Fortsetzung
brauchbar. Sie liefert keine vollständige Lesung des originalen f83r und
keinen universellen Mechanismus. Keine automatische Steigerung auf drei
Teile, neue Aliaswerte, andere Satzgrenzen oder zusätzliche Korpussuche.
GDT1023 und IDEA492 behalten ihre ursprünglichen Entscheidungen.

Die erfolgreichen drei vollständigen Eingaben haben je einen lexikalischen
Pfad unter der Hauptregel. Diese Eindeutigkeit gilt ausschließlich relativ
zu den 88 geratenen Werten und 13 verfassten Mustern. Die ursprünglichen
Materialalternativen und die direkte Stein- versus Gesamtobjekt-Zuschreibung
im Kommentar bleiben offen. Auch opake Umbenennungen der Tags passen gleich
gut. Die alten verworfenen physischen Gegenmodelle werden nicht neu geprüft;
der heutige Test liefert **keine zusätzliche Auswahl** zwischen Bedeutungen.
Es gibt kein suchweites Nullmodell und keine Signifikanzbehauptung.

Primärprogramm und unabhängig geschriebenes Prüfprogramm stimmen über die
gesamte Alternativtabelle, alle 20 vollständigen Modell/Eingabe-Ergebnisse,
sämtliche erfolgreichen Kanten und Quellmetadaten überein. 23 unabhängige
synthetische Prüfungen bestanden; zwölf zusätzliche Handerwartungen wurden
am Primäralgorithmus geprüft. Der frühere Konsolentext nannte diese zwölf
versehentlich vierzehn, ohne Auswirkung auf den Manuskriptlauf. Alle 16
Registrierungsbindungen bleiben unverändert. Bestätigte Wörter: **0**.
