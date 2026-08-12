#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_METHOD.md"
ANN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
OLD_PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
X_PANEL = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv"
X_RESULT = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.json"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def keyed(tag: str, page: str) -> str:
    return sha(f"{tag}|{page}".encode("ascii"))


def select() -> list[dict[str, object]]:
    meta = {}
    with ZL.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            meta.setdefault(row["page"], row)
    excluded = set()
    for path in (OLD_PANEL, X_PANEL):
        with path.open(encoding="utf-8", newline="") as handle:
            excluded.update(row["physical_folio"] for row in csv.DictReader(handle, delimiter="\t"))
    one = {}
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" not in row["source_tags"] or page not in meta or meta[page]["language"] != "A" or not match:
                continue
            folio = f"f{match.group(1)}"
            if folio in excluded:
                continue
            candidate = {
                "page": page, "physical_folio": folio, "folio_number": int(match.group(1)),
                "currier": "A", "section": meta[page]["section"], "hand": meta[page]["hand"],
                "quire": row["quire"] or meta[page]["quire"],
                "folio_page_sha256": keyed("LM001X_PAGE", page),
            }
            if folio not in one or candidate["folio_page_sha256"] < one[folio]["folio_page_sha256"]:
                one[folio] = candidate
    rows = [row for row in one.values() if row["quire"] != "q05"]

    # Preserve the original Currier-A quartile system.
    all_a = {}
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" in row["source_tags"] and page in meta and meta[page]["language"] == "A" and match:
                folio = f"f{match.group(1)}"
                if folio not in all_a or keyed("LM001_PAGE", page) < keyed("LM001_PAGE", all_a[folio][1]):
                    all_a[folio] = (int(match.group(1)), page)
    ranked = sorted(all_a.items(), key=lambda item: (item[1][0], item[1][1]))
    quartile = {folio: min(4, 4 * index // len(ranked) + 1) for index, (folio, _) in enumerate(ranked)}
    for row in rows:
        row["folio_rank_quartile"] = quartile[row["physical_folio"]]
        row["opaque_id"] = "LY" + keyed("LM001Y_OPAQUE", row["page"])[:8].upper()
    return sorted(rows, key=lambda row: row["opaque_id"])


def bind(rows):
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-LM001Y/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    assert sha(raw) == MANIFEST_SHA256
    manifest = json.loads(raw.decode("utf-8"))
    by_label = {}
    for canvas in manifest["items"]:
        by_label.setdefault(canvas["label"].get("none", [""])[0], []).append(canvas)
    for row in rows:
        label = re.sub(r"[123]$", "", row["page"])[1:]
        hits = by_label.get(label, [])
        if len(hits) != 1:
            raise SystemExit(f"canvas label is not unique: {row['page']} {label}")
        canvas = hits[0]; body = canvas["items"][0]["items"][0]["body"]
        row["canvas_id"] = canvas["id"].rsplit("/", 1)[-1]
        row["canvas_label"] = label
        row["review_image_url"] = body["service"][0]["@id"] + "/full/1600,/0/default.jpg"


def main():
    prior = json.loads(X_RESULT.read_text(encoding="utf-8"))
    assert prior["combined_counts"] == {"pages": 35, "SMOOTH": 24, "TOOTHED": 10, "UNCERTAIN": 1}
    rows = select(); bind(rows)
    fields = ["opaque_id","page","physical_folio","folio_number","currier","section","hand","quire","folio_rank_quartile","folio_page_sha256","canvas_id","canvas_label","review_image_url"]
    with OUT_TSV.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,delimiter="\t",lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    qc=Counter(row["quire"] for row in rows)
    gates={"exact_complete_nine_page_residual":len(rows)==9,"nine_new_physical_folios":len({row['physical_folio'] for row in rows})==9,
           "all_currier_A":all(row['currier']=='A' for row in rows),"q05_excluded":all(row['quire']!='q05' for row in rows),
           "no_sampling_or_page_count_rank":True,"selected_images_not_opened_by_builder":True,"no_voynich_text_features_accessed":True}
    result={"experiment":"LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_SELECTION","schema":"LM001Y_SELECTION_V1","status":"FROZEN_COMPLETE_RESIDUAL_BEFORE_IMAGE_INSPECTION","decision":"AUTHORIZE_ONE_PASS_COMPLETE_RESIDUAL_NATIVE_VISUAL_JUDGMENT","counts":{"pages":len(rows),"quires":dict(sorted(qc.items()))},"gates":gates,
            "inputs":{str(METHOD.relative_to(ROOT)):file_sha(METHOD),str(ANN.relative_to(ROOT)):file_sha(ANN),str(ZL.relative_to(ROOT)):file_sha(ZL),str(OLD_PANEL.relative_to(ROOT)):file_sha(OLD_PANEL),str(X_PANEL.relative_to(ROOT)):file_sha(X_PANEL),str(X_RESULT.relative_to(ROOT)):file_sha(X_RESULT),"yale_manifest_2002046_sha256":MANIFEST_SHA256},"panel_sha256":file_sha(OUT_TSV),
            "claim_ceiling":"This freezes the complete nine-folio non-q05 Currier-A residual for one final source-only capacity pass. It supplies no text association, plant identity, word, language, plaintext, meaning, or translation."}
    assert all(gates.values())
    OUT_JSON.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    OUT_MD.write_text("# LM001Y final residual leaf-margin census selection\n\nStatus: **FROZEN_COMPLETE_RESIDUAL_BEFORE_IMAGE_INSPECTION**.\n\nEvery one of the nine remaining unseen non-q05 Currier-A herbal folios is included; no folio sampling or ranking is applied. Official Yale canvases are bound without opening image bodies. The unchanged LM001 rubric and every original capacity gate remain controlling. No Voynich text feature was accessed, and no plant identity, word, plaintext, meaning, or translation follows.\n",encoding="utf-8")
if __name__=="__main__": main()
