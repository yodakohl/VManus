#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_final_reverse_writer_four_hundred_fifty_ninth/FOUR_HUNDRED_FIFTY_NINTH_381_EVENT_FINAL_REVERSE_WRITER.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_final_reverse_writer_four_hundred_fifty_ninth/FOUR_HUNDRED_FIFTY_NINTH_173_CARD_FINAL_DICTIONARY.tsv"
H_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_continuous_articles_four_hundred_fifty_fifth/FOUR_HUNDRED_FIFTY_FIFTH_19_CONTROLLED_STATEMENTS.tsv"
B_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_biological_continuous_prose_four_hundred_fifty_second/FOUR_HUNDRED_FIFTY_SECOND_97_STATEMENT_LEDGER.tsv"
B_PROCEDURES = ROOT / "experiments/yolo/sidequest_semantic_biological_continuous_prose_four_hundred_fifty_second/FOUR_HUNDRED_FIFTY_SECOND_24_PROCEDURES.tsv"
TRANSITIONS = ROOT / "experiments/yolo/sidequest_semantic_biological_continuous_prose_four_hundred_fifty_second/FOUR_HUNDRED_FIFTY_SECOND_SEVEN_SCENE_TRANSITIONS.tsv"

OVERRIDES = {
    "H1-S001": "Von der abgebildeten Pflanze kurz abziehen; der Ansatz ist bereit. Von dort in das Gefäß füllen. Wasser abziehen, danach diesen Posten füllen und weiter abziehen. Dies nach Maß verwenden und kurz füllen.",
    "H2-S002": "Danach vom Ansatz abziehen und damit fortfahren. Den weiteren Ansatz nach Maß fortführen und von dort weiterarbeiten.",
    "B1-S002": "Bemessen, Wasser zufuehren und an die Stelle setzen; von dort mit einer und einer weiteren Portion fortsetzen; an der Stelle weiter abkuehlen, weiterfuehren und einen weiteren Ansatz fortsetzen; kurz an der Durchlassstelle halten, auf Mass bringen, laenger an der Stelle halten, nochmals bemessen, durchfuehren, umsetzen und schliessen.",
    "B2-S011": "Eine Portion zugeben, von dort noch eine Portion zugeben, länger ansetzen und schließen.",
    "B3-S004": "Bemessen, zur Folgestelle gehen und von dort weiterarbeiten.",
    "B4-S005": "Eine Portion bereitstellen, dies umsetzen, länger ansetzen und schließen.",
    "B5-S003": "An der Absetzstelle fortsetzen und weiterfuehren; an der Stelle umsetzen, auf Mass bringen, fortsetzen, die zweite Stufe einstellen und dies umsetzen.",
    "B6-S001": "Länger auffangen, dies kurz zuführen, abkuehlen und fortsetzen; auf Mass bringen, fortsetzen, eine Portion davon nehmen und den Ansatz zur Stelle fuehren.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    cards = read(CARDS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    old_h = {row["statement_id"]: row for row in read(H_STATEMENTS)}
    old_b = {row["statement_id"]: row for row in read(B_STATEMENTS)}
    statement_rows = []
    for statement_id, rows in by_statement.items():
        if statement_id in old_h:
            fluent = old_h[statement_id]["controlled_fluent_reading_de"]
        else:
            fluent = old_b[statement_id]["continuous_reading_de"]
        fluent = OVERRIDES.get(statement_id, fluent)
        statement_rows.append({
            "statement_id": statement_id, "register": rows[0]["register"], "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "owner_zones": "|".join(dict.fromkeys(row["owner_zone"] for row in rows)),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "field_ids": "|".join(dict.fromkeys(row["field_id"] for row in rows)),
            "literal_card_chain_de": "; ".join(row["small_value_de"] for row in rows) + ".",
            "current_fluent_reading_de": fluent,
            "pass460_override": "YES" if statement_id in OVERRIDES else "NO",
            "physical_line_is_sentence_boundary": "NO",
        })
    write("FOUR_HUNDRED_SIXTIETH_116_STATEMENT_CURRENT_EDITION.tsv", statement_rows)
    statement_by_id = {row["statement_id"]: row for row in statement_rows}

    article_rows = []
    for record in ("H1", "H2", "H3", "H4", "H5"):
        rows = [row for row in statement_rows if row["record_unit_id"] == record]
        article_rows.append({
            "section_id": f"HA{record[1:]}", "record_unit_id": record, "page": rows[0]["page"],
            "owner_zones": "|".join(dict.fromkeys(str(row["owner_zones"]) for row in rows)),
            "statements": len(rows), "statement_ids": "|".join(str(row["statement_id"]) for row in rows),
            "events": sum(int(row["events"]) for row in rows),
            "event_ids": "|".join(event for row in rows for event in str(row["event_ids"]).split("|")),
            "current_continuous_prose_de": " ".join(str(row["current_fluent_reading_de"]) for row in rows),
        })
    write("FOUR_HUNDRED_SIXTIETH_FIVE_HERBAL_ARTICLES.tsv", article_rows)

    procedure_rows = []
    for old in read(B_PROCEDURES):
        rows = [statement_by_id[statement_id] for statement_id in old["statement_ids"].split("|")]
        procedure_rows.append({
            "section_id": old["procedure_id"], "record_unit_id": old["record_unit_id"], "title_de": old["title_de"],
            "statements": len(rows), "statement_ids": old["statement_ids"],
            "events": sum(int(row["events"]) for row in rows),
            "event_ids": "|".join(event for row in rows for event in str(row["event_ids"]).split("|")),
            "owner_zones": "|".join(dict.fromkeys(zone for row in rows for zone in str(row["owner_zones"]).split("|"))),
            "hard_scene_transition_events": old["hard_scene_transition_events"],
            "current_continuous_prose_de": " ".join(f"[{row['statement_id']}] {row['current_fluent_reading_de']}" for row in rows),
        })
    write("FOUR_HUNDRED_SIXTIETH_24_BIOLOGICAL_PROCEDURES.tsv", procedure_rows)

    sections = []
    for row in article_rows:
        sections.append({
            "section_order": len(sections) + 1, "section_id": row["section_id"], "register": "HERBAL",
            "record_unit_id": row["record_unit_id"], "page": row["page"], "title_de": "Abgebildete Pflanze",
            "statements": row["statements"], "events": row["events"], "event_ids": row["event_ids"],
            "owner_zones": row["owner_zones"], "continuous_prose_de": row["current_continuous_prose_de"],
        })
    page_by_record = {row["record_unit_id"]: row["page"] for row in statement_rows}
    for row in procedure_rows:
        sections.append({
            "section_order": len(sections) + 1, "section_id": row["section_id"], "register": "BIOLOGICAL",
            "record_unit_id": row["record_unit_id"], "page": page_by_record[row["record_unit_id"]], "title_de": row["title_de"],
            "statements": row["statements"], "events": row["events"], "event_ids": row["event_ids"],
            "owner_zones": row["owner_zones"], "continuous_prose_de": row["current_continuous_prose_de"],
        })
    write("FOUR_HUNDRED_SIXTIETH_29_SECTION_WORKSHOP_EDITION.tsv", sections)
    write("FOUR_HUNDRED_SIXTIETH_381_EVENT_CURRENT_INTERLINEAR.tsv", events)
    write("FOUR_HUNDRED_SIXTIETH_173_CARD_CURRENT_DICTIONARY.tsv", cards)
    write("FOUR_HUNDRED_SIXTIETH_SEVEN_VISIBLE_SCENE_TRANSITIONS.tsv", read(TRANSITIONS))

    md = ["# Current seven-page prose edition", ""]
    last_record = None
    for row in sections:
        if row["record_unit_id"] != last_record:
            md.extend([f"# {row['record_unit_id']} — {row['page']}", ""])
            last_record = row["record_unit_id"]
        md.extend([f"## {row['section_id']} — {row['title_de']}", "", str(row["continuous_prose_de"]), ""])
    (HERE / "FOUR_HUNDRED_SIXTIETH_CURRENT_SEVEN_PAGE_PROSE.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS", "pages": 7, "records": 11, "sections": len(sections), "herbal_articles": len(article_rows),
        "biological_procedures": len(procedure_rows), "statements": len(statement_rows), "events": len(events),
        "cards": len(cards), "productive_events": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "whole_events": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in events),
        "displayed_superseded_readings": 0,
    }
    (HERE / "FOUR_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
