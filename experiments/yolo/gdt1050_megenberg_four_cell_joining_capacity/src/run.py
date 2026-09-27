#!/usr/bin/env python3
"""A fixed necessary-capacity census. No semantic value is inferred."""
from pathlib import Path
import argparse,collections,csv,datetime,hashlib,itertools,json,re
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(name,obj): (ART/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def signature(seq):
 ids={};return tuple(ids.setdefault(x,len(ids)) for x in seq)
def checked_inputs():
 lock=load(EXP/'src/PREREG_LOCK.json')
 for path,h in lock['files'].items():assert sha(ROOT/path)==h,path
 return load(EXP/'src/SPEC.json')
def make_schemas(spec):
 bank=load(ROOT/spec['bank']);assert len(bank)==22
 clauses=spec['clauses'];schemas=[]
 for order in itertools.permutations(['P','ARG1','ARG2']):
  for placement in ['before_clause','after_clause']:
   pattern=[];roles=[]
   for ci,c in enumerate(clauses):
    vals={'P':'P','ARG1':'AB'[c['arg1']],'ARG2':'AB'[c['arg2']]}
    cr=[{'clause':ci,'slot':s,'argument':c['arg1'] if s=='ARG1' else c['arg2'] if s=='ARG2' else None,'reported_J':not c['negative']} for s in order]
    pp=[vals[s] for s in order]
    if c['negative']:
     neg={'clause':ci,'slot':'N','argument':None,'reported_J':False}
     if placement=='before_clause':pp=['N']+pp;cr=[neg]+cr
     else:pp=pp+['N'];cr=cr+[neg]
    pattern+=pp;roles+=cr
   schemas.append({'id':f'A{len(schemas)+1:03d}','family':'ATOMIC14','pattern':pattern,'variables':['P','N','A','B'],'roles':roles,'slot_order':list(order),'negative_placement':placement,'semantic_mapping':'P=J, N=negative, A/B=anonymous kinds; actual names and complemented polarity unresolved'})
 for bi,(x,y) in enumerate(bank):
  for a_suffix in ['r','l']:
   for alignment in ['preserve_suffix','reverse_suffix']:
    suffix={'A':a_suffix,'B':'l' if a_suffix=='r' else 'r'}
    ys={k:(v if alignment=='preserve_suffix' else 'l' if v=='r' else 'r') for k,v in suffix.items()}
    forms={'X_A':x+suffix['A'],'X_B':x+suffix['B'],'Y_A':y+ys['A'],'Y_B':y+ys['B']}
    assert len(set(forms.values()))==4
    for placement in ['before_clause','after_clause']:
     pattern=[];roles=[]
     for ci,c in enumerate(clauses):
      pp=[forms['X_'+'AB'[c['arg1']]],forms['Y_'+'AB'[c['arg2']]]]
      cr=[{'clause':ci,'slot':'X_ARG1','argument':c['arg1'],'reported_J':not c['negative']},{'clause':ci,'slot':'Y_ARG2','argument':c['arg2'],'reported_J':not c['negative']}]
      if c['negative']:
       neg={'clause':ci,'slot':'N','argument':None,'reported_J':False}
       if placement=='before_clause':pp=['N']+pp;cr=[neg]+cr
       else:pp+=['N'];cr+=[neg]
      pattern+=pp;roles+=cr
     schemas.append({'id':f'R{sum(s["family"]=="ROLE10" for s in schemas)+1:03d}','family':'ROLE10','pattern':pattern,'variables':['N'],'forms':forms,'ordered_stems':[x,y],'bank_index':bi,'first_role_A_suffix':a_suffix,'cross_role_alignment':alignment,'negative_placement':placement,'roles':roles,'semantic_mapping':'X_a=J(a,-), Y_b=b; cross-role identity and one curried predicate are hypotheses'})
 assert len(schemas)==188
 classes={};skeletons={}
 for s in schemas:
  key=(s['family'],signature(s['pattern']) if s['family']=='ATOMIC14' else tuple(s['pattern']))
  s['equivalence_class']=classes.setdefault(key,f'E{len(classes)+1:03d}')
  s['anonymous_equality_skeleton']=list(signature(s['pattern']))
  skeletons.setdefault(s['family'],set()).add(signature(s['pattern']))
 return schemas,{'literal_equivalence_classes':len(classes),'anonymous_skeleton_counts':{k:len(v) for k,v in skeletons.items()},'raw_branches':{'ATOMIC14':12,'ROLE10':176}}
def match(words,s):
 if len(words)!=len(s['pattern']):return None
 vset=set(s['variables']);mapping={};fixed={t for t in s['pattern'] if t not in vset}
 for token,w in zip(s['pattern'],words):
  if token in vset:
   if token in mapping:
    if mapping[token]!=w:return None
   elif w in fixed or w in mapping.values():return None
   else:mapping[token]=w
  elif token!=w:return None
 return mapping
def eligibility(gs):
 raw=all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs);seams=True
 for a,b in zip(gs,gs[1:]):
  if a['locus']==b['locus']:
   okay=b['source_group_index']==a['source_group_index']+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
  else:okay=a['source_group_index']==a['source_group_count'] and b['source_group_index']==1 and int(b['locus'].rsplit('.',1)[1])==int(a['locus'].rsplit('.',1)[1])+1
  seams=seams and okay
 return bool(raw),bool(seams)
def panels(spec):
 allowed=set(load(ROOT/spec['allowed_selectors_spec'])['allowed_selectors']);assert len(allowed)==179
 groups={};metadata={}
 for path in spec['raw_caches']:
  d=load(ROOT/path)
  for line in d['lines']:
   m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
   gs=[dict(zip(d['group_columns'],row)) for row in line['groups']]
   assert len(gs)==int(m['source_group_count'])
   for g in gs:
    g.update({k:m[k] for k in ['page','locus','edition','paragraph_start','paragraph_end','kind']});g['source_group_index']=int(g['source_group_index']);g['source_group_count']=int(m['source_group_count']);assert g['source_group_id'] not in groups;groups[g['source_group_id']]=g
   metadata[(m['edition'],m['locus'])]=m
 data=load(ROOT/spec['paragraphs']);out={}
 for ed,ps in data.items():
  out[ed]=[]
  for p in ps:
   assert p['page'] in allowed and not p['page'].startswith('f84');flat=[]
   for li,line in enumerate(p['lines']):
    m=metadata[(ed,line['locus'])];assert m['kind']=='P' and m['page']==p['page'];assert (m['paragraph_start']=='1')==(li==0);assert (m['paragraph_end']=='1')==(li==len(p['lines'])-1)
    for word,sid in zip(line['words'],line['source_ids']):
     g=groups[sid];assert g['ivtff_group_raw']==word and g['edition']==ed and g['locus']==line['locus'];flat.append(g)
    assert len(line['words'])==len(line['source_ids'])==int(m['source_group_count'])
   assert len(flat)==p['groups'];out[ed].append((p,flat))
 assert {ed:len(ps) for ed,ps in out.items()}=={'ZL3b':659,'IT2a':690,'RF1b':0}
 return out

def census(data,schemas):
 counts={};matches=[];hosts={}
 for ed,ps in data.items():
  cc={'complete_paragraphs':len(ps),'total_groups':sum(len(gs) for p,gs in ps),'windows':{},'branch_counts':{s['id']:0 for s in schemas}}
  for length in [10,14]:cc['windows'][str(length)]={'total':0,'eligible':0,'invalid_raw':0,'invalid_seam':0,'both_invalid':0}
  for p,flat in ps:
   for length in [10,14]:
    ss=[s for s in schemas if len(s['pattern'])==length];c=cc['windows'][str(length)]
    for offset in range(max(0,len(flat)-length+1)):
     gs=flat[offset:offset+length];raw,seams=eligibility(gs);c['total']+=1;c['invalid_raw']+=not raw;c['invalid_seam']+=not seams;c['both_invalid']+=not raw and not seams
     if not(raw and seams):continue
     c['eligible']+=1;words=[g['ivtff_group_raw'] for g in gs]
     for s in ss:
      mapping=match(words,s)
      if mapping is None:continue
      cc['branch_counts'][s['id']]+=1
      row={'reader':ed,'branch_id':s['id'],'family':s['family'],'equivalence_class':s['equivalence_class'],'paragraph_id':p['id'],'page':p['page'],'leaf':p['leaf'],'offset':offset,'length':length,'mapping':mapping,'role_forms':s.get('forms',{}),'words':words,'positions':[{'paragraph_offset':offset+i,'source_group_id':g['source_group_id'],'locus':g['locus'],'source_group_index':g['source_group_index'],'observed':g['ivtff_group_raw'],'predicted_pattern_token':s['pattern'][i],**s['roles'][i]} for i,g in enumerate(gs)],'outside_groups':len(flat)-length,'whole_paragraph_interpreted':False}
      matches.append(row);hosts[(ed,p['id'])]={'reader':ed,'paragraph':p}
  counts[ed]=cc
 return counts,matches,[hosts[k] for k in sorted(hosts)]
def fixtures(schemas):
 positive=[]
 for s in schemas:
  vv={'A':'entitya','B':'entityb','P':'predicate','N':'negative'};words=[vv[t] if t in s['variables'] else t for t in s['pattern']];assert match(words,s) is not None
  positive.append({'branch_id':s['id'],'words':words,'recognized':True})
 s=schemas[0];base=positive[0]['words'];cases=[]
 for name,index,new in [('wrong_self_cell',3,'entityb'),('wrong_cross_cell',10,'entityb'),('different_negator',4,'anothernegative')]:
  w=base.copy();w[index]=new;assert match(w,s) is None,(name,w);cases.append({'case':name,'rejected':True})
 assert match(base[1:],s) is None;cases.append({'case':'dropped_negator','rejected':True})
 return {'positive_branches':positive,'negative_cases':cases,'semantic_limit':'Synthetic literal recognition only; not meaning or source truth.'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--schemas-only',action='store_true');args=ap.parse_args();spec=checked_inputs();schemas,eq=make_schemas(spec)
 if args.schemas_only:
  write('SCHEMAS.json',schemas);write('EQUIVALENCE.json',eq);write('SCHEMA_FREEZE.json',{'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_target_census':True,'sha256':sha(ART/'SCHEMAS.json'),'equivalence_sha256':sha(ART/'EQUIVALENCE.json')});print(json.dumps(eq));return
 freeze=load(ART/'SCHEMA_FREEZE.json');assert sha(ART/'SCHEMAS.json')==freeze['sha256'];assert load(ART/'SCHEMAS.json')==schemas
 source=load(EXP/'src/SOURCE.json');raw=(ROOT/source['whole_cache_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['whole_cache_sha256'];a,z=source['corrected_argument_byte_range'];assert hashlib.sha256(raw[a:z]).hexdigest()==source['corrected_argument_sha256']
 fix=fixtures(schemas);data=panels(spec);counts,matches,hosts=census(data,schemas)
 write('FIXTURES.json',fix);write('CENSUS.json',counts);write('MATCHES.json',matches);write('CANDIDATE_PARAGRAPHS.json',hosts)
 decisions={}
 for ed in ['ZL3b','IT2a','RF1b']:
  decisions[ed]={}
  for family,length in [('ATOMIC14',14),('ROLE10',10)]:
   n=sum(m['reader']==ed and m['family']==family for m in matches);eligible=counts[ed]['windows'][str(length)]['eligible']
   decisions[ed][family]={'matches':n,'unique_host_paragraphs':len({m['paragraph_id'] for m in matches if m['reader']==ed and m['family']==family}),'eligible_windows':eligible,'decision':'NO_NATIVE_PARAGRAPH_CAPACITY' if ed=='RF1b' else 'NO_ELIGIBLE_WINDOWS' if not eligible else 'CANDIDATE_CAPACITY_ONLY' if n else 'NO_REALIZATION_IN_FIXED_COMPLETE_PARAGRAPHS'}
 result={'status':'COMPLETE_FIXED_FOUR_CELL_CAPACITY_CENSUS','primary':'ZL3b','decisions':decisions,'all_raw_branches':len(schemas),'equivalence':eq,'reported_source_table':[[False,True],[True,False]],'semantic_symmetries':['A/B metal names may swap','predicate complement with marked polarity reversed','many other symmetric irreflexive relations','WITH material role not fixed by table'],'independent_confirmation_capacity':0,'source_copy_identified':False,'significance_claim':False,'confirmed_translated_words':0,'whole_source_duties_expressed':0}
 write('RESULT.json',result)
 with (ART/'CANDIDATE_PREDICTION_TABLE.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['branch_id','family','equivalence_class','complete_prediction','ZL3b_matches','IT2a_matches','RF1b_status'])
  for s in schemas:w.writerow([s['id'],s['family'],s['equivalence_class'],' '.join(s['pattern']),counts['ZL3b']['branch_counts'][s['id']],counts['IT2a']['branch_counts'][s['id']],'NO_NATIVE_PARAGRAPH_CAPACITY'])
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
