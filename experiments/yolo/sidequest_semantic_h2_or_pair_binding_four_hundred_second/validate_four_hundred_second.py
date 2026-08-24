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
    pair = read("FOUR_HUNDRED_SECOND_OR_PAIR_BINDING.tsv")
    paraphrases = read("FOUR_HUNDRED_SECOND_FOUR_PARAPHRASES.tsv")
    contrasts = read("FOUR_HUNDRED_SECOND_SIX_DUPLICATION_CONTRASTS.tsv")
    registers = read("FOUR_HUNDRED_SECOND_REGISTER_TRACE.tsv")
    checks = {
        "two_or_events": len(pair) == 2,
        "event_ids": [row["event_id"] for row in pair] == ["E033", "E034"],
        "same_exact_card": len({row["joint_tuple_id"] for row in pair}) == 1,
        "different_surfaces": {row["surface"] for row in pair} == {"shor", "chor"},
        "surface_has_no_semantic_load": {row["surface_wrapper_semantics"] for row in pair} == {"NONE_RENDERER_ONLY"},
        "two_active_registers": len({row["active_register"] for row in pair}) == 2,
        "four_paraphrases": len(paraphrases) == 4,
        "one_strongest": sum(row["ranking"] == "STRONGEST" for row in paraphrases) == 1,
        "six_duplicate_controls": len(contrasts) == 6,
        "register_trace_six_steps": len(registers) == 6,
        "combined_item_after_pair": registers[-1]["primary_register"] == "COMBINED_VESSEL_POST",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_SECOND_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
