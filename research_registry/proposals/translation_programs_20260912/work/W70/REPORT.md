# W70: gemeinsamer Ablauf mit sichtbaren Abzweigungen

**Ein bedingter Ablauf auf f75v.45 bleibt unter beiden W69-Fassungen erhalten:** „Den erwärmten Anteil anhaltend erhitzen, [nochmals] anhaltend erhitzen, mäßig erwärmen; fertig.“ Die vier Prädikate werden jeweils an qokar .45:2 gebunden. „Nochmals“ beschreibt nur die zweite gleiche Wortnennung, keinen gelesenen Wiederholungsmarker. Die Wörter und ihre Bindungsregel sind weiter freie Hypothesen, keine unabhängige Wärmeerkenntnis.

Der vollständige Quellwortlaut ist in ZL3b und IT2a gleich:

`yshey qokar olchedy qor oiin okeedy qokeed qokeey qokeey otey qoky dy`

Es werden weder die offenen Wörter vor den Wärmeverben noch `otey` zwischen ihnen weggelassen: [READING.md](READING.md) enthält alle sechs vollständigen Absatztranskriptionen mit beiden Ereignisfassungen und ihren Abzweigungen. Die flüssige Kurzfassung oben ist nur der bereits angesetzte Prädikatsablauf. Sie ist keine lückenlose Übersetzung dieser Zeile.

## Vollständiger Vergleich

Alle 135 W69-Ereignisse wurden an identischen Quellenpositionen innerhalb derselben Transkription zusammengeführt. Keine unsichere Zuordnung zwischen Transkriptionen wurde ergänzt.

| Kategorie | Lesepositionen | Bedeutung für den Entwurf |
|---|---:|---|
| identische Folge mit benanntem Patienten | 33 | unter NRC und AMV gleicher hypothetischer Bezug |
| identisch, aber Patient fehlt | 9 | gemeinsam unvollständig; kein tragender Ablauf |
| beide haben Prädikat, Folgen unterscheiden sich | 15 | beide Zweige sichtbar erhalten |
| nur NRC hat dort ein Prädikat | 11 | chey-Prüfungen entfallen unter AMV |
| nur AMV hat dort ein Prädikat | 10 | sheckhy-Aktionen fehlen als Aktionen unter NRC |
| gesamte Vereinigung | 78 | jede vorhandene Ereignisposition erfasst |

Gleichheit verlangt identische Glosse, Prädikatsart, Polarität und Materialnennung samt Materialglosse. Bloß zwei fehlende Patienten ergeben deshalb keine gemeinsame gebundene Folge. [COMPARISON.tsv](COMPARISON.tsv) enthält jede Position und jedes abweichende Feld. Die 33 Fälle sind keine 33 unabhängigen Beweise: Beide Modelle erben denselben Großteil des Glossars und dieselbe Rückbindung.

## Sämtliche zusammenhängenden Folgen mit demselben Material

Die feste Regel liefert fünf Folgen in den einzelnen Transkriptionen. Jede Abweichung, jeder fehlende Patient und jeder Wechsel der Materialnennung bricht die Folge ab; offene Nicht-Prädikatswörter bleiben im Quelltext sichtbar.

| Transkription und Stelle | Gemeinsamer hypothetischer Ablauf | Grenze |
|---|---|---|
| ZL f116r.34–35 | Dosis des Grundansatzes erwärmen, anhaltend erhitzen | IT hat anderes Material und anderen Belegort |
| IT f116r.34–35 | erwärmte Dosis P erwärmen, anhaltend erhitzen | keine identische Dosisbestimmung über die Transkriptionen hinweg |
| ZL f116r.41–42 | Zubereitung B einmischen, nehmen | IT hat unter AMV ein Verbot; kein transkriptionsübergreifender gemeinsamer Ablauf |
| ZL f75v.45 | erwärmten Anteil zweimal anhaltend erhitzen, mäßig erwärmen; fertig | offene Zwischenwörter, keine physikalische Prüfung |
| IT f75v.45 | dieselbe hypothetische Folge | zweite Transkription derselben Manuskriptstelle, keine unabhängige Bestätigung |

[CHAINS.json](CHAINS.json) nennt alle Ereignis- und Materialpositionen. Es gibt unter dieser Regel keine entsprechende Folge auf f80r. Die f75v-Folge ist somit die einzige der drei unterschiedlichen Stellen, bei der hier sowohl Wortlaut als auch der angesetzte Materialbezug in beiden Transkriptionen übereinstimmen. Das ist ein manuell direkt am vollständigen Wortlaut kontrollierter Vergleich, keine automatische allgemeine Zuordnung der Transkriptionen.

## Was daraus folgt

Der Gesamtentwurf kann f75v.45 als gemeinsamen **hypothetischen Prozessabschnitt** enthalten, während die übrigen Absätze ihre ausdrücklich unterschiedlichen Zweige behalten. W69s „Zubereitung B nicht vermischen“ bleibt genau so eine Abzweigung, kein gemeinsamer Satz. Es wird keine Gesamtfassung als Sieger ausgewählt.

Die physikalische Plausibilität des gemeinsamen Abschnitts ist offen: Anhaltendes Erhitzen gefolgt von mäßigem Erwärmen braucht unter einer zeitlichen Befehlslesung eine Erklärung. Ein Wechsel der Wärmezufuhr, ein anderer Gegenstand oder eine andere Textfunktion ist nicht gelesen und wird nicht ergänzt. Ebenso bedeutet dy≈fertig in diesem Entwurf nur eine angenommene Qualitätsaussage, kein unabhängig belegtes Prozessende. Unbekannte Wörter könnten weitere Handlungen, Bezüge oder Satzgrenzen enthalten und damit die gesetzte Folge verändern.

**Nächster inhaltlicher Anschluss:** die ganze f75v.45-Folge gegen die bereits untersuchten Wärme-/Prozessannahmen prüfen: Welche konkrete Funktion könnte die Folge qokeey qokeey … qoky dy innerhalb einer plausiblen Anweisung haben, ohne offene Wörter zu tilgen oder einen Zustandswechsel zu erfinden? Vor einer neuen Rechnung sind die primären Wärme- und Zustandsversuche auf genau diesen Fall zu prüfen. Eine weitere unveränderte Schnittmengenrechnung bringt keine Übersetzung.

## Daten und Nachvollziehbarkeit

DECISION.md wurde vor der Klassifikation geschrieben. `build.py` erzeugt Vergleich, ganze Absätze und alle Folgen; `validate.py` rekonstruiert den Vergleich separat aus sämtlichen W69-Ereignissen und prüft die maximalen Folgen. Keine neue Grammatik, kein Decoder, kein Zustandstest und keine unabhängige Bedeutungsprüfung. W69 und ältere Quellen bleiben unverändert. Alle Absätze bereits exponiert; keine neuen Bilder, Kontakte oder Reserven, f84/f84r bleiben geschlossen. Keine Signifikanz oder bestätigten Pflanzen-/Wortbedeutungen. Unabhängige Bestätigungskapazität null.

Registryprüfung PASS. Globale Prüfung meldet weiterhin sieben bekannte ungebundene GDT600-Dateien. Lokale Vergleichsprüfung siehe VALIDATION.json; keine semantische Validierung.
