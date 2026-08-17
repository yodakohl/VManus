#!/usr/bin/env python3
"""Independent retained-output validation for GDT176."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


CLASSES = ("OPENER", "OPERATION", "INGREDIENT", "TOOL", "CLOSER")


def rows(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def near(a: float, b: float, tolerance: float = 3e-6) -> bool:
    return abs(a - b) <= tolerance * max(1, abs(a), abs(b))


def model_metrics(rr: list[dict[str, str]]) -> tuple[int, float, float, float]:
    n = len(rr)
    correct = sum(r["oracle_role"] == r["predicted_role"] for r in rr)
    f1s = []
    for role in CLASSES:
        tp = sum(r["oracle_role"] == role and r["predicted_role"] == role for r in rr)
        fp = sum(r["oracle_role"] != role and r["predicted_role"] == role for r in rr)
        fn = sum(r["oracle_role"] == role and r["predicted_role"] != role for r in rr)
        f1s.append(2 * tp / max(1, 2 * tp + fp + fn))
    bits = -sum(math.log2(max(float(r[f"p_{r['oracle_role'].lower()}"]), 1e-12)) for r in rr) / n
    return n, correct / n, sum(f1s) / len(f1s), bits


def main() -> None:
    result = json.loads(Path("gdt176_result.json").read_text())
    source = json.loads(Path("gdt176_source_freeze.json").read_text())
    units = rows("gdt176_external_role_units.tsv")
    folds = rows("gdt176_external_role_folds.tsv")
    predictions = rows("gdt176_external_role_predictions.tsv")
    confusion = rows("gdt176_external_role_confusion.tsv")
    projections = rows("gdt176_q20_role_like_projection.tsv")
    summary = rows("gdt176_q20_role_like_summary.tsv")
    abstract_summary = rows("gdt176_q20_abstract_role_summary.tsv")
    atlas = rows("gdt176_q20_opaque_host_role_atlas.tsv")
    fields = rows("gdt127_q20_field_inventory.tsv")
    checks: list[tuple[str, bool]] = []

    checks.append(("source_status", source["status"] == "EXTERNAL_ROLE_CALIBRATION_SOURCE_FROZEN"))
    checks.append(("external_counts", len(units) == result["external_units"] == 22394))
    checks.append(("external_roles", set(r["oracle_role"] for r in units) == set(CLASSES)))
    checks.append(("six_held_collections", set(r["held_collection"] for r in folds) == {"b4", "b6", "br1", "bs1", "gr1", "w1"}))
    checks.append(("prediction_models", set(r["model"] for r in predictions) == {"POSITION_LENGTH", "POSITION_LENGTH_PLUS_OPAQUE_RECURRENCE"}))

    fold_index = {(r["held_collection"], r["model"]): r for r in folds}
    for key, rr in defaultdict(list, {
        key: [r for r in predictions if (r["held_collection"], r["model"]) == key]
        for key in {(r["held_collection"], r["model"]) for r in predictions}
    }).items():
        n, accuracy, macro_f1, bits = model_metrics(rr)
        stored = fold_index[key]
        checks.append((f"fold_{key[0]}_{key[1]}", n == int(stored["n"]) and near(accuracy, float(stored["accuracy"])) and near(macro_f1, float(stored["macro_f1"])) and near(bits, float(stored["bits_per_unit"]))))

    chosen = result["projection_model_selected_on_external_folds_only"]
    model_bits = {
        model: sum(float(r["bits_per_unit"]) * int(r["n"]) for r in folds if r["model"] == model)
        for model in ("POSITION_LENGTH", "POSITION_LENGTH_PLUS_OPAQUE_RECURRENCE")
    }
    checks.append(("external_selection", chosen == min(model_bits, key=model_bits.get) == "POSITION_LENGTH"))
    checks.append(("position_positive_all_folds", result["held_collection_results"]["POSITION_LENGTH"]["positive_folds_vs_prior"] == 6))

    chosen_predictions = [r for r in predictions if r["model"] == chosen]
    rebuilt_confusion = Counter((r["oracle_role"], r["predicted_role"]) for r in chosen_predictions)
    checks.append(("confusion", all(int(r["count"]) == rebuilt_confusion[(r["oracle_role"], r["predicted_role"])] for r in confusion)))

    checks.append(("q20_count", len(projections) == result["q20_projected_fields"] == len(fields) == 4443))
    checks.append(("q20_no_f84", all(not r["page"].startswith("f84") and not r["field_id"].startswith("f84") for r in projections) and all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in fields)))
    checks.append(("q20_probabilities", all(near(sum(float(r[f"p_{role.lower()}"]) for role in CLASSES), 1, 2e-8) for r in projections)))
    rebuilt_summary = Counter((r["edition"], r["record_scope"], r["predicted_role_like"]) for r in projections)
    checks.append(("q20_summary", all(int(r["field_count"]) == rebuilt_summary[(r["edition"], r["record_scope"], r["predicted_role_like"])] for r in summary) and sum(int(r["field_count"]) for r in summary) == len(projections)))
    rebuilt_abstract = Counter((r["edition"], r["record_scope"], r["supported_abstract_role_like"]) for r in projections)
    checks.append(("q20_abstract_summary", all(int(r["field_count"]) == rebuilt_abstract[(r["edition"], r["record_scope"], r["supported_abstract_role_like"])] for r in abstract_summary) and sum(int(r["field_count"]) for r in abstract_summary) == len(projections)))

    field_map = {r["field_id"]: r for r in fields if r["edition"] == "ZL3b"}
    host_events: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in projections:
        if r["edition"] == "ZL3b":
            f = field_map[r["field_id"]]
            host = f["page_hosts"].split("|")[0]
            if host:
                host_events[host].append((r["predicted_role_like"], r["physical_folio"]))
    atlas_map = {r["page_host"]: r for r in atlas}
    checks.append(("atlas_host_set", set(atlas_map) == set(host_events)))
    checks.append(("atlas_counts", all(int(atlas_map[h]["event_count"]) == len(ev) and int(atlas_map[h]["physical_folio_count"]) == len({f for _, f in ev}) for h, ev in host_events.items())))

    checks.append(("input_hashes", all(sha(p) == d for p, d in result["inputs"].items())))
    checks.append(("output_hashes", all(sha(p) == d for p, d in result["outputs"].items())))
    checks.append(("document_hashes", all(sha(p) == d for p, d in result["documents"].items())))
    checks.append(("implementation_hash", all(sha(p) == d for p, d in result["implementation"].items())))
    clean = dict(result); expected = clean.pop("content_hash")
    actual = hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    checks.append(("content_hash", actual == expected))
    checks.append(("partial_class_scope", result["selected_model_class_metrics"]["TOOL"]["recall"] == 0 and result["selected_model_class_metrics"]["OPENER"]["recall"] < 0.02))
    checks.append(("claim_ceiling", result["projection_is_role_like_not_semantic_confirmation"] and not result["f84r_accessed"] and result["status"].startswith("PARTIAL_")))

    failed = [name for name, ok in checks if not ok]
    validation = {
        "experiment": result["experiment"],
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha("gdt176_result.json"),
        "report_sha256": sha("GDT176_READABLE_RECIPE_ROLE_CALIBRATION_REPORT.md"),
        "counterexamples_sha256": sha("gdt176_counterexamples.tsv"),
        "variant_log_sha256": sha("gdt176_variant_log.tsv"),
        "scope": "independent retained-prediction arithmetic, joins, hashes, f84 exclusion, and claim-state validation; classifier optimization is not independently refit",
    }
    Path("gdt176_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"{validation['status']} {validation['checks_passed']}/{validation['checks_total']}")
    if failed:
        print(failed)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
