#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R116 = ROOT / "experiments/yolo/sidequest_semantic_exact_portable_deck_hundred_sixteenth_edition"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv"

EXERCISES = [
    ("EX01", ["MC154"], "den Posten zum Ziel führen", "B1-S021"),
    ("EX02", ["MC026"], "den aktuellen Posten ansetzen", "B3-S009"),
    ("EX03", ["MC019"], "weiterführen und schließen", "B4-S010"),
    ("EX04", ["MC055", "MC026"], "aus der Quelle den Posten ansetzen", "GENERATED_CORE_EXERCISE"),
    ("EX05", ["MC080", "MC123", "MC039"], "den aktuellen Ansatz auf Sollmaß bringen", "GENERATED_CORE_EXERCISE"),
    ("EX06", ["MC123", "MC039", "MC123"], "zwei Posten unter dasselbe Sollmaß stellen", "GENERATED_CORE_EXERCISE"),
    ("EX07", ["MC040", "MC032"], "am Ziel ansetzen und den Posten länger wärmen", "GENERATED_CORE_EXERCISE"),
    ("EX08", ["MC120", "MC161"], "Sollmaß ansetzen und den Posten bereit halten", "GENERATED_CORE_EXERCISE"),
    ("EX09", ["MC086", "MC154", "MC074"], "einen Teil abteilen und am Ziel umsetzen", "GENERATED_CORE_EXERCISE"),
    ("EX10", ["MC157", "MC153"], "den vorigen Ansatz weiterführen", "GENERATED_CORE_EXERCISE"),
    ("EX11", ["MC171", "MC026"], "danach den nächsten Posten ansetzen", "GENERATED_CORE_EXERCISE"),
    ("EX12", ["MC119", "MC019"], "das Ergebnis übernehmen, weiterführen und schließen", "GENERATED_CORE_EXERCISE"),
]


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def short_variant(card, mode):
    variants = card["all_registered_surfaces"].split("|")
    if mode == "MASTER":
        return card["master_form"]
    if mode == "S_FLOW":
        return next((x for x in variants if x.startswith("sh")), next((x for x in variants if x.startswith("s")), card["master_form"]))
    return min(enumerate(variants), key=lambda x: (len(x[1]), x[0]))[1]


def main():
    deck = load(R116 / "HUNDRED_SIXTEENTH_SEVENTEEN_EXACT_PORTABLE_CARDS.tsv")
    deck_ids = {r["master_card_id"] for r in deck}
    dictionary = load(R116 / "HUNDRED_SIXTEENTH_173_FINAL_TEACHING_DICTIONARY.tsv")
    card_map = {r["master_card_id"]: r for r in dictionary}
    statements = load(STATEMENTS)

    coverage_rows = []
    for row in statements:
        ids = row["visible_surface_sequence"].split()
        # Recover IDs from the atom-aligned centennial statement through source order.
        # The master IDs are not carried in R110, so look them up by visible surface.
        candidates = defaultdict(list)
        for card in dictionary:
            for surface in card["all_registered_surfaces"].split("|"):
                candidates[surface].append(card["master_card_id"])
        resolved = []
        for surface, atoms in zip(ids, row["semantic_atom_program"].split(" | ")):
            matches = [cid for cid in candidates[surface] if card_map[cid]["semantic_atoms"] == atoms]
            if len(matches) != 1:
                raise AssertionError((row["statement_id"], surface, atoms, matches))
            resolved.append(matches[0])
        hit = [cid in deck_ids for cid in resolved]
        status = "FULLY_WRITABLE_WITH_17" if all(hit) else "NO_PORTABLE_CARD" if not any(hit) else "PORTABLE_SKELETON_ONLY"
        missing = [card_map[cid] for cid, ok in zip(resolved, hit) if not ok]
        coverage_rows.append({
            "statement_order": row["statement_order"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "master_card_ids": " ".join(resolved),
            "visible_surface_sequence": row["visible_surface_sequence"],
            "portable_card_count": str(sum(hit)),
            "total_card_count": str(len(hit)),
            "coverage_status": status,
            "missing_card_forms": "|".join(x["master_form"] for x in missing) if missing else "NONE",
            "missing_teaching_tiers": "|".join(x["final_teaching_tier"] for x in missing) if missing else "NONE",
            "current_reading_de": row["current_reading_de"],
        })
    write_tsv("HUNDRED_SEVENTEENTH_116_MINIMAL_DECK_COVERAGE.tsv", coverage_rows)

    by_record = defaultdict(list)
    for row in coverage_rows:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    for record, members in by_record.items():
        portable_events = sum(int(r["portable_card_count"]) for r in members)
        all_events = sum(int(r["total_card_count"]) for r in members)
        record_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "statement_count": str(len(members)),
            "fully_writable_statements": str(sum(r["coverage_status"] == "FULLY_WRITABLE_WITH_17" for r in members)),
            "skeleton_only_statements": str(sum(r["coverage_status"] == "PORTABLE_SKELETON_ONLY" for r in members)),
            "no_portable_card_statements": str(sum(r["coverage_status"] == "NO_PORTABLE_CARD" for r in members)),
            "portable_events": str(portable_events),
            "total_events": str(all_events),
        })
    write_tsv("HUNDRED_SEVENTEENTH_ELEVEN_RECORD_COVERAGE.tsv", record_rows)

    exercise_rows = []
    for ex_id, ids, source, provenance in EXERCISES:
        selected = [card_map[x] for x in ids]
        exercise_rows.append({
            "exercise_id": ex_id,
            "source_instruction_de": source,
            "provenance": provenance,
            "master_card_ids": " ".join(ids),
            "atom_program": " | ".join(x["semantic_atoms"] for x in selected),
            "master_rendering": " ".join(short_variant(x, "MASTER") for x in selected),
            "s_flow_rendering": " ".join(short_variant(x, "S_FLOW") for x in selected),
            "short_hand_rendering": " ".join(short_variant(x, "SHORT") for x in selected),
            "uses_only_17_card_deck": "YES" if set(ids) <= deck_ids else "NO",
        })
    write_tsv("HUNDRED_SEVENTEENTH_TWELVE_MINIMAL_DECK_EXERCISES.tsv", exercise_rows)

    statuses = Counter(r["coverage_status"] for r in coverage_rows)
    portable_events = sum(int(r["portable_card_count"]) for r in coverage_rows)
    total_events = sum(int(r["total_card_count"]) for r in coverage_rows)
    report = [
        "# Hundertsiebzehnte Runde: Was kann das 17-Karten-Deck allein?", "",
        "Nur drei der 116 vorhandenen Aussagen sind vollständig mit dem echten portablen Deck schreibbar:",
        "B1-S021 (`chal`), B3-S009 (`qoky`) und B4-S010 (`oldy`). 54 weitere Aussagen haben ein",
        "portables Gerüst, 59 enthalten überhaupt keine der siebzehn exakten Karten.", "",
        f"Auf Ereignisebene deckt das Deck {portable_events} von {total_events} sichtbaren Karten. Es ist",
        "also ein echtes Kontroll- und Argumentdeck, aber kein vollständiges Inhaltslexikon. Genau dafür",
        "braucht der Lehrling die sektionsgebundenen Karten und fünf Spezialtafeln.", "",
        "Zwölf Schreibübungen zeigen dennoch, dass das kleine Deck produktiv ist. Drei sind echte kurze",
        "Aussagen; neun kombinieren die Karten zu vorhergesagten Anweisungen wie `chey aiin chey` für",
        "zwei Posten unter demselben Sollmaß oder `chety al chdy` für Teilen und Umsetzen am Ziel.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_SEVENTEENTH_MINIMAL_DECK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "statements": len(coverage_rows), "coverage_status": dict(statuses), "portable_events": portable_events, "total_events": total_events, "exercises": len(exercise_rows)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
