# GDT1170 — kein behaltenes Kontextsignal bei exakten Doppelungen

**NO_RETAINED_CONTEXT_SIGNAL.** Der registrierte Test wurde ausgeführt. Die äußeren Nachbarn von maximalen Doppelungen unterscheiden sich unter diesem Verfahren nicht ausreichend von denen vergleichbarer Einzelvorkommen. Insbesondere ist kein rechtsseitiger Anschlusswechsel gestützt. Das ist ein negativer struktureller Test, keine Wortübersetzung und kein Nachweis von Schreibfehlern.

| Lesung | Vergleichbare Doppelungen | Alle verglichenen Runs | Physische Blätter | Exakte Wortformen | Gemischte Strata |
|---|---:|---:|---:|---:|---:|
| IT2a | 154 | 701 | 53 | 58 | 141 |
| ZL3b | 124 | 523 | 48 | 50 | 115 |
| RF1b | 77 | 263 | 40 | 36 | 73 |

Verglichen wurde jeweils dasselbe exakte Wort auf demselben physischen Blatt und im selben Drittel einer Textzeile. Gezählt wurden ausschließlich die Nachbarn außerhalb der Wiederholung. Unsichere Wortformen, unsichere Abstände, Randpositionen und Dreier-/längere Runs gingen nicht in den Vergleich ein. Die vollständigen Aufstellungen stehen in RUNS.tsv und LONGER_RUNS.json. Die drei Lesungen sind keine unabhängigen Handschriften.

Alle drei Kanäle hatten die vorab verlangte nominelle Kapazität. Für IT2a/ZL3b lagen die standardisierten rechten Scores bei +0,33/-0,41 gegenüber den konditionalen Umverteilungen; rechts-minus-links bei -0,87/-1,62. Keine der drei gemeinsam kalibrierten Statistiken erfüllte die registrierte Auswahlregel in beiden Hauptlesungen. Die vollständigen 1.999 Umverteilungen je Lesung sind gespeichert. Die Kalibrierung umfasst nur die drei festgelegten Statistiken, nicht die gesamte frühere Forschungssuche; daraus wird keine Signifikanzbehauptung abgeleitet.

## Konsequenz für Lesungen

Eine Satzwiederaufnahme speziell anhand eines geänderten rechten Nachbarn wird durch diesen Versuch nicht weiter gestützt. Kontextneutrale Verdopplung bleibt als enger Vergleichsmechanismus offen. Daraus folgt ausdrücklich KEINE Erlaubnis, Wörter zu löschen, alle Wiederholungen zu Schreibfehlern zu erklären oder beliebige Funktionswortlesungen zu retten. Das Verfahren prüft einen Formähnlichkeitskern und kann semantisch unterschiedliche Nachbarn mit ähnlicher Form übersehen. Es prüft weder natürliche Sprachsyntax noch eine Übersetzung.

Der Nulltest setzt konditionale Austauschbarkeit voraus; lokale Schreibbedingungen jenseits von Blatt, Wort und Position sind nicht vollständig kontrolliert. Zweierstrata können trotz beweglicher Labels beim quadratischen Score invariant bleiben; die unabhängige Validierung berichtet daher zusätzlich die tatsächlich variationsfähige Kapazität: 103/141 Strata in IT2a, 85/115 in ZL3b und 43/73 in RF1b. Für den Rechts-minus-links-Vergleich tragen darin 116/94/47 Doppelungen zur Variation bei. Alle 30 Prüfungen einschließlich unabhängiger Rekonstruktion sämtlicher Umverteilungen sind bestanden; dies validiert die Berechnung, nicht die Austauschbarkeitsannahme oder eine Bedeutung. Nominelle Blattzahlen sind keine Zahl unabhängiger Bedeutungsbestätigungen.

## Daten und Reproduktion

179 bereits bekannte Textselektoren, keine neuen Bilder oder Seiten. Sealed f84/f84r und nicht zugelassenes f116v wurden nicht geöffnet. Keine Reserve wurde als Bestätigung genutzt; unabhängige Bestätigungskapazität 0. Die guarded Projektion, Quell-Hash und Aufnahmezeit sind in GUARD.json gebunden, die vorangehende lokale Registrierung in REGISTRATION_LOCK.json. Keine ältere Methode oder Transkription verändert.

Vorgänger: GDT820 stellt bereits klar, dass Wiederholung allein keine Wortart festlegt; GDT574 rendert übernommene Aktionsrollen, GDT803 prüft l/m-Umgebungen und GDT910 lokale Kurz-/Langalternativen. Keiner wird durch diesen Versuch ersetzt. IDEA924 wurde als roher Vorschlag vor Aufnahme festgehalten.

Reproduktion: `python experiments/yolo/gdt1170_repetition_context_neutral_copy/src/run.py --cached`; unabhängige Prüfung: `python experiments/yolo/gdt1170_repetition_context_neutral_copy/src/validate.py`. Das Ergebnis bleibt lokal; kein GitHub-Push dieses negativen Zwischenstands.
