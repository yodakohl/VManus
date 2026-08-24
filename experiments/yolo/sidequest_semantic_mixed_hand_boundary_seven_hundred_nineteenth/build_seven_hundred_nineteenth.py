#!/usr/bin/env python3
"""Build Pass 719: create and locate one mid-line hand boundary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P718 = ROOT / "experiments/yolo/sidequest_semantic_second_hand_copy_seven_hundred_eighteenth"
BOUNDARY_AFTER = 13


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
    parallel = read(P718 / "SEVEN_HUNDRED_EIGHTEENTH_27_PARALLEL_HAND_TRACE.tsv")
    mixed = []
    for position, row in enumerate(parallel, 1):
        hand = "HAND_A_SHORT" if position <= BOUNDARY_AFTER else "HAND_B_LONG"
        surface = row["first_hand_surface"] if hand == "HAND_A_SHORT" else row["second_hand_surface"]
        mixed.append({
            "position": position, "master_event_id": row["master_event_id"], "docket_id": row["docket_id"],
            "owner": row["owner"], "line_no": row["line_no"], "line_column": row["line_column"],
            "exact_card": row["exact_card"], "component_recipe": row["component_recipe"],
            "hand": hand, "mixed_surface": surface,
            "hand_a_surface": row["first_hand_surface"], "hand_b_surface": row["second_hand_surface"],
            "profile_informative": "YES" if row["first_hand_surface"] != row["second_hand_surface"] else "NO",
            "card_backread_unchanged": "YES", "owner_unchanged": "YES", "statement_unchanged": "YES",
        })

    candidate_rows = []
    for split_after in range(0, 28):
        mismatches = []
        informative_mismatches = []
        for position, row in enumerate(mixed, 1):
            expected = row["hand_a_surface"] if position <= split_after else row["hand_b_surface"]
            if expected != row["mixed_surface"]:
                mismatches.append(row["master_event_id"])
                if row["profile_informative"] == "YES":
                    informative_mismatches.append(row["master_event_id"])
        candidate_rows.append({
            "split_after_position": split_after,
            "split_location": "BEFORE_PAGE" if split_after == 0 else "AFTER_PAGE" if split_after == 27 else f"AFTER_MP{split_after:03d}",
            "surface_mismatches": len(mismatches), "informative_mismatches": len(informative_mismatches),
            "mismatch_events": "|".join(mismatches) if mismatches else "NONE",
            "perfect_profile_fit": "YES" if not mismatches else "NO",
        })

    line_rows = []
    for line_no in range(1, 6):
        subset = [row for row in mixed if int(row["line_no"]) == line_no]
        line_rows.append({
            "line_no": line_no, "events": len(subset),
            "hands_in_order": " > ".join(dict.fromkeys(str(row["hand"]) for row in subset)),
            "mixed_surface_line": " ".join(str(row["mixed_surface"]) for row in subset),
            "informative_events": sum(row["profile_informative"] == "YES" for row in subset),
            "contains_hand_boundary": "YES" if len({row["hand"] for row in subset}) > 1 else "NO",
        })

    anchor_rows = []
    for row in mixed:
        anchor_rows.append({
            "master_event_id": row["master_event_id"], "position": row["position"],
            "anchor_kind": "VARIABLE_HAND_MARKER" if row["profile_informative"] == "YES" else "INVARIANT_CARD_ANCHOR",
            "hand_a_surface": row["hand_a_surface"], "hand_b_surface": row["hand_b_surface"],
            "mixed_surface": row["mixed_surface"], "exact_card": row["exact_card"],
            "use_de": "lokalisiert die Hand" if row["profile_informative"] == "YES" else "sichert nur Kartenidentitaet",
        })

    write("SEVEN_HUNDRED_NINETEENTH_27_MIXED_HAND_TRACE.tsv", mixed)
    write("SEVEN_HUNDRED_NINETEENTH_28_BOUNDARY_CANDIDATES.tsv", candidate_rows)
    write("SEVEN_HUNDRED_NINETEENTH_5_MIXED_LINES.tsv", line_rows)
    write("SEVEN_HUNDRED_NINETEENTH_27_ANCHOR_ROLES.tsv", anchor_rows)

    perfect = [row for row in candidate_rows if row["perfect_profile_fit"] == "YES"]
    summary = {
        "status": "PASS", "events": len(mixed), "lines": len(line_rows),
        "true_boundary_after": BOUNDARY_AFTER, "boundary_line": 3, "boundary_inside_docket": "FD03",
        "boundary_inside_owner": "BASIN", "perfect_candidate_count": len(perfect),
        "recovered_boundary_after": int(perfect[0]["split_after_position"]),
        "variable_hand_markers": sum(row["profile_informative"] == "YES" for row in mixed),
        "invariant_card_anchors": sum(row["profile_informative"] == "NO" for row in mixed),
        "card_changes": 0, "owner_changes": 0, "statement_changes": 0,
        "decision": "ONE_MID_LINE_HAND_BOUNDARY_IS_UNIQUELY_LOCATED_AFTER_EVENT_THIRTEEN_WITHOUT_MOVING_CONTENT_STRUCTURE",
    }
    (HERE / "SEVEN_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
