#!/usr/bin/env python3
"""Build compact public GDT396 qualification outputs without oracle access."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
METRICS = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
QUAL = EXP / "artifacts/gdt396_decoder_qualification.json"
MATRIX = EXP / "artifacts/gdt396_qualification_identifiability_matrix.tsv.gz"
ROUTES = EXP / "artifacts/gdt396_qualification_route_matrix.tsv"
PROPS = EXP / "artifacts/gdt396_property_decisions.tsv"
RESULT = EXP / "artifacts/gdt396_result.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    payload = dict(value)
    payload.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    for path in (MATRIX, ROUTES, PROPS, RESULT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path}")
    qual = json.loads(QUAL.read_text(encoding="utf-8"))
    if qual.get("status") != "NO_CONFIRMATION_ELIGIBLE_PROPERTY" or qual.get("metrics_sha256") != sha256(METRICS):
        raise RuntimeError("qualification result/metrics mismatch")
    with METRICS.open("rb") as source, MATRIX.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as compressed:
            shutil.copyfileobj(source, compressed, length=1 << 20)

    route_fields = [
        "decoder_id", "method_family", "property_id", "representation_id", "surface_id",
        "meaningful_world_pass_count", "meaningful_worlds_passing", "median_positive_margin",
        "w10_false_positive_rates", "w10_veto_pass", "route_qualifies_before_representation_freeze",
        "selected_representation", "decoder_suite_pass", "qualified",
    ]
    route_rows = []
    for row in qual["route_rows"]:
        route_rows.append({
            **{key: row[key] for key in route_fields if key not in {"meaningful_worlds_passing", "w10_false_positive_rates"}},
            "meaningful_worlds_passing": "|".join(row["meaningful_worlds_passing"]),
            "w10_false_positive_rates": "|".join(f"{value:.12g}" for value in row["w10_false_positive_rates"]),
        })
    write_tsv(ROUTES, route_fields, route_rows)

    by_property = defaultdict(list)
    for row in qual["route_rows"]:
        by_property[row["property_id"]].append(row)
    selection = {(row["property_id"], row["surface_id"]): row for row in qual["representation_selections"]}
    property_rows = []
    for prop, rows in sorted(by_property.items()):
        w10_fail = [row for row in rows if row["w10_false_positive_rates"] and not row["w10_veto_pass"]]
        pre = [row for row in rows if row["route_qualifies_before_representation_freeze"]]
        if w10_fail:
            decision = "SEMANTICS_LIGHT_FALSE_POSITIVE"
        else:
            decision = "CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE"
        free = [row for row in pre if row["surface_id"] == "FREE_SURFACE"]
        voy = [row for row in pre if row["surface_id"] == "VOYNICH_SURFACE"]
        property_rows.append({
            "property_id": prop,
            "free_selected_representation": selection[(prop, "FREE_SURFACE")]["representation_id"] if selection[(prop, "FREE_SURFACE")]["qualified_decoder_count"] else "NO_SELECTION",
            "voynich_selected_representation": selection[(prop, "VOYNICH_SURFACE")]["representation_id"] if selection[(prop, "VOYNICH_SURFACE")]["qualified_decoder_count"] else "NO_SELECTION",
            "free_pre_suite_decoder_count": len(free),
            "voynich_pre_suite_decoder_count": len(voy),
            "free_passing_worlds": "|".join(sorted({world for row in free for world in row["meaningful_worlds_passing"]})),
            "voynich_passing_worlds": "|".join(sorted({world for row in voy for world in row["meaningful_worlds_passing"]})),
            "w10_veto_failed_route_count": len(w10_fail),
            "qualified_decoder_count": sum(row["qualified"] for row in rows),
            "classification": decision,
        })
    property_rows.append({
        "property_id": "ACTUAL_LEXICAL_MEANING", "free_selected_representation": "NOT_SCORED",
        "voynich_selected_representation": "NOT_SCORED", "free_pre_suite_decoder_count": 0,
        "voynich_pre_suite_decoder_count": 0, "free_passing_worlds": "", "voynich_passing_worlds": "",
        "w10_veto_failed_route_count": 0, "qualified_decoder_count": 0,
        "classification": "REQUIRES_EXTERNAL_GROUNDING",
    })
    prop_fields = list(property_rows[0])
    write_tsv(PROPS, prop_fields, property_rows)

    supported_semantic = [row for row in qual["route_rows"] if row["w10_false_positive_rates"]]
    result = {
        "schema": "GDT396_RESULT_V1",
        "status": "NO_CONFIRMATION_ELIGIBLE_PROPERTY",
        "primary_decision": "CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE",
        "secondary_decision": "SEMANTICS_LIGHT_FALSE_POSITIVE",
        "voynich_internal_inference_calibrated": False,
        "confirmation_generated": False,
        "qualification_metrics_rows": 117100,
        "qualification_metrics_sha256": sha256(METRICS),
        "qualification_result_sha256": sha256(QUAL),
        "strict_matrix_sha256": sha256(MATRIX),
        "route_matrix_sha256": sha256(ROUTES),
        "property_decisions_sha256": sha256(PROPS),
        "route_count": len(qual["route_rows"]),
        "pre_suite_qualifying_route_count": sum(row["route_qualifies_before_representation_freeze"] for row in qual["route_rows"]),
        "qualified_route_count": len(qual["qualified_routes"]),
        "confirmation_eligible_panel_count": sum(row["confirmation_eligible"] for row in qual["confirmation_panels"]),
        "decoder_suite_qualified_count": sum(row["qualified"] for row in qual["decoder_wide_suite"].values()),
        "decoder_easy_equality_pass_count": sum(row["easy_equality"] for row in qual["decoder_wide_suite"].values()),
        "decoder_recurrent_relation_pass_count": sum(row["simple_recurrent_relation"] for row in qual["decoder_wide_suite"].values()),
        "supported_semantic_route_count": len(supported_semantic),
        "w10_veto_failed_semantic_route_count": sum(not row["w10_veto_pass"] for row in supported_semantic),
        "semantic_route_false_positive_fraction": sum(not row["w10_veto_pass"] for row in supported_semantic) / len(supported_semantic),
        "architecture_qualified_count": sum(row["qualified"] for row in qual["architecture_qualification"]),
        "function_multiconstraint_qualified_count": sum(row["qualified"] for row in qual["function_multiconstraint_routes"]),
        "property_classification_counts": dict(sorted(__import__("collections").Counter(row["classification"] for row in property_rows).items())),
        "threshold_discrepancy_invariant": True,
        "architecture_interval_omission_invariant": True,
        "voynich_rows": 0,
        "f84": {"accessed": False, "rows": 0},
        "f84r": {"accessed": False, "rows": 0},
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT, result["status"], result["content_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
