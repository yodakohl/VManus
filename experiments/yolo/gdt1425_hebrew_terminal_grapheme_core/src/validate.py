#!/usr/bin/env python3
"""Independent final-grapheme projection, certificates, and pinned old DFS."""
import argparse,concurrent.futures,copy,hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,'No changed-result overwrite '+n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load(path,name):
 z=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);return m

def setup():
 s=read(E/'src/SPEC.json');lock=read(E/'LOCK.json');pins=lock['files']
 if isinstance(pins,dict):
  for p,h in pins.items():assert sha(ROOT/p)==h,p
 else:
  for p in pins:assert sha(ROOT/p['path'])==p['sha256'],p['path']
 for p,h in s['input_sha256'].items():assert sha(ROOT/p)==h,p
 return s

def final_word(w,mp):
 assert isinstance(w,str) and w
 chars=list(w);chars[-1]=mp.get(chars[-1],chars[-1]);return ''.join(chars)
def inverse(w,mp):return ''.join({v:k for k,v in mp.items()}.get(c,c) for c in w)
def fixtures():
 mp=dict(zip('כמנפצ','ךםןףץ'));count=0
 for base,final in mp.items():
  for w in [base,'א'+base,base+'א',base+base]:
   out=final_word(w,mp);assert inverse(out,mp)==w and out[:-1]==w[:-1]
   assert out[-1]==(final if w[-1]==base else w[-1]);count+=1
 assert final_word('אמ',mp)[::-1]=='םא' and final_word('אמ'[::-1],mp)=='מא';count+=1
 return count

def rendered(s):
 assert (s['source_tokens'],s['source_sections'],s['base_alphabet_count'],s['rendered_alphabet_count'])==(6288,71,22,27)
 orig=read(ROOT/s['source_path']);sections=copy.deepcopy(orig['source_sections']);mp=s['final_map'];assert mp==dict(zip('כמנפצ','ךםןףץ'))
 oldwords=[w for sec in sections for w in sec['words']]
 for sec in sections:
  for i,w in enumerate(sec['words']):
   assert inverse(w,mp)==w,'Input must be folded'
   sec['words'][i]=final_word(w,mp);assert inverse(sec['words'][i],mp)==w
 words=[w for sec in sections for w in sec['words']]
 assert len(words)==len(oldwords)==6288 and len(sections)==71
 oldalpha=sorted(set(''.join(oldwords)));alpha=sorted(set(''.join(words)));assert len(oldalpha)==22 and len(alpha)==27
 got=read(A/'RENDERED_SOURCE.json')
 assert got['source_sha256']==sha(ROOT/s['source_path']) and got['final_map']==mp
 assert got['sections']==sections and got['tokens']==6288
 assert got['old_unique_words']==len(set(oldwords)) and got['new_unique_words']==len(set(words))
 assert got['base_alphabet']==oldalpha and got['rendered_alphabet']==alpha
 return sorted(set(words))

def cert(r,groups,W,signs,mode):
 assert r['status']=='SAT';key=r['key'];words=r.get('words',r.get('source_words'));directions=r['directions']
 assert set(key)==set(''.join(W)) and all(v in signs for v in key.values())
 assert len(words)==len(directions)==len(groups)
 for w,d,g in zip(words,directions,groups):
  assert w in W and d in (['FWD'] if mode=='FWD' else ['FWD','REV'])
  text=w if d=='FWD' else w[::-1];assert [key[c] for c in text]==g


def gate(write=True):
 s=setup();W=rendered(s);g=read(A/'CONTROL.json');parent=read(ROOT/s['parent_control']);prior=read(ROOT/s['parent_control_subset'])
 canon=parent['source_words'];assert len(canon)==32 and canon==prior['source_words']
 ws=[final_word(w,s['final_map']) for w in canon]
 key=dict(parent['planted_key'])
 for base,final in s['final_map'].items():key[final]=next(u for u in s['signs'] if u not in ['e','i','y'] and u!=key[base])
 encoded=[[key[c] for c in w] for w in ws]
 assert g['canonical_source_words']==canon and g['rendered_source_words']==ws and g['planted_key']==key and g['encoded_groups']==encoded
 distinct_groups_ok=len(set(map(tuple,encoded)))>=2
 def keep(us):return bool(us) and not any(a==b and a in ('e','i') for a,b in zip(us,us[1:])) and us[-2:]!=['d','y']
 all_kept=all(keep(us) for us in encoded)
 assert g['all32_kept']==all_kept
 active=set(''.join(ws));pairs=[(base,final) for base,final in s['final_map'].items() if base in active and final in active and key[base]!=key[final]]
 domain_valid=distinct_groups_ok and all_kept and bool(pairs)
 check_activity_schema(g,s,active,key,pairs)
 cert({'status':'SAT','key':key,'words':ws,'directions':['FWD']*32},encoded,set(W),s['signs'],'FWD')
 assert g['result']['status'] in ['SAT','UNKNOWN'],'Known positive cannot be UNSAT'
 if not domain_valid:
  assert g['status']=='STOP' and g['result']['status']=='UNKNOWN'
  assert g['result']['reason']=='CONTROL_FINAL_DOMAIN_OR_PREDICATE_ABSENT'
  assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 elif g['result']['status']=='SAT':cert(g['result'],encoded,set(W),s['signs'],'FWD');assert g['status']=='PASS'
 else:
  assert g['status']=='STOP'
  assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 check_control_pins(g,s)
 out={'status':g['status'],'control_sha256':sha(A/'CONTROL.json'),'rendered_source_sha256':sha(A/'RENDERED_SOURCE.json'),'lock_sha256':sha(E/'LOCK.json'),'spec_sha256':sha(E/'src/SPEC.json'),'validator_sha256':sha(Path(__file__)),'source_tokens':6288,'source_sections':71,'base_alphabet_size':22,'rendered_alphabet_size':27,'control_groups':32,'control_domain_valid':domain_valid,'all32_kept':all_kept,'at_least_two_distinct_groups':distinct_groups_ok,'active_final_pairs':[list(p) for p in pairs],'synthetic_rule_checks':fixtures(),'scope':'Source rendering and ANY-key certificate only; no recovery of original orthography or word meaning. All five rules tested, not all five claimed active in control.'}
 if write:save('GATE_VALIDATION.json',out)
 return out

def worker(job):
 mode,groups,W,signs,caps,path,pin=job;assert sha(ROOT/path)==pin
 m=load(path,'exact1421dfs');return {'mode':mode,'result':m.solve(groups,W,signs,mode,caps)}
def native():
 s=setup();assert gate(False)==read(A/'GATE_VALIDATION.json');assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
 assert not (A/'INDEPENDENT_RESULT.json').exists(),'No search rerun'
 v=load(s['old_source_validator'],'oldsource');old=read(ROOT/s['old1421spec']);rows,units,ids=v.native_packet(old);groups=[units[i] for i in ids];assert len(ids)==46
 caps=s['search']['old_dfs'];assert all(caps[k]==old[k] for k in ['seconds_per_case','nodes_cap','checks_cap']);assert s['signs']==old['signs'] and s['modes']==old['modes']
 W=rendered(s);jobs=[(mode,groups,W,s['signs'],caps,s['dfs_engine'],s['input_sha256'][s['dfs_engine']]) for mode in s['modes']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(2,s['search']['workers'])) as ex:cases=list(ex.map(worker,jobs))
 for c in cases:
  if c['result']['status']=='SAT':cert(c['result'],groups,set(W),s['signs'],c['mode'])
 save('INDEPENDENT_RESULT.json',{'source':'deot_final5','cases':cases,'positions_zero_based':ids,'groups':groups,'original_groups':rows,'original_units':units,'engine':'Pinned unchanged1421 rowDFS','validator_sha256':sha(Path(__file__)),'lock_sha256':sha(E/'LOCK.json')})
 print(json.dumps([(c['mode'],c['result']['status']) for c in cases]))
def validate():
 s=setup();g=gate(False);assert g==read(A/'GATE_VALIDATION.json')
 if g['status']!='PASS':save('VALIDATION.json',{'status':'PASS_CONTROL_STOP_ACCOUNTING','gate':g,'native_executed':False});return
 v=load(s['old_source_validator'],'oldsource');rows,units,ids=v.native_packet(read(ROOT/s['old1421spec']));groups=[units[i] for i in ids];W=set(rendered(s));a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json')
 for r in [a,b]:
  assert r['source']=='deot_final5' and r['positions_zero_based']==ids and r['groups']==groups
  if 'original_groups' in r:assert r['original_groups']==rows
  if 'original_units' in r:assert r['original_units']==units
 check_result_pins(a,s)
 aa={c['mode']:c['result'] for c in a['cases']};bb={c['mode']:c['result'] for c in b['cases']};assert len(a['cases'])==len(b['cases'])==2 and set(aa)==set(bb)==set(s['modes']);decisions=[]
 for mode in s['modes']:
  ra,rb=aa[mode],bb[mode];sa,sb=ra['status'],rb['status'];assert sa in ['SAT','UNSAT','UNKNOWN'] and sb in ['SAT','UNSAT','UNKNOWN']
  for r in [ra,rb]:
   if r['status']=='SAT':cert(r,groups,W,s['signs'],mode)
  assert {sa,sb}!={'SAT','UNSAT'},'Solver disagreement'
  effective='SAT_CAPACITY_ONLY' if 'SAT' in [sa,sb] else 'UNSAT_BOTH' if sa==sb=='UNSAT' else 'UNKNOWN_OPEN'
  decisions.append({'mode':mode,'boolean':sa,'row_dfs':sb,'effective':effective})
 save('VALIDATION.json',{'status':'PASS_INDEPENDENT_RENDER_CERTIFICATES_AND_DFS_COMPARISON','cases':decisions,'source_tokens':6288,'source_sections':71,'positions':46,'validator_sha256':sha(Path(__file__)),'primary_sha256':sha(A/'RESULT.json'),'independent_sha256':sha(A/'INDEPENDENT_RESULT.json'),'limits':['Canonical finalization of a bare edition, not original historical orthography.','SAT preimages are structural witnesses, not translations; UNKNOWN remains open; UNSAT only both engines.','No primary wrapper/compiler import; old source parser and DFS explicitly reused unchanged.']})
 print(json.dumps(decisions))
# Serialization adapters completed from root-declared schema before lock, no primary code read.
def check_activity_schema(g,s,active,key,pairs):
 expected=[{'base':base,'final':final,'base_occurs':base in active,'final_occurs':final in active,'contrast_active':base in active and final in active and key[base]!=key[final],'base_unit':key[base],'final_unit':key[final]} for base,final in s['final_map'].items()]
 assert g['active_final_pairs']==expected
def check_control_pins(g,s):
 assert g['parent_control_sha256']==sha(ROOT/s['parent_control'])
 assert g['rendered_source_sha256']==sha(A/'RENDERED_SOURCE.json')
 assert g['lock_sha256']==sha(E/'LOCK.json')
def check_result_pins(g,s):
 assert g['status']=='FINAL5_FIXED_CORE_CASES'
 assert g['source_sha256']==sha(A/'RENDERED_SOURCE.json')
 assert g['core_sha256']==sha(ROOT/s['core_path'])
 assert g['lock_sha256']==sha(E/'LOCK.json')
 assert g['witness_status']=='UNASSESSED_SOURCE_PREIMAGES_NOT_WORD_ASSIGNMENTS'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.gate:print(json.dumps(gate()))
 elif a.native:native()
 elif a.validate or a.check:validate()
 else:p.error('choose --gate,--native,--validate/--check')
