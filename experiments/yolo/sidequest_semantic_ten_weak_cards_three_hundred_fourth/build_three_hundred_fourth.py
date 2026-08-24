#!/usr/bin/env python3
"""Replace the ten last named worksteps with narrow context-driven verbs."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_imperative_edition_three_hundred_third/THREE_HUNDRED_THIRD_173_IMPERATIVE_CARD_LEXICON.tsv"
EVENTS_303 = ROOT / "experiments/yolo/sidequest_semantic_imperative_edition_three_hundred_third/THREE_HUNDRED_THIRD_381_IMPERATIVE_EVENTS.tsv"
RAW_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
PUNCT = ROOT / "experiments/yolo/sidequest_semantic_punctuated_edition_three_hundred_second/THREE_HUNDRED_SECOND_116_PUNCTUATED_STATEMENTS.tsv"
SCOPE = ROOT / "experiments/yolo/sidequest_semantic_endpoint_scope_three_hundred_first/THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv"


OVERRIDES = {
    "MC024": ("Setze den verbleibenden Posten erneut ein", "setze erneut ein", "nur 'weiter einsetzen'", "folgt auf Weiterabzug und Abführung, vor Absetzen"),
    "MC063": ("Führe ihn länger im Folgegang weiter", "führe länger weiter", "beliebige lange Folge", "beide Belege stehen zwischen Voroperation und neuer Ziel-/Zuführungsphase"),
    "MC089": ("Gieße ihn von der Quellseite zu", "gieße von der Quelle zu", "Quellausguss als Nomen", "steht nach Zieladresse und vor Absetzen/Nachtransfer"),
    "MC102": ("Halte den zugeführten Posten kurz am Ziel", "halte kurz am Ziel", "beliebiger Kurzhalt", "steht genau zwischen Zuführung und Zielschluss"),
    "MC112": ("Setze den nächsten Durchgang an", "setze nächsten Durchgang an", "Fortsetzung vorbereiten", "folgt auf Durchleiten plus Maß und eröffnet Wärme-Abzug-Folge"),
    "MC135": ("Führe ihn kurz zum Folgeschritt weiter", "führe kurz zum Folgeschritt", "beliebige Kurzfolge", "beide Belege verbinden eine Ziel-/Maßphase mit dem nächsten Transfer oder Abzug"),
    "MC138": ("Lass frische Spülflüssigkeit ein", "lass frische Spülflüssigkeit ein", "Frischwasser zugeben", "beginnt nach sichtbarem Stationswechsel eine neue Inline-Spülphase"),
    "MC144": ("Lass ihn bis zum Sollstand absetzen", "lass bis Sollstand absetzen", "Sollabsetzung als Nomen", "steht zwischen Quelltransfer und weiterem Überführen/Zugeben/Bereit"),
    "MC146": ("Stelle ihn am Zielgefäß bereit", "stelle am Zielgefäß bereit", "Zielbereitung", "folgt auf Bereitkarte und geht langer Sammlung voraus"),
    "MC162": ("Nimm den nächsten Einsatzposten", "nimm nächsten Einsatzposten", "Weiterposten", "steht nach langem Einwirken und vor einer neuen langen/kurzen Einwirkungsfolge"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lexicon = read(LEXICON)
    raw = read(RAW_EVENTS)
    prior_events = {r["event_id"]: r for r in read(EVENTS_303)}
    punct = {r["statement_id"]: r for r in read(PUNCT)}
    scope = {r["event_id"]: r for r in read(SCOPE)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[str]] = defaultdict(list)
    positions = {r["event_id"]: i for i, r in enumerate(raw)}
    for event in raw:
        by_statement[event["statement_id"]].append(event)
        if event["statement_id"] not in by_record[event["record_unit_id"]]:
            by_record[event["record_unit_id"]].append(event["statement_id"])

    clause_by_card = {r["master_card_id"]: r["imperative_clause_de"] for r in lexicon}
    for card_id, (clause, *_rest) in OVERRIDES.items():
        clause_by_card[card_id] = clause

    decisions = []
    for card_id, (clause, atomic, rival, reason) in OVERRIDES.items():
        occurrences = [r for r in raw if r["master_card_id"] == card_id]
        contexts = []
        for event in occurrences:
            selected = by_statement[event["statement_id"]]
            index = selected.index(event)
            before = selected[index - 1]["visible_surface"] if index else "<START>"
            after = selected[index + 1]["visible_surface"] if index + 1 < len(selected) else "<END>"
            contexts.append(f"{event['event_id']}:{event['record_unit_id']}/{event['statement_id']}:{before}>{event['visible_surface']}>{after}")
        source = next(r for r in lexicon if r["master_card_id"] == card_id)
        decisions.append({
            "master_card_id": card_id,
            "master_form": source["master_form"],
            "source_short_value_de": source["source_short_value_de"],
            "old_imperative_de": source["imperative_clause_de"],
            "selected_atomic_action_de": atomic,
            "new_imperative_de": clause,
            "strongest_rival_de": rival,
            "context_reason_de": reason,
            "occurrence_count": len(occurrences),
            "occurrence_contexts": " | ".join(contexts),
        })
    decision_path = HERE / "THREE_HUNDRED_FOURTH_TEN_CARD_DECISIONS.tsv"
    write(decision_path, decisions)

    revised_lexicon = []
    for row in lexicon:
        out = dict(row)
        if row["master_card_id"] in OVERRIDES:
            out["imperative_clause_de"] = clause_by_card[row["master_card_id"]]
            out["conversion_method"] = "CONTEXT_NARROWED_VERB"
        revised_lexicon.append(out)
    lexicon_path = HERE / "THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv"
    write(lexicon_path, revised_lexicon)

    revised_events = []
    for event in raw:
        prior = prior_events[event["event_id"]]
        clause = clause_by_card[event["master_card_id"]]
        if event["event_id"] == "E180":
            clause += " [am Zeilenrand einmal lesen]"
        elif event["event_id"] == "E181":
            clause = "[sichtbare Wiederholung; nicht nochmals ausführen]"
        out = dict(prior)
        out["imperative_clause_de"] = clause
        revised_events.append(out)
    event_path = HERE / "THREE_HUNDRED_FOURTH_381_REVISED_IMPERATIVE_EVENTS.tsv"
    write(event_path, revised_events)

    statement_rows = []
    for statement_id, selected in by_statement.items():
        p = punct[statement_id]
        clauses = []
        previous_field = None
        read_tokens = []
        for event in selected:
            if event["event_id"] == "E181":
                continue
            if previous_field is not None and previous_field != event["field_id"]:
                clauses.append("Öffne das nächste Feld")
            if event["event_id"] in {"E203", "E264", "E291", "E356"}:
                clauses.append("Setze den sichtbaren Besitzer neu")
            clause = clause_by_card[event["master_card_id"]]
            if event["event_id"] == "E180":
                clause += " und lies die Randwiederholung nur einmal"
            clauses.append(clause)
            read_tokens.append(scope[event["event_id"]]["source_token_id"])
            previous_field = event["field_id"]
        ending = ";" if p["punctuation_class"] == "COMMIT_SEMICOLON" else (" …" if p["punctuation_class"] == "OPEN_RECORD_RELEASE" else " ↪")
        continuous = clauses[0] + "".join("; dann " + c[0].lower() + c[1:] for c in clauses[1:]) + ending
        statement_rows.append({
            "statement_id": statement_id, "record_unit_id": p["record_unit_id"], "page": p["page"],
            "owner_slot": p["owner_slot"], "field_path": p["field_path"],
            "visible_event_count": len(selected), "read_source_token_count": len(set(read_tokens)),
            "surface_punctuated": p["surface_punctuated"], "fluent_imperative_de": continuous,
            "punctuation_class": p["punctuation_class"],
        })
    statement_path = HERE / "THREE_HUNDRED_FOURTH_116_REVISED_STATEMENTS.tsv"
    write(statement_path, statement_rows)

    affected = {r["statement_id"] for r in raw if r["master_card_id"] in OVERRIDES}
    lines = ["# Zehn schwache Karten: konkrete Verbrunde", "", "Die zehn Restkarten werden nicht mehr als bloß benannte Arbeitsschritte vorgelesen. Alle Vorkommen bleiben unten im vollständigen Aussagekontext.", ""]
    by_id = {r["statement_id"]: r for r in statement_rows}
    for decision in decisions:
        lines += [f"## {decision['master_form']} — {decision['selected_atomic_action_de']}", "", f"**Arbeitsklausel:** {decision['new_imperative_de']}.", "", f"**Warum:** {decision['context_reason_de']}.", ""]
    lines += ["# Vollständige betroffene Aussagen", ""]
    for statement_id in sorted(affected, key=lambda x: (x.split("-")[0], int(x.split("S")[1]))):
        row = by_id[statement_id]
        lines += [f"**{statement_id}:** {row['fluent_imperative_de']}", ""]
    reading_path = HERE / "THREE_HUNDRED_FOURTH_TEN_CARD_CONTEXT_READINGS.md"
    reading_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_FOURTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 304: die zehn letzten generischen Schritte bekommen Verben\n\n"
        "Die zehn Karten aus der Restklasse NAMED_WORKSTEP_IMPERATIVE sind anhand sämtlicher zwölf Vorkommen konkretisiert. Die stärksten neuen Kurzwerte sind: nächsten Durchgang ansetzen, länger im Folgegang weiterführen, frische Spülflüssigkeit einlassen, kurz am Ziel halten, kurz zum Folgeschritt weiterführen, bis Sollstand absetzen, am Zielgefäß bereitstellen, nächsten Einsatzposten nehmen, verbleibenden Posten erneut einsetzen und von der Quellseite zugießen.\n\n"
        "Damit enthält das 173-Karten-Imperativlexikon keine generische benannte Restoperation mehr. Der nächste Pass kann nun wiederkehrende Mehrkartenketten als gelernte Rezeptformeln erkennen, ohne die Einzelwörter umzudeuten.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "target_cards": len(OVERRIDES),
        "target_occurrences": sum(int(r["occurrence_count"]) for r in decisions),
        "cards": len(revised_lexicon), "events": len(revised_events), "statements": len(statement_rows),
        "remaining_named_worksteps": sum(r["conversion_method"] == "NAMED_WORKSTEP_IMPERATIVE" for r in revised_lexicon),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [LEXICON, EVENTS_303, RAW_EVENTS, PUNCT, SCOPE]},
        "output_hashes": {p.name: sha(p) for p in [decision_path, lexicon_path, event_path, statement_path, reading_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
