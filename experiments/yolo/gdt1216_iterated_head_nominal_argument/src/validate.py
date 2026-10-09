#!/usr/bin/env python3
"""Independently bounded short nominal grammar; old parser/runner not imported."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 s=json.loads((ROOT/'experiments/yolo/gdt1214_short_square_fixed_grammar/src/SPEC.json').read_text());own=json.loads((D/'src/SPEC.json').read_text());out=json.loads((A/'RESULT.json').read_text())
 # Complete nominal core words of length <=2. Productive unary nominal adds
 # one sign to a >=2-sign core; binary adds one plus two such cores. A nonempty
 # literal costs >=3; a tagged or unpacked bare constructor cannot cost2.
 short={tuple(r['glyphs']) for r in s['roots'] if r['arity']==0}|{tuple(r) for r in s['references'] if len(r)<=2}
 assert all(len(w)==2 for w in short)
 assert sorted(map(list,short))==out['two_sign_nominal_initials'] and len(short)==18
 codes=[('f','e'),('f','i'),('ch','a'),('ch','o'),('ch','e'),('ch','i'),('sh','e'),('sh','i')]
 assert len(codes)==8 and set(codes).isdisjoint(short)
 roots={tuple(r['glyphs']):r['arity'] for r in s['roots']};assert all(roots[c]>0 for c in codes)
 assert {tuple(c['head_glyphs']) for c in out['cells']}==set(codes)
 for c in out['cells']:
  code=tuple(c['head_glyphs']);assert c['arity']==roots[code] and c['teaching_head'] in own['repeatable_heads'] and c['following_B_starts_nominal']==(code in short)
 prior=json.loads((ROOT/'experiments/yolo/gdt1214_short_square_fixed_grammar/artifacts/RESULT.json').read_text())
 assert len(prior['grid'])==462 and all(not c['double_readable'] for c in prior['grid'])
 assert out['ordered_pairs']==462 and out['old_readable_square_pairs']==0 and out['new_repeatable_pairs']==8 and out['compatible_typed_pairs']==0
 context=json.loads((ROOT/'experiments/yolo/gdt1215_paragraph_local_iteration_arity/artifacts/RETAINED_CONTEXTS.json').read_text());raw={r['source_group_id']:r for line in context['occurrence_lines'] for r in line}
 assert len(out['bindings'])==3
 for b in out['bindings']:
  x,y=b['doubled'],b['following_base'];assert x==raw[x['source_group_id']] and y==raw[y['source_group_id']]
  assert x['edition']==y['edition']==b['edition'] and x['locus']==y['locus']=='f79r.17'
  assert x['ivtff_group_raw']==y['ivtff_group_raw']*2 and y['ivtff_group_raw']=='ol'
  assert x['left_separator']==x['right_separator']==y['left_separator']=='DEFINITE_SPACE' and y['right_separator']=='LINE_END'
  assert int(y['source_group_index'])==int(x['source_group_index'])+1
 assert out['status']=='ITERATED_HEAD_NOMINAL_ARGUMENT_CONTRADICTED' and not out['paragraph_closure_assumed']
 report={'status':'PASS','short_nominal_initials':len(short),'eligible_repeated_heads':len(codes),'intersection':0,'native_bindings':3,'old_square_cells_verified':462,'runner_or_old_parser_imported':False,'native_meaning_validation':False,'completed_utc':datetime.now(timezone.utc).isoformat()}
 (A/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
