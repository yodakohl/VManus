#!/usr/bin/env python3
"""AW exploratory preservation/coverage and conditional binding diagnostic, not semantics."""
import csv,hashlib,io,json,subprocess
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[3]
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def table(rs,cols):
 f=io.StringIO();w=csv.DictWriter(f,cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs);return f.getvalue()
def build():
 receipt=json.loads((B/'AW_PUBLIC_PROJECTION.json').read_text())
 for n,h in receipt['public_sha256'].items():assert hashlib.sha256((B/n).read_bytes()).hexdigest()==h,n
 scope=json.loads((B/'AW_SCOPE.json').read_text())
 for p,h in scope['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 author=json.loads((B/'AW_AUTHOR_PUBLIC.json').read_text());values={x['form']:x['value'] for x in author['new_values']}
 assert len(values)==len(author['new_values'])==40 and author['rule_count']==len(author['new_composition_rules'])==4 and len(author['alias_bridges'])==8
 cols=['source_group_id','edition','page','locus','kind','source_group_index','ivtff_group_raw','left_separator','right_separator','paragraph_start','paragraph_end']
 cmd=[str(R/'vmanus-exp'),'query-tsv',str(B/'F_TARGET_RAW.tsv'),'--selector','page','--allow','f22r','--allow','f32r','--allow','f42v','--columns',','.join(cols)]
 p=subprocess.run(cmd,cwd=R,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 rs=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'));assert len(rs)==891 and {r['page'] for r in rs}=={'f22r','f32r','f42v'}
 ls=defaultdict(list)
 for r in rs:ls[r['edition'],r['locus']].append(r)
 occ=[];perreader=defaultdict(Counter)
 for r in rs:
  ed=r['edition'];raw=r['ivtff_group_raw'];target=r['page']=='f32r' and 6<=int(r['locus'].split('.')[-1])<=19
  perreader[ed]['total_owned_groups']+=1
  if target:perreader[ed]['target_groups']+=1
  if raw not in values:continue
  perreader[ed]['target_assigned' if target else 'outside_assigned']+=1
  occ.append({k:r[k] for k in cols}|{'C0_guess':values[raw],'scope':'TARGET_SECOND_F32R' if target else 'OTHER_EXPOSED_OWNED_CONTEXT','whole_line':' '.join(x['ivtff_group_raw'] for x in ls[ed,r['locus']])})
 z=[r for r in rs if r['edition']=='ZL3b' and r['page']=='f32r' and 6<=int(r['locus'].split('.')[-1])<=19]
 assert len(z)==45 and {r['ivtff_group_raw'] for r in z}==set(values) and perreader['ZL3b']['target_assigned']==45
 alltarget=[r for r in rs if r['page']=='f32r' and 6<=int(r['locus'].split('.')[-1])<=19]
 unknown=[r for r in alltarget if r['ivtff_group_raw'] not in values]
 diagnostic=[]
 for ed in ['ZL3b','IT2a']:
  for x in ls[ed,'f32r.14']:
   if x['ivtff_group_raw']!='daiin':continue
   row=ls[ed,'f32r.14'];i=row.index(x);left=row[i-1]['ivtff_group_raw'];right=row[i+1]['ivtff_group_raw']
   assert left=='shey' and right=='cths'
   diagnostic.append({'edition':ed,'locus':'f32r.14','left_raw':left,'left_C0_value':values[left],'operator_raw':'daiin','right_raw':right,'right_C0_value':values[right],'strict_left_adjacent_argument':'H','author_intended_absent_argument':'D','conditional_outcome':'ARGUMENT_MISMATCH_IF_STRICT_LEFT_ADJACENT_BINDING','whole_package_outcome':'UNRESOLVED_OPERATOR_SCOPE_NOT_UNCONDITIONAL_REFUTATION'})
 counts={ed:dict(c) for ed,c in perreader.items()}
 v={'status':'PASS_SOURCE_IDENTITY_AND_EXACT_COVERAGE_NOT_MEANING','scope':'Three exposed owned folios; no full-corpus semantic test','by_reader':counts,'assigned_rows':len(occ),'unknown_alternate_target_rows':len(unknown),'conditional_diagnostic':diagnostic,'whole_ZL_lexical_assignment':True,'uniform_executable_operator_or_parser':False,'IT_RF_complete_graphs':False,'confirmed_words':0,'independent_confirmation':0,'strict_refutation_of_unspecified_whole_package':False,'significance_claim':False}
 return {'AW_ASSIGNED_OCCURRENCES.tsv':table(occ,list(occ[0])),'AW_TARGET_UNKNOWN_VARIANTS.tsv':table(unknown,cols),'AW_VALIDATION.json':dump(v)}
if __name__=='__main__':
 for n,t in build().items():(B/n).write_text(t)
 print((B/'AW_VALIDATION.json').read_text())
