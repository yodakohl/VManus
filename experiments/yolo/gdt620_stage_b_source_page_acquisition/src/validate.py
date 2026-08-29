#!/usr/bin/env python3
"""Validate the offline GDT620 Stage-B registration."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt620_stage_b_source_page_acquisition")
BASE = ROOT / BASE_REL
PROFILE_REL = BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"
VALIDATION_REL = BASE_REL / "artifacts/REGISTERED_VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"
RUN_REL = BASE_REL / "src/run.py"
ACQUIRER_REL = BASE_REL / "src/acquire_stage_b.py"
VALIDATOR_REL = BASE_REL / "src/validate.py"
REQUIREMENTS_REL = BASE_REL / "requirements.txt"

GDT619_COMMIT = "e82d73d6300f51c810ff131711ace31bb2610b69"
GDT619_STAGE1_REL = Path(
    "experiments/yolo/gdt619_five_source_page_acquisition/"
    "artifacts/STAGE1_RESOLUTION.json"
)
GDT619_STAGE1_SHA = (
    "95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422"
)
GDT619_PROFILE_REL = Path(
    "experiments/yolo/gdt619_five_source_page_acquisition/"
    "artifacts/REGISTERED_REQUEST_PROFILE.json"
)
GDT619_PROFILE_SHA = (
    "c577525c5045b2e59ba68741fd098c1d94f43f6d52ac4364683f4dd1e1064164"
)
STATUS = "STAGE_B_PROFILE_REGISTERED__NO_STAGE_B_REQUEST_EXECUTED"
SUCCESS = "TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED"
EXPECTED_QUESTION = (
    "Can the ten source pages already selected by GDT619 be acquired in one "
    "exact closed order with bounded transport and at-most-once-per-bound-state "
    "request semantics before any source text or Voynich target is opened?"
)
EXPECTED_CLAIM_CEILING = (
    "This registration fixes one exact ten-request source-page deck and an "
    "at-most-once-per-bound-state acquirer. It executes no request, opens no "
    "source image or Voynich target, and assigns no Voynich sign, word, "
    "language, plant, plaintext, operation, or meaning. A later successful "
    "acquisition can establish only that the ten registered source JPEGs were "
    "received and mechanically validated; it still cannot read or translate them."
)
EXPECTED_ARTIFACT_POLICY = {
    "large_artifact_justification": (
        "The ten full-page JPEGs, private state, and request journal remain "
        "outside the repository. Only the compact request profile, validation "
        "certificate, and later public-safe hash/provenance result may be retained."
    ),
    "max_inline_bytes": 5_000_000,
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_RUNTIME_PATHS = (
    str(BASE_REL / "METHOD.md"),
    str(BASE_REL / "PREREGISTRATION.md"),
    str(PROFILE_REL),
    str(REQUIREMENTS_REL),
    str(ACQUIRER_REL),
    str(VALIDATOR_REL),
    str(MANIFEST_REL),
)
EXPECTED_INPUTS = {str(GDT619_STAGE1_REL), str(GDT619_PROFILE_REL)}
EXPECTED_OUTPUTS = {
    str(BASE_REL / "README.md"),
    str(BASE_REL / "METHOD.md"),
    str(BASE_REL / "PREREGISTRATION.md"),
    str(BASE_REL / "artifacts/README.md"),
    str(PROFILE_REL),
    str(VALIDATION_REL),
    str(REQUIREMENTS_REL),
    str(RUN_REL),
    str(ACQUIRER_REL),
    str(VALIDATOR_REL),
}
EXPECTED_TREE_FILES = {
    "README.md",
    "METHOD.md",
    "PREREGISTRATION.md",
    "artifacts/README.md",
    "artifacts/REGISTERED_STAGE_B_PROFILE.json",
    "artifacts/REGISTERED_VALIDATION.json",
    "experiment.json",
    "requirements.txt",
    "src/acquire_stage_b.py",
    "src/run.py",
    "src/validate.py",
}
EXPECTED_TREE_DIRECTORIES = {"artifacts", "src"}
PRIVATE_RUNTIME_BASENAMES = {
    "GDT620_STAGE_B_PRIVATE_OWNER.json",
    "STAGE_B_EXCLUSIVE.lock",
    "stage_b_state.json",
    "REQUEST_JOURNAL.jsonl",
    "STAGE_B_RESULT_DRAFT.json",
}
EXPECTED_ROWS = (
    (1, "DEV01", "BSB", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/max/0/default.jpg", 1707, 2466),
    (2, "DEV02", "BSB", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00075/full/max/0/default.jpg", 1707, 2581),
    (3, "DEV03", "BSB", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00164/full/max/0/default.jpg", 1707, 2562),
    (4, "DEV04", "BSB", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00096/full/max/0/default.jpg", 1707, 2591),
    (5, "DEV05", "BSB", "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00101/full/max/0/default.jpg", 1707, 2581),
    (6, "DEV01", "BNF_GALLICA", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f58/full/full/0/native.jpg", 3302, 4581),
    (7, "DEV02", "BNF_GALLICA", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f96/full/full/0/native.jpg", 3451, 4553),
    (8, "DEV03", "BNF_GALLICA", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f178/full/full/0/native.jpg", 3284, 4557),
    (9, "DEV04", "BNF_GALLICA", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f91/full/full/0/native.jpg", 3333, 4388),
    (10, "DEV05", "BNF_GALLICA", "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f122/full/full/0/native.jpg", 3346, 4574),
)

REQUIRED_SELFTEST_CHECKS = {
    "malicious_git_environment_cannot_redirect_workspace_binding",
    "working_gdt620_profile_registration_compatible_offline",
    "fixed_delay_and_prepublication_network_gate_enforced_offline",
    "public_stage1_commit_and_sha_exact",
    "public_profile_sha_and_gallica_urls_exact",
    "working_gdt620_profile_deck_matches_acquirer",
    "working_gdt620_publication_paths_match",
    "success_status_exact",
    "timeout_public_constants_exact",
    "response_and_total_caps_exact",
    "pillow_runtime_exact",
    "exact_ten_url_allowlist",
    "provider_caps_exact",
    "cumulative_bsb_cap_exact",
    "sealed_target_boundary",
    "exact_request_headers_exclude_range_referer_conditionals",
    "environment_proxy_cookie_auth_handlers_disabled",
    "public_acquire_api_has_no_transport_clock_or_gate_bypass",
    "offline_test_core_refuses_production_transport",
    "public_registration_commit_hex40_required",
    "first_request_has_no_fixed_pause",
    "restart_and_wall_clock_jump_still_sleep_full_four",
    "content_length_over_cap_stops_before_body",
    "duplicate_content_length_stops_before_body",
    "missing_content_length_uses_cap_plus_one",
    "short_content_length_is_partial_stop",
    "nonidentity_content_encoding_stops_before_body",
    "chunked_with_content_length_stops_before_body",
    "total_wall_deadline_stops_stream",
    "truncated_jpeg_decode_stop",
    "wrong_final_url_stops_before_body",
    "wrong_media_stops_before_body",
    "dimension_mismatch_after_full_decode",
    "wrapper_transport_refused_before_private_state_or_request",
    "offline_test_core_requires_exact_fake_clock",
    "intent_wall_clock_observation_is_unset",
    "oversleep_success_observes_five_but_guarantees_four",
    "backward_wall_clock_observation_is_negative_and_not_a_gate",
    "failure_observes_actual_wall_spacing_separate_from_delay",
    "mock_transport_exact_order",
    "mock_transport_concurrency_one",
    "mock_success_result_status",
    "mock_result_fixed_pre_request_delay_exact",
    "mock_fixed_pause_first_then_nine",
    "journal_intent_and_success_rows",
    "journal_registered_fields_complete",
    "full_pass_intents_have_no_wall_spacing_observation",
    "public_safe_result_has_no_private_path",
    "private_modes_exact",
    "simulated_crash_reached_transport_once",
    "crash_intent_permanently_refuses_resend",
    "crash_state_durable_in_flight",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def load_module(relative: Path, name: str):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def git_blob(commit: str, relative: Path) -> bytes | None:
    completed = safe_git_run(
        ["show", f"{commit}:{relative.as_posix()}"],
    )
    return completed.stdout if completed.returncode == 0 else None


def safe_git_run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        [
            "/usr/bin/git",
            f"--git-dir={ROOT / '.git'}",
            f"--work-tree={ROOT}",
            *arguments,
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        timeout=30,
    )


def git_ancestor(commit: str, ref: str) -> bool:
    completed = safe_git_run(["merge-base", "--is-ancestor", commit, ref])
    return completed.returncode == 0


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


def is_exact_main_guard(statement: ast.If) -> bool:
    test = statement.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def qualified_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def top_level_network_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    network_names = {
        "connect",
        "connect_ex",
        "create_connection",
        "getaddrinfo",
        "open_url",
        "requests.get",
        "requests.post",
        "requests.request",
        "sendmsg",
        "sendto",
        "socket.create_connection",
        "socket.getaddrinfo",
        "urllib.request.urlopen",
        "urlopen",
    }

    class ExecutedAtImport(ast.NodeVisitor):
        def __init__(self) -> None:
            self.calls: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)
            if node.returns is not None:
                self.visit(node.returns)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Lambda(self, node: ast.Lambda) -> None:
            del node

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_If(self, node: ast.If) -> None:
            if is_exact_main_guard(node):
                for statement in node.orelse:
                    self.visit(statement)
                return
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            name = qualified_name(node.func)
            if name in network_names or name.rsplit(".", 1)[-1] in {
                "connect",
                "connect_ex",
                "create_connection",
                "getaddrinfo",
                "sendmsg",
                "sendto",
                "urlopen",
            }:
                self.calls.append(name)
            self.generic_visit(node)

    visitor = ExecutedAtImport()
    visitor.visit(tree)
    return visitor.calls


def tree_snapshot(root: Path, *, strong: bool) -> tuple[tuple[Any, ...], ...]:
    rows: list[tuple[Any, ...]] = []
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path == ROOT and ".git" in directory_names:
            directory_names.remove(".git")
        for name in sorted(directory_names + file_names):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                rows.append((relative, "L", info.st_mode, os.readlink(path)))
                if name in directory_names:
                    directory_names.remove(name)
            elif stat.S_ISDIR(info.st_mode):
                rows.append((relative, "D", info.st_mode, info.st_mtime_ns))
            elif stat.S_ISREG(info.st_mode):
                content_digest = digest(path) if strong else None
                rows.append(
                    (
                        relative,
                        "F",
                        info.st_mode,
                        info.st_size,
                        info.st_mtime_ns,
                        content_digest,
                    )
                )
            else:
                rows.append((relative, "O", info.st_mode, info.st_size))
    return tuple(sorted(rows))


def privacy_findings(data: bytes, label: str) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    findings: list[str] = []
    private_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "file" + "://",
        "C:" + "\\Users\\",
        "-----BEGIN " + "PRIVATE KEY-----",
        "-----BEGIN " + "RSA PRIVATE KEY-----",
        "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
        "-----BEGIN " + "EC PRIVATE KEY-----",
    )
    for marker in private_markers:
        if marker in text:
            findings.append(f"{label}:{marker[:24]}")
    credential_patterns = (
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}\b"),
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\b"
            r"\s*[:=]\s*['\"][^'\"\r\n]{12,}['\"]"
        ),
    )
    for pattern in credential_patterns:
        if pattern.search(text):
            findings.append(f"{label}:credential-pattern")
    return findings


def private_path_name(path: str) -> bool:
    name = Path(path).name
    return (
        name in PRIVATE_RUNTIME_BASENAMES
        or name in {".env", ".netrc", "credentials.json", "id_rsa", "id_ed25519"}
        or Path(name).suffix.lower() in {".key", ".p12", ".pem", ".pfx"}
    )


def staged_privacy_findings() -> list[str]:
    listed = safe_git_run(
        ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]
    )
    if listed.returncode != 0:
        return ["staged-tree:list-failed"]
    findings: list[str] = []
    for raw_path in listed.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            findings.append("staged-tree:non-utf8-path")
            continue
        if private_path_name(path):
            findings.append(f"staged-tree:private-name:{path}")
        blob = safe_git_run(["show", f":{path}"])
        if blob.returncode != 0:
            findings.append(f"staged-tree:unreadable:{path}")
            continue
        findings.extend(privacy_findings(blob.stdout, f"staged:{path}"))
    return findings


class NetworkForbidden(RuntimeError):
    pass


def offline_worker() -> int:
    """Import and self-test registration code with socket/process egress denied."""

    import socket
    import urllib.request

    probe_events: list[str] = []
    unexpected_network_events: list[str] = []
    unexpected_process_events: list[str] = []
    probing = True

    def deny(label: str):
        def blocked(*_args: Any, **_kwargs: Any):
            target = probe_events if probing else unexpected_network_events
            target.append(label)
            raise NetworkForbidden(label)

        return blocked

    socket.socket.connect = deny("socket.socket.connect")  # type: ignore[method-assign]
    socket.socket.connect_ex = deny("socket.socket.connect_ex")  # type: ignore[method-assign]
    socket.socket.sendto = deny("socket.socket.sendto")  # type: ignore[method-assign]
    if hasattr(socket.socket, "sendmsg"):
        socket.socket.sendmsg = deny("socket.socket.sendmsg")  # type: ignore[attr-defined,method-assign]
    socket.create_connection = deny("socket.create_connection")
    socket.getaddrinfo = deny("socket.getaddrinfo")
    urllib.request.urlopen = deny("urllib.request.urlopen")
    urllib.request.OpenerDirector.open = deny("urllib.request.OpenerDirector.open")
    urllib.request.AbstractHTTPHandler.do_open = deny(
        "urllib.request.AbstractHTTPHandler.do_open"
    )

    real_subprocess_run = subprocess.run
    real_subprocess_popen = subprocess.Popen
    registered_run_active = False

    def guarded_subprocess_popen(command: Any, *args: Any, **kwargs: Any):
        if not registered_run_active:
            unexpected_process_events.append(repr(command)[:160])
            raise NetworkForbidden("direct subprocess in offline worker")
        return real_subprocess_popen(command, *args, **kwargs)

    def guarded_subprocess_run(command: Any, *args: Any, **kwargs: Any):
        nonlocal registered_run_active
        valid = isinstance(command, (list, tuple)) and len(command) >= 4
        if valid:
            normalized = [str(item) for item in command]
            valid = (
                normalized[0] == "/usr/bin/git"
                and normalized[1] == f"--git-dir={ROOT / '.git'}"
                and normalized[2] == f"--work-tree={ROOT}"
                and normalized[3] in {"merge-base", "rev-parse", "show"}
                and kwargs.get("shell", False) is False
            )
        if not valid:
            unexpected_process_events.append(repr(command)[:160])
            raise NetworkForbidden("unregistered subprocess in offline worker")
        registered_run_active = True
        try:
            return real_subprocess_run(command, *args, **kwargs)
        finally:
            registered_run_active = False

    subprocess.run = guarded_subprocess_run  # type: ignore[assignment]
    subprocess.Popen = guarded_subprocess_popen  # type: ignore[assignment,misc]

    def deny_process(*args: Any, **_kwargs: Any):
        unexpected_process_events.append(repr(args)[:160])
        raise NetworkForbidden("shell/spawn in offline worker")

    os.system = deny_process  # type: ignore[assignment]
    os.popen = deny_process  # type: ignore[assignment]
    for spawn_name in (
        "posix_spawn",
        "posix_spawnp",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
    ):
        if hasattr(os, spawn_name):
            setattr(os, spawn_name, deny_process)

    def expect_blocked(action: Any) -> bool:
        before = len(probe_events)
        try:
            action()
        except NetworkForbidden:
            return len(probe_events) == before + 1
        return False

    def socket_connect_probe() -> None:
        client = socket.socket()
        try:
            client.connect(("127.0.0.1", 9))
        finally:
            client.close()

    probes_ok = all(
        (
            expect_blocked(lambda: socket.getaddrinfo("example.invalid", 443)),
            expect_blocked(
                lambda: socket.create_connection(("127.0.0.1", 9), timeout=0.01)
            ),
            expect_blocked(socket_connect_probe),
            expect_blocked(lambda: urllib.request.urlopen("https://example.invalid")),
            expect_blocked(
                lambda: urllib.request.build_opener().open(
                    "https://example.invalid"
                )
            ),
        )
    )
    probing = False

    try:
        profile_path = ROOT / PROFILE_REL
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        builder = load_module(RUN_REL, "gdt620_builder_guarded")
        acquirer = load_module(ACQUIRER_REL, "gdt620_acquirer_guarded")
        working_profile_ok = True
        try:
            acquirer.validate_gdt620_registration_profile(profile)
        except Exception:
            working_profile_ok = False
        self_test = acquirer.self_test()
        payload = {
            "builder_profile_match": profile_path.read_bytes()
            == builder.canonical_bytes(builder.build_profile()),
            "constants": {
                "follow_redirects": acquirer.FOLLOW_REDIRECTS,
                "maximum_new_bnf_requests": acquirer.MAX_NEW_BNF_REQUESTS,
                "maximum_new_bsb_requests": acquirer.MAX_NEW_BSB_REQUESTS,
                "minimum_request_spacing_seconds": acquirer.MINIMUM_REQUEST_SPACING_SECONDS,
                "pillow_version": acquirer.PILLOW_VERSION,
                "request_total_wall_seconds": acquirer.REQUEST_TOTAL_WALL_SECONDS,
                "response_cap_bytes": acquirer.RESPONSE_CAP_BYTES,
                "retries": acquirer.RETRIES,
                "socket_operation_timeout_seconds": acquirer.SOCKET_OPERATION_TIMEOUT_SECONDS,
                "success_status": acquirer.PASS_STATUS,
                "total_body_cap_bytes": acquirer.TOTAL_BODY_CAP_BYTES,
            },
            "guard_probe_events": probe_events,
            "guard_probes_ok": probes_ok,
            "network_attempts": unexpected_network_events,
            "process_attempts": unexpected_process_events,
            "profile_accepted": working_profile_ok,
            "registered_paths": list(acquirer.GDT620_REGISTERED_PATHS),
            "resource_rows": [
                [
                    resource.sequence,
                    resource.candidate_id,
                    "BSB" if resource.provider == "BSB" else "BNF_GALLICA",
                    resource.url,
                    resource.expected_width,
                    resource.expected_height,
                ]
                for resource in acquirer.RESOURCES
            ],
            "schema_version": 1,
            "self_test": self_test,
            "status": "PASS",
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    except BaseException as exc:
        print(
            json.dumps(
                {
                    "error_type": type(exc).__name__,
                    "guard_probe_events": probe_events,
                    "guard_probes_ok": probes_ok,
                    "network_attempts": unexpected_network_events,
                    "process_attempts": unexpected_process_events,
                    "schema_version": 1,
                    "status": "FAIL",
                },
                sort_keys=True,
            )
        )
        return 1


def run_offline_worker() -> tuple[dict[str, Any], bool]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    environment.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, str(ROOT / VALIDATOR_REL), "--_offline-worker"],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        timeout=180,
    )
    try:
        payload = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {}
    return payload, completed.returncode == 0


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool) -> None:
        self.rows.append({"check": name, "status": "PASS" if condition else "FAIL"})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def payload(self) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "checks": self.rows,
            "decision": STATUS if self.passed else "REGISTRATION_VALIDATION_FAILURE",
            "experiment_id": "GDT620",
            "failed": len(self.rows) - passed,
            "network_requests": 0,
            "passed": passed,
            "schema_version": 1,
            "status": "PASS" if self.passed else "FAIL",
            "total": len(self.rows),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-artifact", action="store_true")
    mode.add_argument("--print-artifact-template", action="store_true")
    mode.add_argument("--_offline-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args._offline_worker:
        return offline_worker()

    audit = Audit()
    profile_path = ROOT / PROFILE_REL
    manifest_path = ROOT / MANIFEST_REL
    validation_path = ROOT / VALIDATION_REL
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repository_before = tree_snapshot(ROOT, strong=False)
    experiment_before = tree_snapshot(BASE, strong=True)
    worker, worker_completed = run_offline_worker()
    experiment_after = tree_snapshot(BASE, strong=True)
    repository_after = tree_snapshot(ROOT, strong=False)

    audit.check(
        "profile_is_canonical_builder_output",
        worker_completed and worker.get("builder_profile_match") is True,
    )
    audit.check(
        "guarded_import_and_selftest_leave_repository_unchanged",
        experiment_before == experiment_after
        and repository_before == repository_after,
    )
    audit.check(
        "profile_identity_status_and_seals",
        profile.get("schema_version") == 1
        and profile.get("experiment_id") == "GDT620"
        and profile.get("decision") == STATUS
        and profile.get("status") == STATUS
        and profile.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    dependency = profile.get("dependency", {})
    audit.check(
        "profile_dependency_exact",
        dependency.get("public_stage1_commit") == GDT619_COMMIT
        and dependency.get("stage1_path") == str(GDT619_STAGE1_REL)
        and dependency.get("stage1_sha256") == GDT619_STAGE1_SHA
        and dependency.get("source_profile_path") == str(GDT619_PROFILE_REL)
        and dependency.get("source_profile_sha256") == GDT619_PROFILE_SHA
        and dependency.get("stage1_publication_effect")
        == "GLOBAL_DELTA_MINUS_ONE__STAGE_B_AUTHORIZED_NOT_EXECUTED",
    )
    stage1_blob = git_blob(GDT619_COMMIT, GDT619_STAGE1_REL)
    source_profile_blob = git_blob(GDT619_COMMIT, GDT619_PROFILE_REL)
    audit.check(
        "gdt619_commit_is_public_ancestor",
        HEX40.fullmatch(GDT619_COMMIT) is not None
        and git_ancestor(GDT619_COMMIT, "refs/remotes/origin/main"),
    )
    audit.check(
        "gdt619_committed_blobs_exact",
        stage1_blob is not None
        and hashlib.sha256(stage1_blob).hexdigest() == GDT619_STAGE1_SHA
        and source_profile_blob is not None
        and hashlib.sha256(source_profile_blob).hexdigest() == GDT619_PROFILE_SHA
        and (ROOT / GDT619_STAGE1_REL).read_bytes() == stage1_blob
        and (ROOT / GDT619_PROFILE_REL).read_bytes() == source_profile_blob,
    )
    inherited_git_dir = os.environ.get("GIT_DIR")
    inherited_git_work_tree = os.environ.get("GIT_WORK_TREE")
    try:
        os.environ["GIT_DIR"] = str(ROOT / "__forbidden_fake_git_dir__")
        os.environ["GIT_WORK_TREE"] = str(ROOT.parent)
        hostile_environment_blob = git_blob(GDT619_COMMIT, GDT619_STAGE1_REL)
    finally:
        if inherited_git_dir is None:
            os.environ.pop("GIT_DIR", None)
        else:
            os.environ["GIT_DIR"] = inherited_git_dir
        if inherited_git_work_tree is None:
            os.environ.pop("GIT_WORK_TREE", None)
        else:
            os.environ["GIT_WORK_TREE"] = inherited_git_work_tree
    audit.check(
        "git_environment_cannot_redirect_public_blob_check",
        hostile_environment_blob is not None
        and hashlib.sha256(hostile_environment_blob).hexdigest() == GDT619_STAGE1_SHA,
    )

    requests = profile.get("requests", [])
    actual_rows = [
        (
            row.get("sequence"),
            row.get("candidate_id"),
            row.get("institution"),
            row.get("url"),
            row.get("expected_dimensions", {}).get("width"),
            row.get("expected_dimensions", {}).get("height"),
        )
        for row in requests
    ]
    audit.check("ten_literal_request_rows_exact", actual_rows == list(EXPECTED_ROWS))
    audit.check(
        "request_headers_and_resource_classes_exact",
        all(
            row.get("headers")
            == {
                "Accept": "image/jpeg",
                "Accept-Encoding": "identity",
                "User-Agent": "VManus-GDT620-stage-b-source-acquisition/1.0",
            }
            and row.get("resource_class")
            == (
                "IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY"
                if row.get("institution") == "BSB"
                else "IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE"
            )
            for row in requests
        ),
    )
    audit.check(
        "application_and_protocol_header_semantics_exact",
        profile.get("protocol", {}).get("header_semantics")
        == {
            "application_headers_exact": [
                "Accept",
                "Accept-Encoding",
                "User-Agent",
            ],
            "opener_default_addheaders_disabled": True,
            "protocol_headers_may_be_generated_by_python": [
                "Host",
                "Connection: close",
            ],
            "wire_header_set_claimed_exact": False,
        },
    )
    audit.check(
        "request_order_uniqueness_and_institution_caps",
        [row[0] for row in actual_rows] == list(range(1, 11))
        and len({row[3] for row in actual_rows}) == 10
        and sum(row[2] == "BSB" for row in actual_rows) == 5
        and sum(row[2] == "BNF_GALLICA" for row in actual_rows) == 5,
    )

    protocol = profile.get("protocol", {})
    delay = protocol.get("fixed_pre_request_delay", {})
    caps = protocol.get("cap_semantics", {})
    audit.check(
        "fixed_delay_contract_exact",
        delay
        == {
            "applies_to_sequences": list(range(2, 11)),
            "elapsed_wall_time_never_reduces_delay": True,
            "required_after_restart": True,
            "seconds": 4.0,
        }
        and "minimum_seconds_between_previous_completion_and_next_start" not in protocol,
    )
    audit.check(
        "transport_caps_and_stops_exact",
        protocol.get("http_method") == "GET"
        and protocol.get("requests_allowed") == 10
        and protocol.get("requests_by_institution") == {"BNF_GALLICA": 5, "BSB": 5}
        and protocol.get("concurrency") == 1
        and protocol.get("retries") == 0
        and protocol.get("follow_redirects") is False
        and protocol.get("socket_operation_timeout_seconds") == 60
        and protocol.get("request_total_wall_seconds") == 180
        and protocol.get("maximum_response_bytes_each") == 50_000_000
        and protocol.get("maximum_response_bytes_total") == 500_000_000
        and protocol.get("proxy_cookie_auth") == "DISABLED"
        and protocol.get("failure_action") == "STOP_ON_FIRST_FAILURE__NO_LATER_REQUEST"
        and protocol.get("unregistered_head_requests") is False
        and protocol.get("unregistered_info_json_requests") is False
        and protocol.get("unregistered_manifest_requests") is False
        and protocol.get("network_crops") is False,
    )
    audit.check(
        "body_encoding_and_jpeg_contract_exact",
        caps.get("content_encoding") == "ABSENT_OR_IDENTITY_ONLY"
        and caps.get("content_length")
        == "ZERO_OR_ONE_VALID_NONNEGATIVE_DECIMAL_AT_MOST_CAP__IF_PRESENT_MUST_EQUAL_OBSERVED_BYTES"
        and caps.get("transfer_encoding")
        == "ABSENT_OR_EXACT_CHUNKED_WITHOUT_CONTENT_LENGTH"
        and "Pillow_10_2_0" in protocol.get("full_jpeg_validation", "")
        and "EXACT_STORED_DIMENSIONS" in protocol.get("full_jpeg_validation", ""),
    )
    audit.check(
        "at_most_once_claim_exact",
        protocol.get("exactly_once", "").startswith("AT_MOST_ONCE_PER_BOUND_EXECUTION_STATE")
        and "SECOND_STATE_DIRECTORY_FORBIDDEN_BY_POLICY" in protocol.get("exactly_once", "")
        and "GLOBAL_EXACTLY_ONCE" not in json.dumps(profile),
    )

    gate = profile.get("execution_publication_gate", {})
    audit.check(
        "publication_gate_exact",
        tuple(gate.get("committed_paths_must_match_runtime_bytes", []))
        == EXPECTED_RUNTIME_PATHS
        and gate.get("network_forbidden_until_registration_commit_is_public") is True
        and gate.get("public_registration_commit_argument_required") is True
        and gate.get("registration_commit_must_be_ancestor_of_origin_main") is True
        and gate.get("working_tree_only_code_cannot_authorize_network") is True,
    )
    output = profile.get("output_contract", {})
    private = output.get("private_directory", {})
    audit.check(
        "private_state_and_result_contract_exact",
        output.get("success_status") == SUCCESS
        and private.get("absolute") is True
        and private.get("outside_repository") is True
        and private.get("mode") == "0700"
        and private.get("no_symlink_components") is True
        and private.get("ownership_marker_required") is True
        and private.get("second_execution_state_directory_forbidden_by_policy") is True
        and output.get("public_result_must_exclude")
        == [
            "absolute_private_path",
            "private_filename",
            "image_bytes",
            "authentication_material",
            "machine_metadata",
        ],
    )
    audit.check(
        "registration_access_boundary_exact",
        profile.get("access_state_at_registration")
        == {
            "image_bytes_received": 0,
            "network_requests": 0,
            "registration_is_offline": True,
            "source_images_opened": 0,
            "stage1_already_public": True,
            "stage_b_acquisition_code_is_separate": True,
            "voynich_material_opened": 0,
        }
        and {"F84", "F84R", "VOYNICH_PAGE", "VOYNICH_TRANSCRIPTION", "SOURCE_IMAGE_DISPLAY", "SOURCE_IMAGE_READING", "OCR", "NETWORK_CROP", "UNREGISTERED_URL"}
        == set(profile.get("forbidden_access", [])),
    )
    rights = profile.get("rights_policy", {})
    audit.check(
        "rights_and_nonredistribution_exact",
        rights.get("image_redistribution_in_repository") is False
        and rights.get("private_source_images_only") is True
        and rights.get("bnf_attribution") == "Bibliothèque nationale de France"
        and rights.get("bsb_rights") == "https://creativecommons.org/publicdomain/mark/1.0/",
    )

    resource_rows = worker.get("resource_rows", [])
    audit.check(
        "acquirer_deck_matches_profile",
        resource_rows == [list(row) for row in EXPECTED_ROWS],
    )
    acquirer_constants = worker.get("constants", {})
    audit.check(
        "acquirer_constants_match_profile",
        acquirer_constants
        == {
            "follow_redirects": False,
            "maximum_new_bnf_requests": 5,
            "maximum_new_bsb_requests": 5,
            "minimum_request_spacing_seconds": 4.0,
            "pillow_version": "10.2.0",
            "request_total_wall_seconds": 180,
            "response_cap_bytes": 50_000_000,
            "retries": 0,
            "socket_operation_timeout_seconds": 60,
            "success_status": SUCCESS,
            "total_body_cap_bytes": 500_000_000,
        }
        and tuple(worker.get("registered_paths", [])) == EXPECTED_RUNTIME_PATHS,
    )
    audit.check(
        "acquirer_accepts_exact_working_profile",
        worker_completed and worker.get("profile_accepted") is True,
    )
    expected_probe_events = {
        "socket.getaddrinfo",
        "socket.create_connection",
        "socket.socket.connect",
        "urllib.request.urlopen",
        "urllib.request.OpenerDirector.open",
    }
    audit.check(
        "isolated_worker_blocks_low_level_and_urllib_network",
        worker_completed
        and worker.get("status") == "PASS"
        and worker.get("guard_probes_ok") is True
        and set(worker.get("guard_probe_events", [])) == expected_probe_events
        and worker.get("network_attempts") == []
        and worker.get("process_attempts") == [],
    )
    self_test = worker.get("self_test", {})
    self_test_rows = self_test.get("checks", [])
    self_test_names = [row.get("name") for row in self_test_rows]
    audit.check(
        "acquirer_offline_selftest_passes",
        self_test.get("decision") == "PASS"
        and self_test.get("network_requests") == 0
        and len(self_test_names) == len(set(self_test_names))
        and REQUIRED_SELFTEST_CHECKS.issubset(set(self_test_names))
        and all(row.get("status") == "PASS" for row in self_test_rows),
    )
    audit.check(
        "registration_modules_have_no_top_level_network_call",
        top_level_network_calls(ROOT / RUN_REL) == []
        and top_level_network_calls(ROOT / ACQUIRER_REL) == []
        and top_level_network_calls(ROOT / VALIDATOR_REL) == [],
    )
    audit.check(
        "pillow_pin_exact",
        (ROOT / REQUIREMENTS_REL).read_text(encoding="utf-8") == "Pillow==10.2.0\n"
        and acquirer_constants.get("pillow_version") == "10.2.0",
    )

    docs = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            BASE_REL / "README.md",
            BASE_REL / "METHOD.md",
            BASE_REL / "PREREGISTRATION.md",
            BASE_REL / "artifacts/README.md",
        )
    }
    readme = docs[BASE_REL / "README.md"]
    method = docs[BASE_REL / "METHOD.md"]
    preregistration = docs[BASE_REL / "PREREGISTRATION.md"]
    artifact_readme = docs[BASE_REL / "artifacts/README.md"]
    normalized_readme = " ".join(readme.lower().split())
    normalized_method = " ".join(method.lower().split())
    normalized_preregistration = " ".join(preregistration.lower().split())
    normalized_artifact_readme = " ".join(artifact_readme.lower().split())
    audit.check(
        "documentation_status_consistent",
        all(STATUS in text for text in docs.values()),
    )
    combined_docs = "\n".join(docs.values()).lower()
    audit.check(
        "documentation_at_most_once_scope_exact",
        "at-most-once" in normalized_method
        and "per bound state directory, not a global network guarantee"
        in normalized_method
        and "at-most-once per execution state" in normalized_preregistration
        and "exactly once" not in combined_docs,
    )
    audit.check(
        "documentation_no_reading_and_sealed_boundary_exact",
        "registration performs no network access and opens no image"
        in normalized_readme
        and "neither displays nor reads the acquired pages" in normalized_method
        and "opens no source image or voynich material"
        in normalized_preregistration
        and "without displaying or reading them" in normalized_preregistration
        and "no source image" in normalized_artifact_readme
        and "voynich material" in normalized_artifact_readme
        and "f84" in combined_docs
        and "f84r" in combined_docs,
    )
    audit.check(
        "documentation_header_semantics_honest",
        "not a claim that the wire header set has only three members"
        in normalized_method
        and "no exact three-member wire-header set is claimed"
        in normalized_preregistration
        and all(term in combined_docs for term in ("host", "connection: close")),
    )

    all_entries = list(BASE.rglob("*"))
    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    special_or_symlink: list[str] = []
    for path in all_entries:
        relative = path.relative_to(BASE).as_posix()
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            special_or_symlink.append(relative)
        elif stat.S_ISREG(info.st_mode):
            actual_files.add(relative)
        elif stat.S_ISDIR(info.st_mode):
            actual_directories.add(relative)
        else:
            special_or_symlink.append(relative)
    audit.check(
        "registration_tree_exact_and_symlink_free",
        actual_files == EXPECTED_TREE_FILES
        and actual_directories == EXPECTED_TREE_DIRECTORIES
        and special_or_symlink == [],
    )
    audit.check(
        "no_private_runtime_file_image_or_pdf_retained",
        not any(private_path_name(relative) for relative in actual_files)
        and not any(
            Path(relative).suffix.lower()
            in {".bmp", ".gif", ".jp2", ".jpeg", ".jpg", ".pdf", ".png", ".tif", ".tiff", ".webp"}
            for relative in actual_files
        ),
    )
    working_privacy_findings: list[str] = []
    for relative in sorted(actual_files):
        working_privacy_findings.extend(
            privacy_findings((BASE / relative).read_bytes(), f"working:{relative}")
        )
    audit.check(
        "registration_working_tree_privacy_patterns_clean",
        working_privacy_findings == [],
    )
    audit.check(
        "exact_staged_tree_privacy_patterns_clean",
        staged_privacy_findings() == [],
    )

    audit.check(
        "manifest_identity_status_and_seals",
        manifest.get("schema_version") == 1
        and manifest.get("experiment_id") == "GDT620"
        and manifest.get("slug") == "stage_b_source_page_acquisition"
        and manifest.get("title") == "Stage-B source-page acquisition"
        and manifest.get("status") == STATUS
        and manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    audit.check(
        "manifest_question_claim_ceiling_and_artifact_policy_exact",
        manifest.get("question") == EXPECTED_QUESTION
        and manifest.get("claim_ceiling") == EXPECTED_CLAIM_CEILING
        and manifest.get("artifact_policy") == EXPECTED_ARTIFACT_POLICY,
    )
    audit.check("manifest_dependency_exact", manifest.get("dependencies") == ["GDT619"])
    audit.check(
        "manifest_commands_exact",
        manifest.get("commands")
        == {
            "run": f"python3 {RUN_REL} --check",
            "validate": f"python3 {VALIDATOR_REL} --check",
        },
    )
    audit.check(
        "manifest_validation_binding",
        manifest.get("validation") == {"artifact": str(VALIDATION_REL), "status": "PASS"},
    )
    inputs = manifest.get("inputs", [])
    outputs = manifest.get("outputs", [])
    audit.check(
        "manifest_path_sets_exact",
        {row.get("path") for row in inputs} == EXPECTED_INPUTS
        and len(inputs) == len(EXPECTED_INPUTS)
        and {row.get("path") for row in outputs} == EXPECTED_OUTPUTS
        and len(outputs) == len(EXPECTED_OUTPUTS),
    )
    nonvalidation = inputs + [row for row in outputs if row.get("path") != str(VALIDATION_REL)]
    audit.check(
        "manifest_nonvalidation_hashes_exact",
        all(
            isinstance(row.get("sha256"), str)
            and HEX64.fullmatch(row["sha256"]) is not None
            and (ROOT / row["path"]).is_file()
            and digest(ROOT / row["path"]) == row["sha256"]
            for row in nonvalidation
        ),
    )

    registered_payload = audit.payload()
    if args.print_artifact_template:
        print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if audit.passed else 1
    if args.write_artifact:
        if not audit.passed:
            print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
            return 1
        validation_path.write_bytes(canonical_bytes(registered_payload))
        print(f"WROTE {VALIDATION_REL} {digest(validation_path)}")
        return 0

    audit.check(
        "validation_artifact_matches_registered_payload",
        validation_path.is_file() and validation_path.read_bytes() == canonical_bytes(registered_payload),
    )
    validation_rows = [row for row in outputs if row.get("path") == str(VALIDATION_REL)]
    audit.check(
        "manifest_validation_artifact_hash_exact",
        len(validation_rows) == 1
        and validation_path.is_file()
        and digest(validation_path) == validation_rows[0].get("sha256"),
    )
    payload = audit.payload()
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
