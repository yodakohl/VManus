# P29 — das vollständige Tintenrezept trägt die HERB4-Lesung nicht

Die eine gewählte Quelle liefert unter den drei festen Bearbeitungsregeln keine vollständig gebundene Aussagekorrespondenz. Die Nassfassung R gewinnt zwei allgemeine Filter-Parallelen gegenüber A, aber keine passende vollständige Folge. Quellenidentität wird für diesen Kandidaten nicht übernommen; die eigenständigen P05-Lesungen bleiben mit ihren offenen Stellen und bisherigen Problemen erhalten.

Quelle: [Recette d’encre du XIVe siècle,1925,S.484](https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583), vollständige veröffentlichte lateinische Rezepttranskription aus BnF lat.8651 f88v. HISTORICAL_TEXT.txt und HISTORICAL_CLAUSES.json enthalten den ganzen Rezepttext, nicht nur die alte Ausdrucksbank. Der französische Herausgeberkommentar ist kein Rezeptbestandteil.

A und R enthalten alle145HERB4-Gruppen, je90hypothetisch und55offen. R übernimmt die ältere P05-Nassfassung mit genau vier globalen Änderungen (MODEL.json); kein neues Einzelfallwörterbuch. Die autonome Vorlage bestand vor dem aktuellen Vergleich; eine quellenunbeeinflusste oder blinde Entstehung wird ausdrücklich nicht behauptet.

## Ganze Absätze, keine passenden Einzelstellen

| Fassung | Absatz | Zieloperationen | reine Familienpaare | Quellaussagen ohne Partner /16 | Zieloperationen ohne Partner | Ordnungsumkehrungen | vollständig gebundene Aussagen |
|---|---|---:|---:|---:|---:|---:|---:|
| A | f17r | 0 | 0 | 16 | 0 | 0 | 0 |
| A | f21r | 2 | 0 | 16 | 2 | 0 | 0 |
| A | f32v | 8 | 2 | 14 | 6 | 1 | 0 |
| A | f29v | 7 | 2 | 14 | 5 | 0 | 0 |
| R | f17r | 0 | 0 | 16 | 0 | 0 | 0 |
| R | f21r | 2 | 0 | 16 | 2 | 0 | 0 |
| R | f32v | 8 | 3 | 13 | 5 | 2 | 0 |
| R | f29v | 7 | 3 | 13 | 4 | 1 | 0 |

Familienpaare sind keine Übersetzungstreffer. Das n-te Vorkommen einer Familie erhält das n-te Quellvorkommen; diese feste Diagnose ist keine optimierte Ausrichtung und widerlegt keine beliebige freie Paraphrase. SOURCE_TARGET_TABLE.tsv zeigt für jeden Absatz alle16Quellaussagen, TARGET_EVENTS.tsv zusätzlich jedes Zielereignis ohne Partner.

## Alle konkreten Operationspaare

| Fassung | Ziel | Familie | Quellaussage | Zielmaterial / Quellmaterial | fehlende Quellbedingung |
|---|---|---|---|---|---|
| A | f32v.7:8 | MIX | S12 | NA / WINE+VITRIOL | beide gut miteinander |
| A | f32v.8:7 | TAKE | S01 | qotaiin / WATER | 12 librae Regenwasser |
| A | f29v.1:6 | WET | S03 | cthy / GALLS+WATER | abends bis morgens; dieselben Gallen und dasselbe Regenwasser |
| A | f29v.4:7 | HEAT | S04 | cthy / GALLS+WATER | Kochen; Wasser bis zur Hälfte verbraucht |
| R | f32v.7:8 | MIX | S12 | NA / WINE+VITRIOL | beide gut miteinander |
| R | f32v.8:7 | TAKE | S01 | qotaiin / WATER | 12 librae Regenwasser |
| R | f32v.9:1 | FILTER | S05 | shan / WATER1 | sehr gut durch feines Tuch; erste Filtration |
| R | f29v.1:6 | WET | S03 | cthy / GALLS+WATER | abends bis morgens; dieselben Gallen und dasselbe Regenwasser |
| R | f29v.3:6 | FILTER | S05 | odaiin / WATER1 | sehr gut durch feines Tuch; erste Filtration |
| R | f29v.4:7 | HEAT | S04 | cthy / GALLS+WATER | Kochen; Wasser bis zur Hälfte verbraucht |

## Warum die ungewöhnliche Abfolge nicht übernommen werden kann

Die Quelle enthält drei Filtrationen und vier Hitzeereignisse: Kochen bis zur Hälfte, Rückkehr ans Feuer, Kochen bis zur Gummiauflösung und kurzes Kochen der letzten Mischung. R hat in jedem der beiden einschlägigen Absätze nur eine angenommene Filtration; nur f29v hat überhaupt eine Erwärmung. Die getrennten Absätze dürfen nicht zu einem Rezept zusammengeschnitten werden. Auch gemeinsam böten sie nur zwei Filterstellen.

Auf f29v folgt die angenommene Erwärmung erst nach dem Filtervorgang; die fest gepaarten ersten Quellereignisse verlangen Erhitzen vor Filtern. Auf f32v steht das vermische vor entnimm und Filter; im Quellenpaar liegt das Wein-/Vitriol-Mischen später. ORDER_CONFLICTS.tsv hält jede Umkehrung fest, ohne Operationen passend umzunummerieren.

Nachtfrist, Halbvolumen, Auflösung des Gummis und die spezifischen Maße erhalten keine gebundene Voynich-Aussage. Standzeit oder festgelegte Dosis ersetzen weder bis morgens noch ein konkretes Mengenverhältnis. Keine Materialkorrespondenz hält hier zugleich Zutatenidentität, Ein-/Ausgaben und alle Wiederaufnahmen fest. Allgemeine Operationen und frei angenommene Stoffnamen genügen nicht.

Die source repone ... ad ignem ist Rückkehr ans Feuer, kein Ruhenlassen. Deshalb bekommen die beiden she≈lasse stehen-Stellen keinen S06-Partner. GDT755s Quellenhinweis wird so präzisiert, nicht als neue Manuskriptentdeckung ausgegeben. Auch die automatische Verallgemeinerung von Kochen zu Erhitzen verliert eine Intensitätsbedingung, die im Tableau offen bleibt.

## Entscheidung und Reproduktion

Den konkreten Tintenrezept-Vorlagenkandidaten nicht behalten: Es müssten überwiegend fehlende Bedingungen, Zutatenbezüge und Operationen ergänzt oder unzulässige Umstellungen vorgenommen werden. A/R bleiben autonome partielle Herstellungsentwürfe, keine bestätigten Rezeptinhalte. P05s frühere Feuchte-/Trockenheits- und Produktidentitätslücken werden durch den Vergleich nicht beseitigt. Kein neuer Decoder, keine Behauptung allgemeiner Quellenlosigkeit, keine Signifikanz und keine Wortbedeutung bestätigt.

SOURCE.json bindet die autonome Vorlage, die gesamte historische Transkription und die vor Ausführung festgelegte Entscheidung. READING_A/R.md und ALIGNMENT_A/R.tsv bewahren alle Gruppen. Reproduktion: `python3 research_registry/proposals/translation_programs_20260912/work/P29/build.py`; `python3 research_registry/proposals/translation_programs_20260912/work/P29/validate.py` aus dem Repository. GDT341/343/887/893/894/923 bleiben unverändert. Keine neuen Voynich-Seiten oder Kontakte; f84/f84r geschlossen.
