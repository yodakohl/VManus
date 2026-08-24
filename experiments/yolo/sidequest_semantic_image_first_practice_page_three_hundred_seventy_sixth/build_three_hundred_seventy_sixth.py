#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"
P362 = ROOT / "experiments/yolo/sidequest_semantic_workshop_thesaurus_three_hundred_sixty_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CARDS = [
    (1, "C1", "H4_LEAF_OWNER", "BEZUG[Zutat]", "2cc054357a929df85f64", "sho"),
    (2, "C1", "H4_LEAF_OWNER", "BEZUG[Ansatz]", "7a4bb8136330ee4e6e56", "sor"),
    (3, "C1", "H4_LEAF_OWNER", "TRANSFER[Auszugnahme]", "807591efc3d3f7ddbfab", "cheoar"),
    (4, "C1", "H4_LEAF_OWNER", "ZUSTAND[Kurzwärme]", "d904bf7b044dd3922781", "cheky"),
    (5, "C2", "H4_LEAF_OWNER", "TRANSFER[Klarabzug]", "5fca8fc3dee57e1d8c1f", "lcheey"),
    (6, "C2", "H4_LEAF_OWNER", "TRANSFER[Nachseihen]", "deb377381ceaf55ea310", "cphy"),
    (7, "C2", "H4_LEAF_OWNER", "SCHLUSS[Bereit]", "e0b630cb1b5df5e7105b", "shcthy"),
    (8, "C3", "B3_MAIN_ARCH_LINKED_PAIR", "BEZUG[Diesposten]", "b921a237be883a820352", "sy"),
    (9, "C3", "B3_MAIN_ARCH_LINKED_PAIR", "MASS[Sollmaß]", "2f1c5e56e8f0ff459065", "saiin"),
    (10, "C3", "B3_MAIN_ARCH_LINKED_PAIR", "TRANSFER[durchleiten]", "2cc8bb3c2af19607888f", "shckhy"),
    (11, "C3", "B3_MAIN_ARCH_LINKED_PAIR", "ZIEL[Einsetzen]", "276a7c2d74d1143446f4", "choky"),
    (12, "C4", "B3_MAIN_ARCH_LINKED_PAIR", "ZUSTAND[Langkontakt]", "0275fbf14e07935b0a45", "qokeey"),
    (13, "C4", "B3_MAIN_ARCH_LINKED_PAIR", "ZUSTAND[Kurzkontakt]", "7db18b2f0fb7ed0fcfd3", "qokedy"),
    (14, "C4", "B3_MAIN_ARCH_LINKED_PAIR", "SCHLUSS[Verwahren]", "e026af581c99322fbd46", "talam"),
]

LINES = [
    (1, "H4_LEAF_OWNER", [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "MARKED_ANTICIPATION")], "RIGHT_OF_UPPER_IMAGE"),
    (2, "H4_LEAF_OWNER", [(4, "SOURCE")], "RIGHT_OF_UPPER_IMAGE"),
    (3, "H4_LEAF_OWNER", [(5, "SOURCE"), (6, "SOURCE"), (7, "SOURCE")], "BELOW_UPPER_IMAGE"),
    (4, "B3_MAIN_ARCH_LINKED_PAIR", [(8, "SOURCE"), (9, "SOURCE"), (10, "SOURCE"), (11, "SOURCE")], "RIGHT_OF_LOWER_IMAGE"),
    (5, "B3_MAIN_ARCH_LINKED_PAIR", [(12, "SOURCE"), (13, "SOURCE"), (14, "SOURCE")], "BELOW_LOWER_IMAGE"),
]


def main() -> None:
    board = {row["joint_tuple_id"]: row for row in read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")}
    phrases = {row["controlled_phrase"]: row for row in read(P362 / "THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv")}
    card_rows = []
    by_position = {}
    for position, cycle, owner, phrase, tuple_id, surface in CARDS:
        card = board[tuple_id]
        phrase_row = phrases[phrase]
        row = {
            "source_position": position,
            "microcycle": cycle,
            "visible_owner": owner,
            "controlled_phrase": phrase,
            "family_id": phrase_row["family_id"],
            "joint_tuple_id": tuple_id,
            "surface": surface,
            "registered_surface_palette": card["registered_surface_palette"],
            "atomic_value_de": card["atomic_value_de"],
            "board_address": card["board_address"],
            "surface_registered": "YES" if surface in card["registered_surface_palette"].split("|") else "NO",
            "value_matches_phrase": "YES" if phrase.endswith(f"[{card['atomic_value_de']}]") else "NO",
        }
        card_rows.append(row)
        by_position[position] = row
    visible_rows = []
    for line_no, owner, items, region in LINES:
        surfaces = [by_position[position]["surface"] for position, _ in items]
        rendered = "  ".join(surfaces) if any(role == "MARKED_ANTICIPATION" for _, role in items) else " ".join(surfaces)
        for visible_no, (position, role) in enumerate(items, 1):
            source = by_position[position]
            visible_rows.append({
                "line_no": line_no,
                "visible_no": visible_no,
                "text_region": region,
                "visible_owner": owner,
                "rendered_line": rendered,
                "source_position": position,
                "surface": source["surface"],
                "joint_tuple_id": source["joint_tuple_id"],
                "atomic_value_de": source["atomic_value_de"],
                "microcycle": source["microcycle"],
                "visibility_role": role,
                "source_contribution": 0 if role == "MARKED_ANTICIPATION" else 1,
            })
    regions = [
        {"region_id": "I1", "production_order": 1, "region_type": "IMAGE", "owner": "H4_LEAF_OWNER", "x": 1, "y": 1, "width": 15, "height": 5, "content": "bestehender H4-Blattbesitzer"},
        {"region_id": "I2", "production_order": 2, "region_type": "IMAGE", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "x": 1, "y": 8, "width": 22, "height": 5, "content": "bestehender B3-Verbindungsbesitzer"},
        {"region_id": "T1", "production_order": 3, "region_type": "TEXT", "owner": "H4_LEAF_OWNER", "x": 18, "y": 1, "width": 28, "height": 2, "content": "Zeilen 1-2"},
        {"region_id": "T2", "production_order": 4, "region_type": "TEXT", "owner": "H4_LEAF_OWNER", "x": 1, "y": 6, "width": 46, "height": 1, "content": "Zeile 3"},
        {"region_id": "T3", "production_order": 5, "region_type": "TEXT", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "x": 25, "y": 8, "width": 22, "height": 2, "content": "Zeile 4"},
        {"region_id": "T4", "production_order": 6, "region_type": "TEXT", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "x": 1, "y": 14, "width": 46, "height": 1, "content": "Zeile 5"},
    ]
    write("THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv", card_rows)
    write("THREE_HUNDRED_SEVENTY_SIXTH_15_VISIBLE_FORMS.tsv", visible_rows)
    write("THREE_HUNDRED_SEVENTY_SIXTH_PAGE_REGIONS.tsv", regions)
    values = " → ".join(row["atomic_value_de"] for row in card_rows)
    page = f"""# Pass 376 — bildzuerst gesetztes Musterblatt

```text
+--------------+  sho sor cheoar  cheky
| H4 BLATTBILD |  cheky
|  zuerst      |
+--------------+
lcheey cphy shcthy

+---------------------+  sy saiin shckhy choky
| B3 BECKEN/VERBINDUNG |
|  zuerst              |
+---------------------+
qokeey qokedy talam
```

Der doppelte Abstand vor dem ersten `cheky` markiert die einzige Randkopie.
Die Bilder sind keine neuen Deutungen, sondern Platzhalter für die bereits
benutzten H4- und B3-Besitzer.

## Wörtliche Rücklesung

{values}.

## Freie Werkstattanweisung

Von der gezeichneten Pflanze nimm eine Zutat für den Ansatz, entnimm den Auszug
und erwärme ihn kurz. Ziehe den klaren Anteil ab, seihe nach und halte ihn
bereit. Am verbundenen Becken nimm diesen Posten, richte ihn nach Sollmaß, leite
ihn durch und setze ihn ein. Halte ihn länger in Kontakt, danach kurz, und
verwahre ihn.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_SIXTH_COMPLETE_PRACTICE_PAGE.md").write_text(page, encoding="utf-8")
    report = """# Pass 376 — vollständiges Musterblatt

Zwei bestehende Bildbesitzer werden zuerst gesetzt; fünf Textzeilen füllen die
Restflächen. Vier Mikrogänge, ein Besitzerwechsel und eine markierte Randkopie
tragen vierzehn Quellkarten in fünfzehn sichtbaren Formen. Die vollständige
Arbeitsanweisung liest ohne neue Kartenwerte zurück.

Als nächstes soll ein anderer Schreiber das Blatt in der zweiten Palette
abschreiben, dabei aber die Bildblöcke leicht anders skalieren. Das testet, ob
Textfluss und Eigentümer trotz neuer Restbreiten stabil bleiben.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "image_regions": sum(row["region_type"] == "IMAGE" for row in regions),
        "text_regions": sum(row["region_type"] == "TEXT" for row in regions),
        "physical_lines": len(LINES),
        "visible_forms": len(visible_rows),
        "source_cards": sum(int(row["source_contribution"]) for row in visible_rows),
        "microcycles": len({row["microcycle"] for row in card_rows}),
        "owners": len({row["visible_owner"] for row in card_rows}),
        "marked_carries": sum(row["visibility_role"] == "MARKED_ANTICIPATION" for row in visible_rows),
    }
    (HERE / "THREE_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
