#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts';CAP=ART/'gdt368_capacity_result.json';OBS=ART/'gdt368_visual_observations.tsv';PLAN=EXP/'FORMAL_SCAN.md';OUT=ART/'gdt368_scan_freeze.json'
def main():
 cap=json.loads(CAP.read_text());assert cap['admitted_axes']==['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'] and not cap['formal_rows_loaded_or_joined']
 p={'schema':'GDT368_SCAN_FREEZE_V1','status':'FROZEN_AFTER_VISUAL_CAPACITY_BEFORE_FORMAL_ROW_ACCESS','formal_source_path':'gdt002_exploratory_visual_formal_join.tsv','formal_channel':'CONTACT_GAP','target_count':27,'endpoints':cap['admitted_axes'],'feature_library':'FAMILY_COMPONENT_WITHIN_GROUP_NGRAM_FIRST_PREFIX_LAST_SUFFIX_DELIMITED_EXACT_LENGTH_GROUP_BOUNDARY_ALTERNATIVE','support_min':4,'absence_min':4,'folio_support_min_each_state':2,'worlds':4096,'null':'WITHIN_COMPLETE_ARRAY_ENDPOINT_PERMUTATION_PRESERVING_STATE_COUNTS','primary_statistic':'ARRAY_STRATIFIED_CONDITIONAL_MUTUAL_INFORMATION_BITS_PER_ROW','held_metric':'LOFO_CATEGORICAL_CODELENGTH_GAIN_JEFFREYS_HALF','max_search':'ALL_THREE_ENDPOINTS_X_ALL_STATE_BLIND_UNIQUE_MASKS','secure_only_sensitivity':True,'formal_access_before_freeze':False,'post_image_selection':True,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (CAP,OBS,PLAN,EXP/'METHOD.md')},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'ANONYMOUS_POSTSELECTED_GEOMETRY_FAMILY_ASSOCIATION_ONLY'};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
