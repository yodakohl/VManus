#!/usr/bin/env python3
"""Render the same twelve workshop programs with four simple scribal habits."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"


PROFILES = [
    ("R-A", "VORLAGENHAND", "use master head form", "Take the workshop master form unless a page exemplar says otherwise."),
    ("R-B", "Q-EINTRITTSHAND", "prefer q-initial allograph", "At eligible entries choose the registered q-form; otherwise copy the master form."),
    ("R-C", "S-FLUSSHAND", "prefer sh/s-initial allograph", "At eligible continuations choose the registered sh/s-form; otherwise copy the master form."),
    ("R-D", "KURZHAND", "prefer shortest registered allograph", "Choose the shortest registered form; ties follow the workshop family order."),
]


PROGRAMS = [
    ("U01", "Setze den Posten auf Sollmaß und halte ihn länger offen.", ["MC120", "MC002"]),
    ("U02", "Gib eine Portion zu, setze sie am Ziel an, übertrage und schließe.", ["MC017", "MC040", "MC025"]),
    ("U03", "Nimm den nächsten Ansatz und halte ihn kurz bereit.", ["MC013", "MC073"]),
    ("U04", "Setze diesen Posten an und führe ihn durch den Durchlass.", ["MC026", "MC035"]),
    ("U05", "Nimm ihn aus der Quelle und setze ihn um.", ["MC055", "MC074"]),
    ("U06", "Stelle das Folgemaß ein und führe danach zum Ziel.", ["MC060", "MC093"]),
    ("U07", "Lass kurz absetzen und lies danach das Ergebnis.", ["MC128", "MC119"]),
    ("U08", "Führe den vorigen Ansatz weiter und übertrage weiter.", ["MC157", "MC028"]),
    ("U09", "Setze den laufenden Posten an und halte ihn länger.", ["MC103", "MC002"]),
    ("U10", "Nimm eine Zutat und gib sie nach Sollmaß zu.", ["MC034", "MC087"]),
    ("U11", "Sammle länger, schließe den Schritt und fahre fort.", ["MC045", "MC153"]),
    ("U12", "Übertrage den Folgeposten, bereite den Ansatz und halte ihn bereit.", ["MC057", "MC080", "MC161"]),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def choose(profile: str, card: dict[str, str]) -> str:
    variants = card["registered_surface_family"].split("|")
    master = card["master_head_form"]
    if profile == "R-A":
        return master
    if profile == "R-B":
        q = [form for form in variants if form.startswith("q")]
        return q[0] if q else master
    if profile == "R-C":
        sh = [form for form in variants if form.startswith("sh")]
        s = [form for form in variants if form.startswith("s")]
        return (sh or s or [master])[0]
    if profile == "R-D":
        return min(enumerate(variants), key=lambda item: (len(item[1]), item[0]))[1]
    raise ValueError(profile)


def main() -> None:
    cards = read_tsv(CARDS)
    by_id = {row["master_card_id"]: row for row in cards}
    by_surface: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        for surface in card["registered_surface_family"].split("|"):
            by_surface[surface].add(card["master_card_id"])

    profile_rows = [
        {"renderer_id": rid, "workshop_name": name, "choice_rule": rule, "five_line_training_note": note}
        for rid, name, rule, note in PROFILES
    ]
    program_rows: list[dict[str, object]] = []
    realizations: list[dict[str, object]] = []
    for program_id, source, ids in PROGRAMS:
        selected = [by_id[card_id] for card_id in ids]
        program_rows.append({
            "program_id": program_id,
            "source_instruction_de": source,
            "master_card_ids": " ".join(ids),
            "semantic_atom_sequence": " | ".join(row["corrected_semantic_atoms"] for row in selected),
            "master_surface_sequence": " ".join(row["master_head_form"] for row in selected),
            "card_count": len(ids),
        })
        for renderer_id, name, _, _ in PROFILES:
            surfaces = [choose(renderer_id, row) for row in selected]
            ambiguous = [surface for surface in surfaces if len(by_surface[surface]) > 1]
            candidate_sizes = [len(by_surface[surface]) for surface in surfaces]
            realizations.append({
                "program_id": program_id,
                "renderer_id": renderer_id,
                "workshop_name": name,
                "source_instruction_de": source,
                "card_identity_sequence": " ".join(ids),
                "visible_surface_sequence": " ".join(surfaces),
                "changed_from_master_cards": sum(surface != row["master_head_form"] for surface, row in zip(surfaces, selected)),
                "surface_ambiguous_cards": len(ambiguous),
                "ambiguous_surfaces": "|".join(ambiguous) if ambiguous else "NONE",
                "surface_candidate_set_sizes": ",".join(str(size) for size in candidate_sizes),
                "semantic_program_preserved": "YES",
                "decode_rule": "REGISTERED_CARD_PLUS_LOCAL_CONSTRUCTION" if ambiguous else "VISIBLE_FAMILY_SUFFICIENT",
            })

    write_tsv(OUT / "NINETY_EIGHTH_FOUR_RENDERER_PROFILES.tsv", list(profile_rows[0]), profile_rows)
    write_tsv(OUT / "NINETY_EIGHTH_12_SOURCE_PROGRAMS.tsv", list(program_rows[0]), program_rows)
    write_tsv(OUT / "NINETY_EIGHTH_48_SCRIBAL_REALIZATIONS.tsv", list(realizations[0]), realizations)

    changed = Counter()
    ambiguous = Counter()
    distinct_outputs = Counter()
    for renderer_id, *_ in PROFILES:
        subset = [row for row in realizations if row["renderer_id"] == renderer_id]
        changed[renderer_id] = sum(int(row["changed_from_master_cards"]) for row in subset)
        ambiguous[renderer_id] = sum(int(row["surface_ambiguous_cards"]) for row in subset)
        distinct_outputs[renderer_id] = len({row["visible_surface_sequence"] for row in subset})

    report = [
        "# Achtundneunzigste Runde: Vier Schreiber, dieselben Anweisungen", "",
        "## Ergebnis", "",
        "Vier leicht lehrbare Renderer erhalten dieselben zwölf Quellanweisungen und",
        "dieselben registrierten Kartenfolgen. Die Vorlagenhand kopiert den Kopf, die",
        "Q-Hand bevorzugt vorhandene q-Eintrittsformen, die S-Hand vorhandene sh/s-Formen",
        "und die Kurzhand die kürzeste bereits registrierte Variante. Keine Hand darf eine",
        "neue Form erfinden oder den Kartenwert ändern.", "",
    ]
    for rid, name, _, _ in PROFILES:
        report.append(f"- **{name}**: {changed[rid]} Karten gegenüber der Vorlage verändert; {ambiguous[rid]} sichtbare Karten brauchen zusätzlich lokalen Konstruktionskontext.")
    report.extend([
        "", "Alle 48 Realisierungen behalten dieselbe Kartenidentitäts- und Bedeutungsfolge.",
        "Damit ist eine kleine Mehrschreiberwerkstatt praktisch denkbar: Der Lehrling lernt",
        "nicht vier Sprachen, sondern eine Karte mit einer kurzen Liste zugelassener",
        "Eintrittsformen. Schwieriger sind nur echte Oberflächenkollisionen wie `shedy`,",
        "wo der sichtbare String allein nicht zwischen zwei registrierten Karten genügt.", "",
        "Die Simulation behauptet nicht, dass diese vier Profile den historischen Händen",
        "entsprechen. Sie zeigt einen ausführbaren einfachen Mechanismus, durch den mehrere",
        "Schreiber bei gleicher Werkstattbedeutung sichtbar verschiedene Formen erzeugen.", "",
        "Nur Karten und Varianten der festen Prosaseiten wurden benutzt; f84 und f84r",
        "blieben versiegelt.",
    ])
    (OUT / "NINETY_EIGHTH_RENDERER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    sample = ["# Zwölf Anweisungen in vier Werkstatthänden", ""]
    for program in program_rows:
        sample.extend([f"## {program['program_id']}", "", f"Quelle: {program['source_instruction_de']}", ""])
        for row in [item for item in realizations if item["program_id"] == program["program_id"]]:
            sample.append(f"- {row['workshop_name']}: `{row['visible_surface_sequence']}`")
        sample.append("")
    (OUT / "NINETY_EIGHTH_TWELVE_PARALLEL_RENDERINGS.md").write_text("\n".join(sample), encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "profiles": len(PROFILES), "programs": len(PROGRAMS),
        "realizations": len(realizations), "programs_preserved": sum(row["semantic_program_preserved"] == "YES" for row in realizations),
        "changed_cards_by_renderer": dict(changed), "ambiguous_cards_by_renderer": dict(ambiguous),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
