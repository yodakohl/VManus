#!/usr/bin/env python3
"""Independent nonimporting validation of the EAS001 provenance hold."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULT = BASE / "results" / "eas001_provenance_bifolio_reaudit.json"
OUT = BASE / "results" / "eas001_provenance_bifolio_reaudit_validation.json"
REPORT = BASE / "results" / "eas001_provenance_bifolio_reaudit_validation.md"
RESET = "900c22f39a0baa1e57839c4190c420c9240dc185"
MANIFEST = "archive_pre_reset_2026-08-06/ARCHIVE_MANIFEST.tsv"
EXPECTED = {
    "semantic_assumptions/freeze_explicit_array_slot_record_boundary_manifest.py": "98fdd38c2c37c262ebb7177a963f848844e98ff65556fad70d6611c230ac36fd",
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen.json": "65b963386b76e8030c7e62eb6c56ef2ba6967c8f3e0a3a421a55e58e438d5285",
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen.tsv": "51e46ec6bff415adbf15bc073582940e0efc4f1cd4f20ef639da8df8aa7bf211",
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen_report.md": "4f510b6b90a068f20e6b487fa0982761b050d4abc5663ff49ab55dc2d606add9",
    "semantic_assumptions/results/explicit_array_slot_record_boundary_slots_frozen.tsv": "0e8bae8e4fc68ac591ecd7ba32e681cd7fa10df993f4f525b52fcaf15f9acac4",
}
EXPECTED_SIZES = {
    "98fdd38c2c37c262ebb7177a963f848844e98ff65556fad70d6611c230ac36fd": 19449,
    "65b963386b76e8030c7e62eb6c56ef2ba6967c8f3e0a3a421a55e58e438d5285": 6520,
    "51e46ec6bff415adbf15bc073582940e0efc4f1cd4f20ef639da8df8aa7bf211": 8600,
    "4f510b6b90a068f20e6b487fa0982761b050d4abc5663ff49ab55dc2d606add9": 1908,
    "0e8bae8e4fc68ac591ecd7ba32e681cd7fa10df993f4f525b52fcaf15f9acac4": 24397,
}


def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL)


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[bool] = []
    ledger = list(csv.DictReader((BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv").open(), delimiter="\t"))
    rows = [r for r in ledger if "EAS001" in r["experiment"] or r["experiment"] == "explicit_array_slot_boundary_route_audit"]
    checks += [len(rows) == 11]
    scientific = [r for r in result["named_paths"] if not r["bookkeeping_only"]]
    checks += [len(scientific) == 9]
    checks.extend(not (ROOT / row["resolved_path"]).exists() for row in scientific)
    manifest = sh("git", "show", f"{RESET}:{MANIFEST}")
    parsed = {row[0]: row[2] for row in csv.reader(manifest.splitlines(), delimiter="\t") if row and row[0] in EXPECTED}
    checks += [parsed == EXPECTED]
    names = sh("git", "rev-list", "--all", "--objects").lower()
    checks += ["eas001" not in names, "explicit_array_slot_boundary" not in names]
    dangling = sh("git", "fsck", "--full", "--no-reflogs", "--unreachable")
    dangling_names: list[str] = []
    for line in dangling.splitlines():
        if "unreachable commit" not in line:
            continue
        tree_names = sh("git", "ls-tree", "-r", "--name-only", line.split()[2])
        dangling_names.extend(
            name for name in tree_names.splitlines()
            if "eas001" in name.lower() or "explicit_array_slot" in name.lower()
        )
    checks += [dangling_names == [], result["dangling_eas001_path_hits"] == []]
    object_rows = sh(
        "git", "cat-file", "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
    )
    matching_blobs: dict[str, list[str]] = {digest: [] for digest in EXPECTED_SIZES}
    sizes = set(EXPECTED_SIZES.values())
    for line in object_rows.splitlines():
        oid, kind, size = line.split()
        if kind != "blob" or int(size) not in sizes:
            continue
        payload = subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT)
        digest = hashlib.sha256(payload).hexdigest()
        if digest in matching_blobs:
            matching_blobs[digest].append(oid)
    checks += [all(not values for values in matching_blobs.values())]
    checks += [all(
        not record["matching_git_blobs"]
        for record in result["reset_manifest_precursors"].values()
    )]
    bifolio = json.loads((BASE / "results" / "public_circle_bifolio_class_capacity.json").read_text())
    checks += [bifolio["scope"] == {"bifolio_units": 4, "extant_folios": 7, "panels": 26}]
    checks += [result["exact_13_folio_membership_recovered"] is False]
    checks += [result["per_folio_effects_recovered"] is False]
    checks += [result["bifolio_clustered_inference_recomputable"] is False]
    checks += [not any(result["gates"].values())]
    checks += [result["status"] == "PROVISIONAL_HISTORICAL_UNRECONSTRUCTED"]
    checks += [result["decision"] == "HOLD_EAS001_AND_DEPENDENT_CLAIMS_UNTIL_ARTIFACT_RECOVERY_OR_NEW_VERSION"]
    checks += [result["ocr_or_automated_vision_used"] is False]
    checks += [result["manuscript_text_or_score_accessed"] is False]
    checks += ["not currently reproducible evidence" in result["claim_ceiling"]]
    if not all(checks):
        raise SystemExit(f"validation failed: {[i for i, ok in enumerate(checks) if not ok]}")
    payload = {
        "status": "PASS_INDEPENDENT_EAS001_PROVENANCE_HOLD_RECONSTRUCTION",
        "checks": len(checks),
        "failures": 0,
        "scientific_named_paths_absent": len(scientific),
        "reset_manifest_precursors": len(parsed),
        "public_extant_folios": bifolio["scope"]["extant_folios"],
        "public_bifolio_units": bifolio["scope"]["bifolio_units"],
        "result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "decision": result["decision"],
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# EAS001 provenance re-audit validation\n\n"
        f"PASS: {len(checks)} independent checks reproduce the nine absent scientific paths, "
        "five reset-manifest precursor hashes, lack of reachable EAS001 paths, public "
        "seven-folio/four-bifolio correction, and provenance HOLD. The historical numeric "
        "summary is preserved but not reconstructed.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
