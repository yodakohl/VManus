#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
B1_DICT = ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def owner_zone(event_number: int) -> str:
    if event_number < 189:
        return "B2_ZONE_A_UPPER_STATIONS"
    if event_number < 198:
        return "B2_ZONE_B_SIDE_POOL"
    if event_number < 203:
        return "B2_ZONE_C_CENTRAL_VESSEL"
    if event_number < 212:
        return "B2_ZONE_D_LOWER_STATIONS"
    return "B2_ZONE_E_TERMINAL_CELL_ROW"


def main() -> None:
    b2 = [row for row in read(BASE) if row["record_unit_id"] == "B2"]
    b1 = {row["joint_tuple_id"]: row for row in read(B1_DICT)}
    shared = set(b1) & {row["joint_tuple_id"] for row in b2}
    events = []
    for order, row in enumerate(b2, start=1):
        number = int(row["event_id"][1:])
        if row["joint_tuple_id"] in shared:
            value = b1[row["joint_tuple_id"]]["small_value_de"]
            source = "B1_EXACT_CARD_TRANSFER"
        elif row["surface_display"] == "sheckhy":
            value = "dies kurz durchführen"
            source = "PREDICTED_SH+E+CKH+Y"
        else:
            value = row["concrete_word_reading_de"]
            source = "B2_LOCAL_LEARNED_CARD"
        events.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"],
            "field_id": row["field_id"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "small_value_de": value, "owner_zone": owner_zone(number), "lexicon_source": source,
        })
    write("FOUR_HUNDRED_THIRTY_FIFTH_B2_62_EVENT_INTERLINEAR.tsv", events)

    translations = {
        "B2-S001": "Überführen und schließen.",
        "B2-S002": "Weiterführen und schließen.",
        "B2-S003": "Eine Portion zugeben, dies nehmen, länger ansetzen und schließen.",
        "B2-S004": "An die Stelle setzen, die zweite Öffnung wählen, hinausführen, länger ansetzen, hinaus seihen und schließen.",
        "B2-S005": "Dies an die Stelle setzen, durch das Seihtuch und den Durchlass führen, bemessen, dieselbe Einstellung halten, länger wärmen, abziehen und schließen.",
        "B2-S006": "Den längeren Folgeposten an die Stelle setzen, dies kurz durchführen und verwenden.",
        "B2-S007": "Frischwasser zugeben und schließen.",
        "B2-S008": "Das Folgemaß nehmen, von dort einsetzen, kurz absetzen und schließen.",
        "B2-S009": "Mit dem Vorigen kurz absetzen und schließen.",
        "B2-S010": "Länger ansetzen, dies verwenden, die erste Öffnung wählen und den Klarauszug nehmen.",
        "B2-S011": "Eine Portion, dasselbe, noch eine Portion, länger ansetzen und schließen.",
        "B2-S012": "Dies abziehen, den Klarauszug kurz bereithalten, länger ansetzen, die benetzte Stelle auf Maß bringen, dies vollständig ansetzen und schließen.",
        "B2-S013": "Hinausführen und schließen.",
        "B2-S014": "Den unteren Ablauf wählen.",
        "B2-S015": "Spülwasser länger ansetzen und schließen.",
        "B2-S016": "An der Stelle aus der Quelle hinausführen, gleiche Anteile und Maß setzen, den längeren Folgeposten bemessen, kurz ansetzen, hineinführen und schließen.",
        "B2-S017": "Warmwasser an der zweiten Öffnung schließen.",
        "B2-S018": "Länger ansetzen und schließen.",
        "B2-S019": "Als Waschung verwenden und schließen.",
        "B2-S020": "Den längeren Folgeschritt ausführen und schließen.",
        "B2-S021": "Länger ansetzen und schließen.",
        "B2-S022": "Den Rest hinausführen und schließen.",
    }
    statements = []
    for statement_id in sorted(translations, key=lambda value: int(value.split("S")[1])):
        rows = [row for row in events if row["statement_id"] == statement_id]
        statements.append({
            "statement_id": statement_id, "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "owner_zones": "|".join(dict.fromkeys(row["owner_zone"] for row in rows)),
            "card_sequence_de": " > ".join(row["small_value_de"] for row in rows),
            "continuous_reading_de": translations[statement_id],
            "cross_line_carry": "E180_E181_READ_ONCE" if statement_id == "B2-S005" else "NONE",
        })
    write("FOUR_HUNDRED_THIRTY_FIFTH_B2_22_STATEMENTS.tsv", statements)

    transfer = []
    for joint_id in sorted(shared):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        transfer.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "B1_drawer": b1[joint_id]["drawer"], "fixed_value_de": b1[joint_id]["small_value_de"],
        })
    write("FOUR_HUNDRED_THIRTY_FIFTH_FOURTEEN_B1_TRANSFERS.tsv", transfer)

    local = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events if row["lexicon_source"] != "B1_EXACT_CARD_TRANSFER"}):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        values = sorted({row["small_value_de"] for row in rows})
        local.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "values_de": "|".join(values),
            "status": "NEW_PRODUCTIVE_PREDICTION" if any(row["lexicon_source"].startswith("PREDICTED") for row in rows) else "B2_LOCAL_WHOLE_CARD",
        })
    write("FOUR_HUNDRED_THIRTY_FIFTH_B2_LOCAL_DECK.tsv", local)

    zones = []
    for zone in dict.fromkeys(row["owner_zone"] for row in events):
        rows = [row for row in events if row["owner_zone"] == zone]
        zones.append({
            "owner_zone": zone, "first_event": rows[0]["event_id"], "last_event": rows[-1]["event_id"],
            "events": len(rows), "statements": "|".join(dict.fromkeys(row["statement_id"] for row in rows)),
            "flow_to_next": "LOCAL_RESET_NOT_GLOBAL_PIPE",
        })
    write("FOUR_HUNDRED_THIRTY_FIFTH_FIVE_OWNER_ZONES.tsv", zones)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "exact_cards": len({row["joint_tuple_id"] for row in events}),
        "B1_shared_cards": len(transfer), "B1_shared_events": sum(int(row["events"]) for row in transfer),
        "B2_local_cards": len(local), "owner_zones": len(zones), "predicted_new_card": "sheckhy=dies kurz durchführen",
    }
    (HERE / "FOUR_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
