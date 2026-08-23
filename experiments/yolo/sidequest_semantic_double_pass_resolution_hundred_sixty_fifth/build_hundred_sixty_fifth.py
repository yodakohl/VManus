#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R164 = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth"
POSITION = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure/CLOSED_381_EVENT_INTERLINEAR.tsv"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R164 / "HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv")
    clauses = read_tsv(R164 / "HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv")
    positions = {row["event_serial"]: row for row in read_tsv(POSITION)}
    by_serial = {row["event_serial"]: row for row in events}

    target_serials = ["327", "328", "329", "330", "331"]
    target_rows = []
    pass_number = {"330": "FIRST_PASS", "331": "SECOND_PASS"}
    for serial in target_serials:
        event = by_serial[serial]
        pos = positions[serial]
        target_rows.append({
            "event_serial": serial, "statement_id": event["statement_id"], "record_unit_id": event["record_unit_id"],
            "page": event["page"], "locus": pos["locus"], "field_id": pos["field_id"],
            "visible_surface": event["visible_surface"], "master_card_id": event["master_card_id"],
            "atomic_value_de": event["card_value_de"], "terminal_status": event["terminal_status"],
            "double_pass_role": pass_number.get(serial, "PREPARE_SHARED_INSERT_AND_CHARGE"),
            "continuous_action_de": {
                "327": "Einlage einsetzen", "328": "den Posten überführen", "329": "länger darin einwirken lassen",
                "330": "einmal durchlassen", "331": "ein zweites Mal durchlassen",
            }[serial],
        })
    write_tsv("HUNDRED_SIXTY_FIFTH_5_EVENT_DOUBLE_PASS.tsv", target_rows)

    models = [
        {
            "model": "TWO_SEQUENTIAL_PASSES_THROUGH_ONE_INSERT", "selection": "SELECTED",
            "separate_committed_cells": "EXPLAINS", "exact_repetition": "EXPLAINS_AS_REPEAT_ACTION",
            "single_visible_owner": "EXPLAINS", "needs_second_drawn_channel": "NO",
            "workshop_reading_de": "Einlage einsetzen; einmal durchlassen; nochmals durchlassen.",
        },
        {
            "model": "TWO_DIFFERENT_CHANNELS_OR_FILTERS", "selection": "REJECTED_FOR_NOW",
            "separate_committed_cells": "EXPLAINS", "exact_repetition": "WEAK",
            "single_visible_owner": "STRAINED", "needs_second_drawn_channel": "YES_NOT_VISIBLE",
            "workshop_reading_de": "Durch Kanal A, dann Kanal B; die Kanäle sind nicht getrennt bezeichnet.",
        },
        {
            "model": "ACCIDENTAL_DITTOGRAPHY", "selection": "LIVE_RIVAL",
            "separate_committed_cells": "STRAINED", "exact_repetition": "EXPLAINS",
            "single_visible_owner": "NEUTRAL", "needs_second_drawn_channel": "NO",
            "workshop_reading_de": "Der zweite Eintrag wäre Kopierwiederholung; warum er eine eigene Zelle bildet, bleibt offen.",
        },
    ]
    write_tsv("HUNDRED_SIXTY_FIFTH_3_DOUBLE_PASS_MODELS.tsv", models)

    affected_ids = ["B1-S020", "B4-S005", "B4-S006", "B4-S007"]
    clause_by_id = {row["statement_id"]: row for row in clauses}
    translations = {
        "B1-S020": "Nach dem kurzen Absetzen erwärme den Posten kurz, lasse ihn durch den Lauf und schließe den Schritt.",
        "B4-S005": "Setze die Einlage ein, überführe den Posten und lasse ihn länger darin einwirken; schließe die Vorbereitung.",
        "B4-S006": "Lasse den Posten einmal durch die vorbereitete Einlage; schließe den ersten Durchgang.",
        "B4-S007": "Lasse denselben Posten ein zweites Mal durch; schließe den zweiten Durchgang.",
    }
    clause_rows = []
    for sid in affected_ids:
        row = clause_by_id[sid]
        clause_rows.append({
            "statement_id": sid, "record_unit_id": row["record_unit_id"], "page": row["page"],
            "owner_trace": row["owner_trace"], "atomic_card_chain_de": row["atomic_card_chain_de"],
            "revised_fluent_translation_de": translations[sid],
            "interpretive_link": "SAME_ACTIVE_ITEM" if sid.startswith("B4") else "LOCAL_WARMED_PASSAGE",
        })
    write_tsv("HUNDRED_SIXTY_FIFTH_4_AFFECTED_CLAUSES.tsv", clause_rows)

    passage = [
        "# Revidierte B1-/B4-Passagen", "",
        "## B1 · f81v", "",
        "Nach dem kurzen Absetzen erwärme den Posten kurz, lasse ihn durch den Lauf und schließe den",
        "Schritt. Bringe den so behandelten Posten danach an die bezeichnete Stelle.", "",
        "## B4 · f83r · Doppelpassage", "",
        "Fixiere zuerst die Arbeitsstelle. Setze die Einlage ein, überführe den Posten und lasse ihn",
        "länger darin einwirken. Lasse ihn einmal durch die Einlage und schließe den Durchgang. Lasse",
        "denselben Posten ein zweites Mal durch und schließe auch diesen Durchgang. Bemiss danach den",
        "behandelten Posten, bearbeite ihn länger, halte ihn und schließe mit kurzem Einwirken ab.", "",
        "Die beiden `shckhedy`-Zellen sind damit zwei Durchgänge derselben Operation. Das Wort selbst",
        "bedeutet weiterhin nur `durchlassen; Schluss`; *durch die Einlage* stammt aus der unmittelbar",
        "vorangehenden lokalen Zelle.",
    ]
    (OUT / "HUNDRED_SIXTY_FIFTH_REVISED_B1_B4_PASSAGES.md").write_text("\n".join(passage) + "\n", encoding="utf-8")

    report = [
        "# Hundertfünfundsechzigste Runde: die doppelte B4-Karte ist eine Doppelpassage", "",
        "At f83r.27, F114 prepares one insert and charge: `Einlage | überführen | lange einwirken; Schluss`.",
        "F115 and F116 are separate one-card committed cells containing the identical `shckhedy`. The selected",
        "reading is therefore two sequential passes through the same prepared insert, not two named filters.", "",
        "This preserves the atomic card correction `durchlassen; Schluss`. The insert comes from the preceding",
        "local whole card; it is not smuggled back into MC143. Two separate channels lack a visible distinction.",
        "Dittography remains the live rival, but the deliberate cell separation makes repeat action more useful.", "",
        "Next follow the prepared material after the second pass through B4-S008–S016 and write that entire",
        "downstream sequence as one coherent product/application chain.",
    ]
    (OUT / "HUNDRED_SIXTY_FIFTH_DOUBLE_PASS_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "target_events": len(target_rows), "target_fields": len({row["field_id"] for row in target_rows}),
        "target_loci": len({row["locus"] for row in target_rows}), "models": len(models),
        "selected_model": "TWO_SEQUENTIAL_PASSES_THROUGH_ONE_INSERT",
        "affected_clauses": len(clause_rows), "card_value_changes": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
