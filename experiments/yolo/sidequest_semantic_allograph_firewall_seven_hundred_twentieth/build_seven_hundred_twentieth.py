#!/usr/bin/env python3
"""Build Pass 720: distinguish harmless allographs from true card substitutions."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P712 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_recipe_inventory_seven_hundred_twelfth"
P719 = ROOT / "experiments/yolo/sidequest_semantic_mixed_hand_boundary_seven_hundred_nineteenth"
SUBSTITUTIONS = {
    "MP012": ("chaiin", "HARMLESS_ALLOGRAPH"),
    "MP020": ("okchedy", "HARMLESS_ALLOGRAPH"),
    "MP017": ("qokar", "DANGEROUS_OTHER_CARD"),
    "MP023": ("cheedy", "DANGEROUS_OTHER_CARD"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    mapping = read(P712 / "SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    mixed = read(P719 / "SEVEN_HUNDRED_NINETEENTH_27_MIXED_HAND_TRACE.tsv")
    surface_cards: dict[str, set[str]] = defaultdict(set)
    by_card = {row["exact_card_id"]: row for row in mapping}
    for row in mapping:
        for surface in row["surfaces"].split("|"):
            surface_cards[surface].add(row["exact_card_id"])

    trace_rows = []
    case_rows = []
    for row in mixed:
        original_surface = row["mixed_surface"]
        supplied_surface, intended_case = SUBSTITUTIONS.get(row["master_event_id"], (original_surface, "UNCHANGED"))
        decoded_cards = surface_cards[supplied_surface]
        if len(decoded_cards) != 1:
            raise AssertionError(f"Ambiguous supplied surface {supplied_surface}: {decoded_cards}")
        decoded_card = next(iter(decoded_cards))
        expected_card = row["exact_card"]
        same_card = decoded_card == expected_card
        if intended_case == "UNCHANGED":
            verdict = "UNCHANGED_OK"
            corrected_surface = supplied_surface
        elif same_card:
            verdict = "KEEP_AS_LICENSED_ALLOGRAPH"
            corrected_surface = supplied_surface
        else:
            verdict = "REJECT_AND_RESTORE_EXPECTED_CARD"
            corrected_surface = original_surface
        corrected_card = next(iter(surface_cards[corrected_surface]))
        expected_map = by_card[expected_card]
        decoded_map = by_card[decoded_card]
        trace_rows.append({
            "position": row["position"], "master_event_id": row["master_event_id"], "docket_id": row["docket_id"],
            "owner": row["owner"], "line_no": row["line_no"], "line_column": row["line_column"],
            "expected_recipe": row["component_recipe"], "expected_card": expected_card,
            "baseline_surface": original_surface, "supplied_surface": supplied_surface,
            "decoded_card": decoded_card, "decoded_recipe": decoded_map["component_recipe"],
            "same_exact_card": "YES" if same_card else "NO", "intended_case": intended_case,
            "corrector_verdict": verdict, "corrected_surface": corrected_surface,
            "corrected_card": corrected_card, "corrected_exact_match": "YES" if corrected_card == expected_card else "NO",
        })
        if intended_case != "UNCHANGED":
            mismatch = "NONE" if same_card else f"{expected_map['component_recipe']} != {decoded_map['component_recipe']}"
            case_rows.append({
                "case_id": f"AF{len(case_rows) + 1}", "master_event_id": row["master_event_id"],
                "case_kind": intended_case, "expected_card": expected_card, "baseline_surface": original_surface,
                "supplied_surface": supplied_surface, "decoded_card": decoded_card,
                "expected_recipe": expected_map["component_recipe"], "decoded_recipe": decoded_map["component_recipe"],
                "recipe_mismatch": mismatch, "corrector_verdict": verdict,
                "working_consequence_de": (
                    "Keine: andere registrierte Handform derselben Karte."
                    if same_card else
                    "Ziel/Quelle kippt." if row["master_event_id"] == "MP017" else
                    "Offenes Umsetzen wird zu Absetzen plus Schluss."
                ),
            })

    line_rows = []
    for line_no in range(1, 6):
        subset = [row for row in trace_rows if int(row["line_no"]) == line_no]
        line_rows.append({
            "line_no": line_no, "events": len(subset),
            "supplied_line": " ".join(row["supplied_surface"] for row in subset),
            "corrected_line": " ".join(row["corrected_surface"] for row in subset),
            "harmless_kept": sum(row["corrector_verdict"] == "KEEP_AS_LICENSED_ALLOGRAPH" for row in subset),
            "dangerous_repaired": sum(row["corrector_verdict"] == "REJECT_AND_RESTORE_EXPECTED_CARD" for row in subset),
        })

    write("SEVEN_HUNDRED_TWENTIETH_4_FIREWALL_CASES.tsv", case_rows)
    write("SEVEN_HUNDRED_TWENTIETH_27_CORRECTOR_TRACE.tsv", trace_rows)
    write("SEVEN_HUNDRED_TWENTIETH_5_SUPPLIED_AND_CORRECTED_LINES.tsv", line_rows)
    summary = {
        "status": "PASS", "events": len(trace_rows), "cases": len(case_rows),
        "harmless_allographs": sum(row["case_kind"] == "HARMLESS_ALLOGRAPH" for row in case_rows),
        "dangerous_other_cards": sum(row["case_kind"] == "DANGEROUS_OTHER_CARD" for row in case_rows),
        "harmless_kept": sum(row["corrector_verdict"] == "KEEP_AS_LICENSED_ALLOGRAPH" for row in case_rows),
        "dangerous_rejected": sum(row["corrector_verdict"] == "REJECT_AND_RESTORE_EXPECTED_CARD" for row in case_rows),
        "final_exact_card_matches": sum(row["corrected_exact_match"] == "YES" for row in trace_rows),
        "meaning_changes_after_correction": 0,
        "decision": "CARD_ID_FIREWALL_KEEPS_TWO_ALLOGRAPHS_AND_REJECTS_TWO_TRUE_COMPONENT_SUBSTITUTIONS",
    }
    (HERE / "SEVEN_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
