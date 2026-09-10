#!/usr/bin/env python3
"""Pack every independent case receipt in deterministic case-ID order."""
import argparse,gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work-dir',type=Path,required=True);a=ap.parse_args()
    scope=json.loads((E/'artifacts/SCOPE.json').read_text());paths=sorted((a.work_dir/'cases').glob('*.json'))
    assert len(paths)==scope['cases'];seen=set();digest=hashlib.sha256();size=0
    out=E/'artifacts/INDEPENDENT_CASES.jsonl.gz';temporary=out.with_suffix('.tmp')
    with temporary.open('wb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:
            for p in paths:
                data=p.read_bytes();r=json.loads(data)
                assert r['case_id']==p.stem and r['status']=='COMPLETE' and p.stem not in seen
                seen.add(p.stem);assert data.endswith(b'\n') and data.count(b'\n')==1
                z.write(data);digest.update(data);size+=len(data)
    temporary.replace(out)
    x=dict(path='artifacts/INDEPENDENT_CASES.jsonl.gz',cases=len(seen),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),logical_bytes=size,logical_sha256=digest.hexdigest(),gzip_mtime=0)
    (E/'artifacts/INDEPENDENT_PACKING.json').write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
    summary_path=E/'artifacts/INDEPENDENT_COMPLETE_VALIDATION.json';summary=json.loads(summary_path.read_text())
    assert summary['status']=='PASS_COMPLETE' and summary['independently_complete_cases']==len(seen)
    summary['independent_cases_gzip_sha256']=x['sha256']
    summary['independent_cases_logical_sha256']=x['logical_sha256']
    primary=(E/'artifacts/CASES.json.gz').read_bytes()
    summary['primary_cases_gzip_sha256']=hashlib.sha256(primary).hexdigest()
    summary['primary_cases_logical_sha256']=hashlib.sha256(gzip.decompress(primary)).hexdigest()
    summary_path.write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');print(json.dumps(x))
if __name__=='__main__':main()
