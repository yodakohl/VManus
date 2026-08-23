#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_173_CARD_POCKET.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"
DECK = ROOT / "experiments/yolo/sidequest_semantic_exact_portable_deck_hundred_sixteenth_edition/HUNDRED_SIXTEENTH_SEVENTEEN_EXACT_PORTABLE_CARDS.tsv"

PROFILES = {
    "R-A": ("VORLAGENHAND", "master form; also corrects the whole batch"),
    "R-B": ("Q-EINTRITTSHAND", "prefer registered q-initial entry form"),
    "R-C": ("S-FLUSSHAND", "prefer registered sh/s continuation form"),
    "R-D": ("KURZHAND", "prefer shortest registered form"),
}

ASSIGNMENT = {
    "H1": "R-D", "H2": "R-B", "H3": "R-D", "H4": "R-D", "H5": "R-C",
    "B1": "R-D", "B2": "R-B", "B3": "R-B", "B4": "R-C", "B5": "R-A", "B6": "R-D",
}

SCHEDULE = {
    "H1": (4, 5), "H2": (4, 6), "H3": (6, 8), "H4": (9, 11), "H5": (4, 7),
    "B1": (12, 18), "B2": (7, 12), "B3": (13, 20), "B4": (8, 13), "B5": (4, 5), "B6": (19, 20),
}


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def choose(profile, card):
    variants = card["all_registered_surfaces"].split("|")
    master = card["master_form"]
    if profile == "R-A":
        return master
    if profile == "R-B":
        return next((x for x in variants if x.startswith("q")), master)
    if profile == "R-C":
        return next((x for x in variants if x.startswith("sh")), next((x for x in variants if x.startswith("s")), master))
    return min(enumerate(variants), key=lambda x: (len(x[1]), x[0]))[1]


def main():
    cards = {r["master_card_id"]: r for r in load(CARDS)}
    events = load(EVENTS)
    shared = {r["master_card_id"] for r in load(DECK)}
    assigned_counts = defaultdict(Counter)
    for row in events:
        assigned_counts[ASSIGNMENT[row["record_unit_id"]]][row["master_card_id"]] += 1

    trace = []
    for row in events:
        profile = ASSIGNMENT[row["record_unit_id"]]
        card = cards[row["master_card_id"]]
        preferred = choose(profile, card)
        if row["master_card_id"] in shared:
            learning = "MEMORIZE_SHARED_17"
        elif assigned_counts[profile][row["master_card_id"]] >= 2:
            learning = "MEMORIZE_RECURRENT_SECTION_CARD"
        else:
            learning = "COPY_SINGLETON_FROM_MASTER"
        trace.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "assigned_renderer": profile,
            "workshop_hand": PROFILES[profile][0],
            "master_card_id": row["master_card_id"],
            "semantic_atoms": row["semantic_atoms"],
            "actual_visible_surface": row["visible_surface"],
            "profile_preferred_surface": preferred,
            "surface_match": "YES" if preferred == row["visible_surface"] else "NO__COPY_PAGE_EXEMPLAR_OVERRIDE",
            "learning_mode": learning,
        })
    write_tsv("HUNDRED_NINETEENTH_381_EVENT_FOUR_HAND_TRACE.tsv", trace)

    record_rows = []
    for record, profile in ASSIGNMENT.items():
        members = [r for r in trace if r["record_unit_id"] == record]
        start, end = SCHEDULE[record]
        record_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "assigned_renderer": profile,
            "workshop_hand": PROFILES[profile][0],
            "day_start": str(start),
            "day_end": str(end),
            "event_count": str(len(members)),
            "surface_matches": str(sum(r["surface_match"] == "YES" for r in members)),
            "page_exemplar_overrides": str(sum(r["surface_match"] != "YES" for r in members)),
            "assignment_reason": "highest or tied-highest simple renderer fit on this record; master hand retains final correction",
        })
    write_tsv("HUNDRED_NINETEENTH_ELEVEN_RECORD_ASSIGNMENTS.tsv", record_rows)

    hand_rows = []
    for profile, (name, habit) in PROFILES.items():
        members = [r for r in trace if r["assigned_renderer"] == profile]
        cards_used = {r["master_card_id"] for r in members}
        memorized_recurrent = {r["master_card_id"] for r in members if r["learning_mode"] == "MEMORIZE_RECURRENT_SECTION_CARD"}
        singleton_copy = {r["master_card_id"] for r in members if r["learning_mode"] == "COPY_SINGLETON_FROM_MASTER"}
        hand_rows.append({
            "renderer_id": profile,
            "workshop_hand": name,
            "habit": habit,
            "assigned_records": "|".join(r for r, p in ASSIGNMENT.items() if p == profile),
            "assigned_events": str(len(members)),
            "distinct_cards_used": str(len(cards_used)),
            "shared_cards_memorized": "17",
            "additional_recurrent_cards_memorized": str(len(memorized_recurrent)),
            "singleton_cards_copied_from_master": str(len(singleton_copy)),
            "actual_surface_matches": str(sum(r["surface_match"] == "YES" for r in members)),
            "page_exemplar_overrides": str(sum(r["surface_match"] != "YES" for r in members)),
            "supervision_duty": "correct all 381 entries after copying" if profile == "R-A" else "submit record to master hand",
        })
    write_tsv("HUNDRED_NINETEENTH_FOUR_SCRIBE_WORKLOADS.tsv", hand_rows)

    md = [
        "# Vier Schreiber: zwanzigtägiger Kopierplan", "",
        "Tage 1–3: Alle vier lernen die siebzehn gemeinsamen Karten, Besitzerwechsel, Zeilenumbruch und Schlusskarten.", "",
    ]
    for row in hand_rows:
        md += [f"## {row['workshop_hand']}", "", f"Records: {row['assigned_records'] or 'keine eigene Langkopie'}; Ereignisse: {row['assigned_events']}.", f"Zusätzlich aktiv merken: {row['additional_recurrent_cards_memorized']} wiederkehrende Fachkarten; aus Vorlage kopieren: {row['singleton_cards_copied_from_master']} Einzelkarten.", ""]
    md += ["Die Vorlagenhand kopiert wenig selbst, prüft aber am Ende sämtliche Records gegen das Masterexemplar."]
    (OUT / "HUNDRED_NINETEENTH_TWENTY_DAY_FOUR_SCRIBE_SCHEDULE.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    report = [
        "# Hundertneunzehnte Runde: vier Hände als echte Werkstatt", "",
        "Die Recordzuweisung folgt der jeweils besten einfachen Rendererpassung: Kurzhand H1/H3/H4/B1/B6,",
        "q-Hand H2/B2/B3, s-Hand H5/B4 und Vorlagenhand B5. Die Vorlagenhand schreibt wenig, korrigiert",
        "aber die vollständige Charge; damit ist ihre geringe Rohlast historisch praktisch statt ein Fehler.", "",
        "Alle Hände lernen zuerst die siebzehn gemeinsamen Karten. Eine sektionsgebundene Karte wird nur",
        "aktiv memoriert, wenn sie in den zugewiesenen Records mindestens zweimal vorkommt; einmalige Karten",
        "werden aus dem Masterexemplar kopiert. Wo die sichtbare Seite nicht der bevorzugten Handform folgt,",
        "gilt die Seitenform als bewusster Exemplar-Override.", "",
        "Das erzeugt einen lehrbaren zwanzigtägigen Produktionsplan ohne vier verschiedene Sprachen oder",
        "eine unmögliche vollständige 173-Karten-Memorierung durch jeden Schreiber.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_NINETEENTH_FOUR_SCRIBE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "events": len(trace), "records": len(record_rows), "hands": len(hand_rows), "total_surface_matches": sum(r["surface_match"] == "YES" for r in trace), "total_overrides": sum(r["surface_match"] != "YES" for r in trace)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
