#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P476 = ROOT / "experiments/yolo/sidequest_semantic_workflow_phases_four_hundred_seventy_sixth"
P475 = ROOT / "experiments/yolo/sidequest_semantic_readable_compression_four_hundred_seventy_fifth"

TEMPLATES = [
    ("M01", ("PREPARE", "MEASURE", "MOVE"), "Bereite den Posten „{posten}“ vor, setze die angegebene Menge oder Stufe und führe ihn zur bezeichneten Stelle."),
    ("M02", ("MEASURE", "MOVE", "MEASURE"), "Setze für den Posten „{posten}“ das erste Maß, bewege ihn und setze am Ziel das nächste Maß."),
    ("M03", ("MOVE", "PREPARE", "MOVE"), "Führe den Posten „{posten}“ zur Arbeitsstelle, bearbeite ihn dort und führe ihn weiter."),
    ("M04", ("MEASURE", "MOVE"), "Nimm vom Posten „{posten}“ das angegebene Maß und führe diesen Teil zur bezeichneten Stelle."),
    ("M05", ("MEASURE", "HOLD"), "Setze für den Posten „{posten}“ Menge oder Stufe und halte ihn wie angegeben."),
    ("M06", ("MOVE", "MEASURE"), "Führe den Posten „{posten}“ zur Stelle und setze dort Menge oder Stufe."),
    ("M07", ("MOVE", "PREPARE"), "Führe den Posten „{posten}“ weiter und beginne damit den nächsten Arbeitsgang."),
    ("M08", ("PREPARE", "MEASURE"), "Bereite den Posten „{posten}“ und setze dafür Menge oder Stufe."),
    ("M09", ("APPLY", "MEASURE"), "Setze den Posten „{posten}“ an der Zielstelle an und bestimme Menge oder Dauer."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def runs(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        if out and out[-1]["phase"] == row["action_phase"]:
            out[-1]["rows"].append(row)  # type: ignore[index]
        else:
            out.append({"phase": row["action_phase"], "rows": [row]})
    return out


def span_text(span: list[dict[str, object]]) -> str:
    event_rows = [row for run in span for row in run["rows"]]  # type: ignore[index]
    return "; ".join(str(row["compressed_event_de"]) for row in event_rows)


def fill(template: str, span: list[dict[str, object]]) -> str:
    first = span[0]["rows"][0]  # type: ignore[index]
    posten = str(first["short_active_before_de"])
    return template.format(posten=posten)


def main() -> None:
    events = read(P476 / "FOUR_HUNDRED_SEVENTY_SIXTH_381_EVENT_PHASES.tsv")
    statements = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_116_READABLE_WORKSHOP_STATEMENTS.tsv")
    astro = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    template_by_pattern = {pattern: (template_id, text) for template_id, pattern, text in TEMPLATES}

    all_occurrences = []
    template_counts: Counter[tuple[str, str]] = Counter()
    template_records: dict[tuple[str, str], set[str]] = defaultdict(set)
    for sid, rows in by_statement.items():
        phase_runs = runs(rows)
        phases = [run["phase"] for run in phase_runs]
        for template_id, pattern, template in TEMPLATES:
            n = len(pattern)
            for index in range(len(phases) - n + 1):
                if tuple(phases[index:index+n]) != pattern:
                    continue
                span = phase_runs[index:index+n]
                event_rows = [event for run in span for event in run["rows"]]  # type: ignore[index]
                key = (template_id, rows[0]["register"])
                template_counts[key] += 1
                template_records[key].add(rows[0]["record_unit_id"])
                all_occurrences.append({
                    "occurrence_id": f"O{len(all_occurrences)+1:03d}",
                    "template_id": template_id,
                    "phase_pattern": ">".join(pattern),
                    "register": rows[0]["register"],
                    "record_unit_id": rows[0]["record_unit_id"],
                    "page": rows[0]["page"],
                    "statement_id": sid,
                    "run_start": index + 1,
                    "event_ids": "|".join(str(row["event_id"]) for row in event_rows),
                    "concrete_referent_de": event_rows[0]["short_active_before_de"],
                    "template_sentence_de": fill(template, span),
                    "actual_span_de": span_text(span),
                    "selected_in_greedy_edition": "NO",
                })

    statement_rows = []
    selected_keys: set[tuple[str, int]] = set()
    covered_events: set[str] = set()
    for source in statements:
        sid = source["statement_id"]
        rows = by_statement[sid]
        phase_runs = runs(rows)
        phases = [run["phase"] for run in phase_runs]
        chunks = []
        templates_used = []
        i = 0
        while i < len(phase_runs):
            chosen = None
            for n in (3, 2):
                pattern = tuple(phases[i:i+n])
                if len(pattern) == n and pattern in template_by_pattern:
                    chosen = (n, pattern, template_by_pattern[pattern])
                    break
            if chosen:
                n, pattern, (template_id, text) = chosen
                span = phase_runs[i:i+n]
                chunks.append(fill(text, span) + " [" + span_text(span) + "]")
                templates_used.append(template_id)
                event_rows = [event for run in span for event in run["rows"]]  # type: ignore[index]
                covered_events.update(str(row["event_id"]) for row in event_rows)
                selected_keys.add((sid, i + 1))
                i += n
            else:
                chunks.append("[" + span_text([phase_runs[i]]) + "]")
                i += 1
        statement_rows.append({
            "statement_id": sid,
            "register": source["register"],
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "events": source["events"],
            "event_ids": source["event_ids"],
            "phase_runs": len(phase_runs),
            "templates_used": "|".join(templates_used) if templates_used else "NONE",
            "template_covered_events": sum(event in covered_events for event in source["event_ids"].split("|")),
            "template_workshop_sentence_de": " ".join(chunks),
        })
    for row in all_occurrences:
        if (row["statement_id"], int(row["run_start"])) in selected_keys:
            row["selected_in_greedy_edition"] = "YES"
    write("FOUR_HUNDRED_SEVENTY_SEVENTH_MOTIF_OCCURRENCES.tsv", all_occurrences)
    write("FOUR_HUNDRED_SEVENTY_SEVENTH_116_TEMPLATE_SENTENCES.tsv", statement_rows)

    template_rows = []
    for template_id, pattern, text in TEMPLATES:
        h = template_counts[(template_id, "HERBAL")]
        b = template_counts[(template_id, "BIOLOGICAL")]
        template_rows.append({
            "template_id": template_id,
            "phase_pattern": ">".join(pattern),
            "teaching_sentence_de": text,
            "herbal_occurrences": h,
            "biological_occurrences": b,
            "herbal_records": len(template_records[(template_id, "HERBAL")]),
            "biological_records": len(template_records[(template_id, "BIOLOGICAL")]),
            "cross_register": "YES" if h and b else "NO",
            "total_occurrences": h + b,
        })
    write("FOUR_HUNDRED_SEVENTY_SEVENTH_NINE_SENTENCE_TEMPLATES.tsv", template_rows)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "template_covered_events": sum(int(row["template_covered_events"]) for row in rows),
            "continuous_template_edition_de": " ".join(row["template_workshop_sentence_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "template_covered_events": 0,
            "continuous_template_edition_de": " ".join(row["readable_locus_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_SEVENTH_14_TEMPLATE_UNIT_EDITIONS.tsv", units)

    md = ["# Sentence-template ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_template_edition_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_SEVENTH_TEMPLATE_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "templates": len(template_rows),
        "cross_register_templates": sum(row["cross_register"] == "YES" for row in template_rows),
        "motif_occurrences": len(all_occurrences),
        "statements": len(statement_rows),
        "statements_using_template": sum(row["templates_used"] != "NONE" for row in statement_rows),
        "unique_events_covered_by_greedy_templates": len(covered_events),
        "prose_events": len(events),
        "units": len(units),
        "groups": sum(int(row["groups"]) for row in units),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
