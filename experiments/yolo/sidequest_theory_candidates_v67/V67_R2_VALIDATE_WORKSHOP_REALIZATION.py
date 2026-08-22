#!/usr/bin/env python3
"""Validate the compact V67 R2 historical workshop realization."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
QUERY = ROOT / "vmanus-exp"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_rows(path: Path, allows: list[str], columns: list[str]) -> list[dict[str, str]]:
    command = [
        str(QUERY),
        "query-tsv",
        str(path),
        "--selector",
        "page",
    ]
    for allowed in allows:
        command.extend(["--allow", allowed])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    material = "\n".join(
        line for line in result.stdout.splitlines() if not line.startswith("GUARD_STATS ")
    )
    return list(csv.DictReader(io.StringIO(material), delimiter="\t"))


def expand_serials(spec: str) -> list[int]:
    if spec == "ASTRO_LOCAL":
        return []
    values: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            values.extend(range(start, end + 1))
        else:
            values.append(int(part))
    return values


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    competition = read_tsv(HERE / "V67_R2_SOURCE_ORDER_AND_MODEL_COMPETITION.tsv")
    manual = read_tsv(HERE / "V67_R2_WORKSHOP_MANUAL.tsv")
    traces = read_tsv(HERE / "V67_R2_FULL_TRACES.tsv")
    sources = read_tsv(HERE / "V67_R2_HISTORICAL_COMPARATORS.tsv")
    report = (HERE / "V67_R2_HISTORICAL_WORKSHOP_REALIZATION_REPORT.md").read_text(
        encoding="utf-8"
    )
    for dataset_name, dataset in (
        ("competition", competition),
        ("manual", manual),
        ("traces", traces),
        ("sources", sources),
    ):
        require(
            all(None not in row and all(value is not None for value in row.values()) for row in dataset),
            f"malformed TSV row in {dataset_name}",
        )

    pure_models = {"LATIN_FORMULARY", "VERNACULAR_IMPERATIVE", "PURE_TABULAR_NOTATION"}
    registers = {"HERBAL", "BIOLOGICAL", "ASTRO"}
    observed_pairs = {(row["model"], row["register"]) for row in competition}
    require(
        {(model, register) for model in pure_models for register in registers}
        <= observed_pairs,
        "model competition must contain all three source styles in all three registers",
    )
    selected = [row for row in competition if row["disposition"] == "SELECTED"]
    require(
        len(selected) == 1 and selected[0]["model"] == "HYBRID_TWO_STAGE",
        "HYBRID_TWO_STAGE must be the sole selected model",
    )

    required_phases = {"CODEBOOK", "GENEALOGY", "COMPILER", "TRAINING", "HANDOFF", "PROOF"}
    phase_counts = Counter(row["phase"] for row in manual)
    require(required_phases <= set(phase_counts), "workshop manual lacks a required phase")
    require(len(manual) == 30, "workshop manual must contain 30 compact steps")
    require(
        all(row["hard_rule"] and row["failure_if_violated"] for row in manual),
        "every manual step needs a hard rule and failure mode",
    )

    source_ids = {row["source_id"] for row in sources}
    require(len(sources) >= 8, "at least eight genuine historical comparators required")
    require(all(row["reference_url"].startswith("https://") for row in sources), "source URL missing")
    for row in manual:
        used_ids = {item for item in row["historical_basis_ids"].split("|") if item}
        require(used_ids <= source_ids, f"unknown historical source ID in {row['manual_step']}")

    expected_trace_ids = {
        "T-H4-01",
        "T-H4-02",
        "T-H4-03",
        "T-H4-04",
        "T-B2-01",
        "T-B2-02",
        "T-B2-03",
        "T-B2-04",
        "T-B2-05",
        "T-B2-06",
        "T-A1",
        "T-A2",
        "T-A3",
    }
    require({row["trace_id"] for row in traces} == expected_trace_ids, "trace set mismatch")
    require(len(traces) == 13, "expected 13 compact full-trace rows")
    require(
        all(
            row["semantic_contract"]
            == "NO_PHONETIC_MAPPING;NO_NEW_CARD_MEANING;LOCAL_EXPANSION_ONLY"
            for row in traces
        ),
        "semantic contract mismatch",
    )

    allowed_short = {
        "NONE",
        "NONE_ASTRO_LOCAL_EXEMPLAR_ONLY",
        "FORMAL_STANDARD_SET",
        "FORMAL_TARGET_SET",
        "FORMAL_LINK",
        "FORMAL_PRESCRIBED_PARAMETER",
        "MASS?",
        "ANWENDEN?",
        "BEREIT?",
        "ANSATZ?",
        "ZIEL?",
        "KLAR?",
        "VORIGES?",
        "ANTEIL?",
        "TEMPERIEREN?",
        "SPÜLEN?",
        "ABLASSEN?",
    }
    for row in traces:
        tokens = set(row["licensed_short_layer"].split("|"))
        require(tokens <= allowed_short, f"unlicensed short value in {row['trace_id']}: {tokens}")

    herbal_input = ROOT / "experiments/yolo/sidequest_theory_candidates_v64/V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv"
    bio_input = ROOT / "experiments/yolo/sidequest_theory_candidates_v65/V65_R2_281_EVENT_BIO_INTERLINEAR.tsv"
    astro_input = ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv"

    herbal_all = guarded_rows(
        herbal_input,
        ["f10r", "f11r", "f55v", "f56r"],
        ["page", "event_serial", "record_unit_id", "surface_display_only"],
    )
    bio_all = guarded_rows(
        bio_input,
        ["f81v", "f82r", "f83r"],
        ["page", "event_serial", "record_unit_id", "surface_display_only"],
    )
    astro_all = guarded_rows(
        astro_input,
        ["f67r2", "f68r1", "f69v"],
        ["page", "group_serial", "locus", "surface_ZL3b"],
    )

    require(len(herbal_all) == 100, "V64 Herbal coverage must remain 100 events")
    require(len({row["record_unit_id"] for row in herbal_all}) == 5, "Herbal record count must be 5")
    require(len(bio_all) == 281, "V65 Bio coverage must remain 281 events")
    require(len({row["record_unit_id"] for row in bio_all}) == 6, "Bio record count must be 6")
    require(len(herbal_all) + len(bio_all) == 381, "prose total must be 381 events")
    require(len(astro_all) == 395, "V66 Astro coverage must remain 395 groups")
    require(len({(row["page"], row["locus"]) for row in astro_all}) == 142, "Astro locus count must be 142")
    astro_page_counts = Counter(row["page"] for row in astro_all)
    require(
        astro_page_counts == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        f"Astro page counts mismatch: {astro_page_counts}",
    )

    h4_rows = [row for row in herbal_all if row["record_unit_id"] == "H4"]
    b2_rows = [row for row in bio_all if row["record_unit_id"] == "B2"]
    h4_surface = {int(row["event_serial"]): row["surface_display_only"] for row in h4_rows}
    b2_surface = {int(row["event_serial"]): row["surface_display_only"] for row in b2_rows}

    for prefix, expected_range, surface_map in (
        ("T-H4", list(range(56, 74)), h4_surface),
        ("T-B2", list(range(167, 229)), b2_surface),
    ):
        subset = [row for row in traces if row["trace_id"].startswith(prefix)]
        observed: list[int] = []
        for row in subset:
            serials = expand_serials(row["event_serials"])
            require(len(serials) == int(row["event_count"]), f"event count mismatch in {row['trace_id']}")
            observed.extend(serials)
            expected_surface = " ".join(surface_map[serial] for serial in serials)
            require(
                row["visible_surface_sequence"] == expected_surface,
                f"surface sequence mismatch in {row['trace_id']}",
            )
        require(observed == expected_range, f"{prefix} trace must be complete, ordered and duplicate-free")

    astro_trace_counts = {
        row["trace_id"]: int(row["event_count"])
        for row in traces
        if row["register"] == "ASTRO"
    }
    require(astro_trace_counts == {"T-A1": 190, "T-A2": 65, "T-A3": 140}, "Astro trace counts mismatch")
    require(sum(astro_trace_counts.values()) == 395, "Astro trace total mismatch")
    require(
        all(row["visible_surface_sequence"] == "SEE_V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv" for row in traces if row["register"] == "ASTRO"),
        "Astro full-ledger reuse reference missing",
    )

    deck = [
        "MASS?",
        "ANWENDEN?",
        "BEREIT?",
        "ANSATZ?",
        "ZIEL?",
        "KLAR?",
        "VORIGES?",
        "ANTEIL?",
        "TEMPERIEREN?",
        "SPÜLEN?",
        "ABLASSEN?",
    ]
    require(all(label in report for label in deck), "report must retain all eleven V60 labels")
    normalized_report = " ".join(report.split())
    require("keine Lautzuweisung" in normalized_report, "no-phonetic disclaimer missing")
    require("A2 und A3 erhalten **keine** direkte Identität" in report, "f68/f69 non-identity missing")

    validation = {
        "status": "PASS",
        "selected_model": "HYBRID_TWO_STAGE",
        "competition_rows": len(competition),
        "manual_steps": len(manual),
        "manual_phase_counts": dict(sorted(phase_counts.items())),
        "historical_comparators": len(sources),
        "trace_rows": len(traces),
        "trace_coverage": {
            "H4_events": len(h4_surface),
            "B2_events": len(b2_surface),
            "A1_groups": astro_page_counts["f67r2"],
            "A2_groups": astro_page_counts["f68r1"],
            "A3_groups": astro_page_counts["f69v"],
        },
        "canonical_reuse": {
            "Herbal_records": 5,
            "Herbal_events": len(herbal_all),
            "Bio_records": 6,
            "Bio_events": len(bio_all),
            "Prose_events": len(herbal_all) + len(bio_all),
            "Astro_diagrams": len(astro_page_counts),
            "Astro_loci": len({(row["page"], row["locus"]) for row in astro_all}),
            "Astro_groups": len(astro_all),
        },
        "semantic_gates": {
            "phonetic_mapping": False,
            "new_card_meanings": False,
            "page_host_or_substring_semantics": False,
            "f68_f69_identity": False,
            "sealed_f84_used": False,
        },
    }
    output_path = HERE / "V67_R2_VALIDATION.json"
    output_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
