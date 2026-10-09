#!/usr/bin/env python3
import hashlib,importlib.util,json
from itertools import permutations
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';P=ROOT/'research_registry/proposals/production_origin_supply_20261003'
def main():
 start=datetime.now(timezone.utc).isoformat()
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 spec=importlib.util.spec_from_file_location('old_grammar',P/'B6_7_PRODUCTIVE_STEMS.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 heads=json.loads((D/'src/SPEC.json').read_text())['repeatable_heads']
 action={tuple(g.tokenize(g.LEX[n]['code'])):n for n in heads}
 nominal={tuple(g.noun_core(g.N(n))) for n in g.NOUNS|set(g.REF) if len(g.noun_core(g.N(n)))==2}
 prior=json.loads((ROOT/'experiments/yolo/gdt1214_short_square_fixed_grammar/artifacts/RESULT.json').read_text());assert prior['double_readable_pairs']==0
 cells=[];bad=[]
 for a,b in permutations(g.GLYPHS,2):
  pair=(a,b)
  if pair not in action:continue
  n=action[pair];arity=g.LEX[n]['arity'];assert arity in (1,2)
  allowed=pair in nominal
  cells.append({'head_glyphs':list(pair),'teaching_head':n,'arity':arity,'following_B_starts_nominal':allowed})
  if allowed:bad.append(pair)
 ctx=json.loads((ROOT/'experiments/yolo/gdt1215_paragraph_local_iteration_arity/artifacts/RETAINED_CONTEXTS.json').read_text());bindings=[]
 for line in ctx['occurrence_lines']:
  if line[0]['locus']!='f79r.17':continue
  x,y=line[-2:];assert [x['ivtff_group_raw'],y['ivtff_group_raw']]==['olol','ol']
  assert x['left_separator']==x['right_separator']==y['left_separator']=='DEFINITE_SPACE' and y['right_separator']=='LINE_END'
  assert int(y['source_group_index'])==int(x['source_group_index'])+1
  bindings.append({'edition':x['edition'],'doubled':x,'following_base':y})
 assert {x['edition'] for x in bindings}=={'ZL3b','IT2a','RF1b'}
 result={'experiment':'GDT1216','status':'ITERATED_HEAD_NOMINAL_ARGUMENT_CONTRADICTED' if not bad else 'SHORT_TYPED_PATH_EXISTS','ordered_pairs':len(g.GLYPHS)*(len(g.GLYPHS)-1),'old_readable_square_pairs':prior['double_readable_pairs'],'new_repeatable_pairs':len(cells),'two_sign_nominal_initials':sorted(map(list,nominal)),'compatible_typed_pairs':len(bad),'cells':cells,'bindings':bindings,'paragraph_closure_assumed':False,'claim_ceiling':'Only unchanged947 with global22-sign bijection, preserved groups, strict nominal arguments and explicit prefix order; no native values or general repetition rejection.'}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(A/'RUN_RECEIPT.json').write_text(json.dumps({'started_utc':start,'completed_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('cells','bindings','two_sign_nominal_initials')},indent=2))
if __name__=='__main__':main()
