#!/usr/bin/env python3
"""Independently validate the retained GDT209 inventories and claims."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt209_external_image_manifest.tsv"
OBS = R / "gdt209_external_visual_observations.tsv"
COMPARISON = R / "gdt209_topology_comparison.tsv"
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"
RESULT = R / "gdt209_result.json"
OUT = R / "gdt209_validation.json"


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
    images = read(MANIFEST)
    observations = read(OBS)
    comparisons = read(COMPARISON)
    visual = read(VISUAL)
    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT209_DQE_APPARATUS_TOPOLOGY_RESULT_V1")
    check("status", result["status"] == "BROAD_ALCHEMICAL_APPARATUS_ECOLOGY_SUPPORTED_SPECIFIC_HOMOLOG_ABSENT")
    check("three_images", len(images) == 3 and len({r["image_id"] for r in images}) == 3)
    check("image_ids", [r["image_id"] for r in images] == ["WOLF_DQE_F40R", "OTHMER_MS7_F10R", "OTHMER_MS7_F36R"])
    check("official_sources", all("hab.de" in r["catalogue_url"] or "openn.library.upenn.edu" in r["catalogue_url"] for r in images))
    check("fixed_hashes", [r["retrieved_image_sha256"] for r in images] == [
        "84dc93ac2daaf14606b65bf062fa9a95653719d8dbb9a794990c062cf005622e",
        "a4a642ee373bec7ff29b600f9e12eb05707eb7fcc6613730d93d0fee5f88b941",
        "6a1d980fddcde7db2d9ed8bc72a2ddb710a343c10a376b55bbc1a6dc72ad7a31",
    ])
    check("dimensions", [r["pixel_dimensions"] for r in images] == ["1024x1353", "1427x1800", "1427x1800"])
    check("direct_provenance", all(r["evidence_class"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in images))
    check("nine_observations", len(observations) == 9 and len({r["observation_id"] for r in observations}) == 9)
    check("observation_images_resolve", {r["image_id"] for r in observations} <= {r["image_id"] for r in images})
    check("observation_provenance", all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" and r["interpretation"] == "OBSERVATION_ONLY" for r in observations))
    check("eleven_axes", len(comparisons) == 11 and [r["criterion_id"] for r in comparisons] == [f"T{i:02d}" for i in range(1, 12)])
    check("three_specific_differences", sum(r["verdict"] == "Q13_SPECIFIC_DIFFERENCE" for r in comparisons) == 3)
    check("bridge_absent", next(r for r in comparisons if r["criterion_id"] == "T10")["verdict"] == "TRANSLATION_BRIDGE_ABSENT")
    check("exact_absent", next(r for r in comparisons if r["criterion_id"] == "T11")["verdict"] == "EXACT_HOMOLOG_ABSENT")
    pages = {r["page"] for r in visual}
    check("five_q13_pages", pages == {"f77r", "f78v", "f81r", "f82v", "f83r"})
    check("no_f84_input", not any(r["page"].startswith("f84") for r in visual))
    check("counts", result["counts"] == {
        "external_images": 3, "direct_visual_observations": 9,
        "topology_axes": 11, "q13_specific_differences": 3,
        "exact_q13_homologs": 0, "readable_label_bridges": 0,
    })
    check("theory_update", result["theory_update"] == {
        "medical_alchemical_apparatus_class_plausibility": "STRENGTHENED",
        "direct_rupescissa_diagram_derivation": "NOT_SUPPORTED",
        "q13_iconographic_specificity": "LOW",
        "f77_four_plus_fifth_refinement": "POSTHOC_UNCONFIRMED",
    })
    check("negative_gates", not result["gates"]["figures_inside_connected_system_homolog"] and not result["gates"]["serial_stage_homolog"] and not result["gates"]["exact_f77_topology_homolog"] and not result["gates"]["translation_authorized"])
    check("f84", result["f84"] == {"input_rows": 0, "formal_payload_accessed": False, "image_opened": False})
    for section in ("inputs", "implementation", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(R / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", csha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT209_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent retained-image manifest, direct-observation, topology, f84 exclusion, claim, content-hash, and file-binding validation; no image-content reinspection.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
