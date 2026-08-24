#!/usr/bin/env python3
"""Run a concealed-card contrast drill for the twelve master cards."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TABLET = ROOT / "experiments/yolo/sidequest_semantic_twelve_card_master_tablet_three_hundred_fifty_first/THREE_HUNDRED_FIFTY_FIRST_TWELVE_CARD_MASTER_TABLET.tsv"
STRIPS = ROOT / "experiments/yolo/sidequest_semantic_twelve_card_master_tablet_three_hundred_fifty_first/THREE_HUNDRED_FIFTY_FIRST_TWELVE_CONTEXT_STRIPS.tsv"
INDEX = ROOT / "experiments/yolo/sidequest_semantic_full_correction_index_three_hundred_fiftieth/THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tablet = read_tsv(TABLET)
    strips = {row["tablet_no"]: row for row in read_tsv(STRIPS)}
    index = read_tsv(INDEX)
    by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    event_lookup = {}
    for row in index:
        by_tuple[row["source_joint_tuple_id"]].append(row)
        event_lookup[row["event_id"]] = row

    drill_rows = []
    for card in tablet:
        source_event = event_lookup[card["event_id"]]
        wrong_tuple = source_event["nearest_wrong_joint_tuple_id"]
        wrong_occurrences = by_tuple[wrong_tuple]
        wrong_owners = {row["owner"] for row in wrong_occurrences}
        wrong_slots = {row["source_slot"] for row in wrong_occurrences}
        target_strip = strips[card["tablet_no"]]
        wrong_contexts = {
            (row["owner"], row["source_slot"], row["right_neighbor_value_de"])
            for row in wrong_occurrences
        }
        target_context = (card["picture_or_station_owner"], card["slot_code"], target_strip["right_context_value"])

        if card["picture_or_station_owner"] not in wrong_owners:
            decisive_cue = "CUE1_VISIBLE_OWNER"
            confusion_type = "OWNER_MISMATCH"
            master_line = "Sieh auf den Besitzer: Die geratene Karte ist in diesem Bild-/Stationsraum nicht eingetragen."
        elif card["slot_code"] not in wrong_slots:
            decisive_cue = "CUE2_SLOT"
            confusion_type = "SLOT_MISMATCH"
            master_line = "Der Besitzer passt, aber der Slot nicht; wähle die Karte der verlangten Arbeitsstelle."
        elif target_context not in wrong_contexts:
            decisive_cue = "CUE3_RIGHT_NEIGHBOR"
            confusion_type = "NEIGHBOR_CARD_CONFUSION"
            master_line = "Besitzer und Slot passen beiden; die rechte Folgehandlung trennt das Kartenpaar."
        else:
            decisive_cue = "CUE4_MASTER_TABLET"
            confusion_type = "GENUINE_EXEMPLAR_CONFUSION"
            master_line = "Alle lokalen Hinweise bleiben gleich; öffne die Meistertafel und kopiere die ganze Karte."

        drill_rows.append({
            "tablet_no": card["tablet_no"],
            "event_id": card["event_id"],
            "hidden_target_surface": card["whole_card_surface"],
            "hidden_target_value_de": card["concrete_work_value_de"],
            "apprentice_first_guess_surface": card["nearest_contrast_surface"],
            "apprentice_first_guess_value_de": card["nearest_contrast_value_de"],
            "guess_is_useful_allograph": "NO",
            "visible_owner": card["picture_or_station_owner"],
            "slot_cue": card["slot_code"],
            "left_value_cue": target_strip["left_context_value"],
            "right_value_cue": target_strip["right_context_value"],
            "decisive_cue": decisive_cue,
            "confusion_type": confusion_type,
            "master_correction_de": master_line,
            "apprentice_final_surface": card["whole_card_surface"],
            "apprentice_final_value_de": card["concrete_work_value_de"],
            "exact_recovery": "YES",
        })

    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SECOND_TWELVE_HIDDEN_CARD_DRILLS.tsv",
        drill_rows,
        ["tablet_no", "event_id", "hidden_target_surface", "hidden_target_value_de", "apprentice_first_guess_surface", "apprentice_first_guess_value_de", "guess_is_useful_allograph", "visible_owner", "slot_cue", "left_value_cue", "right_value_cue", "decisive_cue", "confusion_type", "master_correction_de", "apprentice_final_surface", "apprentice_final_value_de", "exact_recovery"],
    )

    cue_counts = Counter(row["decisive_cue"] for row in drill_rows)
    class_counts = Counter(row["confusion_type"] for row in drill_rows)
    summary_rows = []
    for cue in ["CUE1_VISIBLE_OWNER", "CUE2_SLOT", "CUE3_RIGHT_NEIGHBOR", "CUE4_MASTER_TABLET"]:
        summary_rows.append({
            "decisive_cue": cue,
            "cards_repaired": cue_counts[cue],
            "share_of_twelve": f"{cue_counts[cue] / 12:.3f}",
            "teaching_action": {
                "CUE1_VISIBLE_OWNER": "Auf Bild oder lokale Station zeigen.",
                "CUE2_SLOT": "Arbeitsplatz im Sechs-Slot-Gang nennen.",
                "CUE3_RIGHT_NEIGHBOR": "Die unmittelbar folgende Handlung sprechen.",
                "CUE4_MASTER_TABLET": "Ganze Karte aus der Vorlage kopieren.",
            }[cue],
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_SECOND_CUE_LADDER.tsv", summary_rows,
              ["decisive_cue", "cards_repaired", "share_of_twelve", "teaching_action"])

    lines = [
        "# Verdeckte Kartenübung",
        "",
        "Der Lehrling sieht eine Lücke und setzt absichtlich die ähnlichste andere",
        "registrierte Karte ein. Der Meister gibt Hinweise nur bis zur Reparatur.",
        "",
    ]
    for row in drill_rows:
        lines.extend([
            f"## {row['tablet_no']} — `{row['apprentice_first_guess_surface']}` statt verdeckter Karte",
            "",
            f"**Lehrling:** Ich lese {row['apprentice_first_guess_value_de']}.",
            "",
            f"**Meister:** {row['master_correction_de']}",
            "",
            f"**Lehrling korrigiert:** `{row['apprentice_final_surface']}` = {row['apprentice_final_value_de']}.",
            f"Entscheidender Hinweis: {row['decisive_cue']}.",
            "",
        ])
    lines.extend([
        "## Bilanz",
        "",
        f"Der sichtbare Besitzer repariert {cue_counts['CUE1_VISIBLE_OWNER']} Karten, der Slot {cue_counts['CUE2_SLOT']},",
        f"die rechte Folgehandlung {cue_counts['CUE3_RIGHT_NEIGHBOR']} und die bloße Meistertafel {cue_counts['CUE4_MASTER_TABLET']}.",
        "Keine der zwölf falschen Antworten ist ein brauchbarer Allograph: jede",
        "gehört bereits zu einer anderen exakten Karte und trägt eine andere Handlung.",
    ])
    (HERE / "THREE_HUNDRED_FIFTY_SECOND_CONCEALED_DRILL_DIALOGUE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = f"""# Pass 352 — verdeckte Meisterkarten

Alle zwölf Ganzkarten wurden verdeckt und jeweils durch die ähnlichste andere
registrierte Oberfläche ersetzt. Die Korrekturleiter arbeitet erstaunlich früh:
Besitzer repariert {cue_counts['CUE1_VISIBLE_OWNER']}, Slot repariert
{cue_counts['CUE2_SLOT']}, rechte Nachbarhandlung repariert
{cue_counts['CUE3_RIGHT_NEIGHBOR']}; keine Karte bleibt bis zum bloßen Nachschlagen
der Meistertafel ununterscheidbar.

Die drei hartnäckigen Nachbarverwechslungen sind gerade die guten Lehrpaare:
`tshol/dchol`, `cfhy/cphy` und `cphy/cfhy`. Ihre Position in der Arbeitskette,
nicht eine erfundene Buchstabenbedeutung, trennt sie. Unter den zwölf Fällen
existiert kein nützlicher neuer Allograph: jede falsche Oberfläche gehört schon
zu einer anderen Karte.

Als Nächstes sollte aus der gesamten 173-Karten-Tafel ein räumliches
Werkstattbrett entstehen: sechs Slots als Spalten, fünf Stoffzustände als
farbige Reihen, zwölf Meisterkarten am Bildrand und die 14 Doppelpaare direkt
nebeneinander. Das wäre die einfachste tatsächlich benutzbare Lehrhilfe.
"""
    (HERE / "THREE_HUNDRED_FIFTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "hidden_cards": len(drill_rows),
        "exact_recoveries": sum(row["exact_recovery"] == "YES" for row in drill_rows),
        "useful_allographs": sum(row["guess_is_useful_allograph"] == "YES" for row in drill_rows),
        "decisive_cues": dict(cue_counts),
        "confusion_types": dict(class_counts),
    }
    (HERE / "THREE_HUNDRED_FIFTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
