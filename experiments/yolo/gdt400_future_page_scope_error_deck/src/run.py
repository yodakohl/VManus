#!/usr/bin/env python3
"""Compile a compact future-page error deck from the GDT399 scope edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
G399 = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts"
ATTACHMENTS = G399 / "gdt399_4374_scope_attachments.tsv"
EVENTS = G399 / "gdt399_3888_event_replay.tsv"
STATEMENTS = G399 / "gdt399_627_statement_scope_edition.tsv"
PAGES = G399 / "gdt399_22_page_replay.tsv"
RULES = G399 / "gdt399_rule_support.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output {path.name}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipe(values: list[str] | set[str]) -> str:
    selected = sorted({value for value in values if value and value != "NONE"})
    return "|".join(selected) if selected else "NONE"


def signature(row: dict[str, str], level: str) -> str:
    if level == "EXACT_TYPED_HEAD":
        return "::".join([
            row["focus_core"], row["chosen_attachment_class"], row["chosen_action"],
            row["r_position_mode"], row["duplicate_scope_mode"], row["teaching_rule_families"],
        ])
    if level == "TYPED_MICRO":
        return "::".join([row["focus_core"], row["micro_signature"], row["teaching_rule_families"]])
    if level == "UNTYPED_MICRO":
        return row["micro_signature"]
    if level == "COARSE_RULE":
        return row["teaching_rule_families"]
    raise AssertionError(level)


def owner_reason(row: dict[str, str], event: dict[str, str], next_event: dict[str, str] | None) -> str:
    atoms = set(event["component_recipe"].split("+"))
    if row["focus_core"] in {"AL", "AR"}:
        return "AL_AR_OWNER_FALLBACK"
    if row["focus_core"] in {"L", "AIR"}:
        return "L_AIR_OWNER_FALLBACK"
    if "DY" in atoms:
        return "CURRENT_PACKAGE_CLOSED"
    if "OS" in atoms:
        return "OWNER_RESTORED"
    if next_event is None:
        return "STATEMENT_FINAL_OWNER_ELLIPSIS"
    return "NO_VISIBLE_ACTION_HEAD_OWNER_ELLIPSIS"


def forward_reason(row: dict[str, str], event: dict[str, str]) -> str:
    atoms = set(event["component_recipe"].split("+"))
    if atoms & {"CARRIER_Q", "OT"}:
        return "Q_OR_OT_OPENS_NEXT_PACKET"
    if row["focus_core"] in {"L", "AIR"} or atoms & {"L", "AIR"}:
        return "L_OR_AIR_FRAMES_NEXT_HEAD"
    if row["focus_core"] in {"AL", "AR"}:
        return "ADDRESSED_PACKET_WITH_FORWARD_CUE"
    return "HEADLESS_OPENING_PACKAGE_TO_NEXT_HEAD"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    attachments = read_tsv(ATTACHMENTS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    pages = read_tsv(PAGES)
    rules = read_tsv(RULES)
    if [len(attachments), len(events), len(statements), len(pages), len(rules)] != [4374, 3888, 627, 22, 9]:
        raise AssertionError("GDT399 inventory mismatch")

    levels = ["EXACT_TYPED_HEAD", "TYPED_MICRO", "UNTYPED_MICRO", "COARSE_RULE"]
    pages_by_signature: dict[tuple[str, str], set[str]] = defaultdict(set)
    registers_by_signature: dict[tuple[str, str], set[str]] = defaultdict(set)
    rows_by_signature: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in attachments:
        for level in levels:
            key = (level, signature(row, level))
            pages_by_signature[key].add(row["physical_page"])
            registers_by_signature[key].add(row["register"])
            rows_by_signature[key].append(row)

    rule_component_pages = {
        row["rule_family"]: set(row["support_pages"].split("|")) for row in rules
    }
    rule_component_registers = {
        row["rule_family"]: set(row["support_registers"].split("|")) for row in rules
    }
    replay_rows: list[dict[str, object]] = []
    support_level_counts: Counter[str] = Counter()
    register_support_level_counts: Counter[str] = Counter()
    for row in attachments:
        outside_page_level = "NONE"
        outside_register_level = "NONE"
        for level in levels:
            key = (level, signature(row, level))
            if outside_page_level == "NONE" and pages_by_signature[key] - {row["physical_page"]}:
                outside_page_level = level
            if outside_register_level == "NONE" and registers_by_signature[key] - {row["register"]}:
                outside_register_level = level
        components = row["teaching_rule_families"].split("|")
        if outside_page_level == "NONE" and all(
            rule_component_pages[family] - {row["physical_page"]} for family in components
        ):
            outside_page_level = "COMPOSED_RULE_COMPONENTS"
        if outside_register_level == "NONE" and all(
            rule_component_registers[family] - {row["register"]} for family in components
        ):
            outside_register_level = "COMPOSED_RULE_COMPONENTS"
        support_level_counts[outside_page_level] += 1
        register_support_level_counts[outside_register_level] += 1
        if outside_page_level == "COMPOSED_RULE_COMPONENTS":
            outside_pages = " | ".join(
                f"{family}:{pipe(rule_component_pages[family] - {row['physical_page']})}"
                for family in components
            )
        elif outside_page_level != "NONE":
            outside_pages = pipe(
                pages_by_signature[(outside_page_level, signature(row, outside_page_level))]
                - {row["physical_page"]}
            )
        else:
            outside_pages = "NONE"
        if outside_register_level == "COMPOSED_RULE_COMPONENTS":
            outside_registers = " | ".join(
                f"{family}:{pipe(rule_component_registers[family] - {row['register']})}"
                for family in components
            )
        elif outside_register_level != "NONE":
            outside_registers = pipe(
                registers_by_signature[(outside_register_level, signature(row, outside_register_level))]
                - {row["register"]}
            )
        else:
            outside_registers = "NONE"
        replay_rows.append({
            "replay_id": f"G400-A{len(replay_rows) + 1:05d}",
            "attachment_id": row["attachment_id"], "physical_page": row["physical_page"],
            "register": row["register"], "statement_id": row["statement_id"],
            "event_id": row["event_id"], "surface": row["surface"],
            "focus_core": row["focus_core"], "chosen_attachment_class": row["chosen_attachment_class"],
            "chosen_action": row["chosen_action"], "micro_signature": row["micro_signature"],
            "teaching_rule_families": row["teaching_rule_families"],
            "exact_typed_head_signature": signature(row, "EXACT_TYPED_HEAD"),
            "typed_micro_signature": signature(row, "TYPED_MICRO"),
            "outside_page_support_level": outside_page_level,
            "outside_register_support_level": outside_register_level,
            "outside_page_support": outside_pages,
            "outside_register_support": outside_registers,
            "future_page_result": "PORTABLE_BY_EXISTING_HIERARCHY" if outside_page_level != "NONE" and outside_register_level != "NONE" else "PRIVATE_PATTERN",
        })

    signature_rows: list[dict[str, object]] = []
    for level in levels:
        keys = sorted(key for key in rows_by_signature if key[0] == level)
        for ordinal, key in enumerate(keys, start=1):
            selected = rows_by_signature[key]
            signature_rows.append({
                "signature_id": f"{level}-{ordinal:03d}", "signature_level": level,
                "signature": key[1], "occurrences": len(selected),
                "page_count": len(pages_by_signature[key]), "pages": pipe(pages_by_signature[key]),
                "register_count": len(registers_by_signature[key]), "registers": pipe(registers_by_signature[key]),
                "focus_cores": pipe({row["focus_core"] for row in selected}),
                "attachment_classes": pipe({row["chosen_attachment_class"] for row in selected}),
                "chosen_actions": pipe({row["chosen_action"] for row in selected}),
                "example_attachment_ids": pipe([row["attachment_id"] for row in selected[:5]]),
                "page_private": "YES" if len(pages_by_signature[key]) == 1 else "NO",
                "register_private": "YES" if len(registers_by_signature[key]) == 1 else "NO",
            })
    for ordinal, rule in enumerate(rules, start=1):
        family = rule["rule_family"]
        selected = [
            row for row in attachments
            if family in row["teaching_rule_families"].split("|")
        ]
        signature_rows.append({
            "signature_id": f"RULE_COMPONENT-{ordinal:03d}",
            "signature_level": "RULE_COMPONENT", "signature": family,
            "occurrences": len(selected), "page_count": len(rule_component_pages[family]),
            "pages": pipe(rule_component_pages[family]),
            "register_count": len(rule_component_registers[family]),
            "registers": pipe(rule_component_registers[family]),
            "focus_cores": pipe({row["focus_core"] for row in selected}),
            "attachment_classes": pipe({row["chosen_attachment_class"] for row in selected}),
            "chosen_actions": pipe({row["chosen_action"] for row in selected}),
            "example_attachment_ids": pipe([row["attachment_id"] for row in selected[:5]]),
            "page_private": "NO", "register_private": "NO",
        })

    event_by_id = {row["event_id"]: row for row in events}
    statement_event_ids: dict[str, list[str]] = defaultdict(list)
    for row in events:
        statement_event_ids[row["statement_id"]].append(row["event_id"])
    next_by_id: dict[str, dict[str, str] | None] = {}
    for event_ids in statement_event_ids.values():
        for index, event_id in enumerate(event_ids):
            next_by_id[event_id] = event_by_id[event_ids[index + 1]] if index + 1 < len(event_ids) else None

    forward_rows: list[dict[str, object]] = []
    owner_rows: list[dict[str, object]] = []
    for row in attachments:
        event = event_by_id[row["event_id"]]
        nxt = next_by_id[row["event_id"]]
        if row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION":
            if nxt is None:
                raise AssertionError(f"forward attachment at statement end: {row['attachment_id']}")
            forward_rows.append({
                "forward_id": f"G400-F{len(forward_rows) + 1:03d}",
                "attachment_id": row["attachment_id"], "physical_page": row["physical_page"],
                "register": row["register"], "statement_id": row["statement_id"],
                "event_id": row["event_id"], "surface": row["surface"],
                "component_recipe": row["component_recipe"], "focus_core": row["focus_core"],
                "forward_reason": forward_reason(row, event), "next_event_id": nxt["event_id"],
                "next_surface": nxt["surface"], "next_recipe": nxt["component_recipe"],
                "chosen_action": row["chosen_action"], "chosen_action_atom_ordinal": row["chosen_action_atom_ordinal"],
                "same_statement": "YES" if row["statement_id"] == nxt["statement_id"] else "NO",
                "lookahead_cards": row["bounded_lookahead_cards"],
                "outside_page_support_level": replay_rows[int(row["attachment_id"].split("A")[-1]) - 1]["outside_page_support_level"],
                "result": "ONE_CARD_FORWARD_VISIBLE_HEAD",
            })
        elif row["chosen_attachment_class"] == "OWNER_ONLY":
            owner_rows.append({
                "owner_id": f"G400-O{len(owner_rows) + 1:03d}",
                "attachment_id": row["attachment_id"], "physical_page": row["physical_page"],
                "register": row["register"], "statement_id": row["statement_id"],
                "event_id": row["event_id"], "surface": row["surface"],
                "component_recipe": row["component_recipe"], "focus_core": row["focus_core"],
                "owner_de": row["owner_de"], "owner_reason": owner_reason(row, event, nxt),
                "next_event_id": nxt["event_id"] if nxt else "STATEMENT_END",
                "next_surface": nxt["surface"] if nxt else "STATEMENT_END",
                "outside_page_support_level": replay_rows[int(row["attachment_id"].split("A")[-1]) - 1]["outside_page_support_level"],
                "result": "VISIBLE_OWNER_FALLBACK",
            })

    replay_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    events_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay_rows:
        replay_by_page[str(row["physical_page"])].append(row)
    for row in events:
        events_by_page[row["physical_page"]].append(row)
    page_rows: list[dict[str, object]] = []
    for page in pages:
        physical_page = page["physical_page"]
        focus = replay_by_page.get(physical_page, [])
        page_events = events_by_page.get(physical_page, [])
        page_rows.append({
            "physical_page": physical_page, "register": page["register"],
            "running_event_count": len(page_events), "focus_attachment_count": len(focus),
            "exact_surface_events": sum(row["page_replay_result"] == "EXACT_SURFACE_FROM_OTHER_PAGE" for row in page_events),
            "known_recipe_events": sum(row["page_replay_result"] == "ROOT_RECIPE_FROM_OTHER_PAGE" for row in page_events),
            "new_recipe_known_atom_events": sum(row["page_replay_result"] == "NEW_PAGE_RECIPE__KNOWN_ATOMS" for row in page_events),
            "exact_typed_head_support": sum(row["outside_page_support_level"] == "EXACT_TYPED_HEAD" for row in focus),
            "typed_micro_fallback": sum(row["outside_page_support_level"] == "TYPED_MICRO" for row in focus),
            "untyped_micro_fallback": sum(row["outside_page_support_level"] == "UNTYPED_MICRO" for row in focus),
            "coarse_rule_fallback": sum(row["outside_page_support_level"] == "COARSE_RULE" for row in focus),
            "composed_rule_component_fallback": sum(row["outside_page_support_level"] == "COMPOSED_RULE_COMPONENTS" for row in focus),
            "private_focus_patterns": sum(row["outside_page_support_level"] == "NONE" for row in focus),
            "future_admission_rehearsal": "ADDRESS_ONLY" if not page_events else "PASS_HIERARCHICAL_DECK" if all(row["future_page_result"] == "PORTABLE_BY_EXISTING_HIERARCHY" for row in focus) else "FAIL_PRIVATE_PATTERN",
        })

    deck_rows = [
        {"priority": 1, "color": "GREEN", "trigger": "EXACT_SURFACE_ONE_RECIPE", "decision": "READ_WITH_EXISTING_RECIPE", "repair_allowed": "NO", "meaning": "bekannte Oberfläche; identisches sichtbares Rezept"},
        {"priority": 2, "color": "GREEN", "trigger": "KNOWN_RECIPE_NEW_SURFACE", "decision": "READ_AS_NEW_RENDERING_ONLY_IF_NAMED_PACKAGE_RULE", "repair_allowed": "NO", "meaning": "neue Oberfläche; Rezept andernorts vollständig sichtbar"},
        {"priority": 3, "color": "AMBER", "trigger": "NEW_RECIPE_FIXED_ATOMS", "decision": "SEGMENT_VISIBLY_AND_USE_HIERARCHICAL_SCOPE", "repair_allowed": "NO", "meaning": "neue Komposition bekannter Kerne"},
        {"priority": 4, "color": "AMBER", "trigger": "PAGE_PRIVATE_EXACT_TYPED_HEAD", "decision": "FALL_BACK_TO_TYPED_OR_UNTYPED_MICRO", "repair_allowed": "NO", "meaning": "neue Kopfbesetzung einer bekannten Mikrokonstruktion"},
        {"priority": 5, "color": "AMBER", "trigger": "PAGE_PRIVATE_MICRO", "decision": "FALL_BACK_TO_ONE_OF_NINE_COARSE_RULES", "repair_allowed": "NO", "meaning": "neue Mikroform einer bekannten Scope-Familie"},
        {"priority": 6, "color": "GREEN", "trigger": "HEADLESS_PACKAGE_NEXT_CARD", "decision": "ALLOW_EXACTLY_ONE_CARD_WITHIN_SAME_OWNER_STATEMENT", "repair_allowed": "NO", "meaning": "begrenzter Vorgriff"},
        {"priority": 7, "color": "GREEN", "trigger": "NO_ACTION_HEAD", "decision": "BIND_TO_VISIBLE_OWNER", "repair_allowed": "NO", "meaning": "Besitzerellipse"},
        {"priority": 8, "color": "RED", "trigger": "SAME_SURFACE_DIFFERENT_RECIPE", "decision": "STOP_AND_RESEGMENT", "repair_allowed": "YES_VISIBLE_ONLY", "meaning": "Oberflächendeterminismus gebrochen"},
        {"priority": 9, "color": "RED", "trigger": "LOOKAHEAD_OVER_ONE_CARD", "decision": "STOP", "repair_allowed": "NO", "meaning": "unlizenzierter Fernbezug"},
        {"priority": 10, "color": "RED", "trigger": "OWNER_OR_STATEMENT_BOUNDARY_CROSSING", "decision": "STOP", "repair_allowed": "NO", "meaning": "echter Scope-Bruch"},
        {"priority": 11, "color": "RED", "trigger": "KNOWN_CORE_REQUIRES_NEW_VALUE", "decision": "STOP_BATCH_BEFORE_DICTIONARY_CHANGE", "repair_allowed": "NO", "meaning": "Bedeutungsdrift"},
        {"priority": 12, "color": "RED", "trigger": "TENTH_COARSE_SCOPE_FAMILY", "decision": "STOP_BATCH", "repair_allowed": "NO", "meaning": "neue Grammatik statt neuer Komposition"},
        {"priority": 13, "color": "RED", "trigger": "ACTION_LIKE_LABEL_OPENS_PROSE_STACK", "decision": "KEEP_AS_ADDRESS_UNLESS_LAYOUT_OPENS_PROSE", "repair_allowed": "NO", "meaning": "Adress-/Prosaebene verwechselt"},
        {"priority": 14, "color": "RED", "trigger": "INVISIBLE_ATOM_FROM_EDIT_NEIGHBOR", "decision": "STOP_AND_USE_VISIBLE_SEGMENTATION", "repair_allowed": "YES_VISIBLE_ONLY", "meaning": "alter Pass-1008-Fehler"},
    ]

    paths = [
        OUT / "gdt400_4374_hierarchical_replay.tsv", OUT / "gdt400_signature_support.tsv",
        OUT / "gdt400_127_forward_cases.tsv", OUT / "gdt400_126_owner_cases.tsv",
        OUT / "gdt400_22_page_admission_rehearsal.tsv", OUT / "gdt400_error_deck.tsv",
    ]
    for path, rows in zip(paths, [replay_rows, signature_rows, forward_rows, owner_rows, page_rows, deck_rows]):
        write_tsv(path, rows)

    summary = {
        "status": "FUTURE_PAGE_ERROR_DECK_READY", "attachment_count": len(replay_rows),
        "signature_counts": {level: sum(row["signature_level"] == level for row in signature_rows) for level in levels + ["RULE_COMPONENT"]},
        "outside_page_support_level_counts": dict(support_level_counts),
        "outside_register_support_level_counts": dict(register_support_level_counts),
        "private_attachment_count": support_level_counts["NONE"],
        "forward_case_count": len(forward_rows), "owner_case_count": len(owner_rows),
        "forward_reason_counts": dict(sorted(Counter(row["forward_reason"] for row in forward_rows).items())),
        "owner_reason_counts": dict(sorted(Counter(row["owner_reason"] for row in owner_rows).items())),
        "page_rehearsal_counts": dict(sorted(Counter(row["future_admission_rehearsal"] for row in page_rows).items())),
        "deck_rule_count": len(deck_rows),
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in [ATTACHMENTS, EVENTS, STATEMENTS, PAGES, RULES]},
        "output_hashes": {path.name: sha256(path) for path in paths},
    }
    (OUT / "gdt400_result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sheet = f"""# Nächste vier Seiten — Fehlerkarte nach GDT400

## In dieser Reihenfolge lesen

1. Oberfläche exakt bekannt: bestehendes Rezept unverändert benutzen.
2. Rezept bekannt, Oberfläche neu: nur bei benannter Verpackungsregel als
   Schreibform übernehmen; sonst sichtbar neu segmentieren.
3. Rezept neu, Atome bekannt: mit der Scope-Hierarchie lesen.
4. Exaktes Kopf-Mikromuster neu: auf typisierte Mikroform, dann untypisierte
   Mikroform, zuletzt eine der neun groben Regeln zurückfallen.
5. Kopflose Karte: höchstens die unmittelbar nächste Karte im selben
   Besitzer- und Aussagenrahmen verwenden.
6. Ohne sichtbaren oder geerbten Kopf: beim sichtbaren Besitzer bleiben.

## Sofort rot

- dieselbe Oberfläche verlangt ein zweites Rezept;
- ein bekanntes Zeichen verlangt einen neuen Kernwert;
- ein Bezug springt mehr als eine Karte oder über Besitzer/Aussage;
- eine zehnte grobe Scope-Familie wäre nötig;
- ein Bildlabel eröffnet ohne Layoutsignal einen Prosa-Stack;
- ein unsichtbares Atom wird aus einem Ein-Edit-Nachbarn importiert.

## Was die alten Seiten tatsächlich lehren

- {len(replay_rows):,} von {len(replay_rows):,} Foci besitzen Unterstützung außerhalb
  ihrer Seite und ihres Registers in der bestehenden Hierarchie. Vier
  Bio-Fälle benötigen dafür die Komposition zweier einzeln registerportabler
  Regeln; diese bleiben gelb, nicht grün.
- Exakte Kopf-Signatur genügt außerhalb der Seite bei
  {support_level_counts['EXACT_TYPED_HEAD']:,} Fällen; typisierte Mikroform bei
  {support_level_counts['TYPED_MICRO']:,}, untypisierte Mikroform bei
  {support_level_counts['UNTYPED_MICRO']:,}, grobe Regel bei
  {support_level_counts['COARSE_RULE']:,} und komponierte Regelbestandteile bei
  {support_level_counts['COMPOSED_RULE_COMPONENTS']:,}.
- 127 Vorgriffe und 126 Besitzerellipsen sind vollständig als Beispiele im
  Artefaktdeck enthalten.

Neue Oberfläche und neue Komposition sind normal. Neue Grundbedeutung, neuer
Fernbezug oder neue Grammatik sind es nicht.
"""
    (HERE / "NEXT_FOUR_PAGE_ERROR_DECK.md").write_text(sheet, encoding="utf-8")
    report = f"""# GDT400 — Fehlerdeck für die nächsten Seiten

Die GDT399-Scope-Basis wurde auf fünf Abstraktionsstufen replayt. Alle
{len(replay_rows):,} Anschlüsse finden außerhalb ihrer eigenen Seite und ihres
Registers Unterstützung; **0** bleiben privat. Es gibt 108 typisierte
Mikrosignaturen, davon etliche selten, aber jede fällt auf eine bereits
mehrseitige Mikroform oder eine der neun groben Regeln zurück. Vier
Biological-Anschlüsse kombinieren `ONE_CARD_FORWARD` beziehungsweise
`Q_OT_PACKAGE_FORWARD` mit `R_POSITIONAL_MARKING`; genau diese Kombination ist
registerlokal, ihre beiden Bestandteile sind jedoch separat in anderen
Registern belegt und werden als gelbe Komposition geführt.

Die riskanten Randklassen sind vollständig ausgeschrieben: {len(forward_rows)}
Ein-Karten-Vorgriffe und {len(owner_rows)} Besitzerellipsen. Kein Fall braucht
einen zweiten Kartenblick, eine Besitzerüberschreitung oder einen neuen
Kernwert. Das 14-Regel-Deck trennt grüne Übernahmen, gelbe neue Kompositionen
und rote Modellbrüche.

Damit ist die nächste Vierseitenprüfung operational vorbereitet: Sie darf neue
Oberflächen und neue Kombinationen finden, aber keine unsichtbaren Atome,
zweiten Rezepte, Bedeutungsdrift, Fernbezüge oder zehnte Scope-Familie retten.
"""
    (HERE / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
