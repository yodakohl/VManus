# Begrenzter Kontext für weitere 1000 Versuche

2026-09-14. Expliziter Nutzerauftrag zur Skalierung der Arbeitsweise bei begrenztem Kontext. Keine Entzifferungsarbeit und keine neue Seite.

Primäre Vorgänger: aktuelle Route, Wissenseinstieg, Live-Leitfaden, die drei Dokumentationsaudits, tools/work_cli.py und die bestehende Register-/Kontext-Testarchitektur. Die Registersuche ist bereits paginiert; tests/test_semantic_ideas_context.py besitzt einen 10000-Karten-Test. Ein weiterer Registerimport oder eine neue Wissensdatenbank wäre unnötig. Der bisherige Starttest erwartet dagegen überholte Route-Texte und große Grenzen; das wird am aktuellen Vertrag berichtigt, nicht als neuer Manuskriptbefund gewertet.

Offen: ein erzwungen begrenzter Wiedereinstieg, genaue Übergabefelder und direkter Abruf einschlägiger Dokumentausschnitte ohne Lesen ganzer Leitfäden. Die bisher verpflichtende Route plus Wissenseinstieg umfasst 15346 UTF-8-Bytes. Das ist keine Messung von Modell-Tokens oder gesamtem Gesprächskontext.

Kleinster angemessener Eingriff: additive context-Befehle in vmanus-work, Implementierung in neuem Modul; kleine Navigationsdefinitionen ohne eigene wissenschaftliche Zusammenfassungen; Ausschnitte aus vorhandenen Live-Dokumenten. Start maximal4096Bytes, Thema maximal6000Bytes, Themenliste paginiert. Keine Rohdaten, kein Verfolgen von Berichtlinks, keine Schreiboperation des Abrufbefehls. Geänderte oder fehlende Gliederung muss sichtbar scheitern, nicht still gekürzt werden. Die Route bleibt einzige aktuelle Arbeitsübergabe; bestehende Register und Primärberichte bleiben maßgeblich.

Felder der Übergabe: Phase, Status, Auftrag, zuletzt geänderte Entscheidung, Arbeitsdateien/Annahmen, nächster konkreter Schritt, laufende Arbeit. Vor Kontextwechsel und nach materieller Entscheidung ersetzen. Bei abgeschlossenem Wartungsauftrag keine Forschungsroute automatisch auswählen. Pro Experiment Erkenntnis und Entscheidung im vorhandenen Dossier/Register speichern, nicht in der Route aufsummieren; keine pauschale Rückmigration aller Altversuche.

Prüfung: echte Navigation und Fehlerfälle, Ausgabegrenzen, fehlende/eindeutige Abschnitte, Pfad-/Quelldisziplin und unveränderter Start nach1000zusätzlichen künstlichen Versuchseinträgen. Bestehenden10000-Karten-Test gezielt mitprüfen. Dies misst Kontext-/Abrufverhalten, keine Forschungsqualität oder benötigte Versuchszahl.

Kontrollpunkt: etwa50Minuten einschließlich Vorbereitung, Implementierung, Tests und Veröffentlichung. Falls Ausgaben wachsen oder Quellgrenzen nicht halten, den Helfer korrigieren/verkleinern statt eine neue Infrastrukturkette anzuschließen. GDT001–336, vmanus-exp, alte Berichte/Experimente bleiben unverändert. Keine Kontakte; f84/f84r und Reserven geschlossen.
