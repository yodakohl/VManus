#!/usr/bin/env python3
"""Offline validator for the public GDT620 Stage-B acquisition result.

This validator reads public text artifacts and local Git objects only.  It
does not open an image and its guarded acquirer import cannot make a network
request or start a subprocess.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import math
import os
import re
import socket
import stat
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").is_dir():
            return candidate.resolve(strict=True)
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt620_stage_b_source_page_acquisition")
BASE = ROOT / BASE_REL
RESULT_REL = BASE_REL / "artifacts/STAGE_B_RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/STAGE_B_RESULT_VALIDATION.json"
REPORT_REL = BASE_REL / "STAGE_B_RESULT.md"
ACQUIRER_REL = BASE_REL / "src/acquire_stage_b.py"
VALIDATOR_REL = BASE_REL / "src/validate_result.py"
MANIFEST_REL = BASE_REL / "experiment.json"

RESULT_SHA256 = "f14976f54fd4ea0424ada9f23d19e7f02424beff739f5b4943dd3b0329ae378e"
RESULT_SIZE = 18_435
REGISTRATION_COMMIT = "61a253ce2756ad06a6c69c620e702500f5e640ef"
GDT619_COMMIT = "e82d73d6300f51c810ff131711ace31bb2610b69"
GDT619_PROFILE_SHA256 = "c577525c5045b2e59ba68741fd098c1d94f43f6d52ac4364683f4dd1e1064164"
GDT619_STAGE1_SHA256 = "95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422"
GDT619_STAGE1_REL = Path(
    "experiments/yolo/gdt619_five_source_page_acquisition/"
    "artifacts/STAGE1_RESOLUTION.json"
)
SUCCESS_STATUS = "TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED"
FAILURE_STATUS = "STAGE_B_RESULT_VALIDATION_FAILURE"
SEALED_DATA = {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IMAGE_SUFFIXES = {
    ".bmp",
    ".gif",
    ".jp2",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}

REGISTERED_PATHS = (
    str(BASE_REL / "METHOD.md"),
    str(BASE_REL / "PREREGISTRATION.md"),
    str(BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"),
    str(BASE_REL / "requirements.txt"),
    str(ACQUIRER_REL),
    str(BASE_REL / "src/validate.py"),
    str(MANIFEST_REL),
)
REGISTERED_BLOB_SHA256 = {
    str(BASE_REL / "METHOD.md"): "1b82913e8fb7e498d686ca21d091ebc3cdacf51a797b93cc200af16dc90bcd14",
    str(BASE_REL / "PREREGISTRATION.md"): "40831ba995a6eaf5fc30c6a94f2a97fa03484d44c2c1d84b34b083e2cb427595",
    str(BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"): "239aa320a964460105dee5b077ddc7a3490491e19863d7b7b47159f622d7acb0",
    str(BASE_REL / "requirements.txt"): "2ea4551718a5b6779227e26956103791b7d0a87aca1610fbd4566d5da80988e3",
    str(ACQUIRER_REL): "9d66ff28dad91390ed47dc72c58fc69f769f302f4a91c2612992008ea5a857a4",
    str(BASE_REL / "src/validate.py"): "de1d2cd7da532f6e2ff3f12b215705ef816cff1d3bfe85291872a612c242e821",
    str(MANIFEST_REL): "06c4f88b300c579cb1f1e4d27c9b6946b00ecf63df0962dea60d4fb88c5beeb9",
}


@dataclass(frozen=True)
class ExpectedPage:
    sequence: int
    candidate_id: str
    headword: str
    witness: str
    provider: str
    resource_class: str
    url: str
    width: int
    height: int
    observed_bytes: int
    raw_sha256: str
    request_url_sha256: str
    content_length: str | None
    transfer_encoding: str | None


EXPECTED_PAGES = (
    ExpectedPage(1, "DEV01", "Balsamus", "CLM28531", "BSB", "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/max/0/default.jpg", 1707, 2466, 654233, "82b476a028ad94ba7392520a4cba527c9dc521a577207bbec5842d0f7e266c50", "9d822e27e13a2946e25124a0efada92e8dc1af91ba150f33317551b9e839be25", "654233", None),
    ExpectedPage(2, "DEV02", "Cerfolium", "CLM28531", "BSB", "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00075/full/max/0/default.jpg", 1707, 2581, 590262, "e0c56b10b19e823c7b0247881d1cf27a1302cced0bd432956b98c47aab78746f", "46eb36c6d40120cbccd9fefb10cb2e4b8f52432b393838b09cb8edfa2606c7b6", "590262", None),
    ExpectedPage(3, "DEV03", "Liquiritia", "CLM28531", "BSB", "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00164/full/max/0/default.jpg", 1707, 2562, 616531, "4d87c0f033236b88abbb0ce6a5fe24a3664d63660080e15e0763642d9444aee0", "c28659fd4a398657ef3c51a318648971121f9dd1330b52aebdae79819291ea2f", "616531", None),
    ExpectedPage(4, "DEV04", "Cucurbita", "CLM28531", "BSB", "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00096/full/max/0/default.jpg", 1707, 2591, 562974, "f5a112fd194f45db72518e1a146f05bd2eec239e346a1b137cba7f1eab24e035", "fbe0467c25143f938d2b21937b66ad4231f5d9fb1717c12d929228f411b3dd0d", "562974", None),
    ExpectedPage(5, "DEV05", "Diptamus", "CLM28531", "BSB", "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00101/full/max/0/default.jpg", 1707, 2581, 481123, "808ff7b43c074ee0e67770cf51d7a38f683254c1a11883bf799bc9deeee1f4a8", "823ee249f9365d4ae461b859a7d83c6895fb0f4410b7e7a5c077ec381a5890c7", "481123", None),
    ExpectedPage(6, "DEV01", "Balsamus", "LAT6823", "BNF", "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f58/full/full/0/native.jpg", 3302, 4581, 2399224, "a12f51056ad4e18ae4ed40739987dae3924618787ebbaac1c481ac0b2976ef2a", "3fd3ec58599d4b50e7941d92f93d0e22c847b1565e2f533ffdab0c3f6f5c75c6", None, "chunked"),
    ExpectedPage(7, "DEV02", "Cerfolium", "LAT6823", "BNF", "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f96/full/full/0/native.jpg", 3451, 4553, 1815181, "470aca9b7d6cdfd9aa3cb321d165f86b01e15f8de8193e50d8a9dbb722c71b11", "a80d57a4d1779a19891ff25c79aae50b753a693fb6595f832f32988dfc88d76f", None, "chunked"),
    ExpectedPage(8, "DEV03", "Liquiritia", "LAT6823", "BNF", "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f178/full/full/0/native.jpg", 3284, 4557, 2242239, "01397d43449619b004fcee6fdacc3e236dfb3523f689ef0c51d0ff550f30b6b4", "783b5048ea107a259bac7d3860a2fb3493b696b6de25f650ecb1f4ef1976a77b", None, "chunked"),
    ExpectedPage(9, "DEV04", "Cucurbita", "LAT6823", "BNF", "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f91/full/full/0/native.jpg", 3333, 4388, 1896600, "055dd108bbec73ca7a8b80f9cfa3c467b3ca560ef9650015f05aaffd2e28ca8d", "9cc2a93a0c4459d3263791cb14ffc02a044a31c8a851eb76762c35f865862347", None, "chunked"),
    ExpectedPage(10, "DEV05", "Diptamus", "LAT6823", "BNF", "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f122/full/full/0/native.jpg", 3346, 4574, 1920542, "8091ac2ac1939ac11e88d314501c4ef68d0015e6c38b89ad08a07a30521e0a4a", "2abaea8c6b9b45c95201a13716a73ffeb4844929adb87684bdc112845a07f042", None, "chunked"),
)

TOP_LEVEL_KEYS = {
    "access_boundary",
    "experiment_id",
    "failure_count",
    "gdt619_public_binding",
    "gdt620_public_registration",
    "literal_urls",
    "pages",
    "request_order",
    "request_policy",
    "schema_version",
    "sealed_data",
    "status",
}
PAGE_KEYS = {
    "candidate_id", "content_encoding", "content_length_header", "content_type",
    "decoded_height", "decoded_width", "defined_delay_seconds", "etag", "headword",
    "last_modified", "observed_bytes", "raw_sha256", "redirect_attempts",
    "request_started_utc", "request_url", "request_url_sha256", "resource_class",
    "response_completed_utc", "response_headers", "response_url",
    "seconds_since_previous_request_completion", "sequence", "status",
    "transfer_encoding", "witness",
}
RESPONSE_HEADER_KEYS = {
    "content_encoding", "content_length", "content_type", "etag",
    "last_modified", "transfer_encoding",
}

EXPECTED_MANIFEST_OUTPUTS = {
    str(BASE_REL / "README.md"),
    str(BASE_REL / "METHOD.md"),
    str(BASE_REL / "PREREGISTRATION.md"),
    str(REPORT_REL),
    str(BASE_REL / "artifacts/README.md"),
    str(BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"),
    str(BASE_REL / "artifacts/REGISTERED_VALIDATION.json"),
    str(RESULT_REL),
    str(VALIDATION_REL),
    str(BASE_REL / "requirements.txt"),
    str(BASE_REL / "src/run.py"),
    str(ACQUIRER_REL),
    str(BASE_REL / "src/validate.py"),
    str(VALIDATOR_REL),
}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


class DuplicateJSONKey(ValueError):
    pass


def strict_json(data: bytes) -> Any:
    text = data.decode("utf-8", errors="strict")

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateJSONKey(key)
            result[key] = value
        return result

    return json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )


def safe_git_run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment.update(
        {
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    return subprocess.run(
        [
            "/usr/bin/git",
            f"--git-dir={ROOT / '.git'}",
            f"--work-tree={ROOT}",
            "-c",
            "core.hooksPath=/dev/null",
            *arguments,
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        timeout=30,
    )


def git_blob(commit: str, relative: str) -> bytes | None:
    completed = safe_git_run(["show", f"{commit}:{relative}"])
    return completed.stdout if completed.returncode == 0 else None


def registration_git_evidence() -> tuple[bool, bool, bool]:
    git_dir = ROOT / ".git"
    explicit_workspace = (
        git_dir.is_dir()
        and not git_dir.is_symlink()
        and git_dir.resolve(strict=True) == git_dir
    )
    ancestor = safe_git_run(
        ["merge-base", "--is-ancestor", REGISTRATION_COMMIT, "refs/remotes/origin/main"]
    ).returncode == 0
    tree = safe_git_run(
        ["ls-tree", "-z", REGISTRATION_COMMIT, "--", *REGISTERED_PATHS]
    )
    tree_rows: dict[str, tuple[str, str]] = {}
    if tree.returncode == 0:
        for raw in tree.stdout.split(b"\0"):
            if not raw:
                continue
            try:
                metadata, raw_path = raw.split(b"\t", 1)
                mode, kind, _object_id = metadata.decode("ascii").split(" ", 2)
                tree_rows[raw_path.decode("utf-8")] = (mode, kind)
            except (UnicodeDecodeError, ValueError):
                tree_rows = {}
                break
    blobs_exact = (
        tree_rows == {path: ("100644", "blob") for path in REGISTERED_PATHS}
        and all(
            (blob := git_blob(REGISTRATION_COMMIT, path)) is not None
            and digest_bytes(blob) == REGISTERED_BLOB_SHA256[path]
            for path in REGISTERED_PATHS
        )
    )
    return explicit_workspace, ancestor, blobs_exact


def hostile_git_environment_is_ignored() -> bool:
    previous_dir = os.environ.get("GIT_DIR")
    previous_tree = os.environ.get("GIT_WORK_TREE")
    try:
        os.environ["GIT_DIR"] = str(ROOT / "__nonexistent_adversarial_git_dir__")
        os.environ["GIT_WORK_TREE"] = str(ROOT.parent)
        blob = git_blob(REGISTRATION_COMMIT, str(ACQUIRER_REL))
        return blob is not None and digest_bytes(blob) == REGISTERED_BLOB_SHA256[str(ACQUIRER_REL)]
    finally:
        if previous_dir is None:
            os.environ.pop("GIT_DIR", None)
        else:
            os.environ["GIT_DIR"] = previous_dir
        if previous_tree is None:
            os.environ.pop("GIT_WORK_TREE", None)
        else:
            os.environ["GIT_WORK_TREE"] = previous_tree


class OfflineBoundaryViolation(RuntimeError):
    pass


@contextlib.contextmanager
def offline_import_guard() -> Iterator[list[str]]:
    from PIL import Image

    attempts: list[str] = []

    def deny(label: str):
        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            attempts.append(label)
            raise OfflineBoundaryViolation(label)

        return blocked

    patches = (
        (socket, "create_connection", deny("socket.create_connection")),
        (socket, "getaddrinfo", deny("socket.getaddrinfo")),
        (socket.socket, "connect", deny("socket.socket.connect")),
        (socket.socket, "connect_ex", deny("socket.socket.connect_ex")),
        (socket.socket, "sendto", deny("socket.socket.sendto")),
        (urllib.request, "urlopen", deny("urllib.request.urlopen")),
        (urllib.request.OpenerDirector, "open", deny("urllib.request.OpenerDirector.open")),
        (subprocess, "Popen", deny("subprocess.Popen")),
        (subprocess, "run", deny("subprocess.run")),
        (Image, "open", deny("PIL.Image.open")),
    )
    originals: list[tuple[Any, str, Any]] = []
    for owner, name, replacement in patches:
        originals.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)
    try:
        yield attempts
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def guarded_acquirer_validation(result: dict[str, Any]) -> tuple[bool, bool]:
    module_name = "gdt620_result_validation_acquirer"
    sys.dont_write_bytecode = True
    before = {
        path.relative_to(BASE).as_posix()
        for path in BASE.rglob("*")
        if path.is_file()
    }
    attempts: list[str] = []
    module: Any = None
    try:
        with offline_import_guard() as attempts:
            spec = importlib.util.spec_from_file_location(module_name, ROOT / ACQUIRER_REL)
            if spec is None or spec.loader is None:
                raise RuntimeError("cannot load GDT620 acquirer")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            module.validate_public_result(result)
    except Exception:
        return False, attempts == []
    finally:
        sys.modules.pop(module_name, None)
    after = {
        path.relative_to(BASE).as_posix()
        for path in BASE.rglob("*")
        if path.is_file()
    }
    expected_resources = [
        (
            expected.sequence,
            expected.candidate_id,
            expected.headword,
            expected.witness,
            expected.provider,
            expected.resource_class,
            expected.url,
            expected.width,
            expected.height,
        )
        for expected in EXPECTED_PAGES
    ]
    actual_resources = [
        (
            resource.sequence,
            resource.candidate_id,
            resource.headword,
            resource.witness,
            resource.provider,
            resource.resource_class,
            resource.url,
            resource.expected_width,
            resource.expected_height,
        )
        for resource in module.RESOURCES
    ]
    constants_exact = (
        module.PASS_STATUS == SUCCESS_STATUS
        and module.PUBLIC_GDT619_COMMIT == GDT619_COMMIT
        and tuple(module.GDT620_REGISTERED_PATHS) == REGISTERED_PATHS
        and module.RESPONSE_CAP_BYTES == 50_000_000
        and module.TOTAL_BODY_CAP_BYTES == 500_000_000
        and module.MINIMUM_REQUEST_SPACING_SECONDS == 4.0
        and module.SOCKET_OPERATION_TIMEOUT_SECONDS == 60
        and module.REQUEST_TOTAL_WALL_SECONDS == 180
        and module.RETRIES == 0
        and module.FOLLOW_REDIRECTS is False
        and module.SEALED_DATA == SEALED_DATA
        and actual_resources == expected_resources
    )
    return attempts == [] and before == after, constants_exact


def public_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from public_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from public_strings(child)


def public_privacy_is_clean(result: dict[str, Any], raw: bytes) -> bool:
    private_names = {
        "GDT620_STAGE_B_PRIVATE_OWNER.json",
        "STAGE_B_EXCLUSIVE.lock",
        "stage_b_state.json",
        "REQUEST_JOURNAL.jsonl",
        "STAGE_B_RESULT_DRAFT.json",
        *(f"{page.sequence:02d}_{page.provider}_{page.witness}_{page.candidate_id}.jpg" for page in EXPECTED_PAGES),
    }
    strings = list(public_strings(result))
    joined = "\n".join(strings)
    private_root_markers = tuple(
        os.sep + component + os.sep for component in ("home", "tmp", "Users")
    )
    windows_private = "C:" + "\\" + "Users" + "\\"
    file_scheme = "file" + "://"
    return (
        all(name not in joined for name in private_names)
        and all(not text.startswith(os.sep) for text in strings)
        and all(marker not in text for text in strings for marker in private_root_markers)
        and all(windows_private not in text for text in strings)
        and all(file_scheme not in text.lower() for text in strings)
        and all("data:" + "image" not in text.lower() for text in strings)
        and all(len(text) <= 512 for text in strings)
        and b"\xff\xd8\xff" not in raw
        and b"\x89PNG\r\n\x1a\n" not in raw
        and not any(byte < 0x20 and byte not in b"\t\n\r" for byte in raw)
    )


def repository_has_no_published_images() -> tuple[bool, bool]:
    tracked = safe_git_run(["ls-files", "-z"])
    tracked_clean = tracked.returncode == 0 and not any(
        Path(raw.decode("utf-8")).suffix.lower() in IMAGE_SUFFIXES
        for raw in tracked.stdout.split(b"\0")
        if raw
    )
    experiment_clean = True
    for current, directories, files in os.walk(BASE, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name
            for name in directories
            if not (current_path / name).is_symlink() and name != "__pycache__"
        ]
        if any(Path(name).suffix.lower() in IMAGE_SUFFIXES for name in files):
            experiment_clean = False
            break
    return tracked_clean, experiment_clean


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("+00:00"):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo == timezone.utc else None


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: Any) -> None:
        self.rows.append({"check": name, "status": "PASS" if condition is True else "FAIL"})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def payload(self, *, result_sha256: str) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "checks": self.rows,
            "decision": SUCCESS_STATUS if self.passed else FAILURE_STATUS,
            "experiment_id": "GDT620",
            "failed": len(self.rows) - passed,
            "image_files_opened": 0,
            "network_requests": 0,
            "passed": passed,
            "registration_commit": REGISTRATION_COMMIT,
            "result_sha256": result_sha256,
            "schema_version": 1,
            "status": "PASS" if self.passed else "FAIL",
            "total": len(self.rows),
        }


def result_checks(audit: Audit, result_path: Path) -> tuple[dict[str, Any], bytes, str]:
    raw = b""
    result: dict[str, Any] = {}
    regular = False
    try:
        info = result_path.lstat()
        regular = stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode)
        raw = result_path.read_bytes() if regular else b""
    except OSError:
        pass
    result_sha = digest_bytes(raw)
    audit.check(
        "result_regular_exact_size_and_sha256",
        regular and len(raw) == RESULT_SIZE and result_sha == RESULT_SHA256,
    )
    strict_ok = False
    try:
        loaded = strict_json(raw)
        if isinstance(loaded, dict):
            result = loaded
            strict_ok = canonical_bytes(result) == raw
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        pass
    audit.check("result_unique_key_strict_canonical_json", strict_ok)
    audit.check("result_top_level_key_set_exact", set(result) == TOP_LEVEL_KEYS)
    audit.check(
        "result_identity_status_seals_and_failure_count_exact",
        result.get("schema_version") == 1
        and result.get("experiment_id") == "GDT620"
        and result.get("status") == SUCCESS_STATUS
        and result.get("sealed_data") == SEALED_DATA
        and result.get("failure_count") == 0,
    )
    audit.check(
        "result_access_boundary_exact",
        result.get("access_boundary")
        == {
            "automatic_transcription": False,
            "local_crop_created": False,
            "network_crop_requests": 0,
            "source_text_read": False,
            "target_opened": False,
            "voynich_material_opened": False,
        },
    )
    audit.check(
        "gdt619_public_binding_exact",
        result.get("gdt619_public_binding")
        == {
            "commit": GDT619_COMMIT,
            "profile_sha256": GDT619_PROFILE_SHA256,
            "stage1_artifact": str(GDT619_STAGE1_REL),
            "stage1_sha256": GDT619_STAGE1_SHA256,
        },
    )
    audit.check(
        "gdt620_registration_binding_exact",
        result.get("gdt620_public_registration")
        == {"commit": REGISTRATION_COMMIT, "registered_runtime_paths": list(REGISTERED_PATHS)}
        and HEX40.fullmatch(REGISTRATION_COMMIT) is not None,
    )

    pages = result.get("pages")
    page_rows = (
        pages
        if isinstance(pages, list) and all(isinstance(row, dict) for row in pages)
        else []
    )
    page_schema_ok = (
        len(page_rows) == 10
        and all(isinstance(row, dict) and set(row) == PAGE_KEYS for row in page_rows)
        and all(
            isinstance(row.get("response_headers"), dict)
            and set(row["response_headers"]) == RESPONSE_HEADER_KEYS
            for row in page_rows
        )
    )
    audit.check("ten_page_objects_and_key_sets_exact", page_schema_ok)
    urls = [expected.url for expected in EXPECTED_PAGES]
    audit.check(
        "literal_urls_and_request_order_exact",
        result.get("literal_urls") == urls
        and result.get("request_order") == list(range(1, 11))
        and len(set(urls)) == 10,
    )

    exact_rows = len(page_rows) == len(EXPECTED_PAGES)
    transport_rows = exact_rows
    header_rows = exact_rows
    for row, expected in zip(page_rows, EXPECTED_PAGES):
        exact_rows = exact_rows and (
            row.get("sequence") == expected.sequence
            and row.get("candidate_id") == expected.candidate_id
            and row.get("headword") == expected.headword
            and row.get("witness") == expected.witness
            and row.get("resource_class") == expected.resource_class
            and row.get("request_url") == expected.url
            and row.get("decoded_width") == expected.width
            and row.get("decoded_height") == expected.height
            and row.get("observed_bytes") == expected.observed_bytes
            and row.get("raw_sha256") == expected.raw_sha256
            and row.get("request_url_sha256") == expected.request_url_sha256
            and expected.request_url_sha256 == digest_bytes(expected.url.encode("utf-8"))
            and HEX64.fullmatch(expected.raw_sha256) is not None
        )
        transport_rows = transport_rows and (
            row.get("status") == "SUCCESS"
            and row.get("response_url") == expected.url
            and row.get("redirect_attempts") == 0
            and row.get("content_type") == "image/jpeg"
            and row.get("content_encoding") is None
            and row.get("content_length_header") == expected.content_length
            and row.get("transfer_encoding") == expected.transfer_encoding
        )
        raw_headers = row.get("response_headers")
        headers = raw_headers if isinstance(raw_headers, dict) else {}
        header_rows = header_rows and headers == {
            "content_encoding": row.get("content_encoding"),
            "content_length": row.get("content_length_header"),
            "content_type": row.get("content_type"),
            "etag": row.get("etag"),
            "last_modified": row.get("last_modified"),
            "transfer_encoding": row.get("transfer_encoding"),
        }
        if expected.provider == "BSB":
            header_rows = header_rows and isinstance(row.get("etag"), str) and isinstance(row.get("last_modified"), str)
        else:
            header_rows = header_rows and row.get("etag") is None and row.get("last_modified") is None
    audit.check("ten_urls_dimensions_bytes_and_hashes_exact", exact_rows)
    audit.check("ten_success_final_url_media_encoding_and_redirect_rows_exact", transport_rows)
    audit.check("response_header_projection_exact", header_rows)

    content_rules = len(page_rows) == 10
    for row, expected in zip(page_rows, EXPECTED_PAGES):
        content_length = row.get("content_length_header")
        transfer_encoding = row.get("transfer_encoding")
        content_rules = content_rules and (
            (
                content_length is None
                or (
                    isinstance(content_length, str)
                    and content_length.isdecimal()
                    and int(content_length) == expected.observed_bytes
                )
            )
            and (transfer_encoding is None or transfer_encoding == "chunked")
            and not (content_length is not None and transfer_encoding is not None)
            and expected.observed_bytes <= 50_000_000
        )
    audit.check("content_length_chunked_and_per_response_caps_exact", content_rules)
    observed_total = sum(
        row.get("observed_bytes", 0)
        for row in page_rows
        if type(row.get("observed_bytes")) is int
    )
    audit.check(
        "body_count_and_registered_caps_exact",
        observed_total == 13_178_909
        and observed_total <= 500_000_000
        and sum(page.observed_bytes for page in EXPECTED_PAGES[:5]) == 2_905_123
        and sum(page.observed_bytes for page in EXPECTED_PAGES[5:]) == 10_273_786,
    )
    expected_policy = {
        "accept_encoding": "identity",
        "concurrency": 1,
        "cumulative_bsb_cap": 10,
        "fixed_pre_request_delay": {
            "applies_to_sequences": list(range(2, 11)),
            "elapsed_wall_time_never_reduces_delay": True,
            "required_after_restart": True,
            "seconds": 4.0,
        },
        "follow_redirects": False,
        "http_method": "GET",
        "maximum_new_bnf_requests": 5,
        "maximum_new_bsb_requests": 5,
        "per_response_cap_bytes": 50_000_000,
        "request_total_wall_seconds": 180,
        "retries": 0,
        "second_execution_state_directory_forbidden_by_policy": True,
        "socket_operation_timeout_seconds": 60,
        "stage_b_request_count": 10,
        "total_body_cap_bytes": 500_000_000,
    }
    audit.check("request_policy_exact", result.get("request_policy") == expected_policy)

    timing_ok = len(page_rows) == 10
    fixed_delay_ok = len(page_rows) == 10
    previous_completed: datetime | None = None
    for index, row in enumerate(page_rows):
        started = parse_utc(row.get("request_started_utc"))
        completed = parse_utc(row.get("response_completed_utc"))
        timing_ok = timing_ok and started is not None and completed is not None
        if started is None or completed is None:
            continue
        timing_ok = timing_ok and 0 <= (completed - started).total_seconds() <= 180
        measured = row.get("seconds_since_previous_request_completion")
        defined = row.get("defined_delay_seconds")
        if index == 0:
            timing_ok = timing_ok and measured is None
            fixed_delay_ok = fixed_delay_ok and defined == 0.0
        else:
            recomputed = (started - previous_completed).total_seconds() if previous_completed is not None else math.nan
            timing_ok = timing_ok and (
                type(measured) is float
                and math.isfinite(measured)
                and math.isclose(measured, recomputed, rel_tol=0.0, abs_tol=1e-6)
            )
            fixed_delay_ok = fixed_delay_ok and (
                defined == 4.0
                and type(measured) is float
                and math.isfinite(measured)
                and measured >= 4.0
            )
        previous_completed = completed
    audit.check("utc_timestamps_durations_and_measured_spacing_recompute", timing_ok)
    audit.check("measured_spacing_and_defined_fixed_delay_are_separate_and_satisfied", fixed_delay_ok)
    audit.check("public_result_has_no_private_name_path_or_image_bytes", public_privacy_is_clean(result, raw))
    return result, raw, result_sha


def manifest_core_check() -> bool:
    try:
        manifest = strict_json((ROOT / MANIFEST_REL).read_bytes())
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(manifest, dict):
        return False
    inputs = manifest.get("inputs", [])
    outputs = manifest.get("outputs", [])
    expected_inputs = {
        str(GDT619_STAGE1_REL),
        "experiments/yolo/gdt619_five_source_page_acquisition/artifacts/REGISTERED_REQUEST_PROFILE.json",
    }
    if not (
        manifest.get("schema_version") == 1
        and manifest.get("experiment_id") == "GDT620"
        and manifest.get("slug") == "stage_b_source_page_acquisition"
        and manifest.get("status") == SUCCESS_STATUS
        and manifest.get("sealed_data") == SEALED_DATA
        and manifest.get("commands")
        == {
            "run": f"python3 {BASE_REL / 'src/run.py'} --check",
            "validate": f"python3 {VALIDATOR_REL} --check",
        }
        and manifest.get("validation") == {"artifact": str(VALIDATION_REL), "status": "PASS"}
        and isinstance(inputs, list)
        and isinstance(outputs, list)
        and {row.get("path") for row in inputs if isinstance(row, dict)} == expected_inputs
        and len(inputs) == len(expected_inputs)
        and {row.get("path") for row in outputs if isinstance(row, dict)} == EXPECTED_MANIFEST_OUTPUTS
        and len(outputs) == len(EXPECTED_MANIFEST_OUTPUTS)
    ):
        return False
    nonvalidation = inputs + [
        row for row in outputs
        if isinstance(row, dict) and row.get("path") != str(VALIDATION_REL)
    ]
    for row in nonvalidation:
        if not isinstance(row, dict):
            return False
        relative = row.get("path")
        expected_sha = row.get("sha256")
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not isinstance(expected_sha, str)
            or HEX64.fullmatch(expected_sha) is None
        ):
            return False
        path = ROOT / relative
        try:
            info = path.lstat()
        except OSError:
            return False
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or digest(path) != expected_sha:
            return False
    return True


def build_core() -> tuple[Audit, dict[str, Any]]:
    audit = Audit()
    result, raw, result_sha = result_checks(audit, ROOT / RESULT_REL)
    explicit_git, public_ancestor, blobs_exact = registration_git_evidence()
    audit.check("git_workspace_is_explicit_real_directory", explicit_git)
    audit.check("registration_commit_is_ancestor_of_origin_main", public_ancestor)
    audit.check("seven_registration_commit_blobs_and_modes_exact", blobs_exact)
    audit.check("inherited_git_environment_cannot_redirect_checks", hostile_git_environment_is_ignored())
    tracked_clean, experiment_clean = repository_has_no_published_images()
    audit.check("repository_index_contains_no_image_files", tracked_clean)
    audit.check("gdt620_working_tree_contains_no_image_files", experiment_clean)
    stable_runtime_paths = (
        str(BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"),
        str(ACQUIRER_REL),
    )
    try:
        stable_runtime_exact = all(
            digest(ROOT / relative) == REGISTERED_BLOB_SHA256[relative]
            for relative in stable_runtime_paths
        )
    except OSError:
        stable_runtime_exact = False
    audit.check("working_profile_and_acquirer_match_registration_blobs", stable_runtime_exact)
    guarded_ok, constants_ok = (
        guarded_acquirer_validation(result) if stable_runtime_exact else (False, False)
    )
    audit.check("acquirer_import_and_public_validation_are_offline_and_image_closed", guarded_ok)
    audit.check("acquirer_deck_constants_and_registration_paths_exact", constants_ok)
    audit.check("manifest_nonvalidation_bindings_and_result_status_exact", manifest_core_check())
    del raw
    return audit, audit.payload(result_sha256=result_sha)


def write_validation_artifact(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_bytes(payload))
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-artifact", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit, core_payload = build_core()
    validation_path = ROOT / VALIDATION_REL
    if args.write_artifact:
        if not audit.passed:
            print(json.dumps(core_payload, indent=2, sort_keys=True, ensure_ascii=False))
            return 1
        write_validation_artifact(validation_path, core_payload)
        print(f"WROTE {VALIDATION_REL} {digest(validation_path)}")
        return 0

    audit.check(
        "validation_artifact_matches_core_payload",
        validation_path.is_file()
        and not validation_path.is_symlink()
        and validation_path.read_bytes() == canonical_bytes(core_payload),
    )
    try:
        manifest = strict_json((ROOT / MANIFEST_REL).read_bytes())
        rows = [
            row for row in manifest.get("outputs", [])
            if isinstance(row, dict) and row.get("path") == str(VALIDATION_REL)
        ]
    except (OSError, AttributeError, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        rows = []
    audit.check(
        "manifest_validation_artifact_self_hash_exact",
        len(rows) == 1
        and validation_path.is_file()
        and rows[0].get("sha256") == digest(validation_path),
    )
    payload = audit.payload(result_sha256=core_payload["result_sha256"])
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
