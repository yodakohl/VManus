#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    paths = sorted(OUT.glob("gdt409_*.tsv"))
    first = {str(path): digest(path) for path in paths}
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    second = {str(path): digest(path) for path in paths}
    audit = rows("gdt409_19_core_semantic_audit.tsv")
    registers = rows("gdt409_19_by_register.tsv")
    pairs = rows("gdt409_substitution_frame_pairs.tsv")
    examples = rows("gdt409_cross_register_examples.tsv")
    dictionary = rows("gdt409_selected_minimal_dictionary.tsv")
    result = json.loads((OUT / "gdt409_result.json").read_text(encoding="utf-8"))
    roots = {row["root"] for row in audit}
    checks = {
        "roots_19": len(audit) == 19 and len(roots) == 19,
        "dictionary_19": len(dictionary) == 19 and {row["root"] for row in dictionary} == roots,
        "register_matrix_complete": len(registers) == 19 * 5,
        "all_roots_observed": all(int(row["atom_mention_count"]) > 0 for row in audit),
        "pair_rows_171": len(pairs) == 171,
        "examples_cover_roots": {row["root"] for row in examples} == roots,
        "values_atomic": all(0 < len(row["selected_minimal_value_de"].split()) <= 2 for row in dictionary),
        "no_unknown_value": all(row["selected_minimal_value_de"] not in {"UNKNOWN", "UNBEKANNT", "FORMAL"} for row in dictionary),
        "decision_count": sum(result["decision_counts"].values()) == 19,
        "deterministic_rebuild": first == second,
        "status_exact": result["status"] == "NINETEEN_MINIMAL_VALUES_RETAINED__TEN_PROVISIONAL_VERBS_OR_RELATIONS",
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (audit, registers, pairs, examples, dictionary) for row in table),
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt409_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
