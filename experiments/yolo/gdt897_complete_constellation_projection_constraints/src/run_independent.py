"""Parallel orchestration of unchanged independent per-case finite searches."""
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import independent_search
ROOT=Path(__file__).resolve().parents[1]
def main():
    path=ROOT/'artifacts/SEARCH_PACKET.json.gz';raw=path.read_bytes();packet=json.loads(gzip.decompress(raw))
    assert packet['schema']=='GDT897_SEARCH_PACKET_V1'
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as pool:
        futures=[pool.submit(independent_search.solve_case,c) for c in packet['cases']]
        results=[]
        for future in concurrent.futures.as_completed(futures):
            r=future.result();results.append(r);print(r['case_id'],r['status'],flush=True)
    out={'schema':'GDT897_INDEPENDENT_SEARCH_V1','packet_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'src/independent_search.py').read_bytes()).hexdigest(),'seconds_per_case_orientation':120,'cases':sorted(results,key=lambda r:r['case_id'])}
    (ROOT/'artifacts/INDEPENDENT_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
