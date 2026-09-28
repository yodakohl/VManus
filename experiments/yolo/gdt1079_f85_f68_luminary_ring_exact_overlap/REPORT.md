# GDT1079 — kein gemeinsames exaktes Gruppenwort zwischen innerem f85r2-Kreis und f68r2-Leuchtringen

**Registrierte Entscheidung: `NO_RARE_SUN_ONLY_EXACT_BRIDGE`.** Der vorab festgelegte positive Fall tritt nicht ein. Der vollständige innere Schriftkreis f85r2.24 hat in **keiner** der drei alternativen Lesungen auch nur eine rohe exakte Gruppe gemeinsam mit dem unteren f68r2.31-Sonnenmedaillon oder dem oberen f68r2.6-Sichelmedaillon. Der seltene Sonnen-exklusive Treffer kann deshalb nicht existieren; weder Längen-, Abstand- noch Korpusfrequenzfilter entscheiden das Ergebnis.

| Lesung | f85r2.24 innerer Kreis | f68r2.31 unterer Sun-like Ring | rohe / geeignete Schnittmenge | f68r2.6 oberer Sichelring | rohe / geeignete Schnittmenge |
|---|---:|---:|---:|---:|---:|
| ZL3b | 13 | 12 | 0 / 0 | 8 | 0 / 0 |
| IT2a | 15 | 11 | 0 / 0 | 8 | 0 / 0 |
| RF1b | 16 | 11 | 0 / 0 | 8 | 0 / 0 |

Alle 13/15/16 f85-Gruppen und 12/11/11 beziehungsweise 8/8/8 f68-Gruppen mit Quelle, Gruppenindex, Unsicherheitszeichen, Abständen und Corpuszähler stehen in [RESULT.json](artifacts/RESULT.json). Der inneren f85-Umschrift gehören unter anderem `okees`, `ochar`, `ochedy`, `otody`; die unteren f68-Umschriften beginnen je nach Leser `okey/okeo okoaiin okol`, die oberen `okeo ok[a:?]r/okor/okar`. Diese Beispiele ersetzen **nicht** die vollständige Tabelle. Aus den existierenden Quellpaketen wurden keine Wörter repariert, keine unsicheren Formen glattgezogen und keine zusätzliche f68-Zeile gelesen.

Die registrierte Hypothese verlangte dieselbe mindestens vierbuchstabige, eindeutig getrennte genaue Form in f85 innen und f68 unten bei allen drei Lesern, nicht oben, mit höchstens zehn Außenbelegen je Leser. Bereits die ungefilterten vollständigen Schnittmengen sind leer. Daher gibt es auch keinen durch diesen Test ausgezeichneten C0-Sonnenwortkandidaten und keinen f85-Sektortreffer für einen solchen Kandidaten zu qualifizieren. Der voneinander unabhängig kodierte [Validator](artifacts/VALIDATION.json) rekonstruiert die sechs vollständigen Quellmengen und ihre leeren rohen Schnittmengen; Status PASS.

Die Entscheidung betrifft nur **unveränderte exakte Gruppenwiederholung**. Unterschiedliche Form, Paraphrase, Beugung, Synonym, textuelle Beschreibung statt Benennung und ein menschliches Mikrokosmoszentrum bleiben möglich. f85r2.24 besitzt weiterhin keine gesicherte physische Wort-zu-Winkel-Zuordnung. Die Bilder waren bereits bekannt, die zwei Vergleichsstellen nach ikonographischer Vermutung ausgewählt; drei Transkriptionen sind keine unabhängigen Handschriften. Keine Signifikanz, kein Sonnen-/Mondwort und insgesamt **0 bestätigte übersetzte Wörter**. f84/f84r und Reserven blieben geschlossen.

Das registrierte [METHOD.md](METHOD.md) enthält Entscheidung, festen Umfang, Nullalternative und 30-Minuten-Gesamtbudget. Die Eingangshashes in RESULT binden GDT1042s f85-Gruppen, das frühere f68-Quellpaket sowie die 179-Selektoren-Cachequellen. Reproduktion: `python3 experiments/yolo/gdt1079_f85_f68_luminary_ring_exact_overlap/src/run.py` und anschließend `python3 experiments/yolo/gdt1079_f85_f68_luminary_ring_exact_overlap/src/validate.py`; eine fehlende Wegwerf-Cache-Datei ist zuvor mit `python3 -c 'from tools.word_profiles import ensure_cache; ensure_cache(rebuild=True)'` über den selektorbewachten 179-Seiten-Vertrag wiederherzustellen.
