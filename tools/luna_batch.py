"""Small, read-only handoff helper for bounded Luna worker batches.

This module validates a packet, emits a task-scoped brief, or collects task
output JSON.  It never starts jobs and does not interpret result content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MEANING = (
    "Handoff administration only: this tool does not execute work, validate "
    "scientific content or semantic claims, or alter the ideas registry."
)


def _safe_relative(root: Path, value: Any, *, allow_missing: bool = True) -> Path:
    """Resolve a repository relative path, rejecting traversal and symlinks."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("path must be a non-empty repository-relative string")
    posix = PurePosixPath(value)
    if posix.is_absolute() or str(posix) != value or "." in posix.parts or ".." in posix.parts:
        raise ValueError("path must be normalized and repository-relative")
    root = root.resolve()
    current = root
    for part in posix.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("symlink paths are not allowed")
        if not current.exists():
            if not allow_missing:
                raise ValueError("path does not exist")
            break
    resolved = (root / Path(*posix.parts)).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes repository root") from exc
    return root / Path(*posix.parts)


def _packet_path(root: Path, value: str) -> tuple[Path, str]:
    """Require the packet argument itself to be a safe repository path."""
    if Path(value).is_absolute():
        raise ValueError("packet path must be repository-relative")
    path = _safe_relative(root, value, allow_missing=False)
    return path, PurePosixPath(value).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _string_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{field} must be a list")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} must contain non-empty strings")
    return value


def _validate_document(root: Path, packet: Any, *, packet_path: str | None = None) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")
    if packet.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for field in ("purpose", "claim_ceiling", "output_dir"):
        if not isinstance(packet.get(field), str) or not packet[field]:
            raise ValueError(f"{field} must be a non-empty string")

    selectors = _string_list(packet.get("allowed_selectors"), "allowed_selectors")
    for selector in selectors:
        lowered = selector.lower()
        if lowered == "f116v" or lowered.startswith("f84"):
            raise ValueError("sealed selector is not allowed")

    output_dir = _safe_relative(root, packet["output_dir"])
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError("output_dir must name a directory")

    inputs = packet.get("inputs")
    if not isinstance(inputs, list):
        raise ValueError("inputs must be a list")
    input_map: dict[str, dict[str, str]] = {}
    for row in inputs:
        if not isinstance(row, dict):
            raise ValueError("each input must be an object")
        path_value, digest, role = row.get("path"), row.get("sha256"), row.get("role")
        path = _safe_relative(root, path_value, allow_missing=False)
        if not path.is_file():
            raise ValueError("input path must be a regular file")
        if (not isinstance(digest, str) or len(digest) != 64 or
                digest != digest.lower() or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError("input sha256 must be 64 lowercase hexadecimal characters")
        if not isinstance(role, str) or not role:
            raise ValueError("input role must be a non-empty string")
        key = PurePosixPath(path_value).as_posix()
        if key in input_map:
            raise ValueError("duplicate input path")
        actual = _sha256(path)
        if actual != digest:
            raise ValueError("input sha256 does not match file")
        input_map[key] = {"path": key, "sha256": digest, "role": role}

    tasks = packet.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    task_map: dict[str, dict[str, Any]] = {}
    output_paths: set[str] = set()
    output_prefix = PurePosixPath(packet["output_dir"])
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("each task must be an object")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task id must be a non-empty string")
        if task_id in task_map:
            raise ValueError("duplicate task id")
        for field in ("owner", "question", "output_path"):
            if not isinstance(task.get(field), str) or not task[field]:
                raise ValueError(f"task {field} must be a non-empty string")
        task_inputs = _string_list(task.get("input_paths"), "task input_paths")
        if any(path not in input_map for path in task_inputs):
            raise ValueError(f"task {task_id} references an unbound input")
        required = _string_list(task.get("required_result_fields"), "required_result_fields")
        output_value = task["output_path"]
        output = _safe_relative(root, output_value)
        output_key = PurePosixPath(output_value).as_posix()
        if output_key in input_map or (packet_path is not None and output_key == packet_path):
            raise ValueError(f"task {task_id} output collides with a bound file")
        try:
            PurePosixPath(output_key).relative_to(output_prefix)
        except ValueError as exc:
            raise ValueError(f"task {task_id} output is outside output_dir") from exc
        if output_key in output_paths:
            raise ValueError("duplicate task output path")
        output_paths.add(output_key)
        task_map[task_id] = task

    return {"packet": packet, "inputs": input_map, "tasks": task_map,
            "output_dir": output_dir}


def load_packet(packet_arg: str, *, root: Path = ROOT) -> tuple[dict[str, Any], str]:
    path, display = _packet_path(root, packet_arg)
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("unable to read valid packet JSON") from exc
    return _validate_document(root, packet, packet_path=display), display


def _result_field(result: dict[str, Any], field: str) -> bool:
    current: Any = result
    for component in field.split("."):
        if not isinstance(current, dict) or component not in current:
            return False
        current = current[component]
    return True


def _evidence_ok(root: Path, value: Any, task: dict[str, Any], data: dict[str, Any]) -> bool:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        return False
    bound = set(task["input_paths"])
    output_prefix = PurePosixPath(data["packet"]["output_dir"])
    for item in value:
        try:
            evidence_path = _safe_relative(root, item, allow_missing=False)
            if not evidence_path.is_file():
                return False
            normalized = PurePosixPath(item).as_posix()
        except ValueError:
            return False
        if normalized in bound:
            continue
        try:
            PurePosixPath(normalized).relative_to(output_prefix)
        except ValueError:
            return False
    return True


def collect(data: dict[str, Any], *, root: Path = ROOT, display: str = "PACKET") -> dict[str, Any]:
    rows = []
    for task_id, task in data["tasks"].items():
        output = _safe_relative(root, task["output_path"])
        row: dict[str, Any] = {"id": task_id, "output_path": task["output_path"]}
        if not output.exists():
            row["status"] = "PENDING"
        else:
            try:
                if not output.is_file():
                    raise ValueError("output is not a regular file")
                result = json.loads(output.read_text(encoding="utf-8"))
                if not isinstance(result, dict):
                    raise ValueError("result must be an object")
                missing = [field for field in task["required_result_fields"]
                           if not _result_field(result, field)]
                if missing:
                    raise ValueError("required result fields are missing")
                if "evidence_paths" in result and not _evidence_ok(root, result["evidence_paths"], task, data):
                    raise ValueError("evidence_paths are outside bound inputs/output_dir")
                row["status"] = "DONE"
                row["result"] = result
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError):
                row["status"] = "INVALID"
        rows.append(row)
    statuses = {row["status"] for row in rows}
    overall = "INVALID" if "INVALID" in statuses else "PENDING" if "PENDING" in statuses else "DONE"
    return {"status": overall, "packet": display, "meaning": MEANING, "tasks": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="luna_batch", description=MEANING)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (for fixtures)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "brief", "collect"):
        sub = subparsers.add_parser(command)
        sub.add_argument("packet")
        sub.add_argument("--root", dest="sub_root", type=Path, default=None,
                         help="repository root (for fixtures)")
        if command == "brief":
            sub.add_argument("task_id")
    args = parser.parse_args(argv)
    root = (args.sub_root or args.root).resolve()
    try:
        data, display = load_packet(args.packet, root=root)
        if args.command == "validate":
            output = {"status": "VALID", "packet": display, "meaning": MEANING,
                      "input_count": len(data["inputs"]), "task_count": len(data["tasks"])}
        elif args.command == "brief":
            if args.task_id not in data["tasks"]:
                raise ValueError("unknown task id")
            task = data["tasks"][args.task_id]
            output = {"status": "READY", "packet": display, "meaning": MEANING,
                      "purpose": data["packet"]["purpose"],
                      "claim_ceiling": data["packet"]["claim_ceiling"],
                      "allowed_selectors": data["packet"]["allowed_selectors"],
                      "task": task,
                      "bound_inputs": [data["inputs"][path] for path in task["input_paths"]]}
        else:
            output = collect(data, root=root, display=display)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "meaning": MEANING,
                          "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["status"] in {"VALID", "READY", "DONE", "PENDING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
