#!/usr/bin/env python3
"""Independent integrity validation for the frozen GDT159 source panel."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
PROVENANCE = ROOT / "gdt159_diplomatic_source_provenance.json"
OUT = ROOT / "gdt159_diplomatic_source_validation.json"

EXPECTED = {
    "LATIN_MEDICAL_GRAPHEMATIC": (12000, 21, 14457, 12, "MATCHED_12000"),
    "LATIN_15C_GRAPHEMATIC": (12000, 76, 16376, 12, "MATCHED_12000"),
    "LATIN_SCHOLASTIC_GRAPHEMATIC": (11317, 15, 11317, 6, "LOW_CAPACITY_UNMATCHED_ALL"),
    "IFORAL_1395_1411_GRAPHEMATIC": (6104, 29, 6104, 6, "LOW_CAPACITY_UNMATCHED_ALL"),
    "LATIN_GERMAN_APOTHECARY_LATE15": (1554, 7, 1554, 6, "LOW_CAPACITY_UNMATCHED_ALL"),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    check("schema", payload["schema"] == "GDT159_DIPLOMATIC_CORPORA_V1")
    check("five_corpora", len(manifest) == len(EXPECTED) == 5)
    check("manifest_ids", {row["corpus_id"] for row in manifest} == set(EXPECTED))
    check("record_total", len(payload["records"]) == 42975, len(payload["records"]))

    rows_by: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in payload["records"]:
        rows_by[str(row["corpus_id"])].append(row)
    meta = {row["corpus_id"]: row for row in manifest}
    for corpus_id, expected in EXPECTED.items():
        sampled, units, eligible, folds, state = expected
        rows = rows_by[corpus_id]
        item = meta[corpus_id]
        check(f"{corpus_id}:sampled", len(rows) == sampled, len(rows))
        check(f"{corpus_id}:manifest_counts", (int(item["sampled_tokens"]), int(item["source_units"]), int(item["eligible_source_tokens"]), int(item["folds"]), item["capacity_state"]) == expected)
        check(f"{corpus_id}:fold_count", len({str(row["fold_id"]) for row in rows}) == folds)
        check(f"{corpus_id}:unit_subset", len({str(row["unit_id"]) for row in rows}) <= units)
        check(f"{corpus_id}:surface_only", item["surface_only"] == "1" and item["phoneme_mapping"] == "0" and item["translation_or_lemma_used"] == "0")
        per_fold = Counter(str(row["fold_id"]) for row in rows)
        if state == "MATCHED_12000":
            check(f"{corpus_id}:matched_fold_sizes", set(per_fold.values()) == {1000}, dict(per_fold))
        check(f"{corpus_id}:forms", all(2 <= len(str(row["form"])) <= 30 for row in rows))
        check(f"{corpus_id}:ranks_unique", len({(row["fold_id"], row["sample_rank"]) for row in rows}) == len(rows))

    serialized = json.dumps(payload["records"], ensure_ascii=False)
    check("no_voynich_locus_or_f84r", "f84r" not in serialized and "VOYNICH" not in serialized.upper())
    check("provenance_schema", provenance["schema"] == "GDT159_DIPLOMATIC_SOURCE_PROVENANCE_V1")
    check("provenance_corpora", set(provenance["corpora"]) == set(EXPECTED))
    check("normalized_hash", provenance["normalized_corpora_sha256"] == sha(CORPORA))
    check("source_freeze_flags", provenance["voynich_target_opened"] is False and provenance["f84r_opened"] is False)
    check("repositories_frozen", provenance["repositories"]["CREMMA_MEDII_AEVI"]["commit"] == "292525969ad98380b398e6606a9c2a36d51913ae" and provenance["repositories"]["HTROMANCE_LATIN"]["commit"] == "fe25eb9ffaa37a32333fe0e3f4093ff4dd8186db" and provenance["repositories"]["IFORAL"]["commit"] == "9bdc5b006f634bc2e12abe043ca6e5578dfcdd83")
    check("no_absolute_paths", "/tmp/" not in PROVENANCE.read_text(encoding="utf-8") and "/home/" not in PROVENANCE.read_text(encoding="utf-8"))

    result = {
        "schema": "GDT159_DIPLOMATIC_SOURCE_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_FROZEN_PANEL_INTEGRITY",
        "checks_passed": sum(int(row["passed"]) for row in checks),
        "checks_total": len(checks), "checks": checks,
        "inputs": {path.name: sha(path) for path in (CORPORA, MANIFEST, PROVENANCE)},
    }
    result["validation_content_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
