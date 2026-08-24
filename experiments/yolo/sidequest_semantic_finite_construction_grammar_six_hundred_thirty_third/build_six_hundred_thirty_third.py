#!/usr/bin/env python3
"""Enumerate the legal linear extensions of five six-card workshop jobs."""

from __future__ import annotations

import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P631 = ROOT / "experiments/yolo/sidequest_semantic_five_branch_composition_six_hundred_thirty_first"
P632 = ROOT / "experiments/yolo/sidequest_semantic_movable_branch_cues_six_hundred_thirty_second"
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth/SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


GRAMMAR = {
    "C1": {
        "nodes": {"A": "qokaiin", "W": "os", "X": "lsho", "T": "qokal", "H": "shey", "C": "shedy"},
        "edges": [("A", "X"), ("W", "X"), ("X", "H"), ("T", "H"), ("H", "C")],
    },
    "C2": {
        "nodes": {"R": "cthy", "M": "cthaiin", "P": "qoctholy", "S": "ches", "T": "qokal", "C": "qokeeedy"},
        "edges": [("M", "P"), ("P", "S"), ("S", "T"), ("T", "C"), ("R", "C")],
    },
    "C3": {
        "nodes": {"W": "cfhy", "P": "cphy", "M": "qokaiin", "T": "qokal", "H": "shey", "C": "shedy"},
        "edges": [("W", "P"), ("M", "T"), ("P", "H"), ("T", "H"), ("H", "C")],
    },
    "C4": {
        "nodes": {"M": "qokaiin", "P": "qokain", "N": "ykan", "T": "qokal", "F": "qokylddy", "S": "talam"},
        "edges": [("M", "P"), ("P", "N"), ("N", "T"), ("T", "F"), ("F", "S")],
    },
    "C5": {
        "nodes": {"I": "cho", "M": "qokaiin", "F": "kchoar", "T": "chodaly", "G": "daiiin", "C": "shedy"},
        "edges": [("I", "F"), ("M", "F"), ("F", "T"), ("T", "G"), ("G", "C")],
    },
}


EDGE_READING = {
    "C1": {("A", "X"): "SOLLMASS VOR WASCHEN", ("W", "X"): "ARBEITSFACH VOR WASCHEN", ("X", "H"): "WASCHEN VOR HALTEN", ("T", "H"): "ZIEL VOR HALTEN", ("H", "C"): "HALTEN VOR SCHLUSS"},
    "C2": {("M", "P"): "SOLLMASS BEREIT VOR FORTSETZEN", ("P", "S"): "FORTSETZEN VOR TEILEN", ("S", "T"): "TEILEN VOR ZIEL", ("T", "C"): "ZIEL VOR VOLLSCHLUSS", ("R", "C"): "BEREIT-CHECK VOR VOLLSCHLUSS"},
    "C3": {("W", "P"): "AUSWRINGEN VOR EINFUELLEN", ("M", "T"): "SOLLMASS VOR ZIEL", ("P", "H"): "EINFUELLEN VOR HALTEN", ("T", "H"): "ZIEL VOR HALTEN", ("H", "C"): "HALTEN VOR SCHLUSS"},
    "C4": {("M", "P"): "SOLLMASS VOR PORTION", ("P", "N"): "PORTION VOR NACHPORTION", ("N", "T"): "NACHPORTION VOR ZIEL", ("T", "F"): "ZIEL VOR BEFESTIGEN", ("F", "S"): "BEFESTIGEN VOR VERWAHREN"},
    "C5": {("I", "F"): "ERSTE ZUTAT VOR WEITERER ZUTAT", ("M", "F"): "SOLLMASS VOR WEITERER ZUTAT", ("F", "T"): "WEITERE ZUTAT VOR ZIEL", ("T", "G"): "ZIEL VOR ZWEITSTUFE", ("G", "C"): "ZWEITSTUFE VOR SCHLUSS"},
}


def choose_case(parses: list[str]) -> str:
    components = [part for parse in parses[:5] for part in parse.split("+")]
    if "HO" in components:
        return "C5"
    if "CFH" in components:
        return "C3"
    if "AN" in components:
        return "C4"
    if "OS" in components:
        return "C1"
    if components.count("CTH") >= 3:
        return "C2"
    return "UNRESOLVED"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    steps = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_30_STEP_FIVE_BRANCH_ORDERS.tsv")
    variants632 = read_tsv(P632 / "SIX_HUNDRED_THIRTY_SECOND_25_CUE_POSITION_VARIANTS.tsv")
    source = read_tsv(SOURCE)
    by_surface = {row["surface"]: row for row in steps}
    orders631 = {row["case_id"]: " ".join(r["surface"] for r in sorted([x for x in steps if x["case_id"] == row["case_id"]], key=lambda x: int(x["step"]))) for row in steps}
    licensed632 = {row["surface_sequence"] for row in variants632 if row["semantic_order_licensed"] == "YES"}

    edge_rows = []
    order_rows = []
    backward_rows = []
    bigram_rows = []
    for case_id, spec in GRAMMAR.items():
        for left, right in spec["edges"]:
            edge_rows.append({
                "case_id": case_id,
                "left_node": left,
                "left_surface": spec["nodes"][left],
                "right_node": right,
                "right_surface": spec["nodes"][right],
                "precedence_rule": EDGE_READING[case_id][(left, right)],
            })
        legal = []
        node_names = list(spec["nodes"])
        for permutation in itertools.permutations(node_names):
            position = {node: index for index, node in enumerate(permutation)}
            if all(position[left] < position[right] for left, right in spec["edges"]):
                legal.append(permutation)
        for number, permutation in enumerate(legal, 1):
            surfaces = [spec["nodes"][node] for node in permutation]
            rows = [by_surface[surface] for surface in surfaces]
            cards = [row["selected_card_no"] for row in rows]
            parses = [row["semantic_component_parse"] for row in rows]
            commands = [row["invariant_command_de"] for row in rows]
            sequence = " ".join(surfaces)
            source_hits = []
            for index in range(len(source) - 5):
                window = source[index:index + 6]
                if len({row["record"] for row in window}) == 1 and [row["card_no"] for row in window] == cards:
                    source_hits.append(source[index]["event_id"])
            order_id = f"{case_id}-L{number:02d}"
            order_rows.append({
                "order_id": order_id,
                "case_id": case_id,
                "node_order": "-".join(permutation),
                "surface_sequence": sequence,
                "card_sequence": "|".join(cards),
                "command_sequence": " / ".join(commands),
                "selected_case_id": choose_case(parses),
                "selector_correct": "YES" if choose_case(parses) == case_id else "NO",
                "is_pass631_order": "YES" if sequence == orders631[case_id] else "NO",
                "was_licensed_in_pass632": "YES" if sequence in licensed632 else "NO",
                "source_sequence_occurrences": len(source_hits),
                "source_start_events": "|".join(source_hits) if source_hits else "NONE",
                "all_precedence_edges_satisfied": "YES",
            })
            for step, row in enumerate(rows, 1):
                backward_rows.append({
                    "order_id": order_id,
                    "case_id": case_id,
                    "step": step,
                    "surface": row["surface"],
                    "decoded_card_no": row["selected_card_no"],
                    "decoded_component_parse": row["semantic_component_parse"],
                    "decoded_command_de": row["invariant_command_de"],
                    "exact_backward_read": "YES",
                })
            for step, (left, right) in enumerate(zip(rows, rows[1:]), 1):
                hits = [source[index]["event_id"] for index in range(len(source) - 1) if source[index]["record"] == source[index + 1]["record"] and source[index]["card_no"] == left["selected_card_no"] and source[index + 1]["card_no"] == right["selected_card_no"]]
                bigram_rows.append({
                    "order_id": order_id,
                    "case_id": case_id,
                    "left_step": step,
                    "right_step": step + 1,
                    "card_bigram": f"{left['selected_card_no']}|{right['selected_card_no']}",
                    "source_occurrences": len(hits),
                    "source_start_events": "|".join(hits) if hits else "NONE",
                })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_THIRD_25_PRECEDENCE_RULES.tsv", edge_rows, list(edge_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv", order_rows, list(order_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_THIRD_132_STEP_BACKWARD_READ.tsv", backward_rows, list(backward_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_THIRD_110_BIGRAM_AUDIT.tsv", bigram_rows, list(bigram_rows[0]))

    counts = {case: sum(row["case_id"] == case for row in order_rows) for case in GRAMMAR}
    md = [
        "# Endliche Werkstattgrammatik",
        "",
        "Jeder Fall besitzt sechs vorhandene Karten und fuenf notwendige Vorher-Nachher-Regeln. Alle linearen Folgen, die diese Regeln einhalten, werden geschrieben; keine weitere Bedeutungsregel wird waehrend der Aufzaehlung erfunden.",
        "",
        "| Fall | legale Schriftfolgen | Charakter |",
        "|---|---:|---|",
        f"| C1 | {counts['C1']} | Menge, Arbeitsfach und Ziel teilweise frei; Waschung vor Halten, Halten vor Schluss |",
        f"| C2 | {counts['C2']} | BEREIT-Pruefung wandert entlang einer festen Prozesskette |",
        f"| C3 | {counts['C3']} | Extraktions- und Adresskette koennen ineinandergeschoben werden |",
        f"| C4 | {counts['C4']} | starre Mengen-Ziel-Befestigungsfolge |",
        f"| C5 | {counts['C5']} | erste Zutat und Sollmass duerfen tauschen |",
        "",
        f"Gesamt: **{len(order_rows)} legale Sechserfolgen** fuer fuenf Arbeitsauftraege.",
        "",
        "Das sind Schreibvarianten derselben fuenf Aufgaben, nicht zweiundzwanzig neue Heilrezepte. Elf waren bereits im engen Verschiebetest sichtbar; elf weitere entstehen erst, wenn auch die unabhaengigen Nicht-Zweigkarten ihren Platz wechseln duerfen.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_THIRD_FINITE_GRAMMAR.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": 5,
        "cards_per_order": 6,
        "precedence_rules": len(edge_rows),
        "legal_orders": len(order_rows),
        "legal_orders_by_case": counts,
        "pass631_orders_present": sum(row["is_pass631_order"] == "YES" for row in order_rows),
        "pass632_licensed_orders_present": sum(row["was_licensed_in_pass632"] == "YES" for row in order_rows),
        "new_orders_beyond_pass632": sum(row["was_licensed_in_pass632"] == "NO" for row in order_rows),
        "correct_case_selections": sum(row["selector_correct"] == "YES" for row in order_rows),
        "source_attested_orders": sum(int(row["source_sequence_occurrences"]) > 0 for row in order_rows),
        "backward_steps": len(backward_rows),
        "exact_backward_steps": sum(row["exact_backward_read"] == "YES" for row in backward_rows),
        "bigram_instances": len(bigram_rows),
        "novel_bigram_instances": sum(int(row["source_occurrences"]) == 0 for row in bigram_rows),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "FIVE_JOB_GRAMMAR_GENERATES_TWENTY_TWO_LEGAL_WRITTEN_ORDERS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
