"""Frozen whole-paragraph conditional spelling test; no meaning fitting."""
import argparse, collections, hashlib, itertools, json, math, re
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
BETA=math.log(3); LN2=math.log(2)
def save(name,value):
 (E/'artifacts'/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
def partition(us,counts,lengths):
 forms=sorted(counts); target=tuple(counts[f] for f in forms); states={(0,)*len(forms):0.0}
 for u in us:
  nxt={}
  for state,mass in states.items():
   for j,form in enumerate(forms):
    if state[j]==target[j]:continue
    key=state[:j]+(state[j]+1,)+state[j+1:]; term=mass-BETA*u*lengths[form]
    nxt[key]=float(np.logaddexp(nxt.get(key,-math.inf),term))
  states=nxt
 return states[target]
def extract(packet,spec):
 scope=[]; occurrences=[]; blocks=[]; families=spec['families']; lookup={}
 for fi,f in enumerate(families):
  lens=f['forms_and_raw_lengths']; lo=min(lens.values()); hi=max(lens.values()); assert lo<hi
  for w,n in lens.items():
   assert w.isascii() and len(w)==n and w not in lookup
   lookup[w]=(fi,f['value'],n,(n-lo)/(hi-lo))
 for reader in spec['readers']:
  seen=set()
  for p in sorted(packet[reader],key=lambda p:p['id']):
   page=p['page']; assert not page.startswith('f84') and page not in spec['forbidden_exact']
   assert int(re.match(r'f(\d+)',page)[1])==p['leaf']; assert p['id'] not in seen; seen.add(p['id'])
   row=dict(reader=reader,paragraph=p['id'],page=page,leaf=p['leaf'],groups=p['groups'])
   row['lines']=[dict(locus=l['locus'],anchor_eligible=l.get('anchor_eligible')) for l in p['lines']]; scope.append(row)
   if p['leaf'] in spec['exclude_leaves']:
    row['category']='EXCLUDED_DEVELOPMENT'; continue
   if not p['lines'] or not all(l.get('anchor_eligible') is True for l in p['lines']):
    row['category']='SOURCE_UNCERTAIN'; continue
   row['category']='LITERAL'; local=[]; pos=0
   for line in p['lines']:
    words=line['words']; assert len(words)==len(line['source_ids'])
    assert all(re.fullmatch('[a-z]+',w) for w in words); assert line['offset']==pos
    for j,w in enumerate(words):
     pos+=1
     if w not in lookup:continue
     fi,fam,n,z=lookup[w]
     edge='SINGLE' if len(words)==1 else 'FIRST' if j==0 else 'LAST' if j==len(words)-1 else 'INTERIOR'
     local.append(dict(reader=reader,paragraph=p['id'],leaf=p['leaf'],family=fam,family_index=fi,position=pos,
       locus=line['locus'],line_position=j+1,source_id=line['source_ids'][j],form=w,length=n,z=z,edge=edge,
       prev_dy=bool(j and words[j-1].endswith('dy')),current_dy=w.endswith('dy')))
   assert pos==p['groups']; grouped=collections.defaultdict(list)
   for o in local:grouped[o['family_index']].append(o)
   for os in grouped.values():
    for j,o in enumerate(os):o['family_count']=len(os); o['u']=j/(len(os)-1) if len(os)>1 else None
   occurrences.extend(local); by_block=collections.defaultdict(list)
   for o in local:by_block[(o['family_index'],o['edge'],o['prev_dy'],o['current_dy'])].append(o)
   local_blocks=[]
   for (fi,edge,prev,curr),os in sorted(by_block.items()):
    fam=families[fi]['value']; counts=dict(sorted(collections.Counter(o['form'] for o in os).items()))
    mobile=len(os)>=2 and len({o['length'] for o in os})>=2
    local_blocks.append(dict(id='#'.join([reader,p['id'],fam,edge,str(int(prev)),str(int(curr))]),reader=reader,
      paragraph=p['id'],leaf=p['leaf'],family=fam,family_index=fi,edge=edge,prev_dy=prev,current_dy=curr,
      source_ids=[o['source_id'] for o in os],forms=[o['form'] for o in os],u=[o['u'] for o in os],z=[o['z'] for o in os],
      counts=counts,dp_states=math.prod(c+1 for c in counts.values()),mobile=mobile))
   blocks.extend(local_blocks)
   row['literal_category']='NO_FAMILY' if not local else 'MOBILE' if any(b['mobile'] for b in local_blocks) else 'IMMOBILE'
 return scope,occurrences,blocks
def capacity(scope,occurrences,blocks,spec):
 out={}; c=spec['capacity']
 for r in spec['readers']:
  ss=[s for s in scope if s['reader']==r]; bs=[b for b in blocks if b['reader']==r and b['mobile']]; fs={}
  for f in spec['families']:
   xs=[b for b in bs if b['family']==f['value']]; nf=len({b['leaf'] for b in xs})
   fs[f['value']]=dict(blocks=len(xs),positions=sum(len(b['forms']) for b in xs),leaves=nf,
     powered=len(xs)>=c['family_blocks'] and nf>=c['family_leaves'])
  row=dict(scope_paragraphs=len(ss),scope_groups=sum(s['groups'] for s in ss),categories=dict(collections.Counter(s['category'] for s in ss)),
    literal_categories=dict(collections.Counter(s['literal_category'] for s in ss if s['category']=='LITERAL')),
    occurrences=sum(o['reader']==r for o in occurrences),mobile_blocks=len(bs),mobile_positions=sum(len(b['forms']) for b in bs),
    mobile_leaves=len({b['leaf'] for b in bs}),families=fs,powered_families=sum(f['powered'] for f in fs.values()))
  row['passes']=row['mobile_blocks']>=c['blocks'] and row['mobile_positions']>=c['positions'] and row['mobile_leaves']>=c['leaves'] and row['powered_families']>=c['families']
  row['status']='NO_OWNED_PARAGRAPH_DATA' if not ss else 'READY' if row['passes'] else 'NO_CAPACITY'; out[r]=row
 return out
def aggregate(bs,gains):
 totals=collections.defaultdict(float); ns=collections.Counter()
 for b,g in zip(bs,gains):totals[b['leaf']]+=g; ns[b['leaf']]+=len(b['forms'])
 leaves={str(f):totals[f]/ns[f] for f in sorted(ns)}
 return (sum(leaves.values())/len(leaves) if leaves else None),leaves
def evaluate(blocks,caps,spec):
 selected={r:[b for b in blocks if b['reader']==r and b['mobile']] for r in spec['readers'] if caps[r]['passes']}
 details=[]; results={}
 for r,bs in selected.items():
  for b in bs:
   if b['dp_states']>spec['dp_state_cap']:return [],[],{},'ENGINEERING_BUDGET_OR_STATE_CAP'
   zmap=dict(zip(b['forms'],b['z'])); logz=partition(b['u'],b['counts'],zmap)
   logn=math.lgamma(len(b['forms'])+1)-sum(math.lgamma(n+1) for n in b['counts'].values())
   energy=sum(u*z for u,z in zip(b['u'],b['z'])); b['_constant']=(logn-logz)/LN2; b['_zmap']=zmap; b['_gain']=b['_constant']-BETA/LN2*energy
   details.append(dict(block_id=b['id'],log_partition=logz,log_distinct_assignments=logn,energy=energy,gain_bits=b['_gain']))
  G,leaves=aggregate(bs,[b['_gain'] for b in bs]); fs={}
  for f in spec['families']:
   xs=[b for b in bs if b['family']==f['value']]; fs[f['value']]=aggregate(xs,[b['_gain'] for b in xs])[0]
  results[r]=dict(G=G,leaf_scores=leaves,family_scores=fs,positive_leaf_fraction=sum(v>0 for v in leaves.values())/len(leaves),
    positive_powered_families=sum(caps[r]['families'][f]['powered'] and v is not None and v>0 for f,v in fs.items()))
 worlds=[]
 if selected:
  rng=np.random.Generator(np.random.PCG64(spec['seed']))
  for world in range(1,spec['null_worlds']+1):
   scores={}; changed={}
   for r,bs in selected.items():
    gains=[]; moves=0
    for b in bs:
     forms=b['forms']; shuffled=[forms[int(j)] for j in rng.permutation(len(forms))]
     assert all(w.endswith('dy')==b['current_dy'] for w in shuffled)
     moves+=sum(a!=c for a,c in zip(forms,shuffled)); energy=sum(u*b['_zmap'][w] for u,w in zip(b['u'],shuffled))
     gains.append(b['_constant']-BETA/LN2*energy)
    scores[r]=aggregate(bs,gains)[0]; changed[r]=moves
   worlds.append(dict(world=world,scores=scores,changed_positions=changed))
 for r,result in results.items():
  g=result['G']; eps=spec['tail_tolerance']
  result['tail_upper']=(1+sum(w['scores'][r]>=g-eps for w in worlds))/(len(worlds)+1)
  result['tail_lower']=(1+sum(w['scores'][r]<=g+eps for w in worlds))/(len(worlds)+1)
  result['supports']=g>0 and result['tail_upper']<=spec['support']['tail_upper'] and result['positive_leaf_fraction']>=spec['support']['positive_leaf_fraction'] and result['positive_powered_families']>=spec['support']['positive_powered_families']
  result['status']='SUPPORT_CONDITIONAL_WRITING_RULE' if result['supports'] else 'FAIL_FIXED_PREDICTIVE_RULE' if g<=0 else 'INCONCLUSIVE'
  result['directionally_adverse']=g<0 and result['tail_lower']<=.05
 return details,worlds,results,'EXECUTED' if selected else 'NO_CAPACITY'
def self_test():
 for forms,us,zmap in [(['A','B'],[0,1],{'A':0,'B':1}),(['A','A','B'],[0,.5,1],{'A':0,'B':1}),(['A','B','C'],[0,.5,1],{'A':0,'B':.25,'C':1})]:
  expected=math.log(sum(math.exp(-BETA*sum(u*zmap[w] for u,w in zip(us,p))) for p in set(itertools.permutations(forms))))
  assert abs(partition(us,collections.Counter(forms),zmap)-expected)<1e-12
 assert abs(math.exp(-partition([0,1],{'A':1,'B':1},{'A':0,'B':1}))-.75)<1e-12
 print('PRIMARY_SYNTHETIC_PREFLIGHT_PASS')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); args=ap.parse_args()
 if args.self_test:self_test(); return
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for path,digest in lock['files'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
 spec=json.loads((E/'src/SPEC.json').read_text()); packet=json.loads((R/spec['packet']['path']).read_text())
 scope,occurrences,blocks=extract(packet,spec); caps=capacity(scope,occurrences,blocks,spec)
 save('SCOPE.json',scope);save('OCCURRENCES.json',occurrences);save('BLOCKS.json',blocks);save('CAPACITY.json',caps)
 details,worlds,scored,status=evaluate(blocks,caps,spec)
 rows={r:scored.get(r,dict(status=caps[r]['status'],supports=False,G=None)) for r in spec['readers']}
 result=dict(experiment='GDT1031',status=status,readers=rows,overall_retained_lead=all(rows[r]['supports'] for r in ['ZL3b','IT2a']),null_worlds=len(worlds),confirmed_words=0,source_identified=False,project_wide_significance=False,independent_confirmation=False)
 save('LIKELIHOODS.json',details);save('NULL.json',worlds);save('RESULT.json',result)
 print(json.dumps(dict(status=status,capacity=caps,result=result),ensure_ascii=False))
if __name__=='__main__':main()
