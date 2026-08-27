#!/usr/bin/env python3
"""Final-surface overlay for the GDT517 thirty-page intake compiler."""

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
BASE = ROOT / "experiments/yolo/gdt537_seven_route_final_intake_supplement"
DICTIONARY = BASE / "artifacts/gdt537_159_final_surface_dictionary.tsv"
ROUTES = BASE / "artifacts/gdt537_7_revision_route_cards.tsv"
GDT517 = (
    ROOT
    / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/src"
    / "intake_surface.py"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def exact_final_lookup(
    surface: str,
    domain: str = "AUTO",
    dictionary_rows: list[dict[str, str]] | None = None,
    route_rows: list[dict[str, str]] | None = None,
) -> dict | None:
    """Return the final prose lock, or None when GDT517 must handle the form."""
    if domain == "LOCAL_RECORD":
        return None
    dictionary_rows = dictionary_rows if dictionary_rows is not None else read_tsv(DICTIONARY)
    route_rows = route_rows if route_rows is not None else read_tsv(ROUTES)
    row = next((item for item in dictionary_rows if item["surface"] == surface), None)
    if row is None:
        return None
    route = next((item for item in route_rows if item["surface"] == surface), None)
    return {
        "surface": surface,
        "status": "GDT537_FINAL_PROSE_SURFACE_LOCK",
        "requested_domain": domain,
        "lock_scope": "PROSE_STREAM_ONLY",
        "final_recipe": row["final_working_recipe"],
        "literal_reading_de": row["literal_reading_de"],
        "working_phrase_de": row["working_phrase_de"],
        "candidate_rank": row["gdt529_candidate_rank"],
        "resolution_status": row["resolution_status"],
        "special_route": "YES" if route else "NO",
        "route_class": route["route_class"] if route else "ORDINARY_FINAL_SURFACE_LOCK",
        "route_source": route["source_experiment"] if route else "GDT536_FINAL_EDITION",
        "visible_split": route["visible_split"] if route else "EXACT_SURFACE",
        "recipe_split": route["recipe_split"] if route else row["final_working_recipe"],
        "primary_evidence": route["primary_evidence"] if route else "GDT536_FINAL_EXACT_SURFACE",
        "selection_precedence": "GDT537_FINAL_PROSE_SURFACE_LOCK>GDT517_BASE_INTAKE",
        "guard": "EXACT_FINAL_WORKING_CARD__LOCAL_RECORD_DOMAIN_DELEGATES__NO_CORE_RETUNING",
    }


def delegate_to_gdt517(args: argparse.Namespace) -> dict:
    command = [
        sys.executable,
        str(GDT517),
        "--surface",
        args.surface,
        "--domain",
        args.domain,
        "--top",
        str(args.top),
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
    completed = subprocess.run(
        command, cwd=ROOT, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        return {
            "surface": args.surface,
            "status": "GDT517_DELEGATION_ERROR",
            "returncode": completed.returncode,
            "stderr": completed.stderr,
        }
    return {
        "surface": args.surface,
        "status": "DELEGATED_TO_GDT517_BASE",
        "requested_domain": args.domain,
        "reason": (
            "LOCAL_RECORD_DOMAIN_NOT_COVERED_BY_GDT537_PROSE_LOCK"
            if args.domain == "LOCAL_RECORD"
            else "SURFACE_NOT_IN_GDT537_FINAL_159"
        ),
        "selection_precedence": "GDT517_EXACT_EVENT>KNOWN_SURFACE_ROLE>COMPILED_TOP1",
        "base_intake": json.loads(completed.stdout),
        "guard": "NO_GDT537_OVERRIDE_APPLIED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply the GDT537 final prose overlay, then delegate to GDT517."
    )
    parser.add_argument("--surface", required=True)
    parser.add_argument("--event-id", default="")
    parser.add_argument("--page", default="")
    parser.add_argument(
        "--domain",
        choices=["AUTO", "PROSE_STREAM", "LOCAL_RECORD"],
        default="AUTO",
    )
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--incoming-action", default="")
    parser.add_argument("--incoming-argument", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    exact = exact_final_lookup(args.surface, args.domain)
    result = exact if exact is not None else delegate_to_gdt517(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "GDT517_DELEGATION_ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
