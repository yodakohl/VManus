#!/usr/bin/env python3
"""GDT222: fixed GDT002 module inventory against GDT221 local assemblies."""
import csv, hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
MOD=R/'gdt222_module_manifest.tsv'; MAN=R/'gdt221_assembly_manifest.tsv'
LABELS=R/'gdt012_annotated_core_inventory.tsv'; GROUPS=R/'gdt016_group_state_inventory.tsv'
OLD=R/'gdt221_result.json'; METHOD=R/'GDT222_FIXED_MODULE_LOCAL_ASSEMBLY_METHOD.md'
REPORT=R/'GDT222_FIXED_MODULE_LOCAL_ASSEMBLY_REPORT.md'
INV=R/'gdt222_assembly_module_inventory.tsv'; SCORES=R/'gdt222_assignment_scores.tsv'
CORR=R/'gdt222_module_correspondence.tsv'; LOMO=R/'gdt222_leave_one_module_out.tsv'
COUNTER=R/'gdt222_counterexamples.tsv'; RESULT=R/'gdt222_result.json'

def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0.0

def main():
 modules=[r['module'] for r in read(MOD)]
 assert modules==['ar','ol','dal','dar','sy','te','tee','dy']
 man=read(MAN); assert len(man)==4
 assert {r['page'] for r in man}=={'f75v','f83r'} and not any(r['page'].startswith('f84') for r in man)
 label_loci={x for r in man for x in r['label_loci'].split(',')}
 prose_loci={x for r in man for x in r['prose_loci'].split(',')}
 labels=defaultdict(list)
 with LABELS.open(encoding='utf8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   assert not r['page'].startswith('f84')
   if r['locus'] in label_loci: labels[r['locus']].append(r['token'])
 prose=defaultdict(list); counts={}
 with GROUPS.open(encoding='utf8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'): continue
   if r['locus'] in prose_loci:
    prose[r['locus']].append(r['token']);counts[r['locus']]=int(r['group_count'])
 missing=sorted(label_loci-set(labels)); assert missing==['f75v.22','f75v.23','f83r.50']
 complete={l for l,v in prose.items() if len(v)==counts[l]}
 spec={(r['page'],r['assembly']):r for r in man}
 def toks(row,key,source,complete_only=False):
  loci=row[key].split(',')
  return [t for l in loci if (not complete_only or l in complete) for t in source.get(l,[])]
 def present(ts,exclude=None):return {m for m in modules if m!=exclude and any(m in t for t in ts)}
 inv=[];score_rows=[];scope_sets={}
 for scope,complete_only in [('ALL_AVAILABLE_PRIMARY',False),('COMPLETE_LINES_SENSITIVITY',True)]:
  for page in ('f75v','f83r'):
   sets={}
   for side in ('TOP','BOTTOM'):
    row=spec[(page,side)]
    lt=toks(row,'label_loci',labels);pt=toks(row,'prose_loci',prose,complete_only)
    lm=present(lt);pm=present(pt);sets['L'+side[0]]=lm;sets['P'+side[0]]=pm
    for role,tt,mm in [('LABEL',lt,lm),('PROSE',pt,pm)]:
     miss='|'.join(x for x in row[('label_loci' if role=='LABEL' else 'prose_loci')].split(',') if x not in (labels if role=='LABEL' else prose))
     inv.append({'scope':scope,'page':page,'assembly':side,'role':role,'token_count':len(tt),'tokens':'|'.join(tt),'module_count':len(mm),'modules':'|'.join(m for m in modules if m in mm),'missing_registered_loci':miss or 'NONE'})
   tt=jac(sets['LT'],sets['PT']);tb=jac(sets['LT'],sets['PB']);bt=jac(sets['LB'],sets['PT']);bb=jac(sets['LB'],sets['PB']);lead=tt+bb-tb-bt
   score_rows.append({'scope':scope,'page':page,'top_to_top':f'{tt:.12g}','top_to_bottom':f'{tb:.12g}','bottom_to_top':f'{bt:.12g}','bottom_to_bottom':f'{bb:.12g}','correct_assignment_lead':f'{lead:.12g}'})
   scope_sets[(scope,page)]=sets
 allsets={p:scope_sets[('ALL_AVAILABLE_PRIMARY',p)] for p in ('f75v','f83r')}
 # exact four-world assignment null
 worlds=[]
 for signs in itertools.product((1,-1),repeat=2):
  leads=[]
  for sign,page in zip(signs,('f75v','f83r')):
   s=allsets[page];base=jac(s['LT'],s['PT'])+jac(s['LB'],s['PB'])-jac(s['LT'],s['PB'])-jac(s['LB'],s['PT']);leads.append(sign*base)
  worlds.append(sum(leads))
 obs=worlds[0];p=sum(x>=obs-1e-15 for x in worlds)/len(worlds)
 # module correspondence and max-eight control
 corr=[];world_max=[]
 for swaps in itertools.product((0,1),repeat=2):
  support={m:0 for m in modules}
  for sw,page in zip(swaps,('f75v','f83r')):
   s=allsets[page];pt,pb=(s['PB'],s['PT']) if sw else (s['PT'],s['PB'])
   for m in modules:
    lp=(m in s['LT'],m in s['LB']);pp=(m in pt,m in pb)
    if lp[0]!=lp[1] and pp[0]!=pp[1] and lp==pp:support[m]+=1
  world_max.append(max(support.values()))
 observed_support=None;complete_ar_support=0
 for scope in ('ALL_AVAILABLE_PRIMARY','COMPLETE_LINES_SENSITIVITY'):
  for m in modules:
   per=[]
   for page in ('f75v','f83r'):
    s=scope_sets[(scope,page)];lp=(int(m in s['LT']),int(m in s['LB']));pp=(int(m in s['PT']),int(m in s['PB']));hit=int(lp[0]!=lp[1] and pp[0]!=pp[1] and lp==pp);per.append(hit)
    corr.append({'scope':scope,'module':m,'page':page,'label_top':lp[0],'label_bottom':lp[1],'prose_top':pp[0],'prose_bottom':pp[1],'discriminating_pattern_match':hit,'orientation':('TOP' if lp==(1,0) else 'BOTTOM' if lp==(0,1) else 'NONDISCRIMINATING')})
   if m=='ar' and scope=='ALL_AVAILABLE_PRIMARY':observed_support=sum(per)
   if m=='ar' and scope=='COMPLETE_LINES_SENSITIVITY':complete_ar_support=sum(per)
 max_obs=max(sum(int(m in allsets[p]['LT'])!=int(m in allsets[p]['LB']) and (int(m in allsets[p]['LT']),int(m in allsets[p]['LB']))==(int(m in allsets[p]['PT']),int(m in allsets[p]['PB'])) for p in ('f75v','f83r')) for m in modules)
 maxp=sum(x>=max_obs for x in world_max)/4
 lomo=[]
 for excluded in modules:
  for page in ('f75v','f83r'):
   s={k:v-{excluded} for k,v in allsets[page].items()};lead=jac(s['LT'],s['PT'])+jac(s['LB'],s['PB'])-jac(s['LT'],s['PB'])-jac(s['LB'],s['PT'])
   lomo.append({'excluded_module':excluded,'page':page,'correct_assignment_lead':f'{lead:.12g}','positive':int(lead>0)})
 write(INV,inv);write(SCORES,score_rows);write(CORR,corr);write(LOMO,lomo)
 counter=[
  {'counterexample':'TWO_EXPOSED_PAGES','value':'2','detail':'Only four human-defined assemblies on two already exposed pages are available; the exact assignment null has four worlds.'},
  {'counterexample':'AR_DEPENDENCE','value':'F83_LEAD_NEGATIVE_WITHOUT_AR','detail':'Removing ar changes the f83 lead from +0.233333 to -0.116667; the cross-page result is concentrated in one module.'},
  {'counterexample':'COVERAGE_SENSITIVITY','value':'COMPLETE_LINES_F75_PLUS_POINT083333_F83_MINUS_POINT133333','detail':'The complete-line aggregate is -0.05; f83 reverses and the all-row ar match depends on qotar in incomplete line f83r.53.'},
  {'counterexample':'OPPOSITE_PHYSICAL_ORIENTATION','value':'F75_TOP_F83_BOTTOM','detail':'ar tracks different vertical assemblies on the two pages, excluding a universal top/bottom gloss.'},
  {'counterexample':'NO_EXACT_LABEL_REUSE','value':'0','detail':'The adjacent f83 prose does not reproduce darolsy or its exact PAGE_HOST; only substrings recur.'},
  {'counterexample':'MISSING_LABEL_ROWS','value':','.join(missing),'detail':'The reading-unstable f83r.50 and two f75 labels are not imputed.'},
  {'counterexample':'SUBSTRING_NOT_SEGMENTATION','value':'8_FIXED_PATTERNS','detail':'Literal substring presence does not establish manuscript-native cuts, morphemes, or semantic units.'},
 ]
 write(COUNTER,counter)
 status='FIXED_MODULE_LOCAL_ASSEMBLY_LEAD_COVERAGE_UNSTABLE_NO_TRANSFER_TARGET'
 complete_leads={r['page']:float(r['correct_assignment_lead']) for r in score_rows if r['scope']=='COMPLETE_LINES_SENSITIVITY'}
 result={'schema':'GDT222_FIXED_MODULE_LOCAL_ASSEMBLY_RESULT_V1','status':status,'modules':modules,'pages':2,'assemblies':4,'missing_label_loci':missing,'primary':{'page_leads':{r['page']:float(r['correct_assignment_lead']) for r in score_rows if r['scope']=='ALL_AVAILABLE_PRIMARY'},'aggregate_lead':obs,'positive_pages':sum(x>0 for x in [float(r['correct_assignment_lead']) for r in score_rows if r['scope']=='ALL_AVAILABLE_PRIMARY']),'exact_worlds':4,'exact_assignment_p':p,'max_module_supported_pages':max_obs,'max_eight_module_p':maxp,'ar_supported_pages':observed_support},'complete_line_sensitivity':{'page_leads':complete_leads,'aggregate_lead':sum(complete_leads.values()),'positive_pages':sum(x>0 for x in complete_leads.values()),'ar_supported_pages':complete_ar_support},'interpretation':'Fixed candidate modules align both exposed assemblies only in the all-row view; complete-line f83 reverses and the ar correspondence depends on incomplete f83r.53.','claim_ceiling':'Post-hoc two-page coverage-unstable local component-reuse lead only; no module segmentation semantic role word sound language plaintext or translation.','f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{x.name:sha(x) for x in (MOD,MAN,LABELS,GROUPS,OLD)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in (INV,SCORES,CORR,LOMO,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
 print(json.dumps({'status':status,'aggregate_lead':obs,'p':p,'max8_p':maxp,'ar_pages':observed_support},sort_keys=True))
if __name__=='__main__':main()
