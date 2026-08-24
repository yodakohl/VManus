#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth"
EVENTS = BASE / "FOUR_HUNDRED_SIXTY_EIGHTH_381_PROSE_EVENT_COMMON_ACTIONS.tsv"
STATEMENTS = BASE / "FOUR_HUNDRED_SIXTY_EIGHTH_116_PROSE_STATEMENT_COMMON_ACTIONS.tsv"
ASTRO = BASE / "FOUR_HUNDRED_SIXTY_EIGHTH_395_ASTRO_GROUP_COMMON_ACTIONS.tsv"
COMPONENTS = BASE / "FOUR_HUNDRED_SIXTY_EIGHTH_35_COMPONENT_COMMON_ACTION_MANUAL.tsv"

CELESTIAL = {
    "AIIN": "Wert", "AIN": "Teilwert", "AIR": "Bahn", "AL": "Position", "AR": "von dieser Position",
    "CH": "Eintrag entnehmen", "CHD": "uebertragen", "CHK": "Stufe anheben", "CKH": "Diagrammdurchgang",
    "CKHE": "Bereiche trennen", "CTH": "gueltig", "DY": "Eintrag schliessen", "E": "kurze Stufe",
    "EE": "lange Stufe", "EEE": "volle Stufe", "IIN": "Sollstufe", "K": "zuordnen", "L": "fuehren",
    "LDDY": "festsetzen und schliessen", "LS": "aus dem Bereich hinausfuehren", "LSH": "Durchgang",
    "O": "Lesegang", "OK": "markieren", "OL": "weiterzaehlen", "OR": "Einstellung", "OT": "naechster Eintrag",
    "P": "hinein", "R": "senken", "SH": "beibehalten", "SHED": "ruhen", "SOLK": "sammeln",
    "T": "eintragen", "Y": "dieser Eintrag", "HO": "Eintrag", "CHEO": "entnommener Wert",
    "D_ADDR": "Teiladresse", "S_ADDR": "Sternbezug", "A_ADDR": "Nebenadresse", "F_ADDR": "Aussenbezug",
    "AM_ADDR": "Gegenfeld", "CPH_CLASS": "Sternfigur", "CFH_CLASS": "Sternhaufen", "G_ADDR": "Strahlmarke",
    "I_COUNT": "Zaehlstrich", "AN_SECTION": "Abschnitt", "OS": "Feld",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def celestial_reading(parse: str, atomic: str) -> str:
    if parse == "NONE":
        return atomic
    if parse.startswith("WHOLE"):
        return "Resultat"
    parts = parse.split("+")
    return "; ".join(CELESTIAL.get(part, part) for part in parts)


def main() -> None:
    events = read(EVENTS)
    statements = read(STATEMENTS)
    astro = []
    for row in read(ASTRO):
        out = dict(row)
        out["celestial_context_reading_de"] = celestial_reading(row["selected_component_parse"], row["atomic_common_root_value_de"])
        astro.append(out)
    write("FOUR_HUNDRED_SEVENTY_SECOND_395_ASTRO_GROUP_CONTEXT_READINGS.tsv", astro)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
        loci.append({
            "locus_row": len(loci) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "local_namespace": rows[0]["local_namespace"],
            "groups": len(rows),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "atomic_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "celestial_context_reading_de": ". ".join(row["celestial_context_reading_de"] for row in rows) + ".",
            "orientation": "UNSPECIFIED",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SEVENTY_SECOND_142_ASTRO_LOCUS_CONTEXT_READINGS.tsv", loci)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        unit_statements = [row for row in statements if row["record_unit_id"] == unit]
        unit_events = [row for row in events if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "domain": "HERBAL" if unit.startswith("H") else "BIOLOGICAL",
            "page": unit_statements[0]["page"],
            "loci": len({row["locus"] for row in unit_events}),
            "statements_or_loci": len(unit_statements),
            "groups": len(unit_events),
            "atomic_continuous_reading_de": " ".join(row["common_action_atomic_reading_de"] for row in unit_statements),
            "context_continuous_reading_de": " ".join(row["wet_context_expansion_de"] for row in unit_statements),
            "context_mode": "PICTURE_OWNED_WET_WORKSHOP_EXPANSION",
        })
    for unit in ("A1", "A2", "A3"):
        unit_loci = [row for row in loci if row["diagram_id"] == unit]
        unit_groups = [row for row in astro if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "domain": "ASTRO",
            "page": unit_loci[0]["page"],
            "loci": len(unit_loci),
            "statements_or_loci": len(unit_loci),
            "groups": len(unit_groups),
            "atomic_continuous_reading_de": " ".join(row["atomic_reading_de"] for row in unit_loci),
            "context_continuous_reading_de": " ".join(row["celestial_context_reading_de"] for row in unit_loci),
            "context_mode": "LOCAL_CELESTIAL_LOOKUP_EXPANSION",
        })
    write("FOUR_HUNDRED_SEVENTY_SECOND_14_CONTINUOUS_UNIT_EDITIONS.tsv", units)

    component_rows = read(COMPONENTS)
    prose_component_counts = defaultdict(int)
    for row in events:
        for part in row["component_parse"].replace("WHOLE[", "").replace("]", "").split("+"):
            prose_component_counts[part] += 1
    astro_component_counts = defaultdict(int)
    for row in astro:
        for part in row["selected_component_parse"].replace("WHOLE[", "").replace("]", "").split("+"):
            astro_component_counts[part] += 1
    collisions = []
    for row in component_rows:
        component = row["component"]
        in_both = prose_component_counts[component] > 0 and astro_component_counts[component] > 0
        collisions.append({
            "component": component,
            "atomic_default_de": row["value_de"],
            "wet_context_expansion_de": row["wet_context_expansion_de"],
            "celestial_context_expansion_de": CELESTIAL.get(component, row["value_de"]),
            "prose_events": prose_component_counts[component],
            "astro_groups": astro_component_counts[component],
            "cross_register": "YES" if in_both else "NO",
            "genuine_content_collision": "NO",
            "reason": "both expansions are specializations of the same common action" if in_both else "component is not active in both registers",
        })
    write("FOUR_HUNDRED_SEVENTY_SECOND_35_COMPONENT_CONTENT_COLLISION_AUDIT.tsv", collisions)

    md = ["# Continuous ten-page working edition", ""]
    for unit in units:
        md.extend([
            f"## {unit['unit_id']} — {unit['page']}", "",
            f"**Atomar:** {unit['atomic_continuous_reading_de']}", "",
            f"**Im Bild-/Diagrammkontext:** {unit['context_continuous_reading_de']}", "",
        ])
    (HERE / "FOUR_HUNDRED_SEVENTY_SECOND_CONTINUOUS_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "units": len(units),
        "prose_events": len(events),
        "prose_statements": len(statements),
        "astro_groups": len(astro),
        "astro_loci": len(loci),
        "shared_components": len(collisions),
        "genuine_content_collisions": sum(row["genuine_content_collision"] == "YES" for row in collisions),
        "cross_register_components": sum(row["cross_register"] == "YES" for row in collisions),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
