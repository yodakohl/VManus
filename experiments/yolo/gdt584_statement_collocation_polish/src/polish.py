#!/usr/bin/env python3
"""Deterministic occurrence revisions and German reader-channel rendering for GDT584."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


OBJECT_ROOTS = ("Y", "AIIN", "AIN", "OR")
GRADE_ROOTS = ("E", "EE", "EEE")
FORM_ROOTS = ("O", "IIN", "DA")
SITE_ROOTS = (
    "A_ADDR", "AM_ADDR", "D_ADDR", "S_ADDR", "Z_ADDR", "M_LOCAL",
)
RELATION_ROOTS = ("AL", "AR", "AIR", "L")


OBJECT_FORMS = {
    "SOURCE_SECTION_T": {
        "Y": "das Arbeitsgut",
        "AIIN": "das Flüssigkeitsmaß",
        "AIN": "die Portion",
        "OR": "den Ansatz",
    },
    "HERBAL": {
        "Y": "die Pflanzencharge",
        "AIIN": "den Pflanzenauszug",
        "AIN": "die Pflanzenportion",
        "OR": "die Pflanzen- oder Arbeitseinheit",
    },
    "CELESTIAL": {
        "Y": "die Ringposition",
        "AIIN": "den Positionswert",
        "AIN": "den Sektoranteil",
        "OR": "die Sektoreinheit",
    },
    "BIOLOGICAL": {
        "Y": "den Stationsansatz",
        "AIIN": "das Stations- oder Badmaß",
        "AIN": "die Anwendungsportion",
        "OR": "die Becken- oder Körpereinheit",
    },
    "PHARMA": {
        "Y": "die Drogencharge",
        "AIIN": "das Dosis- oder Mengenmaß",
        "AIN": "den Zutatenanteil",
        "OR": "die Gefäß- oder Arbeitseinheit",
    },
}

GENITIVE_FORMS = {
    "SOURCE_SECTION_T": {
        "Y": "des Arbeitsguts", "AIN": "der Portion", "OR": "des Ansatzes",
    },
    "HERBAL": {
        "Y": "der Pflanzencharge", "AIN": "der Pflanzenportion",
        "OR": "der Pflanzen- oder Arbeitseinheit",
    },
    "CELESTIAL": {
        "Y": "der Ringposition", "AIN": "des Sektoranteils", "OR": "der Sektoreinheit",
    },
    "BIOLOGICAL": {
        "Y": "des Stationsansatzes", "AIN": "der Anwendungsportion",
        "OR": "der Becken- oder Körpereinheit",
    },
    "PHARMA": {
        "Y": "der Drogencharge", "AIN": "des Zutatenanteils",
        "OR": "der Gefäß- oder Arbeitseinheit",
    },
}


WET_SIEVE_TO_STRAIN = {
    "G407-E3903", "G407-E4069", "G407-E4407",
}
STRAIN_TO_DIRECT_SIEVE = {"G407-E4226"}
STAGE_ONLY_SIEVE_SLOT = "RUNNING:G515-E0243@4"
WET_CHD = {
    "G407-E0688", "G407-E0718", "G407-E4207", "G407-E4485",
    "G515-E0183",
}
WET_EXTRACT_CHD = {
    "G407-E0727", "G407-E4166", "G407-E4403", "G407-E4566",
    "G515-E0245",
}
DRY_CONFIRMED_CHD = {"G407-E4476", "G407-E4490"}
SETTLE_BEFORE_STRAIN = {
    "G407-E0582", "G407-E0632", "G407-E4089", "G407-E4110",
    "G407-E4339", "G407-E4562", "G515-E0112", "G515-E0153",
}
WET_TAKE_OFF = {"G407-E4147", "G515-E0131"}
UNIT_ONLY_SOAK = {
    "G407-E0565", "G407-E3800", "G407-E4042", "G407-E4050",
    "G407-E4236",
}


MANUAL_STATEMENTS = (
    "G407-S001", "G407-S005", "G407-S006", "G407-S008", "G407-S009",
    "G407-S011", "G407-S012", "G407-S024", "G407-S027", "G407-S031",
    "G407-S032", "G407-S036", "G407-S040", "G407-S048", "G407-S051",
    "G407-S063", "G407-S064", "G407-S074", "G407-S077", "G407-S203",
    "G407-S215", "G407-S392", "G407-S397", "G407-S648", "G407-S650",
    "G407-S652", "G407-S653", "G407-S663", "G407-S668", "G407-S672",
    "G407-S675", "G407-S678", "G407-S685", "G407-S692", "G407-S693",
    "G407-S714", "G515-S002", "G515-S007", "G515-S008", "G515-S010",
)


def split_pipe(value: str) -> tuple[str, ...]:
    return () if value in {"", "NONE"} else tuple(value.split("|"))


def pipe(values: Iterable[str]) -> str:
    items = sorted(set(values))
    return "|".join(items) if items else "NONE"


def revise_assignment(source: dict[str, str]) -> dict[str, str]:
    """Apply the small GDT584 semantic delta to one fixed GDT583 target slot."""
    event_id = source["source_event_or_card_id"]
    slot_id = source["slot_id"]
    old_rule = source["gdt583_rule_id"]
    rule = old_rule
    gloss = source["gdt583_working_default_de"]
    sense = source["gdt583_concrete_sense_de"]
    disposition = "RETAINED"
    rationale = "GDT583 occurrence sense retained; only the reader renderer changes"

    if slot_id.startswith("RUNNING:"):
        if event_id == "G407-E3488" and source["root"] == "T":
            rule = "T_BIO_RELATION_REGULATE"
            gloss = "Reguliere"
            sense = "vom Ausgangsbecken her regulieren, ohne unbelegtes Abkühlobjekt"
            disposition = "NARROWED"
            rationale = "T hostet nur AR; der SH→T-Pfeil reicht hier nicht für Abkühlen"
        elif event_id == "G407-E4570" and source["root"] == "T":
            rule = "T_HP_LIQUID_TEMPER"
            gloss = "Temperiere"
            sense = "den nachfolgenden flüssigen Auszug temperieren und weiterbearbeiten"
            disposition = "NARROWED"
            rationale = "das folgende CHD hostet AIIN und ist kein trockener Mahlkopf"
        elif old_rule == "T_PHYSICAL_GRADE_TEMPER":
            gloss = "Temperiere"
            disposition = "REPHRASED"
            rationale = "der geschriebene Grad wird vom Argument und nicht doppelt im Verb realisiert"
        elif old_rule == "T_HP_FORM_SET":
            gloss = "Bringe in Form oder stelle die Stufe ein"
            disposition = "REPHRASED"
            rationale = "Form und Stufe werden als Argumente natürlich in die Verbklammer gesetzt"
        elif old_rule in {"T_CELESTIAL_SET", "T_HP_MEASURE_SET"}:
            gloss = "Stelle ein"
            disposition = "REPHRASED"
            rationale = "eingebautes Objektnomen entfernt; der feste Host liefert das Objekt"
        elif old_rule == "T_BIO_STATION_REGULATE":
            gloss = "Reguliere"
            disposition = "REPHRASED"
            rationale = "eingebautes Stationsnomen entfernt; der Host liefert Ort oder Objekt"
        elif old_rule == "SH_CELESTIAL_FIX":
            gloss = "Halte fest"
            disposition = "REPHRASED"
            rationale = "eingebaute Position entfernt; der feste Host liefert sie"
        elif event_id in WET_SIEVE_TO_STRAIN and source["root"] == "S":
            rule = "S_HP_STRAIN_AFTER_WET_STEP"
            gloss = "Seihe ab"
            sense = "den unmittelbar zuvor gezogenen oder eingeweichten Auszug abseihen"
            disposition = "NARROWED"
            rationale = "unmittelbarer Nassablauf hat Vorrang vor der breiteren Sieblesung"
        elif event_id in STRAIN_TO_DIRECT_SIEVE and source["root"] == "S":
            rule = "S_HP_SIEVE_DIRECT_PORTION"
            gloss = "Siebe"
            sense = "die direkt gehostete Pflanzenportion sieben"
            disposition = "NARROWED"
            rationale = "direktes AIN schlägt entferntes AIIN ohne unmittelbar nassen Vorgänger"
        elif slot_id == STAGE_ONLY_SIEVE_SLOT:
            rule = "S_HP_STAGE_SEPARATE"
            gloss = "Sondere aus"
            sense = "nach der geschriebenen Verarbeitungsstufe aussondern"
            disposition = "REVERTED_TO_BROAD"
            rationale = "IIN plus entferntes OR lizenziert kein konkretes Siebobjekt"
        elif event_id in WET_CHD and source["root"] == "CHD":
            rule = "CHD_HP_WET_TRITURATE"
            gloss = "Verreibe oder mazeriere"
            sense = "die feuchte Charge verreiben oder mazerieren"
            disposition = "NARROWED"
            rationale = "unmittelbarer Nassablauf widerspricht einer trockenen Mahlformulierung"
        elif event_id in WET_EXTRACT_CHD and source["root"] == "CHD":
            rule = "CHD_HP_WET_EXTRACT_PROCESS"
            gloss = "Verreibe oder mazeriere"
            sense = "die Charge im Auszug verreiben oder mazerieren"
            disposition = "UPGRADED_FROM_BROAD"
            rationale = "AIIN und Y bilden das nasse Gegenstück zur Materialzerkleinerung"
        elif old_rule == "CHD_HP_DRY_GRIND" and event_id in DRY_CONFIRMED_CHD:
            rule = "CHD_HP_DRY_GRIND_CONFIRMED"
            gloss = "Zerreibe"
            sense = "die zuvor getrocknete Pflanzencharge zerreiben"
            disposition = "NARROWED"
            rationale = "unmittelbarer Trockenschritt und fester Y-Host stimmen überein"
        elif old_rule == "CHD_HP_DRY_GRIND":
            rule = "CHD_HP_MATERIAL_COMMINUTE"
            gloss = "Zerkleinere"
            sense = "Pflanzen- oder Drogengut materiell zerkleinern"
            disposition = "NARROWED"
            rationale = "fehlendes AIIN stützt Materialzerkleinerung, beweist aber keine Trockenheit"
        elif (
            event_id in SETTLE_BEFORE_STRAIN
            and source["root"] == "SH"
            and (event_id != "G407-E4562" or slot_id == "RUNNING:G407-E4562@3")
        ):
            rule = "SH_HP_SETTLE_BEFORE_STRAIN"
            gloss = "Lass stehen oder absetzen"
            sense = "vor dem Abseihen stehen beziehungsweise absetzen lassen"
            disposition = "UPGRADED_FROM_BROAD"
            rationale = "der unmittelbar folgende Seihkopf liefert eine konkrete Prozessrichtung"
        elif event_id in WET_TAKE_OFF and source["root"] == "S":
            rule = "S_HP_TAKE_OFF_AFTER_WET_STEP"
            gloss = "Nimm oder sondere ab"
            sense = "nach dem Nassschritt den abgesetzten Anteil abnehmen oder absondern"
            disposition = "UPGRADED_FROM_BROAD"
            rationale = "unmittelbarer Nassvorgänger stützt Abnehmen statt beliebiges Auswählen"
        elif event_id in UNIT_ONLY_SOAK and source["root"] == "SH":
            rule = "SH_HP_UNIT_HOLD"
            gloss = "Halte"
            sense = "die Material- oder Arbeitseinheit auf der geschriebenen Stufe halten"
            disposition = "NARROWED"
            rationale = "OR allein darf im Pharmaregister nicht als einzuweichendes Gefäß gelesen werden"

    return {
        **source,
        "gdt584_rule_id": rule,
        "gdt584_working_default_de": gloss,
        "gdt584_concrete_sense_de": sense,
        "gdt584_disposition": disposition,
        "gdt584_rationale": rationale,
        "gdt584_guard": (
            "GDT583_SLOT_PRIMARY_GOVERNOR_AND_SURFACE_FIXED__"
            "COLLOCATION_OR_READER_WORDING_ONLY"
        ),
    }


def dedupe_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, str]] = []
    suppressed = 0
    for row in rows:
        key = (row["slot_value"], row["gdt584_default_de"])
        if key in seen:
            suppressed += 1
            continue
        seen.add(key)
        result.append(row)
    return result, suppressed


def join_de(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} und {items[1]}"
    return ", ".join(items[:-1]) + " und " + items[-1]


def object_phrase(register: str, rows: list[dict[str, str]]) -> str:
    values: list[str] = []
    seen: set[str] = set()
    for row in rows:
        root = row["slot_value"]
        if root not in OBJECT_ROOTS or root in seen:
            continue
        seen.add(root)
        values.append(OBJECT_FORMS[register][root])
    return join_de(values)


def material_phrase(register: str, rows: list[dict[str, str]]) -> str:
    by_root = {row["slot_value"]: row for row in rows if row["slot_value"] in OBJECT_ROOTS}
    if "Y" in by_root:
        return OBJECT_FORMS[register]["Y"]
    if "AIN" in by_root:
        return OBJECT_FORMS[register]["AIN"]
    if "OR" in by_root:
        return OBJECT_FORMS[register]["OR"]
    return ""


def modifier_values(
    rows: list[dict[str, str]], excluded: set[str] | None = None
) -> list[str]:
    excluded = excluded or set()
    order = {
        root: index for index, root in enumerate(
            (*FORM_ROOTS, *GRADE_ROOTS, "LOCAL_CHAR_F", "LOCAL_CHAR_G",
             "LOCAL_CHAR_I", "LOCAL_CHAR_B", "LOCAL_CHAR_J", "LOCAL_CHAR_Z",
             "HO", "AN", "OS", "CARRIER_Q", "D_LABEL", "G_LABEL", "S_LABEL",
             *SITE_ROOTS, *RELATION_ROOTS)
        )
    }
    candidates = [
        row for row in rows
        if row["slot_value"] not in OBJECT_ROOTS
        and row["slot_value"] not in excluded
        and row["primary_governor_kind"] != "SELF_ACTION"
        and row["slot_value"] not in {"OT", "OL", "DY", "RESUME_CARD"}
    ]
    candidates.sort(
        key=lambda row: (order.get(row["slot_value"], 999), int(row["slot_position"]), row["slot_id"])
    )
    unique, _ = dedupe_rows(candidates)
    return [row["gdt584_default_de"] for row in unique]


def with_modifiers(base: str, modifiers: list[str]) -> str:
    return base if not modifiers else f"{base} {join_de(modifiers)}"


def generic_action(root: str, register: str, obj: str, modifiers: list[str]) -> str:
    templates = {
        "SOURCE_SECTION_T": {
            "OK": ("Setze", "an"), "CH": ("Entnimm", ""),
            "K": ("Gib", "zu"), "R": ("Kennzeichne oder prüfe", ""),
            "P": ("Bringe", "ein"),
        },
        "HERBAL": {
            "OK": ("Setze", "an"), "CH": ("Entnimm", ""),
            "K": ("Gib", "zu"), "R": ("Kennzeichne oder prüfe", ""),
            "P": ("Bringe", "ein"),
        },
        "CELESTIAL": {
            "OK": ("Trage", "ein"), "CH": ("Lies", "ab"),
            "K": ("Ordne", "zu"), "R": ("Markiere", ""),
            "P": ("Setze", "ein"),
        },
        "BIOLOGICAL": {
            "OK": ("Beschicke oder bereite", "vor"), "CH": ("Entnimm oder lass", "ab"),
            "K": ("Führe", "zu"), "R": ("Kennzeichne oder prüfe", ""),
            "P": ("Wende", "an"),
        },
        "PHARMA": {
            "OK": ("Setze", "an"), "CH": ("Entnimm", ""),
            "K": ("Gib", "zu"), "R": ("Kennzeichne oder prüfe", ""),
            "P": ("Gib", "hinein"),
        },
    }
    lead, suffix = templates.get(register, {}).get(root, ("Bearbeite", ""))
    middle = f" {obj}" if obj else ""
    if modifiers:
        middle += f" {join_de(modifiers)}"
    tail = f" {suffix}" if suffix else ""
    return f"{lead}{middle}{tail}"


def action_clause(action: dict[str, str], rows: list[dict[str, str]], register: str) -> str:
    root = action["slot_value"]
    rule = action["gdt584_rule_id"]
    obj = object_phrase(register, rows)
    material = material_phrase(register, rows)
    modifiers = modifier_values(rows)
    forms = [
        row["gdt584_default_de"] for row in rows
        if row["slot_value"] in FORM_ROOTS
    ]
    forms = list(dict.fromkeys(forms))

    suffix = ""
    if rule == "T_SOURCE_FIX":
        base = f"Lege {obj}" if obj else "Lege die Arbeitsbedingung"
        suffix = "fest"
    elif rule == "T_CELESTIAL_SET":
        base = f"Stelle {obj}" if obj else "Stelle die Position"
        suffix = "ein"
    elif rule == "T_AFTER_SH_COOL":
        base = f"Lass {obj} anschließend" if obj else "Lass anschließend"
        suffix = "abkühlen"
    elif rule == "T_BIO_RELATION_REGULATE":
        base = "Reguliere anschließend"
    elif rule == "T_HP_LIQUID_TEMPER":
        base = f"Temperiere {obj}" if obj else "Temperiere den Auszug"
    elif rule == "T_HP_BEFORE_CHD_DRY":
        base = f"Trockne {obj}" if obj else "Trockne das Material"
    elif rule == "T_HP_BEFORE_SH_WARM":
        base = f"Erwärme {obj}" if obj else "Erwärme das Material"
    elif rule == "T_PHYSICAL_GRADE_TEMPER":
        base = f"Temperiere {obj}" if obj else "Temperiere"
    elif rule == "T_HP_FORM_SET":
        target = obj or "das Material"
        if len(forms) > 1:
            stage = "die Verarbeitungsstufe" if register == "HERBAL" else "die Zubereitungsstufe"
            base = f"Bringe {target} {forms[0]}; stelle anschließend {stage} ein"
        elif forms:
            base = f"Bringe {target} {forms[0]}"
        else:
            base = f"Stelle {target} ein"
    elif rule == "T_BIO_STATION_REGULATE":
        base = f"Reguliere {obj}" if obj else "Reguliere die Stationsbedingung"
    elif rule == "T_HP_MEASURE_SET":
        base = f"Stelle {obj}" if obj else "Stelle Maß oder Ort"
        suffix = "ein"
    elif rule == "T_PHYSICAL_BROAD":
        base = f"Reguliere oder temperiere {obj}" if obj else "Reguliere oder temperiere die Arbeitsbedingung"
    elif rule == "SH_CELESTIAL_FIX":
        base = f"Halte {obj}" if obj else "Halte die Position"
        suffix = "fest"
    elif rule == "SH_BIO_BATHE":
        base = f"Halte {obj} im Bad" if obj else "Halte im Bad"
    elif rule == "SH_HP_EXTRACT_STEEP":
        if material:
            base = f"Lass {material} im Auszug"
        else:
            base = "Lass den Auszug"
        suffix = "ziehen"
    elif rule == "SH_HP_SOAK":
        base = f"Weiche {material or obj or 'das Material'}"
        suffix = "ein"
    elif rule == "SH_HP_UNIT_HOLD":
        base = f"Halte {material or obj or 'die Materialeinheit'}"
    elif rule == "SH_HP_SETTLE_BEFORE_STRAIN":
        base = f"Lass {material or obj or 'den Ansatz'}"
        suffix = "stehen oder absetzen"
    elif rule == "SH_SOURCE_REST":
        base = f"Lass {obj or 'das Arbeitsgut'}"
        suffix = "ruhen"
    elif rule in {"SH_CH_BRIDGE_HOLD", "SH_REST_HOLD"}:
        base = f"Halte {obj}" if obj else "Halte den Zustand"
    elif rule in {"CHD_HP_WET_TRITURATE", "CHD_HP_WET_EXTRACT_PROCESS"}:
        target = material or obj or "die feuchte Charge"
        base = f"Verreibe oder mazeriere {target}"
        if rule == "CHD_HP_WET_EXTRACT_PROCESS" and "im Auszug" not in base:
            base += " im Auszug"
    elif rule == "CHD_HP_DRY_GRIND_CONFIRMED":
        base = f"Zerreibe {material or obj or 'die getrocknete Charge'}"
    elif rule == "CHD_HP_MATERIAL_COMMINUTE":
        base = f"Zerkleinere {material or obj or 'das Material'}"
    elif rule == "CHD_CELESTIAL_CALCULATE":
        base = f"Berechne {obj}" if obj else "Berechne den Wert"
    elif rule == "CHD_BIO_TREAT":
        base = f"Behandle {obj}" if obj else "Behandle den Ansatz"
    elif rule == "CHD_REST_PROCESS":
        base = f"Bearbeite {obj}" if obj else "Bearbeite das Material"
    elif rule in {"S_HP_STRAIN", "S_HP_STRAIN_AFTER_WET_STEP"}:
        if material:
            material_root = next(
                row["slot_value"] for row in rows
                if row["slot_value"] in {"Y", "AIN", "OR"}
            )
            base = f"Seihe den Auszug {GENITIVE_FORMS[register][material_root]}"
        else:
            base = "Seihe den Auszug"
        suffix = "ab"
    elif rule in {"S_HP_SIEVE", "S_HP_SIEVE_DIRECT_PORTION"}:
        base = f"Siebe {material or obj or 'das Material'}"
    elif rule == "S_HP_STAGE_SEPARATE":
        base = f"Sondere {material or obj or 'das Material'}"
        suffix = "aus"
    elif rule == "S_HP_TAKE_OFF_AFTER_WET_STEP":
        base = f"Nimm oder sondere {material or obj or 'den abgesetzten Anteil'}"
        suffix = "ab"
    elif rule in {"S_HP_SEPARATE", "S_SOURCE_SORT_OUT"}:
        base = f"Sondere {obj or 'das Material'}"
        suffix = "aus"
    elif rule == "S_BIO_DIVERT":
        base = f"Leite {obj or 'den Strom'}"
        suffix = "um"
    elif rule == "S_BIO_CHD_CARRIER_SELECT":
        base = f"Wähle {obj or 'den Träger'}"
        suffix = "aus"
    elif rule in {"S_CELESTIAL_SELECT", "S_REST_SELECT"}:
        base = f"Wähle {obj or 'die Einheit'}"
        suffix = "aus"
    else:
        return generic_action(root, register, obj, modifiers)

    consumed = set(OBJECT_ROOTS)
    if rule == "T_HP_FORM_SET":
        consumed.update(FORM_ROOTS)
    if rule in {"SH_HP_EXTRACT_STEEP", "CHD_HP_WET_EXTRACT_PROCESS", "S_HP_STRAIN", "S_HP_STRAIN_AFTER_WET_STEP"}:
        consumed.add("AIIN")
    tail = modifier_values(rows, excluded=consumed)
    result = with_modifiers(base, tail)
    return f"{result} {suffix}" if suffix else result


def render_group(
    rows: list[dict[str, str]], register: str
) -> tuple[str, dict[str, int | str]]:
    ordered = sorted(rows, key=lambda row: (int(row["statement_event_ordinal"]), int(row["slot_position"]), row["slot_id"]))
    action_rows = [row for row in ordered if row["primary_governor_kind"] == "SELF_ACTION"]
    if len(action_rows) > 1:
        raise RuntimeError(f"Multiple self-actions in governor {ordered[0]['primary_governor_key']}")
    packet_ids = list(dict.fromkeys(row["source_event_or_card_id"] for row in ordered))
    anchor = action_rows[0]["source_event_or_card_id"] if action_rows else packet_ids[0]
    _, suppressed = dedupe_rows(ordered)
    values = {row["slot_value"] for row in ordered}

    if action_rows:
        phrase = action_clause(action_rows[0], ordered, register)
        action_root = action_rows[0]["slot_value"]
        action_slot_id = action_rows[0]["slot_id"]
        rule_id = action_rows[0]["gdt584_rule_id"]
    elif values.intersection({"OT", "OL", "DY"}):
        if "OT" in values:
            phrase = "Beginne danach den nächsten Arbeitsgang"
            boundary = "PARAGRAPH_AFTER"
        elif "DY" in values:
            phrase = "Schließe den Arbeitsgang"
            boundary = "PARAGRAPH_AFTER"
        else:
            phrase = "Fahre im selben Arbeitsgang fort"
            boundary = "NONE"
        extras = modifier_values(ordered)
        phrase = with_modifiers(phrase, extras)
        action_root = "CONTROL"
        action_slot_id = "NONE"
        rule_id = "CONTROL_READER_REALIZATION"
        return phrase, {
            "anchor_event_id": anchor,
            "packet_event_ids": "|".join(packet_ids),
            "packet_count": len(packet_ids),
            "action_root": action_root,
            "action_slot_id": action_slot_id,
            "rule_id": rule_id,
            "slot_count": len(ordered),
            "remote_slot_count": sum(row["source_event_or_card_id"] != anchor for row in ordered),
            "deduplicated_reader_argument_count": suppressed,
            "boundary": boundary,
        }
    else:
        extras = object_phrase(register, ordered)
        tail = modifier_values(ordered)
        body = join_de(([extras] if extras else []) + tail)
        phrase = f"Verwende für den vorangehenden Arbeitsschritt {body or 'die Angabe'}"
        action_root = "FRAME"
        action_slot_id = "NONE"
        rule_id = "FRAME_READER_REALIZATION"

    return phrase, {
        "anchor_event_id": anchor,
        "packet_event_ids": "|".join(packet_ids),
        "packet_count": len(packet_ids),
        "action_root": action_root,
        "action_slot_id": action_slot_id,
        "rule_id": rule_id,
        "slot_count": len(ordered),
        "remote_slot_count": sum(row["source_event_or_card_id"] != anchor for row in ordered),
        "deduplicated_reader_argument_count": suppressed,
        "boundary": "NONE",
    }


def sentence_case(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip(" ;.")
    if not text:
        return text
    return text[0].upper() + text[1:]


def compose_paragraph(groups: list[dict[str, str]]) -> tuple[str, int]:
    paragraphs: list[list[str]] = [[]]
    for group in groups:
        phrase = sentence_case(group["gdt584_reader_clause_de"])
        if phrase:
            paragraphs[-1].append(phrase + ".")
        if group["paragraph_boundary"] == "PARAGRAPH_AFTER" and paragraphs[-1]:
            paragraphs.append([])
    paragraphs = [paragraph for paragraph in paragraphs if paragraph]
    return "\n\n".join(" ".join(paragraph) for paragraph in paragraphs), len(paragraphs)


def trace_rows(rows: list[dict[str, str]]) -> str:
    ordered = sorted(rows, key=lambda row: (int(row["statement_event_ordinal"]), int(row["slot_position"]), row["slot_id"]))
    return " ".join(
        f"[{row['slot_id']}={row['slot_value']}:{row['gdt584_default_de']}|{row['primary_governor_key']}]"
        for row in ordered
    )


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[\w/-]*\b", text, flags=re.UNICODE))


def rule_counts(assignments: list[dict[str, str]]) -> Counter[str]:
    return Counter(row["gdt584_rule_id"] for row in assignments)
