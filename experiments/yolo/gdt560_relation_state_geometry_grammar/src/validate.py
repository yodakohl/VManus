#!/usr/bin/env python3
"""Validate GDT560 relation geometry and deterministic artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt560_relation_state_geometry_grammar"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt560_validation.json"
INPUTS = {
    "gdt557_all_state_marker_occurrences.tsv": ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts/gdt557_all_state_marker_occurrences.tsv",
    "gdt429_13_nonaction_core_contrasts.tsv": ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_13_nonaction_core_contrasts.tsv",
}
ARTIFACTS = {
    "gdt560_216_relation_state_assignments.tsv": OUT / "gdt560_216_relation_state_assignments.tsv",
    "gdt560_4_relation_geometry_profiles.tsv": OUT / "gdt560_4_relation_geometry_profiles.tsv",
    "gdt560_8_relation_control_envelopes.tsv": OUT / "gdt560_8_relation_control_envelopes.tsv",
    "gdt560_28_relation_state_projections.tsv": OUT / "gdt560_28_relation_state_projections.tsv",
    "gdt560_44_relation_argument_state_projections.tsv": OUT / "gdt560_44_relation_argument_state_projections.tsv",
    "gdt560_12_multiroot_relation_families.tsv": OUT / "gdt560_12_multiroot_relation_families.tsv",
    "gdt560_6_relation_pair_bridges.tsv": OUT / "gdt560_6_relation_pair_bridges.tsv",
    "gdt560_16_explicit_argument_contacts.tsv": OUT / "gdt560_16_explicit_argument_contacts.tsv",
    "gdt560_2_post_dy_l_tails.tsv": OUT / "gdt560_2_post_dy_l_tails.tsv",
    "GDT560_RELATION_GEOMETRY_BOOK.md": OUT / "GDT560_RELATION_GEOMETRY_BOOK.md",
    "gdt560_result.json": OUT / "gdt560_result.json",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    state = read_tsv(INPUTS["gdt557_all_state_marker_occurrences.tsv"])
    contrasts = read_tsv(INPUTS["gdt429_13_nonaction_core_contrasts.tsv"])
    assignments = read_tsv(ARTIFACTS["gdt560_216_relation_state_assignments.tsv"])
    roots = read_tsv(ARTIFACTS["gdt560_4_relation_geometry_profiles.tsv"])
    envelopes = read_tsv(ARTIFACTS["gdt560_8_relation_control_envelopes.tsv"])
    projections = read_tsv(ARTIFACTS["gdt560_28_relation_state_projections.tsv"])
    rich = read_tsv(ARTIFACTS["gdt560_44_relation_argument_state_projections.tsv"])
    families = read_tsv(ARTIFACTS["gdt560_12_multiroot_relation_families.tsv"])
    pairs = read_tsv(ARTIFACTS["gdt560_6_relation_pair_bridges.tsv"])
    contacts = read_tsv(ARTIFACTS["gdt560_16_explicit_argument_contacts.tsv"])
    tails = read_tsv(ARTIFACTS["gdt560_2_post_dy_l_tails.tsv"])
    result = json.loads(ARTIFACTS["gdt560_result.json"].read_text(encoding="utf-8"))

    check("input_counts", (len(state), len(contrasts)) == (1870, 13), [len(state), len(contrasts)])
    source_pages = {row["physical_page"] for row in state}
    check("source_pages_exclude_f84", not any(page.startswith("f84") for page in source_pages), sorted(page for page in source_pages if page.startswith("f84")))
    check("source_event_deduplication", len({row["event_id"] for row in state}) == 1656, len({row["event_id"] for row in state}))
    observed_row_counts = [len(assignments), len(roots), len(envelopes), len(projections), len(rich), len(families), len(pairs), len(contacts), len(tails)]
    check("artifact_row_counts", observed_row_counts == [216, 4, 8, 28, 44, 12, 6, 16, 2], observed_row_counts)
    assignment_keys = {(row["event_id"], row["relation_occurrence_in_recipe"]) for row in assignments}
    check("assignment_keys_unique", len(assignment_keys) == 216, len(assignment_keys))
    check("assignment_ordinals", [int(row["assignment_ordinal"]) for row in assignments] == list(range(1, 217)), [assignments[0]["assignment_ordinal"], assignments[-1]["assignment_ordinal"]])
    root_counts = Counter(row["relation"] for row in assignments)
    check("relation_counts", root_counts == Counter({"L": 92, "AL": 60, "AR": 58, "AIR": 6}), root_counts)
    multiplicity = Counter(int(row["relation_multiplicity_in_recipe"]) for row in assignments)
    check("relation_multiplicity", multiplicity == Counter({1: 208, 2: 8}), multiplicity)
    event_multiplicity = {}
    for row in assignments:
        event_multiplicity[row["event_id"]] = int(row["relation_multiplicity_in_recipe"])
    check("selected_event_partition", len(event_multiplicity) == 212 and Counter(event_multiplicity.values()) == Counter({1: 208, 2: 4}), [len(event_multiplicity), Counter(event_multiplicity.values())])

    expected_envelopes = {
        "START>R<DY": (91, 19, 5, 64, 3),
        "OT>R<END": (62, 26, 34, 1, 1),
        "START>R<OL": (31, 4, 6, 21, 0),
        "OL>R<END": (26, 9, 11, 4, 2),
        "DY>R<END": (2, 0, 0, 2, 0),
        "OT>R<DY": (2, 1, 1, 0, 0),
        "OL>R<DY": (1, 1, 0, 0, 0),
        "OL>R<OL": (1, 0, 1, 0, 0),
    }
    observed_envelopes = {
        row["carrier_envelope"]: tuple(int(row[key]) for key in ("relation_occurrence_count", "al_count", "ar_count", "l_count", "air_count"))
        for row in envelopes
    }
    check("eight_envelopes_exact", observed_envelopes == expected_envelopes, observed_envelopes)
    check("all_assignments_have_defaults", all(row["compact_relation_reading_de"] and row["compact_relation_reading_de"] != "UNRESOLVED" for row in assignments), [])
    check("all_envelope_defaults_present", all(row["compact_template_de"] for row in envelopes), [])

    root_geometry = {
        row["relation"]: tuple(int(row[key]) for key in (
            "occurrence_count", "block_left_edge_count", "block_right_edge_count",
            "visible_right_action_count", "left_ot_or_ol_count", "right_dy_or_ol_count",
        )) for row in roots
    }
    expected_geometry = {
        "AL": (60, 45, 39, 10, 37, 25),
        "AR": (58, 35, 50, 2, 47, 13),
        "L": (92, 86, 33, 58, 5, 85),
        "AIR": (6, 2, 3, 0, 3, 3),
    }
    check("four_root_geometries_exact", root_geometry == expected_geometry, root_geometry)
    check("geometry_defaults_distinct", len({row["root_geometry_default"] for row in roots}) == 4, [row["root_geometry_default"] for row in roots])

    check("twenty_eight_state_projections", len(projections) == 28 and sum(int(row["event_count"]) for row in projections) == 212 and sum(int(row["relation_occurrence_count"]) for row in projections) == 216, [len(projections), sum(int(row["event_count"]) for row in projections), sum(int(row["relation_occurrence_count"]) for row in projections)])
    projection_map = {row["relation_state_projection"]: int(row["event_count"]) for row in projections}
    check("dominant_projection_counts", {key: projection_map[key] for key in ("L+DY", "OT+AR", "OT+AL", "L+OL", "AL+DY")} == {"L+DY": 64, "OT+AR": 33, "OT+AL": 25, "L+OL": 18, "AL+DY": 17}, {key: projection_map[key] for key in ("L+DY", "OT+AR", "OT+AL", "L+OL", "AL+DY")})
    check("forty_four_rich_projections", len(rich) == 44 and sum(int(row["event_count"]) for row in rich) == 212, [len(rich), sum(int(row["event_count"]) for row in rich)])
    check("all_projection_defaults_present", all(row["literal_working_reading_de"] for row in projections + rich), [])

    expected_families = {
        "REL+OL": (3, 18), "OT+REL": (2, 41), "REL+CHD+DY": (2, 40),
        "REL+DY": (2, 12), "REL+SH+E+DY": (2, 11), "OL+K+REL": (2, 4),
        "OL+REL": (2, 4), "OT+REL+Y": (2, 4), "REL+OL+Y": (2, 4),
        "OK+REL+DY": (2, 2), "OT+E+REL": (2, 2), "OT+REL+DY": (2, 2),
    }
    observed_families = {row["normalized_recipe"]: (int(row["relation_variant_count"]), int(row["event_count"])) for row in families}
    check("twelve_families_exact", observed_families == expected_families, observed_families)
    family_event_ids = {event_id for row in families for event_id in row["event_ids"].split("|")}
    check("family_event_coverage", len(family_event_ids) == 144 and sum(row["substitution_family_id"] == "NONE" for row in assignments) == 72, [len(family_event_ids), sum(row["substitution_family_id"] == "NONE" for row in assignments)])
    check("one_three_root_family", [(row["normalized_recipe"], row["relation_variants"]) for row in families if row["relation_variant_count"] == "3"] == [("REL+OL", "AL|AR|L")], [(row["normalized_recipe"], row["relation_variants"]) for row in families if row["relation_variant_count"] == "3"])
    check("air_absent_from_state_families", all("AIR" not in row["relation_variants"].split("|") for row in families), [])
    check("family_scope_fixed", all(row["scope_result"] == "RELATION_VALUE_SUBSTITUTES_WITHOUT_CHANGING_CONTROL_SCOPE" for row in families), [])

    pair_counts = {row["relation_pair"]: int(row["gdt560_state_family_count"]) for row in pairs}
    check("six_pair_bridge_counts", pair_counts == {"AL~AR": 8, "AL~L": 4, "AL~AIR": 0, "AR~L": 2, "AR~AIR": 0, "L~AIR": 0}, pair_counts)
    old_relation_pairs = {frozenset(row["contrast_pair"].split("~")) for row in contrasts if row["family"] == "RELATION"}
    new_relation_pairs = {frozenset(row["relation_pair"].split("~")) for row in pairs}
    check("gdt429_relation_crosswalk_complete", old_relation_pairs == new_relation_pairs and len(new_relation_pairs) == 6, [len(old_relation_pairs), len(new_relation_pairs)])
    check("air_pair_decisions", all(row["decision"] == "NO_STATE_SUBSTITUTION_BRIDGE__KEEP_AIR_SEPARATE" for row in pairs if "AIR" in row["relation_pair"]), [(row["relation_pair"], row["decision"]) for row in pairs if "AIR" in row["relation_pair"]])

    dy_family_rows = [row for row in families if row["contains_dy"] == "YES"]
    no_dy_family_rows = [row for row in families if row["contains_dy"] == "NO"]
    check("family_dy_scope_switch", sum(int(row["event_count"]) for row in dy_family_rows) == 67 and sum(int(row["statement_final_event_count"]) for row in dy_family_rows) == 67 and sum(int(row["event_count"]) for row in no_dy_family_rows) == 77 and sum(int(row["statement_final_event_count"]) for row in no_dy_family_rows) == 0, [sum(int(row["event_count"]) for row in dy_family_rows), sum(int(row["statement_final_event_count"]) for row in dy_family_rows), sum(int(row["event_count"]) for row in no_dy_family_rows), sum(int(row["statement_final_event_count"]) for row in no_dy_family_rows)])
    right_dy = [row for row in assignments if row["right_control"] == "DY"]
    check("all_right_dy_relations_close", len(right_dy) == 94 and sum(row["statement_final"] == "YES" for row in right_dy) == 94, [len(right_dy), sum(row["statement_final"] == "YES" for row in right_dy)])

    contact_directions = Counter(row["interpretation"] for row in contacts)
    check("sixteen_argument_contacts", contact_directions == Counter({"RELATION_PRECEDES_VISIBLE_ARGUMENT": 12, "RELATION_FOLLOWS_VISIBLE_ARGUMENT": 4}), contact_directions)
    check("argument_contact_defaults", all(row["literal_working_reading_de"] for row in contacts), [])
    tail_ids = [row["event_id"] for row in tails]
    check("two_post_dy_l_tails", tail_ids == ["G407-E2009", "G407-E2236"] and all(row["relation"] == "L" and row["statement_final"] == "YES" for row in tails), tail_ids)
    check("post_dy_written_order", all(row["written_order_reading_de"] == "ABSCHLIESSEN · VERBINDUNG" for row in tails), [row["written_order_reading_de"] for row in tails])

    expected_result = {
        "relation_state_event_count": 212, "relation_occurrence_count": 216,
        "carrier_envelope_count": 8, "relation_state_projection_count": 28,
        "relation_argument_state_projection_count": 44,
        "multiroot_relation_family_count": 12,
        "multiroot_family_event_count": 144,
        "air_state_substitution_family_count": 0,
        "dy_family_event_count": 67, "dy_family_statement_final_count": 67,
        "non_dy_family_event_count": 77, "non_dy_family_statement_final_count": 0,
        "right_dy_relation_occurrence_count": 94,
        "right_dy_relation_statement_final_count": 94,
        "explicit_argument_contact_count": 16,
        "post_dy_l_tail_count": 2,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("zero_scope_mutation", all(result.get(key) == 0 for key in ("new_pages", "recipe_changes", "root_meaning_changes", "statement_boundary_changes")), {key: result.get(key) for key in ("new_pages", "recipe_changes", "root_meaning_changes", "statement_boundary_changes")})
    book = ARTIFACTS["GDT560_RELATION_GEOMETRY_BOOK.md"].read_text(encoding="utf-8")
    check("book_contains_core_findings", all(needle in book for needle in ("AR ist der deutlichste rechte Ausgang", "86/92", "67/67", "Zwei sichtbare Nachschluss-Verbindungen", "Alle28 Relations-Steuerfolgen")), len(book))

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr)
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    payload = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
