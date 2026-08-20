#!/usr/bin/env python3
"""Generate the frozen GDT395 corpus panel into a decoder-separated work area."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

from world_api import CODEBOOK_FIELDS, GENEALOGY_FIELDS, OBS_FIELDS, ORACLE_FIELDS, validate_rows
from normalize_bundle import normalize_bundle, validate_canonical

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
FREEZE = EXP / "artifacts/gdt395_interface_freeze.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_module(path: Path, world_id: str):
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    spec = importlib.util.spec_from_file_location(f"gdt395_{world_id}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_tsv_gz(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
                writer.writeheader(); writer.writerows(rows)


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=EXP / ".work/corpora")
    ap.add_argument("--world", action="append", default=[])
    ap.add_argument("--seeds", type=int, default=None)
    args = ap.parse_args()
    frozen = json.loads(FREEZE.read_text())
    assignments = frozen["world_assignments"]
    if args.world:
        wanted = set(args.world); assignments = [a for a in assignments if a["world_id"] in wanted]
    seeds = frozen["corpus_seeds"][:args.seeds] if args.seeds is not None else frozen["corpus_seeds"]
    target = frozen["target_events_per_seed"]
    manifest = []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for assignment in assignments:
        wid = assignment["world_id"]
        candidates = sorted((EXP / "worlds").glob(f"{wid.lower()}_*/generator.py"))
        if len(candidates) != 1:
            raise RuntimeError(f"{wid}: expected one generator, found {candidates}")
        mod = load_module(candidates[0], wid)
        if mod.WORLD_META["world_id"] != wid:
            raise RuntimeError(f"{wid}: metadata ID mismatch")
        first_codebook = first_genealogy = None
        for seed in seeds:
            bundle = mod.generate(seed, target)
            validate_rows(mod.WORLD_META, bundle, target)
            bundle = normalize_bundle(bundle)
            validate_rows(mod.WORLD_META, bundle, target)
            validate_canonical(bundle)
            if first_codebook is None:
                first_codebook, first_genealogy = bundle["codebook"], bundle["genealogy"]
                write_tsv(args.output_dir / "sealed" / wid / "codebook.tsv", CODEBOOK_FIELDS, first_codebook)
                write_tsv(args.output_dir / "sealed" / wid / "genealogy.tsv", GENEALOGY_FIELDS, first_genealogy)
                (args.output_dir / "sealed" / wid / "world_meta.json").write_text(json.dumps(mod.WORLD_META, indent=2, sort_keys=True) + "\n")
            elif bundle["codebook"] != first_codebook or bundle["genealogy"] != first_genealogy:
                raise RuntimeError(f"{wid}: codebook/genealogy changed across seeds")
            obs_path = args.output_dir / "blind" / wid / f"seed_{seed:02d}.tsv.gz"
            oracle_path = args.output_dir / "sealed" / wid / f"seed_{seed:02d}_oracle.tsv.gz"
            write_tsv_gz(obs_path, OBS_FIELDS, bundle["observations"])
            write_tsv_gz(oracle_path, ORACLE_FIELDS, bundle["oracle"])
            manifest.append({
                "world_id": wid, "corpus_seed": seed, "events": len(bundle["observations"]),
                "record_rewriter": "NONE",
                "observation_relpath": str(obs_path.relative_to(args.output_dir)),
                "observation_sha256": digest(obs_path),
                "oracle_relpath": str(oracle_path.relative_to(args.output_dir)),
                "oracle_sha256": digest(oracle_path),
            })
            print(wid, seed, len(bundle["observations"]), manifest[-1]["observation_sha256"][:12])
    fields = ("world_id", "corpus_seed", "events", "record_rewriter", "observation_relpath", "observation_sha256", "oracle_relpath", "oracle_sha256")
    write_tsv(args.output_dir / "corpus_manifest.tsv", fields, manifest)


if __name__ == "__main__":
    main()
