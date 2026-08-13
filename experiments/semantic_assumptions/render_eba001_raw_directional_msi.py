#!/usr/bin/env python3
"""Deterministically render preregistered EBA001 TIFF products for native review."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image


# Source-space context boxes and display-space target boxes were frozen for the
# corrected, provenance-qualified result.  Target boxes are measured after the
# stated lossless transpose of the native context crop.
CROPS = {
    "f17r": {
        "context_box": (800, 1600, 1800, 5700),
        "transpose": Image.Transpose.ROTATE_270,
        "target_box": (850, 80, 3350, 380),
        "dark_reference_box": (850, 100, 1500, 360),
        "shadow_box": (900, 0, 3200, 160),
    },
    "f116v": {
        "context_box": (6200, 700, 8176, 3600),
        "transpose": Image.Transpose.ROTATE_90,
        "target_box": (1120, 1170, 2900, 1490),
        "dark_reference_box": (1500, 500, 2850, 850),
        "shadow_box": (500, 250, 2400, 750),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_exclusive(image: Image.Image, path: Path) -> None:
    if path.exists():
        raise FileExistsError(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        image.save(output, format="PNG", optimize=False)
        output.flush()
        os.fsync(output.fileno())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preview-width", type=int, default=2044)
    args = parser.parse_args()
    args.output_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    inventory = json.loads(args.inventory.read_bytes())

    for record in inventory["files"]:
        source = args.raw_dir / record["filename"]
        if sha256(source) != record["sha256"]:
            raise RuntimeError(f"hash mismatch: {source}")
        with Image.open(source) as opened:
            pixels = np.asarray(opened, dtype=np.uint16)
        if pixels.ndim != 2:
            raise RuntimeError(f"expected single-channel TIFF: {source}")
        low, high = np.percentile(pixels, [0.5, 99.5], method="linear")
        if not low < high:
            raise RuntimeError(f"degenerate percentiles: {source}")
        display = np.clip((pixels.astype(np.float64) - low) * (255.0 / (high - low)), 0, 255).astype(np.uint8)
        image = Image.fromarray(display, mode="L")
        height = round(image.height * args.preview_width / image.width)
        preview = image.resize((args.preview_width, height), resample=Image.Resampling.BOX)
        stem = Path(record["filename"]).stem
        save_exclusive(preview, args.output_dir / f"{stem}_preview.png")
        crop_rule = CROPS[record["folio"]]
        context = image.crop(crop_rule["context_box"]).transpose(crop_rule["transpose"])
        target = context.crop(crop_rule["target_box"])
        dark_reference = context.crop(crop_rule["dark_reference_box"])
        shadow = context.crop(crop_rule["shadow_box"])
        context_path = args.output_dir / f"{stem}_native_context.png"
        target_path = args.output_dir / f"{stem}_native_target.png"
        dark_reference_path = args.output_dir / f"{stem}_native_dark_reference.png"
        shadow_path = args.output_dir / f"{stem}_native_shadow_control.png"
        save_exclusive(context, context_path)
        save_exclusive(target, target_path)
        save_exclusive(dark_reference, dark_reference_path)
        save_exclusive(shadow, shadow_path)
        metadata = {
            "source_sha256": record["sha256"],
            "low_percentile_0_5": float(low),
            "high_percentile_99_5": float(high),
            "native_width": image.width,
            "native_height": image.height,
            "preview_width": preview.width,
            "preview_height": preview.height,
            "native_context_xyxy": list(crop_rule["context_box"]),
            "native_context_sha256": sha256(context_path),
            "oriented_target_xyxy": list(crop_rule["target_box"]),
            "native_target_sha256": sha256(target_path),
            "oriented_dark_reference_xyxy": list(crop_rule["dark_reference_box"]),
            "native_dark_reference_sha256": sha256(dark_reference_path),
            "oriented_shadow_control_xyxy": list(crop_rule["shadow_box"]),
            "native_shadow_control_sha256": sha256(shadow_path),
        }
        (args.output_dir / f"{stem}_display.json").write_text(
            json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n"
        )


if __name__ == "__main__":
    main()
