#!/usr/bin/env python3
"""Independent structural validator for GDT398."""

from __future__ import annotations

import ast
import csv
import hashlib
import io
import itertools
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt398_opaque_joint_tuple_predictive_equivalence_preflight"
ART = EXP / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
ATLAS = ROOT / "gdt327_joint_tuple_atlas.tsv"
SEPARATORS = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
RUNNER = EXP / "src/run.py"
RESULT = ART / "result.json"
OUTPUT = ART / "validation.json"

FOLD_FIELDS = (
    "outer_fold", "held_folios", "selected_fraction", "selected_k", "training_types", "held_events", "model",
    "bits_total", "bits_previous", "bits_next", "bits_placement", "bits_boundary_before", "bits_boundary_after",
    "raw_gain_vs_exact", "partition_cost", "selector_cost", "selector_paid_gain", "positive",
)
CLUSTER_FIELDS = (
    "outer_fold", "joint_tuple_id", "latent_form_id", "selected_fraction", "training_events", "training_folios", "cluster_size",
)
MERGE_FIELDS = (
    "tuple_a", "tuple_b", "coassignment_stability", "eligible_folds", "direct_merge_folds", "support_events", "support_folios",
    "held_gain_contribution", "page_host_same", "string_group_same", "normalized_edit_diagnostic", "supporting_views",
)
STATUSES = {
    "PREDICTIVE_LATENT_TUPLE_EQUIVALENCE_SUPPORTED",
    "LATENT_SHARING_WEAK_NOT_A_LEXICON_EQUIVALENCE",
    "APPARENT_EQUIVALENCE_EXPLAINED_BY_EXISTING_STRUCTURE",
    "JOINT_TUPLE_LEXICON_NOT_COMPRESSIBLE_BY_FREE_PREDICTIVE_EQUIVALENCE",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: dict) -> str:
    clean = {k: v for k, v in value.items() if k != "content_sha256"}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return tuple(reader.fieldnames or ()), list(reader)


def balanced_folds(rows: list[dict]) -> tuple[dict[str, int], Counter]:
    counts = Counter(row["physical_folio"] for row in rows)
    loads = [0] * 11
    mapping = {}
    for folio, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        fold = min(range(11), key=lambda k: (loads[k], k))
        mapping[folio] = fold
        loads[fold] += n
    return mapping, Counter({i: loads[i] for i in range(11)})


def adjusted_rand(mapping_a: dict[str, str], mapping_b: dict[str, str]) -> float:
    common = sorted(set(mapping_a) & set(mapping_b))
    if len(common) < 2:
        return 1.0
    choose2 = lambda n: n * (n - 1) / 2
    table = Counter((mapping_a[t], mapping_b[t]) for t in common)
    rows = Counter(mapping_a[t] for t in common)
    cols = Counter(mapping_b[t] for t in common)
    index = sum(choose2(v) for v in table.values())
    row_sum = sum(choose2(v) for v in rows.values())
    col_sum = sum(choose2(v) for v in cols.values())
    total = choose2(len(common))
    expected = row_sum * col_sum / total
    maximum = 0.5 * (row_sum + col_sum)
    return (index - expected) / (maximum - expected) if maximum != expected else 1.0


def guarded_view_hash(loci: list[str]) -> tuple[str, int]:
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SEPARATORS), "--selector", "locus"]
    for locus in loci:
        cmd.extend(("--allow", locus))
    cmd.extend((
        "--columns", "edition,locus,page,source_group_index,left_separator,right_separator,paragraph_start,paragraph_end,ivtff_group_raw",
        "--forbid-prefix", "f84",
    ))
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    selected = [row for row in csv.DictReader(io.StringIO(proc.stdout), delimiter="\t") if row["edition"] == "ZL3b"]
    if any(row["page"].lower().startswith("f84") or row["locus"].lower().startswith("f84") for row in selected):
        raise RuntimeError("guarded validator query retained f84")
    return hashlib.sha256(proc.stdout.encode()).hexdigest(), len(selected)


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("refusing to overwrite GDT398 validation")
    checks: dict[str, bool] = {}
    checks["gdt327_hashes"] = (
        sha256(INTER) == "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9"
        and sha256(ATLAS) == "470d34efb4eac432f50d2af1e997d4b5c0ccc4758bcd82d711daa4d7756b9e71"
    )
    _, inter = read_tsv(INTER)
    checks["source_cardinality"] = len(inter) == 8448 and len({r["joint_tuple_id"] for r in inter}) == 1676 and len({r["physical_folio"] for r in inter}) == 91
    checks["source_f84_free"] = not any(
        value.lower().startswith("f84") for row in inter for value in (row["page"], row["physical_folio"], row["locus"])
    )
    fold_map, fold_loads = balanced_folds(inter)
    checks["eleven_balanced_folds"] = len(fold_loads) == 11 and max(fold_loads.values()) - min(fold_loads.values()) <= 100

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks["result_schema_status"] = result.get("schema") == "GDT398_OPAQUE_JOINT_TUPLE_EQUIVALENCE_RESULT_V1" and result.get("status") in STATUSES
    checks["content_hash"] = result.get("content_sha256") == canonical_hash(result)
    safe_hash, safe_rows = guarded_view_hash(sorted({r["locus"] for r in inter}))
    checks["guarded_separator_view"] = safe_rows == 8448 and result["guarded_source"]["selected_view_sha256"] == safe_hash

    fold_header, folds = read_tsv(ART / "fold_scores.tsv")
    cluster_header, clusters = read_tsv(ART / "cluster_summary.tsv")
    merge_header, merges = read_tsv(ART / "stable_merges.tsv")
    counter_header, counters = read_tsv(ART / "counterexamples.tsv")
    checks["exact_tsv_headers"] = (
        fold_header == FOLD_FIELDS and cluster_header == CLUSTER_FIELDS and merge_header == MERGE_FIELDS
        and counter_header == MERGE_FIELDS + ("counterexample_reason",)
    )
    checks["fold_row_family"] = len(folds) == 11 * 13 and {int(r["outer_fold"]) for r in folds} == set(range(11))
    required_models = {
        "GLOBAL_FREQUENCY", "EXACT_TUPLE", "PAGE_HOST", "GDT338_NORMALIZED",
        "STRING_SIMILARITY", "PLACEMENT_FREQUENCY", "LEARNED_LATENT_CLASS",
    }
    checks["exact_model_family"] = all(
        Counter(r["model"] for r in folds if int(r["outer_fold"]) == fold)
        == Counter({**{name: 1 for name in required_models}, "CANDIDATE_CUT": 6})
        for fold in range(11)
    )
    checks["held_fold_binding"] = all(
        set(row["held_folios"].split("|")) == {folio for folio, fold in fold_map.items() if fold == int(row["outer_fold"])}
        and int(row["held_events"]) == fold_loads[int(row["outer_fold"])]
        for row in folds
    )
    checks["gdt338_exact_alias"] = all(
        next(r for r in folds if int(r["outer_fold"]) == fold and r["model"] == "EXACT_TUPLE")["bits_total"]
        == next(r for r in folds if int(r["outer_fold"]) == fold and r["model"] == "GDT338_NORMALIZED")["bits_total"]
        for fold in range(11)
    )
    selected = [r for r in folds if r["model"] == "LEARNED_LATENT_CLASS"]
    checks["one_selected_per_fold"] = len(selected) == 11 and all(r["selected_fraction"] in {"1.00", "0.90", "0.75", "0.60", "0.45", "0.30"} for r in selected)
    by_fold_clusters = defaultdict(list)
    for row in clusters:
        by_fold_clusters[int(row["outer_fold"])].append(row)
    checks["cluster_summary_matches_selected_k"] = all(
        len({r["latent_form_id"] for r in by_fold_clusters[fold]}) == int(next(r for r in selected if int(r["outer_fold"]) == fold)["selected_k"])
        and all(re.fullmatch(r"T\d{4}", r["joint_tuple_id"]) and re.fullmatch(r"LATENT_FORM_\d{4}", r["latent_form_id"]) for r in by_fold_clusters[fold])
        for fold in range(11)
    )

    raw_gain = sum(float(r["raw_gain_vs_exact"]) for r in selected)
    partition_cost = sum(float(r["partition_cost"]) for r in selected)
    selector_cost = sum(float(r["selector_cost"]) for r in selected)
    paid_gain = sum(float(r["selector_paid_gain"]) for r in selected)
    checks["gain_arithmetic"] = (
        abs(raw_gain - result["summary"]["raw_held_gain_bits"]) < 1e-6
        and abs(partition_cost - result["summary"]["partition_cost_bits"]) < 1e-6
        and abs(selector_cost - result["summary"]["selector_cost_bits"]) < 1e-6
        and abs(paid_gain - result["summary"]["selector_paid_gain_bits"]) < 1e-6
        and abs(paid_gain - (raw_gain - partition_cost - selector_cost)) < 1e-6
    )
    checks["positive_fold_count"] = sum(float(r["raw_gain_vs_exact"]) > 0 for r in selected) == result["summary"]["positive_folds"]
    model_totals = Counter()
    for row in folds:
        if row["model"] in required_models:
            model_totals[row["model"]] += float(row["bits_total"])
    checks["model_total_arithmetic"] = all(abs(model_totals[k] - v) < 1e-6 for k, v in result["model_total_bits"].items())

    mappings = [{r["joint_tuple_id"]: r["latent_form_id"] for r in by_fold_clusters[fold]} for fold in range(11)]
    ari = [adjusted_rand(a, b) for a, b in itertools.combinations(mappings, 2)]
    checks["stability_recomputed"] = len(ari) == 55 and max(abs(a - b) for a, b in zip(ari, result["stability"]["pairwise_ari_values"])) < 1e-12
    null_values = result["null"]["selector_paid_gain_values"]
    expected_null_p = (1 + sum(value >= result["summary"]["selector_paid_gain_bits"] for value in null_values)) / (1 + len(null_values))
    checks["null_exact_64"] = len(null_values) == 64 and abs(expected_null_p - result["null"]["inclusive_p"]) < 1e-15
    checks["merge_bounds"] = len(merges) <= 100 and len(counters) <= 100 and all(
        re.fullmatch(r"T\d{4}", row["tuple_a"]) and re.fullmatch(r"T\d{4}", row["tuple_b"])
        and 0 <= float(row["coassignment_stability"]) <= 1 and row["page_host_same"] in {"0", "1"}
        and row["string_group_same"] in {"0", "1"}
        for row in merges + counters
    )

    source = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: ast.get_source_segment(source, node) or "" for node in tree.body if isinstance(node, ast.FunctionDef)}
    candidate_source = "\n".join(functions[name] for name in ("signature_counts", "signature_matrix", "dendrogram", "cut_partition"))
    forbidden = ("page_host", "host_id", "coordinate_id", "raw_surface", "observed_wrapper", "dy_closure", "b3", "known_label_renderer")
    checks["candidate_feature_exclusion_static"] = not any(term in candidate_source for term in forbidden)
    checks["one_algorithm_six_settings"] = "FRACTIONS = (1.00, 0.90, 0.75, 0.60, 0.45, 0.30)" in source and source.count("def dendrogram") == 1
    tabular = (ART / "fold_scores.tsv", ART / "cluster_summary.tsv", ART / "stable_merges.tsv", ART / "counterexamples.tsv")
    checks["sealed_outputs_no_payload"] = not any("f84r." in path.read_text(encoding="utf-8", errors="ignore").lower() for path in tabular)
    checks["no_semantic_assignments"] = result.get("voynich_semantics_scored") is False and all(value is False for seal in (result["f84"], result["f84r"]) for value in seal.values())
    expected_outputs = {
        "REPORT.md": result["documents"]["REPORT.md"],
        "artifacts/fold_scores.tsv": result["outputs"]["fold_scores.tsv"],
        "artifacts/cluster_summary.tsv": result["outputs"]["cluster_summary.tsv"],
        "artifacts/stable_merges.tsv": result["outputs"]["stable_merges.tsv"],
        "artifacts/counterexamples.tsv": result["outputs"]["counterexamples.tsv"],
    }
    checks["output_hashes"] = all((EXP / name).is_file() and sha256(EXP / name) == digest for name, digest in expected_outputs.items())
    checks["implementation_and_documents"] = (
        result["implementation"]["run.py"] == sha256(RUNNER)
        and result["documents"]["METHOD.md"] == sha256(EXP / "METHOD.md")
        and result["documents"]["README.md"] == sha256(EXP / "README.md")
    )

    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT398_VALIDATION_V1", "status": status, "checks": checks,
        "passed": sum(checks.values()), "total": len(checks), "result_sha256": sha256(RESULT),
        "result_content_sha256": result["content_sha256"], "runner_sha256": sha256(RUNNER),
        "validator_sha256": sha256(Path(__file__)), "method_sha256": sha256(EXP / "METHOD.md"),
        "f84": {"allowed": False, "accessed": False}, "f84r": {"allowed": False, "accessed": False},
        "semantic_scoring": False,
    }
    validation["content_sha256"] = canonical_hash(validation)
    OUTPUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, status, f"{validation['passed']}/{validation['total']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
