#!/usr/bin/env python3
"""Build V88 by separating seven portable cores from local axes/patients."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt715_v88_axis_action_patient_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G714 = ROOT / "experiments/yolo/gdt714_v87_bound_c1_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G714 / "V87_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G714 / "V87_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G714 / "V87_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G714 / "V87_109_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G714 / "V87_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V88_7_AUDIT_SPECS.tsv"
PRIMARY_BINDINGS = SRC / "V88_19_PRIMARY_EVIDENCE_BINDINGS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V88_7_AXIS_ACTION_READINGS_REVISED__2_VALUE_CORES_5_ACTION_CORES__"
    "7_TARGET_POSITIONS_7_PAGES__84_WEAK_READINGS_REMAIN__"
    "F7R2_RERENDERED__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for source in rows:
            writer.writerow({field: source.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


def ordered_compact(values: Iterable[str], separator: str = "|", empty: str = "NONE") -> str:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if value and value not in {"NONE", "0"} and value not in seen:
            seen.add(value)
            output.append(value)
    return separator.join(output) if output else empty


def append_pipe(value: str, addition: str) -> str:
    return ordered_compact([*split_pipe(value), addition])


def unique_fields(fields: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(fields))


def level(score: int) -> str:
    if score < 20:
        return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40:
        return "W1_WEAK_WORKING"
    if score < 60:
        return "W2_PROVISIONAL_WORKING"
    if score < 80:
        return "W3_SOLID_WORKING_THEORY"
    return "W4_STRONG_WORKING_THEORY"


def v88_key(value: str) -> str:
    return value.replace("v87", "v88").replace("V87", "V88")


def rename_v87_fields(row: dict[str, str]) -> dict[str, str]:
    return {v88_key(key): value for key, value in row.items()}


def family_v88_key(value: str) -> str:
    return value.replace("v84", "v88").replace("V84", "V88")


def primary_evidence_rows(
    bindings: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Resolve every authored evidence claim against one exact primary row."""
    spec_ids = {row["source_reading_id"] for row in specs}
    output: list[dict[str, Any]] = []
    credit_by_source: dict[str, list[str]] = defaultdict(list)
    for binding in bindings:
        source_id = binding["source_reading_id"]
        assert source_id in spec_ids
        assert "f84" not in binding["evidence_path"].lower()
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        assert all(not value.lower().startswith("f84") for value in selector.values())
        source_path = ROOT / binding["evidence_path"]
        matches = [
            row for row in read_tsv(source_path)
            if all(row.get(field) == expected for field, expected in selector.items())
        ]
        assert len(matches) == 1, (binding["binding_id"], len(matches))
        source = matches[0]
        for field, expected in assertions.items():
            assert source.get(field) == expected, (binding["binding_id"], field, source.get(field), expected)
        credits = split_pipe(binding["score_credit_family_ids"])
        credit_by_source[source_id].extend(credits)
        fingerprint = hashlib.sha256(
            json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        output.append({
            **binding,
            "matched_row_fingerprint_sha256": fingerprint,
            "source_row_match": 1,
            "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
            "historical_confirmation": HISTORICAL,
        })
    bonus_by_family = {row["family_id"]: int(row["family_bonus"]) for row in read_tsv(SOURCE_FAMILIES)}
    score_deltas: dict[str, int] = {}
    for spec in specs:
        source_id = spec["source_reading_id"]
        credits = credit_by_source[source_id]
        assert len(credits) == len(set(credits))
        assert set(credits) == set(split_pipe(spec["score_credit_family_ids"]))
        score_deltas[source_id] = sum(bonus_by_family[family] for family in credits)
        assert score_deltas[source_id] == int(spec["score_delta_lexical_core"])
    return output, score_deltas


def lexical_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], score_deltas: dict[str, int]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v87_fields(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v87_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            delta = score_deltas[spec["source_reading_id"]]
            score = min(base + delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v88_lexical_core_de": spec["v88_lexical_core_de"],
                "v88_context_realizations_de": spec["v88_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT715",
                "base_score": base,
                "score_delta_lexical_core": delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT715"),
                "positive_evidence_de": (
                    "GDT715 trennt Wortkern und einmaligen Kontext: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT715 Gegenbeleg: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v88_audit_decision": spec["decision"],
                "v88_evidence_class": spec["evidence_class"],
                "v88_open_semantic_slots": spec["open_semantic_slots"],
                "v88_component_global_export_allowed": spec["component_global_export_allowed"],
                "v88_prior_lexical_core_de": source["v87_lexical_core_de"],
            })
        else:
            row.update({
                "v88_audit_decision": "NOT_IN_GDT715_TRANCHE",
                "v88_evidence_class": "INHERITED_V87",
                "v88_open_semantic_slots": "NOT_EVALUATED",
                "v88_component_global_export_allowed": "NOT_EVALUATED",
                "v88_prior_lexical_core_de": source["v87_lexical_core_de"],
            })
        output.append(row)

    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def context_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    source_by_locus_ordinal = {
        (row["locus"], int(row["token_ordinal"])): row for row in source_rows
    }
    output: list[dict[str, Any]] = []
    seen_targets: Counter[str] = Counter()
    for source in source_rows:
        row: dict[str, Any] = rename_v87_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        if spec:
            seen_targets[source_id] += 1
            assert source["position_id"] == spec["expected_position_id"]
            assert source["page"] == spec["expected_page"]
            assert source["locus"] == spec["expected_locus"]
            assert source["token_ordinal"] == spec["expected_token_ordinal"]
            left = source_by_locus_ordinal[(source["locus"], int(source["token_ordinal"]) - 1)]
            assert left["surface"] == spec["expected_left_surface"]
        row.update({
            "v88_reading_id": lexical["v88_reading_id"],
            "v88_lexical_core_de": lexical["v88_lexical_core_de"],
            "v88_context_realization_de": spec["v88_context_realization_de"] if spec else source["v87_context_realization_de"],
            "v88_repair_mode": spec["repair_mode"] if spec else source["v87_repair_mode"],
            "v88_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v87_resolved_debt_atom"],
            "v88_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v88_lexical_level": lexical["working_model_level"],
            "v88_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v88_context_level": lexical["context_realization_level"],
            "v88_semantic_scope": lexical["semantic_scope"],
            "v88_semantic_applicability": lexical["semantic_applicability"],
            "v88_global_export_scope": lexical["global_export_scope"],
            "v88_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v88_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v88_historical_confirmation": HISTORICAL,
            "v88_audit_decision": spec["decision"] if spec else "NOT_IN_GDT715_TRANCHE",
            "v88_evidence_class": spec["evidence_class"] if spec else "INHERITED_V87",
            "v88_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v88_component_global_export_allowed": spec["component_global_export_allowed"] if spec else "NOT_EVALUATED",
            "v88_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v88_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
        })
        output.append(row)
    assert seen_targets == Counter({row["source_reading_id"]: 1 for row in specs})
    return output


def census_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        row: dict[str, Any] = rename_v87_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V88",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v88_reading_id": lexical["v88_reading_id"],
                "v88_lexical_core_de": lexical["v88_lexical_core_de"],
                "v88_context_realization_de": spec["v88_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v88_audit_decision": spec["decision"],
                "v88_evidence_class": spec["evidence_class"],
                "v88_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v88_reading_id": lexical["v88_reading_id"],
                "v88_lexical_core_de": lexical["v88_lexical_core_de"],
                "v88_context_realization_de": lexical["v88_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v88_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v88_evidence_class": "INHERITED_V87",
                "v88_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    return output


def delta_rows(
    specs: list[dict[str, str]], source_lexical: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_by_id: dict[str, dict[str, str]] = {}
    for row in source_lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            source_by_id[source_id] = row
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_by_source[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"],
            "surface": source["surface"],
            "decision": spec["decision"],
            "position_id": spec["expected_position_id"],
            "page": spec["expected_page"],
            "locus": spec["expected_locus"],
            "token_ordinal": spec["expected_token_ordinal"],
            "left_surface": spec["expected_left_surface"],
            "old_lexical_core_de": source["v87_lexical_core_de"],
            "v88_lexical_core_de": target["v88_lexical_core_de"],
            "v88_context_realization_de": spec["v88_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v88_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "v88_level": target["working_model_level"],
            "family_ids": spec["family_ids"],
            "score_credit_family_ids": spec["score_credit_family_ids"],
            "decomposition": spec["decomposition"],
            "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"],
            "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "component_global_export_allowed": spec["component_global_export_allowed"],
            "local_context_hypothesis": spec["local_context_hypothesis"],
            "historical_confirmation": HISTORICAL,
        })
    return output


def family_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    wanted = {family for spec in specs for family in split_pipe(spec["family_ids"])}
    specs_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            specs_by_family[family].append(spec)
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["family_id"] not in wanted:
            continue
        selected = specs_by_family[source["family_id"]]
        row: dict[str, Any] = {family_v88_key(key): value for key, value in source.items()}
        row.update({
            "selected_source_readings": len(selected),
            "selected_lexical_readings": len(selected),
            "selected_positions": len(selected),
            "selected_pages": len({spec["expected_page"] for spec in selected}),
            "selected_source_reading_ids": ordered_compact(spec["source_reading_id"] for spec in selected),
            "selected_surfaces": ordered_compact(target_by_source[spec["source_reading_id"]]["surface"] for spec in selected),
            "selected_v88_reading_ids": ordered_compact(target_by_source[spec["source_reading_id"]]["v88_reading_id"] for spec in selected),
            "selected_v88_levels": ordered_compact(target_by_source[spec["source_reading_id"]]["working_model_level"] for spec in selected),
            "automatic_historical_credit": 0,
            "historical_confirmation": HISTORICAL,
            "v88_decisions": ordered_compact(spec["decision"] for spec in selected),
        })
        output.append(row)
    return output


def complete_rows(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V87_LEXICAL_CORE":
            continue
        row: dict[str, Any] = rename_v87_fields(source)
        row.update({
            "v88_audit_decision": "OUTSIDE_ACTIVE_V88_TRANCHE",
            "v88_evidence_class": "INHERITED_GLOBAL_V48",
            "v88_open_semantic_slots": "NOT_EVALUATED",
            "v88_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"],
            "reading_id": row["v88_reading_id"],
            "working_meaning_de": row["v88_lexical_core_de"],
            "current_layer": "ACTIVE_V88_LEXICAL_CORE",
            "semantic_scope": row["semantic_scope"],
            "semantic_applicability": row["semantic_applicability"],
            "form_level": row["form_level"],
            "occurrence_count": row["occurrence_count"],
            "page_count": row["page_count"],
            "locus_count": row["locus_count"],
            "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"],
            "working_model_level": row["working_model_level"],
            "source_gdts": row["source_gdts"],
            "positive_evidence_de": row["positive_evidence_de"],
            "counterevidence_de": row["counterevidence_de"],
            "historical_confirmation": row["historical_confirmation"],
            "historical_analogue": row["historical_analogue"],
            "relation_word_delta": row["relation_word_delta"],
            "global_export_scope": row["global_export_scope"],
            "bound_span_ids": row["bound_span_ids"],
            "unconditional_global_export_allowed": row["unconditional_global_export_allowed"],
            "v88_context_realizations_de": row["v88_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"],
            "v88_audit_decision": row["v88_audit_decision"],
            "v88_evidence_class": row["v88_evidence_class"],
            "v88_open_semantic_slots": row["v88_open_semantic_slots"],
            "v88_component_global_export_allowed": row["v88_component_global_export_allowed"],
        })
    return sorted(output, key=lambda item: (str(item["surface"]), str(item["reading_id"])))


def one_shot_directive_rows(
    contexts: list[dict[str, Any]], spans: list[dict[str, str]], locus: str
) -> list[dict[str, Any]]:
    by_position = {str(row["position_id"]): row for row in contexts}
    selected = [row for row in spans if row["locus"] == locus]
    assert len(selected) == 1
    output: list[dict[str, Any]] = []
    for span in selected:
        for side, action in (("left", "EMIT_SPAN_ONCE"), ("right", "CONSUME_NO_OUTPUT")):
            source = by_position[span[f"{side}_position_id"]]
            output.append({
                "render_unit_id": f"R_{span['bound_span_id']}",
                "page": span["page"],
                "locus": span["locus"],
                "bound_span_id": span["bound_span_id"],
                "anchor_position_id": span["left_position_id"],
                "source_position_id": source["position_id"],
                "source_token_ordinal": source["token_ordinal"],
                "source_surface": source["surface"],
                "source_reading_id": source["source_reading_id"],
                "span_role": span[f"{side}_role"],
                "render_action": action,
                "emitted_text_de": span["render_once_de"] if side == "left" else "",
                "source_context_consumed": 1,
                "global_export_allowed": span["global_export_allowed"],
            })
    return output


def rendered_locus_rows(
    contexts: list[dict[str, Any]], directives: list[dict[str, Any]], locus: str
) -> list[dict[str, Any]]:
    source_rows = sorted(
        (row for row in contexts if row["locus"] == locus), key=lambda row: int(row["token_ordinal"])
    )
    directives_by_position = {row["source_position_id"]: row for row in directives}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        directive = directives_by_position.get(str(source["position_id"]))
        if directive and directive["render_action"] == "CONSUME_NO_OUTPUT":
            continue
        if directive:
            span_rows = [row for row in directives if row["render_unit_id"] == directive["render_unit_id"]]
            positions = [row["source_position_id"] for row in span_rows]
            surfaces = [row["source_surface"] for row in span_rows]
            rendered = directive["emitted_text_de"]
            source_kind = "BOUND_SPAN"
            source_ref = directive["bound_span_id"]
        else:
            positions = [str(source["position_id"])]
            surfaces = [str(source["surface"])]
            rendered = source["v88_context_realization_de"]
            source_kind = "CONTEXT_POSITION"
            source_ref = source["position_id"]
        output.append({
            "output_ordinal": len(output) + 1,
            "page": source["page"],
            "locus": source["locus"],
            "source_kind": source_kind,
            "source_ref": source_ref,
            "anchor_position_id": source["position_id"],
            "consumed_position_ids": ordered_compact(positions),
            "source_surfaces": ordered_compact(surfaces),
            "rendered_text_de": rendered,
            "historical_confirmation": HISTORICAL,
        })
    return output


def report_text(result: dict[str, Any], delta: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        f"| `{row['surface']}` | {row['v88_lexical_core_de']} | {row['v88_context_realization_de']} | {row['old_score']}→{row['v88_score']} ({row['v88_level']}) |"
        for row in delta
    )
    return f"""# GDT715 — V88 axis/action core–context repair

Status: `{STATUS}`

## Ergebnis

Die letzten sieben V87-Holds dieser Klasse haben jetzt einen engen
Woerterbuchkern und eine getrennte konkrete Fundstellenlesung:

| Form | Woerterbuchkern | konkrete Stelle | Confidence |
|---|---|---|---|
{rows}

Der entscheidende Gewinn ist nicht mehr Prosa, sondern Vorhersagbarkeit der
Komposition. `aiiin` liefert nur **Wert IV**; erst P052 waehlt **Menge IV**.
`ydaiin` liefert **Bezugswert III**; weder "drei" noch "Maße" bleiben im Kern.
Bei den fuenf Aktionen sitzt der Vorgang im Wort, waehrend der Patient aus der
explizit benannten linken Stelle kommt. So kann derselbe Aktionskern spaeter an
einem anderen Patienten getestet werden.

## f7r.2 wirklich neu gerendert

Der geerbte Einmal-Span bleibt aktiv:

```text
P288 keo + P289 r  ->  heiße Portion
```

P289 wird konsumiert und nicht separat ausgegeben. P291 verwendet nun den
reparierten DOLD-Kontext. Die acht tatsaechlichen Ausgabeeinheiten sind:

```text
{result['f7r2_rendered_line_de']}
```

## Bestand

- 7 revidierte Lesungen an 7 Positionen auf 7 Seiten
- 2 Wertkerne, 5 Aktionskerne
- 19 exakt aufgeloeste Primaerevidenzbindungen
- Confidence-Aenderung nur bei `aiiin` und `ydaiin`, jeweils `F_N +3`
- aktive Stufen: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- vollstaendiges Woerterbuch: {result['complete_readings']} Lesungen mit Score,
  Level, positiver Evidenz und Gegenbeleg in jeder Zeile
- verbleibende einzeln unbearbeitete schwache Lesungen: {result['remaining_unreviewed_weak_readings']}

## Grenze

Die konkreten Patienten sind bewusst als Fundstellenhypothesen markiert. Sie
werden nicht in den portablen Wortkern und nicht in freie Komponenten
exportiert. Das ist die beste aktuelle Arbeitsuebersetzung, keine bestaetigte
Klartextlesung; historische Bestaetigung bleibt `H0_NONE`.
"""


def main() -> int:
    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_spans = read_tsv(SOURCE_SPANS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)
    bindings = read_tsv(PRIMARY_BINDINGS)

    assert (len(source_lexical), len(source_context), len(source_complete), len(source_census), len(source_spans), len(source_families), len(specs), len(bindings)) == (324, 479, 1586, 109, 2, 13, 7, 19)
    assert Counter(row["decision"] for row in specs) == Counter({"REVISE": 7})
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in source_context)

    evidence, score_deltas = primary_evidence_rows(bindings, specs)
    lexical, lexical_by_source = lexical_rows(source_lexical, specs, score_deltas)
    contexts = context_rows(source_context, specs, lexical_by_source)
    census = census_rows(source_census, specs, lexical_by_source)
    delta = delta_rows(specs, source_lexical, lexical_by_source)
    families = family_rows(source_families, specs, lexical_by_source)
    complete = complete_rows(source_complete, lexical)
    spans = [dict(row) for row in source_spans]
    directives = one_shot_directive_rows(contexts, spans, "f7r.2")
    f7r2 = rendered_locus_rows(contexts, directives, "f7r.2")

    active_levels = Counter(str(row["working_model_level"]) for row in lexical)
    complete_levels = Counter(str(row["working_model_level"]) for row in complete)
    assert len(census) == 91 and sum(row["disposition"] == "REVISED_IN_V88" for row in census) == 7
    assert len(families) == 2 and {row["family_id"] for row in families} == {"F_N", "F_REF"}
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert len(directives) == 2 and len(f7r2) == 8
    assert active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    assert complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287,
        "W1_WEAK_WORKING": 315,
        "W2_PROVISIONAL_WORKING": 541,
        "W3_SOLID_WORKING_THEORY": 443,
    })

    lexical_fields = unique_fields([v88_key(field) for field in source_lexical[0]] + [
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
        "v88_component_global_export_allowed", "v88_prior_lexical_core_de",
    ])
    context_fields = unique_fields([v88_key(field) for field in source_context[0]] + [
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
        "v88_component_global_export_allowed", "v88_local_context_hypothesis",
        "v88_expected_left_surface",
    ])
    census_fields = unique_fields([v88_key(field) for field in source_census[0]] + [
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
    ])
    family_fields = unique_fields([family_v88_key(field) for field in source_families[0]] + ["v88_decisions"])
    complete_fields = unique_fields([v88_key(field) for field in source_complete[0]] + [
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
        "v88_component_global_export_allowed",
    ])

    write_tsv(ART / "V88_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical)
    write_tsv(ART / "V88_479_CONTEXT_REALIZATIONS.tsv", context_fields, contexts)
    write_tsv(ART / "V88_91_HELD_READING_AUDIT.tsv", census_fields, census)
    write_tsv(ART / "V88_7_AXIS_ACTION_CORE_CONTEXT_DELTA.tsv", list(delta[0]), delta)
    write_tsv(ART / "V88_19_PRIMARY_EVIDENCE_BINDINGS.tsv", list(evidence[0]), evidence)
    write_tsv(ART / "V88_2_FAMILY_EVIDENCE.tsv", family_fields, families)
    write_tsv(ART / "V88_2_BOUND_SPAN_RENDERER.tsv", list(spans[0]), spans)
    write_tsv(ART / "V88_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", list(directives[0]), directives)
    write_tsv(ART / "V88_8_F7R2_RENDERED_UNITS.tsv", list(f7r2[0]), f7r2)
    write_tsv(ART / "V88_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete)

    result = {
        "experiment_id": "GDT715",
        "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "audited_readings": 7,
        "audited_positions": 7,
        "audited_pages": 7,
        "value_cores_revised": 2,
        "action_cores_revised": 5,
        "primary_evidence_bindings": len(evidence),
        "score_promotions": {source_id: delta_value for source_id, delta_value in score_deltas.items() if delta_value},
        "active_lexical_readings": len(lexical),
        "active_positions": len(contexts),
        "active_level_counts": dict(sorted(active_levels.items())),
        "active_weak_readings": active_levels["W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"] + active_levels["W1_WEAK_WORKING"],
        "remaining_unreviewed_weak_readings": sum(row["v88_audit_decision"] == "HELD_FOR_LATER_REPAIR" for row in census),
        "complete_readings": len(complete),
        "complete_surfaces": len({row["surface"] for row in complete}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "bound_span_renderers": len(spans),
        "one_shot_directives": len(directives),
        "f7r2_rendered_units": len(f7r2),
        "f7r2_rendered_line_de": " · ".join(str(row["rendered_text_de"]) for row in f7r2),
        "relation_word_credit_gdt715": 0,
        "historical_confirmation": HISTORICAL,
        "new_pages": 0,
        "new_images": 0,
        "new_transcription": 0,
        "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result, delta), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
