#!/usr/bin/env python3
"""Build the source-first R2 documentary audit for V77.

The historical inventory is deliberately a literal data block.  The
``freeze-sources`` command reads no Voynich-derived card table and is run before
the card-audit phase is implemented or executed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CARD_DICTIONARY = HERE.parent / "sidequest_theory_candidates_v69" / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
EVENT_TABLE = HERE.parent / "sidequest_theory_candidates_v69" / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
TARGET_FREEZE = HERE / "V77_TARGET_FREEZE.tsv"

LEGACY_CARD_IDS = [
    "0275fbf14e07935b0a45",
    "276a7c2d74d1143446f4",
    "2f1c5e56e8f0ff459065",
    "308e8ea2d5d190c498e8",
    "7a4bb8136330ee4e6e56",
    "7db18b2f0fb7ed0fcfd3",
    "b5df9126607030b95175",
    "b5fcea1eaed06b2f2291",
    "dcda95c81a5460feb191",
    "dd0ecaf5e27d81befffc",
    "de7321bface5628e35d6",
    "dec401773c1f0347793d",
    "e0b630cb1b5df5e7105b",
    "faf321940aed922846a9",
]

CONTEXT_AUDIT = {
    "0275fbf14e07935b0a45": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "ACTION_TEMPER is repeated in four Biological records, but that template was written using the exposed mnemonic."),
    "276a7c2d74d1143446f4": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "ACTION_APPLY is repeated in Herbal and Biological records; this is internal consistency of the creative ledger, not documentary attestation."),
    "2f1c5e56e8f0ff459065": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "PARAMETER_ASSIGN recurs in all eleven prose records; the formal channel may remain a nonword, but MASS is unattested."),
    "308e8ea2d5d190c498e8": ("FORMAL_ONLY_BY_DEFINITION", "The retained local relation-slot prompt is explicitly not a word value."),
    "7a4bb8136330ee4e6e56": ("BROAD_TEMPLATE_STABLE_NOT_INDEPENDENT", "LINK_ACTIVE spans fresh mixture, salve mixture and generic record-local active item; ANSATZ is therefore broader than a stable object noun."),
    "7db18b2f0fb7ed0fcfd3": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "TERMINAL_FLUSH repeats in three Biological records, but the entries were authored under SPUELEN."),
    "b5df9126607030b95175": ("CONTEXT_DRIFT", "One Herbal context says clear condition while Biological contexts collapse to an unspecified local test state."),
    "b5fcea1eaed06b2f2291": ("FORMAL_ONLY_BY_DEFINITION", "The retained standard-slot prompt is explicitly not a word value."),
    "dcda95c81a5460feb191": ("FORMAL_ONLY_BY_DEFINITION", "The retained active-work-state linking prompt is explicitly not a word value."),
    "dd0ecaf5e27d81befffc": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "TARGET_ASSIGN recurs in Herbal and Biological records, but the template was authored under ZIEL."),
    "de7321bface5628e35d6": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "TERMINAL_DRAIN repeats in Biological records only and remains closure-confounded."),
    "dec401773c1f0347793d": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "SELECT_PREVIOUS has two cross-section occurrences, both inherited from the exposed card reading."),
    "e0b630cb1b5df5e7105b": ("CONTEXT_DRIFT", "Flower opening, general readiness and generic Biological test states do not establish one lexical value."),
    "faf321940aed922846a9": ("TEMPLATE_STABLE_NOT_INDEPENDENT", "SELECT_PART has two cross-section occurrences, both inherited from the exposed card reading."),
    "b921a237be883a820352": ("NONINVARIANT_EXEMPLAR_CONTEXTS", "Eighteen occurrences span collect, add, warm, stir, preserve, take, indication, application and deictic-owner expansions."),
    "bc4f1f5c006c74a4d26d": ("RECURRENT_CONTEXT_PATTERN_NO_FROZEN_GLOSS", "Twelve Biological contexts share a stand/readiness/closure expansion; no source-first word category was proposed or attested."),
    "6f7ff8287eddf4da9fdb": ("CONTEXT_DRIFT", "Ten Biological mix expansions conflict with one Herbal wring-and-settle expansion."),
    "7d25241b0e56c836372a": ("BROAD_PATTERN_NO_FROZEN_GLOSS", "The ten Biological terminal actions cover sitting in a bath, washing/bathing, and dipping a cloth."),
    "1645e612504fcef59ced": ("RECURRENT_CONTEXT_PATTERN_NO_FROZEN_GLOSS", "Seven Biological contexts share insertion of a measured portion; no historical entry licenses a word."),
    "4d4559019a961b834aa1": ("CONTEXT_DRIFT", "Same-source/deictic expansions coexist with an instruction to combine two fractions."),
    "259b2b3b0bf859882e2c": ("RECURRENT_CONTEXT_PATTERN_NO_FROZEN_GLOSS", "Four Biological contexts share terminal rinsing of a used vessel or run; no historical entry licenses a word."),
    "2cc054357a929df85f64": ("NONINVARIANT_SINGLE_RECORD_CONTEXTS", "Four H5 occurrences are assigned collect, crush, dry, and add-honey actions."),
    "2cc8bb3c2af19607888f": ("RECURRENT_CONTEXT_PATTERN_NO_FROZEN_GLOSS", "Four contexts share a connected-run construction, but no lexical value was frozen or attested."),
    "28ffbc88b97772a75f1e": ("RECURRENT_CONTEXT_PATTERN_NO_FROZEN_GLOSS", "Three Biological contexts share set-aside-in-covered-vessel closure, without a source-first word attestation."),
}

MEISTER_1906_CITATION = (
    "Aloys Meister, Die Geheimschrift im Dienste der paepstlichen Kurie von "
    "ihren Anfaengen bis zum Ende des XVI. Jahrhunderts, Quellen und "
    "Forschungen aus dem Gebiete der Geschichte 11 (Paderborn: Ferdinand "
    "Schoeningh, 1906), pp. 171-175"
)
MEISTER_1906_URL = "https://archive.org/details/diegeheimschrift00meis/page/173/mode/1up"
MEISTER_1902_CITATION = (
    "Aloys Meister, Die Anfaenge der modernen diplomatischen Geheimschrift: "
    "Beitraege zur Geschichte der italienischen Kryptographie des XV. "
    "Jahrhunderts (Paderborn: Ferdinand Schoeningh, 1902)"
)
MEISTER_1902_URL = (
    "https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA38"
)


SOURCE_ROWS = [
    {
        "source_id": "SRC_LAVINDE_1379_KEY13",
        "historical_key_identity": "Gabriel de Lavinde key 13, Zifera [Anonym]",
        "archive_shelfmark": "Archivio Apostolico Vaticano, Collect. 393, ff. 166-181 (collection range)",
        "date_or_dated_correspondence": "1379",
        "codebook_type": "substitution alphabet plus nomenclator",
        "source_language": "Latin with Italian/proper-name forms",
        "edition_location": "Meister 1906, p. 173, key no. 13",
        "entry_mapping_status": "EXACT_ENTRIES_ADMITTED_WHERE_CODE_IS_TEXTUALLY_UNAMBIGUOUS",
        "admitted_entry_count": "40",
        "citation": MEISTER_1906_CITATION,
        "stable_locator": MEISTER_1906_URL,
        "source_object_sha256": "5d38b02e1dfd75803fbe645dd70e73ba77ec62fee9dc9a0955522732d37d6c90",
        "notes": "Scholarly documentary edition reproduces alphabet and nomenclator; visually ambiguous sign rows are not admitted.",
    },
    {
        "source_id": "SRC_LAVINDE_1379_KEY26",
        "historical_key_identity": "Gabriel de Lavinde key 26, Ziffera Guigonis Iarenti de Aquis",
        "archive_shelfmark": "Archivio Apostolico Vaticano, Collect. 393, ff. 166-181 (collection range)",
        "date_or_dated_correspondence": "1379",
        "codebook_type": "vowel substitution plus nomenclator",
        "source_language": "Latin with southern French/Italian forms",
        "edition_location": "Meister 1906, p. 175, key no. 26",
        "entry_mapping_status": "EXACT_ENTRIES_ADMITTED_WHERE_CODE_IS_TEXTUALLY_UNAMBIGUOUS",
        "admitted_entry_count": "8",
        "citation": MEISTER_1906_CITATION,
        "stable_locator": "https://archive.org/details/diegeheimschrift00meis/page/175/mode/1up",
        "source_object_sha256": "5d38b02e1dfd75803fbe645dd70e73ba77ec62fee9dc9a0955522732d37d6c90",
        "notes": "Only rows whose printed code can be transcribed without guessing are admitted; ornate or ambiguous signs remain unavailable.",
    },
    {
        "source_id": "SRC_MANTUA_1395_CUM_PAULO",
        "historical_key_identity": "Cum Paulo 1395",
        "archive_shelfmark": "Archivio di Stato di Mantova, E. V. 3",
        "date_or_dated_correspondence": "1395; associated letters dated 27 and 28 November 1395",
        "codebook_type": "substitution key with nulls; no nomenclator printed for this key",
        "source_language": "Latin",
        "edition_location": "Meister 1902, pp. 38-40, example 1",
        "entry_mapping_status": "KEY_VERIFIED_NO_ADMISSIBLE_WORD_ENTRY",
        "admitted_entry_count": "0",
        "citation": MEISTER_1902_CITATION + ", pp. 38-40",
        "stable_locator": MEISTER_1902_URL,
        "source_object_sha256": "5fc9d442dbe4a075c0494a22044d762cca6f82dd3938434ebba208b07810c815",
        "notes": "A real in-period cipher-key control; it supplies no exact word-code row and therefore attests no dictionary category.",
    },
    {
        "source_id": "SRC_MANTUA_1401_SIMEONE",
        "historical_key_identity": "Cum Simeone de Crema, Zifra ultima 1401",
        "archive_shelfmark": "Archivio di Stato di Mantova, E. V. 3",
        "date_or_dated_correspondence": "1401",
        "codebook_type": "homophonic/substitution key",
        "source_language": "Latin",
        "edition_location": "Meister 1902, p. 41, example 2",
        "entry_mapping_status": "KEY_VERIFIED_NO_ADMISSIBLE_WORD_ENTRY",
        "admitted_entry_count": "0",
        "citation": MEISTER_1902_CITATION + ", p. 41",
        "stable_locator": "https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA41",
        "source_object_sha256": "5fc9d442dbe4a075c0494a22044d762cca6f82dd3938434ebba208b07810c815",
        "notes": "The reproduced key is not a source-language word-to-code list; no word entry is manufactured from its title or alphabet.",
    },
    {
        "source_id": "SRC_MANTUA_1404_NUMERIC_NOMENCLATOR",
        "historical_key_identity": "Mantuan 1404 nomenclator reported with codes 1-38",
        "archive_shelfmark": "Archivio di Stato di Mantova, E. V. 3 (collection; exact item not supplied in edition narrative)",
        "date_or_dated_correspondence": "1404",
        "codebook_type": "numeric nomenclator",
        "source_language": "not recoverable from cited narrative",
        "edition_location": "Meister 1902, p. 39",
        "entry_mapping_status": "NOMENCLATOR_VERIFIED_ENTRY_MAPPING_UNAVAILABLE",
        "admitted_entry_count": "0",
        "citation": MEISTER_1902_CITATION + ", p. 39",
        "stable_locator": "https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA39",
        "source_object_sha256": "5fc9d442dbe4a075c0494a22044d762cca6f82dd3938434ebba208b07810c815",
        "notes": "The edition states that codes 1-38 occur but does not print the 38 plaintext mappings here; none is inferred.",
    },
    {
        "source_id": "SRC_PISA_1442_ABBREVIATIONS",
        "historical_key_identity": "Pisan-archive key for Giuseppe Gozzoli and Antonio Lamberti",
        "archive_shelfmark": "Archivio di Stato di Pisa, key associated with Cod. C. 29-30 (edition description)",
        "date_or_dated_correspondence": "7 November 1442",
        "codebook_type": "cipher alphabet plus seven coded abbreviations",
        "source_language": "Italian/Latin abbreviations",
        "edition_location": "Meister 1902, pp. 57-59, Pisa example",
        "entry_mapping_status": "SIGN_LIST_VERIFIED_BUT_EXACT_SIGNS_NOT_ADMITTED_FROM_OCR",
        "admitted_entry_count": "0",
        "citation": MEISTER_1902_CITATION + ", pp. 57-59",
        "stable_locator": "https://books.google.com/books?id=8-Ux0geGhPIC&pg=PA58",
        "source_object_sha256": "5fc9d442dbe4a075c0494a22044d762cca6f82dd3938434ebba208b07810c815",
        "notes": "The seven plaintext abbreviations are printed, but this audit does not admit them because the corresponding graphic signs were not independently transcribed from a facsimile.",
    },
]


KEY13_ENTRIES = [
    ("cardinalis", "3p"),
    ("rex Anglie", "gl"),
    ("Ambien. Card.", "qr"),
    ("Rex Aragonii", "kl"),
    ("dux Andegaviensis", "ml"),
    ("dux Bituricensis", "ty"),
    ("dux Burgundie", "llm"),
    ("comes Saban.", "lt"),
    ("comes Virtutum", "ma"),
    ("d. Barnabos", "ci"),
    ("card. Mediolanus", "ff"),
    ("dux Austrie", "bl"),
    ("Dux Bavarie", "ami"),
    ("Cavallinus", "co"),
    ("ep. Vercellensis", "fi"),
    ("d. octo", "coi"),
    ("Regina", "ba"),
    ("Imperator", "aa"),
    ("Rex Ungarie", "gb"),
    ("Intrusus", "ap"),
    ("Sequaces sui", "br"),
    ("Sicilia", "fa"),
    ("Mons Pesulanus", "e3"),
    ("Ianuensis", "de"),
    ("Veneti", "vie"),
    ("Andreas", "bo"),
    ("Monachus", "an"),
    ("Florentini", "pe"),
    ("Prefectus", "al"),
    ("Papia", "tp"),
    ("Mediolanum", "lo"),
    ("Gentes armorum", "gm"),
    ("Matrimonium", "ln"),
    ("pax", "pR"),
    ("D. Blancha", "no"),
    ("D. Agabitus de Colupna", "fu"),
    ("D. Violanta", "va"),
    ("De Vicomitibus Ludovicus", "su"),
    ("Antonius Pontis", "pro"),
    ("D. Antonius de Gutuariis", "pr"),
]

KEY26_ENTRIES = [
    ("Dominus fulco de Agonto [?]", "bq"),
    ("Domin. Leonardus de Aflicto", "ff"),
    ("Massilia", "mm"),
    ("Napoli", "mh"),
    ("Nicia", "ma"),
    ("Lo cancelier", "ph"),
    ("Lo conte de caserta", "aq"),
    ("Guigo Iarenti", "pq"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_tsv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_entries() -> list[dict]:
    rows: list[dict] = []
    for index, (entry, code) in enumerate(KEY13_ENTRIES, 1):
        confidence = (
            "MEDIUM_HIGH_EDITION_GLYPH_NORMALIZED"
            if entry in {"Ambien. Card.", "pax"}
            else "HIGH_EDITION_PRINT_SEQUENCE"
        )
        rows.append(
            {
                "inventory_entry_id": f"LAV13_{index:03d}",
                "source_id": "SRC_LAVINDE_1379_KEY13",
                "exact_source_language_entry": entry,
                "opaque_code_or_sign": code,
                "historical_key_identity": "Gabriel de Lavinde key 13, Zifera [Anonym]",
                "archive_shelfmark": "Archivio Apostolico Vaticano, Collect. 393, ff. 166-181 (collection range)",
                "date_or_dated_correspondence": "1379",
                "facsimile_or_edition_location": "Meister 1906, p. 173, key no. 13, nomenclator row",
                "codebook_type": "substitution alphabet plus nomenclator",
                "citation": MEISTER_1906_CITATION + ", p. 173",
                "stable_locator": MEISTER_1906_URL,
                "transcription_confidence": confidence,
                "admission_status": "ADMITTED_EXACT_HISTORICAL_ENTRY",
                "granularity_ceiling": "HISTORICAL_DICTIONARY_GRANULARITY_ONLY_NOT_VOYNICH_IDENTITY",
            }
        )
    for index, (entry, code) in enumerate(KEY26_ENTRIES, 1):
        confidence = (
            "MEDIUM_EDITORIAL_READING_UNCERTAIN_RETAINED_LITERALLY"
            if "[?]" in entry
            else "HIGH_EDITION_PRINT_SEQUENCE"
        )
        rows.append(
            {
                "inventory_entry_id": f"LAV26_{index:03d}",
                "source_id": "SRC_LAVINDE_1379_KEY26",
                "exact_source_language_entry": entry,
                "opaque_code_or_sign": code,
                "historical_key_identity": "Gabriel de Lavinde key 26, Ziffera Guigonis Iarenti de Aquis",
                "archive_shelfmark": "Archivio Apostolico Vaticano, Collect. 393, ff. 166-181 (collection range)",
                "date_or_dated_correspondence": "1379",
                "facsimile_or_edition_location": "Meister 1906, p. 175, key no. 26, nomenclator row",
                "codebook_type": "vowel substitution plus nomenclator",
                "citation": MEISTER_1906_CITATION + ", p. 175",
                "stable_locator": "https://archive.org/details/diegeheimschrift00meis/page/175/mode/1up",
                "transcription_confidence": confidence,
                "admission_status": "ADMITTED_EXACT_HISTORICAL_ENTRY",
                "granularity_ceiling": "HISTORICAL_DICTIONARY_GRANULARITY_ONLY_NOT_VOYNICH_IDENTITY",
            }
        )
    return rows


def freeze_sources() -> None:
    source_path = HERE / "V77_R2_HISTORICAL_SOURCE_CORPUS.tsv"
    entry_path = HERE / "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv"
    _write_tsv(source_path, SOURCE_ROWS, list(SOURCE_ROWS[0]))
    entries = source_entries()
    _write_tsv(entry_path, entries, list(entries[0]))
    freeze = {
        "experiment": "V77_R2",
        "phase": "SOURCE_FIRST_FREEZE",
        "frozen_at": "2026-08-22",
        "source_selection_rule": "real surviving 1370-1450 key or coded-sign-list located before card comparison",
        "source_count": len(SOURCE_ROWS),
        "admitted_exact_entry_count": len(entries),
        "historical_source_corpus_sha256": _sha256(source_path),
        "historical_entry_inventory_sha256": _sha256(entry_path),
        "edition_object_hashes": {
            "meister_1906_pdf": "5d38b02e1dfd75803fbe645dd70e73ba77ec62fee9dc9a0955522732d37d6c90",
            "meister_1902_access_copy_html": "5fc9d442dbe4a075c0494a22044d762cca6f82dd3938434ebba208b07810c815",
        },
        "card_tables_read_by_this_phase": [],
        "routing_level_legacy_handle_exposure_due_required_current_theory_read": True,
        "desired_word_search_performed": False,
        "ordinary_recipe_prose_admitted": False,
        "f84_opened": False,
        "f84r_opened": False,
    }
    (HERE / "V77_R2_SOURCE_FREEZE.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def freeze_candidates() -> None:
    """Freeze legacy IDs plus top recurrent non-legacy IDs without gloss access."""
    source_freeze_path = HERE / "V77_R2_SOURCE_FREEZE.json"
    source_freeze = json.loads(source_freeze_path.read_text(encoding="utf-8"))
    assert _sha256(HERE / "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv") == source_freeze[
        "historical_entry_inventory_sha256"
    ]
    counts: dict[str, int] = {}
    with CARD_DICTIONARY.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        assert reader.fieldnames is not None
        assert "joint_tuple_id" in reader.fieldnames and "occurrences" in reader.fieldnames
        for row in reader:
            # Intentionally access no semantic/mnemonic/formal column here.
            counts[row["joint_tuple_id"]] = int(row["occurrences"])
    assert len(counts) == 173
    assert set(LEGACY_CARD_IDS) <= counts.keys()
    extras = sorted(
        ((count, card_id) for card_id, count in counts.items() if card_id not in LEGACY_CARD_IDS),
        key=lambda item: (-item[0], item[1]),
    )[:10]
    rows = []
    for rank, card_id in enumerate(LEGACY_CARD_IDS, 1):
        rows.append(
            {
                "candidate_id": f"LEGACY_{rank:02d}",
                "joint_tuple_id": card_id,
                "selection_class": "FROZEN_LEGACY_CONTROL_CARD",
                "selection_rank": str(rank),
                "training_occurrences": str(counts[card_id]),
                "selection_rule": "frozen V77 legacy fourteen; identity only",
            }
        )
    for rank, (count, card_id) in enumerate(extras, 1):
        rows.append(
            {
                "candidate_id": f"FREQ_EXTRA_{rank:02d}",
                "joint_tuple_id": card_id,
                "selection_class": "FREQUENCY_SELECTED_RECURRENT_EXTRA",
                "selection_rank": str(rank),
                "training_occurrences": str(count),
                "selection_rule": "top 10 non-legacy exact cards by occurrences; descending count then tuple ID",
            }
        )
    candidate_path = HERE / "V77_R2_FREQUENCY_CANDIDATE_FREEZE.tsv"
    _write_tsv(candidate_path, rows, list(rows[0]))
    freeze = {
        "experiment": "V77_R2",
        "phase": "FREQUENCY_CANDIDATE_FREEZE_AFTER_SOURCE_FREEZE",
        "frozen_at": "2026-08-22",
        "source_freeze_sha256": _sha256(source_freeze_path),
        "card_dictionary_sha256": _sha256(CARD_DICTIONARY),
        "legacy_candidate_count": len(LEGACY_CARD_IDS),
        "frequency_extra_count": len(extras),
        "candidate_inventory_sha256": _sha256(candidate_path),
        "features_read_for_extra_selection": ["joint_tuple_id", "occurrences"],
        "tie_break": "joint_tuple_id ascending",
        "authoritative_target_manifest_sha256": _sha256(HERE / "V77_TARGET_FREEZE.tsv"),
        "semantic_columns_read_for_extra_selection": [],
        "f84_opened": False,
        "f84r_opened": False,
    }
    (HERE / "V77_R2_FREQUENCY_CANDIDATE_FREEZE.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def audit_cards() -> None:
    """Compare the frozen candidates with the already-frozen source corpus."""
    source_freeze = json.loads((HERE / "V77_R2_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    candidate_freeze = json.loads(
        (HERE / "V77_R2_FREQUENCY_CANDIDATE_FREEZE.json").read_text(encoding="utf-8")
    )
    assert _sha256(HERE / "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv") == source_freeze[
        "historical_entry_inventory_sha256"
    ]
    assert _sha256(TARGET_FREEZE) == candidate_freeze["authoritative_target_manifest_sha256"]

    target_rows = _read_tsv(TARGET_FREEZE)
    assert len(target_rows) == 24
    target_ids = [row["joint_tuple_id"] for row in target_rows]
    assert target_ids == [row["joint_tuple_id"] for row in _read_tsv(HERE / "V77_R2_FREQUENCY_CANDIDATE_FREEZE.tsv")]

    cards = {row["joint_tuple_id"]: row for row in _read_tsv(CARD_DICTIONARY)}
    events = [row for row in _read_tsv(EVENT_TABLE) if row["joint_tuple_id"] in set(target_ids)]
    assert len(events) == 197
    by_card: dict[str, list[dict]] = {card_id: [] for card_id in target_ids}
    for event in events:
        by_card[event["joint_tuple_id"]].append(event)

    decisions: list[dict] = []
    occurrence_rows: list[dict] = []
    withdrawals: list[dict] = []
    target_by_id = {row["joint_tuple_id"]: row for row in target_rows}
    for target in target_rows:
        card_id = target["joint_tuple_id"]
        card = cards[card_id]
        old_mnemonic = card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        formal_prompt = card["strict_control_prompt"]
        is_formal_only = old_mnemonic in {"UNKNOWN", "NONE", ""} and formal_prompt not in {"NONE", ""}
        is_legacy_mnemonic = old_mnemonic not in {"UNKNOWN", "NONE", ""}
        if is_formal_only:
            proposed = "[FORMAL:" + formal_prompt + "]"
            proposed_kind = "FORMAL_PROMPT_EXPLICITLY_NOT_WORD"
            final_status = "FORMAL_LABEL_NOT_WORD"
        elif is_legacy_mnemonic:
            proposed = old_mnemonic
            proposed_kind = "EXPOSED_CREATIVE_WORKING_MNEMONIC"
            final_status = "EXEMPLAR_VALUE_UNKNOWN"
        else:
            proposed = "[EXEMPLAR_VALUE_UNKNOWN]"
            proposed_kind = "NO_PREEXISTING_WORD_GLOSS"
            final_status = "EXEMPLAR_VALUE_UNKNOWN"
        context_status, context_reason = CONTEXT_AUDIT[card_id]
        card_events = by_card[card_id]
        assert len(card_events) == int(target["occurrences"])
        sections = sorted({"HERBAL" if row["record_unit_id"].startswith("H") else "BIOLOGICAL" for row in card_events})
        records = sorted({row["record_unit_id"] for row in card_events})
        event_templates = sorted({row["event_template"] for row in card_events})
        decisions.append(
            {
                "target_rank": target["target_rank"],
                "selection_class": target["selection_class"],
                "anonymous_exact_card_id": card_id,
                "surface_examples_display_only": target["surface_examples"],
                "occurrences_audited": str(len(card_events)),
                "pages": target["pages"],
                "records": "|".join(records),
                "sections": "|".join(sections),
                "pre_audit_editorial_value": proposed,
                "proposed_value_kind": proposed_kind,
                "preexisting_formal_prompt": formal_prompt,
                "formal_channel_final_status": (
                    "FORMAL_LABEL_NOT_WORD" if formal_prompt not in {"NONE", ""} else "NONE"
                ),
                "event_templates_in_exposed_ledger": "|".join(event_templates),
                "occurrence_invariance_result": context_status,
                "occurrence_invariance_reason": context_reason,
                "historical_inventory_match": "NONE_IN_FROZEN_48_ENTRY_INVENTORY",
                "matched_inventory_entry_id": "NONE",
                "exact_source_language_entry": "NONE",
                "historical_key_identity": "NONE",
                "archive_shelfmark": "NONE",
                "date_or_dated_correspondence": "NONE",
                "edition_location": "NONE",
                "codebook_type": "NONE",
                "opaque_code_or_sign": "NONE",
                "citation_and_locator": "NONE",
                "attestation_confidence": "NO_ATTESTATION",
                "final_decision": final_status,
                "decision_reason": (
                    "Formal operation remains usable only as an editorial nonword label."
                    if is_formal_only
                    else "No exact historical codebook entry supplies the proposed category with all mandatory documentary fields."
                ),
                "interpretation_ceiling": "NO_WORD_LEXEME_SOUND_LANGUAGE_PLAINTEXT_OR_SEMANTIC_IDENTITY_CLAIM",
            }
        )
        if is_legacy_mnemonic:
            withdrawals.append(
                {
                    "anonymous_exact_card_id": card_id,
                    "withdrawn_editorial_handle": old_mnemonic,
                    "replacement": "EXEMPLAR_VALUE_UNKNOWN",
                    "formal_nonword_retained": formal_prompt if formal_prompt not in {"NONE", ""} else "NONE",
                    "historical_reason": "No matching exact entry in the frozen source-first 1379-1442 key corpus.",
                    "occurrence_reason": context_reason,
                    "effective_scope": "all fixed-ten-page prose occurrences",
                }
            )
        for event in card_events:
            occurrence_rows.append(
                {
                    "target_rank": target["target_rank"],
                    "anonymous_exact_card_id": card_id,
                    "event_serial": event["event_serial"],
                    "page": event["page"],
                    "locus": event["locus"],
                    "record_unit_id": event["record_unit_id"],
                    "field_id": event["field_id"],
                    "statement_id": event["statement_id"],
                    "surface_display_only": event["surface_display_only"],
                    "formal_formula_opaque": event["formal_formula_opaque"],
                    "terminal_status": event["terminal_status"],
                    "pre_audit_mnemonic": event["selected_exact_mnemonic"],
                    "pre_audit_formal_prompt": event["strict_formal_prompt"],
                    "event_template_in_exposed_ledger": event["event_template"],
                    "creative_context_excerpt": event["iatromedical_source_segment"],
                    "practical_context_excerpt": event["practical_source_segment"],
                    "context_audit_status": context_status,
                    "historical_attestation_status": "NONE_IN_FROZEN_SOURCE_INVENTORY",
                    "final_card_status": final_status,
                    "audit_note": "Occurrence inspected; exposed context is not an independent source attestation.",
                }
            )

    decision_path = HERE / "V77_R2_CARD_DECISIONS.tsv"
    occurrence_path = HERE / "V77_R2_OCCURRENCE_AUDIT.tsv"
    withdrawal_path = HERE / "V77_R2_WITHDRAWALS.tsv"
    _write_tsv(decision_path, decisions, list(decisions[0]))
    _write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))
    _write_tsv(withdrawal_path, withdrawals, list(withdrawals[0]))

    # A header-only file is intentional: documentary gates admit zero card words.
    attestation_columns = [
        "anonymous_exact_card_id",
        "minimal_proposed_editorial_gloss",
        "exact_source_language_entry",
        "historical_key_identity_or_archive_shelfmark",
        "date_or_dated_correspondence",
        "facsimile_edition_folio_page_or_entry",
        "codebook_type",
        "opaque_code_or_sign",
        "full_citation_and_stable_locator",
        "confidence",
        "granularity_ceiling",
    ]
    _write_tsv(HERE / "V77_R2_ATTESTED_CARD_ROWS.tsv", [], attestation_columns)

    result = {
        "experiment": "V77_R2",
        "status": "COMPLETE_STRICT_DOCUMENTARY_FAILURE",
        "decision": "NO_V77_R2_CARD_WORD_ATTESTED",
        "source_count": len(SOURCE_ROWS),
        "frozen_exact_historical_entries": len(source_entries()),
        "target_cards": len(decisions),
        "occurrences_audited": len(occurrence_rows),
        "withdrawn_mnemonic_handles": len(withdrawals),
        "formal_only_cards": sum(row["final_decision"] == "FORMAL_LABEL_NOT_WORD" for row in decisions),
        "formal_labels_retained_as_nonwords": sum(row["formal_channel_final_status"] == "FORMAL_LABEL_NOT_WORD" for row in decisions),
        "attested_card_words": 0,
        "historical_entry_inventory_sha256": _sha256(HERE / "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv"),
        "target_manifest_sha256": _sha256(TARGET_FREEZE),
        "card_decisions_sha256": _sha256(decision_path),
        "occurrence_audit_sha256": _sha256(occurrence_path),
        "withdrawals_sha256": _sha256(withdrawal_path),
        "ordinary_recipe_prose_used_as_attestation": False,
        "surface_similarity_used": False,
        "desired_word_search_used": False,
        "f84_opened": False,
        "f84r_opened": False,
        "interpretation_ceiling": "creative formal/exemplar audit only; no word, lexeme, sound, language, plaintext or translation",
    }
    (HERE / "V77_R2_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["freeze-sources", "freeze-candidates", "audit-cards"])
    args = parser.parse_args()
    if args.phase == "freeze-sources":
        freeze_sources()
    elif args.phase == "freeze-candidates":
        freeze_candidates()
    elif args.phase == "audit-cards":
        audit_cards()


if __name__ == "__main__":
    main()
