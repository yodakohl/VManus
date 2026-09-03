#!/usr/bin/env python3
"""Build the GDT768 chor/shor complete-whole identity tournament.

The experiment stays inside the already admitted guarded cache. It compares
five explicit whole-word models, preserves a concrete C0 reading for every
anchor and every token in twelve complete lines, and never turns an EVA
substring into a Latin letter, sound, morpheme, or confirmed translation.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt768_chor_shor_part_identity_tournament")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

ANCHOR_SPECS = SRC / "ANCHOR_6_DEFAULT_SPECS.tsv"
MODEL_SPECS = SRC / "MODEL_5_SPECS.tsv"
COMPARISON_SPECS = SRC / "COMPARISON_FEATURE_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_PART_SIGNATURES.tsv"
LINE_SPECS = SRC / "LINE_12_TOKEN_DEFAULT_SPECS.tsv"

OUTPUT_NAMES = (
    "ANCHOR_404_OCCURRENCE_ATLAS.tsv",
    "MULTI_ANCHOR_33_LINE_ATLAS.tsv",
    "ANCHOR_15_PAIR_SUMMARY.tsv",
    "ANCHOR_6X3X3_FAMILY_ABLATION.tsv",
    "ANCHOR_6_ROLE_GEOMETRY.tsv",
    "MODEL_OBSERVED_METRICS.tsv",
    "MODEL_5_FEATURE_EVIDENCE.tsv",
    "MODEL_5_SCOREBOARD.tsv",
    "GDT768_6_WORKING_DICTIONARY.tsv",
    "TWELVE_COMPLETE_LINE_READER.tsv",
    "HISTORICAL_PART_REGISTER_READER.md",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__404_EXACT_ANCHOR_OCCURRENCES__33_MULTI_ANCHOR_LINES__"
    "CHOR_SHOR_GLOBAL_DRY_MOIST_MODEL_REJECTED_BY_FAMILY_ABLATION__"
    "CHOR_SHOR_PARALLEL_NOMINAL_PLANT_PART_WHOLES__"
    "FLOWER_VS_SEED_FRUIT_DIRECTION_UNRESOLVED__"
    "6_CONCRETE_REPLACEABLE_DEFAULTS__12_COMPLETE_CONCRETE_LINES__"
    "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core_atlas = load_module("gdt768_core", SRC / "core_atlas.py")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
    fields: Sequence[str] | None = None,
) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty TSV: {path.name}")
    names = list(fields or rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=names,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def json_cell(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def tuple_cell(value: Iterable[object]) -> str:
    items = [str(item) for item in value]
    return "|".join(items) if items else "NONE"


def donor_cell(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows:
        return "NONE"
    output: list[str] = []
    for row in rows:
        features = tuple_cell(row.get("features", ()))
        output.append(
            f"{row['surface']}@{row['ordinal']}:d{row['distance']}[{features}]"
        )
    return ";".join(output)


def blocked_cell(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows:
        return "NONE"
    return ";".join(
        f"{row['surface']}@{row['ordinal']}:d{row['distance']}" for row in rows
    )


def flatten_occurrences(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    base_fields = (
        "target_occurrence_id",
        "surface",
        "page",
        "physical_folio",
        "locus",
        "line_number",
        "section",
        "language",
        "hand",
        "ordinal",
        "token_index",
        "line_token_count",
        "line_position",
        "normalized_line_position",
        "paragraph_start_line",
        "paragraph_end_line",
        "true_paragraph_opener",
        "true_paragraph_closer",
        "written_line_eva",
    )
    for row in rows:
        flat = {field: row[field] for field in base_fields}
        flat["normalized_line_position"] = f"{float(row['normalized_line_position']):.6f}"
        for radius in core_atlas.ABLATION_RADII:
            view = row["family_views"][radius]
            for scope in core_atlas.SCOPES:
                scope_view = view["scope"][scope]
                stem = f"ed{radius}_{scope.lower()}"
                flat[f"{stem}_features"] = tuple_cell(scope_view["features"])
                flat[f"{stem}_donors"] = donor_cell(scope_view["donors"])
                flat[f"{stem}_family_blocked"] = blocked_cell(
                    scope_view["blocked_family_donors"]
                )
                flat[f"{stem}_source_composed_blocked"] = blocked_cell(
                    scope_view["blocked_source_composed_donors"]
                )
                flat[f"{stem}_eligible_positions"] = scope_view[
                    "eligible_donor_positions"
                ]
                flat[f"{stem}_family_blocked_positions"] = scope_view[
                    "family_blocked_positions"
                ]
                flat[f"{stem}_source_composed_blocked_positions"] = scope_view[
                    "source_composed_blocked_positions"
                ]
        flat.update(
            {
                "reader_exact": 1,
                "gdt754_source_composed_gate": "ACTIVE_172_SURFACES",
                "edit_distance_semantic_credit": 0,
                "component_export_credit": 0,
            }
        )
        output.append(flat)
    return output


def flatten_multi_anchor(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        output.append(
            {
                "multi_anchor_line_id": row["multi_anchor_line_id"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": row["locus"],
                "line_number": row["line_number"],
                "section": row["section"],
                "language": row["language"],
                "hand": row["hand"],
                "paragraph_start_line": row["paragraph_start_line"],
                "paragraph_end_line": row["paragraph_end_line"],
                "line_token_count": row["line_token_count"],
                "distinct_exact_anchor_count": row["distinct_exact_anchor_count"],
                "exact_anchor_occurrence_count": row["exact_anchor_occurrence_count"],
                "exact_anchor_surfaces": tuple_cell(row["exact_anchor_surfaces"]),
                "exact_anchor_ordinals": tuple_cell(row["exact_anchor_ordinals"]),
                "exact_anchor_counts": json_cell(row["exact_anchor_counts"]),
                "written_line_eva": row["written_line_eva"],
                "reader_exact_anchor_positions": 1,
                "confirmed_plaintext": 0,
                "component_export_credit": 0,
            }
        )
    return output


def flatten_pairs(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        output.append(
            {
                **{
                    key: row[key]
                    for key in (
                        "pair_id",
                        "first_surface",
                        "second_surface",
                        "line_count",
                        "page_count",
                        "occurrence_pair_count",
                        "direct_pair_count",
                        "first_before_second",
                        "second_before_first",
                    )
                },
                "loci": tuple_cell(row["loci"]),
                "pages": tuple_cell(row["pages"]),
                "identity_direction_credit": 0,
                "component_export_credit": 0,
            }
        )
    return output


def flatten_ablation(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        flat: dict[str, object] = {
            key: row[key]
            for key in (
                "target_surface",
                "family_radius",
                "scope",
                "target_occurrences",
                "global_family_blocked_surface_count",
                "global_source_composed_blocked_surface_count",
                "eligible_donor_positions",
                "family_blocked_donor_positions",
                "source_composed_blocked_donor_positions",
                "eligible_unique_donor_surfaces",
            )
        }
        flat["global_family_blocked_surfaces"] = tuple_cell(
            row["global_family_blocked_surfaces"]
        )
        for feature in core_atlas.FEATURES:
            stem = feature.lower()
            flat[f"{stem}_target_occurrences"] = row["feature_occurrence_counts"][feature]
            flat[f"{stem}_donor_positions"] = row["feature_donor_counts"][feature]
        flat["eligible_donor_surface_counts"] = json_cell(row["donor_surface_counts"])
        flat["family_blocked_surface_counts"] = json_cell(row["blocked_surface_counts"])
        flat["source_composed_blocked_surface_counts"] = json_cell(
            row["source_composed_blocked_surface_counts"]
        )
        flat["edit_distance_semantic_credit"] = 0
        flat["component_export_credit"] = 0
        output.append(flat)
    return output


def flatten_roles(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        output.append(
            {
                "surface": row["surface"],
                "reader_exact_occurrences": row["reader_exact_occurrences"],
                "pages": row["pages"],
                "physical_folios": row["physical_folios"],
                "loci": row["loci"],
                "line_first": row["line_first"],
                "line_last": row["line_last"],
                "line_position_counts": json_cell(row["line_position_counts"]),
                "paragraph_start_line": row["paragraph_start_line"],
                "paragraph_end_line": row["paragraph_end_line"],
                "true_paragraph_opener": row["true_paragraph_opener"],
                "true_paragraph_closer": row["true_paragraph_closer"],
                "multi_anchor_line_occurrences": row["multi_anchor_line_occurrences"],
                "multi_anchor_loci": row["multi_anchor_loci"],
                "mean_ordinal": f"{float(row['mean_ordinal']):.6f}",
                "mean_normalized_line_position": f"{float(row['mean_normalized_line_position']):.6f}",
                "section_counts": json_cell(row["section_counts"]),
                "language_counts": json_cell(row["language_counts"]),
                "hand_counts": json_cell(row["hand_counts"]),
                "current_target_role_occurrence_counts": json_cell(
                    row["current_target_role_occurrence_counts"]
                ),
                "current_target_axis_occurrence_counts": json_cell(
                    row["current_target_axis_occurrence_counts"]
                ),
                "role_is_translation": 0,
                "component_export_credit": 0,
            }
        )
    return output


def build_dictionary(
    anchor_specs: Sequence[Mapping[str, str]],
    scoreboard: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    ranks = {str(row["model_id"]): int(row["rank"]) for row in scoreboard}
    scores = {str(row["model_id"]): str(row["score_0_1"]) for row in scoreboard}
    direction_gap = abs(float(scores["M02"]) - float(scores["M03"]))
    assert direction_gap < 0.10, "directional part models unexpectedly separated"

    concrete_overrides = {
        "chor": "Blütenstand",
        "shor": "Fruchtstand",
        "cthy": "Blattgut",
        "dair": "Anteil II",
        "kooiin": "dicke oder kriechende Wurzeldroge",
        "koaiin": "kriechende Wurzeldroge",
    }
    portable_overrides = {
        "chor": "nicht-Blatt-Pflanzenteilposten; reproduktive Rolle möglich",
        "shor": "reproduktiver Pflanzenteilposten; genaue Organart offen",
        "cthy": "Blattgut oder oberirdische Blattdroge",
        "dair": "abgemessene Fraktion oder Anteil, Stufe II",
        "kooiin": "Untergrund- oder Wurzelstock-Drogenkopf; genaue Identität offen",
        "koaiin": "Schwesterform eines Untergrund- oder Wurzelstockkopfs; genaue Identität offen",
    }
    confidence_overrides = {
        "chor": "C2_NOMINAL_PART_ROLE__C0_FLOWER_DIRECTION",
        "shor": "C2_NOMINAL_PART_ROLE__C0_FRUIT_DIRECTION",
        "cthy": "C2_HERBAL_LEAF_CLASS__C1_LEAF_IDENTITY",
        "dair": "C2_FRACTION_FAMILY__C0_SUBSTANCE_IDENTITY",
        "kooiin": "C1_VISUAL_ROOTSTOCK_CLASS__N2",
        "koaiin": "C0_C1_VISUAL_ROOTSTOCK_CLASS__N1",
    }
    rival_overrides = {
        "chor": ("Samen- oder Fruchtstand", "allgemeiner Kraut- oder Pflanzenteil"),
        "shor": ("Blütenstand", "Samenstand"),
    }
    output: list[dict[str, object]] = []
    for row in anchor_specs:
        surface = row["surface"]
        output.append(
            {
                "anchor_id": row["anchor_id"],
                "surface": surface,
                "anchor_class": row["anchor_class"],
                "portable_default_de": portable_overrides[surface],
                "concrete_default_de": concrete_overrides[surface],
                "working_confidence": confidence_overrides[surface],
                "primary_rival_de": rival_overrides.get(
                    surface, (row["rival_1_de"], row["rival_2_de"])
                )[0],
                "secondary_rival_de": rival_overrides.get(
                    surface, (row["rival_1_de"], row["rival_2_de"])
                )[1],
                "positive_evidence_de": row["positive_evidence_de"],
                "counterevidence_de": row["counterevidence_de"],
                "register_scope": row["register_scope"],
                "tournament_result": (
                    "PARALLEL_NOMINAL_PART_WHOLES__BOTANICAL_DIRECTION_UNRESOLVED"
                    if surface in {"chor", "shor"}
                    else "CONTROL_DEFAULT_RETAINED"
                ),
                "model_rank_context": json_cell(ranks),
                "directional_model_gap": f"{direction_gap:.6f}",
                "replacement_guard": row["replacement_guard"],
                "default_is_translation": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            }
        )
    assert len(output) == 6
    return output


def build_reader(
    specs: Sequence[Mapping[str, str]],
    dictionary: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    _g764, environment = core_atlas.load_guarded_environment(ROOT)
    context = environment["context"]
    default_by_anchor = {
        str(row["surface"]): str(row["concrete_default_de"]) for row in dictionary
    }
    grouped: defaultdict[int, list[Mapping[str, str]]] = defaultdict(list)
    for row in specs:
        grouped[int(row["line_rank"])].append(row)
    assert sorted(grouped) == list(range(1, 13)), "reader must contain ranks 1..12"

    output: list[dict[str, object]] = []
    for rank in sorted(grouped):
        rows = sorted(grouped[rank], key=lambda row: int(row["ordinal"]))
        locus = rows[0]["locus"]
        assert all(row["locus"] == locus for row in rows)
        assert locus in context.by_line
        line = context.by_line[locus]
        assert [int(row["ordinal"]) for row in rows] == list(range(1, len(line) + 1))
        assert len(rows) == len(line)
        written = " ".join(str(token["eva"]) for token in line)
        assert [row["surface"] for row in rows] == [str(token["eva"]) for token in line]
        assert len({row["line_working_reader_de"] for row in rows}) == 1
        assert len({row["line_finding_de"] for row in rows}) == 1

        sequence: list[str] = []
        line_output: list[dict[str, object]] = []
        for row, token in zip(rows, line):
            ordinal = int(row["ordinal"])
            exact = int(bool(context.exact[(locus, int(token["token_index"]))]))
            assert exact == 1, f"nonexact reader token: {locus}@{ordinal}"
            surface = row["surface"]
            concrete = default_by_anchor.get(surface, row["concrete_default_de"])
            sequence.append(f"{surface}={concrete}")
            line_output.append(
                {
                    "line_rank": rank,
                    "locus": locus,
                    "line_class": row["line_class"],
                    "ordinal": ordinal,
                    "surface": surface,
                    "reader_exact": exact,
                    "portable_role_de": row["portable_role_de"],
                    "concrete_default_de": concrete,
                    "working_confidence": row["working_confidence"],
                    "positive_evidence_de": row["positive_evidence_de"],
                    "counterevidence_de": row["counterevidence_de"],
                    "primary_rival_de": row["primary_rival_de"],
                    "structural_only": int(row["structural_only"]),
                    "written_line_eva": written,
                    "token_default_sequence": "",
                    "line_working_reader_de": row["line_working_reader_de"],
                    "line_finding_de": row["line_finding_de"],
                    "confirmed_plaintext": 0,
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                }
            )
        complete_sequence = " | ".join(sequence)
        for item in line_output:
            item["token_default_sequence"] = complete_sequence
        output.extend(line_output)
    assert len({str(row["locus"]) for row in output}) == 12
    return output


def build_historical_reader(
    dictionary: Sequence[Mapping[str, object]],
    scoreboard: Sequence[Mapping[str, object]],
    reader: Sequence[Mapping[str, object]],
) -> str:
    lines = [
        "# GDT768 — konkreter chor/shor-Arbeitsreader",
        "",
        "Dies ist eine **Arbeitslesung**, keine entzifferte Übersetzung. Die fett",
        "gedachten konkreten Wörter sind absichtlich ersetzbare C0/C1-Defaults;",
        "keine EVA-Zeichenfolge erhält dadurch einen lateinischen Laut- oder",
        "Buchstabenwert.",
        "",
        "## Ergebnis des Fünf-Modell-Vergleichs",
        "",
        "Die globale These `chor = trocken` und `shor = feucht` verliert ihren",
        "entscheidenden Kontrast, sobald nahe vollständige Formfamilien als Geber",
        "entfernt werden. Gleichzeitig bleiben die zielwortfreien Außenprofile",
        "sehr ähnlich und zwölf vollständige Linien behandeln beide Formen als",
        "nominale Inhaltsfelder. Am besten trägt daher die gemeinsame Aussage:",
        "**zwei parallele Pflanzenteil-/Inhaltswörter**. Welche Richtung Blüte",
        "gegen Samen/Frucht hat, bleibt unentschieden.",
        "",
        "| Rang | Modell | Score | Entscheidung |",
        "|---:|---|---:|---|",
    ]
    for row in sorted(scoreboard, key=lambda item: int(item["rank"])):
        lines.append(
            f"| {row['rank']} | `{row['model_id']}` {row['model_label']} | "
            f"{row['score_0_1']} | {row['decision']} |"
        )
    lines.extend(
        [
            "",
            "## Sechs Ganzwort-Defaults",
            "",
            "| EVA-Ganzwort | portabler Arbeitswert | konkrete Ausgabe | Sicherheit | stärkster Rivale |",
            "|---|---|---|---|---|",
        ]
    )
    for row in dictionary:
        lines.append(
            f"| `{row['surface']}` | {row['portable_default_de']} | "
            f"**{row['concrete_default_de']}** | {row['working_confidence']} | "
            f"{row['primary_rival_de']} |"
        )
    lines.extend(["", "## Zwölf vollständige Linien", ""])
    by_line: defaultdict[int, list[Mapping[str, object]]] = defaultdict(list)
    for row in reader:
        by_line[int(row["line_rank"])].append(row)
    for rank in sorted(by_line):
        rows = sorted(by_line[rank], key=lambda item: int(item["ordinal"]))
        lines.extend(
            [
                f"### {rank}. `{rows[0]['locus']}` — {rows[0]['line_class']}",
                "",
                f"EVA: `{rows[0]['written_line_eva']}`",
                "",
                f"Arbeitslesung: {rows[0]['line_working_reader_de']}",
                "",
                f"Warum sie zählt: {rows[0]['line_finding_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Grenze",
            "",
            "`chor=Blütenstand` und `shor=Fruchtstand` sind der aktuelle konkrete",
            "Renderer, nicht der behauptete Klartext. Die Umkehrung bleibt ebenso",
            "möglich. `dair` bleibt Anteil II und ist kein globales Wurzelwort;",
            "`r/s/l/o/ol` erhalten hier keine freien Werte Wurzel/Samen/Holz/Wasser/Öl.",
            "Bestätigte Lexeme, Komponenten und Klartextsätze: jeweils **0**.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    art = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    art.mkdir(parents=True, exist_ok=True)

    core = core_atlas.build_core_atlas(ROOT)
    anchor_specs = read_tsv(ANCHOR_SPECS)
    model_specs = read_tsv(MODEL_SPECS)
    comparison_specs = read_tsv(COMPARISON_SPECS)
    historical_specs = read_tsv(HISTORICAL_SPECS)
    line_specs = read_tsv(LINE_SPECS)
    scoring = load_module("gdt768_model_scoring", SRC / "model_scoring.py")
    model_result = scoring.build_model_evidence(
        core, model_specs, comparison_specs, historical_specs
    )
    metrics = model_result["observed_metrics"]
    feature_evidence = model_result["feature_by_model_evidence"]
    scoreboard = model_result["scoreboard"]

    occurrence_rows = flatten_occurrences(core["occurrences"])
    multi_rows = flatten_multi_anchor(core["multi_anchor_lines"])
    pair_rows = flatten_pairs(core["pair_summary"])
    ablation_rows = flatten_ablation(core["family_ablation"])
    role_rows = flatten_roles(core["role_geometry"])
    dictionary = build_dictionary(anchor_specs, scoreboard)
    reader = build_reader(line_specs, dictionary)
    historical_reader = build_historical_reader(dictionary, scoreboard, reader)

    write_tsv(art / OUTPUT_NAMES[0], occurrence_rows)
    write_tsv(art / OUTPUT_NAMES[1], multi_rows)
    write_tsv(art / OUTPUT_NAMES[2], pair_rows)
    write_tsv(art / OUTPUT_NAMES[3], ablation_rows)
    write_tsv(art / OUTPUT_NAMES[4], role_rows)
    write_tsv(art / OUTPUT_NAMES[5], metrics)
    write_tsv(art / OUTPUT_NAMES[6], feature_evidence)
    write_tsv(art / OUTPUT_NAMES[7], scoreboard)
    write_tsv(art / OUTPUT_NAMES[8], dictionary)
    write_tsv(art / OUTPUT_NAMES[9], reader)
    (art / OUTPUT_NAMES[10]).write_text(historical_reader, encoding="utf-8")

    ranks = sorted(scoreboard, key=lambda row: int(row["rank"]))
    result = {
        "experiment_id": "GDT768",
        "status": STATUS,
        "scope": {
            "source": "ALREADY_ADMITTED_GUARDED_CACHE_ONLY",
            "new_page_opened": False,
            "new_image_opened": False,
            "new_transcription_opened": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "counts": {
            "anchor_forms": 6,
            "anchor_occurrences": len(occurrence_rows),
            "anchor_pages": core["metadata"]["target_pages"],
            "anchor_loci": core["metadata"]["target_loci"],
            "multi_anchor_lines": len(multi_rows),
            "multi_anchor_pages": core["metadata"]["multi_anchor_pages"],
            "unordered_anchor_pairs": len(pair_rows),
            "family_ablation_rows": len(ablation_rows),
            "model_candidates": len(scoreboard),
            "complete_reader_lines": len({row["locus"] for row in reader}),
            "reader_tokens": len(reader),
        },
        "guards": {
            "guard_selected": core["metadata"]["guard"]["selected"],
            "guard_skipped_forbidden": core["metadata"]["guard"]["skipped_forbidden"],
            "guard_skipped_not_allowed": core["metadata"]["guard"]["skipped_not_allowed"],
            "gdt754_source_composed_surfaces": core["metadata"][
                "gdt754_source_composed_surface_count"
            ],
            "gdt754_target_context_exposures": core["metadata"][
                "gdt754_source_composed_target_context_exposures"
            ],
            "edit_distance_semantic_credit": 0,
            "component_export_credit": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "model_result": {
            "top_model_id": ranks[0]["model_id"],
            "top_model_score": ranks[0]["score_0_1"],
            "top_model_decision": ranks[0]["decision"],
            "chor_shor_relation": "PARALLEL_NOMINAL_PLANT_PART_OR_CONTENT_WHOLES",
            "global_dry_moist_pair": "REJECTED_BY_SHOR_POLARITY_REVERSAL_AFTER_FAMILY_ABLATION",
            "flower_seed_fruit_direction": "UNRESOLVED__CONCRETE_C0_CHOR_FLOWER_SHOR_FRUIT",
        },
        "dictionary_result": {
            "entries": len(dictionary),
            "concrete_defaults_present": all(row["concrete_default_de"] for row in dictionary),
            "confirmed_lexemes": 0,
            "component_exports": 0,
        },
        "reader_result": {
            "complete_lines": len({row["locus"] for row in reader}),
            "tokens": len(reader),
            "all_tokens_have_default": all(row["concrete_default_de"] for row in reader),
            "all_tokens_reader_exact": all(int(row["reader_exact"]) == 1 for row in reader),
            "confirmed_plaintext_clauses": 0,
        },
        "claim_boundary": {
            "confirmed_english_lexemes": 0,
            "confirmed_german_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "identified_language": None,
            "identified_cipher": None,
            "identified_plant_or_substance": None,
            "identified_component_values": 0,
        },
    }
    (art / OUTPUT_NAMES[11]).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
