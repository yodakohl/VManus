#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R164 = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth"
TARGET_STATEMENTS = [f"B4-S{i:03d}" for i in range(8, 17)]

PHASES = {
    **{f"B4-S{i:03d}": "I_POST_PASS_FINISH" for i in range(8, 11)},
    **{f"B4-S{i:03d}": "II_LEFT_LOWER_RUN_FRACTION" for i in range(11, 15)},
    **{f"B4-S{i:03d}": "III_RIGHT_S_RUN_APPLICATION" for i in range(15, 17)},
}

TRANSLATIONS = {
    "B4-S008": "Bemiss den doppelt durchgelassenen Posten, bearbeite ihn länger, halte ihn über die lange Stufe und lasse ihn kurz einwirken; schließe den Schritt.",
    "B4-S009": "Lasse den Posten kurz absetzen und schließe den Schritt.",
    "B4-S010": "Markiere den so behandelten Posten als fertig.",
    "B4-S011": "An der linken Unterlaufstation bemiss die Sollmenge, erwärme sie kurz, führe sie über die lange Fortsetzung, gib einen Anteil zu, überführe sie weiter und ziehe eine kleine Fraktion ab.",
    "B4-S012": "Führe den verbleibenden Posten ab und schließe den Schritt.",
    "B4-S013": "Setze die Weiterfraktion ein, lasse sie kurz absetzen und schließe den Schritt.",
    "B4-S014": "Nimm den Ansatz als laufenden Posten, führe ihn durch den kurzen Gang und bis zum Ende dieses Laufs.",
    "B4-S015": "Beim Übergang zur rechten S-Laufstation gib eine Portion des klaren Auszugs zu, führe den Anteil durch die Zielpassage, sammle ihn kurz und führe ihn ab.",
    "B4-S016": "Nimm einen weiteren Anteil, bringe ihn an die Zielstelle, gieße aus der Quelle zu und lasse ihn kurz absetzen; schließe die Folge.",
}


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
    all_events = read_tsv(R164 / "HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv")
    all_clauses = read_tsv(R164 / "HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv")
    events = [row for row in all_events if row["statement_id"] in TARGET_STATEMENTS]
    clauses = [row for row in all_clauses if row["statement_id"] in TARGET_STATEMENTS]
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    event_rows = []
    for row in events:
        sequence = by_statement[row["statement_id"]]
        event_rows.append({
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "workflow_phase": PHASES[row["statement_id"]],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "atomic_card_value_de": row["card_value_de"],
            "event_position_in_clause": f"{sequence.index(row) + 1}/{len(sequence)}",
            "terminal_status": row["terminal_status"],
            "complete_clause_translation_de": TRANSLATIONS[row["statement_id"]],
        })
    write_tsv("HUNDRED_SIXTY_SIXTH_30_EVENT_B4_DOWNSTREAM.tsv", event_rows)

    clause_rows = []
    for row in clauses:
        statement_events = by_statement[row["statement_id"]]
        clause_rows.append({
            "statement_id": row["statement_id"], "page": row["page"],
            "workflow_phase": PHASES[row["statement_id"]],
            "boundary_from_previous": row["boundary_from_previous"], "owner_trace": row["owner_trace"],
            "visible_surface_sequence": " ".join(event["visible_surface"] for event in statement_events),
            "atomic_card_chain_de": row["atomic_card_chain_de"],
            "fluent_downstream_translation_de": TRANSLATIONS[row["statement_id"]],
            "terminal_status": row["terminal_status"],
        })
    write_tsv("HUNDRED_SIXTY_SIXTH_9_CLAUSE_B4_DOWNSTREAM.tsv", clause_rows)

    phase_rows = []
    for phase in dict.fromkeys(PHASES.values()):
        rows = [row for row in clause_rows if row["workflow_phase"] == phase]
        phase_rows.append({
            "workflow_phase": phase, "statement_count": str(len(rows)),
            "event_count": str(sum(len(by_statement[row["statement_id"]]) for row in rows)),
            "owner_trace": " -> ".join(dict.fromkeys(row["owner_trace"] for row in rows)),
            "continuous_phase_de": " ".join(row["fluent_downstream_translation_de"] for row in rows),
        })
    write_tsv("HUNDRED_SIXTY_SIXTH_3_B4_DOWNSTREAM_PHASES.tsv", phase_rows)

    readable = [
        "# B4 nach dem Doppelpass: Produkt, Unterlauf, Zielstation", "",
        "## I. Produkt nach dem zweiten Durchgang", "",
        phase_rows[0]["continuous_phase_de"], "",
        "## II. Linke Unterlaufstation", "",
        phase_rows[1]["continuous_phase_de"], "",
        "## III. Rechte S-Laufstation", "",
        phase_rows[2]["continuous_phase_de"], "",
        "## Gesamtlesung", "",
        "Nach dem doppelten Durchlassen wird der Posten bemessen, nachbearbeitet, gehalten und abgesetzt.",
        "Eine kleine Fraktion wird am linken Unterlauf abgezogen; der Rest wird abgeführt. Der klare",
        "Auszug wird anschließend am rechten S-Lauf portioniert, zur Zielstelle gebracht und dort kurz",
        "abgesetzt.",
    ]
    (OUT / "HUNDRED_SIXTY_SIXTH_COMPLETE_B4_DOWNSTREAM.md").write_text("\n".join(readable) + "\n", encoding="utf-8")

    report = [
        "# Hundertsechsundsechzigste Runde: der B4-Nachlauf wird eine Produkt- und Anwendungskette", "",
        "B4-S008 through S016 contain exactly 30 events in nine clauses. Read after the double pass, they form",
        "three practical phases: finish and settle the passed product; warm, extend and draw a fraction at the",
        "left lower run; then add clarified extract, collect briefly and place the final portion at the right S-run.", "",
        "The image-owner changes are respected. No global direction is inferred: 'left lower run' and 'right",
        "S-run' are local addresses, while source, target and clear extract are supplied by their exact cards.", "",
        "Next join B4-S004–S016 into a single twelve-clause procedure and compare it with the complete H3→B2",
        "master day. The key question is whether B4 is a second application recipe or maintenance of the same",
        "apparatus grammar.",
    ]
    (OUT / "HUNDRED_SIXTY_SIXTH_B4_DOWNSTREAM_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "events": len(event_rows), "clauses": len(clause_rows), "phases": len(phase_rows),
        "first_event": event_rows[0]["event_serial"], "last_event": event_rows[-1]["event_serial"],
        "untranslated_events": 0, "untranslated_clauses": 0, "card_value_changes": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
