#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R156 = ROOT / "experiments/yolo/sidequest_semantic_atomic_current_ten_page_hundred_fifty_sixth"
TARGET_RECORDS = ["H3", "B2"]

PHASES = {
    "H3-S001": "I_EXTRACT_PREPARATION",
    "H3-S002": "II_SECOND_PORTION",
    "H3-S003": "II_SECOND_PORTION",
    "H3-S004": "II_SECOND_PORTION",
    **{f"B2-S{i:03d}": "III_UPPER_DOUBLE_BASIN" for i in range(1, 7)},
    **{f"B2-S{i:03d}": "IV_MIDDLE_LEFT_CLARIFICATION" for i in range(7, 11)},
    **{f"B2-S{i:03d}": "V_MIDDLE_RIGHT_TO_LOWER_FIELD" for i in range(11, 15)},
    **{f"B2-S{i:03d}": "VI_LOWER_EDGE_WASH_AND_DRAIN" for i in range(15, 23)},
}

TRANSLATIONS = {
    "H3-S001": "Nimm von der blau bekrönten Bildpflanze das Kochgut. Setze daraus einen Sud an, wringe ihn aus, lasse ihn die vorgeschriebene Zeit stehen, seihe nochmals und behalte den klaren Auszug; gib zuletzt den Endzusatz bei.",
    "H3-S002": "Lege den weiteren Zugabeteil bereit.",
    "H3-S003": "Nimm diesen Teil aus dem vorigen Ansatz, bearbeite ihn und bringe ihn auf das vorgeschriebene Maß.",
    "H3-S004": "Nimm danach den folgenden Posten, verarbeite ihn weiter und halte ihn als bereiten Arbeitsposten verfügbar.",
    "B2-S001": "Überführe den bereiteten Ansatz in die obere Doppelbecken- und Zylinderstation; schließe den Schritt.",
    "B2-S002": "Führe den Ansatz in derselben oberen Station weiter; schließe den Schritt.",
    "B2-S003": "Gib eine Portion zum laufenden Posten und lasse sie länger einwirken; schließe den Schritt.",
    "B2-S004": "Setze den Posten an der bezeichneten Stelle ein, führe ihn durch den Abführgang, lasse ihn weiter einwirken und trenne den Ablauf ab.",
    "B2-S005": "Setze die nächste Menge am Ziel ein, sammle bis zur Sollmenge, führe sie durch, bemiss sie zweimal, bereite die Fortsetzung vor, halte sie länger warm und ziehe sie ab.",
    "B2-S006": "Im langen Folgeschritt setze den Posten dort ein, führe ihn kurz durch und bringe ihn in den laufenden Arbeitsgang.",
    "B2-S007": "An der mittleren linken Gerätestation lasse den Posten kurz absetzen; schließe den Schritt.",
    "B2-S008": "Nimm für den Folgeschritt das bemessene Gut aus der Quelle und lasse es kurz absetzen.",
    "B2-S009": "Lasse eine weitere Absetzung folgen; schließe den Schritt.",
    "B2-S010": "Lasse den Posten länger einwirken, setze ihn ein, leite ihn zum Auslass und behalte den klaren Auszug.",
    "B2-S011": "An der mittleren rechten Liege- oder Linienstation gib eine Portion zu, nimm davon eine zweite Portion und lasse beide länger einwirken.",
    "B2-S012": "Nimm das abgeführte Gut und den klaren Auszug, bereite sie kurz vor, lasse sie länger einwirken, ziehe die klare Fraktion ab, bemiss sie und setze den ganzen Posten im unteren Feld ein.",
    "B2-S013": "Führe den verbrauchten Posten aus dem unteren Feld ab; schließe den Schritt.",
    "B2-S014": "Nimm den Abzug aus der Quelle für den nächsten Schritt auf.",
    "B2-S015": "An den Randstationen führe den Abzug bis zum klaren Lauf und lasse ihn länger einwirken.",
    "B2-S016": "Bringe ihn an die bezeichnete Stelle, führe aus der Quelle ab, teile nach Sollmaß, bemiss die lange Folge, lasse sie kurz einwirken und führe sie dem Ziel zu.",
    "B2-S017": "Halte den Posten kurz am Ziel und schließe dort ab.",
    "B2-S018": "Lasse den nächsten Posten länger einwirken; schließe den Schritt.",
    "B2-S019": "Schließe den Waschgang ab.",
    "B2-S020": "Halte die folgende Stufe länger; schließe den Schritt.",
    "B2-S021": "Lasse den letzten behandelten Posten länger einwirken; schließe den Schritt.",
    "B2-S022": "Führe den Rest ab und schließe die Stationsfolge.",
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
    all_events = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv")
    all_clauses = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_116_ATOMIC_CLAUSES.tsv")
    events = [row for row in all_events if row["record_unit_id"] in TARGET_RECORDS]
    clauses = [row for row in all_clauses if row["record_unit_id"] in TARGET_RECORDS]
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
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "atomic_card_value_de": row["card_value_de"],
            "event_position_in_clause": f"{sequence.index(row) + 1}/{len(sequence)}",
            "teaching_layer": row["teaching_layer"], "terminal_status": row["terminal_status"],
            "complete_clause_translation_de": TRANSLATIONS[row["statement_id"]],
        })
    write_tsv("HUNDRED_SIXTY_THIRD_79_EVENT_MASTER_DAY_INTERLINEAR.tsv", event_rows)

    clause_rows = []
    for row in clauses:
        statement_events = by_statement[row["statement_id"]]
        clause_rows.append({
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "workflow_phase": PHASES[row["statement_id"]],
            "boundary_from_previous": row["boundary_from_previous"], "visible_owner": row["owner_trace"],
            "visible_surface_sequence": " ".join(event["visible_surface"] for event in statement_events),
            "atomic_card_chain_de": row["atomic_card_chain_de"],
            "fluent_workshop_translation_de": TRANSLATIONS[row["statement_id"]],
            "terminal_status": row["terminal_status"],
            "speculative_day_link": "WORKSHOP_SCENARIO_NOT_VISIBLE_CROSS_PAGE_POINTER",
        })
    write_tsv("HUNDRED_SIXTY_THIRD_26_CLAUSE_MASTER_DAY_EDITION.tsv", clause_rows)

    phase_rows = []
    for phase in dict.fromkeys(PHASES.values()):
        rows = [row for row in clause_rows if row["workflow_phase"] == phase]
        phase_rows.append({
            "workflow_phase": phase, "source_records": "|".join(dict.fromkeys(row["record_unit_id"] for row in rows)),
            "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
            "statement_count": str(len(rows)),
            "event_count": str(sum(len(by_statement[row["statement_id"]]) for row in rows)),
            "continuous_phase_reading_de": " ".join(row["fluent_workshop_translation_de"] for row in rows),
        })
    write_tsv("HUNDRED_SIXTY_THIRD_6_WORKFLOW_PHASES.tsv", phase_rows)

    book = [
        "# Ein vollständiger Werkstatttag: Auszug und Stationsfolge", "",
        "Diese Lesung verbindet H3/f11r und B2/f82r als Lehrszenario eines Meisters. Der Übergang",
        "vom Pflanzenartikel zur Anwendung ist eine praktische Arbeitshypothese, kein sichtbarer",
        "Querverweis im Manuskript.", "",
    ]
    for phase in phase_rows:
        book += [f"## {phase['workflow_phase']}", "", phase["continuous_phase_reading_de"], ""]
    book += ["## Kurze Gesamtlesung", "",
             "Bereite aus der abgebildeten Pflanze einen klaren, bemessenen Auszug. Überführe ihn in",
             "die obere Beckenstation, teile, wärme, lasse einwirken und trenne den Ablauf. Kläre ihn",
             "an der mittleren Station, setze die bemessene Fraktion im unteren Feld ein, wasche an den",
             "Randstationen nach und führe den Rest ab."]
    (OUT / "HUNDRED_SIXTY_THIRD_COMPLETE_MASTER_DAY.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertdreiundsechzigste Runde: ein durchgehend lesbarer Werkstatttag", "",
        "H3 contributes 17 visible events in four clauses; B2 contributes 62 events in 22 clauses. Every token",
        "appears once in a six-phase reading: prepare and clarify a pictured-plant extract, ready a second portion,",
        "charge the upper double basin, clarify at the middle-left station, apply at the middle-right/lower field,",
        "then wash and drain at the lower edge stations.", "",
        "The combined story is intentionally concrete. It makes the strongest current content bet: the Herbal",
        "article can supply a prepared extract used by a Biological bath/station workflow. The cross-page handoff",
        "is not written on either page, so it remains a master-day scenario rather than a decoded pointer.", "",
        "Next test this vocabulary against the remaining three Herbal records and five Biological records by asking",
        "which whole-card values cause the sharpest contradiction with this master-day process, then revise only",
        "those values rather than rewriting the whole dictionary.",
    ]
    (OUT / "HUNDRED_SIXTY_THIRD_MASTER_DAY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "records": len(TARGET_RECORDS), "pages": 2, "events": len(event_rows), "clauses": len(clause_rows),
        "workflow_phases": len(phase_rows),
        "H3_events": sum(row["record_unit_id"] == "H3" for row in event_rows),
        "B2_events": sum(row["record_unit_id"] == "B2" for row in event_rows),
        "H3_clauses": sum(row["record_unit_id"] == "H3" for row in clause_rows),
        "B2_clauses": sum(row["record_unit_id"] == "B2" for row in clause_rows),
        "untranslated_events": 0, "untranslated_clauses": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
