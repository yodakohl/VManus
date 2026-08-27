#!/usr/bin/env python3
"""Role-corrected lookup above the GDT538 phrase and GDT517 base readers."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition"
ROLES = BASE / "artifacts/gdt539_159_surface_role_scopes.tsv"
LOCAL_DEFAULTS = BASE / "artifacts/gdt539_14_local_surface_defaults.tsv"
G538 = (
    ROOT
    / "experiments/yolo/gdt538_final_159_phrase_consistency_edition/src"
    / "phrase_surface.py"
)
G517 = (
    ROOT
    / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/src"
    / "intake_surface.py"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def exact_role_lookup(
    surface: str,
    domain: str = "AUTO",
    role_rows: list[dict[str, str]] | None = None,
    local_rows: list[dict[str, str]] | None = None,
) -> dict | None:
    roles = role_rows if role_rows is not None else read_tsv(ROLES)
    role = next((row for row in roles if row["surface"] == surface), None)
    if role is None:
        return None
    observed = role["observed_domain"]
    if domain != "AUTO" and domain != observed:
        return None
    if observed == "PROSE_STREAM":
        return {
            "surface": surface,
            "status": "GDT539_ROLE_CORRECT_PROSE_SURFACE_LOCK",
            "requested_domain": domain,
            "observed_domain": observed,
            "lock_scope": role["corrected_lock_scope"],
            "final_recipe": role["final_working_recipe"],
            "controlled_order_reading_de": role["controlled_order_reading_de"],
            "working_phrase_de": role["canonical_workshop_phrase_de"],
            "content_roles": role["content_roles"],
            "event_count": role["event_count"],
            "selection_precedence": "GDT539_ROLE_SCOPE>GDT538_PHRASE>GDT537_RECIPE>GDT517_BASE",
            "guard": "OBSERVED_PROSE_ROLE_ONLY__NO_FUTURE_ROLE_PREDICTION",
        }
    local_material = local_rows if local_rows is not None else read_tsv(LOCAL_DEFAULTS)
    local = next(row for row in local_material if row["surface"] == surface)
    return {
        "surface": surface,
        "status": "GDT539_ROLE_CORRECT_LOCAL_SURFACE_LOCK",
        "requested_domain": domain,
        "observed_domain": observed,
        "lock_scope": role["corrected_lock_scope"],
        "final_recipe": role["final_working_recipe"],
        "controlled_order_reading_de": role["controlled_order_reading_de"],
        "working_phrase_de": local["local_surface_default_de"],
        "content_roles": role["content_roles"],
        "event_count": role["event_count"],
        "selection_precedence": "GDT539_LOCAL_ROLE_SCOPE>GDT517_EXACT_LOCAL_EVENT",
        "guard": "OBSERVED_LOCAL_ROLE_ONLY__NO_PROSE_COERCION",
    }


def build_command(reader: Path, args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable, str(reader), "--surface", args.surface,
        "--domain", args.domain, "--top", str(args.top),
    ]
    if args.event_id:
        command.extend(["--event-id", args.event_id])
    if args.page:
        command.extend(["--page", args.page])
    if args.execute:
        command.append("--execute")
    if args.incoming_action:
        command.extend(["--incoming-action", args.incoming_action])
    if args.incoming_argument:
        command.extend(["--incoming-argument", args.incoming_argument])
    return command


def delegate(reader: Path, args: argparse.Namespace, reason: str) -> dict:
    completed = subprocess.run(
        build_command(reader, args), cwd=ROOT, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        return {
            "surface": args.surface,
            "status": "DELEGATION_ERROR",
            "returncode": completed.returncode,
            "stderr": completed.stderr,
        }
    return {
        "surface": args.surface,
        "status": "DELEGATED_BELOW_GDT539_ROLE_SCOPE",
        "requested_domain": args.domain,
        "reason": reason,
        "delegated_reader": "GDT517" if reader == G517 else "GDT538",
        "base_intake": json.loads(completed.stdout),
        "guard": "NO_GDT539_ROLE_OVERRIDE_APPLIED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply GDT539 observed role scopes before prior readers."
    )
    parser.add_argument("--surface", required=True)
    parser.add_argument("--event-id", default="")
    parser.add_argument("--page", default="")
    parser.add_argument(
        "--domain", choices=["AUTO", "PROSE_STREAM", "LOCAL_RECORD"], default="AUTO"
    )
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--incoming-action", default="")
    parser.add_argument("--incoming-argument", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    roles = read_tsv(ROLES)
    role = next((row for row in roles if row["surface"] == args.surface), None)
    exact = exact_role_lookup(args.surface, args.domain, roles)
    if exact is not None:
        result = exact
    elif role is not None:
        result = delegate(
            G517,
            args,
            "REQUESTED_DOMAIN_DIFFERS_FROM_OBSERVED_GDT539_ROLE__BYPASS_OLD_OVERLAY",
        )
    else:
        result = delegate(G538, args, "SURFACE_OUTSIDE_GDT539_FINAL_159")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "DELEGATION_ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
