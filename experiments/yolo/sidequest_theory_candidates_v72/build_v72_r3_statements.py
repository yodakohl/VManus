#!/usr/bin/env python3
"""Build V72 R3's 116 owner-bound technical source-class statements.

The output is a creative executable edition.  It preserves exact V69 event
order and V71 selected visible owners without assigning new card semantics.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STATEMENTS_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_116_STATEMENT_EDITION.tsv"
FIELDS_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
EVENTS_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
OWNER_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_SELECTED_OWNER_LEDGER.tsv"
OUT_TSV = HERE / "V72_R3_116_STATEMENTS.tsv"
REVISION_TSV = HERE / "V72_R3_REVISIONS.tsv"
REPORT_MD = HERE / "V72_R3_TECHNICAL_REPORT.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OWNER_LABELS = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "Ganzpflanzenartikel der f10r-Pflanze",
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": "Ganzpflanzenartikel der dichtkronigen f11r-Pflanze",
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": "Ganzpflanzenartikel der breitblättrigen f55v-Pflanze",
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": "Ganzpflanzenartikel der mehrköpfigen f56r-Pflanze",
    "B1_SHARED_TWO_ROW_POOL": "gemeinsamen zweireihigen f81v-Becken-/Figurenfeld",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "oberen f82r-Figuren-/Zylinderkonfiguration",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "mittleren linken f82r-Ring-/Inline-Knotenposten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "ungelösten mittleren f82r-Linie-/Podestposten",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "unteren grünen f82r-Mehrfigurenfeld",
    "B2_LOWER_POOL_EDGE_STATIONS": "lokalen Randstationen des unteren f82r-Feldes",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "obersten f83r-Randstation mit offenem Fächerende",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "mittleren f83r-Randstation im Rundgefäß",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "unteren f83r-Randstation im Korbgefäß",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "ungelösten f83r-Zwischenposten zwischen Randstapel und Hauptpaar",
    "B3_MAIN_ARCH_LINKED_PAIR": "unteren f83r-Paarstation am ungerichteten Bogen",
    "B4_MAIN_ARCH_LINKED_PAIR": "unteren f83r-Paarstation im Record B4",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linken f83r-Unterlauf mit offenen Fransen",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechten f83r-S-Lauf mit Mehrarmknoten",
    "B5_LEFT_OPEN_FRINGE_STATION": "linken offenen f83r-Endposten",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechten f83r-S-Lauf-/Mehrarm-Endposten",
}


def owner_label(owner: str) -> str:
    if owner not in OWNER_LABELS:
        raise KeyError(f"unmapped selected owner {owner}")
    return OWNER_LABELS[owner]


def constraint_for(owner: str) -> str:
    if owner.startswith("WHOLE_"):
        return "PAGE_OWNER_ONLY; NO_PART_FROM_PROXIMITY; NO_PICTURED_MEDIUM_OR_DIRECTION"
    if owner == "B1_SHARED_TWO_ROW_POOL":
        return "COMMON_BOUNDARY_ONLY; LEFT_CONTACT_UNDIRECTED; NO_ROW_ORDER_OR_GLOBAL_CIRCULATION"
    if owner == "B2_UPPER_PAIRED_BASINS_AND_CYLINDER":
        return "LOCAL_ARC_CYLINDER_CONTACTS_ONLY; NO_CONNECTION_TO_MIDDLE_OR_LOWER_STATIONS"
    if owner == "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE":
        return "LOCAL_HAND_DEVICE_AND_INLINE_NODE_ONLY; NO_DOWNSTREAM_FLOW"
    if owner == "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION":
        return "PROXIMITY_ONLY; LINE_DOES_NOT_SAFELY_CONTACT_PODEST; OWNER_UNRESOLVED"
    if owner == "B2_LOWER_GREEN_MULTI_FIGURE_POOL":
        return "LOWER_POOL_BOUNDARY_ONLY; NO_EDGE_FROM_UPPER_STATIONS; NO_FLOW_DIRECTION"
    if owner == "B2_LOWER_POOL_EDGE_STATIONS":
        return "LOCAL_EDGE_STATIONS_ONLY; NO_INTERSTATION_CONDUIT_OR_ORDER"
    if owner.startswith("B3_UPPER_") or owner.startswith("B3_MIDDLE_") or owner.startswith("B3_LOWER_"):
        return "ONE_MARGIN_STATION_ONLY; NO_EDGE_TO_OTHER_MARGIN_OR_MAIN_STATIONS"
    if owner == "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED":
        return "VISIBLE_GAP; NO_OWNER_INHERITANCE; SOURCE_OWNER_REQUIRES_EXEMPLAR"
    if "ARCH_LINKED_PAIR" in owner:
        return "VISIBLE_ARCH_CONTACT_BETWEEN_PAIR; NO_ARROW_SOURCE_SINK_OR_RETURN_CYCLE"
    if "LEFT_OPEN" in owner or "LEFT_OPEN_FRINGE" in owner:
        return "LEFT_LOCAL_RUN_ENDS_OPEN; NO_RETURN_OR_TRANSFER_TO_RIGHT_STATION"
    if "RIGHT_S_RUN" in owner:
        return "RIGHT_S_RUN_CONTACTS_MULTIPORT_NODE; ARMS_OPEN; NO_FLOW_DIRECTION"
    raise KeyError(owner)


def contradiction_for(owner: str) -> str:
    if owner.startswith("WHOLE_"):
        return "Das Bild weist kein Feld einem Pflanzenteil, Medium, Werkzeug oder Gebrauch zu; alle konkreten Arbeitswerte bleiben exemplarisch."
    if owner == "B1_SHARED_TWO_ROW_POOL":
        return "Die gemeinsame Umgrenzung zeigt weder Mischfolge noch Zielreihenfolge; ein Kreislauf wäre ergänzt."
    if owner == "B2_UPPER_PAIRED_BASINS_AND_CYLINDER":
        return "Bögen und Zylinder können ikonographische Bänder/Aufhängung sein; keine Kante führt zur nächsten Seitenstation."
    if owner == "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE":
        return "Ring, Wellen und Sternknoten können Strahl-/Schmuckmotive sein und enden lokal."
    if owner == "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION":
        return "Die horizontale Linie berührt das Liegepodest nicht sicher; ohne Exemplar ist selbst der örtliche Besitzer unentscheidbar."
    if owner == "B2_LOWER_GREEN_MULTI_FIGURE_POOL":
        return "Das Grünfeld besitzt keine gezeichnete Zuleitung aus den oberen Vignetten."
    if owner == "B2_LOWER_POOL_EDGE_STATIONS":
        return "Benachbarte Figurenplätze sind nicht durch Leitungen oder eine sichtbare Abfolge verbunden."
    if owner.startswith("B3_") and "GAP" in owner:
        return "Zwischen Randstapel und Hauptpaar fehlt eine Kante; jede Fortsetzung braucht einen neuen Exemplaranker."
    if owner.startswith("B3_") and "MARGIN" in owner:
        return "Die Randstation ist nicht sichtbar mit der nächsten Station verbunden; Reihenfolge bleibt bloße Seitenordnung."
    if "ARCH_LINKED_PAIR" in owner:
        return "Der Bogen koppelt die Figuren sichtbar, zeigt aber weder Medium noch Richtung oder zyklische Rückführung."
    if "LEFT_OPEN" in owner:
        return "Der linke Lauf endet offen; ein Übergang zum rechten Lauf ist nicht gezeichnet."
    if "RIGHT_S_RUN" in owner:
        return "Der Mehrarmknoten hat offene Arme; Ziel, Medium und Bewegungsrichtung fehlen."
    raise KeyError(owner)


def parse_state(text: str) -> dict[str, str]:
    state = {}
    for item in text.split(";"):
        key, value = item.split("=", 1)
        state[key] = value
    return state


def literal_event_atom(event: dict[str, str]) -> str:
    serial = int(event["event_serial"])
    tags = []
    if event["selected_exact_mnemonic"] != "UNKNOWN":
        tags.append(f"CARD={event['selected_exact_mnemonic']}")
    if event["strict_formal_prompt"] != "NONE":
        tags.append(f"FORMAL={event['strict_formal_prompt']}")
    if not tags:
        if event["event_template"] == "EXEMPLAR_ONLY":
            tags.append("EXEMPLAR_VALUE_UNKNOWN")
        else:
            tags.append(f"V69_CLASS={event['event_template']}")
            tags.append("EXACT_VALUE_UNKNOWN")
    return f"E{serial:03d}[{'|'.join(tags)}]"


def state_value(state: dict[str, str], key: str, fallback: str) -> str:
    value = state.get(key, "UNSET")
    return fallback if value == "UNSET" else value


def operation_phrases(statement: dict[str, str], section: str) -> list[str]:
    sid = statement["statement_id"]
    sequence = statement["licensed_primitive_sequence"]
    pre = parse_state(statement["pre_state"])
    post = parse_state(statement["post_state"])
    if sequence in {"NONE", ""}:
        target = state_value(post, "TARGET/STATION", f"{sid}:TARGET_UNSET")
        active = state_value(post, "ACTIVE_ITEM/PREPARATION", f"{sid}:ACTIVE_UNSET")
        return [
            f"kopiere den vollständigen typisierten Wert `EXEMPLAR_ENTRY_{sid}` aus dem Master",
            f"buche ihn recordlokal als ACTIVE `{active}` und gegebenenfalls Ziel `{target}`",
        ]
    primitives = sequence.split(" > ")
    phrases = []
    counters: Counter[str] = Counter()
    for primitive in primitives:
        counters[primitive] += 1
        i = counters[primitive]
        slot = f"{sid}:{primitive}_{i:02d}"
        if primitive == "PARAMETER_ASSIGN":
            kind = "Pflanzen-/Arbeitsmaß" if section == "HERBAL" else "Stationsmaß oder Dauer"
            phrases.append(f"trage den Masterwert `{slot}` als örtliches {kind} ein")
        elif primitive == "TARGET_ASSIGN":
            target = state_value(post, "TARGET/STATION", f"{sid}:TARGET")
            phrases.append(f"setze den lokalen Zielslot `{target}` aus `{slot}`")
        elif primitive == "LINK_ACTIVE":
            active = state_value(post, "ACTIVE_ITEM/PREPARATION", f"{sid}:ACTIVE")
            phrases.append(f"verknüpfe den laufenden Recordposten `{active}` mit dem örtlichen Arbeitsstand; keine Bildkante wird ergänzt")
        elif primitive == "SELECT_PREVIOUS":
            previous = state_value(post, "PREVIOUS_ITEM", f"{sid}:PREVIOUS")
            phrases.append(f"wähle ausschließlich den vorigen Posten `{previous}` desselben Records")
        elif primitive == "SELECT_PART":
            phrases.append(f"wähle den im Master bezeichneten Teilposten `{slot}` des sichtbaren Besitzers")
        elif primitive == "STATE_GATE":
            phrases.append(f"prüfe den im Master bezeichneten Freigabezustand `{slot}` und markiere erst danach den Posten bereit")
        elif primitive == "ACTION_APPLY":
            action = "Materialhandlung" if section == "HERBAL" else "Stationshandlung"
            phrases.append(f"führe die exemplarisch bestimmte örtliche {action} `{slot}` am aktuellen Besitzer aus")
        elif primitive == "ACTION_TEMPER":
            phrases.append(f"stelle den exemplarisch angegebenen örtlichen Zustands-/Temperaturwert `{slot}` ein")
        elif primitive == "TERMINAL_DRAIN":
            phrases.append(f"schließe den lokalen End-/Ablassposten `{slot}` ab; vererbe keinen Weiterfluss")
        elif primitive == "TERMINAL_FLUSH":
            phrases.append(f"schließe den lokalen Spül-/Endposten `{slot}` ab; erzeuge kein Folgeziel")
        else:
            raise ValueError(f"unknown primitive {primitive}")
    return phrases


def source_class(statement: dict[str, str]) -> str:
    seq = statement["licensed_primitive_sequence"]
    if seq == "NONE":
        return "TYPED_EXEMPLAR_ENTRY"
    if "TERMINAL_DRAIN" in seq or "TERMINAL_FLUSH" in seq:
        return "LOCAL_TERMINAL_OR_CLOSURE_ENTRY"
    if "STATE_GATE" in seq:
        return "LOCAL_STATE_RELEASE_ENTRY"
    if "ACTION_APPLY" in seq or "ACTION_TEMPER" in seq:
        return "LOCAL_ACTION_OR_CONDITION_ENTRY"
    if "TARGET_ASSIGN" in seq:
        return "LOCAL_TARGET_ASSIGNMENT_ENTRY"
    if "PARAMETER_ASSIGN" in seq:
        return "LOCAL_PARAMETER_BOOKING_ENTRY"
    if "LINK_ACTIVE" in seq:
        return "RECORD_LOCAL_LINK_ENTRY"
    return "COMPOSITE_REGISTER_ENTRY"


def strongest_rival(statement: dict[str, str], owners: list[str]) -> str:
    section = "HERBAL" if statement["record_unit_id"].startswith("H") else "BIOLOGICAL"
    if statement["parse_status"] == "UNPARSED" or any("UNRESOLVED" in owner for owner in owners):
        return "FORMAL_RIVAL: bloßer Exemplar-/Zellwert oder Bildlegende ohne rekonstruierbare Handlung."
    if section == "HERBAL":
        return "MEDICAL_RIVAL: derselbe unbekannte Ganzpflanzenartikel führt eine Heilzubereitung, Dosis oder Anwendung aus dem Masterexemplar."
    return "MEDICAL_RIVAL: lokale therapeutische Bade-, Wasch- oder Anwendungsanweisung an derselben sichtbaren Station."


def line_crossing(field_ids: list[str], field_by_id: dict[str, dict[str, str]]) -> tuple[bool, str]:
    loci = []
    for field_id in field_ids:
        locus = field_by_id[field_id]["locus"]
        if locus not in loci:
            loci.append(locus)
    if len(loci) == 1:
        return False, f"NO:{loci[0]}"
    return True, "YES:" + "→".join(loci) + "; CLAUSE_CONTINUES_ACROSS_PHYSICAL_LINES"


def repair_cost(statement: dict[str, str], owner_rows: list[dict[str, str]], crosses: bool) -> tuple[int, str]:
    cost = 0
    reasons = []
    parse = statement["parse_status"]
    if parse == "AMBIGUOUS":
        cost += 1
        reasons.append("mehrere formale Expansionen")
    elif parse == "UNPARSED":
        cost += 2
        reasons.append("vollständiger Quellenwert exemplar-only")
    else:
        reasons.append("formaler Kanal eindeutig")
    if crosses:
        cost += 1
        reasons.append("Aussage überschreitet physische Linie")
    if any(row["owner_status"] == "UNRESOLVED" for row in owner_rows):
        cost += 1
        reasons.append("mindestens ein Besitzer ungelöst")
    if len({row["selected_visible_owner"] for row in owner_rows}) > 1:
        cost += 1
        reasons.append("sichtbare Lücke erzwingt Ownerwechsel innerhalb der Aussage")
    cost = min(4, cost)
    if cost == 0:
        reasons.append("kein Layout- oder Ownerrepair")
    return cost, "; ".join(reasons)


def owner_binding(row: dict[str, str]) -> str:
    return f"{row['unit_id']}={row['owner_status']}:{row['selected_visible_owner']}"


def build_transition(
    statement: dict[str, str],
    owner_rows: list[dict[str, str]],
    previous_owner: str | None,
    is_last: bool,
) -> tuple[str, str | None]:
    actions = []
    current = previous_owner
    if int(statement["statement_ordinal_in_record"]) == 1:
        actions.append("RESET_RECORD")
        current = None
    for row in owner_rows:
        owner = row["selected_visible_owner"]
        status = row["owner_status"]
        field_id = row["unit_id"]
        if current is None:
            verb = {
                "PAGE_OWNER_ONLY": "SET_PAGE_OWNER",
                "DIRECT_VISIBLE": "SET_DIRECT_OWNER",
                "INHERITED_VISIBLE": "SET_INHERITED_OWNER",
                "UNRESOLVED": "SET_UNRESOLVED_OWNER",
            }[status]
        elif owner != current:
            actions.append("BREAK_VISIBLE_GAP")
            verb = "SET_UNRESOLVED_OWNER" if status == "UNRESOLVED" else ("SET_DIRECT_OWNER" if status == "DIRECT_VISIBLE" else "SET_LOCAL_OWNER")
        else:
            verb = {
                "PAGE_OWNER_ONLY": "REASSERT_PAGE_OWNER",
                "DIRECT_VISIBLE": "REASSERT_DIRECT_OWNER",
                "INHERITED_VISIBLE": "INHERIT_OWNER",
                "UNRESOLVED": "KEEP_UNRESOLVED_OWNER",
            }[status]
        actions.append(f"{verb}[{field_id}:{status}:{owner}]")
        current = owner
    if is_last:
        actions.append("RESET_AT_RECORD_END")
        current = None
    return " -> ".join(actions), current


def owner_constraint(owner_rows: list[dict[str, str]]) -> str:
    owners = []
    for row in owner_rows:
        owner = row["selected_visible_owner"]
        if owner not in owners:
            owners.append(owner)
    constraints = [constraint_for(owner) for owner in owners]
    if any(owner.startswith("B") for owner in owners):
        constraints.insert(0, "NO_DIRECTION_FROM_IMAGE")
    if len(owners) > 1:
        constraints.insert(0, "VISIBLE_GAP_REQUIRES_OWNER_RESET_WITHIN_STATEMENT")
    return " || ".join(constraints)


def row_contradiction(owner_rows: list[dict[str, str]]) -> str:
    owners = []
    for row in owner_rows:
        owner = row["selected_visible_owner"]
        if owner not in owners:
            owners.append(owner)
    pieces = [contradiction_for(owner) for owner in owners]
    if len(owners) > 1:
        pieces.insert(0, "Die Aussage kreuzt zwei sichtbare Besitzer; sie ist nur als zweigliedrige Klausel mit explizitem Reset ausführbar.")
    return " ".join(pieces)


def technical_paraphrase(statement: dict[str, str], owner_rows: list[dict[str, str]]) -> str:
    owners = []
    for row in owner_rows:
        owner = row["selected_visible_owner"]
        if owner not in owners:
            owners.append(owner)
    owner_text = " sowie nach lokalem Reset beim Besitzerposten ".join(f"„{owner_label(owner)}“" for owner in owners)
    section = "HERBAL" if statement["record_unit_id"].startswith("H") else "BIOLOGICAL"
    entry = "Eröffne" if int(statement["statement_ordinal_in_record"]) == 1 else "Fortschreibe"
    phrases = operation_phrases(statement, section)
    post = parse_state(statement["post_state"])
    register_tail = (
        f"Endstand nur in {statement['record_unit_id']}: ACTIVE `{post['ACTIVE_ITEM/PREPARATION']}`, "
        f"TARGET `{post['TARGET/STATION']}`, PREVIOUS `{post['PREVIOUS_ITEM']}`."
    )
    return f"{entry} Buchung `{statement['statement_id']}` beim Besitzerposten {owner_text}: " + "; ".join(phrases) + ". " + register_tail


def build() -> list[dict[str, object]]:
    statements = read_tsv(STATEMENTS_SOURCE)
    fields = read_tsv(FIELDS_SOURCE)
    events = read_tsv(EVENTS_SOURCE)
    selected = [row for row in read_tsv(OWNER_SOURCE) if row["unit_kind"] == "PROSE_FIELD"]
    assert len(statements) == 116
    assert len(fields) == 135
    assert len(events) == 381
    assert len(selected) == 135

    field_by_id = {row["field_id"]: row for row in fields}
    owner_by_field = {row["unit_id"]: row for row in selected}
    events_by_statement: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        events_by_statement.setdefault(event["statement_id"], []).append(event)
    statement_counts = Counter(row["record_unit_id"] for row in statements)
    previous_by_record: dict[str, str | None] = {}
    output = []

    for statement in statements:
        sid = statement["statement_id"]
        record = statement["record_unit_id"]
        field_ids = statement["constituent_fields"].split("|")
        owner_rows = [owner_by_field[field_id] for field_id in field_ids]
        owner_ids = []
        for row in owner_rows:
            if row["selected_visible_owner"] not in owner_ids:
                owner_ids.append(row["selected_visible_owner"])
        crosses, crossing_text = line_crossing(field_ids, field_by_id)
        is_last = int(statement["statement_ordinal_in_record"]) == statement_counts[record]
        transition, previous_by_record[record] = build_transition(
            statement, owner_rows, previous_by_record.get(record), is_last
        )
        cost, reason = repair_cost(statement, owner_rows, crosses)
        event_rows = events_by_statement[sid]
        literal_events = " > ".join(literal_event_atom(event) for event in event_rows)
        bindings = " > ".join(owner_binding(row) for row in owner_rows)
        literal_layer = f"OWNER[{bindings}] || {literal_events}"
        output.append({
            "statement_id": sid,
            "record_unit_id": record,
            "page": statement["page"],
            "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
            "constituent_fields": statement["constituent_fields"],
            "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "v69_primary_template": statement["primary_template"],
            "v69_primitive_sequence": statement["licensed_primitive_sequence"],
            "v69_parse_status": statement["parse_status"],
            "v71_field_owner_bindings": bindings,
            "exact_v71_owner_transition": transition,
            "literal_owner_known_card_exemplar_layer": literal_layer,
            "source_class": source_class(statement),
            "technical_source_class_paraphrase": technical_paraphrase(statement, owner_rows),
            "strongest_medical_or_formal_rival": strongest_rival(statement, owner_ids),
            "repair_cost_0_4": cost,
            "repair_reason": reason,
            "line_crossing": crossing_text,
            "contact_direction_constraint": owner_constraint(owner_rows),
            "hardest_contradiction": row_contradiction(owner_rows),
            "v69_pre_state": statement["pre_state"],
            "v69_post_state": statement["post_state"],
            "semantic_ceiling": "CREATIVE_SOURCE_CLASS_NOT_WORD_CARD_STEM_SOUND_OR_TRANSLATION",
        })
    return output


REVISIONS = [
    ("V72R3-01", "ALL_11_RECORDS", "OWNER could remain implicit across a page", "reset OWNER at every H/B record", "prevents H1→H2 and B3→B4 carry", "0"),
    ("V72R3-02", "HERBAL_19_STATEMENTS", "field proximity could select root/leaf/flower", "all Herbal clauses carry only the selected whole-plant page owner", "part, medium and use become typed exemplar values", "1"),
    ("V72R3-03", "H5-S001", "line boundary could split the action", "one clause crosses F014→F015 under one whole-plant owner", "preserves event order across f56r.5→.7", "2"),
    ("V72R3-04", "B1_21_STATEMENTS", "shared pool was a seven-stage circuit", "all entries are local bookings at one shared field", "no row order, flow or return", "2"),
    ("V72R3-05", "B2-S004_B2-S005", "f82r.2→.4 implied travel", "line crossing stays inside the upper local configuration only", "no owner transfer to middle/lower stations", "2"),
    ("V72R3-06", "B2-S012", "line/podest and lower pool formed one operation", "UNRESOLVED F058 then BREAK then DIRECT F059", "two-clause source reconstruction; no invisible conduit", "4"),
    ("V72R3-07", "B2-S013_B2-S022", "lower entries inherited upper machine state", "lower pool and edge stations receive fresh local owners", "terminal words remain local", "2"),
    ("V72R3-08", "B3-S016", "lower margin station carried into gap", "F086 owner then explicit BREAK to unresolved F087", "no implicit main-station continuation", "4"),
    ("V72R3-09", "B3-S026", "gap and main pair formed one state gate", "F098 unresolved then BREAK to direct F099 pair", "state value comes from exemplar, not connection", "4"),
    ("V72R3-10", "B4-S015", "left and right lower runs formed a directed drain", "F125 left owner then BREAK to F126 right owner", "two local ends; no flow direction", "3"),
    ("V72R3-11", "B5_VS_B6", "both addenda shared a return line", "B5 stays left open fringe; B6 stays right S-run node", "record reset blocks cross-end inheritance", "2"),
    ("V72R3-12", "TERMINAL_DRAIN_FLUSH", "terminal class named a visible water movement", "terminal class closes only the current local entry", "no downstream owner or medium inferred", "1"),
    ("V72R3-13", "KNOWN_CARDS", "mnemonic was read as plaintext", "question-mark card handles remain literal-layer annotations", "paraphrase uses typed source-class slots", "1"),
    ("V72R3-14", "EXEMPLAR_ONLY", "unknown events were smoothed into fluent prose", "every unknown event is printed as E### EXAMPLAR_VALUE_UNKNOWN", "no event silently skipped", "2"),
    ("V72R3-15", "PHYSICAL_LINES", "line end equalled clause end", "line crossing is computed from constituent field loci", "statement identity remains V69-bound", "0"),
]


def write_revisions() -> None:
    columns = ["revision_id", "scope", "old_default", "v72_r3_revision", "executable_effect", "nominal_repair_cost"]
    write_tsv(REVISION_TSV, [dict(zip(columns, row)) for row in REVISIONS], columns)


RECORD_TITLES = {
    "H1": "f10r erster Ganzpflanzenartikel",
    "H2": "f10r zweiter Ganzpflanzenartikel",
    "H3": "f11r Ganzpflanzenartikel",
    "H4": "f55v Ganzpflanzenartikel",
    "H5": "f56r Ganzpflanzenartikel",
    "B1": "f81v gemeinsames zweireihiges Beckenfeld",
    "B2": "f82r lokaler Stationsatlas",
    "B3": "f83r Randstationen, Lücke und Hauptpaar",
    "B4": "f83r Hauptpaar mit getrennten Unterläufen",
    "B5": "f83r linker offener Endposten",
    "B6": "f83r rechter S-Lauf-/Mehrarm-Endposten",
}


def make_report(rows: list[dict[str, object]]) -> str:
    records: OrderedDict[str, list[dict[str, object]]] = OrderedDict()
    for row in rows:
        records.setdefault(str(row["record_unit_id"]), []).append(row)
    costs = Counter(int(row["repair_cost_0_4"]) for row in rows)
    crossing_count = sum(str(row["line_crossing"]).startswith("YES:") for row in rows)
    multi_owner = sum("BREAK_VISIBLE_GAP" in str(row["exact_v71_owner_transition"]) for row in rows)
    lines = [
        "# V72 R3 — 116 ausführbare Quellenklassen unter sichtbaren Besitzern",
        "",
        "Status: kreative technische Arbeitsedition, keine Entzifferung oder Übersetzung.",
        "",
        "## Ergebnis",
        "",
        f"Alle **{len(rows)} Aussagen** der elf Prosa-Records sind vollständig gebunden.",
        "Sie bewahren 135 Felder und 381 Ereignisse. Jede Ereignisnummer erscheint",
        "in genau einer Literalspur; unbekannte Werte bleiben ausdrücklich",
        "`EXEMPLAR_VALUE_UNKNOWN`.",
        "",
        f"Physische Linien werden in {crossing_count} Aussagen überschritten. {multi_owner}",
        "Aussagen enthalten mindestens einen expliziten sichtbaren Ownerwechsel.",
        "",
        "| Reparaturkosten | Aussagen |",
        "|---:|---:|",
    ]
    for cost in range(5):
        lines.append(f"| {cost} | {costs[cost]} |")
    lines += [
        "",
        "## Compilerregel",
        "",
        "1. Recordbeginn löscht `OWNER`, `ACTIVE`, `TARGET` und `PREVIOUS`.",
        "2. V71 setzt den kleinsten ausgewählten sichtbaren Besitzer; Herbal bleibt bewusst Ganzpflanzenartikel.",
        "3. Jede Aussage kopiert ihre exakten V69-Ereignisse in Reihenfolge. Nur gefrorene Fragezeichen-Mnemonics und Formalprompts werden angezeigt.",
        "4. `EXEMPLAR_VALUE_UNKNOWN` wird als typisierter Quellenwert kopiert, niemals aus Kartenbestandteilen errechnet.",
        "5. Eine physische Zeile darf innerhalb derselben Aussage überschritten werden.",
        "6. Ein sichtbarer Spalt erzeugt `BREAK_VISIBLE_GAP`, selbst innerhalb einer V69-Aussage.",
        "7. Bio-Bögen und Läufe geben ohne Pfeil keine Richtung; Terminalklassen schließen nur die lokale Buchung.",
        "8. Recordende löscht alle vier Register; B5 darf B6 nicht beliefern.",
        "",
        "## Die elf vollständigen Records",
    ]
    for record, record_rows in records.items():
        owners = []
        for row in record_rows:
            for binding in str(row["v71_field_owner_bindings"]).split(" > "):
                owner = binding.split(":", 1)[1]
                if owner not in owners:
                    owners.append(owner)
        lines += [
            "",
            f"### {record} — {RECORD_TITLES[record]}",
            "",
            f"Aussagen: {len(record_rows)}; Ereignisse: {sum(int(r['event_count']) for r in record_rows)}; lokale Besitzerfolge: " + " → ".join(f"`{owner}`" for owner in owners) + ".",
            "",
            "| Aussage | Felder/Ereignisse | Ownerübergang | konkrete technische Quellenklasse | Rival | Kosten | Linie |",
            "|---|---|---|---|---|---:|---|",
        ]
        for row in record_rows:
            field_cell = str(row["constituent_fields"]).replace("|", "\\|")
            event_cell = str(row["event_serials"]).replace("|", "\\|")
            lines.append(
                f"| {row['statement_id']} | {field_cell} / {event_cell} | "
                f"{row['exact_v71_owner_transition']} | {row['technical_source_class_paraphrase']} | "
                f"{row['strongest_medical_or_formal_rival']} | {row['repair_cost_0_4']} | {row['line_crossing']} |"
            )
    lines += [
        "",
        "## Härteste Reparaturen",
        "",
        "- `B2-S012`: F058 bleibt an Linie/Podest ungelöst; vor F059 wird innerhalb der Aussage zurückgesetzt.",
        "- `B3-S016`: der untere Randstationsbesitzer endet vor F087 in der bildlichen Lücke.",
        "- `B3-S026`: F098 gehört noch zur ungelösten Lücke; F099 setzt erst danach die sichtbare Hauptpaarstation.",
        "- `B4-S015`: F125 und F126 liegen an verschiedenen unteren Endposten; der alte gerichtete Ablauf wird zweigliedrig.",
        "",
        "## Interpretation",
        "",
        "Die Edition zeigt, wie eine Werkstatt konkrete Quellklassen mit Bildellipse",
        "und Masterexemplar notieren könnte. Sie bestimmt weder die konkreten Masterwerte",
        "noch die historische Domäne. Medizinische Bade-/Herbalprosa und eine rein formale",
        "Bildlegende bleiben die stärksten Rivalen. Bestätigte Lexeme und Klartextklauseln",
        "bleiben null. f84 und f84r blieben versiegelt.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = build()
    columns = [
        "statement_id", "record_unit_id", "page", "statement_ordinal_in_record",
        "constituent_fields", "event_count", "event_serials", "v69_primary_template",
        "v69_primitive_sequence", "v69_parse_status", "v71_field_owner_bindings",
        "exact_v71_owner_transition", "literal_owner_known_card_exemplar_layer",
        "source_class", "technical_source_class_paraphrase",
        "strongest_medical_or_formal_rival", "repair_cost_0_4", "repair_reason",
        "line_crossing", "contact_direction_constraint", "hardest_contradiction",
        "v69_pre_state", "v69_post_state", "semantic_ceiling",
    ]
    assert len(rows) == 116
    assert sum(int(row["event_count"]) for row in rows) == 381
    write_tsv(OUT_TSV, rows, columns)
    write_revisions()
    REPORT_MD.write_text(make_report(rows), encoding="utf-8")
    summary = {
        "status": "BUILT",
        "statements": len(rows),
        "records": dict(Counter(str(row["record_unit_id"]) for row in rows)),
        "fields": sum(len(str(row["constituent_fields"]).split("|")) for row in rows),
        "events": sum(int(row["event_count"]) for row in rows),
        "repair_cost_counts": dict(sorted(Counter(str(row["repair_cost_0_4"]) for row in rows).items())),
        "line_crossing_statements": sum(str(row["line_crossing"]).startswith("YES:") for row in rows),
        "owner_break_statements": sum("BREAK_VISIBLE_GAP" in str(row["exact_v71_owner_transition"]) for row in rows),
        "semantic_ceiling": "CREATIVE_SOURCE_CLASS_NOT_WORD_CARD_STEM_SOUND_OR_TRANSLATION",
        "sealed": ["f84", "f84r"],
    }
    (HERE / "V72_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
