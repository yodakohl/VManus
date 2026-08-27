#!/usr/bin/env python3
"""Independent validation for GDT573's reversible argument anaphors."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt573_intra_clause_argument_pronoun_voice"
OUT = BASE / "artifacts"
G572 = ROOT / "experiments/yolo/gdt572_complete_nonstate_bracket_voice/artifacts"
INPUTS = {
    "events": G572 / "gdt572_5122_bracket_free_event_edition.tsv",
    "statements": G572 / "gdt572_793_bracket_free_statement_edition.tsv",
    "pages": G572 / "gdt572_30_page_bracket_voice_profiles.tsv",
    "argument_forms": G572 / "gdt572_20_nonstate_carried_argument_forms.tsv",
}
ARTIFACTS = {
    "cards": OUT / "gdt573_22_anaphor_voice_cards.tsv",
    "topologies": OUT / "gdt573_8_repeat_topology_profiles.tsv",
    "assignments": OUT / "gdt573_1043_anaphor_replacements.tsv",
    "changes": OUT / "gdt573_841_pronominalized_clauses.tsv",
    "events": OUT / "gdt573_5122_pronoun_voice_event_edition.tsv",
    "statements": OUT / "gdt573_793_pronoun_voice_statement_edition.tsv",
    "pages": OUT / "gdt573_30_page_pronoun_voice_profiles.tsv",
    "book": OUT / "GDT573_PRONOUN_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt573_result.json",
}
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ROOTS = ("Y", "AIIN", "AIN", "OR")
ANAPHOR_RE = re.compile(r"\b(?:ihn|sie|beide)\b")
BRACKET_RE = re.compile(r"\[[^\]]+\]")
STATUS = (
    "PASS_22_ANAPHOR_CARDS__854_REPEAT_GROUPS__1046_LATER_ARGUMENT_MENTIONS_"
    "COVERED_BY_1043_ANAPHORS__841_CLAUSES__5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matches(text: str, phrase: str) -> list[re.Match[str]]:
    return list(re.finditer(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    source_forms = read_tsv(INPUTS["argument_forms"])
    cards = read_tsv(ARTIFACTS["cards"])
    topologies = read_tsv(ARTIFACTS["topologies"])
    assignments = read_tsv(ARTIFACTS["assignments"])
    changes = read_tsv(ARTIFACTS["changes"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_events), len(source_statements), len(source_pages), len(source_forms)] == [5122, 793, 30, 20])
    check("artifact_counts", [len(cards), len(topologies), len(assignments), len(changes), len(events), len(statements), len(pages)] == [22, 8, 1043, 841, 5122, 793, 30])
    sealed_hits = sorted({row.get("physical_page", "").lower() for table in (events, statements, pages) for row in table if row.get("physical_page", "").lower() in {"f84", "f84r"}})
    check("sealed_pages_absent", not sealed_hits, sealed_hits)
    check("source_has_no_anaphor_tokens", not any(ANAPHOR_RE.search(row["bracket_free_working_clause_de"]) for row in source_events))
    check("source_is_bracket_free", not any(BRACKET_RE.search(row["bracket_free_working_clause_de"]) for row in source_events))
    check("anaphor_ordinals", [int(row["anaphor_ordinal"]) for row in assignments] == list(range(1, 1044)))
    check("change_ordinals", [int(row["change_ordinal"]) for row in changes] == list(range(1, 842)))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    form_by_key = {(row["register"], row["argument_root"]): row for row in source_forms}
    expected_keys = {(register, root) for register in REGISTERS for root in ROOTS}
    check("twenty_owner_root_forms", set(form_by_key) == expected_keys)
    variants: dict[str, list[dict[str, str]]] = defaultdict(list)
    expected_card_core: list[tuple[str, str, str, str, str, str, str]] = []
    for ordinal, key in enumerate([(register, root) for register in REGISTERS for root in ROOTS], 1):
        register, root = key
        row = form_by_key[key]
        pronoun = "sie" if row["explicit_argument_phrase_de"].startswith("die ") else "ihn"
        card_id = f"GDT573-P{ordinal:02d}"
        expected_card_core.append((card_id, register, root, "SINGLE_ARGUMENT", row["explicit_argument_phrase_de"], row["carried_argument_phrase_de"], pronoun))
        for form_class, phrase in (("EXPLICIT", row["explicit_argument_phrase_de"]), ("CARRIED", row["carried_argument_phrase_de"])):
            variants[register].append({"root": root, "scope": "SINGLE_ARGUMENT", "class": form_class, "phrase": phrase, "anaphor": pronoun, "card": card_id})
    expected_card_core.extend([
        ("GDT573-P21", "CELESTIAL", "Y|Y", "PAIRED_ARGUMENT", "die beiden Positionsposten", "NOT_APPLICABLE", "sie"),
        ("GDT573-P22", "HERBAL", "TWO_DISTINCT_MASCULINE_ROOTS", "COORDINATED_ARGUMENTS", "maskuline Argumentform 1 und maskuline Argumentform 2", "NOT_APPLICABLE", "beide"),
    ])
    variants["CELESTIAL"].append({"root": "Y|Y", "scope": "PAIRED_ARGUMENT", "class": "PAIRED", "phrase": "die beiden Positionsposten", "anaphor": "sie", "card": "GDT573-P21"})
    actual_card_core = [(row["pronoun_card_id"], row["register"], row["argument_root"], row["argument_scope"], row["explicit_argument_phrase_de"], row["carried_argument_phrase_de"], row["pronoun_de"]) for row in cards]
    check("twenty_two_card_cores_exact", actual_card_core == expected_card_core)
    check("all_cards_used", all(int(row["covered_later_argument_mention_count"]) > 0 and int(row["surface_anaphor_occurrence_count"]) > 0 for row in cards))

    expected_targets: dict[str, str] = {}
    expected_expansions: dict[str, str] = {}
    expected_assignment_core: list[tuple[object, ...]] = []
    expected_changed_ids: list[str] = []
    expected_group_counts: Counter[str] = Counter()
    topology_counts: Counter[tuple[str, int]] = Counter()
    topology_replacements: Counter[tuple[str, int]] = Counter()
    group_ordinal = mention_ordinal = anaphor_ordinal = 0
    source_class_coverage: Counter[str] = Counter()
    anaphor_counts: Counter[str] = Counter()
    card_coverage: Counter[str] = Counter()
    card_surfaces: Counter[str] = Counter()

    for source in source_events:
        event_id = source["event_id"]
        clause = source["bracket_free_working_clause_de"]
        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        spans: list[tuple[int, int]] = []
        for variant in variants[source["register"]]:
            for match in matches(clause, variant["phrase"]):
                grouped[(variant["root"], variant["scope"])].append({
                    "start": match.start(), "end": match.end(), "class": variant["class"],
                    "phrase": variant["phrase"], "anaphor": variant["anaphor"], "card": variant["card"],
                    "root": variant["root"], "scope": variant["scope"],
                })
                spans.append((match.start(), match.end()))
        spans.sort()
        check_overlap = any(left[1] > right[0] for left, right in zip(spans, spans[1:]))
        if check_overlap:
            raise RuntimeError(f"Independent overlap at {event_id}")

        raw: list[dict[str, object]] = []
        ordered_groups = sorted(grouped.items(), key=lambda item: min(int(hit["start"]) for hit in item[1]))
        for _, occurrences in ordered_groups:
            occurrences.sort(key=lambda hit: int(hit["start"]))
            if len(occurrences) < 2:
                continue
            if len({hit["class"] for hit in occurrences}) != 1 or len({hit["card"] for hit in occurrences}) != 1:
                raise RuntimeError(f"Independent mixed realization at {event_id}")
            group_ordinal += 1
            expected_group_counts[event_id] += 1
            key = (str(occurrences[0]["class"]), len(occurrences))
            topology_counts[key] += 1
            topology_replacements[key] += len(occurrences) - 1
            for local_ordinal, occurrence in enumerate(occurrences[1:], 2):
                mention_ordinal += 1
                item = {**occurrence, "mention_id": mention_ordinal, "group_id": group_ordinal, "local_ordinal": local_ordinal, "local_count": len(occurrences), "covered": 1}
                raw.append(item)
                card_coverage[str(item["card"])] += 1

        raw.sort(key=lambda item: int(item["start"]))
        if len(raw) == 2 and expected_group_counts[event_id] == 2 and all(item["anaphor"] == "ihn" for item in raw):
            left, right = raw
            if clause[int(left["end"]) : int(right["start"])] != " und ":
                raise RuntimeError(f"Independent coordinate failure at {event_id}")
            surface = [{
                "start": left["start"], "end": right["end"], "class": "EXPLICIT_COORDINATE",
                "phrase": clause[int(left["start"]) : int(right["end"])], "anaphor": "beide", "card": "GDT573-P22",
                "root": f"{left['root']}|{right['root']}", "scope": "COORDINATED_DISTINCT_ARGUMENTS",
                "mention_ids": f"{left['mention_id']}|{right['mention_id']}", "group_ids": f"{left['group_id']}|{right['group_id']}",
                "local_ordinal": "2|2", "local_count": "2|2", "covered": 2,
            }]
            card_coverage["GDT573-P22"] += 2
        else:
            surface = []
            for item in raw:
                surface.append({**item, "mention_ids": item["mention_id"], "group_ids": item["group_id"]})

        pieces: list[str] = []
        cursor = target_cursor = 0
        for item in surface:
            anaphor_ordinal += 1
            prefix = clause[cursor : int(item["start"])]
            pieces.append(prefix)
            target_cursor += len(prefix)
            target_start = target_cursor
            pieces.append(str(item["anaphor"]))
            target_cursor += len(str(item["anaphor"]))
            target_end = target_cursor
            cursor = int(item["end"])
            anaphor_counts[str(item["anaphor"])] += 1
            card_surfaces[str(item["card"])] += 1
            covered = int(item["covered"])
            source_class_coverage["EXPLICIT" if item["class"] == "EXPLICIT_COORDINATE" else str(item["class"])] += covered
            expected_assignment_core.append((
                anaphor_ordinal, str(item["mention_ids"]), str(item["group_ids"]), event_id,
                str(item["root"]), str(item["scope"]), str(item["class"]), str(item["card"]),
                str(item["local_ordinal"]), str(item["local_count"]), covered,
                int(item["start"]), int(item["end"]), target_start, target_end, str(item["phrase"]), str(item["anaphor"]),
            ))
        pieces.append(clause[cursor:])
        target = "".join(pieces)
        target_hits = list(ANAPHOR_RE.finditer(target))
        if len(target_hits) != len(surface):
            raise RuntimeError(f"Independent anaphor count at {event_id}")
        expansion_parts: list[str] = []
        cursor = 0
        for hit, item in zip(target_hits, surface):
            expansion_parts.extend([target[cursor : hit.start()], str(item["phrase"])])
            cursor = hit.end()
        expansion_parts.append(target[cursor:])
        expansion = "".join(expansion_parts)
        if expansion != clause:
            raise RuntimeError(f"Independent roundtrip at {event_id}")
        expected_targets[event_id] = target
        expected_expansions[event_id] = expansion
        if surface:
            expected_changed_ids.append(event_id)

    check("repeat_group_total", group_ordinal == 854, group_ordinal)
    check("covered_mention_total", mention_ordinal == 1046, mention_ordinal)
    check("surface_anaphor_total", anaphor_ordinal == 1043, anaphor_ordinal)
    check("changed_event_total", len(expected_changed_ids) == 841, len(expected_changed_ids))
    check("eight_topologies", len(topology_counts) == 8, {f"{key[0]}|{key[1]}": value for key, value in topology_counts.items()})
    check("anaphor_partition", anaphor_counts == Counter({"ihn": 949, "sie": 91, "beide": 3}), dict(anaphor_counts))
    check("source_class_coverage", source_class_coverage == Counter({"EXPLICIT": 688, "CARRIED": 355, "PAIRED": 3}), dict(source_class_coverage))

    actual_assignment_core = [(
        int(row["anaphor_ordinal"]), row["covered_argument_mention_ordinals"], row["repeat_group_ordinal"], row["event_id"],
        row["argument_root"], row["argument_scope"], row["source_form_class"], row["pronoun_card_id"],
        row["mention_ordinal_for_argument"], row["mention_count_for_argument"], int(row["covered_argument_mention_count"]),
        int(row["source_start_char"]), int(row["source_end_char"]), int(row["target_start_char"]), int(row["target_end_char"]),
        row["source_argument_phrase_de"], row["pronoun_de"],
    ) for row in assignments]
    check("all_1043_assignments_exact", actual_assignment_core == expected_assignment_core)
    check("assignment_coverage_sum", sum(int(row["covered_argument_mention_count"]) for row in assignments) == 1046)
    check("three_beide_coordinates", [row["event_id"] for row in assignments if row["pronoun_de"] == "beide"] == ["G407-E4419", "G407-E4456", "G515-E0253"])

    source_event_by_id = {row["event_id"]: row for row in source_events}
    event_errors: list[str] = []
    for row in events:
        source = source_event_by_id[row["event_id"]]
        changed = row["event_id"] in set(expected_changed_ids)
        if (
            row["gdt572_bracket_free_clause_de"] != source["bracket_free_working_clause_de"]
            or row["pronoun_voice_working_clause_de"] != expected_targets[row["event_id"]]
            or row["full_argument_expansion_de"] != expected_expansions[row["event_id"]]
            or row["pronoun_voice_changed"] != ("YES" if changed else "NO")
            or int(row["remaining_bracket_count"]) != 0
        ):
            event_errors.append(row["event_id"])
    check("all_5122_events_exact", not event_errors, event_errors[:10])
    check("event_order_exact", [row["event_id"] for row in events] == [row["event_id"] for row in source_events])
    check("all_5122_expansions_exact", all(row["full_argument_expansion_de"] == row["gdt572_bracket_free_clause_de"] for row in events))
    check("changed_ids_exact", [row["event_id"] for row in changes] == expected_changed_ids)
    check("change_text_exact", all(row["before_clause_de"] == source_event_by_id[row["event_id"]]["bracket_free_working_clause_de"] and row["after_clause_de"] == expected_targets[row["event_id"]] and row["full_argument_expansion_de"] == row["before_clause_de"] for row in changes))
    check("state_nonstate_partition", Counter(source_event_by_id[event_id]["state_status"] for event_id in expected_changed_ids) == Counter({"NONSTATE_CARD": 679, "STATE_CARD": 162}))
    check("no_ambiguous_ihn_and_ihn", not any("ihn und ihn" in row["pronoun_voice_working_clause_de"] for row in events))
    check("zero_residual_exact_owner_repeats", all(sum(len(matches(row["pronoun_voice_working_clause_de"], form_by_key[(row["register"], root)][column])) > 1 for root in ROOTS for column in ("explicit_argument_phrase_de", "carried_argument_phrase_de")) == 0 for row in events))
    check("paired_boundary_not_singular_false_hit", expected_targets["G407-E1058"] == "Weiter: nimm die beiden Positionsposten auf und ordne sie zu und nimm sie auf und ordne sie zu.")
    check("outer_inner_wording_retained", sum(row["pronoun_voice_working_clause_de"].count("äußer") + row["pronoun_voice_working_clause_de"].count("inner") for row in events) == sum(row["gdt572_bracket_free_clause_de"].count("äußer") + row["gdt572_bracket_free_clause_de"].count("inner") for row in events))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors: list[str] = []
    changed_statement_ids: set[str] = set()
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        local = events_by_statement[row["statement_id"]]
        before = " ".join(item["gdt572_bracket_free_clause_de"] for item in local)
        after = " ".join(item["pronoun_voice_working_clause_de"] for item in local)
        expansion = " ".join(item["full_argument_expansion_de"] for item in local)
        changed_count = sum(item["pronoun_voice_changed"] == "YES" for item in local)
        if changed_count:
            changed_statement_ids.add(row["statement_id"])
        if before != source["bracket_free_working_reading_de"] or row["gdt572_bracket_free_reading_de"] != before or row["pronoun_voice_working_reading_de"] != after or row["full_argument_expansion_de"] != expansion or expansion != before or int(row["changed_event_count"]) != changed_count:
            statement_errors.append(row["statement_id"])
    check("all_793_statements_exact", not statement_errors, statement_errors[:10])
    check("statement_order_exact", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements])
    check("changed_statement_count", len(changed_statement_ids) == 363, len(changed_statement_ids))

    changed_pages = {source_event_by_id[event_id]["physical_page"] for event_id in expected_changed_ids}
    check("page_order_exact", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("changed_page_count", len(changed_pages) == 28, sorted(changed_pages))
    check("page_anaphor_total", sum(int(row["anaphor_occurrence_count"]) for row in pages) == 1043)
    check("page_mention_total", sum(int(row["covered_later_argument_mention_count"]) for row in pages) == 1046)
    check("zero_running_pages_retained", {row["physical_page"] for row in pages if int(row["event_count"]) == 0} == {"f69v", "f70v"})

    expected_topology = {(row["source_form_class"], int(row["full_mention_count"])): (int(row["repeat_group_count"]), int(row["replacement_occurrence_count"])) for row in topologies}
    check("topology_counts_exact", expected_topology == {key: (topology_counts[key], topology_replacements[key]) for key in topology_counts})
    card_by_id = {row["pronoun_card_id"]: row for row in cards}
    check("card_coverage_exact", all(int(card_by_id[card_id]["covered_later_argument_mention_count"]) == count for card_id, count in card_coverage.items()))
    check("card_surface_exact", all(int(card_by_id[card_id]["surface_anaphor_occurrence_count"]) == count for card_id, count in card_surfaces.items()))

    expected_metrics = {
        "pronoun_voice_card_count": 22,
        "single_argument_card_count": 20,
        "paired_argument_card_count": 1,
        "coordinate_argument_card_count": 1,
        "repeat_topology_count": 8,
        "repeat_argument_group_count": 854,
        "covered_later_argument_mention_count": 1046,
        "surface_anaphor_occurrence_count": 1043,
        "masculine_pronoun_count": 949,
        "feminine_or_plural_pronoun_count": 91,
        "coordinate_pronoun_count": 3,
        "explicit_source_mention_count": 688,
        "carried_source_mention_count": 355,
        "paired_source_mention_count": 3,
        "changed_event_count": 841,
        "unchanged_event_count": 4281,
        "changed_state_event_count": 162,
        "changed_nonstate_event_count": 679,
        "changed_statement_count": 363,
        "changed_physical_page_count": 28,
        "exact_event_expansion_count": 5122,
        "remaining_bracket_occurrence_count": 0,
        "complete_event_count": 5122,
        "complete_statement_count": 793,
        "complete_page_count": 30,
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
    }
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_metrics_exact", result.get("metrics") == expected_metrics, result.get("metrics"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()})
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    check("book_metrics_present", "changed clauses: 841 · covered later mentions: 1046 · anaphors: 1043 · exact expansions: 5122" in book)
    check("book_all_pages_once", all(book.count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(line[:1].isdigit() and ". " in line for line in book.splitlines()) == 793)
    check("book_bracket_free", not BRACKET_RE.search(book))

    pre_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    run = subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    post_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    check("deterministic_replay_exit", run.returncode == 0, run.stderr[-1000:])
    check("deterministic_artifact_hashes", pre_hashes == post_hashes, {name: (pre_hashes[name], post_hashes[name]) for name in pre_hashes if pre_hashes[name] != post_hashes[name]})
    check("deterministic_result_object", json.loads(ARTIFACTS["result"].read_text(encoding="utf-8")) == result)

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    (OUT / "gdt573_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
