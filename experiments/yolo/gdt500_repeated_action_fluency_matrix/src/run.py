#!/usr/bin/env python3
"""Build a complete 495-cell phrase deck with reversible repeated-action fluency."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix"
ART = BASE / "artifacts"
G498 = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix/artifacts"
G499 = ROOT / "experiments/yolo/gdt499_nine_action_composition_priority_atlas/artifacts"

MATRIX_IN = G498 / "gdt498_495_action_frame_register_cells.tsv"
RANKED_IN = G499 / "gdt499_352_ranked_compositions.tsv"
REPEATED_IN = G499 / "gdt499_repeated_action_compositions.tsv"
MATRIX_OUT = ART / "gdt500_495_current_fluent_cells.tsv"
EDITED_OUT = ART / "gdt500_15_repeated_action_fluency_cards.tsv"
UNCHANGED_OUT = ART / "gdt500_480_unchanged_cells.tsv"
OBSERVED_OUT = ART / "gdt500_143_observed_phrase_retention.tsv"
COMPOSED_OUT = ART / "gdt500_352_composed_current_defaults.tsv"
REGISTER_OUT = ART / "gdt500_5_register_fluency_coverage.tsv"
RULE_OUT = ART / "gdt500_3_compression_rule_coverage.tsv"
READABLE_OUT = ART / "GDT500_COMPLETE_495_FLUENT_DEFAULT_DECK.md"
RESULT_OUT = ART / "gdt500_result.json"

STATUS = "FIFTEEN_REPEATED_ACTIONS_FLUENT_AND_REVERSIBLE__FOUR_HUNDRED_EIGHTY_UNCHANGED"
GUARD = "EDITORIAL_FLUENCY_ONLY__TWO_ACTION_SLOTS_RETAINED__NO_MEANING_OR_EVIDENCE_CHANGE"
RULE_BY_RECIPE = {
    "CH+CH": "CH_CH_ACTIVE_ARGUMENT_TO_ZWEIMAL",
    "CHD+CHD+Y": "CHD_CHD_POST_TO_ZWEIMAL",
    "CH+CH+E+Y": "CH_CH_GRADE_POST_TO_ZWEIMAL",
}


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


def lower_initial(text: str) -> str:
    return text[:1].lower() + text[1:]


def parse_repeated_phrase(source: dict[str, str]) -> tuple[str, str, str]:
    phrase = source["current_default_phrase_de"]
    recipe = source["action_recipe"]
    if recipe == "CH+CH+E+Y":
        tail = "; auf Grad I."
    else:
        tail = "."
    if not phrase.endswith(tail):
        raise ValueError(f"unexpected repeated-action tail: {source['matrix_cell_id']} {phrase}")
    body = phrase[:-len(tail)]
    parts = body.split(" und ")
    if len(parts) != 2:
        raise ValueError(f"repeated phrase is not binary: {source['matrix_cell_id']} {phrase}")
    first, second = parts
    if recipe == "CH+CH":
        verb = first.split(" ", 1)[0].lower()
        separable = " auf" if first.endswith(" auf") else ""
        expected_second = f"{verb} es{separable}"
    else:
        expected_second = lower_initial(first)
    if second != expected_second:
        raise ValueError(
            f"second repeated action drift: {source['matrix_cell_id']} expected={expected_second!r} actual={second!r}"
        )
    return first, second, tail


def compress_first_clause(first: str) -> str:
    if first.endswith(" auf"):
        return first[:-4] + " zweimal auf"
    return first + " zweimal"


def expand_from_segments(first: str, second: str, tail: str) -> str:
    return f"{first} und {second}{tail}"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _matrix_fields, matrix = read_tsv(MATRIX_IN)
    _ranked_fields, ranked = read_tsv(RANKED_IN)
    _repeated_fields, repeated = read_tsv(REPEATED_IN)
    if (len(matrix), len(ranked), len(repeated)) != (495, 352, 15):
        raise ValueError("GDT498/GDT499 source count drift")
    ranked_by_id = {row["source_matrix_cell_id"]: row for row in ranked}
    repeated_ids = {row["source_matrix_cell_id"] for row in repeated}
    if len(ranked_by_id) != 352 or len(repeated_ids) != 15:
        raise ValueError("source key drift")

    rows: list[dict[str, object]] = []
    for index, source in enumerate(matrix, start=1):
        source_id = source["matrix_cell_id"]
        is_edited = source_id in repeated_ids
        if is_edited:
            if source["action_recipe"] not in RULE_BY_RECIPE:
                raise ValueError(f"unknown repeated recipe: {source_id} {source['action_recipe']}")
            first, second, tail = parse_repeated_phrase(source)
            current = compress_first_clause(first) + tail
            expanded = expand_from_segments(first, second, tail)
            if expanded != source["current_default_phrase_de"]:
                raise ValueError(f"roundtrip failure: {source_id}")
            editorial_status = "REPEATED_ACTION_COMPRESSED"
            rule = RULE_BY_RECIPE[source["action_recipe"]]
            action_slot_count = 2
            repeated_root = "CHD" if source["action_recipe"].startswith("CHD") else "CH"
            repeated_count = 1
        else:
            first = second = tail = "NONE"
            current = source["current_default_phrase_de"]
            expanded = source["current_default_phrase_de"]
            editorial_status = "UNCHANGED"
            rule = "NONE"
            action_slot_count = sum(token in {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"} for token in source["action_recipe"].split("+"))
            repeated_root = "NONE"
            repeated_count = 0
        rank = ranked_by_id.get(source_id)
        rows.append({
            "current_cell_id": f"G500-M{index:03d}",
            "source_matrix_cell_id": source_id,
            "frozen_frame": source["frozen_frame"],
            "action_root": source["action_root"],
            "action_recipe": source["action_recipe"],
            "register": source["register"],
            "portable_component_trace_de": source["portable_component_trace_de"],
            "owner_local_component_trace_de": source["owner_local_component_trace_de"],
            "previous_default_phrase_de": source["current_default_phrase_de"],
            "current_default_phrase_de": current,
            "editorial_status": editorial_status,
            "compression_rule": rule,
            "action_slot_count_retained": action_slot_count,
            "repeated_action_root_count": repeated_count,
            "repeated_action_roots": repeated_root,
            "source_first_action_clause_de": first,
            "source_second_action_clause_de": second,
            "source_phrase_tail_de": tail,
            "compressed_count_marker_de": "zweimal" if is_edited else "NONE",
            "roundtrip_expanded_phrase_de": expanded,
            "exact_source_phrase_roundtrip": "YES",
            "evidence_status_retained": source["evidence_status"],
            "composition_priority_tier": rank["priority_tier"] if rank else "OBSERVED_EXACT_CELL",
            "composition_global_priority_rank": rank["global_priority_rank"] if rank else "NONE",
            "composition_support_class": source["composition_support_class"],
            "state_requirement": source["state_requirement"],
            "observed_event_count": source["observed_event_count"],
            "observed_pages": source["observed_pages"],
            "all_component_value_cells_old": source["all_component_value_cells_old"],
            "working_root_meaning_changed": "NO",
            "evidence_status_changed": "NO",
            "recipe_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    edited = [row for row in rows if row["editorial_status"] == "REPEATED_ACTION_COMPRESSED"]
    unchanged = [row for row in rows if row["editorial_status"] == "UNCHANGED"]
    observed = [row for row in rows if row["evidence_status_retained"] == "OBSERVED_CLAUSE"]
    composed = [row for row in rows if row["evidence_status_retained"] == "COMPOSED_WORKING"]
    if (len(edited), len(unchanged), len(observed), len(composed)) != (15, 480, 143, 352):
        raise ValueError("output split drift")
    write_tsv(MATRIX_OUT, rows)
    write_tsv(EDITED_OUT, edited)
    write_tsv(UNCHANGED_OUT, unchanged)
    write_tsv(OBSERVED_OUT, observed)
    write_tsv(COMPOSED_OUT, composed)

    by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_register[str(row["register"])].append(row)
    register_rows: list[dict[str, object]] = []
    for register in sorted(by_register):
        group = by_register[register]
        register_rows.append({
            "register": register,
            "cell_count": len(group),
            "observed_cell_count": sum(row["evidence_status_retained"] == "OBSERVED_CLAUSE" for row in group),
            "composed_cell_count": sum(row["evidence_status_retained"] == "COMPOSED_WORKING" for row in group),
            "edited_repeated_action_count": sum(row["editorial_status"] == "REPEATED_ACTION_COMPRESSED" for row in group),
            "unchanged_count": sum(row["editorial_status"] == "UNCHANGED" for row in group),
            "exact_roundtrip_count": sum(row["exact_source_phrase_roundtrip"] == "YES" for row in group),
            "all_component_traces_retained": "YES",
        })
    write_tsv(REGISTER_OUT, register_rows)

    by_rule: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in edited:
        by_rule[str(row["compression_rule"])].append(row)
    rule_rows: list[dict[str, object]] = []
    for rule in sorted(by_rule):
        group = by_rule[rule]
        rule_rows.append({
            "compression_rule": rule,
            "action_recipe": group[0]["action_recipe"],
            "edited_cell_count": len(group),
            "register_count": len({row["register"] for row in group}),
            "registers": "|".join(sorted(str(row["register"]) for row in group)),
            "exact_source_roundtrip_count": sum(row["exact_source_phrase_roundtrip"] == "YES" for row in group),
            "two_action_slots_retained_count": sum(int(row["action_slot_count_retained"]) == 2 for row in group),
            "zweimal_marker_count": sum(str(row["current_default_phrase_de"]).count("zweimal") == 1 for row in group),
        })
    write_tsv(RULE_OUT, rule_rows)

    lines = [
        "# GDT500 — vollständiges flüssiges 495-Zellen-Defaultdeck",
        "",
        f"Status: `{STATUS}`",
        "",
        "Alle technischen Komponenten und Evidenzklassen bleiben erhalten. Nur die",
        "fünfzehn Zellen mit zwei identischen Handlungsslots wechseln von einer",
        "mechanischen Doppelphrase zur expliziten Zählform `zweimal`.",
        "",
        "## Die fünfzehn Verdichtungen",
        "",
        "| Zelle | Rezept | Register | vorher | jetzt | Rückprojektion |",
        "|---|---|---|---|---|---|",
    ]
    for row in edited:
        lines.append(
            f'| `{row["current_cell_id"]}` | `{row["action_recipe"]}` | {row["register"]} | '
            f'{row["previous_default_phrase_de"]} | **{row["current_default_phrase_de"]}** | '
            f'{row["roundtrip_expanded_phrase_de"]} |'
        )
    lines.extend([
        "",
        "## Alle 495 aktuellen Defaults",
        "",
        "| Zelle | Evidenz | Stütze | Rezept | Register | aktueller Default | Redaktion |",
        "|---|---|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f'| `{row["current_cell_id"]}` | `{row["evidence_status_retained"]}` | '
            f'`{row["composition_priority_tier"]}` | `{row["action_recipe"]}` | {row["register"]} | '
            f'{row["current_default_phrase_de"]} | `{row["editorial_status"]}` |'
        )
    lines.extend(["", f"`{GUARD}`", ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    rule_counts = Counter(str(row["compression_rule"]) for row in edited)
    result = {
        "status": STATUS,
        "complete_current_cells": len(rows),
        "observed_cells_retained": len(observed),
        "composed_cells_retained": len(composed),
        "edited_repeated_action_cells": len(edited),
        "unchanged_cells": len(unchanged),
        "ch_ch_active_argument_edits": rule_counts["CH_CH_ACTIVE_ARGUMENT_TO_ZWEIMAL"],
        "chd_chd_post_edits": rule_counts["CHD_CHD_POST_TO_ZWEIMAL"],
        "ch_ch_grade_post_edits": rule_counts["CH_CH_GRADE_POST_TO_ZWEIMAL"],
        "registers_each_with_three_edits": sum(int(row["edited_repeated_action_count"]) == 3 for row in register_rows),
        "zweimal_markers": sum(str(row["current_default_phrase_de"]).count("zweimal") for row in edited),
        "exact_source_phrase_roundtrips": sum(row["exact_source_phrase_roundtrip"] == "YES" for row in edited),
        "two_action_slot_traces_retained": sum(int(row["action_slot_count_retained"]) == 2 for row in edited),
        "observed_phrase_changes": sum(row["previous_default_phrase_de"] != row["current_default_phrase_de"] for row in observed),
        "nonrepeated_composed_phrase_changes": sum(
            row["previous_default_phrase_de"] != row["current_default_phrase_de"]
            for row in composed if row["editorial_status"] == "UNCHANGED"
        ),
        "component_trace_changes": 0,
        "working_root_meaning_changes": 0,
        "evidence_status_changes": 0,
        "recipe_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
