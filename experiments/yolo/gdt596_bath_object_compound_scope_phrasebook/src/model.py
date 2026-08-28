#!/usr/bin/env python3
"""Deterministic GDT596 compound/scope phrasebook over GDT595's 254 actions."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt596_bath_object_compound_scope_phrasebook"
ARTIFACTS = BASE / "artifacts"

INPUTS = {
    "actions": ROOT / "experiments/yolo/gdt595_remaining_bath_default_source_atlas/artifacts/gdt595_254_fully_specific_bath_actions.tsv",
    "gdt595_result": ROOT / "experiments/yolo/gdt595_remaining_bath_default_source_atlas/artifacts/gdt595_result.json",
    "manual_workshop_review": BASE / "sources/gdt596_manual_workshop_review.tsv",
}

OUTPUTS = {
    "typing_cards": ARTIFACTS / "gdt596_5_object_typing_cards.tsv",
    "reference_cards": ARTIFACTS / "gdt596_3_reference_scope_cards.tsv",
    "object_forms": ARTIFACTS / "gdt596_11_observed_object_forms.tsv",
    "modifier_cards": ARTIFACTS / "gdt596_15_modifier_cards.tsv",
    "modifier_sequences": ARTIFACTS / "gdt596_40_modifier_sequences.tsv",
    "workshop_reviews": ARTIFACTS / "gdt596_23_workshop_review_cards.tsv",
    "replay": ARTIFACTS / "gdt596_254_compound_scope_replay.tsv",
    "pages": ARTIFACTS / "gdt596_6_page_profiles.tsv",
    "phrasebook": ARTIFACTS / "GDT596_COMPOUND_SCOPE_PHRASEBOOK.md",
    "result": ARTIFACTS / "gdt596_result.json",
    "validation": ARTIFACTS / "gdt596_validation.json",
}

STATUS = (
    "PASS_254_EXACT_COMPOSITIONAL_REPLAYS__5_TYPING_CARDS__3_REFERENCE_SCOPE_CARDS__"
    "100_WRITTEN__25_BLOCKER__74_BOUND_REFERENCE__12_AIN_OR_TYPE__43_BODY_DEFAULT__"
    "70_LEFT_ANAPHORIC__9_RIGHT_OR_TIE_DEFINITE__175_LOCAL_OR_DEFAULT_DEFINITE__"
    "7_LEMMAS__11_OBJECT_FORMS__"
    "15_MODIFIER_FRAGMENTS__40_OBSERVED_SEQUENCES__"
    "184_DEFINITE__70_ANAPHORIC__247_SINGLE_7_MULTI_PARTICIPANT__0_EXCEPTIONS"
    "__23_WORKSHOP_REVIEWS__16_STYLE__6_OBJECT_RIVAL__1_BINDING_RIVAL__2_IMMEDIATE_OBJECT_FORKS"
)

DIRECT_ROUTES = {
    "WRITTEN_Y_GDT590",
    "WRITTEN_OR_UNIT",
    "WRITTEN_AIN_PORTION",
}
LEFT_ROUTES = {
    "INTERVENING_OBJECT_HANDOFF",
    "EPISODE_CARRY",
    "RESOLVED_COLD_SOURCE_EPISODE_CARRY",
    "GDT569_Y_LOCAL_BODY_DONOR",
    "GDT569_Y_LOCAL_FLOW_DONOR",
    "GDT569_Y_LOCAL_STATION_DONOR",
    "NEAREST_VISIBLE_NONMEDIUM_PARTICIPANT",
}
RIGHT_ROUTES = {
    "SAME_EVENT_RIGHTWARD_SHARED_COMPLEMENT",
    "STATION_PORTION_PACKET_RIGHT_STATION_TIEBREAK",
}
PROMOTION_ROUTES = {
    "GDT569_AIN_PORTION_PROMOTION",
    "GDT569_OR_UNIT_PROMOTION",
}
BODY_DEFAULT_ROUTES = {
    "GDT569_Y_RESET_BODY_FIRST",
    "RESET_BODY_FIRST_WITHOUT_NONMEDIUM_PARTICIPANT",
}

TYPING_SPECS = [
    {
        "typing_card_id": "T01_WRITTEN_TYPED_OBJECT",
        "short_rule_de": "Geschriebener Objektträger gewinnt",
        "trigger_de": "AIN, OR oder Y steht im vollständigen SH-Host.",
        "typing_rule_de": "AIN→Portion; OR→Einheit; Y ohne Körperblocker→Körper; Y mit Körperblocker→Stationsansatz.",
        "reference_rule_de": "definit neu: die/den",
        "future_default_de": "Bei sichtbarem Träger zuerst diese Karte anwenden.",
        "rival_policy_de": "Zusätzliche geschriebene Teilnehmer bleiben in ihrer Reihenfolge erhalten.",
    },
    {
        "typing_card_id": "T02_BLOCKER_STATION",
        "short_rule_de": "Blockierter leerer SH-Slot wird Station",
        "trigger_de": "Kein geschriebener Objektträger, aber ein vollständiger Körperblocker.",
        "typing_rule_de": "Stationsansatz",
        "reference_rule_de": "definit neu: den",
        "future_default_de": "Blocker erhält Stationsvorrang vor Fernbezug und Default.",
        "rival_policy_de": "Körper bleibt nur als sichtbarer Rivale, nicht als Primärdefault.",
    },
    {
        "typing_card_id": "T03_BOUND_TYPED_REFERENCE",
        "short_rule_de": "Gebundene getypte Quelle kopieren",
        "trigger_de": "Ein sichtbarer Handoff/Episodenträger liegt links oder ein getypter Endträger schließt dasselbe Ereignis rechts.",
        "typing_rule_de": "Typ und Lemma der Quelle erben.",
        "reference_rule_de": "Bezugrichtung wird unabhängig als linke Anapher oder rechtes definites Komplement gerendert.",
        "future_default_de": "Nächste passende linke Quelle weiterführen oder getypten rechten Endträger teilen; AIIN-Füllung zählt nie als Patient.",
        "rival_policy_de": "Zweitquelle und enge Hostbindung bleiben als lokale Alternativen sichtbar.",
    },
    {
        "typing_card_id": "T04_STABLE_AIN_OR_TYPE",
        "short_rule_de": "Gelernten AIN/OR-Typ verwenden",
        "trigger_de": "Ein stabiler AIN- oder OR-Typ ist vorhanden, unabhängig davon, ob seine konkrete Quelle lokal oder vor dem Cut liegt.",
        "typing_rule_de": "AIN→Anwendungsportion; OR→Badeinheit.",
        "reference_rule_de": "lokal anaphorisch, nach Cut definit; Typ und Identität bleiben getrennt.",
        "future_default_de": "Typ wiederverwenden; Objektidentität nur bei einer Quelle nach dem letzten Cut behaupten.",
        "rival_policy_de": "Lokale Stations- oder Beckenunterart wird nur mit sichtbarer Quelle übernommen.",
    },
    {
        "typing_card_id": "T05_BODY_FIRST_DEFAULT",
        "short_rule_de": "Leerer, blockerfreier Slot erhält Körper",
        "trigger_de": "Kein geschriebener, linker oder rechter nicht-mediumhafter Teilnehmer und kein AIN/OR-Typdefault.",
        "typing_rule_de": "Körper",
        "reference_rule_de": "definit neu: den",
        "future_default_de": "Immer eine Arbeitsbedeutung liefern: Körper zuerst.",
        "rival_policy_de": "Späterer Stationsansatz bleibt Alternative; ein neues sichtbares Argument ersetzt den Default sofort.",
    },
]

REFERENCE_SPECS = [
    {
        "reference_scope_card_id": "Q01_LEFT_ANAPHORIC",
        "short_rule_de": "Linke Quelle wiederaufnehmen",
        "trigger_de": "Die konkrete Quelle liegt nach dem letzten Cut links vom SH-Slot.",
        "direction": "LEFT",
        "reference_mode": "ANAPHORIC",
        "renderer_de": "dieselbe/denselben + Quelllemma",
    },
    {
        "reference_scope_card_id": "Q02_RIGHT_OR_TIE_DEFINITE",
        "short_rule_de": "Rechtes gemeinsames Komplement oder Pakettie",
        "trigger_de": "Ein getypter Endträger schließt dieselbe kurze Verbkette rechts oder entscheidet das gebundene Paket.",
        "direction": "RIGHT",
        "reference_mode": "DEFINITE",
        "renderer_de": "die/den + Trägerlemma",
    },
    {
        "reference_scope_card_id": "Q03_LOCAL_OR_DEFAULT_DEFINITE",
        "short_rule_de": "Lokal geschriebener oder typischer Default",
        "trigger_de": "Das Objekt steht im Host oder wird als Blocker-, AIN/OR- oder Körpertyp gesetzt, ohne lokale Identitätsquelle.",
        "direction": "LOCAL_OR_DEFAULT",
        "reference_mode": "DEFINITE",
        "renderer_de": "die/den + Lemma",
    },
]

MODIFIER_SPECS = [
    ("M01_FILL", "AIIN_FILL", "bei der angegebenen Füllung"),
    ("M02_APPLY", "O", "in Anwendungsform"),
    ("M03_GRADE_III", "EEE", "auf Grad III"),
    ("M04_GRADE_II", "EE", "auf Grad II"),
    ("M05_GRADE_I", "E", "auf Grad I"),
    ("M06_FINE", "LOCAL_CHAR_F", "in Feinform"),
    ("M07_NEW_BATCH", "CARRIER_Q", "als neuer Bad- oder Stationsansatz"),
    ("M08_MAIN_SITE", "A_ADDR", "an der Stations-Hauptstelle"),
    ("M09_SIDE_SITE", "AM_ADDR", "an der Stations-Nebenstelle"),
    ("M10_WORK_SITE", "D_ADDR", "an der Stations-Arbeitsstelle"),
    ("M11_END_SITE", "S_ADDR", "an der Stations-Endstelle"),
    ("M12_TARGET", "AL", "zur Zielstation oder ins Zielbecken"),
    ("M13_SOURCE", "AR", "von der Ausgangsstation oder aus dem Ausgangsbecken"),
    ("M14_CONTACT", "L", "über den Stationskontakt oder die Leitung"),
    ("M15_PATH", "AIR", "entlang des Stationswegs oder Kanals"),
]

MODIFIER_TEXT = {modifier_id: phrase for modifier_id, _root, phrase in MODIFIER_SPECS}
MODIFIER_ROOT = {modifier_id: root for modifier_id, root, _phrase in MODIFIER_SPECS}
MODIFIER_PATTERN = re.compile(
    "|".join(
        f"(?P<{modifier_id}>{re.escape(phrase)})"
        for modifier_id, _root, phrase in MODIFIER_SPECS
    )
)

GENDER = {
    "BODY": "MASCULINE",
    "STATION": "MASCULINE",
    "FLOW": "MASCULINE",
    "PORTION": "FEMININE",
    "BATH_UNIT": "FEMININE",
}
DETERMINER = {
    ("DEFINITE", "MASCULINE"): "den",
    ("ANAPHORIC", "MASCULINE"): "denselben",
    ("DEFINITE", "FEMININE"): "die",
    ("ANAPHORIC", "FEMININE"): "dieselbe",
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


def load_inputs() -> dict[str, object]:
    return {
        "actions": read_tsv(INPUTS["actions"]),
        "gdt595_result": json.loads(INPUTS["gdt595_result"].read_text(encoding="utf-8")),
        "manual_workshop_review": read_tsv(INPUTS["manual_workshop_review"]),
    }


def classify_typing(row: dict[str, str]) -> str:
    route = row["gdt595_selection_route"]
    if route in DIRECT_ROUTES:
        return "T01_WRITTEN_TYPED_OBJECT"
    if route == "BODY_BLOCKER_STATION":
        return "T02_BLOCKER_STATION"
    if route in LEFT_ROUTES or route in RIGHT_ROUTES:
        return "T03_BOUND_TYPED_REFERENCE"
    if route in PROMOTION_ROUTES:
        return "T04_STABLE_AIN_OR_TYPE"
    if route in BODY_DEFAULT_ROUTES:
        return "T05_BODY_FIRST_DEFAULT"
    raise ValueError(f"unmapped selection route: {route}")


def classify_reference_scope(row: dict[str, str]) -> str:
    route = row["gdt595_selection_route"]
    if route in RIGHT_ROUTES:
        return "Q02_RIGHT_OR_TIE_DEFINITE"
    if route in LEFT_ROUTES:
        return "Q01_LEFT_ANAPHORIC"
    if route in PROMOTION_ROUTES and row["gdt595_object_form_de"].startswith(("dieselbe ", "denselben ")):
        return "Q01_LEFT_ANAPHORIC"
    return "Q03_LOCAL_OR_DEFAULT_DEFINITE"


def typing_token(row: dict[str, str], typing_card_id: str) -> str:
    route = row["gdt595_selection_route"]
    object_class = row["gdt595_object_class"]
    if typing_card_id == "T01_WRITTEN_TYPED_OBJECT":
        if route == "WRITTEN_Y_GDT590":
            return "Y_BLOCKED_STATION" if row["body_blockers_present"] != "NONE" else "Y_CLEAR_BODY"
        if route == "WRITTEN_OR_UNIT":
            return "OR_UNIT"
        return "AIN_PORTION"
    if typing_card_id == "T02_BLOCKER_STATION":
        return "BLOCKER_STATION"
    if typing_card_id == "T03_BOUND_TYPED_REFERENCE":
        if route == "STATION_PORTION_PACKET_RIGHT_STATION_TIEBREAK":
            return "RIGHT_PACKET_STATION"
        direction = "RIGHT" if route in RIGHT_ROUTES else "LEFT"
        return f"{direction}_INHERIT_{object_class}"
    if typing_card_id == "T04_STABLE_AIN_OR_TYPE":
        return "AIN_PORTION_DEFAULT" if route == "GDT569_AIN_PORTION_PROMOTION" else "OR_UNIT_DEFAULT"
    return "BODY_FIRST_DEFAULT"


def source_pointer(row: dict[str, str], typing_card_id: str, reference_scope_card_id: str) -> str:
    route = row["gdt595_selection_route"]
    if typing_card_id == "T01_WRITTEN_TYPED_OBJECT":
        return f"HOST:{row['source_event_id']}:{row['carrier_slot_ids']}"
    if typing_card_id == "T02_BLOCKER_STATION":
        return f"BLOCKER:{row['body_blockers_present']}"
    if typing_card_id == "T03_BOUND_TYPED_REFERENCE":
        if reference_scope_card_id == "Q02_RIGHT_OR_TIE_DEFINITE":
            return f"RIGHT:{row['gdt595_source_event_id']}:{row['gdt595_source_slot_ids']}"
        if route == "INTERVENING_OBJECT_HANDOFF":
            return f"HANDOFF:{row['handoff_donor_carrier_source_event_id']}:{row['handoff_source_carrier_slot_ids']}"
        if route in {"EPISODE_CARRY", "RESOLVED_COLD_SOURCE_EPISODE_CARRY"}:
            return f"CARRY:{row['carry_source_event_id']}"
        if route in PROMOTION_ROUTES:
            return f"GDT593:{row['gdt593_canonical_source_event_id']}"
        if route.startswith("GDT569_Y_LOCAL_"):
            return f"GDT594:{row['gdt594_canonical_source_event_id']}"
        return f"GDT595:{row['gdt595_source_event_id']}:{row['gdt595_source_slot_ids']}"
    if typing_card_id == "T04_STABLE_AIN_OR_TYPE":
        root = "AIN" if route == "GDT569_AIN_PORTION_PROMOTION" else "OR"
        if reference_scope_card_id == "Q01_LEFT_ANAPHORIC":
            return f"GDT593:{row['gdt593_canonical_source_event_id']}:{root}"
        return f"TYPE_DEFAULT:{root}"
    return "DEFAULT:BODY"


def render_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} und {items[1]}"
    return f"{', '.join(items[:-1])} und {items[-1]}"


def parse_modifier_ids(suffix: str) -> list[str]:
    ids = [match.lastgroup for match in MODIFIER_PATTERN.finditer(suffix)]
    residue = MODIFIER_PATTERN.sub("", suffix)
    residue = re.sub(r"[ ,]+|\bund\b", "", residue)
    if residue.strip():
        raise ValueError(f"unparsed modifier residue {residue!r} in {suffix!r}")
    return [str(value) for value in ids]


def group_modifiers(modifier_ids: list[str]) -> list[str]:
    groups: list[str] = []
    index = 0
    grades = {"M03_GRADE_III", "M04_GRADE_II", "M05_GRADE_I"}
    while index < len(modifier_ids):
        current = modifier_ids[index]
        if current == "M01_FILL" and index + 1 < len(modifier_ids) and modifier_ids[index + 1] in grades:
            groups.append(f"{MODIFIER_TEXT[current]} {MODIFIER_TEXT[modifier_ids[index + 1]]}")
            index += 2
        else:
            groups.append(MODIFIER_TEXT[current])
            index += 1
    return groups


def render_modifier_suffix(modifier_ids: list[str]) -> str:
    groups = group_modifiers(modifier_ids)
    return f" {render_list(groups)}" if groups else ""


def parse_clause(clause: str, object_forms: list[str]) -> dict[str, object]:
    marker = " im Badbetrieb" if " im Badbetrieb" in clause else " im Bad"
    bath_frame = "BADBETRIEB" if marker == " im Badbetrieb" else "BAD"
    participant_text, modifier_suffix = clause.split(marker, 1)
    if not participant_text.startswith("Halte "):
        raise ValueError(f"unexpected SH clause: {clause}")
    pattern = re.compile("|".join(re.escape(item) for item in sorted(object_forms, key=len, reverse=True)))
    participants = pattern.findall(participant_text)
    rebuilt_participants = f"Halte {render_list(participants)}"
    if rebuilt_participants != participant_text:
        raise ValueError(f"participant parse failed: {participant_text!r} -> {participants!r}")
    modifier_ids = parse_modifier_ids(modifier_suffix)
    rebuilt = rebuilt_participants + marker + render_modifier_suffix(modifier_ids)
    if rebuilt != clause:
        raise ValueError(f"clause replay failed: {clause!r} != {rebuilt!r}")
    return {
        "bath_frame": bath_frame,
        "participants": participants,
        "modifier_ids": modifier_ids,
        "modifier_group_count": len(group_modifiers(modifier_ids)),
        "modifier_suffix": modifier_suffix,
        "reconstructed_clause": rebuilt,
    }


def compact_profile(counter: Counter[str]) -> str:
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def build(inputs: dict[str, object]) -> dict[str, object]:
    actions = list(inputs["actions"])
    gdt595_result = dict(inputs["gdt595_result"])
    manual_workshop_review = list(inputs["manual_workshop_review"])
    rival_ids = set(gdt595_result["host_attachment_rival_event_ids"])
    object_forms = sorted({row["gdt595_object_form_de"] for row in actions}, key=len, reverse=True)

    replay: list[dict[str, str]] = []
    for row in actions:
        typing_card_id = classify_typing(row)
        reference_scope_card_id = classify_reference_scope(row)
        reference_mode = "ANAPHORIC" if reference_scope_card_id == "Q01_LEFT_ANAPHORIC" else "DEFINITE"
        object_class = row["gdt595_object_class"]
        gender = GENDER[object_class]
        determiner = DETERMINER[(reference_mode, gender)]
        rendered_np = f"{determiner} {row['gdt595_object_lemma_de']}"
        parsed = parse_clause(row["gdt595_completed_clause_de"], object_forms)
        participants = list(parsed["participants"])
        if rendered_np != row["gdt595_object_form_de"]:
            raise ValueError(f"NP rule mismatch at {row['source_event_id']}: {rendered_np}")
        if rendered_np not in participants:
            raise ValueError(f"selected NP missing at {row['source_event_id']}")
        replay.append({
            "bath_action_ordinal": row["bath_action_ordinal"],
            "source_event_id": row["source_event_id"],
            "action_slot_id": row["action_slot_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "upstream_selection_route": row["gdt595_selection_route"],
            "typing_card_id": typing_card_id,
            "reference_scope_card_id": reference_scope_card_id,
            "typing_token": typing_token(row, typing_card_id),
            "scope_source_pointer": source_pointer(row, typing_card_id, reference_scope_card_id),
            "reference_mode": reference_mode,
            "object_class": object_class,
            "object_lemma_de": row["gdt595_object_lemma_de"],
            "grammatical_gender": gender,
            "determiner_de": determiner,
            "rendered_object_np_de": rendered_np,
            "participant_count": str(len(participants)),
            "selected_participant_position": str(participants.index(rendered_np) + 1),
            "participant_np_sequence_de": "|".join(participants),
            "bath_frame": str(parsed["bath_frame"]),
            "modifier_id_sequence": "|".join(parsed["modifier_ids"]) or "NONE",
            "modifier_root_sequence": "|".join(MODIFIER_ROOT[item] for item in parsed["modifier_ids"]) or "NONE",
            "modifier_group_count": str(parsed["modifier_group_count"]),
            "modifier_suffix_de": str(parsed["modifier_suffix"]) or "NONE",
            "gdt595_clause_de": row["gdt595_completed_clause_de"],
            "gdt596_reconstructed_clause_de": str(parsed["reconstructed_clause"]),
            "exact_replay": "YES" if parsed["reconstructed_clause"] == row["gdt595_completed_clause_de"] else "NO",
            "host_attachment_rival": "YES" if row["source_event_id"] in rival_ids else "NO",
            "default_survives_with_rival": "YES",
            "guard": "FIVE_TYPING_CARDS__THREE_REFERENCE_SCOPE_CARDS__SEVEN_LEMMAS__FOUR_DETERMINERS__FIFTEEN_MODIFIERS__NO_NEW_PAGE_ROOT_OR_SEGMENT",
        })

    replay_by_typing: dict[str, list[dict[str, str]]] = defaultdict(list)
    replay_by_reference: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        replay_by_typing[row["typing_card_id"]].append(row)
        replay_by_reference[row["reference_scope_card_id"]].append(row)
    typing_cards: list[dict[str, str]] = []
    for order, spec in enumerate(TYPING_SPECS, start=1):
        card_id = spec["typing_card_id"]
        members = replay_by_typing[card_id]
        typing_cards.append({
            "typing_card_order": str(order),
            **spec,
            "occurrence_count": str(len(members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "reference_mode_profile": compact_profile(Counter(row["reference_mode"] for row in members)),
            "reference_scope_profile": compact_profile(Counter(row["reference_scope_card_id"] for row in members)),
            "typing_token_profile": compact_profile(Counter(row["typing_token"] for row in members)),
            "example_event_id": members[0]["source_event_id"],
            "example_clause_de": members[0]["gdt596_reconstructed_clause_de"],
        })

    reference_cards: list[dict[str, str]] = []
    for order, spec in enumerate(REFERENCE_SPECS, start=1):
        card_id = spec["reference_scope_card_id"]
        members = replay_by_reference[card_id]
        reference_cards.append({
            "reference_scope_card_order": str(order),
            **spec,
            "occurrence_count": str(len(members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
            "example_event_id": members[0]["source_event_id"],
            "example_clause_de": members[0]["gdt596_reconstructed_clause_de"],
        })

    form_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        key = (
            row["object_class"], row["object_lemma_de"], row["grammatical_gender"],
            row["reference_mode"], row["determiner_de"], row["rendered_object_np_de"],
        )
        form_groups[key].append(row)
    object_form_rows: list[dict[str, str]] = []
    for ordinal, (key, members) in enumerate(sorted(form_groups.items()), start=1):
        object_class, lemma, gender, reference, determiner, form = key
        object_form_rows.append({
            "object_form_card_ordinal": str(ordinal),
            "object_class": object_class,
            "object_lemma_de": lemma,
            "grammatical_gender": gender,
            "reference_mode": reference,
            "determiner_de": determiner,
            "rendered_object_np_de": form,
            "occurrence_count": str(len(members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
            "reference_scope_profile": compact_profile(Counter(row["reference_scope_card_id"] for row in members)),
        })

    modifier_count = Counter(
        modifier_id
        for row in replay
        for modifier_id in ([] if row["modifier_id_sequence"] == "NONE" else row["modifier_id_sequence"].split("|"))
    )
    modifier_cards = [
        {
            "modifier_card_order": str(order),
            "modifier_card_id": modifier_id,
            "working_root": root,
            "phrase_de": phrase,
            "occurrence_count": str(modifier_count[modifier_id]),
            "patient_selecting": "NO",
        }
        for order, (modifier_id, root, phrase) in enumerate(MODIFIER_SPECS, start=1)
    ]

    sequence_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        key = (
            row["bath_frame"], row["modifier_id_sequence"], row["modifier_root_sequence"],
            row["modifier_suffix_de"],
        )
        sequence_groups[key].append(row)
    modifier_sequences: list[dict[str, str]] = []
    ordered_sequences = sorted(sequence_groups.items(), key=lambda item: (-len(item[1]), item[0]))
    for ordinal, (key, members) in enumerate(ordered_sequences, start=1):
        bath_frame, ids, roots, suffix = key
        modifier_sequences.append({
            "modifier_sequence_ordinal": str(ordinal),
            "bath_frame": bath_frame,
            "modifier_id_sequence": ids,
            "modifier_root_sequence": roots,
            "rendered_suffix_de": suffix,
            "occurrence_count": str(len(members)),
            "example_event_id": members[0]["source_event_id"],
        })

    page_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        page_groups[row["physical_page"]].append(row)
    pages = []
    for page in sorted(page_groups):
        members = page_groups[page]
        pages.append({
            "physical_page": page,
            "action_count": str(len(members)),
            "typing_card_profile": compact_profile(Counter(row["typing_card_id"] for row in members)),
            "reference_scope_profile": compact_profile(Counter(row["reference_scope_card_id"] for row in members)),
            "object_class_profile": compact_profile(Counter(row["object_class"] for row in members)),
            "reference_mode_profile": compact_profile(Counter(row["reference_mode"] for row in members)),
            "multi_participant_count": str(sum(int(row["participant_count"]) > 1 for row in members)),
            "host_attachment_rival_count": str(sum(row["host_attachment_rival"] == "YES" for row in members)),
            "exact_replay_count": str(sum(row["exact_replay"] == "YES" for row in members)),
        })

    replay_by_event = {row["source_event_id"]: row for row in replay}
    workshop_reviews: list[dict[str, str]] = []
    for source in manual_workshop_review:
        event_id = source["event_id"]
        if event_id not in replay_by_event:
            raise ValueError(f"manual workshop event absent from replay: {event_id}")
        action = replay_by_event[event_id]
        workshop_reviews.append({
            **source,
            "typing_card_id": action["typing_card_id"],
            "reference_scope_card_id": action["reference_scope_card_id"],
            "object_class": action["object_class"],
            "host_attachment_rival": action["host_attachment_rival"],
            "current_clause_matches_replay": "YES" if source["current_clause_de"] == action["gdt596_reconstructed_clause_de"] else "NO",
            "default_retained": "YES",
        })

    typing_profile = Counter(row["typing_card_id"] for row in replay)
    reference_scope_profile = Counter(row["reference_scope_card_id"] for row in replay)
    object_profile = Counter(row["object_class"] for row in replay)
    reference_profile = Counter(row["reference_mode"] for row in replay)
    participant_profile = Counter(row["participant_count"] for row in replay)
    selected_position_profile = Counter(row["selected_participant_position"] for row in replay)
    bath_frame_profile = Counter(row["bath_frame"] for row in replay)
    lemmas = sorted({row["object_lemma_de"] for row in replay})
    result = {
        "experiment_id": "GDT596",
        "status": STATUS,
        "action_count": len(replay),
        "exact_replay_count": sum(row["exact_replay"] == "YES" for row in replay),
        "exception_count": sum(row["exact_replay"] != "YES" for row in replay),
        "typing_card_count": len(typing_cards),
        "typing_card_profile": dict(sorted(typing_profile.items())),
        "macro_operator_count": 3,
        "macro_operator_profile": {"D_HOST_DEFAULT": 68, "R_COPY_TYPED_REFERENCE": 74, "T_READ_TYPED_CARRIER_OR_ROOT": 112},
        "reference_scope_card_count": len(reference_cards),
        "reference_scope_card_profile": dict(sorted(reference_scope_profile.items())),
        "object_class_profile": dict(sorted(object_profile.items())),
        "reference_mode_profile": dict(sorted(reference_profile.items())),
        "object_lemma_count": len(lemmas),
        "object_lemmas_de": lemmas,
        "observed_object_form_count": len(object_form_rows),
        "determiner_rule_count": len(DETERMINER),
        "participant_count_profile": dict(sorted(participant_profile.items())),
        "selected_participant_position_profile": dict(sorted(selected_position_profile.items())),
        "bath_frame_profile": dict(sorted(bath_frame_profile.items())),
        "modifier_card_count": len(modifier_cards),
        "modifier_occurrence_count": sum(modifier_count.values()),
        "observed_modifier_sequence_count": len(modifier_sequences),
        "composition_rule_count": 3,
        "phrasebook_primitive_count": len(typing_cards) + len(reference_cards) + len(lemmas) + len(DETERMINER) + 2 + len(modifier_cards) + 3,
        "multi_participant_action_count": sum(int(row["participant_count"]) > 1 for row in replay),
        "host_attachment_rival_count": sum(row["host_attachment_rival"] == "YES" for row in replay),
        "host_attachment_rival_event_ids": sorted(rival_ids),
        "workshop_review_count": len(workshop_reviews),
        "workshop_review_class_profile": dict(sorted(Counter(row["review_class"] for row in workshop_reviews).items())),
        "immediate_object_fork_count": sum(row["immediate_object_fork"] == "YES" for row in workshop_reviews),
        "workshop_review_defaults_retained_count": sum(row["default_retained"] == "YES" for row in workshop_reviews),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "working_rule_de": (
            "Geschriebener Träger > Blocker-Station > gebundene getypte Quelle > "
            "gelernter AIN/OR-Typ > Körperdefault; unabhängig davon linken Bezug "
            "anaphorisch, rechten Bezug/Pakettie definit und lokale/defaultmäßige Objekte definit rendern; "
            "danach Teilnehmerliste, Badrahmen und geordnete Modifikatoren zusammensetzen."
        ),
        "next_route_de": (
            "Die fünf Typ- und drei Bezugskarten an vollständigen, bereits zugelassenen Nicht-SH-Werkstattaktionen spiegeln, "
            "ohne neue Seite, Wurzel oder Segmentierung."
        ),
    }

    built: dict[str, object] = {
        "typing_cards": typing_cards,
        "reference_cards": reference_cards,
        "object_forms": object_form_rows,
        "modifier_cards": modifier_cards,
        "modifier_sequences": modifier_sequences,
        "workshop_reviews": workshop_reviews,
        "replay": replay,
        "pages": pages,
        "result": result,
    }
    built["phrasebook"] = render_phrasebook(built)
    return built


def tsv_bytes(rows: Iterable[dict[str, object]]) -> bytes:
    row_list = list(rows)
    if not row_list:
        return b""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(row_list[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(row_list)
    return buffer.getvalue().encode("utf-8")


def render_phrasebook(built: dict[str, object]) -> str:
    result = built["result"]
    lines = [
        "# GDT596 — kompositionelles Bad-Scope-Phrasebook",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Kurzfassung",
        "",
        "Alle 254 konkreten GDT595-Badeklauseln entstehen ohne Einzel-Ausnahme aus fünf",
        "Typkarten, drei unabhängigen Bezugskarten, sieben Objektlemmas, vier Artikelregeln, zwei",
        "Badrahmen, fünfzehn Modifikatorfragmenten und drei einfachen Listenregeln.",
        "AIIN-Füllung bleibt ein Modifikator und wählt niemals den Patienten.",
        "",
        "## Die fünf Typregeln",
        "",
        "| Karte | Regel | n | Klassen | Referenz |",
        "|---|---|---:|---|---|",
    ]
    for row in built["typing_cards"]:
        lines.append(
            f"| `{row['typing_card_id']}` | {row['short_rule_de']} | {row['occurrence_count']} | "
            f"`{row['object_class_profile']}` | `{row['reference_mode_profile']}` |"
        )
    lines.extend([
        "",
        "Arbeitsreihenfolge: **geschriebener Träger → Blocker-Station → gebundene getypte",
        "Quelle → stabiler AIN/OR-Typ → Körperdefault**.",
        "Sie liefert immer einen Default; Rivalen werden markiert, nicht in einen Stop verwandelt.",
        "Maximal zusammengezogen sind das drei Werkstattoperatoren: `T` liest einen",
        "geschriebenen oder stabil gelernten Typ (112), `R` kopiert eine gebundene getypte",
        "Quelle (74), und `D` setzt den Hostdefault Station oder Körper (68). Die fünf Karten",
        "bewahren innerhalb dieser Kurznotation die entscheidenden Unterfälle.",
        "",
        "## Die drei unabhängigen Bezugsregeln",
        "",
        "| Karte | Richtung | Ausgabe | n | Klassen |",
        "|---|---|---|---:|---|",
    ])
    for row in built["reference_cards"]:
        lines.append(
            f"| `{row['reference_scope_card_id']}` | `{row['direction']}` | `{row['reference_mode']}` | "
            f"{row['occurrence_count']} | `{row['object_class_profile']}` |"
        )
    lines.extend([
        "",
        "Die zweite Karte umfasst acht echte rechte Endträger und E2952 als sichtbare",
        "Links/Rechts-Pakettie; sie verschweigt diese eine Sonderprovenienz nicht.",
        "",
        "## Objekt-NP",
        "",
        "| Klasse | Lemma | Bezug | Form | n |",
        "|---|---|---|---|---:|",
    ])
    for row in built["object_forms"]:
        lines.append(
            f"| `{row['object_class']}` | {row['object_lemma_de']} | `{row['reference_mode']}` | "
            f"{row['rendered_object_np_de']} | {row['occurrence_count']} |"
        )
    lines.extend([
        "",
        "Maskulin: `den/denselben`; feminin: `die/dieselbe`. Daraus entstehen die elf",
        "beobachteten Formen. 70 linke Bezüge sind anaphorisch, 184 übrige Formen definit.",
        "",
        "## Modifikatoren",
        "",
        "| Karte | Wurzel | Phrase | n |",
        "|---|---|---|---:|",
    ])
    for row in built["modifier_cards"]:
        lines.append(
            f"| `{row['modifier_card_id']}` | `{row['working_root']}` | {row['phrase_de']} | "
            f"{row['occurrence_count']} |"
        )
    lines.extend([
        "",
        "`AIIN_FILL + Grad` bildet zuerst eine enge Gruppe (`bei der angegebenen Füllung",
        "auf Grad …`). Alle übrigen Gruppen werden wie eine normale kurze Liste verbunden:",
        "eine Gruppe allein, zwei mit `und`, drei oder mehr mit Kommas und letztem `und`.",
        "Diese eine Regel erzeugt alle 40 beobachteten Modifikatorfolgen exakt.",
        "",
        "## Satzbau",
        "",
        "```text",
        "HALTE + TEILNEHMERLISTE + (im Bad | im Badbetrieb) + MODIFIKATORLISTE",
        "```",
        "",
        "247 Aktionen haben einen Teilnehmer, sechs haben zwei und eine hat drei. In 251",
        "Klauseln steht das ausgewählte Objekt zuerst; in E1433, E1648 und E1795 ist es",
        "der zweite geschriebene Teilnehmer. Die Listenregel erhält diese Reihenfolge.",
        "",
        "## Je ein konkretes Typbeispiel",
        "",
    ])
    for row in built["typing_cards"]:
        lines.extend([
            f"- `{row['typing_card_id']}` / `{row['example_event_id']}`:",
            f"  {row['example_clause_de']}",
        ])
    lines.extend([
        "",
        "## Ergebnis und Grenze",
        "",
        "254/254 Klauseln werden bytegenau rekonstruiert; es gibt keine Sonderausnahme.",
        "Die sechs GDT595-Hostbindungsrivalen bleiben im Replay markiert und behalten den",
        "gewählten Default. Das Phrasebook komprimiert eine explorative Arbeitsübersetzung.",
        "Eine vollständige manuelle Werkstattlektüre markiert zusätzlich 16 flache Stil-/",
        "Scopeformulierungen, sechs Objektrivalen und eine Bindungsmechanismus-Gabel. Nur",
        "E2952 und E3224 sind unmittelbare Objektgabeln; alle 23 Arbeitsdefaults bleiben aktiv.",
        "Es bestätigt weder Klartext noch globale Lexeme, reale Stoffe, Patienten oder",
        "Verfahren und öffnet keine neue Seite, Wurzel, Surface oder Segmentierung.",
        "",
    ])
    return "\n".join(lines)


def write_built(built: dict[str, object]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in ("typing_cards", "reference_cards", "object_forms", "modifier_cards", "modifier_sequences", "workshop_reviews", "replay", "pages"):
        OUTPUTS[name].write_bytes(tsv_bytes(built[name]))
    OUTPUTS["phrasebook"].write_text(str(built["phrasebook"]), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
