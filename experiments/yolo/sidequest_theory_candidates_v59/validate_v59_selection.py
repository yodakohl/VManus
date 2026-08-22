#!/usr/bin/env python3
"""Validate the canonical strict-exact V59 ten-page sidequest release."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = {
    "cards": ROOT / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv",
    "events": ROOT / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    "fields": ROOT / "V59_R1_FINAL_135_FIELD_EDITION.tsv",
    "astro": ROOT / "V59_R1_FINAL_395_ASTRO_GROUP_EDITION.tsv",
    "ledger": ROOT / "V59_R1_FINAL_776_VISIBLE_UNIT_EDITION.tsv",
    "units": ROOT / "V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv",
    "quick": ROOT / "V59_FINAL_QUICK_DICTIONARY.tsv",
}
SOURCE_VALIDATION = ROOT / "V59_R1_VALIDATION.json"
OUT = ROOT / "V59_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


rows = {name: read_tsv(path) for name, path in FILES.items()}
with SOURCE_VALIDATION.open(encoding="utf-8") as handle:
    source_validation = json.load(handle)

cards = rows["cards"]
events = rows["events"]
fields = rows["fields"]
astro = rows["astro"]
ledger = rows["ledger"]
units = rows["units"]

def event_is_formal(row: dict[str, str]) -> bool:
    return any(
        tag in row["FORMAL_VALUE"] for tag in ("SET_", "MARK_", "LINK_")
    )


def event_has_mnemonic(row: dict[str, str]) -> bool:
    return row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"


formal_events = sum(event_is_formal(row) for row in events)
mnemonic_events = sum(event_has_mnemonic(row) for row in events)
anchored_events = sum(event_is_formal(row) or event_has_mnemonic(row) for row in events)
unknown_events = len(events) - anchored_events

field_events: dict[str, list[dict[str, str]]] = defaultdict(list)
for event in events:
    field_events[event["field_id"]].append(event)

fields_with_anchor = sum(
    any(event_is_formal(row) or event_has_mnemonic(row) for row in member_rows)
    for member_rows in field_events.values()
)
fully_anchored_fields = sum(
    all(event_is_formal(row) or event_has_mnemonic(row) for row in member_rows)
    for member_rows in field_events.values()
)

required_layers = [
    "FORMAL_VALUE",
    "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
    "LOCAL_IATROMEDICAL_EXPANSION",
    "NONMEDICAL_RIVAL",
    "UNKNOWN_EXEMPLAR_STATUS",
]
all_layer_rows = cards + events + fields + astro + ledger + units

allowed_pages = {
    "f10r",
    "f11r",
    "f55v",
    "f56r",
    "f67r2",
    "f68r1",
    "f69v",
    "f81v",
    "f82r",
    "f83r",
}
observed_pages = {row["page"] for row in ledger}

checks = {
    "source_r1_validation_pass": source_validation.get("status") == "PASS",
    "cards_173": len(cards) == 173,
    "events_381": len(events) == 381,
    "fields_135": len(fields) == 135,
    "astro_395": len(astro) == 395,
    "ledger_776": len(ledger) == 776,
    "units_14": len(units) == 14,
    "exact_card_ids_unique": len({row["joint_tuple_id"] for row in cards}) == 173,
    "event_serials_unique": len({row["event_serial"] for row in events}) == 381,
    "field_ids_unique": len({row["field_id"] for row in fields}) == 135,
    "astro_token_ids_unique": len({row["astro_token_id"] for row in astro}) == 395,
    "visible_unit_serials_unique": len({row["visible_unit_serial"] for row in ledger}) == 776,
    "all_required_layers_nonblank": all(
        all(row.get(column, "").strip() for column in required_layers)
        for row in all_layer_rows
    ),
    "page_allowlist_exact": observed_pages == allowed_pages,
    "no_page_host_semantic_column": all(
        "page_host" not in {key.lower() for key in row.keys()}
        for row in cards + events + fields + astro + ledger + units
    ),
    "eleven_exact_card_mnemonics": sum(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN" for row in cards
    ) == 11,
    "other_162_cards_unknown": sum(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == "UNKNOWN" for row in cards
    ) == 162,
    "formal_events_57": formal_events == 57,
    "mnemonic_events_85": mnemonic_events == 85,
    "strict_union_142": anchored_events == 142,
    "unknown_events_239": unknown_events == 239,
    "fields_with_anchor_82": fields_with_anchor == 82,
    "fields_without_anchor_53": len(fields) - fields_with_anchor == 53,
    "fully_anchored_fields_17": fully_anchored_fields == 17,
    "field_event_sum_381": sum(int(row["event_count"]) for row in fields) == 381,
    "closed_90_open_45": Counter(row["closure_status"] for row in fields)
    == Counter({"TERMINAL": 90, "OPEN": 45}),
    "unit_partition_5_6_3": Counter(row["module"] for row in units)
    == Counter({"HERBAL_RECORD": 5, "BIOLOGICAL_RECORD": 6, "ASTRO_DIAGRAM": 3}),
    "unit_event_totals": sum(
        int(row["events_or_groups"]) for row in units
    ) == 776,
    "astro_no_prose_mnemonic": all(
        row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == "NOT_APPLICABLE_ASTRO_LOCAL"
        for row in astro
    ),
    "direct_join_absent_in_source_validation": source_validation["assertions"].get(
        "direct_f68_f69_join_absent"
    )
    is True,
    "quick_dictionary_19_rows": len(rows["quick"]) == 19,
    "confirmed_semantics_not_claimed": source_validation["assertions"].get(
        "semantic_proof_claim_absent"
    )
    is True,
}

payload = {
    "schema": "SIDEQUEST_V59_CANONICAL_SELECTION_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "pages": 10,
        "prose_cards": len(cards),
        "prose_events": len(events),
        "prose_fields": len(fields),
        "astro_groups": len(astro),
        "all_visible_groups": len(ledger),
        "complete_units": len(units),
        "formal_events": formal_events,
        "exact_mnemonic_events": mnemonic_events,
        "strict_annotated_union_events": anchored_events,
        "unknown_exemplar_events": unknown_events,
        "fields_with_strict_anchor": fields_with_anchor,
        "fields_without_strict_anchor": len(fields) - fields_with_anchor,
        "fully_strictly_annotated_fields": fully_anchored_fields,
    },
    "selection": {
        "canonical_release": "V59_R1_STRICT_EXACT_ID_EDITION",
        "reason": "removes_three_nonportable_PAGE_HOST_derived_mnemonics",
        "architecture": "DOMAIN_NEUTRAL_EXEMPLAR_MACHINE",
        "leading_content_default": "IATROMEDICAL_WHAT_HOW_WHEN",
        "strongest_rival": "PLANT_MATERIAL_BATHHOUSE_WORK_ALMANAC_MISCELLANY",
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
    },
    "sha256": {name: sha256(path) for name, path in FILES.items()},
}

OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
