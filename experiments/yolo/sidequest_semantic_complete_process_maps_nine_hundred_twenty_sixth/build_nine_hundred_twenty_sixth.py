#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth"


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


VERB_DE = {
    "P": "einsetzen", "OK": "ansetzen", "CH": "entnehmen", "K": "zugeben",
    "O": "ausführen", "T": "einstellen", "S": "auswählen", "CTH": "bereitstellen",
    "R": "kennzeichnen", "CHK": "behandeln", "CHD": "umsetzen", "SH": "halten",
    "SHED": "absetzen", "CFH": "trennen", "LSH": "spülen", "CPH": "umleiten",
    "SOLK": "auffangen",
}
PHASE = {
    "CH": "SELECT", "S": "SELECT",
    "P": "PREPARE", "OK": "PREPARE", "K": "PREPARE",
    "O": "EXECUTE", "T": "EXECUTE",
    "SH": "CONDITION", "SHED": "CONDITION", "CHK": "CONDITION", "CTH": "CONDITION", "R": "CONDITION",
    "CHD": "TRANSFER", "CFH": "TRANSFER", "LSH": "TRANSFER", "CPH": "TRANSFER", "SOLK": "TRANSFER",
}
OWNER = {
    "HERBAL": "Beim gezeigten Pflanzenmaterial",
    "BIOLOGICAL": "An der gezeigten Bad- oder Arbeitsstation",
    "PHARMA": "Beim bezeichneten Zutaten- oder Vorratsposten",
    "ZODIAC": "Beim bezeichneten Ring- oder Tabellenposten",
}
PHASE_DE = {
    "SELECT": "AUSWÄHLEN/ENTNEHMEN",
    "PREPARE": "EINSETZEN/ANSETZEN/ZUGEBEN",
    "EXECUTE": "AUSFÜHREN/EINSTELLEN",
    "CONDITION": "HALTEN/BEHANDELN/PRÜFEN",
    "TRANSFER": "UMSETZEN/SPÜLEN/TRENNEN/AUFFANGEN",
    "CONTEXT": "BEZUG/MENGE/STELLE",
}


def phase_for(row):
    verbs = [v for v in row["minimal_verb_sequence"].split(">") if v]
    phases = [PHASE[v] for v in verbs if v in PHASE]
    if not phases:
        return "CONTEXT"
    counts = Counter(phases)
    return max(counts, key=lambda p: (counts[p], -phases.index(p)))


def rle(values):
    out = []
    for v in values:
        if out and out[-1][0] == v:
            out[-1][1] += 1
        else:
            out.append([v, 1])
    return out


def component_flags(text):
    comps = [c.strip() for bit in text.split(" | ") for c in bit.split("+") if c.strip()]
    return set(comps)


def render_counts(counts, limit=6):
    parts = []
    for verb, n in counts.most_common(limit):
        parts.append(f"{n}× {VERB_DE[verb]}")
    return ", ".join(parts)


clauses = read_tsv(BASE / "PASS924_354_CURRENT_CLAUSES.tsv")
instructions = read_tsv(BASE / "PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv")
by_clause = defaultdict(list)
for row in instructions:
    by_clause[row["clause_id"]].append(row)

assignments = []
maps = []
page_maps = defaultdict(list)

for clause in clauses:
    rows = by_clause[clause["clause_id"]]
    verb_counts = Counter()
    phases = []
    flags = set()
    for order, row in enumerate(rows, 1):
        verbs = [v for v in row["minimal_verb_sequence"].split(">") if v]
        verb_counts.update(v for v in verbs if v in VERB_DE)
        phase = phase_for(row)
        phases.append(phase)
        flags |= component_flags(row["component_sequence"])
        assignments.append({
            "instruction_id": row["instruction_id"],
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "register": clause["register"],
            "instruction_order": order,
            "phase": phase,
            "start_event": row["start_event"],
            "end_event": row["end_event"],
            "event_count": row["event_count"],
            "minimal_verb_sequence": row["minimal_verb_sequence"] or "NONE",
            "current_fluent_de": row["current_fluent_de"],
        })
    runs = rle(phases)
    run_text = ">".join(f"{p}x{n}" for p, n in runs)
    source_bits = []
    if "AR" in flags or "D_ADDR" in flags: source_bits.append("Entnahmestelle oder bezeichnetes Teil")
    if "OR" in flags: source_bits.append("Ansatz")
    if "CHEO" in flags: source_bits.append("Auszug")
    if "AIIN" in flags: source_bits.append("Sollmaß")
    if "AIN" in flags: source_bits.append("Portion")
    target_bits = []
    if "AL" in flags: target_bits.append("Ziel- oder Anschlussstelle")
    if "L" in flags: target_bits.append("weiterer Lauf")
    if "CKH" in flags: target_bits.append("Durchlass")
    grade_bits = []
    if "E" in flags: grade_bits.append("kurz")
    if "EE" in flags: grade_bits.append("länger")
    if "EEE" in flags: grade_bits.append("vollständig")
    owner = OWNER.get(clause["register"], "Beim bezeichneten Posten")
    sentences = [
        f"{owner} stehen {len(rows)} Arbeitszüge in einer zusammenhängenden Klausel.",
        f"Die wiederkehrenden Handlungen sind {render_counts(verb_counts) or 'nur Bezug und Weiterführung'}.",
    ]
    if source_bits:
        sentences.append("Als Einsatzgrößen erscheinen " + ", ".join(source_bits) + ".")
    if target_bits:
        sentences.append("Der Gang führt über " + ", ".join(target_bits) + ".")
    if grade_bits:
        sentences.append("Die notierten Wirkstufen sind " + ", ".join(grade_bits) + ".")
    if clause["end_reason"] == "LICENSED_DY_CLOSE":
        sentences.append("Danach wird der Arbeitsschritt geschlossen.")
    else:
        sentences.append("Der Arbeitsgang bleibt für die folgende Klausel oder Seite offen.")
    natural = " ".join(sentences)
    row = {
        "clause_id": clause["clause_id"],
        "physical_page": clause["physical_page"],
        "register": clause["register"],
        "start_event": clause["start_event"],
        "end_event": clause["end_event"],
        "events": clause["events"],
        "instructions": len(rows),
        "crosses_physical_line": clause["crosses_physical_line"],
        "end_reason": clause["end_reason"],
        "phase_run_sequence": run_text,
        "phase_runs": len(runs),
        "verb_counts": ";".join(f"{v}:{n}" for v, n in verb_counts.most_common()) or "NONE",
        "source_quantity_inventory": ";".join(source_bits) or "NONE",
        "target_path_inventory": ";".join(target_bits) or "NONE",
        "grade_inventory": ";".join(grade_bits) or "NONE",
        "natural_process_summary_de": natural,
    }
    maps.append(row)
    page_maps[clause["physical_page"]].append(row)

write_tsv(HERE / "PASS926_1435_PHASE_ASSIGNMENTS.tsv", list(assignments[0]), assignments)
write_tsv(HERE / "PASS926_354_PROCESS_MAPS.tsv", list(maps[0]), maps)

doc = [
    "# Pass 926 — vollständige Prozesskarte der Prosaseiten", "",
    "Jede Klausel erhält einen kurzen lesbaren Werkstattabsatz. Die genaue Kartenfolge bleibt in Pass 924; hier wird sie als Handlungs-, Einsatz-, Weg- und Gradprofil gesprochen.", "",
]
for page, rows in page_maps.items():
    doc += [f"## {page}", ""]
    for row in rows:
        doc += [f"### {row['clause_id']}", "", row["natural_process_summary_de"], "", f"Phasenfolge: `{row['phase_run_sequence']}`", ""]
(HERE / "PASS926_COMPLETE_PROSE_PROCESS_EDITION.md").write_text("\n".join(doc).rstrip()+"\n", encoding="utf-8")

phase_counts = Counter(r["phase"] for r in assignments)
report = f"""# Pass 926 — alle 354 Klauseln als Prozesskarten

## Ergebnis

Alle 1.435 gesprochenen Arbeitszüge und alle 354 Klauseln der zwölf Prosaseiten
sind nun in einer einheitlichen Prozesskarte lesbar. Die Redaktion trennt fünf
praktische Schubladen: Auswahl, Vorbereitung, Ausführung, Zustand und Transfer.
Bezugskarten ohne eigenes Tätigkeitswort bleiben als Kontext erhalten.

Die Verteilung lautet: Auswahl {phase_counts['SELECT']}, Vorbereitung
{phase_counts['PREPARE']}, Ausführung {phase_counts['EXECUTE']}, Zustand
{phase_counts['CONDITION']}, Transfer {phase_counts['TRANSFER']} und Kontext
{phase_counts['CONTEXT']}.

## Neue Lesewirkung

Die sehr langen Klauseln sind keine einzelnen überlangen Sätze. Sie sind
Werkprotokolle mit vielen kurzen Zügen unter demselben Bildbesitzer. Die
wiederholten Karten sprechen daher nicht jedes Mal einen neuen Gegenstand an;
sie halten denselben Arbeitsgegenstand aktiv und ändern Handlung, Weg, Grad oder
Abschluss.

## Nächster Schritt

Die wiederkehrenden Phasenübergänge werden jetzt zu einer kleinen Zahl
konkreter Rezept- und Stationsschablonen zusammengezogen. So wird sichtbar,
welche längeren Abläufe wirklich mehrfach auf verschiedenen Seiten vorkommen.
"""
(HERE / "PASS926_REPORT.md").write_text(report, encoding="utf-8")

outputs = [
    "PASS926_1435_PHASE_ASSIGNMENTS.tsv", "PASS926_354_PROCESS_MAPS.tsv",
    "PASS926_COMPLETE_PROSE_PROCESS_EDITION.md", "PASS926_REPORT.md",
]
summary = {
    "status": "PASS", "clauses": len(maps), "instructions": len(assignments),
    "pages": len(page_maps), "phase_counts": dict(phase_counts),
    "outputs": {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in outputs},
}
(HERE / "PASS926_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
