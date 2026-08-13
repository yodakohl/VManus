#!/usr/bin/env python3
"""Acquire the six preregistered EBA001 source TIFF products outside the repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request


FILES = (
    ("f17r", "Voynich_17r+MB365UV_007_F.tif", "13Qxw2IvaYgprVPE-mb5RWDeCN-LxdtN1", "EXPOSURE_007"),
    ("f17r", "Voynich_17r+MB365UV_029_F.tif", "1tjUlqHFFYOoP7wXhMSevC-MsDc4NqZ9Q", "EXPOSURE_029"),
    ("f17r", "Voynich_17r+MB365UV_037_F.tif", "1PVcYQimUWy49xJd1XL7jWFxGGCzNAtw4", "EXPOSURE_037"),
    ("f116v", "Voynich_116v+MB365UV_007_F.tif", "1fFFH6lVG7UgwSj49CdI_JqsBHdhplnQX", "EXPOSURE_007"),
    ("f116v", "Voynich_116v+MB365UV_029_F.tif", "12txJIKIYVWSmaTrqX9KThj8fRMwtJQtE", "EXPOSURE_029"),
    ("f116v", "Voynich_116v+MB365UV_037_F.tif", "1n_woSHJebH1oPN67y5a5mAxao-QWtAlf", "EXPOSURE_037"),
)
URL = "https://drive.usercontent.google.com/download?id={}&export=download&confirm=t"


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def acquire(destination: Path, file_id: str) -> tuple[str, int, str]:
    url = URL.format(file_id)
    partial = destination.with_name(destination.name + ".partial")
    fd = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    digest = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(fd, "wb") as out:
            request = urllib.request.Request(url, headers={"User-Agent": "VManus-EBA001/1.0"})
            with urllib.request.urlopen(request, timeout=120) as response:
                final_url = response.geturl()
                if not final_url.startswith("https://drive.usercontent.google.com/"):
                    raise RuntimeError(f"unexpected final URL: {final_url}")
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    digest.update(block)
                    size += len(block)
                    out.write(block)
            out.flush()
            os.fsync(out.fileno())
        os.link(partial, destination)
        partial.unlink()
        return digest.hexdigest(), size, url
    except BaseException:
        try:
            partial.unlink()
        except FileNotFoundError:
            pass
        raise


def tiff_metadata(path: Path) -> dict[str, object]:
    from PIL import Image

    with Image.open(path) as image:
        if image.n_frames != 1:
            raise RuntimeError(f"expected one TIFF page: {path}")
        bits = image.tag_v2.get(258)
        if isinstance(bits, tuple):
            bits = bits[0]
        model = str(image.tag_v2.get(272, "")).rstrip("\x00")
        capture_datetime = str(image.tag_v2.get(306, ""))
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "bits_per_sample": int(bits),
            "samples_per_pixel": int(image.tag_v2.get(277, 1)),
            "compression_tag": int(image.tag_v2.get(259, 1)),
            "camera_make": str(image.tag_v2.get(271, "")),
            "camera_model_and_exposure": model,
            "capture_datetime": capture_datetime,
            "x_resolution_dpi": float(image.tag_v2.get(282)),
            "y_resolution_dpi": float(image.tag_v2.get(283)),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-dir", type=Path, required=True)
    parser.add_argument("--inventory-out", type=Path, required=True)
    args = parser.parse_args()
    args.download_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    if args.inventory_out.exists():
        raise FileExistsError(args.inventory_out)

    records = []
    for folio, filename, file_id, role in FILES:
        path = args.download_dir / filename
        sha256, size, url = acquire(path, file_id)
        records.append(
            {
                "folio": folio,
                "filename": filename,
                "file_id": file_id,
                "illumination_role": role,
                "source_url": url,
                "sha256": sha256,
                "size": size,
                "tiff": tiff_metadata(path),
            }
        )

    result = {
        "schema": "EBA001_RAW_DIRECTIONAL_MSI_INVENTORY_V1",
        "credit": "The Lazarus Project and the Chester F. Carlson Center for Imaging Science at RIT",
        "manuscript": "Beinecke Rare Book & Manuscript Library MS 408",
        "files": records,
    }
    data = canonical(result)
    fd = os.open(args.inventory_out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    print(data.decode(), end="")


if __name__ == "__main__":
    main()
