#!/usr/bin/env python3
"""Select the V77 four-role working dictionary without changing source rows."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        out = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    r1 = {r["joint_tuple_id"]: r for r in read(HERE / "V77_R1_BOUNDED_CARD_DECISIONS.tsv")}
    r2 = {r["anonymous_exact_card_id"]: r for r in read(HERE / "V77_R2_CARD_DECISIONS.tsv")}
    r3 = {r["joint_tuple_id"]: r for r in read(HERE / "V77_R3_DECISION_TABLE.tsv")}
    r4_rows = read(HERE / "V77_R4_BOUNDED_CARD_DECISIONS.tsv")
    assert len(r1) == len(r2) == len(r3) == len(r4_rows) == 24

    selected: list[dict[str, object]] = []
    for r in r4_rows:
        tid = r["joint_tuple_id"]
        decision = r["decision"]
        if decision == "CODEBOOK_ATTESTED_CATEGORY":
            selection = "PROVISIONAL_CODEBOOK_WORD__MINORITY_CREATIVE_LEAD"
            usable = "YES_WITH_QUESTION_MARK"
        elif decision == "FORMAL_LABEL_NOT_WORD":
            selection = "FORMAL_LABEL_NOT_WORD"
            usable = "NO__NOT_A_WORD"
        else:
            selection = "EXEMPLAR_VALUE_UNKNOWN"
            usable = "NO"
        selected.append({
            **r,
            "r1_decision": r1[tid]["final_atomic_default"],
            "r2_decision": r2[tid]["final_decision"],
            "r3_decision": r3[tid]["portable_dictionary_decision"],
            "r4_decision": decision,
            "selection_status": selection,
            "usable_as_v78_working_word": usable,
            "selection_rationale": (
                "R4 expands the frozen source corpus with genuine 1414 whole-word signs and proposes a new atomic reading after source freeze; retain as a falsifiable creative minority lead rather than let three no-match audits veto exploration."
                if decision == "CODEBOOK_ATTESTED_CATEGORY"
                else "No positive source-plus-context match; keep the strict consensus status."
            ),
            "confirmation_status": "UNCONFIRMED_CREATIVE_SIDEQUEST",
        })
    out = HERE / "V77_SELECTED_CARD_DICTIONARY.tsv"
    write(out, list(selected[0]), selected)

    audit = read(HERE / "V77_R4_FULL_OCCURRENCE_AUDIT.tsv")
    selected_by_id = {r["joint_tuple_id"]: r for r in selected}
    selected_audit = []
    for r in audit:
        s = selected_by_id[r["joint_tuple_id"]]
        selected_audit.append({
            **r,
            "selected_dictionary_status": s["selection_status"],
            "selected_working_word": s["minimal_editorial_gloss"] if s["usable_as_v78_working_word"] == "YES_WITH_QUESTION_MARK" else "NONE",
        })
    audit_out = HERE / "V77_SELECTED_197_OCCURRENCE_AUDIT.tsv"
    write(audit_out, list(selected_audit[0]), selected_audit)

    checks = {
        "four_role_inputs_24_each": len(r1) == len(r2) == len(r3) == len(r4_rows) == 24,
        "selected_cards_24": len(selected) == 24,
        "selected_occurrences_197": len(selected_audit) == 197,
        "two_provisional_words": sum(r["selection_status"].startswith("PROVISIONAL_CODEBOOK_WORD") for r in selected) == 2,
        "two_formal_nonwords": sum(r["selection_status"] == "FORMAL_LABEL_NOT_WORD" for r in selected) == 2,
        "twenty_unknown": sum(r["selection_status"] == "EXEMPLAR_VALUE_UNKNOWN" for r in selected) == 20,
        "working_words_keep_question_mark": all("?" in r["minimal_editorial_gloss"] for r in selected if r["usable_as_v78_working_word"] == "YES_WITH_QUESTION_MARK"),
        "no_confirmed_translation_claim": all(r["confirmation_status"] == "UNCONFIRMED_CREATIVE_SIDEQUEST" for r in selected),
        "no_f84": all(not r["page"].startswith("f84") for r in selected_audit),
    }
    bindings = {}
    for name in [
        "V77_TARGET_FREEZE.tsv",
        "V77_R1_BOUNDED_CARD_DECISIONS.tsv",
        "V77_R2_CARD_DECISIONS.tsv",
        "V77_R3_DECISION_TABLE.tsv",
        "V77_R4_BOUNDED_CARD_DECISIONS.tsv",
        "V77_R4_SOURCE_FIRST_CODEBOOK_INVENTORY.tsv",
        out.name,
        audit_out.name,
    ]:
        bindings[name] = digest(HERE / name)
    validation = {
        "schema": "SIDEQUEST_V77_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "bindings": bindings,
    }
    (HERE / "V77_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("validation failed")
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
