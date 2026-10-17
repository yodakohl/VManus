#!/usr/bin/env python3
"""Finite shared SOURCE->unit tables on the exact old invariant core; no decoder."""
import argparse,concurrent.futures,gzip,hashlib,importlib.util,itertools,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def setup():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 s=read(E/'src/SPEC.json');sp=importlib.util.spec_from_file_location('fixed_selector',ROOT/s['selector_library']);lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib)
 return s,lib.kept

def sources(s):
 recipes=read(ROOT/s['recipe_path']);deot=read(ROOT/s['deot_path']);other=read(ROOT/s['other_path']);out={}
 for name in s['source_names']:
  if name in ('b4','w1','bs1','gr1'):out[name]=[w for r in recipes[name] for w in r['words']]
  elif name=='deot':out[name]=[w for r in deot['source_sections'] for w in r['words']]
  else:out[name]=[r['unit'] for r in other[name]['PRIMARY']['units']];assert len(out[name])==8000
 return out
class Limit(Exception):pass

def solve(groups,words,signs,mode,s):
 start=time.monotonic();nodes=0;checks=0;W=set(words);unique=sorted(set(map(tuple,groups)));tables=[]
 assert unique and mode in ('FWD','BIDIR')
 def tick(n=1):
  nonlocal checks
  checks+=n
  if checks>s['checks_cap']:raise Limit('CHECK_CAP')
  if time.monotonic()-start>s['seconds_per_case']:raise Limit('TIME_CAP')
 try:
  for group in unique:
   table={}
   for word in sorted(W):
    if len(word)!=len(group):continue
    for direction,oriented in [('FWD',word)]+([('REV',word[::-1])] if mode=='BIDIR' else []):
     tick();row={};ok=True
     for c,u in zip(oriented,group):
      if c in row and row[c]!=u:ok=False;break
      row[c]=u
     if ok:table.setdefault(tuple(sorted(row.items())),(word,direction))
   if not table:return {'status':'UNSAT','reason':'EMPTY_WORD_ROW_TABLE','nodes':nodes,'checks':checks,'units':list(group)}
   tables.append(table)
  failed=set()
  def visit(key,left,selected):
   nonlocal nodes
   tick(0)
   if nodes>=s['nodes_cap']:raise Limit('NODE_CAP')
   nodes+=1
   if not left:return key,selected
   state=(tuple(sorted(key.items())),left)
   if state in failed:return None
   best=None;options=None
   for i in left:
    valid=[]
    for row in tables[i]:
     tick()
     if all(c not in key or key[c]==u for c,u in row):valid.append(row)
    if not valid:failed.add(state);return None
    if options is None or len(valid)<len(options):best=i;options=valid
   rest=tuple(i for i in left if i!=best)
   for row in sorted(options):
    nextkey=dict(key);nextkey.update(row);choice=dict(selected);choice[best]=row
    answer=visit(nextkey,rest,choice)
    if answer is not None:return answer
   failed.add(state);return None
  answer=visit({},tuple(range(len(unique))),{})
  if answer is None:return {'status':'UNSAT','reason':'EXHAUSTIVE_FORWARD_TABLE_JOIN','nodes':nodes,'checks':checks}
  key,selected=answer
  for c in sorted(set(''.join(W))):key.setdefault(c,signs[0])
  words_out=[];directions=[];lookup={g:i for i,g in enumerate(unique)}
  for group in groups:
   i=lookup[tuple(group)];word,direction=tables[i][selected[i]];words_out.append(word);directions.append(direction)
   oriented=word if direction=='FWD' else word[::-1];assert [key[c] for c in oriented]==group and word in W
  return {'status':'SAT','key':key,'source_words':words_out,'directions':directions,'nodes':nodes,'checks':checks}
 except Limit as exc:return {'status':'UNKNOWN','reason':str(exc),'nodes':nodes,'checks':checks}

def controls():
 s={'seconds_per_case':3,'nodes_cap':10000,'checks_cap':1000000};count=0
 W0=['a','b','ab','aa']
 for mask in range(1,16):
  W=[w for i,w in enumerate(W0) if mask>>i&1];alpha=sorted(set(''.join(W)))
  for groups in [[['X']],[['Y']],[['X','Y']],[['X','X']],[['X'],['Y']],[['X','Y'],['Y','X']]]:
   for mode in ('FWD','BIDIR'):
    possible=False
    for vals in itertools.product('XY',repeat=len(alpha)):
     key=dict(zip(alpha,vals))
     if all(any([key[c] for c in w]==g or mode=='BIDIR' and [key[c] for c in w[::-1]]==g for w in W) for g in groups):possible=True;break
    r=solve(groups,W,list('XY'),mode,s);assert r['status']==('SAT' if possible else 'UNSAT');count+=1
 assert solve([['X','X']],['ab'],list('XY'),'FWD',s)['status']=='SAT'
 assert solve([['X','Y']],['aa'],list('XY'),'FWD',s)['status']=='UNSAT'
 assert solve([['X']],['a'],list('XY'),'FWD',dict(s,nodes_cap=0))['status']=='UNKNOWN'
 return {'status':'PASS','complete_small_function_cases':count,'merge_allowed_split_forbidden':True,'cap_unknown':True}

def gate(s,kept):
 old=read(ROOT/s['old_control']);assert old['status']=='PASS_EXACT_UNIQUE' and read(ROOT/s['old_control_validation'])['native_authorized']
 ids=[i for i,g in enumerate(old['encoded_groups']) if kept(g)];groups=[old['encoded_groups'][i] for i in ids];words=[old['source_words'][i] for i in ids];key=old['planted_key'];pairs=old['active_collision_pairs'];active=set(''.join(words))
 packet={'groups':groups,'selected_indices':ids,'source_words':words,'planted_key':key,'active_collision_pairs':pairs,'source_free_controls':controls(),'parent_control_sha256':sha(ROOT/s['old_control']),'lock_sha256':sha(E/'LOCK.json')}
 if len(set(map(tuple,groups)))<2 or any(not set(pair)<=active for pair in pairs):packet.update(status='STOP',reason='CONTROL_SUBSET_OR_COLLISIONS_ABSENT');save('CONTROL_SUBSET.json',packet);return
 assert [[key[c] for c in w] for w in words]==groups
 result=solve(groups,sources(s)['deot'],s['signs'],'FWD',s);packet.update(status='PASS' if result['status']=='SAT' else 'STOP',result=result)
 save('CONTROL_SUBSET.json',packet);print(json.dumps({'control':packet['status'],'selected':len(groups)}))
def job(args):
 name,mode,groups,W,s=args
 return {'source':name,'mode':mode,'result':solve(groups,W,s['signs'],mode,s)}
def native(s,kept):
 assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
 packet=read(ROOT/s['native_path']);original=packet['original_groups'];parsed=packet['original_units'];assert len(original)==len(parsed)==77
 ids=[i for i,g in enumerate(parsed) if kept(g)];groups=[parsed[i] for i in ids]
 old=read(ROOT/s['old_subset_result']);assert ids==old['positions_zero_based'] and groups==old['groups'] and original==old['original_groups'] and len(ids)==46
 W=sources(s);jobs=[(n,m,groups,W[n],s) for n in s['source_names'] for m in s['modes']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:cases=list(pool.map(job,jobs))
 save('RESULT.json',{'experiment_id':'GDT1421','status':'FORWARD_MERGER_INVARIANT_CORE_CAPACITY','original_groups':original,'original_units':parsed,'positions_zero_based':ids,'freed_positions':[i for i in range(77) if i not in ids],'groups':groups,'cases':cases,'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':s['claim_ceiling']})
 print(json.dumps({'cases':[(c['source'],c['mode'],c['result']['status']) for c in cases]}),flush=True)
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for mode in ('selftest','gate','native'):g.add_argument('--'+mode,action='store_true')
 a=p.parse_args()
 if a.selftest:print(json.dumps(controls()));return
 s,kept=setup()
 if a.gate:gate(s,kept)
 else:native(s,kept)
if __name__=='__main__':main()
