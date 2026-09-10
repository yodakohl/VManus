#!/usr/bin/env python3
"""Separate guarded intake and full concordance replay, no primary imports."""
import collections,csv,hashlib,io,itertools,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def leaf(page):return re.match(r'f[0-9]+',page)[0]
def kind(short,long):
 if short in long:return 'echo'
 if short==''.join(long):return 'spacing'
 if len(short)>=sum(map(len,long)):return 'nonshort'
 return 'proper'
def observations(lines,columns):
 out=[];raw=0;prose=0
 for line in lines:
  m=line['metadata']
  if m['kind']!='P':continue
  prose+=1;g=[dict(zip(columns,x)) for x in line['groups']];n=len(g)
  if int(m['source_group_count'])!=n or [int(x['source_group_index']) for x in g]!=list(range(1,n+1)):continue
  # Endpoint-first loops independently cover spans of total width3,4,5.
  for start in range(n):
   for end in range(start+2,min(n,start+5)):
    raw+=1;window=g[start:end+1]
    if not all(re.fullmatch('[a-z]+',x['ivtff_group_raw']) for x in window):continue
    if not all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(window,window[1:])):continue
    out.append({'page':m['page'],'locus':m['locus'],'start':start+1,'hand':m['hand'],'section':m['section'],'middle':[x['ivtff_group_raw'] for x in window[1:-1]],'flanks':[window[0]['ivtff_group_raw'],window[-1]['ivtff_group_raw']],'source_ids':[x['source_group_id'] for x in window]})
 out.sort(key=lambda r:(r['page'],r['locus'],len(r['middle']),r['start']))
 return out,raw,prose

def rules(obs):
 byflank=collections.defaultdict(lambda:([],[]))
 for i,o in enumerate(obs):byflank[tuple(o['flanks'])][len(o['middle'])!=1].append(i)
 support=collections.defaultdict(lambda:collections.defaultdict(list))
 for flanks,(shorts,longs) in byflank.items():
  for i,j in itertools.product(shorts,longs):
   s,t=obs[i],obs[j]
   if leaf(s['page'])==leaf(t['page']):continue
   support[(s['middle'][0],tuple(t['middle']))][flanks].append([i,j])
 out=[]
 for (short,long),contexts in sorted(support.items()):
  leaves=set();hands=collections.Counter()
  for pairs in contexts.values():
   for i,j in pairs:
    leaves.update([leaf(obs[i]['page']),leaf(obs[j]['page'])]);hands[(obs[i]['hand'],obs[j]['hand'])]+=1
  classification=kind(short,long)
  out.append({'short':short,'long':list(long),'kind':classification,'contexts':[{'flanks':list(f),'pairs':sorted(ps)} for f,ps in sorted(contexts.items())],'leaves':sorted(leaves),'hand_pairs':[[a,b,n] for (a,b),n in sorted(hands.items())],'qualified':classification=='proper' and len(contexts)>=2 and len(leaves)>=3})
 return out

def invented():
 cols=['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
 def line(page,words,num=1):
  return {'metadata':{'page':page,'locus':page+'.'+str(num),'kind':'P','hand':'h','section':'s','source_group_count':str(len(words))},'groups':[[f'{page}.{num}.{i}',str(i),w,'LINE_START' if i==1 else 'DEFINITE_SPACE','LINE_END' if i==len(words) else 'DEFINITE_SPACE'] for i,w in enumerate(words,1)]}
 lines=[line('f1r',['a','zz','b']),line('f5r',['a','alpha','beta','b']),line('f9r',['c','zz','d']),line('f5r',['c','alpha','beta','d'],2)]
 oo,_,_=observations(lines,cols);rr=rules(oo);assert any(r['short']=='zz' and r['long']==['alpha','beta'] and r['qualified'] for r in rr)
 same=[line('f1r',['a','zz','b']),line('f1v',['a','alpha','beta','b'])];assert rules(observations(same,cols)[0])==[]
 wrong=[line('f1r',['a','zz','b']),line('f5r',['a','alpha','beta','c'])];assert rules(observations(wrong,cols)[0])==[]
 tests=0
 for separator in ['UNCERTAIN_SMALL_SPACE','DRAWING_INTERRUPTION']:
  x=line('f1r',['a','zz','b']);x['groups'][0][4]=separator
  assert observations([x],cols)[0]==[];tests+=1
 x=line('f1r',['a','@152;','b']);assert observations([x],cols)[0]==[]
 x=line('f1r',['a','zz','b']);x['groups'][1][1]='7';assert observations([x],cols)[0]==[]
 assert kind('alphabeta',['alpha','beta'])=='spacing' and kind('alpha',['alpha','beta'])=='echo' and kind('abcdef',['a','b'])=='nonshort'
 return {'recurrent_positive':1,'same_leaf_and_wrong_flanks':2,'separator_negatives':tests,'raw_annotation_and_index_negatives':2,'kind_cases':4}

def main():
 sp=E/'src/SPEC.json';spec=json.loads(sp.read_text());assert spec['flank_groups']==1 and spec['long_groups']==[2,3]
 for b in spec['input_bindings']:assert sha(ROOT/b['path'])==b['sha256']
 selectors=spec['discovery_selectors'];assert all(not p.startswith('f84') and int(leaf(p)[1:])%4==1 for p in selectors)
 command=['./vmanus-exp','query-tsv',spec['source_atlas'],'--selector','page']
 for p in selectors:command+=['--allow',p]
 command+=['--columns',','.join(spec['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
 run=subprocess.run(command,cwd=ROOT,capture_output=True,check=True)
 guard=json.loads((E/'artifacts/DISCOVERY_GUARD.json').read_text());assert hashlib.sha256(run.stdout).hexdigest()==guard['projection_sha256'] and command==guard['command']
 grouped=collections.defaultdict(dict);gcols=spec['group_columns'];mcols=[c for c in spec['columns'] if c not in gcols]
 for row in csv.DictReader(io.StringIO(run.stdout.decode()),delimiter='\t'):
  assert row['page'] in selectors and not row['page'].startswith('f84')
  ed=row['edition'];assert ed in spec['editions'];k=(row['page'],row['locus']);m={c:row[c] for c in mcols}
  rec=grouped[ed].setdefault(k,{'metadata':m,'groups':[]});assert rec['metadata']==m;rec['groups'].append([row[c] for c in gcols])
 packed={'group_columns':gcols,'readings':{}}
 for ed in spec['editions']:
  lines=[]
  for _,r in sorted(grouped[ed].items()):
   r['groups'].sort(key=lambda g:int(g[gcols.index('source_group_index')]));lines.append(r)
  packed['readings'][ed]=lines
 sourcepath=E/'artifacts/DISCOVERY_SOURCE.json';assert packed==json.loads(sourcepath.read_text())
 checks={};frozen={}
 for ed in spec['editions']:
  obs,raw,prose=observations(packed['readings'][ed],gcols);rr=rules(obs);actual=json.loads((E/'artifacts'/f'DISCOVERY_{ed}.json').read_text())
  assert obs==actual['observations'],(ed,'observations')
  assert rr==actual['rules'],(ed,'rules')
  frozen[ed]=[r for r in rr if r['qualified']]
  checks[ed]={'prose_lines':prose,'raw_windows':raw,**{'eligible_'+str(n):sum(len(o['middle'])==n for o in obs) for n in (1,2,3)},'cross_leaf_pairs':sum(len(c['pairs']) for r in rr for c in r['contexts']),'rules':len(rr),'proper_rules':sum(r['kind']=='proper' for r in rr),'recurrent_proper_rules':sum(r['kind']=='proper' and len(r['contexts'])>=2 for r in rr),'qualified_rules':len(frozen[ed])}
 assert all(not r for r in frozen.values())
 frozenpath=E/'artifacts/FROZEN_RULES.json';assert json.loads(frozenpath.read_text())==frozen
 lock=json.loads((E/'artifacts/RULE_LOCK.json').read_text());assert lock=={'rules_sha256':sha(frozenpath),'source_sha256':sha(sourcepath),'spec_sha256':sha(sp)}
 result=json.loads((E/'artifacts/RESULT.json').read_text());assert result['discovery']==checks and result['status']=='NO_RECURRENT_SHORT_LONG_RULE' and result['transfer_accessed'] is False
 out={'status':'PASS','validator_sha256':sha(Path(__file__)),'spec_sha256':sha(sp),'guarded_query_projection_sha256':hashlib.sha256(run.stdout).hexdigest(),'source_sha256':sha(sourcepath),'discovery':checks,'fixtures':invented(),'transfer_accessed_by_validator':False,'frozen_rules_empty':True,'claim_ceiling':'Exact literal same-flank substitutions and true cross-leaf supports independently replayed. No recurring proper shortening qualifies; no reserved transfer was accessed and no abbreviation or meaning is identified.','artifact_sha256':{n:sha(E/'artifacts'/n) for n in ['RESULT.json','FROZEN_RULES.json','RULE_LOCK.json']+[f'DISCOVERY_{ed}.json' for ed in spec['editions']]}}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
