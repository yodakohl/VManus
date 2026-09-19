# GDT982 — ganze Zeilenlesungen mit gemeinsam geprüften Operatoren

**Für f75v.39 stehen jetzt fünf vollständige, ausdrücklich erfundene
Arbeitslesungen. Die Kombination „nicht + wiederhole denselben Vorgang“ ist
unter der festgelegten Einzelportion-/Bereichsregel unmöglich. „Danach“ wird
dadurch nicht entziffert: „nicht + einmal“ bleibt möglich, und die Textsuche
findet kein zweites passendes Vergleichsmuster.**

Die [vollständigen Fassungen und der ganze Absatz](artifacts/READINGS.md),
[alle Wortannahmen](src/CANDIDATES.json),
[alle fünf Kandidatenentscheidungen](artifacts/CANDIDATE_TABLE.tsv) und
[alle591 chey-Kontexte](artifacts/ALL_CHEY.json) sind veröffentlicht.
Die [Registrierung](PREREGISTRATION.md) wurde vor dem neuen Census öffentlich
gepusht (`af933fac5`). Die Ausgangszeile und die Bildansicht waren schon bekannt;
die lokale Modellinkonsistenz war vor der Rechnung ausdrücklich erwartet.

## Eine ganze mögliche Lesung, nicht zwölf identifizierte Wörter

```text
qoqokeey olkain qol sheedy qokeor sheedy qokal or chey qokar ol aiin
```

THEN_REPEAT als flüssiger deutscher Entwurf:

> Bereite ein Gemisch: eine Portion Flüssigkeit. Gieße die Flüssigkeit
> von B nach A, danach von A nach B; wiederhole diesen Vorgang.

A/B sind zwei angenommene Orte, keine entzifferten Namen und keine unabhängig
zugeordneten Bildgefäße. Die Quellreihenfolge stellt das Ziel jeweils vor die
Herkunft; die deutsche Fassung ordnet diese beiden Angaben natürlich um.

| Ganze Form | Gemeinsame Prozessannahme | Grenze |
|---|---|---|
| qoqokeey | bereite | nur ein exaktes Vorkommen je Transkription; rein lokaler Ansatz |
| olkain | Gemisch | keine Stoffidentifikation |
| qol | Portion | keine Zahl, Einheit oder bestätigte Mengenfunktion |
| sheedy | Flüssigkeit | beide Nennungen in der Zeile behalten denselben Wert |
| qokeor | gieße | keine unabhängig beobachtete Handlung |
| qokal / qokar | nach A / nach B | nur diese ganzen Formen, keine allgemeine q-Regel |
| ol / or | von A / von B | keine bestätigten Ortspartikel |
| chey | danach **oder** nicht | vollständige Gegenlesungen, kein ausgewählter Wert |
| aiin | wiederholt **oder** einmal | gemeinsam mit chey zu prüfen, nicht vorab als Wiederholungswort gesetzt |

Die beschreibende fünfte Fassung macht aus qoqokeey „Zubereitung“, aus
qokeor „Flussrichtung“, aus chey „sowie“ und aus aiin „beide Richtungen“:

> Zubereitung: Gemisch, eine Portion Flüssigkeit. Flussrichtung der Flüssigkeit
> von B nach A sowie von A nach B; beide Richtungen.

Sie behauptet Verbindungen, keine zeitlich ausgeführten Bewegungen. Sie wird
nicht als erfolgreicher Prozess gezählt, weil sie dessen Anforderungen gar
nicht macht. Keine alten Wärme-, Wasser-, Gefäß- oder Negationsglossen werden
als Bestätigung übernommen. W57, W30/W31, GDT936/940/981 bleiben unverändert.

## Was die Rechnung unterscheidet

Annahmen: dieselbe Portion, zwei Orte, Ziel zuerst, eine gemeinsame gieße-
Anweisung mit zwei Richtungsgruppen, keine unsichtbare Rücksetzung. Der
Schlussoperator gilt für die ganze Fließanweisung, nicht für eine neue
Vorbereitung frischen Materials bei jeder Wiederholung. NOT verbietet die
rechte Richtung im selben Anweisungsvorgang; sie wird nicht ausgeführt.
Das ist ein neuer Kontrastvertrag, nicht W30s alte Vorwärtsnegationsregel.

| Kandidat | Ausgeführte Folge | Ergebnis unter diesen Annahmen |
|---|---|---|
| danach + wiederholt | B→A→B; B→A→B | im binären Zustandsmodell wiederholbar |
| danach + einmal | B→A→B | einmal ausführbar; endet in B |
| nicht + wiederholt | B→A; nochmals B→A verlangt | scheitert: Portion ist bereits in A |
| nicht + einmal | B→A; A→B verboten | einmal ausführbar; endet in A |
| Beschreibung | mögliche Richtungen B→A und A→B | keine Aussage über den aktuellen Aufenthaltsort |

[Alle Ausführungsschritte](artifacts/RESULT.json) erhalten auch den fehlerhaften
zweiten Schritt. Eine neue Portion, ein stiller Rücktransport, ein anderer
Wiederholungsbereich oder ein neues Wort für aiin wurde nicht nachgereicht.
Die Rechnung modelliert Ortszustand, nicht Strömungsmechanik, Mengenverluste
oder eine tatsächlich funktionierende Apparatur.

**Verworfen ist nur eine gemeinsame Belegung samt ihren Zusatzannahmen.**
Weder chey≈nicht noch aiin≈wiederholt wird einzeln widerlegt. Man könnte auch
die Portionenidentität oder die angesetzte Syntax bezweifeln; das wären andere,
noch nicht geprüfte Modelle. Der vorher festgelegte Test bleibt unverändert.

Eine globale Vertauschung A↔B ändert alle diese Entscheidungen nicht. Die zwei
THEN-Modelle liefern denselben Endort, unterscheiden sich aber in der Zahl der
Ausführungen. Ohne unabhängige Wiederholungsbeobachtung kann dieser Test die
beiden nicht auswählen. Die Beschreibung hat keinen bestimmten Endort und
wird nicht mit einer fehlgeschlagenen Endortvorhersage verwechselt.

## Tatsächliche Textübertragung: nur die bekannte Ausgangsstelle

Der feste Test verlangt zwei unmittelbare Wörter links und rechts von chey,
dieselbe alte GDT915-Paarfamilie auf beiden Seiten und eine nach den Quellflags vollständig
eindeutige Zeile. Alle22 Familien wurden berücksichtigt. Andere
chey-Konstruktionen sind dadurch weder übersetzt noch widerlegt.

| Vollständige Absätze | chey insgesamt | Zeile nicht zulässig | Kein beidseitiges Zweierfenster | Außerhalb der22 Familien | Passende Konstruktionen |
|---|---:|---:|---:|---:|---:|
| ZL3b:659 | 297 | 193 | 45 | 59 | 0 |
| IT2a:690 | 294 | 28 | 98 | 167 | 1 |
| RF1b:keine markierten vollständigen Absätze | 0 | 0 | 0 | 0 | 0 |

Die einzige passende Stelle ist **IT2a f75v.39**, also genau die bereits
verwendete Entwurfsstelle. Zusätzliche physische Vergleichsblätter: **null**.
ZL wird wegen des schon aus GDT981 bekannten unsicheren Abstandes zwischen
qol und sheedy in derselben Zeile nicht nachträglich zugelassen. Die lokale
Glossenanzeige und die strengere Konstruktionsprüfung bleiben getrennt.
[Alle Muster](artifacts/FRAMES.json), [jede Modellkonsequenz](artifacts/PREDICTIONS.json).

Die Häufigkeiten aus allen zugelassenen P-Zeilen sind ein anderer Nenner:
chey310/309/299, aiin422/389/436, qokeor18/19/17 und **qoqokeey1/1/1**
in ZL/IT/RF. [Alle elf Worthäufigkeiten](artifacts/WORD_COUNTS.tsv).
Häufige Wörter erhalten dadurch keinen Bedeutungstest. Drei Darstellungen
des einzigen qoqokeey sind eine Manuskriptstelle, keine drei Bestätigungen.
Der gesamte neue Vorbereitungssatz hängt damit auch an einer frei belegten
Einzelform; das wird nicht als gelungene Generalisierung dargestellt.

## Ganzer Kontext und native Bildkontrolle

Der vollständige Kontext f75v.38–42 bleibt in allen Lesungen erhalten:
ZL59/IT59/RF58 Rohgruppen. Das neue hypothetische Lexikon belegt davon nur
22/23/20 Gruppen. Die Ausgangszeile selbst ist in ZL/IT mit12/12 Gruppen
belegt; RF hat11/12, weil `{ch'}eedy` unbekannt bleibt. „Belegt“ bedeutet
mit einer geratenen Glosse versehen. Mehr als die Hälfte des Absatzes bleibt
ungelesen; es gibt keine vollständige Absatz- oder Gesamtlesung.
Alle880 Modell-/Gruppenzuordnungen stehen in [ALIGNMENT.tsv](artifacts/ALIGNMENT.tsv).

Die zuvor zugelassene Originalaufnahme zeigt verbundene beckenartige Bereiche
mit Figuren. Sie macht ein Flüssigkeits-/Verbindungsmodell vorstellbar, weist
aber keinem der Wörter einen Ort zu. Ein eindeutiger Richtungspfeil oder eine
unabhängig nachgewiesene Rückführung wurde in dieser Ansicht nicht erkannt.
Daraus wird weder Flussrichtung noch das Fehlen einer nicht abgebildeten Handlung
bewiesen. Die native Betrachtung war durch Text und Hypothesen vorbelastet.
[Beobachtung und genaue Bildidentität](src/NATIVE_OBSERVATION.md).

Die [ausgeführte GDT388-Prüfung](artifacts/EDGE_GATE.json) hält die einzige
textgewählte Relationskante für nicht score-ready: null geeignete Kanten,
fehlende Kapazität, Holdout- und mobile Null-Gates. Die Fehlermeldung zur
Exposition bedeutet nicht, dass Quellenblindheit, Richtung oder Portionen-
identität anderweitig erfüllt wären. Unabhängige Bedeutungsbestätigung: null.
Keine Signifikanz, keine Reserven oder Kontakte; f84/f84r bleiben geschlossen.

## Entscheidung und genauer Anschluss

Die fünf Fassungen sind nachvollziehbare Hypothesen. NOT_REPEAT scheitert
unter dem registrierten Vertrag. Die anderen Fassungen sind in diesem Sinn
möglich; der Census liefert **keine zusätzliche Stütze** für eine davon.
Keines der elf Wörter wird ins bestätigte oder bevorzugte Glossar übernommen.
Keine Erweiterung des chey-Fensters und kein Aufweichen der Zeilenregel.

Der nächste Auswahlgegenstand ist der bislang frei gefüllte Anfang:
qoqokeey auf .39 gegenüber dem bereits bekannten qokeey qokeey auf .45.
Ein Routencheck und die Primärberichte GDT751, GDT820, GDT822 sowie W70 wurden
als Nachprüfung gelesen. Sie behandeln q/Basis und Ganzwortwiederholungen,
liefern aber keinen hier festgelegten Nachweis, dass ein wiederholtes qo eine
wiederholte Handlung schreibt. Ein anschließender Versuch müsste genau diese
Schreibregel und einen unterscheidenden Gegenfall festlegen; bekannte Wärme-
oder Feuerwerte werden nicht übernommen. Das ist eine nächste Auswahlfrage,
keine festgestellte Wiederholungsbedeutung oder bereits freigegebene Reparatur.

## Prüfung und Reproduktion

591 chey-Positionen, der eine passende Rahmen und alle15 vollständigen
Kontextzeilen wurden in einer zweiten Implementierung rekonstruiert. Eine
separate algebraische Prüfung kontrolliert alle tatsächlichen Modellurteile;
die Artefakte werden bytegleich regeneriert. Derselbe Autor, keine fachkundige
Gegenlesung und keine semantische Validierung. [VALIDATION](artifacts/VALIDATION.json).
Ausführung: `src/run.py`, Prüfung: `src/validate.py`, Relationsprüfung:
`src/gate.py`, finale Quellenbindung: `src/finalize.py`, jeweils mit Python3.
Die Hashs der öffentlichen Registrierung bleiben unverändert.

Der globale Repository-Check behält die bekannten acht Altfehler von GDT600
und GDT953. Sie werden nicht durch die erfolgreiche lokale Quellen-/Codeprüfung
als erledigt ausgegeben; die exakte Veröffentlichungsmenge wird separat geprüft.

Zeitnachweis bis Abschlussprüfung: 21.81 Minuten seit dem Wiedereinstieg, einschließlich Vorläuferrecherche, nativer Bildansicht, Modellentwurf, öffentlicher Registrierung, Ausführung und Prüfung. Ergebnisveröffentlichung folgt unmittelbar. Die30-Minuten-Grenze ab Modellauswahl bleibt eingehalten; keine weitere Modellerweiterung in diesem Block.
