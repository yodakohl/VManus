#!/usr/bin/env python3
"""Validate and byte-replay GDT633."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt633_cth_interfix_semantic_contrasts"
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V9 = ROOT / "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/WORKING_DICTIONARY_V9.tsv"

GENERATED = (
    ART / "PAGE_ALLOWLIST.tsv",
    ART / "OUTER_LITERAL_E_RUN_OCCURRENCES.tsv",
    ART / "OUTER_LITERAL_E_RUN_LATTICE.tsv",
    ART / "OUTER_E_FIXED_BODY_LADDERS.tsv",
    ART / "EE_RIVAL_CONTEXTS.tsv",
    ART / "LITERAL_E_RUN_BACKGROUND.tsv",
    ART / "INNER_CTH_E_RUN_LADDERS.tsv",
    ART / "INNER_E_PAGE_COEXISTENCE.tsv",
    ART / "INNER_E_SHARED_CONTEXTS.tsv",
    ART / "O_HEAD_DISTRIBUTION.tsv",
    ART / "O_CTH_SAME_REMAINDER_CONTEXTS.tsv",
    ART / "O_CTH_SHARED_CONTEXTS.tsv",
    ART / "E_BINDING_VS_HEATING.tsv",
    ART / "CONTROLLED_INTERFIX_TYPE_PAIRS.tsv",
    ART / "SAME_PAGE_MICROEDITIONS.tsv",
    ART / "CONCRETE_TRANSLATIONS_V5.tsv",
    ART / "ATOMIC_MEANING_CANDIDATES.tsv",
    ART / "CANDIDATE_SCOREBOARD.tsv",
    ART / "PREDICTION_DECK.tsv",
    ART / "WORKING_DICTIONARY_V10.tsv",
    RESULT,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(all(path.is_file() for path in GENERATED), "all generated artifacts exist before replay")
    before = {path: path.read_bytes() for path in GENERATED}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False,
    )
    check(completed.returncode == 0, "builder exits zero")
    expected_summary = (
        "GDT633 built: outer=257/50 ladders=13 ee=2 e_background=397 "
        "inner_contexts=18 o_shared=12 pairs=28 translations=268/55 dictionary=76"
    )
    check(completed.stdout.strip() == expected_summary, "builder summary")
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT633_CTH_INTERFIX_SEMANTIC_CONTRASTS_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT633", "result experiment id")
    check(result["status"] == "WORKING_E_ATTRIBUTIVE_O_PREPARATION_DEFAULTS__INNER_E_FORM_STAGES", "result status")
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(result["content_sha256"] == canonical_hash(result_core), "canonical result hash")
    check(result["guard"] == {
        "allowed_pages": 179,
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }, "guarded source scope")
    expected_inputs = {
        "transcription/voynich_zl3b_tokens.tsv",
        "transcription/voynich_cross_transcription_lines.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/PAGE_ALLOWLIST.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/INTERFIX_FAMILY_OCCURRENCES.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/INTERFIX_QUALITY_DEGREE_CONTACTS.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/WORKING_DICTIONARY_V9.tsv",
        "experiments/yolo/gdt632_cth_interfix_lattice/src/run.py",
        "experiments/yolo/gdt632_cth_interfix_lattice/artifacts/RESULT.json",
        "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/RESULT.json",
        "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/E_LENGTH_SERIES.tsv",
    }
    check(set(result["inputs"]) == expected_inputs, "complete inherited input set")
    for path, digest in result["inputs"].items():
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    for path, digest in result["outputs"].items():
        check(sha256(ROOT / path) == digest, f"output hash {path}")
    check(set(result["outputs"]) == {rel(path) for path in GENERATED if path != RESULT}, "result binds every generated evidence file")

    allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    check(len(allow) == 179 and len({row["page"] for row in allow}) == 179, "179-page allow-list")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in allow), "allow-list excludes held and sealed folios")

    outer = read_tsv(ART / "OUTER_LITERAL_E_RUN_OCCURRENCES.tsv")
    check(len(outer) == 257 and len({row["surface"] for row in outer}) == 50, "257-token 50-type extended outer family")
    check(len({row["page"] for row in outer}) == 104, "extended outer family spans 104 pages")
    check(Counter(row["quality_prefix"] for row in outer) == Counter({"CH": 182, "SH": 75}), "outer quality-prefix partition")
    check(Counter(row["outer_e_level"] for row in outer) == Counter({"0": 190, "1": 65, "2": 2}), "outer E-level partition")
    check(Counter(row["o_slot"] for row in outer) == Counter({"0": 211, "1": 46}), "outer O-slot partition")
    check(sum(int(row["triple_exact_token_stable"]) for row in outer) == 229, "229 outer occurrences triple exact")
    check(sum(int(row["triple_boundary_normalized"]) for row in outer) == 233, "233 outer occurrences boundary normalized")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in outer), "outer occurrences exclude held and sealed folios")
    outer_re = re.compile(r"^(ch|sh)(e*)(o?)cth(.*)$")
    for row in outer:
        match = outer_re.fullmatch(row["surface"])
        check(match is not None, f"literal outer parse exists {row['occurrence_id']}")
        assert match is not None
        check(row["quality_prefix"] == {"ch": "CH", "sh": "SH"}[match.group(1)], f"quality parse {row['occurrence_id']}")
        check(int(row["outer_e_level"]) == len(match.group(2)), f"outer E parse {row['occurrence_id']}")
        check(int(row["o_slot"]) == int(bool(match.group(3))), f"O-slot parse {row['occurrence_id']}")
        check(row["remainder"] == (match.group(4) or "BARE"), f"inner remainder parse {row['occurrence_id']}")
        if row["o_slot"] == "1":
            check("zubereitung" in row["working_translation_de"].lower(), f"O preparation translation {row['occurrence_id']}")
        if row["outer_e_level"] == "2":
            check("erweiterte Bindungsstufe 2" in row["working_translation_de"], f"EE extended-binding translation {row['occurrence_id']}")
        if row["remainder"] == "ey":
            check(row["inner_form_default_de"] == "FORM_I" and "Form I" in row["working_translation_de"], f"inner ey form I {row['occurrence_id']}")
        if row["remainder"] == "eey":
            check(row["inner_form_default_de"] == "FORM_II" and "Form II" in row["working_translation_de"], f"inner eey form II {row['occurrence_id']}")

    lattice = {(int(row["outer_e_level"]), int(row["o_slot"])): row for row in read_tsv(ART / "OUTER_LITERAL_E_RUN_LATTICE.tsv")}
    expected_lattice = {
        (0, 0): (154, 25, 81, 118, 36), (0, 1): (36, 8, 32, 23, 13),
        (1, 0): (55, 10, 22, 34, 21), (1, 1): (10, 5, 9, 6, 4),
        (2, 0): (2, 2, 2, 1, 1), (2, 1): (0, 0, 0, 0, 0),
    }
    check(set(lattice) == set(expected_lattice), "complete E0-E2 by O0-O1 lattice")
    for key, expected in expected_lattice.items():
        observed = tuple(int(lattice[key][field]) for field in ("occurrences", "types", "pages", "ch_occurrences", "sh_occurrences"))
        check(observed == expected, f"outer lattice cell E{key[0]} O{key[1]}")

    ladders = read_tsv(ART / "OUTER_E_FIXED_BODY_LADDERS.tsv")
    check(len(ladders) == 13, "thirteen fixed-body outer-E ladders")
    check(Counter(row["observed_e_levels"] for row in ladders) == Counter({"0|1": 11, "0|1|2": 2}), "outer-E ladder level partition")
    full_ladders = {(row["quality_prefix"], row["o_slot"], row["remainder"]): row for row in ladders if row["observed_e_levels"] == "0|1|2"}
    check(set(full_ladders) == {("CH", "0", "y"), ("SH", "0", "ey")}, "two exact full outer-E ladders")
    check((full_ladders[("CH", "0", "y")]["e0_occurrences"], full_ladders[("CH", "0", "y")]["e1_occurrences"], full_ladders[("CH", "0", "y")]["e2_occurrences"]) == ("75", "26", "1"), "CH-y ladder counts")
    check((full_ladders[("SH", "0", "ey")]["e0_occurrences"], full_ladders[("SH", "0", "ey")]["e1_occurrences"], full_ladders[("SH", "0", "ey")]["e2_occurrences"]) == ("4", "1", "1"), "SH-ey ladder counts")

    ee = read_tsv(ART / "EE_RIVAL_CONTEXTS.tsv")
    check(len(ee) == 2 and all(row["triple_exact_token_stable"] == "1" for row in ee), "two triple-exact EE rivals")
    ee_by_surface = {row["surface"]: row for row in ee}
    check(set(ee_by_surface) == {"cheecthy", "sheecthey"}, "exact EE rival surfaces")
    check((ee_by_surface["cheecthy"]["locus"], ee_by_surface["cheecthy"]["position"], ee_by_surface["cheecthy"]["section"], ee_by_surface["cheecthy"]["language"], ee_by_surface["cheecthy"]["hand"]) == ("f29r.1", "LAST", "H", "A", "1"), "cheecthy provenance and position")
    check((ee_by_surface["sheecthey"]["locus"], ee_by_surface["sheecthey"]["position"], ee_by_surface["sheecthey"]["section"], ee_by_surface["sheecthey"]["language"], ee_by_surface["sheecthey"]["hand"]) == ("f82v.36", "MIDDLE", "B", "B", "2"), "sheecthey provenance and position")
    check((ee_by_surface["cheecthy"]["e0_counterpart"], ee_by_surface["cheecthy"]["e1_counterpart"]) == ("chcthy", "checthy"), "cheecthy shorter counterparts")
    check((ee_by_surface["sheecthey"]["e0_counterpart"], ee_by_surface["sheecthey"]["e1_counterpart"]) == ("shcthey", "shecthey"), "sheecthey shorter counterparts")

    background = read_tsv(ART / "LITERAL_E_RUN_BACKGROUND.tsv")
    check(len(background) == 397, "397 multi-length literal-E background families")
    check(sum(int(row["types"]) for row in background) == 871, "871 types in literal-E background")
    check(sum(int(row["occurrences"]) for row in background) == 8759, "8759 occurrences in literal-E background")
    check(sum(int(row["has_e_ee"]) for row in background) == 365, "365 background e-ee families")
    check(sum(int(row["has_e_ee_eee"]) for row in background) == 73, "73 background e-ee-eee families")
    check(sum(int(row["has_e_through_eeee"]) for row in background) == 3, "three background four-level families")
    check(all(int(row["distinct_lengths"]) >= 2 and int(row["types"]) == int(row["distinct_lengths"]) for row in background), "background rows are genuine multi-length families")
    check(any(row["skeleton"] == "ch<E>cthy" and row["surfaces_by_length"] == "1:checthy|2:cheecthy" for row in background), "target CH EE ladder occurs in manuscript background")

    inner = {(row["head_prefix"], int(row["inner_e_level"])): row for row in read_tsv(ART / "INNER_CTH_E_RUN_LADDERS.tsv")}
    expected_inner = {
        ("CTH", 0): ("cthy", 92, 50, 90, 85, "ATTESTED"),
        ("CTH", 1): ("cthey", 38, 33, 29, 32, "ATTESTED"),
        ("CTH", 2): ("ctheey", 10, 9, 6, 9, "ATTESTED"),
        ("CTH", 3): ("ctheeey", 0, 0, 0, 0, "PREDICTED_GAP"),
        ("O_CTH", 0): ("octhy", 9, 9, 3, 9, "ATTESTED"),
        ("O_CTH", 1): ("octhey", 3, 3, 1, 2, "ATTESTED"),
        ("O_CTH", 2): ("octheey", 0, 0, 0, 0, "PREDICTED_GAP"),
        ("O_CTH", 3): ("octheeey", 0, 0, 0, 0, "UNOBSERVED_CONTROL"),
    }
    check(set(inner) == set(expected_inner), "complete inner CTH/O-CTH E-run table")
    for key, expected in expected_inner.items():
        row = inner[key]
        observed = (row["surface"], *(int(row[field]) for field in ("occurrences", "pages", "herbal_occurrences", "triple_exact_occurrences")), row["observation_status"])
        check(observed == expected, f"inner ladder {key[0]} level {key[1]}")
    inner_pages = read_tsv(ART / "INNER_E_PAGE_COEXISTENCE.tsv")
    check(len(inner_pages) == 13 and Counter(row["head_prefix"] for row in inner_pages) == Counter({"CTH": 12, "O_CTH": 1}), "inner-E page coexistence partition")
    check({row["page"] for row in inner_pages if row["head_prefix"] == "CTH" and row["inner_e_levels"] == "0|1|2"} == {"f21r", "f87v"}, "two pages carry all three naked CTH stages")
    inner_contexts = read_tsv(ART / "INNER_E_SHARED_CONTEXTS.tsv")
    check(len(inner_contexts) == 18, "eighteen shared one-sided inner-E contexts")
    check(Counter(row["inner_e_levels"] for row in inner_contexts) == Counter({"0|1": 10, "0|2": 5, "0|1|2": 3}), "inner-E context level partition")

    heads = {row["head_prefix"]: row for row in read_tsv(ART / "O_HEAD_DISTRIBUTION.tsv")}
    check((heads["CTH"]["occurrences"], heads["CTH"]["types"], heads["CTH"]["pages"], heads["CTH"]["herbal_occurrences"]) == ("408", "69", "125", "347"), "naked CTH head distribution")
    check((heads["O_CTH"]["occurrences"], heads["O_CTH"]["types"], heads["O_CTH"]["pages"], heads["O_CTH"]["herbal_occurrences"]) == ("32", "16", "27", "15"), "naked O-CTH head distribution")
    o_same = read_tsv(ART / "O_CTH_SAME_REMAINDER_CONTEXTS.tsv")
    check(len(o_same) == 32, "one same-remainder row per naked O-CTH occurrence")
    covered_o = [row for row in o_same if int(row["cth_counterpart_occurrences"]) > 0]
    check(len(covered_o) == 29 and len({row["o_surface"] for row in covered_o}) == 13, "29 O tokens and 13 O types have naked CTH counterparts")
    check(len({row["page"] for row in o_same if row["same_page_counterpart"] == "1"}) == 7, "seven pages carry same-remainder CTH and O-CTH heads")
    o_shared = read_tsv(ART / "O_CTH_SHARED_CONTEXTS.tsv")
    check(len(o_shared) == 12 and all(int(row["cth_occurrences"]) and int(row["octh_occurrences"]) for row in o_shared), "twelve exact one-sided CTH/O-CTH contexts")

    heating = read_tsv(ART / "E_BINDING_VS_HEATING.tsv")
    check(len(heating) == 12 and Counter(row["scope"] for row in heating) == Counter({"GLOBAL": 4, "SECTION_B": 4, "SECTION_S": 4}), "twelve occurrence-normalized heating rows")
    global_heat = {(int(row["outer_e_slot"]), int(row["o_slot"])): row for row in heating if row["scope"] == "GLOBAL"}
    expected_heat = {
        (0, 0): (154, 38, 17, 24, 12), (1, 0): (55, 12, 1, 10, 0),
        (0, 1): (36, 3, 4, 1, 2), (1, 1): (10, 1, 2, 1, 0),
    }
    for key, expected in expected_heat.items():
        row = global_heat[key]
        observed = tuple(int(row[field]) for field in ("occurrences", "hot_occurrences", "cold_occurrences", "immediate_hot_occurrences", "immediate_cold_occurrences"))
        check(observed == expected, f"global occurrence-normalized heating E{key[0]} O{key[1]}")
        check(row["hot_share"] == f"{expected[1] / expected[0]:.6f}" and row["cold_share"] == f"{expected[2] / expected[0]:.6f}", f"heating rate arithmetic E{key[0]} O{key[1]}")
    check(12 / 55 < 38 / 154, "no-O E is not hot-enriched after occurrence normalization")
    check(global_heat[(1, 0)]["cold_occurrences"] == "1" and global_heat[(1, 0)]["immediate_cold_occurrences"] == "0", "cold-exclusion heating rival remains explicit")

    pairs = read_tsv(ART / "CONTROLLED_INTERFIX_TYPE_PAIRS.tsv")
    check(len(pairs) == 28 and Counter(row["axis"] for row in pairs) == Counter({"OUTER_E_INSERTION": 13, "O_INSERTION": 10, "E_VS_O": 5}), "28 controlled interfix pairs")
    for row in pairs:
        left = outer_re.fullmatch(row["left_surface"])
        right = outer_re.fullmatch(row["right_surface"])
        check(left is not None and right is not None, f"controlled pair parses {row['pair_id']}")
        assert left is not None and right is not None
        check(left.group(1) == right.group(1) and left.group(4) == right.group(4), f"controlled pair fixes quality and remainder {row['pair_id']}")
        if row["axis"] == "OUTER_E_INSERTION":
            check(len(right.group(2)) == len(left.group(2)) + 1 and left.group(3) == right.group(3), f"E pair changes only outer E {row['pair_id']}")
        elif row["axis"] == "O_INSERTION":
            check(left.group(2) == right.group(2) and left.group(3) == "" and right.group(3) == "o", f"O pair changes only O {row['pair_id']}")
        else:
            check((len(left.group(2)), left.group(3), len(right.group(2)), right.group(3)) == (1, "", 0, "o"), f"E-vs-O pair is directionally fixed {row['pair_id']}")

    micro = read_tsv(ART / "SAME_PAGE_MICROEDITIONS.tsv")
    check(len(micro) == 8, "eight concrete microeditions")
    check({row["locus"] for row in micro} == {"f29r.1", "f82v.36", "f80r.18", "f80v.10", "f20v.10", "f22v.15", "f114v.33", "f85r1.21"}, "exact microedition loci")
    check("vorhergesagt, nicht beobachtet" in next(row["residual_policy_de"] for row in micro if row["locus"] == "f114v.33"), "f114 octheey remains explicitly predicted")

    translations = read_tsv(ART / "CONCRETE_TRANSLATIONS_V5.tsv")
    check(len(translations) == 268 and len({row["normalized_surface"] for row in translations}) == 55, "268 translations in 55 normalized types")
    check(Counter(row["source_kind"] for row in translations) == Counter({"FUSED": 257, "ALL_READER_SEPARATED": 7, "READER_BOUNDARY_BRIDGE": 4}), "translation source partition")
    check(Counter(row["observation_status"] for row in translations) == Counter({"OBSERVED_FUSED": 257, "OBSERVED_BOUNDARY_REALIZATION": 11}), "translation observation-status partition")
    fused_translations = {row["source_id"]: row for row in translations if row["source_kind"] == "FUSED"}
    check(set(fused_translations) == {row["occurrence_id"] for row in outer}, "every fused occurrence has one translation")
    for source in outer:
        translated = fused_translations[source["occurrence_id"]]
        check(translated["normalized_surface"] == source["surface"] and translated["working_translation_de"] == source["working_translation_de"], f"fused translation replay {source['occurrence_id']}")
    prediction_surfaces = {"octheey", "cheeecthy", "sheeecthey", "cheeocthy", "sheeocthy", "ctheeey"}
    check(not prediction_surfaces & {row["normalized_surface"] for row in translations}, "predictions never enter observed translations")
    check(all("Füllprosa" in row["residual_policy_de"] or "Wortgrenze" in row["residual_policy_de"] for row in translations), "translation residual policy forbids invented prose")

    atoms = read_tsv(ART / "ATOMIC_MEANING_CANDIDATES.tsv")
    check(len(atoms) == 9, "nine atomic meaning candidates")
    atom_by_unit = {row["visible_unit"]: row for row in atoms}
    check(set(atom_by_unit) == {"ch", "sh", "äußeres e", "äußeres ee", "cth", "o+cth", "inneres y", "inneres ey", "inneres eey"}, "complete atomic slot dictionary")
    check(atom_by_unit["äußeres e"]["slot"] == "BINDUNG" and "attributive Bindung" in atom_by_unit["äußeres e"]["primary_default_de"], "outer e is binding default")
    check(atom_by_unit["äußeres ee"]["slot"] == "BINDUNGSSTUFE" and "erweiterte" in atom_by_unit["äußeres ee"]["primary_default_de"], "outer ee is extended binding")
    check(atom_by_unit["o+cth"]["slot"] == "ABGELEITETER_MATERIALKOPF" and "Zubereitung/Ansatz" in atom_by_unit["o+cth"]["primary_default_de"], "O-CTH is preparation default")
    check(atom_by_unit["inneres ey"]["primary_default_de"].endswith("form I") and atom_by_unit["inneres eey"]["primary_default_de"].endswith("form II"), "inner ey/eey form stages stay distinct")
    check(not any(re.search(r"\b(?:Wasser|Wein|Öl|Saft)\b", row["primary_default_de"], re.IGNORECASE) for row in atoms), "no specific medium promoted to an atomic default")

    scoreboard = read_tsv(ART / "CANDIDATE_SCOREBOARD.tsv")
    check(len(scoreboard) == 5 and [row["rank"] for row in scoreboard] == ["1", "2", "3", "4", "5"], "five ranked semantic models")
    check(scoreboard[0]["model"] == "E_ATTRIBUTIVE__O_PREPARATION" and scoreboard[0]["disposition"] == "PRIMARY_WORKING_TRANSLATION", "binding-preparation model ranks first")
    check(scoreboard[1]["disposition"] == "LIVE_CONCRETE_RIVAL" and "nicht heiß-angereichert" in scoreboard[1]["counterevidence"], "heating/grade rival stays live but normalized")
    check(scoreboard[3]["model"] == "O_SPECIFIC_MEDIUM" and scoreboard[3]["disposition"] == "TOO_NARROW_NOW", "specific medium remains too narrow")
    check(scoreboard[4]["disposition"] == "REJECTED_AS_PRIMARY", "independent whole words rejected as primary")

    predictions = read_tsv(ART / "PREDICTION_DECK.tsv")
    check(len(predictions) == 6 and {row["surface"] for row in predictions} == prediction_surfaces, "six exact structural predictions")
    check(all(row["observed_allowed_tokens"] == "0" and row["status"] == "PREDICTED_NOT_OBSERVED" for row in predictions), "all predictions are unobserved in the allowed deck")
    octheey = next(row for row in predictions if row["surface"] == "octheey")
    check(octheey["structural_parse"] == "o+cth+eey" and octheey["working_translation_de"] == "CTH-Zubereitung, Form II", "octheey prediction parse and translation")

    old_dictionary = read_tsv(V9)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V10.tsv")
    check(len(old_dictionary) == 67 and len(dictionary) == 76, "V10 contains 67 inherited plus nine new entries")
    revised_entries = {
        "e nach ch/sh", "o+cth+R", "ch/sh+e?+[o?+cth+R]", "che-", "she-", "cho-", "sho-", "cheo-", "sheo-",
        "checthy", "shecthy", "chocthy", "shocthy", "cheocthy", "sheocthy",
    }
    check(sum(row["status"] == "REVISED_V10_CONCRETE_DEFAULT" for row in dictionary[:67]) == 15, "fifteen inherited entries receive concrete revisions")
    for old, new in zip(old_dictionary, dictionary[:67]):
        check(old["entry"] == new["entry"], f"dictionary order retained {old['entry']}")
        if old["entry"] not in revised_entries:
            check(old == new, f"unrevised V9 row retained {old['entry']}")
    additions = {row["entry"]: row for row in dictionary[67:]}
    check(set(additions) == {"ee nach ch/sh", "cth+y", "cth+ey", "cth+eey", "octhy", "octhey", "octheey", "cheecthy", "sheecthey"}, "nine exact V10 additions")
    check(additions["octheey"]["status"] == "NEW_V10_PREDICTED_ENTRY" and "VORHERSAGE" in additions["octheey"]["context_rule"], "dictionary marks octheey as prediction")
    check(additions["sheecthey"]["composition"] == "sh+ee+cth+ey", "dictionary separates outer EE from inner EY")
    check("Zubereitung/Ansatz" in additions["octhy"]["working_meaning_de"] and "Form I" in additions["octhey"]["working_meaning_de"] and "Form II" in additions["octheey"]["working_meaning_de"], "dictionary O-CTH form ladder is coherent")

    check(result["outer_e_o"] == {
        "occurrences": 257, "types": 50, "pages": 104,
        "lattice": {
            "E0_O0": {"occurrences": 154, "types": 25, "pages": 81},
            "E0_O1": {"occurrences": 36, "types": 8, "pages": 32},
            "E1_O0": {"occurrences": 55, "types": 10, "pages": 22},
            "E1_O1": {"occurrences": 10, "types": 5, "pages": 9},
            "E2_O0": {"occurrences": 2, "types": 2, "pages": 2},
            "E2_O1": {"occurrences": 0, "types": 0, "pages": 0},
        },
        "fixed_body_e_ladders": 13, "complete_e0_e1_e2_ladders": 2,
        "ee_occurrences": 2, "ee_types": 2,
        "controlled_pair_counts": {"E_VS_O": 5, "OUTER_E_INSERTION": 13, "O_INSERTION": 10},
    }, "result outer E/O census")
    check(result["literal_e_background"] == {
        "multi_length_families": 397, "types": 871, "occurrences": 8759,
        "families_with_e_ee": 365, "families_with_e_ee_eee": 73, "families_with_e_through_eeee": 3,
    }, "result literal-E background")
    check(result["inner_e"] == {
        "counts": {"cthy": 92, "cthey": 38, "ctheey": 10, "ctheeey": 0, "octhy": 9, "octhey": 3, "octheey": 0, "octheeey": 0},
        "cth_pages_with_multiple_levels": 12, "cth_pages_with_all_three_levels": 2,
        "shared_one_sided_contexts": 18, "shared_contexts_all_three_levels": 3,
        "octheey": "PREDICTED_NOT_OBSERVED",
    }, "result inner-E ladder")
    check(result["o_head"] == {
        "cth": {"occurrences": 408, "types": 69, "pages": 125, "herbal_occurrences": 347},
        "octh": {"occurrences": 32, "types": 16, "pages": 27, "herbal_occurrences": 15},
        "o_occurrences_with_cth_counterpart": 29, "o_types_with_cth_counterpart": 13,
        "pages_with_same_remainder_both_heads": 7, "shared_one_sided_contexts": 12,
    }, "result O-head derivation evidence")
    check(result["e_heating_occurrence_normalized"] == {
        f"E{e}_O{o}": {
            "occurrences": values[0], "hot_occurrences": values[1], "cold_occurrences": values[2],
            "immediate_hot_occurrences": values[3], "immediate_cold_occurrences": values[4],
        }
        for (e, o), values in expected_heat.items()
    }, "result occurrence-normalized heating table")
    check(result["translations"] == {"expressions": 268, "normalized_types": 55, "microeditions": 8, "unknown_neighbor_filler_added": 0}, "result translation coverage")
    check(result["working_dictionary"] == {"entries": 76, "inherited_v9_entries": 67, "revised_v9_entries": 15, "new_v10_entries": 9}, "result dictionary summary")
    check(result["predictions"] == {"rows": 6, "observed_allowed": 0, "primary": "octheey"}, "result prediction summary")
    check(result["working_semantics"]["specific_medium"] == "NOT_LICENSED", "result licenses no specific medium")
    check("predicted and unobserved" in result["claim_boundary"], "claim boundary keeps octheey unobserved")

    filler_pattern = re.compile(r"Arbeitsgut|Arbeitsschritt|ausf(?:ü|ue)hren|weiterleiten|leite\s+weiter", re.IGNORECASE)
    semantic_text = [row["working_translation_de"] for row in translations]
    semantic_text.extend(row["working_translation_de"] for row in micro)
    semantic_text.extend(row["working_meaning_de"] for row in dictionary)
    check(not any(filler_pattern.search(value) for value in semantic_text), "no generic filler pseudo-translation")

    privacy_pattern = re.compile(
        "/" + r"home/|/" + r"tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|AKIA[0-9A-Z]{16}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|password\s*[=:]|api[_-]?key\s*[=:]|secret\s*[=:]",
        re.IGNORECASE,
    )
    required = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json",
        ART / "README.md", *GENERATED, RUN, BASE / "src/validate.py",
    )
    for path in required:
        check(path.is_file(), f"required file {rel(path)}")
        check(not privacy_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {rel(path)}")

    payload = {
        "schema": "GDT633_VALIDATION_V1", "experiment_id": "GDT633", "status": "PASS",
        "check_count": len(checks), "checks": checks, "result_sha256": sha256(RESULT),
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
