#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt366_matched_reproductive_delta';ART=EXP/'artifacts';PANEL=ROOT/'experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_panel.tsv';FEATURES=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal/artifacts/gdt365_feature_manifest.tsv';OUT=ART/'gdt366_freeze.json'
def main():
 ART.mkdir(parents=True,exist_ok=True);rows=list(csv.DictReader(PANEL.open(),delimiter='\t'));d={(r['page'],r['visual_state']) for r in rows};pairs=[{'physical_folio':'f4','berry_page':'f4r','flower_page':'f4v'},{'physical_folio':'f17','berry_page':'f17v','flower_page':'f17r'}];assert all((p['berry_page'],'BERRY_NO_CIRCLES') in d and (p['flower_page'],'FLOWER_SIDE') in d for p in pairs);assert ('f8r','NO_FRUIT_OR_FLOWER') in d and ('f8v','FLOWER_SIDE') in d
 p={'schema':'GDT366_FREEZE_V1','status':'POSTEXPOSURE_SINGLE_TEST_FROZEN_BEFORE_DELTA_COMPUTATION','primary_pairs':pairs,'secondary_unscored_contrast':{'physical_folio':'f8','no_fruit_flower_page':'f8r','flower_page':'f8v'},'feature_manifest_count':sum(1 for _ in csv.DictReader(FEATURES.open(),delimiter='\t')),'primary_statistic':'COSINE_OF_STANDARDIZED_BERRY_MINUS_FLOWER_DELTAS','null':'ALL_DISTINCT_QUIRE_HERBAL_A_HAND1_RECTO_VERSO_FOLIO_PAIRS_X_FOUR_SIGN_ORIENTATIONS','strict_sensitivity':True,'postexposure':True,'access':{'formal_source_opened':False,'new_images_or_catalogues_opened':False,'f84_accessed':False},'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (PANEL,FEATURES,EXP/'METHOD.md')},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'REPLICATED_WITHIN_FOLIO_ANONYMOUS_FORMAL_PAGE_PROFILE_CHANGE_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM'};assert p['feature_manifest_count']==227;p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
