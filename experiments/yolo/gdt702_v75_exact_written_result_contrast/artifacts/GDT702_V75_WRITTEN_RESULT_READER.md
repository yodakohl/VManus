# GDT702 — V75 exact written-result reader

Status: `PASS_V75_11_TARGET_RIGHT_CONTEXTS__7_NOMINAL_3_ACTION_1_EOS__1_EXACT_WRITTEN_RESULT__2X2_DEFAULTS_REJECTED__C012_OCCURRENCE_BOUND__ZERO_WORD_DELTA`

## Konkrete neue Arbeitskette

> Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. Ergebnis: fertiges Holzextraktpulver.

Die neue Kante ist ausschließlich `C012: f105v.1#4 ykaiin → #5 olpchedy`. C001 liefert weiterhin den geschriebenen Patienten `#3 olpcheey`; #4 ist damit die gemeinsame Aktionsbrücke zwischen Eingang und geschriebenem Resultatzustand.

## Vollständiger Rechtskontext-Zensus

| Kante | Locus | vollständige Zielaktion | erster rechter Eintrag | Klasse | Entscheidung |
|---|---|---|---|---|---|
| C001 | `f105v.1` | #4–#4 `ykaiin` | #5 `olpchedy` | NOMINAL_BLOCK | CANDIDATE_C012 |
| C002 | `f113v.17` | #7–#7 `yteeeor` | — | END_OF_LINE | EXCLUDE_END_OF_LINE |
| C003 | `f75r.3` | #4–#4 `qey` | #5 `kain` | NOMINAL_BLOCK | EXCLUDE_STATE_ONLY_NO_MATERIAL_HEAD |
| C004 | `f80v.35` | #4–#5 `y|qol` | #6 `qol` | ACTION_CLAUSE | EXCLUDE_NEXT_ACTION_ALREADY_C008 |
| C005 | `f77r.38` | #6–#6 `qol` | #7 `ltaiin` | NOMINAL_BLOCK | HOLD_MATERIAL_HEAD_MISMATCH |
| C006 | `f86v6.25` | #5–#5 `ykaiin` | #6 `or` | NOMINAL_BLOCK | HOLD_MATERIAL_LABEL_NO_EXACT_RESULT_STATE |
| C007 | `f86v6.25` | #4–#4 `qodar` | #5 `ykaiin` | ACTION_CLAUSE | EXCLUDE_NEXT_ACTION_ALREADY_C006 |
| C008 | `f80v.35` | #6–#6 `qol` | #7 `kain` | NOMINAL_BLOCK | EXCLUDE_STATE_ONLY_NO_MATERIAL_HEAD |
| C009 | `f104v.2` | #6–#6 `qokamdy` | #7 `otarar` | NOMINAL_BLOCK | HOLD_SOURCE_LINEAGE_NOT_RESULT |
| C010 | `f86v5.24` | #3–#3 `ykain` | #4 `okal` | NOMINAL_BLOCK | HOLD_MATERIAL_REGISTER_NOT_RESULT |
| C011 | `f26r.2` | #6–#7 `ytedy|dy` | #8 `checthedy` | ACTION_CLAUSE | EXCLUDE_NEXT_ACTION_C011_STOPS_BEFORE_8 |

Exakte Verteilung: **7 Nominalblöcke, 3 Aktionsklauseln, 1 Zeilenende**. Kein späteres attraktiveres Wort wird über den ersten rechten semantischen Eintrag hinweg ausgewählt.

## Der 2×2-Kontrast

- Das zweite `ykaiin` (`f86v6.25#5`) wird rechts von `or` gefolgt, nicht von einem exakt typisierten Fertigresultat.
- Das zweite `olpchedy` (`f105v.14#4`) folgt auf `qokaiir` ‚nimm den heißen Drogenanteil III‘; das passt materiell nicht zum Holzextraktpulver.
- Deshalb gelten weder `ykaiin → Ergebnis`, noch `olpchedy → vorherige Aktion`, noch bloße Nachbarschaft als Default.
- GDT689 lässt `olpchedy` nur als gelerntes Ganzwort zu; eine produktive `olpche*`-Ableitung bleibt verboten.

## Evidenzgrenze

GDT682 formulierte dieses Ergebnis bereits in der alten praktischen Prosa. GDT687 typisierte beide OLPCHEDY-Stellen als nominale Fertigresultatzustände. Beides macht C012 nachvollziehbar, aber nicht unabhängig: C012 bleibt daher B-tier, occurrence-bound und nicht score-ready. Die 479 Wortglossen, 51 Zeilenübersetzungen und 3 gebundenen Spannen bleiben unverändert; hinzu kommt keine Wortbedeutung und keine Seite.
