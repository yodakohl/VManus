# GDT819 — geschriebene Wiederholung oder künstliche Wortgrenze?

2026-09-05. Ergebnis: Zwei Einwände gegen die letzte Satzhypothese werden
korrigiert beziehungsweise schwächer. Die echten Wiederholungen bleiben.
Keine neue Seite, kein neues bestätigtes Wort, keine bestätigte Übersetzung.

## Was sich tatsächlich ändert

Die RF-Lesung von f77r.35 hat **acht Quellgruppen und einen viergliedrigen
Schluss**, nicht neun Wörter mit fünfgliedrigem Schluss. Die Rohgruppe
`che@152;aiin` wurde beim alten Bereinigen zu `che aiin` zerlegt. Entsprechend
ist RF `shee@152;y` auf f81r.19 eine Quellgruppe, nicht zwei getrennte Wörter.
`@152;` ist dabei ein erhaltenes Transkriptionssymbol, keine entschlüsselte
Bedeutung und hier auch keine automatisch freigegebene EVA-d-Entsprechung.

Das war im Repository bereits am2026-08-09 dokumentiert:
`source_separator_transcription_correction` im Ledger, Spezifikation und
`experiments/semantic_assumptions/results/source_separator_transcription_validation_report.md`.
GDT818 hat die Korrektur bei seinen konkreten RF-Vergleichen nicht ausreichend
berücksichtigt. GDT819 entdeckt deshalb keinen neuen globalen Fehler, sondern
wendet die vorhandene Korrektur auf die aktive Hypothese an. Die früheren
Artefakte bleiben unverändert; ihre betroffenen Wortgrenzenbehauptungen gelten
als überholt. Nicht sämtliche älteren Ergebnisse sind damit erneut geprüft.

Der Mechanismus ist nachvollziehbar: Der alte Cleaner teilt am Semikolon von
`@number;` und entfernt anschließend Nichtbuchstaben. Der vorhandene Atlas
bewahrt dagegen die ganze Quellgruppe und den Typ der echten Quellgrenze.
An allen15 aktuellen Zielvergleichen reproduziert seine Fragmentfolge exakt
die jeweilige heutige Clean-Zeile. Eine Quellgruppe ist trotzdem noch kein
bewiesenes sprachliches Wort.

## Bild und Quelle im direkten Vergleich

| Stelle | Befund | Konsequenz für die Bedeutungen |
|---|---|---|
| f76r.23 | Zwei chedy-artige Schriftkomplexe wirklich geschrieben; RF zweite Gruppe `che@152;y`. | Die Schwierigkeit für einheitlich finites „wird/enthält“ bleibt. |
| f77r.12 | Zusatz über dem ersten strittigen Bench-Zeichen begünstigt lokal IT `shedaiin`; RF hat zwei statt vier künstlich zerlegter Gruppen. | Der ZL-basierte Einwand „ist wird/enthält“ ist weniger quellensicher. Kein Beleg für „ist“. |
| f77r.34 | Beide qokaiin-artigen Gruppen tatsächlich geschrieben. | „Luft Luft“ bleibt unter der Luft-Hypothese offen. Nicht löschen oder zwei Luftsorten erfinden. |
| f77r.35 | Acht große Komplexe plausibel; vorletzte Gruppe kompakt. RF `qotaiin` bleibt echt abweichend; k/t optisch offen. | Der zusätzliche RF-Wortgrenzeneinwand entfällt, nicht die Lesungs- und Bedeutungsunsicherheit. |
| f81r.19 | Mittlere Gruppe zusammenhängend; RF `ol,am` am Ende ist hingegen eine echte unsichere Quellgrenze. | `shee y` widerlegt den Konnektor nicht; „wenn/mit“ und Satzanschluss bleiben unentschieden. |

Alle fünf Stellen liegen innerhalb ihrer Quellabsätze. Keine eindeutig
diagnostische Satzgrenzenmarkierung wurde erkannt. Das beweist weder einen
einzigen durchlaufenden Satz noch die Unmöglichkeit unpunktierter Nebensätze.
Der Bildbefund liefert auch keinen Besitzer eines Wortes in einer Zeichnung.
f76r ist eine Textseite mit Randzeichen, keine Badeszene.

Die lokale Präferenz für IT `shedaiin` ist eine manuelle Bildentscheidung mit
mittlerer Sicherheit. Rohquellen werden nicht überschrieben und die restliche
IT-Zeile nicht automatisch bevorzugt. Zwei Betrachter derselben Aufnahme sind
keine unabhängigen Manuskriptzeugen. Details und Gegenbeobachtungen stehen in
`src/COORDINATOR_VISUAL.md`, `src/F77R_VISUAL.md`, `src/F81R_VISUAL.md` und
`src/SOURCE_AUDIT.md`; die fünf Entscheidungen in `src/READING_DECISIONS.tsv`.

## Was die Arbeitsübersetzung jetzt sagt

Die konkrete ZL/IT-Versuchsaussage bleibt:

> Dessen Dampf wird Wasser, wenn die Luft kalt ist.

Das ist weiterhin eine **vollständig hypothetische Zuordnung samt deutscher
Satzanordnung**, keine gelesene Übersetzung. Die vier neuen Schlussbedeutungen
wurden in GDT818 nach Sichtung passend zur Satzidee vorgeschlagen. Die
Bildprüfung bestätigt weder Dampf/Wasser noch Luft/kalt oder die Grammatik.

Quelltreu ausgerichteter RF-Versuch, ohne erfundene Zusammenführung:

`solkeey | okaiin | chedy | qokain | sheedy | qotaiin | che@152;aiin | chealy`

`Dampf? | dessen? | wird? | Wasser? | wenn? | [offen] | [offen] | kalt?`

Der Schluss hat nun nicht mehr ein zusätzliches vermeintliches Wort. Er ist
aber weiterhin unvollständig. Insbesondere wird `qotaiin` nicht zu `qokaiin`
gemacht und das erhaltene Sondersymbol nicht als bewiesenes d eingesetzt.
Die getrennten Becken-/Enthalten-Rivalen bleiben ebenso unverändert C0.

Der relative Vorteil von „wenn“ gegenüber dem ausdrücklich rechtsgerichteten
präpositionalen „mit + nominaler Ergänzung“ auf f81r.19 hängt weiterhin daran,
dass `chedy` wirklich finit wäre. Die Aufnahme bestätigt diese Wortart nicht.
Die tatsächlichen Doubletten sind gerade ein Grund, die Finite-Verb-Annahme
nicht aus dem gut klingenden Einzelsatz auf den ganzen Text zu übertragen.

## Umfang und Reproduzierbarkeit

Drei bereits freigegebene Seiten, fünf Zielstellen, vier vollständige P-Ströme:
74 Prosa-Loci und neun separat erhaltene Labels. Der Koordinator hat den ganzen
Reader einschließlich abweichender Lesungen gelesen. Nicht alle anderen
Vorkommen der Kandidaten und nicht der gesamte39-Selektoren-Bestand wurden
erneut bildlich oder diplomatisch untersucht.

| Ziel | ZL-Gruppen | IT-Gruppen | RF-Gruppen |
|---|---:|---:|---:|
| f76r.23 | 13 | 13 | 13 |
| f77r.12 | 8 | 9 | 8 |
| f77r.34 | 8 | 9 | 8 |
| f77r.35 | 8 | 8 | 8 |
| f81r.19 | 5 | 5 | 6 |

Insgesamt129 Zielgruppen in15 Lesungsvergleichen;16 markierte Problemgruppen.
IT `sheol.ol` auf f77r.12 und `qol.chedy` auf f77r.34 bleiben echte abweichende
Quelltrennungen. RF `ol,am` auf f81r.19 bleibt ein unsicherer kleiner Abstand.
Diese Unterschiede sind nicht der Semikolonfehler.

13 dokumentierte Bildderivate derselben drei Seiten, davon zehn Regionsbilder,
nicht13 Seiten oder unabhängige Bildbelege. Öffentliche Yale-Identitäten,
Regionen, Größen und Dateihashes sind unter `src/*_IMAGES.tsv` und
`src/CANVASES.json` festgehalten. Neue regionale Downloads sind keine neuen
Seitenfreigaben. Keine Bildgenerierung oder Bildverbesserung.

Runner und unabhängiger Validator bestehen. Letzterer rekonstruiert Quellen,
Grenzen, Fragmentzuordnung, die fünf rohen ZL-Zeilen, Kontext und Metadaten;
sechs Negativmutationen werden erkannt. Er prüft keine Bildpixel, manuelle
Glyphenwahrheit oder Semantik. Keine neue Relation wird als Evidenz angeboten;
die vier GDT818-Alternativen bleiben GDT388-ineligible.

## Nächster konkreter Schritt

Die vorhandene Quellgruppenschicht in die begrenzten GDT818-Konnektor- und
Prädikatkontexte übernehmen; dann die konkreten Bedeutungen an diesen ganzen
Absätzen weiterentwickeln. Vorrang haben die echten Doubletten und die Frage,
ob `chedy` überhaupt ein selbständiges finites Verb sein muss. Keine neue
Wortliste, keine automatische Hilfsverb-Rettung und keine globale Wiederholung
aller alten Experimente. Der kleine Satzversuch bleibt offen, ohne seine
sprachliche Wohlgeformtheit mit einer Entschlüsselung zu verwechseln.
