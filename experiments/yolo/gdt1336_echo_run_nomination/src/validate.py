from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split(),key=lambda x:(-len(x),x));PAT=re.compile('|'.join(A))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def independent(u):
 if len(u)<4 or u[-2:]!=['d','y']:return None
 blocks=[]
 for x,g in itertools.groupby(u[:-2]):
  n=len(list(g));blocks.extend([(x,n)] if x in ('e','i') else [(x,1)]*n)
 h=len(blocks)//2
 if len(blocks)%2 or not h or any(blocks[j][0]!=blocks[h+j][0] for j in range(h)):return None
 pairs=[{'slot':j,'unit':blocks[j][0],'left':blocks[j][1],'right':blocks[h+j][1]} for j in range(1,h-1) if blocks[j][0] in ('e','i')]
 return {'skeleton':[x for x,n in blocks[:h]],'collapsed_run_lengths':[n for x,n in blocks],'inner_pairs':pairs,'eligible':bool(pairs),'mismatch':any(p['left']!=p['right'] for p in pairs)}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/CANDIDATES.json');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;candidates=0;eligible_count=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();expected=[]
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';u=PAT.findall(g[2]);assert u==r['units'];joins+=1
     x=independent(u)
     if x is not None:expected.append(dict(r,**x))
  assert seen==set(byid);expected.sort(key=lambda r:(r['ivtff_group_raw'],r['id']));assert expected==saved[ed];ev=[x for x in expected if x['eligible']];forms=sorted({x['ivtff_group_raw'] for x in ev});candidates+=len(expected);eligible_count+=len(ev)
  assert result['readers'][ed]=={'groups':len(rows),'collapsed_echo_candidates':len(expected),'candidate_types':len({x['ivtff_group_raw'] for x in expected}),'eligible_occurrences':len(ev),'eligible_types':len(forms),'mismatching_occurrences':sum(x['mismatch'] for x in ev),'manual_first_forms':forms[:8],'status':'WITNESSES_ONLY' if ev else 'NO_HOMOLOGOUS_INNER_RUN_OPPORTUNITY'}
 assert result['status']==('NO_HOMOLOGOUS_INNER_RUN_OPPORTUNITY' if not eligible_count else 'READER_SPECIFIC_WITNESSES_ONLY')
 # Independent constructive cases: vary both inner runs without conditioning on equality.
 checks=0
 for a,b in itertools.product(range(1,5),repeat=2):
  u=['a']+['e']*a+['l','a']+['e']*b+['l','d','y'];x=independent(u);assert x['eligible'] and x['mismatch']==(a!=b);assert x['inner_pairs']==[{'slot':1,'unit':'e','left':a,'right':b}];checks+=1
 assert not independent(['ch','e','ch','e','e','d','y'])['eligible']
 out={'status':'PASS','source_joins':joins,'nominated_occurrences_across_alternate_readings':candidates,'eligible_occurrences':eligible_count,'constructive_fixtures':checks,'method':'Independent original source traversal and groupby extraction; all nominations and reader summaries reproduced; no runner imported.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
