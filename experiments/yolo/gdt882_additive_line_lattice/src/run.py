#!/usr/bin/env python3
import argparse,collections,hashlib,importlib.util,json,re
from pathlib import Path
from algebra import analyze,selftest
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
p=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py'
s=importlib.util.spec_from_file_location('source829',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
def compact(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 lock=json.loads((E/'src/PREREG_LOCK.json').read_text())
 for name,digest in lock.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 fixtures=selftest()
 spec=json.loads((E/'src/SPEC.json').read_text());rows,guard=h.query(spec);records=h.records(rows)
 loci=sorted({loc for ed,loc in records});selected=[];rejected=[]
 for loc in loci:
  rr=[records.get((ed,loc)) for ed in spec['editions']];reason=None
  if any(r is None for r in rr):reason='MISSING_ALTERNATE_LOCUS'
  elif any(r['kind']!='P' for r in rr):reason='NON_PROSE'
  elif any(not re.fullmatch(spec['literal_pattern'],g['ivtff_group_raw']) for r in rr for g in r['groups']):reason='NON_LITERAL_OR_UNCERTAIN_CHARACTER'
  elif any(g['right_separator'] not in spec['allowed_internal_separators'] for r in rr for g in r['groups'][:-1]):reason='DRAWING_OR_OTHER_GAP'
  elif len({''.join(g['ivtff_group_raw'] for g in r['groups']) for r in rr})!=1:reason='ALTERNATE_STRING_DISAGREEMENT'
  if reason:rejected.append([loc,reason]);continue
  selected.append(dict(locus=loc,page=rr[0]['page'],literal=''.join(g['ivtff_group_raw'] for g in rr[0]['groups']),readings=[dict(edition=r['edition'],source_group_ids=[g['source_group_id'] for g in r['groups']],groups=[g['ivtff_group_raw'] for g in r['groups']],internal_separators=[g['right_separator'] for g in r['groups'][:-1]]) for r in rr]))
 assert selected,'No eligible source lines: input/capacity stop, not contradiction'
 selected.sort(key=lambda r:(hashlib.sha256((spec['order_salt']+':'+r['locus']).encode()).hexdigest(),r['locus']))
 alphabet=sorted(set(''.join(r['literal'] for r in selected)))
 vectors=[[r['literal'].count(c) for c in alphabet] for r in selected]
 differences=[[x-y for x,y in zip(v,vectors[0])] for v in vectors[1:]]
 lattice=analyze(differences,len(alphabet))
 status='NO_NONZERO_FIXED_ADDITIVE_LINE_INVARIANT' if lattice['unit_lattice'] else 'NONTRIVIAL_QUOTIENT_UNINTERPRETED'
 result=dict(status=status,alphabet=alphabet,eligible_lines=len(selected),physical_leaves=len({re.match(r'f(\d+)',r['page'])[1] for r in selected}),queried_selectors=len(spec['allowed_selectors']),rejections=dict(collections.Counter(reason for loc,reason in rejected)),reference_locus=selected[0]['locus'],lattice=lattice,guard=guard,fixtures=fixtures,claim_ceiling='Exact fixed literal-character whole-line mechanism only; no error-tolerant/stateful/positional/nonlinear code verdict or meaning.')
 artifacts={'SELECTED_LINES.json':selected,'EXCLUSIONS.json':rejected,'RESULT.json':result}
 for name,obj in artifacts.items():
  data=compact(obj);p=E/'artifacts'/name
  if a.check:assert p.read_text()==data,name
  else:p.write_text(data)
 print(compact({k:v for k,v in result.items() if k not in ['guard','lattice']}));print(compact({k:v for k,v in lattice.items() if k not in ['basis','coefficients']}))
if __name__=='__main__':main()
