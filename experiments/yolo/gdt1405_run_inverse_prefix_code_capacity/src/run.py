#!/usr/bin/env python3
"""Necessary prefix-code capacity after a hypothetical native-run inverse."""
from pathlib import Path
import argparse,collections,gzip,hashlib,importlib.util,itertools,json,re,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 p=B/'artifacts'/n;b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def collapse(u):return tuple(x for j,x in enumerate(u) if not(j and x in ('e','i') and x==u[j-1]))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def controls(s,engine):
 fixture=module('legacy_prefix_fixtures',R/s['fixtures_path']);old=fixture.run();old.pop('checked_utc');old.pop('named');n=0
 for length in range(5):
  for u in itertools.product(['a','e','i'],repeat=length):
   assert collapse(collapse(u))==collapse(u);n+=1
   if collapse(u)!=u:continue
   indices=[j for j,x in enumerate(u) if x in ('e','i')]
   for runs in itertools.product([1,2,3],repeat=len(indices)):
    z=[];k=0
    for x in u:
     if x in ('e','i'):z.extend([x]*runs[k]);k+=1
     else:z.append(x)
    assert collapse(z)==u;n+=1
 return {'status':'PASS_SOURCE_FREE_CONTROLS','legacy_prefix_fixtures':old,'collapse_inverse_checks':n,'native_data_read':False}
def upper(rows,signs,head,tails):
 codes=sorted([(x,) for x in signs if x!=head]+[(head,t) for t in tails]);assert all(a==b or b[:len(a)]!=a for a in codes for b in codes)
 usage=collections.Counter();failed=[];active=0
 for row in rows:
  word=row['collapsed_units'];k=0;parsed=[]
  while k<len(word):
   code=(head,word[k+1]) if word[k]==head and k+1<len(word) else (word[k],)
   if code not in codes:break
   parsed.append(code);k+=len(code)
  if k!=len(word):failed.extend(row['ids']);continue
  for c in parsed:usage[c]+=row['count']
  if any(len(c)>1 for c in parsed):active+=row['count']
 return {'head':head,'offered_codes':[list(c) for c in codes],'used_codes':[list(c) for c in sorted(usage)],'used_entries':len(usage),'code_usage':[{'code':list(c),'occurrences':n} for c,n in sorted(usage.items())],'failed_ids':sorted(failed),'failed_groups':len(failed),'active_groups':active,'covers_all':not failed}
def bridge(rows,summary,s):
 env=read(R/s['source_envelope_path'])['sources'];lookup={x['form']:x for x in rows};F=set(summary['F']) if summary is not None else set();items=[]
 for form,u in s['retained_counterforms'].items():
  row=lookup.get(form);c=collapse(u);d={};pattern=tuple(d.setdefault(x,len(d)) for x in c);pk='.'.join(map(str,pattern));missing={n:pk not in env[n]['modes']['BIDIR'] for n in s['source_names']}
  if row is not None:assert row['units']==u and row['collapsed_units']==list(c)
  items.append({'form':form,'present':row is not None,'count':row['count'] if row else 0,'leaves':row['leaves'] if row else [],'collapsed_units':list(c),'forced':set(c)<=F,'not_forced':sorted(set(c)-F),'pattern_key':pk,'source_missing':missing})
 exclusions={}
 for n in s['source_names']:
  witnesses=[x['form'] for x in items if x['present'] and x['forced'] and x['source_missing'][n]];exclusions[n]={'status':'UNKNOWN_INCOMPLETE' if summary is None else 'EXCLUDED_BY_FORCED_SINGLETON_COUNTERFORM' if witnesses else 'NO_RETAINED_COUNTERFORM_EXCLUSION','witnesses':witnesses}
 return items,exclusions

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args();s=read(B/'src/SPEC.json');engine=module('engine',R/s['engine_path'])
 if a.controls:print(json.dumps(controls(s,engine)));return
 assert not(B/'artifacts/RESULT.json').exists()
 lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/s['native_path']);families={};cases=[]
 for ed in s['readers']:
  by=collections.defaultdict(list)
  for row in data[ed]:
   assert row['edition']==ed and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');by[row['ivtff_group_raw']].append(row)
  records=[]
  for form,occ in sorted(by.items()):
   u=tuple(occ[0]['units']);assert all(tuple(x['units'])==u for x in occ);leaves=sorted({re.match(r'^f\d+',x['page']).group() for x in occ});records.append({'form':form,'units':list(u),'collapsed_units':list(collapse(u)),'count':len(occ),'leaves':leaves,'ids':sorted(x['id'] for x in occ)})
  families[ed]=records
  for panel in s['panels']:
   rows=records if panel=='FULL' else [x for x in records if len(x['leaves'])>=2];W={tuple(x['collapsed_units']) for x in rows};cert=engine.derive(W,s['closure_seconds_per_case']);name='CERT_'+ed+'_'+panel+'.json.gz';save(name,cert);summary=cert.get('summary');bound=summary['necessary_nontrivial_bound'] if summary else None
   caps={str(k):'UNKNOWN_INCOMPLETE' if summary is None else 'EXCLUDED_NONTRIVIAL' if bound is None or bound>k else 'NOT_EXCLUDED' for k in s['caps']}
   counterforms,exclusions=bridge(rows,summary,s)
   case={'retained_counterforms':counterforms,'source_exclusions':exclusions,'reader':ed,'panel':panel,'groups':sum(x['count'] for x in rows),'raw_types':len(rows),'collapsed_types':len(W),'changed_groups':sum(x['count'] for x in rows if x['units']!=x['collapsed_units']),'certificate':name,'closure_status':cert['status'],'summary':summary,'caps':caps,'upper_tables':[upper(rows,s['signs'],h,tails) for h,tails in s['fixed_tables'].items()]};cases.append(case);print(json.dumps({'reader':ed,'panel':panel,'status':cert['status'],'forced':summary['F'] if summary else None,'necessary_bound':bound,'upper':[{k:t[k] for k in ['head','used_entries','failed_groups','active_groups']} for t in case['upper_tables']]}),flush=True)
 save('FAMILIES.json.gz',{'readers':families});save('RESULT.json',{'experiment_id':'GDT1405','status':'COMPLETE_PREFIX_CAPACITY' if all(x['closure_status']=='COMPLETE' for x in cases) else 'UNKNOWN_INCOMPLETE','cases':cases,'claim_ceiling':s['claim_ceiling']})
if __name__=='__main__':main()
