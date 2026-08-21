#!/usr/bin/env python3
"""Build the R4 identity-hidden target packet, then reveal only after a freeze.

The source is accessed exclusively through the guarded selector.  ``mask``
never writes or prints an exact tuple, surface, wrapper, or family label.
``reveal`` recomputes the same selection and refuses to run unless the role
freeze names all and only the masked occurrence IDs and records its hash.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
MASK = OUT / "V15_R4_PRE_REVEAL_MASKED_OCCURRENCES.tsv"
FREEZE = OUT / "V15_R4_PRE_REVEAL_VISUAL_ROLE_FREEZE.tsv"
META = OUT / "V15_R4_PRE_REVEAL_FREEZE.json"
JOIN = OUT / "V15_R4_POST_REVEAL_VALUE_ROLE_JOIN.tsv"
PAGES = ("f81v", "f82r", "f83r")
ROLES = {
    "FIGURE_OR_BODY",
    "VESSEL_POOL_OR_CONTAINER",
    "CONDUIT_PATH_OR_FLOW",
    "JUNCTION_OR_INTERMEDIATE_STATION",
    "TERMINAL_OUTLET_OR_ENDPOINT",
    "GENERAL_CONFIGURATION_OR_PAGE_OWNER",
    "VISUALLY_UNOWNED",
}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def guarded_rows() -> list[dict[str, str]]:
    columns = [
        "event_id_sha256", "page", "locus", "group_index", "group_count",
        "record_ordinal", "field_ordinal", "within_field_position",
        "joint_tuple_id", "host_id", "coordinate_id", "observed_wrapper",
        "dy_closure", "b3",
    ]
    cmd = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
        "--selector", "page",
    ]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(columns)]
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 281:
        raise SystemExit(f"expected 281 guarded Bio events, got {len(rows)}")
    return rows


def guarded_surfaces() -> dict[tuple[str, str, str, str, str], dict[str, str]]:
    columns = [
        "page", "locus", "record_ordinal", "field_ordinal",
        "within_field_position", "raw_token", "wrapper",
    ]
    cmd = [
        str(ROOT / "vmanus-exp"), "query-tsv",
        str(ROOT / "gdt276_event_inventory.tsv"), "--selector", "page",
    ]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(columns)]
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 281:
        raise SystemExit(f"expected 281 guarded Bio surfaces, got {len(rows)}")
    return {
        (r["page"], r["locus"], r["record_ordinal"], r["field_ordinal"],
         r["within_field_position"]): r for r in rows
    }


def locus_key(locus: str) -> tuple[int, int]:
    page, line = locus.split(".", 1)
    return PAGES.index(page), int(line)


def selection(rows: list[dict[str, str]]) -> list[tuple[str, dict[str, str], int]]:
    eligible = [r for r in rows if r["dy_closure"] == "1" and r["b3"] == "0"]
    counts = Counter(r["joint_tuple_id"] for r in eligible)
    leaders = sorted(counts, key=lambda x: (-counts[x], x))[:4]
    leader_counts = sorted((counts[x] for x in leaders), reverse=True)
    if leader_counts != [12, 10, 8, 8]:
        raise SystemExit(f"unexpected four-family frequencies: {leader_counts}")
    target = [r for r in eligible if r["joint_tuple_id"] in set(leaders)]
    field_lengths: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for r in rows:
        field_lengths[(r["page"], r["locus"], r["record_ordinal"], r["field_ordinal"])] += 1
    target.sort(key=lambda r: (
        locus_key(r["locus"]), int(r["record_ordinal"]),
        int(r["field_ordinal"]), int(r["group_index"]),
        r["event_id_sha256"],
    ))
    return [
        (f"R4O{i:02d}", r,
         field_lengths[(r["page"], r["locus"], r["record_ordinal"], r["field_ordinal"])])
        for i, r in enumerate(target, 1)
    ]


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def do_mask() -> None:
    chosen = selection(guarded_rows())
    public = []
    for oid, r, field_len in chosen:
        pos_class = r["within_field_position"]
        public.append({
            "occurrence_id": oid,
            "page": r["page"],
            "locus": r["locus"],
            "record_ordinal": r["record_ordinal"],
            "field_ordinal": r["field_ordinal"],
            "field_length": field_len,
            "within_field_position": pos_class,
            "field_position_class": pos_class,
        })
    fields = list(public[0])
    write_tsv(MASK, fields, public)
    print(f"wrote identity-hidden packet: {MASK.name}; rows={len(public)}")
    print(f"sha256={hashlib.sha256(MASK.read_bytes()).hexdigest()}")


def validate_freeze(masked: list[dict[str, str]], frozen: list[dict[str, str]]) -> None:
    if [r["occurrence_id"] for r in frozen] != [r["occurrence_id"] for r in masked]:
        raise SystemExit("freeze IDs/order do not exactly match masked packet")
    for row in frozen:
        if row["visual_role"] not in ROLES:
            raise SystemExit(f"invalid role for {row['occurrence_id']}")
        if row["confidence"] not in CONFIDENCE or not row["ownership_rationale"].strip():
            raise SystemExit(f"incomplete freeze row {row['occurrence_id']}")


def do_seal() -> None:
    if not FREEZE.exists():
        raise SystemExit("role freeze missing; seal refused")
    masked = list(csv.DictReader(MASK.open(encoding="utf-8"), delimiter="\t"))
    frozen = list(csv.DictReader(FREEZE.open(encoding="utf-8"), delimiter="\t"))
    validate_freeze(masked, frozen)
    mask_sha = hashlib.sha256(MASK.read_bytes()).hexdigest()
    freeze_sha = hashlib.sha256(FREEZE.read_bytes()).hexdigest()
    metadata = {
        "agent": "R4_CHANCERY_CORRECTOR",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "masked_packet_sha256": mask_sha,
        "role_freeze_sha256": freeze_sha,
        "rows": len(frozen),
        "sealed_pages": ["f84", "f84r"],
        "identity_visible_before_freeze": "LIMITED_DISCOVERY_LEAK",
        "identity_leak_note": (
            "A broad filename/context discovery grep briefly displayed two old "
            "family hashes and some historical surface examples before masking; "
            "it did not expose the new neutral occurrence-ID mapping or any "
            "visual-role association."
        ),
    }
    META.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")

    print(f"freeze sealed: {freeze_sha}")


def do_reveal() -> None:
    if not META.exists():
        raise SystemExit("freeze metadata missing; run seal before reveal")
    masked = list(csv.DictReader(MASK.open(encoding="utf-8"), delimiter="\t"))
    frozen = list(csv.DictReader(FREEZE.open(encoding="utf-8"), delimiter="\t"))
    validate_freeze(masked, frozen)
    metadata = json.loads(META.read_text(encoding="utf-8"))
    if metadata.get("masked_packet_sha256") != hashlib.sha256(MASK.read_bytes()).hexdigest():
        raise SystemExit("masked packet changed after freeze")
    freeze_sha = hashlib.sha256(FREEZE.read_bytes()).hexdigest()
    if metadata.get("role_freeze_sha256") != freeze_sha:
        raise SystemExit("role map changed after freeze")

    chosen = selection(guarded_rows())
    family_order = sorted({r["joint_tuple_id"] for _, r, _ in chosen})
    # Neutral labels are assigned by descending frequency, then opaque ID only
    # as a deterministic tie-break; the opaque IDs themselves are never emitted.
    freq = Counter(r["joint_tuple_id"] for _, r, _ in chosen)
    family_order.sort(key=lambda x: (-freq[x], x))
    labels = {value: f"VAL-{chr(65 + i)}" for i, value in enumerate(family_order)}
    surfaces = guarded_surfaces()
    freeze_by_id = {r["occurrence_id"]: r for r in frozen}
    joined = []
    for oid, r, field_len in chosen:
        f = freeze_by_id[oid]
        surface = surfaces[(r["page"], r["locus"], r["record_ordinal"],
                            r["field_ordinal"], r["within_field_position"])]
        joined.append({
            "occurrence_id": oid,
            "page": r["page"], "locus": r["locus"],
            "record_ordinal": r["record_ordinal"],
            "field_ordinal": r["field_ordinal"],
            "field_length": field_len,
            "within_field_position": r["within_field_position"],
            "value_family": labels[r["joint_tuple_id"]],
            "surface": surface["raw_token"],
            "wrapper": surface["wrapper"],
            "visual_role": f["visual_role"],
            "confidence": f["confidence"],
            "ownership_rationale": f["ownership_rationale"],
        })
    write_tsv(JOIN, list(joined[0]), joined)
    print(f"wrote post-reveal join: {JOIN.name}; rows={len(joined)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("mask", "seal", "reveal"))
    args = parser.parse_args()
    if args.mode == "mask":
        do_mask()
    elif args.mode == "seal":
        do_seal()
    else:
        do_reveal()


if __name__ == "__main__":
    main()
