#!/usr/bin/env python3
"""Build Pass 1019: four-image check of WERT / ANTEIL / EINHEIT."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth/PASS1018_627_REVISED_CORE_EDITION.tsv"

IMAGES = {
    "f13r": {
        "register": "HERBAL",
        "object": "1006098",
        "sha256": "454eb5f05db936ed0cf729c3881af0ded0993bc116246c6c8fd0c2789f4e9833",
        "structure": "eine ganze Pflanze mit großer Wurzelkrone, getrennten Blattgruppen und Blütenstand",
        "wert": "Arbeits- oder Auswahlwert; lokal kann das eine Menge sein, aber keine Skala ist gezeichnet",
        "anteil": "sichtbarer Pflanzenanteil oder Teilgruppe; im gewählten f13r-Textlauf ist AIN selbst nicht belegt",
        "einheit": "ein Pflanzen- oder Arbeitsblock; ein Gefäßansatz ist nicht sichtbar",
        "not_shown": "Messskala, Gefäß, Mischung, Flussrichtung",
        "verdict": "BREITE_KERNE_PASSEN__ANTEIL_AUF_DIESER_SEITE_NOCH_UNGETESTET",
    },
    "f75r": {
        "register": "BIOLOGICAL",
        "object": "1006208",
        "sha256": "6fd33917722a97ef0c93f905885963332645c1a1c81f60f03a165b12007a7fc3",
        "structure": "viele Figuren in mehreren lokalen grünen Becken-, Insel- und Stationsgruppen",
        "wert": "lokaler Stations-, Halte- oder Einstellwert; kein ablesbares Volumen",
        "anteil": "Teilposten, Figurenplatz oder Anteil innerhalb einer lokalen Gruppe",
        "einheit": "eine lokale Stations- oder Arbeitsgruppe; kein einheitlicher Seitenkreislauf",
        "not_shown": "Nummern, Mengenmaß, globale Reihenfolge, eindeutige Flussrichtung",
        "verdict": "BREITE_KERNE_PASSEN_BESSER_ALS_MASS_PORTION_ANSATZ",
    },
    "f67r2": {
        "register": "CELESTIAL",
        "object": "1006194",
        "sha256": "099ded767a3f8a3472e675dcaa2b609ab2d6842d62813a94159fc1dc20f023f3",
        "structure": "zwei getrennte Himmelsräder mit radialen Sektoren, Ringen, Gestirnen und Einträgen",
        "wert": "Ring-, Tabellen- oder Positionswert",
        "anteil": "Sektor-, Ring- oder Eintragsanteil",
        "einheit": "ein Rad-, Sektor- oder Eintragsblock; keine Stoffzubereitung",
        "not_shown": "verbindender Schlüssel, Startpunkt, Drehrichtung, physisches Maß",
        "verdict": "BREITE_KERNE_SIND_FUER_DAS_HIMMELSREGISTER_NOTWENDIG",
    },
    "f88r": {
        "register": "PHARMA",
        "object": "1037112",
        "sha256": "a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013",
        "structure": "drei Gefäße und drei Reihen gezeichneter Wurzel-, Blatt-, Frucht- und Kronenposten",
        "wert": "Mengen-, Auswahl- oder Listenwert eines bezeichneten Postens",
        "anteil": "ein Zutatenposten oder Anteil davon",
        "einheit": "eine Zutaten-, Gefäß- oder Arbeitsgruppe; ein Ansatz ist möglich, aber nicht erzwungen",
        "not_shown": "Messskala, sichere Zuordnung jeder Textgruppe zu einem Gefäß, genaue Rezeptfolge",
        "verdict": "BREITE_KERNE_TRAGEN__ENGE_REZEPTWERTE_NUR_LOKAL",
    },
}

CHOICES = {
    "P1009-S005": (
        "WERT+EINHEIT",
        "Am gezeigten Pflanzenbesitzer Teilgruppen wählen, den zugehörigen Wert halten, die laufende Einheit weitergeben und schließen.",
        "PLAUSIBEL",
    ),
    "P1009-S006": (
        "WERT+EINHEIT",
        "Den nächsten Pflanzenposten auf den angegebenen Wert einstellen, in derselben Einheit setzen und fortführen; schließen.",
        "PLAUSIBEL",
    ),
    "P1009-S009": (
        "EINHEIT",
        "Den sichtbaren Pflanzenteil wählen und in die laufende Einheit setzen; offen weiterführen.",
        "STARK",
    ),
    "P1009-S075": (
        "ANTEIL+EINHEIT",
        "An der oberen Figuren- und Stationsgruppe einen Anteil setzen, länger halten, innerhalb derselben lokalen Einheit weitergeben und schließen.",
        "PLAUSIBEL",
    ),
    "P1009-S100": (
        "WERT+ANTEIL+EINHEIT",
        "In der lokalen Stationsgruppe einen Anteil nach dem angegebenen Wert setzen, umsetzen und halten; die Einheit schließen.",
        "STARK",
    ),
    "P1009-S179": (
        "WERT",
        "Den lokalen Posten auf den bezeichneten Wert setzen und den kurzen Stationsgang schließen.",
        "PLAUSIBEL",
    ),
    "P1009-S031": (
        "ANTEIL",
        "Im linken Himmelsrad einen Sektoranteil einsetzen, auswählen und zum bezeichneten Ort weiterführen; schließen.",
        "STARK",
    ),
    "P1009-S032": (
        "WERT+ANTEIL+EINHEIT",
        "Im bezeichneten Rad einen Anteil nach seinem Wert auswählen, in die zugehörige Eintragseinheit setzen und bis zur sichtbaren Grenze führen.",
        "STARK",
    ),
    "P1009-S033": (
        "WERT+ANTEIL+EINHEIT",
        "Einen weiteren Radanteil nach seinem Wert nehmen, markieren und als eigene Eintragseinheit weiterführen.",
        "PLAUSIBEL",
    ),
    "P1009-S590": (
        "WERT+ANTEIL+EINHEIT",
        "Aus der bezeichneten Zutatenreihe einen Anteil wählen, seinen Wert setzen und ihn innerhalb der zugehörigen Gefäß- oder Arbeitsgruppe weiterführen.",
        "STARK",
    ),
    "P1009-S592": (
        "WERT+EINHEIT",
        "Den bezeichneten Zutatenposten nach seinem Wert auswählen und in derselben Arbeits- oder Gefäßeinheit fortsetzen.",
        "PLAUSIBEL",
    ),
    "P1009-S594": (
        "WERT+EINHEIT",
        "Weitere Zutatenposten nach ihrem Wert setzen, nehmen und innerhalb der laufenden Einheit offen weiterführen.",
        "PLAUSIBEL",
    ),
}


def read_source() -> dict[str, dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        return {row["statement_id"]: row for row in csv.DictReader(fh, delimiter="\t")}


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_source()
    rows = []
    for number, (statement_id, (roots, reading, judgment)) in enumerate(CHOICES.items(), 1):
        src = source[statement_id]
        page = src["physical_page"]
        image = IMAGES[page]
        rows.append({
            "audit_id": f"P1019-{number:02d}",
            "page": page,
            "register": image["register"],
            "image_object_id": image["object"],
            "image_sha256": image["sha256"],
            "statement_id": statement_id,
            "visible_structure_de": image["structure"],
            "surface_sequence": src["surface_sequence"],
            "component_sequence": src["component_sequence"],
            "portable_roots_present": roots,
            "old_narrow_values_replaced": "MASS->WERT;PORTION->ANTEIL;ANSATZ->EINHEIT",
            "manual_image_owned_reading_de": reading,
            "visual_fit": judgment,
            "image_does_not_show_de": image["not_shown"],
            "decision": "KEEP_WERT_ANTEIL_EINHEIT_WITH_REGISTER_LOCAL_EXPANSION",
        })

    write_tsv(
        OUT / "PASS1019_12_VISUAL_CORE_CONTEXTS.tsv",
        list(rows[0]),
        rows,
    )

    page_rows = []
    for page, image in IMAGES.items():
        page_rows.append({
            "page": page,
            "register": image["register"],
            "image_object_id": image["object"],
            "image_sha256": image["sha256"],
            "visible_structure_de": image["structure"],
            "AIIN_WERT_local_expansion_de": image["wert"],
            "AIN_ANTEIL_local_expansion_de": image["anteil"],
            "OR_EINHEIT_local_expansion_de": image["einheit"],
            "image_does_not_show_de": image["not_shown"],
            "verdict": image["verdict"],
        })
    write_tsv(OUT / "PASS1019_FOUR_IMAGE_CORE_TABLE.tsv", list(page_rows[0]), page_rows)

    summary = {
        "result": "WERT_ANTEIL_EINHEIT_SURVIVE_FOUR_REGISTER_IMAGE_CHECK",
        "pages": len(IMAGES),
        "contexts": len(rows),
        "strong": sum(r["visual_fit"] == "STARK" for r in rows),
        "plausible": sum(r["visual_fit"] == "PLAUSIBEL" for r in rows),
        "image_contradictions": 0,
        "new_roots": 0,
        "important_gap": "AIN is not present in the selected f13r statement run",
    }
    (OUT / "PASS1019_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
