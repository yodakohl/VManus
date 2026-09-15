# GDT963 — Vier vollständige Dioskurides-Texte: Suche unentschieden

**Entscheidung: BOUNDED_SEARCH_UNRESOLVED.** Es wurde kein vollständiger Code und keine Lesung gefunden. Der begrenzte Solverlauf widerlegt das Gesamtmodell ebenfalls nicht. Der Ansatz wird ohne automatische Verlängerung oder Reparatur zurückgestellt.

## Vorhersage und vollständige Prüfung

Vor dem Fit öffentlich registriert in Commit `10a7ba761`: Die vollständigen Quellabschnitte I.1 Iris, I.2 Acorus, I.3 Meum und IV.20 Xiphion müssen mit einem gemeinsamen, injektiven, nichtleeren präfixfreien Inhaltscode auf vier vollständige Kräuterseiten auf vier verschiedenen physischen Blättern passen. Die gedruckte griechische Wortfolge bleibt erhalten; die begrenzte Aliasliste und alle übrigen lexikalischen Atome waren eingefroren. Das setzt keine identifizierte griechische oder lateinische Voynich-Basis voraus.

[PREDICTIONS.tsv](artifacts/PREDICTIONS.tsv) enthält alle 604 Quellwörter und ihre 613 Atomfolgen vor dem Fit. Unter 333 verschiedenen Atomen sind 255 globale Einzelvorkommen. Das lässt viele frei zuzuordnende Werte; selbst ein Fit wäre keine unabhängige Bedeutungsprüfung.

[CANDIDATE_TABLE.tsv](artifacts/CANDIDATE_TABLE.tsv) enthält alle 1.428 Kombinationen aus vier Quellrollen und 357 vollständigen Seitenrahmen. Keine passende Einzelstelle wurde ausgewählt. [ALL_LOCAL_CASES.json.gz](artifacts/ALL_LOCAL_CASES.json.gz) enthält die vollständigen Maschinenbelege; [IDENTICAL_TARGET_STRINGS.json](artifacts/IDENTICAL_TARGET_STRINGS.json) gruppiert identische Zielzeichenfolgen, deren Identitäten dieser Test nicht unterscheiden kann.

| Lokale Konsequenz | Fälle | Interpretation |
|---|---:|---|
| UNKNOWN_SOURCE | 1.016 | Ganze Seite nicht vollständig literal verfügbar; keine Ergänzung erfunden |
| CONTRADICTED_LENGTH_BOUND | 71 | Notwendige Präfixcode-Längenschranke verletzt |
| UNKNOWN_SOLVER | 262 | Innerhalb der festen Rechenzeit unentschieden |
| UNKNOWN_WALL_CEILING | 79 | Prozesszeitgrenze erreicht; kein Widerspruch |
| Gefundener lokaler Code | 0 | Kein Zeuge zur Bedeutungszuordnung |

Von 357 Rahmen sind 103 literal verwendbar: ZL3b 0, IT2a 101 auf 58 physischen Blättern, RF1b 2. Für die gemeinsame Vier-Blatt-Prüfung haben ZL3b und RF1b keine Kapazität. IT2a behält nach notwendigen lokalen Schranken 33/101/101/100 Seiten für die vier Rollen; die gemeinsame 600-Sekunden-Suche endet **UNKNOWN_SOLVER**. [JOINT_RESULTS.json](artifacts/JOINT_RESULTS.json) und [RESULT.json](artifacts/RESULT.json) dokumentieren die Ergebnisse.

## Datenabgrenzung, Mehrdeutigkeit und Validierung

Alle sechs eingefrorenen GDT915-Caches wurden nach der registrierten Ganzseitenregel berücksichtigt. f1r war ausgeschlossen. Unklare Zeichen oder Grenzen bleiben unbekannt. Transkriptionen sind alternative Lesungen desselben Manuskripts. Sämtliche verwendeten Blätter waren zuvor im Projekt exponiert und gehören hier zur Kandidatenauswahl. Unabhängige Bestätigungskapazität: **0 Blätter**. f84/f84r und weitere Reserven blieben geschlossen.

Der separate Validator prüft die Quellprojektion, alle 22 Registrierungsbindungen, die vollständige Zielaufnahme, jede Fallzeile, die Längenschranken und die Statusaggregation. Ergebnis: **VALIDATION_PASS**. Synthetische SAT/UNSAT-Kontrollen prüfen nur die Implementierung. Es gibt keinen gefundenen Manuskriptcode zur Zeugenprüfung und keine geeignete Gegenkontrolle der gesamten Suche. Daher keine Signifikanzbehauptung und **0 bestätigte Wörter**.

Das Ergebnis verändert keine alten Befunde: 71 unmögliche Seitenzuordnungen sind keine Entzifferung; 341 zeitlich unentschiedene lokale Fälle sind keine gestützten Lesungen. Neue Arbeit an diesem Modell benötigt einen eigenständigen vorab festgelegten Entscheider und eine begründete Gesamtzeitgrenze. Zusätzliche Laufzeit allein ist derzeit nicht die bevorzugte Forschungsroute.
