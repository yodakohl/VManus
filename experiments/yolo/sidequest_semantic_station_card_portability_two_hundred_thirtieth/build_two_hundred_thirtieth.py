#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = ROOT / "experiments/yolo/sidequest_semantic_f83r_station_functions_two_hundred_twenty_ninth/TWO_HUNDRED_TWENTY_NINTH_THIRTY_FIVE_OWNED_EVENTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify(total: int, pages: int, owners: int) -> str:
    if total >= 3 and owners >= 3:
        return "STRONG_PORTABLE_ACTION_OR_CONTROL"
    if total >= 2 and owners >= 2:
        return "TENTATIVE_PORTABLE_ACTION_OR_CONTROL"
    return "LOCAL_LEARNED_WHOLE_CARD"


def main() -> None:
    targets = read(TARGET)
    all_events = read(EVENTS)
    target_ids = {row["event_id"] for row in targets}
    target_cards = {row["master_card_id"] for row in targets}
    station_by_event = {row["event_id"]: row["station_id"] for row in targets}
    selected = [row for row in all_events if row["master_card_id"] in target_cards]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        grouped[row["master_card_id"]].append(row)

    card_rows: list[dict[str, object]] = []
    class_by_card: dict[str, str] = {}
    for card_id in sorted(grouped):
        rows = grouped[card_id]
        pages = sorted({row["page"] for row in rows})
        owners = sorted({row["visible_owner"] for row in rows})
        target_rows = [row for row in rows if row["event_id"] in target_ids]
        outside = [row for row in rows if row["event_id"] not in target_ids]
        status = classify(len(rows), len(pages), len(owners))
        class_by_card[card_id] = status
        examples = [f"{row['event_id']}:{row['page']}:{row['visible_owner']}" for row in outside[:3]]
        card_rows.append({
            "master_card_id": card_id,
            "portable_value_de": rows[0]["portable_value_de"],
            "target_station_ids": "|".join(sorted({station_by_event[row["event_id"]] for row in target_rows})),
            "target_occurrences": len(target_rows),
            "all_occurrences": len(rows),
            "outside_station_occurrences": len(outside),
            "page_count": len(pages),
            "pages": "|".join(pages),
            "visible_owner_count": len(owners),
            "portability_class": status,
            "dictionary_action": "KEEP_GENERIC_PORTABLE_VALUE" if status != "LOCAL_LEARNED_WHOLE_CARD" else "KEEP_AS_LOCAL_WHOLE_CARD_ONLY",
            "station_expansion_rule": "Add the visible station noun locally; do not insert it into the card value.",
            "outside_examples": " || ".join(examples) if examples else "NONE_OUTSIDE_TARGET",
        })

    occurrence_rows: list[dict[str, object]] = []
    for row in selected:
        occurrence_rows.append({
            "event_id": row["event_id"],
            "master_card_id": row["master_card_id"],
            "portable_value_de": row["portable_value_de"],
            "page": row["page"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "field_id": row["field_id"],
            "visible_owner": row["visible_owner"],
            "terminal_status": row["terminal_status"],
            "is_r229_station_event": "YES" if row["event_id"] in target_ids else "NO",
            "r229_station_id": station_by_event.get(row["event_id"], "OUTSIDE_R229_STATIONS"),
            "portability_class": class_by_card[row["master_card_id"]],
        })

    station_rows: list[dict[str, object]] = []
    for station_id in sorted({row["station_id"] for row in targets}):
        rows = [row for row in targets if row["station_id"] == station_id]
        counts = Counter(class_by_card[row["master_card_id"]] for row in rows)
        local_cards = sorted({row["master_card_id"] for row in rows if class_by_card[row["master_card_id"]] == "LOCAL_LEARNED_WHOLE_CARD"})
        station_rows.append({
            "station_id": station_id,
            "target_events": len(rows),
            "strong_portable_events": counts["STRONG_PORTABLE_ACTION_OR_CONTROL"],
            "tentative_portable_events": counts["TENTATIVE_PORTABLE_ACTION_OR_CONTROL"],
            "local_whole_card_events": counts["LOCAL_LEARNED_WHOLE_CARD"],
            "transferable_event_total": counts["STRONG_PORTABLE_ACTION_OR_CONTROL"] + counts["TENTATIVE_PORTABLE_ACTION_OR_CONTROL"],
            "local_whole_card_ids": "|".join(local_cards) if local_cards else "NONE",
            "interpretive_result": "CORE_FUNCTION_PORTABLE__SPECIALIZATION_LOCAL" if local_cards else "FUNCTION_FULLY_PORTABLE",
        })

    write(OUT / "TWO_HUNDRED_THIRTIETH_TWENTY_SEVEN_CARD_PORTABILITY.tsv", card_rows)
    write(OUT / "TWO_HUNDRED_THIRTIETH_ONE_HUNDRED_FIFTY_TWO_OCCURRENCES.tsv", occurrence_rows)
    write(OUT / "TWO_HUNDRED_THIRTIETH_THREE_STATION_PORTABILITY.tsv", station_rows)

    strong = sum(row["portability_class"] == "STRONG_PORTABLE_ACTION_OR_CONTROL" for row in card_rows)
    tentative = sum(row["portability_class"] == "TENTATIVE_PORTABLE_ACTION_OR_CONTROL" for row in card_rows)
    local = sum(row["portability_class"] == "LOCAL_LEARNED_WHOLE_CARD" for row in card_rows)
    report = [
        "# Pass 230 — tragen die f83r-Stationskarten außerhalb ihrer Bilder?",
        "",
        f"Die 35 Stationsereignisse enthalten 27 verschiedene exakte Karten. Davon sind {strong} stark portable, {tentative} vorläufig portable und {local} lokale gelernte Ganzkarten. Zusammen besitzen die 27 Karten 152 Vorkommen; 117 davon liegen außerhalb der drei eben benannten Stationen.",
        "",
        "Damit bleibt die saubere Trennung erhalten: `bemessen`, `Sollwert`, `dies`, `einsetzen`, `überführen`, `kurz/lange einwirken`, `kurz absetzen`, `abführen`, `Portion` und ähnliche Werte sind allgemeine Werkstattaktionen oder Kontrollen. Die Nomen Sammelstelle, Haltegefäß und Absetzgefäß stammen aus dem jeweiligen sichtbaren Besitzer und dürfen nicht ins Kartenwörterbuch zurückgeschrieben werden.",
        "",
        "Station 1 besteht aus neun portablen Kartenereignissen und nur einer lokalen Spezialkarte (`Langwärmen; Schluss`). Station 2 hat acht portable und eine lokale (`Postentransfer`). Station 3 hat zehn portable und sechs lokale Spezialkarten: Zielzuführung, Vorbereitungstransfer, Quellposten, Laufeinsatz, Langabsetzen und Abzug. Gerade diese lokalen Karten geben dem dritten Gefäß seine konkrete Arbeitsteilung.",
        "",
        "Der nächste produktive Schritt ist deshalb kein neues Gesamtmodell, sondern die acht lokalen Ganzkarten als kleines f83r-Apparaturlexikon zu verbinden: Welche bilden Eingabe, Aufenthalt, Ausgabe und Wechsel zur nächsten Station?",
    ]
    (OUT / "TWO_HUNDRED_THIRTIETH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "target_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "target_events": len(targets),
        "target_cards": len(card_rows),
        "all_occurrences": len(occurrence_rows),
        "outside_target_occurrences": sum(row["is_r229_station_event"] == "NO" for row in occurrence_rows),
        "strong_portable_cards": strong,
        "tentative_portable_cards": tentative,
        "local_whole_cards": local,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
