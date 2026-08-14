#!/usr/bin/env python3
"""GDT003: predictive formal-composition rectangles and held fourth cells."""
import csv,hashlib,itertools,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
EDS=('ZL3b','IT2a','RF1b');ALPHABET=tuple('abcdefghijklmnopqrstuvwxyz$')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_tsv(p,rr):
 if not rr:raise ValueError(p)
 fields=[]
 for row in rr:
  for key in row:
   if key not in fields:fields.append(key)
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rr)
def guarded(p,locus_col='locus'):
 out=[]
 with p.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');li=h.index(locus_col)
  for line in f:
   c=line.rstrip('\n').split('\t')
   if c[li].startswith('f84r'):continue
   out.append(dict(zip(h,c)))
 return out
def folio(page):
 m=re.match(r'(f\d+)',page);return m.group(1) if m else page
def op_q(s):return None if s.startswith('q') else 'q'+s
def op_ds(s):return 's'+s[1:] if len(s)>1 and s.startswith('d') else None
def op_oot(s):return 'ot'+s[1:] if len(s)>1 and s.startswith('o') and not s.startswith('ot') else None
def add(s,x):return s+x
def repl(s,a,b):return s[:-len(a)]+b if s.endswith(a) else None
OPS={
 'PREPEND_Q':('PREFIX_ADD_1',op_q),
 'INITIAL_D_TO_S':('INITIAL_REPLACE_1_1',op_ds),
 'INITIAL_O_TO_OT':('INITIAL_REPLACE_1_2',op_oot),
 'APPEND_DY':('SUFFIX_ADD_2',lambda s:add(s,'dy')),
 'APPEND_DAL':('SUFFIX_ADD_3',lambda s:add(s,'dal')),
 'APPEND_DAR':('SUFFIX_ADD_3',lambda s:add(s,'dar')),
 'FINAL_DAL_TO_DAR':('FINAL_REPLACE_3_3',lambda s:repl(s,'dal','dar')),
 'FINAL_DAL_TO_DY':('FINAL_REPLACE_3_2',lambda s:repl(s,'dal','dy')),
 'FINAL_DAR_TO_DY':('FINAL_REPLACE_3_2',lambda s:repl(s,'dar','dy')),
}
def editpos(a,b):
 cp=0
 while cp<min(len(a),len(b)) and a[cp]==b[cp]:cp+=1
 cs=0
 while cs<min(len(a)-cp,len(b)-cp) and a[-1-cs]==b[-1-cs]:cs+=1
 den=max(1,max(len(a),len(b)));return cp/den,(max(len(a),len(b))-cs)/den
def lev(a,b):
 d=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  n=[i]
  for j,y in enumerate(b,1):n.append(min(n[-1]+1,d[j]+1,d[j-1]+(x!=y)))
  d=n
 return d[-1]
def wilson(k,n):
 if not n:return (0.0,0.0)
 z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return (max(0,mid-half),min(1,mid+half))
def auc(scores,ys):
 pos=[s for s,y in zip(scores,ys) if y];neg=[s for s,y in zip(scores,ys) if not y]
 if not pos or not neg:return None
 return sum((a>b)+.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg))
def ap(scores,ys,keys):
 z=sorted(zip(scores,ys,keys),key=lambda x:(-x[0],x[2]));p=sum(ys)
 if not p:return None
 hit=0;v=0
 for i,(_,y,_) in enumerate(z,1):
  if y:hit+=1;v+=hit/i
 return v/p
def kt_lm(records,order=4):
 cc=Counter();hc=Counter();K=len(ALPHABET)
 for s,n in records.items():
  seq='^'*order+s+'$'
  for i in range(order,len(seq)):
   h=seq[i-order:i];c=seq[i];cc[h,c]+=n;hc[h]+=n
 def score(s):
  seq='^'*order+s+'$';bits=0.0
  for i in range(order,len(seq)):
   h=seq[i-order:i];c=seq[i];bits-=math.log2((cc[h,c]+.5)/(hc[h]+.5*K))
  return -bits/max(1,len(s)+1)
 return score

# One physical corpus; alternate readings are retained for sensitivity only.
sep=guarded(S/'source_separator_transcription.tsv');meta={x['source_group_id']:x for x in sep}
aln=guarded(S/'source_sta_group_alignment.tsv');groups=defaultdict(dict)
for x in aln:
 m=meta[x['source_group_id']];groups[x['locus'],int(x['source_group_index'])][x['edition']]={**x,'surface':x['nearest_basic_eva_primary'].lower(),'page':m['page'],'folio':folio(m['page']),'section':m['section'],'kind':m['kind']}
records=[];ambiguous=0
for key,em in groups.items():
 if len(em)==3 and len({x['surface'] for x in em.values()})==1 and len({x['source_group_count'] for x in em.values()})==1:
  x=next(iter(em.values()));records.append({'key':key,**x})
 else:ambiguous+=1
forms=set(x['surface'] for x in records);freq=Counter(x['surface'] for x in records);fm=defaultdict(lambda:{'loci':set(),'folios':set(),'sections':set(),'registers':set()})
for x in records:
 z=fm[x['surface']];z['loci'].add(x['locus']);z['folios'].add(x['folio']);z['sections'].add(x['section']);z['registers'].add(x['kind'])
edition_forms={e:{x['surface'] for em in groups.values() if e in em for x in [em[e]]} for e in EDS}

def edges(op,universe):
 fn=OPS[op][1];return {s:fn(s) for s in sorted(universe) if fn(s) is not None and fn(s) in universe}
full_edges={o:edges(o,forms) for o in OPS}
splitrows=[]
with (R/'gdt002_morphology_split_join.tsv').open(newline='',encoding='utf-8') as f:splitrows=list(csv.DictReader(f,delimiter='\t'))
trans=[]
for name,(decl,fn) in OPS.items():
 ee=full_edges[name];ps=[]
 for a,b in ee.items():ps.append(editpos(a,b))
 left=sum(1 for a,b in ps if a<=.15);right=sum(1 for a,b in ps if b>=.85)
 inferred='LEFT_EDGE' if left>right and left>=.8*len(ps) else 'RIGHT_EDGE' if right>left and right>=.8*len(ps) else 'EDGE_MIXED'
 split_hosts=set()
 for z in splitrows:
  a,b,j=z['left_free_group'],z['right_free_group'],z['joined_form']
  if j not in ee.values():continue
  if name=='PREPEND_Q' and a=='q' and ee.get(b)==j:split_hosts.add(b)
  if name.startswith('APPEND_') and ee.get(a)==j:split_hosts.add(a)
 allsrc=set(ee);alltgt=set(ee.values());loci=set().union(*(fm[x]['loci'] for x in allsrc|alltgt)) if ee else set();folios=set().union(*(fm[x]['folios'] for x in allsrc|alltgt)) if ee else set();sections=set().union(*(fm[x]['sections'] for x in allsrc|alltgt)) if ee else set();regs=set().union(*(fm[x]['registers'] for x in allsrc|alltgt)) if ee else set()
 edcounts={e:len(edges(name,edition_forms[e])) for e in EDS}
 trans.append({'transformation':name,'declared_template_only':decl,'inferred_attachment_class':inferred,'exact_pair_types':len(ee),'source_physical_occurrences':sum(freq[x] for x in allsrc),'target_physical_occurrences':sum(freq[x] for x in alltgt),'physical_loci':len(loci),'physical_folios':len(folios),'sections':len(sections),'registers':';'.join(sorted(regs)),'split_join_supported_hosts':len(split_hosts),'split_join_examples':';'.join(sorted(split_hosts)[:12]),'ZL3b_pair_types':edcounts['ZL3b'],'IT2a_pair_types':edcounts['IT2a'],'RF1b_pair_types':edcounts['RF1b'],'retained_for_prediction':int(len(ee)>=5),'claim_state':'FORMAL_TRANSFORMATION_NO_LINGUISTIC_STATUS'})
write_tsv(R/'gdt003_transformations.tsv',trans)

def cells_for(x,a,b):
 fa,fb=OPS[a][1],OPS[b][1];ax=fa(x);bx=fb(x)
 if ax is None or bx is None:return None
 ab=fa(bx);ba=fb(ax)
 return x,ax,bx,ab,ba

rect=[];pair_stats={};rng=random.Random(3003)
for a,b in itertools.combinations(OPS,2):
 rows=[]
 for x in sorted(forms):
  c=cells_for(x,a,b)
  if not c:continue
  x0,ax,bx,ab,ba=c;equal=ab is not None and ab==ba
  present=[x0 in forms,ax in forms,bx in forms,equal and ab in forms]
  n=sum(present)
  if n<2:continue
  state='COMPLETE_4' if n==4 else 'PARTIAL_3' if n==3 else 'PARTIAL_2'
  loccounts=[len(fm[z]['loci']) if z and z in fm else 0 for z in (x0,ax,bx,ab)]
  fols=set().union(*(fm[z]['folios'] for z in (x0,ax,bx,ab) if z and z in fm));secs=set().union(*(fm[z]['sections'] for z in (x0,ax,bx,ab) if z and z in fm));regs=set().union(*(fm[z]['registers'] for z in (x0,ax,bx,ab) if z and z in fm))
  rows.append((x0,ax,bx,ab,ba,equal,state,n,loccounts,fols,secs,regs))
  rect.append({'operation_A':a,'operation_B':b,'base_X':x0,'A_X':ax,'B_X':bx,'A_of_B_X':ab or 'NOT_APPLICABLE','B_of_A_X':ba or 'NOT_APPLICABLE','orders_equal':int(equal),'structure_state':state,'cells_present':n,'X_loci':loccounts[0],'A_X_loci':loccounts[1],'B_X_loci':loccounts[2],'fourth_loci':loccounts[3],'distinct_folios':len(fols),'sections':';'.join(sorted(secs)),'registers':';'.join(sorted(regs)),'fourth_form_seen':int(equal and ab in forms),'claim_state':'FORMAL_RECTANGLE_NO_LINGUISTIC_STATUS'})
 # Graph-permutation null preserves source and target multisets for both operations.
 ea,eb=full_edges[a],full_edges[b];base=set(ea)&set(eb)
 def count_rect(ma,mb):return sum(x in ma and x in mb and mb[x] in ma and ma[x] in mb and ma[mb[x]]==mb[ma[x]] for x in base)
 real=count_rect(ea,eb);null=[]
 sa,ta=list(ea),list(ea.values());sb,tb=list(eb),list(eb.values())
 def length_matched_shuffle(src,tgt):
  out=tgt[:];bins=defaultdict(list)
  for i,s in enumerate(src):bins[len(s)].append(i)
  for ii in bins.values():
   vals=[out[i] for i in ii];rng.shuffle(vals)
   for i,v in zip(ii,vals):out[i]=v
  return out
 for _ in range(256):
  qa=length_matched_shuffle(sa,ta);qb=length_matched_shuffle(sb,tb);null.append(count_rect(dict(zip(sa,qa)),dict(zip(sb,qb))))
 trip=sum(r[6] in {'COMPLETE_4','PARTIAL_3'} and r[5] for r in rows);complete=sum(r[6]=='COMPLETE_4' for r in rows)
 pair_stats[a,b]={'complete':complete,'partial3':sum(r[6]=='PARTIAL_3' for r in rows),'partial2':sum(r[6]=='PARTIAL_2' for r in rows),'triplets':trip,'real_graph_rectangles':real,'null_mean':sum(null)/len(null),'null_max':max(null) if null else 0,'null_p':(1+sum(q>=real for q in null))/(len(null)+1),'algebra_equal_hosts':sum(r[5] for r in rows),'algebra_unequal_hosts':sum(not r[5] for r in rows)}
write_tsv(R/'gdt003_paradigm_rectangles.tsv',rect)

# Interaction classification and distribution-derived attachment grouping.
inter=[]
for (a,b),z in pair_stats.items():
 ea,eb=full_edges[a],full_edges[b];potential=set()
 for x in sorted(forms):
  c=cells_for(x,a,b)
  if c and c[3] is not None and c[4] is not None:potential.add(x)
 fa,fb=OPS[a][1],OPS[b][1]
 a_app=[x for x in sorted(forms) if fa(x) is not None];b_app=[x for x in sorted(forms) if fb(x) is not None]
 a_rate=sum(fa(x) in forms for x in a_app)/len(a_app) if a_app else 0;b_rate=sum(fb(x) in forms for x in b_app)/len(b_app) if b_app else 0
 b_after_den=[x for x in sorted(forms) if fa(x) in forms and fb(fa(x)) is not None];a_after_den=[x for x in sorted(forms) if fb(x) in forms and fa(fb(x)) is not None]
 b_after=sum(fb(fa(x)) in forms for x in b_after_den)/len(b_after_den) if b_after_den else 0;a_after=sum(fa(fb(x)) in forms for x in a_after_den)/len(a_after_den) if a_after_den else 0
 br=b_after/b_rate if b_rate else None;ar=a_after/a_rate if a_rate else None
 stable_rates=br is not None and ar is not None and .5<=br<=2 and .5<=ar<=2
 edition_complete={}
 for ed,u in edition_forms.items():
  edition_complete[ed]=sum((lambda c:c is not None and c[3] is not None and c[3]==c[4] and all(v in u for v in c[:4]))(cells_for(x,a,b)) for x in sorted(u))
 if z['algebra_unequal_hosts']>z['algebra_equal_hosts']:cl='ORDER_DEPENDENT'
 elif z['triplets']<3:cl='INSUFFICIENT_DATA'
 elif z['complete']==0:cl='MUTUALLY_EXCLUSIVE'
 elif z['complete']>=3 and z['null_p']<=.05 and stable_rates:cl='INDEPENDENT'
 else:cl='CONDITIONALLY_COMPATIBLE'
 inter.append({'operation_A':a,'operation_B':b,'A_inferred_class':next(x['inferred_attachment_class'] for x in trans if x['transformation']==a),'B_inferred_class':next(x['inferred_attachment_class'] for x in trans if x['transformation']==b),'applicable_hosts':len(potential),'algebra_equal_hosts':z['algebra_equal_hosts'],'algebra_unequal_hosts':z['algebra_unequal_hosts'],'A_base_edge_rate':a_rate,'B_base_edge_rate':b_rate,'A_after_B_rate':a_after,'B_after_A_rate':b_after,'A_after_B_over_base_ratio':ar if ar is not None else '','B_after_A_over_base_ratio':br if br is not None else '','complete_rectangles':z['complete'],'ZL3b_complete_rectangles':edition_complete['ZL3b'],'IT2a_complete_rectangles':edition_complete['IT2a'],'RF1b_complete_rectangles':edition_complete['RF1b'],'three_cell_rectangles':z['partial3'],'two_cell_rectangles':z['partial2'],'completion_rate_given_three':z['complete']/z['triplets'] if z['triplets'] else 0,'random_graph_mean':z['null_mean'],'random_graph_max':z['null_max'],'random_graph_inclusive_p':z['null_p'],'interaction_class':cl,'claim_state':'FORMAL_INTERACTION_NO_SLOT_MEANING'})
write_tsv(R/'gdt003_transformation_interactions.tsv',inter)

# Fourth-cell tasks with target type hidden globally; only other-host support is used.
host_tasks=[]
for (a,b),z in pair_stats.items():
 if z['algebra_equal_hosts']==0:continue
 for x in sorted(forms):
  c=cells_for(x,a,b)
  if not c or c[3] is None or c[3]!=c[4]:continue
  _,ax,bx,target,_=c
  if not all(q in forms for q in (x,ax,bx)):continue
  other_trip=other_complete=0
  for y in sorted(forms-{x,target}):
   d=cells_for(y,a,b)
   if not d or d[3] is None or d[3]!=d[4]:continue
   if all(q in forms-{target} for q in d[:3]):
    other_trip+=1;other_complete+=int(d[3] in forms-{target})
  if other_complete<1:continue
  y=int(target in forms);p=(other_complete+.5)/(other_trip+1)
  target_loci=sorted(fm[target]['loci']) if y else []
  host_tasks.append({'evaluation':'HOST_CELL_HOLDOUT','fold_id':x,'operation_A':a,'operation_B':b,'base_X':x,'observed_A_X':ax,'observed_B_X':bx,'predicted_fourth':target,'target_hidden_from_model':1,'target_present':y,'target_physical_loci':len(target_loci),'target_locus_examples':';'.join(target_loci[:8]),'target_folios':';'.join(sorted(fm[target]['folios'])) if y else '','training_other_triplets':other_trip,'training_other_complete':other_complete,'paradigm_score':math.log2(p),'ngram_score':'PENDING','whole_group_frequency_score':math.log2(1+freq[x])+math.log2(1+freq[ax])+math.log2(1+freq[bx]),'nearest_edit_score':-sum(lev(target,q) for q in (x,ax,bx))/3,'exact_prediction_correct':y,'top1_correct':'PENDING','top5_correct':'PENDING','model_exposure':'TARGET_FORM_REMOVED_GLOBALLY_BEFORE_SCORING','claim_state':'COMPUTATIONAL_HOLDOUT_NOT_NEW_EVIDENCE'})

def fold_predictions(axis):
 values=sorted({x[axis] for x in records});out=[]
 total_novel=0
 for val in values:
  train=[x for x in records if x[axis]!=val];held=[x for x in records if x[axis]==val];tf=set(x['surface'] for x in train);hf=set(x['surface'] for x in held);tc=Counter(x['surface'] for x in train);lm=kt_lm(tc)
  total_novel+=len(hf-tf)
  eligible=[]
  for a,b in itertools.combinations(OPS,2):
   ea,eb=edges(a,tf),edges(b,tf)
   if len(ea)<5 or len(eb)<5:continue
   complete=trip=0
   for x in sorted(tf):
    c=cells_for(x,a,b)
    if not c or c[3] is None or c[3]!=c[4]:continue
    if all(q in tf for q in c[:3]):trip+=1;complete+=int(c[3] in tf)
   if complete<1:continue
   rate=(complete+.5)/(trip+1)
   for x in sorted(tf):
    c=cells_for(x,a,b)
    if not c or c[3] is None or c[3]!=c[4]:continue
    _,ax,bx,t,_=c
    if all(q in tf for q in (x,ax,bx)) and t not in tf:
     eligible.append({'a':a,'b':b,'x':x,'ax':ax,'bx':bx,'t':t,'p':rate,'trip':trip,'complete':complete,'ps':math.log2(rate)+math.log2(1+min(len(ea),len(eb)))/20,'ng':lm(t),'wf':sum(math.log2(1+tc[q]) for q in (x,ax,bx)),'ed':-sum(lev(t,q) for q in (x,ax,bx))/3})
  best={}
  for q in eligible:
   if q['t'] not in best or (q['ps'],q['a'],q['b'],q['x'])>(best[q['t']]['ps'],best[q['t']]['a'],best[q['t']]['b'],best[q['t']]['x']):best[q['t']]=q
  zz=list(best.values())
  ranks={m:{id(q):r for r,q in enumerate(sorted(zz,key=lambda z:(-z[m],z['t'])),1)} for m in ('ps','ng','wf','ed')}
  for q in zz:
   y=int(q['t'] in hf);loc=sorted({x['locus'] for x in held if x['surface']==q['t']})
   out.append({'evaluation':axis.upper()+'_HELD_NOVEL_FORM','fold_id':val,'operation_A':q['a'],'operation_B':q['b'],'base_X':q['x'],'observed_A_X':q['ax'],'observed_B_X':q['bx'],'predicted_fourth':q['t'],'target_hidden_from_model':1,'target_present':y,'target_physical_loci':len(loc),'target_locus_examples':';'.join(loc[:8]),'target_folios':';'.join(sorted({x['folio'] for x in held if x['surface']==q['t']})),'training_other_triplets':q['trip'],'training_other_complete':q['complete'],'paradigm_score':q['ps'],'ngram_score':q['ng'],'whole_group_frequency_score':q['wf'],'nearest_edit_score':q['ed'],'exact_prediction_correct':y,'paradigm_rank_in_fold':ranks['ps'][id(q)],'ngram_rank_in_fold':ranks['ng'][id(q)],'whole_frequency_rank_in_fold':ranks['wf'][id(q)],'nearest_edit_rank_in_fold':ranks['ed'][id(q)],'model_exposure':'ENTIRE_PHYSICAL_'+axis.upper()+'_EXCLUDED','claim_state':'COMPUTATIONAL_HOLDOUT_NOT_NEW_EVIDENCE'})
 return out,total_novel

# Host-task n-gram scores remove the target type contribution before scoring.
for q in host_tasks:
 tc=freq.copy()
 if q['target_present']:del tc[q['predicted_fourth']]
 q['ngram_score']=kt_lm(tc)(q['predicted_fourth'])
folio_tasks,folio_novel_total=fold_predictions('folio');section_tasks,section_novel_total=fold_predictions('section')

# Rank host-cell candidates within each base host for top-k reporting.
byhost=defaultdict(list)
for q in host_tasks:byhost[q['base_X']].append(q)
for z in byhost.values():
 for score,field in [('paradigm_score','paradigm_rank_in_fold'),('ngram_score','ngram_rank_in_fold'),('whole_group_frequency_score','whole_frequency_rank_in_fold'),('nearest_edit_score','nearest_edit_rank_in_fold')]:
  for i,q in enumerate(sorted(z,key=lambda q:(-float(q[score]),q['predicted_fourth'])),1):q[field]=i
 for q in z:q['top1_correct']=int(q['paradigm_rank_in_fold']==1 and q['target_present']);q['top5_correct']=int(q['paradigm_rank_in_fold']<=5 and q['target_present'])

pred=host_tasks+folio_tasks+section_tasks
write_tsv(R/'gdt003_holdout_predictions.tsv',pred)

def metrics(rr,score,target_denominator):
 ys=[int(x['target_present']) for x in rr];ss=[float(x[score]) for x in rr];keys=['|'.join((x['evaluation'],x['fold_id'],x['operation_A'],x['operation_B'],x['base_X'],x['predicted_fourth'])) for x in rr];k=sum(ys);lo,hi=wilson(k,len(rr));unique_correct=len({(x['fold_id'] if x['evaluation']!='HOST_CELL_HOLDOUT' else 'GLOBAL',x['predicted_fourth']) for x in rr if int(x['target_present'])});return {'n':len(rr),'positives':k,'unique_correct_targets':unique_correct,'precision':k/len(rr) if rr else 0,'precision_ci_low':lo,'precision_ci_high':hi,'recall':unique_correct/target_denominator if target_denominator else 0,'coverage_of_held_novel_types':unique_correct/target_denominator if target_denominator else 0,'target_denominator':target_denominator,'auc':auc(ss,ys),'average_precision':ap(ss,ys,keys),'mean_positive_score':sum(s for s,y in zip(ss,ys) if y)/k if k else None,'mean_negative_score':sum(s for s,y in zip(ss,ys) if not y)/(len(rr)-k) if len(rr)>k else None}
base=[]
for ev,rr,den in [('HOST_CELL_HOLDOUT',host_tasks,len(forms)),('FOLIO_HELD_NOVEL_FORM',folio_tasks,folio_novel_total),('SECTION_HELD_NOVEL_FORM',section_tasks,section_novel_total)]:
 for name,sc in [('PARADIGM_COMPLETION_RATE','paradigm_score'),('CHARACTER_ORDER4_KT','ngram_score'),('VISIBLE_WHOLE_GROUP_FREQUENCY','whole_group_frequency_score'),('NEAREST_EDIT_DISTANCE','nearest_edit_score')]:
  m=metrics(rr,sc,den);rf={'PARADIGM_COMPLETION_RATE':'paradigm_rank_in_fold','CHARACTER_ORDER4_KT':'ngram_rank_in_fold','VISIBLE_WHOLE_GROUP_FREQUENCY':'whole_frequency_rank_in_fold','NEAREST_EDIT_DISTANCE':'nearest_edit_rank_in_fold'}[name];base.append({'evaluation':ev,'baseline':name,**m,'top1_hits':sum(int(x[rf])==1 and int(x['target_present']) for x in rr),'top5_hits':sum(int(x[rf])<=5 and int(x['target_present']) for x in rr),'comparison_scope':'RANKING/EXISTENCE OF EXACT FORMAL FOURTH CELL'})
base.append({'evaluation':'WHOLE_MANUSCRIPT_RECTANGLES','baseline':'MATCHED_RANDOMIZED_TRANSFORMATION_GRAPHS','n':len(pair_stats),'positives':sum(z['complete']>0 for z in pair_stats.values()),'precision':'','precision_ci_low':'','precision_ci_high':'','auc':'','average_precision':'','mean_positive_score':'','mean_negative_score':'','top1_hits':'','top5_hits':'','comparison_scope':'256 edge-count/source-set/target-multiset-preserving nulls per operation pair; see interactions'})
base.append({'evaluation':'ISOLATED_MISSING_GROUP','baseline':'GDT001_CONTEXT_MIXER','n':0,'positives':0,'precision':'','precision_ci_low':'','precision_ci_high':'','auc':'','average_precision':'','mean_positive_score':'','mean_negative_score':'','top1_hits':'','top5_hits':'','comparison_scope':'NOT_DIRECTLY_COMPARABLE: decoder requires full canonical-locus serialization and context, not an isolated group API'})
write_tsv(R/'gdt003_baseline_comparison.tsv',base)

# Split/join productivity and explicit counterexamples.
split_ops={x['transformation'] for x in trans if int(x['split_join_supported_hosts'])>0};split_host=[q for q in host_tasks if q['operation_A'] in split_ops or q['operation_B'] in split_ops];nosplit=[q for q in host_tasks if q['operation_A'] not in split_ops and q['operation_B'] not in split_ops]
folio_m=next(x for x in base if x['evaluation']=='FOLIO_HELD_NOVEL_FORM' and x['baseline']=='PARADIGM_COMPLETION_RATE')
section_m=next(x for x in base if x['evaluation']=='SECTION_HELD_NOVEL_FORM' and x['baseline']=='PARADIGM_COMPLETION_RATE')
ng_f=next(x for x in base if x['evaluation']=='FOLIO_HELD_NOVEL_FORM' and x['baseline']=='CHARACTER_ORDER4_KT')
best_novel=[x for x in folio_tasks if int(x['target_present']) and int(x['target_physical_loci'])>0]
best_novel.sort(key=lambda x:(int(x['target_physical_loci']),x['fold_id'],x['predicted_fourth']))
counter=[
 {'candidate':'UNIVERSAL_COMBINATORIAL_SLOTS','counterexample':'Many operation pairs are order-dependent, mutually exclusive, or have no complete rectangle.','evidence':f"interaction classes {dict(Counter(x['interaction_class'] for x in inter))}",'impact':'No single unrestricted algebra is licensed.'},
 {'candidate':'SPLIT_JOIN_GUARANTEES_PRODUCTIVITY','counterexample':'Manual split/join support is sparse and is tested only as a subgroup.','evidence':f"split-supported host tasks {len(split_host)} with {sum(int(x['target_present']) for x in split_host)} completions; substring-only {len(nosplit)} with {sum(int(x['target_present']) for x in nosplit)}",'impact':'Spaces remain formal boundary evidence, not linguistic morphology.'},
 {'candidate':'AMBIGUITY_FREE_GENERALIZATION','counterexample':'The primary corpus excludes every reading/topology disagreement.','evidence':f'{ambiguous} physical group keys excluded; edition edge counts remain separate in transformations.tsv','impact':'Any union-reading increase is sensitivity, not replication.'},
 {'candidate':'GLOBAL_SOURCE_MODEL_SUPERIORITY','counterexample':'The context mixer cannot score an isolated missing group without its serialized context.','evidence':'No cross-normalized context-mixer baseline is claimed.','impact':'GDT003 compares explicit isolated-form baselines only.'},
 {'candidate':'PRISTINE_NEW_EVIDENCE','counterexample':'All manuscript readings and transformation families were already public before masking.','evidence':'Targets are hidden computationally from the model, not newly acquired from the manuscript.','impact':'Correct cells are cross-validation, not external confirmation.'},
]
write_tsv(R/'gdt003_counterexamples.tsv',counter)

def safe(v):return -1 if v is None else v
folio_adv=safe(folio_m['average_precision'])-safe(ng_f['average_precision'])
host_m=next(x for x in base if x['evaluation']=='HOST_CELL_HOLDOUT' and x['baseline']=='PARADIGM_COMPLETION_RATE');host_best=max(x['average_precision'] for x in base if x['evaluation']=='HOST_CELL_HOLDOUT' and x['baseline']!='PARADIGM_COMPLETION_RATE')
folio_best=max(x['average_precision'] for x in base if x['evaluation']=='FOLIO_HELD_NOVEL_FORM' and x['baseline']!='PARADIGM_COMPLETION_RATE')
real_sig=sum(x['random_graph_inclusive_p']<=.05 and x['complete_rectangles']>=3 for x in inter)
novel_correct=len(best_novel);section_correct=section_m['positives']
host_adv=safe(host_m['average_precision'])-host_best;folio_best_adv=safe(folio_m['average_precision'])-folio_best
if novel_correct>=5 and section_correct>=2 and folio_best_adv>=.05 and host_adv>=.05 and real_sig>=2:decision='PRODUCTIVE COMPOSITION SUPPORTED'
elif novel_correct>0 and real_sig>0 and (folio_best_adv>=.02 or host_adv>=.02):decision='LIMITED/LOCAL COMPOSITION ONLY'
elif novel_correct==0 and real_sig==0:decision='PRODUCTIVE COMPOSITION FALSIFIED'
else:decision='NOT DISTINGUISHABLE FROM STRING STATISTICS'
result={'artifact':'GDT003_PARADIGM_PREDICTION_V1','status':decision,'corpus':{'stable_physical_groups':len(records),'stable_form_types':len(forms),'ambiguous_or_topology_disagreement_keys_excluded':ambiguous,'alternate_readings_not_replications':True},'transformations':{'count':len(trans),'retained':sum(int(x['retained_for_prediction']) for x in trans),'attachment_classes':dict(Counter(x['inferred_attachment_class'] for x in trans))},'rectangles':{'rows':len(rect),'complete':sum(x['structure_state']=='COMPLETE_4' for x in rect),'partial3':sum(x['structure_state']=='PARTIAL_3' for x in rect),'partial2':sum(x['structure_state']=='PARTIAL_2' for x in rect),'operation_pairs_with_random_p_le_05':real_sig},'prediction_metrics':{'host_cell':metrics(host_tasks,'paradigm_score',len(forms)),'folio':folio_m,'section':section_m,'host_AP_advantage_over_best_string_baseline':host_adv,'folio_AP_advantage_over_ngram':folio_adv,'folio_AP_advantage_over_best_string_baseline':folio_best_adv,'folio_exact_novel_correct':novel_correct,'section_exact_novel_correct':section_correct},'highest_value_model_hidden_predictions':best_novel[:25],'split_join':{'supported_operations':sorted(split_ops),'supported_host_tasks':len(split_host),'supported_correct':sum(int(x['target_present']) for x in split_host),'substring_only_tasks':len(nosplit),'substring_only_correct':sum(int(x['target_present']) for x in nosplit)},'interaction_classes':dict(Counter(x['interaction_class'] for x in inter)),'holdout':{'f84r_formal_retained_or_scored':False},'inputs':{str(p.relative_to(R)):sha(p) for p in [S/'source_separator_transcription.tsv',S/'source_sta_group_alignment.tsv',R/'gdt002_morphology_split_join.tsv',R/'gdt002_morphology_results.json',R/'GDT003_METHOD.md',R/'run_gdt003_paradigm_prediction.py',R/'GDT002_YOLO_LEDGER.tsv']},'documents':{str(p.relative_to(R)):sha(p) for p in [R/'GDT003_PARADIGM_PREDICTION_REPORT.md',R/'GDT002_CURRENT_SUMMARY.md']},'outputs':{n:sha(R/n) for n in ['gdt003_transformations.tsv','gdt003_paradigm_rectangles.tsv','gdt003_holdout_predictions.tsv','gdt003_transformation_interactions.tsv','gdt003_baseline_comparison.tsv','gdt003_counterexamples.tsv']},'claim_ceiling':'Predictive formal source-group composition only. No morpheme, operator meaning, part of speech, semantic role, historical language, plaintext, or translation.'}
(R/'gdt003_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(decision);print(result['corpus']);print(result['rectangles']);print(result['prediction_metrics']);print('novel',[(x['fold_id'],x['predicted_fourth'],x['operation_A'],x['operation_B']) for x in best_novel[:15]])
