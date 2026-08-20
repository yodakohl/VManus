#!/usr/bin/env python3
"""Canonicalize cross-designer scalar and physical-index conventions."""

from __future__ import annotations


def _binary(value: object, *, allow_none: bool) -> str:
    if value is None:
        return "NONE" if allow_none else "FALSE"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    text = str(value).strip().upper()
    if text in {"NONE", "NA", "N/A", ""}:
        if allow_none: return "NONE"
        return "FALSE"
    if text in {"FALSE", "NO", "0"}:
        return "FALSE"
    if text in {"TRUE", "YES", "1", "LIMITED"} or text.startswith("PM_"):
        return "TRUE"
    raise ValueError(f"cannot canonicalize binary value {value!r}")


def normalize_bundle(bundle: dict) -> dict:
    out = {k: [dict(r) for r in rows] for k, rows in bundle.items()}
    obs = out["observations"]
    role_map = {role: f"L{i}" for i, role in enumerate(sorted({str(r["layout_role"]) for r in obs}))}
    record_counts = {}
    paragraph_pages = {}
    for row in obs:
        paragraph_pages.setdefault(str(row["paragraph_id"]), set()).add(str(row["page_id"]))
    for i, row in enumerate(obs):
        rid = str(row["record_id"])
        row["corpus_seed"] = int(row["corpus_seed"])
        row["event_index"] = i
        row["group_index"] = record_counts.get(rid, 0); record_counts[rid] = row["group_index"] + 1
        row["ambiguous_boundary"] = _binary(row["ambiguous_boundary"], allow_none=False)
        row["layout_role"] = role_map[str(row["layout_role"])]
        pid = str(row["paragraph_id"])
        if len(paragraph_pages[pid]) > 1:
            row["paragraph_id"] = f"{row['page_id']}::{pid}"
    for i, row in enumerate(obs):
        row["separator_after"] = obs[i + 1]["separator_before"] if i + 1 < len(obs) else "PAGE"
    for row in out["oracle"]:
        row["productive_morphology"] = _binary(row["productive_morphology"], allow_none=True)
    return out


def validate_canonical(bundle: dict) -> None:
    obs, oracle = bundle["observations"], bundle["oracle"]
    if [r["event_index"] for r in obs] != list(range(len(obs))):
        raise ValueError("event_index not global monotone")
    for i, row in enumerate(obs):
        if row["ambiguous_boundary"] not in {"TRUE", "FALSE"}:
            raise ValueError("noncanonical ambiguous_boundary")
        if i + 1 < len(obs) and row["separator_after"] != obs[i + 1]["separator_before"]:
            raise ValueError("boundary mismatch")
    for rid in {r["record_id"] for r in obs}:
        values = [r["group_index"] for r in obs if r["record_id"] == rid]
        if values != list(range(len(values))):
            raise ValueError("group_index not record-local")
    parents = (("paragraph_id", "page_id"), ("record_id", "paragraph_id"), ("line_id", "record_id"))
    for child, parent in parents:
        mapping = {}
        for row in obs: mapping.setdefault(row[child], set()).add(row[parent])
        if any(len(v) != 1 for v in mapping.values()):
            raise ValueError(f"hierarchy not nested: {child}->{parent}")
    if any(r["productive_morphology"] not in {"TRUE", "FALSE", "NONE"} for r in oracle):
        raise ValueError("noncanonical productive_morphology")
