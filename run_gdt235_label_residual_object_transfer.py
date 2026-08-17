#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ANN=ROOT/'experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv';FAM=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv';MAN=ROOT/'gdt233_prefix_manifest.tsv'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def modal(rr):
 c=Counter(r['object_class'] for r in rr);return sorted(c,key=lambda k:(-c[k],k))[0]
def main():
 ann={}
 with ANN.open(encoding='utf-8') as h:
  header=h.readline().rstrip('\n').split('\t')
  for raw in h:
   if raw.startswith('f84'):continue
   r=dict(zip(header,next(csv.reader([raw],delimiter='\t'))))
   if 'LABEL' in r['object_tags'].split(';'):ann[r['locus']]=r
 whitelist=set(ann);fam=defaultdict(list)
 with FAM.open(encoding='utf-8') as h:
  header=h.readline().rstrip('\n').split('\t');li=header.index('locus')
  for raw in h:
   parts=raw.rstrip('\n').split('\t');locus=parts[li]
   if locus not in whitelist:continue
   fam[locus].append(dict(zip(header,parts)))
 for locus in fam:fam[locus].sort(key=lambda r:int(r['consensus_group_index']))
 prefixes={r['prefix'] for r in read(MAN) if r['selection_status']=='STRICT_TRAINING_SELECTED'}
 def strip(s):
  m=sorted((p for p in prefixes if s.startswith(p)),key=lambda p:(-len(p),p));return (m[0],s[len(m[0]):] or 'EMPTY') if m else ('NONE',s)
 def obj(tags):
  t=set(tags.split(';'))
  for source,target in [('PLANT','PLANT'),('WATER_OR_APPARATUS','WATER_OR_APPARATUS'),('ROSETTE_OR_MAP','ROSETTE_OR_MAP'),('STAR_OR_SKY','ASTRONOMICAL'),('FIGURE','FIGURE_ONLY')]:
   if source in t:return target
  return 'OTHER_LABEL'
 inventory=[]
 for locus,a in sorted(ann.items()):
  if locus not in fam:continue
  expr='|'.join(r['family_surface'] for r in fam[locus]);pre,res=strip(expr);m=re.match(r'f\d+',a['page']);folio=m.group(0) if m else a['page']
  inventory.append({'locus':locus,'page':a['page'],'physical_folio':folio,'section':fam[locus][0]['section'],'kind':fam[locus][0]['kind'],'object_class':obj(a['object_tags']),'object_tags':a['object_tags'],'raw_family':expr,'transferred_prefix':pre,'strict_residual':res,'certainty':a['certainty'],'relation_scope':a['relation_scope'],'claim_state':'COARSE_VISIBLE_OBJECT_ENDPOINT_NO_GLOSS'})
 assert len(inventory)==703 and all(not r['page'].startswith('f84') for r in inventory)
 write(ROOT/'gdt235_label_object_inventory.tsv',inventory)
 models=[('RAW_FAMILY','raw_family'),('STRICT_RESIDUAL','strict_residual'),('TRANSFERRED_PREFIX','transferred_prefix')]
 folds=[];summary=[]
 for name,feat in models:
  cov=hit=base=0;positive=negative=tie=0
  for held in sorted({r['physical_folio'] for r in inventory}):
   train=[r for r in inventory if r['physical_folio']!=held];test=[r for r in inventory if r['physical_folio']==held];n=h=b=0
   for r in test:
    if r[feat] in {'NONE','EMPTY'}:continue
    seen=[x for x in train if x[feat]==r[feat]]
    if not seen:continue
    pred=modal(seen);sec=[x for x in train if x['section']==r['section']];prior=modal(sec or train);n+=1;h+=pred==r['object_class'];b+=prior==r['object_class']
   if n:
    positive+=h>b;negative+=h<b;tie+=h==b;folds.append({'split':'HELD_FOLIO','model':name,'held':held,'covered':n,'feature_correct':h,'baseline_correct':b,'accuracy_delta':f'{(h-b)/n:.12f}'})
   cov+=n;hit+=h;base+=b
  summary.append({'split':'HELD_FOLIO','model':name,'covered':cov,'feature_correct':hit,'baseline_correct':base,'feature_accuracy':f'{hit/cov:.12f}','baseline_accuracy':f'{base/cov:.12f}','accuracy_delta':f'{(hit-base)/cov:.12f}','positive_folds':positive,'negative_folds':negative,'tied_folds':tie})
  cov=hit=base=0
  for held in sorted({r['section'] for r in inventory}):
   train=[r for r in inventory if r['section']!=held];test=[r for r in inventory if r['section']==held];n=h=b=0;prior=modal(train)
   for r in test:
    if r[feat] in {'NONE','EMPTY'}:continue
    seen=[x for x in train if x[feat]==r[feat]]
    if not seen:continue
    pred=modal(seen);n+=1;h+=pred==r['object_class'];b+=prior==r['object_class']
   if n:folds.append({'split':'HELD_SECTION','model':name,'held':held,'covered':n,'feature_correct':h,'baseline_correct':b,'accuracy_delta':f'{(h-b)/n:.12f}'})
   cov+=n;hit+=h;base+=b
  summary.append({'split':'HELD_SECTION','model':name,'covered':cov,'feature_correct':hit,'baseline_correct':base,'feature_accuracy':f'{hit/cov:.12f}','baseline_accuracy':f'{base/cov:.12f}','accuracy_delta':f'{(hit-base)/cov:.12f}','positive_folds':sum(int(r['feature_correct'])>int(r['baseline_correct']) for r in folds if r['split']=='HELD_SECTION' and r['model']==name),'negative_folds':sum(int(r['feature_correct'])<int(r['baseline_correct']) for r in folds if r['split']=='HELD_SECTION' and r['model']==name),'tied_folds':sum(int(r['feature_correct'])==int(r['baseline_correct']) for r in folds if r['split']=='HELD_SECTION' and r['model']==name)})
 write(ROOT/'gdt235_object_transfer_folds.tsv',folds);write(ROOT/'gdt235_object_transfer_summary.tsv',summary)
 q13=[r for r in folds if r['split']=='HELD_SECTION' and r['held']=='B']
 result={'experiment':'GDT235_LABEL_RESIDUAL_OBJECT_TRANSFER','status':'LABEL_RESIDUAL_OBJECT_CLASS_NOT_TRANSFERABLE_SECTION_DOMINATES','inventory_rows':len(inventory),'folios':len({r['physical_folio'] for r in inventory}),'object_classes':dict(sorted(Counter(r['object_class'] for r in inventory).items())),'held_folio':{r['model']:{k:(float(r[k]) if 'accuracy' in k else int(r[k])) for k in ('covered','feature_correct','baseline_correct','feature_accuracy','baseline_accuracy','accuracy_delta')} for r in summary if r['split']=='HELD_FOLIO'},'held_section':{r['model']:{k:(float(r[k]) if 'accuracy' in k else int(r[k])) for k in ('covered','feature_correct','baseline_correct','feature_accuracy','baseline_accuracy','accuracy_delta')} for r in summary if r['split']=='HELD_SECTION'},'q13_held_section':{r['model']:{'covered':int(r['covered']),'feature_correct':int(r['feature_correct']),'baseline_correct':int(r['baseline_correct'])} for r in q13},'interpretation':'Exact residuals do not transfer visible object class beyond section/folio nuisance; graphical prefixes and residuals encode register ecology rather than a recovered object dictionary.','claim_ceiling':'Coarse visible-object prediction only; no label ownership, object name, word, morpheme, sound, language, plaintext, or translation.','f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(ANN.relative_to(ROOT)):sha(ANN),str(FAM.relative_to(ROOT)):sha(FAM),MAN.name:sha(MAN)},'outputs':{},'documents':{},'implementation':{}}
 for n in ('gdt235_label_object_inventory.tsv','gdt235_object_transfer_folds.tsv','gdt235_object_transfer_summary.tsv'):result['outputs'][n]=sha(ROOT/n)
 for n in ('GDT235_LABEL_RESIDUAL_OBJECT_TRANSFER_METHOD.md','GDT235_LABEL_RESIDUAL_OBJECT_TRANSFER_REPORT.md'):
  if (ROOT/n).exists():result['documents'][n]=sha(ROOT/n)
 result['implementation'][Path(__file__).name]=sha(Path(__file__));result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ROOT/'gdt235_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'rows':len(inventory),'held_folio':result['held_folio'],'q13':result['q13_held_section']},sort_keys=True))
if __name__=='__main__':main()
