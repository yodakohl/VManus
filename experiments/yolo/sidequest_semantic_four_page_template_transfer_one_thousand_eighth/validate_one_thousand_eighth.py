#!/usr/bin/env python3
"""Validate the Pass-1008 four-page template transfer."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = HERE / "PASS1008_1413_EVENT_TRANSFER.tsv"
LOCI = HERE / "PASS1008_215_LOCUS_EDITION.tsv"
STATEMENTS = HERE / "PASS1008_STATEMENT_TEMPLATE_EDITION.tsv"
OWNERS = HERE / "PASS1008_VISUAL_OWNER_MAP.tsv"
SURFACES = HERE / "PASS1008_SURFACE_TRANSFER_DICTIONARY.tsv"
PROFILES = HERE / "PASS1008_FOUR_PAGE_TEMPLATE_PROFILE.tsv"
IMAGES = HERE / "PASS1008_IMAGE_MANIFEST.tsv"
UNIFIED = HERE / "PASS1008_4581_UNIFIED_EVENT_LEDGER.tsv"
READABLE = HERE / "PASS1008_FOUR_PAGE_READABLE_EDITION.md"
REPORT = HERE / "PASS1008_REPORT.md"
SUMMARY = HERE / "PASS1008_BUILD_SUMMARY.json"
BUILDER = HERE / "build_one_thousand_eighth.py"

ROOTS = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)
BASE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"
    / "PASS1006_3168_UNIFIED_EVENT_LEDGER.tsv"
)

PANEL_ORDER = ["f18r", "f72r1", "f72r2", "f72r3", "f76r", "f89r1", "f89r2"]
EXPECTED_PANEL_COUNTS = {
    "f18r": (14, 84), "f72r1": (18, 105), "f72r2": (32, 113),
    "f72r3": (34, 166), "f76r": (56, 569), "f89r1": (27, 141),
    "f89r2": (34, 235),
}
EXPECTED_PAGE_COUNTS = {
    "f18r": (14, 84, 84, 0, 5),
    "f72r": (84, 384, 288, 96, 22),
    "f76r": (56, 569, 560, 9, 118),
    "f89r": (61, 376, 338, 38, 20),
}
EXPECTED_TRANSFER_COUNTS = {
    "EXACT_REGISTERED_SURFACE": 896,
    "LOCAL_OWNER_ADDRESS": 134,
    "LOCAL_SECTION_MARKER": 9,
    "ONE_EDIT_REGISTERED_ALLOGRAPH": 271,
    "TWO_EDIT_ROOTED_VARIANT": 74,
    "VISIBLE_NEW_COMPOSITION": 29,
}
EXPECTED_TEMPLATE_COUNTS = {
    "T01": 24, "T02": 4, "T03": 9, "T04": 6, "T05": 9,
    "T06": 27, "T07": 24, "T08": 40, "T09": 22,
}
REQUIRED_SLOTS = {
    "T01": {"OWNER", "ACTION"},
    "T02": {"OWNER", "ITEM", "ACTION"},
    "T03": {"OWNER", "SEQUENCE", "ACTION"},
    "T04": {"OWNER", "QUANTITY", "ACTION"},
    "T05": {"OWNER", "PREPARATION", "ACTION"},
    "T06": {"OWNER", "ACTION", "TARGET"},
    "T07": {"OWNER", "ACTION", "PATH"},
    "T08": {"OWNER", "ACTION"},
    "T09": {"OWNER", "ACTION"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def guarded_rows() -> list[dict[str, str]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv",
        str(ROOT / "transcription/voynich_zl3b_lines.tsv"),
        "--selector", "page",
    ]
    for panel in PANEL_ORDER:
        command.extend(["--allow", panel])
    command.extend([
        "--columns", "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix", "f84",
    ])
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def main() -> int:
    events = read_tsv(EVENTS)
    loci = read_tsv(LOCI)
    statements = read_tsv(STATEMENTS)
    owners = read_tsv(OWNERS)
    surfaces = read_tsv(SURFACES)
    profiles = read_tsv(PROFILES)
    images = read_tsv(IMAGES)
    unified = read_tsv(UNIFIED)
    roots = read_tsv(ROOTS)
    base = read_tsv(BASE)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    source = guarded_rows()

    checks: dict[str, bool] = {}
    checks["source loci exact"] = len(source) == 215
    checks["event count exact"] = len(events) == 1413
    checks["locus count exact"] = len(loci) == 215
    checks["statement count exact"] = len(statements) == 165
    checks["owner count exact"] = len(owners) == 31
    checks["surface count exact"] = len(surfaces) == 681
    checks["profile count exact"] = len(profiles) == 4
    checks["image count exact"] = len(images) == 4
    checks["unified count exact"] = len(unified) == 4581
    checks["event IDs unique"] = len({row["event_id"] for row in events}) == len(events)
    checks["statement IDs unique"] = len({row["statement_id"] for row in statements}) == len(statements)
    checks["surface rows unique"] = len({row["surface"] for row in surfaces}) == len(surfaces)
    checks["owner rows unique"] = len({row["owner_id"] for row in owners}) == len(owners)

    source_counts = Counter()
    source_sequences: dict[tuple[str, str], list[str]] = {}
    for row in source:
        source_counts[row["page"]] += 1
        source_sequences[(row["page"], row["locus"])] = row["eva_clean"].split()
    checks["panel locus counts exact"] = all(
        source_counts[panel] == EXPECTED_PANEL_COUNTS[panel][0] for panel in PANEL_ORDER
    )
    checks["panel group counts exact"] = all(
        sum(len(tokens) for (page, _), tokens in source_sequences.items() if page == panel)
        == EXPECTED_PANEL_COUNTS[panel][1]
        for panel in PANEL_ORDER
    )

    event_sequences: dict[tuple[str, str], list[str]] = {}
    for row in events:
        event_sequences.setdefault((row["source_panel"], row["locus"]), []).append(row["surface"])
    checks["guarded token order exact"] = event_sequences == source_sequences
    checks["running and label split exact"] = (
        sum(row["kind"] != "L" for row in events) == 1270
        and sum(row["kind"] == "L" for row in events) == 143
    )
    checks["transfer counts exact"] = Counter(row["transfer_class"] for row in events) == Counter(EXPECTED_TRANSFER_COUNTS)

    allowed = {row["recognition_form"] for row in roots}
    recipe_roots = {
        root
        for row in events
        if row["kind"] != "L"
        for root in row["component_recipe"].split("+")
    }
    checks["53-root inventory exact"] = len(allowed) == 53
    checks["no new portable root"] = recipe_roots <= allowed
    checks["all defaults present"] = all(row["portable_default_de"].strip() for row in events)
    checks["labels stay local"] = all(
        row["component_recipe"] in {"LOCAL_ADDRESS", "SECTION_MARKER"}
        for row in events if row["kind"] == "L"
    )
    checks["running rows are rooted"] = all(
        row["component_recipe"] not in {"LOCAL_ADDRESS", "SECTION_MARKER"}
        for row in events if row["kind"] != "L"
    )

    statement_event_ids = [event_id for row in statements for event_id in row["event_ids"].split("|")]
    running_ids = [row["event_id"] for row in events if row["kind"] != "L"]
    checks["running events partition statements"] = Counter(statement_event_ids) == Counter(running_ids)
    checks["label events outside statements"] = all(not row["statement_id"] for row in events if row["kind"] == "L")
    checks["running statement backlink exact"] = all(row["statement_id"] for row in events if row["kind"] != "L")
    checks["template distribution exact"] = Counter(row["template_id"] for row in statements) == Counter(EXPECTED_TEMPLATE_COUNTS)
    checks["celestial statements T09"] = all(
        row["template_id"] == "T09" for row in statements if row["register"] == "CELESTIAL"
    )
    checks["template requirements satisfied"] = all(
        REQUIRED_SLOTS[row["template_id"]] <= set(row["template_slot_signature"].split(">"))
        for row in statements
    )
    checks["inherited action count exact"] = sum(
        row["action_realization"] == "INHERITED_FROM_ACTIVE_SECTION" for row in statements
    ) == 8
    checks["observed action count exact"] = sum(
        row["action_realization"] == "EXPLICIT_CARD" for row in statements
    ) == 157
    checks["licensed close count exact"] = sum(
        row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements
    ) == 134
    checks["visible boundary count exact"] = sum(
        row["end_mode"].startswith("VISIBLE_") for row in statements
    ) == 31
    checks["no fabricated open end"] = all(not row["end_mode"].startswith("OPEN_") for row in statements)
    checks["cross-line count exact"] = sum(row["crosses_physical_line"] == "YES" for row in statements) == 39

    event_by_id = {row["event_id"]: row for row in events}
    checks["licensed close ends in DY"] = all(
        event_by_id[row["event_ids"].split("|")[-1]]["component_recipe"].split("+")[-1] == "DY"
        for row in statements if row["end_mode"] == "LICENSED_DY_CLOSE"
    )
    checks["nonclose boundary not forced by DY"] = all(
        event_by_id[row["event_ids"].split("|")[-1]]["licensed_close"] == "NO"
        for row in statements if row["end_mode"] != "LICENSED_DY_CLOSE"
    )
    checks["line crossing computed exact"] = all(
        (len(row["locus_span"].split("|")) > 1) == (row["crosses_physical_line"] == "YES")
        for row in statements
    )

    checks["physical page summary exact"] = all(
        (
            int(row["loci"]), int(row["groups"]), int(row["running_groups"]),
            int(row["address_or_marker_groups"]), int(row["statements"]),
        ) == EXPECTED_PAGE_COUNTS[row["physical_page"]]
        for row in profiles
    )
    checks["all nine drawers used"] = {row["template_id"] for row in statements} == {f"T{i:02d}" for i in range(1, 10)}
    checks["f76 is text-only owner model"] = all(
        "unbebilderter" in row["visible_owner_or_namespace_de"]
        for row in statements if row["physical_page"] == "f76r"
    )
    checks["f72 has ten ring namespaces"] = len({row["owner_id"] for row in owners if row["physical_page"] == "f72r"}) == 10
    checks["f89 has seven material batches"] = len({row["owner_id"] for row in owners if row["physical_page"] == "f89r"}) == 7

    checks["image dimensions exact"] = {
        row["physical_page"]: (int(row["width"]), int(row["height"])) for row in images
    } == {"f18r": (2000, 2826), "f72r": (2000, 1270), "f76r": (2000, 2699), "f89r": (2000, 1812)}
    checks["image hashes exact"] = {row["physical_page"]: row["sha256"] for row in images} == {
        "f18r": "1e339b1e6f3153e557ff2371efb9ade8e89017ea8bfde665e880f664520a0b9b",
        "f72r": "46c961644e15d06a76bc4f7a6d209963edb4875ba8d0a802e255d4733c4154f0",
        "f76r": "5cb706c79a119a6b694e7496aedc77324de9460b15372557bdf0081e79cb9931",
        "f89r": "a99a8c993cce967dc1b2a6d9db922f0524b169a9331ff8e45afe057352bfb0a6",
    }
    checks["official image URLs only"] = all(
        row["iiif_url"].startswith("https://collections.library.yale.edu/iiif/2/") for row in images
    )

    checks["base ledger preserved"] = all(
        unified[index]["event_id"] == row["event_id"]
        and unified[index]["surface"] == row["surface"]
        and unified[index]["component_recipe"] == row["component_recipe"]
        for index, row in enumerate(base)
    )
    checks["new ledger appended exact"] = all(
        unified[3168 + index]["event_id"] == row["event_id"]
        and unified[3168 + index]["surface"] == row["surface"]
        and unified[3168 + index]["component_recipe"] == row["component_recipe"]
        for index, row in enumerate(events)
    )
    checks["unified ordinals contiguous"] = [int(row["book_event_ordinal"]) for row in unified] == list(range(1, 4582))

    checks["summary core counts exact"] = (
        summary["groups"] == 1413
        and summary["running_groups"] == 1270
        and summary["address_or_marker_groups"] == 143
        and summary["statements"] == 165
        and summary["unified_groups"] == 4581
        and summary["new_portable_roots"] == 0
        and summary["inherited_action_statements"] == 8
    )
    checks["report decision present"] = "4.581 Gruppen" in REPORT.read_text(encoding="utf-8")
    checks["readable edition covers statements"] = all(
        row["statement_id"] in READABLE.read_text(encoding="utf-8") for row in statements
    )

    artifacts = [EVENTS, LOCI, STATEMENTS, OWNERS, SURFACES, PROFILES, IMAGES, UNIFIED, READABLE, REPORT]
    before = {path.name: digest(path) for path in artifacts}
    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True)
    after = {path.name: digest(path) for path in artifacts}
    checks["deterministic rebuild byte-identical"] = before == after
    checks["summary output hashes exact"] = json.loads(SUMMARY.read_text(encoding="utf-8"))["output_sha256"] == after

    text_blob = b"\n".join(path.read_bytes() for path in artifacts)
    checks["sealed folios absent"] = b"f84" not in text_blob.lower()
    checks["no absolute workspace path in outputs"] = str(ROOT).encode() not in text_blob

    failures = [name for name, passed in checks.items() if not passed]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks_total": len(checks),
        "checks_passed": sum(checks.values()),
        "checks_failed": failures,
        "counts": {
            "physical_pages": 4,
            "source_panels": 7,
            "loci": len(loci),
            "groups": len(events),
            "running_groups": len(running_ids),
            "local_groups": len(events) - len(running_ids),
            "statements": len(statements),
            "owners_or_namespaces": len(owners),
            "unified_groups": len(unified),
        },
        "template_counts": dict(sorted(Counter(row["template_id"] for row in statements).items())),
        "transfer_counts": dict(sorted(Counter(row["transfer_class"] for row in events).items())),
        "checks": checks,
    }
    (HERE / "PASS1008_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: {len(checks)}/{len(checks)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
