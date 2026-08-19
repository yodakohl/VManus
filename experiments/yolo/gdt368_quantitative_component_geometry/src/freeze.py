#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts';TARGET=ROOT/'experiments/yolo/gdt367_joint_cell_visual_acquisition/artifacts/gdt367_target_manifest.tsv';G367=ROOT/'experiments/yolo/gdt367_joint_cell_visual_acquisition/artifacts/gdt367_result.json';SCHEMA=ART/'gdt368_schema.tsv';OUT=ART/'gdt368_freeze.json'
def main():
 ART.mkdir(parents=True,exist_ok=True)
 with TARGET.open(newline='') as h: rows=list(csv.DictReader(h,delimiter='\t'))
 assert len(rows)==len({r['locus'] for r in rows})==27 and all(not r['page'].startswith('f84') for r in rows)
 p={'schema':'GDT368_FREEZE_V1','status':'POST_IMAGE_SELECTION_YOLO_EXTRACTION_FROZEN_BEFORE_FORMAL_ACCESS','target_count':27,'loci_sha256':hashlib.sha256('\n'.join(sorted(r['locus'] for r in rows)).encode()).hexdigest(),'axes':['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'],'post_image_selection':True,'formal_access_before_visual_calls':False,'same_component_assignments_as_gdt367':True,'no_row_drops':True,'single_observer':True,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (TARGET,G367,SCHEMA,EXP/'METHOD.md')},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'COARSE_POSTSELECTED_VISIBLE_GEOMETRY_ONLY'}
 p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
