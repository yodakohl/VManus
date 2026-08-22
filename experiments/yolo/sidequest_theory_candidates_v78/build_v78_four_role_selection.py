#!/usr/bin/env python3
"""Select the V78 continuous edition and expose the PER catchword repair."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> Path:
    path = HERE / name
    with path.open("w", encoding="utf-8", newline="") as fh:
        out = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    r1_fit = {r["event_serial"]: r for r in read("V78_R1_ET_PER_28_FIT.tsv")}
    r2_events = read("V78_R2_381_EVENT_INTERLINEAR.tsv")
    r2_records = read("V78_R2_11_CONTINUOUS_RECORDS.tsv")
    r3_events = {r["event_serial"]: r for r in read("V78_R3_381_EVENT_CONTINUITY.tsv")}
    r3_statements = read("V78_R3_116_STATEMENT_CONTINUITY.tsv")
    r4_fit = {r["event_serial"]: r for r in read("V78_R4_ET_PER_FIT_AUDIT.tsv")}
    assert len(r2_events) == 381 and len(r2_records) == 11 and len(r3_statements) == 116

    selected_events: list[dict[str, object]] = []
    for r in r2_events:
        event = r["event_serial"]
        token = r["continuous_event_token"]
        if event == "180":
            selected_status = "PER_CATCHWORD_COPY__READ_WITH_E181_ONCE"
            token = "[KUSTODE:PER?; AM NAECHSTEN ZEILENANFANG WIEDERHOLT; NICHT DOPPELT SPRECHEN]"
        elif event == "181":
            selected_status = "PER_MAIN_TOKEN_AFTER_CATCHWORD__PROBATIONARY"
            token = "PER? (DURCH/GEMÄSS?)"
        elif r["portable_token_or_formal_prompt"].startswith("ET?"):
            selected_status = "ET_RETAIN_PROVISIONAL__FORMAL_LINK_RIVAL_TIED"
        elif r["portable_token_or_formal_prompt"].startswith("PER?"):
            selected_status = "PER_RETAIN_PROBATIONARY__FORMAL_ENTRY_RIVAL_TIED"
        elif r["portable_status"] == "FORMAL_LABEL_NOT_WORD":
            selected_status = "FORMAL_LABEL_NOT_WORD"
        else:
            selected_status = "EXEMPLAR_VALUE_UNKNOWN"
        selected_events.append({
            **r,
            "v78_central_status": selected_status,
            "selected_continuous_event_token": token,
            "central_repair": (
                "LINE_FINAL_CATCHWORD_COPY_OF_E181__ONE_SOURCE_TOKEN_TWO_VISIBLE_COPIES"
                if event == "180" else
                "MAIN_PER_TOKEN_AFTER_LINE_FINAL_CATCHWORD_COPY"
                if event == "181" else "NONE"
            ),
            "selection_ceiling": "CONTINUOUS_CREATIVE_WORKING_EDITION_NOT_PLAINTEXT",
        })
    event_out = write("V78_SELECTED_381_EVENT_INTERLINEAR.tsv", selected_events)

    selected_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in selected_events:
        selected_by_statement[str(r["statement_id"])].append(r)
    statement_rows: list[dict[str, object]] = []
    for base in r3_statements:
        rows = selected_by_statement[base["statement_id"]]
        statement_rows.append({
            **base,
            "selected_event_tokens": " ".join(str(r["selected_continuous_event_token"]) for r in rows),
            "selected_catchword_repair": "YES__E180_E181_READ_ONCE" if base["statement_id"] == "B2-S005" else "NONE",
            "v78_selection_status": "SELECTED_R3_CONTINUITY_WITH_R2_HISTORICAL_EVENT_LAYER",
        })
    statement_out = write("V78_SELECTED_116_STATEMENTS.tsv", statement_rows)

    record_rows: list[dict[str, object]] = []
    for r in r2_records:
        reading = r["continuous_german_working_reading"].replace(
            "PER? (DURCH/GEMÄSS?) PER? (DURCH/GEMÄSS?)",
            "[KUSTODE:PER?; NUR EINMAL LESEN] PER? (DURCH/GEMÄSS?)",
        )
        record_rows.append({
            **r,
            "selected_continuous_german_working_reading": reading,
            "central_word_status": (
                "ET_PROVISIONAL;PER_PROBATIONARY_WITH_CATCHWORD_RULE"
                if int(r["et_count"]) + int(r["per_count"]) else
                "NO_PORTABLE_WORD_OCCURRENCE"
            ),
            "v78_selection_status": "SELECTED_R2_HISTORICAL_CONTINUOUS_EDITION",
        })
    record_out = write("V78_SELECTED_11_CONTINUOUS_RECORDS.tsv", record_rows)

    fit_rows: list[dict[str, object]] = []
    r2_by_event = {r["event_serial"]: r for r in r2_events}
    for event in sorted(r1_fit, key=int):
        a, b, c, d = r1_fit[event], r2_by_event[event], r3_events[event], r4_fit[event]
        is_et = a["role_card"] == "ET?"
        if event == "180":
            verdict = "PER_CATCHWORD_COPY__READ_WITH_E181_ONCE"
            v79_test = "Apprentice must copy at line edge and suppress the first copy in spoken/source-token count."
        elif event == "181":
            verdict = "PER_MAIN_TOKEN_AFTER_CATCHWORD__PROBATIONARY"
            v79_test = "Apprentice must recover one PER relation plus one preceding catchword copy."
        elif is_et:
            verdict = "ET_PROVISIONAL_SURVIVES__FORMAL_LINK_RIVAL_LIVE"
            v79_test = "Backward reconstruction must choose ET over a silent link without adding lexical senses."
        else:
            verdict = "PER_PROBATIONARY_SURVIVES__FORMAL_ENTRY_RIVAL_LIVE"
            v79_test = "Every non-catchword PER must govern one explicit bracketed complement."
        fit_rows.append({
            "event_serial": event, "record_unit_id": b["record_unit_id"],
            "page": b["page"], "locus": b["locus"], "field_id": b["field_id"],
            "statement_id": b["statement_id"], "joint_tuple_id": b["joint_tuple_id"],
            "word_candidate": a["role_card"],
            "r1_fit_grade": a["fit_grade"], "r1_fit_reason": a["fit_reason"],
            "r2_syntax_status": b["et_per_syntax_status"], "r2_syntax_reason": b["et_per_syntax_reason"],
            "r3_pressure_flags": c["local_grammar_pressure_flags"], "r3_formal_rival": c["formal_link_or_entry_rival"],
            "r4_fit_grade": d["fit_grade"], "r4_fit_class": d["fit_class"],
            "central_verdict": verdict, "v79_apprentice_test": v79_test,
            "confirmed_translation": "NO",
        })
    fit_out = write("V78_SELECTED_ET_PER_28_AUDIT.tsv", fit_rows)

    checks = {
        "selected_events_381": len(selected_events) == 381,
        "selected_statements_116": len(statement_rows) == 116,
        "selected_records_11": len(record_rows) == 11,
        "fit_rows_28": len(fit_rows) == 28,
        "et_rows_19": sum(r["word_candidate"] == "ET?" for r in fit_rows) == 19,
        "per_rows_9": sum(r["word_candidate"] == "PER?" for r in fit_rows) == 9,
        "catchword_pair_exact_180_181": [r["event_serial"] for r in fit_rows if "CATCHWORD" in r["central_verdict"]] == ["180", "181"],
        "only_two_word_candidates": {r["word_candidate"] for r in fit_rows} == {"ET?", "PER?"},
        "all_concrete_expansions_bracketed": all(r["source_expansion_de"].startswith("[EXEMPLAR:") for r in selected_events),
        "no_confirmed_translation": all(r["confirmed_translation"] == "NO" for r in fit_rows),
        "no_f84": all(not r["page"].startswith("f84") for r in selected_events),
    }
    files = [
        "V78_R1_381_EVENT_CONTINUOUS_INTERLINEAR.tsv", "V78_R1_11_RECORD_CONTINUOUS.tsv",
        "V78_R2_381_EVENT_INTERLINEAR.tsv", "V78_R2_11_CONTINUOUS_RECORDS.tsv",
        "V78_R3_381_EVENT_CONTINUITY.tsv", "V78_R3_116_STATEMENT_CONTINUITY.tsv",
        "V78_R4_381_EVENT_CONTINUOUS_INTERLINEAR.tsv", "V78_R4_ET_PER_FIT_AUDIT.tsv",
        event_out.name, statement_out.name, record_out.name, fit_out.name,
    ]
    validation = {
        "schema": "SIDEQUEST_V78_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "bindings": {name: digest(HERE / name) for name in files},
    }
    (HERE / "V78_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
