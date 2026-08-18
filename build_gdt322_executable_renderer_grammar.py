#!/usr/bin/env python3
"""Compile the validated GDT321 two-rule layer into an executable grammar."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt318_frozen_panel.tsv"
G321 = R / "gdt321_result.json"
VALIDATION = R / "gdt321_validation.json"
METHOD = R / "GDT322_EXECUTABLE_RENDERER_GRAMMAR.md"
LEXICON = R / "gdt322_opaque_cell_lexicon.tsv"
MODEL = R / "gdt322_renderer_model.json"
REPORT = R / "GDT322_EXECUTABLE_RENDERER_REPORT.md"
RESULT = R / "gdt322_result.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
def softmax(scores):
    shifted = scores - scores.max(axis=1, keepdims=True); values = np.exp(shifted); return values / values.sum(axis=1, keepdims=True)
def fit(offsets, truth, line, prev, s_index, q_index, ridge):
    beta = np.zeros(2)
    for _ in range(60):
        scores = offsets.copy(); scores[:, s_index] += beta[0] * line; scores[:, q_index] += beta[1] * prev; p = softmax(scores); ys = (truth == s_index); yq = (truth == q_index)
        gradient = np.array([np.sum((p[:, s_index] - ys) * line) + ridge * beta[0], np.sum((p[:, q_index] - yq) * prev) + ridge * beta[1]])
        hessian = np.array([[np.sum(p[:, s_index] * (1-p[:, s_index]) * line*line)+ridge, np.sum(-p[:, s_index]*p[:, q_index]*line*prev)], [np.sum(-p[:, s_index]*p[:, q_index]*line*prev), np.sum(p[:, q_index]*(1-p[:, q_index])*prev*prev)+ridge]])
        step = np.linalg.pinv(hessian) @ gradient; beta -= step
        if abs(step).max() < 1e-10: break
    return beta
def main():
    classes = ["NONE", "ch", "che", "d", "q", "s", "sh", "t"]; ci = {value:index for index,value in enumerate(classes)}; source = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]; assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source); source_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: row for row in source}; panel = read(PANEL); grouped = defaultdict(list)
    for row in panel: grouped[row["cell_id"]].append((row, source_map[row["event_id_sha256"]]))
    lexicon = []
    for cell, members in sorted(grouped.items()):
        counts = Counter(source_row["wrapper"] for _, source_row in members); lexicon.append({"cell_id":cell,"events":len(members),"folios":len({row["physical_folio"] for row,_ in members}),"wrapper_classes":"|".join(wrapper for wrapper in classes if counts[wrapper]),"wrapper_counts_json":json.dumps({wrapper:counts[wrapper] for wrapper in classes},sort_keys=True,separators=(",",":")),"line_start_events":sum(int(row["line_first"]) for row,_ in members),"prev_dy_events":sum(int(row["prev_dy"]) for row,_ in members),"license_state":"OBSERVED_COMPATIBILITY_CELL"})
    write(LEXICON, lexicon); cell_index = {row["cell_id"]:index for index,row in enumerate(lexicon)}; counts = np.full((len(lexicon),len(classes)),.5); truth=[]
    for row in panel:
        value=ci[source_map[row["event_id_sha256"]]["wrapper"]]; truth.append(value); counts[cell_index[row["cell_id"]],value]+=1
    offsets=np.array([np.log(counts[cell_index[row["cell_id"]]]) for row in panel]); truth=np.array(truth); line=np.array([float(row["line_first"]) for row in panel]); prev=np.array([float(row["prev_dy"]) for row in panel]); beta=fit(offsets,truth,line,prev,ci["s"],ci["q"],10.0); total_cells=len({(row["page_host"],row["local_frame"],row["inner_d"],row["right_family"],row["dy_closure"],row["b3"]) for row in source})
    model={"schema":"GDT322_EXECUTABLE_RENDERER_MODEL_V1","status":"EXECUTABLE_TWO_RULE_RENDERER","classes":classes,"formula":"SOFTMAX(LOG(N_CELL_WRAPPER_PLUS_HALF)+S_INDICATOR*BETA_S*LINE_FIRST+Q_INDICATOR*BETA_Q*PREV_DY)","alpha":.5,"ridge":10.0,"beta_s_line_first":float(beta[0]),"beta_q_prev_dy":float(beta[1]),"unseen_cell_policy":"UNLICENSED_OR_UNKNOWN_NO_GENERATED_WRAPPER","coverage":{"events":len(panel),"total_voynich_reference_events":len(source),"event_fraction":len(panel)/len(source),"cells":len(lexicon),"total_observed_cells":total_cells,"cell_fraction":len(lexicon)/total_cells,"folios":len({row["physical_folio"] for row in panel})},"predictive_calibration":{"source":"GDT321_LOFO","gain_bits_per_event":json.loads(G321.read_text())["summary"]["robust_gain_bits_per_event"],"charged_gain_bits":json.loads(G321.read_text())["summary"]["robust_charged_gain_bits"],"fraction_full_gain":json.loads(G321.read_text())["summary"]["fraction_full_gain"]},"excluded_rules":["t_line_entry_failed_GDT319","d_dual_entry_failed_GDT320"],"semantic_assignments":0,"f84":{"input_rows":0,"opened":False,"parsed":False,"retained":False,"joined":False,"scored":False},"inputs":{path.name:sha(path) for path in (SOURCE,PANEL,G321,VALIDATION,METHOD)},"outputs":{LEXICON.name:sha(LEXICON)},"implementation":{Path(__file__).name:sha(Path(__file__))}}; model["content_sha256"]=canonical_hash(model); MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")
    report=["# GDT322 — executable renderer grammar", "", "Status: **EXECUTABLE_TWO_RULE_RENDERER**.", "", f"The opaque lexicon covers {len(panel):,}/{len(source):,} Voynich reference events ({100*len(panel)/len(source):.1f}%) in {len(lexicon)}/{total_cells} observed exact cells and 91 folios.", "", f"Full-panel descriptive coefficients are `beta_s_line_first={beta[0]:+.6f}` and `beta_q_prev_dy={beta[1]:+.6f}`. Predictive calibration remains GDT321: +{model['predictive_calibration']['gain_bits_per_event']:.6f} held bits/event and +{model['predictive_calibration']['charged_gain_bits']:.2f} charged bits.", "", "Unknown cells remain unknown. The executable layer does not infer a license from host spelling or assign a linguistic function.", "", "## Claim ceiling", "", "Opaque-cell wrapper rendering only; no prefix, morpheme, POS, meaning, sound, language, plaintext, translation, or f84 result."]; REPORT.write_text("\n".join(report)+"\n")
    result={"schema":"GDT322_EXECUTABLE_RENDERER_RESULT_V1","status":model["status"],"summary":model["coverage"]|{"beta_s_line_first":float(beta[0]),"beta_q_prev_dy":float(beta[1])},"semantic_assignments":0,"claim_ceiling":"Opaque-cell wrapper rendering only; no prefix morpheme POS meaning sound language plaintext or translation.","f84":model["f84"],"inputs":{path.name:sha(path) for path in (SOURCE,PANEL,G321,VALIDATION)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{LEXICON.name:sha(LEXICON),MODEL.name:sha(MODEL)}}; result["content_sha256"]=canonical_hash(result); RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":result["status"],"summary":result["summary"]},sort_keys=True))
if __name__=="__main__": main()
