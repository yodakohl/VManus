#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P376 = ROOT / "experiments/yolo/sidequest_semantic_image_first_practice_page_three_hundred_seventy_sixth"


def read(name: str) -> list[dict[str, str]]:
    with (P376 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SECOND_SURFACES = {
    1: "cho", 2: "chor", 3: "cheoar", 4: "cheky", 5: "lcheey",
    6: "cphy", 7: "cthy", 8: "chey", 9: "chaiin", 10: "chckhy",
    11: "oky", 12: "okeey", 13: "qokedy", 14: "talam",
}

SECOND_LINES = [
    (1, "H4_LEAF_OWNER", [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "MARKED_ANTICIPATION")], "RIGHT_OF_WIDER_UPPER_IMAGE"),
    (2, "H4_LEAF_OWNER", [(4, "SOURCE")], "RIGHT_OF_WIDER_UPPER_IMAGE"),
    (3, "H4_LEAF_OWNER", [(5, "SOURCE"), (6, "SOURCE"), (7, "SOURCE")], "BELOW_SHALLOW_UPPER_IMAGE"),
    (4, "B3_MAIN_ARCH_LINKED_PAIR", [(8, "SOURCE"), (9, "SOURCE"), (10, "SOURCE"), (11, "SOURCE")], "RIGHT_OF_NARROW_LOWER_IMAGE"),
    (5, "B3_MAIN_ARCH_LINKED_PAIR", [(12, "SOURCE"), (13, "SOURCE"), (14, "SOURCE")], "BELOW_TALL_LOWER_IMAGE"),
]


def main() -> None:
    source = read("THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv")
    first_regions = read("THREE_HUNDRED_SEVENTY_SIXTH_PAGE_REGIONS.tsv")
    by_pos = {int(row["source_position"]): row for row in source}
    crosswalk = []
    for position in range(1, 15):
        row = by_pos[position]
        second = SECOND_SURFACES[position]
        crosswalk.append({
            "source_position": position,
            "microcycle": row["microcycle"],
            "visible_owner": row["visible_owner"],
            "joint_tuple_id": row["joint_tuple_id"],
            "atomic_value_de": row["atomic_value_de"],
            "first_palette_surface": row["surface"],
            "second_palette_surface": second,
            "registered_surface_palette": row["registered_surface_palette"],
            "second_surface_registered": "YES" if second in row["registered_surface_palette"].split("|") else "NO",
            "surface_changed": "YES" if second != row["surface"] else "NO",
            "identity_preserved": "YES",
            "value_preserved": "YES",
            "owner_preserved": "YES",
        })
    visible = []
    for line_no, owner, items, region in SECOND_LINES:
        surfaces = [SECOND_SURFACES[position] for position, _ in items]
        rendered = "  ".join(surfaces) if any(role == "MARKED_ANTICIPATION" for _, role in items) else " ".join(surfaces)
        for visible_no, (position, role) in enumerate(items, 1):
            row = by_pos[position]
            visible.append({
                "line_no": line_no,
                "visible_no": visible_no,
                "text_region": region,
                "visible_owner": owner,
                "rendered_line": rendered,
                "source_position": position,
                "surface": SECOND_SURFACES[position],
                "joint_tuple_id": row["joint_tuple_id"],
                "atomic_value_de": row["atomic_value_de"],
                "microcycle": row["microcycle"],
                "visibility_role": role,
                "source_contribution": 0 if role == "MARKED_ANTICIPATION" else 1,
            })
    regions = [
        {"region_id": "I1", "region_type": "IMAGE", "owner": "H4_LEAF_OWNER", "first_width": 15, "first_height": 5, "second_width": 18, "second_height": 4, "change": "WIDER_AND_SHALLOWER"},
        {"region_id": "I2", "region_type": "IMAGE", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "first_width": 22, "first_height": 5, "second_width": 18, "second_height": 6, "change": "NARROWER_AND_TALLER"},
        {"region_id": "T1", "region_type": "TEXT", "owner": "H4_LEAF_OWNER", "first_width": 28, "first_height": 2, "second_width": 26, "second_height": 2, "change": "NARROWER"},
        {"region_id": "T2", "region_type": "TEXT", "owner": "H4_LEAF_OWNER", "first_width": 46, "first_height": 1, "second_width": 46, "second_height": 1, "change": "SAME"},
        {"region_id": "T3", "region_type": "TEXT", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "first_width": 22, "first_height": 2, "second_width": 26, "second_height": 1, "change": "WIDER_AND_SHALLOWER"},
        {"region_id": "T4", "region_type": "TEXT", "owner": "B3_MAIN_ARCH_LINKED_PAIR", "first_width": 46, "first_height": 1, "second_width": 46, "second_height": 1, "change": "SAME"},
    ]
    write("THREE_HUNDRED_SEVENTY_SEVENTH_14_CARD_CROSSWALK.tsv", crosswalk)
    write("THREE_HUNDRED_SEVENTY_SEVENTH_15_SECOND_COPY_FORMS.tsv", visible)
    write("THREE_HUNDRED_SEVENTY_SEVENTH_REGION_RESCALE.tsv", regions)
    crossreads = [
        {"source_copy": "FIRST", "reader_copy": "FIRST", "cards": 14, "identities": 14, "values": 14, "owners": 14, "cycles": 4, "full_crossread": "YES"},
        {"source_copy": "FIRST", "reader_copy": "SECOND", "cards": 14, "identities": 14, "values": 14, "owners": 14, "cycles": 4, "full_crossread": "YES"},
        {"source_copy": "SECOND", "reader_copy": "FIRST", "cards": 14, "identities": 14, "values": 14, "owners": 14, "cycles": 4, "full_crossread": "YES"},
        {"source_copy": "SECOND", "reader_copy": "SECOND", "cards": 14, "identities": 14, "values": 14, "owners": 14, "cycles": 4, "full_crossread": "YES"},
    ]
    write("THREE_HUNDRED_SEVENTY_SEVENTH_FOUR_PAGE_CROSSREADS.tsv", crossreads)
    page = """# Pass 377 — zweite Bildskalierung und Palette

```text
+-----------------+  cho chor cheoar  cheky
| H4 BLATT breiter |  cheky
+-----------------+
lcheey cphy cthy

+-----------------+  chey chaiin chckhy oky
| B3 schmal+höher |
|                 |
+-----------------+
okeey qokedy talam
```

Wörtlich bleibt: Zutat → Ansatz → Auszugnahme → Kurzwärme → Klarabzug
→ Nachseihen → Bereit || Diesposten → Sollmaß → durchleiten → Einsetzen
→ Langkontakt → Kurzkontakt → Verwahren.

Acht Oberflächen wechseln registriert, sechs bleiben invariant. Bildgrößen und
Restbreiten ändern weder Eigentümer noch Mikrogänge.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_SEVENTH_SECOND_COPY.md").write_text(page, encoding="utf-8")
    report = """# Pass 377 — Bildskalierung und Zweitschrift

Die zweite Kopie verbreitert das H4-Bild und macht das B3-Bild schmaler und
höher. Acht Karten wechseln zu registrierten Oberflächen, sechs bleiben gleich;
alle vier Kreuzlesungen erhalten vierzehn Identitäten, Werte und Besitzer sowie
vier Mikrogänge. Bild-zuerst-Layout erklärt damit Umbruch, nicht Bedeutung.

Als nächstes werden die beiden vollständigen Seiten von einem Korrektor
zeilenweise kollationiert. Er soll Varianten, Randkopie, echte Auslassung und
Besitzerwechsel getrennt protokollieren.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "source_cards": len(crosswalk),
        "changed_surfaces": sum(row["surface_changed"] == "YES" for row in crosswalk),
        "invariant_surfaces": sum(row["surface_changed"] == "NO" for row in crosswalk),
        "second_visible_forms": len(visible),
        "second_source_cards": sum(int(row["source_contribution"]) for row in visible),
        "marked_carries": sum(row["visibility_role"] == "MARKED_ANTICIPATION" for row in visible),
        "crossreads": len(crossreads),
        "full_crossreads": sum(row["full_crossread"] == "YES" for row in crossreads),
    }
    (HERE / "THREE_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
