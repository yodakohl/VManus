#!/usr/bin/env python3
import hashlib,json,subprocess,tempfile
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for name,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/name)==h,name
 a=E/'artifacts';source=ROOT/'experiments/yolo/gdt882_additive_line_lattice/artifacts/SELECTED_LINES.json'
 rows=json.loads(source.read_text());assert len(rows)==413
 assert rows[0]['locus']=='f19r.8'
 assert all(not r['page'].startswith('f84') for r in rows)
 expected='locus\tliteral\n'+''.join(r['locus']+'\t'+r['literal']+'\n' for r in rows)
 assert (a/'INPUT.tsv').read_text()==expected
 with tempfile.TemporaryDirectory(prefix='vmanus_three_state_verify_') as temp:
  binary=Path(temp)/'independent'
  subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(E/'src/independent.cpp'),'-o',str(binary)],check=True)
  subprocess.run([str(binary),str(a/'INPUT.tsv'),str(a/'INDEPENDENT_RESULT.json'),str(a/'INDEPENDENT_RANKS.bin')],check=True,timeout=1230)
 first=(a/'RANKS.bin').read_bytes();second=(a/'INDEPENDENT_RANKS.bin').read_bytes()
 assert len(first)==len(second)==1<<20
 assert 255 not in first and 255 not in second,'Incomplete enumeration is not validated exclusion'
 assert first==second,'Independent rank disagreement'
 result=dict(status='PASS',source_reconstructed=True,complete_mask_rank_comparisons=len(first),ranks_sha256=sha(a/'RANKS.bin'),independent_ranks_sha256=sha(a/'INDEPENDENT_RANKS.bin'),all_full_rank=set(first)=={20},even_leaves_queried=False)
 (a/'VALIDATION.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
