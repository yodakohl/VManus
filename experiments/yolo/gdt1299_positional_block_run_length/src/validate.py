"""Independent raw/source reconstruction and finite inequality check; no runner import."""
import gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def load(n):return json.loads((A/(n+'.json')).read_text())
def main():
 spec=json.loads((B/'src/SPEC.json').read_text());bounds=load('SOURCE_BOUNDS');targets=load('TARGET_WITNESSES');result=load('RESULT');checked=0
 for p,h in spec['input_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 src=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());raw=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
 for book,expected in bounds.items():
  parts=[];words=0
  for i,recipe in enumerate(src[book]):
   if i:parts.append('\n')
   for j,w in enumerate(recipe['words']):
    if j:parts.append(' ')
    parts.append(w);words+=1
  stream=''.join(parts);runs=list(re.finditer(r'(.)\1*',stream,flags=re.DOTALL));R=max(m.end()-m.start() for m in runs);wins=[m for m in runs if m.end()-m.start()==R]
  assert expected['R']==R and expected['characters']==len(stream) and expected['words']==words
  assert expected['minimum_alphabet_with_END']==len(set(stream))+1 and expected['stream_sha256']==hashlib.sha256(stream.encode()).hexdigest()
  assert expected['max_run_count']==len(wins) and expected['first_max_run_witnesses']==[{'character':m.group()[0],'length':R,'offset':m.start()} for m in wins[:8]]
 sign=re.compile(r'c[ktpf]h|ch|sh|[aoeindqysrlmktpf]')
 for ed,expected in targets.items():
  parsed=[]
  for r in raw[ed]:
   units=sign.findall(r['ivtff_group_raw']);assert ''.join(units)==r['ivtff_group_raw'] and units==r['units'];parsed.append((r,units));checked+=1
  maxlen=max(len(u) for _,u in parsed)
  for key,predicate in [('short_witnesses',lambda r,u:len(u)==1),('ol_witnesses',lambda r,u:r['ivtff_group_raw']=='ol'),('primary_witnesses',lambda r,u:r['ivtff_group_raw']==spec['native_primary_long_form'] and r['locus']==spec['native_primary_locus']),('max_witnesses',lambda r,u:len(u)==maxlen)]:
   wanted=[{'id':r['id'],'page':r['page'],'locus':r['locus'],'raw':r['ivtff_group_raw'],'units':u} for r,u in parsed if predicate(r,u)];assert wanted==expected[key]
  assert expected['max_L']==max(len(u) for _,u in parsed)
 configs=0
 for row in result['comparisons']:
  sb=bounds[row['book']];power=sb['R']+row['s'];T=22**(row['L']-1);n=row['minimum_base_necessary'];assert (n-1)**power<=T<n**power
  survivors=[]
  for N in range(max(22,sb['minimum_alphabet_with_END']),83):
   for k in range(1,power+1):
    configs+=1
    if N**k>T:survivors.append((N,k))
  status='UNSUPPORTED_SOURCE_ALPHABET' if sb['minimum_alphabet_with_END']>82 else 'NOT_EXCLUDED' if survivors else 'EXCLUDED';assert row['status']==status
  assert row['length_threshold']==str(T) and row['base82_capacity']==str(82**power)
 primary=[r for r in result['comparisons'] if r['short_tier']=='ONE_UNIT' and r['long_tier']=='FIXED11'];assert result['status']==('ALL_FIXED_SOURCES_PRIMARY_EXCLUDED' if all(r['status']=='EXCLUDED' for r in primary) else 'PRIMARY_NOT_UNIFORMLY_EXCLUDED')
 v={'status':'PASS','scope':'Independent regex source runs, literal target tokenization and all bounded N/k inequalities; no independent manuscript interpretation','source_books':len(bounds),'native_groups_reparsed':checked,'comparisons':len(result['comparisons']),'N_k_inequalities':configs}
 (A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
