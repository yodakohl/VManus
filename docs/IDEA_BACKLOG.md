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

**Aktueller Datenbefund: IP042/GDT845; kein weiterer Versuch ausgewählt.**
Die frühere Fünferauswahl wurde gebündelt geprüft: IP009/IP021/IP022/IP036
brauchen zunächst einen belastbaren Beobachtungsträger; Einzelbefunde unten.
IP014 und IP018 sind nach root-Vorgängerprüfung zurückgestellt; die begrenzten
Prüfergebnisse stehen unten. IP036 rückt als ungeprüfter Kandidat nach.
Reihenfolge: konkrete mechanistische Unterscheidung, möglichst vorhandene Quellen,
Begrenzbarkeit des ersten Tests. Keine Erfolgswahrscheinlichkeit geschätzt.
Für die Übernahme sind Quelle, Admission, Vorgänger, kleinster informativer Test
und Gesamtbudget zu klären; die untenstehenden Minuten sind grobe Gesamtziele,
keine Zusage ausreichender Daten oder abgeschlossener Bestätigung.

### A — Physische Herstellung der Schrift

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP008 | Wenn hohe Zeichen Platzkonventionen ausdrücken, weicht ihre obere Form bei geringer **vorher vorhandener** freier Höhe systematisch aus; ein rein positionsgebundenes Zeichen verlangt diese örtliche Anpassung nicht. | Native Orientierung in `visual_overview/README.md` als Startpunkt; konkrete hohe Zeichen neben gezeichneten Hindernissen müssen erst lokalisiert werden. Zwei eindeutig begrenzte Situationen auf zugelassenen Seiten nativ gegenüberstellen, 5 Minuten. | Gezeichnetes Hindernis kann später entstanden sein; ohne unabhängige Herstellungsfolge keine kausale Platzbehauptung. Nicht l/m-Breite nochmals messen. |
| IP009 | Wenn Teile zweier geschriebener Gruppen gemeinsam ausgeführt wurden, können **durchgehende, beiden zugehörige Striche** die sichtbare Gruppengrenze kreuzen; separat geschriebene Einheiten können nur überlappen. | Ganze hochaufgelöste Gruppen auf zugelassenen Seiten, Ausgangspunkt sichtbare Haken-/Bogenformen im nativen Dossier; konkrete Fundstelle noch unbestimmt. Maximal eine vorab begrenzte Textregion auf eindeutige gemeinsame Strichführung prüfen, 5 Minuten, unauflösbare Überlagerungen ausschließen. | Aus einem statischen Bild lässt sich eine Federbewegung oft nicht nachweisen; eine Ligatur beweist weder gemeinsame Bedeutung noch Lautwert. |
| IP010 | Eine vorgeplante Zeilenfüllung verändert bereits die **frühen** Gruppenbreiten in Abhängigkeit von der später benötigten Gesamtbreite; bloße Reaktion am rechten Rand setzt erst spät ein. | Bereits zugelassene Textblöcke und verlustlose Gruppen, bekannte variierende Schriftflächen aus `visual_writing_order/PROPOSAL.md`. Zuerst wenige Linien mit wiederholten Anfangsformen auf geometrische Vergleichbarkeit prüfen, 5 Minuten; erst danach unabhängige Breitenregel einfrieren. | Textlänge und Breite sind gemeinsam erzeugt; ohne unabhängige Sollbreite kann der Vergleich zirkulär sein. GDT829s fehlende Langparallelstellen nicht durch gelockerte Flanken ersetzen. |
| IP011 | Wenn ein Schreiber eine zeichnerische Vorlage nachzieht, bleibt bei einer Abweichung die **Reihenfolge mehrerer markanter Kurven entlang des ganzen Wortes** eher erhalten als ihr Abstand; eine inhaltliche Neufassung braucht dies nicht. | Positive physische Zustände RBR001, vollständige Grenze RBR002. Benötigt tatsächlich neue spektrale Daten; an einem vollständig recoverierbaren Wort beide Strichpfade ohne Zeichenbenennung vergleichen, 10 Minuten nach Aufnahmeverfügbarkeit. | Aktuell fehlt der benötigte neue Datensatz; zwei alte Teilformen erlauben keine Wiederöffnung der geschlossenen korrigierten-Ring-Route. |

### B — Graphem- und Codierungseinheiten

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP012 | Wenn komplexe Zeichen räumlich montierte Einheiten sind, bewahren wiederkehrende Komponenten ihre **Anschlussstellen** auch dort, wo ihre lineare EVA-Reihenfolge schwer darstellbar ist. | GDT605s rein transkriptionsbasierte Einheiten als Vorgänger, Originalbilder für einen vorher ausgewählten komplexen Zeichentyp. Zunächst zwei vollständige Bildvorkommen topologisch beschreiben, 5 Minuten; keine neue EVA-Lesung erzwingen. | Ein wiederkehrender Schreibstil kann dieselbe Geometrie erzeugen; die bekannte IGR002-Grenze gegen weitere grobe Zeichenklassifikation muss vorab geprüft werden. |
| IP013 | Bei einem graphischen Positionscode bleibt die Orientierung einer Teilform relativ zur **Wortgrundlinie** fest; bei seitenfestem Zusatzcode bleibt sie relativ zur Seite fest, auch in gedrehter Kreisschrift. | Native Kreisschriftbeobachtung in `visual_overview/README.md`, vollständig lokalisierte wiederholte Ganzformen. Nur zwei deutlich verschieden orientierte Stellen desselben Typs prüfen, 5 Minuten. | Schreibergonomie erklärt ebenfalls Unterschiede; kein Stern-/Kalenderwert folgt. Wiederholungs- und Zuordnungskapazität ist unbekannt. |
| IP014 | Falls eine Gruppenkomponente ein Kontrollzeichen ist, bestimmt eine **feste, reihenfolgeunempfindliche Prüffunktion** des restlichen Inhalts sie auch bei neuen Inhaltskombinationen; reine Anschlussgrammatik benötigt diese Invarianz nicht. | Bekannte Binnenstruktur aus `STRUCTURAL_KNOWLEDGE.md`, zugelassene rohe Gruppen erst nach Freeze. Eine kleine vorab bestimmte Familie von Paritäts-/Restklassenregeln an einem festen Entwicklungsanteil prüfen und gesamte Auswahlkosten offenhalten; 10 Minuten für eine Kapazitätsentscheidung. | Nahezu jede kleine Zeichenmenge lässt nachträgliche Scheinkorrelationen zu. Ohne explizit begrenzte Regelklasse und spätere zurückgehaltene Kombinationen kein positiver Codierungsbefund. |
| IP015 | Ein Code aus variabel langen Einheiten kann trotz fehlender Trennzeichen **eindeutig zerlegbar** sein; konkurrierende Grenzen müssen dann durch denselben festen Einheitenvorrat ausgeschlossen werden. | GDT605s veröffentlichter Einheitenvorrat und Rohdarstellung; vorab prüfen, welche Grenzen der Lerner schon geliefert bekam. Kleinster Test ist eine exakte Mehrdeutigkeitsanalyse des eingefrorenen Vorrats, 5 Minuten. | Zeigt möglicherweise nur eine vom Algorithmus erzeugte Eigenschaft. Der gescheiterte Ein-Buchstaben-Code wird dadurch nicht wiederbelebt, kein neuer Decoderlauf. |

### C — Kopieren, Gedächtnis und lokale Erzeugung

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP016 | Bei Kopieren aus dem **sichtbaren schon geschriebenen** Text sollten seltene Kombinationen eher rückwärts erreichbare Vorlagen besitzen; ein zeitlich symmetrischer thematischer Zusammenhang muss diese Richtung nicht zeigen. | Vorhandene rohe Textquellen plus dokumentierte räumliche Ordnung; GDT001s Copy/Modify-Kontrollen als Vorgänger. Zuerst an einem fest begrenzten Block die definierten rückwärts/vorwärts erreichbaren Vorlagen darstellen, 5 Minuten, keine Sprachbewertung. | Abfolge ist oft nicht sicher und Neuheit nimmt auch in echter Sprache gerichtet ab. Alte lokale Ähnlichkeits-/Kopierrouten könnten dies bereits abdecken. |
| IP017 | Eine mitkopierte lokale Abweichung bildet eine **verzweigte Vererbung**: spätere vollständige Passagen teilen mehrere gekoppelte Besonderheiten, nicht bloß häufige Einzelgruppen. | Bereits dokumentierte Wiederholungen; GDT838/829 als harte Kapazitätsvorgänger. Zuerst nur publizierte Wiederholungsbeispiele auf mindestens zwei gekoppelte unterscheidbare Merkmale prüfen, 5 Minuten. | Ausreichende Passagen könnten fehlen; keine Wiederholung der erfolglosen Suche mit kürzeren Flanken oder kleinerem Fenster. Ohne neuen Anker stoppt die Idee. |
| IP018 | Wenn mehrere benachbarte Varianten in einem gemeinsamen Herstellungsschritt erzeugt wurden, wechseln **zwei voneinander getrennte Formmerkmale synchron**; unabhängige Einzelersetzungen sagen solche gebundenen Wechsel nicht voraus. | Quelle: etablierte komplette lokale Paradigmen, zunächst GDT747/GDT748-Berichte. An genau einem schon publizierten mehrteiligen Paradigma prüfen, ob die Kopplung gegenüber unabhängigen Austauschmöglichkeiten überhaupt beobachtbar ist, 5 Minuten. | Die Merkmale können bereits dieselbe formale Klasse codieren oder durch Auswahl gekoppelt sein. Keine alte Rollenmaskierung, keine neue Bedeutungszuweisung aus Ähnlichkeit. |
| IP019 | Ein begrenzter Zwischenpuffer erzeugt einen **Abstandseffekt nach geschriebenen Einheiten**, auch wenn physische Zeilen unterschiedlich lang sind; eine Blicksprungquelle folgt eher der räumlichen Distanz. | GDT001-Kontextmodelle, dokumentierte ungleich breite Layouts, genaue Gruppenkoordinaten noch erforderlich. Zunächst nach einem vorhandenen Block suchen, in dem Einheitendistanz und Bilddistanz auseinanderfallen, 5 Minuten Metadaten-/Kapazitätsprüfung. | Ein hinreichender Koordinatensatz könnte fehlen; Federzustandsroute830/831 nicht reparieren. Gedächtnis und Sprache können dieselbe Distanzstruktur tragen. |

### D — Grammatische Abhängigkeiten ohne Wortübersetzung

| ID | Konkrete Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP020 | Ein lokaler Einbettungsmechanismus erlaubt **Klammerung**: dieselbe äußere Konstruktion umschließt unterschiedlich lange vollständige innere Folgen, deren Randverträglichkeit erhalten bleibt. | GDT581s strukturierte Edition als Hypothesengeber, Rohgruppen zur späteren Kontrolle. Ein publiziertes Paar mit verschieden langer Mitte suchen und die behaupteten Grenzen ohne semantische Tags begründen, 5 Minuten. | Parserklammern können genau die gesuchte Struktur hineingetragen haben. IL026s geschlossene höhere-Ordnung-Route vor jedem Test prüfen. |
| IP021 | Bei positionsübergreifender Kongruenz koppeln Merkmale zweier wiederkehrender Ganzformen auch dann, wenn **unterschiedliche Zwischenfolgen** auftreten; eine feste lokale Formel verlangt die Zwischenvariation nicht. | Vorhandene komplette Kontextkarten, GDT803/804 als Vorgänger. Nur publizierte Beispiele auf einen konstanten Zweierbezug bei mindestens zwei verschiedenen Mittelfolgen prüfen, 5 Minuten. | Kann lediglich Topic-/Schreiberkonfundierung sein; keine Buchstabensuffixe als Grammatikwerte voraussetzen und keine fehlende Kapazität durch größere Radien retten. |
| IP022 | Wenn eine Konstruktion wirklich einen Geltungsbereich eröffnet, verändert ihre Wiederholung **nicht bloß die Häufigkeit**, sondern welcher der folgenden gleichartigen Einträge zu welchem früheren Eintrag gehört; ein einfacher Reihenmarker sagt diese verschachtelte Konkurrenz nicht voraus. | Vorhandene vollständig erhaltene Mehrfeld-Records, zunächst GDT763/764/769 als Primärvorgänger. Eine konkrete geschriebene Folge mit zwei konkurrierenden offenen Feldern nominieren und prüfen, ob beide Modelle verschiedene nächste zulässige Formen vorhersagen, 5 Minuten. | Ohne unabhängige Randmarkierung bleibt die Zuordnung unentscheidbar; keine neuen Teilnehmer über alte Arbeitsübersetzungen erfinden. |
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

Die fünf Prioritäten bleiben eine Prüfauswahl, kein Versuchsauftrag.

**IP014: enge deterministische Endzeichenvariante durch vorhandene Evidenz
widersprochen; allgemeiner Entwurf braucht einen konkreten Träger.**
Primär gelesen: [GDT800](../experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/REPORT.md)
und GDT217s Ergebnis. GDT217 betrifft Querverweisschlüssel, nicht Prüfsummen.
GDT800 dokumentiert `okalal` und `okalam` mit visuell verschiedenen Endformen,
bestätigt in allen drei alternativen Lesungen desselben Manuskripts.
Für die ausdrücklich eingeschränkte Regel `letztes sichtbares Zeichen = F(Rest)`
folgt zugleich `F(okala)=l` und `F(okala)=m`: keine Funktion erfüllt beides.
Das gilt sogar für eine reihenfolgeabhängige Funktion; Gewichte oder Moduli
müssen dafür nicht gesucht werden. Die Vorhersage muss den exakten sichtbaren
Wert determinieren, sonst greift dieser Widerspruch nicht.

Dies ist eine logische Folgerung aus einem alten Befund, keine neue Beobachtung
und keine allgemeine Widerlegung von Prüfsummen. Gleiche latente Werte mit
verschiedenen Schreibungen, Positions-/Zustandsabhängigkeit, Fehler oder andere
Kontrollzeichenträger bleiben außerhalb dieses eng definierten Modells.
Solche Erweiterungen benötigen einen eigenen motivierten Beobachtungsvertrag,
keinen nachträglichen Fit zur Rettung dieser Endzeichenfunktion. IP014 verliert
seine Prüfpriorität; keine neue Auswertung oder Quelle wurde dafür benötigt.
Route-check dieser Prüfung: `checksum parity modular check digit permutation
invariant terminal character`. Die Gesamthistorie wurde nicht erschöpfend geprüft.

**IP018: zwei unabhängige schriftliche Änderungsmerkmale noch nicht benannt.**
GDT747s konkretes Paradigma `tchey qokchey qochey` zeigt einen gemeinsamen
sichtbaren Ausklang; die dort gekoppelten Temperatur-/Stufenachsen sind
Arbeitsdeutungen. GDT748 nominiert über bestehende Achsenkarten und Ganzformnähe.
Die gelesenen Ergebnisabschnitte beider Primärberichte liefern deshalb noch
keinen ausgewählten Fall mit zwei separat definierten schriftlichen Merkmalen,
deren Kopplung geprüft werden könnte. Keine Behauptung, alle Artefakte enthielten
keinen solchen Fall. IP018 bleibt ohne diesen Träger zurückgestellt, nicht READY.
Route-check: `paradigm coupled simultaneous independent two feature change
GDT747 GDT748`. Keine erneute Prüfung der bekannten Bedeutungsabhängigkeit.

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

## Ergänzender Rohvorrat — acht andere Codierungsmechanismen

**IP036–IP043 sind sämtlich `RAW_UNSCREENED`.** Sie ergänzen den bisherigen
Vorrat um unterscheidbare mechanistische Vorhersagen; weder ihre Neuheit noch
Quellenkapazität ist geprüft. IP014 wurde auf root-Hinweis aus der Top-5-Auswahl genommen; IP021 rückt als
weiterhin ungeprüfte Hypothese nach. Root hat anschließend auch IP018 aus der
Prüfauswahl genommen; IP036 rückt nach. IP018 bleibt ausdrücklich nicht READY.
Die Ideen setzen keine neue Bildnähe, Textposition oder bereits übersetzte Rolle
als Erklärung ein. Quellenhinweise nennen spätere Prüfstellen, keine positiven
Belege für den neuen Mechanismus. Tests erst nach Vorgängerprüfung und Freeze.

| ID | Mechanismus und unterscheidende Vorhersage | Nötige Quelle und kleinster Test | Hauptrisiko |
|---|---|---|---|
| IP036 | **Umstellung innerhalb einer vollständigen Einheit:** Zwei Realisierungen derselben unabhängig gebundenen Einheit unterscheiden sich in der Reihenfolge, bewahren aber exakt dieselbe **Multimenge** geschriebener Atome; eine Ersetzung muss das nicht. Eine einzige unveränderte Umstellungsregel muss auch eine weitere unabhängige Einheit vorhersagen. | Vollständige, bereits belegte Alternativrealisierungen mit unabhängig begründeter Zusammengehörigkeit; zuerst GDT338/345 und geschlossene Minimalpaarrouten prüfen. Kleinster Test: an einem schon publizierten gebundenen Paar entscheiden, ob eine feste Umstellung überhaupt möglich ist, 5 Minuten; kein freies Anagrammsuchen im Korpus. | Zusammenhang zweier Formen darf nicht aus ihrer Multimengengleichheit abgeleitet werden. GDT839s Grenzverschiebung prüfte eine andere Erhaltung, rechtfertigt aber keinen automatisch neuen Weg. |
| IP037 | **Selbstsynchronisierender Code:** Nach einer Einfügung oder Auslassung kehrt eine gültige Zerlegung innerhalb einer festen kurzen Distanz zur ursprünglichen Phase zurück; ein gewöhnlicher variabler Code ohne Synchronisation kann dauerhaft verschoben bleiben. Das ist eine Eigenschaft ganzer Codesequenzen, nicht nur eindeutiger Einzelwortzerlegung wie IP015. | Ein vorab begründeter Einheitenvorrat aus GDT605 als möglicher Ausgangspunkt; Grenzen und Eignung erst prüfen. Kleinster Test: eine deterministische Einfügungs-/Löschungsanalyse des unveränderten Vorrats mit vollständigen Gegenbeispielen, 5 Minuten. | Ein algorithmisch gelernter Vorrat kann die Eigenschaft künstlich erzeugen. Das wäre zunächst nur Codekapazität, keine Behauptung tatsächlicher Schreibfehler oder Voynich-Codierung. |
| IP038 | **Homophone aus einem Vorrat ohne Zurücklegen:** Mehrere Zeichen für dieselbe Einheit werden ausgewählt, bis der Vorrat erschöpft ist; dadurch entstehen Wiederverwendungsverbote und eine Wiederkehr nach Erschöpfung, die unabhängige zufällige Homophonie nicht verlangt. | Unabhängig vorgeschlagene Äquivalenzklassen vollständiger Zeichen, noch nicht vorhanden; GDT001-Homophonieversuche und GDT338 als Vorgänger. Zunächst nur prüfen, ob eine vorhandene Klassenhypothese genügend vollständige Folgen für einen eindeutig festgelegten Wiederverwendungswiderspruch liefert, 5 Minuten. | Die Klassen nach Wiederholungsarmut zu bilden wäre zirkulär. Ohne externe Klassenbegründung kein neues Fitten versteckter Alphabete; kein pauschaler Rückschluss aus geringer Wiederholung. |
| IP039 | **Obligatorische ausgeschriebene Abkürzungskonvention:** Ein unabhängig identifizierter Abkürzungsträger ersetzt in mehreren vollständigen Wörtern immer dieselbe fehlende Folge; die Expansion muss auch in einer bisher nicht benutzten Wortumgebung passen. Eine bedeutungstragende Endung verlangt keine solche wörtliche Expansion. | Wirklich dokumentierte ausgeschriebene/verkürzte Paarung, nicht `ofaldo/ofal` oder bloße l/m-Ähnlichkeit. Ausgangsprüfung: GDT835s fehlender vollständiger Suffixinverse-Test und geschlossene Korrektur-/Minimalpaarrouten; 5 Minuten Kapazitätsprüfung vorhandener expliziter Paarungen. | Aktuell fehlt ein solcher unabhängiger Expansionsanker. Diese Idee erlaubt weder neue Suffixzählung noch Wiederöffnung von GDT840 oder eine weitere synthetische Decoderreparatur. |
| IP040 | **Harmonische Lautklassen:** Eine wortweite phonologische Eigenschaft bindet getrennte vokalartige Stellen an dieselbe Klasse, bleibt aber bei variierenden dazwischenliegenden konsonantartigen Teilen erhalten; bloße feste Silbenschablonen verlangen diese entfernungsunabhängige Kopplung nicht. | Produktive Binnenstruktur aus `STRUCTURAL_KNOWLEDGE.md`; GDT001s phonologische/konsonantische Modelle als wichtige Vorgänger. Kleinster Test: prüfen, ob eine einzige vorab begründete Zweiteilung von Stellen und Klassen konkrete bisher veröffentlichte Ganzformkontraste unterschiedlich vorhersagt, 5 Minuten. | Weder EVA-Zeichen noch gelernte Klassen sind etablierte Laute. Nachträgliches Suchen beliebiger Partitionen produziert Scheinharmonie; ohne begrenzte Hypothese kein Modellpanel. |
| IP041 | **Stellenwertnotation mit Übertrag:** Bei unabhängig gesicherter Erhöhung um eins wechselt an einer bestimmten Stelle ein Zeichen zurück und die nächste Stelle steigt — ein gekoppelter Übertrag. Additive Strichzahlen oder bloße geordnete Klassen besitzen diese spezielle Wechselregel nicht. | Eine explizit gebundene vollständige Zählfolge beziehungsweise ein sichtbarer unabhängiger Nachfolgerbezug, bislang nicht nachgewiesen; GDT686-Wertinventar als Navigationsquelle. Zunächst nach einem schon publizierten echten Übertragskontrast fragen, 5 Minuten; keine Kreisordnung als Zählfolge voraussetzen. | Die Nachfolgerrelation darf nicht aus den vermeintlichen Ziffern entstehen. Ohne unabhängig gesicherte Folge bleibt das ein Datenbedarf, keine Erweiterung der III-Arbeitslesung. |
| IP042 | **Tabellenkoordinaten statt laufender Buchstaben:** Zwei getrennt variierende Zeichenteile wählen Zeile und Spalte eines festen Codebuchs; wenn beide Koordinaten über mehrere Kontexte produktiv sind, müssen dieselben Koordinatenkombinationen konsistent dieselbe vollständige Einheit bezeichnen. Das verlangt eine wiederverwendbare zweidimensionale Zuordnung, nicht bloß viele ähnliche Wörter. | Vorhandene vollständige kombinatorische Paradigmen, zunächst GDT635/736/747 sowie GDT603/604-Codebuchvorgänger prüfen. Kleinster Test: ein publiziertes Viererrechteck auf wirklich unabhängig variierende Teile und eine zusätzliche überprüfbare Kombination untersuchen, 5 Minuten. | Morphologie erzeugt ebenfalls kombinatorische Rechtecke; ohne unabhängige Einheitengleichheit kann der Test höchstens die Architektur, nie konkrete Codebuchwerte begründen. |
| IP043 | **Rückverweis mit codierter Länge:** Ein kurzer Ausdruck steht für einen zuvor vollständig geschriebenen Abschnitt und gibt dessen Umfang an; bei unabhängig gebundenen Wiederaufnahmen muss derselbe Längencode denselben Umfang vorhersagen, auch bei anderem Inhalt. Bloßes Kopieren ähnlich aussehender Wörter wie in IP016 verlangt keinen expliziten Umfangscode. | Bereits vollständig dokumentierte längere Wiederaufnahme mit unabhängig gesichertem Ziel, derzeit offen; GDT696/700/798 und GDT838/829 zuerst prüfen. Kleinster Test: an einer vorhandenen expliziten Doppelung prüfen, ob überhaupt ein separat geschriebener Umfangskandidat existiert, 5 Minuten, ohne die Abschnittslänge an den Code anzupassen. | Bezug und Umfang könnten frei gewählt sein; dann erklärt der Mechanismus alles und nichts. Ohne unabhängig bestimmte Abschnittsgrenzen keine weitere Suche nach passenden kleinen Werten. |

Stand dieser Ergänzung: **36 Rohideen IP008–IP043** im Vorrat, zusätzlich die
alten IP001–IP007. Acht hinzugefügt, null geprüft oder getestet, null als neu
bestätigt. Schreibzuständigkeit an root zurückgegeben.


### Gezielte Auswahlprüfung IP021/IP022 — noch kein ausführbarer Kontrast

IP021 erhält `REVIEWED_NEEDS_CONCRETE_CONTRAST`, keine Versuchsfreigabe.
Route-check `nonlocal coupled variation middle same outer complete words agreement`
führte zu [GDT803](../experiments/yolo/gdt803_recurrent_context_rarity_discriminator/REPORT.md)
und [GDT804](../experiments/yolo/gdt804_bracket_middle_independent_field_bridge/REPORT.md);
beide Primärberichte wurden gelesen. Zitierbarer Ausgangspunkt ist GDT803s
`qokedy otal chedy` gegenüber `qokedy otal shedy`: hier variiert **nur der rechte
Partner**, während linker Partner und Mitte gleich bleiben. Daneben stehen
`qokeey chal chedy` und `qokeedy sail chedy`; auch sie liefern noch keinen
gekoppelten Wechsel beider Außenformen über verschiedenartige Mittelfolgen.
Die neue unterscheidende Vorhersage wäre eine feste Links-Rechts-Kopplung, die
auf einem anderen bereits vollständigen Mittelstück dieselben zulässigen
Außenkombinationen vorhersagt. Das müsste als konkretes Viererkontrastset
nominierbar sein; die gelesenen Berichte liefern es nicht. Daher keine neue
Nachbarschaftszählung und keine Kapazität behauptet.

IP022 bleibt RAW mit konkretisiertem Engpass. Route-check `nested scope two open
fields record repeated head competing attachment`; GDT764, GDT769 und GDT579
primär gelesen. GDT764 nennt tatsächlich f105v.5:
`pchedal | qopchdy daiin | chedy daiin | ...`. Das zeigt zwei **serielle** Felder,
aber keinen zweiten geschriebenen Öffner, der vor Abschluss des ersten Feldes
einen konkurrierenden Geltungsbereich eröffnet. Die in GDT579 beschriebenen
Außen-/Innenwerte gehören zur bestehenden Arbeitsgrammatik, nicht zu einem
neuen unabhängigen Quellnachweis der Verschachtelung. Die erforderliche
Konkurrenzstelle fehlt im gelesenen Bereich; kein READY-Status.

IP033 bleibt eine ungescreente Alternative: die route-check-Navigation wurde
begonnen, aber keine primär belegte Handkontrastpaarung gefunden und ausgewertet.
IP036s folgende root-Prüfung ergänzt diesen Stand. Keine allgemeine Widerlegung. Bestand bleibt
36 Ideenskizzen; diese Prüfung fügt keine ID und keinen Manuskriptbefund hinzu.
Schreibzuständigkeit an root zurückgegeben.

### Root-Prüfung IP009/IP036 — Beobachtungsvertrag vor Datentest

**IP009: NEEDS_IDENTIFIABLE_WRITING_PROCESS_OBSERVABLE.** Der Entwurf setzte
sichtbar verbundene Tinte mit gemeinsamem Schreibzug gleich. Das ist aus einem
statischen Foto allein nicht identifizierbar: eine durchgezogene Linie und
zwei getrennt ausgeführte, sich berührende Striche können dasselbe sichtbare
Tintenbild erzeugen. Eine sichtbare Brücke könnte daher allenfalls einen
Kontaktkandidaten liefern, nicht schon eine gemeinsame Federbewegung oder
linguistische Einheit. Der genannte native Überblick beschreibt Schlaufen,
Haken und Abstände, aber keine konkrete grenzüberschreitende Fundstelle.
Kein neuer Bildtest, keine Behauptung, es gebe keine Ligaturen.

Route-check `cross word boundary continuous stroke ligature pen lift interword
bridge`, dann `ligature`. Gelesen: nativer Überblick und
[IGR002-Primärbericht](../experiments/semantic_assumptions/results/igr002_image_grounded_grapheme_atlas_result_report.md).
IGR002 schließt seinen eingefrorenen Sechs-Feld-Formtransfer, nicht sämtliche
Strichfragen; sein Ergebnis liefert keine Brückenfundstelle für IP009. Ein
künftiger Test braucht eine konkret lokalisierte Stelle und eine Beobachtung,
die die behaupteten Schreibabläufe wirklich unterscheidet. Das ist keine
Neuvermessung der erfolglosen Federzustandsrouten GDT830/831.

**IP036: NEEDS_INDEPENDENTLY_BOUND_SURFACE_PAIR.** Route-check `GDT338 GDT345
transposition anagram multiset same independently bound unit`; beide direkten
Primärberichte gelesen. GDT338 prüft normalisierte opake Tupel und begründet
keine neue Äquivalenz durch die getestete Renderer-Normalisierung.
GDT345 prüft Übergänge zwischen formalen Zuständen, ausdrücklich ohne rohe
Zeichenfolgen oder semantische Identität. Keiner der beiden Berichte liefert
das geforderte konkrete rohe Umstellungspaar mit unabhängig begründeter
Einheitengleichheit. Keine Vollsuche aller Artefakte, keine Widerlegung von
Transpositionen. Ohne ein solches Paar kein freies Anagrammsuchen und kein
neuer Chiffrenfit. Die frühere Prüfpriorität ist zurückgestellt.

Die gebündelte Runde prüft vier Vorschläge vor Umsetzung; kein neuer
Manuskriptbefund und kein neues Experiment. IP033 bleibt der nächste
Kandidat zur Quellenprüfung, nicht der nächste bereits freigegebene Versuch.

### IP042 — konkreter Entdeckungsauftrag statt Codebuchbehauptung

`DISCOVERY_COMPLETED_GDT845`: [Bericht](../experiments/yolo/gdt845_extended_form_grid_discovery/REPORT.md).
72Zellen erfasst: ZL3b61belegt; alle48altenZellen jeLeser vorhanden.
`ee+d` ist mit qo6-mal vorhanden gegenüber4,020deskriptiv erwartet; leer1/5,889,
o1/3,891. Vier in allenLesern gleiche qo-Loci auf3Folios. Kein durchgängiges
Verbot, keine bestätigte Präfixregel: Seltenheit/Abschnitt/Hand bleiben offen.
Der ursprüngliche Entwurf folgt als Herkunft, nicht als noch offener Auftrag. Der
Codebuchgedanke wird zunächst auf eine rein geschriebene, unterscheidbare Frage
reduziert: **Sind die beobachteten Kombinationslücken durch Seltenheit erklärbar,
oder koppeln sich zwei nominell unabhängig kombinierbare Stellen?**

Konkrete Ausgangsbelege: [GDT624](../experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md)
belegt alle 48 Zellen von `{leer,o,qo} × {k,t} × {ch,sh} × {leer,e} × {leer,d} × y`;
auf f13r und f22r stehen jeweils `kchy`, `okchy`, `qokchy`.
[GDT646](../experiments/yolo/gdt646_tcheey_surface_completion/REPORT.md)
erweitert dagegen nur den nackten Arm auf zwei e: `kcheey/tcheey/ksheey/tsheey`
sind belegt, während drei zugehörige `eedy`-Zellen fehlen und `kcheedy` nur eine
Leservariante besitzt. Das sind bekannte positive Formen und bekannte Lücken;
der neue Auftrag wäre ihre **gemeinsame vollständige, semantikfreie Darstellung**,
nicht ihre erneute Entdeckung oder eine Grad-/Abschlussübersetzung.

Kleinster tatsächlicher Datenauftrag: vorab genau das 72-Zellen-Raster
`{leer,o,qo} × {k,t} × {ch,sh} × {leer,e,ee} × {leer,d} × y` festlegen;
über den bestehenden bewachten Leser alle vollständigen Gruppen dieses Rasters
in den 179 erlaubten Textselektoren holen. Je Zelle vollständige Rohformen,
Leserstabilität und physische Folios ausgeben; keine weiteren Endungen ergänzen.
Dies erzeugt ein beobachtbares gemeinsames Raster über die drei Wrapper, ohne
vorher bereits eine semantische oder Bildreferenz vorauszusetzen.

Gegenvorhersagen: eine unabhängig kombinierbare Darstellung erklärt fehlende
Zellen durch ihre niedrigen Randhäufigkeiten; eine bedingte Schreibbeschränkung
sagt eine wiederkehrende `ee`-mit-`d`-Unterbesetzung auch in ausreichend exponierten
Wrappern voraus. Erster Pass ist ausdrücklich **Discovery**: Rohcounts und
expositionsabhängige Erwartungswerte, keine nachträglich optimierte Schranke,
kein bestätigendes p und kein Codebuchbeweis. Ein tragfähiger Kontrast würde eine
spätere Kombinationsexklusions-Hypothese motivieren; dünne Exposition beendet
nur diesen Entdeckungsauftrag. Gesamtziel 5 Minuten mit vorhandenem Leser,
Checkpoint nach Extraktion; keine generative Decoderimplementation.

Neuheitsabgleich: route-check `coordinate grid complete factorial independent
combinations pcheey pchedy four heads` und `grid missing cells eedy length d closure
factorial structural zeros occupancy`; Primärberichte GDT624, GDT646 und GDT651
gelesen. GDT651 behandelt ein anderes CKH-Schalenraster. Die gelesenen Berichte
liefern weder diese gemeinsame 72-Zellen-Auswertung noch einen konditionalen
Lückentest; das ist keine Garantie vollständiger Archivneuheit. Vor Umsetzung
insbesondere spätere GDT646-Fortsetzungen gezielt prüfen. Risiko: bereits bekannte
Binnenlaut-/Schreibgrammatik statt unabhängiger Koordinaten; Gruppenatomisierung,
Transkriptionsvarianz und ungesehene Kombinationszahl dürfen nicht verschwinden.
Es wurde kein Rohdatensatz geöffnet oder Test ausgeführt. Ownership an root frei.

### IP033 — begrenzte Quellenprüfung

`NEEDS_INDEPENDENT_SHARED_TEMPLATE_PAIR`. Route-check `same task different
scribal hands crossed record comparison`, dann `CROSS_STRATUM_DIRECTION_SECTION_HAND
same scribal hand template`. IL010-Primärbericht und Ergebnis-/Scopeabschnitte
von GDT737/GDT791 gelesen. IL010 bestätigt nur Currier-Richtung, nicht den
Handtransfer; GDT737 überträgt eine Positionsachse auf neue Restkörper; GDT791
bietet fünf sichtbare Topologiefamilien und drei tief annotierte Seiten. Das
liefert noch kein nominiertes, unabhängig als gleiche Vorlage gebundenes
Recordpaar unterschiedlicher Hände. Keine neue Statistik, kein Rohdatenzugriff
für diese Vorprüfung und keine allgemeine Widerlegung gemeinsamer Vorlagen.

Sieben frühere Prioritäten lieferten im begrenzten Vorgängeraudit keinen
ausführbaren Kontrast. IP042 hat anschließend mit einem konkreten bekannten
Formraster einen tatsächlich ausgeführten Discovery-Pass ermöglicht. Der
Ideenvorrat bleibt bestehen; keine weitere abstrakte Vorzugsroute automatisch
ausführen. Neue Auswahl startet bei konkretem Quellbeispiel plus Vorhersage.

## Zwei vorbereitete Entdeckungsaufträge für die längere Forschungsphase

GDT845 wurde vollständig gelesen. Seine vier exakten qo-Anker und die
Sektion-S-Konzentration bleiben erhalten; der laufende Konfundierungscheck des
root wird hier nicht dupliziert. Die folgenden zwei Kandidaten benötigen kein
bereits übersetztes Goldpaar. Reifegrad jeweils `REVIEWED_DISCOVERY_CANDIDATE`:
konkreter Anker und begrenzbare neue Beobachtung, noch kein Experiment/Fund.

### IP044 — Zwei getrennte e-Läufe: gemeinsame Begrenzung oder freie Kombination?

**Anker:** [GDT633](../experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md)
dokumentiert f29r.1 `cheecthy` und f82v.36 `sheecthey`, beide dreileser-exakt.
Letzteres besitzt zwei äußere und ein inneres `e`, also bereits drei e insgesamt;
eine pauschale Grenze von zwei e wäre damit schon widersprochen und wird nicht
getestet. GDT633 berichtet ferner die vollständigen Leitern
`chcthy/checthy/cheecthy` und `shcthey/shecthey/sheecthey`.
[GDT651](../experiments/yolo/gdt651_ckh_four_shell_family_migration/REPORT.md)
liefert den anderen Kern CKH mit `checkhy/checkhey` und `sheckhy`, unter anderem
in der vollständigen Zeile f80r.43. Sämtliche alten Sachwerte bleiben außen vor.

**Neue Frage/Gegenvorhersage:** Sind die Längen zweier **getrennter Vorkommen
desselben geschriebenen Atoms** unabhängig kombinierbar, oder geht ein längerer
äußerer Lauf innerhalb desselben Kern-/Registerrahmens mit einem kürzeren inneren
Lauf einher? Die zweite Möglichkeit wäre mit einer gemeinsamen Formbegrenzung
vereinbar; sie wäre noch kein mechanischer Platzdruck und keine e-Bedeutung.
Anders als GDT845 geht es nicht um ee+d und Wrapper, sondern um die gemeinsame
Verteilung zweier räumlich getrennter e-Stellen im selben vollständigen Wort.

**Kleinster Test:** Vor der Abfrage exakt 36 Formen einfrieren:
`{ch,sh} + e{0,1,2} + {cth,ckh} + e{0,1,2} + y`.
Die 179 zugelassenen Textselektoren einmal bewacht nach vollständigen Rohgruppen
projizieren; alle 36 Zellen mit Locus, Leser, Hand und Sektion erhalten. Erst
Entdeckungstabelle pro festem Kern und ch/sh, dann Randhäufigkeiten und
beobachtete gemeinsame Belegung zeigen; keine nachträgliche dritte e-Länge,
O-/D-Erweiterung oder Gleichsetzung der drei Leser mit Replikaten. Exposition
entscheidet, ob eine spätere bedingte Hypothese überhaupt prüfbar ist.
Keine neue Seite, keine Bilder, keine maschinell erzeugten Formen als Belege.

**Kosten/Entscheidung:** 5–8 Minuten einschließlich Freeze, bewachter Extraktion,
Gegenaggregation und Publikation; erster Checkpoint nach Zellentabelle.
Gut besetzte Kontraste könnten ein konkretes Zweistellenmodell motivieren;
zu wenige gleichzeitige e-Läufe ergeben einen dokumentierten Kapazitätsstopp,
keinen weiteren Familienausbau. Hauptrisiken sind Register-/Handkonfundierung,
Schreibgruppenfehler und geringe Doppelbelegung. Auch echte Abhängigkeit wäre
mit Morphologie oder Phonotaktik vereinbar und nicht automatisch ein Code.

**Vorgänger:** route-check `two e slots inner outer commutation insertion
displacement checkhey sheckhey` und `outer inner e length total budget cth two
independent runs`; GDT632/633 primär gelesen, GDT651 und GDT845 ebenfalls.
Die alten Berichte belegen getrennte Leitern und geben ihnen Arbeitswerte,
berichten aber keine gemeinsame vollständige Zweilängenmatrix in beiden Kernen.
Das ist gezielter Neuheitsabgleich, keine Garantie vollständiger Archivabdeckung.

### IP045 — Was wird unmittelbar wiederholt: ein Wort oder ein ganzer Block?

**Anker:** [GDT651](../experiments/yolo/gdt651_ckh_four_shell_family_migration/REPORT.md)
nennt die dreileser-strikte Folge f83r.27
`dain chedy qokeedy shckhedy shckhedy`.
[GDT820](../experiments/yolo/gdt820_grouped_predicate_repetition_context/REPORT.md)
behandelt ferner das chedy-Doublet auf f76r.23 samt weiterem chedy und korrigiert
explizit, dass f75r.33 kein solches Doublet ist. Einzelgruppen-Wiederholung ist
also ein konkreter vorhandener Befund; ihre Wortart und Funktion sind offen.

**Neue Frage/Gegenvorhersage:** Ist die kleinste exakt wiederholte Einheit
überwiegend eine vollständige Gruppe X, oder gibt es eigenständige Wiederholung
von **verschiedenen** Gruppenfolgen `XY XY` bzw. `XYZ XYZ`? Ein unmittelbarer
Einzelgruppen-Duplikationsmechanismus allein kann Perioden 2/3 mit unterschiedlichen
Gruppen nicht hervorbringen; ganze Blöcke kopieren oder wiederholen schon.
Das wäre eine Aussage zur notwendigen Erzeugungseinheit, kein Nachweis eines
Abschreibfehlers, einer Handlung oder einer bestimmten syntaktischen Konstruktion.

**Kleinster Test:** Fester textweiter Discovery-Zensus innerhalb einer einzelnen
physischen Zeile, nur sicher getrennte vollständige Rohgruppen, minimale Periode
1, 2 oder 3 und mindestens zwei vollständige Wiederholungen. Alle Vorkommen
speichern; `XXXX` zählt als primitive Periode 1, nicht zusätzlich als Periode 2.
Grenzen mit Zeichnungsunterbrechung oder unsicherem Abstand nicht überqueren;
Varianten getrennt lassen. Häufige unabhängig auftretende XY können zufällig
doppelt nebeneinanderstehen: darum primär Beispiele/Kapazität, keine mechanische
Erklärung aus einem Treffer und kein ungeprüfter Signifikanzgewinn.

**Kosten/Entscheidung:** 8–10 Minuten mit vorhandener bewachter Gruppenquelle,
Präregistrierung des Discoveryumfangs, einfacher unabhängiger Periodenprüfung
und Veröffentlichung. Mehrgruppige primitive Wiederholung liefert ganze konkrete
Passagen für eine spätere Funktions-/Herstellungsfrage. Nur Periode 1 beendet
diesen Zensus; kein Verlängern, Zulassen ähnlicher Gruppen oder Suchabstand.

**Vorgänger/Abgrenzung:** route-check `tandem repeats primitive period complete
group blocks XY XY repetition` sowie `primitive tandem exact period two three
whole word sequence adjacent blocks`; GDT574 primär gelesen, GDT820 REPORT und
WORKING_THEORY geprüft. GDT574s 43 Nachbarpaare sind Handlungsatome innerhalb
der bestehenden Arbeitsedition, kein primitiver Periodenzensus vollständiger
Quellgruppen. GDT820 bewahrt 67 rohe Doppelpaardarstellungen, liefert im gelesenen
Bericht keine vollständige Perioden-2/3-Aufnahme. GDT838 suchte nichtidentische
Rekodierungsabbildungen zwischen 16-Gruppen-Fenstern auf verschiedenen Folios;
GDT829 andere Umbrüche gleicher Langkontexte. Keine dieser Fragestellungen wird
mit kleineren Fenstern neu ausgeführt: hier ist die neue notwendige Eigenschaft
**unmittelbare identische Blockwiederholung innerhalb derselben Quellzeile**.
Vor dem Start bleibt ein gezielter Blick auf GDT820s Methodenumfang sinnvoll,
um einen unvermutet bereits gespeicherten vollständigen Blockzensus auszuschließen.

Bestand: 38 Ideenskizzen IP008–IP045; IP001–IP007 und sämtliche früheren Status
bleiben erhalten. Keine Rohdaten/Bilder/Webzugriffe oder Experimente in dieser
Producer-Runde. Schreibzuständigkeit an root zurückgegeben.

## Nächste Auswahl während GDT848/GDT849

Zwei belastbar vorbereitete Kandidaten statt einer mit schwachen Entwürfen
aufgefüllten Quote. IP044 wird parallel als GDT849 bearbeitet und hier nicht
verändert. Kein weiterer ee+d-Untergruppentest.

### IP045 — Methodenumfang geprüft, weiter Discovery-Priorität 1

GDT820 METHOD wurde jetzt direkt gelesen: Sein Zensus erfasst **exakte rohe
adjazente Paare** in 172 Kernrecords plus zwei Zusatzrecords auf 14 Selektoren,
auch über geeignete P-Zeilenwechsel. Keine primitive Perioden-2/3-Inventur ist
in diesem Methodenvertrag beschrieben. GDT574 dagegen zählt gleiche
Handlungsatome innerhalb seiner Arbeitskarten. Zusammen mit GDT651s konkretem
f83r.27-Doublet ist die vorgeschlagene Untersuchung vollständiger unmittelbar
wiederholter Mehrgruppenblöcke damit hinreichend abgegrenzt, um einen kurzen
Discovery-Pass auszuwählen. Existenz solcher Mehrgruppenblöcke bleibt unbekannt.
Der frühere IP045-Umfang (eine physische Zeile, sichere Grenzen, primitive
Perioden 1/2/3, komplette negative Ergebnisse) bleibt unverändert. Keine
Nachjustierung anhand der GDT838-/GDT829-Ergebnisse. Gesamtziel 8–10 Minuten.

### IP046 — Getrennte und fusionierte Ausdrucksform: tragen sie dieselben Anschlüsse?

Status: `IN_PROGRESS` — root hat IP046 für GDT850 ausgewählt; Registrierung und Ausführung bei root.
**Konkrete Anker:** [GDT824](../experiments/yolo/gdt824_qolchedy_fixed_composition/WORKING_THEORY.md)
belegt die fusionierte Ganzgruppe `qolchedy` neben `qokain` auf f81v.17 und
f82r.2; f77r.34 ist dagegen ein bekannter ZL-joined/IT-split-Leserwechsel.
[GDT823](../experiments/yolo/gdt823_qol_source_anaphor_trial/WORKING_THEORY.md)
belegt `qol chedy qokeey` auf f81r.20/f82r.21 in allen drei Lesungen.
GDT824 hält ausdrücklich fest: In seinem begrenzten Packet folgt `qokeey`
nur den getrennten Ausdrücken. Das ist ein konkreter möglicher Kontrast,
keine neue Beobachtung und kein Nachweis von Feuer/Wasser oder Quellenbezug.

**Eigene Vorhersage:** Bei rein optionaler Raumsetzung in demselben Ausdruck
sollten nach Kontrolle des Registers und der Quellzuverlässigkeit wenigstens
wiederkehrende vollständige Folgegruppen zwischen fusionierter und sicher
getrennter Form geteilt werden. Lexikalisierte beziehungsweise unterschiedlich
gebaute Ausdrücke dürfen dagegen verschiedene Anschlussinventare besitzen.
Ein solcher Unterschied wäre eine Information über die **Einheit, auf die ein
übertragbarer Sinn angesetzt werden darf**, auch ohne einen einzigen alten
Sinnwert vorauszusetzen. Fehlender Overlap bei geringer Exposition entscheidet
nichts; Overlap beweist seinerseits keine Bedeutungsidentität.

**Kleinster Discovery-Test:** Vorab nur zwei Oberflächen einfrieren:
`qolchedy` und `qol` + DEFINITE_SPACE + `chedy`, gleicher physischer P-Zeile.
Alle exakten Vorkommen in den 179 zugelassenen Textselektoren einmal bewacht
sichern, dazu je zwei vollständige linke/rechte Gruppen, Rohgrenzen, Leser,
Hand und Sektion. Varianten und unsichere Grenzen gesondert dokumentieren.
Die bereits von GDT824 exponierten zwölf Loci markieren; der neue Output zeigt
zuerst die außerhalb dieses kleinen Packets vorhandenen **Entdeckungsbeispiele**,
die ausdrücklich nicht als ungesehene Bestätigung gelten. Native Bildkorrekturen
nicht erfinden. Kein erweitertes qol-Präfixlexikon, keine Übersetzung und keine
Suche nach Edit-Nachbarn.

**Entscheidung/Kosten:** 8–10 Minuten einschließlich Freeze, bewachter Abfrage,
Überlappungs-/Rückführungsprüfung und Publikation. Ein unter beiden Quellformen
wiederkehrender Anschluss liefert konkrete Kontextpaare für spätere semantische
Kontraste. Gut exponierte Trennung macht eine automatische freie Komposition
weniger plausibel. Reine Registertrennung oder geringe Kapazität stoppt die
Interpretation, ohne den Zensus nachträglich zu erweitern. Großer Einwand:
Abstandsmarkierung ist ein Transkriptionsurteil; schreiberabhängige Segmentierung
kann den gesamten scheinbaren Ausdruckskontrast erzeugen.

**Primärabgleich:** route-check `qolchedy joined split outside packet context
same whole separation` und `qol two orders chedy source anaphor arguments opposed
order transfer`; GDT823/GDT824 WORKING_THEORY direkt gelesen. GDT824 behandelt
13 joined plus 14 split Leserhits an zwölf Loci innerhalb seines bestehenden
Packets, nicht den vollständigen exakten Zwei-Oberflächen-Zensus aller179Selektoren.
Die neue Frage ist der beobachtbare Anschlusskontrast, nicht ein weiterer
Durchgang durch dieselben C0-Bedeutungen. Vor Start METHOD824 gezielt prüfen,
falls dort ein größerer bereits durchgeführter Anschlusszensus spezifiziert ist.

Eine dritte verlockende Idee zu zwei Qualitätsfeldern und zwei folgenden Werten
wurde nicht ergänzt: GDT810s Primärbericht zeigt bereits die fehlende allgemeine
Aritystütze und f21v.4 `chol daiin daiin`; bloßes neues Zuordnen anhand alter
Qualitätswerte wäre dieselbe Sackgasse. Ebenso liefert `s aiin` aus GDT758
allein keine unabhängige Mehrfachargumentbindung für eine neue ana-Behauptung.
Stand: 39 Skizzen IP008–IP046; keine Daten-/Bild-/Weböffnung und kein Experiment
in dieser Producer-Runde. Schreibzuständigkeit an root zurückgegeben.


## Auswahlprüfung: Was IP045 tatsächlich entscheiden könnte

**IP046 ist als GDT850 ausgewählt; IP045 bleibt
`REVIEWED_DISCOVERY_CANDIDATE`, aber nicht mehr pauschal Priorität 1.**
Die bisherige Reihenfolge wird durch diese Entscheidungsprüfung ersetzt.
GDT848/GDT849 liefern inzwischen einen lokal visuell bestätigten Zwei-Bogen-Anker
auf f104r.33#2, jedoch keine replizierte vollständige Kontrollreihe; daraus wird
hier keine zusätzliche semantische oder kodierungstechnische Evidenz abgeleitet.

**Verfügbare Fundstelle:** [GDT651, „Vier neu vollständige Zeilen“](../experiments/yolo/gdt651_ckh_four_shell_family_migration/REPORT.md)
zeigt f83r.27 `dain chedy qokeedy shckhedy shckhedy`, dort ausdrücklich
als dreileser-strikt bezeichnet. Das ist ein wirklicher Ganzgruppen-Doublet,
kein nur aus Arbeitstags erzeugtes Doppelereignis. [GDT820 METHOD](../experiments/yolo/gdt820_grouped_predicate_repetition_context/METHOD.md)
untersucht rohe adjazente Paare in 174 Records/14 Selektoren; sein Vertrag
enthält keinen primitiven Perioden-2/3-Zensus. Der verfügbare Anker belegt
also Periode 1; eine konkrete Periode 2 oder 3 ist in diesen gelesenen Quellen
weiterhin nicht belegt.

**Expliziter Mechanismengegensatz — derzeit nicht entscheidbar:** Eine unmittelbare
Mehrgruppen-Wiederholung `XYXY` wäre mit einem Kopierer ganzer Blöcke vereinbar.
Sie widerlegt aber weder gewöhnliche lexikalische/syntaktische Wiederholung noch
einen Wortgenerator, der die Folge zufällig oder kontextabhängig erzeugt.
Ebenso widerlegt ihr Ausbleiben keinen seltenen oder anders dimensionierten
Blockkopierer. „Nur wortweises Kopieren“ ist ohne spezifizierten übrigen Generator
keine Wahrscheinlichkeitsverteilung und liefert keinen belastbaren Falsifier.
Der Zensus darf daher nicht als Entscheidung zwischen Chiffre und Sprache,
als Beweis einer Phrase oder als Schätzung der Informationsmenge verkauft werden.

**Was der kleinste Test sinnvoll ändert:** Der unveränderte 8–10-Minuten-Zensus
kann die engere *beobachtbare* Behauptung prüfen, dass sichere unmittelbare
identische Wiederholungen innerhalb einer physischen P-Zeile im zugelassenen
Korpus ausschließlich primitive Periode 1 besitzen. Eine einzige sicher
zurückgeführte Periode 2/3 falsifiziert diese endliche Korpusbehauptung und
liefert eine konkrete ganze Passage als neuen Discoverygegenstand. Keine Treffer
beendet genau diesen Zensus. Das ist ein möglicher Datenfund, aber gegenüber
GDT850 nachrangig, solange kein Folgetest aus dem Fund eine eigenständige
Manuskriptentscheidung macht. Keine automatische Kontrollmodell-Baustelle.

**Neuheitsrisiko und geschlossene Nachbarroute:** route-check
`whole word primitive tandem block copying first order transition preserving Euler shuffle`
führt auch zur geschlossenen Familie
`PAIRWISE_PRESERVING_HIGHER_ORDER_LINE_ASSEMBLY`. Deren Registry-Kurzfassung
nennt IL026s gescheiterte Powerkalibrierung; der dort verlinkte Primärbericht
`results/il026_higher_order_power_calibration.md` war im Arbeitsbaum nicht verfügbar
(auch kein entsprechender Dateiname im gezielten rg-Dateiscreen). Das ist
explizit **keine gelesene Primärquelle** und keine Freigabe für eine Variante
mit neuem Euler-/Markov-Nullmodell. Vor einem solchen Wechsel müssten der
Primärvertrag wiederbeschafft und die geschlossene Route eingehalten werden.
[GDT344 REPORT](../experiments/yolo/gdt344_grammar_transition_paths/REPORT.md)
wurde direkt gelesen: 2.694 atomare GDT327-Gruppen und 2.660 Übergänge auf
17 Folios, kein übertragbarer Gewinn oberhalb des exakten Vorgängers.
Das ist kein bereits durchgeführter Ganzgruppen-Tandemzensus, erlaubt aber
auch keine Behauptung, ein neuer höherer Ordnungstest sei automatisch neu.

**Ergebnis dieser Producer-Prüfung:** In den hierfür gelesenen Primärquellen
ist kein zusätzlicher bereits verfügbarer unabhängiger Kontrast identifiziert,
der einen bestimmten Kodiermechanismus gegen gewöhnliche Wortvariation
entscheidet oder ein Textmerkmal an eine neue nichtsprachliche Beobachtung
bindet. Kein neuer READY-Kandidat und keine neue ID. IP045 ist allenfalls eine
kleine, konkrete Suche nach bisher nicht vorliegenden Beispielen; IP046/GDT850
hat den unmittelbaren Vorrang. Alle bisherigen Skizzen bleiben erhalten.
Keine Rohdaten-/Bild-/Webzugriffe und kein Experiment. Schreibzuständigkeit
an root zurückgegeben.

### Root decision after GDT850

IP046 completed: full179selector census has28target loci,16outside824s target
list. f75v.44 has both joined/split forms in ZL/IT within one line; no uniform
page/hand-only rule. No shared four-neighbor frame or semantic equivalence.
The IT split+qokain75r.33 was already known823. Primary GDT850 REPORT governs.
IP045 selected for GDT851 bounded primitive-period census only; no copying
mechanism test, no new null/IL026 reopening, no automatic enlargement.

### Root decision after GDT851

IP045 completed as fixed primitive-period census. Two all-reading ABAB
anchors f30r.11 cheor/chey and f8r.19 shol/kaiin; all p2hits4/5/3 by
reading and no p3. No copy or phrase meaning. Known850f75v.44 is retained
without new physical-discovery credit. No expansion selected. Primary851REPORT.

### IP047 — Gleiche Zeichenfolge, selektive Lücke oder allgemeine Verdichtung?

Status: `IN_PROGRESS` — root hat GDT852 ausgewählt: f75v vor Bildzugriff
neu zulassen (12→11 verbleibend). IP045/GDT851 und IP046/GDT850 bleiben abgeschlossen.

**Exakter Anker:** [GDT850 REPORT](../experiments/yolo/gdt850_qolchedy_join_split_context_inventory/REPORT.md)
belegt f75v.44 Gruppen7–8 `qol chedy` und Gruppe11 `qolchedy` in ZL/IT.
[GDT851 REPORT](../experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/REPORT.md)
bewahrt die ganze Zeile. RF bestätigt die frühe Trennung, hat später
`qolche@152;y`; die spätere exakte Zeichenidentität ist kein Dreileserbefund.

**Discriminator:** M1 erklärt die scheinbare Fusion ausschließlich durch
proportionale horizontale Verdichtung: Ziellücke und Binnenabstände schrumpfen
zusammen. M2 verändert die l→ch-Lücke selektiv. An beiden Stellen diese
Ziellücke relativ zu den sichtbaren inneren Abständen von `qol` und `chedy`
vergleichen. Klar kleinere relative Ziellücke bei ähnlich breiten inneren
Abständen widerspricht M1s *ausschließlich proportionaler* Erklärung;
proportionale Verdichtung ist mit M1 vereinbar. Ist schon der Lückenkontrast
nativ nicht reproduzierbar, bleibt nur der Transkriptionsbefund.

**Kleinster Test:** Root bindet nach Admission die korrekte Quelle. Ganze
Originalaufnahme in nativer Größe, keine Crops/Bearbeitung, kein Pixeldetektor.
Zwei getrennte native Urteile; nach versiegeltem Urteil A darf B neutrale
Pixelkoordinaten zur Lokalisierung erhalten. Ziel auffindbar ja/nein,
frühere relative Lücke größer/ähnlich/unklar, selektiv/proportional/unklar.
Unklare Lokalisierung oder Geometrie stoppt. Budget12Minuten einschließlich
Admission, Quelle, Urteilen, Bericht und Publikation; kein automatischer
Messnachfolger oder weiterer Seitenzugang.

**Entscheidung:** Sichtbar selektive Raumsetzung schärft die Beobachtungseinheit
für spätere Entzifferung: dieselbe gelesene Zeichenfolge in einer Zeile mit
unterschiedlicher relativer innerer Lücke. Keine Bedeutungsidentität,
Wort-/Morphemgrenze, absichtliche Regel, Federzugchronologie oder Grammatik
folgt daraus. Gewöhnliche unregelmäßige Handschrift bleibt als Ursache offen;
M1 ist enger als „alle nichtsprachlichen Ursachen“.

**Primärabgleich:** route-check `space suppression fusion line justification
remaining width joined split qolchedy`, `native word boundary space gap
identical glyph flank joined separated geometry` und `qolchedy f75v compression
spacing native visual boundary`. GDT850/851 sowie
[GDT784 REPORT](../experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/REPORT.md)
und [GDT819 REPORT](../experiments/yolo/gdt819_written_predicate_boundary_review/REPORT.md)
direkt gelesen:784 prüft f88r.22 chorcholsal;819 fünf Ziele auf f76r/f77r/f81r,
kein f75v.44-Bildziel. Geschlossene f67r2/f75v-Zweizeilen-Tailroute wird nicht
wiederholt: keine abhängigen Zeilen paaren, keine Suffixähnlichkeit messen.
Keine OCR/CV-Scores. Admissionfehlen anhand GDT791 PAGE_SELECTOR_SPECS und
aktueller Route geprüft. Keine Bildidentität oder visuelle Eigenschaft durch
den Producer behauptet. Keine Rohdaten/Bilder/Web oder Experimente geöffnet;
Schreibzuständigkeit an root zurückgegeben.

### Root decision after GDT852

IP047 completed: two native judgments support a localized spacing contrast
on f75v.44; physical source support, no word-boundary/meaning assignment.
Original image only, A sealed before B; no regrading.39visual keys44selectors,
11admissions remain. Primary852REPORT. No next model follows automatically.

### IL026 primary-source availability and scope, 2026-09-06

Targeted recovery found no il026/higher_order_pairwise primary artifact in
the worktree or Git path history. Retained evidence is CLOSED_ROUTE_FAMILIES
row29 and ACTIVE_EXPERIMENT_LEDGER rows168–169: synthetic power failed, no
manuscript trigram score. This is registry testimony, not a recovered or
replayed primary method. The closed family governs pairwise-preserving
higher-order residual tests; its title is not a blanket ban on every new
sequential source question. GDT851s literal census was a different endpoint.
Do not restart the failed null, strengthen planting or score sealed buckets.

### Bounded review after GDT852: IP007 and IP040

**IP007 bleibt DUPLICATE / kein neuer Auftrag.** Der gezielte Ledger-Eintrag
`f66r_border_permitted_evidence_audit` (06.08.2026) hält31/32 Zuordnungen und
bereits fehlgeschlagene Marker-/Bandüberschriften-/f57v-Ordnungsprüfungen fest.
[GDT515 REPORT](../experiments/yolo/gdt515_second_random_four_page_full_admission/REPORT.md)
nennt als konkrete Randformen `x` und `c`, aber kein gebundenes Paar
„dieses Zeichen → genau diese vollständige Textzeile“ und keine neue schriftliche
Gegenvorhersage. Der fehlende Audit-Primärbericht bleibt fehlend; keine weitere
Wiederbeschaffungsschleife gestartet. Eine bloße lokale Zeilenkennung und eine
zeilenbezogene Randannotation können dieselbe Ausrichtung erzeugen. Minimal
nötig wäre ein bereits belegter zusätzlicher Funktionskontrast, etwa ein
explizit wiederholtes Verweiszeichen mit unabhängig sichtbarem Ziel; dessen
Existenz ist hier nicht belegt. Kein neuer Bildtest zur selben Ausrichtung.

**Alternativ IP040 geprüft: NEEDS_DISCRIMINATOR.**
[GDT849 REPORT](../experiments/yolo/gdt849_two_e_run_grid_discovery/REPORT.md)
belegt konkret `chckheey` f52v.4 (0/2), `cheecthy` f29r.1 (2/0) und
`sheecthey` f82v.36 (2/1), jeweils gleiche Ganzform in allen Lesungen. Ein
obligatorischer wortweiter Gleichlauf beider geschriebenen e-Längen ist bereits
im Primärbericht als nicht gestützt abgegrenzt; das ist kein neuer Test.
Eine andere „Harmonie“-Behauptung braucht zuerst eine unabhängig motivierte
konkrete Klassen-/Stellenregel, die diese Formen unterschiedlich vorhersagt.
Eine beliebig neu gesuchte Partition würde keine Phonologie identifizieren.
Route-check `vowel harmony two e positions coupled identical length GDT849`;
keine neue Rohabfrage oder erneute Rasterzählung.

**STOP für diese Producer-Runde:** Kein belastbarer zusätzlicher Kandidat,
keine neue ID, keine Daten-/Bild-/Weböffnung. Bestehende Befunde und root-Notiz
zur IL026-Quellenverfügbarkeit erhalten. Schreibzuständigkeit an root zurück.

### IP012 — Konkreter Dreieranker für die Bildmontage, noch kein Ausführungsauftrag

Status: `REVIEWED_NEEDS_OBSERVATION_CONTRACT`. Keine neue ID.
[GDT633 REPORT, f20v.7](../experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md)
belegt `shocthy sho cthy daiin ...`: zusammengesetzte Ganzform und beide
linearen Bestandteile in derselben Quellzeile. f20v ist nach GDT791 bereits
visuell zugelassen. Der Producer hat weder Aufnahme noch Rohgruppen geöffnet;
der Bericht liefert nicht für diesen Dreier ausdrücklich einen Dreileserstatus.

**Enger möglicher Discriminator:** Ein strikt additiver graphischer Bauplan
verwendet in `shocthy` zwei intakte, lediglich platzierte Teilformen, die den
späteren alleinstehenden `sho` und `cthy` entsprechen. Ein *obligatorisch
strukturell umbauender* Bauplan verändert dagegen eine Anschlussstelle oder
ersetzt/teilt einen sichtbaren Strukturteil im Gesamtkomplex. Verglichen würden
vollständige sichtbare Formen und Verbindungen, nicht Abstände, statistische
Wortkontexte, Bedeutungen oder Federbewegungen. Ein klar erforderlicher Umbau
widerspräche dem streng additiven Modell; die Erhaltung beider Teile widerspräche
nur dem behaupteten obligatorischen Umbau, nicht optionaler Allographie.

**Minimal nächste Beobachtung:** Nach festem Quellen-/Lokalisierungsvertrag
auf dem zugelassenen Original genau diese drei Komplexe vollständig nativ
lokalisieren und beschreiben. Zuerst klären, ob alle relevanten Verbindungen
überhaupt sichtbar sind; danach intakte Teilformen / sichtbarer Umbau /
unaufgelöst. Noch vor Bildöffnung muss eine konkrete Strukturänderung als
Umbaukriterium definiert werden; bloße Größen-/Neigungsabweichung zählt nicht.
Keine Crops, Bildverbesserung, Pixelerkennung oder Glyphen-Neubenennung.
Zwei getrennte Sichturteile, zehn Minuten einschließlich Bericht/Publikation,
nur wenn root den Beobachtungsvertrag ausreichend scharf bekommt. Andernfalls
keine Durchführung. Kein Ersatz für GDT853s getrennte W-/Abstandskontextfrage.

**Nutzen/Grenze:** Allenfalls physische Absicherung oder Einschränkung eines
lokalen additiven Schreibbausteins. Weder Morphem, Laut, Übersetzung noch
allgemeiner Chiffremechanismus folgt. Normale Handschrift kann erhaltene und
umgebaute Formen besitzen; ohne engeren Mechanismus bleibt der Versuch eine
beschreibende Anschauung. Die native Unterscheidbarkeit ist noch unbekannt.

**Vorgänger:** route-check `gallows bench component insertion crossing stroke
topology` und `cth shocthy cthy f20v glyph topology intact core prefix`;
GDT631/GDT633 REPORT direkt gelesen. Die dortigen Kompositionsdeutungen sind
keine nativen Montagebefunde. GDT633s REPORT beschreibt f20v.7 als
Textbeispiel mit Arbeitslesung, nicht als eigene native Betrachtung der drei
Komplexe; das schließt unbekannte ältere Bildbeobachtungen nicht aus.
Ein wichtiges Neuheitsrisiko ist die mögliche Wiederbeschreibung längst
bekannter Ligaturkonstruktion. Es wird keine perfekte pixelgleiche Wiederholung
von Handschrift erwartet, sondern allenfalls erhaltene Anschlussstruktur. CLOSED_ROUTE_FAMILIES
`CURRENT_STA_DISAGREEMENT_VISIBLE_SHAPE_ATLAS` und Ledger1656–1660 halten
IGR002s gescheiterten groben Signaturtransfer samt ungesicherten Zuordnungen
fest. Keine solche Signaturklassifikation, Wiederzuordnung oder Schwellenänderung
vorschlagen. Der alte IGR002-Primärbericht wurde hier nicht als gelesen
behauptet; vor einer neuen Atlas-/Transferstudie wäre dessen Vertrag nötig.

Eine konkret vorbereitbare Beobachtung, null neue READY-Kandidaten; keine
weitere Quote ergänzt. Alle früheren STOP-/Quellenhinweise bleiben erhalten.
Schreibzuständigkeit an root zurückgegeben.

### IP048 — Dasselbe einzelne e an zwei Stellen: Gesamtwert, Stellenfunktion oder Ganzwort?

Status: `REVIEW_PRIORITY_NOT_READY`. Ein Kandidat mit drei konkurrierenden
Vorhersagen; keine drei künstlich getrennten Experimente. IP012 ist von root
als nächste Priorität verworfen: der obligatorische Umbau besitzt keinen
empirisch motivierten Rivalen, bloße Quellensicherheit genügt hier nicht.

**Beobachteter Anker:** [GDT849 REPORT](../experiments/yolo/gdt849_two_e_run_grid_discovery/REPORT.md)
belegt in jeder Lesung beide Ein-e-Zellen aller vier festen Familien:

| Familie | äußeres e | inneres e | ZL-Vorkommen außen / innen |
|---|---|---|---:|
| ch×cth | `checthy` | `chcthey` |26 /7|
| ch×ckh | `checkhy` | `chckhey` |46 /29|
| sh×cth | `shecthy` | `shcthey` |18 /4|
| sh×ckh | `sheckhy` | `shckhey` |33 /10|

Jedes Paar besitzt exakt dieselbe Zeichenmultimenge, Länge und e-Gesamtzahl;
nur die Lage eines e relativ zum Kern wechselt. Das ist aus dem publizierten
Raster ablesbar, kein neuer Manuskriptbefund. Konkrete ältere Zeilenanker sind
[GDT633](../experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md)
f80r.18 `... qokar shcthy qotol shecthy qokain ...` für `shecthy` sowie
[GDT651](../experiments/yolo/gdt651_ckh_four_shell_family_migration/REPORT.md)
f80r.43 `sor sheckhy qokar checkhy okain sheckhy qokeey ly` für zwei weitere
Zielganze. Ein exakt gleicher Kontext für Außen-/Innenform wird nicht behauptet.

**Drei präzise Rivalen und Vorhersagen:**

1. **Gesamt-e-Code mit konventioneller Platzwahl.** In diesem eng begrenzten
   Modell trägt nur die Anzahl der e einen inhaltlichen Wert; bei festem
   Präfix/Kern regeln Hand, Register und physische Position die Platzwahl.
   Nach diesen Kontrollen darf geschriebener Außenkontext keinen zusätzlichen
   reproduzierbaren Unterschied zwischen den beiden Ein-e-Formen liefern.
   Das Modell ist durch die beobachtete unabhängige Platzvariation motiviert,
   nicht durch eine behauptete Zahlübersetzung. Eine Erweiterung, die selbst
   kontextabhängige Platzwahl zulässt, entzieht sich ausdrücklich diesem Test.
2. **Übertragbare Stellenfunktion.** Die äußere/innere Stellung trägt eine
   wiederverwendbare Anschlussinformation. Ein aus vollständigen linken/rechten
   Nachbargruppen gelernter Unterschied muss bei ausgelassener anderer
   Präfix-/Kernfamilie in gleicher Richtung tragen. Die Gesamtsumme genügt dann
   nicht als verlustfreie Darstellung der geprüften Anschlussinformation.
3. **Familiengebundene Ganzwörter oder Allomorphie.** Unterschiedliche Außen-
   kontexte sind innerhalb einzelner Familien möglich, doch der Unterschied
   kann zwischen Familien umkehren oder ausbleiben. Ein nur lokal besseres
   Modell bei erfolglosem gemeinsamen Transfer bevorzugt diese Erklärung
   gegenüber einer universellen Stellenfunktion; es entscheidet nicht zwischen
   Lexikalisierung und sprachabhängiger Allomorphie.

**Kleinster aussagekräftiger Test:** Nur diese acht vollständigen Formen und
beide Ein-e-Lagen einfrieren; keine ee-Erweiterung, keine Suffixsuche. Vor einer
Auswertung muss ein kurzer Vertrag einen physisch-folio-getrennten Vergleich
von Metadatenbasis, gemeinsamem Nachbareffekt und familiengebundenem Nachbareffekt
festlegen. Vorhersageziel ist Außen-/Innenlage. Der konkrete mögliche Kontextkanal ist
je eine vollständige rohe linke und rechte Nachbargruppe, mit separat festen
Gewichten nach Seite: Welche Nachbarn erhöhen im Lernkern die Chance auf äußeres
e? Diese dort gelernten Gewichte werden unverändert auf den anderen Kern
angewandt; zugleich bleibt das jeweilige Zielfolio vollständig aus dem Lernen.
Die spezifische Vorhersage ist also **gleichgerichteter Außenkontext-Effekt
über cth↔ckh hinweg**, nicht bloß vorhandene e-Stellen oder Zellenzählung.
Innerhalb eines Zielfolio×Präfix×Kern-Stratums müssen beide e-Lagen vertreten
sein, damit dessen Vergleich nicht allein das Inventar der Seite spiegelt.
Keine exakte Paarung nach demselben Startindex; relative Zeilenposition und
Randstatus brauchen einen vorab festgelegten Basisterm. Das ist ein Designvorschlag,
noch kein validierter oder gepowerter Schätzer. Keine alten Qualitätstags,
Arbeitsübersetzungen oder aus dem Ziel abgeleiteten Rollen. Zieltyp, Hand/Register, physische Position und Quellgrenzen
müssen berücksichtigt werden. Zusätzlich muss der gemeinsame Effekt eine
vollständig ausgelassene Familie erreichen. Vier Familien sind wenig; Tokens
oder drei Lesungen dürfen ihre Zahl nicht künstlich vergrößern.

Die bestehende849-Matrix beweist **nicht**, dass die erforderliche Folio-
und Kontextkapazität vorhanden ist. Vorab Mindestdeckung und Stop festlegen;
kein nachträgliches Lockern von Paarungen. Keine Wiederholung der gescheiterten
853-W/Grenzverschiebung: hier weder Zwischenräume ändern noch unspacedW-Paare
suchen. Nach dieser Designprüfung Zielbudget20Minuten für gebundene Erhebung,
kleine feste Modelle, unabhängige Prüfung und Bericht; bei fehlender Kapazität
stoppen. Noch kein genehmigter Implementierungsauftrag.

**Was jede Entscheidung ändert:** Zusatzsignal mit Familienübertragung bedeutet,
dass e-Gesamtzahl plus die geprüften Konventionen nicht alle beobachtbare
Anschlussinformation bewahrt; die e-Lage muss im weiteren Strukturmodell erhalten
bleiben. Nur lokale Zusatzinformation spricht gegen freie Übertragung dieser
Stellenfunktion. Kein verlässlich messbarer Zusatz lässt Gesamtzahl als kompakte
Beschreibung dieser begrenzten Aufgabe offen, beweist aber keine Synonymie.
Keines der Ergebnisse identifiziert e als Laut, Zahl, Morphem oder Wortbedeutung;
auch übertragbare kontextabhängige Allographie bleibt als Erklärung möglich.

**Primärvorgänger/Neuheitsrisiko:** route-check `two e positions context exchange
modular operators transfer outer inner independent suffix`, `held whole form
factorial four corners context additive morphology unseen combination` und
`same multiset anagram total e count placement outside context position`.
[GDT345 REPORT](../experiments/yolo/gdt345_productive_operator_transfer/REPORT.md)
prüft nächste atomare Sechskoordinatenzustände, nicht diese geschriebenen
Ein-e-Anagrammpaare. [GDT787 REPORT](../experiments/yolo/gdt787_keedy_remainder_cross_family_transfer/REPORT.md)
hat bereits die additive Vorhersage der vierten Xkeedy-Rasterzelle geprüft:
gegen beide Vergleichsmodelle nur3/9, WHOLE_ONLY bleibt gültig. Ein erneuter
additiver Bedeutungsrest-Test wäre darum keine neue Route. IP048s möglicher
Unterschied ist **positionsveränderte Ein-e-Form bei vollständig erhaltener
Zeichenmultimenge**, mit rein geschriebenem Außenkontext als Vorhersagequelle.
GDT849 prüfte nur das gemeinsame Vorkommen der Stellen; seine Häufigkeiten
werden nicht als Test dieser drei Außenkontextvorhersagen wiederverwendet.
GDT802s Nachbartransfer und weitere Distributionsvorgänger müssen vor Auswahl
noch exakt gegen den endgültigen Vertrag geprüft werden. Kein allgemeiner
Neuigkeitsbeweis, kein Wiederöffnen einer geschlossenen Transfer-/Decoderroute.

Producer-Ergebnis: ein neuer konkret begründeter Kandidat mit drei
Gegenvorhersagen, null READY; keine Rohdaten/Bilder/Web oder Experimente.
Schreibzuständigkeit an root zurückgegeben.


### Geparkte Alternativen nach Root-Primärreview

RBR001s positiver Unterstrichbefund hat bereits den vollständigen RBR002-Stop
(2/12, null unter neun neuen Stellen) als Nachfolger. Der frühere MSI-
Verfügbarkeitscheck ist dokumentiert; keine Wiederholung dieses Audits.

LM002s Neudaten-Ausnahme bleibt prinzipiell möglich. Root stellt klar:
42 gescorte/44 Panelstellen sind nicht sämtliche bereits betrachteten Stellen;
LM00132 (16 Kalibrierung+16 held) plus X19 plus Y9 ergeben60 physisch beurteilte
Stellen. LM001Y erschöpfte A außerhalb q05. Ein möglicher neuer Pool beschränkt
sich deshalb auf restliches q05-A beziehungsweise restliches B, deren
Verfügbarkeit hier unbekannt ist. Eine neue Erhebungsphase darf keine alten
Zellen nachfüllen. Geparkt, keine Behauptung fehlender verfügbarer Daten und
keine neue Metadaten-/Bildabfrage. IP012 bleibt nachrangig, weil der zwingende
Umbau-Rivale empirisch nicht motiviert ist. Schreibzuständigkeit zurück.

### IP048 root selection: GDT854

IN_PREPARATION. Select only the shared cross-kernel raw-neighbor channel,
with each target physical folio excluded from training. Source/line-half
cells, frozen capacity and whole-folio polarity randomization replace the
proposal's unspecified baseline/model suite. No within-family rival model is
fit, so failure cannot prefer learned wholes over conventional placement.
Exact protocol: experiments/yolo/gdt854_e_placement_cross_kernel_transfer/METHOD.md.
Budget25min including publication, starting05:14UTC. No source loaded yet.
