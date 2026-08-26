#!/usr/bin/env python3
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
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    paths = sorted(OUT.glob("gdt408_*.tsv"))
    first = {str(path): digest(path) for path in paths}
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    second = {str(path): digest(path) for path in paths}
    events = rows("gdt408_4576_event_leaveout.tsv")
    local = rows("gdt408_693_local_leaveout.tsv")
    attachments = rows("gdt408_5051_attachment_leaveout.tsv")
    surfaces = rows("gdt408_surface_recipe_leaveout.tsv")
    summary = rows("gdt408_26_page_leaveout_summary.tsv")
    result = json.loads((OUT / "gdt408_result.json").read_text(encoding="utf-8"))
    pages = {row["held_page"] for row in summary}
    checks = {
        "events_4576": len(events) == 4576,
        "local_693": len(local) == 693,
        "attachments_5051": len(attachments) == 5051,
        "pages_26": len(summary) == 26 and len(pages) == 26,
        "event_ids_unique": len({row["global_running_event_id"] for row in events}) == 4576,
        "attachment_ids_unique": len({row["global_attachment_id"] for row in attachments}) == 5051,
        "local_ids_unique": len({row["source_event_id"] for row in local}) == 693,
        "summary_event_sum": sum(int(row["running_event_count"]) for row in summary) == 4576,
        "summary_local_sum": sum(int(row["local_group_count"]) for row in summary) == 693,
        "summary_attachment_sum": sum(int(row["attachment_count"]) for row in summary) == 5051,
        "event_partition": sum(result["event_replay_counts"].values()) == 4576,
        "local_partition": sum(result["local_replay_counts"].values()) == 693,
        "attachment_partition": sum(result["attachment_replay_counts"].values()) == 5051,
        "surface_rows_nonempty": bool(surfaces),
        "factor_failure_rows_explicit": all(row["missing_factor_values"] == "NONE" or row["leave_one_page_replay_class"] == "FAIL_PAGE_PRIVATE_FACTOR_VALUE" for row in attachments),
        "deterministic_rebuild": first == second,
        "status_exact": result["status"] == "TWENTY_SIX_OF_TWENTY_SIX_PAGE_FACTOR_REPLAY_COMPLETE",
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (events, local, attachments, surfaces, summary) for row in table),
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not v for v in checks.values()), "checks": checks}
    (OUT / "gdt408_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
