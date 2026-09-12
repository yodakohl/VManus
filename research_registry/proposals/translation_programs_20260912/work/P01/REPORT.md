# P01 — ähnliche Befunde, gemeinsame Entscheidungsregel?

2026-09-12. **Zwei konkrete Befund→Maßnahme-Ketten passen zur verfassten Regel; dieselbe Regel widerspricht zwei anderen Maßnahmen und begründet vier weitere nicht. Die Diagnosefassung wird deshalb nicht ausgewählt.** Keine medizinische oder historische Therapiebehauptung; geprüft wird eine hypothetische Textlesung.

Alle vier HERB4-Absätze sind in [Diagnosefassung D](READING_D.md) und [Zustandsbeschreibung R](READING_R.md) vollständig ausgerichtet: je 145 Gruppen, 41 Positionen mit zwölf Ganzwortannahmen und 104 offen. [CHAPTER.md](CHAPTER.md) formuliert alle vier Fallgeschichten, den gemeinsamen Entscheidungsbaum und die ebenso vollständige Gegenbeschreibung.

## Vorher festgelegte Begriffe

Sechs Befundwörter: cthy=Schwellung, chor=Schmerz, shor=Absonderung, chol=Trockenheit, shol=Feuchtigkeit, shey=Hitze. Drei symbolische Gradformen: dair=A, dain=B, daiin=C. D liest sho=Benetzen, chkaiin=Trocknen, qotchy=Kühlen; R liest dieselben drei Formen als benetzt/getrocknet/gekühlt. Keine pro Stelle wechselnden Glossen.

Gemeinsame Entscheidungsannahme: vorher genannte Hitze hat Vorrang und verlangt im Modell Kühlen; sonst führt die zuletzt genannte Feuchtigkeit zu Trocknen beziehungsweise Trockenheit zu Benetzen. Ohne solchen Vorbefund bleibt der Grund offen. Schwellung/Schmerz/Absonderung verändern in dieser Version keinen Entscheidungszweig; die Glossen haben daher noch keine differentialdiagnostische Leistung. Aus ungenannten Befunden wird keine negative Beobachtung. Kein Behandlungserfolg wird automatisch angenommen.

## Sämtliche Maßnahmen, rückwärts geprüft

| Stelle | angenommene Maßnahme | vorheriger entscheidender Beleg | Ergebnis |
|---|---|---|---|
| f21r.9:2 sho | Benetzen | keiner | unbegründet im kleinen Modell |
| f21r.9:4 chkaiin | Trocknen | keiner | unbegründet |
| f21r.12:8 chkaiin | Trocknen | shey .11:7: Hitze | Regel erwartet Kühlen: Widerspruch |
| f32v.9:1 qotchy | Kühlen | keiner | unbegründet |
| f32v.10:1 sho | Benetzen | keiner | unbegründet |
| f32v.11:2 sho | Benetzen | chol .10:4: Trockenheit | bedingt passend |
| f29v.3:6 qotchy | Kühlen | shey .3:4: Hitze | bedingt passend |
| f29v.4:8 sho | Benetzen | weiterhin shey .3:4 | Regel erwartet Kühlen: Widerspruch |

[ALL_DECISIONS.tsv](ALL_DECISIONS.tsv) enthält zusätzlich für jede Position das gesamte zuvor bekannte Register, die gebundenen Grade und den abgeleiteten Diagnoseschluss. Die Diagnosenamen 'Hitze-betont' usw. sind Rechenergebnisse des entworfenen Baums, keine übersetzten Manuskriptwörter. Die zwei passenden Fälle sind weder unabhängige Bedeutungstests noch ein Erfolgsanteil.

**Konkreter Entscheidungsvergleich:** f29v.3:6 und f29v.4:8 haben dasselbe nichtleere Register der gewählten Befunde/Grade, aber unterschiedliche angenommene Maßnahmen. Eine zusätzliche Bedingung oder ein beschriebener Behandlungserfolg könnte das erklären, wurde jedoch nicht gelesen. Ein stilles Zurücksetzen der Hitze nach dem ersten Kühlen wäre eine Modellreparatur, keine geprüfte Konsequenz.

Alle 28 Paare der acht Maßnahmen sind in [ALL_CASE_PAIRS.tsv](ALL_CASE_PAIRS.tsv) enthalten. Sechs Paare besitzen ein leeres Register; das bedeutet fehlende Angaben, keine Gleichheit vollständiger klinischer Befunde. Der eine nichtleere Paarwiderspruch ist abhängig vom bereits tabellierten späten f29v-Einzelfall, keine zusätzliche unabhängige Widerlegung.

## Resttext und Gegenfassung

23 Befundvorkommen, zehn Gradpositionen. Nur zwei daiin binden unmittelbar an einen Befund: chol auf f21r.12 und f32v.10. Acht Grade bleiben ungebunden, darunter das daiin-Doppel. [FINDINGS.tsv](FINDINGS.tsv), [GRADES.tsv](GRADES.tsv) und [RECORD_COVERAGE.tsv](RECORD_COVERAGE.tsv) decken alles ab. f17r besitzt Befunde, aber keine der drei Maßnahmen; der fehlende Schluss wird nicht erfunden.

R beschreibt dieselben Befunde und Benetzungs-/Trocknungs-/Kühlzustände, ohne eine ursächliche Maßnahmenentscheidung zu beanspruchen. Sie vermeidet dadurch die falschen Entscheidungsbehauptungen, erklärt aber weder die Zeitfolge noch die offenen Wörter. Die Aktualisierung feucht→trocken→feucht bleibt eine globale Verlaufsannahme, kein gelesener Prozess. Das Bild liefert keinen Patienten oder eine Diagnose.

## Entscheidung und Grenzen

**Die feste D-Regel zurückstellen; R als partielle Darstellung beibehalten.** Das widerlegt weder Diagnosekapitel allgemein noch eine Sprache. Es bestätigt aber auch kein Symptom, keinen Grad und kein Behandlungsverb. Keine nachträgliche Prioritätsumkehr, neue Krankheit, Erfolgsannahme oder Sonderbedeutung wird zum Ausgleich eingesetzt.

[DECISION.md](DECISION.md) wurde vor Ausführung geschrieben. f17r/f21r dienten zur Entwicklung, f32v/f29v zur gleichen Anwendung auf schon exponiertes Material. GDT809s Primärbericht/Absatzdarstellung und seine Transkriptionshinweise bleiben unverändert; P11s abgegrenzte Quellprojektion wurde übernommen, nicht dessen Glossen. Kein neuer Dreilesartenabgleich. Keine Reserveseiten, neuen Bilder oder Kontakte; f84/f84r geschlossen. Keine Signifikanzbehauptung, unabhängige Bedeutungsbestätigung null, keine Bild-Text-Kante.

Reproduktion: `python3 research_registry/proposals/translation_programs_20260912/work/P01/build.py`, dann `python3 research_registry/proposals/translation_programs_20260912/work/P01/validate.py`. Rückleseprüfung kontrolliert Quellhash, beide ganzen Gruppensequenzen, alle acht rückwärts gebundenen Gründe, alle 28 Paare und jede gebundene Gradposition; keine Diagnose- oder Bedeutungsvalidierung.

Nächster Kandidat zur Auswahlprüfung: P07, Körperweg-Anleitung gegenüber Werkstattstationen, mit ganzen Handlungsketten und stabilen Ortsrollen. Kein weiterer automatischer Umbau der gescheiterten P01-Priorität.
