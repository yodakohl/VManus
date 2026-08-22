#!/usr/bin/env python3
"""Build the blinded R2 V63 slot-grammar audit from selected V60--V62 files.

All page-bearing inputs are materialised through ``vmanus-exp query-tsv`` with
seven repeated exact page allow-values and an explicit f84-prefix veto.
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v63"
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")

EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"

EVENT_COLUMNS = (
    "event_serial,page,record_unit_id,field_id,formal_formula_opaque,FORMAL_VALUE,"
    "terminal_status,strict_control_prompt,ATOMIC_OR_WHOLE_CARD_MNEMONIC,mnemonic_scope"
)
STATEMENT_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,constituent_fields,"
    "event_count,event_serials,closure_sequence,entry_boundary_class,exit_boundary_class,"
    "selected_short_card_skeleton,status"
)
TRANSITION_COLUMNS = (
    "transition_serial,statement_id,record_unit_id,page,pre_state,selected_mnemonic_triggers,"
    "observed_triggers,inferred_missing_slots,silent_register_demand,operation_trace,post_state,"
    "backward_reconstructability,irreducible_ambiguity_codes,source_lineage"
)


TEMPLATES = [
    {
        "template_id": "T1_MEASUREMENT",
        "source_function": "Mess-/Parametereintrag",
        "licensed_anchors": "K:MASS? | K:ANTEIL? | F:VORGABEPARAMETER?",
        "slot_order": "OWNER(context) > ACTIVE > PARAMETER[LOCAL_EXEMPLAR]",
        "historical_source_frame": "Von [STILL:ACTIVE] den bezeichneten Anteil nach [STILL:PARAMETER] nehmen.",
        "historical_mechanism": "Rezept- oder Vorratszeile: Gegenstand wird geführt, Einheit und Zahl stehen im lokalen Exemplar.",
        "counter_parse": "Parameter-/Losspalte ohne Mengensyntax.",
        "hard_constraint": "Bezeichnet weder Einheit noch Stoff; mehrere Parameter brauchen getrennte lokale Füller.",
    },
    {
        "template_id": "T2_DESTINATION",
        "source_function": "Ziel-/Stationszuweisung",
        "licensed_anchors": "K:ZIEL? | F:LOKALEN_RELATIONSSLOT_SETZEN",
        "slot_order": "OWNER(context) > ACTIVE > TARGET",
        "historical_source_frame": "[STILL:ACTIVE] an [STILL:TARGET] führen.",
        "historical_mechanism": "Knappes Arbeitsregister lässt Zielstelle, Gefäßstation oder Bildadresse aus dem Exemplar ergänzen.",
        "counter_parse": "Reine Diagrammadresse oder Layoutrelation statt Quellenargument.",
        "hard_constraint": "TARGET bleibt anonyme recordlokale ID; kein Körperteil, Gefäß oder Ort wird aus der Karte gewonnen.",
    },
    {
        "template_id": "T3_BATCH_REFERENCE",
        "source_function": "laufender Ansatz / Rückgriff",
        "licensed_anchors": "K:ANSATZ? | K:VORIGES? | F:STANDARDSLOT_SETZEN | F:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN",
        "slot_order": "OWNER(context) > PREVIOUS(optional) > ACTIVE",
        "historical_source_frame": "[STILL:PREVIOUS] wieder aufnehmen beziehungsweise [STILL:ACTIVE] als laufenden Ansatz halten.",
        "historical_mechanism": "Werkstattliste trägt einen laufenden Posten weiter; Mechanismen wie derselbe/vorige Posten erklären Ellipse, nicht die Voynich-Lautung.",
        "counter_parse": "Kopier-, Status- oder Formularzeiger ohne sprachlichen Rückverweis.",
        "hard_constraint": "Kein Referent wird lexikalisch identifiziert; PREVIOUS ist nur depth-one und kann ambig sein.",
    },
    {
        "template_id": "T4_STATE_GATE",
        "source_function": "Bereitschafts-/Klarheitsbedingung",
        "licensed_anchors": "K:BEREIT? | K:KLAR?",
        "slot_order": "OWNER(context) > ACTIVE > STATE > CRITERION[LOCAL_EXEMPLAR]",
        "historical_source_frame": "[STILL:ACTIVE] stehen lassen, bis [STILL:CRITERION] den bezeichneten Zustand erfüllt.",
        "historical_mechanism": "Rezeptartige Endpunktbedingung; sichtbare Karte liefert nur den kurzen Zustand, nicht Dauer oder Prüfverfahren.",
        "counter_parse": "Zustandsklasse, Prüfhaken oder Bildlabel statt temporaler Nebenklausel.",
        "hard_constraint": "BEREIT?/KLAR? liefern weder Zeit, Temperatur noch Flüssigkeit.",
    },
    {
        "template_id": "T5_APPLY",
        "source_function": "Anwendung",
        "licensed_anchors": "K:ANWENDEN?",
        "slot_order": "OWNER(context) > ACTIVE > TARGET[register/local exemplar]",
        "historical_source_frame": "[STILL:ACTIVE] an [STILL:TARGET] anwenden.",
        "historical_mechanism": "Knappes Gebrauchsschema trägt Mittel und Ziel aus Bild, Überschrift oder laufendem Register nach.",
        "counter_parse": "Neutraler Operationscode oder Weitergabe statt medizinischer Anwendung.",
        "hard_constraint": "Kein Mittel, Patient oder Indikationswort steckt in der Karte.",
    },
    {
        "template_id": "T6_TEMPER",
        "source_function": "Temperieren",
        "licensed_anchors": "K:TEMPERIEREN?",
        "slot_order": "OWNER(context) > ACTIVE > DEGREE_OR_DURATION[LOCAL_EXEMPLAR]",
        "historical_source_frame": "[STILL:ACTIVE] nach [STILL:DEGREE_OR_DURATION] temperieren.",
        "historical_mechanism": "Werkstattanweisung mit lokal ergänztem Grad beziehungsweise Zeitraum.",
        "counter_parse": "Technisches Konditionieren, Färberbad oder bloße Prozessphase.",
        "hard_constraint": "Die Karte liefert weder warm noch kalt, Grad noch Dauer.",
    },
    {
        "template_id": "T7_RINSE",
        "source_function": "Spülen / terminaler Durchgang",
        "licensed_anchors": "K:SPÜLEN?",
        "slot_order": "OWNER(context) > ACTIVE > TARGET > FORMAL_CLOSE",
        "historical_source_frame": "[STILL:TARGET] mit [STILL:ACTIVE] spülen; den Durchgang formal schließen.",
        "historical_mechanism": "Kurze Arbeitszelle kann Spülung als eigenen abgeschlossenen Durchgang buchen.",
        "counter_parse": "Apparaturreinigung oder anonymer Schlussschritt A statt medizinischer Spülung.",
        "hard_constraint": "Medizinischer Körpergebrauch ist nicht kartengestützt; CLOSE bleibt stumm.",
    },
    {
        "template_id": "T8_DRAIN",
        "source_function": "Ablassen / terminaler Durchgang",
        "licensed_anchors": "K:ABLASSEN?",
        "slot_order": "OWNER(context) > ACTIVE > TARGET > FORMAL_CLOSE",
        "historical_source_frame": "[STILL:ACTIVE] nach [STILL:TARGET] ablassen; den Durchgang formal schließen.",
        "historical_mechanism": "Kurze Prozesszelle trennt Ablasshandlung vom vorausgehenden Ansatz.",
        "counter_parse": "Wasserwerkablauf oder anonymer Schlussschritt B statt medizinischem Ablassen.",
        "hard_constraint": "Richtung, Gefäß und Stoff bleiben Register-/Exemplarwerte; CLOSE bleibt stumm.",
    },
]

MNEMONIC_TO_TEMPLATE = {
    "MASS?": "T1_MEASUREMENT",
    "ANTEIL?": "T1_MEASUREMENT",
    "ZIEL?": "T2_DESTINATION",
    "ANSATZ?": "T3_BATCH_REFERENCE",
    "VORIGES?": "T3_BATCH_REFERENCE",
    "BEREIT?": "T4_STATE_GATE",
    "KLAR?": "T4_STATE_GATE",
    "ANWENDEN?": "T5_APPLY",
    "TEMPERIEREN?": "T6_TEMPER",
    "SPÜLEN?": "T7_RINSE",
    "ABLASSEN?": "T8_DRAIN",
}

FORMAL_TO_TEMPLATE = {
    "VORGABEPARAMETER?": "T1_MEASUREMENT",
    "LOKALEN_RELATIONSSLOT_SETZEN": "T2_DESTINATION",
    "STANDARDSLOT_SETZEN": "T3_BATCH_REFERENCE",
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": "T3_BATCH_REFERENCE",
}

RANK = {
    "T3_BATCH_REFERENCE": 10,
    "T1_MEASUREMENT": 20,
    "T6_TEMPER": 30,
    "T4_STATE_GATE": 40,
    "T2_DESTINATION": 50,
    "T5_APPLY": 60,
    "T7_RINSE": 70,
    "T8_DRAIN": 70,
}


def guarded_rows(path: Path, columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", columns, "--forbid-prefix", "f84"])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    payload = "\n".join(
        line for line in completed.stdout.splitlines() if line and not line.startswith("GUARD_STATS ")
    )
    return list(csv.DictReader(io.StringIO(payload), delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() != "NONE"]


def parse_state(value: str) -> dict[str, str]:
    state: dict[str, str] = {}
    for assignment in value.split(";"):
        key, _, val = assignment.partition("=")
        if key:
            state[key] = val or "UNSET"
    return state


def register_value(post: dict[str, str], pre: dict[str, str], name: str, fallback: str) -> str:
    for state in (post, pre):
        value = state.get(name, "UNSET")
        if value and value != "UNSET":
            return value
    return fallback


def group_consecutive(anchors: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    groups: list[list[dict[str, str]]] = []
    for anchor in anchors:
        if not groups or groups[-1][0]["template"] != anchor["template"]:
            groups.append([anchor])
        else:
            groups[-1].append(anchor)
    return groups


def anchor_label(group: list[dict[str, str]]) -> str:
    labels: list[str] = []
    for anchor in group:
        parts = []
        if anchor["formal"] != "NONE":
            parts.append("F:" + anchor["formal"])
        if anchor["mnemonic"] != "UNKNOWN":
            parts.append("K:" + anchor["mnemonic"])
        labels.append(f"e{anchor['event_serial']}:" + "+".join(parts))
    return " | ".join(labels)


def source_clause(
    groups: list[list[dict[str, str]]], pre: dict[str, str], post: dict[str, str], closure: str
) -> str:
    owner = register_value(post, pre, "OWNER", "LOKALES_EXEMPLAR_OWNER")
    active = register_value(post, pre, "ACTIVE_ITEM/PREPARATION", "LOKALES_EXEMPLAR_ACTIVE")
    target = register_value(post, pre, "TARGET/STATION", "LOKALES_EXEMPLAR_TARGET")
    previous = register_value(post, pre, "PREVIOUS_ITEM", "LOKALES_EXEMPLAR_PREVIOUS")
    pieces = [f"[STILL:OWNER={owner}]" ]
    if not groups:
        pieces.append(
            f"[STILL:ACTIVE={active}] [STILL:OPERATION=LOKALES_EXEMPLAR] "
            f"[STILL:TARGET={target}] ausführen"
        )
    for group in groups:
        tid = group[0]["template"]
        anchor = "[ANCHOR:" + anchor_label(group) + "]"
        mnemonics = {item["mnemonic"] for item in group}
        if tid == "T1_MEASUREMENT":
            text = (
                f"{anchor} von [STILL:ACTIVE={active}] den bezeichneten Anteil nach "
                "[STILL:PARAMETER=LOKALES_EXEMPLAR] nehmen"
            )
        elif tid == "T2_DESTINATION":
            text = f"{anchor} [STILL:ACTIVE={active}] an [STILL:TARGET={target}] führen"
        elif tid == "T3_BATCH_REFERENCE":
            if "VORIGES?" in mnemonics:
                text = (
                    f"{anchor} [STILL:PREVIOUS={previous}] wieder aufnehmen und als "
                    f"[STILL:ACTIVE={active}] führen"
                )
            else:
                text = f"{anchor} [STILL:ACTIVE={active}] als laufenden Ansatz halten"
        elif tid == "T4_STATE_GATE":
            text = (
                f"{anchor} [STILL:ACTIVE={active}] stehen lassen, bis "
                "[STILL:CRITERION=LOKALES_EXEMPLAR] erfüllt ist"
            )
        elif tid == "T5_APPLY":
            text = f"{anchor} [STILL:ACTIVE={active}] an [STILL:TARGET={target}] anwenden"
        elif tid == "T6_TEMPER":
            text = (
                f"{anchor} [STILL:ACTIVE={active}] nach "
                "[STILL:DEGREE_OR_DURATION=LOKALES_EXEMPLAR] temperieren"
            )
        elif tid == "T7_RINSE":
            text = f"{anchor} [STILL:TARGET={target}] mit [STILL:ACTIVE={active}] spülen"
        elif tid == "T8_DRAIN":
            text = f"{anchor} [STILL:ACTIVE={active}] nach [STILL:TARGET={target}] ablassen"
        else:
            raise AssertionError(tid)
        pieces.append(text)
    if "TERMINAL" in closure:
        pieces.append("[FORMAL:CLOSE;STILL]")
    return " ; ".join(pieces) + "."


def slot_assignment(
    groups: list[list[dict[str, str]]], pre: dict[str, str], post: dict[str, str]
) -> str:
    owner = register_value(post, pre, "OWNER", "LOKALES_EXEMPLAR_OWNER")
    active = register_value(post, pre, "ACTIVE_ITEM/PREPARATION", "LOKALES_EXEMPLAR_ACTIVE")
    target = register_value(post, pre, "TARGET/STATION", "LOKALES_EXEMPLAR_TARGET")
    previous = register_value(post, pre, "PREVIOUS_ITEM", "LOKALES_EXEMPLAR_PREVIOUS")
    values = {
        "T1_MEASUREMENT": f"OWNER={owner};ACTIVE={active};PARAMETER=LOKALES_EXEMPLAR",
        "T2_DESTINATION": f"OWNER={owner};ACTIVE={active};TARGET={target}",
        "T3_BATCH_REFERENCE": f"OWNER={owner};PREVIOUS={previous};ACTIVE={active}",
        "T4_STATE_GATE": f"OWNER={owner};ACTIVE={active};CRITERION=LOKALES_EXEMPLAR",
        "T5_APPLY": f"OWNER={owner};ACTIVE={active};TARGET={target}",
        "T6_TEMPER": f"OWNER={owner};ACTIVE={active};DEGREE_OR_DURATION=LOKALES_EXEMPLAR",
        "T7_RINSE": f"OWNER={owner};ACTIVE={active};TARGET={target}",
        "T8_DRAIN": f"OWNER={owner};ACTIVE={active};TARGET={target}",
    }
    if not groups:
        return (
            f"EXEMPLAR_ONLY{{OWNER={owner};ACTIVE={active};OPERATION=LOKALES_EXEMPLAR;"
            f"TARGET={target}}}"
        )
    return " > ".join(
        f"{group[0]['template']}{{{values[group[0]['template']]};anchor={anchor_label(group)}}}"
        for group in groups
    )


def counter_parse(template_path: list[str]) -> str:
    if not template_path:
        return "Formular- oder Kopiertext; ohne vorab lizenzierenden Prompt ist keine Slotklausel belegt."
    rivals = {
        "T1_MEASUREMENT": "Parameter-/Losspalte ohne Mengensyntax",
        "T2_DESTINATION": "Diagrammadresse statt Zielargument",
        "T3_BATCH_REFERENCE": "Kopier-/Statuszeiger statt Ansatzrückgriff",
        "T4_STATE_GATE": "Zustandslabel statt zeitlicher Bedingung",
        "T5_APPLY": "neutraler Operationscode statt medizinischer Anwendung",
        "T6_TEMPER": "technisches Konditionieren statt medizinischer Temperierung",
        "T7_RINSE": "Apparaturreinigung oder Schlussschritt A",
        "T8_DRAIN": "Wasserwerkablauf oder Schlussschritt B",
    }
    unique = list(dict.fromkeys(template_path))
    joined = "; ".join(rivals[item] for item in unique)
    if len(unique) > 1:
        joined += "; alternativ unabhängige Formularspalten statt einer Klauselkette"
    return joined + "."


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def main() -> None:
    events = guarded_rows(EVENTS, EVENT_COLUMNS)
    statements = guarded_rows(STATEMENTS, STATEMENT_COLUMNS)
    transitions = guarded_rows(TRANSITIONS, TRANSITION_COLUMNS)
    assert len(events) == 381
    assert len(statements) == 116
    assert len(transitions) == 116

    event_by_serial = {row["event_serial"]: row for row in events}
    transition_by_statement = {row["statement_id"]: row for row in transitions}
    assert len(event_by_serial) == 381
    assert len(transition_by_statement) == 116

    mapped: list[dict[str, object]] = []
    used_event_serials: list[str] = []
    anchor_counts: Counter[str] = Counter()
    prompt_counts: Counter[str] = Counter()
    mnemonic_counts: Counter[str] = Counter()

    for statement in statements:
        transition = transition_by_statement[statement["statement_id"]]
        serials = split_pipe(statement["event_serials"])
        used_event_serials.extend(serials)
        anchors: list[dict[str, str]] = []
        formal_sequence: list[str] = []
        formal_value_sequence: list[str] = []
        terminal_events: list[str] = []
        mnemonic_sequence: list[str] = []
        exact_event_mnemonics: list[str] = []

        for serial in serials:
            event = event_by_serial[serial]
            formal = event["strict_control_prompt"]
            mnemonic = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            if formal != "NONE":
                formal_sequence.append(f"e{serial}:{formal}")
                formal_value_sequence.append(f"e{serial}:{event['FORMAL_VALUE']}")
                prompt_counts[formal] += 1
            if event["terminal_status"] == "TERMINAL":
                terminal_events.append(f"e{serial}:{event['FORMAL_VALUE']}")
            if mnemonic != "UNKNOWN":
                mnemonic_sequence.append(f"e{serial}:{mnemonic}")
                exact_event_mnemonics.append(mnemonic)
                mnemonic_counts[mnemonic] += 1
            tids = set()
            if formal in FORMAL_TO_TEMPLATE:
                tids.add(FORMAL_TO_TEMPLATE[formal])
            if mnemonic in MNEMONIC_TO_TEMPLATE:
                tids.add(MNEMONIC_TO_TEMPLATE[mnemonic])
            assert len(tids) <= 1, (serial, formal, mnemonic, tids)
            if tids:
                tid = next(iter(tids))
                anchors.append(
                    {
                        "event_serial": serial,
                        "template": tid,
                        "formal": formal,
                        "mnemonic": mnemonic,
                    }
                )
                anchor_counts[tid] += 1

        groups = group_consecutive(anchors)
        template_path = [anchor["template"] for anchor in anchors]
        group_path = [group[0]["template"] for group in groups]
        unique_templates = list(dict.fromkeys(template_path))
        conflict_codes: list[str] = []

        repeated_exact = sorted(
            mnemonic for mnemonic, count in Counter(exact_event_mnemonics).items() if count > 1
        )
        if repeated_exact:
            conflict_codes.append("REPEATED_EXACT_SLOT:" + ",".join(repeated_exact))

        terminal_positions = [
            index for index, tid in enumerate(template_path) if tid in {"T7_RINSE", "T8_DRAIN"}
        ]
        if terminal_positions and max(terminal_positions) != len(template_path) - 1:
            conflict_codes.append("TERMINAL_ACTION_NOT_LAST")
        if {"T7_RINSE", "T8_DRAIN"}.issubset(template_path):
            conflict_codes.append("TWO_TERMINAL_ACTIONS")

        ranked_path = [tid for tid in group_path if tid != "T2_DESTINATION"]
        inversions = [
            f"{left}>{right}"
            for left, right in zip(ranked_path, ranked_path[1:])
            if RANK[left] > RANK[right]
        ]
        if inversions:
            conflict_codes.append("CANONICAL_ORDER_STRAIN:" + ",".join(inversions))

        hard_conflict = any(
            code.startswith(("REPEATED_EXACT_SLOT", "TERMINAL_ACTION_NOT_LAST", "TWO_TERMINAL_ACTIONS"))
            for code in conflict_codes
        )
        if not anchors:
            assignment_status = "EXEMPLAR_ONLY"
        elif hard_conflict:
            assignment_status = "CONFLICTING"
        elif inversions:
            assignment_status = "FITS_WITH_ORDER_STRAIN"
        elif len(unique_templates) == 1:
            assignment_status = "SINGLE_TEMPLATE_FIT"
        else:
            assignment_status = "COMPOSITE_FIT"

        pre = parse_state(transition["pre_state"])
        post = parse_state(transition["post_state"])
        owner = register_value(post, pre, "OWNER", "LOKALES_EXEMPLAR_OWNER")
        active = register_value(post, pre, "ACTIVE_ITEM/PREPARATION", "LOKALES_EXEMPLAR_ACTIVE")
        target = register_value(post, pre, "TARGET/STATION", "LOKALES_EXEMPLAR_TARGET")
        previous = register_value(post, pre, "PREVIOUS_ITEM", "LOKALES_EXEMPLAR_PREVIOUS")

        mapped.append(
            {
                "statement_id": statement["statement_id"],
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
                "constituent_fields": statement["constituent_fields"],
                "event_count": statement["event_count"],
                "event_serials": statement["event_serials"],
                "closure_sequence": statement["closure_sequence"],
                "entry_boundary_class": statement["entry_boundary_class"],
                "exit_boundary_class": statement["exit_boundary_class"],
                "formal_prompt_sequence": " | ".join(formal_sequence) or "NONE",
                "formal_value_sequence": " | ".join(formal_value_sequence) or "NONE",
                "terminal_event_sequence": " | ".join(terminal_events) or "NONE",
                "exact_mnemonic_sequence": " | ".join(mnemonic_sequence) or "NONE",
                "source_anchor_stream": " > ".join(anchor_label([anchor]) for anchor in anchors) or "NONE",
                "primary_template": template_path[0] if template_path else "EXEMPLAR_ONLY",
                "template_path": " > ".join(group_path) if group_path else "EXEMPLAR_ONLY",
                "template_anchor_count": len(anchors),
                "unique_template_count": len(unique_templates),
                "slot_assignment_status": assignment_status,
                "conflict_codes": " | ".join(conflict_codes) or "NONE",
                "anonymous_register_state_used": (
                    f"OWNER={owner};ACTIVE={active};TARGET={target};PREVIOUS={previous}"
                ),
                "slot_assignment": slot_assignment(groups, pre, post),
                "historical_style_source_clause": source_clause(
                    groups, pre, post, statement["closure_sequence"]
                ),
                "strongest_counter_parse": counter_parse(template_path),
                "v62_ambiguity_codes_retained": transition["irreducible_ambiguity_codes"],
                "evidence_contract": (
                    "ONLY_SELECTED_V60_EXACT_OR_FORMAL_PROMPT;"
                    "V62_ANONYMOUS_REGISTERS;LOCAL_EXEMPLAR_NOUNS;NO_PHONETICS"
                ),
                "status": "CREATIVE_SLOT_TEST;NOT_DECIPHERMENT",
            }
        )

    assert len(used_event_serials) == 381
    assert len(set(used_event_serials)) == 381
    assert set(used_event_serials) == set(event_by_serial)

    template_columns = [
        "template_id",
        "source_function",
        "licensed_anchors",
        "slot_order",
        "historical_source_frame",
        "historical_mechanism",
        "counter_parse",
        "hard_constraint",
    ]
    mapping_columns = [
        "statement_id",
        "record_unit_id",
        "page",
        "statement_ordinal_in_record",
        "constituent_fields",
        "event_count",
        "event_serials",
        "closure_sequence",
        "entry_boundary_class",
        "exit_boundary_class",
        "formal_prompt_sequence",
        "formal_value_sequence",
        "terminal_event_sequence",
        "exact_mnemonic_sequence",
        "source_anchor_stream",
        "primary_template",
        "template_path",
        "template_anchor_count",
        "unique_template_count",
        "slot_assignment_status",
        "conflict_codes",
        "anonymous_register_state_used",
        "slot_assignment",
        "historical_style_source_clause",
        "strongest_counter_parse",
        "v62_ambiguity_codes_retained",
        "evidence_contract",
        "status",
    ]
    write_tsv(OUT / "V63_R2_SLOT_TEMPLATES.tsv", TEMPLATES, template_columns)
    write_tsv(OUT / "V63_R2_116_STATEMENT_SLOT_MAPPING.tsv", mapped, mapping_columns)

    status_counts = Counter(row["slot_assignment_status"] for row in mapped)
    page_counts = Counter(row["page"] for row in mapped)
    record_counts = Counter(row["record_unit_id"] for row in mapped)
    primary_counts = Counter(row["primary_template"] for row in mapped)
    assignment_statement_counts = Counter()
    for row in mapped:
        for tid in set(row["template_path"].split(" > ")):
            assignment_statement_counts[tid] += 1
    conflict_statements = [row for row in mapped if row["slot_assignment_status"] == "CONFLICTING"]
    strain_statements = [row for row in mapped if row["slot_assignment_status"] == "FITS_WITH_ORDER_STRAIN"]

    forbidden_nouns = re.compile(
        r"\\b(?:Wurzel|Wein|Wasser|Pflanze|Körper|Patient|Frau|Bad|Becken|Gefäß|Leitung|Rohr|Blatt|Blüte)\\b",
        re.IGNORECASE,
    )
    noun_violations = [
        row["statement_id"]
        for row in mapped
        if forbidden_nouns.search(str(row["historical_style_source_clause"]))
    ]
    page_violations = sorted({row["page"] for row in mapped if row["page"] not in PAGES})
    owner_violations = [
        row["statement_id"]
        for row in mapped
        if "[STILL:OWNER=" not in str(row["historical_style_source_clause"])
    ]

    validation = {
        "artifact": "V63_R2_SLOT_GRAMMAR",
        "status": "PASS" if not (noun_violations or page_violations or owner_violations) else "FAIL",
        "scope": {
            "allowed_pages": list(PAGES),
            "sealed_prefix": "f84",
            "source_event_rows": len(events),
            "source_statement_rows": len(statements),
            "source_transition_rows": len(transitions),
            "output_template_rows": len(TEMPLATES),
            "output_mapping_rows": len(mapped),
            "event_serials_covered_once": len(set(used_event_serials)),
            "page_statement_counts": dict(sorted(page_counts.items())),
            "record_statement_counts": dict(sorted(record_counts.items())),
        },
        "coverage": {
            "prompt_licensed_statements": len(mapped) - status_counts["EXEMPLAR_ONLY"],
            "exemplar_only_statements": status_counts["EXEMPLAR_ONLY"],
            "prompt_licensed_fraction": round(
                (len(mapped) - status_counts["EXEMPLAR_ONLY"]) / len(mapped), 6
            ),
            "slot_assignment_status_counts": dict(sorted(status_counts.items())),
            "primary_template_counts": dict(sorted(primary_counts.items())),
            "template_anchor_counts": dict(sorted(anchor_counts.items())),
            "template_statement_counts": dict(sorted(assignment_statement_counts.items())),
            "formal_prompt_event_counts": dict(sorted(prompt_counts.items())),
            "exact_mnemonic_event_counts": dict(sorted(mnemonic_counts.items())),
        },
        "conflict_audit": {
            "conflicting_statement_count": len(conflict_statements),
            "conflicting_statement_ids": [row["statement_id"] for row in conflict_statements],
            "order_strain_statement_count": len(strain_statements),
            "order_strain_statement_ids": [row["statement_id"] for row in strain_statements],
            "all_conflict_code_counts": dict(
                sorted(
                    Counter(
                        code.split(":", 1)[0]
                        for row in mapped
                        for code in str(row["conflict_codes"]).split(" | ")
                        if code != "NONE"
                    ).items()
                )
            ),
        },
        "gates": {
            "all_116_statements_mapped": len(mapped) == 116,
            "all_381_events_covered_once": len(used_event_serials) == len(set(used_event_serials)) == 381,
            "no_forbidden_page": not page_violations,
            "all_clauses_mark_owner": not owner_violations,
            "no_concrete_filled_noun_in_generated_clauses": not noun_violations,
            "no_surface_or_phonetic_column_emitted": True,
            "unknown_content_is_local_exemplar": all(
                "LOCAL_EXEMPLAR" in str(row["evidence_contract"]) for row in mapped
            ),
        },
        "violations": {
            "page": page_violations,
            "owner_marker": owner_violations,
            "concrete_noun": noun_violations,
        },
        "interpretive_limit": (
            "PASS validates row coverage and the declared mechanical grammar only; it does not validate "
            "historical truth, language, sound, or decipherment."
        ),
    }
    (OUT / "V63_R2_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
