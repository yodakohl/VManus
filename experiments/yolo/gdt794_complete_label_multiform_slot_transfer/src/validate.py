#!/usr/bin/env python3
"""Validate GDT794, including two byte-identical builder replays."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt794_complete_label_multiform_slot_transfer"
SRC = BASE / "src"
ART = BASE / "artifacts"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
OUTPUT_NAMES = (
    "GDT794_216_ADMITTED_CIRCLE_LABEL_ATLAS.tsv",
    "GDT794_15_REPEATED_COMPLETE_LABEL_DEFAULTS.tsv",
    "GDT794_CROSS_FOLIO_LOFO_PREDICTIONS.tsv",
    "GDT794_4_COORDINATE_MODEL_SCORES.tsv",
    "GDT794_KLUGE_A_LABEL_GRID.tsv",
    "GDT794_30_KLUGE_HOMOLOG_SUMMARY.tsv",
    "GDT794_5_RAW_SLOT4_CORRECTION.tsv",
    "GDT794_RELATIONAL_PAIR_CAPACITY.tsv",
    "GDT794_CANDIDATE_ADJUDICATION.tsv",
    "GDT794_4_OTODY_POSITION_RIVAL.tsv",
    "GDT794_15_REPEATED_CROSS_SCOPE_DICTIONARY_AUDIT.tsv",
    "GDT794_216_CIRCLE_LABEL_SEQUENCE_OVERRIDES.tsv",
    "RESULT.json",
)
REQUIRED_LOCK_PATHS = {
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/METHOD.md",
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/PREREGISTRATION.md",
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/src/CANDIDATE_MODEL_SPECS.tsv",
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/src/run.py",
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/src/validate.py",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv",
    "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/artifacts/GDT793_5_OUTER_SLOT4_SERIES.tsv",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)


def main() -> int:
    audit = Audit()
    audit.check(LOCK.is_file(), "source lock exists")
    if LOCK.is_file():
        lock_rows = read_tsv(LOCK)
        audit.check({row["path"] for row in lock_rows} == REQUIRED_LOCK_PATHS, "source lock exact path set")
        audit.check(len({row["path"] for row in lock_rows}) == len(lock_rows), "source lock paths unique")
        for row in lock_rows:
            relative = Path(row["path"])
            audit.check(not relative.is_absolute() and ".." not in relative.parts, f"contained lock path {row['path']}")
            path = ROOT / relative
            audit.check(path.is_file(), f"locked source exists {row['path']}")
            if path.is_file():
                audit.check(sha256(path) == row["sha256"], f"locked source hash {row['path']}")

    for name in OUTPUT_NAMES:
        audit.check((ART / name).is_file(), f"artifact exists {name}")
    if audit.failures:
        payload = {"status": "FAIL", "checks": audit.checks, "failures": audit.failures}
        (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f".gdt794_replay_{replay_index}_", dir=BASE) as tmp:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", tmp],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            audit.check(completed.returncode == 0, f"builder replay {replay_index} exits zero")
            audit.check(completed.stdout.startswith("CORRECTION__216_ADMITTED_SLOTS"), f"builder replay {replay_index} status")
            for name in OUTPUT_NAMES:
                replay = Path(tmp) / name
                audit.check(replay.is_file(), f"replay {replay_index} artifact {name}")
                if replay.is_file():
                    audit.check(replay.read_bytes() == (ART / name).read_bytes(), f"byte replay {replay_index} {name}")

    atlas = read_tsv(ART / OUTPUT_NAMES[0])
    defaults = read_tsv(ART / OUTPUT_NAMES[1])
    predictions = read_tsv(ART / OUTPUT_NAMES[2])
    scores = read_tsv(ART / OUTPUT_NAMES[3])
    kluge = read_tsv(ART / OUTPUT_NAMES[4])
    kluge_summary = read_tsv(ART / OUTPUT_NAMES[5])
    correction = read_tsv(ART / OUTPUT_NAMES[6])
    relational = read_tsv(ART / OUTPUT_NAMES[7])
    adjudication = read_tsv(ART / OUTPUT_NAMES[8])
    otody = read_tsv(ART / OUTPUT_NAMES[9])
    cross_scope = read_tsv(ART / OUTPUT_NAMES[10])
    overrides = read_tsv(ART / OUTPUT_NAMES[11])
    result = json.loads((ART / OUTPUT_NAMES[12]).read_text(encoding="utf-8"))

    audit.check(len(atlas) == 216, "216 admitted circle slots")
    audit.check(len({row["array_id"] for row in atlas}) == 19, "19 admitted arrays")
    audit.check(len({row["physical_folio"] for row in atlas}) == 6, "six admitted circle folios")
    audit.check(len({row["complete_label_surface"] for row in atlas}) == 199, "199 complete label surfaces")
    audit.check(sum(int(row["label_token_count"]) for row in atlas) == 274, "274 circle-label tokens")
    audit.check(sum(int(row["label_token_count"]) > 1 for row in atlas) == 47, "47 multi-token inscriptions")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in atlas), "atlas zero component export")
    audit.check(not any(row["source_selector"].startswith("f84") for row in atlas), "atlas excludes sealed folio")

    audit.check(len(defaults) == 15, "15 repeated complete-label defaults")
    audit.check(Counter(int(row["circle_occurrence_count"]) for row in defaults) == Counter({2: 13, 3: 2}), "13 doubletons and two tripletons")
    audit.check(sum(int(row["circle_occurrence_count"]) for row in defaults) == 32, "32 recurrent-label occurrences")
    expected_cross_folio = {"okal", "okaram", "okeal", "okody", "okolar", "otalaiin", "otar", "otody"}
    audit.check({row["complete_label_surface"] for row in defaults if int(row["physical_folio_count"]) >= 2} == expected_cross_folio, "eight exact cross-folio labels")
    audit.check({row["complete_label_surface"] for row in defaults if row["same_array_collision"] == "YES"} == {"okeod", "okal", "okaly"}, "three same-array collision forms")
    audit.check(all(row["working_default_de"] and row["evidence"] and row["counterevidence"] for row in defaults), "all repeated forms have defaults and evidence")
    audit.check(all(row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" for row in defaults), "defaults retain ceiling")
    otody_default = next(row for row in defaults if row["complete_label_surface"] == "otody")
    audit.check(otody_default["clock_positions"] == "1.000000|1.250000", "otody one-o'clock pair")
    audit.check(otody_default["best_observed_model"] == "NARROW_VISIBLE_TIME_OR_DEGREE_POSITION", "otody concrete position rival")

    audit.check(len(scores) == 4 and len({row["model_id"] for row in scores}) == 4, "four coordinate models")
    audit.check({row["coordinate_channel"] for row in scores} == {"SOURCE_SLOT_FRACTION", "VISIBLE_CLOCK_HOUR", "AXIS_FOLDED_CLOCK_HOUR", "KLUGE_A_MEMBER"}, "four coordinate channels")
    audit.check(all(row["gate_result"] == "FAIL_JOINT_TRANSFER" for row in scores), "no joint coordinate codebook passes")
    audit.check(len(predictions) == sum(int(row["target_event_count"]) for row in scores), "prediction rows match score capacity")
    audit.check(all(row["interpretation_ceiling"] == "COMPLETE_WHOLE_COORDINATE_DIAGNOSTIC_ONLY" for row in predictions), "prediction ceiling")

    audit.check(len(kluge) == 101, "101 true Kluge-A records")
    audit.check(len({row["array_id"] for row in kluge}) == 11, "11 Kluge arrays")
    audit.check(Counter(row["physical_folio"] for row in kluge) == Counter({"f70": 43, "f71": 15, "f72": 43}), "Kluge records by folio")
    audit.check(len(kluge_summary) == 30 and [int(row["kluge_a_member"]) for row in kluge_summary] == list(range(1, 31)), "complete Kluge 1-30 summary")
    k9 = [row for row in kluge if row["kluge_a_member"] == "9"]
    audit.check([row["complete_label_surface"] for row in k9] == ["okaldal", "okalal", "otchody", "okalam", "okarcham"], "true Kluge-09A label set")
    audit.check(sum(row["literal_okal_prefix"] == "YES" for row in k9) == 3, "Kluge-09A three of five okal prefix")
    audit.check(len({row["physical_folio"] for row in k9 if row["literal_okal_prefix"] == "YES"}) == 2, "Kluge-09A hits on two folios")

    audit.check(len(correction) == 5, "five raw-slot4 correction rows")
    audit.check([row["kluge_a_member"] for row in correction] == ["9", "17", "9", "13", "NA"], "raw slot4 has three Kluge values plus missing")
    audit.check([row["visible_clock_hour"] for row in correction] == ["3.000000", "0.750000", "1.500000", "0.750000", "0.000000"], "raw slot4 clock positions diverge")
    audit.check(Counter(row["same_true_kluge_homolog_as_first_row"] for row in correction) == Counter({"YES": 2, "NO": 2, "UNKNOWN_MISSING_KLUGE": 1}), "only two raw slot4 rows share true homolog")

    audit.check(len(relational) == 1, "one repeated cross-array label pair")
    audit.check((relational[0]["left_complete_label"], relational[0]["right_complete_label"]) == ("okody", "otody"), "relational pair identity")
    audit.check(relational[0]["shared_array_count"] == "2" and relational[0]["physical_folio_count"] == "2", "relational pair two arrays and folios")
    audit.check(relational[0]["stable_relational_spacing"] == "NO", "relational spacing fails")

    audit.check(len(adjudication) == 7, "seven candidate adjudications")
    selected = [row for row in adjudication if row["selected_working_model"] == "YES"]
    audit.check(len(selected) == 1 and selected[0]["model_id"] == "OPAQUE_ENTRY_CLASS", "opaque entry class remains primary")
    audit.check(next(row for row in adjudication if row["model_id"] == "OTODY_NARROW_CLOCK_POSITION")["gate_result"] == "RETAIN_CONCRETE_WHOLE_POSITION_RIVAL", "otody rival retained")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in adjudication), "adjudication zero component export")

    audit.check(len(otody) == 4, "four exact otody occurrences")
    audit.check(Counter(row["occurrence_kind"] for row in otody) == Counter({"LOCAL_ADDRESS_OR_LABEL": 2, "RUNNING_EVENT": 2}), "otody two labels and two running")
    audit.check(all(row["surface"] == "otody" and row["confirmed_lexeme"] == "NO" for row in otody), "otody exact whole and unconfirmed")

    audit.check(len(cross_scope) == 15 and {row["complete_label_surface"] for row in cross_scope} == {row["complete_label_surface"] for row in defaults}, "15 repeated cross-scope audits")
    audit.check(sum(row["gdt794_cross_scope_decision"].startswith("HOLD_") for row in cross_scope) == 6, "six pharmaceutical whole readings held")
    audit.check(next(row for row in cross_scope if row["complete_label_surface"] == "okal")["gdt794_cross_scope_decision"] == "OLD_PHARMA_READING_ALREADY_SUPERSEDED_BY_GDT793", "okal predecessor supersession recorded")
    audit.check({row["complete_label_surface"] for row in cross_scope if row["gdt794_cross_scope_decision"].startswith("HOLD_")} == {"okaly", "okaram", "okeal", "otaly", "otar", "otody"}, "exact six held wholes")
    audit.check(all(row["prose_scope_disposition"].startswith("PRESERVE_AS_HISTORICAL") for row in cross_scope), "old candidates preserved as history")

    audit.check(len(overrides) == 216 and len({row["locus"] for row in overrides}) == 216, "216 unique sequence overrides")
    audit.check(sum(int(row["suppressed_unconditional_token_default_count"]) for row in overrides) == 97, "97 token-level global readings suppressed")
    suppressed_forms = {
        item.split("=", 1)[0]
        for row in overrides for item in row["suppressed_unconditional_token_defaults"].split("|")
        if item != "NONE"
    }
    audit.check(len(suppressed_forms) == 64, "64 distinct suppressed token surfaces")
    audit.check(sum(int(row["label_token_count"]) == 1 and int(row["suppressed_unconditional_token_default_count"]) == 1 for row in overrides) == 42, "42 licensed single-token circle labels overridden")
    audit.check(sum(int(row["label_token_count"]) > 1 and int(row["suppressed_unconditional_token_default_count"]) > 0 for row in overrides) == 36, "36 multi-token labels contain global defaults")
    audit.check(sum(int(row["label_token_count"]) > 1 and int(row["suppressed_unconditional_token_default_count"]) == int(row["label_token_count"]) for row in overrides) == 14, "14 multi-token labels would fully compose")
    audit.check(all(row["tokenwise_pharmaceutical_composition_allowed"] == "NO" and row["renderer_precedence"] == "RADIAL_LABEL_SEQUENCE_OVERRIDE_GT_GLOBAL_TOKEN" for row in overrides), "sequence context always wins")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in overrides), "override component ceiling")

    audit.check(result["experiment_id"] == "GDT794" and result["status"].startswith("CORRECTION__216_ADMITTED_SLOTS"), "result identity and status")
    audit.check(result["scope"] == {
        "released_physical_pages": 30,
        "source_selectors": 35,
        "admitted_circle_physical_folios": 6,
        "new_pages_or_images_opened": 0,
        "mixed_sources_queried": 0,
        "sealed_rows_materialized": 0,
    }, "result exact scope")
    audit.check(result["counts"]["admitted_circle_slots"] == 216 and result["counts"]["kluge_a_coordinate_slots"] == 101, "result core counts")
    audit.check(result["counts"]["suppressed_unconditional_token_occurrences"] == 97 and result["counts"]["cross_scope_dictionary_holds"] == 6, "result renderer repair counts")
    audit.check(result["decision"]["raw_slot4_correction"] == "SOURCE_SLOT_INDEX_4_IS_NOT_ONE_KLUGE_OR_ANGLE_HOMOLOG", "result raw-slot correction")
    audit.check(result["decision"]["joint_position_codebook"] == "NOT_SELECTED", "result no joint codebook")
    audit.check(result["decision"]["selected_primary_model"] == "OPAQUE_ENTRY_CLASS", "result selected model")
    audit.check(result["counts"]["component_exports"] == result["counts"]["confirmed_lexemes"] == 0, "result zero semantic exports")

    payload = {
        "status": "PASS" if not audit.failures else "FAIL",
        "checks": audit.checks,
        "failures": audit.failures,
        "builder_byte_replay": not any(item.startswith("byte replay") for item in audit.failures),
        "new_pages_or_images_opened": 0,
        "mixed_sources_queried": 0,
        "sealed_rows_materialized": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
