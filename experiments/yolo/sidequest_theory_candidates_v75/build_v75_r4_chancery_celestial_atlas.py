#!/usr/bin/env python3
"""Build V75 R4's complete, namespace-local celestial lookup edition."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = REPO / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = REPO / "experiments/yolo/sidequest_theory_candidates_v71"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def default_for(page: str, owner: str, event_index: str) -> tuple[str, str, str]:
    if page == "f67r2":
        return (
            f"Am lokalen Himmelsfeld „{owner}“ das Beschriftungsfragment {event_index} der zugehörigen Sektorbeziehung eintragen und nur innerhalb dieses Rades nachschlagen.",
            "PAIRED_CELESTIAL_RELATION_WHEEL_LOCAL_LOOKUP",
            "Iatromathematischer Rivale: örtliche Zeichen-, Körper- oder Wahlrelation; konkrete Namen bleiben im Exemplar.",
        )
    if page == "f68r1":
        return (
            f"Im lokalen Sternfeld „{owner}“ Fragment {event_index} des Stationsnamens oder Stationsmerkmals eintragen und nur im selben Paneel verwenden.",
            "MULTIPANEL_STAR_STATION_CATALOGUE_LOCAL_LOOKUP",
            "Astronomischer Rivale: Sternname, Sternbildteil oder Mondstationsmerkmal aus dem lokalen Exemplar.",
        )
    if "RADIAL_SLOT" in owner:
        return (
            f"Am ungeordneten linken Radialplatz „{owner}“ Fragment {event_index} der lokalen Wahl- oder Meidungsnotiz eintragen; weder Start noch Umlaufrichtung übernehmen.",
            "LEFT_WHEEL_UNORDERED_28_SLOT_LOCAL_LOOKUP",
            "Almanach-Rivale: lokaler Mondtag oder Mondhaus mit Tätigkeit; Nummer und Richtung sind unbewiesen.",
        )
    return (
        f"Im eigenständigen Rad „{owner}“ Fragment {event_index} der örtlichen Radlegende eintragen; kein Wert darf in ein anderes f69v-Rad übergehen.",
        "INDEPENDENT_CELESTIAL_WHEEL_RING_LEGEND",
        "Kosmographischer Rivale: eigenständige Rad-, Sphären- oder Kalenderlegende ohne Arbeitsanweisung.",
    )


def main() -> None:
    groups = read_tsv(V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv")
    owners = [row for row in read_tsv(V71 / "V71_SELECTED_OWNER_LEDGER.tsv") if row["unit_kind"] == "ASTRO_LOCUS"]
    owner_by_locus = {row["unit_id"]: row for row in owners}

    group_rows: list[dict[str, object]] = []
    for row in groups:
        owner = owner_by_locus[row["locus"]]
        default, source_class, historical_rival = default_for(row["page"], owner["selected_visible_owner"], row["event_index"])
        group_rows.append({
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "surface_display_only": row["surface_display_only"],
            "owner_status": owner["owner_status"],
            "local_namespace_owner": owner["selected_visible_owner"],
            "exact_literal_layer": f"[SURFACE:{row['surface_display_only']}] > [OPAQUE_LOCAL:{row['opaque_local_id']}] > [OWNER:{owner['selected_visible_owner']}] > [EXEMPLAR:LOCAL_CELESTIAL_LABEL_OR_RULE_FRAGMENT]",
            "concrete_local_default": default,
            "source_class": source_class,
            "confidence": "0.34" if owner["owner_status"] == "DIRECT_VISIBLE" else "0.22",
            "historical_celestial_rival": historical_rival,
            "technical_or_formal_rival": "Das Fragment ist nur eine opake kopierte Beschriftung des sichtbaren Diagrammpostens, ohne rekonstruierbaren Sachwert.",
            "strongest_contradiction": "Weder Oberfläche noch Position identifiziert den externen Namen, die Tätigkeit, den Startpunkt oder die Leserichtung.",
            "orientation_status": "EDITORIAL_LOCUS_ORDER_ONLY; AUTHORIAL_START_DIRECTION_ROTATION_UNPROVEN",
            "cross_namespace_mapping": "NONE",
            "semantic_ceiling": "CONCRETE_LOCAL_EXEMPLAR_NOT_TRANSLATED_WORD_OR_CROSS_PAGE_KEY",
        })

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in group_rows:
        by_locus[str(row["locus"])].append(row)
    locus_rows: list[dict[str, object]] = []
    for owner in owners:
        rows = by_locus[owner["unit_id"]]
        locus_rows.append({
            "locus": owner["unit_id"],
            "page": owner["page"],
            "diagram_id": owner["record_or_diagram"],
            "group_count": len(rows),
            "group_serials": "|".join(str(row["group_serial"]) for row in rows),
            "owner_status": owner["owner_status"],
            "local_namespace_owner": owner["selected_visible_owner"],
            "visible_basis": owner["visible_basis"],
            "concrete_locus_reading": " ".join(str(row["concrete_local_default"]) for row in rows),
            "historical_rival": owner["strongest_rival"],
            "orientation_status": "UNSELECTED",
            "cross_namespace_mapping": "NONE",
            "strongest_contradiction": "Die vollständige Lesung ist ein occurrence-gebundenes Exemplar, nicht aus den sichtbaren Fragmenten übersetzt.",
            "semantic_ceiling": "LOCAL_CELESTIAL_LOCUS_NOT_WORD_OR_EXTERNAL_NAME",
        })

    page_specs = {
        "f67r2": ("A1", "Zwei getrennte Himmelsräder: lokale Sektor- und Ringbeziehungen nachschlagen; das zweite Rad nicht als Fortsetzung des ersten lesen."),
        "f68r1": ("A2", "Mehrpaneeliger Sternstationsatlas: Paneelkopf, lokales Zentrum und einzelne Sternplätze getrennt führen; keine Gesamtrotation auswählen."),
        "f69v": ("A3", "Drei eigenständige Räder: Ringtexte getrennt halten; nur das linke Rad besitzt 28 editorisch adressierte, aber ungeordnete Radialplätze."),
    }
    instrument_rows: list[dict[str, object]] = []
    for page, (diagram_id, reading) in page_specs.items():
        rows = [row for row in locus_rows if row["page"] == page]
        group_count = sum(int(str(row["group_count"])) for row in rows)
        instrument_rows.append({
            "diagram_id": diagram_id,
            "page": page,
            "locus_count": len(rows),
            "group_count": group_count,
            "local_namespace_count": len({row["local_namespace_owner"] for row in rows}),
            "complete_instrument_reading": reading,
            "copying_rule": "Copy owner-local fragments from master exemplar; reset at panel or wheel boundary.",
            "orientation_rule": "Do not select start, direction, or rotation.",
            "cross_page_rule": "NO_F68_F69_MAPPING; NO_PROSE_CARD_IMPORT",
            "strongest_rival": "Celestial iconographic or mnemonic diagram with no operational semantic content.",
            "semantic_ceiling": "COMPLETE_LOCAL_CELESTIAL_WORKING_EDITION_NOT_DECIPHERMENT",
        })

    orientation_rows = [
        {"namespace": "A1_RIGHT_12_SECTOR_WHEEL", "slot_count": 12, "allowed_starts": 12, "allowed_directions": 2, "variant_count": 24, "selected_variant": "NONE", "reason": "No authorial start or arrow is visible."},
        {"namespace": "A1_LEFT_LOCAL_FIELDS", "slot_count": 0, "allowed_starts": 0, "allowed_directions": 0, "variant_count": 0, "selected_variant": "NONCYCLIC_OR_UNRESOLVED", "reason": "V70 did not license one cyclic left inventory."},
        {"namespace": "A2_STAR_STATIONS", "slot_count": 28, "allowed_starts": 28, "allowed_directions": 2, "variant_count": 56, "selected_variant": "NONE", "reason": "Stations are local to a multipanel atlas; global rotation is unproved."},
        {"namespace": "A3_LEFT_RADIAL_SLOTS", "slot_count": 28, "allowed_starts": 28, "allowed_directions": 2, "variant_count": 56, "selected_variant": "NONE", "reason": "Only unordered local slot identity is visible."},
        {"namespace": "A3_MIDDLE_AND_RIGHT_WHEELS", "slot_count": 0, "allowed_starts": 0, "allowed_directions": 0, "variant_count": 0, "selected_variant": "SEPARATE_RING_TEXTS", "reason": "They are separate wheels and not a continuation of the left 28 slots."},
    ]

    write_tsv(OUT / "V75_R4_395_GROUP_CELESTIAL_ATLAS.tsv", group_rows, list(group_rows[0]))
    write_tsv(OUT / "V75_R4_142_LOCUS_CELESTIAL_ATLAS.tsv", locus_rows, list(locus_rows[0]))
    write_tsv(OUT / "V75_R4_THREE_INSTRUMENTS.tsv", instrument_rows, list(instrument_rows[0]))
    write_tsv(OUT / "V75_R4_ORIENTATION_AUDIT.tsv", orientation_rows, list(orientation_rows[0]))

    checks = {
        "groups_395": len(group_rows) == 395,
        "group_serials_exact": [int(row["group_serial"]) for row in group_rows] == list(range(1, 396)),
        "loci_142": len(locus_rows) == 142,
        "instruments_3": len(instrument_rows) == 3,
        "page_counts": {(row["page"], int(row["locus_count"]), int(row["group_count"])) for row in instrument_rows} == {("f67r2", 74, 190), ("f68r1", 37, 65), ("f69v", 31, 140)},
        "f69_left_slots_28": sum("A3_LEFT_RADIAL_SLOT" in str(row["local_namespace_owner"]) for row in locus_rows) == 28,
        "all_defaults_concrete": all(str(row["concrete_local_default"]).strip() for row in group_rows),
        "no_cross_mapping": all(row["cross_namespace_mapping"] == "NONE" for row in group_rows),
        "no_orientation_selected": all(row["selected_variant"] in {"NONE", "NONCYCLIC_OR_UNRESOLVED", "SEPARATE_RING_TEXTS"} for row in orientation_rows),
        "f84_not_named": not any("f84" in str(row["page"]).lower() for row in group_rows),
    }
    validation = {
        "schema": "V75_R4_CHANCERY_CELESTIAL_ATLAS_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"groups": len(group_rows), "loci": len(locus_rows), "instruments": len(instrument_rows), "orientation_rows": len(orientation_rows)},
        "checks": checks,
        "sealed_pages_opened": [],
        "active_v75_sibling_outputs_read": False,
    }
    (OUT / "V75_R4_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))
    print(json.dumps(validation["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
