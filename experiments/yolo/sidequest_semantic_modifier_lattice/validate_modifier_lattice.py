#!/usr/bin/env python3
"""Validate bounded modifier enrichments and family coverage."""

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
    dictionary = read("UPDATED_ASTRO_53_MODIFIER_DICTIONARY.tsv")
    decisions = read("MODIFIER_DECISIONS.tsv")
    pairs = read("E_GRADE_FAMILY_PAIRS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("dictionary_count", len(dictionary) == 53, len(dictionary))
    add("surface_unique", len({row["visible_surface"] for row in dictionary}) == 53, "53 expected")
    add("modifier_decisions", len(decisions) == 8, len(decisions))
    add("e_pairs", len(pairs) == 5, len(pairs))
    add("enriched_count", sum(row["modifier_status"] == "ENRICHED_BOUND_MODIFIER" for row in dictionary) == 22, sum(row["modifier_status"] == "ENRICHED_BOUND_MODIFIER" for row in dictionary))
    by_surface = {row["visible_surface"]: row for row in dictionary}
    add("okar_e_pair", by_surface["okar"]["enriched_atom_sequence"] == "OK+AR" and by_surface["okear"]["enriched_atom_sequence"] == "OK+E+AR", "OK+AR -> OK+E+AR")
    add("otor_e_pair", by_surface["otor"]["enriched_atom_sequence"] == "OT+OR" and by_surface["qoteor"]["enriched_atom_sequence"] == "OT+E+OR", "OT+OR -> OT+E+OR")
    add("otoar_e_pair", by_surface["otoar"]["enriched_atom_sequence"] == "OT+AR" and by_surface["qotoear"]["enriched_atom_sequence"] == "OT+E+AR", "OT+AR -> OT+E+AR")
    add("ee_grade", by_surface["okeeodal"]["enriched_atom_sequence"] == "OK+EE+AL", by_surface["okeeodal"])
    add("y_bound", {row["visible_surface"] for row in dictionary if "Y" in row["bound_modifier"].split("+")} == {"okoaly", "okodaly", "otoly"}, "three Y types")
    add("dy_bound", {row["visible_surface"] for row in dictionary if "DY_BOUND" in row["bound_modifier"].split("+")} == {"okardy", "okoldy"}, "two DY types")
    dy = next(row for row in decisions if row["modifier"] == "DY")
    add("dy_decision_counts", dy["astro_surface_types"] == "2" and dy["astro_occurrences"] == "2", dy)
    add("q_renderer", next(row for row in decisions if row["modifier"] == "Q/S/CH/D/T leading")["decision"] == "KEEP_NONSEMANTIC", "renderer only")
    add("od_held", next(row for row in decisions if row["modifier"] == "O/OD medial")["decision"] == "HOLD", "held")
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (dictionary, decisions, pairs) for row in table), "sealed tokens absent")

    products = ["UPDATED_ASTRO_53_MODIFIER_DICTIONARY.tsv", "MODIFIER_DECISIONS.tsv", "E_GRADE_FAMILY_PAIRS.tsv", "MODIFIER_LATTICE_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_modifier_lattice.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
