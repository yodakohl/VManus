"""Source-free scope demonstration; no native state fit or new corpus selection."""
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
EXP=ROOT/'experiments/yolo/gdt1286_paragraph_additive_lattice'
def product(C,A):
 return [[sum(row[k]*A[k][j] for k in range(len(A))) for j in range(len(A[0]))] for row in C]
def trace(word,maps,start):
 path=[start]
 for s in word:path.append(maps[s][path[-1]])
 return path
def main():
 manifest=json.loads((EXP/'experiment.json').read_text()); hashes={x['path']:x['sha256'] for x in manifest['outputs']}
 files=['artifacts/MATRICES.json','artifacts/CERTIFICATES.json','artifacts/RESULT.json','artifacts/VALIDATION.json']
 receipts={}
 for name in files:
  p=EXP/name;rel=str(p.relative_to(ROOT));h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==hashes[rel];receipts[rel]=h
 matrices=json.loads((EXP/'artifacts/MATRICES.json').read_text());certs=json.loads((EXP/'artifacts/CERTIFICATES.json').read_text())
 for reader,z in certs.items():
  A=matrices[reader]['matrix'];assert len(A[0])==23 and z['unit_lattice'] and z['index']==1
  for j,c in enumerate(z['coefficients']):assert [sum(v*A[int(i)][k] for i,v in c.items()) for k in range(23)]==[int(j==k) for k in range(23)]
 words=['AA','B','BB','ABABA'];maps={'A':[1,0,2],'B':[0,2,1]}
 A=[[w.count('A'),w.count('B'),-1] for w in words];C=[[-1,2,-2,1],[0,-1,1,0],[0,-2,1,0]]
 assert product(C,A)==[[1,0,0],[0,1,0],[0,0,1]]
 traces={w:trace(w,maps,0) for w in words};assert all(t[-1]==0 for t in traces.values())
 actions={w:[trace(w,maps,s)[-1] for s in range(3)] for w in words}
 assert len({tuple(v) for v in actions.values()})>1
 assert trace('AB',maps,0)[-1]!=trace('BA',maps,0)[-1]
 assert set(x for t in traces.values() for x in t)=={0,1,2}
 # Exhaustively check only this abstract two-letter toy on two states.
 cases=[]
 for a,b,start in itertools.product([[0,1],[1,0]],[[0,1],[1,0]],[0,1]):
  m={'A':a,'B':b};ts=[trace(w,m,start) for w in words];common=len({t[-1] for t in ts})==1
  nontrivial=any(m[s][start]!=start for s in m)
  assert not (common and nontrivial)
  cases.append({'A':a,'B':b,'start':start,'common_endpoint':common,'nontrivial_orbit':nontrivial})
 out={'status':'PASS_SOURCE_FREE_SCOPE_DEMONSTRATION','inherited_identity_receipts':receipts,'two_state_corollary':'Every permutation of two states is identity or swap; fixed symbol maps therefore give a C2 additive counter. GDT1286forces every swap bit zero under its same paragraph assumptions.','toy_symbols_are_not_native_values':True,'toy_words':words,'three_state_maps':maps,'traces_from_zero':traces,'complete_actions':actions,'noncommuting_AB_BA_endpoints':[trace(w,maps,0)[-1] for w in ['AB','BA']],'augmented_toy_counts':A,'integer_left_inverse':C,'toy_two_state_cases':cases,'limits':['No native3state search or fit','Not a full information-preserving encoder','No glyph/word meanings','Actual paragraph flags and22working-unit assumptions inherited','Noninvertible maps are not excluded by the two-state corollary','GDT885physical-line3state failure and903large-line witness remain unchanged']}
 (OUT/'PARAGRAPH_STATE_SCOPE_RESULT_20261009.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'traces':traces,'complete_actions':actions,'AB_BA':out['noncommuting_AB_BA_endpoints']}))
if __name__=='__main__':main()
