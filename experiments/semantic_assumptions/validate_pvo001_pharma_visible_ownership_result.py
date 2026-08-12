#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, urllib.request
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions/results';PANEL=B/'pvo001_pharma_visible_ownership_selection.tsv';OBS=B/'pvo001_pharma_visible_ownership_result.tsv';RESULT=B/'pvo001_pharma_visible_ownership_result.json';REPORT=B/'pvo001_pharma_visible_ownership_result_report.md';OUT=B/'pvo001_pharma_visible_ownership_result_validation.json'
def main():
 checks=[];panel={r['opaque_id']:r for r in csv.DictReader(PANEL.open(encoding='utf-8'),delimiter='\t')};rows=list(csv.DictReader(OBS.open(encoding='utf-8'),delimiter='\t'))
 assert len(rows)==12 and {r['opaque_id'] for r in rows}==set(panel);checks.append('exact_complete_frozen_canvas_panel')
 for r in rows:
  req=urllib.request.Request(panel[r['opaque_id']]['review_image_url'],headers={'User-Agent':'VManus-PVO001-result-validator/1.0'})
  with urllib.request.urlopen(req,timeout=60) as response: raw=response.read()
  assert hashlib.sha256(raw).hexdigest()==r['review_image_sha256'] and r['canvas_id']==panel[r['opaque_id']]['canvas_id']
 checks.append('live_official_image_hash_and_canvas_bindings')
 c=Counter(r['visible_owner_state'] for r in rows);assert c=={'OWNER_ABSENT':11,'OWNER_PRESENT':1};checks.append('exact_state_counts')
 positives=[r for r in rows if r['visible_owner_state']=='OWNER_PRESENT'];assert len(positives)==1 and positives[0]['opaque_id']=='PVBF6CD577' and positives[0]['quire']=='q19' and positives[0]['outside_prior_mixed_folios']=='1' and sum(int(r['visible_owner_device_count']) for r in rows)==1;checks.append('sole_device_distribution')
 stored=json.loads(RESULT.read_text());assert stored['status']=='STOP_COMPLETE_CENSUS_ONLY_ONE_VISIBLE_OWNER_CANVAS' and stored['failed_gates']==['at_least_four_owner_present_canvases','both_q15_and_q19_have_owner_present','at_least_six_visible_owner_devices'] and stored['observations_sha256']==hashlib.sha256(OBS.read_bytes()).hexdigest();checks.append('canonical_stop_and_failed_gates')
 assert stored['access']['voynich_transcription_opened'] is False and stored['access']['label_identity_or_formal_feature_opened'] is False and 'stops before object-state mapping' in REPORT.read_text();checks.append('text_and_mapping_access_seal')
 out={'experiment':'PVO001_PHARMA_VISIBLE_OWNERSHIP_RESULT_VALIDATION','status':'PASS_6_CHECK_SOURCE_AND_CAPACITY_STOP_RECONSTRUCTION','check_count':len(checks),'checks':checks,'validated_result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest(),'validated_report_sha256':hashlib.sha256(REPORT.read_bytes()).hexdigest(),'visual_judgments_reclassified_by_validator':False,'claim_ceiling':stored['claim_ceiling']};OUT.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
if __name__=='__main__':main()
