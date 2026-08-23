#!/usr/bin/env python3
"""Bridge the completed prose workshop grammar into the three diagram registers."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROSE = HERE.parent / "sidequest_semantic_bound_carrier_closure"
ASTRO80 = HERE.parent / "sidequest_theory_candidates_v80"
ASTRO75 = HERE.parent / "sidequest_theory_candidates_v75"

PROSE_EVENTS_IN = PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv"
ASTRO_GROUPS_IN = ASTRO80 / "V80_R3_395_ASTRO_GROUPS.tsv"
ASTRO_LOCI_IN = ASTRO75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
NAMESPACES_IN = ASTRO75 / "V75_SELECTED_NAMESPACE_REGISTRY.tsv"

COMPONENTS_OUT = HERE / "SHARED_22_COMPONENT_BRIDGE.tsv"
ASTRO_GROUPS_OUT = HERE / "ASTRO_395_BRIDGED_GROUPS.tsv"
ASTRO_LOCI_OUT = HERE / "ASTRO_142_BRIDGED_LOCI.tsv"
UNIFIED_OUT = HERE / "TEN_PAGE_776_UNIFIED_READING.tsv"
EXAMPLES_OUT = HERE / "BRIDGE_EXAMPLES.tsv"
MANUAL_OUT = HERE / "TEN_PAGE_WORKSHOP_MANUAL.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"


# id -> patterns, common operational nucleus, prose expansion, astro expansion
COMPONENTS = {
    "B01_AIIN_VALUE": (["aiin"], "VORGABEWERT", "Sollmass einer Portion oder Stufe", "Sollwert oder Grad eines Diagrammplatzes"),
    "B02_AIR_COURSE": (["air"], "LAUF", "Wasserlauf", "Himmels-, Ring- oder Zeigerlauf"),
    "B03_AIN_PART": (["ain"], "TEILWERT", "Portion", "gezaehlter Teil oder Unterabschnitt"),
    "B04_IIN_STAGE": (["iin"], "STUFE", "Arbeitsstufe", "Grad- oder Bedingungsstufe"),
    "B05_OK_SET": (["ok"], "SETZEN", "Posten ansetzen", "Diagrammposten setzen oder aktivieren"),
    "B06_OT_NEXT": (["ot"], "FOLGE", "danach oder naechster Posten", "naechster Platz oder folgende Bedingung"),
    "B07_OL_CONTINUE": (["ol"], "FORTSETZEN", "Ansatz oder Weg weiterfuehren", "im selben Ring, Band oder Satz fortsetzen"),
    "B08_OR_WORKSET": (["or"], "ARBEITSSATZ", "Ansatz oder Zubereitung", "Bedingungs-, Tabellen- oder Wahlansatz"),
    "B09_AL_TARGET": (["al"], "ZIEL", "Zielstelle", "Zielsektor, Zielstern oder Zielfeld"),
    "B10_AR_SOURCE": (["ar"], "AUSGANG", "Quelle oder Ausgangsstelle", "Ausgangssektor, Ursprung oder Bezugswert"),
    "B11_HO_INPUT": (["ho"], "EINGANGSPOSTEN", "Zutat", "Himmelsobjekt oder Eingangsbedingung"),
    "B12_TY_PART_UNIT": (["ty"], "TEILPOSTEN", "Teil oder Restportion", "Teilsektor oder Untereintrag"),
    "B13_GRADE": (["eee", "ee"], "GRAD", "lange oder volle Einwirkung", "lange oder volle Diagrammstufe"),
    "B14_READOUT": (["cheey", "shey"], "ABLESEPRODUKT", "Klarlauf oder fertiger Auszug", "abgelesener oder freigegebener Wert"),
    "B15_HOLD": (["shed", "sh"], "HALTEN", "ruhen oder absetzen", "Position oder Bedingung halten"),
    "B16_TRANSFER": (["ched", "chd"], "UEBERTRAGEN", "Posten umsetzen", "Wert oder Platzbezug uebertragen"),
    "B17_PASS": (["ckhe", "ckh"], "DURCHGANG", "durch Leitung oder Seihweg fuehren", "durch Sektor, Ring oder Pruefweg fuehren"),
    "B18_ADJUST": (["chk"], "JUSTIEREN", "waermen oder temperieren", "Grad oder Diagrammzustand justieren"),
    "B19_PROCESS": (["kch"], "BEARBEITEN", "Arbeitsstoff bearbeiten", "Diagrammplatz berechnen oder bearbeiten"),
    "B20_DAN_APPLY": (["dan"], "ANWENDEN", "Zubereitung anwenden", "Bedingung oder Tabellenwert anwenden"),
    "B21_SOLK_COLLECT": (["solk"], "SAMMELPUNKT", "Auffangstelle", "Sammel-, Schnitt- oder Bezugspunkt"),
    "B22_SK_OUTPUT": (["sk"], "AUSGEBEN", "ausgiessen", "Wert oder Bezug ausgeben"),
}


EXACT_ASTRO_ADAPT = {
    "Sollmaß": "Sollwert oder Grad des bezeichneten Himmelsplatzes",
    "daraus": "vom bezeichneten Ausgangsplatz",
    "umsetzen": "auf den bezeichneten Diagrammplatz uebertragen",
    "dorthin": "zum bezeichneten Zielplatz",
    "Klarlauf": "abgelesener oder freigegebener Diagrammwert",
    "dieser Posten": "dieser lokale Diagrammposten",
    "Zutat": "Eingangsobjekt oder Eingangsbedingung",
    "Posten ansetzen": "diesen Diagrammposten setzen",
    "fortsetzen": "im selben Ring oder Band fortsetzen",
    "diesen Posten kurz bearbeiten": "diesen Diagrammplatz kurz bearbeiten",
    "diesen Posten bearbeiten": "diesen Diagrammplatz bearbeiten",
    "kühlen": "diesen Diagrammposten zuruecknehmen",
    "eine Portion zugeben": "einen gezaehlten Teilwert zugeben",
    "dort ansetzen": "am Zielplatz setzen",
    "länger ansetzen": "in langer Stufe setzen",
    "kurz ansetzen": "in kurzer Stufe setzen",
    "vollständig ansetzen; Schluss": "vollstaendig setzen und den Eintrag schliessen",
    "fortsetzen; Schluss": "fortsetzen und den Eintrag schliessen",
    "Fortsetzungsansatz": "fortgesetzter Bedingungs- oder Tabellensatz",
    "Ansatz": "Bedingungs- oder Tabellensatz",
    "Gefaess": "umschliessendes Diagrammfeld",
    "danach von dort": "danach vom bezeichneten Ausgangsplatz",
    "Folgeumsetzung; Schluss": "den folgenden Platz uebertragen und den Eintrag schliessen",
    "Folgeposten": "naechster Diagrammposten",
    "langer Folgeposten": "naechster Diagrammposten in langer Stufe",
    "danach fortsetzen": "danach im selben Ring oder Band fortsetzen",
    "Tuch": "Band-, Schleier- oder Abdecktraeger",
    "laenger ruhen": "diese Position laenger halten",
}


EXAMPLE_SURFACES = [
    "aiin",
    "dal",
    "chol",
    "okeey",
    "okar",
    "alaiin",
    "chedaiin",
    "otolor",
    "saral",
    "airchy",
    "oeoldan",
    "ykshy",
]


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


def owner_kind(content_class: str) -> str:
    value = content_class.upper()
    if "STAR" in value:
        return "Sternplatz"
    if "SECTOR" in value:
        return "Sektorplatz"
    if "SLOT" in value:
        return "Radialplatz"
    if "RING" in value or "BAND" in value:
        return "Ring- oder Bandstelle"
    if "HEADER" in value:
        return "Tafelkopf"
    if "LEGEND" in value:
        return "Legendenstelle"
    if "CENTRE" in value or "CENTER" in value or "FACE" in value:
        return "Zentrumsmarke"
    if "WHEEL" in value:
        return "Radstelle"
    return "lokaler Himmels- oder Kalenderplatz"


def build_pattern_index() -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    for component_id, (patterns, _common, _prose, astro) in COMPONENTS.items():
        for pattern in patterns:
            entries.append((pattern, component_id, astro))
    # Longer strings win. At equal length continuation/target/source operators
    # precede HO and SH, preventing CHOL-like strings from defaulting to HO.
    priority = {component_id: index for index, component_id in enumerate(COMPONENTS)}
    return sorted(entries, key=lambda row: (-len(row[0]), priority[row[1]], row[0]))


PATTERN_INDEX = build_pattern_index()


def component_matches(surface: str) -> tuple[list[tuple[int, int, str, str, str]], list[str]]:
    candidates: dict[int, list[tuple[int, str, str, str]]] = defaultdict(list)
    for pattern, component_id, astro in PATTERN_INDEX:
        start = 0
        while True:
            position = surface.find(pattern, start)
            if position < 0:
                break
            candidates[position].append((position + len(pattern), pattern, component_id, astro))
            start = position + 1

    @lru_cache(maxsize=None)
    def solve(position: int) -> tuple[int, tuple[tuple[int, int, str, str, str], ...]]:
        if position >= len(surface):
            return 0, ()
        best_score, best_matches = solve(position + 1)
        for end, pattern, component_id, astro in candidates.get(position, []):
            tail_score, tail_matches = solve(end)
            score = len(pattern) * 100 + len(pattern) * len(pattern) + tail_score
            proposal = ((position, end, pattern, component_id, astro),) + tail_matches
            if score > best_score:
                best_score, best_matches = score, proposal
        return best_score, best_matches

    _score, selected = solve(0)
    mask = [False] * len(surface)
    for start, end, _pattern, _component_id, _astro in selected:
        for index in range(start, end):
            mask[index] = True
    residuals: list[str] = []
    index = 0
    while index < len(surface):
        if mask[index]:
            index += 1
            continue
        end = index + 1
        while end < len(surface) and not mask[end]:
            end += 1
        residuals.append(surface[index:end])
        index = end
    return list(selected), residuals


def build() -> dict[str, object]:
    prose_events = read_tsv(PROSE_EVENTS_IN)
    astro_groups = read_tsv(ASTRO_GROUPS_IN)
    astro_loci = read_tsv(ASTRO_LOCI_IN)
    namespaces = read_tsv(NAMESPACES_IN)
    assert (len(prose_events), len(astro_groups), len(astro_loci), len(namespaces)) == (381, 395, 142, 13)

    prose_surface_readings: dict[str, set[str]] = defaultdict(set)
    for row in prose_events:
        prose_surface_readings[row["surface_display"]].add(row["closed_card_reading_de"])
    exact_astro_surfaces = {row["surface_display_only"] for row in astro_groups if row["surface_display_only"] in prose_surface_readings}
    assert all(len(prose_surface_readings[surface]) == 1 for surface in exact_astro_surfaces)
    exact_readings = {next(iter(prose_surface_readings[surface])) for surface in exact_astro_surfaces}
    assert exact_readings <= set(EXACT_ASTRO_ADAPT)

    component_rows: list[dict[str, str]] = []
    for component_id, (patterns, common, prose, astro) in COMPONENTS.items():
        component_rows.append({
            "component_id": component_id,
            "visible_patterns": ";".join(patterns),
            "common_operational_nucleus_de": common,
            "prose_register_expansion_de": prose,
            "astro_register_expansion_de": astro,
            "workshop_rule_de": "Gemeinsamen Kern behalten; der Bild- und Seitenregistertyp liefert die konkrete Expansion.",
        })

    bridged_groups: list[dict[str, str]] = []
    for row in astro_groups:
        surface = row["surface_display_only"]
        owner = owner_kind(row["local_content_class"])
        if surface in prose_surface_readings:
            prose_reading = next(iter(prose_surface_readings[surface]))
            bridge_class = "EXACT_PROSE_SURFACE_BRIDGE"
            matches: list[tuple[int, int, str, str, str]] = []
            residuals: list[str] = []
            component_ids = "EXACT:" + prose_reading
            component_values = EXACT_ASTRO_ADAPT[prose_reading]
            reading = f"{owner} {row['local_image_owner']}: {component_values}."
            matched_characters = len(surface)
        else:
            matches, residuals = component_matches(surface)
            if len(matches) >= 2:
                bridge_class = "COMPOSED_COMPONENT_BRIDGE"
            elif len(matches) == 1:
                bridge_class = "SINGLE_COMPONENT_BRIDGE"
            else:
                bridge_class = "LOCAL_ASTRO_NOMENCLATOR"
            component_ids = "|".join(match[3] for match in matches) if matches else "LOCAL_NAME_OR_VALUE"
            component_values = " + ".join(match[4] for match in matches) if matches else "gelerntes lokales Namen- oder Wertsegment"
            residual_note = f"; lokaler Namensrest {'/'.join(residuals)}" if residuals else ""
            reading = f"{owner} {row['local_image_owner']}: {component_values}{residual_note}."
            matched_characters = sum(match[1] - match[0] for match in matches)
        bridged_groups.append({
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "surface_display": surface,
            "namespace_id": row["canonical_namespace_id"],
            "local_image_owner": row["local_image_owner"],
            "local_content_class": row["local_content_class"],
            "bridge_class": bridge_class,
            "matched_component_ids": component_ids,
            "matched_component_values_de": component_values,
            "matched_character_fraction": f"{matched_characters}/{len(surface)}",
            "residual_local_segments": "/".join(residuals) if residuals else "NONE",
            "astro_working_reading_de": reading,
            "orientation_rule": "LOCAL_OWNER_ONLY__NO_START_OR_DIRECTION",
            "crosspage_rule": "NO_F68_F69_KEY__NO_IMPLICIT_NAMESPACE_JOIN",
        })

    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in bridged_groups:
        groups_by_locus[row["locus"]].append(row)
    locus_rows: list[dict[str, str]] = []
    for locus in astro_loci:
        groups = groups_by_locus[locus["locus"]]
        classes = Counter(row["bridge_class"] for row in groups)
        values = [row["matched_component_values_de"] for row in groups if row["bridge_class"] != "LOCAL_ASTRO_NOMENCLATOR"]
        owner = owner_kind(locus["local_content_class"])
        if values:
            complete = f"{owner} {locus['local_image_owner']}: notiere " + " | ".join(values)
            if classes["LOCAL_ASTRO_NOMENCLATOR"]:
                complete += f"; ergaenze {classes['LOCAL_ASTRO_NOMENCLATOR']} lokale Namen-/Wertsegmente aus dem Werkstattdeck"
            complete += "."
        else:
            complete = f"{owner} {locus['local_image_owner']}: kopiere die {len(groups)} lokalen Namen-/Wertsegmente als einen Eintrag."
        locus_rows.append({
            "page": locus["page"],
            "diagram_id": locus["diagram_id"],
            "locus": locus["locus"],
            "namespace_id": locus["local_namespace"],
            "local_image_owner": locus["local_image_owner"],
            "local_content_class": locus["local_content_class"],
            "group_count": str(len(groups)),
            "surface_sequence": " ".join(row["surface_display"] for row in groups),
            "bridge_class_sequence": " ".join(row["bridge_class"] for row in groups),
            "component_sequence": " || ".join(row["matched_component_ids"] for row in groups),
            "exact_surface_groups": str(classes["EXACT_PROSE_SURFACE_BRIDGE"]),
            "composed_component_groups": str(classes["COMPOSED_COMPONENT_BRIDGE"]),
            "single_component_groups": str(classes["SINGLE_COMPONENT_BRIDGE"]),
            "local_nomenclator_groups": str(classes["LOCAL_ASTRO_NOMENCLATOR"]),
            "complete_workshop_reading_de": complete,
            "owner_default_de": locus["silent_argument_default"],
            "orientation_status": "UNORDERED_LOCAL_ADDRESS__COPY_VISIBLE_POSITION",
        })

    unified_rows: list[dict[str, str]] = []
    for row in prose_events:
        unified_rows.append({
            "unified_serial": f"U{len(unified_rows)+1:03d}",
            "register": "PROSE_WORKSHOP",
            "page": row["page"],
            "locus": row["locus"],
            "namespace_or_record": row["record_unit_id"],
            "local_unit_id": row["event_id"],
            "surface_display": row["surface_display"],
            "mechanism": "PRODUCTIVE_COMPONENTS" if row["teaching_symbol"] == "P" else "WHOLE_CARD_CODEBOOK",
            "operational_reading_de": row["contextual_event_reading_de"],
            "local_owner": row["record_unit_id"],
            "register_rule_de": "Prosa: Besitzer erben, Karte komponieren oder im sechzehnkoepfigen Codebuch nachschlagen.",
        })
    for row in bridged_groups:
        unified_rows.append({
            "unified_serial": f"U{len(unified_rows)+1:03d}",
            "register": "ASTRO_DIAGRAM",
            "page": row["page"],
            "locus": row["locus"],
            "namespace_or_record": row["namespace_id"],
            "local_unit_id": row["opaque_local_id"],
            "surface_display": row["surface_display"],
            "mechanism": row["bridge_class"],
            "operational_reading_de": row["astro_working_reading_de"],
            "local_owner": row["local_image_owner"],
            "register_rule_de": "Diagramm: sichtbaren Besitzer adressieren, gemeinsame Operatoren lesen und lokalen Namen-/Wertrest kopieren.",
        })

    examples: list[dict[str, str]] = []
    for surface in EXAMPLE_SURFACES:
        selected = next((row for row in bridged_groups if row["surface_display"] == surface), None)
        if selected is None:
            continue
        examples.append({
            "surface": surface,
            "page": selected["page"],
            "locus": selected["locus"],
            "bridge_class": selected["bridge_class"],
            "matched_components": selected["matched_component_ids"],
            "astro_working_reading_de": selected["astro_working_reading_de"],
            "teaching_note_de": "Nicht als Sternname lesen; dies ist die Werkstattfunktion des sichtbaren Eintrags.",
        })

    class_counts = Counter(row["bridge_class"] for row in bridged_groups)
    manual_lines = [
        "# Gemeinsames Zehn-Seiten-Werkstatthandbuch",
        "",
        "## Prosa",
        "",
        "- 353 Ereignisse werden aus dem Komponenten- und Traegerkasten gebaut.",
        "- 28 Ereignisse kommen aus dem sechzehnkoepfigen Ganzkarten-Codebuch.",
        "- Bildbesitzer und laufender Posten liefern die stillen Gegenstaende.",
        "",
        "## Diagramme",
        "",
        f"- {class_counts['EXACT_PROSE_SURFACE_BRIDGE']} Gruppen wiederholen eine Prosakarten-Oberflaeche exakt.",
        f"- {class_counts['COMPOSED_COMPONENT_BRIDGE']} Gruppen tragen mindestens zwei gemeinsame Komponenten.",
        f"- {class_counts['SINGLE_COMPONENT_BRIDGE']} Gruppen tragen eine gemeinsame Komponente.",
        f"- {class_counts['LOCAL_ASTRO_NOMENCLATOR']} Gruppen sind lokale Namen-/Wertsegmente.",
        "",
        "Diagrammregel: kleinsten sichtbaren Besitzer und Namespace waehlen; gemeinsame Operatoren abstrakt lesen; lokalen Rest aus dem Exemplar kopieren; keinen Start, Drehsinn oder f68-f69-Schluessel erfinden.",
        "",
        "## Wichtigste Registerbruecken",
        "",
        "| Kern | gemeinsame Bedeutung | Prosa | Astro |",
        "|---|---|---|---|",
    ]
    for row in component_rows:
        manual_lines.append(f"| {row['visible_patterns']} | {row['common_operational_nucleus_de']} | {row['prose_register_expansion_de']} | {row['astro_register_expansion_de']} |")
    manual_lines.extend([
        "",
        "> Dasselbe Fachkuerzel darf je Register anders konkret werden: AIR ist LAUF, nicht notwendig immer Wasser; HO ist EINGANGSPOSTEN, nicht notwendig immer eine Pflanze; OR ist ARBEITSSATZ, nicht notwendig immer ein Sud.",
    ])

    write_tsv(COMPONENTS_OUT, component_rows)
    write_tsv(ASTRO_GROUPS_OUT, bridged_groups)
    write_tsv(ASTRO_LOCI_OUT, locus_rows)
    write_tsv(UNIFIED_OUT, unified_rows)
    write_tsv(EXAMPLES_OUT, examples)
    MANUAL_OUT.write_text("\n".join(manual_lines).rstrip() + "\n", encoding="utf-8")

    page_counts = Counter(row["page"] for row in bridged_groups)
    summary = {
        "status": "PASS",
        "shared_components": len(component_rows),
        "prose_events": len(prose_events),
        "astro_groups": len(bridged_groups),
        "astro_loci": len(locus_rows),
        "namespaces": len(namespaces),
        "unified_rows": len(unified_rows),
        "bridge_classes": dict(class_counts),
        "astro_page_counts": dict(page_counts),
        "files": {},
    }
    for path in [COMPONENTS_OUT, ASTRO_GROUPS_OUT, ASTRO_LOCI_OUT, UNIFIED_OUT, EXAMPLES_OUT, MANUAL_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
