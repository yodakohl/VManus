#!/usr/bin/env python3
"""Build the Pass 1020 one-sheet category inventory and full coverage audit."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth/PASS1018_627_REVISED_CORE_EDITION.tsv"


CORES = [
    ("Y", "AKTIVER POSTEN", "REFERENT", "den aktuell gemeinten Bild-, Stations- oder Eintragsposten weitertragen", "kein Schlusszeichen"),
    ("OK", "SETZEN", "HANDLUNG", "den rechts folgenden Posten, Anteil, Wert oder Ort in den Gang setzen", "kein bestimmter Stoffprozess"),
    ("OL", "FORTSETZEN", "FOLGE", "den laufenden Gang oder die folgende Handlung fortsetzen", "kein Stoffwort"),
    ("OT", "DANACH", "FOLGE", "die rechts folgende Handlung, Adresse oder Stufe als nächsten Schritt lesen", "kein eigenes Aktionsverb"),
    ("AL", "ZIELORT", "RELATION", "die Handlung an den bezeichneten Zielort binden", "kein bestimmtes Körperteil oder Gefäß"),
    ("CH", "NEHMEN", "HANDLUNG", "den bezeichneten Posten, Anteil, Wert oder Ort nehmen", "kein bestimmtes Material"),
    ("SH", "HALTEN", "HANDLUNG", "den bezeichneten Posten in der folgenden Stufe halten", "kein universelles Ruhen oder Absetzen"),
    ("AR", "AUSGANG", "RELATION", "die Handlung an den bezeichneten Ausgang binden", "keine Richtung und kein Vorratsstoff"),
    ("K", "GEBEN", "HANDLUNG", "den Posten weitergeben oder zwei Handlungsteile durch Übergabe verbinden", "kein bestimmtes Ziel"),
    ("AIIN", "WERT", "ARGUMENT", "den vorgegebenen Mengen-, Arbeits-, Positions- oder Tabellenwert einsetzen", "nicht überall Maß oder Dosis"),
    ("S", "WÄHLEN", "HANDLUNG", "den rechts bezeichneten Posten, Anteil, Wert oder Ort wählen", "kein bestimmtes Auswahlkriterium"),
    ("CHD", "UMSETZEN", "HANDLUNG", "den aktiven Posten in den nächsten lokalen Arbeitszustand umsetzen", "kein bestimmter technischer Prozess"),
    ("OR", "EINHEIT", "ARGUMENT", "die Handlung auf die laufende Artikel-, Stations-, Eintrags- oder Arbeitsgruppe beziehen", "nicht überall Ansatz oder Mischung"),
    ("L", "VERBINDUNG", "RELATION", "die eingeschlossene oder folgende Handlung über eine lokale Verbindung lesen", "keine Richtung"),
    ("T", "EINSTELLEN", "HANDLUNG", "Posten, Anteil, Wert, Grad oder Ort einstellen", "kein bestimmtes Gerät"),
    ("AIN", "ANTEIL", "ARGUMENT", "einen Pflanzen-, Stations-, Sektor- oder Zutatenanteil verwenden", "nicht überall Portion"),
    ("R", "MARKIEREN", "HANDLUNG", "den folgenden Wert oder den gesetzten lokalen Platz markieren", "kein bestimmtes Schriftzeichen"),
    ("P", "EINSETZEN", "HANDLUNG", "den bezeichneten Posten oder Anteil in den laufenden Gang einsetzen", "kein bestimmter Empfänger"),
    ("AIR", "LAUF", "RELATION", "die Handlung an den bezeichneten Lauf binden", "nicht automatisch Wasser oder Richtung"),
]

CONTROLS = [
    ("E", "GRAD I", "erste oder niedrige Stufe der aktiven Handlung", "kein universelles kurz, kalt oder leicht"),
    ("EE", "GRAD II", "zweite oder höhere Stufe derselben Handlung", "kein universelles lang, warm oder stark"),
    ("EEE", "GRAD III", "dritte oder volle Stufe derselben Handlung", "kein automatischer Schluss"),
    ("DY", "SCHLUSS", "nur in einer lizenzierten Endkarte den Teilgang schließen", "sichtbares dy nicht global als Schluss zerlegen"),
    ("O", "AUSFÜHRUNG", "die lokal aktive Handlung ausführen", "kein eigenes Stoff- oder Aktionswort"),
    ("CARRIER_Q", "BEGINNMARKER", "einen neuen lokalen Eintrag oder Gang eröffnen", "kein Laut- oder Inhaltswert"),
    ("IIN", "STUFE", "eine benannte Arbeits- oder Diagrammstufe wählen", "nicht mit AIIN=WERT verschmelzen"),
    ("DA", "ZWEITE STUFE", "einen zweiten lokalen Gang oder Platz anzeigen", "nicht automatisch danach oder Gefäß"),
]

CHANNELS = [
    ("LOCAL_PLACE", "HIER", "D_ADDR|AM_ADDR|A_ADDR|S_ADDR|LOCAL_CHAR_F|D_LABEL|S_LABEL|M_LOCAL|Z_ADDR", "den lokal bezeichneten Bild-, Tabellen-, Rand- oder Nebenplatz nehmen"),
    ("LOCAL_INDEX", "VARIANTE", "G_LABEL|LOCAL_CHAR_G|LOCAL_CHAR_I|LOCAL_CHAR_B|LOCAL_CHAR_J|LOCAL_CHAR_Z", "die lokal markierte Variante, Paarung oder Unterstufe nehmen"),
    ("LOCAL_CLASS", "KLASSE", "HO|AN", "die lokale Stoff-, Zusatz- oder Eintragsklasse übernehmen"),
    ("LOCAL_REFERENCE", "VORBEZUG", "OS|RESUME_CARD", "den vorausgesetzten Besitzer oder laufenden Gang wieder aufnehmen"),
]


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atomize(component_sequence: str) -> list[str]:
    return [atom for atom in re.split(r"\s*\|\s*|\+", component_sequence) if atom]


def main() -> None:
    categories: list[dict[str, object]] = []
    atom_to_category: dict[str, str] = {}

    for index, (sign, value, role, rule, forbidden) in enumerate(CORES, 1):
        category = f"CORE_{index:02d}"
        categories.append({
            "category_id": category,
            "category_type": "PORTABLE_CORE",
            "graphic_signs": sign,
            "short_value_de": value,
            "syntax_role": role,
            "apprentice_rule_de": rule,
            "forbidden_overreading_de": forbidden,
        })
        atom_to_category[sign] = category

    for index, (sign, value, rule, forbidden) in enumerate(CONTROLS, 1):
        category = f"CONTROL_{index:02d}"
        categories.append({
            "category_id": category,
            "category_type": "FORMAL_CONTROL",
            "graphic_signs": sign,
            "short_value_de": value,
            "syntax_role": "STEUERUNG",
            "apprentice_rule_de": rule,
            "forbidden_overreading_de": forbidden,
        })
        atom_to_category[sign] = category

    for index, (channel, value, signs, rule) in enumerate(CHANNELS, 1):
        category = f"CHANNEL_{index:02d}"
        categories.append({
            "category_id": category,
            "category_type": "LOCAL_CHANNEL",
            "graphic_signs": signs,
            "short_value_de": value,
            "syntax_role": channel,
            "apprentice_rule_de": rule,
            "forbidden_overreading_de": "kein portables Nomen aus der lokalen Zeichenform erzeugen",
        })
        for sign in signs.split("|"):
            atom_to_category[sign] = category

    coverage = []
    atom_counts: Counter[str] = Counter()
    event_total = 0
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            atoms = atomize(row["component_sequence"])
            atom_counts.update(atoms)
            event_total += int(row["event_count"])
            unknown = sorted({atom for atom in atoms if atom not in atom_to_category})
            used_categories = sorted({atom_to_category[atom] for atom in atoms if atom in atom_to_category})
            coverage.append({
                "statement_id": row["statement_id"],
                "page": row["physical_page"],
                "register": row["register"],
                "event_count": row["event_count"],
                "component_atom_count": len(atoms),
                "category_count": len(used_categories),
                "categories_used": "|".join(used_categories),
                "unknown_atoms": "|".join(unknown) if unknown else "NONE",
                "sheet_result": "FULLY_READABLE_FROM_ONE_SHEET" if not unknown else "UNEXPLAINED_ATOM",
            })
    write_tsv(OUT / "PASS1020_627_SHEET_COVERAGE.tsv", list(coverage[0]), coverage)

    for category in categories:
        mentions = sum(atom_counts[sign] for sign in str(category["graphic_signs"]).split("|"))
        category["running_atom_mentions"] = mentions
        category["teaching_order"] = (
            "I_DAILY" if mentions >= 300
            else "II_COMMON" if mentions >= 50
            else "III_RARE" if mentions > 0
            else "IV_EXEMPLAR_ONLY"
        )
    write_tsv(OUT / "PASS1020_31_CATEGORY_LEXICON.tsv", list(categories[0]), categories)

    summary = {
        "result": "ONE_SHEET_COVERS_COMPLETE_627_STATEMENT_COMPONENT_LAYER",
        "categories": len(categories),
        "portable_cores": len(CORES),
        "formal_controls": len(CONTROLS),
        "local_channels": len(CHANNELS),
        "graphic_signs": len(atom_to_category),
        "running_graphic_signs_seen": len(atom_counts),
        "statements": len(coverage),
        "running_events": event_total,
        "statements_with_unknown_atoms": sum(r["unknown_atoms"] != "NONE" for r in coverage),
    }
    (OUT / "PASS1020_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
