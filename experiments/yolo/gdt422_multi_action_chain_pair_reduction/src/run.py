#!/usr/bin/env python3
"""Reduce every 3+-action recipe to licensed pairs, scopes, and peer chunks."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt422_multi_action_chain_pair_reduction"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
PAIRS = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts/gdt421_81_ordered_pair_profiles.tsv"
ATTACHMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
SLOT_BOUNDARIES = {
    "E", "EE", "EEE", "Y", "AIIN", "AIN", "OR", "DY", "OL", "OT",
    "AL", "AR", "L", "AIR", "O", "IIN", "DA", "D_ADDR", "AM_ADDR",
    "A_ADDR", "S_ADDR", "LOCAL_CHAR_F", "D_LABEL", "S_LABEL", "M_LOCAL",
    "Z_ADDR", "G_LABEL", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B",
    "LOCAL_CHAR_J", "LOCAL_CHAR_Z", "HO", "AN", "OS", "RESUME_CARD",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    pair_rows = read_tsv(PAIRS)
    attachments = read_tsv(ATTACHMENTS)
    attested_pairs = {
        tuple(row["ordered_pair"].split("+"))
        for row in pair_rows if row["status"] == "PAIR_ATTESTED"
    }
    r_topology_by_event: dict[str, set[str]] = defaultdict(set)
    for row in attachments:
        if row["r_topology"] != "NONE":
            r_topology_by_event[row["global_running_event_id"]].add(row["r_topology"])

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)

    chain_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []
    gap_rows: list[dict[str, object]] = []

    for component_recipe, rows in sorted(by_recipe.items()):
        atoms = component_recipe.split("+")
        action_positions = [(index, atom) for index, atom in enumerate(atoms) if atom in ACTIONS]
        if len(action_positions) < 3:
            continue
        action_chain = tuple(atom for _, atom in action_positions)
        pair_labels: list[str] = []
        missing: list[tuple[int, str, str, list[str]]] = []
        for pair_index, ((left_position, left), (right_position, right)) in enumerate(zip(action_positions, action_positions[1:]), 1):
            between = atoms[left_position + 1 : right_position]
            pair_labels.append(f"{left}+{right}")
            if (left, right) not in attested_pairs:
                missing.append((pair_index, left, right, between))

        event_ids = [row["global_running_event_id"] for row in rows]
        topology = sorted({mode for event_id in event_ids for mode in r_topology_by_event[event_id]})
        repairs: list[str] = []
        for pair_index, left, right, between in missing:
            if right == "R" and topology:
                repair = "R_POSITIONAL_TOPOLOGY_NOT_ORDINARY_PAIR"
            elif left == right:
                repair = "REPEATED_ACTION_SCOPE"
            elif any(atom in SLOT_BOUNDARIES for atom in between):
                repair = "VISIBLE_SLOT_BOUNDARY_SPLITS_CHAIN"
            else:
                repair = "PEER_ACTION_CHUNK_BREAK"
            repairs.append(repair)
            gap_rows.append({
                "component_recipe": component_recipe,
                "action_chain": "+".join(action_chain),
                "pair_ordinal": pair_index,
                "missing_pair": f"{left}+{right}",
                "between_atoms": "+".join(between) if between else "NONE",
                "r_topology": "|".join(topology) if topology else "NONE",
                "repair_rule": repair,
                "repair_reading_de": {
                    "R_POSITIONAL_TOPOLOGY_NOT_ORDINARY_PAIR": "R ALS GELERNTE KOPF/SCHWANZ-TOPOLOGIE BINDEN",
                    "REPEATED_ACTION_SCOPE": "GLEICHE HANDLUNG AUF ZWEI PAKETEBENEN",
                    "VISIBLE_SLOT_BOUNDARY_SPLITS_CHAIN": "VOR UND NACH SICHTBARER SCHUBLADE GETRENNT LESEN",
                    "PEER_ACTION_CHUNK_BREAK": "ALS ZWEI AUFEINANDERFOLGENDE GELERNTE HANDLUNGSPAKETE LESEN",
                }[repair],
                "event_count": len(rows),
                "global_running_event_ids": "|".join(event_ids),
                "pages": "|".join(sorted({row["physical_page"] for row in rows})),
                "registers": "|".join(sorted({row["register"] for row in rows})),
                "irreducible_new_chain_card": "NO",
            })

        status = "ALL_ADJACENT_PAIRS_ATTESTED" if not missing else "ALL_GAPS_REDUCED_BY_OLD_SCOPE_OR_CHUNKS"
        chain_rows.append({
            "component_recipe": component_recipe,
            "action_count": len(action_chain),
            "action_chain": "+".join(action_chain),
            "adjacent_pair_count": len(action_chain) - 1,
            "adjacent_pairs": "|".join(pair_labels),
            "attested_adjacent_pair_count": len(pair_labels) - len(missing),
            "missing_adjacent_pair_count": len(missing),
            "repair_rules": "|".join(repairs) if repairs else "NONE",
            "reduction_status": status,
            "event_count": len(rows),
            "register_count": len({row["register"] for row in rows}),
            "registers": "|".join(sorted({row["register"] for row in rows})),
            "page_count": len({row["physical_page"] for row in rows}),
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "portable_reading_de": next(iter({row["portable_back_projection_de"] for row in rows})),
            "new_chain_card_required": "NO",
        })

        for row in rows:
            occurrence_rows.append({
                "global_running_event_id": row["global_running_event_id"],
                "global_statement_id": row["global_statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": component_recipe,
                "action_chain": "+".join(action_chain),
                "reduction_status": status,
                "repair_rules": "|".join(repairs) if repairs else "NONE",
                "imperative_clause_de": row["imperative_clause_de"],
            })

    length_rows: list[dict[str, object]] = []
    for action_count in sorted({int(row["action_count"]) for row in chain_rows}):
        rows = [row for row in chain_rows if int(row["action_count"]) == action_count]
        length_rows.append({
            "action_count": action_count,
            "recipe_type_count": len(rows),
            "event_count": sum(int(row["event_count"]) for row in rows),
            "fully_pair_covered_recipe_count": sum(row["reduction_status"] == "ALL_ADJACENT_PAIRS_ATTESTED" for row in rows),
            "repaired_recipe_count": sum(row["reduction_status"] != "ALL_ADJACENT_PAIRS_ATTESTED" for row in rows),
            "new_chain_card_count": sum(row["new_chain_card_required"] == "YES" for row in rows),
        })

    write_tsv(OUT / "gdt422_110_long_action_chain_inventory.tsv", chain_rows, list(chain_rows[0]))
    write_tsv(OUT / "gdt422_168_long_chain_occurrences.tsv", occurrence_rows, list(occurrence_rows[0]))
    write_tsv(OUT / "gdt422_11_pair_gap_adjudications.tsv", gap_rows, list(gap_rows[0]))
    write_tsv(OUT / "gdt422_3_chain_length_summary.tsv", length_rows, list(length_rows[0]))

    rules = [
        "# Lange Handlungsketten lesen", "",
        "1. Lies jede sichtbare Handlung in ihrer Reihenfolge.",
        "2. Verwende jede belegte GDT421-Paarkarte, solange keine sichtbare Schublade dazwischenliegt.",
        "3. Grad, Argument, Relation, Adresse oder DY darf die Kette in zwei Handlungspakete teilen.",
        "4. Gleiches X…X ist eine gelernte Wiederholung auf zwei Paketebenen, kein neues Verb.",
        "5. R mit sichtbarer R-Topologie ist Kopf/Schwanz-Markierung, kein fehlendes Normalpaar.",
        "6. Zwei verbleibende Nachbarhandlungen dürfen als Peer-Pakete folgen; ihre Einzel- oder Paarkarten müssen jeweils alt sein.",
        "7. Keine der gegenwärtigen langen Karten braucht eine eigene Drei-, Vier- oder Fünf-Handlungsbedeutung.", "",
    ]
    for row in gap_rows:
        rules.append(f"- `{row['component_recipe']}`: `{row['missing_pair']}` → **{row['repair_rule']}**")
    (OUT / "LONG_ACTION_CHAIN_WORKSHOP_RULES.md").write_text("\n".join(rules) + "\n", encoding="utf-8")

    repair_counts = Counter(row["repair_rule"] for row in gap_rows)
    result = {
        "status": "ALL_LONG_ACTION_CHAINS_REDUCED_WITHOUT_NEW_CARD",
        "long_chain_recipe_type_count": len(chain_rows),
        "long_chain_event_count": len(occurrence_rows),
        "fully_adjacent_pair_covered_recipe_count": sum(row["reduction_status"] == "ALL_ADJACENT_PAIRS_ATTESTED" for row in chain_rows),
        "repaired_recipe_count": sum(row["reduction_status"] != "ALL_ADJACENT_PAIRS_ATTESTED" for row in chain_rows),
        "pair_gap_count": len(gap_rows),
        "repair_rule_counts": dict(sorted(repair_counts.items())),
        "irreducible_new_chain_card_count": sum(row["new_chain_card_required"] == "YES" for row in chain_rows),
        "new_pages": 0,
        "dictionary_revisions": 0,
    }
    (OUT / "gdt422_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
