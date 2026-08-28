#!/usr/bin/env python3
"""Independent, source-based validator for GDT582.

The validator deliberately does not import either GDT582 generating module. It
re-derives slot partitions, root/register cells, learned-name keys, event and
local-card membership, statement composition, and page totals directly from
the sealed GDT581 TSV artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill"
ART = BASE / "artifacts"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"

INPUTS = {
    "complete_slots": G581 / "gdt581_15889_complete_slot_ledger.tsv",
    "aliases": G581 / "gdt581_4026_inherited_alias_edges.tsv",
    "events": G581 / "gdt581_5122_content_ready_event_edition.tsv",
    "statements": G581 / "gdt581_793_content_ready_statement_edition.tsv",
    "pages": G581 / "gdt581_30_page_boundary_profiles.tsv",
    "local_cards": G581 / "gdt581_744_local_card_hosts.tsv",
    "name_slots": G581 / "gdt581_107_name_core_slots.tsv",
}

OUTPUTS = {
    "complete": ART / "gdt582_15889_complete_default_ledger.tsv",
    "content": ART / "gdt582_13702_content_slot_defaults.tsv",
    "controls": ART / "gdt582_2187_control_slot_defaults.tsv",
    "roots": ART / "gdt582_42_core_stem_defaults.tsv",
    "cells": ART / "gdt582_181_register_realization_cells.tsv",
    "names": ART / "gdt582_80_learned_name_defaults.tsv",
    "aliases": ART / "gdt582_4026_alias_default_resolutions.tsv",
    "events": ART / "gdt582_5122_concrete_event_edition.tsv",
    "statements": ART / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards": ART / "gdt582_744_concrete_local_card_edition.tsv",
    "pages": ART / "gdt582_30_page_concrete_profiles.tsv",
    "event_checks": ART / "gdt582_25_event_sense_checks.tsv",
    "passage_checks": ART / "gdt582_20_complete_passage_sense_checks.tsv",
    "packs": ART / "gdt582_4_candidate_pack_scorecard.tsv",
}

# Pin the precise GDT581 source edition admitted by GDT582. A regenerated
# result file therefore cannot make an upstream mutation silently pass.
EXPECTED_INPUT_SHA256 = {
    "complete_slots": "3adb073e7a572e3f71876d156db9142e1ab324d455e11a797dc2bbd351496176",
    "aliases": "27203f5e2b3c76134eae63082be4a9a4739f8e9507ff599854b1c221e20cd295",
    "events": "ce94f0ec11cd226cf1946a6bc1fa21420bd97c311e35cdab164c46143bc35c43",
    "statements": "ce9f447afb45e171bf5baf026b85051c25e5e04fe9c67f0178ce0353ca1c3801",
    "pages": "9454fa327a53fda42bb97babb9cb59027f37707ded44ef16f73885dc5abefd3c",
    "local_cards": "b4c55fc633e91d1cf4e26cae0f288bb6a4999133fd075846c19ac58f1528fbe3",
    "name_slots": "9011dc01a9e141bf7d202bd290805b0da0a3bd2ce3a88e8e2b2b03e3300b9d6a",
}

EXPECTED_COUNTS = {
    "complete": 15889,
    "content": 13702,
    "controls": 2187,
    "productive": 13593,
    "learned": 109,
    "roots": 42,
    "cells": 181,
    "names": 80,
    "aliases": 4026,
    "events": 5122,
    "statements": 793,
    "local_cards": 744,
    "pages": 30,
    "event_checks": 25,
    "passage_checks": 20,
    "packs": 4,
}

REGISTERS = (
    "SOURCE_SECTION_T",
    "HERBAL",
    "CELESTIAL",
    "BIOLOGICAL",
    "PHARMA",
)

EXPECTED_ROOTS = {
    "AIIN", "AIN", "AIR", "AL", "AM_ADDR", "AN", "AR", "A_ADDR",
    "CARRIER_Q", "CH", "CHD", "DA", "D_ADDR", "D_LABEL", "E", "EE",
    "EEE", "G_LABEL", "HO", "IIN", "K", "L", "LOCAL_CHAR_B",
    "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_J",
    "LOCAL_CHAR_Z", "M_LOCAL", "O", "OK", "OR", "OS", "P", "R", "S",
    "SH", "S_ADDR", "S_LABEL", "T", "Y", "Z_ADDR",
}

EXPECTED_NAME_CLASSES = {
    "STAR_BEARING_RING_POSITION",
    "DRUG_OR_INGREDIENT_OBJECT",
    "BATH_OR_OUTLET_STATION",
    "PICTURED_PLANT",
}

EXPECTED_LOCAL_X = {
    "RUNNING:G515-E0410@2": (
        "INDICATION_OR_ILLNESS",
        "Krankheit oder Beschwerde",
    ),
    "RUNNING:G515-E0438@2": (
        "REMEDY_OR_HEALING",
        "Heilmittel oder Heilwirkung",
    ),
}

# These are deliberate GDT582 theory choices, not values derivable from a
# count. Keeping them here makes the validator independent of defaults.py.
EXPECTED_RELATION_REALIZATIONS = {
    ("AL", "SOURCE_SECTION_T"): "zur Zielstelle oder ins Zielgefäß",
    ("AL", "HERBAL"): "zur Zielstelle oder ins Auffanggefäß",
    ("AL", "CELESTIAL"): "zur Zielposition",
    ("AL", "BIOLOGICAL"): "zur Zielstation oder ins Zielbecken",
    ("AL", "PHARMA"): "ins Aufnahme- oder Zielgefäß",
    ("AR", "SOURCE_SECTION_T"): "von der Quelle oder aus dem Ausgangsgefäß",
    ("AR", "HERBAL"): "vom Ausgangsmaterial oder -gefäß",
    ("AR", "CELESTIAL"): "von der Ausgangsposition",
    ("AR", "BIOLOGICAL"): "von der Ausgangsstation oder aus dem Ausgangsbecken",
    ("AR", "PHARMA"): "aus dem Ausgangsgefäß",
    ("L", "SOURCE_SECTION_T"): "über den Arbeitskontakt",
    ("L", "HERBAL"): "über den Materialkontakt",
    ("L", "CELESTIAL"): "über den Ringkontakt",
    ("L", "BIOLOGICAL"): "über den Stationskontakt oder die Leitung",
    ("L", "PHARMA"): "über den Gefäßkontakt",
    ("AIR", "SOURCE_SECTION_T"): "entlang des Arbeitswegs",
    ("AIR", "HERBAL"): "entlang des Verarbeitungswegs",
    ("AIR", "CELESTIAL"): "entlang der Ringbahn",
    ("AIR", "BIOLOGICAL"): "entlang des Stationswegs oder Kanals",
    ("AIR", "PHARMA"): "durch den Transferkanal",
}

DEFAULT_FIELDS = (
    "gdt582_default_key",
    "gdt582_default_kind",
    "gdt582_core_concept",
    "gdt582_concrete_default_de",
    "gdt582_default_basis",
    "gdt582_default_status",
    "gdt582_guard",
)


class Table:
    def __init__(self, path: Path) -> None:
        self.path = path
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            self.fields = list(reader.fieldnames or [])
            self.rows = list(reader)
        if not self.fields:
            raise RuntimeError(f"Empty or headerless TSV: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return {
            str(key): count
            for key, count in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, set):
        return sorted(str(item) for item in value)
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serial(item) for item in value]
    return value


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(
        self, check_id: str, condition: bool, observed: Any, expected: Any
    ) -> None:
        self.checks.append(
            {
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "observed": serial(observed),
                "expected": serial(expected),
            }
        )

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [check for check in self.checks if check["status"] == "FAIL"]


def unique(
    rows: Iterable[dict[str, str]], key: str
) -> tuple[dict[str, dict[str, str]], list[str]]:
    source = list(rows)
    counts = Counter(row.get(key, "") for row in source)
    duplicates = sorted(value for value, count in counts.items() if count != 1)
    return {row.get(key, ""): row for row in source}, duplicates


def nonempty(value: Any) -> bool:
    return bool(str(value).strip())


def stable_join(values: Iterable[str]) -> str:
    items = sorted(set(values))
    return "|".join(items) if items else "NONE"


def projection_mismatches(
    source: Table, target: Table, key: str
) -> tuple[bool, int, list[str]]:
    if target.fields[: len(source.fields)] != source.fields:
        return False, -1, ["HEADER_PREFIX_MISMATCH"]
    source_by_id, source_duplicates = unique(source.rows, key)
    target_by_id, target_duplicates = unique(target.rows, key)
    duplicate_ids = sorted(set(source_duplicates + target_duplicates))
    if duplicate_ids:
        return False, -1, duplicate_ids[:10]
    mismatch_ids: list[str] = []
    for identity in sorted(set(source_by_id) | set(target_by_id)):
        left = source_by_id.get(identity)
        right = target_by_id.get(identity)
        if left is None or right is None:
            mismatch_ids.append(identity)
            continue
        if any(left[field] != right.get(field, "") for field in source.fields):
            mismatch_ids.append(identity)
    same_order = [row[key] for row in source.rows] == [
        row[key] for row in target.rows
    ]
    return not mismatch_ids and same_order, len(mismatch_ids), mismatch_ids[:10]


def family_from_boundary(boundary_class: str) -> str | None:
    match = re.fullmatch(
        r"(?:RUNNING|LOCAL)_(ACTION|OBJECT|RELATION|MODIFIER)_FUNCTION",
        boundary_class,
    )
    return match.group(1) if match else None


def trace_for(rows: Iterable[dict[str, str]]) -> str:
    ordered = sorted(
        rows, key=lambda row: (int(row["slot_position"]), row["slot_id"])
    )
    return " ".join(
        f"[{row['slot_position']}:{row['slot_value']}="
        f"{row['gdt582_concrete_default_de']}|{row['slot_id']}|"
        f"{row['primary_governor_key']}]"
        for row in ordered
    )


def trace_slot_ids(trace: str) -> list[str]:
    identities: list[str] = []
    for block in re.findall(r"\[([^\[\]]+)\]", trace):
        parts = block.split("|", 2)
        if len(parts) == 3:
            identities.append(parts[1])
    return identities


def row_counts(rows: Iterable[dict[str, str]]) -> tuple[int, int, int]:
    source = list(rows)
    return (
        len(source),
        sum(row["fill_status"] == "CONTENT_CARRIER" for row in source),
        sum(row["fill_status"] == "CONTROL_HOST_ONLY" for row in source),
    )


def validate(audit: Audit) -> None:
    inputs = {name: Table(path) for name, path in INPUTS.items()}
    outputs = {name: Table(path) for name, path in OUTPUTS.items()}
    result_path = ART / "gdt582_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    actual_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    audit.check(
        "pinned_gdt581_input_hashes",
        actual_hashes == EXPECTED_INPUT_SHA256,
        actual_hashes,
        EXPECTED_INPUT_SHA256,
    )
    audit.check(
        "result_declares_actual_input_hashes",
        result.get("input_sha256") == actual_hashes,
        result.get("input_sha256"),
        actual_hashes,
    )

    observed_counts = {name: len(table.rows) for name, table in outputs.items()}
    observed_counts["productive"] = sum(
        row.get("gdt582_default_kind") == "PRODUCTIVE_REGISTER_FUNCTION"
        for row in outputs["complete"].rows
    )
    observed_counts["learned"] = sum(
        row.get("gdt582_default_kind")
        in {"CLASS_CONDITIONED_LEARNED_NAME", "OWNER_BOUND_LOCAL_X"}
        for row in outputs["complete"].rows
    )
    audit.check(
        "all_sixteen_exact_artifact_counts",
        observed_counts == EXPECTED_COUNTS,
        observed_counts,
        EXPECTED_COUNTS,
    )
    source_counts = {
        "complete": len(inputs["complete_slots"].rows),
        "aliases": len(inputs["aliases"].rows),
        "events": len(inputs["events"].rows),
        "statements": len(inputs["statements"].rows),
        "pages": len(inputs["pages"].rows),
        "local_cards": len(inputs["local_cards"].rows),
        "name_slots": len(inputs["name_slots"].rows),
    }
    expected_source_counts = {
        "complete": 15889,
        "aliases": 4026,
        "events": 5122,
        "statements": 793,
        "pages": 30,
        "local_cards": 744,
        "name_slots": 107,
    }
    audit.check(
        "gdt581_source_counts",
        source_counts == expected_source_counts,
        source_counts,
        expected_source_counts,
    )

    source_complete = inputs["complete_slots"]
    complete = outputs["complete"]
    complete_by_id, complete_duplicates = unique(complete.rows, "slot_id")
    source_complete_by_id, source_complete_duplicates = unique(
        source_complete.rows, "slot_id"
    )
    audit.check(
        "complete_slot_id_exactly_once",
        not complete_duplicates
        and not source_complete_duplicates
        and set(complete_by_id) == set(source_complete_by_id),
        {
            "unique": len(complete_by_id),
            "duplicates_or_blanks": complete_duplicates[:10],
            "source_duplicates_or_blanks": source_complete_duplicates[:10],
            "symmetric_difference": len(
                set(complete_by_id) ^ set(source_complete_by_id)
            ),
        },
        {
            "unique": 15889,
            "duplicates_or_blanks": [],
            "source_duplicates_or_blanks": [],
            "symmetric_difference": 0,
        },
    )
    projection_ok, mismatch_count, mismatch_sample = projection_mismatches(
        source_complete, complete, "slot_id"
    )
    audit.check(
        "slot_identity_and_host_projection_unchanged",
        projection_ok,
        {"mismatch_count": mismatch_count, "sample": mismatch_sample},
        {"mismatch_count": 0, "sample": []},
    )

    missing_default_columns = sorted(set(DEFAULT_FIELDS) - set(complete.fields))
    empty_defaults = [
        f"{row.get('slot_id', '?')}:{field}"
        for row in complete.rows
        for field in DEFAULT_FIELDS
        if not nonempty(row.get(field, ""))
    ]
    audit.check(
        "every_complete_slot_has_every_nonempty_default_field",
        not missing_default_columns and not empty_defaults,
        {
            "missing_columns": missing_default_columns,
            "empty_count": len(empty_defaults),
            "sample": empty_defaults[:10],
        },
        {"missing_columns": [], "empty_count": 0, "sample": []},
    )

    source_content = [
        row
        for row in source_complete.rows
        if row["fill_status"] == "CONTENT_CARRIER"
    ]
    source_controls = [
        row
        for row in source_complete.rows
        if row["fill_status"] == "CONTROL_HOST_ONLY"
    ]
    target_content = [
        row for row in complete.rows if row["fill_status"] == "CONTENT_CARRIER"
    ]
    target_controls = [
        row for row in complete.rows if row["fill_status"] == "CONTROL_HOST_ONLY"
    ]
    partition_statuses = Counter(row["fill_status"] for row in source_complete.rows)
    audit.check(
        "complete_content_control_partition",
        partition_statuses
        == {"CONTENT_CARRIER": 13702, "CONTROL_HOST_ONLY": 2187},
        partition_statuses,
        {"CONTENT_CARRIER": 13702, "CONTROL_HOST_ONLY": 2187},
    )
    audit.check(
        "content_artifact_is_exact_complete_projection",
        outputs["content"].fields == complete.fields
        and outputs["content"].rows == target_content,
        {
            "rows": len(outputs["content"].rows),
            "header_equal": outputs["content"].fields == complete.fields,
        },
        {"rows": 13702, "header_equal": True},
    )
    audit.check(
        "control_artifact_is_exact_complete_projection",
        outputs["controls"].fields == complete.fields
        and outputs["controls"].rows == target_controls,
        {
            "rows": len(outputs["controls"].rows),
            "header_equal": outputs["controls"].fields == complete.fields,
        },
        {"rows": 2187, "header_equal": True},
    )

    learned_source = [
        row
        for row in source_content
        if row["boundary_class"]
        in {"LOCAL_LEARNED_NAME_SLOT", "RUNNING_LEARNED_CORE"}
    ]
    learned_ids = {row["slot_id"] for row in learned_source}
    productive_source = [
        row for row in source_content if row["slot_id"] not in learned_ids
    ]
    productive_ids = {row["slot_id"] for row in productive_source}
    observed_semantic_partition = {
        "productive": len(productive_source),
        "learned": len(learned_source),
        "learned_names": sum(
            row["boundary_class"] == "LOCAL_LEARNED_NAME_SLOT"
            for row in learned_source
        ),
        "local_x": sum(
            row["boundary_class"] == "RUNNING_LEARNED_CORE"
            for row in learned_source
        ),
    }
    expected_semantic_partition = {
        "productive": 13593,
        "learned": 109,
        "learned_names": 107,
        "local_x": 2,
    }
    audit.check(
        "source_derived_productive_learned_partition",
        observed_semantic_partition == expected_semantic_partition,
        observed_semantic_partition,
        expected_semantic_partition,
    )
    kind_by_id = {
        row["slot_id"]: row["gdt582_default_kind"] for row in complete.rows
    }
    kind_partition_ok = all(
        kind_by_id[slot_id] == "PRODUCTIVE_REGISTER_FUNCTION"
        for slot_id in productive_ids
    ) and all(
        kind_by_id[row["slot_id"]]
        == (
            "CLASS_CONDITIONED_LEARNED_NAME"
            if row["boundary_class"] == "LOCAL_LEARNED_NAME_SLOT"
            else "OWNER_BOUND_LOCAL_X"
        )
        for row in learned_source
    )
    audit.check(
        "output_default_kinds_match_source_partition",
        kind_partition_ok,
        Counter(kind_by_id[row["slot_id"]] for row in source_content),
        {
            "PRODUCTIVE_REGISTER_FUNCTION": 13593,
            "CLASS_CONDITIONED_LEARNED_NAME": 107,
            "OWNER_BOUND_LOCAL_X": 2,
        },
    )

    # Re-derive the productive root inventory and every observed register cell.
    productive_roots = {row["slot_value"] for row in productive_source}
    source_cells: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    root_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in productive_source:
        root_members[row["slot_value"]].append(row)
        source_cells[(row["slot_value"], row["register"])].append(row)
    audit.check(
        "forty_two_productive_root_inventory",
        productive_roots == EXPECTED_ROOTS,
        productive_roots,
        EXPECTED_ROOTS,
    )
    audit.check(
        "one_hundred_eighty_one_observed_root_register_cells",
        len(source_cells) == 181,
        len(source_cells),
        181,
    )

    roots = outputs["roots"]
    root_by_key, root_duplicates = unique(roots.rows, "root")
    root_families = {
        root: {
            family_from_boundary(row["boundary_class"]) for row in members
        }
        for root, members in root_members.items()
    }
    root_row_errors: list[str] = []
    for root, members in root_members.items():
        row = root_by_key.get(root)
        families = root_families[root]
        if row is None or None in families or len(families) != 1:
            root_row_errors.append(root)
            continue
        expected = {
            "function_family": next(iter(families)),
            "slot_count": str(len(members)),
            "running_slot_count": str(
                sum(member["layer"] == "RUNNING_ATOM" for member in members)
            ),
            "local_slot_count": str(
                sum(member["layer"] == "LOCAL_COMPONENT" for member in members)
            ),
            "register_count": str(
                len({member["register"] for member in members})
            ),
            "registers": stable_join(member["register"] for member in members),
            "boundary_classes": stable_join(
                member["boundary_class"] for member in members
            ),
        }
        if any(row.get(field) != value for field, value in expected.items()):
            root_row_errors.append(root)
        if not nonempty(row.get("invariant_core_concept")) or not nonempty(
            row.get("universal_workshop_rival_de")
        ):
            root_row_errors.append(root)
    audit.check(
        "root_dictionary_rederived_statistics",
        not root_duplicates
        and set(root_by_key) == productive_roots
        and not root_row_errors,
        {
            "duplicates": root_duplicates,
            "key_difference": sorted(set(root_by_key) ^ productive_roots),
            "error_roots": sorted(set(root_row_errors))[:10],
        },
        {"duplicates": [], "key_difference": [], "error_roots": []},
    )

    cells = outputs["cells"]
    cell_counts = Counter((row["root"], row["register"]) for row in cells.rows)
    cell_by_key = {
        (row["root"], row["register"]): row for row in cells.rows
    }
    cell_errors: list[str] = []
    for key, members in source_cells.items():
        row = cell_by_key.get(key)
        root, _register = key
        if row is None:
            cell_errors.append(str(key))
            continue
        expected = {
            "function_family": root_by_key[root]["function_family"],
            "invariant_core_concept": root_by_key[root][
                "invariant_core_concept"
            ],
            "slot_count": str(len(members)),
            "physical_page_count": str(
                len({member["physical_page"] for member in members})
            ),
            "owner_count": str(len({member["owner"] for member in members})),
        }
        if any(row.get(field) != value for field, value in expected.items()):
            cell_errors.append(str(key))
        if not nonempty(row.get("concrete_default_de")) or not nonempty(
            row.get("realization_source")
        ):
            cell_errors.append(str(key))
    audit.check(
        "register_cell_keys_and_rederived_statistics",
        set(cell_by_key) == set(source_cells)
        and all(count == 1 for count in cell_counts.values())
        and not cell_errors,
        {
            "unique_keys": len(cell_by_key),
            "duplicate_keys": sum(count != 1 for count in cell_counts.values()),
            "key_difference": len(set(cell_by_key) ^ set(source_cells)),
            "error_count": len(set(cell_errors)),
            "sample": sorted(set(cell_errors))[:10],
        },
        {
            "unique_keys": 181,
            "duplicate_keys": 0,
            "key_difference": 0,
            "error_count": 0,
            "sample": [],
        },
    )
    observed_relations = {
        key: cell_by_key.get(key, {}).get("concrete_default_de", "")
        for key in EXPECTED_RELATION_REALIZATIONS
    }
    audit.check(
        "twenty_explicit_relation_realizations",
        observed_relations == EXPECTED_RELATION_REALIZATIONS,
        observed_relations,
        EXPECTED_RELATION_REALIZATIONS,
    )

    productive_mapping_errors: list[str] = []
    for source_row in productive_source:
        row = complete_by_id[source_row["slot_id"]]
        cell = cell_by_key[(source_row["slot_value"], source_row["register"])]
        root = root_by_key[source_row["slot_value"]]
        expected = {
            "gdt582_default_key": (
                f"FUNCTION:{source_row['slot_value']}:{source_row['register']}"
            ),
            "gdt582_default_kind": "PRODUCTIVE_REGISTER_FUNCTION",
            "gdt582_core_concept": root["invariant_core_concept"],
            "gdt582_concrete_default_de": cell["concrete_default_de"],
            "gdt582_default_basis": cell["realization_source"],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            productive_mapping_errors.append(source_row["slot_id"])
    audit.check(
        "all_productive_slots_resolve_to_their_root_register_cell",
        not productive_mapping_errors,
        {
            "error_count": len(productive_mapping_errors),
            "sample": productive_mapping_errors[:10],
        },
        {"error_count": 0, "sample": []},
    )

    # Learned names remain keyed by content class and raw core, not by a
    # portable root. Re-derive the eighty types from all 107 source spans.
    name_source = inputs["name_slots"]
    source_name_by_id, source_name_duplicates = unique(
        name_source.rows, "slot_id"
    )
    name_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in name_source.rows:
        name_groups[(row["content_class"], row["raw_name_core"])].append(row)
    names = outputs["names"]
    name_key_counts = Counter(
        (row["content_class"], row["raw_name_core"]) for row in names.rows
    )
    name_by_key = {
        (row["content_class"], row["raw_name_core"]): row for row in names.rows
    }
    name_table_errors: list[str] = []
    for key, members in name_groups.items():
        row = name_by_key.get(key)
        if row is None:
            name_table_errors.append(str(key))
            continue
        expected = {
            "occurrence_count": str(len(members)),
            "physical_pages": stable_join(
                member["physical_page"] for member in members
            ),
            "surfaces": stable_join(member["surface"] for member in members),
        }
        if any(row.get(field) != value for field, value in expected.items()):
            name_table_errors.append(str(key))
        if not all(
            nonempty(row.get(field))
            for field in (
                "name_default_id",
                "provisional_default_de",
                "default_basis",
            )
        ):
            name_table_errors.append(str(key))
    audit.check(
        "eighty_class_raw_core_name_defaults_from_107_occurrences",
        not source_name_duplicates
        and len(source_name_by_id) == 107
        and set(name_by_key) == set(name_groups)
        and len(name_by_key) == 80
        and all(count == 1 for count in name_key_counts.values())
        and not name_table_errors
        and {key[0] for key in name_groups} == EXPECTED_NAME_CLASSES,
        {
            "source_occurrences": len(source_name_by_id),
            "types": len(name_by_key),
            "classes": {key[0] for key in name_groups},
            "duplicate_keys": sum(
                count != 1 for count in name_key_counts.values()
            ),
            "errors": sorted(set(name_table_errors))[:10],
        },
        {
            "source_occurrences": 107,
            "types": 80,
            "classes": EXPECTED_NAME_CLASSES,
            "duplicate_keys": 0,
            "errors": [],
        },
    )
    name_slot_errors: list[str] = []
    for slot_id, source_name in source_name_by_id.items():
        source_slot = source_complete_by_id.get(slot_id)
        target_slot = complete_by_id.get(slot_id)
        default = name_by_key.get(
            (source_name["content_class"], source_name["raw_name_core"])
        )
        if source_slot is None or target_slot is None or default is None:
            name_slot_errors.append(slot_id)
            continue
        source_alignment = (
            source_slot["source_event_or_card_id"]
            == source_name["source_event_id"]
            and source_slot["slot_value"] == source_name["raw_name_core"]
            and source_slot["boundary_class"] == "LOCAL_LEARNED_NAME_SLOT"
            and source_slot["fill_status"] == "CONTENT_CARRIER"
            and source_slot["primary_governor_key"]
            == source_name["primary_governor_key"]
        )
        target_alignment = (
            target_slot["gdt582_default_key"] == default["name_default_id"]
            and target_slot["gdt582_default_kind"]
            == "CLASS_CONDITIONED_LEARNED_NAME"
            and target_slot["gdt582_core_concept"]
            == source_name["content_class"]
            and target_slot["gdt582_concrete_default_de"]
            == default["provisional_default_de"]
            and target_slot["gdt582_default_basis"] == default["default_basis"]
        )
        if not source_alignment or not target_alignment:
            name_slot_errors.append(slot_id)
    audit.check(
        "all_107_name_occurrences_resolve_to_class_raw_core_default",
        not name_slot_errors,
        {"error_count": len(name_slot_errors), "sample": name_slot_errors[:10]},
        {"error_count": 0, "sample": []},
    )

    local_x_rows = {
        row["slot_id"]: complete_by_id[row["slot_id"]]
        for row in learned_source
        if row["boundary_class"] == "RUNNING_LEARNED_CORE"
    }
    observed_local_x = {
        slot_id: (
            row["gdt582_core_concept"],
            row["gdt582_concrete_default_de"],
        )
        for slot_id, row in local_x_rows.items()
    }
    local_x_keys = {row["gdt582_default_key"] for row in local_x_rows.values()}
    audit.check(
        "two_distinct_owner_bound_local_x_cards",
        observed_local_x == EXPECTED_LOCAL_X
        and len(local_x_keys) == 2
        and all(
            row["gdt582_default_kind"] == "OWNER_BOUND_LOCAL_X"
            for row in local_x_rows.values()
        ),
        {"cards": observed_local_x, "default_keys": sorted(local_x_keys)},
        {"cards": EXPECTED_LOCAL_X, "distinct_default_key_count": 2},
    )

    # Controls are a disjoint structural partition and never enter the
    # productive dictionary or learned-name inventory.
    productive_root_set = set(root_by_key)
    control_roots = {row["slot_value"] for row in source_controls}
    control_semantics: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    control_errors: list[str] = []
    for source_row in source_controls:
        row = complete_by_id[source_row["slot_id"]]
        control_semantics[source_row["slot_value"]].add(
            (
                row["gdt582_core_concept"],
                row["gdt582_concrete_default_de"],
                row["gdt582_default_basis"],
            )
        )
        if (
            row["gdt582_default_kind"] != "STRUCTURAL_CONTROL_DEFAULT"
            or row["gdt582_default_key"]
            != f"CONTROL:{source_row['slot_value']}"
        ):
            control_errors.append(source_row["slot_id"])
    audit.check(
        "controls_remain_disjoint_and_root_consistent",
        not control_errors
        and not (control_roots & productive_root_set)
        and all(len(values) == 1 for values in control_semantics.values())
        and not any(
            row["gdt582_default_kind"] == "STRUCTURAL_CONTROL_DEFAULT"
            for row in target_content
        ),
        {
            "control_slots": len(source_controls),
            "control_roots": len(control_roots),
            "root_intersection": sorted(control_roots & productive_root_set),
            "inconsistent_control_roots": sorted(
                root
                for root, values in control_semantics.items()
                if len(values) != 1
            ),
            "slot_errors": control_errors[:10],
        },
        {
            "control_slots": 2187,
            "root_intersection": [],
            "inconsistent_control_roots": [],
            "slot_errors": [],
        },
    )

    # Alias rows are not slots. Every one must point to the same concrete
    # root/register card used by a written productive occurrence.
    alias_projection_ok, alias_mismatch_count, alias_mismatch_sample = (
        projection_mismatches(inputs["aliases"], outputs["aliases"], "alias_id")
    )
    alias_by_id, alias_duplicates = unique(outputs["aliases"].rows, "alias_id")
    alias_errors: list[str] = []
    for row in outputs["aliases"].rows:
        key = (row["inherited_root"], row["register"])
        cell = cell_by_key.get(key)
        if cell is None:
            alias_errors.append(row["alias_id"])
            continue
        expected = {
            "gdt582_default_key": (
                f"FUNCTION:{row['inherited_root']}:{row['register']}"
            ),
            "gdt582_core_concept": cell["invariant_core_concept"],
            "gdt582_inherited_default_de": cell["concrete_default_de"],
            "gdt582_default_basis": cell["realization_source"],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            alias_errors.append(row["alias_id"])
    audit.check(
        "all_4026_aliases_reuse_same_root_register_card",
        alias_projection_ok
        and not alias_duplicates
        and not alias_errors
        and "slot_id" not in outputs["aliases"].fields,
        {
            "rows": len(alias_by_id),
            "projection_mismatches": alias_mismatch_count,
            "projection_sample": alias_mismatch_sample,
            "duplicates": alias_duplicates[:10],
            "mapping_errors": alias_errors[:10],
            "has_slot_id_column": "slot_id" in outputs["aliases"].fields,
        },
        {
            "rows": 4026,
            "projection_mismatches": 0,
            "projection_sample": [],
            "duplicates": [],
            "mapping_errors": [],
            "has_slot_id_column": False,
        },
    )

    # Running events: exact GDT581 identity plus a trace containing each and
    # only each complete running slot once.
    event_projection_ok, event_mismatch_count, event_mismatch_sample = (
        projection_mismatches(inputs["events"], outputs["events"], "event_id")
    )
    event_by_id, event_duplicates = unique(outputs["events"].rows, "event_id")
    running_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete.rows:
        if row["layer"] == "RUNNING_ATOM":
            running_by_event[row["source_event_or_card_id"]].append(row)
    event_errors: list[str] = []
    global_event_trace_ids: list[str] = []
    for event_id, event in event_by_id.items():
        members = running_by_event.get(event_id, [])
        traced = trace_slot_ids(event.get("concrete_slot_trace_de", ""))
        global_event_trace_ids.extend(traced)
        expected_counts = row_counts(members)
        actual_counts = (
            int(event.get("complete_slot_count", "-1")),
            int(event.get("content_slot_count", "-1")),
            int(event.get("control_slot_count", "-1")),
        )
        if (
            not members
            or event.get("concrete_slot_trace_de") != trace_for(members)
            or Counter(traced) != Counter(row["slot_id"] for row in members)
            or actual_counts != expected_counts
            or event.get("gdt581_exact_roundtrip_de")
            != event.get("content_ready_boundary_clause_de")
            or not nonempty(event.get("concrete_working_clause_de"))
        ):
            event_errors.append(event_id)
    source_event_ids = {row["event_id"] for row in inputs["events"].rows}
    global_running_ids = [
        row["slot_id"] for row in complete.rows if row["layer"] == "RUNNING_ATOM"
    ]
    audit.check(
        "all_5122_event_traces_are_exact_and_complete",
        event_projection_ok
        and not event_duplicates
        and set(running_by_event) == source_event_ids
        and not event_errors
        and Counter(global_event_trace_ids) == Counter(global_running_ids),
        {
            "events": len(event_by_id),
            "projection_mismatches": event_mismatch_count,
            "projection_sample": event_mismatch_sample,
            "event_group_difference": len(set(running_by_event) ^ source_event_ids),
            "trace_errors": len(event_errors),
            "sample": event_errors[:10],
            "globally_traced_slots": len(global_event_trace_ids),
        },
        {
            "events": 5122,
            "projection_mismatches": 0,
            "projection_sample": [],
            "event_group_difference": 0,
            "trace_errors": 0,
            "sample": [],
            "globally_traced_slots": 13809,
        },
    )

    # Statements retain exact event lists and are a deterministic join of
    # precisely those concrete event clauses.
    (
        statement_projection_ok,
        statement_mismatch_count,
        statement_mismatch_sample,
    ) = projection_mismatches(
        inputs["statements"], outputs["statements"], "statement_id"
    )
    statement_by_id, statement_duplicates = unique(
        outputs["statements"].rows, "statement_id"
    )
    statement_errors: list[str] = []
    globally_used_events: list[str] = []
    for statement_id, statement in statement_by_id.items():
        event_ids = (
            statement["event_ids"].split("|") if statement["event_ids"] else []
        )
        globally_used_events.extend(event_ids)
        if any(event_id not in event_by_id for event_id in event_ids):
            statement_errors.append(statement_id)
            continue
        member_events = [event_by_id[event_id] for event_id in event_ids]
        expected_reading = " ".join(
            event["concrete_working_clause_de"] for event in member_events
        )
        expected_counts = (
            sum(int(event["complete_slot_count"]) for event in member_events),
            sum(int(event["content_slot_count"]) for event in member_events),
            sum(int(event["control_slot_count"]) for event in member_events),
        )
        actual_counts = (
            int(statement.get("complete_slot_count", "-1")),
            int(statement.get("content_slot_count", "-1")),
            int(statement.get("control_slot_count", "-1")),
        )
        if (
            statement.get("concrete_working_reading_de") != expected_reading
            or actual_counts != expected_counts
            or statement.get("gdt581_exact_roundtrip_de")
            != statement.get("grammar_content_boundary_reading_de")
            or any(event["statement_id"] != statement_id for event in member_events)
            or len(event_ids) != int(statement["event_count"])
        ):
            statement_errors.append(statement_id)
    audit.check(
        "all_793_statements_use_unchanged_exact_event_lists",
        statement_projection_ok
        and not statement_duplicates
        and not statement_errors
        and Counter(globally_used_events) == Counter(event_by_id.keys()),
        {
            "statements": len(statement_by_id),
            "projection_mismatches": statement_mismatch_count,
            "projection_sample": statement_mismatch_sample,
            "composition_errors": len(statement_errors),
            "sample": statement_errors[:10],
            "event_references": len(globally_used_events),
        },
        {
            "statements": 793,
            "projection_mismatches": 0,
            "projection_sample": [],
            "composition_errors": 0,
            "sample": [],
            "event_references": 5122,
        },
    )

    # Local cards use all non-running complete slots. Name spans are extra
    # complete slots beside the component_count inherited from GDT581.
    local_projection_ok, local_mismatch_count, local_mismatch_sample = (
        projection_mismatches(
            inputs["local_cards"],
            outputs["local_cards"],
            "local_card_host_key",
        )
    )
    local_by_key, local_duplicates = unique(
        outputs["local_cards"].rows, "local_card_host_key"
    )
    local_event_counts = Counter(
        row["source_event_id"] for row in outputs["local_cards"].rows
    )
    local_by_event = {
        row["source_event_id"]: row for row in outputs["local_cards"].rows
    }
    local_slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete.rows:
        if row["layer"] != "RUNNING_ATOM":
            local_slots_by_event[row["source_event_or_card_id"]].append(row)
    local_errors: list[str] = []
    global_local_trace_ids: list[str] = []
    for source_event_id, card in local_by_event.items():
        members = local_slots_by_event.get(source_event_id, [])
        traced = trace_slot_ids(card.get("concrete_slot_trace_de", ""))
        global_local_trace_ids.extend(traced)
        expected_counts = row_counts(members)
        actual_counts = (
            int(card.get("complete_slot_count", "-1")),
            int(card.get("content_slot_count", "-1")),
            int(card.get("control_slot_count", "-1")),
        )
        component_count = sum(
            row["layer"] == "LOCAL_COMPONENT" for row in members
        )
        if (
            not members
            or card.get("concrete_slot_trace_de") != trace_for(members)
            or Counter(traced) != Counter(row["slot_id"] for row in members)
            or actual_counts != expected_counts
            or component_count != int(card["component_count"])
            or not nonempty(card.get("concrete_working_clause_de"))
        ):
            local_errors.append(source_event_id)
    source_local_event_ids = {
        row["source_event_id"] for row in inputs["local_cards"].rows
    }
    global_local_ids = [
        row["slot_id"] for row in complete.rows if row["layer"] != "RUNNING_ATOM"
    ]
    name_card_errors = [
        row["slot_id"]
        for row in name_source.rows
        if row["local_card_host_key"] not in local_by_key
        or local_by_key[row["local_card_host_key"]]["source_event_id"]
        != row["source_event_id"]
    ]
    audit.check(
        "all_744_local_cards_are_complete",
        local_projection_ok
        and not local_duplicates
        and all(count == 1 for count in local_event_counts.values())
        and len(local_by_event) == 744
        and set(local_slots_by_event) == source_local_event_ids
        and not local_errors
        and not name_card_errors
        and Counter(global_local_trace_ids) == Counter(global_local_ids),
        {
            "cards": len(local_by_key),
            "projection_mismatches": local_mismatch_count,
            "projection_sample": local_mismatch_sample,
            "duplicate_source_events": sum(
                count != 1 for count in local_event_counts.values()
            ),
            "card_group_difference": len(
                set(local_slots_by_event) ^ source_local_event_ids
            ),
            "trace_or_count_errors": len(local_errors),
            "name_card_errors": len(name_card_errors),
            "globally_traced_slots": len(global_local_trace_ids),
        },
        {
            "cards": 744,
            "projection_mismatches": 0,
            "projection_sample": [],
            "duplicate_source_events": 0,
            "card_group_difference": 0,
            "trace_or_count_errors": 0,
            "name_card_errors": 0,
            "globally_traced_slots": 2080,
        },
    )

    # Page profiles must be the same thirty pages and independently sum every
    # slot class and alias assignment on each page.
    page_projection_ok, page_mismatch_count, page_mismatch_sample = (
        projection_mismatches(inputs["pages"], outputs["pages"], "physical_page")
    )
    page_by_id, page_duplicates = unique(outputs["pages"].rows, "physical_page")
    aliases_per_page = Counter(
        row["physical_page"] for row in outputs["aliases"].rows
    )
    page_errors: list[str] = []
    for physical_page, page in page_by_id.items():
        members = [
            row for row in complete.rows if row["physical_page"] == physical_page
        ]
        expected = {
            "complete_default_slot_count": str(len(members)),
            "content_default_slot_count": str(
                sum(row["fill_status"] == "CONTENT_CARRIER" for row in members)
            ),
            "control_default_slot_count": str(
                sum(row["fill_status"] == "CONTROL_HOST_ONLY" for row in members)
            ),
            "productive_function_slot_count": str(
                sum(row["slot_id"] in productive_ids for row in members)
            ),
            "learned_content_slot_count": str(
                sum(row["slot_id"] in learned_ids for row in members)
            ),
            "alias_default_count": str(aliases_per_page[physical_page]),
        }
        if any(page.get(field) != value for field, value in expected.items()):
            page_errors.append(physical_page)
    page_universe = {row["physical_page"] for row in complete.rows}
    audit.check(
        "thirty_page_membership_and_counts_rederived",
        page_projection_ok
        and not page_duplicates
        and set(page_by_id) == page_universe
        and not page_errors,
        {
            "pages": len(page_by_id),
            "projection_mismatches": page_mismatch_count,
            "projection_sample": page_mismatch_sample,
            "universe_difference": sorted(set(page_by_id) ^ page_universe),
            "count_errors": page_errors[:10],
        },
        {
            "pages": 30,
            "projection_mismatches": 0,
            "projection_sample": [],
            "universe_difference": [],
            "count_errors": [],
        },
    )

    # Manual decks point into the already validated full editions: five and
    # four complete readings per register.
    event_checks = outputs["event_checks"].rows
    event_check_ids = [row["event_id"] for row in event_checks]
    event_check_errors: list[str] = []
    for row in event_checks:
        event = event_by_id.get(row["event_id"])
        if event is None:
            event_check_errors.append(row["event_id"])
            continue
        expected = {
            "physical_page": event["physical_page"],
            "register": event["register"],
            "surface": event["surface"],
            "recipe": event["final_context_recipe"],
            "gdt581_structural_clause_de": event[
                "content_ready_boundary_clause_de"
            ],
            "gdt582_concrete_clause_de": event["concrete_working_clause_de"],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            event_check_errors.append(row["event_id"])
    event_register_counts = Counter(row["register"] for row in event_checks)
    audit.check(
        "twenty_five_event_checks_five_per_register",
        len(set(event_check_ids)) == 25
        and event_register_counts == {register: 5 for register in REGISTERS}
        and not event_check_errors
        and all(
            row["manual_house_sense_disposition"] == "KEEP_REGISTER_HYBRID"
            for row in event_checks
        ),
        {
            "unique_events": len(set(event_check_ids)),
            "registers": event_register_counts,
            "errors": event_check_errors[:10],
        },
        {
            "unique_events": 25,
            "registers": {register: 5 for register in REGISTERS},
            "errors": [],
        },
    )

    passage_checks = outputs["passage_checks"].rows
    passage_ids = [row["statement_id"] for row in passage_checks]
    passage_errors: list[str] = []
    for row in passage_checks:
        statement = statement_by_id.get(row["statement_id"])
        if statement is None:
            passage_errors.append(row["statement_id"])
            continue
        expected = {
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_id": statement["owner_id"],
            "event_count": statement["event_count"],
            "surface_sequence": statement["surface_sequence"],
            "gdt581_structural_reading_de": statement[
                "grammar_content_boundary_reading_de"
            ],
            "gdt582_concrete_reading_de": statement[
                "concrete_working_reading_de"
            ],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            passage_errors.append(row["statement_id"])
    passage_register_counts = Counter(
        row["register"] for row in passage_checks
    )
    audit.check(
        "twenty_complete_statements_four_per_register",
        len(set(passage_ids)) == 20
        and passage_register_counts == {register: 4 for register in REGISTERS}
        and not passage_errors
        and all(
            row["manual_house_sense_disposition"] == "KEEP_REGISTER_HYBRID"
            for row in passage_checks
        ),
        {
            "unique_statements": len(set(passage_ids)),
            "registers": passage_register_counts,
            "errors": passage_errors[:10],
        },
        {
            "unique_statements": 20,
            "registers": {register: 4 for register in REGISTERS},
            "errors": [],
        },
    )

    packs = outputs["packs"].rows
    pack_by_id, pack_duplicates = unique(packs, "pack_id")
    selected_rows = [
        row
        for row in packs
        if row.get("whole_passage_result", "").startswith("SELECTED")
    ]
    pack_coverage_errors = [
        row["pack_id"]
        for row in packs
        if int(row["total_content_slot_coverage"]) != 13702
    ]
    selected_pack = pack_by_id.get("REGISTER_HYBRID_CODEBOOK", {})
    audit.check(
        "selected_register_hybrid_pack",
        not pack_duplicates
        and len(pack_by_id) == 4
        and len(selected_rows) == 1
        and selected_rows[0]["pack_id"] == "REGISTER_HYBRID_CODEBOOK"
        and selected_pack.get("pack_rank") == "1"
        and selected_pack.get("productive_slot_coverage") == "13593"
        and selected_pack.get("learned_slot_coverage") == "109"
        and selected_pack.get("dictionary_or_cell_count") == "305"
        and not pack_coverage_errors
        and result.get("selected_pack") == "REGISTER_HYBRID_CODEBOOK",
        {
            "pack_ids": sorted(pack_by_id),
            "selected_rows": [row["pack_id"] for row in selected_rows],
            "result_selected_pack": result.get("selected_pack"),
            "coverage_errors": pack_coverage_errors,
        },
        {
            "pack_count": 4,
            "selected_rows": ["REGISTER_HYBRID_CODEBOOK"],
            "result_selected_pack": "REGISTER_HYBRID_CODEBOOK",
            "coverage_errors": [],
        },
    )

    expected_result_metrics = {
        "complete_defaults": 15889,
        "content_defaults": 13702,
        "control_defaults": 2187,
        "productive_function_slots": 13593,
        "learned_content_slots": 109,
        "core_stems": 42,
        "register_realization_cells": 181,
        "learned_name_types": 80,
        "alias_defaults": 4026,
        "events": 5122,
        "statements": 793,
        "local_cards": 744,
        "pages": 30,
        "sense_checks": 25,
        "complete_passage_checks": 20,
        "candidate_packs": 4,
    }
    observed_result_metrics = {
        key: result.get(key) for key in expected_result_metrics
    }
    audit.check(
        "result_metrics_match_independent_counts",
        result.get("experiment_id") == "GDT582"
        and observed_result_metrics == expected_result_metrics
        and str(result.get("status", "")).startswith("PASS_"),
        {
            "experiment_id": result.get("experiment_id"),
            "metrics": observed_result_metrics,
            "status": result.get("status"),
        },
        {
            "experiment_id": "GDT582",
            "metrics": expected_result_metrics,
            "status_prefix": "PASS_",
        },
    )

    # Scan data rows and rendered output. The manifest and method intentionally
    # name the forbidden folios as boundaries, so they are not data payloads.
    forbidden = re.compile(r"f84r?", re.IGNORECASE)
    forbidden_hits: list[str] = []
    for group_name, tables in (("input", inputs), ("output", outputs)):
        for table_name, table in tables.items():
            for row_number, row in enumerate(table.rows, 1):
                for field, value in row.items():
                    if forbidden.search(value or ""):
                        forbidden_hits.append(
                            f"{group_name}:{table_name}:{row_number}:{field}"
                        )
    for payload_name, payload in (
        ("result", result_path.read_text(encoding="utf-8")),
        (
            "book",
            (
                ART / "GDT582_CONCRETE_DEFAULT_THIRTY_PAGE_EDITION.md"
            ).read_text(encoding="utf-8"),
        ),
    ):
        if forbidden.search(payload):
            forbidden_hits.append(payload_name)
    audit.check(
        "forbidden_folio_absent_from_all_data_strings",
        not forbidden_hits,
        {"hit_count": len(forbidden_hits), "sample": forbidden_hits[:10]},
        {"hit_count": 0, "sample": []},
    )


def validation_payload(audit: Audit) -> dict[str, Any]:
    failures = audit.failures
    return {
        "experiment_id": "GDT582",
        "validator": "INDEPENDENT_GDT581_SOURCE_REDERIVATION",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(audit.checks),
        "pass_count": len(audit.checks) - len(failures),
        "fail_count": len(failures),
        "checks": audit.checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ART / "gdt582_validation.json",
        help="JSON validation artifact (default: GDT582 artifacts directory)",
    )
    args = parser.parse_args()
    audit = Audit()
    try:
        validate(audit)
    except Exception as exc:  # fail closed while still producing JSON
        audit.check(
            "validator_runtime",
            False,
            f"{type(exc).__name__}: {exc}",
            "NO_EXCEPTION",
        )
    payload = validation_payload(audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
