#!/usr/bin/env python3
"""Build a complete, orientation-explicit V66 R4 Astro audit."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v22/V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = {"f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PAGE_ROLE = {
    "f67r2": "SEVEN_BY_TWELVE_CONFIGURATION_SELECTOR",
    "f68r1": "CENTRE_PLUS_TWENTY_EIGHT_SPATIAL_CATALOGUE",
    "f69v": "INDEPENDENT_TWENTY_EIGHT_RULE_SCHEDULE",
}


DIAGRAMS = {
    "f67r2": {
        "loci": 74,
        "groups": 190,
        "default_de": (
            "Wähle zuerst einen der sieben Himmelsregenten, dann einen der zwölf Tierkreisbereiche und schließlich die im Sektor "
            "notierte Bedingung. Lies daraus, ob die geplante Waschung, Arzneigabe, Ruhe, Entleerung oder örtliche Anwendung an diesem "
            "Zeitpunkt ausgeführt, gemildert oder verschoben wird. Die weiteren Zwölfer- und Achterfelder liefern Kontrollbedingungen."
        ),
        "rival": "allgemeine 7×12 Arbeits-/Qualitätstafel ohne Medizin",
        "uncertainty": "Die Zeichnung zeigt keine vollständige 7×12-Matrix; Planet, Zeichen, Körperteil und Startsektor sind externe Defaults.",
    },
    "f68r1": {
        "loci": 37,
        "groups": 65,
        "default_de": (
            "Das Zentrum bezeichnet den Mond als Katalogbesitzer. Die 28 äußeren Orte sind räumliche Stationsadressen; der Benutzer "
            "identifiziert die Station an ihrer gezeichneten Lage und liest deren örtlich gelernte Bezeichnung. Ohne markierten Start "
            "bleibt jede moderne Nummerierung eine redaktionelle Rotation."
        ),
        "rival": "räumlicher Stern-/Stationsindex ohne Wahlregeln",
        "uncertainty": "Weder Laufrichtung noch erster Ort ist sichtbar; die 28 Namen werden nicht aus den Oberflächen gelesen.",
    },
    "f69v": {
        "loci": 31,
        "groups": 140,
        "default_de": (
            "Lies die drei Kreistextbänder als Gebrauchsanweisung und danach jeden der 28 radialen Plätze als vollständige lokale Regel: "
            "baden oder waschen, salben, ruhen, seihen, eine Portion verkleinern, eine Anwendung wiederholen oder bei ungünstiger "
            "Bedingung aussetzen. Die Reihenfolge ist seitenlokal und wird nicht mit f68r1 gleichgesetzt."
        ),
        "rival": "28-stufiger Werkstatt-/Kalenderplan ohne Himmelssemantik",
        "uncertainty": "LONG/SHORT ist keine Polarität; Start, Richtung und externe Kalenderphase fehlen.",
    },
}


def main() -> None:
    rows = [r for r in read_tsv(SOURCE) if r["page"] in PAGES]
    rows.sort(key=lambda r: int(r["source_event_serial"]))
    out = []
    for row in rows:
        out.append({
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "surface_display_only": row["surface"],
            "opaque_astro_id": row["exact_tuple_id"],
            "page_local_role": PAGE_ROLE[row["page"]],
            "complete_local_default_en": row["default_English"],
            "source_class": row["source_class"],
            "confidence": row["confidence"],
            "orientation_status": "UNORIENTED_LOCAL_LOCUS",
            "cross_page_identity": "NONE_ASSIGNED",
            "interpretive_limit": "LOCAL_DIAGRAM_MNEMONIC_NOT_WORD_TRANSLATION",
        })

    by_locus = defaultdict(list)
    for row in out:
        by_locus[(row["page"], row["locus"])].append(row)
    locus_rows = []
    for (page, locus), members in sorted(by_locus.items(), key=lambda x: min(int(r["opaque_astro_id"].split("_")[-2]) for r in x[1])):
        locus_rows.append({
            "page": page,
            "locus": locus,
            "group_count": len(members),
            "surface_sequence": " ".join(r["surface_display_only"] for r in members),
            "complete_local_reading_en": "; ".join(r["complete_local_default_en"] for r in members),
            "page_local_role": PAGE_ROLE[page],
            "cross_page_identity": "NONE_ASSIGNED",
        })

    diagram_rows = []
    for page in ["f67r2", "f68r1", "f69v"]:
        cfg = DIAGRAMS[page]
        diagram_rows.append({
            "page": page,
            "locus_count": cfg["loci"],
            "group_count": cfg["groups"],
            "selected_role": PAGE_ROLE[page],
            "complete_diagram_default_de": cfg["default_de"],
            "strongest_rival": cfg["rival"],
            "orientation_uncertainty": cfg["uncertainty"],
            "direct_join_to_other_page": "NO",
        })

    orientation_rows = [
        {"page": "f67r2", "variant": "A", "start": "MODERN_TOP_ONLY", "direction": "CLOCKWISE", "status": "EDITORIAL_EXAMPLE", "effect": "changes all external planet/sign labels; leaves visible selector topology unchanged"},
        {"page": "f67r2", "variant": "B", "start": "ONE_SECTOR_ROTATED", "direction": "COUNTERCLOCKWISE", "status": "EQUALLY_VISIBLE", "effect": "different named governors/signs; identical internal adjacency class"},
        {"page": "f68r1", "variant": "A", "start": "MODERN_TOP_ONLY", "direction": "CLOCKWISE", "status": "EDITORIAL_EXAMPLE", "effect": "assigns catalogue numbers 1..28"},
        {"page": "f68r1", "variant": "B", "start": "ANY_OF_28", "direction": "EITHER", "status": "56_EQUIVALENT_ORIENTATIONS", "effect": "renames every station while preserving the spatial catalogue"},
        {"page": "f69v", "variant": "A", "start": "MODERN_FIRST_RADIAL_LOCUS", "direction": "CLOCKWISE", "status": "EDITORIAL_EXAMPLE", "effect": "orders the 28 local rule slots"},
        {"page": "f69v", "variant": "B", "start": "ANY_OF_28", "direction": "EITHER", "status": "56_EQUIVALENT_ORIENTATIONS", "effect": "changes external day/mansion numbers while preserving the page-local cyclic schedule"},
    ]

    write_tsv(HERE / "V66_R4_395_GROUP_ASTRO_LEDGER.tsv", out, list(out[0]))
    write_tsv(HERE / "V66_R4_142_LOCUS_READINGS.tsv", locus_rows, list(locus_rows[0]))
    write_tsv(HERE / "V66_R4_3_DIAGRAM_EDITIONS.tsv", diagram_rows, list(diagram_rows[0]))
    write_tsv(HERE / "V66_R4_ORIENTATION_ALTERNATIVES.tsv", orientation_rows, list(orientation_rows[0]))

    counts = Counter(r["page"] for r in out)
    locus_counts = Counter(r["page"] for r in locus_rows)
    checks = {
        "groups_395": len(out) == 395,
        "loci_142": len(locus_rows) == 142,
        "diagram_count_3": len(diagram_rows) == 3,
        "page_group_counts": counts == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "page_locus_counts": locus_counts == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}),
        "all_defaults_nonempty": all(r["complete_local_default_en"].strip() for r in out),
        "all_local_astrology_scope": all(r["opaque_astro_id"].startswith("ASTRO_") for r in out),
        "no_cross_page_identity": all(r["cross_page_identity"] == "NONE_ASSIGNED" for r in out),
        "no_sealed_page": all(not r["page"].startswith("f84") for r in out),
    }
    payload = {
        "artifact": "V66_R4_ASTRO_CORRECTOR_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"groups": len(out), "loci": len(locus_rows), "diagrams": len(diagram_rows)},
        "page_groups": dict(counts),
        "checks": checks,
        "interpretive_limit": "Completeness and orientation audit do not identify planets, signs, mansions, meanings, language, or sound.",
    }
    (HERE / "V66_R4_VALIDATION.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
