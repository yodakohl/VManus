#!/usr/bin/env python3
"""Complete every remaining six-page action object in the GDT598 host stream.

GDT599 deliberately consumes only the already-published, six-page GDT598
artifacts.  It does not reopen a transcription, parser, page, root, or segment.
The model is a small typed discourse-state machine: participant objects and
measure/condition parameters remain separate, OT/DY end the live state, and a
CARRIER_Q clause commits a new station only after its input has been read.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt599_remaining_action_object_completion"
ARTIFACTS = BASE / "artifacts"
G598 = ROOT / "experiments/yolo/gdt598_six_page_object_statement_integration/artifacts"
PAGES = ("f75r", "f77r", "f81r", "f81v", "f82r", "f83r")
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
TARGET_ROOTS = {"CH", "K", "OK", "P", "R", "SH"}
PARTICIPANT_CLASSES = {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"}
PARAMETER_CLASSES = {"MEASURE", "CONDITION"}
Q_MARKER = "als neuer Bad- oder Stationsansatz"
Q_MARKER_ACCUSATIVE = "als neuen Bad- oder Stationsansatz"
GUARD = "GDT598_SIX_PAGE_ARTIFACTS_ONLY__NO_NEW_PAGE_ROOT_PARSER_OR_SEGMENT"


INPUTS = {
    "hosts": G598 / "gdt598_2272_integrated_host_edition.tsv",
    "gaps": G598 / "gdt598_793_remaining_action_gaps.tsv",
    "local_cards": G598 / "gdt598_40_local_card_passthrough.tsv",
    "manual_reviews": G598 / "gdt598_40_namespaced_manual_reviews.tsv",
    "manual_overrides": BASE / "sources/gdt599_manual_object_overrides.tsv",
    "aiin_substrate_overrides": BASE / "sources/gdt599_aiin_substrate_overrides.tsv",
    "manual_clause_polish": BASE / "sources/gdt599_manual_clause_polish.tsv",
}

OUTPUTS = {
    "replay": ARTIFACTS / "gdt599_793_remaining_action_object_replay.tsv",
    "actions": ARTIFACTS / "gdt599_1443_complete_action_edition.tsv",
    "hosts": ARTIFACTS / "gdt599_2272_complete_host_edition.tsv",
    "statements": ARTIFACTS / "gdt599_313_complete_statements.tsv",
    "typing_cards": ARTIFACTS / "gdt599_8_selection_route_cards.tsv",
    "reference_cards": ARTIFACTS / "gdt599_3_reference_scope_cards.tsv",
    "defaults": ARTIFACTS / "gdt599_6_root_default_cards.tsv",
    "compatibility": ARTIFACTS / "gdt599_6_compatibility_cards.tsv",
    "q_transitions": ARTIFACTS / "gdt599_24_action_q_result_transitions.tsv",
    "manual_decisions": ARTIFACTS / "gdt599_11_manual_workshop_decisions.tsv",
    "propagation_effects": ARTIFACTS / "gdt599_3_override_propagation_effects.tsv",
    "aiin_bindings": ARTIFACTS / "gdt599_46_aiin_quantity_bindings.tsv",
    "clause_polish": ARTIFACTS / "gdt599_3_manual_clause_polish.tsv",
    "review_queue": ARTIFACTS / "gdt599_projection_review_queue.tsv",
    "pages": ARTIFACTS / "gdt599_6_page_profiles.tsv",
    "local_cards": ARTIFACTS / "gdt599_40_local_card_passthrough.tsv",
    "manual_reviews": ARTIFACTS / "gdt599_40_inherited_manual_reviews.tsv",
    "reader": ARTIFACTS / "GDT599_COMPLETE_OBJECT_READER.md",
    "result": ARTIFACTS / "gdt599_result.json",
    "validation": ARTIFACTS / "gdt599_validation.json",
}


ROOT_DEFAULTS = {
    "CH": ("STATION", "Stationsansatz", "Entnahme/Ablass braucht ohne lokale Quelle einen konkreten Arbeitsansatz."),
    "K": ("STATION", "Stationsansatz", "Zuführen nimmt ohne lokale Quelle den laufenden Arbeitsansatz."),
    "OK": ("STATION", "Stationsansatz", "Beschicken/Vorbereiten nimmt ohne lokale Quelle den Arbeitsansatz."),
    "P": ("PORTION", "Anwendungsportion", "Anwenden nimmt ohne lokale Quelle eine konkrete Anwendungsportion."),
    "R": ("STATION", "Stationsansatz", "Kennzeichnen/Prüfen nimmt ohne lokale Quelle den Arbeitsansatz."),
    "SH": ("CONDITION", "Stationsbedingung", "Generisches Halten ohne Teilnehmerquelle hält als Restlesart die Stationsbedingung."),
}

COMPATIBLE_CLASSES = {
    "CH": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
    "K": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
    "OK": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT"},
    "P": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT"},
    "R": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW", "MEASURE", "CONDITION"},
    "SH": {"BODY", "BODY_PART", "STATION", "PORTION", "UNIT", "FLOW"},
}

SELECTION_CARD_SPECS = [
    ("T01_OWN_WRITTEN_PARTICIPANT", "Eigener geschriebener Teilnehmer", "Y/AIN/OR im Zielhost; Teilnehmer vor Parameter lesen."),
    ("T02_OWN_AIIN_PARAMETER", "Eigenes geschriebenes Maß", "AIIN ohne Y/AIN/OR bleibt lokaler MEASURE-Parameter und sucht keinen Fernpatienten."),
    ("T03_EXACT_CH_SH_BRIDGE", "Exakte CH→SH-Brücke", "SH_CH_BRIDGE_HOLD kopiert das unmittelbar vorangehende CH-Objekt."),
    ("T04_RIGHT_SAME_EVENT_WRITTEN", "Rechter geschriebener Ereignisteilnehmer", "Nächster kompatibler geschriebener Teilnehmer desselben Ereignisses."),
    ("T05_LEFT_COMPATIBLE_STATE", "Linker kompatibler Zustand", "Nächster kompatibler Eintrag nach dem letzten OT/DY."),
    ("T06_RIGHT_BOUNDED_COMPLETED_OR_DEFAULT", "Rechter begrenzter Ergänzer", "Nur ohne linke Quelle: kompatible fertige/defaultierte Handlung desselben Ereignisses."),
    ("T07_ROOT_DEFAULT", "Konkreter Wurzeldefault", "Kein lokaler oder gebundener Kandidat; ersetzbarer Default der Aktionswurzel."),
    ("T08_LOCAL_WORKSHOP_OVERRIDE", "Lokale Werkstattkorrektur", "Konkreter Pfad-, Q- oder Übergabekontext ersetzt eine andernfalls holprige Regelprojektion."),
]

REFERENCE_CARD_SPECS = [
    ("Q01_LEFT_ANAPHORIC", "LEFT", "ANAPHORIC", "derselbe/dieselbe/dasselbe + Quelllemma"),
    ("Q02_RIGHT_DEFINITE", "RIGHT", "DEFINITE", "der/die/das + Quelllemma"),
    ("Q03_LOCAL_OR_DEFAULT_DEFINITE", "LOCAL_OR_DEFAULT", "DEFINITE", "der/die/das + Lemma"),
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
    "Stationsmaß": "NEUTER",
    "Stations- oder Badmaß": "NEUTER",
    "abgemessene Menge": "FEMININE",
    "Maßangabe": "FEMININE",
    "Inhalt der Becken- oder Körpereinheit": "MASCULINE",
    "Probe": "FEMININE",
}

DETERMINERS = {
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


def load_inputs() -> dict[str, Any]:
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    if len(data["hosts"]) != 2272 or len(data["gaps"]) != 793:
        raise RuntimeError("GDT598 population drift")
    if len(data["local_cards"]) != 40 or len(data["manual_reviews"]) != 40:
        raise RuntimeError("GDT598 passthrough population drift")
    if len(data["manual_overrides"]) != 11:
        raise RuntimeError("GDT599 manual override population drift")
    if len(data["aiin_substrate_overrides"]) != 1:
        raise RuntimeError("GDT599 AIIN substrate override population drift")
    if len(data["manual_clause_polish"]) != 3:
        raise RuntimeError("GDT599 manual clause polish population drift")
    if {row["physical_page"] for row in data["hosts"]} - set(PAGES):
        raise RuntimeError("GDT598 host artifact escaped the fixed six pages")
    if any(row["physical_page"].startswith("f84") for row in data["hosts"]):
        raise RuntimeError("forbidden page in GDT598 host artifact")
    return data


def compact_profile(counter: Counter[str]) -> str:
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def sentence_case(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" ;.")
    return cleaned[:1].upper() + cleaned[1:] if cleaned else ""


def compose_paragraphs(rows: list[dict[str, str]], field: str) -> tuple[str, int]:
    paragraphs: list[list[str]] = [[]]
    for row in rows:
        clause = sentence_case(row[field])
        if clause:
            paragraphs[-1].append(clause + ".")
        if row["paragraph_boundary"] == "PARAGRAPH_AFTER" and paragraphs[-1]:
            paragraphs.append([])
    nonempty = [paragraph for paragraph in paragraphs if paragraph]
    return "\n\n".join(" ".join(paragraph) for paragraph in nonempty), len(nonempty)


def is_cut(row: dict[str, str]) -> bool:
    return row["action_root"] == "CONTROL" and row["primary_governor_key"].rsplit(":", 1)[-1] in {"OT", "DY"}


def has_q(row: dict[str, str]) -> bool:
    return Q_MARKER in row["gdt598_integrated_clause_de"]


def polish_action_q_case(clause: str) -> str:
    return clause.replace(Q_MARKER, Q_MARKER_ACCUSATIVE)


def split_action_q_result(clause: str, primary_governor_key: str) -> str:
    """Remove embedded Q and append its result as a second, explicit clause."""
    text = polish_action_q_case(clause)
    marker = Q_MARKER_ACCUSATIVE
    replacements = (
        (f", {marker},", ","),
        (f", {marker} und ", " und "),
        (f" und {marker}, ", ", "),
        (f" und {marker}", ""),
        (f", {marker}", ""),
        (f" {marker}", ""),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+", " ", text).strip(" ;,")
    result_clause = {
        "ACTION:G407-E3377@4:S": "übernimm die ausgewählte Einheit als neuen Bad- oder Stationsansatz",
        "ACTION:G407-E3559@3:CH": "übernimm den Ablauf als neuen Bad- oder Stationsansatz",
    }.get(primary_governor_key, "übernimm das Ergebnis als neuen Bad- oder Stationsansatz")
    return f"{text}; {result_clause}"


def class_for_lemma(lemma: str, root: str = "") -> str:
    table = {
        "Körper": "BODY",
        "Körperteil": "BODY_PART",
        "Stationsansatz": "STATION",
        "Strom": "FLOW",
        "Beckeninhalt": "FLOW",
        "Anwendungsportion": "PORTION",
        "Teilmenge": "PORTION",
        "Mengenangabe": "MEASURE",
        "Stationseinheit": "UNIT",
        "Badeinheit": "UNIT",
        "Becken- oder Körpereinheit": "UNIT",
        "Stationsbedingung": "CONDITION",
        "Stationsmaß": "MEASURE",
        "Stations- oder Badmaß": "MEASURE",
    }
    return table.get(lemma, {"Y": "STATION", "AIN": "PORTION", "OR": "UNIT", "AIIN": "MEASURE"}.get(root, "STATION"))


def written_packet(row: dict[str, str]) -> dict[str, Any] | None:
    roots_text = row["written_carrier_roots"]
    if roots_text == "NONE":
        return None
    roots = roots_text.split("+")
    lemmas = row["written_carrier_lemmas_de"].split("|")
    if len(roots) != len(lemmas):
        raise RuntimeError(f"written packet length mismatch at {row['primary_governor_key']}")
    cells = [
        {"root": root, "lemma": lemma, "object_class": class_for_lemma(lemma, root)}
        for root, lemma in zip(roots, lemmas)
    ]
    participants = [cell for cell in cells if cell["root"] in {"Y", "AIN", "OR"}]
    parameters = [cell for cell in cells if cell["root"] == "AIIN"]
    if participants:
        ranks = {"STATION": 0, "BODY": 0, "BODY_PART": 0, "PORTION": 1, "UNIT": 2, "FLOW": 3}
        selected = min(enumerate(participants), key=lambda pair: (ranks[pair[1]["object_class"]], pair[0]))[1]
        route = "PARTICIPANT"
    elif parameters:
        selected = parameters[0]
        route = "AIIN_ONLY_PARAMETER"
    else:
        raise RuntimeError(f"unclassified written packet at {row['primary_governor_key']}")
    unique_lemmas = list(dict.fromkeys(cell["lemma"] for cell in cells))
    return {
        **selected,
        "packet_route": route,
        "raw_root_sequence": "+".join(roots),
        "raw_lemma_sequence": "|".join(lemmas),
        "stable_unique_lemma_sequence": "|".join(unique_lemmas),
        "parameter_count": len(parameters),
        "participant_count": len(participants),
    }


def rendered_np(lemma: str, reference_mode: str) -> tuple[str, str, str]:
    if lemma not in GENDER_BY_LEMMA:
        raise RuntimeError(f"missing gender for {lemma!r}")
    gender = GENDER_BY_LEMMA[lemma]
    determiner = DETERMINERS[(reference_mode, gender)]
    return f"{determiner} {lemma}", gender, determiner


def insert_object(
    row: dict[str, str], object_np: str, object_class: str, renderer_policy: str = "RULE_DEFAULT"
) -> str:
    clause = row["gdt584_upstream_clause_de"]
    root = row["action_root"]
    if root == "SH":
        marker = "Halte den Zustand"
        if not clause.startswith(marker):
            raise RuntimeError(f"unexpected SH frame at {row['primary_governor_key']}: {clause}")
        if object_class in {"CONDITION", "FLOW"}:
            return f"Halte {object_np}" + clause[len(marker):] + " aufrecht"
        return f"Halte {object_np}" + clause[len(marker):]
    if root == "CH" and renderer_policy == "CH_SAMPLE":
        marker = "Entnimm oder lass"
        if not clause.startswith(marker) or not clause.endswith(" ab"):
            raise RuntimeError(f"unexpected CH sample frame at {row['primary_governor_key']}: {clause}")
        modifier_body = clause[len(marker):-len(" ab")]
        return f"Entnimm {object_np} am selben Körperteil{modifier_body}"
    if root == "CH" and object_class in {"BODY", "BODY_PART", "UNIT", "PORTION"}:
        marker = "Entnimm oder lass"
        if not clause.startswith(marker) or not clause.endswith(" ab"):
            raise RuntimeError(f"unexpected CH body frame at {row['primary_governor_key']}: {clause}")
        modifier_body = clause[len(marker):-len(" ab")]
        return f"Nimm {object_np}{modifier_body} heraus"
    if root == "CH" and object_class == "FLOW":
        marker = "Entnimm oder lass"
        if not clause.startswith(marker):
            raise RuntimeError(f"unexpected CH flow frame at {row['primary_governor_key']}: {clause}")
        return f"Lass {object_np}" + clause[len(marker):]
    if root == "P" and (object_class in {"BODY", "BODY_PART", "UNIT", "STATION"} or renderer_policy == "P_INSERT"):
        marker = "Wende"
        if not clause.startswith(marker) or not clause.endswith(" an"):
            raise RuntimeError(f"unexpected P insertion frame at {row['primary_governor_key']}: {clause}")
        modifier_body = clause[len(marker):-len(" an")]
        return f"Setze {object_np}{modifier_body} ein"
    if root == "K" and object_class in {"BODY", "BODY_PART", "UNIT"}:
        marker = "Führe"
        if not clause.startswith(marker) or not clause.endswith(" zu"):
            raise RuntimeError(f"unexpected K workpiece frame at {row['primary_governor_key']}: {clause}")
        modifier_body = clause[len(marker):-len(" zu")]
        return f"Bringe {object_np}{modifier_body} ein"
    if root == "OK" and object_class in {"BODY", "BODY_PART", "PORTION"}:
        marker = "Beschicke oder bereite"
        if not clause.startswith(marker):
            raise RuntimeError(f"unexpected OK body frame at {row['primary_governor_key']}: {clause}")
        return f"Bereite {object_np}" + clause[len(marker):]
    markers = {
        "CH": "Entnimm oder lass",
        "K": "Führe",
        "P": "Wende",
        "OK": "Beschicke oder bereite",
        "R": "Kennzeichne oder prüfe",
    }
    marker = markers[root]
    if not clause.startswith(marker):
        raise RuntimeError(f"unexpected {root} frame at {row['primary_governor_key']}: {clause}")
    return f"{marker} {object_np}" + clause[len(marker):]


def render_aiin_only(
    row: dict[str, str], selected: dict[str, Any], substrate: dict[str, str], consecutive: bool
) -> str:
    """Render AIIN as a quantity wrapper around material, or as an R measure."""
    clause = row["gdt584_upstream_clause_de"]
    literal_np = "das Stations- oder Badmaß"
    if literal_np not in clause:
        raise RuntimeError(f"AIIN literal packet missing at {row['primary_governor_key']}: {clause}")
    if row["action_root"] == "R":
        prefix = f"Kennzeichne oder prüfe {literal_np}"
        if not clause.startswith(prefix):
            raise RuntimeError(f"unexpected AIIN R frame at {row['primary_governor_key']}")
        aiin_count = row["written_carrier_roots"].split("+").count("AIIN")
        noun = "beide Maßangaben" if aiin_count == 2 else "die Maßangabe"
        return f"Kennzeichne oder prüfe {noun}" + clause[len(prefix):]
    if substrate["object_class"] == "STATION":
        possessive = "desselben Stationsansatzes" if substrate["reference_mode"] == "ANAPHORIC" else "des Stationsansatzes"
        quantity_np = f"eine {'weitere ' if consecutive else ''}abgemessene Menge {possessive}"
    elif substrate["object_class"] == "PORTION":
        quantity_np = f"eine {'weitere ' if consecutive else ''}abgemessene Anwendungsportion"
    else:
        raise RuntimeError(f"unexpected AIIN substrate at {row['primary_governor_key']}: {substrate}")
    if row["action_root"] == "CH":
        prefix = f"Entnimm oder lass {literal_np}"
        if not clause.startswith(prefix):
            raise RuntimeError(f"unexpected AIIN CH frame at {row['primary_governor_key']}")
        return f"Lass {quantity_np}" + clause[len(prefix):]
    if row["action_root"] == "K":
        prefix = f"Führe {literal_np}"
        if not clause.startswith(prefix):
            raise RuntimeError(f"unexpected AIIN K frame at {row['primary_governor_key']}")
        return f"Führe {quantity_np}" + clause[len(prefix):]
    if row["action_root"] == "OK":
        prefix = f"Beschicke oder bereite {literal_np}"
        if not clause.startswith(prefix):
            raise RuntimeError(f"unexpected AIIN OK frame at {row['primary_governor_key']}")
        return f"Bereite {quantity_np}" + clause[len(prefix):]
    raise RuntimeError(f"unexpected AIIN-only root at {row['primary_governor_key']}")


def state_entry(
    selected: dict[str, Any], row: dict[str, str], index: int, role: str = "CLAUSE_INPUT"
) -> dict[str, Any]:
    object_class = selected["object_class"]
    return {
        "object_class": object_class,
        "lemma": selected["lemma"],
        "source_governor_key": row["primary_governor_key"],
        "source_action_root": row["action_root"],
        "source_anchor_event_id": row["anchor_event_id"],
        "host_index": index,
        "channel": "PARAMETER" if object_class in PARAMETER_CLASSES else "PARTICIPANT",
        "role": role,
    }


def preview_candidate(row: dict[str, str]) -> dict[str, str] | None:
    """Preview only a fixed completed object or a root default for Q02 fallback."""
    if row["integration_status"] == "COMPLETED_OBJECT_ACTION":
        return {
            "object_class": row["object_class"],
            "lemma": row["object_lemma_de"],
            "source_kind": "GDT598_COMPLETED_PREVIEW",
        }
    packet = written_packet(row)
    if packet is not None:
        if packet["packet_route"] == "PARTICIPANT":
            return {
                "object_class": packet["object_class"],
                "lemma": packet["lemma"],
                "source_kind": "WRITTEN_PARTICIPANT_PREVIEW",
            }
        return None
    if row["action_root"] in ROOT_DEFAULTS and row["gdt584_rule_id"] != "SH_CH_BRIDGE_HOLD":
        object_class, lemma, _reason = ROOT_DEFAULTS[row["action_root"]]
        return {"object_class": object_class, "lemma": lemma, "source_kind": "ROOT_DEFAULT_PREVIEW"}
    return None


def future_written_candidate(row: dict[str, str]) -> dict[str, Any] | None:
    """Return a right written participant with its best already-known typing.

    A completed GDT598 host is more informative than its raw carrier lemma:
    contextual SH-Y can be BODY, and action-conditioned S-OR can be FLOW.  A
    still-open GDT598 host has no such typing yet, so only there do we use the
    stable Y/AIN/OR packet mapping.
    """
    packet = written_packet(row)
    if packet is None or packet["packet_route"] != "PARTICIPANT":
        return None
    if row["integration_status"] == "COMPLETED_OBJECT_ACTION":
        return {
            **packet,
            "object_class": row["object_class"],
            "lemma": row["object_lemma_de"],
            "typing_source": "GDT598_COMPLETED_CONTEXTUAL_OBJECT",
        }
    return {**packet, "typing_source": "GDT598_OPEN_PACKET_MAPPING"}


def build(inputs: dict[str, Any], apply_manual_overrides: bool = True) -> dict[str, Any]:
    hosts = sorted(inputs["hosts"], key=lambda row: int(row["host_ordinal_global"]))
    gap_sources = list(inputs["gaps"])
    local_cards = [dict(row) for row in inputs["local_cards"]]
    inherited_reviews = [dict(row) for row in inputs["manual_reviews"]]
    manual_override_sources = [dict(row) for row in inputs["manual_overrides"]]
    manual_override_by_key = (
        {row["primary_governor_key"]: row for row in manual_override_sources}
        if apply_manual_overrides else {}
    )
    if apply_manual_overrides and len(manual_override_by_key) != len(manual_override_sources):
        raise RuntimeError("duplicate GDT599 manual override key")
    substrate_override_sources = [dict(row) for row in inputs["aiin_substrate_overrides"]]
    substrate_override_by_key = {row["primary_governor_key"]: row for row in substrate_override_sources}
    clause_polish_sources = [dict(row) for row in inputs["manual_clause_polish"]]
    clause_polish_by_key = {row["primary_governor_key"]: row for row in clause_polish_sources}
    gaps_by_key = {row["primary_governor_key"]: row for row in gap_sources}
    host_by_key = {row["primary_governor_key"]: row for row in hosts}
    if set(gaps_by_key) != {
        row["primary_governor_key"] for row in hosts if row["integration_status"] == "REMAINING_ACTION_GAP"
    }:
        raise RuntimeError("GDT598 gap-to-host key drift")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hosts:
        by_statement[row["statement_id"]].append(row)
    for rows in by_statement.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))

    replay_by_key: dict[str, dict[str, str]] = {}
    q_transitions: list[dict[str, str]] = []
    q_suppressed_targets: set[str] = set()

    for _statement_id, sequence in sorted(
        by_statement.items(), key=lambda item: int(item[1][0]["host_ordinal_global"])
    ):
        history: list[dict[str, Any]] = []
        cut_ordinal = 0
        for index, row in enumerate(sequence):
            if is_cut(row):
                history.clear()
                cut_ordinal += 1
                continue
            if row["action_root"] not in ACTION_ROOTS:
                continue

            key = row["primary_governor_key"]
            packet = written_packet(row)
            is_gap = key in gaps_by_key

            if not is_gap:
                selected = {
                    "object_class": row["object_class"],
                    "lemma": row["object_lemma_de"],
                }
                history.append(state_entry(selected, row, index))
                if has_q(row):
                    result = {"object_class": "STATION", "lemma": "Stationsansatz"}
                    history.append(state_entry(result, row, index, "RESULT_STATE"))
                    q_transitions.append({
                        "transition_ordinal": str(len(q_transitions) + 1),
                        "primary_governor_key": key,
                        "statement_id": row["statement_id"],
                        "physical_page": row["physical_page"],
                        "action_root": row["action_root"],
                        "completion_layer": "GDT598_RETAINED_COMPLETION",
                        "input_object_class": selected["object_class"],
                        "input_object_lemma_de": selected["lemma"],
                        "result_object_class": "STATION",
                        "result_object_lemma_de": "Stationsansatz",
                        "commit_order": "READ_INPUT_THEN_COMMIT_RESULT",
                        "frame_q_changes_history": "NO__ACTION_Q_ONLY",
                    })
                continue

            selected: dict[str, Any] | None = None
            typing_card = ""
            reference_card = ""
            reference_mode = "DEFINITE"
            selection_route = ""
            source_pointer = "NONE"
            source_distance = 0
            skipped_incompatible = 0
            q_right_station_tier_checks = 0
            q_right_station_sources: set[str] = set()
            aiin_substrate = {
                "object_class": "NOT_APPLICABLE",
                "lemma": "NOT_APPLICABLE",
                "source_pointer": "NOT_APPLICABLE",
                "selection_route": "NOT_APPLICABLE",
                "reference_mode": "NOT_APPLICABLE",
            }
            aiin_consecutive = False
            aiin_substrate_override_id = "NONE"
            aiin_substrate_override_reason = "NONE"

            if packet is not None and packet["packet_route"] == "PARTICIPANT":
                selected = dict(packet)
                typing_card = "T01_OWN_WRITTEN_PARTICIPANT"
                reference_card = "Q03_LOCAL_OR_DEFAULT_DEFINITE"
                selection_route = "OWN_WRITTEN_PARTICIPANT"
                source_pointer = key
            elif packet is not None:
                selected = dict(packet)
                selected["lemma"] = "Maßangabe" if row["action_root"] == "R" else "abgemessene Menge"
                typing_card = "T02_OWN_AIIN_PARAMETER"
                reference_card = "Q03_LOCAL_OR_DEFAULT_DEFINITE"
                selection_route = "OWN_AIIN_ONLY_PARAMETER"
                source_pointer = key
                if row["action_root"] != "R":
                    substrate_classes = {"STATION", "PORTION"}
                    substrate_candidate: dict[str, Any] | None = None
                    substrate_source = "NONE"
                    substrate_route = ""
                    substrate_reference = "DEFINITE"
                    for future_index in range(index + 1, len(sequence)):
                        future = sequence[future_index]
                        if is_cut(future) or future["anchor_event_id"] != row["anchor_event_id"]:
                            break
                        candidate = future_written_candidate(future)
                        if candidate is None or candidate["object_class"] not in substrate_classes:
                            continue
                        if has_q(row) and candidate["object_class"] == "STATION":
                            continue
                        substrate_candidate = candidate
                        substrate_source = future["primary_governor_key"]
                        substrate_route = "RIGHT_SAME_EVENT_WRITTEN_SUBSTRATE"
                        break
                    if substrate_candidate is None:
                        left_substrate = next(
                            (candidate for candidate in reversed(history) if candidate["object_class"] in substrate_classes),
                            None,
                        )
                        if left_substrate is not None:
                            substrate_candidate = {
                                "object_class": left_substrate["object_class"],
                                "lemma": left_substrate["lemma"],
                            }
                            substrate_source = left_substrate["source_governor_key"]
                            substrate_route = "LEFT_LIVE_SUBSTRATE"
                            substrate_reference = "ANAPHORIC"
                    if substrate_candidate is None:
                        for future_index in range(index + 1, len(sequence)):
                            future = sequence[future_index]
                            if is_cut(future):
                                break
                            candidate = future_written_candidate(future)
                            if candidate is None or candidate["object_class"] not in substrate_classes:
                                continue
                            if has_q(row) and candidate["object_class"] == "STATION":
                                continue
                            substrate_candidate = candidate
                            substrate_source = future["primary_governor_key"]
                            substrate_route = "RIGHT_WITHIN_STATE_WRITTEN_SUBSTRATE"
                            break
                    if substrate_candidate is None:
                        for future_index in range(index + 1, len(sequence)):
                            future = sequence[future_index]
                            if is_cut(future):
                                break
                            candidate = preview_candidate(future)
                            if candidate is None or candidate["object_class"] not in substrate_classes:
                                continue
                            if has_q(row) and candidate["object_class"] == "STATION":
                                continue
                            substrate_candidate = candidate
                            substrate_source = future["primary_governor_key"]
                            substrate_route = "RIGHT_BOUNDED_SUBSTRATE"
                            break
                    if substrate_candidate is None:
                        substrate_candidate = {"object_class": "STATION", "lemma": "Stationsansatz"}
                        substrate_source = f"DEFAULT:{row['action_root']}:STATION_SUBSTRATE"
                        substrate_route = "ROOT_DEFAULT_STATION_SUBSTRATE"
                    aiin_substrate = {
                        "object_class": substrate_candidate["object_class"],
                        "lemma": substrate_candidate["lemma"],
                        "source_pointer": substrate_source,
                        "selection_route": substrate_route,
                        "reference_mode": substrate_reference,
                    }
                    substrate_override = substrate_override_by_key.get(key)
                    if substrate_override is not None:
                        observed = (aiin_substrate["object_class"], aiin_substrate["source_pointer"])
                        expected = (
                            substrate_override["expected_rule_substrate_class"],
                            substrate_override["expected_rule_source_pointer"],
                        )
                        if observed != expected:
                            raise RuntimeError(f"AIIN substrate override drift at {key}: {observed} != {expected}")
                        aiin_substrate = {
                            "object_class": substrate_override["override_substrate_class"],
                            "lemma": substrate_override["override_substrate_lemma_de"],
                            "source_pointer": substrate_override["override_source_pointer"],
                            "selection_route": "MANUAL_AIIN_SUBSTRATE_OVERRIDE",
                            "reference_mode": substrate_override["override_reference_mode"],
                        }
                        aiin_substrate_override_id = substrate_override["review_id"]
                        aiin_substrate_override_reason = substrate_override["reason_de"]
                    previous_action = next(
                        (
                            previous for previous in reversed(sequence[:index])
                            if previous["action_root"] in ACTION_ROOTS or is_cut(previous)
                        ),
                        None,
                    )
                    if previous_action is not None and not is_cut(previous_action):
                        previous_packet = written_packet(previous_action)
                        aiin_consecutive = bool(
                            previous_packet is not None
                            and previous_packet["packet_route"] == "AIIN_ONLY_PARAMETER"
                        )
            else:
                compatible = COMPATIBLE_CLASSES[row["action_root"]]
                if row["gdt584_rule_id"] == "SH_CH_BRIDGE_HOLD":
                    bridge = next(
                        (
                            candidate for candidate in reversed(history)
                            if candidate["source_action_root"] == "CH" and candidate["role"] == "CLAUSE_INPUT"
                        ),
                        None,
                    )
                    if bridge is None:
                        raise RuntimeError(f"missing exact CH source for {key}")
                    selected = {"object_class": bridge["object_class"], "lemma": bridge["lemma"]}
                    typing_card = "T03_EXACT_CH_SH_BRIDGE"
                    reference_card = "Q01_LEFT_ANAPHORIC"
                    reference_mode = "ANAPHORIC"
                    selection_route = "EXACT_CH_TO_SH_BRIDGE"
                    source_pointer = bridge["source_governor_key"]
                    source_distance = index - int(bridge["host_index"])

                if selected is None:
                    for future_index in range(index + 1, len(sequence)):
                        future = sequence[future_index]
                        if is_cut(future) or future["anchor_event_id"] != row["anchor_event_id"]:
                            break
                        future_packet = future_written_candidate(future)
                        if future_packet is None:
                            continue
                        if future_packet["object_class"] not in compatible:
                            skipped_incompatible += 1
                            continue
                        if has_q(row) and future_packet["object_class"] == "STATION":
                            q_right_station_tier_checks += 1
                            q_right_station_sources.add(future["primary_governor_key"])
                            q_suppressed_targets.add(key)
                            continue
                        selected = dict(future_packet)
                        typing_card = "T04_RIGHT_SAME_EVENT_WRITTEN"
                        reference_card = "Q02_RIGHT_DEFINITE"
                        selection_route = "RIGHT_SAME_EVENT_WRITTEN_PARTICIPANT"
                        source_pointer = future["primary_governor_key"]
                        source_distance = future_index - index
                        break

                if selected is None:
                    left = None
                    for candidate in reversed(history):
                        if candidate["object_class"] in compatible:
                            left = candidate
                            break
                        skipped_incompatible += 1
                    if left is not None:
                        selected = {"object_class": left["object_class"], "lemma": left["lemma"]}
                        typing_card = "T05_LEFT_COMPATIBLE_STATE"
                        reference_card = "Q01_LEFT_ANAPHORIC"
                        reference_mode = "ANAPHORIC"
                        selection_route = "LEFT_COMPATIBLE_AFTER_OT_DY"
                        source_pointer = left["source_governor_key"]
                        source_distance = index - int(left["host_index"])

                if selected is None:
                    for future_index in range(index + 1, len(sequence)):
                        future = sequence[future_index]
                        if is_cut(future) or future["anchor_event_id"] != row["anchor_event_id"]:
                            break
                        preview = preview_candidate(future)
                        if preview is None or preview["object_class"] not in compatible:
                            if preview is not None:
                                skipped_incompatible += 1
                            continue
                        if has_q(row) and preview["object_class"] == "STATION":
                            q_right_station_tier_checks += 1
                            q_right_station_sources.add(future["primary_governor_key"])
                            q_suppressed_targets.add(key)
                            continue
                        selected = dict(preview)
                        typing_card = "T06_RIGHT_BOUNDED_COMPLETED_OR_DEFAULT"
                        reference_card = "Q02_RIGHT_DEFINITE"
                        selection_route = "RIGHT_SAME_EVENT_COMPLETED_OR_ROOT_DEFAULT"
                        source_pointer = future["primary_governor_key"]
                        source_distance = future_index - index
                        break

                if selected is None:
                    object_class, lemma, _reason = ROOT_DEFAULTS[row["action_root"]]
                    selected = {"object_class": object_class, "lemma": lemma}
                    typing_card = "T07_ROOT_DEFAULT"
                    reference_card = "Q03_LOCAL_OR_DEFAULT_DEFINITE"
                    selection_route = "ROOT_DEFAULT"
                    source_pointer = f"DEFAULT:{row['action_root']}:{object_class}"

            if selected is None:
                raise RuntimeError(f"unfilled target at {key}")
            baseline_object_class = selected["object_class"]
            baseline_object_lemma = selected["lemma"]
            baseline_typing_card = typing_card
            baseline_selection_route = selection_route
            baseline_source_pointer = source_pointer
            manual_override_id = "NONE"
            manual_override_reason = "NONE"
            renderer_policy = "RULE_DEFAULT"
            manual_override = manual_override_by_key.get(key)
            if manual_override is not None:
                expected = (
                    manual_override["expected_baseline_object_class"],
                    manual_override["expected_baseline_object_lemma_de"],
                )
                observed = (baseline_object_class, baseline_object_lemma)
                if observed != expected:
                    raise RuntimeError(f"manual override baseline drift at {key}: {observed} != {expected}")
                selected = {
                    "object_class": manual_override["override_object_class"],
                    "lemma": manual_override["override_object_lemma_de"],
                }
                typing_card = "T08_LOCAL_WORKSHOP_OVERRIDE"
                selection_route = manual_override["override_selection_route"]
                source_pointer = manual_override["override_source_pointer"]
                reference_mode = manual_override["override_reference_mode"]
                reference_card = (
                    "Q01_LEFT_ANAPHORIC" if reference_mode == "ANAPHORIC"
                    else "Q03_LOCAL_OR_DEFAULT_DEFINITE"
                )
                manual_override_id = manual_override["review_id"]
                manual_override_reason = manual_override["reason_de"]
                renderer_policy = manual_override["renderer_policy"]
                source_distance = 0
                if reference_mode == "ANAPHORIC" and source_pointer.startswith("ACTION:"):
                    manual_source = next(
                        (candidate for candidate in reversed(history) if candidate["source_governor_key"] == source_pointer),
                        None,
                    )
                    if manual_source is None:
                        raise RuntimeError(f"manual override source missing at {key}: {source_pointer}")
                    source_distance = index - int(manual_source["host_index"])
            object_np, gender, determiner = rendered_np(selected["lemma"], reference_mode)
            if packet is not None and packet["packet_route"] == "AIIN_ONLY_PARAMETER":
                completed_clause = render_aiin_only(row, selected, aiin_substrate, aiin_consecutive)
            elif manual_override_id == "W02":
                literal = row["gdt584_upstream_clause_de"]
                old_prefix = "Wende die Becken- oder Körpereinheit"
                if not literal.startswith(old_prefix):
                    raise RuntimeError(f"unexpected W02 written frame: {literal}")
                rewritten_row = dict(row)
                rewritten_row["gdt584_upstream_clause_de"] = "Wende" + literal[len(old_prefix):]
                completed_clause = insert_object(
                    rewritten_row, object_np, selected["object_class"], renderer_policy
                )
            elif packet is not None:
                completed_clause = row["gdt584_upstream_clause_de"]
            else:
                completed_clause = insert_object(row, object_np, selected["object_class"], renderer_policy)
            result_transition = has_q(row)
            if result_transition:
                completed_clause = split_action_q_result(completed_clause, key)
            clause_polish = clause_polish_by_key.get(key)
            clause_polish_id = "NONE"
            if clause_polish is not None:
                if completed_clause != clause_polish["expected_prepolish_clause_de"]:
                    raise RuntimeError(
                        f"manual clause polish drift at {key}: {completed_clause!r} != "
                        f"{clause_polish['expected_prepolish_clause_de']!r}"
                    )
                completed_clause = clause_polish["final_clause_de"]
                clause_polish_id = clause_polish["polish_id"]
            state_commit_class = "STATION" if result_transition else selected["object_class"]
            state_commit_lemma = "Stationsansatz" if result_transition else selected["lemma"]
            state_commit_channel = "PARAMETER" if state_commit_class in PARAMETER_CLASSES else "PARTICIPANT"
            replay_row = {
                "gap_ordinal": gaps_by_key[key]["gap_ordinal"],
                "host_ordinal_global": row["host_ordinal_global"],
                "statement_id": row["statement_id"],
                "host_ordinal_in_statement": row["host_ordinal_in_statement"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "primary_governor_key": key,
                "anchor_event_id": row["anchor_event_id"],
                "action_slot_id": row["action_slot_id"],
                "action_root": row["action_root"],
                "gdt584_rule_id": row["gdt584_rule_id"],
                "cut_ordinal_in_statement": str(cut_ordinal),
                "written_carrier_count": row["written_carrier_count"],
                "written_carrier_roots": row["written_carrier_roots"],
                "written_carrier_lemmas_de": row["written_carrier_lemmas_de"],
                "typing_card_id": typing_card,
                "baseline_typing_card_id": baseline_typing_card,
                "reference_scope_card_id": reference_card,
                "selection_route": selection_route,
                "baseline_selection_route": baseline_selection_route,
                "source_pointer": source_pointer,
                "baseline_source_pointer": baseline_source_pointer,
                "source_distance_hosts": str(source_distance),
                "skipped_incompatible_candidate_count": str(skipped_incompatible),
                "q_right_station_suppressed_unique_source_count": str(len(q_right_station_sources)),
                "q_right_station_suppressed_source_pointers": "|".join(sorted(q_right_station_sources)) or "NONE",
                "q_right_station_suppressed_tier_check_count": str(q_right_station_tier_checks),
                "input_role": (
                    "TRANSIENT_MEASURE_PATIENT" if selection_route == "MANUAL_TRANSIENT_MEASURE_HANDOFF"
                    else "MEASURE_ARGUMENT" if selected["object_class"] == "MEASURE"
                    else "CONDITION_PARAMETER" if selected["object_class"] == "CONDITION"
                    else "PARTICIPANT"
                ),
                "aiin_substrate_object_class": aiin_substrate["object_class"],
                "aiin_substrate_object_lemma_de": aiin_substrate["lemma"],
                "aiin_substrate_source_pointer": aiin_substrate["source_pointer"],
                "aiin_substrate_selection_route": aiin_substrate["selection_route"],
                "aiin_substrate_reference_mode": aiin_substrate["reference_mode"],
                "aiin_consecutive_quantity": "YES" if aiin_consecutive else "NO",
                "aiin_substrate_override_id": aiin_substrate_override_id,
                "aiin_substrate_override_reason_de": aiin_substrate_override_reason,
                "reference_mode": reference_mode,
                "baseline_object_class": baseline_object_class,
                "baseline_object_lemma_de": baseline_object_lemma,
                "object_class": selected["object_class"],
                "object_lemma_de": selected["lemma"],
                "grammatical_gender": gender,
                "determiner_de": determiner,
                "rendered_object_np_de": object_np,
                "gdt584_upstream_clause_de": row["gdt584_upstream_clause_de"],
                "gdt599_completed_clause_de": completed_clause,
                "clause_changed": "YES" if completed_clause != row["gdt584_upstream_clause_de"] else "NO",
                "manual_override_id": manual_override_id,
                "manual_override_reason_de": manual_override_reason,
                "renderer_policy": renderer_policy,
                "manual_clause_polish_id": clause_polish_id,
                "q_result_transition": "YES" if result_transition else "NO",
                "state_commit_object_class": state_commit_class,
                "state_commit_object_lemma_de": state_commit_lemma,
                "state_commit_channel": state_commit_channel,
                "default_is_replaceable": "YES",
                "guard": GUARD,
            }
            replay_by_key[key] = replay_row
            history.append(state_entry(selected, row, index))
            if result_transition:
                result = {"object_class": "STATION", "lemma": "Stationsansatz"}
                history.append(state_entry(result, row, index, "RESULT_STATE"))
                q_transitions.append({
                    "transition_ordinal": str(len(q_transitions) + 1),
                    "primary_governor_key": key,
                    "statement_id": row["statement_id"],
                    "physical_page": row["physical_page"],
                    "action_root": row["action_root"],
                    "completion_layer": "GDT599_REMAINING_COMPLETION",
                    "input_object_class": selected["object_class"],
                    "input_object_lemma_de": selected["lemma"],
                    "result_object_class": "STATION",
                    "result_object_lemma_de": "Stationsansatz",
                    "commit_order": "READ_INPUT_THEN_COMMIT_RESULT",
                    "frame_q_changes_history": "NO__ACTION_Q_ONLY",
                })

    replay = sorted(replay_by_key.values(), key=lambda row: int(row["gap_ordinal"]))
    if len(replay) != 793:
        raise RuntimeError(f"replay count drift: {len(replay)}")

    baseline_replay: list[dict[str, str]] = []
    propagation_effects: list[dict[str, str]] = []
    if apply_manual_overrides:
        baseline_replay = build(inputs, apply_manual_overrides=False)["replay"]
        baseline_by_key = {row["primary_governor_key"]: row for row in baseline_replay}
        compared_fields = (
            "selection_route", "source_pointer", "reference_mode", "object_class",
            "object_lemma_de", "gdt599_completed_clause_de",
        )
        for row in replay:
            if row["primary_governor_key"] in manual_override_by_key:
                continue
            baseline = baseline_by_key[row["primary_governor_key"]]
            changed = [name for name in compared_fields if row[name] != baseline[name]]
            if not changed:
                continue
            propagation_effects.append({
                "propagation_ordinal": str(len(propagation_effects) + 1),
                "primary_governor_key": row["primary_governor_key"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "changed_fields": "|".join(changed),
                "baseline_selection_route": baseline["selection_route"],
                "final_selection_route": row["selection_route"],
                "baseline_source_pointer": baseline["source_pointer"],
                "final_source_pointer": row["source_pointer"],
                "baseline_object_class": baseline["object_class"],
                "final_object_class": row["object_class"],
                "baseline_object_lemma_de": baseline["object_lemma_de"],
                "final_object_lemma_de": row["object_lemma_de"],
                "baseline_clause_de": baseline["gdt599_completed_clause_de"],
                "final_clause_de": row["gdt599_completed_clause_de"],
                "propagation_reason": (
                    "UPSTREAM_MANUAL_OBJECT_CHANGED_LIVE_HISTORY_OR_COMPATIBILITY"
                ),
            })

    replay_by_final_key = {row["primary_governor_key"]: row for row in replay}
    baseline_by_final_key = {
        row["primary_governor_key"]: row for row in (baseline_replay or replay)
    }
    manual_decisions = []
    if apply_manual_overrides:
        for source in manual_override_sources:
            row = replay_by_final_key[source["primary_governor_key"]]
            baseline = baseline_by_final_key[source["primary_governor_key"]]
            manual_decisions.append({
                "review_id": source["review_id"],
                "primary_governor_key": row["primary_governor_key"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "baseline_selection_route": baseline["selection_route"],
                "baseline_source_pointer": baseline["source_pointer"],
                "baseline_object_class": baseline["object_class"],
                "baseline_object_lemma_de": baseline["object_lemma_de"],
                "final_selection_route": row["selection_route"],
                "final_source_pointer": row["source_pointer"],
                "final_object_class": row["object_class"],
                "final_object_lemma_de": row["object_lemma_de"],
                "renderer_policy": source["renderer_policy"],
                "reason_de": source["reason_de"],
                "final_clause_de": row["gdt599_completed_clause_de"],
            })
    aiin_bindings = []
    for row in replay:
        if row["baseline_typing_card_id"] != "T02_OWN_AIIN_PARAMETER":
            continue
        aiin_bindings.append({
            "aiin_binding_ordinal": str(len(aiin_bindings) + 1),
            "primary_governor_key": row["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "action_root": row["action_root"],
            "written_carrier_roots": row["written_carrier_roots"],
            "quantity_reading_de": row["object_lemma_de"],
            "substrate_object_class": row["aiin_substrate_object_class"],
            "substrate_object_lemma_de": row["aiin_substrate_object_lemma_de"],
            "substrate_source_pointer": row["aiin_substrate_source_pointer"],
            "substrate_selection_route": row["aiin_substrate_selection_route"],
            "substrate_reference_mode": row["aiin_substrate_reference_mode"],
            "consecutive_quantity": row["aiin_consecutive_quantity"],
            "substrate_override_id": row["aiin_substrate_override_id"],
            "literal_clause_de": row["gdt584_upstream_clause_de"],
            "quantity_clause_de": row["gdt599_completed_clause_de"],
            "state_channel": "PARAMETER__DOES_NOT_ERASE_SUBSTRATE",
        })

    complete_hosts: list[dict[str, str]] = []
    complete_actions: list[dict[str, str]] = []
    for source in hosts:
        row = dict(source)
        replay_row = replay_by_key.get(source["primary_governor_key"])
        if replay_row is not None:
            row.update({
                "integration_status": "COMPLETED_OBJECT_ACTION",
                "completion_layer": "GDT599_REMAINING_OBJECT_COMPLETION",
                "object_class": replay_row["object_class"],
                "object_lemma_de": replay_row["object_lemma_de"],
                "rendered_object_np_de": replay_row["rendered_object_np_de"],
                "typing_card_id": replay_row["typing_card_id"],
                "reference_scope_card_id": replay_row["reference_scope_card_id"],
                "reference_mode": replay_row["reference_mode"],
                "source_pointer": replay_row["source_pointer"],
                "clause_changed": "YES" if replay_row["gdt599_completed_clause_de"] != source["gdt584_upstream_clause_de"] else "NO",
                "guard": GUARD,
            })
        row["gdt599_complete_clause_de"] = (
            replay_row["gdt599_completed_clause_de"]
            if replay_row is not None else row["gdt598_integrated_clause_de"]
        )
        if row["action_root"] in ACTION_ROOTS and Q_MARKER in row["gdt599_complete_clause_de"]:
            row["gdt599_complete_clause_de"] = split_action_q_result(
                row["gdt599_complete_clause_de"], row["primary_governor_key"]
            )
        clause_polish = clause_polish_by_key.get(row["primary_governor_key"])
        if clause_polish is not None:
            if row["gdt599_complete_clause_de"] == clause_polish["expected_prepolish_clause_de"]:
                row["gdt599_complete_clause_de"] = clause_polish["final_clause_de"]
            elif row["gdt599_complete_clause_de"] != clause_polish["final_clause_de"]:
                raise RuntimeError(f"complete-host clause polish drift at {row['primary_governor_key']}")
        row["gdt599_clause_changed_from_gdt598"] = (
            "YES" if row["gdt599_complete_clause_de"] != source["gdt598_integrated_clause_de"] else "NO"
        )
        row["gdt599_completion_status"] = (
            "ALL_ACTIONS_OBJECT_COMPLETE" if row["action_root"] in ACTION_ROOTS else "NON_ACTION_RETAINED"
        )
        complete_hosts.append(row)
        if row["action_root"] in ACTION_ROOTS:
            complete_actions.append({
                "complete_action_ordinal": str(len(complete_actions) + 1),
                **{name: row[name] for name in (
                    "host_ordinal_global", "statement_id", "host_ordinal_in_statement", "physical_page",
                    "primary_governor_key", "anchor_event_id", "action_slot_id", "action_root", "gdt584_rule_id",
                    "completion_layer", "written_carrier_count", "written_carrier_roots", "object_class",
                    "object_lemma_de", "rendered_object_np_de", "typing_card_id", "reference_scope_card_id",
                    "reference_mode", "source_pointer", "gdt584_upstream_clause_de", "gdt599_complete_clause_de",
                )},
                "gdt599_new_completion": "YES" if replay_row is not None else "NO",
            })
    if len(complete_hosts) != 2272 or len(complete_actions) != 1443:
        raise RuntimeError("complete edition population drift")

    complete_host_by_key = {row["primary_governor_key"]: row for row in complete_hosts}
    clause_polish_rows = []
    for source in clause_polish_sources:
        row = complete_host_by_key[source["primary_governor_key"]]
        clause_polish_rows.append({
            "polish_id": source["polish_id"],
            "primary_governor_key": source["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "action_root": row["action_root"],
            "object_class": row["object_class"],
            "object_lemma_de": row["object_lemma_de"],
            "expected_prepolish_clause_de": source["expected_prepolish_clause_de"],
            "final_clause_de": row["gdt599_complete_clause_de"],
            "reason_de": source["reason_de"],
        })

    complete_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete_hosts:
        complete_by_statement[row["statement_id"]].append(row)
    statements: list[dict[str, str]] = []
    for statement_id, rows in sorted(
        complete_by_statement.items(), key=lambda item: int(item[1][0]["host_ordinal_global"])
    ):
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
        upstream_reader, upstream_paragraphs = compose_paragraphs(rows, "gdt584_upstream_clause_de")
        complete_reader, complete_paragraphs = compose_paragraphs(rows, "gdt599_complete_clause_de")
        actions = [row for row in rows if row["action_root"] in ACTION_ROOTS]
        statements.append({
            "statement_ordinal": str(len(statements) + 1),
            "statement_id": statement_id,
            "physical_page": rows[0]["physical_page"],
            "register": rows[0]["register"],
            "owner_id": rows[0]["owner_id"],
            "host_count": str(len(rows)),
            "action_count": str(len(actions)),
            "object_complete_action_count": str(len(actions)),
            "remaining_action_gap_count": "0",
            "gdt599_new_completion_count": str(sum(row["completion_layer"] == "GDT599_REMAINING_OBJECT_COMPLETION" for row in actions)),
            "coverage_state": "ALL_ACTIONS_OBJECT_COMPLETE",
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in actions)),
            "gdt584_reader_de": upstream_reader,
            "gdt599_complete_reader_de": complete_reader,
            "paragraph_count": str(complete_paragraphs),
            "paragraph_count_preserved": "YES" if upstream_paragraphs == complete_paragraphs else "NO",
        })
    if len(statements) != 313:
        raise RuntimeError("statement population drift")

    by_typing: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_reference: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        by_typing[row["typing_card_id"]].append(row)
        by_reference[row["reference_scope_card_id"]].append(row)
    typing_cards = []
    for order, (card_id, label, trigger) in enumerate(SELECTION_CARD_SPECS, start=1):
        members = by_typing[card_id]
        typing_cards.append({
            "selection_card_order": str(order),
            "typing_card_id": card_id,
            "label_de": label,
            "trigger_de": trigger,
            "occurrence_count": str(len(members)),
            "root_profile": compact_profile(Counter(row["action_root"] for row in members)) or "NONE",
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)) or "NONE",
            "example_governor_key": members[0]["primary_governor_key"] if members else "NONE",
            "example_clause_de": members[0]["gdt599_completed_clause_de"] if members else "NONE",
        })
    reference_cards = []
    for order, (card_id, direction, mode, renderer) in enumerate(REFERENCE_CARD_SPECS, start=1):
        members = by_reference[card_id]
        reference_cards.append({
            "reference_card_order": str(order),
            "reference_scope_card_id": card_id,
            "direction": direction,
            "reference_mode": mode,
            "renderer_de": renderer,
            "occurrence_count": str(len(members)),
            "selection_route_profile": compact_profile(Counter(row["selection_route"] for row in members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
        })
    default_cards = []
    for order, root in enumerate(("CH", "K", "OK", "P", "R", "SH"), start=1):
        object_class, lemma, reason = ROOT_DEFAULTS[root]
        members = [row for row in replay if row["action_root"] == root]
        defaults = [row for row in members if row["typing_card_id"] == "T07_ROOT_DEFAULT"]
        default_cards.append({
            "default_card_order": str(order),
            "action_root": root,
            "default_object_class": object_class,
            "default_lemma_de": lemma,
            "reason_de": reason,
            "target_occurrence_count": str(len(members)),
            "default_used_count": str(len(defaults)),
            "example_governor_key": defaults[0]["primary_governor_key"] if defaults else "NONE",
        })
    compatibility_cards = []
    for order, root in enumerate(("CH", "K", "OK", "P", "R", "SH"), start=1):
        members = [row for row in replay if row["action_root"] == root]
        refs = [row for row in members if row["typing_card_id"] in {
            "T03_EXACT_CH_SH_BRIDGE", "T04_RIGHT_SAME_EVENT_WRITTEN", "T05_LEFT_COMPATIBLE_STATE",
            "T06_RIGHT_BOUNDED_COMPLETED_OR_DEFAULT",
        }]
        compatibility_cards.append({
            "compatibility_card_order": str(order),
            "action_root": root,
            "compatible_object_classes": "|".join(sorted(COMPATIBLE_CLASSES[root])),
            "reference_occurrence_count": str(len(refs)),
            "reference_class_profile": compact_profile(Counter(row["object_class"] for row in refs)) or "NONE",
            "flow_is_compatible": "YES" if "FLOW" in COMPATIBLE_CLASSES[root] else "NO",
            "parameter_is_compatible": "YES" if COMPATIBLE_CLASSES[root] & PARAMETER_CLASSES else "NO",
        })

    review_queue = []
    for row in replay:
        reasons = []
        if row["typing_card_id"] in {"T06_RIGHT_BOUNDED_COMPLETED_OR_DEFAULT", "T07_ROOT_DEFAULT"}:
            reasons.append("WEAK_SOURCE_ROUTE")
        if row["object_class"] in {"BODY", "BODY_PART", "FLOW"}:
            reasons.append("CONCRETE_NONSTATION_OBJECT")
        if int(row["q_right_station_suppressed_unique_source_count"]):
            reasons.append("Q_CIRCULAR_RIGHT_STATION_SUPPRESSED")
        if int(row["source_distance_hosts"]) >= 4:
            reasons.append("LONG_REFERENCE")
        if not reasons:
            continue
        review_queue.append({
            "review_ordinal": str(len(review_queue) + 1),
            "primary_governor_key": row["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "action_root": row["action_root"],
            "selection_route": row["selection_route"],
            "source_pointer": row["source_pointer"],
            "object_class": row["object_class"],
            "object_lemma_de": row["object_lemma_de"],
            "review_reasons": "|".join(reasons),
            "completed_clause_de": row["gdt599_completed_clause_de"],
        })

    page_rows = []
    for page in PAGES:
        page_replay = [row for row in replay if row["physical_page"] == page]
        page_actions = [row for row in complete_actions if row["physical_page"] == page]
        page_statements = [row for row in statements if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "statement_count": str(len(page_statements)),
            "action_count": str(len(page_actions)),
            "gdt598_retained_complete_count": str(len(page_actions) - len(page_replay)),
            "gdt599_new_complete_count": str(len(page_replay)),
            "selection_route_profile": compact_profile(Counter(row["selection_route"] for row in page_replay)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in page_actions)),
            "all_actions_object_complete": "YES",
        })

    route_profile = Counter(row["selection_route"] for row in replay)
    object_profile = Counter(row["object_class"] for row in replay)
    status = (
        "PASS_793_REMAINING_OBJECTS__1443_OF_1443_ACTIONS_COMPLETE__313_OF_313_STATEMENTS_COMPLETE"
        f"__{len(manual_decisions)}_LOCAL_WORKSHOP_DECISIONS__46_AIIN_QUANTITY_BINDINGS"
        f"__{len(q_suppressed_targets)}_Q_CIRCULAR_TARGETS_BLOCKED__0_UNFILLED"
    )
    input_role_profile = Counter(row["input_role"] for row in replay)
    aiin_substrate_profile = Counter(row["substrate_object_class"] for row in aiin_bindings)
    result = {
        "experiment_id": "GDT599",
        "status": status,
        "fixed_pages": list(PAGES),
        "statement_count": len(statements),
        "host_count": len(complete_hosts),
        "action_count": len(complete_actions),
        "gdt598_retained_completed_action_count": 650,
        "gdt599_new_completed_action_count": len(replay),
        "remaining_unfilled_action_count": 0,
        "all_action_complete_statement_count": sum(row["coverage_state"] == "ALL_ACTIONS_OBJECT_COMPLETE" for row in statements),
        "selection_route_profile": dict(sorted(route_profile.items())),
        "object_class_profile": dict(sorted(object_profile.items())),
        "input_role_profile": dict(sorted(input_role_profile.items())),
        "participant_object_count": input_role_profile["PARTICIPANT"] + input_role_profile["TRANSIENT_MEASURE_PATIENT"],
        "ordinary_participant_object_count": input_role_profile["PARTICIPANT"],
        "parameter_argument_count": input_role_profile["MEASURE_ARGUMENT"] + input_role_profile["CONDITION_PARAMETER"],
        "transient_measure_patient_count": input_role_profile["TRANSIENT_MEASURE_PATIENT"],
        "aiin_quantity_binding_count": len(aiin_bindings),
        "aiin_substrate_profile": dict(sorted(aiin_substrate_profile.items())),
        "aiin_substrate_manual_override_count": sum(row["substrate_override_id"] != "NONE" for row in aiin_bindings),
        "aiin_consecutive_quantity_count": sum(row["consecutive_quantity"] == "YES" for row in aiin_bindings),
        "manual_workshop_decision_count": len(manual_decisions),
        "manual_override_propagation_effect_count": len(propagation_effects),
        "manual_clause_polish_count": len(clause_polish_rows),
        "written_clause_byte_preserved_count": sum(
            row["written_carrier_count"] != "0" and row["clause_changed"] == "NO" for row in replay
        ),
        "aiin_quantity_rerender_count": sum(
            row["baseline_typing_card_id"] == "T02_OWN_AIIN_PARAMETER" and row["clause_changed"] == "YES"
            for row in replay
        ),
        "carrierless_clause_completed_count": sum(row["written_carrier_count"] == "0" for row in replay),
        "action_q_result_transition_count": len(q_transitions),
        "gdt599_action_q_result_transition_count": sum(
            row["completion_layer"] == "GDT599_REMAINING_COMPLETION" for row in q_transitions
        ),
        "action_q_split_result_clause_count": sum(
            row["primary_governor_key"] in {transition["primary_governor_key"] for transition in q_transitions}
            and "; " in row["gdt599_complete_clause_de"]
            and "als neuen Bad- oder Stationsansatz" in row["gdt599_complete_clause_de"]
            for row in complete_hosts
        ),
        "q_circular_right_station_target_count": len(q_suppressed_targets),
        "q_circular_right_station_targets": sorted(q_suppressed_targets),
        "q_circular_right_station_unique_source_count": sum(
            int(row["q_right_station_suppressed_unique_source_count"]) for row in replay
        ),
        "q_circular_right_station_tier_check_count": sum(
            int(row["q_right_station_suppressed_tier_check_count"]) for row in replay
        ),
        "frame_q_history_transition_count": 0,
        "review_queue_count": len(review_queue),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "guard": GUARD,
    }

    reader = render_reader(statements, local_cards, result)
    return {
        "replay": replay,
        "actions": complete_actions,
        "hosts": complete_hosts,
        "statements": statements,
        "typing_cards": typing_cards,
        "reference_cards": reference_cards,
        "defaults": default_cards,
        "compatibility": compatibility_cards,
        "q_transitions": q_transitions,
        "manual_decisions": manual_decisions,
        "propagation_effects": propagation_effects,
        "aiin_bindings": aiin_bindings,
        "clause_polish": clause_polish_rows,
        "review_queue": review_queue,
        "pages": page_rows,
        "local_cards": local_cards,
        "manual_reviews": inherited_reviews,
        "reader": reader,
        "result": result,
    }


def render_reader(
    statements: list[dict[str, str]], local_cards: list[dict[str, str]], result: dict[str, Any]
) -> str:
    lines = [
        "# GDT599 – vollständiger Objektleser der sechs Arbeitsseiten",
        "",
        f"Status: `{result['status']}`",
        "",
        "Alle 1.443 Aktionshosts besitzen nun eine konkrete Arbeitsbedeutung. Die 298 geschriebenen Teilnehmerpackets bleiben bis auf eine ausdrücklich dokumentierte Inhaltslesung erhalten; 46 AIIN-only-Packets werden als Mengenhülle oder Maßangabe flüssiger gesprochen. Die Bedeutungen sind eine fortschreibbare Arbeitstheorie, keine behauptete Entzifferung.",
        "",
        "CARRIER_Q liest zuerst seinen Eingang und schreibt erst danach einen neuen Stationsansatz in den Folgezustand. Lokale Karten bleiben vollständig getrennt.",
        "",
    ]
    current_page = ""
    for row in statements:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend((f"## {current_page}", ""))
        lines.extend((f"### {row['statement_id']}", "", row["gdt599_complete_reader_de"], ""))
    lines.extend(("## Getrennte lokale Karten", "", "Diese 40 Karten erben nie in die laufenden Aussagen.", ""))
    current_page = ""
    for row in local_cards:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend((f"### {current_page}", ""))
        lines.extend((f"- `{row['local_card_host_key']}` ({row['locus']}): {row['gdt586_primary_reader_de']}", ""))
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


def write_built(built: dict[str, Any]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in (
        "replay", "actions", "hosts", "statements", "typing_cards", "reference_cards", "defaults",
        "compatibility", "q_transitions", "manual_decisions", "propagation_effects", "aiin_bindings", "clause_polish",
        "review_queue", "pages", "local_cards", "manual_reviews",
    ):
        OUTPUTS[name].write_bytes(tsv_bytes(built[name]))
    OUTPUTS["reader"].write_text(built["reader"], encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
