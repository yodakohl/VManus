"""Bounded full-bijection search; compile once and run independent cases."""
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def compile_solver(directory):
    path=Path(directory)/'search'
    subprocess.run(['g++','-std=c++17','-O3','-Wall','-Wextra',str(ROOT/'src/search.cpp'),'-o',str(path)],check=True)
    return path
def solve_case(case,binary,seconds=120):
    data=struct.pack('<II',case['n'],3 if case['mode']=='gnomonic' else 4)+bytes(case['source_masks'])+bytes(case['target_masks'])
    try:
        p=subprocess.run([str(binary),str(seconds)],input=data,stdout=subprocess.PIPE,check=True,timeout=seconds*2+60)
    except subprocess.TimeoutExpired:
        return {'case_id':case['case_id'],'orientations':[{'g':g,'status':'UNKNOWN_PROCESS_TIMEOUT','witness':[]} for g in (1,-1)]}
    result=json.loads(p.stdout);result['case_id']=case['case_id'];return result
def main():
    packet_path=ROOT/'artifacts/SEARCH_PACKET.json.gz'
    packet=json.loads(gzip.decompress(packet_path.read_bytes()))
    with tempfile.TemporaryDirectory(prefix='gdt897_search_') as directory:
        binary=compile_solver(directory)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures=[pool.submit(solve_case,c,binary) for c in packet['cases']]
            results=[]
            for future in concurrent.futures.as_completed(futures):
                r=future.result();results.append(r);print(r['case_id'],[x['status'] for x in r['orientations']],flush=True)
    out={'schema':'GDT897_PRIMARY_RESULT_V1','packet_sha256':hashlib.sha256(packet_path.read_bytes()).hexdigest(),'seconds_per_orientation':120,'cases':sorted(results,key=lambda r:r['case_id']),'cardinality':packet['cardinality'],'claim_ceiling':'Necessary invariant search only; no continuous map proof, celestial identification or meaning.'}
    (ROOT/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
