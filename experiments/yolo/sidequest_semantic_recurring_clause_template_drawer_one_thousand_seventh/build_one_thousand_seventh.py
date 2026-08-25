#!/usr/bin/env python3
"""Build Pass 1007: a compact clause-template drawer for the Pass-1006 edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


HERE = Path(__file__).resolve().parent
PASS1006 = HERE.parent / "sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"
STATEMENTS = PASS1006 / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv"
PAGE_SUMMARY = PASS1006 / "PASS1006_18_PAGE_SUMMARY.tsv"


ROLE_ROOTS = {
    "SEQUENCE": {"OT", "OL", "R", "CARRIER_Q"},
    "ITEM": {"Y", "HO"},
    "SOURCE": {"AR"},
    "QUANTITY": {"AIN", "AIIN", "IIN"},
    "PREPARATION": {"OR", "CHEO"},
    "ACTION": {
        "OK", "O", "CH", "K", "T", "SH", "CHD", "CHK", "SHED",
        "LSH", "CFH", "CPH", "P",
    },
    "PATH": {"L", "AIR", "CKH", "SOLK"},
    "TARGET": {"AL", "AM_ADDR", "D_ADDR", "A_ADDR", "S_ADDR"},
    "STATE": {"E", "EE", "EEE", "CTH"},
}

CANONICAL_ORDER = [
    "OWNER", "SEQUENCE", "ITEM", "SOURCE", "QUANTITY", "PREPARATION",
    "ACTION", "PATH", "TARGET", "STATE", "CLOSE",
]

# Used only to make a short observed trace. Multi-role evidence is retained in
# event_role_trace and is never discarded from the output.
PRIMARY_PRIORITY = [
    "CLOSE", "SEQUENCE", "TARGET", "PATH", "STATE", "QUANTITY", "SOURCE",
    "PREPARATION", "ACTION", "ITEM", "LOCAL_SIGN",
]

TEMPLATES = {
    "T01": {
        "name": "EINFACHER ARBEITSGANG",
        "pattern": "BESITZER → HANDLUNG → [ZUSTAND] → ENDE",
        "trigger": "Kein eigener Posten-, Folge-, Mengen-, Ansatz-, Weg- oder Zielslot.",
        "required": "OWNER|ACTION",
        "optional": "STATE|END",
        "target_length": 2,
        "example_id": "P1006-S203",
    },
    "T02": {
        "name": "POSTEN BEARBEITEN",
        "pattern": "BESITZER → POSTEN → HANDLUNG → [ZUSTAND] → ENDE",
        "trigger": "Ein ausdrücklicher laufender Posten, aber keine höher priorisierte Adresszone.",
        "required": "OWNER|ITEM|ACTION",
        "optional": "STATE|END",
        "target_length": 3,
        "example_id": "P1006-S161",
    },
    "T03": {
        "name": "FORTSETZUNG ODER FOLGESCHRITT",
        "pattern": "BESITZER → DANACH/FORTSETZEN → [POSTEN] → HANDLUNG → [ZUSTAND] → ENDE",
        "trigger": "Folge- oder Fortsetzungskarte ohne Mengen-, Ansatz-, Weg- oder Zielkern.",
        "required": "OWNER|SEQUENCE|ACTION",
        "optional": "ITEM|STATE|END",
        "target_length": 4,
        "example_id": "P1006-S160",
    },
    "T04": {
        "name": "ABGEMESSENER ARBEITSGANG",
        "pattern": "BESITZER → [POSTEN] → MENGE/STUFE → HANDLUNG → [ZUSTAND] → ENDE",
        "trigger": "Mengen- oder Stufenslot ohne eigenen Ansatz-, Weg- oder Zielkern.",
        "required": "OWNER|QUANTITY|ACTION",
        "optional": "ITEM|SEQUENCE|STATE|END",
        "target_length": 4,
        "example_id": "P1006-S159",
    },
    "T05": {
        "name": "ANSATZ BILDEN ODER WEITERFÜHREN",
        "pattern": "BESITZER → [POSTEN/MENGE] → ANSATZ → HANDLUNG → [ZUSTAND] → ENDE",
        "trigger": "Ausdrücklicher Ansatz- oder Auszugsslot ohne eigenen Weg oder Zielslot.",
        "required": "OWNER|PREPARATION|ACTION",
        "optional": "SEQUENCE|ITEM|SOURCE|QUANTITY|STATE|END",
        "target_length": 5,
        "example_id": "P1006-S009",
    },
    "T06": {
        "name": "AN ZIELSTELLE AUSFÜHREN",
        "pattern": "BESITZER → [FOLGE/POSTEN/MENGE] → HANDLUNG → ZIEL → [ZUSTAND] → ENDE",
        "trigger": "Zielslot vorhanden, aber kein eigener Leitweg und keine Vollkette.",
        "required": "OWNER|ACTION|TARGET",
        "optional": "SEQUENCE|ITEM|SOURCE|QUANTITY|PREPARATION|STATE|END",
        "target_length": 5,
        "example_id": "P1006-S008",
    },
    "T07": {
        "name": "ÜBER EINEN WEG FÜHREN",
        "pattern": "BESITZER → [QUELLE/POSTEN] → HANDLUNG → WEG → [ZIEL/ZUSTAND] → ENDE",
        "trigger": "Leitweg, Lauf, Durchlass oder Auffangweg vorhanden; keine Vollkette.",
        "required": "OWNER|ACTION|PATH",
        "optional": "SEQUENCE|ITEM|SOURCE|QUANTITY|PREPARATION|TARGET|STATE|END",
        "target_length": 6,
        "example_id": "P1006-S018",
    },
    "T08": {
        "name": "VOLLSTÄNDIGE MEHRSCHRITTKETTE",
        "pattern": "BESITZER → [FOLGE] → [POSTEN/QUELLE/MENGE/ANSATZ] → HANDLUNG+ → [WEG/ZIEL/ZUSTAND] → ENDE",
        "trigger": "Mindestens neun Karten oder mindestens acht belegte Arbeitszonen.",
        "required": "OWNER|ACTION",
        "optional": "SEQUENCE|ITEM|SOURCE|QUANTITY|PREPARATION|PATH|TARGET|STATE|END",
        "target_length": 10,
        "example_id": "P1006-S265",
    },
    "T09": {
        "name": "HIMMELSEINTRAG SETZEN ODER PRÜFEN",
        "pattern": "RING/PANEL → [FOLGE] → ADRESSE/WERT → SETZEN/PRÜFEN → [GRAD] → ENDE",
        "trigger": "Lauftext innerhalb eines Himmelsregisters; lokale Ringlabels bleiben außerhalb.",
        "required": "OWNER|ACTION",
        "optional": "SEQUENCE|ITEM|SOURCE|QUANTITY|PREPARATION|PATH|TARGET|STATE|END",
        "target_length": 5,
        "example_id": "P1006-S026",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def event_roots(component: str) -> set[str]:
    return set(component.split("+"))


def event_roles(component: str, is_final_close: bool) -> list[str]:
    roots = event_roots(component)
    roles = [role for role, members in ROLE_ROOTS.items() if roots & members]
    if is_final_close:
        roles.append("CLOSE")
    return roles or ["LOCAL_SIGN"]


def statement_slots(row: dict[str, str]) -> tuple[set[str], set[str]]:
    roots = {
        root
        for component in row["component_sequence"].split(" | ")
        for root in event_roots(component)
    }
    slots = {role for role, members in ROLE_ROOTS.items() if roots & members}
    if row["end_mode"] == "LICENSED_DY_CLOSE":
        slots.add("CLOSE")
    return roots, slots


def choose_template(row: dict[str, str], slots: set[str]) -> str:
    working_slots = slots - {"CLOSE"}
    if row["register"] == "CELESTIAL":
        return "T09"
    if int(row["event_count"]) >= 9 or len(working_slots) >= 8:
        return "T08"
    if "PATH" in working_slots:
        return "T07"
    if "TARGET" in working_slots:
        return "T06"
    if "PREPARATION" in working_slots:
        return "T05"
    if "QUANTITY" in working_slots:
        return "T04"
    if "SEQUENCE" in working_slots:
        return "T03"
    if "ITEM" in working_slots:
        return "T02"
    return "T01"


def end_style(end_mode: str) -> str:
    if end_mode == "LICENSED_DY_CLOSE":
        return "CLOSE"
    if end_mode in {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}:
        return "OPEN"
    return "VISIBLE_BOUNDARY"


def collapse(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


def main() -> None:
    rows = read_tsv(STATEMENTS)
    pages = read_tsv(PAGE_SUMMARY)
    assignments: list[dict[str, object]] = []
    by_template: dict[str, list[dict[str, str]]] = defaultdict(list)
    exact_signatures: Counter[str] = Counter()

    for row in rows:
        roots, slots = statement_slots(row)
        template_id = choose_template(row, slots)
        by_template[template_id].append(row)
        signature = ">".join(role for role in CANONICAL_ORDER if role == "OWNER" or role in slots)
        exact_signatures[signature] += 1

        components = row["component_sequence"].split(" | ")
        role_groups: list[list[str]] = []
        primaries: list[str] = []
        for index, component in enumerate(components):
            is_close = row["end_mode"] == "LICENSED_DY_CLOSE" and index == len(components) - 1
            roles = event_roles(component, is_close)
            role_groups.append(roles)
            primaries.append(next(role for role in PRIMARY_PRIORITY if role in roles))

        style = end_style(row["end_mode"])
        assignments.append({
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "locus_span": row["locus_span"],
            "event_count": row["event_count"],
            "template_id": template_id,
            "template_name_de": TEMPLATES[template_id]["name"],
            "template_pattern_de": TEMPLATES[template_id]["pattern"],
            "canonical_slot_signature": signature,
            "event_role_trace": " | ".join("+".join(group) for group in role_groups),
            "observed_primary_trace": ">".join(collapse(primaries)),
            "end_style": style,
            "crosses_physical_line": row["crosses_physical_line"],
            "surface_sequence": row["surface_sequence"],
            "fluent_workshop_de": row["fluent_workshop_de"],
            "event_ids": row["event_ids"],
        })

    template_rows: list[dict[str, object]] = []
    for template_id in sorted(TEMPLATES):
        definition = TEMPLATES[template_id]
        members = by_template[template_id]
        example = next(row for row in members if row["statement_id"] == definition["example_id"])
        styles = Counter(end_style(row["end_mode"]) for row in members)
        template_rows.append({
            "template_id": template_id,
            "template_name_de": definition["name"],
            "apprentice_pattern_de": definition["pattern"],
            "trigger_rule_de": definition["trigger"],
            "required_slots": definition["required"],
            "optional_slots": definition["optional"],
            "statement_count": len(members),
            "event_count": sum(int(row["event_count"]) for row in members),
            "median_statement_events": f"{median(int(row['event_count']) for row in members):g}",
            "registers": "|".join(sorted({row["register"] for row in members})),
            "pages": "|".join(sorted({row["physical_page"] for row in members})),
            "licensed_close_count": styles["CLOSE"],
            "visible_boundary_count": styles["VISIBLE_BOUNDARY"],
            "open_count": styles["OPEN"],
            "cross_line_count": sum(row["crosses_physical_line"] == "YES" for row in members),
            "example_statement_id": example["statement_id"],
            "example_surface": example["surface_sequence"],
            "example_reading_de": example["fluent_workshop_de"],
        })

    assignment_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in assignments:
        assignment_by_page[str(row["physical_page"])].append(row)

    profile_rows: list[dict[str, object]] = []
    for page in pages:
        members = assignment_by_page[page["physical_page"]]
        counts = Counter(str(row["template_id"]) for row in members)
        dominant = counts.most_common(1)[0][0] if counts else "ADDRESS_ONLY"
        profile_rows.append({
            "page_order": page["page_order"],
            "physical_page": page["physical_page"],
            "register": page["register"],
            "page_description_de": page["page_description_de"],
            "groups": page["total_groups"],
            "running_groups": page["running_groups"],
            "address_or_label_groups": page["address_or_label_groups"],
            "statements": len(members),
            "template_profile": "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "ADDRESS_ONLY",
            "dominant_template": dominant,
            "licensed_closes": sum(row["end_style"] == "CLOSE" for row in members),
            "visible_boundaries": sum(row["end_style"] == "VISIBLE_BOUNDARY" for row in members),
            "open_ends": sum(row["end_style"] == "OPEN" for row in members),
            "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in members),
        })

    drawer_path = HERE / "PASS1007_9_CLAUSE_TEMPLATE_DRAWER.tsv"
    assignment_path = HERE / "PASS1007_462_TEMPLATE_ASSIGNMENTS.tsv"
    profile_path = HERE / "PASS1007_18_PAGE_TEMPLATE_PROFILE.tsv"
    manual_path = HERE / "PASS1007_APPRENTICE_CLAUSE_MANUAL.md"
    report_path = HERE / "PASS1007_REPORT.md"

    write_tsv(drawer_path, list(template_rows[0]), template_rows)
    write_tsv(assignment_path, list(assignments[0]), assignments)
    write_tsv(profile_path, list(profile_rows[0]), profile_rows)

    manual_lines = [
        "# Lehrlingshandbuch: neun Satzschubladen",
        "",
        "Der Lehrling lernt keine 462 Einzelsätze. Er wählt eine von neun Schubladen und füllt nur deren sichtbare Plätze.",
        "",
        "1. Zuerst den Bild-, Gefäß-, Stations- oder Ringbesitzer setzen.",
        "2. Lokale Namen und die 550 Bild-/Ringadressen separat aus dem Exemplar kopieren.",
        "3. Die Karten links nach rechts lesen, aber gleichartige Karten in Arbeitszonen bündeln.",
        "4. Die passendste Schublade nach dieser Reihenfolge wählen: Himmel → Vollkette → Weg → Ziel → Ansatz → Menge → Folge → Posten → einfacher Gang.",
        "5. Eckige Plätze sind optional. Ihre Reihenfolge darf innerhalb der Adress- und Ausführungszone wechseln.",
        "6. ENDE ist ein eigener Schalter: lizenzierte Schlusskarte, sichtbarer Besitzerwechsel oder offen gelassener Fortgang.",
        "7. Eine physische Zeile beendet die Schublade nicht; 160 Aussagen laufen über Zeilen hinweg.",
        "8. Eine lokale Bildfüllung konkretisiert Posten, Ansatz, Weg oder Ziel, verändert aber nicht die 53 Wurzeln.",
        "",
        "## Die Schubladen",
        "",
    ]
    for row in template_rows:
        manual_lines.extend([
            f"- **{row['template_id']} {row['template_name_de']}** — `{row['apprentice_pattern_de']}` "
            f"({row['statement_count']} Aussagen).",
        ])
    manual_lines.extend([
        "",
        "## Schreibprobe",
        "",
        "Für einen neuen Eintrag sagt der Meister zuerst den Besitzer, dann die benötigten Plätze. Der Lehrling wählt die Schublade, setzt die bekannten Karten und kopiert nur unbekannte Eigennamen aus dem Exemplar. Fehlt am Ende eine lizenzierte Schlusskarte, bleibt der Gang offen oder endet am sichtbaren Besitzerwechsel.",
    ])
    manual_path.write_text("\n".join(manual_lines) + "\n", encoding="utf-8")

    report_lines = [
        "# Pass 1007 — neun wiederkehrende Satzschubladen",
        "",
        f"Die 462 Aussagen zeigen {len(exact_signatures)} verschiedene exakte Slotkombinationen, brauchen aber keine {len(exact_signatures)} Satztypen. Als Lehrsystem reichen neun flexible Schubladen. Jede Aussage ist genau einer Schublade zugeordnet; zusammen decken sie alle 2.618 laufenden Gruppen.",
        "",
        "Die häufigsten Arbeitsformen sind Wegführung, einfacher Arbeitsgang, Vollkette und Zielanwendung. Das Ende bleibt unabhängig von der Schublade: 432 lizenzierte Schlüsse, 20 sichtbare Besitzer-/Diagrammgrenzen und 10 wirklich offene Enden. Die 550 lokalen Adressen bleiben außerhalb der Satzgrammatik.",
        "",
        "| Schublade | Kurzregel | Aussagen | Gruppen |",
        "|---|---|---:|---:|",
    ]
    for row in template_rows:
        report_lines.append(
            f"| {row['template_id']} {row['template_name_de']} | {row['apprentice_pattern_de']} | {row['statement_count']} | {row['event_count']} |"
        )
    report_lines.extend([
        "",
        "## Wichtigste Verbesserung",
        "",
        "Die alte Lesung wechselte zu schnell zwischen Einzelkarten und langen freien Paraphrasen. Die neue Fassung hält dazwischen eine stabile Satzebene: Besitzer, Adresszone, Ausführungszone und Ende. Ein Schreiber kann damit neue Kartenfolgen bauen, ohne für jede Folge ein neues Ganzwort oder eine neue Satzregel zu lernen.",
        "",
        "f69v und f70v bleiben reine lokale Adressregister. Sie erhalten absichtlich keine Satzschublade. Die nächste Seitengruppe kann nun gegen diese neun Werkstattmuster gelesen werden.",
    ])
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    outputs = [drawer_path, assignment_path, profile_path, manual_path, report_path]
    summary = {
        "status": "PASS",
        "decision": "NINE_RECURRING_CLAUSE_TEMPLATES_COVER_ALL_RUNNING_TEXT",
        "templates": len(template_rows),
        "statements": len(assignments),
        "running_groups": sum(int(row["event_count"]) for row in rows),
        "exact_slot_signatures": len(exact_signatures),
        "licensed_closes": sum(row["end_style"] == "CLOSE" for row in assignments),
        "visible_boundaries": sum(row["end_style"] == "VISIBLE_BOUNDARY" for row in assignments),
        "open_ends": sum(row["end_style"] == "OPEN" for row in assignments),
        "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in assignments),
        "address_or_label_groups_outside_grammar": sum(int(row["address_or_label_groups"]) for row in pages),
        "new_roots": 0,
        "template_statement_counts": {row["template_id"]: row["statement_count"] for row in template_rows},
        "source_hash": sha256(STATEMENTS),
        "output_hashes": {path.name: sha256(path) for path in outputs},
    }
    (HERE / "PASS1007_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
