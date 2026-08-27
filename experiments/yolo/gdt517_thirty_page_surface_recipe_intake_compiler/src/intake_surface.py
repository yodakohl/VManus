#!/usr/bin/env python3
"""Look up a known surface or compile an unseen one into finite recipe candidates."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as core  # noqa: E402


LEXICON = core.OUT / "gdt517_current30_chunk_mapping_lexicon.tsv"
SURFACE_INDEX = core.OUT / "gdt517_current30_surface_role_index.tsv"
EVENT_DICTIONARY = core.OUT / "gdt517_5866_exact_event_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_mappings() -> dict[str, list[dict[str, object]]]:
    mappings: dict[str, list[dict[str, object]]] = {}
    for row in read_tsv(LEXICON):
        mappings.setdefault(row["surface_chunk"], []).append(
            {
                "recipe": core.atoms(row["recipe"]),
                "support": int(row["support"]),
                "share": float(row["support_share"]),
                "score": float(row["derivation_score"]),
                "scope": row["mapping_scope"],
            }
        )
    return mappings


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--event-id", default="NONE")
    parser.add_argument("--page", default="AUTO")
    parser.add_argument("--domain", choices=("AUTO", "PROSE_STREAM", "LOCAL_RECORD"), default="AUTO")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--incoming-action", default="NONE")
    parser.add_argument("--incoming-argument", default="NONE")
    args = parser.parse_args()

    surface = args.surface.lower()
    exact_events = [row for row in read_tsv(EVENT_DICTIONARY) if row["surface"] == surface]
    if args.event_id != "NONE":
        exact_events = [row for row in exact_events if row["source_event_id"] == args.event_id]
    if args.page != "AUTO":
        exact_events = [row for row in exact_events if row["physical_page"] == args.page]
    if args.domain != "AUTO":
        exact_events = [row for row in exact_events if row["execution_domain"] == args.domain]

    surface_options = [row for row in read_tsv(SURFACE_INDEX) if row["surface"] == surface]
    if args.domain != "AUTO":
        surface_options = [row for row in surface_options if row["execution_domain"] == args.domain]
    if args.page != "AUTO":
        surface_options = [
            row for row in surface_options if args.page in row["physical_pages"].split("|")
        ]

    allow_f66r_local = args.page == "f66r" and args.domain == "LOCAL_RECORD"
    candidates = core.parse_surface(
        surface,
        load_mappings(),
        allow_f66r_local=allow_f66r_local,
    )[: max(1, args.top)]
    values = core.literal_renderer()
    compiled = [
        {
            "rank": rank,
            "recipe": core.recipe_text(candidate.recipe),
            "literal_de": core.render_literal(candidate.recipe, values),
            "visible_chunk_count": candidate.chunk_count,
            "score": round(candidate.score, 6),
            "derivation": core.path_text(candidate),
        }
        for rank, candidate in enumerate(candidates, 1)
    ]

    result: dict[str, object] = {
        "surface": surface,
        "lookup_scope": {
            "event_id": args.event_id,
            "page": args.page,
            "domain": args.domain,
        },
        "exact_event_match_count": len(exact_events),
        "exact_event_matches": exact_events[: max(1, args.top)],
        "known_surface_recipe_options": surface_options[: max(1, args.top)],
        "compiled_candidate_count_shown": len(compiled),
        "compiled_candidates": compiled,
        "selection_precedence": "EXACT_EVENT>KNOWN_SURFACE_ROLE_OPTION>COMPILED_TOP1",
        "default_selection": (
            exact_events[0]["exact_event_recipe"]
            if len(exact_events) == 1
            else surface_options[0]["exact_event_recipe"]
            if len(surface_options) == 1
            else compiled[0]["recipe"]
            if compiled
            else "UNPARSED"
        ),
        "guard": "WORKING_RECIPE_OR_LOCAL_PACKAGE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
    }

    if args.execute:
        selected_domain = (
            exact_events[0]["execution_domain"]
            if len(exact_events) == 1
            else surface_options[0]["execution_domain"]
            if len(surface_options) == 1
            else "PROSE_STREAM"
        )
        recipe = str(result["default_selection"])
        if selected_domain == "LOCAL_RECORD" or "::" in recipe:
            result["execution"] = {
                "decision": "READ_LOCAL_RECORD",
                "route": "LOCAL_PACKAGE_DOES_NOT_ENTER_PORTABLE_ACTION_STREAM",
            }
        elif recipe == "UNPARSED":
            result["execution"] = {"decision": "STOP", "route": "UNPARSED_SURFACE"}
        else:
            intake = load_module("gdt451_intake_for_gdt517_cli", core.G451_INTAKE)
            certificate = intake.issue_integrated_certificate(
                recipe, args.incoming_action, args.incoming_argument, None, "NONE"
            )
            result["execution"] = certificate

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
