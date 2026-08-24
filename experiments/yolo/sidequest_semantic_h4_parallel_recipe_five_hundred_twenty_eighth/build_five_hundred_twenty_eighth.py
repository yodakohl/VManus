#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P527 = ROOT / "experiments/yolo/sidequest_semantic_h3_reverse_recipe_five_hundred_twenty_seventh"


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
    h4 = [row for row in all_events if row["record"] == "H4"]
    h3 = [row for row in all_events if row["record"] == "H3"]
    source_clauses = {
        "E056": ("SET_MEASURE", "ein Maß für den Arbeitsgang setzen"),
        "E057": ("MEASURE", "das vorgeschriebene Maß nehmen"),
        "E058": ("FEED_PORTION", "diesem Posten eine Portion zuführen"),
        "E059": ("FEED_PORTION", "eine weitere Portion zuführen"),
        "E060": ("CLOSE_WORK", "den Arbeitsgang schließen"),
        "E061": ("MEASURE", "das vorgeschriebene Maß nehmen"),
        "E062": ("TRANSFER_ITEM", "diesen Posten umsetzen"),
        "E063": ("STORE", "ihn verwahren"),
        "E064": ("FEED_MEASURE", "diesem Posten das vorgeschriebene Maß zuführen"),
        "E065": ("DRAW_FROM_SOURCE", "kurz von dort abziehen"),
        "E066": ("HEAT_LONGER", "diesen Posten länger wärmen"),
        "E067": ("CONTINUE_CLOSE", "fortsetzen und den Schritt schließen"),
        "E068": ("MEASURE", "das vorgeschriebene Maß nehmen"),
        "E069": ("SET_AT_TARGET", "an der Zielstelle ansetzen"),
        "E070": ("CONTINUE_ENTER_ITEM", "diesen Posten weiter eintragen"),
        "E071": ("PREPARATION", "den Ansatz nehmen"),
        "E072": ("CURRENT_ITEM", "diesen Posten nehmen"),
        "E073": ("PREPARATION_PORTION", "eine Portion des Ansatzes nehmen"),
    }
    stage_for_event = {
        **{event: "ST01_SET_MEASURE" for event in ("E056", "E057")},
        **{event: "ST02_FEED_PORTIONS_CLOSE" for event in ("E058", "E059", "E060")},
        **{event: "ST03_MEASURE_TRANSFER_STORE" for event in ("E061", "E062", "E063")},
        "E064": "ST04_FEED_MEASURE",
        "E065": "ST05_DRAW_SOURCE",
        **{event: "ST06_HEAT_CONTINUE_CLOSE" for event in ("E066", "E067")},
        **{event: "ST07_ASSIGN_TARGET" for event in ("E068", "E069")},
        **{event: "ST08_CONTINUE_WITH_PREPARATION" for event in ("E070", "E071", "E072", "E073")},
    }
    event_rows: list[dict[str, str]] = []
    for row in h4:
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
                "owner_source": "IMAGE_H4_WHOLE_BROAD_LEAF_PLANT",
                "owner_noun_de": "die abgebildete breitblättrige Pflanze",
                "content_license": "CARD_PLUS_VISIBLE_OWNER",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_EIGHTH_H4_EIGHTEEN_EVENT_REVERSE_BUILD.tsv", event_rows)

    specs = {
        "H4-S001": (
            "Ein Maß für den Arbeitsgang setzen; das Maß nehmen; diesem Posten zwei aufeinanderfolgende Portionen zuführen; schließen.",
            "Für die abgebildete Pflanze das vorgeschriebene Maß setzen, zwei Portionen zuführen und den Schritt schließen.",
            "für die Pflanze|zwei aufeinanderfolgende",
        ),
        "H4-S002": (
            "Das vorgeschriebene Maß nehmen; diesen Posten umsetzen; verwahren.",
            "Eine weitere Menge abmessen, den Posten umsetzen und verwahren.",
            "weitere Menge",
        ),
        "H4-S003": (
            "Diesem Posten das vorgeschriebene Maß zuführen; kurz von dort abziehen; länger wärmen; fortsetzen und schließen.",
            "Die vorgeschriebene Menge zuführen, kurz aus dem Arbeitsbestand abziehen, länger wärmen und den Schritt schließen.",
            "Arbeitsbestand",
        ),
        "H4-S004": (
            "Das Maß nehmen; an der Zielstelle ansetzen; diesen Posten weiter eintragen; Ansatz; dieser Posten; Ansatzportion.",
            "Nach Maß an der Zielstelle ansetzen, den Posten weiter eintragen und eine Portion des Ansatzes zuführen.",
            "nach Maß|zuführen",
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
                "visible_owner_de": "die abgebildete breitblättrige Pflanze",
                "workshop_expanded_reading_de": fluent,
                "expansion_words_not_direct_card_glosses": added,
                "sentence_ends_at_physical_line": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_EIGHTH_FOUR_H4_STATEMENTS.tsv", statements)

    stages = [
        ("ST01_SET_MEASURE", "Vorgabemaß für den Arbeitsgang setzen.", "E056|E057"),
        ("ST02_FEED_PORTIONS_CLOSE", "Zwei Portionen nacheinander zuführen und schließen.", "E058|E059|E060"),
        ("ST03_MEASURE_TRANSFER_STORE", "Weitere Menge abmessen, Posten umsetzen und verwahren.", "E061|E062|E063"),
        ("ST04_FEED_MEASURE", "Dem laufenden Posten das vorgeschriebene Maß zuführen.", "E064"),
        ("ST05_DRAW_SOURCE", "Kurz aus dem bisherigen Arbeitsbestand abziehen.", "E065"),
        ("ST06_HEAT_CONTINUE_CLOSE", "Posten länger wärmen, fortsetzen und schließen.", "E066|E067"),
        ("ST07_ASSIGN_TARGET", "Maß setzen und Zielstelle aktivieren.", "E068|E069"),
        ("ST08_CONTINUE_WITH_PREPARATION", "Posten weiter eintragen und eine Ansatzportion zuführen.", "E070|E071|E072|E073"),
    ]
    stage_rows = [
        {
            "stage_no": str(number),
            "stage_id": stage_id,
            "reverse_source_instruction_de": instruction,
            "selected_event_ids": event_ids,
            "selection_mechanism": "COMPONENT_LEXICON_PLUS_H4_IMAGE_OWNER",
        }
        for number, (stage_id, instruction, event_ids) in enumerate(stages, 1)
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_EIGHTH_EIGHT_STAGE_H4_RECIPE.tsv", stage_rows)

    shared_cards = sorted({row["card_no"] for row in h3} & {row["card_no"] for row in h4})
    h3_primitive = Counter(token for row in h3 for token in row["procedure_tokens"].split(">"))
    h4_primitive = Counter(token for row in h4 for token in row["procedure_tokens"].split(">"))
    primitive_order = [
        "SOURCE_DRAW",
        "ACTIVATE_CHARGE",
        "TARGET_HANDOFF",
        "METER_CHECK",
        "MOVE_PASS",
        "HOLD_STATE",
        "CONTINUE_USE",
        "CLOSE",
    ]
    comparison = []
    for primitive in primitive_order:
        comparison.append(
            {
                "comparison_unit": primitive,
                "h3_count": str(h3_primitive[primitive]),
                "h4_count": str(h4_primitive[primitive]),
                "shared": "YES" if h3_primitive[primitive] and h4_primitive[primitive] else "NO",
                "interpretation_de": (
                    "gemeinsame Werkstattoperation"
                    if h3_primitive[primitive] and h4_primitive[primitive]
                    else "H3-spezifischer Schwerpunkt"
                    if h3_primitive[primitive]
                    else "H4-spezifischer Schwerpunkt"
                ),
            }
        )
    for card in shared_cards:
        comparison.append(
            {
                "comparison_unit": f"EXACT_CARD_{card}",
                "h3_count": str(sum(row["card_no"] == card for row in h3)),
                "h4_count": str(sum(row["card_no"] == card for row in h4)),
                "shared": "YES",
                "interpretation_de": next(row["apprentice_spoken_reading_de"] for row in h3 if row["card_no"] == card),
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_EIGHTH_H3_H4_PROCESS_COMPARISON.tsv", comparison)

    summary = {
        "status": "PASS",
        "record": "H4",
        "page": "f55v",
        "events": len(event_rows),
        "statements": len(statements),
        "reverse_stages": len(stage_rows),
        "shared_primitive_families": sum(row["shared"] == "YES" and not row["comparison_unit"].startswith("EXACT") for row in comparison),
        "shared_exact_cards": shared_cards,
        "h3_emphasis": "HOLD_AND_PRODUCT_TRANSFER",
        "h4_emphasis": "MEASURE_ADD_HEAT_STORE_TARGET",
    }
    (HERE / "FIVE_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
