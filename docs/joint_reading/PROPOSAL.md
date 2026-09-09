# Wortfamilien und Absatzkontext unter einem gemeinsamen Leseschlüssel

Umsetzung nach Nutzerauftrag: [GDT832](../../experiments/yolo/gdt832_joint_family_context_control/REPORT.md)
beginnt mit einem begrenzten unabhängigen Kontrollmodell. Der ursprüngliche
Vorschlag unten bleibt als Entwurf erhalten; Status und Ergebnisse stehen im
verlinkten Bericht. Die erste Umsetzung nutzt belegte Co-Lemma-Beziehungen,
noch keinen vollständigen historischen Paradigmengenerator.

5. September 2026. **PROPOSED_CONTROL_ONLY_UNEXECUTED**. Methodenvorschlag und
statische Quellenprüfung; kein neuer GDT, kein Fit, keine Lesung und keine
numerische Preregistrierung. Empfohlener nächster Methodenkandidat. Die frühere
[Parallelpassagensuche](../internal_parallel_passages/PROPOSAL.md) bleibt
ungetestet und wird durch diese Prioritätsänderung nicht widerlegt.

## Idee und erwarteter Nutzen

Eine vorgeschlagene Lesung soll gleichzeitig den vollständigen geschriebenen
Wortformen, ihren wiederkehrenden Formbeziehungen und dem fortlaufenden
Klartextzusammenhang genügen. Ein begrenztes gemeinsames Schreibmodell verbindet
beides. Änderungen an einer Zuordnung wirken dadurch auf sämtliche betroffenen
Wortfamilien und Textstellen. Ziel sind überprüfbare konkrete Lesungen mit einem
übertragbaren Schlüssel. Der Ansatz setzt keine intern doppelt überlieferte
Passage voraus; ob er bessere Erfolgsaussichten hat, ist noch unbekannt.

Als **zu prüfende Modellklasse** dürfen ausgeschriebene Teile, regelhafte
Abkürzungen und eine begrenzte Zahl gespeicherter Ganzformen zusammenwirken.
Das ist keine Feststellung über die tatsächliche Voynichschrift. Frühere
98-Einheiten-Zerlegungen, 34-Rollen-Zahlen und angenommene deutsche Wortwerte
werden nicht zu Beobachtungstatsachen erklärt. Eine konkrete, kapazitätsbegrenzte
Kodierungsklasse muss vor einer Durchführung erst festgelegt werden.

Die [bestätigte formale Struktur](../STRUCTURAL_KNOWLEDGE.md) bleibt erhalten.
Ähnliche Schriftformen werden jedoch nicht automatisch als Flexion derselben
Wurzel behandelt. Der Decoder müsste eine solche Analyse unter einem gemeinsamen
Schreibmodell begründen. Historische Wortfamilien wären externe Beschränkungen
ganzer Formensätze, einschließlich Stammwechseln und mehrdeutigen Formen;
ihre Paradigmenplätze dürfen nicht nachträglich passend umbenannt werden.
Ererbte Parsergrenzen und Wortarten sind keine unabhängige historische Wahrheit.

## Konkreter Anlass aus dem alten Code

Die Prüfung ist begrenzt auf die genannten Quellen. Die dortigen Ergebnisse
wurden nicht neu berechnet:

| Quelle | Nachprüfbare Eigenschaft | Grenze der Schlussfolgerung |
|---|---|---|
| [GDT610-Bericht](../../experiments/yolo/gdt610_consensus_carrier_control_audit/REPORT.md), [Decoder](../../experiments/yolo/gdt610_consensus_carrier_control_audit/src/consensus_carrier_decoder.py), `NgramModel.log_score_word`, `chunk_score` | Im bekannten Kontrollcode sind alle elf Ganzwortträger stabil falsch. Der lokale Score summiert kontextlos einzeln bewertete Wörter sowie Längen-/Anzahlterme. | Das beweist weder die Ursache des gesamten Kontrollfehlers noch einen Nutzen der vorgeschlagenen Reparatur. |
| [GDT612-Decoder](../../experiments/yolo/gdt612_historical_fst34_target_attack/src/full/decoder.cpp), `CharModel::score`, `score_chunk` | Zeichenkontext läuft innerhalb des übergebenen Wortvektors über Wortgrenzen, beginnt aber bei jedem getrennt bewerteten Chunk neu. | GDT612 ignoriert nicht jede Wortfolge. Der spätere Held-Evaluator ist nicht mit dem Trainingsziel gleichzusetzen. |
| [GDT612-Kontrollgenerator](../../experiments/yolo/gdt612_historical_fst34_target_attack/src/full/make_synthetic.py), Schleife über `words` und `Counter(encoded)` | Nicht kodierbare Wörter werden ausgelassen; Kontextbeispiele werden zusätzlich angehängt. Der Fitter erhält frequenzsortierte Chunktypen. | Dies ist kein unverändert verschlüsselter fortlaufender historischer Absatz. Der alte [Autopsiebericht](../../experiments/yolo/gdt612_historical_fst34_target_attack/REPORT.md) nennt weitere Fehler; Kontext allein behebt diese nicht. |
| [GDT001-Ganzwortmodell](../../run_gdt001_word_nomenclator.py), `split` | Es benutzt Wortbigrams, beendet einen Lauf jedoch bei einer Gruppe außerhalb des ausgewählten Ganzwortinventars; der Rest bleibt anonym. | Die Aussage „Wortkontext wurde noch nie benutzt“ wäre falsch. |
| [GDT001-Komponentenmodell](../../run_gdt001_nomenclator.py), `split` | Der alphabetische Sprachlauf endet beim opaken Ganzworteintrag. | Die beiden geprüften Teilmodelle identifizieren nicht gemeinsam einen durchgehenden gemischten Klartext. |
| [GDT001-Morphologiemodell](../../run_gdt001_morphology_grammar.py) | Häufige Präfixe/Suffixe und anonyme Kerne werden ausgewählt und modelliert. | Das ist noch kein Decoder mit historischen Lemma-/Paradigmenzuordnungen unter einem gemeinsamen Schreibschlüssel. |

Root hat diese Codepfade und die GDT610/GDT612-Berichte selbst gelesen;
Subagenten halfen bei unabhängiger Methoden- und Vorgängerprüfung. Die
Quellenprüfung erzeugt keine neue Manuskriptevidenz.

## Was sich gegenüber Vorläufern tatsächlich ändern müsste

[GDT603](../../experiments/yolo/gdt603_naibbe_end_to_end_control/REPORT.md)
benutzt bereits fortlaufenden alphabetischen Kontext und löst seinen
Naibbe-Kontrollfall. Der anschließende
[GDT604](../../experiments/yolo/gdt604_naibbe_frozen_target_attack/REPORT.md)
liefert keine Voynichlesung. Durchgehender Kontext allein wäre deshalb keine
neue Route. [GDT747](../../experiments/yolo/gdt747_supported_whole_passage_application/REPORT.md)
und [GDT748](../../experiments/yolo/gdt748_complete_whole_serial_paradigm_census/REPORT.md)
kombinieren bereits lokale Reihen und Ganzformähnlichkeit; ihre Arbeitsrollen
sind keine unabhängigen historischen Flexionsparadigmen oder Klartextanker.

Der hier vorgeschlagene Unterschied ist eine **gemeinsame Identifikation über
Ganzform-/Komponentenübergänge**, beschränkt durch historische ganze
Formfamilien. Derselbe ausgegebene Klartext muss denselben Sprachscore erhalten,
gleichgültig, an welchen Eingabegrenzen er zusammengesetzt wurde. Kosten für
Schlüssel, Segmentierung und Beobachtung bleiben davon getrennt. Ein kurzer,
für alle Vorkommen gültiger Regelsatz ersetzt keine nachträglich beliebig
änderbare Einzelstellenübersetzung.

Die geschlossene [GDT616-Konfiguration](../../experiments/yolo/gdt616_joint_child_feasible_binding/REPORT.md)
wird nicht repariert oder wiederholt. Ihr erzwungenes Einheiteninventar und
ihre synthetischen Kind-/Override-Bedingungen werden nicht übernommen.

## Erste Entscheidung durch einen unabhängigen Kontrollfall

Vor einem Manuskriptfit muss ein getrennt gebauter Generator unveränderte
historische Absätze unter einer vorab begrenzten Mischkodierung verschlüsseln.
Er darf Wörter nicht auslassen oder umsortieren, um eine erwünschte
Voynich-Chunkverteilung zu erzeugen. Schlüssel und Bestätigungstexte bleiben
dem Decoder verborgen; Referenztraining enthält diese Absätze und ihre
Dublettenkopien nicht.

Der neue Falsifikator ist die korrekte Wiedergewinnung des Klartexts auf ganzen
ausgeschlossenen Absätzen **und** von zuvor ausgeschlossenen Wortformen und
Lemmas unter demselben Schlüssel. Eine Kontrollanalyse muss die Identifizierbarkeit
des Schlüssels prüfen; bei äquivalenten Kodierungen zählt die offen ausgewiesene
Äquivalenzklasse, nicht ein künstlich unmöglicher exakter Parametervergleich.
Für die Prüfungen sind getrennte, ausreichend belegte Partitionen nötig.
Alle informationshaltigen Schlüsselregeln müssen im Discovery-Material
ausreichend vorkommen. Gehaltene neue Formen müssen aus bereits belegten Regeln
rekonstruierbar sein; ein erstmals auftauchender opaker Ganzwortträger erhält
keinen zuvor unbekannten Wortwert. Damit wird GDT612s fehlende Schlüsseldeckung
nicht als vermeintlich strenger Holdout wiederholt.

Verglichen werden das vollständige Modell und ansonsten identische Varianten,
die entweder den Kontext an Mischübergängen abschneiden oder die externen
Lemma-/Paradigmenbeziehungen zerstören. Zusätzlich braucht es Pseudotexte mit
vergleichbarer Häufigkeit, Wortform- und Familienstruktur. Sprachflüssigkeit,
hoher Referenzscore, Restart-Einigkeit und Rückkodierbarkeit allein bestehen
diese Prüfung nicht. Aufwand, Schwellen, Kodierungsklasse und Nullkonstruktionen
müssen vor Ergebnissen numerisch festgeschrieben werden. Diese Seite ersetzt
eine solche Preregistrierung nicht.
Der behauptete gemeinsame Informationsgewinn ist nur unterstützt, wenn die
exakte gehaltene Rekonstruktion beide vorab festgelegten Ablationen materiell
übertrifft. Gleich gute Wiedergewinnung durch alle Varianten zeigt nur die
allgemeine Lösbarkeit dieses Kontrollfalls; auch die Verbesserungsschwelle
gehört in die spätere Preregistrierung.

Historische Sprachkorpora sind im Projekt vorhanden. Eine geeignete geprüfte
historische Lemma-/Paradigmenressource ist für diesen Vorschlag **noch nicht
nachgewiesen**. Ihre Verfügbarkeit und der Informationsgewinn der gemeinsamen
Beschränkungen sind die ersten Machbarkeitsfragen, keine erledigten Arbeitspakete.

## Manuskript- und Evidenzgrenzen

Ein gelöster Kontrollfall prüft das Werkzeug und seine begrenzte Kodierungsklasse.
Er etabliert weder diese Klasse für Voynich noch eine Übersetzung. Der geschlossene
Eintrag `CACHED_DATA_TRANSLATION_SUCCESSOR` und sein
[CDA001-Bericht](../../experiments/semantic_assumptions/results/cda001_cached_data_route_exhaustion.json)
bleiben bestehen: Ein stärkerer Decoder ersetzt die fehlende unabhängige
Text-/Wertverbindung nicht. Ein späterer Zielversuch braucht eine eigene
begründete Evidenzroute und Preregistrierung; dieser Vorschlag öffnet ihn nicht.

Keine neuen Manuskriptbilder oder gemischten Transkriptionszeilen wurden für
diese Prüfung geöffnet. Rohgruppen, unsichere Abstände und alternative Lesungen
bleiben sichtbar; letztere sind keine unabhängigen Manuskripte. Keine neue
Seitenaufnahme; f84 und f84r bleiben versiegelt. Neue Relationsevidenz müsste
weiterhin sämtliche GDT388-Einlassprüfungen bestehen.

## Nutzerauftrag 9. September: Gesamtarchitektur 5 + 3

Aktiver Beginn 18:34:04 UTC; mindestens zehn Stunden angefordert, ohne inaktive
Lücken. Die bestehende Langlaufsteuerung meldet usageLimited; daraus entsteht
keine behauptete Arbeitszeit. Schwerpunkt: unbekannte Schriftbausteine, volle
Flexionsparadigmen und Satzbeziehungen unter einem globalen Leseschlüssel.
832–837 nutzten nur Co-Lemma-Mitgliedschaft, vorgegebene Atome/Grenzen und wenige
Suffixkarten; ihre Fehler und 616 bleiben bestehen. Neu verfügbar ist die
Primärressource LatInfLexi mit expliziten Paradigmenzellen und phonologischen
Formen; sie schließt mittelalterlichen Wortschatz ausdrücklich aus. Sie wird
nicht als belegte Voynichsprache behandelt.

Erster Entscheidungspunkt nach höchstens 30 Minuten einschließlich Quellenzugriff,
Architektur, unabhängiger Kritik und kompakter Veröffentlichung: Gibt es einen
endlichen globalen Schriftkanal, in dem diese zusätzlichen Beschränkungen die
Wort-/Merkmalszuordnungen tatsächlich identifizierbar machen können? Bei einem
konkreten tragfähigen Modell folgt eine gemeinsame Rekonstruktion vollständiger
Texte; ungelöste freie Bedeutungsumbenennung oder fehlende Kanaldefinition führen
zur Modellrevision auf Papier, nicht zu einem größeren LM-/Kontrolllauf. Der
Unterschied muss über den bekannten Co-Lemma-Bonus hinausgehen. Nr.48 bleibt
die unabhängige Quellenalternative. Keine neuen Voynichseiten oder versiegelten
Daten; Quellenregister und Sprachannahmen bleiben getrennt.

Checkpoint nach etwa30Minuten: GDT892 definiert einen endlichen gemeinsamen
orthographischen CV-Kanal ohne freie Wurzelcodes. Präfixfreiheit bei1/2-Zeichen-
Codes reduziert die latenten Zerlegungen auf globale Zeichenmasken; vollständige
Codebuchergänzbarkeit bleibt zusätzlich verpflichtend.425561 feste Quellformen
und eine Grammatik aus13586 projektiven Referenzbäumen liegen vor. Das genügt
für die begrenzte Implementierung/Identifikationsprüfung, nicht für eine
Manuskriptlesung. Nächstes Budget90Minuten ab19:04UTC einschließlich Ergebnis-
prüfung und Veröffentlichung; kein automatischer Reparaturlauf bei Scheitern.

GDT892 stopped before key/cipher generation: the unchanged source supplies12D+9H,
below the fixed12+12 requirement. No decoder fit or threshold/corpus repair.
The architecture remains untested; move to the independently prioritized source
montage model, conditional on complete source runs and an identifiable shared
writing map. No old control failure is reopened.
