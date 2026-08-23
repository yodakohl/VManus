#!/usr/bin/env python3
"""Turn the four-card supplement into a neutral workshop exemplar and copybook."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FOUR_CARD = ROOT / "experiments/yolo/sidequest_semantic_minimal_master_deck_fifty_second_edition/FIFTY_SECOND_144_FOUR_CARD_COMPILER.tsv"
COMPILER = ROOT / "experiments/yolo/sidequest_semantic_compiler_decision_tree_fiftieth_edition/FIFTIETH_144_COMPILER_DECISIONS.tsv"

CATALOG = {
    "CHK": ("M01", "WÄRMEN", "die bezeichnete Portion wärmen"),
    "CKHE": ("M02", "TRENNEN", "den bezeichneten Bestand trennen"),
    "E+CLOSE": ("M03", "KURZ_SCHLUSS", "kurz ausführen und den Schritt schließen"),
    "EE+CLOSE": ("M04", "LAENGER_SCHLUSS", "länger ausführen und den Schritt schließen"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def substitute_catalog(value: str) -> tuple[str, list[str]]:
    used = []
    result = value
    for atom, (catalog_id, _, _) in CATALOG.items():
        marker = f"<{atom}_MASTER_CARD>"
        if marker in result:
            result = result.replace(marker, f"[{catalog_id}]")
            used.append(catalog_id)
    return result, used


def main() -> None:
    four_card = read_tsv(FOUR_CARD)
    old = {row["cell_id"]: row for row in read_tsv(COMPILER)}
    cards = []
    for atom, (catalog_id, short, spoken) in CATALOG.items():
        cards.append({
            "catalog_id": catalog_id,
            "atom_category": atom,
            "short_value_de": short,
            "master_spoken_lesson_de": spoken,
            "physical_exemplar_mark": f"NEUTRALER_LEHRZETTEL_{catalog_id}",
            "voynich_surface": "UNASSIGNED",
            "use_rule_de": "Nur im Übungsbuch als Katalogverweis verwenden; nicht als Manuskriptform ausgeben.",
        })
    write_tsv(OUT / "FIFTY_THIRD_4_MASTER_CATALOG_CARDS.tsv", cards)

    licensed = []
    requests = []
    for row in four_card:
        if row["four_card_branch"] == "REJECT_AND_ASK_MASTER":
            missing = []
            target_parts = row["target_atom_sequence"].split("+")
            # Compound endings must be recognized before their internal atoms.
            target = row["target_atom_sequence"]
            if target.startswith("SHED+"):
                missing.append("SHED")
            if target.startswith("SOLK+"):
                missing.append("SOLK")
            if target.endswith("+CLOSE") and not target.endswith(("+E+CLOSE", "+EE+CLOSE")):
                missing.append("CLOSE")
            if target.endswith("+E+Y"):
                missing.append("E+Y")
            requests.append({
                "request_id": f"REQ-{len(requests)+1:02d}",
                "cell_id": row["cell_id"],
                "wanted_atom_sequence": target,
                "wanted_instruction_de": row["intended_reading_de"],
                "missing_catalog_categories": "|".join(missing),
                "number_of_missing_categories": len(missing),
                "master_request_de": "Bitte passende bare Karte(n) oder konventionelle Ersatzwendung zeigen.",
                "apprentice_must_not_do_de": "Keine neue Zeichenfolge zusammensetzen.",
            })
            continue
        surface, catalog_ids = substitute_catalog(row["output_surface_or_placeholder"])
        readback = old[row["cell_id"]]["spoken_instruction_de"] if row["four_card_branch"] == "CONTROLLED_PARAPHRASE" else row["intended_reading_de"]
        licensed.append({
            "copybook_no": len(licensed) + 1,
            "cell_id": row["cell_id"],
            "intended_atom_sequence": row["target_atom_sequence"],
            "intended_instruction_de": row["intended_reading_de"],
            "compiler_branch": row["four_card_branch"],
            "written_sequence": surface,
            "master_catalog_cards_used": "|".join(catalog_ids) or "NONE",
            "readback_de": readback,
            "meaning_relation": "CONTROLLED_NEAR_PARAPHRASE" if row["four_card_branch"] == "CONTROLLED_PARAPHRASE" else "SAME_COMPOSITIONAL_READING",
            "voynich_surface_invented": "NO",
        })
    write_tsv(OUT / "FIFTY_THIRD_128_LICENSED_EXEMPLAR.tsv", licensed)
    write_tsv(OUT / "FIFTY_THIRD_16_MASTER_REQUEST_SLIPS.tsv", requests)

    pools: dict[str, list[dict[str, object]]] = {
        "OBSERVED_FUSED": [row for row in licensed if row["compiler_branch"] == "OBSERVED_FUSED_CARD"],
        "ANALYTIC_OBSERVED": [row for row in licensed if row["compiler_branch"] == "ANALYTIC_TWO_CARD_FORM" and row["master_catalog_cards_used"] == "NONE"],
        "ANALYTIC_MASTER": [row for row in licensed if row["compiler_branch"] == "ANALYTIC_TWO_CARD_FORM" and row["master_catalog_cards_used"] != "NONE"],
        "CONTROLLED_PARAPHRASE": [row for row in licensed if row["compiler_branch"] == "CONTROLLED_PARAPHRASE"],
    }
    traces = []
    for lesson, pool in pools.items():
        for row in pool[:3]:
            traces.append({
                "trace_id": f"TR-{len(traces)+1:02d}",
                "lesson_branch": lesson,
                "source_instruction_de": row["intended_instruction_de"],
                "lookup_atom_sequence": row["intended_atom_sequence"],
                "written_sequence": row["written_sequence"],
                "readback_de": row["readback_de"],
                "roundtrip_status": "NEAR_WITH_DECLARED_DRIFT" if row["meaning_relation"] == "CONTROLLED_NEAR_PARAPHRASE" else "SAME_WORKSHOP_READING",
                "master_correction_de": "Zusatznuance nennen" if row["meaning_relation"] == "CONTROLLED_NEAR_PARAPHRASE" else "keine",
            })
    write_tsv(OUT / "FIFTY_THIRD_12_APPRENTICE_TRACES.tsv", traces)

    request_counts = Counter()
    for row in requests:
        for value in row["missing_catalog_categories"].split("|"):
            request_counts[value] += 1
    book = [
        "# Simuliertes Meisterexemplar",
        "",
        "Vier neutrale Lehrzettel stehen im Schrank: M01 wärmen, M02 trennen,",
        "M03 kurz-und-schließen, M04 länger-und-schließen. Sie sind keine Voynich-",
        "Schreibungen, sondern Platzhalter dafür, dass ein Meister diese Kategorien",
        "durch eine echte gelernte Karte vermitteln könnte.",
        "",
        "Der Lehrling kann damit 128 Befehle vorwärts schreiben und rückwärts lesen.",
        "Die sechzehn übrigen Zettel verlangen nur noch vier Kategorien:",
        "",
    ]
    for atom in ("CLOSE", "E+Y", "SHED", "SOLK"):
        book.append(f"- `{atom}` wird in {request_counts[atom]} offenen Bestellungen gebraucht.")
    book.extend([
        "",
        "Zwei Bestellungen brauchen je zwei davon zugleich: SHED+CLOSE und SOLK+CLOSE.",
        "Alles andere ist mit genau einem weiteren Lehrzettel erreichbar.",
    ])
    (OUT / "FIFTY_THIRD_SIMULATED_MASTER_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "neutral_catalog_cards": len(cards),
            "licensed_copybook_commands": len(licensed),
            "master_request_slips": len(requests),
            "apprentice_traces": len(traces),
            "new_voynich_surfaces": 0,
        },
        "remaining_category_request_counts": dict(request_counts),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (FOUR_CARD, COMPILER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
