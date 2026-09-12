# P02 — derselbe Ansatz muss seinen Zustand behalten

Die feste Lesung erzeugt einen konkreten Unterschied: Auf f29v.4:9 kehrt in CARRY der zuvor gekühlte Ansatz A1 zurück. NEW führt dort A2 mit unbekanntem Zustand ein. Danach folgt im Arbeitsabsatz keine Zustandsangabe, die zwischen beiden entscheidet. Das ist eine neue bedingte Zustandsvorhersage, keine erkannte Bedeutung von okaiin oder otshy.

| Fassung | Gruppen | Hypothesen / offen | Aktionen | Zustandsprüfungen (Achsen) |
|---|---:|---|---|---|
| CARRY | 145 | 32 / 113 | {'BOUND_TARGET_MISSING_LIQUID': 1, 'BOUND': 4, 'MISSING_TARGET': 2} | {'CONSISTENT': 3, 'CONFLICT': 6, 'INITIAL_CONSTRAINT': 4, 'MISSING_TARGET': 1} |
| NEW | 145 | 32 / 113 | {'BOUND_TARGET_MISSING_LIQUID': 1, 'BOUND': 4, 'MISSING_TARGET': 2} | {'CONSISTENT': 3, 'CONFLICT': 6, 'INITIAL_CONSTRAINT': 4, 'MISSING_TARGET': 1} |

Die Zustandsprüfung arbeitet auf einzelnen Achsen; oltchy erzeugt zwei Prüfzeilen, keine zwei unabhängigen Wörter. Benetzen hat ein Ziel, aber keine gebundene Benetzungsflüssigkeit. Ein Konsistenztreffer bestätigt keine Wortbedeutung.

## Konkreter Verlauf auf f29v.4

1. otshy .4:2 wird probeweise als „kühle“ gelesen; die folgende Ansatznennung okaiin .4:3 bindet den Vollzug. A1 erhält COLD. Diese Aktionslesung ist ausdrücklich neu gegenüber der früheren Qualitätsglosse.
2. cthy .4:4 wechselt den aktiven Teilnehmer zu B1. Seine früheren Zustände bleiben erhalten; oltchy prüft Kälte und Trockenheit an B1.
3. shot .4:7 erwärmt B1. Es erwärmt unter der festen Referenzregel nicht A1.
4. okaiin .4:9 nimmt in CARRY A1 samt COLD wieder auf. NEW führt A2 ein und übernimmt COLD nicht. Das unbekannte sho dazwischen wurde nicht als Zustandstransport oder Neuheitsmarker gedeutet.

Die zweite Nennung ist in NEW der angenommene Einführungsträger; ein besonderer Neuheitsmarker und ein Beschaffungsprozess sind nicht gelesen. Weil kein späterer Zustand an A2/A1 geschrieben zugeordnet wird, sind beide Anfangsannahmen weiter möglich. A2 kann kalt sein, muss es aber nach diesem Modell nicht sein.

## Alle Konflikte und fehlenden Zustandsziele (CARRY; NEW identisch)

| Ort | Teilnehmer | Achse | fortgeführt / behauptet | Herkunft | Befund |
|---|---|---|---|---|---|
| f29v.2:3 | B1 | moisture | WET / DRY | f29v.1:6 | CONFLICT |
| f29v.2:4 | B1 | moisture | WET / DRY | f29v.1:6 | CONFLICT |
| f29v.3:1 | B1 | moisture | WET / DRY | f29v.1:6 | CONFLICT |
| f29v.3:2 | B1 | moisture | WET / DRY | f29v.1:6 | CONFLICT |
| f29v.4:5 | B1 | moisture | WET / DRY | f29v.1:6 | CONFLICT |
| f17r.4:2 | NA | moisture | UNKNOWN / WET | NA | MISSING_TARGET |
| f21r.11:2 | B1 | moisture | WET / DRY | f21r.11:1 | CONFLICT |

Die Trockenbehauptungen auf f29v hängen mehrfach an demselben zuvor benetzten B1. Ohne angenommenes Trocknungsereignis widersprechen sie diesem Konto. Wiederholte Konflikte werden einzeln erhalten, aber nicht als unabhängige Widerlegungen gezählt. Die Konfliktbehandlung überschreibt WET nicht stillschweigend mit DRY. Das ist ein Urteil über diese feste Verlaufshypothese, nicht über die Rezeptgattung.

Die Folge shol chol shol steht auf f21r.11. Der alte P02-Vorschlag nennt hier f32v irrtümlich; er bleibt bytegleich, die Korrektur steht in DECISION.md/SOURCE.json. Auf f21r setzt die erste Feuchtigkeitsangabe zunächst einen unbekannten Zustand; die anschließende Trockenangabe kollidiert damit. Das erneute WET ist mit dem unverändert geführten Konto vereinbar, belegt aber keine durchgeführte Rückbefeuchtung. Dieses schon aus P18 bekannte Zustandsproblem ist kein neuer Entzifferungsfund.

f32v ist als vorgesehener zweiter Absatz vollständig mitgelesen; dort gibt es kein okaiin und deshalb keine Übertragungskapazität für dessen Identitätsregel. Auch f17r besitzt keinen Ansatzbeleg, f21r nur einen. Die drei Teilnehmerkarten sind bewusst klein: andere offene Wörter könnten weitere Teilnehmer oder Vorgänge nennen; sie dürfen im aktuellen Konto nicht als kostenlose Reparatur eingesetzt werden.

## Entscheidung und Nachrechnung

CARRY liefert die konkrete Vorhersage „derselbe Ansatz bleibt kalt“, NEW lässt den späteren Ansatz offen. Keine der beiden Fassungen wird als richtige Identität ausgewählt. Beide behalten dieselben Zustandskonflikte und sind keine kohärente Gesamtübersetzung. Für eine weitere inhaltliche Lesung fehlt ein ausdrücklich zugeordneter späterer Zustand oder eine anders begründete durchgängige Ereignissprache. Keine Reserveseite wurde dafür geöffnet.

MENTIONS.tsv bewahrt Zustand und Ursprung jeder Achse an jeder Nennung; OPERATIONS.tsv beide Koordinaten präpositiver Ereignisse; STATE_CHECKS.tsv alle Aussagen; IDENTITY_CONSEQUENCES.tsv jede Modellabweichung. Beide READING-Dateien enthalten die vollständigen Absätze. SOURCE.json bindet die begrenzte Quelle und die vor Ausführung geschriebene Entscheidung.

`python3 research_registry/proposals/translation_programs_20260912/work/P02/build.py`; `python3 research_registry/proposals/translation_programs_20260912/work/P02/validate.py` aus dem Repository. GDT559/700/809 und P12/P06 bleiben unverändert. Keine Signifikanz, keine bestätigten Wörter, keine unabhängige Bestätigung; f84/f84r geschlossen.
