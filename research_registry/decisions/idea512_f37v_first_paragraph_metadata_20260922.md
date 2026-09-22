# IDEA512: f37v erster Absatz — Metadaten vor Inhaltszugriff

Eingefroren 2026-09-22 15:41:43 UTC. Kein Rohwort-/Bildzugriff und kein Experimentlauf.

**Kapazität vorhanden, noch keine Bedeutungsprüfung oder Inhaltsfreigabe durch diese Notiz.** RAW512 nominiert ohne Inhaltswahl ausschließlich den ersten nativen Absatz von f37v. Dieser ist in ZL und IT vollständig f37v.1–7. ZL besitzt29, IT30 Rohgruppen; beide erfüllen20–100. Eine spätere Ersetzung durch einen anderen Absatz ist nicht Bestandteil dieses Rezepts.

| Leser | Erster ganzer Absatz | Gruppen je Zeile | Summe | Grenzstatus |
|---|---|---|---:|---|
| ZL3b | f37v.1–7 | 5,5,5,4,4,4,2 | 29 | start .1, end .7 |
| IT2a | f37v.1–7 | 5,6,5,4,4,4,2 | 30 | start .1, end .7 |
| RF1b | entsprechende vorhandene Zeilen .1–7 | 5,5,5,4,4,4,2 | 29 | alle paragraph flags0; keine eigene native Absatzgrenze |

RF-Zeilen dürfen vollständig als Gegenfassung des ausdrücklich ZL-/IT-nominierten Zeilenbereichs erhalten werden; daraus folgt keine unabhängige RF-Absatzabgrenzung. Fehlende Flags bedeuten nicht fehlende Zeilen. ZL/IT/RF sind alternative Transkriptionen, keine unabhängigen Manuskriptbelege.

Die tatsächlichen Wörter, Einzeltypen, Wiederholungen, unsicheren Zeichen und Separatoren wurden nicht geöffnet. Die Zahl zuvor unzugewiesener GANZFORMtypen ist höchstens die Rohgruppenzahl: somit maximal30 für jeden möglichen ZL-/IT-Entwurf und bereits unter45. Das ist eine metadatenbasierte Obergrenze, kein Worttypenzensus und kein Bedeutungsbefund. Andere Kosten (sechs Produktionen/acht Bindungen) sind noch nicht geprüft.

## Exakte Zulassung, Quelle und Auswahl

`experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv` enthält exakt `f37v`; SHA256 `f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`. Selektorbindung geprüft durch `./vmanus-exp query-tsv experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv --selector page --allow f37v --columns page`, selected=1. Dies ist Textzulassung, keine neue Bildzulassung.

Wörtliche Metadatenquelle `experiments/semantic_assumptions/results/source_separator_transcription.tsv`, SHA256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`. Guard: `./vmanus-exp query-tsv experiments/semantic_assumptions/results/source_separator_transcription.tsv --selector page --allow f37v --columns edition,page,locus,kind,paragraph_start,paragraph_end,source_row_index,source_group_count`. Ausschließlich diese Metadatenspalten wurden gelesen; wiederholte Zeilenmetadaten wurden identisch dedupliziert. Das ganze Blatt wurde nur nach Absatzflags/Quellreihenfolge angesehen, nicht nach Inhalt.

Die vollständige später zu entwickelnde Auswahl ist **einmal** f37v.1–7 unter ausdrücklich zu benennendem ZL oder IT; die andere Lesung sowie der entsprechende vollständige RF-Zeilenbereich bleiben Gegenfassungen. Diese Auswahl wurde vor jedem Wortinhalt eingefroren. Kein neuer Selektor, keine zweite Absatzwahl, keine Labels als Ersatzabsatz.

Bereits vorhandene f84-freie Quellpakete liegen unter `experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_DISCOVERY_ZL3b.json`, `SOURCE_DISCOVERY_IT2a.json` und `SOURCE_DISCOVERY_RF1b.json`. Der GDT915-SPEC ordnet f37v ausdrücklich DISCOVERY zu. Eine spätere Auswahl darin wäre nur `lines[].metadata.page=f37v` mit `metadata.locus` aus f37v.1–7; sie ersetzt nicht den hier eingefrorenen Selektor-/Grenzvertrag. Ihre Rohgruppen wurden in dieser Aufgabe nicht geöffnet.

Bereits besessene native Primärprämisse: `experiments/semantic_assumptions/results/f102r1_fifth_repeated_plant_label_native_visual_ownership_report.md`, gelesen ohne neues Bild. JSP2025_05 verbindet f37v mit dem Wurzel-/Blattfragment f102r1 row3/item1; die endgültige Materialstufe ist damit nicht beobachtet. Die neue FINAL_OUTPUT-Bindung, volle Lesung und referentielle Kontinuität bleiben Entwicklungsannahmen und werden durch diese Kapazitätsnotiz nicht bestätigt.

## Vollständige eingefrorene Metadaten des ersten Bereichs

| Leser | Locus | kind | start | end | Quellzeile | Gruppen |
|---|---|---|---:|---:|---:|---:|
| ZL3b | f37v.1 | P | 1 | 0 | 885 | 5 |
| ZL3b | f37v.2 | P | 0 | 0 | 886 | 5 |
| ZL3b | f37v.3 | P | 0 | 0 | 887 | 5 |
| ZL3b | f37v.4 | P | 0 | 0 | 888 | 4 |
| ZL3b | f37v.5 | P | 0 | 0 | 889 | 4 |
| ZL3b | f37v.6 | P | 0 | 0 | 890 | 4 |
| ZL3b | f37v.7 | P | 0 | 1 | 891 | 2 |
| IT2a | f37v.1 | P | 1 | 0 | 881 | 5 |
| IT2a | f37v.2 | P | 0 | 0 | 882 | 6 |
| IT2a | f37v.3 | P | 0 | 0 | 883 | 5 |
| IT2a | f37v.4 | P | 0 | 0 | 884 | 4 |
| IT2a | f37v.5 | P | 0 | 0 | 885 | 4 |
| IT2a | f37v.6 | P | 0 | 0 | 886 | 4 |
| IT2a | f37v.7 | P | 0 | 1 | 887 | 2 |
| RF1b | f37v.1 | P | 0 | 0 | 885 | 5 |
| RF1b | f37v.2 | P | 0 | 0 | 886 | 5 |
| RF1b | f37v.3 | P | 0 | 0 | 887 | 5 |
| RF1b | f37v.4 | P | 0 | 0 | 888 | 4 |
| RF1b | f37v.5 | P | 0 | 0 | 889 | 4 |
| RF1b | f37v.6 | P | 0 | 0 | 890 | 4 |
| RF1b | f37v.7 | P | 0 | 0 | 891 | 2 |
