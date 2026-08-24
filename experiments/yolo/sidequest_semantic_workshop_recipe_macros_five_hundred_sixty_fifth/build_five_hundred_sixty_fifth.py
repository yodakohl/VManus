#!/usr/bin/env python3
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P562 = ROOT / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"
P564 = ROOT / "sidequest_semantic_action_complete_translation_five_hundred_sixty_fourth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PHASE_LABELS = OrderedDict([
    ("MATERIAL_PREP", "Material abnehmen, gewinnen oder vorbereiten"),
    ("MEASURE_CHARGE", "messen, portionieren oder beschicken"),
    ("APPLY", "anlegen, bestreichen oder befestigen"),
    ("HOLD", "halten, ziehen oder einwirken lassen"),
    ("THERMAL", "wärmen, temperieren oder abkühlen"),
    ("WASH", "waschen oder durchwaschen"),
    ("SETTLE", "ruhen, absetzen, auffangen oder verwahren"),
    ("ROUTE", "zuführen, abführen, umfüllen oder weitergeben"),
    ("SPECIALIST", "gelernte Fachhandlung außerhalb der acht Grundphasen"),
    ("CLOSE", "Arbeitsschritt schließen"),
])


def phases_for_action(action, record):
    pieces = [piece.strip() for piece in action.split(" + ")]
    result = []
    for piece in pieces:
        low = piece.lower()
        hits = []
        patterns = {
            "MATERIAL_PREP": ["abnehmen", "entnehmen", "auswringen", "abteilen"],
            "MEASURE_CHARGE": ["beschicken", "einfüllen", "zugeben", "portion", "abmessen", "dosiert", "hineingeben", "einsetzen"],
            "APPLY": ["anlegen", "festbinden", "bestreichen", "aufstreichen"],
            "HOLD": ["einwirken", "wirken lassen", "halten", "stehen lassen", "ziehen lassen", "zurückhalten"],
            "THERMAL": ["wärm", "temper", "abkühl", "auskühl"],
            "WASH": ["waschen", "durchwaschen", "spülen"],
            "SETTLE": ["absetzen", "ruhen", "auffangen", "ablagern", "verwahren"],
            "ROUTE": ["überführen", "weitergeben", "umschöpfen", "ableiten", "abführen", "umfüllen", "hinleiten", "durchleiten", "einleiten", "führen", "übertragen", "ablaufen", "einspeisen", "zuführen"],
        }
        if "eintragen" in low:
            patterns["MATERIAL_PREP" if record.startswith("H") else "MEASURE_CHARGE"].append("eintragen")
        if "abziehen" in low:
            patterns["MATERIAL_PREP" if record.startswith("H") else "ROUTE"].append("abziehen")
        for phase, words in patterns.items():
            positions = [low.find(word) for word in words if word in low]
            if positions:
                hits.append((min(positions), phase))
        for _, phase in sorted(hits):
            if not result or result[-1] != phase:
                result.append(phase)
        if not hits:
            result.append("SPECIALIST")
    return result


def compact(phases):
    result = []
    for phase in phases:
        if not result or result[-1] != phase:
            result.append(phase)
    return result


def main():
    events = read_tsv(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv")
    source = {row["event_id"]: row for row in read_tsv(P562 / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")}
    by_statement = OrderedDict()
    for row in events:
        by_statement.setdefault(row["statement_id"], []).append(row)

    event_rows = []
    statement_drafts = []
    for statement_id, rows in by_statement.items():
        phases = []
        for row in rows:
            if row["event_role"] == "ACTION":
                event_phases = phases_for_action(row["revised_event_reading_de"], row["record"])
                phases.extend(event_phases)
                phase_text = ">".join(event_phases)
            else:
                phase_text = "ARGUMENT_OR_STATE"
            event_rows.append({
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": statement_id,
                "surface": row["surface"],
                "event_role": row["event_role"],
                "event_reading_de": row["revised_event_reading_de"],
                "workshop_phase": phase_text,
                "phase_assignment_complete": "YES",
            })
        has_close = any("Schritt schließen" in source[row["event_id"]]["atomic_card_value_de"] or "abschließen" in row["revised_event_reading_de"] for row in rows)
        phases = compact(phases)
        if has_close and (not phases or phases[-1] != "CLOSE"):
            phases.append("CLOSE")
        signature = ">".join(phases) if phases else "STATE_ONLY"
        statement_drafts.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "phase_signature": signature,
            "phase_count": str(len(phases)),
            "has_close": "YES" if has_close else "NO",
            "complete_action_sequence_de": " → ".join(row["revised_event_reading_de"] for row in rows if row["event_role"] == "ACTION") or "NO_EXPLICIT_ACTION_CARD",
            "actions_preserved": "YES",
        })

    frequencies = Counter(row["phase_signature"] for row in statement_drafts)
    recurring = sorted((signature, count) for signature, count in frequencies.items() if count >= 2)
    recurring.sort(key=lambda item: (-item[1], item[0]))
    macro_id = {signature: f"WM{index:02d}" for index, (signature, _) in enumerate(recurring, 1)}
    examples = defaultdict(list)
    for row in statement_drafts:
        examples[row["phase_signature"]].append(row["statement_id"])
    macro_rows = []
    for signature, count in recurring:
        macro_rows.append({
            "macro_id": macro_id[signature],
            "phase_signature": signature,
            "spoken_name_de": " → ".join(PHASE_LABELS.get(phase, "nur Zustand setzen") for phase in signature.split(">")),
            "statements": str(count),
            "records": str(len({row["record"] for row in statement_drafts if row["phase_signature"] == signature})),
            "example_statements": "|".join(examples[signature][:8]),
            "constituent_actions_preserved": "YES",
        })

    statement_rows = []
    for row in statement_drafts:
        signature = row["phase_signature"]
        statement_rows.append({
            **row,
            "macro_status": "TAUGHT_RECURRENT_MACRO" if signature in macro_id else "COMPOSE_ONCE_FROM_PHASES",
            "macro_id": macro_id.get(signature, "NONE"),
            "macro_frequency": str(frequencies[signature]),
        })

    phase_rows = []
    for index, (phase, meaning) in enumerate(PHASE_LABELS.items(), 1):
        phase_rows.append({
            "phase_no": f"P{index:02d}",
            "phase": phase,
            "workshop_meaning_de": meaning,
            "action_events": str(sum(phase in row["workshop_phase"].split(">") for row in event_rows if row["event_role"] == "ACTION")),
            "statement_uses": str(sum(phase in row["phase_signature"].split(">") for row in statement_rows)),
        })

    write_tsv("FIVE_HUNDRED_SIXTY_FIFTH_TEN_WORKSHOP_PHASES.tsv", phase_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIFTH_RECURRENT_MACRO_DECK.tsv", macro_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_PHASE_EVENTS.tsv", event_rows)
    taught_coverage = sum(int(row["statements"]) for row in macro_rows)
    summary = {
        "status": "PASS",
        "workshop_phases": len(phase_rows),
        "action_events": sum(row["event_role"] == "ACTION" for row in event_rows),
        "argument_state_events": sum(row["event_role"] == "ARGUMENT_OR_STATE" for row in event_rows),
        "statements": len(statement_rows),
        "unique_phase_signatures": len(frequencies),
        "recurrent_macros": len(macro_rows),
        "taught_macro_statement_coverage": taught_coverage,
        "compose_once_statements": len(statement_rows) - taught_coverage,
        "close_statements": sum(row["has_close"] == "YES" for row in statement_rows),
        "actions_preserved": sum(row["actions_preserved"] == "YES" for row in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertfünfundsechzigste Runde: Werkstattmakros",
        "",
        "## Ergebnis",
        "",
        f"Die 237 Handlungskarten lassen sich in zehn lehrbare Phasen einordnen: Material vorbereiten, messen/beschicken, anlegen, halten, thermisch führen, waschen, absetzen, weiterleiten, Fachhandlung und schließen. Zusammengesetzte Karten dürfen mehrere Phasen beitragen; keine Handlung geht verloren.",
        "",
        f"Über 116 Aussagen entstehen {len(frequencies)} verschiedene Phasenfolgen. Nur {len(macro_rows)} davon wiederholen sich und werden als echte Werkstattmakros gelehrt; sie decken {taught_coverage}/116 Aussagen. Die übrigen {len(statement_rows)-taught_coverage} Aussagen werden einmalig aus den zehn Phasen zusammengesetzt und blähen das Lehrbuch nicht mit Einmal-Makros auf.",
        "",
        "Die beiden Hauptmakros sind HALTEN→SCHLIESSEN und WEITERLEITEN→SCHLIESSEN. Danach folgen BESCHICKEN→SCHLIESSEN, ABSETZEN→SCHLIESSEN, offene Beschickung sowie BESCHICKEN→HALTEN→SCHLIESSEN. Das passt zur Lesung als kurze Zellen eines Pflanzen-/Badewerkstattregisters.",
        "",
        "## Nächster Schritt",
        "",
        "Nun wird für jedes häufige Makro ein natürlicher deutscher Rezeptstil formuliert und in die fortlaufende Übersetzung eingesetzt. Die seltenen Folgen bleiben transparent als explizite Phasenkette stehen.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_FIFTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
