#!/usr/bin/env python3
"""Download and tile the already allow-listed GDT390 review images."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
MAPPING = ART / "gdt390_image_manifest.tsv"
FREEZE = ART / "gdt390_pre_image_freeze.json"
PUBLIC_HASHES = ART / "gdt390_review_image_hashes.tsv"
REVIEW_ROOT = Path(tempfile.gettempdir()) / "gdt390_review_v1"
IMAGES = REVIEW_ROOT / "images"
SHEETS = REVIEW_ROOT / "contact_sheets"


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    order = freeze["frame"]["page_review_order"]
    with MAPPING.open(encoding="utf-8", newline="") as handle:
        mappings = list(csv.DictReader(handle, delimiter="\t"))
    assert len(mappings) == 13 and {row["page"] for row in mappings} == set(order)
    assert all(not row["page"].lower().startswith("f84") and "84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mappings)
    by_page = {row["page"]: row for row in mappings}
    IMAGES.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    reviewed: list[dict[str, object]] = []
    for page in order:
        row = by_page[page]
        path = IMAGES / f"{row['canvas_id']}.jpg"
        if path.is_file():
            data = path.read_bytes()
        else:
            request = urllib.request.Request(row["review_image_url"], headers={"User-Agent": "VManus-GDT390/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            path.write_bytes(data)
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
        reviewed.append(
            {
                "review_index": len(reviewed) + 1,
                "page": page,
                "physical_folio": row["physical_folio"],
                "canvas_id": row["canvas_id"],
                "canvas_label": row["canvas_label"],
                "review_image_url": row["review_image_url"],
                "pixel_width": width,
                "pixel_height": height,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    with PUBLIC_HASHES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(reviewed[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(reviewed)

    font = ImageFont.load_default(size=22)
    cell_w, cell_h = 1000, 1450
    sheet_rows = []
    for sheet_index in range((len(reviewed) + 3) // 4):
        batch = reviewed[sheet_index * 4 : (sheet_index + 1) * 4]
        sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), "white")
        draw = ImageDraw.Draw(sheet)
        labels = []
        for cell_index, row in enumerate(batch):
            x = (cell_index % 2) * cell_w
            y = (cell_index // 2) * cell_h
            with Image.open(IMAGES / f"{row['canvas_id']}.jpg") as source:
                source = source.convert("RGB")
                source.thumbnail((940, 1360), Image.Resampling.LANCZOS)
                sheet.paste(source, (x + (cell_w - source.width) // 2, y + 55 + (1360 - source.height) // 2))
            label = f"{row['review_index']:02d} {row['page']} | Yale {row['canvas_id']}"
            labels.append(label)
            draw.text((x + 15, y + 15), label, fill="black", font=font)
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#666666", width=2)
        sheet_path = SHEETS / f"sheet_{sheet_index + 1:02d}.jpg"
        sheet.save(sheet_path, quality=92)
        sheet_rows.append({"sheet": sheet_path.name, "labels": " || ".join(labels), "sha256": hashlib.sha256(sheet_path.read_bytes()).hexdigest()})
    sheet_manifest = REVIEW_ROOT / "contact_sheet_manifest.tsv"
    with sheet_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sheet_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sheet_rows)
    print(json.dumps({"pages": len(reviewed), "contact_sheets": len(sheet_rows), "review_hash_manifest_sha256": hashlib.sha256(PUBLIC_HASHES.read_bytes()).hexdigest(), "formal_rows_read": 0, "automated_visual_judgments": 0, "f84_rows_retained": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
