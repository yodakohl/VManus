from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/WITNESSES.json');tables=read(B/'artifacts/PAGES.json');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;npairs=0;excluded=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();forms=collections.defaultdict(set);edges=collections.defaultdict(lambda:collections.defaultdict(list));pairs=0
  for phase in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata'];gs=sorted(line['groups'],key=lambda g:int(g[1]))
    for g in gs:
     if g[0] not in byid:continue
     row=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==row['kind']=='P' and m['page']==row['page'] and m['locus']==row['locus'];assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert g[2]==row['ivtff_group_raw']==''.join(row['units']);assert int(g[1])==int(row['source_group_index']) and g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';forms[m['page']].add(g[2]);joins+=1
    for g,h in zip(gs,gs[1:]):
     if g[0] not in byid or h[0] not in byid or int(h[1])!=int(g[1])+1:continue
     pairs+=1
     if g[2]!=h[2]:edges[m['page']][(g[2],h[2])].append({'left':byid[g[0]],'right':byid[h[0]]})
  assert seen==set(byid);expected=[];qual=[]
  for page in sorted(forms):
   e=edges[page];rec=sorted(k for k in e if k[0]<k[1] and k[::-1] in e);q=len(forms[page])>54 and len(rec)>0
   expected.append({'page':page,'distinct_forms':len(forms[page]),'reciprocal_pairs':len(rec),'qualifies':q})
   if q:qual.append((page,rec[0]))
  assert expected==tables[ed]
  if qual:
   excluded+=1;page,pair=qual[0];w=saved[ed];assert w['page']==page and w['pair']==list(pair) and w['forms']==sorted(forms[page]) and w['distinct_forms']==len(forms[page]);assert len(w['forms'])>54
   for name,key in [('forward',pair),('reverse',pair[::-1])]:assert w[name]==min(edges[page][key],key=lambda p:(p['left']['locus'],int(p['left']['source_group_index'])))
  assert result['readers'][ed]=={'status':'FORWARD_WHEEL_EXCLUDED' if qual else 'NOT_EXCLUDED_BY_THIS_TEST','qualifying_pages':len(qual),'selected_page':qual[0][0] if qual else None,'groups':len(rows),'original_pairs':pairs};npairs+=pairs
 # Independent exhaustive actual index walks, including threshold counterexample.
 cases=0;indexchecks=0
 for s in range(1,7):
  for m in range(s+1,4*s+3):
   found=False
   for a,b in itertools.permutations(range(m),2):
    forward=any((a+d)%m==b for d in range(1,s+1));reverse=any((b+d)%m==a for d in range(1,s+1));indexchecks+=1
    if forward and reverse:found=True;assert m<=2*s
   assert found==(m<=2*s);cases+=1
  assert (0+s)%(2*s)==s and (s+s)%(2*s)==0
 assert result['fixtures']=={'status':'PASS','roundtrips':(1+27+27**2)*3,'small_ring_cases':cases}
 assert result['status']==('FORWARD_WORD_WHEEL_EXCLUDED_ALL_READINGS' if excluded==3 else 'READER_SPECIFIC_NECESSARY_BOUND')
 out={'status':'PASS','source_joins':joins,'original_consecutive_pairs':npairs,'small_ring_cases':cases,'independent_index_pair_checks':indexchecks,'method':'Independent guarded original-source windows and exhaustive directed ring reachability; runner not imported. Roundtrip count checked, source inverse also follows directly from unique bank positions and nonzero distinct steps.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
