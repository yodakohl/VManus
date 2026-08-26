#!/usr/bin/env python3
"""Rank GDT493 composed cells by exact old frame-family support."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt494_composed_cell_family_support_ranking"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
COMPOSED_IN = G493 / "gdt493_73_composed_working_cells.tsv"
G493_RESULT_IN = G493 / "gdt493_result.json"
RANKED = OUT / "gdt494_73_ranked_composed_cells.tsv"
TIER_A = OUT / "gdt494_27_tier_a_multihead_cards.tsv"
TIER_B = OUT / "gdt494_19_tier_b_single_head_cards.tsv"
TIER_C = OUT / "gdt494_5_tier_c_tr_pair_only_cards.tsv"
TIER_D = OUT / "gdt494_22_tier_d_cross_register_only_cards.tsv"
NONTR_SUPPORT = OUT / "gdt494_105_same_register_nontr_support_cells.tsv"
PAIR_SUPPORT = OUT / "gdt494_21_same_register_opposite_tr_cells.tsv"
CROSS_REGISTER = OUT / "gdt494_98_same_action_cross_register_cells.tsv"
FRAME_COVERAGE = OUT / "gdt494_11_frame_ranking_coverage.tsv"
REGISTER_COVERAGE = OUT / "gdt494_5_register_ranking_coverage.tsv"
READABLE = OUT / "GDT494_COMPOSED_CELL_FAMILY_SUPPORT_RANKING.md"
RESULT = OUT / "gdt494_result.json"
STATUS = "TWENTY_SEVEN_MULTIHEAD_PRIORITY_CARDS__FORTY_SIX_NONTR_SUPPORTED__ALL_SEVENTY_THREE_CROSS_REGISTER_ANCHORED"
ACTION_ROOTS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
TIER_ORDER = {
    "A_MULTIHEAD_SAME_REGISTER": 0,
    "B_SINGLE_NONTR_HEAD": 1,
    "C_OPPOSITE_TR_ONLY": 2,
    "D_CROSS_REGISTER_ONLY": 3,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_readable(
    ranked: list[dict[str, object]],
    frames: list[dict[str, object]],
    registers: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT494 — Priorität der 73 zusammengesetzten T/R-Karten",
        "",
        "GDT494 ändert keine GDT493-Lesung und wertet keine Komposition zur Beobachtung auf. Es sortiert die 73 `COMPOSED_WORKING`-Karten ausschließlich danach, welche exakten alten GDT416-Handlungsköpfe denselben formalen Rest im selben Register bereits tragen.",
        "",
        f"- Rangierte Arbeitskarten: **{result['ranked_composed_cell_count']}/73**.",
        f"- Tier A, mindestens zwei andere Nicht-T/R-Köpfe im selben Register: **{result['tier_a_count']}**.",
        f"- Tier B, genau ein anderer Nicht-T/R-Kopf: **{result['tier_b_count']}**.",
        f"- Tier C, nur die lokale T/R-Gegenaktion: **{result['tier_c_count']}**.",
        f"- Tier D, nur dieselbe Zielhandlung in anderen Registern: **{result['tier_d_count']}**.",
        f"- Karten mit irgendeinem Nicht-T/R-Kopf im selben Register: **{result['nontr_supported_target_count']}**; mit irgendeiner lokalen Familienstütze: **{result['same_register_supported_target_count']}**.",
        f"- Karten mit derselben Zielhandlung in einem anderen Register: **{result['cross_register_anchored_target_count']}/73**.",
        "",
        "## Ranglogik",
        "",
        "Es gibt keinen vermischten Geheimscore. Zuerst zählt die verständliche Stufe A–D. Innerhalb einer Stufe folgen: mehr verschiedene Nicht-T/R-Köpfe, mehr ihrer Eventträger, vorhandene T/R-Gegenseite, mehr andere Register mit derselben Zielhandlung, dann Rezept und Register. Jede Karte bleibt `COMPOSED_WORKING`.",
        "",
    ]
    by_tier: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in ranked:
        by_tier[str(row["priority_tier"])].append(row)
    headings = {
        "A_MULTIHEAD_SAME_REGISTER": "Tier A — mindestens zwei andere Fachhandlungen im selben Register",
        "B_SINGLE_NONTR_HEAD": "Tier B — ein anderer Fachhandlungskopf im selben Register",
        "C_OPPOSITE_TR_ONLY": "Tier C — nur die beobachtete T/R-Gegenseite",
        "D_CROSS_REGISTER_ONLY": "Tier D — nur registerübergreifende Zielhandlungsstütze",
    }
    for tier in TIER_ORDER:
        lines.extend([
            f"## {headings[tier]} (`{tier}`)",
            "",
            "| Rang | Rezept | Register | Arbeitslesung | lokale Nicht-T/R-Köpfe | T/R-Paar | andere Zielregister | Zustand |",
            "|---:|---|---|---|---|---|---:|---|",
        ])
        for row in by_tier[tier]:
            lines.append(f"| {row['global_priority_rank']} | `{row['action_recipe']}` | {row['register']} | {row['composed_working_phrase_de']} | `{row['same_register_nontr_roots']}` | {row['opposite_tr_observed']} | {row['same_action_other_register_count']} | {row['state_warning']} |")
        lines.append("")
    lines.extend([
        "## Rahmenprofil",
        "",
        "| Rahmen | Karten | A | B | C | D |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in frames:
        lines.append(f"| `{row['frozen_frame']}` | {row['composed_cell_count']} | {row['tier_a_count']} | {row['tier_b_count']} | {row['tier_c_count']} | {row['tier_d_count']} |")
    lines.extend([
        "",
        "## Registerprofil",
        "",
        "| Register | Karten | A | B | C | D |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in registers:
        lines.append(f"| {row['register']} | {row['composed_cell_count']} | {row['tier_a_count']} | {row['tier_b_count']} | {row['tier_c_count']} | {row['tier_d_count']} |")
    lines.extend([
        "",
        "## Was Tier A praktisch bedeutet",
        "",
        "Die 27 A-Karten sind die besten gegenwärtigen Arbeitsvorhersagen innerhalb der geschlossenen 26-Seiten-Basis. Beispiel: celestial `T+AIIN` und `R+AIIN` sind noch nicht als ganze T/R-Sätze belegt, aber derselbe WERT-Rahmen steht dort bereits mit OK, K, S und CHD. Herbal `T/R+CH+E+Y` hat denselben Rest bereits mit OK, K und S. Das macht die neue T/R-Füllung kompositionell natürlich, ohne ihre Oberfläche oder tatsächliche Vorkunft vorherzusagen.",
        "",
        "Tier D bleibt ebenfalls lesbar, aber schwächer: Dort kennen wir die Zielhandlung mit diesem Rahmen aus einem anderen Register und jeden Slot lokal, jedoch noch keinen anderen kompletten Handlungskopf im Zielregister.",
        "",
        "## Nächster Schritt",
        "",
        "Verdichte die 27 Tier-A-Karten zu einem kurzen Zukunftsblatt mit Komponentenlesung, owner-lokalem Satz, allen lokalen Alternativköpfen und der expliziten Warnung `KEINE OBERFLÄCHENVORHERSAGE`. Danach kann dasselbe Rankingprinzip auf andere eng begrenzte Aktionspaare angewendet werden, ohne die Seiten zu öffnen.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES_IN)
    composed = read_tsv(COMPOSED_IN)
    g493_result = json.loads(G493_RESULT_IN.read_text(encoding="utf-8"))
    if (len(clauses), len(composed)) != (4576, 73):
        raise RuntimeError("Input count drift")
    if g493_result.get("status") != "ONE_HUNDRED_TEN_OWNER_REALIZATIONS__THIRTY_SEVEN_OBSERVED__SEVENTY_THREE_COMPOSED_WORKING":
        raise RuntimeError("GDT493 route drift")
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)

    draft_rows: list[dict[str, object]] = []
    nontr_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    cross_rows: list[dict[str, object]] = []
    for source in composed:
        frame = source["frozen_frame"]
        target_action = source["action_root"]
        register = source["register"]
        local_nontr: list[tuple[str, list[dict[str, str]]]] = []
        local_pair: list[tuple[str, list[dict[str, str]]]] = []
        for alternate_action in ACTION_ROOTS:
            if alternate_action == target_action:
                continue
            alternate_recipe = frame.replace("@ACTION", alternate_action)
            local = clauses_by_recipe_register[(alternate_recipe, register)]
            if not local:
                continue
            support_row = {
                "support_cell_id": "",
                "target_realization_cell_id": source["realization_cell_id"],
                "frozen_frame": frame,
                "target_action_root": target_action,
                "target_action_recipe": source["action_recipe"],
                "register": register,
                "alternate_action_root": alternate_action,
                "alternate_action_recipe": alternate_recipe,
                "event_count": len(local),
                "page_count": len({row["physical_page"] for row in local}),
                "pages": "|".join(sorted({row["physical_page"] for row in local})),
                "observed_clause_form_count": len({row["imperative_clause_de"] for row in local}),
                "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in local})),
                "all_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
                "exact_same_register_frame_support": "YES",
            }
            if alternate_action in {"T", "R"}:
                local_pair.append((alternate_action, local))
                support_row["support_cell_id"] = f"G494-TRS{len(pair_rows) + 1:03d}"
                pair_rows.append(support_row)
            else:
                local_nontr.append((alternate_action, local))
                support_row["support_cell_id"] = f"G494-NS{len(nontr_rows) + 1:03d}"
                nontr_rows.append(support_row)

        same_action_registers: list[tuple[str, list[dict[str, str]]]] = []
        for other_register in REGISTER_ORDER:
            if other_register == register:
                continue
            local = clauses_by_recipe_register[(source["action_recipe"], other_register)]
            if not local:
                continue
            same_action_registers.append((other_register, local))
            cross_rows.append({
                "cross_register_cell_id": f"G494-CR{len(cross_rows) + 1:03d}",
                "target_realization_cell_id": source["realization_cell_id"],
                "frozen_frame": frame,
                "action_root": target_action,
                "action_recipe": source["action_recipe"],
                "target_register": register,
                "observed_other_register": other_register,
                "event_count": len(local),
                "page_count": len({row["physical_page"] for row in local}),
                "pages": "|".join(sorted({row["physical_page"] for row in local})),
                "observed_clause_form_count": len({row["imperative_clause_de"] for row in local}),
                "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in local})),
                "same_action_and_formal_frame": "YES",
                "exact_observed_other_register_cell": "YES",
            })

        nontr_count = len(local_nontr)
        if nontr_count >= 2:
            tier = "A_MULTIHEAD_SAME_REGISTER"
            reason = "AT_LEAST_TWO_EXACT_NONTR_HEADS_IN_TARGET_REGISTER"
        elif nontr_count == 1:
            tier = "B_SINGLE_NONTR_HEAD"
            reason = "ONE_EXACT_NONTR_HEAD_IN_TARGET_REGISTER"
        elif local_pair:
            tier = "C_OPPOSITE_TR_ONLY"
            reason = "EXACT_OPPOSITE_TR_HEAD_IN_TARGET_REGISTER_ONLY"
        else:
            tier = "D_CROSS_REGISTER_ONLY"
            reason = "SAME_TARGET_ACTION_OBSERVED_ONLY_IN_OTHER_REGISTERS"
        draft_rows.append({
            "global_priority_rank": 0,
            "tier_rank": 0,
            "priority_tier": tier,
            "priority_reason": reason,
            "source_realization_cell_id": source["realization_cell_id"],
            "frozen_frame": frame,
            "action_root": target_action,
            "action_recipe": source["action_recipe"],
            "register": register,
            "portable_component_trace_de": source["portable_component_trace_de"],
            "owner_local_slot_trace_de": source["owner_local_slot_trace_de"],
            "composed_working_phrase_de": source["display_phrase_de"],
            "evidence_status_retained": source["evidence_status"],
            "state_requirement": source["state_requirement"],
            "state_warning": "ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT" if source["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" else "NONE",
            "same_register_nontr_head_count": nontr_count,
            "same_register_nontr_roots": "|".join(action for action, _ in local_nontr) or "NONE",
            "same_register_nontr_event_count": sum(len(local) for _, local in local_nontr),
            "same_register_nontr_clause_form_count": sum(len({row["imperative_clause_de"] for row in local}) for _, local in local_nontr),
            "opposite_tr_observed": "YES" if local_pair else "NO",
            "opposite_tr_root": local_pair[0][0] if local_pair else "NONE",
            "opposite_tr_event_count": sum(len(local) for _, local in local_pair),
            "same_action_other_register_count": len(same_action_registers),
            "same_action_other_registers": "|".join(register_name for register_name, _ in same_action_registers),
            "same_action_cross_register_event_count": sum(len(local) for _, local in same_action_registers),
            "same_register_family_supported": "YES" if local_nontr or local_pair else "NO",
            "cross_register_same_action_anchored": "YES" if same_action_registers else "NO",
            "all_slot_values_old": source["all_recipe_value_cells_observed"],
            "composed_working_label_retained": "YES" if source["evidence_status"] == "COMPOSED_WORKING" else "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
        })

    ranked_rows = sorted(
        draft_rows,
        key=lambda row: (
            TIER_ORDER[str(row["priority_tier"])],
            -int(row["same_register_nontr_head_count"]),
            -int(row["same_register_nontr_event_count"]),
            -(row["opposite_tr_observed"] == "YES"),
            -int(row["same_action_other_register_count"]),
            -int(row["same_action_cross_register_event_count"]),
            str(row["action_recipe"]),
            str(row["register"]),
        ),
    )
    tier_counter: Counter[str] = Counter()
    for global_rank, row in enumerate(ranked_rows, 1):
        tier_counter[str(row["priority_tier"])] += 1
        row["global_priority_rank"] = global_rank
        row["tier_rank"] = tier_counter[str(row["priority_tier"])]

    tier_a_rows = [row for row in ranked_rows if row["priority_tier"] == "A_MULTIHEAD_SAME_REGISTER"]
    tier_b_rows = [row for row in ranked_rows if row["priority_tier"] == "B_SINGLE_NONTR_HEAD"]
    tier_c_rows = [row for row in ranked_rows if row["priority_tier"] == "C_OPPOSITE_TR_ONLY"]
    tier_d_rows = [row for row in ranked_rows if row["priority_tier"] == "D_CROSS_REGISTER_ONLY"]
    frame_rows: list[dict[str, object]] = []
    for frame in dict.fromkeys(row["frozen_frame"] for row in composed):
        local = [row for row in ranked_rows if row["frozen_frame"] == frame]
        frame_rows.append({
            "frame_id": f"G494-F{len(frame_rows) + 1:02d}",
            "frozen_frame": frame,
            "composed_cell_count": len(local),
            "tier_a_count": sum(row["priority_tier"] == "A_MULTIHEAD_SAME_REGISTER" for row in local),
            "tier_b_count": sum(row["priority_tier"] == "B_SINGLE_NONTR_HEAD" for row in local),
            "tier_c_count": sum(row["priority_tier"] == "C_OPPOSITE_TR_ONLY" for row in local),
            "tier_d_count": sum(row["priority_tier"] == "D_CROSS_REGISTER_ONLY" for row in local),
            "same_register_supported_count": sum(row["same_register_family_supported"] == "YES" for row in local),
            "cross_register_anchored_count": sum(row["cross_register_same_action_anchored"] == "YES" for row in local),
        })
    register_rows: list[dict[str, object]] = []
    for register in REGISTER_ORDER:
        local = [row for row in ranked_rows if row["register"] == register]
        register_rows.append({
            "register_id": f"G494-R{len(register_rows) + 1:02d}",
            "register": register,
            "composed_cell_count": len(local),
            "tier_a_count": sum(row["priority_tier"] == "A_MULTIHEAD_SAME_REGISTER" for row in local),
            "tier_b_count": sum(row["priority_tier"] == "B_SINGLE_NONTR_HEAD" for row in local),
            "tier_c_count": sum(row["priority_tier"] == "C_OPPOSITE_TR_ONLY" for row in local),
            "tier_d_count": sum(row["priority_tier"] == "D_CROSS_REGISTER_ONLY" for row in local),
            "same_register_supported_count": sum(row["same_register_family_supported"] == "YES" for row in local),
            "cross_register_anchored_count": sum(row["cross_register_same_action_anchored"] == "YES" for row in local),
        })

    counts = tuple(map(len, (ranked_rows, tier_a_rows, tier_b_rows, tier_c_rows, tier_d_rows, nontr_rows, pair_rows, cross_rows, frame_rows, register_rows)))
    if counts != (73, 27, 19, 5, 22, 105, 21, 98, 11, 5):
        raise RuntimeError(f"Unexpected ranking counts: {counts}")
    write_tsv(RANKED, ranked_rows)
    write_tsv(TIER_A, tier_a_rows)
    write_tsv(TIER_B, tier_b_rows)
    write_tsv(TIER_C, tier_c_rows)
    write_tsv(TIER_D, tier_d_rows)
    write_tsv(NONTR_SUPPORT, nontr_rows)
    write_tsv(PAIR_SUPPORT, pair_rows)
    write_tsv(CROSS_REGISTER, cross_rows)
    write_tsv(FRAME_COVERAGE, frame_rows)
    write_tsv(REGISTER_COVERAGE, register_rows)

    result = {
        "status": STATUS,
        "ranked_composed_cell_count": len(ranked_rows),
        "tier_a_count": len(tier_a_rows),
        "tier_b_count": len(tier_b_rows),
        "tier_c_count": len(tier_c_rows),
        "tier_d_count": len(tier_d_rows),
        "nontr_supported_target_count": sum(int(row["same_register_nontr_head_count"]) > 0 for row in ranked_rows),
        "same_register_supported_target_count": sum(row["same_register_family_supported"] == "YES" for row in ranked_rows),
        "cross_register_anchored_target_count": sum(row["cross_register_same_action_anchored"] == "YES" for row in ranked_rows),
        "same_register_nontr_support_cell_count": len(nontr_rows),
        "same_register_nontr_support_event_count": sum(int(row["event_count"]) for row in nontr_rows),
        "same_register_opposite_tr_cell_count": len(pair_rows),
        "same_register_opposite_tr_event_count": sum(int(row["event_count"]) for row in pair_rows),
        "same_action_cross_register_cell_count": len(cross_rows),
        "same_action_cross_register_event_count": sum(int(row["event_count"]) for row in cross_rows),
        "state_warning_card_count": sum(row["state_warning"] != "NONE" for row in ranked_rows),
        "all_composed_labels_retained": all(row["composed_working_label_retained"] == "YES" for row in ranked_rows),
        "all_slot_values_old": all(row["all_slot_values_old"] == "YES" for row in ranked_rows),
        "surface_prediction_count": sum(row["surface_prediction_made"] != "NO" for row in ranked_rows),
        "occurrence_prediction_count": sum(row["occurrence_prediction_made"] != "NO" for row in ranked_rows),
        "meaning_change_count": 0,
        "wording_change_count": 0,
        "evidence_status_upgrade_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Transparent support ranking of 73 fixed GDT493 COMPOSED_WORKING cells by exact same-register alternate heads and cross-register same-action carriers; every composed label and state warning is retained, with no occurrence or surface prediction, evidence upgrade, meaning, recipe, event, or page change.",
    }
    READABLE.write_text(build_readable(ranked_rows, frame_rows, register_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
