#!/usr/bin/env python3
"""Generate GDT396 paired FREE/VOYNICH surfaces from frozen GDT395 worlds."""

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

from surface_channel import encode_group, make_mapping, read_atom_stream, salt_commitment, sha256, write_atom_stream
from phase_authority import require_instrument


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
G395 = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
G395_SRC = G395 / "src"
if str(G395) not in sys.path:
    sys.path.insert(0, str(G395))
if str(G395_SRC) not in sys.path:
    sys.path.insert(0, str(G395_SRC))

from src.world_api import CODEBOOK_FIELDS, GENEALOGY_FIELDS, OBS_FIELDS, ORACLE_FIELDS, validate_rows  # noqa: E402
from src.normalize_bundle import normalize_bundle, validate_canonical  # noqa: E402


SEED_BLOCKS = {
    "legacy": tuple(range(0, 20)),
    "development": tuple(range(3960000, 3960005)),
    "qualification": tuple(range(3961000, 3961005)),
    "confirmation": tuple(range(3962000, 3962005)),
}
TARGET_EVENTS = 8448
META_FIELDS = tuple(field for field in OBS_FIELDS if field != "visible_group") + (
    "surface_channel", "surface_payload_index",
)
MANIFEST_FIELDS = (
    "world_id", "corpus_seed", "seed_block", "events", "free_observation_relpath",
    "free_observation_sha256", "voynich_metadata_relpath", "voynich_metadata_sha256",
    "voynich_surface_relpath", "voynich_surface_sha256", "oracle_relpath",
    "oracle_sha256", "hidden_trace_sha256", "mapping_commitment", "mapping_width",
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def load_world(path: Path, world_id: str):
    spec = importlib.util.spec_from_file_location(f"gdt396_frozen_{world_id}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
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
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def read_salt(path: Path) -> bytes:
    value = path.read_text(encoding="ascii").strip()
    if len(value) != 64:
        raise ValueError("surface salt must be 32 bytes encoded as 64 hex characters")
    return bytes.fromhex(value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", choices=tuple(SEED_BLOCKS), required=True)
    ap.add_argument("--world", action="append", default=[])
    ap.add_argument("--output-dir", type=Path, default=EXP / ".work/corpora")
    ap.add_argument("--salt", type=Path, default=EXP / ".work/sealed/surface_salt.hex")
    ap.add_argument("--allow-confirmation", action="store_true")
    args = ap.parse_args()
    manifest_target = args.output_dir / f"gdt396_{args.block}_paired_manifest.tsv"
    if manifest_target.exists():
        raise RuntimeError(f"refusing to overwrite {manifest_target}")
    if args.block == "qualification":
        require_instrument(EXP, "QUALIFICATION")
    if args.block == "confirmation" and not args.allow_confirmation:
        raise RuntimeError("confirmation generation requires the post-decoder-freeze --allow-confirmation gate")
    if args.block == "confirmation":
        require_instrument(EXP, "CONFIRMATION")

    salt = read_salt(args.salt)
    commitment = salt_commitment(salt)
    panel = json.loads((G395 / "artifacts/gdt395_world_panel_freeze.json").read_text(encoding="utf-8"))
    frozen_worlds = {row["world_id"]: row for row in panel["worlds"]}
    wanted = set(args.world) if args.world else set(frozen_worlds)
    if not wanted <= set(frozen_worlds):
        raise ValueError(f"unknown worlds {sorted(wanted - set(frozen_worlds))}")

    manifest: list[dict] = []
    for world_id in sorted(wanted):
        frozen = frozen_worlds[world_id]
        generator = ROOT / frozen["directory"] / "generator.py"
        if sha256(generator) != frozen["generator_sha256"]:
            raise RuntimeError(f"{world_id}: frozen generator hash mismatch")
        module = load_world(generator, world_id)
        if module.WORLD_META != frozen["final_observation_meta"]:
            raise RuntimeError(f"{world_id}: frozen WORLD_META mismatch")
        mapping = make_mapping(world_id, module.WORLD_META["alphabet"], salt)
        widths = {len(value) for value in mapping.values()}
        if len(widths) != 1:
            raise RuntimeError(f"{world_id}: mapping is not fixed-width")
        width = widths.pop()
        first_codebook = first_genealogy = None
        for seed in SEED_BLOCKS[args.block]:
            bundle = normalize_bundle(module.generate(seed, TARGET_EVENTS))
            validate_rows(module.WORLD_META, bundle, TARGET_EVENTS)
            validate_canonical(bundle)
            if first_codebook is None:
                first_codebook = bundle["codebook"]
                first_genealogy = bundle["genealogy"]
            elif bundle["codebook"] != first_codebook or bundle["genealogy"] != first_genealogy:
                raise RuntimeError(f"{world_id}: hidden codebook/genealogy changed across seeds")

            world_dir = args.output_dir / args.block / world_id
            free_path = world_dir / f"seed_{seed:02d}_free.tsv.gz"
            meta_path = world_dir / f"seed_{seed:02d}_voynich_meta.tsv.gz"
            surface_path = world_dir / f"seed_{seed:02d}_voynich_surface.bin.gz"
            oracle_path = args.output_dir / "sealed" / args.block / world_id / f"seed_{seed:02d}_oracle.tsv.gz"
            write_tsv_gz(free_path, OBS_FIELDS, bundle["observations"])
            meta_rows = []
            payloads = []
            for index, row in enumerate(bundle["observations"]):
                payloads.append(encode_group(row["visible_group"], mapping))
                meta = {field: row[field] for field in OBS_FIELDS if field != "visible_group"}
                meta.update(surface_channel="VOYNICH_SURFACE", surface_payload_index=index)
                meta_rows.append(meta)
            write_tsv_gz(meta_path, META_FIELDS, meta_rows)
            write_atom_stream(surface_path, payloads)
            if len(read_atom_stream(surface_path)) != len(meta_rows):
                raise RuntimeError(f"{world_id}/{seed}: constrained stream count mismatch")
            write_tsv_gz(oracle_path, ORACLE_FIELDS, bundle["oracle"])

            hidden_trace = [
                {field: row[field] for field in OBS_FIELDS if field != "visible_group"}
                for row in bundle["observations"]
            ]
            trace_sha = digest_bytes(canonical_json({"trace": hidden_trace, "oracle": bundle["oracle"]}))
            manifest.append({
                "world_id": world_id,
                "corpus_seed": seed,
                "seed_block": args.block,
                "events": len(bundle["observations"]),
                "free_observation_relpath": str(free_path.relative_to(args.output_dir)),
                "free_observation_sha256": sha256(free_path),
                "voynich_metadata_relpath": str(meta_path.relative_to(args.output_dir)),
                "voynich_metadata_sha256": sha256(meta_path),
                "voynich_surface_relpath": str(surface_path.relative_to(args.output_dir)),
                "voynich_surface_sha256": sha256(surface_path),
                "oracle_relpath": str(oracle_path.relative_to(args.output_dir)),
                "oracle_sha256": sha256(oracle_path),
                "hidden_trace_sha256": trace_sha,
                "mapping_commitment": commitment,
                "mapping_width": width,
            })
            print(world_id, seed, len(bundle["observations"]), free_path.name, surface_path.name)

        sealed_world = args.output_dir / "sealed" / world_id
        write_tsv(sealed_world / "codebook.tsv", CODEBOOK_FIELDS, first_codebook or [])
        write_tsv(sealed_world / "genealogy.tsv", GENEALOGY_FIELDS, first_genealogy or [])
        (sealed_world / "world_meta.json").write_text(json.dumps(module.WORLD_META, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_path = args.output_dir / f"gdt396_{args.block}_paired_manifest.tsv"
    write_tsv(manifest_path, MANIFEST_FIELDS, manifest)
    print(manifest_path, sha256(manifest_path), len(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
