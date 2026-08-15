#!/usr/bin/env python3
"""Independent class and cell reconstruction for GDT078."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PAIRS = ROOT / "gdt076_register_host_rates.tsv"
RESULT = ROOT / "gdt078_result.json"
ATLAS = ROOT / "gdt078_page_host_class_atlas.tsv"
CELLS = ROOT / "gdt078_paradigm_cells.tsv"
PREDICTIONS = ROOT / "gdt078_hpr4_predictions.tsv"
MODEL = ROOT / "gdt078_hpr4_model.json"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt078_validation.json"
FAMILIES = ("aiin", "air", "ain", "ar", "al")


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    source = read(SOURCE)
    pairs = read(PAIRS)
    result = json.loads(RESULT.read_text())
    atlas = read(ATLAS)
    cells = read(CELLS)
    model = json.loads(MODEL.read_text())
    predictions = read(PREDICTIONS)
    checks = {}
    by_host = defaultdict(list)
    for row in pairs:
        by_host[row["page_host"]].append(row)
    stable = []
    for page_host, rows in sorted(by_host.items()):
        folds = len(rows)
        if (
            folds >= 3
            and sum(int(row["training_aiin_high"]) for row in rows) / folds >= 0.60
            and sum(int(row["held_aiin_high"]) for row in rows) / folds >= 0.60
            and sum(row["training_aiin_high"] == row["held_aiin_high"] for row in rows) / folds >= 0.60
        ):
            stable.append(page_host)
    checks["stable_rule"] = stable == result["stable_aiin_high_hosts"] == ["d", "ok", "yk", "yt"]
    checks["atlas"] = (
        len(atlas) == result["atlas_hosts"] == 69
        and {row["page_host"] for row in atlas if row["formal_class"] == "AIIN_STABLE_HIGH"} == set(stable)
    )
    source_index = defaultdict(list)
    for row in source:
        source_index[row["page_host"], row["register"], row["right_family"]].append(row)
    cell_ok = True
    for row in cells:
        selected = source_index[row["page_host"], row["register"], row["right_family"]]
        cell_ok &= (
            len(selected) == int(row["occurrences"])
            and len({value["physical_folio"] for value in selected}) == int(row["physical_folios"])
            and row["cell_state"] == ("OBSERVED" if selected else "ABSENT_IN_REGISTER")
            and (not selected or (row["example_token"] == selected[0]["token"] and row["example_locus"] == selected[0]["locus"]))
        )
    checks["paradigm_cells"] = (
        cell_ok
        and len(cells) == result["paradigm_cells"] == 100
        and sum(row["cell_state"] == "OBSERVED" for row in cells) == result["observed_paradigm_cells"] == 82
    )
    complete = [
        host for host in stable
        if all(any(row["page_host"] == host and row["right_family"] == family for row in source) for family in FAMILIES)
    ]
    checks["complete_five_renderer"] = complete == result["complete_five_renderer_hosts"] == stable
    checks["model"] = (
        model["name"] == "HPR4_HOST_COMPATIBILITY_RECORD_COMPILER"
        and model["stable_aiin_high_hosts"] == stable
        and model["complete_manuscript_wide_five_renderer_hosts"] == stable
        and model["evidence"]["linguistic_morphology_over_string_baseline"] == "NOT_DISTINGUISHABLE_GDT003"
        and model["f84r"] == "SEALED_NOT_TARGETED"
    )
    checks["prospective_prediction"] = (
        len(predictions) == result["frozen_predictions"] == 1
        and predictions[0]["prediction_id"] == "HPR4_P01"
        and predictions[0]["status"] == "FROZEN_NOT_RUN"
        and predictions[0]["future_target"].startswith("FRESH_NON_F84_")
        and "d,ok,yk,yt" in predictions[0]["formal_predictor"]
    )
    checks["negative_evidence"] = "GDT003" in result["negative_evidence"] and "NOT_DISTINGUISHABLE" in result["negative_evidence"]
    checks["f84_seal"] = not any(result["f84r"].values())
    body = dict(result); claimed = body.pop("result_content_sha256")
    checks["content_hash"] = content_sha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT078_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT078_HPR4_FORMAL_PARADIGM_LEXICON_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_CLASS_AND_CELL_RECONSTRUCTION" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently reconstructs the stable-high class rule, complete source-cell inventory/examples, manuscript-wide five-renderer coverage, HPR4 model/prediction/negative evidence, seals, hashes and ledger.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
