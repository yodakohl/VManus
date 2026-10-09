import collections,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def parse(word,codes):
 pos=0;parts=[]
 while pos<len(word):
  found=[c for c in codes if tuple(word[pos:pos+len(c)])==c]
  assert len(found)<=1
  if not found:return None
  c=found[0];parts.append(c);pos+=len(c)
 return parts

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));old=json.loads((R/s['old_tables']).read_text());bound=json.loads((R/s['bound']).read_text());cases=[]
 for reader in s['readers']:
  rows=data[reader];assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
  assert bound['readers'][reader]['summary']['necessary_nontrivial_bound']==27
  for head in s['heads']:
   parent=next(x for x in old['cases'] if x['reader']==reader and x['head']==head);codes=[tuple(x['units']) for x in parent['code_usage']];assert len(codes)==27 and parent['failed_groups']==0
   assert all(not(b[:len(a)]==a) for a in codes for b in codes if a!=b)
   usage=collections.Counter();oldparses={}
   for row in rows:
    parts=parse(row['units'],codes);assert parts is not None;oldparses[row['id']]=parts;usage.update(parts)
   assert usage==collections.Counter({tuple(x['units']):x['occurrences'] for x in parent['code_usage']})
   least=min(usage[c] for c in codes if len(c)>1)
   for removed in sorted(c for c in codes if len(c)>1 and usage[c]==least):
    kept=[c for c in codes if c!=removed];failures=[];newusage=collections.Counter();active=0
    for row in rows:
     parts=parse(row['units'],kept)
     if parts is None:failures.append(row)
     else:
      assert parts==oldparses[row['id']];newusage.update(parts);active+=any(len(c)>1 for c in parts)
    upper=len(failures);lower=1 if active else None;status='EXACT_MINIMUM_ONE_TOKEN_EXCEPTION' if lower==upper==1 else 'CONSTRUCTION_UPPER_BOUND_ONLY'
    cases.append({'reader':reader,'head':head,'removed_code':list(removed),'old_entry_occurrences':usage[removed],'codebook':[list(c) for c in kept],'code_entries':len(kept),'groups':len(rows),'accepted_groups':len(rows)-len(failures),'unparsed_groups':len(failures),'failure_rows':failures,'active_accepted_groups':active,'used_retained_entries':len(newusage),'retained_usage':[{'units':list(c),'occurrences':n} for c,n in sorted(newusage.items())],'global_nontrivial_lower_bound':lower,'attained_upper_bound':upper,'status':status})
 result={'status':'ALL_READERS_EXACT_NONTRIVIAL_PREFIX26_EXCEPTION_MINIMUM_ONE' if all(c['status']=='EXACT_MINIMUM_ONE_TOKEN_EXCEPTION' for c in cases) else 'INCOMPLETE_RADIUS_RESULT','cases':cases,'meaning':'Formal whole-token model discrepancy, not diagnosed errors, sourceletter values or correcteddata. Trivial singleton identity has0cost and is explicitly excluded from the nontrivial class.'}
 (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'cases':[{k:c[k] for k in ['reader','head','removed_code','code_entries','groups','unparsed_groups','active_accepted_groups','failure_rows']} for c in cases]},indent=2))
if __name__=='__main__':main()
