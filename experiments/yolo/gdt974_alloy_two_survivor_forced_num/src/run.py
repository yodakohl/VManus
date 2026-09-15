import csv,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
P=R/'experiments/yolo/gdt973_alloy_packed_header_consequences/artifacts/PREDICTIONS.json'
def test(word):
 chars=[word[i] for i in [2,5,8]] if len(word)==10 else None
 return dict(word=word,length=len(word),required_num_positions_zero_based=[2,5,8],observed_num_characters=chars,decision='UNKNOWN_NONMINIMAL_HEADER' if chars is None else ('NECESSARY_NUM_ONLY' if len(set(chars))==1 else 'SHARED_NUM_CONTRADICTION'))
def main():
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 good=''.join(['a','b','n','d','e','n','f','g','n','h']);bad=good[:5]+'x'+good[6:]
 assert test(good)['decision']=='NECESSARY_NUM_ONLY' and test(bad)['decision']=='SHARED_NUM_CONTRADICTION'
 raw=json.loads(P.read_text());selected=[x for x in raw if x['model']=='R2' and x['decision']=='NECESSARY_FORM_ONLY'];rows=[]
 for x in selected:
  assert x['eligible'] and x['page'] in ['f104r','f114r'];rows.append(dict(id=x['id'],edition=x['edition'],page=x['page'],leaf=x['leaf'],all_four_headers=x['header'],**test(x['header'][0])))
 result=dict(status='ALL_SELECTED_R2_HEADERS_CONTRADICTED' if rows and all(x['decision']=='SHARED_NUM_CONTRADICTION' for x in rows) else 'NOT_ALL_SELECTED_HEADERS_CONTRADICTED',declared_exploratory=True,prior_target_header_exposure=True,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),input_prediction_rows=len(raw),selected_count=len(rows),rows=rows,source_fixtures=dict(positive=test(good),negative=test(bad)),translated_words=0,independent_confirmation_capacity=0,reserve_access=False,full_code_or_body_tested=False)
 (E/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','edition','leaf','first_word','length','NUM_at_3','NUM_at_6','NUM_at_9','decision'])
  for x in rows:w.writerow([x['id'],x['edition'],x['leaf'],x['word'],x['length'],*(x['observed_num_characters'] or ['','','']),x['decision']])
 print(json.dumps(result))
if __name__=='__main__':main()
