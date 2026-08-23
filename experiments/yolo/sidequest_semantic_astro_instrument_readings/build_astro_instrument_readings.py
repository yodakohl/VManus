#!/usr/bin/env python3
"""Turn the 142 closed Astro loci into three usable workshop instruments."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_astro_nomenclator_closure"

LOCI_IN = SOURCE / "ASTRO_142_NOMENCLATOR_CLOSED_LOCI.tsv"
GROUPS_IN = SOURCE / "ASTRO_395_NOMENCLATOR_CLOSED.tsv"
UNIFIED_IN = SOURCE / "TEN_PAGE_776_NOMENCLATOR_CLOSED.tsv"

INSTRUMENTS_OUT = HERE / "THREE_ASTRO_INSTRUMENTS.tsv"
MODULES_OUT = HERE / "FOURTEEN_INSTRUMENT_MODULES.tsv"
LOCI_OUT = HERE / "ASTRO_142_OPERATIONAL_LOCI.tsv"
UNIFIED_OUT = HERE / "TEN_PAGE_776_INSTRUMENT_CONTEXT.tsv"
READINGS_OUT = HERE / "THREE_COMPLETE_INSTRUMENT_READINGS.md"
MANUAL_OUT = HERE / "INSTRUMENT_APPRENTICE_MANUAL.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"


INSTRUMENTS = {
    "I67_TWO_WHEEL_COMPARATOR": {
        "page": "f67r2",
        "title": "Doppelrad für Platz–Aspekt–Bedingungs-Vergleich",
        "input": "sichtbarer Sektor, Sternplatz oder Phasenplatz plus Ausgangs- und Zielbezug",
        "operation": "rechts Klasse oder Bedingung wählen; links Platz, Aspekt, Sollwert und Übertragung eintragen",
        "output": "lokalen Vergleichs-, Grad- oder Ablesewert am gewählten Platz erhalten",
        "practical": "Himmels- oder Kalenderbedingungen für einen geplanten Arbeitsgang vergleichen",
        "medical": "einen Zeitpunkt oder Zustand für Bad, Anwendung oder Zubereitung nachschlagen",
        "narrative": "Das rechte Rad stellt die Bedingung ein; das linke Rad verknüpft Sternplatz, Ausgang, Ziel, Aspekt und Sollwert. Die äußeren Plätze liefern Übertragungs- oder Zielhinweise, die Ringtexte den Bedienrahmen.",
    },
    "I68_STAR_CLASS_ATLAS": {
        "page": "f68r1",
        "title": "Mehrpaneel-Atlas für Sternklasse und Ablesung",
        "input": "sichtbarer Stern- oder Asterismenplatz in einem lokalen Paneel",
        "operation": "Paneelmodus wählen; den Sternplatz adressieren; Klasse, Zustand, Ziel oder Übertragung lesen",
        "output": "lokalen Sternklassen-, Bedingungs- oder Ablesewert erhalten",
        "practical": "Sternplätze nach Arbeitsklasse, Zustand oder Zielbezug nachschlagen",
        "medical": "einen Himmelsplatz als günstige, ungünstige oder graduierte Bedingung für eine Anwendung lesen",
        "narrative": "Die drei Paneelköpfe sind verschiedene Abfragemodi. Die 28 Sternplätze sind einzelne Adressen, keine erzwungene Runde. Zentrum und Legende setzen Ziel und Grundgrad.",
    },
    "I69_THREE_WHEEL_REGISTER": {
        "page": "f69v",
        "title": "Dreirad-Register für Platz, Qualität und Lichtzustand",
        "input": "einer von 28 linken Plätzen oder eine lokale Wetter-/Lichtfrage",
        "operation": "das passende Rad als eigenes Modul wählen und dort Platz, Qualität, Zustand, Quelle oder Ziel lesen",
        "output": "Platzklasse, Qualitätsablesung oder Licht-/Komplexionsbedingung erhalten",
        "practical": "Arbeitsplatz, Himmelsqualität oder Lichtbedingung getrennt nachschlagen",
        "medical": "Platzwahl, Wetterqualität und Licht-/Komplexionsbedingung als drei Hilfen für eine Wahl verwenden",
        "narrative": "Das linke Rad besitzt die lokale 28-Platz-Liste. Das mittlere Rad liest Qualität oder Wetterlage, das rechte Licht- oder Komplexionszustand. Es sind drei benachbarte Werkzeuge, keine zwangsläufige Sequenz.",
    },
}


MODULES = {
    "M67_RIGHT_SECTORS": ("I67_TWO_WHEEL_COMPARATOR", "Rechte Sektoren", "Bedingung, Klasse oder Ausgang einstellen", "Wähle den sichtbaren rechten Sektor und setze seine Klasse oder Bedingung"),
    "M67_RIGHT_RING_RULES": ("I67_TWO_WHEEL_COMPARATOR", "Rechte Ringregeln", "Grad, Fortsetzung und Ablesung des rechten Rades", "Lies die rechte Ringregel als Bedienrahmen"),
    "M67_RIGHT_PHASES": ("I67_TWO_WHEEL_COMPARATOR", "Rechte Phasenplätze", "Licht-, Phasen- oder Kalenderbedingung", "Wähle die sichtbare Phasenstelle und notiere ihre Bedingung"),
    "M67_LEFT_ASPECT_FIELDS": ("I67_TWO_WHEEL_COMPARATOR", "Linke Aspektfelder", "Platz, Aspekt, Sollwert, Ausgang und Ziel kombinieren", "Trage am sichtbaren Sternfeld Platz, Aspekt und Wertbezug ein"),
    "M67_LEFT_OUTER_STATIONS": ("I67_TWO_WHEEL_COMPARATOR", "Äußere linke Sternplätze", "Quelle, Ziel, Übertragung oder Folge auswählen", "Nimm den sichtbaren äußeren Sternplatz als Übertragungs- oder Zielhinweis"),
    "M67_LEFT_RING_RULE": ("I67_TWO_WHEEL_COMPARATOR", "Linke Ringregel", "Sollwert-, Lauf- und Klassenrahmen des linken Rades", "Lies den linken Ringtext als Einstellregel"),
    "M67_SHARED_LEGEND": ("I67_TWO_WHEEL_COMPARATOR", "Gemeinsame Legende", "gemeinsame Ablese- und Einstellbegriffe", "Lies die Legende als gemeinsamen Kartenschlüssel, ohne sie einem Einzelrad aufzuzwingen"),
    "M68_PANEL_HEADERS": ("I68_STAR_CLASS_ATLAS", "Paneelköpfe", "Abfragemodus für Eingang, Phase, Ziel oder Ablesung", "Wähle den sichtbaren Paneelkopf als Modus"),
    "M68_STAR_STATIONS": ("I68_STAR_CLASS_ATLAS", "28 Sternstationen", "lokale Sternklasse, Bedingung, Übertragung oder Zielangabe", "Wähle den sichtbaren Sternplatz und lies seine lokale Funktion"),
    "M68_CENTER_KEY": ("I68_STAR_CLASS_ATLAS", "Zentrum und Legende", "Zielsetzung und Grundgrad", "Nutze Zentrum oder Legende als lokalen Ziel- und Gradschlüssel"),
    "M69_LEFT_RUBRIC": ("I69_THREE_WHEEL_REGISTER", "Linke Ringrubrik", "Arbeitsregel des 28-Platz-Rades", "Lies die linke Ringrubrik als Bedienregel für das 28-Platz-Inventar"),
    "M69_LEFT_28_SLOTS": ("I69_THREE_WHEEL_REGISTER", "28 linke Radialplätze", "einzelne Platz-, Klassen-, Grad- oder Zielwerte", "Wähle genau den sichtbaren Radialplatz und lies seinen Wert"),
    "M69_MIDDLE_QUALITY": ("I69_THREE_WHEEL_REGISTER", "Mittleres Qualitätsrad", "Wetter-, Qualitäts- oder Zustandsablesung", "Lies das mittlere Rad als eigene Qualitäts- oder Wettertafel"),
    "M69_RIGHT_LIGHT": ("I69_THREE_WHEEL_REGISTER", "Rechtes Lichtrad", "Licht-, Planeten- oder Komplexionsbedingung", "Lies das rechte Rad als eigene Licht- oder Zustandsregel"),
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


def module_for(page: str, owner: str) -> str:
    if page == "f67r2":
        if "RIGHT_SECTOR_SLOT" in owner:
            return "M67_RIGHT_SECTORS"
        if "RIGHT_RING_BAND" in owner or "RIGHT_OUTER_RING_TEXT" in owner:
            return "M67_RIGHT_RING_RULES"
        if "RIGHT_PHASE_STATION" in owner:
            return "M67_RIGHT_PHASES"
        if "LEFT_LOCAL_FIELD" in owner:
            return "M67_LEFT_ASPECT_FIELDS"
        if "LEFT_OUTER_STAR_STATION" in owner:
            return "M67_LEFT_OUTER_STATIONS"
        if "LEFT_OUTER_RING_TEXT" in owner:
            return "M67_LEFT_RING_RULE"
        if "PAIRED_WHEEL_LEGEND" in owner:
            return "M67_SHARED_LEGEND"
    if page == "f68r1":
        if "PANEL_HEADER" in owner or "HEADER_FRAGMENT" in owner:
            return "M68_PANEL_HEADERS"
        if "STAR_STATION" in owner:
            return "M68_STAR_STATIONS"
        if "CENTRE_KEY" in owner or "CENTRAL_LEGEND" in owner:
            return "M68_CENTER_KEY"
    if page == "f69v":
        if owner == "A3_LEFT_WHEEL_RING_TEXT":
            return "M69_LEFT_RUBRIC"
        if "LEFT_RADIAL_SLOT" in owner:
            return "M69_LEFT_28_SLOTS"
        if owner == "A3_MIDDLE_WHEEL_RING_TEXT":
            return "M69_MIDDLE_QUALITY"
        if owner == "A3_RIGHT_WHEEL_RING_TEXT":
            return "M69_RIGHT_LIGHT"
    raise ValueError(f"unmapped owner: {page} {owner}")


def operator_class(sequence: str) -> str:
    value = sequence.lower()
    tests = [
        ("ASPECT", ["aspekt"]),
        ("READOUT", ["ablese", "abgeles", "freigegeben"]),
        ("CLASS", ["klasse", "haus", "qualität"]),
        ("CONDITION", ["bedingung", "zustand", "lichtwert"]),
        ("INDEX", ["index"]),
        ("TRANSFER", ["ziel", "ausgang", "quelle", "übertragen", "uebertragen"]),
        ("VALUE", ["sollwert", "grad", "stufe", "hauptwert", "nebenwert"]),
        ("PROCESS", ["setzen", "bearbeiten", "fortsetzen", "anwenden"]),
    ]
    for label, needles in tests:
        if any(needle in value for needle in needles):
            return label
    return "LOCAL_ENTRY"


def build() -> dict[str, object]:
    loci = read_tsv(LOCI_IN)
    groups = read_tsv(GROUPS_IN)
    unified = read_tsv(UNIFIED_IN)
    assert (len(loci), len(groups), len(unified)) == (142, 395, 776)

    operational_loci = []
    module_counts: Counter[str] = Counter()
    module_groups: Counter[str] = Counter()
    module_classes: dict[str, set[str]] = defaultdict(set)
    for row in loci:
        module_id = module_for(row["page"], row["local_image_owner"])
        instrument_id, module_title, module_role, instruction = MODULES[module_id]
        sequence = row["compact_default_sequence_de"]
        imperative = f"{instruction}: {sequence}."
        operational_loci.append({
            "instrument_id": instrument_id,
            "module_id": module_id,
            "page": row["page"],
            "locus": row["locus"],
            "local_image_owner": row["local_image_owner"],
            "local_content_class": row["local_content_class"],
            "surface_sequence": row["surface_sequence"],
            "group_count": row["group_count"],
            "compact_default_sequence_de": sequence,
            "operator_class": operator_class(sequence),
            "module_role_de": module_role,
            "selection_rule": "SELECT_VISIBLE_OWNER__NO_CYCLIC_ORDER",
            "imperative_reading_de": imperative,
            "fluent_workshop_reading_de": f"{module_title}, {row['local_image_owner']}: {sequence}.",
            "orientation_status": row["orientation_status"],
        })
        module_counts[module_id] += 1
        module_groups[module_id] += int(row["group_count"])
        module_classes[module_id].add(row["local_content_class"])

    module_rows = []
    for module_id, (instrument_id, title, role, instruction) in MODULES.items():
        module_rows.append({
            "module_id": module_id,
            "instrument_id": instrument_id,
            "page": INSTRUMENTS[instrument_id]["page"],
            "module_title_de": title,
            "module_role_de": role,
            "apprentice_instruction_de": instruction,
            "locus_count": str(module_counts[module_id]),
            "group_count": str(module_groups[module_id]),
            "content_classes": ";".join(sorted(module_classes[module_id])),
            "order_rule": "OWNER_SELECTED__NOT_CYCLICALLY_ORDERED",
        })

    instrument_counts = Counter(row["instrument_id"] for row in operational_loci)
    instrument_groups = Counter()
    for row in operational_loci:
        instrument_groups[row["instrument_id"]] += int(row["group_count"])
    instrument_rows = []
    for instrument_id, spec in INSTRUMENTS.items():
        instrument_rows.append({
            "instrument_id": instrument_id,
            "page": spec["page"],
            "workshop_title_de": spec["title"],
            "input_de": spec["input"],
            "operation_de": spec["operation"],
            "output_de": spec["output"],
            "practical_expansion_de": spec["practical"],
            "iatromedical_expansion_de": spec["medical"],
            "continuous_working_reading_de": spec["narrative"],
            "selection_rule": "CHOOSE_VISIBLE_OWNER__NO_START_OR_DIRECTION",
            "crosspage_rule": "NO_REQUIRED_CROSSPAGE_KEY",
            "locus_count": str(instrument_counts[instrument_id]),
            "group_count": str(instrument_groups[instrument_id]),
        })

    locus_context = {(row["page"], row["locus"]): row for row in operational_loci}
    contextual_unified = []
    for row in unified:
        out = dict(row)
        if row["register"] == "ASTRO_DIAGRAM":
            context = locus_context[(row["page"], row["locus"])]
            out["instrument_id"] = context["instrument_id"]
            out["module_id"] = context["module_id"]
            out["instrument_context_de"] = f"{context['module_role_de']}: {row['operational_reading_de']}"
        else:
            out["instrument_id"] = "PROSE_NOT_APPLICABLE"
            out["module_id"] = "PROSE_NOT_APPLICABLE"
            out["instrument_context_de"] = row["operational_reading_de"]
        contextual_unified.append(out)

    reading_lines = [
        "# Drei vollständige Astro-Arbeitsinstrumente",
        "",
        "Dies ist die flüssige Werkstattfassung der 142 lokalen Diagrammorte. Ein Platz wird durch seine sichtbare Lage gewählt; die Auflistung behauptet keine Kreisrichtung.",
    ]
    for instrument_id, spec in INSTRUMENTS.items():
        reading_lines.extend([
            "",
            f"## {spec['page']} — {spec['title']}",
            "",
            spec["narrative"],
            "",
            f"Praktische Lesung: {spec['practical']}.",
            f"Iatromedizinische Lesung: {spec['medical']}.",
        ])
        page_modules = [module_id for module_id, values in MODULES.items() if values[0] == instrument_id]
        for module_id in page_modules:
            _iid, title, role, instruction = MODULES[module_id]
            reading_lines.extend(["", f"### {title}", "", f"{role}. {instruction}."])
            for row in operational_loci:
                if row["module_id"] == module_id:
                    reading_lines.append(f"- `{row['locus']}` / `{row['surface_sequence']}` — {row['imperative_reading_de']}")

    manual_lines = [
        "# Lehrlingsmanual für die drei Kreisinstrumente",
        "",
        "1. Bestimme zuerst die Seite und das lokale Rad oder Paneel.",
        "2. Wähle den sichtbaren Besitzer; suche keinen allgemeinen Startpunkt.",
        "3. Lies `AL` als Ziel, `AR` als Ausgang, `AIIN` als Vorgabewert und `AIR` als Lauf.",
        "4. Lies `TO/TE` als Platz oder Phase und `AM` als Aspektwert.",
        "5. Lies `K/KE/KA` als Klasse, Haus oder Qualität.",
        "6. Lies `CHEO/CHEY` als Ablesung, `CTH` als Bedingung und `IIR` als Index.",
        "7. Nutze `Y/O/A/E/S/D` als aktuelle, Grund-, Haupt-, Auswahl-, Neben- und Festwertachse.",
        "8. Auf f67 stellt das rechte Rad die Bedingung ein; das linke vergleicht Platz, Aspekt und Wert.",
        "9. Auf f68 wählt der Paneelkopf den Abfragemodus; der Sternplatz liefert die lokale Adresse.",
        "10. Auf f69 benutzt du linkes Platzrad, mittleres Qualitätsrad und rechtes Lichtrad als getrennte Module.",
        "11. Kopiere lokale sichtbare Adressen, aber erfinde keine Kreisrichtung oder verdeckte Nummerierung.",
        "12. Verbinde die drei Seiten nur thematisch; kein Schlüssel zwischen ihnen ist für die Bedienung nötig.",
    ]

    write_tsv(INSTRUMENTS_OUT, instrument_rows)
    write_tsv(MODULES_OUT, module_rows)
    write_tsv(LOCI_OUT, operational_loci)
    write_tsv(UNIFIED_OUT, contextual_unified)
    READINGS_OUT.write_text("\n".join(reading_lines) + "\n", encoding="utf-8")
    MANUAL_OUT.write_text("\n".join(manual_lines) + "\n", encoding="utf-8")

    outputs = [INSTRUMENTS_OUT, MODULES_OUT, LOCI_OUT, UNIFIED_OUT, READINGS_OUT, MANUAL_OUT]
    summary = {
        "status": "PASS",
        "instruments": len(instrument_rows),
        "modules": len(module_rows),
        "astro_loci": len(operational_loci),
        "astro_groups": sum(int(row["group_count"]) for row in operational_loci),
        "unified_rows": len(contextual_unified),
        "instrument_loci": dict(sorted(instrument_counts.items())),
        "module_loci": dict(sorted(module_counts.items())),
        "files": {path.name: {"sha256": sha256(path), "bytes": path.stat().st_size} for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
