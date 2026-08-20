#!/usr/bin/env python3
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
BASE = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol"
ART = BASE / "artifacts"
P360 = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads((ART / "gdt388_result.json").read_text())
    clone = dict(result)
    reported_content_hash = clone.pop("content_hash")
    check("result_content_hash", reported_content_hash == hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for path, digest in result["inputs"].items():
        check("input_hash:" + path, sha(ROOT / path) == digest)
    for path, digest in result["outputs"].items():
        check("output_hash:" + path, sha(ROOT / path) == digest)
    for path, digest in result["implementation"].items():
        check("implementation_hash:" + path, sha(ROOT / path) == digest)

    annotations = read_tsv(P360)
    relation_channels = {"HUMAN_REL_ATTACHMENT", "HUMAN_REL_CONTACT", "HUMAN_REL_ENCLOSURE", "HUMAN_REL_ARRAY_GROUP"}
    relation = [row for row in annotations if row["channel"] in relation_channels]
    positive = [row for row in relation if row["visual_state"] != "PROXIMITY_ONLY"]
    check("source_f84_free", all(not row["page"].startswith("f84") for row in annotations))
    expected_capacity = {
        "local_relation_catalogue_rows": len(relation),
        "local_relation_unique_loci": len({row["locus"] for row in relation}),
        "local_relation_folios": len({row["physical_folio"] for row in relation}),
        "positive_local_relation_rows": len(positive),
        "positive_local_relation_unique_loci": len({row["locus"] for row in positive}),
        "positive_local_relation_folios": len({row["physical_folio"] for row in positive}),
        "unhedged_positive_rows": sum(row["confidence"] == "UNHEDGED" for row in positive),
        "independent_ordered_target_edges": 0,
        "independent_ordered_target_folios": 0,
    }
    check("capacity_rebuilt", result["current_capacity"] == expected_capacity)
    check("positive_states_rebuilt", result["positive_state_counts"] == dict(sorted(Counter(row["visual_state"] for row in positive).items())))

    capacity = read_tsv(ART / "gdt388_relation_type_capacity.tsv")
    page_frame = read_tsv(ART / "gdt388_page_frame.tsv")
    by_channel = {row["source_channel"]: row for row in capacity}
    check("four_local_relation_families", set(by_channel) == relation_channels)
    for channel in sorted(relation_channels):
        local = [row for row in relation if row["channel"] == channel]
        local_positive = [row for row in local if row["visual_state"] != "PROXIMITY_ONLY"]
        local_unhedged = [row for row in local_positive if row["confidence"] == "UNHEDGED"]
        row = by_channel[channel]
        check(
            "relation_capacity:" + channel,
            int(row["catalogue_rows"]) == len(local)
            and int(row["positive_relation_rows"]) == len(local_positive)
            and int(row["positive_unique_loci"]) == len({item["locus"] for item in local_positive})
            and int(row["positive_folios"]) == len({item["physical_folio"] for item in local_positive})
            and int(row["unhedged_positive_rows"]) == len(local_unhedged)
            and int(row["unhedged_positive_folios"]) == len({item["physical_folio"] for item in local_unhedged})
            and row["ordered_inscription_edges"] == "0"
            and row["relation_instrument_eligible"] == "0",
        )

    batches = read_tsv(ART / "gdt388_acquisition_batches.tsv")
    gates = read_tsv(ART / "gdt388_acquisition_gates.tsv")
    template = read_tsv(ART / "gdt388_edge_packet_template.tsv")
    check("five_acquisition_batches", len(batches) == 5 and len({row["batch_id"] for row in batches}) == 5)
    check("page_frame_exact", len(page_frame) == 61 and len({row["physical_folio"] for row in page_frame}) == 30 and {row["page"] for row in page_frame} == {row["page"] for row in annotations})
    check("page_frame_counts", sum(int(row["annotation_rows"]) for row in page_frame) == len(annotations) and sum(int(row["relation_rows"]) for row in page_frame) == len(relation) and sum(int(row["positive_relation_rows"]) for row in page_frame) == len(positive))
    check("page_frame_sealed", all(row["formal_access_state"] == "SEALED" and row["review_scope"] == "COMPLETE_PAGE_CONNECTOR_CENSUS" for row in page_frame))
    check("primary_authorial_connector_batch", batches[0]["batch_id"] == "B01_AUTHORIAL_CONNECTOR_BETWEEN_LABELED_ENDPOINTS")
    check("primary_uses_complete_page_frame", "All 61 f84-free pages on 30 folios" in batches[0]["selection_frame"])
    check("capacity_thresholds", all(row["required_observations"] == "50" and row["required_folios"] == "5" for row in batches))
    check("nine_gates", len(gates) == 9 and len({row["gate_id"] for row in gates}) == 9)
    check("only_formal_seal_passes", [row["gate_id"] for row in gates if row["current_pass"] == "1"] == ["G01_FORMAL_SEAL"])
    check("empty_edge_packet", template == [])
    with (ART / "gdt388_edge_packet_template.tsv").open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle, delimiter="\t"))
    required = {"edge_id", "pivot_locus", "target_locus", "direction_basis", "ownership_basis", "formal_access_state", "fold_assignment"}
    check("edge_packet_schema", required <= set(header))
    check("decision", result["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES")
    check("scoring_not_authorized", result["acquisition"]["scoring_authorized"] is False)
    check("no_formal_or_visual_access", result["source_access"] == {"voynich_images_opened": False, "voynich_formal_rows_read": 0, "voynich_text_identities_read": 0, "new_visual_observations": 0, "f84_opened_parsed_retained_or_scored": False})
    check("claim_ceiling", result["claim_ceiling"] == "TEXT_BLIND_ACQUISITION_PROTOCOL_AND_CAPACITY_ONLY")

    validation = {
        "schema": "GDT388_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_hash": sha(ART / "gdt388_result.json"),
    }
    (ART / "gdt388_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
