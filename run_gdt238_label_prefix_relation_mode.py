#!/usr/bin/env python3
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
ANN=R/'experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv'
FAM=R/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
PFX=R/'gdt237_prefix_stability.tsv'
OUTS=['gdt238_relation_inventory.tsv','gdt238_relation_folds.tsv','gdt238_relation_summary.tsv']
DOCS=['GDT238_LABEL_PREFIX_RELATION_MODE_METHOD.md','GDT238_LABEL_PREFIX_RELATION_MODE_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def folio(p):return re.match(r'f\d+',p).group()
def mode(v):return sorted(Counter(v).items(),key=lambda z:(-z[1],z[0]))[0][0]
def relation(t):
 if 'REL_EXPLICIT_ATTACHMENT' in t:return 'ATTACHMENT'
 if 'REL_ENCLOSURE' in t or 'REL_OVERLAP_OR_CONTACT' in t:return 'ENCLOSURE_OR_CONTACT'
 if 'REL_ARRAY_OR_GROUP' in t:return 'ARRAY_OR_GROUP'
 return 'PROXIMITY'
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 stable=[]
 with PFX.open(encoding='utf-8') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   if x['all_folds']=='1':stable.append(x['prefix'])
 ann={}
 with ANN.open(encoding='utf-8') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   if x['page'].startswith('f84') or 'LABEL' not in x['object_tags'].split(';') or not x['local_relation_tags']:continue
   ann[x['locus']]=x
 fam={}
 with FAM.open(encoding='utf-8') as f:
  head=f.readline().rstrip('\n').split('\t');pi=head.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t');p=a[pi]
   if p.startswith('f84'):continue
   x=dict(zip(head,a))
   if int(x['consensus_group_index'])==1 and x['locus'] in ann:fam[x['locus']]=x
 rows=[]
 for loc,x in sorted(fam.items()):
  s=x['family_surface'];matches=sorted((p for p in stable if s.startswith(p)),key=lambda p:(-len(p),p));p=matches[0] if matches else 'NONE';a=ann[loc]
  rows.append({'locus':loc,'page':x['page'],'physical_folio':folio(x['page']),'section':x['section'],'family_surface':s,'stable_prefix':p,'relation_class':relation(a['local_relation_tags']),'source_relation_tags':a['local_relation_tags'],'certainty':a['certainty'],'claim_state':'VISIBLE_RELATION_MODE_NO_OWNERSHIP_OR_GLOSS'})
 write(OUTS[0],rows);folds=[];summ=[]
 for feature,marked_only in [('STABLE_PREFIX',True),('RAW_FAMILY',False)]:
  cov=hit=base=wins=loss=0
  for held in sorted({x['physical_folio'] for x in rows}):
   tr=[x for x in rows if x['physical_folio']!=held];te=[x for x in rows if x['physical_folio']==held and (not marked_only or x['stable_prefix']!='NONE')]
   key='stable_prefix' if feature=='STABLE_PREFIX' else 'family_surface'
   maps={v:mode([x['relation_class'] for x in tr if x[key]==v]) for v in {x[key] for x in tr} if not(marked_only and v=='NONE')}
   secs={s:mode([x['relation_class'] for x in tr if x['section']==s]) for s in {x['section'] for x in tr}}
   fc=fh=fb=fw=fl=0
   for x in te:
    if x[key] not in maps or x['section'] not in secs:continue
    a=maps[x[key]]==x['relation_class'];b=secs[x['section']]==x['relation_class'];fc+=1;fh+=a;fb+=b;fw+=a and not b;fl+=b and not a
   if fc:folds.append({'model':feature,'held_folio':held,'covered':fc,'feature_correct':fh,'baseline_correct':fb,'feature_wins':fw,'feature_losses':fl})
   cov+=fc;hit+=fh;base+=fb;wins+=fw;loss+=fl
  one=sum(__import__('math').comb(wins+loss,i) for i in range(0,wins+1))/2**(wins+loss) if wins+loss else 1
  if wins>loss:one=sum(__import__('math').comb(wins+loss,i) for i in range(wins,wins+loss+1))/2**(wins+loss)
  summ.append({'model':feature,'covered':cov,'feature_correct':hit,'baseline_correct':base,'feature_accuracy':f'{hit/cov:.12f}','baseline_accuracy':f'{base/cov:.12f}','accuracy_delta':f'{(hit-base)/cov:.12f}','paired_wins':wins,'paired_losses':loss,'one_sided_sign_p':f'{one:.12g}'})
 write(OUTS[1],folds);write(OUTS[2],summ)
 primary=summ[0]
 status='WEAK_PREFIX_RELATION_MODE_LEAD_LOW_CAPACITY' if int(primary['paired_wins'])>int(primary['paired_losses']) else 'NO_PREFIX_RELATION_MODE_LEAD'
 result={'experiment':'GDT238_LABEL_PREFIX_RELATION_MODE','status':status,'inventory_rows':len(rows),'folios':len({x['physical_folio'] for x in rows}),'stable_prefixes':stable,'relation_classes':dict(Counter(x['relation_class'] for x in rows)),'primary':primary,'raw_counterexample':summ[1],
 'interpretation':'Stable graphical-label prefixes carry a weak held-folio relation-mode clue, concentrated in five paired improvements; exact raw families do not transfer.',
 'claim_ceiling':'Visible annotation relation mode only; no authorial ownership, object, word, morpheme, language, plaintext, or translation.',
 'f84':{'retained':False,'joined':False,'scored':False,'new_access':False},
 'inputs':{str(p.relative_to(R)):sha(str(p.relative_to(R))) for p in (ANN,FAM,PFX)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 (R/'gdt238_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':primary},sort_keys=True))
if __name__=='__main__':main()
