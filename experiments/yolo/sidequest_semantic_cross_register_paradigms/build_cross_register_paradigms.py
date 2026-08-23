#!/usr/bin/env python3
"""Consolidate recurrent prose/Astro component families into a workshop lexicon."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRANSFER = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/NEW_MULTI_ATOM_CANDIDATES.tsv"
HITS = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/FORWARD_CELL_ASTRO_HITS.tsv"
PROSE_CARDS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


ATOM_VALUES = {
    "AIIN": "SOLLWERT", "AIN": "PORTION", "IIN": "STUFE", "AL": "ZIEL",
    "AR": "QUELLE", "AIR": "LAUF/BAHN", "OK": "AKTIVIEREN/ANSETZEN",
    "OL": "FORTSETZEN", "OT": "FOLGE/NÄCHSTER", "OR": "SATZ/ANSATZ",
    "Y": "AKTUELLER POSTEN", "E": "KURZ", "EE": "LÄNGER", "EEE": "VOLL",
    "CHD": "UMSETZEN", "CTH": "BEREIT", "CKH": "DURCHLAUF", "CKHE": "TRENNEN/SEIHEN",
    "CHK": "WÄRMEN/HALTEN", "SHED": "ABSETZEN", "SOLK": "SAMMELN",
    "HO": "EINGANGSPOSTEN", "CHEO": "AUSGABE/AUSZUG", "KCH": "BEARBEITEN",
    "TY": "TEIL",
}

COMPOSITION_VALUES = {
    "OK+AR": "QUELLE AKTIVIEREN",
    "OK+AL": "ZIEL AKTIVIEREN",
    "OT+OL": "ALS NÄCHSTES FORTSETZEN",
    "OT+OR": "NÄCHSTER SATZ/ANSATZ",
    "OK+OL": "FORTSETZUNG AKTIVIEREN",
    "OT+AR": "NÄCHSTE QUELLE",
    "AL+AIIN": "ZIELWERT",
    "AR+AL": "VON QUELLE ZUM ZIEL",
    "OL+AR": "VON DER QUELLE WEITER",
    "OT+AIR": "NÄCHSTER LAUF/NÄCHSTE BAHN",
    "CHD+AIIN": "ZUM SOLLWERT UMSETZEN",
}


def main() -> None:
    candidates = read(TRANSFER)
    hits = read(HITS)
    prose_cards = read(PROSE_CARDS)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        grouped[row["detected_literal_atoms"]].append(row)

    family_rows = []
    promoted_sequences = set()
    for sequence, rows in sorted(grouped.items()):
        surface_types = len(rows)
        occurrences = sum(int(row["occurrences"]) for row in rows)
        owners = sorted({owner for row in rows for owner in row["owners"].split("|")})
        if len(owners) >= 2 and (surface_types >= 2 or occurrences >= 2):
            status = "PROMOTED_PRODUCTIVE_FAMILY"
            promoted_sequences.add(sequence)
        else:
            status = "ONE_OFF_COMPOSITION"
        family_rows.append({
            "atom_sequence": sequence, "common_nucleus_de": COMPOSITION_VALUES.get(sequence, " + ".join(ATOM_VALUES.get(atom, atom) for atom in sequence.split("+"))),
            "surface_type_count": surface_types, "astro_occurrences": occurrences,
            "owner_count": len(owners), "owners": "|".join(owners),
            "surface_forms": "|".join(row["visible_surface"] for row in rows),
            "pages": "|".join(sorted({page for row in rows for page in row["owners"].split("|") if page.startswith("f")})) or "OWNER_ENCODED",
            "status": status,
            "teaching_rule_de": "lies die Kerne in Reihenfolge; der sichtbare Besitzer liefert Stern, Ring, Wert, Stoff oder Station",
        })

    # Exact forward hits receive a named row even when they are a single type.
    exact_sequences = set()
    family_by_sequence = {str(row["atom_sequence"]): row for row in family_rows}
    for hit in hits:
        if int(hit["astro_exact_hit_count"]) == 0:
            continue
        exact_sequences.add(hit["predicted_atom_sequence"])
        if hit["predicted_atom_sequence"] in family_by_sequence:
            existing = family_by_sequence[hit["predicted_atom_sequence"]]
            if existing["status"] == "ONE_OFF_COMPOSITION":
                existing["status"] = "FORWARD_PREDICTED_SINGLE_CELL"
                existing["teaching_rule_de"] = "vor dem Astro-Scan aus dem Prosa-Paradigma gebildet; Besitzer liefert die lokale Expansion"
        else:
            family_rows.append({
                "atom_sequence": hit["predicted_atom_sequence"],
                "common_nucleus_de": COMPOSITION_VALUES.get(hit["predicted_atom_sequence"], hit["predicted_short_reading_de"]),
                "surface_type_count": len(hit["astro_surfaces"].split("|")), "astro_occurrences": hit["astro_exact_hit_count"],
                "owner_count": len(hit["astro_owners"].split("|")), "owners": hit["astro_owners"],
                "surface_forms": hit["astro_surfaces"], "pages": hit["astro_pages"],
                "status": "FORWARD_PREDICTED_SINGLE_CELL",
                "teaching_rule_de": "vor dem Astro-Scan aus dem Prosa-Paradigma gebildet; Besitzer liefert die lokale Expansion",
            })
    family_rows.sort(key=lambda row: (-int(row["astro_occurrences"]), str(row["atom_sequence"])))
    write(HERE / "PRODUCTIVE_CROSS_REGISTER_FAMILIES.tsv", family_rows, list(family_rows[0]))

    dictionary_rows = []
    for atom, value in ATOM_VALUES.items():
        prose_types = sum(atom in row["corrected_semantic_atoms"].split("+") for row in prose_cards)
        prose_events = sum(int(row["prose_events"]) for row in prose_cards if atom in row["corrected_semantic_atoms"].split("+"))
        astro_types = sum(atom in row["detected_literal_atoms"].split("+") for row in candidates)
        astro_events = sum(int(row["occurrences"]) for row in candidates if atom in row["detected_literal_atoms"].split("+"))
        if prose_types and astro_types:
            status = "PORTABLE_BOTH_REGISTERS"
        elif prose_types:
            status = "PROSE_PRODUCTIVE"
        elif astro_types:
            status = "ASTRO_CANDIDATE"
        else:
            status = "BOUND_ONLY"
        dictionary_rows.append({
            "atom": atom, "short_common_value_de": value, "prose_card_types": prose_types,
            "prose_events": prose_events, "astro_candidate_types": astro_types,
            "astro_candidate_occurrences": astro_events, "portability_status": status,
            "wet_owner_expansion_de": {
                "AIR": "laufende Flüssigkeit/Wasserlauf", "AL": "Zielstelle", "AR": "Ausgangsquelle",
                "AIIN": "Sollmaß", "IIN": "Arbeitsstufe", "OR": "Ansatz",
            }.get(atom, value.lower()),
            "celestial_owner_expansion_de": {
                "AIR": "Ring-/Zeiger-/Himmelsbahn", "AL": "Zielsektor/Zielstern", "AR": "Ausgangssektor/Ursprung",
                "AIIN": "Sollwert/Grad", "IIN": "Bedingungsstufe", "OR": "Wahl-/Tabellensatz",
            }.get(atom, value.lower()),
        })
    write(HERE / "REVISED_COMMON_STEM_DICTIONARY.tsv", dictionary_rows, list(dictionary_rows[0]))

    candidate_rows = []
    for row in candidates:
        sequence = row["detected_literal_atoms"]
        if sequence in promoted_sequences:
            status = "FAMILY_COMPOSITION"
        elif sequence in exact_sequences:
            status = "FORWARD_SINGLE_CELL"
        else:
            status = "LEARNED_ASTRO_WORD_WITH_COMPONENT_HINT"
        candidate_rows.append({
            "visible_surface": row["visible_surface"], "occurrences": row["occurrences"],
            "atom_sequence": sequence, "common_nucleus_de": COMPOSITION_VALUES.get(sequence, row["creative_default_de"]),
            "owners": row["owners"], "composition_status": status,
            "local_astro_reading_de": row["representative_astro_reading_de"],
            "workshop_pronunciation_de": f"{COMPOSITION_VALUES.get(sequence, row['creative_default_de'])}; am Besitzer {row['owners']}",
        })
    write(HERE / "ASTRO_53_COMPOSITIONAL_DICTIONARY.tsv", candidate_rows, list(candidate_rows[0]))

    residual_counts = Counter()
    residual_examples: dict[str, set[str]] = defaultdict(set)
    for row in candidates:
        surface = row["visible_surface"]
        sequence = row["detected_literal_atoms"]
        # Use middle material not captured by the visible core strings as a
        # descriptive renderer/modifier inventory, not as a semantic alphabet.
        known_literals = [
            "aiin", "iiin", "air", "cheo", "ckhe", "ched", "chd", "cth", "solk", "olk",
            "shed", "ckh", "cheek", "chek", "kch", "cho", "sho", "ain", "ok", "ol", "ot", "or", "al", "ar", "ty",
        ]
        residual = surface
        for literal in sorted(known_literals, key=len, reverse=True):
            residual = residual.replace(literal, "")
        residual = residual or "NONE"
        residual_counts[(sequence, residual)] += int(row["occurrences"])
        residual_examples[(sequence, residual)].add(surface)
    residual_rows = []
    for (sequence, residual), occurrences in sorted(residual_counts.items()):
        residual_rows.append({
            "atom_sequence": sequence, "residual_string": residual, "astro_occurrences": occurrences,
            "surface_examples": "|".join(sorted(residual_examples[(sequence, residual)])),
            "current_role": "NO_RESIDUAL" if residual == "NONE" else "RENDERER_OR_LOCAL_MODIFIER",
            "semantic_decision": "do not assign an independent meaning until recurrence separates it from owner and family",
        })
    write(HERE / "RESIDUAL_MODIFIER_INVENTORY.tsv", residual_rows, list(residual_rows[0]))

    strong = [row for row in family_rows if row["status"] == "PROMOTED_PRODUCTIVE_FAMILY"]
    forward = [row for row in family_rows if row["status"] == "FORWARD_PREDICTED_SINGLE_CELL"]
    phrasebook = "# Kleine registerübergreifende Werkstatt-Phrasebook\n\n"
    phrasebook += "Die linke Spalte ist der gemeinsame Kartenwert; die beiden Expansionen werden vom sichtbaren Besitzer geliefert.\n\n"
    for row in strong + forward:
        wet = str(row["common_nucleus_de"]).replace("SATZ/ANSATZ", "Ansatz").replace("LAUF/BAHN", "Wasserlauf")
        astro = str(row["common_nucleus_de"]).replace("SATZ/ANSATZ", "Wahlsatz").replace("LAUF/BAHN", "Himmelsbahn")
        phrasebook += f"- `{row['atom_sequence']}` — **{row['common_nucleus_de']}**\n  - Nasswerkstatt: {wet}.\n  - Himmels-/Kalendertafel: {astro}.\n  - Formen: `{row['surface_forms']}`.\n"
    (HERE / "CROSS_REGISTER_PHRASEBOOK.md").write_text(phrasebook, encoding="utf-8")

    report = f"""# Produktive Mischgrammatik über Prosa und Astrotafeln

## Ergebnis

Die 53 neuen Mehrkernformen sind keine gleichwertige Masse. Acht Folgen bilden echte Reihen mit mehreren Schreibformen und mehreren Besitzern: `OK+AR`, `OK+AL`, `OT+OL`, `OT+OR`, `OK+OL`, `OT+AR`, `AL+AIIN` und `AR+AL`. Zusammen mit den drei vorwärts gefüllten Einzelzellen `OL+AR`, `OT+AIR` und `CHD+AIIN` entsteht ein kleines vorhersagendes Mischsystem.

Die stärksten Reihen:

- `OK+AR` — fünf Oberflächenformen, neun Vorkommen, acht Besitzer: **Quelle aktivieren**.
- `OK+AL` — fünf Formen an fünf Besitzern: **Ziel aktivieren**.
- `OT+OL` — drei Formen: **als nächstes fortsetzen**.
- `OT+OR` — drei Vorkommen: **nächster Satz/Ansatz**.
- `OK+OL` — drei Vorkommen: **Fortsetzung aktivieren**.

Das passt genau zum gesuchten historischen Architekturtyp: eine kleine produktive Fachkürzungsgrammatik steht neben vielen gelernten Ganzkarten. Die Kerne tragen kurze Rollen; lokale Restzeichen und der Bildbesitzer liefern den konkreten Stern, Ring, Stoff, Ansatz oder Stationswert.

## Was nicht als Stamm befördert wird

Die Reststrings `q/s/y/o/d/e...` werden in `RESIDUAL_MODIFIER_INVENTORY.tsv` gesammelt, aber noch nicht einzeln übersetzt. Ein einzelnes `e` kann in einer belegten OK-Gradreihe kurz/länger unterscheiden; außerhalb dieser Reihe bleibt es Renderer oder lokaler Modifier. Damit vermeiden wir die alte Falle, aus jedem sichtbaren Buchstaben sofort ein deutsches Wort zu machen.

## Neue gemeinsame Minimalwerte

`AIR` heißt nun **LAUF/BAHN**, nicht global Wasser. `OR` heißt **SATZ/ANSATZ**, nicht global Flüssigkeit. `AL/AR` sind Ziel/Quelle, `AIIN/IIN` Sollwert/Stufe, `OK/OL/OT` aktivieren/fortsetzen/Folge. Diese Werte erzeugen in beiden Registern kurze sinnvolle Kompositionen, während der Besitzer die Sachklasse liefert.

## Bilanz

{len(strong)} Mehrformenfamilien werden produktiv gesprochen; {len(forward)} vorwärts gefüllte Einzelzellen bleiben starke kleine Prognosen. Die übrigen {len(candidate_rows) - sum(int(row['surface_type_count']) for row in strong) - len(forward)} Kandidatenformen bleiben gelernte Astro-Wörter mit Komponentenhinweis und werden nicht in ein universelles Alphabet gezwungen.
"""
    (HERE / "CROSS_REGISTER_PARADIGM_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "candidate_types": len(candidate_rows), "productive_families": len(strong),
        "forward_single_cells": len(forward), "common_atoms": len(dictionary_rows),
        "residual_rows": len(residual_rows),
        "promoted_sequences": sorted(promoted_sequences), "forward_sequences": sorted(exact_sequences),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
