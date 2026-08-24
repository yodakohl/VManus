#!/usr/bin/env python3
"""Validate Pass 722 semantic gloss pressure ranking."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_TWENTY_SECOND_39_COMPONENT_PRESSURE.tsv")
    families = read("SEVEN_HUNDRED_TWENTY_SECOND_163_RECIPE_PRESSURE.tsv")
    selected = [row for row in components if row["decision"] == "REVISE_NOW"]
    queue = [row for row in components if row["decision"] == "NEXT_QUEUE"]
    checks = {
        "components_39": len(components) == 39 and len({row["component"] for row in components}) == 39,
        "families_163": len(families) == 163 and len({row["semantic_family"] for row in families}) == 163,
        "selected_t_ch_k": {row["component"] for row in selected} == {"T", "CH", "K"},
        "selected_atomic_values": {row["candidate_value_de"] for row in selected} == {"ANWENDEN", "ENTNEHMEN", "ZUGEBEN"},
        "queue_o_air_cth_s": {row["component"] for row in queue} == {"O", "AIR", "CTH", "S"},
        "ranks_complete": [int(row["pressure_rank"]) for row in components] == list(range(1, 40)) and [int(row["awkwardness_rank"]) for row in families] == list(range(1, 164)),
        "revision_families_nonempty": any(row["revision_wave"] == "NOW_T_CH_K" for row in families),
        "no_form_edit_fields": all("surface" not in key and "card" not in key for key in components[0]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
