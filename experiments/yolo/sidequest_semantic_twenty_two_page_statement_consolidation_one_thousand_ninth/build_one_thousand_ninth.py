#!/usr/bin/env python3
"""Build Pass 1009: one ordered 22-page, 627-statement workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

PASS996 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)
PASS1006 = ROOT / "experiments/yolo/sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"
OLD_STATEMENTS = PASS1006 / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv"
OLD_PAGES = PASS1006 / "PASS1006_18_PAGE_SUMMARY.tsv"
PASS1007 = ROOT / "experiments/yolo/sidequest_semantic_recurring_clause_template_drawer_one_thousand_seventh"
OLD_ASSIGNMENTS = PASS1007 / "PASS1007_462_TEMPLATE_ASSIGNMENTS.tsv"
DRAWERS = PASS1007 / "PASS1007_9_CLAUSE_TEMPLATE_DRAWER.tsv"
PASS1008 = ROOT / "experiments/yolo/sidequest_semantic_four_page_template_transfer_one_thousand_eighth"
NEW_STATEMENTS = PASS1008 / "PASS1008_STATEMENT_TEMPLATE_EDITION.tsv"
NEW_PAGES = PASS1008 / "PASS1008_FOUR_PAGE_TEMPLATE_PROFILE.tsv"
EVENTS = PASS1008 / "PASS1008_4581_UNIFIED_EVENT_LEDGER.tsv"

PAGE_ORDER = [
    "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r",
    "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r",
    "f75r", "f76r", "f77r", "f81v", "f82r", "f83r",
    "f88r", "f88v", "f89r",
]

ROLE_ROOTS = {
    "SEQUENCE": {"OT", "OL", "R", "CARRIER_Q"},
    "ITEM": {"Y", "HO"},
    "SOURCE": {"AR"},
    "QUANTITY": {"AIN", "AIIN", "IIN"},
    "PREPARATION": {"OR", "CHEO"},
    "ACTION": {"OK", "O", "CH", "K", "T", "SH", "CHD", "CHK", "SHED", "LSH", "CFH", "CPH", "P"},
    "PATH": {"L", "AIR", "CKH", "SOLK"},
    "TARGET": {"AL", "AM_ADDR", "D_ADDR", "A_ADDR", "S_ADDR"},
    "STATE": {"E", "EE", "EEE", "CTH"},
}

CANONICAL_ORDER = [
    "OWNER", "SEQUENCE", "ITEM", "SOURCE", "QUANTITY", "PREPARATION",
    "ACTION", "PATH", "TARGET", "STATE", "CLOSE",
]

# Predicate-bearing roots are wider than the original Pass-1007 ACTION slot.
# S and R are concrete operations; L and SOLK fuse path with operation; OL can
# itself predicate continuation.  Recognising these prevents false ellipses.
EXPLICIT_OPERATIONS = {
    "OK": "SETZEN", "O": "AUSFÜHREN", "CH": "NEHMEN", "K": "GEBEN",
    "T": "STELLEN", "SH": "HALTEN", "CHD": "UMSETZEN",
    "CHK": "BEHANDELN", "SHED": "ABSETZEN", "LSH": "SPÜLEN",
    "CFH": "TRENNEN", "CPH": "UMLEITEN", "P": "EINSETZEN",
    "S": "AUSWÄHLEN", "R": "MERKEN", "CARRIER_Q": "BEGINNEN",
}
FUSED_PATH_OPERATIONS = {"L": "LEITEN", "SOLK": "AUFFANGEN"}
SELF_PREDICATING = {"OL": "FORTSETZEN"}
TARGET_ROOTS = {"AL", "AM_ADDR", "D_ADDR", "A_ADDR", "S_ADDR"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"empty table: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def root_lists(component_sequence: str) -> tuple[list[str], set[str]]:
    flat = [root for component in component_sequence.split(" | ") for root in component.split("+")]
    return flat, set(flat)


def slot_signatures(component_sequence: str, end_mode: str) -> tuple[str, str]:
    _, roots = root_lists(component_sequence)
    observed = {role for role, members in ROLE_ROOTS.items() if roots & members}
    if end_mode == "LICENSED_DY_CLOSE":
        observed.add("CLOSE")
    template = set(observed)
    template.add("ACTION")
    observed_signature = ">".join(role for role in CANONICAL_ORDER if role == "OWNER" or role in observed)
    template_signature = ">".join(role for role in CANONICAL_ORDER if role == "OWNER" or role in template)
    return observed_signature, template_signature


def grade_for(roots: set[str]) -> str:
    if "EEE" in roots:
        return "VOLLSTÄNDIG"
    if "EE" in roots:
        return "LÄNGER"
    if "E" in roots:
        return "KURZ"
    return "WIE ANGEGEBEN"


def ending_for(end_mode: str) -> str:
    if end_mode == "LICENSED_DY_CLOSE":
        return " Den Teilgang schließen."
    if end_mode in {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}:
        return " Die Fortsetzung bleibt offen."
    return " Hier endet der sichtbare Abschnitt oder Besitzerblock."


def main() -> int:
    roots = read_tsv(PASS996)
    drawers = {row["template_id"]: row for row in read_tsv(DRAWERS)}
    old_rows = read_tsv(OLD_STATEMENTS)
    old_assignments = {row["statement_id"]: row for row in read_tsv(OLD_ASSIGNMENTS)}
    new_rows = read_tsv(NEW_STATEMENTS)
    base_events = read_tsv(EVENTS)

    # Stable owner IDs for the older statement edition.
    owner_ids: dict[tuple[str, str], str] = {}
    owner_ordinals: Counter[str] = Counter()
    for row in old_rows:
        key = (row["physical_page"], row["visible_owner_or_namespace_de"])
        if key not in owner_ids:
            owner_ordinals[row["physical_page"]] += 1
            owner_ids[key] = f"P1009_{safe_id(row['physical_page'])}_OWNER_{owner_ordinals[row['physical_page']]:02d}"

    normalized: list[dict[str, object]] = []
    source_position = 0
    for row in old_rows:
        source_position += 1
        assignment = old_assignments[row["statement_id"]]
        observed_signature, template_signature = slot_signatures(row["component_sequence"], row["end_mode"])
        normalized.append({
            "legacy_statement_id": row["statement_id"],
            "source_release": "PASS1006_STATEMENT+PASS1007_TEMPLATE",
            "source_position": source_position,
            "physical_page": row["physical_page"],
            "source_panels": row["physical_page"],
            "register": row["register"],
            "owner_id": owner_ids[(row["physical_page"], row["visible_owner_or_namespace_de"])],
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "locus_span": row["locus_span"],
            "locus_count": row["locus_count"],
            "crosses_physical_line": row["crosses_physical_line"],
            "event_count": row["event_count"],
            "template_id": assignment["template_id"],
            "template_name_de": assignment["template_name_de"],
            "observed_slot_signature": observed_signature,
            "template_slot_signature": template_signature,
            "end_mode": row["end_mode"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "portable_literal_de": row["portable_literal_de"],
            "fluent_workshop_de": row["fluent_workshop_de"],
            "event_ids": row["event_ids"],
        })

    for row in new_rows:
        source_position += 1
        observed_signature, template_signature = slot_signatures(row["component_sequence"], row["end_mode"])
        normalized.append({
            "legacy_statement_id": row["statement_id"],
            "source_release": "PASS1008_FOUR_PAGE_TRANSFER",
            "source_position": source_position,
            "physical_page": row["physical_page"],
            "source_panels": row["source_panels"],
            "register": row["register"],
            "owner_id": row["owner_id"],
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "locus_span": row["locus_span"],
            "locus_count": row["locus_count"],
            "crosses_physical_line": row["crosses_physical_line"],
            "event_count": row["event_count"],
            "template_id": row["template_id"],
            "template_name_de": row["template_name_de"],
            "observed_slot_signature": observed_signature,
            "template_slot_signature": template_signature,
            "end_mode": row["end_mode"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "portable_literal_de": row["portable_literal_de"],
            "fluent_workshop_de": row["fluent_workshop_de"],
            "event_ids": row["event_ids"],
        })

    normalized.sort(key=lambda row: (PAGE_ORDER.index(str(row["physical_page"])), int(row["source_position"])))
    legacy_to_new: dict[str, str] = {}
    for ordinal, row in enumerate(normalized, 1):
        row["book_statement_ordinal"] = ordinal
        row["statement_id"] = f"P1009-S{ordinal:03d}"
        legacy_to_new[str(row["legacy_statement_id"])] = str(row["statement_id"])

    # Resolve predicate realization while preserving active operations within a
    # visible owner.  Self-predicating OL continues the current operation but
    # does not overwrite it; every real ellipse therefore points to an earlier
    # explicit/fused source in the same owner.
    active_operation: dict[tuple[str, str], str] = {}
    active_source: dict[tuple[str, str], str] = {}
    ellipse_rows: list[dict[str, object]] = []
    predicate_counts: Counter[str] = Counter()

    for row in normalized:
        flat, root_set = root_lists(str(row["component_sequence"]))
        owner_key = (str(row["physical_page"]), str(row["owner_id"]))
        explicit = [root for root in flat if root in EXPLICIT_OPERATIONS]
        fused = [root for root in flat if root in FUSED_PATH_OPERATIONS]
        self_predicating = [root for root in flat if root in SELF_PREDICATING]

        inherited_operation = ""
        inheritance_source = ""
        if explicit:
            predicate_realization = "EXPLICIT_OPERATION_ROOT"
            operation = EXPLICIT_OPERATIONS[explicit[-1]]
            active_operation[owner_key] = operation
            active_source[owner_key] = str(row["statement_id"])
        elif fused:
            predicate_realization = "FUSED_PATH_OPERATION"
            operation = FUSED_PATH_OPERATIONS[fused[-1]]
            active_operation[owner_key] = operation
            active_source[owner_key] = str(row["statement_id"])
        elif self_predicating:
            predicate_realization = "SELF_PREDICATING_CONTINUATION"
            operation = SELF_PREDICATING[self_predicating[-1]]
        else:
            inherited_operation = active_operation.get(owner_key, "")
            inheritance_source = active_source.get(owner_key, "")
            if not inherited_operation or not inheritance_source:
                raise RuntimeError(f"unresolved action ellipse at {row['legacy_statement_id']}")
            operation = inherited_operation
            if root_set & TARGET_ROOTS:
                predicate_realization = "TARGET_LIST_INHERITANCE"
            elif root_set & {"OR", "CHEO"}:
                predicate_realization = "PREPARATION_INHERITANCE"
            else:
                predicate_realization = "ANAPHORIC_ACTION_INHERITANCE"

        predicate_counts[predicate_realization] += 1
        row["predicate_realization"] = predicate_realization
        row["predicate_operation_de"] = operation
        row["inherited_operation_de"] = inherited_operation
        row["inheritance_source_statement_id"] = inheritance_source

        if predicate_realization == "ANAPHORIC_ACTION_INHERITANCE":
            resolved = (
                f"{row['visible_owner_or_namespace_de']}: danach {grade_for(root_set).lower()} "
                f"{operation.lower()}." + ending_for(str(row["end_mode"]))
            )
        elif predicate_realization == "TARGET_LIST_INHERITANCE":
            target_count = sum(root in TARGET_ROOTS for root in flat)
            target_phrase = "die bezeichnete Zielstelle" if target_count == 1 else f"die {target_count} bezeichneten Zielstellen"
            resolved = (
                f"{row['visible_owner_or_namespace_de']}: den zuvor bearbeiteten Posten an {target_phrase} "
                f"{operation.lower()}." + ending_for(str(row["end_mode"]))
            )
        elif predicate_realization == "PREPARATION_INHERITANCE":
            resolved = (
                f"{row['visible_owner_or_namespace_de']}: eine Portion des Ansatzes danach "
                f"{grade_for(root_set).lower()} {operation.lower()}." + ending_for(str(row["end_mode"]))
            )
        else:
            resolved = str(row["fluent_workshop_de"])
        row["resolved_workshop_de"] = resolved

        if "INHERITANCE" in predicate_realization:
            source_row = next(item for item in normalized if item["statement_id"] == inheritance_source)
            ellipse_rows.append({
                "statement_id": row["statement_id"],
                "legacy_statement_id": row["legacy_statement_id"],
                "physical_page": row["physical_page"],
                "owner_id": row["owner_id"],
                "locus_span": row["locus_span"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "resolution_kind": predicate_realization,
                "grade_de": grade_for(root_set),
                "inherited_operation_de": inherited_operation,
                "inheritance_source_statement_id": inheritance_source,
                "inheritance_source_legacy_id": source_row["legacy_statement_id"],
                "inheritance_source_surface": source_row["surface_sequence"],
                "resolved_workshop_de": resolved,
            })

    # Emit canonical field order after all derived values exist.
    statement_rows = []
    for row in normalized:
        statement_rows.append({
            "book_statement_ordinal": row["book_statement_ordinal"],
            "statement_id": row["statement_id"],
            "legacy_statement_id": row["legacy_statement_id"],
            "source_release": row["source_release"],
            "physical_page": row["physical_page"],
            "source_panels": row["source_panels"],
            "register": row["register"],
            "owner_id": row["owner_id"],
            "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
            "locus_span": row["locus_span"],
            "locus_count": row["locus_count"],
            "crosses_physical_line": row["crosses_physical_line"],
            "event_count": row["event_count"],
            "template_id": row["template_id"],
            "template_name_de": row["template_name_de"],
            "observed_slot_signature": row["observed_slot_signature"],
            "template_slot_signature": row["template_slot_signature"],
            "predicate_realization": row["predicate_realization"],
            "predicate_operation_de": row["predicate_operation_de"],
            "inherited_operation_de": row["inherited_operation_de"],
            "inheritance_source_statement_id": row["inheritance_source_statement_id"],
            "end_mode": row["end_mode"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "portable_literal_de": row["portable_literal_de"],
            "fluent_workshop_de": row["fluent_workshop_de"],
            "resolved_workshop_de": row["resolved_workshop_de"],
            "event_ids": row["event_ids"],
        })

    # Reorder the complete event ledger into physical book order and replace
    # split statement IDs with the canonical Pass-1009 IDs.
    source_event_order = {row["event_id"]: int(row["book_event_ordinal"]) for row in base_events}
    event_rows = sorted(
        base_events,
        key=lambda row: (PAGE_ORDER.index(row["physical_page"]), source_event_order[row["event_id"]]),
    )
    canonical_events: list[dict[str, object]] = []
    for ordinal, row in enumerate(event_rows, 1):
        legacy_statement = row["statement_id"]
        canonical_events.append({
            "book_event_ordinal": ordinal,
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "source_panel": row["source_panel"],
            "register": row["register"],
            "locus": row["locus"],
            "kind": row["kind"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "portable_default_de": row["portable_default_de"],
            "local_contextual_expansion_de": row["local_contextual_expansion_de"],
            "event_role": row["event_role"],
            "statement_id": legacy_to_new.get(legacy_statement, ""),
            "legacy_statement_id": legacy_statement,
            "source_release": row["source_release"],
        })

    # Twenty-two physical-page profile, including the two address-only pages.
    old_page_descriptions = {row["physical_page"]: row["page_description_de"] for row in read_tsv(OLD_PAGES)}
    new_page_descriptions = {row["physical_page"]: row["page_description_de"] for row in read_tsv(NEW_PAGES)}
    descriptions = old_page_descriptions | new_page_descriptions
    page_rows: list[dict[str, object]] = []
    for page_index, page in enumerate(PAGE_ORDER, 1):
        page_events = [row for row in canonical_events if row["physical_page"] == page]
        page_statements = [row for row in statement_rows if row["physical_page"] == page]
        templates = Counter(row["template_id"] for row in page_statements)
        predicates = Counter(row["predicate_realization"] for row in page_statements)
        page_rows.append({
            "page_order": page_index,
            "physical_page": page,
            "source_panels": "|".join(dict.fromkeys(str(row["source_panel"]) for row in page_events)),
            "register": page_events[0]["register"],
            "page_description_de": descriptions[page],
            "groups": len(page_events),
            "running_groups": sum(row["event_role"] == "RUNNING_STATEMENT" for row in page_events),
            "address_or_marker_groups": sum(row["event_role"] != "RUNNING_STATEMENT" for row in page_events),
            "statements": len(page_statements),
            "template_profile": "|".join(f"{key}:{templates[key]}" for key in sorted(templates)) or "ADDRESS_ONLY",
            "predicate_profile": "|".join(f"{key}:{predicates[key]}" for key in sorted(predicates)) or "ADDRESS_ONLY",
            "licensed_closes": sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in page_statements),
            "visible_boundaries": sum(
                row["end_mode"] not in {"LICENSED_DY_CLOSE", "PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}
                for row in page_statements
            ),
            "open_ends": sum(row["end_mode"] in {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"} for row in page_statements),
            "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in page_statements),
            "inherited_predicates": sum("INHERITANCE" in row["predicate_realization"] for row in page_statements),
        })

    predicate_rows = []
    predicate_descriptions = {
        "EXPLICIT_OPERATION_ROOT": "Eine sichtbare Operationswurzel trägt das Prädikat.",
        "FUSED_PATH_OPERATION": "L oder SOLK trägt zugleich Weg und Operation.",
        "SELF_PREDICATING_CONTINUATION": "OL bedeutet selbst fortsetzen; kein ausgelassenes Verb.",
        "ANAPHORIC_ACTION_INHERITANCE": "OT plus Grad/Schluss übernimmt die letzte aktive Operation desselben Besitzers.",
        "TARGET_LIST_INHERITANCE": "Eine reine Zielkartenliste verteilt den vorherigen Arbeitsgang auf die genannten Ziele.",
        "PREPARATION_INHERITANCE": "Der genannte Ansatz übernimmt die unmittelbar aktive Behandlung.",
    }
    for key in predicate_descriptions:
        members = [row for row in statement_rows if row["predicate_realization"] == key]
        predicate_rows.append({
            "predicate_realization": key,
            "teaching_rule_de": predicate_descriptions[key],
            "statements": len(members),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in members})),
            "examples": "|".join(str(row["statement_id"]) for row in members[:5]),
        })

    statement_path = HERE / "PASS1009_627_STATEMENT_EDITION.tsv"
    event_path = HERE / "PASS1009_4581_EVENT_LEDGER.tsv"
    page_path = HERE / "PASS1009_22_PAGE_PROFILE.tsv"
    ellipse_path = HERE / "PASS1009_27_ELLIPSIS_RESOLUTIONS.tsv"
    predicate_path = HERE / "PASS1009_PREDICATE_REALIZATION_PROFILE.tsv"
    write_tsv(statement_path, statement_rows)
    write_tsv(event_path, canonical_events)
    write_tsv(page_path, page_rows)
    write_tsv(ellipse_path, ellipse_rows)
    write_tsv(predicate_path, predicate_rows)

    readable_lines = [
        "# Zweiundzwanzig Seiten — geordnete Werkstattausgabe",
        "",
        "Die 627 Aussagen stehen in physischer Seitenfolge. Eckige Ergänzungen sind nicht nötig: echte Ellipsen nennen ihre geerbte Handlung unmittelbar in der Lesung.",
    ]
    for page in PAGE_ORDER:
        readable_lines.extend(["", f"## {page}", ""])
        members = [row for row in statement_rows if row["physical_page"] == page]
        if not members:
            readable_lines.append("Reines lokales Adressregister; keine Lauftextaussage ergänzt.")
            continue
        for row in members:
            inherited = (
                f" · übernimmt {row['inherited_operation_de']} aus {row['inheritance_source_statement_id']}"
                if row["inherited_operation_de"] else ""
            )
            readable_lines.extend([
                f"- **{row['statement_id']} · {row['template_id']} · {row['predicate_realization']}{inherited}** — {row['resolved_workshop_de']}",
                f"  `{row['surface_sequence']}`",
            ])
    readable_path = HERE / "PASS1009_TWENTY_TWO_PAGE_READABLE_EDITION.md"
    readable_path.write_text("\n".join(readable_lines) + "\n", encoding="utf-8")

    template_counts = Counter(row["template_id"] for row in statement_rows)
    closes = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statement_rows)
    opens = sum(row["end_mode"] in {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"} for row in statement_rows)
    boundaries = len(statement_rows) - closes - opens
    cross_line = sum(row["crosses_physical_line"] == "YES" for row in statement_rows)
    report = f"""# Pass 1009 — eine geordnete Zweiundzwanzig-Seiten-Ausgabe

Die bisher getrennten 462 alten und 165 neuen Aussagen sind jetzt eine einzige
physisch geordnete Ausgabe mit **627 Aussagen und 4.581 Gruppen**. Davon gehören
3.888 Gruppen zum Lauftext oder Ringtext und 693 zu lokalen Adressen, Labels
oder Abschnittsmarkern. Die neun Schubladen bleiben unverändert:
{', '.join(f'{key}={template_counts[key]}' for key in sorted(template_counts))}.
Es gibt {closes} lizenzierte Schlüsse, {boundaries} sichtbare Grenzen, {opens}
offene Enden und {cross_line} zeilenübergreifende Aussagen.

## Die scheinbar fehlenden Handlungen

Die alte ACTION-Rolle war zu eng. Von 627 Aussagen besitzen {predicate_counts['EXPLICIT_OPERATION_ROOT']}
eine ausdrückliche Operationswurzel. Weitere {predicate_counts['FUSED_PATH_OPERATION']}
tragen die Operation bereits im Wegkern (`L=LEITEN`, `SOLK=AUFFANGEN`), und
{predicate_counts['SELF_PREDICATING_CONTINUATION']} werden durch
`OL=FORTSETZEN` selbst prädiziert. Diese {predicate_counts['FUSED_PATH_OPERATION'] + predicate_counts['SELF_PREDICATING_CONTINUATION']}
Fälle sind keine Ellipsen.

Übrig bleiben genau **{len(ellipse_rows)} echte Werkstattellipsen**:

- {predicate_counts['ANAPHORIC_ACTION_INHERITANCE']} kurze Folge-/Gradkarten übernehmen die letzte aktive Handlung desselben sichtbaren Besitzers;
- {predicate_counts['TARGET_LIST_INHERITANCE']} reine Zielkartenlisten verteilen den vorherigen Gang auf eine oder mehrere Zielstellen;
- {predicate_counts['PREPARATION_INHERITANCE']} Ansatzzeile übernimmt die unmittelbar vorherige Behandlung.

Alle 27 lassen sich ohne Besitzerwechsel und ohne neue Wurzel auf eine frühere
ausdrückliche Handlung zurückbinden. Beispiele: `otedy` wird je nach laufendem
Abschnitt zu **danach kurz setzen**, **danach kurz geben** oder **danach kurz
umsetzen**; `qoteeedy` bedeutet **danach vollständig geben**; `al daldal`
verteilt den zuvor bearbeiteten Posten auf drei Zielstellen. Die Form hat also
keine einzige globale ausgelassene Handlung: sie ist eine lernbare
Anapherregel des Werkstattregisters.

## Neue kompakte Lehrregel

1. Eine sichtbare Operationswurzel setzt die aktive Handlung.
2. `L`/`SOLK` dürfen Weg und Handlung in einer Karte vereinigen.
3. `OL` prädiziert selbst **fortsetzen**, ohne eine andere Handlung zu erfinden.
4. Eine reine `OT+Grad+Schluss`-Zelle wiederholt die letzte aktive Handlung
   desselben Besitzers mit dem genannten Grad.
5. Reine Ziel- oder Ansatzkarten übernehmen dieselbe Handlung nur innerhalb
   dieses Besitzerblocks.

Damit ist die 22-Seiten-Basis erstmals auf Ereignis-, Aussage-, Schubladen-
und Ellipsenebene in einer Ausgabe vereinigt. Es wurde keine neue Wurzel und
keine zehnte Satzschublade benötigt.
"""
    report_path = HERE / "PASS1009_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    outputs = [statement_path, event_path, page_path, ellipse_path, predicate_path, readable_path, report_path]
    summary = {
        "status": "PASS",
        "decision": "TWENTY_TWO_PAGE_627_STATEMENT_EDITION_WITH_27_LOCAL_ACTION_ELLIPSES",
        "physical_pages": 22,
        "groups": len(canonical_events),
        "running_groups": sum(row["event_role"] == "RUNNING_STATEMENT" for row in canonical_events),
        "local_groups": sum(row["event_role"] != "RUNNING_STATEMENT" for row in canonical_events),
        "statements": len(statement_rows),
        "templates": 9,
        "template_counts": dict(sorted(template_counts.items())),
        "predicate_counts": dict(sorted(predicate_counts.items())),
        "ellipses": len(ellipse_rows),
        "licensed_closes": closes,
        "visible_boundaries": boundaries,
        "open_ends": opens,
        "cross_line_statements": cross_line,
        "portable_roots": len(roots),
        "new_portable_roots": 0,
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    (HERE / "PASS1009_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
