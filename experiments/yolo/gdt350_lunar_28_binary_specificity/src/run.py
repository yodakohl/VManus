#!/usr/bin/env python3
import csv
import hashlib
import json
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


def read_tsv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    panel_path = ART / "gdt350_source_panel.tsv"
    obs_path = ART / "gdt350_observations.tsv"
    counter_path = ART / "gdt350_counterexamples.tsv"
    freeze_path = ART / "gdt350_freeze.json"
    panel = read_tsv(panel_path)
    obs = read_tsv(obs_path)
    assert len(panel) == len(obs) == 6
    assert [r["witness_id"] for r in panel] == [r["witness_id"] for r in obs]
    core_ids = {r["witness_id"] for r in panel if r["panel_role"] == "CORE_28"}
    core = [r for r in obs if r["witness_id"] in core_ids]
    exact = [r for r in core if r["final_presentation_state"].startswith("EXACT_BINARY_ALTERNATION")]
    nonalt = [r for r in core if r["final_presentation_state"] == "COMPLETE_NONALTERNATING"]
    unresolved = [r for r in core if r["final_presentation_state"] == "UNRESOLVED_INCOMPLETE_OR_AMBIGUOUS"]
    non_georgian_exact = [r for r in exact if r["witness_id"] != "W001_A65"]
    assert len(core) == 5 and len(exact) == 2 and len(nonalt) == 1 and len(unresolved) == 2
    assert [r["witness_id"] for r in non_georgian_exact] == ["W002_BL_ADD_25435"]
    result = {
        "experiment": "GDT350",
        "status": "A65_28_BINARY_HAS_NON_GEORGIAN_COUNTEREXAMPLE",
        "decision": "A65_28_BINARY_HAS_NON_GEORGIAN_COUNTEREXAMPLE",
        "counts": {
            "all_witnesses": len(obs),
            "core_28_witnesses": len(core),
            "exact_binary_alternation": len(exact),
            "complete_nonalternating": len(nonalt),
            "unresolved": len(unresolved),
            "non_georgian_exact_counterexamples": len(non_georgian_exact),
            "direct_visual_review_rows": sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs),
            "counterexamples_logged": len(read_tsv(counter_path)),
        },
        "exact_witnesses": [r["witness_id"] for r in exact],
        "non_georgian_exact_witnesses": [r["witness_id"] for r in non_georgian_exact],
        "interpretation": {
            "system_compatibility": "RETAINS_BROAD_28_PLUS_BINARY_COMPATIBILITY",
            "georgian_cultural_specificity": "LOW",
            "absolute_medieval_prevalence": "UNRESOLVED_PURPOSIVE_SAMPLE",
            "voynich_table_transfer": "NOT_AUTHORIZED_TARGET_PHASE_AND_TRANSFER_CAPACITY_ABSENT",
        },
        "inputs": {
            str(panel_path.relative_to(ROOT)): sha(panel_path),
            str(obs_path.relative_to(ROOT)): sha(obs_path),
            str(counter_path.relative_to(ROOT)): sha(counter_path),
            str(freeze_path.relative_to(ROOT)): sha(freeze_path),
            str((EXP / "METHOD.md").relative_to(ROOT)): sha(EXP / "METHOD.md"),
            str((EXP / "SOURCE_AUDIT.md").relative_to(ROOT)): sha(EXP / "SOURCE_AUDIT.md"),
        },
        "documents": {str((EXP / "REPORT.md").relative_to(ROOT)): sha(EXP / "REPORT.md")},
        "access": {
            "voynich_source_tables_loaded": False,
            "voynich_images_opened": False,
            "voynich_formal_payload_opened": False,
            "voynich_target_scored": False,
            "f84_accessed": False,
            "ocr_or_automated_vision_used": False,
        },
        "validation_scope": "Independent source/result accounting and provenance checks; not a second visual review.",
        "claim_ceiling": "Independent non-Georgian external counterexample to unique A-65 28-member alternation only; no prevalence estimate, Voynich identification, slot alignment, origin, language, meaning, plaintext, or translation.",
    }
    (ART / "gdt350_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
