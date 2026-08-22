#!/usr/bin/env python3
"""Select the V72 historical Herbal and technical Bio statement editions."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
COLS = [
    "statement_id", "selected_from_role", "record_unit_id", "page",
    "constituent_fields", "event_count", "event_serials", "owner_bindings",
    "owner_transition", "literal_owner_card_exemplar_layer", "source_class",
    "selected_concrete_paraphrase", "strongest_rival", "repair_cost_0_4",
    "repair_reason", "line_crossing", "hardest_contradiction", "semantic_ceiling",
]


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def sha(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def event_count(serials: str) -> int:
    return len([x for x in serials.split("|") if x])


def main() -> None:
    r2 = read("V72_R2_116_STATEMENTS.tsv")
    r3 = read("V72_R3_116_STATEMENTS.tsv")
    selected = []
    for row in r2:
        if not row["record_unit_id"].startswith("H"):
            continue
        selected.append({
            "statement_id": row["statement_id"], "selected_from_role": "R2_HISTORICAL",
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "constituent_fields": row["constituent_fields"],
            "event_count": str(event_count(row["event_serials"])), "event_serials": row["event_serials"],
            "owner_bindings": row["v71_visible_owners"], "owner_transition": row["owner_crossing"],
            "literal_owner_card_exemplar_layer": row["literal_owner_card_exemplar_layer"],
            "source_class": row["historical_source_class"],
            "selected_concrete_paraphrase": row["concrete_source_class_paraphrase"],
            "strongest_rival": row["strongest_rival"], "repair_cost_0_4": row["repair_cost_0_4"],
            "repair_reason": row["repair_reason"], "line_crossing": row["line_crossing"],
            "hardest_contradiction": row["strongest_contradiction"],
            "semantic_ceiling": row["semantic_ceiling"],
        })
    for row in r3:
        if not row["record_unit_id"].startswith("B"):
            continue
        selected.append({
            "statement_id": row["statement_id"], "selected_from_role": "R3_TECHNICAL",
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "constituent_fields": row["constituent_fields"], "event_count": row["event_count"],
            "event_serials": row["event_serials"], "owner_bindings": row["v71_field_owner_bindings"],
            "owner_transition": row["exact_v71_owner_transition"],
            "literal_owner_card_exemplar_layer": row["literal_owner_known_card_exemplar_layer"],
            "source_class": row["source_class"],
            "selected_concrete_paraphrase": row["technical_source_class_paraphrase"],
            "strongest_rival": row["strongest_medical_or_formal_rival"],
            "repair_cost_0_4": row["repair_cost_0_4"], "repair_reason": row["repair_reason"],
            "line_crossing": row["line_crossing"], "hardest_contradiction": row["hardest_contradiction"],
            "semantic_ceiling": row["semantic_ceiling"],
        })
    selected.sort(key=lambda r: int(r["event_serials"].split("|")[0]))
    with (HERE / "V72_SELECTED_116_STATEMENTS.tsv").open("w", encoding="utf-8", newline="") as h:
        w=csv.DictWriter(h,fieldnames=COLS,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(selected)

    event_ids=[x for r in selected for x in r["event_serials"].split("|")]
    hard={"B2-S012","B3-S016","B3-S026","B4-S015"}
    hard_found={r["statement_id"] for r in selected if "BREAK_VISIBLE_GAP" in r["owner_transition"]}
    checks={
        "statements_116":len(selected)==116,
        "herbal_19":sum(r["record_unit_id"].startswith("H") for r in selected)==19,
        "bio_97":sum(r["record_unit_id"].startswith("B") for r in selected)==97,
        "events_381_unique":len(event_ids)==381 and len(set(event_ids))==381,
        "fields_135_unique":len({f for r in selected for f in r["constituent_fields"].split("|")})==135,
        "hard_owner_breaks_retained":hard.issubset(hard_found),
        "concrete_paraphrase_nonblank":all(r["selected_concrete_paraphrase"].strip() for r in selected),
        "costs_bounded":all(0<=int(r["repair_cost_0_4"])<=4 for r in selected),
    }
    result={
        "schema":"V72_FOUR_ROLE_SELECTION_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL",
        "checks":checks,"counts":{"statements":len(selected),"events":len(event_ids),"repair_costs":dict(Counter(r["repair_cost_0_4"] for r in selected))},
        "bindings":{f"V72_R{x}_116_STATEMENTS.tsv":sha(f"V72_R{x}_116_STATEMENTS.tsv") for x in range(1,5)},
        "sealed_pages_opened":[],
    }
    (HERE/"V72_VALIDATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(result["status"],checks)
    if result["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
