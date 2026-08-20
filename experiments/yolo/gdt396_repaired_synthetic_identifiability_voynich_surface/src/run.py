#!/usr/bin/env python3
"""Stage-safe GDT396 orchestration entry point."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
SRC = EXP / "src"
PY = sys.executable


def call(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def manifest_rows(block: str) -> list[dict]:
    path = EXP / f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv"
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def decode_phase(phase: str, workers: int) -> None:
    block = phase.lower(); data = manifest_rows(block)
    worlds = sorted({row["world_id"] for row in data}); surfaces = ("FREE_SURFACE", "VOYNICH_SURFACE")
    decoders = sorted((EXP / "decoders").glob("*/decoder.py")); claims = EXP / ".work/claims"
    parts = claims / "_parts" / block
    if parts.exists() or (claims / f"gdt396_{block}_claim_manifest.tsv").exists():
        raise RuntimeError(f"refusing to overwrite {phase} claims")
    parts.mkdir(parents=True)
    jobs = []
    for decoder in decoders:
        for world in worlds:
            for surface in surfaces:
                manifest = parts / f"{decoder.parent.name}_{world}_{surface}.tsv"
                jobs.append([PY, str(SRC / "run_blind_decoders.py"), "--phase", phase, "--decoder", str(decoder), "--world", world, "--surface", surface, "--output-dir", str(claims), "--manifest", str(manifest)])
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(call, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    merge = [PY, str(SRC / "merge_claim_manifests.py"), "--claims-dir", str(claims)]
    for path in sorted(parts.glob("*.tsv")):
        merge.extend(("--input", str(path)))
    merge.extend(("--output", str(claims / f"gdt396_{block}_claim_manifest.tsv")))
    call(merge)


def main() -> int:
    stages = ("validate-protocol", "generate-qualification", "decode-qualification", "freeze-qualification-claims", "score-qualification", "generate-confirmation", "decode-confirmation", "freeze-confirmation-claims", "score-confirmation")
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=stages); ap.add_argument("--workers", type=int, default=8); args = ap.parse_args()
    if not 1 <= args.workers <= 32:
        raise ValueError("workers must be 1..32")
    if args.stage == "validate-protocol":
        correction_v3 = EXP / "artifacts/gdt396_prequalification_correction_freeze_v3.json"
        correction_v2 = EXP / "artifacts/gdt396_prequalification_correction_freeze_v2.json"
        correction_v1 = EXP / "artifacts/gdt396_prequalification_correction_freeze.json"
        if correction_v3.exists(): call([PY, str(SRC / "validate_prequalification_correction_v3.py")])
        elif correction_v2.exists(): call([PY, str(SRC / "validate_prequalification_correction_v2.py")])
        elif correction_v1.exists(): call([PY, str(SRC / "validate_prequalification_correction.py")])
        else: call([PY, str(SRC / "validate_protocol.py")]); call([PY, str(SRC / "validate_paired_corpora.py")])
    elif args.stage == "generate-qualification":
        call([PY, str(SRC / "generate_paired_corpora.py"), "--block", "qualification"]); call([PY, str(SRC / "repair_trace_manifests.py"), "--block", "qualification"]); call([PY, str(SRC / "validate_phase_corpora.py"), "--phase", "qualification"])
    elif args.stage == "decode-qualification":
        decode_phase("QUALIFICATION", args.workers)
    elif args.stage == "freeze-qualification-claims":
        call([PY, str(SRC / "freeze_claims.py"), "--phase", "QUALIFICATION"])
    elif args.stage == "score-qualification":
        freeze = json.loads((EXP / "artifacts/gdt396_qualification_claim_freeze.json").read_text())
        if freeze["status"] != "FROZEN_BEFORE_ORACLE_SCORING": raise RuntimeError("qualification claims are not frozen")
        call([PY, str(SRC / "score_decoder_phase.py"), "--phase", "QUALIFICATION"]); call([PY, str(SRC / "qualify_decoders.py")])
    elif args.stage == "generate-confirmation":
        call([PY, str(SRC / "generate_paired_corpora.py"), "--block", "confirmation", "--allow-confirmation"]); call([PY, str(SRC / "repair_trace_manifests.py"), "--block", "confirmation"]); call([PY, str(SRC / "validate_phase_corpora.py"), "--phase", "confirmation"])
    elif args.stage == "decode-confirmation":
        decode_phase("CONFIRMATION", args.workers)
    elif args.stage == "freeze-confirmation-claims":
        call([PY, str(SRC / "freeze_claims.py"), "--phase", "CONFIRMATION"])
    elif args.stage == "score-confirmation":
        freeze = json.loads((EXP / "artifacts/gdt396_confirmation_claim_freeze.json").read_text())
        if freeze["status"] != "FROZEN_BEFORE_ORACLE_SCORING": raise RuntimeError("confirmation claims are not frozen")
        call([PY, str(SRC / "score_decoder_phase.py"), "--phase", "CONFIRMATION"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
