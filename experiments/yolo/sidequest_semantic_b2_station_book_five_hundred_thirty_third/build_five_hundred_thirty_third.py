#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_events = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    b2 = [row for row in all_events if row["record"] == "B2"]
    prior_cards = {
        row["card_no"] for row in all_events if row["record"].startswith("H") or row["record"] == "B1"
    }
    stations = [
        ("ST01", range(167, 189), "B2_UPPER_PAIRED_BASINS_AND_CYLINDER", "oberes Beckenpaar mit Zylinder"),
        ("ST02", range(189, 198), "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE", "mittleres linkes Handgerät mit Inline-Knoten"),
        ("ST03", range(198, 203), "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION", "mittlere rechte, bildlich unklare Station"),
        ("ST04", range(203, 212), "B2_LOWER_GREEN_MULTI_FIGURE_POOL", "unteres grünes Mehrfigurenbecken"),
        ("ST05", range(212, 229), "B2_LOWER_POOL_EDGE_STATIONS", "kleine Randstationen des unteren Beckens"),
    ]
    station_for = {
        f"E{number:03d}": (station_id, owner_id, owner_de)
        for station_id, numbers, owner_id, owner_de in stations
        for number in numbers
    }

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in b2:
        by_card[row["card_no"]].append(row)
    dictionary: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"B2 reading drift {card_no}: {readings}")
        dictionary.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "occurrences": str(len(rows)),
                "surfaces": "|".join(dict.fromkeys(row["renderer_final_surface"] for row in rows)),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "shared_with_herbal_or_b1": "YES" if card_no in prior_cards else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_THIRD_FORTY_SIX_B2_CARD_DICTIONARY.tsv", dictionary)

    event_rows: list[dict[str, str]] = []
    for row in b2:
        station_id, owner_id, owner_de = station_for[row["event_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "station_id": station_id,
                "visible_owner_id": owner_id,
                "visible_owner_de": owner_de,
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "invariant_card_reading_de": row["apprentice_spoken_reading_de"],
                "primitive": row["procedure_tokens"],
                "minimum_source_clause_de": row["apprentice_spoken_reading_de"].replace(" · ", " "),
                "terminal": "YES" if "CLOSE" in row["procedure_tokens"].split(">") else "NO",
                "global_network_edge": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_THIRD_SIXTY_TWO_B2_EVENT_INTERLINEAR.tsv", event_rows)

    fluent = {
        "B2-S001": "Den Posten umsetzen und schließen.",
        "B2-S002": "Fortsetzen, umsetzen und schließen.",
        "B2-S003": "Eine Portion ansetzen, den laufenden Posten länger ansetzen und schließen.",
        "B2-S004": "Die Zielstelle setzen, durch den Durchlass führen und umsetzen, länger ansetzen, noch einmal kurz durch den Durchlass führen und schließen.",
        "B2-S005": "Den Posten an der Zielstelle ansetzen, nach Maß auffangen, durch den Durchlass führen, zwei Maße setzen, bis bereit fortsetzen, länger wärmen, abführen und schließen.",
        "B2-S006": "Danach den Posten länger ansetzen, die Zielstelle setzen und ihn kurz am Durchlass halten.",
        "B2-S007": "Kurz halten und schließen.",
        "B2-S008": "Danach das Maß setzen, von dort ansetzen, absetzen und schließen.",
        "B2-S009": "Fortsetzen, kurz halten und schließen.",
        "B2-S010": "Den Posten länger ansetzen, weiter ansetzen und den Empfangsbestand übernehmen.",
        "B2-S011": "Eine Portion von dort nehmen, eine weitere Portion länger ansetzen und schließen.",
        "B2-S012": "An der unklaren Station den Posten führen und abziehen. Ohne Bildverbindung zum unteren Becken wechseln: Empfangsbestand übernehmen, kurz bereit halten, länger ansetzen und führen, nach Maß vollständig ansetzen und schließen.",
        "B2-S013": "Im unteren Becken führen, umsetzen und schließen.",
        "B2-S014": "Von dort weiterführen.",
        "B2-S015": "Den Posten kurz halten, länger ansetzen und schließen.",
        "B2-S016": "Zielstelle setzen, von dort umsetzen, teilen und messen; danach länger ansetzen, das Maß setzen, kurz ansetzen, hinein umsetzen und schließen.",
        "B2-S017": "An der Zielstelle kurz abkühlen und halten; Zielstelle schließen.",
        "B2-S018": "Länger ansetzen und schließen.",
        "B2-S019": "Abkühlen, absetzen und schließen.",
        "B2-S020": "Danach länger halten und schließen.",
        "B2-S021": "Länger ansetzen und schließen.",
        "B2-S022": "Durch den Arbeitsgang führen, umsetzen und schließen.",
    }
    statement_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_members[row["statement_id"]].append(row)
    cells: list[dict[str, str]] = []
    for statement_id, members in statement_members.items():
        owner_ids = list(dict.fromkeys(row["visible_owner_id"] for row in members))
        cells.append(
            {
                "statement_id": statement_id,
                "station_ids": "|".join(dict.fromkeys(row["station_id"] for row in members)),
                "visible_owner_ids": "|".join(owner_ids),
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_literal_de": "; ".join(row["invariant_card_reading_de"] for row in members),
                "fluent_station_reading_de": fluent[statement_id],
                "terminal": "YES" if any(row["terminal"] == "YES" for row in members) else "NO",
                "crosses_visible_owner_boundary": "YES" if len(owner_ids) > 1 else "NO",
                "global_network_claim": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_THIRD_TWENTY_TWO_B2_OPERATING_CELLS.tsv", cells)

    station_rows: list[dict[str, str]] = []
    for station_id, numbers, owner_id, owner_de in stations:
        members = [row for row in event_rows if row["station_id"] == station_id]
        member_cells = [row for row in cells if station_id in row["station_ids"].split("|")]
        station_rows.append(
            {
                "station_id": station_id,
                "visible_owner_id": owner_id,
                "visible_owner_de": owner_de,
                "event_ids": "|".join(row["event_id"] for row in members),
                "events": str(len(members)),
                "statement_ids": "|".join(row["statement_id"] for row in member_cells),
                "closed_cells_touching_station": str(sum(row["terminal"] == "YES" for row in member_cells)),
                "open_cells_touching_station": str(sum(row["terminal"] == "NO" for row in member_cells)),
                "relation_to_next_station": "TEXT_ORDER_ONLY_NO_VISIBLE_NETWORK_EDGE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_THIRD_FIVE_B2_STATIONS.tsv", station_rows)

    shared = [row for row in dictionary if row["shared_with_herbal_or_b1"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_THIRD_FIFTEEN_PRIOR_SHARED_CARDS.tsv", shared)

    lines = [
        "# f82r / B2 — Fünf lokale Stationsbücher auf einer Seite",
        "",
        "Die Textreihenfolge ist erhalten; zwischen den Stationen wird keine unsichtbare Leitung ergänzt.",
        "",
    ]
    for station in station_rows:
        lines.extend([f"## {station['station_id']}: {station['visible_owner_de']}", ""])
        for cell in cells:
            if station["station_id"] in cell["station_ids"].split("|"):
                lines.append(f"- {cell['statement_id']}: {cell['fluent_station_reading_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_THIRTY_THIRD_COMPLETE_B2_STATION_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    summary = {
        "status": "PASS",
        "page": "f82r",
        "record": "B2",
        "events": len(event_rows),
        "statements": len(cells),
        "closed_cells": sum(row["terminal"] == "YES" for row in cells),
        "open_cells": sum(row["terminal"] == "NO" for row in cells),
        "visible_stations": len(station_rows),
        "station_event_counts": {row["station_id"]: int(row["events"]) for row in station_rows},
        "cross_owner_statements": [row["statement_id"] for row in cells if row["crosses_visible_owner_boundary"] == "YES"],
        "exact_cards": len(dictionary),
        "shared_prior_cards": len(shared),
        "global_network_edges_added": 0,
    }
    (HERE / "FIVE_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
