#!/usr/bin/env python3
"""Validate GDT208 source records, comparison claims, counts, and bindings."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt208_external_source_manifest.tsv"
COMPARISON = R / "gdt208_structural_comparison.tsv"
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"
RESULT = R / "gdt208_result.json"
OUT = R / "gdt208_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf8"))
    sources = read(MANIFEST)
    comparisons = read(COMPARISON)
    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("schema", result["schema"] == "GDT208_MEDICAL_ALCHEMICAL_CIRCULATION_RESULT_V1")
    check("status", result["status"] == "MEDICAL_ALCHEMICAL_CIRCULATION_THEORY_STRENGTHENED_EXACT_TRANSLATION_KEY_ABSENT")
    check("four_sources", len(sources) == 4 and len({row["source_id"] for row in sources}) == 4)
    check("authority_mix", {row["authority_type"] for row in sources} == {"INSTITUTIONAL_CATALOGUE", "ACADEMIC_PRIMARY_MANUSCRIPT_STUDY", "INSTITUTIONAL_DERIVED_PUBLIC_IMAGE"})
    check("source_urls_https", all(row["source_url"].startswith("https://") for row in sources))
    image = next(row for row in sources if row["source_id"] == "DONUM_BL_2560_F7_IMAGE")
    check("image_digest", image["retrieved_image_sha256"] == "c53263e4ff60a4664143216464303e62f2a54753fed8a7855a4e7156df396990")
    check("visual_provenance", image["evidence_class"] == "AI_DIRECT_VISUAL_OBSERVATION")
    check("eleven_comparisons", len(comparisons) == 11 and [row["comparison_id"] for row in comparisons] == [f"C{i:02d}" for i in range(1, 12)])
    check("exact_homolog_absent", next(row for row in comparisons if row["comparison_id"] == "C08")["compatibility"] == "EXACT_HOMOLOG_ABSENT")
    check("translation_bridge_absent", next(row for row in comparisons if row["comparison_id"] == "C09")["compatibility"] == "TRANSLATION_BRIDGE_ABSENT")
    check("color_counterexample", next(row for row in comparisons if row["comparison_id"] == "C06")["compatibility"] == "COUNTEREXAMPLE_NO_EXACT_COLOR_PROGRAM")
    check("withdrawn_decoder_preserved", "withdrawn" in next(row for row in comparisons if row["comparison_id"] == "C10")["voynich_observation"])
    visual = read(VISUAL)
    pages = {row["page"] for row in visual}
    check("visual_rows", len(visual) == 5 and len(pages) == 5)
    check("q13_required_pages", {"f77r", "f78v", "f81r", "f82v", "f83r"} <= pages)
    check("q13_no_f84", not any(page.startswith("f84") for page in pages))
    check("counts", result["counts"] == {"external_source_records": 4, "structural_comparisons": 11, "non_f84_visual_evidence_pages": len(pages), "exact_homologs": 0, "singular_readable_voynich_bridges": 0})
    check("semantic_scope", result["semantic_status"] == "HYPOTHESIS_GENERATION_ONLY")
    check("gates", result["gates"] == {"near_contemporary_medical_distillation_context": True, "top_bottom_pipe_circulation_analogy": True, "personified_figure_in_vessel_analogy": True, "exact_f77_six_state_homolog": False, "singular_readable_voynich_label_bridge": False, "translation_authorized": False})
    check("f84_final_scope", result["f84"] == {"final_input_rows": 0, "superseded_builder_global_human_atlas_loaded_before_filter": True, "superseded_f84r_public_page_description_displayed": False, "superseded_f84r_public_page_description_retained_or_used": False, "f84r_transcription_or_formal_payload_accessed": False, "f84r_image_opened": False})
    for section in ("inputs", "implementation", "documents"):
        for filename, digest in result[section].items():
            check("hash:" + filename, sha(R / filename) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", csha(body) == stored)
    failed = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT208_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha(RESULT),
        "scope": "Independent source/comparison inventory, f84-free visual-evidence census, gate, access disclosure, claim, content-hash, and file-binding validation.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
