#!/usr/bin/env python3
"""Integrity and claim-ceiling validation for GDT072."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt072_result.json"
EVIDENCE = ROOT / "gdt072_hpr3_evidence.tsv"
PREDICTIONS = ROOT / "gdt072_hpr3_predictions.tsv"
MODEL = ROOT / "gdt072_hpr3_model.json"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt072_validation.json"


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(value):
    encoded = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def main():
    result = json.loads(RESULT.read_text())
    evidence = read_tsv(EVIDENCE)
    predictions = read_tsv(PREDICTIONS)
    model = json.loads(MODEL.read_text())
    checks = {}

    expected_inputs = {f"gdt{i:03d}_result.json" for i in range(59, 72)}
    checks["complete_prior_chain"] = set(result["inputs"]) == expected_inputs
    checks["prior_chain_f84_sealed"] = all(
        not any(json.loads((ROOT / name).read_text())["f84r"].values())
        for name in expected_inputs
    )
    checks["evidence_ids"] = (
        [row["evidence_id"] for row in evidence]
        == [f"E{i:02d}" for i in range(1, 10)]
        and len({row["layer"] for row in evidence}) == 9
        and result["evidence_rows"] == 9
    )
    checks["negative_evidence_retained"] = {
        row["layer"]: row["status"] for row in evidence
    }["PAGE_HOST_IDENTITY"] == "EXTERNAL_LOCALIZATION_NOT_SUPPORTED"
    checks["prediction_set"] = (
        [row["prediction_id"] for row in predictions]
        == ["HPR3_P01", "HPR3_P02", "HPR3_P03", "HPR3_P04"]
        and all(row["status"] == "FROZEN_NOT_RUN" for row in predictions)
        and all(row["future_target"].startswith("FRESH_NON_F84_") for row in predictions)
        and result["frozen_predictions"] == 4
    )
    checks["model_generator"] = (
        model["schema"] == "GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_MODEL_V1"
        and model["name"] == result["model_name"]
        and model["generator"]["line"]
        == "Q2_ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?"
        and model["generator"]["field"]
        == "WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?"
        and set(model["candidate_classes"])
        == {"HCLASS_RAIIN_HIGH", "HCLASS_WSH_HIGH", "HCLASS_FO_ACTIVE"}
    )
    checks["model_seal"] = model["f84r"] == "SEALED_NOT_TARGETED"
    checks["result_seal"] = not any(result["f84r"].values())
    forbidden = (
        "english gloss",
        "plaintext established",
        "translation established",
        "semantic role confirmed",
    )
    corpus = json.dumps(model).lower() + "\n" + RESULT.read_text().lower()
    checks["claim_ceiling"] = (
        all(term not in corpus for term in forbidden)
        and "no semantic class" in result["claim_ceiling"].lower()
        and "prospective" in result["status"].lower()
    )
    body = dict(result)
    claimed = body.pop("result_content_sha256")
    checks["content_hash"] = content_sha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    ledger_rows = [
        row for row in read_tsv(LEDGER) if row["checkpoint_id"] == "GDT072_CKPT001"
    ]
    checks["ledger"] = (
        len(ledger_rows) == 1
        and ledger_rows[0]["status"] == result["status"]
        and ledger_rows[0]["result_artifact"] == RESULT.name
        and ledger_rows[0]["holdout_page"] == "f84r"
        and ledger_rows[0]["images_opened"] == "0"
    )

    passed = all(checks.values())
    validation = {
        "schema": "GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_VALIDATION_V1",
        "status": "PASS_INTEGRITY_AND_FREEZE_CHECKS" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": (
            "Checks the complete GDT059-GDT071 hash chain and f84 seal, exact "
            "evidence and prediction inventories, model grammar/classes, frozen "
            "status, claim ceiling, hashes, and branch ledger. It does not rerun "
            "the archived experiments or score prospective targets."
        ),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
