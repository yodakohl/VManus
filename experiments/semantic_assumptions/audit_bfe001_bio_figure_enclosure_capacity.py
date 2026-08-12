#!/usr/bin/env python3
"""Filler-blind capacity audit for biological figure enclosure state."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS = HERE / "results"
METHOD = HERE / "BFE001_BIO_FIGURE_ENCLOSURE_CAPACITY_METHOD.md"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
OUT_JSON = RESULTS / "bfe001_bio_figure_enclosure_capacity.json"
OUT_REPORT = RESULTS / "bfe001_bio_figure_enclosure_capacity_report.md"

IMAGES = {
    "f77r": ("1006212", "9ad387ccea37cd8a25ce9602817eb19af5105c545a238203715efe454e5b24ad", 2793, 3752),
    "f77v": ("1006213", "e2e2f629753bfe6a9c111d8157ac63cfc4524966cbf367ddaaffece07cffdab2", 2861, 3697),
    "f80r": ("1006218", "81223a0b0aa0a24fe821cf62a9bdf4ac504f222ab3cfcb89fcedd7946bceada0", 2793, 3733),
    "f82r": ("1006222", "269cb42307824ab82764f80009429e58d98c649371d8efe10d2a1f54132a21ef", 2753, 3745),
    "f82v": ("1006223", "4c86853e2d6e62690ec0106dcc3812c95f009022b06e7edfd347386728003142", 2821, 3709),
    "f83r": ("1006224", "dc353557586906cbe4210f503cc57af58599a3948517fb45b1d222760be96729", 2753, 3745),
    "f83v": ("1006225", "dc4610b14efc89e3eded3b887b28b95f8c98a07adb4bed6d83a10e37daf0c7e9", 2858, 3693),
    "f84r": ("1006226", "7e8fa7c29b6c6ab462ad5359bdabfcd60505622700f6e5cb18478d20cbd79fbe", 2753, 3745),
}

PAGE_STATE = {
    "f77r": "INDIVIDUAL_BOUNDED", "f77v": "INDIVIDUAL_BOUNDED",
    "f80r": "OPEN_OR_COMMUNAL", "f82r": "OPEN_OR_COMMUNAL",
    "f83r": "INDIVIDUAL_BOUNDED", "f83v": "INDIVIDUAL_BOUNDED",
    "f84r": "OPEN_OR_COMMUNAL",
}
F82V_INDIVIDUAL = {"f82v.2", "f82v.39", "f82v.40"}
F82V_COMMUNAL = {"f82v.41", "f82v.46"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise AssertionError(page)
    return match.group(0)


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite BFE001 outputs")
    with CROSSWALK.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_physical = {}
    for row in rows:
        by_physical.setdefault(row["source_physical_location_id"], row)
    selected = sorted([
        row for row in by_physical.values()
        if row["primary_eligible"] == "1" and row["source_section"] == "bio"
        and row["source_object_guess"] == "nymph?"
        and row["source_page"] not in {"f75r", "f75v"}
    ], key=lambda row: row["source_record_id"])
    assert len(selected) == 40
    assert Counter(row["source_page"] for row in selected) == Counter({
        "f84r": 10, "f82r": 7, "f80r": 5, "f82v": 5,
        "f77r": 4, "f83v": 4, "f77v": 3, "f83r": 2,
    })
    observations = []
    for row in selected:
        page, locus = row["source_page"], row["current_locus"]
        if page == "f82v":
            state = ("INDIVIDUAL_BOUNDED" if locus in F82V_INDIVIDUAL
                     else "OPEN_OR_COMMUNAL" if locus in F82V_COMMUNAL
                     else None)
            if state is None:
                raise AssertionError((page, locus))
        else:
            state = PAGE_STATE[page]
        observations.append({"source_record_id": row["source_record_id"], "page": page,
                             "folio": folio(page), "current_locus": locus, "state": state})
    state_counts = Counter(row["state"] for row in observations)
    folios = sorted({row["folio"] for row in observations})
    pages = sorted({row["page"] for row in observations})
    folios_by_state = {state: sorted({row["folio"] for row in observations if row["state"] == state})
                       for state in sorted(state_counts)}
    mixed_folios = sorted({f for f in folios if len({row["state"] for row in observations if row["folio"] == f}) == 2})
    mixed_pages = sorted({p for p in pages if len({row["state"] for row in observations if row["page"] == p}) == 2})
    folio_counts = Counter(row["folio"] for row in observations)
    max_share = max(folio_counts.values()) / len(observations)
    gates = {
        "at_least_30_locations": len(observations) >= 30,
        "at_least_5_folios": len(folios) >= 5,
        "each_state_at_least_3_folios": min(map(len, folios_by_state.values())) >= 3,
        "at_least_3_mixed_folios": len(mixed_folios) >= 3,
        "at_least_3_mixed_pages": len(mixed_pages) >= 3,
        "max_folio_share_at_most_0_35": max_share <= .35,
    }
    passed = all(gates.values())
    result = {
        "experiment": "BFE001_BIO_FIGURE_ENCLOSURE_CAPACITY",
        "status": "GO_FILLER_BLIND_DESIGN_ONLY" if passed else "STOP_ONE_MIXED_FOLIO_PAGE_ECOLOGY_CONFOUND",
        "decision": "AUTHORIZE_FILLER_BLIND_DESIGN_ONLY" if passed else "DO_NOT_OPEN_FIGURE_LABEL_FILLERS_OR_FORMAL_FEATURES",
        "access": {"voynich_label_strings_accessed": False, "formal_features_accessed": False,
                   "ocr_or_automated_vision_used": False,
                   "machine_authored_source_bound_native_visual_inspection": True},
        "candidate_locations": len(observations), "pages": len(pages), "physical_folios": len(folios),
        "state_counts": dict(sorted(state_counts.items())), "folios_by_state": folios_by_state,
        "mixed_folios": mixed_folios, "mixed_pages": mixed_pages,
        "folio_counts": dict(sorted(folio_counts.items())), "maximum_folio_share": round(max_share, 6),
        "paired_mixed_folio_one_sided_p_floor": .5, "gates": gates, "observations": observations,
        "official_images": {page: {"canvas_id": v[0], "sha256": v[1], "width": v[2], "height": v[3],
                                   "image_url": f"https://collections.library.yale.edu/iiif/2/{v[0]}/full/full/0/default.jpg"}
                            for page, v in sorted(IMAGES.items())},
        "inputs": {str(METHOD.relative_to(ROOT)): sha(METHOD), str(CROSSWALK.relative_to(ROOT)): sha(CROSSWALK)},
        "claim_ceiling": "The existing panel has only one physical folio and one page containing both drawing states. The contrast is inseparable from page and folio ecology at this resolution; no figure owner, apparatus owner, bath, procedure, word, name, POS, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        f"# BFE001 biological-figure enclosure capacity\n\nDecision: **{result['status']}**.\n\n"
        f"A filler-blind selection from the existing human current-locus crosswalk retains **{len(observations)}** physical figure-associated candidates on **{len(pages)}** pages and **{len(folios)}** physical folios. Direct source-bound inspection of the eight exact Yale canvases classifies the physical setting only: {state_counts['INDIVIDUAL_BOUNDED']} candidate areas occupy individualized bounded apparatus zones and {state_counts['OPEN_OR_COMMUNAL']} occupy open or communal zones.\n\n"
        f"Nominal support is broad enough to be tempting: `INDIVIDUAL_BOUNDED` occurs on {', '.join(folios_by_state['INDIVIDUAL_BOUNDED'])}, while `OPEN_OR_COMMUNAL` occurs on {', '.join(folios_by_state['OPEN_OR_COMMUNAL'])}. But only **{', '.join(mixed_folios)}** contains both states, and only **{', '.join(mixed_pages)}** mixes them on one page. A paired physical-folio sign orbit therefore has only two assignments and a one-sided floor of **0.5**. Any filler or formal feature could mark page, folio, layout, or apparatus register instead of the drawing state.\n\n"
        f"Gates passed: **{sum(gates.values())}/{len(gates)}**. The label strings and formal features remained unopened. No OCR, automated image recognition, or embedding was used; the visual classifications are machine-authored source-bound observations.\n\n{result['claim_ceiling']}\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
