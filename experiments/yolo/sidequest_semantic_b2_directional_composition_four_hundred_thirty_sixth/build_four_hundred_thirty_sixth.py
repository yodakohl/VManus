#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b2_station_article_four_hundred_thirty_fifth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_THIRTY_FIFTH_B2_62_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_FIFTH_B2_22_STATEMENTS.tsv")
    revisions = {
        "f329f2051370174e9a38": ("L+CHE+CKH+Y", "dies zum Durchlass führen", "OUTWARD+PASSAGE+CURRENT"),
        "ba8142680851f24c9ff2": ("L+CHED", "hinausführen", "OUTWARD+TRANSFER"),
        "c1db6b0a28d5cbb5d3d2": ("L+CHE+CKHE+DY", "hinaus seihen; Schluss", "OUTWARD+STRAIN+CLOSE"),
        "4a7a6326ac95a8809302": ("OK+AL+Y", "dies an die Stelle setzen", "SET+TARGET+CURRENT"),
        "0f15effeca7ab10bb026": ("L+CHED+AR", "von dort hinausführen", "OUTWARD+TRANSFER+SOURCE"),
        "65df3cd9e59060042d47": ("P+CHED+DY", "hineinführen; Schluss", "INWARD+TRANSFER+CLOSE"),
        "f2af6326898fb5b490a4": ("L+O+CHED+DY", "hinausführen; Schluss", "OUTWARD+TRANSFER+CLOSE; O_UNRESOLVED"),
    }
    for row in events:
        if row["joint_tuple_id"] in revisions:
            row["small_value_de"] = revisions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B2_PREDICTED_DIRECTIONAL_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_62_EVENTS.tsv", events)

    fluent = {
        "B2-S004": "An die Stelle setzen, dies zum Durchlass führen, hinausführen, länger ansetzen, hinaus seihen und schließen.",
        "B2-S005": "Dies an die Stelle setzen, durch das Seihtuch und den Durchlass führen, bemessen, dieselbe Einstellung halten, länger wärmen, abziehen und schließen.",
        "B2-S016": "An der Stelle von dort hinausführen, gleiche Anteile und Maß setzen, den längeren Folgeposten bemessen, kurz ansetzen, hineinführen und schließen.",
        "B2-S022": "Hinausführen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_22_STATEMENTS.tsv", statements)

    substitution = [
        {"construction": "CHED", "direction": "NEUTRAL", "path_or_address": "NONE", "referent": "NONE", "close": "NO", "value_de": "überführen"},
        {"construction": "L+CHED", "direction": "OUT", "path_or_address": "NONE", "referent": "NONE", "close": "NO", "value_de": "hinausführen"},
        {"construction": "P+CHED+DY", "direction": "IN", "path_or_address": "NONE", "referent": "NONE", "close": "YES", "value_de": "hineinführen; Schluss"},
        {"construction": "L+CHED+AR", "direction": "OUT", "path_or_address": "SOURCE", "referent": "NONE", "close": "NO", "value_de": "von dort hinausführen"},
        {"construction": "L+CHE+CKH+Y", "direction": "OUT", "path_or_address": "PASSAGE", "referent": "CURRENT", "close": "NO", "value_de": "dies zum Durchlass führen"},
        {"construction": "L+CHE+CKHE+DY", "direction": "OUT", "path_or_address": "STRAIN", "referent": "NONE", "close": "YES", "value_de": "hinaus seihen; Schluss"},
        {"construction": "OK+AL+Y", "direction": "SET", "path_or_address": "TARGET", "referent": "CURRENT", "close": "NO", "value_de": "dies an die Stelle setzen"},
        {"construction": "L+O+CHED+DY", "direction": "OUT", "path_or_address": "O_UNRESOLVED", "referent": "NONE", "close": "YES", "value_de": "hinausführen; Schluss"},
    ]
    write("FOUR_HUNDRED_THIRTY_SIXTH_DIRECTIONAL_SUBSTITUTION_TABLE.tsv", substitution)

    targets = []
    for joint_id, (composition, value, role) in revisions.items():
        row = [row for row in events if row["joint_tuple_id"] == joint_id]
        assert len(row) == 1
        targets.append({
            "event_id": row[0]["event_id"], "statement_id": row[0]["statement_id"],
            "surface": row[0]["surface"], "joint_tuple_id": joint_id,
            "composition": composition, "new_value_de": value, "role": role,
        })
    write("FOUR_HUNDRED_THIRTY_SIXTH_SEVEN_NEW_COMPOSITIONS.tsv", targets)

    shared_ids = {row["joint_tuple_id"] for row in read("FOUR_HUNDRED_THIRTY_FIFTH_FOURTEEN_B1_TRANSFERS.tsv")}
    predicted_ids = {row["joint_tuple_id"] for row in events if row["lexicon_source"].startswith("PREDICTED") or row["lexicon_source"] == "B2_PREDICTED_DIRECTIONAL_COMPOSITION"}
    dictionary = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events}, key=lambda jid: min(int(row["order"]) for row in events if row["joint_tuple_id"] == jid)):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        if joint_id in shared_ids:
            drawer = "B1_TRANSFER"
        elif joint_id in predicted_ids:
            drawer = "B2_PRODUCTIVE_COMPOSITION"
        else:
            drawer = "B2_LOCAL_WHOLE_CARD"
        dictionary.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "drawer": drawer,
            "small_values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
        })
    write("FOUR_HUNDRED_THIRTY_SIXTH_B2_46_CARD_DICTIONARY.tsv", dictionary)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "B1_transfer_cards": sum(row["drawer"] == "B1_TRANSFER" for row in dictionary),
        "B2_productive_cards": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "B2_local_cards": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary),
        "old_rest_word_removed": True,
    }
    (HERE / "FOUR_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
