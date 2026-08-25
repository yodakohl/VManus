#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASTRO = ROOT / "sidequest_theory_candidates_v75"
WHAT_HOW = ROOT / "sidequest_semantic_what_how_workshop_leaf_eight_hundred_sixty_seventh"
GROUPS = ASTRO / "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
LOCI = ASTRO / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
ENTRIES = WHAT_HOW / "EIGHT_HUNDRED_SIXTY_SEVENTH_6_WHAT_HOW_ENTRIES.tsv"
PREFIX = "EIGHT_HUNDRED_SIXTY_EIGHTH"

NAMESPACE_TO_SHELF = {
    "A1_RIGHT_WHEEL_ONLY": "C1",
    "A1_LEFT_WHEEL_ONLY": "C2",
    "A1_OWNER_UNRESOLVED_NO_JOIN": "Q67",
    "A2_LEFT_PANEL_ONLY": "C3",
    "A2_MIDDLE_PANEL_ONLY": "C3",
    "A2_RIGHT_PANEL_ONLY": "C3",
    "A2_LOCAL_STAR_FIELD_ONLY__PANEL_NOT_INFERRED": "C3",
    "A2_LOCAL_OWNER_UNRESOLVED": "C3",
    "A3_LEFT_WHEEL_ONLY": "C4",
    "A3_MIDDLE_WHEEL_ONLY": "C5",
    "A3_RIGHT_WHEEL_ONLY": "C6",
}

SHELVES = {
    "C1": ("f67r2", "RECHTES_SEKTOR_UND_PHASENRAD", "Kalender-, Sektor- oder Phasenbedingung", "lokalen Sektor oder Phasenplatz aus dem Meisterexemplar wählen"),
    "C2": ("f67r2", "LINKES_STERN_UND_ASPEKTRAD", "Stern-, Strahlen- oder Aspektbedingung", "lokalen Stern-/Aspektplatz im linken Rad wählen"),
    "Q67": ("f67r2", "UNZUGEORDNETE_RADLEGENDE", "unaufgelöste Legende", "nur kopieren; keinem Rad automatisch zuweisen"),
    "C3": ("f68r1", "MEHRPANEEL_STERNATLAS", "Sternort- oder Konstellationsbedingung", "sichtbaren Sternort direkt auswählen; kein Gesamtzentrum annehmen"),
    "C4": ("f69v", "LINKES_28_PLATZ_RAD", "lokale 28er Stations- oder Tagesbedingung", "einen der 28 lokalen Plätze per Exemplar auswählen; nicht umlaufend zählen"),
    "C5": ("f69v", "MITTLERES_WELLEN_UND_WOLKENRAD", "Wetter-, Feuchte- oder Luftbedingung", "nur den eigenen mittleren Ring nachschlagen"),
    "C6": ("f69v", "RECHTES_GESICHT_UND_STRAHLENRAD", "Licht-, Körper- oder Qualitätsbedingung", "nur den eigenen rechten Ring nachschlagen"),
}

PRIMARY_CONDITION = {
    "B1": ("C5", "Bei der gemeinsamen Wasser-/Beckenfolge wäre eine Wetter- oder Feuchtebedingung der anschaulichste Meistereintrag."),
    "B2": ("C4", "Die Folge vieler kurzer Stationsanwendungen passt als Arbeitslesung zu einem lokal gewählten 28er Platz."),
    "B3": ("C2", "Für Gewinnung und Verteilung eines Auszugs wäre ein lokaler Stern-/Aspektvermerk eine plausible Werkstattbedingung."),
    "B4": ("C6", "Wärme und Halten lassen sich am ehesten mit einer Licht-/Körperqualitätsbedingung koppeln."),
    "B5": ("C3", "Der kurze Routennachtrag kann an einen direkt gezeigten Sternort im Mehrpaneelatlas gebunden werden."),
    "B6": ("C1", "Die offene Zieleinstellung kann unter einem lokalen Sektor-/Phasenvermerk stehen."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_groups = read(GROUPS)
    source_loci = read(LOCI)
    entries = read(ENTRIES)

    group_rows = []
    for row in source_groups:
        shelf = NAMESPACE_TO_SHELF[row["local_namespace"]]
        group_rows.append(
            {
                "group_serial": row["group_serial"],
                "page": row["page"],
                "locus": row["locus"],
                "opaque_local_id": row["opaque_local_id"],
                "local_namespace": row["local_namespace"],
                "condition_shelf": shelf,
                "condition_family_de": SHELVES[shelf][2],
                "copied_local_label": row["copied_local_meaning_or_label"],
                "orientation_status": "NONE",
                "crosspage_key": "NONE",
                "word_translation": "NONE__LOCAL_LABEL_ONLY",
            }
        )

    locus_rows = []
    for row in source_loci:
        shelf = NAMESPACE_TO_SHELF[row["local_namespace"]]
        locus_rows.append(
            {
                "page": row["page"],
                "locus": row["locus"],
                "group_count": row["group_count"],
                "local_image_owner": row["local_image_owner"],
                "local_namespace": row["local_namespace"],
                "condition_shelf": shelf,
                "condition_family_de": SHELVES[shelf][2],
                "workshop_lookup_de": SHELVES[shelf][3],
                "authorial_start": "UNKNOWN",
                "authorial_direction": "UNKNOWN",
                "crosspage_key": "NONE",
            }
        )

    group_counts = Counter(row["condition_shelf"] for row in group_rows)
    locus_counts = Counter(row["condition_shelf"] for row in locus_rows)
    shelf_rows = []
    for shelf, (page, instrument, condition, rule) in SHELVES.items():
        shelf_rows.append(
            {
                "condition_shelf": shelf,
                "page": page,
                "instrument": instrument,
                "condition_family_de": condition,
                "lookup_rule_de": rule,
                "loci": locus_counts[shelf],
                "groups": group_counts[shelf],
                "usable_as_condition_menu": "NO" if shelf == "Q67" else "YES_WITH_MASTER",
                "exact_external_value_visible": "NO",
            }
        )

    menu_rows = []
    for entry in entries:
        for shelf in ["C1", "C2", "C3", "C4", "C5", "C6"]:
            primary, reason = PRIMARY_CONDITION[entry["how_record"]]
            menu_rows.append(
                {
                    "entry_id": entry["entry_id"],
                    "what_slot": entry["what_slot"],
                    "how_record": entry["how_record"],
                    "condition_shelf": shelf,
                    "condition_family_de": SHELVES[shelf][2],
                    "working_primary": "YES" if shelf == primary else "NO",
                    "selection_source": "MASTER_EXEMPLAR_ONLY",
                    "automatic_join": "NO",
                    "working_reason_de": reason if shelf == primary else "als alternative Bedingungsfamilie im Meisterexemplar möglich",
                }
            )

    selected_rows = []
    for entry in entries:
        shelf, reason = PRIMARY_CONDITION[entry["how_record"]]
        selected_rows.append(
            {
                "entry_id": entry["entry_id"],
                "what_slot": entry["what_slot"],
                "how_record": entry["how_record"],
                "condition_shelf": shelf,
                "condition_family_de": SHELVES[shelf][2],
                "illustrative_workshop_instruction_de": f"Bereite {entry['what_slot']} vor; führe {entry['how_record']} aus, wenn der Meister den passenden Eintrag aus {shelf} nennt.",
                "reason_de": reason,
                "actual_condition_value": "UNNAMED_MASTER_VALUE",
                "join_status": "ILLUSTRATIVE_NOT_ENCODED",
            }
        )

    manual = [
        {"step": 1, "action_de": "WHAT-Slot P1–P4 und HOW-Record B1–B6 bestimmen", "guard_de": "keinen Produktnamen aus Astro ableiten"},
        {"step": 2, "action_de": "Astro-Seite und sichtbares Teilinstrument wählen", "guard_de": "bei Rad-/Paneelgrenze Schlüssel löschen"},
        {"step": 3, "action_de": "lokalen Locus direkt zeigen", "guard_de": "keinen gemeinsamen Start oder Drehsinn ergänzen"},
        {"step": 4, "action_de": "lokale opake Etikette vollständig kopieren", "guard_de": "keine Prosa-Kartenwerte importieren"},
        {"step": 5, "action_de": "Meisterwert für diesen Locus nennen lassen", "guard_de": "keine Himmelsidentität aus Oberfläche erfinden"},
        {"step": 6, "action_de": "Bedingung als Zusatz zum WHAT→HOW-Auftrag notieren", "guard_de": "keinen direkten Seitenkey behaupten"},
        {"step": 7, "action_de": "bei neuer Station Astro-Schlüssel vollständig zurücksetzen", "guard_de": "f68 und f69 nie per gleicher Nummer verbinden"},
    ]

    write(f"{PREFIX}_395_GROUP_CONDITION_SHELF.tsv", group_rows, ["group_serial", "page", "locus", "opaque_local_id", "local_namespace", "condition_shelf", "condition_family_de", "copied_local_label", "orientation_status", "crosspage_key", "word_translation"])
    write(f"{PREFIX}_142_LOCUS_CONDITION_SHELF.tsv", locus_rows, ["page", "locus", "group_count", "local_image_owner", "local_namespace", "condition_shelf", "condition_family_de", "workshop_lookup_de", "authorial_start", "authorial_direction", "crosspage_key"])
    write(f"{PREFIX}_7_CONDITION_SHELVES.tsv", shelf_rows, ["condition_shelf", "page", "instrument", "condition_family_de", "lookup_rule_de", "loci", "groups", "usable_as_condition_menu", "exact_external_value_visible"])
    write(f"{PREFIX}_36_WHAT_HOW_WHEN_MENU.tsv", menu_rows, ["entry_id", "what_slot", "how_record", "condition_shelf", "condition_family_de", "working_primary", "selection_source", "automatic_join", "working_reason_de"])
    write(f"{PREFIX}_6_ILLUSTRATIVE_WHEN_JOINS.tsv", selected_rows, ["entry_id", "what_slot", "how_record", "condition_shelf", "condition_family_de", "illustrative_workshop_instruction_de", "reason_de", "actual_condition_value", "join_status"])
    write(f"{PREFIX}_7_STEP_WHEN_MANUAL.tsv", manual, ["step", "action_de", "guard_de"])

    lines = ["# WHEN/CONDITION-Regal", ""]
    for row in shelf_rows:
        lines.extend([f"## {row['condition_shelf']} / {row['page']}", "", f"{row['condition_family_de']}: {row['lookup_rule_de']}.", f"{row['loci']} {'Bildort' if int(row['loci']) == 1 else 'Bildorte'}, {row['groups']} opake Gruppen.", ""])
    lines.append("## Sechs illustrative Aufträge")
    lines.append("")
    for row in selected_rows:
        lines.append(f"- {row['illustrative_workshop_instruction_de']}")
    lines.extend([
        "",
        "Diese sechs Verbindungen sind eine lesbare Werkstattprobe, kein sichtbarer Schlüssel.",
        "Jeder reale Bedingungswert bleibt lokales Meisterwissen. Insbesondere gibt es keine",
        "gemeinsame Orientierung, keinen automatischen 28er Umlauf und keinen f68↔f69-Join.",
    ])
    (HERE / f"{PREFIX}_WHEN_CONDITION_WORKSHOP_SHELF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "ASTRO_FUNCTIONS_AS_SEPARATE_MASTER_SELECTED_CONDITION_SHELVES",
        "pages": 3,
        "groups": len(group_rows),
        "loci": len(locus_rows),
        "condition_shelves": 6,
        "quarantine_shelves": 1,
        "what_how_when_menu_rows": len(menu_rows),
        "illustrative_primary_links": len(selected_rows),
        "automatic_crosspage_links": 0,
        "identified_condition_values": 0,
        "new_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 868: WHEN/CONDITION shelf\n\n"
        "The three fixed Astro pages are integrated as six usable local condition shelves\n"
        "plus one unresolved f67 legend. All 142 loci and 395 opaque groups remain attached\n"
        "to their real multi-instrument geometry. A 6x6 menu shows how any WHAT-to-HOW job\n"
        "could receive a master-selected celestial, seasonal or material condition.\n\n"
        "This makes the workshop architecture WHAT -> HOW -> WHEN/CONDITION, but not a\n"
        "decoded cross-page key. No start, direction, common 28-cycle, f68-to-f69 mapping or\n"
        "Astro word meaning is added. The master must still select and name every real value.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
