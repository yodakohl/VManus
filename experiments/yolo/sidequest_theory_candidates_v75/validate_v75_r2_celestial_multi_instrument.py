#!/usr/bin/env python3
"""Validate completeness, visual ontology, and semantic ceilings of V75 R2."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"

SOURCE_GROUPS = V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
SOURCE_OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
SOURCE_IMAGES = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
SOURCE_HISTORICAL = V66 / "V66_R2_HISTORICAL_SOURCES.tsv"

GROUPS = OUT / "V75_R2_395_ASTRO_GROUPS.tsv"
LOCI = OUT / "V75_R2_142_ASTRO_LOCI.tsv"
INSTRUMENTS = OUT / "V75_R2_THREE_CELESTIAL_INSTRUMENTS.tsv"
SOURCES = OUT / "V75_R2_HISTORICAL_SOURCE_AUDIT.tsv"
ORIENTATIONS = OUT / "V75_R2_ORIENTATION_ALTERNATIVES.tsv"
UNSUPPORTED = OUT / "V75_R2_UNSUPPORTED_LABELS.tsv"
REPORT = OUT / "V75_R2_CELESTIAL_MULTI_INSTRUMENT_REPORT.md"
BUILDER = OUT / "build_v75_r2_celestial_multi_instrument.py"
VALIDATION = OUT / "V75_R2_VALIDATION.json"

PAGE_GROUP_COUNTS = {"f67r2": 190, "f68r1": 65, "f69v": 140}
PAGE_LOCUS_COUNTS = {"f67r2": 74, "f68r1": 37, "f69v": 31}
PAGE_DIAGRAM = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}
EXPECTED_OWNER_STATUS = Counter({"DIRECT_VISIBLE": 93, "INHERITED_VISIBLE": 39, "UNRESOLVED": 7, "PAGE_OWNER_ONLY": 3})
EXPECTED_ORIENTATION = "LOCAL_EDITORIAL_ADDRESS_ONLY__NO_AUTHORIAL_START_ROTATION_OR_DIRECTION"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def checked(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = bool(condition)


def ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def main() -> None:
    source_groups = read_tsv(SOURCE_GROUPS)
    source_owners = {
        r["unit_id"]: r for r in read_tsv(SOURCE_OWNERS)
        if r["unit_kind"] == "ASTRO_LOCUS"
    }
    source_images = {
        r["page"]: r for r in read_tsv(SOURCE_IMAGES) if r["section"] == "ASTRO"
    }
    source_historical = {r["source_id"]: r for r in read_tsv(SOURCE_HISTORICAL)}

    groups = read_tsv(GROUPS)
    loci = read_tsv(LOCI)
    instruments = read_tsv(INSTRUMENTS)
    sources = read_tsv(SOURCES)
    orientations = read_tsv(ORIENTATIONS)
    unsupported = read_tsv(UNSUPPORTED)
    report = REPORT.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checked(len(groups) == 395, "exactly_395_group_rows", checks)
    checked(len(loci) == 142, "exactly_142_locus_rows", checks)
    checked(len(instruments) == 3, "exactly_3_instrument_rows", checks)
    checked(len(sources) == 8, "exactly_8_historical_source_rows", checks)
    checked(len(orientations) == 15, "exactly_15_orientation_alternatives", checks)
    checked(len(unsupported) >= 14, "unsupported_label_audit_is_explicit_and_bounded", checks)
    checked([r["group_serial"] for r in groups] == [str(i) for i in range(1, 396)], "group_serials_1_395_exact_order", checks)
    checked(Counter(r["page"] for r in groups) == Counter(PAGE_GROUP_COUNTS), "page_group_counts_190_65_140", checks)
    checked(Counter(r["page"] for r in loci) == Counter(PAGE_LOCUS_COUNTS), "page_locus_counts_74_37_31", checks)
    checked({r["page"] for r in groups} == {"f67r2", "f68r1", "f69v"}, "only_three_fixed_astro_pages", checks)
    checked(all(r["diagram_id"] == PAGE_DIAGRAM[r["page"]] for r in groups + loci + instruments), "diagram_page_namespaces_exact", checks)

    source_by_serial = {r["group_serial"]: r for r in source_groups}
    source_group_identity = all(
        all(r[k] == source_by_serial[r["group_serial"]][k] for k in ("diagram_id", "page", "locus", "event_index", "opaque_local_id"))
        for r in groups
    )
    checked(source_group_identity, "v69_opaque_group_identity_order_and_locus_exact", checks)
    checked(all("surface" not in k.casefold() for k in groups[0]), "no_surface_spelling_column", checks)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_page_loci: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_locus[row["locus"]].append(row)
    for row in loci:
        by_page_loci[row["page"]].append(row)

    owner_exact = True
    group_local_label_exact = True
    for row in groups:
        owner = source_owners[row["locus"]]
        if row["local_image_owner"] != owner["selected_visible_owner"]:
            owner_exact = False
        if row["owner_status"] != owner["owner_status"] or row["owner_confidence"] != owner["confidence"]:
            owner_exact = False
        members = by_locus[row["locus"]]
        complete = next(l["complete_copied_local_meaning_or_label"] for l in loci if l["locus"] == row["locus"])
        if complete not in row["copied_local_meaning_or_label"]:
            group_local_label_exact = False
        expected_index = int(row["event_index"])
        if len(members) == 1:
            if not row["copied_local_meaning_or_label"].startswith("Vollständiges lokales Etikett:"):
                group_local_label_exact = False
        elif not row["copied_local_meaning_or_label"].startswith(f"Kopiersegment {expected_index:02d}/{len(members):02d}"):
            group_local_label_exact = False
    checked(owner_exact, "every_group_has_exact_v71_owner_status_and_confidence", checks)
    checked(group_local_label_exact, "every_group_bound_to_complete_local_copied_label_without_word_gloss", checks)

    locus_exact = True
    for row in loci:
        owner = source_owners[row["locus"]]
        members = by_locus[row["locus"]]
        if row["group_count"] != owner["member_count"] or row["group_count"] != str(len(members)):
            locus_exact = False
        if row["group_serials"] != "|".join(r["group_serial"] for r in members):
            locus_exact = False
        if row["opaque_group_ids"] != "|".join(r["opaque_local_id"] for r in members):
            locus_exact = False
        if row["local_image_owner"] != owner["selected_visible_owner"]:
            locus_exact = False
        if row["owner_status"] != owner["owner_status"] or row["owner_confidence"] != owner["confidence"]:
            locus_exact = False
        if row["silent_argument_default"] != owner["silent_argument_default"]:
            locus_exact = False
        if row["image_geometry_guard"] != source_images[row["page"]]["selected_geometry"]:
            locus_exact = False
    checked(locus_exact, "locus_membership_v71_owner_and_v70_geometry_exact", checks)
    checked(Counter(r["owner_status"] for r in loci) == EXPECTED_OWNER_STATUS, "owner_status_distribution_exact", checks)

    checked(all(r["copied_local_meaning_or_label"].strip() for r in groups), "all_groups_have_local_meaning_or_label", checks)
    checked(all(r["copied_label_source_status"].endswith(("EXEMPLAR_ONLY", "FORMAL_COPY_DEFAULT")) for r in groups), "all_groups_have_bounded_source_status", checks)
    checked(all(0.18 <= float(r["meaning_confidence"]) <= 0.40 for r in groups), "all_group_confidences_bounded", checks)
    checked(all(r["strongest_astronomical_calendar_or_formal_rival"].strip() for r in groups), "all_groups_have_astronomical_calendar_or_formal_rival", checks)
    checked(all(r["strongest_contradiction"].strip() for r in groups), "all_groups_have_contradiction", checks)
    checked(all(r["unsupported_labels"].strip() for r in groups), "all_groups_have_unsupported_label_audit", checks)
    checked(all(r["orientation_status"] == EXPECTED_ORIENTATION for r in groups + loci), "no_group_or_locus_has_start_rotation_or_direction", checks)
    checked(all(r["f68_f69_mapping"] == "NONE__NO_VISIBLE_KEY" for r in groups + loci), "no_f68_f69_mapping_in_groups_or_loci", checks)
    checked(all(r["prose_card_import"] == "NONE" for r in groups), "no_prose_card_import_in_groups", checks)
    checked(all(r["semantic_ceiling"] == "LOCAL_COPIED_EXEMPLAR_LABEL_NOT_WORD_SOUND_CARD_STEM_POS_OR_TRANSLATION" for r in groups), "group_semantic_ceiling_exact", checks)

    f67 = [r for r in loci if r["page"] == "f67r2"]
    checked(sum(r["local_namespace"] == "A1_RIGHT_WHEEL_ONLY" for r in f67) == 23, "f67_right_wheel_has_23_local_loci", checks)
    checked(sum(r["local_namespace"] == "A1_LEFT_WHEEL_ONLY" for r in f67) == 50, "f67_left_wheel_has_50_local_loci", checks)
    checked(sum(r["local_namespace"] == "A1_OWNER_UNRESOLVED_NO_JOIN" for r in f67) == 1, "f67_one_unresolved_legend_no_join", checks)

    f68 = [r for r in loci if r["page"] == "f68r1"]
    checked(sum(r["local_content_class"] == "LOCAL_STAR_OR_ASTERISM_STATION" for r in f68) == 28, "f68_has_28_editorial_star_addresses", checks)
    checked(all("weder eine bewiesene Folge noch ein gemeinsames Rad" in r["complete_copied_local_meaning_or_label"] for r in f68 if r["local_content_class"] == "LOCAL_STAR_OR_ASTERISM_STATION"), "f68_28_not_promoted_to_one_cycle", checks)
    checked(sum(r["owner_status"] == "UNRESOLVED" for r in f68) == 6, "f68_six_unresolved_loci_retained", checks)

    f69 = [r for r in loci if r["page"] == "f69v"]
    f69_slots = [r for r in f69 if r["local_content_class"] == "LEFT_WHEEL_LOCAL_28_PLACE_INVENTORY_ENTRY"]
    checked([r["locus"] for r in f69_slots] == [f"f69v.{i}" for i in range(4, 32)], "f69_local_28_slots_exactly_left_loci_4_31", checks)
    checked(all(r["local_namespace"] == "A3_LEFT_WHEEL_ONLY" for r in f69_slots), "f69_28_inventory_confined_to_left_wheel", checks)
    checked({r["local_namespace"] for r in f69[:3]} == {"A3_LEFT_WHEEL_ONLY", "A3_MIDDLE_WHEEL_ONLY", "A3_RIGHT_WHEEL_ONLY"}, "f69_three_ring_texts_have_separate_namespaces", checks)

    instrument_alignment = True
    all_locus_mentions: list[str] = []
    for row in instruments:
        page_loci = by_page_loci[row["page"]]
        found = re.findall(r"\[(f(?:67r2|68r1|69v)\.\d+) \|", row["continuous_instrument_description"])
        all_locus_mentions.extend(found)
        if found != [r["locus"] for r in page_loci]:
            instrument_alignment = False
        if row["locus_count"] != str(PAGE_LOCUS_COUNTS[row["page"]]) or row["group_count"] != str(PAGE_GROUP_COUNTS[row["page"]]):
            instrument_alignment = False
        if row["orientation_status"] != "NO_COMMON_START_ROTATION_OR_DIRECTION":
            instrument_alignment = False
        if row["crosspage_mapping"] != "NONE__F68_F69_KEY_ABSENT" or row["prose_card_import"] != "NONE":
            instrument_alignment = False
    checked(instrument_alignment, "three_continuous_instruments_cover_all_loci_once_in_order", checks)
    checked(len(all_locus_mentions) == 142 and len(set(all_locus_mentions)) == 142, "continuous_descriptions_cover_142_unique_loci", checks)

    source_exact = True
    for row in sources:
        source = source_historical[row["source_id"]]
        if any(row[k] != source[k] for k in ("date", "institution_item", "comparator", "supports", "limits", "url")):
            source_exact = False
        if row["permitted_target_scope"] != "GENRE_OR_LOCAL_COUNT_COMPARATOR_ONLY__NEVER_STRING_OR_LABEL_IDENTITY":
            source_exact = False
    checked(source_exact and set(r["source_id"] for r in sources) == set(source_historical), "historical_source_audit_exact_and_scope_bounded", checks)
    checked(next(r for r in sources if r["source_id"] == "S5")["v75_applicability"] == "LOCAL_28_COMPARATOR_FOR_F69_LEFT_ONLY", "picatrix_28_comparator_confined_to_f69_left", checks)
    checked(next(r for r in sources if r["source_id"] == "S7")["v75_applicability"] == "THIRTY_DAY_COUNTEREXAMPLE", "thirty_day_lunarium_retained_as_counterexample", checks)

    checked(all(r["used_to_assign_content"] == "NO" for r in orientations), "orientation_alternatives_never_assign_content", checks)
    selected_guards = {r["orientation_or_mapping_alternative"] for r in orientations if r["status"].startswith("SELECTED")}
    checked(selected_guards == {"INDEPENDENT_LOCAL_NAMESPACES", "INDEPENDENT_PANELS_NO_COMMON_ORDER", "NO_DIRECT_INDEX_OR_LOOKUP_KEY"}, "only_negative_visual_orientation_guards_selected", checks)
    checked({r["component"] for r in orientations}.issuperset({"A1_RIGHT_WHEEL", "A1_LEFT_WHEEL", "A2_MULTIPANEL", "A3_LEFT_28_WHEEL", "A3_MIDDLE_WHEEL", "A3_RIGHT_WHEEL", "A2_TO_A3"}), "all_required_orientation_components_audited", checks)

    label_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        for label in row["unsupported_labels"].split("|"):
            label_members[label].append(row)
    unsupported_by_id = {r["unsupported_label_or_relation"]: r for r in unsupported}
    checked(set(unsupported_by_id) == set(label_members), "unsupported_label_inventory_complete", checks)
    unsupported_exact = True
    for label, members in label_members.items():
        row = unsupported_by_id[label]
        if row["group_count"] != str(len(members)):
            unsupported_exact = False
        if row["locus_count"] != str(len({m['locus'] for m in members})):
            unsupported_exact = False
        if row["pages"] != "|".join(ordered_unique([m["page"] for m in members])):
            unsupported_exact = False
        if row["loci"] != "|".join(ordered_unique([m["locus"] for m in members])):
            unsupported_exact = False
        if not row["rationale"].strip():
            unsupported_exact = False
    checked(unsupported_exact, "unsupported_label_bindings_counts_and_rationales_exact", checks)
    checked("A3_INTERWHEEL_RELATION" in unsupported_by_id and "F68_F69_DIRECT_KEY" in unsupported_by_id, "interwheel_and_crosspage_relations_explicitly_unsupported", checks)

    semantic_text = "\n".join(
        [r["copied_local_meaning_or_label"] for r in groups]
        + [r["complete_copied_local_meaning_or_label"] for r in loci]
        + [r["compact_historical_working_reading"] + " " + r["continuous_instrument_description"] for r in instruments]
    )
    checked("{number" not in semantic_text, "no_unexpanded_builder_placeholders", checks)
    checked(not re.search(r"\b(Widder|Stier|Zwillinge|Krebs|Löwe|Jungfrau|Waage|Skorpion|Schütze|Steinbock|Wassermann|Fische|Alnat|Albatain|Arexe|Januar)\b", semantic_text, re.I), "no_exact_external_sign_mansion_or_month_labels", checks)
    checked(not re.search(r"\b(PAGE_HOST|EVA|Lautwert|Stammwert|Morphem|Prefix|Suffix)\b", semantic_text, re.I), "no_spelling_sound_stem_or_component_inference", checks)
    checked(not any(r["page"].casefold().startswith("f84") for r in groups), "f84_and_f84r_absent", checks)

    checked(all(f"### {page} —" in report for page in ("f67r2", "f68r1", "f69v")), "report_contains_three_full_instrument_descriptions", checks)
    checked(all(f"| {sid} |" in report for sid in source_historical), "report_contains_all_historical_sources", checks)
    checked("keinen gemeinsamen Start" in report and "keinen f68↔f69-Schlüssel" in report, "report_states_orientation_and_crosspage_guards", checks)
    checked("keine Entzifferung" in report and "f84 und f84r blieben versiegelt" in report, "report_states_interpretation_ceiling_and_seal", checks)

    artifacts = [GROUPS, LOCI, INSTRUMENTS, SOURCES, ORIENTATIONS, UNSUPPORTED, REPORT, BUILDER, Path(__file__)]
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "groups": len(groups),
            "loci": len(loci),
            "instruments": len(instruments),
            "historical_sources": len(sources),
            "orientation_alternatives": len(orientations),
            "unsupported_label_classes": len(unsupported),
            "page_group_counts": dict(Counter(r["page"] for r in groups)),
            "page_locus_counts": dict(Counter(r["page"] for r in loci)),
            "owner_status_distribution": dict(sorted(Counter(r["owner_status"] for r in loci).items())),
            "f68_editorial_star_addresses": len([r for r in f68 if r["local_content_class"] == "LOCAL_STAR_OR_ASTERISM_STATION"]),
            "f69_left_local_28_slots": len(f69_slots),
        },
        "hard_guards": {
            "common_start": False,
            "common_rotation": False,
            "common_direction": False,
            "f68_f69_key": False,
            "prose_card_import": False,
            "surface_spelling_mapping": False,
        },
        "sealed": {"f84": True, "f84r": True},
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
