#!/usr/bin/env python3
"""Build direct semantic contrast cards for ten non-action working roots."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
FOCUS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_5051_focus_edge_portability.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"

ACTIONS = ("CH", "S", "K", "OK", "P", "SH", "CHD", "T", "R")
ARGUMENTS = ("Y", "AIIN", "AIN", "OR")
RELATIONS = ("AL", "AR", "L", "AIR")
ORDERS = ("OL", "OT")
ROOTS = ARGUMENTS + RELATIONS + ORDERS
CONTRASTS = (
    tuple(("ARGUMENT", left, right) for left, right in combinations(ARGUMENTS, 2))
    + tuple(("RELATION", left, right) for left, right in combinations(RELATIONS, 2))
    + (("ORDER", "OL", "OT"),)
)
ROOT_CONTRACT = {
    "Y": ("der aktive, weiterverwendbare Arbeitsposten", "WERT", "POSTEN"),
    "AIIN": ("ein vorgeschriebener oder eingetragener Wert", "MASS", "WERT"),
    "AIN": ("ein abgegrenzter Anteil innerhalb des Besitzers", "PORTION", "ANTEIL"),
    "OR": ("eine begrenzte Arbeits- oder Eintragseinheit", "ZUBEREITUNG", "EINHEIT"),
    "AL": ("die Adresse, an der der folgende Gang ankommt oder gilt", "STELLE", "ZIELORT"),
    "AR": ("die Adresse, von der der aktuelle Gang ausgeht", "QUELLE", "AUSGANG"),
    "L": ("eine Verbindung, die einen folgenden Gang oder Posten trägt", "MIT", "VERBINDUNG"),
    "AIR": ("die Bahn, auf der ein Posten oder Gang geführt wird", "WASSER", "BAHN"),
    "OL": ("den bereits aktiven Gang oder Bezug fortsetzen", "VORIGES", "FORTSETZEN"),
    "OT": ("einen nächsten gleichrangigen Gang danach eröffnen", "NÄCHSTES", "DANACH"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator} ({100 * numerator / denominator:.1f}%)"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    focus_rows = read_tsv(FOCUS)
    dictionary = read_tsv(DICTIONARY)
    meanings = {row["atom"]: row["working_value_de"] for row in dictionary}

    profiles: dict[str, dict[str, object]] = {
        root: {
            "mention_count": 0,
            "events": set(),
            "pages": set(),
            "registers": Counter(),
            "position": Counter(),
            "previous": Counter(),
            "next": Counter(),
            "attached_actions": Counter(),
            "selectors": Counter(),
            "with_close": 0,
            "statement_first": 0,
        }
        for root in ROOTS
    }
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        recipe = row["component_recipe"]
        by_recipe[recipe].append(row)
        atoms = recipe.split("+")
        for index, atom in enumerate(atoms):
            if atom not in profiles:
                continue
            profile = profiles[atom]
            profile["mention_count"] += 1
            profile["events"].add(row["global_running_event_id"])
            profile["pages"].add(row["physical_page"])
            profile["registers"][row["register"]] += 1
            if len(atoms) == 1:
                position = "ONLY"
            elif index == 0:
                position = "FIRST"
            elif index == len(atoms) - 1:
                position = "LAST"
            else:
                position = "MEDIAL"
            profile["position"][position] += 1
            profile["previous"][atoms[index - 1] if index else "START"] += 1
            profile["next"][atoms[index + 1] if index + 1 < len(atoms) else "END"] += 1
            profile["with_close"] += "DY" in atoms
            profile["statement_first"] += index == 0 and row["card_ordinal_in_statement"] == "1"

    for row in focus_rows:
        focus = row["focus_core"]
        if focus not in profiles:
            continue
        profiles[focus]["attached_actions"][row["action_core"]] += 1
        profiles[focus]["selectors"][row["selector_rule"]] += 1

    substitution_index: dict[tuple[str, ...], dict[str, dict[str, object]]] = defaultdict(
        lambda: defaultdict(lambda: {"events": 0, "pages": set(), "registers": set(), "surfaces": set()})
    )
    for recipe, rows in by_recipe.items():
        atoms = recipe.split("+")
        for index, atom in enumerate(atoms):
            if atom not in ROOTS:
                continue
            frame = tuple(atoms[:index] + ["@CORE"] + atoms[index + 1:])
            cell = substitution_index[frame][atom]
            cell["events"] += len(rows)
            cell["pages"].update(row["physical_page"] for row in rows)
            cell["registers"].update(row["register"] for row in rows)
            cell["surfaces"].update(row["surface"] for row in rows)

    substitution_rows: list[dict[str, object]] = []
    pair_frame_counts: Counter[tuple[str, str]] = Counter()
    pair_frame_events: Counter[tuple[str, str]] = Counter()
    for family, left, right in CONTRASTS:
        for frame, members in sorted(substitution_index.items()):
            if left not in members or right not in members:
                continue
            left_cell, right_cell = members[left], members[right]
            pair_frame_counts[(left, right)] += 1
            pair_frame_events[(left, right)] += int(left_cell["events"]) + int(right_cell["events"])
            substitution_rows.append({
                "family": family,
                "contrast_pair": f"{left}~{right}",
                "frozen_frame": "+".join(frame),
                "left_root": left,
                "left_meaning_de": meanings[left],
                "left_event_count": left_cell["events"],
                "left_pages": "|".join(sorted(left_cell["pages"])),
                "left_registers": "|".join(sorted(left_cell["registers"])),
                "left_surfaces": "|".join(sorted(left_cell["surfaces"])),
                "right_root": right,
                "right_meaning_de": meanings[right],
                "right_event_count": right_cell["events"],
                "right_pages": "|".join(sorted(right_cell["pages"])),
                "right_registers": "|".join(sorted(right_cell["registers"])),
                "right_surfaces": "|".join(sorted(right_cell["surfaces"])),
                "reading_rule_de": f"Gleicher Rahmen; {left} liest {meanings[left]}, {right} liest {meanings[right]}",
            })

    profile_rows: list[dict[str, object]] = []
    for root in ROOTS:
        profile = profiles[root]
        mentions = int(profile["mention_count"])
        definition, rival, selected = ROOT_CONTRACT[root]
        attached = profile["attached_actions"]
        profile_rows.append({
            "core_root": root,
            "family": "ARGUMENT" if root in ARGUMENTS else "RELATION" if root in RELATIONS else "ORDER",
            "working_meaning_de": meanings[root],
            "operational_definition_de": definition,
            "mention_count": mentions,
            "event_count": len(profile["events"]),
            "page_count": len(profile["pages"]),
            "register_count": len(profile["registers"]),
            "only_count": profile["position"]["ONLY"],
            "first_count": profile["position"]["FIRST"],
            "medial_count": profile["position"]["MEDIAL"],
            "last_count": profile["position"]["LAST"],
            "chain_end_count": profile["next"]["END"],
            "statement_first_count": profile["statement_first"],
            "next_action_count": sum(profile["next"][action] for action in ACTIONS),
            "next_argument_count": sum(profile["next"][argument] for argument in ARGUMENTS),
            "with_close_count": profile["with_close"],
            "attached_action_count": sum(attached.values()),
            "attached_action_breakdown": "|".join(f"{action}:{attached[action]}" for action in sorted(attached)) if attached else "NONE",
            "selector_breakdown": "|".join(f"{selector}:{profile['selectors'][selector]}" for selector in sorted(profile["selectors"])) if profile["selectors"] else "NONE",
            "register_breakdown": "|".join(f"{register}:{profile['registers'][register]}" for register in sorted(profile["registers"])),
            "strongest_rival_de": rival,
            "decision": f"KEEP_{selected}",
        })

    def p(root: str) -> dict[str, object]:
        return profiles[root]

    def next_actions(root: str) -> int:
        return sum(p(root)["next"][action] for action in ACTIONS)

    def next_arguments(root: str) -> int:
        return sum(p(root)["next"][argument] for argument in ARGUMENTS)

    evidence: dict[tuple[str, str], str] = {
        ("Y", "AIIN"): f"Y führt zu einer weiteren Handlung {next_actions('Y')}×; AIIN {next_actions('AIIN')}×. AIIN endet {pct(p('AIIN')['next']['END'], int(p('AIIN')['mention_count']))}.",
        ("Y", "AIN"): f"Y führt zu einer weiteren Handlung {next_actions('Y')}×; AIN {next_actions('AIN')}×. AIN endet {pct(p('AIN')['next']['END'], int(p('AIN')['mention_count']))}.",
        ("Y", "OR"): f"Y wird an {sum(p('Y')['attached_actions'].values())} Handlungsköpfe gebunden; OR an {sum(p('OR')['attached_actions'].values())}. OR kann ein weiteres Argument tragen ({next_arguments('OR')}×).",
        ("AIIN", "AIN"): f"AIIN: CELESTIAL {p('AIIN')['registers']['CELESTIAL']}/{p('AIIN')['mention_count']}; AIN {p('AIN')['registers']['CELESTIAL']}/{p('AIN')['mention_count']}. AIN: BIOLOGICAL {p('AIN')['registers']['BIOLOGICAL']}/{p('AIN')['mention_count']}; AIIN {p('AIIN')['registers']['BIOLOGICAL']}/{p('AIIN')['mention_count']}.",
        ("AIIN", "OR"): f"AIIN endet {pct(p('AIIN')['next']['END'], int(p('AIIN')['mention_count']))}; OR {pct(p('OR')['next']['END'], int(p('OR')['mention_count']))} und trägt {next_arguments('OR')} nachfolgende Argumente.",
        ("AIN", "OR"): f"AIN endet {pct(p('AIN')['next']['END'], int(p('AIN')['mention_count']))}; OR {pct(p('OR')['next']['END'], int(p('OR')['mention_count']))} und trägt {next_arguments('OR')} nachfolgende Argumente.",
        ("AL", "AR"): f"AL eröffnet/führt weiter {int(p('AL')['mention_count']) - p('AL')['next']['END']}× und steht {p('AL')['statement_first']}× am Aussagestart; AR {int(p('AR')['mention_count']) - p('AR')['next']['END']}× und 0×.",
        ("AL", "L"): f"L steht {p('L')['position']['FIRST']}× karteninitial und öffnet {next_actions('L')} weitere Handlungen; AL {p('AL')['position']['FIRST']}× und {next_actions('AL')} Handlungen.",
        ("AL", "AIR"): f"AIR endet {pct(p('AIR')['next']['END'], int(p('AIR')['mention_count']))}; AL {pct(p('AL')['next']['END'], int(p('AL')['mention_count']))}. Selektoren trennen BAHN von Adressrelation.",
        ("AR", "L"): f"L öffnet {next_actions('L')} weitere Handlungen; AR nur {next_actions('AR')}. AR endet {pct(p('AR')['next']['END'], int(p('AR')['mention_count']))}.",
        ("AR", "AIR"): f"AR nutzt ausschließlich AL_AR_ORDERED_FALLBACK ({sum(p('AR')['selectors'].values())}×); AIR ausschließlich L_AIR_RIGHT_FALLBACK ({sum(p('AIR')['selectors'].values())}×).",
        ("L", "AIR"): f"L steht {p('L')['position']['FIRST']}× karteninitial und öffnet {next_actions('L')} Handlungen; AIR endet {pct(p('AIR')['next']['END'], int(p('AIR')['mention_count']))}.",
        ("OL", "OT"): f"OT steht {pct(p('OT')['position']['FIRST'], int(p('OT')['mention_count']))} karteninitial; OL nur {pct(p('OL')['position']['FIRST'], int(p('OL')['mention_count']))}. OL endet {p('OL')['next']['END']}×, OT {p('OT')['next']['END']}×.",
    }
    interpretation: dict[tuple[str, str], str] = {
        ("Y", "AIIN"): "POSTEN bleibt als aktives Objekt handlungsfähig; WERT füllt eine Einstellung aus.",
        ("Y", "AIN"): "POSTEN wird weiterbearbeitet; ANTEIL begrenzt den gemeinten Teil.",
        ("Y", "OR"): "POSTEN ist der laufende Referent; EINHEIT ist der Rahmen, der weiteren Inhalt tragen kann.",
        ("AIIN", "AIN"): "WERT ist die portablere Einstellgröße; ANTEIL ist stärker besitzer- und Teilstruktur-gebunden.",
        ("AIIN", "OR"): "WERT füllt eine Einheit aus; EINHEIT kann selbst weiteren Inhalt aufnehmen.",
        ("AIN", "OR"): "ANTEIL teilt den Besitzer; EINHEIT bündelt einen selbständigen Arbeits- oder Eintragsblock.",
        ("AL", "AR"): "ZIELORT kann den folgenden Zielgang eröffnen; AUSGANG schließt meist die Herkunftsangabe.",
        ("AL", "L"): "ZIELORT adressiert das Ankommen; VERBINDUNG hält einen folgenden Gang offen.",
        ("AL", "AIR"): "ZIELORT ist eine Adresse; BAHN ist der Wegwert, auf dem der Gang läuft.",
        ("AR", "L"): "AUSGANG nennt die Herkunft; VERBINDUNG trägt die Fortsetzung.",
        ("AR", "AIR"): "AUSGANG und BAHN sind verschiedene Relationstypen mit verschiedenen Binderegeln.",
        ("L", "AIR"): "VERBINDUNG eröffnet einen Anschluss; BAHN bezeichnet den Verlauf dieses Anschlusses.",
        ("OL", "OT"): "FORTSETZEN bleibt im aktiven Gang; DANACH eröffnet fast immer den nächsten Gang.",
    }
    contrast_rows: list[dict[str, object]] = []
    for family, left, right in CONTRASTS:
        contrast_rows.append({
            "family": family,
            "contrast_pair": f"{left}~{right}",
            "left_meaning_de": meanings[left],
            "right_meaning_de": meanings[right],
            "shared_exact_substitution_frame_count": pair_frame_counts[(left, right)],
            "shared_frame_event_count": pair_frame_events[(left, right)],
            "decisive_distributional_contrast": evidence[(left, right)],
            "workshop_interpretation_de": interpretation[(left, right)],
            "decision": "DISTINCT_MEANINGS_RETAINED",
        })

    write_tsv(OUT / "gdt429_10_nonaction_semantic_profiles.tsv", profile_rows, list(profile_rows[0]))
    write_tsv(OUT / "gdt429_13_nonaction_core_contrasts.tsv", contrast_rows, list(contrast_rows[0]))
    write_tsv(OUT / "gdt429_256_direct_substitution_frames.tsv", substitution_rows, list(substitution_rows[0]))

    deck = [
        "# Zehn Nicht-Handlungen: kurze Kontrastkarte", "",
        "Der Rahmen bleibt gleich; das ausgetauschte Kürzel ändert Argument, Relation oder Reihenfolge.", "",
    ]
    for row in profile_rows:
        deck.append(
            f"- **{row['core_root']} = {row['working_meaning_de']}** — {row['operational_definition_de']}. "
            f"Nicht automatisch {row['strongest_rival_de']}."
        )
    deck += ["", "## Drei Lehrsätze", "",
        "- POSTEN wird weitergereicht; WERT füllt eine Einstellung; ANTEIL begrenzt; EINHEIT bündelt.",
        "- ZIELORT nimmt auf; AUSGANG gibt her; VERBINDUNG schließt an; BAHN trägt den Verlauf.",
        "- FORTSETZEN bleibt im Gang; DANACH eröffnet den nächsten Gang.",
    ]
    (OUT / "NONACTION_MEANING_CONTRAST_DECK.md").write_text("\n".join(deck) + "\n", encoding="utf-8")

    result = {
        "status": "TEN_NONACTION_MEANINGS_RETAINED_WITH_DIRECT_CONTRAST_RULES",
        "running_event_count": len(clauses),
        "nonaction_root_count": len(profile_rows),
        "nonaction_mention_count": sum(int(row["mention_count"]) for row in profile_rows),
        "focus_edge_count": len(focus_rows),
        "contrast_pair_count": len(contrast_rows),
        "direct_substitution_frame_count": len(substitution_rows),
        "all_contrasts_have_shared_frames": all(int(row["shared_exact_substitution_frame_count"]) > 0 for row in contrast_rows),
        "meaning_revisions": 0,
        "new_roots": 0,
        "new_pages": 0,
    }
    (OUT / "gdt429_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
