#!/usr/bin/env python3
"""Guarded Yale IIIF mapping for the frozen GDT390 page allow-list."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
FRAME = ART / "gdt390_record_frame.tsv"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"


def iter_raw_canvas_objects(response):
    marker = b'"items":['
    prefix = b""
    while marker not in prefix:
        chunk = response.read(65536)
        if not chunk:
            raise RuntimeError("manifest items array not found")
        prefix += chunk
        if len(prefix) > 1_000_000:
            raise RuntimeError("manifest prefix unexpectedly large")
    pending = prefix.split(marker, 1)[1]
    depth = 0
    in_string = False
    escaped = False
    buffer = bytearray()
    started = False
    while True:
        if not pending:
            pending = response.read(65536)
            if not pending:
                return
        for byte in pending:
            char = chr(byte)
            if not started:
                if char == "]":
                    return
                if char != "{":
                    continue
                started = True
                depth = 1
                buffer = bytearray(b"{")
                in_string = escaped = False
                continue
            buffer.append(byte)
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    yield bytes(buffer)
                    started = False
                    buffer = bytearray()
        pending = b""


def labels(raw: bytes) -> list[str]:
    values: list[str] = []
    for match in re.finditer(rb'"label"\s*:\s*(\{[^{}]*\})', raw):
        try:
            block = json.loads(match.group(1))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for item in block.values() if isinstance(block, dict) else []:
            if isinstance(item, list):
                values.extend(str(value) for value in item)
    return values


def find_service(value):
    if isinstance(value, dict):
        if value.get("type") in {"ImageService2", "ImageService3"} and isinstance(value.get("id"), str):
            return value["id"]
        for child in value.values():
            found = find_service(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_service(child)
            if found:
                return found
    return None


def canvas_oid(value: dict) -> str:
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            identifier = item.get("id")
            if isinstance(identifier, str):
                match = re.search(r"/canvas/(\d+)(?:/|$)", identifier)
                if match:
                    return match.group(1)
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    raise RuntimeError("canvas ID missing")


def main() -> int:
    with FRAME.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle, delimiter="\t"))
    pages = sorted({row["page"] for row in records})
    assert len(pages) == 13 and all(not page.lower().startswith("f84") for page in pages)
    sides = {page[1:]: page for page in pages}
    rows: list[dict[str, object]] = []
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-GDT390/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        etag = response.headers.get("ETag", "")
        last_modified = response.headers.get("Last-Modified", "")
        for raw in iter_raw_canvas_objects(response):
            label_values = labels(raw)
            page_like = sorted({side for label in label_values for side in re.findall(r"(?<!\d)(\d+[rv])(?!\d)", label.lower())})
            if not page_like:
                continue
            # Raw labels are the only fields examined for rejected canvases.
            if any(side.startswith("84") for side in page_like):
                continue
            matched = sorted({sides[side] for side in page_like if side in sides})
            if not matched:
                continue
            canvas = json.loads(raw)
            oid = canvas_oid(canvas)
            service = find_service(canvas) or f"https://collections.library.yale.edu/iiif/2/{oid}"
            label = next((value for value in label_values if re.search(r"\d+[rv]", value.lower())), label_values[-1] if label_values else "")
            for page in matched:
                rows.append(
                    {
                        "page": page,
                        "physical_folio": next(record["physical_folio"] for record in records if record["page"] == page),
                        "canvas_id": oid,
                        "canvas_label": label,
                        "canvas_width": int(canvas.get("width", 0)),
                        "canvas_height": int(canvas.get("height", 0)),
                        "image_service_id": service,
                        "review_image_url": service.rstrip("/") + "/full/2000,/0/default.jpg",
                        "mapping_basis": "OFFICIAL_IIIF_CANVAS_LABEL_ALLOWLIST_MATCH",
                        "formal_access_state": "SEALED",
                    }
                )
    rows.sort(key=lambda row: (str(row["page"]), str(row["canvas_id"])))
    assert {row["page"] for row in rows} == set(pages)
    path = ART / "gdt390_image_manifest.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    meta = {
        "schema": "GDT390_IMAGE_MAPPING_V1",
        "manifest_url": MANIFEST_URL,
        "manifest_etag": etag,
        "manifest_last_modified": last_modified,
        "allowed_pages": len(pages),
        "mapped_pages": len({row["page"] for row in rows}),
        "mapping_rows": len(rows),
        "unique_canvases": len({row["canvas_id"] for row in rows}),
        "mixed_f84_canvas_fields_retained": 0,
        "rejected_canvas_nonlabel_fields_parsed_or_retained": 0,
        "formal_rows_read": 0,
        "image_manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    (ART / "gdt390_image_mapping.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print(json.dumps(meta, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
