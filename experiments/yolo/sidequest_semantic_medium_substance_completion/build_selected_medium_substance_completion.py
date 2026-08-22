#!/usr/bin/env python3
"""Build the selected creative medium/substance completion.

The selected edition starts from the independent R3 material/flow candidate,
then applies the central four-role synthesis.  Only the fixed seven prose pages
are read; the three Astro pages remain unchanged and no sealed page is opened.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R3_BUILDER = HERE / "R3_BUILD_MEDIUM_SUBSTANCE.py"
R3_DICT = HERE / "R3_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
R3_EVENTS = HERE / "R3_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
R3_SENTENCES = HERE / "R3_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_MEDIUM_SUBSTANCE_RECORDS.md"
COMPONENT_OUT = HERE / "SELECTED_MEDIUM_SUBSTANCE_COMPONENTS.tsv"
PARADIGM_OUT = HERE / "SELECTED_MEDIUM_SUBSTANCE_PARADIGM.tsv"
COMPARISON_OUT = HERE / "MEDIUM_SUBSTANCE_MODEL_COMPARISON.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def selected(
    parse: str,
    nucleus: str,
    gloss: str,
    family: str,
    slots: str,
    rationale: str,
) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_MEDIUM_SUBSTANCE__" + family,
        "family": family,
        "slots": slots,
        "rationale": rationale,
    }


# Short roots are used only where their containing cards remain mutually
# readable.  Specific liquids and products otherwise stay learned whole cards.
SELECTED = {
    # AIR is the bold creative water root.  The hull supplies inlet, basin,
    # starting, conducting or closing.
    "12efe866f335461823a6": selected("CH_INLET+AIR_WATER", "AIR=Wasser", "Wasserzulauf", "AIR_WATER", "MEDIUM+FLOW_TRANSFER", "Plant preparation, vessel and collection make an aqueous inlet coherent."),
    "22fb87a5a83e5c3fb510": selected("K_BASIN+AIR_WATER", "AIR=Wasser", "Beckenwasser", "AIR_WATER", "MEDIUM", "The visible f81v pool supplies the basin role."),
    "7d2404c835b10a2c06af": selected("OK_START+AIR_WATER", "OK=in Gang setzen; AIR=Wasser", "Wasser in Gang setzen", "AIR_WATER", "MEDIUM+OPERATION+FLOW_TRANSFER", "OK supplies activation while AIR keeps its material value."),
    "b154ff779abe5f196c80": selected("S_RENDERER+CHED_LEAD+AIR_WATER", "CHED=führen; AIR=Wasser", "Wasser weiterführen", "AIR_WATER", "MEDIUM+OPERATION+FLOW_TRANSFER", "CHED supplies transfer while AIR stays water."),
    "8aedd154964a78e555d6": selected("D_RENDERER+AIR_WATER+Y_REFERENT+DY_CLOSE", "AIR=Wasser; Y=Posten; Endkarte=Schluss", "Wasserlauf schließen; Schluss", "AIR_WATER", "MEDIUM+FLOW_TRANSFER+CLOSE", "The learned terminal hull closes the water run."),

    # CHEO is the intermediate extract; SHEY below is its clarified product.
    "087a47b5423438cd6b6a": selected("CH_RENDERER+OK_ADD+CHEO_EXTRACT", "OK=zugeben; CHEO=Auszug", "Auszug zugeben", "CHEO_EXTRACT", "PREPARATION+OPERATION", "The same CHEO product can become the input to the next step."),
    "807591efc3d3f7ddbfab": selected("CHEO_EXTRACT+AR_SOURCE", "CHEO=Auszug; AR=aus", "Auszug entnehmen", "CHEO_EXTRACT", "SOURCE+PREPARATION+OPERATION", "AR supplies source direction; CHEO remains the extract."),

    # OR is a prepared batch.  HO supplies ingredient rather than plant name.
    "7a4bb8136330ee4e6e56": selected("OR_BATCH", "OR=Ansatz", "Ansatz", "OR_BATCH", "PREPARATION", "Seven events across three pages keep the same prepared-batch value."),
    "10488b911aae52b3b334": selected("OT_NEXT+OR_BATCH", "OT=nächster; OR=Ansatz", "nächster Ansatz", "OR_BATCH", "PREPARATION", "OT supplies order."),
    "dec401773c1f0347793d": selected("OL_PREVIOUS+OR_BATCH", "OL=voriger; OR=Ansatz", "voriger Ansatz", "OR_BATCH", "PREPARATION", "OL supplies previous-batch linkage."),
    "b9d7b6d68209a9019e7a": selected("HO_INGREDIENT+OR_BATCH", "HO=Zutat; OR=Ansatz", "Zutatenansatz", "OR_BATCH", "OWNER_ITEM+PREPARATION", "The composition predicts ingredient plus prepared batch without naming a plant."),
    "6afeb5c9ab9f6cbdea0d": selected("OR_BATCH+AIN_PORTION", "OR=Ansatz; AIN=Portion", "Ansatzportion", "OR_BATCH", "QUANTITY+PREPARATION", "AIN supplies portion."),
    "2cc054357a929df85f64": selected("HO_INGREDIENT", "HO=Zutat", "Zutat", "HO_INGREDIENT", "OWNER_ITEM", "One invariant card now covers plant material and the former local honey fill."),

    # Whole-card medium/product deck.  These values are not split into global
    # letter roots merely because they contain similar visible strokes.
    "cb57b696b815fdef9cb7": selected("SHECTHY_TEMPERED_WHOLE_CARD", "SHECTHY=temperiert", "temperiert", "STATE_WHOLE_CARD", "STATE_GRADE", "The card lies between rest and ready states; warmth is a local expansion, not a water root."),
    "428a5e3662aa57b4b256": selected("SCHOAL_WINE_DECOCTION_WHOLE_CARD", "SCHOAL=Weinsud", "Weinsud", "MEDIUM_WHOLE_CARD", "MEDIUM+PREPARATION", "The complete extraction chain supports a compact learned wine-decoction card."),
    "0f18de177ed7c878bf95": selected("DL_BATH_ADDITIVE_WHOLE_CARD", "DL=Badzusatz", "Badzusatz", "MEDIUM_WHOLE_CARD", "MEDIUM", "Two occurrences share a bath-additive slot."),
    "b5df9126607030b95175": selected("SHEY_CLEAR_EXTRACT_WHOLE_CARD", "SHEY=Klarauszug", "Klarauszug", "PRODUCT_WHOLE_CARD", "PREPARATION+STATE_GRADE", "Four post-separation endpoints share the clarified-product value."),
    "d4a31dbcf1ed6d9e5aa9": selected("TSHEY_RINSE_WATER_WHOLE_CARD", "TSHEY=Spülwasser", "Spülwasser", "WATER_WHOLE_CARD", "MEDIUM", "A learned rinse-water card; no free TSH or SHEY composition is asserted."),
    "cbb42a4fe68068325d6b": selected("DSHE_FRESH_WATER+DY_CLOSE", "DSHE=Frischwasser; Endkarte=Schluss", "Frischwasser; Schluss", "WATER_WHOLE_CARD", "MEDIUM+CLOSE", "The exact card supplies fresh water and closes its cell."),
    "98bdc4244c84cbef3321": selected("RSHEAL_WARM_WATER_WHOLE_CARD", "RSHEAL=Warmwasser", "Warmwasser", "WATER_WHOLE_CARD", "MEDIUM", "A learned warm-water card at the second opening."),
    "b2812c8283c3a62438bd": selected("KCHY_DRAUGHT_WHOLE_CARD", "KCHY=Trank", "Trank", "PRODUCT_WHOLE_CARD", "PREPARATION", "The exact card names the prepared drink, not an entire instruction."),
    "c71c72da4e09e0833392": selected("KCHOAR_USE_EXTRACT_WHOLE_CARD", "KCHOAR=Gebrauchsauszug", "Gebrauchsauszug", "PRODUCT_WHOLE_CARD", "PREPARATION", "The shorter product name removes the unsupported chest/cough content."),
    "883a6708116c342cb10b": selected("SKAR_WARM_POUR_WHOLE_CARD", "SKAR=Warmausguss", "Warmausguss", "MEDIUM_WHOLE_CARD", "MEDIUM+FLOW_TRANSFER", "A compact learned product/action noun; no free SK or AR material root is exported."),
}


EVENT_CONTEXTS = {
    "E006": "Wasser zulaufen lassen",
    "E017": "Ansatz",
    "E024": "Nächster Ansatz",
    "E025": "Ansatz",
    "E028": "Voriger Ansatz",
    "E033": "Ansatz",
    "E034": "Ansatz",
    "E040": "Weinsud bereiten",
    "E049": "Trank",
    "E065": "Auszug daraus entnehmen",
    "E071": "Ansatz",
    "E073": "Ansatzportion",
    "E074": "Zutatenansatz",
    "E075": "Zutat",
    "E078": "Zutat",
    "E080": "Nächster Ansatz",
    "E088": "Zutat",
    "E092": "Auszug zugeben",
    "E094": "Zutat zugeben",
    "E096": "Gebrauchsauszug",
    "E103": "Beckenwasser",
    "E112": "Badzusatz",
    "E113": "Voriger Ansatz",
    "E129": "Badzusatz",
    "E189": "Frischwasser zugeben; Schluss",
    "E202": "Auszug abziehen",
    "E212": "Spülwasser",
    "E222": "Warmwasser einlassen",
    "E254": "Ansatz",
    "E260": "Wasser in Gang setzen",
    "E276": "Temperiert",
    "E300": "Wasser weiterführen",
    "E348": "Ansatz",
    "E351": "Wasserlauf schließen; Schluss",
    "E360": "Warmausguss",
}


PARADIGM = [
    ("01_WATER_ROOT", ident) for ident in (
        "12efe866f335461823a6", "22fb87a5a83e5c3fb510", "7d2404c835b10a2c06af",
        "b154ff779abe5f196c80", "8aedd154964a78e555d6",
    )
] + [
    ("02_EXTRACT_ROOT", "087a47b5423438cd6b6a"),
    ("02_EXTRACT_ROOT", "807591efc3d3f7ddbfab"),
    ("03_BATCH_ROOT", "7a4bb8136330ee4e6e56"),
    ("03_BATCH_ROOT", "10488b911aae52b3b334"),
    ("03_BATCH_ROOT", "dec401773c1f0347793d"),
    ("03_BATCH_ROOT", "b9d7b6d68209a9019e7a"),
    ("03_BATCH_ROOT", "6afeb5c9ab9f6cbdea0d"),
    ("04_INGREDIENT_ROOT", "2cc054357a929df85f64"),
    ("05_LEARNED_MEDIUM_DECK", "cb57b696b815fdef9cb7"),
    ("05_LEARNED_MEDIUM_DECK", "428a5e3662aa57b4b256"),
    ("05_LEARNED_MEDIUM_DECK", "0f18de177ed7c878bf95"),
    ("05_LEARNED_MEDIUM_DECK", "b5df9126607030b95175"),
    ("05_LEARNED_MEDIUM_DECK", "d4a31dbcf1ed6d9e5aa9"),
    ("05_LEARNED_MEDIUM_DECK", "cbb42a4fe68068325d6b"),
    ("05_LEARNED_MEDIUM_DECK", "98bdc4244c84cbef3321"),
    ("05_LEARNED_MEDIUM_DECK", "b2812c8283c3a62438bd"),
    ("05_LEARNED_MEDIUM_DECK", "c71c72da4e09e0833392"),
    ("05_LEARNED_MEDIUM_DECK", "883a6708116c342cb10b"),
]


COMPONENTS = [
    ("AIR", "Wasser", "PRODUCTIVE_CANDIDATE", "5 cards / 5 records-side events", "Every AIR hull remains aqueous; a new AIR compound should still concern water."),
    ("CHEO", "Auszug", "PRODUCTIVE_CANDIDATE", "2 cards / 2 Herbal events", "OK+CHEO adds it; CHEO+AR takes it from a source."),
    ("OR", "Ansatz", "PRODUCTIVE_CANDIDATE", "5 cards / 13 events", "OT, OL, HO and AIN predict next, previous, ingredient and portion readings."),
    ("HO", "Zutat", "PRODUCTIVE_CANDIDATE", "1 exact card plus HO+OR", "The exact cho|sho card no longer changes from plant to honey by occurrence."),
    ("SHEY", "Klarauszug", "LEARNED_RESULT_CARD", "1 card / 4 events", "Post-separation result; do not split SH or EY globally."),
    ("WATER_DECK", "Frischwasser | Warmwasser | Spülwasser", "LEARNED_WHOLE_CARDS", "3 cards / 3 events", "Specific water states are memorized whole cards, not AIR compounds."),
    ("SCHOAL", "Weinsud", "LEARNED_WHOLE_CARD", "1 card / 1 event", "Wine is local to this exact card; O and OL remain non-wine."),
    ("DL", "Badzusatz", "LEARNED_WHOLE_CARD", "1 card / 2 events", "The exact card repeats inside one bath record."),
    ("SHECTHY", "temperiert", "LEARNED_STATE_CARD", "1 card / 1 event", "Warm medium is a local expansion; water is not built into the card."),
    ("KCHY", "Trank", "LEARNED_WHOLE_CARD", "1 card / 1 event", "Prepared product, not a sentence."),
    ("KCHOAR", "Gebrauchsauszug", "LEARNED_WHOLE_CARD", "1 card / 1 event", "Chest and cough are owner/exemplar expansions, not lexical content."),
    ("SKAR", "Warmausguss", "LEARNED_WHOLE_CARD", "1 card / 1 event", "No free SK/AR substance decomposition."),
    ("OIL", "unlokalisiert", "LOCAL_FILL_ONLY", "no invariant card", "Oil remains plausible in a recipe but is not a selected word or root."),
    ("HONEY", "possible HO instance", "LOCAL_FILL_ONLY", "one former context only", "Honey may instantiate ZUTAT; it is not the meaning of HO."),
]


COMPARISON = [
    ("AIR", "Laufflüssigkeit", "laufende Arbeitsflüssigkeit", "Wasser", "Wasser", "All five hulls accept water; the bold short root makes new compounds predictable."),
    ("CHEO", "Auszug", "Auszugsmedium", "Auszug", "Auszug", "The two cards agree on an intermediate extract reused as input."),
    ("OR", "Zubereitung", "Ansatz", "Ansatz", "Ansatz", "Ansatz is the shortest stable prepared-batch noun."),
    ("HO / cho|sho", "Pflanzenstoff", "Pflanzenstoff", "Zutat", "Zutat", "Zutat repairs the plant-versus-honey identity conflict and predicts HO+OR."),
    ("SHECTHY", "Badwasser", "warme Arbeitsflüssigkeit", "temperiert", "temperiert", "Its CTHY neighborhood favors a state word over a second water noun."),
    ("specific liquids", "Frisch-/Warm-/Badwasser", "mostly generic media", "mixed learned medium deck", "learned water deck", "Concrete media stay whole cards unless a recurrent composition supports a root."),
    ("wine", "SCHOAL=Weinsud", "uncommitted", "in Wein kochen", "SCHOAL=Weinsud", "A compact nomenclator card is preferable to encoding 'boil in wine' as one word."),
    ("oil", "unlocalized", "removed", "unlocalized", "unlocalized", "Earlier oil readings reused cards with other meanings."),
    ("honey", "removed", "removed", "possible ZUTAT instance", "possible ZUTAT instance", "Keep it as an ingredient hypothesis, not a dictionary identity."),
]


def load_r3_module():
    spec = importlib.util.spec_from_file_location("sidequest_r3_medium", R3_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R3 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build() -> dict[str, object]:
    r3 = load_r3_module()
    r3.main()
    dictionary = read_tsv(R3_DICT)
    events = read_tsv(R3_EVENTS)
    base_sentences = {row["statement_id"]: row for row in read_tsv(R3_SENTENCES)}

    selected_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row.update(
            selected_previous_segmentation=original["semantic_segmentation"],
            selected_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            selected_previous_gloss_de=original["concrete_word_reading_de"],
            selected_medium_family="R3_ACCEPTED",
            selected_medium_rationale="R3 material/flow distinction accepted without central change.",
        )
        choice = SELECTED.get(row["joint_tuple_id"])
        if choice:
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = choice[key]
            row["local_expansion_examples_de"] = "Stoffrunde: " + choice["concrete_word_reading_de"]
            row["selected_medium_family"] = choice["family"]
            row["selected_medium_rationale"] = choice["rationale"]
        selected_dictionary.append(row)
    dictionary_by_id = {row["joint_tuple_id"]: row for row in selected_dictionary}

    selected_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            selected_previous_segmentation=original["semantic_segmentation"],
            selected_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            selected_previous_gloss_de=original["concrete_word_reading_de"],
            selected_previous_context_de=original["contextual_event_reading_de"],
            selected_medium_family="R3_ACCEPTED",
            selected_medium_rationale="R3 material/flow distinction accepted without central change.",
        )
        choice = SELECTED.get(row["joint_tuple_id"])
        if choice:
            drow = dictionary_by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = EVENT_CONTEXTS.get(row["event_id"], sentence_case(drow["concrete_word_reading_de"]))
            row["workshop_slots"] = choice["slots"]
            row["selected_medium_family"] = choice["family"]
            row["selected_medium_rationale"] = choice["rationale"]
        selected_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in selected_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = base_sentences[statement_id]
        row = dict(base)
        revised = [event for event in group if event["joint_tuple_id"] in SELECTED]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["canonical_slots_present"] = ">".join(uniq([slot for event in group for slot in event["workshop_slots"].split("+")]))
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row["selected_medium_revised_event_count"] = str(len(revised))
        row["selected_medium_families"] = "|".join(uniq([event["selected_medium_family"] for event in revised])) or "R3_ACCEPTED"
        row["selected_previous_card_sequence_de"] = base["card_sequence_de"]
        row["selected_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        sentences.append(row)

    record_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        record_groups[row["record_unit_id"]].append(row)
    lines = [
        "# Elf vollständige Records nach der Stoff-/Flüssigkeitsrunde",
        "",
        "Kreative Werkstattlesung. Kurze Stoffwurzeln und gelernte Fachkarten bleiben getrennt; Zeilen sind kein Satzschluss.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = record_groups[record]
        lines.extend([f"## {record} — {'|'.join(uniq([row['page'] for row in rows]))}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.') }.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    event_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_events:
        event_by_card[row["joint_tuple_id"]].append(row)
    paradigm_rows = []
    for stage, ident in PARADIGM:
        drow = dictionary_by_id[ident]
        erows = event_by_card[ident]
        paradigm_rows.append({
            "stage": stage,
            "joint_tuple_id": ident,
            "surface_family": drow["surface_family"],
            "semantic_segmentation": drow["semantic_segmentation"],
            "stable_nucleus_de": drow["stable_concrete_nucleus_de"],
            "card_default_de": drow["concrete_word_reading_de"],
            "occurrences": str(len(erows)),
            "event_ids": "|".join(row["event_id"] for row in erows),
            "statement_ids": "|".join(uniq([row["statement_id"] for row in erows])),
            "pages": "|".join(uniq([row["page"] for row in erows])),
            "selection_rationale": SELECTED[ident]["rationale"],
        })
    component_rows = [
        {"component_id": ident, "selected_default_de": default, "status": status, "support": support, "prediction_or_limit": limit}
        for ident, default, status, support, limit in COMPONENTS
    ]
    comparison_rows = [
        {"target": target, "r1_medical": r1, "r2_material": r2, "r3_technical": r3_value, "selected": chosen, "selection_reason": reason}
        for target, r1, r2, r3_value, chosen, reason in COMPARISON
    ]

    write_tsv(DICT_OUT, selected_dictionary, list(selected_dictionary[0]))
    write_tsv(EVENT_OUT, selected_events, list(selected_events[0]))
    write_tsv(SENTENCE_OUT, sentences, list(sentences[0]))
    write_tsv(COMPONENT_OUT, component_rows, list(component_rows[0]))
    write_tsv(PARADIGM_OUT, paradigm_rows, list(paradigm_rows[0]))
    write_tsv(COMPARISON_OUT, comparison_rows, list(comparison_rows[0]))

    central_changes_from_r3 = sum(
        row["concrete_word_reading_de"] != row["selected_previous_gloss_de"]
        for row in selected_dictionary
    )
    changed_from_application = sum(
        row["concrete_word_reading_de"] != row["r3_previous_gloss_de"]
        for row in selected_dictionary
    )
    selected_events_count = sum(row["joint_tuple_id"] in SELECTED for row in selected_events)
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, COMPONENT_OUT, PARADIGM_OUT, COMPARISON_OUT]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_MEDIUM_SUBSTANCE_V1",
        "status": "BUILT",
        "counts": {
            "cards": len(selected_dictionary),
            "events": len(selected_events),
            "statements": len(sentences),
            "records": len(record_groups),
            "selected_cards": len(SELECTED),
            "selected_card_events": selected_events_count,
            "central_changes_relative_to_r3": central_changes_from_r3,
            "changed_cards_relative_to_application": changed_from_application,
            "component_rows": len(component_rows),
            "paradigm_rows": len(paradigm_rows),
        },
        "input_hashes": {path.name: sha256(path) for path in (R3_DICT, R3_EVENTS, R3_SENTENCES)},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "fixed_pages_only": True,
        "astro_unchanged": True,
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
