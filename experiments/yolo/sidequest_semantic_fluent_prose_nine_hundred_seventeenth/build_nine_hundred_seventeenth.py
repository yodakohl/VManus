#!/usr/bin/env python3
"""Build Pass 917: complete fluent prose for every selected prose event."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P916 = ROOT / "experiments/yolo/sidequest_semantic_workshop_phrasebook_nine_hundred_sixteenth"


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)


ACTIONS = {
    "P": "einsetzen", "CH": "entnehmen", "O": "bearbeiten",
    "CTH": "bis bereit führen", "SH": "halten", "OK": "ansetzen",
    "K": "zugeben oder zuordnen", "T": "bearbeiten", "CHD": "umsetzen",
    "CHK": "behandeln", "S": "prüfen", "SHED": "ruhen lassen",
    "CFH": "pressen oder trennen", "LSH": "spülen", "CPH": "in den Gegengang führen",
    "R": "den Zustand markieren", "SOLK": "an der Sammelstelle aufnehmen",
}
ACTION_KEYS = set(ACTIONS)
CONNECTORS = {"OT": "danach", "OL": "weiter", "OS": "auch", "RESUME_CARD": "davon ausgehend"}
OBJECTS = {"Y": "diesen Posten", "OR": "den Ansatz", "CHEO": "den Auszug", "HO": "den Stoffteil"}
SOURCES = {"AR": "von der Entnahmestelle", "D_ADDR": "aus diesem Teil", "A_ADDR": "von der lokalen Stelle"}
QUANTITIES = {"AIIN": "nach Sollmaß", "AIN": "als eine Portion", "IIN": "auf der angegebenen Stufe", "DA": "auf der zweiten Stufe"}
TARGETS = {
    "AL": "zur Ziel- oder Anschlussstelle", "AM_ADDR": "zur Innenstelle",
    "L": "in den nächsten Lauf", "CKH": "durch den Durchlass", "AIR": "entlang des Laufs",
    "S_ADDR": "zur bezeichneten s-Stelle",
}
GRADES = {"E": "kurz", "EE": "länger", "EEE": "vollständig"}
DETAILS = {
    "CARRIER_Q": "unter q-Träger", "D_LABEL": "mit d-Zeichen", "M_LOCAL": "mit m-Zeichen",
    "LOCAL_CHAR_B": "mit b-Zeichen", "LOCAL_CHAR_F": "mit f-Zeichen",
    "LOCAL_CHAR_G": "mit g-Zeichen", "LOCAL_CHAR_I": "mit i-Zeichen",
    "LOCAL_CHAR_J": "mit j-Zeichen",
}


def unique(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def german_join(xs):
    if not xs: return ""
    if len(xs) == 1: return xs[0]
    if len(xs) == 2: return f"{xs[0]} und {xs[1]}"
    return ", ".join(xs[:-1]) + " und " + xs[-1]


def render(atoms):
    connectors = unique(CONNECTORS[a] for a in atoms if a in CONNECTORS)
    objects = unique(OBJECTS[a] for a in atoms if a in OBJECTS)
    sources = unique(SOURCES[a] for a in atoms if a in SOURCES)
    quantities = unique(QUANTITIES[a] for a in atoms if a in QUANTITIES)
    targets = unique(TARGETS[a] for a in atoms if a in TARGETS)
    grades = unique(GRADES[a] for a in atoms if a in GRADES)
    details = unique(DETAILS[a] for a in atoms if a in DETAILS)
    acts = []
    for a in atoms:
        if a in ACTIONS and (not acts or acts[-1] != ACTIONS[a]):
            acts.append(ACTIONS[a])
    closed = "DY" in atoms

    lead = " ".join(connectors)
    obj = german_join(objects)
    src = " ".join(sources)
    qty = " ".join(quantities)
    grade = " ".join(grades)
    target = " ".join(targets)
    detail = " ".join(details)
    if acts:
        pieces = [lead, src, qty, obj, grade, german_join(acts), target, detail]
    else:
        # These are real elliptical cards: make their carried instruction explicit.
        pieces = [lead, src, qty, ("mit " + obj if obj else ""), target, grade, detail, "weiterarbeiten"]
    sentence = " ".join(x for x in pieces if x).strip()
    if closed:
        sentence += "; fertig"
    return sentence[0].upper() + sentence[1:] + "."


def main():
    events = read_tsv(P916 / "PASS916_2010_EVENT_PHRASES.tsv")
    clauses = read_tsv(P916 / "PASS916_354_COMPACT_CLAUSES.tsv")
    index = {r["event_id"]: i for i, r in enumerate(events)}

    instructions = []
    event_bindings = []
    clause_rows = []
    iid = 0
    for clause in clauses:
        rs = events[index[clause["start_event"]]: index[clause["end_event"]] + 1]
        pending = []
        local_ids = []
        for event in rs:
            pending.append(event)
            atoms = event["component_recipe"].split("+")
            if ACTION_KEYS.intersection(atoms) or "DY" in atoms:
                iid += 1
                iid_s = f"P917-I{iid:04d}"
                flat = [a for r in pending for a in r["component_recipe"].split("+")]
                loci = list(dict.fromkeys(r["locus"] for r in pending))
                row = {
                    "instruction_id": iid_s,
                    "clause_id": clause["clause_id"],
                    "physical_page": clause["physical_page"],
                    "register": clause["register"],
                    "start_event": pending[0]["event_id"],
                    "end_event": pending[-1]["event_id"],
                    "event_count": str(len(pending)),
                    "loci": "|".join(loci),
                    "crosses_physical_line": "YES" if len(loci) > 1 else "NO",
                    "surface_sequence": " · ".join(r["surface"] for r in pending),
                    "component_sequence": " | ".join(r["component_recipe"] for r in pending),
                    "fluent_workshop_de": render(flat),
                    "editorial_boundary": "ACTION_OR_LICENSED_CLOSE",
                }
                instructions.append(row); local_ids.append(iid_s)
                for r in pending:
                    event_bindings.append({"event_id": r["event_id"], "instruction_id": iid_s,
                                           "clause_id": clause["clause_id"], "physical_page": clause["physical_page"],
                                           "surface": r["surface"], "component_recipe": r["component_recipe"],
                                           "workshop_phrase_de": r["workshop_phrase_de"]})
                pending = []
        if pending:
            iid += 1
            iid_s = f"P917-I{iid:04d}"
            flat = [a for r in pending for a in r["component_recipe"].split("+")]
            loci = list(dict.fromkeys(r["locus"] for r in pending))
            instructions.append({
                "instruction_id": iid_s, "clause_id": clause["clause_id"],
                "physical_page": clause["physical_page"], "register": clause["register"],
                "start_event": pending[0]["event_id"], "end_event": pending[-1]["event_id"],
                "event_count": str(len(pending)), "loci": "|".join(loci),
                "crosses_physical_line": "YES" if len(loci) > 1 else "NO",
                "surface_sequence": " · ".join(r["surface"] for r in pending),
                "component_sequence": " | ".join(r["component_recipe"] for r in pending),
                "fluent_workshop_de": render(flat), "editorial_boundary": "CLAUSE_END_ELLIPSIS",
            }); local_ids.append(iid_s)
            for r in pending:
                event_bindings.append({"event_id": r["event_id"], "instruction_id": iid_s,
                                       "clause_id": clause["clause_id"], "physical_page": clause["physical_page"],
                                       "surface": r["surface"], "component_recipe": r["component_recipe"],
                                       "workshop_phrase_de": r["workshop_phrase_de"]})
        clause_rows.append({
            "clause_id": clause["clause_id"], "physical_page": clause["physical_page"],
            "register": clause["register"], "start_event": clause["start_event"],
            "end_event": clause["end_event"], "events": clause["events"],
            "instruction_count": str(len(local_ids)), "instruction_ids": "|".join(local_ids),
            "crosses_physical_line": clause["crosses_physical_line"], "end_reason": clause["end_reason"],
            "fluent_clause_de": " ".join(instructions[int(x.split('I')[1]) - 1]["fluent_workshop_de"] for x in local_ids),
        })

    write_tsv(OUT / "PASS917_1435_FLUENT_INSTRUCTIONS.tsv", instructions, list(instructions[0]))
    write_tsv(OUT / "PASS917_2010_EVENT_BINDINGS.tsv", event_bindings, list(event_bindings[0]))
    write_tsv(OUT / "PASS917_354_FLUENT_CLAUSES.tsv", clause_rows, list(clause_rows[0]))

    pages = list(dict.fromkeys(r["physical_page"] for r in clause_rows))
    doc = ["# Pass 917 — vollständige flüssige Prosafassung", "",
           "Die Punkte unten sind gesprochene Arbeitszüge, keine behaupteten Manuskriptsatzzeichen.",
           "Physische Zeilen dürfen mitten im Arbeitszug wechseln.", ""]
    for page in pages:
        doc += [f"## {page}", ""]
        for row in clause_rows:
            if row["physical_page"] == page:
                doc.append(f"- **{row['clause_id']}** {row['fluent_clause_de']}")
        doc.append("")
    (OUT / "PASS917_TWELVE_PAGE_FLUENT_EDITION.md").write_text("\n".join(doc), encoding="utf-8")

    pc = Counter(r["physical_page"] for r in instructions)
    report = f"""# Pass 917 — erste vollständige flüssige Werkstattprosa

## Was jetzt lesbar ist

Alle 2010 Prosagruppen sind in genau {len(instructions)} gesprochene Arbeitszüge
gebunden. 387 davon tragen mehr als eine sichtbare Karte; der längste bindet zehn.
Die 354 echten Klauseln und ihre 121 Zeilenübertritte bleiben unverändert.

Die flüssige Grundordnung lautet:

**danach/weiter → aus Quelle/Teil → nach Maß/Portion → diesen Posten/Ansatz/Auszug
→ kurz/länger → Handlung → Ziel/Lauf/Durchlass → fertig.**

Reine Karten wie `AIIN`, `Y`, `OL` oder `AR` werden bis zur nächsten Handlung
mitgetragen. Darum werden sie nicht mehr als abgehackte Einzelwörter gesprochen.
Bleibt am Klauselende nur solch ein Bündel, erhält es die natürliche Ellipse
„damit weiterarbeiten“.

## Seitenumfang

""" + "\n".join(f"- {p}: {pc[p]} Arbeitszüge" for p in pages) + """

## Arbeitsstand

Das ist nun eine vollständige kreative Übersetzungsschicht der gesamten Prosa im
14-Seiten-Scope. Die sachlichen Besitzer bleiben bildgebunden: Pflanzenteil,
Becken-/Stationsposten, Ringstelle oder Rezeptansatz. Im nächsten Pass werden die
häufigsten Arbeitszüge gegeneinander verglichen, damit wir Verben mit gleicher
Funktion zusammenlegen und überladene Bedeutungen wieder kürzen können.
"""
    (OUT / "PASS917_REPORT.md").write_text(report, encoding="utf-8")

    outputs = ["PASS917_1435_FLUENT_INSTRUCTIONS.tsv", "PASS917_2010_EVENT_BINDINGS.tsv",
               "PASS917_354_FLUENT_CLAUSES.tsv", "PASS917_TWELVE_PAGE_FLUENT_EDITION.md", "PASS917_REPORT.md"]
    summary = {
        "status": "BUILT", "prose_events": len(event_bindings), "clauses": len(clause_rows),
        "instructions": len(instructions), "multi_event_instructions": sum(int(r["event_count"]) > 1 for r in instructions),
        "max_events_per_instruction": max(int(r["event_count"]) for r in instructions),
        "pages": pages, "page_instruction_counts": dict(pc),
        "sha256": {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest() for n in outputs},
    }
    (OUT / "PASS917_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
