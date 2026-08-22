#!/usr/bin/env python3
"""Expand the V40 prompt lexicon into field and record worksheet schemas."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v40/V40_REVISED_381_EVENT_LEDGER.tsv"
CORE = ROOT / "experiments/yolo/sidequest_theory_candidates_v39/V39_SELECTED_SHARED_CARD_LEXICON.tsv"
PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]

ROLE_MAP = {
    "PARAMETER": "MEASURE",
    "BACK_REFERENCE": "PRIOR_SOURCE",
    "CURRENT_ITEM": "CURRENT_ITEM",
    "DESTINATION": "DESTINATION",
    "EXECUTE_USE": "USE_OR_EXECUTE",
    "WORKING_MATERIAL": "WORKING_MATERIAL",
    "READINESS_GATE": "STATE_GATE",
    "SAME_SOURCE": "SAME_SOURCE",
    "VISIBLE_THRESHOLD": "STATE_GATE",
    "PRIOR_SOURCE_WITHDRAWAL": "PRIOR_SOURCE",
    "PROCESS_TO_UNIFORMITY": "PROCESS",
    "TAKE_SELECTED_PART": "TAKE_SELECTED",
}

PROMPT = {
    "TAKE_SELECTED": "WAS IST ZU NEHMEN?",
    "MEASURE": "WIE VIEL ODER NACH WELCHEM MASS?",
    "PRIOR_SOURCE": "WORAUS ODER MIT WELCHEM VORANSATZ?",
    "SAME_SOURCE": "BLEIBT DIE QUELLE DIESELBE?",
    "CURRENT_ITEM": "WELCHER POSTEN IST JETZT AKTIV?",
    "WORKING_MATERIAL": "WELCHES ARBEITSMATERIAL LIEGT VOR?",
    "PROCESS": "WIE WIRD ES BEARBEITET?",
    "STATE_GATE": "BIS WANN ODER BIS ZU WELCHEM ZUSTAND?",
    "USE_OR_EXECUTE": "WAS IST JETZT AUSZUFÜHREN?",
    "DESTINATION": "WOHIN ODER AN WELCHES ZIEL?",
    "TRANSFER_CLEAN": "WIE SPÜLEN, SEIHEN ODER ABLASSEN?",
    "HEAT_REST": "WIE ERHITZEN, KÜHLEN ODER RUHEN LASSEN?",
    "APPLICATION": "WIE ANWENDEN, BADEN ODER BINDEN?",
    "OWNER_OR_PART": "WELCHER SIMPLEX ODER PFLANZENTEIL?",
    "MEDIUM_OR_INGREDIENT": "WELCHES MEDIUM ODER WELCHER ZUSATZ?",
    "INDICATION": "FÜR WELCHEN BESCHWERDE- ODER ANWENDUNGSFALL?",
    "ARTICLE_DETAIL": "WELCHE WEITERE ARTIKELANGABE?",
    "PROCEDURE_DETAIL": "WELCHER WEITERE ARBEITSSCHRITT?",
}


def fallback_roles(page: str, meanings: str, classes: str) -> list[str]:
    text = (meanings + " " + classes).lower()
    roles = []
    if any(x in text for x in ("wash", "rinse", "strain", "drain", "draw off", "cloth", "outlet", "channel")):
        roles.append("TRANSFER_CLEAN")
    if any(x in text for x in ("heat", "boil", "warm", "cool", "stand", "settle", "ready")):
        roles.append("HEAT_REST")
    if any(x in text for x in ("apply", "use", "bathe", "immerse", "bind", "plaster", "poultice")):
        roles.append("APPLICATION")
    if any(x in text for x in ("root", "leaf", "flower", "plant", "simple", "crown")):
        roles.append("OWNER_OR_PART")
    if any(x in text for x in ("wine", "water", "honey", "oil", "juice", "liquid", "ingredient")):
        roles.append("MEDIUM_OR_INGREDIENT")
    if any(x in text for x in ("pain", "wound", "swollen", "stomach", "sore", "place")):
        roles.append("INDICATION")
    if not roles:
        roles.append("ARTICLE_DETAIL" if page in {"f10r", "f11r", "f55v", "f56r"} else "PROCEDURE_DETAIL")
    return roles


def unique(seq: list[str]) -> list[str]:
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open(encoding="utf-8", newline="") as f:
        ledger = list(csv.DictReader(f, delimiter="\t"))
    with CORE.open(encoding="utf-8", newline="") as f:
        core = {r["exact_tuple_id"]: r for r in csv.DictReader(f, delimiter="\t")}
    assert len(ledger) == 381 and len(core) == 12

    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / "gdt327_joint_tuple_interlinear.tsv"), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--columns", "page,locus,group_index,record_ordinal,field_ordinal,within_field_position,joint_tuple_id,dy_closure,b3", "--forbid-prefix", "f84"]
    text = subprocess.run(cmd, check=True, text=True, capture_output=True).stdout
    lines = [line for line in text.splitlines() if not line.startswith("GUARD_STATS ")]
    formal = list(csv.DictReader(lines, delimiter="\t"))
    meta = {(r["page"], r["locus"], r["group_index"]): r for r in formal}

    fields = defaultdict(list)
    for row in ledger:
        m = meta[(row["page"], row["locus"], row["event_index"])]
        fields[(row["page"], m["record_ordinal"], row["locus"], m["field_ordinal"])].append((row, m))

    field_rows = []
    for (page, record, locus, field_no), events in fields.items():
        roles = []
        for row, _ in events:
            if row["exact_tuple_id"] in core:
                roles.append(ROLE_MAP[core[row["exact_tuple_id"]]["anonymous_workshop_role"]])
        meanings = " / ".join(row["effective_default"] for row, _ in events)
        classes = " / ".join(row["anonymous_workshop_role"] for row, _ in events)
        roles = unique(roles + fallback_roles(page, meanings, classes))
        closure = "DY" if events[-1][1]["dy_closure"] == "1" else "B3" if events[-1][1]["b3"] == "1" else "OPEN_FIELD_END"
        field_rows.append({
            "page": page, "record_ordinal": record, "locus": locus,
            "field_ordinal": field_no, "event_count": len(events),
            "visible_field": " ".join(row["surface"] for row, _ in events),
            "primary_role": roles[0],
            "secondary_roles": "+".join(roles[1:]),
            "worksheet_roles": "+".join(roles),
            "workshop_questions_German": " | ".join(PROMPT[r] for r in roles),
            "complete_card_defaults": meanings,
            "closure": closure,
            "field_status": "COMPLETE_DEFAULT_ROLE_NO_BLANK",
        })
    field_rows.sort(key=lambda r: (PAGES.index(r["page"]), int(r["record_ordinal"]), int(r["locus"].split(".")[1]), int(r["field_ordinal"])))
    write(HERE / "V41_135_FIELD_WORKSHEET.tsv", field_rows)

    records = defaultdict(list)
    for row in field_rows:
        records[(row["page"], row["record_ordinal"])].append(row)
    record_rows = []
    for (page, record), rr in records.items():
        record_rows.append({
            "page": page, "record_ordinal": record,
            "register_default": "HERBAL_SIMPLE_ARTICLE" if page in {"f10r", "f11r", "f55v", "f56r"} else "BIOLOGICAL_PROCEDURE_SHEET",
            "field_count": len(rr), "event_count": sum(int(x["event_count"]) for x in rr),
            "ordered_primary_path": " -> ".join(x["primary_role"] for x in rr),
            "ordered_role_path": " -> ".join(x["worksheet_roles"] for x in rr),
            "ordered_question_path": " || ".join(x["workshop_questions_German"] for x in rr),
            "closure_path": " -> ".join(x["closure"] for x in rr),
            "record_status": "COMPLETE_WORKSHEET_PATH_NO_BLANK",
        })
    record_rows.sort(key=lambda r: (PAGES.index(r["page"]), int(r["record_ordinal"])))
    write(HERE / "V41_ELEVEN_RECORD_WORKSHEETS.tsv", record_rows)

    role_counts = Counter(role for row in field_rows for role in row["worksheet_roles"].split("+"))
    role_rows = [{"role": k, "fields": v, "question_German": PROMPT[k]} for k, v in role_counts.most_common()]
    write(HERE / "V41_ROLE_INVENTORY.tsv", role_rows)
    primary_counts = Counter(row["primary_role"] for row in field_rows)
    primary_rows = [{"primary_role": k, "fields": v, "question_German": PROMPT[k]} for k, v in primary_counts.most_common()]
    write(HERE / "V41_PRIMARY_ROLE_INVENTORY.tsv", primary_rows)

    summary = {
        "schema": "SIDEQUEST_V41_RECORD_WORKSHEET_GRAMMAR_V1",
        "status": "COMPLETE_FIELD_AND_RECORD_PROMPT_GRAMMAR_SELECTED",
        "events": len(ledger), "fields": len(field_rows), "records": len(record_rows),
        "worksheet_roles": len(role_counts),
        "primary_roles": len(primary_counts),
        "fields_without_role": sum(not r["worksheet_roles"] for r in field_rows),
        "records_without_complete_path": sum(not r["ordered_role_path"] for r in record_rows),
        "herbal_records": sum(r["register_default"] == "HERBAL_SIMPLE_ARTICLE" for r in record_rows),
        "biological_records": sum(r["register_default"] == "BIOLOGICAL_PROCEDURE_SHEET" for r in record_rows),
        "f84_rows_accessed": 0, "f84r_rows_accessed": 0,
    }
    (HERE / "V41_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
