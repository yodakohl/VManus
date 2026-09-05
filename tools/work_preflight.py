#!/usr/bin/env python3
"""Focused publication checks against Git's index, never the working tree.

This complements, and does not replace, the strict repository preflight.
It does not run experiment validators or certify unrelated historical files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.repository_preflight import (
    CREDENTIAL_PATTERNS,
    LOCAL_PATH_PATTERNS,
    SENSITIVE_NAME_RE,
)
from tools.vmanus_experiment import validate_manifest_data

EXPERIMENT_PATH = re.compile(r"^experiments/yolo/gdt(\d{3,})_[a-z0-9][a-z0-9_-]*/")
EXPERIMENT_ID = re.compile(r"GDT\d{3,}\Z")
INDEX_PATH = "experiments/EXPERIMENT_INDEX.tsv"


def safe_relative(path: str) -> bool:
    candidate = PurePosixPath(path)
    return bool(candidate.parts) and not candidate.is_absolute() and candidate.as_posix() == path and all(
        part not in {".", ".."} for part in candidate.parts
    ) and not any(character in path for character in "\\*?[]\n\r\0")


class StagedTree:
    """Capture index identities; retrieve bytes by object ID to avoid worktree races."""

    def __init__(self, root: Path):
        self.root = root
        self.raw_index = self.git("ls-files", "--stage", "-z")
        self.entries: dict[str, tuple[str, str]] = {}
        for entry in self.raw_index.split(b"\0"):
            if not entry:
                continue
            metadata, raw_path = entry.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            if stage != "0":
                raise ValueError("unmerged index entries; resolve conflicts before checking")
            self.entries[raw_path.decode("utf-8")] = (mode, oid)
        self.changed = sorted(
            item.decode("utf-8") for item in self.git(
                "diff", "--cached", "--no-renames", "--name-only", "-z"
            ).split(b"\0") if item
        )
        self.hashes: dict[str, str] = {}

    def git(self, *args: str) -> bytes:
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout

    def read(self, path: str) -> bytes:
        mode, oid = self.entries[path]
        if mode not in {"100644", "100755"}:
            raise ValueError(f"non-regular index file: {path}")
        return self.git("cat-file", "blob", oid)

    def digest(self, path: str) -> str:
        if path not in self.hashes:
            # Raw manuscript bindings are hashed as opaque bytes, never parsed.
            self.hashes[path] = hashlib.sha256(self.read(path)).hexdigest()
        return self.hashes[path]


def _check_manifest(tree: StagedTree, path: str, available: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(tree.read(path))
        schema_errors = validate_manifest_data(data, Path(path))
        if schema_errors:
            return [f"{path}: {error}" for error in schema_errors]
        if not data["question"].strip() or not data["claim_ceiling"].strip():
            errors.append(f"{path}: publication question and claim ceiling must be nonempty")
        current = int(data["experiment_id"][3:])
        for dependency in data["dependencies"]:
            if dependency not in available:
                errors.append(f"{path}: missing indexed dependency {dependency}")
            elif int(dependency[3:]) >= current:
                errors.append(f"{path}: dependency is not earlier: {dependency}")
            else:
                source = available[dependency]
                pointer = source.get("manifest") or source.get("primary_report")
                if not pointer or pointer not in tree.entries:
                    errors.append(f"{path}: dependency missing from staged tree: {dependency}")
        bound: set[str] = set()
        for collection in ("inputs", "outputs"):
            for binding in data[collection]:
                target, expected = binding["path"], binding["sha256"]
                if not expected:
                    errors.append(f"{path}: unbound {collection[:-1]}: {target}")
                elif target not in tree.entries:
                    errors.append(f"{path}: missing staged-tree binding: {target}")
                elif tree.digest(target) != expected:
                    errors.append(f"{path}: staged-tree hash mismatch: {target}")
                else:
                    bound.add(target)
        for binding in data["outputs"]:
            target = binding["path"]
            if target not in bound or not (
                target.endswith("_result.json") or target.endswith("/result.json")
            ):
                continue
            result = json.loads(tree.read(target))
            if not isinstance(result, dict):
                errors.append(f"{path}: result artifact root must be an object: {target}")
                continue
            for family in ("document_hashes", "implementation_hashes"):
                bindings = result.get(family, {})
                if not isinstance(bindings, dict):
                    errors.append(f"{path}: {family} must be an object: {target}")
                    continue
                for target, expected in bindings.items():
                    if not safe_relative(target) or target not in tree.entries:
                        errors.append(f"{path}: unsafe or missing indirect binding: {target}")
                    elif tree.digest(target) != expected:
                        errors.append(f"{path}: indirect staged-tree hash mismatch: {target}")
                    else:
                        bound.add(target)
        prefix = path.rsplit("/", 1)[0] + "/"
        limit = data["artifact_policy"]["max_inline_bytes"]
        justification = data["artifact_policy"]["large_artifact_justification"].strip()
        for target in tree.entries:
            if not target.startswith(prefix):
                continue
            local = PurePosixPath(target[len(prefix):])
            required = (len(local.parts) == 1 and local.suffix == ".md") or (
                len(local.parts) == 2 and local.parts[0] == "src" and local.suffix == ".py"
            )
            if required and target not in bound:
                errors.append(f"{path}: unbound reproducibility file: {target}")
            if not justification and len(tree.read(target)) > limit:
                errors.append(f"{path}: oversized artifact lacks justification: {target}")
        artifact = data["validation"]["artifact"]
        if artifact and artifact not in tree.entries:
            errors.append(f"{path}: missing staged validation artifact: {artifact}")
    except (KeyError, ValueError, TypeError, UnicodeError) as exc:
        errors.append(f"{path}: invalid staged manifest or binding: {exc}")
    return errors


def run(*, root: Path = REPOSITORY_ROOT, experiments: tuple[str, ...] = (),
        includes: tuple[str, ...] = ()) -> dict:
    """Return an explicit task-scope result; strict global failures are not suppressed."""
    errors: list[str] = []
    selected = set(experiments)
    allowed = set(includes)
    if not selected and not allowed:
        errors.append("declare --experiment or exact --include paths; no implicit scope")
    for experiment in selected:
        if not EXPERIMENT_ID.fullmatch(experiment) or int(experiment[3:]) < 337:
            errors.append(f"invalid structured experiment selection: {experiment}")
    for path in allowed:
        if not safe_relative(path):
            errors.append(f"--include must be an exact repository-relative file path: {path}")
    tree = StagedTree(root)
    if not tree.changed:
        errors.append("no staged changes")
    manifests: dict[str, str] = {}
    for path in tree.entries:
        match = EXPERIMENT_PATH.match(path)
        if match and path.endswith("/experiment.json") and path.count("/") == 3:
            identifier = f"GDT{int(match.group(1)):03d}"
            if identifier in manifests:
                errors.append(f"duplicate staged-tree manifest ID: {identifier}")
            manifests[identifier] = path
    for path in tree.changed:
        match = EXPERIMENT_PATH.match(path)
        numbered = re.search(r"(?i)gdt(\d{3,})(?!\d)", path)
        if numbered and int(numbered.group(1)) <= 336:
            errors.append(f"byte-frozen legacy experiment path changed: {path}")
        elif numbered and not match:
            errors.append(f"changed experiment path violates structured layout: {path}")
        identifier = f"GDT{int(match.group(1)):03d}" if match else None
        if identifier and identifier not in selected:
            errors.append(f"changed experiment must be selected even with --include: {path}")
        if not (identifier in selected if identifier else path in allowed):
            errors.append(f"staged path outside declared task scope: {path}")
        if path not in tree.entries:  # Deletions remain subject to scope checks above.
            continue
        if SENSITIVE_NAME_RE.search(path):
            errors.append(f"sensitive staged filename: {path}")
        try:
            blob = tree.read(path)
            if any(pattern.search(blob) for pattern in CREDENTIAL_PATTERNS):
                errors.append(f"credential/private-key pattern in staged file: {path}")
            if any(pattern.search(blob) for pattern in LOCAL_PATH_PATTERNS):
                errors.append(f"private/local absolute path in staged file: {path}")
        except ValueError as exc:
            errors.append(str(exc))
    available: dict[str, dict] = {}
    if selected:
        if INDEX_PATH not in tree.entries:
            errors.append("experiment index missing from staged tree")
        else:
            for row in csv.DictReader(io.StringIO(tree.read(INDEX_PATH).decode()), delimiter="\t"):
                identifier = row.get("experiment_id", "")
                if identifier in available:
                    errors.append(f"duplicate staged experiment index ID: {identifier}")
                available[identifier] = row
        for identifier in sorted(selected):
            path = manifests.get(identifier)
            if not path:
                errors.append(f"selected experiment missing from staged tree: {identifier}")
                continue
            if available.get(identifier, {}).get("manifest") != path:
                errors.append(f"selected experiment index manifest mismatch: {identifier}")
            errors.extend(_check_manifest(tree, path, available))
    if tree.git("ls-files", "--stage", "-z") != tree.raw_index:
        errors.append("Git index changed during check; rerun against a stable index")
    return {
        "status": "TASK_STAGED_PREFLIGHT_FAIL" if errors else "TASK_STAGED_PREFLIGHT_PASS",
        "experiments": sorted(selected), "explicit_includes": sorted(allowed),
        "staged_paths": tree.changed, "errors": errors,
        "coverage": "all staged privacy/scope; selected manifest schema, seals, index membership, "
                    "direct dependency existence/order, bound bytes and reproducibility files",
        "not_checked": "global worktree/index rebuild, unrelated historical manifests, "
                       "recursive dependency hashes, experiment validators, manuscript meaning",
        "global_check": "NOT_RUN; run ./vmanus-exp check --all separately; this result does not clear its failures",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", action="append", default=[])
    parser.add_argument("--include", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        result = run(experiments=tuple(args.experiment), includes=tuple(args.include))
    except (ValueError, KeyError, UnicodeError, subprocess.CalledProcessError) as exc:
        print(f"TASK_STAGED_PREFLIGHT_FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
