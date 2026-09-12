# P10 — Lehrdialog tatsächlich ausgearbeitet, Begründung bleibt offen

Zwei vollständige exponierte Absätze wurden mit einer gemeinsamen Gesprächsregel
ausgerichtet und sachlich gelesen. Der konkrete Entwurf unterscheidet Pflanzenqualität
und Wirkung einer Mischung. **Er liefert noch keinen Grund, den Dialog gegenüber
einer beschreibenden Fassung zu bevorzugen.** Das ist ein Ergebnis dieses Entwurfs,
keine Widerlegung der Textgattung und keine bestätigte Übersetzung.

[Die beiden Gesprächslesungen und ihre volle Gegenfassung](READING.md) enthalten
den tatsächlichen Inhalt, seine Annahmen und die offenen Schlussfolgerungen.
[Die Entscheidung vor der Ausarbeitung](DECISION.md) legt Umfang und Rollen fest.
Es wurde kein neuer Decoder und kein neues registriertes GDT-Experiment angelegt;
die Ausgangsprogramme und GDT809/918/925 bleiben unverändert.

| Fassung | Konkrete Annahme | Ausgerichtete Positionen | Davon hypothetisch / offen | Ergebnis |
|---|---|---:|---:|---|
| [D0](RENDERED_v01.md) | qotaiin/shey = warum; qotchy = Antwort; 24 ganze Werte | 79 | 45 / 34 | Je eine Frage vor einer Antwort; Sachgründe noch weitgehend ungelöst |
| [D1](RENDERED_v02.md) | Neun zusätzliche Werte: Eigenart, Mischung, Wirkung und Teilqualitäten | 79 | 55 / 24 | Formulierbares Lehrkonzept; kalt bzw. abweichender Grad werden nicht hergeleitet |
| [R1](RENDERED_rival_v01.md) | Identische 30 Inhaltswerte und Lücken, drei Marker als Thema/Zusatz | 79 | 55 / 24 | Dieselben Qualitätsangaben ohne Sprecher möglich; ebenfalls unvollständig |

Die Zahlen zählen manuelle Annahmen, keine Übersetzungsgenauigkeit. Die volle
Kandidatenzuweisung ist in den drei ALIGNMENT- und LEXICON-TSV-Dateien erhalten.

| Absatz | Vorher festgelegte Konsequenz | Beobachtetes Textgerüst | Sachlicher Befund / Widerspruch / Mehrdeutigkeit |
|---|---|---|---|
| f32v.7–11 | qotaiin-Frage muss durch folgende qotchy-Passage sachlich beantwortet werden | qotaiin otchy d shan → qotchy cfhy skey chocthy daiin cthaiin daiin … | „Warum kalt?“ → „Eigenart bestimmt …“ liefert keine Kälteableitung. Trocken/kalt ist kein Widerspruch. Zwei Γ-Anteile bestimmen ohne Qualitätsachse keine Wirkung. |
| f29v.1–4 | shey-Frage muss durch folgende qotchy-Passage einen zuvor genannten Sachverhalt erklären | shey odaiin → qotchy taiin s she otey sy … otshy okaiin cthy oltchy … | „Warum abweichender Grad?“ → „Mischung und Eigenart bestimmen Wirkung“ benennt weder Vergleichsgrad noch Mischungsbeitrag. Kalt-feuchte Zubereitung versus kalt-trockenes Kraut ist ein konkreter hypothetischer Unterschied, keine erklärte Umwandlung. |

[MARKERS.tsv](MARKERS.tsv) enthält alle vier Markervorkommen, [SEGMENTS.json](SEGMENTS.json)
alle sechs Segmente. Rein nach Reihenfolge: zwei zugeordnete Fragen, null Fragen
ohne nachfolgenden Antwortmarker, null Antworten ohne Frage. Inhaltlich: zwei
nicht gelöste Fragen, null etablierte Begründungen. Die Rollenregel benutzt zwei
verschiedene Frageformen mit demselben Wert; das ist ausdrücklich Modellfreiheit.

[REPETITIONS.tsv](REPETITIONS.tsv) enthält alle innerhalb eines Absatzes wiederholten
Formen. Keine überquert unter der festgelegten Regel einen Sprecherwechsel.
[UPTAKE.json](UPTAKE.json) zeigt die vollständigen exakten Schnittmengen:
keine Frage teilt eine ganze Gruppe mit ihrer Anfangsaussage oder Antwort.
Die Lehrerpassagen teilen daiin auf f32v sowie cthy/s auf f29v. Wiederholte
Behauptungsgegenstände sind damit nicht identifiziert. Freie Paraphrase bleibt
möglich; der Test verlangt nicht nachträglich exakte Sätze. Die auffälligen
Verdoppelungen werden vom Dialog nicht als Sprecher-Echo erklärt.

## Datenabgrenzung und Kontrollen

Beide Blätter sind aus GDT809 und den bisherigen P09/P05-Arbeiten exponiert.
Die Markerauswahl nutzt bekannte P09-Spannen. Keine frische Verblindung, keine
Signifikanz, keine unabhängige Bedeutungsprüfung; Bestätigungskapazität **0**.
Kein neuer Quellen- oder Manuskriptzugriff außerhalb der angegebenen lokalen
Artefakte. f84/f84r und alle reservierten Seiten bleiben geschlossen.

Die Darstellung ist ZL-gerahmt. Insbesondere ist das erste chol-chol auf f29v.2
bei IT anders segmentiert (`schol chol`); bei f32v.8 hat RF `cthodaiin` statt
`ctho daiin`. Diese Unterschiede werden weder normalisiert noch als zusätzliche
Manuskripte gezählt. Ganze alternative Absatzlesungen wurden hier nicht erneut
getestet. D1 behauptet daher nicht, lesungsrobust zu sein.

`python3 research_registry/proposals/translation_programs_20260912/work/P10/build.py`
reproduziert Quellbindung, alle Ausrichtungen, Wiederholungen und Markerinventare.
[VALIDATION.json](VALIDATION.json) prüft Quellen-/Modelltreue; es ist kein unabhängiger
semantischer Test. Es wurde keine scorefähige Relationsevidenz eingereicht und
kein GDT388-Bedeutungs-/Bildbezug beansprucht.

## Entscheidung

Erster P10-Ausarbeitungsdurchgang beendet, Gesamtlesung weiterhin partiell.
Keine zusätzlichen Gesprächswechsel zur Rettung der Verdoppelungen, keine
nachgeschobenen Einzelbedeutungen als Beweis. P05 bleibt der frühere vorläufige
Herstellungskandidat, nicht durch P10 bestätigt. Nächster eigenständiger Ansatz
der bestehenden Reihenfolge: P28. Bestätigte Wörter weiterhin **0**.

Der parallel beauftragte Ideenlieferant schlug eine spätere P10-Variante an
f21r.8–12 mit festem Aussagegegenstand vor; sie wurde hier nicht ausgeführt und
nicht als neue Karte dupliziert. Sie würde einen anderen expliziten Entwurf
benötigen, insbesondere geschriebene Träger der Sprecherwechsel. Keine Kontakte.
