"""Shared infrastructure for structured VManus experiments.

This module contains repository/path discovery, deterministic hashing/seeding,
manifest validation, and a TSV reader that selects on a raw field before
parsing the rest of a row. It contains no scientific model or Voynich parser.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPERIMENT_RE = re.compile(r"^GDT(\d{3,})$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
STRUCTURED_DIR_RE = re.compile(r"^gdt(\d{3,})_([a-z0-9][a-z0-9_-]*)$")
REQUIRED_MANIFEST_KEYS = {
    "schema_version",
    "experiment_id",
    "slug",
    "title",
    "status",
    "created",
    "updated",
    "question",
    "claim_ceiling",
    "sealed_data",
    "commands",
    "dependencies",
    "inputs",
    "outputs",
    "validation",
    "artifact_policy",
}


class ManifestError(ValueError):
    """Raised when a structured experiment manifest is invalid."""


class SealedDataError(RuntimeError):
    """Raised when a forbidden selector reaches a guarded source loader."""


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deterministic_seed(label: str, bits: int = 64) -> int:
    if bits < 8 or bits > 256 or bits % 8:
        raise ValueError("bits must be a multiple of eight between 8 and 256")
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[: bits // 8], "big")


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _relative_path(value: object, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a nonempty string")
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{field} must be repository-relative without '..': {value}")
        return None
    return value


def validate_manifest_data(data: object, manifest_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]
    keys = set(data)
    missing = REQUIRED_MANIFEST_KEYS - keys
    extra = keys - REQUIRED_MANIFEST_KEYS
    if missing:
        errors.append("missing keys: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown keys: " + ", ".join(sorted(extra)))
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")

    experiment_id = data.get("experiment_id")
    id_match = EXPERIMENT_RE.fullmatch(experiment_id) if isinstance(experiment_id, str) else None
    if not id_match:
        errors.append("experiment_id must match GDT followed by at least three digits")
    slug = data.get("slug")
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        errors.append("slug is invalid")
    for field in ("title", "status"):
        if not isinstance(data.get(field), str) or not data[field]:
            errors.append(f"{field} must be a nonempty string")
    for field in ("question", "claim_ceiling"):
        if not isinstance(data.get(field), str):
            errors.append(f"{field} must be a string")
    for field in ("created", "updated"):
        try:
            date.fromisoformat(data.get(field, ""))
        except (TypeError, ValueError):
            errors.append(f"{field} must be an ISO date")

    sealed = data.get("sealed_data")
    if not isinstance(sealed, dict) or sealed.get("f84r") != "FORBIDDEN":
        errors.append("sealed_data.f84r must equal FORBIDDEN")
    elif not all(isinstance(key, str) and isinstance(value, str) for key, value in sealed.items()):
        errors.append("sealed_data keys and values must be strings")
    if id_match and int(id_match.group(1)) >= 394:
        if not isinstance(sealed, dict) or sealed.get("f84") != "FORBIDDEN":
            errors.append("GDT394+ sealed_data.f84 must equal FORBIDDEN")

    commands = data.get("commands")
    if not isinstance(commands, dict) or set(commands) != {"run", "validate"}:
        errors.append("commands must contain exactly run and validate")
    elif not all(isinstance(value, str) and value.strip() for value in commands.values()):
        errors.append("run and validate commands must be nonempty strings")

    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be an array")
    elif len(dependencies) != len(set(item for item in dependencies if isinstance(item, str))):
        errors.append("dependencies must be unique strings")
    else:
        for item in dependencies:
            if not isinstance(item, str) or not EXPERIMENT_RE.fullmatch(item):
                errors.append(f"invalid dependency: {item!r}")

    for collection in ("inputs", "outputs"):
        bindings = data.get(collection)
        if not isinstance(bindings, list):
            errors.append(f"{collection} must be an array")
            continue
        seen: set[str] = set()
        for index, binding in enumerate(bindings):
            prefix = f"{collection}[{index}]"
            if not isinstance(binding, dict) or set(binding) != {"path", "role", "sha256"}:
                errors.append(f"{prefix} must contain exactly path, role, sha256")
                continue
            path = _relative_path(binding.get("path"), prefix + ".path", errors)
            if path in seen:
                errors.append(f"duplicate {collection} path: {path}")
            if path:
                seen.add(path)
            if not isinstance(binding.get("role"), str) or not binding["role"]:
                errors.append(f"{prefix}.role must be nonempty")
            digest = binding.get("sha256")
            if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
                errors.append(f"{prefix}.sha256 must be null or lowercase SHA-256")

    validation = data.get("validation")
    validation_status = None
    if not isinstance(validation, dict) or set(validation) != {"status", "artifact"}:
        errors.append("validation must contain exactly status and artifact")
    else:
        validation_status = validation.get("status")
        if validation_status not in {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}:
            errors.append("validation.status is invalid")
        artifact = validation.get("artifact")
        if artifact is not None:
            _relative_path(artifact, "validation.artifact", errors)

    policy = data.get("artifact_policy")
    if not isinstance(policy, dict) or set(policy) != {"max_inline_bytes", "large_artifact_justification"}:
        errors.append("artifact_policy must contain max_inline_bytes and large_artifact_justification")
    else:
        if not isinstance(policy.get("max_inline_bytes"), int) or policy["max_inline_bytes"] < 1:
            errors.append("artifact_policy.max_inline_bytes must be a positive integer")
        if not isinstance(policy.get("large_artifact_justification"), str):
            errors.append("artifact_policy.large_artifact_justification must be a string")

    if manifest_path is not None and id_match and isinstance(slug, str):
        directory_match = STRUCTURED_DIR_RE.fullmatch(manifest_path.parent.name)
        if not directory_match:
            errors.append("manifest directory must be named gdtNNN_slug")
        elif int(directory_match.group(1)) != int(id_match.group(1)) or directory_match.group(2) != slug:
            errors.append("manifest ID/slug do not match the containing directory")
        if manifest_path.name != "experiment.json":
            errors.append("manifest filename must be experiment.json")
    return errors


def load_manifest(path: Path, *, validate: bool = True) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if validate:
        errors = validate_manifest_data(data, path)
        if errors:
            raise ManifestError(f"{path}: " + "; ".join(errors))
    return data


def verify_manifest_bindings(data: dict, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for collection in ("inputs", "outputs"):
        for binding in data.get(collection, []):
            path = root / binding["path"]
            digest = binding.get("sha256")
            if digest is None:
                continue
            if not path.is_file():
                errors.append(f"missing {collection[:-1]}: {binding['path']}")
            elif sha256_file(path) != digest:
                errors.append(f"hash mismatch: {binding['path']}")
    validation = data.get("validation", {})
    artifact = validation.get("artifact")
    if artifact and not (root / artifact).is_file():
        errors.append(f"missing validation artifact: {artifact}")
    if validation.get("status") == "PASS":
        for collection in ("inputs", "outputs"):
            for binding in data.get(collection, []):
                if binding.get("sha256") is None:
                    errors.append(f"PASS manifest has unbound {collection[:-1]}: {binding['path']}")
        if not artifact:
            errors.append("PASS manifest must name validation.artifact")
    return errors


def manifest_paths(root: Path = ROOT) -> list[Path]:
    return sorted((root / "experiments/yolo").glob("gdt*/experiment.json"))


def format_ledger_row(fields: dict[str, str]) -> str:
    names = ("date", "experiment", "status", "live_scope", "forbidden_inference", "primary_report")
    missing = set(names) - set(fields)
    extra = set(fields) - set(names)
    if missing or extra:
        raise ValueError(f"ledger fields mismatch; missing={sorted(missing)} extra={sorted(extra)}")
    values: list[str] = []
    for name in names:
        value = fields[name]
        if not isinstance(value, str) or not value or "\t" in value or "\n" in value:
            raise ValueError(f"invalid ledger field {name}")
        values.append(value)
    date.fromisoformat(values[0])
    return "\t".join(values)


def _raw_tsv_field(line: str, index: int) -> str | None:
    start = 0
    current = 0
    while current < index:
        tab = line.find("\t", start)
        if tab < 0:
            return None
        start = tab + 1
        current += 1
    end = line.find("\t", start)
    if end < 0:
        end = len(line.rstrip("\r\n"))
    return line[start:end]


@dataclass
class GuardStats:
    lines_seen: int = 0
    selected: int = 0
    skipped_not_allowed: int = 0
    skipped_forbidden: int = 0


class GuardedTSV:
    """Parse only TSV rows whose raw selector field passes a frozen guard.

    The selector field is extracted by tab offsets before `csv.reader` sees the
    remainder of the row. Forbidden or non-whitelisted rows are therefore never
    materialized as parsed dictionaries.
    """

    def __init__(
        self,
        path: Path,
        *,
        selector_column: str,
        allowed_values: set[str] | None = None,
        forbidden_prefixes: tuple[str, ...] = ("f84",),
        forbidden_action: str = "skip",
    ) -> None:
        if forbidden_action not in {"skip", "error"}:
            raise ValueError("forbidden_action must be skip or error")
        self.path = path
        self.selector_column = selector_column
        self.allowed_values = allowed_values
        self.forbidden_prefixes = forbidden_prefixes
        self.forbidden_action = forbidden_action
        self.stats = GuardStats()

    def __iter__(self) -> Iterator[dict[str, str]]:
        with self.path.open(encoding="utf-8", newline="") as handle:
            header_line = handle.readline()
            if not header_line:
                return
            header = next(csv.reader([header_line], delimiter="\t"))
            if self.selector_column not in header:
                raise ValueError(f"missing selector column {self.selector_column!r} in {self.path}")
            selector_index = header.index(self.selector_column)
            for line_number, raw_line in enumerate(handle, start=2):
                self.stats.lines_seen += 1
                raw_selector = _raw_tsv_field(raw_line, selector_index)
                if raw_selector is None:
                    raise ValueError(f"short TSV row {self.path}:{line_number}")
                selector_values = next(csv.reader([raw_selector], delimiter="\t"))
                if len(selector_values) != 1:
                    raise ValueError(f"invalid selector field {self.path}:{line_number}")
                selector = selector_values[0]
                if selector.startswith(self.forbidden_prefixes):
                    self.stats.skipped_forbidden += 1
                    if self.forbidden_action == "error":
                        raise SealedDataError(
                            f"forbidden selector rejected before row parse: {self.path}:{line_number}"
                        )
                    continue
                if self.allowed_values is not None and selector not in self.allowed_values:
                    self.stats.skipped_not_allowed += 1
                    continue
                values = next(csv.reader([raw_line], delimiter="\t"))
                if len(values) != len(header):
                    raise ValueError(f"TSV width mismatch {self.path}:{line_number}")
                self.stats.selected += 1
                yield dict(zip(header, values))
