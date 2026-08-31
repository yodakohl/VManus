#!/usr/bin/env python3
"""Independently rebuild and validate GDT678."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V51_PATH = ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/artifacts/V51_51_LINE_READER.tsv"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|Arbeitsstelle|"
    r"Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|Arbeitsschritt|Stationsansatz|"
    r"Stationsposten|Stationswert|Stationsanteil|Stationseinheit|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt678_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT678 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "SEVENTEEN_COMPLETED_LINES_V52.tsv",
        "V52_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT678_SEVENTEEN_COMPLETED_PRACTICAL_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt678-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    boundaries = read_tsv(ART / "BOUNDARY_DECISIONS.tsv")
    completed = read_tsv(ART / "SEVENTEEN_COMPLETED_LINES_V52.tsv")
    v52 = read_tsv(ART / "V52_51_LINE_READER.tsv")
    global_closed = read_tsv(ART / "GLOBAL_NEWLY_COMPLETED_LINES.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    v51 = read_tsv(V51_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 34, "thirty-four cards")
    audit.check(len({row["surface"] for row in cards}) == 34, "unique cards")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(sum(expected_counts.values()) == 101, "card counts total 101")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["olchey"]["working_meaning_de"] == "Holzdrogenansatz, bis Mittelstufe getrocknet", "olchey concrete")
    audit.check(card_by_surface["qokeod"]["working_meaning_de"] == "heißen Auszug bereiten und abschließen", "qokeod learned qokeo block")
    audit.check(card_by_surface["qoin"]["working_meaning_de"] == "zweiten Ansatz nehmen", "qoin learned oin block")
    audit.check(card_by_surface["qocho"]["working_meaning_de"] == "Trockenansatz nehmen", "qocho learned cho block")
    audit.check(card_by_surface["rr"]["working_meaning_de"] == "getrocknete Wurzeldroge", "rr controlled by rchr")
    audit.check(card_by_surface["rr"]["card_type"] == "READER_CONDITIONED_COMPOUND", "rr reader conditioned")
    audit.check(card_by_surface["keo"]["card_type"] == "READER_BOUND_COMPONENT", "keo bound")
    audit.check(card_by_surface["karchees"]["card_type"] == "READER_BOUND_COMPONENT", "karchees bound")
    audit.check(sum(int(row["licensed_actions"]) for row in cards) == 24, "twenty-four global action occurrences")

    audit.check(len(occurrences) == 101, "101 occurrence rows")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 101, "unique occurrence keys")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence distribution")
    audit.check(all(row["context_decision"].startswith("HOLD_") for row in occurrences), "all contexts hold")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 65, "IT2A_ONLY_EXACT": 15, "RF1B_ONLY_EXACT": 10, "NEITHER_EXACT": 11,
    }, "reader support distribution")
    audit.check(sum(int(row["action_license"]) for row in occurrences) == 24, "occurrence action total")

    audit.check(len(boundaries) == 12, "twelve boundary decisions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" for row in boundaries) == 11, "eleven neither boundary targets")
    rr = next(row for row in boundaries if row["surface"] == "rr")
    audit.check(rr["it2a_render"] == rr["rf1b_render"] == "rchr", "rr alternate form")
    audit.check(rr["practical_resolution_de"] == "getrocknete Wurzeldroge", "rr practical resolution")
    f7_keo = next(row for row in boundaries if row["locus"] == "f7r.2")
    audit.check(f7_keo["it2a_operation"] == "MERGE_2" and f7_keo["rf1b_operation"] == "EXACT", "f7 keor/exact boundary")
    lkar = next(row for row in boundaries if row["surface"] == "karchees")
    audit.check(lkar["it2a_render"] == lkar["rf1b_render"] == "lkarchees", "lkarchees both readers")

    audit.check(len(completed) == 17, "seventeen completed source lines")
    audit.check(len({row["locus"] for row in completed}) == 17, "unique source loci")
    audit.check(sum(len(row["closed_surfaces"].split("|")) for row in completed) == 34, "34 source slots")
    audit.check(sum(len([] if row["added_action_ordinals"] == "NONE" else row["added_action_ordinals"].split("|")) for row in completed) == 11, "eleven new source actions")
    for row in completed:
        tokens = row["zl3b_line"].split()
        chunks = row["aligned_line_de"].rstrip(".").split(" · ")
        literals = row["new_literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(chunks) == len(literals) == int(row["token_count"]), f"token alignment {row['locus']}")
        audit.check("⟦" not in row["aligned_line_de"] and ":?]" not in row["new_literal_token_glosses_de"], f"line closed {row['locus']}")
        audit.check(not GENERIC.search(row["aligned_line_de"]), f"no generic aligned filler {row['locus']}")
        audit.check(not GENERIC.search(row["practical_translation_de"]), f"no generic practical filler {row['locus']}")
    f7 = next(row for row in completed if row["locus"] == "f7r.2")
    audit.check("heiße · Drogenportion" in f7["aligned_line_de"] and "Ansatz auf mittlerer Heizstufe · Wurzel" not in f7["aligned_line_de"], "f7 joint keor render")
    f77 = next(row for row in completed if row["locus"] == "f77v.7")
    audit.check("getrocknete Wurzeldroge nehmen" in f77["practical_translation_de"], "f77 rchr practical")
    f86 = next(row for row in completed if row["locus"] == "f86v6.4")
    audit.check("vollständig getrocknete Charge der ersten heißen Holzfraktion" in f86["practical_translation_de"], "f86 lkarchees practical")

    audit.check(len(v52) == 51, "51 V52 lines")
    audit.check(sum(int(row["token_count"]) for row in v52) == 479, "479 tokens")
    audit.check(sum(int(row["new_v52_positions"]) for row in v52) == 34, "34 V52 positions")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v52) == 93, "93 V52 gaps")
    audit.check(sum(row["complete"] == "1" for row in v52) == 28, "28 complete V52 lines")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v52) == {0: 28, 3: 8, 4: 8, 5: 6, 7: 1}, "V52 gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v52) == 60, "60 V52 actions")
    audit.check(Counter(row["line_mode"] for row in v52) == {
        "ACTION_SEQUENCE": 12, "MIXED_RECORD": 20, "NOMINAL_REGISTER": 11, "QUANTITY_LABEL": 8,
    }, "V52 modes")
    audit.check(all(not GENERIC.search(row["aligned_line_de"]) for row in v52), "V52 no generic")
    v51_by_locus = {row["locus"]: row for row in v51}
    completed_loci = {row["locus"] for row in completed}
    for row in v52:
        old = v51_by_locus[row["locus"]]
        if row["locus"] not in completed_loci:
            audit.check(row["aligned_line_de"] == old["working_line_de"], f"untouched V51 line {row['locus']}")

    audit.check(len(global_closed) == 19, "nineteen global closures")
    audit.check(sum(row["v51_source_line"] == "1" for row in global_closed) == 17, "seventeen source closures")
    audit.check({row["locus"] for row in global_closed if row["v51_source_line"] == "0"} == {"f38v.6", "f80r.21"}, "two extra closures")
    audit.check(all(":?]" not in row["after_literal_de"] for row in global_closed), "global rows closed")
    audit.check(len(predictions) == 10 and len({row["prediction_id"] for row in predictions}) == 10, "ten predictions")
    audit.check(len(analogs) == 7, "seven analogs")
    audit.check(all(row["source_url"].startswith("https://") for row in analogs), "analog URLs")
    audit.check(all(row["scope_limit"] for row in analogs), "analog limits")

    audit.check(result["status"] == "PASS_34_FAMILY_CARDS__101_CONTEXTS_HOLD__17_V52_LINES_CLOSED__V52_93_OPEN", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 82, "skipped_forbidden": 98, "skipped_not_allowed": 5206}, "guard counts")
    audit.check(result["global_overlay"] == {
        "unknown_positions_before": 7923, "unknown_positions_after": 7822, "new_assigned_positions": 101,
        "complete_lines_before": 1391, "complete_lines_after": 1410, "newly_completed_lines": 19,
        "newly_completed_outside_v51_source": ["f38v.6", "f80r.21"],
    }, "global result")
    audit.check(result["v52_reader"]["unknown_after"] == 93, "result V52 gaps")
    audit.check(result["v52_reader"]["assigned_after"] == 386, "result V52 assigned")
    audit.check(result["v52_reader"]["complete_after"] == 28, "result V52 complete")
    audit.check(result["v52_reader"]["new_action_positions"] == 11, "result new actions")
    audit.check(result["v52_reader"]["hard_generic_hits"] == 0, "result zero generic")
    for name, digest in result["files"].items():
        audit.check(builder.sha256(ART / name) == digest, f"result hash {name}")

    local_home_prefix = "/" + "home/"
    secret_markers = (
        "BEGIN " + "PRIVATE KEY",
        "BEGIN " + "OPENSSH PRIVATE KEY",
        "AK" + "IA",
    )
    for name in artifact_names:
        content = (ART / name).read_text(encoding="utf-8")
        audit.check(local_home_prefix not in content and "file://" not in content, f"no local path {name}")
        audit.check(not any(marker in content for marker in secret_markers), f"no credential marker {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_identical_rebuild_files": len(artifact_names),
        "cards": 34,
        "occurrences": 101,
        "boundary_decisions": 12,
        "completed_source_lines": 17,
        "global_newly_completed_lines": 19,
        "v52_lines": 51,
        "v52_tokens": 479,
        "v52_unknown": 93,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
