#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PAIRS=ROOT/'gdt231_visual_homolog_pair_atlas.tsv';MANIFEST=ROOT/'gdt233_prefix_manifest.tsv'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lev(a,b):
 d=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  q=[i]
  for j,y in enumerate(b,1):q.append(min(q[-1]+1,d[j]+1,d[j-1]+(x!=y)))
  d=q
 return d[-1]
def sim(a,b):return 1-lev(a,b)/max(1,len(a),len(b))
def lcp(a,b):
 n=0
 for x,y in zip(a,b):
  if x!=y:break
  n+=1
 return n
def main():
 pairs=read(PAIRS);manifest=read(MANIFEST);prefixes={r['prefix'] for r in manifest if r['selection_status']=='STRICT_TRAINING_SELECTED'}
 def strip(s):
  m=sorted((p for p in prefixes if s.startswith(p)),key=lambda p:(-len(p),p));return (m[0],s[len(m[0]):]) if m else ('',s)
 out=[]
 for r in pairs:
  a,b=r['family_expression_a'],r['family_expression_b'];pa,ra=strip(a);pb,rb=strip(b);raw=sim(a,b);res=sim(ra,rb)
  out.append({'page':r['page'],'unit':r['unit'],'locus_a':r['locus_a'],'locus_b':r['locus_b'],'raw_a':a,'raw_b':b,'prefix_a':pa or 'NONE','prefix_b':pb or 'NONE','residual_a':ra or 'EMPTY','residual_b':rb or 'EMPTY','raw_similarity':f'{raw:.12f}','residual_similarity':f'{res:.12f}','delta_residual_minus_raw':f'{res-raw:.12f}','raw_common_prefix':lcp(a,b),'residual_common_prefix':lcp(ra,rb),'both_residual_nonempty':int(bool(ra and rb)),'claim_state':'REGISTER_RESIDUAL_MECHANISM_DIAGNOSTIC_NO_GLOSS'})
 write(ROOT/'gdt234_residual_homolog_pairs.tsv',out)
 changed=[r for r in out if r['prefix_a']!='NONE' or r['prefix_b']!='NONE'];nonempty=[r for r in changed if r['prefix_a']!='NONE' and r['prefix_b']!='NONE' and int(r['both_residual_nonempty'])==1]
 def summary(name,rr):
  ds=[float(r['delta_residual_minus_raw']) for r in rr]
  return {'scope':name,'pairs':len(rr),'improved':sum(d>1e-12 for d in ds),'degraded':sum(d<-1e-12 for d in ds),'unchanged':sum(abs(d)<=1e-12 for d in ds),'mean_delta':f'{sum(ds)/len(ds):.12f}'}
 summaries=[summary('AT_LEAST_ONE_PREFIX_STRIPPED',changed),summary('BOTH_PREFIXES_STRIPPED_AND_RESIDUALS_NONEMPTY',nonempty),summary('ALL_VISUAL_UNIT_PAIRS',out)]
 write(ROOT/'gdt234_residual_summary.tsv',summaries)
 special=[]
 for name,loci,sensitivity in [('F77V_LEFT_RIGHT_TUBES',{'f77v.2','f77v.4'},False),('F82R_LEFT_RIGHT_WATERFALLS',{'f82r.35','f82r.38'},True),('F78R_NW_NE_GRAPES',{'f78r.1','f78r.2'},False),('F83R_LEFT_RIGHT_TUBE_ENDS',{'f83r.45','f83r.46'},False)]:
  r=next(x for x in out if {x['locus_a'],x['locus_b']}==loci)
  if sensitivity:
   ra=r['raw_a'][4:] if r['raw_a'].startswith('BACA') else r['raw_a'];rb=r['raw_b'][4:] if r['raw_b'].startswith('BACA') else r['raw_b'];note='EXPOSED_BACA_SENSITIVITY'
  else:ra=r['residual_a'];rb=r['residual_b'];note='STRICT_PREFIX_SET'
  special.append({'target':name,'loci':'|'.join(sorted(loci)),'raw_families':f"{r['raw_a']} || {r['raw_b']}",'prefix_rule':note,'residuals':f'{ra} || {rb}','raw_similarity':r['raw_similarity'],'residual_similarity':f'{sim(ra if ra!="EMPTY" else "",rb if rb!="EMPTY" else ""):.12f}','interpretation':'NO_SHARED_CONTENT_RESIDUAL' if lcp(ra,rb)==0 else 'RESIDUAL_REUSE_REMAINS'})
 write(ROOT/'gdt234_special_pairs.tsv',special)
 result={'experiment':'GDT234_LABEL_RESIDUAL_HOMOLOG_TEST','status':'LABEL_PREFIX_EXPLAINS_MOST_HOMOLOG_SIMILARITY_CONTENT_RESIDUAL_NOT_RECOVERED','pairs':len(out),'changed_pairs':len(changed),'both_nonempty_pairs':len(nonempty),'changed_summary':summaries[0],'nonempty_summary':summaries[1],'raw_prefix3_pairs':sum(int(r['raw_common_prefix'])>=3 for r in out),'residual_prefix1_among_raw_prefix3':sum(int(r['raw_common_prefix'])>=3 and int(r['residual_common_prefix'])>=1 for r in out),'interpretation':'Transferred label prefixes carry most formal similarity in comparable visual-unit pairs; residual families do not yield a reusable content key.','claim_ceiling':'Register/content layer decomposition only; no residual meaning, object, word, morpheme, sound, language, plaintext, or translation.','f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{PAIRS.name:sha(PAIRS),MANIFEST.name:sha(MANIFEST)},'outputs':{},'documents':{},'implementation':{}}
 for n in ('gdt234_residual_homolog_pairs.tsv','gdt234_residual_summary.tsv','gdt234_special_pairs.tsv'):result['outputs'][n]=sha(ROOT/n)
 for n in ('GDT234_LABEL_RESIDUAL_HOMOLOG_TEST_METHOD.md','GDT234_LABEL_RESIDUAL_HOMOLOG_TEST_REPORT.md'):
  if (ROOT/n).exists():result['documents'][n]=sha(ROOT/n)
 result['implementation'][Path(__file__).name]=sha(Path(__file__));result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ROOT/'gdt234_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'changed':result['changed_summary'],'nonempty':result['nonempty_summary']},sort_keys=True))
if __name__=='__main__':main()
