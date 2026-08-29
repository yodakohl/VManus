#!/usr/bin/env python3
"""Acquire only the six registered official GDT617 metadata responses."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = EXPERIMENT / "artifacts" / "REGISTERED_SOURCE_BINDINGS.json"
OUTPUT_ROOT = EXPERIMENT / "artifacts" / "source_freeze"


RESOURCE_CLASS_BY_SOURCE_KIND = {
    "OFFICIAL_CATALOGUE_METADATA": "CATALOGUE_METADATA",
    "OFFICIAL_IIIF_MANIFEST": "IIIF_MANIFEST_METADATA",
}


class RedirectBlocked(ValueError):
    """Raised before urllib can issue a redirected follow-up request."""


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    """Record and reject every redirect before a second HTTP request exists."""

    def __init__(self, redirect_log: list[dict[str, Any]]) -> None:
        super().__init__()
        self.redirect_log = redirect_log

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        self.redirect_log.append(
            {
                "code": code,
                "followed": False,
                "from_url": req.full_url,
                "to_url": newurl,
            }
        )
        raise RedirectBlocked(
            f"redirect blocked before follow-up request: {req.full_url} -> {newurl}"
        )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def canonical_bnf_oai_record(data: bytes) -> bytes:
    root = ET.fromstring(data)
    record = next(node for node in root.iter() if local_name(node.tag) == "record")
    header = next(node for node in record if local_name(node.tag) == "header")
    dc = next(node for node in record.iter() if local_name(node.tag) == "dc")

    def fields(parent: ET.Element) -> list[dict[str, Any]]:
        return [
            {
                "attributes": sorted(child.attrib.items()),
                "name": local_name(child.tag),
                "text": (child.text or "").strip(),
            }
            for child in parent
        ]

    payload = {"dc": fields(dc), "header": fields(header)}
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def binding_bytes(source: dict[str, Any], raw: bytes) -> bytes:
    mode = source["binding_mode"]
    if mode == "RAW_BYTES":
        return raw
    if mode == "BNF_OAI_RECORD_CANONICAL_V1":
        return canonical_bnf_oai_record(raw)
    raise ValueError(f"unknown binding mode: {mode}")


def manifest_canvas_count(raw: bytes) -> int:
    payload = json.loads(raw)
    if "sequences" in payload:
        sequences = payload["sequences"]
        if len(sequences) != 1:
            raise ValueError(f"expected one IIIF v2 sequence, found {len(sequences)}")
        return len(sequences[0]["canvases"])
    if "items" in payload:
        return len(payload["items"])
    raise ValueError("manifest has neither IIIF v2 sequences nor IIIF v3 items")


def validate_source_bytes(source: dict[str, Any], raw: bytes) -> dict[str, Any]:
    if len(raw) > 1_000_000:
        raise ValueError(f"{source['source_id']}: response exceeds 1,000,000 bytes")
    text = raw.decode("utf-8")
    for marker in source["required_utf8_markers"]:
        if marker not in text:
            raise ValueError(f"{source['source_id']}: missing marker {marker!r}")

    bound = binding_bytes(source, raw)
    observed_binding_sha = sha256_bytes(bound)
    if observed_binding_sha != source["expected_binding_sha256"]:
        raise ValueError(
            f"{source['source_id']}: binding SHA-256 mismatch: "
            f"{observed_binding_sha} != {source['expected_binding_sha256']}"
        )
    if len(bound) != source["expected_binding_bytes"]:
        raise ValueError(
            f"{source['source_id']}: binding byte length mismatch: "
            f"{len(bound)} != {source['expected_binding_bytes']}"
        )

    canvas_count = None
    if source["source_kind"] == "OFFICIAL_IIIF_MANIFEST":
        canvas_count = manifest_canvas_count(raw)
        if canvas_count != source["expected_canvas_count"]:
            raise ValueError(
                f"{source['source_id']}: canvas count {canvas_count} != "
                f"{source['expected_canvas_count']}"
            )

    return {
        "binding_bytes": len(bound),
        "binding_mode": source["binding_mode"],
        "binding_sha256": observed_binding_sha,
        "canvas_count": canvas_count,
        "filename": source["filename"],
        "raw_bytes": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "source_id": source["source_id"],
        "source_kind": source["source_kind"],
        "url": source["url"],
        "witness_id": source["witness_id"],
    }


def fetch_source(
    source: dict[str, Any],
    user_agent: str,
    max_bytes: int,
    opener: urllib.request.OpenerDirector,
    allowed_urls: set[str],
    request_log: list[dict[str, Any]],
) -> tuple[bytes, str]:
    parsed = urllib.parse.urlsplit(source["url"])
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"{source['source_id']}: registered URL is not HTTPS")
    if source["url"] not in allowed_urls:
        raise ValueError(f"{source['source_id']}: URL is not in the exact registered allow-list")
    request_event = {
        "content_type": None,
        "method": "GET",
        "resource_class": RESOURCE_CLASS_BY_SOURCE_KIND[source["source_kind"]],
        "response_url": None,
        "sequence": len(request_log) + 1,
        "source_id": source["source_id"],
        "status": None,
        "url": source["url"],
    }
    request_log.append(request_event)
    request = urllib.request.Request(
        source["url"],
        headers={
            "Accept": source["accept"],
            "Accept-Encoding": "identity",
            "User-Agent": user_agent,
        },
        method="GET",
    )
    with opener.open(request, timeout=120) as response:
        if response.geturl() != source["url"]:
            raise ValueError(
                f"{source['source_id']}: redirect/final URL differs: {response.geturl()}"
            )
        content_type = response.headers.get_content_type()
        if not any(
            content_type.startswith(prefix.split(";", 1)[0])
            for prefix in source["expected_content_type_prefixes"]
        ):
            raise ValueError(
                f"{source['source_id']}: unexpected content type {content_type!r}"
            )
        request_event.update(
            {
                "content_type": content_type,
                "response_url": response.geturl(),
                "status": int(response.status),
            }
        )
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError(f"{source['source_id']}: response exceeds registered ceiling")
        return raw, content_type


def registry() -> dict[str, Any]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if payload["experiment_id"] != "GDT617" or len(payload["sources"]) != 6:
        raise ValueError("invalid GDT617 source registry")
    return payload


def request_audit_payload(
    cfg: dict[str, Any],
    request_log: list[dict[str, Any]],
    redirect_log: list[dict[str, Any]],
) -> dict[str, Any]:
    sources = cfg["sources"]
    allowed_urls = {source["url"] for source in sources}
    if len(allowed_urls) != len(sources):
        raise ValueError("registered source URLs are not unique")
    if redirect_log:
        raise ValueError("successful acquisition cannot contain a redirect attempt")
    if len(request_log) != len(sources):
        raise ValueError(
            f"request log count {len(request_log)} != registered count {len(sources)}"
        )
    for sequence, (source, event) in enumerate(zip(sources, request_log), start=1):
        expected_fields = {
            "method": "GET",
            "resource_class": RESOURCE_CLASS_BY_SOURCE_KIND[source["source_kind"]],
            "response_url": source["url"],
            "sequence": sequence,
            "source_id": source["source_id"],
            "status": 200,
            "url": source["url"],
        }
        for key, expected in expected_fields.items():
            if event.get(key) != expected:
                raise ValueError(
                    f"request log mismatch for {source['source_id']}:{key}: "
                    f"{event.get(key)!r} != {expected!r}"
                )
        content_type = event.get("content_type")
        if not isinstance(content_type, str) or not any(
            content_type.startswith(prefix.split(";", 1)[0])
            for prefix in source["expected_content_type_prefixes"]
        ):
            raise ValueError(
                f"request log content type mismatch for {source['source_id']}"
            )

    non_allowlisted = sum(event.get("url") not in allowed_urls for event in request_log)
    resource_counts = {
        resource_class: sum(
            event.get("resource_class") == resource_class for event in request_log
        )
        for resource_class in sorted(set(RESOURCE_CLASS_BY_SOURCE_KIND.values()))
    }
    allowlist_rows = [
        {
            "resource_class": RESOURCE_CLASS_BY_SOURCE_KIND[source["source_kind"]],
            "source_id": source["source_id"],
            "url": source["url"],
        }
        for source in sources
    ]
    allowlist_bytes = (
        json.dumps(allowlist_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    return {
        "allowlist_sha256": sha256_bytes(allowlist_bytes),
        "allowlisted_initial_requests": len(request_log) - non_allowlisted,
        "canvas_requests": sum(
            event.get("resource_class") == "IIIF_CANVAS" for event in request_log
        ),
        "image_requests": sum(
            event.get("resource_class") in {"IIIF_CANVAS", "IMAGE_BYTES", "IMAGE_SERVICE"}
            for event in request_log
        ),
        "non_allowlisted_requests": non_allowlisted,
        "redirect_attempts": len(redirect_log),
        "redirect_followed": sum(bool(event.get("followed")) for event in redirect_log),
        "redirect_log": redirect_log,
        "request_log": request_log,
        "requests_completed": sum(event.get("status") == 200 for event in request_log),
        "requests_started": len(request_log),
        "resource_counts": resource_counts,
        "target_requests": sum(
            str(event.get("resource_class", "")).startswith("VOYNICH_")
            for event in request_log
        ),
    }


def report_payload(
    cfg: dict[str, Any],
    rows: list[dict[str, Any]],
    request_log: list[dict[str, Any]],
    redirect_log: list[dict[str, Any]],
) -> dict[str, Any]:
    request_audit = request_audit_payload(cfg, request_log, redirect_log)
    return {
        "canvas_requests": request_audit["canvas_requests"],
        "decision": "SOURCE_BINDING_PASS__TARGET_UNOPENED",
        "experiment_id": "GDT617",
        "image_requests": request_audit["image_requests"],
        "request_audit": request_audit,
        "registry_sha256": sha256_bytes(REGISTRY_PATH.read_bytes()),
        "source_count": len(rows),
        "sources": rows,
        "target_requests": request_audit["target_requests"],
        "witness_count": len({row["witness_id"] for row in rows}),
    }


def write_reports(
    destination: Path,
    cfg: dict[str, Any],
    rows: list[dict[str, Any]],
    request_log: list[dict[str, Any]],
    redirect_log: list[dict[str, Any]],
) -> None:
    (destination / "SOURCE_ACQUISITION.json").write_text(
        json.dumps(
            report_payload(cfg, rows, request_log, redirect_log),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with (destination / "SOURCE_HASHES.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            lineterminator="\n",
            fieldnames=[
                "source_id",
                "witness_id",
                "source_kind",
                "filename",
                "raw_bytes",
                "raw_sha256",
                "binding_mode",
                "binding_bytes",
                "binding_sha256",
                "canvas_count",
                "content_type",
                "url",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def acquire() -> dict[str, Any]:
    if OUTPUT_ROOT.exists():
        raise FileExistsError(
            f"registered output already exists: {OUTPUT_ROOT.relative_to(ROOT)}; "
            "use --verify-existing"
        )
    cfg = registry()
    OUTPUT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="gdt617-source-freeze-", dir=OUTPUT_ROOT.parent))
    rows: list[dict[str, Any]] = []
    request_log: list[dict[str, Any]] = []
    redirect_log: list[dict[str, Any]] = []
    opener = urllib.request.build_opener(RejectRedirects(redirect_log))
    allowed_urls = {source["url"] for source in cfg["sources"]}
    try:
        for source in cfg["sources"]:
            raw, content_type = fetch_source(
                source,
                cfg["user_agent"],
                cfg["max_bytes_per_response"],
                opener,
                allowed_urls,
                request_log,
            )
            row = validate_source_bytes(source, raw)
            row["content_type"] = content_type
            (temp / source["filename"]).write_bytes(raw)
            rows.append(row)
        write_reports(temp, cfg, rows, request_log, redirect_log)
        temp.rename(OUTPUT_ROOT)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    return report_payload(cfg, rows, request_log, redirect_log)


def verify_existing() -> dict[str, Any]:
    cfg = registry()
    if not OUTPUT_ROOT.is_dir():
        raise FileNotFoundError(f"missing registered source freeze: {OUTPUT_ROOT.relative_to(ROOT)}")
    rows: list[dict[str, Any]] = []
    expected_files = {
        source["filename"] for source in cfg["sources"]
    } | {"SOURCE_ACQUISITION.json", "SOURCE_HASHES.tsv"}
    actual_files = {path.name for path in OUTPUT_ROOT.iterdir() if path.is_file()}
    if actual_files != expected_files:
        raise ValueError(
            f"source-freeze file set mismatch: {sorted(actual_files)} != {sorted(expected_files)}"
        )
    for source in cfg["sources"]:
        raw = (OUTPUT_ROOT / source["filename"]).read_bytes()
        rows.append(validate_source_bytes(source, raw))
    observed_report = json.loads(
        (OUTPUT_ROOT / "SOURCE_ACQUISITION.json").read_text(encoding="utf-8")
    )
    observed_audit = observed_report.get("request_audit", {})
    expected_report = report_payload(
        cfg,
        rows,
        observed_audit.get("request_log", []),
        observed_audit.get("redirect_log", []),
    )
    source_by_id = {source["source_id"]: source for source in cfg["sources"]}
    # Network content type is checked but is not part of byte-derived replay.
    for row in observed_report.get("sources", []):
        content_type = row.pop("content_type", "")
        source = source_by_id.get(row.get("source_id"))
        if source is None or not any(
            content_type.startswith(prefix.split(";", 1)[0])
            for prefix in source["expected_content_type_prefixes"]
        ):
            raise ValueError(
                f"SOURCE_ACQUISITION.json has invalid content type for {row.get('source_id')}"
            )
    if observed_report != expected_report:
        raise ValueError("SOURCE_ACQUISITION.json does not replay from registered snapshots")

    with (OUTPUT_ROOT / "SOURCE_HASHES.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        hash_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(hash_rows) != len(rows):
        raise ValueError("SOURCE_HASHES.tsv row count mismatch")
    hash_by_id = {row["source_id"]: row for row in hash_rows}
    for expected in rows:
        observed = hash_by_id.get(expected["source_id"])
        if observed is None:
            raise ValueError(f"SOURCE_HASHES.tsv missing {expected['source_id']}")
        for key in (
            "witness_id",
            "source_kind",
            "filename",
            "raw_sha256",
            "binding_mode",
            "binding_sha256",
            "url",
        ):
            if observed[key] != str(expected[key]):
                raise ValueError(
                    f"SOURCE_HASHES.tsv mismatch for {expected['source_id']}:{key}"
                )
        for key in ("raw_bytes", "binding_bytes"):
            if observed[key] != str(expected[key]):
                raise ValueError(
                    f"SOURCE_HASHES.tsv mismatch for {expected['source_id']}:{key}"
                )
        expected_canvas = "" if expected["canvas_count"] is None else str(expected["canvas_count"])
        if observed["canvas_count"] != expected_canvas:
            raise ValueError(
                f"SOURCE_HASHES.tsv mismatch for {expected['source_id']}:canvas_count"
            )
        source = source_by_id[expected["source_id"]]
        if not any(
            observed["content_type"].startswith(prefix.split(";", 1)[0])
            for prefix in source["expected_content_type_prefixes"]
        ):
            raise ValueError(
                f"SOURCE_HASHES.tsv content type mismatch for {expected['source_id']}"
            )
    return expected_report


def network_guard_selftest() -> dict[str, bool]:
    """Exercise the exact-allowlist audit and redirect blocker without a network call."""

    cfg = registry()
    synthetic_log = [
        {
            "content_type": source["expected_content_type_prefixes"][0],
            "method": "GET",
            "resource_class": RESOURCE_CLASS_BY_SOURCE_KIND[source["source_kind"]],
            "response_url": source["url"],
            "sequence": sequence,
            "source_id": source["source_id"],
            "status": 200,
            "url": source["url"],
        }
        for sequence, source in enumerate(cfg["sources"], start=1)
    ]
    clean = request_audit_payload(cfg, synthetic_log, [])

    tampered = [dict(event) for event in synthetic_log]
    tampered[0]["url"] = "https://example.invalid/not-registered"
    unknown_rejected = False
    try:
        request_audit_payload(cfg, tampered, [])
    except ValueError:
        unknown_rejected = True

    redirect_log: list[dict[str, Any]] = []
    handler = RejectRedirects(redirect_log)
    redirect_rejected = False
    try:
        handler.redirect_request(
            urllib.request.Request(cfg["sources"][0]["url"]),
            None,
            302,
            "Found",
            {},
            "https://example.invalid/redirect-target",
        )
    except RedirectBlocked:
        redirect_rejected = True

    return {
        "clean_exact_six": clean["requests_started"] == 6,
        "redirect_marked_unfollowed": bool(redirect_log)
        and redirect_log[0]["followed"] is False,
        "redirect_rejected": redirect_rejected,
        "unknown_url_rejected": unknown_rejected,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execute-registered-source-acquisition", action="store_true")
    mode.add_argument("--verify-existing", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = acquire() if args.execute_registered_source_acquisition else verify_existing()
    except (OSError, ValueError, KeyError, ET.ParseError, json.JSONDecodeError) as exc:
        print(f"GDT617_SOURCE_BINDING_FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        f"{result['decision']} sources={result['source_count']} "
        f"witnesses={result['witness_count']} images={result['image_requests']} "
        f"targets={result['target_requests']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
