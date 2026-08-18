#!/usr/bin/env python3
"""Independent mechanical validation for GDT337.

The validator does not import the producer.  It reconstructs the local
text-blind capacities and checks the frozen gate logic.  Bibliographic claims
remain a human source-audit layer and are not represented as independently
web-retrieved validation.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt337_external_homologue_census"
ART = EXP / "artifacts"
SC = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
ZODIAC = ROOT / "experiments/semantic_assumptions/results/zodiac_crosssign_phase_capacity.json"
F69 = ROOT / "experiments/semantic_assumptions/results/f69vsd001_start_direction_result.json"
PAIR105 = ROOT / "experiments/semantic_assumptions/results/special_circle_10_to_5_pairing_worth.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    result_path = ART / "gdt337_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    source_rows = read_tsv(ART / "gdt337_external_source_manifest.tsv")
    target_rows = read_tsv(ART / "gdt337_voynich_topology_capacity.tsv")
    candidates = read_tsv(ART / "gdt337_candidate_correspondences.tsv")
    viable = read_tsv(ART / "gdt337_viable_endpoint_freeze.tsv")

    check("schema", result["schema"] == "GDT337_EXTERNAL_HOMOLOGUE_CENSUS_V1")
    check("status", result["status"] == "NO_VIABLE_FROZEN_ENDPOINT")
    check("external_source_count", len(source_rows) == 14, len(source_rows))
    check("external_source_ids_unique", len({r["source_id"] for r in source_rows}) == 14)
    check("candidate_count", len(candidates) == 11, len(candidates))
    check("candidate_ids_unique", len({r["candidate_id"] for r in candidates}) == 11)
    check("zero_viable_rows", len(viable) == 0, len(viable))
    check("every_candidate_explicit", all(r["viable"] in {"YES", "NO"} for r in candidates))
    check("every_exclusion_explained", all(r["viable"] == "YES" or r["exclusion_reason"] for r in candidates))
    check("all_current_candidates_fail", all(r["viable"] == "NO" for r in candidates))
    check("source_urls_bound", all(r["source_url"].startswith(("http://", "https://")) for r in source_rows))
    check("bibliography_nonblank", all(r["bibliographic_reference"] and r["supporting_statement"] for r in source_rows))
    check("new_28_donor_present", any(r["source_id"] == "EXT001_BL_ADD_MS_25435" and r["fixed_order"] == "YES_I_TO_XXVIII" for r in source_rows))

    # Independent source-table reconstruction; parse only this f67-f73 inventory.
    sc_rows = read_tsv(SC)
    check("special_circle_no_f84", all(not r["page"].startswith("f84") for r in sc_rows))
    arrays = {r["array_id"]: r for r in sc_rows}
    folios = {r["physical_folio"] for r in sc_rows}
    check("special_circle_slots", len(sc_rows) == 504, len(sc_rows))
    check("special_circle_arrays", len(arrays) == 45, len(arrays))
    check("special_circle_folios", len(folios) == 7, sorted(folios))
    check("special_circle_array_counts", Counter(r["array_id"] for r in sc_rows) == Counter({a: int(r["slot_count"]) for a, r in arrays.items()}))

    zodiac = json.loads(ZODIAC.read_text(encoding="utf-8"))
    zc = zodiac["counts"]
    check("zodiac_counts", (zc["signs"], zc["expected_slots"], zc["present_labels"], zc["physical_folios"]) == (10, 300, 299, 4), zc)
    check("zodiac_topologies", zc["distinct_panel_topologies"] == 7)
    check("zodiac_disjoint_repeat_capacity", zc["disjoint_folio_repeated_topology_pairs"] == 0)
    f69 = json.loads(F69.read_text(encoding="utf-8"))
    check("f69_no_start", f69["counts"]["author_visible_start_devices"] == 0)
    check("f69_no_direction", f69["counts"]["author_visible_direction_devices"] == 0)
    pair105 = json.loads(PAIR105.read_text(encoding="utf-8"))
    check("ten_five_no_pairing", pair105["counts"]["pages_with_pairing_device"] == 0)
    check("ten_five_three_folios", pair105["counts"]["physical_folios"] == 3)

    target_pages = ";".join(r["pages"] for r in target_rows)
    check("target_output_no_f84", "f84" not in target_pages)
    check("target_rows", len(target_rows) == 48, len(target_rows))
    check("candidate_output_no_text_columns", not ({"token", "surface", "page_host", "tuple_id", "family"} & set(candidates[0])))
    check("target_output_no_text_columns", not ({"token", "surface", "page_host", "tuple_id", "family"} & set(target_rows[0])))

    for mapping in (result["inputs"], result["outputs"], result["implementation"]):
        for rel, digest in mapping.items():
            check(f"hash:{rel}", sha256_file(ROOT / rel) == digest)

    content = dict(result)
    expected_content_hash = content.pop("result_content_sha256")
    check("result_content_hash", hashlib.sha256(canonical_json_bytes(content)).hexdigest() == expected_content_hash)
    check("result_counts", result["counts"]["external_sources"] == len(source_rows) and result["counts"]["candidate_correspondences"] == len(candidates) and result["counts"]["viable_endpoints"] == 0)
    check("seal_flag", result["source_access"]["f84_material_opened_retained_joined_or_scored"] is False)
    check("zero_semantic_score", "score" not in result and "predictions" not in result)

    validation = {
        "schema": "GDT337_VALIDATION_V1",
        "experiment": "GDT337",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "checks": checks,
        "scope": "Independent local topology/capacity, gate, hash, and seal validation. External bibliographic statements are audit claims, not independently refetched web validation.",
        "result_sha256": sha256_file(result_path),
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
    }
    (ART / "gdt337_validation.json").write_bytes(canonical_json_bytes(validation))
    print(json.dumps({"status": "PASS", "checks": len(checks)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
