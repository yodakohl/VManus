#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


HERE = Path(__file__).resolve().parent.parent
ROOT = find_repo_root(HERE)
OUT = HERE / "artifacts"
EXPECTED_INPUTS = {
    "experiments/yolo/gdt607_boundary_word_disentanglement/artifacts/role_attack/REPORT.md":
        "456e56b7b06fe18ef1de72b13d0f0a855c2de566dd04761dd3be03845d66e02a",
    "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/RESULT.json":
        "eb29781a398f661e51ce30c1223fa227d9bdd03f469ef984a7c877eb1bfd2148",
    "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/stable_stem_role_summary.tsv":
        "4c385f59520e4b9ebc9c75274eb1ff8a28efc340b12ccad29754e085d866012b",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks = []

    def check(label, condition, observed=None):
        checks.append({
            "check": label,
            "status": "PASS" if condition else "FAIL",
            "observed": observed,
        })

    observed_inputs = {}
    for relative, expected in EXPECTED_INPUTS.items():
        path = ROOT / relative
        observed = sha(path)
        observed_inputs[relative] = observed
        check("input hash " + relative, observed == expected, observed)

    model_check = subprocess.run(
        [sys.executable, str(HERE / "src/validate_model.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    check("model validator exits zero", model_check.returncode == 0, model_check.returncode)
    check("model validator completion", "VALIDATION_OK" in model_check.stdout, model_check.stdout.splitlines()[-1:] or [])

    candidates = read_tsv(OUT / "candidate_grid.tsv")
    sources = read_tsv(OUT / "source_evidence.tsv")
    model = json.loads((OUT / "model_v1.json").read_text(encoding="utf-8"))
    result = json.loads((OUT / "RESULT.json").read_text(encoding="utf-8"))
    by_id = {row["candidate_id"]: row for row in candidates}

    check("eight candidate systems", len(candidates) == 8, len(candidates))
    check("eleven historical sources", len(sources) == 11, len(sources))
    check("candidate identifiers unique", len(by_id) == len(candidates), sorted(by_id))
    check("medical overlay highest form fit", int(by_id["MEDICAL_RECIPE"]["observed_fit_0_15"]) == 14, by_id["MEDICAL_RECIPE"]["observed_fit_0_15"])
    check("common abbreviation core score", int(by_id["LATIN_COMMON"]["observed_fit_0_15"]) == 12, by_id["LATIN_COMMON"]["observed_fit_0_15"])
    check("nomenclator only capacity calibrator", by_id["DIPLOMATIC_NOM"]["recommendation"] == "CAPACITY_AND_NULL_CALIBRATOR", by_id["DIPLOMATIC_NOM"]["recommendation"])
    check("alchemy rejected as decoder prior", by_id["ALCHEMY_LATIN"]["recommendation"] == "REJECT_AS_DECODER_PRIOR", by_id["ALCHEMY_LATIN"]["recommendation"])

    source_ids = {row["source_id"] for row in sources}
    check("source identifiers unique", len(source_ids) == len(sources), sorted(source_ids))
    check("all source links https", all(row["url"].startswith("https://") for row in sources))
    check("all candidate source references resolve", all(set(row["source_ids"].split(";")) <= source_ids for row in candidates))
    check("all sources expose limitation", all(row["limitation"].strip() for row in sources))
    check("Tranchedini arithmetic warning retained", any(row["source_id"] == "S06" and "82" in row["limitation"] for row in sources))

    buckets = model["primitive_capacity"]["buckets"]
    bucket_counts = {row["role"]: row["count"] for row in buckets}
    check("model capacity declared 34", model["primitive_capacity"]["total"] == 34, model["primitive_capacity"]["total"])
    check("model buckets sum 34", sum(bucket_counts.values()) == 34, sum(bucket_counts.values()))
    check("literal count 18", bucket_counts["literal_carrier"] == 18, bucket_counts)
    check("syllabic count 4", bucket_counts["syllabic_carrier"] == 4, bucket_counts)
    check("prefix suffix count 3 each", bucket_counts["prefix_operator"] == bucket_counts["suffix_operator"] == 3, bucket_counts)
    check("connector context count 2 each", bucket_counts["connector"] == bucket_counts["context_abbreviation_mark"] == 2, bucket_counts)
    check("whole and null count one each", bucket_counts["wholeform_logogram"] == bucket_counts["null_layout"] == 1, bucket_counts)
    check("64 merges default composed", model["frequent_compounds"]["observed_merge_nodes"] == 64, model["frequent_compounds"])
    check("override maximum eight", model["frequent_compounds"]["lexicalized_override_max"] == 8, model["frequent_compounds"])
    check("whole-form override maximum four", model["frequent_compounds"]["wholeform_override_max"] == 4, model["frequent_compounds"])
    check("single null primitive", model["null_policy"]["primitive_slots_max"] == 1, model["null_policy"])
    check("null mass maximum 3 percent", model["null_policy"]["token_mass_max"] == 0.03, model["null_policy"])
    check(
        "qok whole-word shortcut forbidden",
        model["structural_anchor_priors"]["qok_singleton_family"]["forbidden_inference"]
        == "standalone_implies_word_or_long_output",
        model["structural_anchor_priors"]["qok_singleton_family"],
    )

    check("result decision", result["decision"] == "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1_SELECTED", result["decision"])
    check("result primary core", result["primary_core"] == "LATIN_COMMON", result["primary_core"])
    check("result domain overlay", result["domain_overlay"] == "MEDICAL_RECIPE", result["domain_overlay"])
    check("result qok guard", result["target_attack_constraints"]["qok_standalone_implies_word"] is False)
    check("result count consistency", result["candidate_count"] == len(candidates) and result["source_count"] == len(sources), [result["candidate_count"], result["source_count"]])

    report = (HERE / "REPORT.md").read_text(encoding="utf-8")
    for phrase in (
        "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1_SELECTED",
        "allgemeine spätmittelalterliche Abbreviatur-FST",
        "kleiner Rezept/Medizin-Layer",
        "summieren sich allerdings zu **82**",
        "keine semantische Vorbelegung",
    ):
        check("report phrase " + phrase, phrase in report, phrase)

    failures = [row for row in checks if row["status"] == "FAIL"]
    validation = {
        "schema": "gdt609-historical-prior-validation-v1",
        "status": "FAIL" if failures else "PASS",
        "checks_passed": len(checks) - len(failures),
        "checks_failed": len(failures),
        "checks": checks,
        "decision": "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1_SELECTED",
        "claim_ceiling": "historically grounded decoder architecture and capacity prior only; no codebook, glyph value, language, plaintext or meaning",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
        "input_hashes": observed_inputs,
        "artifact_hashes": {
            name: sha(OUT / name)
            for name in ("candidate_grid.tsv", "source_evidence.tsv", "model_v1.json", "RESULT.json")
        },
        "source_hashes": {
            "REPORT.md": sha(HERE / "REPORT.md"),
            "src/validate_model.py": sha(HERE / "src/validate_model.py"),
            "src/validate.py": sha(HERE / "src/validate.py"),
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "checks_passed": validation["checks_passed"],
        "checks_failed": validation["checks_failed"],
        "sha256": sha(OUT / "VALIDATION.json"),
    }, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
