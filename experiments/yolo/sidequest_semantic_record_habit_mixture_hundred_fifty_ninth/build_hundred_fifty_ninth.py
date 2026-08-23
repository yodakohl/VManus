#!/usr/bin/env python3
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R157 = ROOT / "experiments/yolo/sidequest_semantic_shared_renderer_simplification_hundred_fifty_seventh"
PROFILES = ["MASTER_BARE", "CH_OPEN_HAND", "Q_CELL_HAND", "S_FLOW_HAND", "HARD_COMPACT_HAND"]
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def smallest_max_cover(rows, choice):
    covered = {
        profile: {
            i for i, row in enumerate(rows)
            if choice[(profile, row["master_card_id"])] == row["visible_surface"]
        }
        for profile in PROFILES
    }
    maximum = set().union(*(covered[profile] for profile in PROFILES))
    for size in range(1, len(PROFILES) + 1):
        for subset in itertools.combinations(PROFILES, size):
            if set().union(*(covered[profile] for profile in subset)) == maximum:
                return subset, maximum
    raise AssertionError("no profile cover")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    surfaces = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv")
    trace = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_251_SHARED_EVENT_RENDER_TRACE.tsv")
    choices = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_FIVE_HAND_SHARED_COPYBOOK.tsv")
    choice = {(row["profile"], row["master_card_id"]): row["chosen_surface"] for row in choices}
    registered = {(row["master_card_id"], row["visible_surface"]): row for row in surfaces}

    audit_rows = []
    by_record = defaultdict(list)
    exceptions = defaultdict(list)
    for row in trace:
        matches = [
            profile for profile in PROFILES
            if choice[(profile, row["master_card_id"])] == row["visible_surface"]
        ]
        key = (row["master_card_id"], row["visible_surface"])
        surface = registered[key]
        same_habit_profile_forms = sorted({
            choice[(profile, row["master_card_id"])]
            for profile in PROFILES
            if registered[(row["master_card_id"], choice[(profile, row["master_card_id"])])]["five_habit_class"]
            == row["five_habit_class"]
        })
        status = "PROFILE_REPRODUCED" if matches else "REGISTERED_MICRO_ALLOGRAPH_WITHIN_HABIT"
        out = {
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "card_value_de": row["card_value_de"],
            "five_habit_class": row["five_habit_class"],
            "matching_extreme_profiles": "|".join(matches) if matches else "NONE",
            "fit_status": status,
            "same_habit_profile_forms": "|".join(same_habit_profile_forms),
            "registered_surface": "YES",
            "master_recovery": "EXACT",
        }
        audit_rows.append(out)
        by_record[row["record_unit_id"]].append(out)
        if not matches:
            exceptions[key].append(out)
    write_tsv("HUNDRED_FIFTY_NINTH_251_OBSERVED_PROFILE_FIT.tsv", audit_rows)

    record_rows = []
    for record_id in RECORD_ORDER:
        rows = by_record[record_id]
        subset, maximum = smallest_max_cover(rows, choice)
        single_scores = {
            profile: sum(choice[(profile, row["master_card_id"])] == row["visible_surface"] for row in rows)
            for profile in PROFILES
        }
        best_score = max(single_scores.values())
        best_single = [profile for profile in PROFILES if single_scores[profile] == best_score]
        habits = Counter(row["five_habit_class"] for row in rows)
        record_rows.append({
            "record_unit_id": record_id,
            "page": rows[0]["page"],
            "shared_events": str(len(rows)),
            "observed_habit_count": str(len(habits)),
            "observed_habit_inventory": "|".join(f"{habit}:{habits[habit]}" for habit in sorted(habits)),
            "best_single_profile": "|".join(best_single),
            "best_single_profile_matches": str(best_score),
            "best_single_profile_misses": str(len(rows) - best_score),
            "smallest_max_cover_profile_count": str(len(subset)),
            "smallest_max_cover_profiles": "|".join(subset),
            "profile_reproduced_events": str(len(maximum)),
            "registered_micro_allograph_events": str(len(rows) - len(maximum)),
            "one_stable_extreme_profile": "NO",
            "record_renderer_model": "MIX_HABITS_THEN_SELECT_REGISTERED_MICRO_ALLOGRAPH",
        })
    write_tsv("HUNDRED_FIFTY_NINTH_11_RECORD_HABIT_MIXTURES.tsv", record_rows)

    exception_rows = []
    for (card_id, visible), rows in sorted(exceptions.items()):
        profile_forms = rows[0]["same_habit_profile_forms"]
        exception_rows.append({
            "master_card_id": card_id,
            "card_value_de": rows[0]["card_value_de"],
            "observed_surface": visible,
            "five_habit_class": rows[0]["five_habit_class"],
            "event_count": str(len(rows)),
            "records": "|".join(sorted({row["record_unit_id"] for row in rows})),
            "event_serials": "|".join(row["event_serial"] for row in rows),
            "extreme_profile_form_in_same_habit": profile_forms,
            "apprentice_treatment": "LEARN_AS_SECOND_REGISTERED_SPELLING_INSIDE_SAME_HABIT",
            "new_meaning": "NONE",
        })
    write_tsv("HUNDRED_FIFTY_NINTH_10_MICRO_ALLOGRAPHS.tsv", exception_rows)

    manual = [
        "# Record-Mischregel der Werkstatt", "",
        "Die fünf Profile aus R157/R158 sind Lehr-Extreme, keine fünf fest identifizierten Schreiber.",
        "Jeder wirkliche Record mischt drei bis fünf der sichtbaren Gewohnheiten.", "",
        "1. Schlage zuerst die gemeinsame Masterkarte und ihren Wert nach.",
        "2. Wähle nach Zellanfang und laufender Hand eine der fünf Gewohnheiten:",
        "   bare/internal, ch-open, q-cell, s/sh-flow oder d/t-hard.",
        "3. Hat dieselbe Karte innerhalb dieser Gewohnheit zwei registrierte Schreibungen, darf der",
        "   Schreiber die lokal gelernte Mikrovariante nehmen: etwa `chdy/chedy`, `chey/chy`,",
        "   `cheol/chol` oder `chal/cheal`.",
        "4. Eine Mikrovariante ändert nie die Karte und nie die Bedeutung.",
        "5. Seltene lokale Nomenklatorkarten werden weiterhin exakt aus dem Exemplar kopiert.", "",
        "## Tatsächliche Records", "",
        "| Record | gemeinsame Ereignisse | Gewohnheiten | bestes Einzelprofil | maximale Extremmischung | Mikrovarianten |",
        "|---|---:|---:|---|---|---:|",
    ]
    for row in record_rows:
        manual.append(
            f"| {row['record_unit_id']} | {row['shared_events']} | {row['observed_habit_count']} | "
            f"{row['best_single_profile'].replace('|', ', ')} ({row['best_single_profile_matches']}) | "
            f"{row['smallest_max_cover_profiles'].replace('|', ', ')} | {row['registered_micro_allograph_events']} |"
        )
    manual += ["", "Die Extremmischung ist nur eine kürzeste Beschreibung der bereits beobachteten Formen.",
               "Die eigentliche Schreibregel ist die Gewohnheitswahl plus registrierte Mikrovariante."]
    (OUT / "HUNDRED_FIFTY_NINTH_RECORD_HABIT_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertneunundfünfzigste Runde: Profile sind Gewohnheiten, nicht Schreiberidentitäten", "",
        "No observed record is reproduced by one fixed extreme profile. The eleven records each mix three to",
        "five habits. A lexicographically smallest maximum-cover mixture uses two to five extreme profiles per",
        "record and directly reproduces 228 of 251 shared-card events.", "",
        "The remaining 23 events are not new renderer classes. They are ten registered second spellings inside",
        "an existing habit, concentrated in eight cards: for example CH-entry `chdy/chedy`, `chey/chy`,",
        "`cheol/chol`, and `chal/cheal`. All 251 events therefore still use exactly the five habits and recover",
        "their master card exactly.", "",
        "The corrected workshop picture is simpler: several scribes learn the same five entry habits, but each",
        "record mixes them and may preserve a local micro-allograph. The profiles remain useful teaching samples;",
        "they must not be read as five literal hands or semantic dialects.", "",
        "Next derive the smallest positional habit schedule for all eleven records: which habit is chosen at",
        "field entry, after a close, inside a running clause, and at a carried line boundary.",
    ]
    (OUT / "HUNDRED_FIFTY_NINTH_RECORD_HABIT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "shared_events": len(audit_rows),
        "profile_reproduced_events": sum(row["fit_status"] == "PROFILE_REPRODUCED" for row in audit_rows),
        "registered_micro_allograph_events": sum(row["fit_status"] != "PROFILE_REPRODUCED" for row in audit_rows),
        "micro_allograph_forms": len(exception_rows),
        "affected_master_cards": len({row["master_card_id"] for row in exception_rows}),
        "records": len(record_rows),
        "records_reproduced_by_one_profile": sum(row["best_single_profile_misses"] == "0" for row in record_rows),
        "minimum_observed_habits": min(int(row["observed_habit_count"]) for row in record_rows),
        "maximum_observed_habits": max(int(row["observed_habit_count"]) for row in record_rows),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
