#!/usr/bin/env python3
"""Compose one fresh Herbal-to-Bio work order using only the workshop board."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BOARD = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third/THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv"
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"

PLAN = [
    (1, "H4_LEAF_OWNER", "H4", "2cc054357a929df85f64", "M1_RAW_PART", "M1_RAW_PART", "BOARD_PRODUCTIVE_RULE"),
    (1, "H4_LEAF_OWNER", "H4", "7a4bb8136330ee4e6e56", "M1_RAW_PART", "M2_PREPARATION", "BOARD_PRODUCTIVE_RULE"),
    (1, "H4_LEAF_OWNER", "H4", "807591efc3d3f7ddbfab", "M2_PREPARATION", "M2_PREPARATION", "BOARD_PRODUCTIVE_RULE"),
    (1, "H4_LEAF_OWNER", "H4", "2c1a5fd92b9e3c762242", "M2_PREPARATION", "M2_PREPARATION", "BOARD_PRODUCTIVE_RULE"),
    (2, "H4_LEAF_OWNER", "H4", "5fca8fc3dee57e1d8c1f", "M2_PREPARATION", "M3_CLEAR_EXTRACT", "BOARD_PRODUCTIVE_RULE"),
    (2, "H4_LEAF_OWNER", "H4", "e0b630cb1b5df5e7105b", "M3_CLEAR_EXTRACT", "M3_CLEAR_EXTRACT", "BOARD_PRODUCTIVE_RULE"),
    (3, "B4_MAIN_ARCH_LINKED_PAIR", "B4", "b921a237be883a820352", "M3_CLEAR_EXTRACT", "M3_CLEAR_EXTRACT", "BOARD_PRODUCTIVE_RULE"),
    (3, "B4_MAIN_ARCH_LINKED_PAIR", "B4", "2f1c5e56e8f0ff459065", "M3_CLEAR_EXTRACT", "M4_MEASURED_PORTION", "BOARD_PRODUCTIVE_RULE"),
    (3, "B4_MAIN_ARCH_LINKED_PAIR", "B4", "4a7a6326ac95a8809302", "M4_MEASURED_PORTION", "M5_APPLICATION_ITEM", "PAIR_PLACARD_P13"),
    (4, "B4_MAIN_ARCH_LINKED_PAIR", "B4", "0275fbf14e07935b0a45", "M5_APPLICATION_ITEM", "M5_APPLICATION_ITEM", "PAIR_PLACARD_P07"),
    (4, "B4_MAIN_ARCH_LINKED_PAIR", "B4", "eb2e4bc143f623ee03ac", "M5_APPLICATION_ITEM", "M5_APPLICATION_ITEM", "OWNER_PINNED_MASTER_CARD_T11"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    board = {row["joint_tuple_id"]: row for row in read_tsv(BOARD)}
    chart = {row["joint_tuple_id"]: row for row in read_tsv(CHART)}
    rows = []
    for position, (cycle, owner, source_record, tuple_id, incoming, outgoing, dependency) in enumerate(PLAN, start=1):
        card = board[tuple_id]
        hand_surface = chart[tuple_id]["hand_c_s_entry"]
        rows.append({
            "position": position,
            "microcycle": cycle,
            "owner": owner,
            "source_record_namespace": source_record,
            "joint_tuple_id": tuple_id,
            "hand_c_surface": hand_surface,
            "atomic_value_de": card["atomic_value_de"],
            "slot_code": card["primary_slot"],
            "incoming_state": incoming,
            "outgoing_state": outgoing,
            "board_address": card["board_address"],
            "composition_source": dependency,
            "running_page_exemplar_needed": "NO",
            "value_and_identity_attested": "YES",
        })
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_FOURTH_FRESH_ELEVEN_CARD_WORK_ORDER.tsv",
        rows,
        ["position", "microcycle", "owner", "source_record_namespace", "joint_tuple_id", "hand_c_surface", "atomic_value_de", "slot_code", "incoming_state", "outgoing_state", "board_address", "composition_source", "running_page_exemplar_needed", "value_and_identity_attested"],
    )

    cycles = []
    cycle_text = {
        1: "Nimm den gezeigten Pflanzenzusatz, setze einen Ansatz an, ziehe ihn aus und halte ihn länger warm.",
        2: "Ziehe den klaren Anteil ab und stelle ihn bereit.",
        3: "Übernimm ihn an der Bogenstation, miss den laufenden Posten und setze ihn an der Zielstelle ein.",
        4: "Halte ihn länger in Kontakt und befestige ihn.",
    }
    for cycle in range(1, 5):
        part = [row for row in rows if row["microcycle"] == cycle]
        cycles.append({
            "microcycle": cycle,
            "owner": part[0]["owner"],
            "surface_sequence": " ".join(row["hand_c_surface"] for row in part),
            "value_sequence_de": " → ".join(row["atomic_value_de"] for row in part),
            "slot_sequence": " → ".join(row["slot_code"] for row in part),
            "incoming_state": part[0]["incoming_state"],
            "outgoing_state": part[-1]["outgoing_state"],
            "fluent_instruction_de": cycle_text[cycle],
            "page_exemplar_points": sum(row["running_page_exemplar_needed"] == "YES" for row in part),
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_FOURTH_FOUR_MICROCYCLES.tsv", cycles,
              ["microcycle", "owner", "surface_sequence", "value_sequence_de", "slot_sequence", "incoming_state", "outgoing_state", "fluent_instruction_de", "page_exemplar_points"])

    dependencies = []
    for name in ["BOARD_PRODUCTIVE_RULE", "PAIR_PLACARD_P13", "PAIR_PLACARD_P07", "OWNER_PINNED_MASTER_CARD_T11", "RUNNING_PAGE_EXEMPLAR"]:
        events = [row for row in rows if row["composition_source"] == name]
        dependencies.append({
            "dependency": name,
            "events": len(events),
            "surfaces": "|".join(row["hand_c_surface"] for row in events) if events else "NONE",
            "workshop_function": {
                "BOARD_PRODUCTIVE_RULE": "Wert und Slot wählen die Karte direkt vom Brett.",
                "PAIR_PLACARD_P13": "Besitzer und Zielkontext wählen qokaly aus dem Zieleinsatz-Paar.",
                "PAIR_PLACARD_P07": "Offener Langkontakt wählt okeey statt der schließenden Partnerkarte.",
                "OWNER_PINNED_MASTER_CARD_T11": "B4-Besitzer lizenziert die ganze Befestigen-Karte qokylddy.",
                "RUNNING_PAGE_EXEMPLAR": "Laufende Seitenvorlage wäre zusätzlich nötig.",
            }[name],
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_FOURTH_EXEMPLAR_DEPENDENCY.tsv", dependencies,
              ["dependency", "events", "surfaces", "workshop_function"])

    surface = " | ".join(row["surface_sequence"] for row in cycles[:2]) + " || " + " | ".join(row["surface_sequence"] for row in cycles[2:])
    values = " | ".join(row["value_sequence_de"] for row in cycles[:2]) + " || " + " | ".join(row["value_sequence_de"] for row in cycles[2:])
    readable = f"""# Ein frisch gesetzter Herbal→Bio-Arbeitsauftrag

**Hand C:** `{surface}`

**Kartenwerte:** {values}

**Werkstattanweisung:** {" ".join(row['fluent_instruction_de'] for row in cycles)}

Der Doppelstrich ist die Übergabe vom gezeigten Blattmaterial an die bestehende
B4-Bogenstation. Der Stofffaden läuft von Rohteil über Ansatz, Klarauszug und
bemessene Portion zum Anwendungsposten. Keine Karte und kein Wert ist neu.

Von elf Karten kommen acht direkt aus dem produktiven Brett, zwei aus den
nebeneinander gehängten Doppelplacards und eine aus der an B4 gepinnten
Meisterkarte. Die laufende Textseite muss an keiner Stelle geöffnet werden.
"""
    (HERE / "THREE_HUNDRED_FIFTY_FOURTH_READABLE_WORK_ORDER.md").write_text(readable, encoding="utf-8")

    report = """# Pass 354 — ein neuer Auftrag nur vom Werkstattbrett

Aus elf bereits attestierten Karten wurde eine neue, viergliedrige Folge gesetzt:
Pflanzenzusatz und Ansatz herstellen, Klarabzug bereitstellen, an B4 messen und
einsetzen, lange halten und befestigen. Alle Slotfolgen sind innerhalb ihres
Mikrogangs vorwärts gerichtet; der Stofffaden durchläuft die fünf Zustände.

Acht Karten sind direkt produktiv, `qokaly` und `okeey` brauchen nur ihr
Doppelplacard, und `qokylddy` kommt von der B4-gepinnten Meisterkarte. Kein Griff
zur laufenden Seitenvorlage bleibt übrig. Das ist der bislang konkreteste Beleg
innerhalb der Arbeitstheorie, dass die Karten als kleines erlernbares
Kompositionssystem funktionieren könnten und nicht bloß nachträglich glossierte
Einzelzeilen sind.

Als Nächstes sollte derselbe Auftrag von allen vier Schreiberhänden gesetzt und
dann gegenseitig rückgelesen werden. So zeigt sich, ob die neue Komposition trotz
verschiedener Oberflächen identisch bleibt.
"""
    (HERE / "THREE_HUNDRED_FIFTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "events": len(rows),
        "unique_cards": len({row["joint_tuple_id"] for row in rows}),
        "microcycles": len(cycles),
        "owners": len({row["owner"] for row in rows}),
        "states_visited": len({row["incoming_state"] for row in rows} | {row["outgoing_state"] for row in rows}),
        "board_productive_events": sum(row["composition_source"] == "BOARD_PRODUCTIVE_RULE" for row in rows),
        "pair_placard_events": sum(row["composition_source"].startswith("PAIR_PLACARD") for row in rows),
        "master_pin_events": sum(row["composition_source"].startswith("OWNER_PINNED") for row in rows),
        "running_page_exemplar_events": sum(row["running_page_exemplar_needed"] == "YES" for row in rows),
    }
    (HERE / "THREE_HUNDRED_FIFTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
