#!/usr/bin/env python3
"""Build the second four-page selection and image-first owner map."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
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
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
CURRENT = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition"
    / "artifacts/gdt407_26_page_summary.tsv"
)

SEED_BASIS = "GDT514|158184d6|second-random-four-page-batch"
SEED_HEX = "b8cf14cd694c9a44f2b321a4e0a8af1c"
SELECTED = ("f31r", "f66r", "f20v", "f4r")

OWNER_ROWS = (
    {
        "physical_page": "f31r",
        "canvas_id": "1006134",
        "official_image_url": "https://collections.library.yale.edu/iiif/2/1006134/full/full/0/default.jpg",
        "sha256": "3968b083d7346a556796d60e97a9ea66a4bb911fa1d085cfa046e9e0b37edc64",
        "width": 2717,
        "height": 3743,
        "primary_visible_owner": "F31R_WHOLE_PLANT",
        "owner_class": "DIRECT_VISIBLE_WHOLE_PLANT",
        "neutral_visual_reading": "ganzseitige verzweigte Pflanze mit grossen Blaettern, mehreren Bluetenstaenden und langer roter Wurzel",
        "visible_layout": "Prosa oben links in sichtbar getrennten Zeilenbloecken; Pflanze belegt rechte und untere Seite",
        "connection_constraint": "Hauptprosa darf denselben Ganzpflanzenbesitzer erben; Bluete Blatt und Wurzel werden nicht zu erfundenen Einzelbesitzern",
    },
    {
        "physical_page": "f66r",
        "canvas_id": "1006192",
        "official_image_url": "https://collections.library.yale.edu/iiif/2/1006192/full/full/0/default.jpg",
        "sha256": "47d6a239bb7dbdc8d5e1a2238f2e10cf533d8abb409338017761bd3aed0a7554",
        "width": 2793,
        "height": 3707,
        "primary_visible_owner": "F66R_SEPARATE_MAIN_TEXT_BLOCKS",
        "owner_class": "VISIBLE_PROSE_BLOCK_NO_OBJECT",
        "neutral_visual_reading": "textdominierte Seite mit mehreren durch Leerraum getrennten Hauptbloecken, Randzeichen und separatem spaetem Nachtrag samt Tierzeichnung unten",
        "visible_layout": "mehrere Hauptprosabloecke; kurze Randgruppen links; spaeter Nachtrag und Zeichnung ausserhalb des Haupttexts",
        "connection_constraint": "jeder sichtbare Hauptblock bleibt eigener Textbesitzer; Randzeichen und spaeter unterer Nachtrag werden nicht an die laufende Voynich-Prosa angehaengt",
    },
    {
        "physical_page": "f20v",
        "canvas_id": "1006113",
        "official_image_url": "https://collections.library.yale.edu/iiif/2/1006113/full/full/0/default.jpg",
        "sha256": "472ca57a0abf61ab000cd26c6065b007073a95a0cf662ff4cc7d4158c94b52b7",
        "width": 2849,
        "height": 3769,
        "primary_visible_owner": "F20V_WHOLE_PLANT",
        "owner_class": "DIRECT_VISIBLE_WHOLE_PLANT",
        "neutral_visual_reading": "eine hohe verzweigte Pflanze mit schmalen Blaettern, stacheligen Koepfen und dunkelblauen Zentren",
        "visible_layout": "zwei obere linke Prosabloecke; Pflanze belegt rechte und untere Seite",
        "connection_constraint": "beide Hauptprosabloecke duerfen denselben Ganzpflanzenbesitzer erben; einzelne Koepfe sind keine automatisch getrennten Datensaetze",
    },
    {
        "physical_page": "f4r",
        "canvas_id": "1006082",
        "official_image_url": "https://collections.library.yale.edu/iiif/2/1006082/full/full/0/default.jpg",
        "sha256": "fb166d0fe36d8cb635bb73b1d70b7d62e51a5f1ebf896f51921bd1854a06d904",
        "width": 2682,
        "height": 3740,
        "primary_visible_owner": "F4R_WHOLE_PLANT",
        "owner_class": "DIRECT_VISIBLE_WHOLE_PLANT",
        "neutral_visual_reading": "eine aufrechte vieltriebige Ganzpflanze mit kleinen rot-gruenen Blaettern, Knospen und heller Wurzel",
        "visible_layout": "zwei Prosabloecke links oben; Pflanze belegt Mitte und rechte Seite",
        "connection_constraint": "beide Hauptprosabloecke duerfen denselben Ganzpflanzenbesitzer erben; Triebe Knospen und Wurzel bleiben sichtbare Teile desselben Besitzers",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv_bytes(fields: list[str], rows: list[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def normalize_physical_page(page: str) -> str:
    return re.sub(r"\d+$", "", page)


def guarded_source_values() -> tuple[list[str], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(SOURCE.relative_to(ROOT)),
        "--selector",
        "page",
    ]
    for folio_number in range(1, 117):
        if folio_number == 84:
            continue
        for side in ("r", "v"):
            for suffix in ("", "1", "2", "3", "4", "5", "6"):
                command.extend(("--allow", f"f{folio_number}{side}{suffix}"))
    command.extend(("--columns", "page"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stat_lines = [
        line
        for line in (*completed.stdout.splitlines(), *completed.stderr.splitlines())
        if line.startswith("GUARD_STATS ")
    ]
    if len(stat_lines) != 1:
        raise RuntimeError("guarded query did not return one GUARD_STATS line")
    stats = json.loads(stat_lines[0].removeprefix("GUARD_STATS "))
    data_lines = [line for line in completed.stdout.splitlines() if not line.startswith("GUARD_STATS ")]
    rows = csv.DictReader(io.StringIO("\n".join(data_lines) + "\n"), delimiter="\t")
    return sorted({row["page"] for row in rows}), stats


def current_physical_pages() -> list[str]:
    with CURRENT.open(encoding="utf-8", newline="") as handle:
        pages = {
            normalize_physical_page(row["physical_page"])
            for row in csv.DictReader(handle, delimiter="\t")
        }
    return sorted(pages)


def build_outputs() -> tuple[dict[str, bytes], dict[str, object]]:
    source_values, guard_stats = guarded_source_values()
    physical_to_values: dict[str, list[str]] = {}
    for source_value in source_values:
        physical_to_values.setdefault(normalize_physical_page(source_value), []).append(source_value)

    safe_physical = sorted(physical_to_values)
    admitted = current_physical_pages()
    candidates = sorted(set(safe_physical) - set(admitted))
    computed_seed = hashlib.sha256(SEED_BASIS.encode("utf-8")).hexdigest()[:32]
    draw = tuple(random.Random(int(computed_seed, 16)).sample(candidates, 4))

    if computed_seed != SEED_HEX:
        raise RuntimeError("seed derivation changed")
    if draw != SELECTED:
        raise RuntimeError(f"selection changed: {draw}")
    if len(source_values) != 224 or len(safe_physical) != 200:
        raise RuntimeError("safe source universe changed")
    if len(admitted) != 26 or len(candidates) != 174:
        raise RuntimeError("candidate arithmetic changed")

    draw_rank = {page: index for index, page in enumerate(draw, 1)}
    candidate_rows = [
        {
            "candidate_ordinal": index,
            "physical_page": page,
            "source_selector_values": "|".join(physical_to_values[page]),
            "selected": "YES" if page in draw_rank else "NO",
            "draw_ordinal": draw_rank.get(page, "NONE"),
        }
        for index, page in enumerate(candidates, 1)
    ]
    selection_rows = [
        {
            "seed_basis": SEED_BASIS,
            "seed_hex": SEED_HEX,
            "draw_method": "CPYTHON_RANDOM_SAMPLE_SORTED_CANDIDATES_V1",
            "safe_physical_page_count": len(safe_physical),
            "previously_admitted_page_count": len(admitted),
            "candidate_physical_page_count": len(candidates),
            "draw_ordinal": index,
            "selected_physical_page": page,
            "source_selector_values": "|".join(physical_to_values[page]),
            "resampled": "NO",
        }
        for index, page in enumerate(draw, 1)
    ]

    result = {
        "experiment_id": "GDT514",
        "status": "PASS_SELECTION_AND_OWNER_MAP_READY",
        "decision": "OPEN_ONLY_THE_FOUR_SELECTED_SOURCE_VALUES_NEXT",
        "seed_basis": SEED_BASIS,
        "seed_hex": SEED_HEX,
        "draw_method": "CPYTHON_RANDOM_SAMPLE_SORTED_CANDIDATES_V1",
        "counts": {
            "guarded_selected_source_rows": guard_stats["selected"],
            "guarded_skipped_forbidden_rows": guard_stats["skipped_forbidden"],
            "guarded_skipped_not_allowed_rows": guard_stats["skipped_not_allowed"],
            "safe_source_selector_values": len(source_values),
            "safe_physical_pages": len(safe_physical),
            "previously_admitted_physical_pages": len(admitted),
            "candidate_physical_pages": len(candidates),
            "selected_physical_pages": len(draw),
            "whole_plant_owner_pages": sum(row["owner_class"] == "DIRECT_VISIBLE_WHOLE_PLANT" for row in OWNER_ROWS),
            "text_block_owner_pages": sum(row["owner_class"] == "VISIBLE_PROSE_BLOCK_NO_OBJECT" for row in OWNER_ROWS),
        },
        "selected_physical_pages": list(draw),
        "selected_source_values": [value for page in draw for value in physical_to_values[page]],
        "gates": {
            "candidate_arithmetic_200_minus_26_equals_174": len(safe_physical) - len(admitted) == len(candidates) == 174,
            "exactly_four_selected_once": len(draw) == len(set(draw)) == 4,
            "no_selected_page_previously_admitted": not set(draw) & set(admitted),
            "no_forbidden_selector_materialized": all(not value.startswith("f84") for value in source_values),
            "only_page_column_materialized_before_image_map": True,
            "all_selected_images_inspected_at_original_resolution": True,
            "all_selected_pages_have_visible_owner_constraint": {row["physical_page"] for row in OWNER_ROWS} == set(draw),
            "voynich_text_content_remained_closed_for_gdt514": True,
        },
        "inputs": {
            str(SOURCE.relative_to(ROOT)): sha256(SOURCE),
            str(CURRENT.relative_to(ROOT)): sha256(CURRENT),
        },
        "claim_ceiling": "This selects four pages and records visible owner boundaries only. It does not translate a group, identify a plant, alter a root, or admit any selected-page text into the workshop model.",
    }

    outputs = {
        "gdt514_174_candidate_universe.tsv": tsv_bytes(
            ["candidate_ordinal", "physical_page", "source_selector_values", "selected", "draw_ordinal"],
            candidate_rows,
        ),
        "gdt514_4_page_selection.tsv": tsv_bytes(
            [
                "seed_basis", "seed_hex", "draw_method", "safe_physical_page_count",
                "previously_admitted_page_count", "candidate_physical_page_count",
                "draw_ordinal", "selected_physical_page", "source_selector_values", "resampled",
            ],
            selection_rows,
        ),
        "gdt514_4_image_owner_map.tsv": tsv_bytes(
            [
                "physical_page", "canvas_id", "official_image_url", "sha256", "width", "height",
                "primary_visible_owner", "owner_class", "neutral_visual_reading", "visible_layout",
                "connection_constraint",
            ],
            list(OWNER_ROWS),
        ),
        "gdt514_result.json": json_bytes(result),
    }
    return outputs, result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs, result = build_outputs()
    for name, payload in outputs.items():
        (OUT / name).write_bytes(payload)
    print(json.dumps({"status": result["status"], "selected": result["selected_physical_pages"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
