#!/usr/bin/env python3
"""Publish the four bounded V31 visual/herbal identity bets."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
V30 = OUT.parent / "sidequest_theory_candidates_v30/V30_ELEVEN_RECORD_SOURCE_RECONSTRUCTIONS.tsv"

CANDIDATES = [
    {
        "page": "f10r", "selected_identity": "Teufelsabbiss oder Feld-Skabiose (Succisa/Scabiosa-Knautia complex)",
        "confidence": "0.58", "visual_basis": "blauer köpfchenförmiger Blütenstand; gezähnte Gegenblätter; auffällig paarig-verkürzte Wurzel",
        "recipe_basis": "Wurzel und Kraut in Wein; bittere/digestive und äußerliche Verwendung sind historisch plausibel",
        "strongest_rival": "eine andere kardendistelartige Wiesenpflanze oder komposite Lehrbildpflanze",
        "named_article": "Die abgebildete Skabiose wächst auf feuchtem Wiesengrund. Wasche ihre untere Wurzel in fließendem Wasser, zerstoße sie gleichmäßig, gib Rotwein hinzu und trinke die übliche Portion gegen Magenschmerz. Verwende den frischen Ansatz warm; sammle vor der Blüte eine Handvoll. Koche nach Öffnung der Blüte weiter, bis Bitterkeit bleibt, und bewahre den Rest unter Öl.",
    },
    {
        "page": "f11r", "selected_identity": "Veilchenbestand (Viola, wahrscheinlich Duft-/weißes Veilchen als Werkstattkategorie)",
        "confidence": "0.49", "visual_basis": "dichter bodennaher Bestand aus rundlich-gekerbten Blättern und vielen blauen Blüten",
        "recipe_basis": "Veilchenwurzel, -saft und Pflaster gegen Wunden beziehungsweise Schwellungen sind in spätmittelalterlicher Überlieferung belegt",
        "strongest_rival": "Gundermann oder eine stilisierte mehrstämmige Sammelpflanze",
        "named_article": "Sammle im Frühjahr vor der vollen Blüte die Wurzel des Veilchens vom schattigen Waldort. Quetsche und presse sie durch ein Tuch, kläre den Saft zweimal und lasse ihn offen abkühlen. Bewahre die Blüten zurück. Binde die übliche Portion auf die geschwollene Stelle und lege einen warmen Umschlag aus den Blättern auf.",
    },
    {
        "page": "f55v", "selected_identity": "Bärlauch oder breitblättrige Allium-Art (Allium ursinum complex)",
        "confidence": "0.43", "visual_basis": "sehr breite grundständige Blätter und hoher Schaft mit vielteiliger Dolde",
        "recipe_basis": "Allium-Arten waren mittelalterliche Arzneipflanzen; Bärlauch ist archäobotanisch belegt und äußerliche Wundverwendung ist plausibel",
        "strongest_rival": "breitblättriger Wegerich oder bildlich zusammengezogene Kohl-/Blattpflanze",
        "named_article": "Nimm vom breiten Blatt des Bärlauchs die übliche Menge, koche sie sanft in Weißwein und lasse den Auszug klar werden. Rühre eine zweite Portion gleichmäßig und wasche die wunde Stelle einmal. Für den zweiten Gebrauch gib erneut Weißwein hinzu; mische zuletzt beide Teile, bewahre sie bedeckt und verwende den fertigen Auszug frisch.",
    },
    {
        "page": "f56r", "selected_identity": "Sonnentau, wahrscheinlich Drosera intermedia/rotundifolia als Werkstattkategorie",
        "confidence": "0.72", "visual_basis": "eingerolltes Blatt; strahlenförmige Fangblätter; dunkle klebrige Köpfe; lange Blütenstiele",
        "recipe_basis": "nasser Heide-/Moorstandort passt; herba solis ist seit dem 12. Jahrhundert medizinisch belegt, auch in Wein und äußerlich",
        "strongest_rival": "Borretschgewächs mit überzeichneten Blütenständen",
        "named_article": "Sammle den Sonnentau im Frühjahr auf feuchter schattiger Heide. Lege den bezeichneten Anteil vor der Blüte in Weißwein und trage ihn an der gezeigten Stelle auf; lasse das Pflaster offen trocknen. Trockne weitere Pflanzenteile im Schatten, gebrauche den frischen Ansatz gegen Magenschmerz, mische einen Anteil mit Honig und nimm zuletzt die bezeichnete Menge der offenen Blüte.",
    },
]

SOURCES = [
    ("Yale MS 408 manifest", "https://collections.library.yale.edu/manifests/2002046", "official page images, inspected without storing them in the repository"),
    ("Early tentative identifications", "https://www.voynich.nu/extra/herb_oldid.html", "f10r Scabiosa; f56r Boraginaceae/Borago rivals"),
    ("College of Physicians violet note", "https://histmed.collegeofphysicians.org/medieval-monday-13/", "15th-century violet plaster, swelling, root and wound uses"),
    ("Ramsons review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4352197/", "medieval occurrence and external wound-healing tradition"),
    ("Kew sundew profile", "https://www.kew.org/plants/round-leafed-sundew", "wetland form and European medicinal tradition"),
    ("New Forest sundew", "https://www.newforestnpa.gov.uk/discover/plants-fungi/heathland-plants/sundew/", "wet heath, wine distillation, strengthening and respiratory uses"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with V30.open() as f:
        base = {(r["page"], r["record"]): r for r in csv.DictReader(f, delimiter="\t")}
    assert all((c["page"], "1" if c["page"] != "f10r" else "1") in base for c in CANDIDATES)

    result = OUT / "V31_FOUR_PLANT_IDENTIFICATIONS.tsv"
    with result.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(CANDIDATES[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(CANDIDATES)

    report = [
        "# V31 — named Herbal working translation", "",
        "Status: **creative plant identification pass, not botanical proof or decipherment**.", "",
        "The four official Yale folio images were inspected as complete pages. Candidate names were",
        "then compared with the already fixed V30 article readings and historically documented uses.",
        "No text identity or substring selected a plant.", "",
    ]
    for c in CANDIDATES:
        report += [
            f"## {c['page']} — {c['selected_identity']}", "",
            f"Working confidence: `{c['confidence']}`", "",
            f"> {c['named_article']}", "",
            f"Visual fit: {c['visual_basis']}.", "",
            f"Recipe fit: {c['recipe_basis']}.", "",
            f"Strongest rival: {c['strongest_rival']}.", "",
        ]
    report += ["## Sources used", ""] + [f"- [{n}]({u}) — {note}." for n, u, note in SOURCES]
    report += [
        "", "## Selection", "",
        "The identities are retained as concrete defaults until contradicted or outcompeted.",
        "`f56r = SUNDEW` is the strongest because morphology, wet habitat and medical tradition converge.",
        "The other three remain useful but replaceable article owners. None licenses a sound value,",
        "plant-name token, etymology, language, or claim about pages outside the fixed ten-page panel.", "",
    ]
    (OUT / "V31_NAMED_HERBAL_TRANSLATION.md").write_text("\n".join(report))

    selection = """# V31 theory selection

Date: 2026-08-22

Status: **four concrete Herbal owners selected provisionally**.

The V30 articles now receive explicit owners: f10r Skabiose/Teufelsabbiss,
f11r Veilchen, f55v Bärlauch/Allium and f56r Sonnentau. The winner is f56r
Sonnentau; its spiral and radiating trap leaves, wet-heath ecology, wine/honey
preparation and medieval medicinal status jointly improve the prior unnamed
article. The other three are lower-confidence workshop defaults.

These are picture-first hypotheses. No Voynich string was interpreted as a
plant name, and no plant candidate changes the card grammar. f84 and f84r
remained sealed.
"""
    (OUT / "V31_THEORY_SELECTION.md").write_text(selection)

    checks = {
        "four_pages": len(CANDIDATES) == 4 and len({c["page"] for c in CANDIDATES}) == 4,
        "all_named": all(c["selected_identity"].strip() for c in CANDIDATES),
        "all_articles_complete": all(len(c["named_article"].split()) >= 35 for c in CANDIDATES),
        "all_rivals_explicit": all(c["strongest_rival"].strip() for c in CANDIDATES),
        "f84_sealed": all(not c["page"].startswith("f84") for c in CANDIDATES),
    }
    val = {
        "schema": "SIDEQUEST_V31_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "input": {str(V30.relative_to(ROOT)): digest(V30)},
        "outputs": {result.name: digest(result), "V31_NAMED_HERBAL_TRANSLATION.md": digest(OUT / "V31_NAMED_HERBAL_TRANSLATION.md")},
    }
    (OUT / "V31_VALIDATION.json").write_text(json.dumps(val, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": val["status"], "pages": 4, "winner": "f56r_SUNDEW"}))


if __name__ == "__main__":
    main()
