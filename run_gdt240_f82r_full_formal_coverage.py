#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
CONS=R/'gdt002_grammar_consensus_projection.tsv';FLD=R/'gdt239_f82r_field_dossier.tsv';LAB=R/'gdt239_f82r_label_dossier.tsv'
OUTS=['gdt240_f82r_complete_locus_inventory.tsv','gdt240_f82r_coverage_summary.tsv']
DOCS=['GDT240_F82R_FULL_FORMAL_COVERAGE_METHOD.md','GDT240_F82R_FULL_FORMAL_COVERAGE_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def only(path):
 out=[]
 with path.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t')
   if a[pi]!='f82r':continue
   out.append(dict(zip(h,a)))
 return out
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 c=only(CONS);fields=only(FLD);labels=only(LAB);by=defaultdict(list)
 for x in c:by[x['locus']].append(x)
 fb=Counter(x['locus'] for x in fields); lb={x['locus']:x for x in labels};rows=[]
 for loc,rr in sorted(by.items(),key=lambda z:int(z[0].split('.')[1])):
  r=rr[0];groups=[x for x in rr if x['consensus_group_id']];families='|'.join(x['family_surface'] for x in groups)
  rows.append({'page':'f82r','locus':loc,'kind':r['kind'],'grammar_scope':r['grammar_scope'],'code':r['code'],'coverage_state':r['coverage_state'],'consensus_group_count':len(groups),'family_expression':families or 'UNRESOLVED','first_family':groups[0]['family_surface'] if groups else 'UNRESOLVED','last_family':groups[-1]['family_surface'] if groups else 'UNRESOLVED','line_left_boundary':groups[0]['left_boundary_profile'] if groups else 'UNRESOLVED','line_right_boundary':groups[-1]['right_boundary_profile'] if groups else 'UNRESOLVED','gdt229_field_count':fb[loc],'gdt229_semantic_scaffold_coverage':int(fb[loc]>0),'gdt239_label_dossier_coverage':int(loc in lb),'label_prefix':lb[loc]['gdt233_strict_prefix'] if loc in lb else 'NOT_LABEL_OR_UNJOINED','label_residual':lb[loc]['gdt233_strict_residual'] if loc in lb else 'NOT_LABEL_OR_UNJOINED','semantic_value':'UNASSIGNED'})
 write(OUTS[0],rows)
 summary=[]
 for kind in ('ALL','P','L'):
  z=rows if kind=='ALL' else [x for x in rows if x['kind']==kind];cc=Counter(x['coverage_state'] for x in z)
  summary.append({'scope':kind,'loci':len(z),'strict_exact_family':cc['STRICT_EXACT_FAMILY'],'exact_family_with_alternative':cc['EXACT_FAMILY_WITH_ALTERNATIVE'],'no_exact_family_consensus':cc['NO_EXACT_FAMILY_CONSENSUS'],'gdt229_scaffold_covered_loci':sum(x['gdt229_semantic_scaffold_coverage'] for x in z),'gdt239_label_covered_loci':sum(x['gdt239_label_dossier_coverage'] for x in z)})
 write(OUTS[1],summary)
 result={'experiment':'GDT240_F82R_FULL_FORMAL_COVERAGE','status':'F82R_FULL_FORMAL_CENSUS_BUILT_SEMANTIC_SCAFFOLD_REMAINS_25_PERCENT','loci':45,'prose_loci':32,'label_loci':13,'coverage_states':dict(Counter(x['coverage_state'] for x in rows)),'prose_coverage_states':dict(Counter(x['coverage_state'] for x in rows if x['kind']=='P')),'label_coverage_states':dict(Counter(x['coverage_state'] for x in rows if x['kind']=='L')),'semantic_scaffold_prose_loci':sum(x['gdt229_semantic_scaffold_coverage'] for x in rows if x['kind']=='P'),'semantic_scaffold_fraction':sum(x['gdt229_semantic_scaffold_coverage'] for x in rows if x['kind']=='P')/32,
 'interpretation':'Every f82r locus now has an explicit formal coverage state; source-native family consensus is available for 21 of 32 prose loci, while the translation-shaped GDT229 scaffold remains limited to eight.',
 'claim_ceiling':'Full locus/formal coverage accounting only; no missing family imputation, preferred reading, semantic role, word, language, plaintext, or translation.',
 'f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (CONS,FLD,LAB)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt240_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'coverage':result['coverage_states'],'semantic_scaffold':result['semantic_scaffold_prose_loci']},sort_keys=True))
if __name__=='__main__':main()
