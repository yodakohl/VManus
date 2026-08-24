#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_herbal_weak_card_tournament_four_hundred_twenty_sixth/FOUR_HUNDRED_TWENTY_SIXTH_REVISED_HERBAL_100_EVENT_EDITION.tsv"


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
    raw = [
        ("H1", "E001", "KNOLLE", 4, 4, 4, 12, "SELECT"), ("H1", "E001", "WURZEL", 4, 3, 4, 11, "KEEP_RIVAL"),
        ("H1", "E001", "SPEICHERWURZEL", 4, 4, 2, 10, "KEEP_PICTURE_RIVAL"), ("H1", "E001", "TEIL", 2, 4, 4, 10, "REJECT_TOO_GENERIC"),
        ("H2", "E032", "GLASIERTES_GEFÄSS", 4, 1, 2, 7, "REJECT_UNSEEN_SURFACE"), ("H2", "E032", "SCHÜSSEL", 4, 4, 4, 12, "SELECT"),
        ("H2", "E032", "MISCHGEFÄSS", 4, 4, 3, 11, "KEEP_FUNCTION_RIVAL"), ("H2", "E032", "MÖRSER", 3, 3, 4, 10, "KEEP_TOOL_RIVAL"),
        ("H3", "E039", "BLÜTENKRAUT", 4, 4, 4, 12, "SELECT"), ("H3", "E039", "BLÜTEN", 4, 3, 4, 11, "KEEP_RIVAL"),
        ("H3", "E039", "KRONE", 3, 4, 4, 11, "KEEP_PICTURE_RIVAL"), ("H3", "E039", "KRAUT", 3, 4, 4, 11, "KEEP_GENERIC_RIVAL"),
        ("H4", "E060", "ABKÜHLEN", 4, 4, 4, 12, "SELECT"), ("H4", "E060", "RUHEN", 3, 3, 4, 10, "KEEP_RIVAL"),
        ("H4", "E060", "BEISEITE", 2, 3, 4, 9, "REJECT_NO_OPERATION"), ("H4", "E060", "SCHLIESSEN", 2, 2, 4, 8, "REJECT_DUPLICATES_CLOSE"),
        ("H5", "E096", "GEBRAUCHSAUSZUG", 3, 2, 2, 7, "REJECT_REDUNDANT_PRODUCT"), ("H5", "E096", "AUSZUG", 3, 3, 4, 10, "KEEP_PRODUCT_RIVAL"),
        ("H5", "E096", "AUSZIEHEN", 4, 4, 4, 12, "SELECT"), ("H5", "E096", "ABSEIHEN", 3, 2, 4, 9, "REJECT_DUPLICATES_PRIOR_STRAIN"),
    ]
    candidates = [
        {"record": record, "event_id": event_id, "candidate_de": candidate.replace("_", " "),
         "local_sequence_fit": local, "independent_support": support, "brevity": brevity, "total": total, "decision": decision}
        for record, event_id, candidate, local, support, brevity, total, decision in raw
    ]
    write("FOUR_HUNDRED_TWENTY_SEVENTH_TWENTY_CANDIDATES.tsv", candidates)

    decisions = {
        "E001": ("Knolle", "Knolle", "retained from visible red underground swellings"),
        "E032": ("glasiertes Gefäß", "Schüssel", "container function remains but unseen glazing is removed"),
        "E039": ("Blütenkraut", "Blütenkraut", "retained from visibly flower-rich crown"),
        "E060": ("abkühlen; Schluss", "abkühlen; Schluss", "retained by three other cooling cards"),
        "E096": ("Gebrauchsauszug", "ausziehen", "verb completes take-extract-use sequence without product duplication"),
    }
    selected = []
    for event_id, (old, new, reason) in decisions.items():
        source = next(row for row in events if row["event_id"] == event_id)
        selected.append({"record": source["record"], "event_id": event_id, "surface": source["surface"], "old_value_de": old, "selected_value_de": new, "reason": reason, "changed": "YES" if old != new else "NO"})
    write("FOUR_HUNDRED_TWENTY_SEVENTH_FIVE_DECISIONS.tsv", selected)

    revised = []
    for row in events:
        out = dict(row)
        if row["event_id"] in decisions:
            old, new, reason = decisions[row["event_id"]]
            out["small_value_de"] = new
            out["pass427_decision"] = "REVISED" if old != new else "RETAINED_AFTER_COMPARISON"
            out["pass427_reason"] = reason
        else:
            out["pass427_decision"] = "UNCHANGED"
            out["pass427_reason"] = "outside target set"
        revised.append(out)
    write("FOUR_HUNDRED_TWENTY_SEVENTH_REVISED_HERBAL_100_EVENT_EDITION.tsv", revised)

    image_process = [
        {"record": "H1", "target": "Knolle", "source": "IMAGE", "visible_basis": "paired red underground swellings", "process_basis": "none required"},
        {"record": "H2", "target": "Schüssel", "source": "PROCESS", "visible_basis": "no vessel drawn", "process_basis": "two preparations combined before soft mash"},
        {"record": "H3", "target": "Blütenkraut", "source": "IMAGE", "visible_basis": "many small blue flowers in crown", "process_basis": "material enters decoction chain"},
        {"record": "H4", "target": "abkühlen", "source": "PROCESS_FAMILY", "visible_basis": "no cooling object drawn", "process_basis": "independent cooling cards in H3 B1 B3"},
        {"record": "H5", "target": "ausziehen", "source": "PROCESS", "visible_basis": "no extraction tool drawn", "process_basis": "take ingredient then extract then use"},
    ]
    write("FOUR_HUNDRED_TWENTY_SEVENTH_IMAGE_PROCESS_PROVENANCE.tsv", image_process)

    articles = [
        {"record": "H1", "reading_de": "Knolle schälen und bearbeiten, im Topf wässern, Auszug bemessen und die Gabe anwärmen."},
        {"record": "H2", "reading_de": "Zwei Pressprodukte getrennt führen, in der Schüssel vereinigen und auf weichen Sollstand zu Brei bringen."},
        {"record": "H3", "reading_de": "Blütenkraut als Sud auswringen, stehen lassen, nachseihen, klären und später als Trank bemessen."},
        {"record": "H4", "reading_de": "Portion bemessen, abkühlen oder wärmen, Auszug nehmen, Ansatzportion bilden und lagern."},
        {"record": "H5", "reading_de": "Erste und weitere Zutat bereiten, waschen und auftragen; später Zutat nehmen, ausziehen und gebrauchen."},
    ]
    write("FOUR_HUNDRED_TWENTY_SEVENTH_FIVE_ARTICLE_READINGS.tsv", articles)

    summary = {
        "status": "PASS", "candidates": len(candidates), "decisions": len(selected),
        "revisions": sum(row["changed"] == "YES" for row in selected), "retentions": sum(row["changed"] == "NO" for row in selected),
        "decision": "REMOVE_UNSEEN_GLAZE_AND_PRODUCT_DUPLICATION",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
