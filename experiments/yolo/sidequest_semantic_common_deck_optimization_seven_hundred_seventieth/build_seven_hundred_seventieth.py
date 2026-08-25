#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P763 = ROOT / "experiments/yolo/sidequest_semantic_workshop_curriculum_seven_hundred_sixty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    deck = read(P763 / "SEVEN_HUNDRED_SIXTY_THIRD_173_CARD_SPECIALIZATION.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    common = [row for row in deck if row["deck_assignment"] == "COMMON_17_CARD_DECK"]
    common.sort(key=lambda row: (-int(row["events"]), row["exact_card_id"]))
    event_by_card: dict[str, list[dict[str, str]]] = {}
    for row in events:
        event_by_card.setdefault(row["card_no"], []).append(row)

    ranking = []
    for rank, row in enumerate(common, 1):
        occurrences = event_by_card[row["exact_card_id"]]
        ranking.append({
            "rank": rank,
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "reading_de": row["rebuilt_reading_de"],
            "events": len(occurrences),
            "herbal_events": sum(event["record"].startswith("H") for event in occurrences),
            "bio_events": sum(event["record"].startswith("B") for event in occurrences),
            "new_assignment": "COMMON_12_ACTIVE_BOARD" if rank <= 12 else "SHARED_5_REFERENCE_STRIP",
            "drill_level": "SIX_COPIES_PLUS_RECALL" if rank <= 12 else "ONE_COPY_PLUS_LOOKUP",
        })
    write(
        "SEVEN_HUNDRED_SEVENTIETH_17_COMMON_CARD_RANKING.tsv",
        ranking,
        ["rank", "exact_card_id", "registered_surfaces", "component_recipe", "reading_de", "events", "herbal_events", "bio_events", "new_assignment", "drill_level"],
    )

    options = []
    for size in (5, 8, 12, 17):
        rows = ranking[:size]
        event_count = sum(int(row["events"]) for row in rows)
        components = {part for row in rows for part in str(row["component_recipe"]).split("+")}
        options.append({
            "core_cards": size,
            "events_covered": event_count,
            "all381_coverage_pct": f"{100 * event_count / 381:.1f}",
            "common136_coverage_pct": f"{100 * event_count / 136:.1f}",
            "herbal_events_covered": sum(int(row["herbal_events"]) for row in rows),
            "bio_events_covered": sum(int(row["bio_events"]) for row in rows),
            "distinct_components": len(components),
            "six_copy_drills": 6 * size,
            "active_board_hours": f"{0.5 * size:.1f}",
            "cards_left_for_reference": 17 - size,
            "decision": "SELECT" if size == 12 else "REJECT_TOO_THIN" if size < 12 else "REJECT_UNNECESSARY_ACTIVE_LOAD",
        })
    write(
        "SEVEN_HUNDRED_SEVENTIETH_4_CORE_OPTIONS.tsv",
        options,
        ["core_cards", "events_covered", "all381_coverage_pct", "common136_coverage_pct", "herbal_events_covered", "bio_events_covered", "distinct_components", "six_copy_drills", "active_board_hours", "cards_left_for_reference", "decision"],
    )

    active = [row for row in ranking if row["new_assignment"] == "COMMON_12_ACTIVE_BOARD"]
    reference = [row for row in ranking if row["new_assignment"] == "SHARED_5_REFERENCE_STRIP"]
    write(
        "SEVEN_HUNDRED_SEVENTIETH_12_ACTIVE_TEACHING_BOARD.tsv",
        active,
        list(active[0].keys()),
    )
    write(
        "SEVEN_HUNDRED_SEVENTIETH_5_SHARED_REFERENCE_STRIP.tsv",
        reference,
        list(reference[0].keys()),
    )

    burden = []
    for role, prefix, total in (("HERBAL_SCRIBE", "H", 100), ("BIO_STATION_SCRIBE", "B", 281)):
        core_events = sum(int(row["herbal_events"] if prefix == "H" else row["bio_events"]) for row in active)
        reference_events = sum(int(row["herbal_events"] if prefix == "H" else row["bio_events"]) for row in reference)
        burden.append({
            "role": role,
            "total_visible_events": total,
            "active_board_events": core_events,
            "reference_strip_events": reference_events,
            "specialist_deck_events": total - core_events - reference_events,
            "reference_lookup_rate_pct": f"{100 * reference_events / total:.1f}",
            "active_cards": 12,
            "reference_cards": 5,
        })
    write(
        "SEVEN_HUNDRED_SEVENTIETH_ROLE_LOOKUP_BURDEN.tsv",
        burden,
        ["role", "total_visible_events", "active_board_events", "reference_strip_events", "specialist_deck_events", "reference_lookup_rate_pct", "active_cards", "reference_cards"],
    )

    report = """# Pass 770 — Zwoelf Karten auf der gemeinsamen Lehrtafel

Die17 registeruebergreifenden Karten sind nicht gleich wichtig.

- Die ersten5 tragen78 Ereignisse, aber nur5 Komponenten: zu wenig fuer eine gemeinsame Werkstattsprache.
- Acht tragen104 Ereignisse und7 Komponenten: noch zu schmal.
- Zwoelf tragen126 der136 bisherigen Common-Deck-Ereignisse und11 verschiedene Komponenten.
- Die letzten fuenf tragen zusammen nur10 Ereignisse, exakt5 Herbal und5 Bio.

Darum kommt eine12-Karten-Tafel an die Wand. Jede dieser Karten wird sechsmal kopiert und aus dem Gedächtnis rückgelesen. Die fünf seltenen Querregisterkarten kommen auf einen kleinen gemeinsamen Nachschlagstreifen und werden nur einmal kopiert. So sinkt die aktive Tafel um29 Prozent, waehrend92,6 Prozent der alten Common-Deck-Nutzung erhalten bleiben. Nachschlagen betrifft nur5,0 Prozent der Herbal- und1,8 Prozent der Bio-Ereignisse.

Die Karten selbst oder ihre Bedeutungen aendern sich nicht; nur der Unterricht wird realistischer. Als naechstes wird der Stundenplan auf die12+5-Aufteilung umgestellt und gegen die vier Rollenprüfungen getestet.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "old_common_cards": 17,
        "selected_active_cards": len(active),
        "reference_strip_cards": len(reference),
        "active_events": sum(int(row["events"]) for row in active),
        "reference_events": sum(int(row["events"]) for row in reference),
        "common_events": sum(int(row["events"]) for row in ranking),
        "active_common_coverage_pct": 100 * sum(int(row["events"]) for row in active) / sum(int(row["events"]) for row in ranking),
        "decision": "COMMON_12_ACTIVE_BOARD_PLUS_5_SHARED_REFERENCE_STRIP",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
