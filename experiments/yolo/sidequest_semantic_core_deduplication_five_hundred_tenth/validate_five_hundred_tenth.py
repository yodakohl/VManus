#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 a=r('FIVE_HUNDRED_TENTH_41_CARD_VALUE_OVERLAP_AUDIT.tsv');c=r('FIVE_HUNDRED_TENTH_37_DISTINCT_SEMANTIC_CORE.tsv');m=r('FIVE_HUNDRED_TENTH_124_ITEM_DEDUPLICATED_CURRICULUM.tsv');e=r('FIVE_HUNDRED_TENTH_EIGHT_RECLASSIFIED_EVENTS.tsv');re={x['item_id']:x for x in a if x['adds_new_semantic_value']=='NO'}
 checks={'audit41':len(a)==41 and len({x['item_id'] for x in a})==41,'core37':len(c)==37 and len({x['item_id'] for x in c})==37,'four_reclassified':set(re)=={'CKHE','CHEO','LS','PROC169'},'manual124':len(m)==124 and len({x['item_id'] for x in m})==124,'four_alias_rows':sum(x['curriculum_bucket']=='LEARN_COMPOSITE_ALIAS_SIGN' for x in m)==4,'event_audit8':len(e)==8 and len({x['event_id'] for x in e})==8,'ckhe4':sum(x['old_component_or_card']=='CKHE' for x in e)==4,'cheo2':sum(x['old_component_or_card']=='CHEO' for x in e)==2,'ls1':sum(x['old_component_or_card']=='LS' for x in e)==1,'proc169_1':sum(x['old_component_or_card']=='PROC169' for x in e)==1,'no_old_overloads':all(v not in '|'.join(x['teaching_value_or_rule_de'] for x in m) for v in ['OPERATION: seihen','ARGUMENT: Auszug','OPERATION: abfuehren','STUFE II']), 'seal_absent':all(not x['page'].lower().startswith('f84') for x in e)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_TENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
