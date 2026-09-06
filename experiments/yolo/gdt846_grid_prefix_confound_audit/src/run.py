import itertools,json,math,re
from collections import defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
spec=json.loads((E/'src/SPEC.json').read_text())
def save(name,x): (E/'artifacts'/name).write_text(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n')
def informative(v):
 a,b,c,d=v;return all(x>0 for x in [a+b,c+d,a+c,b+d])
def expect(v):
 a,b,c,d=v;return (a+b)*(a+c)/sum(v)
hits=json.loads((ROOT/spec['source']).read_text());parsed=[]
for r in hits:
 m=re.fullmatch(r'(qo|o)?([kt])(ch|sh)(e{0,2})(d?)y',r['ivtff_group_raw']);assert m
 w,h,c,e,d=m.groups();assert not r['page'].startswith('f84')
 parsed.append(dict(r,wrapper=w or '',head=h,middle=c,e2=len(e)==2,d1=bool(d),leaf=re.match(r'f[0-9]+',r['page']).group()))
rows=[];summary=[];pairs=[]
for partition,axes in spec['partitions'].items():
 groups=defaultdict(list)
 for r in parsed:groups[(r['edition'],r['wrapper'],r['head'],r['middle'],*(r[x] for x in axes))].append(r)
 tables={}
 for key,rs in sorted(groups.items()):
  v=[sum(r['e2'] and r['d1'] for r in rs),sum(r['e2'] and not r['d1'] for r in rs),sum(not r['e2'] and r['d1'] for r in rs),sum(not r['e2'] and not r['d1'] for r in rs)]
  row=dict(partition=partition,key=list(key),counts=v,expected=expect(v),informative=informative(v),folios=sorted({r['leaf'] for r in rs}),source_ids=[r['source_group_id'] for r in rs]);rows.append(row);tables[key]=row
 for ed,w in itertools.product(spec['editions'],spec['wrappers']):
  rs=[r for k,r in tables.items() if k[:2]==(ed,w)];inf=[r for r in rs if r['informative']]
  num=sum(r['counts'][0]*r['counts'][3]/sum(r['counts']) for r in inf);den=sum(r['counts'][1]*r['counts'][2]/sum(r['counts']) for r in inf)
  summary.append(dict(partition=partition,edition=ed,wrapper=w,strata=len(rs),informative_strata=len(inf),informative_folios=sorted({f for r in inf for f in r['folios']}),all_observed=sum(r['counts'][0] for r in rs),all_expected=sum(r['expected'] for r in rs),supported_e2=sum(sum(r['counts'][:2]) for r in inf),informative_observed=sum(r['counts'][0] for r in inf),informative_expected=sum(r['expected'] for r in inf),mh_odds=num/den if den else 'INF' if num else 'UNDEFINED'))
 for ed,other in itertools.product(spec['editions'],['','o']):
  supports=[]
  for key,r in tables.items():
   if key[:2]!=(ed,'qo'):continue
   partner=tables.get((ed,other,*key[2:]))
   if partner and r['informative'] and partner['informative']:supports.append(dict(core_and_axes=list(key[2:]),qo=r['counts'],other=partner['counts'],folios=sorted(set(r['folios'])|set(partner['folios']))))
  pairs.append(dict(partition=partition,edition=ed,other=other,shared_informative_strata=len(supports),supports=supports))
save('STRATA.json',rows);save('RESULT.json',dict(status='EXPLORATORY_CONFOUND_AND_CAPACITY_AUDIT_COMPLETE',source_hits=len(hits),summary=summary,paired_support=pairs));print(json.dumps([r for r in summary if r['edition']=='ZL3b']))
