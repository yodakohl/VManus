"""Separate complete selection/case reconstruction; not an independent meaning check."""
import csv,hashlib,json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parents[1]
def load(p):return json.loads((HERE/p).read_text())
def main():
 m=load('src/MODEL.json');lock=load('MODEL_LOCK.json')
 for p,h in {**m['input_hashes'],**lock['files']}.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 original=json.loads((ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());expected=[]
 for e,ps in original.items():
  for p in ps:
   if any(w in {'lchedy','chealy'} for l in p['lines'] for w in l['words']):expected.append({'edition':e,**p})
 source=load('src/SOURCE.json');assert source['units']==expected and source['denominators']=={e:len(ps) for e,ps in original.items()}
 assert all(not p['page'].startswith('f84') and p['page']!='f116v' for p in expected)
 cases=load('artifacts/CASES.json');cold=load('artifacts/COLD_CASES.json');byid={c['target']['id']:c for c in cases};coldid={c['target']['id']:c for c in cold}
 assert len(byid)==len(cases) and len(coldid)==len(cold)
 n=nc=ng=0;expected_align=[];focal=[]
 for p in expected:
  cells=[]
  for line in p['lines']:
   for i,(raw,sid) in enumerate(zip(line['words'],line['source_ids'])):
    cells.append({'id':sid,'raw':raw,'locus':line['locus'],'line_last':i==len(line['words'])-1})
    expected_align.append([p['edition'],p['id'],p['page'],sid,raw,m['dictionary'].get(raw,'UNREAD')])
  ng+=len(cells);last=None;previous=[]
  for i,g in enumerate(cells):
   if g['raw']=='chealy':
    nc+=1;c=coldid[g['id']];assert c['target']==g and c['paragraph_last']==(i==len(cells)-1)
    assert c['if_air_is_cold']==([v['raw'] for v in cells[max(0,i-3):i+1]]==['sheedy','qokaiin','chedaiin','chealy'])
    assert c['before_ids']==[v['id'] for v in cells[:i]]
   if g['raw']=='lchedy':
    n+=1;c=byid[g['id']];assert c['target']==g and c['prior_chedy_count']==len(previous)
    if last is None:assert c['status']=='OVERT_CONSTRUCTOR_CONTRADICTION' and c['last_change'] is None and c['X'] is None and c['Y'] is None
    else:
     prefix=cells[:last];x=prefix[-2] if len(prefix)>=2 and prefix[-1]['raw']=='okaiin' else prefix[-1] if prefix else None;y=cells[last+1] if last+1<len(cells) else None
     assert c['last_change']==cells[last] and c['X']==x and c['Y']==y and c['inverse_from']==y and c['inverse_to']==x
     span=cells[last+1:i];assert c['interval_ids']==[v['id'] for v in span] and c['unknown_interval']==sum(v['raw'] not in m['dictionary'] for v in span)
     status='C0_VAPOUR_WATER_REFERENCE_ONLY' if x and y and x['raw']=='solkeey' and y['raw']=='qokain' else 'CONDITIONAL_REFERENCE_UNBOUND_MATERIALS';assert c['status']==status
     if p['page']=='f77r' and g['locus']=='f77r.37':focal.append((p['edition'],cells[last]['locus'],x['raw'],y['raw']))
   if g['raw']=='chedy':last=i;previous.append(i)
 assert n==len(cases) and nc==len(cold);assert sorted(focal)==[('IT2a','f77r.36','qotain','dolchl'),('ZL3b','f77r.36','qotain','dolchl')]
 result=load('artifacts/RESULT.json');assert result['source_groups']==ng and result['native_paragraphs']==len(expected)
 for e,s in result['summaries'].items():assert s=={'lchedy':sum(c['edition']==e for c in cases),'status_counts':dict(Counter(c['status'] for c in cases if c['edition']==e)),'chealy':sum(c['edition']==e for c in cold),'cold_templates':sum(c['edition']==e and c['if_air_is_cold'] for c in cold)}
 rows=list(csv.reader((HERE/'artifacts/ALIGNMENT.tsv').open(),delimiter='\t'));assert rows[1:]==expected_align
 assert result['decision']=='OVERT_INVERSE_LAST_WRITER_CONTRADICTED' and result['focal_decision']=='DIRECT_35_TO_37_BINDING_CONTRADICTED'
 assert not result['significance'] and result['confirmed_words']==result['independent_meaning_confirmation_capacity']==result['RF_native_capacity']==0
 val={'status':'PASS_COMPLETE_SELECTION_AND_FIXED_CASES','paragraphs':len(expected),'source_groups':ng,'inverse_cases':n,'cold_cases':nc,'focal':focal,'coverage':'source selection, all inverse and cold cases, every alignment; not meaning, complete physical execution or independent review'}
 (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val))
if __name__=='__main__':main()
