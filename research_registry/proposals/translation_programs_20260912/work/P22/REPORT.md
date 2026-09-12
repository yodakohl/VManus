# P22 — Zerlegung muss dieselbe Grammatik tragen

M zerlegt zwei Gruppen nach derselben festen Regel: cthodaiin wird ctho+daiin, odaiin wird o+daiin. Nur ctho besitzt eine angesetzte Stammkarte. Die zusätzliche Pulver-Objektphrase auf f21r.8 bleibt ohne regierende Handlung. An allen sechs Handlungsstellen haben W und M dieselben Ergebnisse; die Grenzregel wählt deshalb keine tragfähige Objektgrammatik aus.

| Modell | Quellgruppen / Elemente | vollständige / partielle Hypothesen / offen | Fallmarker | Handlungen |
|---|---|---|---|---|
| W | 145 / 145 | {'OPEN': 100, 'FULL_HYPOTHESIS': 45} | {'MARKED_OBJECT': 7, 'DUPLICATE_CASE': 1} | {'UNMARKED_ARGUMENT': 4, 'MATCH_OBJECT': 1, 'MISSING_ARGUMENT': 1} |
| M | 145 / 147 | {'OPEN': 98, 'FULL_HYPOTHESIS': 46, 'PARTIAL_HYPOTHESIS': 1} | {'MARKED_OBJECT': 8, 'DUPLICATE_CASE': 1, 'UNKNOWN_STEM': 1} | {'UNMARKED_ARGUMENT': 4, 'MATCH_OBJECT': 1, 'MISSING_ARGUMENT': 1} |

W behält Gruppen als Wörter und daiin als freie Objektpartikel. M trennt jedes nichtleere X+daiin und liest daiin als freie oder gebundene Objektmarkierung. Eine gemeinsame hypothetische Funktion, keine Laut- oder Sprachidentifikation. Zehn feste Materialköpfe und zwei Verben werden in allen vier Absätzen gleich verwendet. Die vollständige Schriftstückausrichtung steht in ELEMENTS_W/M.tsv mit Zeichenintervallen; keine Quellgrenze wird überschrieben.

## Die beiden neuen Zerlegungen

| Ort | Gruppe | Zerlegung | Konsequenz |
|---|---|---|---|
| f21r.8:7 | cthodaiin | ctho + daiin | Pulver als OBJECT; kein regierendes Verb im Modell |
| f29v.3:5 | odaiin | o + daiin | Stamm o unbekannt; keine Zusatzportion erfunden und kein Rückgriff auf einen fremden Kopf |

ctho+daiin auf f21r.8 und geschriebenes ctho daiin auf f32v.8 erhalten in M dieselbe innere Hypothese. Beide markierten NPs sind hier unregiert. GDT809 hatte die alternative RF-Grenze auf f32v.8 schon dokumentiert; die Zeichenübereinstimmung ist kein neuer Fund. Die gemeinsame Funktion wurde eingesetzt, nicht unabhängig entdeckt.

## Sämtliche Handlungsargumente (W und M identisch)

| Ort | Verb | angenommener Kopf | Objektmarkierung | Befund | offene Zwischenstücke |
|---|---|---|---|---|---|
| f21r.9:2 | sho | cthy | UNMARKED | UNMARKED_ARGUMENT | f21r.9:3/1:tshaiin,f21r.9:4/1:chkaiin,f21r.9:5/1:sh,f21r.9:6/1:cthey,f21r.9:7/1:cthody |
| f32v.9:1 | qotchy | chocthy | OBJECT | MATCH_OBJECT | f32v.9:2/1:cfhy,f32v.9:3/1:skey |
| f32v.10:1 | sho | keol | UNMARKED | UNMARKED_ARGUMENT | NONE |
| f32v.11:2 | sho | chy | UNMARKED | UNMARKED_ARGUMENT | NONE |
| f29v.3:6 | qotchy | NA | NA | MISSING_ARGUMENT | f29v.3:7/1:taiin,f29v.3:8/1:s,f29v.3:9/1:she,f29v.3:10/1:otey,f29v.3:11/1:sy |
| f29v.4:8 | sho | okaiin | UNMARKED | UNMARKED_ARGUMENT | NONE |

## Grammatische Gegenfälle

Das doppelte daiin auf f32v.8:2–3 markiert denselben otchol-Kopf zweimal und verletzt die festgelegte Einmalregel. Die Wiederholung bleibt stehen; sie wird weder zu einer Zahl noch zu einer Ausnahme umgedeutet. Ein markierter Materialkopf bei qotchy auf f32v.9 passt zur angesetzten Valenz, aber cfhy und skey bleiben zwischen Verb und Kopf offen; das ist keine unabhängig bestätigte Satzanalyse. Vier andere Argumente sind unmarkiert, ein Argument fehlt.

Der Startabsatz f17r enthält kein daiin und keine gewählte Handlung; er bietet keine Kapazität für die Grenz-/Objektregel. Er wird vollständig als partieller Katalogrest erhalten. Unregierte markierte NPs und unbekannte Wortstücke werden nicht als grammatische Erfolge gezählt. Auch die deutsche Pluralform Blüten liefert kein gelesenes Numerusparadigma.

## Entscheidung

Die Ein-Regel-Zerlegung erzeugt genau eine zusätzliche vollständig hypothetisch lesbare Rohgruppe, aber keine zusätzliche passende Handlung. W und M bleiben hinsichtlich aller Handlungsargumente ununterscheidbar; die feste allgemeine Objektmarkierung passt nicht durchgängig. M ist eine dokumentierte Grenzhypothese, keine ausgewählte Wortanalyse. Eine flektierende Sprache, Silbenwerte und ein Flexionsparadigma wurden nicht bestimmt. Das umfassendere P22-Programm bleibt partiell; kein allgemeines Urteil gegen variable Wortgrenzen.

GDT605/616/895/906/911 und GDT629 bleiben unverändert. Insbesondere kein Neustart alter Einheiten-/CV-Decoder und keine gelockerte GDT616-Entscheidung. P20s feste technische Ganzwörter und P21s Ganzformfälle sind Vorgänger, keine unabhängigen Belege. Alle vier HERB4-Absätze waren exponiert. Keine Reservenöffnung, keine Bedeutung oder Signifikanz behauptet; f84/f84r geschlossen.

## Reproduktion

`python3 research_registry/proposals/translation_programs_20260912/work/P22/build.py`; `python3 research_registry/proposals/translation_programs_20260912/work/P22/validate.py` aus dem Repository. SOURCE.json bindet die begrenzte Quelle und vor Ausführung festgelegte DECISION.md. ALL_SPLITS.tsv enthält jeden Schnitt; CASE_MARKERS/OPERATIONS/NOUN_PHRASES sämtliche grammatischen Folgen; READING_W/M.md alle vier Absätze.
