#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R134 = EXP / "yolo" / "sidequest_semantic_current_ten_page_edition_hundred_thirty_fourth"
R135 = EXP / "yolo" / "sidequest_semantic_period_phrase_order_hundred_thirty_fifth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SHORTER = {
    "MC002": "lange einwirken",
    "MC004": "abziehen; Schluss",
    "MC005": "einführen; Schluss",
    "MC007": "kurz einwirken",
    "MC012": "Zusatz",
    "MC013": "Folgeansatz",
    "MC017": "Anteil zugeben",
    "MC025": "überführen; Schluss",
    "MC028": "weiterführen; Schluss",
    "MC034": "weitere Zutat",
    "MC035": "durchleiten",
    "MC045": "lange sammeln; Schluss",
    "MC060": "Folgemaß",
    "MC082": "lange einwirken; Schluss",
    "MC083": "kurz einwirken; Schluss",
    "MC088": "einführen; Schluss",
    "MC093": "danach dorthin",
    "MC103": "weiterbearbeiten",
    "MC105": "Anteil",
    "MC128": "kurz absetzen; Schluss",
    "MC142": "vom vorigen",
    "MC143": "seihen; Schluss",
    "MC147": "kurz wärmen",
    "MC155": "abführen; Schluss",
}


JOB_TEXTS = {
    "J1_ROOT_AND_LEAF_BASIN": "Wurzel und Blatt nehmen; zerkleinern; Auszug ansetzen; bemessen; dorthin einsetzen; waschen; kurz wärmen; absetzen; abführen; fertig.",
    "J2_CLEAR_EXTRACT_STATIONS": "Blüte und Blatt nehmen; auswringen; stehen lassen; nachseihen; Klarauszug nehmen; dorthin einsetzen; einwirken lassen; abziehen; abführen; fertig.",
    "J3_BOUND_APPLICATION_SERVICE": "Ansatz bemessen; davon Anteil nehmen; dorthin einsetzen; Tuch anlegen; festmachen; waschen; absetzen; Klarauszug sammeln; Rest abführen; fertig.",
    "J4_FRESH_PLANT_LONG_ROUTE": "Frisches Kraut nehmen; Waschung ansetzen; zweiten Anteil zurückhalten; Auszug gewinnen; bemessen; überführen; wärmen; absetzen; sammeln; Klarauszug nehmen; fertig.",
}


def main():
    cards = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv")
    surfaces = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_230_SURFACE_REVERSE_KEY.tsv")
    events = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_381_PROSE_EVENTS.tsv")
    old_statements = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_116_PROSE_STATEMENTS.tsv")
    jobs = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_FOUR_JOBS.tsv")
    proposals = read_tsv(R135 / "HUNDRED_THIRTY_FIFTH_41_ACTIVE_CARD_REVISIONS.tsv")
    overlay = {r["master_card_id"]: r["period_sized_default_de"] for r in proposals}
    overlay.update(SHORTER)

    out_cards = []
    for row in cards:
        new = overlay.get(row["master_card_id"], row["current_spoken_default_de"])
        out_cards.append({**row, "previous_default_de": row["current_spoken_default_de"], "current_spoken_default_de": new,
                          "period_revision": "SHORTENED_ACTIVE_CARD" if new != row["current_spoken_default_de"] else "UNCHANGED"})
    by_card = {r["master_card_id"]: r for r in out_cards}

    out_surfaces = []
    for row in surfaces:
        out_surfaces.append({**row, "current_spoken_default_de": by_card[row["master_card_id"]]["current_spoken_default_de"]})
    out_events = []
    for row in events:
        out_events.append({**row, "previous_default_de": row["current_spoken_default_de"],
                           "current_spoken_default_de": by_card[row["master_card_id"]]["current_spoken_default_de"]})

    events_by_statement = defaultdict(list)
    for row in out_events:
        events_by_statement[row["statement_id"]].append(row)
    out_statements = []
    for row in old_statements:
        chain = [r["current_spoken_default_de"] for r in events_by_statement[row["statement_id"]]]
        out_statements.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "period_sized_card_chain_de": " | ".join(chain),
            "terse_workshop_clause_de": "; ".join(chain).rstrip(".; ") + ".",
            "previous_fluent_expansion_de": row["continuous_working_reading_de"],
        })

    by_record = defaultdict(list)
    for row in out_statements:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    for rid, group in by_record.items():
        record_rows.append({
            "record_unit_id": rid,
            "page": group[0]["page"],
            "statement_count": str(len(group)),
            "event_count": str(sum(len(events_by_statement[r["statement_id"]]) for r in group)),
            "continuous_period_sized_record_de": " ".join(r["terse_workshop_clause_de"] for r in group),
        })

    job_rows = []
    for row in jobs:
        job_rows.append({
            "job_id": row["job_id"],
            "title_de": row["title_de"],
            "what_records": row["what_records"],
            "how_records": row["how_records"],
            "prose_event_count": row["prose_event_count"],
            "optional_when_de": row["selected_when_condition_de"],
            "period_sized_work_order_de": JOB_TEXTS[row["job_id"]],
        })

    write_tsv("HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv", out_cards)
    write_tsv("HUNDRED_THIRTY_SIXTH_230_SURFACE_REVERSE_KEY.tsv", out_surfaces)
    write_tsv("HUNDRED_THIRTY_SIXTH_381_PROSE_EVENTS.tsv", out_events)
    write_tsv("HUNDRED_THIRTY_SIXTH_116_TERSE_STATEMENTS.tsv", out_statements)
    write_tsv("HUNDRED_THIRTY_SIXTH_11_TERSE_RECORDS.tsv", record_rows)
    write_tsv("HUNDRED_THIRTY_SIXTH_FOUR_TERSE_JOBS.tsv", job_rows)

    edition = ["# Periodengroße Werkstattausgabe", "", "The text below is intentionally terse. One learned card",
               "contributes one prompt, object, state or relation; picture and active registers restore omitted nouns.", ""]
    for job in job_rows:
        edition += [f"## {job['job_id']} · {job['title_de']}", "", f"WANN (optional): {job['optional_when_de']}", "",
                    f"AUFTRAG: {job['period_sized_work_order_de']}", ""]
        for rid in (job["what_records"] + "|" + job["how_records"]).split("|"):
            rec = next(r for r in record_rows if r["record_unit_id"] == rid)
            edition += [f"### {rid} · {rec['page']}", "", rec["continuous_period_sized_record_de"], ""]
    (OUT / "HUNDRED_THIRTY_SIXTH_COMPLETE_TERSE_EDITION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertsechsunddreißigste Runde: kurze Wörter, lange Handlungen", "",
        "The R135 period-sized meanings are now propagated through the current edition. All 173 cards, 230",
        "visible spellings, 381 events, 116 statements, eleven records and four jobs remain present. Twenty-nine",
        "active card defaults became shorter; specialist whole-card defaults remain concrete and unchanged.", "",
        "The key gain is grammatical. `char chety` now reads `davon | Anteil`; `okaiin` is `bemessen`;",
        "`checthy chety otaiin` is `bereit | Anteil | Folgemaß`; terminal `oldy` is simply `fertig`. The current",
        "item is supplied by the register, so `choky`, `chdy`, `chey` become `einsetzen`, `überführen`, `dies`.", "",
        "The four work orders can now be said aloud as short workshop clauses. Their fuller medical or technical",
        "readings remain expansions of these prompts, not dictionary entries. Next use the new 116-clause edition",
        "to find where a card is still acting as two incompatible parts of speech or where two cards now look like",
        "a genuine compositional pair.",
    ]
    (OUT / "HUNDRED_THIRTY_SIXTH_PERIOD_SIZED_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "cards": len(out_cards), "surfaces": len(out_surfaces), "events": len(out_events),
               "statements": len(out_statements), "records": len(record_rows), "jobs": len(job_rows),
               "changed_cards": sum(r["period_revision"] == "SHORTENED_ACTIVE_CARD" for r in out_cards)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
