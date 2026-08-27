#!/usr/bin/env python3
"""Validate GDT515's guarded source, complete defaults and 30-page decks."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission"
ART = BASE / "artifacts"
ZL3B = ROOT / "transcription/voynich_zl3b_lines.tsv"
G405 = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"

SELECTED = {"f31r", "f66r", "f20v", "f4r"}
SOURCE_COLUMNS = (
    "page,page_order,locus,line_number,code,relation,kind,subtype,section,"
    "language,hand,quire,folio_type,paragraph_start,paragraph_end,token_count,eva_clean"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source = read_tsv(ART / "gdt515_122_guarded_source_lines.tsv")
    events = read_tsv(ART / "gdt515_597_complete_event_edition.tsv")
    surfaces = read_tsv(ART / "gdt515_377_surface_dictionary.tsv")
    running_absent = read_tsv(ART / "gdt515_169_running_absent_surface_audit.tsv")
    genuinely_new = read_tsv(ART / "gdt515_159_genuinely_new_surface_audit.tsv")
    labels = read_tsv(ART / "gdt515_51_f66r_label_sign_edition.tsv")
    statements = read_tsv(ART / "gdt515_prose_statement_edition.tsv")
    attachments = read_tsv(ART / "gdt515_factorized_attachments.tsv")
    sensitivity = read_tsv(ART / "gdt515_amber_close_sensitivity.tsv")
    pages = read_tsv(ART / "gdt515_4_page_summary.tsv")
    expectations = read_tsv(ART / "gdt515_5_expectation_scorecard.tsv")
    running30 = read_tsv(ART / "gdt515_5122_running_event_edition.tsv")
    local30 = read_tsv(ART / "gdt515_744_local_group_edition.tsv")
    unified30 = read_tsv(ART / "gdt515_5866_unified_group_ledger.tsv")
    pages30 = read_tsv(ART / "gdt515_30_page_summary.tsv")
    dictionary_rows = read_tsv(
        G413 / "gdt413_46_component_working_dictionary.tsv",
    )
    lock_rows = read_tsv(G405 / "gdt405_426_locked_surface_dictionary.tsv")
    old_running = read_tsv(G407 / "gdt407_4576_running_event_edition.tsv")
    result = json.loads((ART / "gdt515_result.json").read_text(encoding="utf-8"))

    expected_counts = {
        "source": 122, "events": 597, "surfaces": 377,
        "running_absent": 169, "genuinely_new": 159, "labels": 51,
        "pages": 4, "expectations": 5, "running30": 5122,
        "local30": 744, "unified30": 5866, "pages30": 30,
    }
    actual_counts = {
        "source": len(source), "events": len(events), "surfaces": len(surfaces),
        "running_absent": len(running_absent),
        "genuinely_new": len(genuinely_new), "labels": len(labels),
        "pages": len(pages), "expectations": len(expectations),
        "running30": len(running30), "local30": len(local30),
        "unified30": len(unified30), "pages30": len(pages30),
    }
    check("artifact_row_counts", actual_counts == expected_counts, str(actual_counts))

    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(ZL3B),
        "--selector", "page",
    ]
    for page in ("f31r", "f66r", "f20v", "f4r"):
        command.extend(("--allow", page))
    command.extend(("--forbid-prefix", "f84", "--columns", SOURCE_COLUMNS))
    queried = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=True,
    )
    lines = [
        line for line in queried.stdout.splitlines()
        if not line.startswith("GUARD_STATS ")
    ]
    query_rows = list(
        csv.DictReader(io.StringIO("\n".join(lines) + "\n"), delimiter="\t"),
    )
    check("guarded_source_replay", query_rows == source, f"rows={len(query_rows)}")
    check(
        "selected_page_set",
        {row["page"] for row in source} == SELECTED,
        "|".join(sorted({row["page"] for row in source})),
    )
    check(
        "forbidden_page_absent",
        not any(row["page"].startswith("f84") for row in source),
        "no f84 selector materialised",
    )

    source_tokens = [
        token for row in source for token in row["eva_clean"].split()
    ]
    check(
        "source_event_exactness",
        source_tokens == [row["surface"] for row in events],
        f"tokens={len(source_tokens)}",
    )
    check(
        "event_ids_unique",
        len({row["event_id"] for row in events}) == len(events),
        f"ids={len({row['event_id'] for row in events})}",
    )
    check(
        "all_events_have_recipe_and_default",
        all(row["visible_recipe"] and row["default_working_reading_de"] for row in events),
        f"complete={sum(bool(row['visible_recipe'] and row['default_working_reading_de']) for row in events)}",
    )
    check(
        "no_portable_retune_or_word_promotion",
        all(
            row["new_portable_atom_count"] == "0"
            and row["portable_meaning_changed"] == "NO"
            and row["structural_tag_promoted_to_word"] == "NO"
            for row in events
        ),
        "597/597 preserve the component dictionary and structural tags",
    )

    recipe_sets: dict[str, set[str]] = defaultdict(set)
    for row in events:
        recipe_sets[row["surface"]].add(row["visible_recipe"])
    check(
        "one_selected_surface_one_recipe",
        len(recipe_sets) == 377 and all(len(values) == 1 for values in recipe_sets.values()),
        f"surfaces={len(recipe_sets)} collisions={sum(len(v) > 1 for v in recipe_sets.values())}",
    )
    check(
        "surface_dictionary_exact",
        {row["surface"]: row["visible_recipe"] for row in surfaces}
        == {surface: next(iter(values)) for surface, values in recipe_sets.items()},
        "377 selected surfaces represented once",
    )

    lock = {row["surface"]: row["locked_recipe"] for row in lock_rows}
    lock_events = [row for row in events if row["surface"] in lock]
    lock_mismatches = [
        row for row in lock_events if row["visible_recipe"] != lock[row["surface"]]
    ]
    check(
        "gdt405_lock_replay",
        len(lock_events) == 276 and not lock_mismatches,
        f"contacts={len(lock_events)} mismatches={len(lock_mismatches)}",
    )

    running_recipes: dict[str, set[str]] = defaultdict(set)
    for row in old_running:
        running_recipes[row["surface"]].add(row["component_recipe"])
    exact_running = [row for row in events if row["surface"] in running_recipes]
    check(
        "old_running_recipe_replay",
        len(exact_running) == 416
        and all(
            row["visible_recipe"] in running_recipes[row["surface"]]
            for row in exact_running
        ),
        f"contacts={len(exact_running)}",
    )

    dictionary_atoms = {row["atom"] for row in dictionary_rows}
    local_atoms = {"LOCAL_NAME_CORE_X", "LOCAL_SIGN_X", "LOCAL_SIGN_C"}
    used_atoms = {
        atom for row in events for atom in row["visible_recipe"].split("+")
    }
    check(
        "atom_inventory_bounded",
        used_atoms <= dictionary_atoms | local_atoms,
        f"used={len(used_atoms)} outside46={sorted(used_atoms - dictionary_atoms)}",
    )
    local_atom_surfaces = defaultdict(set)
    for row in events:
        for atom in row["visible_recipe"].split("+"):
            if atom in local_atoms:
                local_atom_surfaces[atom].add(row["surface"])
    check(
        "local_opaque_atoms_scoped",
        dict(local_atom_surfaces) == {
            "LOCAL_NAME_CORE_X": {"axor", "chxar"},
            "LOCAL_SIGN_X": {"x"},
            "LOCAL_SIGN_C": {"c"},
        },
        json.dumps(
            {
                atom: sorted(surfaces)
                for atom, surfaces in sorted(local_atom_surfaces.items())
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )

    prose = [row for row in events if row["source_kind"] == "P"]
    local = [row for row in events if row["source_kind"] == "L"]
    check(
        "prose_local_split",
        len(prose) == 546 and len(local) == 51 and labels == local,
        f"prose={len(prose)} local={len(local)}",
    )
    check(
        "local_material_excluded_from_statements",
        all(row["statement_id"] == "NONE" for row in local)
        and all(row["statement_id"].startswith("G515-S") for row in prose),
        "51 local cards separate; 546 prose cards assigned",
    )
    event_by_id = {row["event_id"]: row for row in events}
    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose:
        statement_events[row["statement_id"]].append(row)
    boundary_failures = []
    for statement_id, rows in statement_events.items():
        if len({row["physical_page"] for row in rows}) != 1:
            boundary_failures.append(f"{statement_id}:page")
        if len({row["prose_block_id"] for row in rows}) != 1:
            boundary_failures.append(f"{statement_id}:block")
        if len({row["owner_id"] for row in rows}) != 1:
            boundary_failures.append(f"{statement_id}:owner")
    check(
        "statement_owner_boundaries",
        len(statement_events) == len(statements) and not boundary_failures,
        f"statements={len(statement_events)} failures={boundary_failures}",
    )
    check(
        "factorized_parser_pass",
        len(attachments) == 621
        and all(row["factorized_result"] == "PASS_FIXED_FACTORS" for row in attachments)
        and max(int(row["lookahead_cards"]) for row in attachments) <= 1
        and all(row["owner_boundary_crossed"] == "NO" for row in attachments)
        and all(row["statement_boundary_crossed"] == "NO" for row in attachments),
        f"attachments={len(attachments)} maxlook={max(int(row['lookahead_cards']) for row in attachments)}",
    )
    check(
        "amber_close_sensitivity_bounded",
        len([row for row in sensitivity if row["event_id"] != "NONE"]) == 3
        and all(row["alternate_factorized_result"] == "PASS_FIXED_FACTORS" for row in sensitivity),
        f"changed={len([row for row in sensitivity if row['event_id'] != 'NONE'])}",
    )

    check(
        "new_surface_census",
        len({row["surface"] for row in running_absent}) == 169
        and len({row["surface"] for row in genuinely_new}) == 159
        and {row["surface"] for row in genuinely_new}
        == {
            row["surface"] for row in running_absent
            if row["genuinely_new_to_old_26_pages"] == "YES"
        },
        "169 running-absent; 159 absent from all old 26-page groups",
    )
    check(
        "ten_old_local_contacts_visible",
        sum(row["old_local_surface_contact"] == "YES" for row in running_absent) == 10,
        f"contacts={sum(row['old_local_surface_contact'] == 'YES' for row in running_absent)}",
    )
    check(
        "all_five_expectations_seen",
        {row["expectation_id"] for row in expectations}
        == {f"G513-P{i}" for i in range(1, 6)}
        and all(row["observed_result"].startswith("SEEN") for row in expectations),
        "|".join(row["observed_result"] for row in expectations),
    )

    check(
        "extended_running_prefix_exact",
        running30[:4576] == old_running and len(running30[4576:]) == 546,
        "old 4,576 rows unchanged; 546 appended",
    )
    old_local = read_tsv(G407 / "gdt407_693_local_group_edition.tsv")
    check(
        "extended_local_prefix_exact",
        local30[:693] == old_local and len(local30[693:]) == 51,
        "old 693 rows unchanged; 51 appended",
    )
    old_unified = read_tsv(G407 / "gdt407_5269_unified_group_ledger.tsv")
    check(
        "extended_unified_prefix_exact",
        unified30[:5269] == old_unified and len(unified30[5269:]) == 597,
        "old 5,269 rows unchanged; 597 appended",
    )
    check(
        "extended_group_split",
        Counter(row["group_kind"] for row in unified30)
        == Counter({"RUNNING_EVENT": 5122, "LOCAL_ADDRESS_OR_LABEL": 744}),
        str(Counter(row["group_kind"] for row in unified30)),
    )
    check(
        "thirty_page_inventory",
        len({row["physical_page"] for row in pages30}) == 30
        and SELECTED <= {row["physical_page"] for row in pages30},
        f"pages={len({row['physical_page'] for row in pages30})}",
    )
    check(
        "page_defaults_complete",
        sum(int(row["complete_default_count"]) for row in pages) == 597
        and all(row["factorized_failure_count"] == "0" for row in pages),
        f"defaults={sum(int(row['complete_default_count']) for row in pages)}",
    )

    expected_result = {
        "event_count": 597,
        "prose_event_count": 546,
        "local_label_sign_event_count": 51,
        "unique_surface_count": 377,
        "gdt405_exact_event_count": 276,
        "gdt405_lock_mismatch_count": 0,
        "old_running_exact_event_count": 416,
        "old_any_surface_event_count": 429,
        "running_absent_surface_count": 169,
        "genuinely_new_surface_count": 159,
        "genuinely_new_event_count": 168,
        "complete_default_count": 597,
        "statement_count": 78,
        "focus_attachment_count": 621,
        "factorized_failure_count": 0,
        "expectations_seen_count": 5,
        "extended_unified_group_count": 5866,
    }
    check(
        "result_summary_exact",
        all(result.get(key) == value for key, value in expected_result.items()),
        str({key: result.get(key) for key in expected_result}),
    )
    check(
        "source_hash_exact",
        result["source_sha256"]
        == sha256(ART / "gdt515_122_guarded_source_lines.tsv"),
        result["source_sha256"],
    )
    check(
        "reading_book_complete",
        (ART / "GDT515_FOUR_PAGE_COMPLETE_WORKING_READING.md").is_file()
        and (ART / "GDT515_FOUR_PAGE_COMPLETE_WORKING_READING.md").stat().st_size > 100000,
        f"bytes={(ART / 'GDT515_FOUR_PAGE_COMPLETE_WORKING_READING.md').stat().st_size}",
    )

    passed = sum(row["passed"] for row in checks)
    validation = {
        "experiment_id": "GDT515",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed_checks": passed,
        "total_checks": len(checks),
        "checks": checks,
    }
    (ART / "gdt515_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
