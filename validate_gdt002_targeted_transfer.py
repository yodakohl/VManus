#!/usr/bin/env python3
"""Independent reconstruction of GDT002 CKPT010 targeted transfer."""
import csv,hashlib,itertools,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,t=1e-12):return abs(float(a)-float(b))<=t
def kt(k,n):return -(math.lgamma(k+.5)+math.lgamma(n-k+.5)-math.lgamma(n+1)-2*math.lgamma(.5))*math.log2(math.e)

j=read(R/'gdt002_targeted_transfer_join.tsv');res=json.loads((R/'gdt002_targeted_transfer_results.json').read_text());ledger=read(R/'GDT002_YOLO_LEDGER.tsv')
aqa=[x for x in j if x['channel']=='AQA_POSITIONAL_TRANSFER' and x['formal_coverage']=='1'];aca=[x for x in j if x['channel']=='ACA_APPARATUS_TRANSFER']
def stats(xs,pos,feature):
 a=[int(x[feature]) for x in xs if x['visual_state']==pos];b=[int(x[feature]) for x in xs if x['visual_state']!=pos]
 return len(a),len(b),sum(a),sum(b),sum(a)/len(a)-sum(b)/len(b)
f75=[x for x in aqa if x['page']=='f75v'];f67=[x for x in aqa if x['page']=='f67r2'];f77=[x for x in aca if x['page']=='f77r'];f82=[x for x in aca if x['page']=='f82r']
f75s=stats(f75,'TOP','family_prefix_AQA');f67s=stats(f67,'UPPER_ISOLATED','family_prefix_AQA');f77s=stats(f77,'APPARATUS_POSITION','family_contains_ACA');f82s=stats(f82,'APPARATUS_POSITION','family_contains_ACA')

# Exact f75 pair-swap orbit.
pairs={x['pair_id'] for x in f75};f75_tail=f75_worlds=0
for flips in itertools.product((0,1),repeat=len(pairs)):
 top=[];bottom=[]
 for flip,p in zip(flips,sorted(pairs,key=int)):
  q=sorted([x for x in f75 if x['pair_id']==p],key=lambda x:x['visual_state']);v=[int(x['family_prefix_AQA']) for x in q]
  top.append(v[flip]);bottom.append(v[1-flip])
 f75_worlds+=1;f75_tail+=(sum(top)-sum(bottom)>=0)

# Exact f67 page orbit and joint ACA page-preserving orbit.
f67_worlds=math.comb(16,6);f67_tail=0;mask=[int(x['family_prefix_AQA']) for x in f67]
for chosen in itertools.combinations(range(16),6):
 z=set(chosen);e=sum(mask[i] for i in z)/6-sum(mask[i] for i in range(16) if i not in z)/10;f67_tail+=e>=-1e-12
def page_masks(xs):return [int(x['family_contains_ACA']) for x in xs],sum(x['visual_state']=='APPARATUS_POSITION' for x in xs)
m77,k77=page_masks(f77);m82,k82=page_masks(f82);target=(f77s[4]+f82s[4])/2;worlds=tail=0
for a in itertools.combinations(range(len(m77)),k77):
 za=set(a);e1=sum(m77[i] for i in za)/k77-sum(m77[i] for i in range(len(m77)) if i not in za)/(len(m77)-k77)
 for b in itertools.combinations(range(len(m82)),k82):
  zb=set(b);e2=sum(m82[i] for i in zb)/k82-sum(m82[i] for i in range(len(m82)) if i not in zb)/(len(m82)-k82)
  worlds+=1;tail+=(e1+e2)/2>=target-1e-12
null=alt=0.0
for q in (f77,f82):
 y=[int(x['visual_state']=='APPARATUS_POSITION') for x in q];null+=kt(sum(y),len(y))
 for v in (0,1):
  z=[int(x['visual_state']=='APPARATUS_POSITION') for x in q if int(x['family_contains_ACA'])==v]
  if z:alt+=kt(sum(z),len(z))

checks={
 'branch_exact':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='yolo/gdt002-visual-grammar-constraints',
 'canonical_files_unchanged':subprocess.run(['git','diff','--quiet','c7874a9','--','VOYNICH_ACTIVE_STATE.md','experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv','experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv'],cwd=R).returncode==0,
 'join_counts':len(j)==88 and Counter(x['channel'] for x in j)=={'ACA_APPARATUS_TRANSFER':49,'AQA_POSITIONAL_TRANSFER':39} and len(aqa)==36,
 'no_f84':all(x['page']!='f84r' and not x['locus'].startswith('f84r.') for x in j) and res['holdout']['formal_payload_opened'] is False and res['holdout']['used_in_search'] is False,
 'f75_exact':f75s==(10,10,1,1,0.0) and f75_worlds==1024 and f75_tail==768 and close(res['AQA']['pages']['f75v']['one_sided_exact_p'],.75),
 'f67_exact':f67s==(6,10,3,5,0.0) and f67_worlds==8008 and f67_tail==5572 and close(res['AQA']['pages']['f67r2']['one_sided_exact_p'],5572/8008),
 'f77_exact':f77s[:4]==(6,4,1,0) and close(f77s[4],1/6) and close(res['ACA']['pages']['f77r']['one_sided_exact_p'],.6) and close(res['ACA']['pages']['f77r']['raw_mdl_gain_bits'],-.13750352374992936),
 'f82_exact':f82s[:4]==(3,8,3,1) and close(f82s[4],.875) and close(res['ACA']['pages']['f82r']['one_sided_exact_p'],4/165) and close(res['ACA']['pages']['f82r']['raw_mdl_gain_bits'],4.459431618637296),
 'aca_orbit':worlds==34650 and tail==504 and close(res['ACA']['pooled_f77r_f82r']['one_sided_exact_p'],504/34650),
 'aca_mdl':close(null-alt,4.321928094887369) and close(res['ACA']['pooled_f77r_f82r']['two_candidate_selector_paid_mdl_gain_bits'],null-alt-1),
 'fixed_candidate_ids':res['fixed_candidates']['AQA']['source_candidate_id']=='a32e8d85e647' and res['fixed_candidates']['ACA']['source_candidate_id']=='65289bb29690',
 'decision_ceiling':res['status']=='AQA_NO_TRANSFER_ACA_DIRECTION_REPEATS_BUT_TRANSFER_ONLY_WEAK' and res['ACA']['decision']=='INTERESTING_EXPLORATORY_DIRECTION_ONLY_NOT_VALIDATED' and 'UNASSIGNED' in res['claim_ceiling'] and 'translation' in res['claim_ceiling'],
 'ledger_ckpt010':sum(x['checkpoint_id']=='GDT002_CKPT010' and x['status']==res['status'] for x in ledger)==1,
 'input_hashes':all(sha(R/k)==v for k,v in res['inputs'].items()),
 'document_hashes':all(sha(R/k)==v for k,v in res['documents'].items()),
 'output_hashes':all(sha(R/k)==v for k,v in res['outputs'].items()),
}
failed=[k for k,v in checks.items() if not v]
out={'artifact':'GDT002_TARGETED_TRANSFER_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha(R/'gdt002_targeted_transfer_results.json'),'scope':'Independent source-join counts, f75 pair-swap, f67 page orbit, f77/f82 apparatus orbit, KT/MDL accounting, f84 exclusion, hashes, ledger, and claim ceiling. No image or semantic judgment.'}
(R/'gdt002_targeted_transfer_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
