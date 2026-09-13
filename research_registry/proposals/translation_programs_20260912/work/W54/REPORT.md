# W54 — Ist B im bisherigen Textmodell ein behandelter Körper?

**Nein: Die vorhandene W41-Rechnung behandelt B nirgends selbst.** In allen sechs Fassungen ist B Ziel einer Überführung oder (H1) der Handelnde. Die behandelten Objekte sind A/C oder fehlen. Das ist eine Eigenschaft unserer gesetzten Rollen, kein Befund gegen Körper im Manuskript. Die Bildpriorisierung W53 darf daher nicht als Bestätigung einer bereits ausgeführten Patientenlesung erscheinen.

2026-09-13. Vollständiger Audit aller sieben Records, 51 Quellzeilen, 341 Gruppen und 162 gespeicherten Ereigniszeilen. Keine Wortwerte, Bindungen oder Zugriffskonten geändert. Alle exponierten Quellzeilen stehen in COMPLETE_LINES.md; ALL_RECORDS.tsv enthält alle 42 Record/Fassungs-Kombinationen einschließlich ereignislosem Q2 und sämtliche Ereigniskoordinaten. W41s vollständige sechs Lesefassungen bleiben unverändert.

| Record | Erwärmungen | Überführungen | qoky | B als Überführungsziel | B als behandeltes Objekt |
|---|---:|---:|---:|---:|---:|
| P1 | 5 | 1 | 3 | 1 | 0 |
| P2 | 1 | 1 | 0 | 1 | 0 |
| P3 | 3 | 1 | 1 | 0 | 0 |
| P4 | 2 | 3 | 2 | 0 | 0 |
| P5 | 2 | 0 | 1 | 0 | 0 |
| Q1 | 1 | 0 | 0 | 0 | 0 |
| Q2 | 0 | 0 | 0 | 0 | 0 |

Diese Ereignis-/Zielzahlen sind in allen sechs Fassungen gleich. A/C-Bezug und Akteurskonto unterscheiden sich weiterhin. In H1 handelt B an genau einer Erwärmung (.8:5); das macht B zum Ausführenden, nicht zum erwärmten Objekt. Sechs Fassungen sind keine sechs unabhängigen Belege.

## Welche Körperlesung wäre damit möglich?

Eine Person kann eine Flüssigkeit empfangen. Darum wäre „A an B geben“ bei B als Person grundsätzlich formulierbar. Die vorhandene W41-Deutung überträgt dabei jedoch Bearbeitungszugriff; sie behauptet weder Baden noch Trinken noch äußere Anwendung. Keine dieser drei Anwendungsarten wird durch die Zielrolle unterschieden. „B wird warm/benetzt“ folgt ebenfalls nicht aus „B erhält A“. Dafür bräuchte es eine eigens gebundene Zustandsaussage über B. Auch qoky = „B arbeitet weiter“ darf nicht still in „B wird weiter behandelt“ umgeschrieben werden.

Der positive T0/H1-Anschluss .6–8 bleibt also „A an B; B handelt; B erwärmt A“. Er lautet ausdrücklich nicht „B nimmt ein warmes Bad“. Der W41-Gegenfall .14:2/.16:5 und vier qoky ohne Empfänger bleiben unverändert. Eine Patientenfassung durch Weglassen des Zugriffskontos würde diese Fehler nur nicht mehr prüfen.

## Bereits vorhandene Alternative: P07

Der primäre P07-Bericht wurde geprüft. Dort existiert bereits die konstruierte Folge f83r.5–7: „Wasser … Hand – spüle – leite Wasser weiter – Rumpf … ist benetzt.“ Dieselben Bezüge tragen gleich gut „Wasser … Einlass – spüle – leite Wasser weiter – Mittelbecken … ist benetzt“. Alle 341 Gruppen wurden damals verarbeitet, 274 blieben offen. Im Absatzmodell waren 7/20 Handlungen vollständig und 3/13 Zustände an frühere vollständige Ursachen gebunden. PANEL vervollständigte drei weitere Handlungen durch übernommenen Kontext, ohne eine zusätzliche Zustandsfolge zu erklären.

Damit wurde eine Körper-/Zustandslesung schon tatsächlich versucht. Die Bilder liefern weiterhin keine Wortzuordnung zu Hand, Rumpf oder Unterkörper. P07 erneut auszuführen würde dieselbe Unentscheidbarkeit reproduzieren. W54 hat P07 nicht neu gerechnet und behauptet keine neue Bestätigung seiner Zahlen.

## Entscheidung

Die brauchbare Arbeitshypothese bleibt eine Körper-/Flüssigkeitsdarstellung; eine konkrete Textübersetzung ist damit nicht gewählt. W41 wird nicht zu einem Patientenmodell umetikettiert. P07 wird nicht allein wegen der erneuten Bildsichtung wiederholt. Ein nächster semantischer Kandidat braucht eine geschriebene Konsequenz, die Körper und Station unterschiedlich erfüllen, etwa eine ausdrücklich an denselben Teilnehmer gebundene Empfindung oder Reaktion. Solange das nur eine frei gewählte Wortbedeutung wäre, wäre auch dieser Unterschied konstruiert. Kein solcher Textbeleg wird hier behauptet.

Dies ist eine Klärung des vorhandenen Modellumfangs, kein neues entziffertes Wort. Vorherige Projekt- und Bildexposition sind bekannt; keine unabhängige Bedeutungsprüfung, keine Signifikanz. Keine neuen Bilder oder reservierten Texte geöffnet; f84/f84r geschlossen. GDT674s früherer verworfener Guard-Vorfall bleibt als Projektvorbelastung bekannt, dessen Ausgabe wurde hier nicht gelesen.

Reproduktion: `python research_registry/proposals/translation_programs_20260912/work/W54/audit.py`, dann `python research_registry/proposals/translation_programs_20260912/work/W54/validate.py`. Validator prüft vollständige Aggregation und Quellenintegrität, keine Bedeutungswahrheit.

Prüfstatus: Register PASS; globale Prüfung unverändert acht bekannte Altfehler (sieben GDT600-Bindungen und veralteter Index). Diese Altbestände bleiben unverändert.
