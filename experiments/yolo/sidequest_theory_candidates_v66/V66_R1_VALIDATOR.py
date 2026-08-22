#!/usr/bin/env python3
"""Validate total coverage, page namespaces, and the explicit no-join policy."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict

from V66_R1_BUILDER import OUT, P22, PAGES, guarded_astro, read_tsv


def load(name: str) -> list[dict[str, str]]:
    return read_tsv(OUT / name)


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    groups = load("V66_R1_395_GROUP_INTERLINEAR.tsv")
    loci = load("V66_R1_142_LOCUS_EDITION.tsv")
    diagrams = load("V66_R1_THREE_DIAGRAMS.tsv")
    grid = load("V66_R1_F67_84_CONFIGURATION_TABLE.tsv")
    stations = load("V66_R1_F68_28_STATIONS.tsv")
    rules = load("V66_R1_F69_28_RULES.tsv")
    orientations = load("V66_R1_ORIENTATION_ALTERNATIVES.tsv")
    contracts = load("V66_R1_NAMESPACE_CONTRACT.tsv")
    source = guarded_astro(P22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    source_rules = read_tsv(P22 / "V22_F69_28_RULES.tsv")

    require(len(groups) == len(source) == 395, "group count must be 395")
    require(len(loci) == 142, "locus count must be 142")
    require(len(diagrams) == 3, "diagram count must be 3")
    require(len(grid) == 84, "f67 7x12 table must contain 84 combinations")
    require(len(stations) == 28, "f68 station count must be 28")
    require(len(rules) == 28, "f69 rule count must be 28")
    require(len(orientations) == 112, "two 28x2 orientation families must contain 112 rows")
    require(len(contracts) == 3, "namespace contract must contain three rows")

    expected_groups = {"f67r2": 190, "f68r1": 65, "f69v": 140}
    expected_loci = {"f67r2": 74, "f68r1": 37, "f69v": 31}
    require(Counter(row["page"] for row in groups) == Counter(expected_groups), "page group counts mismatch")
    require(Counter(row["page"] for row in loci) == Counter(expected_loci), "page locus counts mismatch")
    require({row["page"] for row in groups} == set(PAGES), "page scope mismatch")
    require(all(not row["page"].startswith("f84") for row in groups + loci + diagrams), "sealed page leaked")

    source_by_serial = {row["source_event_serial"]: row for row in source}
    require(len(source_by_serial) == 395, "source serials not unique")
    require({row["source_event_serial"] for row in groups} == set(source_by_serial), "source coverage mismatch")
    for row in groups:
        src = source_by_serial[row["source_event_serial"]]
        require(row["surface_display_only"] == src["surface"], f"surface changed at {row['source_event_serial']}")
        require(row["astro_local_group_id"] == src["exact_tuple_id"], f"local ID changed at {row['source_event_serial']}")
        require(row["astro_local_group_id"].startswith(f"ASTRO_{row['page']}_"), f"nonlocal ID at {row['source_event_serial']}")
        require(row["german_group_default"].startswith("[ASTRO_LOKAL_EXEMPLAR; KEINE_PROSAKARTE]"), f"unmarked default at {row['source_event_serial']}")
        require(row["competing_value_system"], f"missing rival at {row['source_event_serial']}")
        require(row["cross_page_join"] == "NONE", f"join leaked at {row['source_event_serial']}")
        require(row["binding_status"] == "PAGE_LOCAL_EXEMPLAR;SURFACE_HAS_NO_IMPORTED_MEANING", f"binding contract changed at {row['source_event_serial']}")

    namespace = {"f67r2": "A67", "f68r1": "A68", "f69v": "A69"}
    for row in groups + loci:
        require(row["page_namespace"] == namespace[row["page"]], f"namespace mismatch at {row['locus']}")
        require(row["inventory_address"].startswith(namespace[row["page"]] + ":"), f"foreign address at {row['locus']}")
        require(row["cross_page_join"] == "NONE", f"cross-page join at {row['locus']}")

    source_locus_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    output_locus_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source:
        source_locus_groups[(row["page"], row["locus"])].append(row)
    for row in groups:
        output_locus_groups[(row["page"], row["locus"])].append(row)
    require(set(source_locus_groups) == set(output_locus_groups), "locus identity coverage mismatch")
    locus_map = {(row["page"], row["locus"]): row for row in loci}
    for key, rows in output_locus_groups.items():
        locus = locus_map[key]
        require(int(locus["group_count"]) == len(rows), f"locus group count mismatch {key}")
        require(locus["complete_german_locus_default"].startswith("[ASTRO_LOKAL_EXEMPLAR; KEINE_PROSAKARTE]"), f"unmarked locus {key}")
        require(locus["surface_sequence_display_only"] == " ".join(row["surface_display_only"] for row in rows), f"locus order mismatch {key}")

    grid_pairs = {(int(row["planet_axis_index"]), int(row["zodiac_axis_index"])) for row in grid}
    require(grid_pairs == {(p, z) for p in range(1, 8) for z in range(1, 13)}, "7x12 pair coverage mismatch")
    require(all(row["visible_matrix_cell"] == "NO_DERIVED_FROM_TWO_VISIBLE_INVENTORIES" for row in grid), "derived grid presented as visible")
    require(all(row["medical_configuration_default"].startswith("[IATROMED_EXEMPLAR]") for row in grid), "unmarked f67 medical combination")
    require(all(row["calendar_rival_default"].startswith("[KALENDER_RIVALE]") for row in grid), "unmarked f67 rival")

    require([row["source_locus"] for row in stations] == [f"f68r1.{i}" for i in range(9, 37)], "f68 station loci mismatch")
    require(len({row["station_address"] for row in stations}) == 28, "f68 station addresses not unique")
    require(len({row["conventional_name_exemplar"] for row in stations}) == 28, "f68 mansion names not unique")
    require(all(row["cross_page_join"] == "NONE" for row in stations), "f68 station join leaked")

    require([int(row["ordered_rule_index"]) for row in rules] == list(range(1, 29)), "f69 rule order mismatch")
    require([row["source_locus"] for row in rules] == [f"f69v.{i}" for i in range(4, 32)], "f69 rule loci mismatch")
    require(Counter(row["layout_class"] for row in rules) == Counter({"LONG": 14, "SHORT": 14}), "f69 layout counts mismatch")
    require(all(row["layout_polarity"] == "NONE" and row["cross_page_join"] == "NONE" for row in rules), "layout polarity or join restored")
    repeated = [row for row in rules if row["surface_entry_display_only"] == "okeod"]
    require([int(row["ordered_rule_index"]) for row in repeated] == [11, 15, 24], "okeod positions mismatch")
    require([row["layout_class"] for row in repeated] == ["LONG", "LONG", "SHORT"], "okeod parity witness mismatch")
    require(len({row["medical_regimen_default"] for row in repeated}) == 1, "okeod rule not identity-consistent")

    src_f68 = [row["surface_display_only"] for row in stations]
    src_f69 = [row["surface_entry_display_only"] for row in rules]
    require(sum(a == b for a, b in zip(src_f68, src_f69)) == 0, "same-index f68/f69 full-form match unexpectedly present")
    require(set(src_f68).isdisjoint(src_f69), "cross-inventory exact full-form overlap unexpectedly present")

    system_counts = Counter(row["system"] for row in orientations)
    require(system_counts == Counter({"A68_SPATIAL": 56, "A69_RULE_TRAVERSAL": 56}), "orientation family counts mismatch")
    for system in system_counts:
        rows = [row for row in orientations if row["system"] == system]
        require({(row["direction"], int(row["rotation_offset"])) for row in rows} == {(d, r) for d in ("ASC", "DESC") for r in range(28)}, f"orientation coverage mismatch {system}")
        require(all(len(row["full_mapping_or_traversal"].split("|")) == 28 for row in rows), f"incomplete orientation mapping {system}")
        require(all(row["evidence_preference"] == "NONE" and row["cross_page_join"] == "NONE" for row in rows), f"orientation preference/join leaked {system}")

    require([row["page"] for row in diagrams] == list(PAGES), "diagram order mismatch")
    for row in diagrams:
        require(int(row["group_count"]) == expected_groups[row["page"]], f"diagram group count mismatch {row['page']}")
        require(int(row["locus_count"]) == expected_loci[row["page"]], f"diagram locus count mismatch {row['page']}")
        require(row["direct_crosspage_mapping"] == "NONE" and row["prose_card_import"] == "NONE", f"diagram separation failure {row['page']}")
        for locus in (x for x in loci if x["page"] == row["page"]):
            require(f"[{locus['locus']}]" in row["complete_german_diagram_reading"], f"diagram text omits {locus['locus']}")

    require(all(row["cross_page_join"] == "NONE" for row in contracts), "namespace contract join failure")
    digest = hashlib.sha256("\n".join(row["astro_local_group_id"] for row in groups).encode()).hexdigest()
    validation = {
        "status": "PASS",
        "pages": list(PAGES),
        "groups": len(groups),
        "loci": len(loci),
        "diagrams": len(diagrams),
        "page_group_counts": dict(Counter(row["page"] for row in groups)),
        "page_locus_counts": dict(Counter(row["page"] for row in loci)),
        "f67_7x12_configurations": len(grid),
        "f68_spatial_stations": len(stations),
        "f69_ordered_rules": len(rules),
        "orientation_alternatives": len(orientations),
        "same_index_f68_f69_matches": 0,
        "all_pair_f68_f69_full_form_matches": 0,
        "cross_page_join_rows": 0,
        "prose_card_import_rows": 0,
        "okeod_identity_witness": {"indices": [11, 15, 24], "layouts": ["LONG", "LONG", "SHORT"], "distinct_defaults": 1},
        "astro_local_identity_sha256": digest,
    }
    (OUT / "V66_R1_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
