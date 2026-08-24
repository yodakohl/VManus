#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_herbal_five_article_grammar_four_hundred_twenty_fifth/FOUR_HUNDRED_TWENTY_FIFTH_HERBAL_100_EVENT_EDITION.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(SOURCE)
    candidates = [
        ("H1", "E002", "ABSCHABEN", 3, 4, 3, 10, "KEEP_RIVAL"),
        ("H1", "E002", "SÄUBERN", 4, 2, 4, 10, "KEEP_RIVAL"),
        ("H1", "E002", "SCHÄLEN", 4, 4, 4, 12, "SELECT"),
        ("H1", "E002", "WASCHEN", 4, 1, 4, 9, "REJECT_DUPLICATES_WASH_DECK"),
        ("H2", "E038", "PASTE", 4, 4, 3, 11, "KEEP_RIVAL"),
        ("H2", "E038", "SALBE", 4, 2, 4, 10, "KEEP_MEDICAL_RIVAL"),
        ("H2", "E038", "BREI", 4, 4, 4, 12, "SELECT"),
        ("H2", "E038", "AUFLAGE", 3, 1, 4, 8, "REJECT_ADDS_USE"),
        ("H3", "E049", "TRANK", 4, 3, 4, 11, "SELECT"),
        ("H3", "E049", "SPÜLUNG", 3, 2, 4, 9, "KEEP_TECHNICAL_RIVAL"),
        ("H3", "E049", "AUSZUG", 3, 3, 4, 10, "KEEP_PRODUCT_RIVAL"),
        ("H3", "E049", "MISCHUNG", 3, 3, 3, 9, "REJECT_TOO_GENERIC"),
        ("H4", "E063", "VERWAHREN", 4, 3, 4, 11, "KEEP_RIVAL"),
        ("H4", "E063", "RUHEN", 3, 2, 4, 9, "KEEP_PROCESS_RIVAL"),
        ("H4", "E063", "LAGERN", 4, 4, 4, 12, "SELECT"),
        ("H4", "E063", "VORRAT", 3, 3, 4, 10, "REJECT_NOUN_IN_ACTION_SLOT"),
        ("H5", "E076", "BLÜTEBEGINN", 3, 1, 3, 7, "REJECT_UNNEEDED_TIME"),
        ("H5", "E076", "ERSTE_ZUTAT", 4, 4, 4, 12, "SELECT"),
        ("H5", "E076", "OBERER_TEIL", 3, 2, 3, 8, "KEEP_PICTURE_RIVAL"),
        ("H5", "E076", "FRÜH", 2, 1, 4, 7, "REJECT_INCOMPLETE_ITEM"),
    ]
    candidate_rows = [
        {"record": record, "event_id": event_id, "candidate_de": candidate.replace("_", " "),
         "local_sequence_fit": local, "shared_grammar_fit": grammar, "brevity": brevity, "total": total, "decision": decision}
        for record, event_id, candidate, local, grammar, brevity, total, decision in candidates
    ]
    write("FOUR_HUNDRED_TWENTY_SIXTH_TWENTY_CANDIDATES.tsv", candidate_rows)

    revisions = {
        "E002": ("abschaben", "schälen", "root/tuber preparation before general processing"),
        "E038": ("Paste", "Brei", "soft material state without application claim"),
        "E049": ("Trank", "Trank", "measure context keeps current leader"),
        "E063": ("verwahren", "lagern", "one verb covers storage and resting"),
        "E076": ("Blütebeginn", "erste Zutat", "subsequent ingredient creates ordered ingredient pair"),
    }
    selected = [
        {"record": next(row["record"] for row in events if row["event_id"] == event_id), "event_id": event_id,
         "surface": next(row["surface"] for row in events if row["event_id"] == event_id),
         "old_value_de": old, "selected_value_de": new, "selection_reason": reason}
        for event_id, (old, new, reason) in revisions.items()
    ]
    write("FOUR_HUNDRED_TWENTY_SIXTH_FIVE_SELECTED_VALUES.tsv", selected)

    revised = []
    for row in events:
        out = dict(row)
        if row["event_id"] in revisions:
            old, new, reason = revisions[row["event_id"]]
            out["small_value_de"] = new
            out["pass426_revision"] = f"{old}->{new}"
            out["pass426_reason"] = reason
        else:
            out["pass426_revision"] = "UNCHANGED"
            out["pass426_reason"] = "not one of five weakest cards"
        revised.append(out)
    write("FOUR_HUNDRED_TWENTY_SIXTH_REVISED_HERBAL_100_EVENT_EDITION.tsv", revised)

    articles = [
        {"record": "H1", "continuous_reading_de": "Eine Knolle schälen und bearbeiten, im Topf mit Wasser ausziehen, den Auszug bemessen und als Gabe anwärmen und bereitstellen.", "selected_weak_card": "CTHOOR=SCHÄLEN"},
        {"record": "H2", "continuous_reading_de": "Spitzen zerstoßen und abpressen, zwei Pressprodukte getrennt führen, im glasierten Gefäß vereinigen und auf weichen Sollstand zu einem Brei bringen.", "selected_weak_card": "CHODAIIN=BREI"},
        {"record": "H3", "continuous_reading_de": "Blütenkraut als Sud auswringen, stehen lassen, nachseihen, den Klarauszug kühlen und eine Reserve später zu einem bemessenen Trank verarbeiten.", "selected_weak_card": "KCHY=TRANK"},
        {"record": "H4", "continuous_reading_de": "Portionen bemessen, abkühlen oder wärmen, einen Auszug nehmen, eine Ansatzportion bilden und den Posten lagern.", "selected_weak_card": "TALAM=LAGERN"},
        {"record": "H5", "continuous_reading_de": "Einen Zutatenansatz beginnen, die erste Zutat bemessen, eine weitere auflegen, waschen, auftragen, Auszug abseihen und jede Gabe messen.", "selected_weak_card": "CHODALY=ERSTE ZUTAT"},
    ]
    write("FOUR_HUNDRED_TWENTY_SIXTH_FIVE_REVISED_ARTICLES.tsv", articles)

    summary = {
        "status": "PASS", "candidate_rows": len(candidate_rows), "selected_values": len(selected),
        "revised_events": sum(row["pass426_revision"] != "UNCHANGED" for row in revised),
        "unchanged_leader": "H3_KCHY_TRANK", "decision": "FOUR_REVISIONS_ONE_RETAINED",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
