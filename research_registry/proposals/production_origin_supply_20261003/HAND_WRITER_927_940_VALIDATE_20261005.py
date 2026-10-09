"""Check exact retained witnesses and fixed logical bounds, not native atoms."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify_locked(c):
 for path,h in c['files'].items():assert sha(ROOT/path)==h,path
c=load(P/'HAND_WRITER_IDEA927_CONTRACT_20261005.json');r=load(P/'HAND_WRITER_IDEA927_RESULT_20261005.json');verify_locked(c)
assert sha(P/'HAND_WRITER_IDEA927_CONTRACT_20261005.json')==r['contract_sha256'] and sha(P/'HAND_WRITER_IDEA927_BIND_20261005.py')==r['runner_sha256']
D=ROOT/'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery';hits=load(D/'artifacts/HITS.json');spec=load(D/'src/SPEC.json')
assert [a['form'] for a in r['anchors']]==c['target_forms'];initials=set()
for a in r['anchors']:
 assert a['status']=='BOUND' and len(a['form'])>1
 assert {x['edition'] for x in a['readings']}==set(c['editions'])
 for x in a['readings']:
  assert x['hit'] in hits and x['hit']['period']==1 and x['hit']['groups']==[a['form']]*2
  source=load(D/f'artifacts/SOURCE_{x["edition"]}.json');line=source['lines'][x['hit']['line_array_index']]
  assert line['metadata']==x['metadata'];m=line['metadata'];assert m['locus']==a['locus'] and m['page'] in spec['allowed_selectors'] and not m['page'].startswith('f84')
  gs=[dict(zip(source['group_columns'],v)) for v in line['groups']];assert gs==x['groups'];i,j=x['target_array_indices'];assert j==i+1
  assert [gs[z]['source_group_id'] for z in [i,j]]==x['hit']['source_ids']
  assert [int(gs[z]['source_group_index']) for z in [i,j]]==[a['start_index'],a['start_index']+1]
  assert gs[i]['right_separator']==gs[j]['left_separator']=='DEFINITE_SPACE'
  if i:assert gs[i-1]['right_separator']==gs[i]['left_separator']=='DEFINITE_SPACE'
  else:assert gs[i]['left_separator']=='LINE_START'
  if j<len(gs)-1:assert gs[j]['right_separator']==gs[j+1]['left_separator']=='DEFINITE_SPACE'
  else:assert gs[j]['right_separator']=='LINE_END'
 assert a['literal_initial']==a['form'][0];initials.add(a['literal_initial'])
assert sorted(initials)==r['distinct_literal_initials'] and len(initials)>1
# General proof, not finite testing: length n=k+|rest|>k, for k<4 implies min(4,n)>k;
# for k=4, min(4,n)=4. Literal strings of length>=2 require a header on repetition.
assert r['status']=='LITERAL_ATOM_PREFIX_COPY_CONTRADICTED' and r['literal_atom_binding_assumed'] and not r['native_atoms_proven']
c2=load(P/'HAND_WRITER_IDEA940_CONTRACT_20261005.json');r2=load(P/'HAND_WRITER_IDEA940_RESULT_20261005.json');verify_locked(c2)
assert sha(P/'HAND_WRITER_IDEA940_CONTRACT_20261005.json')==r2['contract_sha256'] and sha(P/'HAND_WRITER_IDEA940_BOUND_20261005.py')==r2['runner_sha256']
book=load(P/'HUMAN_SOURCE_EIGHT_FRAGMENT_CACHE_RAW_20261005.json')['design']['concrete_carrier'];alphabet=set(book['working_glyphs']);assert len(alphabet)==22 and set(r2['working_inventory'])==alphabet
assert r2['original_final_markers']==[book['end_sign'],book['continue_sign']] and len(set(r2['original_final_markers']))==2
lines=load(ROOT/'experiments/yolo/gdt1208_f45r_repeated_dal_body/artifacts/TARGET_LINES.json');forced=set()
for a in r2['anchors']:
 form=a['form'];reachable=[set() for _ in range(len(form)+1)];reachable[0].add(())
 for end in range(1,len(form)+1):
  for atom in alphabet:
   start=end-len(atom)
   if start>=0 and form[start:end]==atom:
    reachable[end].update(prefix+(atom,) for prefix in reachable[start])
 assert reachable[-1]=={tuple(p) for p in a['all_working_glyph_parses']}
 tails={p[-1] for p in reachable[-1]};assert tails==set(a['possible_terminal_glyphs']) and len(tails)==1;forced|=tails
 assert len(a['source_groups'])==3
 for g in a['source_groups']:
  line=next(l for l in lines if l['edition']==g['edition']);assert line['locus']==c2['locus'] and g in line['groups'] and g['ivtff_group_raw']==form
  assert c2['targets'][g['source_group_id'].split('|')[-1]]==form
assert forced==set(r2['forced_target_terminals'])=={'y','r','l'}
# Independent capacity check over possible unordered images of the two roles.
assert not any(forced<={a,b} for a in alphabet for b in alphabet if a!=b)
assert r2['status']=='FIXED_WORKING_INVENTORY_TWO_TERMINALS_CONTRADICTED' and r2['fixed_bijective_relabeling_also_excluded'] and r2['reset_independent'] and not r2['native_atom_binding_proven']
assert r['meanings_assigned']==r2['native_meanings_assigned']==0
assert not any(x['new_manuscript_discovery'] or x['new_frequency_census'] for x in [r,r2])
out={'status':'PASS','scope':'Pinned prior source bytes, exact whole-group/seam provenance, fixed result binding and terminal capacity; mathematical proof reviewed separately by bounded producer','same_author_software':True,'native_atom_or_meaning_validation':False,'idea927_status':r['status'],'idea940_status':r2['status'],'validator_sha256':sha(Path(__file__)),'result_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [P/'HAND_WRITER_IDEA927_RESULT_20261005.json',P/'HAND_WRITER_IDEA940_RESULT_20261005.json']}}
(P/'HAND_WRITER_927_940_VALIDATION_20261005.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
