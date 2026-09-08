#!/usr/bin/env python3
"""Package root-owned GDT878 observation packets without reading source data."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt878_text_picture_combination_feasibility"
ART = EXP / "artifacts"
PROTOCOL = [EXP / "PREREGISTRATION.md", EXP / "METHOD.md"]
ANCHORS = ["f69v.14", "f69v.18", "f69v.27", "f72r2.9", "f72r2.10", "f72r2.11", "f72r2.18"]
FROZEN_PREREG_SHA256 = "efd9ab515904e00d9d4dc2c60ef6bfb14d239ef1d488074af189e38c87251736"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", type=Path, default=ART)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    art = args.artifacts.resolve()
    required = [art / "SOURCES.json", art / "ROOT_OBSERVATION.json", art / "GEOMETRY_B_OBSERVATION.json"]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit("missing root-owned packet(s): " + ", ".join(missing))
    sources, root_obs, geometry_obs = map(load, required)
    package = {
        "schema_version": 1,
        "experiment_id": "GDT878",
        "status": "UNSCORED_OBSERVATION_PACKAGE",
        "protocol_sha256": {p.name: digest(p) for p in PROTOCOL},
        "frozen_preregistration_sha256": FROZEN_PREREG_SHA256,
        "input_packet_sha256": {p.name: digest(p) for p in required},
        "fixed_scope": {"root_anchors": ANCHORS, "geometry_page": "f67r2", "forbidden_prefixes": ["f84", "f84r"]},
        "source_manifest": sources,
        "branches": {"root": root_obs, "geometry_b": geometry_obs},
        "claim_ceiling": "contract/feasibility only; no semantic verdict or independent visual validation",
    }
    out = (args.output or (art / "RUN_PACKAGE.json")).resolve()
    out.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "protocol_sha256": package["protocol_sha256"], "root_anchors": ANCHORS}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
