#!/usr/bin/env python3
"""Validate the promoted cross-register component families."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    families = read("PRODUCTIVE_CROSS_REGISTER_FAMILIES.tsv")
    stems = read("REVISED_COMMON_STEM_DICTIONARY.tsv")
    candidates = read("ASTRO_53_COMPOSITIONAL_DICTIONARY.tsv")
    residuals = read("RESIDUAL_MODIFIER_INVENTORY.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    promoted = {row["atom_sequence"] for row in families if row["status"] == "PROMOTED_PRODUCTIVE_FAMILY"}
    forward = {row["atom_sequence"] for row in families if row["status"] == "FORWARD_PREDICTED_SINGLE_CELL"}
    add("candidate_count", len(candidates) == 53, len(candidates))
    add("stem_count", len(stems) == 25, len(stems))
    add("promoted_count", len(promoted) == 8, sorted(promoted))
    add("promoted_exact", promoted == {"OK+AR", "OK+AL", "OT+OL", "OT+OR", "OK+OL", "OT+AR", "AL+AIIN", "AR+AL"}, sorted(promoted))
    add("forward_count", len(forward) == 3, sorted(forward))
    add("forward_exact", forward == {"OL+AR", "OT+AIR", "CHD+AIIN"}, sorted(forward))
    okar = next(row for row in families if row["atom_sequence"] == "OK+AR")
    add("okar_family", okar["surface_type_count"] == "5" and okar["astro_occurrences"] == "9" and okar["owner_count"] == "8", okar)
    okal = next(row for row in families if row["atom_sequence"] == "OK+AL")
    add("okal_family", okal["surface_type_count"] == "5" and okal["owner_count"] == "5", okal)
    add("air_broadened", next(row for row in stems if row["atom"] == "AIR")["short_common_value_de"] == "LAUF/BAHN", "AIR=LAUF/BAHN")
    add("or_broadened", next(row for row in stems if row["atom"] == "OR")["short_common_value_de"] == "SATZ/ANSATZ", "OR=SATZ/ANSATZ")
    add("all_candidate_statuses", all(row["composition_status"] in {"FAMILY_COMPOSITION", "FORWARD_SINGLE_CELL", "LEARNED_ASTRO_WORD_WITH_COMPONENT_HINT"} for row in candidates), "three statuses only")
    add("residuals_present", len(residuals) == summary["residual_rows"], len(residuals))
    add("no_residual_semantics", all("do not assign" in row["semantic_decision"] for row in residuals), "all held")
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (families, stems, candidates, residuals) for row in table), "sealed tokens absent")

    products = ["PRODUCTIVE_CROSS_REGISTER_FAMILIES.tsv", "REVISED_COMMON_STEM_DICTIONARY.tsv", "ASTRO_53_COMPOSITIONAL_DICTIONARY.tsv", "RESIDUAL_MODIFIER_INVENTORY.tsv", "CROSS_REGISTER_PHRASEBOOK.md", "CROSS_REGISTER_PARADIGM_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_cross_register_paradigms.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
