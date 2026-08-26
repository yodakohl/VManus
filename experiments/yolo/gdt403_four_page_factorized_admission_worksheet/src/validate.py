#!/usr/bin/env python3
"""Validate the blank GDT403 four-page intake sheet."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = json.loads((OUT / "gdt403_result.json").read_text(encoding="utf-8"))
    axis_fields, axes = read_tsv(OUT / "gdt403_parser_axis_catalog.tsv")
    slot_fields, slots = read_tsv(OUT / "gdt403_four_page_slots.tsv")
    event_fields, events = read_tsv(OUT / "gdt403_event_admission_template.tsv")
    decision_fields, decisions = read_tsv(OUT / "gdt403_decision_catalog.tsv")
    checklist_fields, checklist = read_tsv(OUT / "gdt403_operator_checklist.tsv")

    expected_event_fields = [
        "page_slot", "page_id", "locus_id", "statement_id", "event_id", "card_ordinal",
        "surface", "surface_status", "visible_recipe", "recipe_support_id", "owner_id",
        "owner_evidence", "focus_atom_ordinal", "focus_core", "focus_family",
        "scope_selector", "attachment_geometry", "target_card_offset", "target_event_id",
        "target_atom_ordinal", "target_head", "r_topology", "duplicate_mode",
        "duplicate_role", "boundary_crossing", "lookahead_cards", "core_contract_status",
        "working_core_value", "local_expansion", "admission_color", "stop_reason_code",
        "repair_or_next_action", "review_note",
    ]
    checks = {
        "status_ready": result["status"] == "FOUR_PAGE_WORKSHEET_READY__WAITING_FOR_USER_RELEASE",
        "upstream_4374": result["upstream_attachment_count"] == 4374,
        "four_slots": len(slots) == 4,
        "slot_ids_exact": [row["page_slot"] for row in slots] == [f"PAGE_SLOT_{i}" for i in range(1, 5)],
        "all_slots_unreleased": all(row["release_status"] == "UNRELEASED" for row in slots),
        "no_page_ids_loaded": all(row["page_id"] == "PENDING_USER_RELEASE" for row in slots),
        "zero_events_loaded": len(events) == 0 and result["loaded_event_count"] == 0,
        "event_schema_exact": event_fields == expected_event_fields and len(event_fields) == 33,
        "axis_schema_exact": axis_fields == ["axis", "value", "current_occurrences", "current_page_count", "current_register_count", "operator_rule", "future_policy"],
        "selector_count": sum(row["axis"] == "SCOPE_SELECTOR" for row in axes) == 8,
        "geometry_count": sum(row["axis"] == "ATTACHMENT_GEOMETRY" for row in axes) == 6,
        "head_count": sum(row["axis"] == "ACTION_HEAD" for row in axes) == 10,
        "r_topology_count": sum(row["axis"] == "R_TOPOLOGY" for row in axes) == 4,
        "duplicate_count": sum(row["axis"] == "DUPLICATE_MODE" for row in axes) == 3,
        "axis_total_31": len(axes) == 31,
        "decision_schema_exact": decision_fields == ["priority", "color", "code", "trigger", "decision", "allowed_repair"],
        "decision_count_19": len(decisions) == 19,
        "colors_exact": {row["color"] for row in decisions} == {"GREEN", "AMBER", "RED"},
        "green_count": sum(row["color"] == "GREEN" for row in decisions) == 6,
        "amber_count": sum(row["color"] == "AMBER" for row in decisions) == 3,
        "red_count": sum(row["color"] == "RED" for row in decisions) == 10,
        "red_unknown_selector": any(row["code"] == "UNKNOWN_SELECTOR" and row["color"] == "RED" for row in decisions),
        "red_unknown_head": any(row["code"] == "UNKNOWN_HEAD" and row["color"] == "RED" for row in decisions),
        "red_core_retune": any(row["code"] == "KNOWN_CORE_RETUNED" and row["color"] == "RED" for row in decisions),
        "checklist_schema_exact": checklist_fields == ["step", "operation", "required_output", "stop_if"],
        "checklist_14_steps": [int(row["step"]) for row in checklist] == list(range(1, 15)),
        "max_forward_one": result["hard_contract"]["max_forward_cards"] == 1,
        "no_boundaries": result["hard_contract"]["owner_boundary_crossing"] == "FORBIDDEN" and result["hard_contract"]["statement_boundary_crossing"] == "FORBIDDEN",
        "no_invisible_atoms": result["hard_contract"]["invisible_atom_import"] == "FORBIDDEN",
        "no_core_retuning": result["hard_contract"]["known_core_retuning"] == "FORBIDDEN",
        "input_hashes_current": all((ROOT / path).is_file() and sha256(ROOT / path) == digest for path, digest in result["input_hashes"].items()),
        "output_hashes_current": all((OUT / name).is_file() and sha256(OUT / name) == digest for name, digest in result["output_hashes"].items()),
        "page_slot_schema_present": set(slot_fields) == {"page_slot", "release_status", "page_id", "register_or_section", "source_reference", "source_sha256", "locus_count", "event_count", "statement_count", "owner_block_count", "page_decision", "notes"},
    }

    scan_paths = [
        HERE / "README.md", HERE / "METHOD.md", HERE / "REPORT.md",
        HERE / "FOUR_PAGE_ADMISSION_WORKSHEET.md",
        *[OUT / name for name in result["output_hashes"]],
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in scan_paths)
    checks["no_actual_folio_identifier"] = re.search(r"\bf\d+[rv](?:\d)?\b", joined, flags=re.IGNORECASE) is None
    private_home_prefix = chr(47) + "home" + chr(47)
    checks["no_absolute_private_path"] = private_home_prefix not in joined
    checks["all_documentation_present"] = all(path.is_file() for path in scan_paths)

    failures = sorted(name for name, passed in checks.items() if not passed)
    validation = {
        "experiment_id": "GDT403",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "checks": checks,
        "validated_counts": {
            "page_slots": len(slots),
            "loaded_events": len(events),
            "axis_rows": len(axes),
            "decision_codes": len(decisions),
            "checklist_steps": len(checklist),
        },
    }
    (OUT / "gdt403_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
