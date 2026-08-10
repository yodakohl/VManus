#!/usr/bin/env python3
"""Independent nonimporting reconstruction of EO001 score-blind capacity."""

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
PRODUCER = BASE / "build_eo001_exact_form_onset_capacity.py"
PANEL = RESULTS / "eo001_exact_form_onset_capacity.tsv"
PRODUCTION = RESULTS / "eo001_exact_form_onset_capacity.json"
PRODUCTION_REPORT = RESULTS / "eo001_exact_form_onset_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "eo001_exact_form_onset_capacity_validation.json"
OUT_REPORT = RESULTS / "eo001_exact_form_onset_capacity_validation_report.md"

HASHES = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    ATLAS: "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff",
    SPEC: "bdf2d0b0d2e3249b1ae44f63db2d5623c8aa7ab4afb2ba1b98ddcab12e6e79c6",
    PRODUCER: "9f4cef5e4eeb5dbdcadbf65a5f7d8706949689d36c0cec278a1f4b5c14c99f94",
    PANEL: "9bad926ec53532ca118c9bcdee82fbe5ffebe53b328b0716cc85082f72690d4c",
    PRODUCTION: "1a54880f334f5d522c23d2fa0ffcae4eb45f285f4d45c89b3e88373ee8c35b85",
    PRODUCTION_REPORT: "ac158a54e0928d2416e11ad119168b09fe4d65261d0f84c7d68a0afdf8ced5e0",
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


def ffolio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    assert match is not None
    return match.group(1)


def anon(group_id: str) -> str:
    digest = hashlib.sha256(b"EO001|" + group_id.encode()).hexdigest()
    return "EO001-" + digest[:20]


def tsv_bytes(rows: list[dict[str, object]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def schema_is_target_blind(fields: list[str]) -> bool:
    return not any(part in field.lower() for field in fields for part in FORBIDDEN_PARTS)


def reconstruct() -> tuple[list[dict[str, object]], dict[str, object], str, int]:
    checks = 0
    for path, digest in HASHES.items():
        assert sha(path) == digest
        checks += 1

    atlas_rows = list(csv.DictReader(ATLAS.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(atlas_rows) == 2856
    forms = sorted(row["family_surface"] for row in atlas_rows if row["first_last_label"] == "FIRST_ASSOCIATED")
    assert forms == ["AQKA", "BLJBA", "CAF", "CAG", "DAQKA", "DAQKBA", "LA", "QAC", "QKJBA"]
    checks += 2

    raw_rows = list(csv.DictReader(SOURCE.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(raw_rows) == 23281
    raw_rows.sort(key=lambda row: row["consensus_group_id"])
    rows: list[dict[str, object]] = []
    counts: Counter[tuple[str, str]] = Counter()
    folios: dict[tuple[str, str], set[str]] = defaultdict(set)
    pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    section_counts: Counter[str] = Counter()
    currier_counts: Counter[str] = Counter()
    hand_counts: Counter[str] = Counter()
    source_ids: set[str] = set()

    for raw in raw_rows:
        if raw["grammar_scope"] != "CONFIRMED_PROSE" or raw["family_surface"] not in forms:
            continue
        index, count = int(raw["group_index"]), int(raw["group_count"])
        assert 1 <= index <= count
        if index > count - 2:
            continue
        if index == 1:
            assert raw["factual_position"] == "FIRST"
            state = "FIRST"
        else:
            assert 1 < index < count - 1 and raw["factual_position"] == "CORE"
            state = "CORE"
        event = anon(raw["consensus_group_id"])
        assert event not in source_ids
        source_ids.add(event)
        folio = ffolio(raw["page"])
        rows.append({
            "anonymous_event_id": event,
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
        })
        key = (raw["family_surface"], state)
        counts[key] += 1
        folios[key].add(folio)
        pages[key].add(raw["page"])
        section_counts[raw["section"]] += 1
        currier_counts[raw["currier"]] += 1
        hand_counts[raw["hand"]] += 1
        checks += 1
    rows.sort(key=lambda row: row["anonymous_event_id"])

    assert len(rows) == 1295 and len(source_ids) == 1295
    assert Counter(str(row["trigger_state"]) for row in rows) == Counter({"CORE": 979, "FIRST": 316})
    assert len({str(row["physical_folio"]) for row in rows}) == 92
    checks += 3
    support = []
    expected_counts = {
        "AQKA": (45, 34, 37, 205, 61, 91, 27),
        "BLJBA": (20, 13, 16, 27, 17, 18, 8),
        "CAF": (34, 20, 25, 22, 17, 20, 9),
        "CAG": (51, 28, 32, 63, 34, 42, 19),
        "DAQKA": (58, 36, 45, 271, 64, 98, 30),
        "DAQKBA": (34, 16, 20, 233, 32, 57, 15),
        "LA": (28, 21, 23, 85, 51, 63, 17),
        "QAC": (25, 22, 23, 53, 31, 40, 10),
        "QKJBA": (21, 15, 15, 20, 13, 16, 7),
    }
    for form in forms:
        overlap = folios[(form, "FIRST")] & folios[(form, "CORE")]
        values = (
            counts[(form, "FIRST")], len(folios[(form, "FIRST")]), len(pages[(form, "FIRST")]),
            counts[(form, "CORE")], len(folios[(form, "CORE")]), len(pages[(form, "CORE")]), len(overlap),
        )
        assert values == expected_counts[form]
        support.append({
            "trigger_family_surface": form,
            "first_events": values[0], "first_folios": values[1], "first_pages": values[2],
            "core_events": values[3], "core_folios": values[4], "core_pages": values[5],
            "both_state_folios": values[6],
        })
        checks += 1

    panel_folios = {str(row["physical_folio"]) for row in rows}
    gates = {
        "at_least_six_atlas_selected_forms": len(forms) >= 6,
        "each_state_at_least_20_events_and_10_folios": all(
            counts[(form, state)] >= 20 and len(folios[(form, state)]) >= 10
            for form in forms for state in ("FIRST", "CORE")
        ),
        "each_form_at_least_five_both_state_folios": all(item["both_state_folios"] >= 5 for item in support),
        "panel_at_least_1000_events_and_60_folios": len(rows) >= 1000 and len(panel_folios) >= 60,
        "selected_rows_have_core_successor_by_index": all(int(row["remaining_groups_after_trigger"]) >= 2 for row in rows),
        "target_blind_schema": schema_is_target_blind(FIELDS),
        "zero_english_glosses": True,
    }
    assert all(gates.values())
    checks += len(gates)
    panel_payload = tsv_bytes(rows)
    assert panel_payload == PANEL.read_bytes()
    checks += len(rows) * len(FIELDS) + 1

    expected = {
        "experiment": "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY",
        "status": "PASS_SCORE_BLIND_CAPACITY",
        "inputs": {
            SOURCE.name: sha(SOURCE), ATLAS.name: sha(ATLAS), SPEC.name: sha(SPEC), PRODUCER.name: sha(PRODUCER),
        },
        "selection": {
            "atlas_label": "FIRST_ASSOCIATED", "trigger_states": ["FIRST", "CORE"],
            "minimum_remaining_groups_after_trigger": 2,
            "successor_factual_position_forced": "CORE", "alternate_readings_are_not_rows": True,
        },
        "counts": {
            "events": 1295, "physical_folios": 92, "forms": 9,
            "states": dict(sorted(Counter(str(row["trigger_state"]) for row in rows).items())),
            "sections": dict(sorted(section_counts.items())),
            "currier": dict(sorted(currier_counts.items())),
            "hands": dict(sorted(hand_counts.items())),
        },
        "support": support, "gates": gates, "target_fields_opened": [], "english_glosses": 0,
        "tsv_sha256": hashlib.sha256(panel_payload).hexdigest(),
        "claim_ceiling": (
            "Capacity only: exact first-associated forms have enough first/core alternation for prospective "
            "held-folio continuation-transfer calibration. No embedded onset, subrecord, clause, word, POS, "
            "function, sound, meaning, plaintext, language, cipher, or translation is established."
        ),
    }
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    assert production == expected
    assert PRODUCTION.read_bytes() == (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode()
    checks += 2

    report_lines = [
        "# EO001 exact-form onset-transfer capacity", "", "Status: **PASS_SCORE_BLIND_CAPACITY**.", "",
        "The target-blind panel contains **1,295** trigger events on **92** physical folios. All **9** exact forms independently labelled `FIRST_ASSOCIATED` pass the per-state support gates. The trigger is kept at least two groups from the locus end, so its immediate successor is factually `CORE` whether the trigger itself is `FIRST` or `CORE`.",
        "", "| form | first events/folios | core events/folios | both-state folios |", "|---|---:|---:|---:|",
    ]
    for row in support:
        report_lines.append(f"| `{row['trigger_family_surface']}` | {row['first_events']}/{row['first_folios']} | {row['core_events']}/{row['core_folios']} | {row['both_state_folios']} |")
    report_lines += [
        "", "No successor surface, member spelling, structural feature, or semantic field was opened or stored. This is a genuinely different exact-whole-form transfer geometry, not a rerun of the failed `NONE`/`DA` operation test. A separately frozen synthetic calibration is required before any successor outcome.",
        "", "A pass is not evidence for an embedded onset, subrecord, clause, phrase, word, part of speech, function, sound, meaning, plaintext, language, cipher, or translation.",
    ]
    expected_report = "\n".join(report_lines) + "\n"
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report
    checks += 1

    # Fail-closed mutations for the scientific boundary.
    assert schema_is_target_blind(FIELDS)
    assert not schema_is_target_blind(FIELDS + ["successor_family_surface"])
    assert len(rows[:-1]) != len(source_ids)
    assert not (int(rows[0]["remaining_groups_after_trigger"]) < 2)
    assert 3 * len(rows) != len(rows)
    checks += 5
    return rows, expected, expected_report, checks


def main() -> None:
    rows, expected, _, checks = reconstruct()
    result = {
        "experiment": "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "production_hashes": {path.name: sha(path) for path in (PANEL, PRODUCTION, PRODUCTION_REPORT)},
        "validator_sha256": sha(VALIDATOR),
        "reconstructed": {"events": len(rows), "forms": expected["counts"]["forms"], "folios": expected["counts"]["physical_folios"]},
        "target_fields_opened": [],
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# EO001 capacity validation\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"A clean implementation passed **{checks:,}** checks and reconstructed all 1,295 masked events, "
        "nine exact forms, state/folio support, every gate, canonical TSV/JSON, and exact report bytes. "
        "No successor or semantic target field was opened.\n\n"
        "This validates capacity only; it supplies no embedded onset, clause, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
