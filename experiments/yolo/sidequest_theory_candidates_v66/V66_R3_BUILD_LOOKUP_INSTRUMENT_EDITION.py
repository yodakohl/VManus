#!/usr/bin/env python3
"""Build the V66 R3 nonsemantic three-instrument Astro edition."""

from __future__ import annotations

import csv
import io
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"
QUERY_TOOL = ROOT / "vmanus-exp"

SOURCE_DIAGRAMS = YOLO / "sidequest_theory_candidates_v55" / "V55_SELECTED_THREE_DIAGRAMS.tsv"
SOURCE_RULES = YOLO / "sidequest_theory_candidates_v22" / "V22_F69_28_RULES.tsv"
SOURCE_LEDGER = YOLO / "sidequest_theory_candidates_v22" / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"

OUT_GROUPS = HERE / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv"
OUT_LOCI = HERE / "V66_R3_142_LOCUS_FUNCTIONS.tsv"
OUT_MATRIX = HERE / "V66_R3_F67_84_VIRTUAL_LOOKUP_CELLS.tsv"
OUT_ADDRESSES = HERE / "V66_R3_F68_29_ADDRESS_CATALOGUE.tsv"
OUT_RULES = HERE / "V66_R3_F69_28_TECHNICAL_RULES.tsv"
OUT_ROTATIONS = HERE / "V66_R3_196_ROTATION_EQUIVALENCE_VARIANTS.tsv"
OUT_ALGORITHMS = HERE / "V66_R3_3_LOOKUP_ALGORITHMS.tsv"
OUT_DIAGRAMS = HERE / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv"
OUT_COSTS = HERE / "V66_R3_6_MODEL_ASSUMPTION_COSTS.tsv"

QUERY_COLUMNS = (
    "page",
    "locus",
    "record",
    "line",
    "event_index",
    "surface",
    "exact_tuple_id",
    "default_English",
    "source_class",
    "confidence",
    "inheritance_context_rule",
    "ledger_scope",
    "source_event_serial",
)

PAGE_TO_DIAGRAM = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def guarded_astro_rows() -> list[dict[str, str]]:
    command = [
        str(QUERY_TOOL),
        "query-tsv",
        str(SOURCE_LEDGER),
        "--selector",
        "page",
        "--allow",
        "f67r2",
        "--allow",
        "f68r1",
        "--allow",
        "f69v",
        "--columns",
        ",".join(QUERY_COLUMNS),
        "--forbid-prefix",
        "f84",
    ]
    selected = subprocess.check_output(command, text=True)
    return list(csv.DictReader(io.StringIO(selected), delimiter="\t"))


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


TECHNICAL_RULES = (
    "Warmen Arbeitsgang nach Abendbeginn freigeben.",
    "Kühlen Waschgang einmal ausführen und danach stoppen.",
    "Schneiden, Bohren oder Öffnen an diesem Termin unterlassen.",
    "Bewegliche Verbindung ölen und den Lauf prüfen.",
    "Am oberen Gerüst- oder Leitungsabschnitt arbeiten.",
    "Anlage ruhen lassen und keinen Abzug öffnen.",
    "Einen einzelnen Spülgang vollständig ausführen.",
    "Überschüssige Flüssigkeit kontrolliert ablassen.",
    "Starke Erwärmung vermeiden.",
    "Den unteren Kanal- oder Beckenabschnitt bedienen.",
    "Den gewöhnlichen Arbeitsgang freigeben und die Charge einmal umlaufen lassen.",
    "Den Waschgang genau einmal wiederholen.",
    "Die vorige Charge unverändert wiederverwenden.",
    "Die Charge nur bis handwarm erwärmen.",
    "Den gewöhnlichen Arbeitsgang freigeben und die Charge einmal umlaufen lassen.",
    "Die markierte Verbindung ölen.",
    "Arbeit und Anlage in Ruhe halten.",
    "Nur die kleinere Sollmenge verwenden.",
    "Spülen und den Auftrag schließen.",
    "Den Arbeitsgang kein zweites Mal ausführen.",
    "Getrocknetes Vorratsmaterial einsetzen.",
    "Warmen Arbeitsgang ausführen und danach stoppen.",
    "Gewöhnlichen Arbeitsgang unter dem eingetragenen Grenzwert ausführen.",
    "Den gewöhnlichen Arbeitsgang freigeben und die Charge einmal umlaufen lassen.",
    "Arbeitsflüssigkeit durch Tuch oder Sieb führen.",
    "Charge umgießen beziehungsweise übergeben und den Auftrag schließen.",
    "Warme Hülle um Gefäß oder Verbindung legen und die Fuge prüfen.",
    "Arbeitsplan prüfen; bei schwachem oder unsicherem Stand den Auftrag zurückhalten.",
)


ASSUMPTION_WEIGHTS = {
    "STRUCTURAL_TEMPLATE": 1,
    "DOMAIN_ASSIGNMENT": 2,
    "EXTERNAL_ITEM_NAME": 1,
    "LOCAL_RULE_CONTENT": 1,
    "BODY_TREATMENT_BINDING": 2,
    "WORKSHOP_AXIS_BINDING": 1,
    "ORIENTATION_ASSUMPTION": 3,
    "CROSSPAGE_JOIN": 5,
}

ASSUMPTIONS = {
    ("A1", "GENERIC_WORKPLAN"): {"STRUCTURAL_TEMPLATE": 5, "DOMAIN_ASSIGNMENT": 1, "WORKSHOP_AXIS_BINDING": 4},
    ("A1", "MEDICAL_ELECTION_TABLE"): {"STRUCTURAL_TEMPLATE": 5, "DOMAIN_ASSIGNMENT": 1, "EXTERNAL_ITEM_NAME": 39, "BODY_TREATMENT_BINDING": 12},
    ("A2", "GENERIC_WORKPLAN"): {"STRUCTURAL_TEMPLATE": 4, "DOMAIN_ASSIGNMENT": 1, "WORKSHOP_AXIS_BINDING": 1},
    ("A2", "MEDICAL_ELECTION_TABLE"): {"STRUCTURAL_TEMPLATE": 4, "DOMAIN_ASSIGNMENT": 1, "EXTERNAL_ITEM_NAME": 29},
    ("A3", "GENERIC_WORKPLAN"): {"STRUCTURAL_TEMPLATE": 2, "DOMAIN_ASSIGNMENT": 1, "LOCAL_RULE_CONTENT": 28},
    ("A3", "MEDICAL_ELECTION_TABLE"): {"STRUCTURAL_TEMPLATE": 2, "DOMAIN_ASSIGNMENT": 1, "LOCAL_RULE_CONTENT": 28},
}


def encode_assumptions(counts: dict[str, int]) -> str:
    return "|".join(f"{key}:{counts[key]}" for key in ASSUMPTION_WEIGHTS if counts.get(key)) or "NONE"


def assumption_cost(counts: dict[str, int]) -> int:
    return sum(ASSUMPTION_WEIGHTS[key] * value for key, value in counts.items())


def f67_inventory(locus_rows: list[dict[str, str]], lookup: dict[str, dict[str, int]]) -> tuple[str, int, str, str]:
    classes = {row["source_class"] for row in locus_rows}
    locus = locus_rows[0]["locus"]
    if "ZODIAC_BODY_SAFETY_SELECTOR" in classes:
        kind = "COLUMN_12"
        ordinal = lookup[kind][locus]
        return kind, ordinal, f"A1:C{ordinal:02d}", f"Termin-/Sektorspalte C{ordinal:02d} wählen"
    if "SEVENFOLD_GOVERNOR" in classes:
        kind = "ROW_7"
        ordinal = lookup[kind][locus]
        return kind, ordinal, f"A1:R{ordinal:02d}", f"Werk-/Ressourcenreihe R{ordinal:02d} wählen"
    if "ASTROLOGICAL_HOUSE" in classes:
        kind = "AUX_COLUMN_12"
        ordinal = lookup[kind][locus]
        return kind, ordinal, f"A1:X{ordinal:02d}", f"Hilfs-/Kontrollspalte X{ordinal:02d} wählen"
    if "CENTRAL_CONDITION_SECTOR" in classes:
        kind = "CONDITION_8"
        ordinal = lookup[kind][locus]
        return kind, ordinal, f"A1:K{ordinal:02d}", f"Bedingungsslot K{ordinal:02d} prüfen"
    kind = "INSTRUCTION_BLOCK"
    ordinal = lookup[kind][locus]
    return kind, ordinal, f"A1:I{ordinal:02d}", f"Lookup-Anweisungsblock I{ordinal:02d} lesen"


def group_function(page: str, locus_rows: list[dict[str, str]], row: dict[str, str], lookup: dict[str, dict[str, int]], f69_rule_by_locus: dict[str, dict[str, str]]) -> tuple[str, str, str, str]:
    index = int(row["event_index"])
    locus = row["locus"]
    if page == "f67r2":
        kind, ordinal, address, locus_default = f67_inventory(locus_rows, lookup)
        role = {
            "COLUMN_12": "COLUMN_KEY" if index == 1 else "COLUMN_DESCRIPTOR_FRAGMENT",
            "ROW_7": "ROW_KEY" if index == 1 else "ROW_REDUNDANCY_FRAGMENT",
            "AUX_COLUMN_12": "AUXILIARY_KEY" if index == 1 else "AUXILIARY_QUALIFIER_FRAGMENT",
            "CONDITION_8": "CONDITION_KEY" if index == 1 else "CONDITION_REDUNDANCY_FRAGMENT",
            "INSTRUCTION_BLOCK": "LOOKUP_INSTRUCTION_FRAGMENT",
        }[kind]
        local_default = f"{locus_default}; Fragment {index:02d} als opaken Merker bewahren"
        return role, f"{address}:G{index:02d}", local_default, kind
    if page == "f68r1":
        number = locus_number(locus)
        if number <= 7:
            role = "CATALOGUE_HEADER_FRAGMENT"
            address = f"A2:HEADER:L{number:02d}:G{index:02d}"
            local_default = f"Katalogkopf-Fragment {number:02d}.{index:02d} lesen; keine Stationsnummer ableiten"
            kind = "HEADER"
        elif number == 8:
            role = "CENTRAL_OWNER_KEY"
            address = "A2:CENTER:G01"
            local_default = "Zentralen Katalogbesitzer als opaken Mittelpunkt setzen"
            kind = "CENTER"
        elif 9 <= number <= 36:
            role = "SPATIAL_ADDRESS_LABEL"
            address = f"A2:LOC:{locus}:G01"
            local_default = f"Gezeichnete Ortsadresse {locus} nach Bildlage aufsuchen und ihr lokales Label bewahren"
            kind = "STATION_28"
        else:
            role = "CENTRAL_LEGEND_FRAGMENT"
            address = f"A2:LEGEND:G{index:02d}"
            local_default = f"Zentrallegende Fragment {index:02d} lesen; keine Umlaufrichtung erzeugen"
            kind = "LEGEND"
        return role, address, local_default, kind
    require(page == "f69v", f"unexpected page: {page}")
    number = locus_number(locus)
    if number <= 3:
        role = "SCHEDULE_HEADER_FRAGMENT"
        address = f"A3:HEADER:L{number:02d}:G{index:02d}"
        local_default = f"Regelband {number}, Fragment {index:02d}: Konsultationsmodus lesen; Inhalt opak halten"
        kind = "HEADER"
    else:
        rule = f69_rule_by_locus[locus]
        role = "RULE_ENTRY_FRAGMENT"
        address = f"A3:LOC:{locus}:G{index:02d}"
        local_default = f"Regel {int(rule['editorial_rule_index']):02d}, Fragment {index:02d}: {rule['technical_rule_German']}"
        kind = "RULE_28"
    return role, address, local_default, kind


def main() -> None:
    source_diagrams = read_tsv(SOURCE_DIAGRAMS)
    source_rules = read_tsv(SOURCE_RULES)
    astro_rows = guarded_astro_rows()
    require((len(source_diagrams), len(source_rules), len(astro_rows)) == (3, 28, 395), "selected source counts changed")
    require(Counter(row["page"] for row in astro_rows) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}), "Astro page counts changed")
    require({row["ledger_scope"] for row in astro_rows} == {"ZL3B_ASTRO_VISIBLE_TOKEN"}, "non-Astro row reached builder")
    require(len({(row["page"], row["locus"]) for row in astro_rows}) == 142, "Astro locus count changed")
    require(all(row["cross_page_alignment"] == "NONE" and row["polarity_from_layout"] == "NO" for row in source_rules), "V22 no-join/no-polarity contract changed")

    rows_by_page_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro_rows:
        rows_by_page_locus[(row["page"], row["locus"])].append(row)

    # Build explicit f67 inventory lookup from visible locus classes.  Modern
    # order is audit order only and never an authorial origin.
    f67_loci = sorted((key for key in rows_by_page_locus if key[0] == "f67r2"), key=lambda key: locus_number(key[1]))
    inventory_loci: dict[str, list[str]] = defaultdict(list)
    for _, locus in f67_loci:
        classes = {row["source_class"] for row in rows_by_page_locus[("f67r2", locus)]}
        kind = (
            "COLUMN_12" if "ZODIAC_BODY_SAFETY_SELECTOR" in classes else
            "ROW_7" if "SEVENFOLD_GOVERNOR" in classes else
            "AUX_COLUMN_12" if "ASTROLOGICAL_HOUSE" in classes else
            "CONDITION_8" if "CENTRAL_CONDITION_SECTOR" in classes else
            "INSTRUCTION_BLOCK"
        )
        inventory_loci[kind].append(locus)
    require({key: len(value) for key, value in inventory_loci.items()} == {"COLUMN_12": 12, "INSTRUCTION_BLOCK": 35, "ROW_7": 7, "AUX_COLUMN_12": 12, "CONDITION_8": 8}, "f67 inventory partition changed")
    f67_lookup = {kind: {locus: index for index, locus in enumerate(loci, 1)} for kind, loci in inventory_loci.items()}

    f69_rule_rows: list[dict[str, str]] = []
    for source, technical in zip(source_rules, TECHNICAL_RULES, strict=True):
        index = int(source["station_index"])
        expected_locus = f"f69v.{index + 3}"
        require(source["locus"] == expected_locus, f"f69 locus/index changed: {source['station_index']}")
        source_locus_rows = rows_by_page_locus[("f69v", source["locus"])]
        require(" ".join(row["surface"] for row in source_locus_rows) == source["surface_entry"], f"f69 entry/group surface mismatch: {index}")
        f69_rule_rows.append(
            {
                "editorial_rule_index": source["station_index"],
                "source_locus_address": f"A3:LOC:{source['locus']}",
                "source_locus": source["locus"],
                "surface_entry_display_only": source["surface_entry"],
                "layout_class_descriptive_only": source["layout_parity"],
                "technical_rule_German": technical,
                "medical_election_comparator": source["selected_concrete_rule"],
                "polarity_from_layout": "NO",
                "crosspage_alignment": "NONE",
                "orientation_status": "EDITORIAL_INDEX_ONLY;AUTHOR_START_AND_DIRECTION_UNLICENSED",
                "same_entry_contract": "IDENTICAL_FULL_ENTRY_MUST_KEEP_IDENTICAL_TECHNICAL_RULE",
                "source_lineage": "V22_F69_RULE>V55_SELECTED_LOCAL_SCHEDULE>V66_R3_TECHNICAL_RULE",
            }
        )
    f69_rule_by_locus = {row["source_locus"]: row for row in f69_rule_rows}
    repeated_rules: dict[str, set[str]] = defaultdict(set)
    for row in f69_rule_rows:
        repeated_rules[row["surface_entry_display_only"]].add(row["technical_rule_German"])
    require(all(len(values) == 1 for values in repeated_rules.values()), "identical f69 entry received conflicting rule")

    group_rows: list[dict[str, str]] = []
    locus_rows: list[dict[str, str]] = []
    local_group_counter: Counter[str] = Counter()
    page_locus_ordinals: dict[tuple[str, str], int] = {}
    for page in ("f67r2", "f68r1", "f69v"):
        page_loci = sorted((locus for source_page, locus in rows_by_page_locus if source_page == page), key=locus_number)
        for ordinal, locus in enumerate(page_loci, 1):
            page_locus_ordinals[(page, locus)] = ordinal
            diagram = PAGE_TO_DIAGRAM[page]
            source_locus_rows = rows_by_page_locus[(page, locus)]
            local_group_ids: list[str] = []
            group_roles: list[str] = []
            technical_defaults: list[str] = []
            addresses: list[str] = []
            locus_kind = ""
            for source_row in source_locus_rows:
                local_group_counter[page] += 1
                local_group_id = f"{diagram}:G{local_group_counter[page]:03d}"
                role, address, local_default, kind = group_function(page, source_locus_rows, source_row, f67_lookup, f69_rule_by_locus)
                locus_kind = kind
                local_group_ids.append(local_group_id)
                group_roles.append(role)
                technical_defaults.append(local_default)
                addresses.append(address)
                group_rows.append(
                    {
                        "local_group_id": local_group_id,
                        "diagram_id": diagram,
                        "page": page,
                        "source_locus": locus,
                        "locus_ordinal_editorial": str(ordinal),
                        "group_index_within_locus": source_row["event_index"],
                        "surface_display_only": source_row["surface"],
                        "instrument_component": kind,
                        "technical_group_role": role,
                        "local_lookup_address": address,
                        "concrete_technical_function_German": local_default,
                        "medical_election_comparator_local_only": source_row["default_English"],
                        "orientation_contract": "SOURCE_LOCUS_PRESERVED;NO_IMPLICIT_START_OR_DIRECTION",
                        "crosspage_contract": "PAGE_LOCAL_ID_ONLY;NO_F68_F69_JOIN;NO_PROSE_TUPLE",
                        "semantic_status": "LOCAL_FUNCTION_EXEMPLAR_NOT_WORD_MEANING",
                        "source_lineage": "GUARDED_V22_ASTRO_ROW>V55_SELECTED_INSTRUMENT>V66_R3_LOCAL_GROUP",
                    }
                )
            locus_address = addresses[0].rsplit(":G", 1)[0] if all(address.rsplit(":G", 1)[0] == addresses[0].rsplit(":G", 1)[0] for address in addresses) else f"{diagram}:LOC:{locus}"
            locus_rows.append(
                {
                    "local_locus_id": f"{diagram}:L{ordinal:03d}",
                    "diagram_id": diagram,
                    "page": page,
                    "source_locus": locus,
                    "locus_ordinal_editorial": str(ordinal),
                    "group_count": str(len(source_locus_rows)),
                    "local_group_ids": "|".join(local_group_ids),
                    "surface_sequence_display_only": " ".join(row["surface"] for row in source_locus_rows),
                    "instrument_component": locus_kind,
                    "local_lookup_address": locus_address,
                    "technical_role_sequence": " > ".join(group_roles),
                    "complete_technical_locus_reading_German": " ; ".join(technical_defaults),
                    "medical_election_comparator": " ; ".join(row["default_English"] for row in source_locus_rows),
                    "orientation_contract": "LOCUS_IS_PRIMARY;EDITORIAL_ORDINAL_NOT_AUTHORIAL_ORIGIN",
                    "crosspage_contract": "NONE",
                    "source_lineage": "GUARDED_V22_ASTRO_LOCUS>V55_SELECTED_INSTRUMENT>V66_R3_LOCUS_FUNCTION",
                }
            )

    matrix_rows: list[dict[str, str]] = []
    for row_index in range(1, 8):
        for column_index in range(1, 13):
            work_order = f"A1:W{(row_index - 1) * 12 + column_index:02d}"
            matrix_rows.append(
                {
                    "virtual_cell_address": f"A1:R{row_index:02d}:C{column_index:02d}",
                    "row_selector_address": f"A1:R{row_index:02d}",
                    "column_selector_address": f"A1:C{column_index:02d}",
                    "work_order_code": work_order,
                    "technical_default_German": f"Arbeitsklasse R{row_index:02d} im Termin-/Sektorabschnitt C{column_index:02d} buchen; gewählten K-Slot gesondert prüfen",
                    "visible_cell_value": "NONE;VIRTUAL_COMBINATION_ONLY",
                    "auxiliary_axis": "OPTIONAL_A1:X01-X12_CALLER_SUPPLIED",
                    "condition_axis": "REQUIRED_A1:K01-K08_CALLER_SUPPLIED",
                    "rotation_equivalence": f"C7xC12_ORBIT;canonical_coordinates_are_editorial_R{row_index:02d}_C{column_index:02d}",
                    "orientation_status": "NO_AUTHORIAL_ROW_OR_COLUMN_ORIGIN_CLAIM",
                    "source_lineage": "V55_7x12_FORMAL_ROLE>V66_R3_VIRTUAL_MATRIX",
                }
            )

    address_rows: list[dict[str, str]] = [
        {
            "catalogue_entry_type": "CENTER",
            "source_locus": "f68r1.8",
            "local_address": "A2:CENTER",
            "editorial_station_index": "NONE",
            "surface_display_only": rows_by_page_locus[("f68r1", "f68r1.8")][0]["surface"],
            "technical_default_German": "Opaken Mittelpunkt als Besitzer des räumlichen Katalogs setzen",
            "lookup_key": "DRAWN_CENTER_ONLY",
            "rotation_equivalence": "FIXED_CENTER_UNDER_ALL_C28_ROTATIONS",
            "orientation_status": "NO_START;NO_DIRECTION",
            "crosspage_mapping": "NONE",
            "source_lineage": "V55_CENTER_PLUS_28>V66_R3_ADDRESS_CATALOGUE",
        }
    ]
    for station_index, locus_number_value in enumerate(range(9, 37), 1):
        locus = f"f68r1.{locus_number_value}"
        source = rows_by_page_locus[("f68r1", locus)][0]
        address_rows.append(
            {
                "catalogue_entry_type": "SPATIAL_STATION",
                "source_locus": locus,
                "local_address": f"A2:LOC:{locus}",
                "editorial_station_index": str(station_index),
                "surface_display_only": source["surface"],
                "technical_default_German": f"Nach gezeichneter Lage die Ortsadresse {locus} wählen und den angehängten Merker unverändert nachschlagen",
                "lookup_key": "DRAWN_2D_LOCUS;NOT_NUMBER",
                "rotation_equivalence": "C28_ENUMERATION_ORBIT;SPATIAL_LOCUS_REMAINS_PRIMARY",
                "orientation_status": "EDITORIAL_INDEX_ONLY;NO_START;NO_DIRECTION",
                "crosspage_mapping": "NONE",
                "source_lineage": "V55_CENTER_PLUS_28>V66_R3_ADDRESS_CATALOGUE",
            }
        )

    rotation_rows: list[dict[str, str]] = []
    for row_offset in range(7):
        for column_offset in range(12):
            rotation_rows.append(
                {
                    "diagram_id": "A1",
                    "variant_id": f"A1:ROT:R{row_offset}:C{column_offset}",
                    "primary_offset": str(row_offset),
                    "secondary_offset": str(column_offset),
                    "traversal_sense": "PRESERVE_DRAWN_AXIS_ADJACENCY",
                    "mapping_rule": "R_i->R_(((i-1+row_offset) mod 7)+1);C_j->C_(((j-1+column_offset) mod 12)+1)",
                    "preserved_structure": "7x12 incidence; auxiliary12 and condition8 remain separate",
                    "authorial_orientation_licensed": "NO",
                    "crosspage_effect": "NONE",
                }
            )
    for diagram in ("A2", "A3"):
        for offset in range(28):
            for sense in ("FORWARD", "REVERSE"):
                sign = "+" if sense == "FORWARD" else "-"
                rotation_rows.append(
                    {
                        "diagram_id": diagram,
                        "variant_id": f"{diagram}:ROT:{offset:02d}:{sense}",
                        "primary_offset": str(offset),
                        "secondary_offset": "NONE",
                        "traversal_sense": sense,
                        "mapping_rule": f"editorial_i->((( {sign}(i-1)+{offset}) mod 28)+1);source locus remains recorded",
                        "preserved_structure": "center fixed and 28-place adjacency" if diagram == "A2" else "28-rule cyclic adjacency; LONG/SHORT ignored",
                        "authorial_orientation_licensed": "NO",
                        "crosspage_effect": "NONE;variants never align A2 to A3",
                    }
                )

    algorithm_rows = [
        {
            "diagram_id": "A1",
            "formal_instrument": "7x12_SELECTOR_MATRIX_WITH_AUX12_CONDITION8",
            "required_input": "row R01-R07; column C01-C12; condition K01-K08; optional X01-X12",
            "deterministic_algorithm": "VALIDATE_LOCAL_KEYS>FORM_A1:Rxx:Cyy>LOOKUP_84_CELL>ATTACH_CALLER_K_AND_OPTIONAL_X>RETURN_WORK_ORDER_CODE_AND_SOURCE_SELECTOR_LOCI",
            "output": "page-local virtual work-order address plus visible row/column/condition locus references",
            "error_conditions": "missing K; out-of-range key; request for semantic planet/zodiac value without external source",
            "rotation_behavior": "without declared editorial offsets return C7xC12 equivalence orbit; never choose an origin silently",
            "process_graph": "ROW_KEY + COLUMN_KEY + CONDITION_KEY -> VIRTUAL_CELL -> WORK_ORDER_CODE",
            "crosspage_join": "NONE",
        },
        {
            "diagram_id": "A2",
            "formal_instrument": "CENTER_PLUS_28_SPATIAL_ADDRESS_CATALOGUE",
            "required_input": "drawn source locus f68r1.9-f68r1.36 or CENTER",
            "deterministic_algorithm": "VALIDATE_DRAWN_LOCUS>LOOKUP_PAGE_LOCAL_ADDRESS>RETURN_ATTACHED_OPAQUE_LABEL;REJECT_BARE_1_TO_28_WITHOUT_DECLARED_EDITORIAL_VARIANT",
            "output": "A2:CENTER or A2:LOC:f68r1.n with its local group",
            "error_conditions": "bare ordinal without rotation variant; direction assumed; request for f69 rule",
            "rotation_behavior": "return all 56 offset/sense enumerations when enumeration is requested without orientation",
            "process_graph": "DRAWN_2D_LOCUS -> PAGE_LOCAL_ADDRESS -> OPAQUE_CATALOGUE_ENTRY",
            "crosspage_join": "REJECT_UNLICENSED_F68_TO_F69_JOIN",
        },
        {
            "diagram_id": "A3",
            "formal_instrument": "SEPARATE_ORDERED_28_RULE_SCHEDULE",
            "required_input": "source locus f69v.4-f69v.31; optional declared editorial rotation/sense",
            "deterministic_algorithm": "VALIDATE_SOURCE_LOCUS>LOOKUP_LOCAL_RULE>RETURN_TECHNICAL_DEFAULT_AND_OPAQUE_ENTRY;IF_ONLY_ORDINAL_REQUIRE_VARIANT",
            "output": "A3 local rule address and one technical work-plan default",
            "error_conditions": "LONG/SHORT treated as polarity; implicit origin/direction; f68 station used as key",
            "rotation_behavior": "preserve source locus; expose 56 possible cyclic enumerations; identical full entry retains identical rule",
            "process_graph": "HEADER_MODE -> SOURCE_RULE_LOCUS -> LOCAL_RULE -> EXECUTE_OR_WITHHOLD",
            "crosspage_join": "REJECT_UNLICENSED_F68_TO_F69_JOIN",
        },
    ]

    diagram_by_id = {row["diagram_id"]: row for row in source_diagrams}
    cost_rows: list[dict[str, str]] = []
    for (diagram, model), counts in ASSUMPTIONS.items():
        cost_rows.append(
            {
                "diagram_id": diagram,
                "model": model,
                "assumption_counts": encode_assumptions(counts),
                "weighted_cost": str(assumption_cost(counts)),
                "orientation_assumption": "0",
                "crosspage_join_assumption": "0",
                "cost_contract": "STRUCTURE=1;DOMAIN=2;EXTERNAL_NAME=1;LOCAL_RULE=1;BODY_BINDING=2;WORKSHOP_AXIS=1;ORIENTATION=3;CROSSPAGE_JOIN=5",
                "interpretation": "DESCRIPTION_LENGTH_PROXY_NOT_HISTORICAL_PROBABILITY",
                "source_lineage": "V55_SELECTED_COMPETITION>V66_R3_FIXED_COST_MODEL",
            }
        )

    diagram_rows: list[dict[str, str]] = []
    for diagram in ("A1", "A2", "A3"):
        selected = diagram_by_id[diagram]
        technical_cost = assumption_cost(ASSUMPTIONS[(diagram, "GENERIC_WORKPLAN")])
        medical_cost = assumption_cost(ASSUMPTIONS[(diagram, "MEDICAL_ELECTION_TABLE")])
        winner = "GENERIC_WORKPLAN" if technical_cost < medical_cost else "MEDICAL_ELECTION_TABLE" if medical_cost < technical_cost else "TIE"
        technical_article = {
            "A1": "Wähle eine der sieben Werk-/Ressourcenreihen R, eine der zwölf Termin-/Sektorspalten C und einen der acht Bedingungsslots K; bilde R/C, lies den virtuellen Arbeitsauftrag und führe optionale Kontrollspalte X getrennt. Ohne deklarierte Achsenursprünge gib alle rotationsäquivalenten Adressen aus.",
            "A2": "Setze den Mittelpunkt als opaken Besitzer. Wähle eine der 28 Adressen ausschließlich nach ihrer gezeichneten zweidimensionalen Lage, bewahre ihr lokales Label und lehne jede bloße Nummer sowie jede Verknüpfung zu f69 ab.",
            "A3": "Lies die drei Kopfband-Loci als Konsultationsmodus. Wähle danach eine Regel über ihren f69-Quellort, gib den vollständigen lokalen Arbeitsplan aus und behalte gleiche Vollflächeneinträge gleich; LONG/SHORT erzeugt keinen Wert.",
        }[diagram]
        diagram_rows.append(
            {
                "diagram_id": diagram,
                "folio": selected["folio"],
                "locus_count": selected["locus_count"],
                "group_count": selected["group_count"],
                "technical_formal_role": {"A1": "7x12_GENERIC_WORK_SELECTOR", "A2": "CENTER_PLUS_28_SPATIAL_ADDRESS_CATALOGUE", "A3": "SEPARATE_28_WORK_RULE_SCHEDULE"}[diagram],
                "complete_technical_default_German": technical_article,
                "medical_election_comparator": selected["complete_working_translation_German"],
                "technical_assumption_cost": str(technical_cost),
                "medical_assumption_cost": str(medical_cost),
                "cost_winner": winner,
                "historical_fit_winner": "MEDICAL_ELECTION_TABLE" if diagram in {"A1", "A2"} else "TIE_MEDICAL_LEAD",
                "rotation_variants": "84" if diagram == "A1" else "56",
                "orientation_status": "NO_AUTHORIAL_START_OR_DIRECTION_LICENSED",
                "direct_crosspage_mapping": "NONE",
                "strongest_contradiction": selected["main_contradiction"],
                "source_lineage": "V55_SELECTED_DIAGRAM>V66_R3_TECHNICAL_EDITION",
            }
        )

    # Negative join check uses only guarded Astro-local surfaces.
    f68_surfaces = [row["surface_display_only"] for row in address_rows if row["catalogue_entry_type"] == "SPATIAL_STATION"]
    f69_surfaces = [row["surface_entry_display_only"] for row in f69_rule_rows]
    require(sum(left == right for left, right in zip(f68_surfaces, f69_surfaces, strict=True)) == 0, "same-index f68/f69 full form match appeared")
    require(set(f68_surfaces).isdisjoint(f69_surfaces), "crosspage full-form match appeared")

    require((len(group_rows), len(locus_rows), len(matrix_rows), len(address_rows), len(f69_rule_rows), len(rotation_rows), len(algorithm_rows), len(diagram_rows), len(cost_rows)) == (395, 142, 84, 29, 28, 196, 3, 3, 6), "output counts changed")
    write_tsv(OUT_GROUPS, group_rows)
    write_tsv(OUT_LOCI, locus_rows)
    write_tsv(OUT_MATRIX, matrix_rows)
    write_tsv(OUT_ADDRESSES, address_rows)
    write_tsv(OUT_RULES, f69_rule_rows)
    write_tsv(OUT_ROTATIONS, rotation_rows)
    write_tsv(OUT_ALGORITHMS, algorithm_rows)
    write_tsv(OUT_DIAGRAMS, diagram_rows)
    write_tsv(OUT_COSTS, cost_rows)
    print("PASS V66 R3 build")
    print("groups=395 loci=142 matrix_cells=84 addresses=29 rules=28 rotations=196")
    print("pages=f67r2:190/74;f68r1:65/37;f69v:140/31")
    print("f68_to_f69=same_index_0;all_pairs_0;direct_join_NONE")
    print("cost totals=generic_workplan:" + str(sum(int(row['technical_assumption_cost']) for row in diagram_rows)) + ";medical_election:" + str(sum(int(row['medical_assumption_cost']) for row in diagram_rows)))


if __name__ == "__main__":
    main()
