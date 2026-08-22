#!/usr/bin/env python3
"""Build central V75: historical local content under technical namespaces."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
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
        "V75_R2_395_ASTRO_GROUPS.tsv": "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv",
        "V75_R2_142_ASTRO_LOCI.tsv": "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv",
        "V75_R2_THREE_CELESTIAL_INSTRUMENTS.tsv": "V75_SELECTED_THREE_INSTRUMENTS.tsv",
        "V75_R2_HISTORICAL_SOURCE_AUDIT.tsv": "V75_SELECTED_HISTORICAL_SOURCE_AUDIT.tsv",
        "V75_R2_UNSUPPORTED_LABELS.tsv": "V75_SELECTED_UNSUPPORTED_LABELS.tsv",
        "V75_R3_NAMESPACE_REGISTRY.tsv": "V75_SELECTED_NAMESPACE_REGISTRY.tsv",
        "V75_R3_ORIENTATION_ALTERNATIVES.tsv": "V75_SELECTED_ORIENTATION_ALTERNATIVES.tsv",
        "V75_R3_INSTRUMENT_COMPARISON.tsv": "V75_SELECTED_INSTRUMENT_COMPARISON.tsv",
    }
    for source, target in copies.items():
        copy_bytes(source, target)

    groups = read_tsv(copies["V75_R2_395_ASTRO_GROUPS.tsv"])
    loci = read_tsv(copies["V75_R2_142_ASTRO_LOCI.tsv"])
    instruments = read_tsv(copies["V75_R2_THREE_CELESTIAL_INSTRUMENTS.tsv"])
    namespaces = read_tsv(copies["V75_R3_NAMESPACE_REGISTRY.tsv"])
    orientations = read_tsv(copies["V75_R3_ORIENTATION_ALTERNATIVES.tsv"])
    page_groups = Counter(row["page"] for row in groups)
    page_loci = Counter(row["page"] for row in loci)

    role_files = {
        "R1": ["V75_R1_395_GROUP_CELESTIAL_INTERLINEAR.tsv", "V75_R1_142_LOCUS_CELESTIAL_EDITION.tsv", "V75_R1_THREE_COMPLETE_INSTRUMENT_READINGS.md", "V75_R1_ORIENTATION_AUDIT.tsv", "V75_R1_CELESTIAL_MULTI_INSTRUMENT_REPORT.md", "V75_R1_VALIDATION.json"],
        "R2": ["V75_R2_395_ASTRO_GROUPS.tsv", "V75_R2_142_ASTRO_LOCI.tsv", "V75_R2_THREE_CELESTIAL_INSTRUMENTS.tsv", "V75_R2_HISTORICAL_SOURCE_AUDIT.tsv", "V75_R2_ORIENTATION_ALTERNATIVES.tsv", "V75_R2_UNSUPPORTED_LABELS.tsv", "V75_R2_CELESTIAL_MULTI_INSTRUMENT_REPORT.md", "V75_R2_VALIDATION.json"],
        "R3": ["V75_R3_395_GROUP_LOOKUP_EDITION.tsv", "V75_R3_142_LOCUS_LOOKUP_EDITION.tsv", "V75_R3_NAMESPACE_REGISTRY.tsv", "V75_R3_ORIENTATION_ALTERNATIVES.tsv", "V75_R3_INSTRUMENT_COMPARISON.tsv", "V75_R3_TECHNICAL_REPORT.md", "V75_R3_VALIDATION.json"],
        "R4": ["V75_R4_395_GROUP_CELESTIAL_ATLAS.tsv", "V75_R4_142_LOCUS_CELESTIAL_ATLAS.tsv", "V75_R4_THREE_INSTRUMENTS.tsv", "V75_R4_ORIENTATION_AUDIT.tsv", "V75_R4_CHANCERY_CELESTIAL_ATLAS_REPORT.md", "V75_R4_VALIDATION.json"],
    }
    role_bindings = {role: {name: sha256(ROOT / name) for name in names} for role, names in role_files.items()}
    checks = {
        "groups_395": len(groups) == 395,
        "group_serials_1_to_395": [int(row["group_serial"]) for row in groups] == list(range(1, 396)),
        "loci_142": len(loci) == 142,
        "page_group_counts": page_groups == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "page_locus_counts": page_loci == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "instruments_3": len(instruments) == 3,
        "namespaces_13": len(namespaces) == 13,
        "orientation_alternatives_36": len(orientations) == 36,
        "no_orientation_selected": all(row["selected_orientation"] == "NONE" for row in orientations),
        "no_crosspage_effect": all("NEVER_ALIGNS_F68_WITH_F69" in row["cross_instrument_effect"] for row in orientations),
        "f69_left_slots_28": sum(row["locus"].startswith("f69v.") and row["locus"] not in {"f69v.1", "f69v.2", "f69v.3"} for row in loci) == 28,
        "all_groups_have_local_text": all(row["copied_local_meaning_or_label"].strip() for row in groups),
        "no_f68_f69_key": all(row["f68_f69_mapping"].startswith("NONE") for row in groups),
        "all_role_validations_pass": all(json.loads((ROOT / f"V75_{role}_VALIDATION.json").read_text(encoding="utf-8"))["status"] == "PASS" for role in ("R1", "R2", "R3", "R4")),
        "f84_not_named": not any("f84" in row["page"].lower() for row in groups),
    }
    payload = {
        "schema": "V75_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "selection": {
            "content_edition": "R2_HISTORICAL_CELESTIAL_MULTI_INSTRUMENT",
            "namespace_and_orientation_guard": "R3_TECHNICAL_LOCAL_LOOKUP_REGISTRY",
            "strongest_rival": "ASTRONOMICAL_CALENDAR_OR_PURE_ICONOGRAPHIC_MNEMONIC_ATLAS",
            "external_names_identified": False,
        },
        "counts": {"groups": len(groups), "loci": len(loci), "instruments": len(instruments), "namespaces": len(namespaces), "orientation_alternatives": len(orientations)},
        "checks": checks,
        "role_bindings": role_bindings,
        "selected_bindings": {target: sha256(ROOT / target) for target in copies.values()},
        "sealed_pages_opened": [],
    }
    (ROOT / "V75_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps(payload["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
