#!/usr/bin/env python3
"""Independent deterministic validator for GDT734/V99R7."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch"
ART = EXP / "artifacts"
OUT = ART / "VALIDATION.json"
RUNNER = EXP / "src/run.py"
EDITORIAL_SPECS = EXP / "src/ACTIVE_WHOLE_EDITORIAL_SPECS.tsv"
BASE_CELLS = ROOT / "experiments/yolo/gdt733_v99r6_integrated_legacy_grade_cache_renderer/artifacts/V99R6_32339_CELL_REGISTER.tsv"
GENERIC_RX = re.compile(r"(?:Arbeitsgut|Arbeitsitem|Arbeitszyklus|working material|work item|destination place)", re.I)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)

    def equal(self, actual: object, expected: object, label: str) -> None:
        self.check(actual == expected, f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    audit = Audit()
    with tempfile.TemporaryDirectory(prefix="gdt734-validate-") as tmp:
        temp = Path(tmp)
        replay_art = temp / "artifacts"
        replay_report = temp / "REPORT.md"
        env = dict(os.environ)
        env["VMANUS_GDT734_ARTIFACT_DIR"] = str(replay_art)
        env["VMANUS_GDT734_REPORT_PATH"] = str(replay_report)
        proc = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        audit.equal(proc.returncode, 0, "builder replay exit")
        # README is hand-authored documentation, not emitted by run.py.
        published = sorted(p.name for p in ART.iterdir() if p.is_file() and p.name not in {"VALIDATION.json", "README.md"})
        rebuilt = sorted(p.name for p in replay_art.iterdir()) if replay_art.is_dir() else []
        audit.equal(rebuilt, published, "builder artifact name set")
        for name in sorted(set(published) & set(rebuilt)):
            audit.equal(sha(replay_art / name), sha(ART / name), f"byte replay {name}")
        audit.check(replay_report.is_file(), "replayed REPORT exists")
        if replay_report.is_file():
            audit.equal(sha(replay_report), sha(EXP / "REPORT.md"), "byte replay REPORT.md")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    cells = read_tsv(ART / "V99R7_32339_COMPACT_CELL_REGISTER.tsv")
    delta = read_tsv(ART / "V99R7_531_POSITION_DELTA.tsv")
    repairs = read_tsv(ART / "V99R7_71_ACTIVE_WHOLE_EXPORT_REPAIR.tsv")
    candidates = read_tsv(ART / "V99R7_20_UNIQUE_SPLIT_CANDIDATE_DECK.tsv")
    dictionary = read_tsv(ART / "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv")
    lines = read_tsv(ART / "V99R7_4128_INTEGRATED_LINE_READER.tsv")
    roles = read_tsv(ART / "V99R7_19_FAMILY_ROLE_MATRIX.tsv")
    historical = read_tsv(ART / "HISTORICAL_MICROENTRY_COMPARATORS.tsv")
    editorial = read_tsv(ART / "V99R7_28_EDITORIAL_SCOPE_PRECEDENCE_AUDIT.tsv")
    editorial_specs = read_tsv(EDITORIAL_SPECS)
    base_cells = read_tsv(BASE_CELLS)

    audit.equal(len(cells), 32339, "cell count")
    audit.equal(Counter(r["gdt734_dispatch_class"] for r in cells), Counter({"UNCHANGED_GDT733": 31808, "ACTIVE_WHOLE_EXPORT_REPAIR": 305, "UNIQUE_SPLIT_EXPLORATORY_WHOLE": 226}), "dispatch census")
    audit.equal(sum(int(r["unknown_v99r6"]) for r in cells), 7989, "unknown before")
    audit.equal(sum(int(r["unknown_v99r7"]) for r in cells), 7458, "unknown after")
    audit.equal(len({r["surface"] for r in cells if int(r["unknown_v99r6"])}), 5107, "unknown surfaces before")
    audit.equal(len({r["surface"] for r in cells if int(r["unknown_v99r7"])}), 5016, "unknown surfaces after")
    audit.equal(len(delta), 531, "position delta")
    audit.equal(len(repairs), 71, "repair rows")
    audit.equal(sum(int(r["cache_occurrences_repaired"]) for r in repairs), 305, "repair occurrence sum")
    audit.equal(len(editorial_specs), 28, "editorial spec rows")
    audit.equal(len({r["surface"] for r in editorial_specs}), 28, "editorial spec surfaces unique")
    audit.equal(Counter(r["decision"] for r in editorial_specs), Counter({"RENDERER_REVISE": 26, "HOLD_UNCHANGED": 2}), "editorial spec decisions")
    audit.equal(len(editorial), 28, "editorial audit rows")
    audit.equal({r["surface"] for r in editorial}, {r["surface"] for r in editorial_specs}, "editorial audit/spec surface parity")
    audit.equal(Counter(r["renderer_decision"] for r in editorial), Counter({"RENDERER_REVISE": 26, "HOLD_UNCHANGED": 2}), "editorial audit decisions")
    # Reconstruct the renderer-only effect from the independent V99R6 cell base.
    revise_surfaces = {r["surface"] for r in editorial_specs if r["decision"] == "RENDERER_REVISE"}
    expected_override_keys = {
        (r["page"], r["locus"], r["token_ordinal"])
        for r in base_cells
        if r["surface"] in revise_surfaces and re.search(r"\[[^]]+:\?]", r["v99r6_spoken_cell_de"])
    }
    actual_override_keys = {
        (r["page"], r["locus"], r["token_ordinal"])
        for r in cells if int(r["editorial_override_applied"])
    }
    audit.equal(len(expected_override_keys), 132, "independent editorial override positions")
    audit.equal(actual_override_keys, expected_override_keys, "exact editorial override key parity")
    audit.equal(sum(int(r["editorial_override_count"]) for r in lines), 132, "line editorial override sum")
    audit.equal(sum(int(r["editorial_override_count"]) > 0 for r in lines), 124, "lines with editorial override")
    audit.equal(len(candidates), 20, "candidate rows")
    audit.equal(sum(int(r["actual_occurrences"]) for r in candidates), 226, "candidate occurrence sum")
    audit.equal(Counter(r["candidate_decision"] for r in candidates), Counter({"PROMOTE_COMPOSITIONAL_WHOLE": 9, "REVISE_ROLE_CONSTRAINED_WHOLE": 5, "LEARNED_WHOLE_NO_COMPOSITIONAL_CREDIT": 6}), "candidate decisions")
    audit.check(all(r["exact_graphemic_split_count"] == "1" and r["exact_reading_combination_count"] == "1" for r in candidates), "candidate uniqueness")
    audit.check(all(r["component_global_export_allowed"] == "0" for r in candidates), "candidate component export zero")
    audit.equal(len(dictionary), 1606, "dictionary readings")
    audit.equal(len({r["surface"] for r in dictionary}), 1602, "dictionary surfaces")
    for field in ("working_meaning_de", "working_model_score_0_100_not_probability", "working_model_level", "positive_evidence_de", "counterevidence_de", "semantic_scope", "global_export_scope"):
        audit.check(all(r[field] for r in dictionary), f"dictionary populated {field}")
    for surface in ("dchey", "olkar"):
        scoped = [r for r in cells if r["surface"] == surface and int(r["unknown_v99r6"])]
        audit.equal(len(scoped), 1, f"{surface} scoped unknown count")
        audit.check(all(int(r["unknown_v99r7"]) == 1 and r["gdt734_dispatch_class"] == "UNCHANGED_GDT733" for r in scoped), f"{surface} remains scoped")

    audit.equal(len(lines), 4128, "line count")
    audit.equal(sum(int(r["practical_unit_count"]) for r in lines), 32319, "practical units")
    audit.equal(sum(int(r["gdt734_changed_cell_count"]) > 0 for r in lines), 472, "changed lines")
    audit.equal(sum(int(r["complete_line_v99r6"]) for r in lines), 1413, "complete lines before")
    audit.equal(sum(int(r["complete_line_v99r7"]) for r in lines), 1428, "complete lines after")
    audit.equal(sum(int(r["newly_complete_line"]) for r in lines), 15, "new complete lines")
    audit.equal(len(roles), 19, "role rows")
    audit.equal(len(historical), 5, "historical rows")
    audit.check(all(r["historical_relation_credit"] == "0" for r in roles), "role historical credit zero")
    audit.check(all(r["voynich_sign_value_credit"] == "0" for r in historical), "historical sign credit zero")
    audit.check(not any(GENERIC_RX.search(r["v99r7_practical_render_de"]) for r in lines), "no generic work-item prose")
    audit.check(not any(re.match(r"^f84(?:r|v|$)", r["page"]) for r in cells), "f84/f84r absent")
    audit.equal(result["cache_cells"], 32339, "RESULT cache cells")
    audit.equal(result["changed_cells"], 531, "RESULT delta")
    audit.equal(result["unknown_cells_after"], 7458, "RESULT unknown")
    audit.equal(result["unknown_surfaces_after"], 5016, "RESULT unknown surfaces")
    audit.equal(result["complete_dictionary_readings"], 1606, "RESULT dictionary")
    audit.equal(result["editorially_audited_wholes"], 28, "RESULT editorial audits")
    audit.equal(result["editorially_revised_wholes"], 26, "RESULT editorial revisions")
    audit.equal(result["editorial_scope_audit_rows"], 28, "RESULT editorial audit rows")
    audit.equal(result["f84_accessed"], 0, "RESULT f84")
    audit.equal(result["f84r_accessed"], 0, "RESULT f84r")

    replay_failed = any(any(marker in f for marker in ("replay", "builder artifact", "byte replay")) for f in audit.failures)
    payload = {"experiment_id": "GDT734", "status": "PASS" if not audit.failures else "FAIL", "checks": audit.checks, "failures": audit.failures, "builder_replay": "TEMPFILE_BYTE_IDENTICAL" if not replay_failed else "FAILED", "validated_counts": {"cells": len(cells), "delta": len(delta), "repairs": len(repairs), "candidates": len(candidates), "editorial_audits": len(editorial), "editorial_revisions": sum(r["renderer_decision"] == "RENDERER_REVISE" for r in editorial), "editorial_override_positions": len(actual_override_keys), "dictionary_readings": len(dictionary), "lines": len(lines), "roles": len(roles), "historical": len(historical)}}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
