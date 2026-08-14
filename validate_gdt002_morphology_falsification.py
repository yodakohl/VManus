#!/usr/bin/env python3
"""Independent integrity and arithmetic checks for GDT002 CKPT013."""
import csv,hashlib,itertools,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
S=R/'experiments/semantic_assumptions/results'
EDS=('ZL3b','IT2a','RF1b')
MODS=('ar','ol','dal','dar','sy','te','tee','dy')
checks=[]
def check(name,ok,detail=''):
 checks.append({'check':name,'pass':bool(ok),'detail':str(detail)})
 if not ok:raise AssertionError(f'{name}: {detail}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def guarded(p,locus_col='locus'):
 out=[]
 with p.open(encoding='utf-8') as f:
  head=f.readline().rstrip('\n').split('\t');li=head.index(locus_col)
  for line in f:
   cells=line.rstrip('\n').split('\t')
   if cells[li].startswith('f84r'):continue
   out.append(dict(zip(head,cells)))
 return out
def folio(page):
 m=re.match(r'(f\d+)',page);return m.group(1) if m else page

result=json.loads((R/'gdt002_morphology_results.json').read_text())
check('status',result['status']=='FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED')
check('claim_ceiling',all(x in result['claim_ceiling'] for x in ('No candidate is a morpheme','translation')))
check('holdout_flag',result['holdout']['f84r_formal_retained_or_scored'] is False)
for rel,h in {**result['inputs'],**result['documents'],**result['outputs']}.items():
 check('hash_'+rel,sha(R/rel)==h)

out_names=list(result['outputs'])
for name in out_names:
 check('no_f84r_'+name,'f84r' not in (R/name).read_text())

sep=guarded(S/'source_separator_transcription.tsv')
meta={x['source_group_id']:x for x in sep}
align=guarded(S/'source_sta_group_alignment.tsv')
groups=defaultdict(dict);types=defaultdict(lambda:defaultdict(list))
for x in align:
 m=meta[x['source_group_id']];s=x['nearest_basic_eva_primary'].lower()
 rec={**x,'surface':s,'page':m['page'],'section':m['section'],'kind':m['kind']}
 groups[(x['locus'],int(x['source_group_index']))][x['edition']]=rec
 types[x['edition']][s].append(rec)

independent={}
for mod in MODS:
 physical=[]
 for key,em in groups.items():
  if any(mod in x['surface'] for x in em.values()):physical.append((key,em))
 free=set();bound=set();host=set();fs=set();secs=set();prefix=suffix=internal=0
 for key,em in physical:
  first=next(iter(em.values()));fs.add(folio(first['page']));secs.add(first['section'])
  for x in em.values():
   s=x['surface']
   if mod not in s:continue
   host.add(s)
   if s==mod:free.add(key)
   else:
    bound.add(key);prefix+=int(s.startswith(mod));suffix+=int(s.endswith(mod));internal+=int(not s.startswith(mod) and not s.endswith(mod))
 independent[mod]={'physical_rows':len(physical),'free_physical':len(free),'bound_physical':len(bound),'host_types':len(host),'physical_folios':len(fs),'sections':len(secs),'prefix_reading_hits':prefix,'suffix_reading_hits':suffix,'internal_reading_hits':internal}
check('module_summaries',independent==result['modules'])
check('inventory_row_count',sum(x['physical_rows'] for x in independent.values())==len(rows(R/'gdt002_morphology_occurrences.tsv'))==25349)

stable=[]
for em in groups.values():
 if len(em)==3 and len({x['surface'] for x in em.values()})==1 and len({x['source_group_count'] for x in em.values()})==1:stable.append(next(iter(em.values())))
density={}
for role,kind in (('LABEL','L'),('RUNNING_TEXT','P')):
 rr=[x for x in stable if x['kind']==kind];chars=sum(len(x['surface']) for x in rr);hits=sum(sum(x['surface'].count(m) for m in MODS) for x in rr);multi=sum(sum(m in x['surface'] for m in MODS)>=2 for x in rr);free=sum(x['surface'] in MODS for x in rr)
 density[role]={'groups':len(rr),'symbols':chars,'candidate_hits':hits,'hits_per_100_symbols':100*hits/chars,'multi_module_groups':multi,'multi_module_rate':multi/len(rr),'standalone_candidate_groups':free,'standalone_rate':free/len(rr)}
check('density',density==result['density'])
density_sensitivity={}
for name,mods in {'EXCLUDE_NESTED_TE_TEE':('ar','ol','dal','dar','sy','dy'),'RIGHT_EDGE_CANDIDATES_ONLY':('dal','dar','sy','dy')}.items():
 density_sensitivity[name]={}
 for role,kind in (('LABEL','L'),('RUNNING_TEXT','P')):
  rr=[x for x in stable if x['kind']==kind];chars=sum(len(x['surface']) for x in rr);hits=sum(sum(x['surface'].count(m) for m in mods) for x in rr);multi=sum(sum(m in x['surface'] for m in mods)>=2 for x in rr)
  density_sensitivity[name][role]={'candidate_hits':hits,'hits_per_100_symbols':100*hits/chars,'multi_module_groups':multi,'multi_module_rate':multi/len(rr)}
check('density_sensitivity',density_sensitivity==result['density_sensitivity'])

pair_keys=set()
for e in EDS:
 ts=set(types[e])
 def add(rule,a,b,seg):
  if a!=b and a in ts and b in ts:pair_keys.add((rule,a,b,seg))
 for base in ts:
  add('Q_OUTER_INSERTION',base,'q'+base,f'q+{base}')
  if base.startswith('d') and 's'+base[1:] in ts:add('D_S_LEFT_CONTRAST',base,'s'+base[1:],f'd/s+{base[1:]}')
  if base.startswith('o') and 'ot'+base[1:] in ts:add('O_OT_LEFT_CONTRAST',base,'ot'+base[1:],f'o/ot+{base[1:]}')
  for i in range(len(base)-1):
   if base.startswith('te',i):add('TE_TEE_CONTRAST',base,base[:i]+'tee'+base[i+2:],base[:i]+'+te/tee+'+base[i+2:])
  for s1,s2 in itertools.combinations(('', 'dal','dar','sy','dy'),2):
   if s1 and not base.endswith(s1):continue
   stem=base[:-len(s1)] if s1 else base
   if len(stem)>=2:add('RIGHT_MODULE_CONTRAST',base,stem+s2,f'{stem}+{s1 or "∅"}/{s2 or "∅"}')
pc=Counter(x[0] for x in pair_keys)
check('generated_pair_library',sum(pc.values())==2048 and dict(pc)==result['minimal_pairs']['generated_rules'])
mp=rows(R/'gdt002_morphology_minimal_pairs.tsv')
check('minimal_pair_rows',len(mp)==500)
for a,b,lc,rc,lf,rf in (('otedy','qotedy',152,83,38,31),('oteedy','qoteedy',114,75,32,26),('darol','sarol',3,5,3,5)):
 x=next(z for z in mp if z['left_form']==a and z['right_form']==b)
 check('pair_'+a+'_'+b,(int(x['left_loci_count']),int(x['right_loci_count']),int(x['left_physical_folios']),int(x['right_physical_folios']))==(lc,rc,lf,rf))

sj=rows(R/'gdt002_morphology_split_join.tsv')
for a,b,j,sc,jc in (('ar','ol','arol',11,13),('dar','ol','darol',8,3)):
 x=next(z for z in sj if z['left_free_group']==a and z['right_free_group']==b and z['joined_form']==j)
 check('split_join_'+j,(int(x['split_loci_count']),int(x['joined_loci_count']))==(sc,jc))

def exact_tokens(locus):
 return {e:next((x['surface'] for (l,_),em in groups.items() if l==locus and e in em for x in [em[e]]),'MISSING') for e in EDS}
for loc,expected in {'f82r.35':{'ZL3b':'darol','IT2a':'darol','RF1b':'darol'},'f82r.38':{'ZL3b':'darary','IT2a':'daryry','RF1b':'jarary'},'f83r.50':{'ZL3b':'sasoldal','IT2a':'saroldal','RF1b':'saroldal'},'f83r.51':{'ZL3b':'darolsy','IT2a':'darolsy','RF1b':'darolsy'}}.items():
 check('spotlight_'+loc,exact_tokens(loc)==expected==result['spotlight_readings'][loc])
for form in ('dar','sar','dal','sy'):
 got={e:sorted({x['locus'] for x in types[e].get(form,[]) if x['page']=='f83r' and x['kind']=='P'}) for e in EDS}
 check('f83_free_'+form,got==result['f83r_free_running_forms'][form])

rank=rows(R/'gdt002_morphology_rankings.tsv');rd={x['candidate']:x['rank'] for x in rank}
check('rank_te_tee_weak',rd['TE_REUSABLE_FORMAL_UNIT']==rd['TEE_REUSABLE_FORMAL_UNIT']=='WEAK')
check('rank_semantic_template_failed',rd['FOUR_SLOT_SEMANTIC_TEMPLATE']=='FAILED')
vis=rows(R/'gdt002_morphology_visual_associations.tsv')
check('visual_no_small_p',min(float(x['page_conditioned_one_sided_p']) for x in vis)>.15)
ledger=rows(R/'GDT002_YOLO_LEDGER.tsv')
check('ledger_ckpt013',sum(x['checkpoint_id']=='GDT002_CKPT013' for x in ledger)==1)

validation={'artifact':'GDT002_MORPHOLOGY_FALSIFICATION_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(R/'gdt002_morphology_results.json'),'validator_sha256':sha(R/'validate_gdt002_morphology_falsification.py'),'scope':'Independent source-table reconstruction of module counts, density, pair-library cardinality, requested pairs, split/join examples, spotlight readings, ranks, hashes, and f84 exclusion. It does not independently judge visual descriptions.'}
(R/'gdt002_morphology_validation.json').write_text(json.dumps(validation,sort_keys=True,indent=2)+'\n')
print('PASS',len(checks))
