#!/usr/bin/env python3
"""Shared mobility, intake, and multiplicity helpers for GDT588."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt588_carrier_transfer_readiness_deck"
OUT = BASE / "artifacts"
G583 = ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
G587 = ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts"

INPUTS = {
    "rules_583": G583 / "src/rules.py",
    "actions_584": G584 / "gdt584_target_occurrence_revisions.tsv",
    "assignments_587": G587 / "gdt587_1243_action_conditioned_carrier_assignments.tsv",
    "hosts_587": G587 / "gdt587_candidate_statement_host_phrases.tsv",
    "statements_587": G587 / "gdt587_793_complete_statement_reader.tsv",
    "local_cards_587": G587 / "gdt587_744_complete_local_card_reader.tsv",
}

OUTPUTS = {
    "rule_gate": OUT / "gdt588_38_action_rule_gate.tsv",
    "future_cells": OUT / "gdt588_220_future_portable_cell_matrix.tsv",
    "fallbacks": OUT / "gdt588_20_register_root_fallbacks.tsv",
    "packet_cards": OUT / "gdt588_8_packet_cards.tsv",
    "assignments": OUT / "gdt588_1243_assignment_mobility.tsv",
    "selections": OUT / "gdt588_268_strict_selection_signatures.tsv",
    "cells": OUT / "gdt588_136_action_root_cell_mobility.tsv",
    "special_hosts": OUT / "gdt588_74_special_packet_transfer.tsv",
    "special_shapes": OUT / "gdt588_34_special_packet_shapes.tsv",
    "repairs": OUT / "gdt588_13_multiplicity_safe_packet_repairs.tsv",
    "pages": OUT / "gdt588_30_page_readiness_profiles.tsv",
    "statements": OUT / "gdt588_793_count_safe_statement_reader.tsv",
    "local_cards": OUT / "gdt588_744_count_safe_local_card_reader.tsv",
    "book": OUT / "GDT588_COUNT_SAFE_THIRTY_PAGE_READER.md",
    "deck": OUT / "GDT588_CARRIER_TRANSFER_READINESS_DECK.md",
    "contract": OUT / "gdt588_intake_contract.json",
    "result": OUT / "gdt588_result.json",
    "validation": OUT / "gdt588_validation.json",
}

ROOT_ORDER = {"Y": 0, "AIIN": 1, "AIN": 2, "OR": 3}
PORTABLE_CORE = {"Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}

TIER_EXACT = "EXACT_SELECTION_OTHER_PAGE"
TIER_CELL = "SAME_ACTION_ROOT_LEMMA_OTHER_PAGE"
TIER_REGISTER = "SAME_REGISTER_ROOT_OTHER_PAGE"
TIER_PRIVATE = "PAGE_PRIVATE_REGISTER_ROOT"
TIER_ORDER = (TIER_EXACT, TIER_CELL, TIER_REGISTER, TIER_PRIVATE)

STATUS = (
    "PASS_1243_SELECTION_MOBILITY__970_EXACT__146_SAME_CELL__"
    "121_REGISTER_ROOT__6_PAGE_PRIVATE__74_SPECIAL_PACKET_HOSTS__"
    "13_MULTIPLICITY_REPAIRS"
)


def _load_gdt587_nouns() -> Any:
    path = ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/src/nouns.py"
    spec = importlib.util.spec_from_file_location("gdt587_nouns_for_gdt588", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT587 noun model")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NOUNS = _load_gdt587_nouns()


def _load_gdt583_rules() -> Any:
    path = INPUTS["rules_583"]
    name = "gdt583_rules_for_gdt588"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT583 rule model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G583_RULES = _load_gdt583_rules()


PACKET_CARD_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "SOURCE_PART_OF_MATERIAL": {
        "condition": "SOURCE_SECTION_T + T_SOURCE_FIX + exactly Y+AIN",
        "template_de": "Lege [Arbeitsmaterial; Teilmenge] fest",
        "fallback": "emit every selected root noun in written multiplicity",
    },
    "SOURCE_LIQUID_FROM_MATERIAL": {
        "condition": "SOURCE_SECTION_T + S_SOURCE_SORT_OUT + Y and AIIN",
        "template_de": "Sondere [Arbeitsflüssigkeit; Arbeitsmaterial] aus",
        "fallback": "keep liquid and material as separate written carriers",
    },
    "CELESTIAL_POSITION_SEGMENT_VALUE": {
        "condition": "CELESTIAL + T_CELESTIAL_SET + at least two of Y/AIIN/OR",
        "template_de": "Stelle [Ringposition; Ringsegment; Positionswert] ein",
        "fallback": "emit the present ring carriers in root order",
    },
    "BIOLOGICAL_BODY_PART": {
        "condition": "BIOLOGICAL + CHD_BIO_TREAT + exactly Y+AIN",
        "template_de": "Behandle [Körper; Teil]",
        "fallback": "do not force Körper outside the exact packet",
    },
    "BIOLOGICAL_BATH_FILL": {
        "condition": "BIOLOGICAL + SH_BIO_BATHE + AIIN present",
        "template_de": "Halte im Bad [Stationsansatz/Körper; Badfüllung]",
        "fallback": "run the full blocker test for Y and preserve every carrier",
    },
    "BIOLOGICAL_FLOW_PACKET": {
        "condition": "BIOLOGICAL + S_BIO_DIVERT + any carrier root",
        "template_de": "Leite [Strom; Mengenangabe; Teilmenge; Beckeninhalt] um",
        "fallback": "emit only present carriers, with written multiplicity",
    },
    "HP_MEASURE_FOR_MATERIAL": {
        "condition": "HERBAL/PHARMA + T_HP_MEASURE_SET + Y and AIIN",
        "template_de": "Stelle [Auszugs-/Dosismaß; Material] ein",
        "fallback": "keep measure and material distinct",
    },
    "HP_EXTRACT_OF_MATERIAL": {
        "condition": "S_HP_STRAIN or S_HP_STRAIN_AFTER_WET_STEP",
        "template_de": "Seihe [Auszug; Material/Portion/Ansatz] ab",
        "fallback": "use explicit Auszug when AIIN is absent and retain all written carriers",
    },
}


REGISTER_FALLBACK_FORMS: dict[tuple[str, str], dict[str, str]] = {
    ("SOURCE_SECTION_T", "Y"): {"decision": "KEEP_BROAD", "lemma": "Arbeitsgut", "object": "das Arbeitsgut", "genitive": "des Arbeitsguts"},
    ("SOURCE_SECTION_T", "AIIN"): {"decision": "KEEP_BROAD", "lemma": "Flüssigkeitsmaß", "object": "das Flüssigkeitsmaß", "genitive": "des Flüssigkeitsmaßes"},
    ("SOURCE_SECTION_T", "AIN"): {"decision": "REGISTER_INVARIANT", "lemma": "Teilmenge", "object": "die Teilmenge", "genitive": "der Teilmenge"},
    ("SOURCE_SECTION_T", "OR"): {"decision": "REGISTER_INVARIANT", "lemma": "Ansatz", "object": "den Ansatz", "genitive": "des Ansatzes"},
    ("HERBAL", "Y"): {"decision": "REGISTER_INVARIANT", "lemma": "Pflanzenmaterial", "object": "das Pflanzenmaterial", "genitive": "des Pflanzenmaterials"},
    ("HERBAL", "AIIN"): {"decision": "KEEP_BROAD", "lemma": "Pflanzenauszug", "object": "den Pflanzenauszug", "genitive": "des Pflanzenauszugs"},
    ("HERBAL", "AIN"): {"decision": "REGISTER_INVARIANT", "lemma": "Pflanzenportion", "object": "die Pflanzenportion", "genitive": "der Pflanzenportion"},
    ("HERBAL", "OR"): {"decision": "KEEP_BROAD", "lemma": "Pflanzen- oder Arbeitseinheit", "object": "die Pflanzen- oder Arbeitseinheit", "genitive": "der Pflanzen- oder Arbeitseinheit"},
    ("CELESTIAL", "Y"): {"decision": "REGISTER_INVARIANT", "lemma": "Ringposition", "object": "die Ringposition", "genitive": "der Ringposition"},
    ("CELESTIAL", "AIIN"): {"decision": "REGISTER_INVARIANT", "lemma": "Positionswert", "object": "den Positionswert", "genitive": "des Positionswerts"},
    ("CELESTIAL", "AIN"): {"decision": "REGISTER_INVARIANT", "lemma": "Sektoranteil", "object": "den Sektoranteil", "genitive": "des Sektoranteils"},
    ("CELESTIAL", "OR"): {"decision": "REGISTER_INVARIANT", "lemma": "Ringsegment", "object": "das Ringsegment", "genitive": "des Ringsegments"},
    ("BIOLOGICAL", "Y"): {"decision": "KEEP_BROAD", "lemma": "Stationsansatz", "object": "den Stationsansatz", "genitive": "des Stationsansatzes"},
    ("BIOLOGICAL", "AIIN"): {"decision": "KEEP_BROAD", "lemma": "Stations- oder Badmaß", "object": "das Stations- oder Badmaß", "genitive": "des Stations- oder Badmaßes"},
    ("BIOLOGICAL", "AIN"): {"decision": "KEEP_BROAD", "lemma": "Anwendungsportion", "object": "die Anwendungsportion", "genitive": "der Anwendungsportion"},
    ("BIOLOGICAL", "OR"): {"decision": "KEEP_BROAD", "lemma": "Becken- oder Körpereinheit", "object": "die Becken- oder Körpereinheit", "genitive": "der Becken- oder Körpereinheit"},
    ("PHARMA", "Y"): {"decision": "REGISTER_INVARIANT", "lemma": "Drogenmaterial", "object": "das Drogenmaterial", "genitive": "des Drogenmaterials"},
    ("PHARMA", "AIIN"): {"decision": "KEEP_BROAD", "lemma": "Dosis- oder Mengenmaß", "object": "das Dosis- oder Mengenmaß", "genitive": "des Dosis- oder Mengenmaßes"},
    ("PHARMA", "AIN"): {"decision": "REGISTER_INVARIANT", "lemma": "Zutatenportion", "object": "die Zutatenportion", "genitive": "der Zutatenportion"},
    ("PHARMA", "OR"): {"decision": "KEEP_BROAD", "lemma": "Gefäß- oder Arbeitseinheit", "object": "die Gefäß- oder Arbeitseinheit", "genitive": "der Gefäß- oder Arbeitseinheit"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pipe(values: Iterable[str]) -> str:
    selected = sorted(set(value for value in values if value and value != "NONE"))
    return "|".join(selected) if selected else "NONE"


def exact_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    key = (
        row["register"],
        row["gdt584_rule_id"],
        row["carrier_root"],
        row["gdt587_context_family"],
        row["gdt587_lemma_de"],
        row["gdt587_packet_rule_id"],
        row["carrier_root_signature"],
    )
    return (*key, row["layer"]) if same_layer else key


def cell_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    key = (row["register"], row["gdt584_rule_id"], row["carrier_root"])
    return (*key, row["layer"]) if same_layer else key


def cell_lemma_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    return (*cell_key(row, same_layer=same_layer), row["gdt587_lemma_de"])


def register_root_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    key = (row["register"], row["carrier_root"])
    return (*key, row["layer"]) if same_layer else key


def register_root_lemma_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    return (*register_root_key(row, same_layer=same_layer), row["gdt587_lemma_de"])


def root_lemma_key(row: dict[str, str], *, same_layer: bool = False) -> tuple[str, ...]:
    key = (row["carrier_root"], row["gdt587_lemma_de"])
    return (*key, row["layer"]) if same_layer else key


def support_pages(
    rows: list[dict[str, str]], key_function: Callable[[dict[str, str]], tuple[str, ...]]
) -> dict[tuple[str, ...], set[str]]:
    output: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for row in rows:
        output[key_function(row)].add(row["physical_page"])
    return output


def support_rows(
    rows: list[dict[str, str]], key_function: Callable[[dict[str, str]], tuple[str, ...]]
) -> dict[tuple[str, ...], list[dict[str, str]]]:
    output: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        output[key_function(row)].append(row)
    return output


def other_pages(pages: set[str], current_page: str) -> set[str]:
    return pages - {current_page}


def mobility_maps(rows: list[dict[str, str]], *, same_layer: bool = False) -> dict[str, Any]:
    exact = lambda row: exact_key(row, same_layer=same_layer)
    cell = lambda row: cell_key(row, same_layer=same_layer)
    cell_lemma = lambda row: cell_lemma_key(row, same_layer=same_layer)
    register_root = lambda row: register_root_key(row, same_layer=same_layer)
    register_lemma = lambda row: register_root_lemma_key(row, same_layer=same_layer)
    root_lemma = lambda row: root_lemma_key(row, same_layer=same_layer)
    return {
        "exact_pages": support_pages(rows, exact),
        "exact_rows": support_rows(rows, exact),
        "cell_pages": support_pages(rows, cell),
        "cell_lemma_pages": support_pages(rows, cell_lemma),
        "register_root_pages": support_pages(rows, register_root),
        "register_lemma_pages": support_pages(rows, register_lemma),
        "root_lemma_pages": support_pages(rows, root_lemma),
        "same_layer": same_layer,
    }


def classify(row: dict[str, str], maps: dict[str, Any]) -> tuple[str, set[str]]:
    same_layer = bool(maps["same_layer"])
    page = row["physical_page"]
    exact = other_pages(maps["exact_pages"][exact_key(row, same_layer=same_layer)], page)
    if exact:
        return TIER_EXACT, exact
    cell = other_pages(maps["cell_pages"][cell_key(row, same_layer=same_layer)], page)
    if cell:
        # Every such case in GDT588 retains the same contextual lemma. Keep the
        # stricter cell test primary, and validate the lemma equality separately.
        return TIER_CELL, cell
    register = other_pages(
        maps["register_root_pages"][register_root_key(row, same_layer=same_layer)], page
    )
    if register:
        return TIER_REGISTER, register
    return TIER_PRIVATE, set()


def example_slot(
    rows: list[dict[str, str]],
    key_function: Callable[[dict[str, str]], tuple[str, ...]],
    key: tuple[str, ...],
    current_page: str,
) -> str:
    candidates = [row for row in rows if key_function(row) == key and row["physical_page"] != current_page]
    return candidates[0]["carrier_slot_id"] if candidates else "NONE"


def root_multiset(rows: list[dict[str, str]]) -> str:
    counts = Counter(row["carrier_root"] for row in rows)
    return "+".join(
        f"{root}*{counts[root]}" for root in ROOT_ORDER if counts[root]
    )


def lemma_trace(rows: list[dict[str, str]], *, with_counts: bool) -> str:
    counts = Counter(row["carrier_root"] for row in rows)
    output: list[str] = []
    for root in ROOT_ORDER:
        lemmas = sorted({row["gdt587_lemma_de"] for row in rows if row["carrier_root"] == root})
        if not lemmas:
            continue
        multiplicity = f"*{counts[root]}" if with_counts else ""
        output.append(f"{root}{multiplicity}={'/'.join(lemmas)}")
    return "|".join(output)


def count_trace_de(rows: list[dict[str, str]]) -> str:
    counts = Counter(row["carrier_root"] for row in rows)
    output: list[str] = []
    for root in ROOT_ORDER:
        members = [row for row in rows if row["carrier_root"] == root]
        if not members:
            continue
        lemmas = "/".join(sorted({row["gdt587_lemma_de"] for row in members}))
        output.append(f"{lemmas} ×{counts[root]}")
    return "; ".join(output)


def packet_presence_key(rows: list[dict[str, str]]) -> tuple[str, ...]:
    row = rows[0]
    return (
        row["register"],
        row["gdt584_rule_id"],
        row["carrier_root_signature"],
        row["gdt587_packet_rule_id"],
        lemma_trace(rows, with_counts=False),
    )


def packet_multiplicity_key(rows: list[dict[str, str]]) -> tuple[str, ...]:
    row = rows[0]
    return (
        row["register"],
        row["gdt584_rule_id"],
        root_multiset(rows),
        row["gdt587_packet_rule_id"],
        lemma_trace(rows, with_counts=True),
    )


MULTIPLICITY_REPAIRS: dict[str, dict[str, str]] = {
    "G407-S003": {
        "old": "Lege die Teilmenge des Arbeitsmaterials fest",
        "new": "Lege [Arbeitsmaterial ×2; Teilmenge] fest",
    },
    "G407-S009": {
        "old": "Stelle die Auszugsmenge für das Pflanzenmaterial an der Pflanzen-Arbeitsstelle ein",
        "new": "Stelle [Auszugsmenge; Pflanzenmaterial ×2] an der Pflanzen-Arbeitsstelle ein",
    },
    "G407-S031": {
        "old": "Seihe den Pflanzenauszug aus dem Pflanzenansatz in Zubereitungsform, auf Grad I, an der Pflanzen-Arbeitsstelle und über den Materialkontakt ab",
        "new": "Seihe [Pflanzenauszug; Pflanzenansatz ×2] in Zubereitungsform, auf Grad I, an der Pflanzen-Arbeitsstelle und über den Materialkontakt ab",
    },
    "G407-S037": {
        "old": "Seihe den Pflanzenauszug vom Ausgangsmaterial oder -gefäß und über den Materialkontakt ab",
        "new": "Seihe [Pflanzenauszug ×2] vom Ausgangsmaterial oder -gefäß und über den Materialkontakt ab",
    },
    "G407-S047": {
        "old": "Stelle die Ringposition des Ringsegments auf den Positionswert ein",
        "new": "Stelle [Ringposition; Ringsegment ×2; Positionswert] ein",
    },
    "G407-S287": {
        "old": "Behandle den Körperteil",
        "new": "Behandle [Körper; Teil ×2]",
    },
    "G407-S425": {
        "old": "Leite den Strom in Anwendungsform, auf der Anwendungsstufe und über den Stationskontakt oder die Leitung um",
        "new": "Leite [Strom ×2] in Anwendungsform, auf der Anwendungsstufe und über den Stationskontakt oder die Leitung um",
    },
    "G407-S440": {
        "old": "Leite die angegebene Menge des Beckeninhalts in der Innenform und von der Ausgangsstation oder aus dem Ausgangsbecken um",
        "new": "Leite [Beckeninhalt ×2; Mengenangabe] in der Innenform und von der Ausgangsstation oder aus dem Ausgangsbecken um",
    },
    "G407-S531": {
        "old": "Halte den Stationsansatz im Bad bei der angegebenen Füllung auf Grad I und über den Stationskontakt oder die Leitung",
        "new": "Halte im Bad [Stationsansatz ×2; Badfüllung] auf Grad I und über den Stationskontakt oder die Leitung",
    },
    "G407-S670": {
        "old": "Seihe den Arzneiauszug des Drogenmaterials in Arzneiform, auf Grad I, als neuer Arzneiansatz und über den Gefäßkontakt ab",
        "new": "Seihe [Arzneiauszug ×2; Drogenmaterial ×2] in Arzneiform, auf Grad I, als neuer Arzneiansatz und über den Gefäßkontakt ab",
    },
    "G407-S685": {
        "old": "Seihe den Arzneiauszug ins Aufnahme- oder Zielgefäß ab",
        "new": "Seihe [Arzneiauszug ×2] ins Aufnahme- oder Zielgefäß ab",
    },
    "P912-E2117": {
        "old": "Stelle die Ringposition des Ringsegments ein",
        "new": "Stelle [Ringposition ×2; Ringsegment] ein",
    },
    "P912-E1398": {
        "old": "Leite den Beckeninhalt über den Stationskontakt oder die Leitung um",
        "new": "Leite [Beckeninhalt ×2] über den Stationskontakt oder die Leitung um",
    },
}


def allowed_rules_by_register(actions: list[dict[str, str]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in actions:
        output[row["register"]].add(row["gdt584_rule_id"])
    return output


def intake_reading(
    *,
    register: str,
    rule: str,
    root: str,
    roots: Iterable[str],
    host_values: Iterable[str],
    source_page: str = "UNRELEASED",
) -> dict[str, Any]:
    """Apply the fixed GDT587 noun rule, then annotate its old-page support."""
    assignments = read_tsv(INPUTS["assignments_587"])
    actions = read_tsv(INPUTS["actions_584"])
    root_set = frozenset(roots)
    value_set = frozenset(host_values)
    if register not in NOUNS.BASE_LEMMA:
        raise ValueError(f"Unknown register: {register}")
    if root not in ROOT_ORDER:
        raise ValueError(f"Unknown carrier root: {root}")
    if root not in root_set:
        raise ValueError("Selected root must occur in --roots")
    if not root_set <= set(ROOT_ORDER):
        raise ValueError(f"Unsupported carrier roots: {sorted(root_set - set(ROOT_ORDER))}")
    if not root_set <= value_set:
        raise ValueError("Every carrier root must also occur in --host-values")

    allowed = allowed_rules_by_register(actions)
    if rule not in allowed[register]:
        return {
            "register": register,
            "gdt584_rule_id": rule,
            "carrier_root": root,
            "carrier_root_signature": "+".join(sorted(root_set, key=ROOT_ORDER.__getitem__)),
            "portable_carrier_core": PORTABLE_CORE[root],
            "reader_route": "KEEP_PORTABLE_CORE_UNTIL_FIXED_ACTION_RULE_EXISTS",
            "working_lemma_de": PORTABLE_CORE[root],
            "gdt587_packet_rule_id": "NOT_APPLICABLE_UNKNOWN_ACTION_RULE",
            "transfer_tier": "NO_FIXED_GDT584_ACTION_RULE",
            "supporting_pages": "NONE",
            "intake_action": "DO_NOT_INVENT_ACTION_CONDITIONED_NOUN",
        }

    selected = NOUNS.choose_noun(register, rule, root, root_set, value_set)
    packet = NOUNS.packet_rule_id(register, rule, root_set)
    probe = {
        "physical_page": source_page,
        "layer": "FUTURE_INTAKE",
        "register": register,
        "gdt584_rule_id": rule,
        "carrier_root": root,
        "carrier_root_signature": "+".join(sorted(root_set, key=ROOT_ORDER.__getitem__)),
        "gdt587_context_family": selected["gdt587_context_family"],
        "gdt587_lemma_de": selected["gdt587_lemma_de"],
        "gdt587_packet_rule_id": packet,
    }
    maps = mobility_maps(assignments)
    tier, pages = classify(probe, maps)
    actions_by_tier = {
        TIER_EXACT: "REUSE_EXACT_SELECTION_AND_PACKET",
        TIER_CELL: "REUSE_FIXED_ACTION_ROOT_LEMMA_KEEP_NEW_PACKET_TRACE",
        TIER_REGISTER: "APPLY_FIXED_GDT587_RULE_MARK_ACTION_CELL_LOCAL",
        TIER_PRIVATE: "APPLY_FIXED_GDT587_RULE_MARK_REGISTER_ROOT_LOCAL",
    }
    return {
        "register": register,
        "gdt584_rule_id": rule,
        "carrier_root": root,
        "carrier_root_signature": probe["carrier_root_signature"],
        "portable_carrier_core": PORTABLE_CORE[root],
        "reader_route": "FIXED_GDT587_ACTION_CONDITIONED_NOUN",
        "working_context_family": selected["gdt587_context_family"],
        "working_lemma_de": selected["gdt587_lemma_de"],
        "working_object_form_de": selected["gdt587_object_form_de"],
        "working_genitive_form_de": selected["gdt587_genitive_form_de"],
        "gdt587_packet_rule_id": packet,
        "transfer_tier": tier,
        "supporting_pages": pipe(pages),
        "intake_action": actions_by_tier[tier],
        "multiplicity_rule": "PRESERVE_EVERY_WRITTEN_ROOT_SLOT_AND_EMIT_COUNTS_ABOVE_ONE",
    }


def observed_cell_rows(assignments: list[dict[str, str]]) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    output: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        output[(row["register"], row["gdt584_rule_id"], row["carrier_root"])].append(row)
    return output


def register_root_lemmas(assignments: list[dict[str, str]]) -> dict[tuple[str, str], set[str]]:
    output: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in assignments:
        output[(row["register"], row["carrier_root"])].add(row["gdt587_lemma_de"])
    return output


def future_matrix_state(
    register: str, rule: str, root: str, assignments: list[dict[str, str]]
) -> str:
    if (register, rule, root) in observed_cell_rows(assignments):
        return "OBSERVED_CELL"
    return REGISTER_FALLBACK_FORMS[(register, root)]["decision"]


def future_host_reading(
    *,
    action_root: str,
    register: str,
    carrier_roots: Iterable[str],
    direct_tokens: Iterable[str],
    host_tokens: Iterable[str],
    previous_action: str,
    next_action: str,
    source_id: str = "FUTURE_UNRELEASED_HOST",
    physical_page: str = "UNRELEASED",
) -> dict[str, Any]:
    """Select one automatic action rule and bounded carrier defaults.

    Repeated carrier roots remain ordered written slots. The runtime path does
    not auto-apply source-ID-bound rules or manual GDT584 overrides.
    """
    roots_written = list(carrier_roots)
    direct = set(direct_tokens)
    host = set(host_tokens)
    if register not in NOUNS.BASE_LEMMA:
        return {
            "register": register,
            "reader_route": "UNKNOWN_REGISTER_PORTABLE_CORE_ONLY",
            "written_carriers": [PORTABLE_CORE.get(root, "UNKNOWN_ROOT") for root in roots_written],
        }
    if not roots_written:
        raise ValueError("At least one written carrier root is required")
    if any(root not in ROOT_ORDER for root in roots_written):
        return {
            "register": register,
            "reader_route": "UNKNOWN_ROOT_PORTABLE_CORE_ONLY",
            "written_carriers": [PORTABLE_CORE.get(root, "UNKNOWN_ROOT") for root in roots_written],
        }
    if not set(roots_written) <= host:
        raise ValueError("Every written carrier root must occur among --host-tokens")

    rule = G583_RULES.select_rule(
        root=action_root,
        register=register,
        source_id=source_id,
        physical_page=physical_page,
        direct_tokens=direct,
        host_tokens=host,
        previous_action=previous_action,
        next_action=next_action,
    )
    if rule.source_ids:
        raise RuntimeError("Source-ID-bound GDT583 rules are not future-portable")

    assignments = read_tsv(INPUTS["assignments_587"])
    cells = observed_cell_rows(assignments)
    root_set = frozenset(roots_written)
    packet = NOUNS.packet_rule_id(register, rule.rule_id, root_set)
    packet_known = packet != "DEFAULT_GDT584_OBJECT_COMPOSITION" and any(
        row["gdt587_packet_rule_id"] == packet for row in assignments
    )
    slot_readings: list[dict[str, str]] = []
    for ordinal, root in enumerate(roots_written, start=1):
        key = (register, rule.rule_id, root)
        members = cells.get(key, [])
        fallback = REGISTER_FALLBACK_FORMS[(register, root)]
        selected = NOUNS.choose_noun(register, rule.rule_id, root, root_set, frozenset(host))
        if packet_known:
            lookup_route = "KNOWN_PACKET_RULE"
            form = {
                "lemma": selected["gdt587_lemma_de"],
                "object": selected["gdt587_object_form_de"],
                "genitive": selected["gdt587_genitive_form_de"],
            }
            context_family = selected["gdt587_context_family"]
        elif members and selected["gdt587_lemma_de"] in {
            row["gdt587_lemma_de"] for row in members
        }:
            lookup_route = "OBSERVED_ACTION_ROOT_CELL"
            form = {
                "lemma": selected["gdt587_lemma_de"],
                "object": selected["gdt587_object_form_de"],
                "genitive": selected["gdt587_genitive_form_de"],
            }
            context_family = selected["gdt587_context_family"]
        else:
            lookup_route = fallback["decision"]
            if members:
                lookup_route = f"NEW_CELL_VARIANT_TO_{lookup_route}"
            form = fallback
            context_family = (
                "REGISTER_INVARIANT_FALLBACK"
                if fallback["decision"] == "REGISTER_INVARIANT"
                else "BROAD_REGISTER_FALLBACK"
            )
        slot_readings.append(
            {
                "written_carrier_ordinal": str(ordinal),
                "carrier_root": root,
                "portable_core": PORTABLE_CORE[root],
                "lookup_route": lookup_route,
                "context_family": context_family,
                "working_lemma_de": form["lemma"],
                "working_object_form_de": form["object"],
                "working_genitive_form_de": form["genitive"],
            }
        )

    lemma_counts = Counter(row["working_lemma_de"] for row in slot_readings)
    trace = "; ".join(f"{lemma} ×{count}" for lemma, count in lemma_counts.items())
    packet_card = PACKET_CARD_DESCRIPTIONS.get(packet)
    return {
        "register": register,
        "action_root": action_root,
        "automatic_gdt583_rule_id": rule.rule_id,
        "automatic_action_reading_de": rule.working_default_de,
        "action_gate": "AUTO_CONTEXT_RULE_NO_GDT584_MANUAL_OVERRIDE",
        "gdt587_packet_rule_id": packet,
        "packet_template_de": (
            packet_card["template_de"] if packet_card else "[Träger in geschriebener Reihenfolge]"
        ),
        "written_root_sequence": "+".join(roots_written),
        "written_root_multiset": root_multiset(
            [{"carrier_root": root} for root in roots_written]  # type: ignore[list-item]
        ),
        "carrier_count_trace_de": trace,
        "working_packet_de": f"[{trace}]",
        "slot_readings": slot_readings,
        "multiplicity_rule": (
            "EVERY_WRITTEN_CARRIER_RETAINED__COUNTS_ARE_TEXTUAL_NOT_REAL_OBJECT_COUNTS"
        ),
    }
