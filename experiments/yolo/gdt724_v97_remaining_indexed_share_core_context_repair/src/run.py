#!/usr/bin/env python3
"""Build V97 by closing the nineteen remaining indexed-share audit cards."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt724_v97_remaining_indexed_share_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G723 = ROOT / "experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair/artifacts"

SOURCE_LEXICAL = G723 / "V96_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G723 / "V96_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G723 / "V96_47_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G723 / "V96_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G723 / "V96_5_BOUND_SPAN_RENDERER.tsv"
SOURCE_SPAN_EXECUTION = G723 / "V96_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
SOURCE_DIRECTIVES = G723 / "V96_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G723 / "V96_8_F7R2_RENDERED_UNITS.tsv"
G694_MIGRATIONS = (
    ROOT
    / "experiments/yolo/gdt694_residual_fraction_share_migration/artifacts"
    / "V67_22_RESIDUAL_SHARE_MIGRATIONS.tsv"
)
G693_MODEL = (
    ROOT
    / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts"
    / "V66_9_SELECTED_HEAD_MODEL.tsv"
)
G693_REVISIONS = (
    ROOT
    / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts"
    / "V66_57_SELECTED_REVISIONS.tsv"
)
G692_COMPONENTS = (
    ROOT
    / "experiments/yolo/gdt692_o_q_fraction_sister_compositor/artifacts"
    / "V65_COMPONENT_LEXICON.tsv"
)
G716_FAMILY = (
    ROOT
    / "experiments/yolo/gdt716_v89_indexed_share_core_context_repair/artifacts"
    / "V89_1_FAMILY_EVIDENCE.tsv"
)
SPECS = SRC / "V97_19_AUDIT_SPECS.tsv"

HISTORICAL = "H0_NONE"
ACTION_IDS = {"fdar#1", "lldar#1"}
STATUS = (
    "PASS_V97_19_REMAINING_INDEXED_SHARE_HOLDS_AUDITED__"
    "16_CORE_CONTEXT_REPAIRS_PLUS_3_EXACT_WHOLES_RETAINED__"
    "2_LOCAL_ACTIONS_SEPARATED__16_WEAK_READINGS_REMAIN__"
    "82_EVIDENCE_BINDINGS__NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None
) -> None:
    materialized = list(rows)
    if fields is None:
        fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [
        part.strip()
        for part in value.split("|")
        if part.strip() and part.strip() not in {"NONE", "0"}
    ]


def append_pipe(value: str, addition: str) -> str:
    output: list[str] = []
    for item in [*split_pipe(value), *split_pipe(addition)]:
        if item not in output:
            output.append(item)
    return "|".join(output) if output else "NONE"


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


def rename_v96(row: dict[str, str]) -> dict[str, Any]:
    return {
        key.replace("v96", "v97").replace("V96", "V97"): value
        for key, value in row.items()
    }


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(
        row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def target_indexes(
    lexical: list[dict[str, str]],
    contexts: list[dict[str, str]],
    census: list[dict[str, str]],
    migrations: list[dict[str, str]],
    revisions: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[tuple[str, str, str], dict[str, str]],
    dict[tuple[str, str, str], dict[str, str]],
]:
    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            assert source_id not in lexical_by_source
            lexical_by_source[source_id] = row
    context_by_position = {row["position_id"]: row for row in contexts}
    census_by_source = {row["source_reading_id"]: row for row in census}
    migration_by_key = {
        (row["locus"], row["token_ordinal"], row["surface"]): row
        for row in migrations
    }
    revision_by_key = {
        (row["locus"], row["token_ordinal"], row["surface"]): row
        for row in revisions
    }
    return (
        lexical_by_source,
        context_by_position,
        census_by_source,
        migration_by_key,
        revision_by_key,
    )


def build_lineage(
    specs: list[dict[str, str]],
    contexts: list[dict[str, str]],
    migrations: list[dict[str, str]],
    revisions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    context_by_position = {row["position_id"]: row for row in contexts}
    migration_by_key = {
        (row["locus"], row["token_ordinal"], row["surface"]): row
        for row in migrations
    }
    revision_by_key = {
        (row["locus"], row["token_ordinal"], row["surface"]): row
        for row in revisions
    }
    output: list[dict[str, Any]] = []
    for spec in specs:
        context = context_by_position[spec["expected_position_id"]]
        key = (
            spec["expected_locus"],
            spec["expected_token_ordinal"],
            spec["surface"],
        )
        migration = migration_by_key.get(key)
        revision = revision_by_key.get(key)
        assert (migration is None) != (revision is None)
        assert (
            context["page"],
            context["locus"],
            context["token_ordinal"],
            context["surface"],
        ) == (
            spec["expected_page"],
            spec["expected_locus"],
            spec["expected_token_ordinal"],
            spec["surface"],
        )
        if migration:
            assert migration["v67_gloss_de"] == spec["expected_old_core_de"]
            source_gdt = "GDT694"
            rule_id = migration["rule_id"]
            source_class = migration["migration_class"]
            visible_parse = migration["visible_parse"]
            share_index = migration["share_index"]
            preserved_heads = migration["preserved_heads"]
            local_rival = migration["local_rival_de"]
            exact_card_only = migration["exact_card_only"]
            learned_whole = migration["learned_whole_renderer"]
        else:
            assert revision is not None
            assert revision["v66_selected_share_de"] == spec["expected_old_core_de"]
            assert spec["surface"] in {"olkaiir", "oroiir"}
            source_gdt = "GDT693"
            rule_id = revision["v66_rule_id"]
            source_class = revision["revision_class"]
            visible_parse = spec["decomposition"]
            share_index = "III"
            preserved_heads = (
                "OLK=heißer Holzansatz"
                if spec["surface"] == "olkaiir"
                else "OR=Portion;O=Zubereitungsrahmen"
            )
            local_rival = context["live_rivals_de"]
            exact_card_only = "1"
            learned_whole = "0"
        output.append(
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "position_id": spec["expected_position_id"],
                "page": spec["expected_page"],
                "locus": spec["expected_locus"],
                "token_ordinal": spec["expected_token_ordinal"],
                "share_source_gdt": source_gdt,
                "share_source_rule_id": rule_id,
                "share_source_class": source_class,
                "share_source_visible_parse": visible_parse,
                "share_source_index": share_index,
                "share_source_preserved_heads": preserved_heads,
                "share_source_local_rival_de": local_rival,
                "share_source_exact_card_only": exact_card_only,
                "share_source_learned_whole_renderer": learned_whole,
                "active_signals": context["v57_signals"],
                "active_identity_signals": context["v57_identity_signals"],
                "active_action_signals": context["v57_action_signals"],
                "v97_decision": spec["decision"],
                "v97_lineage_class": spec["lineage_class"],
                "v97_selected_portable_core_de": spec["v97_lexical_core_de"],
                "v97_selected_local_renderer_de": spec[
                    "v97_context_realization_de"
                ],
                "exact_whole_surface_default_allowed": 1,
                "component_global_export_allowed": 0,
                "score_credit": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    assert len(output) == 19
    assert Counter(row["v97_decision"] for row in output) == Counter(
        {"REVISE": 16, "RETAIN": 3}
    )
    return output


def binding_row(
    binding_id: str,
    source_reading_id: str,
    surface: str,
    evidence_role: str,
    path: Path,
    selector: str,
    row: dict[str, str],
    status: str = "BOUND_EXACT_PRIMARY_ROW",
) -> dict[str, Any]:
    assert "f84" not in str(path).lower()
    assert all(
        not value.lower().startswith("f84")
        for key, value in row.items()
        if key in {"page", "locus"}
    )
    return {
        "binding_id": binding_id,
        "source_reading_id": source_reading_id,
        "surface": surface,
        "evidence_role": evidence_role,
        "evidence_path": str(path.relative_to(ROOT)),
        "selector": selector,
        "matched_row_fingerprint_sha256": fingerprint(row),
        "source_row_match": 1,
        "score_credit_family_ids": "NONE",
        "evidence_status": status,
        "historical_confirmation": HISTORICAL,
    }


def build_evidence_bindings(
    specs: list[dict[str, str]],
    lexical: list[dict[str, str]],
    contexts: list[dict[str, str]],
    census: list[dict[str, str]],
    migrations: list[dict[str, str]],
    revisions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    (
        lexical_by_source,
        context_by_position,
        census_by_source,
        migration_by_key,
        revision_by_key,
    ) = target_indexes(lexical, contexts, census, migrations, revisions)
    output: list[dict[str, Any]] = []
    for number, spec in enumerate(specs, start=1):
        source_id = spec["source_reading_id"]
        key = (
            spec["expected_locus"],
            spec["expected_token_ordinal"],
            spec["surface"],
        )
        migration = migration_by_key.get(key)
        revision = revision_by_key.get(key)
        assert (migration is None) != (revision is None)
        share_role = (
            "GDT694_EXACT_MIGRATION"
            if migration is not None
            else "GDT693_EXACT_REVISION"
        )
        share_path = G694_MIGRATIONS if migration is not None else G693_REVISIONS
        share_selector = (
            (
                f"locus={spec['expected_locus']};"
                f"token_ordinal={spec['expected_token_ordinal']};"
                f"surface={spec['surface']}"
            )
        )
        share_row = migration if migration is not None else revision
        assert share_row is not None
        exact_rows = [
            (
                "V96_ACTIVE_LEXICAL",
                SOURCE_LEXICAL,
                f"source_reading_ids={source_id}",
                lexical_by_source[source_id],
            ),
            (
                "V96_EXACT_CONTEXT",
                SOURCE_CONTEXT,
                f"position_id={spec['expected_position_id']}",
                context_by_position[spec["expected_position_id"]],
            ),
            (
                "V96_HELD_AUDIT",
                SOURCE_CENSUS,
                f"source_reading_id={source_id}",
                census_by_source[source_id],
            ),
            (
                share_role,
                share_path,
                share_selector,
                share_row,
            ),
        ]
        for subnumber, (role, path, selector, row) in enumerate(exact_rows, start=1):
            output.append(
                binding_row(
                    f"E{number:02d}{subnumber}",
                    source_id,
                    spec["surface"],
                    role,
                    path,
                    selector,
                    row,
                )
            )

    model_rows = {row["model_id"]: row for row in read_tsv(G693_MODEL)}
    family_rows = {row["family_id"]: row for row in read_tsv(G716_FAMILY)}
    component_rows = {
        row["component"]: row for row in read_tsv(G692_COMPONENTS)
    }
    shared = [
        (
            "E00R",
            "GDT693_R_SELECTOR_MODEL",
            G693_MODEL,
            "model_id=S002",
            model_rows["S002"],
            "BOUND_SHARED_MODEL_ROW",
        ),
        (
            "E00O",
            "GDT693_PORTION_CONTROL_MODEL",
            G693_MODEL,
            "model_id=S004",
            model_rows["S004"],
            "BOUND_SHARED_MODEL_ROW",
        ),
        (
            "E00F",
            "GDT716_CORE_CONTEXT_REPAIR_TEMPLATE",
            G716_FAMILY,
            "family_id=F_R",
            family_rows["F_R"],
            "BOUND_SHARED_TEMPLATE_ROW_NO_SCORE",
        ),
        (
            "E00C1",
            "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_I",
            G692_COMPONENTS,
            "component=AR_FRACTION_I",
            component_rows["AR_FRACTION_I"],
            "BOUND_COUNTERMODEL_ROW",
        ),
        (
            "E00C2",
            "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_II",
            G692_COMPONENTS,
            "component=AIR_FRACTION_II",
            component_rows["AIR_FRACTION_II"],
            "BOUND_COUNTERMODEL_ROW",
        ),
        (
            "E00C3",
            "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_III",
            G692_COMPONENTS,
            "component=AIIR_FRACTION_III",
            component_rows["AIIR_FRACTION_III"],
            "BOUND_COUNTERMODEL_ROW",
        ),
    ]
    for binding_id, role, path, selector, row, status in shared:
        output.append(
            binding_row(
                binding_id,
                "ALL_19_BOUND_TARGETS",
                "AR|AIR|AIIR|AIIIR",
                role,
                path,
                selector,
                row,
                status,
            )
        )
    assert len(output) == 82
    assert len({row["binding_id"] for row in output}) == 82
    assert Counter(
        row["source_reading_id"]
        for row in output
        if row["source_reading_id"] != "ALL_19_BOUND_TARGETS"
    ) == Counter({spec["source_reading_id"]: 4 for spec in specs})
    return output


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    seen: Counter[str] = Counter()
    for source in source_rows:
        row = rename_v96(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            source_id = source_ids[0]
            seen[source_id] += 1
            assert source["v96_lexical_core_de"] == spec["expected_old_core_de"]
            score = int(source["working_model_score_0_100_not_probability"])
            assert source["working_model_level"] == level(score) == "W1_WEAK_WORKING"
            decision = (
                "REVISE_CORE_AND_CONTEXT_SCOPE"
                if spec["decision"] == "REVISE"
                else "REVIEWED_RETAINED"
            )
            if spec["decision"] == "REVISE":
                assert spec["v97_lexical_core_de"] != spec["expected_old_core_de"]
            else:
                assert (
                    spec["v97_lexical_core_de"]
                    == spec["v97_context_realization_de"]
                    == spec["expected_old_core_de"]
                )
            row.update(
                {
                    "v97_lexical_core_de": spec["v97_lexical_core_de"],
                    "v97_context_realizations_de": spec[
                        "v97_context_realization_de"
                    ],
                    "family_ids": append_pipe(
                        source["family_ids"], "F_R_BOUND_EXACT"
                    ),
                    "decomposition": spec["decomposition"],
                    "repair_modes": spec["repair_mode"],
                    "resolved_debt_atoms": spec["repair_mode"],
                    "last_semantic_writer": (
                        "GDT724"
                        if spec["decision"] == "REVISE"
                        else source["last_semantic_writer"]
                    ),
                    "base_score": score,
                    "score_delta_lexical_core": 0,
                    "working_model_score_0_100_not_probability": score,
                    "working_model_level": level(score),
                    "context_realization_score_0_100_not_probability": score,
                    "context_realization_level": level(score),
                    "source_gdts": append_pipe(source["source_gdts"], "GDT724"),
                    "positive_evidence_de": (
                        "GDT724 audit: "
                        + spec["evidence_de"]
                        + " || "
                        + source["positive_evidence_de"]
                    ),
                    "counterevidence_de": (
                        "GDT724 Grenze: "
                        + spec["counterevidence_de"]
                        + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                    ),
                    "v97_audit_decision": decision,
                    "v97_evidence_class": spec["evidence_class"],
                    "v97_open_semantic_slots": spec["open_semantic_slots"],
                    "v97_component_global_export_allowed": "0",
                    "v97_exact_whole_surface_default_allowed": "1",
                    "v97_lineage_class": spec["lineage_class"],
                    "v97_prior_lexical_core_de": source["v96_lexical_core_de"],
                }
            )
            if source_id in ACTION_IDS:
                assert "abmessen" not in spec["v97_lexical_core_de"].casefold()
                assert "abmessen" in spec["v97_context_realization_de"].casefold()
        else:
            row.update(
                {
                    "v97_audit_decision": "NOT_IN_GDT724_TRANCHE",
                    "v97_evidence_class": "INHERITED_V96",
                    "v97_open_semantic_slots": "NOT_EVALUATED",
                    "v97_component_global_export_allowed": "NOT_EVALUATED",
                    "v97_exact_whole_surface_default_allowed": "NOT_EVALUATED",
                    "v97_lineage_class": "INHERITED_V96",
                    "v97_prior_lexical_core_de": source["v96_lexical_core_de"],
                }
            )
        output.append(row)
    assert len(output) == 324
    assert seen == Counter({source_id: 1 for source_id in specs_by_id})
    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def build_contexts(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    by_locus_ordinal = {
        (row["locus"], int(row["token_ordinal"])): row for row in source_rows
    }
    seen: Counter[str] = Counter()
    output: list[dict[str, Any]] = []
    for source in source_rows:
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v96(source)
        if spec:
            seen[source_id] += 1
            assert (
                source["position_id"],
                source["page"],
                source["locus"],
                source["token_ordinal"],
            ) == (
                spec["expected_position_id"],
                spec["expected_page"],
                spec["expected_locus"],
                spec["expected_token_ordinal"],
            )
            ordinal = int(source["token_ordinal"])
            left = (
                "<BOS>"
                if ordinal == 1
                else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            )
            right = (
                "<EOS>"
                if (source["locus"], ordinal + 1) not in by_locus_ordinal
                else by_locus_ordinal[(source["locus"], ordinal + 1)]["surface"]
            )
            assert (
                left,
                right,
                source["v68_action_license"],
            ) == (
                spec["expected_left_surface"],
                spec["expected_right_surface"],
                spec["expected_action_license"],
            )
            assert (source_id in ACTION_IDS) == (
                source["v68_clause_type"] == "ACTION_CLAUSE"
            )
        decision = (
            (
                "REVISE_CORE_AND_CONTEXT_SCOPE"
                if spec["decision"] == "REVISE"
                else "REVIEWED_RETAINED"
            )
            if spec
            else "NOT_IN_GDT724_TRANCHE"
        )
        row.update(
            {
                "v97_reading_id": lexical["v97_reading_id"],
                "v97_lexical_core_de": lexical["v97_lexical_core_de"],
                "v97_context_realization_de": (
                    spec["v97_context_realization_de"]
                    if spec
                    else source["v96_context_realization_de"]
                ),
                "v97_repair_mode": (
                    spec["repair_mode"] if spec else source["v96_repair_mode"]
                ),
                "v97_resolved_debt_atom": (
                    spec["repair_mode"]
                    if spec
                    else source["v96_resolved_debt_atom"]
                ),
                "v97_lexical_score": lexical[
                    "working_model_score_0_100_not_probability"
                ],
                "v97_lexical_level": lexical["working_model_level"],
                "v97_context_score": lexical[
                    "context_realization_score_0_100_not_probability"
                ],
                "v97_context_level": lexical["context_realization_level"],
                "v97_semantic_scope": lexical["semantic_scope"],
                "v97_semantic_applicability": lexical[
                    "semantic_applicability"
                ],
                "v97_global_export_scope": lexical["global_export_scope"],
                "v97_lexical_bound_span_ids": lexical["bound_span_ids"],
                "v97_unconditional_global_export_allowed": lexical[
                    "unconditional_global_export_allowed"
                ],
                "v97_historical_confirmation": HISTORICAL,
                "v97_audit_decision": decision,
                "v97_evidence_class": (
                    spec["evidence_class"] if spec else "INHERITED_V96"
                ),
                "v97_open_semantic_slots": (
                    spec["open_semantic_slots"] if spec else "NOT_EVALUATED"
                ),
                "v97_component_global_export_allowed": (
                    "0" if spec else "NOT_EVALUATED"
                ),
                "v97_exact_whole_surface_default_allowed": (
                    "1" if spec else "NOT_EVALUATED"
                ),
                "v97_lineage_class": (
                    spec["lineage_class"] if spec else "INHERITED_V96"
                ),
                "v97_local_context_hypothesis": (
                    spec["local_context_hypothesis"] if spec else "NONE"
                ),
                "v97_expected_left_surface": (
                    spec["expected_left_surface"] if spec else "NONE"
                ),
                "v97_expected_right_surface": (
                    spec["expected_right_surface"] if spec else "NONE"
                ),
            }
        )
        output.append(row)
    assert len(output) == 479
    assert seen == Counter({source_id: 1 for source_id in specs_by_id})
    return output


def build_census(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v96(source)
        if spec:
            revised = spec["decision"] == "REVISE"
            decision = (
                "REVISE_CORE_AND_CONTEXT_SCOPE"
                if revised
                else "REVIEWED_RETAINED"
            )
            row.update(
                {
                    "disposition": (
                        "REVISED_IN_V97"
                        if revised
                        else "REVIEWED_RETAINED_IN_V97"
                    ),
                    "repair_mode": spec["repair_mode"],
                    "resolved_debt_atom": spec["repair_mode"],
                    "v97_reading_id": lexical["v97_reading_id"],
                    "v97_lexical_core_de": lexical["v97_lexical_core_de"],
                    "v97_context_realization_de": spec[
                        "v97_context_realization_de"
                    ],
                    "new_lexical_score": lexical[
                        "working_model_score_0_100_not_probability"
                    ],
                    "new_lexical_level": lexical["working_model_level"],
                    "new_context_score": lexical[
                        "context_realization_score_0_100_not_probability"
                    ],
                    "new_context_level": lexical[
                        "context_realization_level"
                    ],
                    "positive_evidence_de": spec["evidence_de"],
                    "counterevidence_de": spec["counterevidence_de"],
                    "v97_audit_decision": decision,
                    "v97_evidence_class": spec["evidence_class"],
                    "v97_open_semantic_slots": spec["open_semantic_slots"],
                    "v97_lineage_class": spec["lineage_class"],
                }
            )
        else:
            row.update(
                {
                    "v97_reading_id": lexical["v97_reading_id"],
                    "v97_lexical_core_de": lexical["v97_lexical_core_de"],
                    "v97_context_realization_de": lexical[
                        "v97_context_realizations_de"
                    ],
                    "new_lexical_score": lexical[
                        "working_model_score_0_100_not_probability"
                    ],
                    "new_lexical_level": lexical["working_model_level"],
                    "new_context_score": lexical[
                        "context_realization_score_0_100_not_probability"
                    ],
                    "new_context_level": lexical[
                        "context_realization_level"
                    ],
                    "v97_audit_decision": "HELD_FOR_LATER_REPAIR",
                    "v97_evidence_class": "INHERITED_V96",
                    "v97_open_semantic_slots": "NOT_EVALUATED",
                    "v97_lineage_class": "INHERITED_V96",
                }
            )
        output.append(row)
    assert len(output) == 35
    assert Counter(row["disposition"] for row in output) == Counter(
        {
            "REVISED_IN_V97": 16,
            "REVIEWED_RETAINED_IN_V97": 3,
            "HELD_FOR_LATER_REPAIR": 16,
        }
    )
    return output


def build_delta(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_by_id = {
        source_id: row
        for row in source_rows
        for source_id in split_pipe(row["source_reading_ids"])
    }
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = lexical_by_source[spec["source_reading_id"]]
        output.append(
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "decision": spec["decision"],
                "position_id": spec["expected_position_id"],
                "page": spec["expected_page"],
                "locus": spec["expected_locus"],
                "token_ordinal": spec["expected_token_ordinal"],
                "left_surface": spec["expected_left_surface"],
                "right_surface": spec["expected_right_surface"],
                "old_lexical_core_de": source["v96_lexical_core_de"],
                "v97_lexical_core_de": target["v97_lexical_core_de"],
                "v97_context_realization_de": spec[
                    "v97_context_realization_de"
                ],
                "portable_role": spec["portable_role"],
                "old_score": source[
                    "working_model_score_0_100_not_probability"
                ],
                "v97_score": target[
                    "working_model_score_0_100_not_probability"
                ],
                "old_level": source["working_model_level"],
                "v97_level": target["working_model_level"],
                "family_ids": "F_R_BOUND_EXACT",
                "score_credit_family_ids": "NONE",
                "decomposition": spec["decomposition"],
                "lineage_class": spec["lineage_class"],
                "repair_mode": spec["repair_mode"],
                "evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "open_semantic_slots": spec["open_semantic_slots"],
                "local_only_words_or_heads": spec[
                    "local_only_words_or_heads"
                ],
                "exact_whole_surface_default_allowed": 1,
                "component_global_export_allowed": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    assert len(output) == 19
    assert sum(row["decision"] == "REVISE" for row in output) == 16
    assert sum(row["decision"] == "RETAIN" for row in output) == 3
    return output


def build_scope_dictionary() -> list[dict[str, Any]]:
    rows = [
        (
            "BOUND_INDEXED_SHARE_SELECTOR",
            "all_19_targets",
            "Anteil I/II/III/IV innerhalb der gelisteten Ganzformen",
            "keine freie oder universelle ar-Bedeutung",
            "GDT693_S002|GDT694_EXACT_MIGRATIONS",
        ),
        (
            "PORTION_DISTINCT_FROM_SHARE",
            "oroiir|araram",
            "OR=Portion ueber R=Anteil; AR|ARAM als Apposition",
            "keine Verschmelzung von Portion, Anteil und Maß",
            "GDT693_S004|GDT694_M018",
        ),
        (
            "LEARNED_OR_BOUND_WHOLES",
            "araram|arl|chear|lldar|losair|daiiiry|ockhdar|okeeodar",
            "exakter Ganzwortdefault mit sichtbarem Anteilskern",
            "innere Grenze oder Leserentscheidung bleibt gebunden",
            "GDT694_EXACT_CARD_ONLY",
        ),
        (
            "ACTIVE_MATERIAL_IDENTITIES",
            "arl|fdar|lkar|lldar|losair|olkaiir|polairy|sairy|saraiin",
            "Holz, Blüte, Pulver oder Samen nur auf der exakten Karte",
            "keine familienweite Stoffidentitaet",
            "V96_ACTIVE_IDENTITY_SIGNALS",
        ),
        (
            "LOCAL_PRODUCT_AND_PATIENT_HEADS",
            "airoy|araram|arl|chear|chotar|dairody|ockhdar|okeeodar|olkaiir|oroiir",
            "konkreter Fundstellenrenderer",
            "Droge, Ansatz, Auszug, Arznei, Masse oder Posten nicht portabel",
            "V97_CORE_CONTEXT_SEPARATION",
        ),
        (
            "LOCAL_ACTIONS",
            "fdar|lldar",
            "abmessen nur an P163 und P334",
            "kein Aktionsverb im portablen Wortkern",
            "GDT689_ACTION_ORDINALS",
        ),
        (
            "B003_RENDER_ONCE",
            "l|karchees",
            "vollständig getrocknete Charge aus erhitztem Holzanteil I",
            "Holz stammt aus dem sichtbaren linken l; keine Einzelausgabe",
            "GDT694_B003|GDT724_RERENDER",
        ),
    ]
    return [
        {
            "scope_item": scope,
            "surfaces": surfaces,
            "portable_value_de": portable,
            "local_only_content_de": local,
            "lineage": lineage,
            "status": "BOUND_WORKING_DICTIONARY_SCOPE",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        }
        for scope, surfaces, portable, local, lineage in rows
    ]


def build_rivals(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in specs:
        selected = {
            "source_reading_id": spec["source_reading_id"],
            "surface": spec["surface"],
            "model_id": "A_BOUND_CORE_PLUS_EXACT_LOCAL_RENDERER",
            "candidate_portable_default_de": spec["v97_lexical_core_de"],
            "candidate_local_renderer_de": spec["v97_context_realization_de"],
            "decision": "SELECT",
            "evidence_fit_de": spec["evidence_de"],
            "conflict_de": spec["counterevidence_de"],
            "portable_default_selected": 1,
            "component_global_export_allowed": 0,
            "score_credit": 0,
        }
        if spec["decision"] == "REVISE":
            rival_b = {
                **selected,
                "model_id": "B_OLD_FULL_PRODUCT_OR_ACTION_AS_PORTABLE_WORD",
                "candidate_portable_default_de": spec["expected_old_core_de"],
                "candidate_local_renderer_de": spec["expected_old_core_de"],
                "decision": "REJECT_AS_PORTABLE_KEEP_WHERE_LOCAL",
                "evidence_fit_de": "Bleibt an der bekannten Einzelposition als konkrete Arbeitslesung verfügbar.",
                "conflict_de": "Schreibt einen ersetzbaren Patienten, Produktkopf oder ein lokales Verb in den portablen Ganzwortkern.",
                "portable_default_selected": 0,
            }
        else:
            rival_b = {
                **selected,
                "model_id": "B_STRIPPED_GENERIC_SHARE_ONLY",
                "candidate_portable_default_de": "nur unbestimmter Anteil",
                "candidate_local_renderer_de": spec["v97_context_realization_de"],
                "decision": "REJECT_OVERSTRIPPING_ACTIVE_IDENTITY",
                "evidence_fit_de": "Wäre formal knapper.",
                "conflict_de": "Loescht aktive Pulver-, Samen-, Zustands- oder Mengensignale der exakten Karte.",
                "portable_default_selected": 0,
            }
        rival_c = {
            **selected,
            "model_id": "C_UNRELATED_LEARNED_TECHNICAL_WHOLE",
            "candidate_portable_default_de": "anderer gelernter technischer Ganzwert",
            "candidate_local_renderer_de": "offen",
            "decision": "KEEP_COUNTERMODEL",
            "evidence_fit_de": "Die gebundene Ganzform bleibt mit einem anderen Codebookwert vereinbar.",
            "conflict_de": "Erklaert Index, Zustand, Menge und aktive Identitaet nicht besser.",
            "portable_default_selected": 0,
        }
        output.extend([selected, rival_b, rival_c])
    assert len(output) == 57
    return output


def build_target_renderer(
    contexts: list[dict[str, Any]], specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    by_position = {row["position_id"]: row for row in contexts}
    output: list[dict[str, Any]] = []
    for spec in specs:
        row = by_position[spec["expected_position_id"]]
        output.append(
            {
                "position_id": row["position_id"],
                "page": row["page"],
                "locus": row["locus"],
                "token_ordinal": row["token_ordinal"],
                "surface": row["surface"],
                "decision": spec["decision"],
                "left_surface": spec["expected_left_surface"],
                "right_surface": spec["expected_right_surface"],
                "portable_lexical_core_de": row["v97_lexical_core_de"],
                "local_context_realization_de": row[
                    "v97_context_realization_de"
                ],
                "action_license": row["v68_action_license"],
                "lineage_class": spec["lineage_class"],
                "decomposition": spec["decomposition"],
                "exact_whole_surface_default_allowed": 1,
                "component_global_export_allowed": 0,
                "score": row["v97_lexical_score"],
                "level": row["v97_lexical_level"],
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_action_head_separation(
    specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in specs:
        source_id = spec["source_reading_id"]
        action = source_id in ACTION_IDS
        core = spec["v97_lexical_core_de"]
        local = spec["v97_context_realization_de"]
        local_only = split_pipe(spec["local_only_words_or_heads"])
        for item in local_only:
            assert item.casefold() in local.casefold(), (source_id, item, local)
            assert item.casefold() not in core.casefold(), (source_id, item, core)
        if action:
            assert "abmessen" not in core.casefold()
            assert "abmessen" in local.casefold()
        output.append(
            {
                "source_reading_id": source_id,
                "surface": spec["surface"],
                "decision": spec["decision"],
                "position_id": spec["expected_position_id"],
                "position_is_action_licensed": int(action),
                "portable_lexical_core_de": core,
                "local_context_realization_de": local,
                "local_only_words_or_heads": spec[
                    "local_only_words_or_heads"
                ],
                "portable_action_export_allowed": 0,
                "portable_product_head_export_allowed": 0,
                "component_global_export_allowed": 0,
                "audit_status": (
                    "PASS_LOCAL_ACTION_SEPARATED"
                    if action
                    else "PASS_NOMINAL_NO_HIDDEN_ACTION"
                ),
                "historical_confirmation": HISTORICAL,
            }
        )
    assert sum(row["position_is_action_licensed"] for row in output) == 2
    return output


def build_complete(
    source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V96_LEXICAL_CORE":
            continue
        row = rename_v96(source)
        row.update(
            {
                "v97_audit_decision": "OUTSIDE_ACTIVE_V97_TRANCHE",
                "v97_evidence_class": "INHERITED_GLOBAL_V48",
                "v97_open_semantic_slots": "NOT_EVALUATED",
                "v97_component_global_export_allowed": "NOT_EVALUATED",
                "v97_exact_whole_surface_default_allowed": "NOT_EVALUATED",
                "v97_lineage_class": "INHERITED_GLOBAL_V48",
            }
        )
        output.append(row)
    for row in lexical:
        output.append(
            {
                "surface": row["surface"],
                "reading_id": row["v97_reading_id"],
                "working_meaning_de": row["v97_lexical_core_de"],
                "current_layer": "ACTIVE_V97_LEXICAL_CORE",
                "semantic_scope": row["semantic_scope"],
                "semantic_applicability": row["semantic_applicability"],
                "form_level": row["form_level"],
                "occurrence_count": row["occurrence_count"],
                "page_count": row["page_count"],
                "locus_count": row["locus_count"],
                "working_model_score_0_100_not_probability": row[
                    "working_model_score_0_100_not_probability"
                ],
                "working_model_level": row["working_model_level"],
                "source_gdts": row["source_gdts"],
                "positive_evidence_de": row["positive_evidence_de"],
                "counterevidence_de": row["counterevidence_de"],
                "historical_confirmation": row["historical_confirmation"],
                "historical_analogue": row["historical_analogue"],
                "relation_word_delta": row["relation_word_delta"],
                "global_export_scope": row["global_export_scope"],
                "bound_span_ids": row["bound_span_ids"],
                "unconditional_global_export_allowed": row[
                    "unconditional_global_export_allowed"
                ],
                "v97_context_realizations_de": row[
                    "v97_context_realizations_de"
                ],
                "source_reading_ids": row["source_reading_ids"],
                "v97_audit_decision": row["v97_audit_decision"],
                "v97_evidence_class": row["v97_evidence_class"],
                "v97_open_semantic_slots": row["v97_open_semantic_slots"],
                "v97_component_global_export_allowed": row[
                    "v97_component_global_export_allowed"
                ],
                "v97_exact_whole_surface_default_allowed": row[
                    "v97_exact_whole_surface_default_allowed"
                ],
                "v97_lineage_class": row["v97_lineage_class"],
            }
        )
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def build_spans() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    spans: list[dict[str, Any]] = []
    for source in read_tsv(SOURCE_SPANS):
        row: dict[str, Any] = dict(source)
        if source["bound_span_id"] == "B003":
            assert (
                source["render_once_de"]
                == "vollständig getrocknete Charge aus Anteil I der erhitzten Holzdroge"
            )
            row["render_once_de"] = (
                "vollständig getrocknete Charge aus erhitztem Holzanteil I"
            )
            row["source_gdts"] = append_pipe(source["source_gdts"], "GDT724")
        spans.append(row)
    execution: list[dict[str, Any]] = []
    for source in read_tsv(SOURCE_SPAN_EXECUTION):
        row = dict(source)
        if source["bound_span_id"] == "B003":
            row["render_once_de"] = (
                "vollständig getrocknete Charge aus erhitztem Holzanteil I"
            )
        execution.append(row)
    assert len(spans) == len(execution) == 5
    assert sum(
        row["render_once_de"]
        == "vollständig getrocknete Charge aus erhitztem Holzanteil I"
        for row in spans
    ) == 1
    return spans, execution


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs = read_tsv(SPECS)
    assert len(specs) == 19
    assert len({row["source_reading_id"] for row in specs}) == 19
    assert Counter(row["decision"] for row in specs) == Counter(
        {"REVISE": 16, "RETAIN": 3}
    )
    assert all("f84" not in row["expected_page"].lower() for row in specs)

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_census = read_tsv(SOURCE_CENSUS)
    source_complete = read_tsv(SOURCE_COMPLETE)
    migrations = read_tsv(G694_MIGRATIONS)
    revisions = read_tsv(G693_REVISIONS)

    lineage = build_lineage(specs, source_context, migrations, revisions)
    evidence = build_evidence_bindings(
        specs,
        source_lexical,
        source_context,
        source_census,
        migrations,
        revisions,
    )
    lexical, lexical_by_source = build_lexical(source_lexical, specs)
    contexts = build_contexts(source_context, specs, lexical_by_source)
    census = build_census(source_census, specs, lexical_by_source)
    delta = build_delta(source_lexical, specs, lexical_by_source)
    scope_dictionary = build_scope_dictionary()
    rivals = build_rivals(specs)
    target_renderer = build_target_renderer(contexts, specs)
    action_head = build_action_head_separation(specs)
    complete = build_complete(source_complete, lexical)
    spans, span_execution = build_spans()

    write_tsv(ART / "V97_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V97_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V97_35_HELD_READING_AUDIT.tsv", census)
    write_tsv(ART / "V97_19_INDEXED_SHARE_CORE_CONTEXT_DELTA.tsv", delta)
    write_tsv(ART / "V97_7_SCOPE_DICTIONARY.tsv", scope_dictionary)
    write_tsv(ART / "V97_57_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V97_82_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V97_19_LINEAGE_AUDIT.tsv", lineage)
    write_tsv(ART / "V97_19_TARGET_RENDERER.tsv", target_renderer)
    write_tsv(ART / "V97_19_ACTION_HEAD_SEPARATION.tsv", action_head)
    write_tsv(ART / "V97_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    write_tsv(ART / "V97_5_BOUND_SPAN_RENDERER.tsv", spans)
    write_tsv(ART / "V97_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", span_execution)
    shutil.copyfile(
        SOURCE_DIRECTIVES, ART / "V97_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
    )
    shutil.copyfile(SOURCE_F7R2, ART / "V97_8_F7R2_RENDERED_UNITS.tsv")

    levels = Counter(row["working_model_level"] for row in lexical)
    assert levels == Counter(
        {
            "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
            "W1_WEAK_WORKING": 135,
            "W2_PROVISIONAL_WORKING": 163,
            "W3_SOLID_WORKING_THEORY": 19,
        }
    )
    assert len(complete) == 1586
    assert len({row["surface"] for row in complete}) == 1582
    assert all(row["working_meaning_de"] for row in complete)
    assert all(row["working_model_level"] for row in complete)
    assert all(
        row["positive_evidence_de"] and row["counterevidence_de"]
        for row in complete
    )
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete)
    assert all(row["component_global_export_allowed"] == 0 for row in delta)
    assert all(int(row["old_score"]) == int(row["v97_score"]) for row in delta)

    result = {
        "experiment_id": "GDT724",
        "status": STATUS,
        "target_readings_audited": 19,
        "target_positions": 19,
        "target_pages": len({row["expected_page"] for row in specs}),
        "revised_core_context_readings": 16,
        "reviewed_retained_exact_wholes": 3,
        "primary_and_countermodel_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals),
        "scope_dictionary_rows": len(scope_dictionary),
        "action_positions_with_lexical_action_separation": 2,
        "nominal_positions_without_hidden_action": 17,
        "exact_whole_surface_defaults_allowed": 19,
        "component_global_exports": 0,
        "score_credit_families": 0,
        "score_delta_total": 0,
        "active_lexical_rows": len(lexical),
        "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts),
        "non_target_lexical_rows_preserved": len(lexical) - 19,
        "non_target_context_positions_preserved": len(contexts) - 19,
        "remaining_unreviewed_weak_readings": 16,
        "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(
                row["working_meaning_de"]
                and row["working_model_level"]
                and row["positive_evidence_de"]
                and row["counterevidence_de"]
            )
            for row in complete
        ),
        "bound_spans": len(spans),
        "bound_span_execution_rows": len(span_execution),
        "b003_span_rerendered": 1,
        "one_shot_directives_preserved": len(read_tsv(SOURCE_DIRECTIVES)),
        "f7r2_output_units": len(read_tsv(SOURCE_F7R2)),
        "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": (
            "experiments/yolo/gdt724_v97_remaining_indexed_share_core_context_repair/"
            "artifacts/V97_COMPLETE_WORD_CONFIDENCE.tsv"
        ),
    }
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
