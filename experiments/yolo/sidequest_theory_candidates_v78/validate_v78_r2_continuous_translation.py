#!/usr/bin/env python3
"""Executable validation for the independent V78 R2 edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVENTS = HERE / "V78_R2_381_EVENT_INTERLINEAR.tsv"
RECORDS = HERE / "V78_R2_11_CONTINUOUS_RECORDS.tsv"
ORDER = HERE / "V78_R2_SOURCE_ORDER_CONTRADICTIONS.tsv"
RESULT = HERE / "V78_R2_RESULT.json"
OUT = HERE / "V78_R2_VALIDATION.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
PARAMETER_CARD = "2f1c5e56e8f0ff459065"
RELATION_CARD = "308e8ea2d5d190c498e8"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read_tsv(EVENTS)
    records = read_tsv(RECORDS)
    order = read_tsv(ORDER)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: dict[str, object] = {}

    serials = [int(row["event_serial"]) for row in events]
    checks["event_rows_381"] = len(events) == 381
    checks["event_serials_exact_1_381"] = serials == list(range(1, 382))
    checks["event_ids_unique"] = len({row["event_id"] for row in events}) == 381
    checks["statements_116"] = len(order) == 116 and len({row["statement_id"] for row in order}) == 116
    checks["records_11_in_order"] = [row["record_unit_id"] for row in records] == RECORD_ORDER
    checks["record_event_total_381"] = sum(int(row["event_count"]) for row in records) == 381
    checks["record_event_partition_exact"] = sorted(
        int(token) for row in records for token in row["event_serials"].split("|") if token
    ) == list(range(1, 382))

    et = [row for row in events if row["joint_tuple_id"] == ET_CARD]
    per = [row for row in events if row["joint_tuple_id"] == PER_CARD]
    checks["et_exact_count_19"] = len(et) == 19
    checks["per_exact_count_9"] = len(per) == 9
    checks["et_literal_fixed_everywhere"] = all(
        row["portable_token_or_formal_prompt"] == "ET? (UND/AUCH?)"
        and "CODEBOOK-KATEGORIE:ET? (UND/AUCH?)" in row["literal_card_layer"]
        for row in et
    )
    checks["per_literal_fixed_everywhere"] = all(
        row["portable_token_or_formal_prompt"] == "PER? (DURCH/GEMÄSS?)"
        and "CODEBOOK-KATEGORIE:PER? (DURCH/GEMÄSS?)" in row["literal_card_layer"]
        for row in per
    )
    checks["no_old_et_or_per_formal_gloss"] = all(
        "AKTIVEN_ARBEITSSTAND" not in row["literal_card_layer"]
        and "STANDARDSLOT" not in row["literal_card_layer"]
        for row in et + per
    )
    checks["et_no_hard_syntax_break"] = not any(
        row["et_per_syntax_status"].startswith("HARD_SYNTAX_BREAK") for row in et
    )
    per_breaks = [int(row["event_serial"]) for row in per if row["et_per_syntax_status"].startswith("HARD_SYNTAX_BREAK")]
    checks["per_breaks_frozen_e180_e181"] = per_breaks == [180, 181]

    parameter = [row for row in events if row["joint_tuple_id"] == PARAMETER_CARD]
    relation = [row for row in events if row["joint_tuple_id"] == RELATION_CARD]
    checks["parameter_is_nonword_everywhere"] = len(parameter) == 20 and all(
        row["portable_token_or_formal_prompt"] == "[FORMAL:VORGABEPARAMETER?; KEIN WORT]"
        for row in parameter
    )
    checks["relation_is_nonword_everywhere"] = len(relation) == 6 and all(
        row["portable_token_or_formal_prompt"] == "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]"
        for row in relation
    )
    checks["only_two_portable_words"] = {
        row["portable_token_or_formal_prompt"]
        for row in events
        if row["portable_status"].startswith("PROVISIONAL_CODEBOOK_WORD")
    } == {"ET? (UND/AUCH?)", "PER? (DURCH/GEMÄSS?)"}
    checks["all_source_expansions_bracketed"] = all(
        row["source_expansion_de"].startswith("[EXEMPLAR:") and row["source_expansion_de"].endswith("]")
        for row in events
    )
    checks["all_owner_expansions_bracketed"] = all(
        row["image_owner_exemplar"].startswith("[EXEMPLAR:") and row["image_owner_exemplar"].endswith("]")
        for row in events
    )
    checks["physical_lines_never_declared_sentence_ends"] = all(
        row["line_boundary_policy"] == "PHYSICAL_LINE_IS_NOT_A_SENTENCE_BOUNDARY" for row in order
    ) and all("CONTINUOUS_ACROSS_PHYSICAL_LINES" in row["line_policy"] for row in records)
    checks["semantic_ceiling_on_every_event"] = all(
        row["semantic_ceiling"] == "BRACKETED_SOURCE_EXEMPLAR_NOT_CARD_STEM_SOUND_LANGUAGE_OR_DECIPHERMENT"
        for row in events
    )

    # The literal layer must never revive the eleven withdrawn V69/V73/V74
    # portable meanings. Contextual bracketed exemplars may, by design, still
    # describe a source action.
    withdrawn_literal_terms = [
        "CARD:MASS", "CARD:ANWENDEN", "CARD:BEREIT", "CARD:ANSATZ", "CARD:ZIEL",
        "CARD:KLAR", "CARD:VORIGES", "CARD:ANTEIL", "CARD:TEMPERIEREN",
        "CARD:SPÜLEN", "CARD:ABLASSEN",
    ]
    checks["withdrawn_card_glosses_absent_from_literal_layer"] = not any(
        term in row["literal_card_layer"] for term in withdrawn_literal_terms for row in events
    )

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in [EVENTS, RECORDS, ORDER, RESULT])
    checks["sealed_pages_not_accessed_or_named_as_inputs"] = "f84." not in output_text and "f84r." not in output_text
    checks["result_matches_tables"] = (
        result["event_rows"] == len(events)
        and result["statement_rows"] == len(order)
        and result["record_rows"] == len(records)
        and result["et_occurrences"] == len(et)
        and result["per_occurrences"] == len(per)
    )

    failures = [name for name, passed in checks.items() if passed is not True]
    validation = {
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
        "counts": {
            "events": len(events),
            "statements": len(order),
            "records": len(records),
            "et": len(et),
            "per": len(per),
            "per_hard_breaks": per_breaks,
            "record_event_counts": dict(Counter(row["record_unit_id"] for row in events)),
        },
    }
    OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("validation failed: " + ", ".join(failures))
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
