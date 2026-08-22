#!/usr/bin/env python3
"""Build the V62 R2 historical ellipsis/anaphora trace.

The program consumes only the selected V60 exact-card deck and selected V61
clause edition.  Anonymous referent IDs are record-local editorial devices,
not decoded manuscript values.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
RECORD_ORDER = ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")

V60_DECK = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
V61_SELECTION = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_FOUR_ROLE_SELECTION.md"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V61_BOUNDARIES = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_46_LINE_BOUNDARIES.tsv"
V61_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_11_RECORD_CONTINUATIONS.tsv"

STATEMENT_COLUMNS = [
    "statement_id", "record_unit_id", "page", "statement_ordinal_in_record",
    "start_locus", "start_field", "end_locus", "end_field",
    "constituent_loci", "constituent_fields", "physical_line_count",
    "event_count", "event_serials", "closure_sequence", "entry_boundary_class",
    "exit_boundary_class", "internal_cross_line_boundaries",
    "selected_short_card_skeleton", "concrete_workshop_reading",
    "strongest_alternative", "apprentice_reading_rule", "record_flow_context",
    "evidence_basis", "status",
]

BOUNDARY_COLUMNS = [
    "boundary_id", "record_unit_id", "page", "boundary_ordinal_in_record",
    "from_locus", "to_locus", "from_locus_fields", "to_locus_fields",
    "from_locus_closure_pattern", "to_locus_closure_pattern",
    "from_last_field", "from_last_field_closure", "from_last_field_selected_skeleton",
    "from_last_field_local_reading", "to_first_field", "to_first_field_closure",
    "to_first_field_selected_skeleton", "to_first_field_local_reading",
    "classification", "rationale", "strongest_alternative", "from_statement_id",
    "to_statement_id", "cross_line_statement_id", "apprentice_boundary_rule",
    "highlight_f82r_3_to_4", "highlight_all_f83r_boundaries", "status",
]

RECORD_COLUMNS = [
    "record_unit_id", "page", "physical_loci", "fields", "events",
    "line_boundaries", "statements", "open_fields", "terminal_fields",
    "boundary_class_counts", "selected_short_card_skeleton",
    "complete_workshop_reading", "strongest_nonmedical_alternative",
    "strongest_segmentation_pressure", "apprentice_record_rule",
    "inherited_record_contradiction", "status",
]

# A new anonymous item is opened only when the selected clause reading itself
# demands a new part, batch, use, or parallel cell.  These are editorial state
# decisions, never meanings assigned to visible cards.
ACTIVE_RESETS = {
    "H2-S003": "PARALLEL_HARVEST_OR_PREPARATION_CHARGE",
    "H3-S002": "RETAINED_PLANT_PART_BECOMES_ACTIVE",
    "H3-S004": "PARALLEL_POULTICE_PREPARATION",
    "H4-S003": "SECOND_MEDICINAL_USE",
    "H5-S003": "NEXT_PLANT_PART_CELL",
    "H5-S005": "NEXT_HONEY_PREPARATION",
    "H5-S006": "SELECTED_BLOSSOM_PORTION",
    "B1-S002": "NEXT_MEASURED_BATCH",
    "B1-S006": "NEW_MEASURED_VESSEL_PORTION",
    "B1-S007": "NEXT_PARALLEL_HEATING_CELL",
    "B1-S012": "NEW_RINSE_PHASE",
    "B1-S015": "NEXT_PARALLEL_FILL_PHASE",
    "B2-S003": "NEW_MEASURED_BATH_PORTION",
    "B2-S005": "NEXT_BATCH_WITH_F82_EDGE_COPY",
    "B2-S007": "CLEAN_WATER_PHASE",
    "B2-S015": "NEW_RINSE_PHASE",
    "B2-S016": "NEW_MEASURED_OIL_WATER_BATCH",
    "B3-S004": "NEXT_MEASURED_BATCH",
    "B3-S007": "NEXT_MEASURED_BATCH",
    "B3-S013": "NEXT_MEASURED_BATCH",
    "B3-S021": "NEXT_MEASURED_BATCH",
    "B3-S024": "NEXT_PARALLEL_RINSE_CELL",
    "B3-S034": "NEW_FINAL_STATUS_PHASE",
    "B4-S005": "NEXT_PARALLEL_FILTER_BATH_CELL",
    "B4-S008": "NEXT_MEASURED_RINSE_CELL",
    "B4-S011": "NEW_MEASURED_VESSEL_BATCH",
    "B4-S014": "NEW_PREPARED_FLUID",
    "B4-S015": "NEW_MEASURED_CLARITY_BATCH",
}

EXACT_VORIGES_BINDINGS = {
    "H2-S002": "H2:I01",
    "B1-S002": "B1:I02",
}

TARGET_CUES = (
    "ZIEL?", "Stelle", "Becken", "Gefäß", "Gefaess", "Lauf", "Läufe",
    "Oeffnung", "Öffnung", "Ablauf", "Station", "Magenschmerz", "Brust",
    "Husten", "trinke", "bade", "tauche", "Pflaster", "Umschlag",
)

TARGET_RESET_CUES = (
    "nächsten becken", "zweite öffnung", "zweiten lauf", "erste öffnung",
    "oberen lauf", "unteren ablauf", "untere becken", "auffanggefäß",
    "verbundenen läufe",
)

PRIOR_ITEM_CUES = (
    "vorigen", "vorhandenen arbeitsstand", "vorlauf",
)

CURRENT_ITEM_PART_CUES = (
    "aus demselben ansatz", "daraus", "den rest", "rückstand", "übrig",
)

VALID_BOUNDARY_COUNTS = {
    "CONTINUE_SAME_CLAUSE": 19,
    "RESUME_ACTIVE_ITEM": 8,
    "NEXT_PARALLEL_CELL": 10,
    "START_NEW_CLAUSE": 8,
    "UNRESOLVED": 1,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def guarded_query(path: Path, columns: list[str]) -> tuple[list[dict[str, str]], dict]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in ALLOWED_PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{.*\})", result.stderr)
    if not match:
        raise RuntimeError(f"No guard statistics for {path}")
    rows = list(csv.DictReader(result.stdout.splitlines(), delimiter="\t"))
    return rows, json.loads(match.group(1))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def item_kind(record: str, skeleton: str, reading: str) -> str:
    if record.startswith("B"):
        return "WORKING_FLUID_BATCH_OR_CONTENTS"
    combined = f"{skeleton} {reading}".lower()
    if "ansatz?" in combined or any(word in combined for word in ("arznei", "flüssigkeit", "mischung", "auszug", "pflaster", "umschlag")):
        return "SIMPLEX_DERIVATIVE_OR_PREPARATION"
    if any(word in combined for word in ("wurzel", "blüte", "blatt", "samen", "simplex", "pflanze")):
        return "SIMPLEX_OR_PLANT_PART"
    return "SIMPLEX_OR_PREPARATION_UNRESOLVED"


def has_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def main() -> None:
    statements, statement_guard = guarded_query(V61_STATEMENTS, STATEMENT_COLUMNS)
    boundaries, boundary_guard = guarded_query(V61_BOUNDARIES, BOUNDARY_COLUMNS)
    records, record_guard = guarded_query(V61_RECORDS, RECORD_COLUMNS)
    deck = read_tsv(V60_DECK)
    selection_text = V61_SELECTION.read_text(encoding="utf-8")

    record_rank = {record: rank for rank, record in enumerate(RECORD_ORDER)}
    statements.sort(key=lambda row: (record_rank[row["record_unit_id"]], int(row["statement_ordinal_in_record"])))
    boundaries.sort(key=lambda row: (record_rank[row["record_unit_id"]], int(row["boundary_ordinal_in_record"])))
    records.sort(key=lambda row: record_rank[row["record_unit_id"]])
    record_by_id = {row["record_unit_id"]: row for row in records}

    selected_mnemonics = tuple(row["selected_short_mnemonic"] for row in deck)
    skeleton_mnemonics = {
        mnemonic
        for statement in statements
        for mnemonic in selected_mnemonics
        if mnemonic in statement["selected_short_card_skeleton"]
    }

    trace_rows: list[dict[str, object]] = []
    trace_by_id: dict[str, dict[str, object]] = {}
    state_by_record: dict[str, dict[str, object]] = {}

    for statement in statements:
        statement_id = statement["statement_id"]
        record = statement["record_unit_id"]
        first = record not in state_by_record
        if first:
            state_by_record[record] = {
                "owner": None,
                "active": None,
                "active_kind": None,
                "previous": None,
                "target": None,
                "item_counter": 0,
                "target_counter": 0,
            }
        state = state_by_record[record]
        owner_before = state["owner"] or "NONE"
        active_before = state["active"] or "NONE"
        active_kind_before = state["active_kind"] or "NONE"
        previous_before = state["previous"] or "NONE"
        target_before = state["target"] or "NONE"

        if first:
            state["owner"] = f"{record}:O01"
            owner_action = "INTRODUCE_FROM_PICTURE_OR_RECORD_HEADER"
        else:
            owner_action = "CARRY_RECORD_OWNER"

        reset_reason = ACTIVE_RESETS.get(statement_id, "NONE")
        if first:
            state["item_counter"] += 1
            state["active"] = f"{record}:I{state['item_counter']:02d}"
            active_action = "INTRODUCE_ACTIVE_ITEM"
        elif reset_reason != "NONE":
            state["previous"] = state["active"]
            state["item_counter"] += 1
            state["active"] = f"{record}:I{state['item_counter']:02d}"
            active_action = f"RESET_TO_NEW_ITEM:{reset_reason}"
        elif statement["entry_boundary_class"] == "RESUME_ACTIVE_ITEM":
            active_action = "RESUME_ACTIVE_ITEM"
        elif statement["entry_boundary_class"] == "UNRESOLVED":
            active_action = "AMBIGUOUS_CARRY_OR_RESET;DEFAULT_CARRY"
        elif statement["internal_cross_line_boundaries"] != "NONE":
            active_action = "CARRY_THROUGH_REFLOWED_STATEMENT"
        elif "ANSATZ?" in statement["selected_short_card_skeleton"]:
            active_action = "CARRY_AND_RECAST_AS_PREPARATION"
        else:
            active_action = "CARRY_ACTIVE_ITEM"
        state["active_kind"] = item_kind(record, statement["selected_short_card_skeleton"], statement["concrete_workshop_reading"])

        target_required = record.startswith("B") or has_any(
            f"{statement['selected_short_card_skeleton']} {statement['concrete_workshop_reading']}",
            TARGET_CUES,
        )
        target_reset_cue = has_any(statement["concrete_workshop_reading"], TARGET_RESET_CUES)
        if target_required and state["target"] is None:
            state["target_counter"] += 1
            state["target"] = f"{record}:T{state['target_counter']:02d}"
            target_action = "INTRODUCE_PICTURED_OR_LOCALLY_NAMED_TARGET"
        elif target_required and (
            target_reset_cue
            or statement["entry_boundary_class"] == "NEXT_PARALLEL_CELL"
        ):
            state["target_counter"] += 1
            state["target"] = f"{record}:T{state['target_counter']:02d}"
            target_action = "RESET_TO_NEW_TARGET_OR_STATION"
        elif target_required:
            target_action = "RESUME_OR_CARRY_TARGET"
        elif state["target"] is not None:
            target_action = "CARRY_TARGET_UNMENTIONED"
        else:
            target_action = "UNBOUND"

        exact_voriges_count = statement["selected_short_card_skeleton"].count("VORIGES?")
        local_prior_item_cue = has_any(statement["concrete_workshop_reading"], PRIOR_ITEM_CUES)
        local_current_item_part_cue = has_any(statement["concrete_workshop_reading"], CURRENT_ITEM_PART_CUES)
        previous_required = bool(
            exact_voriges_count
            or local_prior_item_cue
            or local_current_item_part_cue
            or statement["entry_boundary_class"] == "RESUME_ACTIVE_ITEM"
        )
        if exact_voriges_count:
            previous_binding = EXACT_VORIGES_BINDINGS[statement_id]
            state["previous"] = previous_binding
            previous_action = "BIND_EXACT_VORIGES_TO_ANONYMOUS_ANTECEDENT"
        elif statement["entry_boundary_class"] == "RESUME_ACTIVE_ITEM":
            previous_binding = active_before if active_before != "NONE" else str(state["active"])
            state["previous"] = previous_binding
            previous_action = "RESUME_ACTIVE_ITEM_AS_ANTECEDENT"
        elif local_prior_item_cue:
            if first and statement_id == "B6-S001":
                previous_binding = "B6:I00"
                previous_action = "INTRODUCE_PRE_RECORD_EXEMPLAR_ANTECEDENT"
            elif reset_reason != "NONE" and state["previous"] is not None:
                previous_binding = str(state["previous"])
                previous_action = "BIND_PRIOR_ACTIVE_ITEM_AFTER_RESET"
            else:
                previous_binding = active_before if active_before != "NONE" else str(state["active"])
                previous_action = "BIND_LOCAL_PRIOR_ITEM_ANAPHORA"
            state["previous"] = previous_binding
        elif local_current_item_part_cue:
            previous_binding = str(state["active"])
            state["previous"] = previous_binding
            previous_action = "BIND_CURRENT_ITEM_PART_OR_DERIVATIVE"
        else:
            previous_binding = "NONE"
            previous_action = "NONE"

        owner_after = str(state["owner"])
        active_after = str(state["active"])
        active_kind_after = str(state["active_kind"])
        previous_after = str(state["previous"]) if state["previous"] is not None else "NONE"
        target_after = str(state["target"]) if state["target"] is not None else "NONE"

        silent_markers = [
            f"[STILL:OWNER={owner_after};{'PICTURED_SIMPLEX' if record.startswith('H') else 'PICTURED_APPARATUS_OR_PATIENT_UNRESOLVED'}]",
            f"[STILL:ACTIVE={active_after};{active_kind_after}]",
        ]
        silent_slots = ["OWNER", "ACTIVE_ITEM"]
        if target_required:
            silent_markers.append(f"[STILL:TARGET={target_after};DESTINATION_BODY_SITE_OR_STATION_UNRESOLVED]")
            silent_slots.append("TARGET_OR_STATION")
        if previous_required:
            silent_markers.append(f"[STILL:PREVIOUS={previous_binding};ANTECEDENT_ID_ONLY]")
            silent_slots.append("PREVIOUS_ITEM")
        if exact_voriges_count:
            silent_markers.append(f"[EXACT:VORIGES?→{previous_binding};ANTECEDENT_TYPE_STILL_SILENT]")
        marked_clause = " ".join(silent_markers + [statement["concrete_workshop_reading"]])

        if record.startswith("H"):
            historical_mechanism = "Bildlemma hält den Simplex; recipe/item gliedert Handlungen; idem/de-eodem/praedictum dienen nur als historische Ellipsenvergleiche."
        else:
            historical_mechanism = "Bildzelle hält Apparat/Patient, Arbeitsflüssigkeit und Station; kurze Bade- oder Gefäßanweisung lässt wiederholte Argumente aus."

        row = {
            "statement_id": statement_id,
            "record_unit_id": record,
            "page": statement["page"],
            "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
            "constituent_loci": statement["constituent_loci"],
            "constituent_fields": statement["constituent_fields"],
            "physical_line_count": statement["physical_line_count"],
            "event_count": statement["event_count"],
            "entry_boundary_class": statement["entry_boundary_class"],
            "exit_boundary_class": statement["exit_boundary_class"],
            "internal_cross_line_boundaries": statement["internal_cross_line_boundaries"],
            "selected_short_card_skeleton_unchanged": statement["selected_short_card_skeleton"],
            "record_reset": "YES" if first else "NO",
            "owner_id_before": owner_before,
            "owner_action": owner_action,
            "owner_id_after": owner_after,
            "active_item_id_before": active_before,
            "active_item_kind_before": active_kind_before,
            "active_item_action": active_action,
            "active_item_reset_reason": reset_reason,
            "active_item_id_after": active_after,
            "active_item_kind_after": active_kind_after,
            "target_id_before": target_before,
            "target_required": "YES" if target_required else "NO",
            "target_action": target_action,
            "target_id_after": target_after,
            "previous_register_before": previous_before,
            "previous_required": "YES" if previous_required else "NO",
            "previous_action": previous_action,
            "previous_binding": previous_binding,
            "previous_register_after": previous_after,
            "exact_voriges_occurrences": exact_voriges_count,
            "exact_voriges_binding": previous_binding if exact_voriges_count else "NONE",
            "required_silent_argument_count": len(silent_slots),
            "required_silent_argument_slots": "|".join(silent_slots),
            "marked_german_source_clause": marked_clause,
            "concrete_workshop_reading_unchanged": statement["concrete_workshop_reading"],
            "historical_ellipsis_mechanism": historical_mechanism,
            "strongest_list_or_form_rival": statement["strongest_alternative"],
            "confidence": ".58" if exact_voriges_count else (".44" if previous_required else ".36"),
            "status": "ANONYMOUS_REFERENT_EDITORIAL_LAYER;NO_NEW_CARD_MEANING",
            "source_lineage": "V60_SELECTED_DECK+V61_SELECTED_116_STATEMENTS>V62_R2",
        }
        trace_rows.append(row)
        trace_by_id[statement_id] = row

    boundary_rows: list[dict[str, object]] = []
    for boundary in boundaries:
        source = trace_by_id[boundary["from_statement_id"]]
        target = trace_by_id[boundary["to_statement_id"]]
        same_statement = boundary["from_statement_id"] == boundary["to_statement_id"]
        classification = boundary["classification"]
        if same_statement:
            active_from = active_to = source["active_item_id_after"]
            target_from = target_to = source["target_id_after"]
        else:
            active_from = source["active_item_id_after"]
            active_to = target["active_item_id_after"]
            target_from = source["target_id_after"]
            target_to = target["target_id_after"]
        if classification == "CONTINUE_SAME_CLAUSE":
            carry_operation = "CARRY_SAME_CLAUSE"
        elif classification == "RESUME_ACTIVE_ITEM":
            carry_operation = "RESUME_IN_NEW_CLAUSE"
        elif classification == "NEXT_PARALLEL_CELL":
            carry_operation = "CARRY_OWNER_RESET_ITEM_AND_OR_TARGET"
        elif classification == "START_NEW_CLAUSE":
            carry_operation = "CARRY_OWNER_RESET_PROCESS_PHASE"
        else:
            carry_operation = "UNRESOLVED_CARRY_OR_RESET"

        boundary_skeleton = f"{boundary['from_last_field_selected_skeleton']} > {boundary['to_first_field_selected_skeleton']}"
        exact_voriges = boundary_skeleton.count("VORIGES?")
        if exact_voriges:
            voriges_target = str(target["exact_voriges_binding"])
        else:
            voriges_target = "NONE"
        f82_edge = boundary["boundary_id"] == "B2-LB02"
        boundary_rows.append({
            "boundary_id": boundary["boundary_id"],
            "record_unit_id": boundary["record_unit_id"],
            "page": boundary["page"],
            "boundary_ordinal_in_record": boundary["boundary_ordinal_in_record"],
            "from_locus": boundary["from_locus"],
            "to_locus": boundary["to_locus"],
            "from_field": boundary["from_last_field"],
            "to_field": boundary["to_first_field"],
            "classification_unchanged": classification,
            "from_statement_id": boundary["from_statement_id"],
            "to_statement_id": boundary["to_statement_id"],
            "same_statement": "YES" if same_statement else "NO",
            "carry_operation": carry_operation,
            "owner_id_from_to": f"{source['owner_id_after']}→{target['owner_id_after']}",
            "active_item_id_from_to": f"{active_from}→{active_to}",
            "target_id_from_to": f"{target_from}→{target_to}",
            "selected_short_skeleton": boundary_skeleton,
            "exact_voriges_occurrences": exact_voriges,
            "exact_voriges_binding": voriges_target,
            "f82_edge_copy": "YES" if f82_edge else "NO",
            "visible_edge_copy": "qokaiin→qokaiin" if f82_edge else "NONE",
            "edge_copy_mechanism": "ANTICIPATORY_COPY_OR_RESUMPTION;NO_CARD_GLOSS" if f82_edge else "NONE",
            "marked_boundary_reading": (
                f"[STILL:OWNER={target['owner_id_after']}] "
                f"[STILL:ACTIVE={active_to}] "
                f"{boundary['from_last_field_local_reading']} || {boundary['to_first_field_local_reading']}"
            ),
            "historical_mechanism": "idem/de eodem/praedictum oder wiederholter recipe-/item-Anfang sind nur Vergleichsmechanismen; keine Form wird damit gleichgesetzt.",
            "strongest_list_or_form_rival": boundary["strongest_alternative"],
            "confidence": ".70" if f82_edge else (".58" if exact_voriges else ".40"),
            "status": "REFERENT_CARRY_HYPOTHESIS;NO_NEW_CARD_MEANING",
            "source_lineage": "V61_SELECTED_46_BOUNDARIES+V62_R2_ANONYMOUS_REGISTERS",
        })

    traces_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    bounds_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in trace_rows:
        traces_by_record[str(row["record_unit_id"])].append(row)
    for row in boundary_rows:
        bounds_by_record[str(row["record_unit_id"])].append(row)

    record_rows: list[dict[str, object]] = []
    for record in RECORD_ORDER:
        source = record_by_id[record]
        traces = traces_by_record[record]
        record_boundaries = bounds_by_record[record]
        owner_ids = sorted({str(row["owner_id_after"]) for row in traces})
        item_ids = sorted({str(row["active_item_id_after"]) for row in traces})
        target_ids = sorted({str(row["target_id_after"]) for row in traces if row["target_id_after"] != "NONE"})
        silent_counts = Counter(
            slot
            for row in traces
            for slot in str(row["required_silent_argument_slots"]).split("|")
        )
        class_counts = Counter(str(row["classification_unchanged"]) for row in record_boundaries)
        marked_record = (
            f"[STILL:OWNER={owner_ids[0]}] "
            f"[STILL:ACTIVE_ITEMS={'|'.join(item_ids)}] "
            f"[STILL:TARGETS={'|'.join(target_ids) if target_ids else 'UNBOUND'}] "
            f"{source['complete_workshop_reading']}"
        )
        if record.startswith("H"):
            mechanism = "Bildbesitzer bleibt als Simplex-Rubrik aktiv; Teile, Ansätze und Verwendungen werden parataktisch eingeführt oder de-eodem-artig wieder aufgenommen."
        else:
            mechanism = "Bildbesitzer bleibt Apparat/Patient-unentschieden; Flüssigkeitscharge und Station werden über kurze Bade-/Gefäßzellen getragen oder zurückgesetzt."
        record_rows.append({
            "record_unit_id": record,
            "page": source["page"],
            "statements": len(traces),
            "line_boundaries": len(record_boundaries),
            "owner_ids": "|".join(owner_ids),
            "active_item_ids": "|".join(item_ids),
            "active_item_introductions": sum(str(row["active_item_action"]).startswith("INTRODUCE") for row in traces),
            "active_item_resets": sum(str(row["active_item_action"]).startswith("RESET") for row in traces),
            "active_item_resumptions": sum(row["active_item_action"] == "RESUME_ACTIVE_ITEM" for row in traces),
            "target_ids": "|".join(target_ids) if target_ids else "NONE",
            "target_introductions_or_resets": sum(row["target_action"] in {"INTRODUCE_PICTURED_OR_LOCALLY_NAMED_TARGET", "RESET_TO_NEW_TARGET_OR_STATION"} for row in traces),
            "previous_required_statements": sum(row["previous_required"] == "YES" for row in traces),
            "exact_voriges_occurrences": sum(int(row["exact_voriges_occurrences"]) for row in traces),
            "required_silent_argument_total": sum(int(row["required_silent_argument_count"]) for row in traces),
            "silent_argument_slot_counts": ";".join(f"{key}={silent_counts[key]}" for key in ("OWNER", "ACTIVE_ITEM", "TARGET_OR_STATION", "PREVIOUS_ITEM") if silent_counts[key]),
            "boundary_class_counts": ";".join(f"{key}={class_counts[key]}" for key in VALID_BOUNDARY_COUNTS if class_counts[key]),
            "f82_edge_copy_present": "YES" if record == "B2" else "NO",
            "marked_complete_record_reading": marked_record,
            "historical_ellipsis_mechanism": mechanism,
            "strongest_list_or_form_rival": source["strongest_nonmedical_alternative"],
            "strongest_counterevidence": source["inherited_record_contradiction"],
            "status": "RECORD_LOCAL_ANONYMOUS_REFERENT_MODEL;CREATIVE_NOT_TRANSLATION",
            "source_lineage": "V61_SELECTED_RECORD+STATEMENTS+BOUNDARIES>V62_R2",
        })

    trace_path = OUT / "V62_R2_116_STATEMENT_REFERENT_TRACE.tsv"
    boundary_path = OUT / "V62_R2_46_BOUNDARY_CARRY_AUDIT.tsv"
    record_path = OUT / "V62_R2_11_RECORD_REFERENT_REGISTERS.tsv"
    validation_path = OUT / "V62_R2_VALIDATION.json"
    write_tsv(trace_path, list(trace_rows[0]), trace_rows)
    write_tsv(boundary_path, list(boundary_rows[0]), boundary_rows)
    write_tsv(record_path, list(record_rows[0]), record_rows)

    boundary_counts = Counter(row["classification_unchanged"] for row in boundary_rows)
    total_silent = sum(int(row["required_silent_argument_count"]) for row in trace_rows)
    slot_counts = Counter(
        slot
        for row in trace_rows
        for slot in str(row["required_silent_argument_slots"]).split("|")
    )
    exact_voriges_rows = [row for row in trace_rows if int(row["exact_voriges_occurrences"]) > 0]
    owner_ids_global = {row["owner_id_after"] for row in trace_rows}
    active_ids_global = {row["active_item_id_after"] for row in trace_rows}
    target_ids_global = {row["target_id_after"] for row in trace_rows if row["target_id_after"] != "NONE"}

    assertions = {
        "selected_116_statements_preserved": len(trace_rows) == 116 and len({row["statement_id"] for row in trace_rows}) == 116,
        "selected_46_boundaries_preserved": len(boundary_rows) == 46 and boundary_counts == Counter(VALID_BOUNDARY_COUNTS),
        "selected_11_records_preserved": [row["record_unit_id"] for row in record_rows] == list(RECORD_ORDER),
        "v60_deck_has_11_cards": len(deck) == 11,
        "no_new_short_mnemonic": skeleton_mnemonics <= set(selected_mnemonics),
        "all_short_skeletons_unchanged": all(row["selected_short_card_skeleton_unchanged"] == next(source["selected_short_card_skeleton"] for source in statements if source["statement_id"] == row["statement_id"]) for row in trace_rows),
        "all_clauses_mark_owner_and_active": all("[STILL:OWNER=" in row["marked_german_source_clause"] and "[STILL:ACTIVE=" in row["marked_german_source_clause"] for row in trace_rows),
        "all_local_readings_unchanged": all(row["concrete_workshop_reading_unchanged"] == next(source["concrete_workshop_reading"] for source in statements if source["statement_id"] == row["statement_id"]) for row in trace_rows),
        "all_referent_ids_record_local": all(
            str(value).startswith(f"{row['record_unit_id']}:")
            for row in trace_rows
            for value in (
                row["owner_id_after"], row["active_item_id_after"],
                row["target_id_after"], row["previous_binding"],
            )
            if value != "NONE"
        ),
        "one_owner_per_record": len(owner_ids_global) == 11 and all(len({row["owner_id_after"] for row in traces_by_record[record]}) == 1 for record in RECORD_ORDER),
        "exact_voriges_two_bound_and_marked": len(exact_voriges_rows) == 2 and sum(int(row["exact_voriges_occurrences"]) for row in exact_voriges_rows) == 2 and all(row["exact_voriges_binding"] != "NONE" and "[EXACT:VORIGES?" in row["marked_german_source_clause"] for row in exact_voriges_rows),
        "f82_edge_copy_single_and_unglossed": sum(row["f82_edge_copy"] == "YES" for row in boundary_rows) == 1 and next(row for row in boundary_rows if row["f82_edge_copy"] == "YES")["boundary_id"] == "B2-LB02" and "NO_CARD_GLOSS" in next(row for row in boundary_rows if row["f82_edge_copy"] == "YES")["edge_copy_mechanism"],
        "selection_report_confirms_f82_edge_copy": "qokaiin" in selection_text and "f82r.3→f82r.4" in selection_text,
        "all_27_selected_carries_audited": boundary_counts["CONTINUE_SAME_CLAUSE"] + boundary_counts["RESUME_ACTIVE_ITEM"] == 27,
        "every_statement_quantifies_silent_arguments": all(2 <= int(row["required_silent_argument_count"]) <= 4 for row in trace_rows),
        "every_statement_has_list_or_form_rival": all(row["strongest_list_or_form_rival"] for row in trace_rows),
        "all_pages_allowlisted": all(row["page"] in ALLOWED_PAGES for row in statements + boundaries + records),
        "guarded_sources_have_no_forbidden_rows": all(stats["skipped_forbidden"] == 0 for stats in (statement_guard, boundary_guard, record_guard)),
    }

    validation = {
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "decision": "RECORD_LOCAL_OWNER_ACTIVE_ITEM_TARGET_AND_PREVIOUS_REGISTERS_ARE_PLAUSIBLE_BUT_EDITORIALLY_COSTLY",
        "scope": {
            "allowed_pages": list(ALLOWED_PAGES),
            "records": len(records),
            "source_statements": len(statements),
            "line_boundaries": len(boundaries),
            "selected_exact_cards": len(deck),
        },
        "counts": {
            "statement_trace_rows": len(trace_rows),
            "boundary_carry_rows": len(boundary_rows),
            "record_register_rows": len(record_rows),
            "selected_continue_or_resume_carries": boundary_counts["CONTINUE_SAME_CLAUSE"] + boundary_counts["RESUME_ACTIVE_ITEM"],
            "owner_introductions": sum(row["owner_action"] == "INTRODUCE_FROM_PICTURE_OR_RECORD_HEADER" for row in trace_rows),
            "owner_carries": sum(row["owner_action"] == "CARRY_RECORD_OWNER" for row in trace_rows),
            "active_item_introductions": sum(str(row["active_item_action"]).startswith("INTRODUCE") for row in trace_rows),
            "active_item_resets": sum(str(row["active_item_action"]).startswith("RESET") for row in trace_rows),
            "active_item_resumptions": sum(row["active_item_action"] == "RESUME_ACTIVE_ITEM" for row in trace_rows),
            "anonymous_owner_ids": len(owner_ids_global),
            "anonymous_active_item_ids": len(active_ids_global),
            "anonymous_target_ids": len(target_ids_global),
            "exact_voriges_occurrences": sum(int(row["exact_voriges_occurrences"]) for row in trace_rows),
            "f82_edge_copy_boundaries": sum(row["f82_edge_copy"] == "YES" for row in boundary_rows),
            "required_silent_argument_total": total_silent,
        },
        "silent_argument_slot_counts": {key: slot_counts[key] for key in ("OWNER", "ACTIVE_ITEM", "TARGET_OR_STATION", "PREVIOUS_ITEM")},
        "boundary_class_counts": {key: boundary_counts[key] for key in VALID_BOUNDARY_COUNTS},
        "assertions": assertions,
        "guards": {
            "statement_query": statement_guard,
            "boundary_query": boundary_guard,
            "record_query": record_guard,
            "forbidden_prefix": "f84",
            "f84_accessed": False,
            "f84r_accessed": False,
            "new_voynich_pages_opened": 0,
            "v62_sibling_files_read": 0,
            "sound_or_language_assignment": False,
            "page_host_or_substring_semantics": False,
        },
        "source_sha256": {
            "v60_selected_deck": sha256(V60_DECK),
            "v61_selection_report": sha256(V61_SELECTION),
            "v61_selected_statements": sha256(V61_STATEMENTS),
            "v61_selected_boundaries": sha256(V61_BOUNDARIES),
            "v61_selected_records": sha256(V61_RECORDS),
        },
        "output_sha256": {
            "statement_trace": sha256(trace_path),
            "boundary_carry_audit": sha256(boundary_path),
            "record_registers": sha256(record_path),
        },
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise AssertionError(json.dumps(assertions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
