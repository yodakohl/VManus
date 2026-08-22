#!/usr/bin/env python3
"""Build the independent R1 V80 canonical third edition.

The builder is deliberately a compiler, not an interpreter.  It only joins the
centrally selected V69/V73--V79 artifacts and applies the explicitly frozen V80
editorial rules.  It never reads images, other pages, or sibling V80 results.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

FIXED_PAGES = (
    "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
)
PROSE_PAGES = set(FIXED_PAGES[:7])
ASTRO_PAGES = set(FIXED_PAGES[7:])

DCDA = "dcda95c81a5460feb191"
B5FCEA = "b5fcea1eaed06b2f2291"
FORMAL_PARAMETER = "2f1c5e56e8f0ff459065"
FORMAL_RELATION_SLOT = "308e8ea2d5d190c498e8"

LEAD_ID = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
RIVAL_ID = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"

SOURCES = {
    "v69_dictionary": (
        "experiments/yolo/sidequest_theory_candidates_v69/"
        "V69_R4_FINAL_173_CARD_DICTIONARY.tsv",
        "85a9cf9df30ff5d47163e809b8de534ec02022a5e85c0821869302d3471cfaec",
    ),
    "v69_prose": (
        "experiments/yolo/sidequest_theory_candidates_v69/"
        "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv",
        "ab6c35739c173587bf10118a48286c2f4c313873d0df35ad4e93a6c3f2f4dcec",
    ),
    "v69_astro": (
        "experiments/yolo/sidequest_theory_candidates_v69/"
        "V69_R4_FINAL_395_ASTRO_GROUPS.tsv",
        "4d60bcdc86878d7ccf42a06ed2e7f0c24e5172c1f977a1c20b71788f4f466850",
    ),
    "v73_events": (
        "experiments/yolo/sidequest_theory_candidates_v73/"
        "V73_SELECTED_100_EVENT_INTERLINEAR.tsv",
        "de9dbc9b7bf834090ee50707f59e3e7f6490844461a7670ad80d720479b645dc",
    ),
    "v73_fields": (
        "experiments/yolo/sidequest_theory_candidates_v73/"
        "V73_SELECTED_20_FIELD_EDITION.tsv",
        "da84a0a99c7a4dd2b60b9888dc5844afeec8500415f11a90dfb67c661b497d08",
    ),
    "v73_articles": (
        "experiments/yolo/sidequest_theory_candidates_v73/"
        "V73_SELECTED_FIVE_ARTICLES.tsv",
        "fe38340b28bc32d62a3556569c83edc4ce1b6f87be18e52559bc4b7e9a5f9ee9",
    ),
    "v74_events": (
        "experiments/yolo/sidequest_theory_candidates_v74/"
        "V74_SELECTED_281_EVENT_INTERLINEAR.tsv",
        "201b1126f3922758bf76eb8bd15180ec6a8c38c4b66a5a9e68b4583c5a42cfe3",
    ),
    "v74_fields": (
        "experiments/yolo/sidequest_theory_candidates_v74/"
        "V74_SELECTED_115_FIELD_EDITION.tsv",
        "64e2688a8a933dcb3901c8d09d0237d9c43e133e2cf4ae27799f7340cb1f679d",
    ),
    "v74_statements": (
        "experiments/yolo/sidequest_theory_candidates_v74/"
        "V74_SELECTED_97_STATEMENT_EDITION.tsv",
        "e06c33ba84b1d99fad202aea8c92098df509ebac4fe48abe4dde4720c95a8b01",
    ),
    "v74_records": (
        "experiments/yolo/sidequest_theory_candidates_v74/"
        "V74_SELECTED_SIX_RECORD_EDITION.tsv",
        "72776e55d262d81618180f2c6f21fe82376d059986b86dbb782dd91205691ea6",
    ),
    "v75_groups": (
        "experiments/yolo/sidequest_theory_candidates_v75/"
        "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv",
        "3c35deb68ee2a4a02b539a7b979011fb4fea1436847249277181974133c8ff8e",
    ),
    "v75_loci": (
        "experiments/yolo/sidequest_theory_candidates_v75/"
        "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv",
        "8f43d3571694025383119101748cd6eb2ba6c909a638a87f532ba61b7270ced5",
    ),
    "v75_instruments": (
        "experiments/yolo/sidequest_theory_candidates_v75/"
        "V75_SELECTED_THREE_INSTRUMENTS.tsv",
        "097678b799d9ce8ee960d82cc613c1375e678f34a8fbc2c97e79b7321a5dc0a8",
    ),
    "v75_namespaces": (
        "experiments/yolo/sidequest_theory_candidates_v75/"
        "V75_SELECTED_NAMESPACE_REGISTRY.tsv",
        "16bce5c1d571e3122d6ebed6d25700eef255d0599095d65d55d5cf09bdced7d0",
    ),
    "v76_purposes": (
        "experiments/yolo/sidequest_theory_candidates_v76/"
        "V76_SELECTED_BOOK_PURPOSE_COMPETITION.tsv",
        "5b05de490eb5f09f177a9d1a5b5f8c208d6e7b5152f26d83e8704ecb5b0a31bd",
    ),
    "v76_contradictions": (
        "experiments/yolo/sidequest_theory_candidates_v76/"
        "V76_SELECTED_CONTRADICTIONS.tsv",
        "eaeb9b44a156a6d109aa18fd2f80e36742488f444b4763ca93574cf9a7c40446",
    ),
    "v76_workflow": (
        "experiments/yolo/sidequest_theory_candidates_v76/"
        "V76_SELECTED_PRODUCTION_WORKFLOW.tsv",
        "e3dcb1b88bb5ede2ebaa0174d835360800fa2b2d0562c42682157e4b5d54c749",
    ),
    "v77_dictionary": (
        "experiments/yolo/sidequest_theory_candidates_v77/"
        "V77_SELECTED_CARD_DICTIONARY.tsv",
        "4aaae864f45ea152da0f44524c515a4f0ba8f61dad5eca09501fbba644c01faf",
    ),
    "v78_events": (
        "experiments/yolo/sidequest_theory_candidates_v78/"
        "V78_SELECTED_381_EVENT_INTERLINEAR.tsv",
        "0872a6f61f7e3396743c54bb1a8ad9e5830ebe7c0ddcf23885204a52ed046ac1",
    ),
    "v78_statements": (
        "experiments/yolo/sidequest_theory_candidates_v78/"
        "V78_SELECTED_116_STATEMENTS.tsv",
        "d12c385ba37dc1e875abbeadd3df55eb34698e5b08ab3d7136e9a8c4eaeef0f0",
    ),
    "v78_records": (
        "experiments/yolo/sidequest_theory_candidates_v78/"
        "V78_SELECTED_11_CONTINUOUS_RECORDS.tsv",
        "c32a202087155e015a6b86d32322fd6ca47c67998431d9b8fd4cc38d71db66f9",
    ),
    "v78_et_per": (
        "experiments/yolo/sidequest_theory_candidates_v78/"
        "V78_SELECTED_ET_PER_28_AUDIT.tsv",
        "7c9c9c3b43e8b9580a2dafdbcebd840d58b5675b36260b38cbbe50ec7e2f6c46",
    ),
    "v79_transitions": (
        "experiments/yolo/sidequest_theory_candidates_v79/"
        "V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv",
        "096f718e72de33b017e33e5aea4ea0f424860a690bd43b849276cbc1fef38dcf",
    ),
    "v79_manual": (
        "experiments/yolo/sidequest_theory_candidates_v79/"
        "V79_SELECTED_MACHINE_MANUAL.tsv",
        "fb91db19df2ac3d725620de1195c76ee8d421d3f439ee6d75f91349ea3a18867",
    ),
    "v79_repairs": (
        "experiments/yolo/sidequest_theory_candidates_v79/"
        "V79_SELECTED_REPAIR_DECISIONS.tsv",
        "e00ad9763e68e8b58e223af7e1371c9d7684bbe8f149a035c12d1b9637949648",
    ),
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(key: str) -> list[dict[str, str]]:
    rel, expected = SOURCES[key]
    path = ROOT / rel
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"source drift {key}: {actual} != {expected}")
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, delimiter="\t", fieldnames=fields,
                           lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def split_ids(value: str) -> list[str]:
    return [x for x in value.split("|") if x and x != "NONE"]


def section_for_record(record: str) -> str:
    return "HERBAL" if record.startswith("H") else "BIOLOGICAL"


def canonical_dictionary_value(card_id: str) -> tuple[str, str, str, str]:
    """value, optional gloss, class, memorized guess."""
    if card_id == DCDA:
        return (
            "FORMAL_LINK_OR_SLOT",
            "ET?=UND/AUCH?__OPTIONAL_QUESTIONED_MASTER_GLOSS_ONLY",
            "AUTONOMOUS_FORMAL_ROLE",
            "ET?=UND/AUCH?__MEMORIZED_ONLY_IF_MASTER_SUPPLIES_IT",
        )
    if card_id == B5FCEA:
        return (
            "FORMAL_RELATION_OR_ENTRY",
            "PER?=DURCH/GEMÄSS?__OPTIONAL_QUESTIONED_MASTER_GLOSS_ONLY",
            "AUTONOMOUS_FORMAL_ROLE",
            "PER?=DURCH/GEMÄSS?__MEMORIZED_ONLY_IF_MASTER_SUPPLIES_IT",
        )
    if card_id == FORMAL_PARAMETER:
        return (
            "FORMAL_PARAMETER_CHANNEL__NOT_A_WORD", "NONE",
            "FORMAL_LABEL_NOT_WORD", "NONE",
        )
    if card_id == FORMAL_RELATION_SLOT:
        return (
            "FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD", "NONE",
            "FORMAL_LABEL_NOT_WORD", "NONE",
        )
    return ("EXEMPLAR_VALUE_UNKNOWN", "NONE", "CONTENT_CARD_UNKNOWN", "NONE")


def event_primary_token(event: dict[str, str]) -> tuple[str, int, str]:
    card = event["joint_tuple_id"]
    event_id = event["event_id"]
    if card == DCDA:
        return "[FORMAL_LINK_OR_SLOT]", 1, "READ_ONE_VISIBLE_SOURCE_TOKEN"
    if card == B5FCEA and event_id == "E180":
        return (
            "[FORMAL_RELATION_OR_ENTRY; ANTICIPATORY_VISIBLE_COPY; READ_WITH_E181_ONCE]",
            0,
            "PRESERVE_VISIBLE_COPY__DO_NOT_EMIT_SECOND_SOURCE_TOKEN",
        )
    if card == B5FCEA:
        return "[FORMAL_RELATION_OR_ENTRY]", 1, "READ_ONE_VISIBLE_SOURCE_TOKEN"
    if card == FORMAL_PARAMETER:
        return "[FORMAL:FORMAL_PARAMETER_CHANNEL; KEIN WORT]", 1, "READ_FORMAL_CHANNEL"
    if card == FORMAL_RELATION_SLOT:
        return "[FORMAL:FORMAL_RELATION_SLOT_CHANNEL; KEIN WORT]", 1, "READ_FORMAL_CHANNEL"
    return "[EXEMPLARWERT UNBEKANNT]", 1, "LOOK_UP_OCCURRENCE_IN_MASTER_EXEMPLAR"


def replace_optional_words(text: str) -> str:
    return (
        text.replace(
            "ET? (UND/AUCH?)",
            "[FORMAL_LINK_OR_SLOT; optionale Meisterglosse ET?=UND/AUCH?]",
        ).replace(
            "PER? (DURCH/GEMÄSS?)",
            "[FORMAL_RELATION_OR_ENTRY; optionale Meisterglosse PER?=DURCH/GEMÄSS?]",
        ).replace(
            "[KUSTODE:PER?; AM NAECHSTEN ZEILENANFANG WIEDERHOLT; NICHT DOPPELT SPRECHEN]",
            "[FORMAL_RELATION_OR_ENTRY; erste sichtbare Kopie; mit Folgelinie einmal lesen]",
        )
    )


def main() -> None:
    data = {key: read_tsv(key) for key in SOURCES}

    # Immutable source sanity.
    assert len(data["v69_dictionary"]) == 173
    assert len(data["v69_prose"]) == len(data["v78_events"]) == 381
    assert len(data["v73_events"]) == 100 and len(data["v74_events"]) == 281
    assert len(data["v73_fields"]) == 20 and len(data["v74_fields"]) == 115
    assert len(data["v78_statements"]) == 116
    assert len(data["v75_groups"]) == len(data["v69_astro"]) == 395
    assert len(data["v75_loci"]) == 142
    assert len(data["v78_records"]) == 11 and len(data["v75_instruments"]) == 3

    v77_by_id = {r["joint_tuple_id"]: r for r in data["v77_dictionary"]}
    dictionary: list[dict[str, object]] = []
    for r in data["v69_dictionary"]:
        card = r["joint_tuple_id"]
        value, gloss, cls, memory = canonical_dictionary_value(card)
        v77 = v77_by_id.get(card, {})
        attestation = "NONE"
        if card in {DCDA, B5FCEA}:
            attestation = v77["historical_attestation"]
        dictionary.append({
            "joint_tuple_id": card,
            "surface_examples_display_only": r["surface_examples"],
            "visible_occurrences": r["occurrences"],
            "pages": r["pages"],
            "autonomous_operational_value": value,
            "optional_questioned_master_gloss": gloss,
            "historical_category_attestation": attestation,
            "dictionary_class": cls,
            "portable_content_value": "NONE",
            "occurrence_exemplar_status": (
                "MASTER_EXEMPLAR_REQUIRED" if cls == "CONTENT_CARD_UNKNOWN"
                else "NOT_A_CONTENT_VALUE"
            ),
            "memorized_guess_exact": memory,
            "apprentice_readback": (
                value if cls != "CONTENT_CARD_UNKNOWN"
                else "REPORT_EXEMPLAR_VALUE_UNKNOWN__DO_NOT_GUESS"
            ),
            "source_lineage": "V69_R4_IDENTITY_AND_COUNTS__V77_SELECTED_SOURCE_AUDIT__V79_FORMAL_DECISION",
            "semantic_ceiling": "OPAQUE_CARD_FORMAL_ROLE_OR_UNKNOWN__NO_WORD_STEM_SOUND_LANGUAGE_MEANING",
        })
    dictionary.sort(key=lambda x: str(x["joint_tuple_id"]))
    dict_by_id = {str(r["joint_tuple_id"]): r for r in dictionary}

    v69_event_by_serial = {r["event_serial"]: r for r in data["v69_prose"]}
    v73_event_by_serial = {r["event_serial"]: r for r in data["v73_events"]}
    v74_event_by_serial = {r["event_serial"]: r for r in data["v74_events"]}
    event_rows: list[dict[str, object]] = []
    for e in data["v78_events"]:
        serial = e["event_serial"]
        old = v69_event_by_serial[serial]
        selected = v73_event_by_serial.get(serial) or v74_event_by_serial.get(serial)
        assert selected and selected["joint_tuple_id"] == e["joint_tuple_id"]
        token, source_count, read_action = event_primary_token(e)
        d = dict_by_id[e["joint_tuple_id"]]
        reset = e["owner_break_before"].startswith("BREAK_VISIBLE_GAP")
        event_rows.append({
            "event_serial": serial,
            "event_id": e["event_id"],
            "section": section_for_record(e["record_unit_id"]),
            "record_unit_id": e["record_unit_id"],
            "page": e["page"],
            "locus": e["locus"],
            "field_id": e["field_id"],
            "statement_id": e["statement_id"],
            "joint_tuple_id": e["joint_tuple_id"],
            "surface_display_only": old["surface_display_only"],
            "image_owner_id": e["image_owner_id"],
            "owner_break_before": e["owner_break_before"],
            "owner_reset": "YES__CLEAR_SUBSTANCE_TARGET_DIRECTION" if reset else "NO",
            "literal_visible_layer": (
                f"[OWNER:{e['image_owner_id']}; EXEMPLAR] > "
                f"[OPAQUE_CARD:{e['joint_tuple_id']}; SURFACE:{old['surface_display_only']}]"
            ),
            "autonomous_primary_token": token,
            "optional_questioned_master_gloss": d["optional_questioned_master_gloss"],
            "occurrence_bound_exemplar": e["source_expansion_de"],
            "source_token_count": source_count,
            "read_action": read_action,
            "line_crossing": e["line_crossing"],
            "terminal_status": e["terminal_status"],
            "source_class": e["source_class"],
            "source_expansion_confidence": e["source_expansion_confidence"],
            "strongest_rival": e["strongest_source_rival"],
            "strongest_contradiction": e["strongest_contradiction"],
            "semantic_ceiling": "EXACT_FORM_PLUS_OCCURRENCE_EXEMPLAR__NO_PORTABLE_CONTENT_GLOSS",
            "source_lineage": "V69_R4_FORM__V73_OR_V74_OWNER_CONTENT__V78_SELECTION__V79_REPAIR",
        })
    event_rows.sort(key=lambda x: int(str(x["event_serial"])))
    event_by_serial = {str(r["event_serial"]): r for r in event_rows}

    # Fields are rebuilt from event rows; V73/V74 supply only selected owner/text/rival.
    field_rows: list[dict[str, object]] = []
    for section, source_key in (("HERBAL", "v73_fields"), ("BIOLOGICAL", "v74_fields")):
        for f in data[source_key]:
            serials = split_ids(f["event_serials"])
            events = [event_by_serial[s] for s in serials]
            owner = f.get("whole_plant_owner") or f.get("local_image_owner") or "UNRESOLVED"
            concrete = f.get("third_edition_field_text") or f.get("balneological_field_text") or ""
            field_rows.append({
                "field_id": f["field_id"],
                "section": section,
                "record_unit_id": f["record_unit_id"],
                "page": f["page"],
                "locus": f["locus"],
                "statement_id": f["statement_id"],
                "event_count": len(events),
                "event_serials": "|".join(serials),
                "image_owner_id": owner,
                "owner_status": f.get("owner_status", "PAGE_OWNER_ONLY"),
                "exact_card_order": " > ".join(str(e["joint_tuple_id"]) for e in events),
                "autonomous_primary_order": " ".join(str(e["autonomous_primary_token"]) for e in events),
                "occurrence_bound_exemplar_sequence": " ".join(str(e["occurrence_bound_exemplar"]) for e in events),
                "selected_source_field_expansion": f"[EXEMPLAR:{concrete}]",
                "strongest_rival": f.get("strongest_alternative") or f.get("strongest_rival") or "NONE",
                "strongest_contradiction": f["strongest_contradiction"],
                "semantic_ceiling": "FIELD_STRUCTURE_PLUS_OCCURRENCE_EXEMPLAR__NOT_TRANSLATION",
            })
    field_rows.sort(key=lambda x: int(str(x["field_id"])[1:]))

    # Statements preserve V78 segmentation but are re-rendered from the autonomous event layer.
    statement_rows: list[dict[str, object]] = []
    for s in data["v78_statements"]:
        serials = split_ids(s["event_serials"])
        events = [event_by_serial[x] for x in serials]
        statement_rows.append({
            "statement_id": s["statement_id"],
            "record_unit_id": s["record_unit_id"],
            "section": s["section"],
            "page": s["page"],
            "statement_ordinal_in_record": s["sentence_index_in_record"],
            "constituent_fields": s["constituent_fields"],
            "physical_lines": s["physical_lines"],
            "event_count": len(events),
            "event_serials": "|".join(serials),
            "exact_card_order": " > ".join(str(e["joint_tuple_id"]) for e in events),
            "autonomous_primary_order": " ".join(str(e["autonomous_primary_token"]) for e in events),
            "occurrence_bound_exemplar_sequence": " ".join(str(e["occurrence_bound_exemplar"]) for e in events),
            "selected_source_sentence": f"[EXEMPLAR:{replace_optional_words(s['continuous_sentence_text'])}]",
            "owner_transition": s["owner_transition"],
            "visible_owner_resets": s["visible_owner_resets"],
            "cross_field_transitions": s["cross_field_transitions"],
            "cross_physical_line_transitions": s["cross_physical_line_transitions"],
            "line_crossing": s["line_crossing_v72"],
            "source_class": s["source_class"],
            "process_or_content_rival": s["process_or_content_rival"],
            "notation_rival": s["notation_rival"],
            "repair_cost_0_4": s["repair_cost_0_4_v72"],
            "hardest_contradiction": s["hardest_contradiction"],
            "semantic_ceiling": "STATEMENT_SEGMENTATION_AND_SOURCE_CLASS_EXEMPLAR__NOT_SENTENCE_TRANSLATION",
        })

    # V75 local behavior is authoritative; V69 contributes only the exact displayed surface.
    v69_group_by_serial = {r["group_serial"]: r for r in data["v69_astro"]}
    astro_rows: list[dict[str, object]] = []
    for g in data["v75_groups"]:
        old = v69_group_by_serial[g["group_serial"]]
        assert old["opaque_local_id"] == g["opaque_local_id"]
        astro_rows.append({
            "group_serial": g["group_serial"],
            "diagram_id": g["diagram_id"],
            "page": g["page"],
            "locus": g["locus"],
            "event_index": g["event_index"],
            "opaque_local_id": g["opaque_local_id"],
            "surface_display_only": old["surface_display_only"],
            "local_image_owner": g["local_image_owner"],
            "owner_status": g["owner_status"],
            "local_namespace": g["local_namespace"],
            "local_content_class": g["local_content_class"],
            "autonomous_primary_reading": "COPY_OPAQUE_GROUP_IN_LOCAL_NAMESPACE",
            "occurrence_bound_exemplar": f"[EXEMPLAR:{g['copied_local_meaning_or_label']}]",
            "source_status": g["copied_label_source_status"],
            "meaning_confidence": g["meaning_confidence"],
            "strongest_historical_rival": g["strongest_astronomical_calendar_or_formal_rival"],
            "strongest_contradiction": g["strongest_contradiction"],
            "orientation_status": g["orientation_status"],
            "f68_f69_mapping": g["f68_f69_mapping"],
            "prose_card_import": g["prose_card_import"],
            "semantic_ceiling": "LOCAL_NAMESPACE_AND_EXEMPLAR_LABEL__NO_NAME_ORDER_OR_CROSSPAGE_KEY",
            "source_lineage": "V69_R4_SURFACE__V75_SELECTED_GROUP_AND_NAMESPACE",
        })
    astro_rows.sort(key=lambda x: int(str(x["group_serial"])))

    unified: list[dict[str, object]] = []
    for e in event_rows:
        unified.append({
            "unified_serial": len(unified) + 1,
            "item_kind": "PROSE_EVENT",
            "section": e["section"],
            "page": e["page"],
            "unit_id": e["record_unit_id"],
            "locus": e["locus"],
            "local_id": e["event_id"],
            "opaque_identity": e["joint_tuple_id"],
            "surface_display_only": e["surface_display_only"],
            "owner": e["image_owner_id"],
            "namespace": "PROSE_RECORD_LOCAL",
            "autonomous_primary_reading": e["autonomous_primary_token"],
            "optional_master_gloss": e["optional_questioned_master_gloss"],
            "occurrence_bound_exemplar": e["occurrence_bound_exemplar"],
            "visible_count": 1,
            "source_token_count": e["source_token_count"],
            "strongest_contradiction": e["strongest_contradiction"],
            "semantic_ceiling": e["semantic_ceiling"],
        })
    for g in astro_rows:
        unified.append({
            "unified_serial": len(unified) + 1,
            "item_kind": "ASTRO_GROUP",
            "section": "ASTRO",
            "page": g["page"],
            "unit_id": g["diagram_id"],
            "locus": g["locus"],
            "local_id": g["opaque_local_id"],
            "opaque_identity": g["opaque_local_id"],
            "surface_display_only": g["surface_display_only"],
            "owner": g["local_image_owner"],
            "namespace": g["local_namespace"],
            "autonomous_primary_reading": g["autonomous_primary_reading"],
            "optional_master_gloss": "NONE",
            "occurrence_bound_exemplar": g["occurrence_bound_exemplar"],
            "visible_count": 1,
            "source_token_count": 1,
            "strongest_contradiction": g["strongest_contradiction"],
            "semantic_ceiling": g["semantic_ceiling"],
        })

    # The complete contradiction ledger combines the frozen model audit, formal repairs,
    # and every distinct occurrence-level contradiction with support counts.
    contradictions: list[dict[str, object]] = []
    for r in data["v76_contradictions"]:
        contradictions.append({
            "contradiction_id": f"PURPOSE_{r['contradiction_id']}",
            "level": "BOOK_PURPOSE",
            "affected_units": r["affected_units"],
            "contradiction": r["contradiction"],
            "support_count": 1,
            "severity": r["severity"],
            "containment": r["containment"],
            "status": r["status"],
            "source": "V76_SELECTED_CONTRADICTIONS",
        })
    for i, r in enumerate(data["v79_repairs"], 1):
        contradictions.append({
            "contradiction_id": f"FORMAL_{i:02d}_{r['issue']}",
            "level": "FORMAL_READBACK",
            "affected_units": "ALL" if "MASTER" in r["issue"] else r["issue"],
            "contradiction": r["failure_or_limit"],
            "support_count": 1,
            "severity": "HIGH",
            "containment": r["apprentice_rule"],
            "status": "CONTAINED_BY_RULE",
            "source": "V79_SELECTED_REPAIR_DECISIONS",
        })
    for level, rows, text_key, id_key, unit_key in (
        ("PROSE_OCCURRENCE", event_rows, "strongest_contradiction", "event_id", "record_unit_id"),
        ("ASTRO_OCCURRENCE", astro_rows, "strongest_contradiction", "opaque_local_id", "diagram_id"),
    ):
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for r in rows:
            grouped[str(r[text_key])].append(r)
        for i, (text, members) in enumerate(sorted(grouped.items()), 1):
            contradictions.append({
                "contradiction_id": f"{level}_{i:03d}",
                "level": level,
                "affected_units": "|".join(sorted({str(x[unit_key]) for x in members})),
                "contradiction": text,
                "support_count": len(members),
                "severity": "LOCAL",
                "containment": "KEEP_OCCURRENCE_BOUND_EXEMPLAR_AND_STRONGEST_RIVAL",
                "status": "OPEN_LOCAL",
                "source": f"V73/V74/V75_SELECTED::{','.join(str(x[id_key]) for x in members[:8])}",
            })

    # Compact manual: all selected V79 machine rules are retained, then V80's five
    # canonical value rules are appended.  No card receives a new content meaning.
    manual: list[dict[str, object]] = []
    for r in data["v79_manual"]:
        manual.append({
            "rule_order": r["rule_order"],
            "phase": r["state"],
            "visible_input": r["visible_input"],
            "condition": r["condition"],
            "apprentice_operation": r["operation"],
            "canonical_v80_readback": r["backward_output"],
            "failure_if_omitted": r["failure_if_omitted"],
            "source": "V79_SELECTED_MACHINE_MANUAL",
        })
    appended = [
        ("17", "DICTIONARY", "dcda exact card", "every occurrence", "REPORT_FORMAL_LINK_OR_SLOT", "Optional master key only: ET?=UND/AUCH?", "Do not infer a word from internal form"),
        ("18", "DICTIONARY", "b5fcea exact card", "after generic read-once", "REPORT_FORMAL_RELATION_OR_ENTRY", "Optional master key only: PER?=DURCH/GEMÄSS?", "Do not infer a word from entry placement"),
        ("19", "DICTIONARY", "two frozen formal channels", "exact ID match", "REPORT_FORMAL_LABEL_NOT_WORD", "No spoken word", "Do not turn prompts into vocabulary"),
        ("20", "DICTIONARY", "all other exact prose cards", "always", "REPORT_EXEMPLAR_VALUE_UNKNOWN", "Consult occurrence in master exemplar", "Never guess a portable content value"),
        ("21", "ASTRO", "opaque local group", "within current owner/namespace", "COPY_LOCAL_GROUP_WITHOUT_TRAVERSAL", "Consult local master label", "No start, direction, f68-f69 key or prose import"),
    ]
    for row in appended:
        manual.append(dict(zip(
            ["rule_order", "phase", "visible_input", "condition", "apprentice_operation",
             "canonical_v80_readback", "failure_if_omitted"], row
        )) | {"source": "V80_FROZEN_INSTRUCTION_FROM_V79_SELECTION"})

    write_tsv("V80_R1_173_CARD_DICTIONARY.tsv", dictionary, [
        "joint_tuple_id", "surface_examples_display_only", "visible_occurrences", "pages",
        "autonomous_operational_value", "optional_questioned_master_gloss",
        "historical_category_attestation", "dictionary_class", "portable_content_value",
        "occurrence_exemplar_status", "memorized_guess_exact", "apprentice_readback",
        "source_lineage", "semantic_ceiling",
    ])
    write_tsv("V80_R1_381_PROSE_EVENT_INTERLINEAR.tsv", event_rows, [
        "event_serial", "event_id", "section", "record_unit_id", "page", "locus",
        "field_id", "statement_id", "joint_tuple_id", "surface_display_only",
        "image_owner_id", "owner_break_before", "owner_reset", "literal_visible_layer",
        "autonomous_primary_token", "optional_questioned_master_gloss",
        "occurrence_bound_exemplar", "source_token_count", "read_action", "line_crossing",
        "terminal_status", "source_class", "source_expansion_confidence", "strongest_rival",
        "strongest_contradiction", "semantic_ceiling", "source_lineage",
    ])
    write_tsv("V80_R1_135_FIELD_EDITION.tsv", field_rows, [
        "field_id", "section", "record_unit_id", "page", "locus", "statement_id",
        "event_count", "event_serials", "image_owner_id", "owner_status", "exact_card_order",
        "autonomous_primary_order", "occurrence_bound_exemplar_sequence",
        "selected_source_field_expansion", "strongest_rival", "strongest_contradiction",
        "semantic_ceiling",
    ])
    write_tsv("V80_R1_116_STATEMENT_EDITION.tsv", statement_rows, [
        "statement_id", "record_unit_id", "section", "page", "statement_ordinal_in_record",
        "constituent_fields", "physical_lines", "event_count", "event_serials",
        "exact_card_order", "autonomous_primary_order", "occurrence_bound_exemplar_sequence",
        "selected_source_sentence", "owner_transition", "visible_owner_resets",
        "cross_field_transitions", "cross_physical_line_transitions", "line_crossing",
        "source_class", "process_or_content_rival", "notation_rival", "repair_cost_0_4",
        "hardest_contradiction", "semantic_ceiling",
    ])
    write_tsv("V80_R1_395_ASTRO_GROUP_EDITION.tsv", astro_rows, [
        "group_serial", "diagram_id", "page", "locus", "event_index", "opaque_local_id",
        "surface_display_only", "local_image_owner", "owner_status", "local_namespace",
        "local_content_class", "autonomous_primary_reading", "occurrence_bound_exemplar",
        "source_status", "meaning_confidence", "strongest_historical_rival",
        "strongest_contradiction", "orientation_status", "f68_f69_mapping",
        "prose_card_import", "semantic_ceiling", "source_lineage",
    ])
    write_tsv("V80_R1_776_UNIFIED_LEDGER.tsv", unified, [
        "unified_serial", "item_kind", "section", "page", "unit_id", "locus", "local_id",
        "opaque_identity", "surface_display_only", "owner", "namespace",
        "autonomous_primary_reading", "optional_master_gloss", "occurrence_bound_exemplar",
        "visible_count", "source_token_count", "strongest_contradiction", "semantic_ceiling",
    ])
    write_tsv("V80_R1_COMPACT_WORKSHOP_MANUAL.tsv", manual, [
        "rule_order", "phase", "visible_input", "condition", "apprentice_operation",
        "canonical_v80_readback", "failure_if_omitted", "source",
    ])
    write_tsv("V80_R1_CONTRADICTION_LEDGER.tsv", contradictions, [
        "contradiction_id", "level", "affected_units", "contradiction", "support_count",
        "severity", "containment", "status", "source",
    ])

    purpose = {r["purpose_id"]: r for r in data["v76_purposes"]}
    records_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in data["v78_records"]:
        records_by_page[r["page"]].append(r)
    instruments_by_page = {r["page"]: r for r in data["v75_instruments"]}
    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for e in event_rows:
        events_by_record[str(e["record_unit_id"])].append(e)

    md: list[str] = [
        "# V80 R1 — kanonische dritte Zehn-Seiten-Ausgabe",
        "",
        "> Kreative, exemplarabhängige Werkstattausgabe; keine Entzifferung und keine Übersetzung.",
        "",
        "## Ein führendes Inhaltsmodell und ein Rivale",
        "",
        f"**Lead (V76, 236 Punkte):** `{LEAD_ID}` — {purpose[LEAD_ID]['period_purpose']}",
        "",
        f"**Einziger Hauptrivale (V76, 235 Punkte):** `{RIVAL_ID}` — {purpose[RIVAL_ID]['period_purpose']}",
        "",
        "Der Ein-Punkt-Abstand ist keine Identifikation. Der Lead verbindet Pflanzenstoff/Zubereitung, "
        "lokale Bad-/Anwendungsstationen und selbständige Himmels-/Kalendernachschläge am sparsamsten. "
        "Der Rivale erklärt Bilddominanz, exemplarweise Zusammenstellung und fehlende Crosspointer fast gleich gut.",
        "",
        "## Exakt memorierte Vermutungen",
        "",
        "- `dcda95c81a5460feb191`: autonom `FORMAL_LINK_OR_SLOT`; nur vom Meister optional "
        "`ET?=UND/AUCH?` (Fi1 1414 belegt nur die Kategorie `et`, nicht diese Zuordnung).",
        "- `b5fcea1eaed06b2f2291`: autonom `FORMAL_RELATION_OR_ENTRY`; nur vom Meister optional "
        "`PER?=DURCH/GEMÄSS?` (Fi1 1414 belegt nur die Kategorie `per`, nicht diese Zuordnung).",
        "- `2f1c5e56e8f0ff459065` und `308e8ea2d5d190c498e8`: formale Kanäle, ausdrücklich keine Wörter.",
        "- Alle übrigen 169 Karten: `EXEMPLAR_VALUE_UNKNOWN`; kein memorierter Wortwert.",
        "- E180/E181: zwei sichtbare Kopien, ein Quelltoken nach der einen positiven generischen "
        "read-once-Regel; lokale Vorwegnahme oder Dittographie bleiben gleichauf.",
        "- Alle konkreten Pflanzen-, Stations- und Himmelswerte unten sind occurrence-gebundene "
        "`[EXEMPLAR:…]`-Vermutungen, keine Kartenbedeutungen.",
        "",
    ]
    for page in FIXED_PAGES:
        md += [f"## {page}", ""]
        if page in PROSE_PAGES:
            for r in records_by_page[page]:
                rec = r["record_unit_id"]
                evs = events_by_record[rec]
                primary = " ".join(str(e["autonomous_primary_token"]) for e in evs)
                readable = replace_optional_words(r["selected_continuous_german_working_reading"])
                md += [
                    f"### {rec} — {r['section']}", "",
                    f"Besitzerfolge: `{r['owner_sequence']}`. Sichtbare Besitzerwechsel: "
                    f"`{r['visible_owner_break_events']}`.", "",
                    "Autonome Formspur:", "",
                    primary,
                    "",
                    "Occurrence-gebundene Quellenausweitung:", "",
                    readable,
                    "",
                    f"Stärkster Rivale: {r['strongest_global_rival']}", "",
                    f"Hauptwiderspruch: {r['strongest_global_contradiction']}", "",
                ]
        else:
            r = instruments_by_page[page]
            md += [
                f"### {r['diagram_id']} — {r['repaired_visual_system']}", "",
                f"Lokale Loci/Gruppen: {r['locus_count']}/{r['group_count']}. "
                f"Orientierung: `{r['orientation_status']}`. Crosspage-Key: `{r['crosspage_mapping']}`. "
                f"Prosaimport: `{r['prose_card_import']}`.", "",
                "Occurrence-gebundene Instrumentenlesung:", "",
                f"[EXEMPLAR:{r['continuous_instrument_description']}]",
                "",
                f"Stärkster Rivale: {r['strongest_competing_instrument']}", "",
                f"Hauptwiderspruch: {r['strongest_counterevidence']}", "",
            ]
    md += [
        "## Kanonische Grenze", "",
        "Die Ausgabe bewahrt 381 sichtbare Prosaereignisse, 135 Felder, 116 Aussagen, "
        "395 Astrogruppen und damit 776 Gruppen. Form, Besitzer, lokale Namespaces und "
        "Grenzen sind rücklesbar. Kein konkreter Inhaltswert ist ohne Masterexemplar rückgewinnbar.", "",
    ]
    (OUT / "V80_R1_TEN_PAGE_READABLE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    report = f"""# V80 R1 — Bericht der kanonischen dritten Ausgabe

Status: `PASS__FORMALLY_TEACHABLE__CONCRETE_CONTENT_MASTER_DEPENDENT`.

## Ergebnis

Diese unabhängige R1-Ausgabe bindet die zentral ausgewählten V69/V73–V79-Artefakte
ohne neue Karte, Form, Bedeutung oder Quelle. Sie enthält exakt 173 Karten, 381
Prosaereignisse, 135 Felder, 116 Aussagen, 395 Astrogruppen und 776 vereinte
Gruppen auf den zehn freigegebenen Seiten. f84 und f84r wurden weder gelesen noch
referenziert.

Autonom liest der Lehrling `{DCDA}` nur als `FORMAL_LINK_OR_SLOT` und
`{B5FCEA}` nur als `FORMAL_RELATION_OR_ENTRY`. `ET?=UND/AUCH?` und
`PER?=DURCH/GEMÄSS?` sind optionale, befragte Meisterglossen aus einer in V77
eingefrorenen Fi1-Kategorie von 1414; sie sind weder durch die Voynichform bewiesen
noch für das Rücklesen nötig. Zwei weitere exakte IDs bleiben formale Nichtwörter.
Alle übrigen 169 Karten haben `EXEMPLAR_VALUE_UNKNOWN`.

## Einfachste Lehrlingsregel um 1420

1. Kopiere Bild/Diagramm und seine freien Räume aus der Vorlage; setze danach Text.
2. Kopiere jede exakte Karte und Grenze, ohne innere Formteile zu deuten.
3. Halte Record, Aussage und sichtbaren Besitzer getrennt; eine Aussage darf die
   physische Linie überschreiten.
4. An einem sichtbaren Besitzerwechsel lösche Stoff, Ziel und Richtung. In B2 sind
   dies exakt E189, E198, E203 und E212.
5. Nur wenn dieselbe exakte Karte am Zeilenende und -anfang, in derselben Aussage,
   beim selben Besitzer und ohne Close steht, bewahre beide sichtbaren Kopien, lies
   aber einmal. Unter 19 Gelegenheiten erfüllt nur E180/E181 diese Regel.
6. Sprich autonom nur die zwei formalen Rollen und zwei Nichtwortkanäle. Für jeden
   konkreten Wert konsultiere den occurrence-gebundenen Eintrag des Masterexemplars.
7. Im Astroblock bleibe im lokalen Rad/Paneel/Slot-Namespace. Erfinde weder Start,
   Richtung, Rotation, f68↔f69-Schlüssel noch einen Prosa-Kartenimport.
8. Bei Unsicherheit kopiere exakt und schreibe `EXEMPLAR_VALUE_UNKNOWN`; ein
   Lehrling darf die Lücke nicht durch Analogie füllen.

## Buchinhalt: genau ein Lead und ein Rivale

Lead: `{LEAD_ID}` — illustriertes therapeutisch-iatromathematisches Praxis- und
Nachschlagekompendium. Rivale: `{RIVAL_ID}` — Natur–Kunst–Himmel-Bildatlas oder
Musterbuch. Der eingefrorene V76-Vorsprung beträgt nur 236:235. Deshalb ist der
Lead die konkrete Arbeitsordnung der Edition, nicht eine historische Identifikation.

## Exakt memorierte Vermutungen

- `{DCDA}` → primär `FORMAL_LINK_OR_SLOT`; optional `ET?=UND/AUCH?` nur vom Meister.
- `{B5FCEA}` → primär `FORMAL_RELATION_OR_ENTRY`; optional `PER?=DURCH/GEMÄSS?` nur vom Meister.
- E180/E181 → zwei sichtbar/ein Quelltoken; lokale Antizipation oder Dittographie.
- Herbal → fünf unbenannte Ganzpflanzenbesitzer mit occurrence-gebundenen Artikeln.
- Bio → lokale Bad-/Anwendungs-/Apparatestationen; kein globaler Fluss.
- Astro → drei lokale Nachschlageinstrumente; Namen, Start und Richtung unbekannt.
- Jedes konkrete Substantiv, Medium, Leiden, Stationsziel und Himmelslabel bleibt
  `[EXEMPLAR:…]`; nichts davon wird aus einer Karte memoriert.

## Widerspruch und Grenze

Der Lead hat keinen sichtbaren Astro→Medizin-Pointer; der Rivale hat keine sichtbare
Natur–Kunst–Himmel-Rubrik. Die Bilder begründen lokale Besitzer, nicht die konkreten
Quellensätze. V79s read-once-Regel besitzt nur ein positives Beispiel. Daher kann
ein Lehrling die 776 Formen rücklesen, aber keinen der konkreten Inhalte ohne
Masterexemplar wiederherstellen.

## Reproduzierbarkeit

`V80_R1_build_canonical_third_edition.py` pinnt alle zentralen Eingaben per SHA-256
und erzeugt sämtliche Tabellen und die lesbare Zehn-Seiten-Ausgabe.
`V80_R1_validate_canonical_third_edition.py` prüft Vollständigkeit, die autonome
Wörterbuchspur, E180/E181, die vier B2-Resets, Astro-Namespaces, Versiegelung und
alle Zählungen. Kein Commit oder Push gehört zu dieser unabhängigen Kandidatenrunde.
"""
    (OUT / "V80_R1_REPORT.md").write_text(report, encoding="utf-8")

    generated = [
        "V80_R1_173_CARD_DICTIONARY.tsv",
        "V80_R1_381_PROSE_EVENT_INTERLINEAR.tsv",
        "V80_R1_135_FIELD_EDITION.tsv",
        "V80_R1_116_STATEMENT_EDITION.tsv",
        "V80_R1_395_ASTRO_GROUP_EDITION.tsv",
        "V80_R1_776_UNIFIED_LEDGER.tsv",
        "V80_R1_TEN_PAGE_READABLE_EDITION.md",
        "V80_R1_COMPACT_WORKSHOP_MANUAL.tsv",
        "V80_R1_CONTRADICTION_LEDGER.tsv",
        "V80_R1_REPORT.md",
    ]
    build_summary = {
        "status": "PASS",
        "fixed_pages": list(FIXED_PAGES),
        "sealed": ["f84", "f84r"],
        "counts": {
            "dictionary_cards": len(dictionary),
            "prose_events": len(event_rows),
            "fields": len(field_rows),
            "statements": len(statement_rows),
            "astro_groups": len(astro_rows),
            "astro_loci": len(data["v75_loci"]),
            "unified_groups": len(unified),
            "records": len(data["v78_records"]),
            "instruments": len(data["v75_instruments"]),
            "pages": len(FIXED_PAGES),
            "contradictions": len(contradictions),
        },
        "dictionary_classes": dict(Counter(str(x["dictionary_class"]) for x in dictionary)),
        "lead_model": LEAD_ID,
        "rival_model": RIVAL_ID,
        "source_hashes": {key: expected for key, (_, expected) in SOURCES.items()},
        "generated_hashes": {name: sha256(OUT / name) for name in generated},
    }
    (OUT / "V80_R1_BUILD_SUMMARY.json").write_text(
        json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
