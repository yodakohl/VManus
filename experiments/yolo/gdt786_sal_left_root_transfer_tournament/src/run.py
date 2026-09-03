#!/usr/bin/env python3
"""Build GDT786's guarded ``sal...`` left-root transfer tournament."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt786_sal_left_root_transfer_tournament"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
TARGET_SPECS = SRC / "TARGET_12_SPECS.tsv"
PASSAGE_SPECS = SRC / "PASSAGE_14_SPECS.tsv"
MODEL_SPECS = SRC / "MODEL_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_ROLE_SPECS.tsv"
GEOMETRY = SRC / "geometry.py"
QUALITATIVE = SRC / "qualitative.py"
REMAINDER_EVIDENCE = SRC / "remainder_evidence.py"
G785_DICTIONARY = ROOT / "experiments/yolo/gdt785_sal_exact_whole_field_census/artifacts/GDT785_2_WORKING_DICTIONARY.tsv"
G735_HISTORICAL = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv"

STATUS = (
    "PARTIAL__12_SAL_PREFIX_WHOLES__14_EXACT_OCCURRENCES__10_PRIMARY_TYPES__"
    "ADDITIVE_05551_VS_SAME_X_05591__5_OF10_P0444__"
    "SAL_ROOT_TOP1_2_TOP2_5_OF10__CONTROL_ROOTS_TOP1_17_TOP2_27_OF29__"
    "SALO_RANK51_SALY_RANK49_OF55__ZERO_EXACT_FORWARD_SPLITS__"
    "ZERO_STOLFI_SAL_X_BOUNDARIES__FORMAL_FAMILY_ONLY__"
    "12_CONCRETE_WHOLE_DEFAULTS__ZERO_COMPONENT_EXPORT"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _text_value(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.12f}"
    return value


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path.name}")
    fields: list[str] = []
    for row in rows:
        fields.extend(field for field in row if field not in fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _text_value(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if len(rows) != 18:
        raise AssertionError(f"expected 18 source locks, got {len(rows)}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        source = ROOT / relative
        if not source.is_file() or sha256(source) != row["expected_sha256"]:
            raise AssertionError(f"source changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def zero_ceiling(row: dict[str, object]) -> dict[str, object]:
    row.update({
        "default_is_translation": 0, "confirmed_lexeme": 0,
        "confirmed_plaintext": 0, "specific_substance_confirmed": 0,
        "component_export_credit": 0,
    })
    return row


def build_target_atlas(geometry, qualitative, target_specs) -> list[dict[str, object]]:
    specs = {row["surface"]: row for row in target_specs}
    qrows = {(row["locus"], row["surface"]): row for row in qualitative["occurrence_rows"]}
    output = []
    for number, item in enumerate(geometry["targets"], 1):
        row = dict(item)
        key = (row["locus"], row["surface"])
        if key not in qrows or row["surface"] not in specs:
            raise AssertionError(f"unmatched target row: {key}")
        qrow, card = qrows[key], specs[row["surface"]]
        output.append(zero_ceiling({
            "occurrence_id": f"G786-O{number:03d}", **row,
            "written_line_eva": qrow["written_line_eva"],
            "target_ordinal": qrow["target_ordinal"], "reader_exact_target": 1,
            "preferred_mechanism": card["preferred_mechanism"],
            "practical_default_de": card["practical_default_de"],
            "working_confidence": card["working_confidence"],
        }))
    if len(output) != 14 or len({row["surface"] for row in output}) != 12:
        raise AssertionError("expected 14 occurrences / 12 complete target forms")
    return output


def build_model_summary(geometry, model_specs) -> list[dict[str, object]]:
    summary = geometry["primary_model_summary"]
    keys = {
        "M01": "additive", "M02": "root_only", "M03": "remainder_only",
        "M04": "family_loto", "M05": "whole_backoff", "M06": "same_x_null",
        "M07": "len_freq_null",
    }
    output = []
    for spec in model_specs:
        row: dict[str, object] = dict(spec)
        model_id = spec["model_id"]
        key = keys.get(model_id, "additive")
        row.update({
            "macro_distance": summary[f"{key}_macro_distance"],
            "macro_similarity": summary[f"{key}_macro_similarity"],
            "formally_scored": int(model_id in keys),
            "decision": (
                "NUMERIC_LEAD_NOT_ROBUST__NO_PORTABLE_TRANSFER" if model_id == "M01" else
                "SAME_FORMAL_FIT_AS_M01__ZERO_EXCLUSIVE_SALT_SIGNAL" if model_id == "M08" else
                "FORMAL_STRING_FAMILY_RETAINED" if model_id == "M04" else "COMPARATOR"
            ),
            "selected_portable_model": 0, "score_is_probability": 0,
        })
        output.append(zero_ceiling(row))
    if len(output) != 8:
        raise AssertionError("expected eight fixed mechanisms")
    return output


def build_dictionary(targets, target_specs) -> list[dict[str, object]]:
    exact_counts = Counter(row["surface"] for row in targets)
    output = []
    for spec in target_specs:
        surface = spec["surface"]
        output.append(zero_ceiling({
            "entry": surface, "remainder": spec["remainder"],
            "preferred_working_default_de": spec["practical_default_de"],
            "drug_composite_rival_de": spec["drug_composite_de"],
            "learned_whole_rival_de": spec["learned_whole_rival_de"],
            "salt_rival_de": spec["salt_rival_de"],
            "preferred_mechanism": spec["preferred_mechanism"],
            "independent_remainder_role": spec["independent_remainder_role"],
            "surface_confidence": "C2_OBSERVED_COMPLETE_WHOLE",
            "working_confidence": spec["working_confidence"],
            "reader_exact_occurrences": exact_counts[surface],
            "positive_evidence_de": spec["positive_evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "scope": f"OBSERVED_COMPLETE_WHOLE_{surface.upper()}_ONLY",
            "replaceable": 1, "portable_sal_root_used": 0,
            "portable_remainder_used": 0,
        }))
    if len(output) != 12 or sum(int(row["reader_exact_occurrences"]) for row in output) != 14:
        raise AssertionError("dictionary shape changed")
    return output


def build_passages(atlas, passage_specs) -> list[dict[str, object]]:
    lookup = {(row["locus"], row["surface"]): row for row in atlas}
    output = []
    for spec in passage_specs:
        row = lookup[(spec["locus"], spec["surface"])]
        words = str(row["written_line_eva"]).split()
        ordinal = int(spec["target_ordinal"])
        if words[ordinal - 1] != spec["surface"]:
            raise AssertionError(f"passage ordinal changed: {spec['passage_id']}")
        words[ordinal - 1] = f"⟦{spec['surface']} = {spec['focus_display_de']}⟧"
        output.append(zero_ceiling({
            **spec, "page": row["page"], "physical_folio": row["physical_folio"],
            "written_line_eva": row["written_line_eva"],
            "target_focused_line": " · ".join(words),
            "render_status": "CONCRETE_REPLACEABLE_WHOLE_DEFAULT_NOT_PLAINTEXT",
            "portable_component_used": 0,
        }))
    if len(output) != 14:
        raise AssertionError("expected fourteen practical passages")
    return output


def build_historical() -> list[dict[str, object]]:
    observations = {row["observation_id"] for row in read_tsv(G735_HISTORICAL)}
    output = []
    for spec in read_tsv(HISTORICAL_SPECS):
        if not set(spec["source_observations"].split("|")) <= observations:
            raise AssertionError(f"missing historical provenance: {spec['comparator_id']}")
        if spec["voynich_identity_credit"] != "0" or spec["spelling_credit"] != "0":
            raise AssertionError("historical comparator exceeds ceiling")
        output.append(zero_ceiling({**spec, "allowed_use": "RECORD_ARCHITECTURE_ONLY", "selects_voynich_mechanism": 0}))
    if len(output) != 4:
        raise AssertionError("expected four historical comparators")
    return output


def build_remainder_rows(remainder) -> list[dict[str, object]]:
    output = []
    for record in remainder["records"]:
        row = dict(record)
        reports, retired, rivals = row.pop("evidence_report_ids"), row.pop("retired_interpretations"), row.pop("rivals_de")
        row.update({
            "evidence_report_ids": "|".join(reports),
            "retired_interpretations": " || ".join(retired),
            "rival_1_de": rivals[0], "rival_2_de": rivals[1],
            "compositional_candidate": int(row["compositional_candidate"]),
            "rank_is_probability": 0, "portable_remainder_export": 0,
        })
        output.append(zero_ceiling(row))
    if len(output) != 12:
        raise AssertionError("expected twelve remainder evidence rows")
    return output


def build_chorcholsal_correction() -> list[dict[str, object]]:
    parent = {row["entry"]: row for row in read_tsv(G785_DICTIONARY)}
    if parent["chorcholsal"]["preferred_working_default_de"] != "trockene Blütendroge":
        raise AssertionError("GDT785 chorcholsal display changed")
    return [zero_ceiling({
        "surface": "chorcholsal", "gdt785_default_de": "trockene Blütendroge",
        "gdt786_default_de": "trockene Blütendroge", "display_changed": 0,
        "written_boundary": "C2_COMPLETE_WHOLE",
        "gdt785_internal_sal_status": "C0_NONEXPORTING_SUFFIX_ECHO",
        "gdt786_internal_sal_status": "C0_GLOSS_MEMORY_ONLY__NOT_SEMANTIC_EVIDENCE",
        "gdt786_internal_read_de": "PART+DRY-Echo; Drogenklasse bleibt Ganzwortdefault",
        "reason": "Left-root transfer is not licensed; suffix use was already morphologically weak.",
        "scope": "UNCHANGED_OBSERVED_COMPLETE_WHOLE_ONLY", "replaceable": 1,
    })]


def artifact_readme() -> str:
    return """# GDT786 artifacts

- target atlas, 29 same-remainder controls, ten primary model cells, eight model summaries and eleven sensitivity runs;
- 39 root-recognition cells, two repeat-coherence rows, twelve split audits, two reverse contacts and fourteen Stolfi checks;
- twelve independent remainder evidence cards, twelve working whole cards, fourteen focused passages and four historical comparators;
- one `chorcholsal` provenance correction plus machine-readable result and validation.

The formal `sal...` family remains useful. Nothing here licenses `sal` or a
remainder as a free component, identifies a specific substance, or confirms
plaintext.
"""


def build_report(result, dictionary, passages, sensitivity, split_rows, stolfi_rows) -> str:
    primary, recognition = result["primary_geometry"], result["root_recognition"]
    repeats = result["repeat_coherence"]
    dictionary_table = "\n".join(
        f"| `{r['entry']}` | {r['preferred_working_default_de']} | {r['preferred_mechanism']} | {r['working_confidence']} | {r['reader_exact_occurrences']} |"
        for r in dictionary
    )
    passage_table = "\n".join(
        f"| {r['locus']} | `{r['surface']}` | {r['focus_display_de']} | {r['historical_preference']} |" for r in passages
    )
    sensitivity_table = "\n".join(
        f"| {r['sensitivity']} | {float(r['additive_macro_distance']):.4f} | {float(r['same_x_null_macro_distance']):.4f} | {float(r['additive_advantage_over_same_x_null']):+.4f} | {r['additive_wins_over_same_x_null']}/{r['types']} |"
        for r in sensitivity
    )
    repeat_table = "\n".join(
        f"| `{r['surface']}` | {float(r['pair_distance']):.4f} | {r['ascending_distance_rank']}/{r['pool_size']} |" for r in repeats
    )
    split_total = sum(int(r["reader_exact_pair_occurrences"]) for r in split_rows)
    stolfi_splits = sum(int(r["same_locus_sal_x_count"]) for r in stolfi_rows)
    return f"""# GDT786 — `sal...`: a real family, but not yet a semantic root

Status: `{result['status']}`

## Working result

All twelve observed complete `sal...` forms now have a short, concrete working
default. The correction is about **how** those cards may be used: `sal = Droge`
remains the standalone GDT785 whole-card, but GDT786 does not license “Droge”
as a mechanical prefix in another word. Longer forms are learned complete
wholes by default. `saldal`, `salkeedy` and `saltar` retain form-specific
composite readings because their own fields support them; no component exports.

Productive `sal-` is not deleted: it remains a low-priority C0 hypothesis. It
just stops driving the live renderer until it predicts something that a
whole-word model does not.

## Transfer tournament

Ten remainder types, twelve occurrences and 29 same-remainder control types
enter the primary comparison. Smaller distance is better. The additive model
scores **{float(primary['additive_macro_distance']):.4f}** against
**{float(primary['same_x_null_macro_distance']):.4f}** for matched `R+X`: only
**{float(primary['additive_advantage_over_same_x_null']):.4f}** advantage,
**{primary['additive_wins_over_same_x_null']}/10** wins and exact sign-flip
**p={float(primary['additive_vs_same_x_null_exact_sign_flip_p']):.4f}**.

The inverse test is clearer. Correct-root recovery is rank 1 for only
**{recognition['sal']['top_1']}/10** `sal` cells and top 2 for
**{recognition['sal']['top_2']}/10**. Matched non-`sal` roots achieve
**{recognition['controls']['top_1']}/29** and
**{recognition['controls']['top_2']}/29**. The deck can recognize many real
root-conditioned fields, but it does not reliably recognize `sal`.

| sensitivity | additive | same-X | advantage | wins |
|---|---:|---:|---:|---:|
{sensitivity_table}

The sign reverses with 17 roots, without singleton occurrences, and without
the large `cho` control. The geometry is exploratory: only ten types, eight
singleton types, coarse bins, an analyst-chosen 14:4 flank weighting, and no
neighbor semantics. It tests distribution, never the meaning “Droge.”

The earlier 61-bin Brier sketch is not contradictory: SAL-only (.081304) and
FAMILY (.083586) already beat ADD (.084619); only remainder-only (.103954) was
clearly worse. One-hot shared-zero credit and lack of a type-balanced same-X
null made that sketch look more additive than it was.

## Repetition and boundaries

| whole | pair distance | coherence rank |
|---|---:|---:|
{repeat_table}

`salo` ranks 51/55 and `saly` 49/55 among equally long, equally frequent pairs:
their two contexts are unusually unlike. There are **{split_total} reader-exact
`sal X`** sequences. One raw `sal ol` exists, but readers do not agree on it.
Of seven same-locus Stolfi readings, **{stolfi_splits}** split at `sal|X`; six
preserve the whole, and the exception is `s,alal`, not `sal,al`. Two exact
reverse contacts (`keedy sal`, `al sal`) do not establish forward composition.

## Concrete complete-whole cards

| EVA whole | working default | mechanism | confidence | n |
|---|---|---|---|---:|
{dictionary_table}

The cards are deliberately short. `saldam` is simply **Pflanzendroge**; the
older Blatt/Wurzel association belongs in local evidence, not in its dictionary
definition. `salf` is **Drogenname**, not a fictional operation.

## Fourteen context checks

| locus | target | focused display | historical preference |
|---|---|---|---|
{passage_table}

The historical reading prefers a learned whole at eight positions, a
form-specific drug composite at three, and leaves three tied. A salt composite
wins zero. Medieval pharmacy certainly used salts, but these fields supply no
exclusive salt signal; visual similarity of EVA `sal` to Latin *sal* scores zero.

## `chorcholsal` and next move

The practical whole display remains **`chorcholsal = trockene Blütendroge`**.
The final `sal` string is no longer counted as independent evidence for
“Droge”; the card survives as a replaceable learned whole with the older
PART+DRY echo.

Historical comparators still favor learned drug names mixed with compact
part/form/quality/degree fields. The next move reverses the test: follow the
best independently supported remainders—first `keedy`, then `dal`, `ar` and
`ol`—across different left families. A stable remainder effect could create
real concrete composition without assuming `sal`.

Confirmed lexemes, plaintext clauses, specific substances and component
exports remain zero. No new page, image, OCR or transcription was opened;
f84/f84r stayed sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt786_sal_left_root_transfer_tournament/src/run.py
python3 -B experiments/yolo/gdt786_sal_left_root_transfer_tournament/src/validate.py
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()
    lock_count, lock_hash = verify_locks()

    geometry = load_module("gdt786_geometry", GEOMETRY).compute()
    qualitative = load_module("gdt786_qualitative", QUALITATIVE).compute(ROOT)
    remainder = load_module("gdt786_remainder", REMAINDER_EVIDENCE).compute(ROOT)
    target_specs, passage_specs, model_specs = read_tsv(TARGET_SPECS), read_tsv(PASSAGE_SPECS), read_tsv(MODEL_SPECS)
    if (len(target_specs), len(passage_specs), len(model_specs)) != (12, 14, 8):
        raise AssertionError("registered specification shape changed")

    targets = build_target_atlas(geometry, qualitative, target_specs)
    model_summary = build_model_summary(geometry, model_specs)
    dictionary = build_dictionary(targets, target_specs)
    passages = build_passages(targets, passage_specs)
    historical = build_historical()
    remainder_rows = build_remainder_rows(remainder)
    chorcholsal = build_chorcholsal_correction()
    repeats = [
        {**row, "pool_median_pair_distance": geometry["repeat_coherence"]["pool_median_pair_distance"], "lower_distance_is_more_coherent": 1}
        for row in geometry["repeat_coherence"]["targets"]
    ]
    primary_rows = []
    for source in geometry["primary_model_rows"]:
        row = dict(source)
        row.setdefault("exact_whole_distance", "NA")
        row.setdefault("exact_whole_similarity", "NA")
        primary_rows.append(row)
    reverse_rows = [
        {"contact_id": f"G786-R{number:02d}", "locus": value.split(":", 1)[0], "written_pair": f"{value.split(':', 1)[1]} sal", "direction": "REMAINDER_THEN_SAL", "component_export_credit": 0}
        for number, value in enumerate(geometry["split_diagnostic"]["reverse_loci"], 1)
    ]
    outputs = {
        "GDT786_14_TARGET_OCCURRENCE_ATLAS.tsv": targets,
        "GDT786_29_SAME_REMAINDER_CONTROL_TYPES.tsv": geometry["same_x_controls"],
        "GDT786_10_PRIMARY_MODEL_SCORECARD.tsv": primary_rows,
        "GDT786_8_MODEL_SUMMARY.tsv": model_summary,
        "GDT786_11_SENSITIVITY_SCORECARD.tsv": geometry["sensitivity_summaries"],
        "GDT786_39_ROOT_RECOGNITION.tsv": geometry["root_recognition_rows"],
        "GDT786_2_REPEAT_COHERENCE.tsv": repeats,
        "GDT786_12_SPLIT_BOUNDARY_AUDIT.tsv": qualitative["split_rows"],
        "GDT786_2_REVERSE_EXACT_CONTACTS.tsv": reverse_rows,
        "GDT786_STOLFI_BOUNDARY_ATLAS.tsv": qualitative["stolfi_rows"],
        "GDT786_12_REMAINDER_EVIDENCE.tsv": remainder_rows,
        "GDT786_12_WORKING_DICTIONARY.tsv": dictionary,
        "GDT786_14_PRACTICAL_PASSAGES.tsv": passages,
        "GDT786_4_HISTORICAL_COMPARATORS.tsv": historical,
        "GDT786_1_CHORCHOLSAL_CORRECTION.tsv": chorcholsal,
    }
    for name, rows in outputs.items():
        write_tsv(artifacts / name, rows)

    preferences = Counter(row["historical_preference"] for row in passage_specs)
    result = {
        "experiment_id": "GDT786", "status": STATUS,
        "source_locks": lock_count, "source_lock_sha256": lock_hash,
        "source_spec_sha256": {
            "targets": sha256(TARGET_SPECS), "passages": sha256(PASSAGE_SPECS),
            "models": sha256(MODEL_SPECS), "historical": sha256(HISTORICAL_SPECS),
        },
        "inherited_guard": geometry["guard"],
        "target": {
            "complete_forms": 12, "reader_exact_occurrences": 14,
            "primary_forms": 10, "primary_occurrences": 12,
            "page_labels": len({row["page"] for row in targets}),
            "physical_folios": len({row["physical_folio"] for row in targets}),
        },
        "primary_geometry": geometry["primary_model_summary"],
        "root_recognition": geometry["root_recognition_summary"],
        "repeat_coherence": repeats, "boundary": qualitative["summary"],
        "green_gates": geometry["green_gates"],
        "historical_preferences": dict(preferences),
        "adjudication": {
            "productive_sal_left_root": "C0_RETAINED_INACTIVE_HYPOTHESIS",
            "formal_sal_left_family": "C1_RETAINED",
            "standalone_sal_default_de": "Droge", "standalone_sal_card_changed": False,
            "default_long_form_mechanism": "LEARNED_COMPLETE_WHOLE",
            "form_specific_composite_leads": ["saldal", "salkeedy", "saltar"],
            "additional_composite_rivals": ["salal", "salar", "salol"],
            "salt_preferred_contexts": 0, "portable_component_exports": 0,
            "recommendation": geometry["recommendation"],
        },
        "chorcholsal": {"display": "trockene Blütendroge", "display_changed": False, "internal_sal_evidence": "REMOVED_FROM_ACTIVE_JUSTIFICATION"},
        "relation_packet": "NOT_APPLICABLE__COMPLETE_WORD_GEOMETRY_AND_BOUNDARY_CENSUS_ONLY",
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "specific_substances": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0,
        "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "C2 observed complete-word boundaries; C1 formal sal-initial family and standalone sal nominal role; C1 at most form-specific whole roles; C0 replaceable German displays; zero plaintext, substance identity, EVA value or free component.",
    }
    write_json(artifacts / "RESULT.json", result)
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    report_path.write_text(build_report(result, dictionary, passages, geometry["sensitivity_summaries"], qualitative["split_rows"], qualitative["stolfi_rows"]), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
