# Ideenpipeline

Stand: 2026-09-06. Dies ist eine priorisierte Arbeitswarteschlange, kein Befundregister.
Der Ideenagent sammelt unabhängig; root prüft und übernimmt genau einen Kandidaten
als `IN_PROGRESS`. Getestete Kandidaten behalten Status und Ergebnislink; keine
Stilllöschung. `READY_FOR_REVIEW` bedeutet prüfbarer Vorschlag, nicht wissenschaftlich
freigegeben oder garantiert ausreichend Daten. Ungeprüfte Voraussetzungen stehen
im Eintrag. Der Agent läuft nur während zugewiesener aktiver Aufgaben, nicht dauerhaft
zwischen Nutzerturns. Root publiziert; Schreibzuständigkeit dieser ersten Fassung ist an root zurückgegeben. Bei einer
neuen Aufgabe erhält der Ideenagent wieder alleinige Zuständigkeit für diese Datei.

Die älteren Einträge IP001–IP007 behalten ihre differenzierten Prüfstatus.
Der neue Rohvorrat weiter unten verwendet zwei getrennte Reifestufen:
`RAW_UNSCREENED` = noch keine Neuheits-/Machbarkeitsprüfung; `REVIEWED` =
route-check plus direkte Primärquelle dokumentiert. `REVIEW_PRIORITY` ist nur
ein Auswahlhinweis innerhalb RAW, weder Freigabe noch behauptete Neuheit.
Root prüft zunächst die fünf Prioritäten, übernimmt höchstens einen Versuch und
lässt die übrigen Ideen liegen. Bekannte Schließbedingungen bleiben verbindlich;
ein Rohvorschlag darf sie nicht durch Umbenennung umgehen.

Alle folgenden Vorschläge betreffen vorhandene interne Quellen. Keine neue
Bild-/Rohdatenöffnung durch den Ideenagenten, keine Websuche, kein Experiment.
f84/f84r bleiben versiegelt; Transkriptionen sind keine unabhängigen Manuskripte.
Die Priorität bewertet den nächsten kleinen Informationsgewinn, nicht die Chance,
eine erwünschte Übersetzung zu erhalten. Zeitbudgets umfassen Prüfung und Publikation.

## In Arbeit

### IP001 — Füllung getragener Sterne innerhalb eines Ringes

Status: `CONTEXT_DECK_ONLY_NEEDS_INDEPENDENT_BINDING`.
[GDT843](../experiments/yolo/gdt843_star_caption_provenance_intake/REPORT.md)
verbindet9/10Sternpunkte eindeutig mit alten Figuren-Crops; O8/A14fehlt.
Sechs der sieben klaren Fälle haben damit einen Beschriftungs-Locus. Rohlesungen
bleiben vollständig: auch2/4Gruppen und Varianten. Keine autorielle Sternbindung,
GDT3880eligibleedges, keine Farb-/Wortkorrelation oder Bedeutungsbeförderung.
[GDT842](../experiments/yolo/gdt842_star_outer_ring_extension/REPORT.md)9/10
Urteilsübereinstimmung und [GDT841](../experiments/yolo/gdt841_star_centre_visual_reliability/REPORT.md)4/5bleiben lokale visuelle Positivbefunde.
Nächster Schritt braucht unabhängige autorielle Zuordnung oder eine neu begründete
Gesamt-Record-Relation; weitere Farbzählung oder nächste Beschriftung hilft nicht.

## Priorisierte Warteschlange

### IP002 — Sichtbare Untereinträge hinter `ychor`

Status: `TWO_PAGE_VISUAL_LEAD_STOPPED`.
[GDT844](../experiments/yolo/gdt844_ychor_visual_subentry/REPORT.md) hat f6v/f9v
bewusst neu zugelassen und nativ geprüft: keine auffällige Einrückung oder
vergrößerter Abstand oberhalb beider Ziele.33Haupttextzeilen dokumentiert.
Kein zusätzlicher grafischer Untereintragsbeleg; sprachliche Funktion offen.
Keine automatische dritte Seite. Die folgende ursprüngliche Datenlücke ist
für diese zwei Seiten durch die registrierte Zulassung überholt.
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

Status: `NEEDS_DISCRIMINATOR` nach direktem Vorgängeraudit; nicht ausführen.
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
Vorgängeraudit Runde 3: GDT704 METHOD trennt bereits exakte Kopf-Wiederholung,
deiktisches Ziel, verwandten/anderen Kopf und fehlenden Kopf. Seine C015-Auswahl
setzt die GDT700-C011-Teilnehmerfortsetzung voraus und unterscheidet die anderen
Wiederholungen über die Arbeitsbedeutung der jeweiligen Operation. Das Entfernen
der deutschen Wörter würde diese bekannte Abhängigkeit erneut vorführen;
ein neues unterscheidendes geschriebenes Signal wurde im Entwurf nicht benannt.
[GDT700 REPORT/METHOD](../experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/REPORT.md)
sagt ausdrücklich: #4 hat keinen separat geschriebenen Ergebnisnamen; die
Fortdauer als erhitzte Krautdroge ist die Hypothese selbst. Die Kombination
`ykecthey → chedy → ytedy` nominiert eine lokale Beziehung, verifiziert aber
keine Teilnehmeridentität. Der Gegenfall f77v.7 besitzt mit `rr` einen
konkurrierenden Arbeitsmaterialträger, dessen Auswahl bereits offen blieb.
[GDT703](../experiments/yolo/gdt703_v76_all_action_finished_result_census/REPORT.md)
registriert den bekannten Zustandszweig #4→#5, ohne daraus #5→#6 zu machen.
[GDT695](../experiments/yolo/gdt695_fixed_v67_clause_realization/REPORT.md)
legt zudem offen, dass Aktion/nominaler Block aus dem bestehenden Arbeitsinventar
kommen; #6 `ytedy` und #8 `checthedy` behalten schwesterabgeleitete Verben.
Ein lokaler unabhängiger Dispatch ist keine externe Bestätigung dieser Semantik.
Nächster Schritt: keiner mit den bisherigen vier Karten. Erst ein konkret
benanntes zusätzliches Quellsignal mit unterschiedlicher Vorhersage für gleiche
und neue Teilnehmer rechtfertigt erneute Prüfung. Keine erneute Maskierung,
kein Kontrolllauf und keine Herabstufung als angeblich neuer Manuskriptbefund.
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

Runde 3: IP003s direkte Vorgänger GDT704 METHOD/REPORT, GDT700 METHOD/REPORT,
GDT703 REPORT und GDT695 REPORT gelesen; die vorgeschlagene Abhängigkeitsprüfung
würde bekannte Grenzen wiederholen. IP003 ist `NEEDS_DISCRIMINATOR`.
Auch die kompakte NEXT_STEP-Vorarbeit wurde erneut berücksichtigt. Keine neue
Idee ohne konkreten neuen Discriminator eingetragen. Keine Roh-TSV, Bilder,
Programme oder Experimente geöffnet/ausgeführt. Schreibzuständigkeit an root frei.

## Produktionsspur: geprüfte Datenlücke statt neuer Test

Runde 4 prüfte die positive physische Schreibprozessbeobachtung
[RBR001](../experiments/semantic_assumptions/results/rbr001_f67r2_red_brown_result_report.md):
f67r2.3 und f67r2.10 zeigen abweichende braune Unterstriche unter roter Nachzeichnung.
Der anschließende [RBR002-Primärbericht](../experiments/semantic_assumptions/results/rbr002_complete_underlayer_capacity_result_report.md)
schließt aber den kompletten sichtbaren Ring bereits ab: nur die zwei bekannten
von zwölf Records, null von neun neuen, verfehlen sämtliche Kapazitätsgrenzen.
Die zuerst attraktiv wirkende Idee, die frühere Textfassung aus dem ganzen Ring
zu gewinnen, wird deshalb nicht als neue ID oder weiterer Bildtest angeboten.

Der konkret fehlende Input ist eine **neue physische/spektrale Aufnahme von f67r2**,
die Unterstriche an denselben vorab fixierten zwölf Records trennen kann; neue
Kontraste oder Zuschnitte derselben Aufnahme genügen nicht. f67r2 ist bereits
visuell zugelassen. Ein zulässiger nächster Beschaffungsschritt wäre ausschließlich
ein zweiminütiger lokaler Metadatenabgleich vorhandener Spektralquellen gegen die
RBR002-Aufnahme: anderer Aufnahmezustand, exakter Folio-/Panelbezug, Wellenband und
Registrierung müssen nachweisbar sein, bevor Bilder geöffnet werden. Fehlt ein
solcher bereits verfügbarer Datensatz, stoppt die lokale Beschaffung; es wird
keine externe Aufnahmeverfügbarkeit unterstellt oder Kontaktaufnahme gestartet.
Dieser Metadatenabgleich wurde in Runde 4 noch nicht ausgeführt.

Duplikatprüfung: `writing process line space compression hyphenation ink retracing
stroke omission`, danach `f67r2 twelve sector underlayer recovery census red brown
retracing`; RBR001/RBR002-Primärberichte und gezielte aktive Registerhinweise gelesen.
Kein neuer Manuskriptbefund, keine neue Entzifferungsidee als bereit ausgegeben.
Schreibzuständigkeit an root zurückgegeben.

### Ausgeführter lokaler Spektral-Metadatencheck für f67r2

Status: `NO_AVAILABLE_CAPTURE_IN_CHECKED_METADATA` — lokale Quellenlücke,
keine Behauptung über das gesamte Dateisystem oder den aktuellen Webbestand.
Geprüft wurden die durch route-check/Repository-Dateinamen gefundenen RBR002-
Auswahlmetadaten, die beiden gespeicherten MSI-Screen-Inventare, EBA001s
Rohaufnahme-Inventar und insbesondere die gespeicherten NVA002-Ordnerlisten.
Keine Aufnahme, Rohtextzeile, Bildvorschau oder Webadresse wurde geöffnet.

- RBR002 bindet das gewöhnliche Yale-Canvas **1006194**, 4972×3738 Pixel,
  SHA-256 `0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c`.
- Die lokale [NVA002-Inventur](../experiments/semantic_assumptions/results/nva002_public_physical_layer_update_prescreen.json)
  enthält für `Processed_Images` und `Raw TIFFs` dieselben zehn Folios:
  f1r, f8r, f17r, f26r, f47r, f70v1, f71r, f93r, f102v1, f116v.
  **f67r2 ist in keiner der beiden gespeicherten Ordnerlisten vertreten.**
- Das lokale [EBA001-Inventar](../experiments/semantic_assumptions/results/eba001_raw_directional_msi_inventory.json)
  beschreibt sechs einzelne `MB365UV`-Aufnahmen, ausschließlich f17r/f116v.
  Das ist eine vorhandene Bandbezeichnung, aber kein f67r2-Datensatz.
- Die zwei MSI-Screen-Metadaten decken sieben beziehungsweise zwei Folios
  dieser Liste ab; auch dort kein f67r2. Die gespeicherten separaten
  True-Color-Ordnernamen begründen weder ein neues Spektralband noch eine
  zusätzliche physische Schicht.

Entscheidung: Im geprüften Quellenbereich existiert kein belegter f67r2-Kandidat,
der gleichzeitig abweichenden Aufnahmezustand und Spektralband dokumentiert.
Den sichtbaren RBR002-Ring daher nicht neu bearbeiten. Nächster sinnvoller Input
wäre ein konkret nachgewiesener neuer f67r2-Spektraldatensatz; ein solcher wird
hier weder bestellt noch als verfügbar ausgegeben. Die NVA002-Metadaten sind
historisch gespeichert und wurden jetzt nicht online aktualisiert.
Schreibzuständigkeit nach diesem begrenzten Check an root zurückgegeben.


## Breiter Rohvorrat — 28 Hypothesen in sieben Mechanismusfamilien

Nutzerkorrektur: mehr Ideen erzeugen, als unmittelbar bearbeitet werden können;
erst die besten prüfen. **Alle IP008–IP035 sind `RAW_UNSCREENED`.** Keine dieser
Ideen wurde vom Produzenten mit route-check geprüft, an Daten getestet oder als
weltweit/projektintern neu erwiesen. Die Quellen sind Ausgangspunkte für die
spätere Prüfung, nicht bereits vorhandene Belege für die jeweilige Vorhersage.
Einige Ideen können nach Prüfung Duplikate sein oder neue Daten brauchen.

**Top 5 zur Prüfung (`REVIEW_PRIORITY`): IP014, IP009, IP018, IP022, IP033.**
Reihenfolge: konkrete mechanistische Unterscheidung, möglichst vorhandene Quellen,
Begrenzbarkeit des ersten Tests. Keine Erfolgswahrscheinlichkeit geschätzt.
Für die Übernahme sind Quelle, Admission, Vorgänger, kleinster informativer Test
und Gesamtbudget zu klären; die untenstehenden Minuten sind grobe Gesamtziele,
keine Zusage ausreichender Daten oder abgeschlossener Bestätigung.

### A — Physische Herstellung der Schrift

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP008 | Wenn hohe Zeichen Platzkonventionen ausdrücken, weicht ihre obere Form bei geringer **vorher vorhandener** freier Höhe systematisch aus; ein rein positionsgebundenes Zeichen verlangt diese örtliche Anpassung nicht. | Native Orientierung in `visual_overview/README.md` als Startpunkt; konkrete hohe Zeichen neben gezeichneten Hindernissen müssen erst lokalisiert werden. Zwei eindeutig begrenzte Situationen auf zugelassenen Seiten nativ gegenüberstellen, 5 Minuten. | Gezeichnetes Hindernis kann später entstanden sein; ohne unabhängige Herstellungsfolge keine kausale Platzbehauptung. Nicht l/m-Breite nochmals messen. |
| IP009 **REVIEW_PRIORITY** | Wenn Teile zweier geschriebener Gruppen gemeinsam ausgeführt wurden, können **durchgehende, beiden zugehörige Striche** die sichtbare Gruppengrenze kreuzen; separat geschriebene Einheiten können nur überlappen. | Ganze hochaufgelöste Gruppen auf zugelassenen Seiten, Ausgangspunkt sichtbare Haken-/Bogenformen im nativen Dossier; konkrete Fundstelle noch unbestimmt. Maximal eine vorab begrenzte Textregion auf eindeutige gemeinsame Strichführung prüfen, 5 Minuten, unauflösbare Überlagerungen ausschließen. | Aus einem statischen Bild lässt sich eine Federbewegung oft nicht nachweisen; eine Ligatur beweist weder gemeinsame Bedeutung noch Lautwert. |
| IP010 | Eine vorgeplante Zeilenfüllung verändert bereits die **frühen** Gruppenbreiten in Abhängigkeit von der später benötigten Gesamtbreite; bloße Reaktion am rechten Rand setzt erst spät ein. | Bereits zugelassene Textblöcke und verlustlose Gruppen, bekannte variierende Schriftflächen aus `visual_writing_order/PROPOSAL.md`. Zuerst wenige Linien mit wiederholten Anfangsformen auf geometrische Vergleichbarkeit prüfen, 5 Minuten; erst danach unabhängige Breitenregel einfrieren. | Textlänge und Breite sind gemeinsam erzeugt; ohne unabhängige Sollbreite kann der Vergleich zirkulär sein. GDT829s fehlende Langparallelstellen nicht durch gelockerte Flanken ersetzen. |
| IP011 | Wenn ein Schreiber eine zeichnerische Vorlage nachzieht, bleibt bei einer Abweichung die **Reihenfolge mehrerer markanter Kurven entlang des ganzen Wortes** eher erhalten als ihr Abstand; eine inhaltliche Neufassung braucht dies nicht. | Positive physische Zustände RBR001, vollständige Grenze RBR002. Benötigt tatsächlich neue spektrale Daten; an einem vollständig recoverierbaren Wort beide Strichpfade ohne Zeichenbenennung vergleichen, 10 Minuten nach Aufnahmeverfügbarkeit. | Aktuell fehlt der benötigte neue Datensatz; zwei alte Teilformen erlauben keine Wiederöffnung der geschlossenen korrigierten-Ring-Route. |

### B — Graphem- und Codierungseinheiten

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP012 | Wenn komplexe Zeichen räumlich montierte Einheiten sind, bewahren wiederkehrende Komponenten ihre **Anschlussstellen** auch dort, wo ihre lineare EVA-Reihenfolge schwer darstellbar ist. | GDT605s rein transkriptionsbasierte Einheiten als Vorgänger, Originalbilder für einen vorher ausgewählten komplexen Zeichentyp. Zunächst zwei vollständige Bildvorkommen topologisch beschreiben, 5 Minuten; keine neue EVA-Lesung erzwingen. | Ein wiederkehrender Schreibstil kann dieselbe Geometrie erzeugen; die bekannte IGR002-Grenze gegen weitere grobe Zeichenklassifikation muss vorab geprüft werden. |
| IP013 | Bei einem graphischen Positionscode bleibt die Orientierung einer Teilform relativ zur **Wortgrundlinie** fest; bei seitenfestem Zusatzcode bleibt sie relativ zur Seite fest, auch in gedrehter Kreisschrift. | Native Kreisschriftbeobachtung in `visual_overview/README.md`, vollständig lokalisierte wiederholte Ganzformen. Nur zwei deutlich verschieden orientierte Stellen desselben Typs prüfen, 5 Minuten. | Schreibergonomie erklärt ebenfalls Unterschiede; kein Stern-/Kalenderwert folgt. Wiederholungs- und Zuordnungskapazität ist unbekannt. |
| IP014 **REVIEW_PRIORITY** | Falls eine Gruppenkomponente ein Kontrollzeichen ist, bestimmt eine **feste, reihenfolgeunempfindliche Prüffunktion** des restlichen Inhalts sie auch bei neuen Inhaltskombinationen; reine Anschlussgrammatik benötigt diese Invarianz nicht. | Bekannte Binnenstruktur aus `STRUCTURAL_KNOWLEDGE.md`, zugelassene rohe Gruppen erst nach Freeze. Eine kleine vorab bestimmte Familie von Paritäts-/Restklassenregeln an einem festen Entwicklungsanteil prüfen und gesamte Auswahlkosten offenhalten; 10 Minuten für eine Kapazitätsentscheidung. | Nahezu jede kleine Zeichenmenge lässt nachträgliche Scheinkorrelationen zu. Ohne explizit begrenzte Regelklasse und spätere zurückgehaltene Kombinationen kein positiver Codierungsbefund. |
| IP015 | Ein Code aus variabel langen Einheiten kann trotz fehlender Trennzeichen **eindeutig zerlegbar** sein; konkurrierende Grenzen müssen dann durch denselben festen Einheitenvorrat ausgeschlossen werden. | GDT605s veröffentlichter Einheitenvorrat und Rohdarstellung; vorab prüfen, welche Grenzen der Lerner schon geliefert bekam. Kleinster Test ist eine exakte Mehrdeutigkeitsanalyse des eingefrorenen Vorrats, 5 Minuten. | Zeigt möglicherweise nur eine vom Algorithmus erzeugte Eigenschaft. Der gescheiterte Ein-Buchstaben-Code wird dadurch nicht wiederbelebt, kein neuer Decoderlauf. |

### C — Kopieren, Gedächtnis und lokale Erzeugung

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP016 | Bei Kopieren aus dem **sichtbaren schon geschriebenen** Text sollten seltene Kombinationen eher rückwärts erreichbare Vorlagen besitzen; ein zeitlich symmetrischer thematischer Zusammenhang muss diese Richtung nicht zeigen. | Vorhandene rohe Textquellen plus dokumentierte räumliche Ordnung; GDT001s Copy/Modify-Kontrollen als Vorgänger. Zuerst an einem fest begrenzten Block die definierten rückwärts/vorwärts erreichbaren Vorlagen darstellen, 5 Minuten, keine Sprachbewertung. | Abfolge ist oft nicht sicher und Neuheit nimmt auch in echter Sprache gerichtet ab. Alte lokale Ähnlichkeits-/Kopierrouten könnten dies bereits abdecken. |
| IP017 | Eine mitkopierte lokale Abweichung bildet eine **verzweigte Vererbung**: spätere vollständige Passagen teilen mehrere gekoppelte Besonderheiten, nicht bloß häufige Einzelgruppen. | Bereits dokumentierte Wiederholungen; GDT838/829 als harte Kapazitätsvorgänger. Zuerst nur publizierte Wiederholungsbeispiele auf mindestens zwei gekoppelte unterscheidbare Merkmale prüfen, 5 Minuten. | Ausreichende Passagen könnten fehlen; keine Wiederholung der erfolglosen Suche mit kürzeren Flanken oder kleinerem Fenster. Ohne neuen Anker stoppt die Idee. |
| IP018 **REVIEW_PRIORITY** | Wenn mehrere benachbarte Varianten in einem gemeinsamen Herstellungsschritt erzeugt wurden, wechseln **zwei voneinander getrennte Formmerkmale synchron**; unabhängige Einzelersetzungen sagen solche gebundenen Wechsel nicht voraus. | Quelle: etablierte komplette lokale Paradigmen, zunächst GDT747/GDT748-Berichte. An genau einem schon publizierten mehrteiligen Paradigma prüfen, ob die Kopplung gegenüber unabhängigen Austauschmöglichkeiten überhaupt beobachtbar ist, 5 Minuten. | Die Merkmale können bereits dieselbe formale Klasse codieren oder durch Auswahl gekoppelt sein. Keine alte Rollenmaskierung, keine neue Bedeutungszuweisung aus Ähnlichkeit. |
| IP019 | Ein begrenzter Zwischenpuffer erzeugt einen **Abstandseffekt nach geschriebenen Einheiten**, auch wenn physische Zeilen unterschiedlich lang sind; eine Blicksprungquelle folgt eher der räumlichen Distanz. | GDT001-Kontextmodelle, dokumentierte ungleich breite Layouts, genaue Gruppenkoordinaten noch erforderlich. Zunächst nach einem vorhandenen Block suchen, in dem Einheitendistanz und Bilddistanz auseinanderfallen, 5 Minuten Metadaten-/Kapazitätsprüfung. | Ein hinreichender Koordinatensatz könnte fehlen; Federzustandsroute830/831 nicht reparieren. Gedächtnis und Sprache können dieselbe Distanzstruktur tragen. |

### D — Grammatische Abhängigkeiten ohne Wortübersetzung

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP020 | Ein lokaler Einbettungsmechanismus erlaubt **Klammerung**: dieselbe äußere Konstruktion umschließt unterschiedlich lange vollständige innere Folgen, deren Randverträglichkeit erhalten bleibt. | GDT581s strukturierte Edition als Hypothesengeber, Rohgruppen zur späteren Kontrolle. Ein publiziertes Paar mit verschieden langer Mitte suchen und die behaupteten Grenzen ohne semantische Tags begründen, 5 Minuten. | Parserklammern können genau die gesuchte Struktur hineingetragen haben. IL026s geschlossene höhere-Ordnung-Route vor jedem Test prüfen. |
| IP021 | Bei positionsübergreifender Kongruenz koppeln Merkmale zweier wiederkehrender Ganzformen auch dann, wenn **unterschiedliche Zwischenfolgen** auftreten; eine feste lokale Formel verlangt die Zwischenvariation nicht. | Vorhandene komplette Kontextkarten, GDT803/804 als Vorgänger. Nur publizierte Beispiele auf einen konstanten Zweierbezug bei mindestens zwei verschiedenen Mittelfolgen prüfen, 5 Minuten. | Kann lediglich Topic-/Schreiberkonfundierung sein; keine Buchstabensuffixe als Grammatikwerte voraussetzen und keine fehlende Kapazität durch größere Radien retten. |
| IP022 **REVIEW_PRIORITY** | Wenn eine Konstruktion wirklich einen Geltungsbereich eröffnet, verändert ihre Wiederholung **nicht bloß die Häufigkeit**, sondern welcher der folgenden gleichartigen Einträge zu welchem früheren Eintrag gehört; ein einfacher Reihenmarker sagt diese verschachtelte Konkurrenz nicht voraus. | Vorhandene vollständig erhaltene Mehrfeld-Records, zunächst GDT763/764/769 als Primärvorgänger. Eine konkrete geschriebene Folge mit zwei konkurrierenden offenen Feldern nominieren und prüfen, ob beide Modelle verschiedene nächste zulässige Formen vorhersagen, 5 Minuten. | Ohne unabhängige Randmarkierung bleibt die Zuordnung unentscheidbar; keine neuen Teilnehmer über alte Arbeitsübersetzungen erfinden. |
| IP023 | Ein textlicher Wiederaufnahmemarker erhält eine **selektive Vorgeschichte**: nach zwei unterschiedlichen eingeführten Ganzformen sollte seine Umgebung eine von ihnen, nicht beliebig beide, wieder aktivieren. | Vorhandene Referenzkarten GDT696/700 und qokaldy-Audit798. Ein bereits publiziertes echtes Zwei-Kandidaten-Beispiel auf ein noch ungenutztes geschriebenes Unterscheidungssignal prüfen, 5 Minuten. | IP003 und GDT798 zeigen gerade die bekannte Unterbestimmtheit; ohne zusätzliches unabhängiges Signal ist dieser Rohentwurf ein Duplikat und wird verworfen. |

### E — Beziehungen zwischen Bild und Text

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP024 | Bei kompositionalen Bildbeschriftungen übernimmt ein **zeichnerisch ausgetauschtes Teilobjekt** nur einen Textteil, während unveränderte Teile ihre Textbeiträge bewahren. | Native Pharma-Übersicht, vorhandene vollständige Objektkarten; erst ein unabhängig begründetes Bildpaar nominieren. Zwei gesamte Zeichnungen samt eindeutig zugeordneten vollständigen Beschriftungen vergleichen, 5 Minuten Kapazitätsprüfung. | Visuelle Teilähnlichkeit ist keine gesicherte Objektidentität; Pflanzenfragment-/Owner-Routen sind bereits stark vorgeprüft. Keine Teilwortähnlichkeit zur Auswahl verwenden. |
| IP025 | Ein gleicher Beschriftungstext kann einen **Recordtyp statt ein Objekt** benennen: dann bleibt er bei unterschiedlichen Objekten, aber gleicher unabhängig sichtbarer Recordfunktion bestehen. | GDT792/811-positive Ganzformwiederverwendung und native vollständige Seiten. Eine veröffentlichte Wiederholung auf einen sichtbaren Funktionskontrast prüfen, der bisher nicht nur durch Lage definiert wurde, 5 Minuten. | Die aktuelle Bilddokumentation kann solche Funktionen nicht unabhängig bestimmen; dann bloß bekanntes Name/Klasse-Unentschieden. |
| IP026 | Ein graphischer Einschluss grenzt den Text semantisch nur dann mit ab, wenn **Textfelder bei verschachtelten Umrandungen** systematisch dieselbe eindeutige Eigentümerschaft besitzen; bloße Nachbarschaft ist weniger strikt. | GDT790/791s Panelhierarchie, originale bereits zugelassene Figuren-/Beckenbilder. Einen Record mit echter Verschachtelung und zwei plausiblen Ebenen vollständig auditieren, 5 Minuten. | Umrandungen können dekorativ sein; die geschlossene Bad-/Owner-Topologieroute könnte den ganzen Vorschlag bereits abdecken. Keine GDT388-Kante allein aus Einschluss. |
| IP027 | Bei unabhängig dokumentiertem **Fehlen** eines grafischen Teils entfällt dessen behaupteter Textbeitrag, während andere Beiträge bestehen bleiben; das unterscheidet komponentielle Beschriftung von pauschalem Eintragsnamen. | Paar aus vollständigen, unbeschädigten Objektzeichnungen mit gesicherter Zuordnung und gleicher Vorlage, noch nicht nachgewiesen. Kleiner erster Schritt: existierende Karten auf ein solches negatives Gegenstück prüfen, 5 Minuten. | Auslassung, Beschädigung und andere Art sind leicht zu verwechseln. Ohne unabhängig gesichertes Gegenstück kein Test; keine alte Blütenzählung neu etikettieren. |

### F — Werte, Maße und Rechenrelationen

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP028 | Ein additives Zahlensystem sollte einen geschriebenen **Gesamtwert und Teilwerte** durch dieselbe arithmetische Beziehung verbinden; bloße Stufen-/Klassenzeichen müssen das nicht. | GDT686/764 bekannte Wertfelder als Start, dazu unabhängig erkennbare Gesamt-/Teilrelation noch benötigt. Eine bereits publizierte Mehrfeldstelle auf einen tatsächlichen Totalmarker prüfen, 5 Minuten, keine Zahlen aus Strichzahl setzen. | Keine gesicherte Totalrelation vorhanden; ohne sie lässt sich jede kleine Reihe nachträglich passend rechnen. |
| IP029 | Ein Verhältnis statt einer Menge bleibt bei **gemeinsamer Skalierung** mehrerer Nachbarwerte unverändert; ein absoluter Betrag verändert sich. | Zwei unabhängig als dieselbe Rezept-/Mischungsrelation gebundene Records mit verschiedenen Werten, bisher nicht festgestellt. Kapazitätsprüfung nur an publizierten vollständigen Parallelrecords, 5 Minuten. | Gleiche Rezeptidentität ist nicht gesichert; beliebige proportionale Lesungen liefern keine Evidenz. |
| IP030 | Eine Rangangabe verträgt geordnete Zwischenwerte, ein Kategorienindex dagegen nicht notwendig: ein unabhängiger **zwischen zwei Endzuständen gezeichneter Zustand** sollte schriftlich zwischen den beiden Werten liegen. | Vollständige visuelle Dreierreihe mit unabhängig lesbarer gradueller Eigenschaft; GDT812s skalare Rivalen als Vorgänger. Erst Eignung eines publizierten Dreiers prüfen, 5 Minuten. | Physische Reihenfolge ist keine Wertordnung; kalender-/ordinalbezogene geschlossene Routen unbedingt prüfen. Keine neue Zahlenbedeutung aus bloßer Platzfolge. |
| IP031 | Ein Maßeinheitenwort müsste bei einem Wechsel zwischen zwei unabhängig erkennbaren Maßarten eine **wiederkehrende Umrechnung** zulassen; ein Stoffname verlangt keine konstante Umrechnung. | Dokumentierte doppelte Wertangabe desselben Gegenstands mit unabhängig verankerten Einheiten; noch keine Quelle bekannt. Zuerst vorhandene Mengenberichte auf ein echtes Doppelmaß prüfen, 5 Minuten. | Aktuell hoher Datenbedarf; historische Umrechnungszahlen dürfen nicht zur Suche passender Voynich-Zahlen missbraucht werden. |

### G — Aufbau des Dokuments und gemeinsame Textvorlage

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP032 | Wenn getrennte Schriftbereiche eine gemeinsame Vorlage zeilenweise umsetzen, bewahren **seltene vollständige Mehrgruppenmotive** ihre relative Abfolge auch bei anderem Layout; unabhängige Textzusammenstellungen müssen das nicht. | Vorhandene vollständige Seiten und veröffentlichte Wiederholungen; GDT838/829 als Kapazitätsgrenze. Nur bereits bekannte Motivkontakte auf eine zweite unabhängig gebundene Reihenbeziehung prüfen, 5 Minuten. | Wahrscheinlich Wiederaufnahme der geschlossenen Parallelstellenkapazität; ohne neuen unabhängigen Motivanker kein Suchlauf mit gelockerten Regeln. |
| IP033 **REVIEW_PRIORITY** | Wenn zwei Schreiber dieselbe Vorlage in unterschiedlichen Schriftkonventionen wiedergeben, bleiben **vollständige mehrteilige Relationstypen** über Handwechsel erhalten, während grafische Realisierungen gemeinsam wechseln; bloßer Themenwechsel verändert auch die Relationen. | Bestehende Handmetadaten, unabhängige Recordgrenzen und positive Binnen-/Gruppenstruktur aus `STRUCTURAL_KNOWLEDGE.md`. Zuerst ein publiziertes Recordpaar mit gleicher unabhängig sichtbarer Aufgabe und verschiedenen Händen auf einen vorab beschreibbaren Unterschied prüfen, 5 Minuten. | Schreiber, Sektion und Aufgabe können untrennbar gekoppelt sein; ohne echten gekreuzten Kontrast keine neue Multihand-Statistik. |
| IP034 | Ein ursprünglicher Anschluss zwischen zwei Blättern könnte durch **unvollständige Endkonstruktion plus eindeutige Anfangsergänzung** erkennbar sein, selbst wenn heutige Reihenfolge anders ist. | Kodikologische Lagenmetadaten und vollständige End-/Anfangsrecords; kein Kandidat vorausgesetzt. Eine bereits dokumentierte Unterbrechung auf genau eine erlaubte Ergänzung prüfen, 5 Minuten, keine global beste Umordnung suchen. | Konstruktionsgrenzen sind nicht Goldstandard; Seitenreihenfolgeoptimierung kann scheinbare Kohärenz erzeugen. Beschädigte/versiegelte Seiten bleiben ausgeschlossen. |
| IP035 | Ein tabellarisches Arbeitsschema bewahrt **Spaltenrollen bei variabler Reihenfolge der Records**; narrative Fortsetzung bewahrt eher die Reihenbeziehungen als starre Felder. | Native Pharma-Records und GDT791s dokumentierte Recordgrenzen, Rollen zunächst nur geometrisch. Zwei klar vergleichbare vollständige Records auf dieselben unabhängig abgegrenzten Felder und unterschiedliche Feldbelegung prüfen, 5 Minuten. | Layoutgrammatik wurde bereits weit untersucht; neue Erkenntnis nur bei einem konkret noch offenen Modellkontrast. Keine Stellungsregel als Übersetzung ausgeben. |

Quellenkürzel GDTNNN sind mit `./vmanus-work lookup GDTNNN` aufzulösen, bevor eine
Idee `REVIEWED` erhält. Genannte Docs sind relativ zu `docs/`; keine neue Aufnahme
oder Textzulassung folgt aus einem Quellenhinweis. Es wurden **28 Rohideen in
7 Familien**, davon **5 REVIEW_PRIORITY**, abgelegt; **0 neue REVIEWED-Ideen**.
Schreibzuständigkeit dieser Fassung an root zurückgegeben.

### Root-Auswahl und begrenzte Vorgängerhinweise

Die fünf Prioritäten bleiben eine Prüfauswahl, kein Versuchsauftrag. IP014 ist
der erste Kandidat für eine vertiefte Vorgänger-/Definitionsprüfung: Welche
konkrete beobachtbare Stelle und welche vorab begrenzte Prüffunktion wären
gemeint? Ohne diese Festlegung kein Suchlauf über frei gewählte Zeichenwerte.
Der erste route-check `checksum parity modular order invariant check symbol
content multiset` liefert keinen direkten Beleg für Neuheit; ebenso wenig die
Dateinamensuche nach checksum/parity/check_digit. Der vollständige Vorgängerabgleich
ist offen. IP014 bleibt RAW_UNSCREENED, kein Prüfsummenbefund.

Für IP021 hat root GDT273/GDT344-Primärberichte, GDT802s Bericht sowie Teile von
GDT608 gelesen: grobe q13-Feldzustände, atomare Tupelübergänge, unmittelbare
l/m-Nachbarn und BPE-Außenkanten sind unterschiedliche bereits geprüfte Ebenen.
Daraus folgt weder Erfolg noch Neuheit einer nichtlokalen Ganzgruppenkopplung;
GDT803/804 und die Kapazitätsvorgänger bleiben vor einem Test zu prüfen.
Für IP016/017 nennt der unabhängige Reviewer zusätzlich
`experiments/semantic_assumptions/results/il011_timm_direction_control_report.md`:
der dortige feste Generator ist bereits verworfen; ein bloßer neuer Fit wäre
keine neue Beobachtung. Zeitlich geordnete Korrekturen brauchen weiterhin eine
unabhängig gesicherte Chronologie, die RCD001 nicht liefert.

Diese Hinweise sind Navigation für die nächste Auswahl. Keine neue Manuskript-
auswertung, kein Reifegrad auf REVIEWED angehoben und keine Seite zugelassen.
