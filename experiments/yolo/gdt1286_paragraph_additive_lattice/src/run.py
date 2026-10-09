import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
OLD=ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance'
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 p=ROOT/'experiments/yolo/gdt882_additive_line_lattice/src/algebra.py';spec=importlib.util.spec_from_file_location('old_source_free_algebra',p);alg=importlib.util.module_from_spec(spec);spec.loader.exec_module(alg)
 fixtures=alg.selftest()
 for rows,expected in [([[2,-1],[4,-1]],2),([[2,-1],[3,-1]],1)]:
  z=alg.analyze(rows,2);assert z['index']==expected;fixtures.append({'matrix':rows,'expected_index':expected,'lattice':z})
 source=json.loads((OLD/'artifacts/CENSUS.json').read_text());s=json.loads((OLD/'src/SPEC.json').read_text());prior=json.loads((OLD/'artifacts/RESULT.json').read_text());alphabet=s['working_signs'];assert len(alphabet)==len(set(alphabet))==22
 matrices={};lattices={};summary={}
 for reader,expected in [('ZL3b',180),('IT2a',379)]:
  recs=source[reader];assert len(recs)==expected==prior['readers'][reader]['paragraphs'];assert len({r['id'] for r in recs})==expected
  for r in recs:
   assert not r['page'].startswith('f84') and r['page']!='f116v'
   assert len(r['counts'])==22 and all(type(n)==int and n>=0 for n in r['counts'])
  assert all(any(r['counts'][j] for r in recs) for j in range(22))
  rows=[r['counts']+[-1] for r in recs];matrices[reader]={'columns':alphabet+['COMMON_TOTAL_NEGATIVE'],'records':recs,'matrix':rows}
  z=alg.analyze(rows,23);lattices[reader]=z
  summary[reader]={'population_paragraphs':len(rows),'pages':len({r['page'] for r in recs}),'rank':z['rank'],'dimension':23,'index':z['index'],'processed_rows':z['rows_processed'],'certificate_rows':len(z['used_indices']),'certificate_ids':[recs[i]['id'] for i in z['used_indices']],'status':'ADDITIVE_PARAGRAPH_INVARIANT_EXCLUDED' if z['unit_lattice'] else 'NONTRIVIAL_QUOTIENT_CAPACITY'}
 status='BOTH_READERS_ALL_ABELIAN_PARAGRAPH_INVARIANTS_EXCLUDED' if all(v['index']==1 for v in summary.values()) else 'NONTRIVIAL_QUOTIENT_OR_MIXED'
 save('MATRICES',matrices);save('CERTIFICATES',lattices);save('FIXTURES',fixtures);save('RESULT',{'status':status,'readers':summary,'ceiling':'Fixed22working-unit additive common total on1259complete marked paragraphs; no general state, syntax, meaning or historical claim.'})
 print(json.dumps({'status':status,'readers':{r:{k:v for k,v in x.items() if k!='certificate_ids'} for r,x in summary.items()}},indent=2))
if __name__=='__main__':main()
