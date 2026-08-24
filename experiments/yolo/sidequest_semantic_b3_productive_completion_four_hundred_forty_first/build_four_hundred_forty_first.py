#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b3_station_article_four_hundred_fortieth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FORTIETH_B3_86_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_FORTIETH_B3_34_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_FORTIETH_TWENTY_SIX_B1_B2_TRANSFERS.tsv")
    revisions = {
        "03626ca94cb17800d767": ("SH+EE+DY", "länger absetzen; Schluss"),
        "a84fbe3ad380df345b97": ("CHK+EE+DY", "länger wärmen; Schluss"),
        "90bcf0a9ec0ef56399e6": ("OT+AL", "Folgestelle"),
        "c45ebac60774620561e2": ("OT+E+DY", "kurzer Folgeschritt; Schluss"),
        "4de12cf322dfb76ded1e": ("OT+CHED+DY", "Folgeüberführung; Schluss"),
        "5e8441397e7c0faf042b": ("CHED+Y", "dies überführen"),
        "2bc2ed2630dbdaaa6b59": ("D+AL+CHED+DY", "an der Stelle überführen; Schluss"),
        "ba540da978ea132f6da5": ("P+CHED+AL", "an der Stelle hineinführen"),
        "abb23e5e6936b4147f76": ("SHED+AL", "an der Stelle absetzen"),
        "d784b2abcaf1a3703de2": ("CHED+AIN", "eine Portion überführen"),
        "7d2404c835b10a2c06af": ("OK+AIR", "Laufflüssigkeit in Gang setzen"),
        "b154ff779abe5f196c80": ("S+CHED+AIR", "Laufflüssigkeit weiterführen"),
        "db167f8e9b53eefb58f8": ("OK+SH+E+DY", "kurz absetzen; Schluss"),
        "e0b630cb1b5df5e7105b": ("CTH+Y", "bereit"),
        "7a4bb8136330ee4e6e56": ("S+OR", "Ansatz"),
        "1779decef17481ec2853": ("OT+E+AIIN", "kurzes Folgemaß"),
        "7811a7daff25d476e28d": ("OL+S+AL+Y", "dies an der Stelle fortsetzen"),
    }
    for row in events:
        if row["joint_tuple_id"] in revisions:
            row["small_value_de"] = revisions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B3_PREDICTED_PRODUCTIVE_COMPOSITION"
        elif row["surface"] == "lo":
            row["small_value_de"] = "Abgang"
            row["lexicon_source"] = "B3_LOCAL_WHOLE_CARD"
    write("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_86_EVENTS.tsv", events)

    fluent = {
        "B3-S002": "An der Folgestelle länger wärmen und schließen.",
        "B3-S006": "Dies überführen, an die Stelle setzen, weiterführen und schließen.",
        "B3-S010": "An der Stelle hineinführen, den kurzen Folgeschritt ausführen und schließen.",
        "B3-S012": "Den Ansatz kurz absetzen und schließen.",
        "B3-S014": "Laufflüssigkeit in Gang setzen, länger absetzen und schließen.",
        "B3-S016": "Am Abgang abschließen; nach dem Besitzerwechsel den Ansatz umsetzen und schließen.",
        "B3-S019": "Kurz absetzen und schließen.",
        "B3-S021": "Bemessen; bereit an die Stelle setzen; dies auf Maß bringen; an der Stelle absetzen und temperieren; dies an der Stelle bereithalten, überführen und schließen.",
        "B3-S022": "Die Folgeüberführung ausführen und schließen.",
        "B3-S026": "An der Beckenstation den Absetzstand setzen, dies umsetzen, eine Portion überführen, bereithalten und den Klarpunkt erreichen; nach dem Besitzerwechsel länger auffangen und schließen.",
        "B3-S030": "Dies verwenden, auf Maß bringen, die Laufflüssigkeit weiterführen, die Folgeüberführung ausführen und schließen.",
        "B3-S032": "Eine Portion umsetzen, dies umsetzen, ein kurzes Folgemaß und danach das nächste Maß setzen, den kurzen Folgeschritt ausführen und schließen.",
        "B3-S034": "Auf Sollstand bringen, bereithalten, zerkleinern, das nächste Maß setzen, dies an der Stelle fortsetzen, kurz absetzen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_34_STATEMENTS.tsv", statements)

    table = []
    for joint_id, (composition, value) in revisions.items():
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        table.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "composition": composition, "small_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_FIRST_SEVENTEEN_NEW_COMPOSITIONS.tsv", table)

    transferred_ids = {row["joint_tuple_id"] for row in transfer}
    productive_ids = set(revisions)
    dictionary = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events}, key=lambda jid: min(int(row["order"]) for row in events if row["joint_tuple_id"] == jid)):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        if joint_id in transferred_ids:
            drawer = "B1_B2_TRANSFER"
        elif joint_id in productive_ids:
            drawer = "B3_PRODUCTIVE_COMPOSITION"
        else:
            drawer = "B3_LOCAL_WHOLE_CARD"
        dictionary.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "drawer": drawer,
            "small_values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
        })
    write("FOUR_HUNDRED_FORTY_FIRST_B3_52_CARD_DICTIONARY.tsv", dictionary)

    local = [row for row in dictionary if row["drawer"] == "B3_LOCAL_WHOLE_CARD"]
    write("FOUR_HUNDRED_FORTY_FIRST_NINE_B3_LOCAL_WHOLE_CARDS.tsv", local)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "transfer_cards": sum(row["drawer"] == "B1_B2_TRANSFER" for row in dictionary),
        "productive_cards": sum(row["drawer"] == "B3_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "local_cards": len(local), "new_productive_events": sum(int(row["events"]) for row in table),
    }
    (HERE / "FOUR_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
