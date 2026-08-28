#!/usr/bin/env python3
"""Deterministic GDT597 object/reference completion for non-SH bath actions."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt597_nonsh_action_object_reference_phrasebook"
ARTIFACTS = BASE / "artifacts"
PAGES = ("f75r", "f77r", "f81r", "f81v", "f82r", "f83r")
TARGET_ROOTS = {"T", "CHD", "S"}
CARRIER_ROOTS = {"Y", "AIIN", "AIN", "OR"}
STATUS = "PASS_396_NONSH_ACTION_OBJECTS__219_WRITTEN__77_LEFT__4_RIGHT__96_DEFAULT__0_UNFILLED"

INPUTS = {
    "gdt584_hosts": ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts/gdt584_statement_wide_host_phrases.tsv",
    "gdt582_slots": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "gdt587_hosts": ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts/gdt587_candidate_statement_host_phrases.tsv",
    "gdt589_hosts": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_953_complete_host_replay.tsv",
    "gdt596_baths": ROOT / "experiments/yolo/gdt596_bath_object_compound_scope_phrasebook/artifacts/gdt596_254_compound_scope_replay.tsv",
    "manual_workshop_review": BASE / "sources/gdt597_manual_workshop_review.tsv",
}

OUTPUTS = {
    "typing_cards": ARTIFACTS / "gdt597_5_object_typing_cards.tsv",
    "reference_cards": ARTIFACTS / "gdt597_3_reference_scope_cards.tsv",
    "default_cards": ARTIFACTS / "gdt597_7_action_default_cards.tsv",
    "compatibility_cards": ARTIFACTS / "gdt597_7_action_compatibility_cards.tsv",
    "determiner_cells": ARTIFACTS / "gdt597_6_determiner_cells.tsv",
    "object_forms": ARTIFACTS / "gdt597_18_observed_object_forms.tsv",
    "replay": ARTIFACTS / "gdt597_396_nonsh_action_object_replay.tsv",
    "pages": ARTIFACTS / "gdt597_6_page_profiles.tsv",
    "long_references": ARTIFACTS / "gdt597_long_reference_review.tsv",
    "rejected_candidates": ARTIFACTS / "gdt597_11_rejected_reference_candidates.tsv",
    "workshop_reviews": ARTIFACTS / "gdt597_17_manual_workshop_decisions.tsv",
    "phrasebook": ARTIFACTS / "GDT597_NONSH_OBJECT_REFERENCE_PHRASEBOOK.md",
    "result": ARTIFACTS / "gdt597_result.json",
    "validation": ARTIFACTS / "gdt597_validation.json",
}

HOST_COLUMNS = [
    "host_ordinal_global", "statement_id", "host_ordinal_in_statement", "physical_page",
    "register", "owner_id", "primary_governor_key", "anchor_event_id", "packet_event_ids",
    "action_root", "action_slot_id", "gdt584_rule_id", "paragraph_boundary",
    "gdt584_reader_clause_de",
]
SLOT_COLUMNS = [
    "slot_id", "layer", "source_event_or_card_id", "statement_or_record_id", "physical_page",
    "register", "surface", "slot_value", "slot_position", "boundary_class",
    "primary_governor_kind", "primary_governor_key", "realization_scope",
    "gdt582_concrete_default_de",
]
G587_COLUMNS = [
    "statement_id", "host_ordinal_in_statement", "physical_page", "primary_governor_key",
    "anchor_event_id", "action_root", "gdt584_rule_id", "carrier_slot_count",
    "carrier_roots", "carrier_slot_ids", "gdt587_packet_rule_id", "gdt584_reader_clause_de",
    "gdt587_reader_clause_de", "reader_clause_changed",
]
G589_COLUMNS = [
    "primary_governor_key", "action_slot_id", "layer", "source_event_or_card_id",
    "statement_or_record_id", "physical_page", "register", "action_root", "gdt583_rule_id",
    "carrier_slot_count", "carrier_slot_ids", "written_root_sequence", "expected_packet_rule_id",
    "expected_lemma_sequence",
]


ACTION_DEFAULTS = {
    "CHD_BIO_TREAT": {
        "lemma": "Stationsansatz", "object_class": "STATION",
        "typing_card_id": "T05_WORKPIECE_DEFAULT",
        "reason_de": "Ohne passende Quelle bleibt der bereits vorhandene Ansatz-Default konkret als Stationsansatz.",
    },
    "S_BIO_DIVERT": {
        "lemma": "Strom", "object_class": "FLOW",
        "typing_card_id": "T02_ACTION_INTERNAL_OBJECT",
        "reason_de": "UMLEITEN besitzt in der vorhandenen Regel bereits den Strom als internes Arbeitsobjekt.",
    },
    "S_REST_SELECT": {
        "lemma": "Stationseinheit", "object_class": "UNIT",
        "typing_card_id": "T04_STABLE_CLASS_DEFAULT",
        "reason_de": "WÄHLEN besitzt ohne Träger den sichtbaren Einheitsplatz; Biological konkretisiert ihn als Stationseinheit.",
    },
    "T_AFTER_SH_COOL": {
        "lemma": "Körper", "object_class": "BODY",
        "typing_card_id": "T05_WORKPIECE_DEFAULT",
        "reason_de": "ABKÜHLEN übernimmt vorrangig sein unmittelbar vorangehendes Badobjekt; Körper ist nur der nie benötigte Notdefault.",
    },
    "T_BIO_RELATION_REGULATE": {
        "lemma": "Stationsansatz", "object_class": "STATION",
        "typing_card_id": "T05_WORKPIECE_DEFAULT",
        "reason_de": "Die Relationsregulierung übernimmt vorrangig das Badobjekt desselben Ereignisses; Stationsansatz bleibt Notdefault.",
    },
    "T_BIO_STATION_REGULATE": {
        "lemma": "Stationsbedingung", "object_class": "CONDITION",
        "typing_card_id": "T02_ACTION_INTERNAL_OBJECT",
        "reason_de": "Die trägerlose Regel nennt bereits die Stationsbedingung; ein früheres Materialobjekt ersetzt sie nicht.",
    },
    "T_PHYSICAL_GRADE_TEMPER": {
        "lemma": "Stationsansatz", "object_class": "STATION",
        "typing_card_id": "T05_WORKPIECE_DEFAULT",
        "reason_de": "TEMPERIEREN übernimmt eine passende Werkstückquelle; ohne Quelle bleibt der Stationsansatz.",
    },
}

COMPATIBLE_CLASSES = {
    "CHD_BIO_TREAT": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
    "S_BIO_DIVERT": {"FLOW"},
    "S_REST_SELECT": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "MEASURE", "FLOW"},
    "T_AFTER_SH_COOL": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
    "T_BIO_RELATION_REGULATE": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
    "T_BIO_STATION_REGULATE": set(),
    "T_PHYSICAL_GRADE_TEMPER": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
}

# Manual workshop decisions where a formally compatible participant has already
# left the live action scope.  These are deliberately explicit locus cards: the
# broad object-class rule remains available everywhere else.
MANUAL_DEFAULT_BLOCKERS = {
    "ACTION:G407-E2765@2:CHD": {
        "source_governor_key": "ACTION:G407-E2764@1:OK",
        "source_class": "PORTION",
        "reason": "COMPLETED_APPLICATION_BLOCKS_USED_PORTION_REFERENCE",
    },
    "ACTION:G407-E3147@1:CHD": {
        "source_governor_key": "ACTION:G407-E3145@1:S",
        "source_class": "FLOW",
        "reason": "DIVERTED_INTERNAL_FLOW_DOES_NOT_BECOME_TREATMENT_PATIENT",
    },
    "ACTION:G407-E3749@1:S": {
        "source_governor_key": "ACTION:G407-E3747@1:K",
        "source_class": "PORTION",
        "reason": "COMPLETED_TRANSFER_BLOCKS_OLD_PORTION_SELECTION",
    },
}

TYPING_SPECS = [
    {
        "typing_card_id": "T01_WRITTEN_TYPED_OBJECT",
        "short_rule_de": "Geschriebener Träger gewinnt",
        "trigger_de": "Y, AIIN, AIN oder OR gehört zum vollständigen T/CHD/S-Host.",
        "output_de": "GDT589-Packet und alle geschriebenen Teilnehmer unverändert übernehmen.",
    },
    {
        "typing_card_id": "T02_ACTION_INTERNAL_OBJECT",
        "short_rule_de": "Aktionsinterner Gegenstand",
        "trigger_de": "Trägerloses UMLEITEN oder trägerlose Stationsregulierung.",
        "output_de": "Strom beziehungsweise Stationsbedingung; ein unpassender Altgegenstand darf ihn nicht verdrängen.",
    },
    {
        "typing_card_id": "T03_BOUND_COMPATIBLE_REFERENCE",
        "short_rule_de": "Nächste kompatible getypte Quelle",
        "trigger_de": "Nach dem letzten OT/DY liegt links eine passende Quelle oder rechts im selben Ereignis ein passender Träger.",
        "output_de": "Klasse und Lemma der Quelle kopieren; unpassende Zwischentypen überspringen.",
    },
    {
        "typing_card_id": "T04_STABLE_CLASS_DEFAULT",
        "short_rule_de": "Stabiler Klassenplatz",
        "trigger_de": "Trägerloses WÄHLEN ohne passende Quelle.",
        "output_de": "Stationseinheit.",
    },
    {
        "typing_card_id": "T05_WORKPIECE_DEFAULT",
        "short_rule_de": "Konkreter Werkstückdefault",
        "trigger_de": "BEHANDELN oder TEMPERIEREN ohne kompatible Quelle; Notfall bei Badnachhandlung.",
        "output_de": "Stationsansatz; Körper nur als unbenutzter Abkühl-Notdefault.",
    },
]

REFERENCE_SPECS = [
    {
        "reference_scope_card_id": "Q01_LEFT_COMPATIBLE_ANAPHORIC",
        "short_rule_de": "Linke kompatible Quelle wiederaufnehmen",
        "direction": "LEFT",
        "reference_mode": "ANAPHORIC",
        "renderer_de": "derselbe/dieselbe/dasselbe + Quelllemma",
    },
    {
        "reference_scope_card_id": "Q02_RIGHT_SAME_EVENT_DEFINITE",
        "short_rule_de": "Rechtes gemeinsames Ereigniskomplement",
        "direction": "RIGHT",
        "reference_mode": "DEFINITE",
        "renderer_de": "der/die/das + Quelllemma",
    },
    {
        "reference_scope_card_id": "Q03_LOCAL_OR_DEFAULT_DEFINITE",
        "short_rule_de": "Geschriebenes oder aktionsinternes Objekt",
        "direction": "LOCAL_OR_DEFAULT",
        "reference_mode": "DEFINITE",
        "renderer_de": "der/die/das + Lemma",
    },
]

GENDER_BY_LEMMA = {
    "Körper": "MASCULINE",
    "Körperteil": "NEUTER",
    "Stationsansatz": "MASCULINE",
    "Strom": "MASCULINE",
    "Beckeninhalt": "MASCULINE",
    "Anwendungsportion": "FEMININE",
    "Teilmenge": "FEMININE",
    "Mengenangabe": "FEMININE",
    "Stationseinheit": "FEMININE",
    "Badeinheit": "FEMININE",
    "Becken- oder Körpereinheit": "FEMININE",
    "Stationsbedingung": "FEMININE",
    "Stationsverbindung": "FEMININE",
    "Stationsmaß": "NEUTER",
    "Stations- oder Badmaß": "NEUTER",
    "Teil": "MASCULINE",
}

DETERMINER = {
    ("DEFINITE", "MASCULINE"): "den",
    ("DEFINITE", "FEMININE"): "die",
    ("DEFINITE", "NEUTER"): "das",
    ("ANAPHORIC", "MASCULINE"): "denselben",
    ("ANAPHORIC", "FEMININE"): "dieselbe",
    ("ANAPHORIC", "NEUTER"): "dasselbe",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guarded_query(path: Path, columns: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "physical_page",
    ]
    for page in PAGES:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns)))
    command.extend(("--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats_line = next(
        line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")
    )
    stats = json.loads(stats_line.removeprefix("GUARD_STATS "))
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if stats["selected"] != len(rows):
        raise RuntimeError(f"guard count mismatch for {path.name}: {stats} vs {len(rows)}")
    if any(row["physical_page"].startswith("f84") for row in rows):
        raise RuntimeError(f"forbidden page materialized from {path.name}")
    return rows, stats


def load_inputs() -> dict[str, Any]:
    hosts, host_guard = guarded_query(INPUTS["gdt584_hosts"], HOST_COLUMNS)
    slots, slot_guard = guarded_query(INPUTS["gdt582_slots"], SLOT_COLUMNS)
    g587, g587_guard = guarded_query(INPUTS["gdt587_hosts"], G587_COLUMNS)
    g589, g589_guard = guarded_query(INPUTS["gdt589_hosts"], G589_COLUMNS)
    baths = read_tsv(INPUTS["gdt596_baths"])
    manual_workshop_review = read_tsv(INPUTS["manual_workshop_review"])
    if {row["physical_page"] for row in baths} - set(PAGES):
        raise RuntimeError("GDT596 input escaped the fixed six-page population")
    return {
        "hosts": hosts,
        "slots": slots,
        "g587": g587,
        "g589": g589,
        "baths": baths,
        "manual_workshop_review": manual_workshop_review,
        "guard_stats": {
            "gdt584_hosts": host_guard,
            "gdt582_slots": slot_guard,
            "gdt587_hosts": g587_guard,
            "gdt589_hosts": g589_guard,
        },
    }


def object_class_for_lemma(lemma: str, root: str = "") -> str:
    if lemma == "Körper":
        return "BODY"
    if lemma == "Körperteil":
        return "BODY_PART"
    if lemma in {"Stationsansatz"}:
        return "STATION"
    if lemma in {"Strom", "Beckeninhalt"}:
        return "FLOW"
    if lemma in {"Anwendungsportion", "Teil", "Teilmenge"}:
        return "PORTION"
    if lemma in {"Stationseinheit", "Badeinheit", "Becken- oder Körpereinheit"}:
        return "UNIT"
    if lemma in {"Stationsmaß", "Stations- oder Badmaß", "Mengenangabe"}:
        return "MEASURE"
    if lemma == "Stationsbedingung":
        return "CONDITION"
    return {"Y": "STATION", "AIIN": "MEASURE", "AIN": "PORTION", "OR": "UNIT"}.get(root, "STATION")


def primary_packet_object(row: dict[str, str]) -> dict[str, str]:
    lemmas = row["expected_lemma_sequence"].split("|") if row["expected_lemma_sequence"] else []
    roots = row["written_root_sequence"].split("+") if row["written_root_sequence"] else []
    packet = row["expected_packet_rule_id"]
    if packet == "BIOLOGICAL_BODY_PART":
        lemma = "Körperteil"
        object_class = "BODY_PART"
    elif packet == "BIOLOGICAL_FLOW_PACKET":
        lemma = next((item for item in ("Strom", "Beckeninhalt", "Teilmenge", "Mengenangabe") if item in lemmas), lemmas[0])
        object_class = "FLOW"
    else:
        ranked = []
        for index, lemma_value in enumerate(lemmas):
            root = roots[index] if index < len(roots) else ""
            object_class_value = object_class_for_lemma(lemma_value, root)
            rank = {
                "BODY": 0, "BODY_PART": 0, "STATION": 1, "PORTION": 2,
                "UNIT": 3, "FLOW": 4, "MEASURE": 5, "CONDITION": 6,
            }[object_class_value]
            ranked.append((rank, index, lemma_value, object_class_value))
        _rank, _index, lemma, object_class = min(ranked)
    return {
        "lemma": lemma,
        "object_class": object_class,
        "participant_lemma_sequence_de": "|".join(lemmas),
        "participant_count": str(len(lemmas)),
        "source_layer": "GDT589_WRITTEN_TARGET",
    }


def broad_carrier_object(rows: list[dict[str, str]]) -> dict[str, str]:
    ranked = []
    for index, row in enumerate(rows):
        lemma = row["gdt582_concrete_default_de"]
        object_class = object_class_for_lemma(lemma, row["slot_value"])
        rank = {"BODY": 0, "BODY_PART": 0, "STATION": 1, "PORTION": 2, "UNIT": 3, "FLOW": 4, "MEASURE": 5, "CONDITION": 6}[object_class]
        ranked.append((rank, index, lemma, object_class))
    _rank, _index, lemma, object_class = min(ranked)
    return {
        "lemma": lemma,
        "object_class": object_class,
        "participant_lemma_sequence_de": "|".join(row["gdt582_concrete_default_de"] for row in rows),
        "participant_count": str(len(rows)),
        "source_layer": "GDT582_WRITTEN_OTHER_ACTION",
    }


def bath_object(row: dict[str, str]) -> dict[str, str]:
    object_class = {"BATH_UNIT": "UNIT"}.get(row["object_class"], row["object_class"])
    return {
        "lemma": row["object_lemma_de"],
        "object_class": object_class,
        "participant_lemma_sequence_de": row["object_lemma_de"],
        "participant_count": row["participant_count"],
        "source_layer": "GDT596_COMPLETED_SH",
    }


def rendered_np(lemma: str, reference_mode: str) -> tuple[str, str, str]:
    if lemma not in GENDER_BY_LEMMA:
        raise ValueError(f"missing grammatical gender for {lemma!r}")
    gender = GENDER_BY_LEMMA[lemma]
    determiner = DETERMINER[(reference_mode, gender)]
    return f"{determiner} {lemma}", gender, determiner


def insert_object(clause: str, rule: str, object_np: str) -> str:
    if rule == "CHD_BIO_TREAT":
        marker = "Behandle den Ansatz"
        if not clause.startswith(marker):
            raise ValueError(f"unexpected carrierless CHD clause: {clause}")
        return f"Behandle {object_np}" + clause[len(marker):]
    if rule == "S_BIO_DIVERT":
        marker = "Leite den Strom"
        if not clause.startswith(marker):
            raise ValueError(f"unexpected carrierless diversion clause: {clause}")
        return f"Leite {object_np}" + clause[len(marker):]
    if rule == "S_REST_SELECT":
        marker = "Wähle die Einheit"
        if not clause.startswith(marker):
            raise ValueError(f"unexpected carrierless selection clause: {clause}")
        return f"Wähle {object_np}" + clause[len(marker):]
    if rule == "T_BIO_STATION_REGULATE":
        marker = "Reguliere die Stationsbedingung"
        if not clause.startswith(marker):
            raise ValueError(f"unexpected carrierless station clause: {clause}")
        return f"Reguliere {object_np}" + clause[len(marker):]
    if rule in {"T_AFTER_SH_COOL"}:
        marker = "Lass "
        if not clause.startswith(marker):
            raise ValueError(f"unexpected carrierless cooling clause: {clause}")
        return f"Lass {object_np} " + clause[len(marker):]
    if rule in {"T_BIO_RELATION_REGULATE", "T_PHYSICAL_GRADE_TEMPER"}:
        verb = "Reguliere" if rule == "T_BIO_RELATION_REGULATE" else "Temperiere"
        if not clause.startswith(verb):
            raise ValueError(f"unexpected carrierless T clause: {clause}")
        return f"{verb} {object_np}" + clause[len(verb):]
    raise ValueError(f"unmapped carrierless rule: {rule}")


def is_cut(host: dict[str, str]) -> bool:
    if host["action_root"] != "CONTROL":
        return False
    clause = host["gdt584_reader_clause_de"]
    return clause.startswith("Beginne danach") or clause.startswith("Schließe")


def compact_profile(counter: Counter[str]) -> str:
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def build(inputs: dict[str, Any]) -> dict[str, Any]:
    hosts = list(inputs["hosts"])
    slots = list(inputs["slots"])
    g587 = list(inputs["g587"])
    g589 = list(inputs["g589"])
    baths = list(inputs["baths"])
    manual_workshop_review = list(inputs["manual_workshop_review"])

    carrier_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        if (
            row["layer"] == "RUNNING_ATOM"
            and row["slot_value"] in CARRIER_ROOTS
            and row["primary_governor_key"].startswith("ACTION:")
        ):
            carrier_by_host[row["primary_governor_key"]].append(row)
    for rows in carrier_by_host.values():
        rows.sort(key=lambda row: (row["source_event_or_card_id"], int(row["slot_position"]), row["slot_id"]))

    g589_by = {
        row["primary_governor_key"]: row for row in g589 if row["layer"] == "RUNNING_ATOM"
    }
    bath_by = {
        f"ACTION:{row['action_slot_id'].removeprefix('RUNNING:')}:SH": row for row in baths
    }
    g587_by = {row["primary_governor_key"]: row for row in g587}

    direct_source: dict[str, dict[str, str]] = {}
    host_by_key = {row["primary_governor_key"]: row for row in hosts}
    for key, host in host_by_key.items():
        if key in bath_by:
            direct_source[key] = bath_object(bath_by[key])
        elif key in g589_by:
            direct_source[key] = primary_packet_object(g589_by[key])
        elif key in carrier_by_host:
            direct_source[key] = broad_carrier_object(carrier_by_host[key])
        if key in direct_source:
            direct_source[key] = {
                **direct_source[key],
                "source_governor_key": key,
                "source_action_root": host["action_root"],
                "source_anchor_event_id": host["anchor_event_id"],
            }

    target_hosts = [row for row in hosts if row["action_root"] in TARGET_ROOTS]
    if len(target_hosts) != 396:
        raise RuntimeError(f"target population drift: {len(target_hosts)}")
    written_target_keys = {row["primary_governor_key"] for row in target_hosts if row["primary_governor_key"] in g589_by}
    if len(written_target_keys) != 219:
        raise RuntimeError(f"written target drift: {len(written_target_keys)}")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hosts:
        by_statement[row["statement_id"]].append(row)
    for rows in by_statement.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))

    replay: list[dict[str, str]] = []
    rejected_candidates: list[dict[str, str]] = []
    for statement_id, sequence in sorted(
        by_statement.items(), key=lambda item: int(item[1][0]["host_ordinal_global"])
    ):
        history: list[dict[str, Any]] = []
        cut_ordinal = 0
        for index, host in enumerate(sequence):
            key = host["primary_governor_key"]
            if is_cut(host):
                history = []
                cut_ordinal += 1
                continue
            if host["action_root"] not in TARGET_ROOTS:
                if key in direct_source:
                    history.append({**direct_source[key], "host_index": index, "cut_ordinal": cut_ordinal})
                continue

            rule = host["gdt584_rule_id"]
            base_clause = g587_by.get(key, {}).get("gdt587_reader_clause_de", host["gdt584_reader_clause_de"])
            route = ""
            reference_scope_card_id = ""
            reference_mode = "DEFINITE"
            source_pointer = "NONE"
            source_distance = 0
            skipped_incompatible = 0
            selection_blocker = "NONE"

            if key in written_target_keys:
                selected = dict(direct_source[key])
                typing_card_id = "T01_WRITTEN_TYPED_OBJECT"
                route = "WRITTEN_GDT589_PACKET"
                reference_scope_card_id = "Q03_LOCAL_OR_DEFAULT_DEFINITE"
                completed_clause = base_clause
                source_pointer = key
            elif rule in {"T_BIO_STATION_REGULATE", "S_BIO_DIVERT"}:
                default = ACTION_DEFAULTS[rule]
                selected = {
                    "lemma": default["lemma"], "object_class": default["object_class"],
                    "participant_lemma_sequence_de": default["lemma"], "participant_count": "1",
                    "source_layer": "ACTION_INTERNAL_DEFAULT", "source_governor_key": "NONE",
                    "source_action_root": "NONE", "source_anchor_event_id": "NONE",
                }
                typing_card_id = default["typing_card_id"]
                route = (
                    "ACTION_INTERNAL_CONDITION_DEFAULT"
                    if rule == "T_BIO_STATION_REGULATE"
                    else "ACTION_INTERNAL_FLOW_DEFAULT"
                )
                reference_scope_card_id = "Q03_LOCAL_OR_DEFAULT_DEFINITE"
            else:
                compatible = COMPATIBLE_CLASSES[rule]
                chosen: dict[str, Any] | None = None
                preferred_right: tuple[dict[str, Any], int] | None = None
                force_default = False
                if rule == "T_PHYSICAL_GRADE_TEMPER" and "als neuer Bad- oder Stationsansatz" in base_clause:
                    nearest_compatible = next(
                        (candidate for candidate in reversed(history) if candidate["object_class"] in compatible),
                        None,
                    )
                    if nearest_compatible is not None and nearest_compatible["object_class"] == "BODY":
                        force_default = True
                        selection_blocker = "NEW_BATCH_MARKER_BLOCKS_BODY_REFERENCE"
                        skipped_incompatible += 1
                        rejected_candidates.append({
                            "target_governor_key": key,
                            "target_rule_id": rule,
                            "rejected_source_governor_key": nearest_compatible["source_governor_key"],
                            "rejected_source_class": nearest_compatible["object_class"],
                            "rejected_source_lemma_de": nearest_compatible["lemma"],
                            "reason": selection_blocker,
                        })
                manual_blocker = MANUAL_DEFAULT_BLOCKERS.get(key)
                if manual_blocker is not None:
                    blocked_candidate = next(
                        (
                            candidate for candidate in reversed(history)
                            if candidate["source_governor_key"] == manual_blocker["source_governor_key"]
                            and candidate["object_class"] == manual_blocker["source_class"]
                        ),
                        None,
                    )
                    if blocked_candidate is None:
                        raise RuntimeError(f"manual blocker source missing for {key}")
                    if not force_default:
                        force_default = True
                        selection_blocker = manual_blocker["reason"]
                        skipped_incompatible += 1
                        rejected_candidates.append({
                            "target_governor_key": key,
                            "target_rule_id": rule,
                            "rejected_source_governor_key": blocked_candidate["source_governor_key"],
                            "rejected_source_class": blocked_candidate["object_class"],
                            "rejected_source_lemma_de": blocked_candidate["lemma"],
                            "reason": selection_blocker,
                        })
                if not force_default and rule == "S_REST_SELECT":
                    same_event_left = next(
                        (
                            candidate for candidate in reversed(history)
                            if candidate["object_class"] in compatible
                            and candidate["source_anchor_event_id"] == host["anchor_event_id"]
                        ),
                        None,
                    )
                    older_left = next(
                        (candidate for candidate in reversed(history) if candidate["object_class"] in compatible),
                        None,
                    )
                    local_right: tuple[dict[str, Any], int] | None = None
                    for future_index in range(index + 1, len(sequence)):
                        future = sequence[future_index]
                        if is_cut(future) or future["anchor_event_id"] != host["anchor_event_id"]:
                            break
                        candidate = direct_source.get(future["primary_governor_key"])
                        if (
                            candidate
                            and future["action_root"] in {"SH", "S"}
                            and candidate["object_class"] in compatible
                        ):
                            local_right = (candidate, future_index - index)
                            break
                    if (
                        same_event_left is None
                        and older_left is not None
                        and local_right is not None
                        and local_right[0]["lemma"] != older_left["lemma"]
                    ):
                        preferred_right = local_right
                        selection_blocker = "LOCAL_RIGHT_DIFFERENT_OBJECT_OUTRANKS_OLDER_LEFT"
                # Cooling and relation regulation first look for the SH object in the same event.
                if not force_default and rule in {"T_AFTER_SH_COOL", "T_BIO_RELATION_REGULATE"}:
                    for candidate in reversed(history):
                        if (
                            candidate["source_action_root"] == "SH"
                            and candidate["source_anchor_event_id"] == host["anchor_event_id"]
                            and candidate["object_class"] in compatible
                        ):
                            chosen = candidate
                            break
                if chosen is None and not force_default and preferred_right is None:
                    for candidate in reversed(history):
                        if candidate["object_class"] in compatible:
                            if rule == "T_PHYSICAL_GRADE_TEMPER" and skipped_incompatible >= 2:
                                force_default = True
                                selection_blocker = "TWO_MEASURE_PARAMETERS_BLOCK_FAR_PARTICIPANT_REFERENCE"
                                rejected_candidates.append({
                                    "target_governor_key": key,
                                    "target_rule_id": rule,
                                    "rejected_source_governor_key": candidate["source_governor_key"],
                                    "rejected_source_class": candidate["object_class"],
                                    "rejected_source_lemma_de": candidate["lemma"],
                                    "reason": selection_blocker,
                                })
                            else:
                                chosen = candidate
                            break
                        skipped_incompatible += 1
                        rejected_candidates.append({
                            "target_governor_key": key,
                            "target_rule_id": rule,
                            "rejected_source_governor_key": candidate["source_governor_key"],
                            "rejected_source_class": candidate["object_class"],
                            "rejected_source_lemma_de": candidate["lemma"],
                            "reason": "INCOMPATIBLE_WITH_ACTION_RULE",
                        })
                if chosen is not None:
                    selected = dict(chosen)
                    typing_card_id = "T03_BOUND_COMPATIBLE_REFERENCE"
                    route = "LEFT_COMPATIBLE_TYPED_SOURCE"
                    reference_scope_card_id = "Q01_LEFT_COMPATIBLE_ANAPHORIC"
                    reference_mode = "ANAPHORIC"
                    source_pointer = chosen["source_governor_key"]
                    source_distance = index - int(chosen["host_index"])
                else:
                    right = preferred_right[0] if preferred_right is not None else None
                    right_distance = preferred_right[1] if preferred_right is not None else 0
                    if right is None:
                        for future_index in (range(index + 1, len(sequence)) if not force_default else ()):
                            future = sequence[future_index]
                            if is_cut(future) or future["anchor_event_id"] != host["anchor_event_id"]:
                                break
                            candidate = direct_source.get(future["primary_governor_key"])
                            if candidate and candidate["object_class"] in compatible:
                                right = candidate
                                right_distance = future_index - index
                                break
                    if right is not None:
                        selected = dict(right)
                        typing_card_id = "T03_BOUND_COMPATIBLE_REFERENCE"
                        route = "RIGHT_SAME_EVENT_COMPATIBLE_SOURCE"
                        reference_scope_card_id = "Q02_RIGHT_SAME_EVENT_DEFINITE"
                        source_pointer = right["source_governor_key"]
                        source_distance = right_distance
                    else:
                        default = ACTION_DEFAULTS[rule]
                        selected = {
                            "lemma": default["lemma"], "object_class": default["object_class"],
                            "participant_lemma_sequence_de": default["lemma"], "participant_count": "1",
                            "source_layer": "ACTION_RULE_DEFAULT", "source_governor_key": "NONE",
                            "source_action_root": "NONE", "source_anchor_event_id": "NONE",
                        }
                        typing_card_id = default["typing_card_id"]
                        route = "ACTION_RULE_TYPED_DEFAULT"
                        reference_scope_card_id = "Q03_LOCAL_OR_DEFAULT_DEFINITE"

            object_np, gender, determiner = rendered_np(selected["lemma"], reference_mode)
            if key not in written_target_keys:
                completed_clause = insert_object(base_clause, rule, object_np)
            replay.append({
                "action_ordinal": str(len(replay) + 1),
                "statement_id": statement_id,
                "host_ordinal_in_statement": host["host_ordinal_in_statement"],
                "physical_page": host["physical_page"],
                "primary_governor_key": key,
                "action_slot_id": host["action_slot_id"],
                "anchor_event_id": host["anchor_event_id"],
                "action_root": host["action_root"],
                "gdt584_rule_id": rule,
                "written_carrier_count": g589_by[key]["carrier_slot_count"] if key in g589_by else "0",
                "written_carrier_roots": g589_by[key]["written_root_sequence"] if key in g589_by else "NONE",
                "typing_card_id": typing_card_id,
                "reference_scope_card_id": reference_scope_card_id,
                "selection_route": route,
                "source_pointer": source_pointer,
                "source_distance_hosts": str(source_distance),
                "skipped_incompatible_source_count": str(skipped_incompatible),
                "selection_blocker": selection_blocker,
                "source_layer": selected["source_layer"],
                "reference_mode": reference_mode,
                "object_class": selected["object_class"],
                "object_lemma_de": selected["lemma"],
                "grammatical_gender": gender,
                "determiner_de": determiner,
                "rendered_object_np_de": object_np,
                "participant_count": selected["participant_count"],
                "participant_lemma_sequence_de": selected["participant_lemma_sequence_de"],
                "upstream_clause_de": base_clause,
                "gdt597_completed_clause_de": completed_clause,
                "default_is_replaceable": "YES",
                "guard": "WRITTEN_FIRST__OT_DY_CUT__COMPATIBLE_TYPED_REFERENCE__ACTION_DEFAULT__NO_NEW_PAGE_ROOT_OR_SEGMENT",
            })
            history.append({
                **selected,
                "source_governor_key": key,
                "source_action_root": host["action_root"],
                "source_anchor_event_id": host["anchor_event_id"],
                "host_index": index,
                "cut_ordinal": cut_ordinal,
            })

    by_typing: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_reference: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        by_typing[row["typing_card_id"]].append(row)
        by_reference[row["reference_scope_card_id"]].append(row)

    typing_cards = []
    for order, spec in enumerate(TYPING_SPECS, start=1):
        members = by_typing[spec["typing_card_id"]]
        typing_cards.append({
            "typing_card_order": str(order), **spec,
            "occurrence_count": str(len(members)),
            "rule_profile": compact_profile(Counter(row["gdt584_rule_id"] for row in members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "example_governor_key": members[0]["primary_governor_key"],
            "example_clause_de": members[0]["gdt597_completed_clause_de"],
        })

    reference_cards = []
    for order, spec in enumerate(REFERENCE_SPECS, start=1):
        members = by_reference[spec["reference_scope_card_id"]]
        reference_cards.append({
            "reference_scope_card_order": str(order), **spec,
            "occurrence_count": str(len(members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "example_governor_key": members[0]["primary_governor_key"],
            "example_clause_de": members[0]["gdt597_completed_clause_de"],
        })

    default_cards = []
    for order, (rule, spec) in enumerate(ACTION_DEFAULTS.items(), start=1):
        members = [row for row in replay if row["gdt584_rule_id"] == rule]
        defaults = [row for row in members if row["selection_route"].startswith("ACTION_")]
        default_cards.append({
            "default_card_order": str(order),
            "gdt584_rule_id": rule,
            "action_root": members[0]["action_root"],
            "default_object_class": spec["object_class"],
            "default_lemma_de": spec["lemma"],
            "typing_card_id": spec["typing_card_id"],
            "reason_de": spec["reason_de"],
            "total_occurrence_count": str(len(members)),
            "carrierless_occurrence_count": str(sum(row["written_carrier_count"] == "0" for row in members)),
            "default_used_count": str(len(defaults)),
        })

    compatibility_cards = []
    for order, (rule, classes) in enumerate(COMPATIBLE_CLASSES.items(), start=1):
        members = [row for row in replay if row["gdt584_rule_id"] == rule]
        refs = [row for row in members if row["typing_card_id"] == "T03_BOUND_COMPATIBLE_REFERENCE"]
        compatibility_cards.append({
            "compatibility_card_order": str(order),
            "gdt584_rule_id": rule,
            "compatible_object_classes": "|".join(sorted(classes)) or "NONE__INTERNAL_OBJECT_ONLY",
            "reference_occurrence_count": str(len(refs)),
            "reference_class_profile": compact_profile(Counter(row["object_class"] for row in refs)) or "NONE",
            "skipped_incompatible_candidate_count": str(sum(int(row["skipped_incompatible_source_count"]) for row in members)),
        })

    determiner_cells = []
    for order, ((reference_mode, gender), determiner) in enumerate(
        sorted(DETERMINER.items(), key=lambda item: (item[0][0], item[0][1])), start=1
    ):
        members = [
            row for row in replay
            if row["reference_mode"] == reference_mode and row["grammatical_gender"] == gender
        ]
        determiner_cells.append({
            "determiner_cell_order": str(order),
            "reference_mode": reference_mode,
            "grammatical_gender": gender,
            "determiner_de": determiner,
            "occurrence_count": str(len(members)),
            "observed_in_gdt597": "YES" if members else "NO",
            "example_object_np_de": members[0]["rendered_object_np_de"] if members else "GRAMMATICAL_COMPLEMENT_WITHOUT_CURRENT_OCCURRENCE",
        })

    form_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        key = (
            row["object_class"], row["object_lemma_de"], row["grammatical_gender"],
            row["reference_mode"], row["determiner_de"], row["rendered_object_np_de"],
        )
        form_groups[key].append(row)
    object_forms = []
    for order, (key, members) in enumerate(sorted(form_groups.items()), start=1):
        object_class, lemma, gender, reference_mode, determiner, rendered = key
        object_forms.append({
            "object_form_order": str(order),
            "object_class": object_class,
            "object_lemma_de": lemma,
            "grammatical_gender": gender,
            "reference_mode": reference_mode,
            "determiner_de": determiner,
            "rendered_object_np_de": rendered,
            "occurrence_count": str(len(members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
        })

    page_rows = []
    for page in PAGES:
        members = [row for row in replay if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "action_count": str(len(members)),
            "root_profile": compact_profile(Counter(row["action_root"] for row in members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
            "reference_scope_profile": compact_profile(Counter(row["reference_scope_card_id"] for row in members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "written_count": str(sum(row["written_carrier_count"] != "0" for row in members)),
            "carrierless_count": str(sum(row["written_carrier_count"] == "0" for row in members)),
        })

    long_references = [
        {
            "primary_governor_key": row["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "gdt584_rule_id": row["gdt584_rule_id"],
            "source_pointer": row["source_pointer"],
            "source_distance_hosts": row["source_distance_hosts"],
            "skipped_incompatible_source_count": row["skipped_incompatible_source_count"],
            "selection_blocker": row["selection_blocker"],
            "object_lemma_de": row["object_lemma_de"],
            "gdt597_completed_clause_de": row["gdt597_completed_clause_de"],
            "review_reason": "DISTANCE_OVER_FIVE_OR_INCOMPATIBLE_OBJECT_SKIPPED",
        }
        for row in replay
        if int(row["source_distance_hosts"]) > 5 or int(row["skipped_incompatible_source_count"]) > 0
    ]

    replay_by_key = {row["primary_governor_key"]: row for row in replay}
    workshop_reviews = []
    for source in manual_workshop_review:
        row = replay_by_key.get(source["primary_governor_key"])
        if row is None:
            raise RuntimeError(f"manual review target missing: {source['primary_governor_key']}")
        expected = {
            "statement_id": source["statement_id"],
            "selection_route": source["expected_selection_route"],
            "source_pointer": source["expected_source_pointer"],
            "object_lemma_de": source["expected_object_lemma_de"],
        }
        observed = {name: row[name] for name in expected}
        if observed != expected:
            raise RuntimeError(
                f"manual review drift for {source['primary_governor_key']}: {observed} != {expected}"
            )
        workshop_reviews.append({
            "review_id": source["review_id"],
            "primary_governor_key": row["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "review_class": source["review_class"],
            "selection_route": row["selection_route"],
            "source_pointer": row["source_pointer"],
            "object_lemma_de": row["object_lemma_de"],
            "selection_blocker": row["selection_blocker"],
            "completed_clause_de": row["gdt597_completed_clause_de"],
            "workshop_reason_de": source["workshop_reason_de"],
            "retained_rival_de": source["retained_rival_de"],
            "decision_de": source["decision_de"],
        })

    typing_profile = Counter(row["typing_card_id"] for row in replay)
    reference_profile = Counter(row["reference_scope_card_id"] for row in replay)
    object_profile = Counter(row["object_class"] for row in replay)
    rule_profile = Counter(row["gdt584_rule_id"] for row in replay)
    result = {
        "experiment_id": "GDT597",
        "status": STATUS,
        "action_count": len(replay),
        "root_profile": dict(sorted(Counter(row["action_root"] for row in replay).items())),
        "rule_profile": dict(sorted(rule_profile.items())),
        "written_action_count": sum(row["written_carrier_count"] != "0" for row in replay),
        "carrierless_action_count": sum(row["written_carrier_count"] == "0" for row in replay),
        "typing_card_profile": dict(sorted(typing_profile.items())),
        "reference_scope_card_profile": dict(sorted(reference_profile.items())),
        "reference_mode_profile": dict(sorted(Counter(row["reference_mode"] for row in replay).items())),
        "object_class_profile": dict(sorted(object_profile.items())),
        "object_lemma_profile": dict(sorted(Counter(row["object_lemma_de"] for row in replay).items())),
        "grammatical_gender_profile": dict(sorted(Counter(row["grammatical_gender"] for row in replay).items())),
        "determiner_cell_count": len(determiner_cells),
        "observed_determiner_cell_count": sum(row["observed_in_gdt597"] == "YES" for row in determiner_cells),
        "observed_object_form_count": len(object_forms),
        "left_reference_count": sum(row["selection_route"] == "LEFT_COMPATIBLE_TYPED_SOURCE" for row in replay),
        "right_reference_count": sum(row["selection_route"] == "RIGHT_SAME_EVENT_COMPATIBLE_SOURCE" for row in replay),
        "action_default_count": sum(row["selection_route"].startswith("ACTION_") for row in replay),
        "long_reference_review_count": len(long_references),
        "rejected_incompatible_candidate_count": len(rejected_candidates),
        "manual_workshop_review_count": len(workshop_reviews),
        "manual_workshop_review_class_profile": dict(sorted(Counter(row["review_class"] for row in workshop_reviews).items())),
        "guard_stats": inputs["guard_stats"],
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "working_rule_de": (
            "Geschriebener Träger gewinnt. Nach jedem OT/DY-Cut sucht eine trägerlose Aktion rückwärts "
            "die nächste mit ihrer Aktionsklasse kompatible getypte Quelle; ein gemeinsames rechtes "
            "Ereigniskomplement folgt erst danach. Trägerlose Stationsregulierung behält immer die "
            "Stationsbedingung. Bleibt keine Quelle, liefert jede der sieben Aktionsregeln einen konkreten Default."
        ),
    }

    built: dict[str, Any] = {
        "typing_cards": typing_cards,
        "reference_cards": reference_cards,
        "default_cards": default_cards,
        "compatibility_cards": compatibility_cards,
        "determiner_cells": determiner_cells,
        "object_forms": object_forms,
        "replay": replay,
        "pages": page_rows,
        "long_references": long_references,
        "rejected_candidates": rejected_candidates,
        "workshop_reviews": workshop_reviews,
        "result": result,
    }
    built["phrasebook"] = render_phrasebook(built)
    return built


def render_phrasebook(built: dict[str, Any]) -> str:
    result = built["result"]
    lines = [
        "# GDT597 — Nicht-SH-Objekt- und Referenzphrasebook",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Ergebnis des aktuellen Builds",
        "",
        f"Alle {result['action_count']} laufenden T/CHD/S-Aktionen der sechs Badseiten besitzen einen konkreten Gegenstand.",
        f"{result['written_action_count']} lesen ihren geschriebenen Träger; {result['left_reference_count']} übernehmen eine kompatible linke Quelle,",
        f"{result['right_reference_count']} teilen ein rechtes Ereigniskomplement und {result['action_default_count']} verwenden einen Aktionsdefault.",
        "",
        "## Fünf Typkarten",
        "",
        "| Karte | Kurzregel | n | Klassen |",
        "|---|---|---:|---|",
    ]
    for row in built["typing_cards"]:
        lines.append(f"| `{row['typing_card_id']}` | {row['short_rule_de']} | {row['occurrence_count']} | `{row['object_class_profile']}` |")
    lines.extend([
        "",
        "## Drei Bezugskarten",
        "",
        "| Karte | Richtung | Modus | n |",
        "|---|---|---|---:|",
    ])
    for row in built["reference_cards"]:
        lines.append(f"| `{row['reference_scope_card_id']}` | {row['direction']} | {row['reference_mode']} | {row['occurrence_count']} |")
    lines.extend([
        "",
        "## Sieben Defaults",
        "",
        "| Aktionsregel | Default | genutzt |",
        "|---|---|---:|",
    ])
    for row in built["default_cards"]:
        lines.append(f"| `{row['gdt584_rule_id']}` | {row['default_lemma_de']} | {row['default_used_count']} |")
    lines.extend([
        "",
        "## Flexion",
        "",
        "Die sechs Zellen männlich/weiblich/sächlich × definit/anaphorisch erzeugen alle 18 beobachteten Objektformen.",
        "Gegenüber GDT596 kommen `das` und das nun tatsächlich dreimal verwendete `dasselbe` hinzu.",
        "",
        "Die Bedeutungen bleiben bewusst austauschbare Arbeitsdefaults. Jede neue sichtbare kompatible Quelle gewinnt sofort;",
        f"{result['manual_workshop_review_count']} schwierige Bindungsentscheidungen bleiben als Werkstattkarten sichtbar.",
        "Keine neue Seite, Wurzel, Segmentierung oder Substringanalyse wurde geöffnet.",
        "",
    ])
    return "\n".join(lines)


def tsv_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    row_list = list(rows)
    if not row_list:
        return b""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(row_list[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(row_list)
    return stream.getvalue().encode("utf-8")


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_bytes(tsv_bytes(rows))


def write_built(built: dict[str, Any]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in ("typing_cards", "reference_cards", "default_cards", "compatibility_cards", "determiner_cells", "object_forms", "replay", "pages", "long_references", "rejected_candidates", "workshop_reviews"):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["phrasebook"].write_text(built["phrasebook"], encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
