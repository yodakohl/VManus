#!/usr/bin/env python3
"""Build V45 R3's stem-transparent ten-page register reading.

This is a deliberately speculative sidequest transformation of frozen V43/V44
cards.  It reads no manuscript transcription and never touches f84/f84r.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V43_PROSE = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_PROSE_DICTIONARY.tsv"
V43_ALL = ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_COMPLETE_DICTIONARY.tsv"
V44_HOSTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v44/V44_R4_CARD_TO_HOST_MEANINGS.tsv"
V40_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v40/V40_REVISED_381_EVENT_LEDGER.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# Longest-prefix selection is deliberately mechanical.  It uses PAGE_HOST only
# after the V43 card has been joined, and never raw spelling similarity between
# candidate cards.  Values are workshop prompts, not linguistic morphemes.
AXES = [
    ("AIIN", ("aiiin", "aiin", "ain", "air"), "BESTIMMTER PARAMETER / MASS- ODER ADRESSWERT", "PARAMETER_AXIS"),
    ("CHOR", ("chor",), "BESCHAFFUNG ODER SAMMELZEIT", "CONTENT_STEM"),
    ("CHEY", ("chey",), "AUSGEWAEHLTER MATERIALANTEIL", "CONTENT_STEM"),
    ("CHY", ("chy",), "WARME ZUBEREITUNG ODER ANWENDUNG", "CONTENT_STEM_WEAK"),
    ("OK", ("ok",), "BEGRENZTEN ARBEITSPOSTEN AKTIVIEREN", "OPERATION_AXIS"),
    ("OT", ("ot",), "MARKIERTEN BEZUG, PARAMETER ODER WEG WAEHLEN", "RELATION_AXIS"),
    ("OR", ("or",), "BEREITETER VERWENDBARER ARBEITSBESTAND", "CONTENT_STEM"),
    ("EY", ("ey",), "GEFORDERTEN BEOBACHTBAREN ENDZUSTAND ERREICHEN", "STATE_AXIS"),
    ("CH", ("ch",), "ARBEITSZUSTAND VERAENDERN ODER UMLEITEN", "TRANSFORMATION_AXIS"),
    ("L", ("l",), "FORTSETZUNGS-, EMPFAENGER- ODER TRANSFERWEG", "TRANSFER_AXIS"),
    ("Y", ("y",), "AKTUELLEN RECORDTRAEGER ODER ZUSTAND FUHREN", "STATE_CARRIER_AXIS"),
    ("E", ("e",), "ZUSTAND, SCHWELLE ODER EINTRITT", "STATE_AXIS_GENERIC"),
    ("K", ("k",), "MATERIAL-, GEFAESS- ODER MITTELWERT", "LOCAL_VALUE_AXIS"),
    ("O", ("o",), "FOLGEPOSTEN ODER ARBEITSBESTAND", "ITEM_AXIS_GENERIC"),
    ("R", ("r",), "FORTGANG ODER RESULTATBEZUG", "SEQUENCE_AXIS"),
    ("S", ("s",), "RELATION ODER GLEICHSETZUNG", "RELATION_AXIS_GENERIC"),
    ("D", ("d",), "RUECK- ODER ZEIGEVERWEIS", "REFERENCE_AXIS"),
    ("P", ("p",), "PASSAGE ODER UEBERGABE", "TRANSFER_AXIS_GENERIC"),
    ("F", ("f",), "PRESS-, FILTER- ODER DURCHGANGSWERT", "FILTER_AXIS"),
    ("H", ("h",), "LOKALER TEIL- ODER OBJEKTWERT", "LOCAL_VALUE_AXIS"),
    ("T", ("t",), "GLEICHMAESSIGER ARBEITS- ODER ZUSTANDSWERT", "CONSTRUCTION_AXIS"),
    ("C", ("c",), "LOKALER KONSTRUKTIONSWERT", "CONSTRUCTION_AXIS"),
    ("A", ("a",), "LOKALER ADRESS- ODER RELATIONSWERT", "ADDRESS_AXIS"),
]


ARGUMENTS = {
    "APPLICATION_PHRASE": "ORT / GEFAESS / OEFFNUNG / ZEITPARAMETER",
    "COMMITTED_TECHNICAL_INSTRUCTION": "LOKALER ARBEITSSCHRITT + ZELLSCHLUSS",
    "APPLICATION_CLAUSE_HEAD": "NEUER ANWENDUNGS- ODER TRANSFERGANG",
    "PREPARATION_ACTION": "GEZEIGTES MATERIAL / ARBEITSMEDIUM",
    "APPLICATION_CLAUSE_END": "ZIEL ODER ERREICHTER FOLGEZUSTAND",
    "PLANT_PART": "BILDLOKALER PFLANZENTEIL",
    "MEDIUM": "LOKALES ARBEITSMITTEL",
    "APPLICATION": "BILDLOKALE ANWENDUNGSSTELLE",
    "GATHERING_TIME": "BILDOWNER + SAISON / ENTWICKLUNGSSTUFE",
    "STORAGE": "RESTBESTAND + AUFBEWAHRUNGSWEISE",
    "CLAUSE_CLOSURE": "VORHERIGER ARBEITSGANG",
    "INDICATION": "LOKALE PRUEFUNG / VERWENDUNGSZWECK",
    "PROCESS_CONDITION": "BEOBACHTBARER ARBEITSZUSTAND",
    "HABITAT": "BILDLOKALER STANDORT",
    "PORTABLE_TECHNICAL_PHRASE": "VORHERIGER ANSATZ / CURRENT RECORD",
    "TEMPER_LUKEWARM": "ARBEITSMEDIUM + TEMPERATURBAND",
    "MEASURED_ADDITION": "ABGEMESSENER ANTEIL + GEFAESS",
    "APPARATUS_WASH_THROUGH_CLOSE": "BENUTZTE APPARATUR + ZELLSCHLUSS",
    "APPLICATION_ACTION": "MARKIERTE ANWENDUNGSSTELLE",
    "RESERVE_MIXED_LIQUID_CLOSE": "GEMISCHTER BESTAND + EMPFANGSGEFAESS",
    "CHANNEL_ROUTE": "VERBUNDENE LAEUFE",
    "SINGLE_WASH_CLOSE": "MARKIERTE STELLE + EIN DURCHGANG",
    "MEASURE_REFERENCE": "VORGESCHRIEBENER STANDARD",
    "COMBINE_PORTIONS": "ZWEI ANTEILE",
    "SETTLE_LIQUID_CLOSE": "ARBEITSFLUESSIGKEIT + RUHEZUSTAND",
    "MEASURE": "MENGE / EINHEIT",
    "SAME_PREPARED_BATCH_REFERENCE": "VORHERIGER ANSATZ",
    "DURATION_REFERENCE": "VORHERIGES ZEITMASS",
    "MIXING_ACTION": "AKTUELLER ARBEITSPOSTEN",
    "PREPARED_LIQUID": "BEREITETER ARBEITSBESTAND",
    "TEMPERED_IMMERSION_CLOSE": "EINGETAUCHTER TEIL + WARMES MEDIUM",
    "LOCAL_RINSE_CLOSE": "MARKIERTE STELLE + EIN SPUELGANG",
    "HEAT_ONCE_CLOSE": "AKTUELLER POSTEN + EIN WAERMEGANG",
    "LOWER_OUTLET_DIRECTION": "UNTERER ABLAUF",
    "MEASURED_PORTION": "ABGEMESSENER ANTEIL",
    "CLARITY_GATE": "SICHTBARER ENDZUSTAND",
    "ENTRY_INSTRUCTION": "NAECHSTER ABGEMESSENER POSTEN",
    "CURRENT_PORTION": "AKTUELLER ARBEITSPOSTEN",
    "SETTLE_READY_CLOSE": "ARBEITSPOSTEN + BEREITSCHAFTSZUSTAND",
    "REFERENCE": "GEZEIGTER OWNER",
    "CLOTH_STRAIN_CLOSE": "ARBEITSMEDIUM + TUCHWEG",
    "GENTLE_HEAT": "ARBEITSPOSTEN + SCHWACHE WAERME",
    "PREPARATION_REFERENCE": "VORHERIGER ANSATZ",
    "APPLICATION_LOCATION": "MARKIERTE ZIELSTELLE",
    "DRAIN_TO_LOWER_RECEIVER_CLOSE": "VERBRAUCHTER BESTAND + UNTERER EMPFAENGER",
    "READINESS_CONDITION": "BEREITSCHAFTSZUSTAND",
    "CLAUSE_HEAD": "NEUER VERWENDUNGSGANG",
    "FINAL_SHARE_INSTRUCTION": "MARKIERTER ANTEIL",
}


def choose_axis(host: str) -> tuple[str, str, str, str]:
    candidates = []
    for name, prefixes, value, kind in AXES:
        for prefix in prefixes:
            if host.startswith(prefix):
                candidates.append((len(prefix), name, prefix, value, kind))
    assert candidates, host
    _, name, prefix, value, kind = max(candidates)
    return name, prefix, value, kind


def normalize_closure(text: str) -> str:
    variants = (
        " und beende diesen Arbeitsschritt",
        " und beende den Arbeitsschritt",
        " und beende diesen Durchgang",
        " und beende den Schritt",
        " und schließe diesen Arbeitsgang",
        "; beende die Zelle",
        "; schließe die Zelle",
        "; schließe diesen Durchlauf",
    )
    out = text.strip()
    for variant in variants:
        out = out.replace(variant, " und schließe die Arbeitszelle")
    return out[0].upper() + out[1:] if out else out


def transparent_reading(host: str, tuple_id: str, current: str) -> str:
    # Only recurring families are rewritten.  Rare lexical arguments remain
    # explicit rather than being hallucinated out of short glyph substrings.
    if tuple_id == "2f1c5e56e8f0ff459065":
        return "Arbeite nach dem vorgeschriebenen Maß"
    if host == "or":
        return ("Verwende den bereiteten Arbeitsbestand frisch" if "frisch" in current.lower()
                else "Der bereitete verwendbare Arbeitsbestand")
    if host == "chor":
        return normalize_closure(current).replace("Vor der Blüte gesammelt", "Beschaffe den Bildowner vor der Blüte").replace(
            "Sammle die Pflanze im Frühjahr", "Beschaffe den Bildowner im Frühjahr")
    if host == "chey":
        if "Wurzel" in current:
            return "Wähle als Materialanteil die faserige untere Wurzel"
        return "Wähle den bezeichneten Materialanteil"
    if host == "ey":
        return "Arbeite bis zum geforderten sichtbaren Endzustand (hier: klarer Ablauf)"
    if host == "ok":
        if tuple_id == "3ae9a121ba0045b913e8":
            return "Aktiviere den begrenzten Arbeitsposten an der bezeichneten Stelle"
        if tuple_id == "b5fcea1eaed06b2f2291":
            return "Aktiviere den nächsten abgemessenen Arbeitsposten"
        lowered = normalize_closure(current)
        return "Aktiviere den begrenzten Arbeitsposten: " + lowered[0].lower() + lowered[1:]
    if host == "ot":
        lowered = normalize_closure(current)
        return "Nutze den markierten Bezug: " + lowered[0].lower() + lowered[1:]
    if tuple_id == "b921a237be883a820352":
        return "Führe diese Einheit als aktuellen Arbeitsposten"
    if tuple_id == "6f7ff8287eddf4da9fdb":
        return "Führe den aktuellen Arbeitsposten bis zur gleichmäßigen Mischung"
    return normalize_closure(current)


def main() -> None:
    prose = [r for r in read(V43_PROSE) if r["scope"] == "PROSE_EXACT_CARD"]
    hosts = read(V44_HOSTS)
    events = read(V40_EVENTS)
    astro = [r for r in read(V43_ALL) if r["scope"] == "ASTRO_SPATIAL_TOKEN"]
    assert len(prose) == 173 and len(hosts) == 173 and len(events) == 381 and len(astro) == 395

    prose_by_id = {r["lexicon_id"]: r for r in prose}
    host_by_id = {r["joint_tuple_id"]: r for r in hosts}
    assert set(prose_by_id) == set(host_by_id)

    lexicon = []
    for tuple_id in sorted(prose_by_id):
        p = prose_by_id[tuple_id]
        h = host_by_id[tuple_id]
        host = h["page_host"]
        axis, prefix, core_value, kind = choose_axis(host)
        extension = host[len(prefix):] or "Ø"
        closes = ("beende" in p["current_default"].lower() or "schließe" in p["current_default"].lower()
                  or all(s.endswith("dy") for s in p["surface_examples"].split("|")))
        completion = f"HOST_EXT={extension}; CELL={h['coordinate_id']}; CLOSE={'DY/COMMIT' if closes else 'OPEN'}"
        exception = p["source_class"] in {"PLANT_PART", "HABITAT"}
        if exception:
            status = "MEMORIZED_LEXICAL_EXCEPTION_WITH_SHARED_AXIS"
        elif kind in {"CONTENT_STEM", "CONTENT_STEM_WEAK"}:
            status = "SHARED_CONTENT_STEM_PLUS_COMPLETION"
        elif kind in {"OPERATION_AXIS", "RELATION_AXIS", "TRANSFER_AXIS", "STATE_CARRIER_AXIS", "TRANSFORMATION_AXIS", "STATE_AXIS"}:
            status = "SHARED_PRODUCTIVE_AXIS_PLUS_COMPLETION"
        else:
            status = "SHARED_TEMPLATIC_AXIS_PLUS_LOCAL_CARD"
        lexicon.append({
            "joint_tuple_id": tuple_id,
            "surface_examples": p["surface_examples"],
            "page_host": host,
            "core_stem_axis": axis,
            "core_surface_basis": prefix,
            "core_minimal_value_German": core_value,
            "completion_coordinate": completion,
            "local_argument_German": ARGUMENTS[p["source_class"]],
            "composition_status": status,
            "v43_reading_German": p["current_default"],
            "v45_r3_complete_reading_German": transparent_reading(host, tuple_id, p["current_default"]),
            "events": p["events"],
            "pages": p["pages"],
            "interpretive_status": "CREATIVE_REGISTER_READING_NOT_DECIPHERMENT",
        })

    by_id = {r["joint_tuple_id"]: r for r in lexicon}
    event_rows = []
    for event in events:
        card = by_id[event["exact_tuple_id"]]
        event_rows.append({
            "page": event["page"],
            "record": event["record"],
            "locus": event["locus"],
            "event_index": event["event_index"],
            "surface": event["surface"],
            "joint_tuple_id": event["exact_tuple_id"],
            "core_stem_axis": card["core_stem_axis"],
            "completion_coordinate": card["completion_coordinate"],
            "local_argument_German": card["local_argument_German"],
            "complete_reading_German": card["v45_r3_complete_reading_German"],
            "status": "SPECULATIVE_COMPLETE_EVENT_READING",
        })

    stem_counts = Counter(r["core_stem_axis"] for r in lexicon)
    stem_rows = []
    for name, prefixes, value, kind in AXES:
        subset = [r for r in lexicon if r["core_stem_axis"] == name]
        if not subset:
            continue
        stem_rows.append({
            "core_stem_axis": name,
            "surface_basis": "|".join(prefixes),
            "minimal_value_German": value,
            "axis_type": kind,
            "exact_cards": len(subset),
            "events": sum(int(r["events"]) for r in subset),
            "distinct_hosts": len({r["page_host"] for r in subset}),
            "memorized_exceptions": sum(r["composition_status"].startswith("MEMORIZED") for r in subset),
            "teaching_rule": "Kernwert beibehalten; Host-Erweiterung, exakte Zelle und lokales Argument spezifizieren die Lesung",
            "confidence": "MEDIUM" if name in {"AIIN", "OR", "OK", "OT", "L", "EY"} else "LOW",
        })

    write(OUT / "V45_R3_STEM_AXIS_LEXICON.tsv", stem_rows)
    write(OUT / "V45_R3_COMPLETE_173_CARD_LEXICON.tsv", lexicon)
    write(OUT / "V45_R3_COMPLETE_381_EVENT_TRANSLATION.tsv", event_rows)
    write(OUT / "V45_R3_ASTRO_395_LABELS_UNCHANGED.tsv", astro)

    exceptions = sum(r["composition_status"].startswith("MEMORIZED") for r in lexicon)
    shared_rule_cards = sum(
        r["composition_status"] in {
            "SHARED_CONTENT_STEM_PLUS_COMPLETION",
            "SHARED_PRODUCTIVE_AXIS_PLUS_COMPLETION",
        }
        for r in lexicon
    )
    templatic_local_cards = sum(
        r["composition_status"] == "SHARED_TEMPLATIC_AXIS_PLUS_LOCAL_CARD"
        for r in lexicon
    )
    validation = {
        "schema": "SIDEQUEST_V45_R3_REGISTER_STEMS_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "prose_cards_173": len(lexicon) == 173,
            "prose_events_381": len(event_rows) == 381,
            "astro_labels_395_unchanged": len(astro) == 395,
            "every_card_has_core": all(r["core_stem_axis"] for r in lexicon),
            "every_card_has_completion": all(r["completion_coordinate"] for r in lexicon),
            "every_card_has_local_argument": all(r["local_argument_German"] for r in lexicon),
            "every_card_has_complete_reading": all(r["v45_r3_complete_reading_German"] for r in lexicon),
            "every_event_mapped": all(r["joint_tuple_id"] in by_id for r in event_rows),
            "shared_axis_inventory": len(stem_rows),
            "meaningfully_rule_composed_cards": shared_rule_cards,
            "templatic_axis_but_local_value_cards": templatic_local_cards,
            "memorized_whole_card_exceptions": exceptions,
            "exception_fraction": round(exceptions / len(lexicon), 6),
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "axis_card_counts": dict(sorted(stem_counts.items())),
    }
    (OUT / "V45_R3_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
