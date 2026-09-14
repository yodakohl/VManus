# GDT942 — native Prüfung der Listen-/Gesamtzahlbindung

DECISION.md und PREREGISTRATION.md fixieren Frage, Aufnahme, Scope, Beobachtungs-
felder und Entscheidung. Die neue Bildzulassung ist in src/PAGE_ADMISSIONS.tsv
gebunden. Root inspiziert Ganzseite und vollständigen Absatz und schreibt ein
unveränderlich auswertbares Beobachtungspaket mit konkreten Pixelbereichen.

src/run.py bindet Quelle, Verlustfrei-Ausschnitte und das menschlich lesbare
Beobachtungspaket an die vorab festgelegte Entscheidungsregel. src/validate.py
prüft die Bildquelle/Abmessungen, Pixelidentität jedes Ausschnitts, alle110alten
Quellgruppen, vollständige Beobachtungsfelder und die berechnete Entscheidung.
Kein Test bestätigt Zahlen, Übersetzungen oder die Richtigkeit nativer Eindrücke.
