# W02: erste zusammenhängende Absatzlesung mit gemeinsamem Wörterbuch

**Eine konkrete Herstellungslesung für den ganzen Absatz f6v.6–21 ist ausgearbeitet und auf alle13festgelegten Absatzumgebungen mit denselben Wortwerten angewendet.** Sie ist eine ausgeschriebene Hypothesenfassung, keine bestätigte Übersetzung. [Den vollständigen ersten Absatz lesen](FIRST_PARAGRAPH.md).

Der neue lokale Entwurf lautet auf f6v.8 unter unseren Annahmen:

> Ferner, [zu den] Blüten: zerstoße [sie] fein [und] erwärme [sie] portionsweise.

Die nächste Zeile setzt mit dem gleichen als Blüten angesetzten Wort bei einem möglichen Abmessen fort. So entsteht unter einer expliziten Identitätsannahme die Folge **fein zerstoßen → portionsweise erwärmen → abmessen**, später mit einer möglichen Aufbewahrung. Eine zweite Kette verbindet dasselbe angenommene Krautpulver mit Trocknen, Erhitzen und Vermischen. Die Schrift trägt die wiederholten Formen; die Bedeutungen und die Chargenidentität wurden von uns angesetzt.

## Was tatsächlich ausgearbeitet wurde

- Alle13ZL-Absätze,152Zeilen,900Originalgruppen; keine angenehme Einzelstelle ausgewählt. In fünf Fällen unterscheidet sich der IT-Absatzumfang; RF liefert keine Absatzgrenzen. Alle152zugehörigen Rohzeilen auch in IT/RF erhalten.
- Ein gemeinsames Wörterbuch mit148ausdrücklich unbestätigten Ganzwortannahmen. 530Positionen erhalten dadurch eine Hypothese,370bleiben ungelesen. Die Zahl ist Abdeckung durch Annahmen, keine Trefferquote.
- Im ersten Absatz sind67von71Gruppen hypothetisch ausgefüllt, vier unsichere Rohgruppen offen. Dazu sind53verschiedene Wortannahmen nötig; dieser hohe Freiheitsgrad verhindert eine Bedeutungsbestätigung.
- Vollständige A/B-Ausrichtung: ychor≈ferner versus ychor≈nimm, alle übrigen147Wortwerte identisch. Eine gemeinsame Argumentregel wird an allen77 beziehungsweise90angenommenen Handlungen angewendet.
- Alle Materialnennungen und34Gruppen wiederholter Materialnamen, mit SAME-/NEW-Identitätsfolgen. Gleiche Wortform erzwingt keine gleiche Charge.

[Alle Absätze und ihre Probleme](PARAGRAPH_INTERPRETATIONS.md), [vollständige additive Ausrichtung](READING_A.md), [Befehlsgegenfassung](READING_B.md), [gemeinsames Wörterbuch](LEXICON.tsv), [sämtliche Argumentbindungen](ARGUMENTS.tsv), [sämtliche Materialketten](MATERIAL_CHAINS.tsv).

## Was der Entwurf noch nicht löst

Die feste lokale Zustandslesung von f9v.11 nennt dasselbe angenommene kühl-feuchte Material anschließend warm. Ohne zeitliche Trennung oder andere Bedeutungsebene bleibt das widersprüchlich; kein zusätzlicher Erwärmungsschritt wird eingefügt. Auf f6v fehlen die zweiten Bestandteile der zwei binären Mischhandlungen und einzelne Qualitätsbezüge. Zahlreiche andere Absätze bleiben stark lückenhaft. Die genaue Rolle des Grundansatzes beim möglichen Abseihen auf f22v.8 ist trotz zweier Materialnamen nicht gebunden.

Die A-Fassung hat47Handlungen mit mindestens einer markierten Abhängigkeit, B49. Das umfasst ungelesene Zwischenwörter, ungesicherte implizite Subjekte, fehlende Mischpartner und fehlende Stoffsorten; diese verschiedenen Probleme sind keine47/49Widersprüche. Die Zahlen prüfen unsere Argumentdarstellung, nicht die historische Wahrheit der Sätze. Eine interne Korrektur zählt sieben bereits als konkrete Materialdosen definierte Wörter auch als mögliche Patienten; V01 bleibt als Darstellungsprotokoll erhalten und wird nicht als neuer semantischer Gewinn verkauft.

## Entscheidung

**Diesen zusammenhängenden Entwurf als konkrete Entwicklungsfassung behalten, keine Wörter bestätigen.** Er ist mehr als die W01-Zeile mit drei ungelesenen Wörtern: Es gibt ein ausgeschriebenes Inhaltsmodell, feste Wortwerte und explizite alternative Rückbezüge. Aber die genaue Blütenidentität und die Verben wurden nicht aus unabhängiger Evidenz erschlossen. Die Befehlsfassung lässt sich ebenfalls formulieren. Eine positionsabhängige Schreibung bleibt offen.

Die inhaltlich nächste Überarbeitung betrifft die Reichweite der Qualitätsangaben und die noch fehlenden Materialbeziehungen; sie müsste global für alle betroffenen Wörter gelten. Die vorliegende Fassung wird nicht durch still ergänzte Herstellungsschritte geglättet. Eine nahezu vollständige plausible Gesamtlesung der13Absätze liegt noch nicht vor. Keine Reserveseitenprüfung, keine Signifikanz, keine Sprach- oder Pflanzenidentifikation.

## Daten und Reproduktion

Nur bereits exponierte GDT928-Absätze und GDT915-Rohprojektionen um die13festen W01-Loci. W01s geglättete Körperzeilen unterscheiden sich an f17v.15/f19v.9/f23r.5 vom unbereinigten ZL; W02 erhält die ursprünglichen Unsicherheitsgruppen. [Alle Zielvarianten und Absatzgrenzen](READING_VARIANTS.md). Keine Quelle, Präfixregel oder Transkription eines alten Experiments geändert. f84/f84r bleiben versiegelt; keine Kontakte.

`python .../W02/extract.py`, `python .../W02/make_lexicon.py`, `python .../W02/build.py`, `python .../W02/build_contexts.py`, anschließend `python .../W02/validate.py`. Die Skripte serialisieren die offen geschriebene Hypothese und ihre Konsequenzen; sie lernen oder entschlüsseln keine Wortwerte. SOURCE.json und ALTERNATE_LINES.json binden die Eingaben mit Hashes. Validierung betrifft Dokumententreue, feste Wörter, vollständige Umfänge und Argumentabdeckung, keine Bedeutungswahrheit.

Bekannte globale Altbestandsprobleme bei GDT600/Index bleiben unverändert. Die zwei zusätzlich registrierten Rohideen IDEA000204/205 sind Planung, keine zusätzlichen Belege. Material und Quellcode werden nach exaktem Datenschutz-/Scope-Check veröffentlicht.
