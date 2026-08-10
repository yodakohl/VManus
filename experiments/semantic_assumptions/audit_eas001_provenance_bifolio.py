#!/usr/bin/env python3
"""Audit whether the historical EAS001 positive result is reproducible."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
LEDGER = BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"
BIFOLIO = BASE / "results" / "public_circle_bifolio_class_capacity.json"
BIFOLIO_VALIDATION = BASE / "results" / "public_circle_bifolio_class_capacity_validation.json"
OUT = BASE / "results" / "eas001_provenance_bifolio_reaudit.json"
REPORT = BASE / "results" / "eas001_provenance_bifolio_reaudit.md"

AUDITED_COMMIT = "c755ab6bc5ac4be5d25089add8c567cd9dd722bf"
RESET_COMMIT = "900c22f39a0baa1e57839c4190c420c9240dc185"
CURATION_COMMIT = "2e8d49197641f16aa8e4abc6982601023b9b4cd6"
RESET_MANIFEST_PATH = "archive_pre_reset_2026-08-06/ARCHIVE_MANIFEST.tsv"
BIFOLIO_HASHES = {
    "experiments/semantic_assumptions/results/public_circle_bifolio_class_capacity.json":
        "286a8c2298849ae4e40239a1b38deacb4cafe81381c9861803a1e77f78566915",
    "experiments/semantic_assumptions/results/public_circle_bifolio_class_capacity_validation.json":
        "8947bacdf6178c998f33a47764dd235622802a0c57d9221c7175869aa792f629",
}
PRECURSORS = {
    "semantic_assumptions/freeze_explicit_array_slot_record_boundary_manifest.py":
        (19449, "98fdd38c2c37c262ebb7177a963f848844e98ff65556fad70d6611c230ac36fd"),
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen.json":
        (6520, "65b963386b76e8030c7e62eb6c56ef2ba6967c8f3e0a3a421a55e58e438d5285"),
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen.tsv":
        (8600, "51e46ec6bff415adbf15bc073582940e0efc4f1cd4f20ef639da8df8aa7bf211"),
    "semantic_assumptions/results/explicit_array_slot_record_boundary_manifest_frozen_report.md":
        (1908, "4f510b6b90a068f20e6b487fa0982761b050d4abc5663ff49ab55dc2d606add9"),
    "semantic_assumptions/results/explicit_array_slot_record_boundary_slots_frozen.tsv":
        (24397, "0e8bae8e4fc68ac591ecd7ba32e681cd7fa10df993f4f525b52fcaf15f9acac4"),
}
BOOKKEEPING_PATHS = {"tests/verify_reset.py", "hypotheses/ACTIVE_HYPOTHESES.tsv"}


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha_matches() -> dict[str, list[str]]:
    sizes = {size for size, _ in PRECURSORS.values()}
    wanted = {digest for _, digest in PRECURSORS.values()}
    records = run(
        "git", "cat-file", "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
    )
    matches = {digest: [] for digest in wanted}
    for line in records.splitlines():
        oid, kind, size_text = line.split()
        if kind != "blob" or int(size_text) not in sizes:
            continue
        payload = subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT)
        digest = hashlib.sha256(payload).hexdigest()
        if digest in matches:
            matches[digest].append(oid)
    return matches


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    assert run("git", "rev-parse", "HEAD").strip() == AUDITED_COMMIT
    for rel, expected in BIFOLIO_HASHES.items():
        assert sha(ROOT / rel) == expected

    ledger_rows = []
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if "EAS001" in row["experiment"] or row["experiment"] == "explicit_array_slot_boundary_route_audit":
                ledger_rows.append(row)
    assert len(ledger_rows) == 11
    path_records = []
    for row in ledger_rows:
        named = row["primary_report"]
        resolved = ROOT / named if named.startswith("archive_pre_reset") else BASE / named
        path_records.append({
            "experiment": row["experiment"],
            "named_path": named,
            "resolved_path": str(resolved.relative_to(ROOT)),
            "bookkeeping_only": named in BOOKKEEPING_PATHS,
            "exists": resolved.exists(),
        })
    scientific = [row for row in path_records if not row["bookkeeping_only"]]
    assert len(scientific) == 9 and all(not row["exists"] for row in scientific)

    reset_manifest = run("git", "show", f"{RESET_COMMIT}:{RESET_MANIFEST_PATH}")
    manifest_rows = {
        row[0]: (int(row[1]), row[2])
        for row in csv.reader(reset_manifest.splitlines(), delimiter="\t")
        if row and row[0] in PRECURSORS
    }
    assert manifest_rows == PRECURSORS
    curated_manifest = run("git", "show", f"{CURATION_COMMIT}:{RESET_MANIFEST_PATH}")
    assert not any(path in curated_manifest for path in PRECURSORS)

    reachable_names = run("git", "rev-list", "--all", "--objects")
    path_needles = ("eas001", "explicit_array_slot_boundary", "explicit_array_slot_record_boundary")
    reachable_name_hits = sorted({
        line.split(" ", 1)[1]
        for line in reachable_names.splitlines()
        if " " in line and any(needle in line.lower() for needle in path_needles)
    })
    dangling = run("git", "fsck", "--full", "--no-reflogs", "--unreachable")
    dangling_commits = [line.split()[2] for line in dangling.splitlines() if "unreachable commit" in line]
    dangling_name_hits = []
    for commit in dangling_commits:
        names = run("git", "ls-tree", "-r", "--name-only", commit)
        dangling_name_hits.extend(
            name for name in names.splitlines()
            if any(needle in name.lower() for needle in path_needles)
        )
    blob_matches = git_blob_sha_matches()
    assert reachable_name_hits == []
    assert dangling_name_hits == []
    assert all(matches == [] for matches in blob_matches.values())

    bifolio = json.loads(BIFOLIO.read_text(encoding="utf-8"))
    bifolio_validation = json.loads(BIFOLIO_VALIDATION.read_text(encoding="utf-8"))
    assert bifolio["scope"] == {"bifolio_units": 4, "extant_folios": 7, "panels": 26}
    assert bifolio_validation["status"].startswith("PASS")
    assert bifolio["pages_by_bifolio"] == {
        "Q09_f67_f68": ["f67r1", "f67r2", "f67v1", "f67v2", "f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"],
        "Q10_f69_f70": ["f69r", "f69v", "f70r1", "f70r2", "f70v1", "f70v2"],
        "Q11_f71_f72": ["f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3"],
        "Q12_f73_f74_missing": ["f73r", "f73v"],
    }

    historical = next(row for row in ledger_rows if row["experiment"] == "EAS001_explicit_array_slot_boundary_final")
    result = {
        "experiment_id": "EAS001_PROVENANCE_REAUDIT",
        "status": "PROVISIONAL_HISTORICAL_UNRECONSTRUCTED",
        "decision": "HOLD_EAS001_AND_DEPENDENT_CLAIMS_UNTIL_ARTIFACT_RECOVERY_OR_NEW_VERSION",
        "audited_commit": AUDITED_COMMIT,
        "reset_commit": RESET_COMMIT,
        "curation_commit": CURATION_COMMIT,
        "ledger_eas001_rows": len(ledger_rows),
        "named_paths": path_records,
        "scientific_named_paths_absent": len(scientific),
        "reset_manifest_precursors": {
            path: {"size": size, "sha256": digest, "matching_git_blobs": blob_matches[digest]}
            for path, (size, digest) in PRECURSORS.items()
        },
        "reachable_eas001_path_hits": reachable_name_hits,
        "dangling_eas001_path_hits": sorted(set(dangling_name_hits)),
        "historical_ledger_summary_preserved": {
            "status": historical["status"],
            "live_scope": historical["live_scope"],
            "primary_report": historical["primary_report"],
        },
        "public_circle_bifolio_binding": {
            "scope": bifolio["scope"],
            "pages_by_bifolio": bifolio["pages_by_bifolio"],
            "source_result_sha256": BIFOLIO_HASHES[str(BIFOLIO.relative_to(ROOT))],
            "source_validation_sha256": BIFOLIO_HASHES[str(BIFOLIO_VALIDATION.relative_to(ROOT))],
        },
        "exact_13_folio_membership_recovered": False,
        "per_folio_effects_recovered": False,
        "bifolio_clustered_inference_recomputable": False,
        "gates": {
            "preregistration_present": False,
            "frozen_inventory_present": False,
            "target_result_present": False,
            "independent_validator_present": False,
            "exact_target_folio_list_present": False,
            "bifolio_robustness_recomputable": False,
        },
        "ocr_or_automated_vision_used": False,
        "manuscript_text_or_score_accessed": False,
        "claim_ceiling": (
            "The EAS001 ledger numerics are historical summaries, not currently reproducible evidence. "
            "They are not shown false, but cannot support an active confirmed boundary claim or any "
            "EAS001-dependent inference until exact artifacts are recovered or a new version is run."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# EAS001 provenance and bifolio re-audit\n\n"
        "Decision: **PROVISIONAL_HISTORICAL_UNRECONSTRUCTED**.\n\n"
        "The active ledger retains an exact positive summary for EAS001, but all nine scientific "
        "paths it names are absent: the precursor inventory report, preregistration, builder, "
        "coverage, core, controls, control validation, target report, and result validation. "
        "No matching EAS001 path occurs in a reachable or dangling Git tree. The reset manifest "
        "records sizes and SHA-256 values for five precursor inventory files, but their bodies "
        "were never committed; none matches any remaining Git blob.\n\n"
        "The historical ledger numbers (+.294219 minimum effect, 48/8192 p=.005859, 10/13 "
        "positive ZL folios) are preserved as history, not independently reconstructed. The exact "
        "13 target folios and their effects cannot be recovered. Public data now establish that "
        "f67--f73 are seven extant folios on only four bifolios, but without EAS001 membership the "
        "bifolio-clustered null cannot be recomputed.\n\n"
        "Therefore EAS001 and claims depending on its frozen inventory are on provenance HOLD. "
        "This is not evidence that the historical effect was false. Reopen only with hash-matching "
        "artifacts or a new versioned text-blind inventory and independent validation. No OCR, "
        "automated vision, manuscript score, word meaning, plaintext, or translation was used.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
