#!/usr/bin/env python3
"""Freeze SME001 morphology labels separately from the anonymous matrix."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_panel.tsv"
ANON = HERE / "anonymous_unit_binding.tsv"
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
BINDING = HERE / "target_source_binding.tsv"
RESULT = HERE / "target_source_capacity.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_target_source_capacity.md"

DROP_PAGE = "f106r"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_stats(rows, field, low, high):
    eligible = [row for row in rows if row[field] in {low, high}]
    pages = sorted({row["page"] for row in rows})
    variable_pages = [
        page for page in pages
        if {row[field] for row in eligible if row["page"] == page} == {low, high}
    ]

    def stratum(predicate):
        kept = [row for row in eligible if predicate(row)]
        informative = [
            page for page in pages
            if {row[field] for row in kept if row["page"] == page} == {low, high}
        ]
        return {
            "rows": len(kept),
            "counts": dict(sorted(Counter(row[field] for row in kept).items())),
            "informative_pages": informative,
            "informative_page_count": len(informative),
            "informative_folios": len({page[:-1] for page in informative}),
        }

    max_ord = {page: max(int(row["star_ordinal"]) for row in rows if row["page"] == page) for page in pages}
    return {
        "field": field,
        "low": low,
        "high": high,
        "rows": len(eligible),
        "counts": dict(sorted(Counter(row[field] for row in eligible).items())),
        "pages": len({row["page"] for row in eligible}),
        "folios": len({row["physical_folio"] for row in eligible}),
        "informative_pages": variable_pages,
        "informative_page_count": len(variable_pages),
        "informative_folios": len({page[:-1] for page in variable_pages}),
        "strata": {
            "ODD": stratum(lambda row: int(row["star_ordinal"]) % 2 == 1),
            "EVEN": stratum(lambda row: int(row["star_ordinal"]) % 2 == 0),
            "EARLY": stratum(lambda row: int(row["star_ordinal"]) <= max_ord[row["page"]] / 2),
            "LATE": stratum(lambda row: int(row["star_ordinal"]) > max_ord[row["page"]] / 2),
        },
    }


def main() -> None:
    source = {(row["page"], row["star_ordinal"], row["locus"]): row for row in read_tsv(SOURCE)}
    anonymous = read_tsv(ANON)
    assert len(anonymous) == 170
    dropped = [row for row in anonymous if row["page"] == DROP_PAGE]
    assert len(dropped) == 14
    retained = [row for row in anonymous if row["page"] != DROP_PAGE]
    assert len(retained) == 156

    output = []
    for row in retained:
        src = source[(row["page"], row["star_ordinal"], row["locus"])]
        output.append({
            "unit_id": row["unit_id"], "page": row["page"],
            "physical_folio": row["physical_folio"], "star_ordinal": row["star_ordinal"],
            "locus": row["locus"], "rays": src["rays"], "tail": src["tail"],
        })
    assert len({row["unit_id"] for row in output}) == 156
    assert len({row["page"] for row in output}) == 12
    assert len({row["physical_folio"] for row in output}) == 7

    fields = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "rays", "tail")
    with BINDING.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    ray = target_stats(output, "rays", "7", "8")
    tail = target_stats(output, "tail", "1", "2")
    assert ray["rows"] == 149 and ray["counts"] == {"7": 83, "8": 66}
    assert ray["informative_page_count"] == 12 and ray["informative_folios"] == 7
    assert ray["strata"]["ODD"]["informative_folios"] == 7
    assert ray["strata"]["EVEN"]["informative_folios"] == 7
    assert ray["strata"]["EARLY"]["informative_folios"] == 6
    assert ray["strata"]["LATE"]["informative_folios"] == 7
    assert tail["rows"] == 155 and tail["counts"] == {"1": 133, "2": 22}
    assert tail["informative_page_count"] == 8 and tail["informative_folios"] == 6
    assert tail["strata"]["ODD"]["informative_folios"] == 5
    assert tail["strata"]["EVEN"]["informative_folios"] == 4
    assert tail["strata"]["EARLY"]["informative_folios"] == 4
    assert tail["strata"]["LATE"]["informative_folios"] == 5

    sequences = {
        page: {
            "rays": "".join(row["rays"] for row in output if row["page"] == page),
            "tail": "".join(row["tail"] for row in output if row["page"] == page),
        } for page in sorted({row["page"] for row in output})
    }
    payload = {
        "experiment": "SME001",
        "status": "PASS_COMPLETE_PAGE_SEQUENCE_TARGET_SOURCE_CAPACITY_NO_TEXT_FEATURE_JOIN",
        "input_hashes": {str(SOURCE.relative_to(ROOT)): sha(SOURCE), str(ANON.relative_to(ROOT)): sha(ANON), str(MATRIX.relative_to(ROOT)): sha(MATRIX)},
        "dropped_complete_page": DROP_PAGE,
        "drop_reason": "one paragraph has unequal alternate-reading physical line sets; retaining the rest would splice the morphology sequence",
        "dropped_units": len(dropped),
        "rows": 156,
        "pages": 12,
        "folios": 7,
        "ray_7_vs_8": ray,
        "tail_1_vs_2": tail,
        "page_sequences": sequences,
        "binding_sha256": sha(BINDING),
        "text_feature_values_accessed": False,
        "morphology_to_feature_join_performed": False,
        "target_result_absent": not (HERE / "TARGET_RESULT.json").exists(),
        "claim_ceiling": "complete-page ray and tail sequence capacity only",
    }
    assert payload["target_result_absent"]
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT.write_text("\n".join([
        "# SME001 target-source sequence capacity", "", "## Decision", "",
        "**PASS — complete-page ray and tail sequences frozen; text features remain unjoined.**", "",
        "The anonymous matrix excludes one paragraph on f106r because IT2a lacks a physical line retained by ZL3b/RF1b. Removing only that entry would splice two nonadjacent morphology states and corrupt the page's run structure, so the entire 14-entry page is excluded before association scoring. The target-source panel retains 156 intact entries on 12 pages / seven physical folios.", "",
        "Seven-vs-eight rays retains 149 entries (83 vs 66); every page and all seven folios vary internally. Both odd/even strata remain informative on seven folios, and early/late strata on six/seven. One-vs-two tails retains 155 entries (133 vs 22), with internal variation on eight pages / six folios. Its odd/even and early/late strata retain five/four and four/five informative folios respectively. The one tail-less marker and rare six/nine-ray markers stay in the frozen sequences as ignored third states rather than being recoded.", "",
        "No text feature value was read or joined. This capacity pass supplies no ray/tail function, root association, meaning, lexeme, plaintext, language, or translation.", "",
        "## Reproduction", "", "```bash", "./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_target_source_binding.py", "```",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
