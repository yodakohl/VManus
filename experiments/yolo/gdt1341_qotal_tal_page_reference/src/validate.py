from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2];PAGES=['f75v','f83r','f104v'];CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END'}
def read(p):
 x=p.read_bytes();return json.loads(gzip.decompress(x) if p.suffix=='.gz' else x)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cols='edition,page,locus,kind,source_row_index,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator';cmd=['./vmanus-exp','query-tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','--selector','page','--columns',cols]
 for page in PAGES:cmd+=['--allow',page]
 call=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True);body='\n'.join(s for s in call.stdout.splitlines() if not s.startswith('GUARD_STATS '));raw=list(csv.DictReader(io.StringIO(body),delimiter='\t'));rows=[]
 for x in raw:
  assert x['page'] in PAGES
  if x['kind']!='P':continue
  ed=x['edition'];n=int(x['source_group_index']);rows.append({'id':f"{ed}|{x['locus']}|G{n:03d}",'edition':ed,'page':x['page'],'locus':x['locus'],'row':int(x['source_row_index']),'index':n,'count':int(x['source_group_count']),'raw':x['ivtff_group_raw'],'left':x['left_separator'],'right':x['right_separator']})
 rows.sort(key=lambda x:(x['edition'],x['page'],x['row'],x['index']));assert rows==read(B/'artifacts/SOURCE.json.gz'),'INVALID_INPUT: old cache is not complete original Ppage intake';saved=read(B/'artifacts/CASES.json');result=read(B/'artifacts/RESULT.json');checks=0
 for ed,records in saved.items():
  assert [x['page'] for x in records]==PAGES
  for rec in records:
   page=rec['page'];rr=[x for x in rows if x['edition']==ed and x['page']==page];bykey={(x['locus'],x['index']):x for x in rr};donors=[x for x in rr if x['raw']=='qotal'];assert rec['P_groups']==len(rr) and rec['qotal_all']==donors;assert rec['joined_cheytal']==[x for x in rr if x['raw']=='cheytal'];ps=[];us=[]
   for right in rr:
    left=bykey.get((right['locus'],right['index']-1))
    if not left or left['raw']!='chey' or right['raw']!='tal':continue
    strict=left['left'] in CLEAR and left['right']=='DEFINITE_SPACE' and right['left']=='DEFINITE_SPACE' and right['right'] in CLEAR;prior=[d for d in donors if d['row']<left['row'] or (d['row']==left['row'] and d['index']<left['index'])];good=[d for d in prior if d['left'] in CLEAR and d['right'] in CLEAR];uncertain=[d for d in prior if d not in good];v={'chey':left,'tal':right,'strict':strict,'earlier_strict_producers':good,'earlier_uncertain_producers':uncertain,'latest_strict_producer':max(good,key=lambda d:(d['row'],d['index'])) if good else None,'status':'NECESSARY_POINTER_AVAILABLE' if good else 'SOURCE_UNCERTAIN' if uncertain else 'MISSING_LITERAL_PRODUCER'}
    if page=='f83r':
     n=int(left['locus'].split('.')[1]);limits=(1,8) if n<=8 else (9,17) if n<=17 else (18,24) if n<=24 else (25,55);v['same_scene_strict_producers']=[d for d in good if limits[0]<=int(d['locus'].split('.')[1])<=limits[1]]
    (ps if strict else us).append(v);checks+=1
   assert rec['strict_consumers']==ps and rec['uncertain_pairs']==us
  cases=[c for p in records if p['page']!='f83r' for c in p['strict_consumers']];counts=Counter(c['status'] for c in cases);decision='NO_CAPACITY' if not cases else 'FIXED_PAGE_RULE_CONTRADICTED' if counts['MISSING_LITERAL_PRODUCER'] else 'SOURCE_UNCERTAIN' if counts['SOURCE_UNCERTAIN'] else 'NECESSARY_CAPACITY_ONLY';assert result['readers'][ed]=={'additional_strict_consumers':len(cases),'status_counts':dict(counts),'decision':decision}
 out={'status':'PASS','original_P_groups':len(rows),'candidate_pairs_checked':checks,'pages_per_reading':3,'method':'Selector-first original-page reconstruction; exact cache completeness; right-neighbor index lookup and independent order predicates; every strict/uncertain/joined case retained. Source and fixed-condition verification only, not meaning.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');(B/'artifacts/GUARD_RECEIPT.json').write_text(json.dumps({'command':cmd,'output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()},indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
