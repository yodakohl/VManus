#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, urllib.request
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PANEL=ROOT/'experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv'
OBS=ROOT/'experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.tsv'
OLD=ROOT/'experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.tsv'
RESULT=ROOT/'experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.json'
OUT=ROOT/'experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result_validation.json'
def main():
    checks=[]
    panel={r['opaque_id']:r for r in csv.DictReader(PANEL.open(encoding='utf-8'),delimiter='\t')}
    rows=list(csv.DictReader(OBS.open(encoding='utf-8'),delimiter='\t'))
    assert len(rows)==19 and {r['opaque_id'] for r in rows}==set(panel); checks.append('exact_frozen_extension_panel')
    assert all(r['currier']=='A' and r['quire']==panel[r['opaque_id']]['quire'] and r['canvas_id']==panel[r['opaque_id']]['canvas_id'] for r in rows); checks.append('metadata_bindings')
    for r in rows:
        req=urllib.request.Request(panel[r['opaque_id']]['review_image_url'],headers={'User-Agent':'VManus-LM001X-result-validator/1.0'})
        with urllib.request.urlopen(req,timeout=60) as response: raw=response.read()
        assert hashlib.sha256(raw).hexdigest()==r['review_image_sha256']
    checks.append('live_official_review_image_hashes')
    c=Counter(r['leaf_margin_state'] for r in rows); assert c=={'SMOOTH':14,'TOOTHED':5}; checks.append('extension_counts')
    old=list(csv.DictReader(OLD.open(encoding='utf-8'),delimiter='\t')); combined=old+rows
    cc=Counter(r['leaf_margin_state'] for r in combined); tq=Counter(r['quire'] for r in combined if r['leaf_margin_state']=='TOOTHED')
    assert cc=={'SMOOTH':24,'TOOTHED':10,'UNCERTAIN':1} and tq['q05']==3 and max(tq.values())/cc['TOOTHED']==0.3; checks.append('combined_counts_and_quire_share')
    stored=json.loads(RESULT.read_text()); assert stored['status']=='STOP_COMBINED_QUIRE_CONCENTRATION_FAILED' and stored['failed_gates']==['max_quire_share_no_more_than_point25'] and stored['observations_sha256']==hashlib.sha256(OBS.read_bytes()).hexdigest(); checks.append('canonical_stop_and_gate')
    assert stored['access']['voynich_text_features_accessed'] is False and stored['access']['extension_images_judged_once'] is True; checks.append('access_boundary')
    out={'experiment':'LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_RESULT_VALIDATION','status':'PASS_7_CHECK_SOURCE_AND_COMBINED_GATE_RECONSTRUCTION','check_count':len(checks),'checks':checks,'validated_result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest(),'visual_judgments_reclassified_by_validator':False,'claim_ceiling':stored['claim_ceiling']}
    OUT.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
if __name__=='__main__': main()
