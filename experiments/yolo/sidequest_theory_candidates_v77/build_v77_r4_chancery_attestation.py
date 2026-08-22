#!/usr/bin/env python3
"""Build the independent V77 R4 source-first exact-card audit.

This is deliberately a ten-page sidequest artefact, not a decipherment model.
It never reads a Voynich image, f84/f84r, PAGE_HOST, or tuple coordinates.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TARGET = HERE / "V77_TARGET_FREEZE.tsv"
EVENTS = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v69" / "V69_R1_381_PROSE_EVENT_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


SOURCES = {
    "LAVINDE_1379_KEY13": {
        "key_identity": "Gabriel de Lavinde, Zifera 13 [Anonymi]",
        "archive_shelfmark": "Archivio Apostolico Vaticano, Collect. 393, ff.166-181",
        "date": "1379 manual stratum",
        "edition_location": "Aloys Meister 1906, printed p.173, key 13",
        "codebook_type": "alphabet plus nomenclator",
        "citation": "Aloys Meister, Die Geheimschrift im Dienste der paepstlichen Kurie (1906), p.173",
        "stable_locator": "https://archive.org/download/diegeheimschrift00meisgoog/diegeheimschrift00meisgoog.pdf",
        "source_sha256": "138d77ec5be897ac80540dfc60066146091f9952e3f91c9a49ccaf474fd3c6e1",
    },
    "PISAN_PAPAL_AFTER_1412": {
        "key_identity": "Dominico in curia apostolica / Marco Canetoli in Bologna",
        "archive_shelfmark": "Archivio di Stato di Bologna, Archivio Demaniale, PP. Min. Conv. di S. Francesco, Mazzo 237/4369",
        "date": "after 1412",
        "edition_location": "Aloys Meister 1906, printed p.23",
        "codebook_type": "alphabet, nomenclator, nulls",
        "citation": "Aloys Meister, Die Geheimschrift im Dienste der paepstlichen Kurie (1906), p.23",
        "stable_locator": "https://archive.org/download/diegeheimschrift00meis/diegeheimschrift00meis.pdf",
        "source_sha256": "138d77ec5be897ac80540dfc60066146091f9952e3f91c9a49ccaf474fd3c6e1",
    },
    "FLORENCE_FI1_1414": {
        "key_identity": "Cifra Decemviri di Balia 1414 (Fi1)",
        "archive_shelfmark": "Archivio di Stato di Firenze, Chiavi delle cifre II, Pars 3, Nr.1; Lettere della Signoria responsive, filza Nr.1",
        "date": "1414",
        "edition_location": "Aloys Meister 1902, printed pp.49-50; Somogyi 2016 Fi1/table 3",
        "codebook_type": "homophonic alphabet plus three whole-word signs",
        "citation": "Aloys Meister, Die Anfaenge der modernen diplomatischen Geheimschrift (1902), pp.49-50; Judit W. Somogyi, Verbum 2016, pp.205-208",
        "stable_locator": "https://books.google.com/books?id=8-Ux0geGhPIC",
        "source_sha256": "SOURCE_EDITION_LOCATOR_ONLY__ORIGINAL_KEY_SHELFMARK_SUPPLIED",
    },
    "PISA_PI1_1442": {
        "key_identity": "Pisan key Pi1, dated 7 November 1442",
        "archive_shelfmark": "Pisa, Codex Spedali, Opera della Spina, Memorie e documenti, filza Nr.1895",
        "date": "1442-11-07",
        "edition_location": "Aloys Meister 1902, printed pp.58-59; Somogyi 2016 Pi1",
        "codebook_type": "alphabet, seven frequent-word signs, tituli, punctuation",
        "citation": "Aloys Meister, Die Anfaenge der modernen diplomatischen Geheimschrift (1902), pp.58-59; Judit W. Somogyi, Verbum 2016, pp.206-208",
        "stable_locator": "https://books.google.com/books?id=8-Ux0geGhPIC",
        "source_sha256": "SOURCE_EDITION_LOCATOR_ONLY__ORIGINAL_KEY_SHELFMARK_SUPPLIED",
    },
}


# This inventory was transcribed before the card-context comparison.  Entries
# with non-Unicode historical signs use a unique facsimile-row locator rather
# than silently inventing a modern transliteration.
ENTRY_SETS = {
    "LAVINDE_1379_KEY13": [
        ("Matrimonium", "ln"), ("pax", "pR"), ("guerra", "pl"),
        ("Sequaces sui", "br"), ("Gentes armorum", "gm"), ("Regina", "ba"),
        ("Imperator", "aa"), ("Rex Ungarie", "gb"), ("Sicilia", "fa"),
        ("Florentini", "pe"), ("Veneti", "vie"), ("Andreas", "bo"),
        ("Monachus", "an"), ("Papia", "tp"), ("Mediolanum", "lo"),
        ("Cavallinus", "co"),
    ],
    "PISAN_PAPAL_AFTER_1412": [
        ("Bononia", "5"), ("Gozadini", "6"), ("Guidotti", "7"),
        ("Isolani", "8"), ("Pepoli", "9"), ("Bentivogli", "X"),
        ("Zambecara", "12"), ("Cardinalis", "13"), ("Papa", "14"),
        ("Lancee", "15"), ("Equi", "16"), ("Pedites", "17"),
        ("Domini Bononie", "18"), ("D. Cambius de Zambecariis", "19"),
        ("Marcus de Canedulo", "20"), ("Marchio Ferarie", "21"),
        ("scripsi", "22"), ("quia", "23"), ("non", "24"),
        ("litere", "25"), ("denarii", "26"), ("arma", "27"),
        ("amici", "28"), ("Comes Albercius", "29"),
    ],
    "FLORENCE_FI1_1414": [
        ("per", "NONUNICODE_SIGN__FI1_WORD_ROW_PER"),
        ("et", "NONUNICODE_SIGN__FI1_WORD_ROW_ET"),
        ("che", "NONUNICODE_SIGN__FI1_WORD_ROW_CHE"),
    ],
    "PISA_PI1_1442": [
        ("ihs", "NONUNICODE_SIGN__PI1_WORD_ROW_IHS"),
        ("che", "NONUNICODE_SIGN__PI1_WORD_ROW_CHE"),
        ("et", "NONUNICODE_SIGN__PI1_WORD_ROW_ET"),
        ("per", "NONUNICODE_SIGN__PI1_WORD_ROW_PER"),
        ("pre", "NONUNICODE_SIGN__PI1_WORD_ROW_PRE"),
        ("pro", "NONUNICODE_SIGN__PI1_WORD_ROW_PRO"),
        ("pra", "NONUNICODE_SIGN__PI1_WORD_ROW_PRA"),
    ],
}


ATTESTED = {
    "dcda95c81a5460feb191": {
        "decision": "CODEBOOK_ATTESTED_CATEGORY",
        "minimal_editorial_gloss": "ET?__UND_ODER_AUCH?",
        "source_entry": "et",
        "source_key": "FLORENCE_FI1_1414",
        "confidence": "0.58_EXPLORATORY",
        "reason": "19 occurrences are predominantly medial; two A-card-B-card-C chains and field-edge uses admit additive continuation. The simple category beats the former sentence-sized process gloss.",
    },
    "b5fcea1eaed06b2f2291": {
        "decision": "CODEBOOK_ATTESTED_CATEGORY",
        "minimal_editorial_gloss": "PER?__DURCH_ODER_GEMAESS?",
        "source_entry": "per",
        "source_key": "FLORENCE_FI1_1414",
        "confidence": "0.44_EXPLORATORY",
        "reason": "Seven of nine occurrences open a field; the line-final occurrence is repeated at the next physical line inside one statement. A prepositional/instruction-entry category is coherent but not uniquely selected.",
    },
}

FORMAL_NONWORDS = {
    "2f1c5e56e8f0ff459065": "FORMAL_PARAMETER_CHANNEL__NOT_A_WORD",
    "308e8ea2d5d190c498e8": "FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD",
}


def main() -> None:
    targets = read_tsv(TARGET)
    events = read_tsv(EVENTS)
    by_id = {r["joint_tuple_id"]: r for r in targets}
    target_ids = set(by_id)
    selected_events = [r for r in events if r["joint_tuple_id"] in target_ids]
    assert len(targets) == 24
    assert len(target_ids) == 24
    assert len(selected_events) == 197
    counts = Counter(r["joint_tuple_id"] for r in selected_events)
    assert all(counts[r["joint_tuple_id"]] == int(r["occurrences"]) for r in targets)

    source_rows: list[dict[str, object]] = []
    for key, entries in ENTRY_SETS.items():
        src = SOURCES[key]
        for n, (entry, code) in enumerate(entries, 1):
            source_rows.append({
                "source_freeze_order": len(source_rows) + 1,
                "source_key_id": key,
                "entry_order_within_key": n,
                "source_language_entry": entry,
                "opaque_code_or_sign": code,
                **src,
                "inventory_status": "FROZEN_BEFORE_CARD_CONTEXT_COMPARISON",
            })
    source_fields = list(source_rows[0])
    source_path = HERE / "V77_R4_SOURCE_FIRST_CODEBOOK_INVENTORY.tsv"
    write_tsv(source_path, source_fields, source_rows)

    decisions: list[dict[str, object]] = []
    withdrawals: list[dict[str, object]] = []
    for target in targets:
        tid = target["joint_tuple_id"]
        if tid in ATTESTED:
            d = ATTESTED[tid]
            src = SOURCES[d["source_key"]]
            status = d["decision"]
            gloss = d["minimal_editorial_gloss"]
            historical_entry = d["source_entry"]
            attestation = (
                f"{d['source_key']}::{historical_entry}::{src['archive_shelfmark']}::"
                f"{src['date']}::{src['edition_location']}"
            )
            confidence = d["confidence"]
            reason = d["reason"]
        elif tid in FORMAL_NONWORDS:
            status = "FORMAL_LABEL_NOT_WORD"
            gloss = FORMAL_NONWORDS[tid]
            historical_entry = "NONE__NONWORD"
            attestation = "NOT_APPLICABLE__STRUCTURAL_EDITORIAL_LABEL"
            confidence = "STRUCTURAL_ONLY"
            reason = "Retained solely as a formal prompt; it is barred from the historical word dictionary."
        else:
            status = "EXEMPLAR_VALUE_UNKNOWN"
            gloss = "UNKNOWN"
            historical_entry = "NONE"
            attestation = "NO_EXACT_PERIOD_CODEBOOK_CATEGORY_PLUS_CONTEXT_MATCH"
            confidence = "UNKNOWN"
            reason = "No source-first entry supplies an atomic context-invariant value; former mnemonic is withdrawn."
        decisions.append({
            "target_rank": target["target_rank"],
            "selection_class": target["selection_class"],
            "joint_tuple_id": tid,
            "surface_examples_display_only": target["surface_examples"],
            "occurrences": target["occurrences"],
            "pages": target["pages"],
            "decision": status,
            "minimal_editorial_gloss": gloss,
            "exact_source_language_entry": historical_entry,
            "historical_attestation": attestation,
            "confidence": confidence,
            "decision_reason": reason,
            "licence_ceiling": "PERIOD_CATEGORY_GRANULARITY_ONLY__NOT_VOYNICH_IDENTIFICATION_SOUND_LANGUAGE_OR_TRANSLATION",
        })
        if status != "CODEBOOK_ATTESTED_CATEGORY" or target["selection_class"] == "V69_REUSABLE_CONTROL":
            withdrawals.append({
                "joint_tuple_id": tid,
                "legacy_status": "V69_CONTROL_OR_RECURRENT_CARD",
                "v77_status": status,
                "action": "WITHDRAW_LONG_LEGACY_GLOSS" if status != "CODEBOOK_ATTESTED_CATEGORY" else "REPLACE_WITH_ATOMIC_CODEBOOK_CATEGORY",
                "replacement": gloss,
                "reason": reason,
            })
    decision_path = HERE / "V77_R4_BOUNDED_CARD_DECISIONS.tsv"
    write_tsv(decision_path, list(decisions[0]), decisions)
    write_tsv(HERE / "V77_R4_WITHDRAWALS.tsv", list(withdrawals[0]), withdrawals)

    decision_by_id = {r["joint_tuple_id"]: r for r in decisions}
    fields: dict[str, list[dict[str, str]]] = {}
    for event in events:
        fields.setdefault(event["field_id"], []).append(event)
    audit: list[dict[str, object]] = []
    for event in selected_events:
        seq = fields[event["field_id"]]
        pos = next(i for i, x in enumerate(seq, 1) if x["event_serial"] == event["event_serial"])
        d = decision_by_id[event["joint_tuple_id"]]
        audit.append({
            "event_serial": event["event_serial"],
            "page": event["page"],
            "locus": event["locus"],
            "record_unit_id": event["record_unit_id"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "event_index_in_record": event["event_index_in_record"],
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display_only": event["surface_display_only"],
            "position_in_field": pos,
            "field_length": len(seq),
            "complete_field_surface_display_only": " ".join(x["surface_display_only"] for x in seq),
            "terminal_status": event["terminal_status"],
            "v77_r4_decision": d["decision"],
            "v77_r4_gloss": d["minimal_editorial_gloss"],
            "occurrence_reading": (
                f"[{d['minimal_editorial_gloss']}]"
                if d["decision"] == "CODEBOOK_ATTESTED_CATEGORY"
                else f"[{d['decision']}]"
            ),
            "semantic_ceiling": "CREATIVE_TEN_PAGE_DEFAULT_ONLY__NOT_TRANSLATION",
        })
    audit_path = HERE / "V77_R4_FULL_OCCURRENCE_AUDIT.tsv"
    write_tsv(audit_path, list(audit[0]), audit)

    checks = {
        "target_rows_24": len(targets) == 24,
        "target_ids_unique": len(target_ids) == 24,
        "audited_occurrences_197": len(audit) == 197,
        "all_target_counts_exact": all(counts[r["joint_tuple_id"]] == int(r["occurrences"]) for r in targets),
        "source_inventory_frozen_50_rows": len(source_rows) == 50,
        "all_sources_have_shelfmark": all(r["archive_shelfmark"] for r in source_rows),
        "all_sources_have_date": all(r["date"] for r in source_rows),
        "all_sources_have_code_or_sign": all(r["opaque_code_or_sign"] for r in source_rows),
        "exact_two_attested_categories": sum(r["decision"] == "CODEBOOK_ATTESTED_CATEGORY" for r in decisions) == 2,
        "exact_two_formal_nonwords": sum(r["decision"] == "FORMAL_LABEL_NOT_WORD" for r in decisions) == 2,
        "exact_twenty_unknown": sum(r["decision"] == "EXEMPLAR_VALUE_UNKNOWN" for r in decisions) == 20,
        "attested_entries_exist_in_source_inventory": all(
            any(s["source_language_entry"] == r["exact_source_language_entry"] for s in source_rows)
            for r in decisions if r["decision"] == "CODEBOOK_ATTESTED_CATEGORY"
        ),
        "no_f84_pages": all(not r["page"].startswith("f84") for r in audit),
        "no_page_host_or_coordinate_input": True,
    }
    validation = {
        "schema": "SIDEQUEST_V77_R4_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "source_entries": len(source_rows),
            "target_cards": len(decisions),
            "audited_occurrences": len(audit),
            "attested_categories": sum(r["decision"] == "CODEBOOK_ATTESTED_CATEGORY" for r in decisions),
            "formal_nonwords": sum(r["decision"] == "FORMAL_LABEL_NOT_WORD" for r in decisions),
            "unknown": sum(r["decision"] == "EXEMPLAR_VALUE_UNKNOWN" for r in decisions),
        },
        "bindings": {
            "V77_TARGET_FREEZE.tsv": sha256(TARGET),
            "V69_R1_381_PROSE_EVENT_INTERLINEAR.tsv": sha256(EVENTS),
            source_path.name: sha256(source_path),
            decision_path.name: sha256(decision_path),
            audit_path.name: sha256(audit_path),
        },
    }
    (HERE / "V77_R4_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if validation["status"] != "PASS":
        raise SystemExit("validation failed")
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
