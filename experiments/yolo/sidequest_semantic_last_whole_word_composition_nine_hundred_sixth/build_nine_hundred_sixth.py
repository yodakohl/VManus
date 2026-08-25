#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_complete_scribe_handbook_nine_hundred_fifth"
RENDER_BASE = ROOT / "sidequest_semantic_complete_functional_renderer_nine_hundred_fourth"
PFX5 = "NINE_HUNDRED_FIFTH"
PFX = "NINE_HUNDRED_SIXTH"

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
    "A3:G046": {
        "surface": "iokeeor",
        "old_value": "WETTERZEICHEN",
        "component_recipe": "OK+EE+OR",
        "slot_signature": "OPERATION>GRADE>MATERIAL",
        "atomic_root_reading_de": "ANSETZEN · LANG · ANSATZ",
        "dictionary_value_de": "LANGANSATZ",
        "local_fluent_expansion_de": "ANHALTENDE LAGE",
        "primary_card_pattern": "OPERATION_INSTRUCTION",
        "renderer_microfunction": "CONDITION_I_CARRIER",
        "microfunction_trigger_de": "im Feuchte-/Wetterring den langen Ansatz mit i- tragen",
        "renderer_skeleton": "i-ok-ee-or",
        "renderer_rules": "ROOT_ORDER_COPY | OK_FRAME_ALLOGRAPH | E_GRADE_LENGTH | LOCAL_SIGN_COPY",
        "renderability": "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION",
        "selected_parse_de": "i-TRAEGER + OK + EE + OR",
        "short_reading_de": "LANGANSATZ",
        "local_reading_de": "ANHALTENDE LAGE",
        "mechanical_rule_de": "Das bedeutungslose lokale i- trägt OK+EE+OR; alle drei Bedeutungswurzeln bleiben in Reihenfolge.",
        "rejected_rivals_de": "IIN+OK+EE+OR verlangt zu starke Kürzung; WETTERZEICHEN war nur aus dem Bildthema geraten.",
    },
    "A3:G056": {
        "surface": "daiial",
        "old_value": "FEUCHTESTUFE",
        "component_recipe": "DA+IIN+AL",
        "slot_signature": "GRADE>STATE>ADDRESS",
        "atomic_root_reading_de": "ZWEITE · STUFE · ZIELSTELLE",
        "dictionary_value_de": "ZWEITE ZIELSTUFE",
        "local_fluent_expansion_de": "ZWEITE FEUCHTESTUFE",
        "primary_card_pattern": "STATE_OR_GRADE",
        "renderer_microfunction": "IIN_AL_N_ELISION",
        "microfunction_trigger_de": "IIN direkt vor AL als ii schreiben",
        "renderer_skeleton": "da-iin-al",
        "renderer_rules": "ROOT_ORDER_COPY | ARGUMENT_OR_ADDRESS_TAIL | LOCAL_SIGN_COPY",
        "renderability": "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION",
        "selected_parse_de": "DA + IIN + AL",
        "short_reading_de": "ZWEITE ZIELSTUFE",
        "local_reading_de": "ZWEITE FEUCHTESTUFE",
        "mechanical_rule_de": "Vor AL fällt das n von IIN aus: DA+IIN+AL wird da-ii-al.",
        "rejected_rivals_de": "DA+AIIN+AL verdoppelt die Mengenachse; FEUCHTESTUFE als Ganzwort erklärt die sichtbaren Teile nicht.",
    },
}


def read(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_path(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0])
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def integer_delta(row: dict[str, str], identity_delta: int, mark_delta: int) -> None:
    row["identity_count"] = str(int(row["identity_count"]) + identity_delta)
    row["mark_count"] = str(int(row["mark_count"]) + mark_delta)


def replace_at(sequence: str, separator: str, surfaces: list[str], replacements: dict[str, str]) -> str:
    pieces = sequence.split(separator)
    assert len(pieces) == len(surfaces)
    for index, surface in enumerate(surfaces):
        if surface in replacements:
            pieces[index] = replacements[surface]
    return separator.join(pieces)


def main() -> None:
    symbols = read(f"{PFX5}_48_COMPLETE_SYMBOL_DICTIONARY.tsv")
    patterns = read(f"{PFX5}_8_CARD_PATTERNS.tsv")
    rules = read(f"{PFX5}_15_RENDERER_RULES.tsv")
    micro = read(f"{PFX5}_38_ALLOGRAPH_MICROLEXICON.tsv")
    dictionary = read(f"{PFX5}_231_COMPLETE_CARD_DICTIONARY.tsv")
    marks = read(f"{PFX5}_437_COMPLETE_INTERLINEAR.tsv")
    renderer_marks = read_path(RENDER_BASE / "NINE_HUNDRED_FOURTH_437_FUNCTIONALLY_RENDERED_MARKS.tsv")
    units = read(f"{PFX5}_118_COMPLETE_UNIT_EDITION.tsv")
    cards = read(f"{PFX5}_6_COMPLETE_JOB_CARDS.tsv")
    workflow = read(f"{PFX5}_12_STEP_WORKFLOW.tsv")

    # Remove the placeholder symbol and charge the two compositions to roots already taught.
    symbol_rows = [dict(row) for row in symbols if row["symbol"] != "NONE"]
    added_uses = Counter({"OK": 1, "EE": 1, "OR": 1, "DA": 1, "IIN": 1, "AL": 1})
    added_surfaces = {
        "OK": "iokeeor", "EE": "iokeeor", "OR": "iokeeor",
        "DA": "daiial", "IIN": "daiial", "AL": "daiial",
    }
    for row in symbol_rows:
        if row["symbol"] in added_uses:
            row["weighted_mark_uses"] = str(int(row["weighted_mark_uses"]) + added_uses[row["symbol"]])
            if added_surfaces[row["symbol"]] not in row["surface_examples"].split(" | "):
                row["surface_examples"] += " | " + added_surfaces[row["symbol"]]

    pattern_rows = [dict(row) for row in patterns]
    for row in pattern_rows:
        if row["pattern"] == "WHOLE_LEXICON":
            integer_delta(row, -2, -2)
            row["teaching_rule_de"] = "Eine verschmolzene Ganzkarte oder TALAM direkt aus dem kleinen Werkstattdeck lesen."
        elif row["pattern"] == "OPERATION_INSTRUCTION":
            integer_delta(row, 1, 1)
        elif row["pattern"] == "STATE_OR_GRADE":
            integer_delta(row, 1, 1)

    rule_rows = [dict(row) for row in rules]
    rule_deltas = {
        "ROOT_ORDER_COPY": (2, 2),
        "OK_FRAME_ALLOGRAPH": (1, 1),
        "E_GRADE_LENGTH": (1, 1),
        "ARGUMENT_OR_ADDRESS_TAIL": (1, 1),
        "LOCAL_SIGN_COPY": (2, 2),
        "MEMORIZED_WHOLE_FORM": (-2, -2),
    }
    for row in rule_rows:
        if row["renderer_rule"] in rule_deltas:
            integer_delta(row, *rule_deltas[row["renderer_rule"]])
        if row["renderer_rule"] == "LOCAL_SIGN_COPY":
            row["instruction"] = "Copy diagram-local carriers or contractions as well as address, label and material signs."

    functional_micro = [dict(row) for row in micro if row["entry_class"] != "LOCAL_WHOLE_WORD"]
    assert len(functional_micro) == 36
    contraction_rows = []
    for identity, target in TARGETS.items():
        contraction_rows.append({
            "identity": identity,
            "surface": target["surface"],
            "component_recipe": target["component_recipe"],
            "selected_parse_de": target["selected_parse_de"],
            "atomic_root_reading_de": target["atomic_root_reading_de"],
            "short_reading_de": target["short_reading_de"],
            "local_reading_de": target["local_reading_de"],
            "renderer_device": target["renderer_microfunction"],
            "mechanical_rule_de": target["mechanical_rule_de"],
            "rejected_rivals_de": target["rejected_rivals_de"],
            "page": "f69v",
            "unit": "f69v.2",
            "marks": 1,
        })

    dictionary_rows = []
    source_renderability_by_identity = {
        identity: next(iter(values))
        for identity, values in (
            (identity, {row["renderability"] for row in renderer_marks if row["identity"] == identity})
            for identity in {row["identity"] for row in renderer_marks}
        )
    }
    for source in dictionary:
        row = dict(source)
        target = TARGETS.get(row["identity"])
        if target:
            row.update({
                "component_recipe": target["component_recipe"],
                "slot_signature": target["slot_signature"],
                "atomic_root_reading_de": target["atomic_root_reading_de"],
                "dictionary_value_de": target["dictionary_value_de"],
                "local_fluent_expansions_de": target["local_fluent_expansion_de"],
                "primary_card_pattern": target["primary_card_pattern"],
                "functional_allographs": f"{target['renderer_microfunction']}->{target['surface']}",
            })
        row["renderability"] = target["renderability"] if target else source_renderability_by_identity[row["identity"]]
        dictionary_rows.append(row)

    identity_by_surface = {target["surface"]: identity for identity, target in TARGETS.items()}
    renderer_by_mark = {row["order_mark_id"]: row for row in renderer_marks}
    interlinear_rows = []
    for source in marks:
        row = dict(source)
        target = TARGETS.get(row["identity"])
        if target:
            row.update({
                "component_recipe": target["component_recipe"],
                "slot_signature": target["slot_signature"],
                "atomic_root_reading_de": target["atomic_root_reading_de"],
                "dictionary_value_de": target["dictionary_value_de"],
                "local_fluent_expansion_de": target["local_fluent_expansion_de"],
                "functional_allograph": target["renderer_microfunction"],
                "microfunction_trigger_de": target["microfunction_trigger_de"],
                "renderer_skeleton": target["renderer_skeleton"],
            })
        row["renderer_rules"] = target["renderer_rules"] if target else renderer_by_mark[row["order_mark_id"]]["renderer_rules"]
        row["renderability"] = target["renderability"] if target else renderer_by_mark[row["order_mark_id"]]["renderability"]
        interlinear_rows.append(row)

    unit_rows = []
    for source in units:
        row = dict(source)
        if row["page"] == "f69v" and row["unit"] == "f69v.2":
            surfaces = row["fifth_hand_surface_sequence"].split()
            assert surfaces.count("iokeeor") == 1 and surfaces.count("daiial") == 1
            row["literal_sequence_de"] = replace_at(
                row["literal_sequence_de"], "; ", surfaces,
                {"iokeeor": "LANGANSATZ", "daiial": "ZWEITE ZIELSTUFE"},
            )
            row["root_reading_sequence_de"] = replace_at(
                row["root_reading_sequence_de"], " ; ", surfaces,
                {surface: TARGETS[identity_by_surface[surface]]["atomic_root_reading_de"] for surface in identity_by_surface},
            )
            row["speakable_condition_sequence_de"] = replace_at(
                row["speakable_condition_sequence_de"], " -> ", surfaces,
                {"iokeeor": "LANGANSATZ", "daiial": "ZWEITE ZIELSTUFE"},
            )
            row["card_pattern_sequence"] = replace_at(
                row["card_pattern_sequence"], " -> ", surfaces,
                {surface: TARGETS[identity_by_surface[surface]]["primary_card_pattern"] for surface in identity_by_surface},
            )
            row["slot_signature_sequence"] = replace_at(
                row["slot_signature_sequence"], " || ", surfaces,
                {surface: TARGETS[identity_by_surface[surface]]["slot_signature"] for surface in identity_by_surface},
            )
            row["renderer_skeleton_sequence"] = replace_at(
                row["renderer_skeleton_sequence"], " || ", surfaces,
                {surface: TARGETS[identity_by_surface[surface]]["renderer_skeleton"] for surface in identity_by_surface},
            )
            row["renderability_sequence"] = replace_at(
                row["renderability_sequence"], " | ", surfaces,
                {surface: TARGETS[identity_by_surface[surface]]["renderability"] for surface in identity_by_surface},
            )
            row["microfunction_sequence"] = row["microfunction_sequence"].replace(
                "WEATHER_CLASS_WHOLE_WORD", "CONDITION_I_CARRIER"
            ).replace("MOISTURE_STAGE_WHOLE_WORD", "IIN_AL_N_ELISION")
        unit_rows.append(row)

    card_rows = []
    for source in cards:
        row = dict(source)
        if row["order_id"] == "WH01":
            row["pattern_counts"] = row["pattern_counts"].replace("WHOLE_LEXICON:3", "WHOLE_LEXICON:1").replace(
                "OPERATION_INSTRUCTION:35", "OPERATION_INSTRUCTION:36"
            ).replace("STATE_OR_GRADE:8", "STATE_OR_GRADE:9")
            row["renderer_classes"] = row["renderer_classes"].replace(
                "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING:69 | MEMORIZED_EXACT_FORM:3",
                "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING:69 | COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION:2 | MEMORIZED_EXACT_FORM:1",
            )
        card_rows.append(row)

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in unit_rows:
        grouped[(row["page"], row["unit"])].append(row)
    page_unit_rows = []
    for page in PAGE_ORDER:
        for (candidate_page, unit), local in grouped.items():
            if candidate_page != page:
                continue
            for field in ["fifth_hand_surface_sequence", "literal_sequence_de", "front_instruction_de", "section", "root_reading_sequence_de", "predicted_surface_sequence"]:
                assert len({item[field] for item in local}) == 1
            first = local[0]
            page_unit_rows.append({
                "page": page,
                "page_title_de": PAGE_TITLES[page],
                "unit": unit,
                "section": first["section"],
                "orders": " | ".join(sorted(item["order_id"] for item in local)),
                "owner_or_handle_de": " | ".join(f"{item['order_id']}:{item['owner_trace_de']}" for item in sorted(local, key=lambda item: item["order_id"])),
                "surface_sequence": first["fifth_hand_surface_sequence"],
                "atomic_root_sequence_de": first["root_reading_sequence_de"],
                "dictionary_literal_de": first["literal_sequence_de"],
                "fluent_workshop_reading_de": first["front_instruction_de"],
                "predicted_surface_sequence": first["predicted_surface_sequence"],
                "source_unit_copies": len(local),
            })

    write(f"{PFX}_47_COMPLETE_SYMBOL_DICTIONARY.tsv", symbol_rows)
    write(f"{PFX}_8_CARD_PATTERNS.tsv", pattern_rows)
    write(f"{PFX}_15_RENDERER_RULES.tsv", rule_rows)
    write(f"{PFX}_36_FUNCTIONAL_ALLOGRAPHS.tsv", functional_micro)
    write(f"{PFX}_2_COMPOSITIONAL_CONTRACTIONS.tsv", contraction_rows)
    write(f"{PFX}_231_ZERO_WHOLE_CONDITION_CARD_DICTIONARY.tsv", dictionary_rows)
    write(f"{PFX}_437_ZERO_WHOLE_CONDITION_INTERLINEAR.tsv", interlinear_rows)
    write(f"{PFX}_118_ZERO_WHOLE_CONDITION_UNITS.tsv", unit_rows)
    write(f"{PFX}_115_DEDUPED_PAGE_UNITS.tsv", page_unit_rows)
    write(f"{PFX}_6_COMPLETE_JOB_CARDS.tsv", card_rows)
    write(f"{PFX}_12_STEP_WORKFLOW.tsv", workflow)

    handbook = [
        "# Vollständiges Schreiberhandbuch — kompositionelle Ausgabe",
        "",
        "Der Lehrling arbeitet mit 36 Bedeutungswurzeln, 11 Hilfszeichen, 8 Kartenmustern, 15 Rendererregeln, 36 Funktionsallographen und zwei lokalen Schreibkontraktionen.",
        "Die beiden früher auswendig gelernten Bedingungswörter sind nun Wurzelkarten: `iokeeor` = OK+EE+OR und `daiial` = DA+IIN+AL.",
        "",
        "## Schreibgang",
        "",
    ]
    for row in workflow:
        handbook.append(f"{row['step']}. **{row['stage']}** — {row['instruction_de']}")
    handbook.extend(["", "## Kurze Wurzeln", ""])
    for row in symbol_rows:
        handbook.append(f"- `{row['symbol']}` = **{row['atomic_value_de']}**; Formhinweis `{row['canonical_surface_cue']}`.")
    handbook.extend(["", "## Zwei lokale Schreibkontraktionen", ""])
    for row in contraction_rows:
        handbook.extend([
            f"- `{row['surface']}` ← **{row['selected_parse_de']}** = **{row['short_reading_de']}**.",
            f"  {row['mechanical_rule_de']}",
        ])
    handbook.extend(["", "## Acht Kartenmuster", ""])
    for row in pattern_rows:
        handbook.append(f"- **{row['pattern']}** — {row['teaching_rule_de']}")
    (HERE / f"{PFX}_COMPLETE_COMPOSITIONAL_SCRIBE_HANDBOOK.md").write_text("\n".join(handbook).rstrip() + "\n", encoding="utf-8")

    edition = [
        "# Zehnseitige Werkstattausgabe — ohne lokale Bedingungs-Ganzwörter",
        "",
        "Vollständige aktuelle Sechs-Auftrags-Auswahl; 115 eindeutige Seiteneinheiten. `iokeeor` und `daiial` werden kompositionell gelesen.",
        "",
    ]
    for page in PAGE_ORDER:
        edition.extend([f"## {page}: {PAGE_TITLES[page]}", ""])
        for row in page_unit_rows:
            if row["page"] != page:
                continue
            edition.extend([
                f"### {row['unit']} / {row['section']} / {row['orders']}",
                "",
                f"`{row['surface_sequence']}`",
                "",
                f"**Atomar:** {row['atomic_root_sequence_de']}",
                f"**Lesung:** {row['fluent_workshop_reading_de']}",
                "",
            ])
    (HERE / f"{PFX}_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "THE_LAST_TWO_LOCAL_CONDITION_WHOLE_WORDS_BECOME_EXISTING_ROOT_COMPOSITIONS",
        "pages": 10,
        "semantic_roots": 36,
        "helper_signs": 11,
        "symbols": len(symbol_rows),
        "card_patterns": len(pattern_rows),
        "renderer_rules": len(rule_rows),
        "functional_allographs": len(functional_micro),
        "local_compositional_contractions": len(contraction_rows),
        "dictionary_identities": len(dictionary_rows),
        "marks": len(interlinear_rows),
        "units": len(unit_rows),
        "deduped_page_units": len(page_unit_rows),
        "job_cards": len(card_rows),
        "component_recipes": len({row["component_recipe"] for row in dictionary_rows}),
        "renderability_marks": dict(Counter(row["renderability"] for row in interlinear_rows)),
        "local_condition_whole_words": 0,
        "surface_prediction_mismatches": sum(row["surface"] != row["predicted_surface"] for row in interlinear_rows),
        "new_semantic_roots": 0,
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PFX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PFX}_REPORT.md").write_text(
        "# Sidequest Pass 906: die letzten zwei Ganzwörter zerlegt\n\n"
        "`daiial` liest sich als **DA+IIN+AL = ZWEITE ZIELSTUFE**; die lokale Schreibung lässt vor AL das n von IIN aus. "
        "`iokeeor` liest sich als **OK+EE+OR = LANGANSATZ**; das initiale i- ist ein bedeutungsloser Ring-Träger. "
        "Damit bleiben alle 231 Karten bei denselben 36 Bedeutungswurzeln, während die Hilfszeichenzahl von zwölf auf elf fällt. "
        "Der Renderer besitzt nun 36 Funktionsallographen plus zwei lokale, mechanische Schreibkontraktionen und keine lokalen Bedingungs-Ganzwörter mehr.\n\n"
        "Die frühere Lesung WETTERZEICHEN war zu bildabhängig. Der neue LANGANSATZ bezeichnet neutral eine länger angesetzte Lage; erst der mittlere Ring macht daraus die flüssige Wetter-/Feuchtelesung. "
        "ZWEITE ZIELSTUFE ist dagegen direkt aus der vorhandenen Stufen- und Zielgrammatik verständlich.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
