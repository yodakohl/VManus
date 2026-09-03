#!/usr/bin/env python3
"""Build the GDT767 target-excluding historical identity tournament."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt767_ofch_historical_identity_cofield_tournament")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G766 = ROOT / "experiments/yolo/gdt766_ofch_chor_role_switch_prediction"

OFCH_SPECS = G766 / "src/OFCH_25_FORM_SPECS.tsv"
CHOR_SPECS = G766 / "src/CHOR_4_FORM_SPECS.tsv"
PASSAGE_SPECS = G766 / "src/PASSAGE_5_LINE_TOKEN_DEFAULTS.tsv"
SHADOW_BRIDGES = G766 / "artifacts/OFCH_REPRODUCTIVE_4_BRIDGE_ATLAS.tsv"
CTHY_CENSUS = ROOT / (
    "experiments/yolo/gdt758_ychor_follower_global_content_census/"
    "artifacts/FOLLOWER_11_GLOBAL_CENSUS.tsv"
)
CANDIDATE_DECK = SRC / "HISTORICAL_CANDIDATE_DECK.tsv"
SOURCE_REGISTRY = SRC / "HISTORICAL_SOURCE_REGISTRY.tsv"

OUTPUT_NAMES = (
    "COFIELD_224_OCCURRENCE_ATLAS.tsv",
    "COFIELD_28_FORM_MATRIX.tsv",
    "OFCH_43_AGGREGATE_FEATURE_SUMMARY.tsv",
    "CHOR_CTHY_15_PARALLEL_ATLAS.tsv",
    "SHADOW_REPRODUCTIVE_4_AUDIT.tsv",
    "HISTORICAL_504_CANDIDATE_TOURNAMENT.tsv",
    "HISTORICAL_IDENTITY_SEPARABILITY.tsv",
    "GDT767_28_WORKING_DICTIONARY.tsv",
    "FIVE_LINE_REVISED_READER.tsv",
    "HISTORICAL_REGISTER_READER.md",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__28_COMPLETE_WHOLES_224_EXACT_OCCURRENCES__"
    "25_OFCH_WHOLES_43_OCCURRENCES__TARGET_EXCLUDING_200_BLOCKED_DONORS__"
    "OFCH_ZERO_CTHY_ZERO_EXACT_CHOR_ANCHORS__"
    "CHOR_CTHY_15_PARALLEL_OCCURRENCES_14_LOCI_5_DIRECT__"
    "18_HISTORICAL_SUBSTANCE_FORM_CANDIDATES__"
    "FORM_CLASS_SIGNAL_WITH_SPECIFIC_SUBSTANCE_OPEN__"
    "OFCH_EOL_EXTRACT_DEFAULTS_DOWNGRADED__"
    "28_FORCED_CONCRETE_REPLACEABLE_DEFAULTS__5_REVISED_LINES__"
    "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
)

CHOR_CHANNELS = {
    "chor": "BASE_CONTENT",
    "schor": "BASE_CONTENT",
    "lchor": "PREPARATION",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cofield = load_module("gdt767_cofield", SRC / "cofield.py")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str] | None = None) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty TSV: {path.name}")
    names = list(fields or rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def values(text: object) -> set[str]:
    return {item for item in str(text).split("|") if item and item != "NONE"}


def joined(items: Iterable[str]) -> str:
    chosen = set(items)
    return "|".join(feature for feature in cofield.FEATURES if feature in chosen) or "NONE"


def donors_text(donors: Sequence[Mapping[str, object]]) -> str:
    return "|".join(
        f"{row['surface']}@{row['ordinal']}:d{row['distance']}[{joined(row['features'])}]"
        for row in donors
    ) or "NONE"


def flatten_atlas(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        output.append({
            "source_occurrence_id": row["source_occurrence_id"],
            "target_family": row["target_family"],
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "ordinal": row["ordinal"],
            "line_token_count": row["line_token_count"],
            "d1_features": joined(row["d1_features"]),
            "r3_features": joined(row["r3_features"]),
            "line_features": joined(row["line_features"]),
            "d1_donors": donors_text(row["d1_donors"]),
            "r3_donors": donors_text(row["r3_donors"]),
            "line_donors": donors_text(row["line_donors"]),
            "written_line_eva": row["written_line_eva"],
            "all_target_surfaces_blocked_as_donors": 1,
            "all_donors_reader_exact_and_clean": 1,
            "component_credit": 0,
        })
    return output


def flatten_matrix(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        flat = {
            "surface": row["surface"],
            "target_family": row["target_family"],
            "reader_exact_occurrences": row["reader_exact_occurrences"],
        }
        for feature in cofield.FEATURES:
            stem = feature.lower()
            flat[f"{stem}_d1"] = row[f"{stem}_d1"]
            flat[f"{stem}_r3"] = row[f"{stem}_r3"]
            flat[f"{stem}_line"] = row[f"{stem}_line"]
            flat[f"{stem}_d1_r3_line"] = row[f"{stem}_d1_r3_line"]
        flat.update({
            "specific_substance_identity_from_cofields": "OPEN",
            "component_credit": 0,
        })
        output.append(flat)
    return output


def aggregate_ofch(atlas: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    rows = [row for row in atlas if row["target_family"] == "OFCH_CONTAINING"]
    assert len(rows) == 43
    output: list[dict[str, object]] = []
    for feature in cofield.FEATURES:
        counts = {
            scope: sum(feature in row[f"{scope.lower()}_features"] for row in rows)
            for scope in cofield.SCOPES
        }
        output.append({
            "feature": feature,
            "ofch_exact_occurrences": len(rows),
            "d1_occurrences": counts["D1"],
            "r3_occurrences": counts["R3"],
            "line_occurrences": counts["LINE"],
            "d1_rate": f"{counts['D1'] / len(rows):.6f}",
            "r3_rate": f"{counts['R3'] / len(rows):.6f}",
            "line_rate": f"{counts['LINE'] / len(rows):.6f}",
            "identity_credit": 0,
            "interpretation": (
                "No independent exact leaf-whole cofield support."
                if feature == "CTHY_LEAF" else
                "No independent exact chor cofield support; shadow family contacts remain separate."
                if feature == "CHOR_REPRO" else
                "Target-excluding state, amount, record or process context; class evidence only."
            ),
        })
    return output


def build_chor_cthy(
    atlas: Sequence[Mapping[str, object]], cthy_prior: Mapping[str, str]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in atlas:
        if row["surface"] != "chor":
            continue
        for donor in row["line_donors"]:
            if donor["surface"] != "cthy":
                continue
            direction = "LEFT" if int(donor["ordinal"]) < int(row["ordinal"]) else "RIGHT"
            output.append({
                "pair_id": f"G767-CP{len(output)+1:02d}",
                "page": row["page"],
                "locus": row["locus"],
                "chor_ordinal": row["ordinal"],
                "cthy_ordinal": donor["ordinal"],
                "cthy_direction_from_chor": direction,
                "distance": donor["distance"],
                "direct_pair": int(int(donor["distance"]) == 1),
                "written_order": "CTHY_CHOR" if direction == "LEFT" else "CHOR_CTHY",
                "written_line_eva": row["written_line_eva"],
                "cthy_working_whole": cthy_prior["gdt758_primary_candidate_de"],
                "cthy_prior_confidence": cthy_prior["working_confidence"],
                "cthy_global_exact_occurrences": cthy_prior["reader_exact_occurrences"],
                "cthy_global_herbal_occurrences": cthy_prior["herbal_occurrences"],
                "chor_portable_whole": "anderer oder reproduktiver Pflanzenteilposten",
                "chor_forced_concrete_default": "Blütenstand",
                "chor_primary_rival": "Samen- oder Fruchtstand",
                "same_identity_reading": "DISFAVORED_BY_REPEATED_PARALLELISM",
                "specific_flower_vs_seed_credit": 0,
                "component_credit": 0,
            })
    assert len(output) == 15
    assert len({str(row["locus"]) for row in output}) == 14
    assert sum(int(row["direct_pair"]) for row in output) == 5
    return output


def build_shadow_audit() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in read_tsv(SHADOW_BRIDGES):
        output.append({
            **row,
            "strict_exact_chor_anchor": 0,
            "gdt767_disposition": "RETAIN_AS_C0_FLOWER_OR_SEED_SHADOW_LEAD",
            "reason": "The contact uses schor, chory, or shor rather than exact chor and remains non-score-ready.",
            "gdt767_identity_credit": 0,
        })
    assert len(output) == 4
    return output


def target_info() -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in read_tsv(OFCH_SPECS):
        output[row["surface"]] = {
            "surface": row["surface"],
            "target_family": "OFCH_CONTAINING",
            "predicted_channel": row["predicted_channel"],
            "prior_portable_default_de": row["portable_default_de"],
            "prior_bold_default_de": row["bold_default_de"],
            "prior_role_confidence": row["role_confidence"],
            "prior_identity_confidence": row["identity_confidence"],
            "primary_rival_de": row["primary_rival_de"],
            "secondary_rival_de": row["secondary_rival_de"],
        }
    for row in read_tsv(CHOR_SPECS):
        if row["surface"] == "pchor":
            continue
        output[row["surface"]] = {
            "surface": row["surface"],
            "target_family": "CHOR_SCHOR_LCHOR",
            "predicted_channel": CHOR_CHANNELS[row["surface"]],
            "prior_portable_default_de": row["portable_default_de"],
            "prior_bold_default_de": row["bold_default_de"],
            "prior_role_confidence": row["role_confidence"],
            "prior_identity_confidence": row["identity_confidence"],
            "primary_rival_de": row["primary_rival_de"],
            "secondary_rival_de": row["secondary_rival_de"],
        }
    assert len(output) == 28
    return output


def candidate_hit(candidate: Mapping[str, str], features: set[str], line_features: set[str]) -> bool:
    required = values(candidate["gate_all_r3"])
    any_of = values(candidate["gate_any_r3"])
    forbidden = values(candidate["forbid_line"])
    if not required and not any_of:
        return False
    return required <= features and (not any_of or bool(any_of & features)) and not bool(forbidden & line_features)


def evidence_level(
    hits: int,
    role_fit: bool,
    redundancy_penalty: bool,
    repeat_required: bool,
) -> tuple[int, str]:
    if redundancy_penalty:
        return 0, "REPEATED_PARALLELISM_COUNTEREVIDENCE"
    if repeat_required and hits < 2:
        return 0, "REPEAT_REQUIREMENT_NOT_MET"
    if hits >= 2 and role_fit:
        return 4, "REPEATED_GATE_AND_ROLE"
    if hits >= 2:
        return 3, "REPEATED_GATE"
    if hits == 1 and role_fit:
        return 2, "ONE_GATE_AND_ROLE"
    if hits == 1:
        return 1, "ONE_OCCURRENCE_GATE"
    return 0, "NO_TARGET_FREE_GATE_HIT"


def build_tournament(
    atlas: Sequence[Mapping[str, object]],
    candidates: Sequence[Mapping[str, str]],
    info: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in atlas:
        by_surface[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in sorted(by_surface):
        rows = by_surface[surface]
        target = info[surface]
        layer_groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for candidate in candidates:
            preferred = values(candidate["preferred_channels"])
            role_fit = str(target["predicted_channel"]) in preferred
            scope_hits: dict[str, int] = {}
            for scope in cofield.SCOPES:
                scope_hits[scope] = sum(
                    candidate_hit(
                        candidate,
                        set(row[f"{scope.lower()}_features"]),
                        set(row["line_features"]),
                    )
                    for row in rows
                )
            redundancy = bool(
                surface == "chor"
                and candidate["candidate_id"] == "S04"
                and scope_hits["LINE"] >= 2
            )
            level, label = evidence_level(
                scope_hits["R3"], role_fit, redundancy,
                candidate["repeat_required"] == "1",
            )
            legacy = int(
                candidate["candidate_id"] == "S01"
                and candidate["legacy_tiebreak_allowed"] == "1"
                and "Blüten" in str(target["prior_bold_default_de"])
            )
            evidence_score = (
                20 * level
                + 10 * scope_hits["R3"] / len(rows)
                + min(9, scope_hits["R3"])
            )
            exploratory_score = evidence_score + 2 * int(role_fit) + legacy
            record: dict[str, object] = {
                "surface": surface,
                "target_family": target["target_family"],
                "reader_exact_occurrences": len(rows),
                "predicted_channel_from_gdt766": target["predicted_channel"],
                "candidate_layer": candidate["candidate_layer"],
                "candidate_id": candidate["candidate_id"],
                "historical_expression": candidate["historical_expression"],
                "working_noun_de": candidate["working_noun_de"],
                "gate_all_r3": candidate["gate_all_r3"],
                "gate_any_r3": candidate["gate_any_r3"],
                "forbid_line": candidate["forbid_line"],
                "d1_gate_hits": scope_hits["D1"],
                "r3_gate_hits": scope_hits["R3"],
                "line_gate_hits": scope_hits["LINE"],
                "r3_gate_rate": f"{scope_hits['R3'] / len(rows):.6f}",
                "role_fit": int(role_fit),
                "repeat_required": candidate["repeat_required"],
                "repeat_requirement_met": int(
                    scope_hits["R3"] >= (2 if candidate["repeat_required"] == "1" else 1)
                ),
                "semantic_redundancy_penalty": int(redundancy),
                "evidence_level_0_4": level,
                "evidence_label": label,
                "evidence_score": f"{evidence_score:.6f}",
                "legacy_flower_tiebreak": legacy,
                "exploratory_score": f"{exploratory_score:.6f}",
                "identity_specificity": candidate["identity_specificity"],
                "source_ids": candidate["source_ids"],
                "attested_forms": candidate["attested_forms"],
                "attestation_scope": candidate["attestation_scope"],
                "literal_identity_confirmed": 0,
                "component_credit": 0,
            }
            layer_groups[str(candidate["candidate_layer"])].append(record)
        for layer_rows in layer_groups.values():
            evidence_order = sorted(
                layer_rows,
                key=lambda row: (
                    -int(row["evidence_level_0_4"]),
                    -float(row["evidence_score"]),
                    str(row["candidate_id"]),
                ),
            )
            exploratory_order = sorted(
                layer_rows,
                key=lambda row: (-float(row["exploratory_score"]), str(row["candidate_id"])),
            )
            for rank, row in enumerate(evidence_order, 1):
                row["evidence_rank"] = rank
            for rank, row in enumerate(exploratory_order, 1):
                row["exploratory_rank"] = rank
            output.extend(sorted(layer_rows, key=lambda row: str(row["candidate_id"])))
    assert len(output) == 28 * len(candidates)
    return output


def build_separability(tournament: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    by_candidate: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in tournament:
        by_candidate[str(row["candidate_id"])].append(row)
    vectors: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for candidate_id, rows in by_candidate.items():
        ordered = sorted(rows, key=lambda row: str(row["surface"]))
        vector = "|".join(
            f"{row['surface']}:{row['d1_gate_hits']}/{row['r3_gate_hits']}/{row['line_gate_hits']}"
            for row in ordered
        )
        digest = hashlib.sha256(vector.encode("utf-8")).hexdigest()[:12]
        layer = str(rows[0]["candidate_layer"])
        vectors[(layer, digest)].append(candidate_id)
    output: list[dict[str, object]] = []
    for group_no, ((layer, digest), candidate_ids) in enumerate(sorted(vectors.items()), 1):
        exemplar = by_candidate[sorted(candidate_ids)[0]][0]
        total_r3 = {
            candidate_id: sum(int(row["r3_gate_hits"]) for row in by_candidate[candidate_id])
            for candidate_id in candidate_ids
        }
        output.append({
            "observed_support_group": f"G767-SEP{group_no:02d}",
            "candidate_layer": layer,
            "candidate_ids": "|".join(sorted(candidate_ids)),
            "candidate_count": len(candidate_ids),
            "support_vector_sha256_12": digest,
            "total_r3_hits_by_candidate": "|".join(
                f"{candidate_id}:{total_r3[candidate_id]}" for candidate_id in sorted(candidate_ids)
            ),
            "observationally_separable_in_current_cofields": int(len(candidate_ids) == 1),
            "interpretation": (
                "Current target-free cofields distinguish this gate profile from every other candidate."
                if len(candidate_ids) == 1 else
                "These historical candidates have identical observed cofield support and remain rivals."
            ),
            "literal_identity_confirmed": 0,
        })
    return output


def selected_candidate(
    rows: Sequence[Mapping[str, object]], layer: str, fallback_id: str
) -> Mapping[str, object]:
    candidates = [row for row in rows if row["candidate_layer"] == layer]
    supported = [
        row for row in candidates
        if int(row["evidence_level_0_4"]) >= 2
        and not int(row["semantic_redundancy_penalty"])
        and int(row["repeat_requirement_met"])
    ]
    if not supported:
        return next(row for row in candidates if row["candidate_id"] == fallback_id)
    return sorted(
        supported,
        key=lambda row: (
            -int(row["evidence_level_0_4"]),
            -float(row["evidence_score"]),
            str(row["candidate_id"]),
        ),
    )[0]


def concrete_revision(surface: str, prior: str) -> tuple[str, str]:
    if surface in {"ofcheol", "qofcheol"}:
        return "Blütenzubereitung", "Auszug, Oel, Wasser, Wein oder Essig bleiben C0-Rivalen"
    return prior, "legacy concrete default retained until contradicted or replaced"


def portable_class(channel: str, form_de: object) -> str:
    form = str(form_de)
    templates = {
        "BASE_CONTENT": "benannter Drogen- oder Pflanzenteilkopf",
        "PART_AMOUNT": "Drogenportion oder Drogenanteil",
        "DRY_RESULT": "Trockenmaterial oder Trockenbereitung",
        "TERMINAL_RESULT": "Endprodukt oder Abschlusszubereitung einer Droge",
        "PREPARATION": "Zubereitung einer benannten Droge",
        "MOIST_PREPARATION": "feuchte Zubereitung einer benannten Droge",
        "EXTRACT": "benannte Zubereitung; Auszug oder Flüssigkeit nicht identifiziert",
        "COMPOUND_PREPARATION": "zusammengesetzte Arzneizubereitung",
    }
    base = templates[channel]
    return f"{base}; target-freie Kontextklasse {form}"


def build_dictionary(
    matrix: Sequence[Mapping[str, object]],
    tournament: Sequence[Mapping[str, object]],
    info: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in tournament:
        by_surface[str(row["surface"])].append(row)
    matrix_by_surface = {str(row["surface"]): row for row in matrix}
    output: list[dict[str, object]] = []
    for surface in sorted(info):
        rows = by_surface[surface]
        substance = selected_candidate(rows, "SUBSTANCE", "S00")
        form = selected_candidate(rows, "FORM", "F00")
        # `chor` repeatedly owns several mutually incompatible state fields.
        # Those contexts classify it as a content head, not as one permanently
        # dried or prepared form, so no single form candidate is exported.
        if surface == "chor":
            form = next(
                row for row in rows
                if row["candidate_layer"] == "FORM" and row["candidate_id"] == "F00"
            )
        target = info[surface]
        stats = matrix_by_surface[surface]
        revised, disposition = concrete_revision(surface, str(target["prior_bold_default_de"]))
        form_level = int(form["evidence_level_0_4"])
        form_confidence = (
            "C2_REPEATED_TARGET_FREE_FORM_GATE" if form_level >= 4 else
            "C1_TARGET_FREE_FORM_GATE" if form_level >= 2 else
            "C0_LOCAL_OR_FALLBACK_FORM"
        )
        if surface == "chor":
            portable = "anderer oder reproduktiver Pflanzenteilposten; nicht Blattgut"
        elif surface == "schor":
            portable = "Pflanzenteil-Unterposten"
        elif surface == "lchor":
            portable = "internes Drogen- oder Zubereitungsfeld"
        else:
            portable = portable_class(
                str(target["predicted_channel"]), form["working_noun_de"]
            )
        zero_features = all(
            int(stats[f"{feature.lower()}_line"]) == 0 for feature in cofield.FEATURES
        )
        output.append({
            "surface": surface,
            "target_family": target["target_family"],
            "reader_exact_occurrences": stats["reader_exact_occurrences"],
            "predicted_channel": target["predicted_channel"],
            "selected_target_free_substance_candidate": substance["candidate_id"],
            "selected_target_free_substance_de": substance["working_noun_de"],
            "substance_evidence_level_0_4": substance["evidence_level_0_4"],
            "selected_target_free_form_candidate": form["candidate_id"],
            "selected_target_free_form_de": form["working_noun_de"],
            "form_evidence_level_0_4": form_level,
            "portable_working_class_de": portable,
            "forced_concrete_default_de": revised,
            "forced_concrete_identity_confidence": "C0_REPLACEABLE_DEFAULT",
            "form_confidence": form_confidence,
            "prior_concrete_default_de": target["prior_bold_default_de"],
            "gdt767_default_disposition": disposition,
            "primary_rival_de": target["primary_rival_de"],
            "secondary_rival_de": target["secondary_rival_de"],
            "dry_d1_r3_line": stats["dry_d1_r3_line"],
            "moist_d1_r3_line": stats["moist_d1_r3_line"],
            "value_amount_d1_r3_line": stats["value_amount_d1_r3_line"],
            "prep_d1_r3_line": stats["prep_d1_r3_line"],
            "process_close_d1_r3_line": stats["process_close_d1_r3_line"],
            "cthy_leaf_d1_r3_line": stats["cthy_leaf_d1_r3_line"],
            "chor_repro_d1_r3_line": stats["chor_repro_d1_r3_line"],
            "zero_admitted_target_free_features": int(zero_features),
            "evidence": (
                f"form={form['candidate_id']} level={form_level}, hits D1/R3/line="
                f"{form['d1_gate_hits']}/{form['r3_gate_hits']}/{form['line_gate_hits']}; "
                f"substance={substance['candidate_id']} level={substance['evidence_level_0_4']}"
            ),
            "counterevidence": (
                "No independent exact chor or cthy anchor identifies an ofch substance; specific noun is a forced working default."
                if target["target_family"] == "OFCH_CONTAINING" else
                "The repeated cthy parallelism supports a different plant-part class but does not choose flower over seed or fruit."
                if surface == "chor" else
                "Specific substance identity is not independently selected."
            ),
            "specific_identity_replaceable": 1,
            "confirmed_lexeme": 0,
            "component_credit": 0,
            "unseen_form_export": 0,
        })
    assert len(output) == 28
    return output


def build_revised_reader(dictionary: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    defaults = {str(row["surface"]): row for row in dictionary}
    source = read_tsv(PASSAGE_SPECS)
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_locus[row["locus"]].append(row)
    line_renderers: dict[str, str] = {}
    line_eva: dict[str, str] = {}
    for locus, rows in by_locus.items():
        ordered = sorted(rows, key=lambda row: int(row["ordinal"]))
        line_renderers[locus] = "; ".join(
            str(defaults[row["surface"]]["forced_concrete_default_de"])
            if row["surface"] in defaults else row["local_default_de"]
            for row in ordered
        ) + "."
        line_eva[locus] = " ".join(row["surface"] for row in ordered)
    output: list[dict[str, object]] = []
    for row in source:
        update = defaults.get(row["surface"])
        output.append({
            "reader_token_id": f"G767-R{len(output)+1:02d}",
            "locus": row["locus"],
            "ordinal": row["ordinal"],
            "surface": row["surface"],
            "gdt766_local_default_de": row["local_default_de"],
            "gdt767_local_default_de": (
                update["forced_concrete_default_de"] if update else row["local_default_de"]
            ),
            "gdt767_confidence": (
                update["forced_concrete_identity_confidence"] if update else row["confidence"]
            ),
            "updated_target": int(update is not None),
            "written_line_eva": line_eva[row["locus"]],
            "gdt767_revised_line_de": line_renderers[row["locus"]],
            "renderer_boundary": "TOKEN_DEFAULTS_IN_WRITTEN_ORDER_SEMICOLONS_ASSERT_NO_ATTACHMENT",
            "confirmed_plaintext": 0,
            "component_credit": 0,
        })
    assert len(output) == 46
    assert len(by_locus) == 5
    return output


def write_historical_reader(
    path: Path,
    sources: Sequence[Mapping[str, str]],
    dictionary: Sequence[Mapping[str, object]],
    aggregate: Sequence[Mapping[str, object]],
    chor_cthy: Sequence[Mapping[str, object]],
    separability: Sequence[Mapping[str, object]],
    reader: Sequence[Mapping[str, object]],
) -> None:
    agg = {str(row["feature"]): row for row in aggregate}
    lines = [
        "# GDT767 historical identity and co-field reader", "",
        "The closest historical model is a mixed pharmacy record: a learned whole name, an optional part or preparation form, quality/state and degree fields; recipes add an opening formula, ingredient, amount, process and result. This is an architecture bridge, not a spelling equation.", "",
        "## Target-excluding result", "",
        f"The 25 observed OFCH-containing wholes contribute 43 exact positions. After blocking every target whole, pchor and all 172 GDT754 source-composed surfaces, independent OFCH contacts are: DRY {agg['DRY']['d1_occurrences']}/{agg['DRY']['r3_occurrences']}/{agg['DRY']['line_occurrences']}, MOIST {agg['MOIST']['d1_occurrences']}/{agg['MOIST']['r3_occurrences']}/{agg['MOIST']['line_occurrences']}, STAGE {agg['STAGE']['d1_occurrences']}/{agg['STAGE']['r3_occurrences']}/{agg['STAGE']['line_occurrences']}, VALUE/AMOUNT {agg['VALUE_AMOUNT']['d1_occurrences']}/{agg['VALUE_AMOUNT']['r3_occurrences']}/{agg['VALUE_AMOUNT']['line_occurrences']}, PREP {agg['PREP']['d1_occurrences']}/{agg['PREP']['r3_occurrences']}/{agg['PREP']['line_occurrences']}. Exact cthy and exact chor identity anchors are both 0/0/0.", "",
        "That supports drug/preparation and state/form classes. It does not independently select flower, seed, root, leaf, wood, resin, salt, oil, water, wine or vinegar.", "",
        "## Working dictionary", "",
        "| whole | n | portable class | forced concrete default | form evidence | identity confidence |", "|---|---:|---|---|---|---|",
    ]
    for row in dictionary:
        lines.append(
            f"| `{row['surface']}` | {row['reader_exact_occurrences']} | {row['portable_working_class_de']} | {row['forced_concrete_default_de']} | `{row['selected_target_free_form_candidate']}:{row['form_evidence_level_0_4']}` | `{row['forced_concrete_identity_confidence']}` |"
        )
    lines.extend([
        "", "## The useful plant-part bridge", "",
        f"Exact chor and cthy occur in parallel at {len(chor_cthy)} chor positions on {len({str(row['locus']) for row in chor_cthy})} loci; {sum(int(row['direct_pair']) for row in chor_cthy)} are direct pairs in both written orders. With the inherited cthy leaf-drug lead, chor is best treated as a different plant-part head. Flower versus seed/fruit remains unresolved.", "",
        "The four OFCH contacts with schor/chory/shor remain useful C0 shadows, but none is an exact chor anchor or score-ready relation. They keep the flower default alive; they do not raise it above seed or another drug.", "",
        "## Observationally tied historical candidates", "",
    ])
    for row in separability:
        if int(row["candidate_count"]) > 1:
            lines.append(f"- `{row['candidate_ids']}`: identical observed target-free support vector.")
    lines.extend(["", "## Five complete working lines", ""])
    seen: set[str] = set()
    for row in reader:
        locus = str(row["locus"])
        if locus in seen:
            continue
        seen.add(locus)
        lines.extend([
            f"### {locus}", "", f"EVA: `{row['written_line_eva']}`", "",
            str(row["gdt767_revised_line_de"]), "",
        ])
    lines.extend(["## Historical sources", ""])
    for source in sources:
        lines.append(
            f"- [{source['work']}]({source['primary_url']}) — {source['date_band']}; {source['register_evidence']}"
        )
    lines.extend([
        "", "No EVA character, initial or substring receives a Latin value. Every concrete noun in the five lines is a replaceable working default; none is confirmed plaintext.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = cofield.build_cofield()
    atlas_raw = result["atlas"]
    matrix_raw = result["matrix"]
    info = target_info()
    candidates = read_tsv(CANDIDATE_DECK)
    sources = read_tsv(SOURCE_REGISTRY)
    cthy_prior = next(
        row for row in read_tsv(CTHY_CENSUS) if row["surface"] == "cthy"
    )
    assert len(candidates) == 18
    assert len(sources) == 6
    assert cthy_prior["reader_exact_occurrences"] == "85"
    assert cthy_prior["herbal_occurrences"] == "83"
    assert cthy_prior["gdt758_primary_candidate_de"] == "Blattgut / Blattdroge"
    assert set(info) == set(result["target_surfaces"])
    assert all(values(row["source_ids"]) <= {source["source_id"] for source in sources} for row in candidates)

    atlas = flatten_atlas(atlas_raw)
    matrix = flatten_matrix(matrix_raw)
    aggregate = aggregate_ofch(atlas_raw)
    chor_cthy = build_chor_cthy(atlas_raw, cthy_prior)
    shadows = build_shadow_audit()
    tournament = build_tournament(atlas_raw, candidates, info)
    separability = build_separability(tournament)
    dictionary = build_dictionary(matrix_raw, tournament, info)
    reader = build_revised_reader(dictionary)

    write_tsv(output_dir / OUTPUT_NAMES[0], atlas)
    write_tsv(output_dir / OUTPUT_NAMES[1], matrix)
    write_tsv(output_dir / OUTPUT_NAMES[2], aggregate)
    write_tsv(output_dir / OUTPUT_NAMES[3], chor_cthy)
    write_tsv(output_dir / OUTPUT_NAMES[4], shadows)
    write_tsv(output_dir / OUTPUT_NAMES[5], tournament)
    write_tsv(output_dir / OUTPUT_NAMES[6], separability)
    write_tsv(output_dir / OUTPUT_NAMES[7], dictionary)
    write_tsv(output_dir / OUTPUT_NAMES[8], reader)
    write_historical_reader(
        output_dir / OUTPUT_NAMES[9], sources, dictionary, aggregate,
        chor_cthy, separability, reader,
    )

    evidence_forms = Counter(str(row["selected_target_free_form_candidate"]) for row in dictionary)
    zero_feature_forms = [
        str(row["surface"]) for row in dictionary
        if int(row["zero_admitted_target_free_features"])
    ]
    downgraded = [
        str(row["surface"]) for row in dictionary
        if row["gdt767_default_disposition"] != "legacy concrete default retained until contradicted or replaced"
    ]
    tied_groups = [row for row in separability if int(row["candidate_count"]) > 1]
    def supported_targets(candidate_id: str, family: str | None = None) -> list[str]:
        selected = [
            row for row in tournament
            if row["candidate_id"] == candidate_id
            and int(row["r3_gate_hits"]) > 0
            and (family is None or row["target_family"] == family)
        ]
        return [
            f"{row['surface']}:{row['r3_gate_hits']}"
            for row in sorted(selected, key=lambda row: str(row["surface"]))
        ]
    guard = result["summary"]
    payload = {
        "schema": "GDT767_RESULT_V1",
        "status": STATUS,
        "scope": {
            **guard,
            "historical_sources": len(sources),
            "historical_candidates": len(candidates),
            "candidate_tournament_rows": len(tournament),
            "chor_cthy_parallel_positions": len(chor_cthy),
            "chor_cthy_parallel_loci": len({str(row["locus"]) for row in chor_cthy}),
            "chor_cthy_direct_pairs": sum(int(row["direct_pair"]) for row in chor_cthy),
            "cthy_prior_exact_occurrences": int(cthy_prior["reader_exact_occurrences"]),
            "cthy_prior_herbal_occurrences": int(cthy_prior["herbal_occurrences"]),
            "shadow_reproductive_contacts": len(shadows),
            "working_dictionary_rows": len(dictionary),
            "complete_reader_tokens": len(reader),
            "complete_reader_lines": len({str(row["locus"]) for row in reader}),
        },
        "ofch_target_excluding_features": {
            row["feature"]: {
                "d1": row["d1_occurrences"],
                "r3": row["r3_occurrences"],
                "line": row["line_occurrences"],
            }
            for row in aggregate
        },
        "selected_target_free_form_candidates": dict(sorted(evidence_forms.items())),
        "zero_target_free_feature_forms": zero_feature_forms,
        "concrete_default_downgrades": downgraded,
        "observationally_tied_candidate_groups": [row["candidate_ids"] for row in tied_groups],
        "specific_candidate_gate_leads": {
            "powder_ofch": supported_targets("F03", "OFCH_CONTAINING"),
            "moist_extract_ofch": supported_targets("F05", "OFCH_CONTAINING"),
            "oil_ofch": supported_targets("F06", "OFCH_CONTAINING"),
            "water_ofch": supported_targets("F07", "OFCH_CONTAINING"),
            "wine_ofch": supported_targets("F08", "OFCH_CONTAINING"),
            "vinegar_ofch": supported_targets("F09", "OFCH_CONTAINING"),
            "exact_chor_flower_ofch": supported_targets("S01", "OFCH_CONTAINING"),
            "exact_chor_seed_ofch": supported_targets("S02", "OFCH_CONTAINING"),
            "cthy_leaf_all_targets": supported_targets("S04"),
        },
        "interpretation": {
            "historical_architecture": "LEARNED_WHOLE_PLUS_PART_OR_FORM_PLUS_QUALITY_DEGREE_OR_RECIPE_FIELDS",
            "portable_ofch_class": "DRUG_OR_PREPARATION_WITH_STATE_FORM_SUBCLASSES",
            "specific_ofch_substance": "OPEN",
            "cthy_chor_relation": "PARALLEL_DISTINCT_PLANT_PART_HEADS",
            "chor_forced_default": "FLOWER_HEAD_WITH_SEED_OR_FRUIT_HEAD_RIVAL",
            "flower_default_status": "C0_RETAINED_UNTIL_CONTRADICTED_OR_REPLACED",
            "oil_water_wine_vinegar": "OBSERVATIONALLY_UNSEPARATED_AND_UNSUPPORTED_FOR_OFCH_EOL",
        },
        "claim_boundary": {
            "forced_concrete_replaceable_defaults": len(dictionary),
            "confirmed_lexemes": 0,
            "confirmed_substances": 0,
            "plaintext_clauses": 0,
            "component_credit": 0,
            "new_pages": 0,
            "new_images": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / OUTPUT_NAMES[10]).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({
        "status": result["status"],
        "scope": result["scope"],
        "selected_forms": result["selected_target_free_form_candidates"],
        "downgrades": result["concrete_default_downgrades"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
