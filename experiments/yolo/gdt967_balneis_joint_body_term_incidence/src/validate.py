#!/usr/bin/env python3
"""Independent GDT967 source/data/search audit; --self-test opens no targets.

The primary is imported only for synthetic oracle comparisons. Actual source,
target vectors and enumeration are reconstructed independently. Tuple signatures
deliberately avoid the primary's mixed-radix representation.
"""
import argparse, collections as C, csv, hashlib, importlib.util
import itertools as I, json, math, random, re, time
from pathlib import Path

E=Path(__file__).resolve().parents[1]; R=E.parents[2]; A=E/'artifacts'
OLD=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
EDS=('ZL3b','IT2a','RF1b'); MODELS=('WHOLE_GROUP','WITHIN_GROUP_PIECE')
ALLOW={f'f{n}{s}' for n in range(75,84) for s in 'rv'}
RULES={
 'AQUA':'aqua aque aquam aquas aquis unda undam undis limpha',
 'HEAD':'caput capitis capitus capiti',
 'STOMACH':'stomachi stomachique stomacho stomachum stomacus',
 'OCULUS':'oculis oculorum oculos','LIVER':'epar iecoris iecur jecur',
 'SPLEEN':'splem splene splenis splenisque','SKIN':'cute cutim cutis',
 'LUNG':'pulmonem pulmoni pulmonis','KIDNEY':'renes renibus',
 'BLADDER':'vesicam vesicas vesice','WOMB':'matrice matricem matrices matrix',
 'NERVOUS_TISSUE':'neruis neruos','HYDROPS':'ydropicis ydropicos ydropisis'}
CHECKS=[]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def eq(a,b,label):
 assert a==b,label
def passed(label,**details): CHECKS.append(dict(check=label,status='PASS',**details))

def hashes():
 lock=read(E/'PREREG_LOCK.json')['files']
 parent=read(R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/PREREG_LOCK.json')['files']
 for scope in (lock,parent):
  for path,digest in scope.items(): eq(sha(R/path),digest,'unchanged binding: '+path)
 passed('current_and_parent_freezes',current=len(lock),parent=len(parent))
 return lock

def source_check(lock):
 s=read(E/'src/SOURCE.json'); matrix=read(E/'src/SOURCE_MATRIX.json')
 primary=[R/p for p,h in lock.items() if h==s['source']['sha256']]
 assert primary,'primary source text must be registered'
 text=primary[0].read_text(); lines=text.splitlines(keepends=True); offsets=[]; cursor=0
 for line in lines: offsets.append(cursor); cursor+=len(line)
 heads=[]; rv={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
 for n,line in enumerate(lines,1):
  m=re.match(r'^([IVXLCDM]+)\. \[([^]]+)\]',line)
  if m:
   vals=[rv[c] for c in m[1]]; num=sum(-v if i+1<len(vals) and vals[i+1]>v else v for i,v in enumerate(vals))
   eq(num,len(heads)+1,'Roman source sequence')
   heads.append(dict(record_id=num,roman=m[1],name=m[2],start_line=n,header_exact=line.rstrip('\r\n'),complete_numbered_entry=True))
 eq(len(heads),33,'all33 heads before exclusion')
 for i,h in enumerate(heads): h['end_line']=heads[i+1]['start_line']-1 if i+1<len(heads) else len(lines)
 eq(heads,s['all_header_boundaries'],'complete source bounds')
 baths=[h for h in heads if h['record_id']!=31]; eq(baths,s['records'],'all32 baths')
 lookup={w:f for f,words in RULES.items() for w in words.split()}; found={f:[] for f in RULES}; excluded=[]
 for h in baths:
  for ln in range(h['start_line'],h['end_line']+1):
   for ti,m in enumerate(re.finditer(r'\S+',lines[ln-1])):
    token=m[0]; norm=re.sub('[^a-z]','',token.lower()); f=lookup.get(norm)
    o=dict(record_id=h['record_id'],source_line=ln,char_offset=offsets[ln-1]+m.start(),line_column=m.start(),source_token_index=ti,sourceword_exact=token,source_line_exact=lines[ln-1].rstrip('\r\n'))
    reject=(ln==23 and norm in ('capue','caput')) or norm in ('aquosas','lymphato','lumine','luminis','lumina','luminibus','lumen')
    if reject: excluded.append(o)
    elif f: found[f].append(o)
 eq(set(s['families']),set(RULES),'operative namespaces')
 for f,os in found.items():
  p=s['families'][f]; eq(set(s['family_form_tables'][f]['dictionary_keys']),set(RULES[f].split()),f+' aliases')
  eq(p['count_total'],len(os),f+' total'); eq(p['count_by_record'],dict(C.Counter(str(o['record_id']) for o in os)),f+' per-record counts')
  eq(len(p['occurrences']),len(os),f+' occurrence count')
  for want,got in zip(os,p['occurrences']):
   eq({k:got[k] for k in want},want,f+' exact source witness')
   eq(text[got['char_offset']:got['char_offset']+len(got['sourceword_exact'])],got['sourceword_exact'],'source substring')
   eq(got['polarity'],'unreviewed','nonoperative polarity')
 em={o['char_offset']:o for o in s['excluded_witnesses']}; eq(set(em),{o['char_offset'] for o in excluded},'exclusion coverage')
 for o in excluded: eq({k:em[o['char_offset']][k] for k in o},o,'exact excluded witness')
 eq(matrix['source_sha256'],sha(E/'src/SOURCE.json'),'matrix source binding'); eq(matrix['columns'],list(RULES),'column order')
 expected_rows=[dict(id=h['record_id'],name=h['name'],counts=[sum(o['record_id']==h['record_id'] for o in found[f]) for f in RULES]) for h in baths]
 eq(matrix['rows'],expected_rows,'all416 source matrix cells')
 eq(sum(map(len,found.values())),166,'source occurrence total')
 eq(len({tuple(r['counts']) for r in expected_rows}),31,'31 source signatures')
 passed('independent_complete_source',headers=33,records=32,cells=416,occurrences=166,exclusions=len(excluded))
 return matrix

def targets_check():
 admitted=set(read(OLD/'src/SPEC.json')['allowed_selectors']); assert ALLOW<=admitted
 targets={}; scopes={}
 for ed in EDS:
  pages=C.defaultdict(list)
  for phase in ('DISCOVERY','EVALUATION'):
   data=read(OLD/'artifacts'/f'SOURCE_{phase}_{ed}.json'); ix={c:i for i,c in enumerate(data['group_columns'])}
   for raw in data['lines']:
    m=raw['metadata']; assert m['page'] in admitted and not m['page'].startswith('f84')
    if m['page'] not in ALLOW or m['kind']!='P': continue
    gs=raw['groups']; ws=[g[ix['ivtff_group_raw']] for g in gs]
    good=len(gs)>=2 and all(re.fullmatch('[a-z]+',w) is not None for w in ws)
    for left,right in zip(gs,gs[1:]):
     good &= int(right[ix['source_group_index']])-int(left[ix['source_group_index']])==1
     good &= left[ix['right_separator']]=='DEFINITE_SPACE' and right[ix['left_separator']]=='DEFINITE_SPACE'
    pages[m['page']].append(dict(row=int(m['source_row_index']),locus=m['locus'],start=m['paragraph_start']=='1',end=m['paragraph_end']=='1',good=bool(good),words=ws,ids=[g[ix['source_group_id']] for g in gs]))
  whole=[]; usable=[]
  for page,ls in sorted(pages.items()):
   ls.sort(key=lambda l:l['row']); starts=[i for i,l in enumerate(ls) if l['start']]
   for k,first in enumerate(starts):
    boundary=starts[k+1] if k+1<len(starts) else len(ls)
    ends=[i for i in range(first,boundary) if ls[i]['end']]
    if not ends: continue
    block=ls[first:ends[0]+1]; numbers=[int(l['locus'].rsplit('.',1)[1]) for l in block]
    if numbers!=list(range(numbers[0],numbers[0]+len(numbers))): continue
    pid=page+'|'+block[0]['locus']+'-'+block[-1]['locus']; leaf=int(page[1:-1]); bad=[l['locus'] for l in block if not l['good']]
    whole.append(dict(id=pid,page=page,leaf=leaf,groups=sum(len(l['words']) for l in block),literal=not bad,ineligible_lines=bad))
    if not bad: usable.append(dict(id=pid,page=page,leaf=leaf,words=[w for l in block for w in l['words']],loci=[l['locus'] for l in block],source_ids=[sid for l in block for sid in l['ids']]))
  assert len({r['id'] for r in whole})==len(whole)
  targets[ed]=sorted(usable,key=lambda r:r['id'])
  scopes[ed]=dict(complete=len(whole),literal=len(usable),nonliteral=len(whole)-len(usable),rows=whole,independent_confirmation_capacity=0)
 eq([(scopes[e]['complete'],scopes[e]['literal']) for e in EDS],[(78,3),(79,71),(0,0)],'fixed capacity')
 eq(targets,read(A/'TARGET.json'),'six-cache independent paragraph reconstruction')
 eq(scopes,read(A/'SCOPE.json'),'every whole frame and unknown')
 passed('independent_six_cache_intake',complete=157,literal=74,nonliteral=83,editions=3)
 return targets,scopes

def profiles_for(rows,model):
 counts=[]
 for row in rows:
  c=C.Counter()
  for word in row['words']:
   if model=='WHOLE_GROUP': c[word]+=1
   else:
    seen=set()
    for length in range(1,len(word)+1):
     for start in range(len(word)-length+1): seen.add(word[start:start+length])
    c.update(seen)
  counts.append(c)
 strings=sorted(set().union(*(set(c) for c in counts))); groups=C.defaultdict(list)
 for s in strings: groups[tuple(c[s] for c in counts)].append(s)
 ordered=sorted(groups.items(),key=lambda item:item[1][0])
 return [dict(id=i,members=members,counts=list(vector)) for i,(vector,members) in enumerate(ordered)]

def domains_for(source,profiles):
 wanted=[C.Counter(r['counts'][j] for r in source['rows']) for j in range(len(source['columns']))]
 domains=[[] for _ in wanted]; table=[]
 for p in profiles:
  available=C.Counter(p['counts']); deficits={}; good=[]
  for j,column in enumerate(source['columns']):
   missing=[dict(count=k,required=n,observed=available[k]) for k,n in sorted(wanted[j].items()) if available[k]<n]
   if missing: deficits[column]=missing
   else: domains[j].append(p['id']); good.append(column)
  table.append(dict(profile=p['id'],eligible_families=good,deficits=deficits))
 return domains,table

def order_for(source):
 return sorted(range(len(source['columns'])),key=lambda j:(-sum(r['counts'][j]>0 for r in source['rows']),-max(r['counts'][j] for r in source['rows']),source['columns'][j]))

def perm(n,k):
 assert n>=k
 return math.factorial(n)//math.factorial(n-k)

def family_value(source,profiles,assignment):
 need=C.Counter(tuple(r['counts']) for r in source['rows'])
 have=C.Counter(zip(*(profiles[p]['counts'] for p in assignment)))
 assert all(have[s]>=n for s,n in need.items()),'full signature packing'
 uses=C.Counter(assignment); assert all(len(profiles[p]['members'])>=n for p,n in uses.items()),'dictionary injectivity'
 return dict(profiles=list(assignment),dictionary_count=str(math.prod(perm(len(profiles[p]['members']),n) for p,n in uses.items())),record_assignment_count=str(math.prod(perm(have[s],n) for s,n in need.items())))

def independent_enumeration(source,profiles,domains,first=None,deadline=None,stats=None):
 order=order_for(source); needed=[C.Counter(tuple(r['counts'][j] for j in order[:depth]) for r in source['rows']) for depth in range(1,len(order)+1)]
 assignment=[None]*len(order); uses=C.Counter(); nt=len(profiles[0]['counts']) if profiles else 0
 def dfs(depth,signatures):
  if deadline is not None and time.monotonic()>deadline: raise TimeoutError('Independent validation timeout; no PASS')
  candidates=[first] if depth==0 and first is not None else domains[order[depth]]
  for pid in candidates:
   st=stats[depth] if stats is not None else None
   if st is not None: st['tried']+=1
   if uses[pid]>=len(profiles[pid]['members']):
    if st is not None: st['injectivity_rejected']+=1
    continue
   new=[sig+(n,) for sig,n in zip(signatures,profiles[pid]['counts'])]; have=C.Counter(new)
   if any(have[s]<n for s,n in needed[depth].items()):
    if st is not None: st['signature_rejected']+=1
    continue
   if st is not None: st['passed']+=1
   assignment[order[depth]]=pid; uses[pid]+=1
   if depth+1==len(order): yield family_value(source,profiles,assignment)
   else: yield from dfs(depth+1,new)
   uses[pid]-=1; assignment[order[depth]]=None
 if all(domains): yield from dfs(0,[()]*nt)

def search_check(source,profiles,domains,search):
 order=order_for(source); eq(search['order'],[source['columns'][j] for j in order],'fixed source-only variable order')
 families=search['families']; assert len({tuple(f['profiles']) for f in families})==len(families)
 for f in families:
  assert all(p in domains[j] for j,p in enumerate(f['profiles']))
  eq(f,family_value(source,profiles,f['profiles']),'all witnessed assignment/pair counts')
 for s in search['stats']: eq(s['tried'],s['passed']+s['signature_rejected']+s['injectivity_rejected'],'statistics reconcile')
 eq(search['calls'],sum(s['passed'] for s in search['stats'][:-1]),'every accepted nonterminal prefix creates one recursive call')
 if any(not d for d in domains):
  eq(search['status'],'CONTRADICTED_EMPTY_COLUMN_DOMAIN','empty domain status')
  eq(search['empty_columns'],[c for c,d in zip(source['columns'],domains) if not d],'empty columns')
  assert search['complete'] and not families and not search['branches'] and search['calls']==0
  return dict(replay='EXACT_EMPTY_DOMAIN_CERTIFICATE',families=0)
 eq([b['first_profile'] for b in search['branches']],domains[order[0]],'all initial branches recorded')
 by_first=C.defaultdict(list)
 for f in families: by_first[f['profiles'][order[0]]].append(f)
 stats=[dict(tried=0,passed=0,signature_rejected=0,injectivity_rejected=0) for _ in order]
 stopped=False; deadline=time.monotonic()+300; reconstructed=[]
 for b in search['branches']:
  wanted=by_first[b['first_profile']]; eq(b['families'],len(wanted),'root branch family count')
  if b['complete']:
   assert not stopped,'complete branch after incomplete suffix'
   got=list(independent_enumeration(source,profiles,domains,first=b['first_profile'],deadline=deadline,stats=stats))
   eq(got,wanted,'exhaustive independent tuple branch replay'); reconstructed.extend(got)
   eq(b['status'],'COMPATIBLE_COMPLETE_BRANCH' if got else 'CONTRADICTED_COMPLETE_BRANCH','branch outcome')
  else:
   stopped=True; assert b['status'] in ('PARTIAL_UNKNOWN','UNVISITED_UNKNOWN')
   if b['status']=='UNVISITED_UNKNOWN': assert not wanted
   elif wanted:
    got=list(I.islice(independent_enumeration(source,profiles,domains,first=b['first_profile'],deadline=deadline),len(wanted)))
    eq(got,wanted,'partial branch saved prefix'); reconstructed.extend(got)
 if search['complete']:
  assert not stopped and search['stop_reason'] is None
  eq(search['status'],'COMPATIBLE_COMPLETE_ENUMERATION' if families else 'CONTRADICTED_COMPLETE_ENUMERATION','exhaustive status')
  eq(stats,search['stats'],'every depth attempt and rejection independently reproduced')
 else:
  assert stopped and search['stop_reason'] in ('TIME_LIMIT','FAMILY_LIMIT')
  eq(search['status'],'WITNESS_ENUMERATION_INCOMPLETE' if families else 'UNKNOWN_COMPUTATION','unknown remains unknown')
  if search['stop_reason']=='FAMILY_LIMIT': eq(len(families),16000,'family limit')
  else: assert search['seconds']>=120,'actual time limit not reached'
 eq(reconstructed,families,'all saved families in deterministic order')
 return dict(replay='EXHAUSTIVE_TUPLE_REPLAY' if search['complete'] else 'SAVED_PREFIX_REPLAY_UNKNOWN_SUFFIX_PRESERVED',families=len(families),stats_reproduced=search['complete'])

def witness_for(source,rows,profiles,f):
 used=C.Counter(); dictionary={}
 for j,c in enumerate(source['columns']):
  pid=f['profiles'][j]; dictionary[c]=profiles[pid]['members'][used[pid]]; used[pid]+=1
 sg={}; tg=C.defaultdict(list)
 for r in source['rows']: sg.setdefault(tuple(r['counts']),[]).append(r['id'])
 for i,r in enumerate(rows): tg[tuple(profiles[p]['counts'][i] for p in f['profiles'])].append(r['id'])
 assignment={}; domains=[]
 for sig,ids in sg.items():
  targets=tg[sig]; assert len(targets)>=len(ids)
  assignment.update((str(sid),tid) for sid,tid in zip(ids,targets))
  domains.append(dict(source_records=ids,target_paragraphs=targets,required_counts=list(sig)))
 return dict(canonical_dictionary=dictionary,canonical_record_assignment=assignment,all_record_domains=domains,carrier_alternatives={c:profiles[f['profiles'][j]]['members'] for j,c in enumerate(source['columns'])},claim_ceiling='Conditional partial term-family annotations only; residual content, polarity and source identity unknown.')

def prediction_tables(source):
 with (A/'SOURCE_PREDICTIONS.tsv').open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
 eq(len(rows),32,'prediction row count')
 for row,s in zip(rows,source['rows']):
  eq(int(row['source_record']),s['id'],'prediction source ID'); eq(row['source_name'],s['name'],'prediction name')
  eq([int(row[c]) for c in source['columns']],s['counts'],'all416 preregistered predictions')
 groups={}
 for r in source['rows']: groups.setdefault(tuple(r['counts']),[]).append(r['id'])
 observed=read(A/'SOURCE_EQUIVALENCE.json'); eq(observed['columns'],source['columns'],'equivalence columns')
 eq(observed['groups'],[dict(counts=list(s),source_records=ids) for s,ids in groups.items()],'all source equivalence classes')
 eq([ids for ids in groups.values() if len(ids)>1],[[11,24]],'indistinguishable bath pair')
 passed('registered_predictions_and_source_equivalence',cells=416,source_groups=31)

def consequence_tables(source,rows,profiles,domains,model,search):
 # These complete contradiction expansions are post-run explanatory artifacts.
 if not search['complete'] or search['families']:
  return dict(status='NOT_APPLICABLE_NO_COMPLETE_EMPTY_SEARCH')
 order=order_for(source); frontier=[()]; depth_counts=[]; checked=0; accepted_by_first=C.Counter()
 for depth,j in enumerate(order,1):
  path=A/f'{model}_DEPTH{depth}_CONSEQUENCES.tsv'
  assert path.exists(),'missing complete prefix consequence table'
  with path.open() as f: reported=list(csv.DictReader(f,delimiter='\t'))
  candidates=[prefix+(pid,) for prefix in frontier for pid in domains[j]]
  eq(len(reported),len(candidates),'all visited prefixes reported')
  needed=C.defaultdict(list)
  for r in source['rows']: needed[tuple(r['counts'][col] for col in order[:depth])].append(r['id'])
  next_frontier=[]; outcomes=C.Counter()
  for assignment,row in zip(candidates,reported):
   available=C.defaultdict(list)
   for i,r in enumerate(rows): available[tuple(profiles[p]['counts'][i] for p in assignment)].append(r['id'])
   uses=C.Counter(assignment)
   inject=[dict(profile=p,required_distinct=n,available_distinct=len(profiles[p]['members'])) for p,n in uses.items() if len(profiles[p]['members'])<n]
   deficits=[dict(signature=list(sig),required=len(ids),observed=len(available[sig]),source_records=ids,target_paragraphs=available[sig]) for sig,ids in sorted(needed.items()) if len(available[sig])<len(ids)]
   status='INJECTIVITY_CONTRADICTION' if inject else 'SIGNATURE_CAPACITY_CONTRADICTION' if deficits else 'PREFIX_COMPATIBLE'
   eq(row['families'].split(','),[source['columns'][k] for k in order[:depth]],'prefix family scope')
   eq([int(x) for x in row['profile_ids'].split(',')],list(assignment),'complete prefix enumeration order')
   eq(json.loads(row['all_carrier_alternatives']),[profiles[p]['members'] for p in assignment],'all carrier aliases')
   eq(row['status'],status,'prefix contradiction type')
   eq(json.loads(row['injectivity_deficits']),inject,'all injectivity certificates')
   eq(json.loads(row['all_count_deficits']),deficits,'all source/target signature certificates and IDs')
   checked+=1; outcomes[status]+=1
   if status=='PREFIX_COMPATIBLE':
    next_frontier.append(assignment)
    if depth==2: accepted_by_first[profiles[assignment[0]]['members'][0]]+=1
  depth_counts.append(dict(outcomes)); frontier=next_frontier
  eq(search['stats'][depth-1]['tried'],len(candidates),'post-run table covers actual attempts')
  if not frontier: break
 assert not frontier,'complete contradiction report cannot retain a full assignment'
 for deeper in range(depth+1,len(order)+1):
  assert not (A/f'{model}_DEPTH{deeper}_CONSEQUENCES.tsv').exists(),'unexpected deeper consequence table'
  eq(search['stats'][deeper-1],dict(tried=0,signature_rejected=0,injectivity_rejected=0,passed=0),'unvisited later variables')
 required=[dict(signature=list(sig),required=len(ids)) for sig,ids in sorted(needed.items())]
 want=dict(complete_contradiction_prefix=[source['columns'][j] for j in order[:depth]],depth_counts=depth_counts,source_requirements=required)
 eq(read(A/'CONTRADICTION_SUMMARY.json')[model],want,'explanatory summary')
 passed('every_prefix_certificate_'+model,table_rows=checked,depths=depth,accepted_pairs_by_first=dict(accepted_by_first))
 return want

def model_check(source,rows,model,summary):
 packet=read(A/(model+'.json')); eq((packet['edition'],packet['model']),('IT2a',model),'model identity')
 profiles=profiles_for(rows,model); eq(profiles,packet['profiles'],'all literal carriers and full count vectors')
 domains,table=domains_for(source,profiles)
 eq(dict(zip(source['columns'],domains)),packet['column_domains'],'all univariate domains')
 eq(table,packet['candidate_table'],'all histograms, zero requirements and deficits')
 with (A/(model+'_CANDIDATES.tsv')).open() as f: records=list(csv.DictReader(f,delimiter='\t'))
 eq(len(records),len(profiles),'candidate table completeness')
 for row,p,t in zip(records,profiles,table):
  eq(int(row['profile']),p['id'],'candidate ID'); eq(row['all_carriers'].split(),p['members'],'all equivalent literal members')
  eq(json.loads(row['paragraph_counts']),p['counts'],'complete71-paragraph vector')
  eq(row['eligible_families'].split(',') if row['eligible_families'] else [],t['eligible_families'],'candidate family list')
  eq(json.loads(row['all_single_column_deficits']),t['deficits'],'every candidate certificate')
 search=packet['search']; replay=search_check(source,profiles,domains,search)
 want=dict(status=search['status'],profiles=len(profiles),literal_carriers=sum(len(p['members']) for p in profiles),column_domain_sizes={c:len(d) for c,d in zip(source['columns'],domains)},complete=search['complete'],stop_reason=search['stop_reason'],profile_families=len(search['families']),dictionary_count_encountered=str(sum(int(f['dictionary_count']) for f in search['families'])),record_dictionary_pairs_encountered=str(sum(int(f['dictionary_count'])*int(f['record_assignment_count']) for f in search['families'])),seconds=search['seconds'])
 eq(summary,want,'model result summary')
 if search['families']:
  eq(read(A/(model+'_FIRST_WITNESS.json')),witness_for(source,rows,profiles,search['families'][0]),'complete first witness display')
  for family in search['families']:
   witness=witness_for(source,rows,profiles,family)
   eq(len(set(witness['canonical_dictionary'].values())),13,'every witnessed dictionary injective')
   eq(len(set(witness['canonical_record_assignment'].values())),32,'every witnessed record assignment injective')
 else: assert not (A/(model+'_FIRST_WITNESS.json')).exists(),'stale witness artifact'
 consequence_tables(source,rows,profiles,domains,model,search)
 passed('independent_model_'+model,profiles=len(profiles),literal_carriers=sum(len(p['members']) for p in profiles),replay=replay,positive_witness_path='EXERCISED' if search['families'] else 'NOT_EXERCISED_NO_ACTUAL_WITNESS',limits='NOT_EXERCISED' if search['complete'] else search['stop_reason'])

def synthetic_checks():
 spec=importlib.util.spec_from_file_location('primary_synthetic_only',E/'src/run.py')
 primary=importlib.util.module_from_spec(spec); spec.loader.exec_module(primary)
 rng=random.Random(967); cases=[]
 for _ in range(18):
  ns,nt,nc,np=rng.randint(1,3),rng.randint(3,5),rng.randint(1,3),rng.randint(2,4)
  ps=[dict(id=p,members=[f'v{p}a']+([f'v{p}b'] if rng.randrange(2) else []),counts=[rng.randrange(3) for _ in range(nt)]) for p in range(np)]
  source=dict(columns=[f'C{j}' for j in range(nc)],rows=[dict(id=i,counts=[rng.randrange(3) for _ in range(nc)]) for i in range(ns)])
  cases.append((source,ps))
 for members in (['a'],['a','b']):
  cases.append((dict(columns=['A','B'],rows=[dict(id=1,counts=[1,1])]),[dict(id=0,members=members,counts=[1,1])]))
 cases.append((dict(columns=['A','B'],rows=[dict(id=1,counts=[0,1]),dict(id=2,counts=[1,0])]),[dict(id=0,members=['a'],counts=[0,1,99]),dict(id=1,members=['b'],counts=[1,0,99])]))
 sat=unsat=0
 for source,ps in cases:
  domains,_=domains_for(source,ps); cp={m:p['id'] for p in ps for m in p['members']}; oracle=C.Counter()
  for dictionary in I.permutations(cp,len(source['columns'])):
   assignment=tuple(cp[m] for m in dictionary)
   for target_ids in I.permutations(range(len(ps[0]['counts'])),len(source['rows'])):
    if all(ps[assignment[j]]['counts'][i]==s['counts'][j] for s,i in zip(source['rows'],target_ids) for j in range(len(assignment))): oracle[assignment]+=1
  independent=list(independent_enumeration(source,ps,domains))
  values={tuple(f['profiles']):int(f['dictionary_count'])*int(f['record_assignment_count']) for f in independent}
  eq(values,dict(oracle),'explicit literal-dictionary and record-permutation oracle')
  result=primary.solve(source,ps,domains,seconds=30,cap=100000); assert result['complete']
  eq(result['families'],independent,'primary synthetic solver vs independent oracle')
  sat+=bool(oracle); unsat+=not bool(oracle)
  # Every canonical display key must be an actual member of the implicit family.
  rows=[dict(id=f'T{i}') for i in range(len(ps[0]['counts']))]
  for family in independent:
   ours=witness_for(source,rows,ps,family); theirs=primary.describe(source,rows,ps,family)
   theirs=json.loads(json.dumps(theirs)); eq(ours,theirs,'synthetic canonical and implicit witness families')
 toy=[dict(words=['aaaa','aba','aba']),dict(words=['a'])]
 profiles=profiles_for(toy,'WITHIN_GROUP_PIECE'); pieces={m:p['counts'] for p in profiles for m in p['members']}
 eq(pieces['a'],[3,1],'once-per-group piece presence'); eq(pieces['aa'],[1,0],'overlapping repeated piece is not multiplied')
 for model in MODELS: eq(profiles_for(toy,model),primary.profiles(toy,model),'primary piece/whole synthetic profiles')
 source=dict(columns=['A'],rows=[dict(id=1,counts=[1])]); ps=[dict(id=0,members=['a'],counts=[1,0]),dict(id=1,members=['b'],counts=[0,1])]
 limited=primary.solve(source,ps,[[0,1]],seconds=30,cap=1)
 assert not limited['complete'] and limited['stop_reason']=='FAMILY_LIMIT' and len(limited['families'])==1
 expired=primary.solve(source,ps,[[0,1]],seconds=-1,cap=100)
 assert not expired['complete'] and expired['stop_reason']=='TIME_LIMIT' and not expired['families']
 passed('synthetic_exhaustive_oracles',cases=len(cases),sat=sat,unsat=unsat,primary_tested=True,injectivity_and_count_overflow=True,canonical_witnesses=True,piece_presence=True,unknown_limits=True)

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--self-test',action='store_true'); args=parser.parse_args()
 synthetic_checks()
 if args.self_test:
  print(json.dumps(dict(status='SYNTHETIC_PASS',checks=CHECKS),separators=(',',':'))); return
 lock=hashes(); source=source_check(lock); prediction_tables(source); targets,scopes=targets_check()
 result=read(A/'RESULT.json')
 for key,value in dict(source_records=32,source_families=13,source_occurrences=166,confirmed_words=0,independent_confirmation_capacity=0,significance_claim=False).items(): eq(result[key],value,'summary '+key)
 eq(set(result['panels']),set(EDS),'all editions reported')
 for ed in EDS:
  eq(set(result['panels'][ed]),set(MODELS),'both models reported')
  for model in MODELS:
   if len(targets[ed])<32:
    want=dict(status='NO_LITERAL_CAPACITY' if scopes[ed]['complete'] else 'NO_COMPLETE_PARAGRAPH_CAPACITY',literal_paragraphs=len(targets[ed]),broader_scope='UNKNOWN_NONLITERAL_OR_BOUNDARIES')
    eq(result['panels'][ed][model],want,'capacity preserves broader unknown scope')
   else:
    eq(ed,'IT2a','fixed literal capacity'); model_check(source,targets[ed],model,result['panels'][ed][model])
 passed('complete_panels_summary_scope',editions=3,models=2,independent_confirmation=0,confirmed_words=0)
 hashes()
 receipt=dict(schema='gdt967_independent_validation.v1',status='VALIDATION_PASS',checks=CHECKS,
              source_review='src/SOURCE_REVIEW.md',validator_sha256=sha(Path(__file__)),result_sha256=sha(A/'RESULT.json'),
              scope='Source/data/computation correctness only; no independent semantic confirmation.')
 (A/'VALIDATION.json').write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps(dict(status=receipt['status'],checks=len(CHECKS)),separators=(',',':')))

if __name__=='__main__': main()
