#!/usr/bin/env python3
"""Build the compact four-page creative workshop reality check.

The transcription is materialized only through the guarded query command and
only for the four newly admitted physical pages.  This is a sidequest builder,
not a semantic scorer.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
DICTIONARY = (
    ROOT
    / "experiments/yolo/sidequest_semantic_zero_learned_whole_roots_nine_hundred_eighth"
    / "NINE_HUNDRED_EIGHTH_231_ZERO_WHOLE_ROOT_CARD_DICTIONARY.tsv"
)
RESULT = BASE / "NINE_HUNDRED_NINTH_FOUR_PAGE_RESULT.tsv"
SUMMARY = BASE / "NINE_HUNDRED_NINTH_BUILD_SUMMARY.json"

UNITS = [
    {
        "unit": "f13r",
        "pages": ["f13r"],
        "register": "HERBAL",
        "visual_reading": "ONE_PICTURED_PLANT_WITH_WRAPPED_ARTICLE_TEXT",
        "working_outcome": "PLANT_OWNER_SURVIVES__LOCAL_CONTENT_TAIL_RETURNS",
    },
    {
        "unit": "f75r",
        "pages": ["f75r"],
        "register": "BIOLOGICAL",
        "visual_reading": "STACKED_FIGURES_IN_GREEN_BATH_OR_FLOW_ZONES",
        "working_outcome": "HOW_DECK_TRANSFERS__BATHING_SCENE_NOT_ONE_MACHINE",
    },
    {
        "unit": "f70v",
        "pages": ["f70v1", "f70v2"],
        "register": "ZODIAC",
        "visual_reading": "PISCES_AND_ARIES_WHEELS_WITH_STAR_HOLDING_FIGURES",
        "working_outcome": "ZODIAC_LOOKUP_CONFIRMED__LABEL_NOMENCLATOR_DOMINATES",
    },
    {
        "unit": "f88r",
        "pages": ["f88r"],
        "register": "PHARMA",
        "visual_reading": "THREE_JARS_WITH_THREE_PICTURED_ROOT_AND_LEAF_SETS",
        "working_outcome": "TECHNICAL_PROSE_TRANSFERS__ZERO_WHOLE_ROOTS_FAILS_ON_LABELS",
    },
]

# ZL3b keeps the seven short f75r figure captions in the generic P class.
# The picture, not the source kind code, identifies them as labels.
VISUAL_LABEL_LOCI = {
    "f75r.47",
    "f75r.48",
    "f75r.49",
    "f75r.50",
    "f75r.51",
    "f75r.52",
    "f75r.53",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_rows(page: str) -> list[dict[str, str]]:
    if page.lower().startswith("f84"):
        raise ValueError("sealed page requested")
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(SOURCE),
        "--selector",
        "page",
        "--allow",
        page,
        "--columns",
        "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix",
        "f84",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if not rows or {row["page"] for row in rows} != {page}:
        raise RuntimeError(f"guarded page load failed for {page}")
    return rows


def main() -> int:
    known_surfaces: set[str] = set()
    with DICTIONARY.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            known_surfaces.update(row["surface_forms"].split(" | "))

    all_tokens: list[str] = []
    output: list[dict[str, str | int]] = []
    for spec in UNITS:
        rows = [row for page in spec["pages"] for row in guarded_rows(page)]
        tokens = [token for row in rows for token in row["eva_clean"].split()]
        exact = [token for token in tokens if token in known_surfaces]
        prose = sum(
            int(row["token_count"])
            for row in rows
            if row["kind"] == "P" and row["locus"] not in VISUAL_LABEL_LOCI
        )
        diagram = len(tokens) - prose
        output.append(
            {
                "unit": spec["unit"],
                "source_pages": "|".join(spec["pages"]),
                "register": spec["register"],
                "loci": len(rows),
                "groups": len(tokens),
                "unique_surfaces": len(set(tokens)),
                "prose_groups": prose,
                "label_or_circle_groups": diagram,
                "exact_old_surface_groups": len(exact),
                "exact_old_surface_types": len(set(exact)),
                "exact_old_surface_rate": f"{len(exact) / len(tokens):.6f}",
                "visual_reading": spec["visual_reading"],
                "working_outcome": spec["working_outcome"],
            }
        )
        all_tokens.extend(tokens)

    exact_all = [token for token in all_tokens if token in known_surfaces]
    output.append(
        {
            "unit": "TOTAL",
            "source_pages": "f13r|f75r|f70v1|f70v2|f88r",
            "register": "FOUR_PAGE_REALITY_CHECK",
            "loci": sum(int(row["loci"]) for row in output),
            "groups": len(all_tokens),
            "unique_surfaces": len(set(all_tokens)),
            "prose_groups": sum(int(row["prose_groups"]) for row in output),
            "label_or_circle_groups": sum(int(row["label_or_circle_groups"]) for row in output),
            "exact_old_surface_groups": len(exact_all),
            "exact_old_surface_types": len(set(exact_all)),
            "exact_old_surface_rate": f"{len(exact_all) / len(all_tokens):.6f}",
            "visual_reading": "FOUR_DISTINCT_OWNER_REGISTERS",
            "working_outcome": "MIXED_PRODUCTIVE_GRAMMAR_PLUS_LOCAL_NOMENCLATOR",
        }
    )

    fields = list(output[0])
    with RESULT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    summary = {
        "status": "BUILT",
        "decision": "MIXED_PRODUCTIVE_GRAMMAR_PLUS_LOCAL_NOMENCLATOR",
        "physical_pages": 4,
        "source_page_selectors": 5,
        "loci": output[-1]["loci"],
        "groups": output[-1]["groups"],
        "unique_surfaces": output[-1]["unique_surfaces"],
        "exact_old_surface_groups": output[-1]["exact_old_surface_groups"],
        "dictionary_sha256": sha(DICTIONARY),
        "result_sha256": sha(RESULT),
        "sealed_pages_accessed": 0,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
