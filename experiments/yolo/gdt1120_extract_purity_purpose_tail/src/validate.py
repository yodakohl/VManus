"""Independent mechanical reconstruction; never semantic validation."""
import json, hashlib, csv, io
from pathlib import Path
H=Path(__file__).resolve().parents[1]
R=H.parents[2]
def j(p):return json.loads((H/p).read_text())
def main():
 m=j('src/MODEL.json')
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h, p
 parent=json.loads((R/'experiments/yolo/gdt1119_preparation_residue_predicate/src/MODEL.json').read_text())['models']['S']['dictionary']
 assert len(parent)==29 and parent==m['parent_dictionary']
 new={'chcthy':'drug-extract','lchedy':'purified','qokaly':'into-basin'}
 assert m['models']['G']['dictionary']=={**parent,**new}
 assert m['models']['I']['dictionary']=={**parent,**new,'lchedy':'purification-intended'}
 assert all(len(v['dictionary'])==32 for v in m['models'].values())
 assert [w for w in m['models']['G']['dictionary'] if m['models']['G']['dictionary'][w]!=m['models']['I']['dictionary'][w]]==['lchedy']
 assert m['select_any_exact']==['chcthy','lchedy','qokaly'] and m['editions']==['ZL3b','IT2a']
 assert set(m['sealed'])=={'f84','f84r'} and m['semantic_selection'] is None and m['confirmed_words']==m['independent_meaning_capacity']==0
 assert m['semantic_validation'] is False
 assert m['finite_construction']['exact']==['dal','chedy']
 cache=json.loads((R/m['source']).read_text());us=[]
 # Selector fields are checked before any paragraph content is examined.
 for e in ['ZL3b','IT2a']:
  for u in cache[e]:
   if u['page'].startswith('f84') or u['page']=='f116v':continue
   if u['id'] in m['include_paragraphs'] or any(w in {'chcthy','lchedy','qokaly'} for l in u['lines'] for w in l['words']):us.append({'edition':e,**u})
 assert us==j('src/SOURCE.json')['units'], 'native source selection differs'
 for e in m['editions']:
  assert set(m['include_paragraphs'])<=set(u['id'] for u in us if u['edition']==e)
 expected=[];targets=[];expected_graphs=[];reader=(H/'artifacts/FULL_READER.md').read_text()
 for u in us:
  assert u['edition']+' '+u['id'] in reader
  seq=[w for l in u['lines'] for w in l['words']];ids=[sid for l in u['lines'] for sid in l['source_ids']];i=0
  assert u['groups']==len(seq)
  for l in u['lines']:
   assert len(l['words'])==len(l['source_ids'])
   assert '### '+l['locus'] in reader
   assert 'RAW: `'+ ' '.join(l['words'])+'`' in reader
   assert 'IDS: `'+ ' '.join(l['source_ids'])+'`' in reader
   rendered={}
   for c,v in m['models'].items():
    vals=[]
    for k,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
     ctor=seq[i+k:i+k+2]==['dal','chedy'];val='NOT' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧');vals.append(val)
     expected.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':k+1,'source_id':sid,'raw':w,'value':val,'lexical':w in v['dictionary'],'construction_only':ctor,'scope_source_id':ids[i+k+1] if ctor else None})
    assert c+': '+' '.join(vals) in reader
    rendered[c]=vals
   for k,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
    if w in {'chcthy','lchedy','qokaly'}:targets.append({'edition':u['edition'],'paragraph':u['id'],'form':w,'locus':l['locus'],'position':k+1,'source_id':sid,'raw_words':l['words'],'source_ids':l['source_ids'],'renderings':rendered})
   i+=len(l['words'])
 assert expected==j('artifacts/ALIGNMENT.json'), 'constant reader / unknown / finite DAL mismatch'
 assert targets==j('artifacts/TARGET_OCCURRENCES.json')
 table=list(csv.reader(io.StringIO((H/'artifacts/CANDIDATE_TABLE.tsv').read_text()),delimiter='\t'))
 assert table==[['raw','parent_1119_S','G','I','status']]+[[w,parent.get(w,'UNASSIGNED'),m['models']['G']['dictionary'][w],m['models']['I']['dictionary'][w],'C0_UNCONFIRMED'] for w in sorted(m['models']['G']['dictionary'])]
 graphs=j('artifacts/GRAPHS.json');eg=[]
 for u in us:
  for l in u['lines']:
   if l['locus'] not in m['focal_loci']:continue
   ids=l['source_ids'];loc=l['locus']
   rendered={c:[x['value'] for x in expected if x['candidate']==c and x['edition']==u['edition'] and x['paragraph']==u['id'] and x['locus']==loc] for c in ['G','I']}
   g={'edition':u['edition'],'paragraph':u['id'],'locus':loc,'raw_words':l['words'],'source_ids':ids,'renderings':rendered,'binding_status':'ASSUMED_NOT_INDEPENDENTLY_BOUND'}
   if loc=='f77r.26':
    assert l['words']==['qoteedy','qokeedy','qokaiin','chcthy','lchedy','qokaly']
    roles={role:ids[pos-1] for role,pos in m['focal26']['roles'].items()}
    edges=[{'from':roles[x],'to':roles[y],'role':x+'_'+y,'status':'ASSUMED'} for x,y in m['focal26']['assumed_edges']]
    g.update(proposed=m['focal26'],whole_line_hypothesis=True,roles=roles,edges=edges,genitive_direction='FORWARD_TO_EXTRACT_LOCAL_ONLY',identity_with25='UNBOUND')
   else:
    core=m['other_cores'][loc];pos=core['groups'];assert pos==([3,4,5,6] if loc=='f80r.30' else [4,5,6])
    roles={'subject':ids[pos[0]-1],'copula':ids[pos[1]-1],'complement':ids[pos[2]-1]}
    assert l['words'][pos[0]-1]=='chcthy' and l['words'][pos[1]-1]=='qokain'
    edges=[{'from':roles['copula'],'to':roles['subject'],'role':'subject','status':'ASSUMED'},{'from':roles['copula'],'to':roles['complement'],'role':'property_or_material_complement','status':'ASSUMED'}]
    if loc=='f80r.30':
     assert l['words'][4:6]==['shedy','okaiin'];roles['liquid_compound_member']=ids[5]
     edges.append({'from':ids[5],'to':ids[4],'role':'reverse_exact_material_preparation_compound','status':'ASSUMED'})
    if loc=='f111v.39':assert l['words'][5]=='chedy'
    if loc=='f80r.14':assert l['words'][5]=='qotchy' and 'property not identity copula' in core['assumptions']
    g.update(proposed=core,whole_line_hypothesis=False,core_positions=pos,roles=roles,edges=edges,outside_core_source_ids=[sid for k,sid in enumerate(ids,1) if k not in pos])
   eg.append(g)
  if u['page']=='f104r':eg.append({'edition':u['edition'],'paragraph':u['id'],'flow_carrier':'UNBOUND','identity_status':'NOT_INDEPENDENTLY_BOUND','old1117_failure':'RETAINED_NOT_RERUN_NOT_REPAIRED'})
 assert eg==graphs, 'full local graph reconstruction'
 assert {(g['edition'],g['locus']) for g in graphs if 'locus' in g}=={(e,l) for e in m['editions'] for l in m['focal_loci']}
 r=j('artifacts/RESULT.json')
 assert r['native_units']==len(us) and r['raw_groups']==sum(u['groups'] for u in us) and r['alignments']==len(expected)
 assert r['units_by_edition']=={e:sum(u['edition']==e for u in us) for e in m['editions']}
 assert r['selected_paragraph_ids']=={e:[u['id'] for u in us if u['edition']==e] for e in m['editions']}
 assert r['finite_adjacent_negation_occurrences']==sum(x['construction_only'] for x in expected if x['candidate']=='G')
 profilepath=next(p for p in m['input_hashes'] if p.endswith('EL_CONTINUATION_PROFILES.json'))
 profile=json.loads((R/profilepath).read_text())
 assert set(r['target_coverage'])==set(m['select_any_exact'])
 for form,coverage in r['target_coverage'].items():
  prof=next(p for p in profile['profiles'] if p['form']==form)
  assert set(coverage)==set(prof['editions'])
  for e,v in coverage.items():
   stat=prof['editions'][e]
   assert v['global_179_selector_count']==stat['count']
   assert v['global_P_count']==next(x['count'] for x in stat['strata']['kind'] if x['value']=='P')
   assert v['selected_complete_native_P_count']==sum(t['edition']==e and t['form']==form for t in targets)
   assert v['unscored_global_count']==stat['count']-v['selected_complete_native_P_count']
   if e=='RF1b':assert v['selected_complete_native_P_count']==0 and v['reason']=='RF_NO_NATIVE_PARAGRAPH_CACHE'
 assert r['target_occurrences']==len(targets) and r['contradictions']=='NOT_INDEPENDENTLY_SCORABLE'
 assert r['semantic_validation'] is False and r['grammar_success'] is None and r['significance'] is False
 assert r['costs']['G_obligation']=='prior purification operation on same material assumed not observed'
 assert r['costs']['I_obligation']=='purification purpose assumed, completion and impurity not asserted'
 assert r['parent_branch']=='1119S extension only; H unresolved unselected'
 assert r['semantic_selection'] is None and r['confirmed_words']==0 and r['independent_meaning_capacity']==0
 out={'status':'PASS','scope':'frozen hashes, 29 parent values, 32 value G/I dictionaries, exact native union selection, all source IDs/raw groups/reader values, adjacent finite NEG, seven retained parent paragraphs and profile-derived coverage, all target positions; RF not native','semantic_validation':False,'contradictions_scorable':False,'semantic_selection':None,'confirmed_words':0,'independent_meaning_capacity':0,'native_units':len(us),'target_occurrences':len(targets),'prior_purification_or_purpose_independently_observed':False,'universal_identity_test_imposed':False,'raw_groups':r['raw_groups'],'alignment_rows':len(expected)}
 (H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
