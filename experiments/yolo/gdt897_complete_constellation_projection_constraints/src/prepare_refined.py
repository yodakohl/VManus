"""One fixed, independently reproduced Bernstein precision refinement."""
import collections
import concurrent.futures
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import prepare
ROOT=Path(__file__).resolve().parents[1]
def calculate(binary,boxes):
    text=str(len(boxes))+'\n'+'\n'.join(' '.join(map(str,b)) for b in boxes)+'\n'
    return subprocess.run([str(binary)],input=text.encode(),stdout=subprocess.PIPE,check=True,timeout=180).stdout
def parse(raw,n):
    rows=[tuple(map(int,line.split(','))) for line in raw.decode().splitlines()]
    assert [r[:4] for r in rows]==list(itertools.combinations(range(n),4))
    assert all(r[4] in (1,2,3,4,6,7) for r in rows)
    return {r[:4]:r[4] for r in rows}
def main():
    oldpath=ROOT/'artifacts/SEARCH_PACKET.json.gz';oldraw=oldpath.read_bytes();old=json.loads(gzip.decompress(oldraw))
    with tempfile.TemporaryDirectory(prefix='gdt897_bernstein_') as directory:
        binaries=[]
        for name in ('bernstein','bernstein_reference'):
            binary=Path(directory)/name
            subprocess.run(['g++','-std=c++17','-O3','-Wall','-Wextra','-Werror',str(ROOT/'src'/f'{name}.cpp'),'-o',str(binary)],check=True);binaries.append(binary)
        fixtures=[[(0,0,0,0),(2,0,2,0),(0,2,0,2),(1,1,1,1)],[(0,0,1,1),(5,0,6,1),(0,5,1,6),(5,5,6,6)],[(7990000,3700000,7990002,3700003),(7990100,3700000,7990103,3700004),(7990000,3700200,7990003,3700204),(7990050,3700050,7990053,3700054)]]
        for boxes in fixtures:
            a=calculate(binaries[0],boxes);b=calculate(binaries[1],boxes);assert a==b
        refined={};details={}
        for targetid in ('LEFT29','LEFT30'):
            boxes=old['targets'][targetid+':stereographic']['boxes'];n=len(boxes)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                outputs=list(pool.map(lambda binary:calculate(binary,boxes),binaries))
            assert outputs[0]==outputs[1],targetid
            masks=parse(outputs[0],n)
            original=next(c for c in old['cases'] if c['target_id']==targetid and c['mode']=='stereographic')['target_masks']
            combined={t:m&original[prepare.flat(t,n)] for t,m in masks.items()};assert all(combined.values())
            refined[targetid]=prepare.tensor(n,4,combined.__getitem__)
            details[targetid]={'canonical_tuples':len(masks),'mask_counts':dict(collections.Counter(combined.values())),'independent_csv_sha256':hashlib.sha256(outputs[0]).hexdigest()}
            print(targetid,details[targetid],flush=True)
    new={k:v for k,v in old.items() if k!='cases'};new['refinement_of_sha256']=hashlib.sha256(oldraw).hexdigest();new['refinement']='fixeddegree2Bernsteincontrols_no_subdivision'
    new['cases']=[dict(c,target_masks=refined[c['target_id']]) for c in old['cases'] if c['mode']=='stereographic']
    path=ROOT/'artifacts/BERNSTEIN_PACKET.json.gz';path.write_bytes(gzip.compress(json.dumps(new,separators=(',',':'),sort_keys=True).encode(),mtime=0))
    result={'schema':'GDT897_BERNSTEIN_VALIDATION_V1','status':'PASS','old_packet_sha256':hashlib.sha256(oldraw).hexdigest(),'refined_packet_sha256':prepare.sha(path),'unchanged':'allsourcevectors/sourcecases, exactboxes, source_signs, completeinventoryalternatives, bothprojectioncontracts; gnomonic results preserved','method':'exactBernsteincontrolrowdeterminant_signrange, independently identical completeCSV, intersectv1masks','kernels':{name:prepare.sha(ROOT/'src'/name) for name in ['bernstein.cpp','bernstein_reference.cpp']},'targets':details,'scope':'necessary-sign precision only; no continuousfit or meaning'}
    (ROOT/'artifacts/BERNSTEIN_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
