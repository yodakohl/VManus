#!/usr/bin/env python3
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
HERE = ROOT / "experiments/yolo/gdt411_provisional_core_process_position"
OUT = HERE / "artifacts"
STATEMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_715_statement_edition.tsv"
ATTACHMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"
BASE_DICT = ROOT / "experiments/yolo/gdt410_provisional_core_rival_tournament/artifacts/gdt410_final_19_core_dictionary.tsv"
BASE_PROFILES = ROOT / "experiments/yolo/gdt410_provisional_core_rival_tournament/artifacts/gdt410_ten_core_complement_profiles.tsv"

ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
TARGETS = ("CH", "K", "S", "CHD", "AIR")
REGISTERS = ("HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA", "SOURCE_SECTION_T")

CANDIDATES = {
    "CH": [
        ("NEHMEN", 3, 3, 3, 3, "CH geht stark vor K und T; ein entnommener Posten kann danach gegeben oder eingestellt werden."),
        ("BEARBEITEN", 3, 3, 2, 2, "Breit möglich, erklärt aber die gerichtete CH→K/T-Folge schlechter."),
        ("AUSWÄHLEN", 2, 3, 2, 2, "Kollidiert mit dem eigenständigen S-Kern und passt nicht zu allen Gradkomplementen."),
    ],
    "K": [
        ("GEBEN", 3, 3, 3, 3, "K folgt CH 216-mal, aber CH folgt K nur 98-mal; der Übergang liest sich sparsam NEHMEN→GEBEN."),
        ("ZUORDNEN", 3, 3, 2, 3, "Im Himmelsregister stark, in stofflichen und körpernahen Folgen unnötig abstrakt."),
        ("ZUFÜHREN", 3, 2, 2, 2, "Technisch plausibel, doch Zielrichtung ist nicht in jeder K-Karte sichtbar."),
    ],
    "S": [
        ("WÄHLEN", 3, 3, 3, 3, "S nimmt Wert, Posten, Ausgang, Ziel und Anteil; WÄHLEN deckt diese Objektbreite knapp."),
        ("PRÜFEN", 3, 3, 3, 2, "Bei Werten plausibel, bei Anteil/Ziel als universeller Befehl schwerer."),
        ("TRENNEN", 2, 2, 3, 1, "Zu stofflich und in Himmels- sowie Quellabschnitten überdehnt."),
    ],
    "CHD": [
        ("UMSETZEN", 3, 3, 3, 2, "Y und L dominieren, doch starke Bio- und Spätpositionslast lässt die konkrete Technik offen."),
        ("WEITERFÜHREN", 3, 2, 2, 3, "Erklärt Transfer, überschneidet sich aber mit OL=FORTSETZEN und L=VERBINDUNG."),
        ("ABSCHLIESSEN", 2, 3, 3, 2, "111 von 301 Fällen sind allein/letzt, aber 46 sind zuerst und 62 führen zu OK."),
    ],
    "AIR": [
        ("BAHN", 3, 3, 3, 3, "Ein neutraler Kurs-/Leitungsraum passt zu neun Köpfen, fünf Registern und Ring wie Becken."),
        ("LAUF", 3, 3, 3, 2, "Weiterhin möglich, klingt bei statischen Himmels- und Adressfeldern zu prozessual."),
        ("WEG", 3, 3, 3, 2, "Weiterhin möglich, unterscheidet sich aber schlechter von L=VERBINDUNG."),
    ],
}

FINAL = {
    "CH": ("NEHMEN", "KEEP"),
    "K": ("GEBEN", "KEEP"),
    "S": ("WÄHLEN", "KEEP"),
    "CHD": ("UMSETZEN", "KEEP_PROVISIONAL"),
    "AIR": ("BAHN", "KEEP"),
}

PROCESS_NOTES = {
    "CH": "CH→K 216 gegen K→CH 98; CH→T 159 gegen T→CH 71",
    "K": "K folgt CH 216-mal, während CH nur 98-mal auf K folgt",
    "S": "S→SH 61 gegen SH→S 31; keine reine Endkontrolle",
    "CHD": "mittlere Phase 0.684; 83 letzte und 28 alleinige, aber auch 46 erste Vorkommen",
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atoms(recipe):
    return [atom for card in recipe.split(" | ") for atom in card.split("+")]


def render(recipe, meanings):
    return " | ".join(" · ".join(meanings.get(atom, atom) for atom in card.split("+")) for card in recipe.split(" | "))


def packed(counter, limit=None):
    items = counter.most_common(limit)
    return "|".join(f"{key}:{value}" for key, value in items) if items else "NONE"


def main() -> int:
    statements = read_tsv(STATEMENTS)
    attachments = read_tsv(ATTACHMENTS)
    atom_dictionary = read_tsv(ATOM_DICT)
    base_dictionary = read_tsv(BASE_DICT)
    base_profiles = {row["root"]: row for row in read_tsv(BASE_PROFILES)}

    action_occurrences = []
    transitions = Counter()
    phase_counts = defaultdict(Counter)
    phase_values = defaultdict(list)
    predecessor = defaultdict(Counter)
    successor = defaultdict(Counter)

    for row in statements:
        seq = [atom for atom in atoms(row["recipe_sequence"]) if atom in ACTIONS]
        for left, right in zip(seq, seq[1:]):
            transitions[(left, right)] += 1
        for index, root in enumerate(seq):
            position = "ONLY" if len(seq) == 1 else "FIRST" if index == 0 else "LAST" if index == len(seq) - 1 else "MIDDLE"
            phase_counts[root][position] += 1
            phase_values[root].append((index + 1) / len(seq))
            if index:
                predecessor[root][seq[index - 1]] += 1
            if index + 1 < len(seq):
                successor[root][seq[index + 1]] += 1
            action_occurrences.append((root, row["global_statement_id"], index, len(seq)))

    relation_heads = Counter()
    relation_head_by_register = defaultdict(Counter)
    for row in attachments:
        if row["focus_core"] == "AIR":
            relation_heads[row["action_core"]] += 1
            relation_head_by_register[row["register"]][row["action_core"]] += 1

    transition_rows = []
    for left in ACTIONS:
        for right in ACTIONS:
            count = transitions[(left, right)]
            reverse = transitions[(right, left)]
            transition_rows.append({
                "left_action": left,
                "right_action": right,
                "left_to_right_count": count,
                "right_to_left_count": reverse,
                "directional_delta": count - reverse,
                "contains_remaining_target": "YES" if left in TARGETS or right in TARGETS else "NO",
            })

    score_rows = []
    for root in TARGETS:
        for value, role, order_fit, breadth, restraint, note in CANDIDATES[root]:
            score_rows.append({
                "root": root,
                "candidate_value_de": value,
                "role_fit_0_3": role,
                "process_order_fit_0_3": order_fit,
                "cross_register_breadth_0_3": breadth,
                "avoids_local_overfit_0_3": restraint,
                "total_0_12": role + order_fit + breadth + restraint,
                "selected_value": "YES" if value == FINAL[root][0] else "NO",
                "final_status": FINAL[root][1] if value == FINAL[root][0] else "RIVAL",
                "reason_de": note,
            })

    profile_rows = []
    for root in TARGETS:
        source = base_profiles[root]
        selected_scores = [row for row in score_rows if row["root"] == root and row["selected_value"] == "YES"][0]
        rival_scores = sorted((int(row["total_0_12"]) for row in score_rows if row["root"] == root and row["selected_value"] == "NO"), reverse=True)
        if root != "AIR":
            total = sum(phase_counts[root].values())
            mean_phase = sum(phase_values[root]) / len(phase_values[root])
            strongest_pair = max(
                ((other, transitions[(root, other)] - transitions[(other, root)], transitions[(root, other)], transitions[(other, root)]) for other in ACTIONS if other != root),
                key=lambda item: abs(item[1]),
            )
            process_note = PROCESS_NOTES[root]
            action_phase = f"{mean_phase:.3f}"
            prev_text = packed(predecessor[root], 5)
            next_text = packed(successor[root], 5)
            air_heads = "NOT_APPLICABLE"
        else:
            total = "NOT_ACTION"
            process_note = f"Relationskern unter neun Handlungsköpfen; häufigste {packed(relation_heads, 5)}"
            action_phase = "NOT_ACTION"
            prev_text = "NOT_ACTION"
            next_text = "NOT_ACTION"
            air_heads = packed(relation_heads)
        profile_rows.append({
            "root": root,
            "selected_value_de": FINAL[root][0],
            "decision": FINAL[root][1],
            "mention_count": source["atom_mention_count"],
            "page_count": source["page_count"],
            "register_count": source["register_count"],
            "action_occurrence_count": total,
            "first_count": phase_counts[root]["FIRST"] if root != "AIR" else source["first_count"],
            "middle_count": phase_counts[root]["MIDDLE"] if root != "AIR" else source["middle_count"],
            "last_count": phase_counts[root]["LAST"] if root != "AIR" else source["last_count"],
            "only_count": phase_counts[root]["ONLY"] if root != "AIR" else "NOT_ACTION",
            "mean_action_phase_0_1": action_phase,
            "top_predecessors": prev_text,
            "top_successors": next_text,
            "air_governing_heads": air_heads,
            "selected_score_0_12": selected_scores["total_0_12"],
            "best_rival_score_0_12": rival_scores[0],
            "selection_margin": int(selected_scores["total_0_12"]) - rival_scores[0],
            "process_position_interpretation_de": process_note,
            "decision_reason_de": selected_scores["reason_de"],
        })

    final_dictionary = []
    for row in base_dictionary:
        updated = dict(row)
        root = row["root"]
        if root in FINAL:
            updated["selected_minimal_value_de"] = FINAL[root][0]
            updated["decision"] = FINAL[root][1]
            rivals = [item[0] for item in CANDIDATES[root] if item[0] != FINAL[root][0]]
            updated["rival_a_de"], updated["rival_b_de"] = rivals
            updated["decision_reason_de"] = next(item[5] for item in CANDIDATES[root] if item[0] == FINAL[root][0])
        final_dictionary.append(updated)

    meanings = {row["atom"]: row["locked_working_value_de"] for row in atom_dictionary}
    meanings.update({row["root"]: row["selected_minimal_value_de"] for row in final_dictionary})
    example_rows = []
    for root in TARGETS:
        for register in REGISTERS:
            candidates = [row for row in statements if row["register"] == register and root in atoms(row["recipe_sequence"])]
            chosen = min(candidates, key=lambda row: (int(row["event_count"]), int(row["global_statement_ordinal"])))
            sequence = [atom for atom in atoms(chosen["recipe_sequence"]) if atom in ACTIONS]
            if root == "AIR":
                phase = "RELATION_TO_" + packed(relation_head_by_register[register], 3)
            else:
                indices = [index for index, atom in enumerate(sequence) if atom == root]
                phase = "|".join(f"{index + 1}/{len(sequence)}" for index in indices)
            example_rows.append({
                "root": root,
                "register": register,
                "global_statement_id": chosen["global_statement_id"],
                "physical_page": chosen["physical_page"],
                "owner_de": chosen["owner_de"],
                "event_count": chosen["event_count"],
                "surface_sequence": chosen["surface_sequence"],
                "recipe_sequence": chosen["recipe_sequence"],
                "target_process_position": phase,
                "revised_literal_core_reading_de": render(chosen["recipe_sequence"], meanings),
                "reading_scope": "FULL_STATEMENT__LOCAL_NOUNS_STILL_OWNER_SUPPLIED",
            })

    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "transitions": OUT / "gdt411_81_action_transition_matrix.tsv",
        "scores": OUT / "gdt411_five_core_candidate_scorecard.tsv",
        "profiles": OUT / "gdt411_five_core_process_profiles.tsv",
        "examples": OUT / "gdt411_25_cross_register_statement_examples.tsv",
        "dictionary": OUT / "gdt411_final_19_core_dictionary.tsv",
    }
    write_tsv(paths["transitions"], transition_rows, list(transition_rows[0]))
    write_tsv(paths["scores"], score_rows, list(score_rows[0]))
    write_tsv(paths["profiles"], profile_rows, list(profile_rows[0]))
    write_tsv(paths["examples"], example_rows, list(example_rows[0]))
    write_tsv(paths["dictionary"], final_dictionary, list(final_dictionary[0]))

    result = {
        "status": "FOUR_MORE_CORES_STABILIZED__CHD_REMAINS_PROVISIONAL",
        "statement_count": len(statements),
        "attachment_count": len(attachments),
        "action_occurrence_count": len(action_occurrences),
        "transition_pair_count": sum(transitions.values()),
        "profile_count": len(profile_rows),
        "example_count": len(example_rows),
        "final_decision_counts": dict(sorted(Counter(row["decision"] for row in final_dictionary).items())),
        "newly_stabilized_roots": [root for root in TARGETS if FINAL[root][1] == "KEEP"],
        "remaining_provisional_roots": [root for root in TARGETS if FINAL[root][1] == "KEEP_PROVISIONAL"],
        "selected_values": {root: FINAL[root][0] for root in TARGETS},
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (STATEMENTS, ATTACHMENTS, ATOM_DICT, BASE_DICT, BASE_PROFILES)},
        "output_sha256": {name: sha256(path) for name, path in paths.items()},
    }
    (OUT / "gdt411_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
