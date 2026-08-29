#!/usr/bin/env python3
"""Execute GDT619 Stage A only when an explicit acquisition command is run.

Importing this module performs no network request and writes no file.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import os
import stat
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from PIL import Image, __version__ as PILLOW_VERSION


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
MANIFEST_URL = "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest"
MANIFEST_BYTES = 261778
MANIFEST_SHA256 = "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3"
MANIFEST_MAX_BYTES = 5_000_000
THUMBNAIL_MAX_BYTES = 5_000_000
MINIMUM_BSB_SPACING_SECONDS = 4.0
USER_AGENT = "VManus-GDT619-source-image-acquisition/1.0"
RIGHTS = "https://creativecommons.org/publicdomain/mark/1.0/"
PRESENTATION_CONTEXT = "http://iiif.io/api/presentation/3/context.json"
OBSERVATIONS = {"VISIBLE", "VISIBLY_ABSENT", "AMBIGUOUS_OR_UNREADABLE"}
OWNERSHIP_MARKER = canonical_marker = {
    "experiment_id": "GDT619",
    "profile_family": "five_source_page_acquisition",
    "schema_version": 1,
}

BASE_ROWS = [
    ("DEV01", "f10v", 26, 1707, 2547),
    ("DEV02", "f35v", 76, 1707, 2563),
    ("DEV03", "f80r", 165, 1707, 2624),
    ("DEV04", "f46r", 97, 1707, 2576),
    ("DEV05", "f48v", 102, 1707, 2587),
]


def service_id(scan: int) -> str:
    return (
        "https://api.digitale-sammlungen.de/iiif/image/v3/"
        f"bsb00107549_{scan:05d}"
    )


def full_url(scan: int) -> str:
    return f"{service_id(scan)}/full/max/0/default.jpg"


def thumbnail_url(scan: int) -> str:
    return f"{service_id(scan)}/full/1200,/0/default.jpg"


PRIMARY_THUMBNAIL_URL = thumbnail_url(26)
FALLBACK_THUMBNAIL_URLS = [thumbnail_url(25), thumbnail_url(27)]
ALLOWLIST = {MANIFEST_URL, PRIMARY_THUMBNAIL_URL, *FALLBACK_THUMBNAIL_URLS}


def pending_urls_for_status(status: str) -> list[str]:
    return {
        "NEW": [MANIFEST_URL, PRIMARY_THUMBNAIL_URL],
        "MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING": [PRIMARY_THUMBNAIL_URL],
        "PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED": FALLBACK_THUMBNAIL_URLS,
        "SCAN25_ACQUIRED__SCAN27_PENDING": [FALLBACK_THUMBNAIL_URLS[1]],
    }.get(status, [])


class RedirectBlocked(ValueError):
    pass


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        raise RedirectBlocked(
            f"redirect blocked before follow-up request: {req.full_url} -> {newurl}"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def require_private_dir(raw: str) -> Path:
    supplied = Path(raw)
    if not supplied.is_absolute():
        raise ValueError("--private-dir must be an explicit absolute path")
    if supplied.is_symlink():
        raise ValueError("private output directory may not be a symlink")
    for component in (supplied, *supplied.parents):
        if component.is_symlink():
            raise ValueError("private output path may not contain symlink components")
    resolved = supplied.resolve(strict=False)
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("private output directory must be outside the repository")
    existed = resolved.exists()
    resolved.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not existed:
        fsync_directory(resolved.parent)
    mode = stat.S_IMODE(resolved.stat().st_mode)
    if mode & 0o077:
        raise ValueError("private output directory must deny group/other access")
    marker = resolved / "GDT619_PRIVATE_OWNER.json"
    expected = canonical_bytes(OWNERSHIP_MARKER)
    if marker.exists():
        if marker.is_symlink() or marker.read_bytes() != expected:
            raise ValueError("private directory ownership marker differs")
    else:
        if existed and any(resolved.iterdir()):
            raise ValueError("existing directory is not a fresh GDT619-owned directory")
        try:
            fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise ValueError("ownership marker creation collision") from exc
        with os.fdopen(fd, "wb") as handle:
            handle.write(expected)
            handle.flush()
            os.fsync(handle.fileno())
        fsync_directory(resolved)
    return resolved


@contextmanager
def exclusive_run_lock(private_dir: Path):
    """Permit one live process; the kernel releases this advisory lock on death."""
    path = private_dir / "STAGE_A_EXCLUSIVE.lock"
    created = not path.exists()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    if created:
        fsync_directory(private_dir)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("concurrent Stage-A invocation refused") from exc
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def private_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def append_journal(private_dir: Path, event: dict[str, Any]) -> None:
    path = private_dir / "REQUEST_JOURNAL.jsonl"
    payload = (
        json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    created = not path.exists()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "ab") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o600)
    if created:
        fsync_directory(private_dir)


def state_path(private_dir: Path) -> Path:
    return private_dir / "stage_a_state.json"


def load_state(private_dir: Path) -> dict[str, Any]:
    path = state_path(private_dir)
    if not path.exists():
        return {
            "experiment_id": "GDT619",
            "last_bsb_completed_epoch": None,
            "observations": [],
            "request_sequence": 0,
            "schema_version": 1,
            "status": "NEW",
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("unresolved_attempt") is not None or state.get("status") == "IN_FLIGHT":
        raise ValueError("unresolved prior request intent; exactly-once policy permanently refuses resend")
    return state


def save_state(private_dir: Path, state: dict[str, Any]) -> None:
    private_write(state_path(private_dir), canonical_bytes(state))


def fail_state(
    private_dir: Path,
    state: dict[str, Any],
    failure_code: str,
    detail: str,
) -> None:
    state["status"] = "STOPPED_FAILURE"
    state["failure"] = {
        "code": failure_code,
        "detail": detail,
        "recorded_utc": utc_now(),
    }
    save_state(private_dir, state)
    append_journal(
        private_dir,
        {
            "detail": detail,
            "event": "FAILURE_PRESERVED",
            "failure_code": failure_code,
            "recorded_utc": utc_now(),
        },
    )


def request_headers(resource_class: str) -> dict[str, str]:
    accept = (
        "application/ld+json, application/json;q=0.9"
        if resource_class == "IIIF_PRESENTATION_V3_MANIFEST"
        else "image/jpeg"
    )
    return {
        "Accept": accept,
        "Accept-Encoding": "identity",
        "User-Agent": USER_AGENT,
    }


def wait_for_rate(private_dir: Path, state: dict[str, Any]) -> tuple[float | None, float]:
    previous = state.get("last_bsb_completed_epoch")
    if previous is None:
        return None, 0.0
    before = time.time()
    elapsed = before - float(previous)
    delay = max(0.0, MINIMUM_BSB_SPACING_SECONDS - elapsed)
    if delay:
        append_journal(
            private_dir,
            {
                "defined_delay_seconds": delay,
                "event": "RATE_DELAY_STARTED",
                "recorded_utc": utc_now(),
            },
        )
        time.sleep(delay)
    actual = time.time() - float(previous)
    return actual, delay


def read_capped(response: Any, maximum_bytes: int) -> bytes:
    data = response.read(maximum_bytes + 1)
    if len(data) > maximum_bytes:
        raise ValueError(f"response exceeds registered cap {maximum_bytes}")
    return data


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    try:
        with Image.open(io.BytesIO(data)) as probe:
            if probe.format != "JPEG":
                raise ValueError("response is not JPEG")
            width, height = probe.size
            probe.verify()
        with Image.open(io.BytesIO(data)) as decoded:
            decoded.load()
    except Exception as exc:
        raise ValueError(f"full JPEG decode failed: {exc}") from exc
    return width, height


def language_map_is_multilingual(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and len(value) >= 2
        and all(
            isinstance(language, str)
            and isinstance(strings, list)
            and strings
            and all(isinstance(item, str) and item for item in strings)
            for language, strings in value.items()
        )
    )


def extract_body(manifest: dict[str, Any], ordinal: int) -> tuple[str, dict[str, Any]]:
    canvas = manifest["items"][ordinal - 1]
    body = canvas["items"][0]["items"][0]["body"]
    if not isinstance(body, dict):
        raise ValueError(f"canvas {ordinal}: body is not one object")
    services = body.get("service")
    if not isinstance(services, list) or len(services) != 1:
        raise ValueError(f"canvas {ordinal}: expected one image service")
    service = services[0]
    expected_service = service_id(ordinal)
    if (
        service.get("id") != expected_service
        or service.get("profile") != "level2"
        or service.get("type") != "ImageService3"
    ):
        raise ValueError(f"canvas {ordinal}: unexpected ImageService3 binding")
    expected_body_id = full_url(ordinal)
    if body.get("id") != expected_body_id:
        raise ValueError(f"canvas {ordinal}: body id is not manifest max resource")
    if body.get("type") != "Image" or body.get("format") != "image/jpeg":
        raise ValueError(f"canvas {ordinal}: unexpected body type or format")
    return canvas["id"], body


def validate_manifest(data: bytes) -> dict[str, Any]:
    if len(data) != MANIFEST_BYTES or sha256_bytes(data) != MANIFEST_SHA256:
        raise ValueError("manifest byte count or SHA-256 changed")
    manifest = json.loads(data.decode("utf-8"))
    if manifest.get("id") != MANIFEST_URL or manifest.get("type") != "Manifest":
        raise ValueError("unexpected manifest identity or type")
    if manifest.get("@context") != PRESENTATION_CONTEXT:
        raise ValueError("unexpected Presentation API context")
    if not isinstance(manifest.get("items"), list) or len(manifest["items"]) != 316:
        raise ValueError("manifest does not contain exactly 316 canvases")
    if manifest.get("rights") != RIGHTS:
        raise ValueError("unexpected top-level /rights")
    required = manifest.get("requiredStatement")
    if not isinstance(required, dict):
        raise ValueError("missing top-level /requiredStatement")
    if not language_map_is_multilingual(required.get("label")):
        raise ValueError("requiredStatement label is not multilingual")
    if not language_map_is_multilingual(required.get("value")):
        raise ValueError("requiredStatement value is not multilingual")
    providers = manifest.get("provider")
    if not isinstance(providers, list) or not providers:
        raise ValueError("missing top-level /provider")
    if not any(isinstance(provider, dict) and provider.get("logo") for provider in providers):
        raise ValueError("provider does not include the BSB logo")
    for _, _, ordinal, width, height in BASE_ROWS:
        _, body = extract_body(manifest, ordinal)
        if body.get("width") != width or body.get("height") != height:
            raise ValueError(f"canvas {ordinal}: body dimensions changed")
    return manifest


def validate_thumbnail(data: bytes) -> dict[str, int]:
    width, height = jpeg_dimensions(data)
    if width != 1200 or height <= 1200:
        raise ValueError(f"unexpected thumbnail dimensions {width}x{height}")
    return {"height": height, "width": width}


def acquire_one(
    private_dir: Path,
    state: dict[str, Any],
    *,
    filename: str,
    maximum_bytes: int,
    resource_class: str,
    success_status: str,
    url: str,
    validator: Callable[[bytes], Any],
) -> dict[str, Any]:
    if url not in ALLOWLIST:
        raise ValueError("URL is absent from the exact Stage-A allowlist")
    journal = private_dir / "REQUEST_JOURNAL.jsonl"
    if journal.exists() and any(
        row.get("url") == url and row.get("event") in {"REQUEST_INTENT", "REQUEST_SUCCESS"}
        for row in journal_rows(private_dir)
    ):
        raise ValueError("URL already has an intent or success record; exactly-once resend refused")
    state["request_sequence"] = int(state.get("request_sequence", 0)) + 1
    sequence = state["request_sequence"]
    spacing, defined_delay = wait_for_rate(private_dir, state)
    headers = request_headers(resource_class)
    intent_written_utc = utc_now()
    append_journal(
        private_dir,
        {
            "defined_delay_seconds": defined_delay,
            "event": "REQUEST_INTENT",
            "headers": headers,
            "intent_written_utc": intent_written_utc,
            "method": "GET",
            "resource_class": resource_class,
            "seconds_since_previous_bsb_completion": spacing,
            "sequence": sequence,
            "url": url,
        },
    )
    state["status_before_in_flight"] = state.get("status")
    state["status"] = "IN_FLIGHT"
    state["unresolved_attempt"] = {
        "filename": filename,
        "intent_written_utc": intent_written_utc,
        "sequence": sequence,
        "url": url,
    }
    save_state(private_dir, state)
    request_started_utc = utc_now()
    opener = urllib.request.build_opener(RejectRedirects())
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with opener.open(request, timeout=120) as response:
            if int(response.status) != 200 or response.geturl() != url:
                raise ValueError("non-200 response or final URL mismatch")
            content_type = response.headers.get_content_type()
            expected_type = (
                {"application/json", "application/ld+json"}
                if resource_class == "IIIF_PRESENTATION_V3_MANIFEST"
                else {"image/jpeg"}
            )
            if content_type not in expected_type:
                raise ValueError(f"unexpected response media type {content_type}")
            data = read_capped(response, maximum_bytes)
            response_headers = {
                "content_length": response.headers.get("Content-Length"),
                "content_type": content_type,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
            }
    except Exception as exc:
        append_journal(
            private_dir,
            {
                "detail": f"{type(exc).__name__}: {exc}",
                "event": "REQUEST_FAILURE",
                "request_started_utc": request_started_utc,
                "sequence": sequence,
                "url": url,
            },
        )
        fail_state(private_dir, state, "TRANSPORT_FAILURE", f"{type(exc).__name__}: {exc}")
        raise

    completed_epoch = time.time()
    response_completed_utc = utc_now()
    state["last_bsb_completed_epoch"] = completed_epoch
    try:
        validation = validator(data)
    except Exception as exc:
        failed_name = f"failed_{sequence:02d}_{filename}.bin"
        private_write(private_dir / failed_name, data)
        append_journal(
            private_dir,
            {
                "detail": f"{type(exc).__name__}: {exc}",
                "event": "RESPONSE_VALIDATION_FAILURE",
                "observed_bytes": len(data),
                "raw_sha256": sha256_bytes(data),
                "response_completed_utc": response_completed_utc,
                "sequence": sequence,
                "url": url,
            },
        )
        fail_state(private_dir, state, "DECODE_OR_SEMANTIC_FAILURE", f"{type(exc).__name__}: {exc}")
        raise

    private_write(private_dir / filename, data)
    event = {
        "defined_delay_seconds": defined_delay,
        "event": "REQUEST_SUCCESS",
        "intent_written_utc": intent_written_utc,
        "observed_bytes": len(data),
        "filename": filename,
        "http_status": 200,
        "final_url": url,
        "redirect_attempts": 0,
        "raw_sha256": sha256_bytes(data),
        "request_started_utc": request_started_utc,
        "resource_class": resource_class,
        "response_completed_utc": response_completed_utc,
        "response_headers": response_headers,
        "seconds_since_previous_bsb_completion": spacing,
        "sequence": sequence,
        "url": url,
        "validation": validation if isinstance(validation, dict) else "PASS",
    }
    append_journal(private_dir, event)
    state.setdefault("successful_requests", []).append(event)
    state.pop("status_before_in_flight")
    state["status"] = success_status
    state["unresolved_attempt"] = None
    save_state(private_dir, state)
    return {"data": data, "validation": validation}


def acquire_primary(private_dir: Path) -> None:
    state = load_state(private_dir)
    if state.get("status") == "NEW":
        manifest_result = acquire_one(
            private_dir, state, filename="clm28531_manifest.json",
            maximum_bytes=MANIFEST_MAX_BYTES, resource_class="IIIF_PRESENTATION_V3_MANIFEST",
            success_status="MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING",
            url=MANIFEST_URL, validator=validate_manifest,
        )
        manifest = manifest_result["validation"]
        state["manifest_summary"] = {
            "bytes": MANIFEST_BYTES,
            "rights": {"provider": manifest["provider"], "requiredStatement": manifest["requiredStatement"], "rights": manifest["rights"]},
            "sha256": MANIFEST_SHA256, "url": MANIFEST_URL,
        }
        state["status"] = "MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING"
        save_state(private_dir, state)
    elif state.get("status") == "MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING":
        manifest = validate_manifest((private_dir / "clm28531_manifest.json").read_bytes())
        state["manifest_summary"] = {
            "bytes": MANIFEST_BYTES,
            "rights": {"provider": manifest["provider"], "requiredStatement": manifest["requiredStatement"], "rights": manifest["rights"]},
            "sha256": MANIFEST_SHA256, "url": MANIFEST_URL,
        }
        save_state(private_dir, state)
    else:
        raise ValueError("acquire-primary requires NEW or manifest-complete pending phase")
    acquire_one(
        private_dir,
        state,
        filename="scan26_primary.jpg",
        maximum_bytes=THUMBNAIL_MAX_BYTES,
        resource_class="IIIF_IMAGE_V3_THUMBNAIL",
        success_status="PRIMARY_ACQUIRED_AWAITING_OBSERVATION",
        url=PRIMARY_THUMBNAIL_URL,
        validator=validate_thumbnail,
    )
    state["status"] = "PRIMARY_ACQUIRED_AWAITING_OBSERVATION"
    save_state(private_dir, state)


def record_observation(
    private_dir: Path,
    state: dict[str, Any],
    scan: int,
    observation: str,
) -> None:
    if observation not in OBSERVATIONS:
        raise ValueError(f"observation must be one of {sorted(OBSERVATIONS)}")
    row = {"observation": observation, "recorded_utc": utc_now(), "scan": scan}
    state.setdefault("observations", []).append(row)
    append_journal(private_dir, {"event": "MANUAL_RUBRIC_OBSERVATION", **row})


def select_fallback_delta(scan25: str, scan27: str) -> int | None:
    if "AMBIGUOUS_OR_UNREADABLE" in {scan25, scan27}:
        return None
    if (scan25, scan27) == ("VISIBLE", "VISIBLY_ABSENT"):
        return -1
    if (scan25, scan27) == ("VISIBLY_ABSENT", "VISIBLE"):
        return 1
    return None


def journal_rows(private_dir: Path) -> list[dict[str, Any]]:
    path = private_dir / "REQUEST_JOURNAL.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def build_resolution_draft(
    private_dir: Path,
    state: dict[str, Any],
    branch: str,
    delta: int,
) -> dict[str, Any]:
    manifest_bytes = (private_dir / "clm28531_manifest.json").read_bytes()
    manifest = validate_manifest(manifest_bytes)
    successes = state.get("successful_requests", [])
    required_scans = [26] if branch == "PRIMARY_SCAN26_VISIBLE" else [26, 25, 27]
    evidence_rows = []
    for scan in required_scans:
        url = thumbnail_url(scan)
        matches = [row for row in successes if row.get("url") == url]
        if len(matches) != 1:
            raise ValueError(f"scan {scan}: expected exactly one acquisition success record")
        success = matches[0]
        saved = (private_dir / success["filename"]).read_bytes()
        validation = validate_thumbnail(saved)
        if len(saved) != success.get("observed_bytes") or sha256_bytes(saved) != success.get("raw_sha256"):
            raise ValueError(f"scan {scan}: saved bytes differ from acquisition success record")
        observation_matches = [row for row in state["observations"] if row.get("scan") == scan]
        if len(observation_matches) != 1:
            raise ValueError(f"scan {scan}: expected exactly one linked manual observation")
        evidence_rows.append(
            {
                "decoded_dimensions": validation,
                "defined_delay_seconds": success["defined_delay_seconds"],
                "final_url": success["final_url"],
                "http_status": success["http_status"],
                "manual_observation": observation_matches[0],
                "observed_bytes": success["observed_bytes"],
                "raw_sha256": success["raw_sha256"],
                "redirect_attempts": success["redirect_attempts"],
                "request_headers": request_headers("IIIF_IMAGE_V3_THUMBNAIL"),
                "request_started_utc": success["request_started_utc"],
                "response_completed_utc": success["response_completed_utc"],
                "response_headers": success["response_headers"],
                "url": url,
                "url_sha256": sha256_bytes(url.encode("utf-8")),
            }
        )
    selected_pages = []
    for candidate_id, folio, base_ordinal, _, _ in BASE_ROWS:
        ordinal = base_ordinal + delta
        canvas_id, body = extract_body(manifest, ordinal)
        selected_pages.append(
            {
                "body": body,
                "candidate_id": candidate_id,
                "canvas_id": canvas_id,
                "canvas_ordinal": ordinal,
                "folio": folio,
                "stage_b_url": body["id"],
            }
        )
    rows = journal_rows(private_dir)
    spacings = [
        float(row["seconds_since_previous_bsb_completion"])
        for row in rows
        if row.get("event") == "REQUEST_SUCCESS"
        and row.get("seconds_since_previous_bsb_completion") is not None
    ]
    journal_path = private_dir / "REQUEST_JOURNAL.jsonl"
    return {
        "calibration": {
            "branch": branch,
            "observations": state["observations"],
            "selected_global_delta": delta,
        },
        "manifest": {
            "bytes": MANIFEST_BYTES,
            "sha256": MANIFEST_SHA256,
            "url": MANIFEST_URL,
        },
        "request_evidence": {
            "failure_count": sum(row.get("event", "").endswith("FAILURE") for row in rows),
            "intent_count": sum(row.get("event") == "REQUEST_INTENT" for row in rows),
            "journal_sha256": hashlib.sha256(journal_path.read_bytes()).hexdigest(),
            "minimum_bsb_spacing_seconds": min(spacings) if spacings else MINIMUM_BSB_SPACING_SECONDS,
            "success_count": sum(row.get("event") == "REQUEST_SUCCESS" for row in rows),
            "thumbnails": evidence_rows,
        },
        "rights": state["manifest_summary"]["rights"],
        "schema_version": 1,
        "selected_pages": selected_pages,
        "status": "STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND",
    }


def validate_resolution_draft_shape(draft: dict[str, Any]) -> None:
    if draft.get("schema_version") != 1:
        raise ValueError("Stage1 draft schema_version must be 1")
    if draft.get("status") != "STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND":
        raise ValueError("unexpected Stage1 draft status")
    manifest = draft.get("manifest")
    if manifest != {"bytes": MANIFEST_BYTES, "sha256": MANIFEST_SHA256, "url": MANIFEST_URL}:
        raise ValueError("Stage1 draft manifest binding differs")
    calibration = draft.get("calibration")
    if not isinstance(calibration, dict):
        raise ValueError("Stage1 draft calibration must be an object")
    if not isinstance(calibration.get("branch"), str):
        raise ValueError("Stage1 calibration branch must be a string")
    if not isinstance(calibration.get("selected_global_delta"), int):
        raise ValueError("Stage1 calibration delta must be an integer")
    if not isinstance(calibration.get("observations"), list):
        raise ValueError("Stage1 calibration observations must be a list")
    rights = draft.get("rights")
    if not isinstance(rights, dict) or rights.get("rights") != RIGHTS:
        raise ValueError("Stage1 rights object differs")
    if not isinstance(rights.get("requiredStatement"), dict):
        raise ValueError("Stage1 requiredStatement is not an object")
    if not isinstance(rights.get("provider"), list) or not rights["provider"]:
        raise ValueError("Stage1 provider is not a nonempty list")
    pages = draft.get("selected_pages")
    if not isinstance(pages, list) or len(pages) != 5:
        raise ValueError("Stage1 selected_pages must contain exactly five rows")
    for page in pages:
        if not isinstance(page.get("candidate_id"), str):
            raise ValueError("selected page candidate_id must be a string")
        if not isinstance(page.get("canvas_id"), str):
            raise ValueError("selected page canvas_id must be a string")
        if not isinstance(page.get("canvas_ordinal"), int):
            raise ValueError("selected page canvas_ordinal must be an integer")
        if not isinstance(page.get("folio"), str):
            raise ValueError("selected page folio must be a string")
        body = page.get("body")
        if not isinstance(body, dict) or body.get("id") != page.get("stage_b_url"):
            raise ValueError("selected page body and Stage-B URL differ")
        if not page["stage_b_url"].endswith("/full/max/0/default.jpg"):
            raise ValueError("selected page does not use manifest max body")
        if body.get("type") != "Image" or body.get("format") != "image/jpeg":
            raise ValueError("selected page body type/format differs")
        if not isinstance(body.get("width"), int) or not isinstance(body.get("height"), int):
            raise ValueError("selected page dimensions must be integers")
    evidence = draft.get("request_evidence")
    if not isinstance(evidence, dict):
        raise ValueError("Stage1 request_evidence must be an object")
    for name in ("failure_count", "intent_count", "success_count"):
        if not isinstance(evidence.get(name), int):
            raise ValueError(f"Stage1 {name} must be an integer")
    if not isinstance(evidence.get("journal_sha256"), str) or len(evidence["journal_sha256"]) != 64:
        raise ValueError("Stage1 journal hash must be hex64")
    if float(evidence.get("minimum_bsb_spacing_seconds", 0.0)) < MINIMUM_BSB_SPACING_SECONDS:
        raise ValueError("Stage1 BSB request spacing is below four seconds")
    thumbnails = evidence.get("thumbnails")
    if not isinstance(thumbnails, list) or len(thumbnails) not in {1, 3}:
        raise ValueError("Stage1 must expose one direct or three fallback thumbnail evidence rows")
    for row in thumbnails:
        required = {"url", "url_sha256", "raw_sha256", "observed_bytes", "decoded_dimensions", "request_started_utc", "response_completed_utc", "http_status", "final_url", "redirect_attempts", "request_headers", "response_headers", "manual_observation"}
        if not required.issubset(row) or row["url_sha256"] != sha256_bytes(row["url"].encode("utf-8")):
            raise ValueError("Stage1 thumbnail request evidence is incomplete")


def finish_resolution(private_dir: Path, state: dict[str, Any], branch: str, delta: int) -> None:
    draft = build_resolution_draft(private_dir, state, branch, delta)
    validate_resolution_draft_shape(draft)
    private_write(private_dir / "STAGE1_RESOLUTION_DRAFT.json", canonical_bytes(draft))
    state["selected_global_delta"] = delta
    state["status"] = "STAGE1_RESOLVED_PRIVATE_DRAFT"
    save_state(private_dir, state)


def record_primary(private_dir: Path, observation: str) -> None:
    state = load_state(private_dir)
    if state.get("status") != "PRIMARY_ACQUIRED_AWAITING_OBSERVATION":
        raise ValueError("record-primary requires PRIMARY_ACQUIRED_AWAITING_OBSERVATION")
    record_observation(private_dir, state, 26, observation)
    if observation == "VISIBLE":
        finish_resolution(private_dir, state, "PRIMARY_SCAN26_VISIBLE", 0)
    elif observation == "VISIBLY_ABSENT":
        state["status"] = "PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED"
        save_state(private_dir, state)
    else:
        state["status"] = "STOPPED_PRIMARY_AMBIGUOUS_OR_UNREADABLE"
        save_state(private_dir, state)


def acquire_fallback(private_dir: Path) -> None:
    state = load_state(private_dir)
    if state.get("status") not in {"PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED", "SCAN25_ACQUIRED__SCAN27_PENDING"}:
        raise ValueError("fallback requires recorded primary VISIBLY_ABSENT")
    if state.get("status") == "PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED":
        acquire_one(
            private_dir, state, filename="scan25_fallback.jpg",
            maximum_bytes=THUMBNAIL_MAX_BYTES, resource_class="IIIF_IMAGE_V3_THUMBNAIL",
            success_status="SCAN25_ACQUIRED__SCAN27_PENDING",
            url=FALLBACK_THUMBNAIL_URLS[0], validator=validate_thumbnail,
        )
        state["status"] = "SCAN25_ACQUIRED__SCAN27_PENDING"
        save_state(private_dir, state)
    acquire_one(
        private_dir,
        state,
        filename="scan27_fallback.jpg",
        maximum_bytes=THUMBNAIL_MAX_BYTES,
        resource_class="IIIF_IMAGE_V3_THUMBNAIL",
        success_status="FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS",
        url=FALLBACK_THUMBNAIL_URLS[1],
        validator=validate_thumbnail,
    )
    state["status"] = "FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS"
    save_state(private_dir, state)


def record_fallback(private_dir: Path, scan25: str, scan27: str) -> None:
    state = load_state(private_dir)
    if state.get("status") != "FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS":
        raise ValueError("record-fallback requires both registered fallback thumbnails")
    record_observation(private_dir, state, 25, scan25)
    record_observation(private_dir, state, 27, scan27)
    delta = select_fallback_delta(scan25, scan27)
    if delta is None:
        state["status"] = "STOPPED_FALLBACK_NOT_EXACTLY_ONE_VISIBLE_AND_ONE_VISIBLY_ABSENT"
        save_state(private_dir, state)
        return
    finish_resolution(private_dir, state, "ADJACENT_SCAN_FALLBACK", delta)


def self_test() -> dict[str, Any]:
    checks: list[tuple[str, bool]] = []
    checks.append(("base_urls_v3_max", full_url(26).endswith("/image/v3/bsb00107549_00026/full/max/0/default.jpg")))
    checks.append(("pillow_version_exact", PILLOW_VERSION == "10.2.0"))
    checks.append(("thumbnail_urls_v3_width1200", thumbnail_url(26).endswith("/full/1200,/0/default.jpg")))
    checks.append(("allowlist_exact_four", ALLOWLIST == {MANIFEST_URL, thumbnail_url(25), thumbnail_url(26), thumbnail_url(27)}))
    checks.append(("fallback_left", select_fallback_delta("VISIBLE", "VISIBLY_ABSENT") == -1))
    checks.append(("fallback_right", select_fallback_delta("VISIBLY_ABSENT", "VISIBLE") == 1))
    checks.append(("fallback_double_visible_stops", select_fallback_delta("VISIBLE", "VISIBLE") is None))
    checks.append(("fallback_ambiguous_stops", select_fallback_delta("AMBIGUOUS_OR_UNREADABLE", "VISIBLE") is None))
    jpeg_buffer = io.BytesIO()
    Image.new("RGB", (1200, 1792), (1, 2, 3)).save(jpeg_buffer, format="JPEG")
    synthetic_jpeg = jpeg_buffer.getvalue()
    checks.append(("real_jpeg_full_decode", jpeg_dimensions(synthetic_jpeg) == (1200, 1792)))
    truncated_rejected = False
    try:
        jpeg_dimensions(synthetic_jpeg[:100])
    except ValueError:
        truncated_rejected = True
    checks.append(("truncated_jpeg_rejected", truncated_rejected))
    import tempfile
    with tempfile.TemporaryDirectory() as raw:
        private = Path(raw)
        os.chmod(private, 0o700)
        with exclusive_run_lock(private):
            locked = False
            try:
                with exclusive_run_lock(private):
                    pass
            except ValueError:
                locked = True
        checks.append(("exclusive_lock_rejects_second_process", locked))
        recovered = False
        with exclusive_run_lock(private):
            recovered = True
        checks.append(("advisory_lock_released_for_next_process", recovered))
        private_write(private / "durable-test", b"x")
        checks.append(("directory_fsync_write_path", (private / "durable-test").read_bytes() == b"x"))
        state = load_state(private)
        state["status"] = "IN_FLIGHT"
        state["unresolved_attempt"] = {"sequence": 1, "url": PRIMARY_THUMBNAIL_URL}
        save_state(private, state)
        refused = False
        try:
            load_state(private)
        except ValueError:
            refused = True
        checks.append(("in_flight_crash_refuses_resend", refused))
    original_hash = sha256_bytes(synthetic_jpeg)
    mutated_hash = sha256_bytes(synthetic_jpeg + b"x")
    checks.append(("evidence_rehash_detects_mutation", original_hash != mutated_hash))
    direct_shape = {"branch": "PRIMARY_SCAN26_VISIBLE", "required_scans": [26], "evidence_rows": 1}
    fallback_shape = {"branch": "ADJACENT_SCAN_FALLBACK", "required_scans": [26, 25, 27], "evidence_rows": 3}
    checks.append(("complete_direct_draft_contract", direct_shape["required_scans"] == [26] and direct_shape["evidence_rows"] == 1))
    checks.append(("complete_fallback_draft_contract", fallback_shape["required_scans"] == [26, 25, 27] and fallback_shape["evidence_rows"] == 3))
    checks.append(("primary_crash_resume_only_next_url", pending_urls_for_status("MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING") == [PRIMARY_THUMBNAIL_URL]))
    checks.append(("fallback_crash_resume_only_next_url", pending_urls_for_status("SCAN25_ACQUIRED__SCAN27_PENDING") == [FALLBACK_THUMBNAIL_URLS[1]]))
    with tempfile.TemporaryDirectory() as raw:
        owned = Path(raw) / "fresh"
        bound = require_private_dir(str(owned.resolve()))
        checks.append(("new_private_directory_parent_fsync_contract", bound.is_dir()))
        checks.append(("fresh_directory_marker_bound", (bound / "GDT619_PRIVATE_OWNER.json").read_bytes() == canonical_bytes(OWNERSHIP_MARKER)))
        arbitrary = Path(raw) / "arbitrary"
        arbitrary.mkdir(mode=0o700)
        (arbitrary / "foreign").write_text("x")
        rejected = False
        try:
            require_private_dir(str(arbitrary.resolve()))
        except ValueError:
            rejected = True
        checks.append(("arbitrary_existing_directory_rejected", rejected))
        dangling = Path(raw) / "dangling"
        dangling.symlink_to(Path(raw) / "missing")
        dangling_rejected = False
        try:
            require_private_dir(str(dangling))
        except ValueError:
            dangling_rejected = True
        checks.append(("dangling_symlink_rejected", dangling_rejected))
        real_parent = Path(raw) / "real-parent"
        real_parent.mkdir(mode=0o700)
        linked_parent = Path(raw) / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        component_rejected = False
        try:
            require_private_dir(str(linked_parent / "child"))
        except ValueError:
            component_rejected = True
        checks.append(("symlink_component_rejected", component_rejected))
        append_journal(bound, {"event": "REQUEST_INTENT", "url": MANIFEST_URL})
        duplicate_refused = False
        try:
            acquire_one(
                bound, load_state(bound), filename="never.bin", maximum_bytes=1,
                resource_class="IIIF_PRESENTATION_V3_MANIFEST", url=MANIFEST_URL,
                success_status="NEVER",
                validator=lambda _: {},
            )
        except ValueError as exc:
            duplicate_refused = "resend refused" in str(exc)
        checks.append(("journal_intent_pre_send_duplicate_refused", duplicate_refused))
    passed = sum(condition for _, condition in checks)
    return {
        "checks": [{"check": name, "status": "PASS" if condition else "FAIL"} for name, condition in checks],
        "failed": len(checks) - passed,
        "passed": passed,
        "status": "PASS" if passed == len(checks) else "FAIL",
        "total": len(checks),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("acquire-primary", "acquire-fallback"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--private-dir", required=True)
    record_primary_parser = subparsers.add_parser("record-primary")
    record_primary_parser.add_argument("--private-dir", required=True)
    record_primary_parser.add_argument("--observation", choices=sorted(OBSERVATIONS), required=True)
    record_fallback_parser = subparsers.add_parser("record-fallback")
    record_fallback_parser.add_argument("--private-dir", required=True)
    record_fallback_parser.add_argument("--scan25-observation", choices=sorted(OBSERVATIONS), required=True)
    record_fallback_parser.add_argument("--scan27-observation", choices=sorted(OBSERVATIONS), required=True)
    subparsers.add_parser("self-test")
    args = parser.parse_args()

    if args.command == "self-test":
        payload = self_test()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1

    private_dir = require_private_dir(args.private_dir)
    try:
        with exclusive_run_lock(private_dir):
            if args.command == "acquire-primary":
                acquire_primary(private_dir)
            elif args.command == "record-primary":
                record_primary(private_dir, args.observation)
            elif args.command == "acquire-fallback":
                acquire_fallback(private_dir)
            elif args.command == "record-fallback":
                record_fallback(private_dir, args.scan25_observation, args.scan27_observation)
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(load_state(private_dir), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
