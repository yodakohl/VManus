#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    output_paths = sorted(OUT.glob("gdt407_*.tsv")) + [HERE / "TWENTY_SIX_PAGE_READABLE_CORE_EDITION.md"]
    first_hashes = {str(path): digest(path) for path in output_paths}
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    second_hashes = {str(path): digest(path) for path in output_paths}

    running = read("gdt407_4576_running_event_edition.tsv")
    local = read("gdt407_693_local_group_edition.tsv")
    groups = read("gdt407_5269_unified_group_ledger.tsv")
    statements = read("gdt407_715_statement_edition.tsv")
    attachments = read("gdt407_5051_attachment_edition.tsv")
    pages = read("gdt407_26_page_summary.tsv")
    result = json.loads((OUT / "gdt407_result.json").read_text(encoding="utf-8"))

    running_ids = {row["global_running_event_id"] for row in running}
    statement_ids = {row["global_statement_id"] for row in statements}
    source_event_ids = {row["source_event_id"] for row in running}
    checks = {
        "running_4576": len(running) == 4576,
        "local_693": len(local) == 693,
        "groups_5269": len(groups) == 5269,
        "statements_715": len(statements) == 715,
        "attachments_5051": len(attachments) == 5051,
        "pages_26": len(pages) == 26,
        "unique_running_ids": len(running_ids) == 4576,
        "unique_group_ids": len({r["global_group_id"] for r in groups}) == 5269,
        "unique_statement_ids": len(statement_ids) == 715,
        "unique_attachment_ids": len({r["global_attachment_id"] for r in attachments}) == 5051,
        "group_partition": Counter(r["group_kind"] for r in groups) == Counter({"RUNNING_EVENT": 4576, "LOCAL_ADDRESS_OR_LABEL": 693}),
        "statement_event_sum": sum(int(r["event_count"]) for r in statements) == 4576,
        "statement_attachment_sum": sum(int(r["focus_attachment_count"]) for r in statements) == 5051,
        "page_group_sum": sum(int(r["visible_group_count"]) for r in pages) == 5269,
        "page_running_sum": sum(int(r["running_event_count"]) for r in pages) == 4576,
        "page_local_sum": sum(int(r["local_group_count"]) for r in pages) == 693,
        "page_statement_sum": sum(int(r["statement_count"]) for r in pages) == 715,
        "page_attachment_sum": sum(int(r["focus_attachment_count"]) for r in pages) == 5051,
        "attachment_events_resolve": all(r["global_running_event_id"] in running_ids for r in attachments),
        "attachment_actions_resolve": all(
            r["selected_action_global_event_id"] in running_ids or r["selected_action_global_event_id"].startswith("OWNER::G407-S")
            for r in attachments
        ),
        "attachment_statements_resolve": all(r["global_statement_id"] in statement_ids for r in attachments),
        "attachment_source_events_resolve": all(r["source_event_id"] in source_event_ids for r in attachments),
        "no_owner_crossing": all(r["owner_boundary_crossed"] == "NO" for r in attachments),
        "no_statement_crossing": all(r["statement_boundary_crossed"] == "NO" for r in attachments),
        "lookahead_at_most_one": max(int(r["lookahead_cards"]) for r in attachments) <= 1,
        "source_layer_split_running": Counter(r["source_layer"] for r in running) == Counter({"ORIGINAL22_RUNNING": 3888, "GDT404_RANDOM4_RUNNING": 688}),
        "source_layer_split_attachments": Counter(r["source_layer"] for r in attachments) == Counter({"ORIGINAL22_GDT402": 4374, "GDT404_FACTORIZED": 677}),
        "all_local_rows_are_local": all(r["surface_status"] == "LOCAL_ADDRESS_OR_LABEL__NO_PROSE_PARSE" for r in local),
        "local_source_role_split": Counter(r["source_local_role"] for r in local) == Counter({"LOCAL_ADDRESS_OR_LABEL": 550, "LOCAL_ADDRESS_OR_SECTION_MARKER": 143}),
        "expected_status": result["status"] == "UNIFIED_TWENTY_SIX_PAGE_EDITION_COMPLETE",
        "deterministic_rebuild": first_hashes == second_hashes,
        "no_forbidden_page": not any("f84" in "\t".join(r.values()).lower() for table in (running, local, groups, statements, attachments, pages) for r in table),
    }
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks), "failure_count": sum(not value for value in checks.values()),
        "checks": checks,
    }
    (OUT / "gdt407_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
