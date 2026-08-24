#!/usr/bin/env python3
import csv, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(name):
 with (HERE/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=read('FIVE_HUNDRED_SIXTH_TWO_REGISTER_PROFILES.tsv');q=read('FIVE_HUNDRED_SIXTH_16_PRIMITIVE_REGISTER_PROFILE.tsv');b=read('FIVE_HUNDRED_SIXTH_56_REGISTER_BIGRAMS.tsv');a=read('FIVE_HUNDRED_SIXTH_116_REGISTER_WORKFLOW_ASSIGNMENTS.tsv');m=read('FIVE_HUNDRED_SIXTH_124_ITEM_REGISTER_MANUAL.tsv');d={x['register']:x for x in p}
 checks={
  'two_profiles':len(p)==2,
  'herbal_19_104_4':(d['HERBAL']['statements'],d['HERBAL']['emitted_tokens'],d['HERBAL']['closed_statements'])==('19','104','4'),
  'bio_97_366_85':(d['BIOLOGICAL']['statements'],d['BIOLOGICAL']['emitted_tokens'],d['BIOLOGICAL']['closed_statements'])==('97','366','85'),
  'primitive_rows_16':len(q)==16,
  'primitive_totals_470':sum(int(x['count']) for x in q)==470,
  'bigram_rows_56':len(b)==56,
  'shared_bigrams_36':sum(x['register_status']=='SHARED' for x in b)==36,
  'herbal_only_3':sum(x['register_status']=='HERBAL_ONLY' for x in b)==3,
  'bio_only_14':sum(x['register_status']=='BIOLOGICAL_ONLY' for x in b)==14,
  'unseen_3':sum(x['register_status']=='UNSEEN' for x in b)==3,
  'assignments_116':len(a)==116 and len({x['statement_id'] for x in a})==116,
  'manual_124':len(m)==124 and sum(x['layer']=='L7_REGISTER_WORKFLOW' for x in m)==2,
  'shared_machine_constant':all(x['shared_machine']=='PASS505_FIVE_STATE_AUTOMATON' for x in a),
  'seal_absent':not any('f84' in str(v).lower() for x in a for v in x.values()),
 }
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SIXTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
