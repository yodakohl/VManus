#!/usr/bin/env python3
"""Validate GDT514's guarded universe, one-time draw, and owner map."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
PRODUCER = HERE / "src/run.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def rows(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8")), delimiter="\t"))


def main() -> int:
    spec = importlib.util.spec_from_file_location("gdt514_producer", PRODUCER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load producer")
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    expected, result = producer.build_outputs()

    checks: list[str] = []
    for name, payload in expected.items():
        require((OUT / name).read_bytes() == payload, f"byte_exact_{name}", checks)

    candidates = rows(expected["gdt514_174_candidate_universe.tsv"])
    selection = rows(expected["gdt514_4_page_selection.tsv"])
    owners = rows(expected["gdt514_4_image_owner_map.tsv"])
    selected = [row["selected_physical_page"] for row in selection]

    require(len(candidates) == 174, "candidate_count_174", checks)
    require(len({row["physical_page"] for row in candidates}) == 174, "candidate_pages_unique", checks)
    require(len(selection) == 4, "selection_count_4", checks)
    require(selected == ["f31r", "f66r", "f20v", "f4r"], "selection_order_exact", checks)
    require(all(row["resampled"] == "NO" for row in selection), "selection_not_resampled", checks)
    require(all(row["candidate_physical_page_count"] == "174" for row in selection), "selection_candidate_arithmetic", checks)
    require(sum(row["selected"] == "YES" for row in candidates) == 4, "candidate_selection_flags_4", checks)
    require({row["physical_page"] for row in candidates if row["selected"] == "YES"} == set(selected), "candidate_flags_match_draw", checks)
    require(all(not row["physical_page"].startswith("f84") for row in candidates), "candidate_universe_forbidden_free", checks)
    require(all(not row["source_selector_values"].startswith("f84") for row in candidates), "selector_values_forbidden_free", checks)
    require(len(owners) == 4, "owner_row_count_4", checks)
    require({row["physical_page"] for row in owners} == set(selected), "owner_pages_match_selection", checks)
    require(sum(row["owner_class"] == "DIRECT_VISIBLE_WHOLE_PLANT" for row in owners) == 3, "three_whole_plant_owner_pages", checks)
    require(sum(row["owner_class"] == "VISIBLE_PROSE_BLOCK_NO_OBJECT" for row in owners) == 1, "one_text_block_owner_page", checks)
    require(all(row["official_image_url"].startswith("https://collections.library.yale.edu/iiif/2/") for row in owners), "official_yale_images", checks)
    require(all(len(row["sha256"]) == 64 for row in owners), "image_hashes_complete", checks)
    require(all(int(row["width"]) > 2600 and int(row["height"]) > 3600 for row in owners), "original_dimensions_recorded", checks)
    require(all(row["connection_constraint"] for row in owners), "connection_constraints_complete", checks)
    require(all(result["gates"].values()), "all_result_gates_true", checks)
    require(result["selected_source_values"] == selected, "one_source_selector_per_selected_page", checks)
    require(result["counts"]["safe_physical_pages"] == 200, "safe_physical_count_200", checks)
    require(result["counts"]["previously_admitted_physical_pages"] == 26, "admitted_count_26", checks)
    require(result["counts"]["guarded_skipped_forbidden_rows"] > 0, "guard_actually_skipped_forbidden_rows", checks)
    require("eva_clean" not in b"".join(expected.values()).decode("utf-8"), "no_text_column_materialized", checks)

    validation = {
        "experiment_id": "GDT514",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha256(expected["gdt514_result.json"]),
        "producer_sha256": sha256(PRODUCER.read_bytes()),
        "selected_physical_pages": selected,
    }
    (OUT / "gdt514_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": len(checks), "selected": selected}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
