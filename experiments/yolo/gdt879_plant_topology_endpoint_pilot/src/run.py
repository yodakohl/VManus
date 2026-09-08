#!/usr/bin/env python3
"""Verify GDT879 source bytes and package native packets when available."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt879_plant_topology_endpoint_pilot"
ART = EXP / "artifacts"
PREREG_SHA256 = "d47c248754d3fa5b79b6f4bc07eba07f495ed55835ccced30f821a37814f7b41"
PAGES = {"f4r", "f10r", "f13r"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_checks(manifest):
    errors = []
    images = manifest.get("images") if isinstance(manifest, dict) else None
    if not isinstance(images, list) or {x.get("page") for x in images} != PAGES:
        return ["SOURCES.json must contain exactly f4r, f10r, and f13r"]
    for item in images:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing source: {item['page']}")
            continue
        raw = path.read_bytes()
        if sha(path) != item.get("sha256") or len(raw) != item.get("bytes"):
            errors.append(f"source hash/byte mismatch: {item['page']}")
        if Image is None:
            errors.append("Pillow unavailable for dimensions")
        else:
            with Image.open(path) as image:
                if image.size != (item.get("width"), item.get("height")):
                    errors.append(f"source dimensions mismatch: {item['page']}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=ART)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    art = args.artifacts.resolve()
    manifest_path = art / "SOURCES.json"
    if not manifest_path.is_file():
        raise SystemExit("missing artifacts/SOURCES.json")
    manifest = load(manifest_path)
    errors = source_checks(manifest)
    packet_paths = [art / "ROOT_OBSERVATION.json", art / "B_OBSERVATION.json"]
    missing = [str(path) for path in packet_paths if not path.is_file()]
    if missing:
        print(json.dumps({"status": "SOURCE_CHECK_ONLY", "errors": errors, "missing_packets": missing, "preregistration_sha256": PREREG_SHA256}))
        return 0 if not errors else 1
    packets = {path.name: load(path) for path in packet_paths}
    package = {
        "schema_version": 1,
        "experiment_id": "GDT879",
        "status": "UNSCORED_NATIVE_PACKET_PACKAGE",
        "preregistration_sha256": PREREG_SHA256,
        "source_manifest_sha256": sha(manifest_path),
        "packet_sha256": {path.name: sha(path) for path in packet_paths},
        "source_errors": errors,
        "packets": packets,
        "claim_ceiling": "source and packet contract only; no autonomous visual adjudication",
    }
    out = (args.output or art / "PACKET_PACKAGE.json").resolve()
    out.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PACKAGED", "output": str(out), "source_errors": errors}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
