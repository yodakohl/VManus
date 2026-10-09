"""Trace fixed merge occurrences on an explicitly scoped cached group panel."""
import collections,csv,gzip,hashlib,json,re,sys
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
SUBS=[('cth','T'),('ckh','K'),('cph','P'),('cfh','F'),('ch','C'),('sh','S'),('iin','N'),('in','I'),('ee','E')]

def collapse(raw):
 text=raw.lower().strip()
 for old,new in SUBS:text=text.replace(old,new)
 return text

def rules_ok(rules):
 seen=set()
 for j,(a,b,c) in enumerate(rules,1):
  assert c==a+b and c not in seen
  assert all(len(x)==1 or x in seen for x in [a,b])
  seen.add(c)

def trace(base,rules):
 nodes=[{'u':c,'s':i,'e':i+1,'b':0,'d':None,'side':None,'parent':None} for i,c in enumerate(base)]
 active=list(range(len(base)));snap=[]
 for j,(left,right,merged) in enumerate(rules,1):
  out=[];i=0
  while i<len(active):
   a=active[i]
   if i+1<len(active) and nodes[a]['u']==left and nodes[active[i+1]]['u']==right:
    b=active[i+1];assert nodes[a]['e']==nodes[b]['s']
    nid=len(nodes);nodes.append({'u':merged,'s':nodes[a]['s'],'e':nodes[b]['e'],'b':j,'d':None,'side':None,'parent':None})
    for child,side in [(a,'L'),(b,'R')]:nodes[child].update(d=j,side=side,parent=nid)
    out.append(nid);i+=2
   else:out.append(a);i+=1
  active=out;snap.append(tuple(active))
 for node in nodes:
  assert base[node['s']:node['e']]==node['u']
  assert node['d'] is None or node['b']<node['d']
 return {'nodes':nodes,'snapshots':snap,'final':tuple(active)}

def fresh():return {'stage_total':0,'stage_end':0,'final_total':0,'final_end':0,'losses':{}}

def features(t,base,rules):
 nodes=t['nodes'];final=set(t['final']);out=[]
 for j,(_left,right,merged) in enumerate(rules,1):
  pair={}
  for role,unit in [('M',merged),('R',right)]:
   cohort=[i for i in t['snapshots'][j-1] if nodes[i]['u']==unit]
   actual={i for i in final if nodes[i]['u']==unit};assert actual<=set(cohort)
   f=fresh()
   for i in cohort:
    node=nodes[i];end=int(node['e']==len(base));f['stage_total']+=1;f['stage_end']+=end
    if i in actual:f['final_total']+=1;f['final_end']+=end
    else:
     assert node['d']>j and node['parent'] is not None
     key=f"{node['d']}:{node['side']}";v=f['losses'].setdefault(key,{'total':0,'end':0});v['total']+=1;v['end']+=end
   pair[role]=f
  out.append(pair)
 return out

def add(dest,src,weight):
 for k in ['stage_total','stage_end','final_total','final_end']:dest[k]+=weight*src[k]
 for key,values in src['losses'].items():
  d=dest['losses'].setdefault(key,{'total':0,'end':0})
  for k in d:d[k]+=weight*values[k]

def ratio(n,d):return None if d==0 else F(n,d)
def pack(x):return None if x is None else {'n':x.numerator,'d':x.denominator}
def summary(row):
 vals={}
 for role in ['M','R']:
  v=row[role];assert v['stage_total']-v['final_total']==sum(x['total'] for x in v['losses'].values())
  assert v['stage_end']-v['final_end']==sum(x['end'] for x in v['losses'].values())
  vals[role+'j']=ratio(v['stage_end'],v['stage_total']);vals[role+'f']=ratio(v['final_end'],v['final_total'])
 if any(v is None for v in vals.values()):return {'rates':{k:pack(v) for k,v in vals.items()},'classification':'UNSCORABLE','gap_j':None,'gap_final':None,'later_selection':None}
 gj=vals['Mj']-vals['Rj'];gf=vals['Mf']-vals['Rf'];sel=(vals['Mf']-vals['Mj'])-(vals['Rf']-vals['Rj']);assert gf==gj+sel
 cl='CREATED_POSITIVE' if gj<=0<gf else 'REMOVED_POSITIVE' if gf<=0<gj else 'POSITIVE_BOTH' if gj>0 and gf>0 else 'NONPOSITIVE_BOTH'
 return {'rates':{k:pack(v) for k,v in vals.items()},'classification':cl,'gap_j':pack(gj),'gap_final':pack(gf),'later_selection':pack(sel)}

def controls():
 rules=[('A','B','AB'),('AB','C','ABC')]
 rows=[]
 for words in [['AB','ABC','B','BA'],['AB','AB','BC','B']]:
  row={'M':fresh(),'R':fresh()}
  for word in words:
   t=trace(word,rules);fs=features(t,word,rules)[0]
   for role in row:add(row[role],fs[role],1)
  rows.append(summary(row))
 assert rows[0]['gap_j']==pack(F(0)) and rows[0]['gap_final']==pack(F(1,2))
 assert rows[1]['gap_j']==rows[1]['gap_final']==pack(F(1,2))
 t=trace('AAA',[('A','A','AA')]);assert [(n['u'],n['s'],n['e']) for n in t['nodes'] if n['b']]==[('AA',0,2)]
 row=features(trace('AAAA',[('A','A','AA')]),'AAAA',[('A','A','AA')])[0];assert summary(row)['classification']=='UNSCORABLE'
 t=trace('ABC',rules);assert all(t['nodes'][i]['u']!='AB' for i in t['final'])
 for raw,expected in [('cthckhcphcfhchsh','TKPFCS'),('iiin','iN'),('iin','N'),('inin','II'),('eeeee','EEe')]:assert collapse(raw)==expected
 assert collapse('ch')=='C' and collapse(collapse('ch'))=='c'
 assert collapse('i')+collapse('in')=='iI' and collapse('iin')=='N'
 try:rules_ok([('A','B','AB'),('A','B','AB')])
 except AssertionError:pass
 else:raise AssertionError('duplicate product accepted')
 return {'status':'PASS','same_stage_fixtures':rows,'self_overlap_births':1,'zero_denominator':'UNSCORABLE','projection_nonidempotence_retained':True}

def main():
 spec=json.loads((P/'src/SPEC.json').read_text())
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 rr=list(csv.DictReader((ROOT/spec['rules']).open(),delimiter='\t'));rules=[(r['left'],r['right'],r['merged']) for r in rr];assert [int(r['rank']) for r in rr]==list(range(1,65));rules_ok(rules)
 source=json.loads(gzip.decompress((ROOT/spec['source']).read_bytes()));allowed=set(spec['allowed_pages']);assert len(allowed)==179
 inverse={new:old for old,new in SUBS};traces={};feat={};examples=[];readers={};receipts={}
 for ed in spec['readers']:
  rows=source[ed];ids=set();weighted=collections.Counter();row_bases={}
  for row in rows:
   assert row['edition']==ed and row['kind']=='P';assert row['page'] in allowed and row['page'] not in spec['forbidden_pages'] and not any(row['page'].startswith(x) for x in spec['forbidden_prefixes'])
   assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert re.fullmatch('[a-z]+',row['ivtff_group_raw'])
   assert row['id'] not in ids;ids.add(row['id']);base=collapse(row['ivtff_group_raw']);assert ''.join(inverse.get(c,c) for c in base)==row['ivtff_group_raw'];weighted[base]+=1;row_bases[row['id']]=base
  table=[{'rank':j,'left':a,'right':b,'merged':c,'M':fresh(),'R':fresh()} for j,(a,b,c) in enumerate(rules,1)]
  for base,weight in sorted(weighted.items()):
   if base not in traces:traces[base]=trace(base,rules);feat[base]=features(traces[base],base,rules)
   for entry,features_j in zip(table,feat[base]):
    for role in ['M','R']:add(entry[role],features_j[role],weight)
  for entry in table:entry.update(summary(entry))
  counts=collections.Counter(r['classification'] for r in table);scorable=64-counts['UNSCORABLE']
  decision='POSITIVE_CONTRAST_CREATED_BY_LATER_PROCESSING' if counts['CREATED_POSITIVE'] else 'NO_SUCH_SIGN_CREATION_OBSERVED' if scorable else 'CAPACITY_STOP'
  readers[ed]={'decision':decision,'classification_counts':dict(counts),'rows':table}
  chosen=set()
  for row in sorted(rows,key=lambda x:x['id']):
   base=row_bases[row['id']];t=traces[base];nodes=t['nodes'];final=set(t['final'])
   for j,(_a,right,merged) in enumerate(rules,1):
    if merged not in spec['highlight_products']:continue
    for role,unit in [('M',merged),('R',right)]:
     for i in t['snapshots'][j-1]:
      node=nodes[i]
      if node['u']!=unit:continue
      key=(j,role,i in final,node['e']==len(base))
      if key in chosen:continue
      chosen.add(key);examples.append({'edition':ed,'source_id':row['id'],'raw':row['ivtff_group_raw'],'projected':base,'rank':j,'merged':merged,'role':role,'node':node,'survives':i in final,'group_final':node['e']==len(base),'stage_tokens':[nodes[k]['u'] for k in t['snapshots'][j-1]],'final_tokens':[nodes[k]['u'] for k in t['final']]})
  rec_hash=hashlib.sha256(json.dumps(sorted(row_bases.items()),separators=(',',':')).encode()).hexdigest()
  receipts[ed]={'groups':len(rows),'source_ids':len(ids),'projected_types':len(weighted),'pages':len({r['page'] for r in rows}),'ordered_id_projection_sha256':rec_hash}
 out={'status':'EXPOSED_PROCESSING_DIAGNOSTIC','scope':spec['population'],'readers':readers,'source_receipts':receipts,'unique_projected_traces':len(traces),'meanings':0}
 (P/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');(P/'artifacts/EXAMPLES.json').write_text(json.dumps(examples,indent=2)+'\n')
 (P/'artifacts/CONTROLS.json').write_text(json.dumps(controls(),indent=2)+'\n')
 print(json.dumps({'receipts':receipts,'decisions':{ed:{k:v for k,v in r.items() if k!='rows'} for ed,r in readers.items()}},indent=2))

if __name__=='__main__':
 if '--controls' in sys.argv:print(json.dumps(controls(),indent=2))
 else:main()
