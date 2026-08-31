#!/usr/bin/env python3
"""Independently rebuild and validate GDT682."""

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
EXP = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V55_PATH = ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/V55_51_LINE_READER.tsv"
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
    spec = importlib.util.spec_from_file_location("gdt682_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT682 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "TARGET_FAMILY_CARDS.tsv",
        "CONTEXT_ROLE_VERDICTS.tsv",
        "TARGET_EXACT_OCCURRENCE_AUDIT.tsv",
        "BOUNDARY_DECISIONS.tsv",
        "FINAL_COMPLETED_LINE_V56.tsv",
        "V56_51_LINE_READER.tsv",
        "GLOBAL_NEWLY_COMPLETED_LINES.tsv",
        "FAMILY_PREDICTIONS.tsv",
        "HISTORICAL_ANALOG_ATLAS.tsv",
        "GDT682_FINAL_COMPLETED_PRACTICAL_READER.md",
        "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt682-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_"), "rebuilt status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "TARGET_FAMILY_CARDS.tsv")
    context_roles = read_tsv(ART / "CONTEXT_ROLE_VERDICTS.tsv")
    occurrences = read_tsv(ART / "TARGET_EXACT_OCCURRENCE_AUDIT.tsv")
    boundaries = read_tsv(ART / "BOUNDARY_DECISIONS.tsv")
    completed = read_tsv(ART / "FINAL_COMPLETED_LINE_V56.tsv")
    v56 = read_tsv(ART / "V56_51_LINE_READER.tsv")
    v55 = read_tsv(V55_PATH)
    global_closed = read_tsv(ART / "GLOBAL_NEWLY_COMPLETED_LINES.tsv")
    predictions = read_tsv(ART / "FAMILY_PREDICTIONS.tsv")
    analogs = read_tsv(ART / "HISTORICAL_ANALOG_ATLAS.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 7, "seven cards")
    audit.check(len({row["surface"] for row in cards}) == 7, "unique cards")
    audit.check({int(row["card_rank"]) for row in cards} == set(range(1, 8)), "unique consecutive card ranks")
    expected_counts = {row["surface"]: int(row["expected_occurrences"]) for row in cards}
    audit.check(expected_counts == {
        "polairy": 1, "oair": 4, "olpcheey": 1, "opchedaiin": 4,
        "dairody": 3, "ypcheddy": 1, "sairy": 3,
    }, "exact seven-card counts")
    card_by_surface = {row["surface"]: row for row in cards}
    audit.check(card_by_surface["polairy"]["working_meaning_de"] == "abgeschlossene zweite Pulverstofffraktion", "polairy concrete")
    audit.check(card_by_surface["oair"]["working_meaning_de"] == "zweite Ansatzfraktion", "oair concrete")
    audit.check("Holzdrogenpulver" in card_by_surface["olpcheey"]["working_meaning_de"], "olpcheey wood powder")
    audit.check(card_by_surface["opchedaiin"]["working_meaning_de"].startswith("drei Dosen"), "opchedaiin triple dose")
    audit.check(card_by_surface["dairody"]["working_meaning_de"] == "fertiggestellte abgemessene Ansatzfraktion II", "dairody result")
    audit.check("Trocknung abschließen" in card_by_surface["ypcheddy"]["working_meaning_de"], "ypcheddy visible close sequence")
    audit.check("abziehen" in card_by_surface["ypcheddy"]["strongest_rival_de"], "ypcheddy draw rival retained")
    audit.check(card_by_surface["sairy"]["working_meaning_de"] == "abgeschlossene zweite Saatgutfraktion", "sairy seed fraction")
    audit.check(sum(int(row["action_license"]) for row in cards) == 1, "one newly licensed action")
    audit.check(card_by_surface["ypcheddy"]["action_license"] == "1", "ypcheddy sole action")
    audit.check(card_by_surface["polairy"]["composition"].endswith("Y_START_OR_CLOSE"), "polairy published Y component")
    audit.check(card_by_surface["sairy"]["composition"].endswith("Y_START_OR_CLOSE"), "sairy published Y component")
    audit.check(card_by_surface["ypcheddy"]["composition"] == "Y_REFERENCE+P_POWDER+CH_DRY+E_MIDDLE+D_TERM_CLOSE+DY_FINISHED", "ypcheddy visible composition order")

    audit.check(len(context_roles) == 17, "seventeen keyed context roles")
    context_keys = {(row["locus"], row["ordinal"]) for row in context_roles}
    audit.check(len(context_keys) == 17, "unique context role keys")
    audit.check(all(row["context_verdict"].startswith("HOLD") for row in context_roles), "all context verdicts hold with explicit rivals")
    audit.check(sum(row["context_verdict"] == "HOLD_PROVISIONAL_FORWARD_BINDING" for row in context_roles) == 2, "two provisional forward-binding rows")

    audit.check(len(occurrences) == 17, "seventeen occurrence rows")
    audit.check(len({(row["locus"], row["ordinal"]) for row in occurrences}) == 17, "unique occurrence keys")
    audit.check({(row["locus"], row["ordinal"]) for row in occurrences} == context_keys, "occurrences equal keyed context roles")
    audit.check(Counter(row["surface"] for row in occurrences) == expected_counts, "occurrence distribution")
    audit.check(len({row["locus"] for row in occurrences}) == 11, "eleven target loci")
    audit.check(len({row["page"] for row in occurrences}) == 10, "ten target pages")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(all(not GENERIC.search(row["context_after_de"]) for row in occurrences), "no generic occurrence filler")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 16, "RF1B_ONLY_EXACT": 1,
    }, "reader support distribution")
    audit.check(all(row["context_verdict"].startswith("HOLD") for row in occurrences), "occurrence verdicts explicit holds")
    audit.check(all(row["context_role"] for row in occurrences), "every occurrence has a semantic role")
    audit.check(sum(row["surface"] == "oair" for row in occurrences) == 4, "four oair contexts")
    audit.check(all(row["reader_support"] == "BOTH_EXACT" for row in occurrences if row["locus"] == "f105v.1"), "source targets bilateral")

    audit.check(len(boundaries) == 1, "one boundary decision")
    boundary = boundaries[0]
    audit.check((boundary["locus"], boundary["ordinal"], boundary["surface"]) == ("f111v.33", "3", "oair"), "oair boundary key")
    audit.check(boundary["it2a_operation"] == "ONE" and boundary["it2a_render"] == "qoair", "IT2a qoair rival")
    audit.check(boundary["rf1b_operation"] == "EXACT" and boundary["rf1b_render"] == "oair", "RF1b exact oair")
    audit.check(boundary["reader_support"] == "RF1B_ONLY_EXACT", "oair support label")
    audit.check(boundary["applied_render_de"] == "zweite Ansatzfraktion", "oair nominal default retained")

    audit.check(len(completed) == 1 and completed[0]["locus"] == "f105v.1", "one completed source line")
    source = completed[0]
    audit.check(source["closed_ordinals"] == "1|2|3|6|7|8|9", "seven closed source ordinals")
    audit.check(source["closed_surfaces"] == "polairy|oair|olpcheey|opchedaiin|dairody|ypcheddy|sairy", "seven closed source surfaces")
    audit.check(source["added_action_ordinals"] == "8" and source["added_action_surfaces"] == "ypcheddy", "one added source action")
    audit.check(source["new_action_ordinals"] == "4|8" and source["new_action_surfaces"] == "ykaiin|ypcheddy", "final source actions")
    tokens = source["zl3b_line"].split()
    chunks = source["aligned_line_de"].rstrip(".").split(" · ")
    literals = source["new_literal_token_glosses_de"].split(" | ")
    audit.check(len(tokens) == len(chunks) == len(literals) == 9, "source token alignment")
    audit.check("⟦" not in source["aligned_line_de"] and ":?]" not in source["new_literal_token_glosses_de"], "source fully closed")
    audit.check(not GENERIC.search(source["aligned_line_de"]), "no generic source filler")
    audit.check(not GENERIC.search(source["practical_translation_de"]), "no generic practical filler")
    audit.check("Holzdrogenpulver" in source["practical_translation_de"], "concrete wood powder")
    audit.check("Stufe III" in source["practical_translation_de"], "concrete heat grade")
    audit.check("drei Dosen" in source["practical_translation_de"], "concrete dose")
    audit.check("Saatgutfraktion" in source["practical_translation_de"], "concrete seed fraction")
    audit.check("abgemessene" in source["practical_translation_de"], "measured preparation retained")
    audit.check("abgeschlossen" in source["practical_translation_de"], "seed closure retained")
    audit.check("Trocknung abschließen" in source["practical_translation_de"], "concrete close operation")

    audit.check(len(v56) == len(v55) == 51, "51-line readers")
    audit.check(sum(int(row["token_count"]) for row in v56) == 479, "479 tokens")
    audit.check(sum(int(row["new_v56_positions"]) for row in v56) == 7, "seven V56 assignments")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v56) == 0, "zero V56 gaps")
    audit.check(sum(row["complete"] == "1" for row in v56) == 51, "all V56 lines complete")
    audit.check(Counter(int(row["residual_unknown_positions"]) for row in v56) == {0: 51}, "V56 gap distribution")
    audit.check(sum(int(row["action_positions"]) for row in v55) == 85, "85 inherited actions")
    audit.check(sum(int(row["action_positions"]) for row in v56) == 86, "86 V56 actions")
    audit.check(Counter(row["line_mode"] for row in v56) == {
        "ACTION_SEQUENCE": 16, "MIXED_RECORD": 23, "NOMINAL_REGISTER": 6, "QUANTITY_LABEL": 6,
    }, "V56 modes")
    audit.check(all(row["remaining_unknown_surfaces"] == "NONE" for row in v56), "no remaining unknown surfaces")
    audit.check(all("⟦" not in row["aligned_line_de"] and ":?]" not in row["literal_token_glosses_de"] for row in v56), "no reader placeholders")
    audit.check(all(not GENERIC.search(row["aligned_line_de"]) for row in v56), "no generic aligned renderer")
    audit.check(all(not GENERIC.search(row["practical_translation_de"]) for row in v56), "no generic practical renderer")
    source_v56 = next(row for row in v56 if row["locus"] == "f105v.1")
    audit.check(source_v56["new_v56_positions"] == "7" and source_v56["assigned_fraction"] == "1.000000", "source V56 closure")
    audit.check(source_v56["action_ordinals"] == "4|8", "source V56 action binding")
    v55_by_locus = {row["locus"]: row for row in v55}
    for row in v56:
        old = v55_by_locus[row["locus"]]
        if row["locus"] != "f105v.1":
            audit.check(row["aligned_line_de"] == old["aligned_line_de"], f"untouched aligned V55 line {row['locus']}")
            audit.check(row["literal_token_glosses_de"] == old["literal_token_glosses_de"], f"untouched literal V55 line {row['locus']}")
            audit.check(row["practical_translation_de"] == old["practical_translation_de"], f"untouched practical V55 line {row['locus']}")

    audit.check(len(global_closed) == 1 and global_closed[0]["locus"] == "f105v.1", "one global closure")
    audit.check(global_closed[0]["target_ordinals"] == "1|2|3|6|7|8|9", "global closure ordinals")
    audit.check("[" not in global_closed[0]["after_literal_de"], "global line fully literalized")
    audit.check(len(predictions) == 7, "seven predictions")
    audit.check({row["prediction_id"] for row in predictions} == {f"GDT682-P0{i}" for i in range(1, 8)}, "prediction ids")
    audit.check(len(analogs) == 7, "seven historical analogs")
    audit.check(len({row["analog_id"] for row in analogs}) == 7, "unique historical analog ids")
    audit.check(all(row["analog_id"].startswith("GDT682-H") for row in analogs), "GDT682 analog ids")

    audit.check(result["status"] == "PASS_7_NEW_CARDS__17_CONTEXTS_HOLD__FINAL_V56_LINE_CLOSED__V56_COMPLETE", "result status")
    audit.check(result["basis"]["new_pages_opened"] == 0, "no new pages")
    audit.check(result["basis"]["f84"] == result["basis"]["f84r"] == "FORBIDDEN", "sealed folios forbidden")
    audit.check(result["basis"]["cross_guard"] == {"selected": 11, "skipped_forbidden": 98, "skipped_not_allowed": 5277}, "guard stats")
    audit.check(result["global_overlay"]["unknown_positions_before"] == 7573, "global unknown before")
    audit.check(result["global_overlay"]["unknown_positions_after"] == 7556, "global unknown after")
    audit.check(result["global_overlay"]["complete_lines_before"] == 1439, "global complete before")
    audit.check(result["global_overlay"]["complete_lines_after"] == 1440, "global complete after")
    audit.check(result["v56_reader"]["assigned_after"] == 479, "result V56 assigned")
    audit.check(result["v56_reader"]["unknown_after"] == 0, "result V56 no gaps")
    audit.check(result["v56_reader"]["hard_generic_hits"] == 0, "result no generic hits")
    audit.check(result["v56_reader"]["legacy_generic_token_positions"] == 6, "six inherited generic OL positions")
    audit.check(result["v56_reader"]["legacy_generic_loci"] == ["f112r.36", "f115r.1", "f80r.17", "f80v.35", "f86v5.2", "f86v6.4"], "legacy OL loci")
    audit.check(result["v56_reader"]["legacy_generic_practical_lines"] == ["f112r.36", "f86v5.2"], "two generic practical lines")
    audit.check(len(result["files"]) == 10, "ten hashed companion artifacts")
    audit.check("not confirmed plaintext" in result["claim_ceiling"], "claim ceiling explicit")
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
        "cards": 7,
        "inherited_cards_reused": 0,
        "occurrences": 17,
        "context_role_verdicts": 17,
        "boundary_decisions": 1,
        "completed_source_lines": 1,
        "global_newly_completed_lines": 1,
        "v56_lines": 51,
        "v56_tokens": 479,
        "v56_unknown": 0,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
