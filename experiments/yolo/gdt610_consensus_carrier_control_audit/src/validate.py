#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


HERE = Path(__file__).resolve().parent.parent
ROOT = find_repo_root(HERE)
OUT = HERE / "artifacts"
UNIT_PATH = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts/unit_sequences.json"
UNIT_SHA = "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf"
CATEGORY_COUNTS = {"L": 42, "D": 4, "S": 34, "N": 7, "W": 11}
LANGUAGES = {"latin", "old_italian", "middle_high_german"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks = []

    def check(label, condition, observed=None):
        checks.append({
            "check": label,
            "status": "PASS" if condition else "FAIL",
            "observed": observed,
        })

    check("canonical GDT606 unit hash", sha(UNIT_PATH) == UNIT_SHA, sha(UNIT_PATH))
    units = json.loads(UNIT_PATH.read_text(encoding="utf-8"))
    check("canonical inventory 98", len(units["inventory"]) == 98, len(units["inventory"]))
    check("canonical train chunks 20336", len(units["sequences"]["train"]) == 20336, len(units["sequences"]["train"]))
    check("canonical held chunks 9838", len(units["sequences"]["held"]) == 9838, len(units["sequences"]["held"]))
    train_folios = {row["physical_folio"] for row in units["sequences"]["train"]}
    held_folios = {row["physical_folio"] for row in units["sequences"]["held"]}
    check("canonical 68/23 folio split", len(train_folios) == 68 and len(held_folios) == 23 and not train_folios & held_folios, [len(train_folios), len(held_folios)])

    anchors = read_tsv(OUT / "anchor_categories.tsv")
    anchor_map = {row["unit"]: row["category"] for row in anchors}
    check("98 unique anchor rows", len(anchors) == len(anchor_map) == 98, [len(anchors), len(anchor_map)])
    check("anchor allocation 42/4/34/7/11", Counter(anchor_map.values()) == Counter(CATEGORY_COUNTS), Counter(anchor_map.values()))
    qok = {"qokaN", "qokEdy", "qokaI", "qokedy", "qokEy"}
    check("five qok units assigned W", all(anchor_map[name] == "W" for name in qok), sorted((name, anchor_map.get(name)) for name in qok))

    control_meta = json.loads((OUT / "synthetic_control_meta.json").read_text(encoding="utf-8"))
    check("control exact chunk lengths", control_meta["exact_chunk_length_sequence"] is True)
    check("control zero encoding failure", control_meta["encoding_failures"] == 0, control_meta["encoding_failures"])
    check("control all 98 units", control_meta["train_inventory_coverage"] == 1.0, control_meta["train_inventory_coverage"])
    check("control rank frequency matched", control_meta["train_frequency_rank_spearman"] > 0.999, control_meta["train_frequency_rank_spearman"])
    check("control JS below .05", control_meta["train_frequency_js_divergence_bits"] < 0.05, control_meta["train_frequency_js_divergence_bits"])

    grid = read_tsv(OUT / "calibration_grid.tsv")
    check("five coupling values", {float(row["coupling"]) for row in grid} == {0.0, 0.03, 0.1, 0.3, 1.0}, [row["coupling"] for row in grid])
    eligible = [row for row in grid if int(row["selection_eligible"])]
    selected = max(eligible, key=lambda row: (float(row["selection_utility"]), -float(row["coupling"])))
    check("lambda .10 selected by utility", float(selected["coupling"]) == 0.1, selected["coupling"])
    check("selected stability .8163", abs(float(selected["all_member_exact_type_fraction"]) - 0.8163265306122449) < 1e-15, selected["all_member_exact_type_fraction"])
    check("selected held char .3374", abs(float(selected["mean_held_plaintext_character_accuracy"]) - 0.3373630008571373) < 1e-15, selected["mean_held_plaintext_character_accuracy"])
    check("coupling increases stability", float(selected["all_member_exact_type_fraction"]) > float(grid[0]["all_member_exact_type_fraction"]), [grid[0]["all_member_exact_type_fraction"], selected["all_member_exact_type_fraction"]])

    calibration = read_tsv(OUT / "calibration_complete_mappings.tsv")
    check("complete calibration map", len(calibration) == 5 * 6 * 98, len(calibration))
    selected_rows = [row for row in calibration if float(row["coupling"]) == 0.1]
    w_rows = [row for row in selected_rows if row["category"] == "W"]
    check("selected control W has 66 rows", len(w_rows) == 6 * 11, len(w_rows))
    w_outputs = defaultdict(set)
    for row in w_rows:
        w_outputs[row["unit"]].add(row["output"])
    check("all eleven W maps six-view stable", len(w_outputs) == 11 and all(len(values) == 1 for values in w_outputs.values()), {key: sorted(value) for key, value in w_outputs.items()})
    check("all eleven stable W maps wrong", all(row["oracle_exact"] == "0" for row in w_rows), sum(row["oracle_exact"] == "1" for row in w_rows))

    diagnostics = read_tsv(OUT / "category_diagnostics.tsv")
    control_diag = {row["category"]: row for row in diagnostics if row["dataset"] == "synthetic_control"}
    check("control diagnostic five categories", set(control_diag) == set("LDSNW"), sorted(control_diag))
    check("control L recovery .9246", abs(float(control_diag["L"]["mean_oracle_type_accuracy"]) - 0.9246031746031746) < 1e-15, control_diag["L"]["mean_oracle_type_accuracy"])
    check("control D and N exact", float(control_diag["D"]["mean_oracle_type_accuracy"]) == float(control_diag["N"]["mean_oracle_type_accuracy"]) == 1.0)
    check("control W zero recovery", float(control_diag["W"]["mean_oracle_type_accuracy"]) == 0.0, control_diag["W"]["mean_oracle_type_accuracy"])

    target = read_tsv(OUT / "target_complete_mappings.tsv")
    check("complete target maps", len(target) == 3 * 2 * 6 * 98, len(target))
    check("target map languages", {row["language"] for row in target} == LANGUAGES, sorted({row["language"] for row in target}))
    check("target categories unchanged", all(row["category"] == anchor_map[row["unit"]] for row in target))
    target_groups = defaultdict(list)
    for row in target:
        target_groups[row["language"], row["condition"], int(row["member"])].append(row)
    check("all target language condition view groups", len(target_groups) == 3 * 2 * 6 and all(len(rows) == 98 for rows in target_groups.values()), len(target_groups))

    target_diag = {
        (row["language"], row["category"]): int(row["all_member_stable_types"])
        for row in diagnostics
        if row["dataset"] == "target" and row["condition"] == "coupled"
    }
    check("Latin syllable stability 1/34", target_diag["latin", "S"] == 1, target_diag["latin", "S"])
    check("Old Italian syllable stability 0/34", target_diag["old_italian", "S"] == 0, target_diag["old_italian", "S"])
    check("MHG syllable stability 2/34", target_diag["middle_high_german", "S"] == 2, target_diag["middle_high_german", "S"])

    matches = read_tsv(OUT / "non_w_exact_matches.tsv")
    check("eight non-W exact matches", len(matches) == 8, len(matches))
    check("non-W matches Latin only", {row["language"] for row in matches} == {"latin"}, sorted({row["language"] for row in matches}))
    check("non-W matches repetitive only", {row["output"] for row in matches} <= {"iiii", "sese", "cccc"}, sorted({row["output"] for row in matches}))
    check("non-W matches explicitly non-readings", all(row["interpretation"] == "repetitive_not_reading" for row in matches))

    result = json.loads((OUT / "result.json").read_text(encoding="utf-8"))
    check("result binds canonical unit hash", result["input_unit_sha256"] == UNIT_SHA, result["input_unit_sha256"])
    check("result hard failure", result["decision"].startswith("FAIL:"), result["decision"])
    check("result selected lambda", result["calibration_selected_coupling"] == 0.1, result["calibration_selected_coupling"])
    check("result no semantic interpretation", "not semantic evidence" in result["decision"], result["decision"])

    agent_validation = json.loads((OUT / "AGENT_VALIDATION.json").read_text(encoding="utf-8"))
    check("upstream 65-check validation pass", agent_validation["status"] == "PASS" and agent_validation["checks"] == 65, [agent_validation.get("status"), agent_validation.get("checks")])

    source = (HERE / "src/consensus_carrier_decoder.py").read_text(encoding="utf-8")
    check("decoder binds canonical unit hash", 'UNIT_SHA256 = "' + UNIT_SHA + '"' in source)
    private_roots = ("/" + "home" + "/", "/" + "tmp" + "/")
    check("decoder has no private paths", not any(value in source for value in private_roots))
    report = (HERE / "REPORT.md").read_text(encoding="utf-8")
    for phrase in (
        "CONSENSUS_STABILITY_INCREASES__WHOLE_WORD_KEY_STABLE_BUT_WRONG",
        "FAIL — no concrete reading",
        "All eleven W carriers are perfectly stable and all eleven are wrong",
        "only 20/34 are stable",
        "repetitive forms rather than a coherent passage",
    ):
        check("report phrase " + phrase, phrase in report, phrase)

    failures = [row for row in checks if row["status"] == "FAIL"]
    validation = {
        "schema": "gdt610-consensus-control-validation-v1",
        "status": "FAIL" if failures else "PASS",
        "checks_passed": len(checks) - len(failures),
        "checks_failed": len(failures),
        "checks": checks,
        "decision": "CONSENSUS_STABILITY_INCREASES__WHOLE_WORD_KEY_STABLE_BUT_WRONG",
        "claim_ceiling": "decoder control and target non-injection audit only; no Voynich word, language, plaintext or meaning",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
        "input_hashes": {str(UNIT_PATH.relative_to(ROOT)): sha(UNIT_PATH)},
        "artifact_hashes": {
            name: sha(OUT / name)
            for name in (
                "anchor_categories.tsv", "calibration_complete_mappings.tsv",
                "calibration_grid.tsv", "category_diagnostics.tsv",
                "non_w_exact_matches.tsv", "result.json",
                "synthetic_control_meta.json", "synthetic_oracle_mapping.tsv",
                "target_complete_mappings.tsv", "target_summary.json",
            )
        },
        "source_hashes": {
            "PREREGISTRATION.md": sha(HERE / "PREREGISTRATION.md"),
            "REPORT.md": sha(HERE / "REPORT.md"),
            "src/consensus_carrier_decoder.py": sha(HERE / "src/consensus_carrier_decoder.py"),
            "src/validate.py": sha(HERE / "src/validate.py"),
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "checks_passed": validation["checks_passed"],
        "checks_failed": validation["checks_failed"],
        "sha256": sha(OUT / "VALIDATION.json"),
    }, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
