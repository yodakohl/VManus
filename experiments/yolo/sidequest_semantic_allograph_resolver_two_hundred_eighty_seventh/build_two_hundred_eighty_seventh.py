#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
CARDS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
EVENTS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"

RESOLVER = {
    "MC039": "GENERAL_MEASURE", "MC144": "SETTLING_MEASURE", "MC170": "EXTRACT_PORTION_MEASURE",
    "MC153": "PLAIN_CONTINUATION", "MC016": "CONNECTION_CONTINUATION", "MC134": "PATH_CONTINUATION",
    "MC026": "SET_CURRENT_ITEM", "MC103": "SET_AND_CONTINUE_ITEM",
    "MC074": "SHORT_TRANSFER_FORM", "MC064": "EXPANDED_TRANSFER_FORM",
    "MC154": "TARGET_ADDRESS", "MC056": "TARGET_MARK",
    "MC055": "SOURCE_ORIGIN", "MC089": "SOURCE_OUTFLOW",
    "MC047": "FIRST_PORTION", "MC072": "PREPARATION_SHARE", "MC105": "GENERAL_PORTION",
    "MC005": "PREVIOUS_ITEM_TRANSFER", "MC088": "NEW_ITEM_TRANSFER",
    "MC077": "TARGET_BINDER", "MC090": "CONTINUATION_BINDER", "MC104": "SHORT_CONTINUATION_BINDER", "MC136": "SOURCE_EXTRACT_BINDER",
    "MC032": "GENERAL_LONG_ADJUSTMENT", "MC166": "LONG_WARMING",
    "MC073": "LOCAL_CTH_ALLOGRAPH", "MC137": "LOCAL_CTH_ALLOGRAPH",
    "MC033": "WORKING_STAGE", "MC172": "END_STAGE",
    "MC057": "LOCAL_OT_TRANSFER_ALLOGRAPH", "MC067": "LOCAL_OT_TRANSFER_ALLOGRAPH",
    "MC107": "SWITCH_TO_NEXT_PROCESS", "MC171": "NEXT_ITEM",
    "MC078": "INTERMEDIATE_TARGET", "MC046": "END_TARGET",
    "MC065": "OUTLET", "MC066": "CLEAR_WITHDRAWAL",
    "MC076": "SHORT_HOLD", "MC106": "SHORT_CONTINUATION",
    "MC053": "CONTINUE_SAME_PROCESS", "MC163": "SWITCH_TO_FOLLOWING_PROCESS",
    "MC010": "CURRENT_INPUT_AT_TARGET", "MC131": "CURRENT_INPUT",
    "MC117": "PROCESS_CURRENT_ITEM", "MC122": "SHORT_PROCESS_CURRENT_ITEM",
}

GLOSS = {
    "GENERAL_MEASURE": "allgemeines Sollmaß",
    "SETTLING_MEASURE": "Sollmaß für Absetzung",
    "EXTRACT_PORTION_MEASURE": "Sollportion des Auszugs",
    "PLAIN_CONTINUATION": "bloß weiter",
    "CONNECTION_CONTINUATION": "Anschluss weiterführen",
    "PATH_CONTINUATION": "Weiterweg",
    "SET_CURRENT_ITEM": "aktuellen Posten einsetzen",
    "SET_AND_CONTINUE_ITEM": "aktuellen Posten einsetzen und weiterbearbeiten",
    "SHORT_TRANSFER_FORM": "kurze Transferform",
    "EXPANDED_TRANSFER_FORM": "ausgebaute Transferform",
    "TARGET_ADDRESS": "zur Zieladresse",
    "TARGET_MARK": "Zielmarke setzen",
    "SOURCE_ORIGIN": "von der Quelle",
    "SOURCE_OUTFLOW": "Quellausguss",
    "FIRST_PORTION": "erste Portion",
    "PREPARATION_SHARE": "Anteil der Zubereitung",
    "GENERAL_PORTION": "allgemeine Portion",
    "PREVIOUS_ITEM_TRANSFER": "vorigen Posten übertragen",
    "NEW_ITEM_TRANSFER": "neuen Posten übertragen",
    "TARGET_BINDER": "an Ziel binden",
    "CONTINUATION_BINDER": "an Fortsetzung binden",
    "SHORT_CONTINUATION_BINDER": "kurz an Fortsetzung binden",
    "SOURCE_EXTRACT_BINDER": "an Quellauszug binden",
    "GENERAL_LONG_ADJUSTMENT": "länger bearbeiten",
    "LONG_WARMING": "länger wärmen",
    "LOCAL_CTH_ALLOGRAPH": "lokale CTH-Kurzform",
    "WORKING_STAGE": "laufende Arbeitsstufe",
    "END_STAGE": "Endstufe",
    "LOCAL_OT_TRANSFER_ALLOGRAPH": "lokale Folgetransferform",
    "SWITCH_TO_NEXT_PROCESS": "zum nächsten Arbeitsgang wechseln",
    "NEXT_ITEM": "nächsten Posten wählen",
    "INTERMEDIATE_TARGET": "Zwischenziel",
    "END_TARGET": "Endziel",
    "OUTLET": "Auslass",
    "CLEAR_WITHDRAWAL": "Klarabzug",
    "SHORT_HOLD": "kurz halten",
    "SHORT_CONTINUATION": "kurz weiterführen",
    "CONTINUE_SAME_PROCESS": "danach im selben Gang weiter",
    "SWITCH_TO_FOLLOWING_PROCESS": "zum Folgegang wechseln",
    "CURRENT_INPUT_AT_TARGET": "aktuelle Eingabe am Ziel",
    "CURRENT_INPUT": "aktuelle Eingabe",
    "PROCESS_CURRENT_ITEM": "aktuellen Posten bearbeiten",
    "SHORT_PROCESS_CURRENT_ITEM": "aktuellen Posten kurz bearbeiten",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_recipe(row: dict[str, str]) -> str:
    old = row["old_component_parse"]
    modifiers: list[str] = []
    if "GRADE_1" in old or "E_SHORT" in old:
        modifiers.append("GRADE=E_SHORT")
    if "GRADE_2" in old:
        modifiers.append("GRADE=EE_LONG")
    if "GRADE_3" in old:
        modifiers.append("GRADE=EEE_FULL")
    if "OK + OK" in old:
        modifiers.append("REPEAT=YES")
    if "DY" not in row["family_parse"] and ("CLOSE" in old or "TERMINAL" in old or "Schluss" in row["local_prose_default_de"]):
        modifiers.append("LICENSED_CLOSE=YES")
    return row["family_parse"] if not modifiers else f"{row['family_parse']}[{','.join(modifiers)}]"


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    composed = [r for r in cards if r["card_class_279"] == "COMPOSED_FROM_36_FAMILIES"]
    card_by_id = {r["master_card_id"]: r for r in composed}
    base_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in composed:
        base_groups[base_recipe(row)].append(row)
    ambiguous = {k: v for k, v in base_groups.items() if len(v) > 1}
    assert len(ambiguous) == 20
    assert set(RESOLVER) == {r["master_card_id"] for rows in ambiguous.values() for r in rows}

    decisions: list[dict[str, object]] = []
    for recipe, members in sorted(ambiguous.items()):
        modifiers = {RESOLVER[r["master_card_id"]] for r in members}
        resolved = len(modifiers) > 1
        pairs = [f"{r['master_form']}={GLOSS[RESOLVER[r['master_card_id']]]}" for r in sorted(members, key=lambda x: x["master_form"])]
        decisions.append({
            "base_recipe": recipe,
            "card_type_count": len(members),
            "event_support": sum(int(r["prose_event_count"]) for r in members),
            "master_forms": "|".join(r["master_form"] for r in members),
            "choice_meanings_de": " | ".join(pairs),
            "decision": "SEMANTIC_SUBTYPE_RESOLVED" if resolved else "LOCAL_ALLOGRAPH_REMAINS",
            "apprentice_rule_de": "Wähle die Form nach dem kurzen Bedeutungszusatz." if resolved else "Beide Formen bedeuten dasselbe; lerne die örtliche Kartenform aus dem Exemplar.",
        })

    refined_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in composed:
        base = base_recipe(row)
        refined = base
        if base in ambiguous:
            refined = f"{base}[SUBTYPE={RESOLVER[row['master_card_id']]}]"
        refined_groups[refined].append(row)

    recipes: list[dict[str, object]] = []
    for refined, members in refined_groups.items():
        ranked = sorted(members, key=lambda r: (-int(r["prose_event_count"]), r["master_card_id"]))
        canonical = ranked[0]
        recipes.append({
            "resolved_recipe": refined,
            "canonical_master_card_id": canonical["master_card_id"],
            "canonical_form": canonical["master_form"],
            "canonical_value_de": canonical["local_prose_default_de"],
            "alternate_forms": "|".join(r["master_form"] for r in ranked[1:]) or "NONE",
            "card_type_count": len(members),
            "event_support": sum(int(r["prose_event_count"]) for r in members),
            "canonical_event_hits": int(canonical["prose_event_count"]),
            "writer_rule": "WRITE_CANONICAL" if len(members) == 1 else "COPY_LOCAL_ALLOGRAPH_FROM_EXEMPLAR",
        })
    recipes.sort(key=lambda r: (-int(r["event_support"]), str(r["resolved_recipe"])))

    event_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        event_by_statement[row["statement_id"]].append(row)
    occurrence_rows: list[dict[str, object]] = []
    ambiguous_ids = {r["master_card_id"] for members in ambiguous.values() for r in members}
    for event in events:
        if event["master_card_id"] not in ambiguous_ids:
            continue
        card = card_by_id[event["master_card_id"]]
        statement = event_by_statement[event["statement_id"]]
        pos = next(i for i, r in enumerate(statement) if r["event_id"] == event["event_id"])
        subtype = RESOLVER[event["master_card_id"]]
        occurrence_rows.append({
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "visible_owner": event["visible_owner"],
            "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"],
            "base_recipe": base_recipe(card),
            "resolved_subtype": subtype,
            "resolved_value_de": GLOSS[subtype],
            "position_in_statement": f"{pos + 1}/{len(statement)}",
            "previous_master_card": statement[pos - 1]["master_card_id"] if pos else "START",
            "next_master_card": statement[pos + 1]["master_card_id"] if pos + 1 < len(statement) else "END",
            "choice_mode": "SEMANTIC_SUBTYPE" if decisions[[d["base_recipe"] for d in decisions].index(base_recipe(card))]["decision"] == "SEMANTIC_SUBTYPE_RESOLVED" else "LOCAL_EXEMPLAR_ALLOGRAPH",
        })

    decision_path = OUT / "TWO_HUNDRED_EIGHTY_SEVENTH_20_ALLOGRAPH_DECISIONS.tsv"
    recipe_path = OUT / "TWO_HUNDRED_EIGHTY_SEVENTH_147_RESOLVED_RECIPES.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_EIGHTY_SEVENTH_126_OCCURRENCE_CHOICES.tsv"
    manual_path = OUT / "TWO_HUNDRED_EIGHTY_SEVENTH_RESOLVED_WRITER_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_SEVENTH_REPORT.md"
    write_tsv(decision_path, decisions, list(decisions[0]))
    write_tsv(recipe_path, recipes, list(recipes[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))

    manual = [
        "# Aufgelöste Werkstattvarianten",
        "",
        "Die scheinbaren Allographen werden nicht pauschal gleichgesetzt. Der Lehrling fragt zuerst nach dem kleinen Bedeutungszusatz. Nur zwei Paare bleiben echte lokale Kartenvarianten.",
        "",
    ]
    for row in decisions:
        manual.extend([
            f"## {row['base_recipe']}",
            "",
            f"{row['choice_meanings_de']}. {row['apprentice_rule_de']}",
            "",
        ])
    manual.extend([
        "## Ergebnis für den Schreiber",
        "",
        "Nach den Zusatzregeln gibt es 147 genaue Bedeutungsrezepte für 149 zusammengesetzte Karten. 145 Rezepte haben genau eine Standardkarte. Nur die zwei lokalen Paare CTH-Kurzvorbereitung und OT-Folgetransfer müssen noch aus dem Masterexemplar kopiert werden. Die Standardwahl trifft damit 350 von 352 zusammengesetzten Vorkommen.",
        "",
    ])
    manual_path.write_text("\n".join(manual), encoding="utf-8")

    unresolved = [r for r in decisions if r["decision"] == "LOCAL_ALLOGRAPH_REMAINS"]
    canonical_hits = sum(int(r["canonical_event_hits"]) for r in recipes)
    report_path.write_text(
        "# Sidequest-Pass 287: Auflösung der restlichen Allographen\n\n"
        "## Ergebnis\n\n"
        "Achtzehn der zwanzig R286-Variantenfamilien enthielten noch einen echten semantischen Zusatz: erste/allgemeine Portion, Quelle/Quellausguss, Ziel/Zielmarke, neuer/voriger Transfer, kurze/lange Bearbeitung und ähnliche Werkstattunterschiede. "
        "Nach ihrer Abtrennung entstehen 147 genaue Rezepte; 145 sind einförmig. Nur zwei je zweiförmige lokale Paare bleiben exemplarabhängig.\n\n"
        "Der Standardencoder wählt nun 350/352 zusammengesetzte Ereignisse direkt. Das ist kein reines Buchstabenalphabet: die Produktivität kommt aus 36 Stämmen und Modifiers, während zwei lokale Allographenpaare und die bekannten Ganzzeichen weiterhin gelernt werden.\n\n"
        f"Inputs `{sha(CARDS)}` und `{sha(EVENTS)}`; unresolved sets {len(unresolved)}.\n",
        encoding="utf-8",
    )

    outputs = (decision_path, recipe_path, occurrence_path, manual_path, report_path)
    summary = {
        "status": "PASS",
        "initial_ambiguous_sets": len(decisions),
        "semantic_subtype_sets": sum(r["decision"] == "SEMANTIC_SUBTYPE_RESOLVED" for r in decisions),
        "remaining_local_allograph_sets": len(unresolved),
        "resolved_recipes": len(recipes),
        "single_form_recipes": sum(int(r["card_type_count"]) == 1 for r in recipes),
        "remaining_ambiguous_recipes": sum(int(r["card_type_count"]) > 1 for r in recipes),
        "ambiguous_occurrences_audited": len(occurrence_rows),
        "canonical_event_hits": canonical_hits,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
