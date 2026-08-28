#!/usr/bin/env python3
"""Independent source/projection audit for GDT585.

This validator deliberately imports neither ``run.py`` nor ``model.py``. It
reconstructs the admitted type, slot, label, repeated-star, image and GDT476
grammar populations directly from frozen upstream TSV files. Passing means the
exploratory atlas is complete and source-faithful, not that a lexeme is proven.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas"
ART = BASE / "artifacts"
G459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"

INPUTS = {
    "name_slots": G581 / "gdt581_107_name_core_slots.tsv",
    "name_types": G582 / "gdt582_80_learned_name_defaults.tsv",
    "content_slots": G582 / "gdt582_13702_content_slot_defaults.tsv",
    "concrete_statements": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "event_triptych": G474 / "gdt474_183_event_meaning_triptych.tsv",
    "tie_decisions": G476 / "gdt476_64_tie_context_decisions.tsv",
    "address_interlinear": G459 / "gdt459_183_address_interlinear.tsv",
    "polished_statements": G584 / "gdt584_591_polished_statement_edition.tsv",
}
OUTPUTS = {
    "types": ART / "gdt585_80_reconciled_name_types.tsv",
    "slots": ART / "gdt585_109_owner_content_slot_assignments.tsv",
    "labels": ART / "gdt585_89_concrete_name_label_edition.tsv",
    "compounds": ART / "gdt585_19_compound_and_pair_readings.tsv",
    "families": ART / "gdt585_5_compositional_family_leads.tsv",
    "local_x": ART / "gdt585_2_local_x_contexts.tsv",
    "history": ART / "gdt585_10_historical_analogy_cards.tsv",
    "images": ART / "gdt585_4_manual_image_cards.tsv",
}
BOOK = ART / "GDT585_CONCRETE_NAME_BOOK.md"
MANUAL_AUDIT = ART / "GDT585_MANUAL_NAME_AUDIT.md"
RESULT = ART / "gdt585_result.json"
VALIDATION = ART / "gdt585_validation.json"

# Exact upstream editions admitted by this experiment.
EXPECTED_INPUT_SHA256 = {
    "name_slots": "9011dc01a9e141bf7d202bd290805b0da0a3bd2ce3a88e8e2b2b03e3300b9d6a",
    "name_types": "54405aa2567addd6a99ecc1e189bc9a818b5430d12839610b5634cad681ca3cc",
    "content_slots": "bfe8005166f784ca4c8346c1e15eec6c0bb810f3a0d1d0647be3d4e8ed9874e3",
    "concrete_statements": "e8d4ab7411a56f9e71daf56eea074981f85fd31fd8fae748746b339ad0ec4482",
    "event_triptych": "a221ab715e7af5b2f680f37eb09273b1240e02fe176ad81d1e13b5e0f4d1d052",
    "tie_decisions": "a40109a0ad37a751bde6f1bad2e6a2e9203240c7f1dfab089ef7fd4957edfe53",
    "address_interlinear": "1668013305dc419fa29c77087248685711e25bb74086a7a592704cb5ffae77ec",
    "polished_statements": "753f4822aa83d309d9a2e93cf004e05cc1d0c6177016e74966a86a62a416eb42",
}
EXPECTED_ROWS = {
    "types": 80, "slots": 109, "labels": 89, "compounds": 19,
    "families": 5, "local_x": 2, "history": 10, "images": 4,
}
EXPECTED_TYPE_CLASSES = {
    "STAR_BEARING_RING_POSITION": 43,
    "DRUG_OR_INGREDIENT_OBJECT": 29,
    "BATH_OR_OUTLET_STATION": 6,
    "PICTURED_PLANT": 2,
}
EXPECTED_NAME_SLOT_CLASSES = {
    "STAR_BEARING_RING_POSITION": 60,
    "DRUG_OR_INGREDIENT_OBJECT": 38,
    "BATH_OR_OUTLET_STATION": 7,
    "PICTURED_PLANT": 2,
}
EXPECTED_LABEL_CLASSES = {
    "STAR_BEARING_RING_POSITION": 52,
    "DRUG_OR_INGREDIENT_OBJECT": 30,
    "BATH_OR_OUTLET_STATION": 5,
    "PICTURED_PLANT": 2,
}
LOCAL_X_DEFAULTS = {
    "RUNNING:G515-E0410@2": ("INDICATION_OR_ILLNESS", "Beschwerde"),
    "RUNNING:G515-E0438@2": ("REMEDY_OR_HEALING", "Heilmittel"),
}
EXPECTED_CHANGED_BUNDLES = {
    "G474-B061": "INSTRUCTION", "G474-B071": "INSTRUCTION",
    "G474-B072": "INSTRUCTION", "G474-B090": "COORDINATE",
    "G474-B115": "INSTRUCTION", "G474-B116": "INSTRUCTION",
}
EXPECTED_FAMILIES = {
    "GDT585-F01": {"or", "ora"},
    "GDT585-F02": {"cheo", "cheosdy"},
    "GDT585-F03": {"cho", "opchos", "opchor", "dchos"},
    "GDT585-F04": {"d", "dy"},
    "GDT585-F05": {"d", "da", "s", "sy", "y", "oiin", "e", "yt", "em"},
}
EXPECTED_HISTORY_URLS = {
    "GDT585-H01": "https://wellcomecollection.org/works/nuckbt25",
    "GDT585-H02": "https://wellcomecollection.org/works/w6ne7k4t",
    "GDT585-H03": "https://wellcomecollection.org/works/actgjagb",
    "GDT585-H04": "https://wellcomecollection.org/works/abjb4cfh",
    "GDT585-H05": "https://wellcomecollection.org/works/f6nzyzh4",
    "GDT585-H06": "https://searcharchives.bl.uk/catalog/040-002116409",
    "GDT585-H07": "https://wellcomecollection.org/works/yuykkdvs",
    "GDT585-H08": "https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Royal_MS_17_A_XVI",
    "GDT585-H09": "https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Add_MS_46143",
    "GDT585-H10": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006233",
}
ALLOWED_HISTORY_DOMAINS = {
    "wellcomecollection.org", "searcharchives.bl.uk", "www.bl.uk",
    "collections.library.yale.edu",
}
EXPECTED_IMAGES = {
    "1006106": (
        "https://collections.library.yale.edu/iiif/2/1006106/full/2000,/0/default.jpg",
        "eccb822a72a8c27045aefa4f19d558dba29ef046c1d8e3772c715a99ee7113b9", 2, 2,
    ),
    "1006203": (
        "https://collections.library.yale.edu/iiif/2/1006203/full/3000,/0/default.jpg",
        "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93", 52, 60,
    ),
    "1006212": (
        "https://collections.library.yale.edu/iiif/2/1006212/full/2000,/0/default.jpg",
        "6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df", 5, 7,
    ),
    "1006233": (
        "https://collections.library.yale.edu/iiif/2/1006233/full/3000,/0/default.jpg",
        "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c", 30, 38,
    ),
}


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


def serial(value_: Any) -> Any:
    if isinstance(value_, Counter):
        value_ = dict(value_)
    if isinstance(value_, defaultdict):
        value_ = dict(value_)
    if isinstance(value_, dict):
        return {str(k): serial(v) for k, v in sorted(value_.items(), key=lambda item: str(item[0]))}
    if isinstance(value_, set):
        return sorted(serial(v) for v in value_)
    if isinstance(value_, (tuple, list)):
        return [serial(v) for v in value_]
    return value_


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, check_id: str, condition: bool, observed: Any, expected: Any) -> None:
        self.checks.append({
            "check_id": check_id,
            "status": "PASS" if condition else "FAIL",
            "observed": serial(observed),
            "expected": serial(expected),
        })

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [row for row in self.checks if row["status"] == "FAIL"]


def value(row: dict[str, str], *candidates: str) -> str:
    for candidate in candidates:
        if candidate in row:
            return row[candidate]
    return ""


def split_values(raw: str) -> list[str]:
    if not raw or raw == "NONE":
        return []
    return [part.strip() for part in raw.split("|") if part.strip() and part.strip() != "NONE"]


def int_value(row: dict[str, str], *candidates: str) -> int:
    try:
        return int(value(row, *candidates))
    except (TypeError, ValueError):
        return -1


def unique_by(
    rows: Iterable[dict[str, str]], candidates: tuple[str, ...]
) -> tuple[dict[str, dict[str, str]], list[str]]:
    source = list(rows)
    keys = [value(row, *candidates) for row in source]
    counts = Counter(keys)
    duplicates = sorted(key for key, count in counts.items() if not key or count != 1)
    return {key: row for key, row in zip(keys, source)}, duplicates


def selected_event_reading(row: dict[str, str], model: str) -> str:
    columns = {
        "COORDINATE": "coordinate_event_reading_de",
        "INSTRUCTION": "instruction_event_reading_de",
        "CATALOGUE": "catalogue_event_reading_de",
    }
    return row[columns[model]]


def page_tokens(row: dict[str, str], fields: Iterable[str]) -> Iterable[str]:
    for field in fields:
        if field in row:
            yield from (
                token.strip().lower()
                for token in re.split(r"[|,; ]+", row[field])
                if token.strip()
            )


def main() -> int:
    audit = Audit()
    inputs = {name: Table(path) for name, path in INPUTS.items()}
    outputs = {name: Table(path) for name, path in OUTPUTS.items()}
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    input_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    audit.check("pinned_input_sha256", input_hashes == EXPECTED_INPUT_SHA256, input_hashes, EXPECTED_INPUT_SHA256)
    audit.check("result_input_sha256", result.get("input_sha256") == input_hashes, result.get("input_sha256"), input_hashes)
    output_paths = {**OUTPUTS, "book": BOOK, "audit": MANUAL_AUDIT}
    output_hashes = {name: sha256(path) for name, path in output_paths.items()}
    audit.check("result_output_sha256", result.get("output_sha256") == output_hashes, result.get("output_sha256"), output_hashes)
    output_counts = {name: len(table.rows) for name, table in outputs.items()}
    audit.check("output_row_counts", output_counts == EXPECTED_ROWS, output_counts, EXPECTED_ROWS)

    source_name_rows = inputs["name_slots"].rows
    source_type_rows = inputs["name_types"].rows
    source_name_by_id, source_name_duplicates = unique_by(source_name_rows, ("slot_id",))
    source_type_by_id, source_type_duplicates = unique_by(source_type_rows, ("name_default_id",))
    audit.check(
        "source_populations",
        len(source_name_rows) == 107 and len(source_type_rows) == 80
        and not source_name_duplicates and not source_type_duplicates,
        {"name_slots": len(source_name_rows), "name_types": len(source_type_rows),
         "name_duplicates": source_name_duplicates, "type_duplicates": source_type_duplicates},
        {"name_slots": 107, "name_types": 80, "name_duplicates": [], "type_duplicates": []},
    )
    source_type_counts = Counter(row["content_class"] for row in source_type_rows)
    source_slot_counts = Counter(row["content_class"] for row in source_name_rows)
    audit.check("source_type_class_counts", source_type_counts == EXPECTED_TYPE_CLASSES, source_type_counts, EXPECTED_TYPE_CLASSES)
    audit.check("source_name_slot_class_counts", source_slot_counts == EXPECTED_NAME_SLOT_CLASSES, source_slot_counts, EXPECTED_NAME_SLOT_CLASSES)

    type_rows = outputs["types"].rows
    type_by_id, type_duplicates = unique_by(
        type_rows,
        ("name_default_id", "source_name_default_id", "gdt582_name_default_id"),
    )
    type_ids_same = list(type_by_id) == list(source_type_by_id)
    type_projection_failures: list[str] = []
    for type_id, old in source_type_by_id.items():
        new = type_by_id.get(type_id, {})
        comparisons = {
            "content_class": value(new, "content_class"),
            "raw_name_core": value(new, "raw_name_core"),
            "occurrence_count": value(new, "occurrence_count"),
            "physical_pages": value(new, "physical_pages"),
            "surfaces": value(new, "surfaces"),
            "old_default": value(
                new, "gdt582_default_de", "gdt582_provisional_default_de",
                "old_provisional_default_de", "provisional_default_de",
            ),
        }
        expected = {
            "content_class": old["content_class"], "raw_name_core": old["raw_name_core"],
            "occurrence_count": old["occurrence_count"], "physical_pages": old["physical_pages"],
            "surfaces": old["surfaces"], "old_default": old["provisional_default_de"],
        }
        if comparisons != expected:
            type_projection_failures.append(type_id)
    audit.check(
        "type_identity_and_exact_projection",
        not type_duplicates and type_ids_same and not type_projection_failures,
        {"duplicates": type_duplicates, "same_order": type_ids_same, "mismatches": type_projection_failures[:20]},
        {"duplicates": [], "same_order": True, "mismatches": []},
    )
    type_class_counts = Counter(value(row, "content_class") for row in type_rows)
    audit.check("reconciled_type_class_counts", type_class_counts == EXPECTED_TYPE_CLASSES, type_class_counts, EXPECTED_TYPE_CLASSES)
    empty_type_meanings = [
        value(row, "name_default_id", "source_name_default_id", "gdt582_name_default_id")
        for row in type_rows
        if not value(
            row, "gdt585_default_de", "gdt585_primary_default_de",
            "reconciled_default_de", "default_de",
        ).strip()
    ]
    audit.check("all_80_types_have_meaning", not empty_type_meanings, empty_type_meanings, [])

    star_slot_counts = Counter(
        row["raw_name_core"] for row in source_name_rows
        if row["content_class"] == "STAR_BEARING_RING_POSITION"
    )
    repeated_star = {core: count for core, count in star_slot_counts.items() if count > 1}
    expected_repeated_star = {"op": 3, "dy": 4, "o": 3, "yt": 2, "ch": 3, "y": 4, "e": 2, "k": 2, "yk": 2, "f": 2}
    audit.check(
        "repeated_star_source_population",
        repeated_star == expected_repeated_star,
        {"types": len(repeated_star), "slots": sum(repeated_star.values()), "counts": repeated_star},
        {"types": 10, "slots": 27, "counts": expected_repeated_star},
    )
    published_repeated_star = {
        value(row, "raw_name_core"): int_value(row, "occurrence_count") for row in type_rows
        if value(row, "content_class") == "STAR_BEARING_RING_POSITION"
        and int_value(row, "occurrence_count") > 1
    }
    audit.check("published_repeated_star_population", published_repeated_star == repeated_star, published_repeated_star, repeated_star)

    content_by_id, content_duplicates = unique_by(inputs["content_slots"].rows, ("slot_id",))
    local_x_sources = {slot_id: content_by_id.get(slot_id, {}) for slot_id in LOCAL_X_DEFAULTS}
    slot_rows = outputs["slots"].rows
    slot_by_id, slot_duplicates = unique_by(slot_rows, ("slot_id",))
    expected_slot_order = [row["slot_id"] for row in source_name_rows] + list(LOCAL_X_DEFAULTS)
    published_slot_order = [value(row, "slot_id") for row in slot_rows]
    audit.check(
        "owner_slot_identity", not slot_duplicates and published_slot_order == expected_slot_order,
        {"duplicates": slot_duplicates, "same_order": published_slot_order == expected_slot_order},
        {"duplicates": [], "same_order": True},
    )
    name_slot_projection_failures: list[str] = []
    for slot_id, old in source_name_by_id.items():
        new = slot_by_id.get(slot_id, {})
        comparisons = (
            value(new, "source_event_id", "source_event_or_card_id"), value(new, "physical_page"),
            value(new, "register"), value(new, "locus"), value(new, "surface"),
            value(new, "raw_name_core"), value(new, "content_class"),
            value(new, "name_slot_in_label", "slot_in_label"),
        )
        expected = (
            old["source_event_id"], old["physical_page"], old["register"], old["locus"],
            old["surface"], old["raw_name_core"], old["content_class"], old["name_slot_in_label"],
        )
        if comparisons != expected:
            name_slot_projection_failures.append(slot_id)
    audit.check("107_name_slot_exact_projection", not name_slot_projection_failures, name_slot_projection_failures[:20], [])

    local_x_projection_failures: list[str] = []
    for slot_id, (concept, default_de) in LOCAL_X_DEFAULTS.items():
        old = local_x_sources[slot_id]
        new = slot_by_id.get(slot_id, {})
        fixed = (
            value(new, "source_event_id", "source_event_or_card_id"), value(new, "physical_page"),
            value(new, "register"), value(new, "owner", "owner_de"), value(new, "surface"),
            value(new, "slot_value", "raw_name_core"),
        )
        expected = (
            old.get("source_event_or_card_id", ""), old.get("physical_page", ""),
            old.get("register", ""), old.get("owner", ""), old.get("surface", ""), "LOCAL_X",
        )
        if (fixed != expected
                or value(new, "semantic_family", "gdt582_core_concept", "core_concept") != concept
                or value(
                    new, "gdt585_default_de", "gdt585_primary_default_de",
                    "reconciled_default_de", "default_de",
                ) != default_de):
            local_x_projection_failures.append(slot_id)
    audit.check(
        "2_local_x_exact_projection_and_defaults",
        not content_duplicates and not local_x_projection_failures,
        {"source_duplicates": content_duplicates[:20], "mismatches": local_x_projection_failures},
        {"source_duplicates": [], "mismatches": []},
    )
    empty_slot_meanings = [
        row_id for row_id, row in slot_by_id.items()
        if not value(
            row, "gdt585_default_de", "gdt585_primary_default_de",
            "reconciled_default_de", "default_de",
        ).strip()
    ]
    audit.check("all_109_slots_have_meaning", not empty_slot_meanings, empty_slot_meanings, [])

    name_slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_name_rows:
        name_slots_by_event[row["source_event_id"]].append(row)
    for rows in name_slots_by_event.values():
        rows.sort(key=lambda row: int(row["name_slot_in_label"]))
    source_label_ids = list(name_slots_by_event)
    source_label_classes = Counter(rows[0]["content_class"] for rows in name_slots_by_event.values())
    audit.check(
        "source_89_label_population",
        len(source_label_ids) == 89 and source_label_classes == EXPECTED_LABEL_CLASSES,
        {"labels": len(source_label_ids), "classes": source_label_classes},
        {"labels": 89, "classes": EXPECTED_LABEL_CLASSES},
    )
    label_rows = outputs["labels"].rows
    label_by_event, label_duplicates = unique_by(label_rows, ("source_event_id", "event_id"))
    published_label_order = [value(row, "source_event_id", "event_id") for row in label_rows]
    audit.check(
        "label_identity_and_order", not label_duplicates and published_label_order == source_label_ids,
        {"duplicates": label_duplicates, "same_order": published_label_order == source_label_ids},
        {"duplicates": [], "same_order": True},
    )

    triptych_by_event, triptych_duplicates = unique_by(inputs["event_triptych"].rows, ("source_event_id",))
    ties_by_bundle, tie_duplicates = unique_by(inputs["tie_decisions"].rows, ("bundle_id",))
    changed_bundles = {
        row["bundle_id"]: row["context_selected_model"] for row in inputs["tie_decisions"].rows
        if row["model_changed_from_gdt474"] == "YES"
    }
    audit.check("gdt476_six_changed_models_source", changed_bundles == EXPECTED_CHANGED_BUNDLES, changed_bundles, EXPECTED_CHANGED_BUNDLES)
    label_projection_failures: list[str] = []
    grammar_projection_failures: list[str] = []
    ordered_core_failures: list[str] = []
    for event_id, slots in name_slots_by_event.items():
        out = label_by_event.get(event_id, {})
        source = triptych_by_event.get(event_id, {})
        fixed = (
            value(out, "bundle_id"), value(out, "physical_page"),
            value(out, "register"), value(out, "locus"), value(out, "surface"),
        )
        expected_fixed = (
            source.get("bundle_id", ""), source.get("physical_page", ""),
            source.get("register", ""), source.get("locus", ""), source.get("surface", ""),
        )
        if fixed != expected_fixed:
            label_projection_failures.append(event_id)
        expected_slot_ids = [row["slot_id"] for row in slots]
        expected_cores = [row["raw_name_core"] for row in slots]
        out_cores = split_values(
            value(out, "raw_name_cores", "ordered_raw_name_cores", "name_cores", "raw_core_sequence")
        )
        published_slot_count = int_value(out, "label_slot_count", "name_slot_count")
        if out_cores != expected_cores or published_slot_count != len(expected_slot_ids):
            ordered_core_failures.append(event_id)
        bundle_id = source.get("bundle_id", "")
        selected_model = (
            ties_by_bundle[bundle_id]["context_selected_model"]
            if bundle_id in ties_by_bundle else source.get("bundle_selected_model", "")
        )
        expected_reading = selected_event_reading(source, selected_model) if source else ""
        if (value(
                out, "grammar_model", "selected_grammar_model",
                "context_selected_model", "gdt585_selected_model",
            ) != selected_model
                or value(out, "grammar_source_reading_de", "source_grammar_reading_de", "selected_event_reading_de") != expected_reading):
            grammar_projection_failures.append(event_id)
    audit.check(
        "89_label_exact_source_projection",
        not triptych_duplicates and not label_projection_failures,
        {"source_duplicates": triptych_duplicates, "mismatches": label_projection_failures[:20]},
        {"source_duplicates": [], "mismatches": []},
    )
    audit.check("89_label_ordered_name_slot_projection", not ordered_core_failures, ordered_core_failures[:20], [])
    audit.check(
        "gdt476_model_and_reading_projection",
        not tie_duplicates and not grammar_projection_failures,
        {"tie_duplicates": tie_duplicates, "mismatches": grammar_projection_failures[:20]},
        {"tie_duplicates": [], "mismatches": []},
    )
    empty_label_meanings = [
        event_id for event_id, row in label_by_event.items()
        if not value(
            row, "gdt585_concrete_reading_de", "gdt585_primary_reading_de",
            "concrete_reading_de", "primary_reading_de",
        ).strip()
    ]
    audit.check("all_89_labels_have_concrete_reading", not empty_label_meanings, empty_label_meanings, [])

    expected_multi_events = {event_id for event_id, rows in name_slots_by_event.items() if len(rows) > 1}
    audit.check("source_multi_name_labels", len(expected_multi_events) == 17, expected_multi_events, "17 exact event IDs")
    compound_rows = outputs["compounds"].rows
    compound_by_id, compound_duplicates = unique_by(
        compound_rows, ("case_id", "compound_case_id", "compound_id")
    )
    covered_multi_events: set[str] = set()
    plant_bundle_found = False
    f89_boundary_found = False
    incomplete_compounds: list[str] = []
    for case_id, row in compound_by_id.items():
        event_ids = set(split_values(value(row, "source_event_ids", "event_ids", "source_event_id")))
        covered_multi_events.update(event_ids & expected_multi_events)
        plant_bundle_found |= {"P1003-E0079", "P1003-E0080"}.issubset(event_ids)
        f89_boundary_found |= {"P1008-E1301", "P1008-E1409"}.issubset(event_ids)
        required_texts = (
            value(row, "grammar_primary_reading_de", "primary_reading_de"),
            value(row, "composition_hypothesis_de"), value(row, "strongest_rival_de"),
            value(row, "reason_de", "working_basis_de"),
        )
        if not all(text.strip() for text in required_texts):
            incomplete_compounds.append(case_id)
    audit.check(
        "19_compound_case_identity", not compound_duplicates and len(compound_by_id) == 19,
        {"duplicates": compound_duplicates, "unique": len(compound_by_id)}, {"duplicates": [], "unique": 19},
    )
    audit.check("17_multi_name_cases_covered", covered_multi_events == expected_multi_events, covered_multi_events, expected_multi_events)
    audit.check(
        "two_cross_event_pair_cases", plant_bundle_found and f89_boundary_found,
        {"plant_bundle": plant_bundle_found, "f89_boundary": f89_boundary_found},
        {"plant_bundle": True, "f89_boundary": True},
    )
    audit.check("all_compounds_have_primary_rival_reason", not incomplete_compounds, incomplete_compounds, [])
    compound_scope_counts = Counter(value(row, "case_scope") for row in compound_rows)
    expected_scope_counts = {
        "CANONICAL_MULTI_OR_SAME_OBJECT_GROUP": 18,
        "EXTENDED_TWO_LINE_VISUAL_CONTEXT_PAIR": 1,
    }
    audit.check(
        "compound_scope_partition",
        compound_scope_counts == expected_scope_counts,
        compound_scope_counts,
        expected_scope_counts,
    )

    family_rows = outputs["families"].rows
    family_by_id, family_duplicates = unique_by(family_rows, ("family_id",))
    published_families = {
        family_id: set(split_values(value(row, "member_raw_cores", "raw_name_cores")))
        for family_id, row in family_by_id.items()
    }
    audit.check(
        "five_family_memberships", not family_duplicates and published_families == EXPECTED_FAMILIES,
        {"duplicates": family_duplicates, "families": published_families},
        {"duplicates": [], "families": EXPECTED_FAMILIES},
    )
    known_cores = {row["raw_name_core"] for row in source_type_rows}
    family_unknown_members = {
        family_id: sorted(core for core in cores if core not in known_cores)
        for family_id, cores in published_families.items() if any(core not in known_cores for core in cores)
    }
    incomplete_families = [
        family_id for family_id, row in family_by_id.items()
        if not all(value(row, field).strip() for field in ("decision", "reason_de", "prediction_de"))
    ]
    audit.check(
        "family_members_exist_and_readings_nonempty", not family_unknown_members and not incomplete_families,
        {"unknown": family_unknown_members, "incomplete": incomplete_families},
        {"unknown": {}, "incomplete": []},
    )

    local_rows = outputs["local_x"].rows
    local_by_id, local_duplicates = unique_by(local_rows, ("slot_id",))
    local_context_failures: list[str] = []
    for slot_id, (concept, default_de) in LOCAL_X_DEFAULTS.items():
        old = local_x_sources[slot_id]
        row = local_by_id.get(slot_id, {})
        if (
            value(row, "source_event_id", "source_event_or_card_id") != old.get("source_event_or_card_id", "")
            or value(row, "statement_id", "statement_or_record_id") != old.get("statement_or_record_id", "")
            or value(row, "surface") != old.get("surface", "")
            or value(row, "semantic_family", "core_concept") != concept
            or value(
                row, "gdt585_default_de", "gdt585_primary_default_de", "default_de"
            ) != default_de
            or not value(
                row, "context_reading_de", "gdt585_context_de",
                "source_context_de", "paragraph_de",
            ).strip()
            or not value(row, "strongest_rival_de").strip()
        ):
            local_context_failures.append(slot_id)
    audit.check(
        "two_local_x_context_cards",
        not local_duplicates and set(local_by_id) == set(LOCAL_X_DEFAULTS) and not local_context_failures,
        {"duplicates": local_duplicates, "ids": set(local_by_id), "mismatches": local_context_failures},
        {"duplicates": [], "ids": set(LOCAL_X_DEFAULTS), "mismatches": []},
    )

    history_rows = outputs["history"].rows
    history_by_id, history_duplicates = unique_by(history_rows, ("source_id", "history_id"))
    history_urls = {source_id: value(row, "url", "source_url") for source_id, row in history_by_id.items()}
    bad_domains = {
        source_id: urlparse(url).netloc for source_id, url in history_urls.items()
        if urlparse(url).netloc not in ALLOWED_HISTORY_DOMAINS
    }
    incomplete_history = [
        source_id for source_id, row in history_by_id.items()
        if not value(row, "observed_practice").strip() or not value(row, "model_use").strip()
        or not value(row, "does_not_support").strip()
    ]
    audit.check(
        "ten_historical_source_urls", not history_duplicates and history_urls == EXPECTED_HISTORY_URLS,
        {"duplicates": history_duplicates, "urls": history_urls},
        {"duplicates": [], "urls": EXPECTED_HISTORY_URLS},
    )
    audit.check(
        "historical_primary_domains_and_cautions", not bad_domains and not incomplete_history,
        {"bad_domains": bad_domains, "incomplete": incomplete_history},
        {"bad_domains": {}, "incomplete": []},
    )

    address_by_event, address_duplicates = unique_by(inputs["address_interlinear"].rows, ("source_event_id",))
    source_images: dict[str, tuple[str, str, int, int]] = {}
    image_label_counts: Counter[str] = Counter()
    image_slot_counts: Counter[str] = Counter()
    image_url_hash: dict[str, tuple[str, str]] = {}
    missing_image_events: list[str] = []
    for event_id, slots in name_slots_by_event.items():
        row = address_by_event.get(event_id, {})
        object_id = row.get("image_object_id", "")
        if not object_id or not row.get("image_url") or not row.get("review_image_sha256"):
            missing_image_events.append(event_id)
            continue
        image_label_counts[object_id] += 1
        image_slot_counts[object_id] += len(slots)
        image_url_hash[object_id] = (row["image_url"], row["review_image_sha256"])
    for object_id, (url, digest) in image_url_hash.items():
        source_images[object_id] = (url, digest, image_label_counts[object_id], image_slot_counts[object_id])
    audit.check(
        "source_four_image_contexts",
        not address_duplicates and not missing_image_events and source_images == EXPECTED_IMAGES,
        {"source_duplicates": address_duplicates, "missing_events": missing_image_events, "images": source_images},
        {"source_duplicates": [], "missing_events": [], "images": EXPECTED_IMAGES},
    )
    image_rows = outputs["images"].rows
    image_by_id, image_duplicates = unique_by(image_rows, ("image_object_id", "object_id"))
    image_projection_failures: list[str] = []
    image_method_failures: list[str] = []
    for object_id, expected in EXPECTED_IMAGES.items():
        row = image_by_id.get(object_id, {})
        published = (
            value(row, "image_url", "url"),
            value(row, "review_image_sha256", "image_sha256"),
        )
        if published != expected[:2]:
            image_projection_failures.append(object_id)
        method = value(row, "inspection_method", "review_method")
        observation = value(row, "manual_observation_de", "observation_de")
        caution = value(row, "does_not_support", "caution_de", "excluded_inference_de")
        if (method and "MANUAL" not in method.upper()) or not observation.strip() or not caution.strip():
            image_method_failures.append(object_id)
    audit.check(
        "four_image_card_exact_projection",
        not image_duplicates and set(image_by_id) == set(EXPECTED_IMAGES) and not image_projection_failures,
        {"duplicates": image_duplicates, "ids": set(image_by_id), "mismatches": image_projection_failures},
        {"duplicates": [], "ids": set(EXPECTED_IMAGES), "mismatches": []},
    )
    audit.check("manual_image_method_and_caution", not image_method_failures, image_method_failures, [])

    drug_visual_context_census = Counter(
        value(row, "visual_object_context") for row in slot_rows
        if value(row, "content_class") == "DRUG_OR_INGREDIENT_OBJECT"
    )
    expected_drug_visual_context_census = {
        "PICTURED_PLANT_FRAGMENT_LABEL": 29,
        "APOTHECARY_CONTAINER_LABEL": 7,
        "TWO_LINE_CONTAINER_PLANT_BOUNDARY_LABEL": 2,
    }
    audit.check(
        "29_7_2_drug_visual_context_census",
        drug_visual_context_census == expected_drug_visual_context_census,
        drug_visual_context_census,
        expected_drug_visual_context_census,
    )

    forbidden_pages: list[str] = []
    page_fields = ("physical_page", "physical_pages", "source_page", "source_pages", "page", "pages", "folio", "folios")
    for table_name, table in {**inputs, **outputs}.items():
        for row_number, row in enumerate(table.rows, 1):
            for token in page_tokens(row, page_fields):
                if token in {"f84", "f84r"} or token.startswith("f84r"):
                    forbidden_pages.append(f"{table_name}:{row_number}:{token}")
    audit.check("f84_f84r_selector_forbidden", not forbidden_pages, forbidden_pages, [])

    privacy_hits: list[str] = []
    private_home = "/" + "home" + "/" + "anon" + "/"
    for name, path in {**output_paths, "result": RESULT}.items():
        text = path.read_text(encoding="utf-8")
        if private_home in text or "PRIVATE KEY" in text or "BEGIN OPENSSH" in text:
            privacy_hits.append(name)
    audit.check("artifact_privacy_strings", not privacy_hits, privacy_hits, [])

    result_count_expected = {
        "types": 80, "slots": 109, "labels": 89, "compounds": 19,
        "families": 5, "local_x": 2, "history": 10, "images": 4,
    }
    audit.check(
        "result_counts",
        result.get("counts") == result_count_expected,
        result.get("counts"),
        result_count_expected,
    )
    result_star_expected = {"repeated_types": 10, "repeated_slots": 27}
    result_star_observed = {
        key: result.get("star_repeat_profile", {}).get(key) for key in result_star_expected
    }
    audit.check(
        "result_star_repeat_profile",
        result_star_observed == result_star_expected,
        result_star_observed,
        result_star_expected,
    )
    audit.check(
        "result_drug_visual_context_counts",
        result.get("drug_visual_context_counts") == expected_drug_visual_context_census,
        result.get("drug_visual_context_counts"),
        expected_drug_visual_context_census,
    )
    expected_changed_label_ids = [
        event_id for event_id in source_label_ids
        if triptych_by_event[event_id]["bundle_id"] in EXPECTED_CHANGED_BUNDLES
    ]
    audit.check(
        "result_gdt476_changed_labels",
        result.get("gdt476_changed_name_labels") == expected_changed_label_ids,
        result.get("gdt476_changed_name_labels"),
        expected_changed_label_ids,
    )
    audit.check(
        "result_compound_partition",
        result.get("canonical_compound_count") == 18,
        result.get("canonical_compound_count"),
        18,
    )

    validation = {
        "experiment_id": "GDT585",
        "status": "PASS" if not audit.failures else "FAIL",
        "check_count": len(audit.checks),
        "pass_count": len(audit.checks) - len(audit.failures),
        "fail_count": len(audit.failures),
        "input_sha256": input_hashes,
        "output_sha256": output_hashes,
        "checks": audit.checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if audit.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
