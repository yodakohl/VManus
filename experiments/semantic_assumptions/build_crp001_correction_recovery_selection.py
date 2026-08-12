#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SOURCE = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
METHOD = BASE / "CRP001_CORRECTION_RECOVERY_PANEL_METHOD.md"
OUT = BASE / "results/crp001_correction_recovery_selection.json"
REPORT = BASE / "results/crp001_correction_recovery_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
PRIOR = {"f81v.19": "PIP001"}
EXPECTED = ["f18r.3", "f19r.2", "f26v.5"]

def sha_bytes(x: bytes) -> str: return hashlib.sha256(x).hexdigest()
def sha(path: Path) -> str: return sha_bytes(path.read_bytes())

def scan(raw: str) -> list[dict[str, str]]:
    comments: list[str] = []
    rows: list[dict[str, str]] = []
    for line in raw.splitlines():
        if line.startswith("#"):
            comments.append(line[1:].strip())
        elif line.startswith("<f"):
            m = re.match(r"<([^;>]+);", line)
            block = " ".join(comments)
            if m and re.search(r"correction", block, re.I) and re.search(r"darker ink|erasure", block, re.I):
                rows.append({"locus": m.group(1), "comment": block})
            comments = []
        elif line.strip() and not line.startswith("@@"):
            comments = []
    return rows

def main() -> None:
    if OUT.exists() or REPORT.exists(): raise SystemExit("refusing overwrite")
    all_hits = scan(SOURCE.read_text(encoding="latin-1"))
    if [x["locus"] for x in all_hits] != ["f18r.3", "f19r.2", "f26v.5", "f81v.19"]:
        raise SystemExit("complete source selection mismatch")
    selected = [x for x in all_hits if x["locus"] not in PRIOR]
    if [x["locus"] for x in selected] != EXPECTED: raise SystemExit("residual mismatch")
    req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-CRP001/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response: raw = response.read()
    if sha_bytes(raw) != MANIFEST_SHA: raise SystemExit("manifest mismatch")
    manifest = json.loads(raw)
    by_label = {c["label"]["none"][0]: c for c in manifest["items"]}
    targets=[]
    for hit in selected:
        page=hit["locus"].split(".")[0]; label=page[1:]; c=by_label[label]
        body=c["items"][0]["items"][0]["body"]
        targets.append({**hit,"page":page,"canvas_label":label,"canvas_id":c["id"].rsplit("/",1)[-1],
                        "official_dimensions":[body["width"],body["height"]],
                        "official_full_image_url":body["service"][0]["@id"]+"/full/full/0/default.jpg",
                        "target_image_opened":False})
    if [t["canvas_id"] for t in targets] != ["1006108","1006110","1006125"]: raise SystemExit("canvas mismatch")
    result={"experiment":"CRP001_CORRECTION_RECOVERY_SELECTION","schema":"CRP001_SELECTION_V1",
      "status":"FROZEN_COMPLETE_THREE_LOCUS_RESIDUAL_PANEL_BEFORE_TARGET_IMAGE_ACCESS",
      "decision":"AUTHORIZE_ONE_DIRECT_NATIVE_VISUAL_INSPECTION_PER_TARGET",
      "counts":{"literal_rule_hits":4,"prior_inspected_exclusions":1,"selected_loci":3,"physical_folios":3},
      "selection_rule":"comment block contains correction and either darker ink or erasure; exclude only named prior target inspections",
      "prior_exclusions":PRIOR,"targets":targets,
      "panel_pass_rule":"AT_LEAST_TWO_RECOVERABLE_TWO_STATE_CORRECTION_OUTCOMES_ON_AT_LEAST_TWO_FOLIOS",
      "gates":{"exact_complete_rule_hits":len(all_hits)==4,"only_named_prior_excluded":len(PRIOR)==1,
               "exact_residual_panel":[t["locus"] for t in targets]==EXPECTED,"three_physical_folios":len({t["page"] for t in targets})==3,
               "official_manifest_bindings":True,"target_image_bodies_unopened":all(not t["target_image_opened"] for t in targets),
               "outcomes_and_five_physical_gates_frozen":True},
      "inputs":{str(METHOD.relative_to(ROOT)):sha(METHOD),str(SOURCE.relative_to(ROOT)):sha(SOURCE),"yale_manifest_2002046_sha256":MANIFEST_SHA},
      "access":{"target_image_bodies_opened":False,"ocr_clip_embeddings_or_automated_recognition_used":False,"formal_identity_or_meaning_used":False},
      "claim_ceiling":"Selection authorizes only three source-bound physical-state inspections; it supplies no correction intent, glyph value, sound, word, language, cipher, plaintext, meaning, or translation."}
    if not all(result["gates"].values()): raise SystemExit("gate failure")
    OUT.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
    REPORT.write_text("# CRP001 correction-recovery selection\n\nStatus: **FROZEN_COMPLETE_THREE_LOCUS_RESIDUAL_PANEL_BEFORE_TARGET_IMAGE_ACCESS**.\n\nThe complete literal rule finds four comments; PIP001 already inspected f81v.19, leaving f18r.3, f19r.2, and f26v.5 on three folios. Official Yale canvases are bound from metadata and target image bodies remain unopened.\n\nThe panel passes only if at least two targets expose two independently traceable states with a physical chronology boundary. No glyph value or translation follows.\n")

if __name__ == "__main__": main()
