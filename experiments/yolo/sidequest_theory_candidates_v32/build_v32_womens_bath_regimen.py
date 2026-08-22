#!/usr/bin/env python3
"""Build V32's concrete three-page Biological regimen reconstruction."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
V30 = OUT.parent / "sidequest_theory_candidates_v30/V30_ELEVEN_RECORD_SOURCE_RECONSTRUCTIONS.tsv"

PAGES = [
    {
        "page": "f81v", "visual_stage": "COMMON_HERBAL_BATH_PREPARATION",
        "medical_stage": "gemeinsames temperiertes Kräuterbad zur Erwärmung und Öffnung des Körpers",
        "confidence": "0.66",
        "visual_reading": "zwei Reihen badender Frauen in einem gemeinsamen grünen Becken; links Zufluss, rechts Abfluss",
        "complete_page_reading": "Bereite die gemeinsame Kräutercharge, mische Öl und Flüssigkeit im unteren Becken und führe sie durch die verbundenen Läufe. Halte das Bad warm, rühre gleichmäßig, lasse den Ansatz stehen und kläre ihn durch Tuch. Die Frauen sitzen nacheinander oder nach Behandlungsklasse im gemeinsamen Bad; spüle die bezeichnete Stelle, lasse die Flüssigkeit absetzen und führe sie schließlich über die erste Öffnung zur lokalen Anwendung.",
        "strongest_rival": "allgemeine Mineralbad-/Kurortbeschreibung ohne besondere Frauenheilkunde",
    },
    {
        "page": "f82r", "visual_stage": "INDIVIDUAL_DOSE_FUMIGATION_AND_REST",
        "medical_stage": "individuelle Dosierung, Dampfanwendung, Teilbad und anschließende Ruhe",
        "confidence": "0.71",
        "visual_reading": "einzelne Frauen in kleinen Gefäßen und trichterartigen Sitzen; ein liegender Ruhezustand; unten großes Sammelbecken",
        "complete_page_reading": "Nach dem gemeinsamen Bad erhält jede Frau die bezeichnete temperierte Portion. Führe die Charge durch die zweite Öffnung, kläre sie im breiten Gefäß und gib Öl, klares oder warmes Wasser zu. Bade oder bedampfe den bezeichneten Körperbereich, lasse die Frau ruhen, ziehe die Flüssigkeit ab und leite sie in das untere Gefäß. Wiederhole Guss, lokale Auflage, Trank oder Bindung nach dem markierten Fall und schließe jeden einzelnen Schritt.",
        "strongest_rival": "schematische pharmazeutische Apparatur, deren Frauen nur abstrakte Prozesszustände markieren",
    },
    {
        "page": "f83r", "visual_stage": "LOCAL_IRRIGATION_GATE_AND_DRAINAGE",
        "medical_stage": "lokale warme/kalte Güsse oder Räucherung mit wiederholtem Abfluss und Zustandswechsel",
        "confidence": "0.74",
        "visual_reading": "Frauen empfangen oder geben Strahlen; farbige Bögen und Röhren verbinden Körper, Öffnungen und ein zentrales Mischorgan",
        "complete_page_reading": "Setze die Frau an das Becken. Gieße die vorbereitete warme Flüssigkeit über den bezeichneten Zugang, lasse sie einwirken und unten ablaufen. Öffne und schließe oberen und unteren Lauf der Reihe nach; rühre, temperiere, kläre und wiederhole Bad oder lokale Spülung für das angegebene Intervall. Wo der Fall es verlangt, kühle statt zu kochen, binde eine Auflage an oder verwende den geklärten Sud sofort. Beende die Kur mit Absetzen, Abzug und einer letzten Spülung der bezeichneten Stelle.",
        "strongest_rival": "humoral-kosmologische Flusskarte ohne wörtlich gebaute Leitungsapparatur",
    },
]

SOURCES = [
    ("Yale MS 408", "https://collections.library.yale.edu/manifests/2002046", "official f81v/f82r/f83r images"),
    ("Morgan De balneis Puteolanis G.74", "https://ica.themorgan.org/manuscript/page/2/77063", "c.1400 illustration of nude women in a therapeutic bath"),
    ("Trotula selections", "https://users.pfw.edu/flemingd/Green%20_TheTrotula_Selections.pdf", "herbal seawater bath, sweating, bed rest and subsequent fumigation"),
    ("Cambridge medieval gynaecology", "https://specialcollections-blog.lib.cam.ac.uk/?p=24362", "women's diseases as a distinct medieval practical field"),
    ("British Library Royal 18 A VI", "https://searcharchives.bl.uk/catalog/040-002107422", "15th-century medical, obstetrical and gynaecological compilation"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with V30.open() as f:
        bio = [r for r in csv.DictReader(f, delimiter="\t") if r["page"] in {"f81v", "f82r", "f83r"}]
    assert len(bio) == 6
    assert sum(int(r["field_count"]) for r in bio) == 115
    assert sum(int(r["event_count"]) for r in bio) == 281

    tsv = OUT / "V32_THREE_PAGE_MEDICAL_FUNCTION_MAP.tsv"
    with tsv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(PAGES[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(PAGES)

    report = [
        "# V32 — concrete women's bath regimen", "",
        "Status: **creative complete-purpose reconstruction, not deciphered medicine**.", "",
        "## Selected purpose", "",
        "The three Biological pages are read as one practical women's regimen for humoral",
        "warming, menstrual regulation or preparation for conception:", "",
        "```text",
        "f81v common medicated bath and base charge",
        "  → f82r individual dose, partial bath/fumigation and rest",
        "  → f83r local irrigation, alternating condition and drainage",
        "```", "",
        "This sequence is historically ordinary enough for c.1420: the Trotula tradition",
        "prescribes herbal baths until sweating, careful bed rest and subsequent aromatic",
        "fumigation. De balneis manuscripts independently depict groups of nude women in",
        "therapeutic pools. The Voynich drawings remain idiosyncratic and need not portray",
        "literal plumbing at engineering scale.", "",
    ]
    for p in PAGES:
        report += [
            f"## {p['page']} — {p['medical_stage']}", "",
            f"Working confidence: `{p['confidence']}`", "",
            f"Visual reading: {p['visual_reading']}.", "",
            f"> {p['complete_page_reading']}", "",
            f"Strongest rival: {p['strongest_rival']}.", "",
        ]
    report += [
        "## What the women represent", "",
        "The repeated nude figure is provisionally a **patient/state icon**, not a distinct named",
        "person. Repetition can encode separate treatment cases, body states, steps or positions.",
        "The manuscript therefore remains teachable: a scribe copies a standard patient figure,",
        "attaches it to the correct vessel/flow construction and fills the accompanying record.", "",
        "## Concrete disease bet", "",
        "The best single bet is a cold/obstructed women's condition—irregular or retained menses,",
        "pain/swelling, or preparation for conception—treated by warming bath, sweating, fumigation",
        "and local rinse. `FERTILITY_REGIMEN` is narrower and less secure than the broader",
        "`WOMENS_HUMORAL_BATH_REGIMEN`; pregnancy or anatomy is not directly drawn.", "",
        "## Sources", "",
    ] + [f"- [{name}]({url}) — {note}." for name, url, note in SOURCES]
    report += [
        "", "## Limits", "",
        "The pictures were drawn before the text and may determine only page-level ownership and",
        "available space. No line is assigned to the nearest figure. No visible group is translated",
        "as WOMAN, WOMB, MENSES or FERTILITY. The strongest live rivals are a general spa regimen,",
        "an abstract pharmaceutical process diagram and a humoral/cosmological flow model.", "",
    ]
    (OUT / "V32_COMPLETE_BIOLOGICAL_READING.md").write_text("\n".join(report))

    selection = """# V32 theory selection

Date: 2026-08-22

Status: **women's humoral bath regimen selected provisionally**.

The 281 Biological events and 115 fields retain their V30 meanings. V32 adds a
single concrete page-level purpose: f81v prepares a common medicated bath, f82r
individualizes partial bath/fumigation and rest, and f83r performs local
irrigation with controlled warming, openings and drainage. A menstrual or
fertility indication is the best narrow bet; the broader women's humoral bath
regimen is the selected owner.

The repeated women are patient/state icons, not decoded persons. No string is
assigned a gynaecological gloss. General spa, abstract process and humoral-flow
rivals remain live. f84 and f84r remained sealed.
"""
    (OUT / "V32_THEORY_SELECTION.md").write_text(selection)

    checks = {
        "three_pages": len(PAGES) == 3,
        "six_records": len(bio) == 6,
        "fields_115": sum(int(r["field_count"]) for r in bio) == 115,
        "events_281": sum(int(r["event_count"]) for r in bio) == 281,
        "all_pages_complete": all(len(p["complete_page_reading"].split()) >= 50 for p in PAGES),
        "all_rivals_explicit": all(p["strongest_rival"] for p in PAGES),
        "f84_sealed": all(not p["page"].startswith("f84") for p in PAGES),
    }
    val = {
        "schema": "SIDEQUEST_V32_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "input": {str(V30.relative_to(ROOT)): digest(V30)},
        "outputs": {tsv.name: digest(tsv), "V32_COMPLETE_BIOLOGICAL_READING.md": digest(OUT / "V32_COMPLETE_BIOLOGICAL_READING.md")},
    }
    (OUT / "V32_VALIDATION.json").write_text(json.dumps(val, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": val["status"], "records": 6, "fields": 115, "events": 281}))


if __name__ == "__main__":
    main()
