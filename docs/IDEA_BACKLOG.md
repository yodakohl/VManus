# Ideenpipeline

Stand: 2026-09-06. Dies ist eine priorisierte Arbeitswarteschlange, kein Befundregister.
Der Ideenagent sammelt unabhängig; root prüft und übernimmt genau einen Kandidaten
als `IN_PROGRESS`. Getestete Kandidaten behalten Status und Ergebnislink; keine
Stilllöschung. `READY_FOR_REVIEW` bedeutet prüfbarer Vorschlag, nicht wissenschaftlich
freigegeben oder garantiert ausreichend Daten. Ungeprüfte Voraussetzungen stehen
im Eintrag. Der Agent läuft nur während zugewiesener aktiver Aufgaben, nicht dauerhaft
zwischen Nutzerturns. Root publiziert; Schreibzuständigkeit dieser ersten Fassung ist an root zurückgegeben. Bei einer
neuen Aufgabe erhält der Ideenagent wieder alleinige Zuständigkeit für diese Datei.

Alle folgenden Vorschläge betreffen vorhandene interne Quellen. Keine neue
Bild-/Rohdatenöffnung durch den Ideenagenten, keine Websuche, kein Experiment.
f84/f84r bleiben versiegelt; Transkriptionen sind keine unabhängigen Manuskripte.
Die Priorität bewertet den nächsten kleinen Informationsgewinn, nicht die Chance,
eine erwünschte Übersetzung zu erhalten. Zeitbudgets umfassen Prüfung und Publikation.

## In Arbeit

### IP001 — Füllung getragener Sterne innerhalb eines Ringes

Status: `PILOT_PASS` — root, GDT841 abgeschlossen.
[Ergebnis](../experiments/yolo/gdt841_star_centre_visual_reliability/REPORT.md):
4/5 getrennte native Urteile stimmen überein:3gefärbte Zentren,1Umrandung;
ein Fall bleibt Aunklar/Bgefärbt. Fünf Sterne im selben Ring derselben Aufnahme.
Keine Beschriftungsabfrage, semantische Verbindung oder historische Farbklasse
bewiesen. Nächster Schritt wäre ein breiterer vorab festgelegter visueller
Beobachtungssatz; ein Texttest ist noch nicht vorbereitet.

## Priorisierte Warteschlange

### IP002 — Sichtbare Untereinträge hinter `ychor`

Status: `NEEDS_DATA` — vorhandene 13 Zielseiten sind nicht visuell zugelassen.
Ausgangspunkt: [GDT756](../experiments/yolo/gdt756_ychor_line_frame_content_slots/REPORT.md)
findet 13/13 Vorkommen zeileninitial, 0/13 absatzinitial;
[GDT757](../experiments/yolo/gdt757_initial_formula_role_atlas/REPORT.md) bestätigt
den Positionskontrast. Das ist bekannt, keine neue Entzifferung.
Neue Vorhersage: Wenn ein sichtbarer Untereintrag markiert wird, sollte der
Zeilenanfang zusätzliche unabhängige Gliederung zeigen: Einzug oder vergrößerter
Abstand zur vorausgehenden Zeile, verglichen mit unmittelbaren Nachbarzeilen.
Kleinster Test: zunächst Schnittmenge der 13 veröffentlichten loci mit bereits
visuell zugelassenen Seiten prüfen; auf höchstens zwei passenden Originalbildern
root nativ betrachten, Zielwort beim geometrischen Urteil abdecken und alle
Nachbarzeilen mitbewerten. Kein OCR, keine neue Seite. Gesamtbudget 5 Minuten;
bei fehlendem zugelassenem locus binnen 60 Sekunden `NEEDS_DATA`.
Entscheidung: sichtbare unabhängige Untergliederung stärkt die strukturelle
Eintragsmarker-Hypothese; ihr Fehlen lässt die semantische Item-Lesung weiter offen
und beendet diesen visuellen Zusatztest. Keine Übersetzung aus Einzug ableiten.
Einwand: Text ist bereits bekannt; Maskierung macht den Betrachter nicht blind.
Metadaten-Nachprüfung (ohne Text-/Bildöffnung): Die 13 Überschriften im
[GDT756-Reader](../experiments/yolo/gdt756_ychor_line_frame_content_slots/artifacts/GDT756_YCHOR_FRAME_READER.md)
lauten f6v.8, f9v.11, f17v.15, f19v.9, f22v.7, f23r.5, f24r.8, f45v.9,
f86v5.20, f93r.28, f99r.52, f102v2.35, f106r.9. Keiner dieser Selektoren steht
in GDT791s `src/PAGE_SELECTOR_SPECS.tsv` oder GDT812s `src/PAGE_ADMISSIONS.tsv`.
Recto und verso wurden nicht gleichgesetzt. Damit ist der vorgeschlagene Test
mit vorhandener visueller Zulassung aktuell nicht ausführbar.
GDT756 METHOD und GDT757 METHOD beschreiben Textposition/Kartengeometrie,
keine native Einzugsmessung. Die Unterscheidung ist somit vorbereitet, die
Bildzulassung fehlt. Nächster Schritt nur bei bewusster neuer Seitenpriorisierung:
einen bisher ungesehenen Zielselektor vor Zugriff registrieren. Kein automatischer
Seitenverbrauch und keine erneute Initialitätszählung.
Duplikatsuche: `ychor indentation visual entry start Item continuation preceding line`;
Primärberichte GDT756/757 gelesen. Keine Behauptung einer vollständigen Negativsuche.

### IP003 — Gleicher Teilnehmer oder nur gleiches Wort in einer Kette?

Priorität: 1. Status: `READY_FOR_REVIEW`.
Ausgangspunkt: [GDT704](../experiments/yolo/gdt704_v77_repeated_written_material_continuation/REPORT.md)
führt f26r.2 #4/#5/#6/#8 als lokale Kette C011/C013/C015; drei andere exakte
Kopf-Wiederholungen (f80v.35 und zweimal f88r.19) gelten als Zutatenwechsel.
Neue Frage: Trägt eine ausschließlich geschriebene, nicht übersetzte
Referenzmarkierung den Unterschied zwischen fortgesetztem und neuem Teilnehmer?
Kleinster Test: vorhandene vier Gegenüberstellungskarten nebeneinander prüfen;
alle deutschen Material-/Operationswörter entfernen; exakte Quellgruppen,
explizite Wiederholung und dokumentierte deiktische Markierungen stehenlassen.
Prüfen, ob die behauptete Teilnehmerfortsetzung dann noch ein unterschiedliches
Quellsignal besitzt. Keine neue Referenzkante vergeben. Gesamtbudget 5 Minuten.
Entscheidung: ein unabhängiges geschriebenes Signal liefert einen konkreten
Kandidaten für einen späteren Transfer-Test; fehlt es, ist die Kette weiterhin
an die Arbeitsübersetzung gebunden und kein unabhängiger Bedeutungsanker.
Einwand: Die abstrakten Tags können selbst aus der alten Deutung stammen;
auch sie müssen auf die geschriebenen Gruppen zurückgeführt werden.
Nächster Schritt: die vier vorhandenen Karten lokalisieren, erst dann fragen,
ob eine neue Unterscheidung über GDT704s bereits bekannte lokale Rivalität hinausgeht.
Duplikatsuche: `C015 repeated material batch identity cooling drying f26r`;
GDT704 gelesen. Kein Wiederholen der bereits geprüften Kopf-Wiederholungsregel.

### IP004 — Wiederholtes Feldende oder konkreter Zahlenwert?

Status: `DUPLICATE` nach vertieftem Vorgängerabgleich; nicht übernehmen.
Ausgangspunkt: [GDT764](../experiments/yolo/gdt764_bounded_value_field_dispatch/REPORT.md)
belegt fünf vollständige H1-X-daiin-Tripel; drei Linien enthalten ein zweites
Y-daiin-Feld, z.B. `pchedal | qopchdy daiin | chedy daiin`.
Neue Vorhersage: Ein obligatorischer Feldabschluss muss an mehreren Feldenden
desselben Records gleich sein; ein konkreter Wert darf unabhängig variieren.
Kleinster Test: nur die drei bereits veröffentlichten Mehrfeld-Linien vollständig
rekonstruieren und die Feldabgrenzung ohne `daiin` bzw. numerische Arbeitswerte
begründen. Bereits vorhandene anders endende Schwesterfelder in denselben
Records würden die obligatorische Abschlusslesung direkt einschränken.
Gesamtbudget 5 Minuten; keine neue Ganzkorpus-Familiensuche.
Entscheidung: unabhängig abgegrenzte Felder mit variierendem Ende rechtfertigen
Parameter- statt Pflichttrenner-Modell; fehlen unabhängige Feldgrenzen, kann das
Parallelitätsargument den Wert III nicht unabhängig stützen. Keine Zahl gewonnen.
Einwand: Wenn nur daiin die Felder definiert, ist der Test zirkulär und stoppt
vor jeder Zählung; Gleichheit allein unterscheidet Wert und Abschluss nicht.
Nachprüfung: [GDT686](../experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/REPORT.md)
belegt bereits 27 identische Nachbarrahmen mit mehreren d-Formen und 49 Linien
mit mehreren Varianten. Die Lesart eines einzigen obligatorischen Literalabschlusses
ist damit kein sinnvoller neuer Hauptgegner; die genaue Zahlbedeutung bleibt dadurch
unbewiesen. [GDT765](../experiments/yolo/gdt765_ofchy_schor_content_field_discriminator/REPORT.md)
behandelt zusätzlich die beiden parallelen Felder auf f22r.4.
Nächster Schritt: kein Test; der Entwurf bleibt hier sichtbar, um erneute Einrichtung
zu vermeiden. Eine neue Zahlenhypothese braucht eine unabhängige Mengenrelation.
Duplikatsuche: `daiin field delimiter terminator numeric value repeated fields independent boundaries`;
GDT764, GDT686 und GDT765 gelesen. Status wurde vor Datentest korrigiert.

### IP005 — AQ/Kontakt auf zusätzlichen unabhängigen Bildarrays

Priorität: 3 ausschließlich für Metadatenprüfung. Status: `NEEDS_DATA`.
Ausgangspunkt: [GDT361](../experiments/yolo/gdt361_aq_contact_prospective/REPORT.md):
prospektiv 1/3 AQ bei CONTACT, 0/2 bei GAP; p=.60. Richtung positiv, äußerst schwach.
Vorhersage: der eingefrorene Kontaktkontrast wiederholt sich in einem vorab
vollständig ausgewählten Panel weiterer physischer Folios.
Kleinster nächster Schritt: höchstens 2 Minuten ausschließlich Metadaten prüfen,
ob zusätzliche zugelassene und noch nicht zielgelesene Arrays vorhanden sind.
Erst danach eigenes Beobachtungsbudget; derzeit kein ausführbarer 5-Minuten-Test.
Entscheidung: verfügbare unabhängige Arrays ermöglichen spätere Weiterprüfung;
ohne sie kein Nachklassifizieren alter Arrays und keine neuen Korrelationsläufe.
Einwand: AQ wurde aus 306 Masken gewählt; ein weiterer bequemer Einzelhit hilft wenig.
Nächster Schritt: Panel-Kapazität und bisherigen Expositionsstatus klären.
Duplikatsuche: `visual connector tube connected basin text order direction network`;
GDT361 einschließlich expliziter nächster Route gelesen. Dies ist eine bekannte
offene Datenanforderung, keine neue eigene AQ-Theorie.

### IP006 — Rohre als gerichtete Verbindung zwischen Beschriftungen

Status: `DUPLICATE` — nicht übernehmen.
Ausgangspunkt: [GDT389](../experiments/yolo/gdt389_connector_edge_census/REPORT.md)
behält 14 Seiten mit Rohr-/Bogen-/Pfadgeometrie, aber null zulässige gerichtete
Inschrift-zu-Inschrift-Kanten im vollständigen geprüften Rahmen.
Verworfene Vorhersage: ein Rohr identifiziert Quell-/Zielbeschriftung einer Textrelation.
Kleinster Test: bereits abgeschlossen; kein erneuter Bilderdurchgang, Budget 0.
Entscheidung: erst neue autorielle Endpunktdaten könnten diese Route ändern.
Einwand: benachbartes Wort ist keine singulär zugeordnete Inschrift am Rohrende.
Nächster Schritt: geschlossen lassen; IP001 behandelt andere beobachtbare Einheiten
und darf diesen Endpunktmangel nicht durch bloße Nähe umgehen.
Duplikatsuche: `visual connector tube connected basin text order direction network`;
Primärbericht GDT389 einschließlich Schließbedingung gelesen.

### IP007 — Gehört die linke f66r-Zeichenspalte zeilenweise zum Haupttext?

Status: `DUPLICATE` nach root-Prüfung; nicht übernehmen.
Korrektur: [NEXT_STEP](visual_overview/NEXT_STEP.md) hält den älteren
f66r_border_permitted_evidence_audit mit31/32räumlichzugeordneten inneren Zeichen
fest. Der Primärbericht fehlt; seine exakten Regeln bleiben unrekonstruiert.
Die bloße Ausrichtung ist trotzdem kein neuer Beobachtungsanker. Der unten
aufbewahrte Entwurf übersah diesen Vorgänger; nicht erneut ausführen.
Ausgangspunkt: [native Übersicht](visual_overview/README.md), Abschnitt
Textflächen/Schriftbild: f66r besitzt links neben dem großen Textblock eine
schmale Folge einzelner Zeichen und kurzer Einträge. f66r ist bereits visuell
zugelassen. Dies ist ein publizierter Beobachtungsanker, kein neuer Bildbefund.
Neue unterscheidende Vorhersage: Ein zeilenweises Verweissystem muss eine
geometrisch eindeutige, monotone Eins-zu-eins-Zuordnung zwischen beiden Spalten
zulassen; eine eigenständige Zeichenliste braucht diese Kopplung nicht.
Kleinster Test: root betrachtet genau das vorhandene f66r-Original nativ und
zeichnet für alle sichtbaren linken Einträge zugehörige Grundlinienintervalle
auf, ohne Zeichenwerte zu lesen. Verglichen werden gleich hohe Haupttextzeile,
nächsthöhere/nächsttiefere Zeile und kein singulärer Partner. Keine erzwungene
Zuordnung durch bloße Nähe. Gesamtbudget 5 Minuten; Sichtbarkeit zuerst.
Entscheidung: eindeutige wiederholte Zeilenbindung liefert einen konkreten
neuen internen Relationstyp zur späteren Quellenprüfung; fehlende Eindeutigkeit
beendet den Ansatz vor Textvergleichen. Eine feste Verbindung wäre weder
Alphabet noch Schlüssel noch Übersetzung und noch kein GDT388-fertiges Paket.
Wichtigster Einwand: gemeinsames Zeilenraster kann rein mechanisch sein;
auch eine perfekte Geometrie beweist keine semantische Abhängigkeit.
Vorgängeraudit: `f66r marginal column single character alignment adjacent text line vertical`;
der direkte [f66r-Primärbericht](../experiments/semantic_assumptions/results/f66r_plain_script_native_visual_relation_report.md)
wurde gelesen. Er verwirft die Äquivalenz zweier unterer Randinschriften auf
getrennten Grundlinien, nicht die linke Spalte am großen Textblock. Das öffnet
keine bilinguale Route erneut. Indexsuche allein belegt keine vollständige Neuheit.
Nächster Schritt: root prüft zuerst, ob die linke Spalte im vorhandenen Canvas
vollständig lesbar lokalisiert ist; keine erneute Prüfung der unteren Randglosse.

Runde 2: IP002-Datenprüfung abgeschlossen und Status vor Bildzugriff korrigiert;
ein neuer Vorschlag IP007 ergänzt. Schreibzuständigkeit an root zurückgegeben.
