#!/usr/bin/env python3
"""Build Pass 916: a compact compositional workshop phrasebook."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P915 = ROOT / "experiments/yolo/sidequest_semantic_clause_word_order_nine_hundred_fifteenth"


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


ATOMS = {
    "AIIN": "Sollmaß", "AIN": "Portion", "AIR": "Lauf", "AL": "Zielstelle",
    "AM_ADDR": "Innenstelle", "AN": "Zusatz", "AR": "Entnahmestelle",
    "A_ADDR": "Adresse", "CARRIER_Q": "q-Träger", "CFH": "pressen/trennen",
    "CH": "entnehmen", "CHD": "umsetzen", "CHEO": "Auszug", "CHK": "behandeln",
    "CKH": "Durchlass", "CPH": "Gegen-/Empfangsgang", "CTH": "Bereitschaft",
    "DA": "zweite Stufe", "DY": "Schluss", "D_ADDR": "Teilstelle",
    "D_LABEL": "d-Zeichen", "E": "kurz", "EE": "länger", "EEE": "vollständig",
    "G_LABEL": "g-Zeichen", "HO": "Stoffteil", "IIN": "Stufe", "K": "zuordnen",
    "L": "leiten", "LD": "befestigen", "LSH": "spülen", "M_LOCAL": "m-Zeichen",
    "O": "Arbeitsgang", "OK": "ansetzen", "OL": "fortsetzen", "OR": "Ansatz",
    "OS": "dazu", "OT": "danach", "P": "einsetzen", "R": "Zustand",
    "RESUME_CARD": "wiederaufnehmen", "S": "prüfen", "SH": "halten",
    "SHED": "absetzen", "SOLK": "Sammelstelle", "S_ADDR": "s-Stelle",
    "T": "bearbeiten", "Y": "dies",
    "LOCAL_CHAR_B": "b-Zeichen", "LOCAL_CHAR_F": "f-Zeichen",
    "LOCAL_CHAR_G": "g-Zeichen", "LOCAL_CHAR_I": "i-Zeichen",
    "LOCAL_CHAR_J": "j-Zeichen",
}


MACROS = [
    ("M01", ("OK", "EE", "DY"), "länger ansetzen; fertig", "graded operation"),
    ("M02", ("OK", "E", "DY"), "kurz ansetzen; fertig", "graded operation"),
    ("M03", ("OK", "EE", "Y"), "dies länger ansetzen", "graded operation"),
    ("M04", ("OK", "E", "Y"), "dies kurz ansetzen", "graded operation"),
    ("M05", ("SH", "EE", "DY"), "länger halten; fertig", "graded hold"),
    ("M06", ("SH", "E", "DY"), "kurz halten; fertig", "graded hold"),
    ("M07", ("SH", "EE", "Y"), "dies länger halten", "graded hold"),
    ("M08", ("SH", "E", "Y"), "dies kurz halten", "graded hold"),
    ("M09", ("OT", "EE", "DY"), "danach länger; fertig", "ordered grade"),
    ("M10", ("OT", "E", "DY"), "danach kurz; fertig", "ordered grade"),
    ("M11", ("SHED", "DY"), "ruhen lassen; fertig", "rest endpoint"),
    ("M12", ("L", "CHD", "DY"), "abführen und umsetzen; fertig", "transfer endpoint"),
    ("M13", ("OL", "CHD", "DY"), "weiter umsetzen; fertig", "continuation endpoint"),
    ("M14", ("OK", "CHD", "DY"), "ansetzen und umsetzen; fertig", "operation endpoint"),
    ("M15", ("P", "CHD", "DY"), "einsetzen und umsetzen; fertig", "entry endpoint"),
    ("M16", ("LSH", "E", "DY"), "kurz spülen; fertig", "wash endpoint"),
    ("M17", ("CHD", "Y"), "dies umsetzen", "referential transfer"),
    ("M18", ("CKH", "Y"), "dies durch den Durchlass", "path phrase"),
    ("M19", ("CHEO", "L"), "den Auszug weiterleiten", "content transfer"),
    ("M20", ("D_ADDR", "AR"), "aus diesem Teil entnehmen", "source phrase"),
    ("M21", ("OK", "AIIN"), "nach Sollmaß ansetzen", "measured operation"),
    ("M22", ("OK", "AIN"), "eine Portion ansetzen", "portioned operation"),
    ("M23", ("OK", "AL"), "an der Zielstelle ansetzen", "targeted operation"),
    ("M24", ("OK", "AR"), "von der Entnahmestelle ansetzen", "sourced operation"),
    ("M25", ("OL", "DY"), "fortsetzen; fertig", "continuation endpoint"),
    ("M26", ("OL", "Y"), "mit diesem fortsetzen", "referential continuation"),
    ("M27", ("OT", "Y"), "danach diesen Posten", "ordered referent"),
    ("M28", ("S", "AIIN"), "das Sollmaß prüfen", "measurement check"),
    ("M29", ("S", "AIN"), "die Portion prüfen", "portion check"),
    ("M30", ("S", "AR"), "die Entnahmestelle prüfen", "source check"),
    ("M31", ("CH", "OR"), "vom Ansatz entnehmen", "content selection"),
    ("M32", ("CTH", "Y"), "die Bereitschaft dieses Postens prüfen", "state check"),
    ("M33", ("CHK", "E", "Y"), "dies kurz behandeln", "graded treatment"),
    ("M34", ("CHK", "EE", "Y"), "dies länger behandeln", "graded treatment"),
    ("M35", ("SOLK", "EE", "Y"), "dies länger an der Sammelstelle halten", "station hold"),
    ("M36", ("OK", "OL"), "den Gang beginnen und fortsetzen", "operation continuation"),
    ("M37", ("OT", "OR"), "danach mit dem Ansatz", "ordered content"),
    ("M38", ("D_ADDR", "OL"), "in diesem Teil fortsetzen", "local continuation"),
    ("M39", ("O", "P", "Y"), "dies in den Arbeitsgang einsetzen", "work entry"),
    ("M40", ("K", "AIIN"), "nach Sollmaß zuordnen", "measured assignment"),
    ("M41", ("K", "AIN"), "eine Portion zuordnen", "portioned assignment"),
    ("M42", ("K", "AL"), "der Zielstelle zuordnen", "target assignment"),
    ("M43", ("SH", "OR"), "den Ansatz halten", "content hold"),
    ("M44", ("OL", "OR"), "mit dem Ansatz fortsetzen", "content continuation"),
]

MACROS_SORTED = sorted(MACROS, key=lambda x: (-len(x[1]), x[0]))
MACRO_IDS = {m[0] for m in MACROS}


def segment(recipe: str):
    atoms = recipe.split("+")
    out = []
    i = 0
    while i < len(atoms):
        match = next((m for m in MACROS_SORTED if tuple(atoms[i:i + len(m[1])]) == m[1]), None)
        if match:
            out.append((match[0], match[2], len(match[1])))
            i += len(match[1])
        else:
            a = atoms[i]
            out.append((a, ATOMS[a], 1))
            i += 1
    return out


def main():
    events = read_tsv(P915 / "PASS915_2010_PROSE_EVENT_SLOTS.tsv")
    clauses = read_tsv(P915 / "PASS915_354_CLAUSE_EDITION.tsv")
    by_event = {}
    event_out = []
    macro_use = Counter()
    macro_events = 0
    covered_atoms = 0
    total_atoms = 0
    for r in events:
        seg = segment(r["component_recipe"])
        ids = [x[0] for x in seg]
        phrases = [x[1] for x in seg]
        hits = [x for x in seg if x[0] in MACRO_IDS]
        macro_use.update(x[0] for x in hits)
        if hits:
            macro_events += 1
        covered_atoms += sum(x[2] for x in hits)
        total_atoms += len(r["component_recipe"].split("+"))
        row = dict(r)
        row.update({
            "phrase_units": "+".join(ids),
            "workshop_phrase_de": "; ".join(phrases),
            "uses_taught_macro": "YES" if hits else "NO",
            "macro_ids": ",".join(x[0] for x in hits) if hits else "NONE",
        })
        event_out.append(row)
        by_event[r["event_id"]] = row

    clause_out = []
    clause_events = defaultdict(list)
    for r in event_out:
        clause_events[r["event_id"]]  # reserve stable access
    event_index = {r["event_id"]: i for i, r in enumerate(event_out)}
    for c in clauses:
        lo, hi = event_index[c["start_event"]], event_index[c["end_event"]]
        rs = event_out[lo:hi + 1]
        assert len(rs) == int(c["events"])
        ids = [m for r in rs for m in r["macro_ids"].split(",") if m and m != "NONE"]
        row = dict(c)
        row.update({
            "macro_event_count": str(sum(r["uses_taught_macro"] == "YES" for r in rs)),
            "macro_ids_used": ",".join(dict.fromkeys(ids)),
            "compact_workshop_reading_de": " · ".join(r["workshop_phrase_de"] for r in rs),
        })
        clause_out.append(row)

    macro_rows = []
    for mid, pattern, phrase, function in MACROS:
        n = macro_use[mid]
        macro_rows.append({
            "macro_id": mid,
            "component_pattern": "+".join(pattern),
            "atomic_length": str(len(pattern)),
            "workshop_phrase_de": phrase,
            "teaching_function": function,
            "uses_in_2010_prose_events": str(n),
            "keep_rule": "KEEP" if n >= 5 else "KEEP_TENTATIVE",
        })

    write_tsv(OUT / "PASS916_PHRASEBOOK.tsv", macro_rows, list(macro_rows[0]))
    write_tsv(OUT / "PASS916_2010_EVENT_PHRASES.tsv", event_out, list(event_out[0]))
    write_tsv(OUT / "PASS916_354_COMPACT_CLAUSES.tsv", clause_out, list(clause_out[0]))

    md = ["# Pass 916 — kompaktes Werkstattphrasenbuch", ""]
    for page in dict.fromkeys(c["physical_page"] for c in clause_out):
        md += [f"## {page}", ""]
        for c in clause_out:
            if c["physical_page"] != page:
                continue
            carry = "zeilenübergreifend" if c["crosses_physical_line"] == "YES" else "lokal"
            md.append(f"- **{c['clause_id']}** ({carry}): {c['compact_workshop_reading_de']}")
        md.append("")
    (OUT / "PASS916_COMPACT_CLAUSE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    report = f"""# Pass 916 — Werkstattphrasen statt Wortsalat

## Ergebnis

Die {len(ATOMS)} Einzelkerne bleiben erhalten, werden aber durch **{len(MACROS)} kurze
Lehrphrasen** ergänzt. Sie fassen {covered_atoms}/{total_atoms} sichtbare
Komponenten in {macro_events}/2010 Prosagruppen zusammen. Das ist kein neues
Wörterbuch, sondern die kleine Redeschicht, die ein Lehrmeister tatsächlich
vormachen könnte.

Die produktivsten Muster sind:

- `OK+E/EE+DY`: kurz/länger ansetzen; fertig;
- `SH+E/EE+Y`: dies kurz/länger halten;
- `CHD+Y`: dies umsetzen;
- `L+CHD+DY`: abführen und umsetzen; fertig;
- `D_ADDR+AR`: aus diesem Teil entnehmen;
- `AIIN/AIN` unter `OK` oder `K`: nach Sollmaß/eine Portion ansetzen oder zuordnen.

## Schreibsystem

Ein Schreiber lernt zuerst die {len(ATOMS)} kurzen Kerne, dann die {len(MACROS)} häufigen
Phrasen als flüssige Ganzbewegungen. Seltene Kombinationen bleiben vollständig
lesbar, weil der Builder sie wieder in dieselben Kerne zerlegt. So verbindet die
Arbeitstheorie Fachkürzel mit eingelernten Ganzformen, ohne für jede Karte eine
eigene lange Bedeutung zu erfinden.

## Nächster Schritt

Die Phrasen werden nun zu einer vollständigen flüssigen Prosafassung verdichtet.
Dabei werden redundante `dies`, `weiter`, `prüfen` und erneute Besitzeraufrufe nur
dann ausgesprochen, wenn sie einen Postenwechsel anzeigen.
"""
    (OUT / "PASS916_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "BUILT",
        "prose_events": len(event_out),
        "clauses": len(clause_out),
        "atoms": len(ATOMS),
        "macros": len(MACROS),
        "events_using_macro": macro_events,
        "component_atoms_total": total_atoms,
        "component_atoms_in_macros": covered_atoms,
        "macro_uses": sum(macro_use.values()),
    }
    outputs = [
        "PASS916_PHRASEBOOK.tsv", "PASS916_2010_EVENT_PHRASES.tsv",
        "PASS916_354_COMPACT_CLAUSES.tsv", "PASS916_COMPACT_CLAUSE_EDITION.md",
        "PASS916_REPORT.md",
    ]
    summary["sha256"] = {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest() for n in outputs}
    (OUT / "PASS916_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
