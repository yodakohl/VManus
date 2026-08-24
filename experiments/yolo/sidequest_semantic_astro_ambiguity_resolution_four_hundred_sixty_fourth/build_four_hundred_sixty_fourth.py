#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third"
GROUPS = BASE / "FOUR_HUNDRED_SIXTY_THIRD_395_ASTRO_GROUP_COMMON_ROOTS.tsv"
LEDGER = BASE / "FOUR_HUNDRED_SIXTY_THIRD_776_GROUP_TEN_PAGE_LEDGER.tsv"
COMPONENTS = BASE / "FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(GROUPS)
    values = {row["component"]: row["value_de"] for row in read(COMPONENTS)}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_locus[row["locus"]].append(row)

    decisions = []
    chosen_by_serial: dict[str, tuple[str, str]] = {}
    for row in source:
        if row["transfer_status"] != "AMBIGUOUS_COMPONENT_SEQUENCE":
            continue
        rows = by_locus[row["locus"]]
        position = rows.index(row) + 1
        total = len(rows)
        alternatives = row["parse_alternatives"].split(" || ")
        serial = int(row["group_serial"])
        if serial in {18, 243, 252}:
            chosen = next(alt for alt in alternatives if "CHD" in alt)
            rule = "KNOWN_CHD_MACRO_BEATS_CH_PLUS_ENDPOINT"
        elif serial in {143, 335, 353}:
            chosen = next(alt for alt in alternatives if alt.startswith("OT+"))
            rule = "KNOWN_OT_SEQUENCE_MARKER_BEATS_O_SPLIT"
        elif serial in {191, 193, 212}:
            chosen = next(alt for alt in alternatives if "HO" in alt)
            rule = "PANEL_HEADER_PREFERS_HO_ENTRY_MACRO"
        elif position == total:
            chosen = next(alt for alt in alternatives if alt.endswith("+DY"))
            rule = "LOCUS_FINAL_OR_SINGLETON_TAKES_LICENSED_ENDPOINT"
        else:
            chosen = next(alt for alt in alternatives if alt.endswith("+Y"))
            rule = "LOCUS_INTERNAL_GROUP_KEEPS_CURRENT_ITEM"
        atomic = " + ".join(values[part] for part in chosen.split("+"))
        chosen_by_serial[row["group_serial"]] = (chosen, atomic)
        decisions.append({
            "decision_order": len(decisions) + 1,
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "position_in_locus": position,
            "groups_in_locus": total,
            "surface": row["surface"],
            "parse_alternatives": row["parse_alternatives"],
            "selected_parse": chosen,
            "selected_atomic_value_de": atomic,
            "selection_rule": rule,
            "working_confidence": "MEDIUM" if total == 1 else "MEDIUM_HIGH",
        })
    write("FOUR_HUNDRED_SIXTY_FOURTH_41_ASTRO_AMBIGUITY_DECISIONS.tsv", decisions)

    groups = []
    for row in source:
        out = dict(row)
        if row["group_serial"] in chosen_by_serial:
            chosen, atomic = chosen_by_serial[row["group_serial"]]
            out["selected_component_parse"] = chosen
            out["atomic_common_root_value_de"] = atomic
            out["transfer_status"] = "POSITION_RESOLVED_COMPONENT_SEQUENCE"
            decision = next(item for item in decisions if item["group_serial"] == row["group_serial"])
            out["ambiguity_resolution_rule"] = decision["selection_rule"]
        else:
            out["ambiguity_resolution_rule"] = "NOT_REQUIRED"
        groups.append(out)
    write("FOUR_HUNDRED_SIXTY_FOURTH_395_ASTRO_GROUP_RESOLVED.tsv", groups)

    resolved_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        resolved_by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in resolved_by_locus.items():
        local = sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows)
        status = "LOCAL_ONLY" if local == len(rows) else "MIXED_LOCAL_AND_RESOLVED" if local else "FULLY_RESOLVED"
        loci.append({
            "locus_row": len(loci) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "local_namespace": rows[0]["local_namespace"],
            "groups": len(rows),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "resolved_atomic_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "resolved_groups": sum(row["transfer_status"] != "ASTRO_LOCAL_LABEL" for row in rows),
            "local_groups": local,
            "locus_resolution_status": status,
            "orientation": "UNSPECIFIED",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_FOURTH_142_ASTRO_LOCUS_RESOLVED.tsv", loci)

    ledger = []
    group_by_serial = {int(row["group_serial"]): row for row in groups}
    for row in read(LEDGER):
        out = dict(row)
        if row["domain"] == "ASTRO":
            serial = int(row["unified_id"].split(":")[1])
            group = group_by_serial[serial]
            out["formal_parse"] = group["selected_component_parse"]
            out["atomic_default_de"] = group["atomic_common_root_value_de"]
            out["context_expansion_de"] = group["atomic_common_root_value_de"]
            out["interpretation_status"] = group["transfer_status"]
        ledger.append(out)
    write("FOUR_HUNDRED_SIXTY_FOURTH_776_GROUP_RESOLVED_LEDGER.tsv", ledger)

    summaries = []
    for diagram in ("A1", "A2", "A3"):
        rows = [row for row in groups if row["diagram_id"] == diagram]
        summaries.append({
            "diagram_id": diagram,
            "page": rows[0]["page"],
            "groups": len(rows),
            "exact_full_card": sum(row["transfer_status"] == "EXACT_PROSE_SURFACE" for row in rows),
            "unique_components": sum(row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE" for row in rows),
            "position_resolved_components": sum(row["transfer_status"] == "POSITION_RESOLVED_COMPONENT_SEQUENCE" for row in rows),
            "local_labels": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows),
            "loci": len({row["locus"] for row in rows}),
        })
    write("FOUR_HUNDRED_SIXTY_FOURTH_THREE_ASTRO_SUMMARY.tsv", summaries)

    md = ["# Resolved Astro workshop reading", ""]
    for diagram in ("A1", "A2", "A3"):
        md.extend([f"## {diagram}", ""])
        for row in loci:
            if row["diagram_id"] == diagram:
                md.append(f"- **{row['locus']}** ({row['locus_resolution_status']}): {row['resolved_atomic_reading_de']}")
        md.append("")
    (HERE / "FOUR_HUNDRED_SIXTY_FOURTH_RESOLVED_ASTRO_READING.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "ambiguous_input_groups": len(decisions),
        "position_resolved_groups": sum(row["transfer_status"] == "POSITION_RESOLVED_COMPONENT_SEQUENCE" for row in groups),
        "transferred_or_resolved_groups": sum(row["transfer_status"] != "ASTRO_LOCAL_LABEL" for row in groups),
        "local_label_groups": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in groups),
        "fully_resolved_loci": sum(row["locus_resolution_status"] == "FULLY_RESOLVED" for row in loci),
        "mixed_loci": sum(row["locus_resolution_status"] == "MIXED_LOCAL_AND_RESOLVED" for row in loci),
        "local_only_loci": sum(row["locus_resolution_status"] == "LOCAL_ONLY" for row in loci),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
