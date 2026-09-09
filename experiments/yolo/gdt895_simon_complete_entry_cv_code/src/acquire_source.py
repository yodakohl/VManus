"""Acquire immutable selected archive HTML; no corpus text extraction or target access."""
import argparse,pathlib,json,urllib.request,urllib.error,urllib.parse,datetime,time,threading,concurrent.futures,hashlib,re,collections
P=None
DEADLINE=None
INITIAL_CACHES=[]
STOP=threading.Event();LOCK=threading.Lock();LAST=0.;STOP_REASON=None
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(path,d):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def gate():
 global LAST
 with LOCK:
  while True:
   if STOP.is_set():raise RuntimeError('GLOBAL_STOP')
   if time.time()>=DEADLINE:raise RuntimeError('ACQUISITION_DEADLINE')
   wait=3-(time.monotonic()-LAST)
   if wait<=0:LAST=time.monotonic();return
   time.sleep(min(wait,.25))
def stop(reason):
 global STOP_REASON
 STOP_REASON=reason;STOP.set()
class Redirects(urllib.request.HTTPRedirectHandler):
 def __init__(self,chain):self.chain=chain
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  self.chain.append({'from':req.full_url,'to':newurl,'code':code,'utc':utc()})
  if urllib.parse.urlparse(newurl).hostname!='web.archive.org':raise RuntimeError('BLOCKED_NONARCHIVE_REDIRECT')
  gate();return super().redirect_request(req,fp,code,msg,headers,newurl)
def cached_sources():
 sources=[]
 for root in INITIAL_CACHES:
  for f in root.glob('*.json'):
   try:d=json.loads(f.read_text())
   except Exception:continue
   if not isinstance(d,dict):continue
   url=d.get('final_url',d.get('url'))
   filename=d.get('file')
   if not filename and f.name.endswith('.receipt.json'):filename=f.name.replace('.receipt.json','.html')
   if url and filename and (root/filename).exists():sources.append((url,root/filename))
 return sources
CACHE=[]
def reuse(r):
 # Same exact selected timestamp and original URL; never nearest-date substitution.
 for url,f in CACHE:
  if url==r['replay_url']:
   b=f.read_bytes()
   if b'mw-content-text' in b and b'Bot Verification' not in b:
    out=P/'html'/(r['id']+'.html');out.write_bytes(b)
    return {'status':'ACQUIRED_FROM_IDENTICAL_CAPTURE_CACHE','final_url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'file':'html/'+out.name,'cached_file_basename':f.name,'oldid':oldid(b)}
def oldid(b):
 m=re.search(rb'(?:&amp;|&)oldid=(\d+)',b);return int(m[1]) if m else None
def run(r):
 receipt=P/'receipts'/(r['id']+'.json')
 if receipt.exists():
  prior=json.loads(receipt.read_text())
  if prior['status']!='PENDING':return prior['status']
 d={'id':r['id'],'title':r['title'],'selected':r['selected'],'requested_url':r['replay_url'],'attempts':[],'status':r['status']}
 if r['selected'] is None:write(receipt,d);return d['status']
 cached=reuse(r)
 if cached:d.update(cached);d['finished_utc']=utc();write(receipt,d);return d['status']
 for attempt in range(1,4):
  if STOP.is_set() or time.time()>=DEADLINE:
   d['status']='NOT_ATTEMPTED_GLOBAL_STOP' if STOP.is_set() else 'DEADLINE_INCOMPLETE';break
  a={'attempt':attempt,'redirect_chain':[]};retry=False;backoff=15*attempt
  try:
   gate();a['started_utc']=utc();op=urllib.request.build_opener(Redirects(a['redirect_chain']))
   with op.open(r['replay_url'],timeout=30) as response:
    b=response.read();a.update(http_status=response.status,final_url=response.url,headers={k:response.headers.get(k) for k in ['Content-Type','Memento-Datetime','X-Archive-Orig-Last-Modified']})
   bf=P/'attempts'/(r['id']+'_'+str(attempt)+'.html');bf.write_bytes(b);a.update(file='attempts/'+bf.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),oldid=oldid(b))
   challenge=bool(re.search(rb'<title[^>]*>\s*(?:Bot Verification|Just a moment|Access Denied|Security Check|Captcha)',b,re.I)) or b'cf-chl-' in b
   if challenge:stop('ACCESS_CHALLENGE');d['status']='ACCESS_CHALLENGE_GLOBAL_STOP'
   elif b'mw-content-text' not in b:d['status']='NOT_MEDIAWIKI_CONTENT'
   else:
    final_stamp=re.search(r'/web/(\d{14})',a['final_url'])
    if not final_stamp or final_stamp[1]!=r['selected']['timestamp']:d['status']='CAPTURE_TIMESTAMP_MISMATCH'
    else:
     out=P/'html'/(r['id']+'.html');out.write_bytes(b);d.update(status='ACQUIRED',file='html/'+out.name,final_url=a['final_url'],sha256=a['sha256'],bytes=len(b),oldid=a['oldid'])
  except urllib.error.HTTPError as e:
   a.update(http_status=e.code,error=str(e),final_url=e.url)
   if e.code==429:
    if attempt>=2:stop('PERSISTENT_429');d['status']='PERSISTENT_429_GLOBAL_STOP'
    else:retry=True;backoff=max(60,int(e.headers.get('Retry-After','60')) if e.headers.get('Retry-After','60').isdigit() else 60);d['status']='HTTP_429_RETRY'
   elif e.code in [408,500,502,503,504]:retry=True;d['status']='TRANSIENT_HTTP_FAILED'
   else:d['status']='HTTP_'+str(e.code)
  except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as e:a['error']=str(e);retry=True;d['status']='TRANSIENT_NETWORK_FAILED'
  except RuntimeError as e:a['error']=str(e);d['status']=str(e)
  except Exception as e:a['error']=repr(e);d['status']='UNEXPECTED_ERROR'
  a['finished_utc']=utc();d['attempts'].append(a);write(receipt,d)
  if not retry or attempt==3:break
  until=min(time.time()+backoff,DEADLINE)
  while time.time()<until and not STOP.is_set():time.sleep(min(.5,until-time.time()))
 d['finished_utc']=utc();write(receipt,d);return d['status']
def progress():
 counts=collections.Counter()
 for f in (P/'receipts').glob('*.json'):
  try:counts[json.loads(f.read_text())['status']]+=1
  except Exception:pass
 d={'utc':utc(),'counts':dict(counts),'global_stop':STOP_REASON,'deadline_utc':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat()};write(P/'PROGRESS.json',d);return d

def prepare(inventory_path):
 """Freeze metadata only. Re-querying CDX may change availability; never replace a frozen fit pool."""
 params=[('url','simonofgenoa.org/index.php?title='),('matchType','prefix'),('output','json'),('filter','statuscode:200'),('filter','mimetype:text/html'),('fl','timestamp,original,mimetype,statuscode,digest,length'),('showResumeKey','true')]
 url='https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(url,timeout=90) as response:raw=response.read();final_url=response.url
 data=json.loads(raw)  # Fail closed if a resume token or non-JSON challenge is returned.
 if data[0]!=['timestamp','original','mimetype','statuscode','digest','length']:raise ValueError('unexpected CDX schema')
 inventory=json.loads(inventory_path.read_text());anchor=datetime.datetime.strptime('20220812000000','%Y%m%d%H%M%S');rows=collections.defaultdict(list);reject=collections.Counter();seen=set()
 for values in data[1:]:
  if len(values)!=6:raise ValueError('incomplete CDX row')
  r=dict(zip(data[0],values));u=urllib.parse.urlparse(r['original']);q=urllib.parse.parse_qs(u.query,keep_blank_values=True)
  if u.hostname not in ['simonofgenoa.org','www.simonofgenoa.org'] or u.path!='/index.php' or set(q)!={'title'} or len(q['title'])!=1:reject['non_plain_title_url']+=1;continue
  if r['mimetype']!='text/html' or r['statuscode']!='200':reject['not_html200']+=1;continue
  title=q['title'][0];key=(title,r['timestamp'],r['original'])
  if key in seen:reject['duplicate_metadata_row']+=1;continue
  seen.add(key);rows[title].append(r)
 def order(r):
  dt=datetime.datetime.strptime(r['timestamp'],'%Y%m%d%H%M%S');return(abs((dt-anchor).total_seconds()),dt,r['original'])
 records=[]
 for rank,e in enumerate(inventory['entries']):
  candidates=sorted(rows.get(e['title'],[]),key=order);choice=candidates[0] if candidates else None
  records.append({'id':f'{rank:04d}','title':e['title'],'index_provenance':e['provenance'],'candidate_captures':candidates,'selected':choice,'replay_url':('https://web.archive.org/web/'+choice['timestamp']+'id_/'+choice['original']) if choice else None,'status':'PENDING' if choice else 'NO_EXACT_TITLE_CAPTURE_METADATA'})
 result={'schema':'simon-fixed-captures-v1','inventory_sha256':hashlib.sha256(inventory_path.read_bytes()).hexdigest(),'cdx_sha256':hashlib.sha256(raw).hexdigest(),'anchor':'20220812000000','policy':'Exact decoded title string; no case/underscore/space/diacritic alias normalization. Nearest absolute timestamp; tie earlier; identical timestamp tie originalURLlexical for determinism. Redirects documented duringreplay.','metadata_rows':len(data)-1,'rejected_rows':dict(reject),'indexed_titles':len(records),'selected_titles':sum(r['selected'] is not None for r in records),'missing_metadata_titles':sum(r['selected'] is None for r in records),'records':records}
 if (P/'CAPTURES.json').exists():raise ValueError('refusing to overwrite frozen CAPTURES.json')
 (P/'CDX_ALL.raw').write_bytes(raw);write(P/'CDX_ALL_RECEIPT.json',{'url':url,'final_url':final_url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)});write(P/'CAPTURES.json',result)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--cache',type=pathlib.Path,required=True)
 parser.add_argument('--inventory',type=pathlib.Path,required=True)
 parser.add_argument('--deadline',required=True,help='ISO8601 timezone-aware UTC deadline')
 parser.add_argument('--captures',type=pathlib.Path,help='Use published frozen capture choices; otherwise use CAPTURES.json already in cache')
 parser.add_argument('--prepare-only',action='store_true',help='Query public CDX and freeze nearest captures; do not acquire bodies')
 parser.add_argument('--initial-cache',type=pathlib.Path,action='append',default=[],help='Optional explicit cache directory; identical replay URLs only')
 args=parser.parse_args();P=args.cache;P.mkdir(parents=True,exist_ok=True)
 deadline=datetime.datetime.fromisoformat(args.deadline.replace('Z','+00:00'))
 if deadline.tzinfo is None:parser.error('--deadline requires a timezone')
 DEADLINE=deadline.timestamp();INITIAL_CACHES=args.initial_cache
 for name in ['html','receipts','attempts']:(P/name).mkdir(exist_ok=True)
 if args.prepare_only:
  prepare(args.inventory);raise SystemExit(0)
 if args.captures:
  src=args.captures.read_bytes();dst=P/'CAPTURES.json'
  if dst.exists() and dst.read_bytes()!=src:parser.error('cache already contains different frozen capture bytes')
  dst.write_bytes(src)
 if not (P/'CAPTURES.json').exists():parser.error('supply --captures or run --prepare-only first')
 CACHE=cached_sources()
 data=json.loads((P/'CAPTURES.json').read_text())
 inv=json.loads(args.inventory.read_text())
 if [(r['id'],r['title']) for r in data['records']] != [(f'{i:04d}',r['title']) for i,r in enumerate(inv['entries'])]:parser.error('capture universe differs from supplied inventory')
 if data['inventory_sha256']!=hashlib.sha256(args.inventory.read_bytes()).hexdigest():parser.error('inventory byte hash differs from frozen capture binding')
 write(P/'RUN.json',{'started_utc':utc(),'capture_sha256':hashlib.sha256((P/'CAPTURES.json').read_bytes()).hexdigest(),'max_workers':2,'minimum_global_start_interval_seconds':3,'retry_limit':2,'stop_deadline_utc':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat()})
 for r in data['records']:
  f=P/'receipts'/(r['id']+'.json')
  if not f.exists():write(f,{'id':r['id'],'title':r['title'],'status':r['status'],'selected':r['selected'],'requested_url':r['replay_url'],'attempts':[]})
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  pending={ex.submit(run,r) for r in data['records']};last=0
  while pending:
   done,pending=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:future.result()
   if time.monotonic()-last>=60:print(progress(),flush=True);last=time.monotonic()
 print(progress(),flush=True)
