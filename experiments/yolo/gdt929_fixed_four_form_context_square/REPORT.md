# GDT929 — kontrollierter Vergleich cheey/lcheey/sheey/lsheey

**Alle vier Formen sind belegt; drei feste unmittelbare Umgebungen tragen sowohl `cheey` als auch `sheey` auf verschiedenen Blättern. Keine Umgebung trägt im festen Test ein l-Paar oder alle vier Formen.** Das trennt den beobachteten ch/sh-Wechsel von dem bisher damit vermischten l-Zusatz. Es identifiziert noch keine Bedeutung.

## Vollständiger Zensus

| Transkription | cheey | lcheey | sheey | lsheey | geprüfte Gruppen insgesamt |
|---|---:|---:|---:|---:|---:|
| ZL3b |153|13|126|6|32363|
| IT2a |150|13|128|8|31875|
| RF1b |148|12|111|6|31946|

874 genaue Vorkommen, davon 719 mit zulässigem unmittelbarem Links-/Rechtsrahmen. Alle Vorkommen einschließlich fehlender/unsicherer Rahmen stehen mit vollständiger Zeile und Quellen-ID in artifacts/OCCURRENCES.json. Die Transkriptionen sind Lesungen eines Manuskripts; ihre Zahlen werden nicht als unabhängige Beobachtungen interpretiert.

## Alle gemeinsamen Rahmen

| Rahmen | cheey | sheey | Zulässige Lesungen | Grund des fehlenden dritten Lesungsbelegs |
|---|---|---|---|---|
| ar … or | f103v.23 | f112v.3 | ZL3b, IT2a | RF1b f112v.3 hat unsichere Rohformen `shee@222;` und `@221;r`. |
| ol … qokain | f79r.7 | f75v.40 | IT2a, RF1b | ZL3b enthält die Formen, aber der Rahmen erfüllt die feste Abstandsprüfung nicht. |
| sol … qokaiin | f83r.2 | f80v.10 | IT2a, RF1b | ZL3b enthält die Formen, aber der Rahmen erfüllt die feste Abstandsprüfung nicht. |

Sechs Lesungs-/Rahmenfälle entsprechen drei unterschiedlichen Rahmen auf sechs physischen Blättern. Kein Rahmen ist nach den festen Kriterien in allen drei Transkriptionen zulässig. Die Lesungsunterschiede werden nicht normalisiert. FRAMES.json enthält sämtliche Belege; HIT_LOCUS_READINGS.json enthält alle drei vollständigen Lesungen aller sechs betroffenen Zeilen als nach dem Zensus erzeugte Diagnose.

| Vorab festgelegter Vergleich | Gemeinsame zulässige Rahmen |
|---|---:|
| cheey / lcheey |0|
| sheey / lsheey |0|
| cheey / sheey |3 verschiedene, 6 Lesungsfälle|
| lcheey / lsheey |0|
| Alle vier im selben Rahmen |0|

## Inhaltliche Konsequenz

Die beiden unpräfigierten Formen können in mindestens drei exakt gleichen unmittelbaren Wortumgebungen stehen. Das ist mit verwandten Funktionen, unterschiedlichen Zuständen oder alternativen Schreibungen vereinbar. Es beweist weder gleiche Bedeutung noch eine bestimmte grammatische Kategorie. Insbesondere ist die bisher gesetzte Gleichsetzung beider Formen mit Bade-/Benetzungsfunktionen dadurch nicht bestätigt.

Für die Körper-/Stationsfrage ergibt sich kein gebundener Unterschied. lcheey und lsheey sind tatsächlich vorhanden, also keine bloß erfundenen fehlenden Paradigmenzellen. Aber der verlangte Kontextvergleich isoliert hier keinen l-Effekt. **Den ch/sh-Kontextbefund behalten; keine Bedeutung von l und kein vollständiges Viererparadigma aus ihm ableiten.** Keine automatische Vergrößerung der Fenster oder neue Glossen, um einen Treffer zu erzeugen. Eine vollständige semantische Absatzlesung ist nicht Gegenstand dieser Strukturprüfung.

## Abgrenzung und Reproduktion

2026-09-14. Fester Test nach W55, kein Decoder. PREREGISTRATION/METHOD/SPEC/run.py wurden vor dem neuen Cachezensus lokal hashgebunden; keine Behauptung einer vorab öffentlich veröffentlichten Registrierung. Die gesamte Textbasis und zahlreiche Formen waren im Projekt bereits exponiert. GDT914 untersuchte vier direkt aufeinanderfolgende Wörter; GDT929 dagegen genau vier vorab benannte Formen mit identischen unmittelbaren Nachbarn auch über Blattgrenzen hinweg. Frühere Wörterbuch- und Kontextarbeiten wurden als Vorgänger erkannt, nicht als Bedeutungsbelege übernommen; kein Anspruch auf Neuheit allgemeiner Kontextvergleiche.

Ausschließlich sechs unveränderte GDT915-Snapshots mit179bereits erlaubten Textselektoren verwendet. Alte DISCOVERY/EVALUATION-Dateinamen erzeugen hier keinen zurückgehaltenen Bestätigungssatz. Keine neuen Bilder oder Reservetexte, f84/f84r geschlossen. Kein Signifikanzanspruch ohne Kontrolle der gesamten Suche. Keine Pflanzennamen oder sonstigen Wörter bestätigt; kein scorefähiges Relationspacket.

Der getrennte Validator rekonstruiert alle Vorkommen, Rahmen, Vergleiche und Nenner vollständig aus den Quellsnapshots und prüft die Registrierungsbytes: PASS. Er prüft keine Bedeutungswahrheit. Reproduktion über die in experiment.json eingetragenen run/validate-Befehle.

Repositoryprüfung: sieben bekannte GDT600-Altfehler bleiben; der für GDT929 aktualisierte Experimentindex ist aktuell. Eigener Validator und Registerprüfung PASS.
