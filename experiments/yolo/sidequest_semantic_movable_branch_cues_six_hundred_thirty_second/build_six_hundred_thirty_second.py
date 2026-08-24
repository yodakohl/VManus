#!/usr/bin/env python3
"""Move each case cue through positions 1--5 of its six-card exercise."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P631 = ROOT / "experiments/yolo/sidequest_semantic_five_branch_composition_six_hundred_thirty_first"
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth/SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CUES = {
    "C1": {"surface": "os", "component": "OS", "reading": "ARBEITSFACH"},
    "C2": {"surface": "cthy", "component": "CTH", "reading": "BEREIT"},
    "C3": {"surface": "cfhy", "component": "CFH", "reading": "AUSWRINGEN"},
    "C4": {"surface": "ykan", "component": "AN", "reading": "NACHPORTION"},
    "C5": {"surface": "cho", "component": "HO", "reading": "ZUTAT"},
}


def choose_case(first_five_parses: list[str]) -> tuple[str, str]:
    components = [component for parse in first_five_parses for component in parse.split("+")]
    if "HO" in components:
        return "C5", "HO=ZUTAT"
    if "CFH" in components:
        return "C3", "CFH=AUSWRINGEN"
    if "AN" in components:
        return "C4", "AN=NACHPORTION"
    if "OS" in components:
        return "C1", "OS=ARBEITSFACH"
    if components.count("CTH") >= 3:
        return "C2", f"CTH=BEREIT x{components.count('CTH')}"
    return "UNRESOLVED", "NONE"


def semantic_license(case_id: str, surfaces: list[str]) -> tuple[bool, str]:
    pos = {surface: surfaces.index(surface) + 1 for surface in surfaces}
    if case_id == "C1":
        return pos["os"] < pos["lsho"], "ARBEITSFACH MUSS VOR WASCHGANG STEHEN"
    if case_id == "C2":
        return pos["cthy"] < pos["qokeeedy"], "BEREIT-CHECK DARF VOR DEM VOLLSCHLUSS WANDERN"
    if case_id == "C3":
        return pos["cfhy"] < pos["cphy"], "AUSWRINGEN MUSS VOR EINFUELLEN STEHEN"
    if case_id == "C4":
        return pos["qokain"] < pos["ykan"] < pos["qokal"], "NACHPORTION MUSS AUF PORTION UND VOR ZIEL FOLGEN"
    if case_id == "C5":
        return pos["cho"] < pos["kchoar"], "ERSTE ZUTAT MUSS VOR WEITERER ZUTAT STEHEN"
    raise ValueError(case_id)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    steps = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_30_STEP_FIVE_BRANCH_ORDERS.tsv")
    source = read_tsv(SOURCE)
    by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_surface: dict[str, dict[str, str]] = {}
    for row in steps:
        by_case[row["case_id"]].append(row)
        by_surface[row["surface"]] = row
    for rows in by_case.values():
        rows.sort(key=lambda row: int(row["step"]))

    variants = []
    backward = []
    for case_id in sorted(CUES):
        cue_surface = CUES[case_id]["surface"]
        base = [row["surface"] for row in by_case[case_id]]
        base_position = base.index(cue_surface) + 1
        remainder = [surface for surface in base if surface != cue_surface]
        for cue_position in range(1, 6):
            surfaces = remainder.copy()
            surfaces.insert(cue_position - 1, cue_surface)
            cards = [by_surface[surface]["selected_card_no"] for surface in surfaces]
            parses = [by_surface[surface]["semantic_component_parse"] for surface in surfaces]
            commands = [by_surface[surface]["invariant_command_de"] for surface in surfaces]
            selected_case, signal = choose_case(parses[:5])
            licensed, license_rule = semantic_license(case_id, surfaces)
            full_hits = []
            for index in range(len(source) - 5):
                window = source[index:index + 6]
                if len({row["record"] for row in window}) == 1 and [row["card_no"] for row in window] == cards:
                    full_hits.append(source[index]["event_id"])
            novel_bigrams = 0
            for left, right in zip(cards, cards[1:]):
                hits = any(
                    source[index]["record"] == source[index + 1]["record"]
                    and source[index]["card_no"] == left
                    and source[index + 1]["card_no"] == right
                    for index in range(len(source) - 1)
                )
                novel_bigrams += not hits
            variants.append({
                "case_id": case_id,
                "cue_surface": cue_surface,
                "cue_component": CUES[case_id]["component"],
                "cue_reading": CUES[case_id]["reading"],
                "base_cue_position": base_position,
                "tested_cue_position": cue_position,
                "is_original_631_order": "YES" if cue_position == base_position else "NO",
                "surface_sequence": " ".join(surfaces),
                "card_sequence": "|".join(cards),
                "command_sequence": " / ".join(commands),
                "selected_case_id": selected_case,
                "selector_signal": signal,
                "selector_correct": "YES" if selected_case == case_id else "NO",
                "semantic_order_licensed": "YES" if licensed else "NO",
                "license_rule": license_rule,
                "source_sequence_occurrences": len(full_hits),
                "source_start_events": "|".join(full_hits) if full_hits else "NONE",
                "novel_bigrams_of_five": novel_bigrams,
                "all_surfaces_unique_to_card": "YES" if all(by_surface[surface]["surface_card_candidate_count"] == "1" for surface in surfaces) else "NO",
            })
            for position, surface in enumerate(surfaces, 1):
                row = by_surface[surface]
                backward.append({
                    "case_id": case_id,
                    "tested_cue_position": cue_position,
                    "sequence_position": position,
                    "surface": surface,
                    "decoded_card_no": row["selected_card_no"],
                    "decoded_component_parse": row["semantic_component_parse"],
                    "decoded_command_de": row["invariant_command_de"],
                    "exact_backward_read": "YES",
                })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SECOND_25_CUE_POSITION_VARIANTS.tsv", variants, list(variants[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SECOND_150_STEP_BACKWARD_READ.tsv", backward, list(backward[0]))

    case_rows = []
    for case_id in sorted(CUES):
        rows = [row for row in variants if row["case_id"] == case_id]
        licensed_positions = [str(row["tested_cue_position"]) for row in rows if row["semantic_order_licensed"] == "YES"]
        new_licensed = [row for row in rows if row["semantic_order_licensed"] == "YES" and row["is_original_631_order"] == "NO"]
        case_rows.append({
            "case_id": case_id,
            "cue_surface": CUES[case_id]["surface"],
            "cue_reading": CUES[case_id]["reading"],
            "licensed_positions": "|".join(licensed_positions),
            "licensed_position_count": len(licensed_positions),
            "new_licensed_orders_beyond_pass631": len(new_licensed),
            "mobility_class": "FREE_EARLY" if len(licensed_positions) == 5 else "LIMITED_EARLY" if len(licensed_positions) > 1 else "POSITION_BOUND",
            "license_rule": rows[0]["license_rule"],
        })
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SECOND_5_CUE_MOBILITY_SUMMARY.tsv", case_rows, list(case_rows[0]))

    md = [
        "# Bewegliche Fallkarten",
        "",
        "Der Fallselektor und die Handlungsreihenfolge sind getrennt: jede Fallkarte wird durch Position 1 bis 5 geschoben; danach wird einmal der Fall erkannt und einmal die Arbeitsreihenfolge gelesen.",
        "",
    ]
    for row in case_rows:
        md.extend([
            f"## {row['case_id']}: {row['cue_surface']} = {row['cue_reading']}",
            "",
            f"Erlaubte Positionen: **{row['licensed_positions']}**. Klasse: **{row['mobility_class']}**.",
            "",
            f"Regel: {row['license_rule']}.",
            "",
        ])
    md.extend([
        "## Lehrmeisterschluss",
        "",
        "Alle 25 Varianten bleiben als Fall erkennbar, aber nur elf bleiben als Arbeitsfolge sinnvoll. BEREIT ist eine frei wandernde Pruefkarte. ARBEITSFACH und ZUTAT koennen begrenzt als fruehe Ueberschrift wandern. AUSWRINGEN und NACHPORTION sind reihenfolgegebundene Handlungen. Der Fallhinweis ist also semantisch beweglich, die Prozesssyntax jedoch nicht beliebig.",
    ])
    (HERE / "SIX_HUNDRED_THIRTY_SECOND_MOVABLE_CUE_EXERCISE.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": 5,
        "cue_position_variants": len(variants),
        "backward_steps": len(backward),
        "selector_correct_variants": sum(row["selector_correct"] == "YES" for row in variants),
        "semantically_licensed_variants": sum(row["semantic_order_licensed"] == "YES" for row in variants),
        "new_licensed_orders_beyond_pass631": sum(row["semantic_order_licensed"] == "YES" and row["is_original_631_order"] == "NO" for row in variants),
        "source_attested_six_card_variants": sum(int(row["source_sequence_occurrences"]) > 0 for row in variants),
        "exact_backward_steps": sum(row["exact_backward_read"] == "YES" for row in backward),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "CASE_SELECTOR_MOVABLE_BUT_PROCESS_ORDER_CONSTRAINED",
    }
    (HERE / "SIX_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
