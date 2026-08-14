#!/usr/bin/env python3
"""Independent retained-model validator for Q20OB001; does not import runner."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "q20ob001_source_panel.tsv"
METHOD = ROOT / "Q20OB001_OPEN_BODY_METHOD.md"
PANEL_AUDIT = ROOT / "q20ob001_source_panel_audit.json"
FOLDS_FILE = ROOT / "q20ob001_fold_results.tsv"
RECORDS_FILE = ROOT / "q20ob001_record_predictions.tsv"
NULL_FILE = ROOT / "q20ob001_null_results.tsv"
BASE_FILE = ROOT / "q20ob001_baseline_comparison.tsv"
RESULT_FILE = ROOT / "q20ob001_result.json"
REPORT = ROOT / "Q20OB001_OPEN_BODY_REPORT.md"
RUNNER = ROOT / "run_q20ob001_open_body.py"
OUT = ROOT / "q20ob001_validation.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
REPS = ("MEMBER", "FAMILY", "GROUP")
FOLIOS = ("f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115")
GRID = (0.0, 1 / 128, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2)
ALPHA = 0.5
WORLDS = 4096
TOL = 7e-7


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a: float, b: float, tolerance: float = TOL) -> bool:
    return abs(a - b) <= tolerance


def load_panel() -> list[dict[str, object]]:
    output = []
    for row in rows(PANEL):
        output.append(
            {
                **row,
                "star_ordinal": int(row["star_ordinal"]),
                "open_member_count": int(row["open_member_count"]),
                "body_line_count": int(row["body_line_count"]),
                "body_member_count": int(row["body_member_count"]),
                "open_members": json.loads(row["open_member_groups_json"]),
                "body_members": json.loads(row["body_member_lines_json"]),
                "open_families": json.loads(row["open_family_groups_json"]),
                "body_families": json.loads(row["body_family_lines_json"]),
            }
        )
    return output


def groups(record: dict[str, object], rep: str, part: str) -> list[list[str]]:
    key = ("open_" if part == "OPEN" else "body_") + ("members" if rep == "MEMBER" else "families")
    value = record[key]
    if part == "OPEN":
        return [list(group) for group in value]  # type: ignore[arg-type]
    return [list(group) for line in value for group in line]  # type: ignore[arg-type]


def group_lines(record: dict[str, object], part: str) -> list[list[str]]:
    if part == "OPEN":
        return [[" ".join(group) for group in record["open_members"]]]  # type: ignore[index]
    return [[" ".join(group) for group in line] for line in record["body_members"]]  # type: ignore[index]


def fit_order2(train: list[dict[str, object]], rep: str, inventory: tuple[str, ...]) -> np.ndarray:
    index = {token: i for i, token in enumerate(inventory)}
    k = len(inventory)
    counts = np.zeros((k + 1, k + 1, k + 1))
    for record in train:
        for group in groups(record, rep, "BODY"):
            a = b = k
            for token in group:
                c = index[token]
                counts[a, b, c] += 1
                a, b = b, c
            counts[a, b, k] += 1
    return (counts + ALPHA) / (counts.sum(2, keepdims=True) + ALPHA * (k + 1))


def symbol_count(record: dict[str, object], rep: str, part: str, index: dict[str, int]) -> np.ndarray:
    output = np.zeros(len(index))
    for group in groups(record, rep, part):
        for token in group:
            output[index[token]] += 1
    return output


def smooth(count: np.ndarray) -> np.ndarray:
    return (count + ALPHA) / (count.sum() + ALPHA * len(count))


def symbol_score(record: dict[str, object], rep: str, model: dict[str, object], mu: float, local: np.ndarray, lam: float = 0.0, opening: np.ndarray | None = None) -> float:
    index, p0 = model["index"], model["p0"]
    assert isinstance(index, dict) and isinstance(p0, np.ndarray)
    k = len(index)
    total = 0.0
    for group in groups(record, rep, "BODY"):
        a = b = k
        for token in group:
            c = index[token]
            probability = (1 - mu) * p0[a, b, c] + mu * local[c]
            if lam:
                assert opening is not None
                probability = (1 - lam) * probability + lam * opening[c]
            total -= math.log2(float(probability))
            a, b = b, c
        total -= math.log2(float(p0[a, b, k]))
    return total


def build_model(train: list[dict[str, object]], all_rows: list[dict[str, object]], rep: str) -> dict[str, object]:
    member_inventory = tuple(sorted({x for record in all_rows for part in ("OPEN", "BODY") for group in groups(record, "MEMBER", part) for x in group}))
    if rep != "GROUP":
        inventory = tuple(sorted({x for record in all_rows for part in ("OPEN", "BODY") for group in groups(record, rep, part) for x in group}))
        return {"index": {x: i for i, x in enumerate(inventory)}, "p0": fit_order2(train, rep, inventory)}
    frequencies = Counter(group for record in train for line in group_lines(record, "BODY") for group in line)
    vocabulary = tuple(sorted(frequencies))
    index = {x: i for i, x in enumerate(vocabulary)}
    escape, eos = len(vocabulary), len(vocabulary) + 1
    counts = np.zeros(len(vocabulary) + 2)
    for value, count in frequencies.items():
        counts[index[value]] = count
    counts[eos] = sum(len(group_lines(record, "BODY")) for record in train)
    return {
        "index": index,
        "escape": escape,
        "eos": eos,
        "p0": (counts + ALPHA) / (counts.sum() + ALPHA * len(counts)),
        "member_index": {x: i for i, x in enumerate(member_inventory)},
        "member_p0": fit_order2(train, "MEMBER", member_inventory),
    }


def category_count(record: dict[str, object], part: str, model: dict[str, object]) -> np.ndarray:
    index = model["index"]
    assert isinstance(index, dict)
    escape = int(model["escape"])
    output = np.zeros(escape + 1)
    for line in group_lines(record, part):
        for group in line:
            output[index.get(group, escape)] += 1
    return output


def escaped_bits(value: str, model: dict[str, object]) -> float:
    index, p0 = model["member_index"], model["member_p0"]
    assert isinstance(index, dict) and isinstance(p0, np.ndarray)
    k = len(index)
    a = b = k
    total = 0.0
    for token in value.split():
        c = index[token]
        total -= math.log2(float(p0[a, b, c]))
        a, b = b, c
    return total - math.log2(float(p0[a, b, k]))


def group_score(record: dict[str, object], model: dict[str, object], mu: float, local: np.ndarray, lam: float = 0.0, opening: np.ndarray | None = None) -> float:
    index, p0 = model["index"], model["p0"]
    assert isinstance(index, dict) and isinstance(p0, np.ndarray)
    escape, eos = int(model["escape"]), int(model["eos"])
    total = 0.0
    for line in group_lines(record, "BODY"):
        for value in line:
            category = index.get(value, escape)
            probability = (1 - mu) * p0[category] + mu * local[category]
            if lam:
                assert opening is not None
                probability = (1 - lam) * probability + lam * opening[category]
            total -= math.log2(float(probability))
            if category == escape:
                total += escaped_bits(value, model)
        total -= math.log2(float(p0[eos]))
    return total


def count(record: dict[str, object], rep: str, part: str, model: dict[str, object]) -> np.ndarray:
    if rep == "GROUP":
        return category_count(record, part, model)
    return symbol_count(record, rep, part, model["index"])  # type: ignore[arg-type]


def score(record: dict[str, object], rep: str, model: dict[str, object], mu: float, local: np.ndarray, lam: float = 0.0, opening: np.ndarray | None = None) -> float:
    return group_score(record, model, mu, local, lam, opening) if rep == "GROUP" else symbol_score(record, rep, model, mu, local, lam, opening)


def local_q(records: list[dict[str, object]], rep: str, model: dict[str, object]) -> dict[str, np.ndarray]:
    total = sum((count(record, rep, "BODY", model) for record in records), start=np.zeros(len(count(records[0], rep, "BODY", model))))
    return {str(record["unit_id"]): smooth(total - count(record, rep, "BODY", model)) for record in records}


def choose(train: list[dict[str, object]], rep: str, model: dict[str, object]) -> tuple[float, float, float, float]:
    by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in train:
        by_folio[str(record["physical_folio"])].append(record)
    local = {key: value for folio_records in by_folio.values() for key, value in local_q(folio_records, rep, model).items()}
    local_bits, mu = min((sum(score(record, rep, model, weight, local[str(record["unit_id"])]) for record in train), weight) for weight in GRID)
    opens = {str(record["unit_id"]): smooth(count(record, rep, "OPEN", model)) for record in train}
    conditional_bits, lam = min(
        (
            sum(score(record, rep, model, mu, local[str(record["unit_id"])], weight, opens[str(record["unit_id"])]) for record in train),
            weight,
        )
        for weight in GRID
    )
    return mu, lam, local_bits, conditional_bits


def main() -> None:
    result = json.loads(RESULT_FILE.read_text())
    panel = load_panel()
    fold_rows = rows(FOLDS_FILE)
    fold_index = {(row["edition"], row["held_folio"], row["representation"]): row for row in fold_rows}
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("schema", result["schema"] == "Q20OB001_OPEN_BODY_RESULT_V1")
    check("status", result["status"] == "OPEN_BODY_DEPENDENCE_NOT_ABOVE_MATCHED_CONTROLS")
    check("input_hashes", all(sha(ROOT / name) == digest for name, digest in result["inputs"].items()))
    check("implementation_hash", result["implementation"] == {RUNNER.name: sha(RUNNER)})
    check("output_hashes", all(sha(ROOT / name) == digest for name, digest in result["outputs"].items()))
    check("panel_capacity", len(panel) == 510 and all(sum(row["edition"] == edition for row in panel) == 170 for edition in EDITIONS))
    check("folio_capacity", {row["physical_folio"] for row in panel} == set(FOLIOS))
    check("f84_sealed", all(not str(row["page"]).startswith("f84r") for row in panel) and result["capacity"]["f84r_rows_retained_joined_or_scored"] == 0)
    check("artifact_rows", len(fold_rows) == 72 and len(rows(RECORDS_FILE)) == 1530 and len(rows(NULL_FILE)) == 9 and len(rows(BASE_FILE)) == 168)

    errors = []
    swappable = Counter()
    for edition in EDITIONS:
        edition_rows = sorted([row for row in panel if row["edition"] == edition], key=lambda row: (FOLIOS.index(str(row["physical_folio"])), str(row["page"]), int(row["star_ordinal"])))
        for folio in FOLIOS:
            train = [row for row in edition_rows if row["physical_folio"] != folio]
            held = [row for row in edition_rows if row["physical_folio"] == folio]
            length_counts = Counter(int(row["open_member_count"]) for row in held)
            swappable[edition] += sum(count_value for count_value in length_counts.values() if count_value >= 2)
            for rep in REPS:
                artifact = fold_index[(edition, folio, rep)]
                model = build_model(train, edition_rows, rep)
                mu, lam, train_local, train_cond = choose(train, rep, model)
                local = local_q(held, rep, model)
                held_string = sum(score(record, rep, model, 0.0, local[str(record["unit_id"])]) for record in held)
                held_local = sum(score(record, rep, model, mu, local[str(record["unit_id"])]) for record in held)
                held_cond = sum(
                    score(record, rep, model, mu, local[str(record["unit_id"])], lam, smooth(count(record, rep, "OPEN", model)))
                    for record in held
                )
                if not (
                    close(mu, float(artifact["selected_local_other_body_weight"]), 1e-10)
                    and close(lam, float(artifact["selected_own_open_weight"]), 1e-10)
                    and close(train_local, float(artifact["training_local_bits"]))
                    and close(train_cond, float(artifact["training_conditional_bits"]))
                    and close(held_string, float(artifact["held_string_baseline_bits"]))
                    and close(held_local, float(artifact["held_local_body_baseline_bits"]))
                    and close(held_cond, float(artifact["held_true_open_conditional_bits"]))
                ):
                    errors.append(f"{edition}:{folio}:{rep}")
    check("all_fold_weights_and_scores", not errors, ";".join(errors[:8]))
    check("all_selected_weights_zero", all(float(row["selected_local_other_body_weight"]) == 0 and float(row["selected_own_open_weight"]) == 0 for row in fold_rows))
    check("swappable_counts", dict(swappable) == result["capacity"]["swappable_records_by_reading"] == {"ZL3b": 124, "IT2a": 126, "RF1b": 122})

    null_rows = rows(NULL_FILE)
    zero_digest = hashlib.sha256(np.zeros(WORLDS, dtype="<f8").tobytes()).hexdigest()
    check("degenerate_null_exact", all(float(row["true_gain_bits"]) == 0 and float(row["local_permutation_p"]) == 1 and float(row["maxT_three_representation_p"]) == 1 and row["null_array_sha256"] == zero_digest for row in null_rows))
    check("result_null_digests", set(result["null_digests"].values()) == {zero_digest})
    check("decision_gates_all_negative_except_capacity", result["decision_gates"] == {"capacity": True, "it_rf_member_positive_gain": False, "zl_member_beats_previous_compatible_open": False, "zl_member_maxT_p_le_0_05": False, "zl_member_nonzero_open_weight_6_of_8": False, "zl_member_positive_gain": False, "zl_member_positive_on_6_of_8_folios": False})
    report = REPORT.read_text()
    check("report_status", result["status"] in report and "zero weight in all eight primary folds" in report)
    check("claim_ceiling", all(term in result["claim_ceiling"] for term in ("no recipe", "language", "meaning", "translation")))

    passed = all(item["passed"] for item in checks)
    validation = {
        "schema": "Q20OB001_OPEN_BODY_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_RETAINED_MODEL_RECONSTRUCTION" if passed else "FAIL",
        "checks_passed": sum(bool(item["passed"]) for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "scope": "Independently reconstructs panel routing, every fitted cache weight, every held string/local/true-pair score, exact-length permutation capacity, zero-weight null consequence, and decision. With all own-OPEN weights frozen at zero, every permutation world is analytically identical and need not be resampled.",
        "result_sha256": sha(RESULT_FILE),
        "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
