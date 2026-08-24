#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b2_liquid_application_four_hundred_thirty_eighth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_22_STATEMENTS.tsv")
    dictionary = read("FOUR_HUNDRED_THIRTY_EIGHTH_B2_46_CARD_DICTIONARY.tsv")
    revisions = {
        "04a3877f0fc81b7597c9": ("L+DY", "abführen; Schluss", "OUTWARD+CLOSE"),
        "54d0e228ca346110af05": ("OT+AIIN", "nächstes Maß", "NEXT+MEASURE"),
        "3ae9a121ba0045b913e8": ("OK+AR", "von dort einsetzen", "SET+SOURCE"),
        "daa1347f456415fe8737": ("OL+SH+E+DY", "mit dem Vorigen kurz absetzen; Schluss", "PREVIOUS+SETTLE+SHORT+CLOSE"),
        "de7321bface5628e35d6": ("L+CHED+DY", "hinausführen; Schluss", "OUTWARD+TRANSFER+CLOSE"),
    }
    for row in events:
        if row["joint_tuple_id"] in revisions:
            row["small_value_de"] = revisions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B2_FINAL_PRODUCTIVE_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_62_EVENTS.tsv", events)

    fluent = {
        "B2-S005": "Dies an die Stelle setzen, durch Seihtuch und Durchlass führen, bemessen, dieselbe Einstellung halten, länger wärmen, abführen und schließen.",
        "B2-S008": "Das nächste Maß nehmen, von dort einsetzen, kurz absetzen und schließen.",
        "B2-S009": "Mit dem Vorigen kurz absetzen und schließen.",
        "B2-S013": "Hinausführen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_22_STATEMENTS.tsv", statements)

    event_by_card: dict[str, list[dict[str, str]]] = {}
    for row in events:
        event_by_card.setdefault(row["joint_tuple_id"], []).append(row)
    for row in dictionary:
        if row["joint_tuple_id"] in revisions:
            row["drawer"] = "B2_PRODUCTIVE_COMPOSITION"
        row["small_values_de"] = "|".join(sorted({event["small_value_de"] for event in event_by_card[row["joint_tuple_id"]]}))
    write("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv", dictionary)

    revised = []
    for joint_id, (composition, value, role) in revisions.items():
        row = event_by_card[joint_id][0]
        revised.append({
            "event_id": row["event_id"], "surface": row["surface"], "joint_tuple_id": joint_id,
            "composition": composition, "small_value_de": value, "role": role,
        })
    write("FOUR_HUNDRED_THIRTY_NINTH_FIVE_FINAL_COMPOSITIONS.tsv", revised)

    local = [row for row in dictionary if row["drawer"] == "B2_LOCAL_WHOLE_CARD"]
    write("FOUR_HUNDRED_THIRTY_NINTH_EIGHT_LOCAL_WHOLE_CARDS.tsv", local)

    trace = []
    dict_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    for row in events:
        d = dict_by_id[row["joint_tuple_id"]]
        trace.append({
            "order": row["order"], "event_id": row["event_id"], "statement_id": row["statement_id"],
            "surface": row["surface"], "drawer": d["drawer"], "small_value_de": row["small_value_de"],
            "owner_zone": row["owner_zone"],
        })
    write("FOUR_HUNDRED_THIRTY_NINTH_B2_62_EVENT_APPRENTICE_TRACE.tsv", trace)

    drawer_order = ["B1_TRANSFER", "B2_PRODUCTIVE_COMPOSITION", "PORTABLE_RECURRENT_WHOLE_CARD", "B2_LOCAL_WHOLE_CARD"]
    drawers = []
    for drawer in drawer_order:
        rows = [row for row in dictionary if row["drawer"] == drawer]
        drawers.append({
            "drawer": drawer, "cards": len(rows), "events": sum(int(row["events"]) for row in rows),
            "instruction": {
                "B1_TRANSFER": "B1-Karte unverändert lesen.",
                "B2_PRODUCTIVE_COMPOSITION": "Aus Richtung, Handlung, Grad, Bezug und Schluss bauen.",
                "PORTABLE_RECURRENT_WHOLE_CARD": "Ganze, seitenübergreifende Produktkarte lernen.",
                "B2_LOCAL_WHOLE_CARD": "Aus dem f82r-Stationsdeck kopieren.",
            }[drawer],
        })
    write("FOUR_HUNDRED_THIRTY_NINTH_FOUR_B2_DRAWERS.tsv", drawers)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(events), "statements": len(statements),
        "drawers": {row["drawer"]: {"cards": int(row["cards"]), "events": int(row["events"])} for row in drawers},
        "local_whole_cards": len(local), "new_final_compositions": len(revised),
    }
    (HERE / "FOUR_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
