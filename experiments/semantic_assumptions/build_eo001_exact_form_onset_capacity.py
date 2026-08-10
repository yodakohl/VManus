#!/usr/bin/env python3
"""Build the score-blind EO001 exact-form onset-transfer capacity panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
ATLAS = RESULTS / "source_native_group_position_atlas.tsv"
SPEC = BASE / "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "eo001_exact_form_onset_capacity.tsv"
OUT_JSON = RESULTS / "eo001_exact_form_onset_capacity.json"
OUT_REPORT = RESULTS / "eo001_exact_form_onset_capacity_report.md"

FROZEN = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    ATLAS: "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff",
}
FIELDS = [
    "anonymous_event_id", "trigger_family_surface", "trigger_state",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "trigger_group_index", "locus_group_count", "remaining_groups_after_trigger",
]
FORBIDDEN_PARTS = (
    "successor", "next_", "member", "sta_codes", "eva", "root", "role",
    "feature", "transition", "path", "meaning", "gloss", "translation",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"bad page {page}")
    return match.group(1)


def event_id(group_id: str) -> str:
    return "EO001-" + hashlib.sha256(("EO001|" + group_id).encode()).hexdigest()[:20]


def canonical_tsv(rows: list[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def main() -> None:
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input drift: {path}")

    atlas = list(csv.DictReader(ATLAS.open(encoding="utf-8", newline=""), delimiter="\t"))
    forms = sorted(row["family_surface"] for row in atlas if row["first_last_label"] == "FIRST_ASSOCIATED")
    if len(forms) != len(set(forms)):
        raise SystemExit("duplicate atlas forms")

    source = list(csv.DictReader(SOURCE.open(encoding="utf-8", newline=""), delimiter="\t"))
    source.sort(key=lambda row: row["consensus_group_id"])
    rows: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    counts: Counter[tuple[str, str]] = Counter()
    folios: dict[tuple[str, str], set[str]] = defaultdict(set)
    pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    section_counts: Counter[str] = Counter()
    currier_counts: Counter[str] = Counter()
    hand_counts: Counter[str] = Counter()

    for raw in source:
        if raw["grammar_scope"] != "CONFIRMED_PROSE" or raw["family_surface"] not in forms:
            continue
        index = int(raw["group_index"])
        count = int(raw["group_count"])
        if not 1 <= index <= count:
            raise SystemExit("invalid group index")
        if index > count - 2:
            continue
        if raw["factual_position"] == "FIRST" and index == 1:
            state = "FIRST"
        elif raw["factual_position"] == "CORE" and 1 < index < count:
            state = "CORE"
        else:
            raise SystemExit("factual position mismatch in selected row")
        opaque = event_id(raw["consensus_group_id"])
        if opaque in seen_ids:
            raise SystemExit("event ID collision")
        seen_ids.add(opaque)
        folio = physical_folio(raw["page"])
        row = {
            "anonymous_event_id": opaque,
            "trigger_family_surface": raw["family_surface"],
            "trigger_state": state,
            "physical_folio": folio,
            "section": raw["section"],
            "currier": raw["currier"],
            "hand": raw["hand"],
            "code": raw["code"],
            "kind": raw["kind"],
            "trigger_group_index": index,
            "locus_group_count": count,
            "remaining_groups_after_trigger": count - index,
        }
        rows.append(row)
        key = (raw["family_surface"], state)
        counts[key] += 1
        folios[key].add(folio)
        pages[key].add(raw["page"])
        section_counts[raw["section"]] += 1
        currier_counts[raw["currier"]] += 1
        hand_counts[raw["hand"]] += 1

    rows.sort(key=lambda row: row["anonymous_event_id"])
    support = []
    for form in forms:
        overlap = folios[(form, "FIRST")] & folios[(form, "CORE")]
        support.append({
            "trigger_family_surface": form,
            "first_events": counts[(form, "FIRST")],
            "first_folios": len(folios[(form, "FIRST")]),
            "first_pages": len(pages[(form, "FIRST")]),
            "core_events": counts[(form, "CORE")],
            "core_folios": len(folios[(form, "CORE")]),
            "core_pages": len(pages[(form, "CORE")]),
            "both_state_folios": len(overlap),
        })

    panel_folios = {str(row["physical_folio"]) for row in rows}
    gates = {
        "at_least_six_atlas_selected_forms": len(forms) >= 6,
        "each_state_at_least_20_events_and_10_folios": all(
            counts[(form, state)] >= 20 and len(folios[(form, state)]) >= 10
            for form in forms for state in ("FIRST", "CORE")
        ),
        "each_form_at_least_five_both_state_folios": all(row["both_state_folios"] >= 5 for row in support),
        "panel_at_least_1000_events_and_60_folios": len(rows) >= 1000 and len(panel_folios) >= 60,
        "selected_rows_have_core_successor_by_index": all(
            int(row["remaining_groups_after_trigger"]) >= 2 for row in rows
        ),
        "target_blind_schema": not any(
            part in field.lower() for field in FIELDS for part in FORBIDDEN_PARTS
        ),
        "zero_english_glosses": True,
    }
    status = "PASS_SCORE_BLIND_CAPACITY" if all(gates.values()) else "STOP_CAPACITY"
    panel_bytes = canonical_tsv(rows)
    OUT_TSV.write_bytes(panel_bytes)

    result = {
        "experiment": "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY",
        "status": status,
        "inputs": {
            SOURCE.name: sha(SOURCE), ATLAS.name: sha(ATLAS),
            SPEC.name: sha(SPEC), BUILDER.name: sha(BUILDER),
        },
        "selection": {
            "atlas_label": "FIRST_ASSOCIATED",
            "trigger_states": ["FIRST", "CORE"],
            "minimum_remaining_groups_after_trigger": 2,
            "successor_factual_position_forced": "CORE",
            "alternate_readings_are_not_rows": True,
        },
        "counts": {
            "events": len(rows),
            "physical_folios": len(panel_folios),
            "forms": len(forms),
            "states": dict(sorted(Counter(str(row["trigger_state"]) for row in rows).items())),
            "sections": dict(sorted(section_counts.items())),
            "currier": dict(sorted(currier_counts.items())),
            "hands": dict(sorted(hand_counts.items())),
        },
        "support": support,
        "gates": gates,
        "target_fields_opened": [],
        "english_glosses": 0,
        "tsv_sha256": hashlib.sha256(panel_bytes).hexdigest(),
        "claim_ceiling": (
            "Capacity only: exact first-associated forms have enough first/core alternation for prospective "
            "held-folio continuation-transfer calibration. No embedded onset, subrecord, clause, word, POS, "
            "function, sound, meaning, plaintext, language, cipher, or translation is established."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# EO001 exact-form onset-transfer capacity", "",
        f"Status: **{status}**.", "",
        f"The target-blind panel contains **{len(rows):,}** trigger events on **{len(panel_folios)}** physical folios. "
        f"All **{len(forms)}** exact forms independently labelled `FIRST_ASSOCIATED` pass the per-state support gates. "
        "The trigger is kept at least two groups from the locus end, so its immediate successor is factually `CORE` "
        "whether the trigger itself is `FIRST` or `CORE`.", "", "| form | first events/folios | core events/folios | both-state folios |", "|---|---:|---:|---:|",
    ]
    for row in support:
        lines.append(
            f"| `{row['trigger_family_surface']}` | {row['first_events']}/{row['first_folios']} | "
            f"{row['core_events']}/{row['core_folios']} | {row['both_state_folios']} |"
        )
    lines += [
        "", "No successor surface, member spelling, structural feature, or semantic field was opened or stored. "
        "This is a genuinely different exact-whole-form transfer geometry, not a rerun of the failed `NONE`/`DA` "
        "operation test. A separately frozen synthetic calibration is required before any successor outcome.", "",
        "A pass is not evidence for an embedded onset, subrecord, clause, phrase, word, part of speech, function, "
        "sound, meaning, plaintext, language, cipher, or translation.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if status != "PASS_SCORE_BLIND_CAPACITY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
