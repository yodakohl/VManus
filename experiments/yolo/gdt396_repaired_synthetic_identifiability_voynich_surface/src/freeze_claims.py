#!/usr/bin/env python3
"""Freeze blind GDT396 claims before the corresponding oracle is scored."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

from phase_authority import require_instrument


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def row_count(path:Path)->int:
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf-8",newline="") as fh:return sum(1 for _ in csv.DictReader(fh,delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("QUALIFICATION", "CONFIRMATION"), required=True)
    ap.add_argument("--claims-dir", type=Path, default=EXP / ".work/claims")
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    require_instrument(EXP, args.phase)
    phase = args.phase.lower()
    manifest = args.manifest or args.claims_dir / f"gdt396_{phase}_claim_manifest.tsv"
    output = args.output or EXP / f"artifacts/gdt396_{phase}_claim_freeze.json"
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    panel = EXP / "artifacts/gdt396_decoder_panel_freeze.json"
    if not panel.is_file():
        raise RuntimeError("decoder panel is not frozen")
    panel_data = json.loads(panel.read_text())
    decoder_hashes = {row["decoder_id"]: row["decoder_sha256"] for row in panel_data["decoders"]}
    data = rows(manifest)
    if not data or {row["phase"] for row in data} != {args.phase}:
        raise ValueError("mixed/empty claim manifest")
    bindings = {};cells=set();model_hashes={};training_expected="legacy;development" if args.phase=="QUALIFICATION" else "legacy;development;qualification"
    decoders = set(); worlds = set(); surfaces = set(); seeds = set(); representations = set()
    for row in data:
        if row["decoder_id"] not in decoder_hashes or row["decoder_sha256"] != decoder_hashes[row["decoder_id"]]:
            raise ValueError("decoder source differs from frozen panel")
        path = (args.claims_dir / row["relpath"]).resolve()
        if not path.is_relative_to(args.claims_dir.resolve()):
            raise ValueError("claim path escapes claims-dir")
        if not path.is_file() or sha256(path) != row["sha256"] or row_count(path)!=int(row["rows"]):
            raise ValueError(f"claim binding mismatch {path}")
        cell=(row["decoder_id"],row["world_id"],row["surface_id"],int(row["corpus_seed"]),row["representation_id"],row["table_name"])
        if cell in cells:raise ValueError(f"duplicate claim cell {cell}")
        cells.add(cell)
        if row["training_blocks"]!=training_expected:raise ValueError("wrong training blocks")
        model_key=(row["decoder_id"],row["world_id"],row["surface_id"])
        if model_key in model_hashes and model_hashes[model_key]!=row["model_sha256"]:raise ValueError("model hash instability")
        model_hashes[model_key]=row["model_sha256"]
        bindings[row["relpath"]] = row["sha256"]
        decoders.add(row["decoder_id"]); worlds.add(row["world_id"]); surfaces.add(row["surface_id"])
        seeds.add(int(row["corpus_seed"])); representations.add(row["representation_id"])
    expected_seeds = set(range(3961000,3961005)) if args.phase == "QUALIFICATION" else set(range(3962000,3962005))
    if worlds != {f"W{i:02d}" for i in range(1,11)} or surfaces != {"FREE_SURFACE","VOYNICH_SURFACE"} or seeds != expected_seeds:
        raise ValueError("claim panel does not cover the frozen phase worlds/surfaces/seeds")
    expected_cells=set()
    for decoder in panel_data["decoders"]:
        for world in {f"W{i:02d}" for i in range(1,11)}:
            for surface in ("FREE_SURFACE","VOYNICH_SURFACE"):
                for seed in expected_seeds:
                    for representation in decoder["supported_representations"]:
                        for table in ("partition_claims","binary_claims","target_queries","target_ranks","scope_claims","morphology_claims","record_partition_claims","architecture_partition_claims","architecture_binary_claims"):
                            expected_cells.add((decoder["decoder_id"],world,surface,seed,representation,table))
    if cells!=expected_cells:raise ValueError(f"claim Cartesian mismatch missing={len(expected_cells-cells)} extra={len(cells-expected_cells)}")
    result = {
        "schema": "GDT396_BLIND_CLAIM_FREEZE_V1", "status": "FROZEN_BEFORE_ORACLE_SCORING",
        "phase": args.phase, "decoder_panel_freeze_sha256": sha256(panel),
        "claim_manifest_sha256": sha256(manifest), "claim_file_count": len(bindings),
        "claim_rows": sum(int(row["rows"]) for row in data), "decoders": sorted(decoders),
        "worlds": sorted(worlds), "surfaces": sorted(surfaces), "seeds": sorted(seeds),
        "representations": sorted(representations), "claim_bindings": dict(sorted(bindings.items())),
        "oracle_scored_before_freeze": False, "voynich_corpus_files_opened": 0, "voynich_rows": 0,
        "f84": {"allowed":False,"opened":False,"rows":0}, "f84r":{"allowed":False,"opened":False,"rows":0},
    }
    payload=dict(result); result["content_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(output,sha256(output),result["claim_rows"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
