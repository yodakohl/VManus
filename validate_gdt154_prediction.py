#!/usr/bin/env python3
"""Independent source-only validation of the GDT154 target freeze."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
H = R / "gdt062_right_family_inventory.tsv"; S = R / "gdt089_os_cases.tsv"
T = R / "gdt154_os_visual_predictions.tsv"; P = R / "gdt154_prediction.json"
OUT = R / "gdt154_prediction_validation.json"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main():
    prediction = json.loads(P.read_text(encoding="utf8")); seeds = read(S); stored = read(T)
    excluded = {row["locus"].split(".")[0] for row in seeds}
    rebuilt = []
    with H.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84") or row["section"] != "H" or row["page"] in excluded: continue
            if (row["page_host"], row["token"], row["wrapper"], row["right_family"], row["dy_closure"], row["b3"]) == ("os", "chos", "ch", "NONE", "0", "0"):
                rebuilt.append((row["locus"], row["page"], row["physical_folio"]))
    rebuilt.sort(key=lambda item: (int("".join(ch for ch in item[2] if ch.isdigit())), item[1], item[0]))
    all_eligible = list(rebuilt); rebuilt = rebuilt[:2]
    checks = {
        "schema": prediction["schema"] == "GDT154_OS_VISUAL_TRANSFER_PREDICTION_V1",
        "status": prediction["status"] == "FROZEN_BEFORE_TARGET_IMAGE_ACCESS",
        "seed_pages": excluded == {"f88v", "f100v"},
        "eligible_candidates": all_eligible == [("f15r.9", "f15r", "f15"), ("f27r.4", "f27r", "f27"), ("f29r.4", "f29r", "f29"), ("f33r.7", "f33r", "f33"), ("f90v2.5", "f90v2", "f90")] and prediction["eligible_candidates"] == 5,
        "exact_targets": rebuilt == [("f15r.9", "f15r", "f15"), ("f27r.4", "f27r", "f27")],
        "stored_rows": [(r["locus"], r["page"], r["physical_folio"]) for r in stored] == rebuilt,
        "frozen_states": all(r["predicted_dark_leaf"] == r["predicted_light_root"] == "POSITIVE" and r["predicted_joint_state"] == "DARK_LEAF_AND_LIGHT_ROOT" for r in stored),
        "ownership_caveat": all(r["occurrence_scope"] == "RUNNING_TEXT_PAGE_LEVEL_NO_SINGULAR_OWNERSHIP" for r in stored),
        "image_access": all(r["image_access_at_freeze"] == "NOT_OPENED_FOR_GDT154" for r in stored),
        "f84_absent": not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in stored) and all(v is False for v in prediction["f84r"].values()),
        "input_hashes": all((R / n).exists() and sha(R / n) == h for n, h in prediction["inputs"].items()),
        "implementation_hash": all((R / n).exists() and sha(R / n) == h for n, h in prediction["implementation"].items()),
        "output_hash": sha(T) == prediction["outputs"][T.name],
        "document_hash": all((R / n).exists() and sha(R / n) == h for n, h in prediction["documents"].items()),
    }
    content = dict(prediction); recorded = content.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == recorded
    status = "PASS_INDEPENDENT_SOURCE_ONLY_TARGET_FREEZE" if all(checks.values()) else "FAIL"
    result = {"schema": "GDT154_OS_VISUAL_TRANSFER_PREDICTION_VALIDATION_V1", "status": status,
              "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
              "prediction_sha256": sha(P), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__": main()
