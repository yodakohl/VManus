#!/usr/bin/env python3
"""Recompose the strongest local singleton cards from the selected workshop kit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
SOURCE = PARENT / "sidequest_semantic_shared_headword_resolution"
LEXICON = PARENT / "sidequest_semantic_open_middle_lexicon"

WORDS_IN = SOURCE / "APPRENTICE_68_RESOLVED_WORD_DECK.tsv"
PHRASES_IN = SOURCE / "APPRENTICE_116_RESOLVED_PHRASES.tsv"
EVENTS_IN = LEXICON / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv"

DISPOSITION_OUT = HERE / "SINGLETON_55_DISPOSITION.tsv"
COMPONENTS_OUT = HERE / "RESCUED_COMPONENT_LEXICON.tsv"
WORDS_OUT = HERE / "APPRENTICE_68_RECOMPOSED_WORD_DECK.tsv"
PHRASES_OUT = HERE / "APPRENTICE_116_RECOMPOSED_PHRASES.tsv"
RECORDS_OUT = HERE / "APPRENTICE_11_RECOMPOSED_RECORDS.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


# surface -> status, composition, new compact reading, confidence, reason
# These are deliberately workshop readings: the test is whether known pieces
# replace a sentence-sized local guess with a shorter executable instruction.
RESCUES = {
    "chary": ("PRODUCTIVE_RESCUE", "AR_FROM+Y_CURRENT", "daraus", "HIGH", "The already taught AR source card is followed by the current-item Y; the following statement receives that product."),
    "raly": ("PRODUCTIVE_RESCUE", "AL_TO+Y_CURRENT", "diesen Posten dorthin", "HIGH", "The known AL target plus Y item fits the transfer chain better than an unattested side-arm noun."),
    "choy": ("PRODUCTIVE_RESCUE", "HO_INGREDIENT+Y_CURRENT", "diese Zutat", "HIGH", "The HO ingredient family plus Y item supplies the object before SET and APPLY; no wash verb is needed."),
    "sheckhy": ("PRODUCTIVE_RESCUE", "CKH_THROUGH+E_SHORT+Y_CURRENT", "kurz durchleiten", "HIGH", "It extends the CKH through-pass grid with the already taught short E grade and Y item."),
    "qockhey": ("PRODUCTIVE_RESCUE", "OK_SET+CKH_THROUGH+E_SHORT+Y_CURRENT", "kurzen Durchlauf ansetzen", "HIGH", "OK plus CKH plus short grade plus item predicts a short pass; the old overflow noun was owner-derived."),
    "lar": ("PRODUCTIVE_RESCUE", "L_OUT+AR_FROM", "von dort abfuehren", "HIGH", "The outward L routine and AR source produce a complete one-card discharge instruction."),
    "lcheey": ("PRODUCTIVE_RESCUE", "L_OUT+CHEEY_CLEAR_FLOW", "Klarlauf abfuehren", "HIGH", "L outward action attaches directly to the learned CHEEY clear-flow card."),
    "solkaiin": ("PRODUCTIVE_RESCUE", "SOLK_COLLECT+AIIN_MEASURE", "bis Sollmass sammeln", "HIGH", "The collection family plus target measure predicts collection to measure; no cloth noun is required."),
    "shecthy": ("PRODUCTIVE_RESCUE", "CTH_READY+E_SHORT+Y_CURRENT", "kurz bereit halten", "HIGH", "The ready core, short grade and current item form a regular state instruction rather than hand-warm."),
    "chckhal": ("PRODUCTIVE_RESCUE", "CKH_THROUGH+AL_TO", "zur Zielstelle durchleiten", "HIGH", "CKH through-pass plus AL target supplies the missing path and target in the local sequence."),
    "sheckhal": ("PRODUCTIVE_RESCUE", "CKH_THROUGH+E_SHORT+AL_TO", "kurz zur Zielstelle durchleiten", "HIGH", "The same through-to-target program receives the short E grade; the old middle-measure gloss duplicated AIIN."),
    "qotedaiin": ("PRODUCTIVE_RESCUE", "OT_FOLLOW+E_SHORT+AIIN_MEASURE", "kurzes Folgemass", "HIGH", "OT follow plus short grade plus target measure predicts the first member of a three-step follow-up sequence."),
    "cheedar": ("PRODUCTIVE_RESCUE", "CHED_TRANSFER+AR_FROM", "von dort umsetzen", "HIGH", "CHED transfer plus AR source is a regular directional command; the basin came only from the picture."),
    "qolchey": ("PRODUCTIVE_RESCUE", "OL_CONTINUE+Y_CURRENT", "diesen Posten weiterfuehren", "HIGH", "OL continue plus the current-item card replaces an unsupported working-basin noun."),
    "qotchol": ("PRODUCTIVE_RESCUE", "OT_FOLLOW+OL_CONTINUE", "danach weiterfuehren", "HIGH", "The visible OT and OL order operators compose directly; no heat core is present."),
    "oltchy": ("PRODUCTIVE_RESCUE", "OL_CONTINUE+CTH_READY+Y_CURRENT", "bereit weiterfuehren", "HIGH", "OL continue plus CTH ready plus Y item predicts a ready-item continuation, not warming."),
    "schoal": ("PRODUCTIVE_RESCUE", "HO_INGREDIENT+AL_TO", "Zutat dorthin", "HIGH", "The already selected ingredient and target components replace the unsupported wine-decoction noun."),
    "shecthedchy": ("PRODUCTIVE_RESCUE", "CTH_READY+CHED_TRANSFER+Y_CURRENT", "bereiten Posten umsetzen", "HIGH", "The ready and transfer cores plus Y item form a regular executable command."),
    "octheol": ("PRODUCTIVE_RESCUE", "CTH_READY+OL_CONTINUE", "bereit weiterfuehren", "HIGH", "Ready plus continue fits the measured process chain; no independent equality operator is needed."),
    "qoctholy": ("PRODUCTIVE_RESCUE", "CTH_READY+OL_CONTINUE+Y_CURRENT", "bereiten Posten weiterfuehren", "HIGH", "The same ready-continuation construction takes the current item; pressing was an isolated story gloss."),
    "teol": ("PRODUCTIVE_RESCUE", "E_SHORT+OL_CONTINUE", "kurz weiterfuehren", "HIGH", "Short grade plus continuation fits between target and terminal transfer; no tap noun is needed."),
    "keol": ("PRODUCTIVE_RESCUE", "E_SHORT+OL_CONTINUE", "kurz weiterfuehren", "HIGH", "Short grade plus continuation fits between follow-up item and target measure; no dose noun is needed."),
    "cheeety": ("PARTIAL_RESCUE", "EEE_FULL+Y_CURRENT", "vollstaendig halten", "MEDIUM", "The visible EEE grade and final item wrapper are useful, but the internal carrier remains local."),
    "sheey": ("PARTIAL_RESCUE", "SH_REST+EE_LONG+Y_CURRENT", "laenger ruhen", "MEDIUM", "It extends the learned SH rest family with the long grade and item; this is preferable to an invented drain polarity."),
    "rsheal": ("PARTIAL_RESCUE", "SH_REST+E_SHORT+AL_TO", "kurz am Ziel ruhen", "MEDIUM", "The rest family, short grade and target explain the card without introducing warm water."),
    "rol": ("PARTIAL_RESCUE", "OL_CONTINUE", "weiterfuehren", "MEDIUM", "The visible continuation core survives; the initial wrapper remains local and warmth is removed."),
    "lol": ("PARTIAL_RESCUE", "L_OUT+OL_CONTINUE", "von dort weiterfuehren", "MEDIUM", "Outward direction plus continuation fits the transfer record; the doubled-looking wrapper is not yet generalized."),
    "otytchol": ("PARTIAL_RESCUE", "OT_FOLLOW+Y_CURRENT+OL_CONTINUE", "naechsten Posten weiterfuehren", "MEDIUM", "Follow, current item and continuation are all visible, while the internal wrapper remains local."),
}


COMPONENT_ROWS = [
    ("AIIN_MEASURE", "aiin", "Sollmass", "solkaiin|qotedaiin", "Measures collection or the following short step."),
    ("AL_TO", "al", "zur Zielstelle", "raly|chckhal|sheckhal|rsheal|schoal", "Supplies target rather than a vessel or body-part noun."),
    ("AR_FROM", "ar", "von dort; daraus", "chary|lar|cheedar", "Supplies source or origin."),
    ("CHED_TRANSFER", "chd|ched", "umsetzen", "cheedar|shecthedchy", "Productive transfer core."),
    ("CHEEY_CLEAR_FLOW", "cheey|shey", "Klarlauf", "lcheey", "Learned clear-flow card can be selected by outward L."),
    ("CKH_THROUGH", "ckh", "durchleiten", "sheckhy|qockhey|chckhal|sheckhal", "Expands the existing through-pass family."),
    ("CTH_READY", "cth", "bereit", "shecthy|oltchy|shecthedchy|octheol|qoctholy", "Ready-state core composes with grade, item, transfer and continuation."),
    ("E_SHORT", "e", "kurz", "sheckhy|qockhey|chckhal|sheckhal|rsheal|teol|keol|qotedaiin", "Short grade in licensed process environments."),
    ("EE_LONG", "ee", "laenger", "sheey", "Long grade in the local rest family."),
    ("EEE_FULL", "eee", "vollstaendig", "cheeety", "Full grade; carrier remains locally learned."),
    ("HO_INGREDIENT", "cho|sho", "Zutat", "choy|schoal", "Ingredient/object core from the selected medium pass."),
    ("L_OUT", "l", "ab; aus", "lar|lcheey|lol", "Outward selector, now extended beyond CHED in three locally coherent cards."),
    ("OK_SET", "ok|qok", "ansetzen", "qockhey", "Activates the short through-pass."),
    ("OL_CONTINUE", "ol|chol|qol", "weiterfuehren", "qotchol|oltchy|qolchey|octheol|qoctholy|teol|keol|rol|lol|otytchol", "Continuation core explains ten former whole-card guesses."),
    ("OT_FOLLOW", "ot|qot", "danach; naechster", "qotchol|qotedaiin|otytchol", "Orders the following item, measure or continuation."),
    ("SH_REST", "sh", "ruhen", "sheey|rsheal", "Bound learned rest family, not a global letter meaning."),
    ("SOLK_COLLECT", "solk", "sammeln", "solkaiin", "Collection core selects a target measure."),
    ("Y_CURRENT", "y|chy wrapper", "dieser Arbeitsposten", "chary|raly|choy|sheckhy|qockhey|shecthy|qolchey|oltchy|shecthedchy|qoctholy|cheeety|sheey|otytchol", "Current item remains distinct from closure."),
]


SENTENCE_REVISIONS = {
    "H1-S001": "Nimm die Wurzel, bereite den Ansatz, zerkleinere daraus in das Gefaess, gib den Wasserzulauf zu, fuehre den naechsten Posten weiter, setze ihn nach Sollmass an und behalte den Rest.",
    "H1-S002": "Setze den Posten an, fuehre ihn danach weiter und halte ihn bereit.",
    "H2-S001": "Nimm den bereiten Auszugsansatz, bringe den Ansatz auf Fertigmass, fuehre den bereiten Posten weiter und stelle sein Sollmass ein.",
    "H3-S001": "Nimm das Bluetenkraut, gib die Zutat dorthin, wringe aus, lass bis zum Standmass stehen, seih nach, nimm den Klarlauf und stelle ihn kalt.",
    "H4-S004": "Stelle das Sollmass ein, setze dort an, fuehre den bereiten Ansatz weiter und nimm davon eine Portion.",
    "H5-S002": "Nimm vom Vorposten diese Zutat, setze sie an und trage sie auf.",
    "H5-S006": "Nimm den Folgeposten, fuehre ihn kurz weiter und stelle das Sollmass ein.",
    "B1-S002": "Stelle das Sollmass ein, setze den Posten dort an, gib die weiteren Portionen und den Zusatz zu, fuehre den Ansatz weiter, leite kurz zur Zielstelle durch, stelle das Sollmass ein, halte dort laenger, leite durch, setze um und schliesse.",
    "B1-S017": "Fuehre dorthin, fuehre kurz weiter, setze um und schliesse.",
    "B2-S005": "Setze diesen Posten dort an, sammle bis zum Sollmass, leite durch, stelle das Sollmass ein, fuehre bereit weiter, waerme laenger, ziehe ab und schliesse.",
    "B2-S006": "Nimm den langen Folgeposten, setze ihn dort an, leite ihn kurz durch und setze den Posten an.",
    "B2-S012": "Ziehe den Posten ab, nimm den Klarlauf, halte ihn kurz bereit, setze ihn laenger an, fuehre den Klarlauf ab, stelle das Sollmass ein, fuehre den Posten vollstaendig aus und schliesse.",
    "B2-S014": "Fuehre von dort ab.",
    "B2-S017": "Lass den Posten kurz am Ziel ruhen, schliesse die Nebenöffnung und beende den Schritt.",
    "B3-S011": "Setze den bereiten Posten um, setze ihn an, setze erneut um und nimm daraus den folgenden Posten.",
    "B3-S021": "Stelle das Sollmass ein, halte bereit, fuehre dorthin, lass dort absetzen, halte den Posten kurz bereit, fuehre ihn erneut dorthin, setze um und schliesse.",
    "B3-S026": "Setze von dort um, warte bis zum Absetzmass, setze erneut um, gib eine Portion zu, halte bereit, pruefe den Klarpunkt, sammle laenger und schliesse.",
    "B3-S029": "Fuehre weiter, halte den Posten vollstaendig, setze kurz an und schliesse.",
    "B3-S032": "Setze eine Portion um, stelle ein kurzes Folgemass und danach das Folgemass ein, fuehre die kurze Folge aus und schliesse.",
    "B4-S002": "Fuehre diesen Posten weiter, setze ihn laenger und dann kurz an und schliesse.",
    "B4-S008": "Stelle das Sollmass ein, waerme laenger, lass laenger ruhen, setze kurz an und schliesse.",
    "B4-S014": "Setze den Ansatz in einen kurzen Durchlauf, schliesse den Wasserlauf und beende den Schritt.",
    "B4-S015": "Gib eine Portion zu, nimm den Klarlauf, leite die Portion zur Zielstelle, sammle kurz, fuehre ab und schliesse.",
    "B5-S003": "Lass dort absetzen, fuehre dorthin und weiter, fuehre von dort weiter, setze dort um, stelle das Sollmass ein und setze weiter um.",
    "B6-S001": "Sammle den rohen Posten laenger, fuehre diesen Posten dorthin, stelle das Sollmass ein, lege das Tuch ein und fuehre den Posten zum Endziel.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head(reading: str) -> str:
    return reading.split(";")[0].strip()


def build() -> dict[str, object]:
    words = read_tsv(WORDS_IN)
    prior_phrases = read_tsv(PHRASES_IN)
    events = read_tsv(EVENTS_IN)
    assert (len(words), len(prior_phrases), len(events)) == (68, 116, 381)
    assert {row["page"] for row in events} <= ALLOWED_PAGES

    singletons = [row for row in words if row["word_class"] == "LOCAL_EXEMPLAR_SINGLETON"]
    assert len(singletons) == 55
    singleton_by_surface = {row["surface_family"]: row for row in singletons}
    assert set(RESCUES) <= set(singleton_by_surface)

    events_by_id = {row["event_id"]: row for row in events}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)

    dispositions: list[dict[str, str]] = []
    for word in singletons:
        event = events_by_id[word["event_ids"]]
        sequence = events_by_statement[event["statement_id"]]
        index = sequence.index(event)
        before = sequence[index - 1]["concrete_word_reading_de"] if index else "START"
        after = sequence[index + 1]["concrete_word_reading_de"] if index + 1 < len(sequence) else "END"
        if word["surface_family"] in RESCUES:
            status, composition, reading, confidence, reason = RESCUES[word["surface_family"]]
        else:
            status = "WHOLE_RETAIN"
            composition = "MEMORIZED_WHOLE_CARD"
            reading = word["resolved_reading_de"]
            confidence = "LOCAL"
            reason = "No already taught component chain predicts this card cleanly; keep one short learned entry rather than force a split."
        dispositions.append({
            "joint_tuple_id": word["joint_tuple_id"],
            "surface_family": word["surface_family"],
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "page": event["page"],
            "previous_reading_de": word["resolved_reading_de"],
            "composition_status": status,
            "selected_composition": composition,
            "recomposed_reading_de": reading,
            "preceding_card_de": before,
            "following_card_de": after,
            "confidence": confidence,
            "reason_en": reason,
        })
    disposition_by_card = {row["joint_tuple_id"]: row for row in dispositions}

    recomposed_words: list[dict[str, str]] = []
    for word in words:
        decision = disposition_by_card.get(word["joint_tuple_id"])
        row = dict(word)
        row["pre_recomposition_reading_de"] = word["resolved_reading_de"]
        row["singleton_composition_status"] = decision["composition_status"] if decision else "NOT_LOCAL_SINGLETON"
        row["singleton_selected_composition"] = decision["selected_composition"] if decision else "UNCHANGED"
        row["recomposed_reading_de"] = decision["recomposed_reading_de"] if decision else word["resolved_reading_de"]
        row["recomposition_confidence"] = decision["confidence"] if decision else "UNCHANGED"
        recomposed_words.append(row)
    word_map = {row["joint_tuple_id"]: row for row in recomposed_words}

    phrase_rows: list[dict[str, str]] = []
    for prior in prior_phrases:
        statement_events = events_by_statement[prior["statement_id"]]
        heads: list[str] = []
        tagged: list[str] = []
        changed: list[str] = []
        for event in statement_events:
            word = word_map.get(event["joint_tuple_id"])
            reading = word["recomposed_reading_de"] if word else head(event["concrete_word_reading_de"])
            close = event["step_closure_role"] == "COMMIT_CELL"
            heads.append(reading + (" [SCHLUSS]" if close else ""))
            tagged.append(f"[PROGRAM] {reading} [SCHLUSS]" if close else f"[{event['workshop_slots']}] {reading}")
            if event["joint_tuple_id"] in disposition_by_card and disposition_by_card[event["joint_tuple_id"]]["composition_status"] != "WHOLE_RETAIN":
                changed.append(event["joint_tuple_id"])
        fluent = SENTENCE_REVISIONS.get(prior["statement_id"], prior["resolved_fluent_sentence_de"])
        phrase_rows.append({
            **prior,
            "pre_recomposition_headwords_de": prior["resolved_headword_sequence_de"],
            "recomposed_headword_sequence_de": " → ".join(heads),
            "recomposed_slot_sequence_de": " | ".join(tagged),
            "recomposed_singleton_cards": "|".join(dict.fromkeys(changed)) if changed else "NONE",
            "recomposed_singleton_count": str(len(dict.fromkeys(changed))),
            "pre_recomposition_fluent_de": prior["resolved_fluent_sentence_de"],
            "recomposed_fluent_sentence_de": fluent,
            "recomposition_changed_statement": "YES" if changed else "NO",
        })

    component_rows = [{
        "component_id": cid,
        "visible_realizations": visible,
        "compact_value_de": value,
        "rescued_surfaces": surfaces,
        "use_in_this_pass_en": note,
    } for cid, visible, value, surfaces, note in COMPONENT_ROWS]

    lines = [
        "# Elf Records nach Zerlegung lokaler Einzelkarten",
        "",
        "Diese Ausgabe liest die sichtbare Kartenfolge mit dem bereits gelernten Werkstattbaukasten. Kontext bleibt kreativ; die neue Leistung ist die kuerzere Kartenkomposition.",
        "",
    ]
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrase_rows:
        by_record[row["record_unit_id"]].append(row)
    for record in RECORD_ORDER:
        selected = by_record[record]
        lines.extend([f"## {record} — {selected[0]['page']}", ""])
        for row in selected:
            marker = " · NEU ZERLEGT" if row["recomposition_changed_statement"] == "YES" else ""
            lines.append(f"- **{row['statement_id']}{marker}**")
            lines.append(f"  - Karten: {row['recomposed_headword_sequence_de']}")
            lines.append(f"  - Lesung: {row['recomposed_fluent_sentence_de']}")
        lines.append("")

    write_tsv(DISPOSITION_OUT, dispositions)
    write_tsv(COMPONENTS_OUT, component_rows)
    write_tsv(WORDS_OUT, recomposed_words)
    write_tsv(PHRASES_OUT, phrase_rows)
    RECORDS_OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    counts = Counter(row["composition_status"] for row in dispositions)
    changed_statements = sum(row["recomposition_changed_statement"] == "YES" for row in phrase_rows)
    summary = {
        "status": "PASS",
        "local_singletons": len(dispositions),
        "productive_rescues": counts["PRODUCTIVE_RESCUE"],
        "partial_rescues": counts["PARTIAL_RESCUE"],
        "whole_cards_retained": counts["WHOLE_RETAIN"],
        "recomposed_singletons": counts["PRODUCTIVE_RESCUE"] + counts["PARTIAL_RESCUE"],
        "changed_statements": changed_statements,
        "word_deck_rows": len(recomposed_words),
        "phrase_rows": len(phrase_rows),
        "source_event_rows": len(events),
        "records": len(by_record),
        "files": {},
    }
    for path in [DISPOSITION_OUT, COMPONENTS_OUT, WORDS_OUT, PHRASES_OUT, RECORDS_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
