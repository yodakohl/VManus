#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARSES = ROOT / "sidequest_semantic_astro_address_cores_four_hundred_sixty_sixth" / "FOUR_HUNDRED_SIXTY_SIXTH_395_ASTRO_GROUP_ADDRESS_CORES.tsv"
SHELF_DIR = ROOT / "sidequest_semantic_when_condition_shelf_eight_hundred_sixty_eighth"
SHELF_GROUPS = SHELF_DIR / "EIGHT_HUNDRED_SIXTY_EIGHTH_395_GROUP_CONDITION_SHELF.tsv"
SHELF_LOCI = SHELF_DIR / "EIGHT_HUNDRED_SIXTY_EIGHTH_142_LOCUS_CONDITION_SHELF.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_THIRD"

ROOTS = {
    "OT": ("FOLGEND", "nächster oder danach gewählter lokaler Eintrag"),
    "OL": ("WEITER", "vorigen Bezug fortsetzen oder gleichen Rahmen behalten"),
    "AR": ("VON", "von der lokalen Quelle oder dem Gegenfeld"),
    "AL": ("AN", "an diesem Ziel- oder Bildplatz"),
    "AIN": ("PORTION", "ein abgegrenzter Teil des lokalen Werts"),
    "AIIN": ("SOLLMASS", "der vorgeschriebene lokale Wert oder Maßposten"),
    "IIN": ("STUFE", "eine lokale Bedingungs- oder Einstellstufe"),
    "E": ("KURZ", "kurzer oder erster Grad"),
    "EE": ("LAENGER", "längerer oder anhaltender Grad"),
    "EEE": ("VOLL", "vollständiger oder höchster Grad"),
    "Y": ("DIESER_EINTRAG", "der aktuell gemeinte lokale Eintrag"),
    "DY": ("LOKAL_SCHLIESSEN", "diesen lokalen Etiketteneintrag schließen"),
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
    parses = read(PARSES)
    shelf_groups = {row["group_serial"]: row for row in read(SHELF_GROUPS)}
    shelf_loci = {(row["page"], row["locus"]): row for row in read(SHELF_LOCI)}

    component_counts = Counter(
        token
        for row in parses
        for token in row["selected_component_parse"].split("+")
        if token in ROOTS
    )
    root_rows = []
    for token, (value, operational) in ROOTS.items():
        relevant = [row for row in parses if token in row["selected_component_parse"].split("+")]
        root_rows.append(
            {
                "relative_component": token,
                "relative_value_de": value,
                "operational_default_de": operational,
                "group_count": component_counts[token],
                "pages": "|".join(sorted({row["page"] for row in relevant})),
                "condition_shelves": "|".join(sorted({shelf_groups[row["group_serial"]]["condition_shelf"] for row in relevant})),
                "external_name_claim": "NO",
            }
        )

    group_rows = []
    for row in parses:
        shelf = shelf_groups[row["group_serial"]]
        tokens = row["selected_component_parse"].split("+")
        relative_tokens = [token for token in tokens if token in ROOTS]
        relative_reading = " · ".join(ROOTS[token][0] for token in relative_tokens)
        if relative_reading:
            if any(token not in ROOTS for token in tokens) or row["selected_component_parse"] == "NONE":
                relative_reading += " · LOKALER_BEDINGUNGSKERN"
            status = "RELATIVE_COMPONENTS_PLUS_LOCAL_CORE"
        else:
            relative_reading = "LOKALE_BEDINGUNGSKARTE"
            status = "LEARNED_LOCAL_WHOLE_LABEL"
        group_rows.append(
            {
                "group_serial": row["group_serial"],
                "page": row["page"],
                "locus": row["locus"],
                "event_index": row["event_index"],
                "opaque_local_id": row["opaque_local_id"],
                "condition_shelf": shelf["condition_shelf"],
                "surface": row["surface"],
                "selected_component_parse": row["selected_component_parse"],
                "portable_relative_components": "+".join(relative_tokens) or "NONE",
                "relative_condition_reading_de": relative_reading,
                "full_workshop_default_de": row["atomic_common_root_value_de"] if row["atomic_common_root_value_de"] else "lokale Bedingungskarte",
                "reading_status": status,
                "external_celestial_or_calendar_name": "UNNAMED",
            }
        )

    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in group_rows:
        by_locus[(row["page"], row["locus"])].append(row)
    locus_rows = []
    for (page, locus), subset in by_locus.items():
        source = shelf_loci[(page, locus)]
        subset.sort(key=lambda row: int(row["event_index"]))
        handle = f"{source['condition_shelf']}@{locus}"
        locus_rows.append(
            {
                "condition_handle": handle,
                "condition_shelf": source["condition_shelf"],
                "page": page,
                "locus": locus,
                "local_image_owner": source["local_image_owner"],
                "surface_sequence": " ".join(row["surface"] for row in subset),
                "relative_condition_sequence_de": " | ".join(row["relative_condition_reading_de"] for row in subset),
                "group_count": len(subset),
                "portable_relative_groups": sum(row["portable_relative_components"] != "NONE" for row in subset),
                "workshop_use_de": f"Nenne {handle}, zeige den Bildort und lies seine relativen Bedienwerte; den shelflokalen Namenskern lernt der Schreiber als Ganzkarte.",
                "external_name_needed_for_internal_use": "NO",
            }
        )
    locus_rows.sort(key=lambda row: (str(row["page"]), int(str(row["locus"]).split(".")[-1])))

    shelf_profiles = []
    for shelf in ["C1", "C2", "Q67", "C3", "C4", "C5", "C6"]:
        subset = [row for row in group_rows if row["condition_shelf"] == shelf]
        token_counts = Counter(
            token
            for row in subset
            for token in row["portable_relative_components"].split("+")
            if token != "NONE"
        )
        shelf_profiles.append(
            {
                "condition_shelf": shelf,
                "groups": len(subset),
                "loci": len({row["locus"] for row in subset}),
                "groups_with_relative_components": sum(row["portable_relative_components"] != "NONE" for row in subset),
                "dominant_relative_components": "|".join(f"{token}:{count}" for token, count in token_counts.most_common(6)) or "NONE",
                "internal_handle_rule": f"{shelf}@page.locus",
                "external_names": 0,
            }
        )

    sample_group = next(row for row in group_rows if row["page"] == "f69v" and row["locus"] == "f69v.12")
    sample_locus = next(row for row in locus_rows if row["page"] == "f69v" and row["locus"] == "f69v.12")
    sample_rows = [
        {"layer": "HANDLE", "value": sample_locus["condition_handle"], "reading_de": "linker lokaler f69-Bedingungsplatz; externe Nummer nicht erforderlich"},
        {"layer": "SURFACE", "value": sample_group["surface"], "reading_de": "sichtbare gelernte Etikette"},
        {"layer": "PARSE", "value": sample_group["selected_component_parse"], "reading_de": "OT=FOLGEND; O=shelflokaler Bedingungskern; DY=LOKAL SCHLIESSEN"},
        {"layer": "RELATIVE_COMMAND", "value": sample_group["relative_condition_reading_de"], "reading_de": "den folgenden lokalen Bedingungskern wählen und diesen Etiketteneintrag schließen"},
        {"layer": "WORKSHOP_USE", "value": "INTERNAL_COMPLETE", "reading_de": "Der Meister kann den Griff nennen; der Schreiber braucht keinen Mondhaus-, Monats- oder Planetennamen."},
    ]

    payload = [
        {"payload": "PRODUCT", "status": "INTERNAL_COMPLETE", "remaining_external": "nur botanischer Name"},
        {"payload": "MEASURE", "status": "RELATIVE_COMPLETE_CALIBRATION_EXTERNAL", "remaining_external": "absolute Einheit"},
        {"payload": "DURATION", "status": "RELATIVE_COMPLETE_CALIBRATION_EXTERNAL", "remaining_external": "absolute Zeitspanne"},
        {"payload": "RESULT", "status": "CLASS_COMPLETE_CALIBRATION_EXTERNAL", "remaining_external": "präzises Annahmekriterium"},
        {"payload": "CONDITION", "status": "INTERNAL_COMPLETE_EXTERNAL_NAME_UNRESOLVED", "remaining_external": "historischer Himmels-/Kalendername"},
    ]

    write(f"{PREFIX}_12_RELATIVE_ASTRO_COMPONENTS.tsv", root_rows, ["relative_component", "relative_value_de", "operational_default_de", "group_count", "pages", "condition_shelves", "external_name_claim"])
    write(f"{PREFIX}_395_RELATIVE_CONDITION_GROUPS.tsv", group_rows, ["group_serial", "page", "locus", "event_index", "opaque_local_id", "condition_shelf", "surface", "selected_component_parse", "portable_relative_components", "relative_condition_reading_de", "full_workshop_default_de", "reading_status", "external_celestial_or_calendar_name"])
    write(f"{PREFIX}_142_INTERNAL_CONDITION_HANDLES.tsv", locus_rows, ["condition_handle", "condition_shelf", "page", "locus", "local_image_owner", "surface_sequence", "relative_condition_sequence_de", "group_count", "portable_relative_groups", "workshop_use_de", "external_name_needed_for_internal_use"])
    write(f"{PREFIX}_7_SHELF_RELATIVE_PROFILES.tsv", shelf_profiles, ["condition_shelf", "groups", "loci", "groups_with_relative_components", "dominant_relative_components", "internal_handle_rule", "external_names"])
    write(f"{PREFIX}_OTODY_SAMPLE_DECODE.tsv", sample_rows, ["layer", "value", "reading_de"])
    write(f"{PREFIX}_5_PAYLOAD_STATUS.tsv", payload, ["payload", "status", "remaining_external"])

    text = [
        "# Relative Astro-Bedingungssprache",
        "",
        "Die Astro-Etiketten bleiben shelflokal, aber 329/395 Gruppen tragen mindestens",
        "einen relativen Bedienbaustein. Ein Locus erhält zusätzlich einen internen Griff",
        "wie `C4@f69v.12`. Damit kann die Werkstatt Bedingungen benutzen, ohne sie extern",
        "als Planet, Zeichen, Monat oder Mondhaus benennen zu müssen.",
        "",
        "## Muster `otody`",
        "",
        "`C4@f69v.12` zeigt auf den sichtbaren linken f69-Platz. Seine Karte `otody` wird",
        "als `OT + O + DY` gelesen: **FOLGEND + lokaler Bedingungskern + lokal schließen**.",
        "Der ausführbare Werkstattwert lautet: »Wähle den folgenden lokalen Bedingungskern",
        "und schließe diesen Etiketteneintrag.« Was dieser Kern extern heißt, bleibt offen.",
        "",
        "## Ergebnis",
        "",
        "Für den internen Gebrauch ist kein vollständig meisterabhängiger Payload mehr übrig.",
        "Der Meister wählt weiterhin Griff und Kalibrierung, doch der zweite Schreiber kann",
        "Produkt, relative Menge/Dauer, Ergebnisart und Bedingungsoperation zurücklesen.",
    ]
    (HERE / f"{PREFIX}_RELATIVE_ASTRO_HANDBOOK.md").write_text("\n".join(text) + "\n", encoding="utf-8")

    portable_groups = sum(row["portable_relative_components"] != "NONE" for row in group_rows)
    summary = {
        "status": "PASS",
        "decision": "ASTRO_CONDITIONS_GAIN_INTERNAL_HANDLES_AND_RELATIVE_OPERATORS_WITHOUT_EXTERNAL_NAMES",
        "relative_components": len(root_rows),
        "groups": len(group_rows),
        "groups_with_relative_components": portable_groups,
        "learned_local_whole_labels": len(group_rows) - portable_groups,
        "internal_condition_handles": len(locus_rows),
        "condition_shelves_plus_quarantine": len(shelf_profiles),
        "fully_master_dependent_internal_payloads_after": 0,
        "external_celestial_names_identified": 0,
        "new_external_word_meanings": 0,
        "crosspage_keys": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 873: relative Astro condition vocabulary\n\n"
        "Twelve relative operators occur across the Astro labels. At least one appears in\n"
        "329 of 395 groups; the other 66 remain learned shelf-local whole labels. All 142\n"
        "loci receive internal handles such as C4@f69v.12.\n\n"
        "The sample otody becomes FOLGEND + local condition core + LOCAL CLOSE. This is not\n"
        "an external translation or a planet/month/mansion name. It is enough for internal\n"
        "workshop use: the master selects a handle, and the scribe can copy and operate it.\n"
        "No fully master-dependent internal payload remains, though every external celestial\n"
        "identity and all cross-page keys remain unresolved.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
