import concurrent.futures,gzip,hashlib,json,urllib.request
from datetime import datetime,timezone
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'VManus-research-source-receipt/1.0'})
 with urllib.request.urlopen(req,timeout=45) as r:return r.read()
def one(s):
 data=fetch(s['url']);assert len(data)==s['bytes'] and sha(data)==s['sha256'],'SOURCE_IDENTITY_MISMATCH '+s['corpus_id']
 packed=gzip.compress(data,mtime=0);dest=B/s['local_file'];dest.write_bytes(packed)
 readme=fetch(s['readme_url']);rp=B/'artifacts/sources'/str(s['corpus_id']+'_README.md');rp.write_bytes(readme)
 # Only source format metadata, no profile counting or token sampling.
 header=data.split(b'\n\n',1)[0].decode('utf-8');comments=[line.split('=',1)[0].strip() for line in header.splitlines() if line.startswith('#')]
 return {'corpus_id':s['corpus_id'],'url':s['url'],'raw_bytes':len(data),'raw_sha256':sha(data),'compressed_sha256':sha(packed),'local_file':s['local_file'],'readme_url':s['readme_url'],'readme_file':str(rp.relative_to(B)),'readme_sha256':sha(readme),'first_sentence_comment_keys':comments,'status':'SOURCE_HASH_MATCH'}
def main():
 lock=json.loads((B/'src/ACQUISITION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert sha((B/p).read_bytes())==h
 spec=json.loads((B/'src/SOURCE_SPEC.json').read_text());results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
  futures={ex.submit(one,s):s for s in spec['sources']}
  for future,s in futures.items():
   try:results.append(future.result())
   except Exception as e:results.append({'corpus_id':s['corpus_id'],'status':'SOURCE_ACQUISITION_STOP','error':str(e)})
 receipt={'utc':datetime.now(timezone.utc).isoformat(),'sources':results,'scope':'Only selected public historical-source files; no native payload archive opened.'}
 (B/'artifacts/SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
