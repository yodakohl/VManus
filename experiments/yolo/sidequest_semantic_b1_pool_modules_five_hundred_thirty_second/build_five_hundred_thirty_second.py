#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P531 = ROOT / "experiments/yolo/sidequest_semantic_complete_herbal_edition_five_hundred_thirty_first"


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
    b1 = [row for row in all_events if row["record"] == "B1"]
    herbal_dictionary = read_tsv(P531 / "FIVE_HUNDRED_THIRTY_FIRST_SIXTY_SIX_CARD_HERBAL_DICTIONARY.tsv")
    herbal_cards = {row["card_no"] for row in herbal_dictionary}

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in b1:
        by_card[row["card_no"]].append(row)
    dictionary: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"B1 card reading drift {card_no}: {readings}")
        dictionary.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "occurrences": str(len(rows)),
                "surfaces": "|".join(dict.fromkeys(row["renderer_final_surface"] for row in rows)),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "shared_with_herbal": "YES" if card_no in herbal_cards else "NO",
                "owner_scope": "B1_SHARED_TWO_ROW_POOL",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SECOND_FORTY_THREE_B1_CARD_DICTIONARY.tsv", dictionary)

    event_rows: list[dict[str, str]] = []
    for row in b1:
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "invariant_card_reading_de": row["apprentice_spoken_reading_de"],
                "primitive": row["procedure_tokens"],
                "minimum_source_clause_de": row["apprentice_spoken_reading_de"].replace(" · ", " "),
                "visible_owner_de": "gemeinsame zweireihige Figuren-/Beckenstation",
                "owner_id": "B1_SHARED_TWO_ROW_POOL",
                "terminal": "YES" if "CLOSE" in row["procedure_tokens"].split(">") else "NO",
                "global_flow_direction": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SECOND_SIXTY_SIX_B1_EVENT_INTERLINEAR.tsv", event_rows)

    readings = {
        "B1-S001": "Einen kurzen Einsatz ansetzen und schließen.",
        "B1-S002": "Nach Maß den Lauf speisen und die Zielstelle ansetzen; von dort Portionen weiterführen, abkühlen lassen, den Ansatz fortsetzen, am Durchlass halten, weitere Maße und Ziel setzen, umsetzen und schließen.",
        "B1-S003": "Fortsetzen, durch Halten zuführen, umsetzen und schließen.",
        "B1-S004": "Den Posten umsetzen, fortsetzen, absetzen und schließen.",
        "B1-S005": "Weiter umsetzen und schließen.",
        "B1-S006": "Eine Portion ansetzen, durch den Durchlass führen, weiterleiten und abgekühlt an der Zielstelle halten.",
        "B1-S007": "Den Posten ansetzen, umsetzen und schließen.",
        "B1-S008": "Den Posten fortsetzen, kurz wärmen, weiterführen, absetzen und schließen.",
        "B1-S009": "Einen kurzen Einsatz ansetzen und schließen.",
        "B1-S010": "Einen weiteren kurzen Einsatz ansetzen und schließen.",
        "B1-S011": "Den Durchlass mit dem laufenden Posten belegen und ansetzen.",
        "B1-S012": "Den Waschgang beginnen, den Posten kurz ansetzen und den kurzen Waschgang schließen.",
        "B1-S013": "Einen kurzen Waschgang schließen.",
        "B1-S014": "Den Posten umsetzen, auffangen, zur Zielstelle führen, fortsetzen und danach von dort nehmen.",
        "B1-S015": "Den Posten kurz eintragen, ansetzen, umsetzen und schließen.",
        "B1-S016": "An der Zielstelle ansetzen, länger halten, fortsetzen, absetzen und schließen.",
        "B1-S017": "Die Zielstelle setzen, kurz fortsetzen, umsetzen und schließen.",
        "B1-S018": "Den Posten führen, kurz halten und fortsetzen, auf Sollstufe bringen, länger auffangen und schließen.",
        "B1-S019": "Absetzen und schließen.",
        "B1-S020": "Kurz wärmen, kurz am Durchlass halten und schließen.",
        "B1-S021": "Die Zielstelle übernehmen.",
    }
    statement_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_members[row["statement_id"]].append(row)
    statements: list[dict[str, str]] = []
    for statement_id, members in statement_members.items():
        statements.append(
            {
                "statement_id": statement_id,
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_literal_de": "; ".join(row["invariant_card_reading_de"] for row in members),
                "fluent_pool_reading_de": readings[statement_id],
                "terminal": "YES" if any(row["terminal"] == "YES" for row in members) else "NO",
                "unit_type": "INDEPENDENT_CLOSED_CELL" if any(row["terminal"] == "YES" for row in members) else "OPEN_POOL_INSTRUCTION",
                "visible_owner_de": "gemeinsame zweireihige Figuren-/Beckenstation",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SECOND_TWENTY_ONE_B1_OPERATING_CELLS.tsv", statements)

    locus_order = ["f81v.2", "f81v.7", "f81v.17", "f81v.18", "f81v.21", "f81v.24", "f81v.27"]
    module_names = {
        "f81v.2": "Grundsetup, Maß, Lauf und Ziel",
        "f81v.7": "Fortsetzung und geschlossener Transfer",
        "f81v.17": "Umsetzen, Absetzen und Durchlassportion",
        "f81v.18": "Wärme-, Absetz- und Kurzeinsatzzyklen",
        "f81v.21": "Waschen, Auffangen und Zielweitergabe",
        "f81v.24": "Ziel-, Halte-, Sollstufen- und Auffangzyklen",
        "f81v.27": "Absetzen, kurzes Wärmen und offene Zielübergabe",
    }
    modules: list[dict[str, str]] = []
    for number, locus in enumerate(locus_order, 1):
        member_statements = [row for row in statements if locus in row["loci"].split("|")]
        member_events = [row for row in event_rows if row["locus"] == locus]
        modules.append(
            {
                "module_no": str(number),
                "locus": locus,
                "module_name_de": module_names[locus],
                "statement_ids": "|".join(row["statement_id"] for row in member_statements),
                "event_ids": "|".join(row["event_id"] for row in member_events),
                "events": str(len(member_events)),
                "closed_cells": str(sum(row["terminal"] == "YES" for row in member_statements)),
                "open_instructions": str(sum(row["terminal"] == "NO" for row in member_statements)),
                "owner": "B1_SHARED_TWO_ROW_POOL",
                "module_relation": "LOCAL_MODULE_WITHOUT_GLOBAL_FLOW_ORDER",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SECOND_SEVEN_B1_POOL_MODULES.tsv", modules)

    shared = [row for row in dictionary if row["shared_with_herbal"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_SECOND_TEN_HERBAL_SHARED_CARDS.tsv", shared)

    lines = [
        "# f81v / B1 — Arbeitsausgabe der gemeinsamen Beckenstation",
        "",
        "Bildbesitzer: gemeinsame zweireihige Figuren-/Beckenstation.",
        "Die 21 Aussagen sind lokale Betriebszellen; es wird keine globale Flussrichtung ergänzt.",
        "",
    ]
    for module in modules:
        lines.extend([f"## Modul {module['module_no']}: {module['module_name_de']}", ""])
        for statement in statements:
            if module["locus"] in statement["loci"].split("|"):
                lines.append(f"- {statement['statement_id']}: {statement['fluent_pool_reading_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_THIRTY_SECOND_COMPLETE_B1_POOL_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    summary = {
        "status": "PASS",
        "page": "f81v",
        "record": "B1",
        "events": len(event_rows),
        "statements": len(statements),
        "closed_cells": sum(row["terminal"] == "YES" for row in statements),
        "open_instructions": sum(row["terminal"] == "NO" for row in statements),
        "local_modules": len(modules),
        "exact_cards": len(dictionary),
        "shared_with_herbal_cards": len(shared),
        "global_flow_direction": "NONE",
    }
    (HERE / "FIVE_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
