import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 if not (E/'artifacts/RESULT.json').exists():print('PASS_DECLARATION_ONLY');return
 raw=json.loads((R/'experiments/yolo/gdt973_alloy_packed_header_consequences/artifacts/PREDICTIONS.json').read_text());expected=[]
 for x in raw:
  if x['model']!='R2' or x['decision']!='NECESSARY_FORM_ONLY':continue
  word=x['header'][0];assert x['eligible'] and x['page'] in ('f104r','f114r');values=None;decision='UNKNOWN_NONMINIMAL_HEADER'
  if len(word)==10:
   bindings={};violations=[];pattern=['GRADE_HEAD','A','NUM','digit_a','B','NUM','digit_b','C','NUM','digit_c']
   for component,char in zip(pattern,word):
    if component in bindings and bindings[component]!=char:violations.append(component)
    bindings[component]=char
   values=[char for component,char in zip(pattern,word) if component=='NUM'];decision='SHARED_NUM_CONTRADICTION' if violations else 'NECESSARY_NUM_ONLY'
  expected.append(dict(id=x['id'],edition=x['edition'],page=x['page'],leaf=x['leaf'],all_four_headers=x['header'],word=word,length=len(word),required_num_positions_zero_based=[2,5,8],observed_num_characters=values,decision=decision))
 result=json.loads((E/'artifacts/RESULT.json').read_text());checks=dict(rows_exact=result['rows']==expected,all_survivors=result['selected_count']==len(expected),denominator=result['input_prediction_rows']==len(raw),status=result['status']==('ALL_SELECTED_R2_HEADERS_CONTRADICTED' if expected and all(x['decision']=='SHARED_NUM_CONTRADICTION' for x in expected) else 'NOT_ALL_SELECTED_HEADERS_CONTRADICTED'),exposure=result['declared_exploratory'] and result['prior_target_header_exposure'],ceilings=result['translated_words']==result['independent_confirmation_capacity']==0 and not result['reserve_access'] and not result['full_code_or_body_tested'])
 table=[['id','edition','leaf','first_word','length','NUM_at_3','NUM_at_6','NUM_at_9','decision']]+[[str(c) for c in [x['id'],x['edition'],x['leaf'],x['word'],x['length'],*(x['observed_num_characters'] or ['','','']),x['decision']]] for x in expected]
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open() as f:checks['table']=list(csv.reader(f,delimiter='\t'))==table
 out=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,independent_scientific_confirmation=False);(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['status']=='PASS'
if __name__=='__main__':main()
