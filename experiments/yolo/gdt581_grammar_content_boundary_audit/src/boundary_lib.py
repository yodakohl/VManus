#!/usr/bin/env python3
"""Shared deterministic helpers for GDT581."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
OBJECT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
GRADE_ROOTS = {"E", "EE", "EEE"}
STATE_ROOTS = {"OT", "OL", "DY"}
LOCAL_MACRO_ROOTS = {
    "CFH", "CHEO", "CHK", "CKH", "CPH", "CTH",
    "LOCAL_SIGN_C", "LOCAL_SIGN_X", "SECTION_MARKER",
}
RUNNING_SPECIAL_ROOTS = {"LOCAL_X", "RESUME_CARD"}

ACTION_NOMINALS = {
    "OK": "Setzen",
    "CH": "Entnehmen",
    "SH": "Halten",
    "K": "Zuordnen",
    "S": "Wählen",
    "CHD": "Bearbeiten",
    "T": "Festlegen",
    "R": "Kennzeichnen",
    "P": "Einsetzen",
}

RUNNING_MODIFIER_ROOTS = {
    "AM_ADDR", "AN", "A_ADDR", "CARRIER_Q", "DA", "D_ADDR", "D_LABEL",
    "E", "EE", "EEE", "G_LABEL", "HO", "IIN", "LOCAL_CHAR_B",
    "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_J",
    "M_LOCAL", "O", "OS", "S_ADDR",
}

STATUS = (
    "PASS_15889_COMPLETE_SLOTS__13702_CONTENT_CARRIERS__2187_CONTROL_SLOTS__"
    "4026_INHERITED_ALIASES__5672_FOCUS_HOSTS__8_FINAL_RECIPE_RECONCILIATIONS__"
    "269_FOCUS_VOICE_REPAIRS__232_EVENT_REPAIRS__2_SAFE_EXPLICIT_REMOTE_SLOTS__"
    "744_LOCAL_CARD_HOSTS__1973_LOCAL_COMPONENTS__107_NAME_SLOTS__"
    "ZERO_UNOWNED_SLOTS__5122_EXACT_ROUNDTRIPS"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty table: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_index(
    rows: Iterable[dict[str, str]], key: str, label: str
) -> dict[str, dict[str, str]]:
    rows = list(rows)
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {label} identity")
    return result


def atoms(recipe: str) -> list[str]:
    return [] if recipe in {"", "NONE"} else recipe.split("+")


def occurrence_rank(parts: list[str], root: str, position_one_based: int) -> int:
    if position_one_based < 1 or position_one_based > len(parts):
        raise RuntimeError(f"Atom position {position_one_based} outside recipe")
    if parts[position_one_based - 1] != root:
        raise RuntimeError(
            f"Expected {root} at {position_one_based}, found {parts[position_one_based - 1]}"
        )
    return sum(atom == root for atom in parts[:position_one_based])


def nth_position(parts: list[str], root: str, rank: int) -> int | None:
    seen = 0
    for position, atom in enumerate(parts, 1):
        if atom == root:
            seen += 1
            if seen == rank:
                return position
    return None


def action_positions(parts: list[str]) -> list[tuple[int, str]]:
    return [
        (position, root)
        for position, root in enumerate(parts, 1)
        if root in ACTION_ROOTS
    ]


def nearest_action(
    parts: list[str], focus_position: int, prefer: str = "LEFT_TIE"
) -> tuple[int, str] | None:
    candidates = action_positions(parts)
    if not candidates:
        return None
    if prefer == "RIGHT_TIE":
        return min(candidates, key=lambda item: (abs(item[0] - focus_position), -item[0]))
    return min(candidates, key=lambda item: (abs(item[0] - focus_position), item[0]))


def content_boundary_class(root: str, layer: str) -> tuple[str, str]:
    prefix = "RUNNING" if layer == "RUNNING" else "LOCAL"
    if root in ACTION_ROOTS:
        return f"{prefix}_ACTION_FUNCTION", "CONTENT_CARRIER"
    if root in OBJECT_ROOTS:
        return f"{prefix}_OBJECT_FUNCTION", "CONTENT_CARRIER"
    if root in RELATION_ROOTS:
        return f"{prefix}_RELATION_FUNCTION", "CONTENT_CARRIER"
    if root in GRADE_ROOTS or (
        layer == "RUNNING" and root in RUNNING_MODIFIER_ROOTS
    ):
        return f"{prefix}_MODIFIER_FUNCTION", "CONTENT_CARRIER"
    if root in STATE_ROOTS:
        return f"{prefix}_STATE_CONTROL", "CONTROL_HOST_ONLY"
    if layer == "RUNNING" and root == "LOCAL_X":
        return "RUNNING_LEARNED_CORE", "CONTENT_CARRIER"
    if layer == "RUNNING" and root == "RESUME_CARD":
        return "RUNNING_RESUMPTION_CONTROL", "CONTROL_HOST_ONLY"
    if layer == "LOCAL" and root in LOCAL_MACRO_ROOTS:
        return "LOCAL_MACRO_OR_SIGN_CONTROL", "CONTROL_HOST_ONLY"
    if layer == "LOCAL":
        return "LOCAL_MODIFIER_FUNCTION", "CONTENT_CARRIER"
    raise RuntimeError(f"Unclassified {layer} root: {root}")


def extract_name_slots(surface: str, template: str) -> list[tuple[str, str]]:
    placeholders = re.findall(r"\{(NAME_[0-9]+)\}", template)
    if not placeholders:
        return []
    chunks = re.split(r"\{NAME_[0-9]+\}", template)
    pattern = "^"
    for index, chunk in enumerate(chunks):
        pattern += re.escape(chunk)
        if index < len(placeholders):
            pattern += "(.+?)"
    pattern += "$"
    match = re.match(pattern, surface)
    if not match:
        raise RuntimeError(f"Template {template!r} does not match surface {surface!r}")
    return list(zip(placeholders, match.groups()))
