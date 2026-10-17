#!/usr/bin/env python3
"""Bind original words to reversed views and reverse control UNIT lists only."""
from pathlib import Path
import json,hashlib
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 assert not p.exists(),str(p);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 s=read(E/'src/SPEC.json')
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 data=read(ROOT/s['source_projection']);W=data['words'];pairs=[[w,w[::-1]] for w in W];views=sorted(w for _,w in pairs)
 assert len(W)==len(set(views))==2133 and sorted(set(''.join(views)))==data['alphabet'] and all(a==b[::-1] and len(a)==len(b) for a,b in pairs)
 save(ROOT/s['direction_projection'],{'status':'REVERSED_VIEW_OF_UNCHANGED_WORDS_NOT_NEW_ORTHOGRAPHY','pairs':pairs,'words':views,'alphabet':data['alphabet'],'source_projection_sha256':sha(ROOT/s['source_projection']),'original_words':2133,'source_letters':23,'direction':'GLOBAL_REVERSE'})
 old=read(ROOT/s['control_input']);groups=[list(reversed(g)) for g in old['groups']]
 assert [[old['planted_key'][c] for c in w[::-1]] for w in old['planted_words']]==groups
 # Multicharacter working units stay intact: raw EVA character reversal differs.
 original=['ch','y','cth'];rev=list(reversed(original));assert rev==['cth','y','ch'] and ''.join(rev)!=''.join(original)[::-1]
 save(ROOT/s['reverse_control_input'],{'direction':'GLOBAL_REVERSE','source_words':old['planted_words'],'planted_key':old['planted_key'],'groups':groups,'parent_control_sha256':sha(ROOT/s['control_input']),'working_unit_reversal_fixture':{'original':original,'reversed':rev,'raw_character_reversal_wrong':True},'scope':'Same original32sourcewords andkey, globallymirroredoutputgroups; no meaning or unique recovery.'})
 print(json.dumps({'source_words':len(views),'reversed_control_groups':len(groups),'working_units_preserved':True}))
if __name__=='__main__':main()
