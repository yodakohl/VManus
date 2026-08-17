#!/usr/bin/env python3
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
EXT=R/'gdt176_external_role_units.tsv';FIELDS=R/'gdt241_f82r_hpr2_fields.tsv';COORD=R/'gdt242_f82r_paragraph_coordinate.tsv';PROJ=R/'gdt002_grammar_projection.tsv'
OUTS=['gdt243_f82r_missingness_role_projection.tsv','gdt243_f82r_paragraph_uncertainty.tsv','gdt243_role_summary.tsv']
DOCS=['GDT243_F82R_MISSINGNESS_AWARE_ROLE_METHOD.md','GDT243_F82R_MISSINGNESS_AWARE_ROLE_REPORT.md']
CLASSES=('OPENER','OPERATION','INGREDIENT','TOOL','CLOSER');AB={'OPENER':'UNRESOLVED_EDGE_CLASS','OPERATION':'INSTRUCTION_CLAUSE_LIKE','INGREDIENT':'SHORT_ARGUMENT_LIKE','TOOL':'SHORT_ARGUMENT_LIKE','CLOSER':'RECORD_CLOSER_LIKE'}
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def fit(X,y):
 mean=X.mean(0);scale=X.std(0);scale[scale<1e-9]=1;Z=np.column_stack([np.ones(len(X)),(X-mean)/scale]);Y=np.eye(5)[y];b=np.zeros((5,5));b[0]=np.log(np.bincount(y,minlength=5)/len(y)+1e-12);m=np.zeros_like(b);v=np.zeros_like(b)
 for step in range(1,801):
  z=Z@b;z-=z.max(1,keepdims=True);p=np.exp(z);p/=p.sum(1,keepdims=True);g=Z.T@(p-Y)/len(y);g[1:]+=.001*b[1:];m=.9*m+.1*g;v=.999*v+.001*g*g;mh=m/(1-.9**step);vh=v/(1-.999**step);b-=.03*mh/(np.sqrt(vh)+1e-8)
 return b,mean,scale
def pred(X,model):
 b,m,s=model;Z=np.column_stack([np.ones(len(X)),np.clip((X-m)/s,-4,4)]);z=Z@b;return z.argmax(1)
def main():
 er=read(EXT);X=np.array([[float(x['relative_position']),float(x['relative_position'])**2,math.log2(1+int(x['span_token_count'])),math.log2(1+int(x['record_unit_count']))] for x in er]);y=np.array([CLASSES.index(x['oracle_role']) for x in er]);model=fit(X,y)
 fields=read(FIELDS);coord=read(COORD);cb={x['locus']:x for x in coord};maxg=defaultdict(int)
 with PROJ.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t')
   if a[pi]!='f82r':continue
   x=dict(zip(h,a))
   if x['kind']=='P':maxg[x['locus']]=max(maxg[x['locus']],int(x['source_group_count']))
 byline=defaultdict(list)
 for x in fields:byline[x['locus']].append(x)
 para=[];out=[]
 for pid in ('P1','P2','P3'):
  lines=sorted((x for x in coord if x['paragraph_id']==pid),key=lambda x:int(x['paragraph_line_ordinal']));known=sum(int(x['hpr2_field_count']) for x in lines);missing=[x for x in lines if x['hpr2_available']=='0'];mn=len(missing);mx=sum(maxg[x['locus']] for x in missing)
  para.append({'paragraph_id':pid,'physical_lines':len(lines),'covered_lines':sum(x['hpr2_available']=='1' for x in lines),'known_fields':known,'missing_lines':mn,'missing_field_min':mn,'missing_field_max':mx,'total_field_min':known+mn,'total_field_max':known+mx})
  known_before=0
  for line in lines:
   if line['hpr2_available']=='0':continue
   lnum=int(line['paragraph_line_ordinal']);before_missing=[x for x in missing if int(x['paragraph_line_ordinal'])<lnum];after_missing=[x for x in missing if int(x['paragraph_line_ordinal'])>lnum]
   bmin=len(before_missing);bmax=sum(maxg[x['locus']] for x in before_missing);amin=len(after_missing);amax=sum(maxg[x['locus']] for x in after_missing)
   lf=sorted(byline[line['locus']],key=lambda x:int(x['line_field_ordinal']))
   for local,x in enumerate(lf,1):
    cases=[]
    for bm in range(bmin,bmax+1):
     for am in range(amin,amax+1):
      total=known+bm+am;ordinal=known_before+bm+local;rel=ordinal/total;cases.append([rel,rel*rel,math.log2(1+int(x['field_group_count'])),math.log2(1+total)])
    ids=pred(np.array(cases),model);classes=sorted({CLASSES[int(i)] for i in ids});abstract=sorted({AB[c] for c in classes});robust=len(abstract)==1
    out.append({'page':'f82r','paragraph_id':pid,'locus':x['locus'],'line_field_ordinal':x['line_field_ordinal'],'field_group_count':x['field_group_count'],'source_tokens':x['source_tokens'],'page_hosts':x['page_hosts'],'line_field_end':x['line_field_end'],'missing_before_min':bmin,'missing_before_max':bmax,'missing_after_min':amin,'missing_after_max':amax,'feasible_coordinates':len(cases),'predicted_five_way_classes':'|'.join(classes),'predicted_abstract_classes':'|'.join(abstract),'robust_abstract_role_like':abstract[0] if robust else 'UNRESOLVED_MISSINGNESS_SENSITIVE','robust_under_missingness':int(robust),'semantic_value':'UNASSIGNED'})
   known_before+=len(lf)
 write(OUTS[0],out);write(OUTS[1],para)
 count=Counter(x['robust_abstract_role_like'] for x in out);summary=[{'role_like':k,'fields':v,'fraction':f'{v/len(out):.12f}'} for k,v in sorted(count.items())];write(OUTS[2],summary)
 result={'experiment':'GDT243_F82R_MISSINGNESS_AWARE_ROLE','status':'F82R_MISSINGNESS_AWARE_ROLE_PROJECTION_BUILT_FORMAL_ANALOGY_ONLY','fields':len(out),'robust_fields':sum(int(x['robust_under_missingness']) for x in out),'unresolved_fields':sum(not int(x['robust_under_missingness']) for x in out),'role_counts':dict(count),'paragraph_uncertainty':para,
 'interpretation':'The external readable-recipe position/length instrument is applied across the complete feasible missing-field range; retained classes are robust abstract analogies, not semantic roles.',
 'claim_ceiling':'Missingness-robust position/length role likeness only; no field ownership, ingredient, operation, object, word, language, plaintext, or translation.',
 'f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (EXT,FIELDS,COORD,PROJ)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt243_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'fields':len(out),'robust':result['robust_fields'],'counts':result['role_counts'],'paragraphs':para},sort_keys=True))
if __name__=='__main__':main()
