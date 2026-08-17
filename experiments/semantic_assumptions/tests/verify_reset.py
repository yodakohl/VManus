#!/usr/bin/env python3
"""Verify active research state and curated archive evidence pointers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ACTIVE = ROOT / "experiments" / "semantic_assumptions"
ARCHIVE = ROOT / "archive_pre_reset_2026-08-06"
MANIFEST = ARCHIVE / "ARCHIVE_MANIFEST.tsv"
SUMMARY = ARCHIVE / "ARCHIVE_MANIFEST.json"
LOCK = ACTIVE / "grammar" / "PRIMARY_EVIDENCE_LOCK.tsv"
PRE_GROUNDING_COVERAGE = ACTIVE / "results" / "pre_grounding_surface_coverage_audit.json"


def is_transient(path: Path) -> bool:
    """Ignore interpreter/build debris that is not research evidence."""
    return "__pycache__" in path.parts or path.suffix == ".pyc" or path.name.endswith(".part")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-archive", action="store_true")
    args = parser.parse_args()
    required = [
        ROOT / "VOYNICH_ACTIVE_STATE.md",
        ACTIVE / "ACTIVE_EXPERIMENT_LEDGER.tsv",
        ACTIVE / "CLOSED_ROUTE_FAMILIES.tsv",
        ACTIVE / "grammar" / "CONFIRMED_GRAMMAR.md",
        ACTIVE / "hypotheses" / "ACTIVE_HYPOTHESES.tsv",
        MANIFEST,
        SUMMARY,
        LOCK,
        PRE_GROUNDING_COVERAGE,
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing[0])
    ledger = read_tsv(ACTIVE / "ACTIVE_EXPERIMENT_LEDGER.tsv")
    # The ledger is intentionally row-oriented and grows after every material
    # pass. Keep a generous hard ceiling so this catches accidental archive
    # re-expansion without failing during normal compact experiment turnover.
    if len(ledger) > 1792:
        raise RuntimeError(f"active ledger is no longer compact: {len(ledger)} rows")
    hypotheses = read_tsv(ACTIVE / "hypotheses" / "ACTIVE_HYPOTHESES.tsv")
    if len(hypotheses) > 64:
        raise RuntimeError(f"active hypothesis registry is no longer compact: {len(hypotheses)} rows")
    identifiers = [row["hypothesis_id"] for row in hypotheses]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("duplicate active hypothesis id")
    required_hypothesis_fields = {
        "hypothesis_id", "status", "claim", "independent_evidence",
        "predeclared_falsifier", "held_data", "result",
    }
    for row in hypotheses:
        missing_fields = sorted(
            field for field in required_hypothesis_fields if not row.get(field)
        )
        if missing_fields:
            raise RuntimeError(
                f"incomplete hypothesis {row.get('hypothesis_id', '?')}: {missing_fields}"
            )
        if row["status"] == "REGISTERED_UNSCORED" and row["result"] != "PENDING":
            raise RuntimeError(
                f"registered hypothesis {row['hypothesis_id']} has a non-pending result"
            )

    archive_rows = read_tsv(MANIFEST)
    archive_by_path = {row["path"]: row for row in archive_rows}
    if len(archive_by_path) != len(archive_rows):
        raise RuntimeError("duplicate path in archive manifest")
    locked = read_tsv(LOCK)
    for row in locked:
        path = ROOT / row["path"]
        if path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"]:
            raise RuntimeError(f"primary evidence drift: {row['path']}")
        archive_prefix = f"{ARCHIVE.name}/"
        if row["path"].startswith(archive_prefix):
            relative = row["path"][len(archive_prefix):]
            bound = archive_by_path.get(relative)
            if bound is None or bound["sha256"] != row["sha256"]:
                raise RuntimeError(f"primary evidence absent from archive manifest: {relative}")

    old_ledger = ARCHIVE / "semantic_assumptions" / "ACTIVE_EXPERIMENT_LEDGER.tsv"
    if len(read_tsv(old_ledger)) != 105:
        raise RuntimeError("legacy ledger row count drift")

    pre_grounding_coverage = json.loads(PRE_GROUNDING_COVERAGE.read_text(encoding="utf-8"))
    if pre_grounding_coverage.get("status") != "PASS_COMPLETE_SURFACE_PARTIAL_FORMAL_COVERAGE":
        raise RuntimeError("pre-grounding coverage correction absent")
    if pre_grounding_coverage.get("totals") != {
        "affected_rows": 2833,
        "omitted_characters": 5237,
        "omitted_tokens": 3838,
        "parsed_characters": 568072,
        "parsed_nodes": 114173,
        "rows": 15960,
        "surface_characters": 573309,
        "surface_tokens": 118011,
    }:
        raise RuntimeError("pre-grounding coverage correction drift")

    old_semantic = ARCHIVE / "semantic_assumptions"
    sys.path.insert(0, str(old_semantic))
    spec = importlib.util.spec_from_file_location("reset_archived_common", old_semantic / "common.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load archived common.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.BASE != ROOT or not module.TRANSCRIPT.is_file():
        raise RuntimeError("archived runner root/transcript resolution is broken")
    parsed = module.parse_rows()
    loci, tokens = len(parsed), sum(len(row.words) for row in parsed)
    if (loci, tokens) != (5376, 38988):
        raise RuntimeError(f"canonical transcription drift: loci={loci}, tokens={tokens}")

    if args.full_archive:
        for row in archive_rows:
            path = ARCHIVE / row["path"]
            if path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"]:
                raise RuntimeError(f"archive drift: {row['path']}")
        actual = {
            str(path.relative_to(ARCHIVE)) for path in ARCHIVE.rglob("*") if path.is_file()
            and path.name not in {MANIFEST.name, SUMMARY.name} and not is_transient(path)
        }
        if actual != set(archive_by_path):
            raise RuntimeError("archive file inventory drift")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    output = {
        "status": "ACTIVE_STATE_VERIFIED",
        "active_ledger_rows": len(ledger),
        "active_hypotheses": len(hypotheses),
        "registered_unscored_hypotheses": sum(
            row["status"] == "REGISTERED_UNSCORED" for row in hypotheses
        ),
        "primary_evidence_files": len(locked),
        "archive_files": len(archive_rows),
        "archive_manifest_sha256": digest(MANIFEST),
        "legacy_experiment_rows": len(read_tsv(old_ledger)),
        "canonical_loci": loci,
        "canonical_tokens": tokens,
        "pre_grounding_unparsed_surface_tokens": pre_grounding_coverage["totals"]["omitted_tokens"],
        "full_archive_verified": args.full_archive,
        "summary_status": summary["status"],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
