#!/usr/bin/env python3
"""Build the central V76 purpose selection and bind all four role audits."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def copy_bytes(source: str, target: str) -> None:
    (ROOT / target).write_bytes((ROOT / source).read_bytes())


def main() -> None:
    copies = {
        "V76_R2_776_GROUP_PURPOSE_BINDING.tsv": "V76_SELECTED_776_GROUP_PURPOSE_BINDING.tsv",
        "V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv": "V76_SELECTED_14_UNIT_PURPOSE_SCORECARD.tsv",
        "V76_R2_BOOK_PURPOSE_COMPETITION.tsv": "V76_SELECTED_BOOK_PURPOSE_COMPETITION.tsv",
        "V76_R2_PRODUCTION_WORKFLOW.tsv": "V76_SELECTED_PRODUCTION_WORKFLOW.tsv",
        "V76_R2_HISTORICAL_SOURCE_AUDIT.tsv": "V76_SELECTED_HISTORICAL_SOURCE_AUDIT.tsv",
        "V76_R2_CONTRADICTIONS.tsv": "V76_SELECTED_CONTRADICTIONS.tsv",
        "V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv": "V76_SELECTED_PROCESS_OWNERSHIP_GRAPH.tsv",
        "V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv": "V76_SELECTED_TECHNICAL_SYMMETRIC_RUBRIC.tsv",
    }
    for source, target in copies.items():
        copy_bytes(source, target)

    bindings = read_tsv(copies["V76_R2_776_GROUP_PURPOSE_BINDING.tsv"])
    units = read_tsv(copies["V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv"])
    purposes = read_tsv(copies["V76_R2_BOOK_PURPOSE_COMPETITION.tsv"])
    sources = read_tsv(copies["V76_R2_HISTORICAL_SOURCE_AUDIT.tsv"])
    graph = read_tsv(copies["V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv"])
    rubric = read_tsv(copies["V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv"])

    role_files = {
        "R1": ["V76_R1_14_UNIT_PURPOSE_MATRIX.tsv", "V76_R1_PRODUCTION_WORKFLOW.tsv", "V76_R1_COMPETITION_SCORECARD.tsv", "V76_R1_CONTRADICTION_LEDGER.tsv", "V76_R1_HISTORICAL_BOOK_PURPOSE_REPORT.md", "V76_R1_VALIDATION.json"],
        "R2": ["V76_R2_776_GROUP_PURPOSE_BINDING.tsv", "V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv", "V76_R2_BOOK_PURPOSE_COMPETITION.tsv", "V76_R2_PRODUCTION_WORKFLOW.tsv", "V76_R2_HISTORICAL_SOURCE_AUDIT.tsv", "V76_R2_CONTRADICTIONS.tsv", "V76_R2_HISTORICAL_BOOK_PURPOSE_REPORT.md", "V76_R2_VALIDATION.json"],
        "R3": ["V76_R3_14_UNIT_DUAL_PURPOSE.tsv", "V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv", "V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv", "V76_R3_CONTRADICTIONS.tsv", "V76_R3_TECHNICAL_BOOK_PURPOSE_REPORT.md", "V76_R3_VALIDATION.json"],
        "R4": ["V76_R4_FOURTEEN_UNIT_PURPOSE_MATRIX.tsv", "V76_R4_PRODUCTION_WORKFLOW.tsv", "V76_R4_PURPOSE_SCORECARD.tsv", "V76_R4_CONTRADICTION_LEDGER.tsv", "V76_R4_CHANCERY_BOOK_PURPOSE_REPORT.md", "V76_R4_VALIDATION.json"],
    }
    role_bindings = {role: {name: sha256(ROOT / name) for name in names} for role, names in role_files.items()}
    validations = {role: json.loads((ROOT / f"V76_{role}_VALIDATION.json").read_text(encoding="utf-8")) for role in ("R1", "R2", "R3", "R4")}
    checks = {
        "bindings_776": len(bindings) == 776,
        "bindings_unique": len({row["binding_id"] for row in bindings}) == 776,
        "units_14": len(units) == 14,
        "unit_groups_776": sum(int(row["group_count"]) for row in units) == 776,
        "purposes_2": len(purposes) == 2,
        "purpose_totals_236_235": sorted(int(row["ordinal_total"]) for row in purposes) == [235, 236],
        "sources_12": len(sources) == 12,
        "all_sources_mechanism_only": all(row["codebook_or_lexical_use"].startswith("NONE") for row in sources),
        "graph_nonempty": bool(graph),
        "technical_rubric_nonempty": bool(rubric),
        "all_bindings_no_gloss_added": all(row["codebook_attestation_status"] == "NO_DICTIONARY_GLOSS_ADDED" for row in bindings),
        "all_role_validations_pass": all(value["status"] == "PASS" for value in validations.values()),
        "f84_not_named_in_bindings": not any("f84" in row["page"].lower() for row in bindings),
    }
    payload = {
        "schema": "V76_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "selection": {
            "working_lead": "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM",
            "strongest_rival": "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK",
            "result": "NEAR_TIE__A_PRACTICAL_COHERENCE__B_VISIBLE_PRODUCTION_ECONOMY",
            "r2_score": "236:235",
            "r3_local_score": "398:404",
            "r3_book_score": "53:49",
            "dictionary_glosses_added": 0,
        },
        "counts": {"bindings": len(bindings), "units": len(units), "purposes": len(purposes), "historical_sources": len(sources)},
        "checks": checks,
        "role_bindings": role_bindings,
        "selected_bindings": {target: sha256(ROOT / target) for target in copies.values()},
        "sealed_pages_opened": [],
    }
    (ROOT / "V76_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps(payload["selection"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
