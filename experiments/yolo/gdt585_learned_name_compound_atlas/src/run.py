#!/usr/bin/env python3
"""Build GDT585: concrete learned-name and compound working atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas"
OUT = BASE / "artifacts"
G459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (  # noqa: E402
    COMPOUND_OVERRIDES,
    FAMILY_RECONCILIATIONS,
    HISTORICAL_SOURCES,
    LOCAL_X_TYPES,
    fixed_type_default,
    serializable_model,
    star_type_default,
)


INPUTS = {
    "address_interlinear": G459 / "gdt459_183_address_interlinear.tsv",
    "event_triptych": G474 / "gdt474_183_event_meaning_triptych.tsv",
    "tie_decisions": G476 / "gdt476_64_tie_context_decisions.tsv",
    "name_slots": G581 / "gdt581_107_name_core_slots.tsv",
    "name_types": G582 / "gdt582_80_learned_name_defaults.tsv",
    "content_slots": G582 / "gdt582_13702_content_slot_defaults.tsv",
    "concrete_statements": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "polished_statements": G584 / "gdt584_591_polished_statement_edition.tsv",
}

OUTPUTS = {
    "types": OUT / "gdt585_80_reconciled_name_types.tsv",
    "slots": OUT / "gdt585_109_owner_content_slot_assignments.tsv",
    "labels": OUT / "gdt585_89_concrete_name_label_edition.tsv",
    "compounds": OUT / "gdt585_19_compound_and_pair_readings.tsv",
    "families": OUT / "gdt585_5_compositional_family_leads.tsv",
    "local_x": OUT / "gdt585_2_local_x_contexts.tsv",
    "history": OUT / "gdt585_10_historical_analogy_cards.tsv",
    "images": OUT / "gdt585_4_manual_image_cards.tsv",
}

BOOK = OUT / "GDT585_CONCRETE_NAME_BOOK.md"
MANUAL_AUDIT = OUT / "GDT585_MANUAL_NAME_AUDIT.md"
RESULT = OUT / "gdt585_result.json"

STATUS = (
    "PASS_80_CLASS_CORE_TYPES__109_OWNER_CONTENT_SLOTS__89_NAME_LABELS__"
    "18_CANONICAL_GROUPS_PLUS_1_VISUAL_CONTEXT_PAIR"
)


DRUG_CONTAINER_EVENTS = {
    "P1003-E0413",
    "P1003-E0458",
    "P1003-E0554",
    "P1008-E1175",
    "P1008-E1179",
    "P1008-E1228",
}
DRUG_BOUNDARY_EVENTS = {"P1008-E1301", "P1008-E1409"}


IMAGE_CARDS: tuple[dict[str, str], ...] = (
    {
        "image_card_id": "GDT585-I01",
        "physical_pages": "f17r",
        "content_focus": "PICTURED_PLANT",
        "image_object_id": "1006106",
        "image_url": "https://collections.library.yale.edu/iiif/2/1006106/full/2000,/0/default.jpg",
        "review_image_sha256": "eccb822a72a8c27045aefa4f19d558dba29ef046c1d8e3772c715a99ee7113b9",
        "manual_observation_de": (
            "Eine Wurzel, ein Stängel und eine Pflanze; OIIL liegt beim linken, "
            "OT+EEEON beim rechten Seitenblütenkopf."
        ),
        "consequence_de": "Zwei Blütenformen derselben Pflanze; Namens- oder Synonympaar bleibt Rivale.",
        "excluded_inference_de": "keine zweite unsichtbare Pflanze und keine sichere Artbestimmung",
    },
    {
        "image_card_id": "GDT585-I02",
        "physical_pages": "f71v|f72r",
        "content_focus": "STAR_BEARING_RING_VALUES",
        "image_object_id": "1006203",
        "image_url": "https://collections.library.yale.edu/iiif/2/1006203/full/3000,/0/default.jpg",
        "review_image_sha256": "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93",
        "manual_observation_de": (
            "Sterntragende Figuren stehen an Ringpositionen; 60 Slots bilden 52 Figurenlabels, "
            "acht davon mit zwei gelernten Kernen."
        ),
        "consequence_de": "Kerne sind Ring-, Kalender-, Figuren- oder Attributwerte; Position kommt aus Panel und Locus.",
        "excluded_inference_de": "keine erfundene Serienposition und kein bestimmter Sternname",
    },
    {
        "image_card_id": "GDT585-I03",
        "physical_pages": "f77r",
        "content_focus": "BATH_OR_OUTLET_ITINERARY",
        "image_object_id": "1006212",
        "image_url": "https://collections.library.yale.edu/iiif/2/1006212/full/2000,/0/default.jpg",
        "review_image_sha256": "6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df",
        "manual_observation_de": (
            "D wiederholt sich an den zwei menschlichen Endfiguren; KCHS, ORK und SOR "
            "liegen an inneren Anschluss-, Tropf- oder Sprühköpfen."
        ),
        "consequence_de": "Links-rechts-Itinerar aus Endfiguren, Anschlüssen und Auslassköpfen.",
        "excluded_inference_de": "kein sichtbarer Wärme-, Kälte-, Sitz- oder Beckenbeweis für alte Aliasse",
    },
    {
        "image_card_id": "GDT585-I04",
        "physical_pages": "f88v|f89r",
        "content_focus": "APOTHECARY_NAME_DECK",
        "image_object_id": "1006233",
        "image_url": "https://collections.library.yale.edu/iiif/2/1006233/full/3000,/0/default.jpg",
        "review_image_sha256": "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c",
        "manual_observation_de": (
            "Von 38 Drogenslots liegen 29 an klaren Pflanzenfragmenten, sieben an sechs "
            "Gefäßlabels und zwei in einem zweizeiligen Grenzlabel."
        ),
        "consequence_de": "Pflanzenorgane werden Primärdefaults; alte Stoffaliase bleiben Rivalen.",
        "excluded_inference_de": "keine sichere Art- oder Gefäßinhaltsbestimmung allein aus dem Bild",
    },
)


STAR_SERIES: dict[str, set[str]] = {
    "CH_SERIES": {"chf", "chody", "chdaiird", "cho", "ch", "chdamy", "chos"},
    "OP_SERIES": {"op", "opoiiin", "opo"},
    "E_SERIES": {"ef", "e", "ee", "eeeo", "oeeo", "oeees", "eees", "eor", "et"},
    "Y_SERIES": {"yt", "y", "yd", "yp", "yk", "yf", "yto"},
    "AI_SERIES": {"ain", "aiin", "aiir"},
    "DY_SERIES": {"chody", "ody", "dy", "odady"},
}


COMPOSITIONAL_ATOMS = {"d", "y", "s", "sy", "oiin", "e", "yt", "em", "da", "am"}
FORMAL_FAMILIES = {"OTORA_ROOT_FAMILY", "CHEO_FIBRE_ROOT_FAMILY", "CHOS_CHOR_FIBRE_ROOT_FAMILY"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty table: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipe(values: list[str]) -> str:
    return "|".join(values) if values else "NONE"


def star_series(raw_core: str) -> str:
    return pipe([series for series, members in STAR_SERIES.items() if raw_core in members])


def final_model(event: dict[str, str], ties: dict[str, dict[str, str]]) -> tuple[str, str]:
    tie = ties.get(event["bundle_id"])
    if tie:
        return tie["context_selected_model"], tie["model_changed_from_gdt474"]
    return event["bundle_selected_model"], "NO"


def model_reading(event: dict[str, str], model: str) -> str:
    return event[
        {
            "COORDINATE": "coordinate_event_reading_de",
            "INSTRUCTION": "instruction_event_reading_de",
            "CATALOGUE": "catalogue_event_reading_de",
        }[model]
    ]


def inject_defaults(reading: str, rows: list[dict[str, Any]]) -> str:
    result = reading
    replacements = {
        str(row["raw_name_core"]): str(row["gdt585_primary_default_de"])
        for row in rows
    }
    for raw_core in sorted(replacements, key=lambda value: (-len(value), value)):
        needle = f"»{raw_core}«"
        replacement = f"»{replacements[raw_core]} [{raw_core}]«"
        if needle not in result:
            raise RuntimeError(f"Name core missing from selected reading: {needle} in {reading}")
        result = result.replace(needle, replacement)
    return result


def drug_visual_context(event_id: str) -> str:
    if event_id in DRUG_CONTAINER_EVENTS:
        return "APOTHECARY_CONTAINER_LABEL"
    if event_id in DRUG_BOUNDARY_EVENTS:
        return "TWO_LINE_CONTAINER_PLANT_BOUNDARY_LABEL"
    return "PICTURED_PLANT_FRAGMENT_LABEL"


def segmentation_status(content_class: str, raw_core: str, semantic_family: str) -> str:
    if content_class == "STAR_BEARING_RING_POSITION":
        return "OPAQUE_LEARNED_OR_REUSABLE_VALUE"
    if content_class in {"BATH_OR_OUTLET_STATION", "PICTURED_PLANT"}:
        return "OPAQUE_WHOLE_CORE"
    if semantic_family in FORMAL_FAMILIES:
        return "FAMILY_RELATED_WHOLE_CORE__NO_AUTOMATIC_SUBSTRING_PARSE"
    if raw_core in COMPOSITIONAL_ATOMS:
        return "OCCURRENCE_LEVEL_COMPOSITION_ATOM__STRING_PARSE_NOT_PORTABLE"
    return "OPAQUE_WHOLE_CORE"


def occurrence_role(source: dict[str, str], label_rows: list[dict[str, str]]) -> str:
    content_class = source["content_class"]
    raw_cores = [row["raw_name_core"] for row in label_rows]
    slot_index = int(source["name_slot_in_label"])
    if content_class == "STAR_BEARING_RING_POSITION":
        if len(label_rows) == 1:
            return "PRIMARY_RECORD_VALUE"
        if len(set(raw_cores)) == 1:
            return "DUPLICATE_SAME_RING_VALUE"
        return "PRIMARY_RECORD_VALUE" if slot_index == 1 else "CARRIED_FIGURE_OR_ATTRIBUTE_VALUE"
    package_roles: dict[str, tuple[str, ...]] = {
        "P1003-E0081": ("COMMON_LEFT_END_FIGURE", "LEFT_SOURCE_CONNECTION"),
        "P1003-E0088": ("COMMON_RIGHT_END_FIGURE", "RIGHT_END_CONNECTION"),
        "P1003-E0554": ("ROOT_PART", "PREPARATION_BASE"),
        "P1003-E0555": ("REPEATED_PLANT_REFERENCE", "REPEATED_PLANT_REFERENCE"),
        "P1003-E0557": ("ROOT_PART", "PLANT_TAXON"),
        "P1008-E1176": ("LEAF_OR_HERB_PART", "ROOT_PART"),
        "P1008-E1177": ("INFLORESCENCE_PART", "HERB_OR_PLANT_FORM"),
        "P1008-E1182": ("LEAF_PART", "RHIZOME_PART", "PLANT_TAXON"),
        "P1008-E1412": ("LEAF_PART", "PLANT_TAXON"),
    }
    roles = package_roles.get(source["source_event_id"])
    return roles[slot_index - 1] if roles else "SINGLE_LEARNED_VALUE"


def type_disposition(content_class: str, raw_core: str) -> str:
    if content_class == "STAR_BEARING_RING_POSITION":
        return "SERIAL_POSITION_REPLACED_BY_RING_VALUE_ROLE"
    if content_class == "PICTURED_PLANT":
        return "ONE_PLANT_TWO_FLOWER_FORMS__NAME_PAIR_RETAINED_AS_RIVAL"
    if content_class == "BATH_OR_OUTLET_STATION":
        return "VISUAL_ITINERARY_REPLACED_UNSEEN_STATION_PROPERTY"
    if raw_core in {"yd", "od", "yko", "yor"}:
        return "CONTAINER_OR_BOUNDARY_ALIAS_CONTEXTUALIZED"
    return "PLANT_IMAGE_OR_COMPOSITION_PROMOTED__LEGACY_ALIAS_RETAINED_AS_RIVAL"


def build_type_rows(
    names: list[dict[str, str]], old_types: list[dict[str, str]]
) -> list[dict[str, Any]]:
    names_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in names:
        names_by_key[(row["content_class"], row["raw_name_core"])].append(row)
    output: list[dict[str, Any]] = []
    for old in old_types:
        key = (old["content_class"], old["raw_name_core"])
        occurrences = names_by_key[key]
        if not occurrences:
            raise RuntimeError(f"Uninstantiated learned-name type: {key}")
        first_count = sum(row["name_slot_in_label"] == "1" for row in occurrences)
        later_count = len(occurrences) - first_count
        if old["content_class"] == "STAR_BEARING_RING_POSITION":
            model = star_type_default(old["raw_name_core"], len(occurrences), first_count, later_count)
            series = star_series(old["raw_name_core"])
        else:
            model = fixed_type_default(old["content_class"], old["raw_name_core"])
            series = model["semantic_family"]
            if model["legacy_house_alias_de"] != old["provisional_default_de"]:
                raise RuntimeError(f"Legacy alias drift for {key}")
        output.append(
            {
                "type_ordinal": len(output) + 1,
                "gdt582_name_default_id": old["name_default_id"],
                "class_core_key": f"{old['content_class']}::{old['raw_name_core']}",
                "content_class": old["content_class"],
                "raw_name_core": old["raw_name_core"],
                "occurrence_count": len(occurrences),
                "source_occurrence_count": old["occurrence_count"],
                "first_slot_count": first_count,
                "later_slot_count": later_count,
                "label_count": len({row["source_event_id"] for row in occurrences}),
                "physical_pages": pipe(sorted({row["physical_page"] for row in occurrences})),
                "surfaces": pipe(sorted({row["surface"] for row in occurrences})),
                "gdt582_provisional_default_de": old["provisional_default_de"],
                "gdt585_primary_default_de": model["default_de"],
                "semantic_family": model["semantic_family"],
                "name_role": model["name_role"],
                "segmentation_status": segmentation_status(
                    old["content_class"], old["raw_name_core"], model["semantic_family"]
                ),
                "composition_atom_de": model["composition_atom_de"],
                "substance_head_de": model["substance_head_de"],
                "plant_part_de": model["plant_part_de"],
                "series_tags": series,
                "legacy_house_alias_de": model["legacy_house_alias_de"],
                "strongest_rival_de": model["strongest_rival_de"],
                "working_basis": model["working_basis"],
                "disposition": type_disposition(old["content_class"], old["raw_name_core"]),
                "guard": "CLASS_IS_PART_OF_KEY__NO_AUTOMATIC_SUBSTRING_PARSE__RIVAL_VISIBLE",
            }
        )
    return output


def build_name_assignments(
    names: list[dict[str, str]], type_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    types = {(row["content_class"], row["raw_name_core"]): row for row in type_rows}
    labels: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in names:
        labels[source["source_event_id"]].append(source)
    for rows in labels.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))
    output: list[dict[str, Any]] = []
    for source in sorted(names, key=lambda row: int(row["name_slot_ordinal"])):
        model = types[(source["content_class"], source["raw_name_core"])]
        visual = {
            "STAR_BEARING_RING_POSITION": "STAR_BEARING_FIGURE_LABEL",
            "BATH_OR_OUTLET_STATION": "BATH_ITINERARY_LABEL",
            "PICTURED_PLANT": "ONE_PICTURED_PLANT_LABEL",
        }.get(source["content_class"])
        if source["content_class"] == "DRUG_OR_INGREDIENT_OBJECT":
            visual = drug_visual_context(source["source_event_id"])
        output.append(
            {
                "assignment_ordinal": len(output) + 1,
                "source_kind": "GDT581_NAME_SPAN",
                "slot_id": source["slot_id"],
                "source_event_or_card_id": source["source_event_id"],
                "statement_or_record_id": source["local_card_host_key"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "locus": source["locus"],
                "owner_de": source["owner_de"],
                "surface": source["surface"],
                "surface_template": source["surface_template"],
                "name_slot_in_label": source["name_slot_in_label"],
                "raw_name_core": source["raw_name_core"],
                "content_class": source["content_class"],
                "class_core_key": model["class_core_key"],
                "type_default_id": model["gdt582_name_default_id"],
                "label_slot_count": len(labels[source["source_event_id"]]),
                "occurrence_role": occurrence_role(source, labels[source["source_event_id"]]),
                "visual_object_context": visual or "NONE",
                "semantic_family": model["semantic_family"],
                "name_role": model["name_role"],
                "segmentation_status": model["segmentation_status"],
                "gdt585_primary_default_de": model["gdt585_primary_default_de"],
                "composition_atom_de": model["composition_atom_de"],
                "gdt582_legacy_house_alias_de": model["legacy_house_alias_de"],
                "strongest_rival_de": model["strongest_rival_de"],
                "working_basis": model["working_basis"],
                "primary_governor_key": source["primary_governor_key"],
                "guard": "EXACT_GDT581_SPAN__ONE_PRIMARY_DEFAULT__TECHNICAL_SHELL_FIXED",
            }
        )
    return output


def build_local_x_rows(
    content: list[dict[str, str]],
    g582_statements: list[dict[str, str]],
    g584_statements: list[dict[str, str]],
) -> list[dict[str, Any]]:
    content_by_id = {row["slot_id"]: row for row in content}
    statements_582 = {row["statement_id"]: row for row in g582_statements}
    statements_584 = {row["statement_id"]: row for row in g584_statements}
    output: list[dict[str, Any]] = []
    for ordinal, (slot_id, model) in enumerate(LOCAL_X_TYPES.items(), 1):
        source = content_by_id[slot_id]
        statement_id = source["statement_or_record_id"]
        if statement_id in statements_584:
            context_source = "GDT584_POLISHED_STATEMENT"
            old_context = statements_584[statement_id]["gdt584_polished_paragraph_de"]
        else:
            context_source = "GDT582_CONCRETE_STATEMENT"
            old_context = statements_582[statement_id]["concrete_working_reading_de"]
        old_alias = source["gdt582_concrete_default_de"]
        if old_alias not in old_context:
            raise RuntimeError(f"LOCAL_X alias absent from statement: {slot_id}")
        output.append(
            {
                "local_x_ordinal": ordinal,
                "slot_id": slot_id,
                "source_event_id": source["source_event_or_card_id"],
                "statement_id": statement_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner": source["owner"],
                "surface": source["surface"],
                "class_core_key": f"OWNER_BOUND_LOCAL_X::{source['owner']}",
                "semantic_family": model["semantic_family"],
                "name_role": model["name_role"],
                "gdt582_legacy_house_alias_de": model["legacy_house_alias_de"],
                "gdt585_primary_default_de": model["default_de"],
                "composition_atom_de": model["composition_atom_de"],
                "strongest_rival_de": model["strongest_rival_de"],
                "working_basis": model["working_basis"],
                "context_source": context_source,
                "source_context_de": old_context,
                "gdt585_context_de": old_context.replace(old_alias, model["default_de"]),
                "guard": "OWNER_BOUND__X_NOT_PORTABLE_BETWEEN_TEXT_BLOCKS",
            }
        )
    return output


def append_local_x_assignments(
    assignments: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
    content: list[dict[str, str]],
) -> None:
    content_by_id = {row["slot_id"]: row for row in content}
    for local in local_rows:
        source = content_by_id[str(local["slot_id"])]
        assignments.append(
            {
                "assignment_ordinal": len(assignments) + 1,
                "source_kind": "GDT582_OWNER_BOUND_LOCAL_X",
                "slot_id": source["slot_id"],
                "source_event_or_card_id": source["source_event_or_card_id"],
                "statement_or_record_id": source["statement_or_record_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "locus": source["locus"],
                "owner_de": source["owner"],
                "surface": source["surface"],
                "surface_template": "OWNER_LOCAL_X",
                "name_slot_in_label": source["slot_position"],
                "raw_name_core": "LOCAL_X",
                "content_class": "OWNER_BOUND_LOCAL_X",
                "class_core_key": local["class_core_key"],
                "type_default_id": f"GDT585-X{int(local['local_x_ordinal']):02d}",
                "label_slot_count": 1,
                "occurrence_role": local["name_role"],
                "visual_object_context": "TEXT_OWNER_CONTEXT",
                "semantic_family": local["semantic_family"],
                "name_role": local["name_role"],
                "segmentation_status": "OWNER_BOUND_WHOLE_CORE",
                "gdt585_primary_default_de": local["gdt585_primary_default_de"],
                "composition_atom_de": local["composition_atom_de"],
                "gdt582_legacy_house_alias_de": local["gdt582_legacy_house_alias_de"],
                "strongest_rival_de": local["strongest_rival_de"],
                "working_basis": local["working_basis"],
                "primary_governor_key": source["primary_governor_key"],
                "guard": "EXACT_GDT582_LOCAL_X_SLOT__OWNER_KEY_IS_PART_OF_IDENTITY",
            }
        )


def grammar_aware_for_event(
    event_id: str,
    assignment_by_event: dict[str, list[dict[str, Any]]],
    events: dict[str, dict[str, str]],
    ties: dict[str, dict[str, str]],
) -> tuple[str, str, str, str]:
    event = events[event_id]
    model, changed = final_model(event, ties)
    source_reading = model_reading(event, model)
    concrete = inject_defaults(source_reading, assignment_by_event[event_id])
    return model, changed, source_reading, concrete


def build_compound_rows(
    names: list[dict[str, str]],
    assignments: list[dict[str, Any]],
    events: dict[str, dict[str, str]],
    ties: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    source_names: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in names:
        source_names[row["source_event_id"]].append(row)
    for rows in source_names.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))
    assignment_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assignments:
        if row["source_kind"] == "GDT581_NAME_SPAN":
            assignment_by_event[str(row["source_event_or_card_id"])].append(row)
    for rows in assignment_by_event.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))

    provisional: list[dict[str, Any]] = []

    plant_event_ids = ["P1003-E0080", "P1003-E0079"]
    plant_assigned = [assignment_by_event[event_id][0] for event_id in plant_event_ids]
    plant_models: list[str] = []
    plant_grammar: list[str] = []
    for event_id in plant_event_ids:
        model, _, _, grammar = grammar_aware_for_event(
            event_id, assignment_by_event, events, ties
        )
        plant_models.append(model)
        plant_grammar.append(grammar)
    plant_override = COMPOUND_OVERRIDES["G474-B001"]
    provisional.append(
        {
            "case_scope": "CANONICAL_MULTI_OR_SAME_OBJECT_GROUP",
            "source_kind": plant_override["source_kind"],
            "source_event_ids": pipe(plant_event_ids),
            "bundle_id": "G474-B001",
            "physical_page": "f17r",
            "register": "HERBAL",
            "locus": "f17r.13",
            "surface_sequence": "oiil|oteeeon",
            "surface_templates": "<NAME>|OT+<NAME>",
            "raw_core_sequence": "oiil|eeeon",
            "primary_default_sequence": pipe(
                [str(row["gdt585_primary_default_de"]) for row in plant_assigned]
            ),
            "selected_models": pipe(plant_models),
            "grammar_primary_reading_de": " ".join(plant_grammar),
            "semantic_mode": plant_override["semantic_mode"],
            "composition_hypothesis_de": plant_override["primary_reading_de"],
            "strongest_rival_de": plant_override["strongest_rival_de"],
            "reason_de": plant_override["reason_de"],
        }
    )

    multi_events = sorted(
        (event_id for event_id, rows in source_names.items() if len(rows) > 1),
        key=lambda event_id: min(
            int(row["name_slot_ordinal"]) for row in source_names[event_id]
        ),
    )
    for event_id in multi_events:
        source = source_names[event_id]
        assigned = assignment_by_event[event_id]
        event = events[event_id]
        model, _, _, grammar = grammar_aware_for_event(
            event_id, assignment_by_event, events, ties
        )
        override = COMPOUND_OVERRIDES.get(event_id)
        if override:
            semantic_mode = override["semantic_mode"]
            hypothesis = override["primary_reading_de"]
            rival = override["strongest_rival_de"]
            reason = override["reason_de"]
            source_kind = override["source_kind"]
        else:
            raw_cores = [row["raw_name_core"] for row in source]
            defaults = [str(row["gdt585_primary_default_de"]) for row in assigned]
            source_kind = "MULTI_NAME_LABEL"
            if len(set(raw_cores)) == 1:
                semantic_mode = "ONE_FIGURE_REPEATED_RING_VALUE"
                hypothesis = (
                    f"Eine Ringfigur trägt denselben Wert {defaults[0]} zweimal in "
                    "technisch getrennten Rollen."
                )
            else:
                semantic_mode = "ONE_FIGURE_PRIMARY_AND_CARRIED_VALUE"
                hypothesis = (
                    f"Eine Ringfigur koppelt den Primärwert {defaults[0]} mit dem "
                    f"getragenen oder attributiven Wert {defaults[1]}."
                )
            rival = "zwei selbständige geordnete Stern- oder Kalendereinträge"
            reason = (
                "Beide Kerne stehen im selben sichtbaren Figurenlabel; die technische Hülle "
                "zwischen ihnen bleibt in der Primärlesung erhalten."
            )
        provisional.append(
            {
                "case_scope": "CANONICAL_MULTI_OR_SAME_OBJECT_GROUP",
                "source_kind": source_kind,
                "source_event_ids": event_id,
                "bundle_id": event["bundle_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "locus": event["locus"],
                "surface_sequence": event["surface"],
                "surface_templates": source[0]["surface_template"],
                "raw_core_sequence": pipe([row["raw_name_core"] for row in source]),
                "primary_default_sequence": pipe(
                    [str(row["gdt585_primary_default_de"]) for row in assigned]
                ),
                "selected_models": model,
                "grammar_primary_reading_de": grammar,
                "semantic_mode": semantic_mode,
                "composition_hypothesis_de": hypothesis,
                "strongest_rival_de": rival,
                "reason_de": reason,
            }
        )

    context_key = "GDT585-CONTEXT-F89R-DCHOS-YOR"
    context_override = COMPOUND_OVERRIDES[context_key]
    context_ids = ["P1008-E1301", "P1008-E1409"]
    context_assigned = [assignment_by_event[event_id][0] for event_id in context_ids]
    context_models: list[str] = []
    context_grammar: list[str] = []
    for event_id in context_ids:
        model, _, _, grammar = grammar_aware_for_event(
            event_id, assignment_by_event, events, ties
        )
        context_models.append(model)
        context_grammar.append(grammar)
    provisional.append(
        {
            "case_scope": "EXTENDED_TWO_LINE_VISUAL_CONTEXT_PAIR",
            "source_kind": context_override["source_kind"],
            "source_event_ids": pipe(context_ids),
            "bundle_id": context_key,
            "physical_page": "f89r",
            "register": "PHARMA",
            "locus": "f89r2.21|f89r2.30",
            "surface_sequence": "okshdchos|yorain",
            "surface_templates": "OK+SH+<NAME>|<NAME>+AIIN",
            "raw_core_sequence": "dchos|yor",
            "primary_default_sequence": pipe(
                [str(row["gdt585_primary_default_de"]) for row in context_assigned]
            ),
            "selected_models": pipe(context_models),
            "grammar_primary_reading_de": " ".join(context_grammar),
            "semantic_mode": context_override["semantic_mode"],
            "composition_hypothesis_de": context_override["primary_reading_de"],
            "strongest_rival_de": context_override["strongest_rival_de"],
            "reason_de": context_override["reason_de"],
        }
    )

    output: list[dict[str, Any]] = []
    for ordinal, row in enumerate(provisional, 1):
        output.append(
            {
                "compound_ordinal": ordinal,
                "compound_id": f"GDT585-C{ordinal:03d}",
                **row,
                "guard": "GRAMMAR_PRIMARY__COMPOSITION_HYPOTHESIS_SEPARATE__SHELL_FIXED",
            }
        )
    return output


def build_label_rows(
    names: list[dict[str, str]],
    assignments: list[dict[str, Any]],
    events: dict[str, dict[str, str]],
    ties: dict[str, dict[str, str]],
    compounds: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_names: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in names:
        source_names[row["source_event_id"]].append(row)
    for rows in source_names.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))
    assigned: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assignments:
        if row["source_kind"] == "GDT581_NAME_SPAN":
            assigned[str(row["source_event_or_card_id"])].append(row)
    for rows in assigned.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))
    compound_by_event: dict[str, dict[str, Any]] = {}
    for compound in compounds:
        for event_id in str(compound["source_event_ids"]).split("|"):
            compound_by_event[event_id] = compound

    ordered_events = sorted(
        source_names,
        key=lambda event_id: min(
            int(row["name_slot_ordinal"]) for row in source_names[event_id]
        ),
    )
    output: list[dict[str, Any]] = []
    for event_id in ordered_events:
        event = events[event_id]
        slots = assigned[event_id]
        model, changed, source_reading, grammar = grammar_aware_for_event(
            event_id, assigned, events, ties
        )
        compound = compound_by_event.get(event_id)
        output.append(
            {
                "label_ordinal": len(output) + 1,
                "source_event_id": event_id,
                "bundle_id": event["bundle_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "locus": event["locus"],
                "owner_de": source_names[event_id][0]["owner_de"],
                "surface": event["surface"],
                "surface_template": source_names[event_id][0]["surface_template"],
                "label_slot_count": len(slots),
                "raw_core_sequence": pipe([str(row["raw_name_core"]) for row in slots]),
                "primary_default_sequence": pipe(
                    [str(row["gdt585_primary_default_de"]) for row in slots]
                ),
                "occurrence_role_sequence": pipe(
                    [str(row["occurrence_role"]) for row in slots]
                ),
                "legacy_alias_sequence": pipe(
                    [str(row["gdt582_legacy_house_alias_de"]) for row in slots]
                ),
                "gdt474_selected_model": event["bundle_selected_model"],
                "gdt585_selected_model": model,
                "gdt476_context_changed": changed,
                "source_grammar_reading_de": source_reading,
                "gdt585_primary_reading_de": grammar,
                "compound_group_id": compound["compound_id"] if compound else "NONE",
                "interpretation_mode": (
                    compound["semantic_mode"]
                    if compound else "SINGLE_LEARNED_VALUE_IN_TECHNICAL_SHELL"
                ),
                "composition_hypothesis_de": (
                    compound["composition_hypothesis_de"] if compound else "NONE"
                ),
                "guard": "GRAMMAR_PRIMARY__EXACT_SURFACE_AND_NAME_SPANS_FIXED",
            }
        )
    return output


def build_book(
    types: list[dict[str, Any]],
    compounds: list[dict[str, Any]],
    local_x: list[dict[str, Any]],
) -> str:
    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in types:
        by_class[str(row["content_class"])].append(row)
    lines = [
        "# GDT585 — konkretes Namens- und Kompositbuch",
        "",
        "Explorative Arbeitsedition, kein wiedergewonnener Klartext.",
        "",
        "## Neue Basis",
        "",
        "Die beste aktuelle Lesung ist ein klassen- und besitzergebundener Nomenklator:",
        "technische Hülle + gelernter Kern oder Kurzcode + technische Hülle.",
        "Die Hüllen bleiben strukturell; Primärdefault, Kompositionsatom und alter Hausalias "
        "werden getrennt angezeigt.",
        "",
        "Der Bildaudit verschiebt das Pharma-Deck: 29 von 38 Slots liegen an "
        "Pflanzenfragmenten, sieben an Gefäßlabels und zwei an einem Grenzlabel. Deshalb "
        "sind Pflanzenorgane primär; Wasser, Wein, Öl und Salz bleiben sichtbare Rivalen.",
    ]
    headings = {
        "PICTURED_PLANT": "Abgebildete Pflanze",
        "STAR_BEARING_RING_POSITION": "Ring- und Figurenwerte",
        "BATH_OR_OUTLET_STATION": "Bad-, Anschluss- und Auslasswerte",
        "DRUG_OR_INGREDIENT_OBJECT": "Pflanzendrogen und Gefäßvorräte",
    }
    for content_class in (
        "PICTURED_PLANT",
        "STAR_BEARING_RING_POSITION",
        "BATH_OR_OUTLET_STATION",
        "DRUG_OR_INGREDIENT_OBJECT",
    ):
        rows = by_class[content_class]
        lines.extend(["", f"## {headings[content_class]} ({len(rows)} Typen)", ""])
        lines.append(
            "| Kern | Vorkommen | Primärdefault | Kompositionsrolle | alter Hausalias / Rivale |"
        )
        lines.append("|---|---:|---|---|---|")
        for row in rows:
            legacy = str(row["legacy_house_alias_de"])
            rival = str(row["strongest_rival_de"])
            rival_cell = rival if legacy == "NONE" else f"{legacy}; Rivale: {rival}"
            lines.append(
                f"| {row['raw_name_core']} | {row['occurrence_count']} | "
                f"{row['gdt585_primary_default_de']} | {row['composition_atom_de']} | "
                f"{rival_cell} |"
            )
    lines.extend(["", "## Komposit- und Paarlesungen", ""])
    for row in compounds:
        lines.extend(
            [
                f"### {row['compound_id']} — {row['surface_sequence']}",
                "",
                f"Grammatische Primärlesung: {row['grammar_primary_reading_de']}",
                "",
                f"Kompositionshypothese: {row['composition_hypothesis_de']}",
                "",
                f"Stärkster Rivale: {row['strongest_rival_de']}",
                "",
            ]
        )
    lines.extend(["## Ownergebundene LOCAL_X-Werte", ""])
    for row in local_x:
        lines.append(
            f"- {row['surface']} / {row['owner']}: {row['gdt585_primary_default_de']} "
            f"(Rivale: {row['strongest_rival_de']})."
        )
    lines.extend(
        [
            "",
            "## Arbeitsgrenze",
            "",
            "Jeder Slot besitzt eine Defaultbedeutung, doch Bildrolle, gelerntes Ganzwort und "
            "konkreter Stoffalias sind verschiedene Ebenen. Kürzere Zeichenfolgen innerhalb "
            "eines Ganzkerns werden nicht automatisch als portable Wortstämme behandelt.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_manual_audit(images: list[dict[str, Any]], types: list[dict[str, Any]]) -> str:
    repeated_star = [
        row for row in types
        if row["content_class"] == "STAR_BEARING_RING_POSITION"
        and int(row["occurrence_count"]) > 1
    ]
    lines = [
        "# GDT585 — manuelles Bild- und Namensaudit",
        "",
        "Nur die bereits in GDT459 zugelassenen Yale-Surrogate wurden erneut betrachtet; "
        "keine neuen Manuskriptseiten und kein OCR wurden verwendet.",
        "",
        "## Bildkarten",
    ]
    for row in images:
        lines.extend(
            [
                "",
                f"### {row['image_card_id']} — {row['physical_pages']}",
                "",
                str(row["manual_observation_de"]),
                "",
                f"Folge: {row['consequence_de']}",
                "",
                f"Nicht daraus abgeleitet: {row['excluded_inference_de']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Pharma-Census",
            "",
            "- 29 Slots an klaren Pflanzenfragmenten.",
            "- 7 Slots an 6 klaren Gefäßlabels.",
            "- 2 Slots in einem zweizeiligen Gefäß-/Pflanzengrenzlabel.",
            "",
            "Die Primärverschiebung D=Wurzel, Y=Krautdroge, S=Blattdroge und "
            "OR=helle Wurzeldroge folgt diesem Census und den Mehrkernpaketen. Die alten "
            "Wasser-/Wein-/Salz-/Öl-Aliasse bleiben im TSV vollständig sichtbar.",
            "",
            "## Ringwerte",
            "",
            f"{len(repeated_star)} wiederkehrende Kerntypen decken "
            f"{sum(int(row['occurrence_count']) for row in repeated_star)} der 60 Slots; "
            "die 33 Singletonkerne werden als gelernte Figuren- oder Sternwerte geführt. "
            "Die Position bleibt Vorkommensmetadatum.",
            "",
            "## Grammatik vor Komposition",
            "",
            "Mehrere Namensslots bleiben mehrere exakte Spannen. GDT474/476 bestimmt die "
            "Primärstimme. Organ-von-Pflanze oder Figurenwert-plus-Attribut steht als zweite, "
            "kreative Kompositionsspur daneben. AR, AL, SH, OT und andere Hüllenteile werden "
            "nicht in das Namenslexem eingeschmolzen.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def artifact_readme() -> str:
    return "\n".join(
        [
            "# GDT585 artifacts",
            "",
            "- gdt585_80_reconciled_name_types.tsv — one row per class×raw-core type.",
            "- gdt585_109_owner_content_slot_assignments.tsv — 107 name slots plus two LOCAL_X slots.",
            "- gdt585_89_concrete_name_label_edition.tsv — grammar-first readings for all name labels.",
            "- gdt585_19_compound_and_pair_readings.tsv — 18 canonical cases plus one visual context pair.",
            "- gdt585_5_compositional_family_leads.tsv — three formal families plus two composition leads.",
            "- gdt585_2_local_x_contexts.tsv — owner-bound complaint and remedy contexts.",
            "- gdt585_10_historical_analogy_cards.tsv — analogy only, never Voynich identity.",
            "- gdt585_4_manual_image_cards.tsv — admitted image hashes and manual observations.",
            "- GDT585_CONCRETE_NAME_BOOK.md — readable complete working edition.",
            "- GDT585_MANUAL_NAME_AUDIT.md — compact visual audit.",
            "- gdt585_result.json and gdt585_validation.json — compact machine checks.",
            "",
        ]
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected_inputs = {
        "address_interlinear": 183,
        "event_triptych": 183,
        "tie_decisions": 64,
        "name_slots": 107,
        "name_types": 80,
        "content_slots": 13702,
        "concrete_statements": 793,
        "polished_statements": 591,
    }
    observed_inputs = {name: len(rows) for name, rows in data.items()}
    if observed_inputs != expected_inputs:
        raise RuntimeError(f"Input count drift: {observed_inputs}")
    if any(
        row.get("physical_page", "").lower().startswith("f84")
        for rows in data.values() for row in rows
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT585")

    events = {row["source_event_id"]: row for row in data["event_triptych"]}
    ties = {row["bundle_id"]: row for row in data["tie_decisions"]}
    types = build_type_rows(data["name_slots"], data["name_types"])
    assignments = build_name_assignments(data["name_slots"], types)
    local_x = build_local_x_rows(
        data["content_slots"], data["concrete_statements"], data["polished_statements"]
    )
    append_local_x_assignments(assignments, local_x, data["content_slots"])
    compounds = build_compound_rows(data["name_slots"], assignments, events, ties)
    labels = build_label_rows(data["name_slots"], assignments, events, ties, compounds)
    families = [dict(row) for row in FAMILY_RECONCILIATIONS]
    history = [
        {
            **dict(row),
            "guard": "HISTORICAL_ANALOGY_ONLY__NO_VOYNICH_IDENTITY_OR_PLAINTEXT_SUPPORT",
        }
        for row in HISTORICAL_SOURCES
    ]
    images = [
        {
            **dict(row),
            "guard": "MANUAL_VISUAL_ROLE_ONLY__NO_SPECIES_OR_SUBSTANCE_IDENTIFICATION",
        }
        for row in IMAGE_CARDS
    ]

    counts = {
        "types": len(types),
        "slots": len(assignments),
        "labels": len(labels),
        "compounds": len(compounds),
        "families": len(families),
        "local_x": len(local_x),
        "history": len(history),
        "images": len(images),
    }
    expected_counts = {
        "types": 80,
        "slots": 109,
        "labels": 89,
        "compounds": 19,
        "families": 5,
        "local_x": 2,
        "history": 10,
        "images": 4,
    }
    if counts != expected_counts:
        raise RuntimeError(f"Output count drift: {counts}")
    canonical_count = sum(
        row["case_scope"] == "CANONICAL_MULTI_OR_SAME_OBJECT_GROUP"
        for row in compounds
    )
    if canonical_count != 18:
        raise RuntimeError(f"Canonical compound count drift: {canonical_count}")

    visual_counts = Counter(
        str(row["visual_object_context"])
        for row in assignments
        if row["content_class"] == "DRUG_OR_INGREDIENT_OBJECT"
    )
    expected_visual = Counter(
        {
            "PICTURED_PLANT_FRAGMENT_LABEL": 29,
            "APOTHECARY_CONTAINER_LABEL": 7,
            "TWO_LINE_CONTAINER_PLANT_BOUNDARY_LABEL": 2,
        }
    )
    if visual_counts != expected_visual:
        raise RuntimeError(f"Drug visual census drift: {visual_counts}")
    repeated_star = [
        row for row in types
        if row["content_class"] == "STAR_BEARING_RING_POSITION"
        and int(row["occurrence_count"]) > 1
    ]
    repeated_star_slots = sum(int(row["occurrence_count"]) for row in repeated_star)
    if len(repeated_star) != 10 or repeated_star_slots != 27:
        raise RuntimeError("Star repeat profile drift")

    write_tsv(OUTPUTS["types"], types)
    write_tsv(OUTPUTS["slots"], assignments)
    write_tsv(OUTPUTS["labels"], labels)
    write_tsv(OUTPUTS["compounds"], compounds)
    write_tsv(OUTPUTS["families"], families)
    write_tsv(OUTPUTS["local_x"], local_x)
    write_tsv(OUTPUTS["history"], history)
    write_tsv(OUTPUTS["images"], images)
    BOOK.write_text(build_book(types, compounds, local_x), encoding="utf-8")
    MANUAL_AUDIT.write_text(build_manual_audit(images, types), encoding="utf-8")
    (OUT / "README.md").write_text(artifact_readme(), encoding="utf-8")

    class_counts = Counter(str(row["content_class"]) for row in assignments)
    raw_classes: dict[str, set[str]] = defaultdict(set)
    for row in types:
        raw_classes[str(row["raw_name_core"])].add(str(row["content_class"]))
    collisions = sorted(raw for raw, class_set in raw_classes.items() if len(class_set) > 1)
    changed_context_labels = [
        row["source_event_id"] for row in labels if row["gdt476_context_changed"] == "YES"
    ]
    star_profiles = Counter(
        (
            "REPEATED" if int(row["occurrence_count"]) > 1 else "SINGLETON",
            "BOTH" if int(row["first_slot_count"]) and int(row["later_slot_count"])
            else "LATER" if int(row["later_slot_count"]) else "FIRST",
        )
        for row in types if row["content_class"] == "STAR_BEARING_RING_POSITION"
    )
    output_hash_paths = {
        **OUTPUTS,
        "book": BOOK,
        "audit": MANUAL_AUDIT,
    }
    result = {
        "experiment_id": "GDT585",
        "status": STATUS,
        "claim": (
            "Complete replaceable name atlas with fixed spans and shells, image-conditioned "
            "primary roles, explicit legacy aliases, and separate composition hypotheses."
        ),
        "claim_ceiling": (
            "Exploratory working meanings only; no recovered plaintext, species identity, "
            "substance identity, pronunciation, or portable substring lexicon."
        ),
        "counts": counts,
        "canonical_compound_count": canonical_count,
        "assignment_class_counts": dict(sorted(class_counts.items())),
        "drug_visual_context_counts": dict(sorted(visual_counts.items())),
        "star_repeat_profile": {
            "repeated_types": len(repeated_star),
            "repeated_slots": repeated_star_slots,
            "singleton_types": 43 - len(repeated_star),
            "singleton_slots": 60 - repeated_star_slots,
            "type_role_profiles": {
                f"{repeat.lower()}_{role.lower()}": count
                for (repeat, role), count in sorted(star_profiles.items())
            },
        },
        "cross_class_raw_core_collisions": collisions,
        "gdt476_changed_name_labels": changed_context_labels,
        "primary_shifts": {
            "d": "Wurzeldroge",
            "y": "Krautdroge",
            "s": "Blattdroge",
            "or": "helle Wurzeldroge",
            "chos_or_chor": "Faser- oder Fingerwurzelfamilie",
        },
        "legacy_palette_policy": "PRESERVED_AS_EXPLICIT_RIVAL_NOT_ERASED",
        "input_sha256": {name: sha256(path) for name, path in sorted(INPUTS.items())},
        "output_sha256": {
            name: sha256(path) for name, path in sorted(output_hash_paths.items())
        },
        "source_sha256": {
            "model": sha256(Path(__file__).resolve().parent / "model.py"),
            "run": sha256(Path(__file__).resolve()),
        },
        "model_snapshot": serializable_model(),
        "forbidden_pages": ["f84", "f84r"],
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "counts": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
