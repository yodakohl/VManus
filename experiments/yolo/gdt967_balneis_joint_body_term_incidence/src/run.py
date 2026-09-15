"""Finite complete-row incidence enumeration; no language score or decoder."""
import argparse,collections,csv,hashlib,importlib.util,json,math,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
MODELS=('WHOLE_GROUP','WITHIN_GROUP_PIECE');SECONDS=120;FAMILY_CAP=16000

def read(p):return json.loads(p.read_text())
def put(name,x):(A/name).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def lockcheck():
 for p,h in read(E/'PREREG_LOCK.json')['files'].items():
  assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h, p

def intake():
 path=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/src/run.py'
 sp=importlib.util.spec_from_file_location('gdt928_unchanged',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 panels,_=m.load();allowed={f'f{n}{s}' for n in range(75,84) for s in 'rv'};out={};scope={}
 for ed,rs in panels.items():
  allrows=[];good=[]
  for p in rs:
   if p['page'] not in allowed:continue
   assert not p['page'].startswith('f84')
   bad=[l['locus'] for l in p['lines'] if not l['anchor_eligible']]
   allrows.append({'id':p['id'],'page':p['page'],'leaf':p['leaf'],'groups':p['groups'],'literal':not bad,'ineligible_lines':bad})
   if not bad:good.append({'id':p['id'],'page':p['page'],'leaf':p['leaf'],'words':[w for l in p['lines'] for w in l['words']],'loci':[l['locus'] for l in p['lines']],'source_ids':[x for l in p['lines'] for x in l['source_ids']]})
  out[ed]=sorted(good,key=lambda p:p['id']);scope[ed]={'complete':len(allrows),'literal':len(good),'nonliteral':len(allrows)-len(good),'rows':allrows,'independent_confirmation_capacity':0}
 return out,scope

def profiles(rows,model):
 vectors={};n=len(rows)
 for i,p in enumerate(rows):
  for w,count in collections.Counter(p['words']).items():
   pieces={w} if model=='WHOLE_GROUP' else {w[a:b] for a in range(len(w)) for b in range(a+1,len(w)+1)}
   for s in pieces:
    if s not in vectors:vectors[s]=[0]*n
    vectors[s][i]+=count
 grouped=collections.defaultdict(list)
 for s,v in sorted(vectors.items()):grouped[tuple(v)].append(s)
 ps=[{'members':ss,'counts':list(v)} for v,ss in grouped.items()];ps.sort(key=lambda p:p['members'][0])
 for i,p in enumerate(ps):p['id']=i
 return ps

def domains(source,ps):
 cols=source['columns'];rows=source['rows'];required=[collections.Counter(r['counts'][j] for r in rows) for j in range(len(cols))]
 ds=[[] for _ in cols];table=[]
 for p in ps:
  h=collections.Counter(p['counts']);deficits={}
  for j,c in enumerate(cols):
   missing=[{'count':v,'required':n,'observed':h[v]} for v,n in sorted(required[j].items()) if h[v]<n]
   if missing:deficits[c]=missing
   else:ds[j].append(p['id'])
  table.append({'profile':p['id'],'eligible_families':[cols[j] for j,d in enumerate(ds) if p['id'] in d],'deficits':deficits})
 return ds,table

def falling(n,k):return math.prod(range(n-k+1,n+1))
def signatures(source,order,base):
 vals=[0]*len(source['rows']);hist=[]
 for j in order:
  vals=[v*base+r['counts'][j] for v,r in zip(vals,source['rows'])];hist.append(collections.Counter(vals))
 return hist

def solve(source,ps,ds,seconds=SECONDS,cap=FAMILY_CAP):
 cols=source['columns'];sr=source['rows'];n=len(ps[0]['counts']) if ps else 0
 order=sorted(range(len(cols)),key=lambda j:(-sum(r['counts'][j]>0 for r in sr),-max(r['counts'][j] for r in sr),cols[j]))
 base=max(v for r in sr for v in r['counts'])+2;hs=signatures(source,order,base)
 result={'order':[cols[j] for j in order],'families':[],'branches':[],'stats':[{'tried':0,'signature_rejected':0,'injectivity_rejected':0,'passed':0} for _ in order],'complete':True,'stop_reason':None,'calls':0}
 if any(not d for d in ds):
  result.update(status='CONTRADICTED_EMPTY_COLUMN_DOMAIN',empty_columns=[cols[j] for j,d in enumerate(ds) if not d],seconds=0.0);return result
 vecs=[[min(v,base-1) for v in p['counts']] for p in ps];start=time.monotonic();deadline=start+seconds
 assigned=[None]*len(cols);used=collections.Counter();last_depth=len(order)-1
 def expired():
  if time.monotonic()>=deadline:result['complete']=False;result['stop_reason']='TIME_LIMIT';return True
  if len(result['families'])>=cap:result['complete']=False;result['stop_reason']='FAMILY_LIMIT';return True
  return False
 def accept(depth,pid,current):
  st=result['stats'][depth];st['tried']+=1
  if used[pid]>=len(ps[pid]['members']):st['injectivity_rejected']+=1;return None
  nv=[v*base+w for v,w in zip(current,vecs[pid])];h=collections.Counter(nv)
  if any(h[k]<need for k,need in hs[depth].items()):st['signature_rejected']+=1;return None
  st['passed']+=1;return nv
 def recurse(depth,current):
  result['calls']+=1
  if expired():return False
  for pid in ds[order[depth]]:
   if expired():return False
   nv=accept(depth,pid,current)
   if nv is None:continue
   assigned[order[depth]]=pid;used[pid]+=1
   if depth==last_depth:
    h=collections.Counter(nv);record_count=math.prod(falling(h[k],need) for k,need in hs[depth].items());dict_count=math.prod(falling(len(ps[p]['members']),q) for p,q in used.items())
    result['families'].append({'profiles':list(assigned),'dictionary_count':str(dict_count),'record_assignment_count':str(record_count)})
   else:
    if not recurse(depth+1,nv):used[pid]-=1;assigned[order[depth]]=None;return False
   used[pid]-=1;assigned[order[depth]]=None
  return True
 for ix,pid in enumerate(ds[order[0]]):
  b={'first_profile':pid,'complete':False,'families':0,'status':'UNVISITED_UNKNOWN'};result['branches'].append(b)
  if not result['complete'] or expired():continue
  old=len(result['families']);nv=accept(0,pid,[0]*n)
  if nv is not None:
   assigned[order[0]]=pid;used[pid]+=1
   if last_depth==0:
    h=collections.Counter(nv);result['families'].append({'profiles':list(assigned),'dictionary_count':str(len(ps[pid]['members'])),'record_assignment_count':str(math.prod(falling(h[k],q) for k,q in hs[0].items()))});done=True
   else:done=recurse(1,nv)
   used[pid]-=1;assigned[order[0]]=None
  else:done=True
  b.update(complete=done,families=len(result['families'])-old,status=('COMPATIBLE_COMPLETE_BRANCH' if len(result['families'])>old else 'CONTRADICTED_COMPLETE_BRANCH') if done else 'PARTIAL_UNKNOWN')
 result['seconds']=time.monotonic()-start
 result['status']=('COMPATIBLE_COMPLETE_ENUMERATION' if result['families'] else 'CONTRADICTED_COMPLETE_ENUMERATION') if result['complete'] else ('WITNESS_ENUMERATION_INCOMPLETE' if result['families'] else 'UNKNOWN_COMPUTATION')
 return result

def describe(source,rows,ps,family):
 selected={};used=collections.Counter();out=[]
 for j,c in enumerate(source['columns']):
  pid=family['profiles'][j];selected[c]=ps[pid]['members'][used[pid]];used[pid]+=1
 source_sigs=collections.defaultdict(list);target_sigs=collections.defaultdict(list)
 for r in source['rows']:source_sigs[tuple(r['counts'])].append(r['id'])
 for i,p in enumerate(rows):target_sigs[tuple(ps[pid]['counts'][i] for pid in family['profiles'])].append(p['id'])
 assignment={}
 for sig,ids in source_sigs.items():
  targets=target_sigs[sig];assert len(targets)>=len(ids)
  for sid,tid in zip(ids,targets):assignment[sid]=tid
  out.append({'source_records':ids,'target_paragraphs':targets,'required_counts':list(sig)})
 return {'canonical_dictionary':selected,'canonical_record_assignment':assignment,'all_record_domains':out,'carrier_alternatives':{c:ps[family['profiles'][j]]['members'] for j,c in enumerate(source['columns'])},'claim_ceiling':'Conditional partial term-family annotations only; residual content, polarity and source identity unknown.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--describe-family',nargs=2,metavar=('MODEL','INDEX'));args=ap.parse_args();lockcheck();source=read(E/'src/SOURCE_MATRIX.json')
 if args.describe_family:
  model,index=args.describe_family;packet=read(A/(model+'.json'));rows=read(A/'TARGET.json')['IT2a'];print(json.dumps(describe(source,rows,packet['profiles'],packet['search']['families'][int(index)]),ensure_ascii=False,indent=2));return
 target,scope=intake();put('TARGET.json',target);put('SCOPE.json',scope);summary={'source_records':len(source['rows']),'source_families':len(source['columns']),'source_occurrences':sum(sum(r['counts']) for r in source['rows']),'panels':{},'confirmed_words':0,'independent_confirmation_capacity':0,'significance_claim':False}
 for ed,rows in target.items():
  summary['panels'][ed]={}
  for model in MODELS:
   if len(rows)<len(source['rows']):summary['panels'][ed][model]={'status':'NO_LITERAL_CAPACITY' if scope[ed]['complete'] else 'NO_COMPLETE_PARAGRAPH_CAPACITY','literal_paragraphs':len(rows),'broader_scope':'UNKNOWN_NONLITERAL_OR_BOUNDARIES'};continue
   assert ed=='IT2a','unexpected new capacity; stop without scope repair'
   ps=profiles(rows,model);ds,table=domains(source,ps);sr=solve(source,ps,ds);packet={'edition':ed,'model':model,'profiles':ps,'column_domains':{c:ds[j] for j,c in enumerate(source['columns'])},'candidate_table':table,'search':sr};put(model+'.json',packet)
   with (A/(model+'_CANDIDATES.tsv')).open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['profile','all_carriers','paragraph_counts','eligible_families','all_single_column_deficits'])
    for p,t in zip(ps,table):w.writerow([p['id'],' '.join(p['members']),json.dumps(p['counts']),','.join(t['eligible_families']),json.dumps(t['deficits'],separators=(',',':'))])
   if sr['families']:put(model+'_FIRST_WITNESS.json',describe(source,rows,ps,sr['families'][0]))
   summary['panels'][ed][model]={'status':sr['status'],'profiles':len(ps),'literal_carriers':sum(len(p['members']) for p in ps),'column_domain_sizes':{c:len(ds[j]) for j,c in enumerate(source['columns'])},'complete':sr['complete'],'stop_reason':sr['stop_reason'],'profile_families':len(sr['families']),'dictionary_count_encountered':str(sum(int(f['dictionary_count']) for f in sr['families'])),'record_dictionary_pairs_encountered':str(sum(int(f['dictionary_count'])*int(f['record_assignment_count']) for f in sr['families'])),'seconds':sr['seconds']}
   print(json.dumps({'edition':ed,'model':model,**summary['panels'][ed][model]}),flush=True);put('RESULT.json',summary)
 put('RESULT.json',summary)
if __name__=='__main__':main()
