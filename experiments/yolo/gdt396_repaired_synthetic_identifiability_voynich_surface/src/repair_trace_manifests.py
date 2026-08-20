#!/usr/bin/env python3
"""Create reconstructable V2 trace digests without rewriting corpus bytes."""

from __future__ import annotations

import csv
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
CORPORA = EXP / ".work/corpora"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def trace_digest(observations: list[dict], oracle: list[dict]) -> str:
    trace = [{key: value for key, value in row.items() if key != "visible_group"} for row in observations]
    payload = json.dumps({"trace": trace, "oracle": oracle}, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", action="append", choices=("legacy", "development", "qualification", "confirmation"), default=[])
    args = ap.parse_args()
    for block in (tuple(args.block) if args.block else ("legacy", "development")):
        source = CORPORA / f"gdt396_{block}_paired_manifest.tsv"
        target = CORPORA / f"gdt396_{block}_paired_manifest_v2.tsv"
        if target.exists():
            raise RuntimeError(f"refusing to overwrite {target}")
        source_rows = rows(source)
        out = []
        for row in source_rows:
            original = row["hidden_trace_sha256"]
            obs = rows(CORPORA / row["free_observation_relpath"])
            oracle = rows(CORPORA / row["oracle_relpath"])
            fixed = dict(row)
            fixed["hidden_trace_sha256"] = trace_digest(obs, oracle)
            fixed["superseded_in_memory_trace_sha256"] = original
            fixed["trace_hash_definition"] = "STORED_TSV_TEXT_SCALARS_VISIBLE_GROUP_OMITTED_PLUS_ORACLE_V1"
            fixed["source_manifest_sha256"] = sha256(source)
            out.append(fixed)
        fields = tuple(out[0])
        with target.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader(); writer.writerows(out)
        print(block, len(out), sha256(source), sha256(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
