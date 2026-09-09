#!/usr/bin/env python3
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
SOURCE=ROOT/'experiments/yolo/gdt882_additive_line_lattice/artifacts/SELECTED_LINES.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
def verify_lock():
 for name,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/name)==h,name
def input_text():
 rows=json.loads(SOURCE.read_text());assert len(rows)==413 and rows[0]['locus']=='f19r.8'
 assert all(not row['page'].startswith('f84') for row in rows)
 assert ''.join(sorted(set(''.join(row['literal'] for row in rows))))=='acdefghiklmnopqrstxy'
 return 'locus\tliteral\n'+''.join(row['locus']+'\t'+row['literal']+'\n' for row in rows)
def fixtures():
 permutations={tuple((e*x+b)%3 for x in range(3)) for e in [-1,1] for b in range(3)}
 assert len(permutations)==6 and all(len(set(p))==3 for p in permutations)
 cases=0
 for signs in itertools.product([-1,1],repeat=3):
  for b in itertools.product(range(3),repeat=3):
   for w in [(0,1,0,2),(2,2,1),(1,0,2,0,1),()]:
    c=[0,0,0];suffix=1
    for a in reversed(w):c[a]=(c[a]+suffix)%3;suffix=signs[a]*suffix
    for start in range(3):
     end=start
     for a in w:end=(signs[a]*end+b[a])%3
     assert end==(suffix*start+sum(x*y for x,y in zip(c,b)))%3
     cases+=1
 return cases

def main():
 verify_lock();fixture_cases=fixtures();a=E/'artifacts';a.mkdir(exist_ok=True)
 (a/'INPUT.tsv').write_text(input_text())
 with tempfile.TemporaryDirectory(prefix='vmanus_three_state_') as temp:
  binary=Path(temp)/'enumerate'
  subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(E/'src/enumerate.cpp'),'-o',str(binary)],check=True)
  subprocess.run([str(binary),str(a/'INPUT.tsv'),str(a/'NATIVE_RESULT.json'),str(a/'RANKS.bin')],check=True,timeout=1230)
 ranks=(a/'RANKS.bin').read_bytes();assert len(ranks)==1<<20
 native=json.loads((a/'NATIVE_RESULT.json').read_text())
 status='UNKNOWN_BUDGET' if 255 in ranks else ('NO_NONTRIVIAL_REVERSIBLE_THREE_STATE_MACHINE' if set(ranks)=={20} else 'RANK_DEFICIENT_REQUIRES_DIRECT_WITNESS')
 put(a/'RESULT.json',dict(status=status,source_sha256=sha(SOURCE),input_sha256=sha(a/'INPUT.tsv'),ranks_sha256=sha(a/'RANKS.bin'),native=native,fixture_cases=fixture_cases,even_leaves_queried=False))
 print(status)
if __name__=='__main__':main()
