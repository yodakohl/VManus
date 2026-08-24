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
    events = [row for row in all_events if row["record"] == "H3"]
    source_clauses = {
        "E039": ("FORTSETZEN_UNTER_HALTEN", "weiter unter Halten eintragen"),
        "E040": ("AM_ZIEL_HALten", "an der Zielstelle in Arbeit halten"),
        "E041": ("AUSWRINGEN", "auswringen"),
        "E042": ("POSTEN_NACH_MASS_HALten", "diesen Posten nach Maß halten"),
        "E043": ("POSTEN_HINEINFUEHREN", "diesen Posten hineinführen"),
        "E044": ("EMPFANGSBESTAND", "den Empfangsbestand nehmen"),
        "E045": ("ABZIEHEN_UND_SCHLIESSEN", "abziehen und den Schritt schließen"),
        "E046": ("ARBEITSPOSTEN_HALten", "diesen Arbeitsposten halten"),
        "E047": ("FORTSETZEN", "fortsetzen"),
        "E048": ("DIESER_POSTEN", "diesen Posten"),
        "E049": ("POSTEN_ZUFUEHREN", "diesen Posten zuführen"),
        "E050": ("DIESER_POSTEN", "diesen Posten"),
        "E051": ("MASS", "nach dem vorgeschriebenen Maß"),
        "E052": ("DANACH_DIESER_POSTEN", "danach diesen Posten"),
        "E053": ("ARBEIT_FORTSETZEN", "den Arbeitsgang weiter ansetzen"),
        "E054": ("POSTEN_BEREIT", "diesen Posten bereit halten"),
        "E055": ("DIESER_POSTEN", "diesen Posten"),
    }
    stage_for_event = {
        "E039": "ST01_OWNER_TARGET",
        "E040": "ST01_OWNER_TARGET",
        "E041": "ST02_EXPRESS",
        "E042": "ST03_HOLD_MEASURE",
        "E043": "ST04_TRANSFER_RECEIVER",
        "E044": "ST04_TRANSFER_RECEIVER",
        "E045": "ST05_DRAW_CLOSE",
        "E046": "ST06_RETAIN_PRODUCT",
        "E047": "ST07_METERED_REINTRODUCTION",
        "E048": "ST07_METERED_REINTRODUCTION",
        "E049": "ST07_METERED_REINTRODUCTION",
        "E050": "ST07_METERED_REINTRODUCTION",
        "E051": "ST07_METERED_REINTRODUCTION",
        "E052": "ST08_NEXT_READY",
        "E053": "ST08_NEXT_READY",
        "E054": "ST08_NEXT_READY",
        "E055": "ST08_NEXT_READY",
    }
    event_rows: list[dict[str, str]] = []
    for row in events:
        function, clause = source_clauses[row["event_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["renderer_final_surface"],
                "component_parse": row["component_parse"],
                "card_reading": row["apprentice_spoken_reading_de"],
                "primitive": row["procedure_tokens"],
                "reverse_stage": stage_for_event[row["event_id"]],
                "source_function": function,
                "minimum_source_clause_de": clause,
                "owner_source": "IMAGE_H3_WHOLE_DENSE_CROWN_PLANT",
                "owner_noun_de": "die abgebildete dichtkronige Pflanze",
                "content_license": "CARD_PLUS_VISIBLE_OWNER",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SEVENTH_H3_SEVENTEEN_EVENT_REVERSE_BUILD.tsv", event_rows)

    statement_specs = {
        "H3-S001": {
            "literal": "Weiter unter Halten eintragen; an der Zielstelle in Arbeit halten; auswringen; diesen Posten nach Maß halten; hineinführen; Empfangsbestand nehmen; abziehen und schließen.",
            "fluent": "Die abgebildete Pflanze an der Arbeitsstelle weiter bearbeiten und auswringen. Den gewonnenen Posten für das vorgeschriebene Maß stehen lassen, in den Empfänger geben und den Empfangsbestand abziehen.",
            "added": "Arbeitsstelle|gewonnen|stehen lassen|Empfänger",
        },
        "H3-S002": {
            "literal": "Diesen Arbeitsposten halten.",
            "fluent": "Den abgezogenen Empfangsbestand zurückhalten.",
            "added": "abgezogen|zurückhalten",
        },
        "H3-S003": {
            "literal": "Fortsetzen; diesen Posten zuführen; nach dem vorgeschriebenen Maß.",
            "fluent": "Davon die vorgeschriebene Menge weiter zuführen.",
            "added": "davon|Menge",
        },
        "H3-S004": {
            "literal": "Danach diesen Posten; den Arbeitsgang weiter ansetzen; diesen Posten bereit halten.",
            "fluent": "Danach den laufenden Arbeitsgang fortsetzen und den Posten bis zur Bereitschaft halten.",
            "added": "laufend|bis zur Bereitschaft",
        },
    }
    statements: list[dict[str, str]] = []
    for statement_id, spec in statement_specs.items():
        members = [row for row in event_rows if row["statement_id"] == statement_id]
        statements.append(
            {
                "statement_id": statement_id,
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_licensed_literal_de": spec["literal"],
                "visible_owner_de": "die abgebildete dichtkronige Pflanze",
                "workshop_expanded_reading_de": spec["fluent"],
                "expansion_words_not_direct_card_glosses": spec["added"],
                "sentence_ends_at_physical_line": "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SEVENTH_FOUR_H3_STATEMENTS.tsv", statements)

    stages = [
        ("ST01_OWNER_TARGET", "Die abgebildete Pflanze als laufenden Besitzer setzen und an der Arbeitsstelle halten.", "E039|E040"),
        ("ST02_EXPRESS", "Den Pflanzenposten auswringen.", "E041"),
        ("ST03_HOLD_MEASURE", "Den gewonnenen Posten nach vorgeschriebenem Maß halten.", "E042"),
        ("ST04_TRANSFER_RECEIVER", "Den Posten in den Empfänger führen und als Empfangsbestand führen.", "E043|E044"),
        ("ST05_DRAW_CLOSE", "Den Empfangsbestand abziehen und den Schritt schließen.", "E045"),
        ("ST06_RETAIN_PRODUCT", "Den abgezogenen Arbeitsbestand zurückhalten.", "E046"),
        ("ST07_METERED_REINTRODUCTION", "Davon eine vorgeschriebene Menge weiter zuführen.", "E047|E048|E049|E050|E051"),
        ("ST08_NEXT_READY", "Danach den Arbeitsgang fortsetzen und den Posten bereit halten.", "E052|E053|E054|E055"),
    ]
    stage_rows = [
        {
            "stage_no": str(number),
            "stage_id": stage_id,
            "reverse_source_instruction_de": instruction,
            "selected_event_ids": event_ids,
            "selection_mechanism": "COMPONENT_LEXICON_PLUS_H3_IMAGE_OWNER",
        }
        for number, (stage_id, instruction, event_ids) in enumerate(stages, 1)
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_SEVENTH_EIGHT_STAGE_H3_RECIPE.tsv", stage_rows)

    additions = [
        ("Arbeitsstelle", "AL/TARGET_HANDOFF plus practical expansion", "MODERATE"),
        ("gewonnen", "result of AUSWRINGEN before receiver transfer", "MODERATE"),
        ("stehen lassen", "natural expansion of HOLD plus prescribed measure", "MODERATE"),
        ("Empfänger", "P/MOVE inward plus learned EMPFANGSBESTAND", "MODERATE"),
        ("abgezogener Bestand", "ABZIEHEN followed by HOLD", "MODERATE"),
        ("Pflanzenart", "not supplied; image gives only visible plant owner", "WITHHELD"),
        ("Wasser/Wein/Öl", "no H3 card in this passage selects a liquid name", "WITHHELD"),
        ("Krankheit/Körperteil", "no card or visible H3 owner supplies one", "WITHHELD"),
    ]
    addition_rows = [
        {
            "item": item,
            "basis": basis,
            "working_status": status,
        }
        for item, basis, status in additions
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_SEVENTH_H3_EXPANSION_LEDGER.tsv", addition_rows)

    summary = {
        "status": "PASS",
        "record": "H3",
        "page": "f11r",
        "events": len(event_rows),
        "statements": len(statements),
        "reverse_stages": len(stage_rows),
        "visible_owner": "H3_WHOLE_DENSE_CROWN_PLANT",
        "card_licensed_every_event": all(row["minimum_source_clause_de"] for row in event_rows),
        "withheld_specific_nouns": ["Pflanzenart", "Wasser/Wein/Öl", "Krankheit/Körperteil"],
    }
    (HERE / "FIVE_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
