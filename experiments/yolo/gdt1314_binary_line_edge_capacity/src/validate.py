import collections,csv,gzip,hashlib,json,re,struct
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def split(raw):
 ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
 for pos in range(len(raw)):
  for s in SIGNS:
   if raw[pos:pos+len(s)]==s:
    ways[pos+len(s)].extend(p+(s,) for p in ways[pos])
    ways[pos+len(s)]=ways[pos+len(s)][:2]
 return ways[-1]
def code(units,key):
 value=0
 for u in units:value=2*value+int(u in key)
 return len(units),value
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};strict=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));edges=json.loads(gzip.decompress((B/'artifacts/EDGES.json.gz').read_bytes()));out=json.loads((B/'artifacts/RESULT.json').read_text());joined=0;checked=0;edge_total=0
 assert split('ch')==[('ch',)] and not split('!') and code(['a'],{'m'})!=code(['a','a'],{'m'})
 for ed,r in out['readers'].items():
  records={};selected={};f=collections.Counter()
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json').read_text())
   for line in d['lines']:
    m=line['metadata'];assert m['page'] in allow and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v')
    all_indices=sorted(int(g[1]) for g in line['groups'])
    for ident,i,raw,lft,rgt in line['groups']:
     assert ident not in records;records[ident]=(m,i,raw,lft,rgt);f['cached_groups']+=1
     if m['kind']!='P':f['non_prose']+=1;continue
     edge=(lft=='LINE_START' and rgt in ('DEFINITE_SPACE','LINE_END')) or (lft=='DEFINITE_SPACE' and rgt=='LINE_END')
     if not edge:f['not_fixed_edge_pair']+=1;continue
     if lft=='LINE_START':assert int(i)==all_indices[0]
     if rgt=='LINE_END':assert int(i)==all_indices[-1]
     if not re.fullmatch('[a-z]+',raw):f['edge_nonliteral']+=1;continue
     parses=split(raw)
     if len(parses)!=1:f['edge_nonunique_parse']+=1;continue
     f['eligible_edge']+=1;selected[ident]=parses[0]
  assert dict(f)==r['filter_counts'];assert set(selected)=={x['id'] for x in edges[ed]};assert len(selected)==len(edges[ed])==r['edge_groups']
  for row in strict[ed]+edges[ed]:
   m,i,raw,lft,rgt=records[row['id']];assert row['page']==m['page'] and row['locus']==m['locus'] and int(row['source_group_index'])==int(i) and row['ivtff_group_raw']==raw and row['left_separator']==lft and row['right_separator']==rgt;assert split(raw)==[tuple(row['units'])]
   if row['id'] not in selected:assert lft==rgt=='DEFINITE_SPACE' and m['kind']=='P';joined+=1
  assert len(strict[ed])==r['strict_groups'];assert r['edge_types']==len({x['ivtff_group_raw'] for x in edges[ed]});assert r['max_units']==max(len(x['units']) for x in strict[ed]+edges[ed]);edge_total+=len(selected)
  buf=gzip.decompress((R/f'experiments/yolo/gdt1312_binary_whole_code_capacity/artifacts/COUNTS_{ed}.u16.gz').read_bytes());allcounts=[t[0] for t in struct.iter_unpack('<H',buf)];keys=[i*2 for i,k in enumerate(allcounts) if i and k<=32];assert keys==[k['mask'] for k in r['keys']]
  for k in r['keys']:
   key={s for j,s in enumerate(SIGNS) if k['mask']&(1<<j)};assert sorted(key)==sorted(k['class1'])
   old=collections.Counter(code(x['units'],key) for x in strict[ed]);new=collections.Counter(code(x['units'],key) for x in edges[ed]);union=set(old)|set(new)
   assert len(old)==allcounts[k['mask']//2]==k['strict_K'];assert len(new)==k['edge_K'];assert len(union)==k['union_K'];assert k['fits32']==(len(union)<=32)
   conv=lambda s:(len(s),int(s,2))
   assert set(map(conv,k['codes']))==union;assert set(map(conv,k['new_codes']))==set(new)-set(old)
   for s,values in k['codes'].items():
    pair=conv(s);assert values['strict_occurrences']==old[pair] and values['edge_occurrences']==new[pair];w=values['witness'];assert w in (edges[ed] if pair not in old else strict[ed]);assert code(w['units'],key)==pair
   checked+=1
  assert r['surviving_masks']==[k['mask'] for k in r['keys'] if k['union_K']<=32]
  assert r['status']==('CAPACITY_RETAINS' if r['surviving_masks'] else 'ALL_FIXED_KEYS_EXCLUDED')
 assert out['status']==('ALL_READINGS_EXCLUDED' if all(not r['surviving_masks'] for r in out['readers'].values()) else 'READER_SPECIFIC_EDGE_CAPACITY')
 result={'status':'PASS','strict_source_joins':joined,'independently_selected_edge_groups':edge_total,'key_cases':checked,'method':'Independent iterative parse and length/integer projections; complete source joins and per-code counts/witness checks. Not palaeographic validation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
