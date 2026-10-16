"""Post-observation finite proof/source verification; no key fitting."""
import argparse,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/R_COMPLETE_UNITS.json'
DERIVATION='research_registry/proposals/production_origin_supply_20261003/C1064_DERIVATION_20261016.json'
ORIGINAL='research_registry/proposals/production_origin_supply_20261003/LEGAL_ACTION_MENU_WRITER_RAW_20261014.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(name,x):(B/'artifacts'/name).write_text(json.dumps(x,indent=2)+'\n')
def controls():
 machines=stable_count=checks=0
 for F in itertools.product(range(2),repeat=4):
  for T in itertools.product([False,True],repeat=4):
   machines+=1
   stable=all(not T[2*s+x] or T[2*F[2*s+x]+x] for s in range(2) for x in range(2))
   if not stable:continue
   stable_count+=1
   for s in range(2):
    for x in range(2):
     if T[2*s+x]:
      next_state=F[2*s+x]; assert T[2*next_state+x];checks+=1
 # Greedy stopping at initial x, then continuing x y, if stability is removed.
 F=[1,0,1,1];T=[True,True,False,True]
 assert T[0] and not T[2*F[0]] and T[3]
 # A stable machine permits x | x y only when the gap resets state0 to1.
 Fr=[0,0,1,1];Tr=[True,True,False,True]
 assert all(not Tr[2*s+x] or Tr[2*Fr[2*s+x]+x] for s in range(2) for x in range(2))
 assert Tr[0] and not Tr[2] and Tr[3]
 return {'status':'PASS','machines':machines,'stable_machines':stable_count,'stable_stop_checks':checks,'escapes':{'nonstable':{'F':F,'T':T,'initial_state':0,'word_signs':[[0],[0,1]],'boundary_reset':None},'boundary_reset':{'F':Fr,'T':Tr,'initial_state':0,'word_signs':[[0],[0,1]],'boundary_reset':1}}}
def parse(raw,signs):
 ways=[[] for _ in range(len(raw)+1)];ways[0]=[[]]
 for i in range(len(raw)):
  for prefix in ways[i]:
   for sign in signs:
    if raw.startswith(sign,i):ways[i+len(sign)].append(prefix+[sign])
 assert len(ways[-1])==1,(raw,len(ways[-1]));return ways[-1][0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--lock');a=ap.parse_args();fixture=controls()
 if a.controls:save('CONTROLS.json',fixture);print(json.dumps(fixture));return
 assert a.lock; lock=load(Path(a.lock)); pins=lock.get('hashes',{})
 for p,h in pins.items():assert sha(R/p)==h,p
 required=[SOURCE,DERIVATION,ORIGINAL,str(Path(__file__).resolve().relative_to(R))]
 assert all(p in pins for p in required)
 raw=load(R/ORIGINAL);master=raw['design']['shared_apparatus']['master_order'];assert len(master)==22
 states=[list(s) for s in itertools.product(range(6),repeat=5) if sum(s)==5];assert len(states)==126
 records=[];terms=set();moves=set()
 for state in states:
  k=sum(x>0 for x in state);menu=[a for a in master if a in ['WAIT','ROTATE'] or state[ord(a[0])-65]>0]
  for rank in range(22):
   legal=rank<len(menu); action=menu[rank] if legal else None; nxt=None;terminal=False;stable=None;nk=None
   if legal:
    nxt=state.copy();terminal=action in ['WAIT','ROTATE']
    if action=='ROTATE':nxt=[state[-1],*state[:-1]]
    elif action!='WAIT':nxt[ord(action[0])-65]-=1;nxt[ord(action[-1])-65]+=1
    nk=sum(x>0 for x in nxt);assert sum(nxt)==5 and min(nxt)>=0
    if terminal:
     terms.add(rank);newmenu=[a for a in master if a in ['WAIT','ROTATE'] or nxt[ord(a[0])-65]>0];stable=rank<len(newmenu) and newmenu[rank] in ['WAIT','ROTATE'];assert stable and nk==k
    else:moves.add(rank)
   records.append({'state':state,'rank':rank,'legal':legal,'action':action,'next_state':nxt,'terminal':terminal,'k':k,'next_k':nk,'stable':stable})
 transition={'states':states,'transitions':records,'terminal_ranks':sorted(terms),'dual_ranks':sorted(terms&moves)}
 source=load(R/SOURCE);deriv=load(R/DERIVATION);witness={}
 for unit in source['units']:
  reader=unit['edition'];line=next(x for x in unit['lines'] if x['metadata']['locus']=='f75v.48');groups=[g for g in line['groups'] if int(g[1]) in [6,7]]
  assert len(groups)==2 and [int(g[1]) for g in groups]==[6,7] and [g[2] for g in groups]==['saino','ol'];assert groups[0][4]==groups[1][3]=='DEFINITE_SPACE'
  parsed=[parse(g[2],deriv['signs']) for g in groups];assert parsed[0][-1]==parsed[1][0] and len(parsed[1])>1
  dr=[r for u in deriv['units'] if u['reader']==reader for r in u['rows'] if r['source_group_id'] in [g[0] for g in groups]]
  assert len(dr)==2 and [r['source_group'] for r in dr]==[dict(zip(unit['group_columns'],g)) for g in groups] and [r['units'] for r in dr]==parsed
  witness[reader]={'boundary_status':unit['boundary_status'],'metadata':line['metadata'],'groups':groups,'parses':parsed,'derivation_rows':dr,'violates_stable_stop':True}
 oldpath=next(R.glob('experiments/yolo/gdt1319*/artifacts/RESULT.json'));assert str(oldpath.relative_to(R)) in pins
 old=load(oldpath);ends={r:sum(x.startswith('O:') for x in v['active_nodes']) for r,v in old['readers'].items()};assert all(n>len(terms) for n in ends.values())
 result={'status':'STABLE_STOP_CONTRACT_EXCLUDED','states':len(states),'state_rank_cases':len(records),'legal_cases':sum(x['legal'] for x in records),'illegal_cases':sum(not x['legal'] for x in records),'terminal_cases':sum(x['terminal'] for x in records),'stable_terminal_cases':sum(x['stable'] is True for x in records),'terminal_ranks':sorted(terms),'dual_ranks':sorted(terms&moves),'inherited_active_end_counts':ends,'witness_readers':sorted(witness)}
 save('TRANSITIONS.json',transition);save('WITNESS.json',{'source':{'path':SOURCE,'sha256':sha(R/SOURCE)},'derivation':{'path':DERIVATION,'sha256':sha(R/DERIVATION)},'readers':witness});save('RESULT.json',result);save('CONTROLS.json',fixture);print(json.dumps(result))
if __name__=='__main__':main()
