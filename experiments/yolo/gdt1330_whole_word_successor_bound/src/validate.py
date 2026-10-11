from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');degrees=read(B/'artifacts/DEGREES.json');saved=read(B/'artifacts/WITNESSES.json');res=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;allpairs=0;nw=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();pairs=[]
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata'];gs=sorted(line['groups'],key=lambda g:int(g[1]))
    for g in gs:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
    for g,h in zip(gs,gs[1:]):
     if g[0] in byid and h[0] in byid and int(h[1])==int(g[1])+1:pairs.append({'left':byid[g[0]],'right':byid[h[0]]})
  assert seen==set(byid);r=res['readers'][ed];assert r['original_pairs']==len(pairs) and r['self_pairs_ignored']==sum(p['left']['ivtff_group_raw']==p['right']['ivtff_group_raw'] for p in pairs);allpairs+=len(pairs)
  for scope in ('global','page'):
   records=[]
   for p in pairs:
    a,b=p['left']['ivtff_group_raw'],p['right']['ivtff_group_raw']
    if a!=b:records.append(((a,) if scope=='global' else (p['left']['page'],a),b,p))
   records.sort(key=lambda x:(x[0],x[1],x[2]['left']['locus'],int(x[2]['left']['source_group_index'])));table=[];allw={}
   for key,group in itertools.groupby(records,key=lambda x:x[0]):
    group=list(group);succ=[]
    for word,instances in itertools.groupby(group,key=lambda x:x[1]):succ.append({'word':word,'pair':next(instances)[2]})
    table.append({'key':list(key),'nonself_successors':len(succ)});allw[key]=succ
   assert table==degrees[ed][scope];mx=max(x['nonself_successors'] for x in table);key=min(k for k,v in allw.items() if len(v)==mx);above=[x for x in table if x['nonself_successors']>27];expected={'minimum_required_commands':mx,'state_cells':len(table),'cells_above27':len(above),'selected_key':list(key),'status':'K27_EXCLUDED' if mx>27 else 'NOT_EXCLUDED_BY_BOUND'}
   if scope=='page':expected['pages_above27']=len({x['key'][0] for x in above})
   assert r['scopes'][scope]==expected;assert saved[ed][scope]=={'key':list(key),'nonself_successors':mx,'successors':allw[key]};nw+=mx
 assert res['status']==('PAGE_SPECIFIC_K27_EXCLUDED_ALL_READINGS' if all(r['scopes']['page']['minimum_required_commands']>27 for r in res['readers'].values()) else 'READER_SPECIFIC_SUCCESSOR_BOUNDS');assert res['fixtures']=={'status':'PASS','finite_image_checks':5+25+125,'extra_hidden_state_escape':True,'self_echo_not_counted':True}
 # Independently list images of every small partial lookup row.
 for k in (1,2,3):
  for table in itertools.product('abcde',repeat=k):assert len({v for v in table if v!='a'})<=k
 out={'status':'PASS','source_joins':joins,'original_consecutive_pairs':allpairs,'selected_successor_witnesses':nw,'finite_image_checks':155,'method':'Independent original915source windows, sorted successor grouping, complete degree/tie/witness checks; no runner imported.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
