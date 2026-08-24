#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
B1 = ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv"
B2 = ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def zone(event_number: int) -> str:
    if event_number < 264:
        return "B3_ZONE_A_UPPER_PAIRED_STATION"
    if event_number < 291:
        return "B3_ZONE_B_MIDDLE_STATION"
    return "B3_ZONE_C_LOWER_STATION"


def main() -> None:
    base = [row for row in read(BASE) if row["record_unit_id"] == "B3"]
    d1 = read(B1)
    d2 = read(B2)
    deck: dict[str, tuple[str, str]] = {}
    for row in d1:
        deck[row["joint_tuple_id"]] = (row["small_value_de"], "B1")
    for row in d2:
        deck[row["joint_tuple_id"]] = (row["small_values_de"], "B2")
    shared = set(deck) & {row["joint_tuple_id"] for row in base}
    events = []
    for order, row in enumerate(base, start=1):
        number = int(row["event_id"][1:])
        value, source = deck.get(row["joint_tuple_id"], (row["concrete_word_reading_de"], "B3_LOCAL"))
        events.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "small_value_de": value, "owner_zone": zone(number),
            "lexicon_source": f"{source}_EXACT_CARD_TRANSFER" if row["joint_tuple_id"] in shared else "B3_LOCAL_LEARNED_CARD",
        })
    write("FOUR_HUNDRED_FORTIETH_B3_86_EVENT_INTERLINEAR.tsv", events)

    translations = {
        "B3-S001": "Länger auffangen und schließen.",
        "B3-S002": "An der Folgestelle länger wärmen und schließen.",
        "B3-S003": "Diesen Posten nach Maß hinausführen und schließen.",
        "B3-S004": "Bemessen, zur Folgestelle gehen und dasselbe verwenden.",
        "B3-S005": "Überführen und schließen.",
        "B3-S006": "Den laufenden Posten zuführen, an die Stelle setzen, weiterführen und schließen.",
        "B3-S007": "Bemessen, dies umsetzen, länger ansetzen und schließen.",
        "B3-S008": "Hinausführen und schließen.",
        "B3-S009": "Dies verwenden.",
        "B3-S010": "An der Einfüllstelle den kurzen Folgeschritt ausführen und schließen.",
        "B3-S011": "Aufstreichen, dies verwenden, umsetzen und abkühlen.",
        "B3-S012": "Den Ansatz kurz absetzen und schließen.",
        "B3-S013": "Bemessen, eine Portion nehmen, dies kurz bereithalten, kurz ansetzen und schließen.",
        "B3-S014": "Wasser in Gang setzen, länger absetzen und schließen.",
        "B3-S015": "Hinausführen und schließen.",
        "B3-S016": "Am Auslass abschließen; nach dem Besitzerwechsel den Ansatz umsetzen und schließen.",
        "B3-S017": "Länger ansetzen und schließen.",
        "B3-S018": "Kurz absetzen und schließen.",
        "B3-S019": "Zum Absetzen stellen und schließen.",
        "B3-S020": "An der Stelle hinausführen und schließen.",
        "B3-S021": "Bemessen; bereit an die Stelle setzen; dies auf Maß bringen; an der Absetzstelle temperieren; dies an der Stelle bereithalten, lokal umsetzen und schließen.",
        "B3-S022": "Die Folgeumsetzung ausführen und schließen.",
        "B3-S023": "Hinausführen und schließen.",
        "B3-S024": "Überführen und schließen.",
        "B3-S025": "Den Ansatz umsetzen und schließen.",
        "B3-S026": "An der Beckenstation den Absetzstand setzen, dies umsetzen, eine Portion zugeben, bereithalten und den Klarpunkt erreichen; nach dem Besitzerwechsel länger auffangen und schließen.",
        "B3-S027": "Den nächsten Schritt länger halten und schließen.",
        "B3-S028": "Länger ansetzen, dann kurz ansetzen und schließen.",
        "B3-S029": "Fortsetzen, die erste Spülung geben, kurz ansetzen und schließen.",
        "B3-S030": "Dies verwenden, auf Maß bringen, Wasser weiterführen, die Folgeumsetzung ausführen und schließen.",
        "B3-S031": "Länger ansetzen und schließen.",
        "B3-S032": "Eine Portion umsetzen, dies umsetzen, im breiten Gefäß das nächste Maß setzen, den kurzen Folgeschritt ausführen und schließen.",
        "B3-S033": "Abführen und schließen.",
        "B3-S034": "Auf Sollstand bringen, bereithalten, zerkleinern, das nächste Maß an der unteren Stelle setzen, kurz absetzen und schließen.",
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
    write("FOUR_HUNDRED_FORTIETH_B3_34_STATEMENTS.tsv", statements)

    transfer = []
    for joint_id in sorted(shared):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        value, source = deck[joint_id]
        transfer.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "latest_source_deck": source, "fixed_value_de": value,
        })
    write("FOUR_HUNDRED_FORTIETH_TWENTY_SIX_B1_B2_TRANSFERS.tsv", transfer)

    local = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events} - shared):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        local.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
            "status": "B3_LOCAL_WHOLE_CARD_PENDING_REVIEW",
        })
    write("FOUR_HUNDRED_FORTIETH_B3_LOCAL_DECK.tsv", local)

    zones = []
    for owner in dict.fromkeys(row["owner_zone"] for row in events):
        rows = [row for row in events if row["owner_zone"] == owner]
        zones.append({
            "owner_zone": owner, "first_event": rows[0]["event_id"], "last_event": rows[-1]["event_id"],
            "events": len(rows), "statements": "|".join(dict.fromkeys(row["statement_id"] for row in rows)),
            "relation_to_next": "VISIBLE_OWNER_RESET_NOT_GLOBAL_FLOW",
        })
    write("FOUR_HUNDRED_FORTIETH_THREE_B3_OWNER_ZONES.tsv", zones)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "exact_cards": len({row["joint_tuple_id"] for row in events}),
        "transferred_cards": len(transfer), "transferred_events": sum(int(row["events"]) for row in transfer),
        "local_cards": len(local), "local_events": sum(int(row["events"]) for row in local),
        "owner_zones": len(zones), "statements_with_owner_break": sum(row["owner_break_inside_statement"] == "YES" for row in statements),
    }
    (HERE / "FOUR_HUNDRED_FORTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
