#!/usr/bin/env python3
"""Nonimporting integrity and source-row validator for GDT354."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt354_ljs443_f68v3_source_audit"
ART = EXP / "artifacts"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> None:
    sources = read(ART / "gdt354_external_sources.tsv")
    observations = read(ART / "gdt354_external_visual_observations.tsv")
    target = read(ART / "gdt354_target_topology.tsv")
    gates = read(ART / "gdt354_endpoint_capacity.tsv")
    result = json.loads((ART / "gdt354_result.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def ck(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    ck("source_count", len(sources) == 7)
    official = [row for row in sources if row["source_class"] == "OFFICIAL_PRIMARY_FACSIMILE"]
    ck("official_facsimile_count", len(official) == 3)
    ck("official_ids", [row["source_id"] for row in official] == ["LJS443_0422", "LJS443_0423", "LJS443_0424"])
    ck("official_hashes", [row["remote_sha256"] for row in official] == [
        "a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530",
        "8254c56b22c5990cd560f7cfcc2efa6105803ee87954b2ea11a191b5bad768bf",
        "6c5227d8f040c16c9d9eed8d2d5563c3c0d5a711f32038af35e47d5a9d28f875",
    ])
    ck("tei_hash", sources[0]["remote_sha256"] == "becfa33a8ca1952a7c914e09d070e4d7cdd4f3509291998916a956397b8391b4")
    ck("observation_count", len(observations) == 3)
    ck("observation_provenance", all(row["provenance"] == "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION" for row in observations))
    ck("same_manuscript_not_replications", all(row["independent_witness"] == "NO_SAME_MANUSCRIPT_SERIES" for row in observations))
    ck("neutral_observations", all(row["interpretation"] == "NONE_GEOMETRY_ONLY" for row in observations))
    ck("eight_compartments", all("eight curved radial compartments" in row["visible_geometry"].lower() for row in observations))

    guard = GuardedTSV(ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv", selector_column="page", allowed_values={"f68v3"})
    selected = list(guard)
    ck("one_guarded_target", len(selected) == 1 and selected[0]["page"] == "f68v3")
    ck("target_row", len(target) == 1 and target[0]["page"] == "f68v3")
    ck("target_human_provenance", target[0]["provenance"] == "EXISTING_HUMAN_ANNOTATION")
    ck("target_exact_description", target[0]["visible_geometry"] == selected[0]["illustrations"])
    ck("target_eight_bands", "eight bands" in target[0]["visible_geometry"].lower())
    ck("target_no_phase", target[0]["fixed_start"] == "NO" and target[0]["fixed_direction"] == "NO" and target[0]["slot_values"] == "UNKNOWN")
    ck("tentative_not_role_evidence", target[0]["tentative_identifications_are_role_evidence"] == "0")
    ck("guard_skips_forbidden_rows", guard.stats.skipped_forbidden > 0)

    by_gate = {row["gate"]: row["status"] for row in gates}
    ck("gate_count", len(gates) == 9)
    ck("external_family_pass", by_gate.get("EXTERNAL_EIGHT_CURVED_COMPARTMENT_FAMILY") == "PASS")
    ck("slot_values_fail", by_gate.get("EXTERNAL_READABLE_SLOT_VALUES") == "FAIL")
    ck("start_order_fail", by_gate.get("EXTERNAL_FIXED_START_AND_ORDER") == "FAIL")
    ck("target_phase_fail", by_gate.get("TARGET_FIXED_PHASE") == "FAIL")
    ck("target_transfer_fail", by_gate.get("TARGET_INDEPENDENT_FOLIO_TRANSFER") == "FAIL")
    ck("scoring_not_authorized", by_gate.get("VOYNICH_FORMAL_SCORING_AUTHORIZED") == "NO")
    ck("status", result["status"] == "PROVISIONAL_EIGHT_BAND_SYSTEM_HOMOLOGUE_NO_SLOT_TRANSFER")
    ck("no_voynich_formal_access", result["source_access"]["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_target_image", result["source_access"]["voynich_images_opened"] is False)
    ck("no_f84_access", result["source_access"]["f84_rows_or_images_accessed"] is False)
    all_rows = sources + observations + target + gates
    ck("no_f84_output", all("f84" not in "\t".join(row.values()).lower() for row in all_rows))
    ck("selected_digest", hashlib.sha256(stable(selected)).hexdigest() == result["selected_human_source_content_sha256"])

    for rel, digest in result["outputs"].items():
        ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    output = {
        "experiment": "GDT354",
        "schema": "GDT354_VALIDATION_V1",
        "status": "PASS" if all(row["pass"] for row in checks) else "FAIL",
        "scope": "Independent guarded reconstruction of the selected human target row, fixed source inventory, gate logic, accounting and hashes. The validator does not independently re-review the external images or fetch remote bytes.",
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_failed": sum(not row["pass"] for row in checks),
        "checks": checks,
        "result_sha256": sha(ART / "gdt354_result.json"),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt354_validation.json").write_bytes(stable(output))
    print(output["status"], output["checks_passed"], output["checks_failed"])
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

