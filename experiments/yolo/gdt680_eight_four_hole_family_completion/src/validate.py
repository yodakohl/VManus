#!/usr/bin/env python3
"""Independently rebuild and validate GDT680."""

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
EXP = ROOT / "experiments/yolo/gdt680_eight_four_hole_family_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V53_PATH = ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion/artifacts/V53_51_LINE_READER.tsv"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|Arbeitsstelle|"
    r"Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|Arbeitsschritt|Stationsansatz|"
    r"Stationsposten|Stationswert|Stationsanteil|Stationseinheit|weiterführen|work item|"
    r"working material|worksite|work cycle|source vessel|destination place|destination vessel)\b",
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
    spec = importlib.util.spec_from_file_location("gdt680_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT680 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "INHERITED_CARD_REUSE.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "EIGHT_COMPLETED_LINES_V54.tsv",
        "V54_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT680_EIGHT_COMPLETED_PRACTICAL_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt680-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    reuse = read_tsv(ART / "INHERITED_CARD_REUSE.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    boundaries = read_tsv(ART / "BOUNDARY_DECISIONS.tsv")
    completed = read_tsv(ART / "EIGHT_COMPLETED_LINES_V54.tsv")
    v54 = read_tsv(ART / "V54_51_LINE_READER.tsv")
    global_closed = read_tsv(ART / "GLOBAL_NEWLY_COMPLETED_LINES.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    v53 = read_tsv(V53_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 30, "thirty new cards")
    audit.check(len({row["surface"] for row in cards}) == 30, "unique cards")
    audit.check(len(reuse) == 1 and reuse[0]["surface"] == "pchedaiin", "one inherited pchedaiin card")
    audit.check(reuse[0]["source_experiment"] == "GDT678", "pchedaiin source")
    audit.check(reuse[0]["working_meaning_de"] == "drei Dosen bis Mittelstufe getrocknetes Pulver", "pchedaiin unchanged")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(sum(expected_counts.values()) == 88, "card counts total 88")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["tshol"]["working_meaning_de"] == "kalt eingeweichter Drogenstoff", "tshol concrete")
    audit.check(card_by_surface["tshol"]["observed_occurrences"] == "6", "tshol family")
    audit.check(card_by_surface["chetain"]["action_license"] == "1", "chetain process")
    audit.check("Kühlstufe II" in card_by_surface["chetain"]["working_meaning_de"], "chetain sequence")
    audit.check(card_by_surface["qodar"]["observed_occurrences"] == "10", "qodar mass command")
    audit.check(card_by_surface["qockhol"]["composition"] == "QO_COMMAND+CKHOL_COMPOSITE_DRUG_MATERIAL", "qockhol composition")
    audit.check("Blütenansatz" in card_by_surface["ofchedy"]["working_meaning_de"], "ofchedy flower correction")
    audit.check(card_by_surface["araram"]["working_meaning_de"] == "ein Maß der ersten Drogenfraktion", "araram one measure")
    audit.check(card_by_surface["qopaiin"]["working_meaning_de"] == "drei Teile Pulveransatz nehmen", "qopaiin take command")
    audit.check("Rohstoffmenge I" in card_by_surface["oidal"]["working_meaning_de"] and "zweite" not in card_by_surface["oidal"]["working_meaning_de"], "oidal odal correction")
    audit.check(card_by_surface["solky"]["confidence"] == "LOW_EXPLORATORY", "solky visibly weak")
    audit.check(sum(int(row["action_license"]) for row in cards) == 9, "nine action cards")

    audit.check(len(occurrences) == 88, "88 occurrence rows")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 88, "unique occurrence keys")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence distribution")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 70,
        "IT2A_ONLY_EXACT": 6,
        "RF1B_ONLY_EXACT": 8,
        "NEITHER_EXACT": 4,
    }, "reader support distribution")
    audit.check(sum(row["context_decision"] == "HOLD_SAME_CARD" for row in occurrences) == 70, "70 fully exact holds")

    audit.check(len(boundaries) == 18, "eighteen reader decisions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" for row in boundaries) == 4, "four neither-exact decisions")
    chair = next(row for row in boundaries if row["surface"] == "chair")
    audit.check(chair["it2a_render"] == chair["rf1b_render"] == "pchair", "chair bilateral prefix repair")
    op = next(row for row in boundaries if row["surface"] == "op")
    audit.check(op["it2a_render"] == "opchedy" and op["rf1b_render"] == "opchedylchey", "op bilateral right join")
    tail = next(row for row in boundaries if row["surface"] == "tail")
    audit.check(tail["it2a_render"] == "kail" and tail["rf1b_render"] == "tail", "tail polarity rival")
    araram = next(row for row in boundaries if row["surface"] == "araram")
    audit.check(araram["it2a_operation"] == "EXACT" and araram["rf1b_operation"] == "SPLIT_2", "araram quantity split")

    audit.check(len(completed) == 8, "eight completed source lines")
    audit.check(len({row["locus"] for row in completed}) == 8, "unique source loci")
    audit.check(sum(len(row["closed_surfaces"].split("|")) for row in completed) == 32, "32 source slots")
    audit.check(sum(len([] if row["added_action_ordinals"] == "NONE" else row["added_action_ordinals"].split("|")) for row in completed) == 10, "ten new source actions")
    for row in completed:
        tokens = row["zl3b_line"].split()
        chunks = row["aligned_line_de"].rstrip(".").split(" · ")
        literals = row["new_literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(chunks) == len(literals) == int(row["token_count"]), f"token alignment {row['locus']}")
        audit.check("⟦" not in row["aligned_line_de"] and ":?]" not in row["new_literal_token_glosses_de"], f"line closed {row['locus']}")
        audit.check(not GENERIC.search(row["aligned_line_de"]), f"no generic aligned filler {row['locus']}")
        audit.check(not GENERIC.search(row["practical_translation_de"]), f"no generic practical filler {row['locus']}")
    f105 = next(row for row in completed if row["locus"] == "f105v.14")
    audit.check("drei Dosen bis Mittelstufe getrocknetes Pulver" in f105["aligned_line_de"], "f105 inherited pchedaiin")
    f23 = next(row for row in completed if row["locus"] == "f23r.6")
    audit.check("kalt eingeweichter Drogenstoff" in f23["aligned_line_de"], "f23 tshol practical")
    f80 = next(row for row in completed if row["locus"] == "f80r.17")
    audit.check("Kühlstufe II" in f80["aligned_line_de"], "f80 chetain practical")
    f88 = next(row for row in completed if row["locus"] == "f88r.19")
    audit.check(f88["new_action_surfaces"].split("|").count("qoekol") == 2, "f88 repeated qoekol actions")
    audit.check("Drogenstoff aus Arzneikompositum zugeben" in f88["aligned_line_de"], "f88 qockhol practical")

    audit.check(len(v54) == 51, "51 V54 lines")
    audit.check(sum(int(row["token_count"]) for row in v54) == 479, "479 tokens")
    audit.check(sum(int(row["new_v54_positions"]) for row in v54) == 32, "32 V54 positions")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v54) == 37, "37 V54 gaps")
    audit.check(sum(row["complete"] == "1" for row in v54) == 44, "44 complete V54 lines")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v54) == {0: 44, 5: 6, 7: 1}, "V54 gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v54) == 75, "75 V54 actions")
    audit.check(Counter(row["line_mode"] for row in v54) == {
        "ACTION_SEQUENCE": 14,
        "MIXED_RECORD": 21,
        "NOMINAL_REGISTER": 9,
        "QUANTITY_LABEL": 7,
    }, "V54 modes")
    audit.check(all(not GENERIC.search(row["aligned_line_de"]) for row in v54), "V54 aligned no generic")
    audit.check(all(not GENERIC.search(row["practical_translation_de"]) for row in v54), "V54 practical no generic")
    v53_by_locus = {row["locus"]: row for row in v53}
    completed_loci = {row["locus"] for row in completed}
    for row in v54:
        old = v53_by_locus[row["locus"]]
        if row["locus"] not in completed_loci:
            audit.check(row["aligned_line_de"] == old["aligned_line_de"], f"untouched aligned V53 line {row['locus']}")
            audit.check(row["literal_token_glosses_de"] == old["literal_token_glosses_de"], f"untouched literal V53 line {row['locus']}")
            audit.check(row["practical_translation_de"] == old["practical_translation_de"], f"untouched practical V53 line {row['locus']}")

    audit.check(len(global_closed) == 11, "eleven global closures")
    audit.check(completed_loci.issubset({row["locus"] for row in global_closed}), "global closures include source")
    audit.check({row["locus"] for row in global_closed} - completed_loci == {"f112v.22", "f14r.2", "f32v.10"}, "three extra global closures")
    audit.check(all(":?]" not in row["after_literal_de"] for row in global_closed), "global rows closed")
    audit.check(len(predictions) == 8 and len({row["prediction_id"] for row in predictions}) == 8, "eight predictions")
    audit.check(len(analogs) == 7, "seven analogs")
    audit.check(all(row["source_url"].startswith("https://") for row in analogs), "analog URLs")
    audit.check(all(row["scope_limit"] for row in analogs), "analog limits")

    audit.check(result["status"] == "PASS_30_NEW_CARDS__88_CONTEXTS_HOLD__1_CARD_REUSED__8_V54_LINES_CLOSED__V54_37_OPEN", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 64, "skipped_forbidden": 98, "skipped_not_allowed": 5224}, "guard counts")
    audit.check(result["global_overlay"] == {
        "unknown_positions_before": 7765,
        "unknown_positions_after": 7677,
        "new_assigned_positions": 88,
        "complete_lines_before": 1418,
        "complete_lines_after": 1429,
        "newly_completed_lines": 11,
        "newly_completed_outside_v53_source": ["f112v.22", "f14r.2", "f32v.10"],
    }, "global result")
    audit.check(result["v54_reader"]["unknown_after"] == 37, "result V54 gaps")
    audit.check(result["v54_reader"]["assigned_after"] == 442, "result V54 assigned")
    audit.check(result["v54_reader"]["complete_after"] == 44, "result V54 complete")
    audit.check(result["v54_reader"]["new_action_positions"] == 10, "result new actions")
    audit.check(result["v54_reader"]["hard_generic_hits"] == 0, "result zero generic")
    for name, digest in result["files"].items():
        audit.check(builder.sha256(ART / name) == digest, f"result hash {name}")

    local_home_prefix = "/" + "home/"
    secret_markers = ("BEGIN " + "PRIVATE KEY", "BEGIN " + "OPENSSH PRIVATE KEY", "AK" + "IA")
    for name in artifact_names:
        content = (ART / name).read_text(encoding="utf-8")
        audit.check(local_home_prefix not in content and "file://" not in content, f"no local path {name}")
        audit.check(not any(marker in content for marker in secret_markers), f"no credential marker {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_identical_rebuild_files": len(artifact_names),
        "cards": 30,
        "inherited_cards_reused": 1,
        "occurrences": 88,
        "boundary_decisions": 18,
        "completed_source_lines": 8,
        "global_newly_completed_lines": 11,
        "v54_lines": 51,
        "v54_tokens": 479,
        "v54_unknown": 37,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
