#!/usr/bin/env python3
"""Injective mechanical role-lift of the unchanged word inventory; no search."""
from pathlib import Path
import json,hashlib
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((E/'src/SPEC.json').read_text())
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 source=json.loads((ROOT/s['source_projection']).read_text());alpha=source['alphabet'];assert len(alpha)==23 and len(source['words'])==2133
 ls=[{'source_letter':c,'INITIAL':chr(0xE000+2*j),'REST':chr(0xE001+2*j)} for j,c in enumerate(alpha)];D={d['source_letter']:d for d in ls}
 def lift(w):return ''.join(D[c]['INITIAL' if i==0 else 'REST'] for i,c in enumerate(w))
 pairs=[[w,lift(w)] for w in source['words']];W=sorted(v for _,v in pairs);assert len(set(W))==2133
 obj={'status':'MECHANICAL_POSITION_LIFT_NOT_NEW_SOURCE_LETTERS','source_projection_sha256':sha(ROOT/s['source_projection']),'letter_lift':ls,'pairs':pairs,'words':W,'alphabet':sorted(set(''.join(W))),'roles':'position0 INITIAL; everylaterposition REST; singleton INITIAL','source_words':2133,'source_letters':23}
 p=ROOT/s['role_projection'];assert not p.exists();p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print({'words':len(W),'active_context_labelled_values':len(obj['alphabet'])})
if __name__=='__main__':main()
