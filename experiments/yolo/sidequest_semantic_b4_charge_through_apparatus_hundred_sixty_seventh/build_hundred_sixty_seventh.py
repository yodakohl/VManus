#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R164 = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth"
TARGET_STATEMENTS = [f"B4-S{i:03d}" for i in range(4, 17)]

TRANSLATIONS = {
    "B4-S004": "Fixiere die Arbeitsstelle und schließe die Einrichtung ab.",
    "B4-S005": "Setze die Einlage ein, überführe den Posten und lasse ihn länger darin einwirken; schließe die Vorbereitung.",
    "B4-S006": "Lasse den Posten einmal durch die vorbereitete Einlage; schließe den ersten Durchgang.",
    "B4-S007": "Lasse denselben Posten ein zweites Mal durch; schließe den zweiten Durchgang.",
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
            "page": row["page"], "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "atomic_card_value_de": row["card_value_de"],
            "event_position_in_clause": f"{sequence.index(row) + 1}/{len(sequence)}",
            "terminal_status": row["terminal_status"],
            "complete_clause_translation_de": TRANSLATIONS[row["statement_id"]],
        })
    write_tsv("HUNDRED_SIXTY_SEVENTH_36_EVENT_B4_PROCEDURE.tsv", event_rows)

    clause_rows = []
    for row in clauses:
        statement_events = by_statement[row["statement_id"]]
        clause_rows.append({
            "statement_id": row["statement_id"], "page": row["page"],
            "boundary_from_previous": row["boundary_from_previous"], "owner_trace": row["owner_trace"],
            "visible_surface_sequence": " ".join(event["visible_surface"] for event in statement_events),
            "atomic_card_chain_de": row["atomic_card_chain_de"],
            "fluent_procedure_de": TRANSLATIONS[row["statement_id"]],
            "terminal_status": row["terminal_status"],
        })
    write_tsv("HUNDRED_SIXTY_SEVENTH_13_CLAUSE_B4_PROCEDURE.tsv", clause_rows)

    record_sets = {
        record: {row["master_card_id"] for row in all_events if row["record_unit_id"] == record}
        for record in ("H3", "B2", "B4")
    }
    meanings = {row["master_card_id"]: row["card_value_de"] for row in all_events}
    bridge_rows = []
    for card_id in sorted(record_sets["B2"] & record_sets["B4"]):
        occurrences = {
            record: [row for row in all_events if row["record_unit_id"] == record and row["master_card_id"] == card_id]
            for record in ("H3", "B2", "B4")
        }
        bridge_rows.append({
            "master_card_id": card_id, "atomic_value_de": meanings[card_id],
            "also_in_H3": "YES" if occurrences["H3"] else "NO",
            "H3_events": "|".join(row["event_serial"] for row in occurrences["H3"]) or "NONE",
            "B2_events": "|".join(row["event_serial"] for row in occurrences["B2"]),
            "B4_events": "|".join(row["event_serial"] for row in occurrences["B4"]),
            "bridge_role": "PRODUCT_IDENTITY_BRIDGE" if card_id in {"MC039", "MC119", "MC123"} else "SHARED_APPLICATION_PROCEDURE",
        })
    write_tsv("HUNDRED_SIXTY_SEVENTH_10_B2_B4_CARD_BRIDGES.tsv", bridge_rows)

    comparison = [
        {
            "model": "SECOND_THERAPEUTIC_APPLICATION_RECIPE", "selected": "NO",
            "human_figures": "STRONG", "conduit_insert_double_pass": "MEDIUM", "H3_product_bridge": "STRONG",
            "owner_station_changes": "MEDIUM", "overall_workshop_score": "12/16",
            "reading_de": "Eine zweite Anwendungsvorschrift für denselben oder ähnlichen Pflanzenauszug.",
        },
        {
            "model": "PURE_APPARATUS_MAINTENANCE", "selected": "NO",
            "human_figures": "WEAK", "conduit_insert_double_pass": "STRONG", "H3_product_bridge": "WEAK",
            "owner_station_changes": "STRONG", "overall_workshop_score": "11/16",
            "reading_de": "Einlage warten, Anlage zweimal durchfahren, Leitungen entleeren und neu beschicken.",
        },
        {
            "model": "TREATMENT_CHARGE_THROUGH_LOCAL_APPARATUS", "selected": "YES",
            "human_figures": "STRONG", "conduit_insert_double_pass": "STRONG", "H3_product_bridge": "STRONG",
            "owner_station_changes": "STRONG", "overall_workshop_score": "16/16",
            "reading_de": "Eine bemessene Behandlungscharge wird durch lokale Apparatur vorbereitet und an Zielstellen verteilt.",
        },
    ]
    write_tsv("HUNDRED_SIXTY_SEVENTH_3_PURPOSE_MODELS.tsv", comparison)

    readable = [
        "# B4: eine Behandlungscharge durch lokale Apparatur", "",
        "Die folgende Lesung umfasst B4-S004 bis S016 vollständig.", "",
    ]
    for row in clause_rows:
        readable += [f"- **{row['statement_id']}** — {row['fluent_procedure_de']}"]
    readable += ["", "## Gesamtlesung", "",
                 "Richte die Station ein, setze die Einlage ein und führe die Charge zweimal hindurch.",
                 "Bemiss und vollende das Produkt, ziehe am linken Unterlauf eine Fraktion ab und führe",
                 "den Rest weiter. Gib am rechten Lauf klaren Auszug hinzu und bringe die letzte Portion",
                 "an ihre Zielstelle."]
    (OUT / "HUNDRED_SIXTY_SEVENTH_COMPLETE_B4_PROCEDURE.md").write_text("\n".join(readable) + "\n", encoding="utf-8")

    report = [
        "# Hundertsiebenundsechzigste Runde: B4 ist eine Behandlungscharge durch lokale Apparatur", "",
        "B4-S004–S016 contain 36 events in thirteen clauses. Ten exact shared cards recur in B2 and B4; three of",
        "them also recur in H3: `Sollmaß`, `Klarauszug`, and `dies/current item`. B2 and B4 additionally share long",
        "exposure, portion addition, insertion, settling, target placement and drainage.", "",
        "A pure second therapy recipe explains the human figures and product bridge but underplays the insert and",
        "double pass. Pure maintenance explains the apparatus but underplays measured clear extract and application",
        "targets. The selected synthesis is a treatment charge prepared through local apparatus and then delivered.", "",
        "Next search the four Herbal records for which pictured article most naturally supplies the B4 charge. Use",
        "only the existing four plant images and the current atomic cards; make one concrete nomination and one",
        "strong rival rather than leaving every plant equally possible.",
    ]
    (OUT / "HUNDRED_SIXTY_SEVENTH_B4_PURPOSE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "events": len(event_rows), "clauses": len(clause_rows), "B2_B4_bridge_cards": len(bridge_rows),
        "H3_B2_B4_bridge_cards": sum(row["also_in_H3"] == "YES" for row in bridge_rows),
        "purpose_models": len(comparison), "selected_model": "TREATMENT_CHARGE_THROUGH_LOCAL_APPARATUS",
        "untranslated_events": 0, "untranslated_clauses": 0, "card_value_changes": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
