import argparse,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def reasons(a,b):
 out=[]
 if a[3] not in ['DEFINITE_SPACE','LINE_START']:out.append('TARGET_LEFT_BOUNDARY')
 if b is None:return out+['NO_FOLLOWER']
 if int(b[1])!=int(a[1])+1:out.append('INDEX_GAP')
 if a[4]!='DEFINITE_SPACE' or b[3]!='DEFINITE_SPACE':out.append('INTERNAL_SEAM')
 if b[4] not in ['DEFINITE_SPACE','LINE_END']:out.append('FOLLOWER_RIGHT_BOUNDARY')
 if re.fullmatch('[a-z]+',b[2]) is None:out.append('FOLLOWER_NOT_PLAIN_ASCII')
 return out
def follower_state(a,b):
 eligible=not reasons(a,b)
 return eligible,bool(eligible and b[2].startswith('qo'))
def controls():
 a=['id','2','qo','DEFINITE_SPACE','DEFINITE_SPACE'];b=['next','3','qokain','DEFINITE_SPACE','LINE_END'];assert follower_state(a,b)==(True,True);assert follower_state(a,[*b[:2],'daiin',*b[3:]])==(True,False)
 for x in [None,['n','4','qokain','DEFINITE_SPACE','LINE_END'],['n','3','qokain','UNCERTAIN_SMALL_SPACE','LINE_END'],['n','3','q@168;','DEFINITE_SPACE','LINE_END']]:assert follower_state(a,x)==(False,False)
 assert follower_state(a,['n','3','qo','DEFINITE_SPACE','LINE_END'])==(True,True)
 assert follower_state(['id','2','qo','UNKNOWN','DEFINITE_SPACE'],b)==(False,False)
 assert follower_state(a,['n','3','qokain','DEFINITE_SPACE','UNKNOWN'])==(False,False)
 assert ('x.1',2,'daiin')!=('x.1',3,'daiin') and 'qo'!='qoo';return dict(status='PASS')
def derive(s,data):
 occurrences=[];known={};summary={};keys={}
 for ed,source in data.items():
  assert source['group_columns']==s['group_columns'];assert len({line['metadata']['locus'] for line in source['lines']})==len(source['lines']), 'Duplicate locus records';known[ed]=[];local=[]
  for line in source['lines']:
   m=line['metadata'];assert m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84') and m['edition']==ed
   if m['locus']==s['exposed_locus']:known[ed].append(line)
   if m['kind']!='P':continue
   for i,g in enumerate(line['groups']):
    if g[2]!='qo':continue
    b=line['groups'][i+1] if i+1<len(line['groups']) else None;eligible,echo=follower_state(g,b);local.append(dict(edition=ed,line=line,group=g,follower=b,eligible=eligible,echo=echo,ineligibility_reasons=reasons(g,b),coordinate=[m['locus'],int(g[1]),b[2]] if b else None))
  occurrences.extend(local);summary[ed]=dict(occurrences=len(local),eligible=sum(x['eligible'] for x in local),echo=sum(x['echo'] for x in local),non_echo=sum(x['eligible'] and not x['echo'] for x in local),unscorable=sum(not x['eligible'] for x in local),exposed_line_count=len(known[ed]));keys[ed]={tuple(x['coordinate']) for x in local if x['eligible']}
 common=sorted(set.intersection(*keys.values()));negative=[list(k) for k in common if not k[2].startswith('qo')];r=dict(status='STRICT_ECHO_COUNTEREXAMPLE' if negative else 'NO_ALL_READER_HARD_COUNTEREXAMPLE',summary=summary,all_reader_eligible_coordinates=[list(k) for k in common],all_reader_non_echo_coordinates=negative,known_locus=s['exposed_locus'])
 return occurrences,known,r
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.controls:(E/'artifacts/CONTROLS.json').write_text(enc(controls()));print('CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());data={}
 for ed,q in s['sources'].items():
  raw=(ROOT/q['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==q['sha256'];data[ed]=json.loads(raw)
 occ,known,r=derive(s,data)
 for n,v in [('OCCURRENCES.json',occ),('EXPOSED_LINES.json',known),('RESULT.json',r)]:
  p=E/'artifacts'/n
  if a.check:assert p.read_text()==enc(v)
  else:p.write_text(enc(v))
 print(enc(r))
if __name__=='__main__':main()
