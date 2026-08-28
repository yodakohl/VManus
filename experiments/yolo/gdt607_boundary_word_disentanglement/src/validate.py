#!/usr/bin/env python3
"""Validate GDT607 role and boundary-capacity artifacts independently."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


SRC = Path(__file__).resolve().parent
HERE = SRC.parent
ROOT = find_repo_root(HERE)
OUT = HERE / "artifacts"
ROLE = OUT / "role_attack"
G606 = HERE.parent / "gdt606_mixed_nomenclator_decoder" / "artifacts"
TARGETS = ("o", "y", "ol", "C", "d")
EXPECTED_SEQUENCE_SHA = "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf"
EXPECTED_CONFIGS = {
    "B0_W11": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 0, "W": 11},
    "B3_W8": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 3, "W": 8},
    "B6_W5": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 6, "W": 5},
    "B8_W3": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 8, "W": 3},
    "B11_W0": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 11, "W": 0},
}
EXPECTED_REFERENCES = {
    "caesar_la.txt": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    "divina_commedia.txt": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    "mhg/Erec-conll.txt": "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
    "mhg/Iwein-conll.txt": "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
    "mhg/Parzival-conll.txt": "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
    "mhg/Rolandslied-conll.txt": "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
    "mhg/Willehalm-conll.txt": "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict] = []
failures: list[dict] = []


def check(name: str, condition: bool, detail) -> None:
    row = {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}
    checks.append(row)
    if not condition:
        failures.append(row)


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)


def main() -> int:
    input_path = G606 / "unit_sequences.json"
    input_hash_before = sha(input_path)
    check("GDT606 unit sequence hash", input_hash_before == EXPECTED_SEQUENCE_SHA, input_hash_before)

    result = json.loads((OUT / "gdt607_result.json").read_text())
    analysis = json.loads((OUT / "gdt607_analysis.json").read_text())
    check("result schema", result["schema"] == "gdt607-boundary-word-disentanglement-v1", result["schema"])
    check("result sequence binding", result["unit_sequences_sha256"] == EXPECTED_SEQUENCE_SHA, result["unit_sequences_sha256"])
    check("reference hashes exact", result["reference_sources"] == EXPECTED_REFERENCES, result["reference_sources"])
    check("category grids exact", result["configs"] == EXPECTED_CONFIGS, result["configs"])
    check("each grid has 98 slots", all(sum(config.values()) == 98 for config in result["configs"].values()), result["configs"])
    check("six deterministic starts", result["seeds"] == [11, 29, 47, 71, 89, 107], result["seeds"])
    check("iteration count", result["iterations"] == 8000, result["iterations"])
    check("run count", result["runs"] == 90 and len(result["run_metrics"]) == 90, result["runs"])

    run_keys = [(row["language"], row["config"], int(row["seed"])) for row in result["run_metrics"]]
    check("90 unique run keys", len(set(run_keys)) == 90, len(set(run_keys)))
    run_counts = Counter((language, config) for language, config, _seed in run_keys)
    check(
        "six runs per language and grid",
        set(run_counts.values()) == {6},
        {f"{language}:{config}": count for (language, config), count in run_counts.items()},
    )
    check(
        "all held metrics finite",
        all(
            all(math.isfinite(float(value)) for key, value in row["held_metrics"].items() if key not in {"empty_chunks", "decoded_characters", "decoded_words"})
            for row in result["run_metrics"]
        ),
        "finite",
    )

    artifact_names = (
        "gdt607_complete_mappings.tsv",
        "gdt607_target_category_grid.tsv",
        "gdt607_unit_structural_features.tsv",
    )
    for name in artifact_names:
        observed = sha(OUT / name)
        check(f"result artifact hash: {name}", result["artifacts"][name] == observed, observed)

    mappings = read_tsv(OUT / "gdt607_complete_mappings.tsv")
    check("complete mapping rows", len(mappings) == 90 * 98, len(mappings))
    mapping_runs: dict[tuple[str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in mappings:
        mapping_runs[(row["language"], row["config"], int(row["seed"]))].append(row)
    check("mapping run keys match result", set(mapping_runs) == set(run_keys), len(mapping_runs))
    for key, rows in mapping_runs.items():
        language, config, seed = key
        counts = Counter(row["category"] for row in rows)
        check(f"capacity exact {language}:{config}:{seed}", counts == Counter(EXPECTED_CONFIGS[config]), dict(counts))
        check(f"98 unique units {language}:{config}:{seed}", len({row["unit"] for row in rows}) == 98, len({row["unit"] for row in rows}))
        check(
            f"empty output only for null/boundary {language}:{config}:{seed}",
            all((row["output"] == "<EMPTY>") == (row["category"] in {"N", "B"}) for row in rows),
            "exact",
        )

    target_rows = read_tsv(OUT / "gdt607_target_category_grid.tsv")
    check("target grid rows", len(target_rows) == 3 * 5 * 5, len(target_rows))
    check("target unit set", {row["unit"] for row in target_rows} == set(TARGETS), sorted({row["unit"] for row in target_rows}))
    check(
        "target counts sum to six",
        all(sum(int(row[f"{category}_count"]) for category in "BWLDSN") == 6 for row in target_rows),
        "all 75 rows",
    )

    primary_w = Counter(row["unit"] for row in mappings if row["config"] == "B0_W11" and row["category"] == "W")
    check("all five primary W in 18/18", {unit: primary_w[unit] for unit in TARGETS} == {unit: 18 for unit in TARGETS}, {unit: primary_w[unit] for unit in TARGETS})
    boundary_target = Counter(
        row["unit"] for row in mappings
        if row["config"] != "B0_W11" and row["unit"] in TARGETS and row["category"] == "B"
    )
    check("target boundary assignments exact", {unit: boundary_target[unit] for unit in TARGETS} == {"o": 0, "y": 0, "ol": 0, "C": 4, "d": 4}, {unit: boundary_target[unit] for unit in TARGETS})
    b8_w = Counter(
        row["unit"] for row in mappings
        if row["config"] == "B8_W3" and row["unit"] in TARGETS and row["category"] == "W"
    )
    check("B8/W3 target W support exact", {unit: b8_w[unit] for unit in TARGETS} == {"o": 7, "y": 16, "ol": 13, "C": 5, "d": 5}, {unit: b8_w[unit] for unit in TARGETS})
    no_w_categories = {
        unit: Counter(row["category"] for row in mappings if row["config"] == "B11_W0" and row["unit"] == unit)
        for unit in TARGETS
    }
    check("targets remain predominantly output macros at W=0", all(counts["S"] >= 15 for counts in no_w_categories.values()), {unit: dict(counts) for unit, counts in no_w_categories.items()})

    check("analysis mapping binding", analysis["input_hashes"]["complete_mappings"] == sha(OUT / "gdt607_complete_mappings.tsv"), analysis["input_hashes"])
    check("analysis structure binding", analysis["input_hashes"]["structural_features"] == sha(OUT / "gdt607_unit_structural_features.tsv"), analysis["input_hashes"])
    check("analysis sequence binding", analysis["input_hashes"]["unit_sequences"] == EXPECTED_SEQUENCE_SHA, analysis["input_hashes"]["unit_sequences"])
    check(
        "combined decision exact",
        analysis["decision"] == "W_BUCKET_CONFUND_CORRECTED__FIVE_DISTINCT_OUTPUT_BEARING_FORMAL_ROLES",
        analysis["decision"],
    )
    correlations = analysis["primary_W_correlations"]
    check("primary W frequency correlation", close(correlations["train_frequency"], 0.6511534737841689), correlations["train_frequency"])
    check("primary W standalone anticorrelation", correlations["train_standalone_fraction"] < 0, correlations["train_standalone_fraction"])
    check(
        "literal standalone counterclass has no primary W",
        all(row["primary_W_runs_of_18"] == 0 and row["train_standalone_fraction"] > 0.96 for row in analysis["standalone_counterclass"].values()),
        analysis["standalone_counterclass"],
    )
    check(
        "no stable B unit at smallest boundary capacity",
        all(not row["all_six_units"] for row in analysis["boundary_category_stability"]["B3_W8"].values()),
        analysis["boundary_category_stability"]["B3_W8"],
    )

    roles = read_tsv(OUT / "gdt607_formal_role_defaults.tsv")
    expected_roles = {
        "C": "STRICT_LOCAL_CHUNK_OPENER",
        "d": "CHUNK_AND_PHYSICAL_LINE_HEAD_CARRIER",
        "y": "CHUNK_LINE_AND_WEAK_PARAGRAPH_CLOSURE_CARRIER",
        "ol": "BOUNDARY_AND_OCCASIONAL_STANDALONE_CARRIER",
        "o": "FLEXIBLE_BIDIRECTIONAL_CONNECTOR",
    }
    check("formal role unit set", {row["unit"] for row in roles} == set(TARGETS), sorted(row["unit"] for row in roles))
    check("formal roles exact", {row["unit"]: row["formal_default"] for row in roles} == expected_roles, {row["unit"]: row["formal_default"] for row in roles})

    role_validation = json.loads((ROLE / "VALIDATION.json").read_text())
    role_result = json.loads((ROLE / "RESULT.json").read_text())
    check("role validation passes 153 checks", role_validation["status"] == "PASS" and role_validation["checks_passed"] == 153 and role_validation["checks_failed"] == 0, {key: role_validation[key] for key in ("status", "checks_passed", "checks_failed")})
    check("role audit target events", role_result["target_occurrences"] == 10277, role_result["target_occurrences"])
    classifier = role_result["classifier"]
    check("role held balanced accuracy", close(classifier["held_balanced_accuracy"], 0.6456134129410045), classifier["held_balanced_accuracy"])
    check("role permutation p-value", close(classifier["balanced_accuracy_empirical_p_ge"], 1 / 201), classifier["balanced_accuracy_empirical_p_ge"])
    check("all pairwise role AUCs above 0.85", min(row["auc_a_over_b"] for row in classifier["pairwise_auc"]) >= 0.8501, min(row["auc_a_over_b"] for row in classifier["pairwise_auc"]))

    report = (HERE / "REPORT.md").read_text()
    for phrase in (
        "W_BUCKET_CONFUND_CORRECTED__FIVE_DISTINCT_OUTPUT_BEARING_FORMAL_ROLES",
        "0.6456",
        "0.73065",
        "8,820",
        "ol=o+l",
        "flexible bidirectional connector",
    ):
        check(f"report claim present: {phrase}", phrase in report, phrase)

    check("input unchanged during validation", sha(input_path) == input_hash_before == EXPECTED_SEQUENCE_SHA, sha(input_path))
    validation = {
        "schema": "gdt607-validation-v1",
        "status": "FAIL" if failures else "PASS",
        "checks_passed": sum(row["status"] == "PASS" for row in checks),
        "checks_failed": len(failures),
        "checks": checks,
        "decision": analysis["decision"],
        "input_hashes": {"gdt606_unit_sequences.json": input_hash_before},
        "artifact_hashes": {
            path.name: sha(path)
            for path in sorted(OUT.glob("gdt607_*"))
            if path.name != "gdt607_validation.json"
        },
        "role_validation_sha256": sha(ROLE / "VALIDATION.json"),
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
        "claim_ceiling": "formal output-bearing roles and decoder-confound correction only; no plaintext meaning",
    }
    output_path = OUT / "gdt607_validation.json"
    output_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": validation["status"],
        "checks_passed": validation["checks_passed"],
        "checks_failed": validation["checks_failed"],
        "sha256": sha(output_path),
    }, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
