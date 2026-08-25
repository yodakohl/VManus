#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ATOMS = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_56_CURRENT_ATOMIC_LEXICON.tsv"
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_79_LEARNED_CARD_FAMILIES.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_2511_LONG_FORMULA_EDITION.tsv"

LEMMAS = {
    "Y": "DIES", "OK": "ANSETZEN", "E": "KURZ", "DY": "SCHLIESSEN", "O": "AUSFÜHREN", "OL": "FORTSETZEN",
    "EE": "LÄNGER", "OT": "DANACH", "AL": "ZIEL", "CH": "ENTNEHMEN", "D_ADDR": "TEIL", "SH": "HALTEN",
    "AR": "QUELLE", "K": "ZUGEBEN", "AIIN": "SOLLMASS", "S": "AUSWÄHLEN", "CHD": "UMSETZEN", "OR": "ANSATZ",
    "L": "LEITEN", "T": "EINSTELLEN", "AIN": "PORTION", "R": "MARKIEREN", "P": "EINSETZEN", "CTH": "BEREIT",
    "SHED": "ABSETZEN", "CKH": "DURCHLASS", "AM_ADDR": "INNEN", "CHEO": "AUSZUG", "DA": "ZWEIT",
    "CARRIER_Q": "BEGINNEN", "A_ADDR": "ORT", "AIR": "LAUF", "CHK": "BEHANDELN", "IIN": "STUFE",
    "S_ADDR": "STERNORT", "SOLK": "AUFFANGEN", "EEE": "VOLL", "LSH": "SPÜLEN", "LOCAL_CHAR_F": "NEBENWEG",
    "CPH": "UMLEITEN", "HO": "TEILSTOFF", "AN": "ZUSATZ", "G_LABEL": "PRÜFEN", "CFH": "TRENNEN",
    "LOCAL_CHAR_G": "EINMAL", "LOCAL_CHAR_I": "UNTERSTUFE", "OS": "DAZU", "D_LABEL": "RAND",
    "S_LABEL": "RAHMEN", "LOCAL_CHAR_B": "PAAR", "M_LOCAL": "MITTE", "Z_ADDR": "AUSSEN", "LD": "BEFESTIGEN",
    "LOCAL_CHAR_J": "VERBINDEN", "LOCAL_CHAR_Z": "ZWISCHEN", "RESUME_CARD": "WIEDER",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    atoms = read_tsv(ATOMS)
    families = read_tsv(FAMILIES)
    events = read_tsv(EVENTS)
    atom_by_component = {row["component"]: row for row in atoms}
    family_by_id = {row["learned_card_id"]: row for row in families}
    if set(atom_by_component) != set(LEMMAS):
        raise SystemExit(f"lemma inventory mismatch: {set(atom_by_component) ^ set(LEMMAS)}")

    lemma_rows: list[dict[str, object]] = []
    for component, source in atom_by_component.items():
        lemma_rows.append({
            "component": component,
            "concrete_root_lemma_de": LEMMAS[component],
            "shelf": source["shelf"],
            "atom_uses": source["total_atom_occurrences"],
            "previous_abstract_value_de": source["atomic_pocket_value_de"],
            "workshop_expansion_de": source["workshop_expansion_de"],
            "image_expansion_de": source["image_expansion_de"],
            "root_rule_de": f"Der Stamm bedeutet nur {LEMMAS[component]}; Satzrollen und konkrete Besitzer kommen von Nachbarkarten und Bild.",
        })
    lemma_rows.sort(key=lambda row: (-int(row["atom_uses"]), str(row["component"])))
    write_tsv(OUT / "PASS955_56_CONCRETE_ROOT_LEMMAS.tsv", lemma_rows)

    event_rows: list[dict[str, object]] = []
    for row in events:
        layer = row["codebook_layer"]
        if layer == "PRODUCTIVE_ABBREVIATION_COMPOSITION":
            components = row["component_recipe"].split("+")
            simple = " · ".join(LEMMAS[component] for component in components)
            route = "ROOT_LEMMA_COMPOSITION"
        elif layer == "LEARNED_FORMULA_CARD":
            family = family_by_id[row["learned_card_id"]]
            simple = family["workshop_learned_value_de"] if row["channel"] == "WORKSHOP_PROSE" else family["image_register_value_de"]
            route = "LEARNED_FORMULA_IDIOM"
        else:
            simple = row["current_value_de"]
            route = "LOCAL_OWNER_VALUE"
        event_rows.append({
            **row,
            "simple_reading_route": route,
            "simple_card_reading_de": simple,
        })
    write_tsv(OUT / "PASS955_2511_SIMPLE_ROOT_AND_FORMULA_EDITION.tsv", event_rows)

    examples: list[dict[str, object]] = []
    for family in families:
        components = family["component_recipe"].split("+")
        examples.append({
            "learned_card_id": family["learned_card_id"],
            "component_recipe": family["component_recipe"],
            "literal_root_lemmas_de": " · ".join(LEMMAS[component] for component in components),
            "learned_workshop_idiom_de": family["workshop_learned_value_de"],
            "surface_variants": family["surface_variants"],
            "events": family["events"],
            "why_whole_card_de": "Die wörtlichen Stammwerte bleiben sichtbar; die häufige Folge wird als flüssige Werkstattwendung gesprochen.",
        })
    write_tsv(OUT / "PASS955_79_ROOT_TO_FORMULA_EXAMPLES.tsv", examples)

    dictionary = [
        "# Konkretes 56-Stämme-Wörterbuch",
        "",
        "Jeder Stamm hat genau ein kurzes Lemma. Eine komplexe Anweisung darf nur aus mehreren Stämmen oder aus einer der 79 ausdrücklich gelernten Formelkarten entstehen.",
        "",
    ]
    for row in lemma_rows:
        dictionary.append(f"- `{row['component']}` = **{row['concrete_root_lemma_de']}**")
    dictionary.extend([
        "",
        "Beispiel: `OK+SH+E+DY` ist wörtlich ANSETZEN · HALTEN · KURZ · SCHLIESSEN und wird als gelernte Karte „ANSETZEN, KURZ HALTEN; ENDE“ gesprochen. Kein einzelner Stamm trägt diesen ganzen Satz.",
    ])
    (OUT / "PASS955_CONCRETE_ROOT_DICTIONARY.md").write_text("\n".join(dictionary) + "\n", encoding="utf-8")

    report = """# Pass 955 — kein Stamm trägt mehr einen ganzen Satz

Die 56 produktiven Komponenten besitzen nun je genau ein kurzes deutsches
Arbeitslemma. Komplexität liegt ausschließlich in der sichtbaren Verkettung oder
in einer der 79 ausdrücklich gelernten Formelkarten.

Damit sind alte Überladungen wie „bis die Flüssigkeit klar abläuft“ auf
Stammebene ausgeschlossen. Ein Wert wie `E=KURZ`, `SH=HALTEN` oder `DY=SCHLIESSEN`
bleibt klein; erst `SH+E+DY` ergibt „kurz halten; Ende“.
"""
    (OUT / "PASS955_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS955_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"root_lemmas": len(lemma_rows), "formula_cards": len(examples), "events": len(event_rows), "outputs": outputs}
    (OUT / "PASS955_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
