#!/usr/bin/env python3
import csv
import hashlib
import json
import re
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt350_lunar_28_binary_specificity"
ART = EXP / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    panel = rows(ART / "gdt350_source_panel.tsv")
    obs = rows(ART / "gdt350_observations.tsv")
    counters = rows(ART / "gdt350_counterexamples.tsv")
    result_path = ART / "gdt350_result.json"
    result = json.loads(result_path.read_text())
    freeze = json.loads((ART / "gdt350_freeze.json").read_text())
    checks = []

    def check(name, value):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    check("six_panel", len(panel) == 6)
    check("six_observations", len(obs) == 6)
    check("ordered_exact_join", [r["witness_id"] for r in panel] == [r["witness_id"] for r in obs])
    core_ids = {r["witness_id"] for r in panel if r["panel_role"] == "CORE_28"}
    core = [r for r in obs if r["witness_id"] in core_ids]
    exact = [r for r in core if r["final_presentation_state"].startswith("EXACT_BINARY_ALTERNATION")]
    nonalt = [r for r in core if r["final_presentation_state"] == "COMPLETE_NONALTERNATING"]
    unresolved = [r for r in core if r["final_presentation_state"] == "UNRESOLVED_INCOMPLETE_OR_AMBIGUOUS"]
    check("five_core", len(core) == 5)
    check("two_exact", len(exact) == 2)
    check("one_nonalternating", len(nonalt) == 1)
    check("two_unresolved", len(unresolved) == 2)
    check("a65_exact", exact[0]["witness_id"] == "W001_A65")
    check("bl_exact_counterexample", exact[1]["witness_id"] == "W002_BL_ADD_25435")
    check("pal1369_nonalternating", nonalt[0]["witness_id"] == "W004_PAL_LAT_1369")
    check("two_direct", sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs) == 2)
    check("source_direct_distinct", all(r["provenance"] in {"AI_DIRECT_VISUAL_OBSERVATION", "EXTERNAL_HUMAN_SOURCE_ASSERTION"} for r in obs))
    direct = [r for r in obs if r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION"]
    check("direct_urls_https", all(all(u.startswith("https://") for u in r["official_image_urls"].split(";")) for r in direct))
    check("direct_hashes", all(all(re.fullmatch(r"[0-9a-f]{64}", h) for h in r["image_sha256s"].split(";")) for r in direct))
    check("six_counterexamples", len(counters) == 6)
    check("counterexample_ids_unique", len({r["counterexample_id"] for r in counters}) == 6)
    check("decision", result["decision"] == "A65_28_BINARY_HAS_NON_GEORGIAN_COUNTEREXAMPLE")
    check("one_non_georgian", result["counts"]["non_georgian_exact_counterexamples"] == 1)
    check("exact_ids", result["exact_witnesses"] == ["W001_A65", "W002_BL_ADD_25435"])
    check("specificity_low", result["interpretation"]["georgian_cultural_specificity"] == "LOW")
    check("prevalence_unresolved", result["interpretation"]["absolute_medieval_prevalence"] == "UNRESOLVED_PURPOSIVE_SAMPLE")
    check("freeze_status", freeze["status"] == "FROZEN_EXTERNAL_PANEL_BEFORE_DIRECT_FACSIMILE_REVIEW")
    check("freeze_two_pending", freeze["counts"]["direct_review_pending"] == 2)
    check("all_hashes", all(sha(ROOT / p) == h for p, h in result["inputs"].items()))
    check("document_hashes", all(sha(ROOT / p) == h for p, h in result["documents"].items()))
    check("no_voynich_input_paths", all("semantic_assumptions/results" not in p for p in result["inputs"]))
    check("zero_voynich_access", not any(result["access"][k] for k in ["voynich_source_tables_loaded", "voynich_images_opened", "voynich_formal_payload_opened", "voynich_target_scored"]))
    check("no_f84_access", not result["access"]["f84_accessed"])
    check("no_automation", not result["access"]["ocr_or_automated_vision_used"])
    report = (EXP / "REPORT.md").read_text()
    check("report_status", "A65_28_BINARY_HAS_NON_GEORGIAN_COUNTEREXAMPLE" in report)
    check("claim_ceiling", "does not estimate prevalence" in report and "translation" in report)
    out = {
        "experiment": "GDT350",
        "status": "PASS",
        "checks": len(checks),
        "check_names": checks,
        "result_sha256": sha(result_path),
        "scope": "Independent accounting/provenance/hash validation; no independent visual reinspection.",
    }
    (ART / "gdt350_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
