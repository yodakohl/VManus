import collections,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def decode(word,codes):
 ways=[0]*(len(word)+1);ways[0]=1;back={}
 for i in range(len(word)):
  if not ways[i]:continue
  for c in codes:
   j=i+len(c)
   if tuple(word[i:j])==c:ways[j]+=ways[i];back[j]=(i,c)
 assert ways[-1]<=1
 if not ways[-1]:return None
 out=[];j=len(word)
 while j:j,c=back[j];out.append(c)
 return out[::-1]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());out=json.loads((B/'artifacts/RESULT.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));old=json.loads((R/s['old_tables']).read_text());bound=json.loads((R/s['bound']).read_text());expected=[];checks=[]
 for reader in s['readers']:
  assert bound['readers'][reader]['summary']['necessary_nontrivial_bound']==27
  for head in s['heads']:
   parent=next(v for v in old['cases'] if v['reader']==reader and v['head']==head);code=[tuple(x['units']) for x in parent['code_usage']];minimum=min(x['occurrences'] for x in parent['code_usage'] if len(x['units'])>1)
   for removal in sorted(tuple(x['units']) for x in parent['code_usage'] if len(x['units'])>1 and x['occurrences']==minimum):expected.append((reader,head,removal))
 assert [(c['reader'],c['head'],tuple(c['removed_code'])) for c in out['cases']]==expected
 for c in out['cases']:
  reader=c['reader'];codes=list(map(tuple,c['codebook']));removed=tuple(c['removed_code']);full=codes+[removed];assert len(set(full))==27 and len(codes)==26
  assert all(x[:len(y)]!=y and y[:len(x)]!=x for i,x in enumerate(codes) for y in codes[:i]);rows=data[reader];fail=[];newusage=collections.Counter();old_removed_uses=0;active=0
  for row in rows:
   assert not row['page'].startswith('f84') and row['page']!='f116v';word=row['units'];original=decode(word,full);assert original is not None;old_removed_uses+=original.count(removed);parts=decode(word,codes)
   if parts is None:assert removed in original;fail.append(row)
   else:
    assert parts==original and [u for p in parts for u in p]==word;newusage.update(parts);active+=any(len(p)>1 for p in parts)
  assert fail==c['failure_rows'] and len(fail)==c['unparsed_groups']==1 and old_removed_uses==c['old_entry_occurrences']==1
  assert active==c['active_accepted_groups']>0 and c['used_retained_entries']==len(newusage)
  assert c['groups']==len(rows) and c['accepted_groups']==len(rows)-len(fail)
  assert c['retained_usage']==[{'units':list(x),'occurrences':n} for x,n in sorted(newusage.items())]
  assert c['global_nontrivial_lower_bound']==c['attained_upper_bound']==1 and c['status']=='EXACT_MINIMUM_ONE_TOKEN_EXCEPTION'
  checks.append({'reader':reader,'head':c['head'],'unparsed_tokens':len(fail),'active_accepted':active,'code_entries':len(codes),'unchanged_accepted_parses':True})
 # Distinguish code-use count from affected token count; a repeated use in one word is still one failed token.
 full=[('a',),('b','a'),('b','b')];kept=[('a',),('b','b')]
 assert decode(list('baba'),full)==[('b','a'),('b','a')] and decode(list('baba'),kept) is None
 assert decode(list('bb'),kept)==[('b','b')]
 val={'status':'PASS','checks':checks,'independence':'Explicit dynamic codeword parses; no primary import; full original population retained. Global lower bound inherited from hash-bound1234proof, not rediscovered by six models.','limits':'No diagnosis of source errors, meaning, historical sourcealphabet or successful writer.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val,indent=2))
if __name__=='__main__':main()
