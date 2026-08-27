#!/usr/bin/env python3
"""Inventory every repeated relation/modifier phrase in the GDT574 edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas"
OUT = BASE / "artifacts"
INPUT = (
    ROOT
    / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts/"
    "gdt574_5122_action_count_event_edition.tsv"
)
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
STATUS = (
    "PASS_4609_RELATION_MODIFIER_SLOTS__96_DUPLICATE_GROUPS_IN_90_EVENTS__"
    "3_SAME_ROOT_ADJACENT__62_SAME_ROOT_INTERRUPTED__31_SURFACE_COLLISIONS__"
    "17_OUTER_INNER_PAIRS__ZERO_SCOPE_COLLAPSE"
)


# Every member is a short renderer already present in the current edition. The
# alternate voice forms remain under one atom key.
PHRASE_SPECS: dict[str, dict[str, object]] = {
    "ADDRESS": {
        "atoms": {"D_ADDR", "AM_ADDR", "A_ADDR", "D_LABEL", "LOCAL_CHAR_F", "M_LOCAL", "S_ADDR"},
        "class": "LOCAL_ADDRESS",
        "phrases": ["an der bezeichneten Stelle"],
    },
    "E": {"atoms": {"E"}, "class": "GRADE", "phrases": ["auf Grad I"]},
    "EE": {"atoms": {"EE"}, "class": "GRADE", "phrases": ["auf Grad II"]},
    "EEE": {"atoms": {"EEE"}, "class": "GRADE", "phrases": ["auf Grad III"]},
    "IIN": {"atoms": {"IIN"}, "class": "STAGE", "phrases": ["auf der bezeichneten Stufe"]},
    "DA": {"atoms": {"DA"}, "class": "STAGE", "phrases": ["auf der zweiten Stufe"]},
    "O": {"atoms": {"O"}, "class": "FORMAL_CONTROL", "phrases": ["als Ausführung", "zur Ausführung"]},
    "CARRIER_Q": {
        "atoms": {"CARRIER_Q"},
        "class": "FORMAL_CONTROL",
        "phrases": ["als neuen Einsatz", "mit Beginnmarker"],
    },
    "CLASS": {
        "atoms": {"AN", "HO"},
        "class": "LOCAL_CLASS",
        "phrases": ["in der bezeichneten Klasse"],
    },
    "LOCAL_VARIANT": {
        "atoms": {"LOCAL_CHAR_I", "LOCAL_CHAR_G", "G_LABEL", "LOCAL_CHAR_B", "LOCAL_CHAR_J"},
        "class": "LOCAL_VARIANT",
        "phrases": ["mit der lokalen Variante i", "mit der lokalen Variante"],
    },
    "AL": {
        "atoms": {"AL"},
        "class": "RELATION",
        "phrases": ["zur Zielspalte", "zur Zielstelle", "zur Zielposition", "zur Zielstation", "zum Zielgefäß"],
    },
    "AR": {
        "atoms": {"AR"},
        "class": "RELATION",
        "phrases": [
            "von der Ausgangszeile", "vom Ausgangsmaterial", "von der Ausgangsposition",
            "von der Ausgangsstation", "vom Ausgangsgefäß",
        ],
    },
    "L": {
        "atoms": {"L"},
        "class": "RELATION",
        "phrases": [
            "über die Eintragsverbindung", "über die Verbindung im Pflanzenartikel",
            "über die Ringverbindung", "über die sichtbare Verbindung", "über die Gefäßverbindung",
        ],
    },
    "AIR": {
        "atoms": {"AIR"},
        "class": "RELATION",
        "phrases": [
            "entlang der Lesebahn", "entlang der Verarbeitungsbahn", "entlang der Ringbahn",
            "entlang der Stationsbahn", "entlang der Transferbahn",
        ],
    },
}
SCOPE_SUFFIXES = {
    "PLAIN": "",
    "OUTER": " im äußeren Zweig",
    "INNER": " im inneren Zweig",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phrase_id(key: str, phrase: str) -> str:
    spec = PHRASE_SPECS[key]
    index = list(spec["phrases"]).index(phrase) + 1
    return f"GDT575-P-{key}-{index:02d}"


def compiled_candidates() -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for key, spec in PHRASE_SPECS.items():
        for phrase in spec["phrases"]:
            for scope, suffix in SCOPE_SUFFIXES.items():
                candidates.append({
                    "alignment_key": key,
                    "phrase": str(phrase),
                    "phrase_id": phrase_id(key, str(phrase)),
                    "scope": scope,
                    "full_phrase": str(phrase) + suffix,
                })
    return sorted(candidates, key=lambda row: (-len(row["full_phrase"]), row["full_phrase"].casefold()))


def match_row(row: dict[str, str], candidates: list[dict[str, str]]) -> list[dict[str, object]]:
    text = row["action_count_working_clause_de"]
    possible: list[dict[str, object]] = []
    for candidate in candidates:
        pattern = re.compile(
            r"(?<!\w)" + re.escape(candidate["full_phrase"]) + r"(?!\w)",
            flags=re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            possible.append({**candidate, "start": match.start(), "end": match.end(), "surface": match.group()})

    # A scoped phrase also contains its unscoped base. Longest-first selection
    # makes those one slot and prevents Grad I from leaking into Grad II/III.
    selected: list[dict[str, object]] = []
    occupied: list[tuple[int, int]] = []
    for match in sorted(
        possible,
        key=lambda item: (
            int(item["start"]),
            -(int(item["end"]) - int(item["start"])),
            str(item["full_phrase"]),
        ),
    ):
        span = (int(match["start"]), int(match["end"]))
        if any(not (span[1] <= left or span[0] >= right) for left, right in occupied):
            continue
        selected.append(match)
        occupied.append(span)

    tokens = row["final_context_recipe"].split("+")
    by_key: dict[str, list[dict[str, object]]] = defaultdict(list)
    for match in selected:
        by_key[str(match["alignment_key"])].append(match)
    for key, spec in PHRASE_SPECS.items():
        positions = [index for index, token in enumerate(tokens) if token in spec["atoms"]]
        matches = sorted(by_key[key], key=lambda item: int(item["start"]))
        if len(matches) != len(positions):
            raise RuntimeError(
                f"Phrase/atom alignment drift at {row['event_id']} for {key}: "
                f"{len(matches)} phrases versus {len(positions)} atoms"
            )
        for match, position in zip(matches, positions):
            match["atom"] = tokens[position]
            match["atom_position"] = position
    return sorted(selected, key=lambda item: int(item["start"]))


def group_topology(tokens: list[str], matches: list[dict[str, object]]) -> tuple[str, str, str]:
    positions = [int(match["atom_position"]) for match in matches]
    atoms = [str(match["atom"]) for match in matches]
    same_root = len(set(atoms)) == 1
    adjacent = all(right == left + 1 for left, right in zip(positions, positions[1:]))
    identity = "SAME_ROOT" if same_root else "DIFFERENT_ROOTS"
    spacing = "RAW_ADJACENT" if adjacent else "INTERRUPTED"
    gaps = []
    for left, right in zip(positions, positions[1:]):
        between = tokens[left + 1:right]
        gaps.append("+".join(between) or "NONE")
    return f"{identity}_{spacing}", "|".join(gaps), "+".join(atoms)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_tsv(INPUT)
    if len(rows) != 5122:
        raise RuntimeError(f"Expected 5,122 GDT574 events, found {len(rows)}")
    candidates = compiled_candidates()
    phrase_occurrences: Counter[str] = Counter()
    phrase_events: dict[str, set[str]] = defaultdict(set)
    phrase_scopes: Counter[tuple[str, str]] = Counter()
    duplicate_by_phrase: Counter[str] = Counter()
    duplicate_extra_by_phrase: Counter[str] = Counter()
    group_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    scope_pair_rows: list[dict[str, object]] = []

    for row in rows:
        matches = match_row(row, candidates)
        for match in matches:
            pid = str(match["phrase_id"])
            phrase_occurrences[pid] += 1
            phrase_events[pid].add(row["event_id"])
            phrase_scopes[(pid, str(match["scope"]))] += 1

        exact_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        base_scope_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for match in matches:
            exact_groups[(str(match["phrase_id"]), str(match["scope"]))].append(match)
            base_scope_groups[(str(match["phrase_id"]), str(match["scope"]))].append(match)
        duplicate_groups = [(key, members) for key, members in exact_groups.items() if len(members) > 1]

        event_classes: list[str] = []
        event_phrases: list[str] = []
        event_group_ids: list[str] = []
        for (pid, scope), members in duplicate_groups:
            key = str(members[0]["alignment_key"])
            tokens = row["final_context_recipe"].split("+")
            topology, gaps, atoms = group_topology(tokens, members)
            group_id = f"GDT575-D{len(group_rows) + 1:03d}"
            recommendation = {
                "SAME_ROOT_RAW_ADJACENT": "COUNT_VOICE_CANDIDATE",
                "SAME_ROOT_INTERRUPTED": "KEEP_ORDER_AND_RESTORE_LOCAL_ATTACHMENT",
                "DIFFERENT_ROOTS_RAW_ADJACENT": "DIFFERENTIATE_ROOT_VOICE_BEFORE_COMPRESSION",
                "DIFFERENT_ROOTS_INTERRUPTED": "DIFFERENTIATE_ROOT_VOICE_AND_KEEP_ORDER",
            }[topology]
            positions = [int(member["atom_position"]) for member in members]
            group_rows.append({
                "duplicate_group_ordinal": len(group_rows) + 1,
                "duplicate_group_id": group_id,
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "surface": row["surface"],
                "final_context_recipe": row["final_context_recipe"],
                "phrase_card_id": pid,
                "alignment_key": key,
                "full_phrase_de": members[0]["full_phrase"],
                "scope": scope,
                "phrase_occurrence_count": len(members),
                "extra_mention_count": len(members) - 1,
                "underlying_atom_sequence": atoms,
                "underlying_atom_positions_zero_based": "+".join(str(position) for position in positions),
                "intervening_atom_sequences": gaps,
                "duplicate_topology": topology,
                "action_atom_between": "YES" if any(
                    token in ACTIONS
                    for left, right in zip(positions, positions[1:])
                    for token in tokens[left + 1:right]
                ) else "NO",
                "recommended_treatment": recommendation,
                "working_clause_de": row["action_count_working_clause_de"],
                "guard": "EXACT_PHRASE_INVENTORY__NO_COMPRESSION_OR_ROOT_CHANGE",
            })
            duplicate_by_phrase[pid] += 1
            duplicate_extra_by_phrase[pid] += len(members) - 1
            event_classes.append(topology)
            event_phrases.append(str(members[0]["full_phrase"]))
            event_group_ids.append(group_id)

        if duplicate_groups:
            event_rows.append({
                "repeated_event_ordinal": len(event_rows) + 1,
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "surface": row["surface"],
                "final_context_recipe": row["final_context_recipe"],
                "duplicate_group_ids": "|".join(event_group_ids),
                "duplicate_full_phrases_de": "|".join(event_phrases),
                "duplicate_topologies": "|".join(event_classes),
                "duplicate_group_count": len(duplicate_groups),
                "extra_mention_count": sum(len(members) - 1 for _, members in duplicate_groups),
                "working_clause_de": row["action_count_working_clause_de"],
                "guard": "EVENT_INVENTORY_ONLY__CLAUSE_BYTE_UNCHANGED",
            })

        # Outer and inner are distinct full phrases. Their common base can be
        # coordinated later without deleting either scope value.
        for pid in sorted({str(match["phrase_id"]) for match in matches}):
            outer = base_scope_groups.get((pid, "OUTER"), [])
            inner = base_scope_groups.get((pid, "INNER"), [])
            if not outer or not inner:
                continue
            if len(outer) != 1 or len(inner) != 1:
                raise RuntimeError(f"Unexpected repeated outer/inner scope at {row['event_id']} / {pid}")
            pair = sorted([outer[0], inner[0]], key=lambda match: int(match["atom_position"]))
            if pair[0]["atom"] != pair[1]["atom"]:
                raise RuntimeError(f"Outer/inner root mismatch at {row['event_id']} / {pid}")
            base_phrase = str(pair[0]["phrase"])
            scope_pair_rows.append({
                "scope_pair_ordinal": len(scope_pair_rows) + 1,
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "surface": row["surface"],
                "final_context_recipe": row["final_context_recipe"],
                "phrase_card_id": pid,
                "alignment_key": pair[0]["alignment_key"],
                "underlying_atom": pair[0]["atom"],
                "outer_atom_position_zero_based": outer[0]["atom_position"],
                "inner_atom_position_zero_based": inner[0]["atom_position"],
                "source_outer_phrase_de": str(outer[0]["full_phrase"]),
                "source_inner_phrase_de": str(inner[0]["full_phrase"]),
                "scope_safe_factorization_de": f"{base_phrase} im äußeren und im inneren Zweig",
                "working_clause_de": row["action_count_working_clause_de"],
                "guard": "BOTH_SCOPE_VALUES_RETAINED__NO_ROOT_OR_ORDER_CHANGE",
            })

    phrase_rows: list[dict[str, object]] = []
    for key, spec in PHRASE_SPECS.items():
        for phrase in spec["phrases"]:
            pid = phrase_id(key, str(phrase))
            phrase_rows.append({
                "phrase_card_ordinal": len(phrase_rows) + 1,
                "phrase_card_id": pid,
                "alignment_key": key,
                "phrase_class": spec["class"],
                "eligible_atoms": "+".join(sorted(spec["atoms"])),
                "base_phrase_de": phrase,
                "occurrence_count": phrase_occurrences[pid],
                "event_count": len(phrase_events[pid]),
                "plain_occurrence_count": phrase_scopes[(pid, "PLAIN")],
                "outer_occurrence_count": phrase_scopes[(pid, "OUTER")],
                "inner_occurrence_count": phrase_scopes[(pid, "INNER")],
                "duplicate_group_count": duplicate_by_phrase[pid],
                "duplicate_extra_mention_count": duplicate_extra_by_phrase[pid],
                "guard": "CURRENT_GERMAN_VOICE_CARD__NO_LEXEME_CLAIM",
            })

    topology_counts = Counter(str(row["duplicate_topology"]) for row in group_rows)
    treatment_rows = []
    treatment_descriptions = {
        "SAME_ROOT_RAW_ADJACENT": "same atom repeated without an intervening raw slot; bounded count candidate",
        "SAME_ROOT_INTERRUPTED": "same atom repeated around other slots; keep order and test local attachment",
        "DIFFERENT_ROOTS_RAW_ADJACENT": "different atoms collide in German voice even though adjacent",
        "DIFFERENT_ROOTS_INTERRUPTED": "different atoms collide in German voice and are interrupted",
    }
    for topology, description in treatment_descriptions.items():
        members = [row for row in group_rows if row["duplicate_topology"] == topology]
        treatment_rows.append({
            "topology_profile_ordinal": len(treatment_rows) + 1,
            "duplicate_topology": topology,
            "duplicate_group_count": len(members),
            "event_count": len({str(row["event_id"]) for row in members}),
            "extra_mention_count": sum(int(row["extra_mention_count"]) for row in members),
            "description": description,
            "example_event_ids": "|".join(dict.fromkeys(str(row["event_id"]) for row in members[:8])) or "NONE",
            "guard": "TOPOLOGY_PROFILE_ONLY__NO_AUTOMATIC_COMPRESSION",
        })

    if len(phrase_rows) != 33:
        raise RuntimeError(f"Expected 33 current phrase forms, found {len(phrase_rows)}")
    if sum(int(row["occurrence_count"]) for row in phrase_rows) != 4609:
        raise RuntimeError("Relation/modifier slot coverage drift")
    if (len(group_rows), len(event_rows), sum(int(row["extra_mention_count"]) for row in group_rows)) != (96, 90, 98):
        raise RuntimeError("Repeated phrase inventory drift")
    if topology_counts != Counter({
        "SAME_ROOT_RAW_ADJACENT": 3,
        "SAME_ROOT_INTERRUPTED": 62,
        "DIFFERENT_ROOTS_RAW_ADJACENT": 13,
        "DIFFERENT_ROOTS_INTERRUPTED": 18,
    }):
        raise RuntimeError(f"Duplicate topology drift: {topology_counts}")
    if len(scope_pair_rows) != 17:
        raise RuntimeError(f"Expected 17 outer/inner pairs, found {len(scope_pair_rows)}")

    write_tsv(OUT / "gdt575_33_relation_modifier_phrase_cards.tsv", phrase_rows)
    write_tsv(OUT / "gdt575_96_exact_duplicate_phrase_groups.tsv", group_rows)
    write_tsv(OUT / "gdt575_90_repeated_phrase_events.tsv", event_rows)
    write_tsv(OUT / "gdt575_4_duplicate_topology_profiles.tsv", treatment_rows)
    write_tsv(OUT / "gdt575_17_outer_inner_scope_pairs.tsv", scope_pair_rows)

    phrase_group_counts = Counter(str(row["full_phrase_de"]).casefold() for row in group_rows)
    result = {
        "experiment_id": "GDT575",
        "status": STATUS,
        "input_event_count": len(rows),
        "relation_modifier_slot_count": sum(int(row["occurrence_count"]) for row in phrase_rows),
        "plain_slot_count": sum(int(row["plain_occurrence_count"]) for row in phrase_rows),
        "outer_slot_count": sum(int(row["outer_occurrence_count"]) for row in phrase_rows),
        "inner_slot_count": sum(int(row["inner_occurrence_count"]) for row in phrase_rows),
        "third_level_relation_modifier_slot_count": 0,
        "phrase_form_count": len(phrase_rows),
        "duplicate_event_count": len(event_rows),
        "duplicate_group_count": len(group_rows),
        "duplicate_extra_mention_count": sum(int(row["extra_mention_count"]) for row in group_rows),
        "same_root_raw_adjacent_group_count": topology_counts["SAME_ROOT_RAW_ADJACENT"],
        "same_root_interrupted_group_count": topology_counts["SAME_ROOT_INTERRUPTED"],
        "different_root_raw_adjacent_group_count": topology_counts["DIFFERENT_ROOTS_RAW_ADJACENT"],
        "different_root_interrupted_group_count": topology_counts["DIFFERENT_ROOTS_INTERRUPTED"],
        "outer_inner_scope_pair_count": len(scope_pair_rows),
        "duplicate_phrase_group_counts": dict(sorted(phrase_group_counts.items())),
        "count_candidate_event_ids": [
            str(row["event_id"]) for row in group_rows
            if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"
        ],
        "input_sha256": sha256(INPUT),
        "claim_ceiling": (
            "Complete inventory of repeated current German relation/modifier voice. "
            "It licenses no compression by itself and changes no clause, atom, root, recipe, page or scope."
        ),
    }
    (OUT / "gdt575_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    atlas = [
        "# GDT575 repeated relation/modifier scope atlas",
        "",
        f"Status: `{STATUS}`.",
        "",
        "All 4,609 current relation/modifier slots are covered: 4,575 plain, 17 outer and 17 inner. "
        "The exact-phrase scan finds 96 duplicate groups in 90 events, containing 98 mentions after the first.",
        "",
        "Only three groups are both the same underlying root and raw-adjacent:",
        "",
    ]
    for row in group_rows:
        if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT":
            atlas.append(f"- `{row['event_id']}` `{row['underlying_atom_sequence']}` — {row['full_phrase_de']}")
    atlas.extend([
        "",
        "The other 62 same-root groups are interrupted, and 31 groups are German surface collisions "
        "between different underlying atoms. They stay explicit. The 17 outer/inner pairs are not duplicates: "
        "both scope values must survive any later coordination.",
        "",
        "This artifact is an inventory, not a rewritten edition. GDT574 remains the complete readable source.",
    ])
    (OUT / "GDT575_REPEAT_SCOPE_ATLAS.md").write_text("\n".join(atlas) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
