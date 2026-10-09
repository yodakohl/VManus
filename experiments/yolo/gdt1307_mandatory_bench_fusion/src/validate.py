"""Separate source/forbidden-pair and canonicalization checks."""
import csv,gzip,hashlib,itertools,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]

def forward(seq,pair):
 # Mark all disjoint source intervals before replacing any of them.
 starts=[];i=0
 while i+1<len(seq):
  if tuple(seq[i:i+2])==pair:starts.append(i);i+=2
  else:i+=1
 out=list(seq)
 for i in reversed(starts):out[i:i+2]=['ckh']
 return out

def main():
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
 r=json.loads((P/'artifacts/RESULT.json').read_text());w=json.loads((P/'artifacts/WITNESSES.json').read_text());source=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));allowed={x['page'] for x in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 pat=re.compile(r'cfh|cph|cth|ckh|ch|sh|[aoeindqysrlmktpf]');expected=[];checks=0
 for ed in ['ZL3b','IT2a','RF1b']:
  hh=[x for x in source[ed] if x['ivtff_group_raw']=='chky' or x['ivtff_group_raw']=='kchy'];expected+=hh
  for x in hh:
   units=pat.findall(x['ivtff_group_raw']);assert ''.join(units)==x['ivtff_group_raw'] and units==x['units']
   assert x['page'] in allowed and not x['page'].startswith('f84') and x['page'] not in {'f1r','f116v'}
   assert x['kind']=='P' and x['left_separator']==x['right_separator']=='DEFINITE_SPACE'
  for form,record in r['readers'][ed]['forms'].items():
   hits=[x for x in hh if x['ivtff_group_raw']==form]
   assert record=={'count':len(hits),'selectors':len(set(x['page'] for x in hits)),'physical_leaves':len(set(re.match(r'f\d+',x['page'])[0] for x in hits)),'source_ids':[x['id'] for x in hits]}
  excluded=[]
  for name,pair in [('forward',('ch','k')),('reverse',('k','ch'))]:
   bad=[]
   for x in hh:
    u=x['units'];forbidden=any(tuple(u[i:i+2])==pair for i in range(len(u)-1))
    decoded=[]
    for token in u:decoded.extend(pair if token=='ckh' else [token])
    rewritten=forward(decoded,pair)
    assert forbidden==(rewritten!=u)
    if forbidden:bad.append(x['id']);assert rewritten==['ckh','y']
    checks+=1
   model=r['readers'][ed]['models'][name];assert model['pair']==list(pair) and model['noncanonical_ids']==bad
   assert model['status']==('EXCLUDED_BOUND_OBLIGATORY_ORDER' if bad else 'NO_COUNTERCASE_IN_FIXED_PACKET');excluded.append(bool(bad))
  assert r['readers'][ed]['decision']==('BOTH_BOUND_ORDERS_EXCLUDED' if all(excluded) else 'CAPACITY_QUALIFIED_OR_NOT_EXCLUDED')
 assert expected==w
 count=0
 for pair in [('ch','k'),('k','ch')]:
  for n in range(1,7):
   for sourceword in itertools.product(['ch','k','y'],repeat=n):
    encoded=forward(sourceword,pair);back=[]
    for u in encoded:back.extend(pair if u=='ckh' else [u])
    assert tuple(back)==sourceword
    assert all(tuple(encoded[i:i+2])!=pair for i in range(len(encoded)-1));count+=1
 assert count==r['source_free_roundtrips']==2184 and r['source_meanings_assigned']==0
 v={'status':'PASS','exact_reader_occurrences':len(w),'orientation_source_checks':checks,'source_free_roundtrips':count,'scope':'Conditional literal-binding pretest/source fidelity only; no new independent image, word meaning or general ligature exclusion.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
