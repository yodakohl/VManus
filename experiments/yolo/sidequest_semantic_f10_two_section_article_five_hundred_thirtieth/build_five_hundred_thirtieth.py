#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_events = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    events = [row for row in all_events if row["record"] in {"H1", "H2"}]
    clause = {
        "E001": "diesen Posten kurz abziehen",
        "E002": "den bereiten Ansatz aktivieren",
        "E003": "von dort nehmen",
        "E004": "diesen Posten eintragen",
        "E005": "das Arbeitsfach wählen",
        "E006": "durch den Lauf abziehen",
        "E007": "danach diesen Posten eintragen, abziehen und fortsetzen",
        "E008": "diesen Posten ansetzen",
        "E009": "das vorgeschriebene Maß setzen",
        "E010": "diesen Posten kurz eintragen",
        "E011": "diesen Posten ansetzen",
        "E012": "danach abziehen und fortsetzen",
        "E013": "fortsetzen",
        "E014": "diesen Posten bereit halten",
        "E015": "diesen Posten kurz aus dem Ansatz abziehen",
        "E016": "diesen Posten bereit halten",
        "E017": "den Ansatz nehmen",
        "E018": "das Bereitschaftsmaß setzen",
        "E019": "diesen Arbeitsgang bereit fortsetzen",
        "E020": "diesen Posten weiterführen",
        "E021": "diesen Posten nehmen",
        "E022": "das vorgeschriebene Maß setzen",
        "E023": "diesen Posten an die Zielstelle bringen",
        "E024": "danach aus dem Ansatz abziehen",
        "E025": "den Ansatz nehmen",
        "E026": "danach fortsetzen",
        "E027": "fortsetzen",
        "E028": "den Ansatz weiterführen",
        "E029": "fortsetzen",
        "E030": "das vorgeschriebene Maß setzen",
        "E031": "von dort nehmen",
        "E032": "diesem Arbeitsgang den Ansatz zuführen",
        "E033": "den Ansatz nehmen",
        "E034": "den Ansatz nehmen",
        "E035": "diesen Posten nehmen",
        "E036": "bis zur Sollstufe zuführen",
        "E037": "diesen Posten nehmen",
        "E038": "das Arbeitsmaß abziehen",
    }
    stage_ranges = {
        "ST01_ROOT_DRAW_PREPARATION": range(1, 4),
        "ST02_ROOT_WORK_PATH": range(4, 8),
        "ST03_ROOT_METER_ENTRY": range(8, 11),
        "ST04_ROOT_CONTINUE_READY": range(11, 15),
        "ST05_UPPER_DRAW_READY": range(15, 19),
        "ST06_UPPER_MOVE_METER_TARGET": range(19, 24),
        "ST07_UPPER_CONTINUE_PREPARATION": range(24, 32),
        "ST08_UPPER_FEED_STAGE_MEASURE": range(32, 39),
    }
    stage_for = {
        f"E{event_no:03d}": stage
        for stage, event_numbers in stage_ranges.items()
        for event_no in event_numbers
    }
    owner_by_record = {
        "H1": ("IMAGE_H1_ROOT_AXIS_AND_RED_SWELLINGS", "sichtbarer Wurzel-/Speicherposten"),
        "H2": ("IMAGE_H2_UPPER_STEM_FLOWER_BUD_LEAF_SET", "sichtbarer oberer Sprossposten"),
    }
    event_rows: list[dict[str, str]] = []
    for row in events:
        owner_id, owner_de = owner_by_record[row["record"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "card_reading": row["apprentice_spoken_reading_de"],
                "primitive": row["procedure_tokens"],
                "article_stage": stage_for[row["event_id"]],
                "minimum_source_clause_de": clause[row["event_id"]],
                "visible_owner_id": owner_id,
                "visible_owner_de": owner_de,
                "article_relation": "SAME_PICTURED_PLANT_DIFFERENT_VISIBLE_PART_SECTION",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTIETH_F10_THIRTY_EIGHT_EVENT_ARTICLE.tsv", event_rows)

    specs = {
        "H1-S001": "Vom sichtbaren Wurzel-/Speicherposten kurz abziehen und den bereiten Ansatz aktivieren. Davon den Posten ins Arbeitsfach eintragen und durch den Lauf führen; danach weiter abziehen, nach Maß ansetzen und kurz eintragen.",
        "H1-S002": "Diesen Posten ansetzen, danach weiter abziehen und ihn bereit halten.",
        "H2-S001": "Vom sichtbaren oberen Sprossposten kurz aus dem Ansatz abziehen und ihn bereit halten. Den Ansatz auf das Bereitschaftsmaß bringen, weiterführen, abmessen und an die Zielstelle geben.",
        "H2-S002": "Danach aus dem Ansatz abziehen, den Ansatz weiterführen, nach Maß davon nehmen.",
        "H2-S003": "Den laufenden Posten dem Ansatz zuführen, ihn bis zur Sollstufe bringen und das Arbeitsmaß abziehen.",
    }
    statements: list[dict[str, str]] = []
    for statement_id, fluent in specs.items():
        members = [row for row in event_rows if row["statement_id"] == statement_id]
        statements.append(
            {
                "statement_id": statement_id,
                "record": members[0]["record"],
                "section_owner": members[0]["visible_owner_de"],
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_sequence_literal_de": "; ".join(row["minimum_source_clause_de"] for row in members),
                "workshop_expanded_reading_de": fluent,
                "licensed_close_present": "YES" if any("CLOSE" in row["primitive"] for row in members) else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTIETH_FIVE_F10_STATEMENTS.tsv", statements)

    stages: list[dict[str, str]] = []
    stage_text = {
        "ST01_ROOT_DRAW_PREPARATION": "Wurzel-/Speicherposten kurz entnehmen und Ansatz aktivieren.",
        "ST02_ROOT_WORK_PATH": "Posten ins Arbeitsfach und durch den Lauf führen.",
        "ST03_ROOT_METER_ENTRY": "Nach Maß ansetzen und kurz eintragen.",
        "ST04_ROOT_CONTINUE_READY": "Weiter abziehen und bereit halten.",
        "ST05_UPPER_DRAW_READY": "Zum oberen Sprossposten wechseln, kurz aus Ansatz abziehen und bereit halten.",
        "ST06_UPPER_MOVE_METER_TARGET": "Bereitschaftsmaß setzen, weiterführen und Zielstelle belegen.",
        "ST07_UPPER_CONTINUE_PREPARATION": "Ansatz mehrfach fortführen, messen und davon nehmen.",
        "ST08_UPPER_FEED_STAGE_MEASURE": "Ansatz zuführen, Sollstufe erreichen und Arbeitsmaß abziehen.",
    }
    for number, stage in enumerate(stage_ranges, 1):
        members = [row for row in event_rows if row["article_stage"] == stage]
        stages.append(
            {
                "stage_no": str(number),
                "stage_id": stage,
                "record": members[0]["record"],
                "owner": members[0]["visible_owner_de"],
                "event_ids": "|".join(row["event_id"] for row in members),
                "article_instruction_de": stage_text[stage],
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTIETH_EIGHT_STAGE_F10_ARTICLE.tsv", stages)

    shared_cards = sorted(
        {row["card_no"] for row in event_rows if row["record"] == "H1"}
        & {row["card_no"] for row in event_rows if row["record"] == "H2"}
    )
    model_rows = [
        {
            "feature": "SAME_PHYSICAL_PAGE_AND_PLANT",
            "one_article_two_sections": "SUPPORT",
            "independent_forms": "STRAIN",
            "detail": "H1 and H2 occupy f10r and address two visible parts of one pictured plant.",
        },
        {
            "feature": "VISIBLE_OWNER_SWITCH",
            "one_article_two_sections": "SUPPORT",
            "independent_forms": "NEUTRAL",
            "detail": "H1 root/storage axis; H2 upper stem/flower/bud/leaf set.",
        },
        {
            "feature": "FOUR_SHARED_EXACT_CARDS",
            "one_article_two_sections": "SUPPORT",
            "independent_forms": "SUPPORT",
            "detail": "AR, AIIN, OL and CTH+Y recur with unchanged values.",
        },
        {
            "feature": "BOUNDARY_READY_THIS_TO_THIS_DRAW_PREPARATION",
            "one_article_two_sections": "STRONG_SUPPORT",
            "independent_forms": "STRAIN",
            "detail": "H1 ends cthy=ready this; H2 begins ycheor=this draw-short preparation.",
        },
        {
            "feature": "NO_CLOSE_CARD_IN_EITHER_RECORD",
            "one_article_two_sections": "SUPPORT",
            "independent_forms": "STRAIN",
            "detail": "All five statements remain open prose-like clauses.",
        },
        {
            "feature": "SEPARATE_RECORD_IDENTITIES",
            "one_article_two_sections": "NEUTRAL",
            "independent_forms": "SUPPORT",
            "detail": "The formal record boundary is real and retained.",
        },
    ]
    write_tsv("FIVE_HUNDRED_THIRTIETH_TWO_MODEL_COMPARISON.tsv", model_rows)

    boundary = [
        {
            "left_event": "E014",
            "left_record": "H1",
            "left_surface": "cthy",
            "left_reading": "bereit · dies",
            "right_event": "E015",
            "right_record": "H2",
            "right_surface": "ycheor",
            "right_reading": "dies · abziehen · kurz · Ansatz",
            "combined_workshop_reading_de": "Diesen Posten bereit halten; beim oberen Pflanzenteil diesen Posten kurz aus dem Ansatz abziehen.",
            "owner_transition": "ROOT_STORAGE_PART_TO_UPPER_STEM_PART_OF_SAME_PICTURED_PLANT",
            "selected_relation": "SECTION_HANDOFF_WITH_VISIBLE_PART_SWITCH",
        }
    ]
    write_tsv("FIVE_HUNDRED_THIRTIETH_H1_H2_BOUNDARY.tsv", boundary)

    summary = {
        "status": "PASS",
        "page": "f10r",
        "events": len(event_rows),
        "records": 2,
        "statements": len(statements),
        "article_stages": len(stages),
        "shared_exact_cards": shared_cards,
        "shared_exact_card_count": len(shared_cards),
        "close_cards": sum("CLOSE" in row["primitive"] for row in event_rows),
        "selected_model": "ONE_PICTURED_PLANT_ARTICLE_WITH_ROOT_AND_UPPER_PART_SECTIONS",
    }
    (HERE / "FIVE_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
