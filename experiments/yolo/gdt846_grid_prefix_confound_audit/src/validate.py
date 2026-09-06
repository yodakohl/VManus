import collections,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
s=json.loads((E/'src/SPEC.json').read_text());hits=json.loads((ROOT/s['source']).read_text());strata=json.loads((E/'artifacts/STRATA.json').read_text());res=json.loads((E/'artifacts/RESULT.json').read_text());byid={r['source_group_id']:r for r in hits};assert len(byid)==len(hits)
for partition,axes in s['partitions'].items():
 rows=[r for r in strata if r['partition']==partition];covered=[]
 for row in rows:
  v=[0,0,0,0];folios=set()
  for rid in row['source_ids']:
   r=byid[rid];w=r['ivtff_group_raw'];prefix='qo' if w.startswith('qo') else 'o' if w.startswith('o') else '';tail=w[len(prefix):];core=tail[:1],tail[1:3];is_d=tail.endswith('dy');e=tail[3:-2] if is_d else tail[3:-1];assert set(e)<={'e'} and len(e)<=2
   leaf=re.match(r'f[0-9]+',r['page']).group();key=[r['edition'],prefix,*core,*[leaf if x=='leaf' else r[x] for x in axes]];assert key==row['key']
   index=(0 if len(e)==2 else 2)+(0 if is_d else 1);v[index]+=1;folios.add(leaf)
  assert v==row['counts'] and sorted(folios)==row['folios'];covered+=row['source_ids']
  a,b,c,d=v;assert math.isclose(row['expected'],(a+b)*(a+c)/sum(v));assert row['informative']==bool((a+b)*(c+d)*(a+c)*(b+d))
 assert collections.Counter(covered)==collections.Counter(byid.keys())
 for summary in [r for r in res['summary'] if r['partition']==partition]:
  rs=[r for r in rows if r['key'][:2]==[summary['edition'],summary['wrapper']]];inf=[r for r in rs if r['informative']]
  assert sum(r['counts'][0] for r in rs)==summary['all_observed'];assert len(inf)==summary['informative_strata']
  assert math.isclose(sum(r['expected'] for r in inf),summary['informative_expected'])
  assert sum(r['counts'][0] for r in inf)==summary['informative_observed']
 for pair in [r for r in res['paired_support'] if r['partition']==partition]:
  left={tuple(r['key'][2:]) for r in rows if r['key'][:2]==[pair['edition'],'qo'] and r['informative']};right={tuple(r['key'][2:]) for r in rows if r['key'][:2]==[pair['edition'],pair['other']] and r['informative']};assert len(left&right)==pair['shared_informative_strata']
(E/'artifacts/VALIDATION.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_SUFFIX_PARSER_AND_PARTITION_COVERAGE','hits':len(hits),'partitions':len(s['partitions']),'meaning_validated':False},indent=2)+'\n');print('PASS')
