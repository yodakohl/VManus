#!/usr/bin/env python3
"""Build the creative state/product layer over the Biological operation edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_biological_operation_completion"

DICT_IN = BASE / "SELECTED_173_BIOLOGICAL_OPERATION_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_BIOLOGICAL_OPERATION_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_BIOLOGICAL_OPERATION_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_STATE_PRODUCT_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_STATE_PRODUCT_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_STATE_PRODUCT_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_STATE_PRODUCT_RECORDS.md"
PARADIGM_OUT = HERE / "STATE_PRODUCT_PARADIGM.tsv"
REGISTER_OUT = HERE / "STATE_PRODUCT_REGISTER.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rev(seg: str, nucleus: str, gloss: str, context: str, family: str, mnemonic: str, reason: str) -> dict[str, str]:
    return {
        "seg": seg,
        "nucleus": nucleus,
        "gloss": gloss,
        "context": context,
        "family": family,
        "mnemonic": mnemonic,
        "reason": reason,
    }


REVISIONS = {
    # Product, not state: four contexts all accept a clear working liquid.
    "b5df9126607030b95175": rev(
        "SHEY_CLEAR_LIQUID_WHOLE",
        "SHEY=Klarflüssigkeit",
        "Klarflüssigkeit",
        "Nimm die Klarflüssigkeit",
        "CLEAR_PRODUCT",
        "LIQUOR CLARUS",
        "The recurrent card names the recovered liquid; extract identity is local to Herbal H3.",
    ),
    # State, not product: this card sits between READY and COLLECT.
    "d788d8d72d41b25a3c71": rev(
        "CHEALROR_CLEAR_STATE_WHOLE",
        "CHEALROR=klar",
        "klar",
        "Warte, bis der Posten klar ist",
        "CLEAR_STATE",
        "CLARUM",
        "Replace the abstract noun 'clarity point' with the state checked at that point.",
    ),
    # ROL and LOL now share one simple state word.
    "1496a731803a9f48d2e1": rev(
        "ROL_WARM_STATE_WHOLE",
        "ROL=warm",
        "warm",
        "Halte den Posten warm",
        "WARM_STATE",
        "CALIDUM",
        "Remove the discourse word 'still'; sequence supplies continuation.",
    ),
    # Narrower ready-for-contact temperature state.
    "cb57b696b815fdef9cb7": rev(
        "SHECTHY_HANDWARM_STATE_WHOLE",
        "SHECTHY=handwarm",
        "handwarm",
        "Halte den Posten handwarm",
        "HANDWARM_STATE",
        "TEPIDUM",
        "Use a concrete workshop temperature instead of the modern broad word 'tempered'.",
    ),
    # Convert a noun-like mini-sentence to a portable action.
    "883a6708116c342cb10b": rev(
        "SKAR_WARM_POUR_WHOLE",
        "SKAR=warm ausgießen",
        "warm ausgießen",
        "Gieße warm aus",
        "WARM_POUR_ACTION",
        "EFFUNDE CALIDUM",
        "The card occupies an action slot; use the verb rather than the noun 'warm pour'.",
    ),
}


SENTENCE_REWRITES = {
    "H3-S001": "Bereite aus dem Blütenkraut einen Weinsud, wringe ihn aus, lass ihn für das Standmaß stehen, seih nach, nimm die Klarflüssigkeit und kühle sie ab",
    "B1-S002": "Stelle das Sollmaß ein, lass Beckenwasser zu, setze dort an, gib eine weitere Portion und Badzusatz hinzu, halte den Fortsetzungsansatz warm, führe ihn weiter, halte die Sollmenge dort länger, leite sie durch, setze sie um und schließe",
    "B2-S010": "Setze länger an, führe den Posten durch die Düse und nimm die Klarflüssigkeit",
    "B2-S012": "Ziehe den Posten ab, nimm die Klarflüssigkeit, halte sie kurz bereit, setze sie länger an der Nassstelle nach Sollmaß an, führe sie vollständig aus und schließe",
    "B3-S021": "Stelle das Sollmaß ein, halte bereit, führe dorthin, lass den Posten absetzen, bis er handwarm ist, führe ihn erneut dorthin, stelle bereit, setze dort um und schließe",
    "B3-S026": "Stelle das Sammelbecken bereit, warte bis zum Absetzstand, setze um, gib eine Portion zu, halte bereit, warte, bis der Posten klar ist, sammle länger und schließe",
    "B4-S015": "Gib eine Portion zu, nimm die Klarflüssigkeit, halte eine Portion für die angegebene Dauer, sammle kurz, führe ab und schließe",
    "B4-S016": "Gib eine weitere Portion dorthin, gieße sie warm aus, lass absetzen und schließe",
}


REGISTER = [
    ("RAW_STATE", "QEKY", "ROH", "CRUDUM", "untreated input state"),
    ("WARM_STATE", "ROL / LOL", "WARM", "CALIDUM", "general warm state; two learned cards"),
    ("HANDWARM_STATE", "SHECTHY", "HANDWARM", "TEPIDUM", "ready-for-contact temperature"),
    ("READY_STATE", "CTH+Y", "BEREIT", "PARATUM", "current item ready"),
    ("READY_HOLD", "CTH+E+Y", "KURZ BEREITHALTEN", "SERVA PARATUM", "brief ready hold"),
    ("SETTLE_STATE", "SHED", "ABSETZEN", "DEPONE", "settling operation"),
    ("CLEAR_STATE", "CHEALROR", "KLAR", "CLARUM", "state checked before collection"),
    ("WATER_MEDIUM", "AIR", "WASSER", "AQUA", "productive water core"),
    ("BASIN_WATER", "K+AIR", "BECKENWASSER", "AQUA LABRI", "water under basin hull"),
    ("WARM_WATER", "RSHEAL", "WARMWASSER", "AQUA CALIDA", "learned whole medium sign"),
    ("RINSE_WATER", "TSHEY", "SPÜLWASSER", "AQUA LOTIONIS", "learned whole medium sign"),
    ("FRESH_WATER", "DSHEDY", "FRISCHWASSER", "AQUA RECENS", "learned whole medium sign"),
    ("ADDITIVE", "DL", "BADZUSATZ", "ADDITAMENTUM", "learned bath additive sign"),
    ("BATCH", "OR", "ANSATZ", "COMPOSITUM", "productive working batch"),
    ("EXTRACT", "CHEO", "AUSZUG", "EXTRACTUM", "intermediate extract"),
    ("CLEAR_PRODUCT", "SHEY", "KLARFLÜSSIGKEIT", "LIQUOR CLARUS", "clear recovered working liquid"),
    ("WINE_DECOCTION", "SCHOAL", "WEINSUD", "DECOCTUM IN VINO", "learned Herbal product sign"),
    ("DRAUGHT", "KCHY", "TRANK", "POTUS", "learned Herbal product sign"),
    ("WARM_POUR", "SKAR", "WARM AUSGIESSEN", "EFFUNDE CALIDUM", "learned action sign"),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentence_base = {row["statement_id"]: row for row in read_tsv(SENTENCE_IN)}
    if (len(dictionary), len(events), len(sentence_base)) != (173, 381, 116):
        raise AssertionError("unexpected input dimensions")

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row.update(
            state_product_previous_segmentation=original["semantic_segmentation"],
            state_product_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            state_product_previous_gloss_de=original["concrete_word_reading_de"],
            state_product_revision="UNCHANGED",
            state_product_family="CARRIED_FORWARD",
            state_product_mnemonic="",
            state_product_reason="Biological operation edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "STATE_PRODUCT__" + chosen["family"]
            row["local_expansion_examples_de"] = "Stoff-/Zustandsfassung: " + chosen["context"]
            row["state_product_revision"] = "REVISED"
            row["state_product_family"] = chosen["family"]
            row["state_product_mnemonic"] = chosen["mnemonic"]
            row["state_product_reason"] = chosen["reason"]
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            state_product_previous_segmentation=original["semantic_segmentation"],
            state_product_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            state_product_previous_gloss_de=original["concrete_word_reading_de"],
            state_product_previous_context_de=original["contextual_event_reading_de"],
            state_product_revision="UNCHANGED",
            state_product_family="CARRIED_FORWARD",
            state_product_reason="Biological operation edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["state_product_revision"] = "REVISED"
            row["state_product_family"] = chosen["family"]
            row["state_product_reason"] = chosen["reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    out_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["state_product_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = SENTENCE_REWRITES.get(statement_id, base["workshop_sentence_de"])
        row["state_product_revised_event_count"] = str(len(changed))
        row["state_product_families"] = "|".join(OrderedDict.fromkeys(event["state_product_family"] for event in changed)) or "CARRIED_FORWARD"
        row["state_product_previous_card_sequence_de"] = base["card_sequence_de"]
        row["state_product_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        out_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Stoff-, Zustands- und Produktfassung — elf Records",
        "",
        "Die Werkstatt liest Material, Zustand, Prüfpunkt und fertigen Arbeitsstoff getrennt. Physische Zeilen bleiben bloßer Umbruch.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        lines.append(". ".join(row["workshop_sentence_de"].rstrip(". ") for row in rows) + ".")
        lines.extend(["", "### Einzelanweisungen", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.') }.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    base_map = {row["joint_tuple_id"]: row for row in dictionary}
    paradigm_rows = []
    for ident, chosen in REVISIONS.items():
        before = base_map[ident]
        after = dmap[ident]
        selected_events = [row for row in out_events if row["joint_tuple_id"] == ident]
        paradigm_rows.append({
            "joint_tuple_id": ident,
            "surface_family": after["surface_family"],
            "occurrences": after["occurrences"],
            "records": after["records"],
            "previous_default_de": before["concrete_word_reading_de"],
            "selected_default_de": after["concrete_word_reading_de"],
            "selected_segmentation": after["semantic_segmentation"],
            "state_or_product_family": chosen["family"],
            "workshop_mnemonic": chosen["mnemonic"],
            "event_ids": "|".join(row["event_id"] for row in selected_events),
            "statement_ids": "|".join(OrderedDict.fromkeys(row["statement_id"] for row in selected_events)),
            "workshop_reason": chosen["reason"],
        })
    register_rows = [
        {"register_role": a, "card_or_component": b, "selected_value_de": c, "ca_1420_teaching_parallel": d, "use_in_workshop": e}
        for a, b, c, d, e in REGISTER
    ]

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(PARADIGM_OUT, paradigm_rows)
    write_tsv(REGISTER_OUT, register_rows)

    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "dictionary_ids_unique": len(dmap) == 173,
        "event_ids_unique": len({row["event_id"] for row in out_events}) == 381,
        "all_cards_concrete": all(row["concrete_word_reading_de"] for row in out_dictionary),
        "all_events_readable": all(row["contextual_event_reading_de"] for row in out_events),
        "event_dictionary_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in out_events),
        "all_events_in_sentences": sum(int(row["event_count"]) for row in out_sentences) == 381,
        "revisions_exact": {row["joint_tuple_id"] for row in out_dictionary if row["state_product_revision"] == "REVISED"} == set(REVISIONS),
        "sentence_rewrites_exact": len(SENTENCE_REWRITES) == 8,
        "state_product_separated": dmap["d788d8d72d41b25a3c71"]["concrete_word_reading_de"] == "klar" and dmap["b5df9126607030b95175"]["concrete_word_reading_de"] == "Klarflüssigkeit",
        "warm_synonyms_aligned": dmap["1496a731803a9f48d2e1"]["concrete_word_reading_de"] == dmap["8c97dfde96fbc78e3355"]["concrete_word_reading_de"] == "warm",
        "only_fixed_pages": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": all(not row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(records),
            "revised_cards": len(REVISIONS),
            "revised_events": sum(row["state_product_revision"] == "REVISED" for row in out_events),
            "rewritten_sentences": len(SENTENCE_REWRITES),
            "register_rows": len(register_rows),
        },
        "working_model": "MATERIAL -> PROCESS STATE -> CLEAR CHECK -> RECOVERED PRODUCT",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, REGISTER_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "input_hashes": {path.name: sha256(path) for path in (DICT_IN, EVENT_IN, SENTENCE_IN)},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "counts": result["counts"],
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
