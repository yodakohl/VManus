import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 src=R/'experiments/yolo/gdt1260_lr_line_margin_capacity/artifacts';ts=json.loads((src/'TOKENS.json').read_text());ps=json.loads((src/'PAIRS.json').read_text())
 old=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts';nom=json.loads((old/'CANDIDATES.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());w=json.loads((B/'artifacts/QOKA_O_RAW_LINES.json').read_text());counts={}
 for reader,tokens in ts.items():
  pairs=ps[reader];raw=json.loads((old/f'SOURCE_EVALUATION_{reader}.json').read_text());lines={x['metadata']['locus']:x for x in raw['lines']}
  assert all(not x['metadata']['page'].startswith('f84') and x['metadata']['page']!='f116v' for x in raw['lines'])
  r=result['readers'][reader];assert [x['stems'] for x in r['rows']]==nom
  occupied=[];incompatible=[];both=0;both_n=0;verified=0
  for row in r['rows']:
   sub=[p for p in pairs if p['stems']==row['stems']];c=collections.Counter();identities=[]
   for p in sub:
    a,b=[tokens[p[k]] for k in ['a','b']];c[a['ending']+b['ending']]+=1
    line=lines[p['locus']];g={z[0]:z for z in line['groups']};ga,gb=[g[s] for s in p['source_ids']]
    assert [ga[2],gb[2]]==[a['word'],b['word']];assert int(gb[1])==int(ga[1])+1 and ga[4]==gb[3]=='DEFINITE_SPACE'
    identities.append((tuple(p['source_ids']),tuple([a['word'],b['word']])));verified+=1
   assert c==collections.Counter({k:v for k,v in row['cells'].items() if v})
   assert sorted(identities)==sorted((tuple(o['source_ids']),tuple(o['words'])) for o in row['occurrences'])
   n=len(c);occupied.append(n);assert row['occupied_cells']==n and row['two_state_compatible']==(n<=2)
   if n>2:incompatible.append(row['stems'])
   varying=len({s[0] for s in c})==2 and len({s[1] for s in c})==2;assert row['both_slots_vary']==varying
   both+=varying;both_n+=len(sub) if varying else 0
  assert (r['occupied_cell_lower_bound'],r['incompatible_families'],r['both_variable_families'],r['both_variable_occurrences'])==(max(occupied),incompatible,both,both_n)
  target=next(x for x in r['rows'] if x['stems']==['qoka','o']);assert len(w[reader])==len(target['occurrences'])
  for x,o in zip(w[reader],target['occurrences']):assert x['occurrence']==o and x['raw_line']==lines[o['locus']]
  counts[reader]={'families':len(r['rows']),'source_bound_occurrences':verified,'raw_qoka_o_lines':len(w[reader]),'status':'PASS'}
 # Independently cardinality-check every function from two inputs to four traces.
 maps=[(a,b) for a in range(4) for b in range(4)];assert len(maps)==16 and all(len(set(m))<=2 for m in maps)
 assert result['status']=='FIXED_INPUT_BINARY_STATE_EXCLUDED' and result['controls']=={'shared_emission_tables':16,'emission_transition_tables':256,'bijective_class_pairs':4}
 out={'status':'PASS','readers':counts,'proof':'Two inputs have at most two distinct output traces; independent16-map enumeration. Native counts verified from1260and exact915raw IDs/seams.','limits':'Exposed transcription-based contract check; no common linguistic construction, actual states, image reading or meaning established.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
