# W14 — „die abgekühlte Zubereitung einweichen und erwärmen“

**Ein konkreter Grammatikzweig macht die bisher konflikthafte Stelle f102v2.35 als Arbeitsanweisung formulierbar, ohne einen zusätzlichen Kühlvorgang zu erfinden:** Die nachgestellte Angabe teody≈abgekühlt kann den Eingang cheo≈Zubereitung beschreiben. Dann lautet die bedingte Lesung: „Weiche die abgekühlte Zubereitung ein und erwärme sie mäßig.“ Der Ablauf ist kalt → kalt und benetzt → warm und benetzt. Keine Wortbedeutung wurde dafür geändert.

Das ist eine neue, ausdrücklich angenommene zeitliche Gliederung der vorhandenen Wörter. Sie bestätigt weder teody noch die Satzregel. Die feste Konstruktion hat im gesamten ausgewerteten Paket **nur diese eine passende Schriftstelle**, unter J und M; keine unabhängige zweite Stelle.

## Registrierung und vollständiger Konstruktionstest

[DECISION.md](DECISION.md) und [SPEC.json](SPEC.json) registrieren den Versuch vor seiner Ausführung, nach Kenntnis der exponierten Problemstelle. IDEA000212 ist eine neue Grammatik-/Zeithypothese; W05 hatte diesen Zeitbezug ausdrücklich offen gelassen. W10s Wortwerte, Effekte, ursprüngliche Konflikte und Dateien bleiben unverändert.

Eine Qualitätsstelle ist nur dann zugelassen, wenn sie:

1. eine vorhandene STANDALONE-Qualität mit fest gebundenem Material ist;
2. unmittelbar nach genau dieser Material-Rohgruppe in derselben Zeile steht;
3. mindestens eine davor geschriebene Handlung derselben Zeile besitzt, die bereits genau dieses nachgestellte Material als Patienten hat.

Keine offene Zwischenform darf übersprungen werden. Alle 30 primären Qualitätspositionen wurden unter B/J/M geprüft: **90 Censuszeilen, zwei passende Grammatikfälle an einem Ort**. [ELIGIBILITY.tsv](ELIGIBILITY.tsv) enthält auch jeden nicht passenden Fall mit Ausschlussgrund. Insbesondere wurde nicht jede störende Kälteangabe zeitlich vorgezogen.

| Fassung | Konkrete Vorhersage an cheo teody | Tatsächlich ausgeführter Verlauf | Entscheidung |
|---|---|---|---|
| O: bisherige Schrift-/Argumentzeit | teody behauptet kalt nach Einweichen und Erwärmen | cheo wird benetzt und warm; die folgende Kältebehauptung widerspricht warm | Ursprünglichen bedingten Konflikt unverändert erhalten |
| I: nachgestelltes Eingangsattribut | teody beschreibt cheo vor den davor geschriebenen, auf cheo gebundenen Handlungen | Anfangstemperatur bisher ungebunden → kalt als Eingangsbedingung; Einweichen setzt benetzt; Erwärmen setzt warm | Als konkreten Attributzweig behalten; keine bestätigte Syntax |
| B, beide Zeitfassungen | Einweichen/Erwärmen betreffen sheeor, nicht cheo | Die Eligibility-Bedingung fehlt; keine Zeitverschiebung und keine neue gemeinsame Arbeitsfolge | B bleibt unverändert |

Die zwei Fälle J/M sind dieselbe Schriftstelle unter zwei angenommenen Grammatiken. D/H betreffen die beiden alten chol-Werte; der hiesige Ablauf hängt an shekeey/qoky und ist in D/H gleich. Vier tabellarische Zielresultate sind deshalb **keine vier unabhängigen Beobachtungen**.

## Die vollständige Zielzeile und ihre Grenzen

Primäres ZL:

`ychor sheol por sheeor shekeey qoky cheo teody qokeol daiin`

Mit den bisherigen, unbestätigten Wortwerten:

> nimm · feuchtes Gemenge · Zubereitungsmenge · wässriger Auszug · weiche ein · erwärme mäßig · Zubereitung · abgekühlt · erhitzte Flüssigkeit · Dosis Q

Der ausgearbeitete I-Kern unter J/M lautet:

> **Weiche die abgekühlte Zubereitung ein und erwärme sie mäßig.**

Die übrigen genannten Stoffe und Mengen bleiben im vollständigen Text stehen. W08s nimm-Vertrag nimmt sheol≈feuchtes Gemenge, **nicht** automatisch die hier bearbeitete cheo-Zubereitung. por und sheeor erhalten keine neue Rolle als Menge beziehungsweise Ausgangsstoff von cheo. Ebenso wird qokeol am Ende nicht zu einem neu gelesenen Produktnamen dieser Handlung erklärt. Die Attributlesung löst diese anderen Verbindungen nicht.

I setzt kalt als geforderte Eingangsbedingung, weil dieser physische Zustand vor der Handlung noch nicht festgelegt war. Das ist keine gemessene Anfangstemperatur und kein erzählter Kühlvorgang. Ein widersprechender früherer Zustand hätte weiterhin einen Konflikt ergeben; er liegt in den hier festgelegten E-Welten für dieses cheo nicht vor.

Die Gruppe teody bleibt an ihrer geschriebenen Position. Nur ihre semantische Zeit wird geändert: als Eigenschaft des nachgestellten Objekts kann sie in einer Anweisung den Eingang beschreiben. Weder Glyphen noch Wortgrenzen noch Reihenfolge der Quellgruppen wurden verändert.

## Ganze Folgeverläufe tatsächlich nachgerechnet

Alle 13 vollständigen primären W02-Absätze wurden in den vorhandenen E-Welten unter B/J/M und beiden chol-Werten D/H ausgeführt: 78 Ausgangsverläufe, jeweils O/I. Die ursprünglichen 2352 W10-E-ZL-Ereignisse werden unter O vollständig reproduziert. Insgesamt liegen 4704 Ereigniszeilen vor, einschließlich aller unveränderten und unbequemen Fälle. Die W09-R-Ergebnisnamenwelten gehören ausdrücklich nicht zu diesem kleinsten Test; kein Befund über deren Verträglichkeit wird behauptet.

[DIFFERENCES.tsv](DIFFERENCES.tsv) enthält genau zwölf abhängige Änderungen: teody sowie die zwei zugehörigen Handlungen, jeweils J/M × D/H. Nur die Anfangszustände und die zeitliche Stelle der Kältebehauptung ändern sich. qoky beendet den Ausschnitt in beiden Modellen bei warm und benetzt.

**Alle nachfolgenden Ereignisse und sämtliche Objektzustände am Absatzende sind wieder gleich.** [FINAL_STATES.tsv](FINAL_STATES.tsv) hält jeden Endzustand fest, [EVENTS.tsv](EVENTS.tsv) jede spätere Handlung und Aussage. Es gibt keine zusätzliche gelesene Folgewirkung, die I gegenüber O unabhängig auswählt. O verwirft den widersprechenden Kältewert gemäß der alten Regel, statt ihn in den Zustand zu schreiben; deshalb kann trotz seines Konflikts derselbe Endzustand entstehen.

[WORLD_SUMMARY.tsv](WORLD_SUMMARY.tsv) zählt die Modellkonflikte, ist aber kein Genauigkeits- oder Bedeutungsmaß. I entfernt genau den hiesigen warm/kalt-Konflikt unter J/M; andere Fälle wie f9v in D, f19vs ungleiche warm/heiß-Angaben in H und die bereits bekannten HOT→WARM-Aktionszuweisungen werden nicht verändert. Keine neue Temperaturstufe, keine automatische Kühlung oder sonstige Reparaturregel.

## Alternative Transkriptionen und Abdeckung

[ALTERNATE_TARGET_LINES.tsv](ALTERNATE_TARGET_LINES.tsv) bewahrt die vollständigen Zielzeilen:

| Lesung | Entscheidender Rohbereich | Kapazitätsgrenze |
|---|---|---|
| ZL3b | cheo teody | Einzige hier mit vorhandener Qualitätskarte ausgeführte Attributstelle |
| IT2a | cheo keody | Andere Ganzform; teody-Bedeutung nicht übertragen |
| RF1b | che@221;teody | Abweichende Rohgruppe; keine nachträgliche Zerlegung in cheo + teody |

Die gleichen Manuskriptstellen sind keine unabhängigen Textzeugen. Es gibt hier keinen neuen vollständigen IT/RF-Qualitätstransfer und keinen positiven Dreileserbeleg für die Attributregel.

[READING.md](READING.md) enthält alle 13 vollständigen ZL-Absätze mit jedem ungelösten Wort und der einen ausdrücklich markierten I-Alternative. [ALIGNMENT.tsv](ALIGNMENT.tsv) bewahrt alle 900 Gruppen. Unverändert 530 mit Wortannahmen belegt, 370 ungelesen. Der ganze betroffene f102v2-Absatz bleibt mit seinen übrigen offenen Gruppen erhalten; die kohärente Teilanweisung ist keine fast vollständige Übersetzung.

## Entscheidung und nächste Grenze

**I als konkreten Grammatikzweig behalten: „die abgekühlte Zubereitung einweichen und erwärmen“.** O bleibt als andere Zeitlesung dokumentiert. Der Gewinn ist die ausgearbeitete Eingangs-/Handlungsfolge mit unveränderten Wörtern und Effekten. Der Wegfall eines selbst erzeugten Konflikts identifiziert weder eine Wortbedeutung noch eine historische Satzkonstruktion.

Die Konstruktion ist innerhalb des festen Pakets vollständig geprüft, aber nur einmal belegt. Sie darf nicht als allgemeine Regel aller nachgestellten Qualitätswörter ausgegeben werden. Kein automatisches Erweitern auf andere Nachbarschaften, kein zusätzlicher Kühlvorgang und kein neuer Resultatname zur Vergrößerung des Erfolgs. Eine neue Entscheidung würde einen anderen tatsächlich gebundenen syntaktischen oder inhaltlichen Anschluss benötigen.

Alles war exponiertes Entwicklungsmaterial; keine Reserveseite, kein neues Bild, keine Kontakte. f84/f84r bleiben geschlossen. Unabhängige Bestätigungskapazität 0, bestätigte Wort-/Pflanzennamen 0. Ohne Gegenkontrolle der gesamten Suche keine Signifikanzbehauptung.

## Reproduktion und Vorgänger

W04/W05/W09/W10 wurden auf die Bindungs-/Zeitannahmen geprüft; P16 behandelt andere bedingte Aussagen, GDT707 einen historischen Ergebnisrenderer. Keiner liefert einen unabhängigen Beleg der neuen Attributlesung. Der Parallelauftrag prüfte eine oar-Teilentnahmeidee, fand jedoch dieselbe ungeklärte Herkunftsbindung wie in W07 und legte keine weitere Karte an.

`python3 research_registry/proposals/translation_programs_20260912/work/W14/build.py`, danach `python3 research_registry/proposals/translation_programs_20260912/work/W14/validate.py`. Quelle und Vorregistrierung SHA256-gebunden; alte W02–W13-Dateien bleiben bytefest. Der separate Validator importiert den Builder nicht und prüft vollständige Eligibility, alle 4704 Ereignisse gegen die alte Spur und separat formulierte Änderung, die neue Reihenfolge, alle gleichen Endzustände und 900 Rohgruppen. [VALIDATION.json](VALIDATION.json): PASS für Ausführungstreue, keine Bedeutungsbestätigung.
