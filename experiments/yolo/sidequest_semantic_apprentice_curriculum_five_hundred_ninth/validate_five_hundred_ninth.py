#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 a=r('FIVE_HUNDRED_NINTH_124_ITEM_CURRICULUM_ASSIGNMENT.tsv');m=r('FIVE_HUNDRED_NINTH_MEMORY_LOAD.tsv');l=r('FIVE_HUNDRED_NINTH_SIX_DAY_LESSON_PLAN.tsv');p=r('FIVE_HUNDRED_NINTH_TEN_PAGE_PRACTICE_SHEET.tsv');c={x['curriculum_bucket']:int(x['items']) for x in m}
 checks={'assignment124':len(a)==124 and len({x['item_id'] for x in a})==124,'six_buckets':len(m)==6 and sum(c.values())==124,'card_memory41':c['MEMORIZE_CARD_VALUE']==41,'workflow_rules9':c['LEARN_WORKFLOW_RULE']==9,'graphic_rules14':c['LEARN_GRAPHIC_RULE']==14,'practice_templates18':c['PRACTISE_AS_MOTOR_TEMPLATE']==18,'address_atlas37':c['READ_FROM_VISIBLE_ADDRESS_ATLAS']==37,'local_copy5':c['COPY_FROM_LOCAL_EXEMPLAR']==5,'six_lessons':len(l)==6,'ten_pages':len(p)==10 and sum(int(x['visible_items']) for x in p)==776,'page_set':{x['page'] for x in p}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r','f67r2','f68r1','f69v'},'all_methods':all(x['training_method_de'] for x in a),'seal_absent':all(not x['page'].lower().startswith('f84') for x in p)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_NINTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
