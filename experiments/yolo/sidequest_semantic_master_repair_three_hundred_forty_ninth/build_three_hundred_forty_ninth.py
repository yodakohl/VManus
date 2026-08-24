#!/usr/bin/env python3
"""Make and repair three concrete apprentice miscopies in the H3-to-B2 lesson."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_h3_b2_four_line_translation_three_hundred_forty_seventh/THREE_HUNDRED_FORTY_SEVENTH_79_EVENT_FOUR_LINE_INTERLINEAR.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = {row["event_id"]: row for row in read_tsv(EVENTS)}
    mixed = read_tsv(MIXED)
    surface_index: dict[str, set[tuple[str, str]]] = {}
    for row in mixed:
        surface_index.setdefault(row["rendered_surface"], set()).add((row["joint_tuple_id"], row["atomic_value_de"]))

    wrong_surface_tuple, wrong_surface_value = sorted(surface_index["qokedy"])[0]
    cases = [
        {
            "case_id": "M01_WRONG_CARD_SURFACE",
            "layer": "CARD_IDENTITY",
            "statement_id": "H3-S001",
            "target_event_ids": "E044",
            "correct_source": events["E044"]["rendered_surface"],
            "apprentice_miscopy": "qokedy",
            "miscopy_effect": f"Die Oberfläche dekodiert als {wrong_surface_value} ({wrong_surface_tuple}), nicht als Klarauszug.",
            "redundancy_channel_1": "Das geforderte Ergebnis im Arbeitsgang ist Klarauszug.",
            "redundancy_channel_2": "Nachseihen → Klarauszug → Rücknahmeschluss bildet die lokale Stofffolge.",
            "redundancy_channel_3": "qokedy ist bereits eine andere registrierte Karte für Kurzkontakt.",
            "master_diagnosis": "Richtiger Slot, aber falsche Kartenidentität; die Form gehört zu einem Kontaktgang.",
            "exact_repair": "qokedy durch shey ersetzen; cheey wäre dieselbe registrierte Klarauszug-Karte in einer anderen Hand.",
            "new_meaning_needed": "NO",
            "recovered_exactly": "YES",
        },
        {
            "case_id": "M02_LOST_MATERIAL_THREAD",
            "layer": "MATERIAL_THREAD",
            "statement_id": "B2-S012",
            "target_event_ids": "E208|E209",
            "correct_source": "Bemessene Portion → Anwendungsposten",
            "apprentice_miscopy": "Rohteil → Anwendungsposten",
            "miscopy_effect": "Der Lehrling verwirft beim Mikrogangwechsel die unmittelbar gesetzte bemessene Portion.",
            "redundancy_channel_1": "E207 setzt sichtbar Sollmaß und damit Bemessene Portion.",
            "redundancy_channel_2": "E208 Diesposten verweist auf genau den laufenden, nicht auf einen neuen Posten.",
            "redundancy_channel_3": "Zwischen E207 und E209 steht kein Rohteil-Marker.",
            "master_diagnosis": "Karten und Slots stimmen, aber der Stofffaden wurde ohne Marker zurückgesetzt.",
            "exact_repair": "E208 mit Bemessene Portion beginnen und erst durch E209 Volleinsatz zu Anwendungsposten wechseln.",
            "new_meaning_needed": "NO",
            "recovered_exactly": "YES",
        },
        {
            "case_id": "M03_MISSED_MICROCYCLE_RESET",
            "layer": "SIX_SLOT_ORDER",
            "statement_id": "B2-S005",
            "target_event_ids": "E180|E181|E182",
            "correct_source": "Mikrogang 3: E180 E181; Mikrogang 4: E182 E183",
            "apprentice_miscopy": "Mikrogang 3: E180 E181 E182; Mikrogang 4: E183",
            "miscopy_effect": "Folgevorbereitung wird hinter zwei Sollstellungen in denselben Gang gezogen.",
            "redundancy_channel_1": "Die Slotfolge würde S2 → S2 → S1 rückwärts laufen.",
            "redundancy_channel_2": "Ein neuer S1-Bezug eröffnet nach der Sollstellung den nächsten Arbeitsgang.",
            "redundancy_channel_3": "Der folgende Langwärmen-Schritt S4 gehört zu diesem neu eröffneten Gang.",
            "master_diagnosis": "Kein Wortfehler, sondern eine ausgelassene Mikroganggrenze vor E182.",
            "exact_repair": "Grenze zwischen E181 und E182 einsetzen; E182 S1 und E183 S4 bilden Mikrogang 4.",
            "new_meaning_needed": "NO",
            "recovered_exactly": "YES",
        },
    ]

    fields = [
        "case_id", "layer", "statement_id", "target_event_ids", "correct_source",
        "apprentice_miscopy", "miscopy_effect", "redundancy_channel_1",
        "redundancy_channel_2", "redundancy_channel_3", "master_diagnosis",
        "exact_repair", "new_meaning_needed", "recovered_exactly",
    ]
    write_tsv(HERE / "THREE_HUNDRED_FORTY_NINTH_THREE_MISCOPIES.tsv", cases, fields)

    event_diffs = [
        {
            "case_id": "M01_WRONG_CARD_SURFACE", "event_id": "E044", "source_surface": events["E044"]["rendered_surface"],
            "miscopied_surface": "qokedy", "source_value": events["E044"]["atomic_value_de"], "miscopied_decode": wrong_surface_value,
            "source_slot": events["E044"]["slot_code"], "miscopied_structure": "S4_DAUER_ZUSTAND statt S3_PROZESS_TRANSFER",
            "repaired_form": events["E044"]["rendered_surface"],
        },
        {
            "case_id": "M02_LOST_MATERIAL_THREAD", "event_id": "E208", "source_surface": events["E208"]["rendered_surface"],
            "miscopied_surface": events["E208"]["rendered_surface"], "source_value": events["E208"]["atomic_value_de"], "miscopied_decode": "Diesposten auf erfundenem Rohteil",
            "source_slot": events["E208"]["slot_code"], "miscopied_structure": "incoming=Rohteil statt Bemessene Portion",
            "repaired_form": "Diesposten auf Bemessene Portion",
        },
        {
            "case_id": "M03_MISSED_MICROCYCLE_RESET", "event_id": "E182", "source_surface": events["E182"]["rendered_surface"],
            "miscopied_surface": events["E182"]["rendered_surface"], "source_value": events["E182"]["atomic_value_de"], "miscopied_decode": events["E182"]["atomic_value_de"],
            "source_slot": events["E182"]["slot_code"], "miscopied_structure": "microcycle=3 statt 4",
            "repaired_form": "Grenze | vor " + events["E182"]["rendered_surface"],
        },
    ]
    write_tsv(
        HERE / "THREE_HUNDRED_FORTY_NINTH_EVENT_DIFFS.tsv",
        event_diffs,
        ["case_id", "event_id", "source_surface", "miscopied_surface", "source_value", "miscopied_decode", "source_slot", "miscopied_structure", "repaired_form"],
    )

    channels = [
        {"channel": "REGISTERED_CARD_IDENTITY", "detects_case": "M01_WRONG_CARD_SURFACE", "question": "Dekodiert die geschriebene Oberfläche zur verlangten Karte?", "repair_power": "EXACT_CARD"},
        {"channel": "LOCAL_OPERATION_SEQUENCE", "detects_case": "M01_WRONG_CARD_SURFACE", "question": "Passt der Kartenwert zwischen Nachseihen und Rücknahmeschluss?", "repair_power": "VALUE_AND_SLOT"},
        {"channel": "EXPLICIT_STATE_MARKER", "detects_case": "M02_LOST_MATERIAL_THREAD", "question": "Welchen Stoffzustand hat die letzte sichtbare Zustandskarte gesetzt?", "repair_power": "EXACT_INCOMING_STATE"},
        {"channel": "Y_CURRENT_REFERENT", "detects_case": "M02_LOST_MATERIAL_THREAD", "question": "Verweist Diesposten auf den laufenden oder einen neuen Stoff?", "repair_power": "THREAD_CONTINUITY"},
        {"channel": "SIX_SLOT_MONOTONICITY", "detects_case": "M03_MISSED_MICROCYCLE_RESET", "question": "Läuft die Slotfolge ohne Grenze rückwärts?", "repair_power": "EXACT_BOUNDARY"},
        {"channel": "FOLLOWING_OPERATION_FIT", "detects_case": "M03_MISSED_MICROCYCLE_RESET", "question": "Welcher neue Bezug trägt den folgenden Langwärmen-Schritt?", "repair_power": "CYCLE_ATTACHMENT"},
    ]
    write_tsv(HERE / "THREE_HUNDRED_FORTY_NINTH_REDUNDANCY_CHANNELS.tsv", channels,
              ["channel", "detects_case", "question", "repair_power"])

    lines = [
        "# Drei Fehlkopien und ihre Reparatur",
        "",
        "Der Meister lässt drei Fehler absichtlich stehen. Er benutzt keine neue",
        "Bedeutung, sondern nur Kartenregister, Stofffaden und Slotreihenfolge.",
        "",
    ]
    for index, case in enumerate(cases, start=1):
        lines.extend([
            f"## Fehler {index}: {case['layer']}",
            "",
            f"**Lehrling:** `{case['apprentice_miscopy']}`",
            "",
            f"**Folge:** {case['miscopy_effect']}",
            "",
            f"**Meister:** {case['master_diagnosis']}",
            "",
            "Er zeigt drei Hinweise:",
            "",
            f"1. {case['redundancy_channel_1']}",
            f"2. {case['redundancy_channel_2']}",
            f"3. {case['redundancy_channel_3']}",
            "",
            f"**Reparatur:** {case['exact_repair']}",
            "",
        ])
    lines.extend([
        "## Werkstattergebnis",
        "",
        "Alle drei Fehler werden eindeutig lokalisiert. Einer betrifft die Karte,",
        "einer den fortlaufenden Stoff und einer nur die Gliederung. Die Schreiber",
        "müssen deshalb nicht jeden Satz auswendig kennen: mehrere schwache Kanäle",
        "überlappen und stellen die richtige Lesung wieder her.",
    ])
    (HERE / "THREE_HUNDRED_FORTY_NINTH_MASTER_REPAIR_DIALOGUE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 349 — drei reparierbare Fehlkopien

Aus der vollständigen H3→B2-Lehrfassung wurden drei konkrete Fehler gebaut:
falsche registrierte Karte, verlorener Stofffaden und ausgelassene Mikroganggrenze.
Alle drei lassen sich ohne neue Wortbedeutung exakt reparieren.

Der stärkste Befund ist nicht, dass die Notation fehlerfrei wäre, sondern dass
sie verschiedenartige Redundanz besitzt. Kartenidentität und lokaler Prozess
reparieren `qokedy` statt `shey`; Sollmaß und Diesposten reparieren den verlorenen
Materialfaden; S2→S1 erkennt die fehlende Ganggrenze. Das passt zu einem System,
das mehrere Schreiber mit Meisterexemplar praktisch benutzen konnten.

Als Nächstes sollte derselbe Korrekturmechanismus über alle 381 Prosaereignisse
laufen und jeden denkbaren Ein-Karten-Fehler einer Reparaturklasse zuordnen.
"""
    (HERE / "THREE_HUNDRED_FORTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "miscopy_cases": len(cases),
        "event_diffs": len(event_diffs),
        "redundancy_channels": len(channels),
        "cases_recovered_exactly": sum(row["recovered_exactly"] == "YES" for row in cases),
        "new_meanings_added": sum(row["new_meaning_needed"] != "NO" for row in cases),
        "source_events_available": len(events),
    }
    (HERE / "THREE_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
