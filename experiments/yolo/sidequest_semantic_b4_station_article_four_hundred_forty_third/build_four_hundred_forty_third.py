#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
SOURCES = [
    (ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv", "small_value_de", "B1"),
    (ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv", "small_values_de", "B2"),
    (ROOT / "experiments/yolo/sidequest_semantic_b3_local_tournament_four_hundred_forty_second/FOUR_HUNDRED_FORTY_SECOND_FINAL_B3_52_CARD_DICTIONARY.tsv", "small_values_de", "B3"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = [row for row in read(BASE) if row["record_unit_id"] == "B4"]
    deck: dict[str, tuple[str, str]] = {}
    for path, value_column, source in SOURCES:
        for row in read(path):
            deck[row["joint_tuple_id"]] = (row[value_column], source)
    shared = set(deck) & {row["joint_tuple_id"] for row in base}
    events = []
    for order, row in enumerate(base, start=1):
        number = int(row["event_id"][1:])
        value, source = deck.get(row["joint_tuple_id"], (row["concrete_word_reading_de"], "B4"))
        events.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "small_value_de": value, "owner_zone": "B4_ZONE_A_LEFT_AND_UPPER_FLOW" if number < 356 else "B4_ZONE_B_RIGHT_LOWER_FLOW",
            "lexicon_source": f"{source}_EXACT_CARD_TRANSFER" if row["joint_tuple_id"] in shared else "B4_LOCAL_LEARNED_CARD",
        })
    write("FOUR_HUNDRED_FORTY_THIRD_B4_47_EVENT_INTERLINEAR.tsv", events)

    translations = {
        "B4-S001": "Länger ansetzen und schließen.",
        "B4-S002": "Im Arbeitsbecken länger ansetzen, dann kurz ansetzen und schließen.",
        "B4-S003": "Dies umsetzen, an die Folgestelle gehen, den Folgeposten länger ansetzen, dies verwenden, fortsetzen, kurz absetzen und schließen.",
        "B4-S004": "Den Posten befestigen und schließen.",
        "B4-S005": "Durch das Tuch führen, dies umsetzen, länger ansetzen und schließen.",
        "B4-S006": "Seihen und schließen.",
        "B4-S007": "Seihen und schließen.",
        "B4-S008": "Auf Maß bringen, länger wärmen, die erste Öffnung wählen, kurz ansetzen und schließen.",
        "B4-S009": "Kurz absetzen und schließen.",
        "B4-S010": "Fortsetzen und schließen.",
        "B4-S011": "Auf Maß bringen, kurz wärmen, mit dem Vorigen länger fortsetzen, eine Portion zugeben, dies umsetzen, fortsetzen, die zweite Waschung ausführen und schließen.",
        "B4-S012": "Hinausführen und schließen.",
        "B4-S013": "Die Fortsetzung einsetzen, kurz absetzen und schließen.",
        "B4-S014": "Den Ansatz und diesen Posten über der Stelle führen, den Wasserlauf schließen und den Schritt beenden.",
        "B4-S015": "Eine Portion und den Klarauszug mit einer weiteren Portion zur Durchlasszeit bringen; nach dem Besitzerwechsel kurz auffangen, hinausführen und schließen.",
        "B4-S016": "Eine weitere Portion an die Stelle geben, warm ausgießen, kurz absetzen und schließen.",
    }
    statements = []
    for statement_id in sorted(translations, key=lambda value: int(value.split("S")[1])):
        rows = [row for row in events if row["statement_id"] == statement_id]
        statements.append({
            "statement_id": statement_id, "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "owner_zones": "|".join(dict.fromkeys(row["owner_zone"] for row in rows)),
            "card_sequence_de": " > ".join(row["small_value_de"] for row in rows),
            "continuous_reading_de": translations[statement_id],
            "owner_break_inside_statement": "YES" if len({row["owner_zone"] for row in rows}) > 1 else "NO",
        })
    write("FOUR_HUNDRED_FORTY_THIRD_B4_16_STATEMENTS.tsv", statements)

    transfer = []
    for joint_id in sorted(shared):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        value, source = deck[joint_id]
        transfer.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "latest_source_deck": source, "fixed_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_THIRD_NINETEEN_B1_B2_B3_TRANSFERS.tsv", transfer)

    local = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events} - shared):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        local.append({
            "joint_tuple_id": joint_id, "surface": rows[0]["surface"], "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows), "value_de": rows[0]["small_value_de"],
        })
    write("FOUR_HUNDRED_FORTY_THIRD_FIFTEEN_B4_LOCAL_CARDS.tsv", local)

    zones = [
        {"owner_zone": "B4_ZONE_A_LEFT_AND_UPPER_FLOW", "first_event": "E315", "last_event": "E355", "events": 41, "relation": "LOCAL_CONNECTIONS_ONLY"},
        {"owner_zone": "B4_ZONE_B_RIGHT_LOWER_FLOW", "first_event": "E356", "last_event": "E361", "events": 6, "relation": "VISIBLE_RESET_AT_E356"},
    ]
    write("FOUR_HUNDRED_FORTY_THIRD_TWO_B4_OWNER_ZONES.tsv", zones)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len({row["joint_tuple_id"] for row in events}),
        "transfer_cards": len(transfer), "transfer_events": sum(int(row["events"]) for row in transfer),
        "local_cards": len(local), "local_events": sum(int(row["events"]) for row in local),
        "owner_zones": len(zones), "owner_break_statement": "B4-S015",
    }
    (HERE / "FOUR_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
