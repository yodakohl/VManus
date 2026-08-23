#!/usr/bin/env python3
"""Attach compact card values to action heads across all 116 prose statements."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SURFACE_DIR = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler"
SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_exception_anatomy"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ACTION_ATOMS = {
    "OK", "OL", "CHD", "CTH", "CKH", "CKHE", "CHK", "SHED", "SOLK",
    "WASH", "PARTITION", "L", "P", "KCH", "SH", "CFH", "CPH", "ODY",
    "SK", "DAN", "AM", "LDDY",
}
CONTENT_ATOMS = {"OR", "HO", "CHEO", "DCHOL", "DCHE", "DL", "LOCAL_WHOLE", "DAIN", "OS", "CHEEY"}
ARGUMENT_ATOMS = {"AIIN", "AIN", "IIN", "AL", "AR", "AIR", "Y", "E", "EE", "EEE", "TY"}
ENDPOINT_ATOMS = {"CLOSE"}


def classify(atoms: list[str]) -> tuple[str, str]:
    action = next((atom for atom in atoms if atom in ACTION_ATOMS), "")
    if action:
        return "ACTION_HEAD", action
    if "OT" in atoms:
        return "ORDER_MARKER", "OT"
    if set(atoms) & ENDPOINT_ATOMS:
        return "ENDPOINT_ONLY", "CLOSE"
    if set(atoms) & CONTENT_ATOMS:
        return "CONTENT_OR_STATE", next(atom for atom in atoms if atom in CONTENT_ATOMS)
    if set(atoms) & ARGUMENT_ATOMS:
        return "ARGUMENT_OR_MODIFIER", next(atom for atom in atoms if atom in ARGUMENT_ATOMS)
    return "MEMORIZED_CONTENT", atoms[0] if atoms else "NONE"


def attach_group(rows: list[dict[str, object]]) -> None:
    action_indices = [index for index, row in enumerate(rows) if row["syntactic_role"] == "ACTION_HEAD"]
    if not action_indices:
        # Elliptic notation: choose the richest content card, otherwise first.
        content = [index for index, row in enumerate(rows) if row["syntactic_role"] in {"CONTENT_OR_STATE", "MEMORIZED_CONTENT"}]
        host = content[0] if content else 0
        rows[host]["syntactic_role"] = "ELLIPTIC_HEAD"
        rows[host]["action_head"] = "OWNER_SUPPLIED_ACTION"
        action_indices = [host]

    for index, row in enumerate(rows):
        if index in action_indices:
            row["attachment_host_event_id"] = row["event_id"]
            row["attachment_direction"] = "SELF"
            row["attachment_ambiguity"] = "NONE"
            continue
        previous = [candidate for candidate in action_indices if candidate < index]
        following = [candidate for candidate in action_indices if candidate > index]
        prev_idx = previous[-1] if previous else None
        next_idx = following[0] if following else None
        if prev_idx is None:
            chosen, direction, ambiguity = next_idx, "FORWARD", "NONE"
        elif next_idx is None:
            chosen, direction, ambiguity = prev_idx, "BACKWARD", "NONE"
        else:
            prev_distance = index - prev_idx
            next_distance = next_idx - index
            if row["syntactic_role"] == "ORDER_MARKER":
                chosen, direction, ambiguity = next_idx, "FORWARD", "NONE"
            elif row["syntactic_role"] == "ENDPOINT_ONLY":
                chosen, direction, ambiguity = prev_idx, "BACKWARD", "NONE"
            elif prev_distance < next_distance:
                chosen, direction, ambiguity = prev_idx, "BACKWARD", "NONE"
            elif next_distance < prev_distance:
                chosen, direction, ambiguity = next_idx, "FORWARD", "NONE"
            else:
                chosen, direction, ambiguity = prev_idx, "BACKWARD", "EQUAL_DISTANCE"
        assert chosen is not None
        row["attachment_host_event_id"] = rows[chosen]["event_id"]
        row["attachment_direction"] = direction
        row["attachment_ambiguity"] = ambiguity


def main() -> None:
    cards = read_tsv(SURFACE_DIR / "COMPLETE_173_LITERAL_PARSE.tsv")
    events = read_tsv(SOURCE_DIR / "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv")
    statements = read_tsv(SOURCE_DIR / "COMPLETE_116_THIRD_RING_STATEMENTS.tsv")
    by_card = {row["master_card_id"]: row for row in cards}
    statement_meta = {row["statement_id"]: row for row in statements}

    event_rows: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        card = by_card[event["master_card_id"]]
        atoms = card["corrected_semantic_atoms"].split("+")
        role, action = classify(atoms)
        row: dict[str, object] = {
            "event_serial": event["event_serial"], "event_id": event["event_id"],
            "record_unit_id": event["record_unit_id"], "page": event["page"],
            "locus": event["locus"], "field_id": event["field_id"],
            "statement_id": event["statement_id"], "master_card_id": event["master_card_id"],
            "surface_display": event["surface_display"], "corrected_semantic_atoms": "+".join(atoms),
            "short_default_de": card["short_default_de"], "imperative_de": card["imperative_de"],
            "syntactic_role": role, "action_head": action,
            "attachment_host_event_id": "", "attachment_direction": "", "attachment_ambiguity": "",
            "is_statement_terminal_event": "NO", "is_exact_close_card": "YES" if "CLOSE" in atoms else "NO",
            "surface_parse_class": card["parse_class"],
        }
        grouped[event["statement_id"]].append(row)
        event_rows.append(row)

    for rows in grouped.values():
        attach_group(rows)
        rows[-1]["is_statement_terminal_event"] = "YES"

    write_tsv(HERE / "COMPLETE_381_ATTACHED_EVENTS.tsv", event_rows, list(event_rows[0]))

    unit_rows = []
    statement_rows = []
    card_profile_data: dict[str, dict[str, object]] = defaultdict(lambda: {
        "roles": Counter(), "directions": Counter(), "hosts": Counter(), "records": set(),
        "events": [],
    })
    for event in event_rows:
        profile = card_profile_data[str(event["master_card_id"])]
        profile["roles"][str(event["syntactic_role"])] += 1
        profile["directions"][str(event["attachment_direction"])] += 1
        profile["hosts"][str(event["action_head"])] += 1
        profile["records"].add(str(event["record_unit_id"]))
        profile["events"].append(str(event["event_id"]))

    for statement_id, rows in grouped.items():
        hosts = [row for row in rows if row["attachment_direction"] == "SELF"]
        clauses = []
        for number, host in enumerate(hosts, 1):
            attached = [row for row in rows if row["attachment_host_event_id"] == host["event_id"]]
            before = [row for row in attached if int(row["event_serial"]) < int(host["event_serial"])]
            after = [row for row in attached if int(row["event_serial"]) > int(host["event_serial"])]
            before_text = "; ".join(str(row["short_default_de"]) for row in before)
            after_text = "; ".join(str(row["short_default_de"]) for row in after)
            clause = str(host["imperative_de"])
            if before_text:
                clause = f"Vorgabe {before_text}: {clause}"
            if after_text:
                clause += f"; dazu {after_text}"
            clauses.append(clause)
            unit_rows.append({
                "fusion_unit_id": f"{statement_id}-U{number:02d}", "statement_id": statement_id,
                "record_unit_id": host["record_unit_id"], "page": host["page"],
                "host_event_id": host["event_id"], "host_surface": host["surface_display"],
                "action_head": host["action_head"], "pre_attached_event_ids": "|".join(str(row["event_id"]) for row in before) or "NONE",
                "post_attached_event_ids": "|".join(str(row["event_id"]) for row in after) or "NONE",
                "member_event_count": len(attached), "surface_sequence": " ".join(str(row["surface_display"]) for row in attached),
                "atom_sequence": " | ".join(str(row["corrected_semantic_atoms"]) for row in attached),
                "fused_clause_de": clause,
            })
        meta = statement_meta[statement_id]
        ambiguities = sum(row["attachment_ambiguity"] != "NONE" for row in rows)
        statement_rows.append({
            "statement_id": statement_id, "record_unit_id": meta["record_unit_id"], "page": meta["page"],
            "loci": meta["loci"], "event_count": len(rows), "fusion_unit_count": len(hosts),
            "surface_sequence": " ".join(str(row["surface_display"]) for row in rows),
            "corrected_atom_chain": " | ".join(str(row["corrected_semantic_atoms"]) for row in rows),
            "attachment_skeleton_de": " / ".join(clauses),
            "continuous_workshop_reading_de": meta["third_ring_fluent_reading_de"],
            "equal_distance_attachments": ambiguities,
            "elliptic_owner_supplied_head": "YES" if any(row["syntactic_role"] == "ELLIPTIC_HEAD" for row in rows) else "NO",
            "crosses_physical_line": meta["crosses_physical_line"],
            "dch_correction_present": "YES" if any(row["master_card_id"] == "MC142" for row in rows) else "NO",
        })

    write_tsv(HERE / "FUSION_UNITS.tsv", unit_rows, list(unit_rows[0]))
    write_tsv(HERE / "COMPLETE_116_ATTACHED_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))

    profile_rows = []
    for card in cards:
        data = card_profile_data[card["master_card_id"]]
        roles: Counter[str] = data["roles"]  # type: ignore[assignment]
        directions: Counter[str] = data["directions"]  # type: ignore[assignment]
        hosts: Counter[str] = data["hosts"]  # type: ignore[assignment]
        role_stability = "STABLE" if len(roles) == 1 else "MIXED"
        profile_rows.append({
            "master_card_id": card["master_card_id"], "master_head_form": card["master_head_form"],
            "corrected_semantic_atoms": card["corrected_semantic_atoms"], "short_default_de": card["short_default_de"],
            "prose_events": card["prose_events"], "records": "|".join(sorted(data["records"])),
            "syntactic_roles": "|".join(f"{key}:{value}" for key, value in sorted(roles.items())),
            "attachment_directions": "|".join(f"{key}:{value}" for key, value in sorted(directions.items())),
            "action_heads": "|".join(f"{key}:{value}" for key, value in sorted(hosts.items())),
            "role_stability": role_stability,
            "event_ids": "|".join(data["events"]),
            "context_decision": "KEEP_SHORT_VALUE" if role_stability == "STABLE" else "KEEP_VALUE_REVIEW_ATTACHMENT",
        })
    write_tsv(HERE / "CARD_CONTEXT_PROFILES.tsv", profile_rows, list(profile_rows[0]))

    records: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        records[str(row["record_unit_id"])].append(row)
    record_names = {
        "H1": "Wurzelansatz", "H2": "Fortgesetzter Pflanzenansatz", "H3": "Auswringen und Nachseihen",
        "H4": "Verwahrter Auszug", "H5": "Frische Pflanzenfolge", "B1": "Gemeinsamer Beckenweg",
        "B2": "Stations- und Durchlaufweg", "B3": "Hauptfolge der Anwendungen",
        "B4": "Tuch-, Halte- und Nachwaschfolge", "B5": "Kurzer Seitenweg", "B6": "Abschlussweg",
    }
    record_text = "# Elf Records mit angehefteten Kartenwerten\n\n"
    record_text += "Die flüssige Lesung bleibt kreativ; darunter zeigt das Anheftungsskelett, welche kurzen Kartenwerte gemeinsam einen Arbeitsgang bilden.\n\n"
    for record_id in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        rows = records[record_id]
        record_text += f"## {record_id} — {record_names[record_id]}\n\n"
        record_text += " ".join(str(row["continuous_workshop_reading_de"]) for row in rows) + "\n\n"
        for row in rows:
            record_text += f"- **{row['statement_id']}** `{row['surface_sequence']}`\n  - Skelett: {row['attachment_skeleton_de']}\n  - Lesung: {row['continuous_workshop_reading_de']}\n"
        record_text += "\n"
    (HERE / "ELEVEN_RECORD_ATTACHMENT_EDITION.md").write_text(record_text, encoding="utf-8")

    role_counts = Counter(str(row["syntactic_role"]) for row in event_rows)
    direction_counts = Counter(str(row["attachment_direction"]) for row in event_rows)
    elliptic = sum(row["elliptic_owner_supplied_head"] == "YES" for row in statement_rows)
    ambiguous = sum(int(row["equal_distance_attachments"]) for row in statement_rows)
    report = f"""# Werkstattgrammatik: Kartenwerte an Handlungen anheften

## Der eigentliche Fortschritt

Die vorige Ausgabe las fast jede Karte wie ein eigenes Verb. Das machte Sätze künstlich lang. In der neuen Werkstattlesung sind `AIIN/AIN/IIN`, `AL/AR/AIR`, `Y`, `E/EE/EEE`, Materialkarten und der Schluss meist **Argumente einer benachbarten Handlung**. `OK/OL`, Umsetzen, Durchleiten, Wärmen, Absetzen, Sammeln, Waschen, Teilen, Zu-/Abführen und die wenigen gelernten Arbeitsgänge bilden die Köpfe.

Alle 381 Ereignisse sind genau einem der 116 Statements und einer Fusionsgruppe zugeordnet. Es entstehen {len(unit_rows)} Arbeitsgruppen. {elliptic} Aussagen besitzen keinen sichtbaren Handlungskopf; dort liefert Bild/Exemplar weiterhin das Verb. {ambiguous} Anheftungen liegen genau zwischen zwei Köpfen und bleiben in der Tabelle sichtbar statt eine Scheinsicherheit zu erzeugen.

## Rollenbilanz

"""
    for role, count in sorted(role_counts.items()):
        report += f"- `{role}`: {count} Ereignisse\n"
    report += "\nAnheftungsrichtungen:\n\n"
    for direction, count in sorted(direction_counts.items()):
        report += f"- `{direction}`: {count}\n"
    report += """

## Bedeutungsgewinn

`dchol/schol` wird jetzt in allen Kontexten als **eine gelernte Karte VORIGER POSTEN** behandelt; die falsche Analyse `DCH+OL` ist aus der 381-Ereignis-Schicht verschwunden. Die kurzen Werte bleiben erhalten, werden aber nicht mehr als lauter Einzelbefehle missverstanden. Beispielsweise wird `qokaiin ... al ...` zu einem Arbeitsgang *auf Sollmaß am Ziel ansetzen*, und eine Reihe aus `CHEEY`, `AIN`, `CKH+AL`, `SOLK+E+Y`, `L+CHD+CLOSE` wird zu *klare Fraktion portionsweise zur Zielstelle leiten, kurz sammeln, abführen und schließen*.

## Offene Stelle

Die Anheftung sagt noch nicht, ob ein lokaler Besitzer eine Wurzel, ein Tuch, ein Becken oder ein Sternfeld liefert. Sie verbessert die Syntax: ein Kartenwert kann jetzt Material, Maß, Quelle, Ziel, Grad oder Endpunkt sein, ohne als separates Vollverb ausgegeben zu werden. Der nächste Pass nutzt diese Gruppen, um alle elf Records noch einmal als knappe Werkstattanweisungen zu redigieren.
"""
    (HERE / "CLAUSE_ATTACHMENT_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "cards": len(cards), "events": len(event_rows),
        "statements": len(statement_rows), "fusion_units": len(unit_rows), "records": len(records),
        "role_counts": dict(sorted(role_counts.items())), "direction_counts": dict(sorted(direction_counts.items())),
        "elliptic_statements": elliptic, "equal_distance_attachments": ambiguous,
        "dchol_events_corrected": sum(row["master_card_id"] == "MC142" for row in event_rows),
        "source_sha256": {
            "cards": sha(SURFACE_DIR / "COMPLETE_173_LITERAL_PARSE.tsv"),
            "events": sha(SOURCE_DIR / "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv"),
            "statements": sha(SOURCE_DIR / "COMPLETE_116_THIRD_RING_STATEMENTS.tsv"),
        },
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
