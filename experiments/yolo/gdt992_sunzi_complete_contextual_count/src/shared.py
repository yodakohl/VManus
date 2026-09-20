import concurrent.futures,datetime,gzip,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
TARGET='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
OLD=E.parent/'gdt987_anastasia_finite_word_proof/src'
LIMITS=dict(primary_seconds=3,primary_nodes=200000,primary_external_seconds=8,
            reverse_seconds=20,reverse_nodes=1000000,reverse_external_seconds=8,shared_seconds=900,workers=24)
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def read(p):
    data=p.read_bytes();return json.loads(gzip.decompress(data) if p.name.endswith('.gz') else data)
def put(name,value):
    data=(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    (A/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def verify_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
def isolated(script,job,deadline,limit):
    remaining=deadline-time.time()
    if remaining<=0:return dict(status='UNKNOWN_QUEUE_LIMIT')
    try:
        p=subprocess.run([sys.executable,str(script),'--worker'],input=json.dumps(job),text=True,capture_output=True,timeout=min(limit,remaining))
        if p.returncode:return dict(status='ERROR_WORKER',returncode=p.returncode)
        return json.loads(p.stdout)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_SHARED_LIMIT' if remaining<limit else 'UNKNOWN_PROCESS_LIMIT')
    except Exception as exc:return dict(status='ERROR_PROTOCOL',error_type=type(exc).__name__)
def work(script,jobs,deadline,limit,journal):
    with (A/journal).open('x') as handle:
        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
            futures={pool.submit(isolated,script,job,deadline,limit):i for i,job in jobs}
            for done,future in enumerate(concurrent.futures.as_completed(futures),1):
                i=futures[future];out=future.result();handle.write(json.dumps(dict(case=i,outcome=out),separators=(',',':'))+'\n');handle.flush()
                if done%64==0 or done==len(jobs):print(json.dumps(dict(completed=done,of=len(jobs),latest=out['status'])),flush=True)
def journal(name):
    path=A/name
    rows=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    d={r['case']:r['outcome'] for r in rows};assert len(d)==len(rows);return d
