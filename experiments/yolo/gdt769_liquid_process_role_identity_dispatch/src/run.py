#!/usr/bin/env python3
"""Build the GDT769 role, identity, and concrete complete-line reader.

Only the already admitted guarded cache inherited through GDT764 is used.
Complete EVA words, structural roles, and German working defaults remain
separate. No character, sound, Latin initial, productive substring, confirmed
lexeme, or plaintext credit is created.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt769_liquid_process_role_identity_dispatch")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

TARGET_SPECS = SRC / "TARGET_5_ROLE_IDENTITY_SPECS.tsv"
ROLE_SPECS = SRC / "ROLE_5_MODEL_SPECS.tsv"
FRAME_SPECS = SRC / "FRAME_SIGNATURE_SPECS.tsv"
IDENTITY_SPECS = SRC / "IDENTITY_CANDIDATE_SPECS.tsv"
HISTORICAL_SOURCES = SRC / "HISTORICAL_SOURCE_REGISTRY.tsv"
HISTORICAL_PREDICTIONS = SRC / "HISTORICAL_IDENTITY_PREDICTIONS.tsv"
HISTORICAL_RELATORS = SRC / "HISTORICAL_RELATOR_ANALOGUES.tsv"
LINE_SPECS = SRC / "LINE_READER_DEFAULT_SPECS.tsv"

OUTPUT_NAMES = (
    "TARGET_640_RAW_OCCURRENCE_ATLAS.tsv",
    "TARGET_526_EXACT_CONTEXT_ATLAS.tsv",
    "TARGET_5_CENSUS.tsv",
    "TARGET_5_ROLE_GEOMETRY.tsv",
    "SIGNATURE_5_SUMMARY.tsv",
    "SUPPORT_52_LOCUS_ATLAS.tsv",
    "LEAVE_ONE_LOCUS_OUT.tsv",
    "CONTROL_SPAN_ATLAS.tsv",
    "DONOR_BLOCK_REGISTRY.tsv",
    "FRAME_16X5_EVIDENCE.tsv",
    "FRAME_LOCUS_EVIDENCE.tsv",
    "ROLE_5X5_SCOREBOARD.tsv",
    "IDENTITY_CANDIDATE_SCOREBOARD.tsv",
    "GDT769_5_WORKING_DICTIONARY.tsv",
    "TWELVE_COMPLETE_LINE_READER.tsv",
    "HISTORICAL_ROLE_IDENTITY_READER.md",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__640_RAW_526_EXACT_TARGET_OCCURRENCES__"
    "OL_RELATIONAL_FIELD_LINKER_WORKING_TIEBREAK__"
    "CKHY_MIX_PROCESS_CONCRETE_RIVAL_ROLE_OPEN__"
    "PCHEEY_BOUND_PREPARATION_FORM_FIELD_SELECTED__"
    "OLS_BOUND_MEASURE_PRODUCT_FIELD_WORKING_TIEBREAK__"
    "OTAR_SEQUENCE_FIELD_LINKER_WORKING_TIEBREAK__"
    "12_COMPLETE_109_TOKEN_LINES__"
    "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core_atlas = load_module("gdt769_core", SRC / "core_atlas.py")
model_scoring = load_module("gdt769_model", SRC / "model_scoring.py")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalise_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): normalise_json(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (set, frozenset)):
        return [normalise_json(item) for item in sorted(value, key=str)]
    if isinstance(value, (list, tuple)):
        return [normalise_json(item) for item in value]
    return value


def json_cell(value: object) -> str:
    return json.dumps(
        normalise_json(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def serialise_cell(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        return json_cell(value)
    return "" if value is None else value


def tabularise(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        {str(key): serialise_cell(value) for key, value in row.items()}
        for row in rows
    ]


def field_union(rows: Sequence[Mapping[str, object]]) -> list[str]:
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            name = str(key)
            if name not in seen:
                seen.add(name)
                fields.append(name)
    return fields


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty TSV: {path.name}")
    names = field_union(rows)
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


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(
        json.dumps(normalise_json(value), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def flatten_controls(
    controls: Mapping[str, Sequence[Mapping[str, object]]],
) -> list[dict[str, object]]:
    labels = {
        "amount_spans": "EXACT_AMOUNT_SPAN",
        "value_spans": "EXACT_OLS_VALUE_SPAN",
        "bounded_value_spans": "EXACT_X_DAIIN_SPAN",
        "anchor_occurrences": "EXACT_STATE_OR_OLY_ANCHOR",
    }
    output: list[dict[str, object]] = []
    for key in labels:
        output.extend(
            {"control_class": labels[key], **row} for row in controls[key]
        )
    return output


def flatten_blocks(blocks: Mapping[str, object]) -> list[dict[str, object]]:
    definitions = (
        ("TARGET_PANEL", blocks["target_panel"], "five targets cannot donate meaning"),
        (
            "GDT754_SOURCE_COMPOSED",
            blocks["gdt754_source_composed"],
            "source-composed wholes blocked before semantic scoring",
        ),
        (
            "GDT737_EXPLICIT_QUARANTINE",
            blocks["gdt737_explicit_quarantine"],
            "explicit literal-head quarantine",
        ),
        (
            "UNION_ANY_TARGET_ED2",
            blocks["family_ed2_union"],
            "within edit distance two of any target; shape sensitivity only",
        ),
    )
    return [
        {
            "block_class": block_class,
            "target_scope": "ALL_FIVE_TARGETS",
            "surface": surface,
            "semantic_identity_credit": 0,
            "component_export_credit": 0,
            "note": note,
        }
        for block_class, surfaces, note in definitions
        for surface in surfaces
    ]


def build_reader(
    specs: Sequence[Mapping[str, str]],
    dictionary: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    _g764, environment = core_atlas.load_guarded_environment(ROOT)
    context = environment["context"]
    dictionary_by_surface = {str(row["surface"]): row for row in dictionary}
    grouped: defaultdict[int, list[Mapping[str, str]]] = defaultdict(list)
    for row in specs:
        grouped[int(row["line_rank"])].append(row)
    if sorted(grouped) != list(range(1, 13)):
        raise AssertionError("reader must contain line ranks 1..12")

    target_word_checks = {
        "ol": ("und", "mit", "von", "aus", "relation"),
        "ckhy": ("misch",),
        "pcheey": ("zubereitungs", "form-ii"),
        "ols": ("maß", "produkt", "portion", "zubereitung"),
        "otar": ("weiter", "dann", "anschließend", "folge"),
    }
    banned_generic = (
        "arbeitsgut",
        "arbeitsschritt",
        "arbeitsgegenstand",
        "work item",
    )
    output: list[dict[str, object]] = []
    target_counts: defaultdict[str, int] = defaultdict(int)

    for rank in sorted(grouped):
        rows = sorted(grouped[rank], key=lambda row: int(row["ordinal"]))
        locus = rows[0]["locus"]
        if any(row["locus"] != locus for row in rows):
            raise AssertionError(f"mixed loci in reader rank {rank}")
        if locus not in context.by_line:
            raise AssertionError(f"reader locus absent from cache: {locus}")
        line = context.by_line[locus]
        if [int(row["ordinal"]) for row in rows] != list(range(1, len(line) + 1)):
            raise AssertionError(f"non-contiguous ordinals: {locus}")
        if [row["surface"] for row in rows] != [
            str(token["eva"]) for token in line
        ]:
            raise AssertionError(f"reader surfaces differ from cache: {locus}")
        if len({row["line_working_reader_de"] for row in rows}) != 1:
            raise AssertionError(f"multiple line readers: {locus}")
        if len({row["line_finding_de"] for row in rows}) != 1:
            raise AssertionError(f"multiple line findings: {locus}")
        full_reader = rows[0]["line_working_reader_de"]
        if any(term in full_reader.lower() for term in banned_generic):
            raise AssertionError(f"generic filler prose: {locus}")
        written = " ".join(str(token["eva"]) for token in line)

        for row, token in zip(rows, line):
            ordinal = int(row["ordinal"])
            token_index = int(token["token_index"])
            actual_exact = int(bool(context.exact[(locus, token_index)]))
            if actual_exact != int(row["reader_exact"]):
                raise AssertionError(f"exactness mismatch: {locus}@{ordinal}")
            surface = row["surface"]
            target_flag = int(row["target_flag"])
            if target_flag != int(surface in core_atlas.TARGET_FORM_SET):
                raise AssertionError(f"target flag mismatch: {locus}@{ordinal}")
            decision: Mapping[str, object] = {}
            if target_flag:
                if not actual_exact:
                    raise AssertionError(f"nonexact target: {locus}@{ordinal}")
                target_counts[surface] += 1
                concrete = row["concrete_default_de"].lower()
                if not any(piece in concrete for piece in target_word_checks[surface]):
                    raise AssertionError(
                        f"target default outside current class: {locus}@{ordinal}"
                    )
                decision = dictionary_by_surface[surface]

            output.append(
                {
                    "line_rank": rank,
                    "locus": locus,
                    "line_class": row["line_class"],
                    "ordinal": ordinal,
                    "surface": surface,
                    "reader_exact": actual_exact,
                    "portable_de": row["portable_de"],
                    "concrete_default_de": row["concrete_default_de"],
                    "primary_rival_de": row["primary_rival_de"],
                    "secondary_rival_de": row["secondary_rival_de"],
                    "evidence_source": row["evidence_source"],
                    "evidence_de": row["evidence_de"],
                    "counterevidence_de": row["counterevidence_de"],
                    "confidence": row["confidence"],
                    "target_flag": target_flag,
                    "replaceable": int(row["replaceable"]),
                    "written_line_eva": written,
                    "line_working_reader_de": full_reader,
                    "line_finding_de": row["line_finding_de"],
                    "dictionary_selected_role": decision.get(
                        "selected_role_model", "NOT_TARGET"
                    ),
                    "dictionary_working_default_de": decision.get(
                        "working_default_de", "NOT_TARGET"
                    ),
                    "dictionary_working_confidence": decision.get(
                        "working_confidence", "NOT_TARGET"
                    ),
                    "default_is_translation": 0,
                    "confirmed_lexeme": 0,
                    "confirmed_plaintext": 0,
                    "component_export_credit": 0,
                }
            )

    expected = {"ol": 2, "ckhy": 2, "pcheey": 3, "ols": 2, "otar": 3}
    if dict(target_counts) != expected:
        raise AssertionError(f"reader target coverage mismatch: {dict(target_counts)}")
    if len(output) != 109:
        raise AssertionError(f"reader must contain 109 tokens, got {len(output)}")
    if sum(int(row["reader_exact"]) for row in output) != 106:
        raise AssertionError("reader must preserve 106 exact and 3 nonexact tokens")
    return output


def markdown_table(
    headers: Sequence[str], rows: Sequence[Sequence[object]]
) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    output.extend(
        "| "
        + " | ".join(str(value).replace("|", "/") for value in row)
        + " |"
        for row in rows
    )
    return output


def build_human_reader(
    dictionary: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    identities: Sequence[Mapping[str, object]],
    reader: Sequence[Mapping[str, object]],
    historical_sources: Sequence[Mapping[str, str]],
    historical_relators: Sequence[Mapping[str, str]],
) -> str:
    lines = [
        "# GDT769 — Rollen-, Identitäts- und konkreter Arbeitsreader",
        "",
        "Dies ist die derzeit beste **ersetzbare Arbeitslesung**, keine bestätigte",
        "Entzifferung. Strukturrolle, deutsches Arbeitswort und historischer",
        "Vergleich bleiben getrennt. Kein EVA-Teilstring erhält einen lateinischen",
        "Buchstaben-, Laut- oder Morphemwert.",
        "",
        "## Fünf Zielwörter",
        "",
    ]
    lines.extend(
        markdown_table(
            (
                "EVA-Ganzwort",
                "gewählte Rolle",
                "Arbeitsdefault",
                "Confidence",
                "Auswahlbasis",
                "stärkster Rivale",
            ),
            [
                (
                    f"`{row['surface']}`",
                    row["selected_role_model"],
                    row["working_default_de"],
                    row["working_confidence"],
                    row["role_selection_basis"],
                    row["primary_rival_de"],
                )
                for row in dictionary
            ],
        )
    )
    lines.extend(
        [
            "",
            "`ol` und `otar` werden vorläufig als mitlaufende Feldzeichen",
            "gelesen. `ckhy` erhält in passenden Endlagen „mischen“, obwohl die",
            "globale Rolle gegen das Nomen „Mischung“ offen bleibt. `pcheey` ist",
            "kein belegtes Trockenwort; `ols` ist weder automatisch flüssig noch",
            "ein Filtrat.",
            "",
            "## Vollständige Zeilen",
            "",
        ]
    )
    grouped: defaultdict[int, list[Mapping[str, object]]] = defaultdict(list)
    for row in reader:
        grouped[int(row["line_rank"])].append(row)
    for rank in sorted(grouped):
        rows = sorted(grouped[rank], key=lambda row: int(row["ordinal"]))
        lines.extend(
            [
                f"### {rank}. `{rows[0]['locus']}` — {rows[0]['line_class']}",
                "",
                f"EVA: `{rows[0]['written_line_eva']}`",
                "",
                f"Arbeitslesung: **{rows[0]['line_working_reader_de']}**",
                "",
                f"Befund: {rows[0]['line_finding_de']}",
                "",
                "Tokenfolge: "
                + " · ".join(
                    f"`{row['surface']}`={row['concrete_default_de']} "
                    f"[{row['confidence']}]"
                    for row in rows
                ),
                "",
            ]
        )

    selected_roles = sum(int(row["role_selected"]) for row in roles)
    selected_identities = sum(int(row["identity_selected"]) for row in identities)
    lines.extend(
        [
            "## Entscheidungsbild",
            "",
            f"Gewählte Rollen: {selected_roles}; gewählte Identitätsdefaults: "
            f"{selected_identities}. Offene C0-Defaults bleiben im Wörterbuch",
            "sichtbar und werden nicht zu bestätigten Lexemen hochgestuft.",
            "",
            "## Historischer Architekturvergleich",
            "",
            f"Das Quellenregister enthält {len(historical_sources)} Einträge. "
            "Sie liefern nur erwartbare Rezeptarchitektur und Kandidatenklassen.",
        ]
    )
    if historical_relators:
        lines.append(
            f"Der gezielte Relatorvergleich ergänzt {len(historical_relators)} "
            "periodennahe Muster für Mengenrelation, finales Mischen und Schrittfolge."
        )
    lines.extend(
        [
            "",
            "## Behauptungsgrenze",
            "",
            "Bestätigte Lexeme: **0**. Bestätigte Klartextklauseln: **0**. "
            "Produktive Komponenten oder EVA→Latein-Zuordnungen: **0**. "
            "Die Ausgabe ist konkret genug, um an weiteren zugelassenen Zeilen "
            "ersetzt oder verbessert zu werden, aber keine fertige Übersetzung.",
            "",
        ]
    )
    return "\n".join(lines)


def build_result(
    core: Mapping[str, object],
    dispatch: Mapping[str, object],
    reader: Sequence[Mapping[str, object]],
    historical_sources: Sequence[Mapping[str, str]],
    historical_relators: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    dictionary = dispatch["dictionary_decisions"]
    return {
        "experiment_id": "GDT769",
        "status": STATUS,
        "question": (
            "Do ol, ckhy, pcheey, ols and otar behave as substances, operations, "
            "products, bounded record fields, or relational sequence/field linkers, "
            "and which concrete replaceable defaults survive local conjunction and "
            "strongest-locus removal?"
        ),
        "scope": {
            "source": "already admitted GDT764 guarded cache only",
            "new_pages_opened": 0,
            "new_images_opened": 0,
            "new_transcriptions_opened": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "counts": {
            "raw_target_occurrences": len(core["raw_occurrences"]),
            "reader_exact_target_occurrences": len(core["occurrences"]),
            "target_forms": len(core_atlas.TARGET_FORMS),
            "support_loci": len(core["support_loci"]),
            "frame_specs": dispatch["metadata"]["frame_spec_count"],
            "frame_evaluations": len(dispatch["frame_evidence"]),
            "role_specs": dispatch["metadata"]["role_spec_count"],
            "role_evaluations": len(dispatch["role_scoreboard"]),
            "identity_specs": dispatch["metadata"]["identity_spec_count"],
            "identity_evaluations": len(dispatch["identity_scoreboard"]),
            "reader_lines": len({str(row["locus"]) for row in reader}),
            "reader_tokens": len(reader),
            "reader_exact_tokens": sum(int(row["reader_exact"]) for row in reader),
            "historical_source_rows": len(historical_sources),
            "historical_relator_rows": len(historical_relators),
        },
        "selected_working_defaults": {
            str(row["surface"]): {
                "role": row["selected_role_model"],
                "role_selection_basis": row["role_selection_basis"],
                "role_evidence_superiority": bool(row["role_evidence_superiority"]),
                "supported_role_rivals": row["supported_role_rivals"],
                "identity": row["selected_identity_id"],
                "reader": row["working_default_de"],
                "confidence": row["working_confidence"],
                "rival": row["primary_rival_de"],
                "role_identity_consistent": bool(row["identity_role_consistent"]),
            }
            for row in dictionary
        },
        "key_observations": {
            "ol_relational_amount_contacts": 9,
            "ol_relational_amount_pages": 8,
            "ckhy_line_final_occurrences": 6,
            "ckhy_line_initial_occurrences": 0,
            "pcheey_moist_context_occurrences": 3,
            "pcheey_dry_context_occurrences": 0,
            "ols_direct_value_contacts": 3,
            "ols_line_final_occurrences": 5,
            "otar_medial_occurrences": 105,
            "otar_exact_occurrences": 110,
        },
        "guards": {
            "union_ed2_verified": bool(dispatch["metadata"]["union_ed2_verified"]),
            "family_ed2_union_surface_count": dispatch["metadata"][
                "family_ed2_union_surface_count"
            ],
            "gdt754_source_composed_surface_count": dispatch["metadata"][
                "gdt754_source_composed_surface_count"
            ],
            "gdt737_explicit_quarantined_surface_count": dispatch["metadata"][
                "gdt737_explicit_quarantined_surface_count"
            ],
            "historical_predictions_create_voynich_evidence": 0,
            "eva_latin_identity_credit": 0,
            "substring_identity_export_credit": 0,
            "default_is_translation": 0,
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "component_exports": 0,
        },
        "result": (
            "ol and otar retain relational field/sequence roles as explicit "
            "specificity tiebreaks over supported nominal rivals; pcheey uniquely "
            "selects a bounded preparation/form field; ols keeps the bounded "
            "record/measure tiebreak but no specific identity; ckhy=mix remains "
            "the concrete contextual default while its global role stays open."
        ),
        "claim_ceiling": (
            "GDT769 may select replaceable complete-word roles and reader defaults "
            "for the five targets and render twelve admitted complete lines. It "
            "does not confirm a lexeme, plaintext, language, cipher, plant, liquid, "
            "disease, cure, character value, Latin correspondence, productive "
            "substring, unseen form, new page, image, transcription, f84, or f84r."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    target_specs = read_tsv(TARGET_SPECS)
    role_specs = read_tsv(ROLE_SPECS)
    frame_specs = read_tsv(FRAME_SPECS)
    identity_specs = read_tsv(IDENTITY_SPECS)
    historical_sources = read_tsv(HISTORICAL_SOURCES)
    historical_predictions = read_tsv(HISTORICAL_PREDICTIONS)
    historical_relators = (
        read_tsv(HISTORICAL_RELATORS) if HISTORICAL_RELATORS.is_file() else []
    )
    line_specs = read_tsv(LINE_SPECS)

    if len(target_specs) != 5 or len(role_specs) != 5 or len(frame_specs) != 16:
        raise AssertionError("GDT769 requires 5 targets, 5 roles and 16 frames")

    core = core_atlas.build_core_atlas(ROOT)
    dispatch = model_scoring.build_model_dispatch(
        core,
        role_specs,
        identity_specs,
        frame_specs,
        historical_predictions,
    )
    reader = build_reader(line_specs, dispatch["dictionary_decisions"])

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    tables = {
        "TARGET_640_RAW_OCCURRENCE_ATLAS.tsv": core["raw_occurrences"],
        "TARGET_526_EXACT_CONTEXT_ATLAS.tsv": core["occurrences"],
        "TARGET_5_CENSUS.tsv": core["target_census"],
        "TARGET_5_ROLE_GEOMETRY.tsv": core["role_geometry"],
        "SIGNATURE_5_SUMMARY.tsv": core["signature_summary"],
        "SUPPORT_52_LOCUS_ATLAS.tsv": core["support_loci"],
        "LEAVE_ONE_LOCUS_OUT.tsv": core["leave_one_locus_out"],
        "CONTROL_SPAN_ATLAS.tsv": flatten_controls(core["controls"]),
        "DONOR_BLOCK_REGISTRY.tsv": flatten_blocks(core["donor_blocks"]),
        "FRAME_16X5_EVIDENCE.tsv": dispatch["frame_evidence"],
        "FRAME_LOCUS_EVIDENCE.tsv": dispatch["frame_locus_evidence"],
        "ROLE_5X5_SCOREBOARD.tsv": dispatch["role_scoreboard"],
        "IDENTITY_CANDIDATE_SCOREBOARD.tsv": dispatch["identity_scoreboard"],
        "GDT769_5_WORKING_DICTIONARY.tsv": dispatch["dictionary_decisions"],
        "TWELVE_COMPLETE_LINE_READER.tsv": reader,
    }
    for name, rows in tables.items():
        write_tsv(out / name, tabularise(rows))

    human = build_human_reader(
        dispatch["dictionary_decisions"],
        dispatch["role_scoreboard"],
        dispatch["identity_scoreboard"],
        reader,
        historical_sources,
        historical_relators,
    )
    (out / "HISTORICAL_ROLE_IDENTITY_READER.md").write_text(
        human, encoding="utf-8"
    )
    result = build_result(
        core, dispatch, reader, historical_sources, historical_relators
    )
    write_json(out / "RESULT.json", result)

    missing = [name for name in OUTPUT_NAMES if not (out / name).is_file()]
    if missing:
        raise AssertionError(f"missing declared outputs: {missing}")
    if not args.quiet:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
