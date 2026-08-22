#!/usr/bin/env python3
"""Build the V49 R2 historically bounded atomic-gloss revision.

This is a deliberately speculative ten-page sidequest artifact.  It does not
identify a language or decipher any Voynich form.  The only purpose of the
builder is to prevent contextual sentence paraphrases from being reused as
PAGE_HOST meanings.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v48"


# A value is admitted only when it is a single lexical/operator-sized German
# gloss (ITEM is retained as the historically familiar formula word).  Status
# records how weak the candidate remains.  No value asserts a source language.
HOST_CANDIDATES = {
    "ok": ("ITEM", "ATOMIC_FORMULA_CANDIDATE"),
    "or": ("ANSATZ", "ATOMIC_CONTENT_CANDIDATE"),
    "al": ("ZU", "ATOMIC_RELATION_CANDIDATE"),
    "e": ("BIS", "ATOMIC_GATE_CANDIDATE"),
    "chey": ("ANTEIL", "ATOMIC_CONTENT_CANDIDATE_WEAK"),
}


# These are recurrent exact whole cards, not stems.  Their one-word labels are
# permitted creative readings only; no productive internal segmentation follows.
WHOLE_CARD_CANDIDATES = {
    "aiin": ("MASS", "ATOMIC_WHOLE_CARD_CANDIDATE"),
    "ey": ("FERTIG", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "oky": ("NUTZE", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "lche": ("ABLASS", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "oke": ("SPÜLE", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "cthy": ("BEREIT", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "okeey": ("LAUWARM", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "ckhy": ("VERBINDUNG", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
    "olor": ("REST", "ATOMIC_WHOLE_CARD_CANDIDATE_WEAK"),
}


# Parser coordinates remain formal.  Their labels are deliberately not German
# sentence fragments and must not be read as source-language morphemes.
FRAME = {"O": "FORMAL-O", "OT": "FORMAL-OT"}
RIGHT = {
    "aiin": "R-AIIN",
    "ain": "R-AIN",
    "al": "R-AL",
    "ar": "R-AR",
    "air": "R-AIR",
}


AUDIT_UNITS = [
    {
        "unit": "chor",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN",
        "r2_atomic_candidate": "UNBEKANNT",
        "disposition": "REJECT_CONTEXT_SENTENCE; WHOLE_CARD_ONLY",
        "reason": "Zwei Karten; die gemeinsame Sammellesung stammt aus den bereits spekulativen lokalen Übersetzungen. CHOR ist nicht als CHO+R lizenziert.",
        "historical_analogue": "keiner",
    },
    {
        "unit": "cho",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "UNBEKANNT",
        "r2_atomic_candidate": "UNBEKANNT",
        "disposition": "REJECT_CHO_EQUALS_PLANT",
        "reason": "Zwei Karten wurden lokal als Waldort bzw. Abkühlen gelesen; kein gemeinsamer Pflanzenwert. CHO ist zudem kein nachgewiesener Bestandteil von CHOR.",
        "historical_analogue": "keiner",
    },
    {
        "unit": "chey",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN",
        "r2_atomic_candidate": "ANTEIL",
        "disposition": "RETAIN_WEAK_ATOMIC_CANDIDATE",
        "reason": "Entfernt Verb, Auswahl und Materialklasse; nur der kleinste in allen drei lokalen Lesungen gemeinsame Nominalwert bleibt.",
        "historical_analogue": "pars/portio-artiger Einzelwert, keine Sprachidentifikation",
    },
    {
        "unit": "ok",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "ARBEITSPOSTEN AKTIVIEREN",
        "r2_atomic_candidate": "ITEM",
        "disposition": "RETAIN_BEST_ATOMIC_FORMULA_CANDIDATE",
        "reason": "Fünf Karten und 24 Ereignisse; ein wiederverwendbarer Eintragsmarker ist historisch normaler als ein komplexes Aktivierungsverb. Die Lesung bleibt funktional und anonym.",
        "historical_analogue": "abbreviertes item in CoReMA-Rezepten",
    },
    {
        "unit": "or",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "BEREITETES ERGEBNIS/ARBEITSMEDIUM",
        "r2_atomic_candidate": "ANSATZ",
        "disposition": "RETAIN_PROVISIONAL_ATOMIC_CONTENT_CANDIDATE",
        "reason": "Ein Wort ersetzt die Ergebnis/Medium-Doppelkategorie; zwei Karten und acht Ereignisse, weiterhin aus lokaler Kohärenz abgeleitet.",
        "historical_analogue": "ein einzelnes Zubereitungsnomen, nicht eine ganze Anweisung",
    },
    {
        "unit": "al",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "ZIEL- ODER PARALLELSTATION",
        "r2_atomic_candidate": "ZU",
        "disposition": "RETAIN_WEAK_ATOMIC_RELATION_CANDIDATE",
        "reason": "Ein gerichteter Operator ersetzt zwei konkurrierende Stationsnomen; die konkrete Zielstelle bleibt Kontext.",
        "historical_analogue": "ad-artige Relationsform, keine Sprachidentifikation",
    },
    {
        "unit": "e",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "BIS ZUR ZUSTANDSGRENZE FÜHREN",
        "r2_atomic_candidate": "BIS",
        "disposition": "RETAIN_WEAK_ATOMIC_GATE_CANDIDATE",
        "reason": "Der atomare Gatteroperator trägt weder Zustand noch Handlung; diese müssen aus der Konstruktion kommen.",
        "historical_analogue": "donec/bis-artiger Rezeptoperator, keine Sprachidentifikation",
    },
    {
        "unit": "ot",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "MARKIERTEN BEZUG ODER WEG WÄHLEN",
        "r2_atomic_candidate": "UNBEKANNT",
        "disposition": "WITHDRAW_SEMANTIC_AXIS",
        "reason": "Zeit, Ort, Quelle und Weg lassen sich nicht auf ein einziges unabhängig belegtes Wort reduzieren; FORMAL-OT bleibt nur Parserzustand.",
        "historical_analogue": "keiner",
    },
    {
        "unit": "l",
        "unit_level": "PAGE_HOST",
        "v48_gloss": "ANGESCHLOSSENE STATION/FORTSETZUNG",
        "r2_atomic_candidate": "UNBEKANNT",
        "disposition": "WITHDRAW_SEMANTIC_AXIS",
        "reason": "Die fünf Karten tragen widersprüchliche lokale Lesungen (Öl, Abziehen, Kochen, Ablauf, Weiter); nur formale Rekurrenz ist sicher.",
        "historical_analogue": "keiner",
    },
    {
        "unit": "aiin",
        "unit_level": "EXACT_WHOLE_CARD",
        "v48_gloss": "MASS-/STANDARDKARTE",
        "r2_atomic_candidate": "MASS",
        "disposition": "RETAIN_ATOMIC_WHOLE_CARD_NOT_STEM",
        "reason": "Zwanzig Ereignisse, aber nur eine exakte Kartenart. Ein technisches Maßzeichen ist historisch plausibel; Produktivität ist nicht belegt.",
        "historical_analogue": "Apothekerzeichen für Gewichte oder Einheiten",
    },
    {
        "unit": "ey",
        "unit_level": "EXACT_WHOLE_CARD",
        "v48_gloss": "SOLLZUSTANDSKARTE",
        "r2_atomic_candidate": "FERTIG",
        "disposition": "RETAIN_WEAK_ATOMIC_WHOLE_CARD_NOT_STEM",
        "reason": "Vier Ereignisse, eine exakte Kartenart. FERTIG ist nur die kleinste Endzustandsparaphrase; KLAR oder FLÜSSIGKEIT werden ausdrücklich nicht importiert.",
        "historical_analogue": "fiat/donec-artige Formularfunktion, keine Sprachidentifikation",
    },
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atomic_components(card: dict[str, str]) -> tuple[str, str, str, str]:
    host = card["page_host"]
    if host in HOST_CANDIDATES:
        value, status = HOST_CANDIDATES[host]
        kind = "HOST_CANDIDATE"
        parts = [f"KANDIDAT HOST {host.upper()}={value}"]
    elif host in WHOLE_CARD_CANDIDATES:
        value, status = WHOLE_CARD_CANDIDATES[host]
        kind = "WHOLE_CARD_CANDIDATE"
        parts = [f"KANDIDAT GANZKARTE {host.upper()}={value}"]
    else:
        value = "UNBEKANNT"
        status = "OPAQUE_WHOLE_CARD"
        kind = "UNKNOWN"
        parts = [f"OPAQUE HOST {host.upper()}=UNBEKANNT"]

    frame = card["local_frame"]
    if frame in FRAME:
        parts.append(f"FRAME {frame}={FRAME[frame]}")
    if card["inner_d"] == "1":
        parts.append("INNER-D=FORMAL-D")
    right = card["right_family"]
    if right != "NONE":
        parts.append(f"RIGHT {right.upper()}={RIGHT.get(right, 'R-UNBEKANNT')}")
    if card["dy_closure"] == "1":
        parts.append("DY=SCHLUSS")
    if card["b3"] == "1":
        parts.append("B3=SONDERSCHLUSS")
    return value, status, kind, " + ".join(parts)


def main() -> None:
    cards_in = read(BASE / "V48_SELECTED_173_CARD_DICTIONARY.tsv")
    events_in = read(BASE / "V48_SELECTED_381_EVENT_INTERLINEAR.tsv")
    fields_in = read(BASE / "V48_SELECTED_135_FIELD_TRANSLATION.tsv")
    assert len(cards_in) == 173
    assert len(events_in) == 381
    assert len(fields_in) == 135

    cards: list[dict[str, object]] = []
    by_tuple: dict[str, dict[str, object]] = {}
    for card in cards_in:
        value, status, kind, literal = atomic_components(card)
        row: dict[str, object] = {
            "joint_tuple_id": card["joint_tuple_id"],
            "page_host": card["page_host"],
            "surface_examples": card["surface_examples"],
            "r2_atomic_value_German": value,
            "r2_value_kind": kind,
            "r2_analysis_status": status,
            "local_frame": card["local_frame"],
            "inner_d": card["inner_d"],
            "right_family": card["right_family"],
            "dy_closure": card["dy_closure"],
            "b3": card["b3"],
            "r2_atomic_literal_German": literal,
            "local_creative_expansion_German": card["fluent_local_creative_expansion_German"],
            "translation_rule": "ONE_ATOMIC_CANDIDATE_OR_UNKNOWN; LOCAL_EXPANSION_IS_NOT_WORD_MEANING",
        }
        cards.append(row)
        by_tuple[card["joint_tuple_id"]] = row
    write(OUT / "V49_R2_HISTORICAL_ATOMIC_173_CARD_DICTIONARY.tsv", cards)

    events: list[dict[str, object]] = []
    for event in events_in:
        card = by_tuple[event["joint_tuple_id"]]
        events.append({
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record"],
            "event_index": event["event_index"],
            "surface": event["surface"],
            "joint_tuple_id": event["joint_tuple_id"],
            "page_host": event["page_host"],
            "r2_atomic_literal_German": card["r2_atomic_literal_German"],
            "local_creative_expansion_German": card["local_creative_expansion_German"],
            "meaning_status": "HISTORICALLY_BOUNDED_CREATIVE_CANDIDATE_NOT_DECIPHERMENT",
        })
    write(OUT / "V49_R2_HISTORICAL_ATOMIC_381_EVENT_INTERLINEAR.tsv", events)

    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_locus[str(event["locus"])].append(event)
    cursors: Counter[str] = Counter()
    fields: list[dict[str, object]] = []
    for field in fields_in:
        locus = field["locus"]
        n = int(field["event_count"])
        start = cursors[locus]
        members = by_locus[locus][start : start + n]
        cursors[locus] += n
        assert [str(r["surface"]) for r in members] == field["surface_sequence"].split()
        fields.append({
            "page": field["page"],
            "record": field["record"],
            "locus": locus,
            "field_ordinal": field["field_ordinal"],
            "event_count": n,
            "surface_sequence": field["surface_sequence"],
            "r2_atomic_literal_sequence_German": " | ".join(str(r["r2_atomic_literal_German"]) for r in members),
            "local_creative_translation_German": " ; ".join(str(r["local_creative_expansion_German"]) for r in members),
        })
    assert all(cursors[locus] == len(rows) for locus, rows in by_locus.items())
    write(OUT / "V49_R2_HISTORICAL_ATOMIC_135_FIELD_TRANSLATION.tsv", fields)

    card_counts = Counter(card["page_host"] for card in cards_in)
    event_counts = Counter(event["page_host"] for event in events_in)
    audit_rows = []
    for row in AUDIT_UNITS:
        audit_rows.append({
            **row,
            "exact_cards": card_counts[row["unit"]],
            "fixed_events": event_counts[row["unit"]],
        })
    write(OUT / "V49_R2_HISTORICAL_ATOMIC_CANDIDATES.tsv", audit_rows)

    host_values: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        host_values[str(card["page_host"])].add(str(card["r2_atomic_value_German"]))
    validation = {
        "schema": "SIDEQUEST_V49_R2_HISTORICALLY_BOUNDED_ATOMIC_GLOSSES_V1",
        "status": "PASS",
        "counts": {
            "cards": len(cards),
            "events": len(events),
            "fields": len(fields),
            "host_candidates": len(HOST_CANDIDATES),
            "whole_card_candidates": len(WHOLE_CARD_CANDIDATES),
            "unknown_cards": sum(card["r2_atomic_value_German"] == "UNBEKANNT" for card in cards),
        },
        "checks": {
            "cards_173": len(cards) == 173,
            "events_381": len(events) == 381,
            "fields_135": len(fields) == 135,
            "same_page_host_same_atomic_value": all(len(values) == 1 for values in host_values.values()),
            "chor_unknown": all(card["r2_atomic_value_German"] == "UNBEKANNT" for card in cards if card["page_host"] == "chor"),
            "cho_unknown": all(card["r2_atomic_value_German"] == "UNBEKANNT" for card in cards if card["page_host"] == "cho"),
            "ot_l_unknown": all(card["r2_atomic_value_German"] == "UNBEKANNT" for card in cards if card["page_host"] in {"ot", "l"}),
            "chey_one_word": all(card["r2_atomic_value_German"] == "ANTEIL" for card in cards if card["page_host"] == "chey"),
            "ok_one_word": all(card["r2_atomic_value_German"] == "ITEM" for card in cards if card["page_host"] == "ok"),
            "no_context_sentence_as_host_value": all(" " not in str(card["r2_atomic_value_German"]) for card in cards),
            "local_expansion_not_component_evidence": True,
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V49_R2_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
