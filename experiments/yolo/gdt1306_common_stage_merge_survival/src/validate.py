"""Separate projection scanner and scheduled interval-replacement validator."""
import collections,csv,gzip,hashlib,itertools,json,re,sys
from fractions import Fraction
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]

def project(raw,subs):
 s=raw.lower().strip()
 for before,after in subs:
  out=[];i=0
  while i<len(s):
   if s.startswith(before,i):out.append(after);i+=len(before)
   else:out.append(s[i]);i+=1
  s=''.join(out)
 return s

def replay(base,rules):
 # Node fields: type, start, end, born, consumed, side, parent.
 nodes=[[u,i,i+1,0,None,None,None] for i,u in enumerate(base)]
 active=list(range(len(nodes)));snapshots=[]
 for rank,(left,right,merged) in enumerate(rules,1):
  hits=[];cursor=0
  while cursor+1<len(active):
   x,y=active[cursor:cursor+2]
   if nodes[x][0]==left and nodes[y][0]==right:hits.append(cursor);cursor+=2
   else:cursor+=1
  replacements=[]
  for pos in hits:
   x,y=active[pos:pos+2];assert nodes[x][2]==nodes[y][1]
   z=len(nodes);nodes.append([merged,nodes[x][1],nodes[y][2],rank,None,None,None])
   nodes[x][4:]=[rank,'L',z];nodes[y][4:]=[rank,'R',z];replacements.append((pos,z))
  for pos,z in reversed(replacements):active[pos:pos+2]=[z]
  assert ''.join(nodes[x][0] for x in active)==base
  assert [nodes[x][1] for x in active]==[0]+[nodes[x][2] for x in active[:-1]]
  snapshots.append(tuple(active))
 for n in nodes:
  assert base[n[1]:n[2]]==n[0]
  assert n[4] is None or n[3]<n[4]
 return nodes,snapshots,tuple(active)

def collect(nodes,snap,final,base,rules):
 finalset=set(final);values=[]
 for j,(_,right,merged) in enumerate(rules,1):
  pair={}
  for role,symbol in [('M',merged),('R',right)]:
   cohort={n for n in snap[j-1] if nodes[n][0]==symbol}
   after={n for n in final if nodes[n][0]==symbol};assert after<=cohort
   count=[len(cohort),sum(nodes[n][2]==len(base) for n in cohort),len(after),sum(nodes[n][2]==len(base) for n in after)]
   losses=collections.Counter((nodes[n][4],nodes[n][5],nodes[n][2]==len(base)) for n in cohort-after)
   assert all(rank>j for rank,_,_ in losses)
   assert count[0]-count[2]==sum(losses.values())
   assert count[1]-count[3]==sum(v for (_,_,end),v in losses.items() if end)
   pair[role]=(count,losses)
  values.append(pair)
 return values

def empty():return [0,0,0,0],collections.Counter()
def pack(f):return {'n':f.numerator,'d':f.denominator}
def derived(M,R):
 vals=[]
 for v in [M,R]:
  vals.extend([None if v[0]==0 else Fraction(v[1],v[0]),None if v[2]==0 else Fraction(v[3],v[2])])
 rates={k:None if v is None else pack(v) for k,v in zip(['Mj','Mf','Rj','Rf'],vals)}
 if None in vals:return {'rates':rates,'classification':'UNSCORABLE','gap_j':None,'gap_final':None,'later_selection':None}
 mj,mf,rj,rf=vals;before=mj-rj;after=mf-rf;delta=after-before
 if before<=0 and after>0:cl='CREATED_POSITIVE'
 elif before>0 and after<=0:cl='REMOVED_POSITIVE'
 elif before>0:cl='POSITIVE_BOTH'
 else:cl='NONPOSITIVE_BOTH'
 return {'rates':rates,'classification':cl,'gap_j':pack(before),'gap_final':pack(after),'later_selection':pack(delta)}

def role_object(value):
 counts,loss=value;out=dict(zip(['stage_total','stage_end','final_total','final_end'],counts));by={}
 for (rank,side,end),n in loss.items():
  target=by.setdefault(f'{rank}:{side}',{'total':0,'end':0});target['total']+=n;target['end']+=int(end)*n
 out['losses']=by;return out

def node_object(n):return dict(zip(['u','s','e','b','d','side','parent'],n))

def controls():
 rules=[('A','B','AB'),('AB','C','ABC')]
 results=[]
 for words in [['AB','ABC','B','BA'],['AB','AB','BC','B']]:
  total={'M':empty(),'R':empty()}
  for word in words:
   nodes,snap,end=replay(word,rules);row=collect(nodes,snap,end,word,rules)[0]
   for role in total:
    for i,v in enumerate(row[role][0]):total[role][0][i]+=v
    total[role][1].update(row[role][1])
  results.append(derived(total['M'][0],total['R'][0]))
 assert results[0]['gap_j']==pack(Fraction(0)) and results[0]['gap_final']==pack(Fraction(1,2))
 assert results[1]['gap_j']==results[1]['gap_final']==pack(Fraction(1,2))
 for word,births in [('AAA',1),('AAAA',2)]:
  nodes,snap,last=replay(word,[('A','A','AA')]);assert sum(n[3]==1 for n in nodes)==births
  if word=='AAAA':
   fs=collect(nodes,snap,last,word,[('A','A','AA')])[0];assert derived(fs['M'][0],fs['R'][0])['classification']=='UNSCORABLE'
 return results

def main():
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 spec=json.loads((P/'src/SPEC.json').read_text());result=json.loads((P/'artifacts/RESULT.json').read_text());examples=json.loads((P/'artifacts/EXAMPLES.json').read_text())
 rules=[(r['left'],r['right'],r['merged']) for r in csv.DictReader((ROOT/spec['rules']).open(),delimiter='\t')]
 assert len(rules)==64 and len({r[2] for r in rules})==64
 assert all(m==l+r for l,r,m in rules)
 allowed={r['page'] for r in csv.DictReader((ROOT/spec['allowlist']).open(),delimiter='\t')};assert allowed==set(spec['allowed_pages']) and len(allowed)==179
 source=json.loads(gzip.decompress((ROOT/spec['source']).read_bytes()));assert set(source)==set(spec['readers'])
 cache={};processed=0;cohorts=0;expected_examples={};total_rows=0
 pattern=re.compile(r'cfh|cph|cth|ckh|ch|sh|[aoeindqysrlmktpf]')
 for ed in spec['readers']:
  rawrows=source[ed];byid={};freq=collections.Counter();ids_bases=[]
  for row in rawrows:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in {'f1r','f116v'}
   assert row['edition']==ed and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   raw=row['ivtff_group_raw'];units=pattern.findall(raw);assert ''.join(units)==raw and units==row['units']
   base=project(raw,spec['substitutions']);assert row['id'] not in byid;byid[row['id']]=(row,base);freq[base]+=1;ids_bases.append((row['id'],base))
   if base not in cache:
    nodes,snap,last=replay(base,rules);cache[base]=(nodes,snap,last,collect(nodes,snap,last,base,rules));processed+=1
  tables=[{'M':empty(),'R':empty()} for _ in rules]
  for base,weight in freq.items():
   for total,local in zip(tables,cache[base][3]):
    for role in total:
     for i,n in enumerate(local[role][0]):total[role][0][i]+=weight*n
     for key,n in local[role][1].items():total[role][1][key]+=weight*n
     cohorts+=1
  observed=result['readers'][ed];assert len(observed['rows'])==64;classes=collections.Counter()
  for j,(raw_rule,total,actual) in enumerate(zip(rules,tables,observed['rows']),1):
   left,right,merged=raw_rule
   expected={'rank':j,'left':left,'right':right,'merged':merged,'M':role_object(total['M']),'R':role_object(total['R'])}
   expected.update(derived(total['M'][0],total['R'][0]));assert expected==actual,(ed,j)
   classes[expected['classification']]+=1;total_rows+=1
  assert dict(classes)==observed['classification_counts']
  decision='POSITIVE_CONTRAST_CREATED_BY_LATER_PROCESSING' if classes['CREATED_POSITIVE'] else 'NO_SUCH_SIGN_CREATION_OBSERVED' if 64-classes['UNSCORABLE'] else 'CAPACITY_STOP'
  assert decision==observed['decision']
  receipt={'groups':len(rawrows),'source_ids':len(byid),'projected_types':len(freq),'pages':len({r['page'] for r in rawrows}),'ordered_id_projection_sha256':hashlib.sha256(json.dumps(sorted(ids_bases),separators=(',',':')).encode()).hexdigest()}
  assert receipt==result['source_receipts'][ed]
  # Independently locate the lexicographically first source witness in each category.
  for sid,(row,base) in sorted(byid.items()):
   nodes,snap,last,_=cache[base];lastset=set(last)
   for j,(_,right,merged) in enumerate(rules,1):
    if merged not in spec['highlight_products']:continue
    for role,unit in [('M',merged),('R',right)]:
     for nodeid in snap[j-1]:
      node=nodes[nodeid]
      if node[0]!=unit:continue
      key=(ed,j,role,nodeid in lastset,node[2]==len(base))
      expected_examples.setdefault(key,{'edition':ed,'source_id':sid,'raw':row['ivtff_group_raw'],'projected':base,'rank':j,'merged':merged,'role':role,'node':node_object(node),'survives':nodeid in lastset,'group_final':node[2]==len(base),'stage_tokens':[nodes[i][0] for i in snap[j-1]],'final_tokens':[nodes[i][0] for i in last]})
 actual_examples={(r['edition'],r['rank'],r['role'],r['survives'],r['group_final']):r for r in examples}
 assert len(actual_examples)==len(examples) and actual_examples==expected_examples
 assert processed==result['unique_projected_traces']
 assert result['status']=='EXPOSED_PROCESSING_DIAGNOSTIC' and result['scope']==spec['population'] and result['meanings']==0
 toy=controls();assert json.loads((P/'artifacts/CONTROLS.json').read_text())['same_stage_fixtures']==toy
 out={'status':'PASS','raw_groups_replayed':sum(len(r) for r in source.values()),'unique_projected_traces':processed,'reader_rule_rows_replayed':total_rows,'type_stage_role_cohorts':cohorts,'illustration_records_checked':len(examples),'scope':'Exact projection, span lineage, same-stage/final counts and arithmetic only; same-author independent implementation, not semantic or independent manuscript confirmation.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':
 if '--controls' in sys.argv:print(json.dumps(controls(),indent=2))
 else:main()
