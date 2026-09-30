"""Independent mechanical reconstruction; never semantic validation."""
import json, hashlib, csv, io
from pathlib import Path
H=Path(__file__).resolve().parents[1]
R=H.parents[2]
def j(p):return json.loads((H/p).read_text())
def main():
 m=j('src/MODEL.json')
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h, p
 parent=json.loads((R/'experiments/yolo/gdt1118_liquid_preparation_joint_reading/src/MODEL.json').read_text())['models']['N']['dictionary']
 assert len(parent)==26 and parent==m['parent_dictionary']
 new={'qokal':'in-basin','shedar':'deposits','daror':'residue'}
 assert m['models']['S']['dictionary']=={**parent,**new}
 assert m['models']['H']['dictionary']=={**parent,**new,'shedar':'contains'}
 assert all(len(v['dictionary'])==29 for v in m['models'].values())
 assert [w for w in m['models']['S']['dictionary'] if m['models']['S']['dictionary'][w]!=m['models']['H']['dictionary'][w]]==['shedar']
 assert m['select_any_exact']==['qokal','shedar','daror'] and m['editions']==['ZL3b','IT2a']
 assert set(m['sealed'])=={'f84','f84r'} and m['semantic_selection'] is None and m['confirmed_words']==m['independent_meaning_capacity']==0
 assert m['finite_construction']['exact']==['dal','chedy']
 cache=json.loads((R/m['source']).read_text());us=[]
 # Selector fields are checked before any paragraph content is examined.
 for e in ['ZL3b','IT2a']:
  for u in cache[e]:
   if u['page'].startswith('f84') or u['page']=='f116v':continue
   if u['id'] in m['include_paragraphs'] or any(w in {'qokal','shedar','daror'} for l in u['lines'] for w in l['words']):us.append({'edition':e,**u})
 assert us==j('src/SOURCE.json')['units'], 'native source selection differs'
 for e in m['editions']:
  assert set(m['include_paragraphs'])<=set(u['id'] for u in us if u['edition']==e)
  daror={l['locus'] for u in us if u['edition']==e for l in u['lines'] if 'daror' in l['words']}
  assert daror=={'f18v.8','f77r.25','f85r1.14'}, daror
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
    if w in {'qokal','shedar','daror'}:targets.append({'edition':u['edition'],'paragraph':u['id'],'form':w,'locus':l['locus'],'position':k+1,'source_id':sid,'raw_words':l['words'],'source_ids':l['source_ids'],'renderings':rendered})
   if l['locus'] in ['f77r.25','f77r.26']:
    negs=[{'source_id':x['source_id'],'scope_source_id':x['scope_source_id']} for x in expected if x['candidate']=='S' and x['edition']==u['edition'] and x['paragraph']==u['id'] and x['locus']==l['locus'] and x['construction_only']]
    expected_graphs.append({'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'raw_words':l['words'],'source_ids':l['source_ids'],'renderings':rendered,'proposed':m['focal_core' if l['locus']=='f77r.25' else 'focal_continuation'],'finite_negations':negs,'binding_status':'ASSUMED_NOT_INDEPENDENTLY_BOUND'})
   i+=len(l['words'])
  if u['page']=='f104r':expected_graphs.append({'edition':u['edition'],'paragraph':u['id'],'flow_carrier':'UNBOUND','identity_status':'NOT_INDEPENDENTLY_BOUND','old1117_failure':'RETAINED_NOT_RERUN_NOT_REPAIRED'})
 assert expected==j('artifacts/ALIGNMENT.json'), 'constant reader / unknown / finite DAL mismatch'
 assert targets==j('artifacts/TARGET_OCCURRENCES.json')
 table=list(csv.reader(io.StringIO((H/'artifacts/CANDIDATE_TABLE.tsv').read_text()),delimiter='\t'))
 assert table==[['raw','parent_N','S','H','status']]+[[w,parent.get(w,'UNASSIGNED'),m['models']['S']['dictionary'][w],m['models']['H']['dictionary'][w],'C0_UNCONFIRMED'] for w in sorted(m['models']['S']['dictionary'])]
 for g in expected_graphs:
  if 'locus' not in g:continue
  ids=g['source_ids']
  if g['locus']=='f77r.25':
   g['proposed_roles']={'subject':ids[2],'location':ids[3],'predicate':ids[4],'negation':ids[5],'quality':ids[6],'object':ids[7],'outside_core':ids[:2]}
   g['proposed_edges']=[{'from':ids[4],'to':ids[2],'role':'subject'},{'from':ids[4],'to':ids[7],'role':'object'},{'from':ids[3],'to':ids[2],'role':'location_assumed'},{'from':ids[5],'to':ids[6],'role':'finite_exact_negation'},{'from':ids[6],'to':ids[7],'role':'quality_attachment_assumed'}]
  else:
   g['proposed_roles']={'portion':ids[0],'flow_predicate':ids[1],'of_liquid':ids[2],'unread_tail':ids[3:]}
   g['proposed_edges']=[{'from':ids[1],'to':ids[0],'role':'flow_carrier_assumed'},{'from':ids[2],'to':ids[0],'role':'genitive_back_attachment_assumed'}]
   g['identity_with_25_preparation']='UNBOUND'
 assert expected_graphs==j('artifacts/GRAPHS.json'), 'focal/counter graph conservation'
 for g in j('artifacts/GRAPHS.json'):
  u=next(u for u in us if u['edition']==g['edition'] and u['id']==g['paragraph'])
  if 'locus' in g:
   l=next(l for l in u['lines'] if l['locus']==g['locus']);assert g['raw_words']==l['words'] and g['source_ids']==l['source_ids']
   for c in ['S','H']:assert g['renderings'][c]==[x['value'] for x in expected if x['candidate']==c and x['edition']==g['edition'] and x['paragraph']==g['paragraph'] and x['locus']==g['locus']]
   assert g['proposed']==m['focal_core' if g['locus']=='f77r.25' else 'focal_continuation']
   assert g['binding_status']=='ASSUMED_NOT_INDEPENDENTLY_BOUND'
  else:assert g['flow_carrier']=='UNBOUND'
 r=j('artifacts/RESULT.json')
 assert r['native_units']==len(us) and r['raw_groups']==sum(u['groups'] for u in us) and r['alignments']==len(expected)
 assert r['units_by_edition']=={e:sum(u['edition']==e for u in us) for e in m['editions']}
 assert r['selected_paragraph_ids']=={e:[u['id'] for u in us if u['edition']==e] for e in m['editions']}
 assert r['daror_complete_native_paragraphs']=={e:[u['id'] for u in us if u['edition']==e and any(w=='daror' for l in u['lines'] for w in l['words'])] for e in m['editions']}
 assert r['finite_adjacent_negation_occurrences']==sum(x['construction_only'] for x in expected if x['candidate']=='S')
 for form,coverage in r['target_coverage'].items():
  for e,v in coverage.items():
   assert v['selected_complete_native_P_count']==sum(t['edition']==e and t['form']==form for t in targets)
   assert v['unscored_global_count']==v['global_179_selector_count']-v['selected_complete_native_P_count']
   if e=='RF1b':assert v['selected_complete_native_P_count']==0 and v['reason']=='RF_NO_NATIVE_PARAGRAPH_CACHE'
 assert r['target_occurrences']==len(targets) and r['contradictions']=='NOT_INDEPENDENTLY_SCORABLE'
 assert r['semantic_selection'] is None and r['confirmed_words']==0 and r['independent_meaning_capacity']==0
 out={'status':'PASS','scope':'frozen hashes, 26 parent values, 29 value S/H dictionaries, exact native union selection, all source IDs/raw groups/reader values, adjacent finite NEG, three DAROR contexts, all target positions; RF not native','semantic_validation':False,'contradictions_scorable':False,'semantic_selection':None,'confirmed_words':0,'independent_meaning_capacity':0,'native_units':len(us),'raw_groups':r['raw_groups'],'alignment_rows':len(expected)}
 (H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
