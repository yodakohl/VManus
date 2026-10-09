"""Two literal-bound compulsory fusion pretests; no meanings or key fit."""
import collections,csv,gzip,hashlib,itertools,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
ORDERS={'forward':['ch','k'],'reverse':['k','ch']}
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
ALLOW='experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'

def encode(word,pair):
 out=[];i=0
 while i<len(word):
  if word[i:i+2]==pair:out.append('ckh');i+=2
  else:out.append(word[i]);i+=1
 return out

def decode(word,pair):return [v for unit in word for v in (pair if unit=='ckh' else [unit])]

def main():
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 control=0
 for pair in ORDERS.values():
  for n in range(1,7):
   for word in itertools.product(['ch','k','y'],repeat=n):
    word=list(word);out=encode(word,pair);assert decode(out,pair)==word
    assert not any(out[j:j+2]==pair for j in range(len(out)-1));control+=1
 allowed={r['page'] for r in csv.DictReader((ROOT/ALLOW).open(),delimiter='\t')};assert len(allowed)==179
 source=json.loads(gzip.decompress((ROOT/SOURCE).read_bytes()));readers={};selected=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  hits=[r for r in source[ed] if r['ivtff_group_raw'] in ['chky','kchy']]
  for row in hits:
   assert row['page'] in allowed and row['page'] not in ['f1r','f116v'] and not row['page'].startswith('f84')
   assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   assert row['units']==(['ch','k','y'] if row['ivtff_group_raw']=='chky' else ['k','ch','y'])
  forms={}
  for form in ['chky','kchy']:
   hh=[r for r in hits if r['ivtff_group_raw']==form]
   forms[form]={'count':len(hh),'selectors':len({r['page'] for r in hh}),'physical_leaves':len({re.match(r'f\d+',r['page']).group() for r in hh}),'source_ids':[r['id'] for r in hh]}
  models={}
  for name,pair in ORDERS.items():
   failures=[r['id'] for r in hits if encode(decode(r['units'],pair),pair)!=r['units']]
   models[name]={'pair':pair,'noncanonical_ids':failures,'status':'EXCLUDED_BOUND_OBLIGATORY_ORDER' if failures else 'NO_COUNTERCASE_IN_FIXED_PACKET'}
  readers[ed]={'forms':forms,'models':models,'decision':'BOTH_BOUND_ORDERS_EXCLUDED' if all(m['noncanonical_ids'] for m in models.values()) else 'CAPACITY_QUALIFIED_OR_NOT_EXCLUDED'}
  selected.extend(hits)
 out={'status':'BOUND_MANDATORY_BENCH_FUSION_PRETEST','readers':readers,'source_free_roundtrips':control,'native_binding':'Stipulated literal ch/k and ckh shortcut; not independently established palaeography','source_meanings_assigned':0}
 (P/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');(P/'artifacts/WITNESSES.json').write_text(json.dumps(selected,indent=2)+'\n')
 print(json.dumps({'roundtrips':control,'readers':{ed:{'forms':{f:{k:v for k,v in a.items() if k!='source_ids'} for f,a in r['forms'].items()},'decision':r['decision']} for ed,r in readers.items()}},indent=2))
if __name__=='__main__':main()
