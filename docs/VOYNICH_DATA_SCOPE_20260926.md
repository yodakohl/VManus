# Datenzugriff: Fortschreibung nach GDT1043

Diese Fortschreibung ergänzt den hashgebundenen historischen Stand in
[VOYNICH_DATA_SCOPE.md](VOYNICH_DATA_SCOPE.md), dessen Bytes für GDT968–979
unverändert bleiben. Neue Aufnahme: ausschließlich GDT1043 f85r2.

Stand: 26. September 2026, nach GDT1043. Der frühere Dokumentationsaudit
öffnete keine Daten; GDT942 hat anschließend f115v vor Bildzugriff für den
festen Absatz37–40 zugelassen. Aufnahmezahlen bezeichnen
verschiedene Einheiten; eine Quote ersetzt nicht den konkreten Zulassungsvertrag.

| Bereich | Aktueller Umfang | Verbindliche Grenze |
|---|---|---|
| Text | 179 Selektoren im [GDT631-Allowlist](../experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv) | Kein Bildrecht für 179 Seiten. GDT811s Union von 190 Selektoren und GDT327s 91-Blatt-Edition erweitern diesen Umfang nicht. |
| Bilder | 51 Bildschlüssel / 57 Selektoren; kein freier Platz im bisherigen Kontingent | GDT1043 ergänzt ausschließlich das vom Nutzer benannte f85r2. Jede neue Aufnahme vor Zugriff registrieren. f1r nur zugelassene Ränder; f106v nur der feste GDT923-Absatz für GDT924. Die Einzelverträge unten entscheiden. |
| Reserven | Keine Öffnung durch diesen Audit | Erst für eine nahezu vollständige plausible Gesamtlesung verwenden; frühere Exposition und Entwicklungsauswahl offenlegen. Freigabe ist keine unabhängige Bestätigung. |
| Explizite Sperren | f84 und f84r bleiben geschlossen; f116v ist aktuell nicht zugelassen | Historische MSI-Arbeit an f116v hebt diese Grenze nicht auf. |

## Primäre Bildzulassungen

Diese Tabelle ist ein Verzeichnis der vorhandenen Verträge, keine pauschale
Zulassung aller in einem Bericht erwähnten Seiten. Zählstand nach GDT1043:
51 Schlüssel/57 Selektoren. Der neue Eintrag betrifft ausschließlich GDT1043;
frühere Einzelverträge bleiben unverändert.

| Zulassung | Vertrag |
|---|---|
| GDT791: ursprüngliche 30 Schlüssel / 35 Selektoren | [PAGE_SELECTOR_SPECS](../experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv) |
| GDT812: f21r/f32v/f100v/f101r | [PAGE_ADMISSIONS](../experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv) |
| GDT844: f6v/f9v | [PAGE_ADMISSIONS](../experiments/yolo/gdt844_ychor_visual_subentry/src/PAGE_ADMISSIONS.tsv) |
| GDT848: f104r/f104v | [PAGE_ADMISSIONS](../experiments/yolo/gdt848_f104_visual_e_run_audit/src/PAGE_ADMISSIONS.tsv) |
| GDT852: f75v | [PAGE_ADMISSIONS](../experiments/yolo/gdt852_f75v_native_join_split_spacing/src/PAGE_ADMISSIONS.tsv) |
| GDT861 | [PAGE_ADMISSIONS](../experiments/yolo/gdt861_extended_entity_native_comparison/src/PAGE_ADMISSIONS.tsv) |
| GDT867 | [PAGE_ADMISSIONS](../experiments/yolo/gdt867_shared_canvas_native_orientation/src/PAGE_ADMISSIONS.tsv) |
| GDT871: f67r1/f68r2/f68r3 | [PAGE_ADMISSIONS](../experiments/yolo/gdt871_remaining_shared_diagram_orientation/src/PAGE_ADMISSIONS.tsv) |
| GDT881: f99v | [PAGE_ADMISSIONS](../experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/src/PAGE_ADMISSIONS.tsv) |
| Nutzerfrage zu f2r | [Einzelzulassung](visual_overview/F2R_USER_QUESTION_ADMISSION.md) |
| GDT912: f1r, nur Ränder | [PAGE_ADMISSIONS](../experiments/yolo/gdt912_f1r_progressive_key/src/PAGE_ADMISSIONS.tsv) |
| GDT924: f106v, fester Absatz | [PAGE_ADMISSIONS](../experiments/yolo/gdt924_f106v_fixed_candidate_native_audit/src/PAGE_ADMISSIONS.tsv) |
| GDT942: f115v, fester Absatz37–40 | [PAGE_ADMISSIONS](../experiments/yolo/gdt942_f115v_native_list_total_binding/src/PAGE_ADMISSIONS.tsv) |
| GDT1043: f85r2, ausschließlich benanntes Panel | [PAGE_ADMISSIONS](../experiments/yolo/gdt1043_f85r2_native_attribute_binding/src/PAGE_ADMISSIONS.tsv), [Vertrag und Bildregion](../experiments/yolo/gdt1043_f85r2_native_attribute_binding/METHOD.md) |

## Quellenidentität und Exposition

- Yale 1006204 zeigt f72v, nicht f72r. Die
  [GDT812-Korrektur](../experiments/yolo/gdt812_additional_page_semantic_bridge/src/F72R_SOURCE_CORRECTION.md)
  bleibt verbindlich. Panel-Schlüssel wie f67r2/f68r1 erhalten;
  Seite, Selektor, Bildschlüssel und physisches Blatt nicht gleichsetzen.
- GDT819s [Quellenkorrekturen](../experiments/yolo/gdt819_written_predicate_boundary_review/REPORT.md)
  gelten weiter. Rohgruppen, `@entities`, unsichere Abstände und native Flags
  erhalten. Alte Bereinigung kann Gruppen spalten oder löschen; alte Bildnamen
  identifizieren keine Pflanzenarten. Kein stiller Transkriptionswechsel.
- Gemischte TSV-Quellen, einschließlich
  `experiments/semantic_assumptions/results/source_separator_transcription.tsv`,
  nur durch `./vmanus-exp query-tsv` mit expliziten Selektor-Allow-Werten und
  Ausgabespalten lesen. f84-Präfixe vor Materialisierung des übrigen Zeileninhalts
  verwerfen; nicht ganze Zeilen parsen und anschließend filtern.
- Alte Bild- und Textarbeit ist Projektexposition. Neue Bearbeiter und alternative
  Transkriptionen machen bekannte Seiten nicht blind. Ganze physische Blätter
  einschließlich Gegenseiten bei Trennung von Auswahl und Bestätigung beachten;
  Kapazität gesondert von Befund und Zugriffserlaubnis ausweisen.
- Bereits dokumentierte Vorbelastung: Das
  [Verständnisdossier](VOYNICH_UNDERSTANDING.md) verzeichnet GDT622s versehentliche
  f84v-Zeilenexposition; [W54](../research_registry/proposals/translation_programs_20260912/work/W54/REPORT.md)
  nennt GDT674s früher verworfenen Guard-Vorfall. Hier wurden diese Vorfälle
  nicht neu untersucht oder ihre Ausgaben geöffnet. Aktuell geschlossen bedeutet
  nicht historisch niemals exponiert; keine neue Zugriffserlaubnis folgt daraus.
- NVA002/EBA001 sind vorhandene MSI-Vorgeschichte, kein neu entdeckter Kanal.
  GDT924s native Prüfung liefert sechs gemeinsam passende und elf ungeklärte
  Gruppen, keine Bestätigung aller 17 oder ihrer Bedeutungen. Details:
  [Strukturdossier](STRUCTURAL_KNOWLEDGE.md),
  [GDT924](../experiments/yolo/gdt924_f106v_fixed_candidate_native_audit/REPORT.md).

Die bis zum Audit geltende Route ist [bytegleich archiviert](../research_registry/decisions/documentation_audit_20260914/ROUTE_BEFORE.md).
Neue tatsächliche Zulassungen müssen diese Tabelle und die Route synchron
aktualisieren; historische Erörterungen dürfen ihren Umfang nicht erweitern.

## Unbeabsichtigte Suchausgabe am27September2026

Eine begleitende Quellensuche durch Markdown/JSON im Vorschlagsverzeichnis
traf mit einer unbeschränkten numerischen Alternative auch ältere Absatzdaten.
Die Ausgabe war stark gekürzt; ihr vollständiger Expositionsumfang und die
Abwesenheit gesperrter Seiten können daraus nicht bescheinigt werden. Der Lauf
wurde gestoppt, die Ausgabe nicht erneut geöffnet und von wissenschaftlicher
Verwendung ausgeschlossen. Der [Vorfallsbericht](../research_registry/proposals/laufenberg_f85r2_20260926/FACULTY_PERSONIFICATION_SUPPLY.md)
enthält nur bekannte Suchmetadaten, keine reproduzierten Transkriptionsdaten.

Keine neue Zulassung folgt daraus. f84/f84r bleiben gesperrt; dieser normative
Status ist keine Behauptung vollständiger historischer Nichtexposition. Die
laufenden568/572-Pakete verwenden ausschließlich ihre schon festgelegte
f85r2-Projektion; kein Reservetest oder unabhängiger Bedeutungsbeleg folgt aus
dem Vorfall. Künftige Quellensuchen müssen bekannte Berichte oder den Register-
Index gezielt auswählen; rekursive JSON-Suchen mit bloßen Zahlen sind dafür
ungeeignet. Eine nachträgliche Freigabe oder Rekonstruktion der Ausgabe wurde
nicht vorgenommen.

## Bekannte Ideenkarten im folgenden Quellenauftrag

Ein späterer, eng begrenzter Quellenauftrag las vier bereits bekannte
Ideenkarten vollständig, bevor eine Feldbeschränkung nachgereicht wurde.
Dadurch wurden dort gespeicherte ältere f85r2-Bindungen mit ausgegeben. Diese
Produktion ist deshalb als informierte Exploration ausgewiesen, nicht als
verblindete Quellenkontrolle. Der [separate Bericht](../research_registry/proposals/laufenberg_f85r2_20260926/SOURCE_REUSE_SUPPLY_20260927.md)
dokumentiert die bekannten Zugriffe. Die Ausgabe wird nicht zur nachträglichen
Expositionsprüfung rekonstruiert. Es gab in diesem Auftrag keine neue
Transkriptionsabfrage oder Bildzulassung; die neuen Rohideen573/574 sind weder
ausgewählt noch getestet. Ihre etwaige Auswahl benötigt den üblichen
Primärvergleich. Frühere Zugriffsvorfälle und Reservengrenzen bleiben bestehen.
