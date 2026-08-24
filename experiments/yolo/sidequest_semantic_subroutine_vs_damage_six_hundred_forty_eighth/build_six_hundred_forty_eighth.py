#!/usr/bin/env python3
"""Separate contiguous short subroutines from gapped damaged remnants."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P646 = ROOT / "experiments/yolo/sidequest_semantic_case_fragment_capacity_six_hundred_forty_sixth"
P647 = ROOT / "experiments/yolo/sidequest_semantic_owner_resolution_six_hundred_forty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    ambiguous = read_tsv(P646 / "SIX_HUNDRED_FORTY_SIXTH_AMBIGUOUS_FRAGMENTS.tsv")
    owner_contexts = read_tsv(P647 / "SIX_HUNDRED_FORTY_SEVENTH_74_OWNER_CONTEXTS.tsv")

    shape_rows: list[dict[str, object]] = []
    shape_by_id: dict[str, dict[str, object]] = {}
    for row in ambiguous:
        positions = [int(value) for value in row["source_positions"].split("|")]
        contiguous = positions == list(range(positions[0], positions[-1] + 1))
        missing_inside = [value for value in range(positions[0], positions[-1] + 1) if value not in positions]
        if len(positions) == 1:
            shape = "SINGLE_CARD"
            diagnosis = "LEGITIMATE_SINGLE_CARD_CELL_POSSIBLE"
        elif contiguous and positions[-1] == 6:
            shape = "CONTIGUOUS_CLOSED_SUFFIX"
            diagnosis = "LEGITIMATE_CLOSED_SUFFIX_POSSIBLE"
        elif contiguous and positions[0] == 1:
            shape = "CONTIGUOUS_PREFIX"
            diagnosis = "LEGITIMATE_OPEN_PREFIX_POSSIBLE"
        elif contiguous:
            shape = "CONTIGUOUS_INTERNAL"
            diagnosis = "LEGITIMATE_INTERNAL_SUBROUTINE_POSSIBLE"
        else:
            shape = "GAPPED_SUBSEQUENCE"
            diagnosis = "NONCONTIGUOUS_REMAINDER__OMISSION_OR_COLLATION_REQUIRED"
        item = {
            "fragment_id": row["fragment_id"],
            "source_case": row["source_case"],
            "surface_fragment": row["surface_fragment"],
            "card_fragment": row["card_fragment"],
            "source_positions": row["source_positions"],
            "position_shape": shape,
            "contiguous_in_owner_case": "YES" if contiguous else "NO",
            "starts_at_case_start": "YES" if positions[0] == 1 else "NO",
            "ends_at_case_close": "YES" if positions[-1] == 6 else "NO",
            "missing_internal_positions": "|".join(str(value) for value in missing_inside) if missing_inside else "NONE",
            "safe_diagnosis": diagnosis,
            "may_be_legitimate_short_unit": "YES" if contiguous else "NO",
            "may_insert_missing_cards_without_damage_evidence": "NO",
        }
        shape_rows.append(item)
        shape_by_id[row["fragment_id"]] = item

    context_rows: list[dict[str, object]] = []
    for context in owner_contexts:
        shape = shape_by_id[context["fragment_id"]]
        context_rows.append({
            "fragment_id": context["fragment_id"],
            "source_case": context["source_case"],
            "domain": context["domain"],
            "page": context["page"],
            "record": context["record"],
            "surface_fragment": context["surface_fragment"],
            "owner_address_resolved": context["record_resolves"],
            "source_positions": shape["source_positions"],
            "position_shape": shape["position_shape"],
            "contiguous_in_owner_case": shape["contiguous_in_owner_case"],
            "ends_at_case_close": shape["ends_at_case_close"],
            "missing_internal_positions": shape["missing_internal_positions"],
            "safe_diagnosis": shape["safe_diagnosis"],
            "editor_action": (
                "READ_AS_POSSIBLE_SHORT_UNIT__DO_NOT_EXPAND"
                if shape["contiguous_in_owner_case"] == "YES"
                else "MARK_POSSIBLE_LOSS__SEEK_SECOND_COPY_OR_VISIBLE_DAMAGE"
            ),
            "automatic_insertions": 0,
        })

    backbone_rows = [
        {**row}
        for row in context_rows
        if row["surface_fragment"] == "qokaiin qokal shey shedy" and row["source_case"] in {"C1", "C3"}
    ]
    for row in backbone_rows:
        row["backbone_interpretation_de"] = (
            "C3: zusammenhaengende Positionen 3-6; kann ein vollstaendiger kurzer Enduntergang sein"
            if row["source_case"] == "C3"
            else "C1: Positionen 1,4,5,6; OS und LSH fehlen im Inneren, daher nur als Lueckenrest einer Vollform"
        )

    write_tsv(HERE / "SIX_HUNDRED_FORTY_EIGHTH_37_FRAGMENT_SHAPES.tsv", shape_rows, list(shape_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_EIGHTH_74_CONTEXT_JUDGMENTS.tsv", context_rows, list(context_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_EIGHTH_4_C1_C3_BACKBONE_CONTEXTS.tsv", backbone_rows, list(backbone_rows[0]))

    counts = {
        "contiguous": sum(row["contiguous_in_owner_case"] == "YES" for row in context_rows),
        "gapped": sum(row["contiguous_in_owner_case"] == "NO" for row in context_rows),
        "closed_suffix": sum(row["position_shape"] == "CONTIGUOUS_CLOSED_SUFFIX" for row in context_rows),
        "single": sum(row["position_shape"] == "SINGLE_CARD" for row in context_rows),
    }
    md = [
        "# Kurzer Untergang oder beschädigte Vollform?",
        "",
        f"Von 74 adressierten Kontexten sind {counts['contiguous']} zusammenhängende Ausschnitte und {counts['gapped']} nichtzusammenhängende Reste mit inneren Lücken.",
        "",
        "## Der entscheidende identische Vierer",
        "",
        "`qokaiin qokal shey shedy` hat je nach Besitzer zwei verschiedene editorische Zustände:",
        "",
        "- in C3 steht er auf Position 3–6 zusammenhängend und kann ein absichtlich kurzer geschlossener Enduntergang sein;",
        "- in C1 verbindet er Position 1 mit 4–6; `os lsho` fehlen im Inneren. Als Rest der vollen C1-Form setzt er daher eine Lücke oder Kollation voraus.",
        "",
        "Die Kartenbedeutung ändert sich dabei nicht. Der Besitzer plus Stellung entscheidet nur, ob Expansion überhaupt nötig erscheint.",
        "",
        "## Korrekturregel",
        "",
        "Zusammenhängende Fragmente werden zunächst als legitime kurze Einheiten gelesen. Nichtzusammenhängende Fragmente werden als mögliche Verluste markiert, aber erst nach zweiter Kopie oder sichtbarer Beschädigung ergänzt. Automatische Einsetzungen bleiben null.",
    ]
    (HERE / "SIX_HUNDRED_FORTY_EIGHTH_SUBROUTINE_DAMAGE_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "fragment_shapes": len(shape_rows),
        "owner_contexts": len(context_rows),
        "contiguous_contexts": counts["contiguous"],
        "gapped_contexts": counts["gapped"],
        "closed_suffix_contexts": counts["closed_suffix"],
        "single_card_contexts": counts["single"],
        "c1_c3_backbone_contexts": len(backbone_rows),
        "automatic_insertions": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "OWNER_PLUS_CONTIGUITY_SEPARATES_SHORT_UNITS_FROM_GAPPED_REMAINDERS",
    }
    (HERE / "SIX_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
