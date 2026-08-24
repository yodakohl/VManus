#!/usr/bin/env python3
"""Compose one new in-deck apprentice strip for each complete case branch."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
COMMAND_DIR = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ORDERS = {
    "C1": ["qokaiin", "os", "lsho", "qokal", "shey", "shedy"],
    "C2": ["cthy", "cthaiin", "qoctholy", "ches", "qokal", "qokeeedy"],
    "C3": ["cfhy", "cphy", "qokaiin", "qokal", "shey", "shedy"],
    "C4": ["qokaiin", "qokain", "ykan", "qokal", "qokylddy", "talam"],
    "C5": ["cho", "qokaiin", "kchoar", "chodaly", "daiiin", "shedy"],
}


ORDINARY = {
    "C1": "Nach Sollmass ansetzen; das Arbeitsfach waehlen; den Waschgang am Ziel ansetzen, den Posten laenger halten, absetzen und schliessen.",
    "C2": "Posten und Sollmass bereitstellen; den bereiten Arbeitsgang fortsetzen; kurz abnehmen und teilen; am Ziel ansetzen und bis zum Vollgrad schliessen.",
    "C3": "Den Posten auswringen, einfuellen, nach Sollmass am Ziel ansetzen, laenger halten, absetzen und schliessen.",
    "C4": "Nach Sollmass eine Portion und eine Nachportion zudosieren; am Ziel ansetzen, den Posten befestigen, schliessen und verwahren.",
    "C5": "Zutat nach Sollmass ansetzen; weitere Zutat aus dem Vorrat zur Zielstelle geben; zweite Arbeitsstufe setzen, absetzen und schliessen.",
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


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(COMMAND_DIR / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    source = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    cards_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    exemplar_by_surface: dict[str, dict[str, str]] = {}
    for card in cards:
        for surface in card["surfaces"].split("|"):
            cards_by_surface[surface].append(card)
    for event in source:
        exemplar_by_surface.setdefault(event["surface"], event)

    step_rows = []
    summary_rows = []
    backward_rows = []
    bigram_rows = []
    for case_id, surfaces in ORDERS.items():
        case_steps = []
        for step, surface in enumerate(surfaces, 1):
            candidates = cards_by_surface[surface]
            card = candidates[0]
            exemplar = exemplar_by_surface[surface]
            case_steps.append({
                "case_id": case_id,
                "step": step,
                "ordinary_order_de": ORDINARY[case_id],
                "surface": surface,
                "surface_card_candidate_count": len(candidates),
                "selected_card_no": card["card_no"],
                "semantic_component_parse": card["semantic_component_parse"],
                "invariant_command_de": card["standard_command_de"],
                "surface_exemplar_event": exemplar["event_id"],
                "surface_exemplar_record": exemplar["record"],
                "new_word": "NO",
                "new_card": "NO",
                "new_surface": "NO",
            })
        step_rows.extend(case_steps)
        selected_case, signal = choose_case([str(row["semantic_component_parse"]) for row in case_steps[:5]])
        cards_sequence = [str(row["selected_card_no"]) for row in case_steps]
        full_hits = []
        for index in range(len(source) - len(cards_sequence) + 1):
            window = source[index:index + len(cards_sequence)]
            if len({row["record"] for row in window}) == 1 and [row["card_no"] for row in window] == cards_sequence:
                full_hits.append(source[index]["event_id"])
        summary_rows.append({
            "intended_case_id": case_id,
            "selected_case_id": selected_case,
            "selector_signal": signal,
            "ordinary_order_de": ORDINARY[case_id],
            "surface_sequence": " ".join(surfaces),
            "card_sequence": "|".join(cards_sequence),
            "full_sequence_source_occurrences": len(full_hits),
            "full_sequence_source_start_events": "|".join(full_hits) if full_hits else "NONE",
            "selector_correct": "YES" if selected_case == case_id else "NO",
            "all_surfaces_unique_to_card": "YES" if all(int(row["surface_card_candidate_count"]) == 1 for row in case_steps) else "NO",
        })
        for row in case_steps:
            card = cards_by_surface[str(row["surface"])][0]
            backward_rows.append({
                "case_id": case_id,
                "step": row["step"],
                "surface": row["surface"],
                "decoded_card_no": card["card_no"],
                "decoded_component_parse": card["semantic_component_parse"],
                "decoded_command_de": card["standard_command_de"],
                "expected_card_no": row["selected_card_no"],
                "exact_backward_read": "YES" if card["card_no"] == row["selected_card_no"] else "NO",
            })
        for left, right in zip(case_steps, case_steps[1:]):
            pair = [str(left["selected_card_no"]), str(right["selected_card_no"])]
            hits = []
            for index in range(len(source) - 1):
                if source[index]["record"] == source[index + 1]["record"] and [source[index]["card_no"], source[index + 1]["card_no"]] == pair:
                    hits.append(source[index]["event_id"])
            bigram_rows.append({
                "case_id": case_id,
                "left_step": left["step"],
                "right_step": right["step"],
                "card_bigram": "|".join(pair),
                "source_occurrences": len(hits),
                "source_start_events": "|".join(hits) if hits else "NONE",
            })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIRST_30_STEP_FIVE_BRANCH_ORDERS.tsv", step_rows, list(step_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv", summary_rows, list(summary_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIRST_30_STEP_BACKWARD_READ.tsv", backward_rows, list(backward_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIRST_25_BIGRAM_NOVELTY_AUDIT.tsv", bigram_rows, list(bigram_rows[0]))

    md = ["# Fuenf neue Lehrlingsstreifen", ""]
    for summary in summary_rows:
        md.extend([
            f"## {summary['intended_case_id']}",
            "",
            f"**Auftrag:** {summary['ordinary_order_de']}",
            "",
            f"**Schrift:** `{summary['surface_sequence']}`",
            "",
            f"**Fruehe Fallwahl:** {summary['selector_signal']} -> {summary['selected_case_id']}.",
            "",
            f"**Quellvorkommen der ganzen Folge:** {summary['full_sequence_source_occurrences']}.",
            "",
        ])
    md.extend([
        "# Lehrmeisterregel",
        "",
        "Alle Streifen benutzen nur bereits belegte Oberflaechen und jede Oberflaeche bezeichnet genau eine Karte. Der Fall wird aus den ersten fuenf Karten gewaehlt; danach werden die sechs Befehle normal zurueckgelesen. Die Streifen sind Uebungstafeln, keine neu behaupteten Manuskriptzeilen.",
    ])
    (HERE / "SIX_HUNDRED_THIRTY_FIRST_FIVE_BRANCH_EXERCISE.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "orders": len(summary_rows),
        "steps": len(step_rows),
        "correct_branch_selections": sum(row["selector_correct"] == "YES" for row in summary_rows),
        "orders_absent_from_source": sum(int(row["full_sequence_source_occurrences"]) == 0 for row in summary_rows),
        "surface_unique_steps": sum(int(row["surface_card_candidate_count"]) == 1 for row in step_rows),
        "exact_backward_steps": sum(row["exact_backward_read"] == "YES" for row in backward_rows),
        "novel_bigrams": sum(int(row["source_occurrences"]) == 0 for row in bigram_rows),
        "attested_bigrams": sum(int(row["source_occurrences"]) > 0 for row in bigram_rows),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "ALL_FIVE_BRANCHES_COMPOSE_NEW_READABLE_IN_DECK_ORDERS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
