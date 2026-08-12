#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, urllib.request
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PANEL=ROOT/'experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv'
OBS=ROOT/'experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration.tsv'
RESULT=ROOT/'experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration.json'
OUT=ROOT/'experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration_validation.json'
def main():
    checks=[]
    panel={r['opaque_id']:r for r in csv.DictReader(PANEL.open(encoding='utf-8'),delimiter='\t') if r['phase']=='CALIBRATION'}
    rows=list(csv.DictReader(OBS.open(encoding='utf-8'),delimiter='\t'))
    assert len(rows)==16 and {r['opaque_id'] for r in rows}==set(panel); checks.append('exact_frozen_calibration_panel')
    assert all(r['currier']==panel[r['opaque_id']]['currier'] and r['canvas_id']==panel[r['opaque_id']]['canvas_id'] for r in rows); checks.append('metadata_bindings')
    for r in rows:
        req=urllib.request.Request(panel[r['opaque_id']]['review_image_url'],headers={'User-Agent':'VManus-LM001-validator/1.0'})
        with urllib.request.urlopen(req,timeout=60) as response: raw=response.read()
        assert hashlib.sha256(raw).hexdigest()==r['review_image_sha256']
    checks.append('live_official_review_image_hashes')
    c=Counter(r['leaf_margin_state'] for r in rows); assert c=={'SMOOTH':6,'TOOTHED':6,'UNCERTAIN':4}; checks.append('stored_judgment_counts')
    stored=json.loads(RESULT.read_text()); assert stored['status']=='PASS_RUBRIC_WORKABLE_NO_AMENDMENT' and stored['observations_sha256']==hashlib.sha256(OBS.read_bytes()).hexdigest(); checks.append('canonical_result')
    assert stored['gates']['rubric_amended'] is False and stored['gates']['held_images_opened_for_judgment'] is False and stored['gates']['voynich_text_features_accessed'] is False; checks.append('access_and_phase_boundary')
    out={'experiment':'LM001_LEAF_MARGIN_VISUAL_CALIBRATION_VALIDATION','status':'PASS_6_CHECK_SOURCE_AND_IMAGE_RECONSTRUCTION','check_count':len(checks),'checks':checks,'validated_result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest(),'visual_judgments_reclassified_by_validator':False,'claim_ceiling':stored['claim_ceiling']}
    OUT.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
if __name__=='__main__': main()
