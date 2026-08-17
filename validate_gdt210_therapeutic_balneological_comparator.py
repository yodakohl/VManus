#!/usr/bin/env python3
"""Validate GDT210 inventories, comparison counts, scope, and bindings."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt210_balneological_image_manifest.tsv"
OBS = R / "gdt210_balneological_observations.tsv"
COMPARISON = R / "gdt210_theory_comparison.tsv"
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"
RESULT = R / "gdt210_result.json"
OUT = R / "gdt210_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf8"))
    images, observations = read(MANIFEST), read(OBS)
    comparisons, visual = read(COMPARISON), read(VISUAL)
    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_RESULT_V1")
    check("status", result["status"] == "THERAPEUTIC_BALNEOLOGY_LEADING_Q13_CONTENT_THEORY_HYDRAULIC_HYBRID_PROVISIONAL")
    check("four_images", len(images) == 4 and len({r["image_id"] for r in images}) == 4)
    check("folios", [r["folio"] for r in images] == ["9r", "19r", "21r", "25r"])
    check("one_manuscript", {r["manuscript"] for r in images} == {"MS G.74"})
    check("authority", {r["authority"] for r in images} == {"Morgan Library & Museum"})
    check("image_hashes", [r["retrieved_image_sha256"] for r in images] == [
        "0d750fbd776556d7d964a7e599c29494a3026ba8bfe4085b2794f2d9d9ef4c7a",
        "9a60ceb1e1a28b41b020cf89a6d35c595c5cff2d370c3a0e90afe4df47e957ac",
        "58931edd9c49b45878dd2afb4b8fb5061271db5cb5598d928053ebe590a3d192",
        "e85e5574c9020aa99256b1b3c5d994f4413b307b524f24c6bbbd4d9d06352f38",
    ])
    check("nine_observations", len(observations) == 9 and len({r["observation_id"] for r in observations}) == 9)
    check("observations_resolve", {r["image_id"] for r in observations} <= {r["image_id"] for r in images})
    check("direct_provenance", all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in observations))
    check("thirteen_axes", len(comparisons) == 13 and [r["axis_id"] for r in comparisons] == [f"A{i:02d}" for i in range(1, 14)])
    check("six_bath_leads", sum(r["assessment"] == "BALNEOLOGY_SPECIFIC_LEAD" for r in comparisons) == 6)
    check("one_alch_lead", sum(r["assessment"] == "ALCHEMICAL_HYDRAULIC_SECONDARY_LEAD" for r in comparisons) == 1)
    check("exact_absent", comparisons[-1]["assessment"] == "EXACT_HOMOLOG_ABSENT")
    pages = {r["page"] for r in visual}
    check("five_frozen_q13_pages", pages == {"f77r", "f78v", "f81r", "f82v", "f83r"})
    check("no_f84", not any(r["page"].startswith("f84") for r in visual))
    check("counts", result["counts"] == {
        "external_images": 4, "direct_visual_observations": 9,
        "comparison_axes": 13, "balneology_specific_leads": 6,
        "alchemical_hydraulic_secondary_leads": 1,
        "exact_translation_bridges": 0,
    })
    check("posthoc", result["analysis_status"] == "POSTHOC_EXPLORATORY_THEORY_RANKING")
    check("negative_gates", not result["gates"]["cross_page_duct_explained_by_bath_comparator"] and not result["gates"]["singular_readable_label_bridge"] and not result["gates"]["translation_authorized"])
    check("f84", result["f84"] == {"input_rows": 0, "formal_payload_accessed": False, "image_opened": False})
    for section in ("inputs", "implementation", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(R / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", csha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT210_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent retained-image, observation, theory-axis, f84 exclusion, posthoc-status, claim, content-hash, and file-binding validation; no image-content reinspection.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
