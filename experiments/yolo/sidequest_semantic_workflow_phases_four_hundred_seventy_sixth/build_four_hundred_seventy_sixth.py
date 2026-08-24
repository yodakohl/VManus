#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P475 = ROOT / "experiments/yolo/sidequest_semantic_readable_compression_four_hundred_seventy_fifth"

PHASES = {
    "SELECT": "aktiven Stoff, Posten oder Bezug wählen",
    "PREPARE": "Ansatz bilden, bearbeiten oder fortsetzen",
    "MEASURE": "Menge, Anteil oder Stufe setzen",
    "MOVE": "Bestand zwischen Stelle, Gefäß oder Durchgang bewegen",
    "APPLY": "Bestand an einer Zielstelle verwenden oder befestigen",
    "HOLD": "kurz/länger halten, wärmen, senken oder absetzen",
    "CHECK": "Bereitschaft, Ergebnis oder Fachzustand lesen",
    "COLLECT": "Fraktion entnehmen oder aufgefangenen Bestand bilden",
    "CLOSE": "lokalen Arbeitsschritt abschließen",
}


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


def classify(value: str, parse: str) -> tuple[str, str]:
    low = value.lower()
    parts = set(parse.replace("WHOLE[", "").replace("]", "").split("+"))
    if any(word in low for word in ("verwende", "befestigen", "auflegen", "bestreichen", "aufstreichen")) or ("stelle" in low and any(word in low for word in ("ansetzen", "setzen", "halten"))):
        return "APPLY", "application wording"
    if any(word in low for word in ("maß", "portion", "bemessen", "stufe", "grad")) or parts & {"AIIN", "AIN", "IIN"}:
        return "MEASURE", "quantity or grade wording/component"
    if any(word in low for word in ("auffangen", "klarauszug", "ergebnis", "abziehen", "entnahme")):
        return "COLLECT", "fraction/result wording"
    if any(word in low for word in ("halten", "wärmen", "abkühlen", "absetzen", "ruhen", "bereit halten", "bereithalten")) or parts & {"E", "EE", "EEE", "SH", "SHED", "R", "CHK"}:
        return "HOLD", "duration/state-change wording/component"
    if any(word in low for word in ("bereit", "fach", "prüf", "gültig")) or parts & {"CTH", "OS"}:
        return "CHECK", "readiness or status wording/component"
    if any(word in low for word in ("zuführen", "führen", "füllen", "hinein", "hinaus", "durchgang", "lauf", "von dort", "zur stelle", "an die stelle")) or parts & {"L", "P", "T", "AIR", "CHD", "CKH", "LS", "AR", "AL"}:
        return "MOVE", "source/path/target wording/component"
    if any(word in low for word in ("zutat", "gabe", "nächster posten", "nehmen", "auswähl")) or parts & {"CH", "CHEO", "HO", "OT", "Y"}:
        return "SELECT", "item/reference wording/component"
    if any(word in low for word in ("ansatz", "umsetzen", "fortsetzen", "eintragen", "trennen", "waschen", "spülen", "auswringen")) or parts & {"OR", "OK", "K", "CKHE", "LSH"}:
        return "PREPARE", "preparation wording/component"
    return "PREPARE", "default workshop manipulation"


def has_close(value: str, parse: str) -> bool:
    parts = set(parse.replace("WHOLE[", "").replace("]", "").split("+"))
    return bool(parts & {"DY", "LDDY"}) or "schluss" in value.lower() or "schließen" in value.lower()


def main() -> None:
    events = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_381_READABLE_EVENT_ALIGNMENT.tsv")
    statements = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_116_READABLE_WORKSHOP_STATEMENTS.tsv")
    astro = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv")

    phase_rows = []
    for row in events:
        phase, reason = classify(row["compressed_event_de"], row["component_parse"])
        close = has_close(row["compressed_event_de"], row["component_parse"])
        phase_rows.append({
            **row,
            "action_phase": phase,
            "phase_reason": reason,
            "closes_step": "YES" if close else "NO",
            "phase_path": phase + (">CLOSE" if close else ""),
        })
    write("FOUR_HUNDRED_SEVENTY_SIXTH_381_EVENT_PHASES.tsv", phase_rows)

    segments = []
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phase_rows:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    transition_counts: Counter[tuple[str, str, str]] = Counter()
    for record in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = by_record[record]
        current: list[dict[str, str]] = []
        record_segments: list[dict[str, object]] = []

        def flush() -> None:
            nonlocal current
            if not current:
                return
            close = current[-1]["closes_step"] == "YES"
            seg = {
                "segment_id": f"{record}-P{len(record_segments)+1:03d}",
                "record_unit_id": record,
                "register": current[0]["register"],
                "page": current[0]["page"],
                "owner_code": current[0]["owner_code"],
                "phase": current[0]["action_phase"],
                "ends_with_close": "YES" if close else "NO",
                "events": len(current),
                "event_ids": "|".join(row["event_id"] for row in current),
                "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in current)),
                "readable_segment_de": "; ".join(row["compressed_event_de"] for row in current) + ("; Schritt schließen" if close and "schluss" not in current[-1]["compressed_event_de"].lower() else "") + ".",
            }
            record_segments.append(seg)
            segments.append(seg)
            current = []

        for row in rows:
            if current and (row["action_phase"] != current[-1]["action_phase"] or row["owner_reset"] == "YES" or current[-1]["closes_step"] == "YES"):
                flush()
            current.append(row)
            if row["closes_step"] == "YES":
                flush()
        flush()
        chain = [str(row["phase"]) + (">CLOSE" if row["ends_with_close"] == "YES" else "") for row in record_segments]
        for left, right in zip(chain, chain[1:]):
            transition_counts[(rows[0]["register"], left, right)] += 1
        record_rows.append({
            "record_order": len(record_rows) + 1,
            "record_unit_id": record,
            "register": rows[0]["register"],
            "page": rows[0]["page"],
            "events": len(rows),
            "statements": len({row["statement_id"] for row in rows}),
            "phase_segments": len(record_segments),
            "owner_resets": sum(row["owner_reset"] == "YES" for row in rows),
            "phase_chain": ">".join(chain),
            "readable_workflow_de": " ".join(f"[{seg['phase']}] {seg['readable_segment_de']}" for seg in record_segments),
        })
    write("FOUR_HUNDRED_SEVENTY_SIXTH_PROSE_PHASE_SEGMENTS.tsv", segments)
    write("FOUR_HUNDRED_SEVENTY_SIXTH_11_RECORD_PHASE_CHAINS.tsv", record_rows)

    transition_rows = []
    keys = sorted({(left, right) for _, left, right in transition_counts})
    for left, right in keys:
        h = transition_counts[("HERBAL", left, right)]
        b = transition_counts[("BIOLOGICAL", left, right)]
        transition_rows.append({
            "from_phase": left,
            "to_phase": right,
            "herbal_count": h,
            "biological_count": b,
            "shared_across_registers": "YES" if h and b else "NO",
            "total": h + b,
        })
    write("FOUR_HUNDRED_SEVENTY_SIXTH_PHASE_TRANSITIONS.tsv", transition_rows)

    phase_lexicon = []
    for phase, description in PHASES.items():
        phase_lexicon.append({
            "phase": phase,
            "workshop_function_de": description,
            "events_as_action_phase": sum(row["action_phase"] == phase for row in phase_rows),
            "terminal_events": sum(row["action_phase"] == phase and row["closes_step"] == "YES" for row in phase_rows),
            "herbal_events": sum(row["action_phase"] == phase and row["register"] == "HERBAL" for row in phase_rows),
            "biological_events": sum(row["action_phase"] == phase and row["register"] == "BIOLOGICAL" for row in phase_rows),
        })
    write("FOUR_HUNDRED_SEVENTY_SIXTH_PHASE_LEXICON.tsv", phase_lexicon)

    astro_records = []
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro if row["diagram_id"] == unit]
        astro_records.append({
            "record_order": len(record_rows) + len(astro_records) + 1,
            "record_unit_id": unit,
            "register": "ASTRO",
            "page": rows[0]["page"],
            "events": sum(int(row["groups"]) for row in rows),
            "statements": len(rows),
            "phase_segments": len(rows),
            "owner_resets": len(rows),
            "phase_chain": "LOCATE>READ>RECORD repeated independently at each visible locus",
            "readable_workflow_de": " ".join(row["readable_locus_de"] for row in rows),
        })
    units = record_rows + astro_records
    write("FOUR_HUNDRED_SEVENTY_SIXTH_14_PHASED_UNIT_EDITIONS.tsv", units)

    md = ["# Fourteen phased workshop units", ""]
    for unit in units:
        md.extend([f"## {unit['record_unit_id']} — {unit['page']}", "", f"**Phasen:** {unit['phase_chain']}", "", unit["readable_workflow_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_SIXTH_PHASED_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    h_transitions = {(row["from_phase"], row["to_phase"]) for row in transition_rows if int(row["herbal_count"]) > 0}
    b_transitions = {(row["from_phase"], row["to_phase"]) for row in transition_rows if int(row["biological_count"]) > 0}
    summary = {
        "status": "PASS",
        "events": len(phase_rows),
        "phase_segments": len(segments),
        "records": len(record_rows),
        "units": len(units),
        "groups": sum(int(row["events"]) for row in units),
        "phase_counts": {row["phase"]: int(row["events_as_action_phase"]) for row in phase_lexicon},
        "herbal_transition_types": len(h_transitions),
        "biological_transition_types": len(b_transitions),
        "shared_transition_types": len(h_transitions & b_transitions),
        "shared_transition_fraction_of_herbal": round(len(h_transitions & b_transitions) / len(h_transitions), 3),
        "shared_transition_fraction_of_biological": round(len(h_transitions & b_transitions) / len(b_transitions), 3),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
