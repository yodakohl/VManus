#!/usr/bin/env python3
"""At-most-once-per-bound-state GDT620 Stage-B source-page acquisition.

Importing this module performs no network request and writes no file.  The
``acquire`` command is the sole network-enabled entry point.  ``self-test``
uses an in-memory mock transport only.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import inspect
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from PIL import Image, ImageFile, __version__ as PILLOW_VERSION


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
WORKSPACE_GIT_DIR = ROOT / ".git"
GIT_EXECUTABLE = Path("/usr/bin/git")

EXPERIMENT_ID = "GDT620"
SCHEMA_VERSION = 1
PUBLIC_GDT619_COMMIT = "e82d73d6300f51c810ff131711ace31bb2610b69"
GDT619_STAGE1_RELATIVE_PATH = (
    "experiments/yolo/gdt619_five_source_page_acquisition/"
    "artifacts/STAGE1_RESOLUTION.json"
)
GDT619_STAGE1_SHA256 = (
    "95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422"
)
GDT619_PROFILE_RELATIVE_PATH = (
    "experiments/yolo/gdt619_five_source_page_acquisition/"
    "artifacts/REGISTERED_REQUEST_PROFILE.json"
)
GDT619_PROFILE_SHA256 = (
    "c577525c5045b2e59ba68741fd098c1d94f43f6d52ac4364683f4dd1e1064164"
)
GDT619_MANIFEST_SHA256 = (
    "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3"
)
GDT619_STAGE1_JOURNAL_SHA256 = (
    "46d652c4128ae06cfe73cb8eb32a2819257cbda7008b99c7aab9920e0070ea73"
)
GDT619_LAST_BSB_COMPLETED_UTC = "2026-08-29T06:02:18.011459+00:00"

RESPONSE_CAP_BYTES = 50_000_000
TOTAL_BODY_CAP_BYTES = 500_000_000
SOCKET_OPERATION_TIMEOUT_SECONDS = 60
REQUEST_TOTAL_WALL_SECONDS = 180
# Backward-readable name for the public 180-second per-request wall deadline.
REQUEST_TIMEOUT_SECONDS = REQUEST_TOTAL_WALL_SECONDS
STREAM_CHUNK_BYTES = 1024 * 1024
MINIMUM_REQUEST_SPACING_SECONDS = 4.0
# GDT619 used the narrower name; its Stage1 evidence is validated against the
# same four-second value.
MINIMUM_BSB_SPACING_SECONDS = MINIMUM_REQUEST_SPACING_SECONDS
MAX_NEW_BSB_REQUESTS = 5
MAX_NEW_BNF_REQUESTS = 5
PRIOR_STAGE_A_BSB_REQUESTS = 5
CUMULATIVE_BSB_REQUEST_CAP = 10
MAX_TOTAL_STAGE_B_REQUESTS = 10
CONCURRENCY = 1
RETRIES = 0
FOLLOW_REDIRECTS = False
HTTP_METHOD = "GET"
USER_AGENT = "VManus-GDT620-stage-b-source-acquisition/1.0"
REQUEST_HEADERS = {
    "Accept": "image/jpeg",
    "Accept-Encoding": "identity",
    "User-Agent": USER_AGENT,
}
PILLOW_REQUIRED_VERSION = "10.2.0"

OWNER_MARKER_FILENAME = "GDT620_STAGE_B_PRIVATE_OWNER.json"
LOCK_FILENAME = "STAGE_B_EXCLUSIVE.lock"
STATE_FILENAME = "stage_b_state.json"
JOURNAL_FILENAME = "REQUEST_JOURNAL.jsonl"
RESULT_DRAFT_FILENAME = "STAGE_B_RESULT_DRAFT.json"

SEALED_DATA = {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
PASS_STATUS = (
    "TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED"
)
SECOND_EXECUTION_STATE_DIRECTORY_FORBIDDEN_BY_POLICY = True

GDT620_REGISTERED_PATHS = (
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/METHOD.md",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/PREREGISTRATION.md",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/artifacts/REGISTERED_STAGE_B_PROFILE.json",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/requirements.txt",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/src/acquire_stage_b.py",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/src/validate.py",
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/experiment.json",
)
SELF_TEST_REGISTRATION_COMMIT = "0" * 40

REGISTERED_LOG_FIELDS = (
    "SEQUENCE",
    "STAGE",
    "CANDIDATE_ID",
    "RESOURCE_CLASS",
    "REQUEST_URL",
    "REQUEST_URL_SHA256",
    "STATUS",
    "RESPONSE_URL",
    "REDIRECT_ATTEMPTS",
    "CONTENT_TYPE",
    "CONTENT_LENGTH_HEADER",
    "OBSERVED_BYTES",
    "RAW_SHA256",
    "DECODED_WIDTH",
    "DECODED_HEIGHT",
    "ETAG",
    "LAST_MODIFIED",
    "INTENT_WRITTEN_UTC",
    "REQUEST_STARTED_UTC",
    "RESPONSE_COMPLETED_UTC",
    "SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION",
    "DEFINED_DELAY_SECONDS",
)


@dataclass(frozen=True)
class Resource:
    sequence: int
    candidate_id: str
    headword: str
    witness: str
    provider: str
    resource_class: str
    url: str
    expected_width: int
    expected_height: int
    filename: str


def bsb_resource(
    sequence: int,
    candidate_id: str,
    headword: str,
    scan: int,
    width: int,
    height: int,
) -> Resource:
    return Resource(
        sequence=sequence,
        candidate_id=candidate_id,
        headword=headword,
        witness="CLM28531",
        provider="BSB",
        resource_class="IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY",
        url=(
            "https://api.digitale-sammlungen.de/iiif/image/v3/"
            f"bsb00107549_{scan:05d}/full/max/0/default.jpg"
        ),
        expected_width=width,
        expected_height=height,
        filename=f"{sequence:02d}_BSB_CLM28531_{candidate_id}.jpg",
    )


def bnf_resource(
    sequence: int,
    candidate_id: str,
    headword: str,
    canvas: int,
    width: int,
    height: int,
) -> Resource:
    return Resource(
        sequence=sequence,
        candidate_id=candidate_id,
        headword=headword,
        witness="LAT6823",
        provider="BNF",
        resource_class="IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE",
        url=(
            "https://gallica.bnf.fr/iiif/ark:/12148/"
            f"btv1b6000517p/f{canvas}/full/full/0/native.jpg"
        ),
        expected_width=width,
        expected_height=height,
        filename=f"{sequence:02d}_BNF_LAT6823_{candidate_id}.jpg",
    )


RESOURCES = (
    bsb_resource(1, "DEV01", "Balsamus", 25, 1707, 2466),
    bsb_resource(2, "DEV02", "Cerfolium", 75, 1707, 2581),
    bsb_resource(3, "DEV03", "Liquiritia", 164, 1707, 2562),
    bsb_resource(4, "DEV04", "Cucurbita", 96, 1707, 2591),
    bsb_resource(5, "DEV05", "Diptamus", 101, 1707, 2581),
    bnf_resource(6, "DEV01", "Balsamus", 58, 3302, 4581),
    bnf_resource(7, "DEV02", "Cerfolium", 96, 3451, 4553),
    bnf_resource(8, "DEV03", "Liquiritia", 178, 3284, 4557),
    bnf_resource(9, "DEV04", "Cucurbita", 91, 3333, 4388),
    bnf_resource(10, "DEV05", "Diptamus", 122, 3346, 4574),
)
EXACT_ALLOWLIST = frozenset(resource.url for resource in RESOURCES)

def owner_marker(public_registration_commit: str) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "gdt619_profile_sha256": GDT619_PROFILE_SHA256,
        "gdt619_stage1_commit": PUBLIC_GDT619_COMMIT,
        "gdt619_stage1_sha256": GDT619_STAGE1_SHA256,
        "gdt620_public_registration_commit": public_registration_commit,
        "profile_family": "stage_b_source_page_acquisition",
        "schema_version": SCHEMA_VERSION,
        "second_execution_state_directory_forbidden_by_policy": True,
    }


class StageBError(RuntimeError):
    """Base class for deterministic Stage-B stops."""


class UnresolvedAttemptError(StageBError):
    """A durable intent exists whose request cannot safely be repeated."""


class AcquisitionFailure(StageBError):
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.context = context or {}


class RedirectBlocked(AcquisitionFailure):
    def __init__(self, old_url: str, new_url: str, status: int) -> None:
        super().__init__(
            "REDIRECT_BLOCKED",
            "redirect blocked before follow-up request",
            context={
                "HTTP_STATUS": status,
                "RESPONSE_URL": new_url,
                "REDIRECT_ATTEMPTS": 1,
                "REQUEST_URL": old_url,
            },
        )


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
        del fp, msg, headers
        raise RedirectBlocked(req.full_url, newurl, code)


class Clock(Protocol):
    def time(self) -> float: ...

    def monotonic(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...


class SystemClock:
    def time(self) -> float:
        return time.time()

    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class Transport(Protocol):
    def open(self, request: urllib.request.Request, timeout: int) -> Any: ...


class UrllibTransport:
    """One-shot transport with proxies, cookies, auth, and redirects disabled."""

    def __init__(self) -> None:
        # An explicit empty ProxyHandler prevents environment proxy discovery.
        # No cookie or authentication handler is installed.
        self._proxy_handler = urllib.request.ProxyHandler({})
        self._opener = urllib.request.build_opener(
            self._proxy_handler, RejectRedirects()
        )
        self._opener.addheaders = []

    def open(self, request: urllib.request.Request, timeout: int) -> Any:
        observed = {key.lower(): value for key, value in request.header_items()}
        expected = {key.lower(): value for key, value in REQUEST_HEADERS.items()}
        if observed != expected:
            raise StageBError("request contains an implicit or unregistered header")
        if request.get_method() != HTTP_METHOD or request.full_url not in EXACT_ALLOWLIST:
            raise StageBError("transport received an unregistered method or URL")
        return self._opener.open(request, timeout=timeout)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def utc_from_epoch(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(
        timespec="microseconds"
    )


def parse_utc(value: str) -> float:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise StageBError("UTC timestamp lacks a timezone")
    return parsed.timestamp()


def fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def nofollow_flag() -> int:
    return getattr(os, "O_NOFOLLOW", 0)


def validate_private_file(path: Path, *, expected_mode: int = 0o600) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise StageBError(f"required private file is absent: {path.name}") from exc
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise StageBError(f"private entry is not a regular non-symlink: {path.name}")
    if info.st_uid != os.geteuid():
        raise StageBError(f"private file owner differs: {path.name}")
    if stat.S_IMODE(info.st_mode) != expected_mode:
        raise StageBError(f"private file mode differs from {expected_mode:04o}: {path.name}")


def raw_components_are_symlink_free(path: Path) -> bool:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if os.path.lexists(current) and stat.S_ISLNK(os.lstat(current).st_mode):
            return False
    return True


def permitted_private_names() -> set[str]:
    return {
        OWNER_MARKER_FILENAME,
        LOCK_FILENAME,
        STATE_FILENAME,
        JOURNAL_FILENAME,
        RESULT_DRAFT_FILENAME,
        *(resource.filename for resource in RESOURCES),
    }


def audit_private_directory_entries(private_dir: Path) -> None:
    permitted = permitted_private_names()
    for path in private_dir.iterdir():
        if path.name not in permitted:
            raise StageBError("private directory contains an unrecognized entry")
        validate_private_file(path)


def create_owner_marker(private_dir: Path, public_registration_commit: str) -> None:
    path = private_dir / OWNER_MARKER_FILENAME
    payload = canonical_bytes(owner_marker(public_registration_commit))
    if path.exists() or path.is_symlink():
        validate_private_file(path)
        if path.read_bytes() != payload:
            raise StageBError("private directory owner marker differs")
        return
    if any(private_dir.iterdir()):
        raise StageBError("existing private directory is neither fresh nor GDT620-owned")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow_flag()
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(fd)
    fsync_directory(private_dir)


def require_private_dir(raw: str, public_registration_commit: str) -> Path:
    supplied = Path(raw)
    if not supplied.is_absolute():
        raise StageBError("--private-dir must be an explicit absolute path")
    if ".." in supplied.parts:
        raise StageBError("--private-dir may not contain parent traversal")
    if not raw_components_are_symlink_free(supplied):
        raise StageBError("private output path may not contain symlink components")
    resolved = supplied.resolve(strict=False)
    if resolved == ROOT or ROOT in resolved.parents:
        raise StageBError("private output directory must be outside the repository")
    if resolved == Path(resolved.anchor):
        raise StageBError("filesystem root cannot be the private output directory")
    if not resolved.exists():
        if not resolved.parent.is_dir():
            raise StageBError("private output parent must already exist")
        os.mkdir(resolved, mode=0o700)
        os.chmod(resolved, 0o700)
        fsync_directory(resolved.parent)
    info = resolved.lstat()
    if not stat.S_ISDIR(info.st_mode) or resolved.is_symlink():
        raise StageBError("private output must be a non-symlink directory")
    if info.st_uid != os.geteuid():
        raise StageBError("private output directory owner differs")
    if stat.S_IMODE(info.st_mode) != 0o700:
        raise StageBError("private output directory mode must be exactly 0700")
    create_owner_marker(resolved, public_registration_commit)
    audit_private_directory_entries(resolved)
    return resolved


@dataclass
class PrivateRunLock:
    private_dir: Path
    fd: int | None = None

    def __enter__(self) -> "PrivateRunLock":
        path = self.private_dir / LOCK_FILENAME
        created = not os.path.lexists(path)
        flags = os.O_WRONLY | os.O_CREAT | nofollow_flag()
        fd = os.open(path, flags, 0o600)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            os.close(fd)
            raise StageBError("Stage-B lock is not an owned regular file")
        if not created and stat.S_IMODE(info.st_mode) != 0o600:
            os.close(fd)
            raise StageBError("Stage-B lock mode differs from 0600")
        os.fchmod(fd, 0o600)
        if created:
            os.fsync(fd)
            fsync_directory(self.private_dir)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(fd)
            raise StageBError("concurrent Stage-B invocation refused") from exc
        self.fd = fd
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        del exc_type, exc, traceback
        assert self.fd is not None
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)
        self.fd = None


def private_write(path: Path, data: bytes, *, replace: bool) -> None:
    if path.exists() or path.is_symlink():
        validate_private_file(path)
        if not replace:
            raise StageBError(f"refusing to overwrite private file: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    if temporary.exists() or temporary.is_symlink():
        raise StageBError("stale private temporary file exists")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow_flag()
    fd = os.open(temporary, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        fsync_directory(path.parent)
    finally:
        os.close(fd)
        if temporary.exists():
            temporary.unlink()


def append_journal(private_dir: Path, event: dict[str, Any]) -> None:
    missing = set(REGISTERED_LOG_FIELDS) - set(event)
    if missing:
        raise StageBError(f"journal event lacks registered fields: {sorted(missing)}")
    path = private_dir / JOURNAL_FILENAME
    created = not os.path.lexists(path)
    if not created:
        validate_private_file(path)
    payload = (
        json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | nofollow_flag()
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "ab", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(fd)
    if created:
        fsync_directory(private_dir)


def journal_rows(private_dir: Path) -> list[dict[str, Any]]:
    path = private_dir / JOURNAL_FILENAME
    if not path.exists():
        return []
    validate_private_file(path)
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise StageBError(f"journal line {line_number} is invalid JSON") from exc
        if not isinstance(row, dict) or not set(REGISTERED_LOG_FIELDS).issubset(row):
            raise StageBError(f"journal line {line_number} violates the log contract")
        rows.append(row)
    return rows


def workspace_git_environment() -> dict[str, str]:
    """Return the process environment without any inherited Git override."""

    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }


def run_workspace_git(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Run a read-only Git query against this workspace's explicit repository."""

    if not GIT_EXECUTABLE.is_file() or not os.access(GIT_EXECUTABLE, os.X_OK):
        raise StageBError("bound system Git executable is unavailable")
    if not WORKSPACE_GIT_DIR.is_dir() or WORKSPACE_GIT_DIR.is_symlink():
        raise StageBError("workspace .git is not a regular repository directory")
    return subprocess.run(
        [
            str(GIT_EXECUTABLE),
            f"--git-dir={WORKSPACE_GIT_DIR}",
            f"--work-tree={ROOT}",
            *arguments,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        env=workspace_git_environment(),
        timeout=30,
    )


def load_git_blob(commit: str, relative_path: str) -> bytes:
    completed = run_workspace_git(["show", f"{commit}:{relative_path}"])
    if completed.returncode != 0:
        raise StageBError("bound public git object is unavailable offline")
    return completed.stdout


def validate_gdt620_registration_profile(profile: dict[str, Any]) -> None:
    """Validate the network-authorizing portions of a GDT620 profile."""

    gate = profile.get("execution_publication_gate", {})
    if tuple(gate.get("committed_paths_must_match_runtime_bytes", [])) != GDT620_REGISTERED_PATHS:
        raise StageBError("public GDT620 runtime path gate differs")
    if (
        gate.get("network_forbidden_until_registration_commit_is_public") is not True
        or gate.get("public_registration_commit_argument_required") is not True
        or gate.get("registration_commit_must_be_ancestor_of_origin_main") is not True
        or gate.get("working_tree_only_code_cannot_authorize_network") is not True
    ):
        raise StageBError("public GDT620 publication gate differs")
    requests = profile.get("requests", [])
    if len(requests) != len(RESOURCES):
        raise StageBError("public GDT620 request count differs")
    for registered, resource in zip(requests, RESOURCES):
        if (
            registered.get("sequence") != resource.sequence
            or registered.get("candidate_id") != resource.candidate_id
            or registered.get("url") != resource.url
            or registered.get("resource_class") != resource.resource_class
            or registered.get("headers") != REQUEST_HEADERS
            or registered.get("expected_dimensions")
            != {"height": resource.expected_height, "width": resource.expected_width}
        ):
            raise StageBError("public GDT620 literal request deck differs")
    protocol = profile.get("protocol", {})
    fixed_delay = protocol.get("fixed_pre_request_delay")
    if (
        not isinstance(fixed_delay, dict)
        or set(fixed_delay)
        != {
            "seconds",
            "applies_to_sequences",
            "required_after_restart",
            "elapsed_wall_time_never_reduces_delay",
        }
        or type(fixed_delay.get("seconds")) is not float
        or fixed_delay.get("seconds") != MINIMUM_REQUEST_SPACING_SECONDS
        or fixed_delay.get("applies_to_sequences") != list(range(2, 11))
        or any(
            type(sequence) is not int
            for sequence in fixed_delay.get("applies_to_sequences", [])
        )
        or fixed_delay.get("required_after_restart") is not True
        or fixed_delay.get("elapsed_wall_time_never_reduces_delay") is not True
    ):
        raise StageBError("public GDT620 fixed pre-request delay differs")
    if (
        protocol.get("maximum_response_bytes_each") != RESPONSE_CAP_BYTES
        or protocol.get("maximum_response_bytes_total") != TOTAL_BODY_CAP_BYTES
        or protocol.get("socket_operation_timeout_seconds")
        != SOCKET_OPERATION_TIMEOUT_SECONDS
        or protocol.get("request_total_wall_seconds") != REQUEST_TOTAL_WALL_SECONDS
        or protocol.get("concurrency") != CONCURRENCY
        or protocol.get("follow_redirects") is not False
        or protocol.get("retries") != RETRIES
        or profile.get("output_contract", {}).get("success_status") != PASS_STATUS
    ):
        raise StageBError("public GDT620 protocol constants differ")


def validate_public_registration_commit(commit: str) -> dict[str, str]:
    """Bind execution to already-published GDT620 code and configuration."""

    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise StageBError("--public-registration-commit must be lowercase hex40")
    remote_ref = "refs/remotes/origin/main"
    remote = run_workspace_git(
        ["rev-parse", "--verify", "--quiet", remote_ref]
    )
    if remote.returncode != 0:
        raise StageBError("local origin/main reference is unavailable")
    ancestor = run_workspace_git(
        ["merge-base", "--is-ancestor", commit, remote_ref]
    )
    if ancestor.returncode != 0:
        raise StageBError("registration commit is not an ancestor of origin/main")

    hashes: dict[str, str] = {}
    for relative_path in GDT620_REGISTERED_PATHS:
        committed = load_git_blob(commit, relative_path)
        runtime_path = ROOT / relative_path
        if not runtime_path.is_file() or runtime_path.is_symlink():
            raise StageBError("registered runtime path is absent or a symlink")
        runtime = runtime_path.read_bytes()
        if runtime != committed:
            raise StageBError("runtime bytes differ from the public registration blob")
        hashes[relative_path] = sha256_bytes(committed)

    profile_path = GDT620_REGISTERED_PATHS[2]
    profile = json.loads((ROOT / profile_path).read_text(encoding="utf-8"))
    validate_gdt620_registration_profile(profile)
    return hashes


def validate_public_stage1(data: bytes) -> dict[str, Any]:
    if sha256_bytes(data) != GDT619_STAGE1_SHA256:
        raise StageBError("public GDT619 Stage1 SHA-256 differs")
    stage1 = json.loads(data.decode("utf-8"))
    if (
        stage1.get("schema_version") != 1
        or stage1.get("status")
        != "STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND"
    ):
        raise StageBError("public GDT619 Stage1 identity/status differs")
    calibration = stage1.get("calibration", {})
    observed = [
        (row.get("scan"), row.get("observation"))
        for row in calibration.get("observations", [])
    ]
    if (
        calibration.get("branch") != "ADJACENT_SCAN_FALLBACK"
        or calibration.get("selected_global_delta") != -1
        or observed
        != [
            (26, "VISIBLY_ABSENT"),
            (25, "VISIBLE"),
            (27, "VISIBLY_ABSENT"),
        ]
    ):
        raise StageBError("public GDT619 Stage1 calibration differs")
    manifest = stage1.get("manifest", {})
    if (
        manifest.get("sha256") != GDT619_MANIFEST_SHA256
        or manifest.get("bytes") != 261_778
        or manifest.get("url")
        != "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest"
    ):
        raise StageBError("public GDT619 manifest binding differs")
    evidence = stage1.get("request_evidence", {})
    if (
        evidence.get("intent_count") != 5
        or evidence.get("success_count") != 4
        or evidence.get("failure_count") != 1
        or evidence.get("journal_sha256") != GDT619_STAGE1_JOURNAL_SHA256
        or float(evidence.get("minimum_bsb_spacing_seconds", 0.0))
        < MINIMUM_BSB_SPACING_SECONDS
    ):
        raise StageBError("public GDT619 request evidence differs")
    thumbnails = evidence.get("thumbnails", [])
    if not isinstance(thumbnails, list) or len(thumbnails) != 3:
        raise StageBError("public GDT619 thumbnail evidence differs")
    if thumbnails[-1].get("response_completed_utc") != GDT619_LAST_BSB_COMPLETED_UTC:
        raise StageBError("public GDT619 last BSB completion differs")

    expected = [
        ("DEV01", "f10v", 25, 1707, 2466),
        ("DEV02", "f35v", 75, 1707, 2581),
        ("DEV03", "f80r", 164, 1707, 2562),
        ("DEV04", "f46r", 96, 1707, 2591),
        ("DEV05", "f48v", 101, 1707, 2581),
    ]
    pages = stage1.get("selected_pages", [])
    if not isinstance(pages, list) or len(pages) != len(expected):
        raise StageBError("public GDT619 selected-page count differs")
    for row, expected_row, resource in zip(pages, expected, RESOURCES[:5]):
        candidate, folio, ordinal, width, height = expected_row
        body = row.get("body", {})
        service_id = (
            "https://api.digitale-sammlungen.de/iiif/image/v3/"
            f"bsb00107549_{ordinal:05d}"
        )
        expected_service = {
            "id": service_id,
            "profile": "level2",
            "type": "ImageService3",
        }
        if (
            row.get("candidate_id") != candidate
            or row.get("folio") != folio
            or row.get("canvas_ordinal") != ordinal
            or row.get("canvas_id")
            != (
                "https://api.digitale-sammlungen.de/iiif/presentation/v3/"
                f"bsb00107549/canvas/{ordinal}"
            )
            or body.get("id") != resource.url
            or row.get("stage_b_url") != resource.url
            or body.get("width") != width
            or body.get("height") != height
            or body.get("type") != "Image"
            or body.get("format") != "image/jpeg"
            or body.get("service") != [expected_service]
        ):
            raise StageBError("public GDT619 selected-page binding differs")
    return stage1


def validate_public_profile(data: bytes) -> dict[str, Any]:
    if sha256_bytes(data) != GDT619_PROFILE_SHA256:
        raise StageBError("public GDT619 profile SHA-256 differs")
    profile = json.loads(data.decode("utf-8"))
    stage_b = profile.get("stage_b", {})
    expected_urls = [resource.url for resource in RESOURCES[5:]]
    if stage_b.get("gallica_native_pages", {}).get("urls") != expected_urls:
        raise StageBError("public GDT619 Gallica URL order differs")
    candidates = profile.get("candidates", [])
    expected = [
        ("DEV01", 3302, 4581),
        ("DEV02", 3451, 4553),
        ("DEV03", 3284, 4557),
        ("DEV04", 3333, 4388),
        ("DEV05", 3346, 4574),
    ]
    if len(candidates) != len(expected):
        raise StageBError("public GDT619 candidate count differs")
    for row, (candidate, width, height), resource in zip(
        candidates, expected, RESOURCES[5:]
    ):
        lat = row.get("lat6823", {})
        size = lat.get("canvas_size", {})
        if (
            row.get("candidate_id") != candidate
            or lat.get("native_image_url") != resource.url
            or size != {"height": height, "width": width}
        ):
            raise StageBError("public GDT619 Gallica page binding differs")
    if stage_b.get("access_order") != [
        "BSB_CLM28531_DEV01",
        "BSB_CLM28531_DEV02",
        "BSB_CLM28531_DEV03",
        "BSB_CLM28531_DEV04",
        "BSB_CLM28531_DEV05",
        "BNF_LAT6823_DEV01",
        "BNF_LAT6823_DEV02",
        "BNF_LAT6823_DEV03",
        "BNF_LAT6823_DEV04",
        "BNF_LAT6823_DEV05",
    ]:
        raise StageBError("public GDT619 Stage-B access order differs")
    return profile


def load_and_validate_public_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    stage1 = validate_public_stage1(
        load_git_blob(PUBLIC_GDT619_COMMIT, GDT619_STAGE1_RELATIVE_PATH)
    )
    profile = validate_public_profile(
        load_git_blob(PUBLIC_GDT619_COMMIT, GDT619_PROFILE_RELATIVE_PATH)
    )
    if PILLOW_VERSION != PILLOW_REQUIRED_VERSION:
        raise StageBError(
            f"Pillow runtime must be exactly {PILLOW_REQUIRED_VERSION}"
        )
    return stage1, profile


def state_path(private_dir: Path) -> Path:
    return private_dir / STATE_FILENAME


def initial_state(public_registration_commit: str) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "gdt619_profile_sha256": GDT619_PROFILE_SHA256,
        "gdt619_stage1_commit": PUBLIC_GDT619_COMMIT,
        "gdt619_stage1_sha256": GDT619_STAGE1_SHA256,
        "gdt620_public_registration_commit": public_registration_commit,
        "next_index": 0,
        "request_sequence": 0,
        "schema_version": SCHEMA_VERSION,
        "sealed_data": SEALED_DATA,
        "second_execution_state_directory_forbidden_by_policy": True,
        "status": "READY_FOR_NEXT_REQUEST",
        "successful_requests": [],
        "target_opened": False,
        "unresolved_attempt": None,
    }


def save_state(private_dir: Path, state: dict[str, Any]) -> None:
    private_write(state_path(private_dir), canonical_bytes(state), replace=True)


def validate_saved_successes(private_dir: Path, state: dict[str, Any]) -> None:
    next_index = state.get("next_index")
    successes = state.get("successful_requests")
    if not isinstance(next_index, int) or not 0 <= next_index <= len(RESOURCES):
        raise StageBError("private state next_index differs")
    if not isinstance(successes, list) or len(successes) != next_index:
        raise StageBError("private state success count differs")
    for resource, success in zip(RESOURCES[:next_index], successes):
        path = private_dir / resource.filename
        validate_private_file(path)
        data = path.read_bytes()
        if (
            success.get("SEQUENCE") != resource.sequence
            or success.get("REQUEST_URL") != resource.url
            or success.get("RAW_SHA256") != sha256_bytes(data)
            or success.get("OBSERVED_BYTES") != len(data)
            or success.get("DECODED_WIDTH") != resource.expected_width
            or success.get("DECODED_HEIGHT") != resource.expected_height
        ):
            raise StageBError("saved response differs from private state")


def validate_journal_state(private_dir: Path, state: dict[str, Any]) -> None:
    rows = journal_rows(private_dir)
    intents = [row for row in rows if row.get("EVENT") == "REQUEST_INTENT"]
    successes = [row for row in rows if row.get("EVENT") == "REQUEST_SUCCESS"]
    failures = [row for row in rows if row.get("EVENT") == "REQUEST_FAILURE"]
    intent_urls = [row.get("REQUEST_URL") for row in intents]
    success_urls = [row.get("REQUEST_URL") for row in successes]
    if intent_urls != [resource.url for resource in RESOURCES[: len(intents)]]:
        raise StageBError("journal intent order differs from the exact deck")
    if success_urls != [resource.url for resource in RESOURCES[: len(successes)]]:
        raise StageBError("journal success order differs from the exact deck")
    if len({row.get("REQUEST_URL") for row in intents}) != len(intents):
        raise UnresolvedAttemptError("duplicate request intent permanently forbids resend")
    next_index = state["next_index"]
    unresolved = state.get("unresolved_attempt")
    status = state.get("status")
    if unresolved is not None or status in {"IN_FLIGHT", "STOPPED_FAILURE"}:
        raise UnresolvedAttemptError(
            "unresolved or failed request intent permanently forbids resend"
        )
    if failures:
        raise UnresolvedAttemptError("failed request intent permanently forbids resend")
    if len(intents) != next_index or len(successes) != next_index:
        raise UnresolvedAttemptError("journal contains an unresolved request intent")
    if successes != state.get("successful_requests"):
        raise StageBError("private state successes differ from append-only journal")
    for intent, success in zip(intents, successes):
        if (
            intent.get("SEQUENCE") != success.get("SEQUENCE")
            or intent.get("REQUEST_URL") != success.get("REQUEST_URL")
            or intent.get("REQUEST_URL_SHA256") != success.get("REQUEST_URL_SHA256")
            or intent.get("INTENT_WRITTEN_UTC") != success.get("INTENT_WRITTEN_UTC")
        ):
            raise StageBError("journal intent/success linkage differs")
    if state.get("request_sequence") != next_index:
        raise StageBError("private state request sequence differs")


def load_or_create_state(
    private_dir: Path, public_registration_commit: str
) -> dict[str, Any]:
    path = state_path(private_dir)
    if not path.exists():
        if (private_dir / JOURNAL_FILENAME).exists() or any(
            (private_dir / resource.filename).exists() for resource in RESOURCES
        ):
            raise UnresolvedAttemptError("response or journal exists without durable state")
        state = initial_state(public_registration_commit)
        private_write(path, canonical_bytes(state), replace=False)
        return state
    validate_private_file(path)
    state = json.loads(path.read_text(encoding="utf-8"))
    if (
        state.get("schema_version") != SCHEMA_VERSION
        or state.get("experiment_id") != EXPERIMENT_ID
        or state.get("gdt619_stage1_commit") != PUBLIC_GDT619_COMMIT
        or state.get("gdt619_stage1_sha256") != GDT619_STAGE1_SHA256
        or state.get("gdt619_profile_sha256") != GDT619_PROFILE_SHA256
        or state.get("gdt620_public_registration_commit")
        != public_registration_commit
        or state.get("sealed_data") != SEALED_DATA
        or state.get("second_execution_state_directory_forbidden_by_policy")
        is not True
        or state.get("target_opened") is not False
    ):
        raise StageBError("private state identity or sealed-data boundary differs")
    next_index = state.get("next_index")
    status = state.get("status")
    if status not in {
        "READY_FOR_NEXT_REQUEST",
        "ACQUIRED_ALL_AWAITING_RESULT_DRAFT",
        "COMPLETE",
        "IN_FLIGHT",
        "STOPPED_FAILURE",
    }:
        raise StageBError("private state status differs")
    ready_relation_bad = status == "READY_FOR_NEXT_REQUEST" and (
        not isinstance(next_index, int)
        or not 0 <= next_index < len(RESOURCES)
    )
    terminal_relation_bad = (
        status in {"ACQUIRED_ALL_AWAITING_RESULT_DRAFT", "COMPLETE"}
        and next_index != len(RESOURCES)
    )
    if ready_relation_bad or terminal_relation_bad:
        raise StageBError("private state status/sequence relation differs")
    validate_saved_successes(private_dir, state)
    validate_journal_state(private_dir, state)
    return state


def base_journal_row(
    resource: Resource,
    *,
    intent_written_utc: str,
    defined_delay_seconds: float,
) -> dict[str, Any]:
    row = {field: None for field in REGISTERED_LOG_FIELDS}
    row.update(
        {
            "CANDIDATE_ID": resource.candidate_id,
            "DEFINED_DELAY_SECONDS": defined_delay_seconds,
            "METHOD": HTTP_METHOD,
            "REQUEST_HEADERS": REQUEST_HEADERS,
            "REQUEST_URL": resource.url,
            "REQUEST_URL_SHA256": sha256_bytes(resource.url.encode("utf-8")),
            "RESOURCE_CLASS": resource.resource_class,
            "SEQUENCE": resource.sequence,
            "STAGE": "STAGE_B",
            "SOCKET_OPERATION_TIMEOUT_SECONDS": SOCKET_OPERATION_TIMEOUT_SECONDS,
            "TOTAL_WALL_DEADLINE_SECONDS": REQUEST_TOTAL_WALL_SECONDS,
        }
    )
    row["INTENT_WRITTEN_UTC"] = intent_written_utc
    return row


def observed_wall_seconds_since_previous_completion(
    state: dict[str, Any], request_started_utc: str
) -> float | None:
    """Measure logged wall-clock spacing; never use it as a request gate.

    A wall-clock correction may make this observation negative.  The separate
    ``DEFINED_DELAY_SECONDS`` field records the guaranteed pre-request sleep.
    """

    successes = state.get("successful_requests", [])
    if not successes:
        return None
    previous_completed_utc = successes[-1].get("RESPONSE_COMPLETED_UTC")
    if not isinstance(previous_completed_utc, str):
        raise StageBError("previous success lacks a completion timestamp")
    return parse_utc(request_started_utc) - parse_utc(previous_completed_utc)


def fixed_pre_request_pause(resource: Resource, clock: Clock) -> float:
    """Sleep a full four seconds immediately before every non-first GET.

    This deliberately does not subtract elapsed wall time.  A resumed pass
    therefore sleeps four fresh seconds, and wall-clock jumps cannot shorten
    the registered delay.
    """

    if resource.sequence == 1:
        return 0.0
    clock.sleep(MINIMUM_REQUEST_SPACING_SECONDS)
    return MINIMUM_REQUEST_SPACING_SECONDS


def safe_header_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if len(text) > 1024 or "\r" in text or "\n" in text:
        raise AcquisitionFailure("INVALID_RESPONSE_HEADER", "unsafe response header")
    return text


def header_values(headers: Any, name: str) -> list[str]:
    if headers is None:
        return []
    get_all = getattr(headers, "get_all", None)
    if get_all is not None:
        values = get_all(name) or []
        return [value for item in values if (value := safe_header_value(item)) is not None]
    getter = getattr(headers, "get", None)
    if getter is None:
        return []
    value = getter(name)
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [item for raw in value if (item := safe_header_value(raw)) is not None]
    safe = safe_header_value(value)
    return [] if safe is None else [safe]


def single_header_value(headers: Any, name: str) -> str | None:
    values = header_values(headers, name)
    if len(values) > 1:
        raise AcquisitionFailure(
            "DUPLICATE_RESPONSE_HEADER", f"multiple {name} fields are forbidden"
        )
    return values[0] if values else None


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    previous_truncated_setting = ImageFile.LOAD_TRUNCATED_IMAGES
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as probe:
                if probe.format != "JPEG":
                    raise ValueError("decoded format is not JPEG")
                if getattr(probe, "n_frames", 1) != 1:
                    raise ValueError("JPEG must contain exactly one frame")
                # These are stored pixel dimensions.  EXIF orientation is
                # deliberately neither read nor applied.
                width, height = probe.size
                probe.verify()
            with Image.open(io.BytesIO(data)) as decoded:
                if decoded.format != "JPEG":
                    raise ValueError("reopened format is not JPEG")
                if getattr(decoded, "n_frames", 1) != 1:
                    raise ValueError("reopened JPEG must contain one frame")
                decoded.load()
    except Exception as exc:
        raise AcquisitionFailure(
            "DECODE_FAILURE", "full Pillow JPEG verify/load failed"
        ) from exc
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = previous_truncated_setting
    return width, height


def response_context(response: Any) -> dict[str, Any]:
    status = getattr(response, "status", None)
    if status is None and hasattr(response, "getcode"):
        status = response.getcode()
    final_url = response.geturl() if hasattr(response, "geturl") else None
    headers = getattr(response, "headers", None)
    content_length_values = header_values(headers, "Content-Length")
    if len(content_length_values) > 1:
        raise AcquisitionFailure(
            "DUPLICATE_RESPONSE_HEADER",
            "multiple Content-Length fields are forbidden",
        )
    return {
        "HTTP_STATUS": status,
        "RESPONSE_URL": final_url,
        "REDIRECT_ATTEMPTS": int(getattr(response, "redirect_attempts", 0)),
        "CONTENT_TYPE": single_header_value(headers, "Content-Type"),
        "CONTENT_LENGTH_HEADER": (
            content_length_values[0] if content_length_values else None
        ),
        "CONTENT_ENCODING": single_header_value(headers, "Content-Encoding"),
        "TRANSFER_ENCODING": single_header_value(headers, "Transfer-Encoding"),
        "ETAG": single_header_value(headers, "ETag"),
        "LAST_MODIFIED": single_header_value(headers, "Last-Modified"),
        "OBSERVED_BYTES": None,
        "RAW_SHA256": None,
        "DECODED_WIDTH": None,
        "DECODED_HEIGHT": None,
}


def enforce_total_wall_deadline(
    clock: Clock | None,
    deadline_monotonic: float | None,
    context: dict[str, Any],
) -> None:
    if (
        clock is not None
        and deadline_monotonic is not None
        and clock.monotonic() > deadline_monotonic
    ):
        raise AcquisitionFailure(
            "TOTAL_WALL_TIMEOUT",
            "request exceeded the registered 180-second total wall deadline",
            context=context,
        )


def consume_response(
    response: Any,
    resource: Resource,
    *,
    cap_bytes: int = RESPONSE_CAP_BYTES,
    clock: Clock | None = None,
    deadline_monotonic: float | None = None,
) -> tuple[bytes, dict[str, Any]]:
    context = response_context(response)
    enforce_total_wall_deadline(clock, deadline_monotonic, context)
    if context["HTTP_STATUS"] != 200:
        raise AcquisitionFailure(
            "HTTP_STATUS_FAILURE", "response status is not HTTP 200", context=context
        )
    if context["REDIRECT_ATTEMPTS"] != 0:
        raise AcquisitionFailure(
            "REDIRECT_FAILURE", "response records a redirect attempt", context=context
        )
    if context["RESPONSE_URL"] != resource.url:
        raise AcquisitionFailure(
            "FINAL_URL_MISMATCH", "final response URL differs", context=context
        )
    media_type = (context["CONTENT_TYPE"] or "").split(";", 1)[0].strip().lower()
    if media_type != "image/jpeg":
        raise AcquisitionFailure(
            "WRONG_MEDIA_TYPE", "response media type is not image/jpeg", context=context
        )

    content_encoding = (context["CONTENT_ENCODING"] or "").strip().lower()
    if content_encoding not in {"", "identity"}:
        raise AcquisitionFailure(
            "CONTENT_ENCODING_FAILURE",
            "Content-Encoding must be absent or identity",
            context=context,
        )
    transfer_encoding = (context["TRANSFER_ENCODING"] or "").strip().lower()
    if transfer_encoding not in {"", "chunked"}:
        raise AcquisitionFailure(
            "TRANSFER_ENCODING_FAILURE",
            "Transfer-Encoding must be absent or exactly chunked",
            context=context,
        )
    if transfer_encoding == "chunked" and context["CONTENT_LENGTH_HEADER"] is not None:
        raise AcquisitionFailure(
            "TRANSFER_LENGTH_CONFLICT",
            "chunked Transfer-Encoding forbids Content-Length",
            context=context,
        )

    content_length: int | None = None
    raw_content_length = context["CONTENT_LENGTH_HEADER"]
    if raw_content_length is not None:
        if not raw_content_length.isdigit():
            raise AcquisitionFailure(
                "INVALID_CONTENT_LENGTH",
                "Content-Length is not a nonnegative integer",
                context=context,
            )
        content_length = int(raw_content_length)
        if content_length > cap_bytes:
            context["OBSERVED_BYTES"] = 0
            raise AcquisitionFailure(
                "RESPONSE_CAP_EXCEEDED",
                "Content-Length exceeds the registered per-response cap",
                context=context,
            )

    chunks: list[bytes] = []
    observed = 0
    digest = hashlib.sha256()
    try:
        while True:
            enforce_total_wall_deadline(clock, deadline_monotonic, context)
            remaining = cap_bytes + 1 - observed
            if remaining <= 0:
                break
            chunk = response.read(min(STREAM_CHUNK_BYTES, remaining))
            enforce_total_wall_deadline(clock, deadline_monotonic, context)
            if not chunk:
                break
            if not isinstance(chunk, bytes):
                raise TypeError("response.read() did not return bytes")
            chunks.append(chunk)
            digest.update(chunk)
            observed += len(chunk)
            if observed > cap_bytes:
                context["OBSERVED_BYTES"] = observed
                context["RAW_SHA256"] = digest.hexdigest()
                raise AcquisitionFailure(
                    "RESPONSE_CAP_EXCEEDED",
                    "streamed response exceeds the registered per-response cap",
                    context=context,
                )
    except AcquisitionFailure:
        raise
    except Exception as exc:
        context["OBSERVED_BYTES"] = observed
        context["RAW_SHA256"] = digest.hexdigest() if observed else None
        raise AcquisitionFailure(
            "PARTIAL_RESPONSE", "response stream ended with an error", context=context
        ) from exc

    data = b"".join(chunks)
    context["OBSERVED_BYTES"] = len(data)
    context["RAW_SHA256"] = sha256_bytes(data)
    if content_length is not None and len(data) != content_length:
        raise AcquisitionFailure(
            "PARTIAL_RESPONSE",
            "observed bytes differ from Content-Length",
            context=context,
        )
    try:
        enforce_total_wall_deadline(clock, deadline_monotonic, context)
        width, height = jpeg_dimensions(data)
        enforce_total_wall_deadline(clock, deadline_monotonic, context)
    except AcquisitionFailure as exc:
        exc.context = context
        raise
    context["DECODED_WIDTH"] = width
    context["DECODED_HEIGHT"] = height
    if (width, height) != (resource.expected_width, resource.expected_height):
        raise AcquisitionFailure(
            "DIMENSION_MISMATCH",
            "decoded dimensions differ from the public Stage-B binding",
            context=context,
        )
    return data, context


def transport_failure(exc: Exception, resource: Resource) -> AcquisitionFailure:
    if isinstance(exc, AcquisitionFailure):
        return exc
    if isinstance(exc, urllib.error.HTTPError):
        headers = exc.headers
        context = {
            "HTTP_STATUS": exc.code,
            "RESPONSE_URL": exc.geturl(),
            "REDIRECT_ATTEMPTS": 0,
            "CONTENT_TYPE": single_header_value(headers, "Content-Type"),
            "CONTENT_LENGTH_HEADER": single_header_value(headers, "Content-Length"),
            "CONTENT_ENCODING": single_header_value(headers, "Content-Encoding"),
            "TRANSFER_ENCODING": single_header_value(headers, "Transfer-Encoding"),
            "ETAG": single_header_value(headers, "ETag"),
            "LAST_MODIFIED": single_header_value(headers, "Last-Modified"),
            "OBSERVED_BYTES": 0,
            "RAW_SHA256": None,
            "DECODED_WIDTH": None,
            "DECODED_HEIGHT": None,
        }
        return AcquisitionFailure(
            "HTTP_STATUS_FAILURE", "transport returned a non-200 HTTP status", context=context
        )
    del resource
    return AcquisitionFailure(
        "TRANSPORT_FAILURE", f"transport failed: {type(exc).__name__}"
    )


def enforce_request_deck_and_caps(
    state: dict[str, Any], resource: Resource, rows: list[dict[str, Any]]
) -> None:
    next_index = state["next_index"]
    if next_index >= len(RESOURCES) or resource != RESOURCES[next_index]:
        raise StageBError("request does not match the next exact allowlisted resource")
    if resource.url not in EXACT_ALLOWLIST or resource.sequence != next_index + 1:
        raise StageBError("request URL or sequence is outside the exact Stage-B deck")
    intents = [row for row in rows if row.get("EVENT") == "REQUEST_INTENT"]
    if any(row.get("REQUEST_URL") == resource.url for row in intents):
        raise UnresolvedAttemptError("prior request intent permanently forbids resend")
    bsb_intents = sum(
        row.get("EVENT") == "REQUEST_INTENT"
        and row.get("RESOURCE_CLASS")
        == "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY"
        for row in rows
    )
    bnf_intents = sum(
        row.get("EVENT") == "REQUEST_INTENT"
        and row.get("RESOURCE_CLASS") == "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE"
        for row in rows
    )
    if len(intents) >= MAX_TOTAL_STAGE_B_REQUESTS:
        raise StageBError("Stage-B total request cap reached")
    if resource.provider == "BSB" and bsb_intents >= MAX_NEW_BSB_REQUESTS:
        raise StageBError("new BSB request cap reached")
    if resource.provider == "BNF" and bnf_intents >= MAX_NEW_BNF_REQUESTS:
        raise StageBError("new BnF request cap reached")
    observed_total = sum(
        int(row.get("OBSERVED_BYTES") or 0)
        for row in rows
        if row.get("EVENT") == "REQUEST_SUCCESS"
    )
    if observed_total < 0 or observed_total > TOTAL_BODY_CAP_BYTES:
        raise StageBError("Stage-B total body cap state differs")


def record_failure(
    private_dir: Path,
    state: dict[str, Any],
    base: dict[str, Any],
    failure: AcquisitionFailure,
    *,
    request_started_utc: str,
    response_completed_utc: str,
) -> None:
    context = failure.context
    row = dict(base)
    row.update(
        {
            "CONTENT_LENGTH_HEADER": context.get("CONTENT_LENGTH_HEADER"),
            "CONTENT_ENCODING": context.get("CONTENT_ENCODING"),
            "CONTENT_TYPE": context.get("CONTENT_TYPE"),
            "DECODED_HEIGHT": context.get("DECODED_HEIGHT"),
            "DECODED_WIDTH": context.get("DECODED_WIDTH"),
            "DETAIL": failure.detail,
            "ETAG": context.get("ETAG"),
            "EVENT": "REQUEST_FAILURE",
            "FAILURE_CODE": failure.code,
            "HTTP_STATUS": context.get("HTTP_STATUS"),
            "LAST_MODIFIED": context.get("LAST_MODIFIED"),
            "OBSERVED_BYTES": context.get("OBSERVED_BYTES"),
            "RAW_SHA256": context.get("RAW_SHA256"),
            "REDIRECT_ATTEMPTS": context.get("REDIRECT_ATTEMPTS"),
            "REQUEST_STARTED_UTC": request_started_utc,
            "RESPONSE_COMPLETED_UTC": response_completed_utc,
            "RESPONSE_URL": context.get("RESPONSE_URL"),
            "STATUS": "FAILURE",
            "TRANSFER_ENCODING": context.get("TRANSFER_ENCODING"),
        }
    )
    append_journal(private_dir, row)
    state["failure"] = {
        "code": failure.code,
        "detail": failure.detail,
        "recorded_utc": response_completed_utc,
        "sequence": base["SEQUENCE"],
        "url": base["REQUEST_URL"],
    }
    state["status"] = "STOPPED_FAILURE"
    # Deliberately retain unresolved_attempt.  The URL can never be resent.
    save_state(private_dir, state)


def acquire_next(
    private_dir: Path,
    state: dict[str, Any],
    *,
    transport: Transport,
    clock: Clock,
) -> None:
    if state.get("status") != "READY_FOR_NEXT_REQUEST":
        raise StageBError("private state is not ready for another request")
    resource = RESOURCES[state["next_index"]]
    rows = journal_rows(private_dir)
    enforce_request_deck_and_caps(state, resource, rows)
    delay = (
        0.0 if resource.sequence == 1 else MINIMUM_REQUEST_SPACING_SECONDS
    )
    intent_written_utc = utc_from_epoch(clock.time())
    base = base_journal_row(
        resource,
        intent_written_utc=intent_written_utc,
        defined_delay_seconds=delay,
    )
    intent = dict(base)
    intent.update(
        {
            "EVENT": "REQUEST_INTENT",
            "STATUS": "IN_FLIGHT",
        }
    )
    append_journal(private_dir, intent)
    state["request_sequence"] = resource.sequence
    state["status"] = "IN_FLIGHT"
    state["unresolved_attempt"] = {
        "intent_written_utc": intent_written_utc,
        "sequence": resource.sequence,
        "url": resource.url,
        "url_sha256": base["REQUEST_URL_SHA256"],
    }
    save_state(private_dir, state)

    prior_body_bytes = sum(
        int(row.get("OBSERVED_BYTES") or 0)
        for row in state["successful_requests"]
    )
    remaining_total_cap = TOTAL_BODY_CAP_BYTES - prior_body_bytes
    if remaining_total_cap <= 0:
        raise StageBError("Stage-B total body cap reached before request")
    request = urllib.request.Request(
        resource.url,
        headers=REQUEST_HEADERS,
        method=HTTP_METHOD,
    )
    observed_delay = fixed_pre_request_pause(resource, clock)
    if observed_delay != delay:
        raise StageBError("fixed pre-request delay differs")
    request_started_epoch = clock.time()
    request_started_utc = utc_from_epoch(request_started_epoch)
    # This is an honest wall-clock observation, not the fixed-delay gate.  It
    # may be negative if the system clock moves backwards.
    base["SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"] = (
        observed_wall_seconds_since_previous_completion(
            state, request_started_utc
        )
    )
    deadline_monotonic = clock.monotonic() + REQUEST_TOTAL_WALL_SECONDS
    response: Any | None = None
    try:
        response = transport.open(
            request, timeout=SOCKET_OPERATION_TIMEOUT_SECONDS
        )
        data, context = consume_response(
            response,
            resource,
            cap_bytes=min(RESPONSE_CAP_BYTES, remaining_total_cap),
            clock=clock,
            deadline_monotonic=deadline_monotonic,
        )
        if prior_body_bytes + len(data) > TOTAL_BODY_CAP_BYTES:
            raise AcquisitionFailure(
                "TOTAL_BODY_CAP_EXCEEDED",
                "response would exceed the registered total-body cap",
                context=context,
            )
    except Exception as exc:
        failure = transport_failure(exc, resource)
        record_failure(
            private_dir,
            state,
            base,
            failure,
            request_started_utc=request_started_utc,
            response_completed_utc=utc_from_epoch(clock.time()),
        )
        raise failure
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                # The body has already reached EOF or a durable failure.  A
                # close-only exception cannot authorize a second request.
                pass

    response_completed_epoch = clock.time()
    response_completed_utc = utc_from_epoch(response_completed_epoch)
    private_write(private_dir / resource.filename, data, replace=False)
    saved = (private_dir / resource.filename).read_bytes()
    if len(saved) != len(data) or sha256_bytes(saved) != context["RAW_SHA256"]:
        raise StageBError("durable JPEG reread differs before success commit")
    success = dict(base)
    success.update(
        {
            "CONTENT_LENGTH_HEADER": context["CONTENT_LENGTH_HEADER"],
            "CONTENT_ENCODING": context["CONTENT_ENCODING"],
            "CONTENT_TYPE": context["CONTENT_TYPE"],
            "DECODED_HEIGHT": context["DECODED_HEIGHT"],
            "DECODED_WIDTH": context["DECODED_WIDTH"],
            "ETAG": context["ETAG"],
            "EVENT": "REQUEST_SUCCESS",
            "HTTP_STATUS": context["HTTP_STATUS"],
            "LAST_MODIFIED": context["LAST_MODIFIED"],
            "OBSERVED_BYTES": context["OBSERVED_BYTES"],
            "RAW_SHA256": context["RAW_SHA256"],
            "REDIRECT_ATTEMPTS": context["REDIRECT_ATTEMPTS"],
            "REQUEST_STARTED_UTC": request_started_utc,
            "RESPONSE_COMPLETED_UTC": response_completed_utc,
            "RESPONSE_URL": context["RESPONSE_URL"],
            "STATUS": "SUCCESS",
            "TRANSFER_ENCODING": context["TRANSFER_ENCODING"],
        }
    )
    append_journal(private_dir, success)
    state["successful_requests"].append(success)
    state["next_index"] += 1
    state["unresolved_attempt"] = None
    state["status"] = (
        "ACQUIRED_ALL_AWAITING_RESULT_DRAFT"
        if state["next_index"] == len(RESOURCES)
        else "READY_FOR_NEXT_REQUEST"
    )
    save_state(private_dir, state)


def public_result_from_state(state: dict[str, Any]) -> dict[str, Any]:
    successes = state["successful_requests"]
    if len(successes) != len(RESOURCES):
        raise StageBError("ten successes are required for the public result draft")
    pages = []
    for resource, row in zip(RESOURCES, successes):
        pages.append(
            {
                "candidate_id": resource.candidate_id,
                "content_encoding": row["CONTENT_ENCODING"],
                "content_length_header": row["CONTENT_LENGTH_HEADER"],
                "content_type": row["CONTENT_TYPE"],
                "decoded_height": row["DECODED_HEIGHT"],
                "decoded_width": row["DECODED_WIDTH"],
                "defined_delay_seconds": row["DEFINED_DELAY_SECONDS"],
                "etag": row["ETAG"],
                "headword": resource.headword,
                "last_modified": row["LAST_MODIFIED"],
                "observed_bytes": row["OBSERVED_BYTES"],
                "raw_sha256": row["RAW_SHA256"],
                "redirect_attempts": row["REDIRECT_ATTEMPTS"],
                "request_started_utc": row["REQUEST_STARTED_UTC"],
                "request_url": row["REQUEST_URL"],
                "request_url_sha256": row["REQUEST_URL_SHA256"],
                "resource_class": resource.resource_class,
                "response_headers": {
                    "content_encoding": row["CONTENT_ENCODING"],
                    "content_length": row["CONTENT_LENGTH_HEADER"],
                    "content_type": row["CONTENT_TYPE"],
                    "etag": row["ETAG"],
                    "last_modified": row["LAST_MODIFIED"],
                    "transfer_encoding": row["TRANSFER_ENCODING"],
                },
                "response_completed_utc": row["RESPONSE_COMPLETED_UTC"],
                "response_url": row["RESPONSE_URL"],
                "seconds_since_previous_request_completion": row[
                    "SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"
                ],
                "sequence": resource.sequence,
                "status": row["STATUS"],
                "transfer_encoding": row["TRANSFER_ENCODING"],
                "witness": resource.witness,
            }
        )
    return {
        "access_boundary": {
            "automatic_transcription": False,
            "local_crop_created": False,
            "network_crop_requests": 0,
            "source_text_read": False,
            "target_opened": False,
            "voynich_material_opened": False,
        },
        "experiment_id": EXPERIMENT_ID,
        "failure_count": 0,
        "gdt619_public_binding": {
            "commit": PUBLIC_GDT619_COMMIT,
            "profile_sha256": GDT619_PROFILE_SHA256,
            "stage1_artifact": GDT619_STAGE1_RELATIVE_PATH,
            "stage1_sha256": GDT619_STAGE1_SHA256,
        },
        "gdt620_public_registration": {
            "commit": state["gdt620_public_registration_commit"],
            "registered_runtime_paths": list(GDT620_REGISTERED_PATHS),
        },
        "literal_urls": [resource.url for resource in RESOURCES],
        "pages": pages,
        "request_order": [resource.sequence for resource in RESOURCES],
        "request_policy": {
            "accept_encoding": "identity",
            "concurrency": CONCURRENCY,
            "cumulative_bsb_cap": CUMULATIVE_BSB_REQUEST_CAP,
            "follow_redirects": FOLLOW_REDIRECTS,
            "http_method": HTTP_METHOD,
            "maximum_new_bnf_requests": MAX_NEW_BNF_REQUESTS,
            "maximum_new_bsb_requests": MAX_NEW_BSB_REQUESTS,
            "fixed_pre_request_delay": {
                "seconds": MINIMUM_REQUEST_SPACING_SECONDS,
                "applies_to_sequences": list(range(2, 11)),
                "required_after_restart": True,
                "elapsed_wall_time_never_reduces_delay": True,
            },
            "per_response_cap_bytes": RESPONSE_CAP_BYTES,
            "socket_operation_timeout_seconds": SOCKET_OPERATION_TIMEOUT_SECONDS,
            "request_total_wall_seconds": REQUEST_TOTAL_WALL_SECONDS,
            "total_body_cap_bytes": TOTAL_BODY_CAP_BYTES,
            "retries": RETRIES,
            "second_execution_state_directory_forbidden_by_policy": True,
            "stage_b_request_count": len(successes),
        },
        "schema_version": SCHEMA_VERSION,
        "sealed_data": SEALED_DATA,
        "status": PASS_STATUS,
    }


def validate_public_result(result: dict[str, Any]) -> None:
    boundary = result.get("access_boundary", {})
    if (
        result.get("schema_version") != SCHEMA_VERSION
        or result.get("experiment_id") != EXPERIMENT_ID
        or result.get("status") != PASS_STATUS
        or result.get("sealed_data") != SEALED_DATA
        or result.get("failure_count") != 0
        or result.get("request_order") != list(range(1, 11))
        or result.get("literal_urls") != [resource.url for resource in RESOURCES]
        or boundary.get("source_text_read") is not False
        or boundary.get("target_opened") is not False
        or boundary.get("voynich_material_opened") is not False
        or boundary.get("automatic_transcription") is not False
    ):
        raise StageBError("public result identity or claim ceiling differs")
    pages = result.get("pages", [])
    if len(pages) != len(RESOURCES):
        raise StageBError("public result does not contain exactly ten pages")
    if [row.get("request_url") for row in pages] != [
        resource.url for resource in RESOURCES
    ]:
        raise StageBError("public result URL order differs")
    for resource, row in zip(RESOURCES, pages):
        if (
            row.get("status") != "SUCCESS"
            or row.get("response_url") != resource.url
            or row.get("redirect_attempts") != 0
            or row.get("decoded_width") != resource.expected_width
            or row.get("decoded_height") != resource.expected_height
            or (row.get("content_encoding") or "").lower() not in {"", "identity"}
            or (row.get("transfer_encoding") or "").lower() not in {"", "chunked"}
            or (
                (row.get("transfer_encoding") or "").lower() == "chunked"
                and row.get("content_length_header") is not None
            )
            or not isinstance(row.get("raw_sha256"), str)
            or len(row["raw_sha256"]) != 64
        ):
            raise StageBError("public result page evidence differs")

    forbidden_private_names = {
        OWNER_MARKER_FILENAME,
        LOCK_FILENAME,
        STATE_FILENAME,
        JOURNAL_FILENAME,
        RESULT_DRAFT_FILENAME,
        *(resource.filename for resource in RESOURCES),
    }

    def strings(value: Any):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for key, child in value.items():
                yield str(key)
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)

    all_strings = list(strings(result))
    joined = "\n".join(all_strings)
    if any(name in joined for name in forbidden_private_names):
        raise StageBError("public result leaks a private filename")
    private_root_prefixes = tuple(
        os.sep + component + os.sep
        for component in ("home", "tmp", "Users")
    )
    if any(text.startswith(private_root_prefixes) for text in all_strings):
        raise StageBError("public result leaks an absolute private path")


def revalidate_all_saved_jpegs(private_dir: Path, state: dict[str, Any]) -> None:
    """Reread, rehash, fully decode, and dimension-check all ten files."""

    successes = state.get("successful_requests", [])
    if len(successes) != len(RESOURCES) or state.get("unresolved_attempt") is not None:
        raise StageBError("result finalization requires ten resolved successes")
    total = 0
    for resource, row in zip(RESOURCES, successes):
        path = private_dir / resource.filename
        validate_private_file(path)
        data = path.read_bytes()
        total += len(data)
        if total > TOTAL_BODY_CAP_BYTES:
            raise StageBError("saved JPEGs exceed the registered total-body cap")
        if (
            len(data) != row.get("OBSERVED_BYTES")
            or sha256_bytes(data) != row.get("RAW_SHA256")
        ):
            raise StageBError("saved JPEG byte count or raw hash differs")
        width, height = jpeg_dimensions(data)
        if (
            width != resource.expected_width
            or height != resource.expected_height
            or width != row.get("DECODED_WIDTH")
            or height != row.get("DECODED_HEIGHT")
        ):
            raise StageBError("saved JPEG dimensions differ during final reread")


def finalize_result(private_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    revalidate_all_saved_jpegs(private_dir, state)
    result = public_result_from_state(state)
    validate_public_result(result)
    payload = canonical_bytes(result)
    path = private_dir / RESULT_DRAFT_FILENAME
    if path.exists():
        validate_private_file(path)
        if path.read_bytes() != payload:
            raise StageBError("existing result draft differs")
    else:
        private_write(path, payload, replace=False)
    state["result_draft_sha256"] = sha256_bytes(payload)
    state["status"] = "COMPLETE"
    save_state(private_dir, state)
    return result


def _run_acquisition_loop(
    raw_private_dir: str,
    *,
    public_registration_commit: str,
    transport: Transport,
    clock: Clock,
) -> dict[str, Any]:
    private_dir = require_private_dir(raw_private_dir, public_registration_commit)
    with PrivateRunLock(private_dir):
        state = load_or_create_state(private_dir, public_registration_commit)
        if state.get("status") == "COMPLETE":
            revalidate_all_saved_jpegs(private_dir, state)
            result = public_result_from_state(state)
            validate_public_result(result)
            return result
        while state["next_index"] < len(RESOURCES):
            acquire_next(
                private_dir,
                state,
                transport=transport,
                clock=clock,
            )
        return finalize_result(private_dir, state)


def acquire_all(
    raw_private_dir: str,
    *,
    public_registration_commit: str,
) -> dict[str, Any]:
    """Execute the public, commit-gated acquisition with the fixed runtime."""

    load_and_validate_public_inputs()
    validate_public_registration_commit(public_registration_commit)
    return _run_acquisition_loop(
        raw_private_dir,
        public_registration_commit=public_registration_commit,
        transport=UrllibTransport(),
        clock=SystemClock(),
    )


class FakeClock:
    def __init__(self, epoch: float) -> None:
        self.epoch = epoch
        self.sleeps: list[float] = []

    def time(self) -> float:
        return self.epoch

    def monotonic(self) -> float:
        return self.epoch

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise AssertionError("negative mock sleep")
        self.sleeps.append(seconds)
        self.epoch += seconds


class OversleepClock(FakeClock):
    """Offline clock whose requested four-second sleep advances five seconds."""

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise AssertionError("negative mock sleep")
        self.sleeps.append(seconds)
        self.epoch += seconds + 1.0


class MockResponse:
    def __init__(
        self,
        data: bytes,
        url: str,
        *,
        status: int = 200,
        headers: dict[str, str] | None = None,
        redirect_attempts: int = 0,
        read_error_after: int | None = None,
        on_close: Any = None,
    ) -> None:
        self.data = data
        self.url = url
        self.status = status
        self.headers = headers or {}
        self.redirect_attempts = redirect_attempts
        self.read_error_after = read_error_after
        self.offset = 0
        self.read_calls = 0
        self.closed = False
        self.on_close = on_close

    def geturl(self) -> str:
        return self.url

    def getcode(self) -> int:
        return self.status

    def read(self, count: int = -1) -> bytes:
        self.read_calls += 1
        if self.read_error_after is not None and self.offset >= self.read_error_after:
            raise OSError("mock partial stream")
        if count < 0:
            count = len(self.data) - self.offset
        end = min(len(self.data), self.offset + count)
        chunk = self.data[self.offset : end]
        self.offset = end
        return chunk

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            if self.on_close is not None:
                self.on_close()


class MockTransport:
    def __init__(self, payloads: dict[str, bytes]) -> None:
        self.payloads = payloads
        self.calls: list[str] = []
        self.active = 0
        self.maximum_active = 0

    def open(self, request: urllib.request.Request, timeout: int) -> MockResponse:
        if request.get_method() != HTTP_METHOD:
            raise AssertionError("mock observed a non-GET request")
        if timeout != SOCKET_OPERATION_TIMEOUT_SECONDS:
            raise AssertionError("mock observed the wrong timeout")
        observed_headers = {key.lower(): value for key, value in request.header_items()}
        expected_headers = {key.lower(): value for key, value in REQUEST_HEADERS.items()}
        if observed_headers != expected_headers:
            raise AssertionError("mock observed different request headers")
        url = request.full_url
        if url not in self.payloads:
            raise AssertionError("mock observed a URL outside the exact allowlist")
        self.calls.append(url)
        self.active += 1
        self.maximum_active = max(self.maximum_active, self.active)

        def closed() -> None:
            self.active -= 1

        data = self.payloads[url]
        return MockResponse(
            data,
            url,
            headers={
                "Content-Type": "image/jpeg",
                "Content-Length": str(len(data)),
                "ETag": f'"mock-{len(self.calls):02d}"',
                "Last-Modified": "Sat, 29 Aug 2026 00:00:00 GMT",
            },
            on_close=closed,
        )


class SimulatedCrash(BaseException):
    """Offline process-death surrogate deliberately outside Exception."""


class MockCrashTransport:
    """Guaranteed-offline transport that simulates death before a response."""

    def __init__(self) -> None:
        self.calls = 0

    def open(self, request: urllib.request.Request, timeout: int) -> Any:
        del request, timeout
        self.calls += 1
        raise SimulatedCrash()


def _acquire_all_core(
    raw_private_dir: str,
    *,
    public_registration_commit: str,
    transport: Transport,
    clock: Clock,
) -> dict[str, Any]:
    """Exercise the acquisition loop with an explicitly offline test runtime."""

    if type(transport) not in {MockTransport, MockCrashTransport} or type(clock) is not FakeClock:
        raise StageBError("offline self-test core requires exact internal mock types")
    return _run_acquisition_loop(
        raw_private_dir,
        public_registration_commit=public_registration_commit,
        transport=transport,
        clock=clock,
    )


def synthetic_jpeg(width: int, height: int, value: int) -> bytes:
    buffer = io.BytesIO()
    with Image.new("L", (width, height), color=value % 256) as image:
        image.save(buffer, format="JPEG", quality=25, optimize=True)
    return buffer.getvalue()


def expect_failure_code(
    response: MockResponse,
    resource: Resource,
    code: str,
    *,
    cap_bytes: int,
    clock: Clock | None = None,
    deadline_monotonic: float | None = None,
) -> AcquisitionFailure:
    try:
        consume_response(
            response,
            resource,
            cap_bytes=cap_bytes,
            clock=clock,
            deadline_monotonic=deadline_monotonic,
        )
    except AcquisitionFailure as exc:
        if exc.code != code:
            raise AssertionError(f"expected {code}, received {exc.code}") from exc
        return exc
    raise AssertionError(f"expected {code}, response passed")


def self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL"})
        if not condition:
            raise AssertionError(name)

    stage1, profile = load_and_validate_public_inputs()
    poisoned_git_values = {
        "GIT_DIR": str(ROOT / "adversarial-not-workspace-git"),
        "GIT_WORK_TREE": str(ROOT.parent / "adversarial-not-workspace-tree"),
        "GIT_OBJECT_DIRECTORY": str(ROOT / "adversarial-object-directory"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(
            ROOT / "adversarial-alternate-objects"
        ),
        "PATH": str(ROOT / "adversarial-binary-directory"),
    }
    prior_git_values = {
        key: os.environ.get(key) for key in poisoned_git_values
    }
    try:
        os.environ.update(poisoned_git_values)
        cleaned_environment = workspace_git_environment()
        poisoned_stage1, poisoned_profile = load_and_validate_public_inputs()
        bound_top = run_workspace_git(["rev-parse", "--show-toplevel"])
        bound_git_dir = run_workspace_git(["rev-parse", "--absolute-git-dir"])
    finally:
        for key, prior_value in prior_git_values.items():
            if prior_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prior_value
    check(
        "malicious_git_environment_cannot_redirect_workspace_binding",
        not any(key.startswith("GIT_") for key in cleaned_environment)
        and poisoned_stage1 == stage1
        and poisoned_profile == profile
        and bound_top.returncode == 0
        and Path(bound_top.stdout.decode("utf-8").strip()) == ROOT
        and bound_git_dir.returncode == 0
        and Path(bound_git_dir.stdout.decode("utf-8").strip())
        == WORKSPACE_GIT_DIR,
    )
    working_gdt620_profile = json.loads(
        (
            ROOT
            / "experiments/yolo/gdt620_stage_b_source_page_acquisition/"
            "artifacts/REGISTERED_STAGE_B_PROFILE.json"
        ).read_text(encoding="utf-8")
    )
    working_profile_compatible = True
    try:
        validate_gdt620_registration_profile(working_gdt620_profile)
    except StageBError:
        working_profile_compatible = False
    check(
        "working_gdt620_profile_registration_compatible_offline",
        working_profile_compatible,
    )
    incompatible_delay_profile = json.loads(json.dumps(working_gdt620_profile))
    incompatible_delay_profile["protocol"]["fixed_pre_request_delay"][
        "required_after_restart"
    ] = False
    incompatible_gate_profile = json.loads(json.dumps(working_gdt620_profile))
    incompatible_gate_profile["execution_publication_gate"][
        "network_forbidden_until_registration_commit_is_public"
    ] = False
    incompatible_profile_rejections = 0
    for incompatible_profile in (
        incompatible_delay_profile,
        incompatible_gate_profile,
    ):
        try:
            validate_gdt620_registration_profile(incompatible_profile)
        except StageBError:
            incompatible_profile_rejections += 1
    check(
        "fixed_delay_and_prepublication_network_gate_enforced_offline",
        incompatible_profile_rejections == 2,
    )
    check("public_stage1_commit_and_sha_exact", stage1["calibration"]["selected_global_delta"] == -1)
    check("public_profile_sha_and_gallica_urls_exact", profile["stage_b"]["gallica_native_pages"]["urls"] == [resource.url for resource in RESOURCES[5:]])
    check("working_gdt620_profile_deck_matches_acquirer", [(row["sequence"], row["url"], row["resource_class"], row["headers"], row["expected_dimensions"]) for row in working_gdt620_profile["requests"]] == [(resource.sequence, resource.url, resource.resource_class, REQUEST_HEADERS, {"height": resource.expected_height, "width": resource.expected_width}) for resource in RESOURCES])
    check("working_gdt620_publication_paths_match", tuple(working_gdt620_profile["execution_publication_gate"]["committed_paths_must_match_runtime_bytes"]) == GDT620_REGISTERED_PATHS)
    check("success_status_exact", working_gdt620_profile["output_contract"]["success_status"] == PASS_STATUS)
    check("timeout_public_constants_exact", SOCKET_OPERATION_TIMEOUT_SECONDS == 60 and REQUEST_TOTAL_WALL_SECONDS == REQUEST_TIMEOUT_SECONDS == 180)
    check("response_and_total_caps_exact", RESPONSE_CAP_BYTES == 50_000_000 and TOTAL_BODY_CAP_BYTES == 500_000_000)
    check("pillow_runtime_exact", PILLOW_VERSION == PILLOW_REQUIRED_VERSION == "10.2.0")
    check("exact_ten_url_allowlist", len(RESOURCES) == len(EXACT_ALLOWLIST) == 10)
    check("provider_caps_exact", sum(resource.provider == "BSB" for resource in RESOURCES) == MAX_NEW_BSB_REQUESTS == 5 and sum(resource.provider == "BNF" for resource in RESOURCES) == MAX_NEW_BNF_REQUESTS == 5)
    check("cumulative_bsb_cap_exact", PRIOR_STAGE_A_BSB_REQUESTS + MAX_NEW_BSB_REQUESTS == CUMULATIVE_BSB_REQUEST_CAP == 10)
    check("sealed_target_boundary", SEALED_DATA == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"} and not any("voynich" in resource.url.lower() or "f84" in resource.url.lower() for resource in RESOURCES))
    check("exact_request_headers_exclude_range_referer_conditionals", REQUEST_HEADERS == {"Accept": "image/jpeg", "Accept-Encoding": "identity", "User-Agent": "VManus-GDT620-stage-b-source-acquisition/1.0"} and not {"Range", "Referer", "Authorization", "Cookie", "If-None-Match", "If-Modified-Since"}.intersection(REQUEST_HEADERS))
    offline_transport = UrllibTransport()
    offline_opener = offline_transport._opener
    handler_names = {type(handler).__name__ for handler in offline_opener.handlers}
    check("environment_proxy_cookie_auth_handlers_disabled", offline_transport._proxy_handler.proxies == {} and "HTTPCookieProcessor" not in handler_names and "HTTPBasicAuthHandler" not in handler_names and "HTTPDigestAuthHandler" not in handler_names and offline_opener.addheaders == [])
    public_acquire_parameters = inspect.signature(acquire_all).parameters
    check(
        "public_acquire_api_has_no_transport_clock_or_gate_bypass",
        list(public_acquire_parameters) == [
            "raw_private_dir",
            "public_registration_commit",
        ]
        and public_acquire_parameters["raw_private_dir"].kind
        is inspect.Parameter.POSITIONAL_OR_KEYWORD
        and public_acquire_parameters["public_registration_commit"].kind
        is inspect.Parameter.KEYWORD_ONLY,
    )
    production_transport_refused_by_test_core = False
    try:
        _acquire_all_core(
            str(ROOT / "offline-test-must-not-create"),
            public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
            transport=offline_transport,
            clock=FakeClock(0.0),
        )
    except StageBError:
        production_transport_refused_by_test_core = True
    check(
        "offline_test_core_refuses_production_transport",
        production_transport_refused_by_test_core,
    )
    malformed_commit_refused = False
    try:
        validate_public_registration_commit("not-a-commit")
    except StageBError:
        malformed_commit_refused = True
    check("public_registration_commit_hex40_required", malformed_commit_refused)
    first_delay_clock = FakeClock(10_000.0)
    check(
        "first_request_has_no_fixed_pause",
        fixed_pre_request_pause(RESOURCES[0], first_delay_clock) == 0.0
        and first_delay_clock.sleeps == [],
    )
    restarted_clock_after_backward_jump = FakeClock(-10_000.0)
    check(
        "restart_and_wall_clock_jump_still_sleep_full_four",
        fixed_pre_request_pause(RESOURCES[1], restarted_clock_after_backward_jump)
        == MINIMUM_REQUEST_SPACING_SECONDS
        and restarted_clock_after_backward_jump.sleeps
        == [MINIMUM_REQUEST_SPACING_SECONDS],
    )

    first = RESOURCES[0]
    over_header = MockResponse(
        b"unread",
        first.url,
        headers={"Content-Type": "image/jpeg", "Content-Length": "9"},
    )
    expect_failure_code(over_header, first, "RESPONSE_CAP_EXCEEDED", cap_bytes=8)
    check("content_length_over_cap_stops_before_body", over_header.read_calls == 0)

    class DuplicateLengthHeaders(dict):
        def get_all(self, name: str):
            if name.lower() == "content-length":
                return ["1", "1"]
            value = self.get(name)
            return [] if value is None else [value]

    duplicate_length = MockResponse(
        b"x",
        first.url,
        headers=DuplicateLengthHeaders({"Content-Type": "image/jpeg"}),
    )
    expect_failure_code(
        duplicate_length, first, "DUPLICATE_RESPONSE_HEADER", cap_bytes=8
    )
    check("duplicate_content_length_stops_before_body", duplicate_length.read_calls == 0)

    over_stream = MockResponse(
        b"123456789",
        first.url,
        headers={"Content-Type": "image/jpeg"},
    )
    over_stream_failure = expect_failure_code(
        over_stream, first, "RESPONSE_CAP_EXCEEDED", cap_bytes=8
    )
    check("missing_content_length_uses_cap_plus_one", over_stream_failure.context.get("OBSERVED_BYTES") == 9)

    partial = MockResponse(
        b"abc",
        first.url,
        headers={"Content-Type": "image/jpeg", "Content-Length": "10"},
    )
    expect_failure_code(partial, first, "PARTIAL_RESPONSE", cap_bytes=20)
    check("short_content_length_is_partial_stop", partial.read_calls >= 1)

    encoded = MockResponse(
        b"unread",
        first.url,
        headers={
            "Content-Type": "image/jpeg",
            "Content-Encoding": "gzip",
        },
    )
    expect_failure_code(encoded, first, "CONTENT_ENCODING_FAILURE", cap_bytes=20)
    check("nonidentity_content_encoding_stops_before_body", encoded.read_calls == 0)

    transfer_conflict = MockResponse(
        b"unread",
        first.url,
        headers={
            "Content-Type": "image/jpeg",
            "Content-Length": "6",
            "Transfer-Encoding": "chunked",
        },
    )
    expect_failure_code(
        transfer_conflict, first, "TRANSFER_LENGTH_CONFLICT", cap_bytes=20
    )
    check("chunked_with_content_length_stops_before_body", transfer_conflict.read_calls == 0)

    deadline_clock = FakeClock(1_000.0)

    class DeadlineResponse(MockResponse):
        def read(self, count: int = -1) -> bytes:
            deadline_clock.epoch += REQUEST_TOTAL_WALL_SECONDS + 1
            return super().read(count)

    deadline_response = DeadlineResponse(
        b"x",
        first.url,
        headers={"Content-Type": "image/jpeg"},
    )
    expect_failure_code(
        deadline_response,
        first,
        "TOTAL_WALL_TIMEOUT",
        cap_bytes=20,
        clock=deadline_clock,
        deadline_monotonic=1_000.0 + REQUEST_TOTAL_WALL_SECONDS,
    )
    check("total_wall_deadline_stops_stream", deadline_response.read_calls == 1)

    truncated_jpeg = synthetic_jpeg(64, 64, 1)[:-20]
    truncated = MockResponse(
        truncated_jpeg,
        first.url,
        headers={
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(truncated_jpeg)),
        },
    )
    expect_failure_code(truncated, first, "DECODE_FAILURE", cap_bytes=1_000_000)
    check("truncated_jpeg_decode_stop", True)

    wrong_final = MockResponse(
        b"",
        first.url + "?changed=1",
        headers={"Content-Type": "image/jpeg", "Content-Length": "0"},
    )
    expect_failure_code(wrong_final, first, "FINAL_URL_MISMATCH", cap_bytes=8)
    check("wrong_final_url_stops_before_body", wrong_final.read_calls == 0)

    wrong_media = MockResponse(
        b"not-an-image",
        first.url,
        headers={"Content-Type": "text/html", "Content-Length": "12"},
    )
    expect_failure_code(wrong_media, first, "WRONG_MEDIA_TYPE", cap_bytes=20)
    check("wrong_media_stops_before_body", wrong_media.read_calls == 0)

    tiny = synthetic_jpeg(16, 16, 2)
    wrong_dimensions = MockResponse(
        tiny,
        first.url,
        headers={"Content-Type": "image/jpeg", "Content-Length": str(len(tiny))},
    )
    mismatch = expect_failure_code(
        wrong_dimensions, first, "DIMENSION_MISMATCH", cap_bytes=1_000_000
    )
    check("dimension_mismatch_after_full_decode", mismatch.context.get("DECODED_WIDTH") == 16 and mismatch.context.get("DECODED_HEIGHT") == 16)

    payloads = {
        resource.url: synthetic_jpeg(
            resource.expected_width, resource.expected_height, resource.sequence
        )
        for resource in RESOURCES
    }
    start_epoch = parse_utc(GDT619_LAST_BSB_COMPLETED_UTC) + 100.0
    with tempfile.TemporaryDirectory(prefix="gdt620-selftest-") as temporary_parent:
        class WrapperTransport:
            def __init__(self, wrapped: MockTransport) -> None:
                self.wrapped = wrapped

            def open(
                self, request: urllib.request.Request, timeout: int
            ) -> MockResponse:
                return self.wrapped.open(request, timeout)

        wrapped_mock = MockTransport(payloads)
        wrapper_private = Path(temporary_parent) / "wrapper-must-not-create"
        wrapper_refused = False
        try:
            _acquire_all_core(
                str(wrapper_private),
                public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
                transport=WrapperTransport(wrapped_mock),
                clock=FakeClock(start_epoch),
            )
        except StageBError:
            wrapper_refused = True
        check(
            "wrapper_transport_refused_before_private_state_or_request",
            wrapper_refused
            and not wrapper_private.exists()
            and wrapped_mock.calls == [],
        )

        oversleep_core_transport = MockTransport(payloads)
        oversleep_core_private = (
            Path(temporary_parent) / "oversleep-core-must-not-create"
        )
        oversleep_core_refused = False
        try:
            _acquire_all_core(
                str(oversleep_core_private),
                public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
                transport=oversleep_core_transport,
                clock=OversleepClock(start_epoch),
            )
        except StageBError:
            oversleep_core_refused = True
        check(
            "offline_test_core_requires_exact_fake_clock",
            oversleep_core_refused
            and not oversleep_core_private.exists()
            and oversleep_core_transport.calls == [],
        )

        class WrongMediaMockTransport:
            def __init__(self) -> None:
                self.calls = 0

            def open(
                self, request: urllib.request.Request, timeout: int
            ) -> MockResponse:
                if timeout != SOCKET_OPERATION_TIMEOUT_SECONDS:
                    raise AssertionError("wrong mock timeout")
                self.calls += 1
                return MockResponse(
                    b"x",
                    request.full_url,
                    headers={
                        "Content-Type": "text/plain",
                        "Content-Length": "1",
                    },
                )

        timing_private = require_private_dir(
            str(Path(temporary_parent) / "private-timing"),
            SELF_TEST_REGISTRATION_COMMIT,
        )
        timing_transport = MockTransport(payloads)
        with PrivateRunLock(timing_private):
            timing_state = load_or_create_state(
                timing_private, SELF_TEST_REGISTRATION_COMMIT
            )
            acquire_next(
                timing_private,
                timing_state,
                transport=timing_transport,
                clock=FakeClock(start_epoch),
            )
            first_completed_epoch = parse_utc(
                timing_state["successful_requests"][-1][
                    "RESPONSE_COMPLETED_UTC"
                ]
            )
            acquire_next(
                timing_private,
                timing_state,
                transport=timing_transport,
                clock=OversleepClock(first_completed_epoch),
            )
            second_completed_epoch = parse_utc(
                timing_state["successful_requests"][-1][
                    "RESPONSE_COMPLETED_UTC"
                ]
            )
            acquire_next(
                timing_private,
                timing_state,
                transport=timing_transport,
                clock=FakeClock(second_completed_epoch - 10.0),
            )
            third_completed_epoch = parse_utc(
                timing_state["successful_requests"][-1][
                    "RESPONSE_COMPLETED_UTC"
                ]
            )
            wrong_media_transport = WrongMediaMockTransport()
            timing_failure_code = None
            try:
                acquire_next(
                    timing_private,
                    timing_state,
                    transport=wrong_media_transport,
                    clock=OversleepClock(third_completed_epoch),
                )
            except AcquisitionFailure as exc:
                timing_failure_code = exc.code
        timing_rows = journal_rows(timing_private)
        timing_intents = [
            row for row in timing_rows if row.get("EVENT") == "REQUEST_INTENT"
        ]
        timing_successes = [
            row for row in timing_rows if row.get("EVENT") == "REQUEST_SUCCESS"
        ]
        timing_failures = [
            row for row in timing_rows if row.get("EVENT") == "REQUEST_FAILURE"
        ]
        check(
            "intent_wall_clock_observation_is_unset",
            len(timing_intents) == 4
            and all(
                row["SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"] is None
                for row in timing_intents
            ),
        )
        check(
            "oversleep_success_observes_five_but_guarantees_four",
            timing_successes[1][
                "SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"
            ]
            == 5.0
            == (
                parse_utc(timing_successes[1]["REQUEST_STARTED_UTC"])
                - parse_utc(timing_successes[0]["RESPONSE_COMPLETED_UTC"])
            )
            and timing_successes[1]["DEFINED_DELAY_SECONDS"] == 4.0,
        )
        check(
            "backward_wall_clock_observation_is_negative_and_not_a_gate",
            len(timing_successes) == 3
            and timing_successes[2][
                "SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"
            ]
            == -6.0
            == (
                parse_utc(timing_successes[2]["REQUEST_STARTED_UTC"])
                - parse_utc(timing_successes[1]["RESPONSE_COMPLETED_UTC"])
            )
            and timing_successes[2]["STATUS"] == "SUCCESS",
        )
        check(
            "failure_observes_actual_wall_spacing_separate_from_delay",
            timing_failure_code == "WRONG_MEDIA_TYPE"
            and wrong_media_transport.calls == 1
            and len(timing_failures) == 1
            and timing_failures[0][
                "SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"
            ]
            == 5.0
            == (
                parse_utc(timing_failures[0]["REQUEST_STARTED_UTC"])
                - parse_utc(timing_successes[2]["RESPONSE_COMPLETED_UTC"])
            )
            and timing_failures[0]["DEFINED_DELAY_SECONDS"] == 4.0,
        )

        private = Path(temporary_parent) / "private-pass"
        transport = MockTransport(payloads)
        fake_clock = FakeClock(start_epoch)
        result = _acquire_all_core(
            str(private),
            public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
            transport=transport,
            clock=fake_clock,
        )
        check("mock_transport_exact_order", transport.calls == [resource.url for resource in RESOURCES])
        check("mock_transport_concurrency_one", transport.maximum_active == CONCURRENCY == 1 and transport.active == 0)
        check("mock_success_result_status", result["status"] == PASS_STATUS and len(result["pages"]) == 10)
        check(
            "mock_result_fixed_pre_request_delay_exact",
            result["request_policy"]["fixed_pre_request_delay"]
            == {
                "seconds": 4.0,
                "applies_to_sequences": list(range(2, 11)),
                "required_after_restart": True,
                "elapsed_wall_time_never_reduces_delay": True,
            }
            and "minimum_seconds_between_previous_completion_and_next_start"
            not in result["request_policy"],
        )
        check("mock_fixed_pause_first_then_nine", result["pages"][0]["defined_delay_seconds"] == 0.0 and result["pages"][0]["seconds_since_previous_request_completion"] is None and all(row["defined_delay_seconds"] == MINIMUM_REQUEST_SPACING_SECONDS and row["seconds_since_previous_request_completion"] == MINIMUM_REQUEST_SPACING_SECONDS for row in result["pages"][1:]) and fake_clock.sleeps == [MINIMUM_REQUEST_SPACING_SECONDS] * 9)
        journal = journal_rows(private)
        check("journal_intent_and_success_rows", len(journal) == 20 and sum(row["EVENT"] == "REQUEST_INTENT" for row in journal) == 10 and sum(row["EVENT"] == "REQUEST_SUCCESS" for row in journal) == 10)
        check("journal_registered_fields_complete", all(set(REGISTERED_LOG_FIELDS).issubset(row) for row in journal))
        check(
            "full_pass_intents_have_no_wall_spacing_observation",
            all(
                row["SECONDS_SINCE_PREVIOUS_REQUEST_COMPLETION"] is None
                for row in journal
                if row["EVENT"] == "REQUEST_INTENT"
            ),
        )
        result_bytes = (private / RESULT_DRAFT_FILENAME).read_bytes()
        check("public_safe_result_has_no_private_path", str(private).encode("utf-8") not in result_bytes and OWNER_MARKER_FILENAME.encode("utf-8") not in result_bytes)
        check("private_modes_exact", stat.S_IMODE(private.stat().st_mode) == 0o700 and all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in private.iterdir()))

        crash_private = Path(temporary_parent) / "private-crash"
        crash_transport = MockCrashTransport()
        crashed = False
        try:
            _acquire_all_core(
                str(crash_private),
                public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
                transport=crash_transport,
                clock=FakeClock(start_epoch),
            )
        except SimulatedCrash:
            crashed = True
        check("simulated_crash_reached_transport_once", crashed and crash_transport.calls == 1)

        never_transport = MockTransport(payloads)
        refused = False
        try:
            _acquire_all_core(
                str(crash_private),
                public_registration_commit=SELF_TEST_REGISTRATION_COMMIT,
                transport=never_transport,
                clock=FakeClock(start_epoch + 10),
            )
        except UnresolvedAttemptError:
            refused = True
        check("crash_intent_permanently_refuses_resend", refused and never_transport.calls == [])
        crash_state = json.loads((crash_private / STATE_FILENAME).read_text(encoding="utf-8"))
        check("crash_state_durable_in_flight", crash_state["status"] == "IN_FLIGHT" and crash_state["unresolved_attempt"]["url"] == RESOURCES[0].url)

    return {
        "checks": checks,
        "decision": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "experiment_id": EXPERIMENT_ID,
        "network_requests": 0,
        "schema_version": SCHEMA_VERSION,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    acquire_parser = subparsers.add_parser(
        "acquire", help="execute the exact ten-request Stage-B deck"
    )
    acquire_parser.add_argument("--private-dir", required=True)
    acquire_parser.add_argument(
        "--public-registration-commit",
        required=True,
        help="published GDT620 registration commit already reachable from origin/main",
    )
    verify_parser = subparsers.add_parser(
        "verify-public-inputs", help="offline-check the bound GDT619 git objects"
    )
    verify_parser.add_argument("--public-registration-commit")
    subparsers.add_parser(
        "self-test", help="run transport, cap, ordering, and crash tests offline"
    )
    return parser


def sanitized_error(exc: Exception, private_dir: str | None) -> str:
    detail = str(exc)
    if private_dir:
        detail = detail.replace(private_dir, "<PRIVATE_DIR>")
    return f"{type(exc).__name__}: {detail}"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify-public-inputs":
            load_and_validate_public_inputs()
            registration_hashes = (
                validate_public_registration_commit(args.public_registration_commit)
                if args.public_registration_commit
                else None
            )
            print(
                json.dumps(
                    {
                        "decision": "PASS",
                        "gdt619_commit": PUBLIC_GDT619_COMMIT,
                        "gdt619_stage1_sha256": GDT619_STAGE1_SHA256,
                        "gdt620_registration_commit": args.public_registration_commit,
                        "network_requests": 0,
                        "registered_runtime_blob_hashes": registration_hashes,
                    },
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "self-test":
            result = self_test()
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["decision"] == "PASS" else 1
        if args.command == "acquire":
            result = acquire_all(
                args.private_dir,
                public_registration_commit=args.public_registration_commit,
            )
            print(
                json.dumps(
                    {
                        "result_draft_sha256": sha256_bytes(canonical_bytes(result)),
                        "status": result["status"],
                    },
                    sort_keys=True,
                )
            )
            return 0
        raise AssertionError("unreachable command")
    except Exception as exc:
        private_dir = getattr(args, "private_dir", None)
        print(sanitized_error(exc, private_dir), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
