#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE / "artifacts"


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    print(f"PASS\t{label}")


with (ROOT / "candidate_grid.tsv").open(encoding="utf-8", newline="") as handle:
    candidates = list(csv.DictReader(handle, delimiter="\t"))

check(len(candidates) == 8, "eight candidate systems")
check(len({row["candidate_id"] for row in candidates}) == 8, "unique candidate ids")
for row in candidates:
    for key in (
        "composition_0_3",
        "capacity34_0_3",
        "C_d_opener_0_3",
        "y_closer_0_3",
        "o_connector_0_3",
        "ol_boundary_standalone_0_3",
        "qok_singleton_counterclass_0_3",
    ):
        check(0 <= int(row[key]) <= 3, f"{row['candidate_id']} {key} range")
    expected = sum(
        int(row[key])
        for key in (
            "C_d_opener_0_3",
            "y_closer_0_3",
            "o_connector_0_3",
            "ol_boundary_standalone_0_3",
            "qok_singleton_counterclass_0_3",
        )
    )
    check(expected == int(row["observed_fit_0_15"]), f"{row['candidate_id']} observed fit sum")

with (ROOT / "source_evidence.tsv").open(encoding="utf-8", newline="") as handle:
    sources = list(csv.DictReader(handle, delimiter="\t"))

check(len(sources) == 11, "eleven evidence sources")
source_ids = {row["source_id"] for row in sources}
check(len(source_ids) == len(sources), "unique source ids")
check(all(row["url"].startswith("https://") for row in sources), "all sources use https links")
for row in candidates:
    check(set(row["source_ids"].split(";")) <= source_ids, f"{row['candidate_id']} source references resolve")

model = json.loads((ROOT / "model_v1.json").read_text(encoding="utf-8"))
buckets = model["primitive_capacity"]["buckets"]
check(model["primitive_capacity"]["total"] == 34, "declared primitive capacity 34")
check(sum(item["count"] for item in buckets) == 34, "bucket counts sum to 34")
check(len({item["role"] for item in buckets}) == len(buckets), "unique primitive roles")
check(model["frequent_compounds"]["observed_merge_nodes"] == 64, "64 merge nodes modeled")
check(model["frequent_compounds"]["lexicalized_override_max"] <= 8, "macro override cap")
check(model["null_policy"]["primitive_slots_max"] == 1, "primary null cap one")
check(model["null_policy"]["token_mass_max"] <= 0.03, "primary null token-mass cap")
check(model["structural_anchor_priors"]["qok_singleton_family"]["forbidden_inference"] == "standalone_implies_word_or_long_output", "qok standalone guard")

report = (HERE / "REPORT.md").read_text(encoding="utf-8")
check("81" in report and "82" in report, "Tranchedini arithmetic caveat visible")
check("keine historische Identifikation" in report, "non-identification caveat visible")
check("CORE_GRAMMAR" in report and "DOMAIN_OVERLAY" in report, "recommendations visible")
print("VALIDATION_OK")
