#!/usr/bin/env python3
"""Build GDT658: four concrete exact-whole residual cards and V35."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt658_four_residual_concrete_completion")
ART = ROOT / BASE_REL / "artifacts"
G657 = Path("experiments/yolo/gdt657_multi_quality_al_shell_order")
G635_REPORT = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G640_REPORT = Path("experiments/yolo/gdt640_downstream_component_prediction/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt657_builder_for_gdt658", ROOT / G657 / "src/run.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT657 builder")
g657 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g657)

TOKENS_REL = g657.TOKENS_REL
CROSS_REL = g657.CROSS_REL
COVERAGE_FIELDS = g657.COVERAGE_FIELDS
ONE_FIELDS = g657.ONE_FIELDS
STATUS = "PASS_4_RESIDUAL_CONCRETE_WHOLES__V35"

GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)


def card(surface: str, mode: str, meaning: str, composition: str, rival: str) -> dict[str, str]:
    return {
        "surface": surface,
        "mode": mode,
        "working_meaning_de": meaning,
        "composition": composition,
        "rival_de": rival,
    }


TARGET_SPECS = (
    card(
        "otam",
        "EXACT_CONTEXTUAL_WHOLE",
        "ein Maß kalten Ansatzes",
        "O_PREP+T_COLD+AM_MEASURE_I",
        "kalte Dosis I oder gelerntes OTAM-Ganzwort",
    ),
    card(
        "shedefam",
        "READER_WARNING_BOUND_F_WHOLE",
        "ein Maß eingeweichter Blütendroge",
        "SHEDE_LOCAL_MOIST_SHELL+F_BOUND_FLOWER_DRUG_HEAD+AM_MEASURE_I",
        "angefeuchtet als vorsichtiger Rivale; Frucht-, Blatt- oder opakes F; gelerntes SHEDEFAM-Ganzwort",
    ),
    card(
        "schos",
        "EXACT_TWO_SLOTS_S_WHOLE",
        "trockene Arzneimischung aus Samen",
        "S_SEED_HEAD+CHO_DRY_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD",
        "Salz statt Samen; terminales Form-/Sorten-S oder gelerntes SCHOS-Ganzwort",
    ),
    card(
        "chokcheo",
        "EXACT_NESTED_PREPARATION_WHOLE",
        "Trockenansatz aus heißem Trockenpräparat",
        "CHO_DRY_PREPARATION+K_HOT+CHEO_DRY_PREPARED",
        "alternativer innerer Schnitt oder gelerntes CHOKCHEO-Ganzwort",
    ),
)
TARGET_BY_SURFACE = {row["surface"]: row for row in TARGET_SPECS}
EXPECTED_TARGET_COUNTS = {
    "otam": (44, 43, 34, 39, 39),
    "shedefam": (1, 1, 1, 0, 0),
    "schos": (1, 1, 1, 1, 1),
    "chokcheo": (1, 1, 1, 1, 1),
}
WARNING_SURFACES = {"shedefam"}

AM_FAMILY = (
    ("kam", "K_HOT+AM_MEASURE_I", "heiß, Maßform I", 7, 7, 7, 1),
    ("tam", "T_COLD+AM_MEASURE_I", "kalt, Maßform I", 6, 6, 6, 3),
    ("okam", "O_PREP+K_HOT+AM_MEASURE_I", "heißer Ansatz, Maßform I", 27, 27, 24, 17),
    ("otam", "O_PREP+T_COLD+AM_MEASURE_I", "ein Maß kalten Ansatzes", 44, 43, 34, 39),
    ("qokam", "QO_SCOPE+K_HOT+AM_MEASURE_I", "heiß im qo-Rahmen, Maßform I", 25, 25, 21, 22),
    ("qotam", "QO_SCOPE+T_COLD+AM_MEASURE_I", "kalt im qo-Rahmen, Maßform I", 11, 11, 9, 10),
    ("cham", "CH_DRY+AM_MEASURE_I", "trocken, Maßform I", 15, 15, 13, 15),
    ("sham", "SH_MOIST+AM_MEASURE_I", "feucht, Maßform I", 6, 6, 5, 6),
)

STRONG_F_BODIES = (
    "aiir", "ar", "chdy", "chedy", "cheey", "chey", "chody", "chol", "chor", "ol", "olchey", "shedy",
)
COMPLETE_F_GRID_BODIES = {"ar", "chdy", "chedy", "cheey", "chey", "chol", "ol", "shedy"}
F_HEADS = (
    ("p", "P_PULVIS"),
    ("s", "S_SEMEN"),
    ("r", "R_RADIX"),
    ("l", "L_LIGNUM"),
    ("f", "F_BOUND_DRUG_HEAD"),
)

KCHEO_EXPECTED = {
    "cheokcheo": (1, 1, 1, 1),
    "chokcheo": (1, 1, 1, 1),
    "kcheo": (3, 3, 3, 3),
    "lkcheo": (1, 1, 1, 1),
    "otcheo": (1, 1, 1, 1),
    "qokcheo": (2, 2, 2, 2),
    "qotcheo": (4, 3, 4, 4),
    "tcheo": (5, 5, 5, 5),
}
KCHEO_PARSES = {
    "cheokcheo": "CHEO_DRY_PREPARED+K_HOT+CHEO_DRY_PREPARED",
    "chokcheo": "CHO_DRY_PREPARATION+K_HOT+CHEO_DRY_PREPARED",
    "kcheo": "K_HOT+CHEO_DRY_PREPARED",
    "lkcheo": "L_LIGNUM+K_HOT+CHEO_DRY_PREPARED",
    "otcheo": "O_PREP+T_COLD+CHEO_DRY_PREPARED",
    "qokcheo": "QO_SCOPE+K_HOT+CHEO_DRY_PREPARED",
    "qotcheo": "QO_SCOPE+T_COLD+CHEO_DRY_PREPARED",
    "tcheo": "T_COLD+CHEO_DRY_PREPARED",
}

EXPECTED_NEW_COMPLETE = {"f33r.5", "f66v.5", "f93r.32", "f56r.13", "f107r.41"}
EXPECTED_NEW_ONE_HOLE = {"f80v.21": ("y", 0)}
SOURCE_CHECKS = (
    ("G658-S01", "f33r.5", "otam", "TARGET_CLOSURE", "OTAM closes the line in final AM position"),
    ("G658-S02", "f66v.5", "shedefam", "READER_WARNING", "ZL3b/IT2a keep SHEDEFAM; RF1b splits SHE EFAM"),
    ("G658-S03", "f93r.6", "s cho s", "THREE_TOKEN_BOUNDARY", "all readers preserve adjacent S | CHO | S"),
    ("G658-S04", "f93r.32", "schos", "ALL_READER_TARGET_CLOSURE", "all readers preserve SCHOS as one exact whole"),
    ("G658-S05", "f115v.44", "ral rchos", "RCHOS_MATERIAL_CONTEXT", "all readers preserve RAL RCHOS; later line token varies"),
    ("G658-S06", "f56r.13", "chokcheo", "ALL_READER_TARGET_CLOSURE", "all readers preserve nested CHOKCHEO whole"),
    ("G658-S07", "f80v.21", "y", "NEW_ONE_HOLE", "OTAM leaves only the naked Y whole open"),
    ("G658-S08", "f107r.41", "otam", "TARGET_CLOSURE", "OTAM closes an already ranked V34 one-hole line"),
    ("G658-S09", "f41r.6", "shedey", "SHEDE_PREFIX_SISTER", "SHEDEY is exact in all readers"),
    ("G658-S10", "f104v.29", "cheokcheo", "NESTED_KCHEO_SISTER", "CHEOKCHEO is exact in all readers"),
)

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv",
    "TARGET_DECISION_DECK.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv",
    "K_T_AM_FAMILY_GRID.tsv",
    "F_HEAD_BODY_FAMILY_ATLAS.tsv",
    "F_HEAD_BODY_OCCURRENCES.tsv",
    "SHEDEFAM_BOUND_F_AUDIT.tsv",
    "S_CHO_S_FAMILY_EVIDENCE.tsv",
    "KCHEO_TCHEO_FAMILY_ATLAS.tsv",
    "SOURCE_READING_AUDIT.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V35_WORKING_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V35.tsv",
    "COMPLETE_PASSAGES_V35.tsv",
    "ONE_UNKNOWN_PASSAGES_V35.tsv",
    "WORKING_DICTIONARY_V35.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def string_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, str]]:
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def position_label(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "INITIAL"
    if ordinal == length:
        return "FINAL"
    return "MEDIAL"


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": len(glossary),
    }


def sequence_present(line: str, sequence: str) -> int:
    words = line.split()
    wanted = sequence.split()
    return int(any(words[index:index + len(wanted)] == wanted for index in range(len(words) - len(wanted) + 1)))


def contextual_target_meaning(surface: str, position: str) -> str:
    if surface == "otam" and position in {"FINAL", "ONLY"}:
        return "ein Maß kalten Ansatzes."
    return TARGET_BY_SURFACE[surface]["working_meaning_de"]


def contextual_line_translation(
    line: list[dict[str, object]], coverage_row: dict[str, object], target_surfaces: set[str]
) -> str:
    glosses = split_pipe(coverage_row["token_glosses_de"])
    rendered: list[str] = []
    for ordinal, (token, gloss) in enumerate(zip(line, glosses), 1):
        surface = str(token["eva"])
        if surface in target_surfaces:
            rendered.append(contextual_target_meaning(surface, position_label(ordinal, len(line))))
        elif gloss.startswith("["):
            rendered.append(gloss)
        else:
            rendered.append(gloss)
    return "; ".join(rendered)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G657 / "artifacts/PAGE_ALLOWLIST.tsv")}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")

    query = g657.g656.g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.guarded_query
    tokens, token_stats = query(TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand")
    cross, cross_stats = query(
        CROSS_REL,
        pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross}
    by_line, _ = g657.g656.g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.line_maps(
        [dict(row) for row in tokens]
    )
    exact, boundary = g657.g656.g655.g654.g653.g637.g636.g635.g634.stable_maps(tokens, cross_by_locus)
    edition = g657.g656.g655.g654.g653.g637

    base_dict = read_tsv(ROOT / G657 / "artifacts/WORKING_DICTIONARY_V34.tsv")
    base_gloss_rows = read_tsv(ROOT / G657 / "artifacts/V34_WORKING_TOKEN_GLOSSARY.tsv")
    base_gloss = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_cov = read_tsv(ROOT / G657 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V34.tsv")
    base_complete = read_tsv(ROOT / G657 / "artifacts/COMPLETE_PASSAGES_V34.tsv")
    base_one = read_tsv(ROOT / G657 / "artifacts/ONE_UNKNOWN_PASSAGES_V34.tsv")
    if (len(base_dict), len(base_gloss), len(base_cov), len(base_complete), len(base_one)) != (570, 491, 4128, 133, 243):
        raise RuntimeError("GDT657 V34 base counts changed")
    replay_cov, replay_one, _, replay_complete = edition.build_line_coverage(
        by_line, base_gloss, exact, boundary, cross_by_locus
    )
    if (
        string_rows(replay_cov) != string_rows(base_cov)
        or string_rows(replay_one) != string_rows(base_one)
        or string_rows(replay_complete) != string_rows(base_complete)
    ):
        raise RuntimeError("GDT657 V34 editions do not replay")
    if any(surface in base_gloss for surface in TARGET_BY_SURFACE):
        raise RuntimeError("GDT658 target already present in V34")
    if any(GENERIC_FILLER.search(row["working_meaning_de"]) for row in TARGET_SPECS):
        raise RuntimeError("generic target gloss")

    surface_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        surface_members[row["eva"]].append(row)
    for members in surface_members.values():
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))

    def surface_stats(surface: str) -> tuple[int, int, int, int, int]:
        members = surface_members.get(surface, [])
        return (
            len(members),
            len({row["locus"] for row in members}),
            len({row["page"] for row in members}),
            sum(exact[row["locus"], int(row["token_index"])] for row in members),
            sum(boundary[row["locus"], int(row["token_index"])] for row in members),
        )

    for surface, expected in EXPECTED_TARGET_COUNTS.items():
        if surface_stats(surface) != expected:
            raise RuntimeError(f"target count drift {surface}: {surface_stats(surface)!r}")
    target_members = [row for row in tokens if row["eva"] in TARGET_BY_SURFACE]
    if (
        len(target_members),
        len({row["locus"] for row in target_members}),
        len({row["page"] for row in target_members}),
        sum(exact[row["locus"], int(row["token_index"])] for row in target_members),
        sum(boundary[row["locus"], int(row["token_index"])] for row in target_members),
    ) != (47, 46, 37, 41, 41):
        raise RuntimeError("aggregate target census drift")

    otam_positions = Counter()
    for member in surface_members["otam"]:
        line = by_line[member["locus"]]
        otam_positions[position_label(line_position(line, int(member["token_index"])), len(line))] += 1
    if dict(otam_positions) != {"MEDIAL": 16, "FINAL": 28}:
        raise RuntimeError(f"OTAM positional profile drift: {dict(otam_positions)!r}")

    am_rows: list[dict[str, object]] = []
    for surface, composition, meaning, occurrences, lines, page_count, reader_exact in AM_FAMILY:
        observed = surface_stats(surface)
        if observed != (occurrences, lines, page_count, reader_exact, reader_exact):
            raise RuntimeError(f"AM-family count drift {surface}: {observed!r}")
        positions = Counter()
        for member in surface_members[surface]:
            line = by_line[member["locus"]]
            positions[position_label(line_position(line, int(member["token_index"])), len(line))] += 1
        am_rows.append({
            "surface": surface,
            "composition": composition,
            "family_working_meaning_de": meaning,
            "occurrences": occurrences,
            "lines": lines,
            "pages": page_count,
            "reader_exact_occurrences": reader_exact,
            "split_normalized_occurrences": observed[4],
            "initial": positions["INITIAL"],
            "medial": positions["MEDIAL"],
            "final": positions["FINAL"],
            "only": positions["ONLY"],
            "v35_decision": "ACCEPT_EXACT_WHOLE" if surface == "otam" else "FAMILY_EVIDENCE_ONLY__NO_NEW_CARD",
        })
    if sum(int(row["occurrences"]) for row in am_rows) != 141 or sum(int(row["reader_exact_occurrences"]) for row in am_rows) != 113:
        raise RuntimeError("AM-family totals drift")

    all_surfaces = set(surface_members)
    all_f_surfaces = sorted(surface for surface in all_surfaces if surface.startswith("f") and len(surface) > 1)
    all_f_members = [row for row in tokens if row["eva"] in set(all_f_surfaces)]
    if (
        len(all_f_surfaces), len(all_f_members), len({row["page"] for row in all_f_members}),
        sum(exact[row["locus"], int(row["token_index"])] for row in all_f_members),
    ) != (77, 102, 65, 64):
        raise RuntimeError("global initial-F census drift")
    shared_f_bodies = sorted(
        surface[1:] for surface in all_f_surfaces
        if any(head + surface[1:] in all_surfaces for head in "psrl")
    )
    shared_f_members = [row for row in all_f_members if row["eva"][1:] in set(shared_f_bodies)]
    if (
        len(shared_f_bodies), len(shared_f_members), len({row["page"] for row in shared_f_members}),
        sum(exact[row["locus"], int(row["token_index"])] for row in shared_f_members),
    ) != (43, 67, 50, 42):
        raise RuntimeError("P/S/R/L-shared initial-F census drift")
    strong_f_bodies = [
        body for body in shared_f_bodies
        if sum(int(head + body in all_surfaces) for head in "psrl") >= 3 and body != "cho"
    ]
    if tuple(strong_f_bodies) != STRONG_F_BODIES:
        raise RuntimeError(f"strong F-body family drift: {strong_f_bodies!r}")
    if sum(surface_stats("f" + body)[0] for body in strong_f_bodies) != 31:
        raise RuntimeError("strong F-head occurrence total drift")

    f_grid_rows: list[dict[str, object]] = []
    f_occurrence_rows: list[dict[str, object]] = []
    for body in shared_f_bodies:
        support_heads = [head for head in "psrl" if head + body in all_surfaces]
        complete_grid = int(len(support_heads) == 4)
        family_strength = "COMPLETE_FIVE_HEAD_GRID" if complete_grid else "STRONG_THREE_HEAD_SUPPORT" if body in strong_f_bodies else "SHARED_BODY_SUPPORT"
        for head, role in F_HEADS:
            surface = head + body
            observed = surface_stats(surface)
            f_grid_rows.append({
                "body": body,
                "head": head,
                "head_role": role,
                "surface": surface,
                "occurrences": observed[0],
                "lines": observed[1],
                "pages": observed[2],
                "reader_exact_occurrences": observed[3],
                "split_normalized_occurrences": observed[4],
                "four_head_support_count": len(support_heads),
                "four_head_support": "|".join(support_heads),
                "complete_p_s_r_l_f_grid": complete_grid,
                "family_strength": family_strength,
                "interpretation": "FIFTH_MATERIA_HEAD_ARCHITECTURE__F_VALUE_BOUND",
            })
        for occurrence, member in enumerate(surface_members["f" + body], 1):
            line = by_line[member["locus"]]
            ordinal = line_position(line, int(member["token_index"]))
            reader = cross_by_locus[member["locus"]]
            f_occurrence_rows.append({
                "body": body,
                "surface": "f" + body,
                "occurrence": occurrence,
                "page": member["page"],
                "locus": member["locus"],
                "line_position": position_label(ordinal, len(line)),
                "reader_exact": exact[member["locus"], int(member["token_index"])],
                "split_normalized": boundary[member["locus"], int(member["token_index"])],
                "zl3b_line": reader["zl3b_clean"],
                "it2a_line": reader["it2a_clean"],
                "rf1b_line": reader["rf1b_clean"],
            })
    if len(f_grid_rows) != 215 or len(f_occurrence_rows) != 67:
        raise RuntimeError("F-head family materialization drift")
    complete_bodies = {row["body"] for row in f_grid_rows if int(row["complete_p_s_r_l_f_grid"])}
    if complete_bodies != COMPLETE_F_GRID_BODIES:
        raise RuntimeError("complete P/S/R/L/F grid set drift")
    f_only_rows = [row for row in f_grid_rows if row["head"] == "f"]
    if sum(int(row["reader_exact_occurrences"]) for row in f_only_rows) != 42:
        raise RuntimeError("shared F-head exact count drift")

    shedef_rows = []
    shedef_notes = {
        "shedey": ("SHE_MOIST+D_STATE+E_LINK+Y_FORM", "exact weak prefix sister; no F"),
        "shedeeey": ("SHE_MOIST+D_STATE+EEE_GRADE+Y_FORM", "reader-warning extended sister; no F"),
        "shedefam": ("SHEDE_LOCAL_MOIST_SHELL+F_BOUND_FLOWER_DRUG_HEAD+AM_MEASURE_I", "target whole; F=Blüte only here and through the fifth-head family"),
    }
    for surface in ("shedey", "shedeeey", "shedefam"):
        observed = surface_stats(surface)
        composition, note = shedef_notes[surface]
        shedef_rows.append({
            "surface": surface,
            "composition": composition,
            "occurrences": observed[0],
            "pages": observed[2],
            "reader_exact_occurrences": observed[3],
            "split_normalized_occurrences": observed[4],
            "note": note,
            "decision": "ACCEPT_TARGET_WHOLE_WITH_READER_WARNING" if surface == "shedefam" else "BOUND_FAMILY_EVIDENCE_ONLY",
        })
    if [surface_stats(row["surface"])[:1] for row in shedef_rows] != [(1,), (1,), (1,)]:
        raise RuntimeError("SHEDE family drift")

    s_chos_rows: list[dict[str, object]] = []
    terminal_s_members = [row for row in tokens if len(row["eva"]) > 1 and row["eva"].endswith("s")]
    terminal_s_positions = Counter()
    for member in terminal_s_members:
        line = by_line[member["locus"]]
        ordinal = line_position(line, int(member["token_index"]))
        terminal_s_positions["WITH_FOLLOWER" if ordinal < len(line) else "FINAL_OR_SINGLE"] += 1
    if len(terminal_s_members) != 725 or terminal_s_positions != {"WITH_FOLLOWER": 622, "FINAL_OR_SINGLE": 103}:
        raise RuntimeError("global non-standalone terminal-S census drift")
    s_chos_rows.append({
        "evidence_type": "GLOBAL_TERMINAL_S_PROFILE",
        "surface_or_locus": "length>1 and *s",
        "parse_or_sequence": "TERMINAL_S_POSITIONAL_PROFILE",
        "role": "SPECIES_LIKE_DRUG_OR_FORM_CANDIDATE__NOT_FREE_VALUE",
        "occurrences": len(terminal_s_members),
        "pages": len({row["page"] for row in terminal_s_members}),
        "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in terminal_s_members),
        "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in terminal_s_members),
        "note": "622 tokens have a follower; 103 are final or single; no global terminal-S value",
    })
    for surface, parse, role in (
        ("scho", "S_SEED_HEAD+CHO_DRY_PREPARATION", "PREFIX_SISTER"),
        ("schos", "S_SEED_HEAD+CHO_DRY_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD", "TARGET_WHOLE"),
        ("rchos", "R_RADIX+CHO_DRY_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD", "ROOT_HEAD_SISTER"),
        ("fchos", "F_BOUND_DRUG_HEAD+CHO_DRY_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD", "F_HEAD_READER_WARNING_SISTER"),
        ("chos", "CHO_DRY_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD", "BODY_FAMILY"),
        ("cheos", "CHEO_DRY_PREPARED+S_BOUND_SPECIES_DRUG_HEAD", "DRY_PREPARED_BODY_FAMILY"),
        ("cheeos", "CHEEO_DRY_GRADE+S_BOUND_SPECIES_DRUG_HEAD", "DRY_GRADE_BODY_FAMILY"),
        ("shos", "SHO_MOIST_PREPARATION+S_BOUND_SPECIES_DRUG_HEAD", "MOIST_BODY_FAMILY"),
        ("sheos", "SHEO_MOIST_PREPARED+S_BOUND_SPECIES_DRUG_HEAD", "MOIST_PREPARED_BODY_FAMILY"),
        ("sheeos", "SHEEO_MOIST_GRADE+S_BOUND_SPECIES_DRUG_HEAD", "MOIST_GRADE_BODY_FAMILY"),
        ("schol", "S_SEED_HEAD+CHOL_DRY_MATERIAL", "SEED_DRY_MATERIAL_SISTER"),
        ("schor", "S_SEED_HEAD+CHOR_DRY_PORTION", "SEED_DRY_PORTION_SISTER"),
    ):
        observed = surface_stats(surface)
        s_chos_rows.append({
            "evidence_type": "SURFACE_FAMILY",
            "surface_or_locus": surface,
            "parse_or_sequence": parse,
            "role": role,
            "occurrences": observed[0],
            "pages": observed[2],
            "reader_exact_occurrences": observed[3],
            "split_normalized_occurrences": observed[4],
            "note": "initial S and terminal S remain distinct; no global terminal-S value",
        })
    sequence_reader = cross_by_locus["f93r.6"]
    if not all(sequence_present(sequence_reader[key], "s cho s") for key in ("zl3b_clean", "it2a_clean", "rf1b_clean")):
        raise RuntimeError("f93r.6 lost the S | CHO | S reader boundary")
    s_chos_rows.append({
        "evidence_type": "THREE_TOKEN_BOUNDARY",
        "surface_or_locus": "f93r.6",
        "parse_or_sequence": "s | cho | s",
        "role": "ALL_READERS_EXACT_LOCAL_BOUNDARY",
        "occurrences": 1,
        "pages": 1,
        "reader_exact_occurrences": 1,
        "split_normalized_occurrences": 1,
        "note": "same visible sequence as SCHOS, but written as three words",
    })
    if surface_stats("schos") != (1, 1, 1, 1, 1) or surface_stats("rchos") != (1, 1, 1, 1, 1):
        raise RuntimeError("SCHOS/RCHOS anchor drift")
    chos_family = [surface_stats(surface) for surface in ("chos", "cheos", "cheeos", "shos", "sheos", "sheeos")]
    if sum(row[0] for row in chos_family) != 83 or sum(row[3] for row in chos_family) != 70:
        raise RuntimeError("CHO/SHO terminal-S family drift")
    if tuple(surface_stats(surface)[0] for surface in ("schol", "schor", "schos")) != (3, 3, 1):
        raise RuntimeError("SCHOL/SCHOR/SCHOS sister count drift")

    kcheo_rows: list[dict[str, object]] = []
    observed_kcheo_surfaces = {surface for surface in all_surfaces if surface.endswith(("kcheo", "tcheo"))}
    if observed_kcheo_surfaces != set(KCHEO_EXPECTED):
        raise RuntimeError(f"KCHEO/TCHEO family drift: {sorted(observed_kcheo_surfaces)!r}")
    for surface in sorted(KCHEO_EXPECTED):
        observed = surface_stats(surface)
        if observed[0:1] + observed[2:] != KCHEO_EXPECTED[surface]:
            raise RuntimeError(f"KCHEO-family count drift {surface}: {observed!r}")
        kcheo_rows.append({
            "surface": surface,
            "composition": KCHEO_PARSES[surface],
            "occurrences": observed[0],
            "lines": observed[1],
            "pages": observed[2],
            "reader_exact_occurrences": observed[3],
            "split_normalized_occurrences": observed[4],
            "loci": "|".join(sorted({row["locus"] for row in surface_members[surface]})),
            "decision": "ACCEPT_TARGET_WHOLE" if surface == "chokcheo" else "FAMILY_EVIDENCE_ONLY__NO_NEW_CARD",
        })

    source_rows: list[dict[str, object]] = []
    for check_id, locus, sequence, evidence_type, note in SOURCE_CHECKS:
        reader = cross_by_locus[locus]
        present = {
            key: sequence_present(reader[key], sequence)
            for key in ("zl3b_clean", "it2a_clean", "rf1b_clean")
        }
        if evidence_type == "READER_WARNING":
            if present != {"zl3b_clean": 1, "it2a_clean": 1, "rf1b_clean": 0} or not sequence_present(reader["rf1b_clean"], "she efam"):
                raise RuntimeError("SHEDEFAM reader-warning pattern drift")
        elif evidence_type in {"THREE_TOKEN_BOUNDARY", "RCHOS_MATERIAL_CONTEXT", "ALL_READER_TARGET_CLOSURE", "SHEDE_PREFIX_SISTER", "NESTED_KCHEO_SISTER"} and not all(present.values()):
            raise RuntimeError(f"source sequence drift at {locus}: {present!r}")
        elif not present["zl3b_clean"]:
            raise RuntimeError(f"ZL3b source sequence drift at {locus}: {present!r}")
        source_rows.append({
            "check_id": check_id,
            "page": reader["page"],
            "locus": locus,
            "evidence_type": evidence_type,
            "expected_sequence": sequence,
            "zl3b_sequence_present": present["zl3b_clean"],
            "it2a_sequence_present": present["it2a_clean"],
            "rf1b_sequence_present": present["rf1b_clean"],
            "all_three_present": reader["all_three_present"],
            "all_present_exact": reader["all_present_exact"],
            "zl3b_line": reader["zl3b_clean"],
            "it2a_line": reader["it2a_clean"],
            "rf1b_line": reader["rf1b_clean"],
            "note": note,
        })

    deck: list[dict[str, object]] = []
    accepted_defaults: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0,
        "surface": "BASE_V34",
        "mode": "BASE",
        "dictionary_entries": len(base_dict),
        "dictionary_sha256": canonical_hash(base_dict),
        **metrics(base_cov, base_one, base_complete, base_gloss),
    }]
    gloss = {key: dict(value) for key, value in base_gloss.items()}
    dictionary = [dict(row) for row in base_dict]
    coverage, one, _, complete = edition.build_line_coverage(by_line, gloss, exact, boundary, cross_by_locus)

    for index, row in enumerate(TARGET_SPECS, 1):
        surface = row["surface"]
        members = surface_members[surface]
        observed = surface_stats(surface)
        pre_by_locus = {item["locus"]: item for item in coverage}
        edition.set_gloss(
            gloss,
            surface,
            row["working_meaning_de"],
            f"GDT658:{row['mode']}",
            "EXACT_WHOLE_RESIDUAL_CONCRETE_COMPLETION",
            "KNOWN_EXACT_WHOLE",
            156,
        )
        dictionary_entry = {
            "entry": f"{surface}@GDT658_EXACT_WHOLE",
            "kind": f"EXACT_ZL3B_WHOLE_{row['mode']}",
            "working_meaning_de": row["working_meaning_de"],
            "composition": row["composition"],
            "context_rule": f"exact complete ZL3b surface only; {observed[0]} occurrences; {observed[3]} reader-exact; no substring inheritance",
            "status": f"NEW_V35_ACCEPTED_ROUND_{index:02d}",
        }
        dictionary.append(dictionary_entry)
        deck.append({
            "candidate_order": index,
            **row,
            "occurrences": observed[0],
            "lines": observed[1],
            "pages": observed[2],
            "reader_exact_occurrences": observed[3],
            "split_normalized_occurrences": observed[4],
            "decision": "ACCEPT_V35_WITH_READER_WARNING" if surface in WARNING_SURFACES else "ACCEPT_V35_EXACT_WHOLE",
        })
        accepted_defaults.append({
            "surface": surface,
            **dictionary_entry,
            "occurrences": observed[0],
            "acceptance_mode": row["mode"],
        })
        coverage, one, _, complete = edition.build_line_coverage(by_line, gloss, exact, boundary, cross_by_locus)
        post_by_locus = {item["locus"]: item for item in coverage}
        for occurrence, member in enumerate(members, 1):
            locus = member["locus"]
            token_index = int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            location = position_label(ordinal, len(line))
            before = pre_by_locus[locus]
            after = post_by_locus[locus]
            before_glosses = split_pipe(before["token_glosses_de"])
            after_glosses = split_pipe(after["token_glosses_de"])
            reader = cross_by_locus[locus]
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            zl_it_agree = int(
                surface in reader["zl3b_clean"].split() and surface in reader["it2a_clean"].split()
            )
            support = (
                "ALL_THREE_EXACT"
                if reader_exact
                else "ALL_THREE_SPLIT_NORMALIZED"
                if normalized
                else "ZL3B_IT2A_EXACT_RF_SPLIT"
                if zl_it_agree
                else "READER_VARIANT"
            )
            context_meaning = contextual_target_meaning(surface, location)
            verdict = (
                "READER_VARIANT_WARNING"
                if not normalized
                else "CONCRETE_CONTEXT_COMPATIBLE"
                if int(before["known_tokens"]) >= 2
                else "SHORT_OR_OPAQUE_CONTEXT"
            )
            audit_rows.append({
                "audit_id": f"G658-A{index:02d}-{occurrence:04d}",
                "round": index,
                "surface": surface,
                "mode": row["mode"],
                "page": member["page"],
                "locus": locus,
                "section": member["section"],
                "language": member["language"],
                "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": location,
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"],
                "it2a_line": reader["it2a_clean"],
                "rf1b_line": reader["rf1b_clean"],
                "reader_support": support,
                "reader_exact": reader_exact,
                "split_normalized": normalized,
                "zl3b_it2a_exact": zl_it_agree,
                "default_meaning_de": row["working_meaning_de"],
                "contextual_meaning_de": context_meaning,
                "before_gloss_de": before_glosses[ordinal - 1],
                "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": int(before["known_tokens"]),
                "v34_line_de": before["token_glosses_de"],
                "v35_line_de": after["token_glosses_de"],
                "hard_collision": 0,
                "verdict": verdict,
            })
            if not normalized:
                variant_rows.append({
                    "surface": surface,
                    "page": member["page"],
                    "locus": locus,
                    "zl3b_line": before["zl3b_line"],
                    "it2a_line": reader["it2a_clean"],
                    "rf1b_line": reader["rf1b_clean"],
                    "reader_support": support,
                    "zl3b_it2a_exact": zl_it_agree,
                    "working_meaning_de": row["working_meaning_de"],
                    "decision": "RETAIN_ZL3B_WHOLE_WITH_READER_WARNING",
                })
        round_rows.append({
            "round": index,
            "surface": surface,
            "mode": row["mode"],
            "dictionary_entries": len(dictionary),
            "dictionary_sha256": canonical_hash(dictionary),
            **metrics(coverage, one, complete, gloss),
        })

    final_metrics = metrics(coverage, one, complete, gloss)
    expected_metrics = {
        "physical_lines": 4128,
        "known_token_positions": 16743,
        "unknown_token_positions": 15596,
        "complete_multi_token_lines": 138,
        "strict_complete_lines": 80,
        "one_unknown_lines": 239,
        "strict_one_unknown_lines": 57,
        "working_glossary_surfaces": 495,
    }
    if final_metrics != expected_metrics or len(dictionary) != 574:
        raise RuntimeError(f"unexpected V35 metrics: {final_metrics!r}; dictionary={len(dictionary)}")
    if (len(audit_rows), sum(int(row["reader_exact"]) for row in audit_rows), len(variant_rows)) != (47, 41, 6):
        raise RuntimeError("target audit totals changed")
    if any(int(row["hard_collision"]) for row in audit_rows):
        raise RuntimeError("target hard collision")

    base_complete_loci = {row["locus"] for row in base_complete}
    new_complete = [row for row in complete if row["locus"] not in base_complete_loci]
    if {row["locus"] for row in new_complete} != EXPECTED_NEW_COMPLETE:
        raise RuntimeError(f"new-completion set drift: {[row['locus'] for row in new_complete]!r}")
    if sum(int(row["strict_complete"]) for row in new_complete) != 2:
        raise RuntimeError("new strict-completion count drift")
    final_by_locus = {row["locus"]: row for row in coverage}
    base_by_locus = {row["locus"]: row for row in base_cov}
    completed_rows: list[dict[str, object]] = []
    for row in sorted(new_complete, key=lambda item: item["locus"]):
        locus = row["locus"]
        enabled = sorted({token["eva"] for token in by_line[locus] if token["eva"] in TARGET_BY_SURFACE})
        completed_rows.append({
            "page": row["page"],
            "locus": locus,
            "strict_complete": row["strict_complete"],
            "enabled_by_surfaces": "|".join(enabled),
            "zl3b_line": row["zl3b_line"],
            "v34_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v35_tokenwise_de": row["token_glosses_de"],
            "practical_v35_de": contextual_line_translation(by_line[locus], row, set(TARGET_BY_SURFACE)),
        })

    base_one_loci = {row["locus"] for row in base_one}
    final_one_by_locus = {row["locus"]: row for row in one}
    new_one = [row for row in one if row["locus"] not in base_one_loci]
    removed_one_loci = base_one_loci - set(final_one_by_locus)
    if len(removed_one_loci) != 5 or removed_one_loci != EXPECTED_NEW_COMPLETE:
        raise RuntimeError("V34 one-hole closure set drift")
    if {row["locus"] for row in new_one} != set(EXPECTED_NEW_ONE_HOLE):
        raise RuntimeError("new V35 one-hole set drift")
    new_one_rows: list[dict[str, object]] = []
    for row in new_one:
        residual, strict = EXPECTED_NEW_ONE_HOLE[row["locus"]]
        if (row["unknown_surface"], int(row["strict_eligible"])) != (residual, strict):
            raise RuntimeError("f80v.21 one-hole detail drift")
        new_one_rows.append({
            "enabled_by_surface": "otam",
            **{field: row[field] for field in ONE_FIELDS},
            "curated_one_hole_reading_de": contextual_line_translation(
                by_line[row["locus"]], final_by_locus[row["locus"]], set(TARGET_BY_SURFACE)
            ).replace("[y:?]", "[Y: Grundform noch ohne Ganzwortkarte]"),
        })

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted({row["locus"] for row in target_members}):
        line = by_line[locus]
        targets = [token["eva"] for token in line if token["eva"] in TARGET_BY_SURFACE]
        final = final_by_locus[locus]
        target_line_rows.append({
            "page": final["page"],
            "locus": locus,
            "target_surfaces": "|".join(targets),
            "target_positions": len(targets),
            "zl3b_line": final["zl3b_line"],
            "v34_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v35_tokenwise_de": final["token_glosses_de"],
            "practical_v35_de": contextual_line_translation(line, final, set(TARGET_BY_SURFACE)),
            "complete_v35": int(final["unknown_tokens"]) == 0,
        })
    if len(target_line_rows) != 46 or sum(int(row["target_positions"]) for row in target_line_rows) != 47:
        raise RuntimeError("target line materialization drift")

    final_gloss = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(gloss.values(), key=lambda item: item["surface"])
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", deck, (
        "candidate_order", "surface", "mode", "working_meaning_de", "composition", "rival_de", "occurrences",
        "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "decision",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "occurrences", "acceptance_mode",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "mode", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "zl3b_it2a_exact", "default_meaning_de",
        "contextual_meaning_de", "before_gloss_de", "after_gloss_de", "known_other_tokens", "v34_line_de",
        "v35_line_de", "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "zl3b_it2a_exact", "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "K_T_AM_FAMILY_GRID.tsv", am_rows, (
        "surface", "composition", "family_working_meaning_de", "occurrences", "lines", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "initial", "medial", "final", "only",
        "v35_decision",
    ))
    write_tsv(output_dir / "F_HEAD_BODY_FAMILY_ATLAS.tsv", f_grid_rows, (
        "body", "head", "head_role", "surface", "occurrences", "lines", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "four_head_support_count", "four_head_support",
        "complete_p_s_r_l_f_grid", "family_strength", "interpretation",
    ))
    write_tsv(output_dir / "F_HEAD_BODY_OCCURRENCES.tsv", f_occurrence_rows, (
        "body", "surface", "occurrence", "page", "locus", "line_position", "reader_exact",
        "split_normalized", "zl3b_line", "it2a_line", "rf1b_line",
    ))
    write_tsv(output_dir / "SHEDEFAM_BOUND_F_AUDIT.tsv", shedef_rows, (
        "surface", "composition", "occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "note", "decision",
    ))
    write_tsv(output_dir / "S_CHO_S_FAMILY_EVIDENCE.tsv", s_chos_rows, (
        "evidence_type", "surface_or_locus", "parse_or_sequence", "role", "occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "note",
    ))
    write_tsv(output_dir / "KCHEO_TCHEO_FAMILY_ATLAS.tsv", kcheo_rows, (
        "surface", "composition", "occurrences", "lines", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "loci", "decision",
    ))
    write_tsv(output_dir / "SOURCE_READING_AUDIT.tsv", source_rows, (
        "check_id", "page", "locus", "evidence_type", "expected_sequence", "zl3b_sequence_present",
        "it2a_sequence_present", "rf1b_sequence_present", "all_three_present", "all_present_exact",
        "zl3b_line", "it2a_line", "rf1b_line", "note",
    ))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, (
        "page", "locus", "target_surfaces", "target_positions", "zl3b_line", "v34_tokenwise_de",
        "v35_tokenwise_de", "practical_v35_de", "complete_v35",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "mode", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "working_glossary_surfaces",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", completed_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "v34_tokenwise_de",
        "v35_tokenwise_de", "practical_v35_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", new_one_rows, (
        "enabled_by_surface", *ONE_FIELDS, "curated_one_hole_reading_de",
    ))
    write_tsv(output_dir / "V35_WORKING_TOKEN_GLOSSARY.tsv", final_gloss, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V35.tsv", coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V35.tsv", complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V35.tsv", one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V35.tsv", dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G657 / "src/run.py",
        G657 / "artifacts/PAGE_ALLOWLIST.tsv",
        G657 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V34.tsv",
        G657 / "artifacts/COMPLETE_PASSAGES_V34.tsv",
        G657 / "artifacts/ONE_UNKNOWN_PASSAGES_V34.tsv",
        G657 / "artifacts/V34_WORKING_TOKEN_GLOSSARY.tsv",
        G657 / "artifacts/WORKING_DICTIONARY_V34.tsv",
        G657 / "artifacts/RESULT.json",
        G657 / "REPORT.md",
        G635_REPORT,
        G636_REPORT,
        G640_REPORT,
        TOKENS_REL,
        CROSS_REL,
    )
    verdicts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT658_FOUR_RESIDUAL_CONCRETE_COMPLETION_RESULT_V1",
        "experiment_id": "GDT658",
        "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED",
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
            "new_pages": 0,
            "new_images": 0,
            "allowed_pages": len(pages),
            "token_query": token_stats,
            "cross_query": cross_stats,
        },
        "target_run": {
            "candidates": 4,
            "accepted_whole_cards": 4,
            "reader_exact_wholes": 3,
            "reader_warning_wholes": sorted(WARNING_SURFACES),
            "accepted_surfaces": [row["surface"] for row in deck],
            "audited_occurrences": len(audit_rows),
            "target_lines": len({row["locus"] for row in audit_rows}),
            "target_pages": len({row["page"] for row in audit_rows}),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": len(variant_rows),
            "hard_collisions": 0,
            "verdicts": dict(sorted(verdicts.items())),
        },
        "family_evidence": {
            "am_grid_surfaces": len(am_rows),
            "am_grid_occurrences": sum(int(row["occurrences"]) for row in am_rows),
            "am_grid_reader_exact": sum(int(row["reader_exact_occurrences"]) for row in am_rows),
            "otam_position_profile": dict(sorted(otam_positions.items())),
            "global_initial_f_surface_types": len(all_f_surfaces),
            "global_initial_f_occurrences": len(all_f_members),
            "global_initial_f_pages": len({row["page"] for row in all_f_members}),
            "shared_f_body_types": len(shared_f_bodies),
            "shared_f_head_occurrences": len(f_occurrence_rows),
            "shared_f_head_reader_exact": sum(int(row["reader_exact"]) for row in f_occurrence_rows),
            "strong_f_body_types": len(strong_f_bodies),
            "strong_f_head_occurrences": sum(surface_stats("f" + body)[0] for body in strong_f_bodies),
            "complete_p_s_r_l_f_grids": len(COMPLETE_F_GRID_BODIES),
            "complete_p_s_r_l_f_bodies": sorted(COMPLETE_F_GRID_BODIES),
            "nonstandalone_terminal_s_occurrences": len(terminal_s_members),
            "terminal_s_with_follower": terminal_s_positions["WITH_FOLLOWER"],
            "terminal_s_final_or_single": terminal_s_positions["FINAL_OR_SINGLE"],
            "s_chos_reader_boundary": "f93r.6 preserves s|cho|s in all three readers",
            "rchos_anchor": "f115v.44 preserves ral rchos in all three readers",
            "kcheo_tcheo_surface_types": len(kcheo_rows),
            "structural_tags_not_free_words": [
                "AM_MEASURE_I", "F_BOUND_FLOWER_DRUG_HEAD", "S_BOUND_SPECIES_DRUG_HEAD", "CHO_DRY_PREPARATION",
                "CHEO_DRY_PREPARED", "O_PREP", "QO_SCOPE", "SHEDE_LOCAL_MOIST_SHELL",
            ],
        },
        "coverage": {
            "base": metrics(base_cov, base_one, base_complete, base_gloss),
            "final": final_metrics,
            "newly_completed_lines": len(completed_rows),
            "newly_completed_loci": sorted(EXPECTED_NEW_COMPLETE),
            "newly_exposed_one_hole_lines": len(new_one_rows),
            "new_one_hole_residuals": {"f80v.21": "y"},
            "affected_lines": len(target_line_rows),
        },
        "working_dictionary": {
            "v34_entries": len(base_dict),
            "v35_entries": len(dictionary),
            "accepted_tail_entries": 4,
            "v34_prefix_sha256": canonical_hash(base_dict),
            "v35_sha256": canonical_hash(dictionary),
            "v34_glossary_surfaces": len(base_gloss),
            "v35_glossary_surfaces": len(gloss),
        },
        "determinism_contract": {
            "builder_supports_external_tempdir_replay": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory exact-whole working translations for OTAM, SHEDEFAM, SCHOS and CHOKCHEO. "
            "SHEDEFAM retains a reader warning; F=Blüte and terminal S=species/form remain bound to their "
            "whole/family cards. No free component, substring inheritance, plaintext, phonetics, language, "
            "unseen cell, exact plant or ingredient identity, instruction, f1r, new page or image is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    with tempfile.TemporaryDirectory(prefix="gdt658_replay_") as directory:
        replay_dir = Path(directory)
        replay_result = build(replay_dir)
        if replay_result != result:
            raise RuntimeError("tempdir result replay differs")
        for name in (*OUTPUT_NAMES, "RESULT.json"):
            if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        "GDT658 built: accepted=4 audits=47 exact=41 "
        f"known={result['coverage']['final']['known_token_positions']} replay=22/22"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
