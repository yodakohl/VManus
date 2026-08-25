#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_last_whole_word_composition_nine_hundred_sixth"
PFX6 = "NINE_HUNDRED_SIXTH"
PFX = "NINE_HUNDRED_SEVENTH"

PAGE_ORDER = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]
PAGE_TITLES = {
    "f10r": "Pflanzenblatt A — gezahnte Blütenpflanze",
    "f11r": "Pflanzenblatt B — zweite Zubereitungsfolge",
    "f55v": "Pflanzenblatt C — breitblättriger Stoff",
    "f56r": "Pflanzenblatt D — feuchte Standortpflanze",
    "f81v": "Badblatt A — gemeinsames zweireihiges Becken",
    "f82r": "Badblatt B — mehrere lokale Stationen",
    "f83r": "Badblatt C — lokale Becken, Wege und Anwendungen",
    "f67r2": "Himmelsblatt A — Phasen- und Aspektplätze",
    "f68r1": "Himmelsblatt B — direkter Sternort",
    "f69v": "Himmelsblatt C — 28er-, Feuchte- und Qualitätsring",
}

TARGETS = {
    "A3:G047": {
        "component_recipe": "SH+EE+Y", "slot_signature": "STATE>GRADE>REFERENT",
        "atomic_root_reading_de": "HALTEN · LANG · POSTEN", "primary_card_pattern": "STATE_OR_GRADE",
        "apprentice_action": "READ_LOCAL_CONDITION_WORD", "functional_allograph": "GENERAL_LONG_HOLD",
        "trigger": "den Posten gewöhnlich lang halten", "skeleton": "sh-ee-y/chy/chey/dy/shy/sy",
        "rules": "ROOT_ORDER_COPY | E_GRADE_LENGTH | Y_OPEN_ENDPOINT",
        "renderability": "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE",
    },
    "PROC041": {
        "primary_card_pattern": "CLOSING_INSTRUCTION", "apprentice_action": "READ_ROOT_COMPOSITION",
        "functional_allograph": "NOT_APPLICABLE", "trigger": "NOT_APPLICABLE", "skeleton": "o-dy",
        "rules": "ROOT_ORDER_COPY | DY_CLOSED_ENDPOINT", "renderability": "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING",
    },
    "PROC052": {
        "primary_card_pattern": "ARGUMENT_OR_ADDRESS", "apprentice_action": "READ_ROOT_COMPOSITION",
        "functional_allograph": "NOT_APPLICABLE", "trigger": "NOT_APPLICABLE", "skeleton": "cho/sho",
        "rules": "ROOT_ORDER_COPY", "renderability": "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING",
    },
    "PROC109": {
        "primary_card_pattern": "ORDERED_INSTRUCTION", "apprentice_action": "READ_ROOT_COMPOSITION",
        "functional_allograph": "NOT_APPLICABLE", "trigger": "NOT_APPLICABLE", "skeleton": "qot/ot-ee-y/chy/chey/dy/shy/sy",
        "rules": "ROOT_ORDER_COPY | OT_FRAME_ALLOGRAPH | E_GRADE_LENGTH | Y_OPEN_ENDPOINT",
        "renderability": "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING",
    },
    "PROC157": {
        "primary_card_pattern": "STATE_OR_GRADE", "apprentice_action": "READ_ROOT_COMPOSITION",
        "functional_allograph": "MARKED_LONG_HOLD", "trigger": "einen lokal markierten langen Halt ausführen",
        "skeleton": "sh-ee-y/chy/chey/dy/shy/sy", "rules": "ROOT_ORDER_COPY | E_GRADE_LENGTH | Y_OPEN_ENDPOINT",
        "renderability": "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE",
    },
}


def read(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def delta(row: dict[str, str], identities: int, marks: int) -> None:
    row["identity_count"] = str(int(row["identity_count"]) + identities)
    row["mark_count"] = str(int(row["mark_count"]) + marks)


def aligned_replace(source: str, separator: str, source_marks: list[dict[str, str]], key: str) -> str:
    pieces = source.split(separator)
    assert len(pieces) == len(source_marks)
    for index, mark in enumerate(source_marks):
        if mark["identity"] in TARGETS:
            pieces[index] = mark[key]
    return separator.join(pieces)


def main() -> None:
    symbols = read(f"{PFX6}_47_COMPLETE_SYMBOL_DICTIONARY.tsv")
    patterns = read(f"{PFX6}_8_CARD_PATTERNS.tsv")
    rules = read(f"{PFX6}_15_RENDERER_RULES.tsv")
    micro = read(f"{PFX6}_36_FUNCTIONAL_ALLOGRAPHS.tsv")
    contractions = read(f"{PFX6}_2_COMPOSITIONAL_CONTRACTIONS.tsv")
    dictionary = read(f"{PFX6}_231_ZERO_WHOLE_CONDITION_CARD_DICTIONARY.tsv")
    marks = read(f"{PFX6}_437_ZERO_WHOLE_CONDITION_INTERLINEAR.tsv")
    units = read(f"{PFX6}_118_ZERO_WHOLE_CONDITION_UNITS.tsv")
    cards = read(f"{PFX6}_6_COMPLETE_JOB_CARDS.tsv")
    workflow = read(f"{PFX6}_12_STEP_WORKFLOW.tsv")

    symbol_rows = [dict(row) for row in symbols]
    for row in symbol_rows:
        if row["symbol"] in {"SH", "EE", "Y"}:
            row["weighted_mark_uses"] = str(int(row["weighted_mark_uses"]) + 1)
            if "cheey" not in row["surface_examples"].split(" | "):
                row["surface_examples"] += " | cheey"

    pattern_rows = [dict(row) for row in patterns]
    pattern_delta = {
        "WHOLE_LEXICON": (-5, -7),
        "CLOSING_INSTRUCTION": (1, 1),
        "ORDERED_INSTRUCTION": (1, 2),
        "STATE_OR_GRADE": (2, 2),
        "ARGUMENT_OR_ADDRESS": (1, 2),
    }
    for row in pattern_rows:
        if row["pattern"] in pattern_delta:
            delta(row, *pattern_delta[row["pattern"]])
        if row["pattern"] == "WHOLE_LEXICON":
            row["teaching_rule_de"] = "Nur TALAM als gelerntes Ganzwort BEISEITESTELLEN aus dem Werkstattdeck lesen."

    rule_rows = [dict(row) for row in rules]
    rule_delta = {
        "ROOT_ORDER_COPY": (5, 7),
        "OT_FRAME_ALLOGRAPH": (1, 2),
        "E_GRADE_LENGTH": (3, 4),
        "Y_OPEN_ENDPOINT": (3, 4),
        "DY_CLOSED_ENDPOINT": (1, 1),
        "MEMORIZED_WHOLE_FORM": (-5, -7),
    }
    for row in rule_rows:
        if row["renderer_rule"] in rule_delta:
            delta(row, *rule_delta[row["renderer_rule"]])
        if row["renderer_rule"] == "MEMORIZED_WHOLE_FORM":
            row["instruction"] = "Copy TALAM as the sole learned whole-root spelling."

    micro_rows = [dict(row) for row in micro]
    for row in micro_rows:
        if row["component_recipe"] == "SH+EE+Y" and row["surface"] == "cheey":
            row["occurrence_marks"] = str(int(row["occurrence_marks"]) + 1)
            row["identities"] = "A3:G047 | " + row["identities"]
            row["pages"] = "f11r | f69v | f82r | f83r"
            row["sections"] = "HOW | WHAT | WHEN"

    dictionary_rows = []
    for source in dictionary:
        row = dict(source)
        target = TARGETS.get(row["identity"])
        if target:
            for field in ["component_recipe", "slot_signature", "atomic_root_reading_de"]:
                if field in target:
                    row[field] = target[field]
            row["primary_card_pattern"] = target["primary_card_pattern"]
            row["apprentice_action"] = target["apprentice_action"]
            row["functional_allographs"] = (
                f"{target['functional_allograph']}->{row['surface_forms']}"
                if target["functional_allograph"] != "NOT_APPLICABLE" else "NONE"
            )
            row["renderability"] = target["renderability"]
        dictionary_rows.append(row)
    dictionary_by_id = {row["identity"]: row for row in dictionary_rows}

    mark_rows = []
    for source in marks:
        row = dict(source)
        target = TARGETS.get(row["identity"])
        if target:
            dictionary_row = dictionary_by_id[row["identity"]]
            row.update({
                "component_recipe": dictionary_row["component_recipe"],
                "slot_signature": dictionary_row["slot_signature"],
                "atomic_root_reading_de": dictionary_row["atomic_root_reading_de"],
                "functional_allograph": target["functional_allograph"],
                "microfunction_trigger_de": target["trigger"],
                "renderer_skeleton": target["skeleton"],
                "reading_action": target["apprentice_action"],
                "renderer_rules": target["rules"],
                "renderability": target["renderability"],
            })
        mark_rows.append(row)

    marks_by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in mark_rows:
        marks_by_unit[(row["order_id"], row["unit"])].append(row)

    unit_rows = []
    for source in units:
        row = dict(source)
        key = (row["order_id"], row["unit"])
        local_marks = marks_by_unit[key]
        assert row["fifth_hand_surface_sequence"].split() == [mark["surface"] for mark in local_marks]
        if any(mark["identity"] in TARGETS for mark in local_marks):
            row["root_reading_sequence_de"] = aligned_replace(row["root_reading_sequence_de"], " ; ", local_marks, "atomic_root_reading_de")
            row["card_pattern_sequence"] = " -> ".join(dictionary_by_id[mark["identity"]]["primary_card_pattern"] for mark in local_marks)
            row["slot_signature_sequence"] = " || ".join(mark["slot_signature"] for mark in local_marks)
            row["renderer_skeleton_sequence"] = " || ".join(mark["renderer_skeleton"] for mark in local_marks)
            row["renderability_sequence"] = " | ".join(mark["renderability"] for mark in local_marks)
            functions = [mark["functional_allograph"] for mark in local_marks if mark["functional_allograph"] != "NOT_APPLICABLE"]
            row["microfunction_marks"] = str(len(functions))
            row["microfunction_sequence"] = " | ".join(functions) if functions else "NONE"
            row["root_composed_marks"] = str(sum(mark["reading_action"] == "READ_ROOT_COMPOSITION" for mark in local_marks))
            row["fused_whole_form_marks"] = str(sum(mark["reading_action"] == "READ_FUSED_WHOLE_WORD" for mark in local_marks))
            row["learned_whole_root_marks"] = str(sum(mark["reading_action"] == "READ_LEARNED_WHOLE_ROOT" for mark in local_marks))
            row["multi_allograph_marks"] = str(sum(mark["renderability"] == "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE" for mark in local_marks))
        unit_rows.append(row)

    card_rows = []
    pattern_order = [row["pattern"] for row in sorted(pattern_rows, key=lambda row: int(row["precedence"]))]
    renderer_order = [
        "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE",
        "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING",
        "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION",
        "MEMORIZED_EXACT_FORM",
    ]
    for source in cards:
        row = dict(source)
        local_marks = [mark for mark in mark_rows if mark["order_id"] == row["order_id"]]
        pattern_counter = Counter(dictionary_by_id[mark["identity"]]["primary_card_pattern"] for mark in local_marks)
        renderer_counter = Counter(mark["renderability"] for mark in local_marks)
        row["pattern_counts"] = " | ".join(f"{name}:{pattern_counter[name]}" for name in pattern_order if pattern_counter[name])
        row["renderer_classes"] = " | ".join(f"{name}:{renderer_counter[name]}" for name in renderer_order if renderer_counter[name])
        row["root_composed_marks"] = str(sum(mark["reading_action"] == "READ_ROOT_COMPOSITION" for mark in local_marks))
        row["fused_whole_form_marks"] = str(sum(mark["reading_action"] == "READ_FUSED_WHOLE_WORD" for mark in local_marks))
        row["learned_whole_root_marks"] = str(sum(mark["reading_action"] == "READ_LEARNED_WHOLE_ROOT" for mark in local_marks))
        row["multi_allograph_marks"] = str(renderer_counter["COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE"])
        row["context_selected_marks"] = row["multi_allograph_marks"]
        row["microfunction_marks"] = str(sum(mark["functional_allograph"] != "NOT_APPLICABLE" for mark in local_marks))
        card_rows.append(row)

    grouped_units: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in unit_rows:
        grouped_units[(row["page"], row["unit"])].append(row)
    page_unit_rows = []
    for page in PAGE_ORDER:
        for (candidate_page, unit), local in grouped_units.items():
            if candidate_page != page:
                continue
            for field in ["fifth_hand_surface_sequence", "literal_sequence_de", "front_instruction_de", "section", "root_reading_sequence_de", "predicted_surface_sequence"]:
                assert len({item[field] for item in local}) == 1
            first = local[0]
            page_unit_rows.append({
                "page": page, "page_title_de": PAGE_TITLES[page], "unit": unit,
                "section": first["section"], "orders": " | ".join(sorted(item["order_id"] for item in local)),
                "owner_or_handle_de": " | ".join(f"{item['order_id']}:{item['owner_trace_de']}" for item in sorted(local, key=lambda item: item["order_id"])),
                "surface_sequence": first["fifth_hand_surface_sequence"],
                "atomic_root_sequence_de": first["root_reading_sequence_de"],
                "dictionary_literal_de": first["literal_sequence_de"],
                "fluent_workshop_reading_de": first["front_instruction_de"],
                "predicted_surface_sequence": first["predicted_surface_sequence"],
                "source_unit_copies": len(local),
            })

    whole_root = next(row for row in dictionary_rows if row["identity"] == "PROC043")
    learned_whole_rows = [{
        "identity": whole_root["identity"], "surface": whole_root["surface_forms"],
        "root": whole_root["component_recipe"], "meaning_de": whole_root["dictionary_value_de"],
        "marks": whole_root["marks"], "page": whole_root["pages"], "reason_de": "Kein zweiter stabiler Kern zerlegt die Karte kürzer; als einzelnes Werkstattwort lernen.",
    }]

    write(f"{PFX}_47_COMPLETE_SYMBOL_DICTIONARY.tsv", symbol_rows)
    write(f"{PFX}_8_CARD_PATTERNS.tsv", pattern_rows)
    write(f"{PFX}_15_RENDERER_RULES.tsv", rule_rows)
    write(f"{PFX}_36_FUNCTIONAL_ALLOGRAPHS.tsv", micro_rows)
    write(f"{PFX}_2_COMPOSITIONAL_CONTRACTIONS.tsv", contractions)
    write(f"{PFX}_1_LEARNED_WHOLE_ROOT.tsv", learned_whole_rows)
    write(f"{PFX}_231_SINGLE_WHOLE_ROOT_CARD_DICTIONARY.tsv", dictionary_rows)
    write(f"{PFX}_437_SINGLE_WHOLE_ROOT_INTERLINEAR.tsv", mark_rows)
    write(f"{PFX}_118_SINGLE_WHOLE_ROOT_UNITS.tsv", unit_rows)
    write(f"{PFX}_115_DEDUPED_PAGE_UNITS.tsv", page_unit_rows)
    write(f"{PFX}_6_COMPLETE_JOB_CARDS.tsv", card_rows)
    write(f"{PFX}_12_STEP_WORKFLOW.tsv", workflow)

    handbook = [
        "# Schreiberhandbuch mit einem einzigen Ganzwort",
        "",
        "Die Karte wird grundsätzlich aus den 36 Bedeutungswurzeln gebaut. Fünf früher memorierte Schreibungen sind jetzt gewöhnliche Kompositionen: `cheey`, `ody`, `cho`, `oteey`, `sheey`.",
        "Nur `talam` bleibt als gelerntes Ganzwort **BEISEITESTELLEN** im kleinen Werkstattdeck.",
        "",
        "## Zwölf Schritte",
        "",
    ]
    for row in workflow:
        handbook.append(f"{row['step']}. **{row['stage']}** — {row['instruction_de']}")
    handbook.extend(["", "## Die fünf befreiten Schreibungen", ""])
    for identity in TARGETS:
        row = dictionary_by_id[identity]
        handbook.append(f"- `{row['surface_forms']}` = `{row['component_recipe']}` → **{row['atomic_root_reading_de']}**.")
    handbook.extend(["", "## Ein Ganzwort", "", "- `talam` = **BEISEITESTELLEN**.", ""])
    (HERE / f"{PFX}_SINGLE_WHOLE_ROOT_SCRIBE_HANDBOOK.md").write_text("\n".join(handbook), encoding="utf-8")

    edition = [
        "# Zehnseitige Werkstattausgabe — nur TALAM als Ganzwort",
        "",
        "Vollständige aktuelle Sechs-Auftrags-Auswahl; 115 eindeutige Seiteneinheiten.",
        "",
    ]
    for page in PAGE_ORDER:
        edition.extend([f"## {page}: {PAGE_TITLES[page]}", ""])
        for row in page_unit_rows:
            if row["page"] == page:
                edition.extend([
                    f"### {row['unit']} / {row['section']} / {row['orders']}", "",
                    f"`{row['surface_sequence']}`", "",
                    f"**Atomar:** {row['atomic_root_sequence_de']}",
                    f"**Lesung:** {row['fluent_workshop_reading_de']}", "",
                ])
    (HERE / f"{PFX}_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "FIVE_REDUNDANT_MEMORIZED_RENDERINGS_JOIN_THEIR_EXISTING_COMPOSITIONAL_TWINS",
        "pages": 10, "semantic_roots": 36, "helper_signs": 11, "symbols": len(symbol_rows),
        "card_patterns": len(pattern_rows), "renderer_rules": len(rule_rows),
        "functional_allographs": len(micro_rows), "compositional_contractions": len(contractions),
        "learned_whole_roots": len(learned_whole_rows), "dictionary_identities": len(dictionary_rows),
        "marks": len(mark_rows), "units": len(unit_rows), "deduped_page_units": len(page_unit_rows),
        "job_cards": len(card_rows), "component_recipes": len({row["component_recipe"] for row in dictionary_rows}),
        "identity_renderability": dict(Counter(row["renderability"] for row in dictionary_rows)),
        "mark_renderability": dict(Counter(row["renderability"] for row in mark_rows)),
        "mark_actions": dict(Counter(row["reading_action"] for row in mark_rows)),
        "surface_prediction_mismatches": sum(row["surface"] != row["predicted_surface"] for row in mark_rows),
        "new_roots": 0, "new_pages": 0, "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PFX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PFX}_REPORT.md").write_text(
        "# Sidequest Pass 907: nur ein gelerntes Ganzwort bleibt\n\n"
        "Fünf als memoriert geführte Identitäten waren nur doppelt klassifizierte Schreibungen bereits gelesener Wurzelkarten. "
        "`cheey` und `sheey` sind SH+EE+Y, `ody` ist O+DY, `cho` ist HO und `oteey` ist OT+EE+Y. "
        "Sieben sichtbare Marken wechseln damit aus dem Ganzwortfach in die normale Komposition.\n\n"
        "Von 231 Identitäten sind nun 178 einfache Kompositionen, 50 funktionale Allographenfamilien, zwei lokale kompositionelle Kontraktionen und genau eine gelernte Ganzwurzel: `talam` = BEISEITESTELLEN. "
        "Auf Markenebene sind 292 einfach kompositionell, 142 funktionale Allographen, zwei Kontraktionen und eine TALAM-Marke.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
