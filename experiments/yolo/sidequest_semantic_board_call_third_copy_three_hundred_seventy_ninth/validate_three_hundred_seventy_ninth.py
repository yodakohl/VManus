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
    calls = read("THREE_HUNDRED_SEVENTY_NINTH_14_BOARD_CALLS.tsv")
    hidden = read("THREE_HUNDRED_SEVENTY_NINTH_14_HIDDEN_VALUE_CHECK.tsv")
    visible = read("THREE_HUNDRED_SEVENTY_NINTH_15_THIRD_COPY_FORMS.tsv")
    variable = [r for r in calls if r["surface_class"] == "VARIABLE"]
    invariant = [r for r in calls if r["surface_class"] == "INVARIANT"]
    checks = {
        "14_calls": len(calls) == 14 and len({r["board_call_only"] for r in calls}) == 14,
        "no_german_spoken": all(r["german_value_spoken"] == "NO" for r in calls),
        "all_surfaces_registered": all(r["selected_registered"] == "YES" for r in calls),
        "eight_variable_six_invariant": len(variable) == 8 and len(invariant) == 6,
        "variation_rule_obeyed": all(r["obeyed_variation_rule"] == "YES" for r in calls),
        "all_hidden_layers_match": len(hidden) == 14 and all(r["identity_match"] == r["value_match"] == r["owner_match"] == r["cycle_match"] == "YES" for r in hidden),
        "15_visible_14_source": len(visible) == 15 and sum(int(r["source_contribution"]) for r in visible) == 14,
        "one_carry": sum(r["visibility_role"] == "MARKED_ANTICIPATION" for r in visible) == 1,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_NINTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
