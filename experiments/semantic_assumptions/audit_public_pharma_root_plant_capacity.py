#!/usr/bin/env python3
"""PFR001 source-metadata capacity audit; no Voynich strings are selected."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
ATLAS_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
CROSSWALK_VALIDATION = RESULTS / "existing_human_current_locus_crosswalk_validation.json"
OUT = RESULTS / "public_pharma_root_plant_capacity.json"
REPORT = RESULTS / "public_pharma_root_plant_capacity.md"

PUBLIC_URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)
PUBLIC_SOURCE_SHA256 = "9267a2bbf2d485320ce8baaa2e3eeaccb6be7a02aa81ee9422a39ba00bef420a"
EXPECTED_INPUTS = {
    "results/existing_human_label_annotations.tsv":
        "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    "results/existing_human_current_locus_crosswalk.tsv":
        "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    "results/existing_human_annotation_atlas_validation.json":
        "25c0642753974fec0b0646a22dc379e439242954f048ab778cc8df7c85442673",
    "results/existing_human_current_locus_crosswalk_validation.json":
        "d00c9fecd5f9a2bb282d47053cf88404b78dd591131a7c207a65e7267c9f95eb",
}

ANNOTATION_FIELDS = {
    "source_record_id", "section", "page", "object_class", "object_guess", "certainty"
}
CROSSWALK_FIELDS = {"source_record_id", "current_page", "primary_eligible"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projected_rows(path: Path, fields: set[str]) -> list[dict[str, str]]:
    """Retain only declared metadata columns; no transcription field is selected."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        assert len(header) == len(set(header))
        indexes = {field: header.index(field) for field in fields}
        return [{field: row[index] for field, index in indexes.items()} for row in reader]


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    assert match
    return match.group(0)


def summarize(rows: list[dict[str, str]], page_key: str) -> dict[str, object]:
    pages: dict[str, Counter[str]] = defaultdict(Counter)
    folios: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        page = row[page_key]
        state = row["object_guess"]
        pages[page][state] += 1
        folios[folio(page)][state] += 1
    mixed_pages = {page: counts for page, counts in pages.items() if len(counts) == 2}
    mixed_folios = {name: counts for name, counts in folios.items() if len(counts) == 2}
    orbit = math.prod(
        math.comb(sum(counts.values()), counts["root"])
        for counts in mixed_pages.values()
    )
    return {
        "rows": len(rows),
        "class_counts": dict(sorted(Counter(row["object_guess"] for row in rows).items())),
        "page_counts": {
            page: dict(sorted(counts.items())) for page, counts in sorted(pages.items())
        },
        "folio_counts": {
            name: dict(sorted(counts.items())) for name, counts in sorted(folios.items())
        },
        "class_folio_support": {
            state: sum(counts[state] > 0 for counts in folios.values())
            for state in ("plant", "root")
        },
        "mixed_pages": {
            page: dict(sorted(counts.items())) for page, counts in sorted(mixed_pages.items())
        },
        "mixed_folios": {
            name: dict(sorted(counts.items())) for name, counts in sorted(mixed_folios.items())
        },
        "within_mixed_page_assignment_orbit": orbit,
        "within_mixed_page_minimum_one_sided_p": 1.0 / orbit,
    }


def build_report(result: dict[str, object]) -> str:
    mapped = result["mapped_primary_panel"]
    return f"""# Public pharmaceutical root-versus-plant capacity

Decision: **{result['decision']}**.

The public Stolfi/Grove catalogue supplies 154 unhedged pharmaceutical
fragment-label records (113 `plant`, 41 `root`). The validated current-locus
crosswalk retains **{mapped['rows']}** primary records: **90 plant and 28 root**.
No Voynich label string, transcription, root, role, grammar feature, OCR, or
image model was selected or scored.

The apparent sample size is misleading. `root` occurs on only f89 and f99.
Only two pages mix the classes: f89r1 has 8 plant labels and one root label;
f99v has 14 root labels and one plant label. These are also the only two mixed
physical folios. A folio-synchronous sign orbit therefore has only four states
and minimum one-sided p = **1/4 = 0.25**. The 135 label-level within-page
assignments have a nominal floor of 1/135, but depend on one minority item in
each direction and cannot establish transfer beyond two folios. Holding out
f99 leaves only one mapped root example for training.

All four frozen capacity gates fail. Stop before any text score. This does not
show that root-only and plant-fragment labels are identical; it shows that the
current public annotations cannot distinguish a general register contrast from
f89/f99 page production. Reopen only with additional explicit unhedged
root-only labels on independently mixed folios. `root` and `plant` remain human
catalogue classes, not Voynich translations.

Public source: {PUBLIC_URL}
"""


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    actual_inputs = {
        str(path.relative_to(BASE)): sha(path)
        for path in (ANNOTATIONS, CROSSWALK, ATLAS_VALIDATION, CROSSWALK_VALIDATION)
    }
    assert actual_inputs == EXPECTED_INPUTS
    atlas = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    cross_validation = json.loads(CROSSWALK_VALIDATION.read_text(encoding="utf-8"))
    assert atlas["status"] == "PASS_EXISTING_HUMAN_ANNOTATION_ATLAS_VALIDATION"
    assert cross_validation["status"] == "PASS_INDEPENDENT_CLUSTERED_CURRENT_LOCUS_CROSSWALK_VALIDATION"
    assert atlas["source_hashes"][
        "experiments/semantic_assumptions/cache/existing_human_annotations/labtit-best.idx"
    ] == PUBLIC_SOURCE_SHA256

    annotations = projected_rows(ANNOTATIONS, ANNOTATION_FIELDS)
    crosswalk = {
        row["source_record_id"]: row for row in projected_rows(CROSSWALK, CROSSWALK_FIELDS)
    }
    source = [
        row for row in annotations
        if row["section"] == "pharma"
        and row["object_class"] == "P"
        and row["certainty"] == "UNHEDGED"
        and row["object_guess"] in {"plant", "root"}
    ]
    assert len({row["source_record_id"] for row in source}) == len(source)
    mapped = []
    for row in source:
        match = crosswalk[row["source_record_id"]]
        if match["primary_eligible"] == "1":
            mapped.append({**row, "current_page": match["current_page"]})

    source_summary = summarize(source, "page")
    mapped_summary = summarize(mapped, "current_page")
    assert source_summary["rows"] == 154
    assert source_summary["class_counts"] == {"plant": 113, "root": 41}
    assert mapped_summary["rows"] == 118
    assert mapped_summary["class_counts"] == {"plant": 90, "root": 28}
    assert mapped_summary["mixed_pages"] == {
        "f89r1": {"plant": 8, "root": 1},
        "f99v": {"plant": 1, "root": 14},
    }
    assert mapped_summary["mixed_folios"] == {
        "f89": {"plant": 15, "root": 1},
        "f99": {"plant": 1, "root": 27},
    }
    assert mapped_summary["within_mixed_page_assignment_orbit"] == 135

    folio_counts = mapped_summary["folio_counts"]
    mixed_folios = mapped_summary["mixed_folios"]
    held_minimums = {}
    for held in mixed_folios:
        held_minimums[held] = {
            state: sum(counts.get(state, 0) for name, counts in folio_counts.items() if name != held)
            for state in ("plant", "root")
        }
    minority = Counter()
    for counts in mapped_summary["mixed_pages"].values():
        minority[min(counts, key=counts.get)] += min(counts.values())
    gates = {
        "both_classes_on_at_least_five_folios": min(mapped_summary["class_folio_support"].values()) >= 5,
        "at_least_five_mixed_folios": len(mixed_folios) >= 5,
        "every_held_mixed_folio_has_five_training_labels_per_class": all(
            min(counts.values()) >= 5 for counts in held_minimums.values()
        ),
        "three_minority_labels_in_each_direction": all(minority[state] >= 3 for state in ("plant", "root")),
    }
    assert gates == {key: False for key in gates}
    result = {
        "experiment_id": "PFR001",
        "status": "STOP_UNSCORED_PAGE_AND_FOLIO_CONFOUNDED",
        "decision": "STOP_BEFORE_ANY_VOYNICH_STRING_OR_GRAMMAR_SCORE",
        "public_source": {"url": PUBLIC_URL, "sha256": PUBLIC_SOURCE_SHA256},
        "inputs": actual_inputs,
        "source_catalogue_panel": source_summary,
        "mapped_primary_panel": mapped_summary,
        "held_folio_training_counts": held_minimums,
        "mixed_page_minority_counts": dict(sorted(minority.items())),
        "physical_folio_sign_orbit": 4,
        "physical_folio_minimum_one_sided_p": 0.25,
        "gates": gates,
        "voynich_string_columns_selected": False,
        "semantic_or_grammar_score_computed": False,
        "ocr_or_automated_vision_used": False,
        "claim_ceiling": (
            "Public metadata provide only two mixed folios, each driven by one minority label; "
            "no root/plant label-register difference, Voynich meaning, plaintext, or translation follows."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(build_report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
