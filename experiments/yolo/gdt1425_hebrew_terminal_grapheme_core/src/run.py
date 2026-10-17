#!/usr/bin/env python3
"""Fixed canonical final shapes; unchanged Boolean capacity engine."""
from pathlib import Path
import json,hashlib,importlib.util,argparse
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d):
 p=A/name;assert not p.exists(),'Refuse overwrite '+name;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def load(path):
 sp=importlib.util.spec_from_file_location('frozen_boolean',ROOT/path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def render(w,m):
 assert w;return w[:-1]+m.get(w[-1],w[-1])
def keep(g):return bool(g) and not any(a==b and a in ['e','i'] for a,b in zip(g,g[1:])) and g[-2:]!=['d','y']
def selftest():
 m={'כ':'ך','מ':'ם','נ':'ן','פ':'ף','צ':'ץ'};fold=str.maketrans({v:k for k,v in m.items()})
 for b,f in m.items():
  assert render(b+b,m)==b+f and render(b,m)==f and render(b+'א',m)==b+'א'
  assert render(b+b,m).translate(fold)==b+b
 assert render('כמ',m)[::-1]=='םכ' and render('מכ',m)!='םכ'
 return {'status':'PASS_FIVE_TERMINAL_SHAPE_FIXTURES','rules':5,'inverse_fold':True,'orientation_after_render':True,'scope':'Source-free engineering, not native evidence or all-five control activity.'}
def setup():
 s=read(E/'src/SPEC.json')
 for p,h in s['input_sha256'].items():assert sha(ROOT/p)==h,p
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 return s

def source(s):
 old=read(ROOT/s['source_path']);sections=[];before=[];after=[];fold=str.maketrans({f:b for b,f in s['final_map'].items()})
 for section in old['source_sections']:
  words=section['words'];assert all(w and not set(w)&set(s['final_map'].values()) for w in words)
  new=[render(w,s['final_map']) for w in words];assert [w.translate(fold) for w in new]==words
  sections.append({**section,'words':new});before+=words;after+=new
 assert len(sections)==s['source_sections'] and len(before)==len(after)==old['tokens']==s['source_tokens']
 assert len(set(before))==len(set(after))
 ba=sorted(set(''.join(before)));ga=sorted(set(''.join(after)));assert len(ba)==s['base_alphabet_count'] and len(ga)==s['rendered_alphabet_count']
 return {'source_sha256':sha(ROOT/s['source_path']),'final_map':s['final_map'],'sections':sections,'tokens':len(after),'old_unique_words':len(set(before)),'new_unique_words':len(set(after)),'base_alphabet':ba,'rendered_alphabet':ga}
def gate(s):
 data=source(s);save('RENDERED_SOURCE.json',data);W=sorted({w for sec in data['sections'] for w in sec['words']})
 parent=read(ROOT/s['parent_control']);subset=read(ROOT/s['parent_control_subset']);assert parent['status']=='PASS_EXACT_UNIQUE' and len(parent['source_words'])==32
 canonical=parent['source_words'];assert canonical==subset['source_words'];ws=[render(w,s['final_map']) for w in canonical];assert all(w in W for w in ws)
 key=dict(parent['planted_key']);assert set(key)==set(data['base_alphabet'])
 for b,f in s['final_map'].items():key[f]=next(u for u in s['signs'] if u not in ['e','i','y',key[b]])
 groups=[[key[c] for c in w] for w in ws];active=set(''.join(ws));pairs=[{'base':b,'final':f,'base_occurs':b in active,'final_occurs':f in active,'contrast_active':b in active and f in active and key[b]!=key[f],'base_unit':key[b],'final_unit':key[f]} for b,f in s['final_map'].items()]
 valid=all(map(keep,groups)) and len(set(map(tuple,groups)))>=2 and any(p['contrast_active'] for p in pairs)
 packet={'canonical_source_words':canonical,'rendered_source_words':ws,'encoded_groups':groups,'planted_key':key,'active_final_pairs':pairs,'all32_kept':all(map(keep,groups)),'parent_control_sha256':sha(ROOT/s['parent_control']),'rendered_source_sha256':sha(A/'RENDERED_SOURCE.json'),'lock_sha256':sha(E/'LOCK.json')}
 if not valid:
  packet.update(status='STOP',result={'status':'UNKNOWN','reason':'CONTROL_FINAL_DOMAIN_OR_PREDICATE_ABSENT'});save('CONTROL.json',packet);print(json.dumps({'gate':'STOP','reason':packet['result']['reason']}));return
 # No planted key or aligned plaintext enters this unchanged solver.
 engine=load(s['boolean_engine']);r=engine.solve(groups,W,s['signs'],'FWD',s['search']);packet.update(status='PASS' if r['status']=='SAT' else 'STOP',result=r);save('CONTROL.json',packet);print(json.dumps({'gate':packet['status'],'result_status':r['status'],'stats':r.get('stats',{}),'active_final_pairs':pairs}),flush=True)
def native(s):
 gate=read(A/'GATE_VALIDATION.json');assert gate['status']=='PASS' and gate['control_sha256']==sha(A/'CONTROL.json') and gate['rendered_source_sha256']==sha(A/'RENDERED_SOURCE.json')
 data=read(A/'RENDERED_SOURCE.json');assert data==source(s);W=sorted({w for sec in data['sections'] for w in sec['words']});core=read(ROOT/s['core_path']);groups=core['groups'];ids=core['positions_zero_based'];assert len(groups)==len(ids)==46
 engine=load(s['boolean_engine']);cases=[{'mode':mode,'result':engine.solve(groups,W,s['signs'],mode,s['search'])} for mode in s['modes']]
 save('RESULT.json',{'status':'FINAL5_FIXED_CORE_CASES','source':'deot_final5','cases':cases,'positions_zero_based':ids,'groups':groups,'source_sha256':sha(A/'RENDERED_SOURCE.json'),'core_sha256':sha(ROOT/s['core_path']),'lock_sha256':sha(E/'LOCK.json'),'witness_status':'UNASSESSED_SOURCE_PREIMAGES_NOT_WORD_ASSIGNMENTS'});print(json.dumps([(c['mode'],c['result']['status']) for c in cases]),flush=True)
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for n in ['selftest','gate','native']:g.add_argument('--'+n,action='store_true')
 a=p.parse_args()
 if a.selftest:print(json.dumps(selftest()));return
 s=setup()
 if a.gate:gate(s)
 else:native(s)
if __name__=='__main__':main()
