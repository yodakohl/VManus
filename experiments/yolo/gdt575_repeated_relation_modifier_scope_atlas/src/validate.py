#!/usr/bin/env python3
"""Independent source-level checks for GDT575."""

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
SOURCE = (
    ROOT
    / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts/"
    "gdt574_5122_action_count_event_edition.tsv"
)
STATUS = (
    "PASS_4609_RELATION_MODIFIER_SLOTS__96_DUPLICATE_GROUPS_IN_90_EVENTS__"
    "3_SAME_ROOT_ADJACENT__62_SAME_ROOT_INTERRUPTED__31_SURFACE_COLLISIONS__"
    "17_OUTER_INNER_PAIRS__ZERO_SCOPE_COLLAPSE"
)
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}

# Deliberately restated instead of importing the compiler.
FORMS = {
    "ADDRESS": ({"D_ADDR", "AM_ADDR", "A_ADDR", "D_LABEL", "LOCAL_CHAR_F", "M_LOCAL", "S_ADDR"}, ["an der bezeichneten Stelle"]),
    "E": ({"E"}, ["auf Grad I"]),
    "EE": ({"EE"}, ["auf Grad II"]),
    "EEE": ({"EEE"}, ["auf Grad III"]),
    "IIN": ({"IIN"}, ["auf der bezeichneten Stufe"]),
    "DA": ({"DA"}, ["auf der zweiten Stufe"]),
    "O": ({"O"}, ["als Ausführung", "zur Ausführung"]),
    "CARRIER_Q": ({"CARRIER_Q"}, ["als neuen Einsatz", "mit Beginnmarker"]),
    "CLASS": ({"AN", "HO"}, ["in der bezeichneten Klasse"]),
    "LOCAL_VARIANT": ({"LOCAL_CHAR_I", "LOCAL_CHAR_G", "G_LABEL", "LOCAL_CHAR_B", "LOCAL_CHAR_J"}, ["mit der lokalen Variante i", "mit der lokalen Variante"]),
    "AL": ({"AL"}, ["zur Zielspalte", "zur Zielstelle", "zur Zielposition", "zur Zielstation", "zum Zielgefäß"]),
    "AR": ({"AR"}, ["von der Ausgangszeile", "vom Ausgangsmaterial", "von der Ausgangsposition", "von der Ausgangsstation", "vom Ausgangsgefäß"]),
    "L": ({"L"}, ["über die Eintragsverbindung", "über die Verbindung im Pflanzenartikel", "über die Ringverbindung", "über die sichtbare Verbindung", "über die Gefäßverbindung"]),
    "AIR": ({"AIR"}, ["entlang der Lesebahn", "entlang der Verarbeitungsbahn", "entlang der Ringbahn", "entlang der Stationsbahn", "entlang der Transferbahn"]),
}
SCOPES = {"PLAIN": "", "OUTER": " im äußeren Zweig", "INNER": " im inneren Zweig"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_scan(rows: list[dict[str, str]]) -> dict[str, object]:
    candidates = []
    for key, (atoms, phrases) in FORMS.items():
        for phrase in phrases:
            for scope, suffix in SCOPES.items():
                candidates.append((phrase + suffix, phrase, key, scope, atoms))
    candidates.sort(key=lambda item: (-len(item[0]), item[0].casefold()))

    slots = Counter()
    forms = Counter()
    scopes = Counter()
    group_tops = Counter()
    groups = []
    duplicate_events = set()
    scope_pairs = []
    for row in rows:
        possible = []
        text = row["action_count_working_clause_de"]
        for full, base, key, scope, atoms in candidates:
            pattern = re.compile(r"(?<!\w)" + re.escape(full) + r"(?!\w)", re.IGNORECASE)
            for match in pattern.finditer(text):
                possible.append((match.start(), match.end(), full, base, key, scope, atoms))
        selected = []
        occupied = []
        for match in sorted(possible, key=lambda item: (item[0], -(item[1] - item[0]), item[2])):
            if any(not (match[1] <= left or match[0] >= right) for left, right in occupied):
                continue
            selected.append(match)
            occupied.append((match[0], match[1]))

        tokens = row["final_context_recipe"].split("+")
        keyed = defaultdict(list)
        for match in selected:
            keyed[match[4]].append(list(match))
            slots[match[4]] += 1
            forms[(match[4], match[3])] += 1
            scopes[match[5]] += 1
        for key, (atoms, _) in FORMS.items():
            positions = [index for index, token in enumerate(tokens) if token in atoms]
            matches = sorted(keyed[key], key=lambda item: item[0])
            if len(matches) != len(positions):
                raise AssertionError(f"Independent alignment failed at {row['event_id']} / {key}")
            for match, position in zip(matches, positions):
                match.extend([tokens[position], position])

        exact = defaultdict(list)
        for key_matches in keyed.values():
            for match in key_matches:
                exact[(match[3].casefold(), match[5])].append(match)
        local_group_count = 0
        for (base, scope), members in exact.items():
            if len(members) < 2:
                continue
            local_group_count += 1
            atoms = [member[7] for member in members]
            positions = [member[8] for member in members]
            identity = "SAME_ROOT" if len(set(atoms)) == 1 else "DIFFERENT_ROOTS"
            spacing = "RAW_ADJACENT" if all(b == a + 1 for a, b in zip(positions, positions[1:])) else "INTERRUPTED"
            topology = f"{identity}_{spacing}"
            group_tops[topology] += 1
            groups.append((row["event_id"], base, scope, tuple(atoms), tuple(positions), topology, len(members) - 1))
        if local_group_count:
            duplicate_events.add(row["event_id"])

        by_base_scope = defaultdict(list)
        for key_matches in keyed.values():
            for match in key_matches:
                by_base_scope[(match[3].casefold(), match[5])].append(match)
        for base in {match[3].casefold() for match in selected}:
            outer = by_base_scope[(base, "OUTER")]
            inner = by_base_scope[(base, "INNER")]
            if outer and inner:
                if len(outer) != 1 or len(inner) != 1 or outer[0][7] != inner[0][7]:
                    raise AssertionError(f"Independent scope-pair mismatch at {row['event_id']} / {base}")
                scope_pairs.append((row["event_id"], base, outer[0][7]))
    return {
        "slots": slots,
        "forms": forms,
        "scopes": scopes,
        "group_tops": group_tops,
        "groups": groups,
        "duplicate_events": duplicate_events,
        "scope_pairs": scope_pairs,
    }


def main() -> int:
    source = read_tsv(SOURCE)
    phrases = read_tsv(OUT / "gdt575_33_relation_modifier_phrase_cards.tsv")
    groups = read_tsv(OUT / "gdt575_96_exact_duplicate_phrase_groups.tsv")
    events = read_tsv(OUT / "gdt575_90_repeated_phrase_events.tsv")
    profiles = read_tsv(OUT / "gdt575_4_duplicate_topology_profiles.tsv")
    pairs = read_tsv(OUT / "gdt575_17_outer_inner_scope_pairs.tsv")
    result = json.loads((OUT / "gdt575_result.json").read_text(encoding="utf-8"))
    scan = independent_scan(source)
    source_by_id = {row["event_id"]: row for row in source}

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "expected": expected,
        })

    check("status", result["status"] == STATUS, result["status"], STATUS)
    check("source_rows", len(source) == 5122, len(source), 5122)
    check("phrase_rows", len(phrases) == 33, len(phrases), 33)
    check("group_rows", len(groups) == 96, len(groups), 96)
    check("event_rows", len(events) == 90, len(events), 90)
    check("profile_rows", len(profiles) == 4, len(profiles), 4)
    check("scope_pair_rows", len(pairs) == 17, len(pairs), 17)
    check("source_hash", sha256(SOURCE) == result["input_sha256"], sha256(SOURCE), result["input_sha256"])
    check("independent_slot_total", sum(scan["slots"].values()) == 4609, sum(scan["slots"].values()), 4609)
    check("artifact_slot_total", sum(int(row["occurrence_count"]) for row in phrases) == 4609, sum(int(row["occurrence_count"]) for row in phrases), 4609)
    check("plain_slots", scan["scopes"] == Counter({"PLAIN": 4575, "OUTER": 17, "INNER": 17}), dict(scan["scopes"]), {"PLAIN": 4575, "OUTER": 17, "INNER": 17})
    check("artifact_plain_slots", sum(int(row["plain_occurrence_count"]) for row in phrases) == 4575, sum(int(row["plain_occurrence_count"]) for row in phrases), 4575)
    check("artifact_outer_slots", sum(int(row["outer_occurrence_count"]) for row in phrases) == 17, sum(int(row["outer_occurrence_count"]) for row in phrases), 17)
    check("artifact_inner_slots", sum(int(row["inner_occurrence_count"]) for row in phrases) == 17, sum(int(row["inner_occurrence_count"]) for row in phrases), 17)
    check("independent_group_count", len(scan["groups"]) == 96, len(scan["groups"]), 96)
    check("independent_event_count", len(scan["duplicate_events"]) == 90, len(scan["duplicate_events"]), 90)
    check("independent_extra_mentions", sum(group[-1] for group in scan["groups"]) == 98, sum(group[-1] for group in scan["groups"]), 98)
    expected_tops = Counter({"SAME_ROOT_RAW_ADJACENT": 3, "SAME_ROOT_INTERRUPTED": 62, "DIFFERENT_ROOTS_RAW_ADJACENT": 13, "DIFFERENT_ROOTS_INTERRUPTED": 18})
    check("independent_topologies", scan["group_tops"] == expected_tops, dict(scan["group_tops"]), dict(expected_tops))
    check("artifact_topologies", Counter(row["duplicate_topology"] for row in groups) == expected_tops, dict(Counter(row["duplicate_topology"] for row in groups)), dict(expected_tops))
    check("scope_pairs_independent", len(scan["scope_pairs"]) == 17, len(scan["scope_pairs"]), 17)
    check("scope_pair_event_set", {row["event_id"] for row in pairs} == {row[0] for row in scan["scope_pairs"]}, len({row["event_id"] for row in pairs}), len({row[0] for row in scan["scope_pairs"]}))

    expected_phrase_counts = Counter({
        "an der bezeichneten stelle": 40,
        "auf grad i": 35,
        "als ausführung": 17,
        "auf grad ii": 1,
        "mit der lokalen variante": 1,
        "von der ausgangsstation": 1,
        "zur zielspalte": 1,
    })
    observed_phrase_counts = Counter(row["full_phrase_de"].casefold() for row in groups)
    check("duplicate_phrase_distribution", observed_phrase_counts == expected_phrase_counts, dict(observed_phrase_counts), dict(expected_phrase_counts))
    check("count_candidates", {row["event_id"] for row in groups if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"} == {"G407-E0152", "G407-E1846", "G515-E0379"}, sorted(row["event_id"] for row in groups if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"), ["G407-E0152", "G407-E1846", "G515-E0379"])
    check("event_ids_match", {row["event_id"] for row in events} == scan["duplicate_events"], len({row["event_id"] for row in events}), len(scan["duplicate_events"]))
    check("group_ids_unique", len({row["duplicate_group_id"] for row in groups}) == 96, len({row["duplicate_group_id"] for row in groups}), 96)
    check("phrase_ids_unique", len({row["phrase_card_id"] for row in phrases}) == 33, len({row["phrase_card_id"] for row in phrases}), 33)
    check("event_source_recipes", all(source_by_id[row["event_id"]]["final_context_recipe"] == row["final_context_recipe"] for row in events), "all" if all(source_by_id[row["event_id"]]["final_context_recipe"] == row["final_context_recipe"] for row in events) else "mismatch", "all")
    check("event_source_clauses", all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in events), "all" if all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in events) else "mismatch", "all")
    check("group_source_clauses", all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in groups), "all" if all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in groups) else "mismatch", "all")
    check("pair_source_clauses", all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in pairs), "all" if all(source_by_id[row["event_id"]]["action_count_working_clause_de"] == row["working_clause_de"] for row in pairs) else "mismatch", "all")
    check("group_atom_positions", all(all(source_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(pos)] == atom for pos, atom in zip(row["underlying_atom_positions_zero_based"].split("+"), row["underlying_atom_sequence"].split("+"))) for row in groups), "all", "all")
    check("pair_same_root", all(row["underlying_atom"] == source_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(row["outer_atom_position_zero_based"])] == source_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(row["inner_atom_position_zero_based"])] for row in pairs), "all", "all")
    check("pair_factorization_retains_scopes", all("im äußeren und im inneren Zweig" in row["scope_safe_factorization_de"] for row in pairs), "all", "all")
    check("no_third_level_relation_modifier", result["third_level_relation_modifier_slot_count"] == 0, result["third_level_relation_modifier_slot_count"], 0)
    check("no_new_pages", not any(row["physical_page"].startswith("f84") for row in groups + events + pairs), "none", "none")
    check("group_guards", all(row["guard"] == "EXACT_PHRASE_INVENTORY__NO_COMPRESSION_OR_ROOT_CHANGE" for row in groups), "all", "all")
    check("event_guards", all(row["guard"] == "EVENT_INVENTORY_ONLY__CLAUSE_BYTE_UNCHANGED" for row in events), "all", "all")
    check("pair_guards", all(row["guard"] == "BOTH_SCOPE_VALUES_RETAINED__NO_ROOT_OR_ORDER_CHANGE" for row in pairs), "all", "all")
    check("profile_sum", sum(int(row["duplicate_group_count"]) for row in profiles) == 96, sum(int(row["duplicate_group_count"]) for row in profiles), 96)
    check("result_group_count", result["duplicate_group_count"] == 96, result["duplicate_group_count"], 96)
    check("result_event_count", result["duplicate_event_count"] == 90, result["duplicate_event_count"], 90)
    check("result_extra_count", result["duplicate_extra_mention_count"] == 98, result["duplicate_extra_mention_count"], 98)
    check("result_scope_pair_count", result["outer_inner_scope_pair_count"] == 17, result["outer_inner_scope_pair_count"], 17)

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT575",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt575_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
