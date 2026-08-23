#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_schedule_hundred_nineteenth_edition/HUNDRED_NINETEENTH_381_EVENT_FOUR_HAND_TRACE.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_230_SURFACE_INDEX.tsv"

SECONDARY = {"R-A": "D_ENTRY", "R-B": "D_ENTRY", "R-C": "Q_ENTRY", "R-D": "CH_ENTRY"}


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    trace = load(TRACE)
    surface = {r["visible_surface"]: r for r in load(SURFACES)}
    by_statement = defaultdict(list)
    for row in trace:
        by_statement[row["statement_id"]].append(row)

    audit = []
    for row in trace:
        if row["surface_match"] == "YES":
            continue
        members = by_statement[row["statement_id"]]
        index = next(i for i, x in enumerate(members) if x["event_serial"] == row["event_serial"])
        position = "ONLY" if len(members) == 1 else "FIRST" if index == 0 else "LAST" if index == len(members)-1 else "MIDDLE"
        gesture = surface[row["actual_visible_surface"]]["renderer_gesture"]
        audit.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "assigned_renderer": row["assigned_renderer"],
            "master_card_id": row["master_card_id"],
            "profile_preferred_surface": row["profile_preferred_surface"],
            "actual_visible_surface": row["actual_visible_surface"],
            "actual_renderer_gesture": gesture,
            "statement_position": position,
            "secondary_gesture_for_hand": SECONDARY[row["assigned_renderer"]],
            "resolved_by_secondary_repertoire": "YES" if gesture == SECONDARY[row["assigned_renderer"]] else "NO",
        })
    write_tsv("HUNDRED_TWENTIETH_102_OVERRIDE_AUDIT.tsv", audit)

    hand_rows = []
    for hand, gesture in SECONDARY.items():
        members = [r for r in audit if r["assigned_renderer"] == hand]
        resolved = [r for r in members if r["resolved_by_secondary_repertoire"] == "YES"]
        hand_rows.append({
            "renderer_id": hand,
            "secondary_gesture": gesture,
            "original_overrides": str(len(members)),
            "absorbed_by_secondary": str(len(resolved)),
            "remaining_master_overrides": str(len(members)-len(resolved)),
            "common_positions": "|".join(f"{p}:{n}" for p, n in Counter(r["statement_position"] for r in resolved).most_common()) or "NONE",
            "training_rule": f"besides the primary habit, recognize and copy licensed {gesture} forms when the page exemplar calls for them",
        })
    write_tsv("HUNDRED_TWENTIETH_FOUR_SECONDARY_HAND_HABITS.tsv", hand_rows)

    revised = []
    audit_map = {r["event_serial"]: r for r in audit}
    for row in trace:
        if row["surface_match"] == "YES":
            status = "PRIMARY_HABIT_MATCH"
        elif audit_map[row["event_serial"]]["resolved_by_secondary_repertoire"] == "YES":
            status = "SECONDARY_REPERTOIRE_MATCH"
        else:
            status = "COPY_MASTER_EXEMPLAR_OVERRIDE"
        revised.append({**row, "revised_renderer_status": status})
    write_tsv("HUNDRED_TWENTIETH_381_REVISED_RENDERER_TRACE.tsv", revised)

    absorbed = sum(r["resolved_by_secondary_repertoire"] == "YES" for r in audit)
    models = [
        {"model": "PRIMARY_ONLY", "extra_rules": "0", "explained_events": "279", "remaining_overrides": "102", "gain_per_extra_rule": "NA"},
        {"model": "ONE_SECONDARY_PER_HAND", "extra_rules": "4", "explained_events": str(279+absorbed), "remaining_overrides": str(102-absorbed), "gain_per_extra_rule": f"{absorbed/4:.2f}"},
        {"model": "ONE_SECONDARY_PER_RECORD", "extra_rules": "11", "explained_events": "319", "remaining_overrides": "62", "gain_per_extra_rule": f"{40/11:.2f}"},
        {"model": "SEVEN_FAMILY_RECORD_TABLE", "extra_rules": "36", "explained_events": "330", "remaining_overrides": "51", "gain_per_extra_rule": f"{51/36:.2f}"},
        {"model": "OCCURRENCE_EXEMPLAR", "extra_rules": "102", "explained_events": "381", "remaining_overrides": "0", "gain_per_extra_rule": "1.00"},
    ]
    write_tsv("HUNDRED_TWENTIETH_RENDERER_ECONOMY.tsv", models)

    report = [
        "# Hundertzwanzigste Runde: zweite Handgewohnheit", "",
        "Eine zweite zugelassene Eintrittsgewohnheit pro Hand absorbiert 27 der 102 bisherigen Overrides:",
        "D-Antritt für Vorlagen- und q-Hand, Q-Antritt für s-Hand, CH-Antritt für Kurzhand. Damit steigen",
        "die direkt im Handrepertoire erklärten Ereignisse von 279 auf 306; 75 bleiben Masterexemplar-Kopien.", "",
        "Mehr Regeln lohnen sich kaum. Eine Sekundärregel pro Record erklärt 319 Ereignisse, braucht aber elf",
        "Zusatzregeln. Eine 36-zeilige Familien-/Recordtabelle erklärt 330. Das ist weniger lehrbar als die",
        "schlichte Anweisung, seltene Varianten direkt aus dem Exemplar zu kopieren.", "",
        "Das aktuelle Mehrschreibermodell hat daher je Hand zwei Gewohnheiten, ein gemeinsames 17-Karten-Deck",
        "und 75 sichtbare Exemplar-Overrides. Position allein erklärt die Restformen nicht zuverlässig.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_TWENTIETH_SECONDARY_RENDERER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "original_overrides": len(audit), "absorbed": absorbed, "remaining": len(audit)-absorbed, "primary_matches": 279, "primary_plus_secondary": 279+absorbed}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
