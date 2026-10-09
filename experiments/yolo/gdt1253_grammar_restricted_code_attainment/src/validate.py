import hashlib,itertools,json
from functools import lru_cache
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def alternatives(word):
 @lru_cache(None)
 def walk(pos,previous):
  if pos==len(word):return ('',)
  out=[]
  for meaning,code in [('A','0'),('C','1'),('B','01')]:
   if previous=='A' and meaning=='C':continue
   if word.startswith(code,pos):out.extend(meaning+tail for tail in walk(pos+len(code),meaning))
  return tuple(out)
 return walk(0,'')
def main():
 s=json.loads((B/'src/SPEC.json').read_text());assert hashlib.sha256((ROOT/s['predecessor']).read_bytes()).hexdigest()==s['predecessor_sha256']
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 rows=json.loads((A/'OUTPUT_FIXTURES.json').read_text());expected={''.join(x) for n in range(1,9) for x in itertools.product('01',repeat=n)}
 assert {r['output'] for r in rows}==expected and len(rows)==len(expected)==510
 for r in rows:assert alternatives(r['output'])==(r['source'],)
 source_rows=json.loads((A/'SOURCE_FIXTURES.json').read_text());allowed={''.join(x) for n in range(1,7) for x in itertools.product('ABC',repeat=n) if 'AC' not in ''.join(x)}
 assert {r['source'] for r in source_rows}==allowed and len(source_rows)==len(allowed)
 code=s['code']
 for r in source_rows:
  assert ''.join(code[x] for x in r['source'])==r['output']
  assert alternatives(r['output'])==(r['source'],)
 r=json.loads((A/'RESULT.json').read_text());assert r['finite_output_words']==510 and r['finite_legal_source_words']==len(allowed)
 assert r['finite_illegal_source_words_rejected']==sum(3**n for n in range(1,7))-len(allowed)
 assert code['B']==code['A']+code['C'] and alternatives('01')==('B',)
 result={'status':'PASS','method':'Separate exhaustive parse dynamic program and source-language enumeration, without importing runner. Same author; finite software check, not manuscript evidence or substitute for all-length proof.','output_words':510,'legal_source_words':len(allowed)}
 (A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
