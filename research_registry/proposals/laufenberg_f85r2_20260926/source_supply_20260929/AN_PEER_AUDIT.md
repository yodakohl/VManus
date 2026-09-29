# AN peer audit: predecessor metadata and scope

Audit started 2026-09-29 17:31:52 UTC; completed within the 15-minute bound. This is a read-only metadata and report audit, not an event extraction or scientific reanalysis.

## Findings

GDT1074 and GDT1075 do not identify paragraph membership for each pX/yX event. The fixed GDT1074 event artifact has columns `base`, `edition`, `form`, `lead`, `locus`, `physical_folio`, `right_separator`, `status`, and `physical_paragraph_start`. GDT1075's fixed event artifact has `base`, `edition`, `lead`, `form`, `locus`, `folio`, `start`, `section`, `hand`, and `currier`. `physical_paragraph_start` / `start` is an event-locus flag (1, 0, or NA in the GDT1074 output), not a paragraph identifier. The artifacts therefore cannot establish that a particular pX and yX belong to the same paragraph or that pX precedes yX within it.

This limitation is material even when both starts are 0: their paragraph starts may be earlier loci not represented in the selected p/y event table. The rows also do not provide all intermediate paragraph-start loci needed to walk boundaries between a p event and later y event. If either flag is NA, there is no projected flag at that event. Folio equality alone cannot supply paragraph equality.

For RF1b, GDT1074 assigns the projected `physical_paragraph_start` only where ZL3b and IT2a have matching `paragraph_start` values in {0,1}; otherwise that locus has no consensus entry and the event receives NA. The report states that this is projected physical metadata and that original RF metadata remains unscorable. A shared projected 0 only says that the two source readings did not mark that locus as a start. It does not assert the absence of an unobserved boundary elsewhere, or identify a paragraph. Thus these projected flags cannot establish RF paragraph equality without making an unsupported assumption about missing boundaries.

GDT920 is a relevant methodological predecessor but did not execute AN's exact scope census. It constructs complete paragraph frames from start/end flags, retains frame locus lists, and compares fixed paragraph-initial p/f header anchors with mapped k/t words in their own paragraph bodies against exchangeable bodies. Its registered and reported scope is the p/f-to-k/t whole-form bridge. It does not census fixed pX/yX same-base, same-physical-folio pairs for ordered occurrence in one paragraph. Its result (`BRIDGE_NOT_ESTABLISHED`) therefore neither answers nor supersedes AN's narrower scope question.

## Sources inspected

- `VOYNICH_CURRENT_ROUTE.md` (read first; live route).
- `research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/AN_DECISION.md`.
- `experiments/yolo/gdt1074_physical_paragraph_pair_robustness/REPORT.md` (complete report).
- `experiments/yolo/gdt1074_physical_paragraph_pair_robustness/artifacts/README.md` and `artifacts/EVENTS.tsv` header only.
- `experiments/yolo/gdt1074_physical_paragraph_pair_robustness/src/run.py` (relevant metadata and projection logic, especially lines 18–20, 45–71).
- `experiments/yolo/gdt1075_py_section_hand_confound/REPORT.md` (complete report).
- `experiments/yolo/gdt1075_py_section_hand_confound/artifacts/README.md` and `artifacts/EVENTS.tsv` header only.
- `experiments/yolo/gdt1075_py_section_hand_confound/src/run.py` (fixed-event propagation and start-flag grouping, especially lines 15–18, 46–56, 57–83).
- `experiments/yolo/gdt920_paragraph_gallows_wholeform_bridge/REPORT.md` (complete report).
- `experiments/yolo/gdt920_paragraph_gallows_wholeform_bridge/METHOD.md` (complete scope/method description) and `src/run.py` (paragraph frame and census logic, especially lines 11–42, 60–75).

## Limits

No raw target/source TSV rows were accessed or parsed; no pair counts were extracted. I did not open new pages, images, network sources, sealed data, or reserved data. I did not write outside this audit note, modify globals, rank candidates, infer glossary meanings, or add an experiment or registry entry. Root remains responsible for the authorized fixed-event extraction and any downstream decision.

## Access and reconstruction distinction for the planned follow-up

The missing paragraph IDs in the fixed event tables do not by themselves prohibit the requested census: AN_DECISION explicitly permits the owned underlying receipts while prohibiting line-number-only reconstruction and acquiring more pages. A selector-first query restricted to the 13 frozen side selectors and returning only structural metadata (including ordered loci/row indices and complete start/end boundary fields for first/last groups) is a narrower read of already-admitted source, not new page or text-content access. It can support paragraph membership only if it supplies the full intervening sequence needed to establish that no boundary or unknown interval separates the events. Preserve absent and disagreeing metadata as unknown; do not bridge over it. ZL3b/IT2a agreement can define the physical segmentation under the stated rule. RF1b remains a dependent projection from that consensus, so any RF equality label must be explicitly conditional on the source projection and complete boundary coverage; it is not an independent RF paragraph observation. The flags alone, without that ordered boundary census, remain insufficient.
