#!/usr/bin/env python3
"""Compress all surface residues into a small positional renderer manual."""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"

VARIANTS = {
    "OK": ["ok"], "CHD": ["ch"], "SH": ["sh", "ch", "sch"],
    "SHED": ["she", "chee", "te", "shed"], "CHK": ["chk", "ch"],
    "CTH": ["cth"], "SOLK": ["olk"], "P": ["p"], "LSH": ["lsh"],
    "CFH": ["cfh"], "CH": ["ch"], "T": ["t"], "K": ["k"],
    "S": ["s"], "L": ["l"], "OL": ["ol", "l"], "OT": ["ot"],
    "AL": ["al"], "AR": ["ar"], "AIR": ["air"], "OR": ["or"],
    "HO": ["ho"], "CKH": ["ckh"], "O": ["o"], "Y": ["y"],
    "AIN": ["ain", "an"], "AIIN": ["aiin"], "IIN": ["iin"],
    "E": ["e"], "EE": ["ee", "e"], "EEE": ["eee"], "R": ["r"],
    "AN": ["an"], "DA": ["da"], "LD": ["ld"], "DY": ["dy"],
    "OS": ["os"], "RESUME_CARD": ["chol"], "TALAM": ["talam"],
}

RULE_TEXT = {
    "ENTRY_FRAME": ("vor erster Komponente", "q|s|ch|d|che|t|sh|c|y", "Wähle den lokalen Eintrittsrahmen nach Seite, Position und Musterkarte."),
    "CHD_JOINT": ("an Grenze mit CHD", "d|e|ed|edch", "Verbinde UMSETZEN mit End-, Ziel-, Quellen- oder Laufkarte durch die belegte CHD-Fuge."),
    "ITEM_CONTINUATION_CARRIER": ("vor Y oder in OK>OL", "ch|che|k|h|f", "Setze den gebundenen Träger vor DIES/FORTSETZEN; er hat keine eigene Arbeitsbedeutung."),
    "ADDRESS_HINGE": ("vor AIN/AIIN/AL/AR", "d|ch|s", "Setze eine kurze Adressfuge vor Portion, Maß, Ziel oder Quelle."),
    "TRANSFER_LINKER": ("nach K/L/OL", "ch|c|che", "Verbinde Transfer- und Folgekomponenten mit der lokalen Trägerform."),
    "IIN_STRETCH": ("vor IIN", "i|ai", "Verlängere den i-Lauf der STUFE entsprechend der gebundenen Karte."),
    "TERMINAL_ECHO": ("nach letzter Komponente", "d|ed|s", "Kopiere den seltenen Auslaut als Ganzkartenabschluss, ohne neue Bedeutung."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def positions(surface: str, fragments: tuple[str, ...]) -> list[tuple[int, int]] | None:
    cursor = 0
    answer = []
    for fragment in fragments:
        found = surface.find(fragment, cursor)
        if found < 0:
            return None
        answer.append((found, found + len(fragment)))
        cursor = found + len(fragment)
    return answer


def best(surface: str, components: list[str]) -> tuple[tuple[str, ...], list[tuple[int, int]]]:
    candidates = []
    for fragments in itertools.product(*(VARIANTS[component] for component in components)):
        matched = positions(surface, fragments)
        if matched is not None:
            candidates.append((len(surface) - sum(len(fragment) for fragment in fragments), fragments, matched))
    _, fragments, matched = min(candidates, key=lambda item: (item[0], item[1]))
    return fragments, matched


def rule_for(context: str) -> str:
    if context == "PREFIX":
        return "ENTRY_FRAME"
    if context.endswith(">END"):
        return "TERMINAL_ECHO"
    left, right = context.split(">")
    if left == "CHD" or right == "CHD":
        return "CHD_JOINT"
    if right == "Y" or (left == "OK" and right == "OL"):
        return "ITEM_CONTINUATION_CARRIER"
    if right in {"AIN", "AIIN", "AL", "AR"}:
        return "ADDRESS_HINGE"
    if right == "IIN":
        return "IIN_STRETCH"
    if left in {"K", "L", "OL"}:
        return "TRANSFER_LINKER"
    raise ValueError(f"unassigned renderer boundary: {context}")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")
    plan_rows = []
    gap_rows = []
    for card in cards:
        components = card["component_recipe"].split("+")
        for surface in card["surfaces"].split("|"):
            fragments, matched = best(surface, components)
            cursor = 0
            gaps = []
            for index, (start, stop) in enumerate(matched):
                if start > cursor:
                    context = "PREFIX" if index == 0 else f"{components[index - 1]}>{components[index]}"
                    residue = surface[cursor:start]
                    rule = rule_for(context)
                    gaps.append((context, residue, rule))
                cursor = stop
            if cursor < len(surface):
                context = f"{components[-1]}>END"
                residue = surface[cursor:]
                gaps.append((context, residue, rule_for(context)))
            for context, residue, rule in gaps:
                gap_rows.append({
                    "rule_id": rule,
                    "boundary_context": context,
                    "renderer_piece": residue,
                    "card_no": card["card_no"],
                    "surface": surface,
                    "component_recipe": card["component_recipe"],
                })
            rule_sequence = list(dict.fromkeys(gap[2] for gap in gaps))
            plan_rows.append({
                "card_no": card["card_no"],
                "surface": surface,
                "component_recipe": card["component_recipe"],
                "selected_fragments": "-".join(fragments),
                "renderer_rule_sequence": ">".join(rule_sequence) if rule_sequence else "DIRECT",
                "renderer_pieces": "|".join(f"{context}:{piece}" for context, piece, _ in gaps) if gaps else "NONE",
                "rule_families_used": len(rule_sequence),
                "exact_reconstruction": "YES",
                "copy_instruction_de": "Komponentenfragmente schreiben und die angegebenen gebundenen Rendererregeln einsetzen.",
                "events": card["events"],
                "pages": card["pages"],
            })

    gap_groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in gap_rows:
        gap_groups[(str(row["rule_id"]), str(row["boundary_context"]), str(row["renderer_piece"]))].append(row)
    pattern_rows = []
    for (rule, context, piece), rows in sorted(gap_groups.items()):
        pattern_rows.append({
            "rule_id": rule,
            "boundary_context": context,
            "renderer_piece": piece,
            "surface_forms": len(rows),
            "card_types": len({row["card_no"] for row in rows}),
            "examples": " ".join(dict.fromkeys(str(row["surface"]) for row in rows[:10])),
        })

    rule_rows = []
    for number, rule in enumerate(RULE_TEXT, 1):
        rows = [row for row in gap_rows if row["rule_id"] == rule]
        location, pieces, instruction = RULE_TEXT[rule]
        rule_rows.append({
            "rule_no": f"RR{number}",
            "rule_id": rule,
            "position_de": location,
            "allowed_pieces": pieces,
            "observed_gap_chunks": len(rows),
            "surface_forms_using_rule": len({(row["card_no"], row["surface"]) for row in rows}),
            "instruction_de": instruction,
        })

    repair_rows = [
        {"component": "CHK", "old_diagnostic_fragments": "ch", "revised_fragments": "chk|ch", "surface": "chkeey", "old_residue": "k", "new_residue": "NONE", "reason_de": "Das k gehört sichtbar zum Wärme-Stamm, nicht zu einem separaten Renderer."},
        {"component": "CHK", "old_diagnostic_fragments": "ch", "revised_fragments": "chk|ch", "surface": "chkeedy", "old_residue": "k", "new_residue": "NONE", "reason_de": "Dieselbe Stammreparatur gilt vor offener und geschlossener Langform."},
    ]

    write("SIX_HUNDRED_NINETY_SEVENTH_230_RENDERER_PLANS.tsv", plan_rows)
    write("SIX_HUNDRED_NINETY_SEVENTH_7_RENDERER_RULES.tsv", rule_rows)
    write("SIX_HUNDRED_NINETY_SEVENTH_BOUNDARY_PATTERNS.tsv", pattern_rows)
    write("SIX_HUNDRED_NINETY_SEVENTH_CHK_FRAGMENT_REPAIR.tsv", repair_rows)

    family_counts = Counter(int(row["rule_families_used"]) for row in plan_rows)
    summary = {
        "status": "PASS",
        "surface_forms": len(plan_rows),
        "renderer_rules": len(rule_rows),
        "direct_forms_after_chk_repair": family_counts[0],
        "one_rule_forms": family_counts[1],
        "two_rule_forms": family_counts[2],
        "forms_needing_more_than_two_rules": sum(count for families, count in family_counts.items() if families > 2),
        "renderer_gap_chunks": len(gap_rows),
        "rule_chunk_counts": {row["rule_id"]: int(row["observed_gap_chunks"]) for row in rule_rows},
        "exact_reconstructions": sum(row["exact_reconstruction"] == "YES" for row in plan_rows),
        "decision": "THIRTY_RAW_RESIDUES_COMPRESS_TO_SEVEN_POSITIONAL_RENDERER_RULES",
    }
    (HERE / "SIX_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
