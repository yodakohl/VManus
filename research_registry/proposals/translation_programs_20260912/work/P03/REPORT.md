# P03 — Mittel, Empfänger und Wirkung gemeinsam binden

Die therapeutische Fassung bindet drei der vier angenommenen Verabreichungen an einen ausdrücklich angesetzten Empfänger. Keiner der drei angesetzten Endbefunde folgt einer solchen Anwendung. Die Herstellungsversion hat denselben Referenzgraphen; die Wortwerte bleiben unentschieden.

Dies ist ein tatsächlich ausgeführter erster Teilentwurf, keine vollständige Übersetzung. Alle 145 Gruppen in vier exponierten HERB4-Absätzen stehen in beiden Fassungen und allen drei Mengengegenlesungen.

| Fassung | Hypothesen / offen | Herstellung | Anwendung/Zugabe | Endbefunde |
|---|---|---|---|---|
| T | 89 / 56 | {'MISSING_MATERIAL': 1, 'BOUND': 4, 'BOUND_PRIMARY_MISSING_LIQUID': 1} | {'MISSING_RECIPIENT': 1, 'BOUND': 3} | {'REFERENCE_MISSING': 2, 'BEFORE_APPLICATION': 1} |
| M | 89 / 56 | {'MISSING_MATERIAL': 1, 'BOUND': 4, 'BOUND_PRIMARY_MISSING_LIQUID': 1} | {'MISSING_RECIPIENT': 1, 'BOUND': 3} | {'REFERENCE_MISSING': 2, 'BEFORE_APPLICATION': 1} |

T: she≈Patient, sho≈verabreiche, shey≈beruhigt, sy≈gebessert. M: she≈Grundansatz, sho≈füge hinzu, shey≈ruhend, sy≈abgesetzt. Das sind bewusst rivalisierende Hypothesen, keine übernommenen Bedeutungsbelege. sheey bleibt offen. Gemeinsame Materialkarten stammen aus P11; die feste Herstellungsregel und neue Wortwerte sind in DECISION.md/MODEL.json angegeben.

## Alle Anwendungsstellen (T; M hat dieselben Bindungen)

| Ort | Mittel / Quelle | Empfängerquelle | Dosis | Frühere Bearbeitung desselben Mittels | Befund |
|---|---|---|---|---|---|
| f21r.9:2 | tshaiin / f21r.9:3 | NA | NA | NA | MISSING_RECIPIENT |
| f32v.10:1 | keol / f32v.10:2 | f32v.7:3 | NA | NA | BOUND |
| f32v.11:2 | chy / f32v.11:3 | f32v.7:3 | NA | NA | BOUND |
| f29v.4:8 | okaiin / f29v.4:9 | f29v.3:9 | NA | NA | BOUND |

## Alle angesetzten Endbefunde

| Ort | Wort | Empfängerquelle | Vorherige Anwendung | Konsequenz |
|---|---|---|---|---|
| f21r.11:7 | shey | NA | NA | REFERENCE_MISSING |
| f29v.3:4 | shey | NA | NA | REFERENCE_MISSING |
| f29v.3:11 | sy | f29v.3:9 | NA | BEFORE_APPLICATION |

## Rezept- und Mengenkonsequenzen

f17r besitzt in diesem festen Wörterbuch keine Herstellungs-/Anwendungsoperation. f21r hat eine ausdrücklich angesetzte Flüssigauszug-Gabe, aber keinen zuvor geschriebenen she-Empfänger. f32v ergibt unter T Öl und danach Wasser für denselben Patienten; M liest Öl und danach Wasser als Zugaben zu demselben Grundansatz. f29v ergibt eine Ansatz-Gabe nach dem angenommenen Patienten, doch sy=gebessert steht schon davor. Vorherige Besserung ist keine logische Unmöglichkeit: Sie liefert hier keinen Nachweis einer Wirkung der späteren Gabe.

Elf der zwölf Größenstellen haben einen Materialbezug; dain auf f32v.7:7 hat keinen. BOUND_PRIMARY_MISSING_LIQUID bei shytchy bedeutet nur gebundenes Zielmaterial, keine vollständige Benetzungsoperation.

Alle zwölf Größenstellen mit fünf freien Symbolen stehen einzeln in QUANTITY_CONSEQUENCES.tsv. D (Anwendungsmenge), H (Herstellungsmenge) und G (Stärke) behalten dieselben Materialbindungen. Keine der vier Anwendungen hat unter der festen chronologischen Gleichwortregel eine zugehörige frühere Dosis. Unbenutzte D-Angaben sind nicht nachträglich auf andere Mittel übertragbar; sie bleiben als Anwendungsangaben unverbunden. H und G haben dieselben bloßen Materialzuordnungen und werden dadurch nicht unterschieden. Keine tatsächliche Zahl oder Maßeinheit wurde erkannt.

Die beiden daiin auf f32v.8 beziehen sich unter dieser Regel auf dasselbe otchol. Anders als P05 wird keine Verteilung auf zwei Materialien angenommen. Es sind zwei sichtbare Aussagen desselben freien Wertes, kein Beleg für Doppeldosis. qotaiin bleibt ein hypothetischer Portionsname und ist keine identifizierte Zahl.

Die sichtbare Erwärmung auf f29v.4:7 bindet cthy, die folgende Gabe okaiin. Die Lesung darf deshalb nicht stillschweigend behaupten, der verabreichte Ansatz sei gerade erwärmt worden. Kein Anwendungsstoff hat hier eine frühere zugeordnete Herstellung. Roh oder zuvor hergestellte Mittel wären möglich; eine ungeschriebene Vorgeschichte wird nicht als Textbefund eingetragen. Alle Restmengen bleiben unbestimmt. Benetzen auf f29v.1 hat zusätzlich keine gebundene Benetzungsflüssigkeit.

## Entscheidung

T als partielle therapeutische Hypothese weiter zulässig, aber nicht vor M ausgewählt. Die ausdrücklich geforderte Empfänger→Gabe→späterer Befund-Kette entsteht nicht. Drei vollständige Rollenbindungen sind modellinterne Konsequenzen, keine drei Übersetzungstreffer. Patient und Grundansatz lassen sich im ganzen Graphen vertauschen; dieser Test bindet den semantischen Unterschied Mensch/Material nicht. Auch eine hypothetische Endzustandsaussage würde allein noch keine Kausalität beweisen.

Es wurden sämtliche Gegenfälle und Lücken behalten. Fehlende Rollen, fehlende Ausführungsgrößen und fehlende Bedeutungsbindung sind getrennt; weder eine ungebundene Aussage noch eine zeitlich frühere Besserung wird pauschal zur widerlegten Rezeptgattung erklärt. Eine spätere Version braucht einen tatsächlich getragenen Unterschied zwischen Empfänger und Ansatz bzw. einen anschließenden Wirkungsbezug, keinen Namenstausch.

GDT809/769/904 sowie P05/P14 bleiben unverändert. Kein neuer Decoder, kein historischer Quellensatz eingepasst. Alle vier Absätze sind vorbelastetes Material; keine unabhängige Bestätigungskapazität, kein Signifikanzanspruch, kein bestätigter Pflanzenname. f84/f84r und weitere Reserven bleiben geschlossen.

## Nachrechnung

`python3 research_registry/proposals/translation_programs_20260912/work/P03/build.py` und `python3 research_registry/proposals/translation_programs_20260912/work/P03/validate.py` aus dem Repository. SOURCE.json bindet Quellen und vor Ausführung festgelegte Entscheidung. INPUT/ALIGNMENT bewahren jede Gruppe; OPERATIONS, INVENTORY, ENDPOINTS und QUANTITIES sämtliche Rollen. READING_T_D/H/G.md und READING_M_D/H/G.md enthalten alle vier Rezeptblätter mit offenem Anlass und Endbedingungen.
