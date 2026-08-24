#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b1_dosing_block_four_hundred_thirty_third"
ALL = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    b1 = read(PREV / "FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_66_EVENTS.tsv")
    statements = read(PREV / "FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_21_STATEMENTS.tsv")
    all_events = read(ALL)
    productive = {
        "7db18b2f0fb7ed0fcfd3": "OK+E+DY", "b5fcea1eaed06b2f2291": "OK+AIIN",
        "308e8ea2d5d190c498e8": "OK+AL", "dcda95c81a5460feb191": "OL",
        "9da1b6ac2c929daea697": "K+AIN", "94df4847b7b16c98394a": "OL+K+AIN",
        "dd0ecaf5e27d81befffc": "AL", "dec401773c1f0347793d": "OL+OR",
        "4eab1841ed655c20a348": "SH+E+CKH+AL", "2f1c5e56e8f0ff459065": "AIIN",
        "93f69c38fdedee1598e9": "OK+EE+D+AL", "2cc8bb3c2af19607888f": "CKH+Y",
        "259b2b3b0bf859882e2c": "CHED+DY", "6f7ff8287eddf4da9fdb": "CHED+Y",
        "bc4f1f5c006c74a4d26d": "SH+E+DY", "28ffbc88b97772a75f1e": "OL+CHED+DY",
        "b921a237be883a820352": "Y", "d904bf7b044dd3922781": "CHK+E+Y",
        "276a7c2d74d1143446f4": "OK+Y", "08bd5ca0c2ad137a056d": "OK+E+Y",
        "433713294b25b0a12f66": "L+CHED+AL", "b6b654722e55729cc947": "OT+AR",
        "0275fbf14e07935b0a45": "OK+EE+Y", "74c76d589d44120f647b": "SH+E+OL",
        "2c82523794dcb7d2b343": "O+IIN", "3b70942557b3a40e8030": "SOLK+EE+DY",
        "d68bc8de3bcee09db23c": "SH+CKHE+DY",
    }
    # A conservative apprentice deck: only compositions whose pieces already
    # occur elsewhere in the ten-page working grammar are productive.  The
    # locally learned DL additive deliberately stays outside this set.
    b1_ids = {row["joint_tuple_id"] for row in b1}
    productive = {joint_id: composition for joint_id, composition in productive.items() if joint_id in b1_ids}
    recurrent_whole_candidates = {
        "4d4559019a961b834aa1", "1645e612504fcef59ced", "87411f84689b4f93a303",
        "07913ef9b1fb773cd325",
    }
    recurrent_whole = recurrent_whole_candidates & b1_ids

    dictionary = []
    for index, joint_id in enumerate(sorted(b1_ids, key=lambda jid: min(int(row["order"]) for row in b1 if row["joint_tuple_id"] == jid)), start=1):
        local_rows = [row for row in b1 if row["joint_tuple_id"] == joint_id]
        fixed_rows = [row for row in all_events if row["joint_tuple_id"] == joint_id]
        if joint_id in productive:
            drawer = "PRODUCTIVE_COMPOSITION"
            construction = productive[joint_id]
            apprentice_action = "compose"
        elif joint_id in recurrent_whole:
            drawer = "PORTABLE_RECURRENT_WHOLE_CARD"
            construction = "WHOLE_CARD"
            apprentice_action = "memorize_portably"
        else:
            drawer = "POOL_LOCAL_LEARNED_CARD"
            construction = "WHOLE_CARD"
            apprentice_action = "copy_from_B1_exemplar"
        values = sorted({row["small_value_de"] for row in local_rows})
        assert len(values) == 1
        dictionary.append({
            "card_no": f"B1C{index:02d}", "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({row["surface"] for row in local_rows})),
            "B1_events": len(local_rows), "fixed_page_events": len(fixed_rows),
            "fixed_records": "|".join(sorted({row["record_unit_id"] for row in fixed_rows})),
            "drawer": drawer, "construction": construction,
            "small_value_de": values[0], "apprentice_action": apprentice_action,
        })
    write("FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv", dictionary)

    event_trace = []
    dict_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    for row in b1:
        d = dict_by_id[row["joint_tuple_id"]]
        event_trace.append({
            "order": row["order"], "event_id": row["event_id"], "locus": row["locus"],
            "statement_id": row["statement_id"], "surface": row["surface"],
            "card_no": d["card_no"], "drawer": d["drawer"],
            "small_value_de": row["small_value_de"],
        })
    write("FOUR_HUNDRED_THIRTY_FOURTH_B1_66_EVENT_APPRENTICE_TRACE.tsv", event_trace)

    drawer_rows = []
    for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_RECURRENT_WHOLE_CARD", "POOL_LOCAL_LEARNED_CARD"):
        cards = [row for row in dictionary if row["drawer"] == drawer]
        drawer_rows.append({
            "drawer": drawer, "cards": len(cards),
            "B1_events": sum(int(row["B1_events"]) for row in cards),
            "instruction": {
                "PRODUCTIVE_COMPOSITION": "Baue die Karte aus den gelernten Stämmen.",
                "PORTABLE_RECURRENT_WHOLE_CARD": "Lerne die ganze Karte; sie gilt in mehreren Artikeln.",
                "POOL_LOCAL_LEARNED_CARD": "Kopiere die ganze Karte aus dem B1-Beckenexemplar.",
            }[drawer],
        })
    write("FOUR_HUNDRED_THIRTY_FOURTH_THREE_DRAWERS.tsv", drawer_rows)

    compact = []
    for row in statements:
        compact.append({
            "statement_id": row["statement_id"], "events": row["events"],
            "card_sequence_de": row["card_sequence_de"],
            "continuous_reading_de": row["continuous_reading_de"],
        })
    write("FOUR_HUNDRED_THIRTY_FOURTH_B1_21_CELL_EDITION.tsv", compact)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(event_trace),
        "statements": len(compact),
        "drawers": {row["drawer"]: {"cards": int(row["cards"]), "events": int(row["B1_events"])} for row in drawer_rows},
        "longest_small_value_words": max(len(row["small_value_de"].replace(";", "").split()) for row in dictionary),
    }
    (HERE / "FOUR_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
