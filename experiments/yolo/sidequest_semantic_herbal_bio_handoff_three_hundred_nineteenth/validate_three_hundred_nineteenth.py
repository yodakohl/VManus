#!/usr/bin/env python3
"""Validate the bounded Herbal-to-Bio handoff edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    outputs = read("THREE_HUNDRED_NINETEENTH_FIVE_HERBAL_OUTPUTS.tsv")
    candidates = read("THREE_HUNDRED_NINETEENTH_HERBAL_TO_BIO_CANDIDATES.tsv")
    selected = read("THREE_HUNDRED_NINETEENTH_FIVE_SELECTED_HANDOFFS.tsv")
    checks = {
        "five_outputs": len(outputs) == 5,
        "five_unique_herbal_records": {x["herbal_record"] for x in outputs} == {"H1", "H2", "H3", "H4", "H5"},
        "four_herbal_pages": {x["page"] for x in outputs} == {"f10r", "f11r", "f55v", "f56r"},
        "fifteen_candidates": len(candidates) == 15,
        "five_primary_candidates": sum(x["selection"] == "PRIMARY" for x in candidates) == 5,
        "five_selected": len(selected) == 5,
        "selected_bio_pages_allowed": {x["bio_page"] for x in selected} <= {"f81v", "f82r", "f83r"},
        "no_direct_pointer": all(x["direct_pointer"] == "NO" for x in selected),
        "all_outputs_concrete": all(x["preparation_output"] and x["output_instruction"] for x in outputs),
        "all_selected_have_instruction": all(x["source_work_instruction"] and x["integrated_handoff_reading"] for x in selected),
        "no_sealed_page_token": all("f84" not in "\t".join(x.values()).lower() for rows in [outputs, candidates, selected] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_NINETEENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
