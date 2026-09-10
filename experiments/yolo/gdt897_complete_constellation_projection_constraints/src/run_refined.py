"""Apply the unchanged finite searches once to the refined stereo packet."""
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import run
import independent_search
ROOT=Path(__file__).resolve().parents[1]
def main():
    independent=sys.argv[1:]==['--independent']
    path=ROOT/'artifacts/BERNSTEIN_PACKET.json.gz';raw=path.read_bytes();packet=json.loads(gzip.decompress(raw))
    validation=json.loads((ROOT/'artifacts/BERNSTEIN_VALIDATION.json').read_text())
    assert validation['status']=='PASS' and validation['refined_packet_sha256']==hashlib.sha256(raw).hexdigest()
    results=[]
    with tempfile.TemporaryDirectory(prefix='gdt897_refined_') as directory:
        binary=None if independent else run.compile_solver(directory)
        factory=concurrent.futures.ProcessPoolExecutor if independent else concurrent.futures.ThreadPoolExecutor
        with factory(max_workers=5) as pool:
            futures=[pool.submit(independent_search.solve_case,c) if independent else pool.submit(run.solve_case,c,binary) for c in packet['cases']]
            for future in concurrent.futures.as_completed(futures):
                r=future.result();results.append(r);print(r['case_id'],r.get('status',[o['status'] for o in r['orientations']]),flush=True)
    out={'schema':'GDT897_REFINED_SEARCH_V1','implementation':'independent' if independent else 'primary','packet_sha256':hashlib.sha256(raw).hexdigest(),'seconds_per_case_orientation':120,'cases':sorted(results,key=lambda r:r['case_id']),'claim_ceiling':'necessaryinvariants only; timeoutunknown, compatibilitynotcontinuousmap'}
    (ROOT/'artifacts'/('REFINED_INDEPENDENT_RESULT.json' if independent else 'REFINED_RESULT.json')).write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
