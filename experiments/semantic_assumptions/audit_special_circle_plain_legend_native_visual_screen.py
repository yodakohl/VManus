#!/usr/bin/env python3
"""Record the bounded f67--f73 source-bound plain-legend screen."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue"
PAGES = BASE / "results/existing_human_page_annotations.tsv"
OUT = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
REPORT = BASE / "results/special_circle_plain_legend_native_visual_screen_report.md"

SOURCE_SHA = {
    "cache/public_voynich_nu_catalogue/q09.html": "56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
    "cache/public_voynich_nu_catalogue/q10.html": "2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5",
    "cache/public_voynich_nu_catalogue/q11.html": "5553f82d3c7d016c3a9f7853388e844764239f929cdd24f2870a1d56b172ad64",
    "cache/public_voynich_nu_catalogue/q12.html": "3a9b4e587c9b9d0228bf87eea1b3a0e34f3fcfe4abafd71e712213e0af9132b6",
    "results/existing_human_page_annotations.tsv": "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
}

CANVAS_PANELS = {
    "1006194": ["f67r1", "f67r2"],
    "1006195": ["f67v2", "f67v1"],
    "1006196": ["f68r1", "f68r2", "f68r3"],
    "1006197": ["f68v3", "f68v2", "f68v1"],
    "1006198": ["f69r"],
    "1006199": ["f69v", "f70r1", "f70r2"],
    "1006200": ["f70v2"],
    "1006201": ["f70v1"],
    "1006202": ["f71r"],
    "1006203": ["f71v", "f72r1", "f72r2", "f72r3"],
    "1006204": ["f72v3", "f72v2"],
    "1006205": ["f72v1"],
    "1006206": ["f73r"],
    "1006207": ["f73v"],
}

IMAGE_SHA = {
    "1006194": "a951ffd4d75d18221bde824b636942eb605e33fe7d0329ba6421a18d3a94baf1",
    "1006195": "05e0d37d113a6153dd96a6566b8c2cdd0cfe5830d5b0bb153a2112b35d656c44",
    "1006196": "8a0289c49ea17de906cdbcfa1d1b296c8283f7ffe8383498957c6ebcf9c7fb69",
    "1006197": "419629545c1bdc91c8d76627970887ee68af78825e806ca8ca0c580107da3000",
    "1006198": "7a691f2a1a15464e4752b5c2478a250ab947aebf351e052aac1205bc405c7ec6",
    "1006199": "99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf",
    "1006200": "e2d0a497566f0b441222683bcbc8a29414ed0c821fed6c0449e346b711e3aacf",
    "1006201": "999afda3a21436f47dbdda61f9ee6bae2e269ba4bea5a7d78731622aa71a994f",
    "1006202": "8d2d0cc9f668b310eeede30d909639ea39d82eff14dbab3161c1260ff4693d73",
    "1006203": "ec67ec58715c7aa411db0b727c990928deebbd51c95af1cea7630abecc25aedc",
    "1006204": "46c961644e15d06a76bc4f7a6d209963edb4875ba8d0a802e255d4733c4154f0",
    "1006205": "ec12adf6a3e857f724421bfe521ab89b7c655882a144919512c37dcf8c680a49",
    "1006206": "511f05fc0b35441e369b15a1871ed79b4ea6402ff52dda3f214020bbf1a521e1",
    "1006207": "92d8add69503e220cc88bdd2b89c043656f47c545c73b10cd807abfe28410c8d",
}

MONTHS = {
    "f70v2": "March", "f70v1": "April", "f71r": "April",
    "f71v": "May", "f72r1": "May", "f72r2": "June",
    "f72r3": "July", "f72v3": "August", "f72v2": "September",
    "f72v1": "October", "f73r": "November", "f73v": "December",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def catalogue_mapping() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for name in ("q09", "q10", "q11", "q12"):
        current = None
        for line in (CATALOGUE / f"{name}.html").read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.search(r'<TH CLASS="Ph" ID="([^"]+)">', line, re.I)
            if match:
                current = match.group(1)
            match = re.search(r"child_oid=(1006\d+)", line)
            if match and current and match.group(1) in CANVAS_PANELS:
                found.setdefault(match.group(1), []).append(current)
    return found


def month_mapping() -> dict[str, str]:
    found: dict[str, str] = {}
    with PAGES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] not in MONTHS:
                continue
            text = " ".join(row.values())
            match = re.search(r"month name ([A-Z][A-Za-z]+) is written in the centre in a different hand", text)
            if match:
                found[row["page"]] = match.group(1)
    return found


def report_text(result: dict) -> str:
    return (
        "# Special-circle plain-legend native-visual screen\n\n"
        f"Status: **{result['status']}**\n\n"
        "Fourteen official Yale canvases cover all 26 f67--f73 panels. Direct source-bound inspection finds "
        "no new clearly readable multi-character plain-alphabet or numeral register in the main diagram hand. "
        "The public human catalogue identifies twelve readable zodiac month names, but explicitly assigns them "
        "to a different hand. They label whole pages and do not equate any Voynich group with March--December.\n\n"
        "The sole main-diagram near-miss is the already-audited f68r2 lower-face ending, whose script and reading "
        "remain unresolved. Folio and quire numbers and isolated Latin-shaped marks are navigation or unparsed "
        "marks, not readable paired legends. No Voynich surface was transcribed and no association was scored.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for rel, expected in SOURCE_SHA.items():
        if sha(BASE / rel) != expected:
            raise SystemExit(f"source hash mismatch: {rel}")
    mapping = catalogue_mapping()
    if mapping != CANVAS_PANELS:
        raise SystemExit("canvas/panel mapping mismatch")
    months = month_mapping()
    if months != MONTHS:
        raise SystemExit("different-hand month mapping mismatch")
    status = "STOP_NATIVE_VISUAL_NO_NEW_MAIN_HAND_READABLE_REGISTER"
    result = {
        "experiment": "SPECIAL_CIRCLE_PLAIN_LEGEND_NATIVE_VISUAL_SCREEN",
        "status": status,
        "decision": status,
        "inputs": {
            **SOURCE_SHA,
            **{f"yale_iiif_2000px_canvas_{key}_sha256": value for key, value in IMAGE_SHA.items()},
        },
        "canvas_panels": CANVAS_PANELS,
        "different_hand_month_names": MONTHS,
        "counts": {
            "official_canvases_inspected": len(CANVAS_PANELS),
            "physical_panels_covered": sum(map(len, CANVAS_PANELS.values())),
            "different_hand_readable_month_names": len(MONTHS),
            "new_main_hand_readable_multicharacter_legends": 0,
            "unresolved_preexisting_main_diagram_near_misses": 1,
            "author_visible_plain_voynich_equivalences": 0,
            "voynich_surfaces_transcribed_or_loaded": 0,
            "formal_features_constructed": 0,
            "associations_scored": 0,
        },
        "native_visual_observation": (
            "The official f67--f73 canvases show no new clearly readable multi-character plain-alphabet or numeral "
            "register in the main diagram hand. Readable zodiac month strings are later/different-hand page labels; "
            "the f68r2 ending remains unresolved and no plain/Voynich equivalence device is visible."
        ),
        "gates": {
            "complete_f67_through_f73_canvas_coverage": True,
            "different_hand_month_names_excluded_from_main_hand_anchor": True,
            "preexisting_f68r2_unresolved_sequence_not_reclassified": True,
            "new_main_hand_readable_multicharacter_legend_present": False,
            "author_visible_plain_voynich_equivalence_present": False,
            "zero_voynich_transcription_feature_or_score_access": True,
        },
        "claim_ceiling": (
            "This bounded visual stop establishes no letter value, numeral, month word, zodiac sign name, sound, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_text(result), encoding="utf-8")


if __name__ == "__main__":
    main()
