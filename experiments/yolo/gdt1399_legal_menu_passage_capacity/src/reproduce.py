"""Replay the retained source-free stop audit, without search/native inputs."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];REL=D.relative_to(ROOT)
lock=json.loads((D/'RETENTION_LOCK.json').read_text())
assert lock['kind']=='POST_BENCHMARK_RETENTION_NOT_PREREGISTRATION'
base=Path(tempfile.mkdtemp(prefix='vmanus1399-stop-'))/'repository';base.mkdir()
for name,digest in lock['files'].items():
    source=ROOT/name;assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,name
    target=base/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
subprocess.run([sys.executable,str(base/REL/'src/validate_stop.py')],cwd=base,check=True,stdout=subprocess.DEVNULL)
a=(base/REL/'artifacts/STOP_REVIEW.json').read_bytes();b=(D/'artifacts/STOP_REVIEW.json').read_bytes();assert a==b
print(json.dumps({'status':'STOP_AUDIT_REPLAY_PASS','native_payload_copied':False,'native_search_run':False,'original_benchmark_rerun':False,'stop_review_byte_exact':True},indent=2,sort_keys=True))
