#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts'
def main():
 with (ART/'gdt368_visual_observations.tsv').open(newline='') as h:r=list(csv.DictReader(h,delimiter='\t'))
 p=json.loads((ART/'gdt368_capacity_result.json').read_text());q=dict(p);d=q.pop('content_hash');c=[len(r)==27,len({x['gdt367_target_id'] for x in r})==27,Counter(x['major_body_count'] for x in r)==Counter({'ONE':12,'THREE_PLUS':9,'TWO':6}),Counter(x['terminal_arm_count'] for x in r)==Counter({'FOUR_PLUS':16,'TWO_THREE':7,'ZERO_ONE':3,'UNCERTAIN':1}),Counter(x['dominant_hue'] for x in r)==Counter({'WARM_RED_ORANGE_TAN_BROWN':12,'COOL_GREEN_BLUE':11,'MIXED_COOL_WARM':4}),p['admitted_axes']==['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'],not p['formal_rows_loaded_or_joined'] and not p['formal_search_run'],p['post_image_selection'],not p['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in p['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['outputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['implementation'].items()),hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d];assert all(c);print(f'PASS {sum(c)}/{len(c)}')
if __name__=='__main__':main()
