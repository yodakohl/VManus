#!/usr/bin/env python3
"""Repository, manifest, seal, and exact staged-tree preflight checks."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.vmanus_experiment import (
    ROOT,
    load_manifest,
    manifest_paths,
    sha256_file,
    validate_manifest_data,
    verify_manifest_bindings,
)


CREDENTIAL_PATTERNS = [
    re.compile(rb"BEGIN (?:RSA|EC|OPENSSH|DSA) PRIVATE KEY"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"ASIA[0-9A-Z]{16}"),
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"sk-[A-Za-z0-9]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]+"),
    re.compile(rb"(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]", re.I),
]
LOCAL_PATH_PATTERNS = [
    re.compile(rb"/" + rb"home/[^\s]+"),
    re.compile(rb"/" + rb"Users/[^\s]+"),
    re.compile(rb"[A-Za-z]:\\Users\\[^\s]+"),
    re.compile(rb"/" + rb"tmp/[^\s]+"),
]
SENSITIVE_NAME_RE = re.compile(r"(?:^|/)(?:\.env|id_rsa|id_ed25519|.*\.(?:pem|p12|pfx|key))$", re.I)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=text, stdout=subprocess.PIPE
    )


def staged_paths() -> list[str]:
    output = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").stdout
    return [line for line in output.splitlines() if line]


def staged_blob(path: str) -> bytes:
    return git("show", f":{path}", text=False).stdout


def check_staged_privacy(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if SENSITIVE_NAME_RE.search(path):
            errors.append(f"sensitive staged filename: {path}")
            continue
        data = staged_blob(path)
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(data):
                errors.append(f"credential/private-key pattern in staged file: {path}")
                break
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(data):
                errors.append(f"private/local absolute path in staged file: {path}")
                break
    return errors


def visible_paths() -> list[str]:
    output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    return sorted(set(line for line in output.splitlines() if line))


def check_structured_layout(paths: list[str]) -> list[str]:
    errors: list[str] = []
    future = re.compile(r"(?i)gdt(\d{3,})(?!\d)")
    valid = re.compile(r"^experiments/yolo/gdt(\d{3,})_[a-z0-9][a-z0-9_-]*/")
    directories: set[str] = set()
    for path in paths:
        match = future.search(path)
        if not match or int(match.group(1)) < 337:
            continue
        layout = valid.match(path)
        if not layout or int(layout.group(1)) != int(match.group(1)):
            errors.append(f"GDT{int(match.group(1)):03d} path violates structured layout: {path}")
        else:
            directories.add(path.split("/", 3)[2])
    for directory in sorted(directories):
        manifest = f"experiments/yolo/{directory}/experiment.json"
        if manifest not in paths:
            errors.append(f"structured experiment lacks experiment.json: {directory}")
    return errors


def check_ledger() -> list[str]:
    path = ROOT / "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
    expected = ["date", "experiment", "status", "live_scope", "forbidden_inference", "primary_report"]
    errors: list[str] = []
    if reader.fieldnames != expected:
        errors.append("active ledger schema mismatch")
    for index, row in enumerate(rows, start=2):
        if None in row or any(row.get(name, "") == "" for name in expected):
            errors.append(f"active ledger malformed row {index}")
    return errors


def check_current_route() -> list[str]:
    path = ROOT / "VOYNICH_CURRENT_ROUTE.md"
    if not path.is_file():
        return ["VOYNICH_CURRENT_ROUTE.md missing"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    lines = text.count("\n") + 1
    if lines > 300:
        errors.append(f"current route exceeds 300-line cap: {lines}")
    if len(text.encode()) > 50_000:
        errors.append("current route exceeds 50,000-byte cap")
    for literal in ("Confirmed English lexemes: **0**", "f84r is sealed", "GDT327", "GDT336"):
        if literal not in text:
            errors.append(f"current route missing required literal: {literal}")
    for reference in re.findall(r"`([^`]+\.(?:md|tsv|json|py))`", text, flags=re.I):
        if not (ROOT / reference).exists():
            errors.append(f"current route reference missing: {reference}")
    return errors


def check_navigation_links() -> list[str]:
    errors: list[str] = []
    documents = [
        ROOT / "README.md",
        ROOT / "experiments/EXPERIMENT_INDEX.md",
        ROOT / "experiments/yolo/README.md",
    ]
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]*\]\(([^)#]+)", text):
            if "://" in target:
                continue
            if not (document.parent / target).resolve().exists():
                errors.append(f"broken local link in {document.relative_to(ROOT)}: {target}")
    return errors


def check_manifests() -> list[str]:
    errors: list[str] = []
    for path in manifest_paths():
        try:
            data = load_manifest(path)
        except Exception as exc:  # compact error aggregation for the preflight
            errors.append(str(exc))
            continue
        errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in verify_manifest_bindings(data))
        errors.extend(check_reproducibility_bindings(data, path))
        policy = data["artifact_policy"]
        experiment_dir = path.parent
        large = [
            item for item in experiment_dir.rglob("*")
            if item.is_file() and item.stat().st_size > policy["max_inline_bytes"]
        ]
        if large and not policy["large_artifact_justification"].strip():
            errors.append(
                f"{path.relative_to(ROOT)}: large artifacts lack justification: "
                + ", ".join(str(item.relative_to(ROOT)) for item in large)
            )
    return errors


def check_reproducibility_bindings(
    data: dict,
    manifest_path: Path,
    root: Path = ROOT,
) -> list[str]:
    """Require every experiment document and source file to be hash-bound.

    Most structured experiments bind these files directly in the manifest.
    A compact result may instead carry ``document_hashes`` and
    ``implementation_hashes``; those indirect bindings are independently
    verified here.
    """

    errors: list[str] = []
    bound = {
        item["path"]
        for collection in ("inputs", "outputs")
        for item in data.get(collection, [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for item in data.get("outputs", []):
        raw_path = item.get("path", "") if isinstance(item, dict) else ""
        if not (raw_path.endswith("_result.json") or raw_path.endswith("/result.json")):
            continue
        result_path = root / raw_path
        if not result_path.is_file():
            continue
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        for family in ("document_hashes", "implementation_hashes"):
            bindings = result.get(family)
            if not isinstance(bindings, dict):
                continue
            for raw_bound_path, digest in bindings.items():
                candidate = Path(raw_bound_path)
                if candidate.is_absolute() or ".." in candidate.parts:
                    errors.append(f"{result_path.relative_to(root)}: unsafe {family} path")
                    continue
                full_path = root / candidate
                if not full_path.is_file():
                    errors.append(f"{result_path.relative_to(root)}: missing {family} file {candidate}")
                    continue
                if not isinstance(digest, str) or sha256_file(full_path) != digest:
                    errors.append(f"{result_path.relative_to(root)}: {family} hash mismatch {candidate}")
                    continue
                bound.add(candidate.as_posix())

    experiment_dir = manifest_path.parent
    required = sorted((*experiment_dir.glob("*.md"), *experiment_dir.glob("src/*.py")))
    for path in required:
        relative = path.relative_to(root).as_posix()
        if relative not in bound:
            errors.append(f"{manifest_path.relative_to(root)}: unbound reproducibility file {relative}")
    return errors


def run_index_check() -> list[str]:
    result = subprocess.run(
        [sys.executable, "tools/build_experiment_index.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return [] if result.returncode == 0 else ["experiment index/layout check failed: " + result.stdout.strip()]


def run(*, require_staged: bool = False, all_files: bool = False) -> list[str]:
    errors: list[str] = []
    errors.extend(check_current_route())
    errors.extend(check_navigation_links())
    errors.extend(check_ledger())
    errors.extend(check_structured_layout(visible_paths()))
    errors.extend(check_manifests())
    errors.extend(run_index_check())
    staged = staged_paths()
    if require_staged and not staged:
        errors.append("no staged files for exact-tree privacy scan")
    if staged:
        errors.extend(check_staged_privacy(staged))
    if all_files:
        for path in manifest_paths():
            errors.extend(validate_manifest_data(load_manifest(path, validate=False), path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-staged", action="store_true")
    parser.add_argument("--all", action="store_true", help="CI/full structured-tree mode")
    args = parser.parse_args()
    errors = run(require_staged=args.require_staged, all_files=args.all)
    if errors:
        for error in errors:
            print("FAIL", error)
        return 1
    print("REPOSITORY_PREFLIGHT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
