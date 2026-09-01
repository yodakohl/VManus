#!/usr/bin/env python3
"""Build the complete V83 dictionary confidence and evidence register.

Scores are audit indices inside the exploratory model, never probabilities or
historical decipherment claims.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt710_v83_complete_dictionary_confidence_evidence"
SRC, ART = EXP / "src", EXP / "artifacts"
G671 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G684 = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts"
G685 = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts"
G686 = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts"
G687 = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts"
G689 = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts"
G690 = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/artifacts"
G691 = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/artifacts"
G692 = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor/artifacts"
G693 = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts"
G694 = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration/artifacts"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts"
MASTER = G671 / "WORKING_DICTIONARY_V48.tsv"
GLOSSARY = G671 / "V48_WORKING_TOKEN_GLOSSARY.tsv"
COVERAGE = G671 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
ACTIVE = G695 / "V68_479_TOKEN_FREEZE.tsv"
CONTROLS = SRC / "V83_MANUAL_CONFIDENCE_CONTROLS.tsv"

STATUS = (
    "PASS_V83_2115_MASTER_CARDS__1430_GLOBAL_SURFACES__"
    "1582_COMPLETE_WORD_SURFACES_1594_READINGS__"
    "320_LIVE_SURFACES_332_LIVE_READINGS_479_OCCURRENCES__"
    "ALL_H0_NONE__CONFIDENCE_IS_NOT_PLAINTEXT"
)
HISTORICAL = "H0_NONE"
RELATION_WORD_DELTA = "0_GDT696_TO_GDT709"
STAGE_DESCRIPTIONS = {
    "GDT684": "V57-Positionsaudit des geerbten Wortwerts",
    "GDT685": "Zustandszellen-Dispatch und Entfernung generischer Ansatzkoepfe",
    "GDT686": "Wertkopf-Dispatch fuer Grad gegen Menge",
    "GDT687": "vollstaendiger Action/Result/Boundary-Dispatch",
    "GDT689": "gebundener dy-Schwestervergleich und Endpunkt-Dispatch",
    "GDT690": "Nomenordinal-, Kopf- und Rivalenapparat",
    "GDT691": "Rollen-Dispatch der Zubereitungskoepfe",
    "GDT692": "O/Q-Fraktions-Schwesterkompositor",
    "GDT693": "AR-Kopf-Semantiktournament",
    "GDT694": "Migration der restlichen Anteilslesungen",
    "GDT695": "byte-identischer Wortfreeze; nur Klauselrealisation",
}
STRUCTURAL_RE = re.compile(
    r"^(?:[.;,:]|hierzu:?|hieran anschließend|davon|dazu)$|"
    r"klausel|zeilen|grenze|anschluss|verweis|bezug|satzzeichen", re.I,
)
IDENTITY_RE = re.compile(
    r"gummi|harz|samen|wurzel|blatt|blueten|blüten|holz|kraut|droge|pulver|"
    r"mazerat|auszug|absud|arzneikompositum|rohstoff", re.I,
)
CONCRETE_RE = re.compile(
    r"trock|feucht|heiss|heiß|kalt|einweich|erhitz|abmess|nehm|nimm|zugeb|"
    r"fertig|abgeschlossen|pulver|holz|kraut|droge|samen|wurzel|blatt|"
    r"bluet|blüt|harz|mazerat|auszug|absud", re.I,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for source in rows:
            writer.writerow({field: source.get(field, "") for field in fields})


def compact(values: Iterable[str], empty: str = "NONE") -> str:
    cleaned = sorted({value.strip() for value in values if value and value.strip() not in {"NONE", "0"}})
    return "|".join(cleaned) if cleaned else empty


def key(row: dict[str, str]) -> tuple[str, str, int, str]:
    return row["page"], row["locus"], int(row.get("token_ordinal") or row.get("ordinal") or "0"), row["surface"]


def attestation_scores(occurrences: int, pages: int) -> tuple[int, int, int]:
    occ_score = 0 if occurrences <= 1 else 2 if occurrences == 2 else 4 if occurrences <= 4 else 6 if occurrences <= 8 else 8
    page_score = 0 if pages <= 1 else 3 if pages == 2 else 6 if pages <= 4 else 9 if pages <= 8 else 12
    return occ_score, page_score, occ_score + page_score


def level(score: int) -> str:
    if score < 20:
        return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40:
        return "W1_WEAK_WORKING"
    if score < 60:
        return "W2_PROVISIONAL_WORKING"
    if score < 80:
        return "W3_SOLID_WORKING_THEORY"
    return "W4_STRONG_WORKING_THEORY"


def specificity_score(gloss: str, live_rival: bool = False) -> int:
    if STRUCTURAL_RE.search(gloss.strip()):
        return 0
    if CONCRETE_RE.search(gloss):
        return 8 if live_rival else 12
    if re.search(r"grad|stufe|mass|maß|menge|portion|anteil|teil|zustand|ansatz|gut|material", gloss, re.I):
        return 4
    return 4


def form_level(scope_state: str, occurrences: int, active: bool = False) -> str:
    if occurrences == 0:
        return "F0_NO_EXACT_ZL3B_OCCURRENCE"
    if active:
        return "F3_EXACT_ACTIVE_ZL3B_TOKEN"
    if scope_state == "KNOWN_EXACT_WHOLE":
        return "F3_EXACT_ZL3B_WHOLE"
    if scope_state in {"KNOWN_CONTEXT_LICENSED", "KNOWN_READER_VARIANT_WHOLE"}:
        return "F2_CONTEXT_OR_READER_VARIANT"
    return "F1_AMBIGUOUS_OR_READER_UNSTABLE"


def strength_flags(value: str) -> tuple[bool, bool]:
    upper = value.upper()
    exploratory = "EXPLOR" in upper
    return "LOW" in upper or exploratory, exploratory


def rule_score(strength: str, kind: str = "") -> int:
    text = f"{strength} {kind}".upper()
    if "PRACTICAL_RENDERING_CARD" in text:
        return 0
    if "PRODUCTIVE" in text or "STRONG_" in text or "COMPONENT_GRID" in text or "TARGET_DEFAULT" in text:
        return 20
    if "FAMILY" in text or "COMPOSITION" in text or "SERIES" in text or "MIGRATION" in text:
        return 15
    if "EXACT" in text or "TARGET_SURFACE" in text or "CONTEXTUAL" in text:
        return 10
    if "LEARNED" in text or "WHOLE" in text or "DEFAULT" in text:
        return 5
    return 0


def finish_score(parts: dict[str, int], penalties: list[tuple[str, int]], caps: list[tuple[str, int]], floor: int = 0) -> dict[str, Any]:
    raw = sum(parts.values())
    penalized = max(0, raw + sum(delta for _, delta in penalties))
    cap_value = min([79, *[cap for _, cap in caps]])
    final = min(max(penalized, floor), cap_value)
    return {
        **{f"score_{name}": value for name, value in parts.items()},
        "penalties": compact([f"{name}:{delta}" for name, delta in penalties]),
        "raw_score": raw,
        "cap_reason": compact([f"{name}:MAX_{cap}" for name, cap in caps] + ["NO_PROSPECTIVE_PLAINTEXT_TEST:MAX_79"]),
        "working_model_score_0_100_not_probability": final,
        "working_model_level": level(final),
    }


def manual_control(controls: list[dict[str, str]], scope: str, surface: str, gloss: str) -> dict[str, str] | None:
    hits = [row for row in controls if row["scope"] == scope and row["surface"] == surface and row["working_meaning_de"] in {"*", gloss}]
    exact = [row for row in hits if row["working_meaning_de"] == gloss]
    return exact[0] if exact else hits[0] if hits else None


def global_occurrences(coverage: list[dict[str, str]], surfaces: set[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {
        surface: {"count": 0, "pages": set(), "loci": set(), "sections": set(), "samples": []}
        for surface in surfaces
    }
    for row in coverage:
        assert not row["page"].startswith("f84") and not row["locus"].startswith("f84")
        for surface in row["zl3b_line"].split():
            if surface not in result:
                continue
            info = result[surface]
            info["count"] += 1
            info["pages"].add(row["page"]); info["loci"].add(row["locus"]); info["sections"].add(row["section"])
            if row["locus"] not in info["samples"] and len(info["samples"]) < 6:
                info["samples"].append(row["locus"])
    return result


def build_lineage(master: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    paths: list[tuple[int, str, Path, list[dict[str, str]]]] = []
    for path in ROOT.glob("experiments/yolo/gdt*/artifacts/WORKING_DICTIONARY_V*.tsv"):
        vm = re.search(r"WORKING_DICTIONARY_V(\d+)\.tsv$", path.name)
        gm = re.search(r"/gdt(\d+)_", path.as_posix())
        if vm and gm:
            paths.append((int(vm.group(1)), f"GDT{int(gm.group(1)):03d}", path, read_tsv(path)))
    paths.sort()
    by_entry: dict[str, list[tuple[int, str, Path, dict[str, str]]]] = defaultdict(list)
    for version, gdt, path, rows in paths:
        for source in rows:
            if version == 2:
                row = {
                    "entry": source["surface"], "kind": source["layer"],
                    "working_meaning_de": source["default_meaning_de"],
                    "composition": source["composition_slot"],
                    "context_rule": f"{source['evidence']} | {source['caveat']}",
                    "status": source["status"],
                }
            else:
                row = dict(source)
                if "context_rule" not in row:
                    row["context_rule"] = row.pop("scope")
            by_entry[row["entry"]].append((version, gdt, path, row))
    result: dict[str, dict[str, Any]] = {}
    for current in master:
        history = by_entry[current["entry"]]
        signatures = [tuple(item[3][field] for field in ("kind", "working_meaning_de", "composition", "context_rule", "status")) for item in history]
        meanings = [item[3]["working_meaning_de"] for item in history]
        revision_count = sum(a != b for a, b in zip(signatures, signatures[1:]))
        meaning_revisions = sum(a != b for a, b in zip(meanings, meanings[1:]))
        last_changed = max(i for i, signature in enumerate(signatures) if i == 0 or signature != signatures[i - 1])
        versions = [item[0] for item in history]
        result[current["entry"]] = {
            "first_version": history[0][0], "first_experiment": history[0][1],
            "last_changed_version": history[last_changed][0], "last_changed_experiment": history[last_changed][1],
            "versions_present": len(history), "revision_count": revision_count,
            "meaning_revision_count": meaning_revisions,
            "continuous_from_first": int(versions == list(range(versions[0], 49))),
            "source_artifacts": compact([item[2].relative_to(ROOT).as_posix() for item in history]),
        }
    return result


def build_pre_v57_origins(v57_rows: list[dict[str, str]]) -> dict[tuple[str, str, int, str], dict[str, str]]:
    """Replay V50--V57 so GDT684 survivors retain their real card origin."""
    glossary_pairs = {(row["surface"], row["working_meaning_de"]): row for row in read_tsv(GLOSSARY)}
    v50_path = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer/artifacts/V50_EXTERNAL_TOKEN_READER.tsv"
    state: dict[tuple[str, str, int, str], dict[str, str]] = {}
    for row in read_tsv(v50_path):
        pair = (row["surface"], row["v50_gloss_de"])
        if row["information_category"] == "NEW_V50":
            semantic_origin = "GDT675"
        elif pair in glossary_pairs:
            source = glossary_pairs[pair]["source"]
            match = re.search(r"GDT(\d+)", source)
            semantic_origin = f"GDT{int(match.group(1)):03d}" if match else "GDT636_V13"
        elif row["surface"] == "os" and row["v50_gloss_de"] == "Ansatzcharge":
            semantic_origin = "GDT673"
        elif row["surface"] == "r" and row["v50_gloss_de"] == "Wurzel":
            semantic_origin = "GDT661_CONTEXT_ONLY"
        else:
            semantic_origin = "GDT676_INHERITED_UNRESOLVED"
        state[key(row)] = {
            "gloss": row["v50_gloss_de"], "position_assignment_writer_gdt": "GDT676",
            "semantic_card_origin_gdt": semantic_origin,
            "semantic_origin_artifact": v50_path.relative_to(ROOT).as_posix(),
            "semantic_origin_label": row["information_category"],
        }
    for gdt_number, version in zip(range(677, 684), range(51, 58)):
        path = next(ROOT.glob(f"experiments/yolo/gdt{gdt_number}_*/artifacts/V{version}_51_LINE_READER.tsv"))
        for line in read_tsv(path):
            surfaces = line["zl3b_line"].split(); glosses = line["literal_token_glosses_de"].split(" | ")
            assert len(surfaces) == len(glosses) == int(line["token_count"])
            for ordinal, (surface, gloss) in enumerate(zip(surfaces, glosses), 1):
                position = (line["page"], line["locus"], ordinal, surface)
                assert position in state
                if gloss != state[position]["gloss"]:
                    state[position] = {
                        "gloss": gloss, "position_assignment_writer_gdt": f"GDT{gdt_number}",
                        "semantic_card_origin_gdt": f"GDT{gdt_number}",
                        "semantic_origin_artifact": path.relative_to(ROOT).as_posix(),
                        "semantic_origin_label": f"V{version}_TARGET_OR_RENDER_REVISION",
                    }
    # Explicit inherited-card reuse: assignment writer and semantic card origin
    # are deliberately distinct for these two positions.
    state[("f105v", "f105v.14", 1, "pchedaiin")]["semantic_card_origin_gdt"] = "GDT678"
    state[("f105v", "f105v.14", 1, "pchedaiin")]["semantic_origin_label"] = "INHERITED_CARD_REUSE_FROM_GDT678"
    state[("f105v", "f105v.14", 1, "pchedaiin")]["semantic_origin_artifact"] = "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
    state[("f86v5", "f86v5.4", 7, "chepy")]["semantic_card_origin_gdt"] = "GDT680"
    state[("f86v5", "f86v5.4", 7, "chepy")]["semantic_origin_label"] = "INHERITED_CARD_REUSE_FROM_GDT680"
    state[("f86v5", "f86v5.4", 7, "chepy")]["semantic_origin_artifact"] = "experiments/yolo/gdt680_eight_four_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
    assert set(state) == {key(row) for row in v57_rows}
    for row in v57_rows:
        assert state[key(row)]["gloss"] == row["literal_gloss_de"]
    return state


def build_active_state() -> tuple[list[dict[str, str]], dict[tuple[str, str, int, str], dict[str, Any]], dict[str, dict[tuple[str, str, int, str], dict[str, str]]]]:
    v57_rows = read_tsv(G684 / "V57_479_POSITION_INFORMATION_AUDIT.tsv")
    pre_v57 = build_pre_v57_origins(v57_rows)
    state: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    for row in v57_rows:
        prior = pre_v57[key(row)]
        state[key(row)] = {"gloss": row["literal_gloss_de"], "baseline_gloss": row["literal_gloss_de"], "last_writer": "GDT684", "last_artifact": "V57_479_POSITION_INFORMATION_AUDIT.tsv", "change_chain": ["GDT684"], "baseline": row, **prior}
    stage_maps: dict[str, dict[tuple[str, str, int, str], dict[str, str]]] = {}
    stages = [
        ("GDT685", G685 / "V58_TARGET_POSITION_DEBT_DELTA.tsv", "new_literal_gloss_de"),
        ("GDT686", G686 / "V59_TARGET_POSITION_DEBT_DELTA.tsv", "new_literal_gloss_de"),
        ("GDT687", G687 / "V60_95_POSITION_SCOPE_DISPATCH.tsv", "v60_literal_gloss_de"),
        ("GDT689", G689 / "V62_50_POSITION_REVISIONS.tsv", "v62_literal_gloss_de"),
        ("GDT690", G690 / "V63_479_TOKEN_NOUN_BINDING.tsv", "v63_main_token_gloss_de"),
        ("GDT691", G691 / "V64_479_TOKEN_READER.tsv", "v64_token_gloss_de"),
        ("GDT692", G692 / "V65_479_TOKEN_READER.tsv", "v65_token_gloss_de"),
        ("GDT693", G693 / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv", "v66_selected_gloss_de"),
        ("GDT694", G694 / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv", "v67_token_gloss_de"),
        ("GDT695", G695 / "V68_479_TOKEN_FREEZE.tsv", "v68_token_gloss_de"),
    ]
    for gdt, path, gloss_field in stages:
        rows = read_tsv(path); mapping = {key(row): row for row in rows}; stage_maps[gdt] = mapping
        for position, row in mapping.items():
            if position not in state:
                raise AssertionError(f"unknown active position in {gdt}: {position}")
            new_gloss = row[gloss_field]; cell = state[position]
            if new_gloss != cell["gloss"]:
                cell["gloss"] = new_gloss; cell["last_writer"] = gdt; cell["last_artifact"] = path.name; cell["change_chain"].append(gdt)
                cell["position_assignment_writer_gdt"] = gdt; cell["semantic_card_origin_gdt"] = gdt
                cell["semantic_origin_artifact"] = path.relative_to(ROOT).as_posix(); cell["semantic_origin_label"] = "EXPLICIT_LATER_SEMANTIC_REVISION"
    active = read_tsv(ACTIVE)
    assert len(active) == 479 and {key(row) for row in active} == set(state)
    for row in active:
        assert state[key(row)]["gloss"] == row["v68_token_gloss_de"]
    expected_origins = Counter({"GDT676": 141, "GDT677": 2, "GDT678": 13, "GDT679": 12, "GDT680": 13, "GDT681": 13, "GDT683": 7})
    surviving_origins = Counter(cell["position_assignment_writer_gdt"] for cell in state.values() if cell["last_writer"] == "GDT684")
    assert surviving_origins == expected_origins, (surviving_origins, expected_origins)
    return active, state, stage_maps


def stage_rivals(position: tuple[str, str, int, str], last_writer: str, stage_maps: dict[str, dict[tuple[str, str, int, str], dict[str, str]]]) -> str:
    """Return only live/final rivals, never superseded earlier alternatives."""
    values: list[str] = []
    final_row = stage_maps["GDT694"].get(position)
    if final_row:
        for field in ("live_rivals_de", "v65_product_rival_de", "v67_local_rival_de"):
            value = final_row.get(field, "")
            if value and value not in {"NONE", "INHERITED", "N/A"}:
                values.append(value)
    if last_writer == "GDT686":
        row = stage_maps["GDT686"].get(position, {})
        values.extend(value for field in ("live_rival_de", "remaining_caveat") if (value := row.get(field, "")) and value != "NONE")
    elif last_writer == "GDT687":
        row = stage_maps["GDT687"].get(position, {})
        value = row.get("strongest_rival_de", "")
        if value and value != "NONE": values.append(value)
    return compact(values)


def build_global_rows(glossary: list[dict[str, str]], occurrence_map: dict[str, dict[str, Any]], master_entries: set[str], active_surfaces: set[str], active_reading_counts: Counter[str], controls: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []; named_dispatch = {"daiin", "dain", "ol", "y", "dy", "dchey"}
    for index, row in enumerate(sorted(glossary, key=lambda item: item["surface"]), 1):
        surface, gloss = row["surface"], row["working_meaning_de"]; info = occurrence_map[surface]
        occurrences, pages = info["count"], len(info["pages"]); _, _, attestation = attestation_scores(occurrences, pages)
        scope = row["scope_state"]; low, exploratory = strength_flags(row["strength"])
        invariance = 0 if occurrences <= 1 else 10 if scope == "KNOWN_EXACT_WHOLE" and occurrences >= 3 else 7 if scope == "KNOWN_EXACT_WHOLE" else 5 if surface in named_dispatch else 2
        parts = {"attestation": attestation, "invariance": invariance, "rule": rule_score(row["strength"]), "provenance": 4 if low else 8, "specificity": specificity_score(gloss, scope == "AMBIGUOUS_ACTIVE_RIVAL"), "stress_survival": 6}
        penalties: list[tuple[str, int]] = []; caps: list[tuple[str, int]] = []
        if exploratory:
            penalties.append(("LOW_EXPLORATORY_SOURCE", -18)); caps.append(("ALL_SEMANTIC_SOURCES_EXPLORATORY", 39))
        elif low:
            penalties.append(("LOW_SOURCE", -12)); caps.append(("ALL_SEMANTIC_SOURCES_LOW", 39))
        if scope == "AMBIGUOUS_ACTIVE_RIVAL":
            penalties.append(("AMBIGUOUS_ACTIVE_RIVAL", -10)); caps.append(("UNRESOLVED_SURFACE_RIVAL", 39))
        elif "READER_UNSTABLE" in scope:
            caps.append(("READER_UNSTABLE", 39))
        elif scope == "KNOWN_CONTEXT_LICENSED" and surface not in named_dispatch:
            caps.append(("CONTEXT_LICENSED_ONLY", 59))
        if occurrences == 0:
            caps.append(("NO_EXACT_ZL3B_OCCURRENCE", 19))
        elif occurrences == 1 and parts["rule"] <= 5:
            caps.append(("SINGLETON_LEARNED_WHOLE", 39))
        if exploratory and IDENTITY_RE.search(gloss):
            caps.append(("SPECIFIC_IDENTITY_WITHOUT_INDEPENDENT_IDENTITY_SIGNAL", 19))
        control = manual_control(controls, "GLOBAL_SURFACE", surface, gloss); floor = int(control["minimum_score"]) if control else 0
        if control: caps.append(("MANUAL_REALITY_CONTROL", int(control["maximum_score"])))
        scored = finish_score(parts, penalties, caps, floor)
        positive = [f"V48-Quelle {row['source']} mit Staerke {row['strength']} und Scope {scope}", f"{occurrences} exakte ZL3b-Vorkommen auf {pages} Seiten und {len(info['loci'])} Zeilen"]
        counter = ["keine unabhaengige Klartextzuordnung; Bedeutung bleibt Arbeitstheorie"]
        if low: counter.append("Quelle ist ausdruecklich LOW/EXPLORATORY")
        if occurrences <= 1: counter.append("kein seitenuebergreifender Bedeutungsbeleg")
        if scope != "KNOWN_EXACT_WHOLE": counter.append(f"Form-/Bedeutungsscope {scope} ist nicht global exakt")
        if control: positive.append(control["positive_evidence_de"]); counter.append(control["counterevidence_de"])
        output.append({
            "entity_type": "GLOBAL_SURFACE", "entity_id": f"GS{index:04d}", "surface": surface, "working_meaning_de": gloss,
            "form_level": form_level(scope, occurrences), "occurrence_count": occurrences, "page_count": pages, "locus_count": len(info["loci"]),
            "sections": compact(info["sections"]), "sample_loci": "|".join(info["samples"]) or "NONE", "source": row["source"], "strength": row["strength"], "scope_state": scope,
            "exact_master_entry": int(surface in master_entries), "active_surface": int(surface in active_surfaces), "active_reading_count": active_reading_counts[surface],
            "semantic_applicability": control["semantic_applicability"] if control else "SEMANTIC_WORKING_READING", **scored,
            "historical_confirmation": HISTORICAL, "historical_analogue": "NONE", "relation_word_delta": RELATION_WORD_DELTA,
            "positive_evidence_de": "; ".join(positive), "counterevidence_de": "; ".join(counter),
        })
    return output


def build_active_rows(active: list[dict[str, str]], state: dict[tuple[str, str, int, str], dict[str, Any]], stage_maps: dict[str, dict[tuple[str, str, int, str], dict[str, str]]], global_by_surface: dict[str, dict[str, Any]], controls: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    occurrence_rows: list[dict[str, Any]] = []
    span_map: dict[tuple[str, int], tuple[str, str]] = {}
    for span in read_tsv(G694 / "V67_3_BOUND_SPANS.tsv"):
        start, end = int(span["start_ordinal"]), int(span["end_ordinal"])
        for ordinal in range(start, end + 1):
            role = "LEFT" if ordinal == start else "RIGHT" if ordinal == end else "MEDIAL"
            span_map[(span["locus"], ordinal)] = (span["span_id"], role)
    for row in active:
        position = key(row); cell = state[position]; base = cell["baseline"]; rival = stage_rivals(position, cell["last_writer"], stage_maps)
        global_surface_row = global_by_surface.get(row["surface"])
        global_row = global_surface_row if global_surface_row and global_surface_row["working_meaning_de"] == row["v68_token_gloss_de"] else None
        debt_applies = cell["gloss"] == cell["baseline_gloss"]; low_current = debt_applies and base["low_or_exploratory_card"] == "1"
        span_id, span_role = span_map.get((row["locus"], int(row["token_ordinal"])), ("NONE", "NONE"))
        occurrence_rows.append({
            "page": row["page"], "locus": row["locus"], "token_ordinal": row["token_ordinal"], "surface": row["surface"], "working_meaning_de": row["v68_token_gloss_de"],
            "form_level": "F3_EXACT_ACTIVE_ZL3B_TOKEN", "v68_clause_type": row["v68_clause_type"], "v68_action_license": row["v68_action_license"], "v68_active_verb_occurrences": row["v68_active_verb_occurrences"],
            "last_semantic_writer": cell["last_writer"], "last_semantic_artifact": cell["last_artifact"], "semantic_change_chain": "|".join(cell["change_chain"]), "last_writer_evidence_de": STAGE_DESCRIPTIONS[cell["last_writer"]],
            "position_assignment_writer_gdt": cell["position_assignment_writer_gdt"], "semantic_card_origin_gdt": cell["semantic_card_origin_gdt"],
            "semantic_origin_artifact": cell["semantic_origin_artifact"], "semantic_origin_label": cell["semantic_origin_label"],
            "v57_baseline_gloss_de": cell["baseline_gloss"], "v57_debt_applicability": "APPLIES_TO_CURRENT_GLOSS" if debt_applies else "SUPERSEDED_BY_EXPLICIT_SEMANTIC_REPAIR",
            "v57_debt_severity": base["debt_severity"], "v57_primary_class": base["primary_class"], "v57_signals": base["signals"], "v57_identity_signals": base["identity_signals"], "v57_action_signals": base["action_signals"],
            "v57_specificity_open": base["specificity_open"], "v57_strict_card_debt": base["strict_card_debt"], "v57_strict_debt_categories": base["strict_debt_categories"],
            "v57_low_or_exploratory_applies": int(low_current), "v57_low_confidence_sources": base["low_confidence_sources"] if low_current else "SUPERSEDED_OR_NONE", "live_rivals_de": rival,
            "global_v48_semantic_match": int(bool(global_row)),
            "global_v48_prior_gloss_de": global_surface_row["working_meaning_de"] if global_surface_row else "NO_V48_EXACT_SURFACE_CARD",
            "global_v48_source": global_row["source"] if global_row else "NO_EXACT_SURFACE_GLOSS_MATCH", "global_v48_strength": global_row["strength"] if global_row else "NONE", "global_v48_scope_state": global_row["scope_state"] if global_row else "NONE",
            "bound_span_id": span_id, "bound_span_role": span_role,
            "bound_span_global_export_allowed": 0 if span_id != "NONE" else 1,
            "evidence_summary_de": f"Form exakt; aktuelle Glosse zuletzt {cell['last_writer']} zugewiesen; Kartenursprung {cell['semantic_card_origin_gdt']}; Signale {base['signals']}; Rivalen {rival}.",
            "historical_confirmation": HISTORICAL, "relation_word_delta": RELATION_WORD_DELTA,
        })
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in occurrence_rows: grouped[(row["surface"], row["working_meaning_de"])].append(row)
    surface_sense_count = Counter(surface for surface, _ in grouped); reading_rows: list[dict[str, Any]] = []
    for index, ((surface, gloss), rows) in enumerate(sorted(grouped.items()), 1):
        occurrences = len(rows); pages = len({row["page"] for row in rows}); loci = len({row["locus"] for row in rows}); _, _, attestation = attestation_scores(occurrences, pages)
        polysemous = surface_sense_count[surface] > 1; last_writer = rows[0]["last_semantic_writer"]; assert len({row["last_semantic_writer"] for row in rows}) == 1
        global_surface_row = global_by_surface.get(surface)
        global_row = global_surface_row if global_surface_row and global_surface_row["working_meaning_de"] == gloss else None
        global_strength = global_row["strength"] if global_row else ""; low_global, exploratory_global = strength_flags(global_strength)
        low_occurrences = sum(int(row["v57_low_or_exploratory_applies"]) for row in rows); rivals = compact(row["live_rivals_de"] for row in rows); live_rival = rivals != "NONE"
        scoring_live_rival = live_rival and surface != "dchey"
        action_positions = sum(row["v68_action_license"] != "NOT_ACTION_LICENSED" for row in rows); identity_positions = sum(row["v57_identity_signals"] != "NONE" for row in rows)
        semantic_origins = {row["semantic_card_origin_gdt"] for row in rows}
        invariance = 0 if occurrences == 1 else 5 if polysemous else 7 if occurrences == 2 else 10
        if surface == "dchey" or last_writer in {"GDT687", "GDT689"}: rule = 20
        elif last_writer == "GDT690" and occurrences >= 2: rule = 15
        elif last_writer != "GDT684": rule = 10
        elif action_positions: rule = max(15, rule_score(global_strength) if global_row else 0)
        elif semantic_origins & {"GDT677", "GDT678", "GDT679", "GDT680", "GDT681"}: rule = 15
        elif "GDT675" in semantic_origins: rule = 10
        elif global_row: rule = rule_score(global_strength)
        else: rule = 5
        provenance = 12 if last_writer != "GDT684" or action_positions or semantic_origins & {"GDT675", "GDT677", "GDT678", "GDT679", "GDT680", "GDT681", "GDT683"} else 4 if (low_occurrences or low_global) else 8
        focused_origin = any(re.fullmatch(r"GDT(?:67[5-9]|68[0-3])", origin) for origin in semantic_origins)
        parts = {"attestation": attestation, "invariance": invariance, "rule": rule, "provenance": provenance, "specificity": specificity_score(gloss, scoring_live_rival), "stress_survival": 10 if last_writer != "GDT684" or focused_origin else 6}
        penalties: list[tuple[str, int]] = []; caps: list[tuple[str, int]] = []
        applicable_debts = [row["v57_debt_severity"] for row in rows if row["v57_debt_applicability"] == "APPLIES_TO_CURRENT_GLOSS"]
        if "CRITICAL" in applicable_debts: penalties.append(("CURRENT_GDT684_CRITICAL_DEBT", -20))
        elif "MAJOR" in applicable_debts: penalties.append(("CURRENT_GDT684_MAJOR_DEBT", -10))
        later_semantic_audit = last_writer != "GDT684"; all_low = low_occurrences == occurrences or low_global
        if all_low and not later_semantic_audit:
            penalties.append(("ALL_CURRENT_SOURCES_LOW_OR_EXPLORATORY", -18 if exploratory_global or low_occurrences else -12)); caps.append(("NO_INDEPENDENT_LATER_SEMANTIC_AUDIT", 39))
            if exploratory_global and IDENTITY_RE.search(gloss): caps.append(("SPECIFIC_IDENTITY_WITHOUT_IDENTITY_SIGNAL", 19))
        elif all_low: penalties.append(("INHERITED_LOW_SOURCE_CAVEAT_AFTER_REPAIR", -6))
        if scoring_live_rival: penalties.append(("LIVE_RIVAL", -10)); caps.append(("UNRESOLVED_LIVE_RIVAL", 59))
        if occurrences == 1:
            caps.append(("SINGLETON", 59))
            if rule <= 5 or all_low: caps.append(("SINGLETON_WITHOUT_STRONG_RULE", 39))
        if polysemous and surface not in {"daiin", "dain", "dchey", "dy", "ol", "y"}:
            penalties.append(("UNEXPLAINED_MULTIGLOSS", -15)); caps.append(("NO_NAMED_SCOPE_DISPATCH", 39))
        control = manual_control(controls, "ACTIVE_READING", surface, gloss); floor = int(control["minimum_score"]) if control else 0
        if control: caps.append(("MANUAL_REALITY_CONTROL", int(control["maximum_score"])))
        scored = finish_score(parts, penalties, caps, floor)
        positive = [f"{occurrences} aktive exakte Positionen auf {pages} Seiten und {loci} Zeilen", f"letzte semantische Entscheidung {last_writer}: {STAGE_DESCRIPTIONS[last_writer]}", f"{action_positions} aktionslizenzierte und {identity_positions} identitaetssignalisierte Positionen"]
        counter = ["historisch unbestaetigt; Score bewertet nur die interne Arbeitstheorie"]
        if applicable_debts: counter.append("aktuelle GDT684-Schuld: " + compact(applicable_debts))
        if low_occurrences or low_global: counter.append("LOW/EXPLORATORY-Provenienz bleibt sichtbar")
        if global_surface_row and not global_row: counter.append("aelterer V48-Default ist superseded prior, nicht Evidenz der aktuellen Glosse: " + global_surface_row["working_meaning_de"])
        if live_rival: counter.append("lebender Rivale: " + rivals)
        if polysemous: counter.append(f"Oberflaeche besitzt {surface_sense_count[surface]} getrennte Kontextlesarten")
        if control: positive.append(control["positive_evidence_de"]); counter.append(control["counterevidence_de"])
        reading_rows.append({
            "entity_type": "ACTIVE_READING", "entity_id": f"AR{index:03d}", "surface": surface, "reading_id": f"{surface}#{sum(1 for prior in reading_rows if prior['surface'] == surface) + 1}",
            "working_meaning_de": gloss, "semantic_scope": "NAMED_CONTEXT_DISPATCH" if polysemous else "ACTIVE_EXACT_WHOLE_READING", "semantic_applicability": control["semantic_applicability"] if control else "SEMANTIC_WORKING_READING",
            "form_level": "F3_EXACT_ACTIVE_ZL3B_TOKEN", "occurrence_count": occurrences, "page_count": pages, "locus_count": loci, "surface_reading_count": surface_sense_count[surface], "action_licensed_positions": action_positions, "identity_signal_positions": identity_positions,
            "sample_loci": "|".join(sorted({row["locus"] for row in rows})[:6]), "last_semantic_writer": last_writer, "position_assignment_writers": compact(row["position_assignment_writer_gdt"] for row in rows), "semantic_card_origins": compact(row["semantic_card_origin_gdt"] for row in rows), "semantic_origin_artifacts": compact(row["semantic_origin_artifact"] for row in rows), "semantic_change_chains": compact(row["semantic_change_chain"] for row in rows), "source_gdts": compact(row["semantic_card_origin_gdt"] for row in rows), "source_artifacts": compact(row["last_semantic_artifact"] for row in rows),
            "gdt684_current_debt_counts": compact(f"{severity}:{applicable_debts.count(severity)}" for severity in sorted(set(applicable_debts))), "gdt684_repair_status": "CURRENT_DEBT_APPLIES" if applicable_debts else "SUPERSEDED_OR_NO_DEBT", "low_source_positions": low_occurrences, "live_rivals_de": rivals,
            "bound_span_ids": compact(row["bound_span_id"] for row in rows),
            "global_export_scope": "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT" if any(row["bound_span_id"] != "NONE" for row in rows) else "NAMED_CONTEXT_ONLY" if polysemous else "ACTIVE_WORKING_DEFAULT",
            **scored, "historical_confirmation": HISTORICAL, "historical_analogue": "NONE", "relation_word_delta": RELATION_WORD_DELTA,
            "positive_evidence_de": "; ".join(positive), "counterevidence_de": "; ".join(counter),
        })
    reading_id_by_pair = {(row["surface"], row["working_meaning_de"]): row["reading_id"] for row in reading_rows}
    for index, row in enumerate(occurrence_rows, 1):
        row["position_id"] = f"P{index:03d}"
        row["reading_id"] = reading_id_by_pair[(row["surface"], row["working_meaning_de"])]
    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in reading_rows: by_surface[row["surface"]].append(row)
    surface_rows: list[dict[str, Any]] = []
    for index, surface in enumerate(sorted(by_surface), 1):
        readings = by_surface[surface]; scores = [int(row["working_model_score_0_100_not_probability"]) for row in readings]; counts = sum(int(row["occurrence_count"]) for row in readings)
        surface_rows.append({
            "entity_type": "ACTIVE_SURFACE", "entity_id": f"AS{index:03d}", "surface": surface, "reading_count": len(readings), "working_meanings_de": " || ".join(row["working_meaning_de"] for row in readings), "occurrence_count": counts,
            "page_count": len({row["page"] for row in occurrence_rows if row["surface"] == surface}), "form_level": "F3_EXACT_ACTIVE_ZL3B_TOKEN", "surface_semantic_status": "CONTEXT_SPLIT__SEE_READING_ROWS" if len(readings) > 1 else readings[0]["working_model_level"],
            "minimum_working_score": min(scores), "maximum_working_score": max(scores), "minimum_working_level": level(min(scores)), "maximum_working_level": level(max(scores)), "reading_ids": "|".join(row["reading_id"] for row in readings), "source_gdts": compact(row["source_gdts"] for row in readings),
            "positive_evidence_de": f"{counts} aktive Positionen; {len(readings)} getrennte Lesart(en); Form im aktiven ZL3b-Text exakt.", "counterevidence_de": "Semantische Confidence steht in den Lesartzeilen; eine polyseme Form erhaelt bewusst keinen gemittelten Wortwert.", "historical_confirmation": HISTORICAL, "relation_word_delta": RELATION_WORD_DELTA,
        })
    return occurrence_rows, reading_rows, surface_rows


def build_master_rows(master: list[dict[str, str]], lineage: dict[str, dict[str, Any]], global_by_surface: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, row in enumerate(master, 1):
        entry, kind, gloss, status = row["entry"], row["kind"], row["working_meaning_de"], row["status"]; history = lineage[entry]; global_row = global_by_surface.get(entry)
        occurrences = int(global_row["occurrence_count"]) if global_row else 0; pages = int(global_row["page_count"]) if global_row else 0; _, _, attestation = attestation_scores(occurrences, pages)
        invariance = int(global_row["score_invariance"]) if global_row else 5 if history["versions_present"] >= 3 and history["meaning_revision_count"] == 0 else 2 if history["versions_present"] >= 2 else 0
        provenance = int(global_row["score_provenance"]) if global_row else 4 if "PROVISIONAL" in status or "EXPLOR" in status or "LOW" in status else 8 if "EXACT" in kind or "ATTESTED" in status else 0
        renderer_card = "PRACTICAL_RENDERING_CARD" in kind
        parts = {"attestation": attestation, "invariance": invariance, "rule": rule_score(status, kind), "provenance": provenance, "specificity": 0 if renderer_card else specificity_score(gloss, "RIVAL" in row["context_rule"].upper()), "stress_survival": 6 if history["versions_present"] >= 3 else 3}
        penalties: list[tuple[str, int]] = []; caps: list[tuple[str, int]] = []; status_upper = status.upper()
        if "EXPLOR" in status_upper: penalties.append(("EXPLORATORY_STATUS", -18)); caps.append(("EXPLORATORY_MASTER_CARD", 39))
        elif "LOW" in status_upper: penalties.append(("LOW_STATUS", -12)); caps.append(("LOW_MASTER_CARD", 39))
        if "PROVISIONAL" in status_upper: penalties.append(("PROVISIONAL_STATUS", -6)); caps.append(("PROVISIONAL_MASTER_CARD", 59))
        if "CONTEXT_RENDER" in status_upper or "CONTEXT_CARD_NOT_GLOBAL" in status_upper: caps.append(("CONTEXT_OR_RENDERER_CARD", 39))
        if renderer_card: caps.append(("RENDERER_CARD_NOT_WORD_MEANING", 19))
        if not global_row and parts["rule"] <= 5: caps.append(("NO_EXACT_CURRENT_SURFACE_CARRIER", 39))
        if occurrences == 1 and parts["rule"] <= 5: caps.append(("SINGLETON_LEARNED_CARD", 39))
        scored = finish_score(parts, penalties, caps); entry_scope = "EXACT_GLOBAL_SURFACE_CARD" if global_row else "RENDERER_CARD_NOT_WORD" if renderer_card else "MASTER_RULE_OR_COMPOSITION_CARD"
        positive = [f"V48-Masterkarte {kind} mit Status {status}", f"seit V{history['first_version']} ({history['first_experiment']}) in {history['versions_present']} Versionen gefuehrt"]
        if global_row: positive.append(f"exakter Surface-Traeger mit {occurrences} Belegen auf {pages} Seiten")
        counter = ["Masterkarten sind Regel-/Rendererobjekte und nicht automatisch selbststaendige Woerter", "historisch unbestaetigt"]
        if not global_row: counter.append("kein gleichnamiger exakter Eintrag im globalen V48-Wortglossar")
        if "PROVISIONAL" in status_upper: counter.append("Status ist ausdruecklich PROVISIONAL")
        if renderer_card: counter.append("reine praktische Rendererkarte; keine eigenstaendige Wortbedeutung")
        output.append({
            "entity_type": "MASTER_CARD", "entity_id": f"MC{index:04d}", "entry": entry, "entry_scope": entry_scope, "kind": kind, "working_meaning_de": gloss, "composition": row["composition"], "context_rule": row["context_rule"], "status": status,
            **history, "exact_global_surface_match": int(bool(global_row)), "exact_occurrence_count": occurrences, "exact_page_count": pages, "form_level": global_row["form_level"] if global_row else "NA_RULE_OR_RENDERER_CARD", "semantic_applicability": "RENDERER_NOT_WORD_MEANING" if renderer_card else "SEMANTIC_WORKING_CARD",
            **scored, "historical_confirmation": HISTORICAL, "historical_analogue": "NONE", "relation_word_delta": RELATION_WORD_DELTA, "positive_evidence_de": "; ".join(positive), "counterevidence_de": "; ".join(counter),
        })
    return output


def make_complete_word_rows(global_rows: list[dict[str, Any]], active_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_surfaces = {row["surface"] for row in active_rows}; selected: list[dict[str, Any]] = []
    for row in global_rows:
        if row["surface"] not in active_surfaces:
            selected.append({"surface": row["surface"], "reading_id": row["surface"] + "#GLOBAL", "working_meaning_de": row["working_meaning_de"], "current_layer": "GLOBAL_V48_DEFAULT", "semantic_scope": row["scope_state"], "semantic_applicability": row["semantic_applicability"], "form_level": row["form_level"], "occurrence_count": row["occurrence_count"], "page_count": row["page_count"], "locus_count": row["locus_count"], "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"], "working_model_level": row["working_model_level"], "source_gdts": row["source"], "positive_evidence_de": row["positive_evidence_de"], "counterevidence_de": row["counterevidence_de"], "historical_confirmation": HISTORICAL, "historical_analogue": row["historical_analogue"], "relation_word_delta": RELATION_WORD_DELTA})
    for row in active_rows:
        selected.append({"surface": row["surface"], "reading_id": row["reading_id"], "working_meaning_de": row["working_meaning_de"], "current_layer": "ACTIVE_V68_READING", "semantic_scope": row["semantic_scope"], "semantic_applicability": row["semantic_applicability"], "form_level": row["form_level"], "occurrence_count": row["occurrence_count"], "page_count": row["page_count"], "locus_count": row["locus_count"], "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"], "working_model_level": row["working_model_level"], "source_gdts": row["source_gdts"], "positive_evidence_de": row["positive_evidence_de"], "counterevidence_de": row["counterevidence_de"], "historical_confirmation": HISTORICAL, "historical_analogue": row["historical_analogue"], "relation_word_delta": RELATION_WORD_DELTA})
    return sorted(selected, key=lambda row: (row["surface"], row["reading_id"]))


def rubric_rows() -> list[dict[str, str]]:
    return [
        {"dimension": "FORM", "rule_id": "F0", "condition": "kein exaktes ZL3b-Vorkommen", "points_or_cap": "label only", "meaning": "keine Formattestation"},
        {"dimension": "FORM", "rule_id": "F1", "condition": "ambig oder reader-unstabil", "points_or_cap": "label only", "meaning": "schwache Segmentierung"},
        {"dimension": "FORM", "rule_id": "F2", "condition": "kontextlizenziert oder Reader-Variante", "points_or_cap": "label only", "meaning": "lokal lesbare Form"},
        {"dimension": "FORM", "rule_id": "F3", "condition": "exakte aktive oder globale ZL3b-Oberflaeche", "points_or_cap": "label only", "meaning": "Form sicherer als Semantik"},
        {"dimension": "WORKING", "rule_id": "A", "condition": "Vorkommen 1/2/3-4/5-8/9+ und Seiten 1/2/3-4/5-8/9+", "points_or_cap": "0-20", "meaning": "Attestation"},
        {"dimension": "WORKING", "rule_id": "I", "condition": "Singleton bis vollstaendig invariante Zuordnung", "points_or_cap": "0-10", "meaning": "Invarianz der benannten Lesart"},
        {"dimension": "WORKING", "rule_id": "R", "condition": "kein Pfad bis produktives Raster", "points_or_cap": "0-25 (aktuell max 20)", "meaning": "Regel-/Kompositionspfad"},
        {"dimension": "WORKING", "rule_id": "P", "condition": "unexportiert/LOW/exakte Karte/exakte Ordinalprovenienz", "points_or_cap": "0-15", "meaning": "Provenienz"},
        {"dimension": "WORKING", "rule_id": "S", "condition": "strukturell bis lokal voll gebunden", "points_or_cap": "0-15", "meaning": "Spezifitaet und Scope"},
        {"dimension": "WORKING", "rule_id": "T", "condition": "in-sample bis fokussierter Rival-/Kontrollaudit", "points_or_cap": "0-15", "meaning": "Stress und Survival"},
        {"dimension": "CAP", "rule_id": "LOW", "condition": "nur LOW/EXPL ohne spaeteren Semantikaudit", "points_or_cap": "-12/-18; max W1", "meaning": "Fluessigere Prosa hebt schwache Quelle nicht auf"},
        {"dimension": "CAP", "rule_id": "DEBT", "condition": "aktuelle GDT684 CRITICAL/MAJOR-Schuld", "points_or_cap": "-20/-10", "meaning": "nur wenn dieselbe aktuelle Glosse betroffen ist"},
        {"dimension": "CAP", "rule_id": "RIVAL", "condition": "lebender unaufgeloester Rivale", "points_or_cap": "-10; max W2", "meaning": "Rivale bleibt im Apparatus"},
        {"dimension": "CAP", "rule_id": "REL", "condition": "GDT696-GDT709 Relationskanten", "points_or_cap": "+0", "meaning": "alle sind ZERO_WORD_DELTA"},
        {"dimension": "LEVEL", "rule_id": "W0", "condition": "0-19", "points_or_cap": "placeholder", "meaning": "semantisch leer oder nur strukturell"},
        {"dimension": "LEVEL", "rule_id": "W1", "condition": "20-39", "points_or_cap": "weak", "meaning": "schwache Arbeitshypothese"},
        {"dimension": "LEVEL", "rule_id": "W2", "condition": "40-59", "points_or_cap": "provisional", "meaning": "provisorische Arbeitshypothese"},
        {"dimension": "LEVEL", "rule_id": "W3", "condition": "60-79", "points_or_cap": "solid", "meaning": "solide innerhalb der Arbeitstheorie"},
        {"dimension": "LEVEL", "rule_id": "W4", "condition": "80-100", "points_or_cap": "strong", "meaning": "derzeit durch fehlenden Prospektivtest gedeckelt; keine Entzifferung"},
        {"dimension": "HISTORICAL", "rule_id": "H0", "condition": "keine unabhaengige Voynich-Klartext-Zuordnung", "points_or_cap": "alle Eintraege", "meaning": "historisch unbestaetigt"},
    ]


def source_registry() -> list[dict[str, str]]:
    specs = [
        ("GDT623-GDT671", "WORKING_DICTIONARY_V2..V48.tsv", "vollstaendige Masterkarten-Lineage"),
        ("GDT671", MASTER.relative_to(ROOT).as_posix(), "2115 aktuelle Masterkarten"), ("GDT671", GLOSSARY.relative_to(ROOT).as_posix(), "1430 globale exakte Oberflaechendefaults"), ("GDT671", COVERAGE.relative_to(ROOT).as_posix(), "4128 Zeilen fuer exakte Surface-Zaehler"),
        ("GDT684", (G684 / "V57_479_POSITION_INFORMATION_AUDIT.tsv").relative_to(ROOT).as_posix(), "Basisdebt und sichtbare Signale"), ("GDT685", (G685 / "V58_TARGET_POSITION_DEBT_DELTA.tsv").relative_to(ROOT).as_posix(), "V58 Bedeutungsreparaturen"), ("GDT686", (G686 / "V59_TARGET_POSITION_DEBT_DELTA.tsv").relative_to(ROOT).as_posix(), "V59 Wertachsenentscheidungen"), ("GDT687", (G687 / "V60_95_POSITION_SCOPE_DISPATCH.tsv").relative_to(ROOT).as_posix(), "V60 Action/Result/Boundary"), ("GDT689", (G689 / "V62_50_POSITION_REVISIONS.tsv").relative_to(ROOT).as_posix(), "V62 dy-Schwesterrevisionen"),
        ("GDT690", (G690 / "V63_479_TOKEN_NOUN_BINDING.tsv").relative_to(ROOT).as_posix(), "V63 Nomen und Rivalen"), ("GDT691", (G691 / "V64_479_TOKEN_READER.tsv").relative_to(ROOT).as_posix(), "V64 Zubereitungskopfrollen"), ("GDT692", (G692 / "V65_479_TOKEN_READER.tsv").relative_to(ROOT).as_posix(), "V65 Fraktionskomposition"), ("GDT693", (G693 / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv").relative_to(ROOT).as_posix(), "V66 AR-Tournament"), ("GDT694", (G694 / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv").relative_to(ROOT).as_posix(), "V67 letzte Wortrevisionen"), ("GDT695", ACTIVE.relative_to(ROOT).as_posix(), "V68 aktiver Wortfreeze"),
        ("GDT696-GDT709", "relation experiment manifests", "ausdruecklich +0 Wortconfidence (ZERO_WORD_DELTA)"), ("GDT710", CONTROLS.relative_to(ROOT).as_posix(), "manuelle Reality-Controls und transparente Caps"),
    ]
    return [{"source": source, "artifact_or_family": artifact, "use": use, "word_confidence_delta": "0" if source == "GDT696-GDT709" else "RUBRIC_DEPENDENT"} for source, artifact, use in specs]


def write_report(complete: list[dict[str, Any]], active_readings: list[dict[str, Any]]) -> None:
    complete_levels = Counter(row["working_model_level"] for row in complete)
    active_levels = Counter(row["working_model_level"] for row in active_readings)

    def selected(surface: str, starts: str = "") -> dict[str, Any]:
        hits = [row for row in active_readings if row["surface"] == surface and row["working_meaning_de"].startswith(starts)]
        assert len(hits) == 1
        return hits[0]

    examples = [
        ("`dchey` Aktionslesart", selected("dchey", "Eine"), "neun scope-konsistente Aktionsbelege auf neun Seiten"),
        ("`dchey` Resultatlesart", selected("dchey", "fertige"), "fünf getrennte Resultatbelege auf fünf Seiten"),
        ("`chol = trocken`", selected("chol"), "wiederholter Zustandswert nach expliziter GDT685-Reparatur"),
        ("`qokaiin = heiß, Grad III`", selected("qokaiin"), "geordnete Wertzelle plus sichtbarer Qualitätskopf"),
        ("`pchedaiin`", selected("pchedaiin"), "zwei konsistente Kompositionsbelege, aber offene Achse und Identität"),
        ("`olkar`", selected("olkar"), "häufig, jedoch weiterhin lokale provisorische Holzbindung"),
        ("`shx = eingeweichtes Gummi`", selected("shx"), "LOW-Singleton; Feuchte sichtbar, Gummi nicht unabhängig belegt"),
    ]
    lines = [
        "# GDT710 — Vollständiges Wörterbuch mit Confidence und Evidenz", "", f"Status: `{STATUS}`", "",
        "## Ergebnis", "",
        "Die primäre Worttabelle enthält 1.582 verschiedene Oberflächenformen und 1.594 Lesarten. Sie verwendet für jede der 320 aktiven Formen den neueren V68-Sinnbestand und für die übrigen Formen den globalen V48-Default. Polyseme Formen werden nicht zusammengemittelt.", "",
        "Die 2.115 Zeilen des Master-Wörterbuchs sind separat bewertet, weil darunter Regeln und 563 praktische Renderer-Karten stehen. Eine Renderer-Karte ist kein zusätzliches Voynich-Wort.", "",
        "Jede Zeile nennt positive Evidenz, Gegenbeleg, Formniveau, sechs Scorekomponenten, Abzüge/Caps und den letzten semantischen Writer. Der Zahlenwert ist ein Auditindex innerhalb der Arbeitstheorie, keine Wahrscheinlichkeit.", "",
        "Nur 127/479 aktive Positionen stimmen zugleich in Surface und Gloss mit V48 überein. Weitere 152 haben dieselbe Surface, aber einen später revidierten Gloss; 200 besitzen keine V48-Surfacekarte. Alte V48-Glossen sind dann superseded prior, nicht Evidenz der neuen Bedeutung.", "",
        "## Verteilung der vollständigen Worttabelle", "", "| Level | Lesarten |", "|---|---:|",
    ]
    lines.extend(f"| `{name}` | {count} |" for name, count in sorted(complete_levels.items()))
    lines += ["", "## Aktive 332 Lesarten", "", "| Level | Lesarten |", "|---|---:|"]
    lines.extend(f"| `{name}` | {count} |" for name, count in sorted(active_levels.items()))
    lines += [
        "", "Sechs Formen sind polysem und besitzen eigene Sinnzeilen: `daiin`, `dain`, `dchey`, `dy`, `ol`, `y`. Die abstrakten globalen Wertzellen `daiin/dain` sind stabiler als jede konkrete lokale Grad-/Mengenbindung; `dchey` erreicht W3 nur innerhalb seines benannten Action/Result-Scopes; `dy/y` können formal brauchbar sein, bleiben semantisch strukturell.",
        "", "## Reality-Check an Schlüsselwörtern", "", "| Lesart | Score/Level | Warum |", "|---|---:|---|",
    ]
    for label, row, why in examples:
        lines.append(f"| {label} | {row['working_model_score_0_100_not_probability']} / {row['working_model_level'].split('_', 1)[0]} | {why} |")
    local_values = [int(row["working_model_score_0_100_not_probability"]) for row in active_readings if row["surface"] in {"daiin", "dain"}]
    structural_values = [int(row["working_model_score_0_100_not_probability"]) for row in active_readings if row["surface"] in {"dy", "y"}]
    lines += [
        f"| konkrete `daiin/dain`-Bindungen | {min(local_values)}–{max(local_values)} / W1 | jeweils lokaler Grad-/Mengenentscheid mit lebendem Rivalen |",
        f"| freies `dy/y` | höchstens {max(structural_values)} / W0 | struktureller/punktueller Renderer, kein portables Wort |", "",
        "Die drei gebundenen V67-Spans B001–B003 sind an sechs Positionen markiert und haben `bound_span_global_export_allowed=0`; eine kombinierte Spanbedeutung wird nicht doppelt als zwei Lexemevidenzen gezählt.", "",
        "## Historische Grenze", "", f"Alle {len(complete)} aktuellen Wortlesarten und alle 2.115 Masterkarten stehen auf `H0_NONE`. Zeitnahe Fachbuch- oder Kürzelanalogien wären Kategorienvergleiche, keine Bestätigung einer Voynich-Klartextzuordnung.", "",
        "## Nullbeitrag der Relationsrunden", "", "GDT696 bis GDT709 sind `ZERO_WORD_DELTA`. C019, C021, A048 und alle anderen Relationskanten geben daher exakt null Punkte zur Wortconfidence.", "",
        "## Dateien", "", "- `V83_COMPLETE_WORD_CONFIDENCE.tsv`: primäre vollständige Wort-/Sinnliste", "- `V83_2115_MASTER_CARD_CONFIDENCE.tsv`: alle Masterkarten, inklusive Regel-/Rendererobjekte", "- `V83_1430_GLOBAL_SURFACE_CONFIDENCE.tsv`: globaler V48-Snapshot", "- `V83_332_LIVE_READING_CONFIDENCE.tsv`: aktive Sinne", "- `V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv`: positionsgenaue Belegkette", "- `V83_CONFIDENCE_RUBRIC.tsv`: vollständige Rubrik", "",
        "## Claim ceiling", "", "Die Ausgabe ordnet die vorhandene explorative Arbeitstheorie und macht ihre Schuld sichtbar. Sie bestätigt kein einziges historisches Lexem, keine Sprache, keinen Codebook-Schlüssel und keinen Klartext.", "",
    ]
    (EXP / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    master, glossary, coverage, controls = read_tsv(MASTER), read_tsv(GLOSSARY), read_tsv(COVERAGE), read_tsv(CONTROLS)
    assert len(master) == len({row["entry"] for row in master}) == 2115; assert len(glossary) == len({row["surface"] for row in glossary}) == 1430
    occurrence_map = global_occurrences(coverage, {row["surface"] for row in glossary}); active, state, stage_maps = build_active_state(); active_surfaces = {row["surface"] for row in active}; active_pairs = {(row["surface"], row["v68_token_gloss_de"]) for row in active}; active_reading_counts = Counter(surface for surface, _ in active_pairs)
    global_rows = build_global_rows(glossary, occurrence_map, {row["entry"] for row in master}, active_surfaces, active_reading_counts, controls); global_by_surface = {row["surface"]: row for row in global_rows}
    occurrence_rows, active_readings, active_surface_rows = build_active_rows(active, state, stage_maps, global_by_surface, controls); lineage = build_lineage(master); master_rows = build_master_rows(master, lineage, global_by_surface); complete_rows = make_complete_word_rows(global_rows, active_readings)
    assert len(occurrence_rows) == 479 and len(active_surface_rows) == 320 and len(active_readings) == 332; assert len(master_rows) == 2115 and len(global_rows) == 1430; assert len({row["surface"] for row in complete_rows}) == 1582 and len(complete_rows) == 1594
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete_rows + active_readings + global_rows + master_rows)
    for name, rows in [("V83_1430_GLOBAL_SURFACE_CONFIDENCE.tsv", global_rows), ("V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv", occurrence_rows), ("V83_332_LIVE_READING_CONFIDENCE.tsv", active_readings), ("V83_320_LIVE_SURFACE_CONFIDENCE.tsv", active_surface_rows), ("V83_2115_MASTER_CARD_CONFIDENCE.tsv", master_rows), ("V83_COMPLETE_WORD_CONFIDENCE.tsv", complete_rows)]: write_tsv(ART / name, list(rows[0]), rows)
    rubric = rubric_rows(); registry = source_registry(); write_tsv(ART / "V83_CONFIDENCE_RUBRIC.tsv", list(rubric[0]), rubric); write_tsv(ART / "V83_EVIDENCE_SOURCE_REGISTRY.tsv", list(registry[0]), registry)
    writer_counts = Counter(row["last_semantic_writer"] for row in occurrence_rows)
    result = {"experiment_id": "GDT710", "status": STATUS, "master_cards": len(master_rows), "global_surfaces": len(global_rows), "complete_word_surfaces": len({row["surface"] for row in complete_rows}), "complete_word_readings": len(complete_rows), "active_surfaces": len(active_surface_rows), "active_readings": len(active_readings), "active_occurrences": len(occurrence_rows), "active_polysemous_surfaces": sorted(surface for surface, count in active_reading_counts.items() if count > 1), "global_zero_exact_occurrence_surfaces": sorted(surface for surface, info in occurrence_map.items() if info["count"] == 0), "complete_level_counts": dict(sorted(Counter(row["working_model_level"] for row in complete_rows).items())), "active_level_counts": dict(sorted(Counter(row["working_model_level"] for row in active_readings).items())), "master_level_counts": dict(sorted(Counter(row["working_model_level"] for row in master_rows).items())), "active_last_semantic_writer_positions": dict(sorted(writer_counts.items())), "historical_confirmation": HISTORICAL, "historically_confirmed_words": 0, "relation_word_delta": 0, "score_is_probability": False, "claim_ceiling": "complete confidence/evidence inventory inside the exploratory model; no plaintext or historically confirmed word"}
    (ART / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"); write_report(complete_rows, active_readings); print(STATUS); print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
