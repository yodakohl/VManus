#!/usr/bin/env python3
"""Action-conditioned carrier nouns and bounded packet composition for GDT587."""

from __future__ import annotations

from typing import Any


OBJECT_ROOTS = ("Y", "AIIN", "AIN", "OR")
ROOT_ORDER = {root: ordinal for ordinal, root in enumerate(OBJECT_ROOTS)}


FORMS: dict[str, dict[str, str]] = {
    "Arbeitsgut": {
        "lemma": "Arbeitsgut", "object": "das Arbeitsgut", "genitive": "des Arbeitsguts",
    },
    "Arbeitsmaterial": {
        "lemma": "Arbeitsmaterial", "object": "das Arbeitsmaterial", "genitive": "des Arbeitsmaterials",
    },
    "Arbeitsflüssigkeit": {
        "lemma": "Arbeitsflüssigkeit", "object": "die Arbeitsflüssigkeit", "genitive": "der Arbeitsflüssigkeit",
    },
    "Flüssigkeitsmenge": {
        "lemma": "Flüssigkeitsmenge", "object": "die Flüssigkeitsmenge", "genitive": "der Flüssigkeitsmenge",
    },
    "Teilmenge": {
        "lemma": "Teilmenge", "object": "die Teilmenge", "genitive": "der Teilmenge",
    },
    "Ansatz": {
        "lemma": "Ansatz", "object": "den Ansatz", "genitive": "des Ansatzes",
    },
    "Pflanzenmaterial": {
        "lemma": "Pflanzenmaterial", "object": "das Pflanzenmaterial", "genitive": "des Pflanzenmaterials",
    },
    "Pflanzenauszug": {
        "lemma": "Pflanzenauszug", "object": "den Pflanzenauszug", "genitive": "des Pflanzenauszugs",
    },
    "Auszugsmenge": {
        "lemma": "Auszugsmenge", "object": "die Auszugsmenge", "genitive": "der Auszugsmenge",
    },
    "Pflanzenportion": {
        "lemma": "Pflanzenportion", "object": "die Pflanzenportion", "genitive": "der Pflanzenportion",
    },
    "Pflanzeneinheit": {
        "lemma": "Pflanzeneinheit", "object": "die Pflanzeneinheit", "genitive": "der Pflanzeneinheit",
    },
    "Pflanzenansatz": {
        "lemma": "Pflanzenansatz", "object": "den Pflanzenansatz", "genitive": "des Pflanzenansatzes",
    },
    "Arbeitseinheit": {
        "lemma": "Arbeitseinheit", "object": "die Arbeitseinheit", "genitive": "der Arbeitseinheit",
    },
    "Ringposition": {
        "lemma": "Ringposition", "object": "die Ringposition", "genitive": "der Ringposition",
    },
    "Positionswert": {
        "lemma": "Positionswert", "object": "den Positionswert", "genitive": "des Positionswerts",
    },
    "Sektoranteil": {
        "lemma": "Sektoranteil", "object": "den Sektoranteil", "genitive": "des Sektoranteils",
    },
    "Ringsegment": {
        "lemma": "Ringsegment", "object": "das Ringsegment", "genitive": "des Ringsegments",
    },
    "Stationsansatz": {
        "lemma": "Stationsansatz", "object": "den Stationsansatz", "genitive": "des Stationsansatzes",
    },
    "Badfüllung": {
        "lemma": "Badfüllung", "object": "die Badfüllung", "genitive": "der Badfüllung",
    },
    "Stationsmaß": {
        "lemma": "Stationsmaß", "object": "das Stationsmaß", "genitive": "des Stationsmaßes",
    },
    "Anwendungsportion": {
        "lemma": "Anwendungsportion", "object": "die Anwendungsportion", "genitive": "der Anwendungsportion",
    },
    "Stationseinheit": {
        "lemma": "Stationseinheit", "object": "die Stationseinheit", "genitive": "der Stationseinheit",
    },
    "Körper": {
        "lemma": "Körper", "object": "den Körper", "genitive": "des Körpers",
    },
    "Teil": {
        "lemma": "Teil", "object": "den Teil", "genitive": "des Teils",
    },
    "Badeinheit": {
        "lemma": "Badeinheit", "object": "die Badeinheit", "genitive": "der Badeinheit",
    },
    "Beckeninhalt": {
        "lemma": "Beckeninhalt", "object": "den Beckeninhalt", "genitive": "des Beckeninhalts",
    },
    "Strom": {
        "lemma": "Strom", "object": "den Strom", "genitive": "des Stroms",
    },
    "Mengenangabe": {
        "lemma": "Mengenangabe", "object": "die Mengenangabe", "genitive": "der Mengenangabe",
    },
    "Drogenmaterial": {
        "lemma": "Drogenmaterial", "object": "das Drogenmaterial", "genitive": "des Drogenmaterials",
    },
    "Arzneiauszug": {
        "lemma": "Arzneiauszug", "object": "den Arzneiauszug", "genitive": "des Arzneiauszugs",
    },
    "Dosismaß": {
        "lemma": "Dosismaß", "object": "das Dosismaß", "genitive": "des Dosismaßes",
    },
    "Zutatenportion": {
        "lemma": "Zutatenportion", "object": "die Zutatenportion", "genitive": "der Zutatenportion",
    },
    "Materialeinheit": {
        "lemma": "Materialeinheit", "object": "die Materialeinheit", "genitive": "der Materialeinheit",
    },
    "Arzneiansatz": {
        "lemma": "Arzneiansatz", "object": "den Arzneiansatz", "genitive": "des Arzneiansatzes",
    },
    "Gefäßeinheit": {
        "lemma": "Gefäßeinheit", "object": "die Gefäßeinheit", "genitive": "der Gefäßeinheit",
    },
}


BASE_LEMMA = {
    "SOURCE_SECTION_T": {
        "Y": "Arbeitsgut", "AIIN": "Flüssigkeitsmaß", "AIN": "Portion", "OR": "Ansatz",
    },
    "HERBAL": {
        "Y": "Pflanzencharge", "AIIN": "Pflanzenauszug", "AIN": "Pflanzenportion",
        "OR": "Pflanzen- oder Arbeitseinheit",
    },
    "CELESTIAL": {
        "Y": "Ringposition", "AIIN": "Positionswert", "AIN": "Sektoranteil", "OR": "Sektoreinheit",
    },
    "BIOLOGICAL": {
        "Y": "Stationsansatz", "AIIN": "Stations- oder Badmaß", "AIN": "Anwendungsportion",
        "OR": "Becken- oder Körpereinheit",
    },
    "PHARMA": {
        "Y": "Drogencharge", "AIIN": "Dosis- oder Mengenmaß", "AIN": "Zutatenanteil",
        "OR": "Gefäß- oder Arbeitseinheit",
    },
}


HERBAL_UNIT_RULES = {
    "SH_CH_BRIDGE_HOLD", "SH_HP_EXTRACT_STEEP", "SH_HP_SOAK",
    "SH_HP_UNIT_HOLD", "SH_REST_HOLD",
}
HERBAL_WORK_UNIT_RULES = {"T_HP_FORM_SET", "T_HP_MEASURE_SET"}
PHARMA_UNIT_RULES = {
    "SH_HP_EXTRACT_STEEP", "SH_HP_SOAK", "SH_HP_UNIT_HOLD", "SH_REST_HOLD",
}
PHARMA_VESSEL_RULES = {"T_HP_FORM_SET", "T_HP_MEASURE_SET"}


def _selection(
    key: str, family: str, rationale: str, base: str, packet: bool = False
) -> dict[str, str]:
    form = FORMS[key]
    if key == base:
        disposition = "BASE_RETAINED"
    elif packet:
        disposition = "PACKET_NARROWED"
    else:
        disposition = "ACTION_NARROWED"
    return {
        "gdt587_context_family": family,
        "gdt587_lemma_de": form["lemma"],
        "gdt587_object_form_de": form["object"],
        "gdt587_genitive_form_de": form["genitive"],
        "gdt587_disposition": disposition,
        "gdt587_rationale": rationale,
    }


def choose_noun(
    register: str,
    rule: str,
    root: str,
    carrier_roots: frozenset[str],
    host_values: frozenset[str],
) -> dict[str, str]:
    """Choose one bounded occurrence noun; portable roots remain unchanged."""
    base = BASE_LEMMA[register][root]

    if register == "SOURCE_SECTION_T":
        if root == "Y":
            key = "Arbeitsmaterial" if rule in {
                "CHD_REST_PROCESS", "SH_SOURCE_REST", "S_SOURCE_SORT_OUT",
            } else "Arbeitsgut"
            return _selection(key, "SOURCE_ACTION_OBJECT", "physical source actions select material; fixing retains the broader work item", base)
        if root == "AIIN":
            key = "Arbeitsflüssigkeit" if rule in {"SH_SOURCE_REST", "S_SOURCE_SORT_OUT"} else "Flüssigkeitsmenge"
            return _selection(key, "SOURCE_LIQUID_OR_MEASURE", "resting and sorting select a working liquid; fixing selects its quantity", base)
        if root == "AIN":
            return _selection("Teilmenge", "SOURCE_PART", "the part carrier is realized as a partial quantity in source operations", base)
        return _selection("Ansatz", "SOURCE_BATCH", "the established source-register batch reading remains sufficient", base)

    if register == "HERBAL":
        if root == "Y":
            return _selection("Pflanzenmaterial", "HERBAL_MATERIAL", "the written carrier is the plant material acted on, while wet/dry state remains in the verb", base)
        if root == "AIIN":
            key = "Auszugsmenge" if rule == "T_HP_MEASURE_SET" else "Pflanzenauszug"
            return _selection(key, "HERBAL_EXTRACT_OR_MEASURE", "wet and processing heads select extract; explicit measure-setting selects extract quantity", base)
        if root == "AIN":
            return _selection("Pflanzenportion", "HERBAL_PORTION", "the existing portion reading is already action-compatible", base)
        if rule in HERBAL_UNIT_RULES:
            key, family = "Pflanzeneinheit", "HERBAL_HELD_UNIT"
        elif rule in HERBAL_WORK_UNIT_RULES:
            key, family = "Arbeitseinheit", "HERBAL_SET_UNIT"
        else:
            key, family = "Pflanzenansatz", "HERBAL_PROCESSED_BATCH"
        return _selection(key, family, "the action selects held plant unit, set work unit, or processed plant batch", base)

    if register == "CELESTIAL":
        key = {
            "Y": "Ringposition", "AIIN": "Positionswert", "AIN": "Sektoranteil", "OR": "Ringsegment",
        }[root]
        return _selection(key, "CELESTIAL_RING_ENTRY", "ring actions distinguish position, value, share, and segment", base)

    if register == "BIOLOGICAL":
        body_blockers = {
            "AL", "AR", "AIR", "L",
            "A_ADDR", "D_ADDR", "S_ADDR", "M_LOCAL",
            "O", "IIN", "DA", "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I",
            "CARRIER_Q",
        }
        body_packet = (
            (
                rule in {"SH_BIO_BATHE", "T_AFTER_SH_COOL"}
                and carrier_roots == frozenset({"Y"})
                and not (host_values & body_blockers)
            )
            or (rule == "CHD_BIO_TREAT" and carrier_roots == frozenset({"Y", "AIN"}))
        )
        if rule == "S_BIO_DIVERT":
            key = {"Y": "Strom", "AIIN": "Mengenangabe", "AIN": "Teilmenge", "OR": "Beckeninhalt"}[root]
            return _selection(key, "BIOLOGICAL_FLOW_PACKET", "diversion composes stream, amount, part, and basin content instead of listing equal objects", base, packet=True)
        if root == "Y":
            key = "Körper" if body_packet else "Stationsansatz"
            return _selection(key, "BIOLOGICAL_BODY_OR_STATION", "only clean bathing/cooling and exact body-part packets select body; mixed hosts retain station batch", base, packet=body_packet)
        if root == "AIIN":
            key = "Badfüllung" if rule == "SH_BIO_BATHE" else "Stationsmaß"
            return _selection(key, "BIOLOGICAL_BATH_OR_STATION_MEASURE", "bathing selects bath fill; other station actions retain a station measure", base)
        if root == "AIN":
            key = "Teil" if body_packet else "Anwendungsportion"
            return _selection(key, "BIOLOGICAL_PART_OR_PORTION", "AIN supplies the part atom only in the exact Y+AIN treatment packet", base, packet=body_packet)
        key = "Badeinheit" if rule == "SH_BIO_BATHE" else "Stationseinheit"
        return _selection(key, "BIOLOGICAL_BATH_OR_STATION_UNIT", "the action removes the inherited basin/body disjunction", base)

    if register == "PHARMA":
        if root == "Y":
            return _selection("Drogenmaterial", "PHARMA_MATERIAL", "the carrier is the drug material acted on; process state stays in the verb", base)
        if root == "AIIN":
            key = "Dosismaß" if rule == "T_HP_MEASURE_SET" else "Arzneiauszug"
            return _selection(key, "PHARMA_EXTRACT_OR_DOSE", "explicit measure-setting selects dose measure; other wet or physical heads select medicinal extract", base)
        if root == "AIN":
            return _selection("Zutatenportion", "PHARMA_PORTION", "the ingredient part is realized as a portion", base)
        if rule in PHARMA_UNIT_RULES:
            key, family = "Materialeinheit", "PHARMA_HELD_UNIT"
        elif rule in PHARMA_VESSEL_RULES:
            key, family = "Gefäßeinheit", "PHARMA_SET_UNIT"
        else:
            key, family = "Arzneiansatz", "PHARMA_PROCESSED_BATCH"
        return _selection(key, family, "the action selects held material unit, set vessel unit, or processed medicinal batch", base)

    raise RuntimeError(f"Unsupported register: {register}")


def carrier_root_set(rows: list[dict[str, str]]) -> frozenset[str]:
    return frozenset(row["slot_value"] for row in rows if row["slot_value"] in OBJECT_ROOTS)


def packet_rule_id(register: str, rule: str, roots: frozenset[str]) -> str:
    if register == "SOURCE_SECTION_T" and rule == "T_SOURCE_FIX" and roots == frozenset({"Y", "AIN"}):
        return "SOURCE_PART_OF_MATERIAL"
    if register == "SOURCE_SECTION_T" and rule == "S_SOURCE_SORT_OUT" and {"Y", "AIIN"} <= roots:
        return "SOURCE_LIQUID_FROM_MATERIAL"
    if register == "CELESTIAL" and rule == "T_CELESTIAL_SET" and len(roots & {"Y", "AIIN", "OR"}) >= 2:
        return "CELESTIAL_POSITION_SEGMENT_VALUE"
    if register == "BIOLOGICAL" and rule == "CHD_BIO_TREAT" and roots == frozenset({"Y", "AIN"}):
        return "BIOLOGICAL_BODY_PART"
    if register == "BIOLOGICAL" and rule == "SH_BIO_BATHE" and "AIIN" in roots:
        return "BIOLOGICAL_BATH_FILL"
    if register == "BIOLOGICAL" and rule == "S_BIO_DIVERT" and roots:
        return "BIOLOGICAL_FLOW_PACKET"
    if register in {"HERBAL", "PHARMA"} and rule == "T_HP_MEASURE_SET" and {"Y", "AIIN"} <= roots:
        return "HP_MEASURE_FOR_MATERIAL"
    if rule in {"S_HP_STRAIN", "S_HP_STRAIN_AFTER_WET_STEP"}:
        return "HP_EXTRACT_OF_MATERIAL"
    return "DEFAULT_GDT584_OBJECT_COMPOSITION"


def patch_polish(polish: Any) -> Any:
    """Patch the imported GDT584 renderer with occurrence forms and packet rules."""
    original_action_clause = polish.action_clause

    def object_phrase(_register: str, rows: list[dict[str, str]]) -> str:
        values: list[str] = []
        seen: set[str] = set()
        for row in rows:
            root = row["slot_value"]
            if root not in OBJECT_ROOTS or root in seen:
                continue
            seen.add(root)
            values.append(row["gdt587_object_form_de"])
        return polish.join_de(values)

    def material_phrase(_register: str, rows: list[dict[str, str]]) -> str:
        by_root = {row["slot_value"]: row for row in rows if row["slot_value"] in OBJECT_ROOTS}
        for root in ("Y", "AIN", "OR"):
            if root in by_root:
                return by_root[root]["gdt587_object_form_de"]
        return ""

    def finish(base: str, rows: list[dict[str, str]], suffix: str = "") -> str:
        tail = polish.modifier_values(rows, excluded=set(OBJECT_ROOTS))
        result = polish.with_modifiers(base, tail)
        return f"{result} {suffix}" if suffix else result

    def action_clause(action: dict[str, str], rows: list[dict[str, str]], register: str) -> str:
        rule = action["gdt584_rule_id"]
        roots = carrier_root_set(rows)
        by_root = {row["slot_value"]: row for row in rows if row["slot_value"] in OBJECT_ROOTS}

        if rule in {"S_HP_STRAIN", "S_HP_STRAIN_AFTER_WET_STEP"}:
            extract = by_root.get("AIIN")
            material = next((by_root[root] for root in ("Y", "AIN", "OR") if root in by_root), None)
            base = f"Seihe {extract['gdt587_object_form_de']}" if extract else "Seihe den Auszug"
            if material:
                if material["slot_value"] == "AIN":
                    source = (
                        "aus der Pflanzenportion" if register == "HERBAL"
                        else "aus der Zutatenportion"
                    )
                    base += f" {source}"
                elif material["slot_value"] == "OR":
                    source = (
                        "aus dem Pflanzenansatz" if register == "HERBAL"
                        else "aus dem Arzneiansatz"
                    )
                    base += f" {source}"
                else:
                    base += f" {material['gdt587_genitive_form_de']}"
            return finish(base, rows, "ab")

        if register == "SOURCE_SECTION_T" and rule == "T_SOURCE_FIX" and roots == frozenset({"Y", "AIN"}):
            return finish("Lege die Teilmenge des Arbeitsmaterials", rows, "fest")

        if register == "SOURCE_SECTION_T" and rule == "S_SOURCE_SORT_OUT" and {"Y", "AIIN"} <= roots:
            return finish("Sondere die Arbeitsflüssigkeit vom Arbeitsmaterial", rows, "aus")

        if register == "CELESTIAL" and rule == "T_CELESTIAL_SET" and roots <= {"Y", "AIIN", "OR"} and len(roots) >= 2:
            if "Y" in roots:
                target = "die Ringposition"
                if "OR" in roots:
                    target += " des Ringsegments"
            else:
                target = "das Ringsegment"
            if "AIIN" in roots:
                target += " auf den Positionswert"
            return finish(f"Stelle {target}", rows, "ein")

        if register == "BIOLOGICAL" and rule == "CHD_BIO_TREAT" and roots == frozenset({"Y", "AIN"}):
            return finish("Behandle den Körperteil", rows)

        if register == "BIOLOGICAL" and rule == "SH_BIO_BATHE" and "AIIN" in roots:
            if "Y" in roots:
                return finish("Halte den Stationsansatz im Bad bei der angegebenen Füllung", rows)
            return finish("Halte die Badfüllung", rows)

        if register == "BIOLOGICAL" and rule == "S_BIO_DIVERT" and roots:
            if {"OR", "AIIN"} <= roots:
                target = "die angegebene Menge des Beckeninhalts"
                if "AIN" in roots:
                    target = "die angegebene Teilmenge des Beckeninhalts"
                if "Y" in roots:
                    target += " als Strom"
            elif {"AIIN", "AIN"} <= roots:
                target = "die angegebene Teilmenge"
            elif {"Y", "AIN"} <= roots:
                target = "den Teilstrom"
            elif {"Y", "OR"} <= roots:
                target = "den Beckeninhalt als Strom"
            elif "Y" in roots:
                target = "den Strom"
            elif "OR" in roots:
                target = "den Beckeninhalt"
            elif "AIN" in roots:
                target = "die Teilmenge"
            else:
                target = "die angegebene Menge"
            return finish(f"Leite {target}", rows, "um")

        if register in {"HERBAL", "PHARMA"} and rule == "T_HP_MEASURE_SET" and {"Y", "AIIN"} <= roots:
            target = by_root["AIIN"]["gdt587_object_form_de"]
            material = by_root["Y"]["gdt587_object_form_de"]
            return finish(f"Stelle {target} für {material}", rows, "ein")

        return original_action_clause(action, rows, register)

    polish.object_phrase = object_phrase
    polish.material_phrase = material_phrase
    polish.action_clause = action_clause
    return polish
