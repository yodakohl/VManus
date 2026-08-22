#!/usr/bin/env python3
"""Build a deterministic four-register machine over the 116 V61 statements."""

from __future__ import annotations

import csv
import itertools
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V61 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v61"

SOURCE_VALUES = V60 / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
SOURCE_STATEMENTS = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_BOUNDARIES = V61 / "V61_SELECTED_46_LINE_BOUNDARIES.tsv"

OUT_TRANSITIONS = HERE / "V62_R3_116_STATE_TRANSITIONS.tsv"
OUT_INVENTORY = HERE / "V62_R3_REGISTER_INVENTORY.tsv"
OUT_ERRORS = HERE / "V62_R3_IRREDUCIBLE_ERROR_AUDIT.tsv"
OUT_MODELS = HERE / "V62_R3_REDUCED_REGISTER_MODELS.tsv"

REGISTERS = ("OWNER", "ACTIVE_ITEM/PREPARATION", "TARGET/STATION", "PREVIOUS_ITEM")
OPERATIONS = {"INTRODUCE", "CARRY", "RESUME", "RESET"}
NEW_ITEM_BOUNDARIES = {"NEXT_PARALLEL_CELL", "START_NEW_CLAUSE"}
ACTIVE_RESUME_BOUNDARIES = {"RESUME_ACTIVE_ITEM"}
ACTIVE_CARRY_BOUNDARIES = {"WITHIN_LOCUS_FIELD_BOUNDARY", "UNRESOLVED"}
ACTIVE_EXACT = {"ANSATZ?", "ANTEIL?"}
TARGET_SENSITIVE_EXACT = {"ANWENDEN?", "SPÜLEN?", "ABLASSEN?", "ZIEL?"}

# These are record-local fillers already printed in the selected V61 creative
# readings.  They can populate an anonymous register but never become a card
# value.  Specific phrases precede generic phrases.
TARGET_CUE_PATTERNS = (
    ("FIRST_OPENING", ("erste öffnung", "ersten öffnung")),
    ("SECOND_OPENING", ("zweite öffnung", "zweiten öffnung")),
    ("LOWER_BASIN", ("untere becken", "unteren becken")),
    ("LOWER_OUTLET", ("untere ablauf", "unteren ablauf")),
    ("UPPER_RUN", ("oberen lauf", "obere lauf")),
    ("CONNECTED_RUNS", ("verbundenen läufe", "verbundene läufe")),
    ("BROAD_VESSEL", ("breite gefäß", "breiten gefäß")),
    ("COVERED_CATCH_VESSEL", ("bedeckten auffanggefäß", "bedeckte auffanggefäß")),
    ("VESSEL_OR_RUN", ("gefäß oder den lauf", "gefäß oder lauf")),
    ("CLOTH", ("durch ein tuch", "durch tuch")),
    ("MARKED_TARGET", ("bezeichnete zielstelle", "bezeichneten zielstelle", "markierten stelle", "bezeichnete stelle", "bezeichneten stelle", "örtlich bezeichneten stelle", "örtlich bezeichnete stelle", "betroffene stelle", "wunde stelle", "geschwollene stelle")),
    ("PERSON_AT_BASIN", ("person an das becken",)),
    ("SHADOW_PLACE", ("im schatten", "schattigen waldort", "schattiger heide")),
)

PREVIOUS_CUE_PATTERNS = (
    ("PREVIOUS_PREPARATION", ("vorigen zubereitung", "vorige zubereitung")),
    ("PREVIOUS_BATCH", ("vorigen ansatz", "vorige ansatz")),
    ("PREVIOUS_MIXTURE", ("vorigen mischung", "vorige mischung")),
    ("RETURNING_STREAM", ("zurücklaufenden strom", "zurücklaufende strom")),
    ("REMAINDER", ("den rest", "der rest", "übrige wurzel", "übrigen material", "rückstand")),
    ("RETAINED_PART", ("behalte die", "bewahre die")),
    ("TWO_SHARES", ("beide anteile", "beiden anteile")),
    ("SAME_SETTING", ("derselben einstellung", "gleiche einstellung", "derselben einstellung")),
    ("SAME_DURATION", ("dieselbe dauer", "gleichen dauer")),
)

PRIOR_HISTORY_CUES = {"PREVIOUS_PREPARATION", "PREVIOUS_BATCH", "PREVIOUS_MIXTURE", "RETURNING_STREAM", "SAME_SETTING", "SAME_DURATION"}
CURRENT_DERIVATION_CUES = {"REMAINDER", "RETAINED_PART", "TWO_SHARES"}

ISSUE_META = {
    "UNRESOLVED_BOUNDARY": ("HIGH", "V61 leaves this boundary unresolved.", "Carry all four registers deterministically and retain the unresolved flag.", "Reset or resume the active item instead.", "YES", "YES"),
    "PREVIOUS_SLOT_OVERWRITTEN": ("MEDIUM", "A new active item replaces an already occupied depth-one previous slot.", "Keep only the immediately displaced active item.", "Use an unbounded history stack.", "NO", "YES"),
    "TARGET_RESET_DISCARDS_PRIOR_TARGET": ("LOW", "A new or parallel clause resets an occupied target register.", "Treat the reset as intentional station scoping.", "Carry the prior station across the clause boundary.", "NO", "YES"),
    "TARGET_INTRODUCTION_OVERWRITES_PRIOR_TARGET": ("LOW", "A newly observed local target replaces a carried target.", "Keep the most recently introduced target.", "Retain a target stack or multi-target frame.", "NO", "YES"),
    "INFERRED_PREVIOUS_IDENTITY": ("HIGH", "A previous-item cue occurs before a uniquely stored previous item is available.", "Introduce one anonymous record-local previous item.", "Leave the reading unresolved or import a deeper history.", "YES", "YES"),
    "PREVIOUS_REFERENT_CLASS_AMBIGUOUS": ("HIGH", "The cue does not choose uniquely among prior item, preparation, run, remainder or setting.", "Use the depth-one PREVIOUS_ITEM register.", "Split PREVIOUS_ITEM into typed history registers.", "YES", "YES"),
    "MULTIPLE_TARGETS_ONE_SLOT": ("HIGH", "More than one local target/station cue occurs in one statement.", "Execute them in reading order and retain the final anonymous target.", "Use multiple simultaneous target slots.", "YES", "YES"),
    "REPEATED_ACTIVE_TRIGGER": ("MEDIUM", "The same statement contains repeated active-preparation or portion triggers.", "Treat later repetitions as confirmations of the current anonymous item.", "Introduce a distinct item for every repetition.", "YES", "YES"),
    "TWO_INPUTS_ORDER_AMBIGUOUS": ("HIGH", "The reading combines two shares but does not encode which is ACTIVE and which is PREVIOUS.", "Keep the current item active and the other in PREVIOUS_ITEM.", "Swap the two registers; the visible result is unchanged.", "YES", "YES"),
    "TARGET_INFERRED_WITHOUT_EXACT_OR_LOCAL_CUE": ("HIGH", "A target-sensitive operation has no exact ZIEL? and no concrete local target cue.", "Introduce one anonymous target/station from record context.", "Treat the operation as intransitive or owner-targeted.", "YES", "YES"),
    "OPEN_RECORD_END": ("MEDIUM", "The selected statement exits the record with an OPEN field.", "Keep the post-state available only inside the closed record audit; do not carry it to the next record.", "Infer an unmarked final commit.", "YES", "NO"),
}


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


def mnemonic_tokens(skeleton: str) -> list[str]:
    return re.findall(r"[A-ZÄÖÜ]+\?", skeleton)


def local_cues(text: str, patterns: tuple[tuple[str, tuple[str, ...]], ...]) -> list[str]:
    lowered = text.casefold()
    hits: list[tuple[int, str]] = []
    for label, aliases in patterns:
        positions = [lowered.find(alias.casefold()) for alias in aliases]
        positions = [position for position in positions if position >= 0]
        if positions:
            hits.append((min(positions), label))
    return [label for _, label in sorted(hits)]


def state_text(state: dict[str, str]) -> str:
    return ";".join(f"{register}={state[register]}" for register in REGISTERS)


def add_issue(issues: list[str], code: str) -> None:
    if code not in issues:
        issues.append(code)


def main() -> None:
    values = read_tsv(SOURCE_VALUES)
    statements = read_tsv(SOURCE_STATEMENTS)
    boundaries = read_tsv(SOURCE_BOUNDARIES)
    require((len(values), len(statements), len(boundaries)) == (11, 116, 46), "selected source counts changed")
    allowed_mnemonics = {row["selected_short_mnemonic"] for row in values}
    require(len(allowed_mnemonics) == 11, "V60 selected mnemonics must be unique")
    require(all(row["binding"] == "EXACT_JOINT_TUPLE_ID_ONLY" for row in values), "V60 binding changed")

    statement_ids = {row["statement_id"] for row in statements}
    require(len(statement_ids) == 116, "statement IDs not unique")
    for boundary in boundaries:
        require(boundary["from_statement_id"] in statement_ids and boundary["to_statement_id"] in statement_ids, f"boundary statement missing: {boundary['boundary_id']}")
        if boundary["cross_line_statement_id"] != "NONE":
            require(boundary["cross_line_statement_id"] in statement_ids, f"cross-line statement missing: {boundary['boundary_id']}")

    boundary_by_statement: dict[str, list[str]] = defaultdict(list)
    for boundary in boundaries:
        for role, key in (("FROM", "from_statement_id"), ("TO", "to_statement_id"), ("INTERNAL", "cross_line_statement_id")):
            statement_id = boundary[key]
            if statement_id != "NONE":
                boundary_by_statement[statement_id].append(f"{role}:{boundary['boundary_id']}:{boundary['classification']}")

    transition_rows: list[dict[str, str]] = []
    issue_rows: list[dict[str, str]] = []
    silent_demands_by_statement: dict[str, set[str]] = {}
    operation_counts: dict[str, Counter[str]] = {register: Counter() for register in REGISTERS}
    current_record = ""
    state = {register: "UNSET" for register in REGISTERS}
    owner_counter = item_counter = target_counter = 0

    def new_owner(record: str) -> str:
        nonlocal owner_counter
        owner_counter += 1
        return f"{record}:O{owner_counter:02d}"

    def new_item(record: str) -> str:
        nonlocal item_counter
        item_counter += 1
        return f"{record}:I{item_counter:03d}"

    def new_target(record: str) -> str:
        nonlocal target_counter
        target_counter += 1
        return f"{record}:T{target_counter:03d}"

    for serial, source in enumerate(statements, start=1):
        record = source["record_unit_id"]
        if record != current_record:
            current_record = record
            state = {register: "UNSET" for register in REGISTERS}
            owner_counter = item_counter = target_counter = 0
        pre = dict(state)
        entry = source["entry_boundary_class"]
        triggers = [f"BOUNDARY:{entry}"]
        exact = mnemonic_tokens(source["selected_short_card_skeleton"])
        require(set(exact) <= allowed_mnemonics, f"unselected mnemonic in {source['statement_id']}")
        triggers.extend(f"EXACT_SELECTED:{token}" for token in exact)
        triggers.append(f"CLOSURE:{source['closure_sequence']}")
        target_cues = local_cues(source["concrete_workshop_reading"], TARGET_CUE_PATTERNS)
        previous_cues = local_cues(source["concrete_workshop_reading"], PREVIOUS_CUE_PATTERNS)
        triggers.extend(f"LOCAL_TARGET_FILLER:{cue}" for cue in target_cues)
        triggers.extend(f"LOCAL_PREVIOUS_CUE:{cue}" for cue in previous_cues)
        if boundary_by_statement[source["statement_id"]]:
            triggers.extend(f"SOURCE_{value}" for value in boundary_by_statement[source["statement_id"]])

        ops = {register: "CARRY" for register in REGISTERS}
        trace: list[str] = []
        issues: list[str] = []
        backward_losses: list[str] = []

        # Structural transition before the exact selected mnemonic triggers.
        if entry == "RECORD_START":
            state["OWNER"] = new_owner(record)
            state["ACTIVE_ITEM/PREPARATION"] = new_item(record)
            state["TARGET/STATION"] = "UNSET"
            state["PREVIOUS_ITEM"] = "UNSET"
            ops.update({"OWNER": "INTRODUCE", "ACTIVE_ITEM/PREPARATION": "INTRODUCE", "TARGET/STATION": "RESET", "PREVIOUS_ITEM": "RESET"})
            trace.extend((f"OWNER:INTRODUCE({state['OWNER']})", f"ACTIVE_ITEM/PREPARATION:INTRODUCE({state['ACTIVE_ITEM/PREPARATION']})", "TARGET/STATION:RESET", "PREVIOUS_ITEM:RESET"))
        else:
            require(state["OWNER"] != "UNSET", f"owner absent after record start: {source['statement_id']}")
            trace.append(f"OWNER:CARRY({state['OWNER']})")
            if entry in NEW_ITEM_BOUNDARIES:
                if state["PREVIOUS_ITEM"] != "UNSET":
                    add_issue(issues, "PREVIOUS_SLOT_OVERWRITTEN")
                    backward_losses.append("PREVIOUS_SLOT_OVERWRITTEN")
                state["PREVIOUS_ITEM"] = state["ACTIVE_ITEM/PREPARATION"]
                ops["PREVIOUS_ITEM"] = "INTRODUCE"
                trace.append(f"PREVIOUS_ITEM:INTRODUCE_FROM_ACTIVE({state['PREVIOUS_ITEM']})")
                state["ACTIVE_ITEM/PREPARATION"] = new_item(record)
                ops["ACTIVE_ITEM/PREPARATION"] = "INTRODUCE"
                trace.append(f"ACTIVE_ITEM/PREPARATION:INTRODUCE({state['ACTIVE_ITEM/PREPARATION']})")
                if state["TARGET/STATION"] != "UNSET":
                    add_issue(issues, "TARGET_RESET_DISCARDS_PRIOR_TARGET")
                    backward_losses.append("TARGET_RESET_DISCARDS_PRIOR_TARGET")
                state["TARGET/STATION"] = "UNSET"
                ops["TARGET/STATION"] = "RESET"
                trace.append("TARGET/STATION:RESET(NEW_OR_PARALLEL_CLAUSE)")
            elif entry in ACTIVE_RESUME_BOUNDARIES:
                ops["ACTIVE_ITEM/PREPARATION"] = "RESUME"
                trace.append(f"ACTIVE_ITEM/PREPARATION:RESUME({state['ACTIVE_ITEM/PREPARATION']})")
                trace.append(f"TARGET/STATION:CARRY({state['TARGET/STATION']})")
                trace.append(f"PREVIOUS_ITEM:CARRY({state['PREVIOUS_ITEM']})")
            elif entry in ACTIVE_CARRY_BOUNDARIES:
                trace.append(f"ACTIVE_ITEM/PREPARATION:CARRY({state['ACTIVE_ITEM/PREPARATION']})")
                trace.append(f"TARGET/STATION:CARRY({state['TARGET/STATION']})")
                trace.append(f"PREVIOUS_ITEM:CARRY({state['PREVIOUS_ITEM']})")
                if entry == "UNRESOLVED":
                    add_issue(issues, "UNRESOLVED_BOUNDARY")
            else:
                raise ValueError(f"unsupported entry boundary {entry}: {source['statement_id']}")

        # Exact selected active-item triggers.  ANSATZ? resumes or confirms the
        # current preparation; ANTEIL? derives a new current item unless the
        # structural boundary has already introduced it.
        active_trigger_count = sum(token in ACTIVE_EXACT for token in exact)
        if active_trigger_count > 1:
            add_issue(issues, "REPEATED_ACTIVE_TRIGGER")
        for token in exact:
            if token == "ANSATZ?":
                if state["ACTIVE_ITEM/PREPARATION"] == "UNSET":
                    state["ACTIVE_ITEM/PREPARATION"] = new_item(record)
                    ops["ACTIVE_ITEM/PREPARATION"] = "INTRODUCE"
                    trace.append(f"ACTIVE_ITEM/PREPARATION:INTRODUCE({state['ACTIVE_ITEM/PREPARATION']};ANSATZ?)")
                else:
                    if ops["ACTIVE_ITEM/PREPARATION"] == "CARRY":
                        ops["ACTIVE_ITEM/PREPARATION"] = "RESUME"
                    trace.append(f"ACTIVE_ITEM/PREPARATION:RESUME_OR_CONFIRM({state['ACTIVE_ITEM/PREPARATION']};ANSATZ?)")
            elif token == "ANTEIL?":
                if ops["ACTIVE_ITEM/PREPARATION"] == "INTRODUCE":
                    trace.append(f"ACTIVE_ITEM/PREPARATION:CONFIRM_INTRODUCED({state['ACTIVE_ITEM/PREPARATION']};ANTEIL?)")
                else:
                    if state["PREVIOUS_ITEM"] != "UNSET":
                        add_issue(issues, "PREVIOUS_SLOT_OVERWRITTEN")
                        backward_losses.append("PREVIOUS_SLOT_OVERWRITTEN")
                    state["PREVIOUS_ITEM"] = state["ACTIVE_ITEM/PREPARATION"]
                    ops["PREVIOUS_ITEM"] = "INTRODUCE"
                    trace.append(f"PREVIOUS_ITEM:INTRODUCE_FROM_ACTIVE({state['PREVIOUS_ITEM']};ANTEIL?)")
                    state["ACTIVE_ITEM/PREPARATION"] = new_item(record)
                    ops["ACTIVE_ITEM/PREPARATION"] = "INTRODUCE"
                    trace.append(f"ACTIVE_ITEM/PREPARATION:INTRODUCE({state['ACTIVE_ITEM/PREPARATION']};ANTEIL?)")
            elif token == "VORIGES?":
                if state["PREVIOUS_ITEM"] == "UNSET":
                    state["PREVIOUS_ITEM"] = new_item(record)
                    add_issue(issues, "INFERRED_PREVIOUS_IDENTITY")
                    trace.append(f"PREVIOUS_ITEM:INTRODUCE_INFERRED({state['PREVIOUS_ITEM']};VORIGES?)")
                old_active = state["ACTIVE_ITEM/PREPARATION"]
                state["ACTIVE_ITEM/PREPARATION"] = state["PREVIOUS_ITEM"]
                state["PREVIOUS_ITEM"] = old_active
                ops["ACTIVE_ITEM/PREPARATION"] = "RESUME"
                ops["PREVIOUS_ITEM"] = "RESUME"
                trace.append(f"ACTIVE_ITEM/PREPARATION:RESUME_FROM_PREVIOUS({state['ACTIVE_ITEM/PREPARATION']};VORIGES?)")

        # A true backward cue queries the depth-one history.  A remainder,
        # retained part or two-share construction instead creates a current
        # derived item; it must not fabricate a pre-record history.
        history_cues = [cue for cue in previous_cues if cue in PRIOR_HISTORY_CUES]
        derivation_cues = [cue for cue in previous_cues if cue in CURRENT_DERIVATION_CUES]
        if history_cues or "VORIGES?" in exact:
            add_issue(issues, "PREVIOUS_REFERENT_CLASS_AMBIGUOUS")
            if state["PREVIOUS_ITEM"] == "UNSET":
                state["PREVIOUS_ITEM"] = new_item(record)
                ops["PREVIOUS_ITEM"] = "INTRODUCE"
                add_issue(issues, "INFERRED_PREVIOUS_IDENTITY")
                trace.append(f"PREVIOUS_ITEM:INTRODUCE_INFERRED({state['PREVIOUS_ITEM']};LOCAL_FILLER)")
            elif ops["PREVIOUS_ITEM"] == "CARRY":
                ops["PREVIOUS_ITEM"] = "RESUME"
                trace.append(f"PREVIOUS_ITEM:RESUME({state['PREVIOUS_ITEM']};LOCAL_FILLER)")
        if derivation_cues:
            if "TWO_SHARES" in derivation_cues:
                add_issue(issues, "TWO_INPUTS_ORDER_AMBIGUOUS")
            if state["PREVIOUS_ITEM"] == "UNSET":
                state["PREVIOUS_ITEM"] = new_item(record)
                ops["PREVIOUS_ITEM"] = "INTRODUCE"
                trace.append(f"PREVIOUS_ITEM:INTRODUCE_DERIVED({state['PREVIOUS_ITEM']};LOCAL_{derivation_cues[0]})")

        # Current local target fillers are executed in printed order.  A single
        # target register deliberately retains only the final one.
        if len(target_cues) > 1:
            add_issue(issues, "MULTIPLE_TARGETS_ONE_SLOT")
        for cue in target_cues:
            if state["TARGET/STATION"] != "UNSET":
                add_issue(issues, "TARGET_INTRODUCTION_OVERWRITES_PRIOR_TARGET")
                backward_losses.append("TARGET_INTRODUCTION_OVERWRITES_PRIOR_TARGET")
            state["TARGET/STATION"] = new_target(record)
            ops["TARGET/STATION"] = "INTRODUCE"
            trace.append(f"TARGET/STATION:INTRODUCE({state['TARGET/STATION']};LOCAL_{cue})")

        if "ZIEL?" in exact and not target_cues:
            if state["TARGET/STATION"] == "UNSET":
                state["TARGET/STATION"] = new_target(record)
                ops["TARGET/STATION"] = "INTRODUCE"
                trace.append(f"TARGET/STATION:INTRODUCE({state['TARGET/STATION']};ZIEL?_ANONYMOUS_FILLER)")
            else:
                if ops["TARGET/STATION"] == "CARRY":
                    ops["TARGET/STATION"] = "RESUME"
                trace.append(f"TARGET/STATION:RESUME({state['TARGET/STATION']};ZIEL?)")

        target_sensitive = bool(set(exact) & TARGET_SENSITIVE_EXACT)
        if target_sensitive and not target_cues and "ZIEL?" not in exact:
            if state["TARGET/STATION"] == "UNSET":
                state["TARGET/STATION"] = new_target(record)
                ops["TARGET/STATION"] = "INTRODUCE"
                add_issue(issues, "TARGET_INFERRED_WITHOUT_EXACT_OR_LOCAL_CUE")
                trace.append(f"TARGET/STATION:INTRODUCE_INFERRED({state['TARGET/STATION']};TARGET_SENSITIVE_ACTION)")
            else:
                if ops["TARGET/STATION"] == "CARRY":
                    ops["TARGET/STATION"] = "RESUME"
                trace.append(f"TARGET/STATION:RESUME({state['TARGET/STATION']};TARGET_SENSITIVE_ACTION)")

        if source["exit_boundary_class"] == "RECORD_END" and source["closure_sequence"].split(" > ")[-1].endswith(":OPEN"):
            add_issue(issues, "OPEN_RECORD_END")

        # Missing slots distinguish absent exact-card role marking from local
        # filler. Silent demand is narrower: it records values that must persist
        # from prior state rather than being introduced by this statement.
        missing_slots: list[str] = []
        if entry != "RECORD_START":
            missing_slots.append("OWNER")
        if not set(exact) & ACTIVE_EXACT:
            missing_slots.append("ACTIVE_ITEM/PREPARATION")
        if target_sensitive and "ZIEL?" not in exact:
            missing_slots.append("TARGET/STATION")
        if history_cues or "VORIGES?" in exact:
            missing_slots.append("PREVIOUS_ITEM")

        silent_demand: set[str] = set()
        if entry != "RECORD_START":
            silent_demand.add("OWNER")
        if entry in ACTIVE_RESUME_BOUNDARIES | ACTIVE_CARRY_BOUNDARIES and not set(exact) & ACTIVE_EXACT:
            silent_demand.add("ACTIVE_ITEM/PREPARATION")
        if target_sensitive and not target_cues and "ZIEL?" not in exact:
            silent_demand.add("TARGET/STATION")
        if history_cues or "VORIGES?" in exact:
            silent_demand.add("PREVIOUS_ITEM")
        silent_demands_by_statement[source["statement_id"]] = silent_demand

        backward_losses.extend(code for code in issues if ISSUE_META[code][5] == "YES")
        backward_losses = list(dict.fromkeys(backward_losses))
        post_only = "NO" if backward_losses else "YES"
        post = dict(state)
        require(all(operation in OPERATIONS for operation in ops.values()), f"bad operation: {source['statement_id']}")
        for register, operation in ops.items():
            operation_counts[register][operation] += 1

        transition_rows.append(
            {
                "transition_serial": str(serial),
                "statement_id": source["statement_id"],
                "record_unit_id": record,
                "page": source["page"],
                "statement_ordinal_in_record": source["statement_ordinal_in_record"],
                "constituent_fields": source["constituent_fields"],
                "entry_boundary_class": entry,
                "exit_boundary_class": source["exit_boundary_class"],
                "pre_state": state_text(pre),
                "selected_mnemonic_triggers": " | ".join(exact) if exact else "NONE",
                "observed_triggers": " | ".join(triggers),
                "inferred_missing_slots": " | ".join(missing_slots) if missing_slots else "NONE",
                "silent_register_demand": " | ".join(register for register in REGISTERS if register in silent_demand) if silent_demand else "NONE",
                "owner_operation": ops["OWNER"],
                "active_item_preparation_operation": ops["ACTIVE_ITEM/PREPARATION"],
                "target_station_operation": ops["TARGET/STATION"],
                "previous_item_operation": ops["PREVIOUS_ITEM"],
                "operation_trace": " -> ".join(trace),
                "post_state": state_text(post),
                "backward_reconstructable_from_post_state_only": post_only,
                "backward_reconstructability": "TRANSITION_LOG=YES;POST_STATE_ONLY=" + post_only + (":" + "|".join(backward_losses) if backward_losses else ":ANONYMOUS_BUT_DETERMINISTIC"),
                "irreducible_ambiguity_codes": " | ".join(issues) if issues else "NONE",
                "complete_creative_reading": source["concrete_workshop_reading"],
                "strongest_source_alternative": source["strongest_alternative"],
                "source_boundary_triggers": " | ".join(boundary_by_statement[source["statement_id"]]) if boundary_by_statement[source["statement_id"]] else "NONE",
                "anonymous_id_contract": f"{record}:Oxx/{record}:Ixxx/{record}:Txxx;RECORD_LOCAL_ONLY",
                "card_binding_contract": "V60_SELECTED_EXACT_MNEMONICS_ONLY;NO_STRING_OR_COMPONENT_INHERITANCE;LOCAL_FILLER_IS_NOT_CARD_MEANING",
                "source_lineage": "V60_SELECTED_VALUES>V61_SELECTED_STATEMENTS+BOUNDARIES>V62_R3_FOUR_REGISTER_MACHINE",
            }
        )

        for code in issues:
            severity, description, resolution, alternative, irreducible, impacts_backward = ISSUE_META[code]
            issue_rows.append(
                {
                    "error_serial": str(len(issue_rows) + 1),
                    "error_id": f"ERR{len(issue_rows) + 1:03d}",
                    "statement_id": source["statement_id"],
                    "record_unit_id": record,
                    "severity": severity,
                    "error_code": code,
                    "evidence": description + " Trigger=" + (" | ".join(triggers)),
                    "four_register_resolution": resolution,
                    "strongest_alternative": alternative,
                    "irreducible_with_four_registers": irreducible,
                    "impacts_post_state_backward_reconstruction": impacts_backward,
                    "source_lineage": "V61_SELECTED_STATEMENT>V62_R3_ERROR_AUDIT",
                }
            )

    require(len(transition_rows) == 116, "transition count must be 116")
    require(issue_rows, "error audit must not be empty")

    # Exhaustive strongest subsets make the 0/1/2-register comparison paid and
    # reproducible instead of selecting a convenient rival by hand.
    model_rows: list[dict[str, str]] = []
    for size in (0, 1, 2, 3, 4):
        candidates = list(itertools.combinations(REGISTERS, size))
        scored = []
        for subset_tuple in candidates:
            subset = set(subset_tuple)
            covered = [statement_id for statement_id, demand in silent_demands_by_statement.items() if demand <= subset]
            failures = [statement_id for statement_id, demand in silent_demands_by_statement.items() if not demand <= subset]
            missing_instances = sum(len(demand - subset) for demand in silent_demands_by_statement.values())
            scored.append((len(covered), -missing_instances, tuple(subset_tuple), covered, failures, missing_instances))
        best = max(scored, key=lambda item: (item[0], item[1], tuple(-REGISTERS.index(x) for x in item[2])))
        covered_count, _, subset_tuple, covered, failures, missing_instances = best
        model_rows.append(
            {
                "register_count": str(size),
                "model_name": {0: "NO_PERSISTENT_STATE", 1: "STRONGEST_ONE_REGISTER", 2: "STRONGEST_TWO_REGISTER", 3: "STRONGEST_THREE_REGISTER", 4: "FULL_FOUR_REGISTER_MACHINE"}[size],
                "kept_registers": " | ".join(subset_tuple) if subset_tuple else "NONE",
                "statements_fully_generable": str(covered_count),
                "statements_failing": str(len(failures)),
                "statement_coverage": f"{covered_count / len(statements):.6f}",
                "missing_silent_slot_instances": str(missing_instances),
                "first_failure_witnesses": " | ".join(failures[:12]) if failures else "NONE",
                "selection_rule": "EXHAUSTIVE_ALL_REGISTER_SUBSETS;MAX_STATEMENTS_THEN_MIN_MISSING_SLOT_INSTANCES",
                "verdict": "SUFFICIENT_FOR_ALL_116_CREATIVE_READINGS" if not failures else "INSUFFICIENT_FOR_COMPLETE_CREATIVE_READING",
                "source_lineage": "V62_R3_SILENT_REGISTER_DEMAND>EXHAUSTIVE_SUBSET_COMPARISON",
            }
        )

    inventory_rows: list[dict[str, str]] = []
    exact_trigger_map = {
        "OWNER": "NONE;VISIBLE_RECORD_OWNER_AT_RECORD_START",
        "ACTIVE_ITEM/PREPARATION": "ANSATZ?|ANTEIL?",
        "TARGET/STATION": "ZIEL?",
        "PREVIOUS_ITEM": "VORIGES?",
    }
    patterns = {
        "OWNER": "<RECORD>:O01",
        "ACTIVE_ITEM/PREPARATION": "<RECORD>:I001...",
        "TARGET/STATION": "<RECORD>:T001...",
        "PREVIOUS_ITEM": "pointer to <RECORD>:Ixxx",
    }
    introduce_rules = {
        "OWNER": "RECORD_START or visible owner",
        "ACTIVE_ITEM/PREPARATION": "RECORD_START; NEXT_PARALLEL_CELL; START_NEW_CLAUSE; ANTEIL?",
        "TARGET/STATION": "ZIEL? or record-local target filler or required anonymous target",
        "PREVIOUS_ITEM": "displaced ACTIVE_ITEM or inferred prior-item filler",
    }
    resume_rules = {
        "OWNER": "not applicable; CARRY inside record",
        "ACTIVE_ITEM/PREPARATION": "RESUME_ACTIVE_ITEM; ANSATZ?; VORIGES?",
        "TARGET/STATION": "target-sensitive operation without new target filler",
        "PREVIOUS_ITEM": "VORIGES? or local prior-item cue",
    }
    reset_rules = {
        "OWNER": "record boundary only",
        "ACTIVE_ITEM/PREPARATION": "record boundary only; otherwise replaced by INTRODUCE",
        "TARGET/STATION": "RECORD_START; NEXT_PARALLEL_CELL; START_NEW_CLAUSE",
        "PREVIOUS_ITEM": "record boundary only; depth-one overwrite on new active item",
    }
    for register in REGISTERS:
        witnesses = [statement_id for statement_id, demand in silent_demands_by_statement.items() if register in demand]
        inventory_rows.append(
            {
                "register": register,
                "anonymous_record_local_value_pattern": patterns[register],
                "initial_state": "UNSET",
                "introduce_rule": introduce_rules[register],
                "carry_rule": "CARRY only inside the same record; never across record boundary",
                "resume_rule": resume_rules[register],
                "reset_rule": reset_rules[register],
                "licensed_v60_exact_trigger": exact_trigger_map[register],
                "operation_counts": ";".join(f"{operation}={operation_counts[register][operation]}" for operation in ("INTRODUCE", "CARRY", "RESUME", "RESET")),
                "silent_demand_statement_count": str(len(witnesses)),
                "necessity_witnesses": " | ".join(witnesses[:12]) if witnesses else "NONE",
                "loss_if_removed": f"{len(witnesses)} statements lose a persistent {register} value",
                "historical_execution": "one marginal or mental current-entry slot; rewrite anonymous value only when INTRODUCE/RESET fires",
                "semantic_status": "CREATIVE_REGISTER_VALUE_NOT_DECRYPTION;EXACT_CARD_ROLE_NEVER_EXTENDED",
            }
        )

    write_tsv(OUT_TRANSITIONS, transition_rows)
    write_tsv(OUT_INVENTORY, inventory_rows)
    write_tsv(OUT_ERRORS, issue_rows)
    write_tsv(OUT_MODELS, model_rows)
    print("PASS build")
    print(f"transitions={len(transition_rows)} registers={len(inventory_rows)} errors={len(issue_rows)} models={len(model_rows)}")
    print("models=" + ";".join(f"{row['register_count']}:{row['statements_fully_generable']}/116:{row['kept_registers']}" for row in model_rows))


if __name__ == "__main__":
    main()
