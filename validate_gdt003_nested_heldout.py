#!/usr/bin/env python3
"""Independent integrity and held-out reconstruction for nested GDT003."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
S = ROOT / "experiments/semantic_assumptions/results"
RESULT = ROOT / "gdt003_nested_result.json"
VALIDATION = ROOT / "gdt003_nested_validation.json"
EDITIONS = {"ZL3b", "IT2a", "RF1b"}
checks: list[dict[str, object]] = []


def check(name: str, ok: object, detail: object = "") -> None:
    checks.append({"check": name, "pass": bool(ok), "detail": str(detail)})
    if not ok:
        raise AssertionError(f"{name}: {detail}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_rows(path: Path) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        fields = handle.readline().rstrip("\r\n").split("\t")
        index = fields.index("locus")
        for raw in handle:
            values = raw.rstrip("\r\n").split("\t")
            if values[index].startswith("f84r"):
                continue
            output.append(dict(zip(fields, values, strict=True)))
    return output


def physical_folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    return match.group(1) if match else page


def parse_operation(identifier: str) -> tuple[str, str, str]:
    family, expression = identifier.split(":", 1)
    if family.endswith("ADD"):
        return family, "", expression
    old, new = expression.split(">", 1)
    return family, old, new


def apply_operation(identifier: str, value: str) -> str | None:
    family, old, new = parse_operation(identifier)
    if family == "PREFIX_ADD":
        return new + value
    if family == "SUFFIX_ADD":
        return value + new
    if family == "PREFIX_REPLACE":
        return new + value[len(old):] if value.startswith(old) and len(value) > len(old) else None
    if family == "SUFFIX_REPLACE":
        return value[:-len(old)] + new if value.endswith(old) and len(value) > len(old) else None
    raise ValueError(identifier)


result = json.loads(RESULT.read_text(encoding="utf-8"))
check("schema", result["schema"] == "GDT003_NESTED_HELDOUT_RESULT_V1")
check("status", result["status"] == "LIMITED/LOCAL COMPOSITION ONLY")
check("frozen_holdout", result["holdout"]["unit"] == "COMPLETE_PHYSICAL_FOLIO")
check("f84r_flag", result["holdout"]["f84r_formal_payload_retained_joined_or_scored"] is False)
check("claim_ceiling", all(term in result["claim_ceiling"] for term in ("no morpheme", "language", "translation")))

for relative, digest in {**result["inputs"], **result["implementation"], **result["outputs"]}.items():
    check("hash_" + relative, sha256(ROOT / relative) == digest)
content = dict(result)
recorded_content_hash = content.pop("result_content_sha256")
check("result_content_hash", canonical_sha(content) == recorded_content_hash)

# Independently reconstruct the strict three-reading physical corpus.
metadata = {row["source_group_id"]: row for row in guarded_rows(S / "source_separator_transcription.tsv")}
aligned: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
for row in guarded_rows(S / "source_sta_group_alignment.tsv"):
    meta = metadata[row["source_group_id"]]
    aligned[row["locus"], int(row["source_group_index"])][row["edition"]] = {
        "surface": row["nearest_basic_eva_primary"].lower(),
        "group_count": row["source_group_count"],
        "locus": row["locus"],
        "page": meta["page"],
        "folio": physical_folio(meta["page"]),
    }

records: list[dict[str, str]] = []
rejected = 0
for edition_map in aligned.values():
    if (
        set(edition_map) == EDITIONS
        and len({item["surface"] for item in edition_map.values()}) == 1
        and len({item["group_count"] for item in edition_map.values()}) == 1
    ):
        records.append(edition_map["ZL3b"])
    else:
        rejected += 1
folios = sorted({row["folio"] for row in records})
check("strict_corpus_count", len(records) == result["corpus"]["strict_physical_groups"] == 18760)
check("rejected_count", rejected == result["corpus"]["ambiguous_or_topology_disagreement_keys_excluded"] == 20704)
check("physical_folio_count", len(folios) == result["corpus"]["physical_folios"] == 102)
check("no_f84r_record", not any(row["page"].startswith("f84r") for row in records))

by_folio: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in records:
    by_folio[row["folio"]].append(row)

transforms = rows(ROOT / "gdt003_nested_transformations.tsv")
fold_summary = rows(ROOT / "gdt003_nested_fold_summary.tsv")
correct = rows(ROOT / "gdt003_nested_correct_predictions.tsv")
tops = rows(ROOT / "gdt003_nested_top_predictions.tsv")
baseline = rows(ROOT / "gdt003_nested_baseline_comparison.tsv")

check("fold_ids_exact", {row["fold_id"] for row in fold_summary} == set(folios) and len(fold_summary) == 102)
check("transformation_count", len(transforms) == result["counts"]["transformation_rows"] == 42019)
check("correct_export_count", len(correct) == result["counts"]["correct_prediction_artifact_rows"] == 950)
check("top_export_count", len(tops) == result["counts"]["top_prediction_artifact_rows"] == 5100)

# Rebuild every fold's operation-set hash from the public selected-rule table.
transform_by_fold: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in transforms:
    transform_by_fold[row["fold_id"]].append(row)
for summary in fold_summary:
    fold = summary["fold_id"]
    selected = sorted(transform_by_fold[fold], key=lambda row: row["operation_id"])
    payload = [
        {
            "operation_id": row["operation_id"],
            "edge_types": int(row["training_edge_types"]),
            "edge_occurrence_support": int(row["training_edge_occurrence_support"]),
            "edge_folios": int(row["training_edge_folios"]),
            "rank": int(row["rank_within_stratum"]),
        }
        for row in selected
    ]
    check("operation_hash_" + fold, canonical_sha(payload) == summary["operation_set_sha256"])
    check("operation_count_" + fold, len(selected) == int(summary["discovered_eligible_operations"]))

# Verify every published exact prediction from independently reconstructed folds.
scope_counts = Counter(row["evaluation_scope"] for row in correct)
check("correct_scope_counts", scope_counts == Counter({"ALL_DISCOVERED_ALGEBRA": 925, "PREDECLARED_Q_RIGHT_SUBGROUP": 25}))
correct_by_scope_fold = Counter((row["evaluation_scope"], row["fold_id"]) for row in correct)
for summary in fold_summary:
    fold = summary["fold_id"]
    check("broad_hits_" + fold, correct_by_scope_fold["ALL_DISCOVERED_ALGEBRA", fold] == int(summary["exact_correct"]))
    check("q_hits_" + fold, correct_by_scope_fold["PREDECLARED_Q_RIGHT_SUBGROUP", fold] == int(summary["q_right_correct"]))

for index, row in enumerate(correct, 1):
    fold = row["fold_id"]
    train = [item for other, items in by_folio.items() if other != fold for item in items]
    train_forms = {item["surface"] for item in train}
    held = by_folio[fold]
    held_forms = {item["surface"] for item in held}
    base, ax, bx, target = (row[key] for key in ("base_X", "A_X", "B_X", "predicted_fourth"))
    operation_a, operation_b = row["operation_A"], row["operation_B"]
    check(f"formula_{index}", apply_operation(operation_a, base) == ax and apply_operation(operation_b, base) == bx)
    check(f"commuting_fourth_{index}", apply_operation(operation_a, bx) == target == apply_operation(operation_b, ax))
    check(f"training_firewall_{index}", {base, ax, bx} <= train_forms and target not in train_forms)
    check(f"held_presence_{index}", target in held_forms and row["target_present"] == "1")
    expected_loci = ";".join(sorted({item["locus"] for item in held if item["surface"] == target}))
    check(f"held_loci_{index}", row["target_loci"] == expected_loci)
    if row["evaluation_scope"] == "PREDECLARED_Q_RIGHT_SUBGROUP":
        operations = {operation_a, operation_b}
        q_ok = "PREFIX_ADD:q" in operations
        right_ok = any(
            op.startswith("SUFFIX_") and ({parse_operation(op)[1], parse_operation(op)[2]} & {"dy", "dal", "dar"})
            for op in operations
        )
        check(f"q_right_membership_{index}", q_ok and right_ok and row["q_right_named_subgroup"] == "1")

# Exact aggregate arithmetic and top-k counts are recoverable from positive rows.
baseline_map = {(row["scope"], row["model"]): row for row in baseline}
score_models = {
    "NESTED_PARADIGM": "paradigm_rank_in_fold",
    "CHARACTER_ORDER2_KT": "character_order2_kt_rank_in_fold",
    "CHARACTER_ORDER4_KT": "character_order4_kt_rank_in_fold",
    "VISIBLE_WHOLE_GROUP_FREQUENCY": "visible_whole_group_frequency_rank_in_fold",
    "NEAREST_EDIT_DISTANCE": "nearest_edit_rank_in_fold",
}
scope_to_count = {"ALL_DISCOVERED_ALGEBRA": 1017225, "PREDECLARED_Q_RIGHT_SUBGROUP": 9754}
for scope, prediction_count in scope_to_count.items():
    positive_rows = [row for row in correct if row["evaluation_scope"] == scope]
    for model, rank_field in score_models.items():
        row = baseline_map[scope, model]
        check("prediction_count_" + scope + model, int(row["predictions"]) == prediction_count)
        check("exact_count_" + scope + model, int(row["exact_correct"]) == len(positive_rows))
        check("precision_" + scope + model, math.isclose(float(row["precision"]), len(positive_rows) / prediction_count))
        check("top1_" + scope + model, int(row["top1_hits"]) == sum(int(item[rank_field]) == 1 for item in positive_rows))
        check("top5_" + scope + model, int(row["top5_hits"]) == sum(int(item[rank_field]) <= 5 for item in positive_rows))

all_paradigm = baseline_map["ALL_DISCOVERED_ALGEBRA", "NESTED_PARADIGM"]
all_strings = [baseline_map["ALL_DISCOVERED_ALGEBRA", model] for model in score_models if model != "NESTED_PARADIGM"]
q_paradigm = baseline_map["PREDECLARED_Q_RIGHT_SUBGROUP", "NESTED_PARADIGM"]
q_strings = [baseline_map["PREDECLARED_Q_RIGHT_SUBGROUP", model] for model in score_models if model != "NESTED_PARADIGM"]
broad_advantage = float(all_paradigm["average_precision"]) - max(float(row["average_precision"]) for row in all_strings)
q_advantage = float(q_paradigm["average_precision"]) - max(float(row["average_precision"]) for row in q_strings)
check("broad_AP_advantage", math.isclose(broad_advantage, result["prediction"]["paradigm_AP_advantage_over_best_string"]))
check("q_AP_advantage", math.isclose(q_advantage, result["prediction"]["q_right_AP_advantage_over_best_string"]))
check("broad_small_positive", 0 < broad_advantage < 0.02)
check("q_subgroup_loses", q_advantage < 0)
check("permutation_arithmetic", math.isclose(result["permutation"]["inclusive_plus_one_p"], (result["permutation"]["exceedances"] + 1) / (result["permutation"]["worlds"] + 1)))
check("decision_reconstruction", result["status"] == "LIMITED/LOCAL COMPOSITION ONLY")

# The nine previously highlighted forms were not supplied to discovery but all
# are independently present among the broad nested hits.
old = json.loads((ROOT / "gdt003_results.json").read_text(encoding="utf-8"))
old_nine = {(row["fold_id"], row["predicted_fourth"]) for row in old["highest_value_model_hidden_predictions"]}
broad_hits = {(row["fold_id"], row["predicted_fourth"]) for row in correct if row["evaluation_scope"] == "ALL_DISCOVERED_ALGEBRA"}
check("old_nine_recovered", len(old_nine & broad_hits) == result["counts"]["old_gdt003_nine_recovered"] == 9)

ledger = rows(ROOT / "GDT002_YOLO_LEDGER.tsv")
check("ledger_registration", sum(row["checkpoint_id"] == "GDT003_CKPT002" for row in ledger) == 1)
check("ledger_result", sum(row["checkpoint_id"] == "GDT003_CKPT003" for row in ledger) == 1)

validation = {
    "artifact": "GDT003_NESTED_HELDOUT_VALIDATION_V1",
    "status": "PASS_INDEPENDENT_HOLDOUT_AND_HIT_RECONSTRUCTION",
    "checks_passed": len(checks),
    "checks": checks,
    "result_sha256": sha256(RESULT),
    "validator_sha256": sha256(Path(__file__)),
    "scope": (
        "Independent reconstruction of the strict three-reading corpus, f84r firewall, every fold operation-set hash, "
        "all 950 published exact-hit records and formulas, target absence from training, held-folio target/locus presence, "
        "q/right membership, aggregate/top-k arithmetic, decision, hashes, and ledger. AP/AUC score order and the "
        "4096-world permutation stream are producer-reproducible rather than independently regenerated here."
    ),
}
VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(validation["status"], len(checks))
