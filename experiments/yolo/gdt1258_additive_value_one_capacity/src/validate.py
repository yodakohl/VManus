import csv,hashlib,io,itertools,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
s=json.loads((B/'src/SPEC.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());single=json.loads((B/'artifacts/SINGLETONS.json').read_text())
for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
source=json.loads((R/s['source']).read_text());flat=[]
for section in source['source_sections']:
 for word in section['words']:flat.extend(list(word))
N=len(flat);K=sum(c==s['value_one_source_letter'] for c in flat)
assert N==result['source_letters']==24668 and K==result['value_one_letters']
assert result['source_letter_counts']=={c:flat.count(c) for c in sorted(set(flat))}
assert result['source_value_one_fraction']==K/N
allowed=json.loads((R/s['scope_spec']).read_text())['allowed'];cmd=['./vmanus-exp','query-tsv',s['native_source'],'--selector','page']
for p in allowed:cmd+=['--allow',p]
cmd+=['--columns',','.join(s['columns'])];c=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True)
receipt=json.loads((B/'artifacts/GUARD_RECEIPT.json').read_text());assert cmd==receipt['command'] and hashlib.sha256(c.stdout.encode()).hexdigest()==receipt['output_sha256']
units=set(s['working_signs'])
def counts(word):
    ways=[set() for _ in range(len(word)+1)];ways[0].add(0)
    for j in range(len(word)):
        for u in units:
            if word.startswith(u,j):ways[j+len(u)].update(n+1 for n in ways[j])
    assert len(ways[-1])<=1
    return next(iter(ways[-1]),0)
cache={};eligible={r:[] for r in s['readers']};ones={r:[] for r in s['readers']};seen=set();rows=list(csv.DictReader(io.StringIO(c.stdout),delimiter='\t'))
assert len(rows)==result['native_guarded_rows']
for row in rows:
    if row['kind']!='P':continue
    if row['left_separator'] not in {'LINE_START','DEFINITE_SPACE'} or row['right_separator'] not in {'LINE_END','DEFINITE_SPACE'}:continue
    word=row['ivtff_group_raw']
    if word not in cache:cache[word]=counts(word)
    length=cache[word]
    if not length:continue
    key=(row['edition'],row['locus'],row['source_group_index']);assert key not in seen;seen.add(key)
    eligible[row['edition']].append(row)
    if length==1:ones[row['edition']].append(row)
old=json.loads((R/s['old_summary']).read_text())
for reader,r in result['readers'].items():
    G=len(eligible[reader]);S=len(ones[reader]);assert G==r['eligible_groups']==old['eligible_groups'][reader]
    assert ones[reader]==single[reader] and S==r['singleton_groups']
    assert r['singleton_forms']=={w:sum(x['ivtff_group_raw']==w for x in ones[reader]) for w in sorted({x['ivtff_group_raw'] for x in ones[reader]})}
    assert r['singleton_upper_bound_any_N_selection']==min(S,N) and r['deficit']==K-S
    expected='INSUFFICIENT_PACKET_POPULATION' if G<N else ('VALUE_ONE_CAPACITY_EXCLUDED' if K>S else 'NECESSARY_CAPACITY_ONLY');assert r['status']==expected
# Exhaust finite subset upper bounds independently of source/cipher choice.
fixtures=0
for size in range(6):
 for flags in itertools.product((0,1),repeat=size):
  for n in range(size+1):
   observed=max(sum(flags[i] for i in selected) for selected in itertools.combinations(range(size),n))
   assert observed==min(sum(flags),n);fixtures+=1
for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
out={'status':'PASS','checks':['source/native/scope hashes','all source character positions','selector-first guard replay','independent DP native eligibility and unit lengths','unchanged1228denominators','every singleton raw row','all reader capacity bounds','finite subset maxima','registration hashes'],'subset_fixtures':fixtures,'scope':'Conditional exact counts and source consistency; not source identity, measured physical gap widths or word meanings.'}
(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
