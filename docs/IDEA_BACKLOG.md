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

Status: `IN_PROGRESS` (root; ausschließlich visueller Vorcheck).
Ausgangspunkt laut root: korrektes f72r3-Panel Yale1006203 nativ betrachtet;
helle/gelbliche Zentren sichtbar, belastbare Binärklassifikation noch nicht festgestellt.
Unterscheidung: ganze Figur-Stern-Beschriftungskarte, kein unterstellter Sternname.
Vorgängeraudit laut root: GDT796 prüfte barrel/clothing/facing; STAR_ENTRY_MARKER_COLOR
betrifft Absatzsterne, ZST002 Schweife, DIRECT_STAR_LABEL_RAY_COUNT scheiterte an
singulärer Zuordnung. Das ist eine vom Koordinator übermittelte Arbeitsnotiz;
dieser Agent hat weder Bildbefund noch jene drei Primärberichte selbst geprüft.
[Vorcheck des root](visual_overview/STAR_FILL_PILOT.md): f72r3 und f70v wurden
nativ betrachtet; Pigmentvariation bleibt eine zunächst ungeprüfte Beobachtung,
kein labelspezifischer Test. Nächster Schritt: root entscheidet erst über zuverlässig
sichtbare Variation und Zuordnung, bevor eine Textkorrelation oder ein GDT startet.

## Priorisierte Warteschlange

### IP002 — Sichtbare Untereinträge hinter `ychor`

Priorität: 1. Status: `READY_FOR_REVIEW`.
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
Die Bild-Schnittmenge wurde hier noch nicht geprüft; keine Kapazität zugesichert.
Nächster Schritt: root prüft locus/Seitenzulassung und ob GDT756/757 bereits
native Einzugsurteile enthalten. Nicht nochmals Initialitätsraten zählen.
Duplikatsuche: `ychor indentation visual entry start Item continuation preceding line`;
Primärberichte GDT756/757 gelesen. Keine Behauptung einer vollständigen Negativsuche.

### IP003 — Gleicher Teilnehmer oder nur gleiches Wort in einer Kette?

Priorität: 2. Status: `READY_FOR_REVIEW`.
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
