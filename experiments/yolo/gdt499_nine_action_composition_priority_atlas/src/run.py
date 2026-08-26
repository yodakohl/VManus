#!/usr/bin/env python3
"""Rank all 352 GDT498 compositions and expose exact whole-cell witnesses."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt499_nine_action_composition_priority_atlas"
ART = BASE / "artifacts"
G498 = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix/artifacts"
MATRIX_IN = G498 / "gdt498_495_action_frame_register_cells.tsv"
RESULT_IN = G498 / "gdt498_result.json"

RANKED_OUT = ART / "gdt499_352_ranked_compositions.tsv"
TIER_A_OUT = ART / "gdt499_165_local_multihead_compositions.tsv"
TIER_B_OUT = ART / "gdt499_88_local_single_head_compositions.tsv"
TIER_C_OUT = ART / "gdt499_49_cross_register_compositions.tsv"
TIER_D_OUT = ART / "gdt499_50_old_values_only_compositions.tsv"
LOCAL_OUT = ART / "gdt499_local_observed_support_witnesses.tsv"
CROSS_OUT = ART / "gdt499_cross_register_observed_support_witnesses.tsv"
REPEATED_OUT = ART / "gdt499_repeated_action_compositions.tsv"
FRAME_OUT = ART / "gdt499_11_frame_priority_coverage.tsv"
ACTION_OUT = ART / "gdt499_9_action_priority_coverage.tsv"
READABLE_OUT = ART / "GDT499_NINE_ACTION_COMPOSITION_PRIORITY_ATLAS.md"
RESULT_OUT = ART / "gdt499_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
TIER_ORDER = {
    "A_LOCAL_MULTIHEAD": 0,
    "B_LOCAL_SINGLE_HEAD": 1,
    "C_CROSS_REGISTER_SAME_ACTION": 2,
    "D_OLD_VALUES_ONLY": 3,
}
STATUS = "ONE_HUNDRED_SIXTY_FIVE_PRODUCTIVE_MULTIHEAD_COMPOSITIONS__FIFTY_OLD_VALUES_ONLY_FRONTIER"
GUARD = "COMPOSED_WORKING_RETAINED__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def union_pages(rows: list[dict[str, str]]) -> list[str]:
    pages: set[str] = set()
    for row in rows:
        pages.update(page for page in row["observed_pages"].split("|") if page and page != "NONE")
    return sorted(pages, key=page_key)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _matrix_fields, matrix = read_tsv(MATRIX_IN)
    source_result = json.loads(RESULT_IN.read_text(encoding="utf-8"))
    if len(matrix) != 495 or source_result.get("composed_cells") != 352:
        raise ValueError("GDT498 matrix drift")
    observed = [row for row in matrix if row["evidence_status"] == "OBSERVED_CLAUSE"]
    composed = [row for row in matrix if row["evidence_status"] == "COMPOSED_WORKING"]
    if (len(observed), len(composed)) != (143, 352):
        raise ValueError("GDT498 evidence split drift")

    observed_by_frame_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    observed_by_frame_action: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in observed:
        observed_by_frame_register[(row["frozen_frame"], row["register"])].append(row)
        observed_by_frame_action[(row["frozen_frame"], row["action_root"])].append(row)

    draft: list[dict[str, object]] = []
    local_witness_rows: list[dict[str, object]] = []
    cross_witness_rows: list[dict[str, object]] = []
    for source in composed:
        local = [
            row for row in observed_by_frame_register[(source["frozen_frame"], source["register"])]
            if row["action_root"] != source["action_root"]
        ]
        cross = [
            row for row in observed_by_frame_action[(source["frozen_frame"], source["action_root"])]
            if row["register"] != source["register"]
        ]
        if len(local) >= 2:
            tier = "A_LOCAL_MULTIHEAD"
            reason = "TWO_OR_MORE_EXACT_OTHER_ACTION_CELLS_SAME_FRAME_REGISTER"
        elif len(local) == 1:
            tier = "B_LOCAL_SINGLE_HEAD"
            reason = "ONE_EXACT_OTHER_ACTION_CELL_SAME_FRAME_REGISTER"
        elif cross:
            tier = "C_CROSS_REGISTER_SAME_ACTION"
            reason = "EXACT_SAME_ACTION_FRAME_IN_OTHER_REGISTER"
        else:
            tier = "D_OLD_VALUES_ONLY"
            reason = "ONLY_COMPONENT_VALUE_CELLS_OBSERVED"
        expected_map = {
            "COMPOSED_MULTIHEAD_SAME_REGISTER": "A_LOCAL_MULTIHEAD",
            "COMPOSED_SINGLE_HEAD_SAME_REGISTER": "B_LOCAL_SINGLE_HEAD",
            "COMPOSED_CROSS_REGISTER_SAME_ACTION": "C_CROSS_REGISTER_SAME_ACTION",
            "COMPOSED_OLD_VALUES_ONLY": "D_OLD_VALUES_ONLY",
        }
        if expected_map[source["composition_support_class"]] != tier:
            raise ValueError(f"support-class drift: {source['matrix_cell_id']}")

        tokens = source["action_recipe"].split("+")
        action_tokens = [token for token in tokens if token in ACTION_ROOTS]
        repeated_actions = sorted(root for root, count in Counter(action_tokens).items() if count > 1)
        local_pages = union_pages(local)
        cross_pages = union_pages(cross)
        draft.append(
            {
                "global_priority_rank": 0,
                "tier_rank": 0,
                "priority_tier": tier,
                "priority_reason": reason,
                "source_matrix_cell_id": source["matrix_cell_id"],
                "frozen_frame": source["frozen_frame"],
                "action_root": source["action_root"],
                "action_recipe": source["action_recipe"],
                "register": source["register"],
                "portable_component_trace_de": source["portable_component_trace_de"],
                "owner_local_component_trace_de": source["owner_local_component_trace_de"],
                "current_default_phrase_de": source["current_default_phrase_de"],
                "state_requirement": source["state_requirement"],
                "editorial_change_type": source["editorial_change_type"],
                "component_count": len(tokens),
                "action_component_count": len(action_tokens),
                "repeated_action_root_count": len(repeated_actions),
                "repeated_action_roots": "|".join(repeated_actions) or "NONE",
                "repeated_action_fluency_warning": "YES" if repeated_actions else "NO",
                "local_observed_head_count": len(local),
                "local_observed_heads": "|".join(row["action_root"] for row in local) or "NONE",
                "local_observed_event_count": sum(int(row["observed_event_count"]) for row in local),
                "local_observed_clause_form_count": sum(int(row["observed_clause_form_count"]) for row in local),
                "local_observed_page_count": len(local_pages),
                "local_observed_pages": "|".join(local_pages) or "NONE",
                "cross_register_observed_cell_count": len(cross),
                "cross_register_observed_registers": "|".join(row["register"] for row in cross) or "NONE",
                "cross_register_observed_event_count": sum(int(row["observed_event_count"]) for row in cross),
                "cross_register_observed_page_count": len(cross_pages),
                "cross_register_observed_pages": "|".join(cross_pages) or "NONE",
                "all_component_value_cells_old": source["all_component_value_cells_old"],
                "evidence_status_retained": source["evidence_status"],
                "working_root_meaning_changed": "NO",
                "surface_prediction_made": "NO",
                "occurrence_prediction_made": "NO",
                "guard": GUARD,
            }
        )
        target_id = source["matrix_cell_id"]
        for witness in local:
            local_witness_rows.append(
                {
                    "local_witness_id": f"G499-L{len(local_witness_rows) + 1:04d}",
                    "target_matrix_cell_id": target_id,
                    "target_frame": source["frozen_frame"],
                    "target_action_root": source["action_root"],
                    "target_action_recipe": source["action_recipe"],
                    "target_register": source["register"],
                    "observed_matrix_cell_id": witness["matrix_cell_id"],
                    "observed_action_root": witness["action_root"],
                    "observed_action_recipe": witness["action_recipe"],
                    "observed_event_count": witness["observed_event_count"],
                    "observed_clause_form_count": witness["observed_clause_form_count"],
                    "observed_pages": witness["observed_pages"],
                    "observed_event_ids": witness["observed_event_ids"],
                    "observed_selected_phrase_de": witness["current_default_phrase_de"],
                    "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                    "exact_same_frame_and_register": "YES",
                }
            )
        for witness in cross:
            cross_witness_rows.append(
                {
                    "cross_witness_id": f"G499-X{len(cross_witness_rows) + 1:04d}",
                    "target_matrix_cell_id": target_id,
                    "target_frame": source["frozen_frame"],
                    "target_action_root": source["action_root"],
                    "target_action_recipe": source["action_recipe"],
                    "target_register": source["register"],
                    "observed_matrix_cell_id": witness["matrix_cell_id"],
                    "observed_register": witness["register"],
                    "observed_event_count": witness["observed_event_count"],
                    "observed_clause_form_count": witness["observed_clause_form_count"],
                    "observed_pages": witness["observed_pages"],
                    "observed_event_ids": witness["observed_event_ids"],
                    "observed_selected_phrase_de": witness["current_default_phrase_de"],
                    "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                    "exact_same_action_and_frame": "YES",
                }
            )

    ranked = sorted(
        draft,
        key=lambda row: (
            TIER_ORDER[str(row["priority_tier"])],
            -int(row["local_observed_head_count"]),
            -int(row["local_observed_event_count"]),
            -int(row["cross_register_observed_cell_count"]),
            -int(row["cross_register_observed_event_count"]),
            int(row["repeated_action_root_count"]),
            int(row["component_count"]),
            str(row["action_recipe"]),
            str(row["register"]),
        ),
    )
    tier_counter: Counter[str] = Counter()
    for rank, row in enumerate(ranked, start=1):
        tier_counter[str(row["priority_tier"])] += 1
        row["global_priority_rank"] = rank
        row["tier_rank"] = tier_counter[str(row["priority_tier"])]

    tier_a = [row for row in ranked if row["priority_tier"] == "A_LOCAL_MULTIHEAD"]
    tier_b = [row for row in ranked if row["priority_tier"] == "B_LOCAL_SINGLE_HEAD"]
    tier_c = [row for row in ranked if row["priority_tier"] == "C_CROSS_REGISTER_SAME_ACTION"]
    tier_d = [row for row in ranked if row["priority_tier"] == "D_OLD_VALUES_ONLY"]
    repeated = [row for row in ranked if row["repeated_action_fluency_warning"] == "YES"]

    def summarize(axis: str) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for value in sorted({str(row[axis]) for row in ranked}):
            group = [row for row in ranked if row[axis] == value]
            tiers = Counter(str(row["priority_tier"]) for row in group)
            output.append(
                {
                    axis: value,
                    "composed_cell_count": len(group),
                    "tier_a_multihead_count": tiers["A_LOCAL_MULTIHEAD"],
                    "tier_b_single_head_count": tiers["B_LOCAL_SINGLE_HEAD"],
                    "tier_c_cross_register_count": tiers["C_CROSS_REGISTER_SAME_ACTION"],
                    "tier_d_old_values_only_count": tiers["D_OLD_VALUES_ONLY"],
                    "local_witness_cell_count": sum(int(row["local_observed_head_count"]) for row in group),
                    "local_witness_event_count": sum(int(row["local_observed_event_count"]) for row in group),
                    "cross_witness_cell_count": sum(int(row["cross_register_observed_cell_count"]) for row in group),
                    "cross_witness_event_count": sum(int(row["cross_register_observed_event_count"]) for row in group),
                    "repeated_action_warning_count": sum(row["repeated_action_fluency_warning"] == "YES" for row in group),
                    "all_composed_labels_retained": "YES",
                }
            )
        return output

    frame_rows = summarize("frozen_frame")
    action_rows = summarize("action_root")
    write_tsv(RANKED_OUT, ranked)
    write_tsv(TIER_A_OUT, tier_a)
    write_tsv(TIER_B_OUT, tier_b)
    write_tsv(TIER_C_OUT, tier_c)
    write_tsv(TIER_D_OUT, tier_d)
    write_tsv(LOCAL_OUT, local_witness_rows)
    write_tsv(CROSS_OUT, cross_witness_rows)
    write_tsv(REPEATED_OUT, repeated)
    write_tsv(FRAME_OUT, frame_rows)
    write_tsv(ACTION_OUT, action_rows)

    lines = [
        "# GDT499 — Priorität der 352 Neun-Handlungs-Kompositionen",
        "",
        f"Status: `{STATUS}`",
        "",
        "Die vier GDT498-Stützklassen bleiben unverändert. Innerhalb jeder Klasse",
        "zählen zuerst mehr lokale beobachtete Köpfe/Events, dann mehr",
        "registerübergreifende Zielhandlungszellen; Wiederholungs- und Komplexitäts-",
        "merkmale brechen nur nachgeordnete Gleichstände.",
        "",
        f"- Tier A, lokale Mehrkopffamilie: **{len(tier_a)}**;",
        f"- Tier B, ein lokaler Kopf: **{len(tier_b)}**;",
        f"- Tier C, nur gleiche Handlung in anderem Register: **{len(tier_c)}**;",
        f"- Tier D, nur alte Einzelwerte: **{len(tier_d)}**;",
        f"- mechanisch wiederholte Handlungswurzeln: **{len(repeated)}**.",
        "",
        "## Die 165 produktiven Hauptkarten",
        "",
        "| Rang | Rezept | Register | Arbeitsdefault | lokale Köpfe/Events | andere Register/Events | Wiederholung |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for row in tier_a:
        lines.append(
            f'| {row["global_priority_rank"]} | `{row["action_recipe"]}` | {row["register"]} | '
            f'{row["current_default_phrase_de"]} | {row["local_observed_head_count"]}/{row["local_observed_event_count"]} '
            f'(`{row["local_observed_heads"]}`) | {row["cross_register_observed_cell_count"]}/{row["cross_register_observed_event_count"]} | '
            f'{row["repeated_action_fluency_warning"]} |'
        )
    lines.extend(["", "## Vollständige Rangfolge", "", "| Rang | Tier | Rezept | Register | Default | lokale Köpfe | cross |", "|---:|---|---|---|---|---:|---:|"])
    for row in ranked:
        lines.append(
            f'| {row["global_priority_rank"]} | `{row["priority_tier"]}` | `{row["action_recipe"]}` | '
            f'{row["register"]} | {row["current_default_phrase_de"]} | {row["local_observed_head_count"]} | '
            f'{row["cross_register_observed_cell_count"]} |'
        )
    lines.extend(["", f'`{GUARD}`', ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    result = {
        "status": STATUS,
        "ranked_compositions": len(ranked),
        "tier_a_local_multihead": len(tier_a),
        "tier_b_local_single_head": len(tier_b),
        "tier_c_cross_register_same_action": len(tier_c),
        "tier_d_old_values_only": len(tier_d),
        "local_observed_support_witnesses": len(local_witness_rows),
        "local_observed_support_events": sum(int(row["observed_event_count"]) for row in local_witness_rows),
        "cross_register_observed_support_witnesses": len(cross_witness_rows),
        "cross_register_observed_support_events": sum(int(row["observed_event_count"]) for row in cross_witness_rows),
        "tier_a_local_support_witnesses": sum(int(row["local_observed_head_count"]) for row in tier_a),
        "tier_a_local_support_events": sum(int(row["local_observed_event_count"]) for row in tier_a),
        "repeated_action_compositions": len(repeated),
        "repeated_action_tier_a": sum(row["priority_tier"] == "A_LOCAL_MULTIHEAD" for row in repeated),
        "repeated_action_tier_d": sum(row["priority_tier"] == "D_OLD_VALUES_ONLY" for row in repeated),
        "all_old_value_cells_retained": sum(row["all_component_value_cells_old"] == "YES" for row in ranked),
        "composed_labels_retained": sum(row["evidence_status_retained"] == "COMPOSED_WORKING" for row in ranked),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in ranked),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in ranked),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in ranked),
        "frame_count": len(frame_rows),
        "action_count": len(action_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
