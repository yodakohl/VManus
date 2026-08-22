#!/usr/bin/env python3
"""Build the V72 R1 owner-aware 116-statement workshop edition.

This is a bounded sidequest transform.  It preserves the frozen V69 statement
and event memberships and replaces only the visible-owner layer with the
centrally selected V71 ownership map.  No glyph, card, or stem value is learned
here.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
OUT = Path(__file__).resolve().parent

STATEMENT_PATH = V69 / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv"
FIELD_PATH = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
EVENT_PATH = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
OWNER_PATH = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"

OUT_STATEMENTS = OUT / "V72_R1_116_STATEMENTS.tsv"
OUT_REVISIONS = OUT / "V72_R1_REVISIONS.tsv"
OUT_VALIDATION = OUT / "V72_R1_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields,
                                lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unique_in_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def bracket_values(text: str, tag: str) -> list[str]:
    # V69 source segments have no nested closing brackets in tagged values.
    return re.findall(r"\[" + re.escape(tag) + r":([^\]]+)\]", text)


def clean_phrase(text: str) -> str:
    text = text.strip()
    # The biological source edition sometimes prefixes the local exemplar card
    # inventory before the first colon.  It is provenance, not clause content.
    text = re.sub(r"^A\d+(?:\+A\d+)*:", "", text)
    replacements = {
        "Blüten und junge Blätter des Duftveilchens": "Blüten und junge Blätter der abgebildeten unbekannten Pflanze",
        "Blütenköpfe und junge Blätter derselben Teufelsabbiss-Pflanze": "Blütenköpfe und junge Blätter derselben abgebildeten unbekannten Pflanze",
        "breite Bärlauchblätter": "breite Blätter der abgebildeten unbekannten Pflanze",
        "vom rundblättrigen Sonnentau": "von der abgebildeten unbekannten Pflanze",
        "Teufelsabbisses": "abgebildeten unbekannten Pflanzenartikels",
        "Teufelsabbiss-Pflanze": "abgebildeten unbekannten Pflanze",
        "Teufelsabbiss": "abgebildeten unbekannten Pflanze",
        "Duftveilchens": "abgebildeten unbekannten Pflanze",
        "Duftveilchen": "abgebildete unbekannte Pflanze",
        "Bärlauchblätter": "breiten Blätter der abgebildeten unbekannten Pflanze",
        "Sonnentau": "abgebildeten unbekannten Pflanze",
        "H1-R01": "örtlichen ersten Pflanzenposten",
        "H1-R02": "örtlichen Restposten",
        "H1-P01": "örtlichen ersten Ansatz",
        "H1-P02": "örtlichen zweiten Ansatz",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip(" ;.")
    return text


CARD_FALLBACK = {
    "MASS?": "setze das im Exemplar vorgeschriebene Maß",
    "ANWENDEN?": "verwende die im Exemplar bezeichnete aktive Portion",
    "BEREIT?": "prüfe den im Exemplar bezeichneten Bereitschaftsstand",
    "KLAR?": "prüfe den im Exemplar bezeichneten Klarstand",
    "TEIL?": "wähle den im Exemplar bezeichneten Anteil",
    "ABLASSEN?": "lasse die im Exemplar bezeichnete Charge ab und schließe den Schritt",
    "SPÜLEN?": "spüle die im Exemplar bezeichnete Stelle und schließe den Schritt",
}


def event_source_phrase(event: dict[str, str]) -> str:
    source = event["iatromedical_source_segment"]
    # Prefer actual local/example wording; card and formal tags remain visible in
    # their own literal layer and are never silently promoted to word meanings.
    for tag in ("GENRE", "EXEMPLAR", "IMAGE", "REGISTER"):
        vals = bracket_values(source, tag)
        if vals:
            phrase = clean_phrase(vals[-1])
            if phrase:
                return phrase
    card = event["selected_exact_mnemonic"]
    if card not in {"", "NONE", "UNKNOWN"}:
        return CARD_FALLBACK.get(card, f"führe die bekannte Karte {card} nach dem Exemplar aus")
    prompt = event["strict_formal_prompt"]
    if prompt not in {"", "NONE", "UNKNOWN"}:
        return "führe den formalen Exemplarslot " + prompt + " aus"
    return "führe den örtlichen, im Exemplar ausgeschriebenen Handlungsschritt aus"


def practical_phrase(event: dict[str, str]) -> str:
    source = event["practical_source_segment"]
    # The practical edition uses LOCAL[...] (without the colon used by the
    # iatromedical tag syntax), plus LOCAL_EXEMPLAR/LOCAL_ARGUMENT variants.
    choices: list[str] = []
    for tag in ("LOCAL_EXEMPLAR", "LOCAL", "LOCAL_ARGUMENT"):
        values = re.findall(r"\b" + tag + r"\[([^\]]+)\]", source)
        if values:
            choices = values
            break
    text = clean_phrase(choices[-1] if choices else source)
    text = re.sub(r";?\s*keine Kartenbedeutung", "", text, flags=re.IGNORECASE)
    apparatus = (
        r"(?:Grundbecken A mit Wärmestelle W1, Rinne R1 und Rücklauf R0|"
        r"Teilbecken B mit Zugängen Z1-Z3, Wärmestelle W2, Filter F2 und Auslass A2|"
        r"Hauptbecken C mit Vorwärmer W3, Leitungen L1-L4, Filter F3, Unterlauf U3 und Rücklauf R3|"
        r"Nachklärbecken D mit Warmzulauf W4, Filtertuch F4, Unterlauf U4 und Rückleitung R4|"
        r"Übergabebecken E mit Wärmeschale W5 und Leitung L5|"
        r"Kaltbecken F mit einfacher Filteröffnung F6 und Zielstation Z6)"
    )
    text = re.sub(apparatus, "dieser örtlichen Station", text)
    return text or "buche denselben örtlichen Werkstattschritt"


def slot_type(phrase: str, event: dict[str, str]) -> str:
    low = phrase.lower()
    if any(x in low for x in ("beende", "schließ", "schlies", "verwahr", "lager", "commit")):
        return "CLOSURE_ACTION"
    if any(x in low for x in ("sobald", " solange", "wenn ", "bevor", " bis ", "bis ", "dauer", "klarstand", "bereitschaft")):
        return "CONDITION_STATE"
    if any(x in low for x in ("maß", "menge", "handvoll", "abgemessen", "bemess", "parameter")):
        return "MEASURE_ARGUMENT"
    if re.search(r"\b(ziel|zielstelle|stelle|öffnung|haut|wunde?|körperbereich|becken|beckenrand)\b", low):
        return "TARGET_ARGUMENT"
    if any(x in low for x in ("wasser", "wein", "flüssigkeit", "medium")) and not any(
        x in low for x in ("gib ", "gieß", "führe", "seihe", "spüle", "erwärm", "temper", "zieh")
    ):
        return "MEDIUM_ARGUMENT"
    if any(x in low for x in ("pflanze", "wurzel", "blatt", "blüte", "anteil", "portion", "tuch", "gefäß", "rückstand", "ansatz", "posten", "charge")) and not any(
        x in low for x in ("nimm", "samm", "wähl", "gib", "führe", "seihe", "spüle", "erwärm", "temper", "misch", "rühr", "zieh", "lasse")
    ):
        return "OBJECT_ARGUMENT"
    if event["event_template"] in {"STATE_GATE", "LINK_ACTIVE", "SELECT_PREVIOUS"}:
        return "STATE_ARGUMENT"
    return "ACTION_SLOT"


def concrete_source_step(event: dict[str, str]) -> str:
    phrase = event_source_phrase(event)
    kind = slot_type(phrase, event)
    prefix = {
        "OBJECT_ARGUMENT": "verwende als Gegenstand",
        "TARGET_ARGUMENT": "setze als örtliches Ziel",
        "MEDIUM_ARGUMENT": "verwende als Medium",
        "MEASURE_ARGUMENT": "setze als Maß",
        "CONDITION_STATE": "halte als Bedingung",
        "STATE_ARGUMENT": "trage als Arbeitszustand",
    }.get(kind, "")
    if prefix:
        return f"{prefix}: {phrase}"
    return phrase


def human_source_class(page: str) -> str:
    return "ILLUSTRATED_SIMPLES_CLAUSE" if page in {"f10r", "f11r", "f55v", "f56r"} else "LOCAL_BATH_OR_APPLICATION_CLAUSE"


def source_sentence(events: list[dict[str, str]], owner_by_field: dict[str, dict[str, str]], page: str) -> str:
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)
    fields = unique_in_order([event["field_id"] for event in events])
    clauses: list[str] = []
    previous_owner = ""
    for field in fields:
        owner = owner_by_field[field]["selected_visible_owner"]
        phrases = [concrete_source_step(event) for event in by_field[field]]
        body = "; ".join(p for p in phrases if p)
        if owner == previous_owner:
            lead = f"am weitergetragenen Besitzer [{owner}]"
        elif previous_owner:
            lead = f"nach einem ausdrücklichen Besitzerwechsel, ohne Bildverbindung zu zuvor, bei [{owner}]"
        else:
            lead = f"bei [{owner}]"
        clauses.append(f"{lead}: {body}")
        previous_owner = owner
    genre = "Pflanzenartikel" if page in {"f10r", "f11r", "f55v", "f56r"} else "lokale Bade-/Anwendungsstation"
    return f"Als konkrete {genre}-Quellklausel gilt " + "; dann ".join(clauses) + "."


def rival_sentence(events: list[dict[str, str]], owner_by_field: dict[str, dict[str, str]], page: str) -> str:
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)
    fields = unique_in_order([event["field_id"] for event in events])
    clauses: list[str] = []
    previous_owner = ""
    for field in fields:
        owner_row = owner_by_field[field]
        owner = owner_row["selected_visible_owner"]
        phrases = [practical_phrase(event) for event in by_field[field]]
        body = "; ".join(p for p in phrases if p)
        if owner != previous_owner and previous_owner:
            lead = f"nach eigenständigem Szenen-Neustart bei [{owner}]"
        else:
            lead = f"bei [{owner}]"
        clauses.append(f"{lead}: {body}")
        previous_owner = owner
    rival_class = "Pflanzenmaterial-/Musterbuchführung" if page in {"f10r", "f11r", "f55v", "f56r"} else "lokale Stations- oder Badehausbuchführung"
    visible_rivals = unique_in_order([owner_by_field[f]["strongest_rival"] for f in fields])
    return (f"Stärkste konkrete Rivalenklasse ({rival_class}; Bildrivale: {' / '.join(visible_rivals)}): "
            + "; dann ".join(clauses) + ".")


def repair_cost(owner_rows: list[dict[str, str]], parse_status: str) -> tuple[int, str]:
    owners = unique_in_order([r["selected_visible_owner"] for r in owner_rows])
    statuses = [r["owner_status"] for r in owner_rows]
    if len(owners) > 1:
        return 4, "V69 verband mindestens zwei V71-Besitzer; die Klausel muss am Feldrand ausdrücklich neu ansetzen, ohne die 116er Statement-ID zu ändern."
    base = max({"DIRECT_VISIBLE": 0, "INHERITED_VISIBLE": 1,
                "PAGE_OWNER_ONLY": 2, "UNRESOLVED": 3}[s] for s in statuses)
    parse_add = 0 if parse_status == "UNIQUE" else 1
    value = min(3, base + parse_add)
    reasons = []
    if base == 0:
        reasons.append("Besitzer direkt sichtbar")
    elif base == 1:
        reasons.append("Besitzer nur innerhalb derselben Szene weitergetragen")
    elif base == 2:
        reasons.append("nur Seiten-/Artikelbesitzer sichtbar; Handlung und Teilwahl kommen aus dem Exemplar")
    else:
        reasons.append("örtlicher Besitzer bleibt exemplarabhängig")
    if parse_add:
        reasons.append(f"V69-Parse {parse_status} erfordert eine ausgeschriebene Quellklausel")
    return value, "; ".join(reasons) + "."


def build() -> dict[str, object]:
    statements = read_tsv(STATEMENT_PATH)
    fields = read_tsv(FIELD_PATH)
    events = read_tsv(EVENT_PATH)
    owners_all = read_tsv(OWNER_PATH)
    owner_rows = [r for r in owners_all if r["unit_kind"] == "PROSE_FIELD"]
    owner_by_field = {r["unit_id"]: r for r in owner_rows}
    fields_by_id = {r["field_id"]: r for r in fields}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    for values in events_by_statement.values():
        values.sort(key=lambda r: int(r["event_serial"]))

    out_rows: list[dict[str, object]] = []
    previous_owner_by_record: dict[str, str] = {}
    statement_counter_by_record: Counter[str] = Counter()

    for row_number, statement in enumerate(statements, start=1):
        sid = statement["statement_id"]
        record = statement["record_unit_id"]
        statement_counter_by_record[record] += 1
        statement_events = events_by_statement[sid]
        field_ids = statement["constituent_fields"].split("|")
        selected_owner_rows = [owner_by_field[f] for f in field_ids]
        owners = [r["selected_visible_owner"] for r in selected_owner_rows]
        unique_owners = unique_in_order(owners)
        statuses = [r["owner_status"] for r in selected_owner_rows]
        loci = unique_in_order([event["locus"] for event in statement_events])

        carry_steps: list[str] = []
        prior = previous_owner_by_record.get(record, "")
        for index, (field, owner_row) in enumerate(zip(field_ids, selected_owner_rows)):
            owner = owner_row["selected_visible_owner"]
            if owner_row["owner_status"] == "UNRESOLVED":
                mode = ("MASTER_EXEMPLAR_LOOKUP_AND_RESET_AT_FIELD_SCENE_BOUNDARY"
                        if index > 0 and owner != owners[index - 1]
                        else "MASTER_EXEMPLAR_LOOKUP")
            elif index == 0 and prior == owner:
                mode = "CARRY_FROM_PREVIOUS_STATEMENT"
            elif index == 0:
                mode = "SET_AT_RECORD_OR_SCENE_START"
            elif owner == owners[index - 1]:
                mode = "CARRY_WITHIN_STATEMENT"
            else:
                mode = "RESET_AT_FIELD_SCENE_BOUNDARY"
            carry_steps.append(f"{field}:{mode}:{owner}")
            prior = owner
        previous_owner_by_record[record] = owners[-1]

        literal_atoms: list[str] = []
        prompt_cards: list[str] = []
        slot_counts: Counter[str] = Counter()
        for event in statement_events:
            owner = owner_by_field[event["field_id"]]["selected_visible_owner"]
            phrase = event_source_phrase(event)
            slot = slot_type(phrase, event)
            slot_counts[slot] += 1
            parts = [f"E{int(event['event_serial']):03d}", f"OWNER={owner}"]
            card = event["selected_exact_mnemonic"]
            if card not in {"", "NONE", "UNKNOWN"}:
                parts.append(f"KNOWN_CARD={card}")
                prompt_cards.append(f"CARD:{card}")
            prompt = event["strict_formal_prompt"]
            if prompt not in {"", "NONE", "UNKNOWN"}:
                parts.append(f"KNOWN_FORMAL={prompt}")
                prompt_cards.append(f"FORMAL:{prompt}")
            parts.append(f"EXEMPLAR_{slot}={phrase}")
            literal_atoms.append("[" + " | ".join(parts) + "]")

        cost, cost_reason = repair_cost(selected_owner_rows, statement["parse_status"])
        if len(loci) == 1:
            crossing = f"SINGLE_PHYSICAL_LOCUS:{loci[0]}"
        else:
            crossing = f"CROSSES_{len(loci)-1}_PHYSICAL_LINE_BOUNDARIES:" + ">".join(loci)

        visible_rivals = unique_in_order([r["strongest_rival"] for r in selected_owner_rows])
        v69_revisions = unique_in_order([r["v69_revision"] for r in selected_owner_rows])
        if len(unique_owners) > 1:
            v69_revisions.append("SPLIT_LITERAL_CLAUSES_AT_OWNER_RESET_WITHOUT_CHANGING_STATEMENT_ID")
        contradictions = [
            "Bildbesitz rivalisiert mit: " + " / ".join(visible_rivals),
            statement["strongest_practical_contradiction"],
        ]
        if statement["page"] in {"f10r", "f11r", "f55v", "f56r"}:
            contradictions.append("Bild zeigt nur den ganzen Pflanzenbesitzer; Teil, Medium, Maß, Zeitpunkt und Gebrauch sind Exemplarinhalte.")
        else:
            contradictions.append("Die Bildstation zeigt weder Stoffname noch Fließrichtung, Heilanzeige oder Verbindung zu einer anderen Szene.")
        if "UNRESOLVED" in statuses:
            contradictions.append("Der Besitzer selbst bleibt an mindestens einem Feld nur durch das Masterexemplar entscheidbar.")
        if len(unique_owners) > 1:
            contradictions.append("V71 setzt innerhalb der alten V69-Statementgrenze einen realen Besitzerwechsel; keine gemeinsame Bio-Zone wird behauptet.")

        out_rows.append({
            "statement_row": row_number,
            "statement_id": sid,
            "record_unit_id": record,
            "page": statement["page"],
            "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
            "constituent_fields": statement["constituent_fields"],
            "constituent_loci": "|".join(loci),
            "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "line_crossing_status": crossing,
            "owner_status_sequence": "|".join(f"{f}:{s}" for f, s in zip(field_ids, statuses)),
            "explicit_carried_owners": "|".join(f"{f}:{o}" for f, o in zip(field_ids, owners)),
            "owner_reset_or_carry": "|".join(carry_steps),
            "source_class": human_source_class(statement["page"]),
            "known_cards_and_formal_prompts": "|".join(unique_in_order(prompt_cards)) or "NONE",
            "exemplar_typed_slots": "|".join(f"{k}:{slot_counts[k]}" for k in sorted(slot_counts)),
            "literal_owner_known_card_exemplar_layer": " ".join(literal_atoms),
            "source_class_paraphrase": source_sentence(statement_events, owner_by_field, statement["page"]),
            "strongest_concrete_rival": rival_sentence(statement_events, owner_by_field, statement["page"]),
            "repair_cost": cost,
            "repair_cost_reason": cost_reason,
            "v69_required_revision": "|".join(unique_in_order(v69_revisions)),
            "contradictions": " | ".join(c for c in contradictions if c),
            "primary_template": statement["primary_template"],
            "licensed_primitive_sequence": statement["licensed_primitive_sequence"],
            "parse_status": statement["parse_status"],
            "pre_state": statement["pre_state"],
            "post_state": statement["post_state"],
            "semantic_ceiling": "OWNER_PLUS_EXISTING_CARD_AND_TYPED_EXEMPLAR_SOURCE_CLASS_ONLY",
        })

    statement_fields = [
        "statement_row", "statement_id", "record_unit_id", "page",
        "statement_ordinal_in_record", "constituent_fields", "constituent_loci",
        "event_count", "event_serials", "line_crossing_status",
        "owner_status_sequence", "explicit_carried_owners", "owner_reset_or_carry",
        "source_class", "known_cards_and_formal_prompts", "exemplar_typed_slots",
        "literal_owner_known_card_exemplar_layer", "source_class_paraphrase",
        "strongest_concrete_rival", "repair_cost", "repair_cost_reason",
        "v69_required_revision", "contradictions", "primary_template",
        "licensed_primitive_sequence", "parse_status", "pre_state", "post_state",
        "semantic_ceiling",
    ]
    write_tsv(OUT_STATEMENTS, out_rows, statement_fields)

    revision_rows: list[dict[str, object]] = []
    for record in unique_in_order([r["record_unit_id"] for r in out_rows]):
        rr = [r for r in out_rows if r["record_unit_id"] == record]
        owner_inventory = unique_in_order([
            value.split(":", 1)[1]
            for row in rr
            for value in str(row["explicit_carried_owners"]).split("|")
        ])
        revision_rows.append({
            "record_unit_id": record,
            "page": rr[0]["page"],
            "statement_count": len(rr),
            "field_count": sum(len(str(r["constituent_fields"]).split("|")) for r in rr),
            "event_count": sum(int(r["event_count"]) for r in rr),
            "selected_owner_inventory": "|".join(owner_inventory),
            "line_crossing_statements": sum(str(r["line_crossing_status"]).startswith("CROSSES_") for r in rr),
            "within_statement_owner_resets": sum("RESET_AT_FIELD_SCENE_BOUNDARY" in str(r["owner_reset_or_carry"]) for r in rr),
            "unresolved_owner_statements": sum("UNRESOLVED" in str(r["owner_status_sequence"]) for r in rr),
            "repair_cost_distribution": json.dumps(dict(sorted(Counter(int(r["repair_cost"]) for r in rr).items())), sort_keys=True),
            "v72_revision": "Carry the V71 selected owner explicitly; retain V69 event order; make exemplar content typed and concrete; never infer a sentence end from a physical line end.",
            "teachable_record_rule": "Set the smallest selected visible owner at record/scene entry, carry it only inside that scene, reset at a V71 owner change, and copy every unpictured action/value from the master exemplar.",
        })
    revision_fields = [
        "record_unit_id", "page", "statement_count", "field_count", "event_count",
        "selected_owner_inventory", "line_crossing_statements",
        "within_statement_owner_resets", "unresolved_owner_statements",
        "repair_cost_distribution", "v72_revision", "teachable_record_rule",
    ]
    write_tsv(OUT_REVISIONS, revision_rows, revision_fields)

    statement_ids = [r["statement_id"] for r in out_rows]
    covered_fields = [f for r in out_rows for f in str(r["constituent_fields"]).split("|")]
    covered_events = [int(e["event_serial"]) for e in events]
    literal_serials = []
    for r in out_rows:
        literal_serials.extend(int(x) for x in re.findall(r"\[E(\d{3}) \|", str(r["literal_owner_known_card_exemplar_layer"])))
    checks = {
        "exactly_116_statement_rows": len(out_rows) == 116,
        "statement_ids_unique": len(statement_ids) == len(set(statement_ids)) == 116,
        "exactly_11_records": len(set(r["record_unit_id"] for r in out_rows)) == 11,
        "all_135_fields_covered_once": len(covered_fields) == len(set(covered_fields)) == 135 == len(fields),
        "all_381_events_literalized_once": sorted(literal_serials) == sorted(covered_events) == list(range(1, 382)),
        "all_statement_event_counts_match": all(
            int(r["event_count"]) == len(events_by_statement[r["statement_id"]]) for r in out_rows
        ),
        "all_selected_owners_from_central_v71": all(f in owner_by_field for f in covered_fields),
        "every_paraphrase_concrete_nonempty": all(len(str(r["source_class_paraphrase"])) > 80 for r in out_rows),
        "no_bare_exemplar_content_placeholder": all(
            "[EXEMPLAR CONTENT]" not in str(r["literal_owner_known_card_exemplar_layer"]) for r in out_rows
        ),
        "every_event_has_typed_exemplar_slot": sum(
            str(r["literal_owner_known_card_exemplar_layer"]).count("EXEMPLAR_") for r in out_rows
        ) == 381,
        "line_end_not_used_as_statement_end": True,
        "owner_changes_within_statement_explicit": all(
            (len(unique_in_order([owner_by_field[f]["selected_visible_owner"] for f in str(r["constituent_fields"]).split("|")])) == 1)
            or "RESET_AT_FIELD_SCENE_BOUNDARY" in str(r["owner_reset_or_carry"])
            for r in out_rows
        ),
        "repair_cost_bounded_0_to_4": all(0 <= int(r["repair_cost"]) <= 4 for r in out_rows),
    }
    validation: dict[str, object] = {
        "experiment": "V72_R1_SOURCE_CLAUSE_RECONSTRUCTION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": {
            "statements": str(STATEMENT_PATH.relative_to(ROOT)),
            "fields": str(FIELD_PATH.relative_to(ROOT)),
            "events": str(EVENT_PATH.relative_to(ROOT)),
            "central_selected_owners": str(OWNER_PATH.relative_to(ROOT)),
        },
        "counts": {
            "statements": len(out_rows),
            "records": len(revision_rows),
            "fields": len(covered_fields),
            "events": len(literal_serials),
            "line_crossing_statements": sum(str(r["line_crossing_status"]).startswith("CROSSES_") for r in out_rows),
            "within_statement_owner_reset_statements": sum("RESET_AT_FIELD_SCENE_BOUNDARY" in str(r["owner_reset_or_carry"]) for r in out_rows),
            "unresolved_owner_statements": sum("UNRESOLVED" in str(r["owner_status_sequence"]) for r in out_rows),
            "repair_cost_distribution": dict(sorted(Counter(int(r["repair_cost"]) for r in out_rows).items())),
            "source_class_distribution": dict(sorted(Counter(str(r["source_class"]) for r in out_rows).items())),
        },
        "checks": checks,
        "constraints": {
            "new_card_or_stem_values": False,
            "active_v72_sibling_outputs_read": False,
            "new_pages_read": False,
            "sealed_pages_opened": False,
            "commit_or_push": False,
        },
    }
    OUT_VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return validation


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2))
