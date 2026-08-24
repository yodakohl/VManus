#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    handoff = read("FOUR_HUNDRED_FIFTH_11_EVENT_HANDOFF.tsv")
    expansions = read("FOUR_HUNDRED_FIFTH_THREE_CONCRETE_EXPANSIONS.tsv")
    mirror = read("FOUR_HUNDRED_FIFTH_FOUR_MIRRORED_ROLES.tsv")
    checks = {
        "eleven_events": len(handoff) == 11,
        "exact_event_range": [row["event_id"] for row in handoff] == [f"E{n:03d}" for n in range(270, 281)],
        "phase_counts": (sum(row["phase"] == "PHASE_A" for row in handoff), sum(row["phase"] == "PHASE_B" for row in handoff)) == (4, 7),
        "crosses_loci": {row["locus"] for row in handoff} == {"f83r.14", "f83r.15"},
        "owner_unresolved_everywhere": {row["visible_owner"] for row in handoff} == {"UNRESOLVED_GAP_BETWEEN_MARGIN_AND_MAIN_PAIR"},
        "terminal_final": handoff[-1]["operation"] == "LOCAL_TRANSFER_CLOSE",
        "three_expansions": len(expansions) == 3,
        "bath_selected_by_score": max(expansions, key=lambda row: int(row["score"]))["model"] == "BATH_HANDOFF",
        "four_mirrored_roles": {row["role"] for row in mirror} == {"MEASURE", "READY", "TARGET", "CURRENT_ITEM"},
        "ready_exact_reuse": next(row for row in mirror if row["role"] == "READY")["phase_a_surface"] == next(row for row in mirror if row["role"] == "READY")["phase_b_surface"],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_FIFTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
