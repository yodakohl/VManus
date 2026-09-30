"""Separate reconstruction of exact source, tuples and exploratory rendering."""
import json,hashlib,itertools,csv,io
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def j(p):return json.loads((H/p).read_text())
def main():
 m=j('src/MODEL.json')
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 old=json.loads((R/'experiments/yolo/gdt932_joint_flow_participant_reading/src/MODEL.json').read_text())['models']
 base=json.loads((R/'experiments/yolo/gdt1117_purification_operation_efficacy/src/MODEL.json').read_text())['candidates']['EFF']['dictionary']
 for c in ['M','V']:
  expected={**base,**{w:m['source_concept_map'][v[0]] for w,v in old[c]['lexicon'].items()}};assert expected==m['models'][c]['dictionary']
 n={**base,**{w:m['source_concept_map'][v[0]] for w,v in old['V']['lexicon'].items()}};n.update(shedy='moist-preparation',qokeedy='flows',otedy='mouth',qotedy='from-mouth');assert n==m['models']['N']['dictionary']
 for w,v in base.items():assert n[w]==v
 cache=json.loads((R/m['source']).read_text());us=[]
 for e in m['editions']:
  for wanted in m['paragraphs']:
   hits=[u for u in cache[e] if u['id']==wanted];assert len(hits)==1;us.append({'edition':e,**hits[0]})
 assert us==j('src/SOURCE.json')['units'];assert len(us)==10
 expected=[];reader=(H/'artifacts/FULL_READER.md').read_text()
 for u in us:
  seq=[w for l in u['lines'] for w in l['words']];i=0;assert u['edition']+' '+u['id'] in reader
  for l in u['lines']:
   assert l['locus']+' RAW: `'+ ' '.join(l['words'])+'`' in reader
   for c,v in m['models'].items():
    vals=[]
    for k,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
     ctor=seq[i+k:i+k+2]==['dal','chedy'];val='NOT(scope-next-chedy)_C0' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧');vals.append(val)
     expected.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':k+1,'source_id':sid,'raw':w,'value':val,'lexical':w in v['dictionary'],'construction_only':ctor})
    assert c+': '+' '.join(vals) in reader
   i+=len(l['words'])
 assert expected==j('artifacts/ALIGNMENT.json')
 table=list(csv.reader(io.StringIO((H/'artifacts/CANDIDATE_TABLE.tsv').read_text()),delimiter='\t'))
 expected_table=[['raw','1117EFF','M','V','N']]+[[w,base.get(w,'UNASSIGNED')]+[m['models'][c]['dictionary'].get(w,'UNASSIGNED') for c in ['M','V','N']] for w in sorted(set().union(*(set(v['dictionary']) for v in m['models'].values())))]
 assert table==expected_table
 comp=j('artifacts/DICTIONARY_COMPARISON.json')
 for x in comp['pairs']:
  a,b=x['left'],x['right'];da=m['models'][a]['dictionary'];db=m['models'][b]['dictionary'];diff=[{'raw':w,a:da[w],b:db[w]} for w in sorted(set(da)&set(db)) if da[w]!=db[w]];assert x['incompatible_shared_values']==diff and x['unchanged_shared_dictionary_compatible']==(not diff)
 assert comp['EFF_parent_overrides']['N']=={} and set(comp['EFF_parent_overrides']['M'])=={'okaiin'} and set(comp['EFF_parent_overrides']['V'])=={'qokeedy'}
 graphs=j('artifacts/GRAPHS.json')
 for g in graphs:
  if 'raw' in g:
   l=next(l for u in us if u['edition']==g['edition'] for l in u['lines'] if l['locus']==g['locus']);assert g['raw']==l['words'] and g['source_ids']==l['source_ids'] and g['interpretation']==m['focal_graphs'][g['locus']]
   if g['locus']=='f77r.27':assert g['N_subject_ids']==l['source_ids'][2:4] and g['N_flow_id']==l['source_ids'][4] and g['N_source_id']==l['source_ids'][5]
  if 'N_possible_nominal_mentions' in g:
   u=next(u for u in us if u['edition']==g['edition'] and u['id']==g['paragraph']);heads=[{'raw':w,'source_id':sid} for l in u['lines'] for w,sid in zip(l['words'],l['source_ids']) if w in m['N_nominal_candidates']];assert g['N_possible_nominal_mentions']==heads and g['N_flow_carrier']=='UNBOUND'
 r=j('artifacts/RESULT.json');assert r['native_units']==len(us) and r['raw_groups']==sum(u['groups'] for u in us) and r['alignments']==len(expected) and r['physical_leaves']==[77,104,115]
 for l,v in r['focal_N_ZL'].items():
  a=[x for x in expected if x['candidate']=='N' and x['edition']=='ZL3b' and x['locus']==l];assert v=={'assigned':sum(x['lexical'] for x in a),'raw':len(a)}
 assert r['focal_N_ZL']['f77r.27']=={'assigned':6,'raw':6} and r['focal115_N_assigned']=={'ZL3b':15,'IT2a':15}
 assert r['counter104_N_possible_nominal_mentions']=={'ZL3b':0,'IT2a':0} and r['semantic_selection'] is None and r['confirmed_words']==0
 out={'status':'PASS','scope':'hashes, parent tuples, explicit overrides, exact complete source, every constant assignment, finite NEG, raw focal graphs, comparison and counts','semantic_validation':False,'units':len(us),'raw_groups':r['raw_groups'],'alignment_rows':len(expected)};(H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
