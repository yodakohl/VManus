#!/usr/bin/env python3
"""Close the twenty-card bound-carrier layer of the workshop dictionary."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_nomenclator_family_completion"
DICT_IN = SOURCE / "COMPACT_173_CARD_DICTIONARY.tsv"
EVENTS_IN = SOURCE / "COMPACT_381_EVENT_INTERLINEAR.tsv"
PHRASES_IN = SOURCE / "COMPACT_116_PHRASES.tsv"

LEXICON_OUT = HERE / "BOUND_CARRIER_8_LEXICON.tsv"
CLOSURE_OUT = HERE / "PARTIAL_20_CLOSURE.tsv"
DICT_OUT = HERE / "CLOSED_173_CARD_DICTIONARY.tsv"
EVENTS_OUT = HERE / "CLOSED_381_EVENT_INTERLINEAR.tsv"
PHRASES_OUT = HERE / "CLOSED_116_PHRASES.tsv"
DRILLS_OUT = HERE / "CARRIER_8_DRILLS.tsv"
RECORDS_OUT = HERE / "CLOSED_11_RECORDS.md"
MANUAL_OUT = HERE / "BOUND_CARRIER_LEAF.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"


# id -> kind, visible realization, contribution, teaching rule
CARRIER_RULES = {
    "C01_LOCAL_FRAME": (
        "FORMAL_FRAME",
        "R... / T...",
        "kein eigenes Sachwort; bindet die Karte an den lokalen aktiven Posten",
        "R oder T nicht uebersetzen; den eingeschlossenen bekannten Kern lesen.",
    ),
    "C02_TERMINAL_D_FRAME": (
        "FORMAL_FRAME",
        "D...D / lizenzierte ...DY-Endkarte",
        "setzt den bekannten Arbeitsgang als geschlossene Zelle",
        "Nur bei den gelernten exakten Karten als Schlussrahmen lesen; niemals nacktes D global als SCHLUSS lesen.",
    ),
    "C03_O_RESIDUAL_BRANCH": (
        "BOUND_CLASSIFIER",
        "O innerhalb L-O oder L-O-CHED",
        "waehlt Rest- oder Nebenast des laufenden Weges",
        "Mit L als abgehenden Rest-/Nebenast lesen; mit CHED den Rest abfuehren.",
    ),
    "C04_S_PORT": (
        "BOUND_CLASSIFIER",
        "S nach L",
        "waehlt den markierten Auslass",
        "L+S als Abgang durch den markierten Auslass lesen.",
    ),
    "C05_KY_PATH": (
        "BOUND_CLASSIFIER",
        "KY nach OL",
        "haelt den lokalen Arbeitsweg aktiv",
        "OL+KY als auf demselben lokalen Arbeitsweg weiterfuehren lesen.",
    ),
    "C06_DAN_APPLY": (
        "LEXICAL_MICROCORE",
        "DAN",
        "anwenden",
        "OT+DAN als danach anwenden lesen.",
    ),
    "C07_SK_POUR": (
        "LEXICAL_MICROCORE",
        "SK",
        "ausgiessen",
        "SK+AR als aus der bezeichneten Quelle ausgiessen lesen.",
    ),
    "C08_T_AM_STORE": (
        "LEXICAL_MICROCORE",
        "T...AM mit eingesetztem AL",
        "verwahren",
        "T+AL+AM als am Ziel verwahren lesen.",
    ),
}


# surface -> rule ids, fully closed parse, unchanged concise reading, rationale
CARD_CLOSURES = {
    "ldy": ("C02_TERMINAL_D_FRAME", "L_OUT+CLOSE_EXACT", "abziehen; Ende", "L liefert den Abgang; die exakte Endkarte schliesst."),
    "rol": ("C01_LOCAL_FRAME", "R_FRAME+OL_CONTINUE", "weiterfuehren", "R ist lokaler Rahmen; OL traegt die Fortsetzung."),
    "lo": ("C03_O_RESIDUAL_BRANCH", "L_OUT+O_RESIDUAL_BRANCH", "abfuehren", "L und der gebundene O-Restast genuegen."),
    "ral": ("C01_LOCAL_FRAME", "R_FRAME+AL_TO", "zur Zielstelle", "R ist lokaler Rahmen; AL traegt das Ziel."),
    "ls": ("C04_S_PORT", "L_OUT+S_PORT", "Auslass", "S waehlt den markierten Port innerhalb des L-Abgangs."),
    "sotodan": ("C01_LOCAL_FRAME|C06_DAN_APPLY", "S_FRAME+OT_FOLLOW+DAN_APPLY", "danach anwenden", "S ist Rahmen; OT ordnet; DAN liefert Anwenden."),
    "otytchol": ("NONE_ALREADY_COMPOSED", "OT_FOLLOW+TY_PART+OL_CONTINUE", "naechsten Teilposten weiterfuehren", "Alle drei sichtbaren Kerne waren bereits im Lehrkasten."),
    "daldy": ("C02_TERMINAL_D_FRAME", "D_SIDE_FRAME+AL_TO+CLOSE_EXACT", "Nebenoeffnung; Schluss", "Der D-Rahmen waehlt die seitliche Zielzelle; AL liefert das Ziel."),
    "skar": ("C07_SK_POUR", "SK_POUR+AR_FROM", "von dort ausgiessen", "SK liefert Ausgiessen; AR liefert die Quelle."),
    "dairydy": ("C02_TERMINAL_D_FRAME", "D_TERMINAL_FRAME+AIR_WATER+Y_ITEM+CLOSE_EXACT", "Wasserlauf schliessen; Schluss", "AIR und Y liefern Wasserlauf und Posten; der exakte D-Rahmen schliesst."),
    "lol": ("NONE_ALREADY_COMPOSED", "L_OUT+OL_CONTINUE", "von dort weiterfuehren", "L und OL sind bereits bekannte Richtungs- und Fortsetzungskerne."),
    "cheeety": ("NONE_ALREADY_COMPOSED", "EEE_FULL+TY_PART", "ganzen Teilposten", "EEE und TY sind bereits bekannte Grad- und Teilkerne."),
    "sheey": ("NONE_ALREADY_COMPOSED", "SH_REST+EE_LONG+Y_CURRENT", "laenger ruhen", "SH, EE und Y sind bereits bekannte Zustandskerne."),
    "tshol": ("C01_LOCAL_FRAME", "T_FRAME+HO_INGREDIENT+L_OUT", "Zutat entnehmen", "T ist lokaler Rahmen; HO und L liefern Zutat und Entnahme."),
    "rsheal": ("C01_LOCAL_FRAME", "R_FRAME+SH_REST+E_SHORT+AL_TO", "kurz am Ziel ruhen", "R ist Rahmen; SH, E und AL liefern Zustand, Grad und Ziel."),
    "qolky": ("C05_KY_PATH", "Q_FRAME+OL_CONTINUE+KY_PATH", "weiterfuehren", "Q ist Oberflaechenrahmen; OL und KY halten denselben Arbeitsweg."),
    "tshey": ("C01_LOCAL_FRAME", "T_FRAME+SHEY_CLEAR_FLOW", "Klarlauf", "T ist lokaler Rahmen; SHEY traegt den Klarlauf."),
    "chealror": ("C01_LOCAL_FRAME", "AL_TO+R_FRAME+OR_BATCH", "Ansatz von dort zur Zielstelle", "R bindet lokal; AL und OR liefern Ziel und Ansatz."),
    "talam": ("C08_T_AM_STORE", "T_STORE_FRAME+AL_TO+AM_STORE", "am Ziel verwahren", "Der Speicherrahmen T...AM umschliesst AL als Ziel."),
    "lochedy": ("C03_O_RESIDUAL_BRANCH|C02_TERMINAL_D_FRAME", "L_OUT+O_RESIDUAL_BRANCH+CHED_TRANSFER+CLOSE_EXACT", "Rest abfuehren; Schluss", "O waehlt den Restast; L und CHED fuehren ihn ab; die exakte Karte schliesst."),
}


DRILL_STATEMENTS = {
    "C01_LOCAL_FRAME": "B1-S006",
    "C02_TERMINAL_D_FRAME": "B3-S033",
    "C03_O_RESIDUAL_BRANCH": "B2-S022",
    "C04_S_PORT": "B2-S010",
    "C05_KY_PATH": "B1-S014",
    "C06_DAN_APPLY": "H5-S005",
    "C07_SK_POUR": "B4-S016",
    "C08_T_AM_STORE": "H4-S002",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENTS_IN)
    phrases = read_tsv(PHRASES_IN)
    assert (len(dictionary), len(events), len(phrases)) == (173, 381, 116)
    partial = [row for row in dictionary if row["compact_architecture"] == "PARTIAL_COMPOSITION"]
    assert len(partial) == 20
    assert {row["surface_family"] for row in partial} == set(CARD_CLOSURES)

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_card[event["joint_tuple_id"]].append(event)
        events_by_statement[event["statement_id"]].append(event)
    partial_ids = {row["joint_tuple_id"] for row in partial}
    assert sum(row["joint_tuple_id"] in partial_ids for row in events) == 21

    closure_rows: list[dict[str, str]] = []
    for card in partial:
        rule_ids, closed_parse, closed_reading, rationale = CARD_CLOSURES[card["surface_family"]]
        card_events = events_by_card[card["joint_tuple_id"]]
        closure_rows.append({
            "joint_tuple_id": card["joint_tuple_id"],
            "surface_family": card["surface_family"],
            "occurrences": str(len(card_events)),
            "event_ids": "|".join(row["event_id"] for row in card_events),
            "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in card_events)),
            "pages": "|".join(dict.fromkeys(row["page"] for row in card_events)),
            "previous_parse": card["compact_parse"],
            "previous_reading_de": card["compact_reading_de"],
            "carrier_rule_ids": rule_ids,
            "closed_parse": closed_parse,
            "closed_reading_de": closed_reading,
            "closure_status": "PROMOTED_TO_PRODUCTIVE_COMPOSITION",
            "apprentice_rationale_de": rationale,
        })
    closure_rows.sort(key=lambda row: int(row["event_ids"].split("|")[0][1:]))
    closure_by_id = {row["joint_tuple_id"]: row for row in closure_rows}

    carrier_rows: list[dict[str, str]] = []
    for rule_id, (kind, realization, contribution, teaching) in CARRIER_RULES.items():
        selected = [row for row in closure_rows if rule_id in row["carrier_rule_ids"].split("|")]
        carrier_rows.append({
            "carrier_rule_id": rule_id,
            "carrier_kind": kind,
            "visible_realization": realization,
            "contribution_de": contribution,
            "card_types": str(len(selected)),
            "occurrences": str(sum(int(row["occurrences"]) for row in selected)),
            "surface_families": ";".join(row["surface_family"] for row in selected),
            "apprentice_rule_de": teaching,
        })

    dict_rows: list[dict[str, str]] = []
    for card in dictionary:
        closure = closure_by_id.get(card["joint_tuple_id"])
        if closure:
            status = "PROMOTED_FROM_PARTIAL"
            rules = closure["carrier_rule_ids"]
            architecture = "PRODUCTIVE_COMPOSITION"
            parse = closure["closed_parse"]
            reading = closure["closed_reading_de"]
        else:
            status = "UNCHANGED_WHOLE" if card["compact_architecture"] == "MEMORIZED_WHOLE_CARD" else "UNCHANGED_PRODUCTIVE"
            rules = "NONE"
            architecture = card["compact_architecture"]
            parse = card["compact_parse"]
            reading = card["compact_reading_de"]
        dict_rows.append({
            "joint_tuple_id": card["joint_tuple_id"],
            "surface_family": card["surface_family"],
            "occurrences": card["occurrences"],
            "records": card["records"],
            "pages": card["pages"],
            "previous_architecture": card["compact_architecture"],
            "previous_parse": card["compact_parse"],
            "previous_reading_de": card["compact_reading_de"],
            "carrier_closure_status": status,
            "carrier_rule_ids": rules,
            "closed_architecture": architecture,
            "closed_parse": parse,
            "closed_reading_de": reading,
            "teaching_symbol": "W" if architecture == "MEMORIZED_WHOLE_CARD" else "P",
        })
    closed_by_id = {row["joint_tuple_id"]: row for row in dict_rows}

    event_rows: list[dict[str, str]] = []
    for event in events:
        card = closed_by_id[event["joint_tuple_id"]]
        event_rows.append({
            "event_serial": event["event_serial"],
            "event_id": event["event_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display": event["surface_display"],
            "previous_architecture": event["compact_architecture"],
            "carrier_closure_status": card["carrier_closure_status"],
            "carrier_rule_ids": card["carrier_rule_ids"],
            "closed_architecture": card["closed_architecture"],
            "teaching_symbol": card["teaching_symbol"],
            "closed_parse": card["closed_parse"],
            "closed_card_reading_de": card["closed_reading_de"],
            "contextual_event_reading_de": event["compact_contextual_event_de"],
            "step_closure_role": event["step_closure_role"],
        })

    phrase_rows: list[dict[str, str]] = []
    for phrase in phrases:
        selected = events_by_statement[phrase["statement_id"]]
        closed_events = [next(row for row in event_rows if row["event_id"] == event["event_id"]) for event in selected]
        symbols = [row["teaching_symbol"] for row in closed_events]
        promoted = [row for row in closed_events if row["carrier_closure_status"] == "PROMOTED_FROM_PARTIAL"]
        phrase_rows.append({
            "statement_id": phrase["statement_id"],
            "record_unit_id": phrase["record_unit_id"],
            "page": phrase["page"],
            "loci": phrase["loci"],
            "event_count": phrase["event_count"],
            "surface_sequence": " ".join(row["surface_display"] for row in closed_events),
            "architecture_sequence": " ".join(symbols),
            "card_reading_sequence_de": " -> ".join(row["closed_card_reading_de"] for row in closed_events),
            "fluent_workshop_sentence_de": phrase["compact_fluent_sentence_de"],
            "lesson_level": "L2_CODEBOOK" if "W" in symbols else "L1_FULLY_COMPOSED",
            "promoted_carrier_cards": "|".join(row["surface_display"] for row in promoted) if promoted else "NONE",
            "promoted_carrier_rule_ids": "|".join(dict.fromkeys(
                rule for row in promoted for rule in row["carrier_rule_ids"].split("|") if rule != "NONE_ALREADY_COMPOSED"
            )) or "NONE",
        })

    phrase_by_id = {row["statement_id"]: row for row in phrase_rows}
    drill_rows: list[dict[str, str]] = []
    for ordinal, (rule_id, statement_id) in enumerate(DRILL_STATEMENTS.items(), start=1):
        carrier = next(row for row in carrier_rows if row["carrier_rule_id"] == rule_id)
        phrase = phrase_by_id[statement_id]
        drill_rows.append({
            "drill_id": f"C{ordinal:02d}",
            "carrier_rule_id": rule_id,
            "carrier_kind": carrier["carrier_kind"],
            "statement_id": statement_id,
            "page": phrase["page"],
            "surface_sequence": phrase["surface_sequence"],
            "target_instruction_de": phrase["fluent_workshop_sentence_de"],
            "carrier_contribution_de": carrier["contribution_de"],
            "exercise_de": "Unterstreiche den bekannten Kern, klammere den gebundenen Traeger ein und lies danach den ganzen Arbeitsschritt.",
        })

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for phrase in phrase_rows:
        records[phrase["record_unit_id"]].append(phrase)
    record_lines = [
        "# Geschlossene Elf-Record-Werkstattausgabe",
        "",
        "`P` umfasst jetzt auch die acht gebundenen Traegerregeln; `W` bleibt eine gelernte Ganzkarte.",
        "",
    ]
    for record_id, rows in records.items():
        record_lines.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for row in rows:
            record_lines.append(f"- **{row['statement_id']}** `{row['architecture_sequence']}` — {row['fluent_workshop_sentence_de']}")
        record_lines.append("")

    manual_lines = [
        "# Blatt der acht gebundenen Traeger",
        "",
        "Die Traeger sind keine zwanzig neuen Woerter. Zwei sind Schreibrahmen, drei sind kleine Klassifikatoren und drei kurze Fachkerne.",
        "",
        "| ID | Art | sichtbare Form | Beitrag |",
        "|---|---|---|---|",
    ]
    for row in carrier_rows:
        manual_lines.append(f"| {row['carrier_rule_id']} | {row['carrier_kind']} | `{row['visible_realization']}` | {row['contribution_de']} |")
    manual_lines.extend([
        "",
        "## Lehrregel",
        "",
        "1. R/T-Rahmen nicht als eigenes Sachwort uebersetzen.",
        "2. Den D-Schluss nur in der lizenzierten exakten Karte lesen.",
        "3. O, S und KY waehlen Restast, Auslass oder lokalen Arbeitsweg.",
        "4. DAN, SK und T...AM tragen die kurzen Fachwerte ANWENDEN, AUSGIESSEN und VERWAHREN.",
        "5. Alle uebrigen sichtbaren Kerne normal zusammensetzen.",
        "",
        "> Nach diesem Blatt gibt es keine teilweise gelesene Karte mehr: nur gebaute Karten und gelernte Ganzkarten.",
    ])

    write_tsv(LEXICON_OUT, carrier_rows)
    write_tsv(CLOSURE_OUT, closure_rows)
    write_tsv(DICT_OUT, dict_rows)
    write_tsv(EVENTS_OUT, event_rows)
    write_tsv(PHRASES_OUT, phrase_rows)
    write_tsv(DRILLS_OUT, drill_rows)
    RECORDS_OUT.write_text("\n".join(record_lines).rstrip() + "\n", encoding="utf-8")
    MANUAL_OUT.write_text("\n".join(manual_lines).rstrip() + "\n", encoding="utf-8")

    type_architecture = Counter(row["closed_architecture"] for row in dict_rows)
    event_architecture = Counter(row["closed_architecture"] for row in event_rows)
    lesson_levels = Counter(row["lesson_level"] for row in phrase_rows)
    summary = {
        "status": "PASS",
        "carrier_rules": len(carrier_rows),
        "promoted_card_types": len(closure_rows),
        "promoted_events": sum(row["carrier_closure_status"] == "PROMOTED_FROM_PARTIAL" for row in event_rows),
        "card_architecture": dict(type_architecture),
        "event_architecture": dict(event_architecture),
        "lesson_levels": dict(lesson_levels),
        "files": {},
    }
    for path in [LEXICON_OUT, CLOSURE_OUT, DICT_OUT, EVENTS_OUT, PHRASES_OUT, DRILLS_OUT, RECORDS_OUT, MANUAL_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
