#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal';ART=EXP/'artifacts'
INPUTS=[ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/artifacts/gdt363_panel.tsv',ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/artifacts/gdt363_result.json',ROOT/'experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_panel.tsv',ROOT/'experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_result.json',EXP/'METHOD.md']
OUT=ART/'gdt365_freeze.json'
def main():
 ART.mkdir(parents=True,exist_ok=True)
 p={'schema':'GDT365_FREEZE_V1','status':'POSTEXPOSURE_MODEL_FROZEN_BEFORE_DISTRIBUTED_FORMAL_SCORING','endpoints':['LEAF_MARGIN_BINARY','REPRODUCTIVE_THREE_CLASS'],'dimensions':[2,4,8],'feature_support_min':8,'feature_absence_min':8,'nuisance_residual_ridge':8.0,'classifier':'SMOOTHED_NEAREST_CLASS_CENTROID_SPHERICAL','primary':'LEAVE_ONE_PHYSICAL_FOLIO_OUT','sensitivity':'LEAVE_ONE_QUIRE_OUT','null_worlds':1024,'max_family':6,'postexposure':True,'pharma_local_overlap_capacity':{'contact_x_root_color':2,'root_color_x_root_leaf':6,'flower_count_x_root_color':7,'model_run':False},'access':{'formal_source_opened':False,'new_images_or_catalogues_opened':False,'f84_accessed':False},'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in INPUTS},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'POSTEXPOSURE_DISTRIBUTED_ANONYMOUS_PAGE_SIGNAL_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM'}
 p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
