#!/usr/bin/env python3
"""Render the same card plans through four bounded workshop scribe profiles."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
ENCODER = ROOT / "experiments/yolo/sidequest_semantic_scribe_forward_encoder"
MACRO = ROOT / "experiments/yolo/sidequest_semantic_workshop_macro_grammar"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: str(row.get(key, "")) for key in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


PROFILES = [
    {
        "scribe_id": "S1_BARE_MASTER",
        "workshop_background_de": "älterer Meisterschreiber; bevorzugt die erste unmarkierte Familienform und schreibt die Kartenfolge auf einer Übungszeile",
        "allow_s_entry": False, "allow_q_postcommit": False, "line_width": 0, "fallback": "BARE_FIRST",
    },
    {
        "scribe_id": "S2_Q_CELL_SCRIBE",
        "workshop_background_de": "Zellenschreiber; setzt nach einer geschlossenen Karte wenn möglich die registrierte q-Form des nächsten Postens",
        "allow_s_entry": False, "allow_q_postcommit": True, "line_width": 0, "fallback": "BARE_FIRST",
    },
    {
        "scribe_id": "S3_S_LINE_SCRIBE",
        "workshop_background_de": "Zeilenschreiber; bricht die Übung alle drei Karten um und setzt am neuen Zeilenanfang wenn möglich die registrierte s-Form",
        "allow_s_entry": True, "allow_q_postcommit": False, "line_width": 3, "fallback": "BARE_FIRST",
    },
    {
        "scribe_id": "S4_MIXED_COMPACT",
        "workshop_background_de": "kompakter Werkstattschreiber; vier Karten je Zeile, s am Zeilenanfang und q nach lokalem Abschluss, sofern die Familie beides erlaubt",
        "allow_s_entry": True, "allow_q_postcommit": True, "line_width": 4, "fallback": "SHORTEST_REGISTERED",
    },
]


def is_close(card: dict[str, str]) -> bool:
    parse = card["closed_parse"].upper()
    reading = card["closed_reading_de"].lower()
    return "CLOSE" in parse or "TERMINAL" in parse or "schluss" in reading or reading.endswith("ende")


def choose_surface(card: dict[str, str], profile: dict[str, object], line_start: bool, previous_close: bool) -> tuple[str, str]:
    variants = card["surface_family"].split("|")
    s_forms = [v for v in variants if v.startswith("s")]
    q_forms = [v for v in variants if v.startswith("q")]
    bare = [v for v in variants if not v.startswith(("q", "s"))]
    if line_start and profile["allow_s_entry"] and s_forms:
        return s_forms[0], "REGISTERED_S_LINE_ENTRY"
    if previous_close and profile["allow_q_postcommit"] and q_forms:
        return q_forms[0], "REGISTERED_Q_AFTER_COMMIT"
    if profile["fallback"] == "SHORTEST_REGISTERED":
        return min(variants, key=lambda value: (len(value), variants.index(value))), "SHORTEST_REGISTERED_FALLBACK"
    if bare:
        return bare[0], "BARE_REGISTERED_FALLBACK"
    return variants[0], "FIXED_OR_MARKED_ONLY_FALLBACK"


def render_plan(
    item_kind: str,
    item_id: str,
    tuple_ids: list[str],
    original_tokens: list[str],
    profile: dict[str, object],
    card_by_tuple: dict[str, dict[str, str]],
    initial_previous_close: bool = False,
) -> tuple[list[str], str, list[dict[str, object]]]:
    chosen: list[str] = []
    line_parts: list[list[str]] = [[]]
    trace: list[dict[str, object]] = []
    width = int(profile["line_width"])
    previous_close = initial_previous_close
    for index, tuple_id in enumerate(tuple_ids, start=1):
        if width and len(line_parts[-1]) >= width:
            line_parts.append([])
        line_start = len(line_parts[-1]) == 0
        card = card_by_tuple[tuple_id]
        surface, reason = choose_surface(card, profile, line_start, previous_close)
        chosen.append(surface)
        line_parts[-1].append(surface)
        trace.append({
            "item_kind": item_kind, "item_id": item_id, "scribe_id": profile["scribe_id"],
            "token_ordinal": index, "line_number": len(line_parts), "line_start": "YES" if line_start else "NO",
            "previous_card_closed": "YES" if previous_close else "NO", "joint_tuple_id": tuple_id,
            "semantic_reading_de": card["closed_reading_de"], "registered_surface_family": card["surface_family"],
            "original_or_exercise_surface": original_tokens[index - 1], "chosen_surface": surface,
            "choice_reason": reason, "meaning_change": "NONE",
        })
        previous_close = is_close(card)
    return chosen, " / ".join(" ".join(line) for line in line_parts), trace


def main() -> None:
    dictionary = read_tsv(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")
    exercises = read_tsv(ENCODER / "GENERATED_DICTATION_EXERCISES.tsv")
    statement_macros = read_tsv(MACRO / "STATEMENT_MACRO_PARSES.tsv")
    card_by_tuple = {row["joint_tuple_id"]: row for row in dictionary}
    tuple_by_surface = {row["surface_display"]: row["joint_tuple_id"] for row in events}
    macro_by_statement = {row["statement_id"]: row for row in statement_macros}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    previous_event_by_id: dict[str, dict[str, str] | None] = {}
    previous_by_record_for_statement: dict[str, dict[str, str]] = {}
    for event in events:
        previous_event_by_id[event["event_id"]] = previous_by_record_for_statement.get(event["record_unit_id"])
        previous_by_record_for_statement[event["record_unit_id"]] = event

    profile_rows = [{
        "scribe_id": p["scribe_id"], "five_line_background_de": p["workshop_background_de"],
        "s_line_entry": "YES" if p["allow_s_entry"] else "NO",
        "q_after_commit": "YES" if p["allow_q_postcommit"] else "NO",
        "exercise_line_width_cards": p["line_width"] or "NO_FORCED_BREAK",
        "fallback_rule": p["fallback"], "shared_dictionary": "SAME_173_EXACT_CARDS",
        "semantic_policy": "MEANING_AND_TUPLE_SEQUENCE_INVARIANT",
    } for p in PROFILES]
    write_tsv(OUT / "FOUR_SCRIBE_PROFILES.tsv", profile_rows,
              ["scribe_id", "five_line_background_de", "s_line_entry", "q_after_commit", "exercise_line_width_cards",
               "fallback_rule", "shared_dictionary", "semantic_policy"])

    # Position census on the observed prose events.
    first_in_locus: set[str] = set()
    seen_loci: set[tuple[str, str]] = set()
    previous_by_record: dict[str, dict[str, str]] = {}
    position_by_event: dict[str, tuple[bool, bool]] = {}
    for event in events:
        key = (event["record_unit_id"], event["locus"])
        first = key not in seen_loci
        if first:
            seen_loci.add(key); first_in_locus.add(event["event_id"])
        previous = previous_by_record.get(event["record_unit_id"])
        postcommit = bool(previous and previous["step_closure_role"] == "COMMIT_CELL")
        position_by_event[event["event_id"]] = (first, postcommit)
        previous_by_record[event["record_unit_id"]] = event

    events_by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_tuple[event["joint_tuple_id"]].append(event)
    census_rows: list[dict[str, object]] = []
    for card in dictionary:
        variants = card["surface_family"].split("|")
        if len(variants) == 1:
            continue
        card_events = events_by_tuple[card["joint_tuple_id"]]
        variant_counts = Counter(e["surface_display"] for e in card_events)
        entry_counts = Counter(e["surface_display"] for e in card_events if position_by_event[e["event_id"]][0])
        post_counts = Counter(e["surface_display"] for e in card_events if position_by_event[e["event_id"]][1])
        census_rows.append({
            "joint_tuple_id": card["joint_tuple_id"], "semantic_reading_de": card["closed_reading_de"],
            "registered_surface_family": card["surface_family"], "variant_count": len(variants),
            "occurrences": card["occurrences"],
            "variant_event_counts": ";".join(f"{v}:{variant_counts[v]}" for v in variants),
            "line_entry_counts": ";".join(f"{v}:{entry_counts[v]}" for v in variants),
            "postcommit_counts": ";".join(f"{v}:{post_counts[v]}" for v in variants),
            "bare_forms": ";".join(v for v in variants if not v.startswith(("q", "s"))) or "NONE",
            "q_forms": ";".join(v for v in variants if v.startswith("q")) or "NONE",
            "s_forms": ";".join(v for v in variants if v.startswith("s")) or "NONE",
            "tuple_meaning_status": "INVARIANT_ACROSS_REGISTERED_SURFACES",
        })
    census_fields = ["joint_tuple_id", "semantic_reading_de", "registered_surface_family", "variant_count", "occurrences",
                     "variant_event_counts", "line_entry_counts", "postcommit_counts", "bare_forms", "q_forms", "s_forms",
                     "tuple_meaning_status"]
    write_tsv(OUT / "MULTI_SURFACE_FAMILY_CENSUS.tsv", census_rows, census_fields)

    statement_rows: list[dict[str, object]] = []
    token_trace: list[dict[str, object]] = []
    for phrase in phrases:
        statement_id = phrase["statement_id"]
        statement_events = events_by_statement[statement_id]
        tuple_ids = [e["joint_tuple_id"] for e in statement_events]
        original_tokens = [e["surface_display"] for e in statement_events]
        semantic_readback = " -> ".join(card_by_tuple[t]["closed_reading_de"] for t in tuple_ids)
        previous_event = previous_event_by_id[statement_events[0]["event_id"]]
        initial_previous_close = bool(previous_event and previous_event["step_closure_role"] == "COMMIT_CELL")
        for profile in PROFILES:
            chosen, rendered, trace = render_plan(
                "MANUSCRIPT_STATEMENT_COPY", statement_id, tuple_ids, original_tokens, profile, card_by_tuple,
                initial_previous_close=initial_previous_close,
            )
            token_trace.extend(trace)
            statement_rows.append({
                "statement_id": statement_id, "record_unit_id": phrase["record_unit_id"], "page": phrase["page"],
                "dossier_id": macro_by_statement[statement_id]["dossier_id"], "master_command_de": phrase["fluent_workshop_sentence_de"],
                "macro_sequence": macro_by_statement[statement_id]["macro_sequence"], "scribe_id": profile["scribe_id"],
                "tuple_sequence": " ".join(tuple_ids), "semantic_readback_de": semantic_readback,
                "original_surface_sequence": phrase["surface_sequence"], "counterfactual_surface_sequence": " ".join(chosen),
                "line_broken_copy": rendered, "changed_token_count": sum(a != b for a, b in zip(original_tokens, chosen)),
                "starts_after_committed_cell": "YES" if initial_previous_close else "NO",
                "tuple_sequence_changed": "NO", "meaning_changed": "NO",
                "copy_status": "COUNTERFACTUAL_WORKSHOP_COPY__NOT_MANUSCRIPT_TRANSCRIPTION",
            })
    statement_fields = ["statement_id", "record_unit_id", "page", "dossier_id", "master_command_de", "macro_sequence",
                        "scribe_id", "tuple_sequence", "semantic_readback_de", "original_surface_sequence",
                        "counterfactual_surface_sequence", "line_broken_copy", "changed_token_count", "tuple_sequence_changed",
                        "starts_after_committed_cell", "meaning_changed", "copy_status"]
    write_tsv(OUT / "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv", statement_rows, statement_fields)

    exercise_rows: list[dict[str, object]] = []
    for exercise in exercises:
        original_tokens = exercise["generated_surface_sequence"].split()
        tuple_ids = [tuple_by_surface[token] for token in original_tokens]
        semantic_readback = " -> ".join(card_by_tuple[t]["closed_reading_de"] for t in tuple_ids)
        for profile in PROFILES:
            chosen, rendered, trace = render_plan("GENERATED_DICTATION_COPY", exercise["exercise_id"], tuple_ids, original_tokens, profile, card_by_tuple)
            token_trace.extend(trace)
            exercise_rows.append({
                "exercise_id": exercise["exercise_id"], "dossier_id": exercise["dossier_id"],
                "master_dictation_de": exercise["master_dictation_de"], "scribe_id": profile["scribe_id"],
                "tuple_sequence": " ".join(tuple_ids), "semantic_readback_de": semantic_readback,
                "base_generated_sequence": exercise["generated_surface_sequence"], "scribe_surface_sequence": " ".join(chosen),
                "line_broken_copy": rendered, "changed_token_count": sum(a != b for a, b in zip(original_tokens, chosen)),
                "tuple_sequence_changed": "NO", "meaning_changed": "NO", "all_surfaces_registered": "YES",
                "copy_status": "APPRENTICE_EXERCISE__NOT_MANUSCRIPT_TEXT",
            })
    exercise_fields = ["exercise_id", "dossier_id", "master_dictation_de", "scribe_id", "tuple_sequence",
                       "semantic_readback_de", "base_generated_sequence", "scribe_surface_sequence", "line_broken_copy",
                       "changed_token_count", "tuple_sequence_changed", "meaning_changed", "all_surfaces_registered", "copy_status"]
    write_tsv(OUT / "FOUR_HAND_16_EXERCISE_RENDERINGS.tsv", exercise_rows, exercise_fields)

    trace_fields = ["item_kind", "item_id", "scribe_id", "token_ordinal", "line_number", "line_start",
                    "previous_card_closed", "joint_tuple_id", "semantic_reading_de", "registered_surface_family",
                    "original_or_exercise_surface", "chosen_surface", "choice_reason", "meaning_change"]
    write_tsv(OUT / "RENDERER_TOKEN_TRACE.tsv", token_trace, trace_fields)

    copybook = ["# Vier Schreiber, ein gemeinsames Wörterbuch", "",
                "Jede Übung besitzt genau eine Bedeutungs- und Tuplefolge. Die vier Profile ändern nur Zeilenumbruch und eine bereits registrierte Oberflächenform. Sie sind Werkstattrollen, keine Identifikation realer Voynich-Hände.", ""]
    for exercise in exercises:
        copybook += [f"## {exercise['exercise_id']}: {exercise['master_dictation_de']}", "",
                     f"Tuple-/Sinnplan: {exercise['semantic_card_trace_de']}", ""]
        for row in exercise_rows:
            if row["exercise_id"] == exercise["exercise_id"]:
                copybook.append(f"- **{row['scribe_id']}**: `{row['line_broken_copy']}`")
        copybook.append("")
    copybook += ["## Vier vorhandene Aussagen als Kopierprobe", ""]
    samples = ["H1-S001", "H3-S001", "B2-S016", "B4-S012"]
    for statement_id in samples:
        phrase = next(row for row in phrases if row["statement_id"] == statement_id)
        copybook += [f"### {statement_id}: {phrase['fluent_workshop_sentence_de']}", ""]
        for row in statement_rows:
            if row["statement_id"] == statement_id:
                copybook.append(f"- **{row['scribe_id']}**: `{row['line_broken_copy']}`")
        copybook.append("")
    (OUT / "FOUR_SCRIBE_COPYBOOK.md").write_text("\n".join(copybook).rstrip() + "\n", encoding="utf-8")

    statement_surface_sets: dict[str, set[str]] = defaultdict(set)
    for row in statement_rows:
        statement_surface_sets[row["statement_id"]].add(row["counterfactual_surface_sequence"])
    exercise_surface_sets: dict[str, set[str]] = defaultdict(set)
    for row in exercise_rows:
        exercise_surface_sets[row["exercise_id"]].add(row["scribe_surface_sequence"])
    statement_changed = sum(len(values) > 1 for values in statement_surface_sets.values())
    exercise_changed = sum(len(values) > 1 for values in exercise_surface_sets.values())
    profile_change_counts = Counter()
    for row in statement_rows:
        profile_change_counts[row["scribe_id"]] += int(row["changed_token_count"])
    trace_reasons = Counter(row["choice_reason"] for row in token_trace)

    report = f"""# Vier-Schreiber-Kopierwerkstatt

## Ergebnis

Dieselbe Bedeutungs- und Exact-Tuplefolge kann durch vier einfache Schreibprofile laufen, ohne dass ein Schreiber das Wörterbuch ändert oder eine neue Kartenform erfindet. Die Profile sind didaktische Werkstattrollen: bare Meisterform, q nach lokaler Schließung, s am neuen Zeilenanfang und ein kompaktes Mischprofil.

Das Prosa-Inventar enthält {len(census_rows)} exakte Kartenfamilien mit mehr als einer registrierten Oberfläche. Über alle 116 Aussagen entstehen 464 Gegenkopien. {statement_changed} Aussagen erhalten unter den vier Profilen mindestens zwei verschiedene sichtbare Folgen; die übrigen besitzen an den betreffenden Stellen nur feste oder für diese Regeln nicht alternative Formen. Alle Tuplefolgen und Bedeutungsrücklesungen bleiben gleich.

Die sechzehn neuen Diktierübungen ergeben 64 Kopien; {exercise_changed} Übungen werden sichtbar in mindestens zwei Varianten gesetzt. Kein erzeugtes Token liegt außerhalb seiner beobachteten Exact-Tuple-Familie.

## Die vier Rollen

1. **S1 Bare Master:** bevorzugt die erste unmarkierte registrierte Form.
2. **S2 Q Cell Scribe:** nimmt nach einer geschlossenen Karte die q-Form des nächsten Postens, falls diese bereits zur Familie gehört.
3. **S3 S Line Scribe:** bricht nach drei Karten um und nimmt am neuen Zeilenanfang die registrierte s-Form.
4. **S4 Mixed Compact:** schreibt vier Karten je Zeile, kombiniert s-Zeilenanfang und q-nach-Schluss und benutzt sonst die kürzeste registrierte Form.

## Was der Lehrling tatsächlich lernen muss

Die Bedeutungsseite endet vor dem Renderer: Meisterbefehl -> Makros -> Exact Tuple. Erst dann folgt: lokale Position -> registrierte Oberfläche. Dadurch können mehrere Schreiber dieselbe Werkstattanweisung unterschiedlich aussehen lassen, ohne Synonyme, andere Lautungen oder andere Fachwörter anzunehmen.

Im vollständigen Tokenprotokoll verteilen sich die Entscheidungen auf {dict(trace_reasons)}. Gegenüber den jeweils vorliegenden Ausgangsoberflächen ändern die Profile zusammen {dict(profile_change_counts)} Tokens in den 464 Aussagekopien.

Die vier Profile sind kreative Ausführungsmodelle und keine Zuweisung an reale Handschriftenhände. `FOUR_HAND_116_STATEMENT_RENDERINGS.tsv` enthält alle Aussagekopien, `FOUR_HAND_16_EXERCISE_RENDERINGS.tsv` die neuen Diktierübungen, und `RENDERER_TOKEN_TRACE.tsv` begründet jede einzelne Formwahl.
"""
    (OUT / "FOUR_SCRIBE_COPYSHOP_REPORT.md").write_text(report, encoding="utf-8")

    outputs = ["FOUR_SCRIBE_PROFILES.tsv", "MULTI_SURFACE_FAMILY_CENSUS.tsv",
               "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv", "FOUR_HAND_16_EXERCISE_RENDERINGS.tsv",
               "RENDERER_TOKEN_TRACE.tsv", "FOUR_SCRIBE_COPYBOOK.md", "FOUR_SCRIBE_COPYSHOP_REPORT.md"]
    summary = {
        "status": "PASS", "scribe_profiles": 4, "multi_surface_families": len(census_rows),
        "statements": 116, "statement_renderings": len(statement_rows), "statements_with_multiple_renderings": statement_changed,
        "exercises": 16, "exercise_renderings": len(exercise_rows), "exercises_with_multiple_renderings": exercise_changed,
        "renderer_token_rows": len(token_trace), "choice_reasons": dict(trace_reasons),
        "output_sha256": {name: sha(OUT / name) for name in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
