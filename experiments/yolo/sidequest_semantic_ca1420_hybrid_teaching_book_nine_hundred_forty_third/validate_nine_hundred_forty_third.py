#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("PASS943_20_TEACHING_RULES.tsv")
    demos = read("PASS943_8_COMPOSITION_DEMONSTRATIONS.tsv")
    predictions = read("PASS943_27_FORWARD_COMPOSITIONS.tsv")
    checks = [
        ("rules_20", len(rules) == 20, len(rules)),
        ("demos_8", len(demos) == 8, len(demos)),
        ("predictions_27", len(predictions) == 27, len(predictions)),
        ("unique_recipes", len({row["component_recipe"] for row in predictions}) == 27, len({row["component_recipe"] for row in predictions})),
        ("concrete_readback", all(row["readback_de"].strip() for row in demos), "nonempty"),
        ("surface_candidates", all(row["candidate_bare_surface"] and row["candidate_entry_surface"] for row in predictions), "present"),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in rules + demos + predictions), "sealed"),
    ]
    targets = [OUT / "PASS943_20_TEACHING_RULES.tsv", OUT / "PASS943_8_COMPOSITION_DEMONSTRATIONS.tsv", OUT / "PASS943_27_FORWARD_COMPOSITIONS.tsv", OUT / "PASS943_CA1420_HYBRID_TEACHING_BOOK.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_third.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS943_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
