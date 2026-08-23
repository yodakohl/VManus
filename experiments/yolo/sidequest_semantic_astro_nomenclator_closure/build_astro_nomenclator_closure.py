#!/usr/bin/env python3
"""Close the 63 local Astro nomenclator occurrences into teachable families."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent / "sidequest_semantic_ten_page_register_bridge"

GROUPS_IN = BRIDGE / "ASTRO_395_BRIDGED_GROUPS.tsv"
LOCI_IN = BRIDGE / "ASTRO_142_BRIDGED_LOCI.tsv"
UNIFIED_IN = BRIDGE / "TEN_PAGE_776_UNIFIED_READING.tsv"

FAMILY_OUT = HERE / "LOCAL_ASTRO_10_FAMILIES.tsv"
RESOLUTION_OUT = HERE / "LOCAL_ASTRO_63_RESOLUTION.tsv"
GROUPS_OUT = HERE / "ASTRO_395_NOMENCLATOR_CLOSED.tsv"
LOCI_OUT = HERE / "ASTRO_142_NOMENCLATOR_CLOSED_LOCI.tsv"
UNIFIED_OUT = HERE / "TEN_PAGE_776_NOMENCLATOR_CLOSED.tsv"
CARD_OUT = HERE / "ASTRO_APPRENTICE_CARD.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"


FAMILIES = {
    "N01_VALUE_SIGNS": (
        "A O E S D G R Y Q",
        "KURZWERTACHSE",
        "A Hauptwert; O Grundwert; E Auswahlwert; S Nebenwert; D fest; G Grad; R Bezug; Y aktuell; Q neuer Eintrag",
    ),
    "N02_AM_ASPECT": (
        "am",
        "ASPEKTWERT",
        "AM bezeichnet einen Winkel-, Beziehungs- oder Aspektwert des lokalen Sternfeldes.",
    ),
    "N03_TO_TE_PLACE_PHASE": (
        "to te tay tey teo",
        "PLATZ_ODER_PHASE",
        "TO bezeichnet einen Platz; TE/TAY/TEY/TEO konkretisieren ihn als Phase oder Zeitpunkt.",
    ),
    "N04_K_HOUSE_CLASS": (
        "k ke ka ko kos",
        "HAUS_KLASSE_QUALITAET",
        "K/KE ist Haus oder Klasse; KA eine Qualität; KO/KOS eine Grund- oder Unterklasse.",
    ),
    "N05_CHE_READOUT": (
        "che cheo chey",
        "ABLESUNG_ERGEBNIS",
        "CHE/CHEO/CHEY bezeichnet einen abgeleiteten, sichtbaren oder auszugebenden Tabellenwert.",
    ),
    "N06_CH_CTH_CONDITION": (
        "ch chs cth",
        "ZUSTAND_BEDINGUNG",
        "CH/CHS/CTH bezeichnet Zustand, Zeichenlage oder Bedingung des adressierten Platzes.",
    ),
    "N07_IIR_INDEX": (
        "iir",
        "INDEXNUMMER",
        "IIR ist eine lokale Index- oder Ordnungszahl im 28-Platz-Inventar.",
    ),
    "N08_P_RELATION_SELECTION": (
        "p pch cph",
        "BEZUG_ODER_AUSWAHL",
        "P/PCH/CPH wählt oder paart einen lokalen Bezug.",
    ),
    "N09_FY_YG_LIGHT_GRADE": (
        "fy yg",
        "LICHT_ODER_GRADWERT",
        "FY/YG trägt einen Licht-, Stärke- oder Gradwert.",
    ),
    "N10_ENTRY_ENDING": (
        "dy ody",
        "FEST_EINGETRAGEN",
        "DY/ODY schließt hier keinen Satz, sondern markiert einen fest eingetragenen Diagrammwert.",
    ),
}

SUPPORT_TOKENS = {
    "N01_VALUE_SIGNS": {"A", "O", "E", "S", "D", "G", "R", "Y", "Q"},
    "N02_AM_ASPECT": {"AM"},
    "N03_TO_TE_PLACE_PHASE": {"TO", "TE", "TAY", "TEO"},
    "N04_K_HOUSE_CLASS": {"K", "KE", "KA", "KO", "KOS"},
    "N05_CHE_READOUT": {"CHE", "CHEO", "CHEY"},
    "N06_CH_CTH_CONDITION": {"CH", "CHS", "CTH"},
    "N07_IIR_INDEX": {"IIR"},
    "N08_P_RELATION_SELECTION": {"PCH", "CPH", "EOP"},
    "N09_FY_YG_LIGHT_GRADE": {"FY", "YG"},
    "N10_ENTRY_ENDING": {"DY", "ODY"},
}


# surface -> family, segmentation, compact default
LOCAL_MAP = {
    "a": ("N01_VALUE_SIGNS", "A", "Hauptwert"),
    "d": ("N01_VALUE_SIGNS", "D", "Festwert"),
    "g": ("N01_VALUE_SIGNS", "G", "Gradwert"),
    "o": ("N01_VALUE_SIGNS", "O", "Grundwert"),
    "r": ("N01_VALUE_SIGNS", "R", "Bezugswert"),
    "s": ("N01_VALUE_SIGNS", "S", "Nebenwert"),
    "ay": ("N01_VALUE_SIGNS", "A+Y", "aktueller Hauptwert"),
    "ey": ("N01_VALUE_SIGNS", "E+Y", "aktueller Auswahlwert"),
    "es": ("N01_VALUE_SIGNS", "E+S", "ausgewählter Nebenwert"),
    "og": ("N01_VALUE_SIGNS", "O+G", "Grundgrad"),
    "odas": ("N01_VALUE_SIGNS", "O+D+A+S", "fester Nebenwert"),
    "qsg": ("N01_VALUE_SIGNS", "Q+S+G", "neuer Nebengrad"),
    "am": ("N02_AM_ASPECT", "AM", "Aspektwert"),
    "amy": ("N02_AM_ASPECT", "AM+Y", "aktueller Aspektwert"),
    "ydam": ("N02_AM_ASPECT", "Y+D+AM", "festgelegter Aspektwert"),
    "yto": ("N03_TO_TE_PLACE_PHASE", "Y+TO", "aktueller Platz"),
    "ytody": ("N03_TO_TE_PLACE_PHASE", "Y+TO+DY", "Platz fest eingetragen"),
    "yteody": ("N03_TO_TE_PLACE_PHASE", "Y+TEO+DY", "Phasenplatz fest eingetragen"),
    "yteos": ("N03_TO_TE_PLACE_PHASE", "Y+TEO+S", "sekundärer Phasenplatz"),
    "ytoeopchey": ("N03_TO_TE_PLACE_PHASE", "Y+TO+EOP+CHEY", "Vergleichswert dieses Platzes"),
    "chetody": ("N03_TO_TE_PLACE_PHASE", "CHE+TO+DY", "abgeleiteter Platzwert"),
    "dchetay": ("N03_TO_TE_PLACE_PHASE", "D+CHE+TAY", "fester Hauptphasenwert"),
    "tochso": ("N03_TO_TE_PLACE_PHASE", "TO+CHS+O", "Grundzustand dieses Platzes"),
    "tey": ("N03_TO_TE_PLACE_PHASE", "TE+Y", "aktueller Phasenwert"),
    "yetey": ("N03_TO_TE_PLACE_PHASE", "Y+E+TE+Y", "ausgewählter Phasenwert"),
    "ykeody": ("N04_K_HOUSE_CLASS", "Y+KE+ODY", "Klassenplatz fest eingetragen"),
    "eykeody": ("N04_K_HOUSE_CLASS", "E+Y+KE+ODY", "ausgewählter Klassenplatz"),
    "chekody": ("N04_K_HOUSE_CLASS", "CHE+K+ODY", "abgeleiteter Klassenwert"),
    "ykey": ("N04_K_HOUSE_CLASS", "Y+KE+Y", "aktuelle Klasse"),
    "ykeydy": ("N04_K_HOUSE_CLASS", "Y+KE+Y+DY", "aktuelle Klasse fest"),
    "yky": ("N04_K_HOUSE_CLASS", "Y+K+Y", "aktuelles Haus"),
    "cheyky": ("N04_K_HOUSE_CLASS", "CHEY+K+Y", "Ablesung dieses Hauses"),
    "yka": ("N04_K_HOUSE_CLASS", "Y+KA", "aktuelle Qualität"),
    "ykady": ("N04_K_HOUSE_CLASS", "Y+KA+DY", "aktuelle Qualität fest"),
    "qkoy": ("N04_K_HOUSE_CLASS", "Q+KO+Y", "neue Grundklasse"),
    "sykos": ("N04_K_HOUSE_CLASS", "S+Y+KOS", "sekundäre Grundklasse"),
    "cheo": ("N05_CHE_READOUT", "CHEO", "Ablesewert"),
    "cheos": ("N05_CHE_READOUT", "CHEO+S", "sekundärer Ablesewert"),
    "cheody": ("N05_CHE_READOUT", "CHEO+DY", "Ablesewert fest"),
    "ycheody": ("N05_CHE_READOUT", "Y+CHEO+DY", "aktueller Ablesewert fest"),
    "ychey": ("N05_CHE_READOUT", "Y+CHEY", "aktueller Ablesewert"),
    "ch": ("N06_CH_CTH_CONDITION", "CH", "Zustand"),
    "dchy": ("N06_CH_CTH_CONDITION", "D+CH+Y", "fester Zustand"),
    "chsdy": ("N06_CH_CTH_CONDITION", "CHS+DY", "sekundärer Zustand fest"),
    "octhey": ("N06_CH_CTH_CONDITION", "O+CTH+E+Y", "ausgewählte Grundbedingung"),
    "octhys": ("N06_CH_CTH_CONDITION", "O+CTH+Y+S", "sekundäre Grundbedingung"),
    "odchecthy": ("N06_CH_CTH_CONDITION", "O+D+CHE+CTH+Y", "feste abgeleitete Bedingung"),
    "doiir": ("N07_IIR_INDEX", "D+O+IIR", "fester Grundindex"),
    "saiir": ("N07_IIR_INDEX", "S+A+IIR", "sekundärer Hauptindex"),
    "ocphy": ("N08_P_RELATION_SELECTION", "O+CPH+Y", "Grundauswahl"),
    "qopchy": ("N08_P_RELATION_SELECTION", "Q+O+PCH+Y", "neuer Paarbezug"),
    "ofydy": ("N09_FY_YG_LIGHT_GRADE", "O+FY+DY", "fester Grundlichtwert"),
    "oygy": ("N09_FY_YG_LIGHT_GRADE", "O+YG+Y", "aktueller Grundgrad"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    groups = read_tsv(GROUPS_IN)
    loci = read_tsv(LOCI_IN)
    unified = read_tsv(UNIFIED_IN)
    local_rows = [row for row in groups if row["bridge_class"] == "LOCAL_ASTRO_NOMENCLATOR"]
    assert (len(groups), len(loci), len(unified), len(local_rows)) == (395, 142, 776, 63)
    local_types = {row["surface_display"] for row in local_rows}
    assert len(local_types) == 53
    assert local_types == set(LOCAL_MAP), (sorted(local_types - set(LOCAL_MAP)), sorted(set(LOCAL_MAP) - local_types))

    occurrence_counts = Counter(row["surface_display"] for row in local_rows)
    family_counts = Counter(LOCAL_MAP[row["surface_display"]][0] for row in local_rows)
    family_types: dict[str, set[str]] = defaultdict(set)
    for surface, (family, _segmentation, _reading) in LOCAL_MAP.items():
        family_types[family].add(surface)

    support_types: dict[str, set[str]] = defaultdict(set)
    support_occurrences: Counter[str] = Counter()
    for surface, (_primary_family, segmentation, _reading) in LOCAL_MAP.items():
        tokens = set(segmentation.split("+"))
        for family_id, licensed_tokens in SUPPORT_TOKENS.items():
            if tokens & licensed_tokens:
                support_types[family_id].add(surface)
                support_occurrences[family_id] += occurrence_counts[surface]

    family_rows = []
    for family_id, (visible_material, nucleus, rule) in FAMILIES.items():
        family_rows.append({
            "family_id": family_id,
            "visible_material": visible_material,
            "compact_nucleus_de": nucleus,
            "teaching_rule_de": rule,
            "resolved_surface_types": str(len(family_types.get(family_id, set()))),
            "resolved_occurrences": str(family_counts.get(family_id, 0)),
            "supporting_surface_types": str(len(support_types.get(family_id, set()))),
            "supporting_occurrences": str(support_occurrences.get(family_id, 0)),
            "surface_inventory": ";".join(sorted(family_types.get(family_id, set()))) or "BOUND_ENDING_ONLY",
        })

    resolution_rows = []
    by_group_id: dict[str, dict[str, str]] = {}
    for row in local_rows:
        family, segmentation, compact = LOCAL_MAP[row["surface_display"]]
        resolved = {
            "group_serial": row["group_serial"],
            "opaque_local_id": row["opaque_local_id"],
            "page": row["page"],
            "locus": row["locus"],
            "namespace_id": row["namespace_id"],
            "local_image_owner": row["local_image_owner"],
            "local_content_class": row["local_content_class"],
            "surface_display": row["surface_display"],
            "family_id": family,
            "segmentation": segmentation,
            "compact_default_de": compact,
            "closed_workshop_reading_de": f"{row['local_image_owner']}: {compact}.",
            "copy_rule_de": "Familie und Achsen lesen; die konkrete Stern-, Sektor- oder Tabellenadresse aus dem sichtbaren Besitzer übernehmen.",
        }
        resolution_rows.append(resolved)
        by_group_id[row["opaque_local_id"]] = resolved

    closed_groups = []
    compact_by_group: dict[str, str] = {}
    for row in groups:
        out = dict(row)
        if row["opaque_local_id"] in by_group_id:
            resolved = by_group_id[row["opaque_local_id"]]
            out["nomenclator_status"] = "FAMILY_RESOLVED"
            out["nomenclator_family"] = resolved["family_id"]
            out["local_segmentation"] = resolved["segmentation"]
            out["compact_operational_default_de"] = resolved["compact_default_de"]
            out["closed_workshop_reading_de"] = resolved["closed_workshop_reading_de"]
        else:
            out["nomenclator_status"] = "COMMON_BRIDGE_RETAINED"
            out["nomenclator_family"] = "COMMON_22_COMPONENT_BRIDGE"
            out["local_segmentation"] = row["matched_component_ids"]
            out["compact_operational_default_de"] = row["matched_component_values_de"]
            out["closed_workshop_reading_de"] = row["astro_working_reading_de"]
        compact_by_group[row["opaque_local_id"]] = out["compact_operational_default_de"]
        closed_groups.append(out)

    groups_by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in closed_groups:
        groups_by_locus[(row["page"], row["locus"])].append(row)
    closed_loci = []
    for row in loci:
        members = groups_by_locus[(row["page"], row["locus"])]
        assert len(members) == int(row["group_count"])
        assert " ".join(member["surface_display"] for member in members) == row["surface_sequence"]
        out = dict(row)
        out["nomenclator_family_sequence"] = " || ".join(member["nomenclator_family"] for member in members)
        out["compact_default_sequence_de"] = " | ".join(member["compact_operational_default_de"] for member in members)
        out["family_resolved_groups"] = str(sum(member["nomenclator_status"] == "FAMILY_RESOLVED" for member in members))
        out["closed_locus_reading_de"] = f"{row['local_image_owner']}: " + out["compact_default_sequence_de"] + "."
        closed_loci.append(out)

    closed_unified = []
    for row in unified:
        out = dict(row)
        if row["register"] == "ASTRO_DIAGRAM":
            resolved_group = next(group for group in closed_groups if group["opaque_local_id"] == row["local_unit_id"])
            out["mechanism"] = resolved_group["nomenclator_status"]
            out["operational_reading_de"] = resolved_group["closed_workshop_reading_de"]
            out["register_rule_de"] = "Diagramm: gemeinsame Kürzel plus lokale Astro-Familie lesen; Besitzer liefert die konkrete Adresse."
        out["nomenclator_layer"] = "PROSE_NOT_APPLICABLE" if row["register"] == "PROSE_WORKSHOP" else (
            "LOCAL_ASTRO_FAMILY" if row["local_unit_id"] in by_group_id else "COMMON_22_COMPONENT_BRIDGE"
        )
        closed_unified.append(out)

    card_lines = [
        "# Astro-Nomenklatorkarte für den Lehrling",
        "",
        "Die 63 bislang lokalen Gruppen sind 53 sichtbare Formen, aber nur zehn Lehrfamilien.",
        "",
        "## Achsen",
        "",
        "`Y` aktuell · `O` Grundwert · `A` Hauptwert · `E` ausgewählt · `S` Nebenwert · `D/DY` fest eingetragen · `Q` neuer Eintrag.",
        "",
        "## Inhaltsfamilien",
        "",
        "| Familie | Kern | Kurzregel | Hauptformen | gesamte Nutzung |",
        "|---|---|---|---:|---:|",
    ]
    for row in family_rows:
        card_lines.append(f"| {row['family_id']} | {row['compact_nucleus_de']} | {row['teaching_rule_de']} | {row['resolved_surface_types']} | {row['supporting_occurrences']} |")
    card_lines.extend([
        "",
        "Beispiele: `Y+TO+DY` = Platz fest eingetragen; `Y+KE+ODY` = Klassenplatz fest eingetragen; `AM+Y` = aktueller Aspektwert; `D+O+IIR` = fester Grundindex; `Y+CHEO+DY` = aktueller Ablesewert fest.",
        "",
        "Das sind Diagrammcodes, keine ausgesprochenen Sternnamen. Der sichtbare Platz liefert die konkrete Sache.",
    ])

    write_tsv(FAMILY_OUT, family_rows)
    write_tsv(RESOLUTION_OUT, resolution_rows)
    write_tsv(GROUPS_OUT, closed_groups)
    write_tsv(LOCI_OUT, closed_loci)
    write_tsv(UNIFIED_OUT, closed_unified)
    CARD_OUT.write_text("\n".join(card_lines) + "\n", encoding="utf-8")

    outputs = [FAMILY_OUT, RESOLUTION_OUT, GROUPS_OUT, LOCI_OUT, UNIFIED_OUT, CARD_OUT]
    summary = {
        "status": "PASS",
        "local_occurrences": len(local_rows),
        "local_surface_types": len(local_types),
        "teaching_families": len(FAMILIES),
        "astro_groups": len(closed_groups),
        "astro_loci": len(closed_loci),
        "unified_rows": len(closed_unified),
        "family_occurrences": dict(sorted(family_counts.items())),
        "family_support_occurrences": dict(sorted(support_occurrences.items())),
        "files": {path.name: {"sha256": sha256(path), "bytes": path.stat().st_size} for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
