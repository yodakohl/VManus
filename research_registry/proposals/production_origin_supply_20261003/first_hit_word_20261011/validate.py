from pathlib import Path
from fractions import Fraction as F
import hashlib,itertools,json
B=Path(__file__).resolve().parent

def main():
 for name,digest in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest
 r=json.loads((B/'RESULT.json').read_text());means=list(map(F,r['means_exact']));h=[F(0)]+means[1:]
 for d in range(1,27):assert 22*h[d]==22+sum(h[(d-step)%27] for step in range(1,23))
 assert 22*means[0]==22+sum(h[(-step)%27] for step in range(1,23)) and means[0]==27 and all(v>=22 for v in means)
 # Two-step access proves finite mean and uniqueness of this absorption solution.
 for state,target in itertools.product(range(27),repeat=2):
  direct=[v for v in range(1,23) if (state+v)%27==target];assert len(direct)<=1
  assert direct or any((state+x+y)%27==target for x,y in itertools.product(range(1,23),repeat=2))
 accepted=0;rejected=0
 def valid(w):
  last=sum(w)%27
  return all(sum(w[:i])%27!=last for i in range(1,len(w)))
 for n in range(1,4):
  for w in itertools.product(range(1,23),repeat=n):
   if valid(w):accepted+=1
   else:rejected+=1
 assert accepted==r['paths_length1to3_accepted'] and rejected==r['paths_length1to3_rejected']
 for c,w in r['constructive_targets'].items():assert valid(w) and sum(w)%27==int(c)
 alphabet=' abcdefghijklmnopqrstuvwxyz'
 for source in ['', 'a z','nimm wasser','  aa  ']:
  words=[r['constructive_targets'][str(alphabet.index(c))] for c in source];back=''.join(alphabet[sum(w)%27] for w in words);assert back==source
 assert not valid([1,5,22]) and valid([5,1,22]);assert r['means_decimal']==list(map(float,means)) and r['minimum_expected_length']==float(min(means)) and r['maximum_expected_length']==float(max(means));assert not r['native_data_used']
 out={'status':'PASS','exact_recurrences':27,'state_target_hazard_and_access_checks':729,'short_output_paths':accepted+rejected,'constructive_targets':27,'exact_source_messages':4,'scope':'Source-free exact recurrence/termination, prefix admissibility and readback; not native fit or historical proof.'};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
