#!/usr/bin/env python3
"""Turn the twelve exemplar-only cards into a master teaching tablet."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REPAIRS = ROOT / "experiments/yolo/sidequest_semantic_full_correction_index_three_hundred_fiftieth/THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MNEMONICS = {
    "E001": ("Beim Wurzelbild eröffnet dchey den tiefen Pflanzenteil.", "BILDTEIL"),
    "E039": ("tshol eröffnet die Blütenkette vor Auswringen und Seihen.", "BILDTEIL"),
    "E041": ("cfhy drückt zuerst aus; das ähnlich gebaute cphy seiht danach.", "GEORDNETES_PAAR"),
    "E043": ("cphy kommt nach dem Stehen: nicht drücken, sondern nochmals seihen.", "GEORDNETES_PAAR"),
    "E063": ("talam steht am Ende des Blattpostens: zur Ablage verwahren.", "SCHLUSSHANDLUNG"),
    "E086": ("Die lange cheeckhody-Karte beendet den ganzen Pflanzenauftrag.", "SCHLUSSHANDLUNG"),
    "E087": ("Das nackte sh zeigt hier den neuen sichtbaren Pflanzenteil.", "BILDTEIL"),
    "E097": ("sotodan steht am Zielslot: das hergestellte Gut gebrauchen.", "ANWENDUNG"),
    "E159": ("ly sitzt am Beckenende und nennt das Auffanggefäß, nicht den Stoff.", "GEFÄSS"),
    "E216": ("ches zerlegt die laufende Menge; chey verweist nur auf sie.", "MENGENHANDLUNG"),
    "E326": ("qokylddy schließt die Auflage: ansetzen, festhalten, Schluss.", "BEFESTIGUNG"),
    "E374": ("qekey ist der kurze Arbeitsgang; qokey ist der kurze Kontakt.", "DAUERKONTRAST"),
}


def main() -> None:
    all_repairs = read_tsv(REPAIRS)
    targets = [row for row in all_repairs if row["repair_class"] == "MASTER_EXEMPLAR_ONLY"]
    trace = read_tsv(TRACE)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        by_statement[row["statement_id"]].append(row)
    assert len(targets) == 12

    tablet = []
    strips = []
    for number, row in enumerate(targets, start=1):
        mnemonic, family = MNEMONICS[row["event_id"]]
        statement = by_statement[row["statement_id"]]
        surfaces = [item["surface"] for item in statement]
        values = [item["atomic_value_de"] for item in statement]
        target_index = next(i for i, item in enumerate(statement) if item["event_id"] == row["event_id"])
        marked_surface = surfaces.copy()
        marked_surface[target_index] = "[" + marked_surface[target_index] + "]"
        marked_value = values.copy()
        marked_value[target_index] = "[" + marked_value[target_index] + "]"
        tablet.append({
            "tablet_no": f"T{number:02d}",
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "joint_tuple_id": row["source_joint_tuple_id"],
            "whole_card_surface": row["source_surface"],
            "concrete_work_value_de": row["source_value_de"],
            "slot_code": row["source_slot"],
            "picture_or_station_owner": row["owner"],
            "memory_family": family,
            "master_mnemonic_de": mnemonic,
            "nearest_contrast_surface": row["nearest_wrong_surface"],
            "nearest_contrast_value_de": row["nearest_wrong_value_de"],
            "contrast_lesson_de": f"Nicht {row['nearest_wrong_surface']}={row['nearest_wrong_value_de']}; hier {row['source_surface']}={row['source_value_de']}.",
            "must_remain_whole_card": "YES",
        })
        strips.append({
            "tablet_no": f"T{number:02d}",
            "statement_id": row["statement_id"],
            "target_event_id": row["event_id"],
            "surface_strip": " ".join(marked_surface),
            "value_strip_de": " → ".join(marked_value),
            "left_context_value": values[target_index - 1] if target_index else "START",
            "right_context_value": values[target_index + 1] if target_index + 1 < len(values) else "END",
            "owner": row["owner"],
        })

    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_FIRST_TWELVE_CARD_MASTER_TABLET.tsv",
        tablet,
        ["tablet_no", "event_id", "record_unit_id", "page", "joint_tuple_id", "whole_card_surface", "concrete_work_value_de", "slot_code", "picture_or_station_owner", "memory_family", "master_mnemonic_de", "nearest_contrast_surface", "nearest_contrast_value_de", "contrast_lesson_de", "must_remain_whole_card"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_FIRST_TWELVE_CONTEXT_STRIPS.tsv",
        strips,
        ["tablet_no", "statement_id", "target_event_id", "surface_strip", "value_strip_de", "left_context_value", "right_context_value", "owner"],
    )

    lines = [
        "# Die zwölf Karten des Meisters",
        "",
        "Diese Karten werden nicht zerlegt. Der Meister zeigt erst Bild oder Station,",
        "spricht die kurze Handlung und lässt dann die ganze Karte kopieren.",
        "",
    ]
    for row in tablet:
        lines.extend([
            f"## {row['tablet_no']} — `{row['whole_card_surface']}` = {row['concrete_work_value_de']}",
            "",
            f"- **Besitzer:** {row['picture_or_station_owner']}",
            f"- **Merksatz:** {row['master_mnemonic_de']}",
            f"- **Verwechslung:** {row['contrast_lesson_de']}",
            f"- **Kartenstreifen:** `{next(item['surface_strip'] for item in strips if item['tablet_no'] == row['tablet_no'])}`",
            "",
        ])
    (HERE / "THREE_HUNDRED_FIFTY_FIRST_MASTER_TABLET.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    drill = """# Lehrlingsübung in vier Durchgängen

1. **Zeigen:** Meister zeigt Bildbesitzer und ganze Karte; Lehrling spricht den
   kurzen Wert und kopiert die Karte dreimal.
2. **Kontrastieren:** Meister legt die nächstähnliche Karte daneben; Lehrling
   nennt beide verschiedenen Handlungen.
3. **Einsetzen:** Meister zeigt den vollständigen Kartenstreifen mit einer Lücke;
   Lehrling setzt die zwölf Ganzkarten nacheinander ein.
4. **Rücklesen:** Meister zeigt nur die Karte; Lehrling nennt Besitzer, Handlung,
   Slot und rechte Folgehandlung.

Die Paare `cfhy/cphy`, `ches/chey` und `qekey/qokey` werden immer unmittelbar
nebeneinander geübt. Eine falsche Zerlegung zählt als Fehler, selbst wenn der
erratene Satz zufällig flüssig klingt.
"""
    (HERE / "THREE_HUNDRED_FIFTY_FIRST_APPRENTICE_DRILL.md").write_text(drill, encoding="utf-8")

    report = """# Pass 351 — Meistertafel für zwölf Ganzkarten

Der nichtproduktive Rest ist jetzt ein lehrbares Mini-Nomenklatorium statt ein
unbestimmter Ausnahmehaufen. Jede der zwölf einmaligen Karten besitzt genau eine
Bild-/Stationsadresse, einen kurzen konkreten Arbeitswert, einen Merksatz, einen
vollständigen Satzstreifen und die nächstähnliche Kontrastkarte.

Drei besonders gute Lehrpaare entstehen: `cfhy` Auswringen gegen `cphy`
Nachseihen, `ches` Teilen gegen `chey` Diesposten und `qekey` Kurzbearbeitung
gegen `qokey` Kurzkontakt. Diese Gegensätze erklären, warum bloße
Buchstabenzerlegung gefährlich wäre und warum ein kleiner gelernter Ganzwortsatz
neben der produktiven Kartenkomposition sinnvoll ist.

Als Nächstes sollte ein Lehrling alle zwölf Karten in verdeckten Lückensätzen
aus dem Besitzer, linken und rechten Arbeitswert rekonstruieren; falsche
Antworten werden nicht verworfen, sondern als mögliche neue Allographen,
Nachbarkarten oder echte Verwechslungen sortiert.
"""
    (HERE / "THREE_HUNDRED_FIFTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "master_cards": len(tablet),
        "context_strips": len(strips),
        "records": len({row["record_unit_id"] for row in tablet}),
        "pages": len({row["page"] for row in tablet}),
        "memory_families": len({row["memory_family"] for row in tablet}),
        "whole_card_rows": sum(row["must_remain_whole_card"] == "YES" for row in tablet),
    }
    (HERE / "THREE_HUNDRED_FIFTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
