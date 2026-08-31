#!/usr/bin/env python3
"""Independently rebuild and validate GDT683."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V56_PATH = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/V56_51_LINE_READER.tsv"
LEGACY_GLOSS = "Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz"
GENERIC = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|work item|working material|worksite|work cycle|source vessel|"
    r"destination place|destination vessel)\b",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt683_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT683 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    artifact_names = [
        "OL_CARD_RECONCILIATION.tsv", "OL_463_OCCURRENCE_AUDIT.tsv", "OL_417_LINE_RERENDER.tsv",
        "N25_BOUNDARY_DECISIONS.tsv", "ADJACENT_OL_PAIRS.tsv", "V57_SIX_OL_DEBT_REVISIONS.tsv",
        "V57_51_LINE_READER.tsv", "GDT683_V57_PRACTICAL_READER.md", "RESULT.json",
    ]
    for name in artifact_names:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt683-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"].startswith("PASS_374_BILATERAL_"), "rebuilt pass status")
        for name in artifact_names:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    cards = read_tsv(ART / "OL_CARD_RECONCILIATION.tsv")
    occurrences = read_tsv(ART / "OL_463_OCCURRENCE_AUDIT.tsv")
    lines = read_tsv(ART / "OL_417_LINE_RERENDER.tsv")
    n25 = read_tsv(ART / "N25_BOUNDARY_DECISIONS.tsv")
    adjacent = read_tsv(ART / "ADJACENT_OL_PAIRS.tsv")
    debts = read_tsv(ART / "V57_SIX_OL_DEBT_REVISIONS.tsv")
    v57 = read_tsv(ART / "V57_51_LINE_READER.tsv")
    v56 = read_tsv(V56_PATH)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    audit.check(len(cards) == 5, "five-layer reconciliation")
    card_by_layer = {row["layer"]: row for row in cards}
    audit.check(card_by_layer["BILATERAL_WORKING_TRANSLATION"]["value_de"] == "Grundansatz", "bilateral card concrete")
    audit.check(card_by_layer["BILATERAL_WORKING_TRANSLATION"]["scope"].startswith("374 positions"), "bilateral card scoped")
    audit.check(card_by_layer["MAJORITY_WORKING_TRANSLATION"]["value_de"] == "Grundansatz", "majority default concrete")
    audit.check(card_by_layer["MAJORITY_WORKING_TRANSLATION"]["scope"].startswith("64 positions"), "majority card scoped")
    audit.check("NOT_ALL_READERS" in card_by_layer["MAJORITY_WORKING_TRANSLATION"]["status"], "majority card not called universal")
    audit.check(card_by_layer["STRUCTURAL_META_GLOSS"]["value_de"] == LEGACY_GLOSS, "structural history retained separately")
    audit.check(card_by_layer["BOUNDARY_RENDERER"]["status"] == "LOCAL_COMPOUND_ONLY", "bound cards local")
    audit.check(card_by_layer["LOCAL_RIVAL_RENDERER"]["status"] == "NO_OL_EXPORT", "reader rivals do not export")

    audit.check(len(occurrences) == 463, "463 occurrence rows")
    keys = {(row["locus"], row["ordinal"]) for row in occurrences}
    audit.check(len(keys) == 463, "unique occurrence keys")
    audit.check(len({row["locus"] for row in occurrences}) == 417, "417 occurrence loci")
    audit.check(len({row["page"] for row in occurrences}) == 108, "108 occurrence pages")
    audit.check(all(not row["page"].lower().startswith("f84") for row in occurrences), "sealed pages absent")
    audit.check(Counter(row["reader_support"] for row in occurrences) == {
        "BOTH_EXACT": 374, "IT2A_ONLY_EXACT": 35, "RF1B_ONLY_EXACT": 29, "NEITHER_EXACT": 25,
    }, "BIRN distribution")
    audit.check(sum(row["it2a_operation"] == "EXACT" for row in occurrences) == 409, "IT2a exact count")
    audit.check(sum(row["rf1b_operation"] == "EXACT" for row in occurrences) == 403, "RF1b exact count")
    audit.check(sum(int(row["boundary_active"]) for row in occurrences) == 63, "63 boundary-active positions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" for row in occurrences) == 25, "25 neither-exact positions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" and row["boundary_active"] == "1" for row in occurrences) == 23, "23 N boundary positions")
    audit.check(sum(row["reader_support"] == "NEITHER_EXACT" and row["boundary_active"] == "0" for row in occurrences) == 2, "two N form conflicts")
    audit.check(Counter(row["semantic_decision"] for row in occurrences) == {
        "BILATERAL_PORTABLE_OL_BASE": 374,
        "MAJORITY_OL_BASE_WITH_READER_RIVAL": 64,
        "BOUND_OL_MATERIAL_COMPONENT": 19,
        "LOCAL_MATERIAL_READER_CONFLICT": 5,
        "LOCAL_OLY_ACTION_CONFLICT": 1,
    }, "semantic dispatch")
    audit.check(all(row["working_translation_de"] == "Grundansatz" for row in occurrences if row["reader_support"] != "NEITHER_EXACT"), "438 bilateral-or-majority defaults")
    audit.check(all(row["reader_rival_surface"] != "NONE" and row["reader_rival_de"] != "NONE" for row in occurrences if row["semantic_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL"), "64 explicit reader rivals")
    audit.check(all(LEGACY_GLOSS not in row["reader_rival_de"] for row in occurrences if row["semantic_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL"), "no majority rival reimports stale OL meta-gloss")
    audit.check(all(row["export_policy"] == "MAJORITY_DEFAULT__NOT_ALL_READERS" for row in occurrences if row["semantic_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL"), "majority never exported to all readers")
    audit.check(all(row["working_translation_de"] != "Grundansatz" for row in occurrences if row["reader_support"] == "NEITHER_EXACT"), "N cases never receive blind base card")
    audit.check(all(row["export_policy"] in {"LOCAL_COMPOUND_ONLY", "NO_OL_EXPORT"} for row in occurrences if row["reader_support"] == "NEITHER_EXACT"), "N export quarantine")
    audit.check(Counter(row["section"] for row in occurrences) == {"B": 193, "S": 117, "H": 85, "T": 42, "P": 22, "C": 4}, "section spread")
    audit.check(Counter(row["position"] for row in occurrences) == {"BOS": 31, "MEDIAL": 390, "EOS": 42}, "position spread")

    audit.check(len(lines) == 417, "417 rerender rows")
    audit.check(sum(int(row["ol_count"]) for row in lines) == 463, "line OL total")
    audit.check(sum(int(row["old_target_legacy_positions"]) for row in lines) == 463, "all targets inherited meta gloss")
    audit.check(sum(int(row["new_target_legacy_positions"]) for row in lines) == 0, "all target meta glosses removed")
    audit.check(sum(int(row["unrelated_legacy_positions"]) for row in lines) == 1, "one unrelated L debt preserved")
    audit.check(all(len(row["zl3b_line"].split()) == len(row["token_debt_dispatch_de"].split(" | ")) for row in lines), "417 token dispatch alignments")
    audit.check(all(len(row["span_aware_source_groups"].split(" | ")) == len(row["span_aware_render_de"].split(" · ")) for row in lines), "417 span-aware render alignments")
    audit.check(all(int(row["span_aware_segment_count"]) == len(row["span_aware_source_groups"].split(" | ")) for row in lines), "span counts exact")

    audit.check(len(n25) == 25, "25 boundary decision rows")
    audit.check({(row["locus"], row["ordinal"]) for row in n25} == {(row["locus"], row["ordinal"]) for row in occurrences if row["reader_support"] == "NEITHER_EXACT"}, "N25 exact key set")
    audit.check(sum(row["semantic_decision"] == "BOUND_OL_MATERIAL_COMPONENT" for row in n25) == 19, "19 bound material decisions")
    audit.check(sum(row["semantic_decision"] == "LOCAL_MATERIAL_READER_CONFLICT" for row in n25) == 5, "five material conflicts")
    audit.check(sum(row["semantic_decision"] == "LOCAL_OLY_ACTION_CONFLICT" for row in n25) == 1, "one action conflict")
    audit.check(all(row["evidence_type"] and row["composition"] and row["reader_scope"] and row["render_span_tokens"] for row in n25), "N25 provenance fields complete")
    lines_by_locus = {row["locus"]: row for row in lines}
    for row in n25:
        line = lines_by_locus[row["locus"]]
        groups = line["span_aware_source_groups"].split(" | ")
        renderings = line["span_aware_render_de"].split(" · ")
        group = row["render_span_tokens"].replace("|", "+")
        audit.check(groups.count(group) == 1, f"one source span {row['locus']}")
        audit.check(renderings[groups.index(group)] == row["working_translation_de"], f"one span rendering {row['locus']}")
    cheopol = next(row for row in n25 if row["locus"] == "f115r.1")
    audit.check(cheopol["ordinal"] == "6" and cheopol["it2a_render"] == "cheopolteeedy" and cheopol["rf1b_render"] == "cheopol", "cheopol bilateral bind")
    audit.check(cheopol["working_translation_de"] == "bis zur Mittelstufe getrockneter Pulverstoff", "cheopol powder render")
    oly = next(row for row in n25 if row["locus"] == "f78r.35")
    audit.check(oly["it2a_render"] == "oly" and oly["rf1b_operation"] == "FUZZY_MERGE_2" and oly["rf1b_render"] == "ly", "oly action boundary")
    audit.check(oly["working_translation_de"] == "abseihen", "oly concrete action")

    audit.check(len(adjacent) == 7, "seven adjacent pairs")
    audit.check(all(row["working_render_de"] == "zwei getrennte Grundansatz-Einträge" for row in adjacent), "adjacent repeat render")
    audit.check(all(row["nominal_scope_render_de"] == "zwei getrennte Grundansatz-Einträge" for row in adjacent), "nominal repeat render")
    action_pairs = [row for row in adjacent if row["selected_scope"] == "ACTION_ADDITION"]
    nominal_pairs = [row for row in adjacent if row["selected_scope"] == "NOMINAL_REGISTER"]
    audit.check(len(action_pairs) == 1 and action_pairs[0]["locus"] == "f81r.5", "one licensed adjacent action scope")
    audit.check(action_pairs[0]["action_scope_render_de"] == "Grundansatz in zwei Zugaben", "licensed action repeat render")
    audit.check(len(nominal_pairs) == 6 and all(row["action_scope_render_de"] == "NONE" for row in nominal_pairs), "six nominal pairs do not invent additions")
    audit.check(all(row["rule"] == "REPEAT_SAME_PORTABLE_CARD__CONTEXT_SELECTS_ENTRY_OR_ADDITION__DO_NOT_INVENT_SECOND_LEXEME_OR_MEASURE" for row in adjacent), "no repeat lexeme invention")

    audit.check(len(debts) == 6, "six V57 debt rows")
    debt_keys = {(row["locus"], row["ordinal"]) for row in debts}
    audit.check(debt_keys == {("f112r.36", "2"), ("f115r.1", "6"), ("f80r.17", "8"), ("f80v.35", "9"), ("f86v5.2", "9"), ("f86v6.4", "4")}, "six exact debt keys")
    audit.check(Counter(row["decision"] for row in debts) == {"BILATERAL_PORTABLE_OL_BASE": 4, "MAJORITY_OL_BASE_WITH_READER_RIVAL": 1, "LOCAL_BOUND_CHEOPOL": 1}, "four bilateral, one majority, one bound")
    audit.check(sum(row["render_mode"] == "MERGE_WITH_PREVIOUS" for row in debts) == 1, "one V57 merge")
    audit.check(all(LEGACY_GLOSS in row["before_literal_token_glosses_de"] for row in debts), "debt present before")
    audit.check(all(LEGACY_GLOSS not in row["after_literal_token_glosses_de"] for row in debts), "debt absent after")
    audit.check(all("Ansatz/Gut" not in row["after_aligned_line_de"] for row in debts), "aligned debt absent")
    audit.check(all("Ansatz/Gut" not in row["after_practical_translation_de"] for row in debts), "practical debt absent")
    audit.check("drei teile grundansatz" in next(row for row in debts if row["locus"] == "f86v6.4")["after_practical_translation_de"].lower(), "quantity III attaches to base")
    audit.check("bis zur Mittelstufe getrockneter Pulverstoff" in next(row for row in debts if row["locus"] == "f115r.1")["after_practical_translation_de"], "cheopol rendered once in prose")

    audit.check(len(v57) == len(v56) == 51, "51-line readers")
    audit.check(sum(int(row["token_count"]) for row in v57) == 479, "479 V57 tokens")
    audit.check(sum(int(row["v57_semantic_revisions"]) for row in v57) == 6, "six V57 revisions")
    audit.check(sum(int(row["v57_bound_compounds"]) for row in v57) == 1, "one V57 compound")
    audit.check(sum(int(row["residual_unknown_positions"]) for row in v57) == 0, "zero V57 unknowns")
    audit.check(sum(int(row["action_positions"]) for row in v57) == 86, "action count unchanged")
    audit.check(all(len(row["zl3b_line"].split()) == len(row["literal_token_glosses_de"].split(" | ")) for row in v57), "V57 literal token alignment")
    audit.check(all(len(row["zl3b_line"].split()) == len(row["aligned_line_de"].rstrip(".").split(" · ")) for row in v57), "V57 aligned line token alignment")
    audit.check(all(LEGACY_GLOSS not in row["literal_token_glosses_de"] for row in v57), "no V57 OL meta gloss")
    audit.check(all("Ansatz/Gut" not in row["aligned_line_de"] and "Ansatz/Gut" not in row["practical_translation_de"] for row in v57), "no V57 Ansatz/Gut")
    audit.check(all(not GENERIC.search(row["practical_translation_de"]) for row in v57), "no generic work filler")
    f80r17 = next(row for row in v57 if row["locus"] == "f80r.17")
    audit.check(f80r17["v57_ol_decision"] == "MAJORITY_OL_BASE_WITH_READER_RIVAL" and f80r17["v57_reader_support"] == "IT2A_ONLY_EXACT", "f80r.17 taxonomy retains one-reader support")
    audit.check("Pfund / Gewichtseinheit" in f80r17["review_note"], "f80r.17 exposes RF1b l rival")
    audit.check(f80r17["aligned_line_de"].split(" · ")[-1] == "eine Teilmenge abmessen", "f80r.17 aligned part measure")
    audit.check("gleichen Teil" not in f80r17["aligned_line_de"], "f80r.17 no unsupported equal part")
    f86v5 = next(row for row in v57 if row["locus"] == "f86v5.2")
    audit.check("kalt angesetzte Rohdroge" not in f86v5["practical_translation_de"], "f86v5 nominal segment does not invent setting action")
    f39 = next(row for row in occurrences if row["locus"] == "f39r.15" and row["ordinal"] == "6")
    audit.check(f39["rf1b_operation"] == "SPLIT_2" and f39["rf1b_render"] == "o|l", "f39r.15 preserves RF1b split")
    audit.check(f39["reader_rival_de"] == "Ansatzwasser | Pfund / Gewichtseinheit", "f39r.15 renders both split rivals")
    f115 = next(row for row in v57 if row["locus"] == "f115r.1")
    audit.check(f115["literal_token_glosses_de"].split(" | ")[4:6] == ["bis zur Mittelstufe getrocknet", "Pulverstoff"], "cheopol token components do not duplicate")
    audit.check(f115["aligned_line_de"].split(" · ")[4:6] == ["bis zur Mittelstufe getrocknet", "Pulverstoff"], "cheopol aligned components do not duplicate")
    v56_by_locus = {row["locus"]: row for row in v56}
    for row in v57:
        old = v56_by_locus[row["locus"]]
        if row["locus"] not in {key[0] for key in debt_keys}:
            for field in v56[0].keys():
                audit.check(row[field] == old[field], f"unchanged inherited field {row['locus']}:{field}")

    audit.check(result["status"] == "PASS_374_BILATERAL_OL_BASE__64_MAJORITY_WITH_RIVAL__25_OVERRIDES__V57_ZERO_OL_DEBT", "result status")
    audit.check(result["basis"]["cross_guard"] == {"selected": 417, "skipped_forbidden": 98, "skipped_not_allowed": 4871}, "guard statistics")
    audit.check(result["reader_support"] == {"BOTH_EXACT": 374, "IT2A_ONLY_EXACT": 35, "NEITHER_EXACT": 25, "RF1B_ONLY_EXACT": 29}, "result reader support")
    audit.check(result["boundary"]["active_positions"] == 63 and result["boundary"]["neither_exact_boundary_positions"] == 23 and result["boundary"]["neither_exact_form_conflicts"] == 2, "result boundary counts")
    audit.check(result["v57_reader"]["legacy_generic_positions_before"] == 6, "result six old debts")
    audit.check(result["v57_reader"]["legacy_generic_positions_after"] == 0, "result zero new debts")
    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"result hash {name}")

    private_home = "/" + "home" + "/" + "anon"
    private_key_marker = "BEGIN " + "PRIVATE KEY"
    ssh_key_marker = "BEGIN " + "OPENSSH PRIVATE KEY"
    for path in [*EXP.glob("*.md"), *EXP.glob("*.json"), *EXP.glob("src/*"), *EXP.glob("artifacts/*")]:
        if not path.is_file() or path.name == "VALIDATION.json":
            continue
        text = path.read_text(encoding="utf-8")
        audit.check(private_home not in text and private_key_marker not in text and ssh_key_marker not in text, f"privacy scan {path.name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuild_files": len(artifact_names),
        "ol_positions": len(occurrences),
        "ol_loci": len(lines),
        "n_boundary_decisions": len(n25),
        "v57_semantic_revisions": len(debts),
        "sealed_pages_present": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
