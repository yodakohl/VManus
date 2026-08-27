#!/usr/bin/env python3
"""Phrase-complete overlay for the GDT537/GDT517 surface reader."""

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
BASE = ROOT / "experiments/yolo/gdt538_final_159_phrase_consistency_edition"
DICTIONARY = BASE / "artifacts/gdt538_159_complete_phrase_dictionary.tsv"
GDT537 = (
    ROOT
    / "experiments/yolo/gdt537_seven_route_final_intake_supplement/src"
    / "intake_surface.py"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def exact_phrase_lookup(
    surface: str,
    domain: str = "AUTO",
    dictionary_rows: list[dict[str, str]] | None = None,
) -> dict | None:
    if domain == "LOCAL_RECORD":
        return None
    rows = dictionary_rows if dictionary_rows is not None else read_tsv(DICTIONARY)
    row = next((item for item in rows if item["surface"] == surface), None)
    if row is None:
        return None
    return {
        "surface": surface,
        "status": "GDT538_PHRASE_COMPLETE_PROSE_SURFACE_LOCK",
        "requested_domain": domain,
        "lock_scope": row["lock_scope"],
        "final_recipe": row["final_working_recipe"],
        "literal_reading_de": row["literal_reading_de"],
        "controlled_order_reading_de": row["controlled_order_reading_de"],
        "canonical_workshop_phrase_de": row["canonical_workshop_phrase_de"],
        "phrase_template": row["phrase_template"],
        "all_slots_explicit": row["all_slots_explicit"],
        "special_route": row["special_route"],
        "route_class": row["route_class"],
        "route_source": row["route_source"],
        "selection_precedence": "GDT538_PHRASE_LOCK>GDT537_FINAL_RECIPE>GDT517_BASE_INTAKE",
        "guard": "PHRASE_ONLY__EXACT_PROSE_SURFACE__LOCAL_RECORD_DELEGATES",
    }


def delegate(args: argparse.Namespace) -> dict:
    command = [
        sys.executable,
        str(GDT537),
        "--surface", args.surface,
        "--domain", args.domain,
        "--top", str(args.top),
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
            "status": "GDT537_DELEGATION_ERROR",
            "returncode": completed.returncode,
            "stderr": completed.stderr,
        }
    return {
        "surface": args.surface,
        "status": "DELEGATED_TO_GDT537_FINAL_RECIPE_LAYER",
        "requested_domain": args.domain,
        "reason": (
            "LOCAL_RECORD_DOMAIN_NOT_COVERED_BY_GDT538_PROSE_PHRASE_LOCK"
            if args.domain == "LOCAL_RECORD"
            else "SURFACE_NOT_IN_GDT538_FINAL_159"
        ),
        "base_intake": json.loads(completed.stdout),
        "guard": "NO_GDT538_PHRASE_OVERRIDE_APPLIED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply the GDT538 phrase layer, then delegate to GDT537."
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
    exact = exact_phrase_lookup(args.surface, args.domain)
    result = exact if exact is not None else delegate(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "GDT537_DELEGATION_ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
