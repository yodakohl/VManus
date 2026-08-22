#!/usr/bin/env python3
"""Validate V75 R1 coverage, source fidelity, namespaces and orientation ceilings."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_SELECTED_OWNER_LEDGER.tsv"
GROUPS = OUT / "V75_R1_395_GROUP_CELESTIAL_INTERLINEAR.tsv"
LOCI = OUT / "V75_R1_142_LOCUS_CELESTIAL_EDITION.tsv"
READING = OUT / "V75_R1_THREE_COMPLETE_INSTRUMENT_READINGS.md"
AUDIT = OUT / "V75_R1_ORIENTATION_AUDIT.tsv"
RESULT = OUT / "V75_R1_VALIDATION.json"
PAGES = {"f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source = read_tsv(V69)
    owners = [r for r in read_tsv(V71)
              if r["unit_kind"] == "ASTRO_LOCUS" and r["page"] in PAGES]
    groups = read_tsv(GROUPS)
    loci = read_tsv(LOCI)
    audit = read_tsv(AUDIT)
    reading = READING.read_text(encoding="utf-8")

    src_by_serial = {r["group_serial"]: r for r in source}
    own_by_locus = {r["locus"]: r for r in owners}
    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        groups_by_locus[row["locus"]].append(row)
    locus_by_id = {r["locus"]: r for r in loci}

    required_group = [
        "opaque_local_id", "surface_display_only", "exact_visible_identity_layer",
        "v71_visible_owner", "local_namespace", "silent_argument_default",
        "concrete_copied_label_or_instruction", "source_status", "confidence",
        "historical_celestial_rival", "technical_formal_rival", "contradiction",
    ]
    checks: dict[str, bool] = {}
    checks["exactly_395_groups"] = len(groups) == 395
    checks["group_serials_exact_1_to_395"] = [int(r["group_serial"]) for r in groups] == list(range(1, 396))
    checks["exactly_142_loci"] = len(loci) == 142 and len(locus_by_id) == 142
    checks["pages_exactly_fixed_three"] = {r["page"] for r in groups} == PAGES == {r["page"] for r in loci}
    checks["page_group_counts_exact"] = Counter(r["page"] for r in groups) == {"f67r2": 190, "f68r1": 65, "f69v": 140}
    checks["page_locus_counts_exact"] = Counter(r["page"] for r in loci) == {"f67r2": 74, "f68r1": 37, "f69v": 31}
    checks["source_group_identities_exact"] = len(src_by_serial) == 395 and all(
        r["group_serial"] in src_by_serial and
        all(r[k] == src_by_serial[r["group_serial"]][k] for k in
            ("diagram_id", "page", "locus", "event_index", "opaque_local_id",
             "surface_display_only")) and
        r["v69_local_formal_role"] == src_by_serial[r["group_serial"]]["local_formal_role"]
        for r in groups)
    checks["exact_identity_layer_contains_id_locus_surface"] = all(
        r["opaque_local_id"] in r["exact_visible_identity_layer"] and
        r["locus"] in r["exact_visible_identity_layer"] and
        r["surface_display_only"] in r["exact_visible_identity_layer"]
        for r in groups)
    checks["all_group_required_values_nonempty"] = all(
        all(r.get(k, "").strip() for k in required_group) for r in groups)
    checks["every_group_instruction_copies_its_surface"] = all(
        r["surface_display_only"] in r["concrete_copied_label_or_instruction"] and
        r["concrete_copied_label_or_instruction"].endswith(".")
        for r in groups)
    checks["v71_owner_status_owner_and_default_exact"] = len(own_by_locus) == 142 and all(
        r["locus"] in own_by_locus and
        r["v71_owner_status"] == own_by_locus[r["locus"]]["owner_status"] and
        r["v71_visible_owner"] == own_by_locus[r["locus"]]["selected_visible_owner"] and
        r["silent_argument_default"] == own_by_locus[r["locus"]]["silent_argument_default"]
        for r in groups)
    checks["locus_membership_and_labels_exact"] = all(
        locus in groups_by_locus and
        int(row["group_count"]) == len(groups_by_locus[locus]) == int(own_by_locus[locus]["member_count"]) and
        row["group_serials"] == "|".join(r["group_serial"] for r in groups_by_locus[locus]) and
        row["opaque_local_ids"] == "|".join(r["opaque_local_id"] for r in groups_by_locus[locus]) and
        row["surface_sequence"] == "|".join(r["surface_display_only"] for r in groups_by_locus[locus]) and
        row["complete_visible_label"] == " ".join(r["surface_display_only"] for r in groups_by_locus[locus])
        for locus, row in locus_by_id.items())
    checks["locus_owners_exact_v71"] = all(
        r["selected_visible_owner"] == own_by_locus[r["locus"]]["selected_visible_owner"] and
        r["v71_owner_status"] == own_by_locus[r["locus"]]["owner_status"] and
        r["visible_basis"] == own_by_locus[r["locus"]]["visible_basis"]
        for r in loci)
    checks["f67_has_two_separate_wheels_plus_unresolved_legend"] = {
        r["local_namespace"] for r in loci if r["page"] == "f67r2"
    } == {"A67_RIGHT_CELESTIAL_WHEEL", "A67_LEFT_CELESTIAL_WHEEL",
          "A67_PAIRED_WHEEL_PAGE_LEGEND_UNRESOLVED"}
    checks["f68_is_multipanel_with_28_spatial_star_labels"] = (
        sum(r["local_owner_kind"] == "MULTIPANEL_STAR_LABEL" for r in loci) == 28 and
        all("SOURCE_LOCUS_ADDRESS_ONLY" in r["orientation_status"]
            for r in loci if r["page"] == "f68r1") and
        len({r["local_namespace"] for r in loci if r["page"] == "f68r1"}) == 4)
    f69_slots = [r for r in loci if r["local_owner_kind"] == "LEFT_WHEEL_UNORDERED_RADIAL_SLOT_LABEL"]
    checks["exactly_28_f69_slots_only_on_left_wheel"] = (
        len(f69_slots) == 28 and
        {r["locus"] for r in f69_slots} == {f"f69v.{i}" for i in range(4, 32)} and
        all(r["local_namespace"] == "A69_LEFT_28_PLACE_WHEEL" for r in f69_slots) and
        not any("RADIAL_SLOT" in r["selected_visible_owner"] and
                r["local_namespace"] != "A69_LEFT_28_PLACE_WHEEL" for r in loci))
    checks["f69_three_disconnected_wheel_namespaces"] = {
        r["local_namespace"] for r in loci if r["page"] == "f69v"
    } == {"A69_LEFT_28_PLACE_WHEEL", "A69_MIDDLE_CLOUD_WAVE_WHEEL",
          "A69_RIGHT_FACE_RAY_WHEEL"}
    checks["no_start_direction_rotation_or_crosspage_join"] = all(
        r["authorial_start"] == "UNKNOWN_OR_NOT_APPLICABLE" and
        r["authorial_direction"] == "UNKNOWN_OR_NOT_APPLICABLE" and
        r["rotation_status"] == "UNLICENSED" and
        r["f68_f69_mapping"] == "NONE" and r["cross_wheel_join"] == "NONE"
        for r in groups)
    checks["no_prose_card_or_global_7x12"] = all(
        r["prose_card_import"] == "NONE" and r["global_7x12"] == "NONE"
        for r in groups + loci)
    checks["all_group_rival_layers_present"] = all(
        r["historical_celestial_rival"] and r["technical_formal_rival"] and r["contradiction"]
        for r in groups)
    checks["all_142_loci_present_once_in_continuous_reading"] = (
        len(re.findall(r"^- \*\*(f(?:67r2|68r1|69v)\.\d+)\*\*", reading, flags=re.M)) == 142 and
        set(re.findall(r"^- \*\*(f(?:67r2|68r1|69v)\.\d+)\*\*", reading, flags=re.M)) == set(locus_by_id))
    checks["three_complete_page_readings_present"] = all(
        heading in reading for heading in (
            "## f67r2 — zwei getrennte Himmelsräder",
            "## f68r1 — mehrpaneeliger Sternatlas",
            "## f69v — drei unverbundene heterogene Räder"))
    checks["orientation_audit_complete"] = (
        len(audit) == 15 and [r["audit_id"] for r in audit] == [f"O{i:02d}" for i in range(1, 16)] and
        all(r["cross_namespace_join"] == "NONE" for r in audit) and
        any(r["instrument_scope"] == "globale 7×12-Annahme" and r["rotation_status"] == "FORBIDDEN" for r in audit) and
        any(r["page_scope"] == "f68r1↔f69v" and r["rotation_status"] == "FORBIDDEN" for r in audit))
    old_value_terms = ("Saturn", "Jupiter", "Mars", "Venus", "Merkur", "Widder", "Stier",
                       "Aderlass", "Warmbad", "Heilmittel")
    checks["old_v66_exemplar_values_not_imported_as_group_instructions"] = not any(
        term in r["concrete_copied_label_or_instruction"] for term in old_value_terms for r in groups)
    checks["semantic_ceiling_explicit_everywhere"] = all(
        "NOT_WORD_CARD_STEM_SOUND_LANGUAGE_OR_MEANING" in r["semantic_ceiling"] for r in groups)

    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "experiment": "V75_R1_CELESTIAL_MULTI_INSTRUMENT_THIRD_EDITION",
        "status": status,
        "counts": {
            "groups": len(groups),
            "loci": len(loci),
            "pages": len({r["page"] for r in loci}),
            "orientation_audit_rows": len(audit),
            "groups_by_page": dict(Counter(r["page"] for r in groups)),
            "loci_by_page": dict(Counter(r["page"] for r in loci)),
            "owner_status_loci": dict(Counter(r["v71_owner_status"] for r in loci)),
            "owner_status_groups": dict(Counter(r["v71_owner_status"] for r in groups)),
            "local_namespaces": len({r["local_namespace"] for r in loci}),
            "f68_spatial_star_labels": sum(r["local_owner_kind"] == "MULTIPANEL_STAR_LABEL" for r in loci),
            "f69_left_unordered_slots": len(f69_slots),
        },
        "checks": checks,
        "constraints": {
            "common_start_added": False,
            "direction_added": False,
            "rotation_added": False,
            "f68_f69_key_added": False,
            "prose_card_import_added": False,
            "global_7x12_added": False,
            "new_card_stem_sound_language_meaning": False,
            "new_pages_read": False,
            "f84_or_f84r_opened": False,
            "active_v75_sibling_output_read": False,
            "commit_or_push": False,
        },
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
