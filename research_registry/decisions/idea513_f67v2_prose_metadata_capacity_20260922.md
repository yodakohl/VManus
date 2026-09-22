# IDEA513: vollständige f67v2-Prosametadaten vor Inhaltszugriff

Eingefroren 2026-09-22 15:40:11 UTC. Nur Metadaten; keine Rohwörter/Bilder/Modelle geöffnet.

**Entscheidung: STOP_RAW513_PARAGRAPH_CAP_EXCEEDED.** Ganze native Prosa ist vorhanden: ZL und IT besitzen jeweils vier vollständige Absätze. RAW513 begrenzt das gesamte nominierte Set auf höchstens drei. Es wird kein Absatz entfernt, kein Grenzwert erhöht und kein Ersatzblatt gewählt.

| Ganze Einheit | ZL-Gruppen | IT-Gruppen | RF |
|---|---:|---:|---|
| f67v2.3–4 | 11 | 11 | Zeilen vorhanden, native Absatzgrenzen fehlen |
| f67v2.5–6 | 6 | 7 | Zeilen vorhanden, native Absatzgrenzen fehlen |
| f67v2.7–8 | 8 | 8 | Zeilen vorhanden, native Absatzgrenzen fehlen |
| f67v2.9–10 | 9 | 10 | Zeilen vorhanden, native Absatzgrenzen fehlen |
| Gesamtes Prosa-Set | 34 | 36 | 34 Gruppen in acht P-Zeilen, kein eigener vollständig begrenzter Absatz |

Jeder ZL-/IT-Absatz beginnt auf der ersten genannten Zeile mit paragraph_start=1 und endet auf der zweiten mit paragraph_end=1. RF hat für alle acht P-Zeilen beide Flags0. Fehlende RF-Absatzgrenzen sind keine fehlenden RF-Zeilen. Die 250-Gruppen-Grenze würde eingehalten; neue Worttypen/70-Werte-Grenze wurden nicht gelesen oder gezählt, weil die Vier-Absatz-Grenze bereits entscheidet.

## Quelle und Zulassung

Primäre wörtliche Selektormetadaten: `experiments/semantic_assumptions/results/source_separator_transcription.tsv`, SHA256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`. Alle Leser werden über den exakten page-Selektor `f67v2` erfasst. Ausgegeben wurden ausschließlich `edition,page,locus,kind,paragraph_start,paragraph_end,source_row_index,source_group_count`; je Wortgruppe wiederholte Zeilenmetadaten wurden identisch dedupliziert. Keine Wortspalte, kein Entityinhalt, kein Separatorinhalt wurde ausgegeben.

Guard-Rezept: `./vmanus-exp query-tsv experiments/semantic_assumptions/results/source_separator_transcription.tsv --selector page --allow f67v2 --columns edition,page,locus,kind,paragraph_start,paragraph_end,source_row_index,source_group_count`. GUARD_STATS {"selected": 184, "skipped_forbidden": 2122, "skipped_not_allowed": 113164}

Die aktuelle zentrale Textliste `experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv` enthält keine wörtliche f67v2-Zeile; auch die überprüften wörtlichen f67v/f67v1-Aliasse hatten keinen Treffer. Daraus folgt hier nur fehlende direkte Listenbindung, keine globale Behauptung über sämtliche historischen Kontext-/Aliaszulassungen. Eine weitere Zulassungsrecherche wurde nach dem unabhängigen Absatzkostenstopp nicht fortgesetzt. Die gegenwärtige Aufgabe autorisierte diese Metadatenprüfung, keinen Inhaltszugriff.

Die alte native Prämisse liegt in `experiments/semantic_assumptions/results/f67v2_rosettes_native_visual_scaffold.json` und gleichnamigem `_report.md`: zentrale Struktur, vier angefügte Achsenstrukturen, vier abgesetzte einwärts gerichtete Eckgruppen. Die Quelldatei nennt Yale-Canvas1006195, Label67v, Bildhash4799e8ebd8d968ea28dae919cfb86065566662b4e77c8b429d12e3e6e685638b. Diese Bildprovenienz ist keine neue Bildöffnung und ersetzt keine aktuelle Textzulassung.

RAW513 sowie der verlinkte native Bericht und GDT827 WORKING_THEORY wurden gelesen; fehlende Wort-Endpunktbindung bleibt bestehen. Dieser Stopp widerlegt weder Passage/Facing noch die Existenz eines vollständigen Vier-Absatz-Entwurfs; er beendet das konkrete vorgelegte Drei-Absatz-Rezept vor Wortinhalt.

## Vollständiges eingefrorenes Metadateninventar

| Leser | Locus | kind | start | end | Quellzeile | Gruppen |
|---|---|---|---:|---:|---:|---:|
| ZL3b | f67v2.1 | L | 0 | 0 | 1742 | 1 |
| ZL3b | f67v2.2 | L | 0 | 0 | 1743 | 1 |
| ZL3b | f67v2.3 | P | 1 | 0 | 1744 | 7 |
| ZL3b | f67v2.4 | P | 0 | 1 | 1745 | 4 |
| ZL3b | f67v2.5 | P | 1 | 0 | 1746 | 3 |
| ZL3b | f67v2.6 | P | 0 | 1 | 1747 | 3 |
| ZL3b | f67v2.7 | P | 1 | 0 | 1748 | 4 |
| ZL3b | f67v2.8 | P | 0 | 1 | 1749 | 4 |
| ZL3b | f67v2.9 | P | 1 | 0 | 1750 | 4 |
| ZL3b | f67v2.10 | P | 0 | 1 | 1751 | 5 |
| ZL3b | f67v2.11 | R | 0 | 0 | 1752 | 2 |
| ZL3b | f67v2.12 | R | 0 | 0 | 1753 | 2 |
| ZL3b | f67v2.13 | R | 0 | 0 | 1754 | 2 |
| ZL3b | f67v2.14 | R | 0 | 0 | 1755 | 3 |
| ZL3b | f67v2.15 | R | 0 | 0 | 1756 | 3 |
| ZL3b | f67v2.16 | R | 0 | 0 | 1757 | 3 |
| ZL3b | f67v2.17 | R | 0 | 0 | 1758 | 2 |
| ZL3b | f67v2.18 | R | 0 | 0 | 1759 | 2 |
| ZL3b | f67v2.19 | L | 0 | 0 | 1760 | 2 |
| ZL3b | f67v2.20 | L | 0 | 0 | 1761 | 2 |
| ZL3b | f67v2.21 | L | 0 | 0 | 1762 | 1 |
| ZL3b | f67v2.22 | L | 0 | 0 | 1763 | 2 |
| IT2a | f67v2.2 | L | 0 | 0 | 1738 | 1 |
| IT2a | f67v2.3 | P | 1 | 0 | 1739 | 7 |
| IT2a | f67v2.4 | P | 0 | 1 | 1740 | 4 |
| IT2a | f67v2.5 | P | 1 | 0 | 1741 | 3 |
| IT2a | f67v2.6 | P | 0 | 1 | 1742 | 4 |
| IT2a | f67v2.7 | P | 1 | 0 | 1743 | 4 |
| IT2a | f67v2.8 | P | 0 | 1 | 1744 | 4 |
| IT2a | f67v2.9 | P | 1 | 0 | 1745 | 5 |
| IT2a | f67v2.10 | P | 0 | 1 | 1746 | 5 |
| IT2a | f67v2.11 | R | 0 | 0 | 1747 | 2 |
| IT2a | f67v2.12 | R | 0 | 0 | 1748 | 3 |
| IT2a | f67v2.13 | R | 0 | 0 | 1749 | 2 |
| IT2a | f67v2.14 | R | 0 | 0 | 1750 | 3 |
| IT2a | f67v2.15 | R | 0 | 0 | 1751 | 3 |
| IT2a | f67v2.16 | R | 0 | 0 | 1752 | 2 |
| IT2a | f67v2.17 | R | 0 | 0 | 1753 | 2 |
| IT2a | f67v2.18 | R | 0 | 0 | 1754 | 2 |
| IT2a | f67v2.19 | L | 0 | 0 | 1755 | 2 |
| IT2a | f67v2.20 | L | 0 | 0 | 1756 | 2 |
| IT2a | f67v2.22 | L | 0 | 0 | 1757 | 1 |
| RF1b | f67v2.1 | L | 0 | 0 | 1742 | 1 |
| RF1b | f67v2.2 | L | 0 | 0 | 1743 | 1 |
| RF1b | f67v2.3 | P | 0 | 0 | 1744 | 7 |
| RF1b | f67v2.4 | P | 0 | 0 | 1745 | 4 |
| RF1b | f67v2.5 | P | 0 | 0 | 1746 | 3 |
| RF1b | f67v2.6 | P | 0 | 0 | 1747 | 3 |
| RF1b | f67v2.7 | P | 0 | 0 | 1748 | 4 |
| RF1b | f67v2.8 | P | 0 | 0 | 1749 | 4 |
| RF1b | f67v2.9 | P | 0 | 0 | 1750 | 4 |
| RF1b | f67v2.10 | P | 0 | 0 | 1751 | 5 |
| RF1b | f67v2.11 | R | 0 | 0 | 1752 | 2 |
| RF1b | f67v2.12 | R | 0 | 0 | 1753 | 2 |
| RF1b | f67v2.13 | R | 0 | 0 | 1754 | 2 |
| RF1b | f67v2.14 | R | 0 | 0 | 1755 | 3 |
| RF1b | f67v2.15 | R | 0 | 0 | 1756 | 3 |
| RF1b | f67v2.16 | R | 0 | 0 | 1757 | 3 |
| RF1b | f67v2.17 | R | 0 | 0 | 1758 | 2 |
| RF1b | f67v2.18 | R | 0 | 0 | 1759 | 2 |
| RF1b | f67v2.19 | L | 0 | 0 | 1760 | 2 |
| RF1b | f67v2.20 | L | 0 | 0 | 1761 | 2 |
| RF1b | f67v2.21 | L | 0 | 0 | 1762 | 1 |
| RF1b | f67v2.22 | L | 0 | 0 | 1763 | 1 |
