#!/usr/bin/env python3
"""Independent integrity/accounting validation for GDT393."""

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
EXP = ROOT / "experiments/yolo/gdt393_remaining_page_connector_census"
ART = EXP / "artifacts"
OUT = ART / "gdt393_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = json.loads((ART / "gdt393_result.json").read_text(encoding="utf-8"))
    frame = read_tsv("gdt393_residual_page_frame.tsv")
    images = read_tsv("gdt393_image_manifest.tsv")
    obs = read_tsv("gdt393_page_observations.tsv")
    candidates = read_tsv("gdt393_ambiguous_candidates.tsv")
    edges = read_tsv("gdt393_eligible_edge_packet.tsv")
    gates = read_tsv("gdt393_capacity_gates.tsv")
    access = json.loads((ART / "gdt393_access_log.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    pages = {row["page"] for row in frame}
    check("frame_size", len(frame) == len(pages) == 12, len(frame))
    check("page_join", pages == {row["page"] for row in images} == {row["page"] for row in obs}, sorted(pages))
    check("folio_count", len({row["physical_folio"] for row in images}) == 11, sorted({row["physical_folio"] for row in images}))
    check("canvas_count", len({row["canvas_id"] for row in images}) == 11, sorted({row["canvas_id"] for row in images}))
    check("no_f84_rows", all(not row["page"].lower().startswith("f84") for row in frame + images + obs), len(pages))
    check("role_counts", [sum(int(row[k] or 0) for row in frame) for k in ("L_count", "C_count", "R_count")] == [102, 13, 16], result["role_counts"])
    outcomes = Counter(row["page_outcome"] for row in obs)
    check("outcome_counts", outcomes == {"NO_CONNECTOR_CANDIDATE": 8, "AMBIGUOUS_CONNECTOR": 4}, dict(outcomes))
    check("candidate_count", len(candidates) == 4 and all(row["eligibility_status"] == "INELIGIBLE" for row in candidates), len(candidates))
    check("zero_edges", len(edges) == 0, len(edges))
    check("capacity_gates", len(gates) == 3 and all(row["pass"] == "0" for row in gates), gates)
    check("direction_zero", all(int(row["directed_pair_count"]) == 0 for row in obs), sum(int(row["directed_pair_count"]) for row in obs))
    check("exact_endpoint_pairs_zero", all(int(row["exact_endpoint_pair_count"]) == 0 for row in obs), 0)
    check("single_ai_provenance", all(row["reviewer"] == "PRIMARY_AI_DIRECT_VISUAL" for row in obs), len(obs))
    check("safe_page_exposure_disclosed", "provenance-qualified" in access["safe_page_formal_exposure_after_freeze_before_image_review"], access["safe_page_formal_exposure_after_freeze_before_image_review"])
    check("metadata_parse_disclosed", "split two forbidden page-description metadata rows" in access["f84_metadata_parse_disclosure"], access["f84_metadata_parse_disclosure"])
    check("no_f84_image_or_formal", access["f84_image_opened"] is False and access["f84_formal_payload_opened"] is False, False)
    check("no_formal_score", result["formal_grounding_score_run"] is False and result["formal_identity_rows_joined"] == 0, 0)
    check("decision", result["status"] == "COMPLETE_RESIDUAL_CENSUS_ZERO_ELIGIBLE_DIRECTED_EDGES", result["status"])

    bare = dict(result)
    expected_content = bare.pop("content_sha256")
    encoded = json.dumps(bare, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    check("content_hash", hashlib.sha256(encoded).hexdigest() == expected_content, expected_content)
    for family in ("input_hashes", "document_hashes", "implementation_hashes"):
        for rel, expected in result[family].items():
            path = ROOT / rel
            check(f"{family}:{rel}", path.is_file() and sha(path) == expected, expected)

    passed = sum(int(item["pass"]) for item in checks)
    payload = {
        "experiment_id": "GDT393",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "result_sha256": sha(ART / "gdt393_result.json"),
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{payload['status']} {passed}/{len(checks)}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
