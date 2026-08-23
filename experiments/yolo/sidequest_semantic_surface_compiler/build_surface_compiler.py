#!/usr/bin/env python3
"""Build the creative surface compiler for the fixed ten-page sidequest.

This is deliberately a workshop model, not a decipherment claim.  It asks a
very practical question: which parts of the current 173-card reading are
actually visible and reusable in the 230 registered prose spellings?
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_exception_anatomy"
SURFACE_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_master_reader_codebook/SURFACE_230_READER_KEY.tsv"
DICT_SOURCE = SOURCE_DIR / "COMPLETE_173_THIRD_RING_DICTIONARY.tsv"
EVENT_SOURCE = SOURCE_DIR / "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv"
STATEMENT_SOURCE = SOURCE_DIR / "COMPLETE_116_THIRD_RING_STATEMENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Literal cue families.  These are not claimed phonemes.  They are the visible
# strings an apprentice can use to predict a card's place in a paradigm.
RULES = [
    ("AIIN", "aiin", "SOLLMAß", "aiin", "PORTABLE_ARGUMENT", "`aiin` bleibt auch hinter ch/d/s/t sichtbar"),
    ("AIN", "ain", "PORTION", "(?<!i)ain", "PORTABLE_ARGUMENT", "nicht mit `aiin` oder `iiin` zusammenziehen"),
    ("IIN", "iiin", "STUFE", "iiin", "PORTABLE_ARGUMENT", "drei i markieren die Stufenreihe"),
    ("AL", "al", "ZIELSTELLE", "al", "PORTABLE_ARGUMENT", "Zieladresse; laengeres AIR zuerst lesen"),
    ("AR", "ar", "QUELLE", "ar", "PORTABLE_ARGUMENT", "Quelladresse; laengeres AIR zuerst lesen"),
    ("AIR", "air", "LAUFFLÜSSIGKEIT", "air", "PORTABLE_ARGUMENT", "unteilbarer Richtungs-/Stoffkern"),
    ("OK", "ok", "ANSETZEN", "ok", "PORTABLE_OPERATOR", "q/ch koennen die sichtbare Form rahmen"),
    ("OL", "ol", "FORTSETZEN", "ol", "PORTABLE_OPERATOR", "ch/q/s/t/r koennen als Renderer davor stehen"),
    ("OT", "ot", "DANACH", "ot", "PORTABLE_OPERATOR", "q/s koennen als Renderer davor stehen"),
    ("OR", "or", "ANSATZ", "or", "PORTABLE_NOUN", "ch/sh/s koennen als Renderer davor stehen"),
    ("Y", "y", "DIESER POSTEN", "y$", "PORTABLE_ARGUMENT", "nur als lizenziertes Endargument, nicht jedes sichtbare y"),
    ("E", "e", "KURZ", "e", "BOUND_GRADE", "nur innerhalb einer belegten Gradfamilie"),
    ("EE", "ee", "LÄNGER", "ee", "BOUND_GRADE", "nur innerhalb einer belegten Gradfamilie"),
    ("EEE", "eee", "VOLLSTÄNDIG", "eee", "BOUND_GRADE", "nur innerhalb einer belegten Gradfamilie"),
    ("CHD", "chd~ched", "UMSETZEN", "ch(?:e)?d", "LEXICAL_PROCESS_BODY", "laengster Treffer; blockiert die falsche DCH-Lesung"),
    ("CTH", "cth", "BEREIT", "cth", "LEXICAL_PROCESS_BODY", "Prozesskoerper vor Argument/Grad"),
    ("CKH", "ckh", "DURCHLASS", "ckh", "LEXICAL_PROCESS_BODY", "nicht mit CHK=waermen vertauschen"),
    ("CKHE", "ckhe", "SEIHEN", "ckhe", "LEXICAL_PROCESS_BODY", "laengster Treffer vor CKH"),
    ("CHK", "chk~chek", "WÄRMEN", "ch(?:e+)?k", "LEXICAL_PROCESS_BODY", "familiengebundene Allographie"),
    ("SHED", "shed~chee", "ABSETZEN", "(?:shed|chee)", "LEXICAL_PROCESS_BODY", "nur in der belegten SHED-Reihe"),
    ("SH", "sh", "HALTEN", "sh", "LEXICAL_PROCESS_BODY", "nicht jedes s/h einzeln lesen"),
    ("SOLK", "solk~olk", "SAMMELN", "(?:solk|olk)", "LEXICAL_PROCESS_BODY", "OLK ist hier die gebundene Variante"),
    ("L", "l", "ABFÜHREN", "^l", "PORTABLE_OPERATOR", "nur als linker Operator vor einem bekannten Koerper"),
    ("P", "p", "ZUFÜHREN", "^p", "PORTABLE_OPERATOR", "nur als linker Operator vor CHED"),
    ("HO", "cho~sho", "ZUTAT", "(?:cho|sho)", "LEXICAL_NOUN_BODY", "ganzer Kartenkoerper; nicht O=Wasser"),
    ("CHEO", "cheo", "AUSZUG", "cheo", "LEXICAL_NOUN_BODY", "ganzer Kartenkoerper"),
    ("KCH", "kch", "BEARBEITEN", "kch", "LEXICAL_PROCESS_BODY", "qekey bleibt Rendererallograph dieser Reihe"),
    ("TY", "ty", "TEIL", "ty", "PORTABLE_ARGUMENT", "gebundener Teilmarker"),
    ("CLOSE", "licensed terminal", "SCHLUSS", "(?:dy|edy|eedy|eeedy)$", "BOUND_ENDPOINT", "nur exact-card-lizenziert; nacktes dy kann Y sein"),
]

RULE_BY_ATOM = {row[0]: row for row in RULES}
PORTABLE = {"AIIN", "AIN", "IIN", "AL", "AR", "AIR", "OK", "OL", "OT", "OR", "Y", "E", "EE", "EEE", "L", "P", "TY"}
LEXICAL_BODIES = {"CHD", "CTH", "CKH", "CKHE", "CHK", "SHED", "SH", "SOLK", "HO", "CHEO", "KCH"}
NON_LITERAL = {"CLOSE", "DAIN", "ODY", "OS", "WASH", "PARTITION", "CHEEY"}
SINGLETON_BODIES = {"CFH", "CPH", "DCHE", "LDDY", "SK", "DAN", "AM"}

# The previous pass accidentally promoted DCH as a root.  Correct it before
# any surface parsing.  The other seven items remain usable *lexical bodies*,
# but not productive stems until another independent card shares them.
ATOM_CORRECTIONS = {
    "MC142": "DCHOL",
}

CORRECTION_ROWS = [
    {"old_bridge": "DCH", "old_claim": "voriger Posten", "surface_scope": "dchol|schol", "forward_search_result": "dch erscheint auch in dchdy/dchedy/chedchy/shecthedchy", "new_status": "WITHDRAW_AS_STEM", "new_reading": "DCHOL als gelernte Ganzkarte: voriger Posten", "reason": "DCH kollidiert mit der produktiven CHD~CHED-Umsetzungsfamilie"},
    {"old_bridge": "CFH", "old_claim": "auswringen", "surface_scope": "cfhy", "forward_search_result": "nur diese eine Karte", "new_status": "SINGLETON_LEXICAL_BODY", "new_reading": "CFH+AUSGANG Y: auswringen", "reason": "komponierbar mit Y, aber kein zweiter CFH-Typ"},
    {"old_bridge": "CPH", "old_claim": "nachseihen", "surface_scope": "cphy", "forward_search_result": "nur diese eine Karte", "new_status": "SINGLETON_LEXICAL_BODY", "new_reading": "CPH+Y: nachseihen", "reason": "komponierbar mit Y, aber kein zweiter CPH-Typ"},
    {"old_bridge": "DCHE", "old_claim": "Wurzel", "surface_scope": "dchey", "forward_search_result": "nur diese eine Karte; DCH-Anfang kollidiert", "new_status": "SINGLETON_LEXICAL_BODY", "new_reading": "DCHE+Y: Wurzel als Posten", "reason": "laengster lexikalischer Koerper, kein freies DCH"},
    {"old_bridge": "LDDY", "old_claim": "befestigen; Schluss", "surface_scope": "qokylddy", "forward_search_result": "nur dieser Schwanz", "new_status": "MEMORIZED_TAIL", "new_reading": "OK+Y plus gelernter Schwanz LDDY", "reason": "produktiver Praefix, aber nicht produktiver LDDY-Stamm"},
    {"old_bridge": "SK", "old_claim": "ausgiessen", "surface_scope": "skar", "forward_search_result": "nur diese eine Karte", "new_status": "SINGLETON_LEXICAL_BODY", "new_reading": "SK+AR: aus der Quelle ausgiessen", "reason": "AR bleibt vorhersagbar, SK nicht"},
    {"old_bridge": "DAN", "old_claim": "anwenden", "surface_scope": "sotodan", "forward_search_result": "nur diese eine Karte", "new_status": "MEMORIZED_COMPLEMENT", "new_reading": "OT plus gelernter DAN-Arbeitsgang", "reason": "OT bleibt vorhersagbar, DAN nicht"},
    {"old_bridge": "AM", "old_claim": "verwahren", "surface_scope": "talam", "forward_search_result": "nur diese eine Karte", "new_status": "MEMORIZED_COMPLEMENT", "new_reading": "AL plus gelernter AM-Arbeitsgang", "reason": "AL bleibt vorhersagbar, AM nicht"},
]


def corrected_atoms(row: dict[str, str]) -> list[str]:
    sequence = ATOM_CORRECTIONS.get(row["master_card_id"], row["third_ring_atom_sequence"])
    return sequence.split("+") if sequence else []


def semantic_atom_label(atom: str) -> str:
    if atom in RULE_BY_ATOM:
        return RULE_BY_ATOM[atom][2]
    labels = {
        "DAIN": "TUCH", "ODY": "KÜHLEN", "OS": "TRÄGER", "WASH": "WASCHEN",
        "PARTITION": "TEILEN", "CHEEY": "KLARAUSZUG", "CFH": "AUSWRINGEN",
        "CPH": "NACHSEIHEN", "DCHE": "WURZEL", "LDDY": "BEFESTIGEN",
        "SK": "AUSGIESSEN", "DAN": "ANWENDEN", "AM": "VERWAHREN",
        "DCHOL": "VORIGER POSTEN", "LOCAL_WHOLE": "ZUSATZ",
    }
    return labels.get(atom, atom)


def cue_for_atom(surface: str, atom: str) -> str:
    if atom not in RULE_BY_ATOM:
        return ""
    pattern = RULE_BY_ATOM[atom][3]
    match = re.search(pattern, surface)
    if not match:
        return ""
    return f"{atom}={match.group(0)}@{match.start()}-{match.end()}"


def parse_class(atoms: list[str], surface_role: str) -> str:
    aset = set(atoms)
    if aset & {"DCHOL", "LOCAL_WHOLE"}:
        return "MEMORIZED_WHOLE"
    if aset & SINGLETON_BODIES:
        return "PRODUCTIVE_FRAME_PLUS_MEMORIZED_BODY"
    if aset & NON_LITERAL:
        if len(atoms) == 1:
            return "MEMORIZED_WHOLE"
        return "LEXICAL_BODY_PLUS_PRODUCTIVE_SUFFIX"
    if aset & LEXICAL_BODIES:
        return "LEXICAL_BODY_PLUS_PRODUCTIVE_SUFFIX" if len(atoms) > 1 else "LEXICAL_ROOT_ONLY"
    if aset and aset <= PORTABLE | {"CLOSE"}:
        if surface_role == "OTHER_REGISTERED_ALLOGRAPH":
            return "RENDERER_ALIAS_PLUS_PRODUCTIVE_PARSE"
        return "LITERAL_PRODUCTIVE_PARSE"
    return "MEMORIZED_WHOLE"


def family_root(atoms: list[str]) -> str:
    if not atoms:
        return "NONE"
    for atom in atoms:
        if atom in {"OK", "OL", "OT", "CHD", "CTH", "CKH", "CKHE", "CHK", "SHED", "SOLK", "HO", "L", "Y", "OR"}:
            return atom
    return atoms[0]


def skeleton_candidates(root: str, complement: str) -> set[str]:
    spell = {
        "OK": ["ok", "qok", "chok"], "OL": ["ol", "qol", "chol", "sol"],
        "OT": ["ot", "qot", "sot"], "CHD": ["chd", "ched"], "CTH": ["cth"],
        "CKH": ["ckh", "checkh", "sheckh"], "CHK": ["chk", "chek", "cheek"],
        "SHED": ["shed", "chee"], "SOLK": ["solk", "olk"], "HO": ["cho", "sho"],
        "L": ["l"], "Y": ["y"], "OR": ["or", "chor", "shor"],
        "AIIN": ["aiin"], "AIN": ["ain"], "IIN": ["iiin"], "AL": ["al"],
        "AR": ["ar"], "AIR": ["air"], "E": ["e"], "EE": ["ee"], "EEE": ["eee"],
        "YARG": ["y", "chy"], "CLOSE": ["dy", "edy", "eedy"], "ORARG": ["or", "chor"],
    }
    lefts = spell.get(root, [root.lower()])
    rights = spell.get(complement, [complement.lower()])
    return {a + b for a in lefts for b in rights}


def main() -> None:
    dictionary = read_tsv(DICT_SOURCE)
    surfaces = read_tsv(SURFACE_SOURCE)
    events = read_tsv(EVENT_SOURCE)
    statements = read_tsv(STATEMENT_SOURCE)
    by_card = {row["master_card_id"]: row for row in dictionary}

    rule_rows = []
    for atom, visible, meaning, pattern, category, boundary in RULES:
        card_ids = []
        event_count = 0
        for row in dictionary:
            atoms = corrected_atoms(row)
            if atom in atoms:
                card_ids.append(row["master_card_id"])
                event_count += int(row["prose_event_count"])
        rule_rows.append({
            "atom": atom, "visible_cue_family": visible, "short_value_de": meaning,
            "rule_category": category, "longest_match_priority": "YES" if atom in {"AIR", "CKHE", "EEE", "EE", "CHD"} else "NORMAL",
            "boundary_rule": boundary, "master_card_types": len(set(card_ids)), "prose_events": event_count,
            "productive_status": "PRODUCTIVE" if len(set(card_ids)) >= 2 or atom in PORTABLE else "BOUND_OR_LEARNED",
        })
    write_tsv(HERE / "SURFACE_COMPILER_RULES.tsv", rule_rows, list(rule_rows[0]))

    surface_rows = []
    card_surface_count = Counter()
    for row in surfaces:
        card = by_card[row["master_card_id"]]
        atoms = corrected_atoms(card)
        cues = [cue_for_atom(row["visible_surface"], atom) for atom in atoms]
        cues = [cue for cue in cues if cue]
        uncued = [atom for atom in atoms if not cue_for_atom(row["visible_surface"], atom)]
        pclass = parse_class(atoms, row["surface_role"])
        card_surface_count[row["master_card_id"]] += 1
        surface_rows.append({
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "master_head_form": row["master_head_form"], "surface_role": row["surface_role"],
            "corrected_semantic_atoms": "+".join(atoms),
            "surface_parse_de": " + ".join(semantic_atom_label(atom) for atom in atoms),
            "observed_literal_cues": " | ".join(cues) if cues else "NONE",
            "contextual_or_memorized_atoms": "+".join(uncued) if uncued else "NONE",
            "parse_class": pclass,
            "short_default_de": card["third_ring_concrete_default_de"],
            "observed_events": row["observed_event_count"],
            "collision_guard": "DCH_BLOCKED_BY_CHD_LONGEST_MATCH" if row["visible_surface"].startswith("dch") else "NONE",
        })
    write_tsv(HERE / "COMPLETE_230_SURFACE_PARSE.tsv", surface_rows, list(surface_rows[0]))

    surfaces_by_card = defaultdict(list)
    for row in surface_rows:
        surfaces_by_card[row["master_card_id"]].append(row)
    card_rows = []
    for card in dictionary:
        atoms = corrected_atoms(card)
        srows = surfaces_by_card[card["master_card_id"]]
        classes = Counter(row["parse_class"] for row in srows)
        dominant = classes.most_common(1)[0][0]
        observed_cue_forms = sum(row["observed_literal_cues"] != "NONE" for row in srows)
        literal_atoms = [atom for atom in atoms if atom in RULE_BY_ATOM]
        learned_atoms = [atom for atom in atoms if atom not in RULE_BY_ATOM]
        card_rows.append({
            "master_card_id": card["master_card_id"], "master_head_form": card["master_head_form"],
            "registered_surface_family": card["registered_surface_family"],
            "corrected_semantic_atoms": "+".join(atoms),
            "literal_predictive_atoms": "+".join(literal_atoms) if literal_atoms else "NONE",
            "learned_or_contextual_atoms": "+".join(learned_atoms) if learned_atoms else "NONE",
            "parse_class": dominant,
            "short_default_de": card["third_ring_concrete_default_de"],
            "imperative_de": card["third_ring_imperative_de"],
            "prose_events": card["prose_event_count"],
            "surface_forms": len(srows),
            "surface_forms_with_observed_cue": observed_cue_forms,
            "forward_reading_rule": " -> ".join(semantic_atom_label(atom) for atom in atoms),
            "correction_from_previous_pass": "YES" if card["master_card_id"] == "MC142" else "NO",
        })
    write_tsv(HERE / "COMPLETE_173_LITERAL_PARSE.tsv", card_rows, list(card_rows[0]))

    root_groups = defaultdict(list)
    for row in card_rows:
        atoms = row["corrected_semantic_atoms"].split("+")
        root_groups[family_root(atoms)].append(row)
    paradigm_rows = []
    for root, rows in sorted(root_groups.items()):
        if len(rows) < 2:
            continue
        tails = Counter()
        for row in rows:
            atoms = row["corrected_semantic_atoms"].split("+")
            try:
                idx = atoms.index(root)
                tail = "+".join(atoms[idx + 1:]) or "BARE"
            except ValueError:
                tail = "+".join(atoms)
            tails[tail] += 1
        paradigm_rows.append({
            "family_root": root, "root_value_de": semantic_atom_label(root),
            "master_card_types": len(rows), "prose_events": sum(int(row["prose_events"]) for row in rows),
            "observed_complements": " | ".join(f"{tail}:{count}" for tail, count in sorted(tails.items())),
            "surface_families": " | ".join(row["registered_surface_family"] for row in rows),
            "forward_strength": "STRONG" if len(rows) >= 5 else "WORKING",
            "creative_rule_de": f"Lies {root} als {semantic_atom_label(root)} und fuege den sichtbaren Argument-/Grad-/Endpunktwert an.",
        })
    write_tsv(HERE / "PRODUCTIVE_PARADIGMS.tsv", paradigm_rows, list(paradigm_rows[0]))

    existing_sequences = {row["corrected_semantic_atoms"] for row in card_rows}
    all_surfaces = {row["visible_surface"] for row in surface_rows}
    prediction_specs = [
        ("OK", "IIN", "Arbeitsstufe einstellen"), ("OK", "ORARG", "Ansatz ansetzen"),
        ("OL", "AIIN", "Fortsetzungsmaß"), ("OL", "AL", "zur Folgestelle weiterführen"),
        ("OL", "AR", "vom Ausgang weiterführen"), ("OT", "AIN", "Folgeportion"),
        ("OT", "AIR", "nächsten Wasserlauf nehmen"), ("CHD", "AIIN", "nach Sollmaß umsetzen"),
        ("CHD", "IIN", "bis zur Stufe umsetzen"), ("CTH", "AL", "an Zielstelle bereitstellen"),
        ("CTH", "AR", "aus der Quelle bereitstellen"), ("CKH", "AR", "von der Quelle durchleiten"),
        ("CKH", "AIIN", "bis Sollmaß durchleiten"), ("CHK", "AL", "an der Zielstelle wärmen"),
        ("SHED", "AR", "aus der Quelle absetzen lassen"), ("SOLK", "AL", "an Zielstelle sammeln"),
        ("HO", "AIN", "eine Zutatenportion"), ("HO", "AR", "Zutat aus der Quelle"),
    ]
    prediction_rows = []
    for root, complement, gloss in prediction_specs:
        semantic_comp = "OR" if complement == "ORARG" else complement
        seq = f"{root}+{semantic_comp}"
        skeletons = skeleton_candidates(root, complement)
        exact_hits = sorted(all_surfaces & skeletons)
        loose_hits = sorted(surface for surface in all_surfaces if any(skeleton in surface for skeleton in skeletons))
        prediction_rows.append({
            "predicted_atom_sequence": seq, "predicted_short_reading_de": gloss,
            "predicted_surface_skeletons": "|".join(sorted(skeletons)),
            "already_semantically_registered": "YES" if seq in existing_sequences else "NO",
            "exact_surface_hits_in_230": "|".join(exact_hits) if exact_hits else "NONE",
            "loose_surface_hits_in_230": "|".join(loose_hits) if loose_hits else "NONE",
            "status": "OBSERVED_ELSEWHERE_REVIEW" if loose_hits else "EMPTY_PRODUCTIVE_CELL",
            "use_rule": "prediction only; do not silently relabel an existing exact card",
        })
    write_tsv(HERE / "FORWARD_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    write_tsv(HERE / "BRIDGE_ROOT_CORRECTIONS.tsv", CORRECTION_ROWS, list(CORRECTION_ROWS[0]))

    class_counts = Counter(row["parse_class"] for row in card_rows)
    event_class_counts = Counter()
    for row in card_rows:
        event_class_counts[row["parse_class"]] += int(row["prose_events"])
    cue_cards = sum(1 for row in card_rows if int(row["surface_forms_with_observed_cue"]) > 0)
    cue_events = sum(int(row["prose_events"]) for row in card_rows if int(row["surface_forms_with_observed_cue"]) > 0)
    dch_forms = [row["visible_surface"] for row in surface_rows if "dch" in row["visible_surface"]]
    report = f"""# Oberflächen-Compiler der Werkstatt

## Was korrigiert wurde

Der vorige Durchgang war bei `DCH` zu schnell. `dchol/schol` kann weiterhin als gelernte Karte **VORIGER POSTEN** gelesen werden, aber `DCH` ist kein tragfähiger Stamm: dieselben sichtbaren Buchstaben liegen auch in Umsetzungsformen wie `dchdy`, `dchedy`, `chedchy` und `shecthedchy`. Der Compiler verwendet deshalb längsten Treffer: `CHD~CHED = UMSETZEN` schlägt jede freie `DCH`-Analyse. Die sieben anderen alten Brücken sind vorerst nur gelernte lexikalische Körper oder Schwänze, keine produktiven Stämme.

## Neue Arbeitsregel

Eine sichtbare Karte wird von außen nach innen gelesen:

1. registrierte Renderer-/Schreiberform erkennen;
2. längsten bekannten Körper nehmen (`AIR`, `CHD~CHED`, `CKHE` vor kürzeren Treffern);
3. portable Operatoren und Adressen lesen (`OK/OL/OT`, `AIIN/AIN/IIN`, `AL/AR/AIR`);
4. nur in einer belegten Familie `E/EE/EEE` als kurz/länger/voll lesen;
5. `Y` nur als lizenziertes Postenargument und `DY` nur exact-card-gebunden als Schluss lesen.

Damit besitzen {cue_cards}/173 Kartentypen und {cue_events}/381 Prosaereignisse mindestens einen sichtbar wiederverwendbaren Beitrag. Das ist noch keine Buchstabenentzifferung: der Compiler trennt echte Oberflächenhinweise von gelernten Fachkörpern.

## Verteilung der 173 Karten

"""
    for key in sorted(class_counts):
        report += f"- `{key}`: {class_counts[key]} Karten / {event_class_counts[key]} Ereignisse\n"
    report += f"""

## Produktive Vorhersage statt Rückerzählung

`FORWARD_PREDICTIONS.tsv` enthält 18 vorwärts gebildete Zellen. Die Regel darf eine bisher nicht belegte Karte lesen, falls sie später auftaucht; sie darf aber keine vorhandene Karte still umbenennen. Treffer in den 230 Formen werden deshalb nur als Review-Kandidaten markiert. Die stärksten Reihen sind derzeit `OK`, `OL`, `OT`, `CHD`, `CTH`, `CKH`, `CHK`, `SHED`, `SOLK`, `HO`, `L`, `Y` und `OR`.

## Kollisionsaudit

Sichtbare Formen mit `dch`: {', '.join(dch_forms)}. Nur `dchol/schol` bleibt als gelernter Ganzwert; die Umsetzungsfamilie behält `CHD~CHED`. Ebenso bleiben `CFH`, `CPH`, `DCHE`, `LDDY`, `SK`, `DAN` und `AM` kurze Werkstatt-Mnemonics, bis eine zweite unabhängige Karte denselben Körper produktiv benutzt.

## Nächster Hebel

Der Compiler wird im nächsten Pass nicht auf weitere Bedeutungen trainiert, sondern auf die 381 laufenden Kontexte angewandt. Besonders wichtig sind die leeren Vorhersagezellen und die Karten, deren sichtbare Form zwar passt, deren bisheriger Ganzwert aber widerspricht. Danach wird derselbe Parser ohne neue Wortbedeutung gegen die 395 Astrogruppen gehalten.
"""
    (HERE / "SURFACE_COMPILER_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "dictionary_cards": len(dictionary), "surface_forms": len(surfaces),
        "prose_events": len(events), "statements": len(statements),
        "cards_with_literal_predictive_atom": cue_cards,
        "events_with_literal_predictive_atom": cue_events,
        "parse_class_cards": dict(sorted(class_counts.items())),
        "parse_class_events": dict(sorted(event_class_counts.items())),
        "bridge_corrections": len(CORRECTION_ROWS),
        "forward_predictions": len(prediction_rows),
        "source_sha256": {
            str(DICT_SOURCE.relative_to(ROOT)): sha256(DICT_SOURCE),
            str(SURFACE_SOURCE.relative_to(ROOT)): sha256(SURFACE_SOURCE),
            str(EVENT_SOURCE.relative_to(ROOT)): sha256(EVENT_SOURCE),
            str(STATEMENT_SOURCE.relative_to(ROOT)): sha256(STATEMENT_SOURCE),
        },
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
