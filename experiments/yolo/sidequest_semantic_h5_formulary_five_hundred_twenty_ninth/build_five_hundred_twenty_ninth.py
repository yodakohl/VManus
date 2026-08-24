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
    h5 = [row for row in all_events if row["record"] == "H5"]
    source_clauses = {
        "E074": ("DRAW_PREPARATION_DOSE", "eine Gabe aus dem Ansatz abziehen"),
        "E075": ("DOSE", "eine Gabe nehmen"),
        "E076": ("DOSE_TO_TARGET", "diese Gabe an die Zielstelle bringen"),
        "E077": ("MEASURE", "das vorgeschriebene Maß setzen"),
        "E078": ("DOSE", "eine weitere Gabe nehmen"),
        "E079": ("FEED_CONTINUE", "zuführen und fortsetzen"),
        "E080": ("NEXT_DRAW_PREPARATION", "danach aus dem Ansatz abziehen"),
        "E081": ("SET_ITEM", "diesen Posten ansetzen"),
        "E082": ("TARGET", "die Zielstelle nehmen"),
        "E083": ("CONTINUE", "fortsetzen"),
        "E084": ("CURRENT_DOSE", "diese Gabe nehmen"),
        "E085": ("SET_ITEM", "diesen Posten ansetzen"),
        "E086": ("LONG_PASS_CLOSE", "länger durch den Durchlass führen und schließen"),
        "E087": ("HOLD", "halten"),
        "E088": ("DOSE", "eine Gabe nehmen"),
        "E089": ("FEED_BRIEFLY", "diesen Posten kurz zuführen"),
        "E090": ("SET_AGAIN", "diesen Posten erneut ansetzen"),
        "E091": ("SET_ITEM", "diesen Posten ansetzen"),
        "E092": ("SET_EXTRACT", "den Auszug ansetzen"),
        "E093": ("FEED_TO_TARGET", "zur Zielstelle zuführen"),
        "E094": ("DOSE", "eine Gabe nehmen"),
        "E095": ("SET_ITEM", "diesen Posten ansetzen"),
        "E096": ("FEED_DOSE_FROM_SOURCE", "eine Gabe von dort zuführen"),
        "E097": ("NEXT_WORK_PORTION", "danach eine Arbeitsportion nehmen"),
        "E098": ("NEXT_ITEM", "danach diesen Posten nehmen"),
        "E099": ("FEED_BRIEFLY_CONTINUE", "kurz zuführen und fortsetzen"),
        "E100": ("MEASURE", "nach dem vorgeschriebenen Maß"),
    }
    stage_for_event = {
        "E074": "ST01_DRAW_DOSE",
        **{event: "ST02_DOSE_TARGET_MEASURE" for event in ("E075", "E076", "E077")},
        **{event: "ST03_SECOND_DOSE_CONTINUE" for event in ("E078", "E079")},
        **{event: "ST04_NEXT_DRAW_SET_TARGET" for event in ("E080", "E081", "E082")},
        **{event: "ST05_CONTINUE_PASSAGE_CLOSE" for event in ("E083", "E084", "E085", "E086")},
        **{event: "ST06_HOLD_FEED_REPEAT" for event in ("E087", "E088", "E089", "E090")},
        **{event: "ST07_SET_EXTRACT_TARGET" for event in ("E091", "E092", "E093")},
        **{event: "ST08_DOSE_SOURCE_PORTION" for event in ("E094", "E095", "E096", "E097")},
        **{event: "ST09_NEXT_BRIEF_CONTINUE_MEASURE" for event in ("E098", "E099", "E100")},
    }
    event_rows: list[dict[str, str]] = []
    for row in h5:
        function, clause = source_clauses[row["event_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "card_reading": row["apprentice_spoken_reading_de"],
                "primitive": row["procedure_tokens"],
                "reverse_stage": stage_for_event[row["event_id"]],
                "source_function": function,
                "minimum_source_clause_de": clause,
                "owner_source": "IMAGE_H5_WHOLE_MULTIHEAD_COILED_PLANT",
                "owner_noun_de": "die abgebildete mehrköpfige Pflanze",
                "content_license": "CARD_PLUS_VISIBLE_OWNER",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_NINTH_H5_TWENTY_SEVEN_EVENT_REVERSE_BUILD.tsv", event_rows)

    specs = {
        "H5-S001": (
            "Gabe aus Ansatz abziehen; Gabe an Zielstelle; Maß; weitere Gabe zuführen und fortsetzen; danach aus Ansatz abziehen; Posten ansetzen; Zielstelle.",
            "Eine Gabe aus dem Ansatz nehmen und nach Maß an der Zielstelle ansetzen. Eine weitere Gabe zuführen; danach erneut aus dem Ansatz nehmen und an der Zielstelle ansetzen.",
            "eine|nach Maß|weitere|erneut",
        ),
        "H5-S002": (
            "Fortsetzen; diese Gabe; Posten ansetzen; länger durch den Durchlass führen; schließen.",
            "Die Anwendung fortsetzen, diese Gabe ansetzen und den Posten länger durch den Durchlass führen; schließen.",
            "Anwendung",
        ),
        "H5-S003": (
            "Halten; Gabe; kurz zuführen; erneut ansetzen.",
            "Eine Gabe halten, kurz zuführen und am laufenden Posten erneut ansetzen.",
            "am laufenden Posten",
        ),
        "H5-S004": (
            "Posten ansetzen; Auszug ansetzen; zur Zielstelle zuführen.",
            "Den laufenden Posten und den Auszug ansetzen, dann zur Zielstelle zuführen.",
            "laufend|dann",
        ),
        "H5-S005": (
            "Gabe; Posten ansetzen; Gabe von dort zuführen; danach Arbeitsportion.",
            "Eine Gabe ansetzen, eine weitere Gabe aus derselben Quelle zuführen und danach eine Arbeitsportion nehmen.",
            "weitere|derselben Quelle",
        ),
        "H5-S006": (
            "Danach diesen Posten; kurz zuführen und fortsetzen; Maß.",
            "Danach den Posten kurz weiter zuführen, nach dem vorgeschriebenen Maß.",
            "weiter",
        ),
    }
    statements: list[dict[str, str]] = []
    for statement_id, (literal, fluent, added) in specs.items():
        members = [row for row in event_rows if row["statement_id"] == statement_id]
        statements.append(
            {
                "statement_id": statement_id,
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_licensed_literal_de": literal,
                "visible_owner_de": "die abgebildete mehrköpfige Pflanze",
                "workshop_expanded_reading_de": fluent,
                "expansion_words_not_direct_card_glosses": added,
                "crosses_physical_line": "YES" if statement_id == "H5-S001" else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_NINTH_SIX_H5_STATEMENTS.tsv", statements)

    stages = [
        ("ST01_DRAW_DOSE", "Eine Gabe aus dem Ansatz ziehen.", "E074"),
        ("ST02_DOSE_TARGET_MEASURE", "Gabe nach Maß an die Zielstelle bringen.", "E075|E076|E077"),
        ("ST03_SECOND_DOSE_CONTINUE", "Weitere Gabe zuführen und fortsetzen.", "E078|E079"),
        ("ST04_NEXT_DRAW_SET_TARGET", "Danach erneut aus dem Ansatz ziehen und den Zielposten setzen.", "E080|E081|E082"),
        ("ST05_CONTINUE_PASSAGE_CLOSE", "Anwendung länger durch den Durchlass führen und schließen.", "E083|E084|E085|E086"),
        ("ST06_HOLD_FEED_REPEAT", "Gabe halten, kurz zuführen und erneut ansetzen.", "E087|E088|E089|E090"),
        ("ST07_SET_EXTRACT_TARGET", "Posten und Auszug ansetzen und zur Zielstelle führen.", "E091|E092|E093"),
        ("ST08_DOSE_SOURCE_PORTION", "Gabe aus derselben Quelle zuführen, dann Arbeitsportion.", "E094|E095|E096|E097"),
        ("ST09_NEXT_BRIEF_CONTINUE_MEASURE", "Danach kurz nach vorgeschriebenem Maß weiter zuführen.", "E098|E099|E100"),
    ]
    stage_rows = [
        {
            "stage_no": str(number),
            "stage_id": stage_id,
            "reverse_source_instruction_de": instruction,
            "selected_event_ids": event_ids,
            "selection_mechanism": "COMPONENT_LEXICON_PLUS_H5_IMAGE_OWNER",
        }
        for number, (stage_id, instruction, event_ids) in enumerate(stages, 1)
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_NINTH_NINE_STAGE_H5_RECIPE.tsv", stage_rows)

    records = {record: [row for row in all_events if row["record"] == record] for record in ("H3", "H4", "H5")}
    primitives = ["SOURCE_DRAW", "ACTIVATE_CHARGE", "TARGET_HANDOFF", "METER_CHECK", "MOVE_PASS", "HOLD_STATE", "CONTINUE_USE", "CLOSE"]
    comparison: list[dict[str, str]] = []
    counts_by_record = {
        record: Counter(token for row in rows for token in row["procedure_tokens"].split(">"))
        for record, rows in records.items()
    }
    for primitive in primitives:
        comparison.append(
            {
                "formulary_role": primitive,
                "h3_count": str(counts_by_record["H3"][primitive]),
                "h4_count": str(counts_by_record["H4"][primitive]),
                "h5_count": str(counts_by_record["H5"][primitive]),
                "present_all_three": "YES" if all(counts_by_record[record][primitive] for record in records) else "NO",
                "working_formulary_value": {
                    "SOURCE_DRAW": "Quelle/Abziehen",
                    "ACTIVATE_CHARGE": "Arbeitsgang/Gabe ansetzen",
                    "TARGET_HANDOFF": "Zielstelle",
                    "METER_CHECK": "Maß",
                    "MOVE_PASS": "Weiter-/Hineinführen",
                    "HOLD_STATE": "Halten/Zustand",
                    "CONTINUE_USE": "Fortsetzen",
                    "CLOSE": "Schritt schließen",
                }[primitive],
            }
        )
    comparison.append(
        {
            "formulary_role": "EXACT_CARD_PROC009_AIIN",
            "h3_count": str(sum(row["card_no"] == "PROC009" for row in records["H3"])),
            "h4_count": str(sum(row["card_no"] == "PROC009" for row in records["H4"])),
            "h5_count": str(sum(row["card_no"] == "PROC009" for row in records["H5"])),
            "present_all_three": "YES",
            "working_formulary_value": "vorgeschriebenes Maß",
        }
    )
    comparison.extend(
        [
            {
                "formulary_role": "ARTICLE_SPECIFIC_CHAIN",
                "h3_count": "17",
                "h4_count": "18",
                "h5_count": "27",
                "present_all_three": "YES",
                "working_formulary_value": "H3 Extraktion/Empfang; H4 Dosierung/Hitze/Lager; H5 wiederholte Gabe/Ziel/Durchlass",
            },
            {
                "formulary_role": "VISIBLE_OWNER",
                "h3_count": "1",
                "h4_count": "1",
                "h5_count": "1",
                "present_all_three": "YES",
                "working_formulary_value": "jeweils ganze abgebildete Pflanze; keine Artbezeichnung",
            },
        ]
    )
    write_tsv("FIVE_HUNDRED_TWENTY_NINTH_H3_H5_FORMULARY.tsv", comparison)

    summary = {
        "status": "PASS",
        "record": "H5",
        "page": "f56r",
        "events": len(event_rows),
        "statements": len(statements),
        "reverse_stages": len(stage_rows),
        "shared_primitives_all_three": [row["formulary_role"] for row in comparison if row["present_all_three"] == "YES" and row["formulary_role"] in primitives],
        "shared_exact_measure_card_counts": {record: sum(row["card_no"] == "PROC009" for row in rows) for record, rows in records.items()},
    }
    (HERE / "FIVE_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
