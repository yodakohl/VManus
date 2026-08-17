#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SRC=R/'gdt016_group_state_inventory.tsv';OLD=R/'gdt239_f82r_field_dossier.tsv';COV=R/'gdt240_f82r_complete_locus_inventory.tsv'
OUTS=['gdt241_f82r_hpr2_fields.tsv','gdt241_f82r_line_coverage.tsv']
DOCS=['GDT241_F82R_HPR2_FIELD_EXPANSION_METHOD.md','GDT241_F82R_HPR2_FIELD_EXPANSION_REPORT.md']
RIGHT=('aiin','air','ain','ar','al')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def pre(x):
 h=x['residual_host'];b3=int(h.endswith('m') and len(h)>1);h=h[:-1] if b3 else h;right='NONE'
 for s in RIGHT:
  if h.endswith(s) and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(x['stripped_prefix'] in {'ch','che','sh'} and h.startswith('d') and len(h)>1);h=h[1:] if inner else h
 return h,b3,right,inner
def main():
 prose=[]
 with COV.open(encoding='utf-8') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   if x['page']=='f82r' and x['kind']=='P':prose.append(x['locus'])
 allrows=[];target=[]
 with SRC.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t');p=a[pi]
   if p.startswith('f84'):continue
   x=dict(zip(h,a));allrows.append(x)
   if p=='f82r' and x['locus'] in prose:target.append(x)
 counts=Counter(pre(x)[0] for x in allrows);licensed={h for h in counts if counts[h] and counts['o'+h] and counts['ot'+h]}|{'ar','al','ol'}
 def parse(x):
  h,b3,right,inner=pre(x);frame='NONE'
  if h.startswith('ot') and h[2:] in licensed:h=h[2:];frame='OT'
  elif h.startswith('o') and h[1:] in licensed:h=h[1:];frame='O'
  return h or 'EMPTY',b3,right,inner,frame
 by=defaultdict(list)
 for x in target:by[x['locus']].append(x)
 old=defaultdict(list)
 with OLD.open(encoding='utf-8') as f:
  for x in csv.DictReader(f,delimiter='\t'):old[x['locus']].append(x)
 fields=[];lines=[];overlap_ok=0
 for locus in sorted(by,key=lambda x:int(x.split('.')[1])):
  gg=sorted(by[locus],key=lambda x:int(x['group_index']));fs=[];cur=[]
  for g in gg:
   cur.append(g)
   if g['dy_closure']=='1':fs.append(cur);cur=[]
  if cur:fs.append(cur)
  built=[]
  for i,z in enumerate(fs,1):
   pp=[parse(g) for g in z];row={'page':'f82r','locus':locus,'line_field_ordinal':i,'line_field_count':len(fs),'field_group_count':len(z),'source_tokens':'|'.join(g['token'] for g in z),'page_hosts':'|'.join(p[0] for p in pp),'compiler_cells':'|'.join(f"{g['stripped_prefix']}:{p[4]}:{p[3]}:{p[2]}:{g['dy_closure']}:{p[1]}" for p,g in zip(pp,z)),'line_field_end':'DY' if z[-1]['dy_closure']=='1' else 'LINE_END','gdt229_role_available':int(locus in old),'semantic_role':'UNASSIGNED'};fields.append(row);built.append(row)
  exact=0
  if locus in old:
   oo=old[locus];exact=int(len(oo)==len(built) and all((a['source_tokens'],a['page_hosts'],a['compiler_cells'],a['line_field_end'])==(b['source_tokens'],b['page_hosts'],b['compiler_cells'],b['line_field_end']) for a,b in zip(oo,built)));overlap_ok+=exact
  lines.append({'page':'f82r','locus':locus,'source_group_count':len(gg),'hpr2_field_count':len(fs),'gdt229_role_available':int(locus in old),'overlap_exact_match':exact if locus in old else 'NOT_APPLICABLE','coverage_state':'HPR2_FORMAL_FIELD_SEGMENTED_NO_SEMANTIC_ROLE'})
 write(OUTS[0],fields);write(OUTS[1],lines)
 result={'experiment':'GDT241_F82R_HPR2_FIELD_EXPANSION','status':'F82R_HPR2_FORMAL_COVERAGE_EXPANDED_8_TO_17_LINES_SEMANTIC_ROLES_UNCHANGED','human_prose_loci':32,'hpr2_covered_loci':len(lines),'prior_role_scaffold_loci':len(old),'new_formal_only_loci':len(lines)-len(old),'hpr2_fields':len(fields),'prior_fields':sum(len(v) for v in old.values()),'overlap_exact_loci':overlap_ok,'licensed_o_ot_hosts':len(licensed),
 'interpretation':'Formal HPR2 field segmentation now covers 17 f82r prose loci, while abstract/semantic role coverage remains frozen at eight complete-line loci.',
 'claim_ceiling':'Formal field/compiler expansion only; no new role, field ownership, word, language, plaintext, or translation.',
 'f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (SRC,OLD,COV)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt241_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'lines':len(lines),'fields':len(fields),'new_lines':result['new_formal_only_loci'],'overlap_exact':overlap_ok},sort_keys=True))
if __name__=='__main__':main()
