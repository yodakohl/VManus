#!/usr/bin/env python3
"""Validate the GDT415 owner-local semantic atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas"
OUT = BASE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    atlas = rows("gdt415_95_register_expansion_atlas.tsv")
    owners = rows("gdt415_owner_specific_expansion_atlas.tsv")
    events = rows("gdt415_4576_event_owner_local_edition.tsv")
    statements = rows("gdt415_715_statement_owner_local_edition.tsv")
    result = json.loads((OUT / "gdt415_result.json").read_text(encoding="utf-8"))
    expected_pages = {
        "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v", "f56r", "f95v",
        "f75r", "f76r", "f77r", "f81r", "f81v", "f82r", "f83r",
        "f67r2", "f68r1", "f71v", "f72r", "f88r", "f88v", "f89r",
    }
    checks = {
        "atlas_95": len(atlas) == 95,
        "atlas_unique_root_register": len({(r["root"], r["register"]) for r in atlas}) == 95,
        "all_mentions_positive": all(int(r["mention_count"]) > 0 for r in atlas),
        "guardrail_counts_exact": all(r["mention_count"] == r["guardrail_mention_count"] for r in atlas),
        "register_expansions_injective": len({(r["register"], r["owner_local_expansion_de"]) for r in atlas}) == 95,
        "back_projection_exact_atlas": all(r["portable_default_de"] == r["back_projection_de"] for r in atlas),
        "owners_nonempty": len(owners) > 95 and all(r["owner_local_expansion_de"] for r in owners),
        "owners_back_project": all(r["portable_default_de"] == r["back_projection_de"] for r in owners),
        "events_4576": len(events) == 4576,
        "events_unique": len({r["global_running_event_id"] for r in events}) == 4576,
        "event_roundtrip": all(r["roundtrip_exact"] == "YES" for r in events),
        "statements_715": len(statements) == 715,
        "statements_unique": len({r["global_statement_id"] for r in statements}) == 715,
        "statement_roundtrip": all(r["back_projection_exact"] == "YES" for r in statements),
        "event_counts_match": sum(int(r["event_count"]) for r in statements) == 4576,
        "statement_event_counts_exact": all(int(r["event_count"]) == len(r["event_ids"].split("|")) for r in statements),
        "statement_events_cover": len({event_id for r in statements for event_id in r["event_ids"].split("|")}) == 4576,
        "local_statement_readings_nonempty": all(r["owner_local_reading_de"] and r["owner_local_action_chain_de"] for r in statements),
        "pages_exact": {r["physical_page"] for r in events} == expected_pages,
        "no_forbidden_page": all(not r["physical_page"].startswith("f84") for r in events),
        "no_new_meanings": result["new_portable_meanings"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "handbook_exists": (OUT / "OWNER_LOCAL_EXPANSION_DICTIONARY.md").is_file(),
    }
    tracked = [
        OUT / "gdt415_95_register_expansion_atlas.tsv",
        OUT / "gdt415_owner_specific_expansion_atlas.tsv",
        OUT / "gdt415_4576_event_owner_local_edition.tsv",
        OUT / "gdt415_715_statement_owner_local_edition.tsv",
        OUT / "OWNER_LOCAL_EXPANSION_DICTIONARY.md",
        OUT / "gdt415_result.json",
    ]
    before = {p.name: sha(p) for p in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    checks["deterministic_rebuild"] = before == {p.name: sha(p) for p in tracked}
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "failure_count": sum(not value for value in checks.values()),
        "checks": checks,
    }
    (OUT / "gdt415_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
