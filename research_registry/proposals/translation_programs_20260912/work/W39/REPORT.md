# W39 — Die sieben f83r-Records als mögliche Vergleichsfälle

**Zwei Record-Paare unterscheiden sich in der angesetzten Ablaufsequenz nur durch einen expliziten Eingriff. Keines trägt einen vollständigen Vergleich mit gleichem Ausgang und nachfolgendem Befund.** Der Vergleichsbericht bleibt deshalb eine offene Inhaltsidee; er liefert in diesem Test keine Kausalwirkung und keine neue Wortbedeutung.

Das ist ein anderer Ansatz als die letzten W-Versuche: ganze Records als getrennte Fälle vergleichen, statt Wortetiketten, Materialidentitäten oder Satzgrenzen weiter anzupassen. Ausgeführt wurde die vorhandene RAW-Karte **IDEA000192**, nach Prüfung der Primärberichte P01, P06, P12 und P15. Diese alten Versuche und die lokale W38-Eigenschaftsklassen-Lesung bleiben unverändert.

## Vorfestlegung und Datenabgrenzung

[DECISION.md](DECISION.md) und [SPEC.json](SPEC.json) wurden vor Ausführung gespeichert. Alle **sieben bereits früher exponierten f83r-Records, 51 Zeilen, 341 Gruppen**, sämtliche **21 ungeordneten Record-Paare**. Keine Wahl eines günstigen ersten Zweierpaares. Nur die gebundene, zuvor publizierte P12/P15-Projektion wurde gelesen; keine neue Bild-, Leser- oder Reserveseitenöffnung. f84/f84r bleiben geschlossen.

Das feste Achtwortlexikon und die Materialbezüge kommen aus P15-R: shedy≈Flüssigkeit A, lchedy≈Zusatzstoff C, qokaiin≈Gefäß B; chedy≈erwärme, qokeedy≈fülle ein, qokeey≈laufendes Einfüllen, qokedy≈ist eingefüllt, qoteedy≈erneutes Einfüllen. Alles bleibt **unbestätigte Ganzwortannahme**. Keine Wortwerte von W38 wurden in dieses andere Paket übertragen.

P15-I bleibt die gespeicherte Herstellungsrivalin: Dort ist qokedy ein Abschlussbefehl, kein berichteter Endzustand. W39 erfindet in dieser Fassung keine beobachteten Ergebnisse. Die Unterschiede zwischen P15-R und P15-I werden nicht als neue Befunde ausgegeben.

## Was genau als möglicher Vergleich galt

Der Ausgangsproxy ist die geordnete erste Nennung der drei Teilnehmerklassen vor der ersten Nicht-STATE-Meldung. Ein leerer Proxy ist fehlende Information. Auch zwei gleiche, nichtleere Proxys würden weder gleiche Ausgangsmenge noch gleiche Eigenschaften, konkrete Charge oder Gefäßidentität beweisen. Die offenen Gruppen davor werden mitgezählt.

Die vollständige Eingriffs-/Verlaufsfolge enthält jeden Nicht-STATE-Eintrag als `(Art, Patient, Ziel)`, einschließlich unvollständiger Meldungen sowie RUNNING/REPEAT. Ein möglicher Unterschied muss genau eine Einfügung, Entfernung oder Ersetzung betreffen; die abweichende Stelle muss ein explizites HEAT oder DIRECT sein. Alle anderen Tripel müssen übereinstimmen. Sämtliche möglichen Ein-Schritt-Ausrichtungen wurden erfasst; keine günstigste ausgewählt.

Ein Endbefund muss ausdrücklich als gebundenes qokedy-STATE **nach der letzten Nicht-STATE-Meldung** im eigenen Record stehen. Frühere Zustandsangaben, auf die noch weitere Handlungen oder Verlaufsmeldungen folgen, werden nicht zu Endergebnissen umgedeutet. Alle 13 vorhandenen STATE-Stellen stehen in [ALL_STATES.tsv](ALL_STATES.tsv), einschließlich ihrer tatsächlichen Position und Bindung.

## Alle sieben Fälle

| Record | Gruppen | Ausgangsproxy | Offene Gruppen vor erster Meldung | Nicht-STATE-Meldungen | Spätere gebundene Endbefunde |
|---|---:|---|---:|---:|---:|
| P1 | 72 | A, B | 11 | 11 | 0 |
| P2 | 84 | A, B, C | 44 | 2 | 0 |
| P3 | 63 | A, C | 17 | 6 | 0 |
| P4 | 33 | fehlt | 0 | 7 | 0 |
| P5 | 62 | C, A | 48 | 2 | 0 |
| Q1 | 11 | fehlt | 10 | 1 | 0 |
| Q2 | 16 | fehlt | 16 | 0 | 0 |

P4s Null bedeutet, dass die erste Meldung sofort einsetzt, nicht dass sein Ausgang vollständig bekannt wäre. In Q2 gibt es keine Nicht-STATE-Meldung; seine fehlende Behandlung ist keine gelesene unbehandelte Kontrolle.

[RECORDS.tsv](RECORDS.tsv) bewahrt die vollständigen Sequenzen mit Schriftstellen, alle alten Referenz-/Zeitprobleme und sämtliche ungelesenen Wortfolgen. [READING.md](READING.md) formuliert jeden Record als möglichen Fall und erhält **alle 341 Rohgruppen samt hypothetischer Ausrichtung**. Weiterhin 72 Positionen mit alten Annahmen und 269 offen; keine neue semantische Abdeckung.

## Die beiden Beinahe-Paare

| Paar | Genau ein unterschiedlicher expliziter Eingriff | Warum kein vollständiger Vergleich entsteht |
|---|---|---|
| P2 / P5 | Die erste Meldung wechselt von „Flüssigkeit A in Gefäß B einfüllen“ zu „Zusatzstoff C erwärmen“. Die übrige angenommene Ablaufsequenz stimmt danach überein. | Bereits die Ausgangsproxies unterscheiden sich: A,B,C gegenüber C,A. Außerdem wechseln mit der Tätigkeit auch Patient und Zielrolle. Dieser Ein-Triple-Unterschied isoliert keinen einzelnen physikalischen Faktor. Kein nachfolgender gebundener Endbefund. |
| Q1 / Q2 | Q1 enthält eine zusätzliche HEAT-Meldung; Q2 keine Meldung der fünf angesetzten Ereignisarten. | Der HEAT-Patient in Q1 fehlt. Beide Ausgangsproxies sind leer, beide Records überwiegend bzw. vollständig ungelesen. Q2 ist nicht als Kontrollansatz ausgewiesen. Keine Endbefunde. |

Diese beiden Kandidaten sind im vorab festgelegten syntaktischen Ein-Schritt-Sinn enthalten, **nicht** als wissenschaftlich vergleichbare Fälle. Die übrigen 19 Paare haben keine passende Ein-Schritt-Änderung der gesamten modellierten Sequenz. Kein Paar besitzt zwei gleiche nichtleere Ausgangsproxies. Auch die vollständig aufbewahrten ungelesenen Restfolgen unterscheiden sich bei **allen 21 Paaren**; diese Wörter dürfen nicht als wirkungslos gelten.

[ALL_PAIRS.tsv](ALL_PAIRS.tsv) enthält jedes Paar mit beiden Ausgangsproxies, den vollständigen Ein-Schritt-Zeugen, vorhandenen oder fehlenden Endbefunden, offenen Unterschieden und Bestätigungskapazität 0. Die Null an fehlenden Endpunkten ist keine Beobachtung gleicher Wirkung. Der feste R-Wortwert qokedy benennt ohnehin nur „eingefüllt“; er würde ohne weitere Befundwerte noch keinen Temperatur- oder Wirksamkeitsunterschied ausdrücken.

## Entscheidung

**Unter dem eingefrorenen P15-Achtwortlexikon keinen gepaarten Wirkungsvergleich auswählen.** Es fehlen nicht lediglich mehr Rechenvarianten: Die gelesenen Ausgangsfelder unterscheiden sich, die schmalen Vergleichspaare sind unvollständig oder konfundiert, und es fehlt jeder nachgeschaltete gebundene Endbefund nach der vollständigen Verlaufsfolge.

Die allgemeine Möglichkeit vergleichender Aufzeichnungen ist damit nicht widerlegt. Eine Wiederaufnahme braucht zusätzliche konkret begründete Ausgangs-/Befundlesungen oder einen anderen vorab erklärten Inhaltsvertrag. Kein bloß gelockerter Abstand, kein herausgeschnittener kurzer Abschnitt und keine Umdeutung fehlender Angaben zu negativen Beobachtungen. Die P15-Herstellungs-/Zustandsrivalen bleiben unverändert, einschließlich ihrer eigenen bekannten Fehler; ihr Bestehen folgt nicht aus dem fehlenden Vergleichspaar.

Dieser Durchgang ergänzt eine nachvollziehbare vollständige Paarprüfung und zwei konkrete Beinahe-Fälle. **Er bringt keine neue Übersetzung.** Nächste Route noch nicht ausgewählt. Die andere Arbeitsfassung W38 bleibt getrennt erhalten.

## Reproduktion und Grenzen

[VALIDATION.json](VALIDATION.json): PASS. 45 Eingabedateien hashgebunden. Separater Code prüft alle Rohgruppen gegen die gebundene Prosa, alle sieben Record-Proxys, die komplette Menge der 21 Paarungen, jede zulässige Ein-Schritt-Ausrichtung und alle 13 Zustandspositionen. Derselbe Bearbeiter, keine unabhängige Bedeutungsprüfung.

```sh
python research_registry/proposals/translation_programs_20260912/work/W39/build.py
python research_registry/proposals/translation_programs_20260912/work/W39/validate.py
```

Die Inhalte waren bereits in früheren Projektversuchen exponiert; keine Blindheit oder unabhängige Blattbestätigung. Keine neuen Manuskriptseiten oder Kontakte; sämtliche Reserveseiten einschließlich f84/f84r geschlossen. Keine moderne randomisierte Versuchspraxis unterstellt. Keine Signifikanz, Kausalwirkung, bestätigte Wort-/Pflanzennamen oder scorefähige GDT388-Evidenz. Publikationsprüfung ersetzt keine globale Prüfung bekannter GDT600-/Indexaltprobleme.
