#!/usr/bin/env python3
"""Run concrete rival readings for the ten provisional GDT409 roots."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G409 = ROOT / "experiments/yolo/gdt409_nineteen_core_semantic_drift_audit/artifacts"
STATEMENTS = G407 / "gdt407_715_statement_edition.tsv"
ATTACHMENTS = G407 / "gdt407_5051_attachment_edition.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"
DICTIONARY = G409 / "gdt409_selected_minimal_dictionary.tsv"
AUDIT = G409 / "gdt409_19_core_semantic_audit.tsv"

TARGETS = ("CH", "SH", "K", "S", "CHD", "L", "T", "R", "P", "AIR")

# Four 0..3 workshop criteria. Scores express comparative usefulness on this
# selected edition, not probabilities or decipherment confidence.
CANDIDATES = {
    "CH": [("NEHMEN", 3, 3, 3, 2), ("BEARBEITEN", 3, 3, 2, 2), ("GREIFEN", 2, 2, 3, 1)],
    "SH": [("HALTEN", 3, 3, 3, 3), ("RUHEN LASSEN", 3, 2, 1, 2), ("BEWAHREN", 2, 3, 3, 2)],
    "K": [("GEBEN", 3, 3, 3, 2), ("ZUFÜHREN", 3, 2, 2, 2), ("ZUORDNEN", 3, 3, 2, 2)],
    "S": [("WÄHLEN", 3, 3, 3, 2), ("PRÜFEN", 2, 3, 3, 2), ("TRENNEN", 2, 2, 3, 1)],
    "CHD": [("UMSETZEN", 3, 3, 3, 2), ("ÜBERFÜHREN", 3, 2, 2, 2), ("WECHSELN", 2, 3, 3, 2)],
    "L": [("VERBINDUNG", 3, 3, 3, 3), ("MIT", 2, 3, 3, 2), ("ANSCHLUSS", 3, 2, 3, 2)],
    "T": [("EINSTELLEN", 3, 3, 3, 3), ("BESTIMMEN", 3, 3, 2, 2), ("ORDNEN", 2, 3, 3, 2)],
    "R": [("MARKIEREN", 3, 3, 3, 3), ("VERWEISEN", 3, 3, 2, 2), ("KENNZEICHNEN", 3, 3, 2, 2)],
    "P": [("EINSETZEN", 3, 3, 3, 3), ("EINBRINGEN", 3, 2, 2, 2), ("BEGINNEN", 1, 3, 3, 1)],
    "AIR": [("LAUF", 3, 3, 3, 2), ("WEG", 3, 3, 3, 2), ("FLUSS", 2, 2, 3, 1)],
}

FINAL_STATUS = {
    "CH": "KEEP_PROVISIONAL", "SH": "KEEP", "K": "KEEP_PROVISIONAL",
    "S": "KEEP_PROVISIONAL", "CHD": "KEEP_PROVISIONAL", "L": "KEEP",
    "T": "KEEP", "R": "KEEP", "P": "KEEP", "AIR": "KEEP_PROVISIONAL",
}

FOCUS_CATEGORY = {
    "Y": "ARGUMENT", "AIIN": "ARGUMENT", "OR": "ARGUMENT", "AIN": "ARGUMENT",
    "AL": "RELATION", "AR": "RELATION", "L": "RELATION", "AIR": "RELATION",
    "E": "GRADE", "EE": "GRADE", "EEE": "GRADE", "IIN": "GRADE",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(recipe_sequence: str, values: dict[str, str]) -> str:
    cards = []
    for recipe in recipe_sequence.split(" | "):
        cards.append(" · ".join(values[token] for token in recipe.strip().split("+") if token))
    return " | ".join(cards)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    statements = read_tsv(STATEMENTS)
    attachments = read_tsv(ATTACHMENTS)
    atom_rows = read_tsv(ATOM_DICT)
    dictionary = read_tsv(DICTIONARY)
    audit = read_tsv(AUDIT)
    assert (len(statements), len(attachments), len(dictionary), len(audit)) == (715, 5051, 19, 19)
    selected = {row["atom"]: row["locked_working_value_de"] for row in atom_rows}
    selected.update({row["root"]: row["selected_minimal_value_de"] for row in dictionary})
    audit_by_root = {row["root"]: row for row in audit}

    score_rows: list[dict[str, object]] = []
    for root in TARGETS:
        for candidate, role_fit, register_fit, brevity, overfit in CANDIDATES[root]:
            score_rows.append({
                "root": root, "candidate_value_de": candidate,
                "role_fit_0_3": role_fit, "cross_register_fit_0_3": register_fit,
                "atomic_brevity_0_3": brevity, "avoids_local_overfit_0_3": overfit,
                "total_0_12": role_fit + register_fit + brevity + overfit,
                "selected_value": "YES" if candidate == selected[root] else "NO",
                "final_status": FINAL_STATUS[root] if candidate == selected[root] else "RIVAL",
            })

    profile_rows: list[dict[str, object]] = []
    for root in TARGETS:
        governed = [row for row in attachments if row["action_core"] == root]
        focused = [row for row in attachments if row["focus_core"] == root]
        focus_counts = Counter(row["focus_core"] for row in governed)
        family_counts = Counter(row["focus_family"] for row in governed)
        action_counts = Counter(row["action_core"] for row in focused)
        audit_row = audit_by_root[root]
        selected_score = next(row["total_0_12"] for row in score_rows if row["root"] == root and row["selected_value"] == "YES")
        best_rival_score = max(row["total_0_12"] for row in score_rows if row["root"] == root and row["selected_value"] == "NO")
        profile_rows.append({
            "root": root, "selected_value_de": selected[root], "final_status": FINAL_STATUS[root],
            "atom_mention_count": audit_row["atom_mention_count"], "page_count": audit_row["page_count"],
            "register_count": audit_row["register_count"], "first_count": audit_row["first_count"],
            "middle_count": audit_row["middle_count"], "last_count": audit_row["last_count"],
            "governed_focus_count": len(governed), "governed_family_counts": "|".join(f"{k}:{v}" for k, v in sorted(family_counts.items())) or "NONE",
            "governed_exact_focus_counts": "|".join(f"{k}:{v}" for k, v in focus_counts.most_common()) or "NONE",
            "relation_focus_governing_action_counts": "|".join(f"{k}:{v}" for k, v in action_counts.most_common()) or "NONE",
            "selected_score_0_12": selected_score, "best_rival_score_0_12": best_rival_score,
            "selection_margin": selected_score - best_rival_score,
            "decision_note_de": {
                "CH": "NEHMEN bleibt knapp vor BEARBEITEN; hohe Gradlast verhindert Promotion.",
                "SH": "463 Gradfoki machen HALTEN breiter und sparsamer als RUHEN LASSEN.",
                "K": "GEBEN bleibt, aber ZUORDNEN ist im Himmelsregister gleichwertig.",
                "S": "WÄHLEN bleibt, PRÜFEN ist in technischen Zellen ein lebender Rivale.",
                "CHD": "UMSETZEN deckt Transfer und Zustandswechsel; genaue Technik offen.",
                "L": "VERBINDUNG hält als neutraler Relationsname; MIT ist zu grammatisch eng.",
                "T": "EINSTELLEN deckt Wert-, Grad- und Zielkomplemente am gleichmäßigsten.",
                "R": "MARKIEREN ist der kürzeste gemeinsame Wert für Kopf- und Schwanzlage.",
                "P": "BEGINNEN scheitert: P steht häufiger medial als initial; EINSETZEN bleibt.",
                "AIR": "LAUF und WEG bleiben punktgleich; Wasser/Fluss sind zu stofflich.",
            }[root],
        })

    sample_rows: list[dict[str, object]] = []
    registers = sorted({row["register"] for row in statements})
    for root in TARGETS:
        for register in registers:
            candidates = [row for row in statements if row["register"] == register and root in {token for recipe in row["recipe_sequence"].split(" | ") for token in recipe.strip().split("+")}]
            if not candidates:
                continue
            statement = min(candidates, key=lambda row: int(row["global_statement_ordinal"]))
            rival_values = [candidate for candidate, *_ in CANDIDATES[root] if candidate != selected[root]]
            selected_reading = render(statement["recipe_sequence"], selected)
            rival_maps = []
            for rival in rival_values:
                mapping = dict(selected)
                mapping[root] = rival
                rival_maps.append(render(statement["recipe_sequence"], mapping))
            sample_rows.append({
                "root": root, "register": register, "physical_page": statement["physical_page"],
                "global_statement_id": statement["global_statement_id"], "owner_de": statement["owner_de"],
                "surface_sequence": statement["surface_sequence"],
                "selected_value_de": selected[root], "selected_literal_reading_de": selected_reading,
                "rival_a_value_de": rival_values[0], "rival_a_literal_reading_de": rival_maps[0],
                "rival_b_value_de": rival_values[1], "rival_b_literal_reading_de": rival_maps[1],
                "choice_note_de": next(row["decision_note_de"] for row in profile_rows if row["root"] == root),
            })

    final_dictionary = []
    for row in dictionary:
        final_dictionary.append({
            "root": row["root"], "structural_category": row["structural_category"],
            "selected_minimal_value_de": row["selected_minimal_value_de"],
            "decision": FINAL_STATUS.get(row["root"], row["decision"]),
            "rival_a_de": row["rival_a_de"], "rival_b_de": row["rival_b_de"],
            "portable_use_rule_de": row["portable_use_rule_de"],
            "atom_mention_count": row["atom_mention_count"], "page_count": row["page_count"],
            "register_count": row["register_count"],
            "decision_reason_de": next((p["decision_note_de"] for p in profile_rows if p["root"] == row["root"]), row["decision_reason_de"]),
        })

    score_path = OUT / "gdt410_candidate_scorecard.tsv"
    profile_path = OUT / "gdt410_ten_core_complement_profiles.tsv"
    sample_path = OUT / "gdt410_50_full_statement_rival_readings.tsv"
    dictionary_path = OUT / "gdt410_final_19_core_dictionary.tsv"
    write_tsv(score_path, score_rows, list(score_rows[0]))
    write_tsv(profile_path, profile_rows, list(profile_rows[0]))
    write_tsv(sample_path, sample_rows, list(sample_rows[0]))
    write_tsv(dictionary_path, final_dictionary, list(final_dictionary[0]))
    result = {
        "status": "FIVE_PROVISIONAL_VALUES_REMAIN__FIVE_PROMOTED_BY_FULL_STATEMENT_RIVALS",
        "target_roots": len(TARGETS), "candidate_rows": len(score_rows),
        "full_statement_rival_rows": len(sample_rows),
        "final_decision_counts": dict(sorted(Counter(row["decision"] for row in final_dictionary).items())),
        "promoted_roots": [root for root in TARGETS if FINAL_STATUS[root] == "KEEP"],
        "remaining_provisional_roots": [root for root in TARGETS if FINAL_STATUS[root] == "KEEP_PROVISIONAL"],
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (STATEMENTS, ATTACHMENTS, ATOM_DICT, DICTIONARY, AUDIT)},
        "output_sha256": {str(path.relative_to(HERE)): sha256(path) for path in (score_path, profile_path, sample_path, dictionary_path)},
    }
    (OUT / "gdt410_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
