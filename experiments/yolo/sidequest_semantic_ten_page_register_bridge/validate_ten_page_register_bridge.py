#!/usr/bin/env python3
"""Validate the unified prose/diagram workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROSE = HERE.parent / "sidequest_semantic_bound_carrier_closure"
ASTRO80 = HERE.parent / "sidequest_theory_candidates_v80"
ASTRO75 = HERE.parent / "sidequest_theory_candidates_v75"

PROSE_EVENTS_IN = PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv"
ASTRO_GROUPS_IN = ASTRO80 / "V80_R3_395_ASTRO_GROUPS.tsv"
ASTRO_LOCI_IN = ASTRO75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
NAMESPACES_IN = ASTRO75 / "V75_SELECTED_NAMESPACE_REGISTRY.tsv"

COMPONENTS = HERE / "SHARED_22_COMPONENT_BRIDGE.tsv"
ASTRO_GROUPS = HERE / "ASTRO_395_BRIDGED_GROUPS.tsv"
ASTRO_LOCI = HERE / "ASTRO_142_BRIDGED_LOCI.tsv"
UNIFIED = HERE / "TEN_PAGE_776_UNIFIED_READING.tsv"
EXAMPLES = HERE / "BRIDGE_EXAMPLES.tsv"
MANUAL = HERE / "TEN_PAGE_WORKSHOP_MANUAL.md"
SUMMARY = HERE / "BUILD_SUMMARY.json"
VALIDATION = HERE / "VALIDATION.json"
BUILDER = HERE / "build_ten_page_register_bridge.py"
OUTPUTS = [COMPONENTS, ASTRO_GROUPS, ASTRO_LOCI, UNIFIED, EXAMPLES, MANUAL, SUMMARY]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    prose_source = read_tsv(PROSE_EVENTS_IN)
    astro_source = read_tsv(ASTRO_GROUPS_IN)
    locus_source = read_tsv(ASTRO_LOCI_IN)
    namespace_source = read_tsv(NAMESPACES_IN)
    components = read_tsv(COMPONENTS)
    groups = read_tsv(ASTRO_GROUPS)
    loci = read_tsv(ASTRO_LOCI)
    unified = read_tsv(UNIFIED)
    examples = read_tsv(EXAMPLES)

    check("source_counts", (len(prose_source), len(astro_source), len(locus_source), len(namespace_source)) == (381, 395, 142, 13),
          f"prose={len(prose_source)}, astro={len(astro_source)}, loci={len(locus_source)}, namespaces={len(namespace_source)}")
    check("component_inventory", len(components) == 22 and len({row["component_id"] for row in components}) == 22,
          f"rows={len(components)}, unique_ids={len({row['component_id'] for row in components})}")
    check("component_values", all(row["common_operational_nucleus_de"] and row["prose_register_expansion_de"]
          and row["astro_register_expansion_de"] for row in components), "every shared component has common, prose, and diagram values")

    source_group_map = {row["group_serial"]: row for row in astro_source}
    group_map = {row["group_serial"]: row for row in groups}
    check("astro_group_inventory", len(groups) == 395 and len(group_map) == 395 and set(group_map) == set(source_group_map),
          f"rows={len(groups)}, unique_groups={len(group_map)}")
    group_binding_ok = all(
        row["surface_display"] == source_group_map[serial]["surface_display_only"]
        and row["page"] == source_group_map[serial]["page"]
        and row["locus"] == source_group_map[serial]["locus"]
        and row["opaque_local_id"] == source_group_map[serial]["opaque_local_id"]
        for serial, row in group_map.items()
    )
    check("astro_group_binding", group_binding_ok, "all group surfaces, pages, loci, and local ids match the selected atlas")
    page_counts = Counter(row["page"] for row in groups)
    check("astro_page_counts", page_counts == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
          f"f67r2={page_counts['f67r2']}, f68r1={page_counts['f68r1']}, f69v={page_counts['f69v']}")

    class_counts = Counter(row["bridge_class"] for row in groups)
    expected_classes = Counter({
        "EXACT_PROSE_SURFACE_BRIDGE": 89,
        "COMPOSED_COMPONENT_BRIDGE": 78,
        "SINGLE_COMPONENT_BRIDGE": 165,
        "LOCAL_ASTRO_NOMENCLATOR": 63,
    })
    check("bridge_classes", class_counts == expected_classes,
          ", ".join(f"{key}={class_counts[key]}" for key in sorted(class_counts)))
    bridged_count = class_counts["EXACT_PROSE_SURFACE_BRIDGE"] + class_counts["COMPOSED_COMPONENT_BRIDGE"] + class_counts["SINGLE_COMPONENT_BRIDGE"]
    check("bridge_coverage", bridged_count == 332 and class_counts["LOCAL_ASTRO_NOMENCLATOR"] == 63,
          f"shared_surface_or_component={bridged_count}, local_nomenclator={class_counts['LOCAL_ASTRO_NOMENCLATOR']}")
    exact_surface_types = {row["surface_display"] for row in groups if row["bridge_class"] == "EXACT_PROSE_SURFACE_BRIDGE"}
    check("exact_surface_reuse", len(exact_surface_types) == 44,
          f"exact_group_occurrences={class_counts['EXACT_PROSE_SURFACE_BRIDGE']}, exact_surface_types={len(exact_surface_types)}")
    check("complete_astro_defaults", all(row["astro_working_reading_de"] and row["matched_component_values_de"] for row in groups),
          "all 395 diagram groups have a concrete operational or local-name default")
    check("no_placeholder_defaults", not any(token in row["astro_working_reading_de"].upper()
          for row in groups for token in ["UNKNOWN", "UNBEKANNT", "EXEMPLAR_ONLY"]),
          "no diagram reading falls back to an unknown placeholder")
    check("diagram_guards", all(row["orientation_rule"] == "LOCAL_OWNER_ONLY__NO_START_OR_DIRECTION"
          and row["crosspage_rule"] == "NO_F68_F69_KEY__NO_IMPLICIT_NAMESPACE_JOIN" for row in groups),
          "all diagram groups retain local owner, no direction, and no f68-f69 key")

    source_locus_map = {row["locus"]: row for row in locus_source}
    locus_map = {row["locus"]: row for row in loci}
    check("locus_inventory", len(loci) == 142 and len(locus_map) == 142 and set(locus_map) == set(source_locus_map),
          f"rows={len(loci)}, unique_loci={len(locus_map)}")
    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        groups_by_locus[row["locus"]].append(row)
    locus_binding_ok = sum(int(row["group_count"]) for row in loci) == 395 and all(
        int(row["group_count"]) == len(groups_by_locus[row["locus"]])
        and row["surface_sequence"] == " ".join(group["surface_display"] for group in groups_by_locus[row["locus"]])
        and bool(row["complete_workshop_reading_de"])
        for row in loci
    )
    check("locus_binding", locus_binding_ok, "all 142 locus readings preserve and exhaust the 395 group sequences")

    register_counts = Counter(row["register"] for row in unified)
    check("unified_inventory", len(unified) == 776 and register_counts == Counter({"PROSE_WORKSHOP": 381, "ASTRO_DIAGRAM": 395}),
          f"rows={len(unified)}, prose={register_counts['PROSE_WORKSHOP']}, astro={register_counts['ASTRO_DIAGRAM']}")
    check("unified_page_scope", {row["page"] for row in unified} == ALLOWED_PAGES,
          "the unified ledger contains exactly the fixed ten pages")
    prose_unified = [row for row in unified if row["register"] == "PROSE_WORKSHOP"]
    prose_binding_ok = all(
        row["local_unit_id"] == source["event_id"]
        and row["surface_display"] == source["surface_display"]
        and row["operational_reading_de"] == source["contextual_event_reading_de"]
        for row, source in zip(prose_unified, prose_source, strict=True)
    )
    check("unified_prose_binding", prose_binding_ok, "all 381 selected prose readings enter unchanged")
    check("unified_complete_readings", all(row["operational_reading_de"] for row in unified),
          "every one of the 776 rows has a working reading")
    selected_namespaces = {row["namespace_id"] for row in groups}
    source_namespaces = {row["namespace_id"] for row in namespace_source}
    check("namespace_inventory", selected_namespaces == source_namespaces and len(selected_namespaces) == 13,
          "all and only the thirteen selected local diagram namespaces occur")

    check("example_inventory", len(examples) >= 10 and all(row["astro_working_reading_de"] for row in examples),
          f"worked_examples={len(examples)}")
    manual_text = MANUAL.read_text(encoding="utf-8")
    check("manual_contract", all(token in manual_text for token in ["AIR ist LAUF", "HO ist EINGANGSPOSTEN", "OR ist ARBEITSSATZ", "f68-f69"]),
          "manual teaches register expansion and keeps the diagram namespaces separate")
    check("sealed_page_scope", not any(row["page"].startswith("f84") for row in unified),
          "no sealed page selector occurs; tuple or content hashes are not treated as page selectors")

    before = {path.name: digest(path) for path in OUTPUTS}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True)
    after = {path.name: digest(path) for path in OUTPUTS}
    check("deterministic_rebuild", rebuilt.returncode == 0 and before == after,
          "all bridge artifacts rebuilt byte-identically")

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    result = {
        "status": status,
        "checks_passed": sum(bool(row["passed"]) for row in checks),
        "checks_total": len(checks),
        "counts": {
            "shared_components": len(components),
            "prose_events": 381,
            "astro_groups": 395,
            "astro_loci": 142,
            "namespaces": 13,
            "unified_rows": 776,
            "exact_surface_bridge": class_counts["EXACT_PROSE_SURFACE_BRIDGE"],
            "composed_component_bridge": class_counts["COMPOSED_COMPONENT_BRIDGE"],
            "single_component_bridge": class_counts["SINGLE_COMPONENT_BRIDGE"],
            "local_astro_nomenclator": class_counts["LOCAL_ASTRO_NOMENCLATOR"],
        },
        "checks": checks,
        "artifact_sha256": {path.name: digest(path) for path in OUTPUTS},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
