import hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(name,obj):(B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
def controls():
 fs=list(itertools.product([0,1],repeat=2));n=0
 for a,b in itertools.product(fs,repeat=2):assert len({(a[z],b[z]) for z in [0,1]})<=2;n+=1
 updates=0
 for a,b,t,u in itertools.product(fs,repeat=4):
  # u is the post-second-word state update: it cannot alter emitted trace.
  traces={(a[z],b[t[z]]) for z in [0,1]};endstates={u[t[z]] for z in [0,1]}
  assert len(traces)<=2 and len(endstates)<=2;updates+=1
 for ca,cb in itertools.product([0,1],repeat=2):assert len({(z^ca)^(z^cb) for z in [0,1]})==1
 return {'shared_emission_tables':n,'emission_transition_tables':updates,'bijective_class_pairs':4}
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 src=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts';out={'scope':'Exposed cardinality bound, no significance or meaning','readers':{},'controls':controls()};witness={}
 for reader in ['ZL3b','IT2a','RF1b']:
  old=json.loads((src/f'EVALUATION_{reader}.json').read_text());rows=[]
  for row in old['candidates']:
   c=row['cells'];occupied=sum(v>0 for v in c.values());both=all([c['rr']+c['rl'],c['lr']+c['ll'],c['rr']+c['lr'],c['rl']+c['ll']])
   rows.append({'stems':row['stems'],'cells':c,'occupied_cells':occupied,'two_state_compatible':occupied<=2,'both_slots_vary':bool(both),'occurrences':row['occurrences']})
  raw=json.loads((src/f'SOURCE_EVALUATION_{reader}.json').read_text());by={x['metadata']['locus']:x for x in raw['lines']};target=next(x for x in rows if x['stems']==['qoka','o'])
  witness[reader]=[{'occurrence':o,'raw_line':by[o['locus']]} for o in target['occurrences']]
  out['readers'][reader]={'families':len(rows),'occupied_cell_lower_bound':max(x['occupied_cells'] for x in rows),'incompatible_families':[x['stems'] for x in rows if not x['two_state_compatible']],'both_variable_families':sum(x['both_slots_vary'] for x in rows),'both_variable_occurrences':sum(sum(x['cells'].values()) for x in rows if x['both_slots_vary']),'rows':rows}
 out['status']='FIXED_INPUT_BINARY_STATE_EXCLUDED' if out['readers']['ZL3b']['incompatible_families'] else 'NO_CAPACITY_CONTRADICTION'
 save('RESULT',out);save('QOKA_O_RAW_LINES',witness)
 print(json.dumps({r:{k:v for k,v in x.items() if k!='rows'} for r,x in out['readers'].items()},indent=2))
if __name__=='__main__':main()
