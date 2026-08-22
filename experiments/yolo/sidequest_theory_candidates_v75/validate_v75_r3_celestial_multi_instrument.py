#!/usr/bin/env python3
"""Validate V75 R3's local celestial multi-instrument edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def locus_number(source_locus: str) -> int:
    return int(source_locus.rsplit(".", 1)[1])


def main() -> None:
    group_path = OUT / "V75_R3_395_GROUP_LOOKUP_EDITION.tsv"
    locus_path = OUT / "V75_R3_142_LOCUS_LOOKUP_EDITION.tsv"
    namespace_path = OUT / "V75_R3_NAMESPACE_REGISTRY.tsv"
    orientation_path = OUT / "V75_R3_ORIENTATION_ALTERNATIVES.tsv"
    instrument_path = OUT / "V75_R3_INSTRUMENT_COMPARISON.tsv"
    report_path = OUT / "V75_R3_TECHNICAL_REPORT.md"
    summary_path = OUT / "V75_R3_BUILD_SUMMARY.json"
    required = [group_path, locus_path, namespace_path, orientation_path, instrument_path, report_path, summary_path]
    check("all_required_outputs_exist", all(path.is_file() for path in required), [path.name for path in required])

    groups = read_tsv(group_path)
    loci = read_tsv(locus_path)
    namespaces = read_tsv(namespace_path)
    orientations = read_tsv(orientation_path)
    instruments = read_tsv(instrument_path)
    source_groups = {row["astro_group_serial"]: row for row in read_tsv(V69 / "V69_R3_395_ASTRO_GROUP_LEDGER.tsv")}
    final_groups = {row["group_serial"]: row for row in read_tsv(V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv")}
    source_loci = {row["source_locus"]: row for row in read_tsv(V66 / "V66_R3_142_LOCUS_FUNCTIONS.tsv")}
    source_owners = {
        row["locus"]: row
        for row in read_tsv(V71 / "V71_SELECTED_OWNER_LEDGER.tsv")
        if row["section"] == "ASTRO" and row["unit_kind"] == "ASTRO_LOCUS"
    }

    check("exact_395_groups", len(groups) == 395, len(groups))
    check("group_serials_1_through_395_once", [int(row["astro_group_serial"]) for row in groups] == list(range(1, 396)), [groups[0]["astro_group_serial"], groups[-1]["astro_group_serial"]])
    check("unified_ordinals_382_through_776_once", [int(row["unified_group_ordinal"]) for row in groups] == list(range(382, 777)), [groups[0]["unified_group_ordinal"], groups[-1]["unified_group_ordinal"]])
    check("exact_142_loci", len(loci) == 142, len(loci))
    check("only_fixed_three_astro_pages", {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"}, sorted({row["page"] for row in groups}))
    check("group_counts_by_page", Counter(row["page"] for row in groups) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}), dict(Counter(row["page"] for row in groups)))
    check("locus_counts_by_page", Counter(row["page"] for row in loci) == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}), dict(Counter(row["page"] for row in loci)))

    check("all_group_cells_nonblank", all(all(value.strip() for value in row.values()) for row in groups), "395 complete rows")
    check("all_locus_cells_nonblank", all(all(value.strip() for value in row.values()) for row in loci), "142 complete rows")
    check("all_namespace_cells_nonblank", all(all(value.strip() for value in row.values()) for row in namespaces), "13 complete rows")
    check("all_orientation_cells_nonblank", all(all(value.strip() for value in row.values()) for row in orientations), "36 complete rows")
    check("all_instrument_cells_nonblank", all(all(value.strip() for value in row.values()) for row in instruments), "9 complete rows")

    exact_ok = True
    for row in groups:
        source = source_groups[row["astro_group_serial"]]
        final = final_groups[row["astro_group_serial"]]
        exact_ok &= row["diagram_id"] == source["diagram_id"] == final["diagram_id"]
        exact_ok &= row["page"] == source["page"] == final["page"]
        exact_ok &= row["source_locus"] == source["source_locus"] == final["locus"]
        exact_ok &= row["local_locus_id"] == source["local_locus_id"]
        exact_ok &= row["local_group_id"] == source["local_group_id"] == final["opaque_local_id"]
        exact_ok &= row["group_index_within_locus"] == source["group_index_within_locus"] == final["event_index"]
        exact_ok &= row["surface_display_only_exact"] == source["surface_display_only"] == final["surface_display_only"]
        exact_ok &= row["frozen_v69_editorial_address"] == source["local_lookup_address"]
        exact_ok &= row["frozen_v69_formal_role_address_only"] == source["formal_local_role"] == final["local_formal_role"]
    check("exact_surface_identity_and_archived_address_retained", exact_ok, "395/395")

    locus_exact_ok = True
    for row in loci:
        source = source_loci[row["source_locus"]]
        for target, original in [
            ("local_locus_id", "local_locus_id"), ("diagram_id", "diagram_id"), ("page", "page"),
            ("locus_ordinal_editorial", "locus_ordinal_editorial"), ("group_count", "group_count"),
            ("local_group_ids", "local_group_ids"),
            ("surface_sequence_display_only_exact", "surface_sequence_display_only"),
        ]:
            locus_exact_ok &= row[target] == source[original]
    check("exact_locus_group_and_surface_sequences_retained", locus_exact_ok, "142/142")

    owner_ok = all(
        row["smallest_visible_owner"] == source_owners[row["source_locus"]]["selected_visible_owner"]
        and row["owner_status"] == source_owners[row["source_locus"]]["owner_status"]
        for row in groups
    )
    check("all_group_owners_match_v71", owner_ok, "395/395")
    locus_owner_statuses = Counter(row["owner_status"] for row in loci)
    check("frozen_locus_owner_status_distribution", locus_owner_statuses == Counter({"DIRECT_VISIBLE": 93, "INHERITED_VISIBLE": 39, "UNRESOLVED": 7, "PAGE_OWNER_ONLY": 3}), dict(locus_owner_statuses))

    check("every_group_has_exact_local_namespace_address", all(row["v75_local_namespace"] in row["v75_local_namespace_address"] and row["smallest_visible_owner"] in row["v75_local_namespace_address"] and f"FRAGMENT_{int(row['group_index_within_locus']):02d}" in row["v75_local_namespace_address"] for row in groups), "395/395")
    check("every_group_has_concrete_lookup_default", all(row["concrete_technical_lookup_default"].endswith(".") and len(row["concrete_technical_lookup_default"]) >= 150 for row in groups), min(len(row["concrete_technical_lookup_default"]) for row in groups))
    check("every_default_quotes_exact_surface", all(f"„{row['surface_display_only_exact']}“" in row["concrete_technical_lookup_default"] for row in groups), "395/395")
    check("all_confidences_low_and_bounded", all(0.0 < float(row["confidence"]) < 0.50 for row in groups), sorted({row["confidence"] for row in groups}))
    check("all_groups_have_source_class", all(row["source_class"].startswith("OPAQUE_GROUP_") for row in groups), Counter(row["source_class"] for row in groups))
    check("all_groups_have_both_rivals", all(row["iatromedical_rival"].startswith("IATROMEDICAL_RIVAL:") and row["formal_iconographic_rival"].startswith("FORMAL_RIVAL:") for row in groups), "395/395")
    check("all_groups_have_substantial_contradiction", all(len(row["contradiction"]) >= 210 for row in groups), min(len(row["contradiction"]) for row in groups))
    check("all_groups_have_semantic_ceiling", all("NOT_PROSE_CARD_WORD_STEM_SOUND_LANGUAGE_MEANING_OR_TRANSLATION" in row["semantic_ceiling"] for row in groups), "395/395")

    cross_contract = "PAGE_LOCAL_ONLY;NO_F68_F69_JOIN;NO_COMMON_DIRECTION;NO_PROSE_CARD_VALUE"
    check("no_f68_f69_join_or_prose_card_value", all(row["crosspage_contract"] == cross_contract for row in groups), "395/395")
    check("old_models_explicitly_corrected_every_group", all(row["legacy_model_correction"] == "V66_FORMAL_ADDRESS_RETAINED_ONLY;NO_PAGEWIDE_7X12;NO_SINGLE_CENTER_PLUS_28;NO_ORDERED_PAGEWIDE_28_RULES" for row in groups), "395/395")
    forbidden_positive_model_terms = ["bilde r/c", "virtuellen arbeitsauftrag", "gemeinsame f68", "rufe f69", "geordneten vorgänger"]
    positive_defaults = "\n".join(row["concrete_technical_lookup_default"].lower() for row in groups)
    check("no_old_model_in_positive_lookup_defaults", not any(term in positive_defaults for term in forbidden_positive_model_terms), [term for term in forbidden_positive_model_terms if term in positive_defaults])

    check("exact_13_namespaces", len(namespaces) == 13 and len({row["namespace_id"] for row in namespaces}) == 13, len(namespaces))
    check("namespace_group_locus_totals", sum(int(row["group_count"]) for row in namespaces) == 395 and sum(int(row["locus_count"]) for row in namespaces) == 142, {"groups": sum(int(row["group_count"]) for row in namespaces), "loci": sum(int(row["locus_count"]) for row in namespaces)})
    check("all_namespaces_select_no_orientation", all(row["selected_orientation"] == "NONE" for row in namespaces), "13/13")
    check("all_namespaces_reset_and_forbid_crosspage_join", all(row["cross_namespace_rule"].startswith("RESET_ON_NAMESPACE_CHANGE") and row["crosspage_rule"] == "NO_CROSSPAGE_JOIN;F68_AND_F69_KEYS_INCOMPATIBLE" for row in namespaces), "13/13")

    f67_namespaces = {row["namespace_id"] for row in namespaces if row["page"] == "f67r2"}
    check("f67_two_wheels_plus_unresolved_legend_only", f67_namespaces == {"F67_LEFT_WHEEL_NS", "F67_RIGHT_WHEEL_NS", "F67_PAIRED_LEGEND_QUARANTINE_NS"}, sorted(f67_namespaces))
    f67_left_loci = [row for row in loci if row["v75_local_namespace"] == "F67_LEFT_WHEEL_NS"]
    f67_right_loci = [row for row in loci if row["v75_local_namespace"] == "F67_RIGHT_WHEEL_NS"]
    check("f67_wheels_disjoint_and_complete", len(f67_left_loci) == 50 and len(f67_right_loci) == 23 and not ({row["source_locus"] for row in f67_left_loci} & {row["source_locus"] for row in f67_right_loci}), {"left": len(f67_left_loci), "right": len(f67_right_loci)})

    f68_star_loci = [row for row in loci if row["v75_local_namespace"] == "F68_LOCAL_STAR_SLOT_NS"]
    check("f68_28_local_star_loci_direct_but_panel_unassigned", len(f68_star_loci) == 28 and {locus_number(row["source_locus"]) for row in f68_star_loci} == set(range(9, 37)) and all("PANEL_LOCAL_RADIAL" in row["orientation_and_start_alternatives"] for row in f68_star_loci), len(f68_star_loci))
    f68_quarantine = [row for row in loci if row["page"] == "f68r1" and row["owner_status"] == "UNRESOLVED"]
    check("f68_multicentre_and_header_uncertainty_retained", len(f68_quarantine) == 6 and {locus_number(row["source_locus"]) for row in f68_quarantine} == {4, 5, 6, 7, 8, 37}, [row["source_locus"] for row in f68_quarantine])

    f69_left_slots = [row for row in loci if row["page"] == "f69v" and 4 <= locus_number(row["source_locus"]) <= 31]
    check("f69_exactly_28_left_unordered_slots", len(f69_left_slots) == 28 and all(row["v75_local_namespace"] == "F69_LEFT_WHEEL_NS" and "UNORDERED_DIRECT_SLOT" in row["orientation_and_start_alternatives"] for row in f69_left_slots), len(f69_left_slots))
    f69_middle_right = [row for row in loci if row["v75_local_namespace"] in {"F69_MIDDLE_WHEEL_NS", "F69_RIGHT_WHEEL_NS"}]
    check("f69_middle_and_right_have_ring_text_only", len(f69_middle_right) == 2 and {row["source_locus"] for row in f69_middle_right} == {"f69v.2", "f69v.3"}, [(row["source_locus"], row["v75_local_namespace"]) for row in f69_middle_right])
    check("f69_three_wheels_never_share_namespace", {row["v75_local_namespace"] for row in loci if row["page"] == "f69v"} == {"F69_LEFT_WHEEL_NS", "F69_MIDDLE_WHEEL_NS", "F69_RIGHT_WHEEL_NS"}, sorted({row["v75_local_namespace"] for row in loci if row["page"] == "f69v"}))

    check("exact_nine_visible_instruments", len(instruments) == 9 and len({row["instrument_id"] for row in instruments}) == 9, len(instruments))
    required_instruments = {
        "F67_LEFT_WHEEL", "F67_RIGHT_WHEEL", "F68_LEFT_OPEN_STAR_FIELD",
        "F68_MIDDLE_SECTORIZED_SUBMAP", "F68_RIGHT_OPEN_STAR_FIELD", "F68_FACE_CENTRE_SET",
        "F69_LEFT_28_SLOT_WHEEL", "F69_MIDDLE_WAVE_WHEEL", "F69_RIGHT_FACE_RAY_WHEEL",
    }
    check("instrument_inventory_exact", {row["instrument_id"] for row in instruments} == required_instruments, sorted(row["instrument_id"] for row in instruments))
    check("instrument_comparison_has_three_readings", all(row["technical_lookup_reading"] and row["iatromedical_rival"] and row["formal_iconographic_rival"] for row in instruments), "9/9")
    check("no_instrument_selects_start_direction_or_join", all(row["selected_start_or_direction"] == "NONE" and row["cross_instrument_join"] == "NONE" for row in instruments), "9/9")

    check("exact_36_orientation_alternatives", len(orientations) == 36, len(orientations))
    check("four_orientation_alternatives_per_instrument", Counter(row["instrument_id"] for row in orientations) == Counter({instrument: 4 for instrument in required_instruments}), dict(Counter(row["instrument_id"] for row in orientations)))
    check("no_orientation_selected", all(row["selected_orientation"] == "NONE" for row in orientations), "36/36")
    check("orientation_never_aligns_f68_to_f69", all(row["cross_instrument_effect"] == "NONE;NEVER_ALIGNS_F68_WITH_F69" for row in orientations), "36/36")
    circular_instruments = {"F67_LEFT_WHEEL", "F67_RIGHT_WHEEL", "F68_MIDDLE_SECTORIZED_SUBMAP", "F69_LEFT_28_SLOT_WHEEL", "F69_MIDDLE_WAVE_WHEEL", "F69_RIGHT_FACE_RAY_WHEEL"}
    circular_ok = all({row["alternative"] for row in orientations if row["instrument_id"] == instrument} >= {"DIRECT_UNORDERED", "CW_ARBITRARY_START", "CCW_ARBITRARY_START"} for instrument in circular_instruments)
    check("circular_instruments_enumerate_direct_cw_ccw", circular_ok, sorted(circular_instruments))

    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        groups_by_locus[row["source_locus"]].append(row)
    locus_roundtrip = True
    for locus in loci:
        rows = groups_by_locus[locus["source_locus"]]
        locus_roundtrip &= locus["local_group_ids"] == "|".join(row["local_group_id"] for row in rows)
        locus_roundtrip &= locus["surface_sequence_display_only_exact"] == " ".join(row["surface_display_only_exact"] for row in rows)
        locus_roundtrip &= int(locus["group_count"]) == len(rows)
        locus_roundtrip &= all(row["v75_local_namespace"] == locus["v75_local_namespace"] for row in rows)
    check("group_to_locus_roundtrip_exact", locus_roundtrip, "142/142")

    report = report_path.read_text(encoding="utf-8")
    required_report_phrases = [
        "395 Astro-Gruppen", "142 Loci", "keine virtuelle seitenweite 7×12-Matrix",
        "kein einziges Zentrum-plus-28-Objekt", "keine geordnete seitenweite 28-Regelfolge",
        "f67r2 — zwei Räder", "f68r1 — mehrere Paneele und Zentren",
        "f69v — drei Räder; 28 nur links", "36 explizite Alternativen",
        "keine Entzifferung oder Übersetzung", "f84 und f84r",
    ]
    check("report_contains_scope_corrections_and_ceiling", all(phrase in report for phrase in required_report_phrases), required_report_phrases)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_counts = {
        "groups": 395, "loci": 142, "namespaces": 13, "orientation_alternatives": 36,
        "instruments": 9, "f67_groups": 190, "f68_groups": 65, "f69_groups": 140,
        "f69_left_unordered_slots": 28,
    }
    check("build_summary_counts_exact", summary["counts"] == expected_counts, summary["counts"])
    check("summary_no_orientation_join_or_prose_cards", summary["selected_orientation"] == "NONE" and summary["crosspage_mapping"] == "NONE" and summary["prose_card_values"] == "NONE", {key: summary[key] for key in ["selected_orientation", "crosspage_mapping", "prose_card_values"]})
    check("f84_and_f84r_declared_sealed", summary["sealed"] == ["f84", "f84r"], summary["sealed"])

    failed = [item for item in checks if not item["pass"]]
    result = {
        "experiment": "V75_R3_CELESTIAL_MULTI_INSTRUMENT_THIRD_EDITION",
        "status": "PASS" if not failed else "FAIL",
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": [item["name"] for item in failed],
        "dimensions": {"groups": len(groups), "loci": len(loci), "namespaces": len(namespaces), "orientations": len(orientations), "instruments": len(instruments)},
        "checks": checks,
        "selected_orientation": "NONE",
        "crosspage_mapping": "NONE",
        "sealed": ["f84", "f84r"],
    }
    (OUT / "V75_R3_VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failed:
        for item in failed:
            print(f"FAIL {item['name']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
