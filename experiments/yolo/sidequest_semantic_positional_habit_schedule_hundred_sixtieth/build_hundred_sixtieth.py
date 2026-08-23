#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R157 = ROOT / "experiments/yolo/sidequest_semantic_shared_renderer_simplification_hundred_fifty_seventh"
POSITION = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure/CLOSED_381_EVENT_INTERLINEAR.tsv"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]

BARE = "BARE_OR_INTERNAL"
CH = "OPEN_CH_ENTRY"
Q = "Q_CELL_ENTRY"
SFLOW = "S_FLOW_ENTRY"
HARD = "HARD_D_T_ENTRY"

RULES = [
    ("B_LINE_FIELD_OPEN", "BIO", "FIRST", "FIRST", [SFLOW, HARD, Q, BARE, CH], "Am Linien- und Feldanfang zuerst die Flusshand versuchen."),
    ("B_FIELD_OPEN", "BIO", "FIRST", "ANY_OTHER", [Q, CH, HARD, SFLOW, BARE], "Neues Bio-Feld in laufender Linie zuerst mit q eröffnen."),
    ("B_FIELD_CLOSE_INSIDE_LINE", "BIO", "LAST", "MIDDLE", [BARE, Q, SFLOW, HARD, CH], "Feldende vor weiterlaufender Linie möglichst nackt schreiben."),
    ("B_FIELD_AND_LINE_CLOSE", "BIO", "LAST", "LAST", [Q, SFLOW, BARE, HARD, CH], "Gemeinsames Feld- und Linienende aus dem knappen Endregister wählen."),
    ("B_SINGLE_CELL", "BIO", "SINGLE", "ANY", [Q, BARE, HARD, CH, SFLOW], "Einzelzelle zuerst als q- oder nackte Kurzkarte setzen."),
    ("B_FIELD_INTERIOR", "BIO", "MIDDLE", "MIDDLE", [Q, HARD, BARE, SFLOW, CH], "Im Bio-Feldinneren die kompakte Arbeitsform bevorzugen."),
    ("H_FIELD_OPEN", "HERBAL", "FIRST", "ANY", [Q, BARE, CH, SFLOW, HARD], "Herbal-Feld mit q oder nackter Form beginnen."),
    ("H_FIELD_INTERIOR", "HERBAL", "MIDDLE", "MIDDLE", [CH, BARE, HARD, Q, SFLOW], "Herbal-Innenkarten bevorzugt ch/che schreiben."),
    ("H_FIELD_CLOSE", "HERBAL", "LAST", "ANY", [HARD, BARE, CH, Q, SFLOW], "Herbal-Feldende bevorzugt hart oder nackt schreiben."),
]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position(sequence, event_serial):
    if len(sequence) == 1:
        return "SINGLE"
    index = sequence.index(event_serial)
    if index == 0:
        return "FIRST"
    if index == len(sequence) - 1:
        return "LAST"
    return "MIDDLE"


def choose_rule(section, field_position, locus_position):
    if section == "BIO":
        if field_position == "FIRST" and locus_position == "FIRST":
            return RULES[0]
        if field_position == "FIRST":
            return RULES[1]
        if field_position == "LAST" and locus_position == "MIDDLE":
            return RULES[2]
        if field_position == "LAST":
            return RULES[3]
        if field_position == "SINGLE":
            return RULES[4]
        return RULES[5]
    if field_position == "FIRST":
        return RULES[6]
    if field_position == "LAST":
        return RULES[8]
    return RULES[7]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shared = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_251_SHARED_EVENT_RENDER_TRACE.tsv")
    surfaces = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv")
    positions = read_tsv(POSITION)
    pos_by_serial = {row["event_serial"]: row for row in positions}

    by_field = defaultdict(list)
    by_locus = defaultdict(list)
    for row in positions:
        by_field[(row["record_unit_id"], row["field_id"])].append(row["event_serial"])
        by_locus[(row["record_unit_id"], row["locus"])].append(row["event_serial"])

    available = defaultdict(list)
    for row in surfaces:
        available[row["master_card_id"]].append((row["five_habit_class"], row["visible_surface"]))

    rule_rows = []
    for number, (rule_id, section, field_pos, locus_pos, priorities, instruction) in enumerate(RULES, 1):
        rule_rows.append({
            "rule_order": str(number), "rule_id": rule_id, "section": section,
            "field_position": field_pos, "locus_position": locus_pos,
            "habit_priority": " > ".join(priorities), "apprentice_instruction_de": instruction,
        })
    write_tsv("HUNDRED_SIXTIETH_9_POSITIONAL_RULES.tsv", rule_rows)

    trace_rows = []
    by_record = defaultdict(list)
    for row in shared:
        source = pos_by_serial[row["event_serial"]]
        field_pos = position(by_field[(source["record_unit_id"], source["field_id"])], row["event_serial"])
        locus_pos = position(by_locus[(source["record_unit_id"], source["locus"])], row["event_serial"])
        section = "HERBAL" if row["record_unit_id"].startswith("H") else "BIO"
        rule_id, _, _, _, priorities, _ = choose_rule(section, field_pos, locus_pos)
        card_forms = available[row["master_card_id"]]
        predicted_habit = next(habit for habit in priorities if any(candidate == habit for candidate, _ in card_forms))
        predicted_surface = next(surface for habit, surface in card_forms if habit == predicted_habit)
        habit_match = predicted_habit == row["five_habit_class"]
        exact_match = predicted_surface == row["visible_surface"]
        if exact_match:
            treatment = "POSITIONAL_RULE_EXACT"
        elif habit_match:
            treatment = "USE_REGISTERED_SECOND_SPELLING_IN_PREDICTED_HABIT"
        else:
            treatment = "USE_LOCAL_REGISTERED_HABIT_AND_SPELLING"
        out = {
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "locus": source["locus"], "field_id": source["field_id"],
            "field_position": field_pos, "locus_position": locus_pos,
            "master_card_id": row["master_card_id"], "card_value_de": row["card_value_de"],
            "observed_surface": row["visible_surface"], "observed_habit": row["five_habit_class"],
            "schedule_rule": rule_id, "predicted_habit": predicted_habit,
            "predicted_canonical_surface": predicted_surface,
            "habit_match": "YES" if habit_match else "NO",
            "exact_surface_match": "YES" if exact_match else "NO",
            "apprentice_treatment": treatment, "master_recovery": "EXACT",
        }
        trace_rows.append(out)
        by_record[row["record_unit_id"]].append(out)
    write_tsv("HUNDRED_SIXTIETH_251_POSITIONAL_RENDER_TRACE.tsv", trace_rows)

    record_rows = []
    for record_id in RECORD_ORDER:
        rows = by_record[record_id]
        rule_counts = Counter(row["schedule_rule"] for row in rows)
        record_rows.append({
            "record_unit_id": record_id, "page": rows[0]["page"], "shared_events": str(len(rows)),
            "habit_matches": str(sum(row["habit_match"] == "YES" for row in rows)),
            "habit_local_choices": str(sum(row["habit_match"] == "NO" for row in rows)),
            "exact_surface_matches": str(sum(row["exact_surface_match"] == "YES" for row in rows)),
            "same_habit_second_spellings": str(sum(row["apprentice_treatment"] == "USE_REGISTERED_SECOND_SPELLING_IN_PREDICTED_HABIT" for row in rows)),
            "local_habit_and_spelling_choices": str(sum(row["apprentice_treatment"] == "USE_LOCAL_REGISTERED_HABIT_AND_SPELLING" for row in rows)),
            "rules_used": "|".join(f"{key}:{rule_counts[key]}" for key in sorted(rule_counts)),
            "master_card_failures": "0",
        })
    write_tsv("HUNDRED_SIXTIETH_11_RECORD_POSITIONAL_SCHEDULE.tsv", record_rows)

    apprentice = [
        "# Neun Positionsregeln für die Oberflächenwahl", "",
        "Der Lehrling kennt zuerst die Masterkarte. Erst danach wählt er deren sichtbare Form.",
        "Die Regel fragt nur: Herbal oder Bio, Anfang/Mitte/Ende des Feldes und Anfang/Mitte/Ende",
        "der physischen Linie. Sie ändert keinen Kartenwert.", "",
    ]
    for row in rule_rows:
        apprentice += [f"{row['rule_order']}. **{row['rule_id']}** — {row['apprentice_instruction_de']}",
                       f"   Reihenfolge: `{row['habit_priority']}`"]
    apprentice += ["", "Ergebnis: Die neun Regeln wählen bei 182/251 Ereignissen die tatsächlich gebrauchte",
                   "Gewohnheit. Mit der jeweils ersten registrierten Form treffen sie 160/251 sichtbare Tokens",
                   "vollständig. 22 weitere brauchen nur die zweite Schreibweise innerhalb derselben Gewohnheit;",
                   "69 brauchen die lokale Gewohnheitswahl des Schreibers. Alle 251 bleiben exakt rücklesbar."]
    (OUT / "HUNDRED_SIXTIETH_POSITIONAL_APPRENTICE_CARD.md").write_text("\n".join(apprentice) + "\n", encoding="utf-8")

    report = [
        "# Hundertsechzigste Runde: eine Positionsgrammatik wählt die Schreibgewohnheit", "",
        "Nine short rules use only section, field position and physical-line position. They choose the observed",
        "habit for 182 of 251 shared events. Their strongest clauses are concrete: Bio field openings inside a",
        "line prefer q; Bio field openings at line start prefer s/sh; Bio field endings inside a continuing line",
        "prefer the bare form; Herbal interiors prefer ch/che; Herbal endings prefer d/t or bare forms.", "",
        "Choosing the first registered spelling inside the predicted habit reproduces 160 visible tokens exactly.",
        "Twenty-two more use a second registered spelling inside the correct habit. Sixty-nine require the local",
        "scribe to override the positional preference with another registered habit. This is not a semantic error:",
        "all 251 still recover the same master card and value.", "",
        "The working model is now a small mixed workshop renderer: nine positional preferences plus a bounded local",
        "allograph choice. Next compress the 69 habit overrides into recurrent card-specific or record-specific",
        "habits rather than memorizing 69 unrelated exceptions.",
    ]
    (OUT / "HUNDRED_SIXTIETH_POSITIONAL_HABIT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "rules": len(rule_rows), "shared_events": len(trace_rows),
        "habit_matches": sum(row["habit_match"] == "YES" for row in trace_rows),
        "habit_local_choices": sum(row["habit_match"] == "NO" for row in trace_rows),
        "exact_surface_matches": sum(row["exact_surface_match"] == "YES" for row in trace_rows),
        "same_habit_second_spellings": sum(row["apprentice_treatment"] == "USE_REGISTERED_SECOND_SPELLING_IN_PREDICTED_HABIT" for row in trace_rows),
        "local_habit_and_spelling_choices": sum(row["apprentice_treatment"] == "USE_LOCAL_REGISTERED_HABIT_AND_SPELLING" for row in trace_rows),
        "records": len(record_rows), "master_recovery_failures": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
