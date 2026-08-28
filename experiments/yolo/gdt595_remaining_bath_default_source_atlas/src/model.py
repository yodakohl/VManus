#!/usr/bin/env python3
"""Build GDT595's source atlas for the last generic bath-object defaults."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt595_remaining_bath_default_source_atlas"
ART = EXP / "artifacts"
BATH_PAGES = frozenset({"f75r", "f77r", "f81r", "f81v", "f82r", "f83r"})
STATUS = (
    "PASS_44_COLD_DEFAULTS_COMPLETED__20_AIIN_FILL_CONTEXTS__"
    "18_LATE_Y_PACKETS__6_BARE_CONTEXTS__"
    "HYBRID_16_BODY_23_STATION_3_PORTION_2_BATH_UNIT__"
    "2_DEPENDENT_CARRIES_PROPAGATED__254_SPECIFIC_OBJECTS__"
    "0_BATH_OBJECT_DEFAULTS_REMAIN"
)

INPUTS = {
    "gdt594_actions": ROOT / "experiments/yolo/gdt594_gdt569_y_bath_occurrence_completion/artifacts/gdt594_254_y_completed_bath_actions.tsv",
    "gdt594_statements": ROOT / "experiments/yolo/gdt594_gdt569_y_bath_occurrence_completion/artifacts/gdt594_793_y_completed_statement_reader.tsv",
    "gdt581_slots": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_15889_complete_slot_ledger.tsv",
    "gdt582_defaults": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "gdt590_slots": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_1243_adjudicated_slot_replay.tsv",
    "historical_sources": EXP / "sources/gdt595_historical_analogy_sources.tsv",
}

OUTPUTS = {
    "source_cards": ART / "gdt595_44_cold_default_source_cards.tsv",
    "model_comparison": ART / "gdt595_44_model_comparison.tsv",
    "residuals": ART / "gdt595_6_context_residual_choices.tsv",
    "propagations": ART / "gdt595_2_dependent_carry_propagations.tsv",
    "actions": ART / "gdt595_254_fully_specific_bath_actions.tsv",
    "changed_statements": ART / "gdt595_changed_statements.tsv",
    "statements": ART / "gdt595_793_fully_specific_statement_reader.tsv",
    "pages": ART / "gdt595_6_page_profiles.tsv",
    "reader": ART / "GDT595_FULLY_SPECIFIC_BATH_READER.md",
    "result": ART / "gdt595_result.json",
    "validation": ART / "gdt595_validation.json",
}

COLD_EXPECTED = frozenset({
    "G407-E1445", "G407-E1523", "G407-E1573", "G407-E1670", "G407-E1742",
    "G407-E2414", "G407-E2416", "G407-E2426", "G407-E2431", "G407-E2444",
    "G407-E2448", "G407-E2450", "G407-E2452", "G407-E2461", "G407-E2503",
    "G407-E2520", "G407-E2552", "G407-E2597", "G407-E2634", "G407-E2647",
    "G407-E2670", "G407-E2857", "G407-E2863", "G407-E2906", "G407-E2927",
    "G407-E2932", "G407-E2952", "G407-E2988", "G407-E3051", "G407-E3205",
    "G407-E3218", "G407-E3224", "G407-E3227", "G407-E3336", "G407-E3441",
    "G407-E3483", "G407-E3488", "G407-E3523", "G407-E3533", "G407-E3560",
    "G407-E3563", "G407-E3609", "G407-E3664", "G407-E3718",
})

AIIN_FILL_EXPECTED = frozenset({
    "G407-E2414", "G407-E2416", "G407-E2426", "G407-E2431", "G407-E2444",
    "G407-E2448", "G407-E2450", "G407-E2461", "G407-E2503", "G407-E2552",
    "G407-E2597", "G407-E2634", "G407-E2647", "G407-E2906", "G407-E3218",
    "G407-E3224", "G407-E3227", "G407-E3336", "G407-E3441", "G407-E3483",
})

LATE_Y_EXPECTED = frozenset({
    "G407-E1445", "G407-E1523", "G407-E1573", "G407-E1670", "G407-E1742",
    "G407-E2452", "G407-E2520", "G407-E2857", "G407-E2863", "G407-E3051",
    "G407-E3205", "G407-E3523", "G407-E3533", "G407-E3560", "G407-E3563",
    "G407-E3609", "G407-E3664", "G407-E3718",
})

LATE_Y_BODY_EXPECTED = frozenset({"G407-E1742", "G407-E2452"})

WORKSHOP_BODY = frozenset({
    "G407-E1742", "G407-E2414", "G407-E2416", "G407-E2431", "G407-E2444",
    "G407-E2448", "G407-E2450", "G407-E2452", "G407-E2503", "G407-E2647",
    "G407-E2863", "G407-E2927", "G407-E2932", "G407-E3218", "G407-E3224",
    "G407-E3227", "G407-E3483", "G407-E3523", "G407-E3533", "G407-E3664",
})
WORKSHOP_STATION = frozenset({
    "G407-E1573", "G407-E1670", "G407-E2426", "G407-E2461", "G407-E2520",
    "G407-E2597", "G407-E2634", "G407-E2670", "G407-E2906", "G407-E2952",
    "G407-E3051", "G407-E3205", "G407-E3336", "G407-E3441", "G407-E3488",
    "G407-E3560", "G407-E3563", "G407-E3609", "G407-E3718",
})
WORKSHOP_PORTION = frozenset({"G407-E1445", "G407-E2552", "G407-E2857"})
WORKSHOP_UNIT = frozenset({"G407-E1523", "G407-E2988"})

# The selected hybrid keeps the practical participant-chain reading but applies
# one consistent shared-right-complement correction wherever a same-event final
# Y is independently typed as Station.  These four are the only changes from
# the complete manual workshop pass.
RIGHT_COMPLEMENT_CORRECTIONS = frozenset({
    "G407-E2863", "G407-E3523", "G407-E3533", "G407-E3664",
})
SELECTED_BODY = WORKSHOP_BODY - RIGHT_COMPLEMENT_CORRECTIONS
SELECTED_STATION = WORKSHOP_STATION | RIGHT_COMPLEMENT_CORRECTIONS
SELECTED_PORTION = WORKSHOP_PORTION
SELECTED_UNIT = WORKSHOP_UNIT

MODEL_C_STATION = frozenset({
    "G407-E1445", "G407-E1573", "G407-E1670", "G407-E2520", "G407-E2647",
    "G407-E2857", "G407-E2863", "G407-E2932", "G407-E2988", "G407-E3051",
    "G407-E3205", "G407-E3218", "G407-E3224", "G407-E3488", "G407-E3523",
    "G407-E3533", "G407-E3560", "G407-E3563", "G407-E3609", "G407-E3664",
    "G407-E3718",
})
MODEL_C_BODY = COLD_EXPECTED - MODEL_C_STATION

LEFTWARD_ANAPHORA = frozenset({
    "G407-E1445", "G407-E1523", "G407-E1573", "G407-E1670",
    "G407-E2426", "G407-E2461", "G407-E2520", "G407-E2552", "G407-E2597",
    "G407-E2634", "G407-E2670", "G407-E2857", "G407-E2906", "G407-E2988",
    "G407-E3051", "G407-E3205", "G407-E3336", "G407-E3441", "G407-E3488",
    "G407-E3609", "G407-E3718",
})
TIED_LOCAL_PACKET = frozenset({"G407-E2952"})
RIGHTWARD_COMPLEMENT = frozenset({
    "G407-E1742", "G407-E2452", "G407-E2863", "G407-E3523", "G407-E3533",
    "G407-E3560", "G407-E3563", "G407-E3664",
})
DEFINITE_BODY_DEFAULT = frozenset({
    "G407-E2414", "G407-E2416", "G407-E2431", "G407-E2444", "G407-E2448",
    "G407-E2450", "G407-E2503", "G407-E2647", "G407-E2927", "G407-E3224",
    "G407-E3227", "G407-E3483", "G407-E2932", "G407-E3218",
})

LEFT_SOURCE_SLOTS = {
    "G407-E1445": "RUNNING:G407-E1444@2",
    "G407-E1523": "RUNNING:G407-E1521@2",
    "G407-E1573": "RUNNING:G407-E1571@2",
    "G407-E1670": "RUNNING:G407-E1667@3",
    "G407-E2426": "RUNNING:G407-E2425@2",
    "G407-E2461": "RUNNING:G407-E2459@2",
    "G407-E2520": "RUNNING:G407-E2519@2",
    "G407-E2552": "RUNNING:G407-E2550@2",
    "G407-E2597": "RUNNING:G407-E2594@4|RUNNING:G407-E2595@1",
    "G407-E2634": "RUNNING:G407-E2631@5",
    "G407-E2670": "RUNNING:G407-E2665@3",
    "G407-E2857": "RUNNING:G407-E2856@2",
    "G407-E2906": "RUNNING:G407-E2902@1",
    "G407-E2988": "RUNNING:G407-E2986@2",
    "G407-E3051": "RUNNING:G407-E3050@1|RUNNING:G407-E3050@5",
    "G407-E3205": "RUNNING:G407-E3203@3",
    "G407-E3336": "RUNNING:G407-E3334@4",
    "G407-E3441": "RUNNING:G407-E3438@4",
    "G407-E3488": "RUNNING:G407-E3486@5",
    "G407-E3609": "RUNNING:G407-E3608@1",
    "G407-E3718": "RUNNING:G407-E3714@3|RUNNING:G407-E3715@1",
}

TIE_SOURCE_SLOTS = {
    "G407-E2952": (
        "LEFT:RUNNING:G407-E2951@2|LEFT:RUNNING:G407-E2951@4|"
        "RIGHT:RUNNING:G407-E2953@2"
    )
}

# These are the only six cold actions with neither an AIIN fill nor a written
# same-event Y complement.  They remain explicitly marked as contextual working
# choices rather than being smuggled into a global stem dictionary.
MANUAL_RESIDUALS: dict[str, dict[str, str]] = {
    "G407-E2670": {
        "object_class": "STATION",
        "lemma": "Stationsansatz",
        "form": "denselben Stationsansatz",
        "anchor": "PRECEDING_STATION_PREPARATION_AND_FOLLOWING_STATION_WITHDRAWAL",
        "note": "Vorher wird der Stationsansatz vorbereitet, danach wieder entnommen; die Badeklausel liegt in derselben Arbeitskette.",
    },
    "G407-E2927": {
        "object_class": "BODY",
        "lemma": "Körper",
        "form": "den Körper",
        "anchor": "RESET_WITHOUT_NONMEDIUM_PARTICIPANT",
        "note": "Nach dem Satzreset steht vor der Badeklausel kein nicht-mediumhafter Teilnehmer; Körper bleibt der einfache Arbeitsdefault.",
    },
    "G407-E2932": {
        "object_class": "BODY",
        "lemma": "Körper",
        "form": "den Körper",
        "anchor": "CONTRAST_WITH_EXPLICIT_FOLLOWING_STATION_BATH",
        "note": "Im selben Satz folgt bereits eine ausdrücklich stationsgebundene Badeklausel; der erste unmarkierte Patient wird körpernah gelesen.",
    },
    "G407-E2952": {
        "object_class": "STATION",
        "lemma": "Stationsansatz",
        "form": "den Stationsansatz",
        "anchor": "VISIBLE_STATION_AND_PORTION_APPLICATION_CHAIN",
        "note": "Der Satz führt Stationsansatz und Portion zu und behandelt danach ausdrücklich wieder den Stationsansatz.",
    },
    "G407-E2988": {
        "object_class": "BATH_UNIT",
        "lemma": "Becken- oder Körpereinheit",
        "form": "dieselbe Becken- oder Körpereinheit",
        "anchor": "VISIBLE_PRECEDING_BASIN_OR_BODY_UNIT",
        "note": "Die unmittelbar sichtbare Becken- oder Körpereinheit liefert hier den konkretesten lokalen Badeträger.",
    },
    "G407-E3488": {
        "object_class": "STATION",
        "lemma": "Stationsansatz",
        "form": "denselben Stationsansatz",
        "anchor": "VISIBLE_STATION_AND_MEASURE_TRANSFER_CHAIN",
        "note": "Stationsansatz und Maß werden unmittelbar vor der Badeklausel zugeführt; die Station ist der engste sichtbare Patient.",
    },
}

DEPENDENT_CARRY_EXPECTED = {
    "G407-E3219": "G407-E3218",
    "G407-E3489": "G407-E3488",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def guarded_rows(path: Path, *, selector: str) -> list[dict[str, str]]:
    return list(
        GuardedTSV(
            path,
            selector_column=selector,
            allowed_values=BATH_PAGES,
            forbidden_prefixes=("f84",),
            forbidden_action="skip",
        )
    )


def read_derived_reader(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["physical_page"].lower().startswith("f84") for row in rows):
        raise RuntimeError("derived GDT594 reader unexpectedly contains f84/f84r")
    return rows


def read_plain_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise RuntimeError("refusing to serialize empty TSV")
    stream = io.StringIO(newline="")
    fields = list(rows[0])
    writer = csv.DictWriter(
        stream, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: str(row.get(field, "")) for field in fields})
    return stream.getvalue().encode("utf-8")


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tsv_bytes(rows))


def atom_position(action_slot_id: str) -> int:
    match = re.search(r"@(\d+)(?::|$)", action_slot_id)
    if not match:
        raise RuntimeError(f"action slot lacks atom position: {action_slot_id}")
    return int(match.group(1))


def contextual_class(lemma: str) -> str:
    normalized = lemma.casefold()
    if "körper" in normalized or "koerper" in normalized:
        return "BODY"
    if "station" in normalized:
        return "STATION"
    if "einheit" in normalized:
        return "BATH_UNIT"
    if "strom" in normalized:
        return "FLOW"
    return "UNRESOLVED"


def selected_class_for(event_id: str) -> str:
    memberships = [
        ("BODY", SELECTED_BODY),
        ("STATION", SELECTED_STATION),
        ("PORTION", SELECTED_PORTION),
        ("BATH_UNIT", SELECTED_UNIT),
    ]
    selected = [name for name, members in memberships if event_id in members]
    if len(selected) != 1:
        raise RuntimeError(f"selected class partition error at {event_id}: {selected}")
    return selected[0]


def workshop_class_for(event_id: str) -> str:
    for name, members in (
        ("BODY", WORKSHOP_BODY),
        ("STATION", WORKSHOP_STATION),
        ("PORTION", WORKSHOP_PORTION),
        ("BATH_UNIT", WORKSHOP_UNIT),
    ):
        if event_id in members:
            return name
    raise RuntimeError(f"missing workshop class at {event_id}")


def model_c_class_for(event_id: str) -> str:
    if event_id in MODEL_C_STATION:
        return "STATION"
    if event_id in MODEL_C_BODY:
        return "BODY"
    raise RuntimeError(f"missing Model C class at {event_id}")


def evidence_direction_for(event_id: str) -> str:
    if event_id in LEFTWARD_ANAPHORA:
        return "LEFTWARD_ANAPHORA"
    if event_id in RIGHTWARD_COMPLEMENT:
        return "RIGHTWARD_SHARED_COMPLEMENT"
    if event_id in TIED_LOCAL_PACKET:
        return "BIDIRECTIONAL_PACKET_TIEBREAK"
    if event_id in DEFINITE_BODY_DEFAULT:
        return "DEFINITE_BODY_DEFAULT"
    raise RuntimeError(f"missing evidence direction at {event_id}")


def lemma_for(object_class: str) -> str:
    return {
        "BODY": "Körper",
        "STATION": "Stationsansatz",
        "PORTION": "Anwendungsportion",
        "BATH_UNIT": "Becken- oder Körpereinheit",
    }[object_class]


def object_form(object_class: str, *, anaphoric: bool) -> str:
    if object_class == "BODY":
        return "denselben Körper" if anaphoric else "den Körper"
    if object_class == "STATION":
        return "denselben Stationsansatz" if anaphoric else "den Stationsansatz"
    if object_class == "PORTION":
        return "dieselbe Anwendungsportion" if anaphoric else "die Anwendungsportion"
    if object_class == "BATH_UNIT":
        return (
            "dieselbe Becken- oder Körpereinheit"
            if anaphoric else "die Becken- oder Körpereinheit"
        )
    raise RuntimeError(f"unsupported object class: {object_class}")


def selection_note(event_id: str, object_class: str) -> tuple[str, str, str]:
    """Return route, strength and concise German justification."""
    direction = evidence_direction_for(event_id)
    if direction == "LEFTWARD_ANAPHORA":
        route = "NEAREST_VISIBLE_NONMEDIUM_PARTICIPANT"
        strength = "VISIBLE_SAME_SEGMENT_PARTICIPANT"
        note = (
            f"AIIN/Stationsmaß bleibt gegebenenfalls Medium; der sichtbare linke "
            f"{lemma_for(object_class)}-Teilnehmer derselben Arbeitskette wird wiederaufgenommen."
        )
    elif direction == "RIGHTWARD_SHARED_COMPLEMENT":
        route = "SAME_EVENT_RIGHTWARD_SHARED_COMPLEMENT"
        strength = "WRITTEN_SAME_EVENT_COMPLEMENT_WORKING_RULE"
        note = (
            f"Der im selben Ereignis rechts geschriebene Träger wird als gemeinsames "
            f"{lemma_for(object_class)}-Komplement der kurzen Verbkette gelesen; die "
            "ältere enge Hostanbindung bleibt als Rivale erhalten."
        )
    elif direction == "BIDIRECTIONAL_PACKET_TIEBREAK":
        route = "STATION_PORTION_PACKET_RIGHT_STATION_TIEBREAK"
        strength = "VISIBLE_BIDIRECTIONAL_TIEBREAK"
        note = (
            "Links stehen Stationsansatz und Portion gleichrangig; die folgende "
            "Stationsbehandlung entscheidet den Arbeitsdefault zugunsten der Station."
        )
    else:
        route = "RESET_BODY_FIRST_WITHOUT_NONMEDIUM_PARTICIPANT"
        strength = "EXPLORATORY_BODY_FIRST_DEFAULT"
        if event_id == "G407-E2932":
            note = (
                "Der Portionszeuge beginnt erst im Folgeereignis und die Station erhält "
                "danach eine eigene Badeklausel; die erste resetgebundene Stelle bleibt Körper."
            )
        elif event_id == "G407-E3218":
            note = (
                "AIIN füllt nur die Füllungsstelle; zwei verbundene Badeklauseln werden "
                "körperlich gelesen, bevor die Station ausdrücklich neu übergeben wird."
            )
        else:
            note = (
                "Nach dem letzten Schnitt steht kein belastbarer nicht-mediumhafter "
                "Teilnehmer bereit; Körper ist der einfache definitive Arbeitsdefault."
            )
    return route, strength, note


def patch_bath_clause(old: str, new_form: str) -> str:
    for neutral in ("das zu badende Gut", "dasselbe zu badende Gut"):
        count = old.count(neutral)
        if count == 1:
            return old.replace(neutral, new_form, 1)
    raise RuntimeError(f"bath clause has no unique neutral object: {old!r}")


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "gdt594_actions": guarded_rows(INPUTS["gdt594_actions"], selector="physical_page"),
        "gdt594_statements": read_derived_reader(INPUTS["gdt594_statements"]),
        "gdt581_slots": guarded_rows(INPUTS["gdt581_slots"], selector="physical_page"),
        "gdt582_defaults": guarded_rows(INPUTS["gdt582_defaults"], selector="physical_page"),
        "gdt590_slots": guarded_rows(INPUTS["gdt590_slots"], selector="physical_page"),
        "historical_sources": read_plain_tsv(INPUTS["historical_sources"]),
    }


def build(inputs: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    source_actions = inputs["gdt594_actions"]
    source_statements = inputs["gdt594_statements"]
    if len(source_actions) != 254 or len(source_statements) != 793:
        raise RuntimeError("GDT594 source population drift")
    if (
        len(inputs["historical_sources"]) != 5
        or {row["source_id"] for row in inputs["historical_sources"]}
        != {"HIST01", "HIST02", "HIST03", "HIST04", "HIST05"}
    ):
        raise RuntimeError("historical analogy source deck drift")

    cold_sources = [
        row for row in source_actions
        if row["gdt594_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"
    ]
    cold_ids = {row["source_event_id"] for row in cold_sources}
    if cold_ids != COLD_EXPECTED or len(cold_sources) != 44:
        raise RuntimeError("GDT594 cold-default population drift")
    if (
        SELECTED_BODY | SELECTED_STATION | SELECTED_PORTION | SELECTED_UNIT
    ) != COLD_EXPECTED:
        raise RuntimeError("selected object partition does not cover the cold set")
    if sum(map(len, (
        SELECTED_BODY, SELECTED_STATION, SELECTED_PORTION, SELECTED_UNIT
    ))) != 44:
        raise RuntimeError("selected object partition overlaps")
    if (
        LEFTWARD_ANAPHORA | RIGHTWARD_COMPLEMENT
        | TIED_LOCAL_PACKET | DEFINITE_BODY_DEFAULT
    ) != COLD_EXPECTED:
        raise RuntimeError("evidence-direction partition does not cover the cold set")
    if sum(map(len, (
        LEFTWARD_ANAPHORA, RIGHTWARD_COMPLEMENT,
        TIED_LOCAL_PACKET, DEFINITE_BODY_DEFAULT,
    ))) != 44:
        raise RuntimeError("evidence-direction partition overlaps")

    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    slots_by_id: dict[str, dict[str, str]] = {}
    for row in inputs["gdt581_slots"]:
        slots_by_event[row["source_event_or_card_id"]].append(row)
        slots_by_id[row["slot_id"]] = row
    expected_context_slots = {
        part.removeprefix("LEFT:").removeprefix("RIGHT:")
        for value in (*LEFT_SOURCE_SLOTS.values(), *TIE_SOURCE_SLOTS.values())
        for part in value.split("|")
    }
    missing_context_slots = expected_context_slots - set(slots_by_id)
    if missing_context_slots:
        raise RuntimeError(
            f"missing primary context slots: {sorted(missing_context_slots)}"
        )
    defaults_by_slot = {row["slot_id"]: row for row in inputs["gdt582_defaults"]}
    refinements_by_slot = {
        row["carrier_slot_id"]: row for row in inputs["gdt590_slots"]
    }

    source_cards: list[dict[str, Any]] = []
    card_by_event: dict[str, dict[str, Any]] = {}
    for source in sorted(cold_sources, key=lambda row: int(row["bath_action_ordinal"])):
        event_id = source["source_event_id"]
        fill_present = (
            source["gdt569_inherited_argument_root"] == "AIIN"
            or source["aiin_fill_present"] == "YES"
        )
        late_y_slots = [
            row for row in slots_by_event[event_id]
            if row["layer"] == "RUNNING_ATOM"
            and row["slot_value"] == "Y"
            and int(row["slot_position"]) > atom_position(source["action_slot_id"])
        ]
        if fill_present and late_y_slots:
            raise RuntimeError(f"fill/Y source collision at {event_id}")

        if fill_present:
            source_kind = "AIIN_FILL_CONTEXT"
            frame_evidence_slot_ids = source["carrier_slot_ids"]
            if frame_evidence_slot_ids == "NONE":
                frame_evidence_slot_ids = f"GDT569:{event_id}:AIIN_CONTEXT_CARRY"
            frame_evidence_lemma = "Füllung"
            frame_evidence_basis = (
                "DIRECT_WRITTEN_AIIN_FILL"
                if source["aiin_fill_present"] == "YES"
                else "GDT569_INHERITED_AIIN_FILL"
            )
            complement_order = "AIIN_MEDIUM_PLUS_SEPARATELY_SELECTED_PATIENT"
        elif late_y_slots:
            if len(late_y_slots) != 1:
                raise RuntimeError(f"expected one late Y complement at {event_id}")
            slot = late_y_slots[0]
            default = defaults_by_slot.get(slot["slot_id"])
            if default is None:
                raise RuntimeError(f"missing GDT582 default for {slot['slot_id']}")
            refinement = refinements_by_slot.get(slot["slot_id"])
            if refinement is not None:
                frame_evidence_lemma = refinement["gdt590_lemma_de"]
                frame_evidence_basis = "GDT590_EXACT_ACTION_CONDITIONED_LATE_Y"
            else:
                frame_evidence_lemma = default["gdt582_concrete_default_de"]
                frame_evidence_basis = "GDT582_EXACT_WRITTEN_LATE_Y"
            source_kind = "SAME_EVENT_LATE_Y_PACKET"
            frame_evidence_slot_ids = slot["slot_id"]
            complement_order = "PATIENT_WRITTEN_AFTER_COMPACT_ACTION_CHAIN"
        else:
            manual = MANUAL_RESIDUALS.get(event_id)
            if manual is None:
                raise RuntimeError(f"unclassified cold residual at {event_id}")
            source_kind = "NO_AIIN_OR_SAME_EVENT_Y_CONTEXT"
            frame_evidence_slot_ids = "NO_DIRECT_AIIN_OR_SAME_EVENT_Y_SOURCE"
            frame_evidence_lemma = "NOT_APPLICABLE"
            frame_evidence_basis = "VISIBLE_STATEMENT_OPERATION_CHAIN"
            complement_order = "CONTEXTUAL_PATIENT_COMPLETION"

        selected_class = selected_class_for(event_id)
        selected_lemma = lemma_for(selected_class)
        direction = evidence_direction_for(event_id)
        selected_form = object_form(
            selected_class, anaphoric=direction == "LEFTWARD_ANAPHORA"
        )
        selection_route, working_strength, note = selection_note(
            event_id, selected_class
        )
        if event_id in MANUAL_RESIDUALS:
            note = f"{note} {MANUAL_RESIDUALS[event_id]['note']}"
        if direction == "LEFTWARD_ANAPHORA":
            primary_source_slot_ids = LEFT_SOURCE_SLOTS[event_id]
        elif direction == "RIGHTWARD_SHARED_COMPLEMENT":
            if not late_y_slots:
                raise RuntimeError(f"rightward complement lacks same-event Y at {event_id}")
            primary_source_slot_ids = late_y_slots[0]["slot_id"]
        elif direction == "BIDIRECTIONAL_PACKET_TIEBREAK":
            primary_source_slot_ids = TIE_SOURCE_SLOTS[event_id]
        else:
            primary_source_slot_ids = "NO_PRIMARY_OBJECT_SOURCE"

        old_clause = source["gdt594_completed_clause_de"]
        new_clause = patch_bath_clause(old_clause, selected_form)
        card = {
            "source_card_ordinal": len(source_cards) + 1,
            "bath_action_ordinal": source["bath_action_ordinal"],
            "action_slot_id": source["action_slot_id"],
            "target_event_id": event_id,
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "locus": source["locus"],
            "host_ordinal_in_statement": source["host_ordinal_in_statement"],
            "surface": source["surface"],
            "component_recipe": source["component_recipe"],
            "aiin_fill_present": source["aiin_fill_present"],
            "gdt569_inherited_argument_root": source["gdt569_inherited_argument_root"],
            "same_event_late_y_count": len(late_y_slots),
            "frame_evidence_slot_ids": frame_evidence_slot_ids,
            "frame_evidence_lemma_de": frame_evidence_lemma,
            "frame_evidence_basis": frame_evidence_basis,
            "source_kind": source_kind,
            "complement_order": complement_order,
            "primary_object_source_direction": direction,
            "primary_object_source_slot_ids": primary_source_slot_ids,
            "gdt595_selection_route": selection_route,
            "gdt595_object_class": selected_class,
            "gdt595_object_lemma_de": selected_lemma,
            "gdt595_object_form_de": selected_form,
            "gdt594_previous_clause_de": old_clause,
            "gdt595_completed_clause_de": new_clause,
            "retained_badegut_clause_de": old_clause,
            "retained_body_clause_de": patch_bath_clause(old_clause, "den Körper"),
            "retained_station_clause_de": patch_bath_clause(old_clause, "den Stationsansatz"),
            "retained_portion_clause_de": patch_bath_clause(old_clause, "die Anwendungsportion"),
            "retained_unit_clause_de": patch_bath_clause(old_clause, "die Badeinheit"),
            "workshop_model_class": workshop_class_for(event_id),
            "model_c_class": model_c_class_for(event_id),
            "hybrid_changed_from_workshop": (
                "YES" if event_id in RIGHT_COMPLEMENT_CORRECTIONS else "NO"
            ),
            "hybrid_agrees_with_model_c": (
                "YES" if selected_class == model_c_class_for(event_id) else "NO"
            ),
            "working_strength": working_strength,
            "working_note_de": note,
            "reader_clause_occurrence_index": "PENDING",
            "completion_status": "COLD_DEFAULT_COMPLETED_AT_OCCURRENCE_LEVEL",
            "guard": (
                "EXACT_COLD_ACTION_ONLY__SOURCE_PRIORITY_FILL_THEN_LATE_Y_THEN_CONTEXT__"
                "OLD_BADEGUT_AND_MAJOR_RIVALS_RETAINED__NO_GLOBAL_STEM_REDEFINITION"
            ),
        }
        source_cards.append(card)
        card_by_event[event_id] = card

    observed_fill = {
        row["target_event_id"] for row in source_cards
        if row["source_kind"] == "AIIN_FILL_CONTEXT"
    }
    observed_late_y = {
        row["target_event_id"] for row in source_cards
        if row["source_kind"] == "SAME_EVENT_LATE_Y_PACKET"
    }
    if observed_fill != AIIN_FILL_EXPECTED or observed_late_y != LATE_Y_EXPECTED:
        raise RuntimeError("GDT595 source partition drift")

    # First resolve the 44 cold actions, then carry those newly concrete types
    # through the two already accepted same-segment episode links.
    action_drafts: list[dict[str, Any]] = []
    final_by_event: dict[str, dict[str, Any]] = {}
    for source in source_actions:
        card = card_by_event.get(source["source_event_id"])
        if card is None:
            final_class = source["gdt594_object_class"]
            final_lemma = source["gdt594_object_lemma_de"]
            final_form = source["gdt594_object_form_de"]
            final_clause = source["gdt594_completed_clause_de"]
            status = "RETAINED_GDT594_OBJECT"
            source_kind = "NOT_APPLICABLE"
            source_event = "NOT_APPLICABLE"
            source_slots = "NOT_APPLICABLE"
            route = source["gdt594_selection_route"]
            changed = "NO"
        else:
            final_class = card["gdt595_object_class"]
            final_lemma = card["gdt595_object_lemma_de"]
            final_form = card["gdt595_object_form_de"]
            final_clause = card["gdt595_completed_clause_de"]
            status = "COMPLETED_COLD_DEFAULT"
            source_kind = card["source_kind"]
            source_event = card["target_event_id"]
            source_slots = card["primary_object_source_slot_ids"]
            route = card["gdt595_selection_route"]
            changed = "YES"
        final = {
            **source,
            "gdt595_object_status": status,
            "gdt595_source_kind": source_kind,
            "gdt595_source_event_id": source_event,
            "gdt595_source_slot_ids": source_slots,
            "gdt595_selection_route": route,
            "gdt595_object_class": final_class,
            "gdt595_object_lemma_de": final_lemma,
            "gdt595_object_form_de": final_form,
            "gdt595_completed_clause_de": final_clause,
            "gdt595_clause_changed": changed,
            "gdt595_guard": (
                "GDT594_OBJECT_RETAINED_OR_EXACT_COLD_SOURCE_COMPLETED__"
                "SURFACE_SLOT_ROOT_AND_SEGMENTATION_UNCHANGED"
            ),
        }
        action_drafts.append(final)
        final_by_event[source["source_event_id"]] = final

    propagations: list[dict[str, Any]] = []
    for source, final in zip(source_actions, action_drafts):
        donor_event = source["carry_source_event_id"]
        if (
            source["gdt594_selection_route"] != "EPISODE_CARRY"
            or donor_event not in card_by_event
        ):
            continue
        donor = final_by_event[donor_event]
        carried_class = donor["gdt595_object_class"]
        carried_lemma = donor["gdt595_object_lemma_de"]
        carried_form = object_form(carried_class, anaphoric=True)
        old_clause = source["gdt594_completed_clause_de"]
        new_clause = patch_bath_clause(old_clause, carried_form)
        final.update({
            "gdt595_object_status": "PROPAGATED_FROM_RESOLVED_COLD_SOURCE",
            "gdt595_source_kind": "DEPENDENT_EPISODE_CARRY",
            "gdt595_source_event_id": donor_event,
            "gdt595_source_slot_ids": donor["action_slot_id"],
            "gdt595_selection_route": "RESOLVED_COLD_SOURCE_EPISODE_CARRY",
            "gdt595_object_class": carried_class,
            "gdt595_object_lemma_de": carried_lemma,
            "gdt595_object_form_de": carried_form,
            "gdt595_completed_clause_de": new_clause,
            "gdt595_clause_changed": "YES",
        })
        propagation = {
            "propagation_ordinal": len(propagations) + 1,
            "target_event_id": source["source_event_id"],
            "target_action_slot_id": source["action_slot_id"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "locus": source["locus"],
            "carry_source_event_id": donor_event,
            "carry_source_action_slot_id": source["carry_source_action_slot_id"],
            "carry_host_ordinal_distance": source["carry_host_ordinal_distance"],
            "carry_intervening_host_count": source["carry_intervening_host_count"],
            "source_resolved_class": carried_class,
            "source_resolved_lemma_de": carried_lemma,
            "gdt594_previous_clause_de": old_clause,
            "gdt595_completed_clause_de": new_clause,
            "reader_clause_occurrence_index": "PENDING",
            "guard": "ONLY_EXACT_EXISTING_EPISODE_CARRY_FROM_A_GDT595_RESOLVED_SOURCE",
        }
        propagations.append(propagation)

    if {
        row["target_event_id"]: row["carry_source_event_id"] for row in propagations
    } != DEPENDENT_CARRY_EXPECTED:
        raise RuntimeError("dependent carry propagation population drift")

    # Re-index after propagation updates; event IDs are unique in this particular
    # source/target set, while the full action table can contain other duplicate events.
    actions = action_drafts
    final_by_slot = {row["action_slot_id"]: row for row in actions}
    card_by_slot = {row["action_slot_id"]: row for row in source_cards}
    propagation_by_slot = {
        row["target_action_slot_id"]: row for row in propagations
    }

    source_actions_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    final_actions_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source, final in zip(source_actions, actions):
        source_actions_by_statement[source["statement_id"]].append(source)
        final_actions_by_statement[final["statement_id"]].append(final)
    sort_key = lambda row: (  # noqa: E731
        int(row["host_ordinal_in_statement"]), int(row["bath_action_ordinal"])
    )
    for rows in source_actions_by_statement.values():
        rows.sort(key=sort_key)
    for rows in final_actions_by_statement.values():
        rows.sort(key=sort_key)

    changes_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in actions:
        if row["gdt595_clause_changed"] == "YES":
            changes_by_statement[row["statement_id"]].append(row)

    statements: list[dict[str, Any]] = []
    changed_statements: list[dict[str, Any]] = []
    for source in source_statements:
        statement_id = source["statement_id"]
        changes = changes_by_statement.get(statement_id, [])
        original = source["gdt594_primary_reader_de"]
        patches: list[tuple[int, int, str, dict[str, Any], int]] = []
        for final_action in changes:
            source_action = next(
                row for row in source_actions_by_statement[statement_id]
                if row["action_slot_id"] == final_action["action_slot_id"]
            )
            old_clause = source_action["gdt594_completed_clause_de"]
            ordered_actions = source_actions_by_statement[statement_id]
            occurrence = sum(
                row["gdt594_completed_clause_de"] == old_clause
                and sort_key(row) <= sort_key(source_action)
                for row in ordered_actions
            )
            matches = list(re.finditer(re.escape(old_clause), original))
            if occurrence < 1 or occurrence > len(matches):
                raise RuntimeError(
                    f"cannot locate action clause {occurrence}/{len(matches)} "
                    f"in {statement_id}: {old_clause!r}"
                )
            match = matches[occurrence - 1]
            patches.append((
                match.start(), match.end(), final_action["gdt595_completed_clause_de"],
                final_action, occurrence,
            ))
        if len({(start, end) for start, end, *_ in patches}) != len(patches):
            raise RuntimeError(f"overlapping statement patches at {statement_id}")
        final_text = original
        for start, end, replacement, final_action, occurrence in sorted(
            patches, key=lambda item: item[0], reverse=True
        ):
            final_text = final_text[:start] + replacement + final_text[end:]
            if final_action["action_slot_id"] in card_by_slot:
                card_by_slot[final_action["action_slot_id"]][
                    "reader_clause_occurrence_index"
                ] = occurrence
            elif final_action["action_slot_id"] in propagation_by_slot:
                propagation_by_slot[final_action["action_slot_id"]][
                    "reader_clause_occurrence_index"
                ] = occurrence
        bath_actions = final_actions_by_statement.get(statement_id, [])
        row = {
            **source,
            "gdt595_completion_count": len(changes),
            "gdt595_completed_action_slot_ids": (
                "|".join(row["action_slot_id"] for row in sorted(changes, key=sort_key))
                if changes else "NONE"
            ),
            "gdt595_bath_object_sequence": (
                "|".join(row["gdt595_object_lemma_de"] for row in bath_actions)
                if bath_actions else "NONE"
            ),
            "gdt595_primary_reader_de": final_text,
            "gdt595_reader_changed": "YES" if changes else "NO",
            "gdt595_guard": (
                "ONLY_44_DIRECT_COLD_CLAUSES_AND_2_EXISTING_DEPENDENT_CARRIES_CHANGED__"
                "ALL_OTHER_GDT594_STATEMENTS_BYTE_RETAINED"
            ),
        }
        statements.append(row)
        if changes:
            changed_statements.append(row)

    residuals = [
        row for row in source_cards
        if row["source_kind"] == "NO_AIIN_OR_SAME_EVENT_Y_CONTEXT"
    ]
    model_comparison = [{
        "comparison_ordinal": index,
        "target_event_id": row["target_event_id"],
        "statement_id": row["statement_id"],
        "physical_page": row["physical_page"],
        "surface": row["surface"],
        "morphological_frame": row["source_kind"],
        "primary_object_source_direction": row["primary_object_source_direction"],
        "workshop_model_class": row["workshop_model_class"],
        "source_precedence_model_c_class": row["model_c_class"],
        "selected_hybrid_class": row["gdt595_object_class"],
        "changed_from_workshop": row["hybrid_changed_from_workshop"],
        "agrees_with_model_c": row["hybrid_agrees_with_model_c"],
        "selected_clause_de": row["gdt595_completed_clause_de"],
        "body_rival_de": row["retained_body_clause_de"],
        "station_rival_de": row["retained_station_clause_de"],
        "portion_rival_de": row["retained_portion_clause_de"],
        "unit_rival_de": row["retained_unit_clause_de"],
        "selection_note_de": row["working_note_de"],
        "guard": (
            "THREE_EXPLORATORY_MODELS_COMPARED__SELECTED_HYBRID_IS_WORKING_PRIMARY__"
            "ALL_MAJOR_RIVALS_RETAINED"
        ),
    } for index, row in enumerate(source_cards, start=1)]

    pages: list[dict[str, Any]] = []
    for page in sorted(BATH_PAGES):
        members = [row for row in actions if row["physical_page"] == page]
        direct = [row for row in source_cards if row["physical_page"] == page]
        propagated = [row for row in propagations if row["physical_page"] == page]
        pages.append({
            "page_ordinal": len(pages) + 1,
            "physical_page": page,
            "bath_action_count": len(members),
            "direct_completion_count": len(direct),
            "dependent_propagation_count": len(propagated),
            "source_kind_profile": json.dumps(
                dict(sorted(Counter(row["source_kind"] for row in direct).items())),
                ensure_ascii=False,
                sort_keys=True,
            ),
            "direct_object_profile": json.dumps(
                dict(sorted(Counter(row["gdt595_object_class"] for row in direct).items())),
                ensure_ascii=False,
                sort_keys=True,
            ),
            "final_object_profile": json.dumps(
                dict(sorted(Counter(row["gdt595_object_class"] for row in members).items())),
                ensure_ascii=False,
                sort_keys=True,
            ),
            "guard": "SIX_ALREADY_ADMITTED_BATH_PAGES_ONLY__NO_NEW_PAGE_OR_F84",
        })

    final_profile = Counter(row["gdt595_object_class"] for row in actions)
    direct_profile = Counter(row["gdt595_object_class"] for row in source_cards)
    source_profile = Counter(row["source_kind"] for row in source_cards)
    result = {
        "experiment_id": "GDT595",
        "status": STATUS,
        "bath_action_count": len(actions),
        "statement_count": len(statements),
        "cold_source_card_count": len(source_cards),
        "dependent_carry_propagation_count": len(propagations),
        "changed_action_count": sum(
            row["gdt595_clause_changed"] == "YES" for row in actions
        ),
        "changed_statement_count": len(changed_statements),
        "retained_statement_count": len(statements) - len(changed_statements),
        "source_kind_profile": dict(sorted(source_profile.items())),
        "source_direction_profile": dict(sorted(Counter(
            row["primary_object_source_direction"] for row in source_cards
        ).items())),
        "direct_completion_object_profile": dict(sorted(direct_profile.items())),
        "workshop_model_profile": dict(sorted(Counter(
            row["workshop_model_class"] for row in source_cards
        ).items())),
        "source_precedence_model_c_profile": dict(sorted(Counter(
            row["model_c_class"] for row in source_cards
        ).items())),
        "hybrid_changed_from_workshop_event_ids": sorted(
            RIGHT_COMPLEMENT_CORRECTIONS
        ),
        "host_attachment_rival_event_ids": sorted({
            "G407-E2863", "G407-E3224", "G407-E3523", "G407-E3533",
            "G407-E3563", "G407-E3664",
        }),
        "final_object_profile": dict(sorted(final_profile.items())),
        "late_y_body_event_ids": sorted(
            row["target_event_id"] for row in source_cards
            if row["source_kind"] == "SAME_EVENT_LATE_Y_PACKET"
            and row["gdt595_object_class"] == "BODY"
        ),
        "context_residual_event_ids": sorted(MANUAL_RESIDUALS),
        "dependent_carry_map": dict(sorted(DEPENDENT_CARRY_EXPECTED.items())),
        "historical_analogy_source_count": len(inputs["historical_sources"]),
        "historical_analogy_source_ids": [
            row["source_id"] for row in inputs["historical_sources"]
        ],
        "remaining_cold_bath_object_default_count": sum(
            row["gdt595_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"
            for row in actions
        ),
        "remaining_bath_object_class_count": final_profile.get("BATH_OBJECT", 0),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "working_rule_de": (
            "Die letzten 44 neutralen Badegut-Stellen werden auf Vorkommensebene "
            "vervollständigt. AIIN bleibt in zwanzig überlappenden Konstruktionen "
            "Füllung oder Medium und entscheidet den Patienten nie allein. Einundzwanzig "
            "sichtbare linke Teilnehmer werden anaphorisch wiederaufgenommen; acht "
            "gleichereignisige Endträger dürfen als rechtsabschließendes gemeinsames "
            "Komplement einer kurzen Verbkette wirken; eine Paketgabel wird durch den "
            "Nachkontext entschieden; vierzehn signalärmere Resetstellen erhalten "
            "Körper als definiten Arbeitsdefault. Zwei bestehende Episodenverweise "
            "übernehmen anschließend den neu konkreten Quelltyp. Das ist ein vollständiger "
            "Arbeitsleser, keine globale Gleichsetzung von SH, AIIN oder Y mit einem Nomen."
        ),
    }
    return {
        "source_cards": source_cards,
        "model_comparison": model_comparison,
        "residuals": residuals,
        "propagations": propagations,
        "actions": actions,
        "changed_statements": changed_statements,
        "statements": statements,
        "pages": pages,
        "historical_sources": inputs["historical_sources"],
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    statements = {row["statement_id"]: row for row in built["statements"]}
    actions_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in built["actions"]:
        actions_by_statement[row["statement_id"]].append(row)
    lines = [
        "# GDT595 — vollständig spezifischer Badeaktions-Leser",
        "",
        "Die letzten 44 generischen `Badegut`-Defaults sind hier mit konkreten "
        "Vorkommensbedeutungen gefüllt. Zwanzig AIIN-Kontakte bleiben Füllung/Medium, "
        "achtzehn Zielwörter enthalten ein späteres Y-Paket, und sechs besitzen keines "
        "von beidem; die Objektwahl folgt jedoch der sichtbaren Teilnehmerkette statt "
        "einer pauschalen AIIN- oder Y-Gleichung. "
        "Zwei schon vorher etablierte Episodenverweise übernehmen den dadurch "
        "konkretisierten Quelltyp. Damit hat jede der 254 Badeaktionen einen "
        "spezifischen Arbeitsgegenstand; `Badegut` bleibt in den Kartentabellen als "
        "Rivalenlesung erhalten.",
        "",
        "Das Ergebnis ist ausdrücklich eine durchgängige Arbeitstheorie. Es bedeutet "
        "nicht `AIIN = Körper`, `Y = Stationsansatz` oder `SH = baden`: Füllung, "
        "Patient und Aktionswert bleiben getrennte Stellen der Komposition.",
        "",
    ]
    for page in sorted(BATH_PAGES):
        lines.extend([f"## {page}", ""])
        statement_ids = list(dict.fromkeys(
            row["statement_id"] for row in built["actions"]
            if row["physical_page"] == page
        ))
        for statement_id in statement_ids:
            members = sorted(
                actions_by_statement[statement_id],
                key=lambda row: int(row["bath_action_ordinal"]),
            )
            trace = " → ".join(
                f"{row['source_event_id']}={row['gdt595_object_lemma_de']}"
                f"[{row['gdt595_selection_route']}]"
                for row in members
            )
            lines.extend([
                f"### {statement_id}",
                "",
                f"Objektspur: `{trace}`",
                "",
                statements[statement_id]["gdt595_primary_reader_de"],
                "",
            ])
    lines.extend(["## Die 44 geschlossenen Default-Karten", ""])
    for row in built["source_cards"]:
        lines.append(
            f"- `{row['target_event_id']}` `{row['surface']}`: "
            f"**{row['gdt595_completed_clause_de']}** — "
            f"`{row['primary_object_source_direction']}` über "
            f"`{row['primary_object_source_slot_ids']}`; "
            f"{row['working_note_de']} Rivalenfassung: "
            f"*{row['retained_badegut_clause_de']}*"
        )
    lines.extend(["", "## Zwei abhängige Weitergaben", ""])
    for row in built["propagations"]:
        lines.append(
            f"- `{row['target_event_id']}` übernimmt von "
            f"`{row['carry_source_event_id']}` **{row['source_resolved_lemma_de']}**: "
            f"{row['gdt595_completed_clause_de']}"
        )
    lines.extend([
        "",
        "## Historische Werkstattanalogien",
        "",
        "Die Quellen belegen nicht die Voynich-Bedeutungen, wohl aber die hier "
        "verwendete Arbeitsgrammatik: kurze Verbketten mit gemeinsamem Objekt, "
        "pronominale Wiederaufnahme und die Trennung von Maßangabe und fortgeführtem "
        "Stoff oder Patienten.",
        "",
    ])
    for row in built["historical_sources"]:
        lines.append(
            f"- [{row['source_title']}]({row['source_url']}) "
            f"({row['approx_date']}): {row['gdt595_relevance']} "
            f"Grenze: {row['transfer_limit']}"
        )
    lines.extend([
        "",
        "## Ergebnis",
        "",
        "Im 254-Aktionen-Badkorpus verbleibt keine generische `Badegut`-Klasse. "
        "Die vollständige Objektfolge und alle erhaltenen Alternativen stehen in "
        "`gdt595_254_fully_specific_bath_actions.tsv`; die 793-Satz-Ausgabe enthält "
        "nur die 46 exakt lokalisierten Klauseländerungen und lässt alle übrigen "
        "Sätze bytegleich zu GDT594.",
        "",
    ])
    return "\n".join(lines)


def write_built(built: dict[str, Any]) -> None:
    for name in (
        "source_cards", "model_comparison", "residuals", "propagations", "actions",
        "changed_statements", "statements", "pages",
    ):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["reader"].write_text(render_reader(built), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
